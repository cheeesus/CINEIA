import time
from main_recommender import (
    recommend_cf_for_user,
    recommend_content_for_user,
    precompute_for_content,
    recommend_hybrid_for_user   
)
from models import get_movie_titles, get_user_view_history, evaluate_recommendation

def main_test(user_id):
    print(f"Generating recommendations for user_id = {user_id} ...\n")

    # ========= 1) Collaborative Filtering =========
    print("[Collaborative Filtering] Recommendation results:")
    start_cf = time.time()
    cf_results = recommend_cf_for_user(user_id)  # dict[movie_id] = score
    end_cf = time.time()

    cf_ids = list(cf_results.keys())
    cf_titles = get_movie_titles(cf_ids)
    for mid in cf_ids[:10]:
        print(f" - {mid}: {cf_titles.get(mid, '[Unknown Movie]')}")

    print(f"Time taken for Collaborative Filtering: {end_cf - start_cf:.4f} seconds")

    cf_eval = evaluate_recommendation(user_id, cf_ids, top_n=10)
    print(f"[CF Evaluation] Precision@10: {cf_eval['precision']}, Recall: {cf_eval['recall']}")
    if cf_eval["hits"]:
        hit_titles = get_movie_titles(cf_eval["hits"])
        print(" CF hits in user watch history:", [hit_titles[mid] for mid in cf_eval["hits"]])
    else:
        print(" CF no hit in the user's watch history.")

    # ========= 2) Content-Based Filtering =========
    print("\n[Content-Based Filtering] Recommendation results:")
    start_content = time.time()
    content_results = recommend_content_for_user(user_id)  # dict[movie_id] = score
    end_content = time.time()

    content_ids = list(content_results.keys())
    content_titles = get_movie_titles(content_ids)
    for mid in content_ids[:10]:
        print(f" - {mid}: {content_titles.get(mid, '[Unknown Movie]')}")

    print(f"Time taken for Content-Based Filtering: {end_content - start_content:.4f} seconds")

    content_eval = evaluate_recommendation(user_id, content_ids, top_n=10)
    print(f"[Content-Based Evaluation] Precision@10: {content_eval['precision']}, Recall: {content_eval['recall']}")
    if content_eval["hits"]:
        hit_titles = get_movie_titles(content_eval["hits"])
        print(" Content hits in user watch history:", [hit_titles[mid] for mid in cf_eval["hits"]])
    else:
        print(" Content no hit in the user's watch history.")

    # ========= 3) Hybrid Recommendation =========
    print("\n[Hybrid Recommendation] (α=0.6):")
    start_hybrid = time.time()
    hybrid_results = recommend_hybrid_for_user(user_id, alpha=0.6)  # list[movie_id]
    end_hybrid = time.time()

    hybrid_titles = get_movie_titles(hybrid_results)
    for mid in hybrid_results[:10]:
        print(f" - {mid}: {hybrid_titles.get(mid, '[Unknown Movie]')}")

    print(f"Time taken for Hybrid Recommendation: {end_hybrid - start_hybrid:.4f} seconds")

    hybrid_eval = evaluate_recommendation(user_id, hybrid_results, top_n=10)
    print(f"[Hybrid Evaluation] Precision@10: {hybrid_eval['precision']}, Recall: {hybrid_eval['recall']}")


if __name__ == "__main__":
    main_test(user_id=2)
