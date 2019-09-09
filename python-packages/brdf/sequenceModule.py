#
# This module implements classes relating to sequence objects
#
from types import *
import os
import logging
import globalConf

from obmodule import getNewObid,getObjectRecord,getColumnAliases
from brdfExceptionModule import brdfException
from opmodule import op
from obmodule import ob, canonicalDate
from htmlModule import tidyout, defaultMenuJS
import databaseModule
from imageModule import makeBarGraph
from displayProcedures import getSequenceAnnotationBundle,getSequenceTraceViewPanel,getInlineURL,getGraphicFeaturePanel,getSpotExpressionDisplay,getContigAlignmentViewPanel,getInlineTable


sequencemodulelogger = logging.getLogger('sequencemodule')
sequencemodulehdlr = logging.FileHandler(os.path.join(globalConf.LOGPATH,'sequencemodule.log'))
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
sequencemodulehdlr.setFormatter(formatter)
sequencemodulelogger.addHandler(sequencemodulehdlr) 
sequencemodulelogger.setLevel(logging.INFO)        



class bioSequenceOb ( ob ) :
    """ a list of objects """
    def __init__(self, obid=None):
        ob.__init__(self)

        self.MAX_INLINE_SEQUENCE_LENGTH = 50000
        self.MAX_INLINE_FEATURE_COUNT = 100
        self.AboutMe['default'][0]['heading'] = 'BRDF Sequence Object'
        self.AboutMe['default'][0]['text'] = """
        This page displays a sequence object from the BRDF database. Contents include:

        <ul>
           <li> Basic sequence information - the sequence, length, molecule type
           <li> Blast or other search annotation if available
           <li> A graphical feature display if features have been loaded
           <li> A trace viewer if there is a trace file linked to the sequence. The clipped off ends
                are usually shaded gray in this view, the sequence corresponding to that shown in the basic
                sequence information panel is unshaded. In some cases there may be no shading, if the
                drawing code could not determine where the clipping started. Some ABI files seem to
                adopt a convention of starting the clipped sequence at position zero, and it may be possible to
                identify the start of clipping using this rule, even when we have not shaded the clipped
                region.
        </ul>
        
        In the BRDF database schema, sequence objects are stored in a table called
        biosequenceob. Various types of sequence can be stored in this table - for example,
        nucleotide, protein, mRNA sequence, genomic sequence. Also, various types of
        sequence model can be stored in addition to the common models of nucleic and amino acid symbol strings -
        for example, other models of sequences include regular expressions and HMMs.
        </p>
        The type of a sequence object is stored in the sequencetype field of this table.
        The current set of types that are supported in this database are recorded in an ontology called
        AGSEQUENCE_ONTOLOGY (you can browse this ontology by selecting ONTOLOGIES from the drop down list
        of search types on the main page, and entering AGSEQUENCE_ONTOLOGY as the search phrase).
        <p/>
        A Sequence Object in the BRDF database may have relationships with other types of object
        in the database. For example, if the sequence is a primary sequence resulting from lab work, then
        there is a relation between the biological sample used in the sequencing experiment and one or more
        lab resources (vectors, primers); a sequence may be the product of a gene and thus related to
        a BRDF geneticob record; if we have searched sequence databases (e.g. via BLAST) and
        found similar sequences and stored these search results in the BRDF schema, then this involves a
        relationship with a database search run and another (hit) biosequence. All of the possible relationships that a
        sequence object may have with other objects in the database are depicted by icons in the information
        map section of the page.
        <p/>
        The icon is composed of the sequenceob symbol connected to the symbols for the related objects
        by horizontal lines. Where the database does not yet contain any related objects for a sequence,
        the icon for that relationship is greyed out.
        <p/>
        We may store various types of facts about a given sequence object - for example, features of the
        sequence; or miscellaneous facts specific to a given project. Each type of fact supported by the
        BRDF is depicted by a line connecting the sequence symbol, to a square box labelled info, with the type of
        fact appearing to the right of the icon. Where the database does not yet contain any facts
        of a given type for a sequence object, the info icon is greyed out.
        """

        if obid != None:
            con = databaseModule.getConnection()
            self.initFromDatabase(obid, con)
            con.close()
        


    def initNew(self,connection):      
        self.obState.update({'NEW' : 1, 'DB_PENDING' : 1})

        self.databaseFields = {
            'obid' : getNewObid(connection) ,
            'sequencename' : None,
            'sequencedescription' : None,
            'xreflsid' : None,
            'sequencetype' : None,
            'seqstring' : None,
            'seqlength' : None,
            'sequenceurl' : None,
            'seqcomment' : None,
            'fnindex_accession' : None,
            'fnindex_id' : None
        }         

    def initFromDatabase(self, identifier, connection):
        """ method for initialising geneticob from database """

        # first init base class - this will get obid
        ob.initFromDatabase(self, identifier, "bioSequenceOb", connection)

        # now get the complete object
        # self.databaseFields = getObjectRecord(connection, "bioSequenceOb", self.databaseFields['obid'])
        # replace this with a method that handles large sequences
        sql = """
        select
 obid        ,       
 obtypeid           , 
 xreflsid           , 
 createddate        , 
 createdby          , 
 lastupdateddate    , 
 lastupdatedby      , 
 checkedout         , 
 checkedoutby       , 
 checkoutdate       , 
 obkeywords         , 
 statuscode         , 
 sequencename       , 
 sequencetype       , 
 sequencedescription, 
 sequencetopology   , 
 seqlength          , 
 sequenceurl        , 
 seqcomment         , 
 gi                 , 
 fnindex_accession  , 
 fnindex_id         
    from biosequenceob where obid = %(obid)s
    """%self.databaseFields
        obCursor = connection.cursor()
        obCursor.execute(sql)
        obFieldValues = obCursor.fetchone()
        if obCursor.rowcount != 1:
            raise brdfException, "getObjectRecord : unable to find one unique object using " + sql
        fieldNames = [item[0] for item in obCursor.description]
        self.databaseFields = dict(zip(fieldNames,obFieldValues))

        # if the sequence is not too long then get that as well
        if self.databaseFields['seqlength'] > self.MAX_INLINE_SEQUENCE_LENGTH:
            self.databaseFields["seqstring"] = "( ** only sequences of length less than %s are displayed inline in this panel - click View | asFasta or View | asGenbank to view sequence ** )"%self.MAX_INLINE_SEQUENCE_LENGTH
        else:
            sql = """select seqstring from biosequenceob where obid = %(obid)s"""%self.databaseFields
            obCursor = connection.cursor()
            obCursor.execute(sql)
            obFieldValues = obCursor.fetchone()        
            self.databaseFields["seqstring"] = obFieldValues[0]

        obCursor.close()

        # get any column alises that have been defined
        if self.columnAliases == None:
            self.columnAliases = getColumnAliases(connection, "bioSequenceOb")


    def insertDatabase(self,connection):
        """ method used by bioSequence object to save itself to database  """
        sql = """
        insert into bioSequenceOb(obid,sequencename,sequencedescription,xreflsid,sequencetype,
        seqstring,seqlength,sequenceurl,seqcomment,fnindex_accession,fnindex_id)
        values(%(obid)s,%(sequencename)s,%(sequencedescription)s,%(xreflsid)s,%(sequencetype)s,
        %(seqstring)s,%(seqlength)s,%(sequenceurl)s,%(seqcomment)s,%(fnindex_accession)s,%(fnindex_id)s)
        """
        #print "executing " + sql%self.databaseFields
        insertCursor = connection.cursor()
        insertCursor.execute(sql,self.databaseFields)
        connection.commit()
        insertCursor.close()
        self.obState.update({'NEW' : 0 , 'ERROR' : 0, 'DB_PENDING' : 0, 'MESSAGE' : "database insert OK"})
        return

    def updateDatabase(self,connection):
        """ method used by bioSequence object to update specific database fields via the edit form """
        sql = """
        update bioSequenceOb 
        set sequencedescription = '%(sequencedescription)s',
            seqstring = '%(seqstring)s',
            seqlength = %(seqlength)s,
            lastupdateddate=now()
        where obid = %(obid)s
        """%self.databaseFields
        #print "executing " + sql%self.databaseFields
        insertCursor = connection.cursor()
        sequencemodulelogger.info("executing %s"%sql)
        insertCursor.execute(sql)
        connection.commit()
        insertCursor.close()
        self.obState.update({'NEW' : 0 , 'ERROR' : 0, 'DB_PENDING' : 0, 'MESSAGE' : "database insert OK"})
        return

    def createSequencingFunction(self, connection, biosampleob, xreflsid, labresourceob = None, \
                               labresourcelist = None , sequencingdate = None, sequencedby = None, functionComment = None,voptypeid = None):
        """ method used to relate this sample to a subject and optionally a protocol """
        functionDetails = {
            'biosequenceob' : self.databaseFields['obid'],
            'biosampleob' : eval({True : "None", False : "biosampleob.databaseFields['obid']"}[biosampleob == None]),
            'functionComment' : functionComment,
            'xreflsid' : xreflsid,
            'labresourceob' : eval({False : "labresourceob.databaseFields['obid']", True : "None" }[labresourceob == None]),
            'labresourcelist' : eval({ False : "labresourcelist.databaseFields['obid']", True : "None" }[labresourcelist == None]),
            'sequencingdate' : sequencingdate,
            'sequencedby' : sequencedby  ,
            'voptypeid' : voptypeid
        }
        if functionDetails['sequencingdate'] != None:
            functionDetails['sequencingdate'] = canonicalDate(functionDetails['sequencingdate'])        
        sql = """
        insert into sequencingfunction(biosequenceob,biosampleob,functionComment,
        xreflsid,labresourceob,labresourcelist,sequencingdate,sequencedby,voptypeid)
        values(%(biosequenceob)s,%(biosampleob)s,%(functionComment)s,
        %(xreflsid)s,%(labresourceob)s,%(labresourcelist)s,to_date(%(sequencingdate)s,'dd/mm/yyyy'),
        %(sequencedby)s,%(voptypeid)s)
        """
        #print "executing %s"%(sql%functionDetails)
        sequencemodulelogger.info("executing %s"%(sql%functionDetails))
        insertCursor = connection.cursor()
        insertCursor.execute(sql,functionDetails)
        connection.commit()
        insertCursor.close()
        self.obState.update({'NEW' : 0 , 'ERROR' : 0, 'DB_PENDING' : 0, 'MESSAGE' : "sequencing function insert OK"})


    def addFeature(self,connection,featureDict, featureAttributes = None, checkExisting = False):
        featureDict.update ({
            'biosequenceob' : self.databaseFields['obid'],
            'xreflsid' : "%s.feature.%s"%(self.databaseFields['xreflsid'],featureDict['featuretype']),
            'featurestrand' : eval({True : 'featureDict["featurestrand"]', False : "None"}[featureDict.has_key("featurestrand")]),
            'featurestart' : eval({True : 'featureDict["featurestart"]', False : "None"}[featureDict.has_key("featurestart")]),            
            'featurestop' : eval({True : 'featureDict["featurestop"]', False : "None"}[featureDict.has_key("featurestop")]),
            'featurecomment' : eval({True : 'featureDict["featurecomment"]', False : "None"}[featureDict.has_key("featurecomment")]),
            'featureaccession' : eval({True : 'featureDict["featureaccession"]', False : "None"}[featureDict.has_key("featureaccession")]),
            'featurelength' : eval({True : 'featureDict["featurelength"]', False : "None"}[featureDict.has_key("featurelength")]),
            'evidence' : eval({True : 'featureDict["evidence"]', False : "None"}[featureDict.has_key("evidence")])              
            })

        insertCursor = connection.cursor()
        
        # first check if this feature is already in the db - if it is do not duplicate
        featureExists = False
        if checkExisting:
            sql = """
            select obid from biosequencefeaturefact where
            biosequenceob = %(biosequenceob)s and
            featuretype = %(featuretype)s """
            if featureDict['featurestart'] != None:
                sql += " and featurestart = %(featurestart)s "
            if featureDict['featurestop'] != None:
                sql += " and featurestop = %(featurestop)s "
            if featureDict['featurestrand'] != None:
                sql += " and featurestrand = %(featurestrand)s "
            if featureDict['featurelength'] != None:
                sql += " and featurelength = %(featurelength)s "            
            sequencemodulelogger.info("checking for feature using %s"%(sql%featureDict))
            insertCursor.execute(sql,featureDict)
            insertCursor.fetchone()
            sequencemodulelogger.info("rowcount = %s"%insertCursor.rowcount)

            if insertCursor.rowcount != 0:
                featureExists = True
                
            
        if not featureExists:
            featureDict.update ({
                'obid' : getNewObid(connection)
            })
            
            sql = """
            insert into bioSequenceFeatureFact(obid,biosequenceob,xreflsid,featuretype,featurestrand,featurestart,featurestop,featurecomment,
            evidence,featurelength)
            values(%(obid)s,%(biosequenceob)s,%(xreflsid)s,%(featuretype)s,%(featurestrand)s,%(featurestart)s,%(featurestop)s,%(featurecomment)s,
            %(evidence)s,%(featurelength)s)
            """
            sequencemodulelogger.info("executing %s"%(sql%featureDict))
            insertCursor.execute(sql,featureDict)
            connection.commit()


            # if necessary add feature attributes
            if featureAttributes != None:
                if len(featureAttributes) > 0:
                    for attribute in featureAttributes:
                        sql = """
                        insert into biosequencefeatureattributefact( biosequencefeaturefact , factnamespace , attributename , attributevalue)
                        values(%(biosequencefeaturefact)s , %(factnamespace)s , %(attributename)s , %(attributevalue)s)
                        """

                        insertCursor.execute(sql,{
                            'biosequencefeaturefact' : featureDict.obid,
                            'factnamespace' : attribute[0],
                            'attributename' : attribute[1],
                            'attributevalue' : attribute[2] })
                    connection.commit()
                            
            insertCursor.close()
            self.obState.update({'NEW' : 0 , 'DB_PENDING' : 0, 'ERROR' : 0, 'MESSAGE' : "database insert OK"})

            
        else:
            insertCursor.close()        
        
        
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
                    'fastaURL' : self.fastaURL%(self.databaseFields['obid']),
                    'genbankURL' : self.genbankURL%(self.databaseFields['obid'])                    
                    }
        try:
            menuDict['editURL'] =  self.editURL%self.databaseFields['obid']
        except:
            menuDict['editURL'] =  self.editURL
            
            
        
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
            return location.href="%(editURL)s"+anchor;
        }

        function viewButton(link) {
            hideMenu();
            return location.href=link;        
        }

        function toolButton(link) {
            hideMenu();
            return location.href=link;        
        }        
        
        var editItemArray = new Array();
        editItemArray[0] = new Array("editButton(\"\");","Edit Basic Sequence Details");
        editItemArray[1] = new Array("editButton(\"#Primer\");","Add Primer");
        editItemArray[2] = new Array("editButton(\"#Vector\");","Add Vector");
        editItemArray[3] = new Array("editButton(\"#Feature\");","Add Feature");
        
        var annotateItemArray = new Array();
        annotateItemArray[0] = new Array("annotateButton(\"%(addCommentURL)s\");","Add Comment");
        annotateItemArray[1] = new Array("annotateButton(\"%(addLinkURL)s\");","Add Hyperlink");
        
        var viewItemArray = new Array();
        viewItemArray[0] = new Array("viewButton(\"%(fastaURL)s\");","as FASTA");
        viewItemArray[1] = new Array("viewButton(\"%(genbankURL)s\");","as Genbank");
        
        var toolsItemArray = new Array();
        toolsItemArray[0] = new Array("unimplemented(\"BLAST against this sequence\");","BLAST");
        
        var helpItemArray = new Array();
        helpItemArray[0] = new Array("helpButton();","Help");
        """%menuDict
        
        return defaultMenuJS%dynamicMenuJS
    


    def asHTMLTableRows(self,title='',width="90%",context='default'):
        if context == 'default':
            return ob.asHTMLTableRows(self,title,width,context)
        elif context == 'briefsearchsummary':
            return ob.asHTMLTableRows(self,title,width,context)
        else:
            return ob.asHTMLTableRows(self,title,width,context)


    def myToolsPanel(self, table, width=800,context="default"):
        """
        this overrides the abstract method myToolsPanel defined in the ob base class, and
        will return HTML for a tools panel, containing tools as specified in the
        tools descriptor
        """
        if self.databaseFields['seqstring'] != None:
            if len(self.databaseFields['seqstring']) > 0:
                if len(self.tools) > 0:
                    toolHTML = ""
                    for tool in self.tools:
                        toolHTML+= """
                        <form name="%(toolname)s method="post" action="%(cgiscript)s" target="main">
                        <input type="submit" value="%(tooldisplayname)s" alt="%(toolhelp)s"/>
                        <input name="seqstring" type="hidden" value="%(seqstring)s"/>
                        <input name="xreflsid" type="hidden" value="%(xreflsid)s/>
                        </form>
                        """%{
                            "toolname" : tool,
                          "cgiscript" : self.tools[tool]["cgiscript"],
                            "tooldisplayname" : self.tools[tool]["tooldisplayname"],
                            "seqstring" : self.databaseFields["seqstring"],
                            "xreflsid" : self.databaseFields["xreflsid"],
                            "toolhelp" : self.databaseFields["toolhelp"]
                        }   
                        table += """
                        <tr class=%s>
                        <td colspan=2>
                        <table class=%s>
                        <tr>            
                        <td colspan=2 align=left> 
                        <a name="Tools" class=whiteheading>
                        Tools
                        </a>
                        </td>
                        </tr>
                        <tr>            
                        <td colspan=2 align=left>
                        %s
                        </td>
                        </tr>                        
                        </table>
                        </td>            
                        </tr>"""%(self.theme["section heading class"],self.theme["section heading class"],toolHTML)

        

    def myHTMLSummary(self, table, width="90%",context='default'):
        summaryFieldNames = ['sequencename','sequencetype','sequencedescription','seqlength','seqcomment','sequencetopology',\
                             'sequenceurl','fnindex_accession','fnindex_id','xreflsid','gi']
        summaryItems = [(fieldName, self.databaseFields[fieldName]) for fieldName in summaryFieldNames if self.databaseFields[fieldName] != None]
        sequenceItems = [('seqstring',self.databaseFields['seqstring'])]


        # get sequence features
        connection = databaseModule.getConnection()


        # initialise each analysisfunction and test security 
        if self.obState['DYNAMIC_ANALYSES'] > 0:
            connection=databaseModule.getConnection()
            accessibleFunctions = []
            for func in self.analysisFunctions:
                sequencemodulelogger.info('initialising analysisfunction %s to test access '%func[9])       
                import analysisModule
                funcOb = analysisModule.analysisFunction()
                funcOb.initFromDatabase(func[9],connection)
                funcOb.initMetadata(connection)
                funcOb.initProtections(connection)
                funcOb.username = self.username
                if funcOb.runSecurityFunctions(resourcename="analysis procedure menu"):
                    sequencemodulelogger.info('adding accessible function %s'%funcOb.databaseFields['xreflsid'])        
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
        


        #table += getSequenceAnnotationBundle(connection, self.databaseFields['obid'], obtype='biosequenceob', usercontext=context, fetcher=self.fetcher,\
        #            imagepath=self.imagepath, tempimageurl=self.tempimageurl,\
        #            panelTitle1="Database Search Results",panelTitle2="and Gene Ontology Associations",\
        #            bundleType = "DBHITS,GO",databaseSearchList = [ 93588, 93591, 93604, 93650, 93974, 94282], topHits = 3, \
        #            databaseQueryID = self.databaseFields['obid'])
        mydisplayhtml = ''
        if self.obState['DYNAMIC_DISPLAYS'] > 0:
            displayFunctionAccess = True
            if self.obState['SECURITY_POLICIES'] > 0:
                displayFunctionAccess = self.runSecurityFunctions(context,"display functions")
            #mapAccess = False
            if displayFunctionAccess:              
                sequencemodulelogger.info('running non-virtual display functions')
                for displayFunction in self.displayFunctions:
                    # exclude virtual functions - these will be instantiated in specific contexts or subclasses
                    if displayFunction[7] == None:
                        sequencemodulelogger.info('running %s'%displayFunction[0])
                        mydisplayhtml += eval(displayFunction[0])
                        #table += mydisplayhtml  # - now add after summary      


        featureCursor = connection.cursor()
        sql = """
        select bsf.xreflsid,featuretype,featurestrand,featurestart,featurestop,featurecomment,evidence
        from
        biosequencefeaturefact bsf join biosequenceob bso
        on
        bso.obid = %s  and
        bsf.biosequenceob = bso.obid
        order by
        featuretype
        """%self.databaseFields['obid']
        featureCursor.execute(sql)
        rows = featureCursor.fetchall()
        fieldNames = [item[0].lower() for item in featureCursor.description]

        # get columnAliases for features
        featureHeadings = getColumnAliases(connection,'biosequencefeaturefact')
        if featureHeadings == None:
            featureHeadings = dict(zip(fieldNames,fieldNames))

        for field in fieldNames:
            if field not in featureHeadings:
                featureHeadings[field] = field 
                
        
        if featureCursor.rowcount > 0:
            featureRows = """
            <tr> <td colspan="2" class=inside>
            <table class=inside>
            <tr>
            <td class=tableheading colspan="%s"><br/>
            Feature Table
            </td>
            </tr>
            """%len(fieldNames)
            featureRows += "<tr>" + reduce(lambda x,y:x+y, ['<td class=fieldname>'+featureHeadings[fieldName]+'</td>\n' \
                                                   for fieldName in fieldNames ]) + "</tr>"

            if len(rows) <= self.MAX_INLINE_FEATURE_COUNT:
                for feature in rows:
                    featureRow = "<tr>" + reduce(lambda x,y:x+y, ['<td class=fieldvalue>'+str(featureAttribute)+'</td>\n' \
                                                       for featureAttribute in feature ]) + "</tr>"
                    featureRows += featureRow
            else:
                    featureRow = "<tr><td colspan=%s>"%len(fieldNames) + "( ** Too many features - features only displayed inline if there are less than %s : click the Info icon on the Sequence Feature link below to download features ** )"%self.MAX_INLINE_FEATURE_COUNT  + "</td></tr>"
                    featureRows += featureRow
                
                
            featureRows += "</table></td></tr>"
        else:
            featureRows = ""
        featureCursor.close()            


        # get vectors and primers
        labCursor = connection.cursor()
        sql = """
        select lr.xreflsid,lr.resourcename, lr.resourcetype, lr.resourcesequence,lr.obid
        from
        ((biosequenceob bs join sequencingfunction sf
        on bs.obid = %s and sf.biosequenceob = bs.obid)
        join labresourceob lr on lr.obid = sf.labresourceob)
        union
        select lr.xreflsid,lr.resourcename, lr.resourcetype, lr.resourcesequence, lr.obid
        from
        (((biosequenceob bs join sequencingfunction sf
        on bs.obid = %s and sf.biosequenceob = bs.obid) 
        join labresourcelistmembershiplink  lrl on lrl.labresourcelist = sf.labresourcelist) join
        labresourceob lr on lr.obid = lrl.labresourceob)
        """%(self.databaseFields['obid'],self.databaseFields['obid'])
        labCursor.execute(sql)
        rows = labCursor.fetchall()
        fieldNames = [item[0].lower() for item in labCursor.description if item[0].lower() != 'obid']

        # modify the data rows - hyperlink the lsids and get rid of the obid
        rows = [ ('<a href=' + self.fetcher + "?context=%s&obid=%s&target=ob"%(context,item[4]) + '>%s</a>'%item[0], item[1],item[2], item[3])  for item in rows ]        

        # get column aliases for lab resources
        labHeadings = {
            'xreflsid' : 'LSID',
            'resourcename' : 'Name',
            'resourcetype' : 'Vector/Primer',
            'resourcesequence' : 'Sequence'
        }
        
        if labCursor.rowcount > 0:
            labRows = """
            <tr> <td colspan="2" class=inside> 
            <table class=inside>
            <tr>
            <td class=tableheading colspan="%s"> <br/>
            Vectors / Primers Table
            </td>
            </tr>
            """%len(fieldNames)
            labRows += "<tr>" + reduce(lambda x,y:x+y, ['<td class=fieldname>'+labHeadings[fieldName]+'</td>\n' \
                                                   for fieldName in fieldNames ]) + "</tr>"
            for resource in rows:
                labRow = "<tr>" + reduce(lambda x,y:x+y, ['<td class=fieldvalue>'+str(resourceAttribute)+'</td>\n' \
                                                   for resourceAttribute in resource ]) + "</tr>"
                labRows += labRow
                
            labRows += "</table></td></tr>"
        else:
            labRows = ""
        labCursor.close()



        # get lab resource rows


        #FieldItems = [item for item in self.databaseFields.items() if not isinstance(item[1],ListType)]
        summaryRows =  reduce(lambda x,y:x+y, ['<tr><td class=fieldname>'+self.getColumnAlias(key)+'</td><td class=fieldvalue>'+tidyout(str(value), 80, 1,'<br/>')[0]+'</td></tr>\n' \
                                                   for key,value in summaryItems if self.getColumnAlias(key) != None])
        seqRows =  reduce(lambda x,y:x+y, ['<tr><td class=fieldname>'+self.getColumnAlias(key)+'</td><td class=fieldvalue>'+tidyout(str(value), 80, 1,'<br/>')[0]+'</td></tr>\n' \
                                                   for key,value in sequenceItems if self.getColumnAlias(key) != None])
        
        summaryRows = '<tr><td class=inside colspan="2"><table class=inside border="0">' + summaryRows + seqRows + featureRows + labRows + '</table></td></tr>'



        # see if there is any expression information available for which we can draw a map
        # Note that there is now a displayProcedure that may be dynamically attached - at soem point
        # we should probably remove the following hard-coded expression display, and use the
        # dnamically attached display procedure
        sql = """
        select          
            expressionmapname , 
            expressionmaplocus ,
            expressionamount
        from
            geneticexpressionfact
        where
            biosequenceob = %(obid)s
        order by
            expressionmapname
        """
        sequencemodulelogger.info("executing %s"%sql%self.databaseFields)
        expressionCursor=connection.cursor()
        expressionCursor.execute(sql,self.databaseFields)
        rows = expressionCursor.fetchall()
        expressionmaps={}
        for row in rows:
            if row[0] not in expressionmaps:
                expressionmaps[row[0]] = {}
            expressionmaps[row[0]].update( {
                row[1] : row[2]
            })
        sequencemodulelogger.info("expression maps : %s"%str(expressionmaps))


        myGraphHTML = ""
        # for each map , obtain map information including drawing instructions. To have maps drawn,
        # an update like this is needed :
        #insert into  ontologyfact(ontologyob,factnamespace,attributename,attributevalue)
        #select obid, 'Display Settings','Expression Graph Type','Bar Graph'
        #from ontologyob where ontologyname = 'My Tissue Libaries';

        for expressionmap in expressionmaps.keys():
            sql = """
            select
               obid,
               attributevalue
            from
               ontologyob o join ontologyfact otf on
               o.ontologyname = %(mapname)s and

               otf.ontologyob = o.obid and
               otf.factnamespace = 'Display Settings' and
               otf.attributename = 'Expression Graph Type'
            """
            sequencemodulelogger.info("executing %s"%sql%{ 'mapname' : expressionmap })
            expressionCursor.execute(sql,{ 'mapname' : expressionmap })
            rows = expressionCursor.fetchall()
            if expressionCursor.rowcount != 1:
                continue

            sequencemodulelogger.info("Expression map info : %s"%str(rows))
            graphType = rows[0][1]

            # get the expression data
            sql = """
            select
               termname,
               termdescription,
               obid
            from
               ontologytermfact
            where
               ontologyob = %s
            """%rows[0][0]
            sequencemodulelogger.info("executing %s"%sql)
            expressionCursor.execute(sql)
            rows = expressionCursor.fetchall()
            mapDomainDict = dict(zip( [row[0] for row in rows], [(row[1],row[2]) for row in rows] ) )
            sequencemodulelogger.info("map domain :  %s"%str(mapDomainDict))

            # we only support a bar graph at the moment
            # prepare the arguments to the imageModule method for drawing a bar graph
            mapData=[]
            for mapDomainItem in mapDomainDict.keys():
                dataTuple = [0,mapDomainDict[mapDomainItem][0],self.fetcher + "?context=%s&obid=%s&target=ob"%(context,mapDomainDict[mapDomainItem][1]),mapDomainItem]
                #sequencemodulelogger.info("checking if %s in %s"%(mapDomainItem,str(expressionmap)))
                if mapDomainItem in expressionmaps[expressionmap]:
                    dataTuple[0] = expressionmaps[expressionmap][mapDomainItem]
                dataTuple = tuple(dataTuple)
                mapData.append(dataTuple)

            sequencemodulelogger.info(str(mapData))
            #graphImageFile = makeBarGraph("c:/temp/",mapData,\
            #currenttuple=None,label1="Tissue Expression for",label2=self.databaseFields['sequencename'],\
            #barwidth=20,colourScheme=0)
            (myGraphName,myGraphMap) = makeBarGraph(imageDirectory=self.imagepath,datatuples=mapData,currenttuple=None,label1="Tissue Expression for",\
                                                    label2=self.databaseFields['sequencename'],\
                                                    barwidth=15,colourScheme=0)
            myGraphHTML= """
                        <tr>
                        <td colspan=2 align=center>
                        <p/>
                        <img src="%s%s" halign="center" usemap="#%s" border="0"/>
                        <p/>
                        %s
                        </td>
                        </tr>
                        """
            myGraphHTML = myGraphHTML%(self.tempimageurl,myGraphName,myGraphName.split('.')[0],myGraphMap)

            
                                                

        expressionCursor.close()
        connection.close()
        #------------------------- end expression maps section ---------------------------
        

        sequencemodulelogger.info('listing fields')

        table +="""
        <TH colspan="2" style="BACKGROUND: silver ; color:white; font-size:16pt" align=middle>Basic Sequence Details</TH>
        """

        table += summaryRows
        if len(myGraphHTML) > 0:
            table += """
            <tr> <td colspan="2" class=inside> 
            <table class=inside>
            <tr>
            <td class=tableheading> <br/>
            Expression Maps
            </td>
            </tr>
            """            
        table +=  myGraphHTML + mydisplayhtml


        return table


    def addFact(self,connection,argfactNameSpace, argattributeName, argattributeValue, checkExisting = True):
        factFields = {
            'bioSequenceOb' : self.databaseFields['obid'],
            'factNameSpace' : argfactNameSpace,
            'attributeName' : argattributeName,
            'attributeValue' : argattributeValue }

        insertCursor = None

        doInsert = True
        if checkExisting:
            sql = """
            select biosequenceob from bioSequenceFact where
            biosequenceob = %(bioSequenceOb)s and
            factNameSpace = %(factNameSpace)s and
            attributeName = %(attributeName)s and
            attributeValue = %(attributeValue)s
            """
            insertCursor = connection.cursor()
            sequencemodulelogger.info("checking for fact using %s"%(sql%factFields))
            insertCursor.execute(sql,factFields)
            insertCursor.fetchone()
            sequencemodulelogger.info("rowcount = %s"%insertCursor.rowcount)
            if insertCursor.rowcount > 0:
                doInsert = False
                
        if doInsert:
            if insertCursor == None:
                insertCursor = connection.cursor()
                
            sql = """
            insert into bioSequenceFact(biosequenceob,factNameSpace, attributeName, attributeValue)
            values(%(bioSequenceOb)s,%(factNameSpace)s,%(attributeName)s,%(attributeValue)s)
            """
            sequencemodulelogger.info("executing %s"%(sql%factFields))
            insertCursor.execute(sql,factFields)
            connection.commit()
            self.obState.update({'NEW' : 0 , 'DB_PENDING' : 0, 'ERROR' : 0, 'MESSAGE' : "database insert OK"})

        insertCursor.close()             
    



class bioSequenceFeatureFact ( op ) :
    """ a list of objects """
    def __init__(self):
        op.__init__(self)


    def initNew(self,connection):      
        self.obState.update({'NEW' : 1, 'DB_PENDING' : 1})

        self.databaseFields = {
            'biosequenceob' : None,
            'obid' : getNewObid(connection) ,
            'featuretype' : None,   
            'featurestart' : None,  
            'featurestop' : None  , 
            'featurestrand' : None ,
            'featurecomment' : None,
            'featureaccession' : None
        }         

    def initFromDatabase(self, identifier, connection):
        """ method for initialising geneticob from database """

        # first init base class - this will get obid
        ob.initFromDatabase(self, identifier, "bioSequenceFeatureFact", connection)

        # now get the complete object
        self.databaseFields = getObjectRecord(connection, "bioSequenceFeatureFact", self.databaseFields['obid'])

        # at some point maybe add retrieval of any associated feature attributs


class sequenceAlignmentFact ( op ) :
    """ a list of objects """
    def __init__(self):
        op.__init__(self)


    def initNew(self,connection):      
        self.obState.update({'NEW' : 1, 'DB_PENDING' : 1})

        self.databaseFields = {
         'xreflsid' : None ,                  
         'databasesearchobservation' : None , 
         'bitscore' : None ,                  
         'score' : None ,                     
         'evalue' : None ,                    
         'queryfrom' : None ,                 
         'queryto' : None ,                   
         'hitfrom' : None ,                  
         'hitto' : None ,                     
         'queryframe' : None ,                
         'hitframe' : None ,                  
         'identities' : None ,                
         'positives' : None ,                 
         'alignlen' : None ,
         'pctidentity' : None,
         'mismatches' : None,
         'hspqseq' : None ,                   
         'hsphseq' : None ,                   
         'hspmidline' : None ,                
         'alignmentcomment' : None ,          
         'hitstrand' : None ,                 
         'gaps' : None                     
        }         

    def initFromDatabase(self, identifier, connection):
        """ method for initialising sequencealignmentfact from database """

        # first init base class - this will get obid
        ob.initFromDatabase(self, identifier, "sequenceAlignmentFact", connection)

        # now get the complete object
        self.databaseFields = getObjectRecord(connection, "sequenceAlignmentFact", self.databaseFields['obid'])

        # at some point maybe add retrieval of any associated feature attributs



class sequencingFunction ( op ) :
    """ sequencing function """
    def __init__(self):
        op.__init__(self)


    #def initNew(self,connection):      

    def initFromDatabase(self, identifier, connection):
        """ method for initialising sequencing function from database """

        # first init base class - this will get obid
        ob.initFromDatabase(self, identifier, "sequencingFunction", connection)

        # now get the complete object
        self.databaseFields = getObjectRecord(connection, "sequencingFunction", self.databaseFields['obid'])

        # at some point maybe add retrieval of any associated feature attributs
        

class bioLibraryOb ( ob ) :
    """ sequencing library """
    def __init__(self):
        ob.__init__(self)


    def initNew(self,connection):
        self.obState.update({'NEW' : 1, 'DB_PENDING' : 1})        
        self.databaseFields = {
            'obid' : getNewObid(connection) ,
            'xreflsid' : None,
            'libaryname' : None,
            'librarytype' : None,
            'librarydate' : None,
            'librarydescription' : None,
            'librarystorage' : None}


    def initFromDatabase(self, identifier, connection):
        """ method for initialising bioLibraryOb from database """

        # first init base class - this will get obid
        ob.initFromDatabase(self, identifier, "bioLibraryOb", connection)

        # now get the complete object
        self.databaseFields = getObjectRecord(connection, "bioLibraryOb", self.databaseFields['obid'])


    def insertDatabase(self,connection):
        """ method used by biolibraryob object to save itself to database  """
        sql = """
        insert into biolibraryob(obid,xreflsid,libraryname,librarytype,
        librarydate,librarydescription,librarystorage)
        values(%(obid)s,%(xreflsid)s,%(libraryname)s,%(librarytype)s,
        %(librarydate)s,%(librarydescription)s,%(librarystorage)s)
        """
        #print "executing " + sql%self.databaseFields
        insertCursor = connection.cursor()
        insertCursor.execute(sql,self.databaseFields)
        connection.commit()
        insertCursor.close()
        self.obState.update({'NEW' : 0 , 'ERROR' : 0, 'DB_PENDING' : 0, 'MESSAGE' : "database insert OK"})
        return


class librarySequencingFunction ( op ) :
    """ library sequencing function """
    def __init__(self):
        op.__init__(self)


    #def initNew(self,connection):      

    def initFromDatabase(self, identifier, connection):
        """ method for initialising library sequencing function from database """

        # first init base class - this will get obid
        ob.initFromDatabase(self, identifier, "librarySequencingFunction", connection)

        # now get the complete object
        self.databaseFields = getObjectRecord(connection, "librarySequencingFunction", self.databaseFields['obid'])

        # at some point maybe add retrieval of any associated feature attributs    
        
        
            
        

def main():
    #set up database connection  and the top level cursor
    #try :
        #page=geneSummaryPage()
        #htmlChunk = page.asHTML(304);
        #page.close()
    #except :
    #    errorPage("Error creating geneSummaryPage")
    return


if __name__ == "__main__":
   main()
        
