import os
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("RAWG_API_KEY")
BASE_URL = "https://api.rawg.io/api"

# Fetch top games of the year
def fetch_yearly_top_games(api_key=API_KEY, year=None, page_size=10):
    if year is None:
        year = datetime.today().year

    start_date = f"{year}-01-01"
    end_date = f"{year}-12-31"

    url = f"{BASE_URL}/games"
    params = {
        "key": api_key,
        "dates": f"{start_date},{end_date}",
        "ordering": "-added",   # You can change to "-rating" or "-metacritic"
        "page_size": page_size
    }

    response = requests.get(url, params=params)

    if response.status_code != 200:
        raise Exception(f"Error fetching data: {response.status_code}")

    data = response.json()
    games = []

    for game in data.get("results", []):
        games.append({
            "id": game.get("id"),
            "name": game.get("name"),
            "released": game.get("released"),
            "rating": game.get("rating"),
            "platforms": [p["platform"]["name"] for p in game.get("platforms", [])],
            "background_image": game.get("background_image"),
        })

    return games

# Function that fetch detailed info about a specific game.
def fetch_game_info(api_key=API_KEY, game_id=None):
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
        "background_image": data.get("background_image"),
        "website": data.get("website")
    }

# Function that search for games by title (20 items by default)
def search_games(api_key=API_KEY, query=None, page_size=20):
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
            "platforms": [p["platform"]["name"] for p in g.get("platforms", [])],
            "background_image": g.get("background_image")
        })
    return games

# Function that fetch list of available genres.
def fetch_genres(api_key=API_KEY):
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

# Function that fetch games from a specific genre.
def fetch_games_by_genre(api_key=API_KEY, genre_slug=None, page_size=10):
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
            "platforms": [p["platform"]["name"] for p in g.get("platforms", [])],
            "background_image": g.get("background_image")
        })
    return games

# Fetch screenshots for a specific game
def fetch_game_screenshots(api_key=API_KEY, game_id=None, page_size=10):
    url = f"{BASE_URL}/games/{game_id}/screenshots"
    params = {"key": api_key, "page_size": page_size}
    response = requests.get(url, params=params)

    if response.status_code != 200:
        raise Exception(f"Error fetching screenshots: {response.status_code}")

    data = response.json()
    screenshots = []
    for s in data.get("results", []):
        screenshots.append({
            "id": s.get("id"),
            "image": s.get("image")
        })

    return screenshots


# Example usage:
if __name__ == "__main__":
    '''
    top_games = fetch_yearly_top_games(api_key=API_KEY, year=2025)
    for idx, game in enumerate(top_games, start=1):
        print(f"{idx}. {game['name']} (Rating: {game['rating']})")
        print(f"   ID: {game['id']}")
        print(f"   Released: {game['released']}")
        print(f"   Image: {game['background_image']}")
    '''
    '''
    search_results = search_games(api_key=API_KEY, query="Elden Ring")
    for idx, game in enumerate(search_results, start=1):
        print(f"{idx}. {game['name']} (Rating: {game['rating']})")
        print(f"   Released: {game['released']}")
        print(f"   Image: {game['background_image']}")
    
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
    '''
    # 4. Get games from a specific genre
    action_games = fetch_games_by_genre(api_key=API_KEY, genre_slug="action")
    for idx, game in enumerate(action_games, start=1):
        print(f"{idx}. {game['name']} (Rating: {game['rating']}) {game['background_image']}")
    '''
    game_info = fetch_game_info(api_key=API_KEY, game_id=3498)  # Example: GTA V
    print(f"Title: {game_info['name']}")
    print(f"Released: {game_info['released']}")
    print(f"Rating: {game_info['rating']}")
    print(f"Developers: {', '.join(game_info['developers'])}")
    print(f"Genres: {', '.join(game_info['genres'])}")
    print(f"Description: {game_info['description']}...")
    print(game_info['background_image'])

    screenshots = fetch_game_screenshots(API_KEY, game_id=3498)
    for idx, shot in enumerate(screenshots, start=1):
        print(f"{idx}. Screenshot URL: {shot['image']}")
    '''

