#!/usr/bin/env python3
"""
scripts/interactive_demo.py
CLI 交互式推荐演示

流程：
  1. 输入一个用户 ID（若不存在自动插入）
  2. 调用 service.recommender 推荐 TOP_N 部电影
  3. 用户手动选择若干部想看的 → 写入 view_history
  4. 每 LOOP_FOR_RETRAIN 轮：
        • 召回侧增量训练 1 epoch
        • 精排侧增量训练 1 epoch
  5. 回到步骤 2，直到输入 q / quit 退出
"""

from typing import List

# ------- readline 在 Linux / macOS 默认有；Windows 没有也不影响 -------
try:
    import readline  # noqa: F401
except ImportError:
    pass

from models.db import (
    fetchone_dict, execute_sql,
    get_movie_titles, get_user_view_count,
)
from models.recall.train_incremental import incremental_train as recall_inc_train
from models.ranking.train_ranking import main as ranking_train_main
from service.recommender import recommend_movies_for_user

TOP_N = 10
LOOP_FOR_RETRAIN = 3      # 每 3 轮做一次增量重训（可调为 0 关闭）


# ------------------------------------------------------------------ #
#                 DB 帮助函数：建用户 / 插观看记录                    #
# ------------------------------------------------------------------ #
def ensure_user(user_id: int):
    if not fetchone_dict("SELECT 1 FROM users WHERE id=%s", (user_id,)):
        execute_sql(
            "INSERT INTO users (id, email, password_hash) VALUES (%s, %s, %s)",
            (user_id, f"cli_{user_id}@demo.com", b"hash_placeholder"),
        )
        print(f"✅ 已创建新用户 {user_id}")


def insert_views(user_id: int, movie_ids: List[int]):
    for mid in movie_ids:
        execute_sql(
            "INSERT INTO view_history (user_id, movie_id) VALUES (%s, %s)",
            (user_id, mid),
        )


# ------------------------------------------------------------------ #
#                             交互函数                               #
# ------------------------------------------------------------------ #
def choose_movies(candidates: List[int], titles: dict[int, str]) -> List[int] | None:
    print("\n请输入想看的电影序号（空格分隔），或 q 退出：")
    for i, m in enumerate(candidates, 1):
        print(f"[{i:02}] {titles.get(m, 'Unknown')}")

    while True:
        raw = input("你的选择: ").strip().lower()
        if raw in {"q", "quit"}:
            return None
        try:
            idxs = [int(s) for s in raw.split()]
            chosen = [candidates[i - 1] for i in idxs if 1 <= i <= len(candidates)]
            return chosen
        except ValueError:
            print("❌ 输入格式错误，请重新输入")


# ------------------------------------------------------------------ #
#                         增量训练封装                                #
# ------------------------------------------------------------------ #
def incremental_retrain():
    print("\n📈 增量训练开始（召回 1 epoch + 精排 1 epoch）...")
    recall_inc_train(neg_ratio=1, epochs=1)
    ranking_train_main(epochs=1, batch_size=4096, neg_ratio=1)
    print("📈 增量训练完成\n")


# ------------------------------------------------------------------ #
#                           主循环                                   #
# ------------------------------------------------------------------ #
def interactive_loop(user_id: int):
    ensure_user(user_id)
    loop_cnt = 0

    while True:
        viewed = get_user_view_count(user_id)
        print(f"\n=== 用户 {user_id} 已观看 {viewed} 部电影 ===")

        rec_ids = recommend_movies_for_user(user_id, n_final=TOP_N)
        if not rec_ids:
            print("⚠️  未能获得推荐，请检查数据。")
            break

        title_map = get_movie_titles(rec_ids)
        chosen = choose_movies(rec_ids, title_map)
        if chosen is None:
            print("\n👋 Bye~")
            break

        insert_views(user_id, chosen)
        print(f"✅ 已记录观看 {len(chosen)} 部影片。")
        loop_cnt += 1

        # ---- 条件触发增量训练 ----
        if LOOP_FOR_RETRAIN and loop_cnt % LOOP_FOR_RETRAIN == 0:
            incremental_retrain()


# ------------------------------------------------------------------ #
#                                 main                               #
# ------------------------------------------------------------------ #
if __name__ == "__main__":
    try:
        uid = int(input("请输入用户 ID（新的随便填一个整数）： ").strip())
    except ValueError:
        print("❌ 用户 ID 必须是整数")
        exit(1)

    interactive_loop(uid)
