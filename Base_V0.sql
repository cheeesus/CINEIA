------------ BASE

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

-- USER ----------------------------------------

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

-- LIST ----------------------------------------
CREATE TABLE lists (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    UNIQUE (user_id, name) 
);

CREATE TABLE list_movies (
    list_id INT REFERENCES lists(id) ON DELETE CASCADE,
    movie_id INT REFERENCES movies(id) ON DELETE CASCADE,
    PRIMARY KEY (list_id, movie_id)
);

-- CASTING ----------------------------------------
CREATE TABLE actors (
    id INT PRIMARY KEY,
    actor_name VARCHAR(100) NOT NULL,
    profile_path VARCHAR(255)
);

CREATE TABLE casting (
    movie_id INT REFERENCES movies(id) ON DELETE CASCADE,
    actor_id INT REFERENCES actors(id) ON DELETE CASCADE,
    movie_character VARCHAR(255),
    PRIMARY KEY (movie_id, actor_id, movie_character)
);

-- AJOUT DE backdrop_path--------------------------
ALTER TABLE movies ADD COLUMN backdrop_path VARCHAR(255);



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

-- -- Index
-- CREATE INDEX idx_view_history_user_date ON view_history(user_id, view_date DESC);
-- CREATE INDEX idx_users_ratings_score ON users_ratings(user_id, rating DESC);





-- -------------------------------
-- --- Lister toutes les listes d’un utilisateur (avec leur user_id)
-- SELECT * FROM lists WHERE user_id = $1; -- Remplace $1 par l'ID de l'utilisateur

-- -------------------------------
-- --- Lister tous les films d’une liste d’un utilisateur (toutes les infos du film)
-- SELECT m.*
-- FROM movies m
-- JOIN list_movies lm ON m.id = lm.movie_id
-- JOIN lists l ON l.id = lm.list_id
-- WHERE l.user_id = $1 AND l.name = $2; -- $1 = id utilisateur, $2 = nom de la liste

-- -------------------------------
-- --- Créer une liste (si elle n’existe pas) avec id utilisateur + nom
-- INSERT INTO lists (user_id, name)
-- VALUES ($1, $2)
-- ON CONFLICT (user_id, name) DO NOTHING
-- RETURNING id; -- $1 = id utilisateur, $2 = nom de la liste


-- -------------------------------
-- --- Ajouter un film à une liste à partir du nom et id utilisateur
-- -- Étape 1 : Récupérer l’id de la liste
-- SELECT id FROM lists WHERE user_id = $1 AND name = $2; -- $1 = id utilisateur, $2 = nom de la liste

-- -- Étape 2 : Ajouter le film dans la liste
-- INSERT INTO list_movies (list_id, movie_id)
-- VALUES ($3, $4)
-- ON CONFLICT DO NOTHING; -- $3 = list_id obtenu à l'étape 1, $4 = id du film

-- ------------------------------
-- --- Supprimer une liste à partir de l’id utilisateur et du nom de la liste
-- DELETE FROM lists
-- WHERE user_id = $1 AND name = $2; -- $1 = id utilisateur, $2 = nom de la liste


-- -- -- Index pour List
-- CREATE INDEX idx_lists_user_id ON lists(user_id);
-- CREATE INDEX idx_list_movies_list_id ON list_movies(list_id);
-- CREATE INDEX idx_lists_user_id_name ON lists(user_id, name);
