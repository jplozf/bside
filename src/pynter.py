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
# Lot of credits and thanks to Taven (daegontaven)
#-------------------------------------------------------------------------------
# Imports
#-------------------------------------------------------------------------------
import re
import sys
import subprocess
import time
import platform
from code import InteractiveConsole

from PyQt5.QtCore import pyqtSlot, QThread, QObject, pyqtSignal, QTimer, Qt
from PyQt5.QtGui import QTextOption, QTextCursor
from PyQt5.QtWidgets import *
from PyQt5.Qt import *

if platform.system() == 'Windows':
    import win32gui

import settings
import utils
import shrealding

#-------------------------------------------------------------------------------
# Class ConsoleBuffer
#-------------------------------------------------------------------------------
class ConsoleBuffer(QObject):
    excrete = pyqtSignal(str)
#-------------------------------------------------------------------------------
# __init__()
#-------------------------------------------------------------------------------
    def __init__(self, parent=None, minimum=0.050):
        super(ConsoleBuffer, self).__init__(parent)
        self.minimum = minimum
        self.last_time = time.monotonic() - minimum
        self.buffer = []
        self.timer = QTimer()
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self._excrete)

    @pyqtSlot(str)
#-------------------------------------------------------------------------------
# consume()
#-------------------------------------------------------------------------------
    def consume(self, s):
        self.buffer.append(s)

        delta = time.monotonic() - self.last_time
        remaining = self.minimum - delta
        if remaining <= 0:
            self._excrete()
        elif not self.timer.isActive():
            self.timer.start(int(1000 * remaining))

#-------------------------------------------------------------------------------
# _excrete()
#-------------------------------------------------------------------------------
    def _excrete(self):
        self.timer.stop()
        s = ''.join(self.buffer)
        if len(s):
            self.last_time = time.monotonic()
            self.excrete.emit(s)
        self.buffer = []


#-------------------------------------------------------------------------------
# Class ConsoleStream
#-------------------------------------------------------------------------------
class ConsoleStream(QObject):
    """
    Custom StreamIO class that handles when send data
    to console_log
    """
    written = pyqtSignal(str)
#-------------------------------------------------------------------------------
# __init__()
#-------------------------------------------------------------------------------
    def __init__(self, parent=None):
        super(ConsoleStream, self).__init__(parent)

#-------------------------------------------------------------------------------
# write()
#-------------------------------------------------------------------------------
    def write(self, string):
        self.written.emit(string)


#-------------------------------------------------------------------------------
# Class PythonInterpreter
#-------------------------------------------------------------------------------
class PythonInterpreter(QObject, InteractiveConsole):
    """
    A reimplementation of the builtin InteractiveConsole to
    work with threads.
    """
    push_command = pyqtSignal(str)
    multi_line = pyqtSignal(bool)
    output = pyqtSignal(str)
    error = pyqtSignal(str)
#-------------------------------------------------------------------------------
# __init__()
#-------------------------------------------------------------------------------
    def __init__(self, parent=None):
        super(PythonInterpreter, self).__init__(parent)
        self.locals = {}
        InteractiveConsole.__init__(self, self.locals)
        self.stream = ConsoleStream(self)
        self.push_command.connect(self.command)

#-------------------------------------------------------------------------------
# write()
#-------------------------------------------------------------------------------
    def write(self, string):
        self.error.emit(string)

#-------------------------------------------------------------------------------
# runcode()
#-------------------------------------------------------------------------------
    def runcode(self, code):
        """
        Overrides and captures stdout and stdin from
        InteractiveConsole.
        """
        sys.stdout = self.stream
        sys.stderr = self.stream
        sys.excepthook = sys.__excepthook__
        result = InteractiveConsole.runcode(self, code)
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__
        return result

    @pyqtSlot(str)
#-------------------------------------------------------------------------------
# command()
#-------------------------------------------------------------------------------
    def command(self, command):
        """
        :param command: line retrieved from console_input on
                        returnPressed
        """
        result = self.push(command)
        self.multi_line.emit(result)

#-------------------------------------------------------------------------------
# Class LXInter
#-------------------------------------------------------------------------------
class LXInter(QWidget):
#-------------------------------------------------------------------------------
# __init__()
#-------------------------------------------------------------------------------
    def __init__(self, filename = None, parent = None, window = None):
        QWidget.__init__(self)
        self.parent = parent
        self.window = window

        self.process = QProcess(self)
        self.terminal = QWidget(self)
        
        hwnd = self.terminal.winId().__int__()
        self.process.start(settings.db['LINUX_CONSOLE'] % str(hwnd))

        layout = QVBoxLayout(self)
        layout.addWidget(self.terminal)


#-------------------------------------------------------------------------------
# Class WXInter
#-------------------------------------------------------------------------------
class WXInter(QWidget):
#-------------------------------------------------------------------------------
# __init__()
#-------------------------------------------------------------------------------
    def __init__(self, filename = None, parent = None, window = None):
        QWidget.__init__(self, parent)
        self.parent = parent
        self.window = window

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
# Class WInter
#-------------------------------------------------------------------------------
class WInter(QWidget):    
#-------------------------------------------------------------------------------
# __init__()
#-------------------------------------------------------------------------------
    def __init__(self, filename = None, parent = None, window = None):
        QWidget.__init__(self, parent)
        self.parent = parent
        self.window = window
        
        css1 = 'border: 2px solid gray; border-radius: 6px; font: %dpt "%s"; background-color: %s; color: %s;' % (settings.db['CONSOLE_FONT_SIZE'],settings.db['CONSOLE_FONT'],settings.db['CONSOLE_COLOR_BACKGROUND'],settings.db['CONSOLE_COLOR_FOREGROUND'])        
        css2 = 'font: %dpt "%s";' % (settings.db['CONSOLE_FONT_SIZE'],settings.db['CONSOLE_FONT'])
        self.consoleLog = QPlainTextEdit()
        self.consoleLog.setStyleSheet(css1)
        self.consoleLog.setReadOnly(True)
        self.consolePrompt = QLabel()
        self.consolePrompt.setStyleSheet(css2)
        self.consoleInput = QLineEdit()
        self.consoleInput.setStyleSheet(css1)
        self.consoleInput.installEventFilter(self)
        self.consoleCopy = QPushButton()
        self.consoleCopy.setIcon(QIcon(QPixmap("pix/16x16/Clipboard Paste.png")))
        self.consoleCopy.clicked.connect(self.copyClipboard)
        
        self.consoleVars = QTableWidget()
        self.consoleVars.setColumnCount(3)
        self.consoleVars.setHorizontalHeaderLabels(["Name", "Type", "Value"])
        
        # Console Properties
        self.consoleLog.document().setMaximumBlockCount(500)
        self.consoleLog.setWordWrapMode(QTextOption.WrapAnywhere)

        self.ps1 = settings.db['CONSOLE_PS1']
        self.ps2 = settings.db['CONSOLE_PS2']
        self.consolePrompt.setText(self.ps1)

        # Controls
        self.cursor = self.consoleLog.textCursor()
        self.scrollbar = self.consoleLog.verticalScrollBar()

        # Spawn Interpreter
        self.thread = QThread()
        self.thread.start()

        self.buffer = ConsoleBuffer()

        self.interpreter = PythonInterpreter()
        self.interpreter.moveToThread(self.thread)

        # Interpreter Signals
        # self.consoleInput.returnPressed.connect(self.send_console_input)
        self.interpreter.stream.written.connect(self.buffer.consume)
        self.buffer.excrete.connect(self.send_console_log)
        self.interpreter.error.connect(self.send_console_log)
        self.interpreter.multi_line.connect(self.prompt)
        
        # Layout the console objects
        vLayout = QVBoxLayout(self)
        splitter1 = QSplitter(Qt.Horizontal)
        splitter1.addWidget(self.consoleLog)
        splitter1.addWidget(self.consoleVars)
        vLayout.addWidget(splitter1)
        hLayout = QHBoxLayout(self)
        hLayout.addWidget(self.consolePrompt)
        hLayout.addWidget(self.consoleInput)
        hLayout.addWidget(self.consoleCopy)
        vLayout.addLayout(hLayout)
        
        # Print the banner
        self.interpreter.push_command.emit('import sys')
        self.interpreter.push_command.emit('print("Python " + sys.version)')
        self.interpreter.push_command.emit('print("' + settings.db['CONSOLE_BANNER'] + '")')
        self.interpreter.push_command.emit('print()')
        self.interpreter.push_command.emit('print()')       
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.displayVars)
        self.timer.start(500)
        
#-------------------------------------------------------------------------------
# copyClipboard()
#-------------------------------------------------------------------------------
    def copyClipboard(self):
        clipboard = QApplication.clipboard().text()
        for line in clipboard.splitlines():
            self.consoleInput.setText(line)
            self.send_console_input()
            # self.interpreter.push_command.emit(line)
        self.send_console_input()
    
#-------------------------------------------------------------------------------
# eventFilter()
#-------------------------------------------------------------------------------
    def eventFilter(self, object, event):
        if object is self.consoleInput and event.type() == event.KeyPress:
            key = event.key()
            if key == Qt.Key_Up:
                if self.window.aCommands:
                    if self.window.iCommands > 0:
                        self.window.iCommands = self.window.iCommands - 1
                    else:
                        self.window.iCommands = len(self.window.aCommands) - 1
                    self.consoleInput.setText(self.window.aCommands[self.window.iCommands])
            elif key == Qt.Key_Down:
                if self.window.aCommands:
                    if self.window.iCommands < (len(self.window.aCommands) - 1):
                        self.window.iCommands = self.window.iCommands + 1
                    else:
                        self.window.iCommands = 0
                    self.consoleInput.setText(self.window.aCommands[self.window.iCommands])
            elif key in (Qt.Key_Enter, Qt.Key_Return):
                self.send_console_input()
            elif key == Qt.Key_Tab:
                pos = self.consoleInput.cursorPosition()
                out = self.consoleInput.text()
                out = out[:pos] + settings.db['BSIDE_TAB_SPACES'] * " " + out[pos:]
                self.consoleInput.setText(out)
                # self.consoleInput.setFocusPolicy(Qt.StrongFocus)
                # self.consoleInput.setFocus()
                return True
        return False       

#-------------------------------------------------------------------------------
# prompt()
#-------------------------------------------------------------------------------
    def prompt(self, multi_line):
        """
        Sets what prompt to use.
        """
        if multi_line:
            self.consolePrompt.setText(self.ps2)
        else:
            self.consolePrompt.setText(self.ps1)

#-------------------------------------------------------------------------------
# displayVars()
#-------------------------------------------------------------------------------
    def displayVars(self):
        vars = self.interpreter.locals
        self.consoleVars.setRowCount(0)
        for key, value in vars.items():
            rowPosition = self.consoleVars.rowCount()
            self.consoleVars.insertRow(rowPosition)
            s = str(type(value))                    
            self.consoleVars.setItem(rowPosition , 0, QTableWidgetItem(key))
            self.consoleVars.setItem(rowPosition , 1, QTableWidgetItem(re.findall(r"'([^']*)'", s)[0]))
            self.consoleVars.setItem(rowPosition , 2, QTableWidgetItem(str(value)))
        self.consoleVars.horizontalHeader().setStretchLastSection(True)
        
#-------------------------------------------------------------------------------
# send_console_input()
#-------------------------------------------------------------------------------
    def send_console_input(self):
        """
        Send input grabbed from the QLineEdit prompt to the console.
        """
        command = self.consoleInput.text()
        self.window.aCommands.append(command)
        self.window.iCommands = self.window.iCommands + 1        
        self.consoleInput.clear()
        self.interpreter.push_command.emit(str(command))
        self.consoleLog.insertPlainText("> " + str(command) + "\n")
        # self.displayVars()

#-------------------------------------------------------------------------------
# send_console_log()
#-------------------------------------------------------------------------------
    def send_console_log(self, output):
        """
        Set the output from InteractiveConsole in the QTextEdit.
        Auto scroll scrollbar.
        """
        # Move cursor
        self.cursor.movePosition(QTextCursor.End)
        self.consoleLog.setTextCursor(self.cursor)

        # Insert text
        self.consoleLog.insertPlainText(output)
        
        if output.isprintable() == True:
            self.window.lblBigDisplay.setText(str(output))
        
        # Move scrollbar
        self.scrollbar.setValue(self.scrollbar.maximum())

#-------------------------------------------------------------------------------
# Class TabPIP
#-------------------------------------------------------------------------------
class TabPIP(QWidget):      
#-------------------------------------------------------------------------------
# __init__()
#-------------------------------------------------------------------------------
    def __init__(self, parent = None, window = None):
            QWidget.__init__(self, parent)
            self.parent = parent
            self.window = window
            
            vLayout = QVBoxLayout(self)
            
            self.tblPackages = QTableWidget()
            self.tblPackages.itemClicked.connect(self.pckClicked)
            self.tblPackages.setAlternatingRowColors(True)
            self.txtInfoPackage = QTextEdit()
            self.txtInfoPackage.setReadOnly(True)
            self.txtInfoPackage.setAcceptRichText(True)
            
            hLayout1 = QHBoxLayout(self)
            hLayout1.addWidget(self.tblPackages)
            hLayout1.addWidget(self.txtInfoPackage)
            hLayout1.setStretch(1,1)
            
            self.lblPackages = QLabel("0")
            self.txtPackage = QLineEdit()
            self.btnRefresh = QPushButton("Refresh")
            self.btnRefresh.clicked.connect(self.displayPackagesList)
            self.chkUser = QCheckBox("user")
            self.chkUpgrade = QCheckBox("upgrade")
            self.btnInstall = QPushButton("Install")
            self.btnInstall.clicked.connect(self.installClicked)
            self.btnRemove = QPushButton("Remove")
            self.btnRemove.clicked.connect(self.removeClicked)
            hLayout2 = QHBoxLayout(self)
            hLayout2.addWidget(self.btnRefresh)
            hLayout2.addWidget(self.lblPackages)
            hLayout2.addWidget(self.txtPackage)            
            hLayout2.addWidget(self.chkUser)
            hLayout2.addWidget(self.chkUpgrade)
            hLayout2.addWidget(self.btnInstall)
            hLayout2.addWidget(self.btnRemove)
            h2Spacer = QSpacerItem(20, 40, QSizePolicy.Expanding, QSizePolicy.Minimum)
            hLayout2.addItem(h2Spacer)
            
            vLayout.addLayout(hLayout1)            
            vLayout.addLayout(hLayout2)            
                        
            self.displayPackagesList()          
            
#-------------------------------------------------------------------------------
# initPackagesList()
#-------------------------------------------------------------------------------
    def initPackagesList(self):
        while (self.tblPackages.rowCount() > 0):
            self.tblPackages.removeRow(0)
        self.tblPackages.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
        self.tblPackages.setColumnCount(2)
        self.tblPackages.setHorizontalHeaderLabels(["Package", "Version"])
        self.tblPackages.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tblPackages.verticalHeader().setVisible(True)
        self.lblPackages.setText("0")
            
#-------------------------------------------------------------------------------
# displayPackagesList()
#-------------------------------------------------------------------------------
    def displayPackagesList(self):
        self.initPackagesList()
        # packs = utils.getPackagesList()
        packs = reqs = subprocess.check_output([sys.executable, '-m', 'pip', 'freeze', '--all']).decode('utf-8')
        packs = packs.split('\n')
        packs = [pkg for pkg in packs if pkg != '']

        for i in range(len(packs)):
            rowPosition = self.tblPackages.rowCount()
            self.tblPackages.insertRow(rowPosition)
            itmPack = packs[i].split("==")

            item = QTableWidgetItem(itmPack[0])
            item.setTextAlignment(Qt.AlignVCenter)
            self.tblPackages.setItem(rowPosition, 0, item)

            item = QTableWidgetItem(itmPack[1])
            item.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
            self.tblPackages.setItem(rowPosition, 1, item)
            self.parent.showDebug(packs[i])
        self.lblPackages.setText(str(len(packs)))
        self.tblPackages.resizeColumnsToContents()
        self.tblPackages.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
        
#-------------------------------------------------------------------------------
# displayPackageInfo()
#-------------------------------------------------------------------------------
    def displayPackageInfo(self, pkg):
        info = utils.getPackageInfo(pkg)
        html = ("<h1>%s</h1>" % info.project_name)
        html = html + ("<style>")
        html = html + ("table {")
        html = html + ("border-collapse: separate;")
        html = html + ("border-spacing: 0 15px;")        
        html = html + ("}")
        html = html + ("td {")
        html = html + ("width: 150px;")
        html = html + ("text-align: center;")
        html = html + ("border: 1px solid black;")
        html = html + ("padding: 5px;")
        html = html + ("}")
        html = html + ("</style>")
        html = html + ("<p>")
        html = html + ("<table>")
        html = html + ("<tr><td>Package</td><td>%s</td></tr>" % info.key)
        html = html + ("<tr><td>Version</td><td>%s</td></tr>" % info.version)
        html = html + ("<tr><td>Location</td><td>%s</td></tr>" % info.location)
        html = html + ("<tr><td>Egg</td><td>%s</td></tr>" % info.egg_name())
        
        if info.platform is not None:
            html = html + ("<tr><td>Location</td><td>%s</td></tr>" % info.platform)
            
        html = html + ("</table>")
        html = html + ("</p>")
        
        html = html + ("<p>")
        html = html + ("<table>")
        extras = info.extras
        for x in extras:
            html = html + ("<tr><td>Extras require</td><td>%s</td></tr>" % x)
            
        require = info.requires(extras=extras)
        for r in require:
            html = html + ("<tr><td>Requirement</td><td>%s</td></tr>" % r)
        
        html = html + ("</table>")
        html = html + ("</p>")
        
        self.txtInfoPackage.setText(html)        

#-------------------------------------------------------------------------------
# pckClicked()
#-------------------------------------------------------------------------------
    def pckClicked(self, item):
        pkg = self.tblPackages.item(item.row(), 0).text()
        self.txtPackage.setText(pkg)
        self.displayPackageInfo(pkg)

#-------------------------------------------------------------------------------
# installClicked()
#-------------------------------------------------------------------------------
    def installClicked(self):
        if self.txtPackage.text() != "":
            self.installPackage(self.txtPackage.text())

#-------------------------------------------------------------------------------
# removeClicked()
#-------------------------------------------------------------------------------
    def removeClicked(self):
        if self.txtPackage.text() != "":
            self.uninstallPackage(self.txtPackage.text())

#-------------------------------------------------------------------------------
# installPackage()
#-------------------------------------------------------------------------------
    def installPackage(self, pkg):
        cmd = "%s install %s %s %s" % (\
        settings.db['CONSOLE_PACKAGE_INSTALLER'],\
        "--upgrade" if self.chkUpgrade.isChecked() else "",\
        pkg,\
        "--user" if self.chkUser.isChecked() else ""\
        )
        self.parent.tbwLowRight.setCurrentIndex(0)
        self.parent.showMessage("%s" % cmd)
        self.tCmd = shrealding.Shreald(self.parent, cmd, "./", shell=True)
        self.tCmd.linePrinted.connect(self.handleLine)                    

#-------------------------------------------------------------------------------
# uninstallPackage()
#-------------------------------------------------------------------------------
    def uninstallPackage(self, pkg):
        cmd = "%s uninstall %s -y" % (settings.db['CONSOLE_PACKAGE_INSTALLER'], pkg)
        self.parent.tbwLowRight.setCurrentIndex(0)
        self.parent.showMessage("%s" % cmd)
        self.tCmd = shrealding.Shreald(self.parent, cmd, "./", shell=True)
        self.tCmd.linePrinted.connect(self.handleLine)                    

#-------------------------------------------------------------------------------
# handleLine()
#-------------------------------------------------------------------------------
    def handleLine(self, line):
        if line !=  "":
            if line[0] == '1':
                self.parent.showMessage("[OUT] %s " % line[1:].rstrip())
            elif line[0] == '2':
                self.parent.showMessage("[ERR] %s " % line[1:].rstrip())
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
        if self.tCmd.returncode is not None:
            self.parent.showMessage("Return Code : %d" % self.tCmd.returncode)
        self.displayPackagesList()
        