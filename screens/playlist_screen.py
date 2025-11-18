from typing import List
from PyQt6.QtWidgets import QWidget, QLabel, QPushButton, QHBoxLayout, QVBoxLayout, QFrame, QSizePolicy, QScrollArea, QLineEdit
from PyQt6.QtCore import Qt, QSize, QByteArray, QThreadPool
from PyQt6.QtGui import QFont, QIcon, QPixmap
import controllers.api_client as ytapi
from controllers.async_loader import ImageLoader, load_placeholder_pixmap
from controllers.api_client import get_album_tracks
from controllers.clickable import ClickableLabel


class PlaylistScreen(QWidget):
    def __init__(self, app_controller=None, browse_id=None, playlist_img=None):
        super().__init__()
        self.app_controller = app_controller
        self.playlist = get_album_tracks(browse_id)
        self.playlist_img = playlist_img

        self.active_loaders: List[ImageLoader] = []

        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setStyleSheet("SearchScreen { background-color: #121212; }")

        self._placeholder = load_placeholder_pixmap()

        self.init_ui()

    def init_ui(self):
        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(10)

        # Search
        self.album_panel = self.create_album_panel()
        self.main_layout.addWidget(self.album_panel)

        self.song_panel = self.create_song_panel()
        self.song_panel.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.main_layout.addWidget(self.song_panel)

        self.main_layout.setStretch(0, 1)
        self.main_layout.setStretch(1, 4)

    def create_album_panel(self):
        panel = QFrame()
        panel.setFixedWidth(320)
        panel.setStyleSheet("""
            QFrame {
                background-color: #1E1E1E;
                border: none;
            }
        """)

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(24, 32, 24, 32)
        layout.setSpacing(20)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # === Artist Image (200x200, 1:1, rounded) ===
        self.playlist_image_label = QLabel()
        self.playlist_image_label.setFixedSize(300, 200)
        self.playlist_image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.playlist_image_label.setStyleSheet("""
            QLabel {
                background: none;
                border: none;
            }
        """)

        # Load placeholder first
        placeholder = self._placeholder.scaled(
            200, 200,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        self.playlist_image_label.setPixmap(placeholder)

        # Async load real image (1:1 with center crop)
        if self.playlist_img:
            self._async_load_playlist_image(self.playlist_img, self.playlist_image_label, size=200)

        layout.addWidget(self.playlist_image_label, alignment=Qt.AlignmentFlag.AlignCenter)

        # Playlist Title
        playlist = self.playlist.get('title', 'Unknown')
        playlist_label = QLabel(playlist)
        playlist_label.setFont(QFont("Segoe UI", 22, QFont.Weight.Bold))
        playlist_label.setStyleSheet("color: white; background: transparent;")
        playlist_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        playlist_label.setWordWrap(True)
        layout.addWidget(playlist_label)

        layout.addStretch()

        return panel

    def create_song_panel(self):
        wrapper = QFrame()
        wrapper.setStyleSheet("""
            QFrame {
                background-color: #1E1E1E;
                border-radius: 12px;
            }
        """)

        main_layout = QVBoxLayout(wrapper)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        header = QFrame()
        header.setStyleSheet("background-color: transparent;")
        header_layout = QVBoxLayout(header)
        header_layout.setContentsMargins(18, 18, 18, 12)
        header_layout.setSpacing(4)

        title_lbl = QLabel("Album Tracks")
        title_lbl.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        title_lbl.setStyleSheet("color: white;")
        header_layout.addWidget(title_lbl)

        main_layout.addWidget(header)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setStyleSheet("""
            QScrollArea {
                background: transparent;
                border: none;
            }
            QScrollBar:vertical {
                background: #1E1E1E;
                width: 8px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #1DB954;
                border-radius: 4px;
                min-height: 20px;
            }
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                height: 0;
                width: 0;
            }
            QScrollBar::add-page:vertical,
            QScrollBar::sub-page:vertical {
                background: none;
            }
        """)

        scroll_content = QWidget()
        scroll_content.setStyleSheet("background-color: transparent;")

        self.scroll_layout = QVBoxLayout(scroll_content)
        self.scroll_layout.setContentsMargins(18, 0, 18, 18)
        self.scroll_layout.setSpacing(12)

        songs = self.playlist.get('tracks', [])

        for song in songs:
            item = self.create_song_item(song)
            self.scroll_layout.addWidget(item)

        self.scroll_layout.addStretch()

        scroll_area.setWidget(scroll_content)
        main_layout.addWidget(scroll_area)

        return wrapper

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

        playlist_label = QLabel(song.get('title'))
        playlist_label.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        playlist_label.setStyleSheet("color: white; background-color: transparent;")
        playlist_label.setWordWrap(False)

        artist_label = QLabel(song.get('artist', 'Unknown Artist'))
        artist_label.setFont(QFont("Segoe UI", 11))
        artist_label.setStyleSheet("color: white; background-color: transparent;")
        artist_label.setWordWrap(False)

        text_layout.addWidget(playlist_label)
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

    def _async_load_playlist_image(self, url: str, label: QLabel, size: int = 200):
        loader = ImageLoader(url)
        self.active_loaders.append(loader)

        def on_finished(img_url: str, data: QByteArray):
            if loader in self.active_loaders:
                self.active_loaders.remove(loader)

            if img_url != url or data.isEmpty():
                return
            if not label.parent():
                return

            pix = QPixmap()
            if pix.loadFromData(data):
                # Force perfect 1:1 circle-ready square
                pix = pix.scaled(
                    size, size,
                    Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                    Qt.TransformationMode.SmoothTransformation
                )
                pix = pix.copy((pix.width() - size) // 2, (pix.height() - size) // 2, size, size)
                label.setPixmap(pix)

        loader.signals.finished.connect(on_finished)
        QThreadPool.globalInstance().start(loader)

    def _async_load_icon(self, url: str, label: QLabel):
        loader = ImageLoader(url)
        self.active_loaders.append(loader)  # Track it

        def on_finished(img_url: str, data: QByteArray):
            # Remove from active list first
            if loader in self.active_loaders:
                self.active_loaders.remove(loader)

            if img_url != url or data.isEmpty():
                return

            # if label was deleted, skip
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
