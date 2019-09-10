#-----------------------------------------------------------------------+
# Name:		geneIndexProcedures.py           			|
#									|
# Description:	classes that implements procedures for creating and     |
# maintaining a gene index in the brdf                                  |
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
# 6/2007    AFM  initial version                                        |
#-----------------------------------------------------------------------+
import sys
import types
import PgSQL
import csv
import re
import os
import math
import random
from datetime import date
import globalConf

from obmodule import getNewObid
from brdfExceptionModule import brdfException
from annotationModule import commentOb, uriOb
from ontologyModule import ontologyOb
from biosubjectmodule import bioSubjectOb, bioSampleOb, bioSampleList
from studyModule import phenotypeStudy, geneExpressionStudy
from labResourceModule import labResourceOb
from dataImportModule import dataSourceOb,importProcedureOb,labResourceImportFunction,microarrayExperimentImportFunction
from studyModule import microarrayObservation
from sequenceModule import bioSequenceOb
from sequenceFileParsers import FastaParser
from geneticModule import geneticOb, geneticLocationFact

import databaseModule

import logging


# set up logger if we want logging
proceduremodulelogger = logging.getLogger('geneindexProcedures')
proceduremodulehdlr = logging.FileHandler(os.path.join(globalConf.LOGPATH,'geenindexProcedures.log'))
#hdlr = logging.FileHandler('c:/temp/sheepgenomicsforms.log')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
proceduremodulehdlr.setFormatter(formatter)
proceduremodulelogger.addHandler(proceduremodulehdlr) 
proceduremodulelogger.setLevel(logging.INFO)        

""" --------- module variables ----------"""


""" --------- module methods ------------"""

    
""" --------- classes -------------------"""
#class dbprocedure (object) :
#    def __init__(self,connection,stampobid = False):
#        object.__init__(self)
#
#        # stamp the maximum obid to assist with rollbacks
#        self.connection=connection
#        if self.connection != None and stampobid:
#            stampCursor = connection.cursor()
#            sql = "SELECT last_value FROM ob_obidseq" #Formerly "select max(obid) from ob" but it was WAY too slow!
#            stampCursor.execute(sql)
#            maxobid = stampCursor.fetchone()
#            proceduremodulelogger.info("Form obid stamp : max obid = %s"%maxobid[0])
#            stampCursor.close()
#
#        self.procedureState = {
#            'ERROR' : 0,
#            'MESSAGE' : ''}


def LoadHomologeneAliases(infile):
    """
    This methods processes a file containing records like
3	AU018656
3	Acadm
3	LOC490207
3	ACADM
3	MCAD
3	MCADH
3	ACAD1
5	vlcad
5	ACAD6

    And from this creates ontologies.

    This is step 1 of creating a gene index

    """
    connection=databaseModule.getConnection()    
    reader = open(infile, "rb")
    currentgene = 0
    recordCount = 0
    for record in reader:
        recordCount += 1
        print "processing %s"%record
        fields = re.split('\t',record.strip())

        if len(fields) < 2:
            break

        # for testing
        #if recordCount > 50:
        #    break

        if fields[0] != currentgene:
            # set up new ontology
            ontology = ontologyOb()
            ontology.initNew(connection)
            ontology.databaseFields.update ( {
                'xreflsid' : 'ontology.HOMOLOGENE_ALIASES.%s'%fields[0],
                'ontologyname' : 'Homologene Alias Ontology HGID %s'%fields[0],
                'ontologydescription' : 'Homologene Alias Ontology HGID %s'%fields[0],
                'ontologycomment' : 'This ontology referenced by gene index'
            })
            ontology.insertDatabase(connection)
            currentgene = fields[0]


            # add the URL
            uri = uriOb()
            uri.initNew(connection)
            uri.databaseFields.update(
            {
                'createdby' : 'system',
                'uristring' : 'http://www.ncbi.nlm.nih.gov/entrez/query.fcgi?cmd=Retrieve&db=homologene&dopt=HomoloGene&list_uids=%s'%fields[0],
                'xreflsid' : 'http://www.ncbi.nlm.nih.gov/entrez/query.fcgi?cmd=Retrieve&db=homologene&dopt=HomoloGene&list_uids=%s'%fields[0],
                'visibility' : 'public'
            }
            )
            uri.insertDatabase(connection)
            uri.createLink(connection,ontology.databaseFields['obid'],'Link to NCBI Homologene Record for HGID %s'%fields[0],'system')

        # insert term
        ontology.addTerm(connection,fields[1],False)
        
                
            
                
        #print fields

    reader.close()
    connection.close()
    


def updateHomologeneAliases(infile, update="insert"):
    """
    This methods processes a file containing records like
3	AU018656
3	Acadm
3	LOC490207
3	ACADM
3	MCAD
3	MCADH
3	ACAD1
5	vlcad
5	ACAD6

    And from this will :

    - if the mode is insert , will create newontologies where necessary
    - if the mode is insert , will add terms to existing ontologies if necessary
    

    This is step 1 of creating a gene index

    """
    connection=databaseModule.getConnection()


    # get the existing ontologies
    sql = """
    select
       xreflsid,
       obid
    from
       ontologyob
    where
       xreflsid like 'ontology.HOMOLOGENE_ALIASES.%'
    """
    insertcursor = connection.cursor()
    insertcursor.execute(sql)
    ontologyDict  = dict(insertcursor.fetchall())
    print "loaded %s alias ontologies"%len(ontologyDict)


    # get the existing terms
    sql = """
    select
       o.xreflsid,
       termname
    from
       ontologyob o join ontologytermfact otf on
       otf.ontologyob = o.obid
    where
       o.xreflsid like 'ontology.HOMOLOGENE_ALIASES.%'
    """
    insertcursor = connection.cursor()
    insertcursor.execute(sql)
    ontologyTermDict = {}
    term = insertcursor.fetchone()
    while insertcursor.rowcount == 1:
        if term[0] not in ontologyTermDict:
            ontologyTermDict[term[0]] = [term[1]]
        else:
            ontologyTermDict[term[0]].append(term[1])
        term = insertcursor.fetchone()
    print "loaded %s alias ontology term lists "%len(ontologyTermDict)

    
    reader = open(infile, "rb")
    recordCount = 0
    for record in reader:
        recordCount += 1
        print "processing %s"%record
        fields = re.split('\t',record.strip())

        if len(fields) < 2:
            break

        # for testing
        #if recordCount > 50:
        #    break

        if update == "insert":
            
            # check ontology is in database
            ontologylsid = 'ontology.HOMOLOGENE_ALIASES.%s'%fields[0]
            if ontologylsid not in ontologyDict:
                ontology = ontologyOb()
                ontology.initNew(connection)
                ontology.databaseFields.update ( {
                    'xreflsid' : 'ontology.HOMOLOGENE_ALIASES.%s'%fields[0],
                    'ontologyname' : 'Homologene Alias Ontology HGID %s'%fields[0],
                    'ontologydescription' : 'Homologene Alias Ontology HGID %s'%fields[0],
                    'ontologycomment' : 'This ontology referenced by gene index, loaded as an update from %s'%infile
                })
                ontology.insertDatabase(connection)

                # add the URL
                uri = uriOb()
                uri.initNew(connection)
                uri.databaseFields.update(
                    {
                        'createdby' : 'system',
                        'uristring' : 'http://www.ncbi.nlm.nih.gov/entrez/query.fcgi?cmd=Retrieve&db=homologene&dopt=HomoloGene&list_uids=%s'%fields[0],
                        'xreflsid' : 'http://www.ncbi.nlm.nih.gov/entrez/query.fcgi?cmd=Retrieve&db=homologene&dopt=HomoloGene&list_uids=%s'%fields[0],
                        'visibility' : 'public'
                    }
                )
                uri.insertDatabase(connection)
                uri.createLink(connection,ontology.databaseFields['obid'],'Link to NCBI Homologene Record for HGID %s'%fields[0],'system')

                # insert term
                ontology.addTerm(connection,fields[1],False)

                # update in-memory dictionary of ontologies and terms
                ontologyDict[ontologylsid] = ontology.databaseFields['obid']
                ontologyTermDict[ontologylsid] = [fields[1]]
                

                print "added new homologene %s (%s)"%(tuple(fields))


            else: # we already have this ontology - see if we have the term
                if fields[1] not in ontologyTermDict[ontologylsid]:
                    sql = """
                    insert into ontologytermfact(ontologyob, xreflsid, termname)
                    values(%(ontologyob)s, %(xreflsid)s, %(termname)s)
                    """
                    insertcursor.execute(sql,{
                        'ontologyob' : ontologyDict[ontologylsid],
                        'xreflsid' : '%s.%s'%(ontologylsid,fields[1]),
                        'termname' : fields[1]
                        })
                    connection.commit()

                    print "added alias %s to entry %s"%(fields[1],ontologylsid)
        
        
                
        #print fields

    reader.close()
    connection.close()
    
    

def LoadHomologeneTitles(infile):
    """
    This methods processes a file containing records like
3	acyl-Coenzyme A dehydrogenase, medium chain
3	acyl-Coenzyme A dehydrogenase, C-4 to C-12 straight chain
3	similar to Acyl-CoA dehydrogenase, medium-chain specific, mitochondrial precursor (MCAD)
3	acetyl-Coenzyme A dehydrogenase, medium chain
5	acyl-Coenzyme A dehydrogenase, very long chain

    And from this creates ontologies.

    It is step 2 in the build of a gene index

    """

    
    connection=databaseModule.getConnection()    

    sql = """
    select
       xreflsid,
       obid
    from
       uriob
    """
    insertcursor = connection.cursor()
    insertcursor.execute(sql)
    uridict = dict(insertcursor.fetchall())
    print "retrieved %s uri's"%len(uridict)

    print str(uridict)
    

    reader = open(infile, "rb")
    
    currentgene = 0
    recordCount = 0
    for record in reader:
        recordCount += 1
        print "processing %s"%record
        fields = re.split('\t',record.strip())

        if len(fields) < 2:
            break

        # for testing
        #if recordCount > 50:
        #    break

        if fields[0] != currentgene:
            # set up new ontology
            ontology = ontologyOb()
            ontology.initNew(connection)
            ontology.databaseFields.update ( {
                'xreflsid' : 'ontology.HOMOLOGENE_TITLES.%s'%fields[0],
                'ontologyname' : 'Homologene Titles Ontology HGID %s'%fields[0],
                'ontologydescription' : 'Homologene Titles Ontology HGID %s'%fields[0],
                'ontologycomment' : 'This ontology referenced by gene index'
            })
            ontology.insertDatabase(connection)
            currentgene = fields[0]


            # add the URL
            #uri = uriOb()
            #uri.initFromDatabase('http://www.ncbi.nlm.nih.gov/entrez/query.fcgi?cmd=Retrieve&db=homologene&dopt=HomoloGene&list_uids=%s'%fields[0],connection)
            #uri.createLink(connection,ontology.databaseFields['obid'],'Link to NCBI Homologene Record for HGID %s'%fields[0],'system')

            uri = uridict['http://www.ncbi.nlm.nih.gov/entrez/query.fcgi?cmd=Retrieve&db=homologene&dopt=HomoloGene&list_uids=%s'%fields[0]]
            sql = """
            insert into urilink(uriob,ob,displaystring,createdby)
            values(%(uri)s,%(ob)s,%(displaystring)s,%(createdby)s)
            """
            insertcursor.execute(sql,{
                'uri' : uri,
                'ob' : ontology.databaseFields['obid'],
                'displaystring' : 'Link to NCBI Homologene Record for HGID %s'%fields[0],
                'createdby' : 'system'
            })
            connection.commit()
            


        # insert term
        ontology.addTerm(connection,fields[1],False)
        
                
              
        #print fields

    reader.close()
    connection.close()
    

def updateHomologeneTitles(infile, update="insert"):
    """
    This methods processes a file containing records like
3	acyl-Coenzyme A dehydrogenase, medium chain
3	acyl-Coenzyme A dehydrogenase, C-4 to C-12 straight chain
3	similar to Acyl-CoA dehydrogenase, medium-chain specific, mitochondrial precursor (MCAD)
3	acetyl-Coenzyme A dehydrogenase, medium chain
5	acyl-Coenzyme A dehydrogenase, very long chain

    - if the mode is insert , will create newontologies where necessary
    - if the mode is insert , will add terms to existing ontologies if necessary

    It is step 2 in the build of a gene index

    """    
    connection=databaseModule.getConnection()    

    # get the homologene uri
    sql = """
    select
       xreflsid,
       obid
    from
       uriob
    """
    insertcursor = connection.cursor()
    insertcursor.execute(sql)
    uridict = dict(insertcursor.fetchall())
    print "retrieved %s uri's"%len(uridict)


    # get the existing ontologies
    sql = """
    select
       xreflsid,
       obid
    from
       ontologyob
    where
       xreflsid like 'ontology.HOMOLOGENE_TITLES.%'
    """
    insertcursor = connection.cursor()
    insertcursor.execute(sql)
    ontologyDict  = dict(insertcursor.fetchall())
    print "loaded %s titles ontologies"%len(ontologyDict)


    # get the existing terms
    sql = """
    select
       o.xreflsid,
       termname
    from
       ontologyob o join ontologytermfact otf on
       otf.ontologyob = o.obid
    where
       o.xreflsid like 'ontology.HOMOLOGENE_TITLES.%'
    """
    insertcursor = connection.cursor()
    insertcursor.execute(sql)
    ontologyTermDict = dict([(key,[]) for key in ontologyDict.keys()])
    term = insertcursor.fetchone()
    while insertcursor.rowcount == 1:
        if term[0] not in ontologyTermDict:
            ontologyTermDict[term[0]] = [term[1]]
        else:
            ontologyTermDict[term[0]].append(term[1])
        term = insertcursor.fetchone()
    print "loaded %s titles ontology term lists "%len(ontologyTermDict)


    reader = open(infile, "rb")
    
    currentgene = 0
    recordCount = 0
    ontologylsid = ''
    for record in reader:
        recordCount += 1
        print "processing %s"%record
        fields = re.split('\t',record.strip())

        if len(fields) < 2:
            break

        # for testing
        #if recordCount > 50:
        #    break

        if update == "insert":

            if fields[0] != currentgene:       # if this is the next gene     
                # check ontology is in database
                ontologylsid = 'ontology.HOMOLOGENE_TITLES.%s'%fields[0]
                if ontologylsid not in ontologyDict:
                    ontology = ontologyOb()
                    ontology.initNew(connection)
                    ontology.databaseFields.update ( {
                        'xreflsid' : 'ontology.HOMOLOGENE_TITLES.%s'%fields[0],
                        'ontologyname' : 'Homologene Titles Ontology HGID %s'%fields[0],
                        'ontologydescription' : 'Homologene Titles Ontology HGID %s'%fields[0],
                        'ontologycomment' : 'This ontology referenced by gene index, loaded as an update from %s'%infile
                    })
                    ontology.insertDatabase(connection)

                    # add the URL
                    uri = uridict['http://www.ncbi.nlm.nih.gov/entrez/query.fcgi?cmd=Retrieve&db=homologene&dopt=HomoloGene&list_uids=%s'%fields[0]]
                    sql = """
                    insert into urilink(uriob,ob,displaystring,createdby)
                    values(%(uri)s,%(ob)s,%(displaystring)s,%(createdby)s)
                    """
                    insertcursor.execute(sql,{
                        'uri' : uri,
                        'ob' : ontology.databaseFields['obid'],
                        'displaystring' : 'Link to NCBI Homologene Record for HGID %s'%fields[0],
                        'createdby' : 'system'
                    })
                    connection.commit()

                    # update in-memory dictionary of ontologies and terms
                    ontologyDict[ontologylsid] = ontology.databaseFields['obid']
                    ontologyTermDict[ontologylsid] = []
                
                    print "added new homologene ontology from %s (%s)"%(tuple(fields))

                currentgene = fields[0]

            # if we needed a new ontology we have one - now just process the term                
            if fields[1] not in ontologyTermDict[ontologylsid]:
                sql = """
                insert into ontologytermfact(ontologyob, xreflsid, termname)
                values(%(ontologyob)s, %(xreflsid)s, %(termname)s)
                """
                insertcursor.execute(sql,{
                    'ontologyob' : ontologyDict[ontologylsid],
                    'xreflsid' : '%s.%s'%(ontologylsid,fields[1]),
                    'termname' : fields[1]
                    })
                connection.commit()
                ontologyTermDict[ontologylsid].append(fields[1])
                

                print "added title %s to entry %s"%(fields[1],ontologylsid)
        
    

    reader.close()
    connection.close()





def LoadHomologeneUnigenes(infile):
    """
3	Bt.48936
3	Bt.53582
3	Dr.7343
3	Cfa.1658
3	Hs.445040
3	Mfa.707
3	Mm.10530
3	Omy.9778
3	Omy.23716
3	Ola.5334
3	Oar.4444
3	Rn.6302
3	Ssc.142
3	Ssa.6580
3	Tru.2925
3	Xl.26359
3	Xl.45234
3	Str.51637
5	Bt.48920
5	Cfa.16087
5	Rn.33319
5	Mfa.3443
5	Mfa.3892

    And from this creates ontologies.

    """
    connection=databaseModule.getConnection()
    insertcursor = connection.cursor()


    # get the homologene URI
    sql = """
    select
       xreflsid,
       obid
    from
       uriob
    where
       xreflsid like 'http://www.ncbi.nlm.nih.gov/entrez/query.fcgi?cmd=Retrieve&db=homologene&dopt=HomoloGene%'
    """
    insertcursor.execute(sql)
    homologeneURIDict = dict(insertcursor.fetchall())


    # get the unigene URI
    sql = """
    select
       xreflsid,
       obid
    from
       uriob
    where
       xreflsid like 'http://www.ncbi.nlm.nih.gov/UniGene/clust.cgi?ORG=%'
    """
    insertcursor.execute(sql)
    unigeneURIDict = dict(insertcursor.fetchall())    

    
    
    reader = open(infile, "rb")
    currentgene = 0
    recordCount = 0
    for record in reader:
        recordCount += 1
        print "processing %s"%record
        fields = re.split('\t',record.strip())

        if len(fields) < 2:
            break

        # for testing
        #if recordCount > 100:
        #    break

        if fields[0] != currentgene:
            # set up new ontology
            ontology = ontologyOb()
            ontology.initNew(connection)
            ontology.databaseFields.update ( {
                'xreflsid' : 'ontology.HOMOLOGENE_UNIGENES.%s'%fields[0],
                'ontologyname' : 'Homologene Unigene Ontology HGID %s'%fields[0],
                'ontologydescription' : 'Homologene Unigene Ontology HGID %s'%fields[0],
                'ontologycomment' : 'This ontology referenced by gene index'
            })
            ontology.insertDatabase(connection)
            currentgene = fields[0]

            # link to the URI for the homologene entry
            uri = homologeneURIDict['http://www.ncbi.nlm.nih.gov/entrez/query.fcgi?cmd=Retrieve&db=homologene&dopt=HomoloGene&list_uids=%s'%fields[0]]
            sql = """
            insert into urilink(uriob,ob,displaystring,createdby)
            values(%(uri)s,%(ob)s,%(displaystring)s,%(createdby)s)
            """
            insertcursor.execute(sql,{
                'uri' : uri,
                'ob' : ontology.databaseFields['obid'],
                'displaystring' : 'Link to NCBI Homologene Record for HGID %s'%fields[0],
                'createdby' : 'system'
            })
            connection.commit()

        # insert term
        (termobid,isNew) = ontology.addTerm(connection,fields[1],False)

        # each term is linked to the unigene entry
        tokens = re.split('\.',fields[1])
        unigenelsid = 'http://www.ncbi.nlm.nih.gov/UniGene/clust.cgi?ORG=%s&CID=%s'%tuple(tokens)
        # the uri entry may or may not exist - some unigenes are linked to more than
        # one homologene (?)
        if unigenelsid not in unigeneURIDict:
            uri = uriOb()
            uri.initNew(connection)
            uri.databaseFields.update(
                {
                    'createdby' : 'system',
                    'uristring' : unigenelsid,
                    'xreflsid' : unigenelsid,
                    'visibility' : 'public',
                    'uricomment' : 'Unigene %s'%fields[1]
                }
            )
            uri.insertDatabase(connection)
            connection.commit()
            unigeneURIDict[unigenelsid] = uri.databaseFields['obid']
                
        uri = unigeneURIDict[unigenelsid]
        sql = """
            insert into urilink(uriob,ob,displaystring,createdby)
            values(%(uri)s,%(ob)s,%(displaystring)s,%(createdby)s)
            """
        insertcursor.execute(sql,{
                'uri' : uri,
                'ob' : termobid,
                'displaystring' : 'Link to Unigene %s'%fields[1],
                'createdby' : 'system'
        })
        connection.commit()
                        
        #print fields

    reader.close()
    connection.close()

    




def updateHomologeneUnigenes(infile,update="insert"):
    """
This updates the Unigene ontology from a file fomatted as below.

Before running this you will normally want to delete all the existing unigene
terms.

This is done as follows

1. first check there are no terms using the NCBI and geneid namespaces, apart from 
   the Unigene terms

select 
   ontologytermid
from 
   ontologytermfact2
where
   factnamespace = 'NCBI' and
   attributename = 'geneid'
except
select
   obid
from 
   ontologytermfact 
where
   xreflsid like 'ontology.HOMOLOGENE_UNIGENES%';

2. If this is OK then

delete from ontologytermfact2 where factnamespace = 'NCBI' and attributename = 'geneid';


3. If this is OK then

delete from ontologytermfact2 where  factnamespace = 'NCBI' and attributename = 'geneid'
delete from ontologytermfact where xreflsid like 'ontology.HOMOLOGENE_UNIGENES%';

3	Bt.48936
3	Bt.53582
3	Dr.7343
3	Cfa.1658
3	Hs.445040
3	Mfa.707
3	Mm.10530
3	Omy.9778
3	Omy.23716
3	Ola.5334
3	Oar.4444
3	Rn.6302
3	Ssc.142
3	Ssa.6580
3	Tru.2925
3	Xl.26359
3	Xl.45234
3	Str.51637
5	Bt.48920
5	Cfa.16087
5	Rn.33319
5	Mfa.3443
5	Mfa.3892

    And from this creates ontologies.

    """
    connection=databaseModule.getConnection()
    insertcursor = connection.cursor()


    # get the homologene URI
    sql = """
    select
       xreflsid,
       obid
    from
       uriob
    where
       xreflsid like 'http://www.ncbi.nlm.nih.gov/entrez/query.fcgi?cmd=Retrieve&db=homologene&dopt=HomoloGene%'
    """
    insertcursor.execute(sql)
    homologeneURIDict = dict(insertcursor.fetchall())


    # get the unigene URI
    sql = """
    select
       xreflsid,
       obid
    from
       uriob
    where
       xreflsid like 'http://www.ncbi.nlm.nih.gov/UniGene/clust.cgi?ORG=%'
    """
    insertcursor.execute(sql)
    unigeneURIDict = dict(insertcursor.fetchall())    


    # get the existing ontologies
    sql = """
    select
       xreflsid,
       obid
    from
       ontologyob
    where
       xreflsid like 'ontology.HOMOLOGENE_UNIGENES.%'
    """
    insertcursor = connection.cursor()
    insertcursor.execute(sql)
    ontologyDict  = dict(insertcursor.fetchall())
    print "loaded %s unigenes ontologies"%len(ontologyDict)


    # get the existing terms
    sql = """
    select
       o.xreflsid,
       termname
    from
       ontologyob o join ontologytermfact otf on
       otf.ontologyob = o.obid
    where
       o.xreflsid like 'ontology.HOMOLOGENE_UNIGENES.%'
    """
    insertcursor = connection.cursor()
    insertcursor.execute(sql)
    ontologyTermDict = dict([(key,[]) for key in ontologyDict.keys()])
    term = insertcursor.fetchone()
    while insertcursor.rowcount == 1:
        if term[0] not in ontologyTermDict:
            ontologyTermDict[term[0]] = [term[1]]
        else:
            ontologyTermDict[term[0]].append(term[1])
        term = insertcursor.fetchone()
    print "loaded %s unigenes ontology term lists "%len(ontologyTermDict)

    
    reader = open(infile, "rb")
    currentgene = 0
    recordCount = 0
    ontologylsid = ''
    for record in reader:
        recordCount += 1
        print "processing %s"%record
        fields = re.split('\t',record.strip())

        if len(fields) < 2:
            break

        # for testing
        #if recordCount > 100:
        #    break

        if update == "insert":

            if fields[0] != currentgene:       # if this is the next gene     
                # check ontology is in database
                ontologylsid = 'ontology.HOMOLOGENE_UNIGENES.%s'%fields[0]
                if ontologylsid not in ontologyDict:
        

                    ontology = ontologyOb()
                    ontology.initNew(connection)
                    ontology.databaseFields.update ( {
                        'xreflsid' : 'ontology.HOMOLOGENE_UNIGENES.%s'%fields[0],
                        'ontologyname' : 'Homologene Unigene Ontology HGID %s'%fields[0],
                        'ontologydescription' : 'Homologene Unigene Ontology HGID %s'%fields[0],
                        'ontologycomment' : 'This ontology referenced by gene index'
                    })
                    ontology.insertDatabase(connection)
                    currentgene = fields[0]

                    # link to the URI for the homologene entry
                    uri = homologeneURIDict['http://www.ncbi.nlm.nih.gov/entrez/query.fcgi?cmd=Retrieve&db=homologene&dopt=HomoloGene&list_uids=%s'%fields[0]]
                    sql = """
                    insert into urilink(uriob,ob,displaystring,createdby)
                    values(%(uri)s,%(ob)s,%(displaystring)s,%(createdby)s)
                    """
                    insertcursor.execute(sql,{
                        'uri' : uri,
                        'ob' : ontology.databaseFields['obid'],
                        'displaystring' : 'Link to NCBI Homologene Record for HGID %s'%fields[0],
                        'createdby' : 'system'
                    })
                    connection.commit()

                    # update in-memory dictionary of ontologies and terms
                    ontologyDict[ontologylsid] = ontology.databaseFields['obid']
                    ontologyTermDict[ontologylsid] = []
                
                    print "added new homologene ontology from %s (%s)"%(tuple(fields))
                    

            # if we needed a new ontology we have one - now just process the term                
            if fields[1] not in ontologyTermDict[ontologylsid]:
                sql = """
                insert into ontologytermfact(obid,ontologyob, xreflsid, termname)
                values(%(obid)s,%(ontologyob)s, %(xreflsid)s, %(termname)s)
                """
                termobid = getNewObid(connection)
                insertcursor.execute(sql,{
                    'obid' : termobid,
                    'ontologyob' : ontologyDict[ontologylsid],
                    'xreflsid' : '%s.%s'%(ontologylsid,fields[1]),
                    'termname' : fields[1]
                    })
                connection.commit()
                ontologyTermDict[ontologylsid].append(fields[1])
                

                print "added unigene %s to entry %s"%(fields[1],ontologylsid)

                # each term is linked to the unigene entry
                tokens = re.split('\.',fields[1])
                unigenelsid = 'http://www.ncbi.nlm.nih.gov/UniGene/clust.cgi?ORG=%s&CID=%s'%tuple(tokens)
                # the uri entry may or may not exist - some unigenes are linked to more than
                # one homologene (?)
                if unigenelsid not in unigeneURIDict:
                    uri = uriOb()
                    uri.initNew(connection)
                    uri.databaseFields.update(
                        {
                            'createdby' : 'system',
                            'uristring' : unigenelsid,
                            'xreflsid' : unigenelsid,
                            'visibility' : 'public',
                            'uricomment' : 'Unigene %s'%fields[1]
                        }
                    )
                    uri.insertDatabase(connection)
                    connection.commit()
                    unigeneURIDict[unigenelsid] = uri.databaseFields['obid']
                        
                uri = unigeneURIDict[unigenelsid]
                sql = """
                    insert into urilink(uriob,ob,displaystring,createdby)
                    values(%(uri)s,%(ob)s,%(displaystring)s,%(createdby)s)
                    """
                insertcursor.execute(sql,{
                        'uri' : uri,
                        'ob' : termobid,
                        'displaystring' : 'Link to Unigene %s'%fields[1],
                        'createdby' : 'system'
                })
                connection.commit()
                        
        #print fields

    reader.close()
    connection.close()


def LoadEntrezgeneUnigenes(infile):
    """
This should be run after loading the Unigenes. The file is otained from ftp://ftp.ncbi.nlm.nih.gov/gene/DATA/gene2unigene

It links the Unigenes to Entrez gene ids, which is required for display in the gene index view

1268663	Aga.54
1268672	Aga.79
1268761	Aga.86
1268665	Aga.108
1268433	Aga.201
1275399	Aga.237
1269117	Aga.282
1275208	Aga.762


    """
    speciesToProcess = [ 'Bt','Cfa','Dr','Gga','Hs','Mfa','Mm','Mmu','Oar','Ocu','Ola','Omy','Rn','Ssa','Ssc','Str','Tru','Xl']
    connection=databaseModule.getConnection()
    insertCursor = connection.cursor()
    reader = open(infile, "rb")
    recordCount = 0
    for record in reader:
        recordCount += 1

        if recordCount == 1:
            continue

        if recordCount%100 == 1:
            print "processing %s,%s"%(recordCount,record)
        fields = re.split('\t',record.strip())
        fields = [item.strip() for item in fields]
        species = re.split('\.',fields[1])[0]
        if species not in speciesToProcess:
            continue

        if len(fields) < 2:
            break

        # for testing
        #if recordCount > 20000:
        #    break

        sql = """
        insert into ontologytermfact2 (
        ontologytermid,
        factnamespace,
        attributename,
        attributevalue)
        select
        obid,
        'NCBI',
        'geneid',
        '%s'
        from
        ontologytermfact
        where
        termname = '%s'
        """%tuple(fields)
        
        if recordCount%100 == 1:
            print "executing %s"%sql
        insertCursor.execute(sql)
        connection.commit()
    reader.close()
    connection.close()





def LoadOrUpdateHomologeneDATA(infile):
    """
3	H.sapiens	9606	34	ACADM	NM_000016.2	NP_000007.1
3	C.familiaris	9615	490207		XM_547328.2	XP_547328.2
3	M.musculus	10090	11364	Acadm	NM_007382.1	NP_031408.1
3	R.norvegicus	10116	24158	Acadm	NM_016986.1	NP_058682.1
5	H.sapiens	9606	37	ACADVL	NM_000018.2	NP_000009.1
5	P.troglodytes	9598	455237		XM_511979.1	XP_511979.1
5	C.familiaris	9615	489463		XM_546581.2	XP_546581.2
5	M.musculus	10090	11370	Acadvl	NM_017366.1	NP_059062.1
5	R.norvegicus	10116	25363	Acadvl	NM_012891.1	NP_037023.1
6	H.sapiens	9606	38	ACAT1	NM_000019.2	NP_000010.1
6	C.familiaris	9615	489421		XM_546539.2	XP_546539.2
6	M.musculus	10090	110446	Acat1	NM_144784.2	NP_659033.1
6	R.norvegicus	10116	25014	Acat1	NM_017075.1	NP_058771.1
6	G.gallus	9031	418968		XM_417162.1	XP_417162.1
7	H.sapiens	9606	90	ACVR1	NM_001105.2	NP_001096.1
7	P.troglodytes	9598	470565		XM_525946.1	XP_525946.1
7	C.familiaris	9615	478757		XM_851059.1	XP_856152.1
7	M.musculus	10090	11477	Acvr1	NM_007394.2	NP_031420.2
7	R.norvegicus	10116	79558	Acvr1	NM_024486.1	NP_077812.1

    """

    # create a tax dictionary indexed by the abbreviated name, from the
    # tax dictionary in the globalConf module which looks like
    #taxTable = {     
    #            9606 : {
    #                'taxname' : 'H.sapiens',
    #                'speciesname' : 'Homo sapiens',
    #                'unigeneprefix' : 'Hs',
    #                'sortorder' : 1,
    #                'homologene' : True
    #            },
    # etc
    #
    #speciesTable = dict(zip([globalConf.taxTable['taxid']['taxname'] for taxid in 

    
    
    speciesTable =  {
        'H.sapiens' : 'Homo sapiens',
        'C.familiaris' : 'Canis familiaris',
        'M.musculus' : 'Mus musculus',
        'R.norvegicus' : 'Rattus norvegicus',
        'G.gallus' : 'Gallus gallus',
        'P.troglodytes' : 'Pan troglodytes'
    }


    connection=databaseModule.getConnection()
    insertcursor=connection.cursor()

    # get all NCBI sequences in the database
    sql = """
    select
        xreflsid,
        obid
    from
        biosequenceob
    where
        xreflsid like 'NCBI%'
    """
    insertcursor.execute(sql)
    seqDict = dict(insertcursor.fetchall())

    # get all the entrez gene uri in the database,  
    sql = """
    select
        xreflsid,
        obid
    from
        uriob
    where
        uricomment like 'Entrez geneid%'
    """
    insertcursor.execute(sql)
    geneuriDict = dict(insertcursor.fetchall())

    # get all the genes in the database
    sql = """
    select
        xreflsid,
        obid
    from
        geneticob
    where
        xreflsid like 'geneticob.HGID%'
    """
    insertcursor.execute(sql)
    geneDict = dict(insertcursor.fetchall())

    # get all the ontologies in the database
    sql = """
    select
        xreflsid,
        obid
    from
        ontologyob
    where
        xreflsid like 'ontology.HOMOLOGENE%'
    """
    insertcursor.execute(sql)
    ontologyDict = dict(insertcursor.fetchall())

    # get all the gene product links in the database
    sql = """
    select
       xreflsid
    from
       geneproductlink
    """
    insertcursor.execute(sql)
    geneProductList = insertcursor.fetchall()
    geneProductList = [item[0] for item in geneProductList]


    # get the existing locations of each of the genes
    sql = """
    select
       g.xreflsid as genelsid,
       glf.xreflsid as locationlsid
    from
       geneticlocationfact glf join geneticob g on
       glf.evidence = 'Homologene Homolog' and
       glf.geneticob = g.obid
    """
    insertcursor.execute(sql)
    geneLocationDict = {}
    location = insertcursor.fetchone()
    while insertcursor.rowcount == 1:
        if location[0] not in geneLocationDict:
            geneLocationDict[location[0]] = [location[1]]
        else:
            geneLocationDict[location[0]].append(location[1])
        location = insertcursor.fetchone()
    print "loaded %s location lists "%len(geneLocationDict)
                      
                         
    reader = open(infile, "rb")
    currentgene = 0
    genelsid=""
    recordCount = 0
    for record in reader:
        recordCount += 1
        print "processing %s"%record
        fields = re.split('\t',record.strip())

        if len(fields) < 4:
            break

        # for testing
        #if recordCount > 10000:
        #    break

        # set up the Entrez gene URI implied by this record. It may or may not already exist
        #proceduremodulelogger.info("1 setting up entrez gene")
        entrezgenelsid = 'http://www.ncbi.nlm.nih.gov/entrez/query.fcgi?db=gene&cmd=Retrieve&dopt=full_report&list_uids=%s'%fields[3]
        if entrezgenelsid not in geneuriDict:
            uri = uriOb()
            uri.initNew(connection)
            uri.databaseFields.update(
            {
                    'createdby' : 'system',
                    'uristring' : entrezgenelsid,
                    'xreflsid' : entrezgenelsid,
                    'visibility' : 'public',
                    'uricomment' : 'Entrez geneid %s (%s %s)'%(fields[3],fields[1],fields[4])
            }
            )
            uri.insertDatabase(connection)
            geneuriDict[entrezgenelsid] = uri.databaseFields['obid']


        # get or set up the transcript product
        mrnasequencelsid = 'NCBI.%s'%fields[5]
        mrnasequencename = re.split('\.',fields[5])[0]
        proceduremodulelogger.info("2 setting up sequence")
        if mrnasequencelsid not in seqDict:
            mrnasequence = bioSequenceOb()
            mrnasequence.initNew(connection)
            mrnasequence.databaseFields.update( {
                    'xreflsid' : mrnasequencelsid,
                    'obkeywords' : '%s  %s geneid %s homologene %s'%(mrnasequencename,fields[4],fields[3],fields[0]),
                    'sequencename' : mrnasequencename,
                    'sequencetype' : 'mRNA Reference Sequence',
                    'sequenceurl' : 'http://www.ncbi.nlm.nih.gov/entrez/viewer.fcgi?db=nucleotide&val=%s'%fields[5],
                    'fnindex_accession' : fields[5]
            })
            mrnasequence.insertDatabase(connection)

            seqDict[mrnasequencelsid] = mrnasequence.databaseFields['obid']
            # add a genetic location fact for this gene implied by this record.
            locationFact = geneticLocationFact()
            locationFact.initNew(connection)
            locationFact.databaseFields.update(
            {
                    'biosequenceob' : mrnasequence.databaseFields['obid'],
                    'xreflsid' : 'Entrez Gene.%s'%fields[3],
                    'speciesname' : speciesTable[fields[1]],
                    'speciestaxid' : fields[2],
                    'entrezgeneid' : fields[3],
                    'locusname' : fields[4],
                    'evidence' : 'NCBI Reference Sequence',
                    'voptypeid' : 176
            })
            locationFact.insertDatabase(connection)

            # link this location to entrez gene
            sql = """
            insert into urilink(uriob,ob,displaystring,createdby)
            values(%(uri)s,%(ob)s,%(displaystring)s,%(createdby)s)
            """
            insertcursor.execute(sql,{
                'uri' : geneuriDict[entrezgenelsid],
                'ob' : locationFact.databaseFields['obid'],
                'displaystring' : 'Link to Entrez geneid %s (%s %s)'%(fields[3],fields[1],fields[4]),
                'createdby' : 'system'
            })
            connection.commit()            



        # get or set up the protein product
        protsequencelsid = 'NCBI.%s'%fields[6]
        protsequencename = re.split('\.',fields[6])[0]
        proceduremodulelogger.info("3 setting up sequence")
        if protsequencelsid not in seqDict:
            proteinsequence = bioSequenceOb()
            proteinsequence.initNew(connection)
            proteinsequence.databaseFields.update( {
                    'xreflsid' : protsequencelsid,
                    'obkeywords' : '%s  %s geneid %s homologene %s'%(protsequencename,fields[4],fields[3],fields[0]),
                    'sequencename' : protsequencename,
                    'sequencetype' : 'Protein Reference Sequence',
                    'sequenceurl' : 'http://www.ncbi.nlm.nih.gov/entrez/viewer.fcgi?db=protein&val=%s'%fields[6],
                    'fnindex_accession' : fields[6]
            })
            proteinsequence.insertDatabase(connection)

            seqDict[protsequencelsid] = proteinsequence.databaseFields['obid']
            # add a genetic location fact for this gene implied by this record.
            locationFact = geneticLocationFact()
            locationFact.initNew(connection)
            locationFact.databaseFields.update(
            {
                    'biosequenceob' : proteinsequence.databaseFields['obid'],
                    'xreflsid' : 'Entrez Gene.%s'%fields[3],
                    'speciesname' : speciesTable[fields[1]],
                    'speciestaxid' : fields[2],
                    'entrezgeneid' : fields[3],
                    'locusname' : fields[4],
                    'evidence' : 'NCBI Reference Sequence',
                    'voptypeid' : 176
            })
            locationFact.insertDatabase(connection)

            # link this location to entrez gene
            sql = """
            insert into urilink(uriob,ob,displaystring,createdby)
            values(%(uri)s,%(ob)s,%(displaystring)s,%(createdby)s)
            """
            insertcursor.execute(sql,{
                'uri' : geneuriDict[entrezgenelsid],
                'ob' : locationFact.databaseFields['obid'],
                'displaystring' : 'Link to Entrez geneid %s (%s %s)'%(fields[3],fields[1],fields[4]),
                'createdby' : 'system'
            })
            connection.commit()            

        

        if fields[0] != currentgene:
            
            # create the gene entry if necessary. Note that we include storing the human symbol and this is based on
            # the ordering of the file whereby the human symbol comes first
            proceduremodulelogger.info("4 setting up gene")
            genelsid = 'geneticob.HGID.%s'%fields[0]

            if genelsid not in geneDict:
                gene = geneticOb()
                gene.initNew(connection)
                gene.databaseFields.update( {
                    'xreflsid' : genelsid,
                    'createdby' : 'system',
                    'obkeywords' : 'gene index homologene %s %s'%(fields[0],fields[4]),
                    'geneticobname' : 'Homologene %s %s'%(fields[0],fields[4]),
                    'geneticobtype' : 'Homologene',
                    'geneticobsymbols' : fields[4],
                    'geneticobdescription' : 'Gene Index Homologene %s %s'%(fields[0],fields[4]),
                    'obcomment' : 'Added as part of Gene Index bootstrap from homologene.build55.1.DATA'
                })
                gene.insertDatabase(connection)
                currentgene = fields[0]
                geneDict[genelsid] = gene.databaseFields['obid']
                geneLocationDict[genelsid] = []
            

                # set up the nomenclature links to the unigene, titles and aliases ontologies
                # aliases : 
                aliaseslsid = 'ontology.HOMOLOGENE_ALIASES.%s'%fields[0]
                updatedict = {
                    'linklsid' : 'nomenclaturelink.geneticob.HG aliases.%s'%fields[0],
                    'geneticobid' : geneDict[genelsid],
                    'ontologyobid' : ontologyDict[aliaseslsid],
                    'predicatecomment' : 'Link to aliases ontology for homologene %s'%fields[0]
                }
                sql = """
                    insert into predicatelink(
                    xreflsid  ,
                    voptypeid  ,
                    subjectob  ,
                    objectob   ,
                    predicate  ,
                    predicatecomment )
                    values ( %(linklsid)s,355,%(geneticobid)s,%(ontologyobid)s,
                    'PROVIDES_NOMENCLATURE',%(predicatecomment)s )
                """
                print sql%updatedict
                proceduremodulelogger.info("6 linking ontology")
                insertcursor.execute(sql,updatedict)
                connection.commit()


                # titles : 
                titleslsid = 'ontology.HOMOLOGENE_TITLES.%s'%fields[0]
                updatedict = {
                    'linklsid' : 'nomenclaturelink.geneticob.HG titles.%s'%fields[0],
                    'geneticobid' : geneDict[genelsid],
                    'ontologyobid' : ontologyDict[titleslsid],
                    'predicatecomment' : 'Link to titles ontology for homologene %s'%fields[0]
                }
                sql = """
                    insert into predicatelink(
                    xreflsid  ,
                    voptypeid  ,
                    subjectob  ,
                    objectob   ,
                    predicate  ,
                    predicatecomment )
                    values ( %(linklsid)s,355,%(geneticobid)s,%(ontologyobid)s,
                    'PROVIDES_NOMENCLATURE',%(predicatecomment)s )
                """
                print sql%updatedict
                proceduremodulelogger.info("6 linking ontology")
                insertcursor.execute(sql,updatedict)
                connection.commit()


                # unigenes :
                # the unigene may not have been set up yet  - some seem to be missing 
                unigeneslsid = 'ontology.HOMOLOGENE_UNIGENES.%s'%fields[0]
                if unigeneslsid in ontologyDict:
                    updatedict = {
                        'linklsid' : 'nomenclaturelink.geneticob.HG unigenes.%s'%fields[0],
                        'geneticobid' : geneDict[genelsid],
                        'ontologyobid' : ontologyDict[unigeneslsid],
                        'predicatecomment' : 'Link to unigenes ontology for homologene %s'%fields[0]
                    }
                    sql = """
                        insert into predicatelink(
                        xreflsid  ,
                        voptypeid  ,
                        subjectob  ,
                        objectob   ,
                        predicate  ,
                        predicatecomment )
                        values ( %(linklsid)s,355,%(geneticobid)s,%(ontologyobid)s,
                        'PROVIDES_NOMENCLATURE',%(predicatecomment)s )
                    """
                    print sql%updatedict
                    proceduremodulelogger.info("6 linking ontology")
                    insertcursor.execute(sql,updatedict)
                    connection.commit()
                else:
                    print "Warning : Unigene ontology %s is missing"%unigeneslsid


                # add the canonical symbol fact. This relies on the fact that we know this gene
                # will be the human locus - i.e. this locus occurs first in the file
                if len(fields[4]) > 0:
                    updatedict.update (
                        {
                            'geneticobid' : geneDict[genelsid],
                            'xreflsid' : '%s.symbol'%genelsid,
                            'locusname' : fields[4]
                        }
                    )
                    proceduremodulelogger.info("11 adding fact ")
                    sql = """
                    insert into geneticfact(geneticob,xreflsid, factnamespace,attributename,attributevalue)
                    values(%(geneticobid)s,%(xreflsid)s,'Nomenclature','Canonical Symbol',%(locusname)s)
                    """
                    insertcursor.execute(sql,updatedict)
                # end block setting up new gene
        


        ############### end of block setting up the new gene record ########################            

        # add the gene transcript product links if not there

        proceduremodulelogger.info("12 adding productlink ")
        splicedLinkLSID = '%s.%s'%(genelsid,mrnasequencename)
        if splicedLinkLSID not in geneProductList:
            sql = """
                insert into geneProductLink(geneticob,biosequenceob,xreflsid,
                producttype,evidence)
                values(%(geneticob)s,%(biosequenceob)s,%(xreflsid)s,
                %(producttype)s,%(evidence)s)
            """
            insertcursor.execute(sql,{
                'geneticob' : geneDict[genelsid],
                'biosequenceob' : seqDict[mrnasequencelsid],
                'xreflsid' : splicedLinkLSID ,
                'producttype' : 'spliced transcript',
                'evidence' : 'NCBI Refseq'
            })
            connection.commit()
            geneProductList.append(splicedLinkLSID)

        
        
        # add the protein product link if not there
        proceduremodulelogger.info("13 adding productlink ")
        proteinLinkLSID = '%s.%s'%(genelsid,protsequencename)
        if proteinLinkLSID not in geneProductList:
            sql = """
                insert into geneProductLink(geneticob,biosequenceob,xreflsid,
                producttype,evidence)
                values(%(geneticob)s,%(biosequenceob)s,%(xreflsid)s,
                %(producttype)s,%(evidence)s)
            """
            insertcursor.execute(sql,{
                'geneticob' : geneDict[genelsid],
                'biosequenceob' : seqDict[protsequencelsid],
                'xreflsid' : proteinLinkLSID ,
                'producttype' : 'protein',
                'evidence' : 'NCBI Refseq'
            })
            connection.commit()
            geneProductList.append(proteinLinkLSID)
                    
                

        # add a genetic location fact for this gene implied by this record, if we do not already have such a link
        locationlsid = 'Entrez Gene.%s'%fields[3]

        # sometimes need to update the dictionary of locations, e.g. if have restarted
        # or for some reason there was not existing location for the gene
        if genelsid not in geneLocationDict:
            geneLocationDict[genelsid] = []

        if locationlsid not in geneLocationDict[genelsid]:
            locationFact = geneticLocationFact()
            locationFact.initNew(connection)
            locationFact.databaseFields.update(
            {
                'geneticob' : geneDict[genelsid],
                'xreflsid' : 'Entrez Gene.%s'%fields[3],
                'speciesname' : speciesTable[fields[1]],
                'speciestaxid' : fields[2],
                'entrezgeneid' : fields[3],
                'locusname' : fields[4],
                'evidence' : 'Homologene Homolog'
            })
            proceduremodulelogger.info("15 adding location fact ")
            locationFact.insertDatabase(connection)

            geneLocationDict[genelsid].append(locationlsid)



            # link this location to entrez gene
            sql = """
            insert into urilink(uriob,ob,displaystring,createdby)
            values(%(uri)s,%(ob)s,%(displaystring)s,%(createdby)s)
            """
            insertcursor.execute(sql,{
                'uri' : geneuriDict[entrezgenelsid],
                 'ob' : locationFact.databaseFields['obid'],
                'displaystring' : 'Link to Entrez geneid %s (%s %s)'%(fields[3],fields[1],fields[4]),
                'createdby' : 'system'
            })
            connection.commit()                   
 


    reader.close()
    connection.close()



def linkSpotToGeneSymbol(arraylsid,inputfile,fileKeyDetails= {"column" : "probe set id", "regexp" : None}, \
                                              dbKeyDetails={"column" : "xreflsid", "regexp" : "^Affymetrix\.Bovine Genome Array\.(.+)$"},\
                                              fileSymbolDetails={"column" : "gene symbol or accession", "regexp" : None},\
                                              geneFactColumns = ["gene title"],
                                              fieldnamesrow=1,datastartsrow=3,creategenes=True):
        """ Example input data :
Probe Set ID	GeneChip Array	Species Scientific Name	Annotation Date	Sequence Type	Sequence Source	Transcript ID(Array Design)	Target Description	Representative Public ID	Archival UniGene Cluster	UniGene ID	Genome Version	Alignments	Gene Title	Gene Symbol	Chromosomal Location	Unigene Cluster Type	Ensembl	Entrez Gene	SwissProt	EC	OMIM	RefSeq Protein ID	RefSeq Transcript ID	FlyBase	AGI	WormBase	MGI Name	RGD Name	SGD accession number	Gene Ontology Biological Process	Gene Ontology Cellular Component	Gene Ontology Molecular Function	Pathway	Protein Families	Protein Domains	InterPro	Trans Membrane	QTL	Annotation Description	Annotation Transcript Cluster	Transcript Assignments	Annotation Notes	Best Accession	Gene Symbol or Accession 	Source
Bt.28446.1.A1_at	Bovine Array	Bos taurus	Jul 12, 2006	Consensus sequence	GenBank	Bt.28446.1	gb:U73392.1 /DB_XREF=gi:1657896 /TID=Bt.28446.1 /CNT=2 /FEA=mRNA /TIER=ConsEnd /STK=0 /UG=Bt.28446 /UG_TITLE=T cell receptor delta chain variable region precursor (BVd1.25) mRNA, partial cds /DEF=Bos taurus T cell receptor delta chain variable region precursor (BVd1.25) mRNA, partial cds.	U73392.1	Bt.28446	Bt.28446			T cell receptor delta chain variable region	BVd1.25				407200	---											---	---	---							This probe set was annotated using the Accession mapped clusters based pipeline to a Entrez Gene identifier using 1 transcripts. // false // Accession mapped clusters // E	U73392	U73392 // /DEF=Bos taurus T cell receptor delta chain variable region precursor (BVd1.25) mRNA, partial cds. // gb // --- // ---	XM_868104 // refseq // 4 // Negative Strand Matching Probes /// XM_864808 // refseq // 11 // Negative Strand Matching Probes /// ENSBTAT00000031700 // ensembl_transcript // 4 // Negative Strand Matching Probes /// ENSBTAT00000033285 // ensembl_transcript // 11 // Negative Strand Matching Probes /// GENSCAN00000037017 // ensembl_prediction // 4 // Negative Strand Matching Probes /// GENSCAN00000022315 // ensembl_prediction // 11 // Negative Strand Matching Probes	1401240A	1401240A	Unigene - Human
Bt.28446.1.S1_x_at	Bovine Array	Bos taurus	Jul 12, 2006	Consensus sequence	GenBank	Bt.28446.1	gb:U73392.1 /DB_XREF=gi:1657896 /TID=Bt.28446.1 /CNT=2 /FEA=mRNA /TIER=ConsEnd /STK=0 /UG=Bt.28446 /UG_TITLE=T cell receptor delta chain variable region precursor (BVd1.25) mRNA, partial cds /DEF=Bos taurus T cell receptor delta chain variable region precursor (BVd1.25) mRNA, partial cds.	U73392.1	Bt.28446	Bt.28446			T cell receptor delta chain variable region	BVd1.25			ENSBTAG00000024121	407200	---											---	---	---				IPR002035 // von Willebrand factor, type A // 8.6E-29 ///  //  // 6.8E-12			This probe set was annotated using the Matching Probes based pipeline to a Entrez Gene identifier using 1 transcripts. // false // Matching Probes // A	U73392(11)	U73392 // Bos taurus T cell receptor delta chain variable region precursor (BVd1.25) mRNA, partial cds. // gb // 11 // --- /// XM_864808 // PREDICTED: Bos taurus similar to T-cell receptor alpha chain V region HPB-MLT precursor (LOC613744), mRNA. // refseq // 10 // --- /// ENSBTAT00000033285 // cdna:novel scaffold:Btau_2.0:ChrUn.6643:3999:4561:1 gene:ENSBTAG00000024121 // ensembl_transcript // 10 // --- /// GENSCAN00000022315 // cdna:Genscan scaffold:Btau_2.0:ChrUn.6643:4005:4723:1 // ensembl_prediction // 10 // ---	XM_868104 // refseq // 6 // Cross Hyb Matching Probes /// XM_583486 // refseq // 1 // Cross Hyb Matching Probes /// XM_608984 // refseq // 1 // Cross Hyb Matching Probes /// ENSBTAT00000001488 // ensembl_transcript // 1 // Cross Hyb Matching Probes /// ENSBTAT00000031700 // ensembl_transcript // 6 // Cross Hyb Matching Probes /// ENSBTAT00000031147 // ensembl_transcript // 1 // Cross Hyb Matching Probes /// GENSCAN00000122524 // ensembl_prediction // 1 // Cross Hyb Matching Probes /// GENSCAN00000037017 // ensembl_prediction // 6 // Cross Hyb Matching Probes /// GENSCAN00000064344 // ensembl_prediction // 1 // Cross Hyb Matching Probes	1401240A	1401240A	Unigene - Human
Bt.29690.1.A1_at	Bovine Array	Bos taurus	Jul 12, 2006	Consensus sequence	GenBank	Bt.29690.1	gb:U73386.1 /DB_XREF=gi:1657884 /TID=Bt.29690.1 /CNT=1 /FEA=mRNA /TIER=ConsEnd /STK=0 /UG=Bt.29690 /UG_TITLE=T cell receptor delta chain variable region precursor (BVd1.19) mRNA, partial cds /DEF=Bos taurus T cell receptor delta chain variable region precursor (BVd1.19) mRNA, partial cds.	U73386.1	Bt.29690	Bt.29690			T cell receptor delta chain variable region	BVd1.19				407203	---			XP_598882.2	XM_598882							---	---	---	---	---	---	---	---	---	This probe set was annotated using the Accession mapped clusters based pipeline to a Entrez Gene identifier using 1 transcripts. // false // Accession mapped clusters // E	U73386	U73386 // /DEF=Bos taurus T cell receptor delta chain variable region precursor (BVd1.19) mRNA, partial cds. // gb // --- // ---	XM_598882 // refseq // 11 // Negative Strand Matching Probes /// XM_868180 // refseq // 1 // Negative Strand Matching Probes /// ENSBTAT00000001487 // ensembl_transcript // 11 // Negative Strand Matching Probes /// ENSBTAT00000003677 // ensembl_transcript // 11 // Negative Strand Matching Probes /// ENSBTAT00000035228 // ensembl_transcript // 2 // Negative Strand Matching Probes /// ENSBTAT00000040367 // ensembl_transcript // 2 // Negative Strand Matching Probes /// GENSCAN00000016640 // ensembl_prediction // 11 // Negative Strand Matching Probes /// GENSCAN00000028639 // ensembl_prediction // 1 // Negative Strand Matching Probes	1401240A	1401240A	Unigene - Human
Bt.29690.1.S1_at	Bovine Array	Bos taurus	Jul 12, 2006	Consensus sequence	GenBank	Bt.29690.1	gb:U73386.1 /DB_XREF=gi:1657884 /TID=Bt.29690.1 /CNT=1 /FEA=mRNA /TIER=ConsEnd /STK=0 /UG=Bt.29690 /UG_TITLE=T cell receptor delta chain variable region precursor (BVd1.19) mRNA, partial cds /DEF=Bos taurus T cell receptor delta chain variable region precursor (BVd1.19) mRNA, partial cds.	U73386.1	Bt.29690	Bt.29690			T cell receptor delta chain variable region	BVd1.19			ENSBTAG00000027922	407203	---			XP_598882.2	XM_598882							---	---	---	---	---	---	IPR008160 // Collagen triple helix repeat // 3.0E-11 /// IPR008160 // Collagen triple helix repeat // 3.5E-14 /// IPR008160 // Collagen triple helix repeat // 5.6E-5 /// IPR008160 // Collagen triple helix repeat // 4.1E-15 /// IPR008160 // Collagen triple helix repeat // 2.4E-13 /// IPR008160 // Collagen triple helix repeat // 3.6E-7 /// IPR007872 // CSL zinc finger // 2.7E-32 /// IPR000024 // Frizzled CRD region // 1.5E-53 /// IPR000834 // Peptidase M14, carboxypeptidase A // 4.2E-41 /// IPR000834 // Peptidase M14, carboxypeptidase A // 1.2E-11 /// IPR008575 // Peptidase M14B // 4.5E-63	---	---	This probe set was annotated using the Matching Probes based pipeline to a Entrez Gene identifier using 1 transcripts. // false // Matching Probes // A	XM_598882(11)	XM_598882 // PREDICTED: Bos taurus T cell receptor delta chain variable region (BVd1.19), partial mRNA. // refseq // 11 // --- /// ENSBTAT00000001487 // cdna:novel scaffold:Btau_2.0:ChrUn.13594:1634:7219:-1 gene:ENSBTAG00000027922 // ensembl_transcript // 11 // --- /// ENSBTAT00000003677 // cdna:novel scaffold:Btau_2.0:ChrUn.13594:1634:2203:-1 gene:ENSBTAG00000027922 // ensembl_transcript // 11 // --- /// GENSCAN00000016640 // cdna:Genscan scaffold:Btau_2.0:ChrUn.13594:1490:2441:-1 // ensembl_prediction // 11 // ---	XM_868180 // refseq // 1 // Cross Hyb Matching Probes /// ENSBTAT00000035228 // ensembl_transcript // 1 // Cross Hyb Matching Probes /// ENSBTAT00000040367 // ensembl_transcript // 1 // Cross Hyb Matching Probes /// GENSCAN00000028639 // ensembl_prediction // 1 // Cross Hyb Matching Probes	1401240A	1401240A	Unigene - Human
Bt.29691.1.A1_at	Bovine Array	Bos taurus	Jul 12, 2006	Consensus sequence	GenBank	Bt.29691.1	gb:U73383.1 /DB_XREF=gi:1657878 /TID=Bt.29691.1 /CNT=2 /FEA=mRNA /TIER=ConsEnd /STK=0 /UG=Bt.29691 /UG_TITLE=T cell receptor delta chain variable region precursor (BVd1.18) mRNA, partial cds /DEF=Bos taurus T cell receptor delta chain variable region precursor (BVd1.16) mRNA, partial cds.	U73383.1	Bt.29691	Bt.29691			T cell receptor delta chain variable region	BVd1.18				407204	---			XP_588656.2	XM_588656							---	---	---	---	---	---	---	---	---	This probe set was annotated using the Accession mapped clusters based pipeline to a Entrez Gene identifier using 1 transcripts. // false // Accession mapped clusters // E	U73385	U73385 // /DEF=Bos taurus T cell receptor delta chain variable region precursor (BVd1.18) mRNA, partial cds. // gb // --- // ---	XM_871305 // refseq // 6 // Negative Strand Matching Probes /// XM_588656 // refseq // 11 // Negative Strand Matching Probes /// ENSBTAT00000037480 // ensembl_transcript // 6 // Negative Strand Matching Probes /// ENSBTAT00000031250 // ensembl_transcript // 11 // Negative Strand Matching Probes /// GENSCAN00000045690 // ensembl_prediction // 5 // Negative Strand Matching Probes	1401240A	1401240A	Unigene - Human


Example record to link to :

Affymetrix.Bovine Genome Array.Bt.365.1.S1_at

        """

        connection=databaseModule.getConnection()
        insertCursor=connection.cursor()
        reader =csv.reader(file(inputfile))

        # get the spots
        sql = """
        select msf.%s as accession, msf.obid  from
        microarrayspotfact msf join labresourceob lr on
        msf.labresourceob = lr.obid and
        lr.xreflsid = '%s'
        """%(dbKeyDetails["column"],arraylsid)
        proceduremodulelogger.info("running %s"%sql)
        insertCursor.execute(sql)
        spots=insertCursor.fetchall()

        # make a dictionary with the accession as key (after any regexp processing required), and a list of all obids matching that accession
        # as value , as there will in general be replicates
        spotDict = {}
        for (accession,obid) in spots:

            # if there is a regexp to extract the key , use it
            spotKey = accession
            if dbKeyDetails["regexp"] != None:
                parseresult = re.search(dbKeyDetails["regexp"],accession)
                if parseresult == None:
                    raise brdfException("error parsing %s using %s, giving up on import"%(accession,dbKeyDetails["regexp"] ))
                else:
                    if len(parseresult.groups()) > 0:
                        spotKey = parseresult.groups()[0]
                    else:
                        raise brdfException("error parsing %s using %s, giving up on import"%(accession,dbKeyDetails["regexp"] ))

            if spotKey not in spotDict:
                spotDict[spotKey] = [obid]
            else:
                spotDict[spotKey].append(obid)
           
        proceduremodulelogger.info("retrieved %s spots"%len(spotDict))
        print "example rows"
        for key in spotDict.keys()[0:50]:
            print "%s : %s"%(key,spotDict[key])

        # get the ontology terms, and the genes they are linked to
        sql = """
        select
           upper(otf.termname) as symbol,
           p.subjectob as geneobid,
           g.xreflsid as genelsid
        from
           (ontologytermfact otf join predicatelink p on
           otf.xreflsid like 'ontology.HOMOLOGENE_ALIASES%' and
           p.predicate = 'PROVIDES_NOMENCLATURE' and
           p.objectob = otf.ontologyob) join geneticob g on
           g.obid = p.subjectob
        """
        proceduremodulelogger.info("running %s"%sql)
        insertCursor.execute(sql)
        terms = insertCursor.fetchall()
        # make a dictionary with the term as key, and a list of all genes matching that term
        # as value , as there will unfortunately be terms that link to more than one gene
        termDict = {}
        for (term,obid,lsid) in terms:
            if term not in termDict:
                termDict[term] = [(obid,lsid)]
            else:
                if (obid,lsid) not in termDict[term]:
                    termDict[term].append((obid,lsid))


        # add ontology terms, from the non-homologene ontologies
        sql = """
        select
           upper(otf.termname) as symbol,
           p.subjectob as geneobid,
           g.xreflsid as genelsid
        from
           (ontologytermfact otf join predicatelink p on
           otf.xreflsid like 'ontology.GENEINDEX_ALIASES%' and
           p.predicate = 'PROVIDES_NOMENCLATURE' and
           p.objectob = otf.ontologyob) join geneticob g on
           g.obid = p.subjectob
        """
        proceduremodulelogger.info("running %s"%sql)
        insertCursor.execute(sql)
        terms = insertCursor.fetchall()
        for (term,obid,lsid) in terms:
            if term not in termDict:
                termDict[term] = [(obid,lsid)]
            else:
                if (obid,lsid) not in termDict[term]:
                    termDict[term].append((obid,lsid))
              
        
        proceduremodulelogger.info("retrieved %s terms"%len(termDict))
        print "example rows"
        for key in termDict.keys()[0:50]:
            print "%s : %s"%(key,termDict[key])


        #for row in reader:
        rowCount = 0
        linkedCount = 0
        geneCount = 0
        linkednames =[]
        for row in reader:
            rowCount += 1

            # get the column headings
            if rowCount == fieldnamesrow:
                fieldNames = [name.lower().strip() for name in row]
                print "Field names : %s"%fieldNames
                continue
            elif  rowCount >= datastartsrow:
                fieldDict = dict(zip(fieldNames,[item.strip() for item in row]))
            else:
                continue

            print fieldDict

            if fieldDict[fileSymbolDetails["column"]] == None:
                continue

            if len(fieldDict[fileSymbolDetails["column"]]) == 0:
                continue

            if re.search('^[\-]+$',fieldDict[fileSymbolDetails["column"]]) != None:
                continue            

            # make the symbol we need to find upper case
            symbolKey = fieldDict[fileSymbolDetails["column"]].upper()

            if fieldDict[fileKeyDetails["column"]] == None:
                continue

            if len(fieldDict[fileKeyDetails["column"]]) == 0:
                continue            

            if fieldDict[fileKeyDetails["column"]] in linkednames:
               continue

            # if we need to parse the key in the file then do so
            spotKey = fieldDict[fileKeyDetails["column"]]
            if fileKeyDetails["regexp"] != None:
                parseresult = re.search(fileKeyDetails["regexp"],spotKey)
                if parseresult == None:
                    raise brdfException("error parsing %s using %s, giving up on import"%(spotKey,fileKeyDetails["regexp"] ))
                else:
                    if len(parseresult.groups()) > 0:
                        spotKey = parseresult.groups()[0]
                    else:
                        raise brdfException("error parsing %s using %s, giving up on import"%(spotKey,fileKeyDetails["regexp"] ))            


            # check we can find the spot
            if spotKey not in spotDict:
                print "warning - could not find spot with name %s"%spotKey
                continue

            if spotKey in linkednames:
               continue
            
            
            
            # find a gene by looking up the symbol- if not found then create
            # if not found , insert gene                
            if symbolKey not in termDict:
                if not creategenes:
                    print "Warning : could not find gene %s (and not creating genes)"%symbolKey
                    continue
                else:
                    print "Warning : could not find gene for alias %s and creategenes set so creating new gene "%symbolKey                    
                    gene = geneticOb()
                    gene.initNew(connection)
                    gene.databaseFields.update({
                        "xreflsid" : "geneticob.%s"%fieldDict[fileSymbolDetails["column"]],
                        "obkeywords" : fieldDict[fileSymbolDetails["column"]],
                        "geneticobname" : fieldDict[fileSymbolDetails["column"]],
                        "geneticobdescription" : fieldDict[geneFactColumns[0]],
                        "geneticobtype" : "Homologene",
                        "geneticobsymbols" : fieldDict[fileSymbolDetails["column"]],
                        "obcomment" : "Added by linkSpotToGeneSymbol procedure, for missing gene"
                    })
                    print "\n\ncreating new gene %s %s"%(fieldDict[fileSymbolDetails["column"]],fieldDict[geneFactColumns[0]])
                    gene.insertDatabase(connection)
                    geneCount += 1


                    # create aliases ontology
                    ontology = ontologyOb()
                    ontologylsid = 'ontology.GENEINDEX_ALIASES.%s'%fieldDict[fileSymbolDetails["column"]]
                    ontology.initNew(connection)
                    ontology.databaseFields.update ( {
                        'xreflsid' : ontologylsid,
                        'ontologyname' : 'Gene Index Alias Ontology %s'%fieldDict[fileSymbolDetails["column"]],
                        'ontologydescription' : 'Gene Index Alias Ontology %s'%fieldDict[fileSymbolDetails["column"]],
                        'ontologycomment' : 'This ontology referenced by gene index, loaded as an update from %s'%inputfile
                    })
                    ontology.insertDatabase(connection)


                    # insert term
                    ontology.addTerm(connection,fieldDict[fileSymbolDetails["column"]],False)


                    # nomenclature link
                    updatedict = {
                        'linklsid' : 'nomenclaturelink.geneticob.Gene Index aliases.%s'%fieldDict[fileSymbolDetails["column"]],
                        'geneticobid' : gene.databaseFields['obid'],
                        'ontologyobid' : ontology.databaseFields['obid'],
                        'predicatecomment' : 'Link to aliases ontology for gene index entry %s'%fieldDict[fileSymbolDetails["column"]]
                    }
                    sql = """
                        insert into predicatelink(
                        xreflsid  ,
                        voptypeid  ,
                        subjectob  ,
                        objectob   ,
                        predicate  ,
                        predicatecomment )
                        values ( %(linklsid)s,355,%(geneticobid)s,%(ontologyobid)s,
                        'PROVIDES_NOMENCLATURE',%(predicatecomment)s )
                    """
                    print sql%updatedict
                    insertCursor.execute(sql,updatedict)
                    connection.commit()

                    # create titles ontology 
                    ontologylsid = 'ontology.GENEINDEX_TITLES.%s'%fieldDict[fileSymbolDetails["column"]]
                    ontology = ontologyOb()                    
                    ontology.initNew(connection)
                    ontology.databaseFields.update ( {
                        'xreflsid' : ontologylsid,
                        'ontologyname' : 'Gene Index Titles Ontology %s'%fieldDict[fileSymbolDetails["column"]],
                        'ontologydescription' : 'Gene Index Titles Ontology %s'%fieldDict[fileSymbolDetails["column"]],
                        'ontologycomment' : 'This ontology referenced by gene index, loaded as an update from %s'%inputfile
                    })
                    ontology.insertDatabase(connection)


                    # insert term
                    ontology.addTerm(connection,fieldDict[geneFactColumns[0]],False)

                    # nomenclature link
                    updatedict = {
                        'linklsid' : 'nomenclaturelink.geneticob.Gene Index titles.%s'%fieldDict[fileSymbolDetails["column"]],
                        'geneticobid' : gene.databaseFields['obid'],
                        'ontologyobid' : ontology.databaseFields['obid'],
                        'predicatecomment' : 'Link to titles ontology for gene index entry %s'%fieldDict[fileSymbolDetails["column"]]
                    }
                    sql = """
                        insert into predicatelink(
                        xreflsid  ,
                        voptypeid  ,
                        subjectob  ,
                        objectob   ,
                        predicate  ,
                        predicatecomment )
                        values ( %(linklsid)s,355,%(geneticobid)s,%(ontologyobid)s,
                        'PROVIDES_NOMENCLATURE',%(predicatecomment)s )
                    """
                    print sql%updatedict
                    insertCursor.execute(sql,updatedict)
                    connection.commit()

                    # update in-memory term dictionary so we don't create it again

                    
                    termDict[symbolKey] = [(gene.databaseFields['obid'],gene.databaseFields['xreflsid'])]
                    # we do not have enough informationin the types of file currently processed by this , to
                    # include any location info for this gene

                
            # set up predicate link between the spot and each gene associated with this term
            for gene in termDict[symbolKey]:
                for spot in spotDict[spotKey]:
                    predicateDetails = {
                        'xreflsid' : "%s.%s"%(gene[1],spotKey),
                        'voptypeid' : 375,
                        'subjectob' : spot,
                        'objectob' : gene[0],
                        'predicate' : 'ARRAYSPOT-GENE'
                    }
                    
                    sql = """
                        insert into predicatelink(
                        xreflsid,
                        voptypeid,
                        subjectob,
                        objectob,
                        predicate)
                        values (
                        %(xreflsid)s,
                        %(voptypeid)s,
                        %(subjectob)s,
                        %(objectob)s,
                        %(predicate)s)"""
                    print "executing %s"%(sql%predicateDetails)
                    insertCursor.execute(sql,predicateDetails)
                    connection.commit();
                    linkedCount += 1

            linkednames.append(spotKey)

        insertCursor.close()
        connection.close()
        print "row count = %s, new gene count = %s, linked count = %s "%(rowCount, geneCount, linkedCount)

    




def loadGeneinfo(infile,producttype):
    """

    Load genes and geneinfo from a file like this :
    
 c.dbxref, geneid, taxid,symbol,synonyms,chromosome,map_location,description,type_of_gene

 - assumed sorted by geneid

 e.g. from this query :

 select
 geneid, c.dbxref, taxid,symbol,synonyms,chromosome,map_location,description,type_of_gene
from 
 pubstore.geneinfo g, cohort c
where 
 c.cohortid = 10156 and 
 g.geneid = pubplsqlutils.getgeneidfromaccession(c.dbxref,10)
order by 
 geneid

    """


    connection=databaseModule.getConnection()
    insertcursor = connection.cursor()

    # retrieve the sequences to link to
    sql = """
    select
        sequencename,
        obid
    from
        biosequenceob
    where
        xreflsid like 'NCBI%'
    """
    insertcursor.execute(sql)
    seqDict = dict(insertcursor.fetchall())

    # retrieve all the genes
    sql = """
    select
        xreflsid,
        obid
    from
        geneticob
    """
    insertcursor.execute(sql)
    geneDict = dict(insertcursor.fetchall())
                
    reader = csv.reader(open(infile, "rb"))
    
    rowcount = 1
    fieldNames = [ "geneid", "dbxref", "taxid","symbol","synonyms","chromosome","map_location","description","type_of_gene"]

    currentgene = ""
    for row in reader:

        fieldDict = dict(zip(fieldNames,row))

        genelsid = "NCBI.%(geneid)s"%fieldDict

        # if we have a new gene create it, else retrieve it
        if genelsid not in geneDict:
                
            currentGene = geneticOb()
            currentGene.initNew(connection)
            currentGene.databaseFields.update( {
                    'xreflsid': genelsid,
                    'obkeywords' : string.lower(string.join([fieldDict['symbol']] + string.split(fieldDict['synonyms'],'|'),' ')),
                    'geneticobname' : fieldDict['symbol'],
                    'geneticobtype' : 'Gene',
                    'geneticobdescription' : fieldDict['description'],
                    'geneticobsymbols' : string.join([fieldDict['symbol'],fieldDict['synonyms']],'|')
            })
            currentGene.insertDatabase(connection)
            geneDict[genelsid] = currentGene.databaseFields['obid']


            # set up the location record to insert
            locationDict = {
                'geneticob' : genelsid,
                'xreflsid' : 'entrezgene.%s'%fieldDict['geneid'],
                'speciestaxid' : fieldDict['taxid'],
                'entrezgeneid' : fieldDict['geneid'],
                'locusname' : fieldDict['symbol'],
                'locussynonyms' : fieldDict['synonyms'],
                'cytopos' : fieldDict['map_location'],
                'chromosomename' : fieldDict['chromosome']
            }
            # insert location facts
            sql = """
                insert into geneticLocationFact(
                    geneticob ,                    
                    xreflsid,
                    speciestaxid ,   
                    entrezgeneid  ,  
                    locusname     ,    
                    locussynonyms ,  
                    cytopos       ,  
                    chromosomename)
                values(
                    %(geneticob)s,
                    %(xreflsid)s,
                    %(speciestaxid)s ,   
                    %(entrezgeneid)s  ,  
                    %(locusname)s     ,
                    %(locussynonyms)s ,
                    %(cytopos)s       ,  
                    %(chromosomename)s  
                )
                """
            try :
                #print "will execute " + sql%locationDict
                insertcursor.execute(sql,locationDict)
                connection.commit()
            except:
                print "Exception caught executing " + sql%locationDict



        # add gene product link
        sql = """
        insert into
        geneproductlink(geneticob,biosequenceob,xreflsid,producttype,evidence)
        values(%(geneticob)s,%(biosequenceob)s,%(xreflsid)s,%(producttype)s,%(evidence)s)
        """
        productDict = {
            "geneticob" : geneDict[genelsid],
            "biosequenceob" : seqDict[fieldDict["sequencename"]],
            "xreflsid" : "s.%s"%(genelsid,seqDict["sequencename"]),
            "producttype" : producttype,
            "evidence" : "entrezgene"
        }
        insertcursor.execute(sql,poductDict)
        connection.commit()
                                                  

        rowCount += 1

                    
    insertcursor.close()
    connection.close()





def main():
    #LoadHomologeneAliases("c:/working/homologene/homologene.build55.ALIASES")
    #LoadHomologeneTitles("c:/working/homologene/homologene.build55.TITLES")
    #LoadHomologeneUnigenes("c:/working/homologene/homologene.build55.UNIGENE")    
    #updateHomologeneAliases("/home/sheepgen/data/sheepgeneindex/homologene.build55.ALIASES")
    #LoadOrUpdateHomologeneDATA("c:/working/homologene/homologene.build55.DATA")
    #updateHomologeneTitles("/home/sheepgen/data/sheepgeneindex/homologene.build55.TITLES")
    #updateHomologeneUnigenes("/home/sheepgen/data/sheepgeneindex/homologene.build55.UNIGENE")
    #LoadEntrezgeneUnigenes("/home/sheepgen/data/sheepgeneindex/gene2unigene.txt")
    #LoadOrUpdateHomologeneDATA("/home/sheepgen/data/sheepgeneindex/homologene.build55.DATA")
    linkSpotToGeneSymbol("Affymetrix.Bovine Genome Array","/home/sheepgen/data/microarray/test.csv",\
                                              fileKeyDetails= {"column" : "probe set id", "regexp" : None}, \
                                              dbKeyDetails={"column" : "xreflsid", "regexp" : "^Affymetrix\.Bovine Genome Array\.(.+)$"},\
                                              fileSymbolDetails={"column" : "gene symbol or accession", "regexp" : None},\
                                              geneFactColumns = ["gene title"],
                                              fieldnamesrow=11,datastartsrow=12,creategenes=True)

        

if __name__ == "__main__":
    main()        














    

