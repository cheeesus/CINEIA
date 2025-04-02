# models/db.py
import psycopg2
from psycopg2.extras import RealDictCursor
from collections import Counter
from config import DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT

def get_connection():
    return psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )

def fetchall_dict(query, params=None):
    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query, params)
            return cur.fetchall()

def fetchone_dict(query, params=None):
    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query, params)
            return cur.fetchone()


def get_movie_titles(movie_ids):
    query = "SELECT id, title FROM movies WHERE id = ANY(%s)"
    rows = fetchall_dict(query, (movie_ids,))
    return {row["id"]: row["title"] for row in rows}


def get_max_user_id():
    row = fetchone_dict("SELECT MAX(id) as m FROM users")
    return row["m"] or 0

def get_max_movie_id():
    row = fetchone_dict("SELECT MAX(id) as m FROM movies")
    return row["m"] or 0

def get_all_movie_ids_with_language():
    rows = fetchall_dict("SELECT id, original_language FROM movies")
    return [(r["id"], r["original_language"]) for r in rows if r["original_language"]]


def get_user_view_languages(user_id):
    query = """
        SELECT m.original_language
        FROM view_history v
        JOIN movies m ON v.movie_id = m.id
        WHERE v.user_id = %s
    """
    rows = fetchall_dict(query, (user_id,))
    lang_counter = Counter(r["original_language"] for r in rows if r["original_language"])
    if not lang_counter:
        return set()
    top_languages = {lang for lang, _ in lang_counter.most_common(2)}
    return top_languages