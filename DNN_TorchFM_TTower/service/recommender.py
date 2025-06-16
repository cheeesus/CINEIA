# service/recommender.py

"""
统一推荐入口：
    • 新用户       → 冷启动 (PopRec + 随机多样化)
    • 老用户       → Two-Tower 召回  → DeepFM 精排
对上层调用者隐藏实现细节，只暴露一个函数 `recommend_movies_for_user`
"""

from __future__ import annotations

import functools
import time
from typing import List, Tuple

from DNN_TorchFM_TTower.models.db import (
    get_user_view_count,
    fetchone_dict,
    execute_sql,
)
from DNN_TorchFM_TTower.models.recall import cold_start
from DNN_TorchFM_TTower.models.recall.two_tower import load_model as _load_tower, recommend_warm_start
from DNN_TorchFM_TTower.models.ranking.infer_ranking import rank_candidates


# --------------------------------------------------------------------------- #
#                          全局缓存 —— 只加载一次                              #
# --------------------------------------------------------------------------- #
_TOWER_MODEL = functools.lru_cache(maxsize=1)(_load_tower)()   # type: ignore


# core interface
# 只改 recommend_movies_for_user 的返回值 & 末尾 CLI 打印
def recommend_movies_for_user(user_id: int,
                              n_recall: int = 300,
                              n_final:  int = 20) -> tuple[list[int], list[float], str]:
    """
    返回 (movie_ids, scores, strategy)
    strategy: 'cold' | 'warm' | 'warm+rank'
    """
    # --- 1) 确保新用户在 users 表中有记录，否则 view_count 会继续返回 0 之外的值 ---
    if not fetchone_dict("SELECT 1 FROM users WHERE id=%s", (user_id,)):
        execute_sql(
            "INSERT INTO users (id, email, password_hash) VALUES (%s, %s, %s)",
            (user_id, f"api_{user_id}@demo.com", b"hash_placeholder"),
        )

    # --- 2) 拿到观看历史数 ---
    view_cnt = get_user_view_count(user_id)

    # -------- cold --------
    if view_cnt == 0:
        mids = cold_start.recommend_cold_start(top_n=n_final)
        return mids, [None] * len(mids), "cold"

    # -------- warm（Two-Tower）＋catch越界 fallback--------
    try:
        recall_ids, recall_scores = recommend_warm_start(
            _TOWER_MODEL, user_id, top_n=n_recall
        )
    except IndexError:
        # embedding 长度不足，新用户越界：退回 cold-start
        print(f"[recommender] user {user_id} embedding 越界，fallback cold-start")
        mids = cold_start.recommend_cold_start(top_n=n_final)
        return mids, [None] * len(mids), "cold"

    if not recall_ids:
        mids = cold_start.recommend_cold_start(top_n=n_final)
        return mids, [None] * len(mids), "cold"

    # -------- rank --------
    mids = rank_candidates(user_id, recall_ids, recall_scores, top_n=n_final)
    return mids, recall_scores[:n_final], "warm+rank"


# CLI 测试保持，改为 JSON 打印
if __name__ == "__main__":
    import json, datetime, argparse
    from models.db import get_movie_titles

    ap = argparse.ArgumentParser()
    ap.add_argument("user_id", type=int)
    ap.add_argument("--top", type=int, default=10)
    args = ap.parse_args()

    mids, scores, strategy = recommend_movies_for_user(args.user_id, n_final=args.top)
    titles = get_movie_titles(mids)
    payload = {
        "user_id": args.user_id,
        "generated_at": datetime.datetime.utcnow().isoformat() + "Z",
        "strategy": strategy,
        "items": [
            {
                "rank": i + 1,
                "movie_id": mid,
                "title": titles.get(mid, "Unknown"),
                "score": float(scores[i]) if scores[i] is not None else None,
            }
            for i, mid in enumerate(mids)
        ],
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
