#!c:/python23/python.exe
#-----------------------------------------------------------------------+
# Name:		fetchDisplay.py				                |
#									|
# Description:	This CGI script is handles AJAX style requests for a    |
# display fragment , which will be merged in the calling HTML page      |
#	                                                                |
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
import sheepgenomicsConf
import databaseModule

from sheepgenomicsPages import testPage, fetchPage
from obmodule import ob,getColumnAliases
from studyModule import microarrayObservation
from displayProcedures import getExpressionMapDisplay,getGenepixThumbnailDisplay
from brdfExceptionModule import brdfException


import logging


""" logging - comment out when not required """
# set up logger if we want logging
fetchdisplaylogger = logging.getLogger('fetchdisplay')
fetchdisplayhdlr = logging.FileHandler(os.path.join(globalConf.LOGPATH,'sgp_fetchdisplay.log'))
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
fetchdisplayhdlr.setFormatter(formatter)
fetchdisplaylogger.addHandler(fetchdisplayhdlr) 
fetchdisplaylogger.setLevel(logging.INFO)

# we need the same constants as the pages module.
fetcher="/%s/fetch.py"%sheepgenomicsConf.CGIPATH
displayfetcher="/%s/fetchDisplay.py"%sheepgenomicsConf.CGIPATH
imageurl="/%s/"%sheepgenomicsConf.IMAGEURLPATH
tempimageurl="/%s/"%sheepgenomicsConf.TEMPIMAGEURLPATH
imagepath=os.path.join(globalConf.IMAGEFILEPATH,sheepgenomicsConf.IMAGEFILEPATH)
jointomemberurl="/%s/"%sheepgenomicsConf.CGIPATH + "join.py?context=%s&totype=%s&jointype=%s&joininstance=%s"
jointonullurl="/%s/"%sheepgenomicsConf.CGIPATH + "join.py?context=%s&jointype=%s&joininstance=%s"       
jointooburl="/%s/"%sheepgenomicsConf.CGIPATH + "join.py?context=%s&totype=%s&fromob=%s&jointype=%s&joinhash=1"
joinfacturl="/%s/"%sheepgenomicsConf.CGIPATH + "join.py?context=%s&fromob=%s&jointype=%s&joinhash=2"
addCommentURL="/%s/"%sheepgenomicsConf.CGIPATH + "form.py?context=%s&formname=commentform&formstate=insert&aboutob=%s&aboutlsid=%s"
addLinkURL="/%s/"%sheepgenomicsConf.CGIPATH + "form.py?context=%s&formname=uriform&formstate=insert&aboutob=%s&aboutlsid=%s"
homeurl="/%s"%sheepgenomicsConf.HOMEPATH
underConstructionURL=os.path.join(sheepgenomicsConf.PAGEPATH,sheepgenomicsConf.UNDERCONSTRUCTION)


objectDumpURL="/%s/"%sheepgenomicsConf.CGIPATH + "fetch.py?obid=%s&context=%s"
#listChunkLink='<a href="/%s/"'%sheepgenomicsConf.CGIPATH + 'fetch.py?obid=%s&context=list&bookmark=%s&chunkSize=50>Next 50 items</a>'
listChunkLink="/%s/"%sheepgenomicsConf.CGIPATH + 'fetch.py?obid=%s&context=briefsearchsummarypage&bookmark=%s&target=ob&childview=%s&page=%s'



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

fetchdisplaylogger.info("initiated with %s\n\n"%str(fieldDict))

#expected fields are context, "obid" and the lsid of a display procedure.
# easiest way to get set up is to instantiate the object and use the
# built-in method for grabbing all displayfunctions attached to the
# object. In fact we need an instance of the object anyway, because the
# display procedure call that we will make, refers to self.
connection=databaseModule.getConnection()
myObject = ob()
result=""
fetchdisplaylogger.info("initialising object")
try:
    myObject.initFromDatabase(int(fieldDict['obid']),'ob',connection)
except:
    # try assuming we have an lsid
    try:
        myObject.initFromDatabase(fieldDict['obid'],'ob',connection)

        # complete the initialisation of the object , as in general the
        # displayFunction will need some data fields from the complete object.
        # see also the *Pages.py module which has a complete set of the
        # types for which we support complete intitialisation
    except:
        raise brdfException("object not found : %s" % fieldDict['obid'])        

if myObject.databaseFields['tablename'] == 'microarrayobservation':
    myObject = microarrayObservation()
    myObject.username=fieldDict['REMOTE_USER']
    myObject.initFromDatabase(int(fieldDict['obid']),connection)
    myObject.initMetadata(connection)
    myObject.discoverLinks(connection)
    myObject.initComments(connection)
    myObject.initHyperLinks(connection)                        
    myObject.initListMembership(connection)                        
    myObject.initDisplayFunctions(connection)
else:
    raise brdfException("fetchDisplay needs to be updated to be able to initialise %s"%myObject.databaseFields['tablename'])

# intialise the ob with the call back URL paths for this instance of the brdf
if myObject.obState['METADATA'] == 1:
    myObject.columnAliases = getColumnAliases(connection, myObject.metadataFields['tablename'])
            
myObject.fetcher=fetcher
myObject.displayfetcher=fetcher
myObject.imageurl=imageurl
myObject.tempimageurl=tempimageurl        
myObject.imagepath=imagepath
myObject.jointomemberurl=jointomemberurl
myObject.jointonullurl=jointonullurl
myObject.jointooburl=jointooburl
myObject.joinfacturl=joinfacturl
myObject.addCommentURL=addCommentURL
myObject.addLinkURL=addLinkURL
myObject.homeurl=homeurl
myObject.underConstructionURL=underConstructionURL


    
#test = testPage(fieldDict
fetchdisplaylogger.info("running display proc : %s"%fieldDict['displayprocedure'])
result = myObject.runDisplayFunctions(connection,procedureList = [fieldDict['displayprocedure']],context=fieldDict['context'])

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





