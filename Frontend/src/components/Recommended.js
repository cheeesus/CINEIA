import React, { useEffect, useState, useRef, useContext } from "react";
import { UserContext } from '@/context/UserContext';
import styles from "@/styles/movieSlider.module.css"
import Link from "next/link"; 
import axios from "axios"; 


const RecommendedSlider = () => {
  const { user, isLoggedIn } = useContext(UserContext);
  const [recommendedMovies, setRecommendedMovies] = useState([]);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [hasMore, setHasMore] = useState(true);
  const sliderRef = useRef(null);

  const fetchRecommendedMovies = async () => {
    if (!isLoggedIn) return;

    try {
      setLoading(true);
      const response = await axios.get(`http://127.0.0.1:5000/api/movies/${user.userId}/recommend`, {
        params: {
          page: page,
          limit: 24,
        },
      });
      console.log("API Response Data:", response.data.items);
      const newRecommendedMovies = response.data.items;
      if (newRecommendedMovies.length < 24) {
        setHasMore(false); // If there are fewer than 24 movies, it's the last page
      }

      setRecommendedMovies((prevMovies) => [...prevMovies, ...newRecommendedMovies]);
    } catch (err) {
      setError("Failed to load movies");
    } finally {
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
      fetchRecommendedMovies();
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
          `http://127.0.0.1:5000/api/movies/${user.userId}/history`,
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
          <button className={styles.scrollBtnLeft} onClick={scrollLeft}>←</button>
          
          <div className={styles.movieSlider} ref={sliderRef}>
            {recommendedMovies.map((movie) => (
              movie.poster_url ? (
                <div key={movie.id} className={styles.movieItem} onClick={() => handleMovieClick(movie.id)}>
                  <Link href={`/movies/${movie.id}`}>
                    <img 
                      src={movie.poster_url || "https://via.placeholder.com/400x600?text=No+Image+Available"} 
                      alt={movie.title} 
                      className={styles.moviePoster} 
                    />
                    <h3>{movie.title}</h3>
                    <span>{formatDate(movie.release_date)}</span>
                  </Link>
                </div>
              ) : null
            ))}
          </div>

          <button className={styles.scrollBtnRight} onClick={scrollRight}>→</button>
        </div>

        {hasMore && (
          <Link href="/movies">
            <button onClick={loadMore} className={styles.loadMoreBtn}>
              Load More
            </button>
          </Link>
        )}
      </>
    );
};
export default RecommendedSlider;
