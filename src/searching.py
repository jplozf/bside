#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#===============================================================================
#                                                       ____      _     _      
#                                                      | __ ) ___(_) __| | ___ 
#                                                      |  _ \/ __| |/ _` |/ _ \
#                                                      | |_) \__ \ | (_| |  __/
#                                                      |____/|___/_|\__,_|\___|
#                         
#============================================================(C) JPL 2020=======

#-------------------------------------------------------------------------------
# Imports
#-------------------------------------------------------------------------------
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

import os
import re

import mainwindow
import editor

#-------------------------------------------------------------------------------
# Class Weasel
#-------------------------------------------------------------------------------
class Weasel():
    SCOPE_FILE = 0
    SCOPE_EDITOR = 1
    SCOPE_PROJECT = 2
    
    FIND_REGEX = 0
    FIND_FUNCTION_USAGE = 1
    FIND_TEXT_CASE_MATCH = 2
    FIND_TEXT_NO_CASE_MATCH = 3

#-------------------------------------------------------------------------------
# __init__()
#-------------------------------------------------------------------------------
    def __init__(self, source):
        # scope document or project
        # tablewiew output => return list
        # find text or regex
        # find or find/replace
        # function usage
        # case match or not
        # highlight matches or not
        # goto line
        # bookmark
        # previous / next edit
        # interactive
        # history
        self.source = source
        if type(source) is editor.WEditor:
            self.setEditor(source)
        elif type(source) is projects.Project:
            pass
        
#-------------------------------------------------------------------------------
# setScope()
#-------------------------------------------------------------------------------
    def setScope(self, scope):
        self.scope = scope
        
#-------------------------------------------------------------------------------
# setEditor()
#-------------------------------------------------------------------------------
    def setEditor(self, txtEditor):
        self.txtEditor = txtEditor

#-------------------------------------------------------------------------------
# setClue()
#-------------------------------------------------------------------------------
    def setClue(self, clue):
        self.clue = clue
        
#-------------------------------------------------------------------------------
# find()
#-------------------------------------------------------------------------------
    def find(self):
        if self.scope == SCOPE_EDITOR:
            self._findInEditor()
    
#-------------------------------------------------------------------------------
# _findInEditor()
#-------------------------------------------------------------------------------
    def _findInEditor(self):
        """
        The GotoSearch widget could be used with a line number or a pattern to search for.
        """
        self.txtEditor.blockSignals(True)
        if self.clue != "":
            # Deselect all first
            myCursor = self.txtEditor.textCursor()
            myCursor.clearSelection()
            self.txtEditor.setTextCursor(myCursor)

            # Is it a pattern to search for ?
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
            pattern = self.clue
            regex = QRegExp(pattern)

            # Process the displayed document
            pos = 0
            match = 0
            self.window.tblSearch.setRowCount(0)
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
            self.lblGotoSearch.setText("%d" % match)
            self.txtEditor.setTextCursor(prevCursor)
            self.txtEditor.setFocus()
            self.window.tbwLowLeft.setCurrentIndex(1)
        self.txtEditor.blockSignals(False)
        
