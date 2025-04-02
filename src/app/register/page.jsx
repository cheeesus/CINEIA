'use client'; // Ensure client-side rendering

import { useState } from "react";
import { registerUser } from "../../helpers/auth";
import { useRouter } from "next/navigation"; // Use next/navigation for routing in App Directory
import styles from "@/styles/login.module.css";
import Header from "@/components/Header";

export default function Register() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [age, setAge] = useState("");
  const [error, setError] = useState("");
  const router = useRouter(); 

  const handleRegister = async (e) => {
    e.preventDefault();
    try {
      // Send data to API 
      await registerUser(email, password, age);
      router.push("/login"); // Redirect to login page after registration
    } catch (err) {
      setError(err.message); 
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
          {error && <p>{error}</p>} {/* Display any error */}
          <button className={styles.submitBtn} type="submit">Register</button>
        </form>
      </div>
    </div>
  );
}
