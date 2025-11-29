import os

# Base project directory (this file is in the project root)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DB_PATH = '' # For SQLite Database
WINDOW_SIZE = (1200, 800) # Default window size (shows all controls properly)
MIN_WINDOW_SIZE = (1024, 768) # Minimum window size for proper UI display

# Use absolute paths so QPixmap/QIcon find assets regardless of CWD
IMAGE_PATH = os.path.join(BASE_DIR, 'assets', 'images') + os.sep
ICON_PATH = os.path.join(BASE_DIR, 'assets', 'icons') + os.sep
LOCAL_MUSIC_PATH = os.path.join(BASE_DIR, 'local_music') + os.sep
LYRICS_PATH = os.path.join(BASE_DIR, 'lyrics') + os.sep

DEFAULT_VOLUME = 50 # Temporary fixed volume

API_KEYS = {} # Used to interact systems using API

# TMDB API Configuration
TMDB_API_KEY = "4fc92bbedcf713b032d10ed99be51798"
TMDB_BASE_URL = "https://api.themoviedb.org/3/"
TMDB_IMAGE_BASE_URL = "https://image.tmdb.org/t/p/"
TMDB_MAX_REQUESTS_PER_SECOND = 10
TMDB_REQUEST_TIMEOUT = 10  # seconds