import requests
import sqlite3
import os
import json

# TMDB API Configuration
TMDB_API_HEADERS = {
    "accept": "application/json",
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiJjNmNiYzg3YTUxNzY0YzEzODQ0NTE2OTg4ZDliNzMyZCIsIm5iZiI6MTczMzg1MzYwMS4wMDE5OTk5LCJzdWIiOiI2NzU4ODFhMDM2ODg0NTlkNzU4OWFmMjYiLCJzY29wZXMiOlsiYXBpX3JlYWQiXSwidmVyc2lvbiI6MX0.UDruEGkcZ3wC4F4tmApouiPAuVzqWLVRmxn2nYbhwpI"
}
TMDB_SEARCH_URL = "https://api.themoviedb.org/3/search/movie"
TMDB_GENRE_URL = "https://api.themoviedb.org/3/genre/movie/list?language=en"

# List of movie titles
movies = [
    "Barbie", "Home Alone", "3 Idiots", "Spy Kids", "Flipped", 
    "The Godfather", "The Shawshank Redemption", "Pulp Fiction", 
    "The Dark Knight", "Schindler's List", "Forrest Gump", 
    "The Lord of the Rings: The Return of the King", "Fight Club", 
    "Inception", "The Matrix", "The Silence of the Lambs", 
    "Star Wars: Episode V - The Empire Strikes Back", "Goodfellas", 
    "The Lord of the Rings: The Fellowship of the Ring", 
    "The Lord of the Rings: The Two Towers", "The Green Mile", 
    "The Godfather: Part II", "Se7en", "The Usual Suspects", 
    "The Lion King", "Gladiator", "Saving Private Ryan", 
    "The Departed", "The Prestige", "The Pianist", 
    "The Dark Knight Rises", "The Avengers", "Titanic", 
    "Jurassic Park", "The Terminator", "The Truman Show", 
    "Back to the Future", "Ghostbusters", "Shershaah", 
    "Good Will Hunting", "Braveheart", "The Shining", 
    "Psycho", "The Sixth Sense", "The Exorcist", 
    "A Clockwork Orange", "American History X", 
    "The Good, the Bad and the Ugly", "A Fistful of Dollars", 
    "For a Few Dollars More", "Unforgiven", "No Country for Old Men", 
    "Fargo", "The Big Lebowski", "O Brother, Where Art Thou?", 
    "True Grit", "The Revenant", 
    "Birdman or (The Unexpected Virtue of Ignorance)", 
    "The Grand Budapest Hotel", "Moonrise Kingdom", 
    "The Royal Tenenbaums", "Fantastic Mr. Fox", 
    "Isle of Dogs", "Reservoir Dogs", "Jackie Brown", 
    "Kill Bill: Vol. 1", "Kill Bill: Vol. 2", "Death Proof", 
    "Django Unchained", "The Hateful Eight", 
    "Once Upon a Time in Hollywood", "Spirited Away", 
    "My Neighbor Totoro", "Princess Mononoke", 
    "Howl's Moving Castle", "Ponyo", "Castle in the Sky", 
    "Kiki's Delivery Service", "Nausicaä of the Valley of the Wind", 
    "Porco Rosso", "Lagaan", "Dilwale Dulhania Le Jayenge", 
    "3 Idiots", "PK", "Gully Boy", "Queen", 
    "Taare Zameen Par", "Zindagi Na Milegi Dobara", "Dangal", 
    "Swades", "Rang De Basanti", "Barfi!", "Andhadhun", 
    "Mughal-E-Azam", "Chak De! India", "Kahaani", 
    "Dil Chahta Hai", "Gangs of Wasseypur", "Bajrangi Bhaijaan", 
    "Kabhi Khushi Kabhie Gham", "Vicky Donor", "Om Shanti Om", 
    "My Name Is Khan", "Devdas"
]

# Fetch and store genres
def fetch_genres():
    response = requests.get(TMDB_GENRE_URL, headers=TMDB_API_HEADERS)
    print(f"Genre fetch response status: {response.status_code}")  # Debugging output
    if response.status_code != 200:
        print(f"Error fetching genres: {response.text}")
        return {}
    genre_data = response.json().get("genres", [])
    return {genre["id"]: genre["name"] for genre in genre_data}

# Fetch movie data from TMDB
def fetch_movie_data(movie_title):
    params = {
        "query": movie_title,
        "language": "en-US",
        "page": 1
    }
    response = requests.get(TMDB_SEARCH_URL, headers=TMDB_API_HEADERS, params=params)
    print(f"Movie fetch response status for '{movie_title}': {response.status_code}")  # Debugging output
    if response.status_code != 200:
        print(f"Error fetching movie data for '{movie_title}': {response.text}")
        return None
    movie_data = response.json().get("results", [])
    return movie_data[0] if movie_data else None

# Insert genres into the database
def insert_genres(cursor, genre_mapping):
    for genre_id, genre_name in genre_mapping.items():
        cursor.execute('''INSERT OR IGNORE INTO genres (id, name) VALUES (?, ?)''', (genre_id, genre_name))

# Insert movie data into the database
def insert_movie_data(cursor, movie_data):
    if movie_data:
        title = movie_data.get("title")
        year = movie_data.get("release_date", "").split("-")[0]
        imdb_rating = movie_data.get("vote_average")
        
        cursor.execute('''INSERT OR IGNORE INTO movies (title, year, imdb_rating) VALUES (?, ?, ?)''', 
                       (title, year, imdb_rating))
        return cursor.lastrowid  # Return movie's row ID

def link_movie_genres(cursor, movie_id, genre_ids):
    if not movie_id or not genre_ids:
        return  # Skip if movie_id or genre_ids are invalid
    
    for genre_id in genre_ids:
        cursor.execute(
            '''INSERT OR IGNORE INTO movie_genres (movie_id, genre_id) VALUES (?, ?)''',
            (movie_id, genre_id)
        )

# Initialize SQLite database
def create_database():
    base_path = os.path.abspath(os.path.dirname(__file__))
    db_path = os.path.join(base_path, 'movies.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    # Create tables
    cursor.execute('''CREATE TABLE IF NOT EXISTS movies (
                      id INTEGER PRIMARY KEY,
                      title TEXT UNIQUE,
                      year TEXT,
                      imdb_rating TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS genres (
                      id INTEGER PRIMARY KEY,
                      name TEXT UNIQUE)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS movie_genres (
                      movie_id INTEGER,
                      genre_id INTEGER,
                      PRIMARY KEY (movie_id, genre_id),
                      FOREIGN KEY (movie_id) REFERENCES movies(id),
                      FOREIGN KEY (genre_id) REFERENCES genres(id))''')
    conn.commit()
    conn.close()

# Load last processed index from file
def load_last_index():
    try:
        with open('last_index.json', 'r') as file:
            return json.load(file).get('last_index', 0)
    except (FileNotFoundError, json.JSONDecodeError):
        return 0

# Save last processed index to file
def save_last_index(index):
    with open('last_index.json', 'w') as file:
        json.dump({'last_index': index}, file)

# Process a batch of movies
def process_movies(cursor, movie_titles):
    for movie_title in movie_titles:
        # Fetch movie data from the API
        print(f"Fetching data for movie: {movie_title}")
        movie_data = fetch_movie_data(movie_title)
        print(f"Fetched data for movie: {movie_title} - Data: {movie_data}")  # Debugging output
        
        # Insert movie data into the database
        try:
            movie_id = insert_movie_data(cursor, movie_data)
            print(f"Inserting movie: {movie_data.get('title')}")  # Debugging output
            genre_ids = movie_data.get("genre_ids", [])
            link_movie_genres(cursor, movie_id, genre_ids)
        except Exception as e:
            print(f"Error inserting movie '{movie_title}': {e}")

# Main function to execute the script
def main():
    import sqlite3

def main():
    create_database()
    conn = sqlite3.connect('movies.db')
    cursor = conn.cursor()
    
    # Fetch and insert genres
    genre_mapping = fetch_genres()
    insert_genres(cursor, genre_mapping)

    # Load the last processed index
    last_index = load_last_index()
    print(f"Last processed index: {last_index}")  # Debugging output

    # Get the total number of movies
    total_movies = len(movies)
    
    # Calculate the next index range to process
    next_index = last_index + 25  # Calculate the next index range
    if last_index < total_movies:  # Only process if there are more movies to process
        for i in range(last_index, min(next_index, total_movies)):  # Process up to 25 movies
            print(f"Processing movie: {movies[i]} (Index: {i})")
            process_movies(cursor, [movies[i]])  # Process one movie at a time
            conn.commit()  # Commit after each movie

        # Save the last processed index
        save_last_index(next_index)
        
        print(f"Processed up to index: {next_index}")  # Debugging output

    else:
        print("All movies have been processed already.")

    print("Run complete. Next run will continue from index:", next_index)

if __name__ == "__main__":
    main()
