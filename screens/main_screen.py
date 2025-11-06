from functools import partial
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtWidgets import QMainWindow, QVBoxLayout, QPushButton, QButtonGroup, QScrollArea, QWidget, QSizePolicy
from PyQt6.QtGui import QIcon, QFont, QPixmap
from UI.main_screen_ui import Ui_MainWindow
from screens.home_screen import HomeScreen
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

        self.add_home_page()
        self.add_about_page()
        self.add_profile_page()

    def init_ui(self):
        pixmap1 = QPixmap(config.IMAGE_PATH + 'μsic_sync-removebg.png').scaled(
            150, 150)
        self.ui.logo_1.setPixmap(pixmap1)

        pixmap2 = QPixmap(config.IMAGE_PATH + 'μsic_sync_with_name-removebg.png').scaled(
            200, 100)
        self.ui.logo_2.setPixmap(pixmap2)

        self.ui.home1.setIcon(QIcon(config.ICON_PATH + 'music.png'))
        self.ui.home2.setIcon(QIcon(config.ICON_PATH + 'music.png'))
        self.ui.home1.setChecked(True)
        self.ui.home2.setChecked(True)

        self.ui.genre1.setIcon(QIcon(config.ICON_PATH + 'genre.svg'))
        self.ui.genre2.setIcon(QIcon(config.ICON_PATH + 'genre.svg'))

        self.ui.search1.setIcon(QIcon(config.ICON_PATH + 'search.svg'))
        self.ui.search2.setIcon(QIcon(config.ICON_PATH + 'search.svg'))

        self.ui.local1.setIcon(QIcon(config.ICON_PATH + 'local-play-button.png'))
        self.ui.local2.setIcon(QIcon(config.ICON_PATH + 'local-play-button.png'))

        self.ui.about1.setIcon(QIcon(config.ICON_PATH + 'info.png'))
        self.ui.about2.setIcon(QIcon(config.ICON_PATH + 'info.png'))

        self.ui.user1.setIcon(QIcon(config.ICON_PATH + 'user.png'))
        self.ui.user2.setIcon(QIcon(config.ICON_PATH + 'user.png'))

        self.ui.burger_icon.setIcon(QIcon(config.ICON_PATH + 'burger-bar.png'))

        self.ui.widget_icontexts.setHidden(True)

        self.button_group.setExclusive(True)

    def connect_signals(self):
        self.ui.local1.clicked.connect(self.app_controller.goto_local)
        self.ui.local2.clicked.connect(self.app_controller.goto_local)

        self.ui.home1.clicked.connect(self.app_controller.goto_home)
        self.ui.home2.clicked.connect(self.app_controller.goto_home)

        self.ui.about1.clicked.connect(self.app_controller.goto_about)
        self.ui.about2.clicked.connect(self.app_controller.goto_about)

        self.ui.user1.clicked.connect(self.app_controller.goto_profile)
        self.ui.user2.clicked.connect(self.app_controller.goto_profile)

    def add_home_page(self):
        home_widget = HomeScreen(self.app_controller)

        # Make it expand properly to fill available space
        home_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        home_widget.setMinimumSize(0, 0)
        home_widget.setMaximumSize(16777215, 16777215)

        # Wrap in a scroll area just like profile page
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QScrollArea.Shape.NoFrame)
        scroll_area.setWidget(home_widget)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        # Style the scrollbar (reuse same styling as profile)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: #F5F5F5;
            }
            QScrollBar:vertical {
                border: none;
                background: #E0E0E0;
                width: 10px;
                border-radius: 5px;
                margin: 2px;
            }
            QScrollBar::handle:vertical {
                background: #71C562;
                border-radius: 5px;
                min-height: 40px;
            }
            QScrollBar::handle:vertical:hover {
                background: #5fb052;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)

        # Add to stacked widget (home_stack). Keep track of its index for navigation.
        self.home_widget_index = self.ui.home_stack.addWidget(scroll_area)
        print(self.home_widget_index)

    def add_about_page(self):
        # Create about screen widget
        about_widget = AboutScreen(self.app_controller)

        # Make it expand properly to fill available space
        about_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        about_widget.setMinimumSize(0, 0)
        about_widget.setMaximumSize(16777215, 16777215)

        # Wrap in a scroll area just like profile page
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QScrollArea.Shape.NoFrame)
        scroll_area.setWidget(about_widget)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        # Style the scrollbar (reuse same styling as profile)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: #F5F5F5;
            }
            QScrollBar:vertical {
                border: none;
                background: #E0E0E0;
                width: 10px;
                border-radius: 5px;
                margin: 2px;
            }
            QScrollBar::handle:vertical {
                background: #71C562;
                border-radius: 5px;
                min-height: 40px;
            }
            QScrollBar::handle:vertical:hover {
                background: #5fb052;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)

        # Add to stacked widget (home_stack). Keep track of its index for navigation.
        self.ui.home_stack.addWidget(scroll_area)
        # store index so AppController can navigate reliably
        self.about_widget_index = self.ui.home_stack.count() - 1

    def add_profile_page(self):
        """Add profile screen to the home stack"""
        # Create profile screen widget
        profile_widget = ProfileScreen(self.app_controller)

        # Make it expand properly to fill available space
        profile_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        profile_widget.setMinimumSize(0, 0)
        profile_widget.setMaximumSize(16777215, 16777215)  # Remove fixed size constraints

        # Make it scrollable if it's taller than the screen
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QScrollArea.Shape.NoFrame)
        scroll_area.setWidget(profile_widget)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        # Style the scrollbar
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: #F5F5F5;
            }
            QScrollBar:vertical {
                border: none;
                background: #E0E0E0;
                width: 10px;
                border-radius: 5px;
                margin: 2px;
            }
            QScrollBar::handle:vertical {
                background: #71C562;
                border-radius: 5px;
                min-height: 40px;
            }
            QScrollBar::handle:vertical:hover {
                background: #5fb052;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)

        # Add to stacked widget (this is the content area beside the sidebar)
        self.ui.home_stack.addWidget(scroll_area)
        self.profile_widget_index = self.ui.home_stack.addWidget(scroll_area)
        print(self.profile_widget_index)

    def display_local_playlist(self):
        if self.local_playlist is None:
            return

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
            }
            QScrollArea QWidget {
                background-color: #555;
            }
        """)

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
                QPushButton { 
                    color: #fff; 
                    text-align: left; 
                    background-color: transparent; 
                    padding: 8px 10px;
                    border: none;
                    border-radius: 5px; 
                }
                QPushButton:hover {
                    background-color: #3a3a3a;
                }
                QPushButton:checked {
                    background-color: #1DB954;
                }
                QIcon {
                    border-radius: 5px;
                }
            ''')
            song_btn.clicked.connect(partial(self.app_controller.open_music_player, song_title))

            self.button_group.addButton(song_btn, id=i)
            content_layout.addWidget(song_btn)

        scroll_area.setWidget(content_widget)
        self.ui.list_layout.addWidget(scroll_area)

