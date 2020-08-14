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

#-------------------------------------------------------------------------------
# Imports
#-------------------------------------------------------------------------------
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from subprocess import PIPE
import platform
import socket
import time
import os
import subprocess
import re

import utils
import settings
import shrealding
import web

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
    bsideMode = False

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
        
        css1 = "QWidget {border: 2px solid gray; border-radius: 6px; background-color: %s; color: %s; font-family: %s; font-size: %spx}" % (settings.db['SHELL_BACKGROUND'], settings.db['SHELL_FOREGROUND'], settings.db['SHELL_FONT_FAMILY'], settings.db['SHELL_FONT_SIZE'])
        css2 = 'font: %dpt "%s";' % (settings.db['SHELL_FONT_SIZE'], settings.db['SHELL_FONT_FAMILY'])

        self.lblShellPrompt = QLabel(settings.db['SHELL_PROMPT'])
        self.lblShellPrompt.setStyleSheet(css2)
        self.txtCommand = QLineEdit()
        self.txtCommand.setStyleSheet(css1)
        self.txtCommand.installEventFilter(self)
        
        self.txtConsoleOut = QTextEdit()
        self.txtConsoleOut.setAcceptRichText(True)
        self.txtConsoleOut.setStyleSheet(css1)
        self.txtConsoleOut.setReadOnly(True)
        
        self.lblTime = QLabel("0:00:00.00")
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
        self.time1 = time.time()
        if command == "cls" or command == "clear":
            self.txtConsoleOut.setText("")            
            self.finalizeCommand()
        elif (command == "quit" or command == "exit") and self.bsideMode == False:
            self.close()
        elif command == "!bside+" or command == "!b+":
            self.lblShellPrompt.setText("!!!>")
            self.bsideMode = True
            self.txtConsoleOut.append("Bside console activated, type \"help\" to see available commands.\n")
            self.finalizeCommand()
        elif command == "!bside-" or command == "!b-":
            self.lblShellPrompt.setText(settings.db['SHELL_PROMPT'])
            self.bsideMode = False
            self.txtConsoleOut.append("End of Bside console.\n")
            self.finalizeCommand()
        elif command[1:2] == ":":
            self.CurrentDrive = command[0:2].upper()
            self.CurrentDir = os.sep
            self.txtConsoleOut.append("<b>%s %s</b>" % (settings.db['SHELL_PROMPT'], command))
            self.finalizeCommand()
        elif command[0:3] == "cd ":
            #-------------------------------------------------------------------
            # TODO : Fix the directory navigation
            self.CurrentDir = os.path.abspath(command[3:])
            #-------------------------------------------------------------------
            self.txtConsoleOut.append("<b>%s %s</b>" % (settings.db['SHELL_PROMPT'], command))
            self.finalizeCommand()
        else:
            if self.bsideMode == False:
                self.txtConsoleOut.append("<b>%s %s</b>" % (settings.db['SHELL_PROMPT'], command))
                self.btnBreak.setEnabled(True)
                QGuiApplication.processEvents()                     
                self.tCmd = shrealding.Shreald(self.parent, command, self.CurrentDir, shell=True)
                self.tCmd.linePrinted.connect(self.handleLine)                    
                self.lblTime.setText("---")
                self.txtCommand.setEnabled(False)
            else:
                self.bsideCommand(command)
                self.finalizeCommand()

#-------------------------------------------------------------------------------
# bsideCommand()
#-------------------------------------------------------------------------------
    def bsideCommand(self, command):
        """
        ================================================================
        Emulated internal commands :
        ================================================================
        X help
        X set <parameter> = <value>
        > save repository
        > quit IDE
        > quit force IDE
        X start web server
        X stop web server
        > send report
        > check update
        > export log IDE
        > export log web
        > export config
        > open project
        > export project as zip
        > open log file
        > edit file
        > save file
        > save project
        > close project
        > close tab
        > add TODO note
        > check TODO note
        > add tool to menu
        > open help file
        > open URL
        > shutdown computer
        > set alarm
        > start timer
        > start stopwatch
        """
        self.txtConsoleOut.append("<b>%s %s</b>" % ("!!!>", command))
        if command.lower() == "web start":
            self.txtConsoleOut.append("%s" % web.startServer(self.parent))
        elif command.lower() == "web stop":
            self.txtConsoleOut.append("%s" % web.stopServer(self.parent))
        elif command.lower() == "web status":
            self.txtConsoleOut.append("%s" % web.statusServer(self.parent))
        elif command.lower() == "web restart":
            self.txtConsoleOut.append("%s" % web.restartServer(self.parent))
        elif command.lower() == "help":
            self.txtConsoleOut.append("%s" % self.bsideHelp())
        else:
            if not self.cmdSet(command):
                self.txtConsoleOut.append("%s" % "Error : Unknown Bside command.\nPlease type \"help\" to have the list of available commands.")
        # self.txtConsoleOut.append("\n")

#-------------------------------------------------------------------------------
# cmdSet()
#-------------------------------------------------------------------------------
    def cmdSet(self, cmd):
        # set param = value
        m = re.search('^set\s*([\w]+)\s*=\s*(.+)', cmd)
        if m is not None:
            param = m.group(1)
            value = m.group(2)
            self.txtConsoleOut.append("%s => %s" % (param, str(value)))

            if type(settings.db[param]) is str:
                settings.db[param] = value
            elif type(settings.db[param]) is int:
                settings.db[param] = int(value)
            elif type(settings.db[param]) is float:
                settings.db[param] = float(value)
            elif type(settings.db[param]) is bool:
                if value.lower() == "true":
                    settings.db[param] = True
                else:
                    settings.db[param] = False
            else:
                settings.db[param] = str(value)

            rc = True
        else:
            # set param
            m = re.search('^set\s*([\w]*$)', cmd)
            if m is not None:
                param = m.group(1)
                params = settings.getSet(param)
                html = "<p><table>\n"
                for key in sorted(params):
                    html = html + "<tr><td><b>" + key + "</b></td><td>&nbsp;=>&nbsp;</td><td>" + str(params[key]) + "</td></tr>\n"
                html = html + "</table></p>"
                self.txtConsoleOut.append(html)
                rc = True
            else:
                rc = False
        return rc
            
#-------------------------------------------------------------------------------
# bsideHelp()
#-------------------------------------------------------------------------------
    def bsideHelp(self):
        html = """
<p>
Bside console commands :
<table>
<tr><td>------------------------</b></td><td>&nbsp;</td></tr>
<tr><td><b>help</b></td><td>Display this help</td></tr>
<tr><td><b>set [param]</b></td><td>Display all the parameters starting with [param]</td></tr>
<tr><td><b>set [param] = [value]</b></td><td>Set a parameter to the defined value</td></tr>
<tr><td><b>web start</b></td><td>Start the embedded web server</td></tr>
<tr><td><b>web stop</b></td><td>Stop the embedded web server</td></tr>
<tr><td><b>web status</b></td><td>Display the status of the web server</td></tr>
<tr><td><b>web restart</b></td><td>Stop and restart the web server</td></tr>
<tr><td>------------------------</b></td><td>&nbsp;</td></tr>
<tr><td><b>!bside+</b></td><td>Activate the Bside console</td></tr>
<tr><td><b>!bside-</b></td><td>Go back to OS shell console</td></tr>
</table>
</p>
        """
        return html
    
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
        # elapsed = (self.time2 - self.time1)*1000.0
        # self.lblTime.setText("{:.3f} ms".format(elapsed))
        elapsed = self.time2 - self.time1
        self.lblTime.setText(utils.getHumanTime(elapsed))
        
        self.flagBusy = False
        self.btnEnter.setEnabled(True)
        # self.statusBar.showMessage("Running...", settings.dbSettings['TIMER_STATUS'])
        self.lblLED.setPixmap(QPixmap("pix/icons/led_green.png"))
        if platform.system() == 'Windows':
            self.lblCDR.setText(self.CurrentDrive)
        self.lblPWD.setText(self.CurrentDir)
        if hasattr(self, "tCmd"):
            if self.tCmd.returncode is not None:
                self.lblRC.setText("RC=%d" % self.tCmd.returncode)
        self.txtConsoleOut.append("\n")
        self.txtCommand.setEnabled(True)
        self.txtCommand.selectAll()
        self.txtCommand.setFocus()
        self.btnBreak.setEnabled(False)
