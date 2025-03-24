
'use client';  // This marks the component as a client component
import { useEffect, useState } from 'react';
import Header from "@/components/Header";

import "../../../styles/MovieDetails.css";
 
const MovieDetails = ({params}) => {
  const [movieId, setMovieId] = useState(null); 
  const [movie, setMovie] = useState(null);
  // Use React.use to unwrap the Promise
  useEffect(() => {
    const getMovieId = async () => {
      const resolvedParams = await params;  // Unwrap the params promise
      setMovieId(resolvedParams.movieId);   // Set the movieId state
    };

    getMovieId();
  }, [params]);
  useEffect(() => {
    const fetchMovie = async () => {
      const response = await fetch(`http://127.0.0.1:5000/movies/${movieId}`);
      if (!response.ok) {
        console.error("Error fetching movie details");
        return;
      }
      const data = await response.json();
      setMovie(data);
    };

    if (movieId) {
      fetchMovie();
    }
  }, [movieId]);

  if (!movie) {
    return <div>Loading movie details...</div>;
  }

  return (
    <div>
      <Header />
      <main>
        <h1>{movie.title}</h1>
        <img src={movie.poster_url || "https://via.placeholder.com/500x750?text=No+Image+Available"} alt={movie.title} />
        <p>{movie.overview}</p>
        <p><strong>Release Date:</strong> {movie.release_date}</p>
        <p><strong>Director:</strong> {movie.director}</p>
        {/* Add other movie details here */}
      </main>
    </div>
  );
};

export default MovieDetails;
