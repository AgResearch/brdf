#!/usr/bin/env python
#
# ths script marshalls a file referred to by a datasource object, into a folder
# where it can be accessed by a web-pae, and returns a redirect to the 
# file

import sys
import types
import cgi
import cgitb; cgitb.enable()
import os
import os.path

from types import *
from os import environ

import agbrdfConf

from agresearchPages import testPage, errorPage,getManualRedirect
from brdfExceptionModule import brdfException
from displayProcedures import marshallDataSource


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

# marshall the file to be made available to the user
uncompress = False
if "uncompress" in fieldDict:
   if fieldDict["uncompress"].upper() == "TRUE":
      uncompress = True

targetfilename = ''
if "targetfilename" in fieldDict:
   if len(fieldDict["targetfilename"]) > 4:
      targetfilename = fieldDict["targetfilename"] 



tempfilename = marshallDataSource(fieldDict['datasource'],agbrdfConf.BFILE_TEMPFOLDER,uncompress=uncompress,targetfilename=targetfilename)

# return redirect to the tempfile
tempfileurl=os.path.join(agbrdfConf.BFILE_TEMPURLPATH, tempfilename)
#page = getMetaRedirect(tempfileurl,tempfilename,context="bfile")
page = getManualRedirect(tempfileurl,tempfilename,context="bfile")
print page


    

#################### test code for basic functionality ##########
#print "Content-Type: text/html"     # HTML is following
#print                               # blank line, end of headers

#print "<html>\n"
#print "<head>\n"
#print "<TITLE>getFile script output</TITLE>"
#print "</head>\n"
#print "<body>\n"
#print "<H1>getFile</H1>"
#print "Hello, world!"
#print page


#form = cgi.FieldStorage()

#for key in form.keys():
#	print key + "=" + form[key].value

#print "</body>\n"
#print "</html>\n"

#form = cgi.FieldStorage()
#for key in form.keys():
#	print key + "=" + form[key].value

#print sys.path





