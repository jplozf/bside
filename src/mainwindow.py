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
from PyQt5 import uic
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import os
import platform
import sys
import subprocess
import datetime
import psutil
import pickle
import datetime
# import vlc
from os.path import expanduser
from os import path
import sqlite3
import time

import settings
import const
import helpme
import editor
import utils
import dialog
import projects
import mediaPlayer
import pynter
import shell
import backup
import QHexEditor
import scratch
import workspace
import pyinstall
import sqlinter
import tools
import todomgr
import lorem
import toolsbase64
import shrealding

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

    return os.path.join(base_path, relative_path)

#-------------------------------------------------------------------------------
# Class MainWindow
#-------------------------------------------------------------------------------
class MainWindow(QMainWindow):
    EXIT_CODE_REBOOT = -123
    HAS_FOCUS = 0
    HAS_NOT_FOCUS = 1
    appDir = ""
    noname = 0
    nopyth = 0
    noshell = 0
    CurrentOS = platform.system()
    CurrentDrive = os.path.splitdrive(os.path.realpath(__file__))[0]
    CurrentDir = os.path.splitdrive(os.path.dirname(os.path.realpath(__file__)))[1]
    aCommands = []
    iCommands = 0
    fullSplitHorizontal = False
    fullSplitVertical = False
    sizesHorizontal = []
    sizesVertical = []
    aSQL = []
    iSQL = 0
    tools = []
    lastBackup = datetime.datetime(1970,1,1,0,0)    
    lastProject = None
    debug = False
    tick = 0
    bgJob = 0
    SQLDatabase = ":memory:"
    timeNoFocus = 0
    timeNoFocus1 = 0
    timeNoFocus2 = 0
    focusState = HAS_FOCUS
    previousFocusState = HAS_FOCUS
    aAlarms = []
    
#-------------------------------------------------------------------------------
# __init__()
#-------------------------------------------------------------------------------
    def __init__(self, parent = None):
        QMainWindow.__init__( self, parent )
        uic.loadUi(resource_path('mainwindow.ui'), self)
        
        self.appDir = os.path.join(os.path.expanduser("~"), const.APP_FOLDER)
        if not os.path.exists(self.appDir):
            os.makedirs(self.appDir)
        
        self.dbTODO = sqlite3.connect(os.path.join(self.appDir, const.TODO_DATABASE))
        self.curTODO = self.dbTODO.cursor()
        
        self.dbSQLDatabase = sqlite3.connect(self.SQLDatabase)
        self.curSQLDatabase = self.dbSQLDatabase.cursor()

        # self.project = projects.Project(parent = self)
        self.project = None
        self.todoManager = todomgr.TodoManager(parent = self)
        
        self.clipboardFull = False
        self.tabNames = {}
        self.bgColor = "#ffffff"
        self.fgColor = "#000000"
        
        self.actionQuit.triggered.connect(self.close)
        self.actionNewPythonFile.triggered.connect(self.newPythonFile)
        self.actionOpenFile.triggered.connect(self.openFile)
        self.actionSave.triggered.connect(self.saveFile)
        self.actionSaveAll.triggered.connect(self.saveAll)
        self.actionClose.triggered.connect(self.closeFile)
        self.actionCloseAll.triggered.connect(self.closeAll)
        self.actionSettings.triggered.connect(self.settings)
        self.actionAbout.triggered.connect(self.about)
        self.actionNewProject.triggered.connect(self.newProject)
        self.actionOpenProject.triggered.connect(self.openProject)
        self.actionCloseProject.triggered.connect(self.closeProject)
        self.actionPythonConsole.triggered.connect(self.newPynter)
        self.actionShell.triggered.connect(self.newShell)
        self.actionRunScript.triggered.connect(self.runScript)
        self.actionShowFullScreen.triggered.connect(self.switchFullScreen)
        self.actionPythonHelp.triggered.connect(self.helpPython)
        self.actionScratchFile.triggered.connect(self.scratchFile)
        self.actionPackages.triggered.connect(self.doPackagesAction)
        self.actionWelcome.triggered.connect(self.welcome)
        self.actionAddTools.triggered.connect(lambda x, mw=self : tools.manageTools(mw))
        self.actionSplitHorizontal.triggered.connect(self.splitHorizontalResize)
        self.actionSplitVertical.triggered.connect(self.splitVerticalResize)        
        
        self.txtBackgroundColor.setText(self.bgColor)
        self.txtForegroundColor.setText(self.fgColor)
        self.btnBackgroundColor.clicked.connect(self.colorBackgroundPicker)
        self.btnForegroundColor.clicked.connect(self.colorForegroundPicker)
        self.btnSwapColors.clicked.connect(self.swapColors)
               
        self.btnExportOutput.clicked.connect(self.outputExport)
        self.btnClearOutput.clicked.connect(self.outputClear)
        self.btnKillProcess.clicked.connect(self.killProcess)
        self.btnKillProcess.setEnabled(False)
        
        self.tbwHighRight.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tbwHighRight.customContextMenuRequested.connect(self.openContextMenu)        
        self.tbwHighRight.setTabsClosable(True)
        self.tbwHighRight.tabCloseRequested.connect(self.closeTabFromIndex)
        self.tbwHighRight.currentChanged.connect(self.tabChange)
        
        self.tvwModel = QFileSystemModel()
        self.tvwModel.setRootPath(settings.db['BSIDE_REPOSITORY'])   
        self.tvwModel.setIconProvider(IconProvider())
        self.tvwRepository.setModel(self.tvwModel)        
        self.tvwRepository.setRootIndex(self.tvwModel.index(settings.db['BSIDE_REPOSITORY']))
        self.tvwRepository.setAnimated(False)
        self.tvwRepository.setIndentation(10)
        self.tvwRepository.setSortingEnabled(True)        
        for i in range(1, self.tvwRepository.header().length()):
            self.tvwRepository.hideColumn(i)
        self.tvwRepository.sortByColumn(0, Qt.AscendingOrder)
        self.tvwRepository.setContextMenuPolicy(Qt.CustomContextMenu)        
        self.tvwRepository.customContextMenuRequested.connect(self.menuContextTree)
        self.tvwRepository.clicked.connect(self.clickedTreeView)        
        self.tvwRepository.doubleClicked.connect(self.doubleClickedTreeView)        
        
        self.tvmProject = QFileSystemModel()
        self.tvmProject.setIconProvider(IconProvider())        
        self.tvwProject.setContextMenuPolicy(Qt.CustomContextMenu)        
        self.tvwProject.customContextMenuRequested.connect(self.menuContextProject)
        self.tvwProject.clicked.connect(self.clickedProject)        
        self.tvwProject.doubleClicked.connect(self.doubleClickedProject)        
        self.btnProjectExport.clicked.connect(self.doExportProject)
        self.btnProjectClose.clicked.connect(self.closeProject)
        self.btnProjectProperties.clicked.connect(self.doProjectPropertiesAction)
        self.tvwProject.setModel(None)
        
        self.movieWidget = mediaPlayer.MovieWidget()
        self.tabVideoSplitter.addWidget(self.movieWidget)
        self.tbwLowRight.currentChanged.connect(self.onChangeLowRight)
        
        # self.txtFocus.textChanged.connect(self.changeFocusText)
        self.txtFocus.installEventFilter(self)
        self.txtFocus.setStyleSheet("QWidget {font-family: %s; font-size: %spx}" % (settings.db['FOCUS_FONT_FAMILY'], settings.db['FOCUS_FONT_SIZE']))
        
        self.btnBuildEXE.clicked.connect(self.doBuildEXE)
        self.lblRCBuild.setFont(QFont('Courier', 10))
        self.lblTimeBuild.setFont(QFont('Courier', 10))
        self.btnBrowseMainFile.clicked.connect(lambda: pyinstall.browseMainFile(self))
        self.btnRunEXE.clicked.connect(lambda: pyinstall.runEXE(self))
        
        lorem.initFormLorem(self)
        
        pyinstall.initFormEXE(self)
        
        sqlinter.initFormSQL(self)
        
        toolsbase64.initBase64(self)
        
        self.setTabsText(self.tbwLowLeft, settings.db['TAB_LOW_LEFT_NAMES'])
        self.setTabsText(self.tbwLowRight, settings.db['TAB_LOW_RIGHT_NAMES'])
                
        self.tblSearch.clicked.connect(self.clickedSearchLine)
        self.clearTableSearch()
        self.tblSearch.horizontalHeader().setStretchLastSection(True)
        
        self.tblStructure.clicked.connect(self.clickedStructure)
        self.clearTableStructure()
        self.tblStructure.horizontalHeader().setStretchLastSection(True)
        self.btnSortByLine.clicked.connect(self.doSortByLine)
        self.btnSortByType.clicked.connect(self.doSortByType)
        self.btnSortByAlpha.clicked.connect(self.doSortByAlpha)

        self.tblActions.clicked.connect(self.clickedActions)
        self.clearTableActions()
        self.tblActions.horizontalHeader().setStretchLastSection(True)

        if settings.db['BSIDE_SHOW_REPOSITORY']:
            self.lblRepositoryIcon = QLabel()
            self.lblRepositoryIcon.setPixmap(QPixmap("pix/16x16/Home.png"))
            self.statusBar.addPermanentWidget(self.lblRepositoryIcon)
        self.lblRepository = QLabel()
        self.statusBar.addPermanentWidget(self.lblRepository)             
        
        self.lblPythonVersionIcon = QLabel()
        self.lblPythonVersionIcon.setPixmap(QPixmap("pix/icons/python2.5.png"))
        self.lblPythonVersion = QLabel(platform.python_version())
        self.statusBar.addPermanentWidget(self.lblPythonVersionIcon)
        self.statusBar.addPermanentWidget(self.lblPythonVersion)
        
        self.lblProjectIcon = QLabel()
        self.lblProjectIcon.setPixmap(QPixmap("pix/16x16/My Documents.png"))
        self.lblProject = QLabel(const.PROJECT_NONE)
        self.statusBar.addPermanentWidget(self.lblProjectIcon)
        self.statusBar.addPermanentWidget(self.lblProject)

        self.lblMemoryIcon = QLabel()
        self.lblMemoryIcon.setPixmap(QPixmap("pix/16x16/Stats.png"))
        self.lblMemory = QLabel()
        self.statusBar.addPermanentWidget(self.lblMemoryIcon)
        self.statusBar.addPermanentWidget(self.lblMemory)

        self.lblClockIcon = QLabel()
        self.lblClockIcon.setPixmap(QPixmap("pix/16x16/Clock.png"))
        self.lblClock = QLabel()
        self.statusBar.addPermanentWidget(self.lblClockIcon)
        self.statusBar.addPermanentWidget(self.lblClock)
        
        self.lblClockWake = QLabel()
        self.lblClockWake.setPixmap(QPixmap("pix/silk/icons/clock_gray.png"))
        self.lblClockWake.mousePressEvent = self.doClockWake
        self.lblClockTimer = QLabel()
        self.lblClockTimer.setPixmap(QPixmap("pix/silk/icons/time_gray.png"))
        self.lblClockTimer.mousePressEvent = self.doClockTimer
        self.lblClockWatch = QLabel()
        self.lblClockWatch.setPixmap(QPixmap("pix/silk/icons/hourglass_gray.png"))
        self.lblClockWatch.mousePressEvent = self.doClockWatch
        self.statusBar.addPermanentWidget(self.lblClockWake)
        self.statusBar.addPermanentWidget(self.lblClockTimer)
        self.statusBar.addPermanentWidget(self.lblClockWatch)
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.timerCount)
        self.timer.start(settings.db['BSIDE_TIMER_INFO'])
        
        self.txtOutput.setStyleSheet(settings.db['OUTPUT_STYLE'])
        self.txtOutput.setReadOnly(True)
        self.chkVerboseOutput.stateChanged.connect(self.verboseOutputChanged)

        self.lblProjectName.setText(const.PROJECT_NONE)
        self.lblProjectStatus.setText("N/A")
        self.lblFocusMode.setPixmap(QPixmap("pix/16x16/Clock_gray.png"))

        self.restoreSettings()
        # self.btnSaveSettings.clicked.connect(self.backupSettings)
        # self.btnCancelSettings.clicked.connect(self.cancelSettings)
        tools.initMenuTools(self)
        
        focusFileName = os.path.join(os.path.join(self.appDir, const.FOCUS_FILE))
        with open(focusFileName, 'r') as focusFile:
            self.txtFocus.setPlainText(str(focusFile.read()))
        
        if settings.db['BSIDE_OPEN_LAST_WORKSPACE'] == True:
            self.showMessage("Restoring workspace")
            db = workspace.restoreWorkspace()
            if db["PROJECT"] is not None:
                self.tvwProject.setModel(self.tvmProject)
                self.tvwProject.setAnimated(False)
                self.tvwProject.setIndentation(10)
                self.tvwProject.setSortingEnabled(True)        
                for i in range(1, self.tvwProject.header().length()):
                    self.tvwProject.hideColumn(i)
                self.tvwProject.sortByColumn(0, Qt.AscendingOrder)                
                self.project = projects.Project(parent = self)
                self.project.set(db["PROJECT"])
                if self.project.open(raw=True):
                    tabs = db["TABS"]
                    for i in range(len(tabs)):
                        print(tabs[i])
                        if tabs[i][0] == "Welcome":
                            self.welcome()
                        elif tabs[i][0] == "Settings":
                            self.settings()
                        elif tabs[i][0] == "WEditor":
                            self.doEditFile(tabs[i][1])
                        elif tabs[i][0] == "WMarkdown":
                            self.doEditFile(tabs[i][1])
                        elif tabs[i][0] == "WHexedit":
                            self.doEditFile(tabs[i][1], syntax="binary")
                        elif tabs[i][0] == "WXInter" or tabs[i][0] == "LXInter" or tabs[i][0] == "WInter":
                            self.newPynter()
                        elif tabs[i][0] == "WXShell" or tabs[i][0] == "LXShell" or tabs[i][0] == "WShell":
                            self.newShell()
                        elif tabs[i][0] == "TabPIP":
                            self.doPackagesAction()
                        elif tabs[i][0] == "Help":
                            self.about()
                self.tbwHighRight.setCurrentIndex(db["CURRENT_TAB"])
                self.tbwLowRight.setCurrentIndex(db["CURRENT_LOW_TAB"])
        else:
            if settings.db['BSIDE_DISPLAY_WELCOME'] == True:
                self.welcome()
            self.tbwHighRight.setCurrentIndex(0) 
            
#-------------------------------------------------------------------------------
# splitHorizontalResize()
#-------------------------------------------------------------------------------
    def splitHorizontalResize(self):
        if self.fullSplitHorizontal == False:
            self.sizesHorizontal = self.rightSplitter.sizes()
            szTotal = self.sizesHorizontal[0] + self.sizesHorizontal[1]
            sz0 = int(szTotal)
            sz1 = int(0)
            szSplitter = [sz0, sz1]
            self.rightSplitter.setSizes(szSplitter)
            self.fullSplitHorizontal = True
        else:
            self.rightSplitter.setSizes(self.sizesHorizontal)
            self.fullSplitHorizontal = False
    
#-------------------------------------------------------------------------------
# splitVerticalResize()
#-------------------------------------------------------------------------------
    def splitVerticalResize(self):
        if self.fullSplitVertical == False:
            self.sizesVertical = self.mainSplitter.sizes()
            szTotal = self.sizesVertical[0] + self.sizesVertical[1]
            sz1 = int(szTotal)
            sz0 = int(0)
            szSplitter = [sz0, sz1]
            self.mainSplitter.setSizes(szSplitter)
            self.fullSplitVertical = True
        else:
            self.mainSplitter.setSizes(self.sizesVertical)
            self.fullSplitVertical = False

#-------------------------------------------------------------------------------
# doClockWake()
#-------------------------------------------------------------------------------
    def doClockWake(self, event):
        self.showMessage("WAKE")       

#-------------------------------------------------------------------------------
# doClockTimer()
#-------------------------------------------------------------------------------
    def doClockTimer(self, event):
        self.showMessage("TIMER")       

#-------------------------------------------------------------------------------
# doClockWatch()
#-------------------------------------------------------------------------------
    def doClockWatch(self, event):
        self.showMessage("WATCH")       

#-------------------------------------------------------------------------------
# eventFilter()
#-------------------------------------------------------------------------------
    def eventFilter(self, source, event):
        if source == self.txtFocus and event.type() == QEvent.KeyPress:
            key = event.key()
            modifiers = QGuiApplication.queryKeyboardModifiers()
            if key == Qt.Key_D and modifiers == (Qt.ControlModifier | Qt.ShiftModifier):
                today = datetime.datetime.now()
                self.txtFocus.insertPlainText(today.strftime(settings.db['FOCUS_FORMAT_DATE']))
            if key == Qt.Key_H and modifiers == (Qt.ControlModifier | Qt.ShiftModifier):
                today = datetime.datetime.now()
                self.txtFocus.insertPlainText(today.strftime(settings.db['FOCUS_FORMAT_HOUR']))
            if key == Qt.Key_T and modifiers == (Qt.ControlModifier | Qt.ShiftModifier):
                today = datetime.datetime.now()
                self.txtFocus.insertPlainText(today.strftime(settings.db['FOCUS_FORMAT_TIMESTAMP']))
        if source is self.txtSQLInput and event.type() == event.KeyPress:
            key = event.key()
            if key == Qt.Key_Up:
                if self.aSQL:
                    if self.iSQL > 0:
                        self.iSQL = self.iSQL - 1
                    else:
                        self.iSQL = len(self.aSQL) - 1
                    self.txtSQLInput.setText(self.aSQL[self.iSQL])
            elif key == Qt.Key_Down:
                if self.aSQL:
                    if self.iSQL < (len(self.aSQL) - 1):
                        self.iSQL = self.iSQL + 1
                    else:
                        self.iSQL = 0
                    self.txtSQLInput.setText(self.aSQL[self.iSQL])
                
        return QWidget.eventFilter(self, source, event)

#-------------------------------------------------------------------------------
# timerCount()
#-------------------------------------------------------------------------------
    def timerCount(self):
        process = psutil.Process(os.getpid())                
        self.lblMemory.setText("{:.1f}".format(process.memory_info().rss/1024/1024) + " MB ")
        
        if self.project is not None:
            if QApplication.activeWindow() == self:
                self.focusState = self.HAS_FOCUS
                if self.previousFocusState == self.HAS_NOT_FOCUS:
                    self.timeNoFocus2 = time.time()
                    self.timeNoFocus = self.timeNoFocus + (self.timeNoFocus2 - self.timeNoFocus1)
                    self.previousFocusState = self.HAS_FOCUS
                self.lblFocusMode.setPixmap(QPixmap("pix/16x16/Clock.png"))
                # self.setWindowOpacity(1.0)
            else:
                self.focusState = self.HAS_NOT_FOCUS
                if self.previousFocusState == self.HAS_FOCUS:
                    self.timeNoFocus1 = time.time()
                    self.previousFocusState = self.HAS_NOT_FOCUS
                self.lblFocusMode.setPixmap(QPixmap("pix/16x16/Clock_gray.png"))
                # self.setWindowOpacity(0.75)
        else:
            self.lblFocusMode.setPixmap(QPixmap("pix/16x16/Clock_gray.png"))
        
        if self.bgJob == 0 and settings.db['BSIDE_SHOW_REPOSITORY']:
            self.tick = self.tick + 1
            if self.tick == settings.db['BSIDE_TIMER_REPOSITORY']:
                self.tick = 0
                try:
                    self.lblRepository.setText(utils.getHumanSize(utils.getDirSize2(settings.db['BSIDE_REPOSITORY'])) + " / " + utils.getHumanSize(utils.getDirSize2(settings.db['BACKUP_PATH'])))
                except:
                    self.lblRepository.setText("REPOSITORY ERROR ")

        # MON TUE THU WED FRI SAT SUN
        #  0   1   2   3   4   5   6
        self.aAlarms = [[False, "0123456", 19, 0, "A table !"], [False, "0123456", 16, 10, "Test Alarm"]]
        for alarm in self.aAlarms:
            now = datetime.datetime.now()
            if alarm[0] == True:
                if str(now.weekday()) in alarm[1]:
                    hAlarm = now.replace(hour=alarm[2], minute=alarm[3])
                    delta = int((hAlarm - now).total_seconds())
                    if delta <= 0:
                        print(alarm[4])
                        self.showMessage(alarm[4])
        
        try:
            self.lblClock.setText(datetime.datetime.now().strftime(settings.db['BSIDE_CLOCK_FORMAT']) + " ")
        except:
            self.lblClock.setText("INVALID ")
        
#-------------------------------------------------------------------------------
# keyPressEvent()
#-------------------------------------------------------------------------------
    def keyPressEvent(self, event):
        key = event.key()
        if key == Qt.Key_F3:            
            tab = self.tbwHighRight.widget(self.tbwHighRight.currentIndex())
            if isinstance(tab, editor.WEditor):
                tab.txtGotoSearch.setFocus()
        elif key == Qt.Key_F9:
            qApp.exit(MainWindow.EXIT_CODE_REBOOT)
        """
        elif key == Qt.Key_F2:
            self.saveFile()
        elif key == Qt.Key_F10:
            self.close()
        """
    
#-------------------------------------------------------------------------------
# __del__()
#-------------------------------------------------------------------------------
    def __del__(self):
        settings.db.close()
        self.ui = None

#-------------------------------------------------------------------------------
# cancelSettings()
#-------------------------------------------------------------------------------
    def cancelSettings(self):
        self.txtTimerStatus.setText(str(settings.db['BSIDE_TIMER_STATUS']))
        self.txtEditorFont.setText(settings.db['EDITOR_FONT'])

#-------------------------------------------------------------------------------
# restoreSettings()
#-------------------------------------------------------------------------------
    def restoreSettings(self):
        try:
            with open(os.path.join(self.appDir, const.TOOLS_FILE), "rb") as fp:
                self.tools = pickle.load(fp)
        except:
            pass        
        #
        try:
            with open(os.path.join(self.appDir, const.HISTORY_FILE), "rb") as fp:
                self.aCommands = pickle.load(fp)
                self.iCommands = len(self.aCommands)
        except:
            pass        
        #
        try:
            with open(os.path.join(self.appDir, const.HISTORY_SQL), "rb") as fp:
                self.aSQL = pickle.load(fp)
                self.iSQL = len(self.aSQL)
        except:
            pass        
        #
        try:
            with open(os.path.join(self.appDir, const.BACKUP_STAMP), "rb") as fp:
                self.lastBackup = pickle.load(fp)
        except:
            pass        
        #
        regSettings = QSettings()
        size = regSettings.value('MainWindow/Size', QSize(600,500))
        try:
            self.resize(size)
        except:
            self.resize(size.toSize())
        position = regSettings.value('MainWindow/Position', QPoint(0,0))
        try:
            self.move(position)
        except:
            self.move(position.toPoint())
        try:
            self.restoreState(regSettings.value("MainWindow/WindowState", b"", type='QByteArray'))
            # mainSplitter
            mainSplitterSettings = regSettings.value("MainWindow/mainSplitterSettings")
            if mainSplitterSettings:
                try:
                    self.mainSplitter.restoreState(mainSplitterSettings)
                except:
                    try:
                        self.mainSplitter.restoreState(mainSplitterSettings.toPyObject())    
                    except:
                        pass
            # leftSplitter
            leftSplitterSettings = regSettings.value("MainWindow/leftSplitterSettings")
            if leftSplitterSettings:
                try:
                    self.leftSplitter.restoreState(leftSplitterSettings)
                except:
                    try:
                        self.leftSplitter.restoreState(leftSplitterSettings.toPyObject())    
                    except:
                        pass
            # rightSplitter
            rightSplitterSettings = regSettings.value("MainWindow/rightSplitterSettings")
            if rightSplitterSettings:
                try:
                    self.rightSplitter.restoreState(rightSplitterSettings)
                except:
                    try:
                        self.rightSplitter.restoreState(rightSplitterSettings.toPyObject())    
                    except:
                        pass
        except:
            pass
        # self.cancelSettings()

#-------------------------------------------------------------------------------
# backupSettings()
#-------------------------------------------------------------------------------
    def backupSettings(self):
        with open(os.path.join(self.appDir, const.HISTORY_FILE), "wb") as fp:
            pickle.dump(self.aCommands, fp)        
        #
        with open(os.path.join(self.appDir, const.HISTORY_SQL), "wb") as fp:
            pickle.dump(self.aSQL, fp)        
        #
        with open(os.path.join(self.appDir, const.TOOLS_FILE), "wb") as fp:
            pickle.dump(self.tools, fp)        
        #
        with open(os.path.join(self.appDir, const.BACKUP_STAMP), "wb") as fp:
            pickle.dump(self.lastBackup, fp)        
        #
        regSettings = QSettings()
        regSettings.setValue("MainWindow/Size", self.size())
        regSettings.setValue("MainWindow/Position", self.pos())
        regSettings.setValue("MainWindow/WindowState", self.saveState())
        
        # mainSplitter
        mainSplitterSettings = self.mainSplitter.saveState()
        if mainSplitterSettings:
            regSettings.setValue("MainWindow/mainSplitterSettings", self.mainSplitter.saveState())     
        # leftSplitter
        leftSplitterSettings = self.leftSplitter.saveState()
        if leftSplitterSettings:
            regSettings.setValue("MainWindow/leftSplitterSettings", self.leftSplitter.saveState())     
        # rightSplitter
        rightSplitterSettings = self.rightSplitter.saveState()
        if rightSplitterSettings:
            regSettings.setValue("MainWindow/rightSplitterSettings", self.rightSplitter.saveState())     
            
        settings.db.sync()
        self.showMessage("Settings saved")
        
#-------------------------------------------------------------------------------
# showMessage()
#-------------------------------------------------------------------------------
    def showMessage(self, msg):
        self.statusBar.showMessage(msg, settings.db['BSIDE_TIMER_STATUS'])
        self.outputMessage(msg)

#-------------------------------------------------------------------------------
# showDebug()
#-------------------------------------------------------------------------------
    def showDebug(self, msg):
        if self.debug == True:
            self.showMessage("[DEBUG] %s" % msg)
        
#-------------------------------------------------------------------------------
# outputMessage()
#-------------------------------------------------------------------------------
    def outputMessage(self, msg):
        now = datetime.datetime.now()
        self.txtOutput.appendPlainText(now.strftime(settings.db['OUTPUT_TIMESTAMP']) + msg)
        self.txtOutput.moveCursor(QTextCursor.End)
        
#-------------------------------------------------------------------------------
# closeEvent()
#-------------------------------------------------------------------------------
    def closeEvent(self, event):
        result = QMessageBox.question(self, "Confirm Exit", "Are you sure you want to quit ?", QMessageBox.Yes | QMessageBox.No)        
        if result == QMessageBox.Yes:
            self.timer.stop()
            # Close project
            # if self.project.name != "*NONE":
            if self.project is not None:
                self.focusState = self.HAS_FOCUS
                if self.previousFocusState == self.HAS_NOT_FOCUS:
                    self.timeNoFocus2 = time.time()
                    self.timeNoFocus = self.timeNoFocus + (self.timeNoFocus2 - self.timeNoFocus1)
                    self.previousFocusState = self.HAS_FOCUS
                self.project.timeNoFocus = self.timeNoFocus
                self.project.endSession()
            # Close TODO database
            self.curTODO.close()
            self.dbTODO.close()
            # Close SQL database
            self.curSQLDatabase.close()
            self.dbSQLDatabase.close()
            # Check for modified files not saved
            # Save the current files or project open
            for i in reversed(range(self.tbwHighRight.count())):
                tab = self.tbwHighRight.widget(i)
                if isinstance(tab, editor.WEditor) or isinstance(tab, editor.WMarkdown):
                    self.saveTabFromIndex(i)
            if self.isFullScreen():
                self.showMaximized()
            if settings.db['BACKUP_ENABLED'] == True:
                try:
                    self.lastBackup = backup.backupRepository(self.lastBackup, self)
                except:
                    self.showMessage("BACKUP ERROR")
            self.showMessage("Good bye")
            self.backupSettings()
            workspace.saveWorkspace(self)
            self.changeFocusText()
            event.accept()
        else:
            self.showMessage("Welcome back")
            event.ignore()

#-------------------------------------------------------------------------------
# openContextMenu()
#-------------------------------------------------------------------------------
    def openContextMenu(self, position):
        contextMenu = QMenu()
        saveAction = contextMenu.addAction("Save")
        icon = QIcon("pix/16x16/Save.png");
        saveAction.setIcon(icon)
        closeAction = contextMenu.addAction("Close")
        icon = QIcon("pix/16x16/Cancel.png");
        closeAction.setIcon(icon)
        closeAllAction = contextMenu.addAction("Close all")
        closeOthersAction = contextMenu.addAction("Close others")
        action = contextMenu.exec_(self.tbwHighRight.mapToGlobal(position))
        if action == saveAction:
            self.saveFile()
        elif action == closeAction:
            self.closeFile()
        elif action == closeAllAction:
            self.closeAll()
        elif action == closeOthersAction:
            self.closeOthers()

#-------------------------------------------------------------------------------
# about()
#-------------------------------------------------------------------------------
    def about(self):
        foundTab = False
        for i in range(0, self.tbwHighRight.count()):
            tab = self.tbwHighRight.widget(i)
            if isinstance(tab, helpme.TabHelp):
                foundTab = True
                self.tbwHighRight.setCurrentIndex(i)                        
        if foundTab == False:
            txtHelp = helpme.TabHelp(parent=self.tbwHighRight)        
            self.tbwHighRight.addTab(txtHelp, "About")
            idxTab = self.tbwHighRight.count() - 1
            self.tbwHighRight.setTabIcon(idxTab, QIcon("pix/silk/icons/information.png"))
            self.tbwHighRight.setCurrentIndex(idxTab)        
        self.showMessage("About")

#-------------------------------------------------------------------------------
# welcome()
#-------------------------------------------------------------------------------
    def welcome(self):
        foundTab = False
        for i in range(0, self.tbwHighRight.count()):
            tab = self.tbwHighRight.widget(i)
            if isinstance(tab, helpme.TabWelcome):
                foundTab = True
                self.tbwHighRight.setCurrentIndex(i)                        
        if foundTab == False:
            txtWelcome = helpme.TabWelcome(parent=self.tbwHighRight)        
            self.tbwHighRight.addTab(txtWelcome, "Welcome")
            idxTab = self.tbwHighRight.count() - 1
            self.tbwHighRight.setTabIcon(idxTab, QIcon("pix/silk/icons/drink.png"))
            self.tbwHighRight.setCurrentIndex(idxTab)        
        self.showMessage("Welcome")

#-------------------------------------------------------------------------------
# settings()
#-------------------------------------------------------------------------------
    def settings(self):
        foundTab = False
        for i in range(0, self.tbwHighRight.count()):
            tab = self.tbwHighRight.widget(i)
            if isinstance(tab, settings.TabSettings):
                foundTab = True
                self.tbwHighRight.setCurrentIndex(i)                        
        if foundTab == False:
            tabSettings = settings.TabSettings(parent=self.tbwHighRight)        
            self.tbwHighRight.addTab(tabSettings, "Settings")
            idxTab = self.tbwHighRight.count() - 1
            self.tbwHighRight.setTabIcon(idxTab, QIcon("pix/silk/icons/cog.png"))
            self.tbwHighRight.setCurrentIndex(idxTab)
        self.showMessage("Settings")

#-------------------------------------------------------------------------------
# saveFile()
#-------------------------------------------------------------------------------
    def saveFile(self):
        tab = self.tbwHighRight.widget(self.tbwHighRight.currentIndex())
        if isinstance(tab, editor.WEditor) or isinstance(tab, editor.WMarkdown):
            tab.saveFile()
            self.project.refreshStatus()
            self.showMessage("File saved")
        else:
            self.showMessage("Nothing to save")

#-------------------------------------------------------------------------------
# openFile()
#-------------------------------------------------------------------------------
    def openFile(self):
        filename = QFileDialog.getOpenFileName(self, 'Open file', '', 'Python sources (*.py);;XML files (*.xml)')[0]
        self.openFileFromName(filename)

#-------------------------------------------------------------------------------
# openFileFromName()
#-------------------------------------------------------------------------------
    def openFileFromName(self, filename):
        if filename != "":            
            tabEditor = editor.WEditor(filename=filename, parent=self.tbwHighRight, window=self, filetype="python")        
            name = os.path.basename(filename)
            self.tbwHighRight.addTab(tabEditor, name)
            idxTab = self.tbwHighRight.count() - 1
            self.tbwHighRight.setTabIcon(idxTab, QIcon("pix/icons/python2.5.png"))
            self.tbwHighRight.setCurrentIndex(idxTab)               
            
            tabEditor.txtEditor.textChanged.connect(lambda x=tabEditor: self.textChange(x))
            self.showMessage("Opening %s" % filename)   
            tabEditor.txtEditor.setFocus()
        else:
            self.showMessage("Open cancelled")

#-------------------------------------------------------------------------------
# newPythonFile()
#-------------------------------------------------------------------------------
    def newPythonFile(self):
        textBox = editor.WEditor(parent=self.tbwHighRight, window=self, filetype="python")        
        name = const.NEW_FILE % self.noname
        self.tbwHighRight.addTab(textBox, name)
        self.noname = self.noname + 1
        idxTab = self.tbwHighRight.count() - 1
        self.tbwHighRight.setTabIcon(idxTab, QIcon("pix/icons/text-x-python.png"))
        self.tbwHighRight.setCurrentIndex(idxTab)               
        
        textBox.txtEditor.textChanged.connect(lambda x=textBox: self.textChange(x))
        self.showMessage("New file %s" % name)

#-------------------------------------------------------------------------------
# newPynter()
#-------------------------------------------------------------------------------
    def newPynter(self):
        if settings.db['CONSOLE_UI'] == "CONSOLE_QT":
            pyBox = pynter.WInter(parent=self.tbwHighRight, window=self)        
        else:            
            if platform.system() == 'Windows':    # Windows
                # pyBox = pynter.WXInter(parent=self.tbwHighRight)        
                # WXInter is not working well, let's do it with WInter
                pyBox = pynter.WInter(parent=self.tbwHighRight)        
            else:                                 # linux variants
                try:
                    pyBox = pynter.LXInter(parent=self.tbwHighRight)         
                except:
                    pyBox = pynter.WInter(parent=self.tbwHighRight)
        name = "Python-%02d" % self.nopyth
        self.tbwHighRight.addTab(pyBox, name)
        self.nopyth = self.nopyth + 1
        idxTab = self.tbwHighRight.count() - 1
        self.tbwHighRight.setTabIcon(idxTab, QIcon("pix/icons/python2.5.png"))
        self.tbwHighRight.setCurrentIndex(idxTab)               
        # pyBox.consoleInput.setFocus()
        self.showMessage("New Python Interpreter")
        
#-------------------------------------------------------------------------------
# newShell()
#-------------------------------------------------------------------------------
    def newShell(self):
        if settings.db['SHELL_UI'] == "SHELL_QT":
            # shBox = shell.WShell(parent=self.tbwHighRight)
            shBox = shell.WShell(parent=self)
        else:            
            if platform.system() == 'Windows':    # Windows
                # shBox = shell.WXShell(parent=self.tbwHighRight)        
                # WXShell is not working well, let's do it with WShell
                shBox = shell.WShell(parent=self)        
            else:                                 # linux variants
                try:
                    shBox = shell.LXShell(parent=self.tbwHighRight)         
                except:
                    shBox = shell.WShell(parent=self)
        name = "Shell-%02d" % self.noshell
        self.tbwHighRight.addTab(shBox, name)
        self.noshell = self.noshell + 1
        idxTab = self.tbwHighRight.count() - 1
        self.tbwHighRight.setTabIcon(idxTab, QIcon("pix/icons/utilities-terminal-6.png"))
        self.tbwHighRight.setCurrentIndex(idxTab)                       
        # shBox.txtCommand.setFocus()
        self.showMessage("New Shell")

#-------------------------------------------------------------------------------
# textChange()
#-------------------------------------------------------------------------------
    def textChange(self, textBox):
        self.clearTableStructure()
        if hasattr(textBox, "codeStructure"):
            for i in textBox.codeStructure:
                rowPosition = self.tblStructure.rowCount()                     
                self.tblStructure.insertRow(rowPosition)

                item = QTableWidgetItem("%d" % i[0])
                item.setTextAlignment(Qt.AlignHCenter)
                self.tblStructure.setItem(rowPosition , 0, item)   # Line

                """
                item = QTableWidgetItem("%s" % i[2])        
                if i[2] == "class":
                    font = QFont()
                    font.setBold(True)
                    item.setFont(font)            

                item.setTextAlignment(Qt.AlignRight)
                """
                item = QTableWidgetItem()    
                item_hidden = QTableWidgetItem()    
                item.setTextAlignment(Qt.AlignHCenter)
                if i[2] == "class":
                    item.setIcon(QIcon("pix/icons/class.png"))
                    item_hidden.setText("class")
                elif i[2] == "function":
                    item.setIcon(QIcon("pix/icons/function.png"))
                    item_hidden.setText("function")
                elif i[2] == "var":
                    item.setIcon(QIcon("pix/icons/var.png"))                                    
                    item_hidden.setText("var")
                self.tblStructure.setItem(rowPosition , 3, item_hidden)   # Type
                self.tblStructure.setItem(rowPosition , 1, item)   # Type

                item = QTableWidgetItem("%s" % i[3])        
                item.setTextAlignment(Qt.AlignLeft)
                if i[2] == "class":
                    font = QFont()
                    font.setBold(True)
                    item.setFont(font)            
                self.tblStructure.setItem(rowPosition , 2, item)   # Name
                self.tblStructure.setRowHeight(rowPosition, 20)
        # self.tblStructure.horizontalHeader().setResizeMode(QHeaderView.Stretch)
        self.tblStructure.horizontalHeader().setStretchLastSection(True)
                
        self.clearTableActions()
        if hasattr(textBox, "todo"):
            if len(textBox.todo) > 0:
                for i in textBox.todo:
                    rowPosition = self.tblActions.rowCount()                     
                    self.tblActions.insertRow(rowPosition)

                    item = QTableWidgetItem("%d" % i[0])
                    item.setTextAlignment(Qt.AlignHCenter)
                    self.tblActions.setItem(rowPosition , 0, item)   # Line

                    item = QTableWidgetItem("%s" % i[1])        
                    item.setTextAlignment(Qt.AlignLeft)
                    self.tblActions.setItem(rowPosition , 1, item)   # Description

                    self.tblActions.setRowHeight(rowPosition, 20)
        
        self.tblStructure.resizeColumnsToContents()
        self.tblActions.resizeColumnsToContents()
        self.tblStructure.horizontalHeader().setStretchLastSection(True)
        self.tblActions.horizontalHeader().setStretchLastSection(True)
        self.tblStructure.sortItems(0, Qt.AscendingOrder)
        self.tblActions.sortItems(0, Qt.AscendingOrder)
            
#-------------------------------------------------------------------------------
# tabChange()
#-------------------------------------------------------------------------------
    def tabChange(self, index):
        tabEditor = self.tbwHighRight.widget(index)
        if isinstance(tabEditor, editor.WEditor):
            self.textChange(tabEditor)
            self.clearTableSearch()
            if tabEditor.txtGotoSearch.text() != "":
                tabEditor.gotoSearch()
            if tabEditor.filename is not None:
                if os.path.splitext(tabEditor.filename)[1] == ".py":
                    self.actionRunScript.setEnabled(True)
                else:
                    self.actionRunScript.setEnabled(False)
            else:
                    self.actionRunScript.setEnabled(False)            
        else:
            self.actionRunScript.setEnabled(False)            
                
#-------------------------------------------------------------------------------
# clearTableSearch()
#-------------------------------------------------------------------------------
    def clearTableSearch(self):
        while (self.tblSearch.rowCount() > 0):
                self.tblSearch.removeRow(0)
        self.tblSearch.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
        self.tblSearch.setColumnCount(2)
        self.tblSearch.setHorizontalHeaderLabels(["Line", "Text"])
        self.tblSearch.setEditTriggers(QTableWidget.NoEditTriggers)
        self.lblSearch.setText("None")

#-------------------------------------------------------------------------------
# clearTableStructure()
#-------------------------------------------------------------------------------
    def clearTableStructure(self):
        while (self.tblStructure.rowCount() > 0):
                self.tblStructure.removeRow(0)
        self.tblStructure.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
        self.tblStructure.setColumnCount(4)
        self.tblStructure.setHorizontalHeaderLabels(["Line", "Type", "Name", "Type2"])
        self.tblStructure.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tblStructure.verticalHeader().setVisible(False)
        self.tblStructure.setColumnHidden(3, True)
        self.tblStructure.horizontalHeader().setStretchLastSection(True)

#-------------------------------------------------------------------------------
# clearTableActions()
#-------------------------------------------------------------------------------
    def clearTableActions(self):
        while (self.tblActions.rowCount() > 0):
                self.tblActions.removeRow(0)
        self.tblActions.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
        self.tblActions.setColumnCount(2)
        self.tblActions.setHorizontalHeaderLabels(["Line", "Description"])
        self.tblActions.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tblActions.verticalHeader().setVisible(False)

#-------------------------------------------------------------------------------
# closeFile()
#-------------------------------------------------------------------------------
    def closeFile(self):
        self.closeTabFromIndex(self.tbwHighRight.currentIndex())
        
#-------------------------------------------------------------------------------
# closeAll()
#-------------------------------------------------------------------------------
    def closeAll(self):
        self.showDebug("TABS %d" % self.tbwHighRight.count())
        for i in reversed(range(0, self.tbwHighRight.count())):
            self.closeTabFromIndex(i)

#-------------------------------------------------------------------------------
# closeOthers()
#-------------------------------------------------------------------------------
    def closeOthers(self):
        self.showDebug("TABS %d" % self.tbwHighRight.count())
        for i in reversed(range(0, self.tbwHighRight.count())):
            if i != self.tbwHighRight.currentIndex():
                self.closeTabFromIndex(i)

#-------------------------------------------------------------------------------
# saveEnv()
#-------------------------------------------------------------------------------
    def saveWorkspace(self):
        for i in range(0, self.tbwHighRight.count()):
            self.closeTabFromIndex(i)
    
#-------------------------------------------------------------------------------
# closeTabFromIndex()
#-------------------------------------------------------------------------------
    def closeTabFromIndex(self, index, force=False):
        self.showDebug("Closing %d" % index)
        tab = self.tbwHighRight.widget(index)
        self.tbwHighRight.setCurrentIndex(index)
        if force == False:
            if isinstance(tab, editor.WEditor):
                if tab.dirtyFlag == True:
                    result = QMessageBox.question(self,"Confirm close file","The following file\n%s\nhas been modified.\n\nDo you want to save it ?" % tab.filename,QMessageBox.Yes| QMessageBox.No | QMessageBox.Cancel)        
                    if result == QMessageBox.Yes:
                        self.saveFile()
                        tab.deleteLater()
                        self.tbwHighRight.removeTab(index)
                        self.tblStructure.clear()
                        self.showMessage("Save & Close")
                    elif result == QMessageBox.No:
                        tab.deleteLater()
                        self.tbwHighRight.removeTab(index)
                        self.tblStructure.clear()
                        self.showMessage("Close anyway")
                    else:
                        self.showMessage("Abort closing")
                else:
                    tab.deleteLater()
                    self.tbwHighRight.removeTab(index)
                    self.tblStructure.clear()
                    self.showMessage("Close file")
            else:
                    # tab.deleteLater()                
                    self.tbwHighRight.removeTab(index)
                    self.tblStructure.clear()
                    self.showMessage("Close tab")
        else:
            tab.deleteLater()
            self.tbwHighRight.removeTab(index)
            self.tblStructure.clear()
            self.showMessage("Close force")
            
#-------------------------------------------------------------------------------
# saveTabFromIndex()
#-------------------------------------------------------------------------------
    def saveTabFromIndex(self, index):
        tab = self.tbwHighRight.widget(index)
        self.tbwHighRight.setCurrentIndex(index)
        if isinstance(tab, editor.WEditor):
            if tab.dirtyFlag == True:
                result = QMessageBox.question(self,"File modified","The following file\n%s\nhas been modified.\n\nDo you want to save it ?" % tab.filename,QMessageBox.Yes| QMessageBox.No)
                if result == QMessageBox.Yes:
                    self.saveFile()
                    self.showMessage("Saving file %s" % tab.filename)

#-------------------------------------------------------------------------------
# saveAll()
#-------------------------------------------------------------------------------
    def saveAll(self):
        for i in range(0, self.tbwHighRight.count()):
            tab = self.tbwHighRight.widget(i)
            self.tbwHighRight.setCurrentIndex(i)
            if isinstance(tab, editor.WEditor) or isinstance(tab, editor.WMarkdown):
                if tab.dirtyFlag == True:
                    tab.saveFile()
                    self.project.refreshStatus()
                    self.showMessage("File saved")
        
#-------------------------------------------------------------------------------
# clickedSearchLine()
#-------------------------------------------------------------------------------
    def clickedSearchLine(self, item):
        tab = self.tbwHighRight.widget(self.tbwHighRight.currentIndex())
        if isinstance(tab, editor.WEditor):
            line = int(self.tblSearch.item(item.row(), 0).text())
            self.showDebug("Line = %s" % line)
            tab.gotoLine(line)

#-------------------------------------------------------------------------------
# clickedStructure()
#-------------------------------------------------------------------------------
    def clickedStructure(self, item):
        tab = self.tbwHighRight.widget(self.tbwHighRight.currentIndex())
        if isinstance(tab, editor.WEditor):
            line = int(self.tblStructure.item(item.row(), 0).text())
            self.showDebug("Line = %s" % line)
            tab.gotoLine(line)
            
#-------------------------------------------------------------------------------
# doSortByLine()
#-------------------------------------------------------------------------------
    def doSortByLine(self):
        self.tblStructure.sortItems(0, Qt.AscendingOrder)
        self.showMessage("Sort structure by line numbers")

#-------------------------------------------------------------------------------
# doSortByType()
#-------------------------------------------------------------------------------
    def doSortByType(self):
        self.tblStructure.sortItems(3, Qt.AscendingOrder)
        self.showMessage("Sort structure by type")
    
#-------------------------------------------------------------------------------
# doSortByAlpha()
#-------------------------------------------------------------------------------
    def doSortByAlpha(self):
        self.tblStructure.sortItems(2, Qt.AscendingOrder)
        self.showMessage("Sort structure by name")

#-------------------------------------------------------------------------------
# clickedActions()
#-------------------------------------------------------------------------------
    def clickedActions(self, item):
        tab = self.tbwHighRight.widget(self.tbwHighRight.currentIndex())
        if isinstance(tab, editor.WEditor):
            line = int(self.tblActions.item(item.row(), 0).text())
            self.showDebug("Line = %s" % line)
            tab.gotoLine(line)

#-------------------------------------------------------------------------------
# clickedTreeView()
#-------------------------------------------------------------------------------
    def clickedTreeView(self, index):
        self.idxSelectedFile = index
        filePath = self.tvwModel.filePath(self.idxSelectedFile)
        isDir = self.tvwModel.isDir(self.idxSelectedFile)
        isBinary = utils.isBinaryFile(filePath)
        if not isDir and not isBinary:
            # fileName = self.tvwMenuModel.fileName(self.idxSelectedFile)
            fileName = os.path.basename(filePath)
            # self.lblCurrentFile.setText(fileName)
            # self.txtMarkdown.setPlainText(open(filePath).read())

#-------------------------------------------------------------------------------
# clickedProject()
#-------------------------------------------------------------------------------
    def clickedProject(self, index):
        self.idxSelectedFile = index
        filePath = self.tvmProject.filePath(self.idxSelectedFile)
        isDir = self.tvmProject.isDir(self.idxSelectedFile)
        isBinary = utils.isBinaryFile(filePath)
        if not isDir and not isBinary:
            # fileName = self.tvwMenuModel.fileName(self.idxSelectedFile)
            fileName = os.path.basename(filePath)
            # self.lblCurrentFile.setText(fileName)
            # self.txtMarkdown.setPlainText(open(filePath).read())
                   
#-------------------------------------------------------------------------------
# doubleClickedTreeView()
#-------------------------------------------------------------------------------
    def doubleClickedTreeView(self, index):
        self.idxSelectedFile = index
        isDir = self.tvwModel.isDir(self.idxSelectedFile)
        if not isDir:
            self.doOpenAction()

#-------------------------------------------------------------------------------
# doubleClickedProject()
#-------------------------------------------------------------------------------
    def doubleClickedProject(self, index):
        self.idxSelectedFile = index
        isDir = self.tvmProject.isDir(self.idxSelectedFile)
        if not isDir:
            self.doOpenAction()
        
#-------------------------------------------------------------------------------
# menuContextTree()
#-------------------------------------------------------------------------------
    def menuContextTree(self, point):
        index = self.tvwRepository.indexAt(point)
        self.idxSelectedFile = index
        filePath = self.tvwModel.filePath(self.idxSelectedFile)
        isDir = self.tvwModel.isDir(self.idxSelectedFile)
        isBinary = utils.isBinaryFile(filePath)       
        
        # p = vlc.MediaPlayer("resources/sounds/tone01.mp3")
        # p.play()                
              
        menu = QMenu()
        # Open
        openAction = QAction(QIcon("pix/16x16/Folder.png"),"Open")
        menu.addAction(openAction)
        openAction.triggered.connect(self.doOpenAction)
        openAction.setEnabled(not isDir)
        
        # Open as Hexa
        openHexaAction = QAction(QIcon("pix/16x16/Folder.png"),"Open as Hexa")
        menu.addAction(openHexaAction)
        openHexaAction.triggered.connect(self.doOpenHexaAction)
        openHexaAction.setEnabled(not isDir)

        # Promote to Project
        promoteProjectAction = QAction(QIcon("pix/16x16/Folder.png"),"Promote to Project")
        menu.addAction(promoteProjectAction)
        promoteProjectAction.triggered.connect(lambda x, folder=filePath : self.doPromoteProjectAction(folder))
        promoteProjectAction.setEnabled(isDir and not os.path.isfile(os.path.join(filePath, const.PROJECT_FILE_NAME)))
        menu.addSeparator()

        # New
        newAction = QAction(QIcon("pix/16x16/Pen.png"),"New")
        menu.addAction(newAction)
        newAction.triggered.connect(self.doNewAction)
        
        # Edit
        """
        editAction = QAction(QIcon("pix/16x16/Pen.png"),"Edit")
        menu.addAction(editAction)
        editAction.triggered.connect(self.doEditAction)
        editAction.setEnabled(not isDir and not isBinary)
        """    
        # Delete
        deleteAction = QAction(QIcon("pix/16x16/Trash.png"),"Delete")
        menu.addAction(deleteAction)
        deleteAction.triggered.connect(self.doDeleteAction)
        # Rename
        renameAction = QAction(QIcon("pix/16x16/Back.png"),"Rename")
        menu.addAction(renameAction)
        renameAction.triggered.connect(self.doRenameAction)
        menu.addSeparator()
        # Cut
        cutAction = QAction(QIcon("pix/16x16/Clipboard Cut.png"),"Cut")
        menu.addAction(cutAction)
        cutAction.triggered.connect(self.doCutAction)
        # Copy
        copyAction = QAction(QIcon("pix/16x16/Clipboard Copy.png"),"Copy")
        menu.addAction(copyAction)
        copyAction.triggered.connect(self.doCopyAction)
        # Paste
        pasteAction = QAction(QIcon("pix/16x16/Clipboard Paste.png"),"Paste")
        pasteAction.setEnabled(self.clipboardFull)
        menu.addAction(pasteAction)
        pasteAction.triggered.connect(self.doPasteAction)
        menu.addSeparator()
        # Properties
        propertiesAction = QAction(QIcon("pix/16x16/Gear.png"),"Properties")
        menu.addAction(propertiesAction)
        propertiesAction.triggered.connect(self.doPropertiesAction)
        
        menu.exec_(self.tvwRepository.viewport().mapToGlobal(point))     

#-------------------------------------------------------------------------------
# menuContextProject()
#-------------------------------------------------------------------------------
    def menuContextProject(self, point):
        if self.project is not None:
            index = self.tvwProject.indexAt(point)
            self.idxSelectedFile = index
            filePath = self.tvmProject.filePath(self.idxSelectedFile)
            isDir = self.tvmProject.isDir(self.idxSelectedFile)
            isBinary = utils.isBinaryFile(filePath)       

            # p = vlc.MediaPlayer("resources/sounds/tone01.mp3")
            # p.play()                

            menu = QMenu()
            # Open
            openAction = QAction(QIcon("pix/16x16/Folder.png"), "Open")
            menu.addAction(openAction)
            openAction.triggered.connect(self.doOpenAction)
            openAction.setEnabled(not isDir)

            # Open as Hexa
            openHexaAction = QAction(QIcon("pix/16x16/Folder.png"), "Open as Hexa")
            menu.addAction(openHexaAction)
            openHexaAction.triggered.connect(self.doOpenHexaAction)
            openHexaAction.setEnabled(not isDir)
            menu.addSeparator()

            # New...
            newMenu = QMenu("New...")
            menu.addMenu(newMenu)
            # New Module
            newModuleAction = QAction(QIcon("pix/icons/python2.5.png"), "Python module...")
            newMenu.addAction(newModuleAction)
            newModuleAction.triggered.connect(self.project.newModule)
            # New Folder
            newFolderAction = QAction(QIcon("pix/16x16/Folder.png"), "Folder...")
            newMenu.addAction(newFolderAction)
            newFolderAction.triggered.connect(self.project.newFolder)
            # New Markdown
            newMDAction = QAction(QIcon("pix/icons/markdown.png"), "Markdown file...")
            newMenu.addAction(newMDAction)
            newMDAction.triggered.connect(self.project.newMDFile)
            # New XML
            newXMLAction = QAction(QIcon("pix/icons/xml.png"), "XML file...")
            newMenu.addAction(newXMLAction)
            newXMLAction.triggered.connect(self.project.newXMLFile)
            # New HTML
            newHTMLAction = QAction(QIcon("pix/icons/text-html.png"), "HTML file...")
            newMenu.addAction(newHTMLAction)
            newHTMLAction.triggered.connect(self.project.newHTMLFile)
            # New Qt UI
            newQtUIAction = QAction(QIcon("pix/icons/QtUI.png"), "Qt UI file...")
            newMenu.addAction(newQtUIAction)
            newQtUIAction.triggered.connect(self.project.newQtUIFile)
            # New SQL
            newSQLAction = QAction(QIcon("pix/icons/database.png"), "SQL file...")
            newMenu.addAction(newSQLAction)
            newSQLAction.triggered.connect(self.project.newSQLFile)
            # New File
            newFileAction = QAction(QIcon("pix/16x16/Document.png"), "Empty file...")
            newMenu.addAction(newFileAction)
            newFileAction.triggered.connect(self.project.newFile)


            # Edit
            """
            editAction = QAction(QIcon("pix/16x16/Pen.png"),"Edit")
            menu.addAction(editAction)
            editAction.triggered.connect(self.doEditAction)
            editAction.setEnabled(not isDir and not isBinary)
            """    
            # Delete
            deleteAction = QAction(QIcon("pix/16x16/Trash.png"),"Delete")
            menu.addAction(deleteAction)
            deleteAction.triggered.connect(self.doDeleteAction)
            # Rename
            renameAction = QAction(QIcon("pix/16x16/Back.png"),"Rename")
            menu.addAction(renameAction)
            renameAction.triggered.connect(self.doRenameAction)
            menu.addSeparator()
            # Cut
            cutAction = QAction(QIcon("pix/16x16/Clipboard Cut.png"),"Cut")
            menu.addAction(cutAction)
            cutAction.triggered.connect(self.doCutAction)
            # Copy
            copyAction = QAction(QIcon("pix/16x16/Clipboard Copy.png"),"Copy")
            menu.addAction(copyAction)
            copyAction.triggered.connect(self.doCopyAction)
            # Paste
            pasteAction = QAction(QIcon("pix/16x16/Clipboard Paste.png"),"Paste")
            pasteAction.setEnabled(self.clipboardFull)
            menu.addAction(pasteAction)
            pasteAction.triggered.connect(self.doPasteAction)
            menu.addSeparator()
            # Project Properties
            propertiesAction = QAction(QIcon("pix/16x16/Gear.png"),"Project properties")
            menu.addAction(propertiesAction)
            propertiesAction.triggered.connect(self.doProjectPropertiesAction)
            # Close project
            closeProjectAction = QAction(QIcon("pix/16x16/Close.png"),"Close project")
            menu.addAction(closeProjectAction)
            closeProjectAction.triggered.connect(self.closeProject)

            menu.exec_(self.tvwProject.viewport().mapToGlobal(point))     
    
#-------------------------------------------------------------------------------
# isFileOpen()
#-------------------------------------------------------------------------------
    def isFileOpen(self, fname):
        rc = (False, 0)
        for i in range(0, self.tbwHighRight.count()):
            tab = self.tbwHighRight.widget(i)
            if isinstance(tab, editor.WEditor) or isinstance(tab, editor.WMarkdown):
                if os.path.normpath(tab.filename) == os.path.normpath(fname):
                    rc = (True, i)
                    break
        return rc                    
        
#-------------------------------------------------------------------------------
# doOpenAction()
#-------------------------------------------------------------------------------
    def doOpenAction(self):        
        isDir = self.tvwModel.isDir(self.idxSelectedFile)
        if not isDir:
            filename = self.tvwModel.fileName(self.idxSelectedFile)
            filepath = self.tvwModel.filePath(self.idxSelectedFile)                        
            isBinary = utils.isBinaryFile(filepath)            
            if not isBinary:
                (rc, tab) = self.isFileOpen(filepath)
                if not rc:
                    extension = os.path.splitext(filename)[1]
                    if extension == ".bsix":
                        #-------------------------------------------------------
                        # Open project
                        #-------------------------------------------------------
                        projectName = os.path.basename(os.path.normpath(os.path.dirname(filepath)))
                        self.showDebug(projectName)
                        if self.lblProject.text() != projectName:
                            self.tvwProject.setModel(self.tvmProject)
                            self.tvwProject.setAnimated(False)
                            self.tvwProject.setIndentation(10)
                            self.tvwProject.setSortingEnabled(True)        
                            for i in range(1, self.tvwProject.header().length()):
                                self.tvwProject.hideColumn(i)
                            self.tvwProject.sortByColumn(0, Qt.AscendingOrder)
                            myProject = os.path.basename(os.path.normpath(os.path.dirname(filepath)))
                            self.showDebug(myProject)
                            self.project = projects.Project(parent = self)
                            self.project.set(myProject)
                            # (_, filename) = self.project.open()
                            self.project.open()
                        else:
                            self.doEditFile(filepath, syntax="xml")
                            self.showMessage("Project %s already open" % projectName)
                    else:
                        self.doEditFile(filepath)
                else:
                    self.tbwHighRight.setCurrentIndex(tab)
                    self.showMessage("file already open")
            else:
                try:
                    if platform.system() == 'Darwin':       # macOS
                        subprocess.call(('open', filepath))
                    elif platform.system() == 'Windows':    # Windows
                        os.startfile(filepath)
                    else:                                   # linux variants
                        subprocess.call(('xdg-open', filepath))
                    self.showMessage("Opening %s" % filename)
                except:
                    self.showMessage("Don't know how to open %s" % filename)

#-------------------------------------------------------------------------------
# doEditFile()
#-------------------------------------------------------------------------------
    def doEditFile(self, filename, syntax="guess"):
        if self.project is not None:
            encoding = self.project.encoding
        else:
            encoding = settings.db['EDITOR_CODEPAGE']
        if filename is not None:
            if path.exists(filename):
                tabEditor = None
                extension = os.path.splitext(filename)[1]
                if syntax == "guess":
                    if extension == ".md":
                        tabEditor = editor.WMarkdown(filename=filename, parent=self.tbwHighRight, window=self)        
                        if tabEditor != None:
                            name = os.path.basename(filename)
                            self.tbwHighRight.addTab(tabEditor, name)
                            idxTab = self.tbwHighRight.count() - 1
                            self.tbwHighRight.setTabIcon(idxTab, QIcon("pix/icons/markdown.png"))
                            self.tbwHighRight.setCurrentIndex(idxTab)               

                            # tabEditor.txtEditor.textChanged.connect(lambda x=tabEditor: self.textChange(x))
                    else:
                        icon = None
                        if extension == ".py":
                            tabEditor = editor.WEditor(filename=filename, parent=self.tbwHighRight, window=self, filetype="python", encoding=encoding)                    
                            icon = "pix/icons/text-x-python.png"
                        elif extension == ".xml":
                            tabEditor = editor.WEditor(filename=filename, parent=self.tbwHighRight, window=self, filetype="xml", encoding=encoding)
                            icon = "pix/icons/application-xml.png"
                        elif extension == ".html":
                            tabEditor = editor.WEditor(filename=filename, parent=self.tbwHighRight, window=self, filetype="html", encoding=encoding)                    
                            icon = "pix/icons/text-html.png"
                        elif extension == ".sql":
                            tabEditor = editor.WEditor(filename=filename, parent=self.tbwHighRight, window=self, filetype="sql", encoding=encoding)                    
                            icon = "pix/icons/database.png"
                        else:
                            tabEditor = editor.WEditor(filename=filename, parent=self.tbwHighRight, window=self, filetype="text", encoding=encoding)                    
                            icon = "pix/icons/text-icon.png"
                        if tabEditor != None:
                            name = os.path.basename(filename)
                            self.tbwHighRight.addTab(tabEditor, name)
                            idxTab = self.tbwHighRight.count() - 1
                            self.tbwHighRight.setTabIcon(idxTab, QIcon(icon))
                            self.tbwHighRight.setCurrentIndex(idxTab)               

                            # tabEditor.txtEditor.textChanged.connect(lambda x=tabEditor: self.textChange(x))

                elif syntax == "binary":
                    tabEditor = QHexEditor.QHexEditor(filename=filename, readonly=True)        
                    if tabEditor != None:
                        name = os.path.basename(filename)
                        self.tbwHighRight.addTab(tabEditor, name)
                        idxTab = self.tbwHighRight.count() - 1
                        self.tbwHighRight.setTabIcon(idxTab, QIcon("pix/icons/binary-icon.png"))
                        self.tbwHighRight.setCurrentIndex(idxTab)               

                        # tabEditor.txtEditor.textChanged.connect(lambda x=tabEditor: self.textChange(x))
                elif syntax == "markdown":
                    tabEditor = editor.WMarkdown(filename=filename, parent=self.tbwHighRight, window=self, encoding=encoding)        
                    if tabEditor != None:
                        name = os.path.basename(filename)
                        self.tbwHighRight.addTab(tabEditor, name)
                        idxTab = self.tbwHighRight.count() - 1
                        self.tbwHighRight.setTabIcon(idxTab, QIcon("pix/icons/markdown.png"))
                        self.tbwHighRight.setCurrentIndex(idxTab)               

                        # tabEditor.txtEditor.textChanged.connect(lambda x=tabEditor: self.textChange(x))        
                elif syntax == "python":
                    icon = "pix/icons/text-x-python.png"
                    tabEditor = editor.WEditor(filename=filename, parent=self.tbwHighRight, window=self, filetype=filetype, encoding=encoding)                    
                    name = os.path.basename(filename)
                    self.tbwHighRight.addTab(tabEditor, name)
                    idxTab = self.tbwHighRight.count() - 1
                    self.tbwHighRight.setTabIcon(idxTab, QIcon(icon))
                    self.tbwHighRight.setCurrentIndex(idxTab)               
                elif syntax == "xml":
                    icon = "pix/icons/application-xml.png"
                    tabEditor = editor.WEditor(filename=filename, parent=self.tbwHighRight, window=self, filetype="xml", encoding=encoding)                    
                    name = os.path.basename(filename)
                    self.tbwHighRight.addTab(tabEditor, name)
                    idxTab = self.tbwHighRight.count() - 1
                    self.tbwHighRight.setTabIcon(idxTab, QIcon(icon))
                    self.tbwHighRight.setCurrentIndex(idxTab)               
                elif syntax == "html":
                    icon = "pix/icons/text-html.png"
                    tabEditor = editor.WEditor(filename=filename, parent=self.tbwHighRight, window=self, filetype=filetype, encoding=encoding)                    
                    name = os.path.basename(filename)
                    self.tbwHighRight.addTab(tabEditor, name)
                    idxTab = self.tbwHighRight.count() - 1
                    self.tbwHighRight.setTabIcon(idxTab, QIcon(icon))
                    self.tbwHighRight.setCurrentIndex(idxTab)               
                else:
                    icon = "pix/icons/text-icon.png"
                    tabEditor = editor.WEditor(filename=filename, parent=self.tbwHighRight, window=self, filetype=filetype, encoding=encoding)                    
                    name = os.path.basename(filename)
                    self.tbwHighRight.addTab(tabEditor, name)
                    idxTab = self.tbwHighRight.count() - 1
                    self.tbwHighRight.setTabIcon(idxTab, QIcon(icon))
                    self.tbwHighRight.setCurrentIndex(idxTab)               

                if tabEditor != None:
                    self.showMessage("Editing %s" % filename)
                else:
                    self.showMessage("Can't open %s" % filename)
            else:
                self.showMessage("File %s does not exist" % filename)        
        else:
            self.showMessage("File does not exist")

#-------------------------------------------------------------------------------
# doPromoteProjectAction()
#-------------------------------------------------------------------------------
    def doPromoteProjectAction(self, folder):  
        if self.project is not None:
            self.project.close()
        self.project = projects.Project(parent = self)
        self.project.promoteProject(folder)

#-------------------------------------------------------------------------------
# doOpenHexaAction()
#-------------------------------------------------------------------------------
    def doOpenHexaAction(self):        
        isDir = self.tvwModel.isDir(self.idxSelectedFile)
        if not isDir:
            filename = self.tvwModel.fileName(self.idxSelectedFile)
            filepath = self.tvwModel.filePath(self.idxSelectedFile)                        
            (rc, tab) = self.isFileOpen(filepath)
            if not rc:
                # tabEditor = editor.WHexedit(filename=filepath, parent=self.tbwHighRight, window=self)        
                hexEditor = QHexEditor.QHexEditor(filename=filepath, readonly=True)        
                name = os.path.basename(filename)
                self.tbwHighRight.addTab(hexEditor, name)
                self.tbwHighRight.setCurrentIndex(self.tbwHighRight.count() - 1)

                # tabEditor.txtEditor.textChanged.connect(lambda x=tabEditor: self.textChange(x))
                self.showMessage("Editing %s" % filename)
            else:
                self.tbwHighRight.setCurrentIndex(tab)
                self.showMessage("file already open")

#-------------------------------------------------------------------------------
# doNewAction()
#-------------------------------------------------------------------------------
    def doNewAction(self):        
        self.newPythonFile()

#-------------------------------------------------------------------------------
# doAddFileAction()
#-------------------------------------------------------------------------------
    def doAddFileAction(self):        
        self.newPythonFile()
        
#-------------------------------------------------------------------------------
# doEditAction()
#-------------------------------------------------------------------------------
    def doEditAction(self):        
        isDir = self.tvwModel.isDir(self.idxSelectedFile)
        if not isDir:
            filePath = self.tvwModel.filePath(self.idxSelectedFile)
            isBinary = utils.isBinaryFile(filePath)
            if not isBinary:
                fileName = self.tvwModel.fileName(self.idxSelectedFile)
                self.lblCurrentFile.setText(fileName)
                self.txtMarkdown.setPlainText(open(filePath).read())
                self.txtHTML.setText(markdown.markdown(self.txtMarkdown.toPlainText()))
                self.showMessage("Editing %s" % fileName)
       
#-------------------------------------------------------------------------------
# doDeleteAction()
#-------------------------------------------------------------------------------
    def doDeleteAction(self):
        if not self.idxSelectedFile is None:           
            isDir = self.tvwModel.isDir(self.idxSelectedFile)
            filePath = self.tvwModel.filePath(self.idxSelectedFile)
            if isDir:
                msg = "Delete\n\n%s\n\nfolder ?" % os.path.basename(filePath)
            else:
                msg = "Delete\n\n%s\n\nfile ?" % os.path.basename(filePath)
            result = QMessageBox.question(self, "Delete an object", msg, QMessageBox.Yes | QMessageBox.No, QMessageBox.No)        
            if result == QMessageBox.Yes:
                if isDir:
                    self.showDebug("Tabs %d" % self.tbwHighRight.count())
                    for i in reversed(range(self.tbwHighRight.count())):
                        tab = self.tbwHighRight.widget(i) 
                        self.showDebug("Tab %d : %s" % (i, str(type(tab))))
                        if isinstance(tab, editor.WEditor) or isinstance(tab, editor.WMarkdown) or isinstance(tab, editor.WHexedit):
                            self.showDebug("%s vs %s" % (os.path.normpath(filePath), os.path.normpath(os.path.dirname(tab.filename))))
                            if os.path.normpath(os.path.dirname(tab.filename)) == os.path.normpath(filePath):
                                self.closeTabFromIndex(i, force=True)
                    rc = utils.deleteFolder(filePath)
                else:
                    fop = self.isFileOpen(filePath)
                    if fop[0] == True:
                        self.closeTabFromIndex(fop[1], force=True)
                    rc = utils.deleteFile(filePath)
                if rc:
                    self.project.refreshStatus()
                    self.showMessage("Object [%s] deleted" % os.path.basename(filePath))
                else:
                    self.showMessage("Unable to delete object [%s]" % os.path.basename(filePath))
        else:
            self.showMessage("No object selected")

#-------------------------------------------------------------------------------
# doRenameAction()
#-------------------------------------------------------------------------------
    def doRenameAction(self):
        if not self.idxSelectedFile is None:           
            filePath = self.tvwModel.filePath(self.idxSelectedFile)            
            text, ok = QInputDialog.getText(self, 'Rename object', 'New name :', QLineEdit.Normal, os.path.basename(filePath))		
            if ok:
                try:
                    os.rename(filePath, os.path.join(os.path.dirname(filePath), text))
                    self.showMessage("Object renamed")
                except:
                    self.showMessage("Unable to rename object")
        else:
            self.showMessage("No target folder selected")
        
#-------------------------------------------------------------------------------
# doCutAction()
#-------------------------------------------------------------------------------
    def doCutAction(self):
        # cdc.do_it()
        self.showMessage("Action = CUT")
        
#-------------------------------------------------------------------------------
# doCopyAction()
#-------------------------------------------------------------------------------
    def doCopyAction(self):
        self.showMessage("Action = COPY")
        
#-------------------------------------------------------------------------------
# doPasteAction()
#-------------------------------------------------------------------------------
    def doPasteAction(self):
        self.showMessage("Action = PASTE")
        
#-------------------------------------------------------------------------------
# doPropertiesAction()
#-------------------------------------------------------------------------------
    def doPropertiesAction(self):
        fileName = self.tvwModel.fileName(self.idxSelectedFile)
        filePath = self.tvwModel.filePath(self.idxSelectedFile)
        isDir = self.tvwModel.isDir(self.idxSelectedFile)
        fType = self.tvwModel.type(self.idxSelectedFile)
        fSize = self.tvwModel.size(self.idxSelectedFile)
        lastModified = self.tvwModel.lastModified(self.idxSelectedFile)
        
        fileProps = {}
        fileProps.update({'Name': fileName})
        fileProps.update({'Path': filePath})
        # fileProps.update({'type': "Directory" if isDir == True else "File"})
        fileProps.update({'Type': fType})
        fileProps.update({'Size': "%d (%s)" % (fSize, utils.getHumanSize(fSize))})
        fileProps.update({'Last modified': lastModified.toString(Qt.DefaultLocaleLongDate)})
        dlg = dialog.DlgProperties(fileProps)
        dlg.exec()

        self.outputMessage("=" * 80)
        self.showMessage("Show properties for %s" % fileName)
        for key in fileProps:
            self.outputMessage("%s : %s" % (key, fileProps[key]))
        self.outputMessage("=" * 80)            
            
#-------------------------------------------------------------------------------
# doProjectPropertiesAction()
#-------------------------------------------------------------------------------
    def doProjectPropertiesAction(self):
        if self.project is not None:
            dlg = dialog.DlgProperties(self.project.getProperties())
            dlg.exec()

            """
            self.outputMessage("=" * 80)
            self.showMessage("Show properties for %s" % fileName)
            for key in fileProps:
                self.outputMessage("%s : %s" % (key, fileProps[key]))
            self.outputMessage("=" * 80)            
            """
        else:
            self.showMessage("No open project")
            
#-------------------------------------------------------------------------------
# doExportProject()
#-------------------------------------------------------------------------------
    def doExportProject(self):
        if self.project is not None:
            self.project.exportProject()
        else:
            self.showMessage("No open project")
        
#-------------------------------------------------------------------------------
# doPackagesAction()
#-------------------------------------------------------------------------------
    def doPackagesAction(self):
        foundTab = False
        for i in range(0, self.tbwHighRight.count()):
            tab = self.tbwHighRight.widget(i)
            if isinstance(tab, pynter.TabPIP):
                foundTab = True
                self.tbwHighRight.setCurrentIndex(i)                        
        if foundTab == False:
            tabPackages = pynter.TabPIP(self)        
            self.tbwHighRight.addTab(tabPackages, "Packages")
            idxTab = self.tbwHighRight.count() - 1
            self.tbwHighRight.setTabIcon(idxTab, QIcon("pix/silk/icons/package.png"))
            self.tbwHighRight.setCurrentIndex(idxTab)               
        self.showMessage("Packages management")

#-------------------------------------------------------------------------------
# onChangeLowRight()
#-------------------------------------------------------------------------------
    def onChangeLowRight(self, index):
        # self.showMessage("TAB INDEX %d" % index)
        #-----------------------------------------------------------------------
        # Player smart pause
        #-----------------------------------------------------------------------
        if hasattr(self, 'movieWidget'):
            if ( settings.db['PLAYER_A_SMART_PAUSE'] == True and self.movieWidget.isVideoAvailable == False ) or ( settings.db['PLAYER_V_SMART_PAUSE'] == True and self.movieWidget.isVideoAvailable == True ):
                # index = self.tbwLowRight.currentIndex()
                if index == 2:
                    self.movieWidget.playForce()
                else:
                    self.movieWidget.pauseForce()
        #-----------------------------------------------------------------------
        # PyInstaller tab
        #-----------------------------------------------------------------------
        if index == 4:
            if self.txtMainFile.text() == "":
                tab = self.tbwHighRight.widget(self.tbwHighRight.currentIndex())
                if isinstance(tab, editor.WEditor):
                    self.txtMainFile.setText(tab.filename)           

#-------------------------------------------------------------------------------
# doBuildEXE()
#-------------------------------------------------------------------------------
    def doBuildEXE(self):
        pyinstall.buildEXE(self)
        
#-------------------------------------------------------------------------------
# changeEvent()
#-------------------------------------------------------------------------------
    def changeEvent(self, event):
        if hasattr(self, 'movieWidget'):
            if ( settings.db['PLAYER_A_SMART_PAUSE'] == True and self.movieWidget.isVideoAvailable == False ) or ( settings.db['PLAYER_V_SMART_PAUSE'] == True and self.movieWidget.isVideoAvailable == True ):
                if event.type() == QEvent.WindowStateChange:
                    if self.isMinimized():
                        self.movieWidget.pauseForce()
                    else:
                        index = self.tbwLowRight.currentIndex()
                        if index == 2:
                            self.movieWidget.playForce()

#-------------------------------------------------------------------------------
# setTabsText()
#-------------------------------------------------------------------------------
    def setTabsText(self, tabWidget, value):
        key = tabWidget.objectName()
        if key not in self.tabNames:
            names = []
            for i in range(0, tabWidget.count()):
                names.append(tabWidget.tabText(i))
            self.tabNames[key] = names
        if value == True:
            names = self.tabNames.get(key)
            for i in range(0, tabWidget.count()):
                tabWidget.setTabText(i, names[i])
        else:
            for i in range(0, tabWidget.count()):
                tabWidget.setTabText(i, "")
                
#-------------------------------------------------------------------------------
# colorBackgroundPicker()
#-------------------------------------------------------------------------------
    def colorBackgroundPicker(self):
        color = QColorDialog.getColor(QColor(self.bgColor))
        if QColor.isValid(color):
            self.bgColor = color.name()
            self.txtBackgroundColor.setText(self.bgColor)
            self.lblColorPickerSample.setStyleSheet("QWidget { background-color: %s; color: %s}" % (self.bgColor, self.fgColor))
    
#-------------------------------------------------------------------------------
# colorForegroundPicker()
#-------------------------------------------------------------------------------
    def colorForegroundPicker(self):
        color = QColorDialog.getColor(QColor(self.fgColor))
        if QColor.isValid(color):
            self.fgColor = color.name()
            self.txtForegroundColor.setText(self.fgColor)
            self.lblColorPickerSample.setStyleSheet("QWidget { background-color: %s; color: %s}" % (self.bgColor, self.fgColor))

#-------------------------------------------------------------------------------
# swapColors()
#-------------------------------------------------------------------------------
    def swapColors(self):
        self.bgColor, self.fgColor = self.fgColor, self.bgColor
        self.txtBackgroundColor.setText(self.bgColor)
        self.lblColorPickerSample.setStyleSheet("QWidget { background-color: %s; color: %s}" % (self.bgColor, self.fgColor))
        self.txtForegroundColor.setText(self.fgColor)
        self.lblColorPickerSample.setStyleSheet("QWidget { background-color: %s; color: %s}" % (self.bgColor, self.fgColor))
    
#-------------------------------------------------------------------------------
# verboseOutputChanged()
#-------------------------------------------------------------------------------
    def verboseOutputChanged(self, state):
        self.debug = (state == Qt.Checked)
        self.showMessage("Debug Mode %s" % str(self.debug))
        
#-------------------------------------------------------------------------------
# outputExport()
#-------------------------------------------------------------------------------
    def outputExport(self):
        home = expanduser("~")
        fileName = QFileDialog.getSaveFileName(self, 'Export Output', home, filter='*.txt', options = QFileDialog.DontUseNativeDialog)
        # fileName = QFileDialog.getOpenFileName(self,    tr("Open Image"), "/home/jana", tr("Image Files (*.png *.jpg *.bmp)"))
        if fileName[0]:
            with open(fileName[0], "w") as fOutput:
                fOutput.write(self.txtOutput.toPlainText())    
                self.showMessage("Exporting output to file %s" % fileName[0])
        else:
            self.showMessage("Cancelling export of output")
                
#-------------------------------------------------------------------------------
# outputClear()
#-------------------------------------------------------------------------------
    def outputClear(self):
        self.txtOutput.setPlainText("")
    
#-------------------------------------------------------------------------------
# changeFocusText()
#-------------------------------------------------------------------------------
    def changeFocusText(self):
        focusFileName = os.path.join(os.path.join(self.appDir, const.FOCUS_FILE))
        with open(focusFileName, 'w') as focusFile:
            focusFile.write(str(self.txtFocus.toPlainText()))

#-------------------------------------------------------------------------------
# scratchFile()
#-------------------------------------------------------------------------------
    def scratchFile(self):
        utils.createDirectory(settings.db['BSIDE_REPOSITORY'], const.SCRATCH_FOLDER)
        name = scratch.createScratchFile(os.path.join(settings.db['BSIDE_REPOSITORY'], const.SCRATCH_FOLDER))
        idx = self.tvwModel.index(name)
        self.tvwRepository.scrollTo(idx)
        self.tvwRepository.setCurrentIndex(idx)        
        self.showMessage("Creating scratch file %s" % name)
        self.openFileFromName(name)
        
#-------------------------------------------------------------------------------
# runScript()
#-------------------------------------------------------------------------------
    def runScript(self):
        tabEditor = self.tbwHighRight.widget(self.tbwHighRight.currentIndex())        
        if tabEditor.filename is not None:
            if settings.db['BSIDE_SAVE_BEFORE_RUN'] == True:
                # tabEditor.saveFile()     
                self.saveAll()
            pybin = sys.executable
            script = tabEditor.filename    
            
            dlg = dialog.DlgRunScript(script)
            dlg.exec()
            if dlg.result() != 0:
                self.showMessage("=" * 80)
                self.showMessage("Run script %s" % script)
                self.showMessage("Parameters [%s]" % dlg.params)
                self.showMessage("External Shell %s" % str(dlg.externalShell))
                cmd = "%s %s %s" % (pybin, script, dlg.params)
                if dlg.externalShell == True:
                    self.btnKillProcess.setEnabled(False)
                    if platform.system() == 'Windows':
                        os.system("start /wait cmd /c \"%s & pause\"" % cmd)
                    else:
                        os.system("gnome-terminal -e 'bash -c \"%s; echo; read -p Paused\"'" % cmd)
                    self.showMessage("End of running script %s" % script)
                    self.showMessage("=" * 80)                
                else:
                    cmd = (pybin, "-u", script, dlg.params)
                    self.btnKillProcess.setEnabled(True)
                    self.tbwLowRight.setCurrentIndex(0)
                    QGuiApplication.processEvents()                     
                    # self.tCmd = shrealding.Shreald(self, "%s -u %s" % (pybin, script))
                    self.tCmd = shrealding.Shreald(self, cmd, os.path.dirname(script))
                    self.tCmd.linePrinted.connect(self.handleLine)                    
            else:
                self.showMessage("Cancel running script %s" % script)   

#-------------------------------------------------------------------------------
# handleLine()
#-------------------------------------------------------------------------------
    def handleLine(self, line):
        if line !=  "":
            # print("Handle %s" % line)
            if line[0] == '1':
                self.showMessage("[OUT] %s " % line[1:].rstrip())
            elif line[0] == '2':
                self.showMessage("[ERR] %s " % line[1:].rstrip())
            elif line[0] == 'x':
                self.killProcess()
            
#-------------------------------------------------------------------------------
# killProcess()
#-------------------------------------------------------------------------------
    def killProcess(self):        
        self.showMessage("Ending application with PID %s" % str(self.tCmd.process.pid))
        self.showMessage("End of script %s" % str(self.tCmd.cmd[2]))
        try:
            self.tCmd.kill()
        except:
            pass
        self.btnKillProcess.setEnabled(False)
        if self.tCmd.returncode is not None:
            self.showMessage("Return Code : %d" % self.tCmd.returncode)
        self.showMessage("=" * 80)                        
        
#-------------------------------------------------------------------------------
# newProject()
#-------------------------------------------------------------------------------
    def newProject(self):
        self.project = projects.Project(parent = self)
        if self.project.createNew():
            self.showMessage("Project created")
        else:
            self.project = None
            self.showMessage("No project")

#-------------------------------------------------------------------------------
# openProject()
#-------------------------------------------------------------------------------
    def openProject(self):
        home = settings.db['BSIDE_REPOSITORY']
        filename = QFileDialog.getOpenFileName(self, 'Open Project', home, filter='*.bsix', options = QFileDialog.DontUseNativeDialog)
        if filename[0]:
            if self.project is not None:
                self.project.close()
            self.tvwProject.setModel(self.tvmProject)
            self.tvwProject.setAnimated(False)
            self.tvwProject.setIndentation(10)
            self.tvwProject.setSortingEnabled(True)        
            for i in range(1, self.tvwProject.header().length()):
                self.tvwProject.hideColumn(i)
            self.tvwProject.sortByColumn(0, Qt.AscendingOrder)
            projectName = os.path.basename(os.path.normpath(os.path.dirname(filename[0])))
            self.showDebug(projectName)
            self.project = projects.Project(parent = self)
            self.project.set(projectName)
            self.project.open()
        
#-------------------------------------------------------------------------------
# closeProject()
#-------------------------------------------------------------------------------
    def closeProject(self):
        if self.project is not None:
            self.project.close()
            # self.tvmProject.setRootPath(expanduser("~"))        
            # self.tvwProject.setRootIndex(self.tvmProject.index(expanduser("~")))
            self.tvwProject.setModel(None)
            self.tbwHighLeft.setCurrentIndex(0)
            self.lblProject.setText(const.PROJECT_NONE)
            self.lblProjectName.setText(const.PROJECT_NONE)          
            self.lblProjectStatus.setText("N/A")
            self.project = None
        else:
            self.showMessage("No open project")

            
#-------------------------------------------------------------------------------
# switchFullScreen()
#-------------------------------------------------------------------------------
    def switchFullScreen(self):
        """
        if self.isFullScreen() == False:
            self.showFullScreen()            
        else:
            self.showNormal()
        """
        if self.windowState() & Qt.WindowFullScreen:
            print("switch normal")
            self.showNormal()
        else:
            print("switch full screen")
            self.showFullScreen()            
            
#-------------------------------------------------------------------------------
# helpPython()
#-------------------------------------------------------------------------------
    def helpPython(self):
        filepath = settings.db['BSIDE_PYTHON_HELP_FILE']
        try:
            if platform.system() == 'Darwin':       # macOS
                subprocess.call(('open', filepath))
            elif platform.system() == 'Windows':    # Windows
                os.startfile(filepath)
            else:                                   # linux variants
                subprocess.call(('xdg-open', filepath))
        except:
            self.showMessage("Help file not found")
                    
"""
MARKDOWN

import markdown

['EDITOR_MD_EXTENSIONS', ['tables', 'fenced_code', 'codehilite', 'nl2br']]

def textChanged(self):
        filePath = self.tvwMenuModel.filePath(self.idxSelectedFile)
        open(filePath, 'w').write(self.txtMarkdown.toPlainText())
        self.txtHTML.setText(markdown.markdown(self.txtMarkdown.toPlainText(), extensions=settings.db['EDITOR_MD_EXTENSIONS']))
""" 

#-------------------------------------------------------------------------------
# Class IconProvider
#-------------------------------------------------------------------------------
class IconProvider(QFileIconProvider):
#-------------------------------------------------------------------------------
# icon()
#-------------------------------------------------------------------------------
    def icon(self, fileInfo):
        if fileInfo.isDir():
            return QIcon("pix/16x16/Folder.png") 
        if fileInfo.suffix() == "py":
            return QIcon("pix/icons/python.png") 
        if fileInfo.suffix() == "md":
            return QIcon("pix/icons/markdown.png") 
        if fileInfo.suffix() == "xml":
            return QIcon("pix/icons/xml.png") 
        if fileInfo.suffix() == "ui":
            return QIcon("pix/icons/QtUI.png") 
        if fileInfo.suffix() == "db":
            return QIcon("pix/icons/database.png") 
        if fileInfo.suffix() == "sql":
            return QIcon("pix/icons/database.png") 
        if fileInfo.suffix() == "zip":
            return QIcon("pix/icons/zip.png") 
        if fileInfo.suffix() == "txt":
            return QIcon("pix/icons/txt.png") 
        if fileInfo.suffix() == "bsix":
            return QIcon("pix/bside.png") 
        return QFileIconProvider.icon(self, fileInfo)
    
    """
    html, chm, txt, ui, spec, pyc, tar, gz, gzip, rar, png, mp3, avi, pdf, exe
    """        
