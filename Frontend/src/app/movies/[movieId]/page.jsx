
'use client';  // This marks the component as a client component
import { useEffect, useState, useContext } from 'react';
import axios from "axios";
import { FaHeart, FaStar } from "react-icons/fa";
import { FiPlus } from "react-icons/fi";
import Header from "@/components/Header";
import styles from "@/styles/movieDetails.module.css";
import { UserContext } from "@/context/UserContext";

const MovieDetails = ({params}) => {
  const { user, isLoggedIn } = useContext(UserContext);
  const [movieId, setMovieId] = useState(null);
  const [movie, setMovie] = useState(null);
  const [isFavorite, setIsFavorite] = useState(false);
  const [rating, setRating] = useState(0);
  const [showListModal, setShowListModal] = useState(false);

  // Unwrap params and set movieId
  useEffect(() => {
    const getMovieId = async () => {
      const resolvedParams = await params;
      setMovieId(resolvedParams.movieId);
    };
    getMovieId();
  }, [params]);

  // Fetch movie details
  useEffect(() => {
    const fetchMovie = async () => {
      try {
        const response = await fetch(`http://127.0.0.1:5000/api/movies/${movieId}`);
        if (!response.ok) {
          throw new Error("Failed to fetch movie details");
        }
        const data = await response.json();
        setMovie(data);
        setRating(data.user_rating || 0);
      } catch (err) {
        console.error(err);
      }
    };

    if (movieId) {
      fetchMovie();
    }
  }, [movieId]);

  const handleFavoriteToggle = async () => {
    if (!isLoggedIn) {
      alert("You need to be logged in to manage favorites.");
      return;
    }

    try {
      if (isFavorite) {
        // If the movie is already a favorite, send a DELETE request to remove it
        await axios.delete(
          `http://127.0.0.1:5000/api/movies/${movieId}/favorite`, // Use DELETE for removal
          {
            headers: { Authorization: `Bearer ${user?.token}` }, // Use token from context
          }
        );
        alert("Movie removed from favorites.");
      } else {
        // If the movie is not a favorite, send a POST request to add it
        await axios.post(
          `http://127.0.0.1:5000/api/movies/${movieId}/favorite`, // Use POST for addition
          {}, // No additional body is required for adding to favorites
          {
            headers: { Authorization: `Bearer ${user?.token}` }, // Use token from context
          }
        );
        alert("Movie added to favorites.");
      }

      // Toggle the isFavorite state
      setIsFavorite((prev) => !prev);
    } catch (err) {
      alert("Failed to update favorites.");
    }
  };

  const handleRating = async (newRating) => {
    if (!isLoggedIn) {
      alert("You need to be logged in to rate a movie.");
      return;
    }

    try {
      await axios.post(
        `http://127.0.0.1:5000/api/movies/${movieId}/rate`,
        { movie_id: movieId, rating: newRating },
        { headers: { Authorization: `Bearer ${user?.token}` } } 
      );
      setRating(newRating);
    } catch (err) {
      alert("Failed to submit rating.");
    }
  };

  const handleAddToList = async (listName) => {
    if (!isLoggedIn) {
      alert("You need to be logged in to add to a list.");
      return;
    }

    try {
      await axios.post(
        `http://127.0.0.1:5000/api/movies/${movieId}/add-to-list`,
        { movie_id: movieId, list_name: listName },
        { headers: { Authorization: `Bearer ${user?.token}` } } 
      );
      alert(`Movie added to the list: ${listName}`);
    } catch (err) {
      alert("Failed to add the movie to the list.");
    }
  };

  if (!movie) {
    return <div>Loading movie details...</div>;
  }

  return (
    <div>
      <Header />
      <main className={styles.container}>
          <img className={styles.moviePoster} src={movie.poster_url || "https://via.placeholder.com/500x750?text=No+Image+Available"} alt={movie.title} />
          <div className={styles.details}>
            <h1>{movie.title}</h1>
            <div className={styles.movieActions}>
              {/* 5-Star Rating */}
              <div className={styles.rating}>
                {[1, 2, 3, 4, 5].map((star) => (
                  <FaStar
                    key={star}
                    size={24}
                    color={star <= rating ? "#FFD700" : "#E0E0E0"}
                    onClick={() => handleRating(star)}
                    style={{ cursor: isLoggedIn ? "pointer" : "not-allowed" }}
                  />
                ))}
              </div>
              {/* Favorite Button */}
              <button onClick={handleFavoriteToggle} className={styles.favoriteBtn}>
                <FaHeart size={24} color={isFavorite ? "red" : "gray"} />
              </button>

              {/* Add to List Button */}
              <button onClick={() => setShowListModal(true)} className={styles.addToListBtn}>
                <FiPlus size={24} />
                Add to List
              </button>
            </div>
            {/* List Modal */}
            {showListModal && (
              <div className={styles.listModal}>
                <div className={styles.modalContent}>
                  <h3>Add to List</h3>
                  <input
                    type="text"
                    placeholder="Enter new list name"
                    onKeyDown={(e) => {
                      if (e.key === "Enter") {
                        handleAddToList(e.target.value);
                        setShowListModal(false);
                      }
                    }}
                  />
                  <button onClick={() => setShowListModal(false)}>Cancel</button>
                </div>
              </div>
            )}
            <p><strong>Release Date:</strong> {movie.release_date}</p>
            <p><strong>Director:</strong> {movie.director}</p>
            <p className={styles.overview}>{movie.overview}</p>
          </div>
      </main>
    </div>
  );
};

export default MovieDetails;
