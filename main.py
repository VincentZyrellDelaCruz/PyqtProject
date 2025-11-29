import sys
import os

# Configure VLC path before importing any modules that use VLC
os.environ["PYTHON_VLC_MODULE_PATH"] = r"C:\Program Files\VideoLAN\VLC"
os.environ["PATH"] = os.environ["PYTHON_VLC_MODULE_PATH"] + os.pathsep + os.environ["PATH"]

from PyQt6.QtWidgets import QApplication
from controllers.app_controller import AppController

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
