from PyQt6.QtWidgets import QWidget, QLabel, QPushButton, QHBoxLayout, QVBoxLayout, QFrame, QSizePolicy, QScrollArea
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QPixmap, QFont, QIcon
import controllers.api_client as ytapi
import os, sys, config, requests


class HomeScreen(QWidget):
    def __init__(self, app_controller=None):
        super().__init__()
        self.app_controller = app_controller

        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setStyleSheet("HomeScreen { background-color: #121212; }")

        self.create_home_ui()

    def create_home_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(24)

        # Recommended songs section
        top_songs_section = self.create_top_songs_section()
        top_artist_section = self.create_top_artist_section()

        main_layout.addWidget(top_songs_section)
        main_layout.addWidget(top_artist_section)

        main_layout.addStretch()

    def create_top_songs_section(self):
        card_frame = QFrame()
        card_frame.setStyleSheet("""
            QFrame {
                background-color: #1E1E1E;
                border-radius: 12px;
            }
        """)

        card_layout = QVBoxLayout(card_frame)
        card_layout.setContentsMargins(18, 14, 18, 14)
        card_layout.setSpacing(10)

        # Header
        header_label = QLabel("Top 10 Songs")
        header_label.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        header_label.setStyleSheet("color: white;")
        card_layout.addWidget(header_label)

        # Scrollable song cards container
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setStyleSheet("""
            QScrollArea {
                background: transparent;
                border: none;
            }
            QScrollBar:horizontal {
                background: #1E1E1E;
                height: 6px;
            }
            QScrollBar::handle:horizontal {
                background: #444;
                border-radius: 3px;
            }
        """)

        # Inner widget of the scroll area
        scroll_widget = QWidget()
        scroll_widget.setStyleSheet("""
            QWidget {
                background-color: transparent;
            }
        """)

        scroll_layout = QHBoxLayout(scroll_widget)
        scroll_layout.setContentsMargins(0, 2, 0, 8)
        scroll_layout.setSpacing(20)

        # Load top 10 songs
        songs = ytapi.get_weekly_top_10()

        for song in songs:
            song_card = self.create_song_card(song)
            scroll_layout.addWidget(song_card)

        scroll_widget.setLayout(scroll_layout)
        scroll_area.setWidget(scroll_widget)
        card_layout.addWidget(scroll_area)

        return card_frame

    def create_recommendation_section(self):
        pass

    def create_top_artist_section(self):
        from controllers import api_client  # make sure api_client is imported

        # Outer container
        top_artist_frame = QFrame()
        top_artist_frame.setStyleSheet("""
            QFrame {
                background-color: #1E1E1E;
                border-radius: 12px;
            }
        """)

        card_layout = QVBoxLayout(top_artist_frame)
        card_layout.setContentsMargins(18, 14, 18, 14)
        card_layout.setSpacing(10)

        # Header
        header_label = QLabel("Top Artists")
        header_label.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        header_label.setStyleSheet("color: white;")
        card_layout.addWidget(header_label)

        # Content widget inside scroll area
        content_widget = QWidget()
        content_widget.setStyleSheet("background-color: transparent;")
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 2, 0, 8)
        content_layout.setSpacing(10)

        # Load top artists from API client
        artists = api_client.get_top_artists()

        for artist in artists:
            artist_name = artist.get('name', 'Unknown Artist')
            artist_icon = artist.get('thumbnails', '')  # match your dict key

            artist_btn = QPushButton((' '*3) + artist_name)
            artist_btn.setFont(QFont('Segoe UI', 14))

            # Get thumbnail bytes
            thumbnail_data = self.get_thumbnail(artist_icon)

            # Load the image from the bytes into QPixmap
            pixmap = QPixmap()
            if pixmap.loadFromData(thumbnail_data):
                artist_btn.setIcon(QIcon(pixmap))
            else:
                # If loading the image fails, set a default (placeholder) icon
                pixmap.loadFromData(self.get_thumbnail(''))  # Use the default image for failed loads
                artist_btn.setIcon(QIcon(pixmap))

            artist_btn.setIconSize(QSize(40, 40))
            artist_btn.setStyleSheet('''
                QPushButton { 
                    color: #fff;
                    text-align: left;
                    background-color: transparent; 
                    padding: 8px 10px;
                    border: none;
                    border-radius: 6px; 
                }
                QPushButton:hover {
                    background-color: #3a3a3a;
                }
                QPushButton:checked {
                    background-color: #1DB954;
                }
                QIcon {
                    border-radius: 5px;
                }
            ''')
            content_layout.addWidget(artist_btn)

        content_widget.setLayout(content_layout)
        card_layout.addWidget(content_widget)

        return top_artist_frame

    def create_song_card(self, song):
        card = QFrame()
        card.setFixedSize(140, 190)
        card.setStyleSheet("""
            QFrame {
                background-color: #2A2A2A;
                border-radius: 10px;
            }
            QFrame:hover {
                background-color: #333333;
            }
        """)

        vbox = QVBoxLayout(card)
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.setSpacing(8)
        vbox.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Thumbnail
        img_label = QLabel()
        img_label.setFixedSize(140, 140)
        img_label.setStyleSheet("border-radius: 10px; background-color: #444;")

        image = self.get_thumbnail(song.get("thumbnail", ""))

        pixmap = QPixmap()
        pixmap.loadFromData(image)
        pixmap = pixmap.scaled(140, 140, Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                                          Qt.TransformationMode.SmoothTransformation)
        img_label.setPixmap(pixmap)


        vbox.addWidget(img_label)

        # Title
        title_label = QLabel(song.get("title", "Unknown"))
        title_label.setWordWrap(True)
        title_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        title_label.setStyleSheet("color: white;")
        vbox.addWidget(title_label)

        # Artist
        artist_label = QLabel(song.get("artist", "Unknown"))
        artist_label.setFont(QFont("Segoe UI", 9))
        artist_label.setStyleSheet("color: #BBBBBB;")
        vbox.addWidget(artist_label)

        return card

    def get_thumbnail(self, image_url: str):
        # Safely fetch thumbnail image. Returns raw image bytes.
        try:
            # Validate URL before requesting
            if not image_url or not image_url.startswith(("http://", "https://")):
                # Return placeholder image instead of crashing
                placeholder_path = os.path.join(config.BASE_DIR, "assets", "placeholder.png")
                if os.path.exists(placeholder_path):
                    with open(placeholder_path, "rb") as f:
                        return f.read()
                # If no placeholder file exists, return empty bytes
                return b""

            response = requests.get(image_url, timeout=5)
            response.raise_for_status()
            return response.content

        except Exception as e:
            print(f"[WARN] Failed to load thumbnail ({image_url}): {e}")
            # Fallback to placeholder image
            placeholder_path = os.path.join(config.BASE_DIR, "assets", "placeholder.png")
            if os.path.exists(placeholder_path):
                with open(placeholder_path, "rb") as f:
                    return f.read()
            return b""
