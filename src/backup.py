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
import os
import zipfile
from datetime import datetime
import sqlite3

import settings

#-------------------------------------------------------------------------------
# backupRepository()
#-------------------------------------------------------------------------------
def backupRepository(since, parent):
    # ago = now - datetime.timedelta(hours = 24)
    # ago 
    
    db = sqlite3.connect("backup.db")
    db.execute("CREATE TABLE IF NOT EXISTS backups (id INTEGER PRIMARY KEY, backupID TEXT, path TEXT, size INTEGER, mtime INTEGER)")
    db.execute("CREATE TABLE IF NOT EXISTS files (id INTEGER PRIMARY KEY, path TEXT, backupTime INTEGER, status TEXT, size INTEGER, backupID TEXT)")
    
    """
    Table backups contents ONLY files which are in the backupID zip file
    Table files   contents ALL files for the given date and their backupID location 
    """
    
    now = datetime.now()    
    backupID = now.strftime("bside_%Y%m%d-%H%M%S.zip")
    zipFilePath = os.path.join(settings.db['BACKUP_PATH'], backupID)
    outFile = zipfile.ZipFile(zipFilePath, "w", compression=zipfile.ZIP_DEFLATED)

    for root, dirs, files in os.walk(settings.db['BSIDE_REPOSITORY']):  
        for fname in files:
            path = os.path.join(root, fname)
            st = os.stat(path)    
            mtime = datetime.fromtimestamp(st.st_mtime)
            status = "Created"
            if mtime > since:
                parent.showDebug('%s modified %s'%(path, mtime))
                outFile.write(path)
                status = "Modified"
                datas = (backupID, path, st.st_size, st.st_mtime)
                db.execute("INSERT INTO backups (backupID, path, size, mtime) VALUES (?, ?, ?, ?)", datas)
            datas = (path, datetime.timestamp(now), status, st.st_size, backupID)
            db.execute("INSERT INTO files (path, backupTime, status, size, backupID) VALUES (?, ?, ?, ?, ?)", datas)            
    outFile.close()    
    db.commit()
    db.close()
    return now


#---------------------------------------------------------------------------
# zipdir()
#---------------------------------------------------------------------------
def zipDir(dirPath=None, zipFilePath=None, includeDirInZip=True):
    """Create a zip archive from a directory.

    Note that this function is designed to put files in the zip archive with
    either no parent directory or just one parent directory, so it will trim any
    leading directories in the filesystem paths and not include them inside the
    zip archive paths. This is generally the case when you want to just take a
    directory and make it into a zip file that can be extracted in different
    locations. 

    Keyword arguments:

    dirPath -- string path to the directory to archive. This is the only
    required argument. It can be absolute or relative, but only one or zero
    leading directories will be included in the zip archive.

    zipFilePath -- string path to the output zip file. This can be an absolute
    or relative path. If the zip file already exists, it will be updated. If
    not, it will be created. If you want to replace it from scratch, delete it
    prior to calling this function. (default is computed as dirPath + ".zip")

    includeDirInZip -- boolean indicating whether the top level directory should
    be included in the archive or omitted. (default True)

    """
    if not zipFilePath:
        zipFilePath = dirPath + ".zip"
    if not os.path.isdir(dirPath):
        raise OSError("dirPath argument must point to a directory. "
                      "'%s' does not." % dirPath)
    parentDir, dirToZip = os.path.split(dirPath)
    #Little nested function to prepare the proper archive path
    def trimPath(path):
        archivePath = path.replace(parentDir, "", 1)
        if parentDir:
            archivePath = archivePath.replace(os.path.sep, "", 1)
        if not includeDirInZip:
            archivePath = archivePath.replace(dirToZip + os.path.sep, "", 1)
        return os.path.normcase(archivePath)

    outFile = zipfile.ZipFile(zipFilePath, "w",
                              compression=zipfile.ZIP_DEFLATED)
    for (archiveDirPath, dirNames, fileNames) in os.walk(dirPath):
        for fileName in fileNames:
            filePath = os.path.join(archiveDirPath, fileName)
            outFile.write(filePath, trimPath(filePath))
        #Make sure we get empty directories as well
        if not fileNames and not dirNames:
            zipInfo = zipfile.ZipInfo(trimPath(archiveDirPath) + "/")
            #some web sites suggest doing
            #zipInfo.external_attr = 16
            #or
            #zipInfo.external_attr = 48
            #Here to allow for inserting an empty directory.  Still TBD/TODO.
            outFile.writestr(zipInfo, "")
    outFile.close()
