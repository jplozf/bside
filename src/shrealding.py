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
import subprocess
import psutil
import queue
import subprocess
import threading
from time import sleep

from PyQt5.QtCore import QThread, pyqtSignal

#-------------------------------------------------------------------------------
# Class Shreald
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
                            # sleep(1)
                            break
                    except:
                        pass

                tp.join()
                to.join()
                te.join()
            except:
                self.mw.bgJob = self.mw.bgJob - 1
                
#-------------------------------------------------------------------------------
# enqueueStream()
#-------------------------------------------------------------------------------
    def enqueueStream(self, stream, queue, type):
        # print("enqueue", flush=True)
        for line in iter(stream.readline, b''):
            # print("enqueue %s" % line.decode('utf-8'), flush=True)
            queue.put(str(type) + line.decode('utf-8'))
            # queue.put(str(type) + line)
        stream.flush()
        stream.close()

#-------------------------------------------------------------------------------
# enqueueProcess()
#-------------------------------------------------------------------------------
    def enqueueProcess(self, process, queue):
        process.wait()
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
