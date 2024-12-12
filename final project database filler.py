import matplotlib.pyplot as plt
import json
import re
import csv
import requests
import sqlite3
import pprint
import os
from requests_oauthlib import OAuth1Session
import base64

# Your Spotify credentials
CLIENT_ID = "8ef7803a77064d34bb353919da745f09"
CLIENT_SECRET = "bb633203692a41e5b9cda1a1f1f81877"

# Spotify token URL
TOKEN_URL = "https://accounts.spotify.com/api/token"
  
    
### Request access token
def get_spotify_access_token(client_id, client_secret):
    # Encode client ID and secret into Base64
    client_credentials = f"{client_id}:{client_secret}"
    encoded_credentials = base64.b64encode(client_credentials.encode()).decode()

    # Set up headers and body for the POST request
    headers = {
        "Authorization": f"Basic {encoded_credentials}",
        "Content-Type": "application/x-www-form-urlencoded",
    }
    data = {
        "grant_type": "client_credentials"
    }

    # Make the POST request
    response = requests.post(TOKEN_URL, headers=headers, data=data)

    # Check for successful response
    if response.status_code == 200:
        return response.json().get("access_token")
        
    else:
        print(f"Failed to retrieve token. Status code: {response.status_code}")
        print(f"Response: {response.json()}")
        return None
    

# get several artists info using artist ids (100, 25 at a time?)

## iterate through file to get str of artist ids
## I couldn't find a way to program getting artist IDs so I found 100 by hand to use as input for the API.

def get_artist_info(client_id, client_secret, start_index):
    #get access token in here
    access_token = get_spotify_access_token(client_id, client_secret)
    if not access_token:
        print('u got get_artist_info wrong..')
        return
    
    batch = 25
    #actual artist info finder
    with open("100 artists - Sheet1.csv", "r") as file:
        reader = csv.reader(file)
        next(reader) #skip empty head
        artist_ids = [row[0] for row in reader]

        #get the batch of artist ids
        batch_ids = artist_ids[start_index:start_index + batch]
        if not batch_ids:
            print("No more artist IDs to process.")
            return []

### ACTUAL CODE ###
# ask API for stuff
    url = "https://api.spotify.com/v1/artists"
    params = {"ids": ",".join(batch_ids)}
    headers = {"Authorization": f"Bearer {access_token}"}

    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        returndict = response.json().get('artists', 000)
        return returndict  #return dict
    else:
        print(f"error in get_artist_info: {response.status_code}")
        print(response.text)
        return None

### TEST CODE ###

    # params = {"ids": '4YRxDV8wJFPHPTeXepOstw,06HL4z0CvFAxyc27GXpf02,6eUKZXaKkcviH0Ku9w2n3V'}
    # response = requests.get(url, headers=headers, params=params)

    # if response.status_code == 200:
    #     returndict = response.json() #gives me dict
    #     # json_string = json.dumps(returndict) #gives me json
    #     return returndict
    #     # print(json_string)  # print artist information!!
    # else:
    #     print(f"Error: {response.status_code}")
    #     print(response.text)

    # for artist in returndict['artists']:
    #     popularity = artist['popularity']
    #     genre = artist['genres'][0]
    #     name = artist['name']
    #     print('WHAT AM IMEANT TO DO NOW')
    #     pass
    ### trash code ###
        # #use 2 lists of len 50 because the max number of IDs I can input to API at once is 50
        # counter = 0
        # outvalue1 = []
        # outvalue2 = []

        # for row in reader:
        #     if counter < 50:
        #         outvalue1.append(row[0])  # First 50 rows
        #     else:
        #         outvalue2.append(row[0])  # Last 50 rows
        #     counter += 1

        # # Join rows into comma-separated strings
        # # print(len(outvalue1))
        # # print(len(outvalue2))
        # result1 = ",".join(outvalue1)
        # result2 = ",".join(outvalue2)

        # # print(result1)
        # # print(result2)

    # url = "https://api.spotify.com/v1/artists"
    # params = {
    #     "ids": "4YRxDV8wJFPHPTeXepOstw,06HL4z0CvFAxyc27GXpf02,6eUKZXaKkcviH0Ku9w2n3V,0du5cEVh5yTK9QJze8zA0C,1Xyo4u8uXC1ZmMpatF05PJ"
    # }
    # headers = {
    #     "Authorization": f"Bearer {access_token}"
    # }
        # for result in [result1, result2]:
        # if not result:
        #     continue  # skip if no ids
        # params = {"ids": result}
        # response = requests.get(url, headers=headers, params=params)
        # # Check the response
        # if response.status_code == 200:
        #     returndict = response.json()
        #     return returndict
        # else:
        #     print(f"Error: {response.status_code}")
        #     print(response.text)

# put artist popularity, and first artist genre in list of genres in db

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

def create_spotify_table(data, cur, conn, limit=25): #sets limit variable number right in func def
    cur.execute("""
    CREATE TABLE IF NOT EXISTS Spotify_artists (
        id TEXT NOT NULL PRIMARY KEY,
        name TEXT NOT NULL,
        popularity INTEGER NOT NULL,
        genre TEXT NOT NULL
    )
    """)
    counter = 0  #to count num entries
    for artist in data:
        if counter >= limit: #checks if 25 entry limit is reached, stops if is
            break  

        #extract artist details
        id = artist['id']
        name = artist['name']
        popularity = artist['popularity']
        genre = artist['genres'][0] if artist['genres'] else "Unknown" #checks if artist has genre

        #see if artist exists
        cur.execute("SELECT 1 FROM Spotify_artists WHERE id = ?", (id,))
        if cur.fetchone():
            # skips existing artist
            continue

        #insert new artist
        try:
            cur.execute("""
                INSERT INTO Spotify_artists (id, name, popularity, genre)
                VALUES (?, ?, ?, ?)
            """, (id, name, popularity, genre))
            counter += 1  #count +1 for new entries
        except sqlite3.Error as err:
            print(f"Failed to insert {name}: {err}")

    conn.commit()
    print('did stuff in the db')

def get_toptrack_info(client_id, client_secret, start_index):
        #get access token in here
    access_token = get_spotify_access_token(client_id, client_secret)
    if not access_token:
        print('u got get_toptrack_info wrong..')
        return
    
    batch = 25
    #actual artist info finder
    with open("100 artists - Sheet1.csv", "r") as file:
        reader = csv.reader(file)
        next(reader) #skip empty head
        artist_ids = [row[0] for row in reader]
        # print(artist_ids)

        #get the batch of artist ids
        batch_ids = artist_ids[start_index:start_index + batch]
        # print(batch_ids)
        if not batch_ids:
            print("No more artist IDs to process.")
            return []
        
    # ask API for stuff
    params = {"ids": ",".join(batch_ids)}
    headers = {"Authorization": f"Bearer {access_token}"}

    tracksdictlist = []
    for artist_id in batch_ids:
        # print(artist_id)
        url = "https://api.spotify.com/v1/artists/"+artist_id+"/top-tracks"

        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            tracksdict = response.json().get("tracks", [])
            tracksdictlist.append(tracksdict)
            # print(tracksdict)
        else:
            print(f"error in get_toptrack_info: {response.status_code}")
            print(response.text)
            return None
    return tracksdictlist

def create_toptrack_table(data, cur, conn, limit=25):
    cur.execute("""
    CREATE TABLE IF NOT EXISTS Top_tracks (
    id TEXT NOT NULL PRIMARY KEY,
    top_track TEXT NOT NULL    
    )""")
    # print(data)
    counter = 0  #to count num entries
    print("Going through " + str(len(data)) + " entries in data")
    for tracks in data:
        # print(tracks)
        tracks = tracks[0]
        if counter >= limit: #checks if 25 entry limit is reached, stops if is
            print("Limit reached")
            break  
        #artist toptrack details
        
        # id = tracks['artists'][0]['id']
        id = 0
        for artist in tracks['artists']:
            artist_id = artist['id']
            cur.execute("SELECT 1 FROM Spotify_artists WHERE id = ?", (artist_id,)) #checks if artist id here is in spotify_artists
            if cur.fetchone():
                id = artist_id #sets id to this val
            else:
                continue
        
        toptrack = tracks['name']

        id = id.encode('utf-8').decode('utf-8')
        toptrack = toptrack.encode('utf-8').decode('utf-8')
        # print(id)
        # print(toptrack)

        #see if artist id exists
        cur.execute("SELECT 1 FROM Top_tracks WHERE id = ?", (id,))
        if cur.fetchone():
            # skips existing artist
            print('skipping '+id)
            continue

        #insert new track
        try:
            print("inserting " + toptrack)
            cur.execute("""
                INSERT INTO Top_tracks (id, top_track)
                VALUES (?, ?)
            """, (id, toptrack))
            counter += 1  #count +1 for new entries
        except BaseException as e :
            print("Failed to insert " + str(e) + str(id))

        #had to skip one song because there's an emoji in the title

    conn.commit()
    print('did stuff in the NEW db table')

    pass
    
def initialize_tracker_table(cur, conn):
    cur.execute("""
    CREATE TABLE IF NOT EXISTS Progress (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        last_processed_index INTEGER
    )
    """)
    #insert initial tracker if it doesn't exist
    cur.execute("SELECT COUNT(*) FROM Progress")
    if cur.fetchone()[0] == 0:
        cur.execute("INSERT INTO Progress (last_processed_index) VALUES (0)")
    conn.commit()


def main():
    cur, conn = set_up_database("spotify_artists.db")
    initialize_tracker_table(cur, conn)
    
    cur.execute("SELECT last_processed_index FROM Progress")
    start_index = cur.fetchone()[0]

    artist_data = get_artist_info(CLIENT_ID, CLIENT_SECRET, start_index)
    if artist_data:
        create_spotify_table(artist_data, cur, conn, limit=25)

        #update progress tracker
        cur.execute("UPDATE Progress SET last_processed_index = ?", (start_index + 25,))
        conn.commit()
    else:
        print("nothing received..")

    track_data = get_toptrack_info(CLIENT_ID, CLIENT_SECRET, start_index)
    if track_data:
        create_toptrack_table(track_data, cur, conn, limit=25)

        #update progress tracker
        cur.execute("UPDATE Progress SET last_processed_index = ?", (start_index + 25,))
        conn.commit()
    else:
        print("nothing received..")

    conn.close()


if __name__ == "__main__":
    main()
    