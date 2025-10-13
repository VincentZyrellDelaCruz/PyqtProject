from PyQt6.QtWidgets import QDialog
from UI.signup_screen_ui import Ui_Dialog

class SignupScreen(QDialog):
    def __init__(self, app_controller):
        super().__init__()
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)

        self.app_controller = app_controller
        self.ui.login_btn.clicked.connect(self.app_controller.goto_login)