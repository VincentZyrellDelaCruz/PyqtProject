from PyQt6.QtWidgets import QDialog
from PyQt6.QtGui import QPixmap
from UI.welcome_screen_ui import Ui_Dialog
import config

class WelcomeScreen(QDialog):
    def __init__(self, app_controller):
        super().__init__()
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)

        self.app_controller = app_controller
        self.init_ui()

        self.ui.login_btn.clicked.connect(self.app_controller.goto_login)

    # For customizing outside Qt Designer
    def init_ui(self):
        import os
        image_path = os.path.join(config.IMAGE_PATH, "reels.jpg")
        print(f"Trying to load image from: {image_path}")
        print(f"Image exists: {os.path.exists(image_path)}")
        
        pixmap = QPixmap(image_path)

        if not pixmap.isNull():
            self.ui.img_label.setPixmap(pixmap)
            self.ui.img_label.setScaledContents(True)
            print("Image loaded successfully!")
        else:
            print(f"Failed to load image from: {image_path}")