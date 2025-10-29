# README

## REQUIRED INSTALL:

`pip install PyQt6`

`pip install python-dotenv`

`pip install requests`

`pip install eyed3` 

## NOTE: 
After you created/update your UI file, you need to convert from ui (xml) to python file by entering this command to terminal:

python -m PyQt6.uic.pyuic UI/'name of ui' -o UI/'name of python file'

__Example:__

**Welcome Screen**

`python -m PyQt6.uic.pyuic UI/welcome_screen.ui -o UI/welcome_screen_ui.py`

**Login Screen**

`python -m PyQt6.uic.pyuic UI/login_screen.ui -o UI/login_screen_ui.py`

**Main Screen**

`python -m PyQt6.uic.pyuic UI/main_screen.ui -o UI/main_screen_ui.py`

**Music Player Screen**

`python -m PyQt6.uic.pyuic UI/music_player.ui -o UI/music_player_ui.py`



