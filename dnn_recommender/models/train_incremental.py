# models/train_incremental.py

import os
import time
import numpy as np

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader

from models.db import fetchone_dict
from models.train import generate_training_data, RecommendationDataset
from models.pytorch_model import TwoTowerMLPModel

def incremental_train(neg_ratio=1, epochs=3, model_path="saved_model/dnn_recommender.pt"):
    """
    执行一次小规模的增量训练，让模型纳入最新的用户行为记录。
    1. 重新生成正负样本
    2. 加载已有模型参数
    3. 只训练少量 epochs
    4. 覆盖保存或另存一份模型参数
    """
    # Step 1: 生成最新数据
    df = generate_training_data(neg_ratio=neg_ratio)
    if df.empty:
        print("No training data found, skipping incremental training.")
        return
    
    dataset = RecommendationDataset(df)
    data_loader = DataLoader(dataset, batch_size=64, shuffle=True)

    # Step 2: 加载现有模型
    max_user_id = fetchone_dict("SELECT MAX(id) as m FROM users")["m"] or 0
    max_movie_id = fetchone_dict("SELECT MAX(id) as m FROM movies")["m"] or 0
    
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Base model file {model_path} not found. Please run train.py first.")
    
    model = TwoTowerMLPModel(max_user_id, max_movie_id, embedding_dim=32, hidden_dim=64)
    model.load_state_dict(torch.load(model_path, map_location=torch.device("cpu")))
    
    # Step 3: 增量小批量训练
    criterion = nn.BCEWithLogitsLoss()
    optimizer = optim.Adam(model.parameters(), lr=0.0005, weight_decay=1e-5)
    # 可根据实际情况调整 lr
    
    model.train()
    start_time = time.time()
    for e in range(epochs):
        losses = []
        for user_ids, movie_ids, ratings in data_loader:
            optimizer.zero_grad()
            logits = model(user_ids, movie_ids)
            loss = criterion(logits, ratings)
            loss.backward()
            optimizer.step()
            losses.append(loss.item())
        avg_loss = np.mean(losses)
        print(f"[Incremental Epoch {e+1}/{epochs}] Avg Loss = {avg_loss:.4f}")
    
    print(f"Incremental training completed in {time.time() - start_time:.2f} s.")
    
    # Step 4: 保存更新后的模型
    torch.save(model.state_dict(), model_path)
    print("Incrementally updated model saved.")

if __name__ == "__main__":
    # 示例： python train_incremental.py
    incremental_train(neg_ratio=1, epochs=3)
