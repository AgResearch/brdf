#!/usr/bin/env python
#-----------------------------------------------------------------------+
# Name:         form.py                                                 |
#                                                                       |
#=======================================================================|
# Copyright 2005 by AgResearch (NZ).                                    |
# All rights reserved.                                                  |
#                                                                       |
#=======================================================================|
# Revision History:                                                     |
#                                                                       |
# Date      Ini Description                                             |
# --------- --- ------------------------------------------------------- |
# 3/2006    AFM  initial version                                        |
# 02/2005   JSM  updated the imports from agresearchForms, and added    |
#                  handling for the forms based on the formname param.  |
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
from os import environ

from agresearchForms import commentForm, uriForm, AgResearchSequenceSubmissionForm,fileSubmissionForm, \
 microarrayProtocolForm, microarraySubjectForm, microarraySampleForm, microarrayFileForm, \
 microarraySeriesForm, microarrayContrastForm, microarrayDocumentForm, editAnalysisProcedureForm, \
 defineArrayHeatMapForm

from agresearchPages import errorPage, testPage

agbrdfcgimodulelogger = logging.getLogger('cgi')
agbrdfcgimodulehdlr = logging.FileHandler(os.path.join(globalConf.LOGPATH,'agresearchcgi.log'))
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
agbrdfcgimodulehdlr.setFormatter(formatter)
agbrdfcgimodulelogger.addHandler(agbrdfcgimodulehdlr) 
agbrdfcgimodulelogger.setLevel(logging.INFO)   


# obtain form variables and copy into a dicionary
fields = cgi.FieldStorage()
agbrdfcgimodulelogger.info(fields)
fieldDict = dict()
#microarrayForm = False
#if fields['formname'].value.startswith('microarray') or fields['formname'].value.startswith('Microarray'):
#    microarrayForm = True

for key in fields.keys():
    if key.startswith("external_filename") or \
    (key.startswith("file") and key != 'fileCount' and key != 'files' and not key.startswith("fileType")) :
        fieldDict[key] = fields[key].file.read()
        fieldDict[key+".filename"] = fields[key].filename
    elif isinstance(fields[key],ListType):
        if fields['formname'].value not in  ["AgResearchSequenceSubmissionForm", "fileSubmissionForm"]:
            # we'll have to see if this breaks anything
            #fieldDict[key] = fields[key] # before 12/8/2008

            # now this..
            instanceCount = 0
            listValue = []
            for item in fields[key]:
                #fieldName = "%s_%s"%(item.name,instanceCount)
                listValue.append(item.value)
                #fieldDict[fieldName] = item.value
                instanceCount += 1
            fieldDict[key] = listValue

            
        else :
            # not actually sure now which forms use this odd way of handling lists - I think it is at most the above two  
            agbrdfcgimodulelogger.info("List : ")
            agbrdfcgimodulelogger.info(fields[key])
            instanceCount = 0
            for item in fields[key]:
                fieldName = "%s_%s"%(item.name,instanceCount)
                fieldDict[fieldName] = item.value
                instanceCount += 1
                agbrdfcgimodulelogger.info("(added %s = %s)"%(fieldName, item.value))
    else:
        fieldDict[key] = fields[key].value

if 'REMOTE_USER' in environ:
    fieldDict.update({"REMOTE_USER" : environ['REMOTE_USER']})
else:
    fieldDict.update({"REMOTE_USER" : 'nobody'})      

test = testPage(fieldDict)
form = None
if fieldDict['formname'] == 'commentform':
    form = commentForm(fieldDict)
elif fieldDict['formname'] == 'fileSubmissionForm':
    form = fileSubmissionForm(fieldDict)
elif fieldDict['formname'] == 'uriform':
    form = uriForm(fieldDict)
elif fieldDict['formname'] == 'microarrayProtocolForm' or fieldDict['formname'] == 'MicroarrayForm1.htm':
    form = microarrayProtocolForm(fieldDict)
elif fieldDict['formname'] == 'microarraySubjectForm' or fieldDict['formname'] == 'MicroarrayForm2.htm':
    form = microarraySubjectForm(fieldDict)
elif fieldDict['formname'] == 'microarraySampleForm' or fieldDict['formname'] == 'MicroarrayForm3.htm':
    form = microarraySampleForm(fieldDict)
elif fieldDict['formname'] == 'microarrayFileForm' or fieldDict['formname'] == 'MicroarrayForm4.htm':
    form = microarrayFileForm(fieldDict)
elif fieldDict['formname'] == 'microarraySeriesForm' or fieldDict['formname'] == 'MicroarrayForm5.htm':
    form = microarraySeriesForm(fieldDict)
elif fieldDict['formname'] == 'microarrayContrastForm' or fieldDict['formname'] == 'MicroarrayForm6.htm':
    form = microarrayContrastForm(fieldDict)
elif fieldDict['formname'] == 'microarrayDocumentForm' or fieldDict['formname'] == 'MicroarrayForm7.htm':
    form = microarrayDocumentForm(fieldDict)
elif fieldDict['formname'] == 'AgResearchSequenceSubmissionForm':
    agbrdfcgimodulelogger.info("about to create form")   
    form = AgResearchSequenceSubmissionForm(fieldDict)
elif fieldDict['formname'] == 'editAnalysisProcedureForm':
    agbrdfcgimodulelogger.info("about to create form editAnalysisProcedureForm")   
    form = editAnalysisProcedureForm(fieldDict)
elif fieldDict['formname'] == 'defineArrayHeatMapForm':
    agbrdfcgimodulelogger.info("about to create form defineArrayHeatMapForm")
    form = defineArrayHeatMapForm(fieldDict)
else:
    errorPage("unsupported form : %s"%fieldDict['formname'])
