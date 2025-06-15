'use client'
import React, { useEffect, useState, useContext } from "react";
import { UserContext } from "@/context/UserContext";
import styles from "@/styles/searchResults.module.css"
import Header from "@/components/Header";
import Link from "next/link"; 
import axios from "axios"; 

// Load environment variables
const API_URL = process.env.API_URL;

const SearchPage = ({ params }) => {
  const [searchQuery, setSearchQuery] = useState("");
  const [searchResults, setSearchResults] = useState([]);
  const { user, isLoggedIn } = useContext(UserContext);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

  // Unwrap params and set searchQuery
  useEffect(() => {
    let isMounted = true; // To prevent setting state on unmounted component
    const resolveParams = async () => {
      try {
        const resolvedParams = await params; // Assume params is a promise
        if (isMounted) setSearchQuery(resolvedParams.searchQuery);
      } catch (error) {
        console.error("Error resolving params:", error);
      }
    };
    resolveParams();

    return () => {
      isMounted = false;
    };
  }, [params]);


  // Function to fetch search query results
  useEffect(() => {
    const fetchSearchResults = async () => {
      if (!searchQuery.trim()) {
        setSearchResults([]);
        return;
      }

      try {
        const response = await axios.get(`${API_URL}/movies/search`, {
          params: { query: searchQuery },
        });

        setSearchResults(response.data.movies);
        console.log(response.data.movies);
        setLoading(false);
      } catch (error) {
        setLoading(false);
        setError("Failed to load movies");
        console.error("Search error:", error);
      }
    };

    const delayDebounce = setTimeout(() => {
      fetchSearchResults();
    }, 300); // Debounce API calls (wait 300ms)

    return () => clearTimeout(delayDebounce);
  }, [searchQuery]);

  // Function to format the date
  const formatDate = (dateStr) => {
    const date = new Date(dateStr);
    return new Intl.DateTimeFormat('en-GB', {
      day: '2-digit',
      month: 'short',
      year: 'numeric'
    }).format(date);
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
      <Header />
      <h1>Results for : {searchQuery}</h1>
      <div className={styles.searchResultsContainer}>
        {searchResults.map((movie) => (
          (movie.poster_url && movie.rating > 0) ? (
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
    </>
  );
};

export default SearchPage;
