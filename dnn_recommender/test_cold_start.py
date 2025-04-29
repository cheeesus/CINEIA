# test_cold_start.py

import random
from models.db import fetchone_dict, get_user_view_count, get_movie_titles,execute_sql
from models.cold_start import recommend_cold_start


def ensure_new_user(user_id):
    """
    如果数据库里没有 user_id = X，就插入一条记录表示新用户。
    根据你的 users 表字段自行调整插入语句。
    """
    row = fetchone_dict("SELECT id FROM users WHERE id=%s", (user_id,))
    if row:
        print(f"User {user_id} already exists. Proceeding.")
    else:
        sql = "INSERT INTO users (id, email, password_hash) VALUES (%s, %s, %s)"
        execute_sql(sql, (user_id, f"test_{user_id}@test.com", "hash_placeholder"))
        print(f"Inserted new user with id={user_id}")

def simulate_user_view(user_id, movie_ids):
    """
    模拟用户观看行为，往 view_history 表里插记录。
    """
    for mid in movie_ids:
        sql = "INSERT INTO view_history (user_id, movie_id) VALUES (%s, %s)"
        execute_sql(sql, (user_id, mid))
    print(f"User {user_id} viewed {len(movie_ids)} movie(s).")

if __name__ == "__main__":
    # 1) 假设指定测试 user_id=101 表示新用户
    TEST_USER_ID = 101
    ensure_new_user(TEST_USER_ID)
    
    count = get_user_view_count(TEST_USER_ID)
    print(f"User {TEST_USER_ID} has watch record: {count}")
    if count > 0:
        print("This user is not empty. For a truly new user, please use a fresh ID.")
    
    # 2) 冷启动推荐
    rec_movies = recommend_cold_start(top_n=5)
    if not rec_movies:
        print("No recommended movies found. Please check your database data.")
    else:
        title_map = get_movie_titles(rec_movies)
        print(f"[Cold Start] Top 5 movies for user {TEST_USER_ID}:")
        for mid in rec_movies:
            print(f"  MovieID={mid}, Title={title_map.get(mid, 'Unknown')}")
        
        # 3) 模拟用户看了其中一半
        watched_subset = random.sample(rec_movies, max(1, len(rec_movies)//2))
        simulate_user_view(TEST_USER_ID, watched_subset)

    print("Cold start test completed. Next step: run incremental training & warm start.")
