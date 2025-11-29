import os
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("RAWG_API_KEY")
BASE_URL = "https://api.rawg.io/api"

# Static data for when API is not available
STATIC_TOP_GAMES = [
    {"id": 3498, "name": "Grand Theft Auto V", "released": "2013-09-17", "rating": 4.47, "platforms": ["PC", "PlayStation 5", "PlayStation 4", "Xbox Series S/X"], "background_image": "https://media.rawg.io/media/games/20a/20aa03a10cda45239fe22d035c0ebe64.jpg"},
    {"id": 3328, "name": "The Witcher 3: Wild Hunt", "released": "2015-05-18", "rating": 4.66, "platforms": ["PC", "PlayStation 5", "PlayStation 4", "Xbox One"], "background_image": "https://media.rawg.io/media/games/618/618c2031a07bbff6b4f611f10b6bcdbc.jpg"},
    {"id": 4200, "name": "Portal 2", "released": "2011-04-18", "rating": 4.61, "platforms": ["PC", "Xbox 360", "PlayStation 3"], "background_image": "https://media.rawg.io/media/games/2ba/2bac0e87cf45e5b508f227d281c9252a.jpg"},
    {"id": 5286, "name": "Tomb Raider (2013)", "released": "2013-03-05", "rating": 4.05, "platforms": ["PC", "PlayStation 4", "Xbox One"], "background_image": "https://media.rawg.io/media/games/021/021c4e21a1824d2526f925eff6324653.jpg"},
    {"id": 13537, "name": "Half-Life 2", "released": "2004-11-16", "rating": 4.49, "platforms": ["PC", "Xbox 360", "PlayStation 3"], "background_image": "https://media.rawg.io/media/games/b8c/b8c243eaa0fbac8115e0cdccac3f91dc.jpg"},
    {"id": 12020, "name": "Left 4 Dead 2", "released": "2009-11-17", "rating": 4.09, "platforms": ["PC", "Xbox 360"], "background_image": "https://media.rawg.io/media/games/d58/d588947d4286e7b5e0e12e1bea7d9844.jpg"},
    {"id": 5679, "name": "The Elder Scrolls V: Skyrim", "released": "2011-11-11", "rating": 4.42, "platforms": ["PC", "PlayStation 5", "PlayStation 4", "Xbox Series S/X"], "background_image": "https://media.rawg.io/media/games/7cf/7cfc9220b401b7a300e409e539c9afd5.jpg"},
    {"id": 28, "name": "Red Dead Redemption 2", "released": "2018-10-26", "rating": 4.59, "platforms": ["PC", "PlayStation 4", "Xbox One"], "background_image": "https://media.rawg.io/media/games/511/5118aff5091cb3efec399c808f8c598f.jpg"},
    {"id": 58175, "name": "God of War", "released": "2018-04-20", "rating": 4.57, "platforms": ["PC", "PlayStation 4"], "background_image": "https://media.rawg.io/media/games/4be/4be6a6ad0364751a96229c56bf69be59.jpg"},
    {"id": 802, "name": "Borderlands 2", "released": "2012-09-18", "rating": 4.01, "platforms": ["PC", "PlayStation 4", "Xbox One"], "background_image": "https://media.rawg.io/media/games/49c/49c3dfa4ce2f6f140cc4825868e858cb.jpg"},
]

# Fetch top games of the year
def fetch_yearly_top_games(api_key=API_KEY, year=None, page_size=10):
    # Return static data if no API key
    if not api_key or api_key == "your_api_key_here":
        return STATIC_TOP_GAMES[:page_size]
    
    if year is None:
        year = datetime.today().year

    start_date = f"{year}-01-01"
    end_date = f"{year}-12-31"

    url = f"{BASE_URL}/games"
    params = {
        "key": api_key,
        "dates": f"{start_date},{end_date}",
        "ordering": "-added",
        "page_size": page_size
    }

    try:
        response = requests.get(url, params=params)
        
        if response.status_code != 200:
            print(f"API error {response.status_code}, using static data")
            return STATIC_TOP_GAMES[:page_size]

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
    except Exception as e:
        print(f"Error fetching games: {e}, using static data")
        return STATIC_TOP_GAMES[:page_size]

# Function that fetch detailed info about a specific game.
def fetch_game_info(api_key=API_KEY, game_id=None):
    # Return static data if no API key
    if not api_key or api_key == "your_api_key_here":
        return {
            "name": "Grand Theft Auto V",
            "released": "2013-09-17",
            "description": "Grand Theft Auto V is an action-adventure game played from either a third-person or first-person perspective.",
            "rating": 4.47,
            "ratings_count": 6500,
            "developers": ["Rockstar North"],
            "genres": ["Action", "Adventure"],
            "background_image": "https://media.rawg.io/media/games/20a/20aa03a10cda45239fe22d035c0ebe64.jpg",
            "website": "http://www.rockstargames.com/V/"
        }
    
    url = f"{BASE_URL}/games/{game_id}"
    params = {"key": api_key}
    
    try:
        response = requests.get(url, params=params)

        if response.status_code != 200:
            print(f"API error {response.status_code}, using static data")
            return {
                "name": "Game Info Unavailable",
                "released": "N/A",
                "description": "API key required for game details",
                "rating": 0,
                "ratings_count": 0,
                "developers": [],
                "genres": [],
                "background_image": "",
                "website": ""
            }

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
    except Exception as e:
        print(f"Error fetching game info: {e}")
        return {
            "name": "Error Loading Game",
            "released": "N/A",
            "description": "Could not load game information",
            "rating": 0,
            "ratings_count": 0,
            "developers": [],
            "genres": [],
            "background_image": "",
            "website": ""
        }

# Function that search for games by title (20 items by default)
def search_games(api_key=API_KEY, query=None, page_size=20):
    # Return filtered static data if no API key
    if not api_key or api_key == "your_api_key_here":
        if query:
            filtered = [g for g in STATIC_TOP_GAMES if query.lower() in g["name"].lower()]
            return filtered[:page_size]
        return STATIC_TOP_GAMES[:page_size]
    
    url = f"{BASE_URL}/games"
    params = {"key": api_key, "search": query, "page_size": page_size}
    
    try:
        response = requests.get(url, params=params)

        if response.status_code != 200:
            print(f"API error {response.status_code}, using static data")
            if query:
                filtered = [g for g in STATIC_TOP_GAMES if query.lower() in g["name"].lower()]
                return filtered[:page_size]
            return STATIC_TOP_GAMES[:page_size]

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
    except Exception as e:
        print(f"Error searching games: {e}, using static data")
        if query:
            filtered = [g for g in STATIC_TOP_GAMES if query.lower() in g["name"].lower()]
            return filtered[:page_size]
        return STATIC_TOP_GAMES[:page_size]

# Function that fetch list of available genres.
def fetch_genres(api_key=API_KEY):
    # This is not used anymore since we have static genres in game_genre_screen.py
    # But keeping for compatibility
    return []

# Function that fetch games from a specific genre.
def fetch_games_by_genre(api_key=API_KEY, genre_slug=None, page_size=10):
    # Return static data if no API key
    if not api_key or api_key == "your_api_key_here":
        return STATIC_TOP_GAMES[:page_size]
    
    url = f"{BASE_URL}/games"
    params = {"key": api_key, "genres": genre_slug, "page_size": page_size}
    
    try:
        response = requests.get(url, params=params)

        if response.status_code != 200:
            print(f"API error {response.status_code}, using static data")
            return STATIC_TOP_GAMES[:page_size]

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
    except Exception as e:
        print(f"Error fetching games by genre: {e}, using static data")
        return STATIC_TOP_GAMES[:page_size]

# Fetch screenshots for a specific game
def fetch_game_screenshots(api_key=API_KEY, game_id=None, page_size=10):
    # Return empty if no API key
    if not api_key or api_key == "your_api_key_here":
        return []
    
    url = f"{BASE_URL}/games/{game_id}/screenshots"
    params = {"key": api_key, "page_size": page_size}
    
    try:
        response = requests.get(url, params=params)

        if response.status_code != 200:
            print(f"API error {response.status_code}, no screenshots available")
            return []

        data = response.json()
        screenshots = []
        for s in data.get("results", []):
            screenshots.append({
                "id": s.get("id"),
                "image": s.get("image")
            })

        return screenshots
    except Exception as e:
        print(f"Error fetching screenshots: {e}")
        return []


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

