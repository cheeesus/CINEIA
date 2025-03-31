SELECT
    table_name AS 表名,
    column_name AS 字段名,
    data_type AS 数据类型,
    is_nullable AS 是否可空,
    column_default AS 默认值
FROM
    information_schema.columns
WHERE
    table_schema = 'public'
ORDER BY
    table_name, ordinal_position;



SELECT
    con.conname AS 外键名,
    conrel.relname AS 从表,
    att2.attname AS 外键字段,
    confrel.relname AS 主表,
    att.attname AS 主键字段
FROM
    pg_constraint con
JOIN
    pg_class conrel ON conrel.oid = con.conrelid
JOIN
    pg_class confrel ON confrel.oid = con.confrelid
JOIN
    pg_attribute att ON att.attrelid = con.confrelid AND att.attnum = con.confkey[1]
JOIN
    pg_attribute att2 ON att2.attrelid = con.conrelid AND att2.attnum = con.conkey[1]
WHERE
    con.contype = 'f';  -- 只选外键约束


- 做 **协同过滤推荐**（基于 `view_history`）
- 做 **内容推荐**（基于 `movies` + `movie_genre` + `movie_keyword`）

目前你的推荐模型依赖于“用户对电影的评分”，但 `view_history` 中只有 “是否看过” 的行为。这会限制模型的预测质量。`view_history` 中增加一个 `rating` 字段

modification: 

在 `view_history` 表中增加了用户评分字段 `rating`

ALTER TABLE view_history
ADD COLUMN rating INTEGER DEFAULT 1;

ALTER TABLE view_history
ADD CONSTRAINT chk_rating_range CHECK (rating >= 0 AND rating <= 5);

修改 `view_date` 字段为只保留“天”的精度

ALTER TABLE view_history
ALTER COLUMN view_date TYPE DATE USING view_date::date,
ALTER COLUMN view_date SET DEFAULT CURRENT_DATE;

在 `user_preferences` 中添加 `weight` 字段，计算用户对某类型/关键词的偏好权重，但是目前还没用上 :)

关于推荐系统，协同过滤，Python + scikit-surprise

coldstart_scenario.py 冷启动推荐，新用户尚未登录、首次访问，没有任何历史偏好
**推荐策略**：返回全库评分最高的电影（按 `vote_average`, `vote_count` 排序）

用户偏好推荐（`user_preference_scenario.py`）
**适用情景**：用户手动选了一些喜欢的电影
**推荐策略**：将这些记录插入 `view_history`，然后重新训练模型，为该用户预测可能喜欢的其他电影

recommendation_ai/
├── recommendation_ai/
│   ├── **init**.py
│   ├── [config.py](http://config.py/)
│   ├── [database.py](http://database.py/)               ← all operation database
│   ├── recommendation_model.py   ← rec models
│   ├── [main.py](http://main.py/)                   ← single training and the main process
│   ├── fake_data.py              ← insert test data
│   └── scenarios/
│       ├── coldstart_scenario.py         ← cold run
│       └── user_preference_scenario.py   ← preferrence recommandation
├── tests/
│   ├── **init**.py
│   ├── test_all.py
│   ├── test_database.py
│   └── test_model.py
└── requirements.txt