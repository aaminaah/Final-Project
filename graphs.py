import matplotlib.pyplot as plt
import pandas as pd

# Graph for calculate_average_imdb_rating
def graph_imdb():
    # Strategy 1: Optimize CSV reading by specifying relevant columns
    df = pd.read_csv('imdb_calculations.csv', usecols=['Description', 'Average Rating'])

    # Strategy 4: Explicitly use figure and axes for plotting
    fig, ax = plt.subplots(figsize=(6, 4))  # Set a reasonable figure size
    ax.bar(df['Description'], df['Average Rating'], color='pink')
    ax.set_title("Average IMDb Rating")
    ax.set_xlabel('Description')
    ax.set_ylabel('Average Rating')

    plt.tight_layout()

    # Strategy 5: Save the graph as an image for reuse
    plt.savefig('imdb_graph.png')  # Save the graph as a PNG image
    print("Saved IMDb graph as 'imdb_graph.png'.")  # Inform the user

    plt.show()

# Graph for calculate_average_rating_by_genre
def genre_imdb():
    # Strategy 1: Optimize CSV reading by specifying relevant columns
    df = pd.read_csv('genre_calculations.csv', usecols=['Genre', 'Average Rating'])

    # Strategy 4: Explicitly use figure and axes for plotting
    fig, ax = plt.subplots(figsize=(8, 6))  # Set a reasonable figure size
    ax.bar(df['Genre'], df['Average Rating'], color='blue')
    ax.set_title('Average IMDb Rating by Genre')
    ax.set_xlabel('Genre')
    ax.set_ylabel('Average Rating')
    plt.xticks(rotation=45, ha='right')  # Adjust label rotation for better readability

    plt.tight_layout()

    # Strategy 5: Save the graph as an image for reuse
    plt.savefig('genre_graph.png')  # Save the graph as a PNG image
    print("Saved Genre graph as 'genre_graph.png'.")  # Inform the user

    plt.show()

def main():
    graph_imdb()
    genre_imdb()

if __name__ == "__main__":
    main()

