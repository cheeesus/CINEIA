from recommendation.collaborative_filtering import build_user_item_matrix, recommend_by_user_cf
from recommendation.content_based import (
    recommend_by_content,
    gather_all_genres,
    gather_all_keywords,
    precompute_movie_vectors
)

from models import (
    get_all_user_ids,
    get_all_movie_ids,
    get_user_view_dict,
    get_user_view_history,
    get_movie_content_data
)

# 全局缓存 (可选)，或通过一个 init 函数集中预计算
_cached_movie_vectors = None
_cached_movie_data_dict = None
_cached_all_movies = None

def precompute_for_content():
    """
    预先获取所有电影的内容数据，并构建向量。只需执行一次。
    """
    global _cached_movie_vectors, _cached_movie_data_dict, _cached_all_movies
    if _cached_movie_vectors is not None:
        return  # 已经预计算过了

    movie_data_dict = get_movie_content_data()     # {movie_id -> {genres, keywords, language}}
    all_genres = gather_all_genres(movie_data_dict)
    all_keywords = gather_all_keywords(movie_data_dict)
    movie_vectors, _, _ = precompute_movie_vectors(movie_data_dict, all_genres, all_keywords)

    _cached_movie_data_dict = movie_data_dict
    _cached_movie_vectors = movie_vectors
    _cached_all_movies = list(movie_data_dict.keys())  # 全部 movie_id

def recommend_cf_for_user(user_id, top_k=5, top_n=10):
    """
    基于协同过滤给用户推荐,用于推荐的最相似的用户数量为 top_k，推荐的电影数量为 top_n。
    """
    user_ids = get_all_user_ids()
    movie_ids = get_all_movie_ids()
    user_view_dict = get_user_view_dict()

    R, user_idx_map, movie_idx_map = build_user_item_matrix(user_ids, movie_ids, user_view_dict)
    recommended_ids = recommend_by_user_cf(
        user_id,
        R,
        user_ids,
        movie_ids,
        user_idx_map,
        movie_idx_map,
        top_k=top_k,
        top_n=top_n
    )
    return recommended_ids

def recommend_content_for_user(user_id, top_n=10):
    """
    基于内容给用户推荐
    """
    # 保证已经做过预计算
    precompute_for_content()

    view_history = get_user_view_history(user_id)
    # 直接使用全局缓存的 movie_data 和 movie_vectors
    return recommend_by_content(
        user_id,
        view_history,
        _cached_all_movies,       # 候选就是全量电影
        _cached_movie_data_dict,
        _cached_movie_vectors,
        top_n=top_n
    )

def recommend_hybrid_for_user(user_id, alpha=0.5, top_k=5, top_n=10):
    """
    混合推荐：α * CF + (1-α) * Content
    - alpha: CF权重，范围 0~1
    """
    # 保证内容向量预计算完成
    precompute_for_content()

    # Step 1: 获取两种方法的打分
    user_ids = get_all_user_ids()
    movie_ids = get_all_movie_ids()
    user_view_dict = get_user_view_dict()
    R, user_idx_map, movie_idx_map = build_user_item_matrix(user_ids, movie_ids, user_view_dict)

    cf_scores = recommend_by_user_cf(user_id, R, user_ids, movie_ids, user_idx_map, movie_idx_map, top_k=top_k, top_n=1000)
    view_history = get_user_view_history(user_id)
    content_scores = recommend_by_content(
        user_id,
        view_history,
        _cached_all_movies,
        _cached_movie_data_dict,
        _cached_movie_vectors,
        top_n=1000
    )

    # Step 2: 归一化得分
    def normalize(score_dict):
        if not score_dict:
            return {}
        max_val = max(score_dict.values())
        if max_val == 0:
            return score_dict
        return {k: v / max_val for k, v in score_dict.items()}

    cf_scores = normalize(cf_scores)
    content_scores = normalize(content_scores)

    # Step 3: 融合得分
    hybrid_scores = {}
    all_movie_ids = set(cf_scores.keys()) | set(content_scores.keys())
    for m_id in all_movie_ids:
        cf_val = cf_scores.get(m_id, 0)
        cont_val = content_scores.get(m_id, 0)
        hybrid_scores[m_id] = alpha * cf_val + (1 - alpha) * cont_val

    # Step 4: 排序并返回 top_n
    sorted_movies = sorted(hybrid_scores.items(), key=lambda x: x[1], reverse=True)
    return [m_id for m_id, _ in sorted_movies[:top_n]]
