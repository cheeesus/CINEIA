import React, { useEffect, useState, useRef } from "react";
import Link from "next/link"; // Correct way to import Link from Next.js
import axios from "axios"; // Use axios for API requests


const TopRatedSlider = () => {
  const [TopMovies, setTopMovies] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [page, setPage] = useState(1);  // Track the current page
  const [hasMore, setHasMore] = useState(true);  // Flag to check if there are more movies
  const sliderRef = useRef(null);
  // Function to fetch recent movies with pagination
  const fetchTopMovies = async () => {
    try {
      const response = await axios.get("http://127.0.0.1:5000/api/movies/top", {
        params: {
          page: page,
          limit: 24,  // Limit the number of movies per request
        },
      });
      const newTopMovies = response.data;

      if (newTopMovies.length < 24) {
        setHasMore(false);  // If there are less than 24 movies, it's the last page
      }

      setTopMovies((prevMovies) => [...prevMovies, ...newTopMovies]);
      setLoading(false);
    } catch (err) {
      setError("Failed to load movies");
      setLoading(false);
    }
  };

  // Scroll the slider left
  const scrollLeft = () => {
    if (sliderRef.current) {
      sliderRef.current.scrollBy({ left: -300, behavior: 'smooth' });
    }
  };

  // Scroll the slider right
  const scrollRight = () => {
    if (sliderRef.current) {
      sliderRef.current.scrollBy({ left: 300, behavior: 'smooth' });
    }
  };
  // Function to format the date
  const formatDate = (dateStr) => {
    const date = new Date(dateStr);
    return new Intl.DateTimeFormat('en-GB', {
      day: '2-digit',
      month: 'short',
      year: 'numeric'
    }).format(date);
  };
// Fetch movies when the page number changes
  useEffect(() => {
    fetchTopMovies();
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
      <div className="movie-slider-container">
        <button className="scroll-btn left" onClick={scrollLeft}>←</button>
        
        <div className="movie-slider" ref={sliderRef}>
          {TopMovies.map((movie) => (
            movie.poster_url ? (
              <div key={movie.id} className="movie-item">
                <Link href={`/movies/${movie.id}`}>
                  <img 
                    src={movie.poster_url || "https://via.placeholder.com/400x600?text=No+Image+Available"} 
                    alt={movie.title} 
                    className="movie-poster" 
                  />
                  <h3>{movie.title}</h3>
                  <span>{formatDate(movie.release_date)}</span>
                </Link>
              </div>
            ) : null
          ))}
        </div>

        <button className="scroll-btn right" onClick={scrollRight}>→</button>
      </div>

      {hasMore && (
        <Link href="/movies">
          <button onClick={loadMore} className="load-more-btn">
            Load More
          </button>
        </Link>
      )}
    </>
  );
};

export default TopRatedSlider;
