from PyQt6.QtWidgets import QWidget, QLabel, QPushButton, QHBoxLayout, QVBoxLayout, QFrame, QSizePolicy, QScrollArea
from PyQt6.QtCore import Qt, QSize, QByteArray, QThreadPool
from PyQt6.QtGui import QPixmap, QFont, QIcon
from controllers.clickable import ClickableLabel
import os, config, requests
from controllers.game_api_client import fetch_game_info
from controllers.async_loader import ImageLoader, load_placeholder_pixmap
from typing import List


class GameInfoScreen(QWidget):
    def __init__(self, app_controller=None, game_id=None):
        super().__init__()
        self.app_controller = app_controller
        self.game_id = game_id

        self.active_loaders: List[ImageLoader] = []

        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setStyleSheet("background-color: #121212;")

        self._placeholder = load_placeholder_pixmap()

        # Fetch game details
        self.game_info = fetch_game_info(game_id=game_id) if game_id else {}

        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(24)

        # Back button at the top
        back_button = self.create_back_button()
        main_layout.addWidget(back_button)

        # Game header section
        header_section = self.create_header_section()
        main_layout.addWidget(header_section)

        # Game details section
        details_section = self.create_details_section()
        main_layout.addWidget(details_section)

        main_layout.addStretch()

    def create_back_button(self):
        """Create a back button to return to games list"""
        button_container = QFrame()
        button_container.setStyleSheet("background-color: transparent; border: none;")
        button_layout = QHBoxLayout(button_container)
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.setSpacing(8)

        back_btn = QPushButton("← Back")
        back_btn.setFixedWidth(120)
        back_btn.setFixedHeight(40)
        back_btn.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        back_btn.setStyleSheet("""
            QPushButton {
                background-color: #092f94;
                color: white;
                border-radius: 8px;
                padding: 6px;
            }
            QPushButton:hover {
                background-color: #1177EE;
            }
            QPushButton:pressed {
                background-color: #0055AA;
            }
        """)
        
        if self.app_controller:
            back_btn.clicked.connect(self.app_controller.go_back_from_game_detail)

        button_layout.addWidget(back_btn)
        button_layout.addStretch()

        return button_container

    def create_header_section(self):
        """Create header with game image and basic info"""
        header_frame = QFrame()
        header_frame.setStyleSheet("""
            QFrame {
                background-color: #1E1E1E;
                border-radius: 12px;
            }
        """)

        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(24, 24, 24, 24)
        header_layout.setSpacing(24)

        # Game image (left side)
        self.game_image_label = QLabel()
        self.game_image_label.setFixedSize(250, 350)
        self.game_image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.game_image_label.setStyleSheet("""
            QLabel {
                background: #0a0a0a;
                border: 1px solid #333;
                border-radius: 8px;
            }
        """)

        # Load placeholder first
        placeholder = self._placeholder.scaled(
            250, 350,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        self.game_image_label.setPixmap(placeholder)

        # Async load real image
        image_url = self.game_info.get('background_image')
        if image_url:
            self._async_load_game_image(image_url, self.game_image_label, size=250)

        header_layout.addWidget(self.game_image_label)

        # Game info (right side)
        info_layout = QVBoxLayout()
        info_layout.setSpacing(12)

        # Game Title
        title = self.game_info.get('name', 'Unknown Game')
        title_label = QLabel(title)
        title_label.setFont(QFont("Segoe UI", 28, QFont.Weight.Bold))
        title_label.setStyleSheet("color: white;")
        title_label.setWordWrap(True)
        info_layout.addWidget(title_label)

        # Release Date
        released = self.game_info.get('released', 'N/A')
        released_label = QLabel(f"Released: {released}")
        released_label.setFont(QFont("Segoe UI", 12))
        released_label.setStyleSheet("color: #AAAAAA;")
        info_layout.addWidget(released_label)

        # Rating
        rating = self.game_info.get('rating', 0)
        rating_label = QLabel(f"★ Rating: {rating:.1f}")
        rating_label.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        rating_label.setStyleSheet("color: #FFD700;")
        info_layout.addWidget(rating_label)

        # Platforms
        platforms = self.game_info.get('platforms', [])
        if platforms:
            platforms_text = ", ".join(platforms) if isinstance(platforms, list) else str(platforms)
            platforms_label = QLabel(f"Platforms: {platforms_text}")
            platforms_label.setFont(QFont("Segoe UI", 11))
            platforms_label.setStyleSheet("color: #AAAAAA;")
            platforms_label.setWordWrap(True)
            info_layout.addWidget(platforms_label)

        # Genres
        genres = self.game_info.get('genres', [])
        if genres:
            genres_text = ", ".join([g.get('name', '') if isinstance(g, dict) else str(g) for g in genres])
            genres_label = QLabel(f"Genres: {genres_text}")
            genres_label.setFont(QFont("Segoe UI", 11))
            genres_label.setStyleSheet("color: #AAAAAA;")
            genres_label.setWordWrap(True)
            info_layout.addWidget(genres_label)

        info_layout.addStretch()

        header_layout.addLayout(info_layout, stretch=1)
        header_frame.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        return header_frame

    def create_details_section(self):
        """Create section with game description and additional info"""
        details_frame = QFrame()
        details_frame.setStyleSheet("""
            QFrame {
                background-color: #1E1E1E;
                border-radius: 12px;
            }
        """)

        details_layout = QVBoxLayout(details_frame)
        details_layout.setContentsMargins(24, 24, 24, 24)
        details_layout.setSpacing(16)

        # Description header
        desc_header = QLabel("Description")
        desc_header.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        desc_header.setStyleSheet("color: white;")
        details_layout.addWidget(desc_header)

        # Description text
        description = self.game_info.get('description', 'No description available.')
        # Strip HTML tags if present
        import re
        description = re.sub('<[^<]+?>', '', description)
        
        desc_label = QLabel(description)
        desc_label.setFont(QFont("Segoe UI", 11))
        desc_label.setStyleSheet("color: #CCCCCC;")
        desc_label.setWordWrap(True)
        desc_label.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        
        details_layout.addWidget(desc_label)

        # Additional info grid
        info_grid_layout = QVBoxLayout()
        info_grid_layout.setSpacing(12)

        # Metacritic Score
        metacritic = self.game_info.get('metacritic')
        if metacritic:
            metacritic_label = QLabel(f"Metacritic Score: {metacritic}")
            metacritic_label.setFont(QFont("Segoe UI", 11))
            metacritic_label.setStyleSheet("color: #AAAAAA;")
            info_grid_layout.addWidget(metacritic_label)

        # Developer
        developers = self.game_info.get('developers', [])
        if developers:
            dev_text = ", ".join([d.get('name', '') if isinstance(d, dict) else str(d) for d in developers])
            dev_label = QLabel(f"Developer: {dev_text}")
            dev_label.setFont(QFont("Segoe UI", 11))
            dev_label.setStyleSheet("color: #AAAAAA;")
            dev_label.setWordWrap(True)
            info_grid_layout.addWidget(dev_label)

        # Publisher
        publishers = self.game_info.get('publishers', [])
        if publishers:
            pub_text = ", ".join([p.get('name', '') if isinstance(p, dict) else str(p) for p in publishers])
            pub_label = QLabel(f"Publisher: {pub_text}")
            pub_label.setFont(QFont("Segoe UI", 11))
            pub_label.setStyleSheet("color: #AAAAAA;")
            pub_label.setWordWrap(True)
            info_grid_layout.addWidget(pub_label)

        details_layout.addLayout(info_grid_layout)
        details_layout.addStretch()

        details_frame.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        return details_frame

    def _async_load_game_image(self, url: str, label: QLabel, size: int = 250):
        """Load game image asynchronously"""
        def on_finished(img_url: str, data: QByteArray):
            if img_url != url or data.isEmpty():
                return

            pix = QPixmap()
            if not pix.loadFromData(data):
                return

            if pix.isNull():
                return

            scaled = pix.scaled(
                size, size + 100,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )

            label.setPixmap(scaled)

        loader = ImageLoader(url)
        loader.signals.finished.connect(on_finished)
        self.active_loaders.append(loader)
        QThreadPool.globalInstance().start(loader)
