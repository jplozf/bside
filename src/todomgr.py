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
import sqlite3
from googlesearch import search 
import webbrowser
from pathlib import Path

import settings
import dialog
import utils

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
# Class TodoManager
#-------------------------------------------------------------------------------
class TodoManager():
#-------------------------------------------------------------------------------
# __init__()
#-------------------------------------------------------------------------------
    def __init__(self, parent = None):
        self.mw = parent
        
        self.mw.btnNowTODO.clicked.connect(self.nowTODO)
        self.mw.btnAddTODO.clicked.connect(self.addTODO)
        self.mw.btnDelTODO.clicked.connect(self.delTODO)
        self.mw.btnUpTODO.clicked.connect(self.upTODO)
        self.mw.btnDownTODO.clicked.connect(self.downTODO)        
        self.mw.txtNote.textChanged.connect(self.changeNote)
        
        selmodel = self.mw.tvwTODO.selectionModel()
        selmodel.selectionChanged.connect(self.handleTODOSelection)
        self.mw.tvwTODO.itemChanged.connect(self.handleTODOChecked)
        self.mw.tvwTODO.setHeaderHidden(True)
        
        self.db = sqlite3.connect(os.path.join(self.mw.appDir, "todo.db"))
        self.db.execute(
        """
        CREATE TABLE IF NOT EXISTS TODOs (
	idTODO INTEGER PRIMARY KEY,
	lblTODO TEXT,
	ordTODO INTEGER DEFAULT 10,
	txtTODO TEXT,
	txtNOTE TEXT,
	chkTODO INTEGER DEFAULT 0
        );
        """
        )
        self.db.commit()      
        self.displayTODOs()
            
#-------------------------------------------------------------------------------
# nowTODO()
#-------------------------------------------------------------------------------
    def nowTODO(self):
        self.mw.showMessage("Now")

#-------------------------------------------------------------------------------
# addTODO()
#-------------------------------------------------------------------------------
    def addTODO(self):
        dlg = dialog.DlgAddTODO(self.mw)
        result = dlg.exec()
        if result == QDialog.Accepted:
            sDate = str(dlg.tplTODO[0])
            sText = str(dlg.tplTODO[1])
            sNote = str(dlg.tplTODO[2])
            iTODO = self.getNextOrder(sDate)
            print("NEXT = %d" % iTODO)
            self.addDBTODO(sDate, sText, ordTODO=iTODO, txtNOTE=sNote)
            self.mw.showMessage("Add")
            
#-------------------------------------------------------------------------------
# addDBTODO()
#-------------------------------------------------------------------------------
    def addDBTODO(self, lblTODO, txtTODO, ordTODO=10, txtNOTE="", chkTODO=0):
        cur = self.db.cursor()
        data = (lblTODO, txtTODO, ordTODO, txtNOTE, chkTODO)
        print(data)
        cur.execute("insert into TODOs(lblTODO, txtTODO, ordTODO, txtNOTE, chkTODO) values (?, ?, ?, ?, ?)", data)
        cur.close      
        self.db.commit()
        self.displayTODOs()
        self.setTODOFocus(lblTODO, txtTODO)
        
#-------------------------------------------------------------------------------
# getNextOrder()
#-------------------------------------------------------------------------------
    def getNextOrder(self, lblTODO):
        cur = self.db.cursor()
        cur.execute("select max(ordTODO)+10 from TODOs where lblTODO = :label", {"label": lblTODO})
        nxt = cur.fetchone()[0]
        if nxt is None:
            nxt = 10
        cur.close()
        return(nxt)

#-------------------------------------------------------------------------------
# delTODO()
#-------------------------------------------------------------------------------
    def delTODO(self):
        self.mw.showMessage("Delete")
    
#-------------------------------------------------------------------------------
# upTODO()
#-------------------------------------------------------------------------------
    def upTODO(self):
        self.mw.showMessage("Go up")
    
#-------------------------------------------------------------------------------
# downTODO()
#-------------------------------------------------------------------------------
    def downTODO(self):
        self.mw.showMessage("Go down")
        
#-------------------------------------------------------------------------------
# changeNOTE()
#-------------------------------------------------------------------------------
    def changeNote(self):
        self.mw.showMessage("Edit Note")
        
#-------------------------------------------------------------------------------
# setTODOFocus()
#-------------------------------------------------------------------------------
    def setTODOFocus(self, lbl, txt):
        found = False
        root = self.mw.tvwTODO.invisibleRootItem()
        children = root.childCount()
        for i in range(children):
            itmLabel = root.child(i)
            if itmLabel.text(0) == lbl:
                jChildren = itmLabel.childCount()
                for j in range(jChildren):
                    itmTxt = itmLabel.child(j)
                    if itmTxt.text(0) == txt:
                        found = True
                        break
        if found == True:
            self.mw.tvwTODO.setCurrentItem(itmTxt)

#-------------------------------------------------------------------------------
# displayTODOs()
#-------------------------------------------------------------------------------
    def displayTODOs(self):
        cur = self.db.cursor()
        cur.execute("select idTODO, lblTODO, ordTODO, txtTODO, txtNOTE, chkTODO from TODOs order by lblTODO, ordTODO")
        rows = cur.fetchall() 
        self.clearQTreeWidget(self.mw.tvwTODO)
        self.mw.tvwTODO.blockSignals(True)
        for row in rows:
            idTODO = row[0]
            lblTODO = row[1]
            ordTODO = row[2]
            txtTODO = row[3]
            txtNOTE = row[4]
            chkTODO = row[5]
            # print(dteTODO)
            found = False
            root = self.mw.tvwTODO.invisibleRootItem()
            children = root.childCount()
            for i in range(children):
                itm = root.child(i)
                if itm.text(0) == lblTODO:
                    found = True
                    break
            if found == False:
                itmLabel = QTreeWidgetItem(self.mw.tvwTODO)
                font = QFont()
                font.setWeight(QFont.Bold)
                itmLabel.setFont(0, font)
                itmLabel.setText(0, lblTODO)

                itmText = QTreeWidgetItem(itmLabel)
                itmText.setText(0, txtTODO)
                itmText.setText(1, str(idTODO))
                itmText.setFlags(itmText.flags() | Qt.ItemIsUserCheckable)
                itmText.setCheckState(0, Qt.Unchecked if chkTODO == 0 else Qt.Checked)
            else:
                itmText = QTreeWidgetItem(itm)
                itmText.setText(0, txtTODO)
                itmText.setText(1, str(idTODO))
                itmText.setFlags(itmText.flags() | Qt.ItemIsUserCheckable)
                itmText.setCheckState(0, Qt.Unchecked if chkTODO == 0 else Qt.Checked)

        self.mw.tvwTODO.blockSignals(False)
        cur.close()

#-------------------------------------------------------------------------------
# clearQTreeWidget()
#-------------------------------------------------------------------------------
    def clearQTreeWidget(self, tree):
        iterator = QTreeWidgetItemIterator(tree, QTreeWidgetItemIterator.All)
        while iterator.value():
            iterator.value().takeChildren()
            iterator +=1
        i = tree.topLevelItemCount()
        while i > -1:
            tree.takeTopLevelItem(i)
            i -= 1
            
#-------------------------------------------------------------------------------
# handleTODOSelection()
#-------------------------------------------------------------------------------
    def handleTODOSelection(self, selected, deselected):
        for index in selected.indexes():
            item = self.mw.tvwTODO.itemFromIndex(index)
            try:
                self.mw.txtNote.setPlainText(self.getNote(int(item.text(1))))
                if settings.db["TODO_AUTORESIZE_NOTE"]:
                    if self.mw.txtNote.toPlainText() == "":
                        self.resizeSplitter(self.mw.splitter, 0, 90)
                    else:
                        self.resizeSplitter(self.mw.splitter, 0, 50)
            except:
                self.mw.txtNote.setPlainText("")
                if settings.db["TODO_AUTORESIZE_NOTE"]:
                    self.resizeSplitter(self.mw.splitter, 0, 90)
                
#-------------------------------------------------------------------------------
# handleTODOChecked()
#-------------------------------------------------------------------------------
    def handleTODOChecked(self, item, column):
        self.mw.tvwTODO.blockSignals(True)
        if item.checkState(column) == Qt.Checked:
            print("CHECKED")            
        elif item.checkState(column) == Qt.Unchecked:
            print("UNCHECKED")
        self.updateCheckedTODO(int(item.text(1)), item.checkState(column))
        self.mw.tvwTODO.blockSignals(False)
                
#-------------------------------------------------------------------------------
# resizeSplitter()
#-------------------------------------------------------------------------------
    def resizeSplitter(self, splitter, iWidget, percent):
        szSplitter = splitter.sizes()
        szTotal = szSplitter[0] + szSplitter[1]
        if iWidget == 0:
            sz0 = int(szTotal * percent / 100)
            sz1 = int(szTotal - sz0)
        else:
            sz1 = int(szTotal * percent / 100)
            sz0 = int(szTotal - sz1)
        szSplitter = [sz0, sz1]
        splitter.setSizes(szSplitter)
                
#-------------------------------------------------------------------------------
# getNote()
#-------------------------------------------------------------------------------
    def getNote(self, id):
        cur = self.db.cursor()
        cur.execute("select txtNOTE from TODOs where idTODO = :id", {"id": id})
        note = cur.fetchone()[0]
        cur.close()
        return note
    
#-------------------------------------------------------------------------------
# updateCheckedTODO()
#-------------------------------------------------------------------------------
    def updateCheckedTODO(self, id, checked):
        cur = self.db.cursor()
        chk = 0 if checked == Qt.Unchecked else 1
        cur.execute("update TODOs set chkTODO = :chk where idTODO = :id", {"chk": chk, "id": id})
        self.db.commit()
        cur.close()
      
            

"""
REGEX TESTER    https://regex101.com/
BANNER ASCII    http://patorjk.com/software/taag/#p=display&f=Graffiti&t=Type%20Something%20
QtDesigner

CREATE TABLE TODOs (
	idTODO INTEGER DEFAULT 1 NOT NULL,
	dteTODO INTEGER,
	ordTODO INTEGER DEFAULT 10 NOT NULL,
	txtTODO TEXT NOT NULL,
	txtNOTE TEXT,
	chkTODO INTEGER DEFAULT 0 NOT NULL
);

>>> import time
>>> import datetime
>>> s = "01/12/2011"
>>> time.mktime(datetime.datetime.strptime(s, "%d/%m/%Y").timetuple())
1322697600.0

selmodel = self.treeWidget.selectionModel()
selmodel.selectionChanged.connect(self.handleSelection)
        ...

    def handleSelection(self, selected, deselected):
        for index in selected.indexes():
            item = self.treeWidget.itemFromIndex(index)
            print('SEL: row: %s, col: %s, text: %s' % (
                index.row(), index.column(), item.text(0)))
        for index in deselected.indexes():
            item = self.treeWidget.itemFromIndex(index)
            print('DESEL: row: %s, col: %s, text: %s' % (
                index.row(), index.column(), item.text(0)))

"""
