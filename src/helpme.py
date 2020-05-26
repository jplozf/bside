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

import const
import platform
import sys
import socket

from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtWebEngineWidgets import QWebEngineView

from PyQt5.QtCore import QT_VERSION_STR
from PyQt5.Qt import PYQT_VERSION_STR
from sip import SIP_VERSION_STR

#-------------------------------------------------------------------------------
# Class TabHelp
#-------------------------------------------------------------------------------
class TabHelp(QWidget):    
#-------------------------------------------------------------------------------
# __init__()
#-------------------------------------------------------------------------------
    def __init__(self, parent = None):
        QWidget.__init__(self, parent)
        self.txtHelp = QTextEdit()
        self.txtHelp.setReadOnly(True)        
        self.txtHelp.setText(help)
        vLayout = QVBoxLayout(self)
        vLayout.addWidget(self.txtHelp)

#-------------------------------------------------------------------------------
# Class TabWelcome
#-------------------------------------------------------------------------------
class TabWelcome(QWidget):    
#-------------------------------------------------------------------------------
# __init__()
#-------------------------------------------------------------------------------
    def __init__(self, parent = None):
        QWidget.__init__(self, parent)    
        self.txtWelcome = QWebEngineView()
        self.txtWelcome.setHtml(welcome)
        vLayout = QVBoxLayout(self)
        vLayout.addWidget(self.txtWelcome)

help = "<center><table cellpadding='0' cellspacing='5'>"

help = help + "<tr bgcolor='#6992c2'><td colspan = 2><center><b>" + const.APPLICATION_NAME + "</b></center></td></tr>"

help = help + "<tr><td colspan = 2><center><i>" + const.BLAHBLAH_01 + "</i></center></td></tr>"
help = help + "<tr><td colspan = 2><center><i>" + const.BLAHBLAH_02 + "</i></center></td></tr>"
help = help + "<tr><td colspan = 2><center><i>" + const.BLAHBLAH_03 + "</i></center></td></tr>"
help = help + "<tr><td colspan = 2>&nbsp;</td></tr>"

help = help + "<tr><td><b>Author</b></td><td>" + const.AUTHOR + "</td></tr>"
help = help + "<tr><td><b>Copyright</b></td><td>" + const.COPYRIGHT + "</td></tr>"
help = help + "<tr><td><b>License</b></td><td>" + const.LICENSE + "</td></tr>"
help = help + "<tr><td><b>Version</b></td><td>" + const.VERSION + "</td></tr>"
help = help + "<tr><td><b>Email</b></td><td>" + const.EMAIL + "</td></tr>"
help = help + "<tr><td><b>Organization Name</b></td><td>" + const.ORGANIZATION_NAME + "</td></tr>"
help = help + "<tr><td><b>Organization Domain</b></td><td>" + const.ORGANIZATION_DOMAIN + "</td></tr>"        
help = help + "<tr><td colspan = 2>&nbsp;</td></tr>"

help = help + "<tr bgcolor='#6992c2'><td colspan = 2><center><b>Host</b></center></td></tr>"

help = help + "<tr><td><b>Hostname</b></td><td>" + socket.gethostname() + "</td></tr>"
help = help + "<tr><td><b>Machine</b></td><td>" + platform.machine() + "</td></tr>"
help = help + "<tr><td><b>Version</b></td><td>" + platform.version() + "</td></tr>"
help = help + "<tr><td><b>Platform</b></td><td>" + platform.platform() + "</td></tr>"
help = help + "<tr><td><b>System</b></td><td>" + platform.system() + "</td></tr>"
help = help + "<tr><td><b>Processor</b></td><td>" + platform.processor() + "</td></tr>"
help = help + "<tr><td colspan = 2>&nbsp;</td></tr>"
help = help + "<tr><td><b>Python version</b></td><td>" + sys.version + "</td></tr>"
help = help + "<tr><td><b>PyQt version</b></td><td>" + PYQT_VERSION_STR + "</td></tr>"
help = help + "<tr><td><b>Qt version</b></td><td>" + QT_VERSION_STR + "</td></tr>"
help = help + "<tr><td><b>SIP version</b></td><td>" + SIP_VERSION_STR + "</td></tr>"
help = help + "<tr><td colspan = 2>&nbsp;</td></tr>"       

help = help + "<tr bgcolor='#6992c2'><td colspan = 2><center><b>Interface</b></center></td></tr>"        

help = help + "<tr><td><b>F1</b></td><td>Show this help page</td></tr>"
help = help + "<tr><td><b>F2</b></td><td>Save the current file</td></tr>"
help = help + "<tr><td><b>F3 or Ctrl-F</b></td><td>Search & GoTo Line</td></tr>"
help = help + "<tr><td><b>F5</b></td><td>Run current script</td></tr>"
help = help + "<tr><td><b>F6</b></td><td>Open a Python console</td></tr>"
help = help + "<tr><td><b>Ctrl+N</b></td><td>Open a new blank file</td></tr>"
help = help + "<tr><td><b>Ctrl+O</b></td><td>Open a file</td></tr>"
help = help + "<tr><td><b>F8</b></td><td>Open a new Python scratch file</td></tr>"
help = help + "<tr><td><b>F9</b></td><td>Restart BSide</td></tr>"
help = help + "<tr><td><b>F10</b></td><td>Exit from BSide</td></tr>"
help = help + "<tr><td><b>F11</b></td><td>Switch between full screen and normal mode</td></tr>"
help = help + "<tr><td colspan = 2>&nbsp;</td></tr>"       

help = help + "<tr bgcolor='#6992c2'><td colspan = 2><center><b>Tools management</b></center></td></tr>"        
help = help + "<tr><td colspan = 2><i>These variables embedded between [ and ] are available for using in tools command line.</i></td></tr>"
help = help + "<tr><td colspan = 2>&nbsp;</td></tr>"
help = help + "<tr><td><b>FULLNAME</b></td><td>Full name with path and extension of the current file</td></tr>"
help = help + "<tr><td><b>BASENAME</b></td><td>Name with extension of the current file</td></tr>"
help = help + "<tr><td><b>DIRNAME</b></td><td>Path of the current file</td></tr>"
help = help + "<tr><td><b>FULLNAME_WITHOUT_EXT</b></td><td>Full name with path but no extension of the current file</td></tr>"
help = help + "<tr><td><b>NAME_WITHOUT_EXT</b></td><td>Name without path nor extension of the current file</td></tr>"
help = help + "<tr><td><b>EXTENSION</b></td><td>Extension of the current file</td></tr>"
help = help + "<tr><td><b>RANDOM_NAME</b></td><td>A random file name without extension</td></tr>"
help = help + "<tr><td><b>TEMPDIR</b></td><td>Path to the local temporary folder</td></tr>"
help = help + "<tr><td><b>PATHSEP</b></td><td>The path separator according to the current OS</td></tr>"
help = help + "<tr><td><b>PROJECT</b></td><td>The project name</td></tr>"
help = help + "<tr><td><b>HOME</b></td><td>The home folder of the connected user</td></tr>"
help = help + "<tr><td colspan = 2>&nbsp;</td></tr>"       

help = help + "</table></center>"

"""
welcome = "<html>"
welcome = welcome + "<body style=\"font-family: 'Open Sans', arial, sans-serif;>\">"
welcome = welcome + "<h1>Welcome</h1>"
welcome = welcome + "<p>"
welcome = welcome + "<table>"
welcome = welcome + "<tr><td rowspan='4' style=\"vertical-align : middle;text-align:center;\"><center><img src='./pix/bside.png'></center></td><td><h3>" + const.BLAHBLAH_01 + "</h3></td></tr>"
welcome = welcome + "<tr><td><h3>" + const.BLAHBLAH_02 + "</h3></td></tr>"
welcome = welcome + "<tr><td><h3>" + const.BLAHBLAH_03 + "</h3></td></tr>"
welcome = welcome + "<tr><td><i>&copy; jpl@ozf.fr 2019</i></td></tr>"
welcome = welcome + "</table>"
welcome = welcome + "</p>"
welcome = welcome + "<p>You can find the last version of BSide at <a href='" + const.ORGANIZATION_DOMAIN + "'>" + const.ORGANIZATION_DOMAIN + ".</p>"        
welcome = welcome + "<p><center><img src='http://www.ozf.fr/bside/news.png'></center></p>"
welcome = welcome + "</body"
welcome = welcome + "</html>"
"""
welcome = "<p><center><img src='http://www.ozf.fr/bside/BSide_inside.png'></center></p>"
# welcome = welcome + "<p><center><img src='file:///media/jpl/JPL004/Projets/Python/Bside/src/pix/bside.png'></center></p>"
# welcome = welcome + "<p><center><img src='pix/bside.png'></center></p>"
