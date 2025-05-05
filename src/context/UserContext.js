"use client";
import React, { createContext, useState, useEffect } from "react";
import Cookies from "js-cookie";
import { getCurrentUser, isAuthenticated } from "@/helpers/auth";

// Create Context
export const UserContext = createContext(null);

// Provider Component
export const UserProvider = ({ children }) => {
  const [user, setUser] = useState(null); // Current user
  const [isLoggedIn, setIsLoggedIn] = useState(false); // Login state

  useEffect(() => {
    // Check login status on app load
    const loggedIn = isAuthenticated();
    setIsLoggedIn(loggedIn);

    if (loggedIn) {
      const currentUser = getCurrentUser(); // Fetch user info from token
      if (currentUser) {
        setUser(currentUser);  // Set user object in context
      } 
    }  
  }, []);

  const login = (userData) => {
    setUser(userData);  // Set user data in context (including token and email)
    setIsLoggedIn(true);
  };

  const logout = () => {
    setUser(null);  // Clear user data
    setIsLoggedIn(false);
    Cookies.remove("token");
  };

  return (
    <UserContext.Provider value={{ user, isLoggedIn, login, logout }}>
      {children}
    </UserContext.Provider>
  );
};
