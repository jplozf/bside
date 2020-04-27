from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import sqlite3
import os

import settings

#-------------------------------------------------------------------------------
# initFormSQL()
#-------------------------------------------------------------------------------
def initFormSQL(mw):
    mw.SQLDatabase = ":memory:"
    mw.lblSQLDatabase.setText(mw.SQLDatabase)
    mw.btnSQLDatabaseClose.setEnabled(False)
    mw.btnSQLDatabaseClose.clicked.connect(lambda _, mw=mw : closeDatabase(mw))
    mw.btnSQLDatabaseBrowse.clicked.connect(lambda _, mw=mw : browseDatabase(mw))
    mw.btnSQLRun.clicked.connect(lambda _, mw=mw : runSQL(mw))
    mw.txtSQLInput.setText("")

    css = 'font: %dpt "%s"; background-color: %s; color: %s;' % (settings.db['SQLITE3_FONT_SIZE'],settings.db['SQLITE3_FONT'],settings.db['SQLITE3_COLOR_BACKGROUND'],settings.db['SQLITE3_COLOR_FOREGROUND'])        
    mw.txtSQLOutput.setStyleSheet(css)
    mw.txtSQLOutput.setReadOnly(True)
    mw.txtSQLOutput.setPlainText("SQLite3 version %s\n" % sqlite3.sqlite_version)
   
#-------------------------------------------------------------------------------
# browseDatabase()
#-------------------------------------------------------------------------------
def browseDatabase(mw):
    filename = QFileDialog.getOpenFileName(mw, 'Open database', '', 'SQLite database (*.db);;All files (*.*)', options = QFileDialog.DontUseNativeDialog)[0]
    if filename != None:
        mw.SQLDatabase = filename
        mw.lblSQLDatabase.setText(os.path.splitext(os.path.basename(filename))[0])
        mw.btnSQLDatabaseClose.setEnabled(True)
        mw.dbSQLDatabase = sqlite3.connect(mw.SQLDatabase)
        mw.curSQLDatabase = mw.dbSQLDatabase.cursor()

#-------------------------------------------------------------------------------
# closeDatabase()
#-------------------------------------------------------------------------------
def closeDatabase(mw):
    mw.dbSQLDatabase.commit()
    mw.dbSQLDatabase.close()
    mw.SQLDatabase = ":memory:"
    mw.lblSQLDatabase.setText(mw.SQLDatabase)
    mw.btnSQLDatabaseClose.setEnabled(False)
    mw.dbSQLDatabase = sqlite3.connect(mw.SQLDatabase)
    mw.curSQLDatabase = mw.dbSQLDatabase.cursor()

#-------------------------------------------------------------------------------
# runSQL()
#-------------------------------------------------------------------------------
def runSQL(mw):
    cmd = mw.txtSQLInput.text().strip()
    try:
        mw.txtSQLOutput.appendPlainText("%s%s" % (settings.db['SQLITE3_PROMPT'], cmd))
        mw.curSQLDatabase.execute(cmd)
        
        if cmd.lstrip().upper().startswith("SELECT"):
            rows = mw.curSQLDatabase.fetchall()
            for row in rows:
                out = ""
                for field in row:
                    out = out + str(field) + " "
                mw.txtSQLOutput.appendPlainText(out)
    except sqlite3.Error as e:
        mw.txtSQLOutput.appendPlainText("An error occurred : %s" % str(e.args[0]))
       
