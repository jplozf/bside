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
 

import settings
import dialog

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
        
        # self.mw.dbTODO = sqlite3.connect(os.path.join(self.mw.appDir, "todo.db"))
        self.mw.dbTODO.execute(
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
        self.mw.dbTODO.commit()      
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
        item = self.mw.tvwTODO.currentItem()
        if item:
            parent = item.parent()
            if parent is not None:
                lbl = parent.text(0)
            else:
                lbl = item.text(0)
            dlg = dialog.DlgAddTODO(self.mw, lbl)
        else:
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
        # cur = self.mw.dbTODO.cursor()
        data = (lblTODO, txtTODO, ordTODO, txtNOTE, chkTODO)
        print(data)
        self.mw.curTODO.execute("insert into TODOs(lblTODO, txtTODO, ordTODO, txtNOTE, chkTODO) values (?, ?, ?, ?, ?)", data)
        # cur.close      
        self.mw.dbTODO.commit()
        self.displayTODOs()
        self.setTODOFocus(lblTODO, txtTODO)
        
#-------------------------------------------------------------------------------
# getNextOrder()
#-------------------------------------------------------------------------------
    def getNextOrder(self, lblTODO):
        # cur = self.mw.dbTODO.cursor()
        self.mw.curTODO.execute("select max(ordTODO)+10 from TODOs where lblTODO = :label", {"label": lblTODO})
        nxt = self.mw.curTODO.fetchone()[0]
        if nxt is None:
            nxt = 10
        # cur.close()
        return(nxt)

#-------------------------------------------------------------------------------
# delTODO()
#-------------------------------------------------------------------------------
    def delTODO(self):
        item = self.mw.tvwTODO.currentItem()
        if item:
            parent = item.parent().text(0)                
            idTODO = int(item.text(1))
            self.mw.curTODO.execute("delete from TODOs where idTODO = (?)", (idTODO,))
            self.mw.dbTODO.commit()
            self.displayTODOs()
            self.setTODOFocus(parent)

#-------------------------------------------------------------------------------
# upTODO()
#-------------------------------------------------------------------------------
    def upTODO(self):
        item = self.mw.tvwTODO.currentItem()
        if item:
            if item.text(1) != "":
                currID = int(item.text(1))
                prevID = self.getPrevID(currID)
                print("CurrID = %d" % currID)
                print("PrevID = %d" % prevID)
                        
#-------------------------------------------------------------------------------
# downTODO()
#-------------------------------------------------------------------------------
    def downTODO(self):
        item = self.mw.tvwTODO.currentItem()
        if item:
            if item.text(1) != "":
                currID = int(item.text(1))
                nextID = self.getNextID(currID)
                print("CurrID = %d" % currID)
                print("NextID = %d" % nextID)
        
#-------------------------------------------------------------------------------
# changeNOTE()
#-------------------------------------------------------------------------------
    def changeNote(self):
        item = self.mw.tvwTODO.currentItem()
        if item:
            try:
                self.updateNoteTODO(int(item.text(1)), self.mw.txtNote.toPlainText())
            except:
                pass
        
#-------------------------------------------------------------------------------
# setTODOFocus()
#-------------------------------------------------------------------------------
    def setTODOFocus(self, lbl, txt=None):
        found = False
        root = self.mw.tvwTODO.invisibleRootItem()
        children = root.childCount()
        for i in range(children):
            itmLabel = root.child(i)
            if itmLabel.text(0) == lbl:
                if txt is not None:
                    jChildren = itmLabel.childCount()
                    for j in range(jChildren):
                        itmTxt = itmLabel.child(j)
                        if itmTxt.text(0) == txt:
                            found = True
                            break
                    else:
                        itmTxt = itmLabel
                        found = True
        if found == True:
            self.mw.tvwTODO.setCurrentItem(itmTxt)
        self.mw.tvwTODO.expandAll()

#-------------------------------------------------------------------------------
# displayTODOs()
#-------------------------------------------------------------------------------
    def displayTODOs(self):
        self.mw.curTODO.execute("select idTODO, lblTODO, ordTODO, txtTODO, txtNOTE, chkTODO from TODOs order by lblTODO, ordTODO")
        rows = self.mw.curTODO.fetchall() 
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
        # cur.close()

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
                        self.resizeSplitter(self.mw.splitter, 0, 100)
                    else:
                        self.resizeSplitter(self.mw.splitter, 0, 50)
            except:
                self.mw.txtNote.setPlainText("")
                if settings.db["TODO_AUTORESIZE_NOTE"]:
                    self.resizeSplitter(self.mw.splitter, 0, 100)
                
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
        # cur = self.db.cursor()
        self.mw.curTODO.execute("select txtNOTE from TODOs where idTODO = :id", {"id": id})
        note = self.mw.curTODO.fetchone()[0]
        # cur.close()
        return note
    
#-------------------------------------------------------------------------------
# updateCheckedTODO()
#-------------------------------------------------------------------------------
    def updateCheckedTODO(self, id, checked):
        chk = 0 if checked == Qt.Unchecked else 1
        self.mw.curTODO.execute("update TODOs set chkTODO = :chk where idTODO = :id", {"chk": chk, "id": id})
        self.mw.dbTODO.commit()
      
#-------------------------------------------------------------------------------
# updateNoteTODO()
#-------------------------------------------------------------------------------
    def updateNoteTODO(self, id, note):
        self.mw.tvwTODO.blockSignals(True)
        self.mw.curTODO.execute("update TODOs set txtNOTE = :note where idTODO = :id", {"note": note, "id": id})
        self.mw.dbTODO.commit()
        self.mw.tvwTODO.blockSignals(False)

#-------------------------------------------------------------------------------
# getNextID()
# https://stackoverflow.com/questions/17828070/select-next-and-previous-row-data-sqlite
#-------------------------------------------------------------------------------
    def getNextID(self, id):
        self.mw.curTODO.execute("select idTODO from TODOs where idTODO > ? order by lblTODO, ordTODO limit 1", (id,))
        nextID = self.mw.curTODO.fetchone()[0]
        return nextID
        """
        SELECT *
        FROM MyTable
        WHERE NameID > 8787
        ORDER BY NameID
        LIMIT 1
        """    

#-------------------------------------------------------------------------------
# getPrevID()
# https://stackoverflow.com/questions/17828070/select-next-and-previous-row-data-sqlite
#-------------------------------------------------------------------------------
    def getPrevID(self, id):
        self.mw.curTODO.execute("select idTODO from TODOs where idTODO < ? order by lblTODO, ordTODO desc limit 1", (id,))
        prevID = self.mw.curTODO.fetchone()[0]
        return prevID
        """
        SELECT *
        FROM MyTable
        WHERE NameID < 8787
        ORDER BY NameID DESC
        LIMIT 1
        """