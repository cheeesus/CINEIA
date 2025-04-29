# models/warm_start.py
import os
import time
import numpy as np
import torch
from models.pytorch_model import TwoTowerMLPModel
from models.db import (
    get_max_user_id,
    get_max_movie_id,
    get_all_movie_ids_with_language,
    get_user_view_languages
)

def load_model(model_path="saved_model/dnn_recommender.pt", embedding_dim=32):
    max_u = get_max_user_id()
    max_m = get_max_movie_id()
    model = TwoTowerMLPModel(max_u, max_m, embedding_dim=embedding_dim, hidden_dim=64)
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model file {model_path} not found. Please run train.py first.")
    model.load_state_dict(torch.load(model_path, map_location=torch.device("cpu")))
    model.eval()
    return model

def recommend_warm_start(model, user_id, top_n=10):
    """
    有历史记录的用户直接用深度模型预测。
    """
    start_t = time.time()
    preferred_langs = get_user_view_languages(user_id)
    
    all_movies = get_all_movie_ids_with_language()
    if preferred_langs:
        candidate_movies = [mid for mid, lang in all_movies if lang in preferred_langs]
    else:
        print("No language preference detected, using all movies.")
        candidate_movies = [mid for mid, _ in all_movies]
    
    if not candidate_movies:
        print("No valid candidates found.")
        return [], []
    
    movie_tensor = torch.tensor(candidate_movies, dtype=torch.long)
    user_tensor = torch.full((len(candidate_movies),), user_id, dtype=torch.long)
    
    with torch.no_grad():
        logits = model(user_tensor, movie_tensor)
        scores = torch.sigmoid(logits)

    scores_np = scores.numpy().flatten()
    top_idx = np.argsort(-scores_np)[:top_n]
    top_movie_ids = np.array(candidate_movies)[top_idx]
    top_scores = scores_np[top_idx]
    
    print(f"Inference completed in {time.time() - start_t:.2f} seconds.")
    return top_movie_ids.tolist(), top_scores.tolist()
