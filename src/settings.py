#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#===============================================================================
#                                                       ____      _     _
#                                                      | __ ) ___(_) __| | ___
#                                                      |  _ \/ __| |/ _` |/ _ \
#                                                      | |_) \__ \ | (_| |  __/
#                                                      |____/|___/_|\__,_|\___|
#
#============================================================(C) JPL 2019=======

from PyQt5.QtWidgets import QWidget, QGroupBox, QFormLayout, QLabel, QLineEdit, QVBoxLayout, QHBoxLayout, QScrollArea, QSpacerItem, QSizePolicy, QFileDialog, QDialog, QMessageBox
from PyQt5.QtGui import QColor, QPixmap
from PyQt5 import uic
import shelve
import copy

import const
import os
import utils

#-------------------------------------------------------------------------------
# These are the default values
#-------------------------------------------------------------------------------
defaultValues = [
    ['BSIDE_TIMER_STATUS', 3000, "Time delay for displaying message in status bar"],
    ['EDITOR_CODEPAGE', "utf_8", "Default code page for opening files"],
    ['EDITOR_MD_EXTENSIONS', ['tables', 'fenced_code', 'codehilite', 'nl2br'], "Markdown extensions enabled"],
    ['EDITOR_FONT', "Courier", "Editor font's name"],
    ['EDITOR_FONT_SIZE', 12, "Editor font's size"],
    ['EDITOR_COLOR_CHANGED_FILE', "red", "Color of the title's tab when the file is modified"],
    ['EDITOR_BULLET_CHANGED_FILE', False, "Bullet in the title's bar when the file is modified"],
    ['EDITOR_COLOR_BACKGROUND', "#EFE3D9", "Editor background's color"],
    ['EDITOR_COLOR_CURRENT_LINE', "white", "Editor current line background's color"],
    ['EDITOR_RIGHT_MARGIN', True, "Right margin displayed"],
    ['EDITOR_RIGHT_MARGIN_COLUMN', 80, "Right margin place in characters"],
    ['EDITOR_RIGHT_MARGIN_COLOR', "#FFA8A8", "Right margin color"],
    ['EDITOR_LINES_AREA_COLOR', "#E9E8E2", ""],
    ['EDITOR_LINES_NUMBER_COLOR', "black"],
    ['CONSOLE_FONT', "Courier"],
    ['CONSOLE_FONT_SIZE', 12],
    ['CONSOLE_COLOR_BACKGROUND', "#f9f0e1"],
    ['CONSOLE_COLOR_FOREGROUND', "#000000"],
    ['CONSOLE_BANNER', "Hello from BSide"],
    ['CONSOLE_PS1', ">>>"],
    ['CONSOLE_PS2', "..."],
    ['CONSOLE_PACKAGE_INSTALLER', "pip"],
    ['BSIDE_REPOSITORY', "/media/jpl/JPL004/Projets/Python"],
    ['BSIDE_DISPLAY_WELCOME', True, "Display welcome screen on start"],
    ['BSIDE_OPEN_LAST_WORKSPACE', True, "Open the last workspace on start"],
    ['BSIDE_CLOCK_FORMAT', "%a %d/%m/%y %H:%M", "Clock format display"],
    ['BSIDE_PYTHON_HELP_FILE', "python370.chm", "Python help file location"],
    ['BSIDE_TAB_SPACES', 4],
    ['BSIDE_EXIT_CONFIRM', True],
    ['BSIDE_THEME', "LIGHT"],
    ['BSIDE_SAVE_BEFORE_RUN', True],
    ['BSIDE_TIMER_INFO', 5000],
    ['BSIDE_TIMER_REPOSITORY', 10],
    ['BSIDE_SHOW_REPOSITORY', False],
    ['BSIDE_BIG_DISPLAY', False],
    ['BSIDE_BIG_DISPLAY_WIDTH', 25],
    ['BSIDE_BIG_DISPLAY_COLOR', "#ce5408"],
    ['BSIDE_MRU_PROJECTS', 5],
    ['BSIDE_QTDESIGNER_PATH', "/usr/bin/designer"],
    ['BSIDE_MINIMIZE_TO_SYSTEM_TRAY', False],
    ['THEME_ALTERNATE', ["#efefef","#000000","#ffffff","#f7f7f7","#ffffdc","#000000","#000000","#efefef","#000000","#ffffff","#0000ff","#308cc6","#ffffff"]],
    ['TAB_LOW_LEFT_NAMES', True],
    ['TAB_LOW_RIGHT_NAMES', True],
    ['PROJECT_USER_NAME', "Your name"],
    ['PROJECT_MAIL', "yourname@yourcompany.org"],
    ['PROJECT_COMPANY', "YourCompany Ltd"],
    ['PROJECT_SITE', "www.yourcompany.org"],
    ['PROJECT_LICENSE', "gnu-gpl-v3.0"],
    ['PROJECT_DISPLAY_TIME', True],
    ['PROJECT_USE_FOCUS_TIME', True],
    ['BACKUP_PATH', "~/Documents/Backup"],
    ['BACKUP_RETAINS', 5],
    ['BACKUP_ENABLED', True],
    ['PLAYER_A_SMART_PAUSE', False],
    ['PLAYER_V_SMART_PAUSE', True],
    ['PLAYER_A_FOLDER', "~/Music"],
    ['PLAYER_V_FOLDER', "~/Videos"],
    ['HEXEDITOR_HEXA_BACKGROUND', "#CCFFFF"],
    ['HEXEDITOR_TEXT_BACKGROUND', "#CCCCFF"],
    ['HEXEDITOR_FOREGROUND_1', "#506080"],
    ['HEXEDITOR_FOREGROUND_2', "#8D431F"],
    ['HEXEDITOR_HEXA_HIGHLIGHT', "#53868B"],
    ['HEXEDITOR_TEXT_HIGHLIGHT', "#53868B"],
    ['HEXEDITOR_FONT', "Courier"],
    ['SHELL_BANNER', "Hello from BSide"],
    ['SHELL_BACKGROUND', "#000000"],
    ['SHELL_FOREGROUND', "#FFFFFF"],
    ['SHELL_FONT_FAMILY', "Courier"],
    ['SHELL_FONT_SIZE', 10],
    ['SHELL_PROMPT', "=>"],
    ['SHELL_CODEPAGE', "cp850"],
    ['SHELL_UI', "SHELL_QT"],
    ['CONSOLE_UI', "CONSOLE_QT"],
    ['WINDOWS_SHELL_COMMAND', "start c:\\Windows\\system32\\cmd.exe"],
    ['WINDOWS_CONSOLE', "start ipython"],
    ['LINUX_SHELL_RXVT', "urxvt -embed %s"],
    ['LINUX_SHELL_XTERM', "xterm -into %s -geometry 132x48 -maximized"],
    ['LINUX_SHELL_OTHER', "xterm -into %s"],
    ['LINUX_CONSOLE', "xterm -into %s -geometry 132x48 -maximized -e ipython"],
    ['OUTPUT_STYLE', "font: 9pt 'Courier'; background-color: #49453e; color: #ffa500;"],
    ['OUTPUT_TIMESTAMP', "[%Y%m%d-%H%M%S] "],
    ['SYNTAX_PYTHON_KEYWORD', 'brown normal'],
    ['SYNTAX_PYTHON_OPERATOR', 'red normal'],
    ['SYNTAX_PYTHON_BRACE', 'darkgray normal'],
    ['SYNTAX_PYTHON_DEF', 'black bold'],
    ['SYNTAX_PYTHON_CLASS', 'red bold'],
    ['SYNTAX_PYTHON_STRING', '#E8AF30 normal'],
    ['SYNTAX_PYTHON_STRING2', '#E8AF30 normal'],
    ['SYNTAX_PYTHON_COMMENT', '#969696 italic'],
    ['SYNTAX_PYTHON_SELF', '#0066F6 italic'],
    ['SYNTAX_PYTHON_NUMBERS', 'brown normal'],
    ['SYNTAX_PYTHON_DUNDERS', '#0066F6 italic bold'],
    ['FOCUS_FONT_FAMILY', "Courier"],
    ['FOCUS_FONT_SIZE', 10],
    ['FOCUS_FORMAT_DATE', '%d/%m/%Y'],
    ['FOCUS_FORMAT_HOUR', '%H:%M:%S'],
    ['FOCUS_FORMAT_TIMESTAMP', '%d/%m/%Y - %H:%M:%S'],
    ['TODO_AUTORESIZE_NOTE', False],
    ['SQLITE3_FONT', "Courier"],
    ['SQLITE3_FONT_SIZE', 12],
    ['SQLITE3_COLOR_BACKGROUND', "#f9f0e1"],
    ['SQLITE3_COLOR_FOREGROUND', "#000000"],
    ['SQLITE3_PROMPT', "> "],
    ['AWELE_LEVEL_DEFAULT', 3],
    ['AWELE_HUMAN_COLOR_BACKGROUND', "#49453e"],
    ['AWELE_HUMAN_COLOR_FOREGROUND', "orange"],
    ['AWELE_COMPUTER_COLOR_BACKGROUND', "#285179"],
    ['AWELE_COMPUTER_COLOR_FOREGROUND', "#bed4d9"],
    ['AWELE_VERBOSE_MODE', False],
    ['AWELE_LEVEL_SET_OPTIMIZED', True],
    ['WEB_SERVER_PORT', 8086],
    ['WEB_SERVER_ADDRESS', "127.0.0.1"],
    ['WEB_SERVER_ENABLED', True],
    ['WEB_SSL_ENABLED', False],
    ['WEB_SSL_PRIVATE_KEY', "./privkey.pem"],
    ['WEB_SSL_CERTIFICATE', "./certificate.pem"]
]

#-------------------------------------------------------------------------------
# Open config file
#-------------------------------------------------------------------------------
firstTime = False

appDir = os.path.join(os.path.expanduser("~"), const.APP_FOLDER)
if not os.path.exists(appDir):    
    os.makedirs(appDir)
    firstTime = True
dbFileName = os.path.join(os.path.join(appDir, const.CONFIG_FILE))
db = shelve.open(dbFileName, writeback=True)

#-------------------------------------------------------------------------------
# Set default values if they not exists in config file
#-------------------------------------------------------------------------------
for x in defaultValues:
   if not x[0] in db:
      db[x[0]] = x[1]

#-------------------------------------------------------------------------------
# Save config file
#-------------------------------------------------------------------------------
db.sync()

cached_db = shelve.open(os.path.join(os.path.join(appDir, const.CACHED_CONFIG_FILE)))
cached_db.update(copy.deepcopy(dict(db)))
cached_db.close()

#-------------------------------------------------------------------------------
# resetSettings()
#-------------------------------------------------------------------------------
def resetSettings():
    for x in defaultValues:
        db[x[0]] = x[1]
            
#-------------------------------------------------------------------------------
# getSet()
#-------------------------------------------------------------------------------
def getSet(param):
    """
    Return a dict of all parameters beginning by the provided string with their values
    """
    rc = {}
    for x in db:
        if x in (i[0] for i in defaultValues):
            if x.startswith(param) or param == "":
                rc.update({x:db[x]})
    return rc        

#-------------------------------------------------------------------------------
# Class TabSettings
#-------------------------------------------------------------------------------
class TabSettings(QWidget):
#-------------------------------------------------------------------------------
# setFields()
#-------------------------------------------------------------------------------
    def setFields(self):
        self.lblLine01 = QLabel("Timer status")
        self.txtTimerStatus = QTextEdit()

#-------------------------------------------------------------------------------
# __init__()
#-------------------------------------------------------------------------------
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()

#-------------------------------------------------------------------------------
# initUI()
#-------------------------------------------------------------------------------
    def initUI(self):
        self.vLayout = QVBoxLayout()
        self.central = QWidget()
        self.central.setLayout(self.vLayout)

        i = 0
        fields = []
        self.layout = QFormLayout()
        prevKeyword = ""

        self.formGroupBox = QGroupBox("Warning")
        self.formGroupBox.setStyleSheet("font-weight: bold;")
        self.fLayout = QHBoxLayout()
        self.formGroupBox.setLayout(self.fLayout)
        pixLabel = QLabel()
        pixLabel.setPixmap(QPixmap("pix/16x16/Exclamation.png"))
        self.fLayout.addWidget(pixLabel)
        self.fLayout.addWidget(QLabel("Some settings require restarting the IDE to be applied"))
        self.spaceItem = QSpacerItem(150, 10, QSizePolicy.Expanding)
        self.fLayout.addSpacerItem(self.spaceItem)
        self.vLayout.addWidget(self.formGroupBox)

        for key, value in sorted(db.items(), key=lambda kv: kv[0]):
            if key in (i[0] for i in defaultValues):    # don't display obsolete settings removed from defaultValues array
                thisKeyword = key.split('_')[0]
                if thisKeyword != prevKeyword:
                    self.layout = QFormLayout()
                    self.formGroupBox = QGroupBox(thisKeyword)
                    self.formGroupBox.setStyleSheet("font-weight: bold;")
                sValue =  str(value)
                fields.append(list([QLabel(key),QLineEdit(sValue)]))
                fields[i][0].setStyleSheet("font-weight: normal;")
                if sValue[0] == "#" or utils.isColorName(sValue.split()[0]) == True:
                    fields[i][1].setStyleSheet("font-weight: normal; background-color: %s" % sValue.split()[0])
                else:
                    fields[i][1].setStyleSheet("font-weight: normal;")
                self.layout.addRow(fields[i][0], fields[i][1])
                fields[i][1].textChanged.connect(lambda text, label=fields[i][0].text(), x=i: self.lineChanged(label, text, x))
                i = i + 1
                if thisKeyword != prevKeyword:
                    self.formGroupBox.setLayout(self.layout)
                    self.vLayout.addWidget(self.formGroupBox)
                    prevKeyword = thisKeyword

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(self.central)

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(scroll)
        self.setLayout(mainLayout)

#-------------------------------------------------------------------------------
# lineChanged()
#-------------------------------------------------------------------------------
    def lineChanged(self, label, text, i):
        if type(db[label]) is str:
            db[label] = text
        elif type(db[label]) is int:
            db[label] = int(text)
        elif type(db[label]) is float:
            db[label] = float(text)
        elif type(db[label]) is bool:
            if text.lower() == "true":
                db[label] = True
            else:
                db[label] = False
        else:
            db[label] = str(text)

#-------------------------------------------------------------------------------
# fontPicker()
#-------------------------------------------------------------------------------
    def fontPicker(self, event):
        # TODO : Fix the font picker and maybe the saving of this setting
        # TODO : Manage font bold and italic
        font, ok = QFontDialog.getFont(QFont(settings.db['CONSOLE_FONT_FAMILY'], int(settings.db['CONSOLE_FONT_SIZE'])))
        if ok:
            settings.db['CONSOLE_FONT_FAMILY'] = font.family()
            settings.db['CONSOLE_FONT_SIZE'] = str(font.pointSize())
            self.lblConsoleFont.setText(font.family()+ " " + str(font.pointSize()))
            self.lblConsoleFont.setStyleSheet("QWidget {font-family: %s; font-size: %spx}" % (settings.db['CONSOLE_FONT_FAMILY'], settings.db['CONSOLE_FONT_SIZE']))
            self.txtConsoleOut.setStyleSheet("QWidget {background-color: %s; color: %s; font-family: %s; font-size: %spx}" % (settings.db['CONSOLE_BACKGROUND'], settings.db['CONSOLE_FOREGROUND'], settings.db['CONSOLE_FONT_FAMILY'], settings.db['CONSOLE_FONT_SIZE']))

#-------------------------------------------------------------------------------
# colorBackgroundPicker()
#-------------------------------------------------------------------------------
    def colorBackgroundPicker(self, event):
        color = QColorDialog.getColor(QColor(settings.db['CONSOLE_BACKGROUND']))
        if QColor.isValid(color):
            settings.db['CONSOLE_BACKGROUND'] = color.name()
            self.lblConsoleBackgroundColor.setText(settings.db['CONSOLE_BACKGROUND'])
            self.txtConsoleOut.setStyleSheet("QWidget { background-color: %s; color: %s}" % (settings.db['CONSOLE_BACKGROUND'], settings.db['CONSOLE_FOREGROUND']))
            self.lblConsoleForegroundColor.setStyleSheet("QWidget { background-color: %s; color: %s}" % (settings.db['CONSOLE_BACKGROUND'], settings.db['CONSOLE_FOREGROUND']))
            self.lblConsoleBackgroundColor.setStyleSheet("QWidget { background-color: %s; color: %s}" % (settings.db['CONSOLE_BACKGROUND'], settings.db['CONSOLE_FOREGROUND']))

#-------------------------------------------------------------------------------
# colorForegroundPicker()
#-------------------------------------------------------------------------------
    def colorForegroundPicker(self, event):
        color = QColorDialog.getColor(QColor(settings.db['CONSOLE_FOREGROUND']))
        if QColor.isValid(color):
            settings.db['CONSOLE_FOREGROUND'] = color.name()
            self.lblConsoleForegroundColor.setText(settings.db['CONSOLE_FOREGROUND'])
            self.txtConsoleOut.setStyleSheet("QWidget { background-color: %s; color: %s}" % (settings.db['CONSOLE_BACKGROUND'], settings.db['CONSOLE_FOREGROUND']))
            self.lblConsoleForegroundColor.setStyleSheet("QWidget { background-color: %s; color: %s}" % (settings.db['CONSOLE_BACKGROUND'], settings.db['CONSOLE_FOREGROUND']))
            self.lblConsoleBackgroundColor.setStyleSheet("QWidget { background-color: %s; color: %s}" % (settings.db['CONSOLE_BACKGROUND'], settings.db['CONSOLE_FOREGROUND']))

#-------------------------------------------------------------------------------
# resource_path()
# Define function to import external files when using PyInstaller.
# https://stackoverflow.com/questions/37888581/pyinstaller-ui-files-filenotfounderror-errno-2-no-such-file-or-directory
#-------------------------------------------------------------------------------
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    rp = os.path.join(base_path, relative_path)
    # print("RP=%s" % rp)
    return rp

#-------------------------------------------------------------------------------
# class DlgFirstTimeSettings
#-------------------------------------------------------------------------------
class DlgFirstTimeSettings(QDialog):
    
    BROWSE_DIR = 0
    BROWSE_FILE = 1
    
    allParametersSet = False
    
#-------------------------------------------------------------------------------
# __init__()
#-------------------------------------------------------------------------------
    def __init__(self, parent):
        super().__init__(parent)
        uic.loadUi(resource_path('firstTimeWizard.ui'), self)
        
        # Screen #1 User
        self.txt_PROJECT_USER_NAME.setText(db['PROJECT_USER_NAME'])
        self.txt_PROJECT_MAIL.setText(db['PROJECT_MAIL'])
        self.txt_PROJECT_SITE.setText(db['PROJECT_SITE'])
        self.txt_PROJECT_COMPANY.setText(db['PROJECT_COMPANY'])

        # Screen #2 Paths
        self.txt_BSIDE_REPOSITORY.setText(db['BSIDE_REPOSITORY'])
        self.btn_BSIDE_REPOSITORY.clicked.connect(lambda state, browse=self.BROWSE_DIR, field=self.txt_BSIDE_REPOSITORY : self.browseFor(browse, field))
        self.txt_BSIDE_PYTHON_HELP_FILE.setText(db['BSIDE_PYTHON_HELP_FILE'])
        self.btn_BSIDE_PYTHON_HELP_FILE.clicked.connect(lambda state, browse=self.BROWSE_FILE, field=self.txt_BSIDE_PYTHON_HELP_FILE, filt="Help files (*.hlp *.chm *.html);;All files (*)" : self.browseFor(browse, field, None, filt))
        self.txt_BSIDE_QTDESIGNER_PATH.setText(db['BSIDE_QTDESIGNER_PATH'])
        self.btn_BSIDE_QTDESIGNER_PATH.clicked.connect(lambda state, browse=self.BROWSE_FILE, field=self.txt_BSIDE_QTDESIGNER_PATH, filt="All files (*)" : self.browseFor(browse, field, None, filt))
        
        # Screen #3 Backup
        self.chk_BACKUP_ENABLED.setChecked(db['BACKUP_ENABLED'])        
        self.txt_BACKUP_PATH.setText(db['BACKUP_PATH'])
        self.btn_BACKUP_PATH.clicked.connect(lambda state, browse=self.BROWSE_DIR, field=self.txt_BACKUP_PATH : self.browseFor(browse, field))
        self.spn_BACKUP_RETAINS.setValue(db['BACKUP_RETAINS'])
        
        # Screen #4 Web server
        self.chk_WEB_SERVER_ENABLED.setChecked(db['WEB_SERVER_ENABLED'])
        self.txt_WEB_SERVER_ADDRESS.setText(db['WEB_SERVER_ADDRESS'])
        self.spn_WEB_SERVER_PORT.setValue(db['WEB_SERVER_PORT'])
        self.chk_WEB_SSL_ENABLED.setChecked(db['WEB_SSL_ENABLED'])
        self.txt_WEB_SSL_PRIVATE_KEY.setText(db['WEB_SSL_PRIVATE_KEY'])
        self.btn_WEB_SSL_PRIVATE_KEY.clicked.connect(lambda state, browse=self.BROWSE_FILE, field=self.txt_WEB_SSL_PRIVATE_KEY, filt="Private keys (*.pem);;All files (*)" : self.browseFor(browse, field, None, filt))
        self.txt_WEB_SSL_CERTIFICATE.setText(db['WEB_SSL_CERTIFICATE'])
        self.btn_WEB_SSL_CERTIFICATE.clicked.connect(lambda state, browse=self.BROWSE_FILE, field=self.txt_WEB_SSL_CERTIFICATE, filt="Certificates (*.pem);;All files (*)" : self.browseFor(browse, field, None, filt))
        
        # Screen #5 Media
        self.txt_PLAYER_A_FOLDER.setText(db['PLAYER_A_FOLDER'])
        self.btn_PLAYER_A_FOLDER.clicked.connect(lambda state, browse=self.BROWSE_DIR, field=self.txt_PLAYER_A_FOLDER : self.browseFor(browse, field))
        self.txt_PLAYER_V_FOLDER.setText(db['PLAYER_V_FOLDER'])        
        self.btn_PLAYER_V_FOLDER.clicked.connect(lambda state, browse=self.BROWSE_DIR, field=self.txt_PLAYER_V_FOLDER : self.browseFor(browse, field))
        
        # Navigation buttons
        self.btnBack.clicked.connect(self.goBack)
        self.btnNext.clicked.connect(self.goNext)
        self.btnFinish.clicked.connect(self.goFinish)
        self.btnCancel.clicked.connect(self.goCancel)
        self.tabWidget.currentChanged.connect(self.onTabChange)
    
#-------------------------------------------------------------------------------
# browseFor()
#-------------------------------------------------------------------------------
    def browseFor(self, browse, field, path=None, filt=None):
        if path == None:
            path = os.path.expanduser("~")
        if browse == self.BROWSE_DIR:
            fname = QFileDialog.getExistingDirectory(self, "Select Directory", path, QFileDialog.ShowDirsOnly)
            if fname:
                field.setText(fname)
        elif browse == self.BROWSE_FILE:
            fname = QFileDialog.getOpenFileName(self, "Select file", path, filt)
            if fname:
                field.setText(fname[0])

#-------------------------------------------------------------------------------
# goBack()
#-------------------------------------------------------------------------------
    def goBack(self):
        i = self.tabWidget.currentIndex()
        if i > 0:
            self.tabWidget.setCurrentIndex(i - 1)

#-------------------------------------------------------------------------------
# goNext()
#-------------------------------------------------------------------------------
    def goNext(self):
        i = self.tabWidget.currentIndex()
        if i < 4:
            self.tabWidget.setCurrentIndex(i + 1)

#-------------------------------------------------------------------------------
# goFinish()
#-------------------------------------------------------------------------------
    def goFinish(self):
        self.close()

#-------------------------------------------------------------------------------
# goCancel()
#-------------------------------------------------------------------------------
    def goCancel(self):
        self.close()
    
#-------------------------------------------------------------------------------
# onTabChange()
#-------------------------------------------------------------------------------
    def onTabChange(self, i):
        if i == 0:
            self.btnBack.setEnabled(False)
        else:
            self.btnBack.setEnabled(True)
        if i == 4:
            self.btnNext.setEnabled(False)
        else:
            self.btnNext.setEnabled(True)            

#-------------------------------------------------------------------------------
# closeEvent()
#-------------------------------------------------------------------------------
    def closeEvent(self, evnt):
        if self.allParametersSet:
            super(DlgFirstTimeSettings, self).closeEvent(evnt)
        else:
            buttonReply = QMessageBox.question(self, 'First time settings', "All parameters are not set.\nDo you want to close this wizard ?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if buttonReply == QMessageBox.Yes:
                self.validateSettings()
                evnt.accept()
            if buttonReply == QMessageBox.No:
                evnt.ignore()

#-------------------------------------------------------------------------------
# validateSettings()
#-------------------------------------------------------------------------------
    def validateSettings(self):
        # Screen #1 User
        db['PROJECT_USER_NAME'] = self.txt_PROJECT_USER_NAME.text()
        db['PROJECT_MAIL'] = self.txt_PROJECT_MAIL.text()
        db['PROJECT_SITE'] = self.txt_PROJECT_SITE.text()
        db['PROJECT_COMPANY'] = self.txt_PROJECT_COMPANY.text()

        # Screen #2 Paths
        db['BSIDE_REPOSITORY'] = self.txt_BSIDE_REPOSITORY.text()
        db['BSIDE_PYTHON_HELP_FILE'] = self.txt_BSIDE_PYTHON_HELP_FILE.text()
        db['BSIDE_QTDESIGNER_PATH'] = self.txt_BSIDE_QTDESIGNER_PATH.text()
        
        # Screen #3 Backup
        db['BACKUP_ENABLED'] = self.chk_BACKUP_ENABLED.isChecked()
        db['BACKUP_PATH'] = self.txt_BACKUP_PATH.text()
        db['BACKUP_RETAINS'] = self.spn_BACKUP_RETAINS.value()
        
        # Screen #4 Web server
        db['WEB_SERVER_ENABLED'] = self.chk_WEB_SERVER_ENABLED.isChecked()
        db['WEB_SERVER_ADDRESS'] = self.txt_WEB_SERVER_ADDRESS.text()
        db['WEB_SERVER_PORT'] = self.spn_WEB_SERVER_PORT.value()
        db['WEB_SSL_ENABLED'] = self.chk_WEB_SSL_ENABLED.isChecked()
        db['WEB_SSL_PRIVATE_KEY'] = self.txt_WEB_SSL_PRIVATE_KEY.text()
        db['WEB_SSL_CERTIFICATE'] = self.txt_WEB_SSL_CERTIFICATE.text()
        
        # Screen #5 Media
        db['PLAYER_A_FOLDER'] = self.txt_PLAYER_A_FOLDER.text()
        db['PLAYER_V_FOLDER'] = self.txt_PLAYER_V_FOLDER.text()
        
        # Commit
        db.sync()