from PyQt6.QtWidgets import QWidget, QLabel, QPushButton, QHBoxLayout, QVBoxLayout, QFrame, QSizePolicy, QScrollArea, QGridLayout
from PyQt6.QtCore import Qt, QSize, QThreadPool, QByteArray
from PyQt6.QtGui import QPixmap, QFont, QIcon
from controllers.game_api_client import fetch_yearly_top_games, fetch_genres, fetch_games_by_genre, fetch_games_sorted
from controllers.clickable import ClickableLabel
from controllers.async_loader import ImageLoader, load_placeholder_pixmap
import os, config, requests
from typing import List

class GameHomeScreen(QWidget):
    def __init__(self, app_controller=None):
        super().__init__()

        self.app_controller = app_controller
        self.genre_labels = []
        self.active_loaders: List[ImageLoader] = []
        self.sort_buttons = {}
        self.current_sort = "recent"
        self.current_genre = {'name': 'Action', 'slug': 'action'}

        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setStyleSheet("background-color: #121212;")

        # Load placeholder once
        self._placeholder = load_placeholder_pixmap()

        # Fetch genres
        try:
            self.game_genres = fetch_genres()
        except:
            self.game_genres = []

        self.init_ui()

    def init_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(24, 24, 24, 24)
        self.main_layout.setSpacing(24)

        # Sort options section
        sort_section = self.create_sort_section()
        self.main_layout.addWidget(sort_section)

        # Games display section (vertical scrolling grid)
        games_section = self.create_games_section()
        self.main_layout.addWidget(games_section, stretch=1)

    def create_sort_section(self):
        """Create sort/filter options section"""
        sort_frame = QFrame()
        sort_frame.setStyleSheet("""
            QFrame {
                background-color: #1E1E1E;
                border-radius: 12px;
            }
        """)

        sort_layout = QHBoxLayout(sort_frame)
        sort_layout.setContentsMargins(18, 14, 18, 14)
        sort_layout.setSpacing(12)

        sort_label = QLabel("Sort by:")
        sort_label.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        sort_label.setStyleSheet("color: white;")
        sort_layout.addWidget(sort_label)

        # Create sort buttons
        self.sort_options = [
            ("Recent", "recent"),
            ("Most Rated", "rating"),
            ("Most Popular", "popular"),
            ("Most Viewed", "views")
        ]
        sort_options = self.sort_options

        for label, sort_key in sort_options:
            btn = QPushButton(label)
            btn.setFixedHeight(40)
            btn.setMinimumWidth(120)
            btn.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #2D2D2D;
                    color: white;
                    border-radius: 8px;
                    padding: 6px 12px;
                    border: 1px solid #444;
                }
                QPushButton:hover {
                    background-color: #383838;
                    border: 1px solid #555;
                }
            """)
            
            # Set initial active state for "Recent"
            if sort_key == "recent":
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #092f94;
                        color: white;
                        border-radius: 8px;
                        padding: 6px 12px;
                        border: 1px solid #0055AA;
                    }
                    QPushButton:hover {
                        background-color: #1177EE;
                        border: 1px solid #1177EE;
                    }
                """)
            
            btn.clicked.connect(lambda checked, key=sort_key: self.on_sort_selected(key, sort_options))
            self.sort_buttons[sort_key] = btn
            sort_layout.addWidget(btn)

        sort_layout.addStretch()

        sort_frame.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        return sort_frame

    def on_sort_selected(self, sort_key, sort_options):
        """Handle sort option selection"""
        self.current_sort = sort_key

        # Find the label for this sort key
        sort_label = "Recent"
        for label, key in self.sort_options:
            if key == sort_key:
                sort_label = label
                break

        # Update results header with sort name
        self.results_label.setText(sort_label)

        # Update button styling
        for key, btn in self.sort_buttons.items():
            if key == sort_key:
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #092f94;
                        color: white;
                        border-radius: 8px;
                        padding: 6px 12px;
                        border: 1px solid #0055AA;
                    }
                    QPushButton:hover {
                        background-color: #1177EE;
                        border: 1px solid #1177EE;
                    }
                """)
            else:
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #2D2D2D;
                        color: white;
                        border-radius: 8px;
                        padding: 6px 12px;
                        border: 1px solid #444;
                    }
                    QPushButton:hover {
                        background-color: #383838;
                        border: 1px solid #555;
                    }
                """)

        # Reload games with new sort
        self.on_genre_selected(self.current_genre)

    def create_genre_section(self):
        """Create genre selection section with vertical scrolling"""
        card_frame = QFrame()
        card_frame.setStyleSheet("""
            QFrame {
                background-color: #1E1E1E;
                border-radius: 12px;
            }
        """)

        card_layout = QVBoxLayout(card_frame)
        card_layout.setContentsMargins(18, 14, 18, 14)
        card_layout.setSpacing(10)

        header_label = QLabel("Select Genre")
        header_label.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        header_label.setStyleSheet("color: white;")
        card_layout.addWidget(header_label)

        # Vertical scroll area for genres
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setFixedHeight(180)

        scroll_area.setStyleSheet("""
            QScrollArea {
                background: transparent;
                border: none;
            }
            QScrollBar:vertical {
                background: #1E1E1E;
                width: 8px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background: #092f94;
                border-radius: 4px;
                min-height: 20px;
            }
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                height: 0;
            }
        """)

        # Scroll widget with vertical layout
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.setContentsMargins(0, 0, 0, 0)
        scroll_layout.setSpacing(8)

        # Create genre buttons/cards
        if self.game_genres:
            for genre in self.game_genres:
                genre_card = self.create_genre_card(genre)
                scroll_layout.addWidget(genre_card)

        scroll_layout.addStretch()
        scroll_area.setWidget(scroll_widget)
        card_layout.addWidget(scroll_area)

        card_frame.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        return card_frame

    def create_genre_card(self, genre):
        """Create a clickable genre card"""
        card = QFrame()
        card.setFixedHeight(50)
        card.setStyleSheet("""
            QFrame {
                background-color: #092f94;
                border-radius: 8px;
                padding: 5px;
            }
            QFrame:hover {
                background-color: #1177EE;
            }
        """)
        card.setCursor(Qt.CursorShape.PointingHandCursor)

        layout = QHBoxLayout(card)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(8)

        title_label = ClickableLabel(genre.get('name', 'Unknown'))
        title_label.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        title_label.setStyleSheet("color: white; background-color: transparent;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        
        # Handle genre selection
        title_label.clicked.connect(lambda g=genre: self.on_genre_selected(g))
        
        layout.addWidget(title_label)
        layout.addStretch()

        return card

    def create_games_section(self):
        """Create games display section with vertical grid"""
        games_frame = QFrame()
        games_frame.setStyleSheet("""
            QFrame {
                background-color: #1E1E1E;
                border-radius: 12px;
            }
        """)
        games_frame.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        results_layout = QVBoxLayout(games_frame)
        results_layout.setContentsMargins(18, 14, 18, 14)
        results_layout.setSpacing(20)

        # Header (will be updated by sort selection)
        self.results_label = QLabel("Recent")
        self.results_label.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        self.results_label.setStyleSheet("color: white;")
        results_layout.addWidget(self.results_label)

        # Scroll area with grid inside
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setStyleSheet('''
            QScrollArea {
                background: transparent;
                border: none;
            }
            QScrollBar:vertical {
                background: #1E1E1E;
                width: 8px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background: #092f94;
                border-radius: 4px;
                min-height: 20px;
            }
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                height: 0;
            }
        ''')

        # Grid container
        scroll_content = QWidget()
        scroll_content.setStyleSheet("background-color: transparent;")

        self.grid_layout = QGridLayout(scroll_content)
        self.grid_layout.setContentsMargins(10, 10, 10, 10)
        self.grid_layout.setHorizontalSpacing(24)
        self.grid_layout.setVerticalSpacing(28)

        scroll_area.setWidget(scroll_content)
        results_layout.addWidget(scroll_area, stretch=1)

        # Load action games by default
        self.on_genre_selected({'name': 'Action', 'slug': 'action'})

        return games_frame

    def on_genre_selected(self, genre):
        """Handle genre selection and load games with current sort"""
        self.current_genre = genre

        # Cancel previous loaders
        for loader in self.active_loaders[:]:
            loader.cancel()
        self.active_loaders.clear()

        # Clear previous grid
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Fetch games by genre with current sort option
        try:
            games = fetch_games_sorted(
                genre_slug=genre.get('slug'),
                sort_by=self.current_sort,
                page_size=20
            )
        except Exception as e:
            print('Error fetching games:', e)
            games = []

        if not games:
            no_results = QLabel("No games found in this genre.")
            no_results.setFont(QFont("Segoe UI", 14))
            no_results.setStyleSheet("color: #BBBBBB;")
            no_results.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.grid_layout.addWidget(no_results, 0, 0, 1, 3)
        else:
            # Display games in a 3-column grid
            for index, game in enumerate(games):
                card = self.create_game_card(game)
                row = index // 3
                col = index % 3
                self.grid_layout.addWidget(card, row, col)

        # Push content to top
        self.grid_layout.setRowStretch(self.grid_layout.rowCount(), 1)

    def create_game_card(self, game):
        card = QFrame()
        card.setFixedSize(250, 320)
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
        image_label.setMinimumWidth(196)
        image_label.setStyleSheet("""
            QLabel {
                background-color: #1a1a1a;
                border-radius: 12px;
            }
        """)
        image_label.setScaledContents(True)

        # Load image asynchronously
        if game.get("background_image"):
            self._async_load_card_image(game["background_image"], image_label)
        else:
            placeholder = self._placeholder.scaled(
                400, 400,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            image_label.setPixmap(placeholder)

        layout.addWidget(image_label)

        # Title
        title = QLabel(game["name"])
        title.setWordWrap(True)
        title.setFont(QFont("Segoe UI", 11, QFont.Weight.DemiBold))
        title.setStyleSheet("color: white;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Rating
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

        # View button
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
            view_btn.clicked.connect(lambda _, gid=game["id"]: self.app_controller.show_game_detail(gid, source=0))

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
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )

            if scaled.width() > scaled.height():
                cropped = scaled.copy((scaled.width() - 156) // 2, 0, 156, 156)
            elif scaled.height() > scaled.width():
                cropped = scaled.copy(0, (scaled.height() - 156) // 2, 156, 156)
            else:
                cropped = scaled

            label.setPixmap(cropped)

        loader = ImageLoader(url)
        loader.signals.finished.connect(on_finished)
        self.active_loaders.append(loader)
        QThreadPool.globalInstance().start(loader)