from PyQt6.QtWidgets import (
    QWidget,
    QLabel,
    QPushButton,
    QHBoxLayout,
    QVBoxLayout,
    QFrame,
    QSizePolicy)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QPixmap, QPainter, QPainterPath, QFont, QIcon
import config
import os


class ProfileScreen(QWidget):
    def __init__(self, app_controller=None):
        super().__init__()
        self.app_controller = app_controller

        # Set size policy to expand and fill available space dynamically
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        # Create UI manually (NO Qt Designer)
        self.create_profile_ui()
        self.load_profile_data()

    def create_profile_ui(self):
        """Create the entire profile UI manually"""
        # Set dark background
        self.setStyleSheet("ProfileScreen { background-color: #121212; }")

        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Profile content centered
        content_widget = QWidget()
        content_widget.setStyleSheet("background-color: #121212;")
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        content_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Center container
        center_container = QWidget()
        center_container.setMaximumWidth(600)
        center_layout = QVBoxLayout(center_container)
        center_layout.setSpacing(40)
        center_layout.setContentsMargins(60, 80, 60, 80)

        # Logo
        logo_label = QLabel()
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_path = os.path.join(config.IMAGE_PATH, 'logo.png')
        if os.path.exists(logo_path):
            pixmap = QPixmap(logo_path)
            scaled_pixmap = pixmap.scaled(350, 120, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            logo_label.setPixmap(scaled_pixmap)
        else:
            logo_label.setText("MusicSync")
            logo_label.setFont(QFont("Segoe UI", 36, QFont.Weight.Bold))
            logo_label.setStyleSheet("color: white;")
        center_layout.addWidget(logo_label)

        center_layout.addSpacing(20)

        # Profile Information
        info_container = QWidget()
        info_container.setStyleSheet("""
            QWidget {
                background-color: #1E1E1E;
                border-radius: 12px;
            }
        """)
        info_layout = QVBoxLayout(info_container)
        info_layout.setSpacing(25)
        info_layout.setContentsMargins(50, 50, 50, 50)

        # Username
        username_label = QLabel("Spectra Medius")
        username_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        username_label.setFont(QFont("Segoe UI", 32, QFont.Weight.Bold))
        username_label.setStyleSheet("color: white; background-color: transparent;")
        info_layout.addWidget(username_label)

        # Email
        email_label = QLabel("spectra@medius.com")
        email_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        email_label.setFont(QFont("Segoe UI", 18))
        email_label.setStyleSheet("color: #BBB; background-color: transparent;")
        info_layout.addWidget(email_label)

        info_layout.addSpacing(20)

        # Divider
        divider = QFrame()
        divider.setFrameShape(QFrame.Shape.HLine)
        divider.setStyleSheet("background-color: #333; max-height: 1px;")
        info_layout.addWidget(divider)

        info_layout.addSpacing(10)

        # Additional Info
        role_label = QLabel("Premium Member")
        role_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        role_label.setFont(QFont("Segoe UI", 14))
        role_label.setStyleSheet("color: #1DB954; background-color: transparent; font-weight: bold;")
        info_layout.addWidget(role_label)

        joined_label = QLabel("Member since November 2025")
        joined_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        joined_label.setFont(QFont("Segoe UI", 12))
        joined_label.setStyleSheet("color: #888; background-color: transparent;")
        info_layout.addWidget(joined_label)

        center_layout.addWidget(info_container)

        center_layout.addSpacing(30)

        # Logout button
        logout_btn = QPushButton("Log Out")
        logout_btn.setFixedHeight(50)
        logout_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        logout_btn.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        logout_btn.setStyleSheet("""
            QPushButton {
                background-color: #E50914;
                color: white;
                border: none;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #F40612;
            }
            QPushButton:pressed {
                background-color: #C4070F;
            }
        """)
        logout_btn.clicked.connect(self.logout)
        center_layout.addWidget(logout_btn)

        content_layout.addWidget(center_container, 0, Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(content_widget)

    def create_circular_pixmap(self, pixmap, size):
        """Safely create a circular pixmap from a square one"""
        if pixmap.isNull():
            safe_pixmap = QPixmap(size, size)
            safe_pixmap.fill(Qt.GlobalColor.lightGray)
            pixmap = safe_pixmap

        scaled_pixmap = pixmap.scaled(
            size, size,
            Qt.AspectRatioMode.KeepAspectRatioByExpanding,
            Qt.TransformationMode.SmoothTransformation
        )

        circular = QPixmap(size, size)
        circular.fill(Qt.GlobalColor.transparent)

        painter = QPainter(circular)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        path = QPainterPath()
        path.addEllipse(0, 0, size, size)
        painter.setClipPath(path)

        x = (size - scaled_pixmap.width()) // 2
        y = (size - scaled_pixmap.height()) // 2
        painter.drawPixmap(x, y, scaled_pixmap)
        painter.end()

        return circular

    def load_profile_data(self):
        """Load and display profile data - not needed for simple navigation layout"""
        pass


    def logout(self):
        """Handle logout action - cleanup all resources and close application"""
        if self.app_controller:
            # Clean up main screen resources (stop music, reset state)
            if hasattr(self.app_controller, 'main') and self.app_controller.main:
                self.app_controller.main.cleanup_on_logout()

            # Clear login form fields for security
            if hasattr(self.app_controller, 'login'):
                self.app_controller.login.clear_fields()

            # Close the application completely
            if hasattr(self.app_controller, 'widget'):
                self.app_controller.widget.close()
        else:
            print("Logout clicked")