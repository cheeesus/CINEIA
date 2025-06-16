# DNN_TorchFM_TTower/models/ranking/feature_engineer.py

"""
Assemble features for DeepFM training and inference,
now including the user's preferred genre as an extra sparse field.
"""

from collections import defaultdict
from typing import List
import pandas as pd

from DNN_TorchFM_TTower.models.db import fetchall_dict, fetchone_dict

def _get_movie_features() -> pd.DataFrame:
    rows = fetchall_dict("""
        SELECT movie_id, genre_id
        FROM movie_genre
        ORDER BY movie_id, genre_id
    """)
    first_genre = {}
    for r in rows:
        first_genre.setdefault(r["movie_id"], r["genre_id"])

    rows = fetchall_dict("""
        SELECT id AS movie_id,
               vote_average,
               popularity
        FROM movies
    """)
    for r in rows:
        r["genre_id"] = first_genre.get(r["movie_id"], 0)
    return pd.DataFrame(rows)

def _get_user_features() -> pd.DataFrame:
    rows = fetchall_dict("SELECT id AS user_id, COALESCE(age, 0) AS age FROM users")
    return pd.DataFrame(rows)

def build_training_df(neg_ratio: int = 1) -> pd.DataFrame:
    pos_rows = fetchall_dict("SELECT user_id, movie_id FROM view_history")
    if not pos_rows:
        return pd.DataFrame()

    pos_df = pd.DataFrame(pos_rows)
    pos_df["label"] = 1

    all_movies = {r["movie_id"] for r in fetchall_dict("SELECT id AS movie_id FROM movies")}
    user_pos  = defaultdict(set)
    for r in pos_rows:
        user_pos[r["user_id"]].add(r["movie_id"])

    import random
    neg_records = []
    for u, watched in user_pos.items():
        cand = list(all_movies - watched)
        k = min(len(cand), neg_ratio * len(watched))
        for m in random.sample(cand, k):
            neg_records.append({"user_id": u, "movie_id": m, "label": 0})
    neg_df = pd.DataFrame(neg_records)

    data_df = pd.concat([pos_df, neg_df], ignore_index=True)

    movies_df = _get_movie_features()
    users_df  = _get_user_features()

    df = data_df.merge(movies_df, on="movie_id", how="left") \
                .merge(users_df,  on="user_id", how="left")

    # <-- NEW: attach the user's chosen genre -->
    pref_rows = fetchall_dict("SELECT user_id, genre_id AS pref_genre_id FROM user_preferences")
    pref_df   = pd.DataFrame(pref_rows)
    df = df.merge(pref_df, on="user_id", how="left")
    df["pref_genre_id"].fillna(0, inplace=True)
    df["pref_genre_id"] = df["pref_genre_id"].astype(int)

    df.fillna(0, inplace=True)
    return df

def build_infer_df(
    user_id: int,
    movie_ids: List[int],
    recall_scores: List[float]
) -> pd.DataFrame:
    movies_df = _get_movie_features()
    users_df  = _get_user_features()

    infer_df = pd.DataFrame({
        "user_id":      user_id,
        "movie_id":     movie_ids,
        "recall_score": recall_scores,
    })

    # <-- NEW: single preference for inference -->
    pref_rows = fetchall_dict(
        "SELECT genre_id AS pref_genre_id FROM user_preferences WHERE user_id = %s",
        (user_id,)
    )
    if pref_rows:
        pref_id = pref_rows[0]["pref_genre_id"]
    else:
        pref_id = 0
    infer_df["pref_genre_id"] = pref_id

    infer_df = infer_df.merge(movies_df, on="movie_id", how="left") \
                       .merge(users_df,  on="user_id",  how="left")

    infer_df.fillna(0, inplace=True)
    return infer_df
