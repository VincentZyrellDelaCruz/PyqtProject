from PyQt6.QtWidgets import QWidget, QLabel, QPushButton, QHBoxLayout, QVBoxLayout, QFrame, QSizePolicy, QScrollArea
from PyQt6.QtCore import Qt, QSize, QByteArray, QThreadPool, QObject, pyqtSignal
from PyQt6.QtGui import QPixmap, QFont, QIcon
from controllers.clickable import ClickableLabel
import os, config, requests
from controllers.game_api_client import fetch_genres, fetch_games_by_genre
from controllers.async_loader import ImageLoader, load_placeholder_pixmap
from typing import List

GAME_GENRES = fetch_genres()

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
        genre_games_frame.setMinimumHeight(800)
        genre_games_frame.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        results_layout = QVBoxLayout(genre_games_frame)
        results_layout.setContentsMargins(18, 14, 18, 14)
        results_layout.setSpacing(20)

        # Header
        self.results_label = QLabel()
        self.results_label.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        self.results_label.setStyleSheet("color: white;")
        results_layout.addWidget(self.results_label)

        # Scroll area with grid inside
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setStyleSheet("background: transparent; border: none;")

        # Grid container
        scroll_content = QWidget()
        scroll_content.setStyleSheet("background-color: transparent;")

        from PyQt6.QtWidgets import QGridLayout
        self.grid_layout = QGridLayout(scroll_content)
        self.grid_layout.setContentsMargins(10, 10, 10, 10)
        self.grid_layout.setHorizontalSpacing(24)
        self.grid_layout.setVerticalSpacing(28)

        scroll_area.setWidget(scroll_content)
        results_layout.addWidget(scroll_area, stretch=1)  # Takes all available height

        self.handle_selected_genre(genre)  # Initial load
        return genre_games_frame

    def handle_selected_genre(self, genre=None):
        if genre is None:
            return

        self.results_label.setText(f"{genre.get('name')} Games")

        # Cancel previous loaders
        for loader in self.active_loaders[:]:
            loader.cancel()
        self.active_loaders.clear()

        # Clear previous grid
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        try:
            games = fetch_games_by_genre(genre_slug=genre.get('slug'))
        except Exception as e:
            print('Error fetching games:', e)
            games = []

        if not games:
            no_results = QLabel("No games found in this genre.")
            no_results.setFont(QFont("Segoe UI", 14))
            no_results.setStyleSheet("color: #BBBBBB;")
            no_results.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.grid_layout.addWidget(no_results, 0, 0, 1, 3)  # Span 3 columns
        else:
            for index, game in enumerate(games):
                card = self.create_game_card(game)
                row = index // 3
                col = index % 3
                self.grid_layout.addWidget(card, row, col)

        # Push content to top
        self.grid_layout.setRowStretch(self.grid_layout.rowCount(), 1)

    def create_genre_card(self, genre):
        card = QFrame()
        card.setFixedSize(180, 100)
        card.setStyleSheet(f"""
            background-color: #092f94;
            border-radius: 10px;
        """)

        vbox = QVBoxLayout(card)
        vbox.setContentsMargins(10, 10, 10, 10)
        vbox.setAlignment(Qt.AlignmentFlag.AlignCenter)

        title_label = ClickableLabel(genre.get('name'))
        self.genre_labels.append(title_label)

        title_label.setWordWrap(True)
        title_label.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        title_label.setStyleSheet("color: white;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        title_label.clicked.connect(lambda g=genre: self.handle_selected_genre(g))

        vbox.addWidget(title_label)
        return card

    def create_game_card(self, game):
        card = QFrame()
        card.setFixedSize(250, 320)  # Wider and taller = more space
        card.setCursor(Qt.CursorShape.PointingHandCursor)
        card.setStyleSheet("""
            QFrame {
                background-color: #2D2D2D;
                border-radius: 16px;
                border: 1px solid #333;
            }
            QFrame:hover {
                background-color: #383838;
                border: 1px solid #555;
            }
        """)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)

        image_label = QLabel()
        image_label.setFixedHeight(150)
        image_label.setMinimumWidth(196)  # 220 - 12*2 margins
        image_label.setStyleSheet("""
            QLabel {
                background-color: #1a1a1a;
                border-radius: 12px;
            }
        """)
        image_label.setScaledContents(True)  # This makes image fill the label completely

        # Load image asynchronously (safe scaling)
        if game.get("background_image"):
            self._async_load_card_image(game["background_image"], image_label)
        else:
            placeholder = self._placeholder.scaled(
                400, 400,  # High-res source
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            image_label.setPixmap(placeholder)

        layout.addWidget(image_label)

        title = QLabel(game["name"])
        title.setWordWrap(True)
        title.setFont(QFont("Segoe UI", 11, QFont.Weight.DemiBold))
        title.setStyleSheet("color: white;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # RATING
        rating_layout = QHBoxLayout()
        rating_layout.setSpacing(6)

        star_lbl = QLabel("★")
        star_lbl.setStyleSheet("color: #FFD700; font-size: 16px;")
        rating_layout.addWidget(star_lbl)

        rating_lbl = QLabel(f"{game.get('rating', 0):.1f}")
        rating_lbl.setStyleSheet("color: #FFD700; font-size: 14px;")
        rating_lbl.setFont(QFont("Segoe UI", 10, QFont.Weight.Medium))
        rating_layout.addWidget(rating_lbl)
        rating_layout.addStretch()
        layout.addLayout(rating_layout)

        # VIEW BUTTON
        view_btn = QPushButton("View")
        view_btn.setFixedHeight(40)
        view_btn.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        view_btn.setStyleSheet("""
            QPushButton {
                background-color: #092f94;
                color: white;
                border-radius: 10px;
                padding: 8px;
            }
            QPushButton:hover   { background-color: #1177EE; }
            QPushButton:pressed { background-color: #0055AA; }
        """)
        if self.app_controller:
            view_btn.clicked.connect(lambda _, gid=game["id"]: self.app_controller.show_game_detail(gid))

        layout.addWidget(view_btn)
        layout.addStretch()

        return card

    def _async_load_card_image(self, url: str, label: QLabel):
        def on_finished(img_url: str, data: QByteArray):
            if img_url != url or data.isEmpty():
                return

            pix = QPixmap()
            if not pix.loadFromData(data):
                return

            if pix.isNull():
                return

            scaled = pix.scaled(
                156, 156,
                Qt.AspectRatioMode.KeepAspectRatio,  # NOT ByExpanding!
                Qt.TransformationMode.SmoothTransformation
            )

            # Center crop to exactly fill 156x156
            if scaled.width() > scaled.height():
                cropped = scaled.copy((scaled.width() - 156) // 2, 0, 156, 156)
            elif scaled.height() > scaled.width():
                cropped = scaled.copy(0, (scaled.height() - 156) // 2, 156, 156)
            else:
                cropped = scaled

            label.setPixmap(cropped)

        loader = ImageLoader(url)
        loader.signals.finished.connect(on_finished)
        QThreadPool.globalInstance().start(loader)