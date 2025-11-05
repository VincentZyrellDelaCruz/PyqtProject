# README

## REQUIRED INSTALL:

`pip install PyQt6`

`pip install python-dotenv`

`pip install requests`

`pip install eyed3`

`pip install ytmusicapi yt-dlp`

FFMPEG (Scroll down below for installation)

## NOTE FOR UPDATING UI FILE: 
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

# FOR INSTALLING FFMPEG
**To install FFmpeg on Windows, download the ZIP from the official site, extract it, and add its `bin` folder to your system PATH.**
Here’s a step-by-step guide to get FFmpeg up and running:

---

### 🛠️ Step-by-Step Installation Guide for FFmpeg on Windows

1. **Download FFmpeg**
   - Go to the [official FFmpeg website](https://ffmpeg.org/download.html).
   - Under "Windows," click on the link to download a build (e.g., from gyan.dev or BtbN).
   - Choose the latest release ZIP file for Windows.

2. **Extract the ZIP File**
   - Right-click the downloaded ZIP and select *Extract All*.
   - Place the extracted folder somewhere permanent, like `C:\ffmpeg` or `C:\ffmpeg\ffmpeg-master-latest-win64-gpl-shared\bin`.

3. **Add FFmpeg to System PATH**
   - Open *Start Menu* → search for **Environment Variables** → click *Edit the system environment variables*.
   - In the *System Properties* window, click **Environment Variables**.
   - Under *System Variables*, find and select **Path**, then click **Edit**.
   - Click **New** and add the path to the `bin` folder inside your extracted FFmpeg directory (e.g., `C:\ffmpeg\bin`).
   - Click **OK** to close all dialogs.

4. **Verify Installation**
   - Open *Command Prompt* and type: `ffmpeg -version`
   - If installed correctly, it will display the FFmpeg version and configuration details.

---

