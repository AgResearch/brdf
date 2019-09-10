#!/usr/bin/env python
#-----------------------------------------------------------------------+
# Name:		fetchSelectList.py		                        |
#									|
# Description:	This CGI script  handles AJAX style requests for a      |
# select list fragment , which will be merged in the calling HTML page  |
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
import agbrdfConf
import databaseModule

from agresearchPages import testPage, fetchPage
from obmodule import ob,getColumnAliases
from studyModule import microarrayObservation
from displayProcedures import getExpressionMapDisplay,getGenepixThumbnailDisplay
from brdfExceptionModule import brdfException


import logging


""" logging - comment out when not required """
# set up logger if we want logging
fetchselectlistlogger = logging.getLogger('fetchselectlist')
fetchselectlisthdlr = logging.FileHandler(os.path.join(globalConf.LOGPATH,'agbrdf_fetchselectlist.log'))
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
fetchselectlisthdlr.setFormatter(formatter)
fetchselectlistlogger.addHandler(fetchselectlisthdlr) 
fetchselectlistlogger.setLevel(logging.INFO)

# we need the same constants as the pages module.
fetcher="/%s/fetch.py"%agbrdfConf.CGIPATH
displayfetcher="/%s/fetchSelectList.py"%agbrdfConf.CGIPATH
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

fetchselectlistlogger.info("initiated with %s\n\n"%str(fieldDict))

connection=databaseModule.getConnection()
listcur = connection.cursor()
fetchselectlistlogger.info("running selectlist proc : %s"%fieldDict['listname'])
result = ""

# expect to receive : 
# listname
#  for arrayslides list report 
#  obid  (of array)
#  xreflsid  (of array)
#
#
if fieldDict['listname'] == "arrayslides":
   sql = """
   select
      ges.xreflsid ,
      coalesce(ges.xreflsid || ' : ' || studydescription,ges.xreflsid) as description ,
      lr.xreflsid
   from
      (geneexpressionstudy ges join labresourceob lr on lr.obid = ges.labresourceob) 
      left outer join geneexpressionstudyfact gesf on
      gesf.geneexpressionstudy = ges.obid and
      gesf.factnamespace = 'BRDF Default Interface Configuration' and
      gesf.attributename = 'Bar graph experiment order'
   where
      labresourceob = %(obid)s
   order by
      to_number(gesf.attributevalue,'999999'), ges.xreflsid
   """
   fetchselectlistlogger.info("executing  : %s"%sql%fieldDict)
   listcur.execute(sql,fieldDict)
   row = listcur.fetchone()
   if listcur.rowcount == 0:
      result = "** no slides have been entered for this array **"
   else:
      fieldDict['xreflsid'] = row[2]
      result = """Select slides from array %(xreflsid)s
         <select name="array_%(obid)s"  multiple size=4>
      """%fieldDict
      while row != None:
         result += """
         <option value="%s"> %s </option>"""%(row[0],row[1])
         row = listcur.fetchone()

      result += '\n</select><br/>';

   listcur.close()
   connection.close()
   fetchselectlistlogger.info(result)


   print "Content-Type: text/html\n\n"
   print result

else:
   print " *** error - unsupported list %s ***"%fieldDict['listname']

