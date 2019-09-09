#!/usr/bin/env python
#-----------------------------------------------------------------------+
# Name:		search.py				                |
#									|
# Description:	This CGI script is called from Nutrigenomics search     |
#	        pages                                                   |
#=======================================================================|
# Copyright 2005 by Nutrigenomics (NZ).					|
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
import os
import logging
import globalConf
import agbrdfConf

from types import *

cgimodulelogger = logging.getLogger('cgi')
cgimodulehdlr = logging.FileHandler(os.path.join(globalConf.LOGPATH,'agresearchcgi.log'))
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
cgimodulehdlr.setFormatter(formatter)
cgimodulelogger.addHandler(cgimodulehdlr)
cgimodulelogger.setLevel(logging.INFO)

cgimodulelogger.info("hello are u logging ? ")

#################### test code for basic functionality ##########
print "Content-Type: text/html"     # HTML is following
print                               # blank line, end of headers

print "<html>\n"
print "<head>\n"
print "<TITLE>CGI script output</TITLE>"
print "</head>\n"
print "<body>\n"
print "<pre>"
print "<H1>This is my first CGI script</H1>"
print "Hello, world!"
print sys.path 
print globalConf.LOGPATH
print "</PRE>"
print "</body>\n"
print "</html>\n"





