from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import subprocess
import shutil
import os
import sys
import time
from subprocess import Popen, PIPE

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
    
    mw.lblAddData.mousePressEvent = lambda event, widget=mw.lstAddData : doClickForAddSRCDST(event, widget)
    mw.lblAddBinary.mousePressEvent = lambda event, widget=mw.lstAddBinary : doClickForAddSRCDST(event, widget)
   
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
def doClickForAddSRCDST(event, widget):
    dlg = dialog.DlgAddData(widget)
    dlg.exec()


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
    
    
    command_line = 'pyinstaller {}{} {}{}{}{}{}{}{}{}{}{}'.format(\
    gen_option,\
    source_file,\
    workpath_option,\
    dispath_option,\
    specpath_option,\
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
    filename = QFileDialog.getOpenFileName(mw, 'Open main file', '', 'Python sources (*.py);;All files (*.*)', options = QFileDialog.DontUseNativeDialog)[0]
    if filename != None:
        mw.txtMainFile.setText(filename)

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
    mw.btnBuildEXE.setEnabled(False)
    mw.lblLEDBuild.setPixmap(QPixmap("pix/icons/led_red.png"))
    mw.repaint()
    mw.txtBuildOutput.appendPlainText(settings.db['SHELL_PROMPT'] + " " + command + "\n")
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
                mw.txtBuildOutput.appendPlainText("%s " % line[1:].rstrip())
            else:
                mw.txtBuildOutput.appendPlainText("[OUT] %s " % line[1:].rstrip())
        elif line[0] == '2':
            if mode == MODE_BUILD:
                mw.txtBuildOutput.appendPlainText("%s " % line[1:].rstrip())
            else:
                mw.txtBuildOutput.appendPlainText("[ERR] %s " % line[1:].rstrip())
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
    mw.txtBuildOutput.appendPlainText("")
    mw.txtBuildOutput.appendPlainText("End of         : %s" % str(tCmd.cmd))
    mw.txtBuildOutput.appendPlainText("Running PID    : %s" % str(tCmd.process.pid))
    mw.txtBuildOutput.appendPlainText("Return Code    : %d" % tCmd.returncode)
    time2 = time.time()
    elapsed = (time2 - time1)*1000.0
    mw.lblTimeBuild.setText("{:.3f} ms".format(elapsed))

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
            mw.txtBuildOutput.appendPlainText("")
            mw.txtBuildOutput.appendPlainText("Executable file info")
            mw.txtBuildOutput.appendPlainText("====================")
            for key, value in fInfo.items():
                mw.txtBuildOutput.appendPlainText("{}\t{}".format(key, value))
            mw.txtBuildOutput.appendPlainText("")
            mw.lblRunEXE.setText(name_EXE)
            mw.showMessage("Build completed successfully")
        else:
            mw.txtBuildOutput.appendPlainText("")
            mw.txtBuildOutput.appendPlainText("!!! BUILD FAILED !!!")
            mw.txtBuildOutput.appendPlainText("Retry with checking first the upper right \"Clean\" option.")
            mw.txtBuildOutput.appendPlainText("")
            mw.btnRunEXE.setEnabled(False)
            mw.lblRunEXE.setText("-")   
            mw.showMessage("Build failed")
    else:
        mw.btnRunEXE.setEnabled(True)
        mw.showMessage("End of runnning builded executable with return code %d" % tCmd.returncode)

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
    
"""
                    cmd = (pybin, "-u", script, dlg.params)
                    self.btnKillProcess.setEnabled(True)
                    self.tbwLowRight.setCurrentIndex(0)
                    QGuiApplication.processEvents()                     
                    # self.tCmd = shrealding.Shreald(self, "%s -u %s" % (pybin, script))
                    self.tCmd = shrealding.Shreald(self, cmd, os.path.dirname(script))
                    self.tCmd.linePrinted.connect(self.handleLine)                    
            else:
                self.showMessage("Cancel running script %s" % script)   

#-------------------------------------------------------------------------------
# handleLine()
#-------------------------------------------------------------------------------
    def handleLine(self, line):
        if line !=  "":
            # print("Handle %s" % line)
            if line[0] == '1':
                self.showMessage("[OUT] %s " % line[1:].rstrip())
            elif line[0] == '2':
                self.showMessage("[ERR] %s " % line[1:].rstrip())
            elif line[0] == 'x':
                self.killProcess()
            
#-------------------------------------------------------------------------------
# killProcess()
#-------------------------------------------------------------------------------
    def killProcess(self):        
        self.showMessage("Killing application PID %s" % str(self.tCmd.process.pid))
        self.showMessage("End of script %s" % str(self.tCmd.cmd[2]))
        try:
            self.tCmd.kill()
        except:
            pass
        self.btnKillProcess.setEnabled(False)
        self.showMessage("Return Code : %d" % self.tCmd.returncode)
        self.showMessage("=" * 80)                        
        

"""        