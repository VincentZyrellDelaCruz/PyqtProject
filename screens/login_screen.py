from PyQt6.QtWidgets import QDialog, QWidget, QMessageBox, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QFrame
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QRect
from PyQt6.QtGui import QFont, QPainter, QColor, QPen
from controllers.auth_controller import AuthController

class LoadingSpinner(QWidget):
    """Animated loading spinner widget."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.angle = 0
        self.setFixedSize(40, 40)
        
        # Timer for animation
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.rotate)
        
    def start(self):
        """Start the spinning animation."""
        self.timer.start(30)  # Update every 30ms for smooth animation
        self.show()
        
    def stop(self):
        """Stop the spinning animation."""
        self.timer.stop()
        self.hide()
        
    def rotate(self):
        """Rotate the spinner."""
        self.angle = (self.angle + 10) % 360
        self.update()
        
    def paintEvent(self, event):
        """Draw the spinner."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw spinning arc
        rect = QRect(5, 5, 30, 30)
        pen = QPen(QColor("#27ae60"))
        pen.setWidth(3)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)
        
        painter.drawArc(rect, self.angle * 16, 120 * 16)

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
        
        # Loading overlay (hidden by default)
        self.loading_overlay = QWidget(login_card)
        self.loading_overlay.setGeometry(0, 0, 400, 540)
        self.loading_overlay.setStyleSheet("""
            QWidget {
                background-color: rgba(255, 255, 255, 0.95);
                border-radius: 20px;
            }
        """)
        self.loading_overlay.hide()
        
        overlay_layout = QVBoxLayout(self.loading_overlay)
        overlay_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Loading spinner
        self.spinner = LoadingSpinner()
        spinner_container = QWidget()
        spinner_layout = QHBoxLayout(spinner_container)
        spinner_layout.addStretch()
        spinner_layout.addWidget(self.spinner)
        spinner_layout.addStretch()
        overlay_layout.addWidget(spinner_container)
        
        # Loading text
        self.loading_label = QLabel("Signing in...")
        self.loading_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.loading_label.setFont(QFont("Segoe UI", 12, QFont.Weight.DemiBold))
        self.loading_label.setStyleSheet("color: #27ae60; margin-top: 10px;")
        overlay_layout.addWidget(self.loading_label)
        
        
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
        
        # Show loading overlay
        self.show_loading(True)
        
        # Disable inputs during login
        self.username_input.setEnabled(False)
        self.password_input.setEnabled(False)
        self.login_btn.setEnabled(False)
        
        # Simulate async authentication with a small delay for UX
        QTimer.singleShot(800, lambda: self.perform_authentication(username, password))
    
    def perform_authentication(self, username, password):
        """Perform the actual authentication."""
        # Authenticate
        if self.auth_controller.authenticate(username, password):
            # Login successful - show success message briefly
            self.loading_label.setText("Success! Redirecting...")
            QTimer.singleShot(500, self.login_success)
        else:
            # Login failed
            self.show_loading(False)
            
            # Re-enable inputs
            self.username_input.setEnabled(True)
            self.password_input.setEnabled(True)
            self.login_btn.setEnabled(True)
            
            # Show error message
            QMessageBox.warning(
                self,
                "Login Failed",
                "Invalid username or password.\n\nPlease try again.",
                QMessageBox.StandardButton.Ok
            )
            # Clear password field
            self.password_input.clear()
    
    def login_success(self):
        """Handle successful login."""
        self.show_loading(False)
        self.app_controller.goto_main()
        self.clear_fields()
        
        # Re-enable inputs for next login
        self.username_input.setEnabled(True)
        self.password_input.setEnabled(True)
        self.login_btn.setEnabled(True)
        self.loading_label.setText("Signing in...")
    
    def show_loading(self, show):
        """Show or hide the loading overlay."""
        if show:
            self.loading_overlay.show()
            self.loading_overlay.raise_()
            self.spinner.start()
        else:
            self.spinner.stop()
            self.loading_overlay.hide()
    
    def clear_fields(self):
        """Clear username and password fields - called on logout for security"""
        self.username_input.clear()
        self.password_input.clear()
