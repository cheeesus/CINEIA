# main_recommender.py

from recommendation.collaborative_filtering import build_user_item_matrix, recommend_by_user_cf
from recommendation.content_based import recommend_by_content, gather_all_genres, gather_all_keywords

from models import (
    get_all_user_ids,
    get_all_movie_ids,
    get_user_view_dict,
    get_user_view_history,
    get_movie_content_data
)

def recommend_cf_for_user(user_id):
    user_ids = get_all_user_ids()
    movie_ids = get_all_movie_ids()
    user_view_dict = get_user_view_dict()
    R, user_idx_map, movie_idx_map = build_user_item_matrix(user_ids, movie_ids, user_view_dict)
    return recommend_by_user_cf(user_id, R, user_ids, movie_ids, user_idx_map, movie_idx_map)

def recommend_content_for_user(user_id):
    movie_data_dict = get_movie_content_data()
    all_movies = list(movie_data_dict.keys())
    view_history = get_user_view_history(user_id)

    all_genres = gather_all_genres(movie_data_dict)
    all_keywords = gather_all_keywords(movie_data_dict)

    return recommend_by_content(
        user_id, view_history, all_movies, movie_data_dict, all_genres, all_keywords
    )
