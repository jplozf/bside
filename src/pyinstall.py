#!/usr/bin/env python
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
import subprocess
import shutil
import os
import sys
import time
import datetime
from subprocess import Popen, PIPE
from importlib import util
import tempfile
from os.path import splitext

import settings
import utils
import dialog
import shrealding

MODE_RUN = 0
MODE_BUILD = 1

#-------------------------------------------------------------------------------
# initFormEXE()
#-------------------------------------------------------------------------------
def initFormEXE(mw):
    mw.cbxLogLevel.addItem("TRACE")
    mw.cbxLogLevel.addItem("DEBUG")
    mw.cbxLogLevel.addItem("INFO")
    mw.cbxLogLevel.addItem("WARN")
    mw.cbxLogLevel.addItem("ERROR")
    mw.cbxLogLevel.addItem("CRITICAL")
    mw.cbxLogLevel.setCurrentIndex(2)       # INFO default
    
    mw.chkOneDir.setChecked(True)
    
    mw.cbxDebug.addItem("none")
    mw.cbxDebug.addItem("all")
    mw.cbxDebug.addItem("imports")
    mw.cbxDebug.addItem("bootloader")
    mw.cbxDebug.addItem("noarchive")
    mw.cbxDebug.addItem("imports, bootloader")
    mw.cbxDebug.addItem("imports, noarchive")
    mw.cbxDebug.addItem("bootloader, noarchive")
    mw.cbxDebug.setCurrentIndex(0)          # NONE default
    
    mw.lblDistPath.mousePressEvent = lambda event, widget=mw.txtDistPath : doClickForPath(event, widget)
    mw.lblWorkPath.mousePressEvent = lambda event, widget=mw.txtWorkPath : doClickForPath(event, widget)
    mw.lblUPXDir.mousePressEvent = lambda event, widget=mw.txtUPXDir : doClickForPath(event, widget)
    mw.lblSpecPath.mousePressEvent = lambda event, widget=mw.txtSpecPath : doClickForPath(event, widget)
    
    mw.lblAddData.mousePressEvent = lambda event, mw=mw : doClickForAddSRCDST(event, mw)
    mw.lblAddBinary.mousePressEvent = lambda event, mw=mw : doClickForAddSRCDST(event, mw)
       
#-------------------------------------------------------------------------------
# doClickForPath()
#-------------------------------------------------------------------------------
def doClickForPath(event, widget):   
    path = QFileDialog.getExistingDirectory(widget, "Open a folder", ".", options = QFileDialog.DontUseNativeDialog | QFileDialog.ShowDirsOnly)
    if path:
        widget.setText(path)

#-------------------------------------------------------------------------------
# doClickForAddSRCDST()
#-------------------------------------------------------------------------------
def doClickForAddSRCDST(event, mw):
    dlg = dialog.DlgAddData(mw)
    result = dlg.exec()
    if result == QDialog.Accepted:
        src = dlg.txtDataSource.text()
        dst = dlg.txtDataDest.text()
        mw.lstAddData.addItem("%s%s%s" % (src, os.pathsep, dst))
        
#-------------------------------------------------------------------------------
# getAddDataOption()
#-------------------------------------------------------------------------------
def getAddDataOption(mw):
    rc = ""
    for i in range(mw.lstAddData.count()):
        rc = rc + '--add-data="%s" ' % str(mw.lstAddData.item(i).text())
    return rc

#-------------------------------------------------------------------------------
# buildEXE()
#-------------------------------------------------------------------------------
def buildEXE(mw):    
    mw.btnRunEXE.setEnabled(False)
    source_file = mw.txtMainFile.text()
    if source_file == "":
        mw.showMessage("Nothing to build")
        return

    if not os.path.isabs(source_file):
        source_file = os.path.join(os.path.abspath('.'), source_file)
    source_path = os.path.split(source_file)[0]
    name_base = mw.txtName.text() if mw.txtName.text() else os.path.splitext(os.path.basename(source_file))[0]
    
    dist_path = mw.txtDistPath.text() if mw.txtDistPath.text() else os.path.join(source_path, "dist")
    work_path = mw.txtWorkPath.text() if mw.txtWorkPath.text() else os.path.join(source_path, "build")

    if not os.path.isabs(dist_path):
        dist_path = os.path.join(source_path, dist_path)
        # source_file = os.path.join(source_file, dist_path)

    if not os.path.isabs(work_path):
        work_path = os.path.join(source_path, work_path)
    
    if mw.chkOneDir.isChecked():
        dist_path = os.path.join(dist_path, name_base)
    
    global name_EXE
    name_EXE = os.path.join(dist_path, name_base)
    
    if mw.CurrentOS == "Windows":
        name_EXE = name_EXE + ".exe" if name_EXE[-3:].lower() != ".exe" else name_EXE
                
    if mw.chkCleanBeforeBuild.isChecked():
        utils.deleteFolder(dist_path)
        utils.deleteFolder(work_path)
        
    command_line = buildCommand(mw)    
    mw.showMessage("Building with %s" % command_line)
    mw.tbwBuild.setCurrentIndex(0)
    runCommand(command_line, source_path, mw, MODE_BUILD)
    mw.project.refreshStatus()

#-------------------------------------------------------------------------------
# isEXE()
#-------------------------------------------------------------------------------
def isEXE(fpath):
      return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

#-------------------------------------------------------------------------------
# getEXE()
#-------------------------------------------------------------------------------
def getEXE(fpath):
    aEXE = []
    for r, d, f in os.walk(fpath):
        for file in f:
            if isEXE(os.path.join(r, file)):
                aEXE.append(os.path.join(r, file))
    print(aEXE)
    return aEXE
                
#-------------------------------------------------------------------------------
# buildCommand()
#-------------------------------------------------------------------------------
def buildCommand(mw):
    source_file = mw.txtMainFile.text()
    if source_file == "":
        mw.showMessage("Nothing to build")
        return
    gen_option = '-D ' if mw.chkOneDir.isChecked() else '-F '
    workpath_option = '--workpath "{}" '.format(mw.txtWorkPath.text()) if mw.txtWorkPath.text() else ''
    dispath_option = '--distpath "{}" '.format(mw.txtDistPath.text()) if mw.txtDistPath.text() else ''
    specpath_option = '--specpath "{}" '.format(mw.txtSpecPath.text()) if mw.txtSpecPath.text() else ''
    upxdir_option = '--upx-dir "{}" '.format(mw.txtUPXDir.text()) if mw.txtUPXDir.text() else ''
    ascii_option = '--ascii ' if mw.chkAscii.isChecked() else ''
    clean_option = '--clean ' if mw.chkClean.isChecked() else ''
    name_option = '--name {} '.format(mw.txtName.text()) if mw.txtName.text() else ''
    key_option = '--key {} '.format(mw.txtKeyBuild.text()) if mw.txtKeyBuild.text() else ''   
    strip_option = '--strip ' if mw.chkStrip.isChecked() else ''
    noupx_option = '--noupx ' if mw.chkNoUPX.isChecked() else ''
    adddata_option = getAddDataOption(mw)
    
    
    command_line = 'pyinstaller {}{} {}{}{}{}{}{}{}{}{}{}{}'.format(\
    gen_option,\
    source_file,\
    workpath_option,\
    dispath_option,\
    specpath_option,\
    adddata_option,\
    name_option,\
    upxdir_option,\
    ascii_option,\
    clean_option,\
    key_option,\
    strip_option,\
    noupx_option\
    )
    print(command_line)
    return command_line

#-------------------------------------------------------------------------------
# browseMainFile()
#-------------------------------------------------------------------------------
def browseMainFile(mw):
    filename = QFileDialog.getOpenFileName(mw, 'Open main file', '', 'Specification files (*.spec);;Python sources (*.py);;All files (*.*)', options = QFileDialog.DontUseNativeDialog)[0]
    if filename != None:
        mw.txtMainFile.setText(filename)
        _, extension = splitext(filename)
        if extension == ".spec":
            # readSpecFile(filename)
            pass

#-------------------------------------------------------------------------------
# runEXE()
#-------------------------------------------------------------------------------
def runEXE(mw):
    try:
        source_path = os.path.split(mw.lblRunEXE.text())[0]
        mw.tbwBuild.setCurrentIndex(0)
        rc = runCommand("{} {}".format(mw.lblRunEXE.text(), mw.txtParamsEXE.text()), source_path, mw, MODE_RUN)
    except:
        mw.btnBuildEXE.setEnabled(True)
        mw.lblLEDBuild.setPixmap(QPixmap("pix/icons/led_green.png"))
        mw.showMessage("Can't run this")

#-------------------------------------------------------------------------------
# runCommand2()
#-------------------------------------------------------------------------------
def runCommand2(command, cwd, mw):        
    mw.btnBuildEXE.setEnabled(False)
    mw.lblLEDBuild.setPixmap(QPixmap("pix/icons/led_red.png"))
    mw.repaint()
    mw.txtBuildOutput.appendPlainText(settings.db['SHELL_PROMPT'] + " " + command + "\n")
    time1 = time.time()
    # p = Popen(command, stdin=PIPE, stdout=PIPE, stderr=PIPE, bufsize=1, universal_newlines=True, shell = True)
    p = Popen(command, cwd=cwd, stdin=PIPE, stdout=PIPE, stderr=PIPE, bufsize=1, shell = True)
    p.poll()
    while True:
        line = p.stdout.readline()
        if mw.CurrentOS == "Windows":
            sLine = line.decode(settings.db['SHELL_CODEPAGE']).rstrip()
            oLine = patchChars(sLine)
            mw.txtBuildOutput.appendPlainText(oLine)
        else:
            mw.txtBuildOutput.appendPlainText(line.decode(settings.db['SHELL_CODEPAGE']).rstrip())
        mw.repaint()
        if not line and p.poll is not None: 
            break

    while True:
        err = p.stderr.readline()
        if mw.CurrentOS == "Windows":
            sLine = err.decode(settings.db['SHELL_CODEPAGE']).rstrip()
            oLine = patchChars(sLine)
            mw.txtBuildOutput.appendPlainText(oLine)
        else:
            mw.txtBuildOutput.appendPlainText(err.decode(settings.db['SHELL_CODEPAGE']).rstrip())
        mw.repaint()
        if not err and p.poll is not None: 
            break

    mw.txtBuildOutput.moveCursor(QTextCursor.End)
    rc = p.poll()
    mw.lblRCBuild.setText("RC=" + str(rc))
    """
    if rc != 0:
        mw.lblRCBuild.setStyleSheet('background-color : red; color: white')
    else:
        mw.lblRCBuild.setStyleSheet('background-color:' + self.colLabel.name() + '; color: black')
    """
    time2 = time.time()
    elapsed = (time2-time1)*1000.0
    mw.lblTimeBuild.setText("{:.3f} ms".format(elapsed))
    mw.btnBuildEXE.setEnabled(True)
    mw.lblLEDBuild.setPixmap(QPixmap("pix/icons/led_green.png"))
    
    return(rc)

#-------------------------------------------------------------------------------
# runCommand()
#-------------------------------------------------------------------------------
def runCommand(command, cwd, mw, typeRun):    
    global mode
    mode = typeRun
    
    mw.setCursor(Qt.WaitCursor)
    mw.btnBuildEXE.setEnabled(False)
    mw.lblLEDBuild.setPixmap(QPixmap("pix/icons/led_red.png"))
    mw.repaint()
    mw.txtBuildOutput.appendPlainText("%s%s %s" % (nowPrompt(),settings.db['SHELL_PROMPT'], command))
    global time1
    time1 = time.time()
    mw.btnBreakEXE.setEnabled(True)
    mw.tbwBuild.setCurrentIndex(0)
    QGuiApplication.processEvents()  
    global tCmd
    tCmd = shrealding.Shreald(mw, command, cwd, shell=True)
    tCmd.linePrinted.connect(lambda line, mw=mw: handleLine(line, mw))
    mw.lblTimeBuild.setText("---")

#-------------------------------------------------------------------------------
# handleLine()
#-------------------------------------------------------------------------------
def handleLine(line, mw):
    global mode
    if line !=  "":
        if line[0] == '1':
            if mode == MODE_BUILD:
                mw.txtBuildOutput.appendPlainText("%s%s" % (nowPrompt(), line[1:].rstrip()))
            else:
                mw.txtBuildOutput.appendPlainText("%s[OUT] %s" % (nowPrompt(), line[1:].rstrip()))
        elif line[0] == '2':
            if mode == MODE_BUILD:
                mw.txtBuildOutput.appendPlainText("%s%s" % (nowPrompt(), line[1:].rstrip()))
            else:
                mw.txtBuildOutput.appendPlainText("%s[ERR] %s" % (nowPrompt(), line[1:].rstrip()))
        elif line[0] == 'x':
            killProcess(mw)

#-------------------------------------------------------------------------------
# killProcess()
#-------------------------------------------------------------------------------
def killProcess(mw):  
    global tCmd
    try:
        tCmd.kill()
    except:
        pass        
    finalizeCommand(mw)

#-------------------------------------------------------------------------------
# finalizeCommand()
#-------------------------------------------------------------------------------
def finalizeCommand(mw):
    global tCmd
    global time1
    mw.txtBuildOutput.appendPlainText("%s" % nowPrompt())
    mw.txtBuildOutput.appendPlainText("%sEnd of         : %s" % (nowPrompt(), str(tCmd.cmd)))
    mw.txtBuildOutput.appendPlainText("%sRunning PID    : %s" % (nowPrompt(), str(tCmd.process.pid)))
    mw.txtBuildOutput.appendPlainText("%sReturn Code    : %d" % (nowPrompt(), tCmd.returncode))
    time2 = time.time()
    elapsed = time2 - time1
    mw.lblTimeBuild.setText(utils.getHumanTime(elapsed))

    mw.lblLEDBuild.setPixmap(QPixmap("pix/icons/led_green.png"))
    mw.lblRCBuild.setText("RC=%d" % tCmd.returncode)
    mw.btnBreakEXE.setEnabled(False)
    mw.btnBuildEXE.setEnabled(True)
    
    global name_EXE
    global mode
    
    if mode == MODE_BUILD:
        if tCmd.returncode == 0:
            mw.btnRunEXE.setEnabled(True)
            # aEXE = getEXE(os.path.join(source_path,"dist"))
            fInfo = utils.getFileInfo(name_EXE)
            mw.txtBuildOutput.appendPlainText("%s" % nowPrompt())
            mw.txtBuildOutput.appendPlainText("%sExecutable file info" % nowPrompt())
            mw.txtBuildOutput.appendPlainText("%s====================" % nowPrompt())
            for key, value in fInfo.items():
                mw.txtBuildOutput.appendPlainText("{}{}\t{}".format(nowPrompt(), key, value))
            mw.txtBuildOutput.appendPlainText("%s" % nowPrompt())
            mw.lblRunEXE.setText(name_EXE)
            mw.showMessage("Build completed successfully")
        else:
            mw.txtBuildOutput.appendPlainText("%s" % nowPrompt())
            mw.txtBuildOutput.appendPlainText("%s!!! BUILD FAILED !!!" % nowPrompt())
            mw.txtBuildOutput.appendPlainText("%sRetry with checking first the upper right \"Clean\" option." % nowPrompt())
            mw.txtBuildOutput.appendPlainText("%s" % nowPrompt())
            mw.btnRunEXE.setEnabled(False)
            mw.lblRunEXE.setText("-")   
            mw.showMessage("Build failed")
        mw.project.refreshStatus()
    else:
        mw.btnRunEXE.setEnabled(True)
        mw.showMessage("End of runnning builded executable with return code %d" % tCmd.returncode)
    mw.setCursor(Qt.ArrowCursor)

#-------------------------------------------------------------------------------
# nowPrompt()
#-------------------------------------------------------------------------------
def nowPrompt():
    now = datetime.datetime.now()
    return now.strftime(settings.db['OUTPUT_TIMESTAMP'])

#-------------------------------------------------------------------------------
# patchChars()
#-------------------------------------------------------------------------------
def patchChars(s):
    myChars = {'“':'ô', 'Š':'ê', '‚':'é', 'ÿ':''}
    foo = s.split()
    ret = []
    for item in foo:
        ret.append(myChars.get(item, item)) # Try to get from dict, otherwise keep value
    return(" ".join(ret))

#-------------------------------------------------------------------------------
# loadPythonFile()
#-------------------------------------------------------------------------------
def loadPythonFile(name, path):
    spec = util.spec_from_file_location(name, path)
    module = util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module
    
#-------------------------------------------------------------------------------
# readSpecFile()
#-------------------------------------------------------------------------------
def readSpecFile(specfile):
    pyfile = shutil.copy(specfile, os.path.join(tempfile.gettempdir(),"spec.py"))
    specmodule = loadPythonFile("spec", pyfile)
    print(specmodule.a.datas)
    