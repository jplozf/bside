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

import os
import re
import markdown
import webbrowser
import subprocess

import QCodeEditor
import QHexEditor
import settings
import syntax
import utils

#-------------------------------------------------------------------------------
# Class WEditor
#-------------------------------------------------------------------------------
class WEditor(QWidget):    
    SYNTAX_TEXT = 0
    SYNTAX_PYTHON = 1
    SYNTAX_XML = 2
    SYNTAX_SQL = 3
    
    OPEN_WITH_LOCAL = 0
    OPEN_WITH_BROWSER = 1
    OPEN_WITH_QTDESIGNER = 2
#-------------------------------------------------------------------------------
# __init__()
#-------------------------------------------------------------------------------
    def __init__(self, filename = None, parent = None, window = None, filetype = None, encoding = None):
        QWidget.__init__(self, parent)
        self.parent = parent
        self.window = window
        self.filetype = filetype
        if encoding == None:
            encoding = settings.db['EDITOR_CODEPAGE']
        self.txtEditor = QCodeEditor.QCodeEditor()     
        
        css = 'font: %dpt "%s"; background-color: %s;' % (settings.db['EDITOR_FONT_SIZE'],settings.db['EDITOR_FONT'],settings.db['EDITOR_COLOR_BACKGROUND'])
        self.txtEditor.setStyleSheet(css)
        # self.txtEditor.keyPressEvent = self.editorKeyPressEvent

        self.lblRowCol = QLabel("00000 : 00000")
        self.lblFileName = QLabel("*NONE")
        self.lblFileName.setTextFormat(Qt.RichText)
        
        self.btnCopyName = QPushButton()
        self.btnCopyName.setIcon(QIcon(QPixmap("pix/16x16/Clipboard Paste.png")))
        self.btnCopyName.clicked.connect(self.copyNameToClipboard)        
        
        self.lblSyntax = QLabel("Syntax")
        self.cbxSyntax = QComboBox()
        self.cbxSyntax.addItem("Text")
        self.cbxSyntax.addItem("Python")
        self.cbxSyntax.addItem("XML")    
        self.cbxSyntax.addItem("SQL")    
        self.cbxSyntax.setCurrentIndex(self.SYNTAX_TEXT)
        self.cbxSyntax.currentIndexChanged.connect(self.doSyntaxChanged)
        
        self.lblOpenWith = QLabel("Open with")
        self.cbxOpenWith = QComboBox()
        self.cbxOpenWith.addItem("Local")
        self.cbxOpenWith.addItem("Browser")
        self.cbxOpenWith.addItem("Qt Designer")
        self.cbxOpenWith.currentIndexChanged.connect(self.doOpenWith)
        
        self.lblModified = QLabel("")
        self.lblCodePage= QLabel("Encoding : %s" % encoding)
        self.lblSize = QLabel("0")
        self.txtGotoSearch = QLineEdit()
        self.lblGotoSearch = QLabel("")
        h1Spacer = QSpacerItem(20, 40, QSizePolicy.Expanding, QSizePolicy.Minimum)
        h2Spacer = QSpacerItem(20, 40, QSizePolicy.Expanding, QSizePolicy.Minimum)
        iSearch = QLabel()
        iSearch.setPixmap(QPixmap("pix/16x16/Search.png"))
        self.filename = filename
        if filename is not None:
            self.lblFileName.setText("&#8227;&nbsp;" + os.path.normpath(filename))
        self.textColor = self.parent.tabBar().tabTextColor(0)
                
        vLayout = QVBoxLayout(self)

        h1Layout = QHBoxLayout(self)
        h1Layout.addWidget(self.btnCopyName)       
        h1Layout.addWidget(self.lblFileName)        
        h1Layout.addItem(h1Spacer)
        h1Layout.addWidget(self.lblSyntax)        
        h1Layout.addWidget(self.cbxSyntax)        
        h1Layout.addWidget(self.lblOpenWith)        
        h1Layout.addWidget(self.cbxOpenWith)        
        
        vLayout.addLayout(h1Layout)        
        vLayout.addWidget(self.txtEditor)
        
        h2Layout = QHBoxLayout(self)
        h2Layout.addWidget(self.lblRowCol)
        # h2Layout.addItem(hSpacer)
        h2Layout.addWidget(iSearch)
        h2Layout.addWidget(self.txtGotoSearch)
        h2Layout.addWidget(self.lblGotoSearch)        
        # h2Layout.addWidget(self.lblFileName)        
        h2Layout.addItem(h2Spacer)
        h2Layout.addWidget(self.lblCodePage)
        h2Layout.addWidget(self.lblModified)
        h2Layout.addWidget(self.lblSize)        
        vLayout.addLayout(h2Layout)
        
        self.dirtyFlag = False
        if filename is not None:
            if self.filetype == "python":
                self.highlight = syntax.PythonHighlighter(self.txtEditor.document())
                self.cbxSyntax.setCurrentIndex(self.SYNTAX_PYTHON)
            elif self.filetype == "xml" or self.filetype == "html":
                self.highlight = syntax.XMLHighlighter(self.txtEditor.document())
                self.cbxSyntax.setCurrentIndex(self.SYNTAX_XML)
            elif self.filetype == "sql":
                self.highlight = syntax.SQLHighlighter(self.txtEditor.document())
                self.cbxSyntax.setCurrentIndex(self.SYNTAX_SQL)
            with open(filename, encoding=encoding) as pyFile:
                self.txtEditor.setPlainText(str(pyFile.read()))
                self.extractFuncs()
                self.displaySize()
        
        self.txtGotoSearch.returnPressed.connect(self.gotoSearch)
        self.txtEditor.textChanged.connect(self.changedText)
        self.txtEditor.selectionChanged.connect(self.handleSelectionChanged)
        self.txtEditor.cursorPositionChanged.connect(self.cursorPosition)
        self.txtEditor.setTabStopDistance(self.txtEditor.fontMetrics().width(' ') * 4)
        self.cursorPosition()                
        
#-------------------------------------------------------------------------------
# doSyntaxChanged()
#-------------------------------------------------------------------------------
    def doSyntaxChanged(self, i):
        if self.cbxSyntax.currentIndex() == self.SYNTAX_PYTHON:
            self.highlight = syntax.PythonHighlighter(self.txtEditor.document())
        elif self.cbxSyntax.currentIndex() == self.SYNTAX_XML:
            self.highlight = syntax.XMLHighlighter(self.txtEditor.document())
        elif self.cbxSyntax.currentIndex() == self.SYNTAX_SQL:
            self.highlight = syntax.SQLHighlighter(self.txtEditor.document())
        else:
            self.highlight = syntax.TextHighlighter(self.txtEditor.document())
            
#-------------------------------------------------------------------------------
# copyNameToClipboard()
#-------------------------------------------------------------------------------
    def copyNameToClipboard(self):
        QApplication.clipboard().setText(self.filename)
        self.window.showMessage("Copy file name to clipboard")
        
#-------------------------------------------------------------------------------
# doOpenWith()
#-------------------------------------------------------------------------------
    def doOpenWith(self, i):
        if self.cbxOpenWith.currentIndex() == self.OPEN_WITH_BROWSER:
            webbrowser.open(self.filename) 
            self.cbxOpenWith.setCurrentIndex(self.OPEN_WITH_LOCAL)
        elif self.cbxOpenWith.currentIndex() == self.OPEN_WITH_QTDESIGNER:
            subprocess.call([settings.db['BSIDE_QTDESIGNER_PATH'], self.filename])
            self.cbxOpenWith.setCurrentIndex(self.OPEN_WITH_LOCAL)
        
#-------------------------------------------------------------------------------
# cursorPosition()
#-------------------------------------------------------------------------------
    def cursorPosition(self):
        line = self.txtEditor.textCursor().blockNumber() + 1
        col = self.txtEditor.textCursor().columnNumber() + 1
        self.lblRowCol.setText("%05d : %05d" % (line, col))
        
#-------------------------------------------------------------------------------
# saveFile()
#-------------------------------------------------------------------------------
    def saveFile(self):
        # Convert tabs to spaces before saving file
        s = self.txtEditor.toPlainText()
        s = s.replace("\t", settings.db['BSIDE_TAB_SPACES'] * ' ')
        self.txtEditor.setPlainText(s)
        
        if self.filename is not None:
            with open(self.filename, "w") as pyFile:
                pyFile.write(self.txtEditor.toPlainText())
                self.dirtyFlag = False
                self.lblModified.setText("")
                self.parent.tabBar().setTabTextColor(self.parent.currentIndex(), self.textColor)
                # self.parent.tabBar().setTabIcon(self.parent.currentIndex(), QIcon())
        else:
            
            if self.filetype == "python":
                filters = "Python sources (*.py);;All files (*.*)"
            elif self.filetype == "xml":
                filters = "XML files (*.xml);;All files (*.*)"
            elif self.filetype == "html":
                filters = "HTML files (*.html);;All files (*.*)"
            elif self.filetype == "sql":
                filters = "SQL files (*.sql);;All files (*.*)"
            else:
                filters = "Text files (*.txt);;All files (*.*)"
            filename = QFileDialog.getSaveFileName(self, 'Save file', './', filters)[0]
            if filename != "":
                self.filename = filename
                shortname = os.path.basename(self.filename)
                self.parent.setTabText(self.parent.currentIndex(), shortname)
                with open(self.filename, "w") as pyFile:
                    pyFile.write(self.txtEditor.toPlainText())
                    self.dirtyFlag = False
                    self.lblModified.setText("")
                    self.parent.tabBar().setTabTextColor(self.parent.currentIndex(), self.textColor)
                    self.parent.tabBar().setTabIcon(self.parent.currentIndex(), QIcon())
                              
#-------------------------------------------------------------------------------
# changedText()
#-------------------------------------------------------------------------------
    def changedText(self):
        self.dirtyFlag = True
        self.lblModified.setText("*modified*")
        self.parent.tabBar().setTabTextColor(self.parent.currentIndex(), QColor(settings.db['EDITOR_COLOR_CHANGED_FILE']))
        if settings.db['EDITOR_BULLET_CHANGED_FILE']!=0:
            self.parent.tabBar().setTabIcon(self.parent.currentIndex(), QIcon("pix/silk/icons/bullet_red.png"))
        self.extractFuncs()
        self.displaySize()
                              
#-------------------------------------------------------------------------------
# editorKeyPressEvent()
#-------------------------------------------------------------------------------
    def editorKeyPressEvent(self, event):
        super(QCodeEditor.QCodeEditor, self.txtEditor).keyPressEvent(event)
        print("KEY EVENT")
        if event.key() == Qt.Key_Tab:
            print("TAB")
                
#-------------------------------------------------------------------------------
# displaySize()
#-------------------------------------------------------------------------------
    def displaySize(self):
        # self.lblSize.setText(str(sys.getsizeof(self.txtEditor.toPlainText())))
        self.lblSize.setText("%d (%s)" % (len(self.txtEditor.toPlainText()), utils.getHumanSize(len(self.txtEditor.toPlainText()))))

#-------------------------------------------------------------------------------
# extractFuncs()
#-------------------------------------------------------------------------------
    def extractFuncs(self):
        self.codeStructure = []
        self.todo = []
        # get the classes
        regexp = re.compile(r"(class)\s([a-zA-Z_]*)\s*\(.*\)")
        for m in regexp.finditer(self.txtEditor.toPlainText()):
            start = m.start()
            lineno = self.txtEditor.toPlainText().count("\n", 0, start) + 1
            line = self.txtEditor.toPlainText().splitlines()[lineno-1]
            indent = self.getIndent(line)
            # print(lineno, indent, line)
            self.codeStructure.append((lineno, indent, "class", m.group(2)))     

        # get the functions
        regexp = re.compile(r"(def)\s([a-zA-Z_]*)\s*\(.*\)")
        for m in regexp.finditer(self.txtEditor.toPlainText()):
            start = m.start()
            lineno = self.txtEditor.toPlainText().count("\n", 0, start) + 1
            line = self.txtEditor.toPlainText().splitlines()[lineno-1]
            indent = self.getIndent(line)
            # print(lineno, indent, line)
            self.codeStructure.append((lineno, indent, "function", m.group(2)))
                
        # get the vars
        """
        regexp = re.compile(r"(?<![\"'])(self.)?([a-zA-Z_]*)\s*(?<![=!])=(?!=)\s*.+(?![\"'])")
        for m in regexp.finditer(self.txtEditor.toPlainText()):
            start = m.start()
            lineno = self.txtEditor.toPlainText().count("\n", 0, start) + 1
            line = self.txtEditor.toPlainText().splitlines()[lineno-1]
            indent = self.getIndent(line)
            # print(lineno, indent, line)
            self.codeStructure.append((lineno, indent, "var", m.group(2)))     
        """

        # get the actions
        regexp = re.compile(r"\s*(#)\s*TODO\s*(.*)")
        for m in regexp.finditer(self.txtEditor.toPlainText()):
            start = m.start()
            lineno = self.txtEditor.toPlainText().count("\n", 0, start) + 1
            self.todo.append((lineno, m.group(2).strip()))     

        self.codeStructure.sort(key=lambda tup: tup[0])
        
        """
        TODO :
        * Sort by class name (none = <root>)
        * Inside class name, sort by function name
        * getClassOfFunction(fName, lineno)
        * get class name where 
        """
            
#-------------------------------------------------------------------------------
# getIndent()
#-------------------------------------------------------------------------------
    def getIndent(self, string):
        return sum(settings.db['BSIDE_TAB_SPACES'] if char is '\t' else 1 for char in string[:-len(string.lstrip())])

#-------------------------------------------------------------------------------
# gotoSearch()
#-------------------------------------------------------------------------------
    def gotoSearch(self):
        self.lblGotoSearch.setText("")
        if self.txtGotoSearch.text() != "":
            # Deselect all first
            myCursor = self.txtEditor.textCursor()
            myCursor.clearSelection()
            self.txtEditor.setTextCursor(myCursor)
            
            try:
                # Goto Line Number
                goto = int(self.txtGotoSearch.text())
                self.gotoLine(goto)
            except ValueError:
                # reset previous CharFormat (if any)
                cursor = self.txtEditor.textCursor()
                prevCursor = self.txtEditor.textCursor()
                cursor.select(QTextCursor.Document)
                cursor.setCharFormat(QTextCharFormat())
                cursor.clearSelection()
                self.txtEditor.setTextCursor(cursor)
                
                # Search for this string
                cursor = self.txtEditor.textCursor()
                
                # Setup the desired format for matches
                format = QTextCharFormat()
                format.setBackground(QBrush(QColor("yellow")))      
                pattern = self.txtGotoSearch.text()
                regex = QRegExp(pattern)
                
                # Process the displayed document
                pos = 0
                match = 0
                index = regex.indexIn(self.txtEditor.toPlainText(), pos)
                while (index != -1):
                    # Select the matched text and apply the desired format
                    cursor.setPosition(index)
                    cursor.movePosition(QTextCursor.EndOfWord, 1)
                    cursor.mergeCharFormat(format)
                    # Move to the next match
                    pos = index + regex.matchedLength()
                    index = regex.indexIn(self.txtEditor.toPlainText(), pos)
                    
                    lineno = self.txtEditor.toPlainText().count('\n', 0, pos) + 1                    
                    rowPosition = self.window.tblSearch.rowCount()                     
                    self.window.tblSearch.insertRow(rowPosition)

                    item = QTableWidgetItem("%d" % lineno)
                    item.setTextAlignment(Qt.AlignHCenter)
                    self.window.tblSearch.setItem(rowPosition, 0, item)
                    
                    self.window.tblSearch.setItem(rowPosition, 1, QTableWidgetItem("%s" % self.getNthLine(self.txtEditor.toPlainText(), lineno).strip()))
                    self.window.tblSearch.setRowHeight(rowPosition, 20)
                    self.window.tblSearch.resizeColumnsToContents()
                    
                    match = match + 1
                    
                self.window.lblSearch.setText("%d : %s" % (match, pattern))
                self.lblGotoSearch.setText("Match : %d" % match)
                self.txtEditor.setTextCursor(prevCursor)
                self.txtEditor.setFocus()
                self.window.tbwLowLeft.setCurrentIndex(1)

#-------------------------------------------------------------------------------
# handleSelectionChanged()
#-------------------------------------------------------------------------------
    def handleSelectionChanged(self):
        myCursor = self.txtEditor.textCursor()
        text = myCursor.selectedText()
        # myCursor.clearSelection()
        # self.txtEditor.setTextCursor(myCursor)
        # self.txtGotoSearch.setText(text)          
    
#-------------------------------------------------------------------------------
# gotoLine()
#-------------------------------------------------------------------------------
    def gotoLine(self, nline):
        self.txtEditor.moveCursor(QTextCursor.End)
        cursor = QTextCursor(self.txtEditor.document().findBlockByLineNumber(nline - 1))
        self.txtEditor.setTextCursor(cursor)   
        self.txtEditor.setFocus()
        
#-------------------------------------------------------------------------------
# getNthLine()
#-------------------------------------------------------------------------------
    def getNthLine(self, text, nline):
        return(text.split('\n')[nline - 1])
        
"""
for m in re.finditer(pattern, src):
	start = m.start()
	lineno = src.count('\n', 0, start) + 1
	offset = start - src.rfind('\n', 0, start)
	word = m.group(1)
	print "2.htm(%s,%s): %s" % (lineno, offset, word)

"""        

#-------------------------------------------------------------------------------
# Class WMarkdown
#-------------------------------------------------------------------------------
class WMarkdown(QWidget):
#-------------------------------------------------------------------------------
# __init__()
#-------------------------------------------------------------------------------
    def __init__(self, filename = None, parent = None, window = None, encoding = None):
        QWidget.__init__(self, parent)
        self.parent = parent
        self.window = window
        if encoding == None:
            encoding = settings.db['EDITOR_CODEPAGE']

        self.txtEditor = QCodeEditor.QCodeEditor()        
        self.txtMarkdown = QTextEdit()
        self.txtMarkdown.setReadOnly(True)
        
        self.btnResizeEditor = QPushButton("Editor")
        self.btnResizeMarkdown = QPushButton("Markdown")
        self.chkSynchroScroll = QCheckBox("Synchro Scrolling")
        
        css = 'font: %dpt "%s"; background-color: %s;' % (settings.db['EDITOR_FONT_SIZE'],settings.db['EDITOR_FONT'],settings.db['EDITOR_COLOR_BACKGROUND'])
        self.txtEditor.setStyleSheet(css)

        self.lblRowCol = QLabel("00000 : 00000")
        self.lblModified = QLabel("")
        self.txtGotoSearch = QLineEdit()
        self.lblGotoSearch = QLabel("")
        hSpacer = QSpacerItem(20, 40, QSizePolicy.Expanding, QSizePolicy.Minimum)
        iSearch = QLabel()
        iSearch.setPixmap(QPixmap("pix/16x16/Search.png"))
        self.filename = filename
        self.textColor = self.parent.tabBar().tabTextColor(0)
        
        vLayout = QVBoxLayout(self)

        hLayout0 = QHBoxLayout(self)
        hLayout0.addWidget(self.btnResizeEditor)
        # hLayout0.addWidget(self.chkSynchroScroll)
        hLayout0.addWidget(self.btnResizeMarkdown)
        vLayout.addLayout(hLayout0)
        
        hLayout1 = QHBoxLayout(self)
        hLayout1.addWidget(self.txtEditor)
        hLayout1.addWidget(self.txtMarkdown)
        vLayout.addLayout(hLayout1)
        hLayout = QHBoxLayout(self)
        hLayout.addWidget(self.lblRowCol)
        # hLayout.addItem(hSpacer)
        hLayout.addWidget(iSearch)
        hLayout.addWidget(self.txtGotoSearch)
        hLayout.addWidget(self.lblGotoSearch)        
        hLayout.addItem(hSpacer)
        hLayout.addWidget(self.lblModified)        
        vLayout.addLayout(hLayout)
        
        self.dirtyFlag = False
        if filename is not None:
            self.highlight = syntax.PythonHighlighter(self.txtEditor.document())
            with open(filename, encoding=encoding) as pyFile:
                self.txtEditor.setPlainText(str(pyFile.read()))
            self.txtMarkdown.setText(markdown.markdown(self.txtEditor.toPlainText(), extensions=settings.db['EDITOR_MD_EXTENSIONS']))
        
        self.txtGotoSearch.returnPressed.connect(self.gotoSearch)
        self.txtEditor.textChanged.connect(self.changedText)
        self.txtEditor.selectionChanged.connect(self.handleSelectionChanged)
        self.txtEditor.cursorPositionChanged.connect(self.cursorPosition)
        self.txtEditor.setTabStopWidth(self.txtEditor.fontMetrics().width(' ') * 4)
        
        self.btnResizeEditor.clicked.connect(self.resizeEditor)
        self.btnResizeMarkdown.clicked.connect(self.resizeMarkdown)
        self.cursorPosition()                
        
#-------------------------------------------------------------------------------
# cursorPosition()
#-------------------------------------------------------------------------------
    def cursorPosition(self):
        line = self.txtEditor.textCursor().blockNumber() + 1
        col = self.txtEditor.textCursor().columnNumber() + 1
        self.lblRowCol.setText("%05d : %05d" % (line, col))
        
#-------------------------------------------------------------------------------
# saveFile()
#-------------------------------------------------------------------------------
    def saveFile(self):
        if self.filename is not None:
            with open(self.filename, "w") as pyFile:
                pyFile.write(self.txtEditor.toPlainText())
                self.dirtyFlag = False
                self.lblModified.setText("")
                self.parent.tabBar().setTabTextColor(self.parent.currentIndex(), self.textColor)
                self.parent.tabBar().setTabIcon(self.parent.currentIndex(), QIcon())
        else:
            filename = QFileDialog.getSaveFileName(self, 'Save file', './', 'Python sources (*.py);;XML files (*.xml);;All files (*.*)')[0]
            if filename != "":
                self.filename = filename
                shortname = os.path.basename(self.filename)
                self.parent.setTabText(self.parent.currentIndex(), shortname)
                with open(self.filename, "w") as pyFile:
                    pyFile.write(self.txtEditor.toPlainText())
                    self.dirtyFlag = False
                    self.lblModified.setText("")
                    self.parent.tabBar().setTabTextColor(self.parent.currentIndex(), self.textColor)
                    self.parent.tabBar().setTabIcon(self.parent.currentIndex(), QIcon())
                              
#-------------------------------------------------------------------------------
# changedText()
#-------------------------------------------------------------------------------
    def changedText(self):
        self.dirtyFlag = True
        self.lblModified.setText("*modified*")
        self.parent.tabBar().setTabTextColor(self.parent.currentIndex(), QColor(settings.db['EDITOR_COLOR_CHANGED_FILE']))
        if settings.db['EDITOR_BULLET_CHANGED_FILE']!=0:
            self.parent.tabBar().setTabIcon(self.parent.currentIndex(), QIcon("pix/silk/icons/bullet_red.png"))
        self.txtMarkdown.setText(markdown.markdown(self.txtEditor.toPlainText(), extensions=settings.db['EDITOR_MD_EXTENSIONS']))
            
#-------------------------------------------------------------------------------
# gotoSearch()
#-------------------------------------------------------------------------------
    def gotoSearch(self):
        self.lblGotoSearch.setText("")
        if self.txtGotoSearch.text() != "":
            # Deselect all first
            myCursor = self.txtEditor.textCursor()
            myCursor.clearSelection()
            self.txtEditor.setTextCursor(myCursor)
            
            try:
                # Goto Line Number
                goto = int(self.txtGotoSearch.text())
                self.gotoLine(goto)
            except ValueError:
                # reset previous CharFormat (if any)
                cursor = self.txtEditor.textCursor()
                prevCursor = self.txtEditor.textCursor()
                cursor.select(QTextCursor.Document)
                cursor.setCharFormat(QTextCharFormat())
                cursor.clearSelection()
                self.txtEditor.setTextCursor(cursor)
                
                # Search for this string
                cursor = self.txtEditor.textCursor()
                
                # Setup the desired format for matches
                format = QTextCharFormat()
                format.setBackground(QBrush(QColor("yellow")))      
                pattern = self.txtGotoSearch.text()
                regex = QRegExp(pattern)
                
                # Process the displayed document
                pos = 0
                match = 0
                index = regex.indexIn(self.txtEditor.toPlainText(), pos)
                while (index != -1):
                    # Select the matched text and apply the desired format
                    cursor.setPosition(index)
                    cursor.movePosition(QTextCursor.EndOfWord, 1)
                    cursor.mergeCharFormat(format)
                    # Move to the next match
                    pos = index + regex.matchedLength()
                    index = regex.indexIn(self.txtEditor.toPlainText(), pos)
                    
                    lineno = self.txtEditor.toPlainText().count('\n', 0, pos) + 1                    
                    rowPosition = self.window.tblSearch.rowCount()                     
                    self.window.tblSearch.insertRow(rowPosition)

                    item = QTableWidgetItem("%d" % lineno)
                    item.setTextAlignment(Qt.AlignHCenter)
                    self.window.tblSearch.setItem(rowPosition, 0, item)
                    
                    self.window.tblSearch.setItem(rowPosition, 1, QTableWidgetItem("%s" % self.getNthLine(self.txtEditor.toPlainText(), lineno).strip()))
                    self.window.tblSearch.setRowHeight(rowPosition, 20)
                    self.window.tblSearch.resizeColumnsToContents()
                    
                    match = match + 1
                    
                self.window.lblSearch.setText("%d : %s" % (match, pattern))
                self.lblGotoSearch.setText("Match : %d" % match)
                self.txtEditor.setTextCursor(prevCursor)
                self.txtEditor.setFocus()
                self.window.tbwLowLeft.setCurrentIndex(1)

#-------------------------------------------------------------------------------
# handleSelectionChanged()
#-------------------------------------------------------------------------------
    def handleSelectionChanged(self):
        myCursor = self.txtEditor.textCursor()
        text = myCursor.selectedText()
        # myCursor.clearSelection()
        # self.txtEditor.setTextCursor(myCursor)
        # self.txtGotoSearch.setText(text)          
    
#-------------------------------------------------------------------------------
# gotoLine()
#-------------------------------------------------------------------------------
    def gotoLine(self, nline):
        self.txtEditor.moveCursor(QTextCursor.End)
        cursor = QTextCursor(self.txtEditor.document().findBlockByLineNumber(nline - 1))
        self.txtEditor.setTextCursor(cursor)   
        self.txtEditor.setFocus()
        
#-------------------------------------------------------------------------------
# getNthLine()
#-------------------------------------------------------------------------------
    def getNthLine(self, text, nline):
        return(text.split('\n')[nline - 1])
            
#-------------------------------------------------------------------------------
# resizeEditor()
#-------------------------------------------------------------------------------
    def resizeEditor(self):
        if self.txtEditor.isHidden():
            self.txtEditor.setVisible(True)
        else:
            if not self.txtMarkdown.isHidden() and not self.txtEditor.isHidden():
                self.txtMarkdown.hide()            
            
#-------------------------------------------------------------------------------
# resizeMarkdown()
#-------------------------------------------------------------------------------
    def resizeMarkdown(self):
        if self.txtMarkdown.isHidden():
            self.txtMarkdown.setVisible(True)
        else:
            if not self.txtMarkdown.isHidden() and not self.txtEditor.isHidden():
                self.txtEditor.hide()            


#-------------------------------------------------------------------------------
# Class WHexedit
#-------------------------------------------------------------------------------
class WHexedit(QWidget):
    """
+----------+--------------------------------------------------+------------------+
| 00000000 | 00 01 02 03 04 05 06 07  08 09 0A 0B 0C 0D 0E 0F | 0123456789abcdef |
| 00000010 | 00 01 02 03 04 05 06 07  08 09 0A 0B 0C 0D 0E 0F | 0123456789abcdef |
| 00000020 | 00 01 02 03 04 05 06 07  08 09 0A 0B 0C 0D 0E 0F | 0123456789abcdef |
| 00000030 | 00 01 02 03 04 05 06 07  08 09 0A 0B 0C 0D 0E 0F | 0123456789abcdef |
| 00000040 | 00 01 02 03 04 05 06 07  08 09 0A 0B 0C 0D 0E 0F | 0123456789abcdef |
+----------+--------------------------------------------------+------------------+
    """
#-------------------------------------------------------------------------------
# __init__()
#-------------------------------------------------------------------------------
    def __init__(self, filename = None, parent = None, window = None):
        QWidget.__init__(self, parent)
        self.parent = parent
        self.window = window
        self.hexEditor = QHexEditor.QHexEditor()             
        
        css = 'font: %dpt "%s"; background-color: %s;' % (settings.db['EDITOR_FONT_SIZE'],settings.db['EDITOR_FONT'],settings.db['EDITOR_COLOR_BACKGROUND'])
        self.hexEditor.setStyleSheet(css)

        self.lblRowCol = QLabel("00000 : 00000")
        self.lblModified = QLabel("")
        self.txtGotoSearch = QLineEdit()
        self.lblGotoSearch = QLabel("")
        hSpacer = QSpacerItem(20, 40, QSizePolicy.Expanding, QSizePolicy.Minimum)
        iSearch = QLabel()
        iSearch.setPixmap(QPixmap("pix/16x16/Search.png"))
        self.filename = filename
        self.textColor = self.parent.tabBar().tabTextColor(0)
        
        vLayout = QVBoxLayout(self)
        
        hLayout1 = QHBoxLayout(self)
        hLayout1.addWidget(self.hexEditor)
        vLayout.addLayout(hLayout1)
        hLayout = QHBoxLayout(self)
        hLayout.addWidget(self.lblRowCol)
        # hLayout.addItem(hSpacer)
        hLayout.addWidget(iSearch)
        hLayout.addWidget(self.txtGotoSearch)
        hLayout.addWidget(self.lblGotoSearch)        
        hLayout.addItem(hSpacer)
        hLayout.addWidget(self.lblModified)        
        vLayout.addLayout(hLayout)
        
        self.dirtyFlag = False
        if filename is not None:
            with open(filename, encoding=settings.db['EDITOR_CODEPAGE']) as hexFile:
                # TODO : Format datas
                self.hexEditor.setPlainText(str(hexFile.read()))
        
        # self.txtGotoSearch.returnPressed.connect(self.gotoSearch)
        # self.hexEditor.textChanged.connect(self.changedText)
        # self.hexEditor.selectionChanged.connect(self.handleSelectionChanged)
        self.hexEditor.cursorPositionChanged.connect(self.cursorPosition)
        self.hexEditor.setTabStopWidth(self.hexEditor.fontMetrics().width(' ') * 4)
        
        self.cursorPosition()                
        
#-------------------------------------------------------------------------------
# cursorPosition()
#-------------------------------------------------------------------------------
    def cursorPosition(self):
        line = self.hexEditor.textCursor().blockNumber() + 1
        col = self.hexEditor.textCursor().columnNumber() + 1
        self.lblRowCol.setText("%05d : %05d" % (line, col))
