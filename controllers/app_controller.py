from PyQt6.QtGui import QGuiApplication, QIcon
from PyQt6.QtWidgets import QStackedWidget
from PyQt6.QtCore import Qt

from screens.main_screen import MainScreen
from screens.startup_screen import StartupScreen
from screens.welcome_screen import WelcomeScreen
from screens.login_screen import LoginScreen

from screens.main_screen import MainScreen
from screens.profile_screen import ProfileScreen
import config, os

class AppController:
    def __init__(self):
        self.widget = QStackedWidget()

        self.widget.setWindowTitle('μsic sync')
        icon_path = os.path.join(config.IMAGE_PATH, "μsic_sync-removebg.png")
        self.widget.setWindowIcon(QIcon(icon_path))
        
        # Set window flags for proper desktop app behavior
        self.widget.setWindowFlags(Qt.WindowType.Window)
        
        # Enable window controls (minimize, maximize, close)
        self.widget.setWindowFlags(
            Qt.WindowType.Window |
            Qt.WindowType.WindowMinimizeButtonHint |
            Qt.WindowType.WindowMaximizeButtonHint |
            Qt.WindowType.WindowCloseButtonHint
        )

        self.startup = StartupScreen(self)
        self.welcome = WelcomeScreen(self)
        self.login = LoginScreen(self)
        # Removed signup screen - no registration needed
        self.main = MainScreen(self)

        self.add_widget_stack()

        # Start on startup screen
        self.widget.setCurrentWidget(self.startup)

        # Set minimum and initial size for proper desktop app behavior
        self.widget.setMinimumSize(1024, 768)  # Minimum usable size
        self.widget.resize(1200, 800)  # Good default size that shows all controls
        
        self.center_widget()
        
        # Show window normally (not maximized) so controls are visible
        self.widget.showMaximized()

    def add_widget_stack(self):
        self.widget.addWidget(self.startup)
        self.widget.addWidget(self.welcome)
        self.widget.addWidget(self.login)
        # Removed signup widget - no registration needed
        self.widget.addWidget(self.main)

    def center_widget(self):
        screen = QGuiApplication.primaryScreen()
        screen_geometry = screen.availableGeometry()
        x = (screen_geometry.width() - self.widget.width()) // 2
        y = (screen_geometry.height() - self.widget.height()) // 2
        self.widget.move(x, y)

    # Centralized Navigation
    def goto_login(self):
        self.widget.setCurrentWidget(self.login)

    # Removed goto_signup method - no registration needed

    def goto_welcome(self):
        self.widget.setCurrentWidget(self.welcome)

    def goto_main(self):
        self.widget.setCurrentWidget(self.main)

    def goto_local(self):
        self.main.ui.page_label.setText('LOCAL PLAY')
        self.main.ui.home_stack.setCurrentIndex(1)

    def goto_home(self):
        self.main.ui.page_label.setText('HOME')
        self.main.ui.home_stack.setCurrentIndex(0)

    def goto_profile(self):
        self.main.ui.page_label.setText('USER PROFILE')
        self.main.ui.home_stack.setCurrentIndex(2)

    def open_music_player(self, song_title):
        # Instead of opening a popup dialog, show music player in main screen
        self.main.show_music_player(song_title)
        self.main.ui.page_label.setText('NOW PLAYING')
        self.main.ui.home_stack.setCurrentIndex(3)

