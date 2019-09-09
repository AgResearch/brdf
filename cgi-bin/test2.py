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
#import cgitb; cgitb.enable()
import globalConf
import agbrdfConf

from types import *
from mx import DateTime
#    from mxDateTime import *
#    from mxDateTime import __version__

#from agresearchPages import errorPage

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





