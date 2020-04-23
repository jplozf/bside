#!/usr/bin/env python
# -*- coding: utf-8 -*-
#===============================================================================
#                                                       ____      _     _      
#                                                      | __ ) ___(_) __| | ___ 
#                                                      |  _ \/ __| |/ _` |/ _ \
#                                                      | |_) \__ \ | (_| |  __/
#                                                      |____/|___/_|\__,_|\___|
#                         
#============================================================(C) JPL 2019=======

#-------------------------------------------------------------------------------
# Imports
#-------------------------------------------------------------------------------
import sys
import time
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from mainwindow import MainWindow

import const
import settings

def setTheme(theme):
    app.setStyle('Fusion')
    palette = QPalette()
    try:
        palette.setColor(QPalette.Window, QColor(theme[0]))
        palette.setColor(QPalette.WindowText, QColor(theme[1]))
        palette.setColor(QPalette.Base, QColor(theme[2]))
        palette.setColor(QPalette.AlternateBase, QColor(theme[3]))
        palette.setColor(QPalette.ToolTipBase, QColor(theme[4]))
        palette.setColor(QPalette.ToolTipText, QColor(theme[5]))
        palette.setColor(QPalette.Text, QColor(theme[6]))
        palette.setColor(QPalette.Button, QColor(theme[7]))
        palette.setColor(QPalette.ButtonText, QColor(theme[8]))
        palette.setColor(QPalette.BrightText, QColor(theme[9]))
        palette.setColor(QPalette.Link, QColor(theme[10]))
        palette.setColor(QPalette.Highlight, QColor(theme[11]))
        palette.setColor(QPalette.HighlightedText, QColor(theme[12]))
    except:
        palette.setColor(QPalette.Window, QColor(const.THEME_LIGHT[0]))
        palette.setColor(QPalette.WindowText, QColor(const.THEME_LIGHT[1]))
        palette.setColor(QPalette.Base, QColor(const.THEME_LIGHT[2]))
        palette.setColor(QPalette.AlternateBase, QColor(const.THEME_LIGHT[3]))
        palette.setColor(QPalette.ToolTipBase, QColor(const.THEME_LIGHT[4]))
        palette.setColor(QPalette.ToolTipText, QColor(const.THEME_LIGHT[5]))
        palette.setColor(QPalette.Text, QColor(const.THEME_LIGHT[6]))
        palette.setColor(QPalette.Button, QColor(const.THEME_LIGHT[7]))
        palette.setColor(QPalette.ButtonText, QColor(const.THEME_LIGHT[8]))
        palette.setColor(QPalette.BrightText, QColor(const.THEME_LIGHT[9]))
        palette.setColor(QPalette.Link, QColor(const.THEME_LIGHT[10]))
        palette.setColor(QPalette.Highlight, QColor(const.THEME_LIGHT[11]))
        palette.setColor(QPalette.HighlightedText, QColor(const.THEME_LIGHT[12]))        
    app.setPalette(palette)
    
if __name__ == '__main__':
    currentExitCode = MainWindow.EXIT_CODE_REBOOT
    while currentExitCode == MainWindow.EXIT_CODE_REBOOT:
        # create application     
        sys.argv.append("--disable-web-security")
        app = QApplication(sys.argv)
        app.setOrganizationName(const.ORGANIZATION_NAME)
        app.setOrganizationDomain(const.ORGANIZATION_DOMAIN)    
        app.setApplicationName(const.APPLICATION_NAME)
        
        if settings.db["BSIDE_THEME"] == "LIGHT":
            setTheme(const.THEME_LIGHT)
        elif settings.db["BSIDE_THEME"] == "DARK":
            setTheme(const.THEME_DARK)       
        elif settings.db["BSIDE_THEME"] == "ALTERNATE":
            setTheme(settings.db["THEME_ALTERNATE"])       
        else:
            setTheme(const.THEME_LIGHT)
            
        # set icon
        icon = QIcon("./pix/bside.png")
        app.setWindowIcon(icon)   

        # Create and display the splash screen
        splash_pix = QPixmap('./pix/splash_loading.png')
        splash = QSplashScreen(splash_pix, Qt.WindowStaysOnTopHint)
        splash.setMask(splash_pix.mask())
        splash.show()
        app.processEvents()

        # Simulate something that takes time
        time.sleep(1)

        # create main widget
        w = MainWindow()
        w.setWindowTitle(const.APPLICATION_NAME)
        w.show()
        
        # execute application
        splash.finish(w)
        currentExitCode = app.exec_()
        app = None
