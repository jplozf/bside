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
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import os
import platform
import subprocess
import tempfile

import const
import editor
import scratch

#-------------------------------------------------------------------------------
# class DlgProperties
#-------------------------------------------------------------------------------
class DlgManageTools(QDialog):
    aLblMenu = []
    aLblProgram = []
    aBtnEdit = []
    aBtnDelete = []
    aBtnBrowse = []
    aBtnCancel = []
    aBtnUp = []
    aBtnDown = []
    
#-------------------------------------------------------------------------------
# __init__()
#-------------------------------------------------------------------------------
    def __init__(self, parent=None):
        super().__init__(parent)
        self.display(parent)
        
#-------------------------------------------------------------------------------
# display()
#-------------------------------------------------------------------------------
    def display(self, parent):
        self.mw = parent        
        self.setWindowTitle("Manage Tools")
        
        self.vLayout = QVBoxLayout(self)                
        
        self.scroll = QScrollArea()
        self.wGrid = QWidget()
        self.vBox = QVBoxLayout()
        self.refreshGrid()        
        self.wGrid.setLayout(self.vBox)   
        self.scroll.setWidget(self.wGrid)
        self.vLayout.addWidget(self.scroll)

        self.hLayout = QHBoxLayout(self)
        self.txtMenu = QLineEdit()
        self.txtProgram = QLineEdit()
        self.btnBrowse = QPushButton("Browse")
        self.btnAdd = QPushButton("Add")
        self.btnAdd.clicked.connect(self.addMenu)
        self.btnBrowse.clicked.connect(lambda _,x=-1 : self.doBrowse(x))
        self.hLayout.addWidget(self.txtMenu)
        self.hLayout.addWidget(self.txtProgram)
        self.hLayout.addWidget(self.btnBrowse)
        self.hLayout.addWidget(self.btnAdd)

        self.vLayout.addLayout(self.hLayout)        

        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok, self);
        buttonBox.accepted.connect(self.OKMenu)        
        
        self.vLayout.addWidget(buttonBox)
        
#-------------------------------------------------------------------------------
# OKMenu()
#-------------------------------------------------------------------------------
    def OKMenu(self):
        initMenuTools(self.mw)
        self.accept()
        
#-------------------------------------------------------------------------------
# addMenu()
#-------------------------------------------------------------------------------
    def addMenu(self):
        if self.txtMenu.text() != "" and self.txtProgram.text() != "":
            self.mw.tools.append([self.txtMenu.text(),self.txtProgram.text()])
            self.txtMenu.setText("")
            self.txtProgram.setText("")
            self.refreshGrid()
        
#-------------------------------------------------------------------------------
# clearLayout()
#-------------------------------------------------------------------------------
    def clearLayout(self, layout):
        if layout is not None:
            while layout.count():
                child = layout.takeAt(0)
                if child.widget() is not None:
                    child.widget().deleteLater()
                elif child.layout() is not None:
                    self.clearLayout(child.layout())        
                    
#-------------------------------------------------------------------------------
# refreshGrid()
#-------------------------------------------------------------------------------
    def refreshGrid(self):
        self.clearLayout(self.vBox)            
        if len(self.mw.tools) > 0:                 
            self.aLblMenu.clear()
            self.aLblProgram.clear()
            self.aBtnEdit.clear()
            self.aBtnDelete.clear()
            self.aBtnBrowse.clear()
            self.aBtnCancel.clear()
            self.aBtnUp.clear()
            self.aBtnDown.clear()
            
            for i in range(len(self.mw.tools)):
                self.lblMenu = QLineEdit(self.mw.tools[i][0])
                self.lblMenu.setReadOnly(True)
                self.aLblMenu.append(self.lblMenu)
                                
                self.lblProgram = QLineEdit(self.mw.tools[i][1])
                self.lblProgram.setReadOnly(True)
                self.aLblProgram.append(self.lblProgram)
                
                self.btnEdit = QPushButton("Edit")
                self.btnEdit.clicked.connect(lambda _,x=i : self.doEdit(x))
                self.aBtnEdit.append(self.btnEdit)
                
                self.btnDelete = QPushButton()
                self.btnDelete.setIcon(QIcon("pix/16x16/Trash.png"))
                self.btnDelete.clicked.connect(lambda _,x=i : self.doDelete(x))
                self.aBtnDelete.append(self.btnDelete)
                
                self.btnBrowse = QPushButton()
                self.btnBrowse.setIcon(QIcon("pix/16x16/Folder.png"))
                self.btnBrowse.clicked.connect(lambda _,x=i : self.doBrowse(x))
                self.btnBrowse.setEnabled(False)
                self.aBtnBrowse.append(self.btnBrowse)
                
                self.btnCancel = QPushButton()
                self.btnCancel.setIcon(QIcon("pix/16x16/Cancel.png"))
                self.btnCancel.clicked.connect(lambda _,x=i : self.doCancel(x))
                self.btnCancel.setEnabled(False)
                self.aBtnCancel.append(self.btnCancel)
                
                self.btnUp =QPushButton()
                self.btnUp.setIcon(QIcon("pix/16x16/Arrow - Up.png"))
                self.btnUp.clicked.connect(lambda _,x=i : self.doUp(x))
                self.btnUp.setEnabled(i!=0)
                self.aBtnUp.append(self.btnUp)
                
                self.btnDown =QPushButton()
                self.btnDown.setIcon(QIcon("pix/16x16/Arrow - Down.png"))
                self.btnDown.clicked.connect(lambda _,x=i : self.doDown(x))
                self.btnDown.setEnabled(i!=len(self.mw.tools)-1)
                self.aBtnDown.append(self.btnDown)

                self.hBox = QHBoxLayout()
                lblPicture = QLabel()
                lblPicture.setPixmap(QPixmap("pix/16x16/Player Play.png"))
                self.hBox.addWidget(lblPicture)
                self.hBox.addWidget(self.aLblMenu[i])
                self.hBox.addWidget(self.aBtnEdit[i])
                self.hBox.addWidget(self.aBtnBrowse[i])
                self.hBox.addWidget(self.aBtnCancel[i])
                self.hBox.addWidget(self.aBtnDelete[i])                               
                self.hBox.addWidget(self.aBtnUp[i])
                self.hBox.addWidget(self.aBtnDown[i])                               
                
                self.vBox.addLayout(self.hBox)
                self.vBox.addWidget(self.aLblProgram[i])
                self.vBox.addWidget(QHLine())

#-------------------------------------------------------------------------------
# doEdit()
#-------------------------------------------------------------------------------
    def doEdit(self, x):
        if self.aBtnEdit[x].text() == "Edit":
            self.aLblMenu[x].setReadOnly(False)
            self.aLblProgram[x].setReadOnly(False)
            self.aBtnBrowse[x].setEnabled(True)
            self.aBtnCancel[x].setEnabled(True)
            self.aBtnEdit[x].setText("Save")
        else:
            self.aLblMenu[x].setReadOnly(True)
            self.aLblProgram[x].setReadOnly(True)
            self.aBtnBrowse[x].setEnabled(False)
            self.aBtnCancel[x].setEnabled(False)
            self.aBtnEdit[x].setText("Edit")
            
            self.mw.tools[x][0] = self.aLblMenu[x].text()
            self.mw.tools[x][1] = self.aLblProgram[x].text()
            
            self.refreshGrid()            

#-------------------------------------------------------------------------------
# doBrowse()
#-------------------------------------------------------------------------------
    def doBrowse(self, x):
        if x == -1:
            curFile = self.txtProgram.text()
        else:
            curFile = self.aLblProgram[x].text()
        fname = QFileDialog.getOpenFileName(self, 'Open file', curFile, "All files (*)")
        if fname:
            if x == -1:
                self.txtProgram.setText(fname[0])
            else:
                self.aLblProgram[x].setText(fname[0])
            
#-------------------------------------------------------------------------------
# doDelete()
#-------------------------------------------------------------------------------
    def doDelete(self, x):
        qm = QMessageBox
        rc = qm.question(self, '', "Delete this line ?", qm.Yes | qm.No)        
        if rc == qm.Yes:
            del self.mw.tools[x]
            self.refreshGrid()

#-------------------------------------------------------------------------------
# doCancel()
#-------------------------------------------------------------------------------
    def doCancel(self, x):
        self.refreshGrid()

#-------------------------------------------------------------------------------
# doUp()
#-------------------------------------------------------------------------------
    def doUp(self, x):
        old = x
        new = x - 1
        self.mw.tools.insert(new, self.mw.tools.pop(old))
        self.refreshGrid()

#-------------------------------------------------------------------------------
# doDown()
#-------------------------------------------------------------------------------
    def doDown(self, x):
        old = x
        new = x + 1
        self.mw.tools.insert(new, self.mw.tools.pop(old))
        self.refreshGrid()

#-------------------------------------------------------------------------------
# manageTools()
#-------------------------------------------------------------------------------
def manageTools(mw):
    dlg = DlgManageTools(mw)
    dlg.exec()

#-------------------------------------------------------------------------------
# initMenuTools()
#-------------------------------------------------------------------------------
def initMenuTools(mw):
    lstActions = mw.menuTools.actions()
    # Clear Tools menu but first action (Manage Tools)
    if len(lstActions) > 1:
        for i in range(1, len(lstActions)):
            mw.menuTools.removeAction(lstActions[i])
    # Populate Tools menu
    if len(mw.tools) > 0:        
        # Action text
        for i in range(len(mw.tools)):
            mw.menuTools.addAction(mw.tools[i][0])
        # Action to run
        lstActions = mw.menuTools.actions()
        for i in range(1, len(lstActions)):
            lstActions[i].triggered.connect(lambda _, m=mw, x=i-1 : doAction(m, x))
            
#-------------------------------------------------------------------------------
# doAction()
#-------------------------------------------------------------------------------
def doAction(mw, i):
    doThis = mw.tools[i][1]
    tab = mw.tbwHighRight.widget(mw.tbwHighRight.currentIndex())
    if isinstance(tab, editor.WEditor) or isinstance(tab, editor.WHexedit) or isinstance(tab, editor.WMarkdown):
        doFile = tab.filename
    else:
        doFile = ""
        
    """
    FULLNAME                FOO
    BASENAME                os.path.basename(FOO)
    DIRNAME                 os.path.dirname(FOO)
    FULLNAME_WITHOUT_EXT    os.path.splitext(FOO)[0]
    NAME_WITHOUT_EXT        os.path.splitext(os.path.basename(FOO))[0]
    EXTENSION               os.path.splitext(FOO)[1]
    RANDOM_NAME             scratch.getRandomName(extension="")
    TEMPDIR                 tempfile.gettempdir()
    PATHSEP                 os.path.sep
    PROJECT                 mw.project.name
    HOME                    os.path.expanduser("~")
    """
    
    doThis = doThis.replace("[FULLNAME]", doFile)
    doThis = doThis.replace("[BASENAME]", os.path.basename(doFile))
    doThis = doThis.replace("[DIRNAME]", os.path.dirname(doFile))
    doThis = doThis.replace("[FULLNAME_WITHOUT_EXT]", os.path.splitext(doFile)[0])
    doThis = doThis.replace("[NAME_WITHOUT_EXT]", os.path.splitext(os.path.basename(doFile))[0])
    doThis = doThis.replace("[EXTENSION]", os.path.splitext(doFile)[1])   
    doThis = doThis.replace("[RANDOM_NAME]", scratch.getRandomName(extension=""))
    doThis = doThis.replace("[TEMPDIR]", tempfile.gettempdir())
    doThis = doThis.replace("[PATHSEP]", os.path.sep)
    doThis = doThis.replace("[PROJECT]", const.PROJECT_NONE if mw.project is None else mw.project.name)
    doThis = doThis.replace("[HOME]", os.path.expanduser("~"))
    
    print("ACTION %s : %s" % (str(i), doThis))
    try:
        lstDoThis = doThis.split()
        subprocess.Popen(lstDoThis)        
        mw.showMessage("Running %s" % doThis)
    except:
        try:
            if platform.system() == 'Darwin':       # macOS
                subprocess.call(('open', doThis))
            elif platform.system() == 'Windows':    # Windows
                os.startfile(doThis)
            else:                                   # linux variants
                subprocess.call(('xdg-open', doThis))
            mw.showMessage("Opening %s" % doThis)
        except:
            mw.showMessage("Don't know how to open %s" % doThis)
            
#-------------------------------------------------------------------------------
# class QHLine
#-------------------------------------------------------------------------------
class QHLine(QFrame):
    def __init__(self):
        super(QHLine, self).__init__()
        self.setFrameShape(QFrame.HLine)
        self.setFrameShadow(QFrame.Sunken)

#-------------------------------------------------------------------------------
# class QVLine
#-------------------------------------------------------------------------------
class QVLine(QFrame):
    def __init__(self):
        super(QVLine, self).__init__()
        self.setFrameShape(QFrame.VLine)
        self.setFrameShadow(QFrame.Sunken)            
    