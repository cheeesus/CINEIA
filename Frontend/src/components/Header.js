
import { useState, useEffect, useRef, useContext } from "react";
import Link from "next/link";
import Image from "next/image";
import { useRouter } from "next/navigation";
import axios from "axios";
import { UserContext } from '@/context/UserContext';
import styles from "../styles/Header.module.css";
import { Search, X } from "lucide-react";
import { FaSignInAlt, FaSignOutAlt, FaUser, FaListAlt } from "react-icons/fa";

export default function Header() {
  const [searchQuery, setSearchQuery] = useState("");
  const [searchResults, setSearchResults] = useState([]);
  const [showDropdown, setShowDropdown] = useState(false);
  const { user, isLoggedIn, logout } = useContext(UserContext);
  const router = useRouter();
  const dropdownRef = useRef(null);

  useEffect(() => {
    const fetchSearchResults = async () => {
      if (!searchQuery.trim()) {
        setSearchResults([]);
        setShowDropdown(false);
        return;
      }

      try {
        const response = await axios.get("http://127.0.0.1:5000/api/movies/search", {
          params: { query: searchQuery },
        });

        setSearchResults(response.data.movies);
        setShowDropdown(true);
      } catch (error) {
        console.error("Search error:", error);
      }
    };

    const delayDebounce = setTimeout(() => {
      fetchSearchResults();
    }, 300); // Debounce API calls (wait 300ms)

    return () => clearTimeout(delayDebounce);
  }, [searchQuery]);

  // Close dropdown when clicking outside
  useEffect(() => {
    function handleClickOutside(event) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setShowDropdown(false);
      }
    }

    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  // Close on Escape key
  useEffect(() => {
    const handleEscape = (event) => {
      if (event.key === "Escape") {
        setShowDropdown(false);
      }
    };
    document.addEventListener("keydown", handleEscape);
    return () => document.removeEventListener("keydown", handleEscape);
  }, []);
  const handleLogin = () => {
    router.push("/login")
  }

  const handleLogout = () => {
    logout();
    router.push("/");
  }
  const handleSearch = (e) => {
    if (e.key === 'Enter') {
      router.push(`/search/${searchQuery}`)
    }
  }

  return (
    <>
      <header className={styles.header}>
        <div className={styles.logo}>
          <Link href="/"><Image src="/CineIA.png" alt="CinéIA Logo" width={100} height={50} /></Link>
        </div>
        <div className={styles.search}>
          <div className={styles.searchWrapper} style={{ position: 'relative' }}>
            <input
              type="text"
              placeholder="Search for movies..."
              className={styles.searchInput}
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onFocus={() => setShowDropdown(true)}
              onKeyDown={handleSearch}
            />
            {showDropdown ? (
              <button
                className={styles.closeButton}
                onClick={() => setShowDropdown(false)}
                aria-label="Close search dropdown"
              >
                <X size={20} />
              </button>
            ) : (
              <button className={styles.searchButton} aria-label="Search">
                <Search size={18} />
              </button>
            )}

            {showDropdown && searchResults.length > 0 && (
              <div className={styles.searchOverlay} ref={dropdownRef}>
                <div className={styles.searchResults}>
                  {searchResults.map((movie) => (
                    <Link
                      key={movie.id}
                      href={`/movies/${movie.id}`}
                      className={styles.resultItem}
                      onClick={() => setShowDropdown(false)}
                    >
                      <span>{movie.title}</span>
                    </Link>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Navigation Menu */}
        <nav className={styles.nav}>
          <ul className={styles.navList}>
            {isLoggedIn ? (
              <>
                <li className={styles.navItem}>
                  <span className={styles.navLink}>Welcome, {user?.username}</span>
                </li>
                <li className={styles.navItem} >
                  <Link key={user.userId} href={`/user/${user.userId}`}>
                    <FaUser size={20}/>
                  </Link>
                </li>
                <li className={styles.navItem} >
                  <Link href={`/user/${user.userId}/lists`} >
                    <FaListAlt size={25} />
                  </Link>
                </li>
                <li className={styles.navItem}>
                  <button onClick={handleLogout} className={styles.buttons}>
                    Logout <FaSignOutAlt style={{ paddingLeft: "3px", width: "20px"}}/>
                  </button>
                </li>
              </>
            ) : (
              <li className={styles.navItem}>
                <button onClick={handleLogin} className={styles.buttons}>
                  Login <FaSignInAlt style={{ paddingLeft: "3px", width: "20px"}} />
                </button>
              </li>
            )}
          </ul>
        </nav>
      </header>

    </>
  );
}
