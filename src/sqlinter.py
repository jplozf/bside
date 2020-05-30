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
    mw.btnSQLCopy.clicked.connect(lambda _, mw=mw : copyClipboard(mw))
    mw.btnSQLRun.clicked.connect(lambda _, mw=mw : runSQL(mw))
    mw.txtSQLInput.returnPressed.connect(lambda mw=mw : runSQL(mw))
    mw.txtSQLInput.installEventFilter(mw) # The eventFilter which is into mainwindow.py
    mw.txtSQLInput.setText("")

    css1 = 'font: %dpt "%s"; background-color: %s; color: %s;' % (settings.db['SQLITE3_FONT_SIZE'],settings.db['SQLITE3_FONT'],settings.db['SQLITE3_COLOR_BACKGROUND'],settings.db['SQLITE3_COLOR_FOREGROUND'])        
    css2 = 'font: %dpt "%s";' % (settings.db['SQLITE3_FONT_SIZE'],settings.db['SQLITE3_FONT'])        
    mw.txtSQLOutput.setStyleSheet(css1)
    mw.txtSQLInput.setStyleSheet(css2)
    mw.txtSQLOutput.setReadOnly(True)
    mw.txtSQLOutput.setPlainText("SQLite3 version %s\n" % sqlite3.sqlite_version)
   
#-------------------------------------------------------------------------------
# browseDatabase()
#-------------------------------------------------------------------------------
def browseDatabase(mw):
    filename = QFileDialog.getSaveFileName(mw, 'Open database', '', 'SQLite database (*.db);;All files (*.*)', options = QFileDialog.DontUseNativeDialog | QFileDialog.DontConfirmOverwrite)[0]
    if filename:
        mw.SQLDatabase = filename
        mw.lblSQLDatabase.setText(os.path.basename(filename))
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
    mw.aSQL.append(cmd)
    mw.iSQL = mw.iSQL + 1        
    
    try:
        mw.txtSQLOutput.append("<br>%s<b>%s</b>" % (settings.db['SQLITE3_PROMPT'], cmd))
        if cmd.startswith("."):
            if cmd.lstrip().upper().startswith(".TABLE"):                
                mw.curSQLDatabase.execute("SELECT name FROM sqlite_master WHERE type ='table' AND name NOT LIKE 'sqlite_%';")
                displayRows(mw, mw.curSQLDatabase.fetchall())
            if cmd.lstrip().upper().startswith(".DATABASE"):                
                mw.curSQLDatabase.execute("PRAGMA database_list;")
                displayRows(mw, mw.curSQLDatabase.fetchall())
            if cmd.lstrip().upper().startswith(".SCHEMA"):                
                try:
                    table = cmd.split()[1]
                    mw.curSQLDatabase.execute("SELECT sql FROM sqlite_master WHERE name = '%s';" % table)
                    displayRows(mw, mw.curSQLDatabase.fetchall())
                except Exception as e:
                    mw.txtSQLOutput.append("<p style='color:#FF0000;'>%s</p>" % str(e.args[0]))
            if cmd.lstrip().upper().startswith(".COLUMNS"):                
                try:
                    table = cmd.split()[1]
                    mw.curSQLDatabase.execute("PRAGMA table_info(%s);" % table)
                    displayRows(mw, mw.curSQLDatabase.fetchall())
                except Exception as e:
                    mw.txtSQLOutput.append("<p style='color:#FF0000;'>%s</p>" % str(e.args[0]))
        else:
            mw.curSQLDatabase.execute(cmd)
            if cmd.lstrip().upper().startswith("SELECT"):
                displayRows(mw, mw.curSQLDatabase.fetchall())
    except sqlite3.Error as e:
        mw.txtSQLOutput.append("<p style='color:#FF0000;'>%s</p>" % str(e.args[0]))
    mw.txtSQLOutput.verticalScrollBar().setValue(mw.txtSQLOutput.verticalScrollBar().maximum())        
    mw.txtSQLInput.selectAll()
        
#-------------------------------------------------------------------------------
# displayRows()
#-------------------------------------------------------------------------------
def displayRows(mw, rows):
    html = "<style>"
    html = html + ("table {")
    html = html + ("border-collapse: separate;")
    html = html + ("border-spacing: 0 15px;")        
    html = html + ("}")
    html = html + ("td {")
    html = html + ("width: 150px;")
    # html = html + ("text-align: center;")
    html = html + ("border: 1px solid black;")
    html = html + ("padding: 5px;")
    html = html + ("}")
    html = html + ("</style>")
    html = html + "<p><table>\n"
    for row in rows:
        html =  html + "<tr>"
        for field in row:
            if type(field) == str:
                align = "align='left'"
            else:
                align = "align='right'"
            html = html + "<td %s>" % align + str(field) + "</td>"
        html = html + "</tr>\n"
    html = html + "</table></p>\n"
    mw.txtSQLOutput.append(html)
    mw.txtSQLOutput.verticalScrollBar().setValue(mw.txtSQLOutput.verticalScrollBar().maximum())

#-------------------------------------------------------------------------------
# copyClipboard()
#-------------------------------------------------------------------------------
def copyClipboard(mw):
    clipboard = QApplication.clipboard().text()
    for line in clipboard.splitlines():
        mw.txtSQLInput.setText(line)
        runSQL(mw)
