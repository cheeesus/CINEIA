# recommendation/collaborative_filtering.py
import numpy as np

def build_user_item_matrix(user_ids, movie_ids, user_view_dict, binary=True):
    """
    构建用户-电影矩阵:
      - user_ids: List[int], 所有用户ID
      - movie_ids: List[int], 所有电影ID
      - user_view_dict: Dict[user_id, Set[movie_id]]，用户看过哪些电影
      - binary: 是否用0/1表示，如果后续需要引入评分，可改为评分矩阵
    返回 (R, user_idx_map, movie_idx_map):
      - R: numpy数组，shape = (num_users, num_movies)
      - user_idx_map: {user_id: row_index}
      - movie_idx_map: {movie_id: col_index}
    """
    user_idx_map = {u: i for i, u in enumerate(user_ids)}
    movie_idx_map = {m: j for j, m in enumerate(movie_ids)}
    R = np.zeros((len(user_ids), len(movie_ids)), dtype=np.float32)

    for u_id in user_ids:
        seen_movies = user_view_dict.get(u_id, set())
        for m_id in seen_movies:
            if m_id in movie_idx_map:
                row = user_idx_map[u_id]
                col = movie_idx_map[m_id]
                R[row, col] = 1.0 if binary else 3.0  # 或者用评分
                
    return R, user_idx_map, movie_idx_map

def cosine_similarity(vec_a, vec_b):
    """
    简单的余弦相似度。
    如果需要别的相似度，比如皮尔逊相关系数，可以另写一个函数。
    """
    norm_a = np.linalg.norm(vec_a)
    norm_b = np.linalg.norm(vec_b)
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return float(np.dot(vec_a, vec_b) / (norm_a * norm_b))

def recommend_by_user_cf(
    target_user_id, 
    R, 
    user_ids, 
    movie_ids, 
    user_idx_map, 
    movie_idx_map, 
    top_k=5, 
    top_n=10
):
    if target_user_id not in user_idx_map:
        return {}

    target_idx = user_idx_map[target_user_id]
    target_vector = R[target_idx, :]

    # 1) 计算相似度
    similarities = []
    for other_user_id in user_ids:
        if other_user_id == target_user_id:
            continue
        other_idx = user_idx_map[other_user_id]
        sim = cosine_similarity(target_vector, R[other_idx, :])
        similarities.append((other_user_id, sim))

    # 2) 选出最相似的 top_k 用户
    similarities.sort(key=lambda x: x[1], reverse=True)
    top_k_users = similarities[:top_k]

    # 3) 统计候选电影并加权相似度得分
    seen_by_target = set(np.where(target_vector > 0)[0])
    candidate_scores = {}

    for (u_id, sim_val) in top_k_users:
        other_idx = user_idx_map[u_id]
        other_vector = R[other_idx, :]
        other_seen = np.where(other_vector > 0)[0]
        for movie_col_idx in other_seen:
            if movie_col_idx not in seen_by_target:
                candidate_scores[movie_col_idx] = candidate_scores.get(movie_col_idx, 0) + sim_val

    # 4) 返回 movie_id -> score 字典
    inv_movie_map = {v: k for k, v in movie_idx_map.items()}
    movie_score_dict = {
        inv_movie_map[col]: score for col, score in candidate_scores.items()
    }

    return movie_score_dict  # 注意这里返回的是 dict，不是 list

