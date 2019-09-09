#!/usr/bin/env python
#-----------------------------------------------------------------------+
# Name:		search.py				                |
#									|
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

from agresearchPages import testPage, searchResultPage


# obtain form variables and copy into a dicionary
fields = cgi.FieldStorage()
fieldDict = dict()
for key in fields.keys():
    fieldDict[key] = fields[key].value

if 'REMOTE_USER' in environ:
    fieldDict.update({"REMOTE_USER" : environ['REMOTE_USER']})
else:
    fieldDict.update({"REMOTE_USER" : 'nobody'})      
    

#test = testPage(fieldDict)
search = searchResultPage(fieldDict)

print search.asHTML()

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





