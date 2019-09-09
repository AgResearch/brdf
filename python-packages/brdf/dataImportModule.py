#
# This module implements classes relating to data import
#
#
# !!! ToDo !!! - establish foreign key to the microarrayspotfact as the experiment is being loaded
#
########################  change log ########################
#
# 8/2/2007 The import of AgResearch microarrays from a CSV files switches metarow and
# metacolumn. This was not noticed when the experiments themselves were also imported from
# CSV extracts but was noticed in the agbrdf database, when GPR files were loaded , for one
# of the AgResearch arrays (There are comments logged in the AgResearch database
# http://devagbrdf.agresearch.co.nz/cgi-bin/fetch.py?obid=1161739&context=default&target=ob
# http://devagbrdf.agresearch.co.nz/cgi-bin/fetch.py?obid=1162326&context=default&target=ob
# See comment in relevant section below
#
#
from types import *

import csv
from obmodule import getNewObid,getObjectRecord
from brdfExceptionModule import brdfException
from opmodule import op
from obmodule import ob
from labResourceModule import labResourceOb
from labResourceModule import labResourceList
from microarrayFileParsers import GPRFileParser,GALFileParser
from studyModule import geneExpressionStudy,databaseSearchStudy
from sequenceFileParsers import parseSequenceID
from sequenceModule import bioSequenceOb
from databaseModule import getConnection
from htmlModule import tidyout, defaultMenuJS, HTMLdoctype, getStyle
from annotationModule import makeComment, makeURL
#from stats import mean, stdev   # not sure where the original stats package was from - refactor to use one pip if necessary
import os
import sys
import logging
import globalConf
import string
import re
from datetime import date
import commands


importmodulelogger = logging.getLogger('dataimportModule')
#hdlr = logging.FileHandler('c:/temp/nutrigenomicsforms.log')
importhdlr = logging.FileHandler(os.path.join(globalConf.LOGPATH,'dataimportmodule.log'))
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
importhdlr.setFormatter(formatter)
importmodulelogger.addHandler(importhdlr) 
importmodulelogger.setLevel(logging.INFO)                                                      


class importProcedureOb (ob ):
    """ importProcedureOb objects document scripts and processes used to import data into the database"""
    def __init__(self):
        ob.__init__(self)

    def initNew(self,connection):
        """ method to initialise a new import procedure object """
        self.databaseFields = {
            'obid' : getNewObid(connection) ,
            'xreflsid' : None,
            'procedurename' : None,
            'procedurecomment' : None
        } 
        self.obState.update({'DB_PENDING' : 1})        

    def initFromDatabase(self, identifier, connection):  
        """ method for initialising an object from database - arg can be an integer obid, or a string importProcedureName"""
          
        # initialise base fields from ob table
        ob.initFromDatabase(self, identifier,"importProcedureOb",connection)

        # now get the complete object
        self.databaseFields = getObjectRecord(connection, "importProcedureOb", self.databaseFields['obid'])
        
        self.obState.update({'ERROR' : 0 , 'NEW' : 0, 'MESSAGE' : "initialised from database OK"})

    def insertDatabase(self,connection):
        """ method used by importProcedure object to save itself to database  """
        sql = """
        insert into importProcedureOb(obid,xreflsid,procedurename,procedurecomment)
        values (%(obid)s,%(xreflsid)s,%(procedurename)s,%(procedurecomment)s)
        """
        #print "executing " + sql%self.databaseFields
        insertCursor = connection.cursor()
        insertCursor.execute(sql,self.databaseFields)
        connection.commit()
        insertCursor.close()
        self.obState.update({'NEW' : 0 , 'ERROR' : 0, 'DB_PENDING' : 0, 'MESSAGE' : "database insert OK"})        
        

class importFunction ( op ) :
    """ an import function is a relation between a data source , and object and an import procedure """
    def __init__(self):
        op.__init__(self)

    def initNew(self,connection):
        """ method to initialise a new import function object """
        self.databaseFields = {
            'obid' : getNewObid(connection) ,
            'xreflsid' : None,
            'ob' : None,
            'datasourceob' : None,
            'importprocedureob' : None,
            'processinginstructions' : None,
            'notificationaddresses' : None,
            'submissionreasons' : None,
            'functioncomment' : None     
        } 
        self.obState.update({'DB_PENDING' : 1})


    def initFromDatabase(self, identifier, connection):  
        """ method for initialising an object from database - arg can be an integer obid, or a string xreflsid"""
          
        # initialise base fields from ob table
        ob.initFromDatabase(self, identifier,"importFunction",connection)

        # now get the complete object
        self.databaseFields = getObjectRecord(connection, "importFunction", self.databaseFields['obid'])
        
        self.obState.update({'ERROR' : 0 , 'NEW' : 0, 'MESSAGE' : "initialised from database OK"})



    def insertDatabase(self,connection):
        """ method used by importFunction object to save itself to database  """
        sql = """
        insert into
        importFunction(obid,ob,xreflsid,datasourceob,importprocedureob,
            processinginstructions,notificationaddresses,submissionreasons,
            functioncomment)
            values (%(obid)s,%(ob)s,%(xreflsid)s,%(datasourceob)s,%(importprocedureob)s,
            %(processinginstructions)s, %(notificationaddresses)s, %(submissionreasons)s,
            %(functioncomment)s)"""
        #print "executing " + sql%self.databaseFields
        insertCursor = connection.cursor()
        insertCursor.execute(sql,self.databaseFields)
        connection.commit()
        insertCursor.close()
        self.obState.update({'NEW' : 0 , 'ERROR' : 0, 'DB_PENDING' : 0, 'MESSAGE' : "database insert OK"})        


#    def addFact(self,connection,argfactNameSpace, argattributeDate, argattributeName, argattributeValue):
#        factFields = {
#            'importFunction' : self.databaseFields['obid'],
#            'factNameSpace' : argfactNameSpace,
#            'attributeDate' : argattributeDate,
#            'attributeName' : argattributeName,
#            'attributeValue' : argattributeValue }
#
#        # first check if this fact is already in the db - if it is do not duplicate
#        sql = """
#        select importFunction from importFunctionFact where
#        importFunction = %(importFunction)s and
#        factNameSpace = '%(factNameSpace)s' and
#        attributeDate = '%(attributeDate)s' and
#        attributeName = '%(attributeName)s' and
#        attributeValue = '%(attributeValue)s'
#        """
#        insertCursor = connection.cursor()
#        modulelogger.info("checking for fact using %s"%(sql%factFields))
#        insertCursor.execute(sql%factFields)
#        insertCursor.fetchone()
#        modulelogger.info("rowcount = %s"%insertCursor.rowcount)
#        if insertCursor.rowcount == 0:
#            sql = """
#            insert into importFunctionFact(importFunction,factNameSpace, attributeDate, attributeName, attributeValue)
#            values(%(importFunction)s,%(factNameSpace)s,%(attributeDate)s,%(attributeName)s,%(attributeValue)s)
#            """
#            modulelogger.info("executing %s"%(sql%factFields))
#            insertCursor.execute(sql,factFields)
#            connection.commit()
#            insertCursor.close()
#            self.obState.update({'NEW' : 0 , 'DB_PENDING' : 0, 'ERROR' : 0, 'MESSAGE' : "database insert OK"})
#        else:
#            insertCursor.close()
     

class labResourceImportFunction ( op ) :
    """ a labResourceImportFunction is a relation between a data source, a lab resource and an import function. """
    def __init__(self):
        op.__init__(self)


    def initNew(self,connection,obtuple):
        argTemplate = [classitem.__name__ for classitem in (dataSourceOb,importProcedureOb,labResourceOb)]
        argsSupplied = [obitem.__class__.__name__ for obitem in obtuple]

        if argTemplate != argsSupplied:
            self.obState.update({'ERROR' : 1 , 'MESSAGE' : "args supplied : " + reduce(lambda x,y:x+" "+ y,argsSupplied) + \
                  " args required : " + reduce(lambda x,y:x+" "+y,argTemplate) })
            raise brdfException, self.obState['MESSAGE']       
        
        self.databaseFields = {
            'obid' : getNewObid(connection) ,
            'dataSourceOb' : obtuple[0].databaseFields['obid'],         \
            'importProcedureOb' : obtuple[1].databaseFields['obid'],    \
            'labResourceOb' : obtuple[2].databaseFields['obid'] ,
            'xreflsid' : "%s.import"%obtuple[2].databaseFields['xreflsid'] }

        self.dataSource = obtuple[0]
        self.importProcedure = obtuple[1]
        self.labResource = obtuple[2]

        self.obState.update({'DB_PENDING' : 1})
            
    def insertDatabase(self,connection):
        """ method used by labResourceImportFunction to save itself to database  """
        
        sql = """
        insert into importFunction(obid,dataSourceOb,importProcedureOb,
        Ob,xreflsid) values (%(obid)s,%(dataSourceOb)s,%(importProcedureOb)s,
        %(labResourceOb)s,%(xreflsid)s)"""
        #print 'executing ' + sql%self.databaseFields
        insertCursor = connection.cursor()
        insertCursor.execute(sql,self.databaseFields)
        connection.commit()
        insertCursor.close()
        self.obState.update({'NEW' : 0 , 'DB_PENDING' : 0, 'MESSAGE' : "database insert OK"})


    def runArrayImport(self, connection):
        """ this method imports a microarray definition into the database.

        The dataSource and labResource objects have already been initialised but
        not yet committed to the database. The importProcedure object already exists in the
        database.
        
        The following steps are involved :

        1. a GALFileParser parses the header and column headings 
        
        2. The dataSource object has been initialised and is now ommitted to the database

        3. The labResource object has been initialised and is now committed to the database
        
        3. The header data is inserted into the microarrayFact table (foreign key the
        existing labResource object already created)
        
        4. The parser.nextRecord method is called , each row inserted into the microarraySpotFact
        # table (foreign key as above)
        
        5. Finally , the importFunction is committed to the database , which records this import
        """
        # get the dataSource type and create a parser
        print "import processing %s"%self.dataSource.databaseFields['datasourcetype']

        if self.dataSource.databaseFields['datasourcetype'] == 'AffyAnnotation':
            # this contains (at least for the bovine chip) records like
            #Probe Set ID	GeneChip Array	Species Scientific Name	Annotation Date	Sequence Type	Sequence Source	Transcript ID(Array Design)	Target Description	Representative Public ID	Archival UniGene Cluster	UniGene ID	Genome Version	Alignments	Gene Title	Gene Symbol	Chromosomal Location	Unigene Cluster Type	Ensembl	Entrez Gene	SwissProt	EC	OMIM	RefSeq Protein ID	RefSeq Transcript ID	FlyBase	AGI	WormBase	MGI Name	RGD Name	SGD accession number	Gene Ontology Biological Process	Gene Ontology Cellular Component	Gene Ontology Molecular Function	Pathway	Protein Families	Protein Domains	InterPro	Trans Membrane	QTL	Annotation Description	Annotation Transcript Cluster	Transcript Assignments	Annotation Notes
            #AFFX-BioB-3_at	Bovine Array	Bos taurus	Jul 12, 2006	Consensus sequence	Affymetrix Proprietary Database	AFFX-Ec-bioB	E. coli /GEN=bioB /DB_XREF=gb:J04423.1 /NOTE=SIF corresponding to nucleotides 2755-3052 of gb:J04423.1 /DEF=E.coli 7,8-diamino-pelargonic acid (bioA), biotin synthetase (bioB), 7-keto-8-amino-pelargonic acid synthetase (bioF), bioC protein, and dethiobiotin synthetase (bioD), complete cds.	AFFX-BioB-3	---	---	---	---	---	---	---	---	---	---	P12994 /// P12995 /// P12996 /// P12998 /// P12999 /// P13000	---	---	---	---	---	---	---	---	---	---	9102 // biotin biosynthesis // inferred from electronic annotation /// 8152 // metabolism // inferred from electronic annotation /// 9058 // biosynthesis // inferred from electronic annotation /// 9236 // cobalamin biosynthesis // inferred from electronic annotation	---	4015 // adenosylmethionine-8-amino-7-oxononanoate transaminase activity // inferred from electronic annotation /// 8483 // transaminase activity // inferred from electronic annotation /// 16740 // transferase activity // inferred from electronic annotation /// 30170 // pyridoxal phosphate binding // inferred from electronic annotation /// 3824 // catalytic activity // inferred from electronic annotation /// 4076 // biotin synthase activity // inferred from electronic annotation /// 5506 // iron ion binding // inferred from electronic annotation /// 46872 // metal ion binding // inferred from electronic annotation /// 51536 // iron-sulfur cluster binding // inferred from electronic annotation /// 51537 // 2 iron, 2 sulfur cluster binding // inferred from electronic annotation /// 51539 // 4 iron, 4 sulfur cluster binding // inferred from electronic annotation /// 8710 // 8-amino-7-oxononanoate synthase activity // inferred from electronic annotation /// 16769 // transferase activity, transferring nitrogenous groups // inferred from electronic annotation /// 8168 // methyltransferase activity // inferred from electronic annotation /// 8757 // S-adenosylmethionine-dependent methyltransferase activity // inferred from electronic annotation /// 166 // nucleotide binding // inferred from electronic annotation /// 287 // magnesium ion binding // inferred from electronic annotation /// 4141 // dethiobiotin synthase activity // inferred from electronic annotation /// 5524 // ATP binding // inferred from electronic annotation /// 16874 // ligase activity // inferred from electronic annotation /// 42242 // cobyrinic acid a,c-diamide synthase activity // inferred from electronic annotation	---	---	---	---	---	---	This probe set was annotated using the Design Representative Id based pipeline to a GenBank identifier using 4 transcripts. // false // Design Representative Id // R	J04423	J04423 // J04423 E coli bioB gene biotin synthetase  (-5, -M, -3 represent transcript regions 5 prime, Middle, and 3 prime respectively) // gb // --- // --- /// J04423 // Escherichia coli /REF=J04423 /DEF=E coli bioB gene biotin synthetase corresponding to nucleotides 2393-2682 of J04423 /LEN=1114 (-5, -M, -3 represent transcript regions 5 prime, Middle, and 3 prime respectively) // gb // --- // --- /// J04423 // J04423 E coli bioB gene biotin synthetase  (-5, -M, -3 represent transcript regions 5 prime, Middle, and 3 prime respectively) // gb // --- // --- /// J04423 // J04423 E coli bioB gene biotin synthetase  (-5, -M, -3 represent transcript regions 5 prime, Middle, and 3 prime respectively) // gb // --- // --- /// J04423 // J04423 E coli bioB gene biotin synthetase  (-5, -M, -3 represent transcript regions 5 prime, Middle, and 3 prime respectively) // gb // --- // --- /// J04423 // J04423 E coli bioB gene biotin synthetase  (-5, -M, -3 represent transcript regions 5 prime, Middle, and 3 prime respectively) // gb // --- // --- /// AFFX-BioB-3 // E. coli /GEN=bioB /DB_XREF=gb:J04423.1 /NOTE=SIF corresponding to nucleotides 2755-3052 of gb:J04423.1 /DEF=E.coli 7,8-diamino-pelargonic acid (bioA), biotin synthetase (bioB), 7-keto-8-amino-pelargonic acid synthetase (bioF), bioC protein, and dethiobiotin synthetase (bioD), complete cds. // affx // --- // --- /// J04423 // Escherichia coli /REF=J04423 /DEF=E coli bioB gene biotin synthetase /LEN=1114 (-5, -M, -3 represent transcript regions 5 prime, Middle, and 3 prime respectively) // gb // --- // --- /// AFFX-BioB-3 // --- // unknown // --- // --- /// AFFX-BioB-3 // --- // unknown // --- // --- /// AFFX-BioB-3 // --- // unknown // --- // --- /// AFFX-BioB-3 // --- // unknown // --- // --- /// AFFX-BioB-3 // --- // gb // --- // --- /// AFFX-BioB-3 // E. coli /GEN=bioB /DB_XREF=gb:J04423.1 /NOTE=SIF corresponding to nucleotides 2755-3052 of gb:J04423.1 /DEF=E.coli 7,8-diamino-pelargonic acid (bioA), biotin synthetase (bioB), 7-keto-8-amino-pelargonic acid synthetase (bioF), bioC protein, and dethiobiotin synthetase (bioD), complete cds. // affx // --- // --- /// J04423 // J04423 E coli bioB gene biotin synthetase  (-5, -M, -3 represent transcript regions 5 prime, Middle, and 3 prime respectively) // gb // --- // --- /// --- // --- // affx // --- // --- /// --- // --- // affx // --- // --- /// AFFX-BioB-3 // --- // unknown // --- // --- /// AFFX-BioB-3 // --- // affx // --- // --- /// AFFX-BioB-3 // --- // affx // --- // --- /// --- // --- // affx // --- // --- /// AFFX-BioB-3 // --- // affx // --- // --- /// AFFX-BioB-3 // --- // affx // --- // --- /// AFFX-BioB-3 // --- // affx // --- // --- /// AFFX-BioB-3 // --- // affx // --- // --- /// AFFX-BioB-3 // --- // affx // --- // --- /// AFFX-BioB-3 // --- // affx // --- // --- /// AFFX-BioB-3 // --- // affx // --- // --- /// AFFX-BioB-3 // --- // affx // --- // --- /// AFFX-BioB-3 // --- // affx // --- // --- /// AFFX-BioB-3 // --- // affx // --- // --- /// AFFX-BioB-3 // --- // affx // --- // --- /// AFFX-BioB-3 // --- // affx // --- // --- /// AFFX-BioB-3 // --- // affx // --- // ---	---
            #AFFX-BioB-5_at	Bovine Array	Bos taurus	Jul 12, 2006	Consensus sequence	Affymetrix Proprietary Database	AFFX-Ec-bioB	E. coli /GEN=bioB /DB_XREF=gb:J04423.1 /NOTE=SIF corresponding to nucleotides 2032-2305 of gb:J04423.1 /DEF=E.coli 7,8-diamino-pelargonic acid (bioA), biotin synthetase (bioB), 7-keto-8-amino-pelargonic acid synthetase (bioF), bioC protein, and dethiobiotin synthetase (bioD), complete cds.	AFFX-BioB-5	---	---	---	---	---	---	---	---	---	---	P12994 /// P12995 /// P12996 /// P12998 /// P12999 /// P13000	---	---	---	---	---	---	---	---	---	---	9102 // biotin biosynthesis // inferred from electronic annotation /// 8152 // metabolism // inferred from electronic annotation /// 9058 // biosynthesis // inferred from electronic annotation /// 9236 // cobalamin biosynthesis // inferred from electronic annotation	---	4015 // adenosylmethionine-8-amino-7-oxononanoate transaminase activity // inferred from electronic annotation /// 8483 // transaminase activity // inferred from electronic annotation /// 16740 // transferase activity // inferred from electronic annotation /// 30170 // pyridoxal phosphate binding // inferred from electronic annotation /// 3824 // catalytic activity // inferred from electronic annotation /// 4076 // biotin synthase activity // inferred from electronic annotation /// 5506 // iron ion binding // inferred from electronic annotation /// 46872 // metal ion binding // inferred from electronic annotation /// 51536 // iron-sulfur cluster binding // inferred from electronic annotation /// 51537 // 2 iron, 2 sulfur cluster binding // inferred from electronic annotation /// 51539 // 4 iron, 4 sulfur cluster binding // inferred from electronic annotation /// 8710 // 8-amino-7-oxononanoate synthase activity // inferred from electronic annotation /// 16769 // transferase activity, transferring nitrogenous groups // inferred from electronic annotation /// 8168 // methyltransferase activity // inferred from electronic annotation /// 8757 // S-adenosylmethionine-dependent methyltransferase activity // inferred from electronic annotation /// 166 // nucleotide binding // inferred from electronic annotation /// 287 // magnesium ion binding // inferred from electronic annotation /// 4141 // dethiobiotin synthase activity // inferred from electronic annotation /// 5524 // ATP binding // inferred from electronic annotation /// 16874 // ligase activity // inferred from electronic annotation /// 42242 // cobyrinic acid a,c-diamide synthase activity // inferred from electronic annotation	---	---	---	---	---	---	This probe set was annotated using the Design Representative Id based pipeline to a GenBank identifier using 4 transcripts. // false // Design Representative Id // R	J04423	J04423 // J04423 E coli bioB gene biotin synthetase  (-5, -M, -3 represent transcript regions 5 prime, Middle, and 3 prime respectively) // gb // --- // --- /// J04423 // Escherichia coli /REF=J04423 /DEF=E coli bioB gene biotin synthetase corresponding to nucleotides 2393-2682 of J04423 /LEN=1114 (-5, -M, -3 represent transcript regions 5 prime, Middle, and 3 prime respectively) // gb // --- // --- /// J04423 // J04423 E coli bioB gene biotin synthetase  (-5, -M, -3 represent transcript regions 5 prime, Middle, and 3 prime respectively) // gb // --- // --- /// J04423 // J04423 E coli bioB gene biotin synthetase  (-5, -M, -3 represent transcript regions 5 prime, Middle, and 3 prime respectively) // gb // --- // --- /// J04423 // J04423 E coli bioB gene biotin synthetase  (-5, -M, -3 represent transcript regions 5 prime, Middle, and 3 prime respectively) // gb // --- // --- /// J04423 // J04423 E coli bioB gene biotin synthetase  (-5, -M, -3 represent transcript regions 5 prime, Middle, and 3 prime respectively) // gb // --- // --- /// J04423 // J04423 E coli bioB gene biotin synthetase  (-5, -M, -3 represent transcript regions 5 prime, Middle, and 3 prime respectively) // gb // --- // --- /// AFFX-BioB-5 // E. coli /GEN=bioB /DB_XREF=gb:J04423.1 /NOTE=SIF corresponding to nucleotides 2032-2305 of gb:J04423.1 /DEF=E.coli 7,8-diamino-pelargonic acid (bioA), biotin synthetase (bioB), 7-keto-8-amino-pelargonic acid synthetase (bioF), bioC protein, and dethiobiotin synthetase (bioD), complete cds. // affx // --- // --- /// J04423 // Escherichia coli /REF=J04423 /DEF=E coli bioB gene biotin synthetase /LEN=1114 (-5, -M, -3 represent transcript regions 5 prime, Middle, and 3 prime respectively) // gb // --- // --- /// AFFX-BioB-5 // --- // unknown // --- // --- /// AFFX-BioB-5 // --- // unknown // --- // --- /// AFFX-BioB-5 // --- // unknown // --- // --- /// AFFX-BioB-5 // --- // unknown // --- // --- /// AFFX-BioB-5 // --- // gb // --- // --- /// AFFX-BioB-5 // E. coli /GEN=bioB /DB_XREF=gb:J04423.1 /NOTE=SIF corresponding to nucleotides 2032-2305 of gb:J04423.1 /DEF=E.coli 7,8-diamino-pelargonic acid (bioA), biotin synthetase (bioB), 7-keto-8-amino-pelargonic acid synthetase (bioF), bioC protein, and dethiobiotin synthetase (bioD), complete cds. // affx // --- // --- /// J04423 // J04423 E coli bioB gene biotin synthetase  (-5, -M, -3 represent transcript regions 5 prime, Middle, and 3 prime respectively) // gb // --- // --- /// --- // --- // affx // --- // --- /// --- // --- // affx // --- // --- /// AFFX-BioB-5 // --- // unknown // --- // --- /// AFFX-BioB-5 // --- // affx // --- // --- /// AFFX-BioB-5 // --- // affx // --- // --- /// --- // --- // affx // --- // --- /// AFFX-BioB-5 // --- // affx // --- // --- /// AFFX-BioB-5 // --- // affx // --- // --- /// AFFX-BioB-5 // --- // affx // --- // --- /// AFFX-BioB-5 // --- // affx // --- // --- /// AFFX-BioB-5 // --- // affx // --- // --- /// AFFX-BioB-5 // --- // affx // --- // --- /// AFFX-BioB-5 // --- // affx // --- // --- /// AFFX-BioB-5 // --- // affx // --- // --- /// AFFX-BioB-5 // --- // affx // --- // --- /// AFFX-BioB-5 // --- // affx // --- // --- /// AFFX-BioB-5 // --- // affx // --- // --- /// AFFX-BioB-5 // --- // affx // --- // --- /// AFFX-BioB-5 // --- // affx // --- // ---	---
            #AFFX-BioB-M_at	Bovine Array	Bos taurus	Jul 12, 2006	Consensus sequence	Affymetrix Proprietary Database	AFFX-Ec-bioB	E. coli /GEN=bioB /DB_XREF=gb:J04423.1 /NOTE=SIF corresponding to nucleotides 2482-2739 of gb:J04423.1 /DEF=E.coli 7,8-diamino-pelargonic acid (bioA), biotin synthetase (bioB), 7-keto-8-amino-pelargonic acid synthetase (bioF), bioC protein, and dethiobiotin synthetase (bioD), complete cds.	AFFX-BioB-M	---	---	---	---	---	---	---	---	---	---	P12994 /// P12995 /// P12996 /// P12998 /// P12999 /// P13000	---	---	---	---	---	---	---	---	---	---	9102 // biotin biosynthesis // inferred from electronic annotation /// 8152 // metabolism // inferred from electronic annotation /// 9058 // biosynthesis // inferred from electronic annotation /// 9236 // cobalamin biosynthesis // inferred from electronic annotation	---	4015 // adenosylmethionine-8-amino-7-oxononanoate transaminase activity // inferred from electronic annotation /// 8483 // transaminase activity // inferred from electronic annotation /// 16740 // transferase activity // inferred from electronic annotation /// 30170 // pyridoxal phosphate binding // inferred from electronic annotation /// 3824 // catalytic activity // inferred from electronic annotation /// 4076 // biotin synthase activity // inferred from electronic annotation /// 5506 // iron ion binding // inferred from electronic annotation /// 46872 // metal ion binding // inferred from electronic annotation /// 51536 // iron-sulfur cluster binding // inferred from electronic annotation /// 51537 // 2 iron, 2 sulfur cluster binding // inferred from electronic annotation /// 51539 // 4 iron, 4 sulfur cluster binding // inferred from electronic annotation /// 8710 // 8-amino-7-oxononanoate synthase activity // inferred from electronic annotation /// 16769 // transferase activity, transferring nitrogenous groups // inferred from electronic annotation /// 8168 // methyltransferase activity // inferred from electronic annotation /// 8757 // S-adenosylmethionine-dependent methyltransferase activity // inferred from electronic annotation /// 166 // nucleotide binding // inferred from electronic annotation /// 287 // magnesium ion binding // inferred from electronic annotation /// 4141 // dethiobiotin synthase activity // inferred from electronic annotation /// 5524 // ATP binding // inferred from electronic annotation /// 16874 // ligase activity // inferred from electronic annotation /// 42242 // cobyrinic acid a,c-diamide synthase activity // inferred from electronic annotation	---	---	---	---	---	---	This probe set was annotated using the Design Representative Id based pipeline to a GenBank identifier using 4 transcripts. // false // Design Representative Id // R	J04423	J04423 // J04423 E coli bioB gene biotin synthetase  (-5, -M, -3 represent transcript regions 5 prime, Middle, and 3 prime respectively) // gb // --- // --- /// J04423 // Escherichia coli /REF=J04423 /DEF=E coli bioB gene biotin synthetase corresponding to nucleotides 2393-2682 of J04423 /LEN=1114 (-5, -M, -3 represent transcript regions 5 prime, Middle, and 3 prime respectively) // gb // --- // --- /// J04423 // J04423 E coli bioB gene biotin synthetase  (-5, -M, -3 represent transcript regions 5 prime, Middle, and 3 prime respectively) // gb // --- // --- /// J04423 // J04423 E coli bioB gene biotin synthetase  (-5, -M, -3 represent transcript regions 5 prime, Middle, and 3 prime respectively) // gb // --- // --- /// J04423 // J04423 E coli bioB gene biotin synthetase  (-5, -M, -3 represent transcript regions 5 prime, Middle, and 3 prime respectively) // gb // --- // --- /// J04423 // J04423 E coli bioB gene biotin synthetase  (-5, -M, -3 represent transcript regions 5 prime, Middle, and 3 prime respectively) // gb // --- // --- /// AFFX-BioB-M // E. coli /GEN=bioB /DB_XREF=gb:J04423.1 /NOTE=SIF corresponding to nucleotides 2482-2739 of gb:J04423.1 /DEF=E.coli 7,8-diamino-pelargonic acid (bioA), biotin synthetase (bioB), 7-keto-8-amino-pelargonic acid synthetase (bioF), bioC protein, and dethiobiotin synthetase (bioD), complete cds. // affx // --- // --- /// J04423 // Escherichia coli /REF=J04423 /DEF=E coli bioB gene biotin synthetase /LEN=1114 (-5, -M, -3 represent transcript regions 5 prime, Middle, and 3 prime respectively) // gb // --- // --- /// AFFX-BioB-M // --- // unknown // --- // --- /// AFFX-BioB-M // --- // unknown // --- // --- /// AFFX-BioB-M // --- // unknown // --- // --- /// AFFX-BioB-M // --- // unknown // --- // --- /// AFFX-BioB-M // --- // gb // --- // --- /// AFFX-BioB-M // E. coli /GEN=bioB /DB_XREF=gb:J04423.1 /NOTE=SIF corresponding to nucleotides 2482-2739 of gb:J04423.1 /DEF=E.coli 7,8-diamino-pelargonic acid (bioA), biotin synthetase (bioB), 7-keto-8-amino-pelargonic acid synthetase (bioF), bioC protein, and dethiobiotin synthetase (bioD), complete cds. // affx // --- // --- /// J04423 // J04423 E coli bioB gene biotin synthetase  (-5, -M, -3 represent transcript regions 5 prime, Middle, and 3 prime respectively) // gb // --- // --- /// --- // --- // affx // --- // --- /// --- // --- // affx // --- // --- /// AFFX-BioB-M // --- // unknown // --- // --- /// AFFX-BioB-M // --- // affx // --- // --- /// AFFX-BioB-M // --- // affx // --- // --- /// --- // --- // affx // --- // --- /// AFFX-BioB-M // --- // affx // --- // --- /// AFFX-BioB-M // --- // affx // --- // --- /// AFFX-BioB-M // --- // affx // --- // --- /// AFFX-BioB-M // --- // affx // --- // --- /// AFFX-BioB-M // --- // affx // --- // --- /// AFFX-BioB-M // --- // affx // --- // --- /// AFFX-BioB-M // --- // affx // --- // --- /// AFFX-BioB-M // --- // affx // --- // --- /// AFFX-BioB-M // --- // affx // --- // --- /// AFFX-BioB-M // --- // affx // --- // --- /// AFFX-BioB-M // --- // affx // --- // --- /// AFFX-BioB-M // --- // affx // --- // --- /// AFFX-BioB-M // --- // affx // --- // ---	---

            # create a GALFile parser.
            parser = GALFileParser(self.dataSource.databaseFields['physicalsourceuri'])
            parser.parse()        


        if self.dataSource.databaseFields['datasourcetype'] == 'GALFile':
            # this contain content like :

#ATF	1.0
#8	10
#"Type=GenePix ArrayList V1.0"
#"BlockCount=1"
#"BlockType=3"
#"URL=http://www.ncbi.nlm.nih.gov/entrez/query.fcgi?cmd=Search&db=Nucleotide&term=[Name]"
#"Supplier=Agilent Technologies"
#"ArrayName=Agilent-012694:Whole Mouse Genome"
#"DesignID=012694"
#"Block1 = 1436.788904, 13845.7999285, 95, 103, 188.148148, 430, 105.8333335"
#"Block"	"Column"	"Row"	"Name"	"ID"	"RefNumber"	"ControlType"	"GeneName"	"TopHit"	"Description"
#"1"	"1"	"1"	"BrightCorner"	"BrightCorner"	"44290"	"pos"	"BrightCorner"	""	""
#"1"	"2"	"1"	"BrightCorner"	"BrightCorner"	"43860"	"pos"	"BrightCorner"	""	""
#"1"	"3"	"1"	"NegativeControl"	"(-)3xSLv1"	"43430"	"neg"	"(-)3xSLv1"	""	""
#"1"	"4"	"1"	"XM_145466"	"A_51_P330380"	"43000"	"false"	"XM_145466"	"ref|XM_145466|ens|ENSMUST00000077356|ens|ENSMUST00000082214|ens|ENSMUST00000076558"	"PREDICTED: Mus musculus similar to cytochrome P450 CYP2B21 (LOC243881), mRNA [XM_145466]"
#"1"	"5"	"1"	"NM_172143"	"A_51_P119161"	"42570"	"false"	"NM_172143"	"ref|NM_172143|gb|AF548110|gb|AF548111|ens|ENSMUST00000054635"	"Mus musculus orofacial cleft 1 candidate 1 (Ofcc1), mRNA [NM_172143]"
#"1"	"6"	"1"	"N                
            # create a GALFile parser.
            if 'headerDict' in self.__dict__:
                parser = GALFileParser(self.dataSource.databaseFields['physicalsourceuri'], headerDict = self.headerDict)
            else:
                parser = GALFileParser(self.dataSource.databaseFields['physicalsourceuri'])
 
            parser.parse()
            if [parser.parserState[state] for state in ("BODY" , "ERROR", "EOF")] != [1,0,0]:
                raise brdfException, "error or EOF parsing GALFile " + parser.comment
                

            # commit the dataSource and labResource obs
            self.dataSource.insertDatabase(connection)
            self.labResource.insertDatabase(connection)

            # insert the microarrayFacts
            self.obState.update({'DB_PENDING' : 1, 'MESSAGE' : "about to insert microarray fact data"})
            # example 'gal_Block1': ' 1000, 1000, 135, 105, 188.148148, 215, 211.666667',
            #'gal_URL': ' http://www.ncbi.nlm.nih.gov/entrez/query.fcgi?cmd', 'gal_BlockType': '0',
            #'gal_BlockCount': '1', 'gal_Supplier': 'Agilent Technologies', 'gal_Type': 'GenePix ArrayList V1.0'
            insertFields = parser.headerDict
            print insertFields
            
            insertFields.update( 
                {'labresourceob' : self.labResource.databaseFields['obid'] , 
                 'arrayname' : self.labResource.databaseFields['xreflsid'] ,
                 'xreflsid' : "%s.details"%self.labResource.databaseFields['xreflsid'],
                 'gal_url' : eval({True : "insertFields['gal_url']" , False : "None"}[ 'gal_url' in insertFields ]),
                 'gal_supplier' : eval({True : "insertFields['gal_supplier']" , False : "None"}[ 'gal_supplier' in insertFields ])                 
                 })
            
            sql = "insert into microarrayfact(labresourceob,xreflsid,arrayname,gal_type, \
                  gal_blockcount, gal_blocktype, gal_url, gal_supplier, gal_block1 ) values \
                 (%(labresourceob)s,%(xreflsid)s,%(arrayname)s,%(gal_type)s, \
                  %(gal_blockcount)s, %(gal_blocktype)s, %(gal_url)s, %(gal_supplier)s, %(gal_block1)s)"
            #print 'executing ' + sql%insertFields
            insertCursor = connection.cursor()
            insertCursor.execute(sql,insertFields)
            insertCursor.close()
            connection.commit()


            # add the rest of the header as misc lab resource facts
            for key in insertFields.keys():
                if key not in [
                    'labresourceob',
                    'xreflsid',
                    'arrayname',
                    'gal_type',
                    'gal_blockcount',
                    'gal_blocktype',
                    'gal_url',
                    'gal_supplier',
                    'gal_block1'
                    ]:
                    self.labResource.addFact(connection,'MICROARRAY SPECIFICATION', key, insertFields[key])
                    


            # insert the microarrayFacts
            self.obState.update({'DB_PENDING' : 1, 'MESSAGE' : "done microarrayfacts about to do microarray spot facts"})



            # insert the microarray spot facts
            sql = """
                  insert into microarrayspotfact(labresourceob,obkeywords,gal_block, gal_column, gal_row, 
                  gal_name, gal_id, gal_refnumber, gal_controltype, gal_genename, 
                  gal_tophit, gal_description, xreflsid)
                  values ( %(labresourceob)s,%(obkeywords)s,%(gal_block)s, %(gal_column)s, %(gal_row)s, 
                  %(gal_name)s, %(gal_id)s, %(gal_refnumber)s, %(gal_controltype)s, %(gal_genename)s, 
                  %(gal_tophit)s, %(gal_description)s ,  %(xreflsid)s) """
            insertCursor = connection.cursor()
            insertCount = 0
            while parser.parserState["EOF"] == 0 :
                insertFields = parser.nextRecord()

                if insertFields == None:
                    break

                #sometimes we only have Block	Column	Row	ID	Name
                insertFields.update(
                    {
                    'xreflsid' : "%s.B%s.C%s.R%s"%(self.labResource.databaseFields['xreflsid'],insertFields['gal_block'],insertFields['gal_column'],insertFields['gal_row']),
                    'labresourceob' : self.labResource.databaseFields['obid'] , 
                    'obkeywords' : eval({True : "insertFields['gal_description']" , False : "None"}[ 'gal_description' in insertFields ]),
                    'gal_refnumber' : eval({True : "insertFields['gal_refnumber']" , False : "None"}[ 'gal_refnumber' in insertFields ]) ,
                    'gal_controltype' : eval({True : "insertFields['gal_controltype']" , False : "None"}[ 'gal_controltype' in insertFields ]) ,
                    'gal_genename' : eval({True : "insertFields['gal_genename']" , False : "None"}[ 'gal_genename' in insertFields ]) ,
                    'gal_tophit' : eval({True : "insertFields['gal_tophit']" , False : "None"}[ 'gal_tophit' in insertFields ]) ,
                    'gal_description' : eval({True : "insertFields['gal_description']" , False : "None"}[ 'gal_description' in insertFields ])                     
                    })
                self.obState.update({'MESSAGE' : 'executing ' + sql%insertFields })
                insertCursor.execute(sql,insertFields)
                connection.commit()
                insertCount += 1
                
            insertCursor.close()

            # commit the import function
            self.insertDatabase(connection)

            # create a labResourceList object and add the new array to it
            resourceList = labResourceList()
            resourceList.initNew(connection=connection, \
                                 listname=self.labResource.databaseFields['resourcename'] + " List", \
                                 xreflsid=self.labResource.databaseFields['xreflsid'] + " List", \
                                 obkeywords=self.labResource.databaseFields['obkeywords'] + " List" )
            resourceList.insertDatabase(connection)
            resourceList.addLabResource(connection,self.labResource,"Default List")
            

            self.obState.update({'DB_PENDING' : 0, 'MESSAGE' : "Array import complete , inserted " + str(insertCount) + " records"})

            
        elif self.dataSource.databaseFields['datasourcetype'] == 'GALFile_noheader':
# this contains content like :
#            meta_row	meta_col	row1	col	ref
#1	4	1	24	CPROT70 3919
#1	4	2	24	CPROT70 02407
#1	4	3	24	CPROT70 03990
#1	4	4	24	CPROT70 00252
#1	4	5	24	CPROT70 01134
#1	4	6	24	CPROT70 02139
#1	4	7	24	CPROT70 00438
#1	4	8	24	CPROT70 00733
#1	4	9	24	CPROT70 00024
            # create a GALFile parser.
            parser = GALFileParser(self.dataSource.databaseFields['physicalsourceuri'],False)
            parser.parse()
            if [parser.parserState[state] for state in ("BODY" , "ERROR", "EOF")] != [1,0,0]:
                raise brdfException, "error or EOF parsing GALFile " + parser.comment
                

            # commit the dataSource and labResource obs
            self.dataSource.insertDatabase(connection)
            self.labResource.insertDatabase(connection)



            #['gal_meta_row', 'gal_meta_col', 'gal_row1', 'gal_col', 'gal_ref']
            # insert the microarray spot facts
            sql = """
                  insert into microarrayspotfact(labresourceob, xreflsid, blockrow,blockcolumn,metarow,metacolumn,
                  gal_row,gal_column,gal_name,accession)
                  values ( %(labresourceob)s, %(xreflsid)s, %(blockrow)s,%(blockcolumn)s,%(metarow)s,%(metacolumn)s,
                  %(gal_row)s,%(gal_column)s,%(gal_name)s,%(accession)s)"""
            insertCursor = connection.cursor()
            insertCount = 0
            while parser.parserState["EOF"] == 0 :
                insertFields = parser.nextRecord()

                print "processing %s"%str(insertFields)

                if insertFields == None:
                    break

                insertFields.update(
                    {
                    'xreflsid' : "%s.BC%s.BR%s.C%s.R%s"%(self.labResource.databaseFields['xreflsid'],\
                                    insertFields['gal_meta_col'],insertFields['gal_meta_row'],insertFields['gal_col'],\
                                    insertFields['gal_row1']),
                    'labresourceob' : self.labResource.databaseFields['obid'] , 
                    'blockrow' : insertFields['gal_row1'] ,
                    'blockcolumn' : insertFields['gal_col']  ,
                    'metarow' : insertFields['gal_meta_row'] ,
                    'metacolumn' : insertFields['gal_meta_col']  ,
                    'gal_row' : insertFields['gal_row1'] ,
                    'gal_column' : insertFields['gal_col']  ,
                    'gal_name' : insertFields['gal_ref'] ,
                    'accession' : insertFields['gal_ref']
                    })
                self.obState.update({'MESSAGE' : 'executing ' + sql%insertFields })
                insertCursor.execute(sql,insertFields)
                connection.commit()
                insertCount += 1
                
            insertCursor.close()

            # commit the import function
            self.insertDatabase(connection)

            # create a labResourceList object and add the new array to it
            resourceList = labResourceList()
            resourceList.initNew(connection=connection, \
                                 listname=self.labResource.databaseFields['resourcename'] + " List", \
                                 xreflsid=self.labResource.databaseFields['xreflsid'] + " List", \
                                 obkeywords=self.labResource.databaseFields['obkeywords'] + " List" )
            resourceList.insertDatabase(connection)
            resourceList.addLabResource(connection,self.labResource,"Default List")
            

            self.obState.update({'DB_PENDING' : 0, 'MESSAGE' : "Array import complete , inserted " + str(insertCount) + " records"})

            blockSQL = """
            update microarrayspotfact
            set blocknumber  = metacolumn +(metarow-1)*
            (select max(metacolumn) from
            microarrayspotfact
            where labresourceob=%s) where labresourceob=%s;


            update microarrayspotfact
            set gal_block = blocknumber where
            labresourceob = %s

            """%(self.labResource.databaseFields['obid'], \
                 self.labResource.databaseFields['obid'], \
                 self.labResource.databaseFields['obid'])            
            print "!!!!! execute the following code to intialise block number : %s"%blockSQL            
            
        elif self.dataSource.databaseFields['datasourcetype'] == 'AgResearchArrayExtract1':
            """
            the extract being processed here looks like this :

EST,SpotId,publishedid,rw,cl,metarw,metacl,nr,NRDESCRIPTION,NREVALUE,NR_GENE,SYNONYMS,NR_GENEID,GOANNOTATION
 
"000811BMVB005956HT",796610,"DY124989",1,1,1,1,"","","","","",,""
"000811BMVB005935HT",796586,"AGNZ114582",1,1,1,2,"NP_777046","ref|NP_777046.1| transforming growth factor beta, receptor 1 [Bos taurus] gb|AAC02717.1| transforming growth factor-beta receptor type I [Bos taurus","   .00E+00","TGFBR1","-",282382,"ATP binding ; integral to membrane ; magnesium ion binding ; manganese ion binding ; membrane ; nucleotide binding ; protein amino acid phosphorylation ; receptor activity ; transferase activity ; transforming growth factor beta receptor activity, type I ; transforming growth factor beta receptor signaling pathway"
"000811BMVB005909HT",796562,"DY169711",1,1,1,3,"","","","","",,""
"000829BEMN001374HT",796538,"DY082449",1,1,1,4,"XP_514718","ref|XP_514718.1| PREDICTED: hypothetical protein XP_514718 [Pan troglodytes","  2.00E-75","LOC458329","-",458329,""

            and the code that generates this is as follows :

select
   /*+ RULE */
   nvl(agplsqlutils.getSequenceName(altid_num),mps.contentid)  "EST",
   mps.spotid "SpotId",
   nvl(ags.genbankaccession, 'AGNZ'||to_char(mpsp.publishedid)) "publishedid",
   mps.dimension1 "rw",
   mps.dimension2 "cl",
   mps.dimension3 "metarw",
   mps.dimension4 "metacl",
   agplsqlutils.deVersion(agplsqlutils.dePipe(agplsqlutils.getTopDBSearchHit(altid_num,'NCBInr','hitid'))) "nr",
   agplsqlutils.getTopDBSearchHit(altid_num,'NCBInr','description') nrdescription ,
   agplsqlutils.getTopDBSearchHit(altid_num,'NCBInr','evalue') nrevalue ,
   g.symbol nr_gene,
   g.synonyms,
   g.geneid nr_geneid,
   pubplsqlutils.getGoString(pubplsqlutils.getGeneIdFromAccession(agplsqlutils.deVersion(agplsqlutils.dePipe(agplsqlutils.getTopDBSearchHit(altid_num,'NCBInr','hitid'))),10)) goAnnotation
from
   ops$seqstore.agsequence ags, microarray_productspotpub mpsp , pubstore.geneinfo g, microarray_productspot mps
where
   mps.arrayproductid = 39 and
   mpsp.spotid = mps.spotid and
   g.geneid(+) = pubplsqlutils.getGeneIdFromAccession(agplsqlutils.dePipe(agplsqlutils.getTopDBSearchHit(altid_num,'NCBInr','hitid')),10) and
   ags.sequenceid(+) = mps.altid_num

"""

            
            print "opening reader for %s"%self.dataSource.databaseFields['physicalsourceuri']
            reader = csv.reader(open(self.dataSource.databaseFields['physicalsourceuri'], "rb"))
            rowCount = 0
            insertCursor = connection.cursor()
            insertCount = 0
            fieldNames = []
            # commit the dataSource and labResource obs
            self.dataSource.insertDatabase(connection)
            self.labResource.insertDatabase(connection)            
            for row in reader:
                if len(row) < 10:
                    break
                rowCount += 1
                if rowCount == 1:
                    fieldNames = row
                    fieldNames = [item.lower().strip() for item in fieldNames]
                    print "fieldNames = %s"%str(fieldNames)
                else:
                    # insert the microarrayFacts
                    self.obState.update({'DB_PENDING' : 1, 'MESSAGE' : "about to do microarray spot facts"})

                    fieldDict=dict(zip(fieldNames,row))
                    if fieldDict['nrdescription'] != None:
                        fieldDict['nrdescription'] += ' (blastx evalue=%s)'%fieldDict['nrevalue']
                    fieldDict['obkeywords'] = "%s %s %s"%(fieldDict['nr_gene'],fieldDict['synonyms'],fieldDict['goannotation'])



                    # 8/1/2007. Previous imports mixed up row <-> metarow, col <-> metacol - theis next code was incorrect.
                    # insert the microarray spot fact
                    #sql = """
                    #  insert into microarrayspotfact(labresourceob,obkeywords,metarow,metacolumn,
                    #  blockrow, blockcolumn, accession, gal_tophit, gal_description, gal_genename,xreflsid)
                    #  values ( %(labresourceob)s,%(obkeywords)s,%(metarw)s, %(metacl)s, %(rw)s, 
                    #  %(cl)s, %(est)s, %(nr)s, %(nrdescription)s, %(nr_gene)s,%(xreflsid)s) """
                    #
                    sql = """
                      insert into microarrayspotfact(labresourceob,obkeywords,blockrow, blockcolumn,metarow,metacolumn,
                      accession, gal_tophit, gal_description, gal_genename,xreflsid,gal_name,gal_id)
                      values ( %(labresourceob)s,%(obkeywords)s,%(metarw)s, %(metacl)s, %(rw)s, 
                      %(cl)s, %(est)s, %(nr)s, %(nrdescription)s, %(nr_gene)s,%(xreflsid)s,%(publishedid)s,%(spotid)s) """
                                        
                    fieldDict.update(
                        {
                        'xreflsid' : "%s.BC%s.BR%s.C%s.R%s"%(self.labResource.databaseFields['xreflsid'],\
                                                fieldDict['cl'],fieldDict['rw'],\
                                                fieldDict['metacl'],fieldDict['metarw']),
                        'labresourceob' : self.labResource.databaseFields['obid'] , 
                        'obkeywords' : "%s %s %s"%(fieldDict['nr_gene'],fieldDict['synonyms'],fieldDict['goannotation'])
                        })
                    self.obState.update({'MESSAGE' : 'executing ' + sql%fieldDict })
                    #print "executing %s"%(str(sql%fieldDict))
                    insertCursor.execute(sql,fieldDict)
                    connection.commit()
                    insertCount += 1
                
            insertCursor.close()

            # 8/1/2007 changes corresponding to the above required 
            # update the block column , required for experiment import
            # This is the previous incorrect code
            oldblockSQL = """
            update microarrayspotfact
            set blocknumber  = blockcolumn +(blockrow-1)*
            (select max(blockcolumn) from
            microarrayspotfact
            where labresourceob=%s) where labresourceob=%s;


            update microarrayspotfact
            set gal_block = blocknumber where
            labresourceob = %s

            update microarrayspotfact set gal_column = metacolumn where gal_column is null;
            update microarrayspotfact set gal_row = metarow where gal_row is null;

            """%(self.labResource.databaseFields['obid'], \
                 self.labResource.databaseFields['obid'], \
                 self.labResource.databaseFields['obid'])

            
            blockSQL = """
            update microarrayspotfact
            set blocknumber  = metacolumn +(metarow-1)*
            (select max(metacolumn) from
            microarrayspotfact
            where labresourceob=%s) where labresourceob=%s;


            update microarrayspotfact
            set gal_block = blocknumber where
            labresourceob = %s

            update microarrayspotfact set gal_column = blockcolumn where gal_column is null;
            update microarrayspotfact set gal_row = blockrow where gal_row is null;

            """%(self.labResource.databaseFields['obid'], \
                 self.labResource.databaseFields['obid'], \
                 self.labResource.databaseFields['obid'])            
            print "!!!!! execute the following code to intialise block number : %s"%blockSQL


            
            

            # commit the import function
            self.insertDatabase(connection)

            # create a labResourceList object and add the new array to it
            resourceList = labResourceList()
            resourceList.initNew(connection=connection, \
                                 listname=self.labResource.databaseFields['resourcename'] + " List", \
                                 xreflsid=self.labResource.databaseFields['xreflsid'] + " List", \
                                 obkeywords=self.labResource.databaseFields['obkeywords'] + " List" )
            resourceList.insertDatabase(connection)
            resourceList.addLabResource(connection,self.labResource,"Default List")
            

            self.obState.update({'DB_PENDING' : 0, 'MESSAGE' : "Array import complete , inserted " + str(insertCount) + " records"})

            



class microarrayExperimentImportFunction ( op ) :
    """ a microarrayExperimentImportFunction is a """
    def __init__(self):
        op.__init__(self)

    def initFromDatabase(self, identifier, connection):  
        """ method for initialising an object from database - arg can be an integer obid, or a string importProcedureName"""
          
        if isinstance(identifier,ob):
            #print "initialising import function from id of imported object"
            sql = "select obid from importFunction where ob = %s" % identifier.databaseFields['obid']
            #print "executing " + sql
            obCursor = connection.cursor()
            obCursor.execute(sql)
            obidField = obCursor.fetchone()       
            if obCursor.rowcount != 1:
                self.obState.update({'ERROR' : 1 , 'MESSAGE' : "initFromDatabase unable to find one unique object using " + sql})
                raise brdfException, self.obState['MESSAGE']
            obCursor.close()     
            ob.initFromDatabase(self, obidField[0],"importFunction",connection)
        else:
            ob.initFromDatabase(self, identifier,"importFunction",connection)

        # now get the complete object
        self.databaseFields = getObjectRecord(connection, "importFunction", self.databaseFields['obid'])
        
        self.obState.update({'ERROR' : 0 , 'NEW' : 0, 'MESSAGE' : "initialised from database OK"})                 
        


    def initNew(self,connection,obtuple):
        argTemplate = [classitem.__name__ for classitem in (dataSourceOb,importProcedureOb,geneExpressionStudy)]
        argsSupplied = [obitem.__class__.__name__ for obitem in obtuple]

        if argTemplate != argsSupplied:
            self.obState.update({'ERROR' : 1 , 'MESSAGE' : "args supplied : " + reduce(lambda x,y:x+" "+ y,argsSupplied) + \
                  " args required : " + reduce(lambda x,y:x+" "+y,argTemplate) })
            raise brdfException, self.obState['MESSAGE']       
        
        self.databaseFields = {
            'obid' : getNewObid(connection) ,
            'xreflsid' : "%s.import"%obtuple[2].databaseFields['xreflsid'],
            'dataSourceOb' : obtuple[0].databaseFields['obid'],         
            'importProcedureOb' : obtuple[1].databaseFields['obid'],    
            'geneExpressionStudy' : obtuple[2].databaseFields['obid'] }

        self.dataSource = obtuple[0]
        self.importProcedure = obtuple[1]
        self.geneExpressionStudy = obtuple[2]

        self.obState.update({'DB_PENDING' : 1})
            
    def insertDatabase(self,connection):
        """ method used by microarrayStudyImportFunction to save itself to database  """
        
        sql = "insert into importFunction(obid,dataSourceOb,importProcedureOb,Ob,xreflsid) values (%(obid)s,%(dataSourceOb)s,%(importProcedureOb)s,%(geneExpressionStudy)s,%(xreflsid)s)"
        #print 'executing ' + sql%self.databaseFields
        insertCursor = connection.cursor()
        insertCursor.execute(sql,self.databaseFields)
        connection.commit()
        insertCursor.close()
        self.obState.update({'NEW' : 0 , 'DB_PENDING' : 0, 'MESSAGE' : "database insert OK"})


    def runExperimentImport(self, connection, miameDict=None, lsidprefix=None, arraylsid=None, overrideGALNamecheck = False):
        """ this method imports a microarray experiment into the database.

        The dataSource and study objects have already been initialised but
        not yet committed to the database. The importProcedure object already exists in the
        database.
        
        The following steps are involved :

        1. a GPRFileParser parses the header and column headings 
        
        2. The dataSource object has been initialised and is now ommitted to the database

        3. The study object has been initialised and is now committed to the database
        
        3. The header data is inserted into the miameFact table (foreign key the
        existing labResource object already created)
        
        4. The parser.nextRecord method is called , each row inserted into the microarrayObservation
        # table (foreign key as above)
        
        5. Finally , the importFunction is committed to the database , which records this import
        """






        if self.dataSource.databaseFields['datasourcetype'] == 'CSV from Affy CEL File':
            # "","names","affs427.9.2197PI.181005.CEL","affs427.9.2197PI.181005.CEL.1"
            # This is : probename,probesetname,mismatch,perfectmatch
            #"AFFX-BioB-3_at1","AFFX-BioB-3_at",100,142
            #"AFFX-BioB-3_at2","AFFX-BioB-3_at",94,253
            #"AFFX-BioB-3_at3","AFFX-BioB-3_at",372,519
            #"AFFX-BioB-3_at4","AFFX-BioB-3_at",310,268
            #"AFFX-BioB-3_at5","AFFX-BioB-3_at",72,89
            #"AFFX-BioB-3_at6","AFFX-BioB-3_at",60,109
            fieldNames = ["probename","probesetname","mismatch","perfectmatch"]
            reader = csv.reader(open(self.dataSource.databaseFields['physicalsourceuri']))
                    
            # insert the microarray raw data observations. For the affy arrays, all of the
            # probesets are accumulated in an array and stored in the rawDataRecord field,
            # and just the averages and standard deviations are stored in the main table. This code
            # assumes the data is sorted into probeset groups

            # get all the probesets
            sql = """
            select
                upper(msf.xreflsid),
                msf.xreflsid,
                msf.obid
            from
                microarrayspotfact msf join labresourceob lr on
                lr.xreflsid like '%s%%' and
                msf.labresourceob = lr.obid                
            """%(lsidprefix)

            print "executing %s"%sql
            spotCursor = connection.cursor()
            spotCursor.execute(sql)

            # make a dictionary of seqs for lookup - key is upper case xreflsid, value is a tuple of (xreflsid,obid)
            targetDict = dict([ (mytuple[0],(mytuple[1],mytuple[2])) for mytuple in spotCursor.fetchall() ])
            for key in targetDict.keys()[1:100]:
                print key

            print "%s existing spots loaded"%len(targetDict)

            rowCount = 0
            currentprobeset = ""
            probesetdata = []
            insertCount = 0

            
            for row in reader:
                rowCount += 1
                if rowCount%1000 == 1:
                    print "processing %s"%row

                if rowCount == 1:
                    continue

                fieldDict = dict(zip(fieldNames,row))

                #print "comparing %s and %s"%(fieldDict['probesetname'], currentprobeset)
                if fieldDict['probesetname'] != currentprobeset:
                    if currentprobeset != "":
                        # output the current probesetdata
                        if rowCount%100 == 1:
                            print "inserting %s"%probesetdata
                        # find the probeset in the dictionary
                        # probesetlsid = "%s.%s"%(lsidprefix,fieldDict['probesetname']) ooops ! wrong-o !
                        probesetlsid = "%s.%s"%(lsidprefix,currentprobeset) 
                        if probesetlsid.upper() not in targetDict:
                            print "** error : datapoint %s not found in database"%probesetlsid
                            None
                        else:
                            #print "-- thats good , found %s"%probesetlsid
                            sql = """
                            insert into microarrayobservation(
                             xreflsid              ,
                             microarraystudy       ,
                             microarrayspotfact    ,
                             rawdatarecord         ,
                             affy_meanpm           ,
                             affy_meanmm           ,
                             affy_stddevpm         ,
                             affy_stddevmm         ,
                             affy_count            
                            )
                            values(
                             %(xreflsid)s              ,
                             %(microarraystudy)s       ,
                             %(microarrayspotfact)s    ,
                             %(rawdatarecord)s         ,
                             %(affy_meanpm)s           ,
                             %(affy_meanmm)s         ,
                             %(affy_stdevpm)s         ,
                             %(affy_stdevmm)s         ,
                             %(affy_count)s                                        
                            )
                            """
                            insertData = {
                                'xreflsid' : "%s.%s"%(self.geneExpressionStudy.databaseFields['xreflsid'],probesetlsid),
                                'microarraystudy' : self.geneExpressionStudy.databaseFields['obid'],
                                'microarrayspotfact' : targetDict[probesetlsid.upper()][1],
                                'rawdatarecord' : str(   [(item[0],item[2],item[3]) for item in probesetdata]   ),
                                'affy_count' : len(probesetdata),
                                'affy_meanpm' : mean([float(item[3]) for item in probesetdata]),
                                'affy_meanmm' : mean([float(item[2]) for item in probesetdata]),
                                'affy_stdevpm' : stdev([float(item[3]) for item in probesetdata]),
                                'affy_stdevmm' : stdev([float(item[2]) for item in probesetdata])
                            }
                            if rowCount%100 == 1:
                                print "executing %s"%str(sql%insertData)
                            spotCursor.execute(sql,insertData)
                            connection.commit()
                            insertCount += 1
                        
                        
                    probesetdata = [row]
                    currentprobeset = fieldDict['probesetname']
                else:
                    probesetdata.append(row)

                    
            # output the final row        
            probesetlsid = "%s.%s"%(lsidprefix,currentprobeset) 
            if probesetlsid.upper() not in targetDict:
                print "** error : datapoint %s not found in database"%probesetlsid
                None
            else:
                #print "-- thats good , found %s"%probesetlsid
                sql = """
                    insert into microarrayobservation(
                             xreflsid              ,
                             microarraystudy       ,
                             microarrayspotfact    ,
                             rawdatarecord         ,
                             affy_meanpm           ,
                             affy_meanmm           ,
                             affy_stddevpm         ,
                             affy_stddevmm         ,
                             affy_count            
                            )
                            values(
                             %(xreflsid)s              ,
                             %(microarraystudy)s       ,
                             %(microarrayspotfact)s    ,
                             %(rawdatarecord)s         ,
                             %(affy_meanpm)s           ,
                             %(affy_meanmm)s         ,
                             %(affy_stdevpm)s         ,
                             %(affy_stdevmm)s         ,
                             %(affy_count)s                                        
                            )
                            """
                insertData = {
                        'xreflsid' : "%s.%s"%(self.geneExpressionStudy.databaseFields['xreflsid'],probesetlsid),
                        'microarraystudy' : self.geneExpressionStudy.databaseFields['obid'],
                        'microarrayspotfact' : targetDict[probesetlsid.upper()][1],
                        'rawdatarecord' : str(   [(item[0],item[2],item[3]) for item in probesetdata]   ),
                        'affy_count' : len(probesetdata),
                        'affy_meanpm' : mean([float(item[3]) for item in probesetdata]),
                        'affy_meanmm' : mean([float(item[2]) for item in probesetdata]),
                        'affy_stdevpm' : stdev([float(item[3]) for item in probesetdata]),
                        'affy_stdevmm' : stdev([float(item[2]) for item in probesetdata])
                }
                spotCursor.execute(sql,insertData)
                connection.commit()
                insertCount += 1
                    
        
        

        elif self.dataSource.databaseFields['datasourcetype'] == 'GPRFile':
            # create a GPRFile parser.
            parser = GPRFileParser(self.dataSource.databaseFields['physicalsourceuri'])
            parser.parse()
            if [parser.parserState[state] for state in ("BODY" , "ERROR", "EOF")] != [1,0,0]:
                raise brdfException, "error or EOF parsing GPRFile " + parser.comment


            # check that the GAL file used matches the lsid of the array. The gal file
            # name looks like 'gpr_galfile': 'D:\\012694_D_20050902.gal'
            galfilename = parser.headerDict['gpr_galfile'].split('\\')[-1]
            galspecified = labResourceOb()
            galspecified.initFromDatabase(self.geneExpressionStudy.databaseFields['labresourceob'],connection)
            resourcefilename = string.join(galspecified.databaseFields['xreflsid'].split('.')[-2:],'.')
            if resourcefilename != galfilename and not overrideGALNamecheck :
                raise brdfException , "Error - trying to import using %s but GPR says array is %s"%(resourcefilename,galfilename)
            

#Experimentid!,Experimentname!,Spotid!,Slide_block!,Slide_col!,Slide_row!,Metarow!,Metacol!,ROW!,COL!,EST!,SpotCode!,X!,Y!,Dia,F1Median,F1Mean,F1SD,B1Median,B1Mean,B1SD,B1_PCT_GT_1SD,B1_PCT_GT_2SD,F1_PCT_SAT,F2Median,F2Mean,F2SD,B2Median,B2Mean,B2SD,B2_PCT_GT_1SD,B2_PCT_GT_2SD,F2_PCT_SAT,Ratio_of_Medians,Ratio_of_Means,Median_of_Ratios,Mean_of_Ratios,Ratios_SD,Rgn_Ratio,Rgn_R_SQUARED,F_Pixels,B_Pixels,Sum_of_Medians,Sum_of_Means,Log_Ratio,F1_Median_minus_B1,F2_Median_minus_B2,F1_Mean_minus_B1,F2_Mean_minus_B2,Flags,spotGPRId$
 
#623,"67-29",267199,1,1,1,1,1,1,1,"020502OMGB11020048HT",1,2050,3310,100,1551,1628,789,321,697,2657,7,0,0,1912,2102,1121,830,1164,2641,13,1,0,1.137,1.028,0.944,0.942,2.699,2.041,0.012,80,495,2312,2579,0.185,1230,1082,1307,1272,-100,"OMGB1020048HT"
#623,"67-29",267184,1,2,1,1,1,1,2,"020502OMGB11006045HT",1,2240,3320,80,1302,1341,620,260,344,349,84,69,0,1940,1967,824,897,1016,605,69,40,0,0.999,1.01,1.053,1.122,2.95,0.446,0.112,52,293,2085,2151,-0.001,1042,1043,1081,1070,-100,"OMGB1006045HT"
#623,"67-29",267169,1,3,1,1,1,1,3,"control No. 8",1,2410,3300,100,244,318,226,242,313,217,21,11,0,861,860,454,804,926,591,11,1,0,0.035,1.357,0.257,0.356,3.411,0.021,0.002,80,456,59,132,-4.833,2,57,76,56,-50,"control No. 8"
#623,"67-29",267154,1,4,1,1,1,1,4,"020731OFLT054063HT",1,2580,3310,90,1849,1906,1035,269,363,400,96,86,0,2018,2245,936,633,793,872,76,38,0,1.141,1.016,0.934,1.042,2.346,0.884,0.263,52,364,2965,3249,0.19,1580,1385,1637,1612,0,"OFLT054063HT"
#623,"67-29",267139,1,5,1,1,1,1,5,"020731OFLT041061HT",1,2790,3300,80,1801,1838,716,248,687,2668,7,0,0,2351,2413,1049,588,1602,6660,0,0,0,0.881,0.871,1.093,0.928,2.794,0.567,0.904,52,306,3316,3415,-0.183,1553,1763,1590,1825,0,"OFLT041061HT"
            

            # check that we can map the fields from this source
            if parser.headerDict['gpr_type'] in ['GenePix Results 3', 'GenePix Results 2']:
                fieldMapping = { 'gpr_block' : 'gpr_block',
                                'gpr_column' : 'gpr_column',
                                'gpr_row' : 'gpr_row',
                                'gpr_name' : 'gpr_name',
                                'gpr_id' : 'gpr_id' ,
                                'gpr_dye1foregroundmean' : 'gpr_f635 median',
                                'gpr_dye1backgroundmean' : 'gpr_b635 median',
                                'gpr_dye2foregroundmean' : 'gpr_f532 median',
                                'gpr_dye2backgroundmean' : 'gpr_b532 median',
                                'gpr_logratio' : 'gpr_log ratio (635/532)',
                                'gpr_flags' : 'gpr_flags',
                                'gpr_autoflag' : 'gpr_autoflag'}
                #print "using mapping :"
                #print fieldMapping

                # handle the log ratio the other way around
                if 'gpr_log ratio (635/532)' not in parser.columnHeadings:
                    if 'gpr_log ratio (532/635)' in parser.columnHeadings:
                        fieldMapping['gpr_logratio'] = 'gpr_log ratio (532/635)'
                    else:
                        self.obState.update({'NEW' : 0 , 'ERROR' : 1 , 'MESSAGE' : "Error - cannot find logratio in GPR file"})
                        raise brdfException, self.obState['MESSAGE']

                # handle missing autoflag
                if 'gpr_autoflag' not in parser.columnHeadings:
                    del fieldMapping['gpr_autoflag']


                
            elif parser.headerDict['gpr_type'] in ['GenePix Results 1.4']:
                fieldMapping = { 'gpr_block' : 'gpr_block',
                                'gpr_column' : 'gpr_column',
                                'gpr_row' : 'gpr_row',
                                'gpr_name' : 'gpr_name',
                                'gpr_id' : 'gpr_id' ,
                                'gpr_dye1foregroundmean' : 'gpr_f635 median',
                                'gpr_dye1backgroundmean' : 'gpr_b635 median',
                                'gpr_dye2foregroundmean' : 'gpr_f532 median',
                                'gpr_dye2backgroundmean' : 'gpr_b532 median',
                                'gpr_logratio' : 'gpr_log ratio',
                                'gpr_flags' : 'gpr_flags',
                                'gpr_autoflag' : 'EMPTY'}
                #print "using mapping :"
                #print fieldMapping
            else:
                self.obState.update({'NEW' : 0 , 'ERROR' : 1 , 'MESSAGE' : "Error - do not know how to map fields from GPR type " + parser.headerDict['gpr_type']})
                raise brdfException, self.obState['MESSAGE']


                    
            

            # commit the dataSource and study obs
            #self.dataSource.insertDatabase(connection)
            #self.geneExpressionStudy.insertDatabase(connection)

            # insert the column headings and miameFact
            self.obState.update({'DB_PENDING' : 1, 'MESSAGE' : "about to insert miame fact data"})

            # insert the column headings
            sql="""insert into miamefact(microarraystudy,factnamespace,attributename,attributevalue) 
                    values(%(geneexpressionstudy)s,%(factnamespace)s,%(attributename)s,%(attributevalue)s)"""
            insertFields={
                'geneexpressionstudy' : self.geneExpressionStudy.databaseFields['obid'],
                'factnamespace' : 'GPRColumnHeadings',
                'attributename' : 'GPRColumnHeadings',
                'attributevalue' : string.join(parser.columnHeadings,'\t')}
            #print 'executing' + sql%insertFields
            insertCursor = connection.cursor()
            insertCursor.execute(sql,insertFields)
            connection.commit()
            insertCursor.close()            


            # see whether we have an ontology in the database called GENEPIX_GPR_FIELDS
            # containing mappings of GPR names to user-friendlynames
            sql = """
            select
               lower(otf.termname),
               otf2.attributeValue
            from
               (ontologyob o join ontologytermfact otf on
               o.xreflsid = 'ontology.GENEPIX_GPR_FIELDS' and
               otf.ontologyob = o.obid) join
               ontologytermfact2 otf2 on otf2.ontologytermid = otf.obid
            where
                otf2.factnamespace = 'DISPLAY' and
                otf2.attributeName = 'DISPLAYNAME'
            """
            # load above into dictionary and in the code below, use the
            # mapped name
            # !!!!!!!!!!!!!!!!!!! above TO DO at 30/6/2006 !!!!!!!!!!!!!!!!!!!!!!!!!!!

            
            
            for gprKey in parser.headerDict.keys():
                sql="""insert into miamefact(microarraystudy,factnamespace,attributename,attributevalue) 
                    values(%(geneexpressionstudy)s,%(factnamespace)s,%(attributename)s,%(attributevalue)s)"""
                insertFields={
                    'geneexpressionstudy' : self.geneExpressionStudy.databaseFields['obid'],
                    'factnamespace' : 'GPRHeader',
                    'attributename' : gprKey,
                    'attributevalue' : parser.headerDict[gprKey]}
                #print 'executing' + sql%insertFields
                insertCursor = connection.cursor()
                insertCursor.execute(sql,insertFields)
                connection.commit()
                insertCursor.close()

            if miameDict != None:
                for miameKey in miameDict.keys():
                    sql="""insert into miamefact(microarraystudy,factnamespace,attributename,attributevalue) 
                        values(%(geneexpressionstudy)s,%(factnamespace)s,%(attributename)s,%(attributevalue)s)"""
                    insertFields={
                        'geneexpressionstudy' : self.geneExpressionStudy.databaseFields['obid'],
                        'factnamespace' : 'Other',
                        'attributename' : miameKey,
                        'attributevalue' : miameDict[miameKey]}
                    #print 'executing' + sql%insertFields
                    insertCursor = connection.cursor()
                    insertCursor.execute(sql,insertFields)
                    connection.commit()
                    insertCursor.close()                
                

            # insert the microarray raw data observations
            # example : 
            # insert the microarrayRawDataFacts - example :
            #"Block"	"Column"	"Row"	"Name"	"ID"	"X"	"Y"	"Dia."	"F635 Median"	"F635 Mean"	"F635 SD"	"F635 CV"	"B635"	"B635 Median"	"B635 Mean"	"B635 SD"	"B635 CV"	"% > B635+1SD"	"% > B635+2SD"	"F635 % Sat."	"F532 Median"	"F532 Mean"	"F532 SD"	"F532 CV"	"B532"	"B532 Median"	"B532 Mean"	"B532 SD"	"B532 CV"	"% > B532+1SD"	"% > B532+2SD"	"F532 % Sat."	"Ratio of Medians (635/532)"	"Ratio of Means (635/532)"	"Median of Ratios (635/532)"	"Mean of Ratios (635/532)"	"Ratios SD (635/532)"	"Rgn Ratio (635/532)"	"Rgn R2 (635/532)"	"F Pixels"	"B Pixels"	"Circularity"	"Sum of Medians (635/532)"	"Sum of Means (635/532)"	"Log Ratio (635/532)"	"F635 Median - B635"	"F532 Median - B532"	"F635 Mean - B635"	"F532 Mean - B532"	"F635 Total Intensity"	"F532 Total Intensity"	"SNR 635"	"SNR 532"	"Flags"	"Normalize"	"Autoflag"
            #    1	1	1	""	""	670	13170	130	163	171	45	26	111	111	113	31	27	70	41	0	2116	2136	438	20	123	123	129	47	36	99	99	0	0.026	0.030	0.028	0.025	2.412	0.026	0.323	120	750	100	2045	2073	-5.260	52	1993	60	2013	20480	256343	1.871	42.702	0	0	0
            #    1	2	1	""	""	860	13170	130	185	184	45	24	114	114	508	4392	864	0	0	0	2157	2190	402	18	129	129	1327	7568	570	0	0	0	0.035	0.034	0.037	0.031	2.338	0.032	0.428	120	637	100	2099	2131	-4.836	71	2028	70	2061	22029	262764	-0.074	0.114	0	0	0
            #    1	3	1	""	""	1040	13160	120	124	131	35	26	114	114	546	4589	840	0	0	0	420	423	125	29	138	138	1472	7900	536	0	0	0	0.035	0.060	0.096	0.094	3.386	0.481	0.515	120	583	100	292	302	-4.818	10	282	17	285	15748	50798	-0.090	-0.133	0	0	0
            #self.obState.update({'DB_PENDING' : 1, 'MESSAGE' : "done miameFacts about to do microarray spot facts"})

            allFields = parser.nextRecord()
            insertCount = 0
            while parser.parserState["EOF"] == 0:

                # set up the data for the insert
                insertFields={
                    'labresourceob' : self.geneExpressionStudy.databaseFields['labresourceob'],
                    'geneexpressionstudy' : self.geneExpressionStudy.databaseFields['obid'],
                    'gpr_block' : allFields[fieldMapping['gpr_block']],
                    'gpr_column' : allFields[fieldMapping['gpr_column']],
                    'gpr_row' : allFields[fieldMapping['gpr_row']],
                    'gpr_name' : allFields[fieldMapping['gpr_name']],
                    'gpr_id' : allFields[fieldMapping['gpr_id']],
                    'gpr_dye1foregroundmean' : allFields[fieldMapping['gpr_dye1foregroundmean']],
                    'gpr_dye1backgroundmean' : allFields[fieldMapping['gpr_dye1backgroundmean']],
                    'gpr_dye2foregroundmean' : allFields[fieldMapping['gpr_dye2foregroundmean']],
                    'gpr_dye2backgroundmean' : allFields[fieldMapping['gpr_dye2backgroundmean']],
                    'gpr_logratio' : allFields[fieldMapping['gpr_logratio']],
                    'gpr_flags' : allFields[fieldMapping['gpr_flags']],
                    'gpr_autoflag' : eval({ True : "allFields[fieldMapping['gpr_autoflag']]" , False : "None" }['gpr_autoflag' in fieldMapping]),
                    'rawdatarecord' : parser.rawRecord }                

                # obtain the spot id
                sql = "select obid , xreflsid from microarrayspotfact \
                where labresourceob = %(labresourceob)s and \
                gal_block = %(gpr_block)s and \
                gal_column = %(gpr_column)s and \
                gal_row = %(gpr_row)s"
                self.obState.update({'MESSAGE' : "Getting spotid using " + sql%insertFields})
                spotCursor = connection.cursor()
                spotCursor.execute(sql%insertFields)
                spotsFound = spotCursor.fetchall()
                if spotCursor.rowcount != 1:
                    self.obState.update({'ERROR' : 1 , 'MESSAGE' : "Error - could not get a single spot using " + sql%insertFields})
                    raise brdfException, self.obState['MESSAGE']
                insertFields['microarrayspotfact'] = spotsFound[0][0]
                insertFields['xreflsid'] = "%s.%s"%(self.geneExpressionStudy.databaseFields['xreflsid'],
                                                    spotsFound[0][1])
                spotCursor.close()                
                
                
                
                sql = "insert into microarrayobservation(microarraystudy,microarrayspotfact,gpr_block,gpr_column,gpr_row,gpr_name,\
                gpr_id,gpr_dye1foregroundmean,gpr_dye1backgroundmean,gpr_dye2foregroundmean,gpr_dye2backgroundmean, \
                gpr_logratio,gpr_flags,gpr_autoflag,rawdatarecord,xreflsid) values ( \
                %(geneexpressionstudy)s,%(microarrayspotfact)s,%(gpr_block)s,%(gpr_column)s,%(gpr_row)s,%(gpr_name)s,\
                %(gpr_id)s,%(gpr_dye1foregroundmean)s,%(gpr_dye1backgroundmean)s,%(gpr_dye2foregroundmean)s,%(gpr_dye2backgroundmean)s, \
                %(gpr_logratio)s,%(gpr_flags)s,%(gpr_autoflag)s,%(rawdatarecord)s,%(xreflsid)s)"            


                    
                                            
                if insertCount%100 == 1:
                    print 'record %s , executing %s '%(insertCount,sql%insertFields)
                insertCursor = connection.cursor()
                insertCursor.execute(sql,insertFields)
                connection.commit()
                insertCursor.close()
                insertCount += 1

                allFields = parser.nextRecord()



        elif self.dataSource.databaseFields['datasourcetype'] == 'AgResearchArrayExport1':
            #SPOTRESULTID,SPOTID,EXPERIMENTID,SLIDE_BLOCK,SLIDE_COL,SLIDE_ROW,SPOTNAME,X,Y,DIA,F1MEDIAN,F1MEAN,
            #F1SD,B1MEDIAN,B1MEAN,B1SD,B1_PCT_GT_1SD,B1_PCT_GT_2SD,F1_PCT_SAT,F2MEDIAN,F2MEAN,F2SD,B2MEDIAN,
            #B2MEAN,B2SD,B2_PCT_GT_1SD,B2_PCT_GT_2SD,F2_PCT_SAT,RATIO_OF_MEDIANS,RATIO_OF_MEANS,MEDIAN_OF_RATIOS,
            #MEAN_OF_RATIOS,RATIOS_SD,RGN_RATIO,RGN_R_SQUARED,F_PIXELS,B_PIXELS,SUM_OF_MEDIANS,SUM_OF_MEANS,
            #LOG_RATIO,F1_MEDIAN_MINUS_B1,F2_MEDIAN_MINUS_B2,F1_MEAN_MINUS_B1,F2_MEAN_MINUS_B2,FLAGS,SPOTGPRID,
            #MISSINGVALUES,NORMALISE,F1TOTALINTENSITY,F2TOTALINTENSITY,SNR1,SNR2,F1CV,B1,B1CV,F2CV,B2,B2CV,CIRCULARITY,
            #AUTOFLAG,SCRATCH1
            
            #18691060,885812,2134,21,21,23,"ky01PArr54g10",4530,38790,50,9247,9124,2697,4157,4887,2431,79,50,0,2651,2678,594,1948,1996,366,70,41,0,7.24,6.804,6.975,7.028,3.645,13.809,0.096,24,63,5793,5697,2.856,5090,703,4967,730,0,"ky01PArr54g10","",0,218964,64275,1.743,1.863,29,4157,49,22,1948,18,52,0
            #18691061,885788,2134,21,22,23,"kx37ILrr54a02",4700,38790,50,9758,10418,4434,3317,3426,831,100,94,0,2974,3087,567,1930,1929,365,84,78,0,6.17,6.137,6.335,5.711,2.666,10.872,0.299,19,74,7485,8258,2.625,6441,1044,7101,1157,0,"kx37ILrr54a02","",0,197946,58648,8.414,3.173,42,3317,24,18,1930,18,64,0
            #18691062,885764,2134,21,23,23,"kx37ILrr54a06",4850,38780,60,7489,8444,3032,3416,3509,806,100,91,0,3396,3398,785,1879,1933,434,94,82,0,2.685,3.31,3.531,3.212,2.56,5.733,0.305,34,150,5590,6547,1.425,4073,1517,5028,1519,0,"kx37ILrr54a06","",0,287096,115532,6.123,3.376,35,3416,22,23,1879,22,67,01

            # set up mappings from external database
            fieldMapping = { 'gpr_block' : 'slide_block',
                             'gpr_column' : 'slide_col',
                                'gpr_row' : 'slide_row',
                                'gpr_name' : 'spotname',
                                'gpr_id' : 'spotid' ,
                                'gpr_dye1foregroundmean' : 'f1median',
                                'gpr_dye1backgroundmean' : 'b1median',
                                'gpr_dye2foregroundmean' : 'f2median',
                                'gpr_dye2backgroundmean' : 'b2median',
                                'gpr_logratio' : 'log_ratio',
                                'gpr_flags' : 'flags',
                                'gpr_autoflag' : 'autoflag'}


            # "","names","affs427.9.2197PI.181005.CEL","affs427.9.2197PI.181005.CEL.1"
            # This is : probename,probesetname,mismatch,perfectmatch
            #"AFFX-BioB-3_at1","AFFX-BioB-3_at",100,142
            #"AFFX-BioB-3_at2","AFFX-BioB-3_at",94,253
            #"AFFX-BioB-3_at3","AFFX-BioB-3_at",372,519
            #"AFFX-BioB-3_at4","AFFX-BioB-3_at",310,268
            #"AFFX-BioB-3_at5","AFFX-BioB-3_at",72,89
            #"AFFX-BioB-3_at6","AFFX-BioB-3_at",60,109
            fieldNames = ["SPOTRESULTID","SPOTID","EXPERIMENTID","SLIDE_BLOCK","SLIDE_COL","SLIDE_ROW","SPOTNAME","X","Y","DIA","F1MEDIAN","F1MEAN",
                          "F1SD","B1MEDIAN","B1MEAN","B1SD","B1_PCT_GT_1SD","B1_PCT_GT_2SD","F1_PCT_SAT","F2MEDIAN","F2MEAN","F2SD","B2MEDIAN",
                          "B2MEAN","B2SD","B2_PCT_GT_1SD","B2_PCT_GT_2SD","F2_PCT_SAT","RATIO_OF_MEDIANS","RATIO_OF_MEANS","MEDIAN_OF_RATIOS",
                          "MEAN_OF_RATIOS","RATIOS_SD","RGN_RATIO","RGN_R_SQUARED","F_PIXELS","B_PIXELS","SUM_OF_MEDIANS","SUM_OF_MEANS",
                          "LOG_RATIO","F1_MEDIAN_MINUS_B1","F2_MEDIAN_MINUS_B2","F1_MEAN_MINUS_B1","F2_MEAN_MINUS_B2","FLAGS","SPOTGPRID",
                          "MISSINGVALUES","NORMALISE","F1TOTALINTENSITY","F2TOTALINTENSITY","SNR1","SNR2","F1CV","B1","B1CV","F2CV","B2","B2CV",
                          "CIRCULARITY","AUTOFLAG","SCRATCH1"]
            fieldNames = [item.lower() for item in fieldNames]
            reader = csv.reader(open(self.dataSource.databaseFields['physicalsourceuri']))
                    
            # insert the microarray raw data observations. For the affy arrays"," all of the
            # probesets are accumulated in an array and stored in the rawDataRecord field,
            # and just the averages and standard deviations are stored in the main table. This code
            # assumes the data is sorted into probeset groups

            # get all the spots
            sql = """
            select
                msf.gal_block||'.'||msf.gal_column || '.' || msf.gal_row as "spotkey",
                msf.xreflsid,
                msf.obid
            from
                microarrayspotfact msf join labresourceob lr on
                lr.xreflsid = '%s' and
                msf.labresourceob = lr.obid                
            """%(arraylsid)

            print "executing %s"%sql
            spotCursor = connection.cursor()
            spotCursor.execute(sql)

            # make a dictionary of seqs for lookup - key is upper case xreflsid, value is a tuple of (xreflsid,obid)
            spotDict = dict( [(row[0], (row[1],row[2])) for row in  spotCursor.fetchall()])

            print "retrieved %s spots"%len(spotDict)

            # insert the column headings
            sql="""insert into miamefact(microarraystudy,factnamespace,attributename,attributevalue) 
                    values(%(geneexpressionstudy)s,%(factnamespace)s,%(attributename)s,%(attributevalue)s)"""
            insertFields={
                'geneexpressionstudy' : self.geneExpressionStudy.databaseFields['obid'],
                'factnamespace' : 'GPRColumnHeadings',
                'attributename' : 'GPRColumnHeadings',
                'attributevalue' : string.join(fieldNames,'\t')}
            #print 'executing' + sql%insertFields
            insertCursor = connection.cursor()
            insertCursor.execute(sql,insertFields)
            connection.commit()
            insertCursor.close()            
            
            
            
            insertCount = 0
            rowCount = 0
            for row in reader:
                rowCount += 1
                if rowCount%1000 == 1:
                    print "processing %s"%row

                if rowCount == 1:
                    row = [item.lower() for item in row]
                    if row != fieldNames:
                        raise brdfException("error - field headings \n%s do not match format \n%s"%(str(row),str(fieldNames)))
                    continue

                fieldDict = dict(zip(fieldNames,row))

                # checks
                if miameDict['experimentid'] != int(fieldDict['experimentid']):
                    raise brdfException("error - data file has experimentid %s but import is for experimentid %s"%(fieldDict['experimentid'], miameDict['experimentid']))
                    

                spotkey = "%(slide_block)s.%(slide_col)s.%(slide_row)s"%fieldDict
                if spotkey not in spotDict:
                    raise brdfException("** import error could not find spot key %s"%spotkey)
                sql = """
                    insert into microarrayobservation(
                  microarraystudy,
                  microarrayspotfact,
                  gpr_block,
                  gpr_column,
                  gpr_row,
                  gpr_name,
                  gpr_id,
                  gpr_dye1foregroundmean,
                  gpr_dye1backgroundmean,
                  gpr_dye2foregroundmean,
                  gpr_dye2backgroundmean, 
                  gpr_logratio,gpr_flags,
                  gpr_autoflag,
                  rawdatarecord,
                  xreflsid)
                  values ( 
                    %(geneexpressionstudy)s,
                    %(microarrayspotfact)s,
                    %(gpr_block)s,
                    %(gpr_column)s,
                    %(gpr_row)s,
                    %(gpr_name)s,
                    %(gpr_id)s,
                    %(gpr_dye1foregroundmean)s,
                    %(gpr_dye1backgroundmean)s,
                    %(gpr_dye2foregroundmean)s,
                    %(gpr_dye2backgroundmean)s, 
                    %(gpr_logratio)s,
                    %(gpr_flags)s,
                    %(gpr_autoflag)s,
                    %(rawdatarecord)s,
                    %(xreflsid)s)"""       
                insertFields={
                    'xreflsid' : "%s.%s"%(self.geneExpressionStudy.databaseFields['xreflsid'],spotDict[spotkey][0]),
                    'geneexpressionstudy' : self.geneExpressionStudy.databaseFields['obid'],
                    'microarrayspotfact'  : spotDict[spotkey][1],
                    'gpr_block' : fieldDict[fieldMapping['gpr_block']],
                    'gpr_column' : fieldDict[fieldMapping['gpr_column']],
                    'gpr_row' : fieldDict[fieldMapping['gpr_row']],
                    'gpr_name' : fieldDict[fieldMapping['gpr_name']],
                    'gpr_id' : fieldDict[fieldMapping['gpr_id']],
                    'gpr_dye1foregroundmean' : fieldDict[fieldMapping['gpr_dye1foregroundmean']],
                    'gpr_dye1backgroundmean' : fieldDict[fieldMapping['gpr_dye1backgroundmean']],
                    'gpr_dye2foregroundmean' : fieldDict[fieldMapping['gpr_dye2foregroundmean']],
                    'gpr_dye2backgroundmean' : fieldDict[fieldMapping['gpr_dye2backgroundmean']],
                    'gpr_logratio' : eval({ True : 'None' , False : fieldDict[fieldMapping['gpr_logratio']] }[len(fieldDict[fieldMapping['gpr_logratio']]) == 0]),
                    'gpr_flags' : fieldDict[fieldMapping['gpr_flags']],
                    'gpr_autoflag' : eval({ True : 'None' , False : fieldDict[fieldMapping['gpr_autoflag']] }[len(fieldDict[fieldMapping['gpr_autoflag']]) == 0]),
                    'rawdatarecord' : string.join([fieldDict[key] for key in fieldNames],'\t')                 
                }
                if rowCount%100 == 1:
                    print "executing %s"%str(sql%insertFields)
                spotCursor.execute(sql,insertFields)
                connection.commit()
                insertCount += 1


                """
                this query can be used to check the accessions on array and import match
                select
                   msf.accession ,
                   split_part(mo.rawdatarecord,'\t',4) as "imported"
                from
                   microarrayspotfact msf join microarrayobservation mo
                on
                   msf.obid = mo.microarrayspotfact
                """
                                    

        self.insertDatabase(connection)                
            
        self.obState.update({'DB_PENDING' : 0, 'MESSAGE' : "Experiment import complete , inserted " + str(insertCount) + " records"})
            


        
class dataSourceOb (ob ):
    """ dataSourceOb"""
    def __init__(self):
        ob.__init__(self)
        self.relatedAnalysisFunctions = None

    def initFromDatabase(self, identifier, connection):  
        """ method for initialising an object from database - arg can be an integer obid, or a string importProcedureName"""
          
        # initialise base fields from ob table
        ob.initFromDatabase(self, identifier,"dataSourceOb",connection)

        # now get the complete object
        self.databaseFields = getObjectRecord(connection, "dataSourceOb", self.databaseFields['obid'])
        self.obState.update({'ERROR' : 0 , 'NEW' : 0, 'MESSAGE' : "initialised from database OK"})                     
        
    def initNew(self,connection,datasourcetype='Other',physicalsourceuri=''):
        """ method to initialise a new labResourceModule object """
        self.databaseFields = {
            'xreflsid' : physicalsourceuri,
            'obid' : getNewObid(connection),
            'datasourcetype' : datasourcetype, 
            'physicalsourceuri' : physicalsourceuri,
            'numberoffiles' : None,
            'createdby' : None,
            'obkeywords' : None,
            'datasourcename' : None,
            'datasupplier' : None,
            'datasupplieddate' : None,
            'datasourcecomment' : None,
            'datasourcecontent' : None,
            'dynamiccontentmethod' : None,
            'uploadsourceuri' : None
            } 
        self.obState.update({'DB_PENDING' : 1})

    def insertDatabase(self,connection):
        """ method used by dataSource object to save itself to database  """
        sql = """
           insert into dataSourceOb(
           obid,xreflsid,createdby,
           obkeywords,datasourcename,datasourcetype,
           datasupplier,physicalsourceuri,datasupplieddate,
           datasourcecomment,numberoffiles, datasourcecontent, dynamiccontentmethod,uploadSourceURI)
           values(
           %(obid)s,%(xreflsid)s,%(createdby)s,
           %(obkeywords)s,%(datasourcename)s,%(datasourcetype)s,
           %(datasupplier)s,%(physicalsourceuri)s,%(datasupplieddate)s,
           %(datasourcecomment)s,%(numberoffiles)s,%(datasourcecontent)s,%(dynamiccontentmethod)s,%(uploadsourceuri)s)
           """
        
        #sql = """
        #   insert into dataSourceOb(obid,datasourcetype,physicalsourceuri,xreflsid,numberoffiles)
        #   values (%(obid)s,%(datasourcetype)s,%(physicalsourceuri)s,%(xreflsid)s,%(numberoffiles)s)
        #   """
        importmodulelogger.info("executing " + sql%self.databaseFields)
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
                    'editURL' : self.editURL%self.databaseFields,
                    'linkAnalysisProcedureURL' : self.linkAnalysisProcedureURL%self.databaseFields}
        
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
        
        function toolsButton(anchor) {
            hideMenu();
            window.open("%(linkAnalysisProcedureURL)s"+anchor);
        }


        var editItemArray = new Array();
        editItemArray[0] = new Array("editButton(\"\");","Edit / Create Data Source");

        var annotateItemArray = new Array();
        annotateItemArray[0] = new Array("annotateButton(\"%(addCommentURL)s\");","Add Comment");
        annotateItemArray[1] = new Array("annotateButton(\"%(addLinkURL)s\");","Add Hyperlink");

        var toolsItemArray = new Array();
        toolsItemArray[0] = new Array("toolsButton(\"\");","Add an analysis to this data");

        var viewItemArray = new Array();
        //viewItemArray[0] = new Array("unimplemented(\"view this sequence as FASTA\");","as FASTA");
        //viewItemArray[1] = new Array("unimplemented(\"view this sequence as Genbank\");","as Genbank");

        var helpItemArray = new Array();
        helpItemArray[0] = new Array("helpButton();","Help");
        """%menuDict

        return defaultMenuJS%dynamicMenuJS

    


        

    # this initialiases a list of all analysis instances related to this data source - this is
    # distinct from the list of analyses "attached manually" to this object.
    def initRelatedAnalysisFunctions(self,connection):
        sql = """
        select
            af.invocation,
            af.functioncomment,
            ap.xreflsid,
            ap.procedurename,
            ap.proceduretype,
            af.datasourcelist,
            af.voptypeid,
            ap.proceduredescription,
            af.invocationorder,
            af.obid
        from
            (datasourcelistmembershiplink dll join analysisfunction af on
            dll.datasourceob = %(obid)s and af.datasourcelist = dll.datasourcelist) join
            analysisprocedureob ap on af.analysisprocedureob = ap.obid
        order by
            ap.proceduredescription,
            af.invocationorder
        """
     
        importmodulelogger.info('executing SQL to retrieve default dynamic analysis functions : %s'%str(sql%self.databaseFields))
        importmodulelogger.info("(attached analysis functions : %s)"%str(self.relatedAnalysisFunctions))                
        analysisCursor = connection.cursor()
        analysisCursor.execute(sql,self.databaseFields)
        self.relatedAnalysisFunctions = analysisCursor.fetchall()

                
        #self.relatedAnalysisFunctions = analysisCursor.fetchall()
        self.obState.update({'RELATED_DYNAMIC_ANALYSES' : analysisCursor.rowcount , 'MESSAGE' : "related dynamic analyses initialised from database OK"})
        analysisCursor.close()

        if self.relatedAnalysisFunctions == None:
            self.relatedAnalysisFunctions = []
            

        importmodulelogger.info("Default analysis functions : %s"%str(self.relatedAnalysisFunctions))        
            
        

    # this overrides the base class method and supports running all related analyses as obtained above , as well as the directly linked analyses- see "runAnalysisFunctions" in
    # obmodule
    def runAnalysisFunctions(self,connection,context="default",procedureList = None, functionList = None, runVirtual = True, runNonVirtual = True,\
                             dynamicDataSources=None):
        """ This method allows a call to be made to this object to get it to run
        either all instances of a given list of analysis procedures, or all specific
        analysisProcedure instances - i.e. all analysis functions of a given type that are attached.
        """
        from analysisModule import runProcedure
        result = ''
        importmodulelogger.info("runAnalysisFunctions : obstate = %s"%str(self.obState))
        if self.obState['DYNAMIC_ANALYSES'] > 0:
            importmodulelogger.info('running non virtual analysis functions , procedures = %s, functions=%s'%(str(procedureList),str(functionList)))
            for analysisFunctionInstance in self.analysisFunctions:

                # (note that the name "analysisFunctionInstance" is usually referenced in the procedure call that is evaluated)
                importmodulelogger.info("checking %s"%analysisFunctionInstance)
                runit = False
                if procedureList != None:
                    if analysisFunctionInstance[2] in procedureList or str(analysisFunctionInstance[2]) in procedureList:
                        runit = True
                if functionList != None:
                    if analysisFunctionInstance[9] in functionList or str(analysisFunctionInstance[9]) in functionList:
                        runit = True

                if runit:
                    importmodulelogger.info("running %s"%analysisFunctionInstance)
                    myResult = eval(analysisFunctionInstance[0])
                    result += myResult
                    
        if self.obState['RELATED_DYNAMIC_ANALYSES'] > 0:
            importmodulelogger.info('running non virtual analysis functions , procedures = %s, functions=%s'%(str(procedureList),str(functionList)))
            for analysisFunctionInstance in self.relatedAnalysisFunctions:

                # (note that the name "analysisFunctionInstance" is usually referenced in the procedure call that is evaluated)
                importmodulelogger.info("checking %s"%analysisFunctionInstance)
                runit = False
                if procedureList != None:
                    if analysisFunctionInstance[2] in procedureList or str(analysisFunctionInstance[2]) in procedureList:
                        runit = True
                if functionList != None:
                    if analysisFunctionInstance[9] in functionList or str(analysisFunctionInstance[9]) in functionList:
                        runit = True

                if runit:
                    importmodulelogger.info("running %s"%analysisFunctionInstance)
                    myResult = eval(analysisFunctionInstance[0])
                    result += myResult

        return result        


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
        if self.databaseFields['datasourcetype'] in ['SQL','Python data'] :
            nonSystemFieldRows =  reduce(lambda x,y:x+y, ['<tr><td class=fieldname>'+self.getColumnAlias(key)+'</td><td class=fieldvalue>'+tidyout(str(value), 80, 1,'<br/>')[0]+'</td></tr>\n' \
                                                   for key,value in FieldItems if not key in ( \
                                        'obid','obtypeid','createddate','createdby','lastupdateddate',\
                                        'lastupdatedby','checkedout','checkedoutby','checkoutdate','obkeywords','statuscode','datasourcecontent') and self.getColumnAlias(key) != None])
        
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

        # build a select list of instances of this procedure that can be run
        allAnalysisFunctions = []
        if self.obState['DYNAMIC_ANALYSES'] > 0:
            allAnalysisFunctions = eval ({
                (True,True) : 'None',
                (True,False) : 'self.relatedAnalysisFunctions',
                (False, True) : 'self.analysisFunctions',
                (False, False) : 'self.analysisFunctions + self.relatedAnalysisFunctions'
                }[( self.analysisFunctions == None), (self.relatedAnalysisFunctions == None)])

        #allAnalysisFunctions = eval ({
        #    (True,True) : 'None',
        #    (True,False) : 'self.relatedAnalysisFunctions',
        #    (False, True) : 'self.analysisFunctions',
        #    (False, False) : 'self.analysisFunctions + self.relatedAnalysisFunctions'
        #    }[( self.analysisFunctions == None), (self.relatedAnalysisFunctions == None)])
        
        if len(allAnalysisFunctions) > 0:
            #selectlisttuples = ["<option value=%s> %s : %s </option>"%(item[9], item[3], item[1]) for item in allAnalysisFunctions ]
            selectlisttuples = ["<option value=%s selected> %s : %s </option>"%(item[9], item[3], item[1]) for item in [allAnalysisFunctions[0]] ]
            if len(allAnalysisFunctions) > 1:
                selectlisttuples = ["<option value=%s> %s : %s </option>"%(item[9], item[3], item[1]) for item in allAnalysisFunctions[1:] ]
            
            selectlisthtml = """
            <tr>
            <td colspan=2 align=left>
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
                """%"Run selected analyses on this data"                    
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
            importmodulelogger.info('running non-virtual display functions')
            for displayFunction in self.displayFunctions:
                # exclude virtual functions - these will be instantiated in specific contexts or subclasses
                if displayFunction[7] == None:
                    importmodulelogger.info('running %s'%displayFunction[0])
                    myGraphHTML = eval(displayFunction[0])
                    table += myGraphHTML        
        
        importmodulelogger.info('listing dictionaries')
        # if we have formatted dictionaries , output these first , they are usually the most interesting
        # content of the object
        if len(ListDictionaryRows) >  0:
            table += ListDictionaryRows

        importmodulelogger.info('listing fields')
        # next the field rows
        table += nonSystemFieldRows

        importmodulelogger.info('listing lists')
        # next the other lists
        if len(ListOtherRows) > 0:
            table += ListOtherRows

        return table


    def upload(self):
        """ this is usually called from a web form handler, to upload a file. The handler should
        have stored instanceData["uploadsourceuri"]  = (filename, fieldstorage object)"""

        if 'instanceData' not in dir(self):
            raise brdfException("in dataSourceOb.upload : missing instanceData")

        if 'uploadsourceuri' not in self.instanceData:
            raise brdfException("in dataSourceOb.upload : missing uploadsourceuri")

        if self.instanceData['uploadsourceuri'][0] != self.databaseFields['uploadsourceuri']:
            raise brdfException("uploadsourceuri in database (%s) not the same as in instanceData (%s)"%(databaseFields["uploadsourceuri"],instanceData["uploadsourceuri"]))

        try :
            storageRoot = self.formSettings['Handler Bindings']['Upload Root']
        except:
            importmodulelogger.info("warning - failed getting formSettings['Handler Bindings']['Upload Root']")
            storageRoot = ''

        # standardise the path separators
        Uuploadsourceuri = re.sub("\\\\","/",self.databaseFields['uploadsourceuri'])
        Uphysicalsourceuri  = re.sub("\\\\","/",self.databaseFields['physicalsourceuri'])

        # the complete storage path is currently assumed to be root + physicalsourceuri + basename  - but we check
        # physicalsourceuri does not already contain the basename
        storagePath = Uphysicalsourceuri

        storageBase = os.path.basename( Uuploadsourceuri )  # for example would be myfile.zip
        importmodulelogger.info("storage base = %s"%storageBase)
        if storageBase == os.path.basename(storagePath):
            storageFileName = os.path.join(storageRoot, storagePath)
        else:
            storageFileName = os.path.join(storageRoot, storagePath, storageBase)


        # if the path does not exist, create it. This does not handle all cases - e.g. if the new
        # path would require creation of a second folder inside the first. Can add this if required
        if not os.path.isdir(os.path.dirname(storageFileName)):
            os.mkdir( os.path.dirname(storageFileName) )

        if os.path.isfile(storageFileName):
            raise brdfException("error in file upload : %s already exists"%storageFileName)

        importmodulelogger.info("uploading %(uploadsourceuri)s"%self.databaseFields)
        importmodulelogger.info("storing as %s"%storageFileName)

        self.databaseFields.update( {
            "physicalsourceuri" : storageFileName
        })
        con = getConnection()
        mycur = con.cursor()
        sql = """
        update datasourceob
        set physicalsourceuri = %(physicalsourceuri)s
        where obid = %(obid)s
        """
        mycur.execute(sql,self.databaseFields)

        mywriter = file(storageFileName, 'wb')
        myreader = self.instanceData["uploadsourceuri"][1].file

        inbytes = myreader.read(10000)

        byteCount = 0

        while len(inbytes) > 0:
            mywriter.write(inbytes)
            byteCount += len(inbytes)
            inbytes = myreader.read(10000)

        mywriter.close()
        importmodulelogger.info("uploaded %d bytes"%byteCount)
        importmodulelogger.info("upload done code = %s"%self.instanceData["uploadsourceuri"][1].done)

        makeComment(con,self,"""
        file was uploaded to : %s
        bytes uploaded : %s 
        upload result code (0=OK ) : %s
        """%(storageFileName,byteCount,self.instanceData["uploadsourceuri"][1].done))

        makeURL(con,self,"%s?context=download&obid=%s&target=ob"%(self.fetcher,self.databaseFields["obid"]),"Download %s"%os.path.basename(storageFileName))

        con.close()
        

#    while 1:
#        line = fileitem.file.readline()
#        if not line: break
#        linecount = linecount + 1
#        output.write(self.databaseFields["xreflsid"])
#        #Find out filesize
#       output.flush()
#       fileSize = output.tell()
#       output.close()



    def execute(self, connection, format="html", outfile=sys.stdout, delivery = None, oversizecallback = None, oversizelimit = None):
        """ some datasources such as SQL sources can be executed. This is useful for implementing
        simple single-query reports.
        """

        # some formatting functions
        def getReportHeader(title, heading, fieldNames, outputformat = 'html',includeContentType = True):
            page = ""
            if includeContentType:
                page += "Content-Type: text/html\n\n" + HTMLdoctype
            if outputformat == 'html':
                page += '<html>\n<header>\n<title>\n' + title + '</title>\n' + getStyle() + '</header>\n<body>\n'
                #page += '<table with=90% border="1">\n<tr>\n<td><h2 halign="center">'+heading+'</h2><p>'
                if fieldNames != None:
                    page += '<table style="BORDER-COLLAPSE: collapse" bordercolor="#388FBD" cellpadding="3" border="1">'
                    page += '<tr> <td colspan=%s> %s </td></tr>'%(len(fieldNames) , heading)
                    page += '<tr>' + reduce(lambda x,y: x + '<td><b>' + str(y) + '</b></td>' , fieldNames,'') + '</tr>'
                else:
                    page += '<h2> %s </h2>'%heading
            elif outputformat == 'csv':
                page += heading + "\n"
                page += reduce(lambda x,y: x + '"' + str(y) + '",' , fieldNames,'')
                page = re.sub(',$','',page)
            else:
                page += heading
                
            return page


        #def getDownloadHeader(fileName):
        #    page =\
        #"""Content-Type: text/plain; name="%s"
        #Content-Description: %s
        #Content-Disposition: attachment; filename="%s"
        #"""%(fileName,fileName,fileName)
        #    return page

        def getDownloadHeader(fileName,outputformat="raw"):
             page = "Content-Type: application/x-download\n"
             page += "Content-Disposition: attachment; filename=%s;\n\n"%fileName
             return page


        def OldgetDownloadHeader(fileName,title, heading,fieldNames, outputformat = 'html'):
            page =\
        """Content-Type: text/plain; name="%s"
        Content-Description: %s
        Content-Disposition: attachment; filename="%s"
        """%(fileName,fileName,fileName)
            #page += "Content-Type: text/html\n\n" + htmlModule.HTMLdoctype
            page += "Content-Type: text/html\n\n"

            if outputformat == 'html':
                page += '<html>\n<header>\n<title>\n' + title + '</title>\n' +  getStyle() + ' </header>\n<body>\n'
                ##page += '<table with=90% border="1">\n<tr>\n<td><h2 halign="center">'+heading+'</h2><p>'
                page += '<table with=90% border="1">\n<tr>\n<td><p>'
                page += '<tr> <td colspan=%s> %s </td></tr>'%(len(fieldNames) , heading)
                page += '<tr>' + reduce(lambda x,y: x + '<td><b>' + str(y) + '</b></td>' , fieldNames,'') + '</tr>'
            elif outputformat == 'csv':
                page += heading + "\n"
                page += reduce(lambda x,y: x + '"' + str(y) + '",' , fieldNames,'')
                page = re.sub(',$','',page)

            #page = "Content-Type: application/x-download\n\n"
            #page += "Content-Disposition: attachment; filename=test.dl;\n\n"

            return page


        def getReportFooter(rowCount,message=''):
            page = '<p><p>\n'
            page += '<p></td>\n</tr>\n</table>\n'
            page += '<p/><p/>%s Rows Returned<p/>'%rowCount
            page += '<b>%s</b>'%message    
            page += '</body>\n</html>\n'
            return page
        

        #if self.databaseFields["datasourcetype"] == "Executable":
        if re.search("Executable",self.databaseFields["datasourcetype"]) != None:
            importmodulelogger.info("datasource is executing %s"%self.databaseFields['datasourcecontent'])
            status, output = commands.getstatusoutput(self.databaseFields['datasourcecontent'])
            importmodulelogger.info("Length of output: %s"%len(output))
            importmodulelogger.info("Status: %s"%status)
            if outfile == sys.stdout and format == "html":
                if re.search("Raw Download",self.databaseFields["datasourcetype"]) != None:
                    outfile.write(getDownloadHeader(self.databaseFields["datasourcename"]) + "\n")
                    outfile.write(output)
                else:                
                    outfile.write(getReportHeader(self.databaseFields["xreflsid"],"","", "") + "\n")
                    outfile.write("<pre>%s</pre>"%output)

            elif outfile == sys.stdout:
                outfile.write(output)
                
                
            return (status, output)
        
        elif self.databaseFields["datasourcetype"] == "SQL":

            reportCursor=connection.cursor()

            sql = self.databaseFields["datasourcecontent"]
                
            
            # execute the report query
            reportCursor.execute(sql)
            fieldNames = [item[0] for item in reportCursor.description]

            # now construct heading
            if format == "html":        
                reportHeading = """
                    <h1 align=center>%s</h1>             
                    <h3 align=center> as at %s </h3>"""\
                                %(self.databaseFields["datasourcename"],date.isoformat(date.today()))
            else:
                reportHeading =""


            if delivery == "download":
                reportHeading = getDownloadHeader("%(datasourcename)s"%self.databaseFields)
            
            reportFieldValues = reportCursor.fetchone()
            rowCount = 0


            if delivery == "download":
                outfile.write(getDownloadHeader("%(datasourcename)s"%self.databaseFields))
                outfile.write(getReportHeader(reportHeading,reportHeading,fieldNames, format,includeContentType=False) + "\n")                
            else:
                outfile.write(getReportHeader(reportHeading,reportHeading,fieldNames, format) + "\n")
            while reportFieldValues != None:
                rowCount += 1

                if oversizelimit != None:
                    if rowCount >= oversizelimit:
                        outfile.write(oversizecallback)
                        break
                        
                if format == "html":
                    record = '<tr>'
                    record+=reduce(lambda x,y: x+'<td>'+str(y)+'</td>', reportFieldValues,'')
                    outfile.write(record+'</tr>\n')               
                else:
                    record += reduce(lambda x,y: x+'\t'+str(y), reportFieldValues,'')
                    outfile.write(record+'\n')   
                    
                reportFieldValues = reportCursor.fetchone()

            if format == "html" : 
                outfile.write( getReportFooter(rowCount) + "\n")

            reportCursor.close()
            
        else: # another type that is not executable
            return



    # added support for storing voptypeid
    def addImportFunction(self, target,importprocedure,connection):
        """ method used to link this datasource to an object in the database """
        instanceValues = {
            'obid'  : getNewObid(connection),
            'xreflsid' : "%s.%s.import"%(self.databaseFields['xreflsid'],target.databaseFields['xreflsid']),
            'ob' : target.databaseFields['obid'],
            'datasourceob' : self.databaseFields['obid'],
            'importprocedureob' : importprocedure.databaseFields['obid'],
            'voptypeid' : None
        }

        # 5/2011 set some virtual types where possible - this improves
        # link performance
        if target.__class__.__name__ == "bioSequenceOb":
            instanceValues["voptypeid"] = 127
            

        
        sql = """
        insert into importfunction (obid,xreflsid,datasourceob, importprocedureob, ob, voptypeid)
        values(%(obid)s,%(xreflsid)s,%(datasourceob)s, %(importprocedureob)s, %(ob)s, %(voptypeid)s)
        """
        insertCursor = connection.cursor()
        insertCursor.execute(sql,instanceValues)
        connection.commit()
        insertCursor.close()

    def addFact(self,connection,argfactNameSpace,argattributeName,argattributeValue,checkExisting=True):
        factFields = {
            'datasourceOb' : self.databaseFields['obid'],
            'factNameSpace' : argfactNameSpace,
            'attributeName' : argattributeName,
            'attributeValue' : argattributeValue }

        doinsert = True
        insertCursor = connection.cursor()

        # first check if this fact is already in the db - if it is do not duplicate (if asked to do this)
        if checkExisting:
            sql = """
            select datasourceOb from datasourceFact where
            datasourceOb = %(datasourceOb)s and
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
            insert into datasourceFact(datasourceOb,factNameSpace, attributeName, attributeValue)
            values(%(datasourceOb)s,%(factNameSpace)s,%(attributeName)s,%(attributeValue)s)
            """
            #studymodulelogger.info("executing %s"%(sql%factFields))
            insertCursor.execute(sql,factFields)
            connection.commit()
            insertCursor.close()
            self.obState.update({'NEW' : 0 , 'DB_PENDING' : 0, 'ERROR' : 0, 'MESSAGE' : "database insert OK"})
        else:
            insertCursor.close()




class dataSourceList (op) :
    def __init__(self):
        op.__init__(self)

    def initNew(self,connection,listname='',xreflsid='',obkeywords=''):
        """ method to initialise a new dataSourceList Module object """
        self.databaseFields = \
            { 'listname' : listname, 'obid' : getNewObid(connection) , 'xreflsid' : xreflsid , \
            'obkeywords' : obkeywords 
              }
        self.obState.update({'DB_PENDING' : 1, 'ERROR' : 0})

    def initFromDatabase(self, identifier, connection):
        """ method for initialising dataSourceList from database"""

        # first init base class - this will get obid
        ob.initFromDatabase(self, identifier, "dataSourceList", connection)

        # now get the complete object
        self.databaseFields = getObjectRecord(connection, "dataSourceList", self.databaseFields['obid'])

        # for this object type we need to get the members of the list
        sql = "select dataSourceob from dataSourcelistmembershiplink where dataSourcelist = %s " % self.databaseFields['obid']
        #print "executing " + sql        
        obCursor = connection.cursor()
        obCursor.execute(sql)
        obFieldValues = obCursor.fetchall()
        self.databaseFields.update({'dataSources' : [item[0] for item in obFieldValues]})
        obCursor.close()

        self.obState.update({'ERROR' : 0 , 'NEW' : 0, 'DB_PENDING' : 0, 'MESSAGE' : "initialised from database OK"})              

        

    def insertDatabase(self,connection):
        """ method used by dataSourceList object to save itself to database  """
        sql = "insert into dataSourceList(obid,xreflsid,obkeywords,listname) \
                      values (%(obid)s,%(xreflsid)s,%(obkeywords)s,%(listname)s)"
        insertCursor = connection.cursor()
        insertCursor.execute(sql,self.databaseFields)
        connection.commit()
        insertCursor.close()
        self.obState.update({'NEW' : 0 , 'DB_PENDING' : 0, 'MESSAGE' : "database insert OK"})        

    def adddataSource(self,connection,dataSource,inclusionComment=''):
        """ method for adding a dataSource to an existing dataSourceList """

        #check type
        if dataSource.__class__.__name__ != "dataSourceOb":
            self.obState.update({'ERROR' : 1 , 'MESSAGE' : "adddataSource called with arg type" + dataSource.__class__.__name__ + " - should be dataSourceOb"})
            raise brdfException, self.ObState['MESSAGE']

        # check list is in appropriate state
        if [self.obState[state] for state in ("NEW" , "DB_PENDING", "ERROR")] != [0,0,0]:
            self.obState.update({'MESSAGE' : "dataSourceList state does not permit adding a dataSource"})
            raise brdfException, self.obState['MESSAGE']

        self.obState.update({'DB_PENDING' : 1 , 'MESSAGE' : "adding lab resource"})

        sql = "insert into dataSourceListMembershipLink(dataSourcelist,dataSourceob,inclusionComment) \
                      values (%(dataSourcelist)s,%(dataSourceob)s,%(inclusionComment)s)"

        membershipFields= {\
            'dataSourcelist' : self.databaseFields['obid'] ,
            'dataSourceob' : dataSource.databaseFields['obid'],
            'inclusionComment' : inclusionComment
            }

        #print "executing " + sql%membershipFields
        
        insertCursor = connection.cursor()
        insertCursor.execute(sql,membershipFields)
        connection.commit()
        insertCursor.close()
        self.obState.update({'NEW' : 0 , 'DB_PENDING' : 0, 'MESSAGE' : "datasource  added OK"})



    

# minimal implementation
class dataSourceNamedListMembershipLink (op) :
    def __init__(self):
        op.__init__(self)

    def initFromDatabase(self, identifier, connection):
        """ method for initialising dataSourceNamedListMembershipLink from database"""

        # first init base class - this will get obid
        ob.initFromDatabase(self, identifier, "dataSourceNamedListMembershipLink", connection)

        # now get the complete object
        self.databaseFields = getObjectRecord(connection, "dataSourceNamedListMembershipLink", self.databaseFields['obid'])

        self.obState.update({'ERROR' : 0 , 'NEW' : 0, 'DB_PENDING' : 0, 'MESSAGE' : "initialised from database OK"})

class databaseSearchImportFunction ( op ) :
    """ import a database search study - e.g. a blast search """
    def __init__(self):
        op.__init__(self)

    def initFromDatabase(self, identifier, connection):
        # first init base class - this will get obid
        ob.initFromDatabase(self, identifier, "importFunction", connection)

        # now get the complete object
        self.databaseFields = getObjectRecord(connection, "importFunction", self.databaseFields['obid'])
        
        
        self.obState.update({'ERROR' : 0 , 'NEW' : 0, 'MESSAGE' : "initialised from database OK"})                 
        

    def initNew(self,connection,obtuple):
        argTemplate = [classitem.__name__ for classitem in (dataSourceOb,importProcedureOb,databaseSearchStudy)]
        argsSupplied = [obitem.__class__.__name__ for obitem in obtuple]

        if argTemplate != argsSupplied:
            self.obState.update({'ERROR' : 1 , 'MESSAGE' : "args supplied : " + reduce(lambda x,y:x+" "+ y,argsSupplied) + \
                  " args required : " + reduce(lambda x,y:x+" "+y,argTemplate) })
            raise brdfException, self.obState['MESSAGE']

        #print str(obtuple[2])
        
        self.databaseFields = {
            'obid' : getNewObid(connection) ,
            'xreflsid' : "%s.import"%obtuple[2].databaseFields['xreflsid'],
            'dataSourceOb' : obtuple[0].databaseFields['obid'],         
            'importProcedureOb' : obtuple[1].databaseFields['obid'],    
            'databaseSearchStudy' : obtuple[2].databaseFields['obid'] }

        self.dataSource = obtuple[0]
        self.importProcedure = obtuple[1]
        self.databaseSearchStudy = obtuple[2]

        self.obState.update({'DB_PENDING' : 1})
            
    def insertDatabase(self,connection):
        """ method used by databaseSearchImportFunction to save itself to database  """
        
        sql = "insert into importFunction(obid,dataSourceOb,importProcedureOb,Ob,xreflsid) values (%(obid)s,%(dataSourceOb)s,%(importProcedureOb)s,%(databaseSearchStudy)s,%(xreflsid)s)"
        #print 'executing ' + sql%self.databaseFields
        insertCursor = connection.cursor()
        insertCursor.execute(sql,self.databaseFields)
        connection.commit()
        insertCursor.close()
        self.obState.update({'NEW' : 0 , 'DB_PENDING' : 0, 'MESSAGE' : "database insert OK"})


    def runStudyImport(self, connection, querylsidprefix=None, subjectlsidprefix=None, subjectparseregexp=None, checkExistingHits = False,\
                       createMissingQueries = False, createMissingHits = True, newQuerySequenceType = "GENOMIC DNA SEQUENCE",\
                       newHitSequenceType = "PROTEIN SEQUENCE", queryparseregexp=None, hitimportlimit=0, alignmentimportlimit=0, \
                       limitorderby='evalue_score', hspcountforrepeat = 1000, adjustedevaluecutoff = 1.0e-20, singlehitevaluecutoff = 1.0e-5 , locationMapDetails = None ,\
                       annotateGenomeMapping = False, dataStartsRow = 0, fieldNamesRow = 0, queryTableColumn = "xreflsid", cacheQueryList = True,\
                       cacheHitList = True, fileFormat = "csv"):
        """ this method imports a database search into the database.
        The import instance itself has already been committed to the database

        The dataSource and study objects have already been initialised but
        not yet committed to the database. The importProcedure object already exists in the
        database.
        
        The following steps are involved :

        
        2. The dataSource object has been initialised and is now ommitted to the database

        3. The study object has been initialised and is now committed to the database
        

        
        5. Finally , the importFunction is committed to the database , which records this import
        """

        """
        !!!!!! This section is obviously pretty incomplete !!!!!!
        """
        # we will need the following sign function for a later sort function
	def sign(arg):
            if arg<0.0:
                return -1
	    elif arg ==0.0 :
		return 0
	    elif arg > 0.0:
		return 1
	# this comparison function is used to compare hsps
	def hspcomp(dicta,dictb,method):
            if method == 'evalue_score' : 
                if float(dicta['evalue']) > float(dictb['evalue']):
                    return 1
                elif float(dicta['evalue']) < float(dictb['evalue']):
                    return -1
                elif float(dicta['evalue']) == float(dictb['evalue']):
                    if 'bitscore' in dicta:
                        if float(dicta['bitscore']) >  float(dictb['bitscore']):
                            return 1
                        elif float(dicta['bitscore']) <  float(dictb['bitscore']):
                            return -1
                        else:
                            return 0
                    else:
                        if float(dicta['score']) >  float(dictb['score']):
                            return 1
                        elif float(dicta['score']) <  float(dictb['score']):
                            return -1
                        else:
                            return 0

            else:
                raise brdfException("unsupported comparison function %s"%method)
            
		    
        # check that the regexp tuples are tuples - it is easy for these to be mistakenly passed
        # as strings if given as (e.g.) ('blah') - they need to be passed as (e.g.) ('blah',)
        if subjectparseregexp != None:
            if subjectparseregexp.__class__.__name__ != 'tuple':
                raise brdfException("subject regexp parsers must be passed as a tuple of strings - e.g. ('myregexp',)")
        if queryparseregexp != None:
            if queryparseregexp.__class__.__name__ != 'tuple':
                raise brdfException("query regexp parsers must be passed as a tuple of strings - e.g. ('myregexp',)")                                
                                

            
        importmodulelogger.info("in runstudyImport for blast search with queryparseregexp=%s  subjectparseregexp=%s"%(queryparseregexp,subjectparseregexp)) 
        importmodulelogger.info("using hitimportlimit=%s , alignmentimportlimit=%s"%(hitimportlimit,alignmentimportlimit)) 
        importcursor=connection.cursor()
        # query the database to retrieve all the query sequences
        if cacheQueryList:
            if querylsidprefix != None:
                sql = """
                    select
                        upper(%s),
                        xreflsid,
                        obid,
                        seqlength
                    from
                        biosequenceob
                    where
                        %s like '"""%(queryTableColumn, queryTableColumn) + querylsidprefix + "%%'"

                importmodulelogger.info("executing %s"%sql)
                importcursor = connection.cursor()
                importcursor.execute(sql)

                # make a dictionary of seqs for lookup - key is upper case xreflsid, value is a tuple of (xreflsid,obid,seqlength)
                queryDict = dict([ (mytuple[0],(mytuple[1],mytuple[2],mytuple[3])) for mytuple in importcursor.fetchall() ])

            else:
                sql = """
                    select
                        upper(%s),
                        xreflsid,
                        obid,
                        seqlength
                    from
                        biosequenceob
                        """%(queryTableColumn)

                importmodulelogger.info("executing %s"%sql)
                importcursor = connection.cursor()
                importcursor.execute(sql)

                # make a dictionary of seqs for lookup - key is upper case xreflsid, value is a tuple of (xreflsid,obid,seqlength)
                queryDict = dict([ (mytuple[0],(mytuple[1],mytuple[2],mytuple[3])) for mytuple in importcursor.fetchall() ])

        else:
            queryDict = {}


        # query the database to retrieve all the hits
        if cacheHitList:
            sql = """
                select
                    upper(xreflsid),
                    xreflsid,
                    obid
                from
                    biosequenceob
                where
                    xreflsid like '""" + subjectlsidprefix + "%%'"

            importmodulelogger.info("executing %s"%sql)
            importcursor.execute(sql)

            # make a dictionary of seqs for lookup - key is upper case xreflsid, value is a tuple of (xreflsid,obid)
            subjectDict = dict([ (mytuple[0],(mytuple[1],mytuple[2])) for mytuple in importcursor.fetchall() ])
        else:
            subjectDict = {}


        # make a dictionary of query-hit pairs - i.e. observations - will be indexed by (query,hit)
        observations = {}
        

        # process the files
        fieldNames = ()
            
        if self.dataSource.databaseFields['datasourcetype'] == 'blastx_agresearch_csv':
            """
            example : 
566,"1188_10_14726946_16654_48515_032.ab1","ref|NP_175314.1|",1,191,"ref|NP_175314.1| structural constituent of ribosome [Arabidopsis thaliana] ref|NP_849786.1| structural constituent of ribosome [Arabidopsis thaliana] sp|Q9C514|RS71_ARATH 40S ribosomal protein S7-1 gb|AAG50658.1|AC084242_2 40S ribosomal protein S7 homolog, putative [Arabidopsis thaliana] gb|AAG60128.1|AC073555_12 40S ribosomal protein S7 homolog, putative [Arabidopsis thaliana] gb|AAL06501.1|AF412048_1 At1g48830/T24P22_5 [Arabidopsis thaliana] gb|AAL62008.1| At1g48830/T24P22_5 [Arabidopsis thaliana] gb|AAM63913.1| 40S ribosomal protein S7 homolog, putative [Arabidopsis thaliana]",
"112","7e-24",55,62,62,0,10,195,92,153,"ref np_175314 structural constituent of ribosome arabidopsis thaliana ref np_849786 structural constituent of ribosome arabidopsis thaliana sp q9c514 rs71_arath 40s ribosomal protein s7-1 gb aag50658 ac084242_2 40s ribosomal protein s7 homolog putative arabidopsis thaliana gb aag60128 ac073555_12 40s ribosomal protein s7 homolog putative arabidopsis thaliana gb aal06501 af412048_1 at1g48830 t24p22_5 arabidopsis thaliana gb aal62008 at1g48830 t24p22_5 arabidopsis thaliana gb aam63913 40s ribosomal protein s7 homolog putative arabidopsis thaliana"
566,"1188_10_14726946_16654_48515_032.ab1","ref|NP_175314.1|",3,191,"ref|NP_175314.1| structural constituent of ribosome [Arabidopsis thaliana] ref|NP_849786.1| structural constituent of ribosome [Arabidopsis thaliana] sp|Q9C514|RS71_ARATH 40S ribosomal protein S7-1 gb|AAG50658.1|AC084242_2 40S ribosomal protein S7 homolog, putative [Arabidopsis thaliana] gb|AAG60128.1|AC073555_12 40S ribosomal protein S7 homolog, putative [Arabidopsis thaliana] gb|AAL06501.1|AF412048_1 At1g48830/T24P22_5 [Arabidopsis thaliana] gb|AAL62008.1| At1g48830/T24P22_5 [Arabidopsis thaliana] gb|AAM63913.1| 40S ribosomal protein S7 homolog, putative [Arabidopsis thaliana]","112","1e-11",32,39,38,0,387,503,153,191,"ref np_175314 structural constituent of ribosome arabidopsis thaliana ref np_849786 structural constituent of ribosome arabidopsis thaliana sp q9c514 rs71_arath 40s ribosomal protein s7-1 gb aag50658 ac084242_2 40s ribosomal protein s7 homolog putative arabidopsis thaliana gb aag60128 ac073555_12 40s ribosomal protein s7 homolog putative arabidopsis thaliana gb aal06501 af412048_1 at1g48830 t24p22_5 arabidopsis thaliana gb aal62008 at1g48830 t24p22_5 arabidopsis thaliana gb aam63913 40s ribosomal protein s7 homolog putative arabidopsis thaliana"
566,"1188_10_14726946_16654_48515_032.ab1","gb|ABA40437.1|",1,191,"gb|ABA40437.1| 40S ribosomal protein S7-like protein [Solanum tuberosum] gb|ABA46775.1| unknown [Solanum tuberosum] gb|ABB17004.1| ribosomal protein S7-like protein [Solanum tuberosum] gb|ABB87101.1| 40S ribosomal protein S7-like protein-like [Solanum tuberosum]","112","1e-23",55,62,61,0,10,195,92,153,"gb aba40437 40s ribosomal protein s7-like protein solanum tuberosum gb aba46775 unknown solanum tuberosum gb abb17004 ribosomal protein s7-like protein solanum tuberosum gb abb87101 40s ribosomal protein s7-like protein-like solanum tuberosum"
566,"1188_10_14726946_16654_48515_032.ab1","gb|ABA40437.1|",3,191,"gb|ABA40437.1| 40S ribosomal protein S7-like protein [Solanum tuberosum] gb|ABA46775.1| unknown [Solanum tuberosum] gb|ABB17004.1| ribosomal protein S7-like protein [Solanum tuberosum] gb|ABB87101.1| 40S ribosomal protein S7-like protein-like [Solanum tuberosum]","112","3e-13",36,39,39,0,387,503,153,191,"gb aba40437 40s ribosomal protein s7-like protein solanum tuberosum gb aba46775 unknown solanum tuberosum gb abb17004 ribosomal protein s7-like protein solanum tuberosum gb abb87101 40s ribosomal protein s7-like protein-like solanum tuberosum"
566,"1188_10_14726946_16654_48515_032.ab1","gb|ABD35819.1|",1,164,"gb|ABD35819.1| putative 40S riensis]","110","5e-23",52,62,59,0,10,195,92,153,"gb abd35819 putative 40s ribosomal protein s7 populus x canadensis" bitscore                  | double precision        |

without keywords :

4127,"LPSB","gi|124110198|gb|ABM91454.1|",3,1351,"lysergyl peptide synthetase LpsB [Neotyphodium lolii]",5939,"0",1153,1153,1153,,669,4127,199,1351
4127,"LPSB","gi|124110198|gb|ABM91454.1|",1,1351,"lysergyl peptide synthetase LpsB [Neotyphodium lolii]",1039,"1.91217e-110",198,198,198,,1,594,1,198

            """
            fieldNames = ("querylength","queryid","hitid","queryframe","hitlength","hitdescription","score",\
            "evalue","identities","alignlen","positives","gaps","queryfrom","queryto","hitfrom","hitto","keywords")
        elif self.dataSource.databaseFields['datasourcetype'] == 'blastx_agresearch_csv_nokeywords':
            fieldNames = ("querylength","queryid","hitid","queryframe","hitlength","hitdescription","score",\
            "evalue","identities","alignlen","positives","gaps","queryfrom","queryto","hitfrom","hitto")
        elif self.dataSource.databaseFields['datasourcetype'] == 'blastx_agresearch_csv_moderated':
            fieldNames = ("queryid","querydescription","hitid","hitdescription","pctidentity","evalue","alignlen","hitlength","queryfrom",\
                          "queryto","hitfrom","hitto","queryframe","hitframe","userflags")                  
        elif self.dataSource.databaseFields['datasourcetype'] == 'blastn_agresearch_csv_moderated':
            fieldNames = ("queryid","querydescription","hitid","hitdescription","pctidentity","evalue","alignlen","hitlength","queryfrom",\
                          "queryto","hitfrom","hitto","queryframe","hitframe","userflags")
        elif self.dataSource.databaseFields['datasourcetype'] == 'interpro_csv':
            fieldNames = ("queryid","hitid","hitdescription")
        elif self.dataSource.databaseFields['datasourcetype'] == 'blastn_agresearch_csv':
            """
            example :
678,"1188_10_14726942_16654_48515_016.ab1","emb|AM462343.1|","Plus / Minus",88730,"emb|AM462343.1| Vitis vinifera, whole genome shotgun sequence, contig VV78X049507.10, clone ENTAV 115","504","1e-139",344,372,19,298,658,67965,68328,""
678,"1188_10_14726942_16654_48515_016.ab1","gb|AC141115.22|","Plus / Minus",126187,"gb|AC141115.22| Medicago truncatula clone mth2-16b23, complete sequence","504","1e-139",285,295,4,1,295,63094,63384,""
678,"1188_10_14726942_16654_48515_016.ab1","emb|Y08501.2|MIATGENA","Plus / Plus",366924,"emb|Y08501.2|MIATGENA Arabidopsis thaliana mitochondrial genome","460","1e-126",351,387,14,298,675,286457,286838,""
678,"1188_10_14726942_16654_48515_016.ab1","emb|Y08501.2|MIATGENA","Plus / Plus",366924,"emb|Y08501.2|MIATGENA Arabidopsis thaliana mitochondrial genome","460","2e-72",194,211,4,1,211,53534,53740,""
678,"1188_10_14726942_16654_48515_016.ab1","emb|X98301.1|MIATNADB","Plus / Minus",4544,"emb|X98301.1|MIATNADB A.thaliana mitochondrial nad1 gene, exons 2 & 3","460","1e-126",351,387,14,298,675,3844,4225,""
            """
            fieldNames = ("querylength","queryid","hitid","hitstrand","hitlength","hitdescription","score",\
            "evalue","identities","alignlen","gaps","queryfrom","queryto","hitfrom","hitto","keywords")
        elif self.dataSource.databaseFields['datasourcetype'] == 'megablast_D3':
            """
            example :
Mon Aug  6 23:00:30 NZST 2007: Done.
Mon Aug  6 23:00:30 NZST 2007: Syncing btau3ClippedContigs_3.seq* from illuminati.agresearch.co.nz
Finished downloading btau3ClippedContigs_3.seq
Mon Aug  6 23:00:30 NZST 2007: Running MEGABLAST
Mon Aug  6 23:00:30 NZST 2007: /usr/local/blast/megablast -D2 -i chunk_25.seq -d "/home/nobody/blast/data/transient/btau3ClippedContigs_3.seq" -D 3 -t 21 -W 1
1 -q -3 -r 2 -G 5 -E 2 -e 0.01 -N 2 -F "m D" -U T -v 2 -b 2 -z 2732726237
# MEGABLAST 2.2.10 [Oct-19-2004]
# Database: /home/nobody/blast/data/transient/btau3ClippedContigs_3.seq
# Fields: Query id, Subject id, % identity, alignment length, mismatches, gap openings, q. start, q. end, s. start, s. end, e-value, bit score
413P17_454.contig00029  gi|112112410|gb|AAFC03065901.1| 89.11   101     11      0       1993    2093    101     1       3e-28    132
122B5_454.contig00079   gi|112112410|gb|AAFC03065901.1| 89.00   100     10      1       395     494     101     3       2e-26    127
            """
            fieldNames = ("queryid","hitid","pctidentity","alignlen","mismatches","gaps",\
            "queryfrom","queryto","hitfrom","hitto","evalue","bitscore")
        elif self.dataSource.databaseFields['datasourcetype'] == 'paralignprot':
            """
ENSBTAP00000023671 Btar:1k48 EOG7001QQ  gi|undefined    gnl|BL_ORD_ID|12879 ENSMEUP00000003733 pep:novel genescaffold:Meug_1.0:GeneScaffold_3275:78227:89772:-1 gene:ENSMEUG00000004096 transcript:ENSMEUT00000004109 215     1110    0       215     213     213     0       0       77      291     1       215
ENSBTAP00000023671 Btar:1k48 EOG7001QQ^Igi|undefined^Ignl|BL_ORD_ID|12879 ENSMEUP00000003733 pep:novel genescaffold:Meug_1.0:GeneScaffold_3275:78227:89772:-1 gene:ENSMEUG00000004096 transcript:ENSMEUT00000004109^I215^I1110^I0^I215^I213^I213^I0^I0^I77^I291^I1^I215$


Fields (from paralign manual) : 

query sequence description header
database sequence description header
database sequence length (215)
alignment score (1110)
evalue (0)
length of alignment (215)
number of identical symbols in alignment (213)
number of similar symbols in alignment (corresponding to a positive value in the score matrix) (213)
number of gaps (0)
number of indels (0)
alignment starting position in query sequence (1-based) (77)
alignment ending position in query sequence (1-based) (291)
alignment starting position in database sequence (1-based) (1)
alignment ending position in database sequence (1-based) (215)


            """
            fieldNames = ("queryid","junk","hitid","hitlength","score",\
            "evalue","alignlen","identities","positives","gaps","indels","queryfrom","queryto","hitfrom","hitto")
            # note needs rules  to parse queryid and description, and hitid and description , from this data as indicated above
        
        #if  self.dataSource.databaseFields['datasourcetype'] not in ('megablast_D3',"paralignprot"):           
        if fileFormat.lower() == "csv":
            reader = csv.reader(file(self.dataSource.databaseFields['physicalsourceuri']))
        else:
            reader = file(self.dataSource.databaseFields['physicalsourceuri'])
            
        rowCount = 0
        insertCount = 0
        additionalHSPCount = 0
        queryInsertCount = 0
        hitInsertCount = 0
        currentquery=''
        insertQueue = []
        queryAlignmentCount = 0
        queryAlignmentBaseCount = []
        doSemanticChecks = False
        currentqueryid = ''
        for record in reader:
            row = record
            #if rowCount%100 == 1:
            #    print "processing record %s : %s"%(rowCount, str(record))
            #if self.dataSource.databaseFields['datasourcetype'] == 'megablast_D3':
            #if self.dataSource.databaseFields['datasourcetype'].lower() != 'csv':
            if fileFormat.lower() != 'csv':
                row = re.split('\t',record.strip())
                doSemanticChecks = True

            rowCount += 1
            #if rowCount <= 3: 
            if doSemanticChecks:
                # check length and allow for field-headings and empty rows and various cruft
                if re.search("^#",record) != None:
                    continue
                elif re.search("^Downloading",record) != None:
                    continue
                elif re.search("^Finished downloading",record) != None:
                    continue
                elif re.search(".*\d\d:\d\d:\d\d.*NZDT.*:",record) != None:
                    continue
                elif len(row) != len(fieldNames):
                    if len(row) < 5:
                        continue
                    else:
                        raise brdfException("expecting \n%s \n got \n %s"%(str(fieldNames),str(row)))

                # semantically skip a row of fieldnames
                if reduce(lambda x,y: x and y, map(lambda x,y : x.upper() == y.upper(),fieldNames,row)):
                    continue

            # skip fieldnames row if one is indicated                
            if fieldNamesRow > 0 and rowCount == fieldNamesRow:
                continue
            
            fieldDict = dict(zip(fieldNames,row))
            #print str(fieldDict)
            #print "\n"

            # various filters to sanitise
            for field in fieldNames:
                if len(fieldDict[field]) == 0:
                    fieldDict[field] = None

            if "userflags" not in fieldDict:
               fieldDict["userflags"] = None

            # the bioPerl parser cannot cope with a blast format change, which
            # results in a comman in the evalue - remve
            if 'evalue' in fieldDict:
                fieldDict['evalue'] = re.sub(',','',fieldDict['evalue'])

            if 'hitdescription' not in fieldDict:
                fieldDict['hitdescription'] = fieldDict['hitid']
            if 'querydescription' not in self.dataSource.databaseFields:
                fieldDict['querydescription'] = fieldDict['queryid']

                           
            if rowCount%1000 == 1:
                print "processing row %s : %s"%(rowCount, str(fieldDict))



            # some searches such as Interpro scan have just a bare hit and description -
            # assign null values to the rest of the records.


            # check the query accession - this includes any parsing to recover the accession from the raw id in
            # the file (e.g. including removing version numbers). One or more regular expressions are provided -
            # the first one to retrieve an accession is used. This allows handling the variations in accession
            # formats that occurrs in databases. Add lsid if not there already, if necessary
            queryid = fieldDict["queryid"]
            if queryparseregexp != None:
                for rule in queryparseregexp:
                    parseresult = re.search(rule,fieldDict['queryid'])
                    if parseresult != None:
                        break
                        
                if parseresult == None:
                    raise brdfException("error parsing %s using %s, giving up on import"%(fieldDict['queryid'], str(queryparseregexp)))
                else:
                    if len(parseresult.groups()) > 0:
                        queryid = parseresult.groups()[0]
                    else:
                        raise brdfException("error parsing %s using %s, giving up on import"%(fieldDict['queryid'], str(queryparseregexp)))
                        

            # filter various bad types of record
            if queryid == None:
                importmodulelogger.info("** warning - skippng %s as short or empty queryid : %s"%(rowCount, str(fieldDict)))
                continue
            
            if len(queryid) < 2:
                importmodulelogger.info("** warning - skippng %s as short or empty queryid : %s"%(rowCount, str(fieldDict)))
                continue
                
            # if we have encountered a new query , then process any queued inserts for the current query, and consider
            # annotation of repeat. Note that it only makes sense to attempt to annotate repeats like this , if we have an
            # insert queue , i.e. if we have imposed limits on the import
            #if querysequencelsid != currentquery and currentquery != '' and len(insertQueue) > 0:
            if queryid != currentqueryid and currentqueryid != '' and len(insertQueue) > 0:

                ############# Begin block for processing queued inserts #####################
                #importmodulelogger.info("running updates using importQueue : %s"%str(insertQueue))
                for hspList in insertQueue:
                    for (tempfieldDict, queueDict) in hspList:
                        # find id's of sequences. If appropriate, create missing sequences in the database
                        #importmodulelogger.info("DEBUG (2) : checking %s in %s"%(queueDict['hitxreflsid'].upper() , str(subjectDict)))
                        if queueDict['hitxreflsid'].upper() not in subjectDict:
                            if cacheHitList and createMissingHits:
                                newsequence = bioSequenceOb()
                                newsequence.initNew(connection)                            
                                newsequence.databaseFields.update ( {
                                    'xreflsid' : queueDict['hitxreflsid'],
                                    'sequencename' :  queueDict['hitsequencename'],
                                    'sequencetype' : newHitSequenceType,
                                    'sequencedescription' : eval({True : "tempfieldDict['hitdescription']",False : "None"}['hitdescription' in tempfieldDict]),
                                    'seqlength' : eval({True : "tempfieldDict['hitlength']",False : "None"}['hitlength' in tempfieldDict]),
                                    'seqcomment' : "created by database search import",
                                    'fnindex_accession' : tempfieldDict['hitid']
                                })
                                newsequence.insertDatabase(connection)
                                subjectDict[queueDict['hitxreflsid'].upper()] = (queueDict['hitxreflsid'], newsequence.databaseFields['obid'])
                                hitInsertCount += 1
                            elif not cacheHitList: # hits were not pre-fetched to try to obtain now
                                sql = """
                                    select
                                        upper(xreflsid),
                                        xreflsid,
                                        obid
                                    from
                                        biosequenceob
                                    where
                                        xreflsid = '""" + subjectlsidprefix +  "." + queueDict['hitxreflsid'] + "'"

                                #importmodulelogger.info("executing %s"%sql)
                                importcursor.execute(sql)

                                # make a dictionary of seqs for lookup - key is upper case xreflsid, value is a tuple of (xreflsid,obid)
                                subjectDict.update(dict([ (mytuple[0],(mytuple[1],mytuple[2])) for mytuple in importcursor.fetchall() ]))



                                # check that we now have it and take appropriate action if not
                                if queueDict['hitxreflsid'].upper() not in subjectDict :
                                    if createMissingHits:
                                        newsequence = bioSequenceOb()
                                        newsequence.initNew(connection)
                                        newsequence.databaseFields.update ( {
                                            'xreflsid' : queueDict['hitxreflsid'],
                                            'sequencename' :  queueDict['hitsequencename'],
                                            'sequencetype' : newHitSequenceType,
                                            'sequencedescription' : eval({True : "tempfieldDict['hitdescription']",False : "None"}['hitdescription' in tempfieldDict]),
                                            'seqlength' : eval({True : "tempfieldDict['hitlength']",False : "None"}['hitlength' in tempfieldDict]),
                                            'seqcomment' : "created by database search import",
                                            'fnindex_accession' : tempfieldDict['hitid']
                                        })
                                        newsequence.insertDatabase(connection)
                                        subjectDict[queueDict['hitxreflsid'].upper()] = (queueDict['hitxreflsid'], newsequence.databaseFields['obid'])

                                    else:
                                        raise brdfException("%s not found in database - giving up"%queueDict['hitxreflsid'])

                            else:
                                raise brdfException("%s not found in database - giving up"%queueDict['hitxreflsid'])                                            

                        # see if we already have this observation
                        observationpair = (queryDict[queueDict['querysequencelsid'].upper()][1] , subjectDict[queueDict['hitxreflsid'].upper()][1])
                        if observationpair not in observations:
                            (observation,insertDone) = self.databaseSearchStudy.addHit(connection, querysequence = queryDict[queueDict['querysequencelsid'].upper()][1], \
                                                       hitsequence = subjectDict[queueDict['hitxreflsid'].upper()][1], \
                                                       queryxreflsid = queueDict['querysequencelsid'], \
                                                       querylength = eval({True : "tempfieldDict['querylength']",False : "queryDict[querysequencelsid.upper()][2]"}['querylength' in tempfieldDict]),\
                                                       hitxreflsid = queueDict['hitxreflsid'],\
                                                       hitdescription = eval({True : "tempfieldDict['hitdescription']",False : "None"}['hitdescription' in tempfieldDict]),\
                                                       hitlength = eval({True : "tempfieldDict['hitlength']",False : "None"}['hitlength' in tempfieldDict]),\
                                                       hitevalue = tempfieldDict['evalue'],\
                                                       checkExisting = checkExistingHits)
                            observations[observationpair] = observation


                        if insertDone:
                            insertCount += 1
                        else:
                            additionalHSPCount += 1

                        observations[observationpair].addAlignmentFact(connection,tempfieldDict, checkExistingHits)
                    # for each hsp
                # for each hit (i.e. list of hsps for a given hit)



                if annotateGenomeMapping:
                    # consider annotation of the sequence :
                    # (1) annotation of a map location
                    # (2) annotation of a repeat_region
                    # (3) annotation of the HSP count
                    # calculate the adjusted evalue, which is the evalue of the top hit divided by the evalue of the
                    # second to top hit.
                    #importmodulelogger.info("annotating sequence")

                    adjevalue = 1
                    (topAlignment, topqueueDict) =  insertQueue[0][0]
                    (secondAlignment,secondqueueDict) = (None, None)
                    if len(insertQueue[0]) > 1:
                        (secondAlignment,secondqueueDict) = insertQueue[0][1]
                    elif len(insertQueue) > 1:
                        (secondAlignment,secondqueueDict) = insertQueue[1][0]

                    evaluecutoff = 0.0
                    evidencephase = ""
                    if secondAlignment != None:
                        if float(secondAlignment['evalue']) == 0:
                            adjevalue = 1.0 # implies top must also be 0 
                        else:
                            adjevalue =  float(topAlignment['evalue'])/float(secondAlignment['evalue'])
                            
                        evidencephrase = '(multiple hits , adjusted evalue cutoff of %s)'%adjustedevaluecutoff
                        evaluecutoff = adjustedevaluecutoff

                    else:
                        adjevalue = float(topAlignment['evalue'])
                        evidencephrase = '(single hit evalue cutoff %s)'%singlehitevaluecutoff
                        evaluecutoff = singlehitevaluecutoff


                    if adjevalue <= evaluecutoff:
                        # annotate a genetic location
                        sql = """
                        insert into geneticlocationfact(
                    biosequenceob,
                    voptypeid,
                    xreflsid,
                    mapname,
                    mapobid,
                    chromosomename,
                    strand,
                    locationstart,
                    locationstop,
                    evidence,
                    evidencepvalue)
                    values(%(biosequenceob)s,
                    176,
                    %(xreflsid)s,
                    %(mapname)s,
                    %(mapobid)s,
                    %(chromosomename)s,
                    %(strand)s,
                    %(locationstart)s,
                    %(locationstop)s,
                    %(evidence)s,
                    %(evidencepvalue)s)
                    """
                        #print str(topqueueDict)
                        #print "**************"
                        #print str(topAlignment)
                        updateDetails = {
                            'biosequenceob' : queryDict[topqueueDict['querysequencelsid'].upper()][1],
                            'mapobid' : subjectDict[topqueueDict['hitxreflsid'].upper()][1],
                            'chromosomename' : topqueueDict['hitsequencename'],
                            'locationstart' : topAlignment['hitfrom'],
                            'locationstop' : topAlignment['hitto'],
                            'strand' : {True : '1', False : '-1'}[float(topAlignment['hitto']) - float(topAlignment['hitfrom']) >= 0.0],
                            'evidencepvalue' : adjevalue
                            }
                        updateDetails.update(locationMapDetails)
                        updateDetails['evidence'] += evidencephrase
                        updateDetails.update({
                            'xreflsid' : '%s.%s'%(updateDetails['mapname'],querysequencelsid)
                        })
                        #importmodulelogger.info("executing %s"%str(sql%updateDetails))
                        importcursor.execute(sql,updateDetails)
                        connection.commit()
                                                                


                    # annotate the HSP count
                    sql = """
                    insert into biosequencefact(
                       biosequenceob,
                       factnamespace,
                       attributename,
                       attributevalue)
                    select
                       %(biosequenceob)s,
                       ds.xreflsid || ' : Details',
                       'HSP Count',
                       %(queryAlignmentCount)s
                    from
                       databasesearchstudy ds
                    where
                       obid = %(databasesearchstudy)s
                    """%{
                        'biosequenceob' : queryDict[topqueueDict['querysequencelsid'].upper()][1],
                        'queryAlignmentCount' : queryAlignmentCount,
                        'databasesearchstudy' : self.databaseFields['databaseSearchStudy']
                        }
                    #importmodulelogger.info("executing %s"%str(sql))
                    importcursor.execute(sql)
                    connection.commit()                
                    


                    # annotate repeat regions. These are regions whose bases are members of more than hspcountforrepeat hsps
                    #importmodulelogger.info("annotating repeat regions using %s"%str(queryAlignmentBaseCount))
                    if max(queryAlignmentBaseCount) > hspcountforrepeat:
                        # we move along the sequence annotating regions. A region begins with the next base with more
                        # than hspcountforrepeat, and ends when there have been 10 consecutive positions with < hspcountforrepeat/2
                        # counts
                        regions = []
                        region = [None,None]
                        flankcount = 0
                        for ibase in range(0,len(queryAlignmentBaseCount)):
                            if queryAlignmentBaseCount[ibase] > hspcountforrepeat:
                                if region[0] == None:
                                    region[0] = ibase
                                flankcount = 0
                            elif queryAlignmentBaseCount[ibase] > hspcountforrepeat/2.0:
                                flankcount = 0
                            elif queryAlignmentBaseCount[ibase]  <= hspcountforrepeat/2.0:
                                if region[0] != None:
                                    flankcount += 1
                                    if flankcount >= 10:
                                        # store region
                                        region[1] = ibase - 10
                                        regions.append(region)
                                        region = [None, None]
                        if region[0] != None and region[1] == None:
                            region[1] = len(queryAlignmentBaseCount) - 1
                            regions.append(region)
                            
                        # if we have any regions, annotate them all
                        for region in regions:
                            sql = """
                            insert into biosequencefeaturefact(
             biosequenceob,
             xreflsid,
             featuretype,
             featurestart,
             featurestop,
             featurestrand,
             evidence,
             featurelength) values(
             %(biosequenceob)s,
             %(xreflsid)s,
             %(featuretype)s,
             %(featurestart)s,
             %(featurestop)s,
             %(featurestrand)s,
             %(evidence)s,
             %(featurelength)s         
             )
             """
                            updateDetails = {
                                'biosequenceob' : queryDict[topqueueDict['querysequencelsid'].upper()][1],
                                'xreflsid' : "%s.repeat_region.%s"%(topqueueDict['querysequencelsid'],1+region[0]),
                                'featuretype' : 'repeat_region',
                                'featurestart' : 1+region[0],
                                'featurestop' : 1+region[1],
                                'featurestrand' : '1',
                                'evidence' : 'Megablast against Btau4, > %s hsps'%hspcountforrepeat,
                                'featurelength' : region[1] - region[0]
                            }
                            #importmodulelogger.info("executing %s"%str(sql%updateDetails))
                            importcursor.execute(sql,updateDetails)
                            connection.commit()
                    # end of block to do genome mapping annotation

                                
                # reset the insert queue and associated stats after processing the queue for this sequence        
                insertQueue = []
                observations = {}    # this is a bit ad-hoc - if we are using queued inserts we will get a very large
                                     # dictionary here - and also we are unlikely to be refreshing blasts, which is
                                     # all this was used for. Alternatively, we could manage the size of this
                                     # as is done below, for the non-queue insert option
                #print "queryAlignmentCount for %s = %s"%(currentquery,queryAlignmentCount)
                queryAlignmentCount = 0
                queryAlignmentBaseCount = []

                ############# End block for processing queued inserts #####################        
            # end of block for processing queued inserts and annotating repeats before moving on to next sequence
            

            # flush the query alignment counts if this is a new query (may already have
            # been flushed if we just processed a queue)
            if currentqueryid != queryid:
                queryAlignmentCount = 0
                queryAlignmentBaseCount  = []                
            
            currentqueryid = queryid

            if querylsidprefix != None:
                if re.search("^%s\."%querylsidprefix, currentqueryid) == None:
                    querysequencelsid = "%s.%s"%(querylsidprefix, currentqueryid)
                else:
                    querysequencelsid = currentqueryid
                    
            else:
                querysequencelsid = currentqueryid
            

            # check the hit accession - this includes any parsing to recover the accession from the raw id in
            # the file (e.g. including removing version numbers). One or more regular expressions are provided -
            # the first one to retrieve an accession is used. This allows handling the variations in accession
            # formats that occurrs in databases. Add lsid if not there already, if necessary
            hitsequence = fieldDict["hitid"]
            if subjectparseregexp != None:
                for rule in subjectparseregexp:
                    parseresult = re.search(rule,fieldDict['hitid'])
                    if parseresult != None:
                        break
                        
                if parseresult == None:
                    raise brdfException("error parsing %s using %s, giving up on import"%(fieldDict['hitid'], str(subjectparseregexp)))
                else:
                    if len(parseresult.groups()) > 0:
                        hitsequence = parseresult.groups()[0]
                    else:
                        raise brdfException("error parsing %s using %s, giving up on import"%(fieldDict['hitid'], str(subjectparseregexp)))

            # filter various bad types of record
            if len(hitsequence) < 2:
                importmodulelogger.info("** warning - skippng %s as short or empty hitid : %s"%(rowCount, str(fieldDict)))
                continue

                    
            hitsequencelsid = hitsequence
                    
            if subjectlsidprefix != None:
                if re.search("^%s\."%subjectlsidprefix, hitsequencelsid) == None:
                    hitsequencelsid = "%s.%s"%(subjectlsidprefix, hitsequence)

            # find id's of sequences. If appropriate, create missing sequences in the database
            # if we did not pre-query all the queries, then we will need to search the 
            # db to find this sequence.
            if querysequencelsid.upper() not in queryDict:
                if cacheQueryList and createMissingQueries: # we should already have the sequence - we don't and 
                                                            # it is OK to create queries, so do so
                    newsequence = bioSequenceOb()
                    newsequence.initNew(connection)                            
                    newsequence.databaseFields.update ( {
                             'xreflsid' : querysequencelsid,
                                'sequencename' :  queryid,
                                'sequencetype' : newQuerySequenceType,
                                'seqlength' : eval({True : "fieldDict['querylength']",False : "None"}['querylength' in fieldDict]),
                                'seqcomment' : "created by database search import"
                    })
                    newsequence.insertDatabase(connection)
                    queryDict[querysequencelsid.upper()] = (querysequencelsid, newsequence.databaseFields['obid'], newsequence.databaseFields['seqlength'])
                    queryInsertCount += 1
                elif not cacheQueryList:     # queries were not pre-fetched to try to obtain now
                    if querylsidprefix != None:
                        sql = """
                            select
                                upper(%s),
                                xreflsid,
                                obid,
                                seqlength
                            from
                                biosequenceob
                            where
                                %s = '"""%(queryTableColumn, queryTableColumn) + querylsidprefix + "." + querysequencelsid + "'"

                        #importmodulelogger.info("executing %s (1)"%sql)
                        importcursor = connection.cursor()
                        importcursor.execute(sql)

                        # make a dictionary of seqs for lookup - key is upper case xreflsid, value is a tuple of (xreflsid,obid,seqlength)
                        #queryDict.update(dict([ (mytuple[0],(mytuple[1],mytuple[2],mytuple[3])) for mytuple in importcursor.fetchall() ]))
                        queryDict = dict([ (mytuple[0],(mytuple[1],mytuple[2],mytuple[3])) for mytuple in importcursor.fetchall() ])

                    else:
                        sql = """
                            select
                                upper(%s),
                                xreflsid,
                                obid,
                                seqlength
                            from
                                biosequenceob
                            where 
                                %s = '"""%(queryTableColumn,queryTableColumn) + querysequencelsid + "'"

                        #importmodulelogger.info("executing %s (2)"%sql)
                        importcursor = connection.cursor()
                        importcursor.execute(sql)

                        # make a dictionary of seqs for lookup - key is upper case xreflsid, value is a tuple of (xreflsid,obid,seqlength)
                        #queryDict.update(dict([ (mytuple[0],(mytuple[1],mytuple[2],mytuple[3])) for mytuple in importcursor.fetchall() ]))
                        queryDict = dict([ (mytuple[0],(mytuple[1],mytuple[2],mytuple[3])) for mytuple in importcursor.fetchall() ])

                        #importmodulelogger.info("DEBUG : queryDict = %s"%str(queryDict))

                    # check that we now have it and take appropriate action if not
                    if querysequencelsid.upper() not in queryDict :
                        if createMissingQueries:
                            newsequence = bioSequenceOb()
                            newsequence.initNew(connection)
                            newsequence.databaseFields.update ( {
                             'xreflsid' : querysequencelsid,
                             'sequencename' :  queryid,
                             'sequencetype' : newQuerySequenceType,
                             'seqlength' : eval({True : "fieldDict['querylength']",False : "None"}['querylength' in fieldDict]),
                             'seqcomment' : "created by database search import"
                            })
                            newsequence.insertDatabase(connection)
                            queryDict[querysequencelsid.upper()] = (querysequencelsid, newsequence.databaseFields['obid'],newsequence.databaseFields['seqlength'])
                            queryInsertCount += 1
                        else:
                            raise brdfException("%s not found in database - giving up"%querysequencelsid)


                else:
                    raise brdfException("%s not found in database - giving up"%querysequencelsid)


            # update the queryAlignmentCount and the individual base alignment counts
            queryAlignmentCount += 1

            if len(queryAlignmentBaseCount) == 0 and queryDict[querysequencelsid.upper()][2] != None:
                queryAlignmentBaseCount  = int(queryDict[querysequencelsid.upper()][2]) * [0]
            else:
                queryAlignmentBaseCount = []
                

            if 'queryfrom' in fieldDict and 'queryto' in fieldDict and len(queryAlignmentBaseCount) > 0:
                try:
                    for ibase in range(int(fieldDict['queryfrom'])-1 , int(fieldDict['queryto'])):
                        queryAlignmentBaseCount[ibase] += 1
                except IndexError,e:
                    print "Error indexing queryAlignmentBaseCount of length %s using %s "%(len(queryAlignmentBaseCount), str(fieldDict))
                    print "(queryAlignmentBaseCount set up from %s)"%str(queryDict[querysequencelsid.upper()])
                    print "Re-raising exception...."
                    raise e




            ##### if we do not have any import limits then update db now ####
            if hitimportlimit == 0 and alignmentimportlimit == 0:

                #importmodulelogger.info("==>debug1")

                # find id's of sequences. If appropriate, create missing sequences in the database
                if hitsequencelsid.upper() not in subjectDict :
                    if cacheHitList and createMissingHits:
                        newsequence = bioSequenceOb()
                        newsequence.initNew(connection)                            
                        newsequence.databaseFields.update ( {
                                'xreflsid' : hitsequencelsid,
                                'sequencename' :  hitsequence,
                                'sequencetype' : newHitSequenceType,
                                'sequencedescription' : eval({True : "fieldDict['hitdescription']",False : "None"}['hitdescription' in fieldDict]),
                                'seqlength' :  eval({True : "fieldDict['hitlength']",False : "None"}['hitlength' in fieldDict]),
                                'seqcomment' : "created by database search import",
                                'fnindex_accession' : fieldDict['hitid']
                        })
                        newsequence.insertDatabase(connection)
                        subjectDict[hitsequencelsid.upper()] = (hitsequencelsid, newsequence.databaseFields['obid'])
                        hitInsertCount += 1

                    elif not cacheHitList: # hits were not pre-fetched to try to obtain now
                        sql = """
                            select
                                upper(xreflsid),
                                xreflsid,
                                obid
                            from
                                biosequenceob
                            where
                                xreflsid = '""" + subjectlsidprefix +  "." + hitsequencelsid + "'"

                        #importmodulelogger.info("executing %s"%sql)
                        importcursor.execute(sql)

                        # make a dictionary of seqs for lookup - key is upper case xreflsid, value is a tuple of (xreflsid,obid)
                        subjectDict.update(dict([ (mytuple[0],(mytuple[1],mytuple[2])) for mytuple in importcursor.fetchall() ]))


                        # check that we now have it and take appropriate action if not
                        if hitsequencelsid.upper() not in subjectDict : 
                            if createMissingHits:

                                newsequence = bioSequenceOb()
                                newsequence.initNew(connection)
                                newsequence.databaseFields.update ( {
                                    'xreflsid' : hitsequencelsid,
                                    'sequencename' :  hitsequence,
                                    'sequencetype' : newHitSequenceType,
                                    'sequencedescription' : eval({True : "fieldDict['hitdescription']",False : "None"}['hitdescription' in fieldDict]),
                                    'seqlength' :  eval({True : "fieldDict['hitlength']",False : "None"}['hitlength' in fieldDict]),
                                    'seqcomment' : "created by database search import",
                                    'fnindex_accession' : fieldDict['hitid']
                                })
                                newsequence.insertDatabase(connection)
                                subjectDict[hitsequencelsid.upper()] = (hitsequencelsid, newsequence.databaseFields['obid'])
                                hitInsertCount += 1

                            else:
                                raise brdfException("%s not found in database - giving up"%hitsequencelsid)

                    else:
                        raise brdfException("%s not found in database - giving up"%hitsequencelsid)


                # see if we already have this observation
                observationpair = (queryDict[querysequencelsid.upper()][1] , subjectDict[hitsequencelsid.upper()][1])
                if observationpair not in observations:
                    
                
                        
                    (observation,insertDone) = self.databaseSearchStudy.addHit(connection, querysequence = queryDict[querysequencelsid.upper()][1], \
                                            hitsequence = subjectDict[hitsequencelsid.upper()][1], \
                                               queryxreflsid = querysequencelsid, \
                                               querylength = eval({True : "fieldDict['querylength']",False : "queryDict[querysequencelsid.upper()][2]"}['querylength' in fieldDict]),\
                                               #querylength = fieldDict['querylength'],\
                                               hitxreflsid = hitsequencelsid,\
                                               hitdescription = eval({True : "fieldDict['hitdescription']",False : "None"}['hitdescription' in fieldDict]),\
                                               hitlength =  eval({True : "fieldDict['hitlength']",False : "None"}['hitlength' in fieldDict]),\
                                               hitevalue = eval({True : "fieldDict['evalue']",False : "None"}['evalue' in fieldDict]),\
                                               checkExisting = checkExistingHits, \
                                               userflags = fieldDict['userflags'])

                    
                    observations[observationpair] = observation # we may need to add a memory management strategy here to
                                                                # prevent this getting too big. For example, assuming the blast is
                                                                # sorted , then go through and remove all entries where the query is
                                                                # different to the current query.....
                                                                
                    # clean this dictionary - it gets too big with large blasts
                    for observationtocheck in observations.keys():
                        if observationtocheck[0] != observationpair[0]:
                            del observations[observationtocheck]
                            
                else:
                    # if the data set we are importing has user flags for the hit, do an update
                    if 'userflags' in fieldDict:
                        if fieldDict['userflags'] != None:
                            self.databaseSearchStudy.updateHit(connection, queryxreflsid = querysequencelsid, \
                                               hitxreflsid = hitsequencelsid, updateDict = {
                                                   'userflags' : fieldDict['userflags']
                                                   })

                if insertDone:
                    insertCount += 1
                else:
                    additionalHSPCount += 1

                observations[observationpair].addAlignmentFact(connection,fieldDict, checkExistingHits)

                
            else:
                ########### we have import limits to apply so we update the queue , rather than do the insert ######
                # update insert queue  - any current item in the queue that is worse than
                # the candidate record will be replaced.
                # the structure of the queue is that it is a sorted list of sorted lists of dictionary tuples - e.g.
                # to access a tuple of dictionaries to be used in an update : 
                # (fieldDict,queueDict) = outerlist[3][4]
                #
                # Each list in the outer list corresponds to a hit - i.e. for each hit we have a list
                # of hsps. The inner list of hsps is sorted by evalue of the alignment. The outer list
                # is sorted by the evalue of the best alignment of the inner list. 
                #
                # Begin queue update :
                #
                # First, if the length of the queue is less than the hit limit (or there is no hit limit) then
                # , if this is a new hit not in the queue , add the candidate hit to the queue, and re-sort the queue
                hspadded = False
                #importmodulelogger.info(str(insertQueue))
                if (len(insertQueue) < hitimportlimit) or hitimportlimit == 0:
                    #importmodulelogger.info("** checking for queue append **")
                    hspList = [ (fieldDict, {
                        'hitxreflsid' : hitsequencelsid,
                        'hitsequencename' :  hitsequence,
                        'querysequencelsid' : querysequencelsid
                        })]
                    if len(insertQueue) == 0:                        
                        insertQueue.append(hspList)
                        #insertQueue.sort(lambda x,y:sign( float(x[0][0][limitorderby])-float(y[0][0][limitorderby]) ) )
                        insertQueue.sort(lambda x,y:hspcomp(x[0][0],y[0][0],limitorderby))
                        
                        hspadded = True
                    else:
                        # see if this is a new hit
                        newhit = True
                        for hspListTemp in insertQueue:
                            if hspListTemp[0][1]['hitxreflsid'] == hitsequencelsid:
                                newhit = False
                                break
                        if newhit:
                            insertQueue.append(hspList)
                            #insertQueue.sort(lambda x,y:sign( float(x[0][0][limitorderby])-float(y[0][0][limitorderby]) ) )
                            insertQueue.sort(lambda x,y:hspcomp(x[0][0],y[0][0],limitorderby))
                            hspadded = True

                # if we have not added this hit to the queue then check the queue to see if this 
                # hit can update it. This can occurr if either
                # 1) this is a new hit, but the queue is already at max length so we did not add it above - if this
                #    hit has a better HSP than one in the queue, it should replace it
                # 2) this is not a new hit , but either we can add an HSP if the alignment count is not at 
                #    max, or we can replace an HSP if it is at max
                if not hspadded:
                    #importmodulelogger.info("** checking for queue update **")
                    # check whether this hsp should replace one that is already queued
                    #
                    # for each hit in the queue
                    resort = False
                    for i in range(0,len(insertQueue)):
                        hspList = insertQueue[i]
                        # if the candidate hsp is a different hit to the current hit, and its evalue
                        # is better than the best hsp evalue of the current hit
                        # replace this hit with the
                        # current one and break (do not need to re-sort as we know the set of hits will still be
                        # sorted correctly - we have just insert something that comes before the current entry
                        # but after the previous one
                        if hspList[0][1]['hitxreflsid'] != hitsequencelsid:
                            #if  float(fieldDict[limitorderby]) < float(hspList[0][0][limitorderby]):
                            if  hspcomp(fieldDict, hspList[0][0],limitorderby) == -1:
                                insertQueue.insert(i, [ (fieldDict, {
                                    'hitxreflsid' : hitsequencelsid,
                                    'hitsequencename' :  hitsequence,
                                    'querysequencelsid' : querysequencelsid
                                })])
                                del insertQueue[-1]
                                break
                        else:
                            # this hit matches this Hsp list - so we may be able to either append to the
                            # hsp list, or else replace one of the entries in it
                            # 
                            # if the length of the hsp list is less than the maximum, then
                            # append this alignment to the hsp list and re-sort it , set the resort flag
                            # (since the whole queue needs re-sorting) then break       
                            if (len(hspList) < alignmentimportlimit) or alignmentimportlimit == 0:
                                hspList.append((fieldDict, {
                                    'hitxreflsid' : hitsequencelsid,
                                    'hitsequencename' :  hitsequence,
                                    'querysequencelsid' : querysequencelsid
                                }))
                                #hspList.sort(lambda x,y:sign( float(x[0][limitorderby])-float(y[0][limitorderby]) ) )
                                #importmodulelogger.info("sorting queue (1)")
                                hspList.sort(lambda x,y:hspcomp(x[0],y[0],limitorderby)) 
                                #importmodulelogger.info("queue after sort and update : %s"%str(hspList))
                                
                                resort = True
                            else:
                                # see if we can replace any hsps with this one, if it is better
                                # for each HSP
                                for j in range(0,len(hspList)):
                                    hsp = hspList[j]
                                    # if the candidate hsp is better then replace
                                    #importmodulelogger.info("*** comparing %s and %s"%(float(fieldDict[limitorderby]), float(hsp[0][limitorderby])))
                                    #if float(fieldDict[limitorderby]) < float(hsp[0][limitorderby]):
                                    if hspcomp(fieldDict,hsp[0],limitorderby) == -1:
                                        #replace this candidate alignment
                                        hspList.insert(j,(fieldDict, {
                                            'hitxreflsid' : hitsequencelsid,
                                            'hitsequencename' :  hitsequence,
                                            'querysequencelsid' : querysequencelsid
                                        }))
                                        del hspList[-1]
                                        resort = True
                                        # break out of the loop considering the hsps in the hsp list
                                        break
                            # the candidate hit matched one of the queued hits. We have either appended another
                            # HSP or replaced one. We do not need to consider any further items in the queue, so break
                            # out of the loop that is checking the queue
                            break
                        
                    # resort the queue if needed
                    if resort:
                        #importmodulelogger.info("sorting queue (2)")
                        #insertQueue.sort(lambda x,y:sign( float(x[0][0][limitorderby])-float(y[0][0][limitorderby]) ) )
                        insertQueue.sort(lambda x,y:hspcomp(x[0][0],y[0][0],limitorderby))
                        #importmodulelogger.info("queue after sort and update : %s"%str(hspList))

                        
        ###### if we are using an insert queue , then do a final processing of this queueu
        # note that this block is a simple copy of the block above for processing the queue - this is very
        # ugly and should be fixed !
        if len(insertQueue) > 0:        
            ############# Begin block for processing queued inserts #####################
            #importmodulelogger.info("running updates using importQueue : %s"%str(insertQueue))
            for hspList in insertQueue:
                for (tempfieldDict, queueDict) in hspList:
                    # find id's of sequences. If appropriate, create missing sequences in the database
                    #importmodulelogger.info("DEBUG (2) : checking %s in %s"%(queueDict['hitxreflsid'].upper() , str(subjectDict)))
                    if queueDict['hitxreflsid'].upper() not in subjectDict:
                        if cacheHitList and createMissingHits:
                            newsequence = bioSequenceOb()
                            newsequence.initNew(connection)                            
                            newsequence.databaseFields.update ( {
                                'xreflsid' : queueDict['hitxreflsid'],
                                'sequencename' :  queueDict['hitsequencename'],
                                'sequencetype' : newHitSequenceType,
                                'sequencedescription' : eval({True : "tempfieldDict['hitdescription']",False : "None"}['hitdescription' in tempfieldDict]),
                                'seqlength' : eval({True : "tempfieldDict['hitlength']",False : "None"}['hitlength' in tempfieldDict]),
                                'seqcomment' : "created by database search import",
                                'fnindex_accession' : tempfieldDict['hitid']
                            })
                            newsequence.insertDatabase(connection)
                            subjectDict[queueDict['hitxreflsid'].upper()] = (queueDict['hitxreflsid'], newsequence.databaseFields['obid'])
                            hitInsertCount += 1
                        elif not cacheHitList: # hits were not pre-fetched to try to obtain now
                            sql = """
                                select
                                    upper(xreflsid),
                                    xreflsid,
                                    obid
                                from
                                    biosequenceob
                                where
                                    xreflsid = '""" + subjectlsidprefix +  "." + queueDict['hitxreflsid'] + "'"

                            #importmodulelogger.info("executing %s"%sql)
                            importcursor.execute(sql)

                            # make a dictionary of seqs for lookup - key is upper case xreflsid, value is a tuple of (xreflsid,obid)
                            subjectDict.update(dict([ (mytuple[0],(mytuple[1],mytuple[2])) for mytuple in importcursor.fetchall() ]))



                            # check that we now have it and take appropriate action if not
                            if queueDict['hitxreflsid'].upper() not in subjectDict :
                                if createMissingHits:
                                    newsequence = bioSequenceOb()
                                    newsequence.initNew(connection)
                                    newsequence.databaseFields.update ( {
                                        'xreflsid' : queueDict['hitxreflsid'],
                                        'sequencename' :  queueDict['hitsequencename'],
                                        'sequencetype' : newHitSequenceType,
                                        'sequencedescription' : eval({True : "tempfieldDict['hitdescription']",False : "None"}['hitdescription' in tempfieldDict]),
                                        'seqlength' : eval({True : "tempfieldDict['hitlength']",False : "None"}['hitlength' in tempfieldDict]),
                                        'seqcomment' : "created by database search import",
                                        'fnindex_accession' : tempfieldDict['hitid']
                                    })
                                    newsequence.insertDatabase(connection)
                                    subjectDict[queueDict['hitxreflsid'].upper()] = (queueDict['hitxreflsid'], newsequence.databaseFields['obid'])

                                else:
                                    raise brdfException("%s not found in database - giving up"%queueDict['hitxreflsid'])

                        else:
                            raise brdfException("%s not found in database - giving up"%queueDict['hitxreflsid'])                                            

                    # see if we already have this observation
                    observationpair = (queryDict[queueDict['querysequencelsid'].upper()][1] , subjectDict[queueDict['hitxreflsid'].upper()][1])
                    if observationpair not in observations:
                        (observation,insertDone) = self.databaseSearchStudy.addHit(connection, querysequence = queryDict[queueDict['querysequencelsid'].upper()][1], \
                                                   hitsequence = subjectDict[queueDict['hitxreflsid'].upper()][1], \
                                                   queryxreflsid = queueDict['querysequencelsid'], \
                                                   querylength = eval({True : "tempfieldDict['querylength']",False : "queryDict[querysequencelsid.upper()][2]"}['querylength' in tempfieldDict]),\
                                                   hitxreflsid = queueDict['hitxreflsid'],\
                                                   hitdescription = eval({True : "tempfieldDict['hitdescription']",False : "None"}['hitdescription' in tempfieldDict]),\
                                                   hitlength = eval({True : "tempfieldDict['hitlength']",False : "None"}['hitlength' in tempfieldDict]),\
                                                   hitevalue = tempfieldDict['evalue'],\
                                                   checkExisting = checkExistingHits)
                        observations[observationpair] = observation


                    if insertDone:
                        insertCount += 1
                    else:
                        additionalHSPCount += 1

                    observations[observationpair].addAlignmentFact(connection,tempfieldDict, checkExistingHits)
                # for each hsp
            # for each hit (i.e. list of hsps for a given hit)



            if annotateGenomeMapping:
                # consider annotation of the sequence :
                # (1) annotation of a map location
                # (2) annotation of a repeat_region
                # (3) annotation of the HSP count
                # calculate the adjusted evalue, which is the evalue of the top hit divided by the evalue of the
                # second to top hit.
                #importmodulelogger.info("annotating sequence")

                adjevalue = 1
                (topAlignment, topqueueDict) =  insertQueue[0][0]
                (secondAlignment,secondqueueDict) = (None, None)
                if len(insertQueue[0]) > 1:
                    (secondAlignment,secondqueueDict) = insertQueue[0][1]
                elif len(insertQueue) > 1:
                    (secondAlignment,secondqueueDict) = insertQueue[1][0]

                evaluecutoff = 0.0
                evidencephase = ""
                if secondAlignment != None:
                    if float(secondAlignment['evalue']) == 0:
                        adjevalue = 1.0 # implies top must also be 0 
                    else:
                        adjevalue =  float(topAlignment['evalue'])/float(secondAlignment['evalue'])
                        
                    evidencephrase = '(multiple hits , adjusted evalue cutoff of %s)'%adjustedevaluecutoff
                    evaluecutoff = adjustedevaluecutoff

                else:
                    adjevalue = float(topAlignment['evalue'])
                    evidencephrase = '(single hit evalue cutoff %s)'%singlehitevaluecutoff
                    evaluecutoff = singlehitevaluecutoff


                if adjevalue <= evaluecutoff:
                    # annotate a genetic location
                    sql = """
                    insert into geneticlocationfact(
                biosequenceob,
                voptypeid,
                xreflsid,
                mapname,
                mapobid,
                chromosomename,
                strand,
                locationstart,
                locationstop,
                evidence,
                evidencepvalue)
                values(%(biosequenceob)s,
                176,
                %(xreflsid)s,
                %(mapname)s,
                %(mapobid)s,
                %(chromosomename)s,
                %(strand)s,
                %(locationstart)s,
                %(locationstop)s,
                %(evidence)s,
                %(evidencepvalue)s)
                """
                    #print str(topqueueDict)
                    #print "**************"
                    #print str(topAlignment)
                    updateDetails = {
                        'biosequenceob' : queryDict[topqueueDict['querysequencelsid'].upper()][1],
                        'mapobid' : subjectDict[topqueueDict['hitxreflsid'].upper()][1],
                        'chromosomename' : topqueueDict['hitsequencename'],
                        'locationstart' : topAlignment['hitfrom'],
                        'locationstop' : topAlignment['hitto'],
                        'strand' : {True : '1', False : '-1'}[float(topAlignment['hitto']) - float(topAlignment['hitfrom']) >= 0.0],
                        'evidencepvalue' : adjevalue
                        }
                    updateDetails.update(locationMapDetails)
                    updateDetails['evidence'] += evidencephrase
                    updateDetails.update({
                        'xreflsid' : '%s.%s'%(updateDetails['mapname'],querysequencelsid)
                    })
                    #importmodulelogger.info("executing %s"%str(sql%updateDetails))
                    importcursor.execute(sql,updateDetails)
                    connection.commit()
                                                            


                # annotate the HSP count
                sql = """
                insert into biosequencefact(
                   biosequenceob,
                   factnamespace,
                   attributename,
                   attributevalue)
                select
                   %(biosequenceob)s,
                   ds.xreflsid || ' : Details',
                   'HSP Count',
                   %(queryAlignmentCount)s
                from
                   databasesearchstudy ds
                where
                   obid = %(databasesearchstudy)s
                """%{
                    'biosequenceob' : queryDict[topqueueDict['querysequencelsid'].upper()][1],
                    'queryAlignmentCount' : queryAlignmentCount,
                    'databasesearchstudy' : self.databaseFields['databaseSearchStudy']
                    }
                #importmodulelogger.info("executing %s"%str(sql))
                importcursor.execute(sql)
                connection.commit()                
                


                # annotate repeat regions. These are regions whose bases are members of more than hspcountforrepeat hsps
                #importmodulelogger.info("annotating repeat regions using %s"%str(queryAlignmentBaseCount))
                if max(queryAlignmentBaseCount) > hspcountforrepeat:
                    # we move along the sequence annotating regions. A region begins with the next base with more
                    # than hspcountforrepeat, and ends when there have been 10 consecutive positions with < hspcountforrepeat/2
                    # counts
                    regions = []
                    region = [None,None]
                    flankcount = 0
                    for ibase in range(0,len(queryAlignmentBaseCount)):
                        if queryAlignmentBaseCount[ibase] > hspcountforrepeat:
                            if region[0] == None:
                                region[0] = ibase
                            flankcount = 0
                        elif queryAlignmentBaseCount[ibase] > hspcountforrepeat/2.0:
                            flankcount = 0
                        elif queryAlignmentBaseCount[ibase]  <= hspcountforrepeat/2.0:
                            if region[0] != None:
                                flankcount += 1
                                if flankcount >= 10:
                                    # store region
                                    region[1] = ibase - 10
                                    regions.append(region)
                                    region = [None, None]
                    if region[0] != None and region[1] == None:
                        region[1] = len(queryAlignmentBaseCount) - 1
                        regions.append(region)
                        
                    # if we have any regions, annotate them all
                    for region in regions:
                        sql = """
                        insert into biosequencefeaturefact(
         biosequenceob,
         xreflsid,
         featuretype,
         featurestart,
         featurestop,
         featurestrand,
         evidence,
         featurelength) values(
         %(biosequenceob)s,
         %(xreflsid)s,
         %(featuretype)s,
         %(featurestart)s,
         %(featurestop)s,
         %(featurestrand)s,
         %(evidence)s,
         %(featurelength)s         
         )
         """
                        updateDetails = {
                            'biosequenceob' : queryDict[topqueueDict['querysequencelsid'].upper()][1],
                            'xreflsid' : "%s.repeat_region.%s"%(topqueueDict['querysequencelsid'],1+region[0]),
                            'featuretype' : 'repeat_region',
                            'featurestart' : 1+region[0],
                            'featurestop' : 1+region[1],
                            'featurestrand' : '1',
                            'evidence' : 'Megablast against Btau4, > %s hsps'%hspcountforrepeat,
                            'featurelength' : region[1] - region[0]
                        }
                        #importmodulelogger.info("executing %s"%str(sql%updateDetails))
                        importcursor.execute(sql,updateDetails)
                        connection.commit()
                # end of block to do genome mapping annotation

                            
            # reset the insert queue and associated stats after processing the queue for this sequence        
            insertQueue = []
            observations = {}    # this is a bit ad-hoc - if we are using queued inserts we will get a very large
                                 # dictionary here - and also we are unlikely to be refreshing blasts, which is
                                 # all this was used for. Alternatively, we could manage the size of this
                                 # as is done below, for the non-queue insert option
            #print "queryAlignmentCount for %s = %s"%(currentquery,queryAlignmentCount)
            queryAlignmentCount = 0
            queryAlignmentBaseCount = []

            ############# End block for processing queued inserts #####################        
                



        self.obState.update({
            'DB_PENDING' : 0,
            'MESSAGE' : """
            Database search import complete.

            Insert count            =       %s
            additional HSPcount     =       %s
            Query seqs created      =       %s
            Hit seqs created        =       %s
            """%(insertCount, additionalHSPCount,queryInsertCount,hitInsertCount)})
            
            
        
        
        
        
        

