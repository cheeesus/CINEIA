# test_warm_start.py

import sys
from models.db import get_user_view_count, get_movie_titles
from models.train_incremental import incremental_train
from models.warm_start import load_model, recommend_warm_start

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_warm_start.py <user_id> [top_n]")
        sys.exit(1)

    user_id = int(sys.argv[1])
    top_n = 5
    if len(sys.argv) >= 3:
        top_n = int(sys.argv[2])

    # 1) 检查用户观影记录
    count = get_user_view_count(user_id)
    print(f"User {user_id} has {count} watch records.")
    
    if count == 0:
        print("This user has no watch history. Please run test_cold_start.py first!")
        sys.exit(0)

    # 2) 做一次增量训练，让模型纳入该用户的行为数据
    print("\n[Incremental Training] Start ...")
    incremental_train(neg_ratio=1, epochs=3)  # 只训练3个 epoch 作为演示
    print("[Incremental Training] Done.\n")

    # 3) 加载模型并做“热启动”推荐
    model = load_model()
    rec_ids, scores = recommend_warm_start(model, user_id, top_n=top_n)
    if not rec_ids:
        print("No personalized recommendation found. Possibly no candidate movies or data issues.")
        sys.exit(0)

    # 4) 输出推荐结果
    title_map = get_movie_titles(rec_ids)
    print(f"\n[Warm Start] Top {top_n} movies for user {user_id}:")
    for mid, sc in zip(rec_ids, scores):
        title = title_map.get(mid, "Unknown Title")
        print(f"  MovieID={mid}, Title={title}, Score={sc:.4f}")
    
    print("\nWarm start test completed.")
