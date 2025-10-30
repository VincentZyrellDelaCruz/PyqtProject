from PyQt6.QtWidgets import QDialog
from UI.login_screen_ui import Ui_Dialog

class LoginScreen(QDialog):
    def __init__(self, app_controller):
        super().__init__()
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)

        self.app_controller = app_controller
        self.ui.signup_btn.clicked.connect(self.app_controller.goto_signup)
        self.ui.login_btn.clicked.connect(self.app_controller.goto_main)