# CINEIA – AI

1 · Prepare .env
Create FlaskAPI/.env with your database credentials:
```bash
DB_HOST=postgresql-yannr.alwaysdata.net
DB_NAME=yannr_00
DB_USER=yannr_01
DB_PASSWORD=Projet1234
SECRET_KEY=dev-key
```

(The key can be any value - it is only used by Flask.)

2 · Install Python dependencies
Activate your virtual-env, then install the two requirement files:
```bash
pip install -r DNN_TorchFM_TTower/requirements.txt
pip install -r FlaskAPI/requirements.txt
```
3 · Train (or re-train) the AI models
Run from the project root CINEIA/.
Note the fully-qualified module paths (DNN_TorchFM_TTower. prefix).

3-A Train / retrain the Two-Tower recall model
```bash
python -m DNN_TorchFM_TTower.models.recall.train_two_tower --epochs 3 --batch 128
```
3-B Train / retrain the DeepFM re-rank model
```bash
python -m DNN_TorchFM_TTower.models.ranking.train_ranking --epochs 3
```
(You may shorten epochs while testing; saved weights go to DNN_TorchFM_TTower/saved_model/.)

4 · Run the Flask API
```bash
python FlaskAPI/app.py # default http://127.0.0.1:5000
```
Visiting / shows 404 – that is expected; the API lives under /api.

5 · Call the Recommendation endpoint
Pattern:
```bash
GET /api/recommend/<user_id>?top=<N>
```
Example:
```bash
http://localhost:5000/api/recommend/51
```