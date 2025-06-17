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
    from collections import defaultdict
    import pandas as pd
    import random

    # 正样本：用户观看历史
    pos_rows = fetchall_dict("SELECT user_id, movie_id FROM view_history")
    if not pos_rows:
        return pd.DataFrame()

    pos_df = pd.DataFrame(pos_rows)
    pos_df["label"] = 1

    # 所有电影 & 构造负样本（未看过的）
    all_movies = {r["movie_id"] for r in fetchall_dict("SELECT id AS movie_id FROM movies")}
    user_pos = defaultdict(set)
    for r in pos_rows:
        user_pos[r["user_id"]].add(r["movie_id"])

    neg_records = []
    for u, watched in user_pos.items():
        cand = list(all_movies - watched)
        k = min(len(cand), neg_ratio * len(watched))
        for m in random.sample(cand, k):
            neg_records.append({"user_id": u, "movie_id": m, "label": 0})
    neg_df = pd.DataFrame(neg_records)

    data_df = pd.concat([pos_df, neg_df], ignore_index=True)

    # 加载电影特征 & 用户特征
    movies_df = _get_movie_features()
    users_df  = _get_user_features()

    df = data_df.merge(movies_df, on="movie_id", how="left") \
                .merge(users_df,  on="user_id", how="left")

    # 加入用户偏好题材（pref_genre_id）
    pref_rows = fetchall_dict("SELECT user_id, genre_id AS pref_genre_id FROM user_preferences")
    pref_df = pd.DataFrame(pref_rows)
    df = df.merge(pref_df, on="user_id", how="left")
    df["pref_genre_id"].fillna(0, inplace=True)
    df["pref_genre_id"] = df["pref_genre_id"].astype(int)

    # ===== 新增：是否标记为收藏（favorites）=====
    fav_rows = fetchall_dict("""
        SELECT l.user_id, lm.movie_id
        FROM lists l
        JOIN list_movies lm ON l.id = lm.list_id
        WHERE l.name = 'favorites'
    """)
    fav_df = pd.DataFrame(fav_rows)
    fav_df["is_favorite"] = 1

    df = df.merge(fav_df, on=["user_id", "movie_id"], how="left")
    df["is_favorite"].fillna(0, inplace=True)
    df["is_favorite"] = df["is_favorite"].astype(int)

    # ===== 新增：用户历史行为统计特征 =====
    watch_count = pos_df.groupby("user_id")["movie_id"].count().reset_index()
    watch_count.columns = ["user_id", "user_watch_count"]

    fav_count = fav_df.groupby("user_id")["movie_id"].count().reset_index()
    fav_count.columns = ["user_id", "user_fav_count"]

    df = df.merge(watch_count, on="user_id", how="left")
    df = df.merge(fav_count, on="user_id", how="left")

    df["user_watch_count"].fillna(0, inplace=True)
    df["user_fav_count"].fillna(0, inplace=True)

    # 最后统一填充所有空值
    df.fillna(0, inplace=True)
    return df


def build_infer_df(user_id: int, candidate_movies: list[int]) -> pd.DataFrame:
    """构造用于排序阶段的输入 DataFrame"""
    rows = [{"user_id": user_id, "movie_id": mid} for mid in candidate_movies]
    df = pd.DataFrame(rows)

    # 加载电影特征 & 用户特征
    movies_df = _get_movie_features()
    users_df  = _get_user_features()

    df = df.merge(movies_df, on="movie_id", how="left") \
           .merge(users_df,  on="user_id", how="left")

    # 用户偏好题材
    pref_rows = fetchall_dict("SELECT user_id, genre_id AS pref_genre_id FROM user_preferences")
    pref_df   = pd.DataFrame(pref_rows)
    df = df.merge(pref_df, on="user_id", how="left")
    df["pref_genre_id"].fillna(0, inplace=True)
    df["pref_genre_id"] = df["pref_genre_id"].astype(int)

    # 是否收藏该电影
    fav_rows = fetchall_dict("""
        SELECT l.user_id, lm.movie_id
        FROM lists l
        JOIN list_movies lm ON l.id = lm.list_id
        WHERE l.name = 'favorites'
    """)
    fav_df = pd.DataFrame(fav_rows)
    fav_df["is_favorite"] = 1
    df = df.merge(fav_df, on=["user_id", "movie_id"], how="left")
    df["is_favorite"].fillna(0, inplace=True)
    df["is_favorite"] = df["is_favorite"].astype(int)

    # 用户行为统计
    watch_count = fetchall_dict("SELECT user_id, COUNT(*) AS user_watch_count FROM view_history GROUP BY user_id")
    fav_count   = fetchall_dict("""
        SELECT l.user_id, COUNT(*) AS user_fav_count
        FROM lists l JOIN list_movies lm ON l.id = lm.list_id
        WHERE l.name = 'favorites' GROUP BY l.user_id
    """)
    watch_df = pd.DataFrame(watch_count)
    fav_df   = pd.DataFrame(fav_count)
    df = df.merge(watch_df, on="user_id", how="left")
    df = df.merge(fav_df,   on="user_id", how="left")

    df["user_watch_count"].fillna(0, inplace=True)
    df["user_fav_count"].fillna(0, inplace=True)

    df.fillna(0, inplace=True)
    return df

def fetch_user_favorite_movies() -> dict[int, set[int]]:
    """返回字典 user_id → 他们收藏的 movie_id 集合"""
    rows = fetchall_dict("""
        SELECT lm.movie_id, l.user_id
        FROM list_movies lm
        JOIN lists l ON lm.list_id = l.id
        WHERE l.name = 'favorites'
    """)
    fav_map = {}
    for r in rows:
        fav_map.setdefault(r["user_id"], set()).add(r["movie_id"])
    return fav_map