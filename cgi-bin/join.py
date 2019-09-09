#!/usr/bin/env python
#---------------------------------------------------------------------------------------------------+
# Name:		join.py		        		                                            |
#									                            |
# Description:	This CGI script is fetches objects                                                  |
#                                                                                                   |	                                                                |
#===================================================================================================|
# Copyright 2006 by AgResearch (NZ).					                            |
# All rights reserved.							                            |
#									                            |
#===================================================================================================|
# Revision History:							                            |
#									                            |
# Date      Ini Description		                                        		    |
# --------- --- ------------------------------------------------------------------------------------|
# 11/2005    AFM  initial version                                                                   |
#---------------------------------------------------------------------------------------------------+


import sys
import types
import cgi
import cgitb; cgitb.enable()

from types import *
from os import environ
import agbrdfConf

#sys.path.append('python/sitemodules')
#sys.path.append('m:\\projects\\brdf\\python\\modules')
#sys.path.append('C:/Python23/lib/site-packages/nutrigenomics')

from agresearchPages import testPage, joinPage


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



#test = testPage(fieldDict)
result = joinPage(fieldDict)

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





