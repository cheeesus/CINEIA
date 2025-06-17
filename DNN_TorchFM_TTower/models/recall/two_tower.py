"""
Two-Tower recall model inference logic
—— 在召回前根据用户在 user_preferences 表里的偏好 genre 过滤候选电影
"""
import time
from pathlib import Path
from typing import List, Tuple

import numpy as np
import torch

from DNN_TorchFM_TTower.models.db import (
    get_max_user_id,
    get_max_movie_id,
    get_all_movie_ids_with_language,
    get_user_preferences,
    fetchall_dict
)
from DNN_TorchFM_TTower.models.pytorch_model import TwoTowerMLPModel

def load_model(model_path: str | None = None, *, embedding_dim: int = 32) -> TwoTowerMLPModel:
    """
    加载 Two-Tower 模型，并对“新用户 / 新电影”做安全扩容拷贝。
    """
    if model_path is None:
        model_path = Path(__file__).resolve().parents[3] / "saved_model" / "dnn_recommender.pt"
    model_path = Path(model_path)

    # ── 1. 取得最新 vocab size ──────────────────────────────────────────
    max_u = get_max_user_id()
    max_m = get_max_movie_id()
    model = TwoTowerMLPModel(max_u, max_m,
                             embedding_dim=embedding_dim, hidden_dim=64)

    # 如果还没有训练过，直接返回随机初始化的模型
    if not model_path.exists():
        return model.eval()

    # ── 2. 断点权重加载（带扩容） ────────────────────────────────────────
    state = torch.load(model_path, map_location="cpu")

    def _copy(old_w, new_w):
        rows = min(old_w.size(0), new_w.size(0))
        new_w[:rows].data.copy_(old_w[:rows])

    # 扩容 embedding 并拷贝旧权重
    if "user_embedding.weight" in state:
        _copy(state["user_embedding.weight"], model.user_embedding.weight)
    if "movie_embedding.weight" in state:
        _copy(state["movie_embedding.weight"], model.movie_embedding.weight)

    # 删除已处理的 key，后续用 strict=False 加载余下部分
    for key in ("user_embedding.weight", "movie_embedding.weight"):
        state.pop(key, None)
    model.load_state_dict(state, strict=False)

    return model.eval()


def recommend_warm_start(
    model: TwoTowerMLPModel,
    user_id: int,
    top_n: int = 10
) -> Tuple[List[int], List[float]]:
    """
    基于 Two-Tower 对老用户做召回，并对召回候选集做 genre 过滤。

    返回 (movie_ids, scores) 两个长度为 top_n 的列表。
    """
    tic = time.time()

    # 1) 从 user_preferences 表里拿用户偏好的 genre 列表
    preferred_genres = get_user_preferences(user_id)  # e.g. [12, 5, 20]

    # 2) 拿到所有电影及其语言（language 信息不影响 genre 过滤）
    all_movies_lang = get_all_movie_ids_with_language()  # [(movie_id, lang), ...]

    # 3) 如果有偏好 genre，则先在 movie_genre 表里把这些 genre 对应的 movie_id 拉出来
    if preferred_genres:
        rows = fetchall_dict(
            "SELECT movie_id FROM movie_genre WHERE genre_id = ANY(%s)",
            (preferred_genres,)
        )
        genre_movie_set = {r["movie_id"] for r in rows}
        # 只保留这些 movie_id
        candidate_movies = [m for m, _ in all_movies_lang if m in genre_movie_set]
    else:
        # 无显式偏好时全量召回
        candidate_movies = [m for m, _ in all_movies_lang]

    if not candidate_movies:
        return [], []

    # 4) Two-Tower 推理：批量计算用户对所有候选的打分
    device = next(model.parameters()).device
    movie_tensor = torch.tensor(candidate_movies, dtype=torch.long, device=device)
    user_tensor  = torch.full((len(candidate_movies),), user_id,
                              dtype=torch.long, device=device)

    with torch.no_grad():
        logits = model(user_tensor, movie_tensor)
        scores = torch.sigmoid(logits).cpu().numpy()

    # 5) 根据得分排序并截断
    top_idx = np.argsort(-scores)[:top_n]
    top_ids = np.array(candidate_movies)[top_idx].tolist()
    top_scores = scores[top_idx].tolist()

    print(f"[two_tower] Inference finished in {time.time() - tic:.2f}s | "
          f"candidates after genre filter: {len(candidate_movies)} → top {top_n}")
    return top_ids, top_scores


if __name__ == "__main__":
    import argparse
    from DNN_TorchFM_TTower.models.db import get_movie_titles

    parser = argparse.ArgumentParser()
    parser.add_argument("user_id", type=int)
    parser.add_argument("--top_n", type=int, default=10)
    args = parser.parse_args()

    model = load_model()
    mids, scs = recommend_warm_start(model, args.user_id, args.top_n)
    titles = get_movie_titles(mids)

    print(f"\nTop {args.top_n} recommendations for user {args.user_id}:")
    for i, (mid, score) in enumerate(zip(mids, scs), start=1):
        print(f"  {i:02}. ID={mid:<6}  {titles.get(mid,'Unknown'):<40}  score={score:.4f}")
