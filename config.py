import os

# Base project directory (this file is in the project root)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DB_PATH = '' # For SQLite Database
WINDOW_SIZE = (1020, 680) # Default fixed size (1000, 667)

# Use absolute paths so QPixmap/QIcon find assets regardless of CWD
IMAGE_PATH = os.path.join(BASE_DIR, 'assets', 'images') + os.sep
ICON_PATH = os.path.join(BASE_DIR, 'assets', 'icons') + os.sep
LOCAL_MUSIC_PATH = os.path.join(BASE_DIR, 'local_music') + os.sep

API_KEYS = {} # Used to interact systems using API