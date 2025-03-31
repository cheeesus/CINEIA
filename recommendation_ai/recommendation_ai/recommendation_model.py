import pandas as pd
from surprise import Dataset, Reader, KNNBasic
from surprise.model_selection import train_test_split


class RecommendationModel:
    def __init__(self, rating_scale=(1, 5), algo_class=KNNBasic, algo_params=None):
        self.rating_scale = rating_scale
        self.algo_class = algo_class
        self.algo_params = algo_params or {}
        self.algo = None

    def train(self, df: pd.DataFrame):
        reader = Reader(rating_scale=self.rating_scale)
        data = Dataset.load_from_df(df[['user_id', 'movie_id', 'rating']], reader)
        trainset, testset = train_test_split(data, test_size=0.2, random_state=42)

        self.algo = self.algo_class(**self.algo_params)
        self.algo.fit(trainset)

        # from surprise import accuracy
        # predictions = self.algo.test(testset)
        # rmse = accuracy.rmse(predictions)

    def recommend_for_user(self, user_id, all_movie_ids, top_n=5):
        if not self.algo:
            raise RuntimeError("模型尚未训练，请先调用 train(df)。")

        predictions = []
        for mid in all_movie_ids:
            pred = self.algo.predict(user_id, mid)
            predictions.append((mid, pred.est))

        predictions.sort(key=lambda x: x[1], reverse=True)
        return predictions[:top_n]
