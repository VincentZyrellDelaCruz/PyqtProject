from functools import partial
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtWidgets import QMainWindow, QVBoxLayout, QPushButton, QButtonGroup, QScrollArea, QWidget
from PyQt6.QtGui import QIcon, QFont
from UI.main_screen_ui import Ui_MainWindow
import config, os
import controllers.music_metadata as metadata

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

    def init_ui(self):

        self.ui.home1.setIcon(QIcon(config.ICON_PATH + 'music.png'))
        self.ui.home2.setIcon(QIcon(config.ICON_PATH + 'music.png'))

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

