"use client";
import React, { useEffect, useState, useContext } from "react";
import Header from "@/components/Header";
import RecentMoviesList from "@/components/RecentMoviesListSlider";
import TopRatedSlider from "@/components/TopRatedSlider";
import PopularMoviesByPreference from "@/components/PopularByPreference";
import Recommended from "@/components/Recommended";
import { UserContext } from "@/context/UserContext";

export default function Home() {
  const { user, isLoggedIn } = useContext(UserContext);

  // ✅ 调试：打印 API 地址确认是否读取了 .env.local
  useEffect(() => {
    console.log("🔍 NEXT_PUBLIC_API_BASE =", process.env.NEXT_PUBLIC_API_BASE);
  }, []);

  return (
    <div>
      <Header />
      <main>
        {isLoggedIn && (
          <>
            <h1>Recommended For You</h1>
            <Recommended />
          </>
        )}
        <h1>Recent Releases</h1>
        <RecentMoviesList />
        <br />
        <h1>Top Rated</h1>
        <TopRatedSlider />
        <br />
        {isLoggedIn && (
          <>
            <h1>Popular by genre</h1>
            <PopularMoviesByPreference />
          </>
        )}
      </main>
    </div>
  );
}
