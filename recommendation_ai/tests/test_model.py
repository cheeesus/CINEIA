# tests/test_model.py

import pytest
import pandas as pd
from recommendation_ai.database import fetch_view_data  # 或其他函数
from recommendation_ai.recommendation_model import RecommendationModel


def test_recommendation_model():
    # 构造一份简单的样本数据
    data = {
        "user_id": [1, 1, 2, 2, 3, 3],
        "movie_id": [10, 20, 10, 30, 20, 30],
        "rating":   [3, 4, 5, 2, 3, 5]
    }
    df = pd.DataFrame(data)

    # 初始化模型
    model = RecommendationModel(rating_scale=(0, 5))
    model.train(df)

    # 所有电影 IDs
    all_movie_ids = df['movie_id'].unique()

    # 给 user_id=1 做推荐
    recommended = model.recommend_for_user(user_id=1, all_movie_ids=all_movie_ids, top_n=2)
    # recommended 格式类似于: [(movie_id, pred_score), (movie_id, pred_score), ...]

    # 检查返回数量
    assert len(recommended) == 2, "返回的推荐数量不正确"

    # 打印看看
    print("Test recommendation for user=1 =>", recommended)
