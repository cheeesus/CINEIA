import sys
from db import get_user_view_count, get_movie_titles
from cold_start import recommend_cold_start
from warm_start import load_model, recommend_warm_start

def recommend_movies_for_user(user_id, top_n=10):
    """
    根据用户是否有历史观看记录，决定走冷启动还是热启动。
    """
    view_count = get_user_view_count(user_id)
    if view_count == 0:
        # 冷启动
        print(f"User {user_id} is new, using Cold Start strategy.")
        rec_ids = recommend_cold_start(top_n=top_n)
        scores = [None] * len(rec_ids)  # 冷启动推荐不经过模型，可不提供分数
    else:
        # 热启动
        print(f"User {user_id} has {view_count} watched records, using Warm Start (DNN).")
        model = load_model()
        rec_ids, scores = recommend_warm_start(model, user_id, top_n=top_n)
    return rec_ids, scores

if __name__ == "__main__":
    # 用法示例： python service.py  <user_id> [top_n]
    if len(sys.argv) < 2:
        print("Usage: python service.py <user_id> [top_n]")
        sys.exit(1)

    user_id = int(sys.argv[1])
    top_n = 10
    if len(sys.argv) >= 3:
        top_n = int(sys.argv[2])

    rec_ids, scores = recommend_movies_for_user(user_id, top_n=top_n)
    if not rec_ids:
        print("No recommendations found.")
        sys.exit(0)

    # 获取电影标题并打印
    title_map = get_movie_titles(rec_ids)
    print(f"Top {top_n} Recommendations for user {user_id}:")
    for mid, sc in zip(rec_ids, scores):
        title = title_map.get(mid, "Unknown Title")
        if sc is not None:
            print(f"  Movie ID: {mid}, Title: {title}, Score: {sc:.4f}")
        else:
            print(f"  Movie ID: {mid}, Title: {title}, (No Score - Cold Start)")
