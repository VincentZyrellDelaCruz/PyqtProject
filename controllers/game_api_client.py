import os
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("RAWG_API_KEY")
BASE_URL = "https://api.rawg.io/api"

# Fetch top games of the year
def fetch_yearly_top_games(api_key=API_KEY, year=None, page_size=10):
    # Default to current year if none provided
    if year is None:
        year = datetime.today().year

    start_date = f"{year}-01-01"
    end_date = f"{year}-12-31"

    url = "https://api.rawg.io/api/games"
    params = {
        "key": api_key,
        "dates": f"{start_date},{end_date}",
        "ordering": "-added",  # You can change to "-rating" or "-metacritic"
        "page_size": page_size
    }

    response = requests.get(url, params=params)

    if response.status_code != 200:
        raise Exception(f"Error fetching data: {response.status_code}")

    data = response.json()
    games = []

    for game in data.get("results", []):
        games.append({
            "name": game.get("name"),
            "released": game.get("released"),
            "rating": game.get("rating"),
            "platforms": [p["platform"]["name"] for p in game.get("platforms", [])]
        })

    return games

def fetch_game_info(api_key: str, game_id: int):
    """
    Fetch detailed info about a specific game.
    Returns a dictionary with consistent keys.
    """
    url = f"{BASE_URL}/games/{game_id}"
    params = {"key": api_key}
    response = requests.get(url, params=params)

    if response.status_code != 200:
        raise Exception(f"Error fetching game info: {response.status_code}")

    data = response.json()
    return {
        "name": data.get("name"),
        "released": data.get("released"),
        "description": data.get("description_raw"),
        "rating": data.get("rating"),
        "ratings_count": data.get("ratings_count"),
        "developers": [dev["name"] for dev in data.get("developers", [])],
        "genres": [genre["name"] for genre in data.get("genres", [])],
        "platforms": [p["name"] for p in data.get("platforms", [])] if data.get("platforms") else [],
        "background_image": data.get("background_image"),
        "website": data.get("website")
    }


def search_games(api_key: str, query: str, page_size: int = 10):
    """
    Search for games by title.
    Returns a list of dictionaries.
    """
    url = f"{BASE_URL}/games"
    params = {"key": api_key, "search": query, "page_size": page_size}
    response = requests.get(url, params=params)

    if response.status_code != 200:
        raise Exception(f"Error searching games: {response.status_code}")

    data = response.json()
    games = []
    for g in data.get("results", []):
        games.append({
            "id": g.get("id"),
            "name": g.get("name"),
            "released": g.get("released"),
            "rating": g.get("rating"),
            "platforms": [p["platform"]["name"] for p in g.get("platforms", [])]
        })
    return games


def fetch_genres(api_key: str):
    """
    Fetch list of available genres.
    Returns a list of dictionaries.
    """
    url = f"{BASE_URL}/genres"
    params = {"key": api_key}
    response = requests.get(url, params=params)

    if response.status_code != 200:
        raise Exception(f"Error fetching genres: {response.status_code}")

    data = response.json()
    genres = []
    for g in data.get("results", []):
        genres.append({
            "id": g.get("id"),
            "name": g.get("name"),
            "slug": g.get("slug"),
            "games_count": g.get("games_count")
        })
    return genres


def fetch_games_by_genre(api_key: str, genre_slug: str, page_size: int = 10):
    """
    Fetch games from a specific genre.
    Returns a list of dictionaries.
    """
    url = f"{BASE_URL}/games"
    params = {"key": api_key, "genres": genre_slug, "page_size": page_size}
    response = requests.get(url, params=params)

    if response.status_code != 200:
        raise Exception(f"Error fetching games by genre: {response.status_code}")

    data = response.json()
    games = []
    for g in data.get("results", []):
        games.append({
            "id": g.get("id"),
            "name": g.get("name"),
            "released": g.get("released"),
            "rating": g.get("rating"),
            "platforms": [p["platform"]["name"] for p in g.get("platforms", [])]
        })
    return games


# Example usage:
if __name__ == "__main__":
    '''
    top_games = fetch_yearly_top_games(year=2025)
    for idx, game in enumerate(top_games, start=1):
        print(f"{idx}. {game['name']} (Rating: {game['rating']})")

    info = fetch_game_info(API_KEY, game_id=3498)
    print(info)
    

    # 2. Search for games
    search_results = search_games(api_key=API_KEY, query="Elden Ring")
    for idx, game in enumerate(search_results, start=1):
        print(f"{idx}. {game['name']} (Released: {game['released']}, Rating: {game['rating']})")
    ''''''
    # 3. Get genre list
    genres = fetch_genres(api_key=API_KEY)
    for idx, genre in enumerate(genres, start=1):
        print(f"{idx}. {genre['name']} (Games Count: {genre['games_count']})")

    # 4. Get games from a specific genre
    action_games = fetch_games_by_genre(api_key=API_KEY, genre_slug="action")
    for idx, game in enumerate(action_games, start=1):
        print(f"{idx}. {game['name']} (Rating: {game['rating']})")
    '''


