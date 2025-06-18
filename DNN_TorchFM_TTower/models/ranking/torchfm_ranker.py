"""
torchfm_ranker.py
"""

from pathlib import Path
from typing import Sequence

import torch
# from torchfm.deepfm import DeepFM
from DNN_TorchFM_TTower.models.ranking.torchfm.deepfm import DeepFM

MODEL_PATH = Path("saved_model/deepfm_ranker.pt")


def create_model(field_dims: Sequence[int],
                 embed_dim: int = 16):
    """
    field_dims : List[int]  每个 sparse 特征（user_id, movie_id, genre_id）的 vocab_size
    """
    model = DeepFM(field_dims,
                   embed_dim=embed_dim,
                   mlp_dims=(128, 64),
                   dropout=0.2)
    return model


def save_model(model: torch.nn.Module) -> None:
    MODEL_PATH.parent.mkdir(exist_ok=True)
    torch.save(model.state_dict(), MODEL_PATH)


def load_model(field_dims: Sequence[int]):
    """
    若模型文件存在则加载并返回 eval() 后模型，否则返回 None。

    当数据库中新增了用户或电影时，只恢复已有的行，新增加的 embedding 行保持随机初始化。
    """
    if MODEL_PATH.exists():
        # 1) 构建一个按最新 field_dims 大小初始化的网络
        m = create_model(field_dims)
        # 2) 只恢复已训练好的权重行，strict=False 保留了新加行的随机初始化
        m.load_state_dict(torch.load(MODEL_PATH, map_location="cpu"), strict=False)
        m.eval()
        return m
    return None
