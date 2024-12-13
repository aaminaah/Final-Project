import matplotlib.pyplot as plt
import pandas as pd
import sqlite3

# Constants
DATABASE_NAME = 'combined.db'

# Helper function to get data from CSVs
def read_csv_data(filename, usecols=None):
    df = pd.read_csv(filename, usecols=usecols)
    return df

# Function to visualize average rating of all books
def visualize_book_data():
    df = read_csv_data('book_calculations.csv', usecols=['Average Rating of All Books', 'Genre', 'Average Rating'])
    average_rating = df.iloc[0]['Average Rating of All Books']
    genres = df['Genre'][1:].dropna()
    avg_ratings = df['Average Rating'][1:].dropna()

    plt.barh(genres, avg_ratings)
    plt.xlabel('Average Rating')
    plt.title('Average Ratings of Books by Genre')
    plt.tight_layout()
    plt.show()

# Function to visualize average rating by genre
def average_rating_by_genre_graph():
    df = read_csv_data('book_calculations.csv', usecols=['Genre', 'Average Rating'])
    genres = df['Genre'][1:].dropna()
    avg_ratings = df['Average Rating'][1:].dropna()

    plt.barh(genres, avg_ratings)
    plt.xlabel('Average Rating')
    plt.title('Average Rating by Genre')
    plt.tight_layout()
    plt.show()

# Graph for average IMDb rating
def graph_imdb():
    df = read_csv_data('imdb_calculations.csv', usecols=['Description', 'Average Rating'])
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.bar(df['Description'], df['Average Rating'], color='pink')
    ax.set_title("Average IMDb Rating")
    ax.set_xlabel('Description')
    ax.set_ylabel('Average Rating')
    plt.tight_layout()
    plt.savefig('imdb_graph.png')
    print("Saved IMDb graph as 'imdb_graph.png'.")
    plt.show()

# Graph for average IMDb rating by genre
def genre_imdb():
    df = read_csv_data('genre_calculations.csv', usecols=['Genre', 'Average Rating'])
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.bar(df['Genre'], df['Average Rating'], color='blue')
    ax.set_title('Average IMDb Rating by Genre')
    ax.set_xlabel('Genre')
    ax.set_ylabel('Average Rating')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig('genre_graph.png')
    print("Saved Genre graph as 'genre_graph.png'.")
    plt.show()

# Graph for top song popularity
def plot_by_top_song(data):
    popularity = [row[2] for row in data[:5]]
    toptrack = [row[4] for row in data[:5]]

    plt.figure(figsize=(8, 5))
    plt.bar(toptrack, popularity, color='violet', width=0.5)
    plt.xlabel('Top track')
    plt.ylabel('Popularity')
    plt.title('Top Track by Artist Popularity')
    plt.tight_layout()
    plt.show()

# Graph for top artist popularity
def plot_by_top_artist(data):
    popularity = [row[2] for row in data[:10]]
    artist = [row[1] for row in data[:10]]

    plt.figure(figsize=(8, 5))
    plt.bar(artist, popularity, color='darkblue', width=0.5)
    plt.xlabel('Artist')
    plt.xticks(rotation=20)
    plt.ylabel('Popularity')
    plt.title('Artist by Popularity')
    plt.tight_layout()
    plt.show()

# Graph for top genre popularity
def plot_by_top_genre(data):
    popularity = [row[2] for row in data[:5]]
    genre = [row[3] for row in data[:5]]

    plt.figure(figsize=(8, 5))
    plt.bar(genre, popularity, color='orange', width=0.8)
    plt.xlabel('Genre')
    plt.ylabel('Popularity')
    plt.title('Genre by Artist Popularity')
    plt.tight_layout()
    plt.show()

# Main function to generate all graphs
def main_graphs():
    # Book data graphs
    visualize_book_data()
    average_rating_by_genre_graph()

    # IMDb data graphs
    graph_imdb()
    genre_imdb()

    # Spotify data graphs
    spotify_data = read_csv_data('spotify_data.csv').values
    plot_by_top_song(spotify_data)
    plot_by_top_artist(spotify_data)
    plot_by_top_genre(spotify_data)

if __name__ == "__main__":
    main_graphs()
