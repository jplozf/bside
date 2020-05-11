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

from PyQt5.QtCore import QThread, pyqtSignal

#-------------------------------------------------------------------------------
# Class Shreald
#-------------------------------------------------------------------------------
class Shreald(QThread):

    linePrinted = pyqtSignal(str)

#-------------------------------------------------------------------------------
# __init__()
#-------------------------------------------------------------------------------
    def __init__(self, parent, cmd):
        super(Shreald, self).__init__(parent)
        self.cmd = cmd
        self.daemon = True
        self.start()

#-------------------------------------------------------------------------------
# run()
#-------------------------------------------------------------------------------
    def run(self):
        # print("starting Shreald")
        if self.cmd:
            self.process = subprocess.Popen(self.cmd, bufsize=1, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
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
                    # print(line)
                    self.linePrinted.emit(line)
                except:
                    pass
                
            tp.join()
            to.join()
            te.join()                        
                   
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
        
#-------------------------------------------------------------------------------
# kill()
#-------------------------------------------------------------------------------
    def kill(self):
        ppid = psutil.Process(self.process.pid)
        for proc in ppid.children(recursive=True):
            proc.kill()
        ppid.kill()