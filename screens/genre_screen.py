from PyQt6.QtWidgets import QWidget, QLabel, QPushButton, QHBoxLayout, QVBoxLayout, QFrame, QSizePolicy, QScrollArea
from PyQt6.QtCore import Qt, QByteArray, QThreadPool
from PyQt6.QtGui import QPixmap, QFont
import controllers.api_client as ytapi
from controllers.clickable import ClickableLabel
from controllers.async_loader import ImageLoader, load_placeholder_pixmap
from typing import List

GENRES = [
    {'name': 'OPM',   'id': 'RDCLAK5uy_l3gmCPbU_mzs8z79aSnl_DDZY1EdqPc8U'},
    {'name': 'Metal', 'id': 'PLEGvyr7gIqkFQOVzs21J18TYFAuhfNm_m'},
    {'name': 'R&B & Soul',  'id': 'RDCLAK5uy_lQi-t2mN-swhdhGPOg4h4Zw-P5KzdwUSM'},
    {'name': 'Kpop',  'id': 'RDCLAK5uy_lYcZ4MYVJGyRwpiW773f6tOgQGK8rqD9Q'},
    {'name': 'Jpop',  'id': 'RDCLAK5uy_nbK9qSkqYZvtMXH1fLCMmC1yn8HEm0W90'},
    {'name': 'Hip Hop',   'id': 'RDCLAK5uy_kP2172rQNb3KFXz880xp6M98R_ME5CIKA'},
    {'name': 'Thai',   'id': 'RDCLAK5uy_nIawIGq1WuKLBwtCIIcCh3WRwh-u21efk'},
]

class GenreScreen(QWidget):
    def __init__(self, app_controller=None):
        super().__init__()
        self.app_controller = app_controller

        # Keep references to clickable labels to avoid garbage collection
        self.genre_labels = []
        self.active_loaders: List[ImageLoader] = []

        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setStyleSheet("background-color: #121212;")

        self._placeholder = load_placeholder_pixmap()

        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(24)

        top_songs_section = self.create_genre_section()
        main_layout.addWidget(top_songs_section)

        genre_songs_section = self.create_songs_section(GENRES[0])
        main_layout.addWidget(genre_songs_section)

        main_layout.addStretch()

    def create_genre_section(self):
        card_frame = QFrame()
        card_frame.setStyleSheet("""
            background-color: #1E1E1E;
            border-radius: 12px;
        """)

        card_layout = QVBoxLayout(card_frame)
        card_layout.setContentsMargins(18, 14, 18, 14)
        card_layout.setSpacing(10)

        header_label = QLabel("Select Genres")
        header_label.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        header_label.setStyleSheet("color: white;")
        card_layout.addWidget(header_label)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setFixedHeight(150)

        scroll_area.setStyleSheet("""
            QScrollArea {
                background: transparent;
                border: none;
            }
            QScrollBar:horizontal {
                background: #1E1E1E;
                height: 8px;
                border-radius: 4px;
            }
            QScrollBar::handle:horizontal {
                background: #71C562;
                border-radius: 4px;
                min-width: 20px;
            }
            QScrollBar::add-line:horizontal,
            QScrollBar::sub-line:horizontal {
                width: 0;
                height: 0;
            }
        """)

        # scroll widget (NO double layout setting)
        scroll_widget = QWidget()
        scroll_layout = QHBoxLayout(scroll_widget)
        scroll_layout.setContentsMargins(0, 0, 10, 10)
        scroll_layout.setSpacing(10)

        for genre in GENRES:
            genre_card = self.create_genre_card(genre)
            scroll_layout.addWidget(genre_card)

        scroll_layout.addStretch()

        scroll_area.setWidget(scroll_widget)
        card_layout.addWidget(scroll_area)

        card_frame.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        return card_frame

    def create_songs_section(self, genre=None):
        genre_songs_frame = QFrame()
        genre_songs_frame.setStyleSheet("""
            QFrame {
                background-color: #1E1E1E;
                border-radius: 12px;
            }
        """)

        genre_songs_frame.setMinimumHeight(1000)

        results_layout = QVBoxLayout(genre_songs_frame)
        results_layout.setContentsMargins(18, 14, 18, 14)
        results_layout.setSpacing(10)

        # Header label for results
        self.results_label = QLabel()
        self.results_label.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        self.results_label.setStyleSheet("color: white;")
        results_layout.addWidget(self.results_label)

        # Scrollable area for results
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                background: transparent;
                border: none;
            }
        """)

        # Inner content widget
        scroll_content = QWidget()
        scroll_content.setStyleSheet("background-color: transparent;")
        self.scroll_layout = QVBoxLayout(scroll_content)
        self.scroll_layout.setContentsMargins(0, 0, 0, 0)
        self.scroll_layout.setSpacing(10)

        self.scroll_area.setWidget(scroll_content)
        results_layout.addWidget(self.scroll_area)

        self.handle_selected_genre(genre) # Initial load

        return genre_songs_frame

    def handle_selected_genre(self, genre=None):
        if genre is None:
            return

        self.results_label.setText(f"{genre['name']} Songs")

        # Cancels all pending image loads
        for loader in self.active_loaders[:]:
            loader.cancel()
        self.active_loaders.clear()

        scroll_content = QWidget()
        scroll_content.setStyleSheet("background-color: transparent;")
        content_layout = QVBoxLayout(scroll_content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(10)

        try:
            playlist = ytapi.get_playlist(genre.get('id'))
            songs = playlist.get('tracks', [])
        except Exception as e:
            print('Error fetching songs:', e)
            songs = []

        if not songs:
            placeholder = QLabel('No results found.')
            placeholder.setFont(QFont('Segoe UI', 12))
            placeholder.setStyleSheet('color: #BBBBBB;')
            placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
            content_layout.addWidget(placeholder)
        else:
            for song in songs:
                song_widget = self.create_song_item(song)
                content_layout.addWidget(song_widget)

        content_layout.addStretch()

        # Replace scroll widget safely
        old_widget = self.scroll_area.widget()
        if old_widget:
            # Delay deletion to avoid race with pending events
            old_widget.deleteLater()

        self.scroll_area.setWidget(scroll_content)

    def create_genre_card(self, genre):
        card = QFrame()
        card.setFixedSize(180, 100)
        card.setStyleSheet(f"""
            background-color: #71C562;
            border-radius: 10px;
        """)

        vbox = QVBoxLayout(card)
        vbox.setContentsMargins(10, 10, 10, 10)
        vbox.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # KEEP REFERENCE — prevents PyQt from deleting it
        title_label = ClickableLabel(genre['name'])
        self.genre_labels.append(title_label)

        title_label.setWordWrap(True)
        title_label.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        title_label.setStyleSheet("color: white;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        title_label.clicked.connect(lambda g=genre: self.handle_selected_genre(g))

        vbox.addWidget(title_label)
        return card

    def create_song_item(self, song):
        song_widget = QWidget()
        song_layout = QHBoxLayout(song_widget)
        song_layout.setContentsMargins(12, 8, 12, 8)
        song_layout.setSpacing(14)

        # Icon
        icon_label = QLabel()
        icon_label.setFixedSize(48, 48)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        placeholder = self._placeholder.scaled(
            48, 48,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        icon_label.setPixmap(placeholder)

        thumbnail_url = song.get('thumbnails')
        if thumbnail_url:
            self._async_load_icon(thumbnail_url, icon_label)
        else:
            icon_label.setText("♪")

        icon_label.setStyleSheet("""
            QLabel {
                background-color: #1DB954;
                border-radius: 6px;
                color: white;
                font-size: 22px;
                font-weight: bold;
            }
        """)

        # Title and Artist stacked vertically
        text_container = QWidget()
        text_layout = QVBoxLayout(text_container)
        text_layout.setContentsMargins(0, 0, 0, 0)
        text_layout.setSpacing(2)

        name_label = QLabel(song.get('title'))
        name_label.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        name_label.setStyleSheet("color: white; background-color: transparent;")
        name_label.setWordWrap(False)

        artist_label = QLabel(song.get('artist', 'Unknown Artist'))
        artist_label.setFont(QFont("Segoe UI", 11))
        artist_label.setStyleSheet("color: white; background-color: transparent;")
        artist_label.setWordWrap(False)

        text_layout.addWidget(name_label)
        text_layout.addWidget(artist_label)

        # Play button
        play_btn = QPushButton("▶")
        play_btn.setFixedSize(40, 40)
        play_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        play_btn.setStyleSheet("""
            QPushButton {
                background-color: #1DB954;
                border: none;
                border-radius: 20px;
                color: white;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1ed760;
            }
            QPushButton:pressed {
                background-color: #169c46;
            }
        """)
        play_btn.clicked.connect(lambda: self.app_controller.open_api_music_player(song))

        song_layout.addWidget(icon_label)
        song_layout.addWidget(text_container, 1)
        song_layout.addWidget(play_btn)

        return song_widget

    def _async_load_icon(self, url: str, label: QLabel):
        loader = ImageLoader(url)
        self.active_loaders.append(loader)  # Track it

        def on_finished(img_url: str, data: QByteArray):
            # Remove from active list first
            if loader in self.active_loaders:
                self.active_loaders.remove(loader)

            if img_url != url or data.isEmpty():
                return

            # Safety: if label was deleted, skip
            if label is None or not label.parent():
                return

            pix = QPixmap()
            if not pix.loadFromData(data):
                return

            # Force 1:1 square
            pix = pix.scaled(
                48, 48,
                Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                Qt.TransformationMode.SmoothTransformation
            )
            pix = pix.copy((pix.width() - 48) // 2, (pix.height() - 48) // 2, 48, 48)
            label.setPixmap(pix)

        loader.signals.finished.connect(on_finished)
        QThreadPool.globalInstance().start(loader)