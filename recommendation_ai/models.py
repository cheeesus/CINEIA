# models.py

from db import fetchall_dict, fetchone_dict, execute_query

def get_all_user_ids():
    query = "SELECT id FROM users"
    rows = fetchall_dict(query)
    return [r["id"] for r in rows]

def get_all_movie_ids():
    query = "SELECT id FROM movies"
    rows = fetchall_dict(query)
    return [r["id"] for r in rows]

def get_user_view_history(user_id):
    query = "SELECT movie_id FROM view_history WHERE user_id = %s"
    rows = fetchall_dict(query, (user_id,))
    return [r["movie_id"] for r in rows]

def get_user_view_dict():
    # 返回 {user_id: set(movie_id)} 的格式
    query = "SELECT user_id, movie_id FROM view_history"
    rows = fetchall_dict(query)
    user_view_map = {}
    for r in rows:
        u = r["user_id"]
        m = r["movie_id"]
        if u not in user_view_map:
            user_view_map[u] = set()
        user_view_map[u].add(m)
    return user_view_map

def get_movie_content_data():
    """
    返回 movie_id -> dict of genres + keywords
    假设有辅助表 movie_genre(movie_id, genre_id) 和 movie_keyword(movie_id, keyword_id)
    """
    data = {}
    # genres
    genre_rows = fetchall_dict("SELECT movie_id, genre_id FROM movie_genre")
    for r in genre_rows:
        mid = r["movie_id"]
        gid = r["genre_id"]
        data.setdefault(mid, {"genres": [], "keywords": []})
        data[mid]["genres"].append(gid)

    # keywords
    keyword_rows = fetchall_dict("SELECT movie_id, keyword_id FROM movie_keyword")
    for r in keyword_rows:
        mid = r["movie_id"]
        kid = r["keyword_id"]
        data.setdefault(mid, {"genres": [], "keywords": []})
        data[mid]["keywords"].append(kid)

    return data


def get_movie_titles(movie_ids):
    if not movie_ids:
        return {}
    format_ids = tuple(movie_ids)
    query = f"SELECT id, title FROM movies WHERE id IN %s"
    result = fetchall_dict(query, (format_ids,))
    return {row["id"]: row["title"] for row in result}
