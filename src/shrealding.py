#!/usr/bin/env python3
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
import subprocess
import psutil
import queue
import subprocess
import threading
import time

from PyQt5.QtCore import QThread, pyqtSignal

import settings

#-------------------------------------------------------------------------------
# Class Shreald
# Shrealding means "Shell in Thread"
#-------------------------------------------------------------------------------
class Shreald(QThread):

    linePrinted = pyqtSignal(str)

#-------------------------------------------------------------------------------
# __init__()
#-------------------------------------------------------------------------------
    def __init__(self, parent, cmd, cwd, shell=False):
        super(Shreald, self).__init__(parent)
        self.cmd = cmd
        self.cwd = cwd
        self.mw = parent
        self.shell = shell
        self.daemon = True
        self.returncode = None
        print(cmd)
        self.start()

#-------------------------------------------------------------------------------
# run()
#-------------------------------------------------------------------------------
    def run(self):
        # print("starting Shreald")
        if self.cmd:
            self.mw.bgJob = self.mw.bgJob + 1
            try:
                self.process = subprocess.Popen(self.cmd, cwd=self.cwd, bufsize=1, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=self.shell)
                q = queue.Queue()
                to = threading.Thread(target=self.enqueueStream, args=(self.process.stdout, q, 1))
                te = threading.Thread(target=self.enqueueStream, args=(self.process.stderr, q, 2))
                tp = threading.Thread(target=self.enqueueProcess, args=(self.process, q))
                te.start()
                to.start()
                tp.start()

                while True:
                    try:
                        line = q.get_nowait()
                        self.linePrinted.emit(line)
                        if line[0] == 'x':
                            break
                    except:
                        pass

                tp.join()
                to.join()
                te.join()
            except:
                print("Shreald Except")
                self.mw.bgJob = self.mw.bgJob - 1
                
#-------------------------------------------------------------------------------
# enqueueStream()
#-------------------------------------------------------------------------------
    def enqueueStream(self, stream, queue, type):
        # print("enqueue", flush=True)
        for line in iter(stream.readline, b''):
            queue.put(str(type) + line.decode(settings.db['SHELL_CODEPAGE']))
        stream.flush()
        stream.close()

#-------------------------------------------------------------------------------
# enqueueProcess()
#-------------------------------------------------------------------------------
    def enqueueProcess(self, process, queue):
        self.returncode = process.wait()
        # let's add some ignition delay to let time to complete the output
        time.sleep(0.3)
        queue.put('x')
        self.mw.bgJob = self.mw.bgJob - 1
        
#-------------------------------------------------------------------------------
# kill()
#-------------------------------------------------------------------------------
    def kill(self):
        ppid = psutil.Process(self.process.pid)
        for proc in ppid.children(recursive=True):
            proc.kill()
        ppid.kill()
