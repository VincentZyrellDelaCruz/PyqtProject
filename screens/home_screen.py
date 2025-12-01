from PyQt6.QtWidgets import (
    QWidget, QLabel, QPushButton, QHBoxLayout, QVBoxLayout, QFrame,
    QSizePolicy, QScrollArea
)
from PyQt6.QtCore import Qt, QSize, QThreadPool, QByteArray
from PyQt6.QtGui import QPixmap, QFont, QIcon
import controllers.api_client as ytapi
from controllers.clickable import ClickableLabel
from controllers.async_loader import ImageLoader, load_placeholder_pixmap
import os, config, requests


class HomeScreen(QWidget):
    def __init__(self, app_controller=None):
        super().__init__()
        self.app_controller = app_controller

        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setStyleSheet("HomeScreen { background-color: #121212; }")

        # Load placeholder once
        self._placeholder = load_placeholder_pixmap()

        self.create_home_ui()

    def create_home_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(24)

        # Top Songs Section
        self.top_songs_section = self.create_top_songs_section()
        main_layout.addWidget(self.top_songs_section)

        # Two-column layout for Artists + Recommendations
        two_column_frame = QFrame()
        two_column_frame.setStyleSheet("background: transparent;")
        two_column_layout = QHBoxLayout(two_column_frame)
        two_column_layout.setContentsMargins(0, 0, 0, 0)
        two_column_layout.setSpacing(24)

        top_artist_section = self.create_top_artist_section()
        self.recommendation_section = self.create_recommendation_section()

        top_artist_section.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.recommendation_section.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

        two_column_layout.addWidget(top_artist_section)
        two_column_layout.addWidget(self.recommendation_section)

        main_layout.addWidget(two_column_frame)
        main_layout.addStretch()

    def create_top_songs_section(self):
        card_frame = QFrame()
        card_frame.setStyleSheet("""
            QFrame {
                background-color: #1E1E1E;
                border-radius: 12px;
            }
        """)

        self.top_songs_layout = QVBoxLayout(card_frame)
        self.top_songs_layout.setContentsMargins(18, 14, 18, 14)
        self.top_songs_layout.setSpacing(10)

        # Header (kept permanently)
        header_label = QLabel("Top 10 Songs")
        header_label.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        header_label.setStyleSheet("color: white;")
        self.top_songs_layout.addWidget(header_label)

        self.load_top_songs()  # Initial load

        card_frame.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        return card_frame

    def load_top_songs(self):
        # Clear everything below the header
        for i in reversed(range(self.top_songs_layout.count())):
            item = self.top_songs_layout.itemAt(i)
            if item.widget() and item.widget() != self.top_songs_layout.itemAt(0).widget():
                item.widget().setParent(None)

        songs = ytapi.get_weekly_top_10()

        if not songs:
            no_data_label = QLabel("The song is not available")
            no_data_label.setStyleSheet("color: #AAAAAA; font-size: 16px;")
            no_data_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

            retry_btn = QPushButton("Retry")
            retry_btn.setStyleSheet("""
                QPushButton {
                    background-color: #71C562;
                    color: white;
                    border: none;
                    padding: 10px 20px;
                    border-radius: 8px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #5AA64F;
                }
            """)
            retry_btn.clicked.connect(self.load_top_songs)

            container = QWidget()
            container.setStyleSheet('background: transparent;')
            container_layout = QVBoxLayout(container)
            container_layout.addStretch()
            container_layout.addWidget(no_data_label)
            container_layout.addWidget(retry_btn, alignment=Qt.AlignmentFlag.AlignCenter)
            container_layout.addStretch()

            self.top_songs_layout.addWidget(container)
            return

        # Normal scroll area with songs
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setFixedHeight(230)
        scroll_area.setStyleSheet("""
            QScrollArea { background: transparent; border: none; }
            QScrollBar:horizontal {
                background: #1E1E1E; height: 8px; margin: 0px; border-radius: 4px;
            }
            QScrollBar::handle:horizontal {
                background: #71C562; border-radius: 4px; min-width: 20px;
            }
        """)

        scroll_widget = QWidget()
        scroll_widget.setStyleSheet("background-color: transparent;")
        scroll_layout = QHBoxLayout(scroll_widget)
        scroll_layout.setContentsMargins(0, 0, 10, 10)
        scroll_layout.setSpacing(20)

        for song in songs:
            song_card = self.create_song_card(song)
            scroll_layout.addWidget(song_card)

        scroll_layout.addStretch()
        scroll_area.setWidget(scroll_widget)
        self.top_songs_layout.addWidget(scroll_area)

    def create_recommendation_section(self):
        recommendation_frame = QFrame()
        recommendation_frame.setStyleSheet("""
            QFrame {
                background-color: #1E1E1E;
                border-radius: 12px;
            }
        """)

        self.recommendation_layout = QVBoxLayout(recommendation_frame)
        self.recommendation_layout.setContentsMargins(18, 14, 18, 14)
        self.recommendation_layout.setSpacing(10)

        # Header (permanent)
        self.recommendation_header = QLabel("Songs around the world")
        self.recommendation_header.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        self.recommendation_header.setStyleSheet("color: white;")
        self.recommendation_layout.addWidget(self.recommendation_header)

        self.load_recommendations()

        return recommendation_frame

    def load_recommendations(self):
        # Remove all widgets except the header (index 0)
        for i in reversed(range(self.recommendation_layout.count())):
            if i == 0:  # Skip header
                continue
            item = self.recommendation_layout.itemAt(i)
            if item.widget():
                item.widget().setParent(None)
            elif item.layout():
                # Clear layout if present
                layout = item.layout()
                while layout.count():
                    child = layout.takeAt(0)
                    if child.widget():
                        child.widget().deleteLater()

        songs = ytapi.get_recommended_songs()

        if not songs:
            no_data_label = QLabel("The song is not available")
            no_data_label.setStyleSheet("background: transparent; color: #AAAAAA; font-size: 16px;")
            no_data_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

            retry_btn = QPushButton("Retry")
            retry_btn.setStyleSheet("""
                QPushButton {
                    background-color: #71C562;
                    color: white;
                    border: none;
                    padding: 10px 20px;
                    border-radius: 8px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #5AA64F;
                }
            """)
            retry_btn.clicked.connect(self.load_recommendations)

            container = QWidget()
            container.setStyleSheet('background: transparent;')
            container_layout = QVBoxLayout(container)
            container_layout.addStretch()
            container_layout.addWidget(no_data_label)
            container_layout.addWidget(retry_btn, alignment=Qt.AlignmentFlag.AlignCenter)
            container_layout.addStretch()

            self.recommendation_layout.addWidget(container)
            return

        # Normal list of recommended songs
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 2, 0, 8)
        content_layout.setSpacing(10)

        for song in songs:
            song_btn = self.create_song_button(song)
            content_layout.addWidget(song_btn)

        self.recommendation_layout.addWidget(content_widget)

    def create_top_artist_section(self):
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

        header_label = QLabel("Top Artists")
        header_label.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        header_label.setStyleSheet("color: white;")
        card_layout.addWidget(header_label)

        content_widget = QWidget()
        content_widget.setStyleSheet("background-color: transparent;")
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 2, 0, 8)
        content_layout.setSpacing(10)

        artists = ytapi.get_top_artists() or []

        for artist in artists:
            artist_btn = self.create_artist_button(artist)
            content_layout.addWidget(artist_btn)

        card_layout.addWidget(content_widget)
        return top_artist_frame

    # === Rest of your methods remain unchanged ===
    def create_song_button(self, song):
        title = song.get('title', 'Unknown')
        url = song.get('thumbnails', '')

        btn = QPushButton('   ' + title)
        btn.setFont(QFont('Segoe UI', 14))
        btn.setIconSize(QSize(40, 40))
        btn.setStyleSheet('''
            QPushButton {color:#fff; text-align:left; background:transparent;
                         padding:8px 10px; border:none; border-radius:6px;}
            QPushButton:hover {background:#3a3a3a;}
            QPushButton:checked {background:#1DB954;}
        ''')

        placeholder_icon = QIcon(self._placeholder.scaled(40, 40, Qt.AspectRatioMode.KeepAspectRatio,
                                                          Qt.TransformationMode.SmoothTransformation))
        btn.setIcon(placeholder_icon)
        btn.clicked.connect(lambda _, s=song: self.app_controller.open_api_music_player(s))

        if url:
            self._async_load_button_icon(url, btn, size=40)
        return btn

    def create_artist_button(self, artist):
        name = artist.get('name', 'Unknown Artist')
        url = artist.get('thumbnails', '')

        btn = QPushButton('   ' + name)
        btn.setFont(QFont('Segoe UI', 14))
        btn.setIconSize(QSize(40, 40))
        btn.setStyleSheet('''
            QPushButton {color:#fff; text-align:left; background:transparent;
                         padding:8px 10px; border:none; border-radius:6px;}
            QPushButton:hover {background:#3a3a3a;}
            QPushButton:checked {background:#1DB954;}
        ''')
        btn.clicked.connect(lambda: self.app_controller.goto_artist(name))

        placeholder_icon = QIcon(self._placeholder.scaled(40, 40, Qt.AspectRatioMode.KeepAspectRatio,
                                                          Qt.TransformationMode.SmoothTransformation))
        btn.setIcon(placeholder_icon)

        if url:
            self._async_load_button_icon(url, btn, size=40)
        return btn

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

        img_label = QLabel()
        img_label.setFixedSize(140, 140)
        img_label.setStyleSheet("border-radius: 10px; background-color: #444;")
        img_label.setPixmap(self._placeholder.scaled(140, 140,
                                                     Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                                                     Qt.TransformationMode.SmoothTransformation))

        vbox.addWidget(img_label)

        title_label = ClickableLabel(song.get("title", "Unknown"))
        title_label.setWordWrap(True)
        title_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        title_label.setStyleSheet("color: white;")
        vbox.addWidget(title_label)

        artist_label = ClickableLabel(song.get("artist", "Unknown"))
        artist_label.setFont(QFont("Segoe UI", 9))
        artist_label.setStyleSheet("color: #BBBBBB;")
        vbox.addWidget(artist_label)

        title_label.clicked.connect(lambda: self.app_controller.open_api_music_player(song))

        url = song.get("thumbnails", "")
        if url:
            self._async_load_card_image(url, img_label)

        return card

    def get_thumbnail(self, image_url: str):
        try:
            if not image_url or not image_url.startswith(("http://", "https://")):
                placeholder_path = os.path.join(config.BASE_DIR, "assets", "placeholder.png")
                if os.path.exists(placeholder_path):
                    with open(placeholder_path, "rb") as f:
                        return f.read()
                return b""

            response = requests.get(image_url, timeout=5)
            response.raise_for_status()
            return response.content

        except Exception as e:
            print(f"[WARN] Failed to load thumbnail ({image_url}): {e}")
            placeholder_path = os.path.join(config.BASE_DIR, "assets", "placeholder.png")
            if os.path.exists(placeholder_path):
                with open(placeholder_path, "rb") as f:
                    return f.read()
            return b""

    def _async_load_button_icon(self, url: str, button: QPushButton, size: int = 40):
        def on_finished(img_url: str, data: QByteArray):
            if img_url != url or data.isEmpty():
                return
            pix = QPixmap()
            pix.loadFromData(data)
            pix = pix.scaled(size, size, Qt.AspectRatioMode.KeepAspectRatio,
                             Qt.TransformationMode.SmoothTransformation)
            button.setIcon(QIcon(pix))

        loader = ImageLoader(url)
        loader.signals.finished.connect(on_finished)
        QThreadPool.globalInstance().start(loader)

    def _async_load_card_image(self, url: str, label: QLabel):
        def on_finished(img_url: str, data: QByteArray):
            if img_url != url or data.isEmpty():
                return
            pix = QPixmap()
            pix.loadFromData(data)
            pix = pix.scaled(140, 140, Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                             Qt.TransformationMode.SmoothTransformation)
            label.setPixmap(pix)

        loader = ImageLoader(url)
        loader.signals.finished.connect(on_finished)
        QThreadPool.globalInstance().start(loader)