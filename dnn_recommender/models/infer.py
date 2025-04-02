# models/infer.py
import os
import time
import numpy as np
import torch
from pytorch_model import TwoTowerMLPModel
from db import fetchall_dict, fetchone_dict
from collections import Counter

def get_max_user_id():
    row = fetchone_dict("SELECT MAX(id) as m FROM users")
    return row["m"] or 0

def get_max_movie_id():
    row = fetchone_dict("SELECT MAX(id) as m FROM movies")
    return row["m"] or 0

def load_model(model_path="saved_model/dnn_recommender.pt", embedding_dim=32):
    max_u = get_max_user_id()
    max_m = get_max_movie_id()
    model = TwoTowerMLPModel(max_u, max_m, embedding_dim=32, hidden_dim=64)
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model file {model_path} not found. Please run train.py first.")
    model.load_state_dict(torch.load(model_path, map_location=torch.device("cpu")))
    model.eval()
    return model

def get_all_movie_ids_with_language():
    rows = fetchall_dict("SELECT id, original_language FROM movies")
    return [(r["id"], r["original_language"]) for r in rows if r["original_language"]]

def get_user_view_languages(user_id):
    query = """
        SELECT m.original_language
        FROM view_history v
        JOIN movies m ON v.movie_id = m.id
        WHERE v.user_id = %s
    """
    rows = fetchall_dict(query, (user_id,))
    lang_counter = Counter(r["original_language"] for r in rows if r["original_language"])
    if not lang_counter:
        return set()
    top_languages = {lang for lang, _ in lang_counter.most_common(2)}
    return top_languages

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
    print(f"Top 5 recommendations for user {user_id} with language filtering:")
    for mid, score in zip(rec_ids, scores):
        print(f"  Movie ID: {mid}, Score: {score:.4f}")
