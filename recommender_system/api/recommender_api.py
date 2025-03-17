from fastapi import FastAPI
import pandas as pd
import os

app = FastAPI()  # Initialize the FastAPI app

BASE_DIR = os.path.join('..')  # Navigate up one level to recommender_system
filepath = os.path.join(BASE_DIR, 'data', 'database_data', 'trending_movies.csv')

def load_trending_movies_from_csv():
    
    try:
        trending_movies = pd.read_csv(filepath,  nrows=100)
        return trending_movies
    except FileNotFoundError:
        print(f"File not found: {filepath}")
        return None
    except Exception as e:
        print(f"Error loading trending movies from {filepath}: {e}")
        return None

@app.get('/api/trending_movies')
def get_trending_movies():
    trending_movies = load_trending_movies_from_csv()
    if trending_movies is not None:
        movies_json = trending_movies.to_dict(orient='records')
        return movies_json
    else:
        return {"error": "Trending movies data not available"}