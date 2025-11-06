from PyQt6.QtWidgets import QDialog, QWidget, QMessageBox, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QFrame
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from controllers.auth_controller import AuthController

class LoginScreen(QWidget):  # Changed from QDialog to QWidget for stacked widget
    def __init__(self, app_controller):
        super().__init__()
        self.app_controller = app_controller
        self.auth_controller = AuthController()
        
        # Create UI manually (NO Qt Designer UI)
        self.create_modern_ui()
    
    def create_modern_ui(self):
        """Create a simple, modern login UI."""
        # Set background gradient for the entire widget
        self.setStyleSheet("""
            QWidget {
                background: qlineargradient(
                    x1:0, y1:0, x2:0, y2:1,
                    stop:0 #e8f5e9,
                    stop:1 #c8e6c9
                );
            }
        """)
        
        # Main layout fills the entire stacked widget area
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Create login card container
        login_card = QFrame()
        login_card.setFixedSize(400, 540)
        login_card.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 20px;
            }
        """)
        login_card.setGraphicsEffect(self.create_shadow())
        
        # Card layout
        card_layout = QVBoxLayout(login_card)
        card_layout.setContentsMargins(45, 50, 45, 45)
        card_layout.setSpacing(0)
        
        # Title
        title = QLabel("Welcome Back")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont("Segoe UI", 32, QFont.Weight.Bold))
        title.setStyleSheet("color: #1e3a2e; margin: 0px; padding: 0px;")
        card_layout.addWidget(title)
        card_layout.addSpacing(12)
        
        # Subtitle
        subtitle = QLabel("Please sign in to continue")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setFont(QFont("Segoe UI", 11))
        subtitle.setStyleSheet("color: #7f8c8d; margin: 0px; padding: 0px;")
        card_layout.addWidget(subtitle)
        card_layout.addSpacing(40)
        
        # Username field
        username_label = QLabel("Username")
        username_label.setFont(QFont("Segoe UI", 10, QFont.Weight.DemiBold))
        username_label.setStyleSheet("color: #2c3e50; margin: 0px; padding: 0px;")
        card_layout.addWidget(username_label)
        card_layout.addSpacing(10)
        
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter your username")
        self.username_input.setFixedHeight(48)
        self.username_input.setFont(QFont("Segoe UI", 11))
        self.username_input.setStyleSheet("""
            QLineEdit {
                padding: 0px 18px;
                border: 2px solid #e0e0e0;
                border-radius: 10px;
                background-color: #fafafa;
                color: #2c3e50;
            }
            QLineEdit:focus {
                border: 2px solid #27ae60;
                background-color: white;
            }
            QLineEdit:hover {
                border: 2px solid #bdc3c7;
            }
        """)
        card_layout.addWidget(self.username_input)
        card_layout.addSpacing(22)
        
        # Password field
        password_label = QLabel("Password")
        password_label.setFont(QFont("Segoe UI", 10, QFont.Weight.DemiBold))
        password_label.setStyleSheet("color: #2c3e50; margin: 0px; padding: 0px;")
        card_layout.addWidget(password_label)
        card_layout.addSpacing(10)
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter your password")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setFixedHeight(48)
        self.password_input.setFont(QFont("Segoe UI", 11))
        self.password_input.setStyleSheet("""
            QLineEdit {
                padding: 0px 18px;
                border: 2px solid #e0e0e0;
                border-radius: 10px;
                background-color: #fafafa;
                color: #2c3e50;
            }
            QLineEdit:focus {
                border: 2px solid #27ae60;
                background-color: white;
            }
            QLineEdit:hover {
                border: 2px solid #bdc3c7;
            }
        """)
        card_layout.addWidget(self.password_input)
        card_layout.addSpacing(40)
        
        # Login button
        self.login_btn = QPushButton("Sign In")
        self.login_btn.setFixedHeight(52)
        self.login_btn.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        self.login_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.login_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                border-radius: 10px;
                padding: 0px;
                letter-spacing: 1px;
            }
            QPushButton:hover {
                background-color: #229954;
            }
            QPushButton:pressed {
                background-color: #1e8449;
            }
        """)
        self.login_btn.clicked.connect(self.handle_login)
        card_layout.addWidget(self.login_btn)
        card_layout.addSpacing(28)
        
        # Info text
        info_label = QLabel("Default: admin / admin123")
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info_label.setFont(QFont("Segoe UI", 9))
        info_label.setStyleSheet("color: #95a5a6;")
        card_layout.addWidget(info_label)
        
        # Center the card in the window both horizontally and vertically
        # Horizontal centering
        h_layout = QHBoxLayout()
        h_layout.addStretch()
        h_layout.addWidget(login_card)
        h_layout.addStretch()
        
        # Vertical centering
        main_layout.addStretch()
        main_layout.addLayout(h_layout)
        main_layout.addStretch()
        
        # Connect Enter key to login
        self.username_input.returnPressed.connect(self.handle_login)
        self.password_input.returnPressed.connect(self.handle_login)
    
    def create_shadow(self):
        """Create a shadow effect for the login card."""
        from PyQt6.QtWidgets import QGraphicsDropShadowEffect
        from PyQt6.QtGui import QColor
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(40)
        shadow.setXOffset(0)
        shadow.setYOffset(8)
        shadow.setColor(QColor(0, 0, 0, 40))
        return shadow
    
    def handle_login(self):
        """Handle login button click with authentication."""
        # Get username and password
        username = self.username_input.text().strip()
        password = self.password_input.text()
        
        # Validate inputs
        if not username or not password:
            QMessageBox.warning(
                self,
                "Missing Information",
                "Please enter both username and password.",
                QMessageBox.StandardButton.Ok
            )
            return
        
        # Authenticate
        if self.auth_controller.authenticate(username, password):
            # Login successful
            self.app_controller.goto_main()
            self.clear_fields()
        else:
            # Login failed - show error message
            QMessageBox.warning(
                self,
                "Login Failed",
                "Invalid username or password.\n\nPlease try again.",
                QMessageBox.StandardButton.Ok
            )
            # Clear password field
            self.password_input.clear()
    
    def clear_fields(self):
        """Clear username and password fields - called on logout for security"""
        self.username_input.clear()
        self.password_input.clear()
