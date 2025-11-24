from PyQt6.QtWidgets import QWidget, QLabel, QPushButton, QHBoxLayout, QVBoxLayout, QFrame, QSizePolicy, QScrollArea
from PyQt6.QtCore import Qt, QSize, QThreadPool, QByteArray
from PyQt6.QtGui import QPixmap, QFont, QIcon
from controllers.game_api_client import fetch_yearly_top_games
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
        self._placeholder = load_placeholder_pixmap()

        self.init_ui()

    def init_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(24, 24, 24, 24)
        self.main_layout.setSpacing(24)

        # Top Songs Section
        top_games_section = self.create_top_games_section()
        self.main_layout.addWidget(top_games_section)

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
        header_label = QLabel("Top 10 Games of the Year")
        header_label.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        header_label.setStyleSheet("color: white;")
        container_layout.addWidget(header_label)

        # Scroll Area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setFixedHeight(340)
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
        games = fetch_yearly_top_games() or []

        for game in games:
            song_card = self.create_game_card(game)
            scroll_layout.addWidget(song_card)

        scroll_layout.addStretch()
        scroll_widget.setLayout(scroll_layout)
        scroll_area.setWidget(scroll_widget)
        container_layout.addWidget(scroll_area)

        # Allows expansion so the frame height fits the scroll content nicely
        container.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        return container

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

        # TITLE
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