#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PyQt5 import QtWidgets, uic
import sys

class Ui(QtWidgets.QMainWindow):
    def __init__(self):
        super(Ui, self).__init__()
        uic.loadUi('mainwindow.ui', self)

        self.statusbar.showMessage("Good morning Earth", 3000)		

        self.show()

app = QtWidgets.QApplication(sys.argv)
window = Ui()
app.exec_()