"use client";
import React, { useEffect, useState } from "react";
import Header from "@/components/Header";
import "../styles/movieSlider.css";
import RecentMoviesList from "@/components/RecentMoviesListSlider"; // Assuming you have this component for listing movies
import TopRatedSlider from "@/components/TopRatedSlider"

export default function Home() {
  return (
    <div>
      <Header />
      <main>
        <h1>Recent Releases</h1>
        <RecentMoviesList /> 
        <br></br>
        <h1>Top Rated</h1>
        <TopRatedSlider />   
      </main>
    </div>
  );
}
