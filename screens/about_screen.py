from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QFrame,
    QSizePolicy
)
from PyQt6.QtGui import QFont


class AboutScreen(QWidget):
    def __init__(self, app_controller=None):
        super().__init__()
        self.app_controller = app_controller

        # Allow responsive resizing
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        # White background like profile screen
        self.setStyleSheet("AboutScreen { background-color: #F5F5F5; }")

        self.create_about_ui()

    def create_about_ui(self):
        """Main layout structure similar to ProfileScreen"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # 1. About Section Card
        about_card = self.create_about_section()
        main_layout.addWidget(about_card)

        # 2. Developer Section
        dev_card = self.create_developer_section()
        main_layout.addWidget(dev_card)

        # Add stretch to push everything to top
        main_layout.addStretch()

    def create_about_section(self):
        """About description section"""
        card_frame = QFrame()
        card_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 12px;
                padding: 0px;
            }
        """)

        card_layout = QVBoxLayout(card_frame)
        card_layout.setSpacing(0)
        card_layout.setContentsMargins(0, 0, 0, 0)

        # Header
        header_frame = QFrame()
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(18, 14, 18, 8)

        title_label = QLabel("About Music Sync")
        title_label.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        title_label.setStyleSheet("""
            QLabel {
                color: #1A1A1A;
                background-color: transparent;
                letter-spacing: -0.3px;
            }
        """)

        header_layout.addWidget(title_label)
        header_layout.addStretch()
        card_layout.addWidget(header_frame)

        # Content
        content_frame = QFrame()
        content_frame.setStyleSheet("background-color: transparent;")

        content_layout = QVBoxLayout(content_frame)
        content_layout.setSpacing(10)
        content_layout.setContentsMargins(18, 0, 18, 18)

        description = QLabel(
            "Music Sync is a modern music player application designed to provide "
            "seamless playback, lyrics synchronization, and a smooth user experience. "
            "With Music Sync, you can manage your local music library effortlessly "
            "while enjoying a clean, responsive interface built for music lovers."
        )
        description.setWordWrap(True)
        description.setFont(QFont("Segoe UI", 11))
        description.setStyleSheet("""
            QLabel {
                color: #5A5A5A;
                background-color: transparent;
                line-height: 1.4;
            }
        """)
        content_layout.addWidget(description)

        # Version info
        version_label = QLabel("Version 1.0.0  |  © 2025 Music Sync Team")
        version_label.setFont(QFont("Segoe UI", 9))
        version_label.setStyleSheet("color: #999999; background-color: transparent; margin-top: 4px;")
        content_layout.addWidget(version_label)

        card_layout.addWidget(content_frame)
        return card_frame

    def create_developer_section(self):
        """Developer info section"""
        card_frame = QFrame()
        card_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 12px;
                padding: 0px;
            }
        """)

        card_layout = QVBoxLayout(card_frame)
        card_layout.setSpacing(0)
        card_layout.setContentsMargins(0, 0, 0, 0)

        # Header
        header_frame = QFrame()
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(18, 14, 18, 8)

        dev_label = QLabel("Development Team")
        dev_label.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        dev_label.setStyleSheet("""
            QLabel {
                color: #1A1A1A;
                background-color: transparent;
                letter-spacing: -0.3px;
            }
        """)
        header_layout.addWidget(dev_label)
        header_layout.addStretch()
        card_layout.addWidget(header_frame)

        # Content
        content_frame = QFrame()
        content_layout = QVBoxLayout(content_frame)
        content_layout.setSpacing(8)
        content_layout.setContentsMargins(18, 0, 18, 18)

        # Developer list
        names = QLabel(
            "• Student Name 1\n"
            "• Student Name 2\n"
            "• Student Name 3\n"
            "• Student Name 4"
        )
        names.setFont(QFont("Segoe UI", 11))
        names.setStyleSheet("""
            QLabel {
                color: #5A5A5A;
                background-color: transparent;
                line-height: 1.6;
            }
        """)
        content_layout.addWidget(names)

        content_layout.addSpacing(3)
        card_layout.addWidget(content_frame)

        return card_frame
