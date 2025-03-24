import Image from "next/image";
import React, { useContext } from "react";
import { Search } from "lucide-react";
import styles from "@/app/Header.module.css";
import { UserContext } from '@/context/UserContext'; // Import UserContext hook
import Link from "next/link"; // Use Link for navigation

const Header = () => {
  const { user, isLoggedIn, logout } = useContext(UserContext); // Access user and logout function from UserContext

  const handleLogout = () => {
    logout();
  }
  return (
    <header className={styles.header}>
      <div className={styles.logo}>
        <Image src="/CineIA.png" alt="CinéIA Logo" width={100} height={50} />
      </div>
      <div className={styles.search}>
        <div className={styles.searchWrapper}>
          <input
            type="text"
            placeholder="Search for movies..."
            className={styles.searchInput}
          />
          <button className={styles.searchButton}>
            <Search size={18} />
          </button>
        </div>
      </div>

      <nav className={styles.nav}>
        <ul className={styles.navList}>
          <li className={styles.navItem}>
            <Link href="/" className={styles.navLink}>Home</Link>
          </li>
          <li className={styles.navItem}>
            <Link href="/movies" className={styles.navLink}>Movies</Link>
          </li>
          <li className={styles.navItem}>
            <Link href="/about" className={styles.navLink}>About</Link>
          </li>
          {isLoggedIn ? (
            <>
              <li className={styles.navItem}>
              <span className={styles.navLink}>Welcome, {user.email}</span>
              </li>
              <li className={styles.navItem}>
                <button
                  onClick={handleLogout}
                  className={`${styles.navLink} ${styles.logoutButton}`}
                >
                  Logout
                </button>
              </li>
            </>
          ) : (
            // Show Login link when not logged in
            <li className={styles.navItem}>
              <Link href="/login" className={styles.navLink}>Login</Link>
            </li>
          )}
        </ul>
      </nav>
    </header>
  );
};

export default Header;
