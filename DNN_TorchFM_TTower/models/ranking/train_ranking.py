import os
import argparse
import torch
import torch.nn as nn
from torch.utils.data import TensorDataset, DataLoader
from sklearn.model_selection import train_test_split
from tqdm import tqdm

from DNN_TorchFM_TTower.models.db import fetchone_dict
from DNN_TorchFM_TTower.models.ranking.feature_engineer import build_training_df
from DNN_TorchFM_TTower.models.ranking.custom_deepfm import DeepFM

# Ensure save directory exists
os.makedirs("saved_model", exist_ok=True)
MODEL_PATH = "saved_model/deepfm_ranker.pt"

def _vocab_sizes():
    mu = fetchone_dict("SELECT MAX(id) AS m FROM users")["m"] or 0
    mm = fetchone_dict("SELECT MAX(id) AS m FROM movies")["m"] or 0
    mg = fetchone_dict("SELECT MAX(id) AS m FROM genres")["m"] or 0
    # 四个稀疏域：user_id, movie_id, genre_id, pref_genre_id
    return [mu + 2, mm + 2, mg + 2, mg + 2]

def _to_tensor(df, sparse_cols, dense_cols):
    Xs = torch.tensor(df[sparse_cols].values, dtype=torch.long)
    Xd = torch.tensor(df[dense_cols].values, dtype=torch.float32)
    y  = torch.tensor(df["label"].values, dtype=torch.float32)
    return TensorDataset(Xs, Xd, y)

def main(epochs=3, batch_size=2048, neg_ratio=1):
    df = build_training_df(neg_ratio)
    if df.empty:
        print("[train_ranking] no training data")
        return

    # 训练时 recall_score 设为常数 0.0
    df["recall_score"] = 0.0

    sparse_cols = ["user_id", "movie_id", "genre_id", "pref_genre_id"]
    dense_cols  = ["recall_score", "vote_average", "popularity", "age"]

    print(f"[train_ranking] samples={len(df)}  pos:neg≈1:{neg_ratio}")

    # 划分训练/验证集
    tr_df, val_df = train_test_split(df, test_size=0.2, random_state=42)
    train_loader = DataLoader(_to_tensor(tr_df, sparse_cols, dense_cols), 
                              batch_size=batch_size, shuffle=True)
    val_loader   = DataLoader(_to_tensor(val_df, sparse_cols, dense_cols),   
                              batch_size=batch_size, shuffle=False)

    # 构建 DeepFM 模型
    field_dims = _vocab_sizes()
    model = DeepFM(
        field_dims,
        num_dense=len(dense_cols),
        embed_dim=16,
        mlp_dims=(128, 64),
        dropout=0.2
    )

    device = "cuda" if torch.cuda.is_available() else "cpu"
    model.to(device)

    optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)
    loss_fn   = nn.BCEWithLogitsLoss()

    # 训练 & 验证循环
    for ep in range(1, epochs + 1):
        # 训练
        model.train()
        total_loss, count = 0.0, 0
        for Xs, Xd, y in tqdm(train_loader, desc=f"Ep {ep}/{epochs}", ncols=80):
            Xs, Xd, y = Xs.to(device), Xd.to(device), y.to(device)
            optimizer.zero_grad()
            loss = loss_fn(model(Xs, Xd), y)
            loss.backward()
            optimizer.step()
            total_loss += loss.item() * y.size(0)
            count += y.size(0)
        print(f"  train_loss={total_loss/count:.4f}")

        # 验证
        model.eval()
        total_val, count_val = 0.0, 0
        with torch.no_grad():
            for Xs, Xd, y in val_loader:
                Xs, Xd, y = Xs.to(device), Xd.to(device), y.to(device)
                v_loss = loss_fn(model(Xs, Xd), y).item()
                total_val += v_loss * y.size(0)
                count_val += y.size(0)
        print(f"  val_loss  ={total_val/count_val:.4f}")

    # 保存模型
    torch.save(model.cpu().state_dict(), MODEL_PATH)
    print("DeepFM saved →", MODEL_PATH)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--epochs",    type=int, default=3)
    parser.add_argument("--batch",     type=int, default=2048)
    parser.add_argument("--neg_ratio", type=int, default=1)
    args = parser.parse_args()
    main(args.epochs, args.batch, args.neg_ratio)