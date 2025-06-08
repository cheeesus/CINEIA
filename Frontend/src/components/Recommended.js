import React, { useEffect, useState, useRef, useContext } from "react";
import { UserContext } from '@/context/UserContext';
import Link from "next/link"; 
import axios from "axios"; 


const RecommendedSlider = () => {
  const { user, isLoggedIn, logout } = useContext(UserContext);
  const { RecommendedMovies , setRecommendedMovies} = useState([]);
  const [page, setPage] = useState(1);
  const fetchRecommendedMovies = async (user) => {
    try {
      const response = await axios.get(`http://127.0.0.1:5000/api/recommend/${user.userId}`, {
        params: {
          page: page,
          limit: 24, 
        },
      });
      const newRecommendedMovies = response.data;

      if (newRecommendedMovies.length < 24) {
        setHasMore(false);  // If there are less than 24 movies, it's the last page
      }

      setRecommendedMovies((prevMovies) => [...prevMovies, ...newRecommendedMovies]);
      setLoading(false);

    } catch (err) {
      setError("Failed to load movies");
      setLoading(false);
    }
  }

  useEffect(() => {
      fetchRecommendedMovies(user);
    }, [page]);
};
export default RecommendedSlider;
