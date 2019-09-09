#!/usr/bin/env python
#-----------------------------------------------------------------------+
# Name:		fetch.py				                |
#									|
# Description:	This CGI script is fetches AgResearch objects 	        |                                                        |
#=======================================================================|
# Copyright 2005 by AgResearch (NZ).					|
# All rights reserved.							|
#									|
#=======================================================================|
# Revision History:							|
#									|
# Date      Ini Description						|
# --------- --- ------------------------------------------------------- |
# 9/2005    AFM  initial version                                        |
#-----------------------------------------------------------------------+


import sys
import types
import cgi
import cgitb; cgitb.enable()
import agbrdfConf

from types import *
from os import environ

#sys.path.append('python/sitemodules')
#sys.path.append('m:\\projects\\brdf\\python\\modules')
#sys.path.append('C:/Python23/lib/site-packages/nutrigenomics')

from agresearchPages_new import testPage, fetchPage,errorPage


# obtain form variables and copy into a dicionary
fields = cgi.FieldStorage()
fieldDict = dict()
for key in fields.keys():
    fieldDict[key] = fields[key].value

# potential environ on windows :
#{'environ': "{'AUTH_TYPE': 'Basic', 'HTTP_REFERER': 'http://localhost/cgi-bin/nutrigenomics/form.py',
#'SERVER_SOFTWARE': 'Apache/2.0.54 (Win32)', 'SCRIPT_NAME': '/cgi-bin/nutrigenomics/fetch.py', 'SERVER_SIGNATURE':
#'<address>Apache/2.0.54 (Win32) Server at localhost Port 80</address>\\n', 'REQUEST_METHOD': 'GET', 'SERVER_PROTOCOL':
#'HTTP/1.1', 'QUERY_STRING': 'context=default&obid=38201&target=ob', 'PATH': 'C:\\\\WINDOWS\\\\system32;C:\\\\WINDOWS;
#C:\\\\WINDOWS\\\\System32\\\\Wbem;C:\\\\Program Files\\\\Common Files\\\\Roxio Shared\\\\DLLShared;C:\\\\PROGRA~1\\\\
#CA\\\\SHARED~1\\\\SCANEN~1;C:\\\\PROGRA~1\\\\CA\\\\ETRUST~1;C:\\\\Program Files\\\\orant\\\\BIN;C:\\\\Program Files\\\\
#ATI Technologies\\\\ATI Control Panel', 'TK_LIBRARY': 'C:\\\\python23\\\\tcl\\\\tk8.4', 'HTTP_USER_AGENT': 'Mozilla/4.
#0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; .NET CLR 1.0.3705; .NET CLR 1.1.4322)', 'HTTP_CONNECTION':
#'Keep-Alive', 'SERVER_NAME': 'localhost', 'REMOTE_ADDR': '127.0.0.1', 'TIX_LIBRARY': 'C:\\\\python23\\\\tcl\\\\tix8.1',
#'SERVER_PORT': '80', 'SERVER_ADDR': '127.0.0.1', 'DOCUMENT_ROOT': 'C:/Program Files/Apache Group/Apache2/htdocs',
#'SYSTEMROOT': 'C:\\\\WINDOWS', 'COMSPEC': 'C:\\\\WINDOWS\\\\system32\\\\cmd.exe', 'SCRIPT_FILENAME':
#'C:/Program Files/Apache Group/Apache2/cgi-bin/nutrigenomics/fetch.py', 'SERVER_ADMIN': 'admin@agresearch.co.nz',
#'TCL_LIBRARY': 'C:\\\\python23\\\\tcl\\\\tcl8.4', 'REMOTE_USER': 'mccullocha', 'HTTP_HOST': 'localhost',
#'PATHEXT': '.COM;.EXE;.BAT;.CMD;.VBS;.VBE;.JS;.JSE;.WSF;.WSH',
#'REQUEST_URI': '/cgi-bin/nutrigenomics/fetch.py?context=default&obid=38201&target=ob',
#'HTTP_ACCEPT': 'image/gif, image/x-xbitmap, image/jpeg, image/pjpeg, application/vnd.ms-excel,
#application/vnd.ms-powerpoint, application/msword, application/x-shockwave-flash, */*', 'WINDIR':
#'C:\\\\WINDOWS', 'GATEWAY_INTERFACE': 'CGI/1.1', 'REMOTE_PORT': '1287', 'HTTP_ACCEPT_LANGUAGE': 'en-nz',
#'HTTP_ACCEPT_ENCODING': 'gzip, deflate'}", 'obid': '38201', 'target': 'ob', 'context': 'default'}

if 'REMOTE_USER' in environ:
    fieldDict.update({"REMOTE_USER" : environ['REMOTE_USER']})
else:
    fieldDict.update({"REMOTE_USER" : 'nobody'})

fieldDict.update({'environment' : str(environ)})
    

#test = testPage(fieldDict)
result = fetchPage(fieldDict)

if result.pageState['ERROR']:
    errorPage(result.pageState['MESSAGE'])
else:
    if fieldDict['context'] == 'genbank':
        print result.asGenbank()
    elif fieldDict['context'] == 'fasta':
        print result.asFASTA()
    else:
        print result.asHTML()

#test.asHTML()


#################### test code for basic functionality ##########
#print "Content-Type: text/html"     # HTML is following
#print                               # blank line, end of headers

#print "<html>\n"
#print "<head>\n"
#print "<TITLE>CGI script output</TITLE>"
#print "</head>\n"
#print "<body>\n"
#print "<H1>This is my first CGI script</H1>"
#print "Hello, world!"


#form = cgi.FieldStorage()

#for key in form.keys():
#	print key + "=" + form[key].value

#print "</body>\n"
#print "</html>\n"

#form = cgi.FieldStorage()
#for key in form.keys():
#	print key + "=" + form[key].value

#print sys.path





