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
import sys
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
        vLayout.addWidget(self.consoleLog)
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
            self.txtInfoPackage = QPlainTextEdit()
            hLayout1 = QHBoxLayout(self)
            hLayout1.addWidget(self.tblPackages)
            hLayout1.addWidget(self.txtInfoPackage)
            
            self.txtPackage = QLineEdit()
            self.btnRefresh = QPushButton("Refresh")
            self.btnInstall = QPushButton("Install")
            self.btnRemove = QPushButton("Remove")
            hLayout2 = QHBoxLayout(self)
            hLayout2.addWidget(self.btnRefresh)
            hLayout2.addWidget(self.txtPackage)            
            hLayout2.addWidget(self.btnInstall)
            hLayout2.addWidget(self.btnRemove)
            
            vLayout.addLayout(hLayout1)            
            vLayout.addLayout(hLayout2)            

            while (self.tblPackages.rowCount() > 0):
                self.tblPackages.removeRow(0)
            self.tblPackages.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
            self.tblPackages.setColumnCount(2)
            self.tblPackages.setHorizontalHeaderLabels(["Package", "Version"])
            self.tblPackages.setEditTriggers(QTableWidget.NoEditTriggers)
            self.tblPackages.verticalHeader().setVisible(True)

            packs = utils.getPackagesList()
            for i in range(len(packs)):
                rowPosition = self.tblPackages.rowCount()
                self.tblPackages.insertRow(rowPosition)
                itmPack = packs[i].split(",")
                
                item = QTableWidgetItem(itmPack[0])
                item.setTextAlignment(Qt.AlignVCenter)
                self.tblPackages.setItem(rowPosition, 0, item)
                
                item = QTableWidgetItem(itmPack[1])
                item.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                self.tblPackages.setItem(rowPosition, 1, item)
                parent.showDebug(packs[i])
            self.tblPackages.resizeColumnsToContents()