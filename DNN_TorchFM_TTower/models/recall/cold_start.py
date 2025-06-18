# models/recall/cold_start.py
import random
from DNN_TorchFM_TTower.models.db import fetchall_dict

def prepare_cold_start_features(user_genres, movies):
    """
    Prepare features for cold-start recommendation.

    Args:
        user_genres: List of genres selected by the user.
        movies: List of movie dictionaries with attributes.

    Returns:
        Torch tensor of features.
    """
    features = []
    for movie in movies:
        feature_vector = [
            int(movie["genre_id"] in user_genres),  # Genre match
            movie["vote_average"],  # Continuous feature
            movie["vote_count"],    # Continuous feature
        ]
        features.append(feature_vector)
    return torch.tensor(features, dtype=torch.float32)
    

def recommend_cold_start(user_genres, movies, deepfm_model, top_n=10):
    """
    Recommend movies for a cold-start user using DeepFM.

    Args:
        user_genres: List of genres selected by the user.
        movies: List of movie dictionaries with attributes.
        deepfm_model: Trained DeepFM model.
        top_n: Number of recommendations to return.

    Returns:
        List of recommended movie IDs.
    """
    features = prepare_cold_start_features(user_genres, movies)
    movie_ids = [movie["id"] for movie in movies]

    # Score using DeepFM
    with torch.no_grad():
        scores = deepfm_model(features).numpy()

    # Rank and return top-n
    ranked_indices = np.argsort(-scores)[:top_n]
    return [movie_ids[i] for i in ranked_indices]


# def recommend_cold_start(top_n=10):
#     """
#     针对无历史用户(冷启动)：先选一批高评分热门电影，再随机抽取 top_n。
#     示例：我们假设在 movies 表中有 vote_average, vote_count 字段。
#     """
#     query = """
#         SELECT id
#         FROM movies
#         WHERE vote_count > 0
#         ORDER BY vote_average DESC, vote_count DESC
#         LIMIT 50
#     """
#     rows = fetchall_dict(query)
#     if not rows:
#         return []
#     candidate_ids = [r["id"] for r in rows]
    
#     # 从这 50 部评分最高的影片里随机抽 top_n
#     if len(candidate_ids) <= top_n:
#         return candidate_ids
#     return random.sample(candidate_ids, top_n)
