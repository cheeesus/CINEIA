# tests/test_movies.py

import pytest
from app import create_app
import psycopg2
import json

@pytest.fixture
def app():
    # Create and configure the Flask app for testing
    app = create_app()
    app.config['TESTING'] = True  # Enable testing mode for the app
    yield app

@pytest.fixture
def client(app):
    # Get the Flask test client
    return app.test_client()

@pytest.fixture
def init_db():
    # Set up the database with some test data
    conn = psycopg2.connect(
        host='postgresql-yannr.alwaysdata.net',
        database='yannr_00',
        user='yannr_01',
        password='Projet1234'
    )
    cursor = conn.cursor()
    
    # Ensure the movies table exists
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS movies (
            id SERIAL PRIMARY KEY,
            title VARCHAR(255) NOT NULL,
            genre VARCHAR(100) NOT NULL
        );
    """)
    
    # Insert some test data into the movies table
    cursor.execute("""
        INSERT INTO movies (title, genre) 
        VALUES 
            ('Movie A', 'Action'),
            ('Movie B', 'Comedy'),
            ('Movie C', 'Drama')
        ON CONFLICT (id) DO NOTHING;
    """)
    conn.commit()
    cursor.close()
    conn.close()

    yield  # After the test, clean up the data

    # Cleanup: drop the movies table after testing
    conn = psycopg2.connect(
        host='your_host.alwaysdata.net',
        database='your_database_name',
        user='your_database_user',
        password='your_database_password'
    )
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS movies;")
    conn.commit()
    cursor.close()
    conn.close()

def test_get_movies(client, init_db):
    # Send a GET request to the /movies/ route
    response = client.get('/movies/')
    
    # Check that the response status code is 200 (OK)
    assert response.status_code == 200
    
    # Verify that the response data matches the movies in the database
    data = response.get_json()
    
    # Test if the number of movies returned is correct
    assert len(data) == 3  # There should be 3 movies in the database

    # Test if the movies have the correct titles and genres
    assert data[0]['title'] == 'Movie A'
    assert data[0]['genre'] == 'Action'
    assert data[1]['title'] == 'Movie B'
    assert data[1]['genre'] == 'Comedy'
    assert data[2]['title'] == 'Movie C'
    assert data[2]['genre'] == 'Drama'
