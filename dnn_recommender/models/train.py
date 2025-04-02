# models/train.py
import os
import random
import time
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader

from db import fetchall_dict, fetchone_dict
from pytorch_model import TwoTowerMLPModel

os.makedirs("saved_model", exist_ok=True)

def get_all_users():
    rows = fetchall_dict("SELECT id FROM users")
    return [r["id"] for r in rows]

def get_all_movies():
    rows = fetchall_dict("SELECT id FROM movies")
    return [r["id"] for r in rows]

def get_movie_genres():
    rows = fetchall_dict("SELECT movie_id, genre_id FROM movie_genre")
    movie_genres = {}
    for r in rows:
        movie_id = r["movie_id"]
        genre_id = r["genre_id"]
        movie_genres.setdefault(movie_id, set()).add(genre_id)
    return movie_genres

def get_positive_samples():
    rows = fetchall_dict("SELECT user_id, movie_id FROM view_history")
    if not rows:
        return pd.DataFrame(columns=["user_id", "movie_id", "rating"])
    df = pd.DataFrame(rows)
    df["rating"] = 1
    return df

def generate_training_data(neg_ratio=1):

    pos_df = get_positive_samples()
    if pos_df.empty:
        print("No positive samples found in view_history, training data is empty!")
        return pd.DataFrame(columns=["user_id", "movie_id", "rating"])
    
    all_movies = set(get_all_movies())
    movie_genres = get_movie_genres()
    
    # 构造每个用户的正样本集合和观看的所有 genre 集合
    user_pos_map = pos_df.groupby("user_id")["movie_id"].apply(set).to_dict()
    user_genres = {}
    for user, pos_movies in user_pos_map.items():
        genres = set()
        for m in pos_movies:
            if m in movie_genres:
                genres.update(movie_genres[m])
        user_genres[user] = genres

    neg_records = []
    for user, pos_movies in user_pos_map.items():
        # 候选负样本：那些电影的 genre 与用户观看的 genre 没有交集
        user_watched_genres = user_genres.get(user, set())
        neg_candidates = []
        for m in all_movies - pos_movies:
            genres = movie_genres.get(m, set())
            # if movies without genre or genres not in user_watched_genres, add as neg_candidates
            if not genres or genres.isdisjoint(user_watched_genres):
                neg_candidates.append(m)
        num_neg = neg_ratio * len(pos_movies)
        if len(neg_candidates) < num_neg:
            neg_candidates = list(all_movies - pos_movies)
            num_neg = min(len(neg_candidates), num_neg)
        if neg_candidates:
            chosen = random.sample(neg_candidates, int(num_neg))
            for m in chosen:
                neg_records.append({"user_id": user, "movie_id": m, "rating": 0})
    
    neg_df = pd.DataFrame(neg_records)
    train_df = pd.concat([pos_df, neg_df], ignore_index=True)
    return train_df

class RecommendationDataset(Dataset):
    def __init__(self, df):
        self.users = torch.tensor(df["user_id"].values, dtype=torch.long)
        self.movies = torch.tensor(df["movie_id"].values, dtype=torch.long)
        self.ratings = torch.tensor(df["rating"].values, dtype=torch.float32)
    
    def __len__(self):
        return len(self.users)
    
    def __getitem__(self, idx):
        return self.users[idx], self.movies[idx], self.ratings[idx]

def get_max_user_id():
    row = fetchone_dict("SELECT MAX(id) as m FROM users")
    return row["m"] or 0

def get_max_movie_id():
    row = fetchone_dict("SELECT MAX(id) as m FROM movies")
    return row["m"] or 0

def main():
    total_start = time.time()
    df = generate_training_data(neg_ratio=1)
    if df.empty:
        print("No training data. Please insert more user and view_history data.")
        return
    
    print("Training data size:", len(df))
    print(f"The number of users actually participating in the training: {df['user_id'].nunique()}，Movies attended: {df['movie_id'].nunique()}")
    
    # 拆分训练集与验证集
    train_df, val_df = train_test_split(df, test_size=0.2, random_state=42)
    train_dataset = RecommendationDataset(train_df)
    val_dataset = RecommendationDataset(val_df)
    
    train_loader = DataLoader(train_dataset, batch_size=64, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=64, shuffle=False)
    
    max_user_id = get_max_user_id()
    max_movie_id = get_max_movie_id()
    print(f"Max user ID = {max_user_id}, Max movie ID = {max_movie_id}")
    
    embedding_dim = 32
    model = TwoTowerMLPModel(max_user_id, max_movie_id, embedding_dim=32, hidden_dim=64)
    
    # BCEWithLogitsLoss , model output raw logits
    criterion = nn.BCEWithLogitsLoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001, weight_decay=1e-5)  # 加入 L2 正则
    
    best_val_loss = float("inf")
    num_epochs = 20
    for epoch in range(num_epochs):
        epoch_start = time.time()
        model.train()
        train_losses = []
        for user_ids, movie_ids, ratings in train_loader:
            optimizer.zero_grad()
            logits = model(user_ids, movie_ids)
            loss = criterion(logits, ratings)
            loss.backward()
            optimizer.step()
            train_losses.append(loss.item())
        avg_train_loss = np.mean(train_losses)
        
        model.eval()
        val_losses = []
        with torch.no_grad():
            for user_ids, movie_ids, ratings in val_loader:
                logits = model(user_ids, movie_ids)
                loss = criterion(logits, ratings)
                val_losses.append(loss.item())
        avg_val_loss = np.mean(val_losses)
        
        epoch_time = time.time() - epoch_start
        print(f"Epoch {epoch+1}/{num_epochs} | TrainLoss={avg_train_loss:.4f}, ValLoss={avg_val_loss:.4f} | Time={epoch_time:.2f}s")
        if avg_val_loss < best_val_loss:
            best_val_loss = avg_val_loss
            torch.save(model.state_dict(), "saved_model/dnn_recommender.pt")
            print("Model saved.")
    total_time = time.time() - total_start
    print(f"Training completed in {total_time:.2f} seconds.")

if __name__ == "__main__":
    main()
