import matplotlib.pyplot as plt
import numpy as np
import json
import re
import csv
import requests
import sqlite3
import pprint
import os
from requests_oauthlib import OAuth1Session
import base64

# Define the database name as a constant
DB_NAME = "combined.db"

def set_up_database(DB_NAME):  # set up database to connect
    """
    Sets up a SQLite database connection and cursor.

    Returns
    -----------------------
    Tuple (Cursor, Connection):
        A tuple containing the database cursor and connection objects.
    """
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(os.path.join(path, DB_NAME))
    cur = conn.cursor()
    return cur, conn

def list_tables():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = c.fetchall()
    conn.close()
    return tables

print(list_tables())

### SPOTIFY calculation

def join_two_tables(cur):  # spotify table join
    cur.execute("""
        SELECT Spotify_artists.id, Spotify_artists.name, Spotify_artists.popularity, Spotify_artists.genre, Top_tracks.top_track
                FROM Spotify_artists 
                JOIN Top_tracks ON Spotify_artists.id = Top_tracks.id
                GROUP BY Spotify_artists.genre
                ORDER BY Spotify_artists.popularity DESC
                """,)
    data = []
    for row in cur:
        data.append(row)

    return data  # data is not 100+ rows because multiple songs have the same first artist on them

### IMDB calculations

def calculate_average_imdb_rating():
    # Connect to the database
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    # Query to calculate the average IMDb rating across all movies
    c.execute("SELECT AVG(CAST(imdb_rating AS REAL)) FROM movies")
    average_rating = c.fetchone()[0]
    conn.close()
    return average_rating

def calculate_average_rating_by_genre():
    # Connect to the database
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    # Query to calculate the average IMDb rating grouped by genre
    c.execute("""
        SELECT g.name AS genre, AVG(CAST(m.imdb_rating AS REAL)) AS average_rating
        FROM movies m
        JOIN movie_genres mg ON m.id = mg.movie_id
        JOIN genres g ON mg.genre_id = g.id
        GROUP BY g.name
        ORDER BY average_rating DESC
    """)
    average_rating_by_genre = c.fetchall()
    conn.close()
    return average_rating_by_genre

### BOOKS calculations 

# Function to calculate average ratings
def calculate_average_ratings():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    query = 'SELECT AVG(average_rating) FROM books WHERE average_rating IS NOT NULL;'
    c.execute(query)
    average_rating = c.fetchone()[0]
    conn.close()
    return average_rating

# Function to calculate average ratings by genre
def average_rating_by_genre():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    query = '''
        SELECT categories.name, AVG(books.average_rating) 
        FROM categories
        JOIN book_categories ON categories.id = book_categories.category_id
        JOIN books ON books.book_unique_id = book_categories.book_unique_id
        WHERE books.average_rating IS NOT NULL
        GROUP BY categories.name;
    '''
    c.execute(query)
    results = c.fetchall()
    conn.close()

    genres = [result[0] for result in results]
    avg_ratings = [result[1] for result in results]
    return genres, avg_ratings

# Function to write calculations to a CSV file
def write_to_bookcsv(genres, avg_ratings, average_rating):
    with open('book_calculations.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Average Rating of All Books", average_rating])
        writer.writerow(["Genre", "Average Rating"])
        for genre, avg_rating in zip(genres, avg_ratings):
            writer.writerow([genre, avg_rating])

# Main function for calculations
def main_calculations():
    average_rating = calculate_average_ratings()
    genres, avg_ratings = average_rating_by_genre()
    write_to_bookcsv(genres, avg_ratings, average_rating)  # this is for just the google books part

### format Spotify, IMDB CSV will be written in

def write_to_csv(data, filename, headers):
    # Write data to a CSV file
    with open(filename, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(headers)
        writer.writerows(data)

       


def main():

    cur, conn = set_up_database("combined.db")

    # Calculate average IMDb rating
    average_imdb_rating = calculate_average_imdb_rating()
    print(f"Average IMDb Rating: {average_imdb_rating:.2f}")

    # Write average IMDb rating to a CSV file
    write_to_csv(
        [(f"Average IMDb Rating", f"{average_imdb_rating:.2f}")],
        'imdb_calculations.csv',
        ['Description', 'Average Rating']
    )

    # Calculate average IMDb rating by genre
    average_rating_by_genre = calculate_average_rating_by_genre()
    print("Average IMDb Rating by Genre:")
    for genre, average_rating in average_rating_by_genre:
        print(f"{genre}: {average_rating:.2f}")

    # Write genre-based calculations to a CSV file
    write_to_csv(
        average_rating_by_genre,
        'genre_calculations.csv',
        ['Genre', 'Average Rating']
    )

    # Join two tables and write to CSV for spotify
    data = join_two_tables(cur)
    write_to_csv(
        data,
        'spotify_data.csv',
        ['id', 'name', 'popularity', 'genre', 'top_track']
    )



if __name__ == "__main__":
    main_calculations()
    main()
