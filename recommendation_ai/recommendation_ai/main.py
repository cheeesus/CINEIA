from .database import fetch_view_data, get_connection
from .recommendation_model import RecommendationModel
from .config import RATING_SCALE

def main():
    df_view = fetch_view_data()
    if df_view.empty:
        print(" view_history null, fake_data.py first ")
        return

    print("view_history preview:")
    print(df_view.head())

    model = RecommendationModel(rating_scale=RATING_SCALE)
    model.train(df_view)

    all_movie_ids = df_view['movie_id'].unique()
    user_id = 1
    top_n = 3
    recommended = model.recommend_for_user(user_id, all_movie_ids, top_n=top_n)

    if recommended:
        print(f"\nto user {user_id} rec {top_n} movies：")
        conn = get_connection()
        with conn.cursor() as cur:
            for (mid, score) in recommended:
                cur.execute("SELECT title FROM movies WHERE id = %s", (int(mid),))  # 强制转换为 Python int
                row = cur.fetchone()
                title = row[0] if row else f"Movie #{mid}"
                print(f"  movies ID={mid} title={title} score I guess={score:.2f}")
        conn.close()
    else:
        print(f"user {user_id} no rec")

if __name__ == "__main__":
    main()
