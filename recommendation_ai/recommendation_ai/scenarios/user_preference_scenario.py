# recommendation_ai/scenarios/user_preference_scenario.py

from ..database import create_user_with_preferences, fetch_view_data, get_connection
from ..recommendation_model import RecommendationModel
from ..config import RATING_SCALE

def recommend_with_preference(preferred_movie_list):
    user_id = create_user_with_preferences(preferred_movie_list)  # 如 [(10,5), 20, 30...]

    # read data from database
    df_view = fetch_view_data()

    model = RecommendationModel(rating_scale=RATING_SCALE)
    model.train(df_view)

    all_movie_ids = df_view['movie_id'].unique()
    recommended = model.recommend_for_user(user_id, all_movie_ids, top_n=5)

    print(f"\nuser has the preferrence user ID={user_id} like {preferred_movie_list}")
    if not recommended:
        print("⚠️ too less movie")
        return

    # 显示推荐结果并查标题
    conn = get_connection()
    with conn.cursor() as cur:
        for (mid, score) in recommended:
            # Note: Force conversion mid => int(mid) in case psycopg2 throws "can't adapt type 'numpy.int64'"
            cur.execute("SELECT title FROM movies WHERE id = %s", (int(mid),))
            row = cur.fetchone()
            title = row[0] if row else f"Movie #{mid}"
            print(f"  Recommended Movie ID={mid}, Title={title}, Predicted Score={score:.2f}")
    conn.close()


if __name__ == "__main__":
    # test1：假设用户只喜欢 movie_id=1,3,5 (rating=5)
    # recommend_with_preference([1, 3, 5])

    # test2：用户对 movie_id=10,20,30 有不同评分    
    # recommend_with_preference([(10,5), (20,3), (30,4)])
    recommend_with_preference([1, 2, 3])
