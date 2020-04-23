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
# from PyQt5.QtWidgets import (QDialog, QHBoxLayout, QVBoxLayout, QPushButton, QLabel, QFormLayout, QLineEdit, QCheckBox)
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import platform
import os

#-------------------------------------------------------------------------------
# class DlgProperties
#-------------------------------------------------------------------------------
class DlgProperties(QDialog):
#-------------------------------------------------------------------------------
# __init__()
#-------------------------------------------------------------------------------
    def __init__(self, dict, parent=None):
        super().__init__(parent)
        
        self.setWindowTitle("Properties")
        layout = QFormLayout(self)
        for key, value in dict.items():
            self.Line = QLabel(self)
            self.Line.setText(str(value))
            layout.addRow(key, self.Line)

        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok, self);
        layout.addWidget(buttonBox)

        buttonBox.accepted.connect(self.accept)
        
#-------------------------------------------------------------------------------
# class DlgRunScript
#-------------------------------------------------------------------------------
class DlgRunScript(QDialog):
#-------------------------------------------------------------------------------
# __init__()
#-------------------------------------------------------------------------------
    def __init__(self, filename, parent=None):
        super().__init__(parent)
        
        self.params = ""
        self.externalShell = False
        
        self.setWindowTitle("Run script")  
        mainLayout = QVBoxLayout(self)
        
        formLayout = QFormLayout(self)
        
        self.Line = QLabel(self)
        self.Line.setText(filename)
        formLayout.addRow("Script", self.Line)        
        
        self.txtParams = QLineEdit()
        formLayout.addRow("Parameters", self.txtParams)
        
        self.lblPython = QLabel(platform.python_version())
        formLayout.addRow("Python version", self.lblPython)
        
        self.chkExternalShell = QCheckBox()
        formLayout.addRow("External Shell", self.chkExternalShell)

        boxLayout = QHBoxLayout(self)
        btnRun = QPushButton()
        icoRun = QIcon("pix/16x16/Player Play.png")
        btnRun.setIcon(icoRun)
        btnCancel = QPushButton()
        icoCancel = QIcon("pix/16x16/Cancel.png")
        btnCancel.setIcon(icoCancel)
        btnRun.clicked.connect(self.runMe)
        btnCancel.clicked.connect(self.close)

        boxLayout.addStretch(1)
        boxLayout.addWidget(btnRun)
        boxLayout.addWidget(btnCancel)

        mainLayout.addLayout(formLayout)
        mainLayout.addLayout(boxLayout)
    
    def runMe(self):
        self.params = self.txtParams.text()
        self.externalShell = self.chkExternalShell.isChecked()
        self.accept()

#-------------------------------------------------------------------------------
# class DlgNewObject
#-------------------------------------------------------------------------------
class DlgNewObject(QDialog):
    """
RW File Name
RO Project
RW Folder       [Browse]
RO Created File
    """    
    rname = ""
#-------------------------------------------------------------------------------
# __init__()
#-------------------------------------------------------------------------------
    def __init__(self, projectName, pHere, oType, filename, parent):
        super().__init__(parent)    
        self.rname = ""
        self.pHere = pHere
        
        self.setWindowTitle("New %s" % oType)  
        mainLayout = QVBoxLayout(self)        
        formLayout = QFormLayout(self)
        
        self.txtFilename = QLineEdit(filename)
        self.txtFilename.textChanged.connect(self.doChangeName)
        formLayout.addRow("File name", self.txtFilename)
        
        self.txtProject = QLineEdit(projectName)
        self.txtProject.setReadOnly(True)
        formLayout.addRow("Project", self.txtProject)
        
        self.hBox = QHBoxLayout()
        self.txtFolder = QLineEdit()
        self.btnBrowse = QPushButton("Browse")
        self.btnBrowse.clicked.connect(self.doBrowse)
        self.hBox.addWidget(self.txtFolder)
        self.hBox.addWidget(self.btnBrowse)
        formLayout.addRow("Folder", self.hBox)
        
        self.txtCreatedFile = QLineEdit(os.path.join(self.pHere, self.txtFilename.text()))
        self.txtCreatedFile.setReadOnly(True)
        formLayout.addRow("Created file", self.txtCreatedFile)
        
        boxLayout = QHBoxLayout(self)
        btnRun = QPushButton()
        icoRun = QIcon("pix/16x16/Player Play.png")
        btnRun.setIcon(icoRun)
        btnCancel = QPushButton()
        icoCancel = QIcon("pix/16x16/Cancel.png")
        btnCancel.setIcon(icoCancel)
        btnRun.clicked.connect(self.itsok)
        btnCancel.clicked.connect(self.close)

        boxLayout.addStretch(1)
        boxLayout.addWidget(btnRun)
        boxLayout.addWidget(btnCancel)

        mainLayout.addLayout(formLayout)
        mainLayout.addLayout(boxLayout)
        
#-------------------------------------------------------------------------------
# itsok()
#-------------------------------------------------------------------------------
    def itsok(self):
        self.rname =  self.txtCreatedFile.text()
        if self.rname != "":
            self.accept()
        else:
            self.reject()
            
#-------------------------------------------------------------------------------
# doBrowse()
#-------------------------------------------------------------------------------
    def doBrowse(self):
        fname = QFileDialog.getExistingDirectory(self, "Select Directory", self.pHere, QFileDialog.ShowDirsOnly)
        if fname:
            self.pHere = fname
            self.txtFolder.setText(fname)
            self.txtCreatedFile.setText(os.path.join(self.pHere, self.txtFilename.text()))            
        
#-------------------------------------------------------------------------------
# doChangeName()
#-------------------------------------------------------------------------------
    def doChangeName(self):
            self.txtCreatedFile.setText(os.path.join(self.pHere, self.txtFilename.text()))            
        
#-------------------------------------------------------------------------------
# class DlgNewObject2
#-------------------------------------------------------------------------------
class DlgNewObject2(QDialog):
    """
RW File Name
RO Project
RW Folder       [Browse]
RO Created File
    """    
    rname = ""
#-------------------------------------------------------------------------------
# __init__()
#-------------------------------------------------------------------------------
    def __init__(self, pHere, oType, parent):
        super().__init__(parent)    
        self.rname = ""
        
        self.setWindowTitle("New %s" % oType)  
        mainLayout = QVBoxLayout(self)
        
        formLayout = QFormLayout(self)
        
        self.Line = QLabel(self)
        self.Line.setText(pHere)
        formLayout.addRow("Into", self.Line)        
        
        self.txtName = QLineEdit()
        formLayout.addRow("Name", self.txtName)
        
        boxLayout = QHBoxLayout(self)
        btnRun = QPushButton()
        icoRun = QIcon("pix/16x16/Player Play.png")
        btnRun.setIcon(icoRun)
        btnCancel = QPushButton()
        icoCancel = QIcon("pix/16x16/Cancel.png")
        btnCancel.setIcon(icoCancel)
        btnRun.clicked.connect(self.itsok)
        btnCancel.clicked.connect(self.close)

        boxLayout.addStretch(1)
        boxLayout.addWidget(btnRun)
        boxLayout.addWidget(btnCancel)

        mainLayout.addLayout(formLayout)
        mainLayout.addLayout(boxLayout)
        
#-------------------------------------------------------------------------------
# itsok()
#-------------------------------------------------------------------------------
    def itsok(self):
        self.rname =  self.txtName.text()
        if self.rname != "":
            self.accept()
        else:
            self.reject()
        
#-------------------------------------------------------------------------------
# Class DlgAddTODO
#-------------------------------------------------------------------------------
class DlgAddTODO(QDialog):
#-------------------------------------------------------------------------------
# __init__()
#-------------------------------------------------------------------------------
    def __init__(self, parent):
        super().__init__(parent)    
        
        self.setWindowTitle("Add TODO")  
        mainLayout = QVBoxLayout(self)
        
        formLayout = QFormLayout(self)
        
        self.dteTODO = QDateEdit()
        self.dteTODO.setDateTime(QDateTime.currentDateTime())
        formLayout.addRow("Date", self.dteTODO)        
        
        self.txtTODO = QLineEdit()
        formLayout.addRow("TODO", self.txtTODO)
        
        self.txtNote = QPlainTextEdit()
        formLayout.addRow("Notes", self.txtNote)

        boxLayout = QHBoxLayout(self)
        btnRun = QPushButton()
        icoRun = QIcon("pix/16x16/OK.png")
        btnRun.setIcon(icoRun)
        btnCancel = QPushButton()
        icoCancel = QIcon("pix/16x16/Cancel.png")
        btnCancel.setIcon(icoCancel)
        
        btnRun.clicked.connect(self.itsOK)
        btnCancel.clicked.connect(self.close)

        boxLayout.addStretch(1)
        boxLayout.addWidget(btnRun)
        boxLayout.addWidget(btnCancel)

        mainLayout.addLayout(formLayout)
        mainLayout.addLayout(boxLayout)
    
#-------------------------------------------------------------------------------
# itsOK()
#-------------------------------------------------------------------------------
    def itsOK(self):
        if self.txtTODO.text() != "":
            self.tplTODO =  (self.dteTODO.date().toString("dd/MM/yyyy"), self.txtTODO.text(), self.txtNote.toPlainText())
            self.accept()
        else:
            self.reject()
            
#-------------------------------------------------------------------------------
# class DlgAddData
#-------------------------------------------------------------------------------
class DlgAddData(QDialog):            
#-------------------------------------------------------------------------------
# __init__()
#-------------------------------------------------------------------------------
    def __init__(self, parent):
        super().__init__(parent)    
        
        self.setWindowTitle("Add Data")  
        mainLayout = QVBoxLayout(self)
        
        formLayout = QFormLayout(self)
        
        self.txtDataSource = QLineEdit()
        formLayout.addRow("Data source file or folder", self.txtDataSource)
        
        self.txtDataDest = QLineEdit()
        formLayout.addRow("Destination", self.txtDataDest)
        
        boxLayout = QHBoxLayout(self)
        btnRun = QPushButton()
        icoRun = QIcon("pix/16x16/OK.png")
        btnRun.setIcon(icoRun)
        btnCancel = QPushButton()
        icoCancel = QIcon("pix/16x16/Cancel.png")
        btnCancel.setIcon(icoCancel)
        
        btnRun.clicked.connect(self.accept)
        btnCancel.clicked.connect(self.close)

        boxLayout.addStretch(1)
        boxLayout.addWidget(btnRun)
        boxLayout.addWidget(btnCancel)

        mainLayout.addLayout(formLayout)
        mainLayout.addLayout(boxLayout)
        