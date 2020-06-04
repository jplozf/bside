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
from datetime import date
import pkg_resources

import utils
import editor


#-------------------------------------------------------------------------------
# class DlgAddMedia
#-------------------------------------------------------------------------------
class DlgAddMedia(QDialog):
    def __init__(self):
        pass
    
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
            self.lblKey = QLabel(key)
            self.txtValue = QLineEdit(str(value))
            self.txtValue.setEnabled(False)
            layout.addRow(self.lblKey, self.txtValue)

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
        
        if projectName is not None:
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
        icoRun = QIcon("pix/16x16/Ok.png")
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
    def __init__(self, parent, lbl=None):
        super().__init__(parent)    
        
        self.setWindowTitle("Add TODO")  
        mainLayout = QVBoxLayout(self)
        
        formLayout = QFormLayout(self)
        
        self.hBox = QHBoxLayout()        
        
        if lbl is None :
            self.lblTODO = QLineEdit(date.today().strftime("%d/%m/%Y"))
        else:
            self.lblTODO = QLineEdit(lbl)
        self.lblTODO.selectAll()
        self.btnPickDate = QPushButton()
        icoPickDate = QIcon("pix/16x16/Clock.png")
        self.btnPickDate.setIcon(icoPickDate)
        self.btnPickDate.clicked.connect(self.pickDate)
        self.hBox.addWidget(self.lblTODO)
        self.hBox.addWidget(self.btnPickDate)
        
        formLayout.addRow("Label", self.hBox)        
        
        self.txtTODO = QLineEdit()
        self.txtTODO.returnPressed.connect(self.itsOK)
        formLayout.addRow("TODO", self.txtTODO)
                
        self.txtNote = QPlainTextEdit()
        formLayout.addRow("Notes", self.txtNote)

        boxLayout = QHBoxLayout(self)
        btnRun = QPushButton()
        icoRun = QIcon("pix/16x16/Ok.png")
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
            self.tplTODO =  (self.lblTODO.text(), self.txtTODO.text(), self.txtNote.toPlainText())
            self.accept()
        else:
            self.reject()
            
#-------------------------------------------------------------------------------
# pickDate()
#-------------------------------------------------------------------------------
    def pickDate(self):
        dlg = DlgCalendar(self)
        result = dlg.exec()
        if result == QDialog.Accepted:
            self.lblTODO.setText(str(dlg.selectedDate))
    
#-------------------------------------------------------------------------------
# Class DlgCalendar
#-------------------------------------------------------------------------------
class DlgCalendar(QDialog):
#-------------------------------------------------------------------------------
# __init__()
#-------------------------------------------------------------------------------
    def __init__(self, parent):
        super().__init__(parent)    
        self.setWindowTitle("Pick up a date")  
        mainLayout = QVBoxLayout(self)
        
        self.calendar = QCalendarWidget()
        mainLayout.addWidget(self.calendar)
        
        boxLayout = QHBoxLayout(self)
        btnRun = QPushButton()
        icoRun = QIcon("pix/16x16/Ok.png")
        btnRun.setIcon(icoRun)
        btnCancel = QPushButton()
        icoCancel = QIcon("pix/16x16/Cancel.png")
        btnCancel.setIcon(icoCancel)
        
        btnRun.clicked.connect(self.itsOK)
        btnCancel.clicked.connect(self.close)

        boxLayout.addStretch(1)
        boxLayout.addWidget(btnRun)
        boxLayout.addWidget(btnCancel)

        mainLayout.addLayout(boxLayout)
    
#-------------------------------------------------------------------------------
# itsOK()
#-------------------------------------------------------------------------------
    def itsOK(self):
        self.selectedDate = self.calendar.selectedDate().toString("dd/MM/yyyy")
        self.accept()
        """
        if self.txtTODO.text() != "":
            self.tplTODO =  (self.dteTODO.date().toString("dd/MM/yyyy"), self.txtTODO.text(), self.txtNote.toPlainText())
            self.accept()
        else:
            self.reject()
        """
            
#-------------------------------------------------------------------------------
# Class DlgAddTODO2
#-------------------------------------------------------------------------------
class DlgAddTODO2(QDialog):
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
        icoRun = QIcon("pix/16x16/Ok.png")
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
        
"""
today = date.today()

# dd/mm/YY
d1 = today.strftime("%d/%m/%Y")
print("d1 =", d1)

# Textual month, day and year	
d2 = today.strftime("%B %d, %Y")
print("d2 =", d2)

# mm/dd/y
d3 = today.strftime("%m/%d/%y")
print("d3 =", d3)

# Month abbreviation, day and year	
d4 = today.strftime("%b-%d-%Y")
print("d4 =", d4)
"""        
#-------------------------------------------------------------------------------
# newModule()
#-------------------------------------------------------------------------------
def newModule(mw, path):
    dlg = DlgNewObject(None, path, "module", "new.py", mw)
    result = dlg.exec()
    if result == QDialog.Accepted:
        mw.showMessage("Create module %s" % dlg.rname)    
        if not os.path.isfile(dlg.rname):
            module = "resources/templates/newfiles/new.py"
            utils.copyFile(pkg_resources.resource_filename(__name__, module), dlg.rname)            
            mw.showMessage("New module %s created" % dlg.rname)
        else:
            mw.showMessage("Module %s already exists" % dlg.rname)
        openFile(mw, dlg.rname, "python")

#-------------------------------------------------------------------------------
# newXMLFile()
#-------------------------------------------------------------------------------
def newXMLFile(mw, path):
    dlg = DlgNewObject(None, path, "XML file", "new.xml", mw)
    result = dlg.exec()
    if result == QDialog.Accepted:
        mw.showMessage("Create XML %s" % dlg.rname)            
        if not os.path.isfile(dlg.rname):
            xml = "resources/templates/newfiles/new.xml"
            utils.copyFile(pkg_resources.resource_filename(__name__, xml), dlg.rname)            
            mw.showMessage("New XML %s created" % dlg.rname)
        else:
            mw.showMessage("XML %s already exists" % dlg.rname)
        openFile(mw, dlg.rname, "xml")

#-------------------------------------------------------------------------------
# newHTMLFile()
#-------------------------------------------------------------------------------
def newHTMLFile(mw, path):
    dlg = DlgNewObject(None, path, "HTML file", "new.html", mw)
    result = dlg.exec()
    if result == QDialog.Accepted:
        mw.showMessage("Create HTML %s" % dlg.rname)            
        if not os.path.isfile(dlg.rname):
            html = "resources/templates/newfiles/new.html"
            utils.copyFile(pkg_resources.resource_filename(__name__, html), dlg.rname)            
            mw.showMessage("New HTML %s created" % dlg.rname)
        else:
            mw.showMessage("HTML %s already exists" % dlg.rname)
        openFile(mw, dlg.rname, "html")

#-------------------------------------------------------------------------------
# newMDFile()
#-------------------------------------------------------------------------------
def newMDFile(mw, path):
    dlg = DlgNewObject(None, path, "MarkDown file", "new.md", mw)
    result = dlg.exec()
    if result == QDialog.Accepted:
        mw.showMessage("Create Markdown %s" % dlg.rname)            
        if not os.path.isfile(dlg.rname):
            md = "resources/templates/newfiles/new.md"
            utils.copyFile(pkg_resources.resource_filename(__name__, md), dlg.rname)            
            mw.showMessage("New Markdown %s created" % dlg.rname)
        else:
            mw.showMessage("Markdown %s already exists" % dlg.rname)
        openFile(mw, dlg.rname, "md")

#-------------------------------------------------------------------------------
# newQtUIFile()
#-------------------------------------------------------------------------------
def newQtUIFile(mw, path):
    dlg = DlgNewObject(None, path, "Qt UI file", "new.ui", mw)
    result = dlg.exec()
    if result == QDialog.Accepted:
        mw.showMessage("Create UI %s" % dlg.rname)            
        if not os.path.isfile(dlg.rname):
            ui = "resources/templates/newfiles/new.ui"
            utils.copyFile(pkg_resources.resource_filename(__name__, ui), dlg.rname)            
            mw.showMessage("New Qt UI %s created" % dlg.rname)
        else:
            mw.showMessage("Qt UI %s already exists" % dlg.rname)
        openFile(mw, dlg.rname, "xml")

#-------------------------------------------------------------------------------
# newSQLFile()
#-------------------------------------------------------------------------------
def newSQLFile(mw, path):
    dlg = DlgNewObject(None, path, "SQL file", "new.sql", mw)
    result = dlg.exec()
    if result == QDialog.Accepted:
        mw.showMessage("Create SQL %s" % dlg.rname)            
        if not os.path.isfile(dlg.rname):
            sql = "resources/templates/newfiles/new.sql"
            utils.copyFile(pkg_resources.resource_filename(__name__, sql), dlg.rname)            
            mw.showMessage("New SQL %s created" % dlg.rname)
        else:
            mw.showMessage("SQL %s already exists" % dlg.rname)
        openFile(mw, dlg.rname, "sql")

#-------------------------------------------------------------------------------
# newFile()
#-------------------------------------------------------------------------------
def newFile(mw, path):
    dlg = DlgNewObject(None, path, "file", "newfile", mw)
    result = dlg.exec()
    if result == QDialog.Accepted:
        mw.showMessage("Create file %s" % dlg.rname)            
        if utils.createFile(os.path.dirname(dlg.rname), os.path.basename(dlg.rname)):                
            mw.showMessage("New file %s created" % dlg.rname)
            openFile(mw, dlg.rname, "text")
        else:
            mw.showMessage("Can't create %s" % dlg.rname)

#-------------------------------------------------------------------------------
# newFolder()
#-------------------------------------------------------------------------------
def newFolder(mw, path):
    dlg = DlgNewObject(None, path, "folder", "newfolder", mw)
    result = dlg.exec()
    if result == QDialog.Accepted:
        mw.showMessage("Create folder %s" % dlg.rname)            
        if utils.createDirectory(os.path.dirname(dlg.rname), os.path.basename(dlg.rname)):                
            mw.showMessage("New folder %s created" % dlg.rname)
        else:
            mw.showMessage("Can't create %s" % dlg.rname)

#-------------------------------------------------------------------------------
# openFile()
#-------------------------------------------------------------------------------
def openFile(mw, name, filetype="python"):
    extension = os.path.splitext(name)[1]
    icon = None
    if extension == ".py":
        icon = "pix/icons/text-x-python.png"
    elif extension == ".xml":
        icon = "pix/icons/application-xml.png"
    elif extension == ".html":
        icon = "pix/icons/text-html.png"
    elif extension == ".sql":
        icon = "pix/icons/database.png"
    elif extension == ".md":
        icon = "pix/icons/markdown.png"
    elif extension == ".ui":
        icon = "pix/icons/QtUI.png"
    else:
        icon = "pix/icons/text-icon.png"

    if mw.isFileOpen(name)[0] == False:
        if filetype == "md":
            tabEditor = editor.WMarkdown(filename=name, parent=mw.tbwHighRight, window=mw)
        else:
            tabEditor = editor.WEditor(filename=name, parent=mw.tbwHighRight, window=mw, filetype=filetype)        
        bname = os.path.basename(name)
        mw.tbwHighRight.addTab(tabEditor, bname)
        idxTab = mw.tbwHighRight.count() - 1
        mw.tbwHighRight.setTabIcon(idxTab, QIcon(icon))
        mw.tbwHighRight.setCurrentIndex(idxTab)               

        # tabEditor.txtEditor.textChanged.connect(lambda x=tabEditor: self.textChange(x))
        mw.showMessage("Editing %s" % name)         

        return tabEditor
    else:
        mw.showMessage("File %s already open" % name)         
            