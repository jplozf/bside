#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PyQt5.QtGui import QWidget, QApplication
from PyQt5.uic import loadUi as load_ui_widget

class PyQtApplication(QApplication):
    def __init__(self, **kwargs):
        super(PyQtApplication, self).__init__([], **kwargs)

    def start(self):
        self.exec_()


class PyQtWidget(QWidget):
    def __init__(self):
        super(PyQtWidget, self).__init__()
        load_ui_widget("mainwindow.ui", self)
        self.setWindowTitle("PyQt Application")
        self.show()

if __name__ == "__main__":
    app = PyQtApplication()
    widget = PyQtWidget()
    app.start()
