"use client";
import React, { useEffect, useState, useContext } from "react";
import Header from "@/components/Header";
import "../styles/movieSlider.css";
import RecentMoviesList from "@/components/RecentMoviesListSlider"; // Assuming you have this component for listing movies
import TopRatedSlider from "@/components/TopRatedSlider"
import Recommended from "@/components/Recommended"
import { UserContext } from "@/context/UserContext";

export default function Home() {
  const { user, isLoggedIn } = useContext(UserContext);
  return (
    <div>
      <Header />
      <main>
        {isLoggedIn ? (
          <><h2>Recommended For You</h2><Recommended /></>
        ) : ( <></>)
        }
        <h1>Recent Releases</h1>
        <RecentMoviesList /> 
        <br></br>
        <h1>Top Rated</h1>
        <TopRatedSlider />   
      </main>
    </div>
  );
}
