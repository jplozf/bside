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
import cgi
import datetime
import shelve
import os
import datetime

import const
import utils

#-------------------------------------------------------------------------------
# header()
#-------------------------------------------------------------------------------
def header(cached_db):
    html = """
    <!doctype html>
    <html>

    <head>
    <meta charset="UTF-8">
    <title>BSide Repository</title>
      <style type="text/css">
         *, *:before, *:after {{
         box-sizing: border-box;
         }}
         body {{
         margin: 5x;
         font: 14px Sans-Serif;
         background-color: #fff;
         color: #fff;
         }}
         h1, p {{
         margin: 0 0 1em 0;
         }}
         
         /* no grid support? */
         .sidebar {{
         float: left;
         width: 50%;
         }}
         .content {{
         float: right;
         width: 50%;
         }}
         /* make a grid */
         .wrapper {{
         max-width: 100%;
         margin: 0 auto;
         display: grid;
         grid-template-columns: 1fr 1fr;
         grid-gap: 2px;
         }}
         .wrapper > * {{
         background-color: #E6E6E6;
         color: #000000;
         border-radius: 5px;
         padding: 5px;
         font-size: 100%;
         /* needed for the floated layout*/
         margin-bottom: 5px;
         }}
         
         .header, .footer {{
         grid-column: 1 / -1;
         /* needed for the floated layout */
         clear: both;
         }}		 
	 a.header {{
         color: #663300;
         text-decoration: none;
         }}
         .footer {{
         text-align: right;
         }}
         
         /* We need to set the widths used on floated items back to auto, and remove the bottom margin as when we have grid we have gaps. */
         @supports (display: grid) {{
         .wrapper > * {{
         width: auto;
         margin: 0;
         }}
         }}
         
         /* File Explorer Table */
         table.fex {{
         background-color: #F3F3F3;
         border-collapse: collapse;
         width: 100%;
         margin: 0 0;
         }}
         th.fex {{
         background-color: #3490C4;
         color: #FFF;
         cursor: pointer;
         padding: 5px 10px;
         }}
         th.fex small {{
         font-size: 9px; 
         }}
         td.fex, th.fex {{
         text-align: left;
         }}
         td.alright {{
         text-align: right;
         }}
         a.fex {{
         text-decoration: none;
         }}
         td.fex a {{
         color: #663300;
         display: block;
         padding: 5px 10px;
         }}
         th.fex a {{
         padding-left: 0
         }}
         td.fex:first-of-type a {{
         background: url(../pix/16x16/Folder.png) no-repeat 10px 50%;
         padding-left: 35px;
         }}
         th.fex:first-of-type {{
         padding-left: 35px;
         }}
         td.fex:not(:first-of-type) a {{
         background-image: none !important;
         }}
         tr.fex:nth-of-type(odd) {{
         background-color: #E6E6E6;
         }}
         tr.fex:hover td {{
         background-color:#CACACA;
         }}
         tr.fex:hover td a {{
         color: #000;
         }}     
         
         /* Browse Directory Menu */
         ul {{
         border: 1px solid #e7e7e7;
         background-color: #f3f3f3;
         list-style-type: none;
         margin: 0;
         padding: 0;
         overflow: hidden;
         }}
         li a {{
         color: #666;
         display: block;
         text-align: center;
         padding: 6px 16px;
         text-decoration: none;
         }}
         li a:hover {{
         background-color: #111;
         color: #3490C4;
         }}
         li {{
         border-right: 1px solid #bbb;
         float: left;
         }}
         .active {{
         background-color: #3490C4;
         color: #FFF;
         }}         
      </style>
    </head>
    <body>    
    <div class="header">
    <table>
    <tr><td rowspan='4'><img src = '../../pix/bside.png'></td><td valign='bottom'><h1>BSIDE REPOSITORY</h1></td></tr>
    <tr><td valign='top'><a class='fex' href='mailto:{var0}'>{var1}</a> for <a class='fex' href='{var2}' target='_blank'>{var3}</a></td></tr>
    <tr><td valign='top'>&nbsp;</td></tr>
    <tr><td valign='top'>&nbsp;</td></tr>
    </table>
    </div>
    
    <div class="split left">
    <div id="container">
    """.format(var0=cached_db['PROJECT_MAIL'], var1=cached_db['PROJECT_USER_NAME'], var2=cached_db['PROJECT_SITE'], var3=cached_db['PROJECT_COMPANY'])
        
    # today = datetime.datetime.now()
    # html = html + "<center>" + today.strftime(cached_db['FOCUS_FORMAT_DATE']) + "&nbsp;" 
    # html = html + today.strftime(cached_db['FOCUS_FORMAT_HOUR']) + "</center><br><br>"   

    return html
    
#-------------------------------------------------------------------------------
# footer()
#-------------------------------------------------------------------------------
def footer(cached_db):
    html = """
    <div class="footer">
    <hr>
    <p class="footer">{copyright}</p>
    </div>
    </body>
    </html>
    """.format(copyright=const.COPYRIGHT)
    return html

#-------------------------------------------------------------------------------
# main()
#-------------------------------------------------------------------------------
def main():
    appDir = os.path.join(os.path.expanduser("~"), const.APP_FOLDER)
    cdbDir = os.path.join(os.path.join(appDir, const.CACHED_CONFIG_FILE))
    cached_db = shelve.open(cdbDir)
    
    params = cgi.FieldStorage()
    action = params.getvalue('a')
    target = params.getvalue('t')
    if (target is None) or (cached_db['BSIDE_REPOSITORY'] not in target) or ("../" in target) or ("..\\" in target):
        target = cached_db['BSIDE_REPOSITORY']    
    else:
        if os.path.isfile(target):
            if utils.isBinaryFile(target):
                # TODO : Download
                pass
            else:
                # TODO : Display
                pass                    
    
    print("Content-type:text/html\r\n\r\n")
    
    html = header(cached_db)
    
    html = html + buildNavBar(target, cached_db)

    html = html + """    
     <table class="fex">
      <thead class="fex">
        <tr class="fex">
          <th class="fex">Filename</th>
          <th class="fex">Type</th>
          <th class="fex">Size</th>
          <th class="fex">Date Modified</th>
        </tr>
      </thead>
      <tbody class="fex">
      """
    
    with os.scandir(target) as oscan:
        for entry in oscan:
            link = buildLink(entry.path)
            # html = html + "<tr><td>" + ("FILE" if entry.is_file() else "DIR") + "</td><td>" + entry.name + "</td></tr>"            
            html = html + "<tr class='fex'><td class='fex'><a class='fex' href='" + link + "'>" + entry.name + "</a></td>"
            html = html + "<td class='fex'><a class='fex' href='" + link + "'>" + ("FILE" if entry.is_file() else "DIR") + "</a></td>"
            html = html + "<td class='fex alright'><a class='fex' href='" + link + "'>" + (utils.getHumanSize(entry.stat().st_size) if entry.is_file() else "-")+ "</a></td>"
            mtime = entry.stat().st_mtime
            timestamp_str = datetime.datetime.fromtimestamp(mtime).strftime('%Y/%m/%d - %H:%M:%S')
            html = html + "<td class='fex'><a class='fex' href='" + link + "'>" + timestamp_str + "</a></td></tr>\n"

    html = html + "</tbody></table></div></div>"

    html = html + footer(cached_db)        
    
    print(html)

#-------------------------------------------------------------------------------
# buildLink()
#-------------------------------------------------------------------------------
def buildLink(entry):
    link = "./" + os.path.basename(__file__)
    link = link + "?t=" + entry
    return link

#-------------------------------------------------------------------------------
# getPathItem()
#-------------------------------------------------------------------------------
def getPathItem(aPath, n, db):
    aPath[0] = db['BSIDE_REPOSITORY']
    rPath = ""
    for i, d in enumerate(aPath):
        rPath = rPath + d + os.path.sep
        if i == n:
            break
    return rPath[:-1]

#-------------------------------------------------------------------------------
# buildNavBar()
#-------------------------------------------------------------------------------
def buildNavBar(target, cached_db):
    if os.path.isfile(target):
        target = os.path.dirname(target)
    target = target.replace(cached_db['BSIDE_REPOSITORY'],'')
    aPath = splitPath(target)
    aPath[0] = '[REPOSITORY]'
    bar = "<ul>\n"
    for i, d in enumerate(aPath):
        if i == 0:
            bar = bar + "<li><a href=\"{fullPath}\">{path}</a></li>\n".format(fullPath=buildLink(getPathItem(aPath, i, cached_db)), path=d)
        elif i == len(aPath) - 1:
            bar = bar + "<li><a class=\"active\" href=\"{fullPath}\">{path}</a></li>\n".format(fullPath=buildLink(getPathItem(aPath, i, cached_db)), path=d)
        else:
            bar = bar + "<li><a href=\"{fullPath}\">{path}</a></li>\n".format(fullPath=buildLink(getPathItem(aPath, i, cached_db)), path=d)
    bar = bar + "</ul>"
    """
    <ul>
        <li><a href="#home">Home</a></li>
        <li><a href="#news">News</a></li>
        <li><a href="#contact">Contact</a></li>
        <li style="float:right"><a class="active" href="#about">About</a></li>
    </ul>
    """
    return bar
    
#-------------------------------------------------------------------------------
# splitPath()
#-------------------------------------------------------------------------------
def splitPath(path):
    allparts = []
    while 1:
        parts = os.path.split(path)
        if parts[0] == path:  # sentinel for absolute paths
            allparts.insert(0, parts[0])
            break
        elif parts[1] == path: # sentinel for relative paths
            allparts.insert(0, parts[1])
            break
        else:
            path = parts[0]
            allparts.insert(0, parts[1])
    return allparts

if __name__ == "__main__":
    main()
