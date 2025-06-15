import React, { useEffect, useState, useRef } from "react";
import styles from "@/styles/movieSlider.module.css"
import Link from "next/link"; 
import axios from "axios"; 

// Load environment variables
const API_URL = process.env.NEXT_PUBLIC_API_URL;

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
      const response = await axios.get(`${API_URL}/movies/top`, {
        params: {
          page: page,
          limit: 24,  // Limit the number of movies per request
        },
      });
      const newTopMovies = response.data;

      if (newTopMovies.length < 24) {
        setHasMore(false);  // If there are less than 24 movies, it's the last page
      }

      setTopMovies(newTopMovies);
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
  const handleMovieClick = async (movieId) => {
    if (!isLoggedIn || !user?.userId || !user?.token) {
      console.log("User not logged in. Skipping view history recording.");
      return;
    }

    try {
      await axios.post(
        `${API_URL}/movies/${user.userId}/history`,
        { movie_id: movieId },
        { headers: { Authorization: `Bearer ${user.token}` } }
      );
      console.log("Movie added to view history.");
    } catch (err) {
      console.error("Failed to add movie to view history:", err);
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
      <div className={styles.movieSliderContainer}>
        <button className={styles.scrollBtnLeft} onClick={scrollLeft}>&#60;</button>
        
        <div className={styles.movieSlider} ref={sliderRef}>
          {TopMovies.map((movie) => (
            (movie.poster_url && movie.rating > 0 && movie.rating < 10) ? (
              <div key={movie.id} className={styles.movieItem} onClick={() => handleMovieClick(movie.id)}>
                <Link href={`/movies/${movie.id}`}>
                  <img 
                    src={movie.poster_url || "https://via.placeholder.com/400x600?text=No+Image+Available"} 
                    alt={movie.title} 
                    className={styles.moviePoster} 
                  />
                  <div className={styles.info}>
                    <div>
                      <h3>{movie.title}</h3>
                      <span>{formatDate(movie.release_date)}</span>
                    </div>
                    <span>{movie.rating}</span>
                  </div>
                  
                </Link>
              </div>
            ) : null
          ))}
        </div>
        <button className={styles.scrollBtnRight} onClick={scrollRight}>&#62;</button>
      </div>

      {hasMore && (
        <button  onClick={loadMore} className={styles.loadMoreBtn}>
          Load More
        </button>
      )}
    </>
  );
};

export default TopRatedSlider;
