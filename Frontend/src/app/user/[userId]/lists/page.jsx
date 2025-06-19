'use client';  // This marks the component as a client component
import { useEffect, useState, useContext } from 'react';
import axios from "axios";
import Link from "next/link"; 
import Header from "@/components/Header";
import styles from "@/styles/listsDetails.module.css";
import { UserContext } from "@/context/UserContext";
import { FaTrash, FaTimes } from "react-icons/fa";

// Load environment variables
const API_URL = process.env.NEXT_PUBLIC_API_URL;

const ListsDetails = () => {
  const { user, isLoggedIn } = useContext(UserContext);
  const [existingLists, setExistingLists] = useState([]); // List of user's lists

  // Fetch user's lists
  useEffect(() => {
    const fetchListsAndMovies = async () => {
        if (!user || !user.userId) {
        console.log("User not available yet.");
        return; // Exit if user is not yet set
        }

        try {
        // Fetch lists
        const listsResponse = await axios.get(
            `${API_URL}/users/${user.userId}/lists`,
            { headers: { Authorization: `Bearer ${user?.token}` } }
        );

        const lists = listsResponse.data;
        console.log("Fetched lists:", lists);

        // Fetch movies for each list
        const listsWithMovies = await Promise.all(
            lists.map(async (list) => {
            try {
                const moviesResponse = await axios.get(
                `${API_URL}/movies/${list.list_id}/movies`,
                { headers: { Authorization: `Bearer ${user?.token}` } }
                );

                const movieIds = moviesResponse.data.movie_ids;
                
                // Fetch movie names for each ID
                const moviesWithNames = await Promise.all(
                movieIds.map(async (movieId) => {
                    try {
                    const movieDetailsResponse = await axios.get(
                        `${API_URL}/movies/${movieId}`,
                        { headers: { Authorization: `Bearer ${user?.token}` } }
                    );
                    
                    return movieDetailsResponse.data;
                    } catch (error) {
                    console.error(`Failed to fetch details for movie ${movieId}:`, error);
                    return { id: movieId, name: "Unknown Movie" }; // Default to unknown movie
                    }
                })
                );

                return { ...list, movies: moviesWithNames };
            } catch (error) {
                console.error(`Failed to fetch movies for list ${list.id}:`, error);
                return { ...list, movies: [] }; // Default to empty movies if fetch fails
            }
            })
        );

        console.log("Lists with movie details:", listsWithMovies);
        setExistingLists(listsWithMovies); // Update state with lists and movies with names
        } catch (error) {
        console.error("Failed to fetch lists:", error);
        }
    };

    fetchListsAndMovies();
    }, [user]);

    // Delete a list
  const deleteList = async (listId) => {
    if (!window.confirm("Are you sure you want to delete this list?")) {
      return;
    }

    try {
      await axios.delete(
        `${API_URL}/movies/${listId}`,
        { headers: { Authorization: `Bearer ${user?.token}` } }
      );

      // Remove the list from state
      setExistingLists((prevLists) => prevLists.filter((list) => list.list_id !== listId));
      window.alert("List deleted successfully!");
    } catch (error) {
        window.alert("Failed to delete list!");
      console.error("Failed to delete list:", error);
    }
  };
  const deleteMovie = async (listId, movieId) => {
    if (!window.confirm("Êtes-vous sûr de vouloir supprimer ce film de la liste ?")) {
      return;
    }

    try {
      await axios.delete(
        `${API_URL}/movies/${listId}/movies/${movieId}`,
        { headers: { Authorization: `Bearer ${user?.token}` } }
      );

      // Mettre à jour l'état pour retirer le film de la liste
      setExistingLists((prevLists) =>
        prevLists.map((list) => {
          if (list.list_id === listId) {
            return {
              ...list,
              movies: list.movies.filter((movie) => movie.id !== movieId),
            };
          }
          return list;
        })
      );

      window.alert("Film supprimé avec succès !");
    } catch (error) {
      window.alert("Échec de la suppression du film !");
      console.error("Échec de la suppression du film :", error);
    }
  };




  if (!isLoggedIn) {
    return (
      <>
        <Header />
        <div>Please log in to view your lists.</div>
      </>
    );
  }

  return (
    <div className={styles.background}>
      <Header />
      <main className={styles.container}>
        {/* Lists Details */}
        <div className={styles.listsDetails}>
          <table className={styles.listsTable}>
            <thead>
              <tr>
                <th>List Name</th>
                <th>Movies</th>
                <th></th> 
              </tr>
            </thead>
            <tbody>
              {existingLists.length > 0 ? (
                existingLists.map((list) => (
                  <tr key={list.list_id}>
                    <td>{list.list_name}</td>
                    <td>
                      {list.movies && list.movies.length > 0 ? (
                        list.movies.map((movie) => (
                          <div key={movie.id} className={styles.listMovie}>
                            <Link href={`/movies/${movie.id}`}>
                              {movie.title}
                            </Link>
                            <FaTimes
                              className={styles.movieDeleteIcon}
                              onClick={() => deleteMovie(list.list_id, movie.id)}
                            />
                          </div>
                        ))
                      ) : (
                        <span>Aucun film dans cette liste.</span>
                      )}
                    </td>
                    <td>
                      <FaTrash
                        className={styles.deleteIcon}
                        onClick={() => deleteList(list.list_id)}
                      />
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={2}>No lists available. Create a new one!</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </main>
    </div>
  );
};

export default ListsDetails;
