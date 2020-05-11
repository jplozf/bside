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
import math
import shutil
import time
import datetime
from datetime import datetime
from dateutil import tz
import pkg_resources
import threading
import subprocess
import traceback
import shlex

#-------------------------------------------------------------------------------
# isBinaryFile()
#-------------------------------------------------------------------------------
def isBinaryFile(filename):
    textchars = bytearray({7,8,9,10,12,13,27} | set(range(0x20, 0x100)) - {0x7f})
    is_binary_string = lambda bytes: bool(bytes.translate(None, textchars))
    _, ext = os.path.splitext(filename)            
    if ext.lower() == ".pdf":
        return True
    if os.path.isfile(filename):
        return (is_binary_string(open(filename, 'rb').read(1024)))
    else:
        return True

#---------------------------------------------------------------------------
# getHumanSize()
#---------------------------------------------------------------------------
def getHumanSize(size, suffix='B'):
    if size > 0:
        magnitude = int(math.floor(math.log(size, 1024)))
        val = size / math.pow(1024, magnitude)
        if magnitude > 7:
            return '{:.1f} {}{}'.format(val, 'Y', suffix)
        return '{:3.1f} {}{}'.format(val, ['', 'K', 'M', 'G', 'T', 'P', 'E', 'Z'][magnitude], suffix)
    else:
        return "Empty"
    
#---------------------------------------------------------------------------
# getDirSize()
#---------------------------------------------------------------------------
def getDirSize(start_path = '.'):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(start_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            # skip if it is symbolic link
            if not os.path.islink(fp):
                total_size += os.path.getsize(fp)

    return total_size

#---------------------------------------------------------------------------
# getDirSize()
#---------------------------------------------------------------------------
def getDirSize2(path, follow_symlinks=False):
    if os.path.exists(path):
        try:
            with os.scandir(path) as it:
                return sum(getDirSize2(entry, follow_symlinks=follow_symlinks) for entry in it)
        except NotADirectoryError:
            return os.stat(path, follow_symlinks=follow_symlinks).st_size
    else:
        return 0

#---------------------------------------------------------------------------
# UnixTime2DateTime()
#---------------------------------------------------------------------------
def UnixTime2DateTime(utime):
    from_zone = tz.tzutc()
    to_zone = tz.tzlocal()
    utc = datetime.utcfromtimestamp(utime)
    utc = utc.replace(tzinfo=from_zone)
    local = utc.astimezone(to_zone)   
    return (local.strftime('%Y-%m-%d %H:%M:%S'))

#---------------------------------------------------------------------------
# getFileInfo()
#---------------------------------------------------------------------------
def getFileInfo(fName):
    fileProps = {}
    fileProps.update({'name': os.path.split(fName)[1]})
    fileProps.update({'path': os.path.split(fName)[0]})
    # fileProps.update({'type': "Directory" if isDir == True else "File"})
    fileProps.update({'size': "%d (%s)" % (os.path.getsize(fName), getHumanSize(os.path.getsize(fName)))})
    fileProps.update({'modified': datetime.fromtimestamp(os.path.getmtime(fName)).strftime('%d/%m/%Y %H:%M:%S')})
    print(fileProps)
    return fileProps

#---------------------------------------------------------------------------
# createFile()
#---------------------------------------------------------------------------
def createFile(target, file):
    try:
        open(os.path.join(target, file), 'a').close()
    except:
        rc = False
    else:
        rc = True
    return rc

#---------------------------------------------------------------------------
# createDirectory()
#---------------------------------------------------------------------------
def createDirectory(target, dir):
    directory = os.path.join(target, dir)
    if not os.path.exists(directory):
        os.makedirs(directory)
        return True
    else:
        return False

#---------------------------------------------------------------------------
# deleteFolder()
#---------------------------------------------------------------------------
def deleteFolder(folder):
    try:
        shutil.rmtree(folder, ignore_errors=True)
    except:
        rc = False
    else:
        rc = True
    return rc

#---------------------------------------------------------------------------
# deleteFile()
#---------------------------------------------------------------------------
def deleteFile(file):
    try:
        os.remove(file)
    except:
        rc = False
    else:
        rc = True
    return rc

#---------------------------------------------------------------------------
# copyFile()
#---------------------------------------------------------------------------
def copyFile(src, dest):
    try:
        shutil.copy2(src, dest)
    except:
        rc = False
    else:
        rc = True
    return rc
    
#---------------------------------------------------------------------------
# copyStringToFile()
#---------------------------------------------------------------------------
def copyStringToFile(string, file):    
    with open(file, "w+") as text_file:
        text_file.write(string)
        
#---------------------------------------------------------------------------
# copyAllFilesFromTo()
#---------------------------------------------------------------------------
def copyAllFilesFromTo(src, dest):
    src_files = os.listdir(src)
    for file_name in src_files:
        full_file_name = os.path.join(src, file_name)
        if os.path.isfile(full_file_name):
            shutil.copy(full_file_name, dest)    
            
#---------------------------------------------------------------------------
# getPackagesList()
#---------------------------------------------------------------------------
def getPackagesList():            
    installed_packages = pkg_resources.working_set
    installed_packages_list = sorted(["%s, %s" % (i.key, i.version) for i in installed_packages])
    # print(installed_packages_list)
    return installed_packages_list

#---------------------------------------------------------------------------
# dateStringToTimeStamp()
#---------------------------------------------------------------------------
def dateStringToTimeStamp(sDate, sFormat="%d/%m/%Y"):
    return(time.mktime(datetime.strptime(sDate, sFormat).timetuple()))

#---------------------------------------------------------------------------
# timeStampToDateString()
#---------------------------------------------------------------------------
def timeStampToDateString(tStamp, sFormat="%d/%m/%Y"):
    # return(datetime.utcfromtimestamp(tStamp).strftime(sFormat))
    return(datetime.fromtimestamp(tStamp).strftime(sFormat))

colors = [
["aliceblue","#F0F8FF","240,248,255"],
["antiquewhite","#FAEBD7","250,235,215"],
["aqua","#00FFFF","0,255,255"],
["aquamarine","#7FFFD4","127,255,212"],
["azure","#F0FFFF","240,255,255"],
["beige","#F5F5DC","245,245,220"],
["bisque","#FFE4C4","255,228,196"],
["black","#000000","0,0,0"],
["blanchedalmond","#FFEBCD","255,235,205"],
["blue","#0000FF","0,0,255"],
["blueviolet","#8A2BE2","138,43,226"],
["brown","#A52A2A","165,42,42"],
["burlywood","#DEB887","222,184,135"],
["cadetblue","#5F9EA0","95,158,160"],
["chartreuse","#7FFF00","127,255,0"],
["chocolate","#D2691E","210,105,30"],
["coral","#FF7F50","255,127,80"],
["cornflowerblue","#6495ED","100,149,237"],
["cornsilk","#FFF8DC","255,248,220"],
["crimson","#DC143C","220,20,60"],
["cyan","#00FFFF","0,255,255"],
["darkblue","#00008B","0,0,139"],
["darkcyan","#008B8B","0,139,139"],
["darkgoldenrod","#B8860B","184,134,11"],
["darkgray","#A9A9A9","169,169,169"],
["darkgreen","#006400","0,100,0"],
["darkgrey","#A9A9A9","169,169,169"],
["darkkhaki","#BDB76B","189,183,107"],
["darkmagenta","#8B008B","139,0,139"],
["darkolivegreen","#556B2F","85,107,47"],
["darkorange","#FF8C00","255,140,0"],
["darkorchid","#9932CC","153,50,204"],
["darkred","#8B0000","139,0,0"],
["darksalmon","#E9967A","233,150,122"],
["darkseagreen","#8FBC8F","143,188,143"],
["darkslateblue","#483D8B","72,61,139"],
["darkslategray","#2F4F4F","47,79,79"],
["darkslategrey","#2F4F4F","47,79,79"],
["darkturquoise","#00CED1","0,206,209"],
["darkviolet","#9400D3","148,0,211"],
["deeppink","#FF1493","255,20,147"],
["deepskyblue","#00BFFF","0,191,255"],
["dimgray","#696969","105,105,105"],
["dimgrey","#696969","105,105,105"],
["dodgerblue","#1E90FF","30,144,255"],
["firebrick","#B22222","178,34,34"],
["floralwhite","#FFFAF0","255,250,240"],
["forestgreen","#228B22","34,139,34"],
["fuchsia","#FF00FF","255,0,255"],
["gainsboro","#DCDCDC","220,220,220"],
["ghostwhite","#F8F8FF","248,248,255"],
["gold","#FFD700","255,215,0"],
["goldenrod","#DAA520","218,165,32"],
["gray","#808080","128,128,128"],
["green","#008000","0,128,0"],
["greenyellow","#ADFF2F","173,255,47"],
["grey","#808080","128,128,128"],
["honeydew","#F0FFF0","240,255,240"],
["hotpink","#FF69B4","255,105,180"],
["indianred","#CD5C5C","205,92,92"],
["indigo","#4B0082","75,0,130"],
["ivory","#FFFFF0","255,255,240"],
["khaki","#F0E68C","240,230,140"],
["lavender","#E6E6FA","230,230,250"],
["lavenderblush","#FFF0F5","255,240,245"],
["lawngreen","#7CFC00","124,252,0"],
["lemonchiffon","#FFFACD","255,250,205"],
["lightblue","#ADD8E6","173,216,230"],
["lightcoral","#F08080","240,128,128"],
["lightcyan","#E0FFFF","224,255,255"],
["lightgoldenrodyellow","#FAFAD2","250,250,210"],
["lightgray","#D3D3D3","211,211,211"],
["lightgreen","#90EE90","144,238,144"],
["lightgrey","#D3D3D3","211,211,211"],
["lightpink","#FFB6C1","255,182,193"],
["lightsalmon","#FFA07A","255,160,122"],
["lightseagreen","#20B2AA","32,178,170"],
["lightskyblue","#87CEFA","135,206,250"],
["lightslategray","#778899","119,136,153"],
["lightslategrey","#778899","119,136,153"],
["lightsteelblue","#B0C4DE","176,196,222"],
["lightyellow","#FFFFE0","255,255,224"],
["lime","#00FF00","0,255,0"],
["limegreen","#32CD32","50,205,50"],
["linen","#FAF0E6","250,240,230"],
["magenta","#FF00FF","255,0,255"],
["maroon","#800000","128,0,0"],
["mediumaquamarine","#66CDAA","102,205,170"],
["mediumblue","#0000CD","0,0,205"],
["mediumorchid","#BA55D3","186,85,211"],
["mediumpurple","#9370DB","147,112,219"],
["mediumseagreen","#3CB371","60,179,113"],
["mediumslateblue","#7B68EE","123,104,238"],
["mediumspringgreen","#00FA9A","0,250,154"],
["mediumturquoise","#48D1CC","72,209,204"],
["mediumvioletred","#C71585","199,21,133"],
["midnightblue","#191970","25,25,112"],
["mintcream","#F5FFFA","245,255,250"],
["mistyrose","#FFE4E1","255,228,225"],
["moccasin","#FFE4B5","255,228,181"],
["navajowhite","#FFDEAD","255,222,173"],
["navy","#000080","0,0,128"],
["oldlace","#FDF5E6","253,245,230"],
["olive","#808000","128,128,0"],
["olivedrab","#6B8E23","107,142,35"],
["orange","#FFA500","255,165,0"],
["orangered","#FF4500","255,69,0"],
["orchid","#DA70D6","218,112,214"],
["palegoldenrod","#EEE8AA","238,232,170"],
["palegreen","#98FB98","152,251,152"],
["paleturquoise","#AFEEEE","175,238,238"],
["palevioletred","#DB7093","219,112,147"],
["papayawhip","#FFEFD5","255,239,213"],
["peachpuff","#FFDAB9","255,218,185"],
["peru","#CD853F","205,133,63"],
["pink","#FFC0CB","255,192,203"],
["plum","#DDA0DD","221,160,221"],
["powderblue","#B0E0E6","176,224,230"],
["purple","#800080","128,0,128"],
["red","#FF0000","255,0,0"],
["rosybrown","#BC8F8F","188,143,143"],
["royalblue","#4169E1","65,105,225"],
["saddlebrown","#8B4513","139,69,19"],
["salmon","#FA8072","250,128,114"],
["sandybrown","#F4A460","244,164,96"],
["seagreen","#2E8B57","46,139,87"],
["seashell","#FFF5EE","255,245,238"],
["sienna","#A0522D","160,82,45"],
["silver","#C0C0C0","192,192,192"],
["skyblue","#87CEEB","135,206,235"],
["slateblue","#6A5ACD","106,90,205"],
["slategray","#708090","112,128,144"],
["slategrey","#708090","112,128,144"],
["snow","#FFFAFA","255,250,250"],
["springgreen","#00FF7F","0,255,127"],
["steelblue","#4682B4","70,130,180"],
["tan","#D2B48C","210,180,140"],
["teal","#008080","0,128,128"],
["thistle","#D8BFD8","216,191,216"],
["tomato","#FF6347","255,99,71"],
["turquoise","#40E0D0","64,224,208"],
["violet","#EE82EE","238,130,238"],
["wheat","#F5DEB3","245,222,179"],
["white","#FFFFFF","255,255,255"],
["whitesmoke","#F5F5F5","245,245,245"],
["yellow","#FFFF00","255,255,0"],
["yellowgreen","#9ACD32","154,205,50"]
]

#---------------------------------------------------------------------------
# isColorName()
#---------------------------------------------------------------------------
def isColorName(sColor):
    rc = False
    for tColor in colors:
        if sColor.lower() == tColor[0].lower():
            rc = True
            break
    return rc

"""
>>> import time
>>> import datetime
>>> s = "01/12/2011"
>>> time.mktime(datetime.datetime.strptime(s, "%d/%m/%Y").timetuple())
1322697600.0
"""

#---------------------------------------------------------------------------
# Class ThreadedCommand2
#---------------------------------------------------------------------------
class ThreadedCommand2(object):
    '''
    Enables to run subprocess commands in a different thread
    with TIMEOUT option!

    Based on jcollado's solution:
    http://stackoverflow.com/questions/1191374/subprocess-with-timeout/4825933#4825933
    '''
#---------------------------------------------------------------------------
# __init__()
#---------------------------------------------------------------------------
    def __init__(self, cmd):
        self.cmd = cmd
        self.process = None
        self.out = None
        self.err = None

#---------------------------------------------------------------------------
# run()
#---------------------------------------------------------------------------
    def run(self, timeout=0, **kwargs):
        def target(**kwargs):
            self.process = subprocess.Popen(self.cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, **kwargs)
            self.out, self.err = self.process.communicate(timeout=1)

        thread = threading.Thread(target=target, kwargs=kwargs)
        thread.start()

        thread.join(timeout)
        if thread.is_alive():
            self.process.terminate()
            thread.join()

        return self.process.returncode
