from PyQt6.QtCore import Qt
from PyQt6.QtGui import QGuiApplication, QIcon
from PyQt6.QtWidgets import QStackedWidget

from screens.main_screen import MainScreen
from screens.startup_screen import StartupScreen
from screens.welcome_screen import WelcomeScreen
from screens.login_screen import LoginScreen
from screens.main_screen import MainScreen
from screens.profile_screen import ProfileScreen
from screens.music_player import MusicPlayer
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

        self.widget.setFixedSize(*config.WINDOW_SIZE)
        self.center_widget()

        self.widget.show()

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

    def goto_about(self):
        self.main.ui.page_label.setText('ABOUT')

        # If the UI actually has an about_page stacked widget, prefer it
        if hasattr(self.main.ui, 'about_page'):
            try:
                # show first page of about_page if available (or index 0)
                self.main.ui.about_page.setCurrentIndex(0)
                return
            except Exception:
                # fall through to try home_stack fallback
                pass

        # Fallback: use the index stored on MainScreen when we added the about widget
        if hasattr(self.main, 'about_widget_index'):
            try:
                self.main.ui.home_stack.setCurrentIndex(self.main.about_widget_index)
                return
            except Exception:
                pass

        # Final fallback: go to home index 0 to avoid crash
        self.main.ui.home_stack.setCurrentIndex(0)

    def goto_profile(self):
        self.main.ui.page_label.setText('USER PROFILE')
        self.main.ui.home_stack.setCurrentIndex(3)

    def open_music_player(self, song_title):
        music_player = MusicPlayer(song_title)
        music_player.exec()

