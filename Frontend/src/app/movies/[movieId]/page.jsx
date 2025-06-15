'use client';  // This marks the component as a client component
import { useEffect, useState, useContext } from 'react';
import axios from "axios";
import { FaHeart, FaStar } from "react-icons/fa";
import { FiPlus } from "react-icons/fi";
import Header from "@/components/Header";
import styles from "@/styles/movieDetails.module.css";
import { UserContext } from "@/context/UserContext";

// Load environment variables
const API_URL = process.env.NEXT_PUBLIC_API_URL;

const MovieDetails = ({params}) => {
  const { user, isLoggedIn } = useContext(UserContext);
  const [movieId, setMovieId] = useState(null);
  const [movie, setMovie] = useState(null);
  const [isFavorite, setIsFavorite] = useState(false);
  const [rating, setRating] = useState(0);
  const [comments, setComments] = useState([]);
  const [newComment, setNewComment] = useState("");
  const [showListModal, setShowListModal] = useState(false);
  const [existingLists, setExistingLists] = useState([]); // List of user's lists

  // Unwrap params and set movieId
  useEffect(() => {
    let isMounted = true; // To prevent setting state on unmounted component
    const resolveParams = async () => {
      try {
        const resolvedParams = await params; // Assume params is a promise
        if (isMounted) setMovieId(resolvedParams.movieId);
      } catch (error) {
        console.error("Error resolving params:", error);
      }
    };
    resolveParams();

    return () => {
      isMounted = false;
    };
  }, [params]);

  // Fetch movie details
  useEffect(() => {
  const fetchMovie = async () => {
    try {
      const response = await fetch(`${API_URL}/movies/${movieId}`, {
        headers: user?.token ? { Authorization: `Bearer ${user.token}` } : {},
      });
      if (!response.ok) {
        throw new Error("Failed to fetch movie details");
      }
      const data = await response.json();
      setMovie(data);
    } catch (err) {
      console.error(err);
    }
  };

  if (movieId) {
    fetchMovie();
  }
}, [movieId, user]);

  // Fetch user's lists
  useEffect(() => {
    const fetchLists = async () => {
      if (!user || !user.userId) {
        console.log("User not available yet.");
        return; // Exit if user is not yet set
      }

      try {
        const response = await axios.get(`${API_URL}/users/${user.userId}/lists`, {
          headers: { Authorization: `Bearer ${user?.token}` },
        });
        console.log(response.data);
        setExistingLists(response.data);
      } catch (error) {
        console.error("Failed to fetch lists:", error);
      }
    };

    fetchLists();
  }, [user]); // Runs only once on mount



  // Fetch comments
  useEffect(() => {
    const fetchComments = async () => {
      try {
        const response = await axios.get(`${API_URL}/movies/${movieId}/comments`);
        setComments(response.data);
      } catch (error) {
        console.error("Failed to fetch comments:", error);
      }
    };

    if (movieId) fetchComments();
  }, [movieId]);

  useEffect(() => {
    const fetchFavoriteStatus = async () => {
      if (!user || !user.userId) {
        console.log("User not available yet.");
        return; // Exit if user is not yet set
      }
      try {
        const response = await axios.get(
          `${API_URL}/users/${user.userId}/lists`, // Endpoint to fetch lists
          { headers: { Authorization: `Bearer ${user?.token}` } }
        );
        
        const favoritesList = response.data.find((list) => list.list_name === "favorites");
        console.log(favoritesList);
        
        if (favoritesList) {
          // Fetch movies in the "Favorites" list
          const response = await axios.get(
            `${API_URL}/movies/${favoritesList['list_id']}/movies`,
            { headers: { Authorization: `Bearer ${user?.token}` } }
          );
          const moviesInFavorites = response.data['movie_ids'];
          const isFavorited = moviesInFavorites.some((movie) => String(movie) === movieId);
          setIsFavorite(isFavorited);
        }
      } catch (error) {
        console.error("Failed to fetch favorite status:", error);
      }
    };
    const fetchUserRating = async () => {
      if (!isLoggedIn || !movieId || !user?.userId) return;

      try {
        const response = await axios.get(`${API_URL}/movies/${movieId}/rating`, {
          headers: { Authorization: `Bearer ${user?.token}` },
        });
        if (response.status === 200) {
          setRating(response.data.user_rating || 0); // Set user rating
        }
      } catch (error) {
        console.error("Failed to fetch user rating:", error);
      }
    };

    if (isLoggedIn && movieId) {
      fetchFavoriteStatus();
      fetchUserRating();
    }
  }, [isLoggedIn, movieId, user]);

  const handleFavoriteToggle = async () => {
    if (!isLoggedIn) {
      alert("You need to be logged in to manage favorites.");
      return;
    }

    try {
      if (isFavorite) {
        // Remove from favorites
        await axios.delete(
          `${API_URL}/movies/${movieId}/favorite`,
          {
            headers: { Authorization: `Bearer ${user?.token}` },
          }
        );
        alert("Movie removed from favorites.");
      } else {
        // Add to favorites
        await axios.post(
          `${API_URL}/movies/${movieId}/favorite`,
          {},
          {
            headers: { Authorization: `Bearer ${user?.token}` },
          }
        );
        alert("Movie added to favorites.");
      }

      // Toggle the isFavorite state
      setIsFavorite((prev) => !prev);
    } catch (err) {
      console.error("Failed to update favorites:", err);
      alert("An error occurred while updating favorites.");
    }
  };

  const handleRating = async (newRating) => {
    if (!isLoggedIn) {
      alert("You need to be logged in to rate a movie.");
      return;
    }

    try {
      const response = await axios.post(
        `${API_URL}/movies/${movieId}/rate`,
        { movie_id: movieId, rating: newRating * 2 },
        { headers: { Authorization: `Bearer ${user?.token}` } }
      );

      if (response.status === 200) {
        setRating(newRating * 2);
        const confirmComment = confirm("Would you like to leave a comment about this movie?");
        if (confirmComment) {
          document.getElementById("commentInput").focus();
        }
      } else {
        console.error("Unexpected response:", response);
        alert("Failed to submit rating.");
      }
    } catch (error) {
      console.error("Failed to submit rating:", error);
      alert("An error occurred. Please try again.");
    }
  };

  const handleSubmitComment = async () => {
  if (!isLoggedIn) {
    alert("You need to be logged in to comment.");
    return;
  }

  if (!newComment.trim()) {
    alert("Comment cannot be empty.");
    return;
  }

  try {
    const response = await axios.post(
      `${API_URL}/movies/${movieId}/comments`,
      { 
        comment: newComment, 
        username: user?.username || "" 
      },
      { headers: { Authorization: `Bearer ${user?.token}` } }
    );

    if (response.status === 200) {
      setComments((prev) => [...prev, response.data]);
      setNewComment("");
      alert("Comment added!");
    }
  } catch (error) {
    console.error("Failed to submit comment:", error);
    alert("Failed to submit comment. Please try again.");
  }
};


  // Handle adding to an existing list
  const handleAddToExistingList = async (listId) => {
    try {
        const response = await axios.post(
            `${API_URL}/users/${user.userId}/${listId}/add`,
            { movieId },
            { headers: { Authorization: `Bearer ${user?.token}` } }
        );

        if (response.status === 200) {
            alert("Movie added to list!");
            setShowListModal(false);
        } else {
            console.error("Unexpected response:", response);
            alert("Failed to add movie to list. Please try again later.");
        }
    } catch (error) {
        if (error.response?.status === 409) {
            // Movie already exists
            alert("This movie is already in the list.");
        } else {
            // Other errors
            console.error("Failed to add movie to list:", error);
            alert("Failed to add movie. Please try again.");
        }
    }
  };


  // Handle creating a new list
  const handleAddToList = async (listName) => {
    if (!isLoggedIn) {
      alert("You need to be logged in to add to a list.");
      return;
    }
    if (!listName.trim()) {
      alert("List name cannot be empty.");
      return;
    }

    try {
      const response = await axios.post(`${API_URL}/movies/${movieId}/add-to-list`, 
        { movie_id: movieId, list_name: listName },
        { headers: { Authorization: `Bearer ${user?.token}` } });
      setExistingLists((prev) => [...prev, response.data]); // Add new list to state
      alert("New list created and movie added!");
    } catch (error) {
      console.error("Failed to create new list:", error);
    }
  };

  if (!movie) {
    return (
      <>
        <Header/>
        <div>Loading movie details...</div>
      </>
    );
  }
  
  // Function to format the date
  const formatDate = (dateStr) => {
    const date = new Date(dateStr);
    return new Intl.DateTimeFormat('en-GB', {
      day: '2-digit',
      month: 'short',
      year: 'numeric'
    }).format(date);
  };
  return (
    <div>
      <Header />
      <main className={styles.container}>
        <div style={{ display: 'flex', justifyContent: 'center', marginBottom: '1rem' }}>
          <img
            width={1000}
            height={562}
            className={styles.moviePoster}
            src={movie.backdrop_url || "https://via.placeholder.com/500x750?text=No+Image+Available"}
            alt={movie.title}
          />
        </div>
        <div className={styles.details}>
          <h1>{movie.title}</h1>
          <div style={{ display: 'flex', flexDirection: 'row' , justifyContent: 'space-between'}}>
            <div>
              <p><strong>Release Date:</strong> {formatDate(movie.release_date)}</p>
              <p><strong>Director:</strong> {movie.director}</p>
              <p><strong>Duration:</strong> {movie.runtime} minutes</p>
              <p><strong>Genres:</strong> {movie.genres.join(', ')}</p>  
            </div>
            <div className={styles.movieActions}>
              <span>{movie.vote_average > 0 ? <> {movie.vote_average} ({movie.vote_count})</>: ""}</span>
              {/* 5-Star Rating */}
              <div className={styles.rating}>
                {[1, 2, 3, 4, 5].map((star) => (
                  <FaStar
                    key={star}
                    size={24}
                    color={star <= rating/2 ? "#FFD700" : "#E0E0E0"}
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
              </button>
            </div>
          </div>

          {/* List Modal */}
          {showListModal && (
            <div className={styles.listModal}>
              <div className={styles.modalContent}>
                <h3>Add to List</h3>

                {/* Display existing lists */}
                <div className={styles.existingLists}>
                  {existingLists.length > 0 ? (
                    <ul>
                      {existingLists.map((list) => (
                        <li key={list.list_id}>
                          <button onClick={() => handleAddToExistingList(list.list_id)}>
                            {list.list_name}
                          </button>
                        </li>
                      ))}
                    </ul>
                  ) : (
                    <p>No lists available. Create a new one!</p>
                  )}
                </div>

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
                <button className={styles.closeBtn} onClick={() => setShowListModal(false)}>Cancel</button>
              </div>
            </div>
          )}
          <p className={styles.overview}>{movie.overview}</p>
          <hr></hr>
          <h3>Cast</h3>
          {movie.actors.length > 0 ? (
            <div className={styles.castContainer}>
              {movie.actors.map((actor, index) => (
                <div key={index} className={styles.actorCard}>
                  <img
                    className={styles.actorProfile}
                    src={actor.profile_url || "/user.jpg"}
                    alt={actor.actor_name}
                  />
                  <h4>{actor.actor_name}</h4>
                  <p>as {actor.character}</p>
                </div>
              ))}
            </div>
          ) : (
            <p>No cast available for this movie...</p>
          )}
          <hr></hr>
          {/* Comment Section */}
          <div className={styles.commentSection}>
            <h3>Comments</h3>
            {comments.length > 0 ? (
              <ul>
                {comments.map((comment, index) => (
                  <li key={index} className={styles.comment}>
                    <strong>{comment.username}</strong>: {comment.comment}
                  </li>
                ))}
              </ul>
            ) : (
              <>
                <p>No comments yet. Be the first to comment!</p>
                <br></br>
              </>
            )}
            <div className={styles.commentForm}>
              <textarea
                id="commentInput"
                value={newComment}
                onChange={(e) => setNewComment(e.target.value)}
                placeholder="Write your comment here..."
              />
              <button onClick={handleSubmitComment}>Submit Comment</button>
            </div>
          </div>
        </div>
      </main>
    </div>
  );

};

export default MovieDetails;
