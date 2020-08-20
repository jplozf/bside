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
import http.server
import threading
import ssl

import settings

webStarted = False

#-------------------------------------------------------------------------------
# startServer()
#-------------------------------------------------------------------------------
def startServer(mw):
    hostName = settings.db['WEB_SERVER_ADDRESS']
    serverPort = settings.db['WEB_SERVER_PORT']
    global webStarted
    if webStarted == False:
        daemon = threading.Thread(target=threadServer, args=(hostName, serverPort, mw))
        daemon.setDaemon(True)
        daemon.start()
        msg = "Web server started at http://%s:%s" % (hostName, serverPort)
    else:
        msg = "Web server already started"
    mw.showMessage(msg)
    return msg

#-------------------------------------------------------------------------------
# threadServer()
#-------------------------------------------------------------------------------
def threadServer(hostName, serverPort, mw):    
    global webServer

    handler = http.server.CGIHTTPRequestHandler
    # handler.cgi_directories = ["./cgi-bin"]
    if settings.db['WEB_SSL_ENABLED'] == True:
        webServer.socket = ssl.wrap_socket(webServer.socket, keyfile = settings.db['WEB_SSL_PRIVATE_KEY'], certfile = settings.db['WEB_SSL_CERTIFICATE'], server_side = True)
    
    try:
        global webStarted
        webStarted = True
        webServer = http.server.HTTPServer((hostName, serverPort), handler)
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass

#-------------------------------------------------------------------------------
# stopServer()
#-------------------------------------------------------------------------------
def stopServer(mw):
    global webStarted
    global webServer
    if webStarted == True:
        webServer.server_close()
        webStarted = False
        msg = "Web server stopped"
    else:
        msg = "Web server not started"
    mw.showMessage(msg)
    return msg

#-------------------------------------------------------------------------------
# statusServer()
#-------------------------------------------------------------------------------
def statusServer(mw):
    global webStarted
    if webStarted == True:
        msg = "Web server is running at http://%s:%s" % (settings.db['WEB_SERVER_ADDRESS'], settings.db['WEB_SERVER_PORT'])
    else:
        msg = "Web server is not running"
    mw.showMessage(msg)
    return msg

#-------------------------------------------------------------------------------
# isRunning()
#-------------------------------------------------------------------------------
def isRunning():
    rc = False
    global webStarted
    if webStarted == True:
        rc = True
    else:
        rc = False
    return rc
               
#-------------------------------------------------------------------------------
# restartServer()
#-------------------------------------------------------------------------------
def restartServer(mw):
    global webStarted
    global webServer
    if webStarted == True:
        webServer.server_close()
        startServer(mw)
        msg = "Web server restarted at http://%s:%s" % (settings.db['WEB_SERVER_ADDRESS'], settings.db['WEB_SERVER_PORT'])
    else:
        msg = startServer(mw)
    webStarted = True
    mw.showMessage(msg)
    return msg
    