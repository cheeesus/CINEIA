psql -h postgresql-yannr.alwaysdata.net -p 5432 -U yannr_01 -d yannr_00
Project1234



查看所有表的字段、数据类型、是否可空、默认值


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


启动方式
# 1. install the requirment packages 
pip install --upgrade -r requirements.txt

# 2. 确保 pytorch_model.py 已复制到 models/ 目录 cd the root branch

# 3. 训练召回模型（快）
# 3. retrain the call back model 
python -m models.recall.train_two_tower --epochs 3 --batch 128

# 4. 训练精排模型（深度特征少，也很快）
# 4. retraion the re-rank model
python -m models.ranking.train_ranking --epochs 3

# 5. run the demo scripts
python -m scripts.interactive_demo

// python -m service/recommender.py 1001 --top 10
