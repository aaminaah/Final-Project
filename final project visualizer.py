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

def set_up_database(db_name):
    """
    Sets up a SQLite database connection and cursor.

    Parameters
    -----------------------
    db_name: str
        The name of the SQLite database.

    Returns
    -----------------------
    Tuple (Cursor, Connection):
        A tuple containing the database cursor and connection objects.
    """
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path + "/" + db_name)
    cur = conn.cursor()
    return cur, conn


#the most popular track per genre ranked by the most popular artist
#get the most popular artist in each genre
#join with the track table to get the most popular track associated with that genre

def join_two_tables(cur):
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
    
    with open("output.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(data)

    return data #data is not 100+ rows because multiple songs have the same first artist on them

def plot_by_top_song(data):
    popularity = []
    toptrack = []
    for row in data[:5]:
        popularity.append(row[2])
        toptrack.append(row[4])

    plt.figure(figsize=(8, 5))
    plt.bar(toptrack, popularity, color='violet', width=0.5)

    plt.xlabel('Top track')
    plt.ylabel('Popularity')
    plt.title('Top Track by Artist Popularity')
    # plt.ylim(0, 100) 

    plt.show()

def plot_by_top_artist(data):
    popularity = []
    artist = []
    for row in data[:10]:
        popularity.append(row[2])
        artist.append(row[1])

    plt.figure(figsize=(8, 5))
    plt.bar(artist, popularity, color='darkblue', width=0.5)

    plt.xlabel('Artist')
    plt.xticks(rotation=20)
    plt.ylabel('Popularity')
    plt.title('Artist by Popularity')
    # plt.ylim(0, 100) 

    plt.show()
    
def plot_by_top_genre(data):
    popularity = []
    genre = []
    for row in data[:5]:
        popularity.append(row[2])
        genre.append(row[3])

    plt.figure(figsize=(8, 5))
    plt.bar(genre, popularity, color='orange', width=0.8)

    plt.xlabel('Genre')
    plt.xticks(rotation=0)
    plt.ylabel('Popularity')
    plt.title('Genre by Artist Popularity')
    # plt.ylim(0, 100) 

    plt.show()

    
def select_data(num, cur):
    cur.execute("""
        SELECT DISTINCT genre FROM Spotify_artists
        SELECT TOP 20 popularity FROM Spotify_artists
        
                """)
    


def main():
    cur, conn = set_up_database("spotify_artists.db")
    plot_by_top_artist(join_two_tables(cur))
    plot_by_top_genre(join_two_tables(cur))
    plot_by_top_song(join_two_tables(cur))


if __name__ == "__main__":
    main()