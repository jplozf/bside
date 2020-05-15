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
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from subprocess import Popen, PIPE
import platform
import socket
import time
import os
import subprocess

import settings
import shrealding

if platform.system() == 'Windows':
    import win32gui

#-------------------------------------------------------------------------------
# Class LXShell
#-------------------------------------------------------------------------------
class LXShell(QWidget):
#-------------------------------------------------------------------------------
# __init__()
#-------------------------------------------------------------------------------
    def __init__(self, parent = None):
        QWidget.__init__(self)
        self.parent = parent
        self.process = QProcess(self)
        self.terminal = QWidget(self)
        
        hwnd = self.terminal.winId().__int__()
        if settings.db['SHELL_UI'] == "LINUX_SHELL_RXVT":
            self.process.start(settings.db['LINUX_SHELL_RXVT'] % str(hwnd))
        elif settings.db['SHELL_UI'] == "LINUX_SHELL_XTERM":
            self.process.start(settings.db['LINUX_SHELL_XTERM'] % str(hwnd))
        elif settings.db['SHELL_UI'] == "LINUX_SHELL_OTHER":
            self.process.start(settings.db['LINUX_SHELL_OTHER'] % str(hwnd))

        layout = QVBoxLayout(self)
        layout.addWidget(self.terminal)


#-------------------------------------------------------------------------------
# Class WxShell
#-------------------------------------------------------------------------------
class WXShell(QWidget):
#-------------------------------------------------------------------------------
# __init__()
#-------------------------------------------------------------------------------
    def __init__(self, parent = None):
        QWidget.__init__(self, parent)
        self.parent = parent
        # create a process
        with open("runme.cmd", "w") as f: 
            f.write("start /wait c:\\Windows\\system32\\cmd.exe /k dir") 
        # exePath = "runme.cmd"
        # exePath = "C:\\Windows\\system32\\cmd.exe /k dir"
        # exePath = "C:\\Windows\\system32\\cmd.exe"
        # os.system("cmd.exe /k dir")
        exePath= "C:\\Users\\jpliguori\\bin\\cmder_mini\\cmder.exe"
        # subprocess.Popen(exePath, stdin=PIPE, stdout=PIPE, stderr=PIPE)
        # subprocess.Popen(exePath)
        # os.system(exePath)
        subprocess.run(exePath, stdin=PIPE)
        # subprocess.call("start")
        time.sleep(0.5)
        # hwnd = win32gui.FindWindow("ConsoleWindowClass", None)
        hwnd = win32gui.FindWindow("VirtualConsoleClass", None)
        # hwnd = win32gui.FindWindow("mintty", None)          
        print("hWnd = %d" % hwnd)
        # time.sleep(0.05)
        widget = self.createWindowContainer(QWindow.fromWinId(hwnd), self)
        vLayout = QVBoxLayout(self)
        vLayout.addWidget(widget)
        widget.setFocus()
                    
#-------------------------------------------------------------------------------
# Class WShell
# Default shell, OS independant
#-------------------------------------------------------------------------------
class WShell(QWidget):    
    aCommands = []
    iCommands = 0
    CurrentOS = platform.system()
    CurrentDrive = os.path.splitdrive(os.path.realpath(__file__))[0]
    CurrentDir = os.path.splitdrive(os.path.dirname(os.path.realpath(__file__)))[1]

#-------------------------------------------------------------------------------
# __init__()
#-------------------------------------------------------------------------------
    def __init__(self, parent = None):
        QWidget.__init__(self, parent)
        self.parent = parent

        self.btnEnter = QPushButton()
        self.btnEnter.setIcon(QIcon("pix/16x16/Player Play.png"))
        self.btnEnter.clicked.connect(self.runCommand)
        
        self.btnBreak = QPushButton()
        self.btnBreak.setIcon(QIcon("pix/16x16/Player Stop.png"))
        self.btnBreak.clicked.connect(self.killProcess)
        self.btnBreak.setEnabled(False)
        
        css = "QWidget {border: 2px solid gray; border-radius: 6px; background-color: %s; color: %s; font-family: %s; font-size: %spx}" % (settings.db['SHELL_BACKGROUND'], settings.db['SHELL_FOREGROUND'], settings.db['SHELL_FONT_FAMILY'], settings.db['SHELL_FONT_SIZE'])
        
        self.lblShellPrompt = QLabel(settings.db['SHELL_PROMPT'])
        self.txtCommand = QLineEdit()
        self.txtCommand.setStyleSheet(css)
        self.txtCommand.installEventFilter(self)
        # self.txtCommand.setFont(QFont('Courier', 10))
        
        self.txtConsoleOut = QTextEdit()
        self.txtConsoleOut.setStyleSheet(css)
        self.txtConsoleOut.setReadOnly(True)
        
        self.lblTime = QLabel("0.000 ms")
        self.lblTime.setFrameShape(QFrame.Panel)
        self.lblTime.setFrameShadow(QFrame.Sunken)
        self.lblTime.setLineWidth(1)
        self.lblTime.setFont(QFont('Courier', 10))

        self.lblRC = QLabel("RC=0")
        self.lblRC.setFrameShape(QFrame.Panel)
        self.lblRC.setFrameShadow(QFrame.Sunken)
        self.lblRC.setLineWidth(1)
        self.lblRC.setFont(QFont('Courier', 10))

        self.lblLED = QLabel()
        self.lblLED.setPixmap(QPixmap("pix/icons/led_green.png"))
        
        if platform.system() == 'Windows':
            self.lblCDR = QLabel(self.CurrentDrive)
            self.lblCDR.setFrameShape(QFrame.Panel)
            self.lblCDR.setFrameShadow(QFrame.Sunken)
            self.lblCDR.setLineWidth(1)
            self.lblCDR.setFont(QFont('Courier', 10))
        
        self.lblPWD = QLabel(self.CurrentDir)
        self.lblPWD.setFrameShape(QFrame.Panel)
        self.lblPWD.setFrameShadow(QFrame.Sunken)
        self.lblPWD.setLineWidth(1)
        self.lblPWD.setFont(QFont('Courier', 10))
        self.flagBusy = False
        
        vLayout = QVBoxLayout(self)
        vLayout.addWidget(self.txtConsoleOut)
        hLayout = QHBoxLayout(self)
        hLayout.addWidget(self.lblShellPrompt)
        hLayout.addWidget(self.txtCommand)
        hLayout.addWidget(self.btnEnter)
        hLayout.addWidget(self.btnBreak)
        if platform.system() == 'Windows':
            hLayout.addWidget(self.lblCDR)
        hLayout.addWidget(self.lblPWD)
        hLayout.addWidget(self.lblTime)
        hLayout.addWidget(self.lblRC)
        hLayout.addWidget(self.lblLED)
        vLayout.addLayout(hLayout)
        
        self.colLabel = self.lblRC.palette().button().color();
        # self.txtConsoleOut.append(80 * '=')
        self.txtConsoleOut.append(platform.platform())
        self.txtConsoleOut.append("Hostname is %s (%s)" % (socket.gethostname(), platform.machine()))
        self.txtConsoleOut.append(settings.db['SHELL_BANNER'])
        # self.txtConsoleOut.append(80 * '=')
        self.txtConsoleOut.append("")
        self.txtConsoleOut.append("")
        self.txtCommand.setFocus()
        
#-------------------------------------------------------------------------------
# runCommand2()
#-------------------------------------------------------------------------------
    def runCommand2(self):        
        self.flagBusy = True
        self.btnEnter.setEnabled(False)
        # self.statusBar.showMessage("Running...", settings.dbSettings['TIMER_STATUS'])
        self.lblLED.setPixmap(QPixmap("pix/icons/led_red.png"))
        self.repaint()
        self.aCommands.append(self.txtCommand.text())
        self.iCommands = self.iCommands + 1        
        command = str(self.txtCommand.text()).strip()        
        # if self.chkClearConsole.isChecked():
        #     self.txtConsoleOut.setText("")
        if command == "cls" or command == "clear":
            self.txtConsoleOut.setText("")
            # self.statusBar.showMessage("Command executed", settings.dbSettings['TIMER_STATUS'])
        elif command == "quit" or command == "exit":
            self.close()
        elif command[1:2] == ":":
            self.CurrentDrive = command[0:2].upper()
            self.CurrentDir = os.sep
            # self.statusBar.showMessage("Current drive changed", settings.dbSettings['TIMER_STATUS'])
        elif command[0:3] == "cd ":
            self.CurrentDir = os.path.abspath(command[3:])
            # self.statusBar.showMessage("Current directory changed", settings.dbSettings['TIMER_STATUS'])
        else:
            self.txtConsoleOut.append(settings.db['SHELL_PROMPT'] + command + "\n")
            time1 = time.time()
            # p = Popen(command, stdin=PIPE, stdout=PIPE, stderr=PIPE, bufsize=1, universal_newlines=True, shell = True)
            p = Popen(command, cwd=os.path.join(self.CurrentDrive, self.CurrentDir), stdin=PIPE, stdout=PIPE, stderr=PIPE, bufsize=1, shell = True)
            p.poll()
            while True:
                line = p.stdout.readline()
                if self.CurrentOS == "Windows":
                    sLine = line.decode(settings.db['SHELL_CODEPAGE']).rstrip()
                    oLine = self.patchChars(sLine)
                    self.txtConsoleOut.append(oLine)
                else:
                    self.txtConsoleOut.append(line.decode(settings.db['SHELL_CODEPAGE']).rstrip())
                self.repaint()
                if not line and p.poll is not None: 
                    break

            while True:
                err = p.stderr.readline()
                if self.CurrentOS == "Windows":
                    sLine = err.decode(settings.db['SHELL_CODEPAGE']).rstrip()
                    oLine = self.patchChars(sLine)
                    self.txtConsoleOut.append(oLine)
                else:
                    self.txtConsoleOut.append(err.decode(settings.db['SHELL_CODEPAGE']).rstrip())
                self.repaint()
                if not err and p.poll is not None: 
                    break

            self.txtConsoleOut.moveCursor(QTextCursor.End)
            rc = p.poll()
            self.lblRC.setText("RC=" + str(rc))
            if rc != 0:
                self.lblRC.setStyleSheet('background-color : red; color: white')
            else:
                self.lblRC.setStyleSheet('background-color:' + self.colLabel.name() + '; color: black')
            time2 = time.time()
            elapsed = (time2-time1)*1000.0
            # self.statusBar.showMessage("Command executed in {:.3f} ms".format(elapsed), settings.dbSettings['TIMER_STATUS'])
            self.lblTime.setText("{:.3f} ms".format(elapsed))
        # self.tabWidget.setCurrentIndex(0)
        self.flagBusy = False
        self.btnEnter.setEnabled(True)
        if platform.system() == 'Windows':
            self.lblCDR.setText(self.CurrentDrive)
        self.lblPWD.setText(self.CurrentDir)
        self.lblLED.setPixmap(QPixmap("pix/icons/led_green.png"))
        self.txtCommand.selectAll()
        self.txtCommand.setFocus()

#-------------------------------------------------------------------------------
# patchChars()
#-------------------------------------------------------------------------------
    def patchChars(self, s):
        myChars = {'“':'ô', 'Š':'ê', '‚':'é', 'ÿ':''}
        foo = s.split()
        ret = []
        for item in foo:
            ret.append(myChars.get(item, item)) # Try to get from dict, otherwise keep value
        return(" ".join(ret))

#-------------------------------------------------------------------------------
# eventFilter()
#-------------------------------------------------------------------------------
    def eventFilter(self, object, event):
        if object is self.txtCommand and event.type() == event.KeyPress:
            key = event.key()
            if key == Qt.Key_Up:
                if self.iCommands > 0:
                    self.iCommands = self.iCommands - 1
                else:
                    self.iCommands = len(self.aCommands) - 1
                if len(self.aCommands)>0:    
                    self.txtCommand.setText(self.aCommands[self.iCommands])
            elif key == Qt.Key_Down:
                if self.iCommands < (len(self.aCommands) - 1):
                    self.iCommands = self.iCommands + 1
                else:
                    self.iCommands = 0
                if len(self.aCommands)>0:
                    self.txtCommand.setText(self.aCommands[self.iCommands])
            elif key in (Qt.Key_Enter, Qt.Key_Return):
                self.runCommand()
        return False
    
#-------------------------------------------------------------------------------
# runCommand()
#-------------------------------------------------------------------------------
    def runCommand(self):        
        self.flagBusy = True
        self.btnEnter.setEnabled(False)
        self.lblLED.setPixmap(QPixmap("pix/icons/led_red.png"))
        self.repaint()
        self.aCommands.append(self.txtCommand.text())
        self.iCommands = self.iCommands + 1        
        command = str(self.txtCommand.text()).strip()        
        # if self.chkClearConsole.isChecked():
        #     self.txtConsoleOut.setText("")
        if command == "cls" or command == "clear":
            self.txtConsoleOut.setText("")            
            self.finalizeCommand()
        elif command == "quit" or command == "exit":
            self.close()
        elif command[1:2] == ":":
            self.CurrentDrive = command[0:2].upper()
            self.CurrentDir = os.sep
            self.txtConsoleOut.append(settings.db['SHELL_PROMPT'] + command)
            self.finalizeCommand()
        elif command[0:3] == "cd ":
            self.CurrentDir = os.path.abspath(command[3:])
            self.txtConsoleOut.append(settings.db['SHELL_PROMPT'] + command)
            self.finalizeCommand()
        else:
            self.txtConsoleOut.append(settings.db['SHELL_PROMPT'] + command)
            self.time1 = time.time()
            self.btnBreak.setEnabled(True)
            QGuiApplication.processEvents()                     
            self.tCmd = shrealding.Shreald(self.parent, command, self.CurrentDir, shell=True)
            self.tCmd.linePrinted.connect(self.handleLine)                    
            self.lblTime.setText("---")
            self.txtCommand.setEnabled(False)

#-------------------------------------------------------------------------------
# handleLine()
#-------------------------------------------------------------------------------
    def handleLine(self, line):
        if line !=  "":
            # print("Shell Handle %s" % line)
            if line[0] == '1':
                self.txtConsoleOut.append("%s" % line[1:].rstrip())
            elif line[0] == '2':
                self.txtConsoleOut.append("%s" % line[1:].rstrip())
            elif line[0] == 'x':
                self.killProcess()

#-------------------------------------------------------------------------------
# killProcess()
#-------------------------------------------------------------------------------
    def killProcess(self):        
        try:
            self.tCmd.kill()
        except:
            pass
        self.finalizeCommand()

#-------------------------------------------------------------------------------
# finalizeCommand()
#-------------------------------------------------------------------------------
    def finalizeCommand(self):
        self.time2 = time.time()
        elapsed = (self.time2 - self.time1)*1000.0
        self.lblTime.setText("{:.3f} ms".format(elapsed))
        
        self.flagBusy = False
        self.btnEnter.setEnabled(True)
        # self.statusBar.showMessage("Running...", settings.dbSettings['TIMER_STATUS'])
        self.lblLED.setPixmap(QPixmap("pix/icons/led_green.png"))
        if platform.system() == 'Windows':
            self.lblCDR.setText(self.CurrentDrive)
        self.lblPWD.setText(self.CurrentDir)
        self.txtCommand.setEnabled(True)
        self.txtCommand.selectAll()
        self.txtCommand.setFocus()
        self.btnBreak.setEnabled(False)
