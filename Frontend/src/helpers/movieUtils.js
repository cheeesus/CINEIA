import axios from "axios";

// Load environment variables
const API_URL = process.env.NEXT_PUBLIC_API_URL;

export const recordMovieView = async (userId, movieId, token) => {
  try {
    await axios.post(
      `${API_URL}/movies/${userId}/history`,
      { movie_id: movieId },
      { headers: { Authorization: `Bearer ${token}` } }
    );
    console.log("Movie added to view history.");
  } catch (err) {
    console.error("Failed to add movie to view history:", err);
  }
};