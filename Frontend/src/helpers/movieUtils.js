import axios from "axios";

export const recordMovieView = async (userId, movieId, token) => {
  try {
    await axios.post(
      `http://127.0.0.1:5000/api/movies/${userId}/history`,
      { movie_id: movieId },
      { headers: { Authorization: `Bearer ${token}` } }
    );
    console.log("Movie added to view history.");
  } catch (err) {
    console.error("Failed to add movie to view history:", err);
  }
};