# 文件: models/ranking/train_ranking.py
import os
import argparse

import torch
import torch.nn as nn
from torch.utils.data import TensorDataset, DataLoader
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, recall_score
from tqdm import tqdm

from DNN_TorchFM_TTower.models.db import fetchone_dict
from DNN_TorchFM_TTower.models.ranking.feature_engineer import build_training_df
from DNN_TorchFM_TTower.models.ranking.custom_deepfm import DeepFM

import matplotlib.pyplot as plt

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

    df["recall_score"] = 0.0
    sparse_cols = ["user_id", "movie_id", "genre_id", "pref_genre_id"]
    dense_cols = ["recall_score", "vote_average", "popularity", "age", "is_favorite", "user_watch_count", "user_fav_count"]

    print(f"[train_ranking] samples={len(df)}  pos:neg≈1:{neg_ratio}")

    tr_df, val_df = train_test_split(df, test_size=0.2, random_state=42)
    train_loader = DataLoader(_to_tensor(tr_df, sparse_cols, dense_cols),
                              batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(_to_tensor(val_df, sparse_cols, dense_cols),
                              batch_size=batch_size, shuffle=False)

    field_dims = _vocab_sizes()
    model = DeepFM(
        field_dims,
        num_dense=len(dense_cols),
        embed_dim=32,
        mlp_dims=(128, 64),
        dropout=0.2
    )

    device = "cuda" if torch.cuda.is_available() else "cpu"
    model.to(device)

    optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)
    loss_fn = nn.BCEWithLogitsLoss()

    train_losses, val_losses = [], []  # Added to store losses

    for ep in range(1, epochs + 1):
        model.train()
        total_loss, count = 0.0, 0
        for Xs, Xd, y in tqdm(train_loader, desc=f"Ep {ep}/{epochs}", ncols=80):
            Xs, Xd, y = Xs.to(device), Xd.to(device), y.to(device)
            optimizer.zero_grad()
            logits = model(Xs, Xd)
            loss = loss_fn(logits, y)
            loss.backward()
            optimizer.step()
            total_loss += loss.item() * y.size(0)
            count += y.size(0)
        train_loss = total_loss / count
        train_losses.append(train_loss)  # Log training loss

        model.eval()
        total_val, count_val = 0.0, 0
        with torch.no_grad():
            for Xs, Xd, y in val_loader:
                Xs, Xd, y = Xs.to(device), Xd.to(device), y.to(device)
                v_loss = loss_fn(model(Xs, Xd), y).item()
                total_val += v_loss * y.size(0)
                count_val += y.size(0)
        val_loss = total_val / count_val
        val_losses.append(val_loss)  # Log validation loss

        print(f"  train_loss={train_loss:.4f}  val_loss={val_loss:.4f}")

    torch.save(model.cpu().state_dict(), MODEL_PATH)
    print("DeepFM saved →", MODEL_PATH)

    # Added: Plotting
    import matplotlib.pyplot as plt
    plt.figure(figsize=(10, 5))
    plt.plot(range(1, epochs + 1), train_losses, label='Train Loss')
    plt.plot(range(1, epochs + 1), val_losses, label='Validation Loss')
    plt.xlabel('Epochs')
    plt.ylabel('Loss')
    plt.title('DeepFM Model Training')
    plt.legend()
    plt.grid(True)
    plt.show()
    # Save the plot as an image file
    plt.savefig('DeepFM_training_plot.png', dpi=300)

    # ===== 新增：在验证集上计算 Accuracy 和 Recall =====
    model.eval()
    all_true, all_pred = [], []
    with torch.no_grad():
        for Xs, Xd, y in val_loader:
            # 同步到当前 device
            Xs, Xd, y = Xs.to(device), Xd.to(device), y.to(device)
            logits = model(Xs, Xd)
            probs  = torch.sigmoid(logits)
            preds  = (probs >= 0.5).float()

            all_true.extend(y.cpu().numpy().tolist())
            all_pred.extend(preds.cpu().numpy().tolist())

    acc = accuracy_score(all_true, all_pred)
    rec = recall_score(all_true, all_pred, zero_division=0)
    # print("\n DeepFM Re-Ranker Evaluation Summary")
    # print(f"• Validation Set: 20% of the full training data")
    # print(f"• Final Validation Loss: {total_val/count_val:.4f}")
    # print(f"\nThe error between the model's prediction and the true label on new, unseen data (the validation set)")
    # print(f"• Accuracy: {acc * 100:.2f}% — Measures how often the model correctly classifies preferences.")
    # print(f"\n Of all predictions, the proportion of the total number of samples in which the predicted result is consistent with the true result")
    # print(f"• Recall:   {rec * 100:.2f}% — Measures how many of the true positives were correctly predicted.")
    # print(f"\nwhich means all user's liked movies that were successfully predicted by the model")

    print("\n DeepFM Re-Ranker Evaluation Summary")
    print(f"• Validation Set: 20% of the full training data")
    print(f"• Final Validation Loss: {total_val/count_val:.4f}")
    print("  ↪︎ Measures the average prediction error (binary cross-entropy) on validation samples.")

    print(f"• Accuracy: {acc * 100:.2f}% — Proportion of correct predictions among all ranking decisions.")
    print("  ↪︎ Accuracy = (True Positives + True Negatives) / Total Samples")
    print("  ↪︎ Reflects how well the model separates preferred and non-preferred movies.")

    print(f"• Recall:   {rec * 100:.2f}% — Proportion of all truly liked movies that were correctly identified.")
    print("  ↪︎ Recall = True Positives / (True Positives + False Negatives)")
    print("  ↪︎ High recall ensures fewer liked movies are missed in final recommendations.")



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--epochs",    type=int, default=3)
    parser.add_argument("--batch",     type=int, default=2048)
    parser.add_argument("--neg_ratio", type=int, default=1)
    args = parser.parse_args()
    main(args.epochs, args.batch, args.neg_ratio)
