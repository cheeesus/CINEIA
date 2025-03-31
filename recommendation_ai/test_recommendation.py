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
from main_recommender import recommend_cf_for_user, recommend_content_for_user
from models import get_movie_titles

if __name__ == "__main__":
    user_id = 1    # massly :)

    print("Generating recommendations for user user_id =", user_id, "...\n")

    # Collaborative Filtering recommendation
    print("[Collaborative Filtering] Recommendation results (based on similarity of movies watched with other users):")
    start_cf = time.time()
    cf_results = recommend_cf_for_user(user_id)
    end_cf = time.time()
    cf_titles = get_movie_titles(cf_results)
    for mid in cf_results:
        print(f" - {mid}: {cf_titles.get(mid, '[Unknown Movie]')}")
    print(f"Time taken for Collaborative Filtering: {end_cf - start_cf:.4f} seconds")

    # Content-Based Filtering recommendation
    print("\n[Content-Based Filtering] Recommendation results (based on similarity of content with movies you've watched):")
    start_content = time.time()
    content_results = recommend_content_for_user(user_id)
    end_content = time.time()
    content_titles = get_movie_titles(content_results)
    for mid in content_results:
        print(f" - {mid}: {content_titles.get(mid, '[Unknown Movie]')}")
    print(f"Time taken for Content-Based Filtering: {end_content - start_content:.4f} seconds")

    print("\nExplanation:")
    print(" - Collaborative Filtering: Recommends movies that other users with similar viewing habits have liked, but you haven't watched.")
    print(" - Content-Based Filtering: Analyzes the genres and keywords of movies you've watched to recommend similar content.")

