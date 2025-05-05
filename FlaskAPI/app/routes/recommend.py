# FlaskAPI/app/routes/recommend.py

# brige AI engine (DNN_TorchFM_TTower) recommendation interface

import sys, pathlib
from flask import Blueprint, jsonify, request

ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.append(str(ROOT))


from DNN_TorchFM_TTower.service.recommender import recommend_movies_for_user
from DNN_TorchFM_TTower.models.db import get_movie_titles

bp = Blueprint("recommend", __name__)

@bp.get("/recommend/<int:user_id>")
def recommend(user_id: int):
    top = int(request.args.get("top", 10))

    mids, scores, strategy = recommend_movies_for_user(user_id, n_final=top)
    mids_py = [int(x) for x in mids]
    titles  = get_movie_titles(mids_py)

    return jsonify({
        "user_id": user_id,
        "strategy": strategy,          # cold | warm+rank
        "items": [
            {
                "rank": i + 1,
                "movie_id": mid,
                "title": titles.get(mid, "Unknown"),
                "score": float(scores[i]) if scores[i] is not None else None
            }
            for i, mid in enumerate(mids_py)
        ]
    })
