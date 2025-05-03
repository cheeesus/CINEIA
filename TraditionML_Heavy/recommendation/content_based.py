import numpy as np
from collections import Counter
from .collaborative_filtering import cosine_similarity

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


def build_movie_vector(movie_info, genre_idx_map, keyword_idx_map):
    """
    根据电影信息构建向量:
      - movie_info: dict, 包含这部电影的 genre_id 列表、keyword_id 列表等
      - genre_idx_map: {genre_id -> index_in_vector}
      - keyword_idx_map: {keyword_id -> index_in_vector}
    返回: numpy向量, shape=(len(genre_idx_map) + len(keyword_idx_map),)
    """
    vector = np.zeros(len(genre_idx_map) + len(keyword_idx_map), dtype=np.float32)

    # genres
    for g_id in movie_info.get("genres", []):
        g_idx = genre_idx_map.get(g_id)
        if g_idx is not None:
            vector[g_idx] = 1.0

    # keywords
    for kw_id in movie_info.get("keywords", []):
        k_idx = keyword_idx_map.get(kw_id)
        if k_idx is not None:
            vector[k_idx] = 1.0

    return vector

def precompute_movie_vectors(movie_data_dict, all_genres, all_keywords):
    """
    一次性为所有电影构建向量并缓存:
      - movie_data_dict: {movie_id -> {"genres": [...], "keywords": [...], "language": ...}, ...}
      - all_genres: list of all possible genre IDs
      - all_keywords: list of all possible keyword IDs
    返回:
      - movie_vectors: {movie_id -> np.array([...])}  # 该电影的内容向量
      - genre_idx_map, keyword_idx_map: 上面提到的映射
    """
    # 先为 genres/keywords 分配向量索引
    genre_idx_map = {g_id: i for i, g_id in enumerate(all_genres)}
    # keyword 的索引要从 len(all_genres) 开始排起
    keyword_idx_map = {}
    offset = len(all_genres)
    for i, k_id in enumerate(all_keywords):
        keyword_idx_map[k_id] = offset + i

    movie_vectors = {}

    for m_id, info in movie_data_dict.items():
        movie_vectors[m_id] = build_movie_vector(info, genre_idx_map, keyword_idx_map)

    return movie_vectors, genre_idx_map, keyword_idx_map

def build_user_profile_vector(user_view_history, movie_vectors):
    """
    根据用户看过的电影，生成用户的“偏好向量” = 其看过电影向量的平均。
      - user_view_history: list of movie_id
      - movie_vectors: {movie_id -> 该电影的向量}
    返回: np.array([...]) (1D)，若用户没看过电影则返回 0 向量
    """
    if not user_view_history:
        # 用户没有观影记录，返回0向量
        some_vector = next(iter(movie_vectors.values()), None)
        if some_vector is None:
            return np.array([], dtype=np.float32)
        return np.zeros_like(some_vector, dtype=np.float32)

    vectors = []
    for m_id in user_view_history:
        if m_id in movie_vectors:
            vectors.append(movie_vectors[m_id])

    if not vectors:
        # 用户看的电影都不在 movie_vectors 里
        return np.zeros_like(next(iter(movie_vectors.values())))

    # 直接对所有向量做平均得到用户向量
    user_profile = np.mean(vectors, axis=0)
    return user_profile

def recommend_by_content(
    user_id,
    user_view_history,
    candidate_movie_ids,
    movie_data_dict,
    movie_vectors,
    top_n=10
):
    user_vector = build_user_profile_vector(user_view_history, movie_vectors)

    from collections import Counter
    language_counter = Counter()
    for m_id in user_view_history:
        movie_info = movie_data_dict.get(m_id)
        if movie_info and "language" in movie_info:
            language_counter[movie_info["language"]] += 1

    if not language_counter:
        preferred_languages = set()
    else:
        preferred_languages = set([lang for lang, _ in language_counter.most_common(2)])

    movie_scores = []
    for m_id in candidate_movie_ids:
        movie_info = movie_data_dict.get(m_id)
        if not movie_info:
            continue
        if preferred_languages and movie_info.get("language") not in preferred_languages:
            continue
        mv = movie_vectors.get(m_id)
        if mv is None:
            continue

        score = cosine_similarity(user_vector, mv)
        movie_scores.append((m_id, score))

    # 改为返回 dict
    return dict(movie_scores)  # dict[movie_id] = score

