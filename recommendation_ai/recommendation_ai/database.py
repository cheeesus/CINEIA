# recommendation_ai/database.py

import psycopg2
import pandas as pd
from .config import DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT

def get_connection():
    conn = psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )
    return conn

def fetch_view_data():
    sql = """
    SELECT user_id, movie_id, rating
    FROM view_history
    """
    conn = get_connection()
    try:
        df = pd.read_sql(sql, conn)
    finally:
        conn.close()
    return df


# ================ get top-N movies, highest score ==================
def fetch_top_movies_by_vote_average(limit=5):
    """
    从 movies 表按 vote_average DESC + vote_count DESC 排序，获取 top-N
    如果你的数据库里没这两个字段或没数据，可改用 'popularity' 等。
    """
    sql = """
    SELECT id, title, vote_average, vote_count
    FROM movies
    ORDER BY vote_average DESC NULLS LAST, vote_count DESC NULLS LAST
    LIMIT %s
    """
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, (limit,))
            rows = cur.fetchall()
            # return list: [(id, title, vote_average, vote_count), ...]
            return rows
    finally:
        conn.close()

# ================ create new client and the score==================
def create_user_with_preferences(preferred_movies, default_rating=5):
    """
    preferred_movies: [ movie_id, ... ] or [ (movie_id, rating), ... ]
    """
    import random
    conn = get_connection()
    cur = conn.cursor()
    try:
        # random regenerate email
        random_email = f"newuser_{random.randint(1000,9999)}@example.com"

        cur.execute("""
            INSERT INTO users (email, password_hash, age)
            VALUES (%s, 'pwdhash', 20)
            RETURNING id
        """, (random_email,))
        new_user_id = cur.fetchone()[0]

        # insert 
        for item in preferred_movies:
            if isinstance(item, tuple):
                (movie_id, rating) = item
            else:
                movie_id = item
                rating = default_rating

            cur.execute("""
                INSERT INTO view_history (user_id, movie_id, rating)
                VALUES (%s, %s, %s)
            """, (new_user_id, movie_id, rating))

        conn.commit()
        return new_user_id
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cur.close()
        conn.close()

