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
        self.widget.setWindowTitle('Spectra Medius')

        icon_path = os.path.join(config.IMAGE_PATH, "logo.png")
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
        self.switch_to_music_page(self.main.ui.tab_home)

    def switch_to_music_page(self, tab, index=1):
        if self.main and hasattr(self.main, "ui"):
            self.main.ui.page_label.setText('MUSIC')
            self.main.ui.home_stack.setCurrentIndex(0)
            tab.setChecked(True)
            self.main.ui.music_stack.setCurrentIndex(index)

    def goto_about(self):
        if self.main and hasattr(self.main, "ui"):
            self.main.ui.page_label.setText('ABOUT')

            self.main.ui.about1.setChecked(True)
            self.main.ui.about2.setChecked(True)

            self.main.ui.home_stack.setCurrentIndex(5)
            self.main.ui.top_tabs.setVisible(False)

    def goto_profile(self):
        if self.main and hasattr(self.main, "ui"):
            self.main.ui.page_label.setText('USER PROFILE')

            self.main.ui.user1.setChecked(True)
            self.main.ui.user2.setChecked(True)

            self.main.ui.home_stack.setCurrentIndex(6)
            self.main.ui.top_tabs.setVisible(False)

    def goto_artist(self, artist):
        if self.main and hasattr(self.main, "ui"):
            music_stack = self.main.ui.music_stack
            if music_stack.count() > 4:
                old = music_stack.widget(4)
                music_stack.removeWidget(old)
                old.deleteLater()
            artist_widget = ArtistScreen(self, artist)
            music_stack.insertWidget(4, artist_widget)
            self.main.ui.home_stack.setCurrentIndex(0)
            music_stack.setCurrentIndex(4)
            self.main.ui.page_label.setText('MUSIC')
            self.main.ui.top_tabs.setVisible(True)

    def goto_playlist(self, browse_id, image):
        if self.main and hasattr(self.main, "ui"):
            music_stack = self.main.ui.music_stack
            if music_stack.count() > 5:
                old = music_stack.widget(5)
                music_stack.removeWidget(old)
                old.deleteLater()
            playlist_widget = PlaylistScreen(self, browse_id, image)
            music_stack.insertWidget(5, playlist_widget)
            self.main.ui.home_stack.setCurrentIndex(0)
            music_stack.setCurrentIndex(5)
            self.main.ui.page_label.setText('MUSIC')
            self.main.ui.top_tabs.setVisible(True)

    def switch_to_music(self):
        self.main.ui.home_stack.setCurrentIndex(0)
        self.main.ui.top_tabs.setVisible(True)

        self.main.ui.widget_icons.setStyleSheet("QWidget {\n"
            " background-color: #71C562;\n"
            " color: white;\n"
            "}\n"
            "\n"
            "QPushButton {\n"
            " border: none;\n"
            " height: 30px;\n"
            " padding-top: 5px;\n"
            " padding-bottom: 5px;\n"
            "}")

        self.main.ui.widget_icontexts.setStyleSheet("QWidget {\n"
                                            " background-color: #71C562;\n"
                                            " color: white;\n"
                                            "}\n"
                                            "QPushButton {\n"
                                            " border: none;\n"
                                            " Con height: 30px;\n"
                                            " padding-top: 5px;\n"
                                            " padding-bottom: 5px;\n"
                                            "}")

        self.main.ui.music_main.setChecked(True)
        self.main.ui.music_main_text.setChecked(True)

        # Show music tabs
        self.main.ui.tab_home.setVisible(True)
        self.main.ui.tab_genre.setVisible(True)
        self.main.ui.tab_search.setVisible(True)
        self.main.ui.tab_local.setVisible(True)

        # Hide movie tabs
        self.main.ui.tab_movie_home.setVisible(False)
        self.main.ui.tab_tvshows.setVisible(False)
        self.main.ui.tab_movies.setVisible(False)
        self.main.ui.tab_movie_genre.setVisible(False)
        self.main.ui.tab_movie_search.setVisible(False)

        self.main.ui.tab_game_home.setVisible(False)
        self.main.ui.tab_game_genre.setVisible(False)
        self.main.ui.tab_game_search.setVisible(False)

        self.main.ui.tab_home.setChecked(True)
        self.main.ui.page_label.setText("MUSIC")

    def switch_to_movies(self):
        self.main.ui.home_stack.setCurrentIndex(1)
        self.main.ui.top_tabs.setVisible(True)

        self.main.ui.widget_icons.setStyleSheet("QWidget {\n"
            " background-color: #E50914;\n"
            " color: white;\n"
            "}\n"
            "\n"
            "QPushButton {\n"
            " border: none;\n"
            " height: 30px;\n"
            " padding-top: 5px;\n"
            " padding-bottom: 5px;\n"
            "}")

        self.main.ui.widget_icontexts.setStyleSheet("QWidget {\n"
                                            " background-color: #E50914;\n"
                                            " color: white;\n"
                                            "}\n"
                                            "QPushButton {\n"
                                            " border: none;\n"
                                            " Con height: 30px;\n"
                                            " padding-top: 5px;\n"
                                            " padding-bottom: 5px;\n"
                                            "}")

        self.main.ui.movies_main.setChecked(True)
        self.main.ui.movies_main_text.setChecked(True)

        # Hide movie tabs
        self.main.ui.tab_home.setVisible(False)
        self.main.ui.tab_genre.setVisible(False)
        self.main.ui.tab_search.setVisible(False)
        self.main.ui.tab_local.setVisible(False)

        # Show movie tabs
        self.main.ui.tab_movie_home.setVisible(True)
        self.main.ui.tab_tvshows.setVisible(True)
        self.main.ui.tab_movies.setVisible(True)
        self.main.ui.tab_movie_genre.setVisible(True)
        self.main.ui.tab_movie_search.setVisible(True)

        self.main.ui.tab_game_home.setVisible(False)
        self.main.ui.tab_game_genre.setVisible(False)
        self.main.ui.tab_game_search.setVisible(False)

        # Ensure only one movie tab is checked (Home by default)
        self.main.ui.tab_movie_home.setChecked(True)
        self.main.ui.page_label.setText("MOVIES")

    def switch_to_games(self):
        self.main.ui.home_stack.setCurrentIndex(2)
        self.main.ui.top_tabs.setVisible(True)

        self.main.ui.widget_icons.setStyleSheet("QWidget {\n"
            " background-color: #092f94;\n"
            " color: white;\n"
            "}\n"
            "\n"
            "QPushButton {\n"
            " border: none;\n"
            " height: 30px;\n"
            " padding-top: 5px;\n"
            " padding-bottom: 5px;\n"
            "}")

        self.main.ui.widget_icontexts.setStyleSheet("QWidget {\n"
                                            " background-color: #092f94;\n"
                                            " color: white;\n"
                                            "}\n"
                                            "QPushButton {\n"
                                            " border: none;\n"
                                            " Con height: 30px;\n"
                                            " padding-top: 5px;\n"
                                            " padding-bottom: 5px;\n"
                                            "}")

        self.main.ui.games_main.setChecked(True)
        self.main.ui.games_main_text.setChecked(True)

        # Hide game tabs
        self.main.ui.tab_home.setVisible(False)
        self.main.ui.tab_genre.setVisible(False)
        self.main.ui.tab_search.setVisible(False)
        self.main.ui.tab_local.setVisible(False)

        # Show game tabs
        self.main.ui.tab_movie_home.setVisible(False)
        self.main.ui.tab_tvshows.setVisible(False)
        self.main.ui.tab_movies.setVisible(False)
        self.main.ui.tab_movie_genre.setVisible(False)
        self.main.ui.tab_movie_search.setVisible(False)

        self.main.ui.tab_game_home.setVisible(True)
        self.main.ui.tab_game_genre.setVisible(True)
        self.main.ui.tab_game_search.setVisible(True)

        # Ensure only one game tab is checked (Home by default)
        self.main.ui.tab_movie_home.setChecked(True)
        self.main.ui.page_label.setText("GAMES")

    def switch_to_movie_page(self, index):
        self.main.ui.movies_stack.setCurrentIndex(index)

    def switch_to_game_page(self, index):
        self.main.ui.games_stack.setCurrentIndex(index)

    def open_music_player(self, song_title):
        music_player = MusicPlayer(song_title)
        music_player.exec()

    def open_api_music_player(self, song):
        print(f"{song['title']} - {song['artist']} ({song['videoId']}) {song['thumbnails']}")
        music_player = ApiMusicPlayer(song)
        music_player.exec()