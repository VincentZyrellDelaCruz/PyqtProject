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

    Priority:
    1. Embedded USLT (standard lyrics frame)
    2. Custom fields (description, synopsis, comment)
    3. .lrc file in config.LYRICS_PATH
    """
    lyrics_data = []

    try:
        audiofile = eyed3.load(song_path)
        tag = getattr(audiofile, "tag", None)

        # --- Step 1: Try standard embedded lyrics (USLT) ---
        if tag and getattr(tag, "lyrics", None):
            for lyric_tag in tag.lyrics:
                if hasattr(lyric_tag, "sync") and lyric_tag.sync:
                    for (timestamp, text) in lyric_tag.sync:
                        lyrics_data.append((timestamp, text.strip()))
                elif lyric_tag.text:
                    lyrics_data.append((0, lyric_tag.text.strip()))
            if lyrics_data:
                return sorted(lyrics_data, key=lambda x: x[0])

        # --- Step 2: Try to find lyrics inside custom metadata text fields ---
        possible_fields = [
            getattr(tag, "comment", None),
            getattr(tag, "description", None),
            getattr(tag, "synopsis", None),
        ]
        text_blocks = []

        for field in possible_fields:
            if isinstance(field, str) and len(field.strip()) > 30:  # heuristic: long enough to be lyrics
                text_blocks.append(field)
            elif hasattr(field, "text") and field.text and len(field.text.strip()) > 30:
                text_blocks.append(field.text)

        # Combine and extract possible lyric lines
        if text_blocks:
            combined_text = "\n".join(text_blocks)
            # Try to cut out only the part after 'LYRICS:' if exists
            if "LYRICS:" in combined_text.upper():
                combined_text = combined_text.split("LYRICS:", 1)[1]
            lines = [line.strip() for line in combined_text.splitlines() if line.strip()]
            lyrics_data = [(i * 5000, line) for i, line in enumerate(lines)]  # fake timestamps for scrolling
            if lyrics_data:
                return lyrics_data

    except Exception as e:
        print(f"[Lyrics] Error extracting embedded/custom lyrics: {e}")

    # --- Step 3: Fallback to external .lrc file ---
    try:
        song_name = os.path.splitext(os.path.basename(song_path))[0]
        lrc_path = os.path.join(config.LYRICS_PATH, f"{song_name}.lrc")

        if os.path.exists(lrc_path):
            with open(lrc_path, "r", encoding="utf-8") as f:
                for line in f:
                    matches = re.findall(r"\[(\d+):(\d+(?:\.\d+)?)\](.*)", line)
                    for match in matches:
                        minutes = int(match[0])
                        seconds = float(match[1])
                        timestamp_ms = int((minutes * 60 + seconds) * 1000)
                        lyric_text = match[2].strip()
                        if lyric_text:
                            lyrics_data.append((timestamp_ms, lyric_text))
    except Exception as e:
        print(f"[Lyrics] Error reading external .lrc file: {e}")

    return sorted(lyrics_data, key=lambda x: x[0])





