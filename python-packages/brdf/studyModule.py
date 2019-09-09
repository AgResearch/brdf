#
# This module implements classes relating to studies
#
from types import *
from datetime import date, datetime


from obmodule import getNewObid,getObjectRecord
from brdfExceptionModule import brdfException
from labResourceModule import labResourceOb,labResourceList
from biosubjectmodule import bioSampleList, bioSampleOb
from htmlModule import tidyout,defaultMenuJS
from imageModule import makeBarGraph
from opmodule import op
from obmodule import ob,canonicalDate
from annotationModule import commentOb
from displayProcedures import getGenepixThumbnailDisplay
import logging
import globalConf
import databaseModule
import os
import re
import commands

studymodulelogger = logging.getLogger('studymodulelogger')
###hdlr = logging.FileHandler('c:/temp/nutrigenomicsforms.log')
studymodulehdlr = logging.FileHandler(os.path.join(globalConf.LOGPATH,'studymodule.log'))
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
studymodulehdlr.setFormatter(formatter)
studymodulelogger.addHandler(studymodulehdlr) 
studymodulelogger.setLevel(logging.INFO)      


class geneExpressionStudy ( op ) :
    """ a geneExpressionStudy """
    def __init__(self):
        op.__init__(self)

        # add gene expression study specific help to the AboutMe dictionary that is inherited from
        # the ob base class
        
        self.AboutMe['default'][0]['heading'] = 'BRDF Gene Expression Study Object'
        self.AboutMe['default'][0]['text'] = """
        This page displays a gene expression study object from the BRDF database.
        <p/>
        In the BRDF schema, a study refers to a set of similar observations. A Gene expression study
        refers to a set of observations of the expression of a number of genes. An example of a gene
        expression study is a microarray hybridisation experiment. Another example is a rtPCR
        experiment. For microarrays, a gene expression study groups together a set of obserations
        from one scan, of one hybridisation. Therefore , there may be a set of several gene expression
        studies involved in a given experimental design.

        <p/>
        In the BRDF schema, a gene expression study is a relation between one or more biosamples (e.g. mRNA
        extracts) ; one or more lab resources (for example , a microarray) , and one or more protocols (normally
        including a hybridisation protocol and a scanning protocol). 

        <p/>
        Gene expression study objects are stored in a table called geneexpressionstudy.
        Various types of expression study can be stored in this table - for example, microarray and
        rtPCR. The type of a gene expression study is recorded in the studytype field of this table.
        The current set of types that are supported in this database are recorded in an ontology
        called GENEEXPRESSIONSTUDYTYPE_ONTOLOGY. (You can browse this ontology by selecting ONTOLOGIES
        from the drop down list of search types on the main page, and entering GENEEXPRESSIONSTUDYTYPE_ONTOLOGY
        as the search phrase)

        <p/>
        The details stored in the geneexpressionstudy table are just those that relate to the
        set of observations as a whole. For example, the set of parameters in a GPR header
        are stored at the geneexpressionstudy level.

        </p>
        (The actual expression values observed are stored as observation objects, in tables that
        connect the study, with the things being observed. In the BRDF schema , an observation is a relation between the
        study that the observation belongs to , and the thing observed. For example microarray expression
        data values are stored in a table called microarrayobservation, that relates the study master, to
        each spot on an array ; rtPCR observations are stored in a table called rtpcrobservation
        that relates the gene expression study master , to the primers used in the rtPCR experiment)

        <p/>
        A Gene Expression Study object in the BRDF database has a number of relationships with other types of object
        in the database - for example , it is related to one or more protocols, biosamples and to the observations of
        gene expression. All of the possible relationships that a gene expression object may have
        with other objects in the database are depicted by icons in the information map section of the page.

        The icon is composed of the gene expression study symbol connected to the symbol for the related object
        by a horizontal line. Where the database does not yet contain any related objects for a study,
        the icon for that relationship is greyed out.

        For example if you click on the Microarray spot symbol of the Microarray Observation icon in the
        information map, this will list all of the observations in the study. (To avoid overloading your browser,
        it will only list the first 200 records to the browser, but appends a hyperlink that will download the
        entire report to file.
        <p/>
        We may store various types of facts about a given gene expression study - for example, MIAME details
        of a microarray gene expression study. Each type of fact supported by the BRDF is depicted
        by a line connecting the gene expression study  symbol , to a square box labelled info, with the type of
        fact appearing to the right of the icon. Where the database does not yet contain any facts
        of a given type for a study, the info icon is greyed out
        """                        
        


    def initNew(self,connection):
        
        self.databaseFields = {
            'xreflsid' : None ,
            'studyname' : None ,            
            'studytype' : None,
            'obid' : getNewObid(connection),
            'labresourcelist' : None,
            'biosamplelist' : None,
            'bioprotocolob' : None,
            'labresourceob' : None,
            'studydescription' : None,
            'createdby' : None}

        self.obState.update({'DB_PENDING' : 1})



    def initFromDatabase(self, identifier, connection):
        """ method for initialising microarrayStudy from database"""

        # first init base class - this will get obid
        ob.initFromDatabase(self, identifier, "geneExpressionStudy", connection)

        # now get the complete object
        self.databaseFields = getObjectRecord(connection, "geneExpressionStudy", self.databaseFields['obid'])
        self.obState.update({'ERROR' : 0 , 'NEW' : 0, 'MESSAGE' : "initialised from database OK"})

        # now get the miamefacts
        sql = "select attributename,attributevalue  from miamefact where microarraystudy = %s" % self.databaseFields['obid']
        #print 'executing ' + sql
        obCursor = connection.cursor()
        obCursor.execute(sql)
        miameRows = obCursor.fetchall()
        obCursor.close()
        newVals = dict(miameRows)
        self.databaseFields.update(newVals)     
        
        self.obState.update({'NEW' : 0 , 'DB_PENDING' : 0, 'MESSAGE' : "init from database OK"})
        
            
    def insertDatabase(self,connection):
        """ method used by geneExpressionStudy to save itself to database  """
        
        sql = """
        insert into geneExpressionStudy(obid,xreflsid,labResourceList,labResourceOb,
        bioSampleList, bioProtocolOb,obkeywords,
        studytype,studydescription,createdby,studyname) values
        (%(obid)s,%(xreflsid)s,%(labresourcelist)s,%(labresourceob)s,
        %(biosamplelist)s,%(bioprotocolob)s,%(xreflsid)s,
        %(studytype)s,%(studydescription)s,%(createdby)s,%(studyname)s)"""
        #studymodulelogger.info("executing %s"%(sql%self.databaseFields))
        insertCursor = connection.cursor()
        insertCursor.execute(sql,self.databaseFields)
        connection.commit()
        insertCursor.close()
        self.obState.update({'NEW' : 0 , 'DB_PENDING' : 0, 'MESSAGE' : "database insert OK"})



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
                                        'lastupdatedby','checkedout','checkedoutby','checkoutdate','obkeywords','statuscode') and self.getColumnAlias(key) != None])
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


        if self.obState['DYNAMIC_ANALYSES'] > 0:
            selectlisttuples = ["<option value=%s selected> %s : %s </option>"%(item[9], item[3], item[1]) for item in [self.analysisFunctions[0]] ]
            if len(self.analysisFunctions) > 1:
                selectlisttuples = ["<option value=%s> %s : %s </option>"%(item[9], item[3], item[1]) for item in self.analysisFunctions[1:] ]


            #selectlisttuples = ["<option value=%s> %s : %s </option>"%(item[9], item[3], item[1]) for item in self.analysisFunctions ]
            selectlisthtml = """
            <tr>
            <td colspan=2 align=center>
            <font size="-1"> (to select multiple analyses press the control key and click. To select a block use the shift key and click) </font> <p/>
            <select name="analyses" id="analyses" multiple size=4>
            """\
            +reduce(lambda x,y:x+y+'\n',selectlisttuples,'')\
            + """
            </select>
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
            studymodulelogger.info('running non-virtual display functions')
            for displayFunction in self.displayFunctions:
                # exclude virtual functions - these will be instantiated in specific contexts or subclasses
                if displayFunction[7] == None:
                    studymodulelogger.info('running %s'%displayFunction[0])
                    myGraphHTML = eval(displayFunction[0])
                    table += myGraphHTML        

        
        studymodulelogger.info('listing dictionaries')
        # if we have formatted dictionaries , output these first , they are usually the most interesting
        # content of the object
        if len(ListDictionaryRows) >  0:
            table += ListDictionaryRows

        studymodulelogger.info('listing fields')
        # next the field rows
        table += nonSystemFieldRows

        studymodulelogger.info('listing lists')
        # next the other lists
        if len(ListOtherRows) > 0:
            table += ListOtherRows

        return table
        


    def addFact(self,connection,argfactNameSpace, argattributeName, argattributeValue):
        factFields = {
            'geneExpressionStudy' : self.databaseFields['obid'],
            'factNameSpace' : argfactNameSpace,
            'attributeName' : argattributeName,
            'attributeValue' : argattributeValue }

        # first check if this fact is already in the db - if it is do not duplicate
        sql = """
        select geneExpressionStudy from geneExpressionStudyFact where
        geneExpressionStudy = %(geneExpressionStudy)s and
        factNameSpace = %(factNameSpace)s and
        attributeName = %(attributeName)s and
        attributeValue = %(attributeValue)s
        """
        insertCursor = connection.cursor()
        studymodulelogger.info("checking for fact using %s"%(sql%factFields))
        insertCursor.execute(sql,factFields)
        insertCursor.fetchone()
        studymodulelogger.info("rowcount = %s"%insertCursor.rowcount)
        if insertCursor.rowcount == 0:        
            sql = """
            insert into geneExpressionStudyFact(geneExpressionStudy,factNameSpace, attributeName, attributeValue)
            values(%(geneExpressionStudy)s,%(factNameSpace)s,%(attributeName)s,%(attributeValue)s)
            """
            studymodulelogger.info("executing %s"%(sql%factFields))
            insertCursor.execute(sql,factFields)
            connection.commit()
            insertCursor.close()
            self.obState.update({'NEW' : 0 , 'DB_PENDING' : 0, 'ERROR' : 0, 'MESSAGE' : "database insert OK"})
        else:
            insertCursor.close()        


    
class phenotypeStudy ( op ) :
    """ phenotype study objects """
    def __init__(self):
        op.__init__(self)


    def initNew(self,connection):      
        self.obState.update({'NEW' : 1, 'DB_PENDING' : 1})

        self.databaseFields = {
            'obid' : getNewObid(connection) ,
            'xreflsid' : None,
            'createdby' : None,
            'studyname' : None,
            'studydescription' : None,
            'studydate' : None ,
            'phenotypeontologyname' : None}

    def initFromDatabase(self, identifier, connection):
        """ method for initialising commentob from database """

        # first init base class - this will get obid
        ob.initFromDatabase(self, identifier, "phenotypeStudy", connection)

        # now get the complete object
        self.databaseFields = getObjectRecord(connection, "phenotypeStudy", self.databaseFields['obid'])

    def insertDatabase(self,connection):
        """ method used by phenotype object to save itself to database  """
        sql = """
        insert into phenotypeStudy(obid,xreflsid,createdby,studyname,studydescription,studydate,phenotypeontologyname)
        values(%(obid)s,%(xreflsid)s,%(createdby)s,%(studyname)s,%(studydescription)s,%(studydate)s,%(phenotypeontologyname)s)
        """
        #print "executing " + sql%self.databaseFields
        insertCursor = connection.cursor()
        insertCursor.execute(sql,self.databaseFields)
        connection.commit()
        insertCursor.close()
        self.obState.update({'NEW' : 0 , 'ERROR' : 0, 'DB_PENDING' : 0, 'MESSAGE' : "database insert OK"})
        return

    def addObservation(self,connection,observationData,checkExisting = False):
        observation = phenotypeObservation()
        if checkExisting:
            try:
                observation.initFromDatabase(observationData['xreflsid'],connection)

                # if we obtained an observation then return false
                return (observation, False)                        
            
            except brdfException, msg:
                if observation.obState['ERROR'] != 1:
                    raise brdfException(msg)
                
                    
        # not found or don't care so add it
        observation.initNew(connection)
        observation.databaseFields.update(observationData)
        observation.insertDatabase(connection)
        return (observation, True)



class surveyStudy ( op ) :
    """ survey study objects """
    def __init__(self):
        op.__init__(self)


    def initNew(self,connection):      
        self.obState.update({'NEW' : 1, 'DB_PENDING' : 1})

        self.databaseFields = {
            'obid' : getNewObid(connection) ,
            'xreflsid' : None,
            'createdby' : None,
            'studyname' : None,
            'studydate' : None ,
            'labresourceob' : None}

    def initFromDatabase(self, identifier, connection):
        """ method for initialising surveystudy from database """

        # first init base class - this will get obid
        ob.initFromDatabase(self, identifier, "surveyStudy", connection)

        # now get the complete object
        self.databaseFields = getObjectRecord(connection, "surveyStudy", self.databaseFields['obid'])

    def insertDatabase(self,connection):
        """ method used by surveystudy object to save itself to database  """
        sql = """
        insert into surveyStudy(obid,xreflsid,createdby,studyname,studydate,labresourceob)
        values(%(obid)s,%(xreflsid)s,%(createdby)s,%(studyname)s,%(studydate)s,%(labresourceob)s)
        """
        #print "executing " + sql%self.databaseFields
        insertCursor = connection.cursor()
        insertCursor.execute(sql,self.databaseFields)
        connection.commit()
        insertCursor.close()
        self.obState.update({'NEW' : 0 , 'ERROR' : 0, 'DB_PENDING' : 0, 'MESSAGE' : "database insert OK"})
        return

    def addObservation(self,connection,observationData,checkExisting = False,answerDict=None):
        insertCursor = connection.cursor()
        observation = surveyObservation()
        if checkExisting:
            try:
                observation.initFromDatabase(observationData['xreflsid'],connection)

                # if we obtained an observation then return false
                return (observation, False)                        
            
            except brdfException, msg:
                if observation.obState['ERROR'] != 1:
                    raise brdfException(msg)
                
                    
        # not found or don't care so add it
        observation.initNew(connection)
        observation.databaseFields.update(observationData)
        observation.insertDatabase(connection)

        # if we are to insert individual questions into the fact table, then do so
        if answerDict != None:
            for question in answerDict.keys():
                sql = """
                insert into  surveyQuestionFact(
                    surveyobservation,
                    question,
                    answer)
                values(
                    %(surveyobservation)s,
                    %(question)s,
                    %(answer)s
                )"""
                insertCursor.execute(sql,{
                    'surveyobservation' : observation.databaseFields['obid'],
                    'question' : question,
                    'answer' : answerDict[question]
                })
                connection.commit()
                
                    
        return (observation, True)


    

class genotypeStudy ( op ) :
    """ a genotypeStudy """
    def __init__(self):
        op.__init__(self)


    def initNew(self,connection,obtuple):
        argTemplate1 = [classitem.__name__ for classitem in (labResourceList,bioSampleList,bioProtocolOb)]
        argTemplate2 = [classitem.__name__ for classitem in (labResourceOb,bioSampleList,bioProtocolOb)]
        argTemplate3 = [classitem.__name__ for classitem in (labResourceList,bioSampleOb,bioProtocolOb)]
        argTemplate4 = [classitem.__name__ for classitem in (labResourceOb,bioSampleOb,bioProtocolOb)]                
        argsSupplied = [obitem.__class__.__name__ for obitem in obtuple]

        if (argTemplate1 != argsSupplied) and (argTemplate2 != argsSupplied) and (argTemplate3 != argsSupplied) \
                 and (argTemplate4 != argsSupplied) :
            self.obState.update({'ERROR' : 1 , 'MESSAGE' : "args supplied : " + reduce(lambda x,y:x+" "+ y,argsSupplied) + \
                  " args required : %s or %s or %s or %s"%(reduce(lambda x,y:x+" "+y,argTemplate1),\
                                                           reduce(lambda x,y:x+" "+y,argTemplate2),\
                                                           reduce(lambda x,y:x+" "+y,argTemplate3),\
                                                           reduce(lambda x,y:x+" "+y,argTemplate4)) })
            raise brdfException, self.obState['MESSAGE']       

        if argTemplate1 == argsSupplied:
            self.labResourceList = obtuple[0]
            self.bioSampleList = obtuple[1]            
            self.databaseFields = {
                'xreflsid' : '' , 
                'studytype' : '', 
                'obid' : getNewObid(connection) , 
                'labresourcelist' : obtuple[0].databaseFields['obid'],
                'labresourceob' : None,
                'biosamplelist' : obtuple[1].databaseFields['obid'],
                'biosampleob' : None,
                'bioprotocolob' : obtuple[2].databaseFields['obid']
            }
        elif argTemplate2 == argsSupplied:
            self.labResourceOb = obtuple[0]
            self.bioSampleList = obtuple[1]            
            self.databaseFields = {
                'xreflsid' : '' , 
                'studytype' : '', 
                'obid' : getNewObid(connection) , 
                'labresourceob' : obtuple[0].databaseFields['obid'],
                'labresourcelist' : None,
                'biosamplelist' : obtuple[1].databaseFields['obid'],
                'biosampleob' : None,                
                'bioprotocolob' : obtuple[2].databaseFields['obid']
            }
        elif argTemplate3 == argsSupplied:
            self.labResourceOb = obtuple[0]
            self.bioSampleOb = obtuple[1]            
            self.databaseFields = {
                'xreflsid' : '' , 
                'studytype' : '', 
                'obid' : getNewObid(connection) , 
                'labresourceob' : obtuple[0].databaseFields['obid'],
                'labresourcelist' : None,
                'biosampleob' : obtuple[1].databaseFields['obid'],
                'biosamplelist' : None,                  
                'bioprotocolob' : obtuple[2].databaseFields['obid']
            }
        elif argTemplate4 == argsSupplied:
            self.labResourceOb = obtuple[0]
            self.bioSampleOb = obtuple[1]            
            self.databaseFields = {
                'xreflsid' : '' , 
                'studytype' : '', 
                'obid' : getNewObid(connection) , 
                'labresourceob' : obtuple[0].databaseFields['obid'],
                'labresourcelist' : None,
                'biosampleob' : obtuple[1].databaseFields['obid'],
                'biosamplelist' : None,                  
                'bioprotocolob' : obtuple[2].databaseFields['obid']
            }                  
            

        self.bioProtocolOb = obtuple[2]

        # obsolete from 3/2006 as no longer necessarily a microarray study, and array may not be in the
        # get the microarray used, from the labResourceList
        #sql="select lr.obid from labresourceob lr, labresourcelistmembershiplink lrm \
        #where lrm.labresourcelist = %s and lr.obid = lrm.labresourceob and \
        #lr.resourcetype = 'microarray'"
        #obCursor = connection.cursor()
        #obCursor.execute(sql%self.databaseFields['labResourceList'])
        #resourceRows = obCursor.fetchall()
        #if obCursor.rowcount != 1:
        #    self.obState.update({'ERROR' : 1 , 'MESSAGE' : "Error - could not get microarray used for this study using" + sql%self.databaseFields['labresourcelist']})
        #    raise brdfException, self.obState['MESSAGE']
        #print "**** got array :"
        #print resourceRows
        
        #self.databaseFields['arrayob'] = resourceRows[0][0]
        #obCursor.close()        

        self.obState.update({'DB_PENDING' : 1})



    def initFromDatabase(self, identifier, connection):
        """ method for initialising genotypeStudy from database"""

        # first init base class - this will get obid
        ob.initFromDatabase(self, identifier, "genotypeStudy", connection)

        # now get the complete object
        self.databaseFields = getObjectRecord(connection, "genotypeStudy", self.databaseFields['obid'])
        self.obState.update({'ERROR' : 0 , 'NEW' : 0, 'MESSAGE' : "initialised from database OK"})


        # obsolete from 3/2006 as no longer necessarily a microarray study, and array may not be in the
        # list member
        # get the microarray used, from the labResourceList
        #sql="select lr.obid from labresourceob lr, labresourcelistmembershiplink lrm \
        #where lrm.labresourcelist = %s and lr.obid = lrm.labresourceob and \
        #lr.resourcetype = 'microarray'"
        #obCursor = connection.cursor()
        #obCursor.execute(sql%self.databaseFields['labresourcelist'])
        #resourceRows = obCursor.fetchall()
        #if obCursor.rowcount != 1:
        #    self.obState.update({'ERROR' : 1 , 'MESSAGE' : "Error - could not get microarray used for this study using" + sql%self.databaseFields['labresourcelist']})
        #    raise brdfException, self.obState['MESSAGE']
        
        #self.databaseFields['arrayob'] = resourceRows[0][0]
        #obCursor.close()
            
        
        self.obState.update({'NEW' : 0 , 'DB_PENDING' : 0, 'MESSAGE' : "init from database OK"})
        
            
    def insertDatabase(self,connection):
        """ method used by genotypeStudy to save itself to database  """
        
        sql = """
        insert into genotypeStudy(obid,xreflsid,labResourceList,labresourceob,
        bioSampleList, biosampleob,bioProtocolOb,
        obkeywords,studytype) values
        (%(obid)s,%(xreflsid)s,%(labresourcelist)s,%(labresourceob)s,%(biosamplelist)s,%(biosampleob)s,
        %(bioprotocolob)s,%(xreflsid)s,%(studytype)s)"""
        #print 'executing ' + sql%self.databaseFields
        insertCursor = connection.cursor()
        insertCursor.execute(sql,self.databaseFields)
        connection.commit()
        insertCursor.close()
        self.obState.update({'NEW' : 0 , 'ERROR' : 0, 'DB_PENDING' : 0, 'MESSAGE' : "database insert OK"})

            
    def addObservation(self,connection,observationData):
        observation = genotypeObservation()
        try:
            observation.initFromDatabase(observationData['xreflsid'],connection)

            # if we obtained an observation then return false
            return (observation, False)                        
            
        except brdfException, msg:
            if observation.obState['ERROR'] == 1:
                # not found so add it
                observation.initNew(connection)
                observation.databaseFields.update(observationData)
                observation.insertDatabase(connection)
                return (observation, True)
            else:
                raise brdfException, observation.obState['MESSAGE']                        

    def updateObservation(self,connection,observationData):
        
        observation = genotypeObservation()
        
        observation.initFromDatabase(observationData['xreflsid'],connection)

        # if we obtained an observation then compare the data passed to us with the
        # data in the DB
        studymodulelogger.info("comparing old and new genotype records....")
        # compare old and new records
        comparison = {}
        for key in ['genotypeobserved','genotypeobserveddescription','finalgenotype','finalgenotypedescription','observationcomment']:
            if str(observation.databaseFields[key]).strip() != str(observationData[key]).strip():
                #studymodulelogger.info("Warning : updexisting genotypeobservation has changed (DB was *not* updated)  : %s \n=>\n%s"%(str(observation.databaseFields),str(observationData)))
                comparison[key] = '%s --> %s'%(observation.databaseFields[key],observationData[key])

        # if update required do it and attach comments
        if len(comparison) > 0:
            observation.databaseFields.update(observationData)
            observation.updateDatabase(connection,comparison.keys())

            # attach a comment describing the update
            comment = commentOb()
            comment.initNew(connection)
            comment.databaseFields.update(
            {
                'createdby' : 'system',
                'commentstring' : "The following updates have been done : %s"%str(comparison),
                'xreflsid' : "%s.comment"%observation.databaseFields['xreflsid']
            })
            comment.insertDatabase(connection)
            comment.createLink(connection,observation.databaseFields['obid'],'system','#EDA7A7')
      
            return (observation, True)
        else:
            return (observation, False)
            
    


class genotypeObservation ( op ) :
    """ genotype observation """
    def __init__(self):
        op.__init__(self)


    def initFromDatabase(self, identifier, connection):
        """ method for initialising genotype observation from database """

        # first init base class - this will get obid
        ob.initFromDatabase(self, identifier, "genotypeObservation", connection)

        # now get the complete object
        self.databaseFields = getObjectRecord(connection, "genotypeObservation", self.databaseFields['obid'])

    def initNew(self,connection):
        self.databaseFields = {
            'obid' : getNewObid(connection),
            'xreflsid' : None,
            'genotypestudy' : None,
            'genetictestfact' : None,
            'observationdate' : None,
            'genotypeobserved' : None,
            'genotypeobserveddescription' : None,
            'finalgenotype' :None,
            'finalgenotypedescription' :None,
            'observationcomment' : None}

        self.obState.update({'DB_PENDING' : 1})        

    def insertDatabase(self,connection):
        sql = """
            insert into genotypeobservation(
                obid  ,
                xreflsid ,
                genotypestudy ,
                genetictestfact,
                observationdate ,
                genotypeobserved ,
                genotypeobserveddescription ,
                finalgenotype ,
                finalgenotypedescription ,
                observationcomment)
            values(
                %(obid)s  ,
                %(xreflsid)s ,
                %(genotypestudy)s ,
                %(genetictestfact)s,
                to_date(%(observationdate)s,'dd-mm-yyyy') ,
                %(genotypeobserved)s ,
                %(genotypeobserveddescription)s ,
                %(finalgenotype)s ,
                %(finalgenotypedescription)s ,
                %(observationcomment)s
            )"""
        #print 'executing ' + sql%self.databaseFields
        insertCursor = connection.cursor()
        insertCursor.execute(sql,self.databaseFields)
        connection.commit()
        insertCursor.close()
        self.obState.update({'NEW' : 0 , 'DB_PENDING' : 0, 'MESSAGE' : "database insert OK"})


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

            // note that the edit URL for this object contains "" characters - hence single quotes used here
            window.open('%(editURL)s'+anchor);
            // modified 1/8/2008 to cause the edit form to open in a new window
            //return location.href="%(editURL)s"+anchor;
        }
        
        var editItemArray = new Array();
        editItemArray[0] = new Array("editButton(\"\");","Edit Genotype");
        
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
    

        

    def updateDatabase(self,connection,fieldsToUpdate = None):
        """ apply the database fields in this object to the database """
        updateExpressions = {
            'observationdate' : "to_date(%(observationdate)s,'dd-mm-yyyy') ",
            'genotypeobserved' : "%(genotypeobserved)s ",
            'genotypeobserveddescription' : "%(genotypeobserveddescription)s ",
            'finalgenotype' : "%(finalgenotype)s ",
            'finalgenotypedescription' : "%(finalgenotypedescription)s ",
            'observationcomment' : "%(observationcomment)s ",
            'lastupdateddate' : "now()",
            "lastupdatedby" : "%(lastupdatedby)s"
        }
        if fieldsToUpdate == None:
            fieldsToUpdate = updateExpressions.keys()

        requiredFields = [ 'lastupdateddate' ]
        for field in requiredFields:
            if field not in fieldsToUpdate:
                fieldsToUpdate.append(field)
            
        updateClause = reduce(lambda x,y : x + "," + y, ["%s = %s"%(field,updateExpressions[field]) for field in fieldsToUpdate] )
            
                    
        sql = """
            update genotypeobservation
            set
                %s
            where
                obid = %s
            """%(updateClause, self.databaseFields['obid'])
        
                
        #print 'executing ' + sql%self.databaseFields
        studymodulelogger.info("updating genotypeobservation using %s"%(sql%self.databaseFields))        
        updateCursor = connection.cursor()
        updateCursor.execute(sql,self.databaseFields)
        connection.commit()
        updateCursor.close()
        self.obState.update({'NEW' : 0 , 'DB_PENDING' : 0, 'MESSAGE' : "database insert OK"})        
        

    
    
class phenotypeObservation ( op ) :
    """ phenotype observation """
    def __init__(self):
        op.__init__(self)


    def initNew(self,connection):
        self.databaseFields = {
            'obid' : getNewObid(connection),
            'xreflsid' : None,
            'phenotypestudy' : None,
            'biosampleob' : None,
            'biosamplelist' : None,
            'biosubjectob' : None,
            'phenotypenamespace' : None,
            'phenotypeterm' : None,
            'phenotyperawscore' : None,
            'phenotypeadjustedscore' : None,
            'observationcomment' : None,
            'observationdate' : None}
        self.obState.update({'DB_PENDING' : 1})                


    def initFromDatabase(self, identifier, connection):
        """ method for initialising phenotype observatin from database """

        # first init base class - this will get obid
        ob.initFromDatabase(self, identifier, "phenotypeObservation", connection)

        # now get the complete object
        self.databaseFields = getObjectRecord(connection, "phenotypeObservation", self.databaseFields['obid'])


    def insertDatabase(self,connection):
        sql = """
            insert into phenotypeobservation(
            obid,
            xreflsid,
            phenotypestudy,
            biosampleob,
            biosamplelist,
            biosubjectob,
            phenotypenamespace,
            phenotypeterm,
            phenotyperawscore,
            phenotypeadjustedscore,
            observationcomment,
            observationdate)
            values(
            %(obid)s,
            %(xreflsid)s,
            %(phenotypestudy)s,
            %(biosampleob)s,
            %(biosamplelist)s,
            %(biosubjectob)s,
            %(phenotypenamespace)s,
            %(phenotypeterm)s,
            %(phenotyperawscore)s,
            %(phenotypeadjustedscore)s,
            %(observationcomment)s,
            to_date(%(observationdate)s,'dd-mm-yyyy')
            )"""
        #print 'executing ' + sql%self.databaseFields
        insertCursor = connection.cursor()
        studymodulelogger.info("executing %s"%(sql%self.databaseFields))
        insertCursor.execute(sql,self.databaseFields)
        connection.commit()
        insertCursor.close()
        self.obState.update({'NEW' : 0 , 'DB_PENDING' : 0, 'MESSAGE' : "database insert OK"})        




class surveyObservation ( op ) :
    """ survey observation """
    def __init__(self):
        op.__init__(self)


    def initNew(self,connection):
        self.databaseFields = {
            'obid' : getNewObid(connection),
            'xreflsid' : None,
            'suveystudy' : None,
            'biosubjectob' : None,
            'rawdatarecord' : None,
            'observationcomment' : None,
            'observationdate' : None}
        self.obState.update({'DB_PENDING' : 1})                


    def initFromDatabase(self, identifier, connection):
        """ method for initialising survey observation from database """

        # first init base class - this will get obid
        ob.initFromDatabase(self, identifier, "surveyObservation", connection)

        # now get the complete object
        self.databaseFields = getObjectRecord(connection, "surveyObservation", self.databaseFields['obid'])


    def insertDatabase(self,connection):
        sql = """
            insert into surveyobservation(
            obid,
            xreflsid,
            surveystudy,
            biosubjectob,
            rawdatarecord,
            observationcomment,
            observationdate)
            values(
            %(obid)s,
            %(xreflsid)s,
            %(surveystudy)s,
            %(biosubjectob)s,
            %(rawdatarecord)s,
            %(observationcomment)s,
            to_date(%(observationdate)s,'dd-mm-yyyy')
            )"""
        #print 'executing ' + sql%self.databaseFields
        insertCursor = connection.cursor()
        studymodulelogger.info("executing %s"%(sql%self.databaseFields))
        insertCursor.execute(sql,self.databaseFields)
        connection.commit()
        insertCursor.close()
        self.obState.update({'NEW' : 0 , 'DB_PENDING' : 0, 'MESSAGE' : "database insert OK"})        





class microarrayObservation ( op ) :
    """ microarray observation """
    def __init__(self):
        op.__init__(self)


        # add microarray observation specific help to the AboutMe dictionary that is inherited from
        # the ob base class
        
        self.AboutMe['default'][0]['heading'] = 'BRDF Microarray Observation Object'
        self.AboutMe['default'][0]['text'] = """
        This page displays a microarray observation object from the BRDF database.
        <p/>
        In the BRDF schema, a study refers to a set of similar observations. A Gene expression study
        refers to a set of observations of the expression of a number of genes. An example of a gene
        expression study is a microarray hybridisation experiment. Another example is a rtPCR
        experiment. For microarrays, a gene expression study groups together a set of obserations
        from one scan, of one hybridisation. Therefore , there may be a set of several gene expression
        studies involved in a given experimental design.

        <p/>
        In the BRDF schema, a gene expression study is a relation between one or more biosamples (e.g. mRNA
        extracts) ; one or more lab resources (for example , a microarray) , and one or more protocols (normally
        including a hybridisation protocol and a scanning protocol). 

        <p/>
        Gene expression study objects are stored in a table called geneexpressionstudy.
        Various types of expression study can be stored in this table - for example, microarray and
        rtPCR. The type of a gene expression study is recorded in the studytype field of this table.
        The current set of types that are supported in this database are recorded in an ontology
        called GENEEXPRESSIONSTUDYTYPE_ONTOLOGY. (You can browse this ontology by selecting ONTOLOGIES
        from the drop down list of search types on the main page, and entering GENEEXPRESSIONSTUDYTYPE_ONTOLOGY
        as the search phrase)

        <p/>
        The details stored in the geneexpressionstudy table are just those that relate to the
        set of observations as a whole. For example, the set of parameters in a GPR header
        are stored at the geneexpressionstudy level.

        </p>
        In the BRDF schema , an observation is a relation between the
        study that the observation belongs to , and the thing observed. For example microarray expression
        data values are stored in a table called microarrayobservation, that relates the study master, to
        each spot on an array ; rtPCR observations are stored in a table called rtpcrobservation
        that relates the gene expression study master , to the primers used in the rtPCR experiment)

        <p/>
        A microarray observation object in the BRDF database has a number of relationships with other types of object
        in the database - for example , it is related to the gene expression study parent record ; it is related to the
        microarray spot that is being observed in the experiment. All of the possible relationships that a microarray observation
        object may have with other objects in the database are depicted by icons in the information map section of the page.

        The icon is composed of the microarray observation symbol connected to the symbol for the related object
        by a horizontal line. Where the database does not yet contain any related objects for an observation,
        the icon for that relationship is greyed out.

        For example if you click on the Microarray spot symbol of the Microarray Observation icon in the
        information map, this will report the spot that the observation relates to , including
        a hyperlink so that you can open a BRDF database page for that spot.
    
        <p/>
        We may store various types of facts about a given microarray spot. Each type of fact supported by the BRDF is depicted
        by a line connecting the microarray observaiton symbol , to a square box labelled info, with the type of
        fact appearing to the right of the icon. Where the database does not yet contain any facts
        of a given type for an observation, the info icon is greyed out


        <p/>
        """
        self.AboutMe['default'].update ( {
            1 : {
                'heading' : 'BRDF Microarray Observation Graphics',
                'text' : """
            The BRDF provides a simple bar graph for each microarray observation, that is intended
            to provide an overview of the expression measured for this spot in other experiments, as
            well as the one being viewed. Thus expression profiles of different spots across many
            experiments can be visually contrasted.
            <p/>
            All experiments in the database that used the same array as the one being viewed , are
            queried (unless access is restricted) , and intensity and logratios are retrieved from
            all experiments on the fly , and displayed in the form of a bar graph. The experiment
            being viewed is highlighted in red. Clicking on other bars will retrieve the
            observation record for that other study, and the red highlight will shift accordingly.
            <p/>
            Where available , normalised  values are graphed in addition to raw values.
            <p/>
            The ordering of the experiments is based on simple lexical ordering of the experiment names.
            If you hold the mouse over a bar, a tool-tip popup should appear giving the name of
            the experiment.
            <p>
            The scale used for the graph is linear
            """
            }
        })
        


    def initFromDatabase(self, identifier, connection):
        """ method for initialising microarray observation from database """

        # first init base class - this will get obid
        op.initFromDatabase(self, identifier, "microarrayObservation", connection)

        # now get the complete object
        self.databaseFields = getObjectRecord(connection, "microarrayObservation", self.databaseFields['obid'])

        self.obState.update({'ERROR' : 0 , 'NEW' : 0, 'MESSAGE' : "initialised from database OK"})
        

        # get virtual displayfunctions - i.e. are linked to parent objects
        sql = """
        select
            df.invocation,
            df.functioncomment,
            dp.xreflsid,
            dp.procedurename,
            ds.datasourcename,
            ds.physicalsourceuri,
            ds.datasourcetype,
            df.voptypeid
        from
            (displayfunction df join displayprocedureob dp on
            df.displayprocedureob = dp.obid) left outer join
            datasourceob ds on ds.obid = df.datasourceob
        where
            df.ob = %(microarraystudy)s and
            df.voptypeid is not null
        """
        studymodulelogger.info('executing SQL to retrieve virtual dynamic display functions : %s'%str(sql%self.databaseFields))
        displayCursor = connection.cursor()
        displayCursor.execute(sql,self.databaseFields)
        self.virtualDisplayFunctions = displayCursor.fetchall()
        studymodulelogger.info(str(self.virtualDisplayFunctions))

        if displayCursor.rowcount > 0:
            self.obState.update({'VIRTUAL_DYNAMIC_DISPLAYS' : displayCursor.rowcount , 'MESSAGE' : "virtual dynamic displays initialised from database OK"})        
        
        


        


    def addFact(self,connection,argfactNameSpace, argattributeName, argattributeValue, checkExisting = True):
        factFields = {
            'microarrayObservation' : self.databaseFields['obid'],
            'factNameSpace' : argfactNameSpace,
            'attributeName' : argattributeName,
            'attributeValue' : argattributeValue }
        
        doinsert = True
        insertCursor = connection.cursor()

        # first check if this fact is already in the db - if it is do not duplicate (if asked to do this)
        if checkExisting:
            sql = """
            select microarrayObservation from microarrayObservationFact where
            microarrayobservation = %(microarrayObservation)s and
            factNameSpace = %(factNameSpace)s and
            attributeName = %(attributeName)s and
            attributeValue = %(attributeValue)s
            """
            #studymodulelogger.info("checking for fact using %s"%(sql%factFields))
            insertCursor.execute(sql,factFields)
            insertCursor.fetchone()
            #studymodulelogger.info("rowcount = %s"%insertCursor.rowcount)
            if insertCursor.rowcount == 0:
                doinsert = True
            else:
                doinsert = False

        if doinsert:
            sql = """
            insert into microarrayObservationFact(microarrayobservation,factNameSpace, attributeName, attributeValue)
            values(%(microarrayObservation)s,%(factNameSpace)s,%(attributeName)s,%(attributeValue)s)
            """
            #studymodulelogger.info("executing %s"%(sql%factFields))
            insertCursor.execute(sql,factFields)
            connection.commit()
            insertCursor.close()
            self.obState.update({'NEW' : 0 , 'DB_PENDING' : 0, 'ERROR' : 0, 'MESSAGE' : "database insert OK"})
        else:
            insertCursor.close()
        

        
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
                                        'lastupdatedby','checkedout','checkedoutby','checkoutdate','obkeywords','statuscode') and self.getColumnAlias(key) != None])
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
                                  


        # execute any linked display procedures : test code
        #table += eval('getGenepixThumbnailDisplay("C:/temp/test.jpg",usercontext=context,fetcher=self.fetcher, imagepath=self.imagepath, tempimageurl=self.tempimageurl, sectionheading="Spot Images" ,headerData=None,spotData=None,thumbcount=3,thumbdimensions=(20,20),zoomincrement=50)')
        # obtain display procedures that are linked to the parent study object , and have the virtual flag set

        # these are now obtained at object initialisation
        #sql = """
        #select
        #    df.invocation,
        #    df.functioncomment,
        #    dp.xreflsid,
        #    dp.procedurename,
        #    ds.datasourcename,
        #    ds.physicalsourceuri,
        #    ds.datasourcetype,
        #    df.voptypeid
        #from
        #    (displayfunction df join displayprocedureob dp on
        #    df.displayprocedureob = dp.obid) left outer join
        #    datasourceob ds on ds.obid = df.datasourceob
        #where
        #    df.ob = %(microarraystudy)s and
        #    df.voptypeid is not null
        #"""
        #studymodulelogger.info('executing SQL to retrieve dynamic display functions : %s'%str(sql%self.databaseFields))
        connection = databaseModule.getConnection()
        #displayCursor = connection.cursor()
        #displayCursor.execute(sql,self.databaseFields)
        #displayFunctions = displayCursor.fetchall()
        #studymodulelogger.info(str(displayFunctions))
        # test code :
        #myGraphHTML = eval('getGenepixThumbnailDisplay(jpegfilename="C:/working/zaneta/9072 ratio 1 mid scan .jpg",xy=re.split("\t",self.databaseFields["rawdatarecord"])[5:7],usercontext=context,fetcher=self.fetcher, imagepath=self.imagepath, tempimageurl=self.tempimageurl, sectionheading="Spot Images" ,pixelsize=10,xyoffset=(780, 12780),thumbcount=3,thumbdimensions=(20,20),zoomincrement=50)')
        #table += myGraphHTML         
        for displayFunction in self.virtualDisplayFunctions:
            myGraphHTML = eval(displayFunction[0])
            table += myGraphHTML



        studymodulelogger.info('checking whether graphic can be made of expression values')            

        #### !! note this should be replaced at some stage by a dynamically linked display procedure !! ####
        studymodulelogger.info('checking whether graphic can be made of expression values')
        # if the data source type for this microarray experiment is GPRFile then we try
        # to graph the logratios from all observations of this spot.
        #connection = databaseModule.getConnection()
        graphCursor = connection.cursor()
        sql= """
        select
           d.datasourcetype
        from
           ((microarrayobservation mo join geneexpressionstudy ges
           on ges.obid = mo.microarraystudy ) join
           importfunction if on if.ob = ges.obid ) join
           datasourceob d on d.obid = if.datasourceob
        where
           mo.obid = %s
           """%self.databaseFields['obid']
        studymodulelogger.info("executing %s"%str(sql))
        graphCursor.execute(sql)
        record=graphCursor.fetchone()
        if graphCursor.rowcount == 1:
            if record[0] in ['GPRFile','AgResearchArrayExport1']:

                # get and graph the log ratios from all observations related to this spot.
                #sql = """
                #select mo.gpr_logratio,
                #mo.xreflsid,
                #mo.obid,
                #(mo.gpr_dye1foregroundmean + mo.gpr_dye2foregroundmean)/2.0 as averagefg
                #from
                #microarrayobservation mo
                #where
                #microarrayspotfact = %s order by
                #mo.xreflsid"""%self.databaseFields['microarrayspotfact']
                sql = """
                select mo.gpr_logratio,
                mo.xreflsid,
                mo.obid,
                (mo.gpr_dye1foregroundmean + mo.gpr_dye2foregroundmean)/2.0 as averagefg
                from
                (geneexpressionstudy ges join microarrayobservation mo
                on
                ges.obid = mo.microarraystudy) left outer join geneexpressionstudyfact gesf on
                gesf.geneexpressionstudy = ges.obid and
                gesf.factnamespace = 'BRDF Default Interface Configuration' and
                gesf.attributename = 'Bar graph experiment order'
                where
                microarrayspotfact = %s order by
                to_number(gesf.attributevalue,'999999'), mo.xreflsid"""%self.databaseFields['microarrayspotfact']

                
                graphCursor.execute(sql)
                datatuples = graphCursor.fetchall()

                # find out which of these items corresponds to this spot
                myindex = 0
                for datatuple in datatuples:
                    if datatuple[2] == self.databaseFields['obid']:
                        break
                    myindex += 1

                # get the obids and save for later use
                observationids = [ item[2] for item in datatuples ]                    

                # each tuple contain a fetch URL - initialise this
                logratiodatatuples = [ (item[0],item[1], self.fetcher + "?context=%s&obid=%s&target=ob"%(context,item[2])) \
                                for item in datatuples ]
                #datatuples = [(item[0],item[1]) for item in datatuples]
                    
                if graphCursor.rowcount > 0:
                    (myGraphName,myGraphMap) = makeBarGraph(imageDirectory=self.imagepath,datatuples=logratiodatatuples,currenttuple=myindex,label1="All raw LogRatios",label2="for this spot",barwidth=5)
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
                    table += """
                <tr> <td colspan="2" class=tableheading> 
                %s
                </td>
                </tr>
                """%"All observed logratios and intensities for this gene, in experiments using this chip"
                    table +=  myGraphHTML


                # graph the intensities 


                
                # each tuple contain a fetch URL - initialise this
                intensitydatatuples = [ (int(item[3]),item[1], self.fetcher + "?context=%s&obid=%s&target=ob"%(context,item[2])) \
                                for item in datatuples ]
                #datatuples = [(item[0],item[1]) for item in datatuples]
                    
                if graphCursor.rowcount > 0:
                    (myGraphName,myGraphMap) = makeBarGraph(imageDirectory=self.imagepath,datatuples=intensitydatatuples,currenttuple=myindex,label1="All average foreground",label2="intensities for this spot",barwidth=5)
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
                    table +=  myGraphHTML


                # we now see whether there are any normalised values that we should graph.
                # the available normalised values are stored in an ontology called
                # MICROARRAY_NORMALISED_VALUES.
                #sql = """
                #select otf.termName , otf.unitname from
                #ontologyob ot join ontologytermfact otf
                #on otf.ontologyob = ot.obid
                #where
                #ot.ontologyname = 'MICROARRAY_NORMALISED_VALUES'
                #order by otf.termName
                #"""
                #studymodulelogger.info("getting normalised data point names using %s"%sql)
                #graphCursor.execute(sql)
                #datapoints = graphCursor.fetchall()


                # we now see whether there are any normalised values that we should graph.
                # the available normalised values are stored in an ontology called
                # MICROARRAY_NORMALISED_VALUES.

                # first get the ontology - for some reason, if you do this in a subquery
                # of the next query performance is horrible (and even worse if you do this in a join)
                sql = """
                select obid from ontologyob where
                ontologyname = 'MICROARRAY_NORMALISED_VALUES'
                """
                studymodulelogger.info("getting normalised data point ontology using %s"%sql)
                graphCursor.execute(sql)
                studymodulelogger.info("done executing, fetching...")
                ontology = graphCursor.fetchone()[0]

                # now get the terms from the ontology
                sql = """
                select otf.termName , otf.unitname from
                ontologytermfact otf where
                ontologyob = %s
                order by otf.termName
                """%ontology
                studymodulelogger.info("getting normalised data point names using %s"%sql)
                graphCursor.execute(sql)
                studymodulelogger.info("done executing, fetching...")
                datapoints = graphCursor.fetchall()
                studymodulelogger.info("done fetching, got...%s"%str(datapoints))


                
                for (datapoint, datatype) in datapoints:
                    # obtain the data points - we re-use the above array of data tuples, since they
                    # contain the correct tooltips and urls - just change the data point value
                    skipdatapoint = False
                    for iobservation in range(0, len(observationids)):
                        sql = """
                        select case when attributeValue is null then '' else attributeValue end
                        from microarrayobservationfact
                        where
                        microarrayobservation = %s and
                        factNameSpace = 'NORMALISED VALUE' and
                        attributeName = '%s'
                        """%(observationids[iobservation],datapoint)
                        studymodulelogger.info("getting normalised data points using %s"%sql)
                        graphCursor.execute(sql)
                        datapointvalue=graphCursor.fetchone()

                        
                        if graphCursor.rowcount == 1:
                            if datapointvalue[0] == None:
                                datatuples[iobservation] = \
                                    (None, datatuples[iobservation][1], logratiodatatuples[iobservation][2])                               
                            elif len(datapointvalue[0]) == 0:
                                datatuples[iobservation] = \
                                    (None, datatuples[iobservation][1], logratiodatatuples[iobservation][2])   
                            else:
                                datatuples[iobservation] = \
                                    (float(datapointvalue[0]), datatuples[iobservation][1], logratiodatatuples[iobservation][2])   
                        else:
                            skipdatapoint = True
                            studymodulelogger.info("skipping data point - query returned no rows")
                            break # we got nothing for this observation - incomplete dataset, give up
                            

                    # if all values missing, skip the whole data point
                    notMissing = [ datatuple[0] for datatuple in datatuples if datatuple[0] != None]
                    if len(notMissing) ==0:
                        skipdatapoint = True


                    if not skipdatapoint:
                        (myGraphName,myGraphMap) = makeBarGraph(imageDirectory=self.imagepath,datatuples=datatuples,currenttuple=myindex,label1="Normalisation:",label2=datapoint,barwidth=5)
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
                        table +=  myGraphHTML


            elif record[0] in ['CSV from Affy CEL File']:
                studymodulelogger.info("attempting to display Affy experiment results")

                # get and graph the individual probe values, store in a raw data record like this :
                # [('AFFX-Bt-NM_131175-1_at1', '498', '177'), ('AFFX-Bt-NM_131175-1_at2', '65', '257'),
                # ('AFFX-Bt-NM_131175-1_at3', '180', '100'), ('AFFX-Bt-NM_131175-1_at4', '122', '157'), ('AFFX-Bt-NM_131175-1_at5', '158', '99'), ('AFFX-Bt-NM_131175-1_at6
                #', '211', '103'), ('AFFX-Bt-NM_131175-1_at7', '59', '85'), ('AFFX-Bt-NM_131175-1
                #_at8', '48', '67'), ('AFFX-Bt-NM_131175-1_at9', '139', '126'), ('AFFX-Bt-NM_1311
                #75-1_at10', '118', '86'), ('AFFX-Bt-NM_131175-1_at11', '51', '52')]
                datatuples = eval(self.databaseFields['rawdatarecord'])

                #!!!! get the obids of each of these probsets - still to do as not avaialable on dev laptop
                pmdatatuples = [ (float(item[2]),item[0], "") for item in datatuples ]
                if len(pmdatatuples) > 0:


                    # get the obids of each of the probes in the probeset so we can link to them. We have to assume that
                    # the interrogation position ordering is the same as the numbering of these
                    sql = """
                    select
                       subjectob ,
                       bs.xreflsid,
                       bf.attributevalue,
                       bs.seqstring
                    from
                       (biosequencefact bf join predicatelink p on
                       bf.biosequenceob = p.subjectob and
                       bf.attributename = 'probe interrogation position' and
                       bf.factnamespace = 'Affy Probe Details') join
                       biosequenceob bs on bs.obid = p.subjectob 
                    where
                       p.objectob = %(microarrayspotfact)s and
                       p.predicate = 'AFFYPROBE-ARRAYPROBESET'
                    """%self.databaseFields
                    studymodulelogger.info("executing %s"%str(sql))
                    graphCursor.execute(sql)
                    probetuples = graphCursor.fetchall()
                    studymodulelogger.info("..done executing have data")
                    studymodulelogger.info(str(probetuples))

                    # attempt to sort the probes by their numeric interrogation position - if we can't
                    # then erase them as they are unuseable
                    try:
                        probetuples.sort(lambda x,y:int(x[2]) - int(y[2]))
                    except Exception,msg:
                        studymodulelogger.info("exception trying to sort probes on interrogation position : %s"%msg)
                        probetuples = []

                    if len(probetuples) == len(pmdatatuples):
                        # we can construct links
                        pmdatatuples = zip([ item[0] for item in pmdatatuples], ["%s ( %s )"%(pitem[1],pitem[3]) for pitem in probetuples],\
                                       [self.fetcher + "?context=%s&obid=%s&target=ob"%(context,oitem[0]) for oitem in probetuples]) 

                    #pmdatatuples = [ (float(item[1]),item[0], "") for item in datatuples ]
                    studymodulelogger.info(str(pmdatatuples))
                        

        
                    table += """
                    <tr> <td colspan="2" class=tableheading> 
                    %s
                    </td>
                    </tr>
                    """%"Individual probe values for probes in probset"
                    (myGraphName,myGraphMap) = makeBarGraph(imageDirectory=self.imagepath,datatuples=pmdatatuples,label1="Probe PM Values",label2="for probes in probeset",barwidth=5,colourScheme=1)
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
                    table +=  myGraphHTML                      
                    mmdatatuples = [ (float(item[1]),item[0], self.fetcher + "?context=%s&obid=%s&target=ob"%(context,item[0])) \
                                    for item in datatuples ]
                    (myGraphName,myGraphMap) = makeBarGraph(imageDirectory=self.imagepath,datatuples=mmdatatuples,label1="Probe MM Values",label2="for probes in probeset",barwidth=5,colourScheme=1)
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
                    table +=  myGraphHTML                                    
                


                # get and graph the log ratios from all observations related to this spot.
                sql = """
                select
                 mo.affy_meanpm,
                 mo.affy_meanmm,
                 mo.affy_stddevpm,
                 mo.affy_stddevmm,
                 mo.affy_count,
                 mo.xreflsid,
                 mo.obid
                from
                microarrayobservation mo 
                where
                microarrayspotfact = %s order by
                mo.xreflsid"""%self.databaseFields['microarrayspotfact']
                studymodulelogger.info("executing %s"%str(sql))
                graphCursor.execute(sql)
                datatuples = graphCursor.fetchall()
                studymodulelogger.info("..done executing have data")

                # find out which of these items corresponds to this spot
                myindex = 0
                for datatuple in datatuples:
                    if datatuple[6] == self.databaseFields['obid']:
                        break
                    myindex += 1            


                observationids = [ item[6] for item in datatuples ]
                # each tuple contain a fetch URL - initialise this
                pmdatatuples = [ (item[0],item[5], self.fetcher + "?context=%s&obid=%s&target=ob"%(context,item[6])) \
                                    for item in datatuples ]
                #datatuples = [(item[0],item[1]) for item in datatuples]
                if graphCursor.rowcount > 0:
                    #PM means
                    (myGraphName,myGraphMap) = makeBarGraph(imageDirectory=self.imagepath,datatuples=pmdatatuples,currenttuple=myindex,label1="All Probeset mean PM",label2="for this probeset",barwidth=5)
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
                    table += """
                    <tr> <td colspan="2" class=tableheading> 
                    %s
                    </td>
                    </tr>
                    """%"All observed probeset means and standard deviations for this probeset, across experiments using this chip"
                    table +=  myGraphHTML

                    #PM stddev
                    pmdatatuples = [ (item[2],item[5], self.fetcher + "?context=%s&obid=%s&target=ob"%(context,item[6])) \
                        for item in datatuples ]
                    (myGraphName,myGraphMap) = makeBarGraph(imageDirectory=self.imagepath,datatuples=pmdatatuples,currenttuple=myindex,label1="All Probeset stddev PM",label2="for this probeset",barwidth=5)
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
                    table +=  myGraphHTML
                    
                
                    
        graphCursor.close()

        
        studymodulelogger.info('listing dictionaries')
        # if we have formatted dictionaries , output these first , they are usually the most interesting
        # content of the object
        if len(ListDictionaryRows) >  0:
            table += ListDictionaryRows

        studymodulelogger.info('listing fields')
        # next the field rows
        table += nonSystemFieldRows

        studymodulelogger.info('listing lists')
        # next the other lists
        if len(ListOtherRows) > 0:
            table += ListOtherRows

        return table
        
        

class bioProtocolOb ( ob ) :
    """ a list of objects """
    def __init__(self):
        ob.__init__(self)


    def initNew(self,connection):
        self.obState.update({'NEW' : 1, 'DB_PENDING' : 1})        
        self.databaseFields = {
            'obid' : getNewObid(connection) ,
            'xreflsid' : None,
            'protocolname' : None,
            'protocoltype' : None,
            'protocoldescription' : None,
            'protocoltext' : None}
        

    def initFromDatabase(self, identifier, connection):
        """ method for initialising bioProtocolOb from database """

        # first init base class - this will get obid
        ob.initFromDatabase(self, identifier, "bioProtocolOb", connection)

        # now get the complete object
        self.databaseFields = getObjectRecord(connection, "bioProtocolOb", self.databaseFields['obid'])


    def insertDatabase(self,connection):
        """ method used by bioprotocolob object to save itself to database  """
        sql = """
        insert into bioprotocolob(obid,xreflsid,protocolname,protocoltype,
        protocoldescription,protocoltext)
        values(%(obid)s,%(xreflsid)s,%(protocolname)s,%(protocoltype)s,
        %(protocoldescription)s,%(protocoltext)s)
        """
        #print "executing " + sql%self.databaseFields
        insertCursor = connection.cursor()
        insertCursor.execute(sql,self.databaseFields)
        connection.commit()
        insertCursor.close()
        self.obState.update({'NEW' : 0 , 'ERROR' : 0, 'DB_PENDING' : 0, 'MESSAGE' : "database insert OK"})
        return



class bioDatabaseOb ( ob ) :
    """ bio database class """
    def __init__(self):
        ob.__init__(self)


    def initNew(self,connection):
        self.obState.update({'NEW' : 1, 'DB_PENDING' : 1})        
        self.databaseFields = {
            'obid' : getNewObid(connection) ,
            'xreflsid' : None,
            'databasename' : None,
            'databasedescription' : None,
            'databasetype' : None,
            'databasecomment' : None}
        

    def initFromDatabase(self, identifier, connection):
        """ method for initialising bioDatabaseOb from database """

        # first init base class - this will get obid
        ob.initFromDatabase(self, identifier, "bioDatabaseOb", connection)

        # now get the complete object
        self.databaseFields = getObjectRecord(connection, "bioDatabaseOb", self.databaseFields['obid'])


    def insertDatabase(self,connection):
        """ method used by biodatabaseob object to save itself to database  """
        sql = """
        insert into biodatabaseob(obid,xreflsid,databasename,databasedescription,
        databasetype,databasecomment)
        values(%(obid)s,%(xreflsid)s,%(databasename)s,%(databasedescription)s,
        %(databasetype)s,%(databasecomment)s)
        """
        #print "executing " + sql%self.databaseFields
        insertCursor = connection.cursor()
        insertCursor.execute(sql,self.databaseFields)
        connection.commit()
        insertCursor.close()
        self.obState.update({'NEW' : 0 , 'ERROR' : 0, 'DB_PENDING' : 0, 'MESSAGE' : "database insert OK"})
        return

    def makeBlastDatabase(self,connection,logger,download=True):
        """ method used by biodatabaseob object to create a blast database. This assumes that the
        fact table for this database contains values for the following keys, in the
        BLAST SETUP namespace :

        SETUP METHOD
        NEXT DUE (dd/mm/yyyy)                   # optional
        LAST UPDATED (dd/mm/yyyy)

        for the standard setup method the following keys are needed :
        
        LOCAL TARGET DIRECTORY
        PREPARE
        DOWNLOAD
        UNPACK
        FILTER
        FORMATDB
        MOVE
        CLEAN UP
        INFO
        INDEX FILE NAME
        INDEX FILE NAME ALIAS
        """

        dbcursor=connection.cursor()

        # obtain blast set up details
        sql = """
        select
           attributename,
           attributevalue
        from
           biodatabasefact
        where
           factnamespace = 'BLAST SETUP' and
           biodatabaseob = %(obid)s
        """
        dbcursor.execute(sql,self.databaseFields)
        setupDetails = dbcursor.fetchall()
        setupDict = dict(setupDetails)

        logger.info("using setup details : %s"%str(setupDict))


        if "SETUP METHOD" not in setupDict:
            raise brdfException("Invalid configuration - need to specify SETUP METHOD")

        if setupDict["SETUP METHOD"] == "METHOD 1":

            # tidy up the setup details as required  - e.g. assign default values
            if "NEXT DUE" not in setupDict:
                setupDict["NEXT DUE"] = None # unimplemented - currently done by cron

            if "DOWNLOAD DIRECTORY" not in setupDict:
                setupDict["DOWNLOAD DIRECTORY"] = "/tmp"

            # decide whether to update
            updateDetails = {
                "updateAttempted" : True,
                "updateCompleted" : False, 
                "downloadDone" : False,
                "unpackDone" : False,
                "formatdbDone" : False,
                "moveDone" : False,
                "cleanupDone" : False,
                "infoDone" : False
            }

            # if next due date is in the future , then do not update
            if setupDict["NEXT DUE"] != None:
                None
                # unimplemented - timing is done by cron 

            if updateDetails["updateAttempted"] : 
                # attempt download

                os.chdir(setupDict["DOWNLOAD DIRECTORY"])
                if os.getcwd() != setupDict["DOWNLOAD DIRECTORY"]:
                    raise brdfException("Failed setting download directory - expected working directory to be %s, but it is %s"%(setupDict["DOWNLOAD DIRECTORY"], os.getcwd())) 


                if download:         
                    if "DOWNLOAD" in setupDict:
                        # check whether we need to download anything
                        # To Do 
                        logger.info("executing %(DOWNLOAD)s"%setupDict)
                        (updateDetails["downloadStatus"], updateDetails["downloadOutput"]) = commands.getstatusoutput(setupDict["DOWNLOAD"])
                        if updateDetails["downloadStatus"] == 0:
                            updateDetails["downloadDone"] = True
                else:
                    (updateDetails["downloadStatus"], updateDetails["downloadOutput"]) = (0,"No download done - assumed already done")
                    updateDetails["downloadDone"] = True
                    

                if "UNPACK" in setupDict and updateDetails["downloadDone"]:
                    #logger.info("executing %(UNPACK)s"%setupDict)
                    #(updateDetails["unpackStatus"], updateDetails["unpackOutput"]) = commands.getstatusoutput(setupDict["UNPACK"])
                    #if updateDetails["unpackStatus"] == 0:
                    #    updateDetails["unpackDone"] = True
                        
                    logger.info("executing %(UNPACK)s"%setupDict)
                    # allow comma-seperated commands
                    unpackCommands = re.split("\s*\;\s*",setupDict["UNPACK"])
                    logger.info("commands are : %s"%str(unpackCommands))
                    (updateDetails["unpackStatus"], updateDetails["unpackOutput"]) = (0,"")
                    for unpackCommand in unpackCommands:
                        logger.info("executing : %s"%unpackCommand)
                        (unpackStatus,unpackOutput) = commands.getstatusoutput(unpackCommand)
                        updateDetails["unpackStatus"] += unpackStatus
                        updateDetails["unpackOutput"] += " ; %s"%unpackOutput
                        
                    if updateDetails["unpackStatus"] == 0:
                        updateDetails["unpackDone"] = True

                # optional additional step regarded as part of unpacking
                if "PREFORMAT" in setupDict and updateDetails["unpackDone"]:
                    logger.info("executing %(PREFORMAT)s"%setupDict)
                    updateDetails["unpackDone"] = False
                    (updateDetails["preformatStatus"], updateDetails["preformatOutput"]) = commands.getstatusoutput(setupDict["PREFORMAT"])
                    if updateDetails["preformatStatus"] == 0:
                        updateDetails["unpackDone"] = True                        

                if "FORMATDB" in setupDict and updateDetails["unpackDone"]:
                    logger.info("executing %(FORMATDB)s"%setupDict)
                    (updateDetails["formatdbStatus"], updateDetails["formatdbOutput"]) = commands.getstatusoutput(setupDict["FORMATDB"])
                    if updateDetails["formatdbStatus"] == 0:
                        updateDetails["formatdbDone"] = True

                if "MOVE" in setupDict and updateDetails["formatdbDone"]:
                    logger.info("executing %(MOVE)s"%setupDict)
                    (updateDetails["moveStatus"], updateDetails["moveOutput"]) = commands.getstatusoutput(setupDict["MOVE"])
                    if updateDetails["moveStatus"] == 0:
                        updateDetails["moveDone"] = True

                if "CLEAN UP" in setupDict:
                    logger.info("executing %(CLEAN UP)s"%setupDict)
                    # allow comma-seperated commands
                    cleanupCommands = re.split("\s*\;\s*",setupDict["CLEAN UP"])
                    (updateDetails["cleanupStatus"], updateDetails["cleanupOutput"]) = (0,"")
                    for cleanupCommand in cleanupCommands:
                        (cleanupStatus,cleanupOutput) = commands.getstatusoutput(cleanupCommand)
                        updateDetails["cleanupStatus"] += cleanupStatus
                        updateDetails["cleanupOutput"] += " ; %s"%cleanupOutput
                        
                    if updateDetails["cleanupStatus"] == 0:
                        updateDetails["cleanupDone"] = True
                        if updateDetails["moveDone"]:
                            updateDetails["updateCompleted"] = True

                      
                if  updateDetails["updateCompleted"]:
                    # log the update 

                    if "INFO" in setupDict:
                        logger.info("executing %(INFO)s"%setupDict)
                        (updateDetails["infoStatus"], updateDetails["infoOutput"]) = commands.getstatusoutput(setupDict["INFO"])
                        if updateDetails["infoStatus"] == 0:
                            updateDetails["infoDone"] = True
                            updateDetails["infoCompleted"] = True

     
                    sql = """
                    insert into biodatabasefact(
                       biodatabaseob,
                       factnamespace,
                       attributename,
                       attributevalue)
                    values(%(obid)s, 'BLAST DATABASE UPDATE LOG', %(key)s, %(info)s)
                    """
                    logger.info("executing %s"%sql)
                    dbcursor.execute(sql,{
                       "obid" : self.databaseFields["obid"],
                       "key" :  "Update info at " + datetime.now().strftime("%Y-%m-%d:%H:%M:%S"),
                       "info" : eval({True : 'updateDetails["infoOutput"]', False : 'None'}["infoOutput" in updateDetails])
                    })
                    connection.commit()

            dbcursor.close()





        else:
            raise brdfException("unknown method : %(SETUP METHOD)s")

            # this method involves querying NCBI eutils
            # example bash script that this was designed from
            junk = """
#Create a url with your query term and database:
QUERY="txid9913[Organism]" #cow
DATABASE="nucest"
OUTFILE="bovine_est.fa"
BLASTDIR="/data/anonftp/pub/mirror/test"

# set proxy in case it's not in .bashrc then retrieve summary 
export http_proxy="http://webgate.agresearch.co.nz:8080/"
wget -q --proxy-user="AGRESEARCH\\prgupload" --proxy-passwd="Cheesem4n"	-O query.xml "http://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?&db=$DATABASE&usehistory=y&retmax=0&term=$QUERY"

#Pull out the Count, QueryKey and WebEnv strings and insert into url to efetch:
WEBENV=`sed '/<WebEnv>/!d' query.xml | sed 's/<\/*WebEnv>//g'`
COUNT=`sed '/<Count>/!d' query.xml | sed 's/<\/*Count>//g'`
QUERYKEY=`sed '/<QueryKey>/!d' query.xml | sed 's/<\/*QueryKey>//g'`

wget -q -c --proxy-user="AGRESEARCH\\prgupload" --proxy-passwd="Cheesem4n" -O $OUTFILE "http://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?&db=$DATABASE&query_key=$QUERYKEY&WebEnv=$WEBENV&retmax=$COUNT&retmode=text&rettype=fasta"

# create database files
TODAY=`date`
formatdb -t "Bovine ESTs as at $TODAY" -n bovine_ests -i $OUTFILE -p F -o T
chmod 644 bovine_ests.n*

# create dir if it doesn't exist
if [ -d $BLASTDIR ]; then
#do nothing
elif
  mkdir $BLASTDIR
fi

# then move to blast dir,
cp bovine_ests.n* $BLASTDIR

# cleanup
rm -f query.xml
rm -f $OUTFILE
rm -f bovine_ests.n*
"""

            
            

            # tidy up the setup details as required  - e.g. assign default values
            if "NEXT DUE" not in setupDict:
                setupDict["NEXT DUE"] = None # unimplemented - currently done by cron

            if "DOWNLOAD DIRECTORY" not in setupDict:
                setupDict["DOWNLOAD DIRECTORY"] = "/tmp"

            updateDetails = {
                "updateAttempted" : True,
                "updateCompleted" : False, 
                "downloadDone" : False,
                "unpackDone" : False,
                "formatdbDone" : False,
                "moveDone" : False,
                "cleanupDone" : False,
                "infoDone" : False
            }

            if updateDetails["updateAttempted"] : 
                # attempt download

                os.chdir(setupDict["DOWNLOAD DIRECTORY"])
                if os.getcwd() != setupDict["DOWNLOAD DIRECTORY"]:
                    raise brdfException("Failed setting download directory - expected working directory to be %s, but it is %s"%(setupDict["DOWNLOAD DIRECTORY"], os.getcwd())) 

                if "DOWNLOAD" in setupDict:
                    # check whether we need to download anything
                    # To Do 
                    logger.info("executing %(DOWNLOAD)s"%setupDict)
                    (updateDetails["downloadStatus"], updateDetails["downloadOutput"]) = commands.getstatusoutput(setupDict["DOWNLOAD"])
                    if updateDetails["downloadStatus"] == 0:
                        updateDetails["downloadDone"] = True

                if "UNPACK" in setupDict and updateDetails["downloadDone"]:
                    logger.info("executing %(UNPACK)s"%setupDict)
                    (updateDetails["unpackStatus"], updateDetails["unpackOutput"]) = commands.getstatusoutput(setupDict["UNPACK"])
                    if updateDetails["unpackStatus"] == 0:
                        updateDetails["unpackDone"] = True

                if "FORMATDB" in setupDict and updateDetails["unpackDone"]:
                    logger.info("executing %(FORMATDB)s"%setupDict)
                    (updateDetails["formatdbStatus"], updateDetails["formatdbOutput"]) = commands.getstatusoutput(setupDict["FORMATDB"])
                    if updateDetails["formatdbStatus"] == 0:
                        updateDetails["formatdbDone"] = True

                if "MOVE" in setupDict and updateDetails["formatdbDone"]:
                    logger.info("executing %(MOVE)s"%setupDict)
                    (updateDetails["moveStatus"], updateDetails["moveOutput"]) = commands.getstatusoutput(setupDict["MOVE"])
                    if updateDetails["moveStatus"] == 0:
                        updateDetails["moveDone"] = True

                if "CLEAN UP" in setupDict and updateDetails["moveDone"]:
                    logger.info("executing %(CLEAN UP)s"%setupDict)

                    # allow a series of commands split by semi colon. Executed one by one
                    cleanupCommands = re.split("\s*\;\s*", setupDict["CLEAN UP"])
                    (updateDetails["cleanupStatus"], updateDetails["cleanupOutput"]) = (0,"")
                    for cleanupCommand in cleanupCommands:                        
                        (status, output) = commands.getstatusoutput(cleanupCommand)
                        updateDetails["cleanupStatus"] += status
                        updateDetails["cleanupOutput"] += ";%s"%output
                        
                    if updateDetails["cleanupStatus"] == 0:
                        updateDetails["cleanupDone"] = True
                        updateDetails["updateCompleted"] = True

                      
                if  updateDetails["updateCompleted"]:
                    # log the update 

                    if "INFO" in setupDict:
                        logger.info("executing %(INFO)s"%setupDict)
                        (updateDetails["infoStatus"], updateDetails["infoOutput"]) = commands.getstatusoutput(setupDict["INFO"])
                        if updateDetails["infoStatus"] == 0:
                            updateDetails["infoDone"] = True
                            updateDetails["infoCompleted"] = True

     
                    sql = """
                    insert into biodatabasefact(
                       biodatabaseob,
                       factnamespace,
                       attributename,
                       attributevalue)
                    values(%(obid)s, 'BLAST DATABASE UPDATE LOG', %(key)s, %(info)s)
                    """
                    logger.info("executing %s"%sql)
                    dbcursor.execute(sql,{
                       "obid" : self.databaseFields["obid"],
                       "key" :  "Update info at " + datetime.now().strftime("%Y-%m-%d:%H:%M:%S"),
                       "info" : eval({True : 'updateDetails["infoOutput"]', False : 'None'}["infoOutput" in updateDetails])
                    })
                    connection.commit()

            dbcursor.close()







            

        return updateDetails
        

    def checkBlastDatabase(self,connection):
        """ method used by biodatabase object to check that its blast database is OK. - e.g. run a blast
            and parse the output. Unimplemented
        """
    




class databaseSearchStudy ( op ) :
    """ database search  study objects """
    def __init__(self):
        op.__init__(self)


    def initNew(self,connection):      
        self.obState.update({'NEW' : 1, 'DB_PENDING' : 1})

        self.databaseFields = {
            'obid' : getNewObid(connection) ,
            'xreflsid' : None,
            'biodatabaseob' : None,
            'bioprotocolob' : None,
            'runby' : None,
            'rundate' : None,
            'studyname' : None,
            'studycomment' : None,
            'studytype' : None,
            'studydescription' : None
        }


    def initFromDatabase(self, identifier, connection):
        """ method for initialising databasesearchstudy from database """

        # first init base class - this will get obid
        ob.initFromDatabase(self, identifier, "databaseSearchStudy", connection)

        # now get the complete object
        self.databaseFields = getObjectRecord(connection, "databaseSearchStudy", self.databaseFields['obid'])

    def insertDatabase(self,connection):
        """ method used by database search study object to save itself to database  """
        sql = """
        insert into databaseSearchStudy(obid,xreflsid,biodatabaseob,bioprotocolob,runby,rundate,studycomment,studytype,studydescription)
        values(%(obid)s,%(xreflsid)s,%(biodatabaseob)s,%(bioprotocolob)s,%(runby)s,%(rundate)s,%(studycomment)s,%(studytype)s,
        %(studydescription)s)
        """
        #print "executing " + sql%self.databaseFields
        insertCursor = connection.cursor()
        insertCursor.execute(sql,self.databaseFields)
        connection.commit()
        insertCursor.close()
        self.obState.update({'NEW' : 0 , 'ERROR' : 0, 'DB_PENDING' : 0, 'MESSAGE' : "database insert OK"})
        return

    def updateDatabase(self,connection):
        """ method used by databasesearchstudy object  to update itself to database  """

        sql = """
        update databaseSearchStudy set
        studycomment = %(studycomment)s,
        studydescription = %(studydescription)s,
        lastupdateddate = now()
        where
        obid = %(obid)s
        """
     
        #print "executing " + sql%self.databaseFields
        updateCursor = connection.cursor()
        updateCursor.execute(sql,self.databaseFields)
        connection.commit()
        updateCursor.close()
        self.obState.update({'NEW' : 0 , 'ERROR' : 0, 'DB_PENDING' : 0, 'MESSAGE' : "database update OK"})
        return


    

    def addHit(self,connection, querysequence = None, hitsequence = None, queryxreflsid = None, querylength = None, hitxreflsid = None, hitdescription = None,\
               hitlength = None, hitevalue = None, hitpvalue = None, rawsearchresult = None, observationcomment = None, checkExisting = False, userflags = None):

        hit = databaseSearchObservation()
        doInsert = True
        if checkExisting:
            hitlsid = "%s.%s.%s"%(self.databaseFields['xreflsid'],queryxreflsid,hitxreflsid)
            try:
                hit.initFromDatabase(hitlsid,connection)
                doInsert = False
            except brdfException:
                if hit.obState['ERROR'] != 1:
                    raise brdfException, hit.obState['MESSAGE']

        if doInsert:
            # not in db - insert
            hit.initNew(connection)
            hit.databaseFields.update( {
                        'xreflsid' : "%s.%s.%s"%(self.databaseFields['xreflsid'],queryxreflsid,hitxreflsid),
                        'databasesearchstudy' : self.databaseFields['obid'],
                        'querysequence' : querysequence,
                        'hitsequence' : hitsequence,
                        'queryxreflsid' : queryxreflsid,
                        'querylength' : querylength,
                        'hitxreflsid' :  hitxreflsid,
                        'hitdescription' :  hitdescription,
                        'hitlength' : hitlength,
                        'hitevalue' : hitevalue,
                        'hitpvalue' : hitpvalue,
                        'rawsearchresult' : rawsearchresult,
                        'observationcomment' : observationcomment ,
                        'userflags' : userflags
            })

            # if there is a hint to compress LSIDs then do so - compress this LSID and do not bother storing
            # the redundant query and hit lsids
            if self.compressionLevel > 0:
                hit.databaseFields.update({
                    "xreflsid" : str(abs(hash(hit.databaseFields['xreflsid']))),
                    "queryxreflsid" : None,
                    "hitxreflsid" : None
                })
                    
            hit.insertDatabase(connection)

        return (hit,doInsert)


    def updateHit(self,connection, queryxreflsid = None, hitxreflsid = None, updateDict = {}):

        hit = databaseSearchObservation()
        hitlsid = "%s.%s.%s"%(self.databaseFields['xreflsid'],queryxreflsid,hitxreflsid)
        try:
            hit.initFromDatabase(hitlsid,connection)
        except brdfException:
            raise brdfException, hit.obState['MESSAGE']

        insertCursor=connection.cursor()
        for updateField in updateDict:
            sql= """
            update databasesearchObservation
            set %s = %%(%s)s
            where obid = %s
            """%(updateField,hit.databaseFields['obid'])
            studymodulelogger.info("executing %s"%(sql%{
                updateField : updateDict[updateField]
            }))
                
            insertCursor.execute(sql,{
                updateField : updateDict[updateField]
            })

            connection.commit()

        return hit    
                

class databaseSearchObservation ( op ) :
    """ class reprsenting a hit in a database search"""
    def __init__(self):
        op.__init__(self)


    def initNew(self,connection):
        self.obState.update({'NEW' : 1, 'DB_PENDING' : 1})        
        self.databaseFields = {
            'obid' : getNewObid(connection) ,
            'xreflsid' : None,
            'databasesearchstudy' : None,
            'querysequence' : None,
            'hitsequence' : None,
            'queryxreflsid' : None,
            'querylength' : None,
            'hitxreflsid' :  None,
            'hitdescription' :  None,
            'hitlength' : None,
            'hitevalue' : None,
            'hitpvalue' : None,
            'rawsearchresult' : None,
            'observationcomment' : None,
            'userflags' : None
        }
        

    def initFromDatabase(self, identifier, connection):
        """ method for initialising databaseSearch observation from database """

        # first init base class - this will get obid
        ob.initFromDatabase(self, identifier, "databaseSearchObservation", connection)

        # now get the complete object
        self.databaseFields = getObjectRecord(connection, "databaseSearchObservation", self.databaseFields['obid'])


    def insertDatabase(self,connection):
        """ method used by database search observation to save itself to database  """
        sql = """
        insert into databaseSearchObservation(obid ,xreflsid, databasesearchstudy,
            querysequence,hitsequence,queryxreflsid,querylength,hitxreflsid,hitdescription,
            hitlength,hitevalue,hitpvalue,rawsearchresult,observationcomment,userflags)
            values (%(obid)s ,%(xreflsid)s, %(databasesearchstudy)s,
            %(querysequence)s,%(hitsequence)s,%(queryxreflsid)s,%(querylength)s,%(hitxreflsid)s,%(hitdescription)s,
            %(hitlength)s,%(hitevalue)s,%(hitpvalue)s,%(rawsearchresult)s,%(observationcomment)s,%(userflags)s)
        """
        #print "executing " + sql%self.databaseFields
        insertCursor = connection.cursor()
        insertCursor.execute(sql,self.databaseFields)
        connection.commit()
        insertCursor.close()
        self.obState.update({'NEW' : 0 , 'ERROR' : 0, 'DB_PENDING' : 0, 'MESSAGE' : "database insert OK"})
        return

    def addAlignmentFact(self,connection,alignmentDict, checkExisting = False):
        """ method to add an alignment fact to a databasesearchobservation """
        strandDict = {
            'PLUS / PLUS' : 1,
            'PLUS / MINUS' : -1,
            'MINUS / MINUS' : 1,
            'MINUS / PLUS' : -1
        }
        insertCursor = connection.cursor()        
        alignmentDict.update ({
            'databasesearchobservation' : self.databaseFields['obid'],
            'bitscore' : eval({True : 'alignmentDict["bitscore"]', False : "None"}[alignmentDict.has_key("bitscore")]),
            'mismatches' : eval({True : 'alignmentDict["mismatches"]', False : "None"}[alignmentDict.has_key("mismatches")]),
            'pctidentity' : eval({True : 'alignmentDict["pctidentity"]', False : "None"}[alignmentDict.has_key("pctidentity")]),            
            'score' : eval({True : 'alignmentDict["score"]', False : "None"}[alignmentDict.has_key("score")]),            
            'evalue' : eval({True : 'alignmentDict["evalue"]', False : "None"}[alignmentDict.has_key("evalue")]),
            'queryfrom' : eval({True : 'alignmentDict["queryfrom"]', False : "None"}[alignmentDict.has_key("queryfrom")]),
            'queryto' : eval({True : 'alignmentDict["queryto"]', False : "None"}[alignmentDict.has_key("queryto")]),
            'hitfrom' : eval({True : 'alignmentDict["hitfrom"]', False : "None"}[alignmentDict.has_key("hitfrom")]),
            'hitto' : eval({True : 'alignmentDict["hitto"]', False : "None"}[alignmentDict.has_key("hitto")])  ,
            'queryframe' : eval({True : 'alignmentDict["queryframe"]', False : "None"}[alignmentDict.has_key("queryframe")])  ,
            'hitstrand' : eval({True : 'strandDict[alignmentDict["hitstrand"].upper()]', False : "None"}[alignmentDict.has_key("hitstrand")])  ,
            'gaps' : eval({True : 'alignmentDict["gaps"]', False : "None"}[alignmentDict.has_key("gaps")])  ,
            'indels' : eval({True : 'alignmentDict["indels"]', False : "None"}[alignmentDict.has_key("indels")])  ,                                    
            'hitframe' : eval({True : 'alignmentDict["hitframe"]', False : "None"}[alignmentDict.has_key("hitframe")])  ,
            'identities' : eval({True : 'alignmentDict["identities"]', False : "None"}[alignmentDict.has_key("identities")])  ,
            'positives' : eval({True : 'alignmentDict["positives"]', False : "None"}[alignmentDict.has_key("positives")])  ,
            'alignlen' : eval({True : 'alignmentDict["alignlen"]', False : "None"}[alignmentDict.has_key("alignlen")])  ,
            'hspqseq' : eval({True : 'alignmentDict["hspqseq"]', False : "None"}[alignmentDict.has_key("hspqseq")])  ,
            'hsphseq' : eval({True : 'alignmentDict["hsphseq"]', False : "None"}[alignmentDict.has_key("hsphseq")])  ,
            'hspmidline' : eval({True : 'alignmentDict["hspmidline"]', False : "None"}[alignmentDict.has_key("hspmidline")])  ,
            'alignmentcomment' : eval({True : 'alignmentDict["alignmentcomment"]', False : "None"}[alignmentDict.has_key("alignmentcomment")])              
            })

        alignmentDict.update({
            'xreflsid' : "%s:%s,%s-%s,%s"%(self.databaseFields['xreflsid'],alignmentDict['queryfrom'],alignmentDict['queryto'],\
                                              alignmentDict['hitfrom'],alignmentDict['hitto'])
        })

        # if there is a hint to compress LSIDs then do so - compress this LSID 
        if self.compressionLevel > 0:
            alignmentDict.databaseFields.update({
                "xreflsid" : str(abs(hash(alignmentDict.databaseFields['xreflsid']))),
            })


        # first check if this alignment is already in the db - if it is do not duplicate
        alignmentExists = False
        if checkExisting:
            sql = """
            select databasesearchobservation from sequencealignmentfact where
            databasesearchobservation = %(databasesearchobservation)s and
            queryfrom  = %(queryfrom)s and
            queryto = %(queryto)s and
            hitfrom = %(hitfrom)s and
            hitto = %(hitto)s
            """
            if alignmentDict['queryfrom'] != None:
                sql += " and queryfrom = %(queryfrom)s "
            if alignmentDict['queryto'] != None:
                sql += " and queryto = %(queryto)s "
            if alignmentDict['hitfrom'] != None:
                sql += " and hitfrom = %(hitfrom)s "
            if alignmentDict['hitto'] != None:
                sql += " and hitto = %(hitto)s "                

            #studymodulelogger.info("checking for alignment using %s"%(sql%alignmentDict))
            insertCursor.execute(sql%alignmentDict)
            insertCursor.fetchone()
            #studymodulelogger.info("rowcount = %s"%insertCursor.rowcount)

            if insertCursor.rowcount != 0:
                alignmentExists = True
                
            
        if not alignmentExists:
                                             
            sql = """
            insert into sequencealignmentfact(
            databasesearchobservation,
            xreflsid,
            bitscore,
            mismatches,
            pctidentity,
            score   ,        
            evalue  ,        
            queryfrom ,      
            queryto   ,      
            hitfrom   ,      
            hitto     ,      
            queryframe ,
            hitstrand,
            hitframe   ,     
            identities ,     
            positives  ,
            gaps,
            alignlen   ,     
            hspqseq    ,     
            hsphseq    ,     
            hspmidline ,     
            alignmentcomment ,
            indels)
            values(
            %(databasesearchobservation)s,
            %(xreflsid)s,
            %(bitscore)s,
            %(mismatches)s,
            %(pctidentity)s,
            %(score)s   ,        
            %(evalue)s  ,        
            %(queryfrom)s ,      
            %(queryto)s   ,      
            %(hitfrom)s   ,      
            %(hitto)s     ,      
            %(queryframe)s ,
            %(hitstrand)s,
            %(hitframe)s   ,     
            %(identities)s ,     
            %(positives)s  ,
            %(gaps)s,
            %(alignlen)s   ,     
            %(hspqseq)s    ,     
            %(hsphseq)s    ,     
            %(hspmidline)s ,     
            %(alignmentcomment)s,
            %(indels)s)
            """
            #studymodulelogger.info("executing %s"%(sql%alignmentDict))
            insertCursor.execute(sql,alignmentDict)
            connection.commit()
            insertCursor.close()
            self.obState.update({'NEW' : 0 , 'DB_PENDING' : 0, 'ERROR' : 0, 'MESSAGE' : "database insert OK"})

            
        else:
            insertCursor.close()


########### Functional Assay Studies #################
class functionalAssayStudy ( op ) :
    """ functional assay study - a set of replicate observations of a given compund sample (e.g. immunoassays) in a
    functional assay series """
    def __init__(self):
        op.__init__(self)


    def initNew(self,connection,obtuple):
        argTemplate1 = [classitem.__name__ for classitem in (labResourceList,bioSampleList,bioProtocolOb)]
        argTemplate2 = [classitem.__name__ for classitem in (labResourceOb,bioSampleList,bioProtocolOb)]
        argTemplate3 = [classitem.__name__ for classitem in (labResourceList,bioSampleOb,bioProtocolOb)]
        argTemplate4 = [classitem.__name__ for classitem in (labResourceOb,bioSampleOb,bioProtocolOb)]                
        argsSupplied = [obitem.__class__.__name__ for obitem in obtuple]

        if (argTemplate1 != argsSupplied) and (argTemplate2 != argsSupplied) and (argTemplate3 != argsSupplied) \
                 and (argTemplate4 != argsSupplied) :
            self.obState.update({'ERROR' : 1 , 'MESSAGE' : "args supplied : " + reduce(lambda x,y:x+" "+ y,argsSupplied) + \
                  " args required : %s or %s or %s or %s"%(reduce(lambda x,y:x+" "+y,argTemplate1),\
                                                           reduce(lambda x,y:x+" "+y,argTemplate2),\
                                                           reduce(lambda x,y:x+" "+y,argTemplate3),\
                                                           reduce(lambda x,y:x+" "+y,argTemplate4)) })
            raise brdfException, self.obState['MESSAGE']

        if argTemplate1 == argsSupplied:
            self.labResourceList = obtuple[0]
            self.bioSampleList = obtuple[1]            
            self.databaseFields = {
                'xreflsid' : '' , 
                'studydescription' : '', 
                'obid' : getNewObid(connection) , 
                'labresourcelist' : obtuple[0].databaseFields['obid'],
                'labresourceob' : None,
                'biosamplelist' : obtuple[1].databaseFields['obid'],
                'biosampleob' : None,
                'bioprotocolob' : obtuple[2].databaseFields['obid']
            }
        elif argTemplate2 == argsSupplied:
            self.labResourceOb = obtuple[0]
            self.bioSampleList = obtuple[1]            
            self.databaseFields = {
                'xreflsid' : '' , 
                'studydescription' : '', 
                'obid' : getNewObid(connection) , 
                'labresourceob' : obtuple[0].databaseFields['obid'],
                'labresourcelist' : None,
                'biosamplelist' : obtuple[1].databaseFields['obid'],
                'biosampleob' : None,                
                'bioprotocolob' : obtuple[2].databaseFields['obid']
            }
        elif argTemplate3 == argsSupplied:
            self.labResourceOb = obtuple[0]
            self.bioSampleOb = obtuple[1]            
            self.databaseFields = {
                'xreflsid' : '' , 
                'studydescription' : '', 
                'obid' : getNewObid(connection) , 
                'labresourceob' : obtuple[0].databaseFields['obid'],
                'labresourcelist' : None,
                'biosampleob' : obtuple[1].databaseFields['obid'],
                'biosamplelist' : None,                  
                'bioprotocolob' : obtuple[2].databaseFields['obid']
            }
        elif argTemplate4 == argsSupplied:
            self.labResourceOb = obtuple[0]
            self.bioSampleOb = obtuple[1]            
            self.databaseFields = {
                'xreflsid' : '' , 
                'studydescription' : '', 
                'obid' : getNewObid(connection) , 
                'labresourceob' : obtuple[0].databaseFields['obid'],
                'labresourcelist' : None,
                'biosampleob' : obtuple[1].databaseFields['obid'],
                'biosamplelist' : None,                  
                'bioprotocolob' : obtuple[2].databaseFields['obid']
            }                  
            

        self.bioProtocolOb = obtuple[2]


        self.obState.update({'DB_PENDING' : 1})



    def initFromDatabase(self, identifier, connection):
        """ method for initialising functionalAssayStudy from database"""

        # first init base class - this will get obid
        ob.initFromDatabase(self, identifier, "functionalAssayStudy", connection)

        # now get the complete object
        self.databaseFields = getObjectRecord(connection, "functionalAssayStudy", self.databaseFields['obid'])
        self.obState.update({'ERROR' : 0 , 'NEW' : 0, 'MESSAGE' : "initialised from database OK"})


                
        self.obState.update({'NEW' : 0 , 'DB_PENDING' : 0, 'MESSAGE' : "init from database OK"})
        
            
    def insertDatabase(self,connection):
        """ method used by functionalAssayStudy to save itself to database  """
        
        sql = """
        insert into functionalAssayStudy(obid,xreflsid,labResourceList,labresourceob,
        bioSampleList, biosampleob,bioProtocolOb,
        obkeywords,studydescription) values
        (%(obid)s,%(xreflsid)s,%(labresourcelist)s,%(labresourceob)s,%(biosamplelist)s,%(biosampleob)s,
        %(bioprotocolob)s,%(xreflsid)s,%(studydescription)s)"""
        #print 'executing ' + sql%self.databaseFields
        insertCursor = connection.cursor()
        insertCursor.execute(sql,self.databaseFields)
        connection.commit()
        insertCursor.close()
        self.obState.update({'NEW' : 0 , 'ERROR' : 0, 'DB_PENDING' : 0, 'MESSAGE' : "database insert OK"})


    def addFact(self,connection,argfactNameSpace, argattributeName, argattributeValue, checkExisting = True):
        factFields = {
            'functionalAssayStudy' : self.databaseFields['obid'],
            'factNameSpace' : argfactNameSpace,
            'attributeName' : argattributeName,
            'attributeValue' : argattributeValue }
        
        doinsert = True
        insertCursor = connection.cursor()

        # first check if this fact is already in the db - if it is do not duplicate (if asked to do this)
        if checkExisting:
            sql = """
            select functionalAssayStudy from functionalAssayStudyFact where
            functionalAssayStudy = %(functionalAssayStudy)s and
            factNameSpace = %(factNameSpace)s and
            attributeName = %(attributeName)s and
            attributeValue = %(attributeValue)s
            """
            #studymodulelogger.info("checking for fact using %s"%(sql%factFields))
            insertCursor.execute(sql,factFields)
            insertCursor.fetchone()
            #studymodulelogger.info("rowcount = %s"%insertCursor.rowcount)
            if insertCursor.rowcount == 0:
                doinsert = True
            else:
                doinsert = False

        if doinsert:
            sql = """
            insert into functionalAssayStudyFact(functionalAssayStudy,factNameSpace, attributeName, attributeValue)
            values(%(functionalAssayStudy)s,%(factNameSpace)s,%(attributeName)s,%(attributeValue)s)
            """
            #studymodulelogger.info("executing %s"%(sql%factFields))
            insertCursor.execute(sql,factFields)
            connection.commit()
            insertCursor.close()
            self.obState.update({'NEW' : 0 , 'DB_PENDING' : 0, 'ERROR' : 0, 'MESSAGE' : "database insert OK"})
        else:
            insertCursor.close()
        

        

            
    def addObservation(self,connection,observationData,checkExisting = True):
        """ method used by functionalAssayStudy to add an observation"""
        
        observation = functionalAssayObservation()

        if checkExisting:
            try:
                observation.initFromDatabase(observationData['xreflsid'],connection)

                # if we obtained an observation then return false
                return (observation, False)                        
            
            except brdfException, msg:
                if observation.obState['ERROR'] == 1:
                    studymodulelogger.info("(existing functional assay observation %s not found, will add)"%observationData['xreflsid'])
                else:
                    raise brdfException,msg
                

        # not found so add it
        observation.initNew(connection)
        observation.databaseFields.update(observationData)
        observation.insertDatabase(connection)
        return (observation, True)

            


            
class functionalAssayObservation ( op ) :
    """ functional assay  observation """
    def __init__(self):
        op.__init__(self)

    def initFromDatabase(self, identifier, connection):
        """ method for initialising functional assay observation from database """

        # first init base class - this will get obid
        ob.initFromDatabase(self, identifier, "functionalAssayObservation", connection)

        # now get the complete object
        self.databaseFields = getObjectRecord(connection, "functionalAssayObservation", self.databaseFields['obid'])

    def initNew(self,connection):
        self.databaseFields = {
            'obid' : getNewObid(connection),
            'xreflsid' : None,
            'functionalassaystudy' : None,
            'functionalassayfact' : None,
            'observationdate' : None,
            'labbookreference' : None,
            'plateid' : None,
            'platex' : None,
            'platey' :None,
            'rawdatarecord' :None,
            'observationcomment' : None}

        self.obState.update({'DB_PENDING' : 1})        

    def insertDatabase(self,connection):
        sql = """
            insert into functionalassayobservation(
                obid  ,
                xreflsid ,
                functionalassaystudy,
                functionalassayfact,
                observationdate,
                plateid,
                platex,
                platey,
                rawdatarecord,
                labbookreference,
                observationcomment)
            values(
                %(obid)s  ,
                %(xreflsid)s ,
                %(functionalassaystudy)s ,
                %(functionalassayfact)s,
                to_date(%(observationdate)s,'dd-mm-yyyy') ,
                %(plateid)s ,
                %(platex)s ,
                %(platey)s ,
                %(rawdatarecord)s ,
                %(labbookreference)s,                
                %(observationcomment)s
            )"""
        #print 'executing ' + sql%self.databaseFields
        insertCursor = connection.cursor()
        insertCursor.execute(sql,self.databaseFields)
        connection.commit()
        insertCursor.close()
        self.obState.update({'NEW' : 0 , 'DB_PENDING' : 0, 'MESSAGE' : "database insert OK"})


    def addFact(self,connection,argfactNameSpace, argattributeName, argattributeValue, checkExisting = True):
        factFields = {
            'functionalAssayObservation' : self.databaseFields['obid'],
            'factNameSpace' : argfactNameSpace,
            'attributeName' : argattributeName,
            'attributeValue' : argattributeValue }
        
        doinsert = True
        insertCursor = connection.cursor()

        # first check if this fact is already in the db - if it is do not duplicate (if asked to do this)
        if checkExisting:
            sql = """
            select functionalAssayObservation from functionalAssayObservationFact where
            functionalAssayObservation = %(functionalAssayObservation)s and
            factNameSpace = %(factNameSpace)s and
            attributeName = %(attributeName)s and
            attributeValue = %(attributeValue)s
            """
            #studymodulelogger.info("checking for fact using %s"%(sql%factFields))
            insertCursor.execute(sql,factFields)
            insertCursor.fetchone()
            #studymodulelogger.info("rowcount = %s"%insertCursor.rowcount)
            if insertCursor.rowcount == 0:
                doinsert = True
            else:
                doinsert = False

        if doinsert:
            sql = """
            insert into functionalAssayObservationFact(functionalAssayObservation,factNameSpace, attributeName, attributeValue)
            values(%(functionalAssayObservation)s,%(factNameSpace)s,%(attributeName)s,%(attributeValue)s)
            """
            #studymodulelogger.info("executing %s"%(sql%factFields))
            insertCursor.execute(sql,factFields)
            connection.commit()
            insertCursor.close()
            self.obState.update({'NEW' : 0 , 'DB_PENDING' : 0, 'ERROR' : 0, 'MESSAGE' : "database insert OK"})
        else:
            insertCursor.close()





        
    
                   



    
    
