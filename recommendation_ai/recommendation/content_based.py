# recommendation/content_based.py
import numpy as np

def build_movie_vector(movie_info, all_genres, all_keywords):
    """
    根据电影信息构建向量:
      - movie_info: dict, 包含这部电影的 genre_id 列表、keyword_id 列表等
      - all_genres: list, 全部可能的 genre_id
      - all_keywords: list, 全部可能的 keyword_id
    返回: numpy向量, 长度 = len(all_genres) + len(all_keywords)
    """
    genre_part = np.zeros(len(all_genres), dtype=np.float32)
    keyword_part = np.zeros(len(all_keywords), dtype=np.float32)
    
    genre_idx_map = {g_id: idx for idx, g_id in enumerate(all_genres)}
    keyword_idx_map = {k_id: idx for idx, k_id in enumerate(all_keywords)}

    # 假设 movie_info["genres"] 是一个 list/set of genre_id
    for g_id in movie_info.get("genres", []):
        idx = genre_idx_map.get(g_id)
        if idx is not None:
            genre_part[idx] = 1.0

    # 假设 movie_info["keywords"] 是一个 list/set of keyword_id
    keyword_idx_map = {kw_id: idx for idx, kw_id in enumerate(all_keywords)}

    for kw_id in movie_info.get("keywords", []):
        idx = keyword_idx_map.get(kw_id)
        if idx is not None:
            keyword_part[idx] = 1.0

    # combination
    return np.concatenate([genre_part, keyword_part])

def build_user_profile_vector(user_id, user_view_history, movie_data_dict, all_genres, all_keywords):
    """
    根据用户看过的电影，生成用户的“偏好向量” = 其看过电影向量的平均或加权平均。
      - user_view_history: list of movie_id
      - movie_data_dict: {movie_id: { "genres": [...], "keywords": [...] }, ...}
    """
    if not user_view_history:
        return np.zeros(len(all_genres) + len(all_keywords), dtype=np.float32)

    vectors = []
    for m_id in user_view_history:
        movie_info = movie_data_dict.get(m_id)
        if not movie_info:
            continue
        mv = build_movie_vector(movie_info, all_genres, all_keywords)
        vectors.append(mv)

    if not vectors:
        return np.zeros(len(all_genres) + len(all_keywords), dtype=np.float32)

    # 直接平均
    user_profile = np.mean(vectors, axis=0)
    return user_profile

def recommend_by_content(
    user_id, 
    user_view_history, 
    candidate_movie_ids, 
    movie_data_dict, 
    all_genres, 
    all_keywords, 
    top_n=10
):
    """
    基于内容的推荐：
      1) 构建用户偏好向量
      2) 依次计算候选电影与用户偏好向量的相似度
      3) 排序并返回前 top_n 个电影ID
    """
    from .collaborative_filtering import cosine_similarity

    user_vector = build_user_profile_vector(user_id, user_view_history, movie_data_dict, all_genres, all_keywords)

    movie_scores = []
    for m_id in candidate_movie_ids:
        movie_info = movie_data_dict.get(m_id)
        if not movie_info:
            continue
        mv = build_movie_vector(movie_info, all_genres, all_keywords)
        score = cosine_similarity(user_vector, mv)
        movie_scores.append((m_id, score))

    # 按相似度降序
    movie_scores.sort(key=lambda x: x[1], reverse=True)
    return [m_id for (m_id, score) in movie_scores[:top_n]]


def gather_all_genres(movie_data_dict):
    """从所有电影信息中提取所有可能的 genre_id 列表"""
    genre_set = set()
    for movie in movie_data_dict.values():
        genre_set.update(movie.get("genres", []))
    return list(genre_set)

def gather_all_keywords(movie_data_dict):
    """从所有电影信息中提取所有可能的 keyword_id 列表"""
    keyword_set = set()
    for movie in movie_data_dict.values():
        keyword_set.update(movie.get("keywords", []))
    return list(keyword_set)
