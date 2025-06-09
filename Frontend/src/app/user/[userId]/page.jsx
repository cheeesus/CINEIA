'use client';  // This marks the component as a client component
import { useEffect, useState, useContext, use } from 'react';
import axios from "axios";
import Header from "@/components/Header";
import { UserContext } from "@/context/UserContext";
import styles from '@/styles/profilePage.module.css';

const allGenres = [
  "Western", "Drama", "Action", "Crime", "Mystery", "Thriller", "Horror",
  "Adventure", "Science Fiction", "Romance", "Comedy", "War", "Fantasy",
  "Animation", "Family", "History", "TV Movie", "Music", "Documentary"
];

const UserProfile = ({params}) => {
  const { user, isLoggedIn } = useContext(UserContext);
  const [userId, setUserId] = useState(null);
  const [profileData, setProfileData] = useState(null);
  const [checkedMovies, setCheckedMovies] = useState([]);
  const [selectedGenres, setSelectedGenres] = useState([]);
  const [isSaving, setIsSaving] = useState(false);


  // Unwrap params and set userId
  useEffect(() => {
    const getUserId = async () => {
      const resolvedParams = await params;
      setUserId(resolvedParams.userId);
    };
    getUserId();
  }, [params]);

  useEffect(() => {
    const fetchProfile = async () => {
        try {
            const response = await axios.get(`http://127.0.0.1:5000/api/users/${userId}`, {
                headers: { Authorization: `Bearer ${user?.token}` },
            });
            setProfileData(response.data);
            setCheckedMovies(response.data.checked_movies || []);
            setSelectedGenres(response.data.genres?.map(g => g.genre_name) || []);
        } catch (err) {
            console.error('failed to fetch user profile:', err);
        }
    };

    if (userId) {
        fetchProfile();
    }
  }, [userId, user]);

  if(!profileData) {
    return <div>Loading profile...</div>
  }

  const toggleGenre = (genre) => {
    setSelectedGenres(prev =>
      prev.includes(genre) ? prev.filter(g => g !== genre) : [...prev, genre]
    );
  };

  const saveGenres = async () => {
    if (!isLoggedIn) {
      alert("You need to be logged in to update genres.");
      return;
    }
    setIsSaving(true);
    console.log(selectedGenres);
    try {
      await axios.put(
        `http://127.0.0.1:5000/api/users/${userId}/genres`,
        { preferred_genres: selectedGenres },
        { headers: { Authorization: `Bearer ${user?.token}` } }
      );
      alert("Preferred genres updated!");
    } catch (err) {
      console.error(err);
      alert("Failed to update genres.");
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div>
      <Header />
      <main className={styles.container}>
        {/* User Details */}
        <div className={styles.profileDetails}>
          <h1>Welcome, {user?.username}</h1>
          <table className={styles.detailsTable}>
            <tbody>
              <tr>
                <th>Email:</th>
                <td>{profileData.email}</td>
              </tr>
              <tr>
                <th>Age:</th>
                <td>{profileData.age}</td>
              </tr>
              <tr>
                <th>Preferred Genres:</th>
                <td>
                  {/* Editable genres list */}
                  <div className={styles.genresList}>
                    {allGenres.map((genre) => (
                      <label key={genre} style={{ marginRight: 10 }}>
                        <input
                          type="radio"
                          checked={selectedGenres.includes(genre)}
                          onChange={() => toggleGenre(genre)}
                        />
                        {genre}
                      </label>
                    ))}
                  </div>
                  <button onClick={saveGenres} disabled={isSaving}>
                    {isSaving ? "Saving..." : "Save Changes"}
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        {/* Checked Movies */}
        <div className={styles.checkedMovies}>
          <h2>History of Checked Movies</h2>
          {checkedMovies.length > 0 ? (
            <table className={styles.moviesTable}>
              <thead>
                <tr>
                  <th>Title</th>
                  <th>Rating</th>
                </tr>
              </thead>
              <tbody>
                {checkedMovies.map((movie) => (
                  <tr key={movie.id}>
                    <td>{movie.title}</td>
                    <td>{movie.rating}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <p>No movies checked yet.</p>
          )}
        </div>
      </main>
    </div>
  );

  
};

export default UserProfile;
