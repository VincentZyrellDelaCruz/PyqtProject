from PyQt6.QtWidgets import QWidget, QLabel, QPushButton, QHBoxLayout, QVBoxLayout, QFrame, QSizePolicy, QScrollArea, QGridLayout
from PyQt6.QtCore import Qt, QThreadPool
from PyQt6.QtGui import QPixmap, QFont
from controllers.movie_api_client import fetch_movie_genres, fetch_movies_by_genre_sync, get_image_url, MOVIE_GENRES
from controllers.clickable import ClickableLabel
from controllers.async_loader import ImageLoader, load_placeholder_pixmap
from controllers.request_manager import RequestThrottle
from screens.detail_view_mixin import DetailViewMixin
import config

class MovieGenreScreen(DetailViewMixin, QWidget):
    def __init__(self, app_controller=None):
        super().__init__()

        self.app_controller = app_controller
        self.active_loaders = []
        self.active_workers = []
        self.click_throttle = RequestThrottle(min_interval_ms=500)
        self.genre_throttle = RequestThrottle(min_interval_ms=800)

        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setStyleSheet("background-color: #121212;")

        self._placeholder = load_placeholder_pixmap()

        self.init_ui()
        self.setup_detail_view()

    def init_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # Genre selection section
        genre_section = self.create_genre_section()
        self.main_layout.addWidget(genre_section)

        # Movies by genre section
        genres = MOVIE_GENRES
        if genres:
            movies_section = self.create_movies_section(genres[0])
            self.main_layout.addWidget(movies_section)

    def create_genre_section(self):
        card_frame = QWidget()
        card_frame.setStyleSheet("background-color: #121212;")

        card_layout = QVBoxLayout(card_frame)
        card_layout.setContentsMargins(30, 30, 30, 20)
        card_layout.setSpacing(15)

        header_label = QLabel("Select Genre")
        header_label.setFont(QFont("Segoe UI", 24, QFont.Weight.Bold))
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
                background: #E50914;
                border-radius: 4px;
                min-width: 20px;
            }
            QScrollBar::add-line:horizontal,
            QScrollBar::sub-line:horizontal {
                width: 0;
                height: 0;
            }
        """)

        scroll_widget = QWidget()
        scroll_layout = QHBoxLayout(scroll_widget)
        scroll_layout.setContentsMargins(0, 0, 10, 10)
        scroll_layout.setSpacing(10)

        for genre in MOVIE_GENRES:
            genre_card = self.create_genre_card(genre)
            scroll_layout.addWidget(genre_card)

        scroll_layout.addStretch()

        scroll_area.setWidget(scroll_widget)
        card_layout.addWidget(scroll_area)

        card_frame.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        return card_frame

    def create_genre_card(self, genre):
        card = QPushButton(genre["name"])
        card.setFixedSize(140, 100)
        card.setCursor(Qt.CursorShape.PointingHandCursor)
        card.setStyleSheet("""
            QPushButton {
                background-color: #2A2A2A;
                color: white;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #E50914;
            }
        """)

        card.clicked.connect(lambda: self.handle_selected_genre(genre))

        return card

    def create_movies_section(self, genre):
        container = QWidget()
        container.setStyleSheet("background-color: #121212;")
        container.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(30, 20, 30, 30)
        container_layout.setSpacing(20)

        # Header
        self.genre_label = QLabel()
        self.genre_label.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        self.genre_label.setStyleSheet("color: white;")
        container_layout.addWidget(self.genre_label)

        # Scroll area with grid
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
                width: 10px;
                background: #2A2A2A;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical {
                background: #E50914;
                border-radius: 5px;
                min-height: 40px;
            }
            QScrollBar::handle:vertical:hover {
                background: #B2070F;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)

        scroll_content = QWidget()
        scroll_content.setStyleSheet("background-color: transparent;")

        self.grid_layout = QGridLayout(scroll_content)
        self.grid_layout.setContentsMargins(0, 0, 0, 10)
        self.grid_layout.setHorizontalSpacing(20)
        self.grid_layout.setVerticalSpacing(20)

        scroll_area.setWidget(scroll_content)
        container_layout.addWidget(scroll_area, stretch=1)

        self.handle_selected_genre(genre)
        return container

    def handle_selected_genre(self, genre):
        if genre is None:
            return
        
        # Throttle rapid genre changes
        if not self.genre_throttle.can_proceed():
            print(f"Genre change throttled, please wait {self.genre_throttle.wait_time()}ms")
            return

        self.genre_label.setText(f"{genre['name']} Movies")

        # Clear existing cards
        for i in reversed(range(self.grid_layout.count())):
            widget = self.grid_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        # Cleanup old loaders
        for loader in self.active_loaders:
            loader.cancel()
        self.active_loaders.clear()

        # Load movies by genre
        movies = fetch_movies_by_genre_sync(genre["id"]) or []

        row, col = 0, 0
        max_cols = 5

        for movie in movies:
            movie_card = self.create_movie_card(movie)
            self.grid_layout.addWidget(movie_card, row, col)

            col += 1
            if col >= max_cols:
                col = 0
                row += 1

    def create_movie_card(self, movie):
        card = QFrame()
        card.setFixedSize(180, 270)
        card.setCursor(Qt.CursorShape.PointingHandCursor)
        card.setStyleSheet("""
            QFrame {
                background-color: #1E1E1E;
                border-radius: 6px;
            }
            QFrame:hover {
                background-color: #3A3A3A;
            }
        """)

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(0, 0, 0, 0)
        card_layout.setSpacing(0)

        # Movie poster
        poster_label = ClickableLabel()
        poster_label.setFixedSize(180, 240)
        poster_label.setScaledContents(True)
        poster_label.setStyleSheet("border-radius: 6px 6px 0 0;")
        poster_label.setPixmap(self._placeholder)
        
        # Load poster image
        poster_url = get_image_url(movie.get("poster_path"), "w500")
        if poster_url:
            def on_finished(url, data):
                if not data.isEmpty():
                    pixmap = QPixmap()
                    pixmap.loadFromData(data)
                    if not pixmap.isNull():
                        poster_label.setPixmap(pixmap)
            
            loader = ImageLoader(poster_url)
            loader.signals.finished.connect(on_finished)
            self.active_loaders.append(loader)
            QThreadPool.globalInstance().start(loader)

        # Click handler to show details
        movie_id = movie.get("id")
        poster_label.clicked.connect(lambda mid=movie_id: self.show_movie_details(mid))

        card_layout.addWidget(poster_label)

        # Rating badge
        rating = movie.get("vote_average", 0)
        rating_badge = QLabel(f"⭐ {rating:.1f}")
        rating_badge.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        rating_badge.setStyleSheet("""
            background-color: rgba(0, 0, 0, 0.8);
            color: #FFD700;
            padding: 4px 8px;
            border-radius: 4px;
        """)
        rating_badge.setFixedHeight(30)
        rating_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(rating_badge)

        return card

    def cleanup(self):
        """Clean up active loaders when widget is destroyed."""
        self.cleanup_detail_view()
        for loader in self.active_loaders:
            loader.cancel()
        self.active_loaders.clear()
        for worker in self.active_workers:
            worker.cancel()
        self.active_workers.clear()

    def __del__(self):
        self.cleanup()
