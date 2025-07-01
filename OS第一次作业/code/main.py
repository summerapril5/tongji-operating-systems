from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon
import sys, threading

from elevator_ui import *
from elevator_func import *


class main_MyElevator(QtWidgets.QMainWindow, ui_MyElevator):
    def __init__(self):
        super(main_MyElevator, self).__init__()
        self.setupUi(self)
        self.setWindowTitle('MyElevator')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = main_MyElevator()
    window.show()
    sys.exit(app.exec())