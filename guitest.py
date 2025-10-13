import sys
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *

# IT'S JUST FOR TESTING PURPOSES
# DOESN'T PART OF THE GUI PROJECT
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setGeometry(300, 300, 250, 150)
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Hello PyQt")
        label = QLabel('Hello PyQt', self)
        label.setGeometry(0, 0, 250, 150)

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()