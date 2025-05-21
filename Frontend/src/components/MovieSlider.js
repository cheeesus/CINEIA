import React, { useRef } from 'react';
import Link from 'next/link';

export default function MovieSlider({ recentMovies, hasMore, loadMore }) {
    const sliderRef = useRef(null);
    const [recentMovies, setRecentMovies] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [page, setPage] = useState(1);  // Track the current page
    const [hasMore, setHasMore] = useState(true);  // Flag to check if there are more movies

    // Function to fetch recent movies with pagination
    const fetchRecentMovies = async () => {
    try {
        const response = await axios.get("http://127.0.0.1:5000/movies/", {
        params: {
            page: page,
            limit: 24,  // Limit the number of movies per request
        },
        });
        const newRecentMovies = response.data;

        if (newRecentMovies.length < 24) {
        setHasMore(false);  // If there are less than 24 movies, it's the last page
        }

        setRecentMovies((prevMovies) => [...prevMovies, ...newRecentMovies]);
        setLoading(false);
    } catch (err) {
        setError("Failed to load movies");
        setLoading(false);
    }
    };

  // Scroll the slider left
  const scrollLeft = () => {
    if (sliderRef.current) {
      sliderRef.current.scrollBy({ left: -300, behavior: 'smooth' });
    }
  };

  // Scroll the slider right
  const scrollRight = () => {
    if (sliderRef.current) {
      sliderRef.current.scrollBy({ left: 300, behavior: 'smooth' });
    }
  };

  return (
    <>
      <div className="movie-slider-container">
        <button className="scroll-btn left" onClick={scrollLeft}>←</button>
        
        <div className="movie-slider" ref={sliderRef}>
          {recentMovies.map((movie) => (
            movie.poster_url ? (
              <div key={movie.id} className="movie-item">
                <Link href={`/movies/${movie.id}`}>
                  <img 
                    src={movie.poster_url || "https://via.placeholder.com/500x750?text=No+Image+Available"} 
                    alt={movie.title} 
                    className="movie-poster" 
                  />
                  <h2>{movie.title}</h2>
                </Link>
              </div>
            ) : null
          ))}
        </div>

        <button className="scroll-btn right" onClick={scrollRight}>→</button>
      </div>

      {hasMore && (
        <Link href="/all-movies">
          <button onClick={loadMore} className="load-more-btn">
            Load More
          </button>
        </Link>
      )}
    </>
  );
}
