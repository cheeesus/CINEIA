'use client'; // Ensure client-side rendering

import { useState } from "react";
import { registerUser } from "../../helpers/auth";
import { useRouter } from "next/navigation"; // Use next/navigation for routing in App Directory
import styles from "@/styles/login.module.css";
import Header from "@/components/Header";

const genresList = [
  "Western", "Drama", "Action", "Crime", "Mystery", "Thriller", "Horror",
  "Adventure", "Science Fiction", "Romance", "Comedy", "War", "Fantasy",
  "Animation", "Family", "History", "TV Movie", "Music", "Documentary"
];

export default function Register() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [age, setAge] = useState("");
  const [selectedGenres, setSelectedGenres] = useState([]);
  const [error, setError] = useState("");
  const router = useRouter(); 

  const maxGenres = 5;

  const handleRegister = async (e) => {
    e.preventDefault();
    try {
      // Send data to API 
      await registerUser(email, password, age, selectedGenres);
      router.push("/login"); // Redirect to login page after registration
    } catch (err) {
      setError(err.message); 
    }
  };

  const toggleGenre = (genre) => {
    if (selectedGenres.includes(genre)) {
      setSelectedGenres(selectedGenres.filter((g) => g !== genre));
    } else if (selectedGenres.length < maxGenres) {
      setSelectedGenres([...selectedGenres, genre]);
    }
  };

  return (
    <div className={styles.background}>
      <Header/>
      <div className={styles.formContainer}>
        <h2 className={styles.title}>Register</h2>
        <form className={styles.form} onSubmit={handleRegister}>
          <input
            className={styles.input}
            type="email"
            placeholder="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />
          <input
            className={styles.input}
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
          <input
            className={styles.input}
            type="number"
            placeholder="Age"
            value={age}
            onChange={(e) => setAge(e.target.value)}
          />
          <div className={styles.genresContainer}>
            <h3 className={styles.subTitle}>Select up to {maxGenres} Genres</h3>
            <div className={styles.genresList}>
              {genresList.map((genre) => (
                <div
                  key={genre}
                  className={`${styles.genreItem} ${
                    selectedGenres.includes(genre) ? styles.selected : ""
                  }`}
                  onClick={() => toggleGenre(genre)}
                >
                  {genre}
                </div>
              ))}
            </div>
          </div>

          {error && <p>{error}</p>} {/* Display any error */}
          <button className={styles.submitBtn} type="submit">Register</button>
        </form>
      </div>
    </div>
  );
}
