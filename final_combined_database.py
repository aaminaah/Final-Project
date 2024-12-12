import os
import random
import requests
import sqlite3
import json
import csv
import base64

# Constants and configurations for APIs
BOOK_API_KEY = 'AIzaSyDp75ZQEtUDinfAW--tDW_pUBt4f6dyxas'
SPOTIFY_CLIENT_ID = "8ef7803a77064d34bb353919da745f09"
SPOTIFY_CLIENT_SECRET = "bb633203692a41e5b9cda1a1f1f81877"
TMDB_API_HEADERS = {
    "accept": "application/json",
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiJjNmNiYzg3YTUxNzY0YzEzODQ0NTE2OTg4ZDliNzMyZCIsIm5iZiI6MTczMzg1MzYwMS4wMDE5OTk5LCJzdWIiOiI2NzU4ODFhMDM2ODg0NTlkNzU4OWFmMjYiLCJzY29wZXMiOlsiYXBpX3JlYWQiXSwidmVyc2lvbiI6MX0.UDruEGkcZ3wC4F4tmApouiPAuVzqWLVRmxn2nYbhwpI"
}
TMDB_SEARCH_URL = "https://api.themoviedb.org/3/search/movie"
TMDB_GENRE_URL = "https://api.themoviedb.org/3/genre/movie/list?language=en"

BOOK_GENRES = ["fiction", "mystery", "fantasy", "romance", "science fiction", "history", "biography", "thriller", "adventure", "horror", "young adult", "philosophy", "classics", "humor", "poetry"]
MOVIE_TITLES = ["Barbie", "Home Alone", "3 Idiots", "Spy Kids", "Flipped", "The Godfather", "The Shawshank Redemption", "Pulp Fiction", "The Dark Knight", "Schindler's List", "Forrest Gump", "The Lord of the Rings: The Return of the King", "Fight Club", "Inception", "The Matrix", "The Silence of the Lambs", "Star Wars: Episode V - The Empire Strikes Back", "Goodfellas", "The Lord of the Rings: The Fellowship of the Ring", "The Lord of the Rings: The Two Towers", "The Green Mile", "The Godfather: Part II", "Se7en", "The Usual Suspects", "The Lion King", "Gladiator", "Saving Private Ryan", "The Departed", "The Prestige", "The Pianist", "The Dark Knight Rises", "The Avengers", "Titanic", "Jurassic Park", "The Terminator", "The Truman Show", "Back to the Future", "Ghostbusters", "Shershaah", "Good Will Hunting", "Braveheart", "The Shining", "Psycho", "The Sixth Sense", "The Exorcist", "A Clockwork Orange", "American History X", "The Good, the Bad and the Ugly", "A Fistful of Dollars", "For a Few Dollars More", "Unforgiven", "No Country for Old Men", "Fargo", "The Big Lebowski", "O Brother, Where Art Thou?", "True Grit", "The Revenant", "Birdman or (The Unexpected Virtue of Ignorance)", "The Grand Budapest Hotel", "Moonrise Kingdom", "The Royal Tenenbaums", "Fantastic Mr. Fox", "Isle of Dogs", "Reservoir Dogs", "Jackie Brown", "Kill Bill: Vol. 1", "Kill Bill: Vol. 2", "Death Proof", "Django Unchained", "The Hateful Eight", "Once Upon a Time in Hollywood", "Spirited Away", "My Neighbor Totoro", "Princess Mononoke", "Howl's Moving Castle", "Ponyo", "Castle in the Sky", "Kiki's Delivery Service", "Nausicaä of the Valley of the Wind", "Porco Rosso", "Lagaan", "Dilwale Dulhania Le Jayenge", "3 Idiots", "PK", "Gully Boy", "Queen", "Taare Zameen Par", "Zindagi Na Milegi Dobara", "Dangal", "Swades", "Rang De Basanti", "Barfi!", "Andhadhun", "Mughal-E-Azam", "Chak De! India", "Kahaani", "Dil Chahta Hai", "Gangs of Wasseypur", "Bajrangi Bhaijaan", "Kabhi Khushi Kabhie Gham", "Vicky Donor", "Om Shanti Om", "My Name Is Khan", "Devdas"]

DATABASE_NAME = 'combined.db'

# Functions related to Google Books API
def fetch_books(query, max_results=25, start_index=0):
    url = f"https://www.googleapis.com/books/v1/volumes?q={query}&maxResults={max_results}&startIndex={start_index}&key={BOOK_API_KEY}"
    response = requests.get(url)
    return response.json()

def store_book_data_in_db(data, cursor):
    for item in data.get('items', []):
        volume_info = item['volumeInfo']
        book_unique_id = item['id']
        title = volume_info.get('title', '')
        published_date = volume_info.get('publishedDate', '')
        average_rating = volume_info.get('averageRating', None)

        cursor.execute('''
            INSERT OR IGNORE INTO books (book_unique_id, title, published_date, average_rating)
            VALUES (?, ?, ?, ?)
        ''', (book_unique_id, title, published_date, average_rating))

        authors = volume_info.get('authors', [])
        for author in authors:
            cursor.execute('INSERT OR IGNORE INTO authors (name) VALUES (?)', (author,))
            cursor.execute('''
                INSERT OR IGNORE INTO book_authors (book_unique_id, author_id)
                SELECT ?, id FROM authors WHERE name = ?
            ''', (book_unique_id, author))

        categories = volume_info.get('categories', [])
        for category in categories:
            cursor.execute('INSERT OR IGNORE INTO categories (name) VALUES (?)', (category,))
            cursor.execute('''
                INSERT OR IGNORE INTO book_categories (book_unique_id, category_id)
                SELECT ?, id FROM categories WHERE name = ?
            ''', (book_unique_id, category))

# Functions related to Spotify API
def get_spotify_access_token(client_id, client_secret):
    credentials = f"{client_id}:{client_secret}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode()
    headers = {
        "Authorization": f"Basic {encoded_credentials}",
        "Content-Type": "application/x-www-form-urlencoded",
    }
    data = {"grant_type": "client_credentials"}
    response = requests.post("https://accounts.spotify.com/api/token", headers=headers, data=data)
    if response.status_code == 200:
        return response.json().get("access_token")
    else:
        print(f"Failed to retrieve token: {response.status_code}, {response.json()}")
        return None

def get_artist_info(client_id, client_secret, start_index, limit=25):
    access_token = get_spotify_access_token(client_id, client_secret)
    if not access_token:
        return []
    with open("100 artists - Sheet1.csv", "r") as file:
        reader = csv.reader(file)
        next(reader)
        artist_ids = [row[0] for row in reader]
        batch_ids = artist_ids[start_index:start_index + limit]
        if not batch_ids:
            return []

    url = "https://api.spotify.com/v1/artists"
    params = {"ids": ",".join(batch_ids)}
    headers = {"Authorization": f"Bearer {access_token}"}

    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        return response.json().get('artists', [])
    else:
        print(f"Error fetching artist info: {response.status_code}, {response.text}")
        return []

def create_spotify_table(data, cursor):
    for artist in data:
        artist_id = artist['id']
        name = artist['name']
        popularity = artist['popularity']
        genre = artist['genres'][0] if artist['genres'] else "Unknown"
        cursor.execute("SELECT 1 FROM Spotify_artists WHERE id = ?", (artist_id,))
        if cursor.fetchone():
            continue
        cursor.execute('''
            INSERT INTO Spotify_artists (id, name, popularity, genre)
            VALUES (?, ?, ?, ?)
        ''', (artist_id, name, popularity, genre))

# Functions related to TMDB API
def fetch_genres():
    response = requests.get(TMDB_GENRE_URL, headers=TMDB_API_HEADERS)
    if response.status_code == 200:
        genre_data = response.json().get("genres", [])
        return {genre["id"]: genre["name"] for genre in genre_data}
    else:
        print(f"Error fetching genres: {response.text}")
        return {}

def fetch_movie_data(movie_title):
    params = {"query": movie_title, "language": "en-US", "page": 1}
    response = requests.get(TMDB_SEARCH_URL, headers=TMDB_API_HEADERS, params=params)
    if response.status_code == 200:
        movie_data = response.json().get("results", [])
        return movie_data[0] if movie_data else None
    else:
        print(f"Error fetching movie data for '{movie_title}': {response.text}")
        return None

def insert_genres(cursor, genre_mapping):
    for genre_id, genre_name in genre_mapping.items():
        cursor.execute('INSERT OR IGNORE INTO genres (id, name) VALUES (?, ?)', (genre_id, genre_name))

def insert_movie_data(cursor, movie_data):
    if movie_data:
        title = movie_data.get("title")
        year = movie_data.get("release_date", "").split("-")[0]
        imdb_rating = movie_data.get("vote_average")
        cursor.execute('INSERT OR IGNORE INTO movies (title, year, imdb_rating) VALUES (?, ?, ?)', (title, year, imdb_rating))
        return cursor.lastrowid

def link_movie_genres(cursor, movie_id, genre_ids):
    if movie_id and genre_ids:
        for genre_id in genre_ids:
            cursor.execute('INSERT OR IGNORE INTO movie_genres (movie_id, genre_id) VALUES (?, ?)', (movie_id, genre_id))

# Initialize progress tracking
def initialize_progress(cursor):
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT UNIQUE,
            last_index INTEGER
        )
    ''')
    cursor.execute('''
        INSERT OR IGNORE INTO progress (category, last_index) VALUES 
        ('books', 0),
        ('artists', 0),
        ('movies', 0)
    ''')

def update_progress(cursor, category, index):
    cursor.execute('''
        UPDATE progress SET last_index = ? WHERE category = ?
    ''', (index, category))

def get_last_index(cursor, category):
    cursor.execute('''
        SELECT last_index FROM progress WHERE category = ?
    ''', (category,))
    result = cursor.fetchone()
    return result[0] if result else 0

# Main function to set up SQLite database and process data
def main():
    db_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), DATABASE_NAME)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create tables
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS books (
            book_unique_id TEXT PRIMARY KEY,
            title TEXT,
            published_date TEXT,
            average_rating REAL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS authors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS book_authors (
            book_unique_id TEXT,
            author_id INTEGER,
            FOREIGN KEY (book_unique_id) REFERENCES books(book_unique_id),
            FOREIGN KEY (author_id) REFERENCES authors(id),
            PRIMARY KEY (book_unique_id, author_id)
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS book_categories (
            book_unique_id TEXT,
            category_id INTEGER,
            FOREIGN KEY (book_unique_id) REFERENCES books(book_unique_id),
            FOREIGN KEY (category_id) REFERENCES categories(id),
            PRIMARY KEY (book_unique_id, category_id)
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Spotify_artists (
            id TEXT NOT NULL PRIMARY KEY,
            name TEXT NOT NULL,
            popularity INTEGER NOT NULL,
            genre TEXT NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS movies (
            id INTEGER PRIMARY KEY,
            title TEXT UNIQUE,
            year TEXT,
            imdb_rating TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS genres (
            id INTEGER PRIMARY KEY,
            name TEXT UNIQUE
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS movie_genres (
            movie_id INTEGER,
            genre_id INTEGER,
            PRIMARY KEY (movie_id, genre_id),
            FOREIGN KEY (movie_id) REFERENCES movies(id),
            FOREIGN KEY (genre_id) REFERENCES genres(id)
        )
    ''')

    # Initialize and fetch progress
    initialize_progress(cursor)
    total_books_processed = get_last_index(cursor, 'books')
    total_artists_processed = get_last_index(cursor, 'artists')
    total_movies_processed = get_last_index(cursor, 'movies')

    # Process book data in batches of 25, up to 100 entries in total
    if total_books_processed < 100:
        query = random.choice(BOOK_GENRES)  # Select a random genre
        books_to_fetch = min(25, 100 - total_books_processed)
        data = fetch_books(query, max_results=books_to_fetch, start_index=total_books_processed)
        if 'items' in data:
            store_book_data_in_db(data, cursor)
            total_books_processed += len(data['items'])
            update_progress(cursor, 'books', total_books_processed)
            conn.commit()
            print(f"Total books processed: {total_books_processed}")

    # Process Spotify artists data in batches of 25
    with open("100 artists - Sheet1.csv", "r") as file:
        reader = csv.reader(file)
        total_artists = list(reader)[1:]
    if total_artists_processed < len(total_artists):
        artists_to_fetch = min(25, len(total_artists) - total_artists_processed)
        artist_data = get_artist_info(SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, start_index=total_artists_processed, limit=artists_to_fetch)
        if artist_data:
            create_spotify_table(artist_data, cursor)
            total_artists_processed += len(artist_data)
            update_progress(cursor, 'artists', total_artists_processed)
            conn.commit()
            print(f"Total artists processed: {total_artists_processed}")

    # Process movie data in batches of 25
    insert_genres(cursor, fetch_genres())
    if total_movies_processed < len(MOVIE_TITLES):
        movies_to_fetch = min(25, len(MOVIE_TITLES) - total_movies_processed)
        batch = MOVIE_TITLES[total_movies_processed:total_movies_processed + movies_to_fetch]
        for movie_title in batch:
            movie_data = fetch_movie_data(movie_title)
            if movie_data:
                movie_id = insert_movie_data(cursor, movie_data)
                genre_ids = movie_data.get("genre_ids", [])
                link_movie_genres(cursor, movie_id, genre_ids)
        total_movies_processed += len(batch)
        update_progress(cursor, 'movies', total_movies_processed)
        conn.commit()
        print(f"Total movies processed: {total_movies_processed}")

    # Commit and close the connection
    conn.commit()
    conn.close()

if __name__ == '__main__':
    main()