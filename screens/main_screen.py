from PyQt6.QtWidgets import QMainWindow
from PyQt6.QtGui import QIcon
from UI.main_screen_ui import Ui_MainWindow
import config

class MainScreen(QMainWindow):
    def __init__(self, app_controller):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.app_controller = app_controller
        self.init_ui()
        self.connect_signals()

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
        self.ui.burger_icon_2.setIcon(QIcon(config.ICON_PATH + 'burger-bar.png'))

        self.ui.widget_icontexts.setHidden(True)

    def connect_signals(self):
        self.ui.local1.clicked.connect(self.app_controller.goto_local)
        self.ui.local2.clicked.connect(self.app_controller.goto_local)

        self.ui.home1.clicked.connect(self.app_controller.goto_home)
        self.ui.home2.clicked.connect(self.app_controller.goto_home)
