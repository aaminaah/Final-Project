import sqlite3
import csv

def calculate_average_imdb_rating():
    # Connect to the database
    conn = sqlite3.connect('movies.db')
    c = conn.cursor()
    # Query to calculate the average IMDb rating across all movies
    c.execute("SELECT AVG(CAST(imdb_rating AS REAL)) FROM movies")
    average_rating = c.fetchone()[0]
    conn.close()
    return average_rating

def calculate_average_rating_by_genre():
    # Connect to the database
    conn = sqlite3.connect('movies.db')
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

def write_to_csv(data, filename, headers):
    # Write data to a CSV file
    with open(filename, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(headers)
        writer.writerows(data)

def main():
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

if __name__ == "__main__":
    main()
