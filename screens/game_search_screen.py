from typing import List
from PyQt6.QtWidgets import QWidget, QLabel, QPushButton, QHBoxLayout, QVBoxLayout, QFrame, QSizePolicy, QScrollArea, QLineEdit
from PyQt6.QtCore import Qt, QSize, QByteArray, QThreadPool
from PyQt6.QtGui import QFont, QIcon, QPixmap
from controllers.game_api_client import search_games
from controllers.async_loader import ImageLoader, load_placeholder_pixmap

class GameSearchScreen(QWidget):
    def __init__(self, app_controller=None):
        super().__init__()
        self.app_controller = app_controller

        self.active_loaders: List[ImageLoader] = []

        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setStyleSheet("SearchScreen { background-color: #121212; }")

        self._placeholder = load_placeholder_pixmap()

        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # Header
        header_label = QLabel("Search Games")
        header_label.setFont(QFont("Segoe UI", 22, QFont.Weight.Bold))
        header_label.setStyleSheet("color: white; background: transparent;")
        main_layout.addWidget(header_label)

        # Search
        search_section = self.create_search_section()
        main_layout.addWidget(search_section)

        # Results section (hidden initially)
        self.results_frame = self.create_results_section()
        main_layout.addWidget(self.results_frame)

        main_layout.addStretch()

    def clear_search(self):
        """Clear the search input field"""
        self.search_input.clear()

    # Function for creating search section
    def create_search_section(self):
        search_frame = QFrame()
        search_frame.setStyleSheet("background-color: #1E1E1E; border-radius: 10px;")
        search_layout = QHBoxLayout(search_frame)
        search_layout.setContentsMargins(14, 10, 14, 10)
        search_layout.setSpacing(10)

        # QLineEdit for search input
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search for games...")
        self.search_input.setFont(QFont("Segoe UI", 12))
        self.search_input.setStyleSheet("""
            QLineEdit {
                color: white;
                background-color: #2A2A2A;
                border-radius: 8px;
                padding: 8px 12px;
                border: 1px solid #333;
            }
            QLineEdit:focus {
                border: 1px solid #1DB954;
                background-color: #333;
            }
        """)
        self.search_input.returnPressed.connect(self.search_handling)

        # Search button
        self.search_button = QPushButton("Search")
        self.search_button.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        self.search_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.search_button.setStyleSheet("""
            QPushButton {
                background-color: #092f94;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 8px 18px;
            }
            QPushButton:hover {
                background-color: #1ed760;
            }
            QPushButton:pressed {
                background-color: #169c46;
            }
        """)

        self.search_button.clicked.connect(self.search_handling)

        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.search_button)

        return search_frame

    # Function for creating results section (initialized as hidden)
    def create_results_section(self):
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame {
                background-color: #1E1E1E;
                border-radius: 12px;
            }
        """)
        frame.setVisible(False)

        frame.setMinimumHeight(800)
        frame.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        results_layout = QVBoxLayout(frame)
        results_layout.setContentsMargins(18, 14, 18, 14)
        results_layout.setSpacing(20)  # ← increased spacing for grid

        # Header label for results
        results_label = QLabel("Search Results")
        results_label.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        results_label.setStyleSheet("color: white;")
        results_layout.addWidget(results_label)

        # NEW: Scroll area + grid container
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setStyleSheet('''
            QScrollArea {
                background: transparent;
                border: none;
            }
            QScrollBar:vertical {
                background: #1E1E1E;
                height: 8px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background: #092f94;
                border-radius: 4px;
                min-width: 20px;
            }
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                width: 0;
                height: 0;
            }''')

        # Container widget that holds the grid
        scroll_content = QWidget()
        scroll_content.setStyleSheet("background-color: transparent;")

        # ←←← 3-column grid layout
        from PyQt6.QtWidgets import QGridLayout
        self.grid_layout = QGridLayout(scroll_content)
        self.grid_layout.setContentsMargins(10, 10, 10, 10)
        self.grid_layout.setHorizontalSpacing(24)
        self.grid_layout.setVerticalSpacing(28)

        scroll_area.setWidget(scroll_content)
        results_layout.addWidget(scroll_area, stretch=1)

        return frame

    # Function for handling and displaying search results
    def search_handling(self):
        query = self.search_input.text().strip()
        if not query:
            return

        # Show results section
        if not self.results_frame.isVisible():
            self.results_frame.setVisible(True)

        # Clear previous results
        while self.grid_layout.count():
            child = self.grid_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        try:
            games = search_games(query=query) or []
        except Exception as e:
            print(f"Error fetching games: {e}")
            no_result = QLabel("Error loading results.")
            no_result.setStyleSheet("color: #BBBBBB;")
            self.grid_layout.addWidget(no_result, 0, 0, 1, 3)
            return

        if not games:
            placeholder = QLabel("No results found.")
            placeholder.setFont(QFont("Segoe UI", 14))
            placeholder.setStyleSheet("color: #BBBBBB;")
            placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.grid_layout.addWidget(placeholder, 0, 0, 1, 3)  # span 3 columns
            return

        # Add cards in 3-column grid
        for index, game in enumerate(games):
            card = self.create_game_card(game)
            row = index // 3
            col = index % 3
            self.grid_layout.addWidget(card, row, col)

        # Optional: add stretch to push everything to top
        self.grid_layout.setRowStretch(self.grid_layout.rowCount(), 1)


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
            view_btn.clicked.connect(lambda _, gid=game["id"]: self.app_controller.show_game_detail(gid, source=2))

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
