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

from PyQt5.QtWidgets import QWidget, QGroupBox, QFormLayout, QLabel, QLineEdit, QVBoxLayout, QHBoxLayout, QScrollArea, QSpacerItem, QSizePolicy
from PyQt5.QtGui import QColor, QPixmap

import shelve
import const
import os
import utils

#-------------------------------------------------------------------------------
# These are the default values
#-------------------------------------------------------------------------------
defaultValues = [ 
    ['BSIDE_TIMER_STATUS', 3000, "Time delay for displaying message in status bar"],    
    ['EDITOR_CODEPAGE', "utf8", "Default code page for opening files"],
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
    ['BSIDE_REPOSITORY', "/media/jpl/JPL004/Projets/Python"],    
    ['BSIDE_DISPLAY_WELCOME', True, "Display welcome screen on start"],
    ['BSIDE_OPEN_LAST_WORKSPACE', True, "Open the last workspace on start"],
    ['BSIDE_CLOCK_FORMAT', "%a %d/%m/%y %H:%M", "Clock format display"],
    ['BSIDE_PYTHON_HELP_FILE', "python370.chm", "Python help file location"],
    ['BSIDE_TAB_SPACES', 4],
    ['BSIDE_THEME', "LIGHT"],
    ['BSIDE_SAVE_BEFORE_RUN', True],
    ['BSIDE_TIMER_INFO', 5000],
    ['BSIDE_TIMER_REPOSITORY', 10],
    ['BSIDE_QTDESIGNER_PATH', "/usr/bin/designer"],    
    ['THEME_ALTERNATE', ["#efefef","#000000","#ffffff","#f7f7f7","#ffffdc","#000000","#000000","#efefef","#000000","#ffffff","#0000ff","#308cc6","#ffffff"]],
    ['TAB_LOW_LEFT_NAMES', True],
    ['TAB_LOW_RIGHT_NAMES', True],
    ['PROJECT_USER_NAME', "Your name"],
    ['PROJECT_MAIL', "yourname@yourcompany.org"],
    ['PROJECT_COMPANY', "YourCompany Ltd"],
    ['PROJECT_SITE', "www.yourcompany.org"],
    ['PROJECT_LICENSE', "gnu-gpl-v3.0"],
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
    ['TODO_AUTORESIZE_NOTE', False]
]

#-------------------------------------------------------------------------------
# Open config file
#-------------------------------------------------------------------------------
appDir = os.path.join(os.path.expanduser("~"), const.APP_FOLDER)
if not os.path.exists(appDir):
    os.makedirs(appDir)
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

#-------------------------------------------------------------------------------
# resetSettings()
#-------------------------------------------------------------------------------
def resetSettings():
    for x in defaultValues:
            db[x[0]] = x[1]    

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
    