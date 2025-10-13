from PyQt6.QtGui import QGuiApplication
from PyQt6.QtWidgets import QStackedWidget
from screens.welcome_screen import WelcomeScreen
from screens.login_screen import LoginScreen
from screens.signup_screen import SignupScreen
import config

class AppController:
    def __init__(self):
        self.widget = QStackedWidget()

        self.widget.setWindowTitle('GUI Project')

        self.welcome = WelcomeScreen(self)
        self.login = LoginScreen(self)
        self.signup = SignupScreen(self)

        self.add_widget_stack()

        self.widget.setCurrentWidget(self.welcome)

        self.widget.setFixedSize(*config.WINDOW_SIZE)
        self.center_widget()

        self.widget.show()

    def add_widget_stack(self):
        self.widget.addWidget(self.welcome)
        self.widget.addWidget(self.login)
        self.widget.addWidget(self.signup)

    def center_widget(self):
        screen = QGuiApplication.primaryScreen()
        screen_geometry = screen.availableGeometry()
        x = (screen_geometry.width() - self.widget.width()) // 2
        y = (screen_geometry.height() - self.widget.height()) // 2
        self.widget.move(x, y)

    # Centralized Navigation
    def goto_login(self):
        self.widget.setCurrentWidget(self.login)

    def goto_signup(self):
        self.widget.setCurrentWidget(self.signup)

    def goto_welcome(self):
        self.widget.setCurrentWidget(self.welcome)

