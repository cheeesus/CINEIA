# tests/test_database.py

import pytest
from recommendation_ai.database import fetch_view_data  # 或其他函数
from recommendation_ai.recommendation_model import RecommendationModel


def test_fetch_view_data():
    df = fetch_view_data()
    # 简单测试：DataFrame 不应该为空
    assert not df.empty, "fetch_view_data() 返回空表，请检查数据库是否有数据"
    # 再检查列是否包含 user_id, movie_id, rating
    expected_cols = {"user_id", "movie_id", "rating"}
    assert expected_cols.issubset(df.columns), f"返回的列中缺少 {expected_cols - set(df.columns)}"
