"use client";
import { useState, useContext } from "react";
import { UserContext } from "@/context/UserContext";
import { loginUser } from "../../helpers/auth";
import { useRouter } from "next/navigation";
import Link from 'next/link'

import Header from "@/components/Header";

import styles from "@/styles/login.module.css";

export default function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const { login } = useContext(UserContext);  // Context for managing the user state
  const router = useRouter();

  const handleLogin = async (e) => {
    e.preventDefault();
    try {
      const response = await loginUser(email, password);  // Login user
      const { token, username: username } = response;  // Destructure token and username from the response
      login({ username, token });  // Set user context with email and token
      console.log(response.username);
      router.push("/");  // Redirect to the home page after successful login
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <div className={styles.background}>
      <Header />
      <div className={styles.formContainer}>
        <h2 className={styles.title}>Login</h2>
        <form className={styles.form} onSubmit={handleLogin}>
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

          <span>Don't have an account? <Link href="/register" style={ {textDecoration: 'underline'}}>Register</Link></span>
          {error && <p>{error}</p>}
          <button className={styles.submitBtn} type="submit">
            Login
          </button>
        </form>
      </div>
    </div>
  );
}
