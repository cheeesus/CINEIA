"use client";
import React, { useEffect, useState, useContext } from "react";
import Header from "@/components/Header";
import RecentMoviesList from "@/components/RecentMoviesListSlider"; // Assuming you have this component for listing movies
import TopRatedSlider from "@/components/TopRatedSlider"
import PopularMoviesByPreference from "@/components/PopularByPreference";
import Recommended from "@/components/Recommended"
import { UserContext } from "@/context/UserContext";

export default function Home() {
  const { user, isLoggedIn } = useContext(UserContext);

  return (
    <div>
      <Header />
      <main>
        {isLoggedIn ? (
          <><h1>Recommended For You</h1><Recommended /></>
        ) : ( <></>)
        }
        <h1>Recent Releases</h1>
        <RecentMoviesList /> 
        <br></br>
        <h1>Top Rated</h1>
        <TopRatedSlider />
        <br/>   
        {isLoggedIn ? (
          <>
          <h1>Popular by genre</h1>
          <PopularMoviesByPreference /> 
          </>
          ) : ( <></>)
        }
      </main>
    </div>
  );
}
