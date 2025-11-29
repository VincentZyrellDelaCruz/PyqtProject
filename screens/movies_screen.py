from PyQt6.QtWidgets import QWidget, QLabel, QHBoxLayout, QVBoxLayout, QFrame, QSizePolicy, QScrollArea, QGridLayout
from PyQt6.QtCore import Qt, QThreadPool
from PyQt6.QtGui import QPixmap, QFont
from controllers.movie_api_client import fetch_popular_movies_sync, get_image_url
from controllers.clickable import ClickableLabel
from controllers.async_loader import ImageLoader, load_placeholder_pixmap
from controllers.request_manager import RequestThrottle
from screens.detail_view_mixin import DetailViewMixin
import config

class MoviesScreen(DetailViewMixin, QWidget):
    def __init__(self, app_controller=None):
        super().__init__()

        self.app_controller = app_controller
        self.active_loaders = []
        self.active_workers = []
        self.click_throttle = RequestThrottle(min_interval_ms=500)

        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setStyleSheet("background-color: #121212;")

        self._placeholder = load_placeholder_pixmap()

        self.init_ui()
        self.setup_detail_view()

    def init_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # Popular Movies Section
        movies_section = self.create_movies_section()
        self.main_layout.addWidget(movies_section)

    def create_movies_section(self):
        container = QWidget()
        container.setStyleSheet("background-color: #121212;")
        container.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(30, 30, 30, 30)
        container_layout.setSpacing(20)

        # Header
        header_label = QLabel("Popular Movies")
        header_label.setFont(QFont("Segoe UI", 24, QFont.Weight.Bold))
        header_label.setStyleSheet("color: white;")
        container_layout.addWidget(header_label)

        # Load popular movies
        movies = fetch_popular_movies_sync() or []

        # Create vertical scrolling area with grid
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
        
        grid_layout = QGridLayout(scroll_content)
        grid_layout.setContentsMargins(0, 0, 0, 10)
        grid_layout.setHorizontalSpacing(20)
        grid_layout.setVerticalSpacing(20)

        row, col = 0, 0
        max_cols = 5

        for movie in movies:
            movie_card = self.create_movie_card(movie)
            grid_layout.addWidget(movie_card, row, col)
            col += 1
            if col >= max_cols:
                col = 0
                row += 1

        scroll_area.setWidget(scroll_content)
        container_layout.addWidget(scroll_area)

        return container

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
