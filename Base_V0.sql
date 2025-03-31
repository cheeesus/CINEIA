CREATE TABLE movies (
    id SERIAL PRIMARY KEY,
    is_adult BOOLEAN NOT NULL,
    budget BIGINT CHECK (budget >= 0),
    original_language VARCHAR(10),
    title VARCHAR(255) NOT NULL,
    overview TEXT,
    popularity FLOAT NOT NULL,
    poster_path VARCHAR(255),
    release_date DATE,
    revenue BIGINT CHECK (revenue >= 0),
    runtime INT,
    vote_average FLOAT CHECK (vote_average BETWEEN 0 AND 10),
    vote_count INT CHECK (vote_count >= 0),
    director VARCHAR(255)
);

CREATE TABLE genres (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL
);

CREATE TABLE movie_genre (
    movie_id INT REFERENCES movies(id) ON DELETE CASCADE,
    genre_id INT REFERENCES genres(id) ON DELETE CASCADE,
    PRIMARY KEY (movie_id, genre_id)
);

CREATE TABLE keywords (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) UNIQUE NOT NULL
);

CREATE TABLE movie_keyword (
    movie_id INT REFERENCES movies(id) ON DELETE CASCADE,
    keyword_id INT REFERENCES keywords(id) ON DELETE CASCADE,
    PRIMARY KEY (movie_id, keyword_id)
);

-- FINI ----------------------------------------

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash BYTEA NOT NULL,
    age INT CHECK (age >= 0)
);

CREATE TABLE user_preferences (
    user_id INT REFERENCES users(id) ON DELETE CASCADE,
    genre_id INT REFERENCES genres(id) ON DELETE CASCADE,
    PRIMARY KEY (user_id, genre_id)
);

CREATE TABLE view_history (
    user_id INT REFERENCES users(id) ON DELETE CASCADE,
    movie_id INT REFERENCES movies(id) ON DELETE CASCADE,
    view_date DATE DEFAULT CURRENT_DATE,
    PRIMARY KEY (user_id, movie_id, view_date)
);

CREATE TABLE users_ratings (
    user_id INT REFERENCES users(id) ON DELETE CASCADE,
    movie_id INT REFERENCES movies(id) ON DELETE CASCADE,
    rating FLOAT CHECK (rating BETWEEN 0 AND 10) NOT NULL,
    rate_date DATE DEFAULT CURRENT_DATE,
    PRIMARY KEY (user_id, movie_id)
);

-- Vider les films et genres
-- TRUNCATE TABLE movie_genre, movies, genres, keywords, movie_keyword RESTART IDENTITY CASCADE;
-- TRUNCATE TABLE users_ratings, view_history, user_preferences RESTART IDENTITY CASCADE;

-- -- Supprimer la BD 
-- DROP TABLE IF EXISTS movie_keyword;
-- DROP TABLE IF EXISTS keywords;
-- DROP TABLE IF EXISTS users_ratings;
-- DROP TABLE IF EXISTS view_history;
-- DROP TABLE IF EXISTS user_preferences;
-- DROP TABLE IF EXISTS users;
-- DROP TABLE IF EXISTS movie_genre;
-- DROP TABLE IF EXISTS genres;
-- DROP TABLE IF EXISTS movies;
