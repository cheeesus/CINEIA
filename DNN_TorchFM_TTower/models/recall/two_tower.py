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
    top_n: int = 10,
    genre_weight: float = 0.7,  # Weight for preferred genres
    diversity_ratio: float = 0.3  # Proportion of non-preferred genres
) -> Tuple[List[int], List[float]]:
    """
    Recommend movies for a user using the Two-Tower model with balanced genre filtering.

    Args:
        model: TwoTowerMLPModel instance for inference.
        user_id: ID of the user.
        top_n: Number of recommendations to return.
        genre_weight: Weight for preferred genres in scoring.
        diversity_ratio: Proportion of non-preferred genres to include.

    Returns:
        Tuple of (movie_ids, scores).
    """
    tic = time.time()

    # Fetch user's preferred genres
    preferred_genres = get_user_preferences(user_id)

    # Fetch all movies and their genres
    all_movies_lang = get_all_movie_ids_with_language()

    if preferred_genres:
        # Movies matching preferred genres
        rows = fetchall_dict(
            "SELECT movie_id FROM movie_genre WHERE genre_id = ANY(%s)",
            (preferred_genres,)
        )
        genre_movie_set = {r["movie_id"] for r in rows}
    else:
        genre_movie_set = set()

    candidate_movies = [m for m, _ in all_movies_lang]
    candidate_genre_movies = [m for m in candidate_movies if m in genre_movie_set]
    non_genre_movies = [m for m in candidate_movies if m not in genre_movie_set]

    if not candidate_movies:
        return [], []

    # Inference for preferred-genre movies
    device = next(model.parameters()).device
    movie_tensor = torch.tensor(candidate_genre_movies, dtype=torch.long, device=device)
    user_tensor = torch.full((len(candidate_genre_movies),), user_id, dtype=torch.long, device=device)

    with torch.no_grad():
        genre_logits = model(user_tensor, movie_tensor)
        genre_scores = torch.sigmoid(genre_logits).cpu().numpy()

    # Inference for non-preferred-genre movies
    movie_tensor_non_genre = torch.tensor(non_genre_movies, dtype=torch.long, device=device)
    user_tensor_non_genre = torch.full((len(non_genre_movies),), user_id, dtype=torch.long, device=device)

    with torch.no_grad():
        non_genre_logits = model(user_tensor_non_genre, movie_tensor_non_genre)
        non_genre_scores = torch.sigmoid(non_genre_logits).cpu().numpy()

    # Combine and adjust scores
    genre_adjusted_scores = genre_weight * genre_scores
    non_genre_adjusted_scores = (1 - genre_weight) * non_genre_scores

    # Rank within each group
    top_genre_idx = np.argsort(-genre_adjusted_scores)[:int(top_n * (1 - diversity_ratio))]
    top_non_genre_idx = np.argsort(-non_genre_adjusted_scores)[:int(top_n * diversity_ratio)]

    # Collect final recommendations
    top_genre_ids = np.array(candidate_genre_movies)[top_genre_idx].tolist()
    top_non_genre_ids = np.array(non_genre_movies)[top_non_genre_idx].tolist()

    # Merge the two pools
    top_ids = top_genre_ids + top_non_genre_ids
    top_scores = np.concatenate((genre_adjusted_scores[top_genre_idx], non_genre_adjusted_scores[top_non_genre_idx])).tolist()

    print(f"[two_tower] Inference finished in {time.time() - tic:.2f}s | "
          f"candidates: genre {len(candidate_genre_movies)}, non-genre {len(non_genre_movies)} → top {top_n}")
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
