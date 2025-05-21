// helpers/auth.js
import axios from "axios";
import Cookies from "js-cookie";
import {jwtDecode} from "jwt-decode"; // Install via npm: npm install jwt-decode

const API_URL = "http://127.0.0.1:5000";

// Register user
export const registerUser = async (email, password, age, selectedGenres) => {
  try {
    const response = await axios.post(`${API_URL}/auth/register`, {
      email,
      password,
      age,
      selectedGenres,
    });
    return response.data;
  } catch (error) {
    throw new Error(error.response?.data?.error || "Registration failed");
  }
};

// Login user and save token in cookie
export const loginUser = async (email, password) => {
  try {
    const response = await axios.post(`${API_URL}/auth/login`, { email, password });
    const { token, email: userEmail } = response.data;

    // Extract the first part of the email as username
    const username = userEmail.split("@")[0];

    // Store token in cookies (secure: true for HTTPS, httpOnly should be set in backend)
    Cookies.set("token", token, { expires: 0.5, secure: true , sameSite: "Strict" });

    return { token, username };
  } catch (error) {
    throw new Error(error.response?.data?.error || "Login failed");
  }
};

// Check if the user is logged in (also checks token expiration)
export const isAuthenticated = () => {
  const token = Cookies.get("token");
  if (!token) return false;

  try {
    const decoded = jwtDecode(token);
    const isTokenExpired = decoded.exp * 1000 < Date.now(); // Convert to milliseconds

    if (isTokenExpired) {
      Cookies.remove("token");
      return false;
    }

    return true;
  } catch (error) {
    return false;
  }
};

// Get current user info safely
export const getCurrentUser = () => {
  const token = Cookies.get("token");
  if (!token) return null;
  try {
    const decoded = jwtDecode(token);
    if (!decoded.email) return null; // Ensure email exists in JWT
    return { 
      username: decoded.email.split("@")[0], // Extract username from email
      email: decoded.email, // Store full email if needed
      userId: decoded.user_id // Store user ID
    };
  } catch (error) {
    return null;
  }
};
