import os, config, eyed3, re
from PyQt6.QtGui import QPixmap
from eyed3.id3.frames import ImageFrame

def get_embedded_image(song_path, square=False):
    pixmap = None
    try:
        audiofile = eyed3.load(song_path)
        if audiofile and audiofile.tag:
            image_data = None
            for image in audiofile.tag.images:
                if image.picture_type == ImageFrame.FRONT_COVER:
                    image_data = image.image_data
                    break

            if not image_data and audiofile.tag.images:
                image_data = list(audiofile.tag.images)[0].image_data

            if image_data:
                pixmap = QPixmap()
                if pixmap.loadFromData(image_data):
                    print("Album art loaded from:", song_path)
                else:
                    pixmap = None

    except Exception as e:
        print("Error extracting album art:", e)

    # Fallback if no album art found
    if not pixmap or pixmap.isNull():
        fallback_path = os.path.join(config.IMAGE_PATH, "default.png")
        pixmap = QPixmap(fallback_path)

    # Make it 1:1 if requested
    if square and not pixmap.isNull():
        w, h = pixmap.width(), pixmap.height()
        if w != h:
            side = min(w, h)
            x = (w - side) // 2
            y = (h - side) // 2
            pixmap = pixmap.copy(x, y, side, side)

    return pixmap

def get_music_metadata(song_path):
    """Return (artist_name, album_art_pixmap)"""
    artist = "Unknown Artist"
    pixmap = get_embedded_image(song_path)

    try:
        audiofile = eyed3.load(song_path)
        if audiofile and audiofile.tag and audiofile.tag.artist:
            artist = audiofile.tag.artist
    except Exception as e:
        print("Error extracting artist:", e)

    return artist, pixmap

def get_lyrics(song_path):
    """
    Returns a list of (timestamp_ms, lyric_line) tuples.
    It first checks for a .lrc file inside config.LYRICS_PATH,
    then falls back to embedded lyrics in the mp3 file.
    """
    lyrics_data = []

    # Get the base filename (without extension)
    song_name = os.path.splitext(os.path.basename(song_path))[0]
    lrc_path = os.path.join(config.LYRICS_PATH, f"{song_name}.lrc")

    # --- Check .lrc file in LYRICS_PATH ---
    if os.path.exists(lrc_path):
        try:
            with open(lrc_path, "r", encoding="utf-8") as f:
                for line in f:
                    # Match lines like: [mm:ss.xx] lyric
                    matches = re.findall(r"\[(\d+):(\d+(?:\.\d+)?)\](.*)", line)
                    for match in matches:
                        minutes = int(match[0])
                        seconds = float(match[1])
                        timestamp_ms = int((minutes * 60 + seconds) * 1000)
                        lyric_text = match[2].strip()
                        if lyric_text:
                            lyrics_data.append((timestamp_ms, lyric_text))
        except Exception as e:
            print(f"[Lyrics] Error reading {lrc_path}: {e}")
        return sorted(lyrics_data, key=lambda x: x[0])

    # --- Fallback: Extract lyrics embedded in MP3 metadata ---
    try:
        audiofile = eyed3.load(song_path)
        if not audiofile or not audiofile.tag:
            return []

        for lyric_tag in getattr(audiofile.tag, "lyrics", []):
            if hasattr(lyric_tag, "sync"):  # synchronized lyrics
                for (timestamp, text) in lyric_tag.sync:
                    lyrics_data.append((timestamp, text.strip()))
            else:  # unsynchronized lyrics
                lyrics_data.append((0, lyric_tag.text.strip()))
            break
    except Exception as e:
        print(f"[Lyrics] Error extracting embedded lyrics: {e}")

    return lyrics_data



