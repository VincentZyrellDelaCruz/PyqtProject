from PyQt6.QtWidgets import QWidget, QLabel, QLineEdit, QPushButton, QHBoxLayout, QVBoxLayout, QFrame, QSizePolicy, QScrollArea, QGridLayout
from PyQt6.QtCore import Qt, QThreadPool
from PyQt6.QtGui import QPixmap, QFont, QIcon
from controllers.movie_api_client import search_movies_sync, search_tv_shows_sync, get_image_url
from controllers.clickable import ClickableLabel
from controllers.async_loader import ImageLoader, load_placeholder_pixmap
from controllers.request_manager import RequestThrottle
from screens.detail_view_mixin import DetailViewMixin
import config

class MovieSearchScreen(DetailViewMixin, QWidget):
    def __init__(self, app_controller=None):
        super().__init__()

        self.app_controller = app_controller
        self.active_loaders = []
        self.active_workers = []
        self.click_throttle = RequestThrottle(min_interval_ms=500)
        self.search_throttle = RequestThrottle(min_interval_ms=1000)

        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setStyleSheet("background-color: #121212;")

        self._placeholder = load_placeholder_pixmap()

        self.init_ui()
        self.setup_detail_view()

    def init_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # Search section
        search_section = self.create_search_section()
        self.main_layout.addWidget(search_section)

        # Results section
        results_section = self.create_results_section()
        self.main_layout.addWidget(results_section)

    def create_search_section(self):
        card_frame = QWidget()
        card_frame.setStyleSheet("background-color: #121212;")

        card_layout = QVBoxLayout(card_frame)
        card_layout.setContentsMargins(30, 30, 30, 20)
        card_layout.setSpacing(15)

        header_label = QLabel("Search Movies & TV Shows")
        header_label.setFont(QFont("Segoe UI", 24, QFont.Weight.Bold))
        header_label.setStyleSheet("color: white;")
        card_layout.addWidget(header_label)

        # Search input
        search_layout = QHBoxLayout()

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Enter movie or TV show name...")
        self.search_input.setStyleSheet("""
            QLineEdit {
                background-color: #2A2A2A;
                color: white;
                border: 2px solid #444;
                border-radius: 8px;
                padding: 12px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 2px solid #E50914;
            }
        """)
        self.search_input.returnPressed.connect(self.perform_search)
        search_layout.addWidget(self.search_input)

        search_btn = QPushButton("Search")
        search_btn.setFixedSize(120, 45)
        search_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        search_btn.setStyleSheet("""
            QPushButton {
                background-color: #E50914;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #B2070F;
            }
        """)
        search_btn.clicked.connect(self.perform_search)
        search_layout.addWidget(search_btn)

        card_layout.addLayout(search_layout)

        card_frame.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        return card_frame

    def create_results_section(self):
        container = QWidget()
        container.setStyleSheet("background-color: #121212;")
        container.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(30, 20, 30, 30)
        container_layout.setSpacing(20)

        # Header
        self.results_label = QLabel("Search results will appear here")
        self.results_label.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        self.results_label.setStyleSheet("color: white;")
        container_layout.addWidget(self.results_label)

        # Scroll area with vertical grid layout
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scroll_area.setStyleSheet("""
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

        self.scroll_content = QWidget()
        self.scroll_content.setStyleSheet("background-color: transparent;")

        self.grid_layout = QGridLayout(self.scroll_content)
        self.grid_layout.setContentsMargins(0, 0, 0, 10)
        self.grid_layout.setHorizontalSpacing(20)
        self.grid_layout.setVerticalSpacing(20)

        self.scroll_area.setWidget(self.scroll_content)
        container_layout.addWidget(self.scroll_area, stretch=1)

        return container

    def perform_search(self):
        query = self.search_input.text().strip()
        
        if not query:
            self.results_label.setText("Please enter a search term")
            return
        
        # Throttle rapid searches
        if not self.search_throttle.can_proceed():
            wait_ms = self.search_throttle.wait_time()
            self.results_label.setText(f"Please wait {wait_ms}ms before searching again...")
            return

        self.results_label.setText(f"Searching for '{query}'...")

        # Clear existing cards
        for i in reversed(range(self.grid_layout.count())):
            widget = self.grid_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        # Cleanup old loaders
        for loader in self.active_loaders:
            loader.cancel()
        self.active_loaders.clear()

        # Search movies and TV shows
        movies = search_movies_sync(query) or []
        tv_shows = search_tv_shows_sync(query) or []

        all_results = []
        for movie in movies:
            all_results.append({"type": "movie", "data": movie})
        for show in tv_shows:
            all_results.append({"type": "tv", "data": show})

        if not all_results:
            self.results_label.setText(f"No results found for '{query}'")
            return

        self.results_label.setText(f"Found {len(all_results)} results for '{query}'")

        row, col = 0, 0
        max_cols = 5

        for result in all_results:
            if result["type"] == "movie":
                card = self.create_movie_card(result["data"])
            else:
                card = self.create_tv_card(result["data"])
            
            self.grid_layout.addWidget(card, row, col)
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

        # Click handler to show movie details
        movie_id = movie.get("id")
        poster_label.clicked.connect(lambda mid=movie_id: self.show_movie_details(mid))

        card_layout.addWidget(poster_label)

        # Rating badge overlay
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

    def create_tv_card(self, show):
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

        # TV show poster
        poster_label = ClickableLabel()
        poster_label.setFixedSize(180, 240)
        poster_label.setScaledContents(True)
        poster_label.setStyleSheet("border-radius: 6px 6px 0 0;")
        poster_label.setPixmap(self._placeholder)
        
        # Load poster image
        poster_url = get_image_url(show.get("poster_path"), "w500")
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

        # Click handler to show TV details
        show_id = show.get("id")
        poster_label.clicked.connect(lambda sid=show_id: self.show_tv_details(sid))

        card_layout.addWidget(poster_label)

        # Rating badge
        rating = show.get("vote_average", 0)
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
