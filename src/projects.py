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
from PyQt5.QtWidgets import (QDialog, QDialogButtonBox, QLabel, QLineEdit, QFormLayout, QComboBox)
from PyQt5.Qt import *
from PyQt5.QtGui import QRegExpValidator
import os
import pkg_resources
import lxml.etree
import lxml.builder    
import xml.etree.ElementTree as ET

from datetime import datetime, timedelta
from string import Template
import time

import utils
import const
import settings
import editor
import dialog
import backup

#-------------------------------------------------------------------------------
# class DlgNewProject
#-------------------------------------------------------------------------------
class DlgNewProject(QDialog):
#-------------------------------------------------------------------------------
# __init__()
#-------------------------------------------------------------------------------
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setWindowTitle("New Project")
        layout = QFormLayout(self)
        
        # Project name
        self.lblProjectName = QLabel("Project Name")
        self.txtProjectName = QLineEdit()
        self.txtProjectName.textChanged.connect(self.changedProjectName)
        self.regExp = QRegExp("^[_a-zA-Z]\\w*$")
        self.validator = QRegExpValidator(self.regExp)
        self.txtProjectName.setValidator(self.validator)
        layout.addRow(self.lblProjectName, self.txtProjectName)
        
        # Project folder
        self.lblProjectFolder = QLabel("Project Folder")
        self.txtProjectFolder = QLabel(settings.db['BSIDE_REPOSITORY'])
        layout.addRow(self.lblProjectFolder, self.txtProjectFolder)

        # Script template
        self.lblTemplate = QLabel("Template")
        self.cbxTemplate = QComboBox()
        for f in pkg_resources.resource_listdir(__name__, 'resources/templates/newfiles/python'):
            self.cbxTemplate.addItem(os.path.splitext(f)[0])
        layout.addRow(self.lblTemplate, self.cbxTemplate)
        
        # Module name
        self.lblModuleName = QLabel("Module Name")
        self.txtModuleName = QLineEdit("main.py")
        layout.addRow(self.lblModuleName, self.txtModuleName)
        
        # Author name
        self.lblAuthorName = QLabel("Author Name")
        self.txtAuthorName = QLineEdit(settings.db['PROJECT_USER_NAME'])
        layout.addRow(self.lblAuthorName, self.txtAuthorName)
        
        # Author mail
        self.lblAuthorMail = QLabel("Author Mail")
        self.txtAuthorMail = QLineEdit(settings.db['PROJECT_MAIL'])
        layout.addRow(self.lblAuthorMail, self.txtAuthorMail)

        # Company
        self.lblCompany = QLabel("Company")
        self.txtCompany = QLineEdit(settings.db['PROJECT_COMPANY'])
        layout.addRow(self.lblCompany, self.txtCompany)

        # Author Site
        self.lblAuthorSite = QLabel("Author Site")
        self.txtAuthorSite = QLineEdit(settings.db['PROJECT_SITE'])
        layout.addRow(self.lblAuthorSite, self.txtAuthorSite)

        # License model
        self.lblLicense = QLabel("License")
        self.cbxLicense = QComboBox()
        for f in pkg_resources.resource_listdir(__name__, 'resources/templates/licenses'):
            self.cbxLicense.addItem(os.path.splitext(f)[0])
        index = self.cbxLicense.findText(settings.db['PROJECT_LICENSE'])
        if index >= 0:
            self.cbxLicense.setCurrentIndex(index)        
        layout.addRow(self.lblLicense, self.cbxLicense)
                
        # Encoding
        self.lblEncoding = QLabel("Encoding")
        self.cbxEncoding = QComboBox()
        for f in const.ENCODING:
            self.cbxEncoding.addItem(f)
        index = self.cbxEncoding.findText(settings.db['EDITOR_CODEPAGE'])
        if index >= 0:
            self.cbxEncoding.setCurrentIndex(index)        
        layout.addRow(self.lblEncoding, self.cbxEncoding)

        # Buttons
        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self);
        layout.addWidget(buttonBox)
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)
        
        # Show modal and resize
        self.setWindowModality(Qt.ApplicationModal)
        self.show()        
        height = self.frameGeometry().height()        
        self.resize(640, height)
        
#-------------------------------------------------------------------------------
# changedProjectName()
#-------------------------------------------------------------------------------
    def changedProjectName(self, *args, **kwargs):
        self.txtProjectFolder.setText(os.path.join(settings.db['BSIDE_REPOSITORY'], self.txtProjectName.text()))
        self.txtAuthorSite.setText(settings.db['PROJECT_SITE'] +"/#" + self.txtProjectName.text())

        sender = self.sender()
        validator = sender.validator()
        state = validator.validate(sender.text(), 0)[0]
        if state == QValidator.Acceptable:
            color = '#c4df9b' # green
        elif state == QValidator.Intermediate:
            color = '#fff79a' # yellow
        else:
            color = '#f6989d' # red
        sender.setStyleSheet('QLineEdit { background-color: %s }' % color)        
    
#-------------------------------------------------------------------------------
# class DlgPromoteProject
#-------------------------------------------------------------------------------
class DlgPromoteProject(QDialog):
#-------------------------------------------------------------------------------
# __init__()
#-------------------------------------------------------------------------------
    def __init__(self, folder, parent=None):
        super().__init__(parent)
        
        self.setWindowTitle("Promote Folder to Project")
        layout = QFormLayout(self)
        
        projectName = os.path.basename(os.path.normpath(folder))
        projectName = projectName.replace(' ', '_')
        # Project name
        self.lblProjectName = QLabel("Project Name")
        self.txtProjectName = QLineEdit(projectName)
        self.txtProjectName.setReadOnly(True)
        layout.addRow(self.lblProjectName, self.txtProjectName)
        
        # Project folder
        self.lblProjectFolder = QLabel("Project Folder")
        self.txtProjectFolder = QLineEdit(folder)
        self.txtProjectFolder.setReadOnly(True)
        layout.addRow(self.lblProjectFolder, self.txtProjectFolder)
       
        # Module name
        self.lblModuleName = QLabel("Module Name")
        self.cbxModuleName = QComboBox()
        for root, dirs, files in os.walk(folder):
            for file in files:
                if file.endswith(".py"):
                    self.cbxModuleName.addItem(os.path.join(root, file))
        layout.addRow(self.lblModuleName, self.cbxModuleName)
        
        # Author name
        self.lblAuthorName = QLabel("Author Name")
        self.txtAuthorName = QLineEdit(settings.db['PROJECT_USER_NAME'])
        layout.addRow(self.lblAuthorName, self.txtAuthorName)
        
        # Author mail
        self.lblAuthorMail = QLabel("Author Mail")
        self.txtAuthorMail = QLineEdit(settings.db['PROJECT_MAIL'])
        layout.addRow(self.lblAuthorMail, self.txtAuthorMail)

        # Company
        self.lblCompany = QLabel("Company")
        self.txtCompany = QLineEdit(settings.db['PROJECT_COMPANY'])
        layout.addRow(self.lblCompany, self.txtCompany)

        # Author Site
        self.lblAuthorSite = QLabel("Author Site")
        self.txtAuthorSite = QLineEdit(settings.db['PROJECT_SITE'])
        layout.addRow(self.lblAuthorSite, self.txtAuthorSite)

        # License model
        self.lblLicense = QLabel("License")
        self.cbxLicense = QComboBox()
        for f in pkg_resources.resource_listdir(__name__, 'resources/templates/licenses'):
            self.cbxLicense.addItem(os.path.splitext(f)[0])
        index = self.cbxLicense.findText(settings.db['PROJECT_LICENSE'])
        if index >= 0:
            self.cbxLicense.setCurrentIndex(index)        
        layout.addRow(self.lblLicense, self.cbxLicense)
                
        # Encoding
        self.lblEncoding = QLabel("Encoding")
        self.cbxEncoding = QComboBox()
        for f in const.ENCODING:
            self.cbxEncoding.addItem(f)
        index = self.cbxEncoding.findText(settings.db['EDITOR_CODEPAGE'])
        if index >= 0:
            self.cbxEncoding.setCurrentIndex(index)        
        layout.addRow(self.lblEncoding, self.cbxEncoding)
                
        # Buttons
        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self);
        layout.addWidget(buttonBox)
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)
        
        # Show modal and resize
        self.setWindowModality(Qt.ApplicationModal)
        self.show()        
        height = self.frameGeometry().height()        
        self.resize(640, height)
        
#-------------------------------------------------------------------------------
# class DlgExportProject
#-------------------------------------------------------------------------------
class DlgExportProject(QDialog):
#-------------------------------------------------------------------------------
# __init__()
#-------------------------------------------------------------------------------
    def __init__(self, folder, parent=None):
        super().__init__(parent)
        
        self.setWindowTitle("Export Project")
        layout = QFormLayout(self)
        
        projectName = os.path.basename(os.path.normpath(folder))
        projectName = projectName.replace(' ', '_')
        # Project name
        self.lblProjectName = QLabel("Project Name")
        self.txtProjectName = QLineEdit(projectName)
        self.txtProjectName.setReadOnly(True)
        layout.addRow(self.lblProjectName, self.txtProjectName)
        
        # Export folder
        self.lblExportFolder = QLabel("Export Folder")
        self.hBox1 = QHBoxLayout()
        self.txtExportFolder = QLineEdit(QDir.homePath())
        self.btnBrowseFolder = QPushButton()
        icoBrowse = QIcon("pix/16x16/Folder.png")
        self.btnBrowseFolder.setIcon(icoBrowse)
        self.btnBrowseFolder.clicked.connect(self.browseExportFolder)
        self.hBox1.addWidget(self.txtExportFolder)
        self.hBox1.addWidget(self.btnBrowseFolder)
        layout.addRow(self.lblExportFolder, self.hBox1)
                       
        # Buttons
        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self);
        layout.addWidget(buttonBox)
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)
        
        # Show modal and resize
        self.setWindowModality(Qt.ApplicationModal)
        self.show()        

#-------------------------------------------------------------------------------
# browseExportFolder()
#-------------------------------------------------------------------------------
    def browseExportFolder(self):
        dlg = QFileDialog.getExistingDirectory(self, 'Select a directory', self.txtExportFolder.text())
        if dlg:
            self.txtExportFolder.setText(str(dlg))
            
#-------------------------------------------------------------------------------
# class Project
#-------------------------------------------------------------------------------
class Project():
    name = "*NONE"
    path = ""
    parent = None
    dirtyFlag = True
    files = []
    openFiles = []
    timeNoFocus = 0
    encoding = None
    
#-------------------------------------------------------------------------------
# __init__()
#-------------------------------------------------------------------------------
    def __init__(self, name = const.PROJECT_NONE, parent = None):
        self.name = name
        self.parent = parent
    
#-------------------------------------------------------------------------------
# set()
#-------------------------------------------------------------------------------
    def set(self, name):
        self.name = name

#-------------------------------------------------------------------------------
# open()
#-------------------------------------------------------------------------------
    def open(self, raw=False):
        print("PROJECT %s" % self.name)
        self.parent.showMessage("Opening project %s" % self.name)
        self.path = os.path.join(settings.db['BSIDE_REPOSITORY'], self.name)
        if os.path.exists(self.path):
            self.parent.tvmProject.setRootPath(self.path)        
            self.parent.tvwProject.setRootIndex(self.parent.tvmProject.index(self.path))
            self.parent.tbwHighLeft.setCurrentIndex(1)
            tabEditor = None
            mainFile = None
            if raw == False:
                mainFile = self.getMainModule(self.path)
                tabEditor = self.openFile(mainFile)
                self.parent.txtMainFile.setText(mainFile)
            self.parent.setWindowTitle(self.name + " - " + const.APPLICATION_NAME)
            self.parent.lblProject.setText(self.name)
            if settings.db['PROJECT_DISPLAY_TIME'] == True:
                self.parent.lblProjectName.setText("%s (%s)" % (self.name, self.getTimeProject()))
            else:
                self.parent.lblProjectName.setText("%s" % (self.name))
            self.refreshStatus()        
            self.startSession()
            return True
        else:
            self.parent.showMessage("Can't find project %s" % self.name)
            return False
        # TODO : Read metadata from XML project.bsix file
        # Name (Project = Package)
        # Path
        # Bside version
        # Main module
        # Author
        # Created
        # Modified
        # License
        # Time spent
        # Files
        
        # return (tabEditor, mainFile)
        
#-------------------------------------------------------------------------------
# refreshStatus()
#-------------------------------------------------------------------------------
    def refreshStatus(self):
        self.parent.lblProjectStatus.setText(str(utils.getHumanSize(utils.getDirSize2(self.path))))
        
#-------------------------------------------------------------------------------
# save()
#-------------------------------------------------------------------------------
    def save(self):
        pass

#-------------------------------------------------------------------------------
# close()
#-------------------------------------------------------------------------------
    def close(self):
        self.parent.showMessage("Closing project")
        self.endSession()
        self.parent.project = None
        self.parent.lastProject = None
        
        # close files belonging to the project
        # clear project treeview
        # set focus on repository tab
    
#-------------------------------------------------------------------------------
# openFile()
#-------------------------------------------------------------------------------
    def openFile(self, name, filetype="python"):
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

        if self.parent.isFileOpen(name)[0] == False:
            if filetype == "md":
                tabEditor = editor.WMarkdown(filename=name, parent=self.parent.tbwHighRight, window=self.parent)
            else:
                tabEditor = editor.WEditor(filename=name, parent=self.parent.tbwHighRight, window=self.parent, filetype=filetype)        
            bname = os.path.basename(name)
            self.parent.tbwHighRight.addTab(tabEditor, bname)
            idxTab = self.parent.tbwHighRight.count() - 1
            self.parent.tbwHighRight.setTabIcon(idxTab, QIcon(icon))
            self.parent.tbwHighRight.setCurrentIndex(idxTab)               
            

            # tabEditor.txtEditor.textChanged.connect(lambda x=tabEditor: self.textChange(x))
            self.parent.showMessage("Editing %s" % name)         

            return tabEditor
        else:
            self.parent.showMessage("File %s already open" % name)         
        
#-------------------------------------------------------------------------------
# closeFile()
#-------------------------------------------------------------------------------
    def closeFile(self, name):
        # if file modified, ask to save
        # if file has no name, ask for one
        pass

#-------------------------------------------------------------------------------
# getMainModule()
#-------------------------------------------------------------------------------
    def getMainModule(self, name):
        xmlFile = os.path.join(name, const.PROJECT_FILE_NAME)
        tree = ET.parse(xmlFile)
        root = tree.getroot()
        mainFile = os.path.join(name, root.find('main').text)
        self.encoding = root.find('encoding').text
        return mainFile
    
#-------------------------------------------------------------------------------
# getProperties()
#-------------------------------------------------------------------------------
    def getProperties(self):
        xmlFile = os.path.join(self.path, const.PROJECT_FILE_NAME)
        tree = ET.parse(xmlFile)
        root = tree.getroot()
        props = {}
        props.update({'Project': os.path.basename(os.path.normpath(self.path))})
        props.update({'Main module': root.find('main').text})
        props.update({'Encoding': root.find('encoding').text})
        props.update({'Created' : root.find('created').text})
        props.update({'Last modified' : root.find('modified').text})
        props.update({'BSide version' : root.find('bside').text})
        props.update({'Size' : str(utils.getHumanSize(utils.getDirSize2(self.path)))})
        props.update({'Time spent so far' : self.getTimeProject()})
        return props
    
#-------------------------------------------------------------------------------
# exportProject()
#-------------------------------------------------------------------------------
    def exportProject(self):
        dialog = DlgExportProject(self.path, self.parent)
        result = dialog.exec()
        if result == QDialog.Accepted:
            archiveName = os.path.join(dialog.txtExportFolder.text(), self.name + time.strftime("_%Y%m%d-%H%M%S.zip"))
            self.parent.showMessage("Exporting project %s to %s" % (self.name, archiveName))
            backup.zipDir(self.path, archiveName)
        else:
            self.parent.showMessage("Export cancelled")

#-------------------------------------------------------------------------------
# promoteProject()
#-------------------------------------------------------------------------------
    def promoteProject(self, folder):
        dialog = DlgPromoteProject(folder, self.parent)
        result = dialog.exec()
        if result == QDialog.Accepted:
            dirProject = dialog.txtProjectFolder.text()
            # Package folder
            package = dirProject
            print("PACKAGE=%s" % package)

            # Main module file
            module = dialog.cbxModuleName.currentText()

            # README.md
            if not os.path.isfile(os.path.join(package, "README.md")):
                readme = self.getReadme(
                    dialog.txtProjectName.text(), 
                    dialog.txtAuthorName.text(),
                    dialog.txtAuthorMail.text(),
                    dialog.txtAuthorSite.text(),
                    dialog.txtCompany.text(),
                    dialog.cbxLicense.currentText()                                        
                )
                utils.copyStringToFile(readme, os.path.join(package, "README.md"))

            # LICENSE.md
            if not os.path.isfile(os.path.join(package, "LICENSE.md")):
                license = 'resources/templates/licenses/' + dialog.cbxLicense.currentText() + ".md"
                utils.copyFile(pkg_resources.resource_filename(__name__, license), os.path.join(package, "LICENSE.md"))

            # update members
            self.name = os.path.basename(os.path.normpath(dirProject))
            self.path = package

            # Encoding
            encoding = dialog.cbxEncoding.currentText()

            # Project file
            self.createXMLProjectFile(module, encoding)

            # Open project
            self.open()

            return True
        else:
            return False        
    
#-------------------------------------------------------------------------------
# createNew()
#-------------------------------------------------------------------------------
    def createNew(self):
        dialog = DlgNewProject(self.parent)
        result = dialog.exec()
        if result == QDialog.Accepted:
            dirProject = dialog.txtProjectName.text()
            if dirProject != "":
                ok = utils.createDirectory(settings.db['BSIDE_REPOSITORY'], dirProject)
                if ok == True:
                    # Package folder
                    package = os.path.join(settings.db['BSIDE_REPOSITORY'], dirProject)

                    # Main module file
                    module = dialog.txtModuleName.text()

                    # Python files
                    templateFolder = pkg_resources.resource_filename(__name__, 'resources/templates/newfiles/python/' + dialog.cbxTemplate.currentText())
                    utils.copyAllFilesFromTo(templateFolder, package)
                    if module != "main.py":
                        os.rename(os.path.join(package, "main.py"), os.path.join(package, module))
                    utils.createFile(package, "__init__.py")

                    # README.md
                    readme = self.getReadme(
                        dialog.txtProjectName.text(), 
                        dialog.txtAuthorName.text(),
                        dialog.txtAuthorMail.text(),
                        dialog.txtAuthorSite.text(),
                        dialog.txtCompany.text(),
                        dialog.cbxLicense.currentText()                                        
                    )                
                    utils.copyStringToFile(readme, os.path.join(package, "README.md"))

                    # LICENSE.md
                    license = 'resources/templates/licenses/' + dialog.cbxLicense.currentText() + ".md"
                    utils.copyFile(pkg_resources.resource_filename(__name__, license), os.path.join(package, "LICENSE.md"))
                    
                    # Encoding
                    encoding = dialog.cbxEncoding.currentText()
                    
                    # update members
                    self.name = dirProject
                    self.path = package

                    # Project file
                    self.createXMLProjectFile(module, encoding)

                    # Open project
                    self.open()
                    
                    return True
            else:
                return False        
        else:
            return False

#-------------------------------------------------------------------------------
# getReadme()
#-------------------------------------------------------------------------------
    def getReadme(self, title, author, mail, site, company, license):
        readme = 'resources/templates/README.md'
        filein = open(pkg_resources.resource_filename(__name__, readme))
        src = Template(filein.read())
        d={ 'PROJECT_TITLE':title, 
            'PROJECT_AUTHOR':author,
            'PROJECT_MAIL':mail,
            'PROJECT_SITE':site,
            'PROJECT_COMPANY':company,
            'PROJECT_LICENSE':license
        }
        result = src.substitute(d)
        return result

#-------------------------------------------------------------------------------
# createXMLProjectFile()
#-------------------------------------------------------------------------------
    def createXMLProjectFile(self, module, encoding):   
        E = lxml.builder.ElementMaker()
        TagProject = E.project
        TagBSide = E.bside
        TagCreated = E.created
        TagModified = E.modified
        TagMain = E.main
        TagEncoding = E.encoding

        XMLDoc = TagProject(
                    TagBSide(const.VERSION),
                    TagCreated(datetime.now().strftime("%Y/%m/%d-%H:%M:%S")),
                    TagModified(datetime.now().strftime("%Y/%m/%d-%H:%M:%S")),
                    TagMain(module),
                    TagEncoding(encoding),
                    name=self.name
                    )

        projectFull = os.path.join(self.path, const.PROJECT_FILE_NAME)
        with open(projectFull, "w") as projectFile:
            # projectFile.write('<?xml version="1.0" encoding="UTF-8"?>\n')  
            projectFile.write(lxml.etree.tostring(XMLDoc, pretty_print=True).decode("utf-8"))    
            
#-------------------------------------------------------------------------------
# startSession()
#-------------------------------------------------------------------------------
    def startSession(self):
        self.session = datetime.now().strftime("%Y/%m/%d-%H:%M:%S")
            
#-------------------------------------------------------------------------------
# endSession()
#-------------------------------------------------------------------------------
    def endSession(self):
        filename = os.path.join(self.path, const.PROJECT_FILE_NAME)
        parser = lxml.etree.XMLParser(remove_blank_text=True)
        tree = lxml.etree.parse(filename, parser)
        root = tree.getroot()
        # Modify the <modified> tag
        modified = root.find('modified')
        modified.text = datetime.now().strftime("%Y/%m/%d-%H:%M:%S")
        # Targeting <SESSIONS> tag
        sessions = root.find('.//sessions')
        if sessions is None:
            # Creating <SESSIONS> tag if it not exists
            sessions = lxml.etree.SubElement(root, 'sessions')
        # Creating the current <SESSION> tag
        session = lxml.etree.SubElement(sessions, 'session')
        endSession = datetime.now().strftime("%Y/%m/%d-%H:%M:%S")
        session.set("start", self.session)
        session.set("end", endSession)
        d = timedelta(days=0, seconds=0, microseconds=0, milliseconds=0, minutes=0, hours=0, weeks=0)
        d1 = datetime.strptime(self.session, "%Y/%m/%d-%H:%M:%S")
        d2 = datetime.strptime(endSession, "%Y/%m/%d-%H:%M:%S")
        # Sum the full time of sessions
        d = d + (d2 - d1)
        timeFocus = d.total_seconds() - self.timeNoFocus        
        # session.set("focus", str(timedelta(seconds=timeFocus)))
        session.set("focus", str(int(timeFocus)))
        # Appending the <SESSION> tag to the <SESSIONS>
        sessions.insert(root.index(sessions) + 1, session)
        # Writing all
        tree.write(filename, pretty_print=True)

#-------------------------------------------------------------------------------
# getTimeProject()
#-------------------------------------------------------------------------------
    def getTimeProject(self):
        filename = os.path.join(self.path, const.PROJECT_FILE_NAME)
        parser = lxml.etree.XMLParser(remove_blank_text=True)
        tree = lxml.etree.parse(filename, parser)
        sessions = tree.xpath('//project/sessions/session')
        # Create blank timedelta object
        d = timedelta(days=0, seconds=0, microseconds=0, milliseconds=0, minutes=0, hours=0, weeks=0)
        s = 0
        for session in sessions:
            # Compute time of each session
            if settings.db['PROJECT_USE_FOCUS_TIME'] == True:
                s = s + int((session.get('focus')))                
            else:
                d1 = datetime.strptime(session.get('start'), "%Y/%m/%d-%H:%M:%S")
                d2 = datetime.strptime(session.get('end'), "%Y/%m/%d-%H:%M:%S")
                # Sum the full time of sessions
                d = d + (d2 - d1)
        if settings.db['PROJECT_USE_FOCUS_TIME'] == True:
            return(str(timedelta(seconds=s)))
        else:
            return(str(d))
                        
#-------------------------------------------------------------------------------
# newModule()
#-------------------------------------------------------------------------------
    def newModule(self):
        dlg = dialog.DlgNewObject(self.name, self.path, "module", "new.py", self.parent)
        result = dlg.exec()
        if result == QDialog.Accepted:
            self.parent.showMessage("Create module %s" % dlg.rname)    
            if not os.path.isfile(dlg.rname):
                module = "resources/templates/newfiles/new.py"
                utils.copyFile(pkg_resources.resource_filename(__name__, module), dlg.rname)            
                self.parent.showMessage("New module %s created" % dlg.rname)
            else:
                self.parent.showMessage("Module %s already exists" % dlg.rname)
            self.openFile(dlg.rname, "python")
        
#-------------------------------------------------------------------------------
# newXMLFile()
#-------------------------------------------------------------------------------
    def newXMLFile(self):
        dlg = dialog.DlgNewObject(self.name, self.path, "XML file", "new.xml", self.parent)
        result = dlg.exec()
        if result == QDialog.Accepted:
            self.parent.showMessage("Create XML %s" % dlg.rname)            
            if not os.path.isfile(dlg.rname):
                xml = "resources/templates/newfiles/new.xml"
                utils.copyFile(pkg_resources.resource_filename(__name__, xml), dlg.rname)            
                self.parent.showMessage("New XML %s created" % dlg.rname)
            else:
                self.parent.showMessage("XML %s already exists" % dlg.rname)
            self.openFile(dlg.rname, "xml")
        
#-------------------------------------------------------------------------------
# newHTMLFile()
#-------------------------------------------------------------------------------
    def newHTMLFile(self):
        dlg = dialog.DlgNewObject(self.name, self.path, "HTML file", "new.html", self.parent)
        result = dlg.exec()
        if result == QDialog.Accepted:
            self.parent.showMessage("Create HTML %s" % dlg.rname)            
            if not os.path.isfile(dlg.rname):
                html = "resources/templates/newfiles/new.html"
                utils.copyFile(pkg_resources.resource_filename(__name__, html), dlg.rname)            
                self.parent.showMessage("New HTML %s created" % dlg.rname)
            else:
                self.parent.showMessage("HTML %s already exists" % dlg.rname)
            self.openFile(dlg.rname, "html")

#-------------------------------------------------------------------------------
# newMDFile()
#-------------------------------------------------------------------------------
    def newMDFile(self):
        dlg = dialog.DlgNewObject(self.name, self.path, "MarkDown file", "new.md", self.parent)
        result = dlg.exec()
        if result == QDialog.Accepted:
            self.parent.showMessage("Create Markdown %s" % dlg.rname)            
            if not os.path.isfile(dlg.rname):
                md = "resources/templates/newfiles/new.md"
                utils.copyFile(pkg_resources.resource_filename(__name__, md), dlg.rname)            
                self.parent.showMessage("New Markdown %s created" % dlg.rname)
            else:
                self.parent.showMessage("Markdown %s already exists" % dlg.rname)
            self.openFile(dlg.rname, "md")
        
#-------------------------------------------------------------------------------
# newQtUIFile()
#-------------------------------------------------------------------------------
    def newQtUIFile(self):
        dlg = dialog.DlgNewObject(self.name, self.path, "Qt UI file", "new.ui", self.parent)
        result = dlg.exec()
        if result == QDialog.Accepted:
            self.parent.showMessage("Create UI %s" % dlg.rname)            
            if not os.path.isfile(dlg.rname):
                ui = "resources/templates/newfiles/new.ui"
                utils.copyFile(pkg_resources.resource_filename(__name__, ui), dlg.rname)            
                self.parent.showMessage("New Qt UI %s created" % dlg.rname)
            else:
                self.parent.showMessage("Qt UI %s already exists" % dlg.rname)
            self.openFile(dlg.rname, "xml")
        
#-------------------------------------------------------------------------------
# newSQLFile()
#-------------------------------------------------------------------------------
    def newSQLFile(self):
        dlg = dialog.DlgNewObject(self.name, self.path, "SQL file", "new.sql", self.parent)
        result = dlg.exec()
        if result == QDialog.Accepted:
            self.parent.showMessage("Create SQL %s" % dlg.rname)            
            if not os.path.isfile(dlg.rname):
                sql = "resources/templates/newfiles/new.sql"
                utils.copyFile(pkg_resources.resource_filename(__name__, sql), dlg.rname)            
                self.parent.showMessage("New SQL %s created" % dlg.rname)
            else:
                self.parent.showMessage("SQL %s already exists" % dlg.rname)
            self.openFile(dlg.rname, "sql")
        
#-------------------------------------------------------------------------------
# newFile()
#-------------------------------------------------------------------------------
    def newFile(self):
        dlg = dialog.DlgNewObject(self.name, self.path, "file", "newfile", self.parent)
        result = dlg.exec()
        if result == QDialog.Accepted:
            self.parent.showMessage("Create file %s" % dlg.rname)            
            if utils.createFile(os.path.dirname(dlg.rname), os.path.basename(dlg.rname)):                
                self.parent.showMessage("New file %s created" % dlg.rname)
                self.openFile(dlg.rname, "text")
            else:
                self.parent.showMessage("Can't create %s" % dlg.rname)
        
#-------------------------------------------------------------------------------
# newFolder()
#-------------------------------------------------------------------------------
    def newFolder(self):
        dlg = dialog.DlgNewObject(self.name, self.path, "folder", "newfolder", self.parent)
        result = dlg.exec()
        if result == QDialog.Accepted:
            self.parent.showMessage("Create folder %s" % dlg.rname)            
            if utils.createDirectory(os.path.dirname(dlg.rname), os.path.basename(dlg.rname)):                
                self.parent.showMessage("New folder %s created" % dlg.rname)
            else:
                self.parent.showMessage("Can't create %s" % dlg.rname)
        

"""
RW File Name
RO Project
RW Folder       [Browse]
RO Created File

"""
