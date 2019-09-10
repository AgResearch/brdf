#!/usr/bin/env python
#-----------------------------------------------------------------------+
# Name:		report.py				                |
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


from agresearchPages import testPage, simpleReportPage


# obtain form variables and copy into a dicionary
#fields = cgi.FieldStorage()
#fieldDict = dict()
#for key in fields.keys():
#    fieldDict[key] = fields[key].value
fields = cgi.FieldStorage()
fieldDict = dict()
for key in fields.keys():
    if not isinstance(fields[key],ListType):
        fieldDict[key] = fields[key].value
    else:
        instanceCount = 0
        listValue = []
        for item in fields[key]:
            #fieldName = "%s_%s"%(item.name,instanceCount)
            listValue.append(item.value)
            #fieldDict[fieldName] = item.value
            instanceCount += 1
        fieldDict[key] = listValue


#test = testPage(fieldDict)
report = simpleReportPage(fieldDict)
if fieldDict['context'] == 'page':
    report.displayReportPage()
else:
    report.doReport()

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





