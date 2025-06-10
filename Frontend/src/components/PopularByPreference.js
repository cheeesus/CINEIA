'use client';
import React, { useState, useEffect, useContext, useRef } from 'react';
import axios from 'axios';
import Link from "next/link"; 
import { UserContext } from '@/context/UserContext';
import styles from '@/styles/PopularMovies.module.css';

const PopularMoviesByPreference = () => {
  const { user, isLoggedIn } = useContext(UserContext);
  const [popularMovies, setPopularMovies] = useState({});
  const [loading, setLoading] = useState(true);
  const sliderRef = useRef(null);

  useEffect(() => {
    if (!isLoggedIn || !user) return;

    const fetchPopularMovies = async () => {
      try {
        const response = await axios.get(`http://127.0.0.1:5000/api/users/${user.userId}/popular-by-preference`, {
          headers: { Authorization: `Bearer ${user.token}` },
        });
        setPopularMovies(response.data.popular_movies);
      } catch (error) {
        console.error('Error fetching popular movies:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchPopularMovies();
  }, [isLoggedIn, user]);

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

  if (loading) {
    return <p>Loading popular movies...</p>;
  }

  if (Object.keys(popularMovies).length === 0) {
    return <p>No popular movies found for your preferences.</p>;
  }

  return (
    <div className={styles.container}>
      {Object.entries(popularMovies).map(([genre, movies]) => (
        <div key={genre} className={styles.movieSliderContainer}>
          <h2>{genre}</h2>
          <button className={styles.scrollBtnLeft} onClick={scrollLeft}>←</button>
          <div className={styles.movieSlider} ref={sliderRef}>
            {movies.map((movie) => (
              <div key={movie.movie_id} className={styles.movieItem} onClick={() => handleMovieClick(movie.movie_id)}>
                <Link href={`/movies/${movie.movie_id}`}>
                    <img src={movie.poster_url || "https://via.placeholder.com/400x600?text=No+Image+Available"} alt={movie.title} className={styles.moviePoster} />
                    <h3>{movie.title}</h3>
                    <p>Release Date: {new Date(movie.release_date).toLocaleDateString()}</p>
                </Link>
              </div>
            ))}
          </div>
          <button className={styles.scrollBtnRight} onClick={scrollRight}>→</button>
        </div>
      ))}
    </div>
  );
};

export default PopularMoviesByPreference;
