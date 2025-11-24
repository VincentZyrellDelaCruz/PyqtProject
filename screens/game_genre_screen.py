from PyQt6.QtWidgets import QWidget, QLabel, QPushButton, QHBoxLayout, QVBoxLayout, QFrame, QSizePolicy, QScrollArea
from PyQt6.QtCore import Qt, QSize, QByteArray, QThreadPool, QObject, pyqtSignal
from PyQt6.QtGui import QPixmap, QFont, QIcon
from controllers.clickable import ClickableLabel
import os, config, requests
from controllers.music_metadata import display_thumbnail
from controllers.async_loader import ImageLoader, load_placeholder_pixmap
from typing import List

GAME_GENRES = [
    {'name': 'Action',   'color': 'blue', 'id': ''},
    {'name': 'Adventure', 'color': 'black', 'id': ''},
    {'name': 'JRPGs',  'color': 'yellow', 'id': ''},
    {'name': 'Strategy',  'color': 'violet', 'id': ''},
    {'name': 'Sports',  'color': 'red', 'id': ''},
    {'name': 'Simulation',   'color': 'green', 'id': ''},
    {'name': 'Shooter',   'color': 'green', 'id': ''},
]

class GameGenreScreen(QWidget):
    def __init__(self, app_controller=None):
        super().__init__()
        self.app_controller = app_controller

        self.genre_labels = []
        self.active_loaders: List[ImageLoader] = []

        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setStyleSheet("background-color: #121212;")

        self._placeholder = load_placeholder_pixmap()

        self.init_ui()

    def init_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(24, 24, 24, 24)
        self.main_layout.setSpacing(24)

        genre_section = self.create_genre_section()
        self.main_layout.addWidget(genre_section)

        genre_games_section = self.create_games_section(GAME_GENRES[0])
        self.main_layout.addWidget(genre_games_section)

        self.main_layout.addStretch()

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
                background: #444;
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

        for genre in GAME_GENRES:
            genre_card = self.create_genre_card(genre)
            scroll_layout.addWidget(genre_card)

        scroll_layout.addStretch()

        scroll_area.setWidget(scroll_widget)
        card_layout.addWidget(scroll_area)

        card_frame.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        return card_frame

    def create_games_section(self, genre=None):
        genre_games_frame = QFrame()
        genre_games_frame.setStyleSheet("""
            QFrame {
                background-color: #1E1E1E;
                border-radius: 12px;
            }
        """)

        genre_games_frame.setMinimumHeight(1000)

        results_layout = QVBoxLayout(genre_games_frame)
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

        return genre_games_frame

    def handle_selected_genre(self, genre=None):
        if genre is None:
            return

        self.results_label.setText(f"{genre['name']} Games")

        # Cancels all pending image loads
        for loader in self.active_loaders[:]:
            loader.cancel()
        self.active_loaders.clear()

        scroll_content = QWidget()
        scroll_content.setStyleSheet("background-color: transparent;")
        content_layout = QVBoxLayout(scroll_content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(10)

        '''
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
        '''
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
            background-color: {genre['color']};
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