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
import dis
import types
from io import StringIO

#-------------------------------------------------------------------------------
# initFormDisass()
#-------------------------------------------------------------------------------
def initFormDisass(mw):
    mw.btnDisassemble.clicked.connect(lambda : disassembleFile(mw))
    mw.btnBrowseSourceFile.clicked.connect(lambda: browseSourceFile(mw))
    mw.btnCopyDis.clicked.connect(lambda: copyDisToClipboard(mw))

#-------------------------------------------------------------------------------
# browseSourceFile()
#-------------------------------------------------------------------------------
def browseSourceFile(mw):
    filename = QFileDialog.getOpenFileName(mw, 'Open source file', '', 'Python sources (*.py);;Python compiled (*.pyc)', options = QFileDialog.DontUseNativeDialog)[0]
    if filename != None:
        mw.txtSourceFile.setText(filename)

#-------------------------------------------------------------------------------
# copyNameToClipboard()
#-------------------------------------------------------------------------------
def copyDisToClipboard(mw):
    QApplication.clipboard().setText(mw.txtDisassembled.toPlainText())
    mw.showMessage("Copy disassembled source to clipboard")

#-------------------------------------------------------------------------------
# disassembleFile()
#-------------------------------------------------------------------------------
def disassembleFile(mw, filename=None):
    if filename == None:
        filename = mw.txtSourceFile.text()

    if filename != "":
        # https://stackoverflow.com/questions/32562163/how-can-i-understand-a-pyc-file-content
        with open(filename) as f_source:
            source_code = f_source.read()

        with StringIO() as out:
            try:
                byte_code = compile(source_code, filename, "exec")
                dis.dis(byte_code, file=out)
                mw.txtDisassembled.setText(out.getvalue())

                for x in byte_code.co_consts:
                    if isinstance(x, types.CodeType):
                        sub_byte_code = x
                        func_name = sub_byte_code.co_name
                        mw.txtDisassembled.append('\nDisassembly of %s:' % func_name)
                        dis.dis(sub_byte_code, file=out)
                        mw.txtDisassembled.append(out.getvalue())
            except:
                mw.showMessage("Can't disassemble this")
