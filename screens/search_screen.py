from PyQt6.QtWidgets import QWidget, QLabel, QPushButton, QHBoxLayout, QVBoxLayout, QFrame, QSizePolicy, QScrollArea, QLineEdit
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont, QIcon
import controllers.api_client as ytapi
import os, config


class SearchScreen(QWidget):
    def __init__(self, app_controller=None):
        super().__init__()
        self.app_controller = app_controller

        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setStyleSheet("SearchScreen { background-color: #121212; }")

        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # Header
        header_label = QLabel("Search Music")
        header_label.setFont(QFont("Segoe UI", 22, QFont.Weight.Bold))
        header_label.setStyleSheet("color: black; background: transparent;")
        main_layout.addWidget(header_label)

        # Search
        search_section = self.create_search_section()
        main_layout.addWidget(search_section)

        # Results section (hidden initially)
        self.results_frame = self.create_results_section()
        main_layout.addWidget(self.results_frame)

        main_layout.addStretch()

    # Function for creating search section
    def create_search_section(self):
        search_frame = QFrame()
        search_frame.setStyleSheet("background-color: #1E1E1E; border-radius: 10px;")
        search_layout = QHBoxLayout(search_frame)
        search_layout.setContentsMargins(14, 10, 14, 10)
        search_layout.setSpacing(10)

        # QLineEdit for search input
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search for songs, artists, or albums...")
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

        # Search button
        self.search_button = QPushButton("Search")
        self.search_button.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        self.search_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.search_button.setStyleSheet("""
            QPushButton {
                background-color: #1DB954;
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
        frame.setVisible(False)  # hidden initially

        results_layout = QVBoxLayout(frame)
        results_layout.setContentsMargins(18, 14, 18, 14)
        results_layout.setSpacing(10)

        # Header label for results
        results_label = QLabel("Search Results")
        results_label.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        results_label.setStyleSheet("color: white;")
        results_layout.addWidget(results_label)

        # Scrollable area for results
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setStyleSheet("""
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

        scroll_area.setWidget(scroll_content)
        results_layout.addWidget(scroll_area)

        return frame

    # Function for handling and displaying search results
    def search_handling(self):
        query = self.search_input.text().strip()
        if not query:
            return

        # Show results section
        self.results_frame.setVisible(True)

        # Clear any previous results
        while self.scroll_layout.count():
            child = self.scroll_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        try:
            songs = ytapi.get_song_titles(query)
        except Exception as e:
            print(f"Error fetching songs: {e}")
            return

        if not songs:
            placeholder = QLabel("No results found.")
            placeholder.setFont(QFont("Segoe UI", 12))
            placeholder.setStyleSheet("color: #BBBBBB;")
            placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.scroll_layout.addWidget(placeholder)
            return

        for song in songs:
            song_widget = self.create_song_item(song)
            self.scroll_layout.addWidget(song_widget)

    # Function for creating visualized song item
    def create_song_item(self, song):
        song_widget = QWidget()
        song_layout = QHBoxLayout(song_widget)
        song_layout.setContentsMargins(12, 8, 12, 8)
        song_layout.setSpacing(14)

        # Icon
        icon_label = QLabel("♪")
        icon_label.setFixedSize(48, 48)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_label.setStyleSheet("""
            QLabel {
                background-color: #1DB954;
                border-radius: 6px;
                color: white;
                font-size: 22px;
                font-weight: bold;
            }
        """)

        # Title
        name_label = QLabel(song.get('title'))
        name_label.setFont(QFont("Segoe UI", 14))
        name_label.setStyleSheet("color: white; background-color: transparent;")
        name_label.setWordWrap(False)

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

        song_layout.addWidget(icon_label)
        song_layout.addWidget(name_label, 1)
        song_layout.addWidget(play_btn)

        return song_widget
