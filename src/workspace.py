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
# Global Constants
#-------------------------------------------------------------------------------
import shelve
import const
import os

import helpme
import settings
import editor
import pynter
import shell
import QHexEditor

#-------------------------------------------------------------------------------
# These are the default values
#-------------------------------------------------------------------------------
defaultValues = [ 
    ['TABS', [['Welcome', None],['About', None]]],
    ['PROJECT', None],
    ['CURRENT_TAB', 0],
    ['CURRENT_LOW_TAB', 0],
    ['MRU_PROJECTS', []]
]

#-------------------------------------------------------------------------------
# restoreWorkspace()
#-------------------------------------------------------------------------------
def restoreWorkspace():
#-------------------------------------------------------------------------------
# Open config file
#-------------------------------------------------------------------------------
    appDir = os.path.join(os.path.expanduser("~"), const.APP_FOLDER)
    if not os.path.exists(appDir):
        os.makedirs(appDir)
    dbFileName = os.path.join(os.path.join(appDir, const.WORKSPACE_FILE))
    db = shelve.open(dbFileName, writeback=True)

#-------------------------------------------------------------------------------
# Set default values if they not exists in config file
#-------------------------------------------------------------------------------
    for x in defaultValues:
       if not x[0] in db:
          db[x[0]] = x[1]

#-------------------------------------------------------------------------------
# Save config file
#-------------------------------------------------------------------------------
    db.sync()
    return db

#-------------------------------------------------------------------------------
# resetWorkspace()
#-------------------------------------------------------------------------------
def resetWorkspace():
    for x in defaultValues:
            db[x[0]] = x[1]    

#-------------------------------------------------------------------------------
# saveWorkspace()
#-------------------------------------------------------------------------------
def saveWorkspace(mw):
    tabs = []
    tTab = []
#-------------------------------------------------------------------------------
# Open config file
#-------------------------------------------------------------------------------
    appDir = os.path.join(os.path.expanduser("~"), const.APP_FOLDER)
    if not os.path.exists(appDir):
        os.makedirs(appDir)
    dbFileName = os.path.join(os.path.join(appDir, const.WORKSPACE_FILE))
    db = shelve.open(dbFileName, writeback=True)

    # Save mw current tab index
    db["CURRENT_TAB"] = mw.tbwHighRight.currentIndex()
    db["CURRENT_LOW_TAB"] = mw.tbwLowRight.currentIndex()
    
    # Save mw current open project     
    if mw.project is not None:
        db["PROJECT"] = mw.project.name
    else:
        db["PROJECT"] = None

    # Save mw open tabs
    for i in range(mw.tbwHighRight.count()):
        tab = mw.tbwHighRight.widget(i)
        tTab = None
        if isinstance(tab, helpme.TabWelcome):
            tTab = ["Welcome", None]
        elif isinstance(tab, helpme.TabHelp):
            tTab = ["Help", None]
        elif isinstance(tab, editor.WEditor):
            tTab = ["WEditor", tab.filename]
        elif isinstance(tab, editor.WMarkdown):
            tTab = ["WMarkdown", tab.filename]
        elif isinstance(tab, QHexEditor.QHexEditor):
            tTab = ["WHexedit", tab.filename]
        elif isinstance(tab, settings.TabSettings):
            tTab = ["Settings", None]
        # Shell Tab
        elif isinstance(tab, pynter.LXInter):
            tTab = ["LXInter", None]
        elif isinstance(tab, pynter.WXInter):
            tTab = ["WXInter", None]
        elif isinstance(tab, pynter.WInter):
            tTab = ["WInter", None]
        # Interpreter Tab
        elif isinstance(tab, shell.LXShell):
            tTab = ["LXShell", None]
        elif isinstance(tab, shell.WXShell):
            tTab = ["WXShell", None]
        elif isinstance(tab, shell.WShell):
            tTab = ["WShell", None]
        # Packages Tab
        elif isinstance(tab, pynter.TabPIP):
            tTab = ["TabPIP", None]
        if tTab != None:
            tabs.append(tTab)
    db["TABS"] = tabs
    
    db["MRU_PROJECTS"] = mw.mruProjects
    
    db.sync()
        