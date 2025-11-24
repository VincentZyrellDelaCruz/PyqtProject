from functools import partial
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtWidgets import QMainWindow, QVBoxLayout, QPushButton, QButtonGroup, QScrollArea, QWidget, QSizePolicy
from PyQt6.QtGui import QIcon, QFont, QPixmap
from UI.main_screen_ui import Ui_MainWindow
from screens.artist_screen import ArtistScreen
from screens.game_genre_screen import GameGenreScreen
from screens.game_home_screen import GameHomeScreen
from screens.game_search_screen import GameSearchScreen
from screens.home_screen import HomeScreen
from screens.genre_screen import GenreScreen
from screens.search_screen import SearchScreen
from screens.profile_screen import ProfileScreen
from screens.about_screen import AboutScreen
import config, os
import controllers.music_metadata as metadata
import controllers.api_client as ytapi

class MainScreen(QMainWindow):
    def __init__(self, app_controller):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.button_group = QButtonGroup(self)
        self.local_playlist = sorted(os.listdir(config.LOCAL_MUSIC_PATH))
        self.app_controller = app_controller
        self.init_ui()
        self.connect_signals()
        self.display_local_playlist()
        self.add_music_pages()
        self.add_about_page()
        self.add_profile_page()
        self.add_games_pages()

    def init_ui(self):
        pixmap1 = QPixmap(config.IMAGE_PATH + 'μsic_sync-removebg.png').scaled(150, 150)
        self.ui.logo_1.setPixmap(pixmap1)
        pixmap2 = QPixmap(config.IMAGE_PATH + 'μsic_sync_with_name-removebg.png').scaled(200, 100)
        self.ui.logo_2.setPixmap(pixmap2)

        self.ui.burger_icon.setIcon(QIcon(config.ICON_PATH + 'burger-bar.png'))

        self.ui.music_main.setIcon(QIcon(config.ICON_PATH + 'music.png'))
        self.ui.music_main_text.setIcon(QIcon(config.ICON_PATH + 'music.png'))

        self.ui.movies_main.setIcon(QIcon(config.ICON_PATH + 'movie.svg'))
        self.ui.movies_main_text.setIcon(QIcon(config.ICON_PATH + 'movie.svg'))

        self.ui.games_main.setIcon(QIcon(config.ICON_PATH + 'game.svg'))
        self.ui.games_main_text.setIcon(QIcon(config.ICON_PATH + 'game.svg'))

        self.ui.about1.setIcon(QIcon(config.ICON_PATH + 'info.png'))
        self.ui.about2.setIcon(QIcon(config.ICON_PATH + 'info.png'))

        self.ui.user1.setIcon(QIcon(config.ICON_PATH + 'user.png'))
        self.ui.user2.setIcon(QIcon(config.ICON_PATH + 'user.png'))

        self.ui.widget_icontexts.setHidden(True)

        self.tab_group = QButtonGroup(self)
        self.tab_group.setExclusive(True)
        self.tab_group.addButton(self.ui.tab_home)
        self.tab_group.addButton(self.ui.tab_genre)
        self.tab_group.addButton(self.ui.tab_search)
        self.tab_group.addButton(self.ui.tab_local)

        self.ui.music_main.setChecked(True)
        self.ui.music_main_text.setChecked(True)
        self.ui.home_stack.setCurrentIndex(0)
        self.ui.top_tabs.setVisible(True)

    def connect_signals(self):
        # Music tabs
        self.ui.tab_home.clicked.connect(lambda: self.app_controller.switch_to_music_page(self.ui.tab_home, 1))
        self.ui.tab_genre.clicked.connect(lambda: self.app_controller.switch_to_music_page(self.ui.tab_genre, 2))
        self.ui.tab_search.clicked.connect(lambda: self.app_controller.switch_to_music_page(self.ui.tab_search, 3))
        self.ui.tab_local.clicked.connect(lambda: self.app_controller.switch_to_music_page(self.ui.tab_local, 0))

        # Movie tabs
        self.ui.tab_movie_home.clicked.connect(lambda: self.app_controller.switch_to_movie_page(0))
        self.ui.tab_tvshows.clicked.connect(lambda: self.app_controller.switch_to_movie_page(1))
        self.ui.tab_movies.clicked.connect(lambda: self.app_controller.switch_to_movie_page(2))
        self.ui.tab_movie_genre.clicked.connect(lambda: self.app_controller.switch_to_movie_page(3))
        self.ui.tab_movie_search.clicked.connect(lambda: self.app_controller.switch_to_movie_page(4))

        # Game tabs
        self.ui.tab_game_home.clicked.connect(lambda: self.app_controller.switch_to_game_page(0))
        self.ui.tab_game_genre.clicked.connect(lambda: self.app_controller.switch_to_game_page(1))
        self.ui.tab_game_search.clicked.connect(lambda: self.app_controller.switch_to_game_page(2))

        self.ui.about1.clicked.connect(self.app_controller.goto_about)
        self.ui.about2.clicked.connect(self.app_controller.goto_about)
        self.ui.user1.clicked.connect(self.app_controller.goto_profile)
        self.ui.user2.clicked.connect(self.app_controller.goto_profile)

        # Sidebar section switching
        self.ui.music_main.clicked.connect(self.app_controller.switch_to_music)
        self.ui.music_main_text.clicked.connect(self.app_controller.switch_to_music)
        self.ui.movies_main.clicked.connect(self.app_controller.switch_to_movies)
        self.ui.movies_main_text.clicked.connect(self.app_controller.switch_to_movies)
        self.ui.games_main.clicked.connect(self.app_controller.switch_to_games)
        self.ui.games_main_text.clicked.connect(self.app_controller.switch_to_games)

        self.ui.about1.clicked.connect(lambda: self.ui.top_tabs.setVisible(False))
        self.ui.about2.clicked.connect(lambda: self.ui.top_tabs.setVisible(False))
        self.ui.user1.clicked.connect(lambda: self.ui.top_tabs.setVisible(False))
        self.ui.user2.clicked.connect(lambda: self.ui.top_tabs.setVisible(False))

    def add_page(self, page_widget, stack):
        page_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        page_widget.setMinimumSize(0, 0)
        page_widget.setMaximumSize(16777215, 16777215)
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QScrollArea.Shape.NoFrame)
        scroll_area.setWidget(page_widget)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setStyleSheet("""
            QScrollArea { border: none; background-color: #F5F5F5; }
            QScrollBar:vertical { border: none; background: #E0E0E0; width: 10px; border-radius: 5px; margin: 2px; }
            QScrollBar::handle:vertical { background: #71C562; border-radius: 5px; min-height: 40px; }
            QScrollBar::handle:vertical:hover { background: #5fb052; }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0px; }
        """)
        stack_no = stack.addWidget(scroll_area)
        print(page_widget, stack_no)

    def add_music_pages(self):
        home_widget = HomeScreen(self.app_controller)
        genre_widget = GenreScreen(self.app_controller)
        search_widget = SearchScreen(self.app_controller)

        for widget in [home_widget, genre_widget, search_widget]:
            self.add_page(widget, self.ui.music_stack)

    def add_about_page(self):
        about_widget = AboutScreen(self.app_controller)
        self.add_page(about_widget, self.ui.home_stack)

    def add_profile_page(self):
        profile_widget = ProfileScreen(self.app_controller)
        self.add_page(profile_widget, self.ui.home_stack)

    def add_games_pages(self):
        home_widget = GameHomeScreen(self.app_controller)
        genre_widget = GameGenreScreen(self.app_controller)
        search_widget = GameSearchScreen(self.app_controller)

        for widget in [home_widget, genre_widget, search_widget]:
            self.add_page(widget, self.ui.games_stack)

    def display_local_playlist(self):
        if self.local_playlist is None:
            return
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setStyleSheet("QScrollArea { border: none; } QScrollArea QWidget { background-color: #555; }")
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(6)
        for i, song_title in enumerate(self.local_playlist):
            song_btn = QPushButton(f"{' '*3}{song_title.replace('.mp3', '')}")
            song_btn.setFont(QFont('Arial', 15))
            song_btn.setCheckable(True)
            song_btn.setIcon(QIcon(metadata.get_embedded_image(config.LOCAL_MUSIC_PATH + song_title, square=True)))
            song_btn.setIconSize(QSize(64, 64))
            song_btn.setStyleSheet('''
                QPushButton { color: #fff; text-align: left; background-color: transparent; padding: 8px 10px; border: none; border-radius: 5px; }
                QPushButton:hover { background-color: #3a3a3a; }
                QPushButton:checked { background-color: #1DB954; }
                QIcon { border-radius: 5px; }
            ''')
            song_btn.clicked.connect(partial(self.app_controller.open_music_player, song_title))
            self.button_group.addButton(song_btn, id=i)
            content_layout.addWidget(song_btn)
        scroll_area.setWidget(content_widget)
        self.ui.music_stack.addWidget(scroll_area)