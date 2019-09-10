#!/usr/bin/python
#-----------------------------------------------------------------------+
# Name:		fetchAnalysis.py				        |
#									|
# Description:	This CGI script  handles AJAX style requests for an     |
# analysis fragment , which will be merged in the calling HTML page     |
#	                                                                |
#=======================================================================|
# Revision History:							|
#									|
# Date      Ini Description						|
# --------- --- ------------------------------------------------------- |
# 2/2008    AFM  initial version                                        |
#-----------------------------------------------------------------------+


import sys
import types
import cgi
import cgitb; cgitb.enable()
import os
import re

from types import *
from os import environ

import globalConf
import agbrdfConf
import databaseModule

from agresearchPages import testPage, fetchPage,errorPage
from obmodule import ob,getColumnAliases
from analysisModule import runProcedure , analysisProcedureOb
from brdfExceptionModule import brdfException
from studyModule import geneExpressionStudy
from listModule import obList
from dataImportModule import dataSourceOb
from labResourceModule import labResourceOb
from sequenceModule import bioSequenceOb


import logging


""" logging - comment out when not required """
# set up logger if we want logging
fetchanalysislogger = logging.getLogger('fetchanalysis')
fetchanalysishdlr = logging.FileHandler(os.path.join(globalConf.LOGPATH,'agbrdf_fetchanalysis.log'))
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
fetchanalysishdlr.setFormatter(formatter)
fetchanalysislogger.addHandler(fetchanalysishdlr) 
fetchanalysislogger.setLevel(logging.INFO)

# we need the same constants as the pages module.
fetcher="/%s/fetch.py"%agbrdfConf.CGIPATH
displayfetcher="/%s/fetchDisplay.py"%agbrdfConf.CGIPATH
analysisfetcher="/%s/fetchAnalysis.py"%agbrdfConf.CGIPATH
imageurl="/%s/"%agbrdfConf.IMAGEURLPATH
tempimageurl="/%s/"%agbrdfConf.TEMPIMAGEURLPATH
imagepath=os.path.join(globalConf.IMAGEFILEPATH,agbrdfConf.IMAGEFILEPATH)
jointomemberurl="/%s/"%agbrdfConf.CGIPATH + "join.py?context=%s&totype=%s&jointype=%s&joininstance=%s"
jointonullurl="/%s/"%agbrdfConf.CGIPATH + "join.py?context=%s&jointype=%s&joininstance=%s"
jointooburl="/%s/"%agbrdfConf.CGIPATH + "join.py?context=%s&totype=%s&fromob=%s&jointype=%s&joinhash=1"
joinfacturl="/%s/"%agbrdfConf.CGIPATH + "join.py?context=%s&fromob=%s&jointype=%s&joinhash=2"
addCommentURL="/%s/"%agbrdfConf.CGIPATH + "form.py?context=%s&formname=commentform&formstate=insert&aboutob=%s&aboutlsid=%s"
addLinkURL="/%s/"%agbrdfConf.CGIPATH + "form.py?context=%s&formname=uriform&formstate=insert&aboutob=%s&aboutlsid=%s"
homeurl="/%s"%agbrdfConf.HOMEPATH
underConstructionURL=os.path.join('/',agbrdfConf.UNDERCONSTRUCTION)


objectDumpURL="/%s/"%agbrdfConf.CGIPATH + "fetch.py?obid=%s&context=%s"
listChunkLink="/%s/"%agbrdfConf.CGIPATH + 'fetch.py?obid=%s&context=briefsearchsummarypage&bookmark=%s&target=ob&childview=%s&page=%s'
#imageurl="http://localhost/agbrdf/NuNZWeb/images/"



# obtain form variables and copy into a dicionary
fields = cgi.FieldStorage()
fieldDict = dict()
#for key in fields.keys():
#    fieldDict[key] = fields[key].value

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


if 'REMOTE_USER' in environ:
    fieldDict.update({"REMOTE_USER" : environ['REMOTE_USER']})
else:
    fieldDict.update({"REMOTE_USER" : 'nobody'})

fieldDict.update({'environment' : str(environ)})

fetchanalysislogger.info("initiated with %s\n\n"%str(fieldDict))

#expected fields are context, "obid" and a list containng a single analysis function to run.
# (the AJAX script loops around and rnus multiple functions , if there are > 1)
# easiest way to get set up is to instantiate the object and use the
# built-in method for grabbing all displayfunctions attached to the
# object. In fact we need an instance of the object anyway, because the
# display procedure call that we will make, refers to self.
#
# optional fields are an additional payload consisting of fields
# names datasourcennnnn - these need to be marshalled into datasourceob
# objects
connection=databaseModule.getConnection()
myObject = ob()
result=""
fetchanalysislogger.info("initialising object")

# check basic integrity of payload

if 'obid' not in fieldDict:
    errorPage("incomplete data received from client : %s"%str(fieldDict))
    sys.exit()

try:
    myObject.initFromDatabase(int(fieldDict['obid']),'ob',connection)
    fetchanalysislogger.info("object initialised OK")
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

if myObject.databaseFields['tablename'] == 'analysisprocedureob':
    myObject = analysisProcedureOb()
    myObject.username=fieldDict['REMOTE_USER']
    myObject.initFromDatabase(int(fieldDict['obid']),connection)
    myObject.initMetadata(connection)
    myObject.discoverLinks(connection)
    myObject.initComments(connection)
    myObject.initHyperLinks(connection)                        
    myObject.initListMembership(connection)                        
    myObject.initAnalysisFunctions(connection)
elif myObject.databaseFields['tablename'] == 'geneexpressionstudy':
    myObject = geneExpressionStudy()
    myObject.username=fieldDict['REMOTE_USER']
    myObject.initFromDatabase(int(fieldDict['obid']),connection)
    myObject.initMetadata(connection)
    myObject.discoverLinks(connection)
    myObject.initComments(connection)
    myObject.initHyperLinks(connection)
    myObject.initListMembership(connection)
    myObject.initAnalysisFunctions(connection)
elif myObject.databaseFields['tablename'] == 'oblist':
    myObject = obList()
    myObject.username=fieldDict['REMOTE_USER']
    myObject.initFromDatabase(int(fieldDict['obid']),connection)
    myObject.initMetadata(connection)
    myObject.discoverLinks(connection)
    myObject.initComments(connection)
    myObject.initHyperLinks(connection)
    myObject.initListMembership(connection)
    myObject.initAnalysisFunctions(connection)
elif myObject.databaseFields['tablename'] == 'datasourceob':
    myObject = dataSourceOb()
    myObject.username=fieldDict['REMOTE_USER']
    myObject.initFromDatabase(int(fieldDict['obid']),connection)
    myObject.initMetadata(connection)
    myObject.discoverLinks(connection)
    myObject.initComments(connection)
    myObject.initHyperLinks(connection)
    myObject.initListMembership(connection)
    myObject.initAnalysisFunctions(connection)
    myObject.initRelatedAnalysisFunctions(connection)
elif myObject.databaseFields['tablename'] == 'labresourceob':
    myObject = labResourceOb()
    myObject.username=fieldDict['REMOTE_USER']
    myObject.initFromDatabase(int(fieldDict['obid']),connection)
    myObject.initMetadata(connection)
    myObject.discoverLinks(connection)
    myObject.initComments(connection)
    myObject.initHyperLinks(connection)
    myObject.initListMembership(connection)
    myObject.initAnalysisFunctions(connection)
elif myObject.databaseFields['tablename'] == 'biosequenceob':
    myObject = bioSequenceOb()
    myObject.username=fieldDict['REMOTE_USER']
    myObject.initFromDatabase(int(fieldDict['obid']),connection)
    myObject.initMetadata(connection)
    myObject.discoverLinks(connection)
    myObject.initComments(connection)
    myObject.initHyperLinks(connection)
    myObject.initListMembership(connection)
    myObject.initAnalysisFunctions(connection)
else:
    raise brdfException("fetchAnalysis needs to be updated to be able to initialise %s"%myObject.databaseFields['tablename'])

# intialise the ob with the call back URL paths for this instance of the brdf
if myObject.obState['METADATA'] == 1:
    myObject.columnAliases = getColumnAliases(connection, myObject.metadataFields['tablename'])
            
myObject.fetcher=fetcher
myObject.displayfetcher=displayfetcher
myObject.analysisfetcher=analysisfetcher
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

# marshall any additional payload into datasourceobjects
dynamicDataSources = None
for key in fieldDict.keys():
    match = re.search("^datasource([0123456789]+)$", key)
    if match != None:
        if dynamicDataSources == None:
            dynamicDataSources = []
        fetchanalysislogger.info("marshalling payload for data source %s"%match.groups()[0])
        source = dataSourceOb()
        source.databaseFields = {
           'obid' : int(match.groups()[0]), 
           'xreflsid' : 'volatile',
           'datasourcetype' : 'Other',
           'datasourcecontent' :  fieldDict[key]
        }
        dynamicDataSources.append(source)
         


    
#test = testPage(fieldDict
fetchanalysislogger.info("running analysis proc : %s"%fieldDict['functioninstance'])
result = myObject.runAnalysisFunctions(connection,functionList = [fieldDict['functioninstance']],context=fieldDict['context'],dynamicDataSources=dynamicDataSources)

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





