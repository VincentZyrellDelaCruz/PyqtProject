from PyQt6.QtWidgets import QWidget, QLabel, QPushButton, QHBoxLayout, QVBoxLayout, QFrame, QSizePolicy, QScrollArea
from PyQt6.QtCore import Qt, QSize, QThreadPool, QByteArray
from PyQt6.QtGui import QPixmap, QFont, QIcon
from controllers.clickable import ClickableLabel
from controllers.async_loader import ImageLoader, load_placeholder_pixmap
import os, config, requests

class GameHomeScreen(QWidget):
    def __init__(self, app_controller=None):
        super().__init__()

        self.app_controller = app_controller

        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setStyleSheet("HomeScreen { background-color: #121212; }")

        # Load placeholder once
        # self._placeholder = load_placeholder_pixmap()

        self.init_ui()

    def init_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(24, 24, 24, 24)
        self.main_layout.setSpacing(24)

        # Top Songs Section
        top_games_section = self.create_top_games_section()
        self.main_layout.addWidget(top_games_section)

        '''
        # Create both sections
        top_artist_section = self.create_top_artist_section()
        recommendation_section = self.create_recommendation_section()

        # Ensure both sections expand evenly
        top_artist_section.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        recommendation_section.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        '''

        # self.main_layout.addWidget()
        self.main_layout.addStretch()

    def create_top_games_section(self):
        container = QFrame()
        container.setStyleSheet("""
            QFrame {
                background-color: #1E1E1E;
                border-radius: 12px;
            }
        """)

        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(18, 14, 18, 14)
        container_layout.setSpacing(10)

        # Header
        header_label = QLabel("Top 10 Games of the Week")
        header_label.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        header_label.setStyleSheet("color: white;")
        container_layout.addWidget(header_label)

        # --- Scroll Area ---
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setFixedHeight(230)
        scroll_area.setStyleSheet("""
            QScrollArea {
                background: transparent;
                border: none;
            }

            QScrollBar:horizontal {
                background: #1E1E1E;
                height: 8px;
                margin: 0px;  
                border-radius: 4px;
            }

            QScrollBar::handle:horizontal {
                background: #444;
                border-radius: 4px;
                min-width: 20px;
            }

            QScrollBar::add-line:horizontal,
            QScrollBar::sub-line:horizontal {
                background: none;
                width: 0px;
                height: 0px;
            }

            QScrollBar::add-page:horizontal,
            QScrollBar::sub-page:horizontal {
                background: #1E1E1E;
            }
        """)

        # Inner widget for scroll area
        scroll_widget = QWidget()
        scroll_widget.setStyleSheet("background-color: transparent;")

        scroll_layout = QHBoxLayout(scroll_widget)
        scroll_layout.setContentsMargins(0, 0, 10, 10)
        scroll_layout.setSpacing(20)

        # Load top 10 songs
        '''
        games = ytapi.get_weekly_top_10() or []

        for game in games:
            song_card = self.create_game_card(game)
            scroll_layout.addWidget(song_card)
        '''

        scroll_layout.addStretch()
        scroll_widget.setLayout(scroll_layout)
        scroll_area.setWidget(scroll_widget)
        container_layout.addWidget(scroll_area)

        # Allows expansion so the frame height fits the scroll content nicely
        container.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        return container

    def create_game_card(self, game):
        pass