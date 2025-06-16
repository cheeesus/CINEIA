# service/recommender.py

"""
统一推荐入口：
    • 新用户       → 冷启动 (PopRec + 随机多样化)
    • 老用户       → Two-Tower 召回  → DeepFM 精排
对上层调用者隐藏实现细节，只暴露一个函数 `recommend_movies_for_user`
"""

from __future__ import annotations

import time
from typing import Tuple

from DNN_TorchFM_TTower.models.db import (
    get_user_view_count,
    fetchone_dict,
    execute_sql,
)
from DNN_TorchFM_TTower.models.recall import cold_start
from DNN_TorchFM_TTower.models.recall.two_tower import load_model as _load_tower, recommend_warm_start
from DNN_TorchFM_TTower.models.ranking.infer_ranking import rank_candidates


def _get_tower_model():
    """
    每次都动态加载 Two-Tower 模型，以保证使用最新的 vocab size。
    """
    return _load_tower()


def recommend_movies_for_user(user_id: int,
                              n_recall: int = 300,
                              n_final:  int = 20
                              ) -> Tuple[list[int], list[float], str]:
    """
    返回 (movie_ids, scores, strategy)
      - strategy: 'cold' | 'warm' | 'warm+rank'
    """

    # 1) 确保新用户在 users 表中有记录
    if not fetchone_dict("SELECT 1 FROM users WHERE id=%s", (user_id,)):
        execute_sql(
            "INSERT INTO users (id, email, password_hash) VALUES (%s, %s, %s)",
            (user_id, f"api_{user_id}@demo.com", b"hash_placeholder"),
        )

    # 2) 获取用户历史观看次数
    view_cnt = get_user_view_count(user_id)

    # -------- 冷启动 --------
    if view_cnt == 0:
        mids = cold_start.recommend_cold_start(top_n=n_final)
        return mids, [None] * len(mids), "cold"

    # -------- 热启动 (Two-Tower) + fallback --------
    recall_model = _get_tower_model()
    try:
        recall_ids, recall_scores = recommend_warm_start(
            recall_model, user_id, top_n=n_recall
        )
    except IndexError:
        # Embedding 越界，新用户/新电影尚未在模型中：fallback 到冷启动
        print(f"[recommender] user {user_id} embedding 越界，fallback cold-start")
        mids = cold_start.recommend_cold_start(top_n=n_final)
        return mids, [None] * len(mids), "cold"

    if not recall_ids:
        mids = cold_start.recommend_cold_start(top_n=n_final)
        return mids, [None] * len(mids), "cold"

    # -------- DeepFM 精排 --------
    mids = rank_candidates(user_id, recall_ids, recall_scores, top_n=n_final)
    return mids, recall_scores[:n_final], "warm+rank"


# -------------------- CLI 测试 --------------------
if __name__ == "__main__":
    import json
    import datetime
    import argparse
    from DNN_TorchFM_TTower.models.db import get_movie_titles, get_movie_genres

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
                "genre": genres.get(mid, ""),  
                "score": float(scores[i]) if scores[i] is not None else None,
            }
            for i, mid in enumerate(mids)
        ],
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
