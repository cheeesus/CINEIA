import pytest

# 这里用绝对导入: from recommendation_ai.XXX
from recommendation_ai.database import fetch_view_data
from recommendation_ai.recommendation_model import RecommendationModel
from recommendation_ai.config import RATING_SCALE

def test_view_data_not_empty():
    df = fetch_view_data()
    assert not df.empty, "view_history 里居然是空？请先运行 fake_data.py"

def test_recommendation_model():
    df = fetch_view_data()
    model = RecommendationModel(rating_scale=RATING_SCALE)
    model.train(df)

    all_movie_ids = df['movie_id'].unique()
    result = model.recommend_for_user(user_id=1, all_movie_ids=all_movie_ids, top_n=2)
    assert len(result) == 2, "推荐结果数量应是2"

    print(f"测试推荐返回：{result}")
