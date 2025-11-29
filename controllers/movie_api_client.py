import os
from datetime import datetime
from PyQt6.QtCore import QObject, pyqtSignal, QRunnable, QThreadPool, QMutex, QMutexLocker
from functools import lru_cache
import requests
import time
from collections import deque
import config

# Use configuration from config.py
TMDB_API_KEY = config.TMDB_API_KEY
BASE_URL = config.TMDB_BASE_URL
IMAGE_BASE_URL = config.TMDB_IMAGE_BASE_URL

# Rate limiting configuration
class RateLimiter:
    """Rate limiter to prevent too many requests per second."""
    def __init__(self, max_requests_per_second=10):
        self.max_requests = max_requests_per_second
        self.request_times = deque()
        self.mutex = QMutex()
    
    def wait_if_needed(self):
        """Wait if rate limit would be exceeded."""
        with QMutexLocker(self.mutex):
            now = time.time()
            
            # Remove timestamps older than 1 second
            while self.request_times and now - self.request_times[0] > 1.0:
                self.request_times.popleft()
            
            # If we've hit the limit, wait
            if len(self.request_times) >= self.max_requests:
                sleep_time = 1.0 - (now - self.request_times[0])
                if sleep_time > 0:
                    time.sleep(sleep_time)
                    # Clean up old timestamps again
                    now = time.time()
                    while self.request_times and now - self.request_times[0] > 1.0:
                        self.request_times.popleft()
            
            # Record this request
            self.request_times.append(time.time())

# Global rate limiter instance
_rate_limiter = RateLimiter(max_requests_per_second=config.TMDB_MAX_REQUESTS_PER_SECOND)

# Cache for API responses (5 minutes TTL simulated via LRU cache)
@lru_cache(maxsize=100)
def _cached_api_request(url: str, params_str: str):
    """Cached API request to avoid redundant calls with rate limiting."""
    import json
    params = json.loads(params_str)
    
    # Apply rate limiting
    _rate_limiter.wait_if_needed()
    
    try:
        response = requests.get(url, params=params, timeout=config.TMDB_REQUEST_TIMEOUT)
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 429:  # Too Many Requests
            print("Rate limit hit, waiting 2 seconds...")
            time.sleep(2)
            # Retry once
            response = requests.get(url, params=params, timeout=config.TMDB_REQUEST_TIMEOUT)
            if response.status_code == 200:
                return response.json()
    except requests.exceptions.Timeout:
        print(f"Request timeout for {url}")
    except requests.exceptions.ConnectionError:
        print(f"Connection error for {url}")
    except Exception as e:
        print(f"API request error: {e}")
    return None

# Static data for fallback
STATIC_POPULAR_MOVIES = [
    {"id": 278, "title": "The Shawshank Redemption", "release_date": "1994-09-23", "vote_average": 8.7, "poster_path": "/q6y0Go1tsGEsmtFryDOJo3dEmqu.jpg", "backdrop_path": "/kXfqcdQKsToO0OUXHcrrNCHDBzO.jpg", "overview": "Framed in the 1940s for the double murder of his wife and her lover, upstanding banker Andy Dufresne begins a new life at the Shawshank prison."},
    {"id": 238, "title": "The Godfather", "release_date": "1972-03-14", "vote_average": 8.7, "poster_path": "/3bhkrj58Vtu7enYsRolD1fZdja1.jpg", "backdrop_path": "/tmU7GeKVybMWFButWEGl2M4GeiP.jpg", "overview": "Spanning the years 1945 to 1955, a chronicle of the fictional Italian-American Corleone crime family."},
    {"id": 240, "title": "The Godfather Part II", "release_date": "1974-12-20", "vote_average": 8.6, "poster_path": "/hek3koDUyRQk7FIhPXsa6mT2Zc3.jpg", "backdrop_path": "/kGzFbGhp99zva6oZODW5atUtnqi.jpg", "overview": "In the continuing saga of the Corleone crime family, a young Vito Corleone grows up in Sicily and in 1910s New York."},
    {"id": 424, "title": "Schindler's List", "release_date": "1993-12-01", "vote_average": 8.6, "poster_path": "/sF1U4EUQS8YHUYjNl3pMGNIQyr0.jpg", "backdrop_path": "/yFuKvT4Vm3sKHdFY4eG6I4ldAnn.jpg", "overview": "The true story of how businessman Oskar Schindler saved over a thousand Jewish lives from the Nazis."},
    {"id": 19404, "title": "Dilwale Dulhania Le Jayenge", "release_date": "1995-10-20", "vote_average": 8.7, "poster_path": "/lfRkUr7DYdHldAqi3PwdQGBRBPM.jpg", "backdrop_path": "/7TavIAeH0TwXC1feYd7LbE8K3QA.jpg", "overview": "Raj is a rich, carefree, happy-go-lucky second generation NRI. Simran is the daughter of Chaudhary Baldev Singh, who in spite of being an NRI is very strict about adherence to Indian values."},
    {"id": 389, "title": "12 Angry Men", "release_date": "1957-04-10", "vote_average": 8.5, "poster_path": "/ow3wq89wM8qd5X7hWKxiRfsFf9C.jpg", "backdrop_path": "/qqHQsStV6exghCM7zbObuYBiYxw.jpg", "overview": "The defense and the prosecution have rested and the jury is filing into the jury room to decide if a young Spanish-American is guilty or innocent of murdering his father."},
    {"id": 155, "title": "The Dark Knight", "release_date": "2008-07-16", "vote_average": 8.5, "poster_path": "/qJ2tW6WMUDux911r6m7haRef0WH.jpg", "backdrop_path": "/hkBaDkMWbLaf8B1lsWsKX7Ew3Xq.jpg", "overview": "Batman raises the stakes in his war on crime with the help of Lt. Jim Gordon and District Attorney Harvey Dent."},
    {"id": 497, "title": "The Green Mile", "release_date": "1999-12-10", "vote_average": 8.5, "poster_path": "/8VG8fDNiy50H4FedGwdSVUPoaJe.jpg", "backdrop_path": "/l6hQWH9eDksNJNiXWYRkWqikOdu.jpg", "overview": "A supernatural tale set on death row in a Southern prison, where gentle giant John Coffey possesses the mysterious power to heal people's ailments."},
    {"id": 680, "title": "Pulp Fiction", "release_date": "1994-09-10", "vote_average": 8.5, "poster_path": "/d5iIlFn5s0ImszYzBPb8JPIfbXD.jpg", "backdrop_path": "/suaEOtk1N1sgg2MTM7oZd2cfVp3.jpg", "overview": "A burger-loving hit man, his philosophical partner, a drug-addled gangster's moll and a washed-up boxer converge in this sprawling, comedic crime caper."},
    {"id": 13, "title": "Forrest Gump", "release_date": "1994-07-06", "vote_average": 8.5, "poster_path": "/arw2vcBveWOVZr6pxd9XTd1TdQa.jpg", "backdrop_path": "/7c9UVPPiTPltouxRVY6N9uUaHDa.jpg", "overview": "A man with a low IQ has accomplished great things in his life and been present during significant historic events."},
]

STATIC_TV_SHOWS = [
    {"id": 1396, "name": "Breaking Bad", "first_air_date": "2008-01-20", "vote_average": 8.9, "poster_path": "/3xnWaLQjelJDDF7LT1WBo6f4BRe.jpg", "backdrop_path": "/tsRy63Mu5cu8etL1X7ZLyf7UP1M.jpg", "overview": "A high school chemistry teacher diagnosed with terminal lung cancer teams up with a former student to manufacture and sell methamphetamine."},
    {"id": 94605, "name": "Arcane", "first_air_date": "2021-11-06", "vote_average": 8.7, "poster_path": "/fqldf2t8ztc9aiwn3k6mlX3tvRT.jpg", "backdrop_path": "/fKs2gmXI5rNwg4m81eWZp8XQmKH.jpg", "overview": "Set in utopian Piltover and the oppressed underground of Zaun, the story follows the origins of two iconic League champions."},
    {"id": 60625, "name": "Rick and Morty", "first_air_date": "2013-12-02", "vote_average": 8.7, "poster_path": "/gdIrmf2DdY5mgN6ycVP0XlzKzbE.jpg", "backdrop_path": "/eV3XnUul4UfIivz3kxgeIozeo50.jpg", "overview": "A genius scientist and his not-so-bright grandson engage in interdimensional adventures."},
    {"id": 1399, "name": "Game of Thrones", "first_air_date": "2011-04-17", "vote_average": 8.4, "poster_path": "/1XS1oqL89opfnbLl8WnZY1O1uJx.jpg", "backdrop_path": "/2OMB0ynKlyIenMJWI2Dy9IWT4c.jpg", "overview": "Seven noble families fight for control of the mythical land of Westeros."},
    {"id": 66732, "name": "Stranger Things", "first_air_date": "2016-07-15", "vote_average": 8.6, "poster_path": "/49WJfeN0moxb9IPfGn8AIqMGskD.jpg", "backdrop_path": "/56v2KjBlU4XaOv9rVYEQypROD7P.jpg", "overview": "When a young boy vanishes, a small town uncovers a mystery involving secret experiments, terrifying supernatural forces."},
    {"id": 85937, "name": "Demon Slayer", "first_air_date": "2019-04-06", "vote_average": 8.7, "poster_path": "/wrCVHdGemUKEIXsXmSILLlP9lek.jpg", "backdrop_path": "/nTvM4mhqNlHIJnXKPmWLEORYW2n.jpg", "overview": "It is the Taisho Period in Japan. Tanjiro, a kindhearted boy who sells charcoal for a living, finds his family slaughtered by a demon."},
    {"id": 31910, "name": "Naruto Shippūden", "first_air_date": "2007-02-15", "vote_average": 8.6, "poster_path": "/zAYRe2bJxpWTVrwwmBc00VFkAf4.jpg", "backdrop_path": "/c14vjmndzL9tBdooGaNu1NsECfB.jpg", "overview": "Naruto Uzumaki, is a loud, hyperactive, adolescent ninja who constantly searches for approval and recognition."},
    {"id": 4194, "name": "The Walking Dead", "first_air_date": "2010-10-31", "vote_average": 8.1, "poster_path": "/xf9wuDcqlUPWABZNeDKPbZUjWx0.jpg", "backdrop_path": "/KP8ZFb4akNRd9pMmGT0FSTkrC6.jpg", "overview": "Sheriff Deputy Rick Grimes wakes up from a coma to learn the world is in ruins and must lead a group of survivors to stay alive."},
    {"id": 46952, "name": "The Boys", "first_air_date": "2019-07-26", "vote_average": 8.5, "poster_path": "/2zmTngn1tYC1AvfnrFLhxeD82hz.jpg", "backdrop_path": "/mGVrXeIjyecj6TKmwPVpHlscEmw.jpg", "overview": "A group of vigilantes known informally as 'The Boys' set out to take down corrupt superheroes."},
    {"id": 95557, "name": "Invincible", "first_air_date": "2021-03-25", "vote_average": 8.9, "poster_path": "/yDWJYRAwMNKbIYT8ZB33qy84uzO.jpg", "backdrop_path": "/6UH52Fmau8RPsMAbQbjwN3wJSCj.jpg", "overview": "Mark Grayson is a normal teenager except for the fact that his father is the most powerful superhero on the planet."},
]

MOVIE_GENRES = [
    {"id": 28, "name": "Action"},
    {"id": 12, "name": "Adventure"},
    {"id": 16, "name": "Animation"},
    {"id": 35, "name": "Comedy"},
    {"id": 80, "name": "Crime"},
    {"id": 99, "name": "Documentary"},
    {"id": 18, "name": "Drama"},
    {"id": 10751, "name": "Family"},
    {"id": 14, "name": "Fantasy"},
    {"id": 36, "name": "History"},
    {"id": 27, "name": "Horror"},
    {"id": 10402, "name": "Music"},
    {"id": 9648, "name": "Mystery"},
    {"id": 10749, "name": "Romance"},
    {"id": 878, "name": "Science Fiction"},
    {"id": 10770, "name": "TV Movie"},
    {"id": 53, "name": "Thriller"},
    {"id": 10752, "name": "War"},
    {"id": 37, "name": "Western"},
]


# QRunnable worker signals
class TMDBWorkerSignals(QObject):
    finished = pyqtSignal(object)  # result
    error = pyqtSignal(str)  # error message


# Thread pool manager to limit concurrent requests
class ThreadPoolManager:
    """Manages thread pool to prevent too many concurrent requests."""
    _instance = None
    _mutex = QMutex()
    
    def __new__(cls):
        if cls._instance is None:
            with QMutexLocker(cls._mutex):
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Initialize the thread pool with limited threads."""
        self.pool = QThreadPool.globalInstance()
        # Limit maximum threads to prevent overwhelming the system
        self.pool.setMaxThreadCount(min(8, self.pool.maxThreadCount()))
        print(f"Thread pool initialized with {self.pool.maxThreadCount()} max threads")
    
    def start(self, runnable):
        """Start a runnable with priority management."""
        # Check if thread pool is near capacity
        if self.pool.activeThreadCount() >= self.pool.maxThreadCount() - 1:
            print("Thread pool near capacity, queuing request...")
        self.pool.start(runnable)
    
    def get_pool(self):
        """Get the managed thread pool instance."""
        return self.pool

# Global thread pool manager
_thread_pool_manager = ThreadPoolManager()


# Generic TMDB API worker
class TMDBWorker(QRunnable):
    def __init__(self, fetch_func, *args, **kwargs):
        super().__init__()
        self.fetch_func = fetch_func
        self.args = args
        self.kwargs = kwargs
        self.signals = TMDBWorkerSignals()
        self._cancelled = False
        self.setAutoDelete(True)

    def cancel(self):
        self._cancelled = True

    def run(self):
        if self._cancelled:
            return
        try:
            result = self.fetch_func(*self.args, **self.kwargs)
            if not self._cancelled:
                self.signals.finished.emit(result)
        except Exception as e:
            if not self._cancelled:
                self.signals.error.emit(str(e))


def get_image_url(path, size="w342"):
    """Construct full image URL from TMDB path. Using w342 for optimization."""
    if not path:
        return ""
    return f"{IMAGE_BASE_URL}{size}{path}"


# Synchronous fetch functions (called from workers)
def _fetch_popular_movies_sync(api_key=TMDB_API_KEY, page=1):
    """Fetch popular movies from TMDB (runs in background thread)."""
    if not api_key:
        return STATIC_POPULAR_MOVIES
    
    url = f"{BASE_URL}movie/popular"
    import json
    params_str = json.dumps({"api_key": api_key, "page": page})
    
    data = _cached_api_request(url, params_str)
    if not data:
        return STATIC_POPULAR_MOVIES
    
    movies = []
    for movie in data.get("results", []):
        movies.append({
            "id": movie.get("id"),
            "title": movie.get("title"),
            "release_date": movie.get("release_date"),
            "vote_average": movie.get("vote_average"),
            "poster_path": movie.get("poster_path"),
            "backdrop_path": movie.get("backdrop_path"),
            "overview": movie.get("overview"),
        })
    
    return movies


def _fetch_trending_movies_sync(api_key=TMDB_API_KEY, time_window="week"):
    """Fetch trending movies (runs in background thread)."""
    if not api_key:
        return STATIC_POPULAR_MOVIES[:10]
    
    url = f"{BASE_URL}trending/movie/{time_window}"
    import json
    params_str = json.dumps({"api_key": api_key})
    
    data = _cached_api_request(url, params_str)
    if not data:
        return STATIC_POPULAR_MOVIES[:10]
    
    movies = []
    for movie in data.get("results", []):
        movies.append({
            "id": movie.get("id"),
            "title": movie.get("title"),
            "release_date": movie.get("release_date"),
            "vote_average": movie.get("vote_average"),
            "poster_path": movie.get("poster_path"),
            "backdrop_path": movie.get("backdrop_path"),
            "overview": movie.get("overview"),
        })
    
    return movies


def _fetch_popular_tv_shows_sync(api_key=TMDB_API_KEY, page=1):
    """Fetch popular TV shows from TMDB (runs in background thread)."""
    if not api_key:
        return STATIC_TV_SHOWS
    
    url = f"{BASE_URL}tv/popular"
    import json
    params_str = json.dumps({"api_key": api_key, "page": page})
    
    data = _cached_api_request(url, params_str)
    if not data:
        return STATIC_TV_SHOWS
    
    shows = []
    for show in data.get("results", []):
        shows.append({
            "id": show.get("id"),
            "name": show.get("name"),
            "first_air_date": show.get("first_air_date"),
            "vote_average": show.get("vote_average"),
            "poster_path": show.get("poster_path"),
            "backdrop_path": show.get("backdrop_path"),
            "overview": show.get("overview"),
        })
    
    return shows


def _fetch_trending_tv_shows_sync(api_key=TMDB_API_KEY, time_window="week"):
    """Fetch trending TV shows (runs in background thread)."""
    if not api_key:
        return STATIC_TV_SHOWS[:10]
    
    url = f"{BASE_URL}trending/tv/{time_window}"
    import json
    params_str = json.dumps({"api_key": api_key})
    
    data = _cached_api_request(url, params_str)
    if not data:
        return STATIC_TV_SHOWS[:10]
    
    shows = []
    for show in data.get("results", []):
        shows.append({
            "id": show.get("id"),
            "name": show.get("name"),
            "first_air_date": show.get("first_air_date"),
            "vote_average": show.get("vote_average"),
            "poster_path": show.get("poster_path"),
            "backdrop_path": show.get("backdrop_path"),
            "overview": show.get("overview"),
        })
    
    return shows


def _fetch_kdramas_sync(api_key=TMDB_API_KEY, page=1):
    """Fetch Korean dramas (runs in background thread)."""
    if not api_key:
        return STATIC_TV_SHOWS[:5]
    
    url = f"{BASE_URL}discover/tv"
    import json
    params_str = json.dumps({
        "api_key": api_key,
        "with_original_language": "ko",
        "sort_by": "popularity.desc",
        "page": page
    })
    
    data = _cached_api_request(url, params_str)
    if not data:
        return STATIC_TV_SHOWS[:5]
    
    kdramas = []
    for show in data.get("results", []):
        kdramas.append({
            "id": show.get("id"),
            "name": show.get("name"),
            "first_air_date": show.get("first_air_date"),
            "vote_average": show.get("vote_average"),
            "poster_path": show.get("poster_path"),
            "backdrop_path": show.get("backdrop_path"),
            "overview": show.get("overview"),
        })
    
    return kdramas


def _fetch_movies_by_genre_sync(genre_id, api_key=TMDB_API_KEY, page=1):
    """Fetch movies by genre (runs in background thread)."""
    if not api_key:
        return STATIC_POPULAR_MOVIES[:10]
    
    url = f"{BASE_URL}discover/movie"
    import json
    params_str = json.dumps({"api_key": api_key, "with_genres": genre_id, "page": page, "sort_by": "popularity.desc"})
    
    data = _cached_api_request(url, params_str)
    if not data:
        return STATIC_POPULAR_MOVIES[:10]
    
    movies = []
    for movie in data.get("results", []):
        movies.append({
            "id": movie.get("id"),
            "title": movie.get("title"),
            "release_date": movie.get("release_date"),
            "vote_average": movie.get("vote_average"),
            "poster_path": movie.get("poster_path"),
            "backdrop_path": movie.get("backdrop_path"),
            "overview": movie.get("overview"),
        })
    
    return movies


def _search_movies_sync(query, api_key=TMDB_API_KEY, page=1):
    """Search for movies by title (runs in background thread)."""
    if not api_key:
        filtered = [m for m in STATIC_POPULAR_MOVIES if query.lower() in m["title"].lower()]
        return filtered if filtered else STATIC_POPULAR_MOVIES[:5]
    
    url = f"{BASE_URL}search/movie"
    import json
    params_str = json.dumps({"api_key": api_key, "query": query, "page": page})
    
    data = _cached_api_request(url, params_str)
    if not data:
        filtered = [m for m in STATIC_POPULAR_MOVIES if query.lower() in m["title"].lower()]
        return filtered if filtered else STATIC_POPULAR_MOVIES[:5]
    
    movies = []
    for movie in data.get("results", []):
        movies.append({
            "id": movie.get("id"),
            "title": movie.get("title"),
            "release_date": movie.get("release_date"),
            "vote_average": movie.get("vote_average"),
            "poster_path": movie.get("poster_path"),
            "backdrop_path": movie.get("backdrop_path"),
            "overview": movie.get("overview"),
        })
    
    return movies


def _search_tv_shows_sync(query, api_key=TMDB_API_KEY, page=1):
    """Search for TV shows by title (runs in background thread)."""
    if not api_key:
        filtered = [s for s in STATIC_TV_SHOWS if query.lower() in s["name"].lower()]
        return filtered if filtered else STATIC_TV_SHOWS[:5]
    
    url = f"{BASE_URL}search/tv"
    import json
    params_str = json.dumps({"api_key": api_key, "query": query, "page": page})
    
    data = _cached_api_request(url, params_str)
    if not data:
        filtered = [s for s in STATIC_TV_SHOWS if query.lower() in s["name"].lower()]
        return filtered if filtered else STATIC_TV_SHOWS[:5]
    
    shows = []
    for show in data.get("results", []):
        shows.append({
            "id": show.get("id"),
            "name": show.get("name"),
            "first_air_date": show.get("first_air_date"),
            "vote_average": show.get("vote_average"),
            "poster_path": show.get("poster_path"),
            "backdrop_path": show.get("backdrop_path"),
            "overview": show.get("overview"),
        })
    
    return shows


def _fetch_movie_details_sync(movie_id, api_key=TMDB_API_KEY):
    """Fetch detailed information about a specific movie (runs in background thread)."""
    if not api_key:
        return STATIC_POPULAR_MOVIES[0]
    
    url = f"{BASE_URL}movie/{movie_id}"
    import json
    params_str = json.dumps({"api_key": api_key, "append_to_response": "credits,videos"})
    
    data = _cached_api_request(url, params_str)
    if not data:
        return STATIC_POPULAR_MOVIES[0]
    
    # Extract trailer URL from videos
    videos = data.get("videos", {}).get("results", [])
    trailer_key = None
    for video in videos:
        if video.get("site") == "YouTube" and video.get("type") in ["Trailer", "Teaser"]:
            trailer_key = video.get("key")
            break
    
    return {
        "id": data.get("id"),
        "title": data.get("title"),
        "release_date": data.get("release_date"),
        "runtime": data.get("runtime"),
        "vote_average": data.get("vote_average"),
        "vote_count": data.get("vote_count"),
        "poster_path": data.get("poster_path"),
        "backdrop_path": data.get("backdrop_path"),
        "overview": data.get("overview"),
        "genres": [g["name"] for g in data.get("genres", [])],
        "cast": [{"name": c["name"], "character": c["character"]} for c in data.get("credits", {}).get("cast", [])[:10]],
        "director": next((c["name"] for c in data.get("credits", {}).get("crew", []) if c["job"] == "Director"), "N/A"),
        "trailer_key": trailer_key,
    }


def _fetch_tv_details_sync(tv_id, api_key=TMDB_API_KEY):
    """Fetch detailed information about a specific TV show (runs in background thread)."""
    if not api_key:
        return STATIC_TV_SHOWS[0]
    
    url = f"{BASE_URL}tv/{tv_id}"
    import json
    params_str = json.dumps({"api_key": api_key, "append_to_response": "credits,videos"})
    
    data = _cached_api_request(url, params_str)
    if not data:
        return STATIC_TV_SHOWS[0]
    
    # Extract trailer URL from videos
    videos = data.get("videos", {}).get("results", [])
    trailer_key = None
    for video in videos:
        if video.get("site") == "YouTube" and video.get("type") in ["Trailer", "Teaser"]:
            trailer_key = video.get("key")
            break
    
    return {
        "id": data.get("id"),
        "name": data.get("name"),
        "first_air_date": data.get("first_air_date"),
        "last_air_date": data.get("last_air_date"),
        "number_of_seasons": data.get("number_of_seasons"),
        "number_of_episodes": data.get("number_of_episodes"),
        "vote_average": data.get("vote_average"),
        "vote_count": data.get("vote_count"),
        "poster_path": data.get("poster_path"),
        "backdrop_path": data.get("backdrop_path"),
        "overview": data.get("overview"),
        "genres": [g["name"] for g in data.get("genres", [])],
        "cast": [{"name": c["name"], "character": c["character"]} for c in data.get("credits", {}).get("cast", [])[:10]],
        "created_by": [c["name"] for c in data.get("created_by", [])],
        "trailer_key": trailer_key,
    }


# Public API - These return workers that can be started with QThreadPool
def fetch_popular_movies(callback, error_callback=None):
    """Fetch popular movies in background. callback receives the result."""
    worker = TMDBWorker(_fetch_popular_movies_sync)
    worker.signals.finished.connect(callback)
    if error_callback:
        worker.signals.error.connect(error_callback)
    return worker


def fetch_trending_movies(callback, error_callback=None):
    """Fetch trending movies in background. callback receives the result."""
    worker = TMDBWorker(_fetch_trending_movies_sync)
    worker.signals.finished.connect(callback)
    if error_callback:
        worker.signals.error.connect(error_callback)
    return worker


def fetch_popular_tv_shows(callback, error_callback=None):
    """Fetch popular TV shows in background. callback receives the result."""
    worker = TMDBWorker(_fetch_popular_tv_shows_sync)
    worker.signals.finished.connect(callback)
    if error_callback:
        worker.signals.error.connect(error_callback)
    return worker


def fetch_movies_by_genre(genre_id, callback, error_callback=None):
    """Fetch movies by genre in background. callback receives the result."""
    worker = TMDBWorker(_fetch_movies_by_genre_sync, genre_id)
    worker.signals.finished.connect(callback)
    if error_callback:
        worker.signals.error.connect(error_callback)
    return worker


def search_movies(query, callback, error_callback=None):
    """Search movies in background. callback receives the result."""
    worker = TMDBWorker(_search_movies_sync, query)
    worker.signals.finished.connect(callback)
    if error_callback:
        worker.signals.error.connect(error_callback)
    return worker


def search_tv_shows(query, callback, error_callback=None):
    """Search TV shows in background. callback receives the result."""
    worker = TMDBWorker(_search_tv_shows_sync, query)
    worker.signals.finished.connect(callback)
    if error_callback:
        worker.signals.error.connect(error_callback)
    return worker


def fetch_movie_details(movie_id, callback, error_callback=None):
    """Fetch movie details in background. callback receives the result."""
    worker = TMDBWorker(_fetch_movie_details_sync, movie_id)
    worker.signals.finished.connect(callback)
    if error_callback:
        worker.signals.error.connect(error_callback)
    return worker


def fetch_tv_details(tv_id, callback, error_callback=None):
    """Fetch TV show details in background. callback receives the result."""
    worker = TMDBWorker(_fetch_tv_details_sync, tv_id)
    worker.signals.finished.connect(callback)
    if error_callback:
        worker.signals.error.connect(error_callback)
    return worker




# Legacy compatibility - synchronous calls (deprecated, use workers instead)
def fetch_popular_movies_sync():
    return _fetch_popular_movies_sync()

def fetch_trending_movies_sync():
    return _fetch_trending_movies_sync()

def fetch_popular_tv_shows_sync():
    return _fetch_popular_tv_shows_sync()

def fetch_trending_tv_shows_sync():
    return _fetch_trending_tv_shows_sync()

def fetch_kdramas_sync():
    return _fetch_kdramas_sync()

def fetch_movie_genres():
    return MOVIE_GENRES

def fetch_movies_by_genre_sync(genre_id):
    return _fetch_movies_by_genre_sync(genre_id)

def search_movies_sync(query):
    return _search_movies_sync(query)

def search_tv_shows_sync(query):
    return _search_tv_shows_sync(query)

def fetch_movie_details_sync(movie_id):
    return _fetch_movie_details_sync(movie_id)


if __name__ == "__main__":
    # Test the API
    print("Testing TMDB API...")
    
    print("\n=== Popular Movies ===")
    movies = _fetch_popular_movies_sync()
    for idx, movie in enumerate(movies[:5], 1):
        print(f"{idx}. {movie['title']} ({movie.get('release_date', 'N/A')[:4]}) - Rating: {movie['vote_average']}")
    
    print("\n=== Popular TV Shows ===")
    shows = _fetch_popular_tv_shows_sync()
    for idx, show in enumerate(shows[:5], 1):
        print(f"{idx}. {show['name']} ({show.get('first_air_date', 'N/A')[:4]}) - Rating: {show['vote_average']}")
    
    print("\n=== Movie Genres ===")
    genres = MOVIE_GENRES
    for genre in genres[:10]:
        print(f"- {genre['name']}")
