#!/usr/bin/python
#-----------------------------------------------------------------------+
# Name:		fetchGeneticTestInfo.py				        |
#									|
# Description:	This CGI script  handles AJAX style requests for a      |
# fragment of information about a SNP , which will be merged in         |
#	                                                                |
#=======================================================================|
# Revision History:							|
#									|
# Date      Ini Description						|
# --------- --- ------------------------------------------------------- |
# 9/2008    AFM  initial version                                        |
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
import databaseModule

from agresearchPages import testPage, fetchPage
from obmodule import ob,getColumnAliases
from brdfExceptionModule import brdfException
from labResourceModule import geneticTestFact
from htmlModule import pageWrap


import logging


""" logging - comment out when not required """
# set up logger if we want logging
fetchgenetictestinfologger = logging.getLogger('fetchgenetictestinfo')
fetchgenetictestinfohdlr = logging.FileHandler(os.path.join(globalConf.LOGPATH,'agbrdf_fetchgenetictestinfo.log'))
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
fetchgenetictestinfohdlr.setFormatter(formatter)
fetchgenetictestinfologger.addHandler(fetchgenetictestinfohdlr) 
fetchgenetictestinfologger.setLevel(logging.INFO)

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
for key in fields.keys():
    fieldDict[key] = fields[key].value

if 'REMOTE_USER' in environ:
    fieldDict.update({"REMOTE_USER" : environ['REMOTE_USER']})
else:
    fieldDict.update({"REMOTE_USER" : 'nobody'})

fieldDict.update({'environment' : str(environ)})

fetchgenetictestinfologger.info("initiated with %s\n\n"%str(fieldDict))

#expected required fields are context, xreflsid and field
# field can be one of : 
#
# comments
# variation
# primers
connection=databaseModule.getConnection()
myObject = ob()
result=""
fetchgenetictestinfologger.info("initialising object")
try:
    myObject.initFromDatabase(fieldDict['xreflsid'],'ob',connection)
except:
    raise brdfException("object not found : %s" % fieldDict['xreflsid'])        

if myObject.databaseFields['tablename'] == 'genetictestfact':
    myObject = geneticTestFact()
    myObject.username=fieldDict['REMOTE_USER']
    myObject.initFromDatabase(fieldDict['xreflsid'],connection)
    myObject.initMetadata(connection)
    myObject.discoverLinks(connection)
    myObject.initComments(connection)
    myObject.initHyperLinks(connection)                        
    myObject.initListMembership(connection)                        
else:
    raise brdfException("fetchAnalysis needs to be updated to be able to initialise %s"%myObject.databaseFields['tablename'])

# intialise the ob with the call back URL paths for this instance of the brdf
# don't really need this stuff but may as well complete the job
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


    
#test = testPage(fieldDict
table=""
if fieldDict["infotype"] == "comments":
    commentRows =  reduce(lambda x,y:x+y, ['<tr><td>by '+commenttuple[3]+ ' on ' + commenttuple[2].strftime("%d/%m/%y")+'</td><td bgcolor='+commenttuple[4]+'><b><i>'+commenttuple[1]+'</i></b></td></tr>\n' \
                                                   for commenttuple in myObject.commentFields],'')
    commentRows = '<tr><td colspan="2"><table border="0">' + commentRows + '</table></td></tr>'

    table = """
            <tr class=%s>
            <td colspan=2>
            <table class=%s>
            <tr>            
            <!-- <tr bgcolor=#388fbd> -->
            <td align=left >
            <a name="comments" class=whiteheading>
            Comments on %s
            </a>
            </td>
            <td align=right>
            <a class="CSSCommentButton" href="%s" target="AddComment">Add a comment</a>              
            </td>
            </tr>
            </table>
            </td>            
            </tr>
            """%(myObject.theme["section heading class"],myObject.theme["section heading class"],fieldDict['xreflsid'],myObject.addCommentURL%(fieldDict["context"],myObject.databaseFields['obid'],\
                                     myObject.databaseFields['xreflsid']))
    table += commentRows
elif fieldDict["infotype"] == "variation":
    table = """
    %s Variation = %s
    """%(fieldDict['xreflsid'],myObject.databaseFields["variation"])
else:
    table = """
    Unknown information type requested : %s
    """%fieldDict["infotype"]

#print table
print pageWrap("",table)
