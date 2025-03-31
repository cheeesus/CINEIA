from ..database import fetch_top_movies_by_vote_average

def cold_start_recommend(top_n=5):
    """
    Cold Start: Recommend top {top_n} movies by global popularity or highest vote average when no user information is available.
    """
    print(f"Cold Start scenario:Recommend the top {top_n} movies by vote average:\n")
    top_movies = fetch_top_movies_by_vote_average(top_n)
    if not top_movies:
        print("⚠️ No movies or vote_average data in the database!")
        return

    for (movie_id, title, vote_avg, vote_count) in top_movies:
        print(f"Film ID={movie_id}, Title={title}, Vote Average={vote_avg}, Vote Count={vote_count}")

if __name__ == "__main__":
    cold_start_recommend(5)
