import React, { useEffect, useState } from "react";
import Link from "next/link"; // Correct way to import Link from Next.js
import axios from "axios"; // Use axios for API requests


const RecentMoviesList = () => {
  const [recentMovies, setRecentMovies] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [page, setPage] = useState(1);  // Track the current page
  const [hasMore, setHasMore] = useState(true);  // Flag to check if there are more movies

  // Function to fetch recent movies with pagination
  const fetchRecentMovies = async () => {
    try {
      const response = await axios.get("http://127.0.0.1:5000/api/movies/recent", {
        params: {
          page: page,
          limit: 24,  // Limit the number of movies per request
        },
      });
      const newRecentMovies = response.data;

      if (newRecentMovies.length < 24) {
        setHasMore(false);  // If there are less than 24 movies, it's the last page
      }

      setRecentMovies((prevMovies) => [...prevMovies, ...newRecentMovies]);
      setLoading(false);
    } catch (err) {
      setError("Failed to load movies");
      setLoading(false);
    }
  };

  // Fetch movies when the page number changes
  useEffect(() => {
    fetchRecentMovies();
  }, [page]);

  // Load more movies when the button is clicked
  const loadMore = () => {
    if (hasMore) {
      setPage(page + 1);  // Load the next page
    }
  };

  // Display loading message or error message
  if (loading) {
    return <div>Loading movies...</div>;
  }

  if (error) {
    return <div>{error}</div>;
  }

  return (
    <>
      <div className="movie-list">
        {recentMovies.map((movie) => (
          movie.poster_url ? ( // Check if poster_url is valid
            <div key={movie.id} className="movie-item">
              <Link href={`/movies/${movie.id}`}>
                <img 
                  src={movie.poster_url || "https://via.placeholder.com/500x750?text=No+Image+Available"} 
                  alt={movie.title} 
                  className="movie-poster" 
                />
                <h3>{movie.title}</h3>
              </Link>
            </div>
          ) : null // Skip rendering if poster_url is null or falsy
        ))}
      </div>
  
      {hasMore && (
        <button onClick={loadMore} className="load-more-btn">
          Load More
        </button>
      )}
    </>
  );
  
};

export default RecentMoviesList;
