#-----------------------------------------------------------------------+
# Name:		analysisProcedures.py           			|
#									|
# Description:	classes that implements analysis procedures             |
#		                                                        |
#                                                                	|
#=======================================================================|
# Copyright 2005 by AgResearch (NZ).					|
# All rights reserved.							|
#									|
#=======================================================================|
# Revision History:							|
#									|
# Date      Ini Description						|
# --------- --- ------------------------------------------------------- |
# 2/2008    AFM  initial version                                        |
#-----------------------------------------------------------------------+
import sys
from types import *
import csv
import re
import os
import math
import random
from datetime import date
from time import time
import globalConf
#import agbrdfConf #<------------------ !!!!!!!!!! for testing only , remove !!!!!!!!!!!!!!!!!!!!
from obmodule import ob,getObjectRecord,getNewObid
from opmodule import op
from htmlModule import tidyout, defaultMenuJS
from brdfExceptionModule import brdfException
from imageModule import makeOpGlyph, makeBarGraph,getJPEGThumbs,getColourScheme
from annotationModule import uriOb
from dataImportModule import dataSourceList, dataSourceOb
from listModule import obList
import databaseModule
import logging
import os.path
import stat
import commands
import string


# set up logger if we want logging
analysismodulelogger = logging.getLogger('analysisProcedures')
analysismodulehdlr = logging.FileHandler(os.path.join(globalConf.LOGPATH,'analysisProcedures.log'))
#hdlr = logging.FileHandler('c:/temp/sheepgenomicsforms.log')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
analysismodulehdlr.setFormatter(formatter)
analysismodulelogger.addHandler(analysismodulehdlr) 
analysismodulelogger.setLevel(logging.INFO)        

""" --------- module variables ----------"""


""" --------- module methods and classes ------------"""


class analysisProcedureOb ( ob ) :
    def __init__(self):
        ob.__init__(self)


    def initNew(self,connection):
        self.obState.update({'NEW' : 1, 'DB_PENDING' : 1})        
        self.databaseFields = {
            'obid' : getNewObid(connection) ,
            'xreflsid' : None,
            'procedurename' : None,
            'author' : None,
            'authordate' : None,
            'sourcecode' : '',
            'procedurenescription' : None,
            'procedurecomment' : None,
            'proceduretype' : None,
            'invocation' : None,
            'presentationtemplate' : None ,
            'textincount' : None,
            'textoutcount' : None,
            'imageoutcount' : None,
            'lastupdatedby' : ''}
        

    def initFromDatabase(self, identifier, connection):
        """ method for initialising bioProtocolOb from database """

        # first init base class - this will get obid
        ob.initFromDatabase(self, identifier, "analysisProcedureOb", connection)

        # now get the complete object
        self.databaseFields = getObjectRecord(connection, "analysisProcedureOb", self.databaseFields['obid'])


    def updateDatabase(self,connection):
        """ method used by analysisPocedure object to update itself """
        sql = """
            update analysisProcedureOb set
            sourcecode  = %(sourcecode)s,
            presentationtemplate = %(presentationtemplate)s,
            procedurecomment = coalesce(procedurecomment || '\r' || now() || ' : ' || %(procedurecomment)s, now() || ' : ' || %(procedurecomment)s),
            lastupdateddate = now(),
            lastupdatedby = %(lastupdatedby)s,
            textincount = %(textincount)s,
            textoutcount = %(textoutcount)s,
            imageoutcount = %(imageoutcount)s
            where obid = %(obid)s
            """
        #print "executing " + sql%self.databaseFields
        updateCursor = connection.cursor()
        analysismodulelogger.info("executing %s"%str(sql%self.databaseFields))
        updateCursor.execute(sql,self.databaseFields)
        connection.commit()
        updateCursor.close()
        self.obState.update({'NEW' : 0 , 'ERROR' : 0, 'DB_PENDING' : 0, 'MESSAGE' : "database update OK"})
        return


    def getSourceCodeFileName(self,savepath):
        """ method used by analysisPocedure object to save code to a file and return the file name. It hashes the
        source code and makes the hash part of the filename , and will only write the file if it does not exist """
        hashconstant = '1' # increment this to force refresh of caches
        filename = "%s.%s"%( str(abs(hash(hashconstant + self.databaseFields['sourcecode']))) , self.databaseFields['procedurename'])
        filepath = os.path.join(savepath,filename)

        if not os.path.exists(filepath) :
            writer = open(filepath,"w")
            writer.write(self.databaseFields['sourcecode'])
            writer.close()

        return filepath
    

    def insertDatabase(self,connection):
        """ method used by analysisProcedureOb object to save itself to database  """
        sql = """
        insert into analysisProcedureOb(obid,xreflsid,procedurename,author,authordate,sourcecode,
            proceduredescription,procedurecomment,proceduretype,invocation,presentationtemplate,
            lastupdatedby) values(%(obid)s,%(xreflsid)s,%(procedurename)s,%(author)s,%(authordate)s,%(sourcecode)s,
            %(proceduredescription)s,%(procedurecomment)s,%(proceduretype)s,%(invocation)s,%(presentationtemplate)s,%(lastupdatedby)s)
        """
        #print "executing " + sql%self.databaseFields
        insertCursor = connection.cursor()
        insertCursor.execute(sql,self.databaseFields)
        connection.commit()
        insertCursor.close()
        self.obState.update({'NEW' : 0 , 'ERROR' : 0, 'DB_PENDING' : 0, 'MESSAGE' : "database insert OK"})
        return
    def getMenuBarJS(self, metadata, context) :
        """ method for displaying the fancy edit/annotate/help menu-bar """
        #Edit | Annotate | View | Tools | Help
        #Get the "defaultMenuJS" string from htmlModule, and set "dynamicMenuJS" for this instance
        
        if metadata == 1 :
            helpchunk = "return brdfpopup(\"%s\",\"%s\")"%('%s %s'%(self.metadataFields['displayname'],self.databaseFields['obid']),self.makeAboutMe(context))
        else :
            helpchunk = "return brdfpopup(\"%s\",\"%s\")"%('BRDF Object %s'%self.databaseFields['obid'],self.makeAboutMe(context))
        
        menuDict = {'helpchunk' : helpchunk,
                    'addCommentURL' : self.addCommentURL%(context,self.databaseFields['obid'],self.databaseFields['xreflsid']),
                    'addLinkURL' : self.addLinkURL%(context,self.databaseFields['obid'],self.databaseFields['xreflsid']),
                    'editURL' : self.editURL%self.databaseFields}
        
        dynamicMenuJS=r"""
        function unimplemented(opt) {
            hideMenu();
            window.alert("Sorry, this option hasn't been implemented yet - please contact Alan McCulloch " + 
                         "(alan.mcculloch@agresearch.co.nz) if you want to be able to " + opt + ".");
        }
        
        function helpButton() {
            hideMenu();
            %(helpchunk)s;
        }
        
        function annotateButton(link) {
            hideMenu();
            return location.href=link;
        }
            
        function editButton(anchor) {
            hideMenu();
            window.open("%(editURL)s"+anchor);
            // modified 1/8/2008 to cause the edit form to open in a new window
            //return location.href="%(editURL)s"+anchor;
        }
        
        var editItemArray = new Array();
        editItemArray[0] = new Array("editButton(\"\");","Edit / Create Procedure");
        
        var annotateItemArray = new Array();
        annotateItemArray[0] = new Array("annotateButton(\"%(addCommentURL)s\");","Add Comment");
        annotateItemArray[1] = new Array("annotateButton(\"%(addLinkURL)s\");","Add Hyperlink");
        
        var viewItemArray = new Array();
        viewItemArray[0] = new Array("unimplemented(\"view this sequence as FASTA\");","as FASTA");
        viewItemArray[1] = new Array("unimplemented(\"view this sequence as Genbank\");","as Genbank");
        
        var toolsItemArray = new Array();
        //toolsItemArray[0] = new Array("unimplemented(\"open this sequence in Vector NTI\");","open in Vector NTI");
        //toolsItemArray[1] = new Array("unimplemented(\"BLAST against this sequence\");","BLAST");
        
        var helpItemArray = new Array();
        helpItemArray[0] = new Array("helpButton();","Help");
        """%menuDict
        
        return defaultMenuJS%dynamicMenuJS
    


    def myHTMLSummary(self, table, width=800,context='default'):
        """ descendants of the ob class will usually override this method rather than the
        entire asHTMLRows method - this method supplies the contents of the summary
        panel
        """
        FieldItems = [item for item in self.databaseFields.items() if not isinstance(item[1],ListType)]
        ListItems = [item for item in self.databaseFields.items() if isinstance(item[1],ListType) and len(item[1]) > 0]           
        ListDictionaryItems = [item for item in ListItems if isinstance(item[1][0],DictType)]
        ListOtherItems = [item for item in ListItems if not isinstance(item[1][0],DictType)]        
        nonSystemFieldRows =  reduce(lambda x,y:x+y, ['<tr><td class=fieldname>'+self.getColumnAlias(key)+'</td><td class=fieldvalue>'+tidyout(str(value), 80, 1,'<br/>')[0]+'</td></tr>\n' \
                                                   for key,value in FieldItems if not key in ( \
                                        'obid','obtypeid','createddate','createdby','lastupdateddate',\
                                        'lastupdatedby','checkedout','checkedoutby','checkoutdate','obkeywords',\
                                        'presentationtemplate','sourcecode','statuscode') and self.getColumnAlias(key) != None])
        nonSystemFieldRows = '<tr><td class=inside colspan="2"><table class=inside border="0">' + nonSystemFieldRows + '</table></td></tr>'
        # Format output for values that are lists of dictionaries
        # in the next line, the inner reduction concatenates the keys and values for a dictionary - e.g. a single
        # function or location , for a gene object.
        # the next reduction out concatnates these for each dictionary in the list (i.e. each location, function or whatever etc)
        # the final reduction concatenates each category name with all the above - e.g function : location : etc     
        ListDictionaryRows = ''
        if len(ListDictionaryItems) > 0 :
            ListDictionaryRows =  reduce(lambda x,y:x+y, ['<tr><td><b>'+key +'</b></td><td>'+\
                                '<table>'+ \
                                    reduce(lambda x,y:x+y , [ \
                                        reduce(lambda x,y:x+y, ['<tr><td><i>'+nestedkey+'</i></td><td><b>'+\
                                                str(nestedvalue)+'</b></td></tr>\n' \
                                        for nestedkey,nestedvalue in nestedDict.items()]) + '<p/>' \
                                    for nestedDict in value ]) + \
                                '</table>' + \
                                '</td></tr>\n' \
                                  for key,value in ListDictionaryItems])
        ListOtherRows = ''
        if len(ListOtherItems) > 0:
            ListOtherRows = reduce(lambda x,y:x+y, ['<tr><td>'+key+'</td><td>'+str(value)+'</td></tr>\n' for key,value in ListOtherItems])


        # build a select list of instances of this procedure that can be run. 
        #sql = """
        #select
        #    af.invocation,
        #    af.functioncomment,
        #    ap.xreflsid,
        #    ap.procedurename,
        #    ap.proceduretype,            
        #    af.datasourcelist,
        #    af.voptypeid,
        #    ap.proceduredescription,
        #    af.invocationorder,
        #    af.obid
        #from
        #    (analysisfunction af join analysisprocedureob ap on
        #    af.analysisprocedureob = ap.obid) left outer join
        #    datasourcelist dl on dl.obid = af.datasourcelist
        #where
        #    ap.obid = %(obid)s and
        #    
        #order by
        #    ap.procedurename,
        #    af.functioncomment
        #"""
        #connection = databaseModule.getConnection()        
        #analysismodulelogger.info('executing SQL to retrieve dynamic analysis functions : %s'%str(sql%self.databaseFields))        
        #analysisCursor = connection.cursor()
        #analysisCursor.execute(sql,self.databaseFields)
        #analysisFunctions = analysisCursor.fetchall()
        #analysisCursor.close()

        
        # initialise each analysisfunction and test security 
        if self.obState['DYNAMIC_ANALYSES'] > 0:
            connection=databaseModule.getConnection()
            accessibleFunctions = []
            for func in self.analysisFunctions:
                analysismodulelogger.info('initialising analysisfunction %s to test access '%func[9])       
                funcOb = analysisFunction()
                funcOb.initFromDatabase(func[9],connection)
                funcOb.initMetadata(connection)
                funcOb.initProtections(connection)
                funcOb.username = self.username
                if funcOb.runSecurityFunctions(resourcename="analysis procedure menu"):
                    analysismodulelogger.info('adding accessible function %s'%funcOb.databaseFields['xreflsid'])        
                    accessibleFunctions.append(func)

            # create the dynamic data section. Item 11 of each function signature is markup containing
            # elements used to acquire user input for the function. The section uses a div element with
            # id equal to the datasource id
            userInputHTML = ''
            if len(accessibleFunctions)  > 0:
                for func in self.analysisFunctions:
                    myElements = func[11]
                    if myElements == None:
                        myElements = ""
                    myHeading = ""
                    if len(myElements) > 0:
                        myHeading = """
                        <SPAN STYLE="background-color: #ffffcc; color:orange">Specify Parameters for %s</SPAN>
                        """%func[1]
                    myInput = """
                    <div id=%s style="display:none">
                    <form name="form%s" id="form%s">
                    %s
                    <p/>
                    %s
                    </form>
                    </div>
                    """%(func[9],func[9],func[9],myHeading,myElements)
                    userInputHTML += myInput

            
                    
                    
            if len(accessibleFunctions)  > 0:
                selectlisttuples = ["<option value=%s> %s : %s </option>"%(item[9], item[3], item[1]) for item in accessibleFunctions ]
                selectlisthtml = """
                <tr>
                <td colspan=2 align=left>
                <script language="JavaScript1.2">
                function showAnalysisUserInput(selectelement) {
                   for(i=0 ; i<selectelement.options.length; i++) {
                      if(selectelement.options[i].selected) {
                         document.getElementById(selectelement.options[i].value).style.display = 'block';
                      }
                      else {
                         document.getElementById(selectelement.options[i].value).style.display = 'none';
                      }
                   }
                }
                </script>
                <font size="-1"> (to select multiple analyses press the control key and click. To select a block use the shift key and click) </font> <p/>
                <select name="analyses" id="analyses" multiple size=4 onchange=showAnalysisUserInput(this)>
                """\
                +reduce(lambda x,y:x+y+'\n',selectlisttuples,'')\
                + """
                </select>
                """\
                + userInputHTML \
                + """
                <p/>
                <input value="Run Analyses" type="button" id="runanalyses" onclick='multipost("%s","analyses","fetchedanalyses","context=%s&amp;obid=%s&amp;functioninstance=","%s","%s",this)'></p>         
                <p/>
                </td>
                </tr>
                """%(self.analysisfetcher,context,self.databaseFields['obid'],self.waitURL,self.waiter)

                table += """
                    <tr> <td colspan="2" class=tableheading> 
                    %s
                    </td>
                    </tr>
                    """%"Run selected analyses"                    
                table +=   selectlisthtml
                table += """
                        <tr>
                        <td>
                        <div id="fetchedanalyses">
                        </div>
                        </td>
                        </tr>
                    """            

        if self.obState['DYNAMIC_DISPLAYS'] > 0:
            analysismodulelogger.info('running non-virtual display functions')
            for displayFunction in self.displayFunctions:
                # exclude virtual functions - these will be instantiated in specific contexts or subclasses
                if displayFunction[7] == None:
                    analysismodulelogger.info('running %s'%displayFunction[0])
                    myGraphHTML = eval(displayFunction[0])
                    table += myGraphHTML        

        
        analysismodulelogger.info('listing dictionaries')
        # if we have formatted dictionaries , output these first , they are usually the most interesting
        # content of the object
        if len(ListDictionaryRows) >  0:
            table += ListDictionaryRows

        analysismodulelogger.info('listing fields')
        # next the field rows
        table += nonSystemFieldRows

        analysismodulelogger.info('listing lists')
        # next the other lists
        if len(ListOtherRows) > 0:
            table += ListOtherRows

        return table

class analysisFunction ( op ) :
    """ sequencing function """
    def __init__(self):
        op.__init__(self)


    #def initNew(self,connection):

    def initFromDatabase(self, identifier, connection):
        """ method for initialising sequencing function from database """

        # first init base class - this will get obid
        ob.initFromDatabase(self, identifier, "analysisFunction", connection)

        # now get the complete object
        self.databaseFields = getObjectRecord(connection, "analysisFunction", self.databaseFields['obid'])

        # at some point maybe add retrieval of any associated feature attributs


def marshallAnalsyisDataSource(datasourceob=None, targetfolder='', targetfilename = '', uncompress=False, bin="/usr/bin"):
    """ this method is similar to the marshallBFile method , however this method obtains the
    source file name from the database. It the uncompress option is set it will try to uncompress the
    source to obtain the temp file, rather than copy it.
    """

    connection=databaseModule.getConnection()
    dataCursor=connection.cursor()
    sql ="""
    select
    physicalsourceuri
    from
    datasourceob
    where
    obid = %s"""%datasourceob
    dataCursor.execute(sql)
    source = dataCursor.fetchone()
    source = source[0]
    connection.close()

    if not uncompress:
        
        BUFSIZE=2048

        # check source file exists - exception if not
        if not os.path.exists(source):
            raise brdfException("marshallDataSource : %s does not exist"%source)

        # get suffix
        suffix = ''
        basename = os.path.basename(source)
        tokens = re.split('\.',basename)
        if len(tokens) > 0:
            suffix = tokens[-1]
            

        
        # calculate the hash of the args which will be the temp file name
        if len(targetfilename)  > 0:
            tempfilename = targetfilename
        else:
            tempfilename = "%s.%s"%(str(abs(hash(  source+targetfolder+targetfilename))), suffix)


        target = os.path.join(targetfolder,tempfilename)


        analysismodulelogger.info("marshallDataSource is checking if  %s => %s"%(source,target))

        # see if the temp file exists
        if not os.path.exists(target):
            fin = None
            fout = None
            try:
                analysismodulelogger.info("marshallDataSource is copying %s -> %s"%(source,target))
                fin = file(source,"rb")
                fout = file(target,"wb")
                buf = fin.read(BUFSIZE)
                while len(buf) > 0:
                    fout.write(buf)
                    buf = fin.read(BUFSIZE)
            finally:
                if fin != None:
                    fin.close()
                if fout != None:
                    fout.close()

                

        return tempfilename
    else:
        # try .gz and .zip  - give up if not these, just do a non-compressed process
        prog = ""
        args = ""
        taget = ""
        if re.search('\.gz$',source) != None:
            prog = "gunzip"
            args = " -c %s > %s"
            target = re.split('\.gz',source)[0]
        elif re.search('\.zip$',source) != None:
            prog = "unzip"
            args = " -c %s > %s"
            target = re.split('\.zip',source)[0]
        else:
            return marshallDataSource(datasourceob, targetfolder, targetfilename , uncompress=False)

        tempfilename = os.path.basename(target)
        target = os.path.join(targetfolder,tempfilename)

        if not os.path.exists(target):        

            # uncompress
            prog = os.path.join(bin,prog)
            cmd = prog + args
            cmd = cmd%(source,target)

            analysismodulelogger.info("marshallDataSource is executing %s"%cmd)
            status, output = commands.getstatusoutput(cmd)
            analysismodulelogger.info("Output: %s"%output)
            analysismodulelogger.info("Status: %s"%status)
            analysismodulelogger.info("Returning: %s"%tempfilename)

        
        return tempfilename


def runProcedure(connection, bindinginfo=None , ob=None, obtype='analysisProcedureOb', usercontext="default", fetcher=None, imagepath=None, tempimageurl=None, \
                              sectionheading="",scriptname=None,cachePersistency=0,textoutputs=1,imageoutputs=0,quoteArgs=True,parameterDataSources=None,\
                              externalSource = False, dynamicDataSources=None):

    """ An analysis procedure is attached to an object, and any data sources it requires,
by creating a record in the analysisfunction table.

The brdf system will choose an appropriate handler for the analysis function call - for 
example if the procedure type is "R procedure" , then the handler method, 
in the analysisProcedures module , will be runProcedure. This will  

1. perform any datasource marshalling that is required, as specified by the datasourcelist. 
   For example in the case of  a series of SQL queries - run each query and write to a temporary file

2. parse the presentationTemplate, and calculate any output filenames
   required for mixed / multimedia output.

   Currently it is assumed that the instantiated template will be
   rendered in-line in an HTML document - i.e. it just consists of an
   HTML fragment.

   Here is an example template : 

   <!----- begin -------/>
   <pre>
   __stdout__     # stdout will be merged here
   </pre>

   <pre>
   __stderr__     # stderr will be merged here
   <pre>


   <pre>
   __myout1__     # output file 1 will be merged here
   <pre>

   <pre>
   __myout2__     # output file 2 will be merged here
   <pre>


   <img src=__mypng1__/>
   <img src=__mypng2__/>

   <!----- end --------/>


for example , the combination of the datasource list, and the presentation template, 
may cause the following invocation to be compiled

./runRProcedure.sh ./myanalysis.r datasource1 datasource2 textout1.txt textout2.txt 14323.png 56765.png 

- the runRprocedure will have marshalled the indicated datasources ; the R code will 
output to the supplied file names ; the runRprocedure will return an instantiated presentationTemplate
to the caller, merging stdout and stderr , and opening the text output to merge into the template as indicated, and 
replace the image file-name placeholders with the actual temporary file names


    test example :

    [nutrigen@imp03 nutrigenomics]$ pwd
/var/www/cgi-bin/nutrigenomics

Rscript --vanilla snp.analysis.r

"""

    # process the data sources 
    dsl = dataSourceList()

    if parameterDataSources == None:
        if bindinginfo[5] != None: 
            dsl.initFromDatabase(int(bindinginfo[5]),connection)
            analysismodulelogger.info("initialised datasource list  %(xreflsid)s"%dsl.databaseFields)
        elif bindinginfo[10] != None:
            dsl.databaseFields={}
            dsl.databaseFields['dataSources'] = []    
            ds = dataSourceOb()
            ds.initFromDatabase(int(bindinginfo[10]),connection)
            dsl.databaseFields['dataSources'].append(ds)
        else:
            raise brdfException("neither parameter data source, datasource or datasource list defined")
    else:
        dsl.databaseFields={}
        dsl.databaseFields['dataSources'] = []
        for pds in parameterDataSources:
            ds = dataSourceOb()
            ds.databaseFields = {}
            ds.databaseFields.update(pds)
            dsl.databaseFields['dataSources'].append(ds)           

    # get the analysisprocedure
    ap = analysisProcedureOb()
    ap.initFromDatabase(bindinginfo[2],connection)

    hashconstant = '8' # increment this to force refresh of caches

    # intialise hashes to construct each text output file name
    textoutputfiles=[hashconstant + str(item) for item in range(0,textoutputs)]
    
    # initialise hashes to construct each image output file name
    imageoutputfiles=[hashconstant + str(item) for item in range(0,imageoutputs)]

    # for each datasource in the list , process it and 
    # output to a temp file
    inputfiles = [] 
    inputfilenames = [] 
    inputphrase = ''
    parameterphrase = ''
    for datasource in dsl.databaseFields['dataSources']:
        if type(datasource) is IntType: 
           ds = dataSourceOb()
           analysismodulelogger.info("initialising datasource using %s"%datasource)
           ds.initFromDatabase(int(datasource),connection)
        else:
           ds = datasource

        # if the data source has type "USER PROMPT", then ignore it
        #if ds.databaseFields["dynamiccontentmethod"] !=  None:
        #    if ds.databaseFields["dynamiccontentmethod"].upper() == "USER PROMPT":
        #        continue

        # some data sources may have been populated dyamically from user input.
        # - this data is supplied via the dyamicDataSources argument
        if dynamicDataSources != None:
            analysismodulelogger.info("checking dynamic data sources")
            for dynamicSource in dynamicDataSources:
                if dynamicSource.databaseFields['obid'] == ds.databaseFields['obid']:

                    # we either replace or merge the dynamic data into the static data. Whether we replace or merge
                    # is controlled by the dynamicContentMethod variable

                    if ds.databaseFields['dynamiccontentmethod'] == 'Merge User Prompt':
                        # the merge method depends on the data source type
                        analysismodulelogger.info("merging dynamic content for %(xreflsid)s"%ds.databaseFields)
                        if ds.databaseFields['datasourcetype'] in ['SQL', 'SQL (no header)']:
                            # example :
                            #select
                            #   msf.gal_genename as gene,
                            #   l.affygene,
                            #   l.inputfile,
                            #   l.anml_key as animal_key,
                            #   l.expression
                            #from
                            #
                            #   microarrayspotfact msf join licexpression1 l
                            #   on l.affygene = msf.gal_name
                            #where
                            #   msf.labresourceob = 42373311 and
                            #   msf.gal_genename in    (
                            #        _list_of_string_
                            #)

                            if re.search("_list_of_string_",ds.databaseFields["datasourcecontent"]) != None:
                                analysismodulelogger.info("attempting to merge data source")
                                stringlist = re.split('[\n\r]+',dynamicSource.databaseFields['datasourcecontent'])
                                if stringlist != None:
                                    # escape and existing strings
                                    stringlist = ["'%s'"%re.sub("'","''",item) for item in stringlist if len(item) > 0]
                                    ds.databaseFields["datasourcecontent"] = re.sub("_list_of_string_",string.join(stringlist,','),ds.databaseFields["datasourcecontent"],1)
                            elif re.search("_temp_list_id_",ds.databaseFields["datasourcecontent"]) != None:
                                analysismodulelogger.info("attempting to cache datasource content to list")
                                mylist = obList()
                                mylist.initNew(connection)
                                mylist.databaseFields["listtype"] = "TEMPWEAKLIST"
                                mylist.databaseFields["xreflsid"] = "tempweaklist.datasourcecache.%s"%dynamicSource.databaseFields["xreflsid"]
                                mylist.databaseFields["listname"] = dynamicSource.databaseFields["xreflsid"]
                                mylist.insertDatabase(connection)
                                stringlist = re.split('[\n\r]+',dynamicSource.databaseFields['datasourcecontent'])
                                for member in stringlist:
                                    if member != None:
                                        if len(member.strip()) > 0:
                                            mylist.addWeakListMember(member.strip(),None,connection,voptype=None,checkExisting = False)
                                ds.databaseFields["datasourcecontent"] = re.sub("_temp_list_id_",str(mylist.databaseFields["obid"]),ds.databaseFields["datasourcecontent"],1)

                            # example :
                            #select
                            #   msf.gal_genename as gene,
                            #   l.affygene,
                            #   l.inputfile,
                            #   l.anml_key as animal_key,
                            #   l.expression
                            #from
                            #
                            #   (microarrayspotfact msf join licexpression1 l
                            #   on l.affygene = msf.gal_name) join listmembershipfact ltemp on
                            #   ltemp.memberid = msf.gal_genename
                            #where
                            #   msf.labresourceob = 42373311 and
                            #   lmtemp.oblist =  _temp_list_id_
                            #)

                                    
                        else:
                            raise brdfException("unsupported data source type for merge")
                            
                    else:
                        analysismodulelogger.info("setting dynamic content for %(xreflsid)s"%ds.databaseFields)
                        ds.databaseFields['datasourcecontent'] = dynamicSource.databaseFields['datasourcecontent']
                        
                    

            
        
        analysismodulelogger.info("processing data source %s"%str(ds.databaseFields))
        analysismodulelogger.info("checking %(xreflsid)s"%ds.databaseFields)
        if ds.databaseFields['datasourcetype'].upper() in ['TAB DELIMITED','CSV','TAB DELIMITED TEXT','R WORKSPACE','FASTA']:
            # if datasourcecontent is not null, then we may need to cache this as a file to make available to script
            if ds.databaseFields['datasourcecontent'] != None:
                if ap.databaseFields['proceduretype'] == 'SQL Query':
                    # for SQL queries we bind the data source information to the query - either by editing the
                    # query source code, or by writing the data to a table
                    #
                    # if the query code contains the token _LIST_OF_STRING_
                    # then we parse the content as such and bind to the query. The query
                    # can contain multiple of these tokens - each will be matched up with a data source,
                    # in order
                    if re.search("_list_of_string_",ap.databaseFields["sourcecode"]) != None:
                        analysismodulelogger.info("attempting to bind query")
                        stringlist = re.split('[\n\r]+',ds.databaseFields['datasourcecontent'])
                        if stringlist != None:
                            # escape and existing strings
                            stringlist = ["'%s'"%re.sub("'","''",item) for item in stringlist]
                            ap.databaseFields["sourcecode"] = re.sub("_list_of_string_",string.join(stringlist,','),ap.databaseFields["sourcecode"],1)
                        else:
                            # we should have matched the token but did not - perhaps the user submitted no data.
                            # replace with an empty string
                            analysismodulelogger.info("no data - attempting to bind query using empty string")
                            ap.databaseFields["sourcecode"] = re.sub("_list_of_string_","''",ap.databaseFields["sourcecode"],1)
                    elif re.search("_temp_list_id_",ap.databaseFields["sourcecode"]) != None:
                        analysismodulelogger.info("attempting to cache data and bind query")
                        mylist = obList()
                        mylist.initNew(connection)
                        mylist.databaseFields["listtype"] = "TEMPWEAKLIST"                        
                        mylist.databaseFields["xreflsid"] = "tempweaklist.datasourcecache.%s"%ds.databaseFields["xreflsid"]
                        mylist.databaseFields["listname"] = ds.databaseFields["xreflsid"]
                        mylist.insertDatabase(connection)
                        stringlist = re.split('[\n\r]+',ds.databaseFields['datasourcecontent'])
                        if stringlist != None:
                            # escape and existing strings
                            for member in stringlist:
                                if member != None:
                                    if len(member.strip()) > 0:
                                        mylist.addWeakListMember(member.strip(),None,connection,voptype=None,checkExisting = False)
                            ap.databaseFields["sourcecode"] = re.sub("_temp_list_id_",str(mylist.databaseFields["obid"]),ap.databaseFields["sourcecode"],1)
                        else:
                            # we should have matched the token but did not - perhaps the user submitted no data.
                            # replace with an empty string
                            analysismodulelogger.info("no data - attempting to bind query using empty string")
                            ap.databaseFields["sourcecode"] = re.sub("_temp_list_id_","''",ap.databaseFields["sourcecode"],1)
                                                        
                else:
                    # for other queries we marshall the data to an output file
                    filename = str(abs(hash(ds.databaseFields['datasourcecontent'] + str(bindinginfo) )))
                    inputfilenames.append(filename)
                    inputfiles.append(os.path.join(imagepath,  filename ))
                    inputwriter = file(os.path.join(imagepath,  filename ),"w")
                    analysismodulelogger.info("caching inline data to %s"%os.path.join(imagepath,  filename ))
                    inputwriter.write(ds.databaseFields['datasourcecontent'])
                    inputwriter.close()

                # recalculate unique text outputfile names
                textoutputfiles = [ str(abs(hash(ds.databaseFields['datasourcecontent'] + str(bindinginfo) + item))) for item in textoutputfiles]
                imageoutputfiles = [ str(abs(hash(ds.databaseFields['datasourcecontent'] + str(bindinginfo) + item))) for item in imageoutputfiles]
                
            else:
                if ap.databaseFields['proceduretype'] == 'SQL Query':
                    # for SQL queries we bind the data source information to the query - either by editing the
                    # query source code, or by writing the data to a table
                    None # unimplemented
                else:
                    textoutputfiles = [ str(abs(hash(ds.databaseFields['physicalsourceuri'] + str(bindinginfo) + item))) for item in textoutputfiles]
                    imageoutputfiles = [ str(abs(hash(ds.databaseFields['physicalsourceuri'] + str(bindinginfo) + item))) for item in imageoutputfiles]
                    inputfiles.append(ds.databaseFields['physicalsourceuri'])

                    # test whether we can create a link to the input file - if it is a file in the 
                    # web root temp area then we can make a link
                    testname = os.path.join(imagepath,os.path.basename(ds.databaseFields['physicalsourceuri']))
                    analysismodulelogger.info("comparing inputfile name %s with tempfile name %s"%(ds.databaseFields['physicalsourceuri'],testname))
                    if testname == ds.databaseFields['physicalsourceuri']:
                        inputfilenames.append(os.path.basename(ds.databaseFields['physicalsourceuri']))
                    else:
                        inputfilenames.append(None)
                    
            if ap.databaseFields['proceduretype'] != "SQL Query":
                if quoteArgs:
                    inputphrase += ' textinput%s="%s"'%(len(inputfiles),inputfiles[-1])
                else:
                    inputphrase += ' textinput%s=%s'%(len(inputfiles),inputfiles[-1])
                    
        elif ds.databaseFields['datasourcetype'] in ['SQL' , 'SQL (no header)']:
            # open the query and write the results . There is a dataSourceDescriptors text field that 
            # be used to specify , e.g., the format of the cache file - CSV or tab-delimited- but
            # this is not currently used.
            sql = ds.databaseFields['datasourcecontent']%{'ob' : ob}

            # update the output file names using a hash of the SQL and the procedure that is analysing
            textoutputfiles = [ str(abs(hash(sql + str(bindinginfo) + item ))) for item in textoutputfiles]
            imageoutputfiles = [ str(abs(hash(sql + str(bindinginfo) + item))) for item in imageoutputfiles]

            # obtain a cache file name for the data
            # check if the data file exists , if it does then do not re-extract, depending on value of 
            # cachepersistency

            base = str(abs(hash( sql + hashconstant)))
            datafilename = base + ".dat"
            datafilepath = os.path.join(imagepath,  datafilename )
            analysismodulelogger.info("checking %s"%datafilepath)

            inputfiles.append(datafilepath)
            inputfilenames.append(datafilename)
            inputphrase += ' textinput%s=%s'%(len(inputfiles),inputfiles[-1])
            refreshdatasource = True
            if os.path.exists(datafilepath) :
                filetime = os.stat(datafilepath)[stat.ST_MTIME]
                analysismodulelogger.info("cache file %s exists with mtime %s , compared with current time %s"%(datafilepath,filetime,time()))               
                if (time() - filetime)/(60.0*60.0*24.0) < cachePersistency:
                    analysismodulelogger.info("will not refresh this data source as cache < %s days old"%cachePersistency)
                    refreshdatasource = False
                else:
                    analysismodulelogger.info("refreshing this data source as cache >= %s days old"%cachePersistency)
                    refreshdatasource = True
            if refreshdatasource:
                #csvfile = file(datafilepath,"w")
                #csvwriter=csv.writer(csvfile)
                sqlwriter = file(datafilepath,"w")
                sourceCursor = connection.cursor()
                analysismodulelogger.info("executing %s"%sql)
                sourceCursor.execute(sql)

                # get the header
                fieldNames = [item[0].lower() for item in sourceCursor.description]
                #csvwriter.writerow(fieldNames)
                if ds.databaseFields['datasourcetype'] != 'SQL (no header)':
                    sqlwriter.write(reduce(lambda x,y: "%s"%x+'\t'+"%s"%y,[{True : '' , False : item}[item == None] for item in fieldNames])+"\n")

                row = sourceCursor.fetchone()
                analysismodulelogger.info("writing %s"%datafilepath)
                while row != None:
                    # write a row
                    #csvwriter.writerow(row)
                    sqlwriter.write(reduce(lambda x,y: "%s"%x+'\t'+"%s"%y,[{True : '' , False : item}[item == None] for item in row])+"\n")


                    # update the hashed output filenames using this row data
                    textoutputfiles = [ str(abs(hash(str(row) + item))) for item in textoutputfiles]
                    imageoutputfiles = [ str(abs(hash(str(row) + item))) for item in imageoutputfiles]

                    row = sourceCursor.fetchone()

                #csvfile.flush()
                #csvfile.close()
                sqlwriter.flush()                    
                sqlwriter.close()
        elif ds.databaseFields['datasourcetype'] == 'Contributed Database Table':
            analysismodulelogger.info("datasourcetype is 'Contributed Database Table' doing nothing")
        elif ds.databaseFields['datasourcetype'] == 'Parameter':
            analysismodulelogger.info("datasourcetype is 'Parameter' adding to invocation...")
            parameterphrase += ' %(datasourcename)s=%(datasourcecontent)s '%ds.databaseFields
            
        else:
            raise brdfException("runProcedure : unsupported datasource type %(datasourcetype)s"%ds.databaseFields)
            
                
    # construct the outputphrase using the cache output file names
    outputphrase = ''
    for i in range(0,len(textoutputfiles)):
        outputphrase+= ' textoutput%s=%s'%(i+1,os.path.join(imagepath,textoutputfiles[i]))+".txt"
    for i in range(0,len(imageoutputfiles)):
        outputphrase+= ' imageoutput%s=%s'%(i+1,os.path.join(imagepath,imageoutputfiles[i]))+".png"
                    
    if ap.databaseFields['proceduretype'] == 'R procedure':
        # if we are to run code from the database, then replace the procedure name in the invocation , with the
        # cached file
        script_to_run = scriptname
        if not externalSource:
            script_to_run = re.sub(ap.databaseFields['procedurename'], ap.getSourceCodeFileName(imagepath) , scriptname)
        cmd = './RscriptWrapper.sh %(scriptname)s %(inputphrase)s %(outputphrase)s %(parameterphrase)s'%{
           'scriptname' : script_to_run,
           'inputphrase' : inputphrase,
           'outputphrase' : outputphrase,
           'parameterphrase' : parameterphrase
        }
        #cmd = '/bin/sh test.sh'
        analysismodulelogger.info("runProcedure is executing %s"%cmd)
        status, output = commands.getstatusoutput(cmd)

    elif ap.databaseFields['proceduretype'] == 'python script':
        # if we are to run code from the database, then replace the procedure name in the invocation , with the
        # cached file
        if scriptname == None:
            scriptname = ap.databaseFields['procedurename']
        if not externalSource:
            script_to_run = re.sub(ap.databaseFields['procedurename'], ap.getSourceCodeFileName(imagepath) , scriptname)
        cmd = './PythonscriptWrapper.sh %(scriptname)s %(inputphrase)s %(outputphrase)s %(parameterphrase)s'%{
           'scriptname' : script_to_run,
           'inputphrase' : inputphrase,
           'outputphrase' : outputphrase,
           'parameterphrase' : parameterphrase
        }
        #cmd = '/bin/sh test.sh'
        analysismodulelogger.info("runProcedure is executing %s"%cmd)
        status, output = commands.getstatusoutput(cmd)
    elif ap.databaseFields['proceduretype'] == 'perl script':
        # if we are to run code from the database, then replace the procedure name in the invocation , with the
        # cached file
        if scriptname == None:
            scriptname = ap.databaseFields['procedurename']
        if not externalSource:
            script_to_run = re.sub(ap.databaseFields['procedurename'], ap.getSourceCodeFileName(imagepath) , scriptname)
        cmd = './PerlscriptWrapper.sh %(scriptname)s %(inputphrase)s %(outputphrase)s %(parameterphrase)s'%{
           'scriptname' : script_to_run,
           'inputphrase' : inputphrase,
           'outputphrase' : outputphrase,
           'parameterphrase' : parameterphrase
        }
        #cmd = '/bin/sh test.sh'
        analysismodulelogger.info("runProcedure is executing %s"%cmd)
        status, output = commands.getstatusoutput(cmd)
    elif ap.databaseFields['proceduretype'] == 'Java jar procedure':
        cmd = '%(scriptname)s %(inputphrase)s %(outputphrase)s  %(parameterphrase)s'%{
           'scriptname' : scriptname,
           'inputphrase' : inputphrase,
           'outputphrase' : outputphrase,
           'parameterphrase' : parameterphrase
        }
        #cmd = '/bin/sh test.sh'
        analysismodulelogger.info("runProcedure is executing %s"%cmd)
        status, output = commands.getstatusoutput(cmd)
    elif ap.databaseFields['proceduretype'] == 'executable':
        cmd = '%(scriptname)s %(inputphrase)s %(outputphrase)s  %(parameterphrase)s'%{
           'scriptname' : scriptname,
           'inputphrase' : inputphrase,
           'outputphrase' : outputphrase,
           'parameterphrase' : parameterphrase
        }
        #cmd = '/bin/sh test.sh'
        analysismodulelogger.info("runProcedure is executing %s"%cmd)
        status, output = commands.getstatusoutput(cmd)        
    elif ap.databaseFields['proceduretype'] == 'SQL Query':
        # check for and clean up any failed bindings
        if re.search("_list_of_string_",ap.databaseFields["sourcecode"]) != None:
            analysismodulelogger.info("cleaning up unbound string lists using empty string to make valid query")
            ap.databaseFields["sourcecode"] = re.sub("_list_of_string_","''",ap.databaseFields["sourcecode"])
            
        queryCursor = connection.cursor()
        analysismodulelogger.info("executing %s"%ap.databaseFields['sourcecode'])
        queryCursor.execute(ap.databaseFields['sourcecode'])
        fieldNames = [item[0] for item in queryCursor.description]
        rows = queryCursor.fetchall()
        queryCursor.close()

        # write output file if there is one required
        if len(textoutputfiles) == 1:
            analysismodulelogger.info("writing output to %s.txt"%os.path.join(imagepath,textoutputfiles[0]))
            mywriter = file(os.path.join(imagepath,textoutputfiles[0])+".txt","w")
            mywriter.write(reduce(lambda x,y:"%s\t%s"%(x,y), fieldNames))
            mywriter.write("\n")
            if len(rows) > 0:
                mywriter.write(reduce(lambda x,y:"%s\n%s"%(x,y),[reduce(lambda x,y:"%s\t%s"%(x,y),row) for row in rows]))
            mywriter.write("\n")
            mywriter.close()
            
        # generate html output if there is an __output__tag
        output = ""
        status = 0
        if re.search("__output__",ap.databaseFields['presentationtemplate']) != None:
            analysismodulelogger.info("generating web output")
            output = """
            <table border="yes">
            """
            output += "<tr>" + reduce(lambda x,y:"%s<td>%s</td>"%(x,y), fieldNames,"") + "</tr>\n"
            if len(rows) > 0:
                output += reduce(lambda x,y:"%s<tr>%s</tr>\n"%(x,y),[reduce(lambda x,y:"%s<td>%s</td>"%(x,y),row,"") for row in rows],"")
            output += "</table>"
    else:
        raise brdfException("unknown procedure type : %(proceduretype)s"%ap.databaseFields)
    
    
    # merge the output and status into the presentation template for this procedure
    presentationtemplateresult = re.sub('__output__',output,ap.databaseFields['presentationtemplate'])
    presentationtemplateresult = re.sub('__status__',str(status),presentationtemplateresult)


    # bind the actual input and output file names, to slots in the presentationtemplate : 
    # output file N is bound to textoutputlinkN and image output file N is bound to imageoutputlinkN
    # input file N is bound to inputlinkN 
    #  <img src="%(tempimageurl)s%(tempimagefile)s" align="center" width="%(width)s" height="%(height)s"></img>
    for i in range(0,len(inputfiles)):
        templatetext = 'textinput%slink'%(1+i)
        if inputfilenames[i] != None:
            bindtext = "%s%s"%(tempimageurl,inputfilenames[i])
        else:
            bindtext = "(this input not available here - suggest locate using main searchbar)"
        #analysismodulelogger.info('replacing __%s__ with %s'%(templatetext,bindtext))
        presentationtemplateresult = re.sub('__%s__'%templatetext,bindtext,presentationtemplateresult)

    for i in range(0,len(textoutputfiles)):
        templatetext = 'textoutput%slink'%(1+i)
        bindtext = "%s%s.txt"%(tempimageurl,textoutputfiles[i])
        #analysismodulelogger.info('replacing __%s__ with %s'%(templatetext,bindtext))
        presentationtemplateresult = re.sub('__%s__'%templatetext,bindtext,presentationtemplateresult)

    for i in range(0,len(imageoutputfiles)):
        templatetext = 'imageoutput%slink'%(1+i)
        bindtext = "%s%s.png"%(tempimageurl,imageoutputfiles[i])
        #analysismodulelogger.info('replacing __%s__ with %s'%(templatetext,bindtext))
        presentationtemplateresult = re.sub('__%s__'%templatetext,bindtext,presentationtemplateresult)



    # remove the leading and trailing comment tags - the template is commented out 
    # as otherwise it is rendered as part of the web page for the procedure
    presentationtemplateresult = re.sub('\<\!\-\-\s*begintemplate','',presentationtemplateresult)
    presentationtemplateresult = re.sub('endtemplate\s*\-\-\>','',presentationtemplateresult)

 
    #analysismodulelogger.info("Output: %s"%output)
    #analysismodulelogger.info("Status: %s"%status)

    resultHTML = """
                    <table>
                    <tr>
                    <td colspan="2" class=tableheading>
                    %(sectionheading)s
                    </td>
                    </tr>
                """%{
                'sectionheading' : sectionheading
                }


    inlineHTML= """
                        <tr>
                        <td colspan=2>
                        <pre>
                        %(presentationtemplateresult)s
                        </pre>
                        </td>
                        </tr>
                """%{
        'presentationtemplateresult' : presentationtemplateresult
        }

    resultHTML += inlineHTML
    resultHTML += """
       </table>
    """


    return resultHTML


def main():
    #AgilentHyperlinkMain()
    #HyperlinkSimilarExpressionMain()
    #myReader = csvSpotReader("c:/working/microarray/jyexps.csv")
    #spot =  myReader.nextSpot()
    #while spot != None:
    #    print spot
    #    print myReader.nextProfile()
    #    spot =  myReader.nextSpot()
    #    
    #print getSpotExpressionDisplay(1502, usercontext="default", fetcher="", imagepath="", tempimageurl="", sectionheading="Gene Expression from Clonetrac print 128 ovine 20K.txt.BC2.BR1.C6.R23",barwidth=10)
    #createProtocolMain()
    #marshallBfile("C:/working/pgc","orion-genomics-logo.gif", "c:/temp", targetfilename = '')
    #connection = databaseModule.getConnection()
    #getSequenceTraceViewPanel(connection, obid=None, obtype='biosequenceob', usercontext="default", fetcher=None, imagepath='/tmp', tempimageurl=None, sectionheading=None,\
    #  shellscript = "./traceviewer.sh", graphicsprog = './traceviewer.pl', displayFunction = \
    #  (0,0,0,0,0,0,'/data/databases/flatfile/bfiles/pgc/tracefiles/orion/pt1/1188_10_f_48515/traces/1188_10_14726942_16654_48515_016.ab1.gz'), height = 200, \
    #  left = 'CAATAGTAAGGGTGCTGCCGTGCCAC', right='AggtcaactTTGgctgttgtCTTG', size=678)

    #print getAlleleFrequencyDisplay(genetictestfact=1128578, usercontext="default", fetcher=None, imagepath="c:/temp", tempimageurl=None, sectionheading="",\
    #                     barwidth=10,graphTitle1="",graphTitle2="")
    #print getAffyProbeGraphs(None, obid=4470805, obtype="microarrayspotfact", usercontext="default", fetcher=None, imagepath="/tmp", tempimageurl=None, sectionheading="Probe Contrast Plots for Affymetrix.Lp19-Lpa530240N (AgResearch Fungal Array).CS37003138FFFFB_at " ,shellscript = "./getAffyProbeGraphs.sh", Rscript = "./getAffyProbeGraphs.r",panelType = "DEFAULT",includeExperimentList = None,excludeExperimentList=None,width=1200, height=1200, imagetype="jpeg")


    #compileSFFFile(outfolder='/tmp', outfilename = 'test1.sff', shellscript= './appendsfffile.sh', sh="/bin/sh", \
    #                readDict = {
    #                   '/data/bfiles/isgcdata/romney180_05/Baylor.E0C6VPL01.sff.gz' :['E0C6VPL01C2GZJ','E0C6VPL01DNJV2', 'E0C6VPL01DWC6B'],
    #                   '/data/bfiles/isgcdata/romney180_05/Baylor.E0FD4S102.sff.gz' :['E0FD4S102F9J6J','E0FD4S102F4KAQ', 'E0FD4S102GGUFE']
    #                }):
    print "hello"


        
if __name__ == "__main__":
   main()


