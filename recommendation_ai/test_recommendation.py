# # test_recommendation.py

# from main_recommender import recommend_cf_for_user, recommend_content_for_user

# if __name__ == "__main__":
#     user_id = 1  # obejct user

#     print("Collaborative filtering Recommendations:")
#     cf_results = recommend_cf_for_user(user_id)
#     print(cf_results)

#     print("\nContent filtering recommendation results：")
#     content_results = recommend_content_for_user(user_id)
#     print(content_results)


import time
from main_recommender import (
    recommend_cf_for_user,
    recommend_content_for_user,
    precompute_for_content   
)
from models import get_movie_titles, get_user_view_history, evaluate_recommendation

def main_test(user_id):
    print(f"Generating recommendations for user_id = {user_id} ...\n")

    # ========= 1) 协同过滤 CF =========
    print("[Collaborative Filtering] Recommendation results:")
    start_cf = time.time()
    cf_results = recommend_cf_for_user(user_id)
    end_cf = time.time()

    cf_titles = get_movie_titles(cf_results)
    for mid in cf_results:
        print(f" - {mid}: {cf_titles.get(mid, '[Unknown Movie]')}")

    print(f"Time taken for Collaborative Filtering: {end_cf - start_cf:.4f} seconds")

    # 对CF结果做简单评估
    cf_eval = evaluate_recommendation(user_id, cf_results, top_n=10)
    print(f"[CF Evaluation] Precision@10: {cf_eval['precision']}, Recall: {cf_eval['recall']}")
    if cf_eval["hits"]:
        hit_titles = get_movie_titles(cf_eval["hits"])
        print(" CF hits in user watch history:", [hit_titles[mid] for mid in cf_eval["hits"]])
    else:
        print(" CF no hit in the user's watch history.")

    # ========= 2) 内容过滤 Content-Based =========
    # 注意：content-based 预计算可以提到主进程只做一次
    print("\n[Content-Based Filtering] Recommendation results:")
    start_content = time.time()
    content_results = recommend_content_for_user(user_id)
    end_content = time.time()

    content_titles = get_movie_titles(content_results)
    for mid in content_results:
        print(f" - {mid}: {content_titles.get(mid, '[Unknown Movie]')}")

    print(f"Time taken for Content-Based Filtering: {end_content - start_content:.4f} seconds")

    # 内容过滤评估
    content_eval = evaluate_recommendation(user_id, content_results, top_n=10)
    print(f"[Content-Based Evaluation] Precision@10: {content_eval['precision']}, Recall: {content_eval['recall']}")
    if content_eval["hits"]:
        hit_titles = get_movie_titles(content_eval["hits"])
        print(" Content hits in user watch history:", [hit_titles[mid] for mid in content_eval["hits"]])
    else:
        print(" Content no hit in the user's watch history.")

    print("\nExplanation:")
    print(" - Collaborative Filtering: Recommends movies that other users with similar viewing habits have liked, but you haven't watched.")
    print(" - Content-Based Filtering: Analyzes the genres/keywords of movies you've watched to recommend similar content.")


if __name__ == "__main__":
    main_test(user_id=2)
