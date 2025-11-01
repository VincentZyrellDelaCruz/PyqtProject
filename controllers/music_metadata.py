import os, config
import eyed3
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
