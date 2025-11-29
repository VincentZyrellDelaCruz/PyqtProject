# README

## IMPORTANT NOTE!
- If there's some error when requesting an api call to ytmusicapi, rerun the program just in case.
- Due to fetching and extracting music file from youtube, the program can be laggy and buggy.

## REQUIRED INSTALL:

`pip install PyQt6`

`pip install python-dotenv`

`pip install requests`

`pip install eyed3`

`pip install ytmusicapi yt-dlp`

`pip install python-vlc`
> **NOTE:** You need to download VLC media player

`pip install yt-dlp`
> **NOTE** Video player for trailers - version 3.0.21203

## FOR UPDATING UI FILE: 
After you created/update your UI file, you need to convert from ui (xml) to python file by entering this command to terminal:

python -m PyQt6.uic.pyuic UI/'name of ui' -o UI/'name of python file'

__Example:__

**Startup Screen**
`python -m PyQt6.uic.pyuic UI/startup_screen.ui -o UI/startup_screen_ui.py`

**Welcome Screen**

`python -m PyQt6.uic.pyuic UI/welcome_screen.ui -o UI/welcome_screen_ui.py`

**Login Screen**

`python -m PyQt6.uic.pyuic UI/login_screen.ui -o UI/login_screen_ui.py`

**Main Screen**

`python -m PyQt6.uic.pyuic UI/main_screen.ui -o UI/main_screen_ui.py`

**Music Player Screen**

`python -m PyQt6.uic.pyuic UI/music_player.ui -o UI/music_player_ui.py`

**SQLite**
If you want to test the Database:
`python test_auth.py`


