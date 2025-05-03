# models/infer.py
import os
import time
import numpy as np
import torch
from pytorch_model import TwoTowerMLPModel
from db import *
from collections import Counter


def load_model(model_path="saved_model/dnn_recommender.pt", embedding_dim=32):
    max_u = get_max_user_id()
    max_m = get_max_movie_id()
    model = TwoTowerMLPModel(max_u, max_m, embedding_dim=32, hidden_dim=64)
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model file {model_path} not found. Please run train.py first.")
    model.load_state_dict(torch.load(model_path, map_location=torch.device("cpu")))
    model.eval()
    return model

def recommend_for_user(model, user_id, top_n=10):
    infer_start = time.time()
    preferred_langs = get_user_view_languages(user_id)
    
    all_movies = get_all_movie_ids_with_language()
    if preferred_langs:
        candidate_movies = [mid for mid, lang in all_movies if lang in preferred_langs]
    else:
        print("No language preference detected, using all movies.")
        candidate_movies = [mid for mid, _ in all_movies]
    
    if not candidate_movies:
        print("No valid movie candidates found.")
        return [], []
    
    movie_tensor = torch.tensor(candidate_movies, dtype=torch.long)
    user_tensor = torch.full((len(candidate_movies),), user_id, dtype=torch.long)
    
    with torch.no_grad():
        logits = model(user_tensor, movie_tensor)
        # to raw logits do sigmoid and get the prediction probability
        scores = torch.sigmoid(logits)
    
    avg_logit = torch.mean(logits).item()
    print(f"Average logit: {avg_logit:.3f}")
    
    scores_np = scores.numpy().flatten()
    top_idx = np.argsort(-scores_np)[:top_n]
    top_movie_ids = np.array(candidate_movies)[top_idx]
    top_scores = scores_np[top_idx]
    
    infer_time = time.time() - infer_start
    print(f"Inference completed in {infer_time:.2f} seconds.")
    
    return top_movie_ids.tolist(), top_scores.tolist()

if __name__ == "__main__":
    user_id = 1  # Massyl 
    model = load_model()
    rec_ids, scores = recommend_for_user(model, user_id, top_n=100)
    # get movie titles
    title_map = get_movie_titles(rec_ids)
    
    print(f"Top 5 recommendations for user {user_id} with language filtering:")
    for mid, score in zip(rec_ids, scores):
        title = title_map.get(mid, "Unknown Title")
        print(f"  Movie ID: {mid}, Title: {title}, Score: {score:.4f}")
