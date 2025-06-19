# models/recall/cold_start.py
from __future__ import annotations

from typing import List, Dict
from DNN_TorchFM_TTower.models.db import fetchall_dict
from DNN_TorchFM_TTower.models.ranking.infer_ranking import rank_candidates

# --------------------------------------------------------------------------- #
# helpers                                                                     #
# --------------------------------------------------------------------------- #

def get_user_genres(user_id: int) -> List[int]:
    """
    Return the genre-ids a user explicitly picked during onboarding.
    Feel free to replace this with your own query.
    """
    rows = fetchall_dict(
        "SELECT genre_id FROM user_preferences WHERE user_id=%s", (user_id,)
    )
    return [r["genre_id"] for r in rows] if rows else []


def _popular_movies(limit: int = 600) -> List[Dict]:
    """
    A popularity-based pool that is large enough to leave room for genre
    filtering.  Extra columns are fetched because DeepFM needs them later.
    """
    sql = """
        SELECT m.id,
               mg.genre_id,
               m.vote_average,
               m.popularity,
               m.vote_count
        FROM   movies m
        JOIN   movie_genre mg ON mg.movie_id = m.id
        WHERE  m.vote_count > 0
        ORDER  BY m.vote_average DESC, m.vote_count DESC
        LIMIT  %s
    """
    return fetchall_dict(sql, (limit,))


def _select_candidates(user_genres: List[int],
                       pool_size: int = 300) -> tuple[list[int], list[float]]:
    """
    1. Keep movies whose `genre_id` is in `user_genres`.
    2. If that set is too small, back-fill with the remaining popular titles.
    3. Build a simple recall-score: 1.0 when the genre matches, else 0.0.
    """
    rows = _popular_movies(limit=600)          # (≥ pool_size to allow filtering)

    # step-1: genre bias ------------------------------------------------------
    if user_genres:
        primary = [r for r in rows if r["genre_id"] in user_genres]
    else:                                     # brand-new user: no preference yet
        primary = []

    # step-2: fill up ---------------------------------------------------------
    seen   = {r["id"] for r in primary}
    filler = [r for r in rows if r["id"] not in seen]
    selected = (primary + filler)[:pool_size]

    # step-3: build recall scores --------------------------------------------
    mids   = [r["id"] for r in selected]
    scores = [1.0 if r["genre_id"] in user_genres else 0.0 for r in selected]
    return mids, scores


# --------------------------------------------------------------------------- #
# public API                                                                  #
# --------------------------------------------------------------------------- #
def recommend_cold_start(user_id: int, top_n: int = 20) -> list[int]:
    """
    Genre-aware cold-start recommendation.

    Parameters
    ----------
    user_id : int
        The (new) user we are producing recommendations for.
    top_n   : int
        Number of items returned.

    Returns
    -------
    List[int] – movie ids, already ranked.
    """
    user_genres = get_user_genres(user_id)
    recall_ids, recall_scores = _select_candidates(user_genres, pool_size=300)
    if not recall_ids:                           # empty DB edge-case
        return []

    return rank_candidates(
        user_id,
        recall_ids,
        recall_scores,
        top_n=top_n
    )


# def recommend_cold_start(top_n=10):
#     """
#     针对无历史用户(冷启动)：先选一批高评分热门电影，再随机抽取 top_n。
#     示例：我们假设在 movies 表中有 vote_average, vote_count 字段。
#     """
#     query = """
#         SELECT id
#         FROM movies
#         WHERE vote_count > 0
#         ORDER BY vote_average DESC, vote_count DESC
#         LIMIT 50
#     """
#     rows = fetchall_dict(query)
#     if not rows:
#         return []
#     candidate_ids = [r["id"] for r in rows]
    
#     # 从这 50 部评分最高的影片里随机抽 top_n
#     if len(candidate_ids) <= top_n:
#         return candidate_ids
#     return random.sample(candidate_ids, top_n)
