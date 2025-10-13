import sys
import os
from PyQt6.QtWidgets import QApplication, QStackedWidget
from PyQt6.uic import loadUi
from controllers.app_controller import AppController
import config

os.environ["QT_SCALE_FACTOR"] = "1"

def main():
    app = QApplication(sys.argv)

    controller = AppController()

    try:
        sys.exit(app.exec())
    except Exception as e:
        print(f"Application error: {e}")

if __name__ == '__main__':
    main()
