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

from PyQt5.QtCore import Qt, QRect, QSize
from PyQt5.QtWidgets import QWidget, QPlainTextEdit, QTextEdit
from PyQt5.QtGui import QColor, QPainter, QTextFormat, QPen, QFontMetricsF, QTextCursor

import settings

#-------------------------------------------------------------------------------
# class QLineNumberArea
#-------------------------------------------------------------------------------
class QLineNumberArea(QWidget):
    def __init__(self, editor):
        super().__init__(editor)
        self.codeEditor = editor

#-------------------------------------------------------------------------------
# sizeHint()
#-------------------------------------------------------------------------------
    def sizeHint(self):
        return QSize(self.editor.lineNumberAreaWidth(), 0)

#-------------------------------------------------------------------------------
# paintEvent()
#-------------------------------------------------------------------------------
    def paintEvent(self, event):
        self.codeEditor.lineNumberAreaPaintEvent(event)

#-------------------------------------------------------------------------------
# class QCodeEditor
#-------------------------------------------------------------------------------
class QCodeEditor(QPlainTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.lineNumberArea = QLineNumberArea(self)
        self.blockCountChanged.connect(self.updateLineNumberAreaWidth)
        self.updateRequest.connect(self.updateLineNumberArea)
        self.cursorPositionChanged.connect(self.highlightCurrentLine)
        self.updateLineNumberAreaWidth(0)
        self.tabPos = 0

#-------------------------------------------------------------------------------
# keyPressEvent()
# TODO : To be continued asap !!!
# https://gist.github.com/LegoStormtroopr/6146161
#-------------------------------------------------------------------------------
    def keyPressEvent(self, event):
        KTAB = settings.db['BSIDE_TAB_SPACES']
        cursor = self.textCursor()
        if event.key() == Qt.Key_Backtab:
            self.tabPos = self.tabPos - 1
            if self.tabPos < 0:
                self.tabPos = 0
        elif event.key() == Qt.Key_Tab:
            self.tabPos = self.tabPos + 1
            cursor.insertText(KTAB * " ")
        elif event.key() == Qt.Key_Enter or event.key() == Qt.Key_Return:
            # TODO : Fix this !
            here = self.textCursor().position()
            cursor = self.textCursor()
            cursor.movePosition(QTextCursor.StartOfLine)
            print(self.tabsAtBeginningOfLine(self.toPlainText()[cursor.position():here], KTAB))
            cursor.movePosition(QTextCursor.EndOfLine)
            self.setTextCursor(cursor)
            if self.toPlainText()[here-1:here] == ":":
                print("MORE TAB")
                self.tabPos = self.tabPos + 1
            cursor.insertText("\n")
            cursor.insertText(KTAB * " " * self.tabPos)
        elif event.key() == Qt.Key_ParenLeft:
            cursor.insertText("()")
            cursor = self.textCursor()
            rc = cursor.movePosition(QTextCursor.Left, QTextCursor.MoveAnchor, 1)
            self.setTextCursor(cursor)
            print(rc)
        elif event.key() == Qt.Key_BracketLeft:
            cursor.insertText("[]")
            cursor = self.textCursor()
            rc = cursor.movePosition(QTextCursor.Left, QTextCursor.MoveAnchor, 1)
            self.setTextCursor(cursor)
        elif event.key() == Qt.Key_BraceLeft:
            cursor.insertText("{}")
            cursor = self.textCursor()
            rc = cursor.movePosition(QTextCursor.Left, QTextCursor.MoveAnchor, 1)
            self.setTextCursor(cursor)
        elif event.key() == Qt.Key_Apostrophe:
            cursor.insertText("''")
            cursor = self.textCursor()
            rc = cursor.movePosition(QTextCursor.Left, QTextCursor.MoveAnchor, 1)
            self.setTextCursor(cursor)
        elif event.key() == Qt.Key_QuoteDbl:
            cursor.insertText("\"\"")
            cursor = self.textCursor()
            rc = cursor.movePosition(QTextCursor.Left, QTextCursor.MoveAnchor, 1)
            self.setTextCursor(cursor)
        elif event.key() == Qt.Key_Backspace:
            here = self.textCursor().position()
            # Treat a tab made out of several spaces as a single TAB char
            if here > KTAB:
                if self.toPlainText()[here - KTAB:here] == (KTAB * " "):
                    for i in range(KTAB):
                        self.textCursor().deletePreviousChar()
                    self.tabPos = self.tabPos - 1
                else:
                    return QPlainTextEdit.keyPressEvent(self, event)
            else:
                return QPlainTextEdit.keyPressEvent(self, event)
        else:
            return QPlainTextEdit.keyPressEvent(self, event)
        print("TABS=%d" % self.tabPos)
            
    def tabsAtBeginningOfLine(self, line, KTAB):
        return((len(line) - len(line.lstrip())) % KTAB)

#-------------------------------------------------------------------------------
# paintEvent()
#-------------------------------------------------------------------------------
    def paintEvent(self, event):
        rect = event.rect()
        painter = QPainter(self.viewport())

        x00 = self.contentOffset().x() + self.document().documentMargin() - 3
        pen = QPen(Qt.SolidLine)
        pen.setColor(QColor("#C2C2C2"))
        pen.setWidth(1)
        painter.setPen(pen)
        painter.drawLine(x00, rect.top(), x00, rect.bottom())
                      
        if settings.db['EDITOR_RIGHT_MARGIN'] !=0:
            font = self.currentCharFormat().font()
            x80 = int(QFontMetricsF(font).averageCharWidth() * settings.db['EDITOR_RIGHT_MARGIN_COLUMN']) + self.contentOffset().x() + self.document().documentMargin()
            pen = QPen(Qt.SolidLine)
            pen.setColor(QColor(settings.db['EDITOR_RIGHT_MARGIN_COLOR']))
            pen.setWidth(1)
            painter.setPen(pen)
            painter.drawLine(x80, rect.top(), x80, rect.bottom())
            
        super(QCodeEditor, self).paintEvent(event)
    
#-------------------------------------------------------------------------------
# lineNumberAreaWidth()
#-------------------------------------------------------------------------------
    def lineNumberAreaWidth(self):
        digits = 1
        max_value = max(1, self.blockCount())
        while max_value >= 10:
            max_value /= 10
            digits += 1
        space = 3 + self.fontMetrics().width('9') * digits
        return space

#-------------------------------------------------------------------------------
# updateLineNumberAreaWidth()
#-------------------------------------------------------------------------------
    def updateLineNumberAreaWidth(self, _):
        self.setViewportMargins(self.lineNumberAreaWidth(), 0, 0, 0)

#-------------------------------------------------------------------------------
# updateLineNumberArea()
#-------------------------------------------------------------------------------
    def updateLineNumberArea(self, rect, dy):
        if dy:
            self.lineNumberArea.scroll(0, dy)
        else:
            self.lineNumberArea.update(0, rect.y(), self.lineNumberArea.width(), rect.height())
        if rect.contains(self.viewport().rect()):
            self.updateLineNumberAreaWidth(0)

#-------------------------------------------------------------------------------
# resizeEvent()
#-------------------------------------------------------------------------------
    def resizeEvent(self, event):
        super().resizeEvent(event)
        cr = self.contentsRect()
        self.lineNumberArea.setGeometry(QRect(cr.left(), cr.top(), self.lineNumberAreaWidth(), cr.height()))

#-------------------------------------------------------------------------------
# highlightCurrentLine()
#-------------------------------------------------------------------------------
    def highlightCurrentLine(self):
        extraSelections = []
        if not self.isReadOnly():
            selection = QTextEdit.ExtraSelection()
            # lineColor = QColor(Qt.yellow).lighter(160)
            lineColor = QColor(settings.db['EDITOR_COLOR_CURRENT_LINE'])
            selection.format.setBackground(lineColor)
            selection.format.setProperty(QTextFormat.FullWidthSelection, True)
            selection.cursor = self.textCursor()
            selection.cursor.clearSelection()
            extraSelections.append(selection)
        self.setExtraSelections(extraSelections)

#-------------------------------------------------------------------------------
# lineNumberAreaPaintEvent()
#-------------------------------------------------------------------------------
    def lineNumberAreaPaintEvent(self, event):
        painter = QPainter(self.lineNumberArea)

        painter.fillRect(event.rect(), QColor(settings.db['EDITOR_LINES_AREA_COLOR']))

        block = self.firstVisibleBlock()
        blockNumber = block.blockNumber()
        top = self.blockBoundingGeometry(block).translated(self.contentOffset()).top()
        bottom = top + self.blockBoundingRect(block).height()

        # Just to make sure I use the right font
        height = self.fontMetrics().height()
        while block.isValid() and (top <= event.rect().bottom()):
            if block.isVisible() and (bottom >= event.rect().top()):
                number = str(blockNumber + 1)
                painter.setPen(QColor(settings.db['EDITOR_LINES_NUMBER_COLOR']))                
                painter.drawText(0, top, self.lineNumberArea.width(), height, Qt.AlignRight, number)

            block = block.next()
            top = bottom
            bottom = top + self.blockBoundingRect(block).height()
            blockNumber += 1
