#!/usr/bin/env python
#-----------------------------------------------------------------------+
# Name:		wait.py	     	 			                |
#									|
# Description:	Just a dummy called asychronously by Ajax posts         |
# so that we can issue a banner page immediately and do the             |
# synchronouse processing in the event handler	                        |
#=======================================================================|
# Revision History:							|
#									|
# Date      Ini Description						|
# --------- --- ------------------------------------------------------- |
# 6/2007    AFM  initial version                                        |
#-----------------------------------------------------------------------+


import sys
import types
import cgi
import cgitb; cgitb.enable()
import os

from types import *
from os import environ

import globalConf
import agbrdfConf

import logging


""" logging - comment out when not required """
# set up logger if we want logging
waitlogger = logging.getLogger('wait')
waithdlr = logging.FileHandler(os.path.join(globalConf.LOGPATH,'agbrdf_wait.log'))
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
waithdlr.setFormatter(formatter)
waitlogger.addHandler(waithdlr) 
waitlogger.setLevel(logging.INFO)

waitURL=os.path.join(agbrdfConf.IMAGEURLPATH,agbrdfConf.WAITGLYPH)


# obtain form variables and copy into a dicionary
fields = cgi.FieldStorage()
fieldDict = dict()
for key in fields.keys():
    fieldDict[key] = fields[key].value

if 'REMOTE_USER' in environ:
    fieldDict.update({"REMOTE_USER" : environ['REMOTE_USER']})
else:
    fieldDict.update({"REMOTE_USER" : 'nobody'})

fieldDict.update({'environment' : str(environ)})

waitlogger.info("initiated with %s\n\n"%str(fieldDict))

result='<img src="/%s" />'%waitURL
waitlogger.info("result : \n%s\n"%result)

print "Content-Type: text/html"     # HTML is following
print                               # blank line, end of headers
print result

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





