from PyQt6.QtWidgets import QDialog
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import QTimer
from UI.startup_screen_ui import Ui_Dialog
import config, os

class StartupScreen(QDialog):
    def __init__(self, app_controller):
        super().__init__()
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)

        self.app_controller = app_controller
        self.init_ui()

        QTimer.singleShot(3000, self.app_controller.goto_welcome)

        # self.ui.login_btn.clicked.connect(self.app_controller.goto_login)

    # For customizing outside Qt Designer
    def init_ui(self):
        image_path = os.path.join(config.IMAGE_PATH, "μsic_sync_with_name-removebg.png")

        logo_pixmap = QPixmap(image_path)

        if not logo_pixmap.isNull():
            self.ui.logo.setPixmap(logo_pixmap)
        else:
            print(f"Failed to load image from: {image_path}")