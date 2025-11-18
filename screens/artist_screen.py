from typing import List
from PyQt6.QtWidgets import QWidget, QLabel, QPushButton, QHBoxLayout, QVBoxLayout, QFrame, QSizePolicy, QScrollArea, QLineEdit
from PyQt6.QtCore import Qt, QSize, QByteArray, QThreadPool
from PyQt6.QtGui import QFont, QIcon, QPixmap
import controllers.api_client as ytapi
from controllers.async_loader import ImageLoader, load_placeholder_pixmap
from controllers.api_client import get_artist_metadata
from controllers.clickable import ClickableLabel


class ArtistScreen(QWidget):
    def __init__(self, app_controller=None, artist=None):
        super().__init__()
        self.app_controller = app_controller

        self.active_loaders: List[ImageLoader] = []

        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setStyleSheet("SearchScreen { background-color: #121212; }")

        self._placeholder = load_placeholder_pixmap()

        # print(get_artist_metadata(artist))
        self.artist_metadata = get_artist_metadata(artist)

        self.init_ui()

    def init_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(10)

        # Search
        artist_panel = self.create_artist_panel()
        main_layout.addWidget(artist_panel)

        self.two_row_section = self.create_two_row_section()

        self.two_row_section.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        main_layout.addWidget(self.two_row_section)

        main_layout.setStretch(0, 1)
        main_layout.setStretch(1, 4)

    def create_artist_panel(self):
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
        self.artist_image_label = QLabel()
        self.artist_image_label.setFixedSize(300, 200)
        self.artist_image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.artist_image_label.setStyleSheet("""
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
        self.artist_image_label.setPixmap(placeholder)

        # Async load real image (1:1 with center crop)
        image_url = self.artist_metadata.get('image')
        if image_url:
            self._async_load_artist_image(image_url, self.artist_image_label, size=200)

        layout.addWidget(self.artist_image_label, alignment=Qt.AlignmentFlag.AlignCenter)

        # Artist Name
        name = self.artist_metadata.get('artist', 'Unknown Artist')
        name_label = QLabel(name)
        name_label.setFont(QFont("Segoe UI", 22, QFont.Weight.Bold))
        name_label.setStyleSheet("color: white; background: transparent;")
        name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        name_label.setWordWrap(True)
        layout.addWidget(name_label)

        # Artist Description / Bio

        desc_container = QFrame()
        desc_container.setStyleSheet("""
            QFrame {
                background-color: #1E1E1E;
                border-radius: 12px;
                border: 1px solid #333;
            }
        """)
        desc_layout = QVBoxLayout(desc_container)
        desc_layout.setContentsMargins(16, 16, 16, 16)
        desc_layout.setSpacing(0)

        # Scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setStyleSheet("""
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

        desc_text = QLabel(self.artist_metadata.get('description', 'No description available.'))
        desc_text.setFont(QFont("Segoe UI", 11))
        desc_text.setStyleSheet("color: #BBBBBB; background: transparent; border: none;")
        desc_text.setWordWrap(True)
        desc_text.setContentsMargins(0, 0, 8, 0)  # Right margin for scrollbar

        scroll.setWidget(desc_text)
        desc_layout.addWidget(scroll)
        layout.addWidget(desc_container)

        layout.addStretch()

        return panel

    def create_two_row_section(self):
        two_row_frame = QFrame()
        two_row_frame.setStyleSheet("background: transparent;")

        two_row_layout = QVBoxLayout(two_row_frame)
        two_row_layout.setContentsMargins(0, 0, 0, 0)
        two_row_layout.setSpacing(10)

        self.album_panel = self.create_album_panel()
        self.song_panel = self.create_song_panel()

        # Allow song panel to expand
        self.album_panel.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.song_panel.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        two_row_layout.addWidget(self.album_panel)
        two_row_layout.addWidget(self.song_panel)

        # Give songs more vertical space than albums
        two_row_layout.setStretch(0, 1)
        two_row_layout.setStretch(1, 2)

        # === SCROLL AREA WRAPPER ===
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
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

        scroll_area.setWidget(two_row_frame)

        return scroll_area

    def create_album_panel(self):
        wrapper = QFrame()
        wrapper.setStyleSheet("""
            QFrame {
                background-color: #1E1E1E;
                border-radius: 12px;
            }
        """)

        main_layout = QVBoxLayout(wrapper)
        main_layout.setContentsMargins(18, 14, 18, 14)
        main_layout.setSpacing(10)

        header = QFrame()
        header.setStyleSheet("background-color: transparent;")
        header_layout = QVBoxLayout(header)
        header_layout.setContentsMargins(18, 18, 18, 12)
        header_layout.setSpacing(4)

        title_lbl = QLabel("Albums")
        title_lbl.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        title_lbl.setStyleSheet("color: white;")
        header_layout.addWidget(title_lbl)

        artist_name = self.artist_metadata.get('artist', 'Unknown Artist')
        subtitle_lbl = QLabel(f"List of Albums Sang by {artist_name}")
        subtitle_lbl.setFont(QFont("Segoe UI", 12))
        subtitle_lbl.setStyleSheet("color: #AAAAAA;")
        header_layout.addWidget(subtitle_lbl)

        main_layout.addWidget(header)

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
                width: 8px;
                margin: 0px;
            }
            QScrollBar::handle:horizontal {
                background: #1DB954;
                border-radius: 4px;
                min-height: 20px;
            }
            QScrollBar::add-line:horizontal,
            QScrollBar::sub-line:horizontal {
                height: 0;
                width: 0;
            }
            QScrollBar::add-page:horizontal,
            QScrollBar::sub-page:horizontal {
                background: none;
            }
        """)

        scroll_content = QWidget()
        scroll_content.setStyleSheet("background-color: transparent;")

        scroll_layout = QHBoxLayout(scroll_content)
        scroll_layout.setContentsMargins(18, 0, 18, 18)
        scroll_layout.setSpacing(20)

        albums = self.artist_metadata.get('albums', [])

        for album in albums:
            card = self.create_album_card(album)
            # Fixed: add to the correct local scroll_layout (not self.scroll_layout)
            scroll_layout.addWidget(card)

        scroll_layout.addStretch()
        scroll_content.setLayout(scroll_layout)
        scroll_area.setWidget(scroll_content)
        main_layout.addWidget(scroll_area)

        return wrapper

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

        title_lbl = QLabel("Top Songs")
        title_lbl.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        title_lbl.setStyleSheet("color: white;")
        header_layout.addWidget(title_lbl)

        # Fixed: single-string label for subtitle
        artist_name = self.artist_metadata.get('artist', 'Unknown Artist')
        subtitle_lbl = QLabel(f"Greatest Hit Songs by {artist_name}")
        subtitle_lbl.setFont(QFont("Segoe UI", 12))
        subtitle_lbl.setStyleSheet("color: #AAAAAA;")
        header_layout.addWidget(subtitle_lbl)

        main_layout.addWidget(header)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setStyleSheet("""
            QScrollArea {
                background: transparent;
                border: none;
            }
        """)

        scroll_content = QWidget()
        scroll_content.setStyleSheet("background-color: transparent;")

        self.scroll_layout = QVBoxLayout(scroll_content)
        self.scroll_layout.setContentsMargins(18, 0, 18, 18)
        self.scroll_layout.setSpacing(12)

        songs = self.artist_metadata.get('songs', [])

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

    def create_album_card(self, album):
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
        img_label.setPixmap(self._placeholder.scaled(140, 140,
                                                     Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                                                     Qt.TransformationMode.SmoothTransformation))

        vbox.addWidget(img_label)

        # Title
        title_label = ClickableLabel(album.get("title", "Unknown"))
        title_label.setWordWrap(True)
        title_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        title_label.setStyleSheet("color: white;")
        vbox.addWidget(title_label)

        # Artist / Year
        year_label = ClickableLabel(album.get("year", "Unknown"))
        year_label.setFont(QFont("Segoe UI", 9))
        year_label.setStyleSheet("color: #BBBBBB;")
        vbox.addWidget(year_label)

        url = album.get("thumbnails", "")
        if url:
            self._async_load_card_image(url, img_label)

        browseId = album.get("browseId", "")
        title_label.clicked.connect(lambda: self.app_controller.goto_playlist(browseId, url))

        return card

    # ASYNC FUNCTIONS
    # Async load for artist image (larger, same logic as thumbnails)
    def _async_load_artist_image(self, url: str, label: QLabel, size: int = 200):
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
