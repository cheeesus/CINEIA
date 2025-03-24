"use client";
import React, { useEffect, useState } from "react";
import Header from "@/components/Header";
import "../styles/MoviesList.css";
import MoviesList from "@/components/MoviesList"; // Assuming you have this component for listing movies

export default function Home() {
  return (
    <div>
      <Header />
      <main>
        <h1>Welcome to CinéIA</h1>
        <MoviesList /> {/* This component will fetch and list movies */}
      </main>
    </div>
  );
}
