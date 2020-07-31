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
import cgi
import datetime
import settings

#-------------------------------------------------------------------------------
# header()
#-------------------------------------------------------------------------------
def header():
    html = """
    <!DOCTYPE html>
    <html>
    <head>
    <title>BSIDE REPOSITORY</title>
    </head>
    <body>
    <h1><center>BSIDE REPOSITORY</center></h1>
    """
    today = datetime.datetime.now()
    html = html + "<center>" + today.strftime(settings.db['FOCUS_FORMAT_DATE']) + "&nbsp;" 
    html = html + today.strftime(settings.db['FOCUS_FORMAT_HOUR']) + "</center><br><br>"   

    return html
    
#-------------------------------------------------------------------------------
# footer()
#-------------------------------------------------------------------------------
def footer():
    html = """
    </body>
    </html>
    """
    return html

#-------------------------------------------------------------------------------
# main()
#-------------------------------------------------------------------------------
def main():
    html = header()

    html = html + "<center><table>"
    
    html = html + "<tr><td>Repository</td><td>" + settings.db['BSIDE_REPOSITORY'] + "</td></tr>"
    html = html + "<tr><td>User</td><td>" + settings.db['PROJECT_USER_NAME'] + "</td></tr>"
    html = html + "<tr><td>Site</td><td>" + settings.db['PROJECT_SITE'] + "</td></tr>"
    html = html + "<tr><td>Mail</td><td>" + settings.db['PROJECT_MAIL'] + "</td></tr>"
    html = html + "<tr><td>Company</td><td>" + settings.db['PROJECT_COMPANY'] + "</td></tr>"    
    
    html = html + "</table></center>"

    html = html + footer()

    print(html)

if __name__ == "__main__":
    main()
