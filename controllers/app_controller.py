from PyQt6.QtCore import Qt
from PyQt6.QtGui import QGuiApplication, QIcon
from PyQt6.QtWidgets import QStackedWidget

from screens.artist_screen import ArtistScreen
from screens.startup_screen import StartupScreen
from screens.welcome_screen import WelcomeScreen
from screens.login_screen import LoginScreen
from screens.main_screen import MainScreen
from screens.playlist_screen import PlaylistScreen
from screens.music_player import MusicPlayer
from screens.apionly_music_player import ApiMusicPlayer
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
        self.main = None # will be initialized after login

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
        # Load MainScreen dynamically after successful login.
        if self.main is None:
            self.main = MainScreen(self)
            self.widget.addWidget(self.main)

        self.widget.setCurrentWidget(self.main)
        self.goto_home()

    def goto_local(self):
        if self.main and hasattr(self.main, "ui"):
            self.main.ui.page_label.setText('LOCAL PLAY')
            self.main.ui.home_stack.setCurrentIndex(1)

    def goto_home(self):
        if self.main and hasattr(self.main, "ui"):
            self.main.ui.page_label.setText('HOME')
            self.main.ui.home_stack.setCurrentIndex(2)

    def goto_genre(self):
        if self.main and hasattr(self.main, "ui"):
            self.main.ui.page_label.setText('GENRE')
            self.main.ui.home_stack.setCurrentIndex(3)

    def goto_search(self):
        if self.main and hasattr(self.main, "ui"):
            self.main.ui.page_label.setText('SEARCH')
            self.main.ui.home_stack.setCurrentIndex(4)

    def goto_about(self):
        if self.main and hasattr(self.main, "ui"):
            self.main.ui.page_label.setText('ABOUT')
            self.main.ui.home_stack.setCurrentIndex(5)

    def goto_profile(self):
        if self.main and hasattr(self.main, "ui"):
            self.main.ui.page_label.setText('USER PROFILE')
            self.main.ui.home_stack.setCurrentIndex(6)

    def goto_artist(self, artist):
        if self.main and hasattr(self.main, "ui"):

            # If an Artist page already exists at index 7 — remove it
            if self.main.ui.home_stack.count() > 7:
                old = self.main.ui.home_stack.widget(7)
                self.main.ui.home_stack.removeWidget(old)
                old.deleteLater()  # <-- prevents ghosts & leftover async loaders

            # Create and insert fresh ArtistScreen
            artist_widget = ArtistScreen(self, artist)
            self.main.ui.home_stack.insertWidget(7, artist_widget)

            # Show it
            self.main.ui.page_label.setText('ARTIST')
            self.main.ui.home_stack.setCurrentIndex(7)

    def goto_playlist(self, browse_id, image):
        if self.main and hasattr(self.main, "ui"):

            # If a Playlist page already exists at index 8 — remove it
            if self.main.ui.home_stack.count() > 8:
                old = self.main.ui.home_stack.widget(8)
                self.main.ui.home_stack.removeWidget(old)
                old.deleteLater()  # Avoid memory leaks

            # Create and insert fresh PlaylistScreen
            playlist_widget = PlaylistScreen(self, browse_id, image)
            self.main.ui.home_stack.insertWidget(8, playlist_widget)

            # Show it
            self.main.ui.page_label.setText('PLAYLIST')
            self.main.ui.home_stack.setCurrentIndex(8)

    def open_music_player(self, song_title):
        music_player = MusicPlayer(song_title)
        music_player.exec()

    def open_api_music_player(self, song):
        print(f"{song['title']} - {song['artist']} ({song['videoId']}) {song['thumbnails']}")
        music_player = ApiMusicPlayer(song)
        music_player.exec()