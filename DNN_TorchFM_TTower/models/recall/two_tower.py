"""
Two-Tower recall model inference logic

把原先的 warm_start.py + infer.py 合并成一个文件，供 service 层调用：
    from models.recall.two_tower import load_model, recommend_warm_start
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
    get_user_view_languages,
)
from DNN_TorchFM_TTower.models.pytorch_model import TwoTowerMLPModel

def load_model(model_path: str = None, embedding_dim: int = 32) -> TwoTowerMLPModel:
    if model_path is None:
        current_dir = Path(__file__).resolve().parent
        model_path = current_dir.parent.parent / 'saved_model' / 'dnn_recommender.pt'
    model_path = Path(model_path)
    if not model_path.exists():
        raise FileNotFoundError(f"[two_tower] Model file {model_path} not found. Please train first.")
    max_u = get_max_user_id()
    max_m = get_max_movie_id()
    model = TwoTowerMLPModel(num_users=max_u, num_movies=max_m, embedding_dim=embedding_dim, hidden_dim=64)
    state = torch.load(model_path, map_location=torch.device("cpu"))
    model.load_state_dict(state, strict=False)
    model.eval()
    return model

def recommend_warm_start(model: TwoTowerMLPModel, user_id: int, top_n: int = 10) -> Tuple[List[int], List[float]]:
    tic = time.time()
    preferred_langs = get_user_view_languages(user_id)
    all_movies = get_all_movie_ids_with_language()
    if preferred_langs:
        candidate_movies = [m for m, lang in all_movies if lang in preferred_langs]
    else:
        candidate_movies = [m for m, _ in all_movies]
    if not candidate_movies:
        return [], []
    movie_tensor = torch.tensor(candidate_movies, dtype=torch.long)
    user_tensor = torch.full((len(candidate_movies),), user_id, dtype=torch.long)
    with torch.no_grad():
        logits = model(user_tensor, movie_tensor)
        scores = torch.sigmoid(logits).numpy().flatten()
    top_idx = np.argsort(-scores)[:top_n]
    top_movie_ids = np.array(candidate_movies)[top_idx]
    top_scores = scores[top_idx]
    print(f"[two_tower] Inference finished in {time.time() - tic:.2f}s")
    return top_movie_ids.tolist(), top_scores.tolist()

if __name__ == "__main__":
    import argparse
    from DNN_TorchFM_TTower.models.db import get_movie_titles
    ap = argparse.ArgumentParser()
    ap.add_argument("user_id", type=int)
    ap.add_argument("--top_n", type=int, default=10)
    args = ap.parse_args()
    mdl = load_model()
    mids, scs = recommend_warm_start(mdl, args.user_id, args.top_n)
    title_map = get_movie_titles(mids)
    print(f"\nTop {args.top_n} recommendations for user {args.user_id}:")
    for idx, (mid, score) in enumerate(zip(mids, scs), start=1):
        print(f"  {idx:02}. ID={mid:<6}  {title_map.get(mid, 'Unknown'):<40}  score={score:.4f}")
