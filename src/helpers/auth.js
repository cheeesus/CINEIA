// helpers/auth.js
import axios from "axios";
import Cookies from "js-cookie";

const API_URL = "http://127.0.0.1:5000"; // Change to your Flask API URL

// Register user
export const registerUser = async (email, password, age) => {
    try {
      const response = await axios.post(`${API_URL}/auth/register`, {
        email,
        password,
        age,
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
      const { token, email: userEmail } = response.data;  // Destructure the response
      // Store the JWT token in a cookie
      Cookies.set("token", token, { expires: 10 });
      return { token, email: userEmail };  // Return the token and email
    } catch (error) {
      throw new Error(error.response?.data?.error || "Login failed");
    }
  };

// Logout user (remove token)
export const logoutUser = async () => {
  try {
    await axios.post(`${API_URL}/auth/logout`);
    Cookies.remove("token");
  } catch (error) {
    console.error("Logout failed", error);
  }
};

// Check if the user is logged in (token is available)
export const isAuthenticated = () => {
  const token = Cookies.get("token");
  return token ? true : false;
};

// Get current user info (by decoding JWT)
export const getCurrentUser = () => {
  const token = Cookies.get("token");
  if (!token) return null;
  const decodedToken = JSON.parse(atob(token.split('.')[1])); // Decode JWT to get user info
  return decodedToken;
};
