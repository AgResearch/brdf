#-----------------------------------------------------------------------+
# Name:		dbProcedures.py           				|
#									|
# Description:	classes that implements db procedures                   |
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
# 11/2005    AFM  initial version                                       |
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
import string

from brdfExceptionModule import brdfException
from annotationModule import commentOb, uriOb
from biosubjectmodule import bioSubjectOb, bioSampleOb, bioSampleList
from studyModule import phenotypeStudy, geneExpressionStudy
from labResourceModule import labResourceOb
from dataImportModule import dataSourceOb,importProcedureOb,labResourceImportFunction,microarrayExperimentImportFunction
from studyModule import microarrayObservation
from sequenceModule import bioSequenceOb
from sequenceFileParsers import FastaParser
from geneticModule import geneticOb, geneticLocationFact
from obmodule import getNewObid
from ontologyModule import ontologyOb


# platform dependent module search path. (This can't be done in
# a .pth because we do not always want this imported)
#sys.path.append('C:/Python23/lib/site-packages/sheepgenomics')



import databaseModule


import logging




# set up logger if we want logging
proceduremodulelogger = logging.getLogger('dbProcedures')
proceduremodulehdlr = logging.FileHandler(os.path.join(globalConf.LOGPATH,'dbprocedures.log'))
#hdlr = logging.FileHandler('c:/temp/sheepgenomicsforms.log')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
proceduremodulehdlr.setFormatter(formatter)
proceduremodulelogger.addHandler(proceduremodulehdlr) 
proceduremodulelogger.setLevel(logging.INFO)        

""" --------- module variables ----------"""


""" --------- module methods ------------"""

    
""" --------- classes -------------------"""
class dbprocedure (object) :
    def __init__(self,connection,stampobid = False):
        object.__init__(self)

        # stamp the maximum obid to assist with rollbacks
        self.connection=connection
        if self.connection != None and stampobid:
            stampCursor = connection.cursor()
            sql = "select max(obid) from ob"
            stampCursor.execute(sql)
            maxobid = stampCursor.fetchone()
            proceduremodulelogger.info("Form obid stamp : max obid = %s"%maxobid[0])
            stampCursor.close()

        self.procedureState = {
            'ERROR' : 0,
            'MESSAGE' : ''}



######################################################################
#
# This procedure is used to update db sequence records
# with sequence
# !!!!! note that this will query the database for each record to check it is not already
# in the database , by default. If thsi is too slow then you can either ask this not
# to be done by setting checkExisting to False OR , this code can easily be modified to
# read all sequence lsids from the database into an array , which can then used to
# check. 
#
######################################################################

class loadSequenceProcedure ( dbprocedure ):
    def runProcedure(self,filename,fileformat='FASTA',sequencetype='mRNA SEQUENCE',lsidprefix='NCBI',checkExisting=True):
        """ load sequences from a csv or fasta file"""

        connection=databaseModule.getConnection()
        

        if fileformat != 'FASTA':
            raise brdfException("loadSequenceProcedure : only FASTA format currentl supported")

        # create a data import - this needs an importProcedure and a dataSource
        # get or create the import procedure
        importProcedure = importProcedureOb()        
        try:
            importProcedure.initFromDatabase("dbprocedures.loadSequenceProcedure",connection)
        except brdfException:
            importProcedure.initNew(connection)
            importProcedure.databaseFields.update ( {
                'xreflsid' : "dbprocedures.loadSequenceProcedure",
                'procedurename' : "dbprocedures.loadSequenceProcedure",
            })
            importProcedure.insertDatabase(connection)        


        dataSource = dataSourceOb()
        dataSource.initNew(connection,fileformat)
        dataSource.databaseFields.update({
            'xreflsid' : filename,
            'numberoffiles' : 1
        })        
        dataSource.insertDatabase(connection)
        
        
        reader = FastaParser(filename)
        rowCount = 0
        insertCount = 0

        sequence = reader.nextRecord()
        #print "processing %s"%str(sequence)
        while sequence != None:
            if rowCount%500 == 1:
                print "rowCount %s processing %s"%(rowCount,str(sequence))
                print str(reader.parserState)
            xreflsid = sequence['id']
            if lsidprefix != None:
                if len(lsidprefix.strip()) > 0:
                    xreflsid = '%s.%s'%(lsidprefix,sequence['id'])
            fieldDict = {
                'xreflsid' : xreflsid,
                'sequencename' : sequence['id'],
                'sequencedescription' : sequence['description'],
                'seqstring' : sequence['sequence'],
                'seqlength' : len(sequence['sequence']),
                'sequencetype' : sequencetype
            }
            bioSequence = bioSequenceOb()
            if checkExisting:
                try:
                    bioSequence.initFromDatabase(fieldDict['xreflsid'],connection)
                except brdfException, msg:
                    if bioSequence.obState['ERROR'] != 1:
                        raise brdfException(msg)
                    else:
                        bioSequence.initNew(connection)
                        bioSequence.databaseFields.update(fieldDict)
                        bioSequence.insertDatabase(connection)
                        insertCount += 1
            else:
                bioSequence.initNew(connection)
                bioSequence.databaseFields.update(fieldDict)
                bioSequence.insertDatabase(connection)
                connection.commit()
                insertCount += 1

            dataSource.addImportFunction(bioSequence,importProcedure,connection)
                
                
            rowCount += 1
            sequence = reader.nextRecord()

        connection.close()
        reader.close()

        print "%s rows processed, %s inserts done\n"%(rowCount,insertCount)



######################################################################
#
# This procedure is used to link sequences to microarray spots
#
######################################################################

class linkSpotToSequenceProcedure( dbprocedure ):
    def runProcedure(self,arraylsid,sequencelsidprefix, microarrayspotfactcolumn='gal_name'):
        """ this procedure will go through and attempt to link each spot in a given microarray , with a sequence,
        using the specified sequence lsid prefix , and the specified column from the gal file"""

        connection=databaseModule.getConnection()
        updateconnection=databaseModule.getConnection()
        spotCount = 0
        linkedCount = 0

        sql = """
        select msf.obid , %s from
        microarrayspotfact msf join labresourceob lr on
        msf.labresourceob = lr.obid and
        lr.xreflsid = '%s'
        """%(microarrayspotfactcolumn,arraylsid)

        linkcursor = connection.cursor()
        updatecursor = updateconnection.cursor()
        linkcursor.execute(sql)

        spotdetails = linkcursor.fetchone()
        while spotdetails != None:
            # try getting a matching sequence
            sequence = bioSequenceOb()
            try :
                print "trying %s.%s"%(sequencelsidprefix,spotdetails[1])
                sequence.initFromDatabase("%s.%s"%(sequencelsidprefix,spotdetails[1]),connection)
                updateDetails = {
                    'xreflsid' : "%s.%s.spotlink"%(sequencelsidprefix,spotdetails[1]),
                    'voptypeid' : 376,
                    'subjectob' : spotdetails[0],
                    'objectob' : sequence.databaseFields['obid'],
                    'predicate' : 'ARRAYSPOT-SEQUENCE'
                }
                    
                updatesql = """
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
                print "executing %s"%(updatesql%updateDetails)
                updatecursor.execute(updatesql,updateDetails)
                updateconnection.commit();
                linkedCount += 1
            except brdfException , msg:
                if sequence.obState['ERROR'] == 1:
                    print "could not find %s.%s"%(sequencelsidprefix,spotdetails[1])
                else :
                    raise brdfException(msg)
                
            spotdetails = linkcursor.fetchone()
            spotCount += 1

        spotcursor.close()
        updatecursor.close()
        connection.close()
        updateconnection.close()

        print "%s rows processed, %s inserts done\n"%(spotCount,linkedCount)


######################################################################
#
# This procedure links a microarray spot to a gene. If the gene record does not
# exist , it is created. It uses as input annotation of spot accessions with
# entrez geneid and species taxid
######################################################################
class linkSpotToGeneProcedure( dbprocedure ):
    def runProcedure(self,arraylsid,inputfile,spotnamedbcolumn='gal_id',spotnamecolumn='systematic name',geneidcolumnname="entrez gene id", creategenes=False,\
                     fieldnamesrow=1,datastartsrow=3):
        """ Example input data :
        Human else Mouse else Rat else NRProtein	TAXID	SYMBOL	SYNONYMS	CHROMOSOME	MAP_LOCATION	DESCRIPTION	TYPE_OF_GENE
7498	9606	XDH	XO|XOR	2	2p23.1	xanthine dehydrogenase	protein-coding
7046	9606	TGFBR1	AAT5|ACVRLK4|ALK-5|ALK5|SKR4|TGFR-1	9	9q22	transforming growth factor, beta receptor I (activin A receptor type II-like kinase, 53kDa)	protein-coding
0							
7335	9606	UBE2V1	CIR1|CROC-1|CROC1|UBE2V|UEV-1|UEV1|UEV1A	20	20q13.2	ubiquitin-conjugating enzyme E2 variant 1	protein-coding
5426	9606	POLE	DKFZp434F222|FLJ21434|POLE1	12	12q24.3	polymerase (DNA directed), epsilon	protein-coding
51720	9606	UIMC1	RAP80|X2HRIP110	5	5q35.2	ubiquitin interaction motif containing 1	protein-coding
196513	9606	DCP1B	DCP1|hDcp1b	12	12p13.33	DCP1 decapping enzyme homolog B (S. cerevisiae)	protein-coding

Other examples (Agilent annotation) :

Systematic Name	Common Name	GenBank Accession No.	Synonyms	Map	Gene Symbol	Dbid	DBid	Description	EC	Entrez Gene ID	Function	GO biological process	GO cellular component	GO molecular function	Keywords	Pathways	Phenotype	Product	PubMedID	RefSeq	Summary	Type	UniGene	ControlType	Cytoband	EnsemblID	EntrezGene	GeneSymbol	Sequence	TIGRID	Date Added	Date Modified	Genomic Element Type
3xSLv1	NegativeControl																							neg				3xSLv1			Wed Mar 08 11:30:32 NZDT 2006	Wed Mar 08 11:30:32 NZDT 2006	Gene
A_51_P100021	NM_010657	NM_010657		chr4:119157784..119157845	Hivep3	ref:NM_010657;gb:AY454345;tc:NP955906;tc:TC1571671	GeneID:16656; MGI:106589; GI:124107625	Mus musculus human immunodeficiency virus type I enhancer binding protein 3 (Hivep3), mRNA [NM_010657]		16656		GO:45941(positive regulation of transcription)	GO:0005634(nucleus)	GO:0003677(DNA binding)				human immunodeficiency virus type I enhancer binding protein 3	16728642; 16141073; 16141072; 15790681; 15627499; 15618518; 15368895; 15033168; 14707112; 12477932; 12466851; 12378523; 12001065; 11804591; 11217851; 11076861; 11042159; 10922068; 10625627; 10349636; 9601941; 8889548; 8812474; 8255760	NM_010657		protein-coding	Mm.378956	FALSE	4qD2.2		16656	Hivep3	CATGGCTGGATTAACGTATGTGTGTGGTATATAGATACACAGAGAGAAACCAAAGTGGTG	NP955906	Wed Mar 08 11:30:32 NZDT 2006	Tue Apr 17 13:50:04 NZST 2007	Gene
A_51_P100034	NM_027162	NM_027162		chr11:115429108..115429049	Mif4gd	ref:NM_027162;gb:BC055812;gb:AK003708;gb:AK010175	GeneID:69674; MGI:1916924; GI:34328402; CCDS:CCDS25643.1	Mus musculus RIKEN cDNA 2310075G12 gene (2310075G12Rik), mRNA [NM_027162]		69674				GO:3723(RNA binding)				MIF4G domain containing	16141073; 16141072; 12477932; 12466851; 11217851; 11076861; 11042159; 10922068; 10349636; 8889548	NM_027162		protein-coding	Mm.24635	FALSE	11qE2	ENSMUST00000021087	69674	2310075G12Rik	GAGACTTTTGTGGAGGAAGCCTGTTTCCTCCAGTCATGAGTGACTGCCTCACCAGGTTGG	NP586093	Wed Mar 08 11:30:32 NZDT 2006	Tue Apr 17 13:50:04 NZST 2007	Gene
A_51_P100052	XM_205324	XM_205324		chrX:61323567..61323626	Slitrk2	gb:XM_205324;gb:AK044761;ens:ENSMUST00000036043;riken:A930040J07	GeneID:245450; MGI:2679449; GI:110350664; CCDS:CCDS30169.1	PREDICTED: SLIT and NTRK-like family, member 2 [Mus musculus], mRNA sequence [XM_205324]		245450		GO:7409(axonogenesis)	GO:16021(integral to membrane); GO:16020(membrane)	GO:3674(molecular_function); GO:5515(protein binding)				SLIT and NTRK-like family, member 2	16141073; 16141072; 15582152; 14557068; 14550773; 12477932; 12466851; 11217851; 11076861; 11042159; 10349636	XM_205324		protein-coding	Mm.336081	FALSE	XqA7.1	ENSMUST00000036043	245450	Slitrk2	CTAAATGTGAATTGCCAAGAAAGGAAGTTCACTAACATCTCTGACCTACAGCCCAAACCT	TC1434615	Wed Mar 08 11:30:32 NZDT 2006	Tue Apr 17 13:50:04 NZST 2007	Gene



        """

        connection=databaseModule.getConnection()
        insertCursor=connection.cursor()
        reader =csv.reader(file(inputfile))

        # get the spots
        sql = """
        select %s as accession, msf.obid  from
        microarrayspotfact msf join labresourceob lr on
        msf.labresourceob = lr.obid and
        lr.xreflsid = '%s'
        """%(spotnamedbcolumn,arraylsid)
        proceduremodulelogger.info("running %s"%sql)
        insertCursor.execute(sql)
        spots=insertCursor.fetchall()

        # make a dictionary with the accession as key, and a list of all obids matching that accession
        # as value , as there will in general be replicates
        spotDict = {}
        for (accession,obid) in spots:
           if accession not in spotDict:
              spotDict[accession] = [obid]
           else:
              spotDict[accession].append(obid)
           
        proceduremodulelogger.info("retrieved %s spots"%len(spotDict))
        print "example rows"
        for key in spotDict.keys()[0:50]:
            print "%s : %s"%(key,spotDict[key])

        # get the genes
        sql = """
        select
           glf.entrezgeneid,
           glf.speciestaxid,
           g.obid,
           g.xreflsid
        from
           geneticob g join geneticlocationfact glf on
           glf.geneticob = g.obid
        """
        proceduremodulelogger.info("running %s"%sql)
        insertCursor.execute(sql)
        genes = insertCursor.fetchall()
        geneDict = dict([ (str(rec[0]),(rec[1],rec[2],rec[3])) for rec in genes ])
        proceduremodulelogger.info("retrieved %s genes"%len(geneDict))


        #for row in reader:
        rowCount = 0
        linkedCount = 0
        geneCount = 0
        linkednames =[]
        for row in reader:
            rowCount += 1

            # get the column headings
            if rowCount == fieldnamesrow:
                fieldNames = [name.lower() for name in row]
                continue
            elif  rowCount >= datastartsrow:
                fieldDict = dict(zip(fieldNames,row))
            else:
                continue

            print fieldDict

            if fieldDict[geneidcolumnname] == '0':
                continue

            if fieldDict[spotnamecolumn] in linkednames:
               continue


            # check we can find the spot
            if fieldDict[spotnamecolumn] not in spotDict:
                print "warning - could not find spot with name %s"%fieldDict[spotnamecolumn]
                continue
            
                

            # find a gene by looking up Entrez Gene id
            # if not found , insert gene                
            if fieldDict[geneidcolumnname] not in geneDict:
                if not creategenes:
                    print "Warning : could not find gene %s (and not creating genes)"%str(fieldDict)
                    continue
                else:                    
                    gene = geneticOb()
                    gene.initNew(connection)
                    gene.databaseFields.update({
                        "xreflsid" : "geneticob.%s"%fieldDict['symbol'],
                        "obkeywords" : "%s %s"%(fieldDict['symbol'], {True : fieldDict['synonyms'], False : ''}[fieldDict['synonyms'] != None]),
                        "geneticobname" : fieldDict['symbol'],
                        "geneticobdescription" : fieldDict['description'],
                        "geneticobtype" : "Homologene",
                        "geneticobsymbols" : fieldDict['symbol'],
                        "obcomment" : "Added by linkSpotToGeneProcedure"
                    })
                    print "\n\ncreating new gene %s %s"%(fieldDict['symbol'],fieldDict['description'])
                    gene.insertDatabase(connection)
                    geneCount += 1

                    geneDict[fieldDict[geneidcolumnname]] = (int(fieldDict['taxid']), gene.databaseFields['obid'], gene.databaseFields['xreflsid'])


                    # add location fact
                    location = geneticLocationFact()
                    location.initNew(connection)
                    location.databaseFields.update({
                        'xreflsid' : "Entrez Gene.%s"%fieldDict[geneidcolumnname],
                        'geneticob' : gene.databaseFields['obid'],
                        'speciestaxid' : fieldDict['taxid'],
                        'speciesname' : eval({True : "globalConf.taxTable[int(fieldDict['taxid'])]['speciesname']", False : "None"}[int(fieldDict['taxid']) in globalConf.taxTable]),
                        'entrezgeneid' : fieldDict[geneidcolumnname],
                        'mapname' : 'Human Cytogenetic',
                        'locationstring' : fieldDict['map_location'],
                        'chromosomename' : fieldDict['chromosome']
                    })
                    location.insertDatabase(connection)



                    # create aliases ontology 
                    ontologylsid = 'ontology.GENEINDEX_ALIASES.%s'%fieldDict['symbol']
                    ontology = ontologyOb()                    
                    ontology.initNew(connection)
                    ontology.databaseFields.update ( {
                        'xreflsid' : ontologylsid,
                        'ontologyname' : 'Gene Index Alias Ontology %s'%fieldDict['symbol'],
                        'ontologydescription' : 'Gene Index Alias Ontology %s'%fieldDict['symbol'],
                        'ontologycomment' : 'This ontology referenced by gene index, loaded as an update from %s'%inputfile
                    })
                    ontology.insertDatabase(connection)


                    # insert term
                    ontology.addTerm(connection,fieldDict['symbol'],False)


                    # nomenclature link
                    updatedict = {
                        'linklsid' : 'nomenclaturelink.geneticob.Gene Index aliases.%s'%fieldDict['symbol'],
                        'geneticobid' : gene.databaseFields['obid'],
                        'ontologyobid' : ontology.databaseFields['obid'],
                        'predicatecomment' : 'Link to aliases ontology for gene index entry %s'%fieldDict['symbol']
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
                    ontologylsid = 'ontology.GENEINDEX_TITLES.%s'%fieldDict['symbol']
                    ontology = ontologyOb()                    
                    ontology.initNew(connection)
                    ontology.databaseFields.update ( {
                        'xreflsid' : ontologylsid,
                        'ontologyname' : 'Gene Index Titles Ontology %s'%fieldDict['symbol'],
                        'ontologydescription' : 'Gene Index Titles Ontology %s'%fieldDict['symbol'],
                        'ontologycomment' : 'This ontology referenced by gene index, loaded as an update from %s'%inputfile
                    })
                    ontology.insertDatabase(connection)


                    # insert term
                    ontology.addTerm(connection,fieldDict['description'],False)

                    # nomenclature link
                    updatedict = {
                        'linklsid' : 'nomenclaturelink.geneticob.Gene Index titles.%s'%fieldDict['symbol'],
                        'geneticobid' : gene.databaseFields['obid'],
                        'ontologyobid' : ontology.databaseFields['obid'],
                        'predicatecomment' : 'Link to titles ontology for gene index entry %s'%fieldDict['symbol']
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

                
            # set up predicate link linking spot and gene
            for spotid in spotDict[fieldDict[spotnamecolumn]]:
               predicateDetails = {
                    'xreflsid' : "%s.%s"%(geneDict[fieldDict[geneidcolumnname]][2],fieldDict[spotnamecolumn]),
                    'voptypeid' : 375,
                    'subjectob' : spotid,
                    'objectob' : geneDict[fieldDict[geneidcolumnname]][1],
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

            linkednames.append(fieldDict[spotnamecolumn])

        insertCursor.close()
        connection.close()
        print "row count = %s, new gene count = %s, linked count = %s "%(rowCount, geneCount, linkedCount)



######################################################################
#
# This procedure is used to link sequences to other sequences that are Affy targets
#
######################################################################

class linkSequenceToAffyTarget( dbprocedure ):
    def runProcedure(self,sequencedatasourcename,targetdatasourcename):
        """ this procedure will go through and attempt to link a sequence that is the target in an Affy array, with
        the parent sequence. Both sets of sequences are loaded into memory for speed
        """

        connection=databaseModule.getConnection()
        sequenceCount = 0
        linkedCount = 0

        # get the source sequences
        sql = """
        select
           b.obid,
           b.sequencename
        from
           (datasourceob d join importfunction f on
           d.xreflsid = %(sequencedatasourcename)s and
           f.datasourceob = d.obid) join
           biosequenceob b on b.obid = f.ob
        """

        print "executing %s"%sql%{'sequencedatasourcename' : sequencedatasourcename}                
        linkcursor = connection.cursor()
        linkcursor.execute(sql,{'sequencedatasourcename' : sequencedatasourcename})
        sourceseqs = linkcursor.fetchall()

        print sourceseqs[0:10]


        # get the target sequences
        sql = """
        select
           b.obid,
           b.sequencename
        from
           (datasourceob d join importfunction f on
           d.xreflsid = %(targetdatasourcename)s and
           f.datasourceob = d.obid) join
           biosequenceob b on b.obid = f.ob
        """

        print "executing %s"%sql%{'targetdatasourcename' : targetdatasourcename}                
        linkcursor = connection.cursor()
        linkcursor.execute(sql,{'targetdatasourcename' : targetdatasourcename})
        targetseqs = linkcursor.fetchall()

        print targetseqs[0:10]

        linkedtargets = []
        linkedseqs = []
        for sourceseq in sourceseqs:
            print "processing %s"%str(sourceseq)

            for targetseq in targetseqs:
                if re.search(sourceseq[1],targetseq[1]) != None:
                    print "linking %s to %s"%(sourceseq[1],targetseq[1])
                    linkedseqs.append(sourceseq[1])
                    linkedtargets.append(targetseq[1])
                    sql="""
                    insert into predicatelink(subjectob,objectob,xreflsid,predicate,voptypeid)
                    values(%(subjectob)s,%(objectob)s,%(xreflsid)s,'AFFYTARGET-SEQUENCE',376)
                    """
                    linkcursor.execute(sql,{'subjectob' : targetseq[0], 'objectob' : sourceseq[0] , 'xreflsid' : '%s:%s'%(targetseq[1],sourceseq[1])})
                    connection.commit()
                    
        
        

        linkcursor.close()
        connection.close()

        print "%s rows processed, %s inserts done\n"%(sequenceCount,linkedCount)


        

######################################################################
#
# This procedure is used to insert a record into the bioProtocol table
# It is just a wrapper for a SQL insert, which due to the long text is
# difficult to do in psql or pgadmin
#
######################################################################

class createProtocolProcedure ( dbprocedure ):
    def runProcedure(self):
        insertCursor = self.connection.cursor()
        sql = """
insert into bioprotocolob (
 xreflsid ,
 createdby ,
 obkeywords ,
 protocolname ,
 protocoltype ,
 protocoldescription ,
 protocoltext   )
values (
'Manual update.Ethnicity2',
'A McCulloch',
'manual update protocol ethnicity',
'Ethnicity update 2',
'Database Update',
'This protocol used to update the ethnicity baseline given new information, and to assign admixed flags',
%(protocoltext)s )"""
        insertDict = {
            'protocoltext' : """
/*
*
* back up existing
*
--
insert into biosubjectfact(biosubjectob,factnamespace,attributename,attributevalue)
select
biosubjectob,
'IBD baseline',
'ethnicity_ibddatabase',
attributevalue
from
biosubjectfact  bsf0
where
attributename = 'ethnicity'
and not exists (
select biosubjectob from biosubjectfact where
) etc etc etc 
"""            
        }
        insertCursor.execute(sql,insertDict)
        insertCursor.close()
        self.connection.commit()
        self.connection.close()
        


######################################################################
#
# This procedure attaches hyperlinks to NCBI accesions, to microarray spots 
#
######################################################################
class hyperlinkSpotAccessionsProcedure ( dbprocedure ):
    """ class for hyperlinkSpotAccessions  """
    def __init__(self, connection, arraylsid, checkExisting = False):
        dbprocedure.__init__(self,connection)
        proceduremodulelogger.info("in constructor of hyperlinkSpotAccessions")
        self.arraylsid = arraylsid
        self.checkExisting = checkExisting

        
    def runProcedure(self):
        if self.checkExisting :
            raise brdfException("hyperlinkSpotAccessionsProcedure : check existing links not supported")
        
        # obtain the lab resource ob
        array=labResourceOb()
        array.initFromDatabase(self.arraylsid,self.connection)
        

        # for each spot
        sql = """
        select obid ,   gal_id  , gal_genename  , gal_controltype
        from microarrayspotfact where labresourceob = %s
        """%array.databaseFields['obid']
        myconnection=databaseModule.getConnection()
        spotCursor = myconnection.cursor()
        spotCursor.execute(sql)
        spotRecord=spotCursor.fetchone()
        fieldNames = [item[0] for item in spotCursor.description]
        while spotRecord != None:
            spotDict = dict(zip(fieldNames,spotRecord))
            if spotDict['gal_controltype'] == 'false' :
                urilsid = 'http://www.ncbi.nlm.nih.gov/entrez/viewer.fcgi?db=nucleotide&val=%s'%spotDict['gal_genename']
                uri = uriOb()
                try:
                    uri.initFromDatabase(urilsid,self.connection)
                except brdfException ,errormessage:
                    #print str(uri.obState)
                    if uri.obState['ERROR'] == 1:
                        print "will insert %s"%urilsid

                        uri.initNew(self.connection)
                        uri.databaseFields.update(
                        {
                            'createdby' : 'system',
                            'uristring' : urilsid,
                            'xreflsid' : urilsid,
                            'visibility' : 'public'
                        })
                        uri.insertDatabase(self.connection)
                        uri.createLink(self.connection,spotDict['obid'],'NCBI Nucleotide record for %s'%spotDict['gal_genename'],'system')
                    else:
                        raise brdfException(errormessage)
                        

            spotRecord=spotCursor.fetchone()
            
        spotCursor.close
        myconnection.close()





######################################################################
#
# This procedure attaches links to lists of spots that have similar and dissimilar expression profiles 
#
######################################################################
class hyperlinkSimilaExpressionProcedure ( dbprocedure ):
    """ class for hyperlinkSimilaExpressionProcedure  """
    def __init__(self, connection, arraylsid, checkExisting = False):
        dbprocedure.__init__(self,connection)
        proceduremodulelogger.info("in constructor of hyperlinkSimilaExpressionProcedure")
        self.arraylsid = arraylsid
        self.checkExisting = checkExisting

        
    def runProcedure(self):
        if self.checkExisting :
            raise brdfException("hyperlinkSpotAccessionsProcedure : check existing links not supported")
        
        # obtain the lab resource ob
        #array=labResourceOb()
        #array.initFromDatabase(self.arraylsid,self.connection)
        

        spotCount = 0
        # for each spot
        #sql = """
        #select obid ,   xreflsid, gal_controltype
        #from microarrayspotfact where labresourceob = %s
        #"""%array.databaseFields['obid']
        #myconnection=databaseModule.getConnection()
        #spotCursor = myconnection.cursor()
        #expressionCursor = myconnection.cursor()
        #spotCursor.execute(sql)
        #spotRecord=spotCursor.fetchone()
        #fieldNames = [item[0] for item in spotCursor.description]
        expressionProfiles = []
        #while spotRecord != None:
        spotReader = csvSpotReader(self.arraylsid)
        spotDict = spotReader.nextSpot()
        while spotDict != None:
            spotCount += 1
            print "reading record %d"%spotCount
            #spotDict = dict(zip(fieldNames,spotRecord))
            # if not a control , then get expression profile
            if spotDict['gal_controltype'] == None:
                spotDict['gal_controltype'] = 'false' 
            if spotDict['gal_controltype'] == 'false' :
                # query to retrieve raw log ratios for this spot
                #sql = """
                #select
                #mo.gpr_logratio
                #from
                #microarrayobservation mo 
                #where
                #microarrayspotfact = %s"""%spotDict['obid'] + """ and
                #xreflsid like '%mid%' order by
                #mo.xreflsid"""
                #expressionCursor.execute(sql)
                #mydatatuples = expressionCursor.fetchall()
                mydatatuples = spotReader.nextProfile()

                # the expression profile is appended to an array or profiles.
                # each element of the array is a tuple (obid,xreflsid,[profile]) - e.g.
                #(328888, 'Agilent.012694_D_20050902.gal.B1.C1.R6', [-0.51600000000000001, -0.84299999999999997,
                #-0.76700000000000002, -0.14599999999999999, -0.16400000000000001, -0.159,
                #-0.39500000000000002, 0.18099999999999999, -1.0489999999999999, -0.499, -0.063,
                #-0.311, -0.38200000000000001, 0.26500000000000001, -0.42399999999999999,
                #-0.42499999999999999, -0.69899999999999995, -0.50600000000000001, -0.32600000000000001,
                #-0.313, -0.51400000000000001, 0.24299999999999999, -0.16600000000000001, -0.25])
                expressionProfiles.append((spotDict['obid'],spotDict['xreflsid'],[datatuple[0] for datatuple in mydatatuples]))


                # for about very 20 profiles, we spike with a profile of all 1's
                if random.randint(1,4) == 1:
                    expressionProfiles.append((spotCount,str(spotCount),[1.0 for datatuple in mydatatuples]))

                    
            #potRecord=spotCursor.fetchone()
            spotDict = spotReader.nextSpot()
            #if spotCount > 200:
            #    break
            
        #spotCursor.close
        #myconnection.close()


        def profileLength(prof):
            length = math.sqrt(reduce(lambda x,y:x+y,map(lambda x:x*x,prof)))
            return length               


        def profileAngle(prof1,prof2):
            #print "calculating distance between : "
            #print str(prof1)
            #print str(prof2)
            angle = math.acos(reduce(lambda x,y:x+y,map(lambda x,y:x*y,prof1,prof2))/(profileLength(prof1) * profileLength(prof2)))
            return angle        

        # now process the profiles. For each profile , we calculate the distance from
        # all other profiles, using euclidean metric, as per this function : 
        def profileDistance(prof1,prof2):
            #print "calculating distance between : "
            #print str(prof1)
            #print str(prof2)
            distance = math.sqrt(reduce(lambda x,y:x+y,map(lambda x,y:(x-y)**2,prof1,prof2)))
            return distance

        # this metric calcutes the disance between a profile and the inverse of another
        # profile
        def profileDistanceToInverse(prof1,prof2):
            #print "calculating distance between : "
            #print str(prof1)
            #print str(prof2)
            distance = math.sqrt(reduce(lambda x,y:x+y,map(lambda x,y:(x+y)**2,prof1,prof2)))
            return distance

        # resample from two profiles
        def resample(profile1,profile2):
            return [random.choice(profile1+profile2) for i in range(0,len(profile1))]
            


        closestDict = {}
        furthestDict = {}
        closestCount = 5
        furthestCount = 5
        profileCount = 0
        freqDistanceFile = open("c:/temp/freqDistanceFile.tmp","w")
        freqAngleFile = open("c:/temp/freqAngleFilekss.tmp","w")
        anglesFile = open("c:/temp/anglesFilekss.tmp","w")
        for index1 in range(0,len(expressionProfiles)):
            profileCount +=1

            # only process some of them , for a test
            if random.randint(1,90) != 1:
                continue            
            profile1 = expressionProfiles[index1]
            skipPartialProfile = reduce(lambda x,y:x or y,[item == None for item in profile1[2]])
            if skipPartialProfile:
                continue
            print "processing profile # %d (%s)"%(profileCount, profile1[1])

            # set up a dictionary of closest and furthest profiles.
            # the value of each dictionary is a list of tuples. Each tuple is
            # the lsid and distance of the other profile
            closestDict[profile1[1]] = []
            furthestDict[profile1[1]] = []
            for index2 in range(0, len(expressionProfiles)):
                if index2 != index1:
                    if random.randint(1,90) != 1:
                        continue    
                    profile2 = expressionProfiles[index2]
                    skipPartialProfile = reduce(lambda x,y:x or y,[item == None for item in profile2[2]])
                    if skipPartialProfile:
                        continue                    
                    
                    distance  = profileDistance(profile1[2],profile2[2])

                    # code to shuffle profiles to generate random distribution
                    
                    angle = profileAngle(profile1[2],profile2[2])
                    #prof1 = resample(profile1[2],profile2[2])
                    #prof2 = resample(profile1[2],profile2[2])
                    #angle = profileAngle(prof1,prof2)                    
                    # output the distance to the frequency table
                    if index1 < index2:
                        freqDistanceFile.write(str(distance)+"\n")
                        freqAngleFile.write(str(angle)+"\n")
                        
                    #if distance != None:
                    #    print "%s-->%s : %6.1f"%(profile1[1],profile2[1],profileDistance(profile1[2],profile2[2]))
                    anglesFile.write("%s-->%s : %6.2f\n"%(profile1[1],profile2[1],angle))


                    
                    if len(closestDict[profile1[1]]) < closestCount:   # fill up the dict with first distances encountered
                        closestDict[profile1[1]].append((profile2[1],distance))
                        closestDict[profile1[1]].sort(lambda x,y:cmp(y[1],x[1])) # sort so that the most distant of the close profiles is first
                    else:
                        # if the current distance is closest than the furthest of the current closest distances,
                        # the replace that furthest distance with the current distance
                        #print "about to check closest : "
                        #print closestDict[profile1[1]]                  
                        if distance < closestDict[profile1[1]][0][1]:
                            closestDict[profile1[1]][0] = (profile2[1],distance)
                            closestDict[profile1[1]].sort(lambda x,y:cmp(y[1],x[1])) # sort so that the most distant of the close profiles is first
                    distance  = profileDistanceToInverse(profile1[2],profile2[2])        
                    if len(furthestDict[profile1[1]]) < furthestCount:
                        furthestDict[profile1[1]].append((profile2[1],distance))
                        furthestDict[profile1[1]].sort(lambda x,y:cmp(y[1],x[1])) # sort so that the most distant of the close inverse profiles is first
                    else:
                        #print "about to check furthest : "
                        #print furthestDict[profile1[1]]                    
                        if distance < furthestDict[profile1[1]][0][1]:
                            furthestDict[profile1[1]][0] = (profile2[1],distance)
                            furthestDict[profile1[1]].sort(lambda x,y:cmp(y[1],x[1])) # sort so that the most distant of the close inverse profiles is first
                        

                    
        #write expressionProfiles
        proxFile = open("c:/temp/proxFile.tmp","w")
        for spot in closestDict.keys():
            proxFile.write("%s is near : "%spot)
            for neighbour in closestDict[spot]:
                proxFile.write(str(neighbour) + "  ,  ")
                proxFile.write("\n")
        proxFile.write("------------------------------------")
        for spot in furthestDict.keys():
            proxFile.write("%s is not near : "%spot)
            for neighbour in furthestDict[spot]:
                proxFile.write(str(neighbour) + "  ,  ")
                proxFile.write("\n")
                
        proxFile.close()
        freqDistanceFile.close()
        freqAngleFile.close()
        anglesFile.close()


class csvSpotReader ( object ):
    """ class for providing an interface to a CSV file of experiment spots that looks a bit like the SQL interface  """
    def __init__(self, filename):
        object.__init__(self)
        self.filename = filename
        self.reader = csv.reader(open(self.filename,"rb"))
        self.fieldNames = [item.lower() for item in self.reader.next()]
        self.currentRow = self.reader.next()
        self.currentDict = dict(zip(self.fieldNames,self.currentRow))
        self.currentDict['gal_controltype'] = 'false'
        self.currentDict['obid'] = self.currentDict['spotid']
        self.currentDict['xreflsid'] = self.currentDict['spotid']        
        self.state = {
            'ERROR' : 0,
            'END' : 0
        }
        
    def nextSpot (self):
        result = None
        if self.state['END'] == 0:
            result = self.currentDict
        return result

    def nextProfile (self):
        if self.state['END'] == 1:
            return None

        currentSpot = self.currentDict['spotid']

        if self.currentDict['log_ratio'] == None:
            self.currentDict['log_ratio'] = ""
        if self.currentDict['log_ratio'] != "":
            profile=[[float(self.currentDict['log_ratio'])]]
        else:
            profile=[[None]]
            
        while currentSpot == self.currentDict['spotid'] and self.state['END'] == 0:
            self.currentRow = self.reader.next()
            if self.currentRow == None:
                self.currentRow = ""
            if len(self.currentRow) == 3:   
                self.currentDict = dict(zip(self.fieldNames,self.currentRow))
                self.currentDict['gal_controltype'] = 'false'
                self.currentDict['obid'] = self.currentDict['spotid']
                self.currentDict['xreflsid'] = self.currentDict['spotid']
                if self.currentDict['spotid'] == currentSpot:
                    if self.currentDict['log_ratio'] == None:
                        self.currentDict['log_ratio'] = ""

                    if self.currentDict['log_ratio'] != "":
                        profile.append([float(self.currentDict['log_ratio'])])
                    else:
                        profile.append([None])
                        
            else:
                self.state['END'] = 1
            

        return profile

class loadCSVFeaturesProcedure (dbprocedure):
    def __init__(self, connection):
        dbprocedure.__init__(self,connection)

    
    def runProcedure(self,infile, lsidprefix, targetseqtype = "mRNA SEQUENCE", comment = "", checkExisting = False):
        """ load features from a CSV file. Supported formats :

    CloneID,ConsensusPos,ContigPos,SNP,Distribution,Depth,TrueDepth,ConsensusLength,ContigLength,SNPsThisContig
    140304CS1900322200001,279,279,a/g,a 0.50:g 0.50:c 0.00:t 0.00,4,4,637,637,2,
    140304CS1900322200001,416,416,g/t,a 0.00:g 0.50:c 0.00:t 0.50,4,4,637,637,2,
    140304CS1901059800004,180,180,c/g,a 0.00:g 0.50:c 0.50:t 0.00,4,4,1108,1101,7,
    140304CS1901059800004,310,310,c/t,a 0.00:g 0.00:c 0.50:t 0.50,4,5,1108,1101,7,


    EXTERNALNAME	CONTIG	RELSTARTPOS	RELENDPOS	RELDIRECTION
    GI|116841074|GB|EG601070.1|EG601070	161106CS44008004FFF87	1	819	1
    GI|116841083|GB|EG601079.1|EG601079	161106CS44008004FFF88	1	764	1
    GI|116841304|GB|EG601300.1|EG601300	161106CS44008004FFF89	1	427	1
    GI|116841409|GB|EG601405.1|EG601405	161106CS44008004FFF8A	1	737	1
    GI|116841896|GB|EG601892.1|EG601892	161106CS44008004FFF8B	1	766	1


    DNANAME  PROTEINNAME  START STOP ORIENTATION
    161106CS4401438300001,161106CS4401438300001_F1_1, 1, 93, 1
        """

        print "opening %s"%infile

        reader = csv.reader(file(infile,"r"))
        insertCursor = self.connection.cursor()    

        # query the database to retrieve all the relevant targets 
        sql = """
            select
               upper(xreflsid),
               xreflsid,
               obid
            from
               biosequenceob
            where
               xreflsid like '%(lsidprefix)s%%' and
               sequencetype = '%(sequencetype)s'"""%{
                  "lsidprefix" : lsidprefix,
                  "sequencetype" : targetseqtype
               } 

        print "executing %s"%sql           
        linkcursor = self.connection.cursor()
        linkcursor.execute(sql)

        # make a dictionary of seqs for lookup - key is upper case xreflsid, value is a tuple of (xreflsid,obid)
        targetDict = dict([ (mytuple[0],(mytuple[1],mytuple[2])) for mytuple in linkcursor.fetchall() ])
        print "retrieved %s target seqs"%len(targetDict)

        # create a data import - this needs an importProcedure and a dataSource
        # get or create the import procedure
        importProcedure = importProcedureOb()        
        try:
            importProcedure.initFromDatabase("dbprocedures.loadCSVFeaturesProcedure",self.connection)
        except brdfException:
            importProcedure.initNew(self.connection)
            importProcedure.databaseFields.update ( {
                'xreflsid' : "dbprocedures.loadCSVFeaturesProcedure",
                'procedurename' : "dbprocedures.loadCSVFeaturesProcedure",
            })
            importProcedure.insertDatabase(self.connection)        


        dataSource = dataSourceOb()
        dataSource.initNew(self.connection,"CSV")
        dataSource.databaseFields.update({
            'xreflsid' : infile,
            'numberoffiles' : 1,
            'datasourcecomment' : comment
        })        
        dataSource.insertDatabase(self.connection)
        dataSource.addImportFunction(dataSource,importProcedure,self.connection)


        rownum = 0
        for row in reader:
            rownum += 1

            if rownum == 1:
                fieldNames = [item.upper() for item in row]
                print str(fieldNames)
                continue
            if fieldNames == ['DNANAME',  'PROTEINNAME'  ,'START' ,'STOP' ,'ORIENTATION']:
                if len(row) < 4:
                    break
                
                fieldDict = dict(zip(fieldNames,row))

                if string.upper(fieldDict['DNANAME']) not in targetDict:
                    raise brdfException("*** gave up as %s not in database"%fieldDict['DNANAME'])
                    
                else:
                    print "processing %s"%str(fieldDict['DNANAME'])
                    
                fieldDict['START'] = int(fieldDict['START'])
                fieldDict['STOP'] = int(fieldDict['STOP'])
                fieldDict['ORIENTATION'] = int(fieldDict['ORIENTATION'])

                fieldDict['ORIENTATION'] = fieldDict['ORIENTATION'] / abs(fieldDict['ORIENTATION'] )

                if(fieldDict['STOP'] < fieldDict['START']) :
                    (fieldDict['STOP'], fieldDict['START']) = (fieldDict['START'], fieldDict['STOP'])

                sql = """
                    insert into bioSequenceFeatureFact(biosequenceob,xreflsid,featuretype,featurestart,featurestop,featurecomment,
                    evidence,featurelength,featureaccession, featurestrand)
                    values(%(biosequenceob)s,%(xreflsid)s,%(featuretype)s,%(featurestart)s,%(featurestop)s,%(featurecomment)s,
                    %(evidence)s,%(featurelength)s,%(featureaccession)s,%(featurestrand)s)
                    """
                
                if rownum%500 == 1:
                    print "row %s"%rownum
                    print "executing %s"%(sql%{
                    'biosequenceob' : targetDict[fieldDict['DNANAME'].upper()][1],
                    'xreflsid' : "%(DNANAME)s.%(PROTEINNAME)s"%fieldDict,
                    'featuretype' : 'cds',
                    'featurestart' : fieldDict['START'],
                    'featurestop' : fieldDict['STOP'],
                    'featurecomment' : "ORF",
                    'evidence' : "6 frame translation",
                    'featurelength' : str(1+abs(int(fieldDict['STOP']) - int(fieldDict['START']))),
                    'featureaccession' : "%(PROTEINNAME)s"%fieldDict,
                    'featurestrand' : "%(ORIENTATION)s"%fieldDict
                    })



                insertCursor.execute(sql,{
                    'biosequenceob' : targetDict[fieldDict['DNANAME'].upper()][1],
                    'xreflsid' : "%(DNANAME)s.%(PROTEINNAME)s"%fieldDict, 
                    'featuretype' : 'cds',
                    'featurestart' : fieldDict['START'],
                    'featurestop' : fieldDict['STOP'],
                    'featurecomment' : "ORF",
                    'evidence' : "6 frame translation",
                    'featurelength' : str(1+abs(int(fieldDict['STOP']) - int(fieldDict['START']))),
                    'featureaccession' : "%(PROTEINNAME)s"%fieldDict,
                    'featurestrand' : "%(ORIENTATION)s"%fieldDict
                    })
                self.connection.commit()
                
            
            elif fieldNames == ['EXTERNALNAME','CONTIG','RELSTARTPOS','RELENDPOS','RELDIRECTION']:

                if len(row) < 4:
                    break
                
                fieldDict = dict(zip(fieldNames,row))

                if string.upper("%s.%s"%(lsidprefix,fieldDict['CONTIG'])) not in targetDict:
                    raise brdfException("*** gave up as %s.%s not in database"%(lsidprefix,fieldDict['CONTIG']))
                    
                else:
                    print "processing %s"%str(fieldDict['EXTERNALNAME'])

                sql = """
                    insert into bioSequenceFeatureFact(biosequenceob,xreflsid,featuretype,featurestart,featurestop,featurecomment,
                    evidence,featurelength,featureaccession, featurestrand)
                    values(%(biosequenceob)s,%(xreflsid)s,%(featuretype)s,%(featurestart)s,%(featurestop)s,%(featurecomment)s,
                    %(evidence)s,%(featurelength)s,%(featureaccession)s,%(featurestrand)s)
                    """
                print "executing %s"%(sql%{
                    'biosequenceob' : targetDict[string.upper("%s.%s"%(lsidprefix,fieldDict['CONTIG']))][1],
                    'xreflsid' : "%s.%s"%(targetDict[string.upper("%s.%s"%(lsidprefix,fieldDict['CONTIG']))][0],fieldDict['EXTERNALNAME']), 
                    'featuretype' : 'mRNA',
                    'featurestart' : fieldDict['RELSTARTPOS'],
                    'featurestop' : fieldDict['RELENDPOS'],
                    'featurecomment' : "contig membership",
                    'evidence' : "CAP3 contig assembly",
                    'featurelength' : str(1+abs(int(fieldDict['RELENDPOS']) - int(fieldDict['RELSTARTPOS']))),
                    'featureaccession' : "%(EXTERNALNAME)s"%fieldDict,
                    'featurestrand' : "%(RELDIRECTION)s"%fieldDict
                    })



                insertCursor.execute(sql,{
                    'biosequenceob' : targetDict[string.upper("%s.%s"%(lsidprefix,fieldDict['CONTIG']))][1],
                    'xreflsid' : "%s.%s"%(targetDict[string.upper("%s.%s"%(lsidprefix,fieldDict['CONTIG']))][0],fieldDict['EXTERNALNAME']), 
                    'featuretype' : 'mRNA',
                    'featurestart' : fieldDict['RELSTARTPOS'],
                    'featurestop' : fieldDict['RELENDPOS'],
                    'featurecomment' : "contig membership",
                    'evidence' : "CAP3 contig assembly",
                    'featurelength' : str(1+abs(int(fieldDict['RELENDPOS']) - int(fieldDict['RELSTARTPOS']))),
                    'featureaccession' : "%(EXTERNALNAME)s"%fieldDict,
                    'featurestrand' : "%(RELDIRECTION)s"%fieldDict
                    })
                self.connection.commit()
                                     
            elif fieldNames == ['CLONEID', 'CONSENSUSPOS', 'CONTIGPOS', 'SNP', 'DISTRIBUTION', \
                              'DEPTH', 'TRUEDEPTH', 'CONSENSUSLENGTH', 'CONTIGLENGTH', 'SNPSTHISCONTIG']:
                fieldDict = dict(zip(fieldNames,row))

                if string.upper("%s.%s"%(lsidprefix,fieldDict['CLONEID'])) not in targetDict:
                    raise brdfException("*** gave up as %s.%s not in database"%(lsidprefix,fieldDict['CLONEID']))
                    
                else:
                    print "processing %s"%str(fieldDict['CLONEID'])

                obid = getNewObid(self.connection)

                sql = """
                    insert into bioSequenceFeatureFact(obid,biosequenceob,xreflsid,featuretype,featurestart,featurestop,featurecomment,
                    evidence,featurelength,featureaccession)
                    values(%(obid)s,%(biosequenceob)s,%(xreflsid)s,%(featuretype)s,%(featurestart)s,%(featurestop)s,%(featurecomment)s,
                    %(evidence)s,%(featurelength)s,%(featureaccession)s)
                    """
                print "executing %s"%(sql%{
                    'obid' : obid,
                    'biosequenceob' : targetDict[string.upper("%s.%s"%(lsidprefix,fieldDict['CLONEID']))][1],
                    'xreflsid' : "%s.%s"%(targetDict[string.upper("%s.%s"%(lsidprefix,fieldDict['CLONEID']))][0],fieldDict['CLONEID']), 
                    'featuretype' : 'variation',
                    'featurestart' : fieldDict['CONTIGPOS'],
                    'featurestop' : fieldDict['CONTIGPOS'],
                    'featurecomment' : "%(SNP)s %(DISTRIBUTION)s"%fieldDict,
                    'evidence' : "SNooPy",
                    'featurelength' : "1",
                    'featureaccession' : "%(SNP)s %(DISTRIBUTION)s"%fieldDict
                    })



                insertCursor.execute(sql,{
                    'obid' : obid,
                    'biosequenceob' : targetDict[string.upper("%s.%s"%(lsidprefix,fieldDict['CLONEID']))][1],
                    'xreflsid' : "%s.%s"%(targetDict[string.upper("%s.%s"%(lsidprefix,fieldDict['CLONEID']))][0],fieldDict['CLONEID']), 
                    'featuretype' : 'variation',
                    'featurestart' : fieldDict['CONTIGPOS'],
                    'featurestop' : fieldDict['CONTIGPOS'],
                    'featurecomment' : "%(SNP)s %(DISTRIBUTION)s"%fieldDict,
                    'evidence' : "SNooPy",
                    'featurelength' : "1",
                    'featureaccession' : "%(SNP)s %(DISTRIBUTION)s"%fieldDict
                    })
                self.connection.commit()
                

                sql="""
                        insert into biosequencefeatureattributefact(biosequencefeaturefact,attributename,
                               attributevalue,factnamespace)
                        values(%(obid)s,%(attributename)s,%(attributevalue)s,'SNP Details')
                        """            

                for attributename in ['CONSENSUSPOS', 'SNP', 'DISTRIBUTION', \
                              'DEPTH', 'TRUEDEPTH', 'CONSENSUSLENGTH', 'SNPSTHISCONTIG']:

                    insertCursor.execute(sql,{
                            'obid' : obid,
                            'attributename' : attributename,
                            'attributevalue' : fieldDict[attributename]
                    })
                    self.connection.commit()



        insertCursor.close()
        self.connection.close()
            

def AgilentHyperlinkMain():
    connection=databaseModule.getConnection()

    myproc = hyperlinkSpotAccessionsProcedure(connection,'Agilent.012694_D_20050902.gal')
    myproc.runProcedure()
    connection.close()

def HyperlinkSimilarExpressionMain():
    #connection=databaseModule.getConnection()
    #myproc = hyperlinkSimilaExpressionProcedure(connection,'Agilent.012694_D_20050902.gal')
    #myproc = hyperlinkSimilaExpressionProcedure(connection,'Clonetrac print 128 ovine 20K.txt')
    myproc = hyperlinkSimilaExpressionProcedure(None,'c:/working/microarray/ksexps.csv')
    myproc.runProcedure()
    #connection.close()

def createProtocolMain():
    connection=databaseModule.getConnection()
    myproc = createProtocolProcedure(connection)
    myproc.runProcedure()

def loadSequenceMain():
    connection=databaseModule.getConnection()
    myproc = loadSequenceProcedure(connection)
    #myproc.runProcedure("c:/working/anar/data/AFT_Affy_chip_seqs.fa",sequencetype='mRNA SEQUENCE', lsidprefix='AFT',checkExisting=False)
    #myproc.runProcedure("m:/projects/agbrdf/data/aft/fungalrefs.fa",sequencetype='genomic DNA', lsidprefix='AFT',checkExisting=False)
    #myproc.runProcedure("c:/working/anar/data/Lp19-Lpa530240N.sif",sequencetype='mRNA SEQUENCE', lsidprefix='AFT',checkExisting=False)
    #myproc = linkSequenceToAffyTarget(connection)
    #myproc.runProcedure("m:/projects/agbrdf/data/aft/AFT_Affy_chip_seqs.fa","M:/projects/agbrdf/data/AFT/AFT Affymetrix Chip/Lp19-Lpa530240N.sif")
    #myproc = loadSequenceProcedure(connection)
    #myproc.runProcedure("c:/temp/Bovine_control",sequencetype='mRNA SEQUENCE', lsidprefix='Affymetrix.Bovine',checkExisting=False)
    #myproc = loadSequenceProcedure(connection)
    #myproc.runProcedure("c:/working/pgc/PG_clover_NR.fas",sequencetype='genomic DNA', lsidprefix='PGC',checkExisting=False)

    #myproc.runProcedure("c:/working/pgc/orionall.seq",sequencetype='genomic DNA', lsidprefix='PGC.Orion',checkExisting=False)
    #myproc.runProcedure("c:/working/leem/cs19annotated.seq",sequencetype='mRNA SEQUENCE', lsidprefix='CS19',checkExisting=False)
    #myproc.runProcedure("c:/working/possum/cs44.seq",sequencetype='mRNA SEQUENCE', lsidprefix='CS44',checkExisting=False)
    #myproc.runProcedure("c:/working/possum/all_good_oligos_final.fa.order.fasta",sequencetype='Microarray Probe Oligo', lsidprefix='CS44',checkExisting=False)
    #myproc.runProcedure("/home/possumbase/data/cs44orfs.seq",sequencetype='PROTEIN SEQUENCE', lsidprefix='CS44.ORF',checkExisting=False)
    #myproc.runProcedure("/home/possumbase/data/possumEST012007.seq",sequencetype='mRNA SEQUENCE', lsidprefix='NCBI.dbEST',checkExisting=False)
    #return

    ##### ISGCDATA imports ##############
    #myproc.runProcedure("/home/isgcdata/data/phase1/sid2263_122B5.fa",sequencetype='genomic DNA', lsidprefix='PHASE0',checkExisting=False)
    #myproc.runProcedure("/home/isgcdata/data/phase0/sid2264_366O21.fa",sequencetype='genomic DNA', lsidprefix='PHASE0',checkExisting=False)
    #myproc.runProcedure("/home/isgcdata/data/phase0/sid2265_413P17.fa",sequencetype='genomic DNA', lsidprefix='PHASE0',checkExisting=False)
    #myproc.runProcedure("/home/isgcdata/data/phase0/sid2266_463D18.fa",sequencetype='genomic DNA', lsidprefix='PHASE0',checkExisting=False)
    #myproc.runProcedure("/home/isgcdata/data/phase0/122B5_454AllContigs.fna",sequencetype='genomic DNA', lsidprefix='PHASE0.Contigs.122B5_454',checkExisting=False)
    #myproc.runProcedure("/home/isgcdata/data/phase0/366O21_454AllContigs.fna",sequencetype='genomic DNA', lsidprefix='PHASE0.Contigs.366O21_454',checkExisting=False)
    #myproc.runProcedure("/home/isgcdata/data/phase0/413P17_454AllContigs.fna",sequencetype='genomic DNA', lsidprefix='PHASE0.Contigs.413P17_454',checkExisting=False)
    #myproc.runProcedure("/home/isgcdata/data/phase0/463D18_454AllContigs.fna",sequencetype='genomic DNA', lsidprefix='PHASE0.Contigs.463D18_454',checkExisting=False)
    #myproc.runProcedure("/home/isgcdata/data/ETEG7N001.fa.masked",sequencetype='genomic DNA', lsidprefix='ETEG7N001.masked',checkExisting=False)
    #myproc.runProcedure("/home/isgcdata/data/ETEG7N002.fa.masked",sequencetype='genomic DNA', lsidprefix='ETEG7N002.masked',checkExisting=False)
    #myproc.runProcedure("/home/isgcdata/data/ETRJPPD01.fa.masked",sequencetype='genomic DNA', lsidprefix='ETRJPPD01.masked',checkExisting=False)
    #myproc.runProcedure("/home/isgcdata/data/ETRJPPD02.fa.masked",sequencetype='genomic DNA', lsidprefix='ETRJPPD02.masked',checkExisting=False)
    #myproc.runProcedure("/home/isgcdata/data/ET2HTXC01.fa.masked",sequencetype='genomic DNA', lsidprefix='ET2HTXC01.masked',checkExisting=False)
    #myproc.runProcedure("/home/isgcdata/data/ET2HTXC02.fa.masked",sequencetype='genomic DNA', lsidprefix='ET2HTXC02.masked',checkExisting=False)
    #myproc.runProcedure("/home/isgcdata/data/EU1SDX201.fa.masked",sequencetype='genomic DNA', lsidprefix='EU1SDX201.masked',checkExisting=False)
    #myproc.runProcedure("/home/isgcdata/data/EU1SDX202.fa.masked",sequencetype='genomic DNA', lsidprefix='EU1SDX202.masked',checkExisting=False)
    #myproc.runProcedure("/home/isgcdata/data/ETAUAXX01.fa.masked",sequencetype='genomic DNA', lsidprefix='ETAUAXX01.masked',checkExisting=False)
    #myproc.runProcedure("/home/isgcdata/data/ETAUAXX02.fa.masked",sequencetype='genomic DNA', lsidprefix='ETAUAXX02.masked',checkExisting=False)
    #myproc.runProcedure("/home/isgcdata/data/ETAUAXX03.fa.masked",sequencetype='genomic DNA', lsidprefix='ETAUAXX03.masked',checkExisting=False)
    #myproc.runProcedure("/home/isgcdata/data/ETAUAXX04.fa.masked",sequencetype='genomic DNA', lsidprefix='ETAUAXX04.masked',checkExisting=False)
    #myproc.runProcedure("/home/isgcdata/data/ETAUAXX05.fa.masked",sequencetype='genomic DNA', lsidprefix='ETAUAXX05.masked',checkExisting=False)
    #myproc.runProcedure("/home/isgcdata/data/ETAUAXX06.fa.masked",sequencetype='genomic DNA', lsidprefix='ETAUAXX06.masked',checkExisting=False)
    #myproc.runProcedure("/home/isgcdata/data/ETAUAXX07.fa.masked",sequencetype='genomic DNA', lsidprefix='ETAUAXX07.masked',checkExisting=False)
    #myproc.runProcedure("/home/isgcdata/data/ETAUAXX08.fa.masked",sequencetype='genomic DNA', lsidprefix='ETAUAXX08.masked',checkExisting=False)
    #myproc.runProcedure("/home/isgcdata/data/ETAUAXX09.fa.masked",sequencetype='genomic DNA', lsidprefix='ETAUAXX09.masked',checkExisting=False)
    #myproc.runProcedure("/home/isgcdata/data/ETAUAXX10.fa.masked",sequencetype='genomic DNA', lsidprefix='ETAUAXX10.masked',checkExisting=False)
    #myproc.runProcedure("/home/isgcdata/data/ETAUAXX11.fa.masked",sequencetype='genomic DNA', lsidprefix='ETAUAXX11.masked',checkExisting=False)
    #myproc.runProcedure("/home/isgcdata/data/ETAUAXX12.fa.masked",sequencetype='genomic DNA', lsidprefix='ETAUAXX12.masked',checkExisting=False)
    #myproc.runProcedure("/home/isgcdata/data/ETAUAXX13.fa.masked",sequencetype='genomic DNA', lsidprefix='ETAUAXX13.masked',checkExisting=False)
    #myproc.runProcedure("/home/isgcdata/data/ETAUAXX14.fa.masked",sequencetype='genomic DNA', lsidprefix='ETAUAXX14.masked',checkExisting=False)
    #myproc.runProcedure("/home/isgcdata/data/ETAUAXX15.fa.masked",sequencetype='genomic DNA', lsidprefix='ETAUAXX15.masked',checkExisting=False)
    #myproc.runProcedure("/home/isgcdata/data/ETAUAXX16.fa.masked",sequencetype='genomic DNA', lsidprefix='ETAUAXX16.masked',checkExisting=False)
    #myproc.runProcedure("/home/isgcdata/data/ETAUAXX16.fa.masked",sequencetype='genomic DNA', lsidprefix='ETAUAXX16.masked',checkExisting=False)
    #myproc.runProcedure("/home/isgcdata/data/EVRD5L302.fa.masked",sequencetype='genomic DNA', lsidprefix='EVRD5L302.masked',checkExisting=False) 
    #myproc.runProcedure("/home/isgcdata/data/EVRD5L301.fa.masked",sequencetype='genomic DNA', lsidprefix='EVRD5L301.masked',checkExisting=False) 
    #myproc.runProcedure("/home/isgcdata/data/EVIDXUB01.fa.masked",sequencetype='genomic DNA', lsidprefix='EVIDXUB01.masked',checkExisting=False)           
    #myproc.runProcedure("/home/isgcdata/data/EVIDXUB02.fa.masked",sequencetype='genomic DNA', lsidprefix='EVIDXUB02.masked',checkExisting=False)       
    #myproc.runProcedure("/home/possumbase/data/possumdownload1106.seq",sequencetype='mRNA SEQUENCE', lsidprefix='',checkExisting=False)       
    #myproc.runProcedure("/home/isgcdata/data/EV41M4G04_masked.fa",sequencetype='genomic DNA', lsidprefix='EV41M4G04_masked.fa',checkExisting=False)       
    #myproc.runProcedure("/home/isgcdata/data/EV41M4G03_masked.fa",sequencetype='genomic DNA', lsidprefix='EV41M4G03_masked.fa',checkExisting=False)       
    #myproc.runProcedure("/home/isgcdata/data/EV41M4G02_masked.fa",sequencetype='genomic DNA', lsidprefix='EV41M4G02_masked.fa',checkExisting=False)       
    #myproc.runProcedure("/home/isgcdata/data/EV41M4G01_masked.fa",sequencetype='genomic DNA', lsidprefix='EV41M4G01_masked.fa',checkExisting=False)       
    #myproc.runProcedure("/home/isgcdata/data/EVWZC7M01_masked.fa",sequencetype='genomic DNA', lsidprefix='EVWZC7M01_masked.fa',checkExisting=False)       
    #myproc.runProcedure("/home/isgcdata/data/EVWZC7M02_masked.fa",sequencetype='genomic DNA', lsidprefix='EVWZC7M02_masked.fa',checkExisting=False)       
    #myproc.runProcedure("/home/isgcdata/data/EWSRYFI01.fa.masked",sequencetype='genomic DNA', lsidprefix='EWSRYFI01.masked',checkExisting=False)       
    #myproc.runProcedure("/home/isgcdata/data/EWSRYFI02.fa.masked",sequencetype='genomic DNA', lsidprefix='EWSRYFI02.masked',checkExisting=False)       
    #myproc.runProcedure("/home/isgcdata/data/EWSRYFI03.fa.masked",sequencetype='genomic DNA', lsidprefix='EWSRYFI03.masked',checkExisting=False)       
    #myproc.runProcedure("/home/isgcdata/data/EWSRYFI04.fa.masked",sequencetype='genomic DNA', lsidprefix='EWSRYFI04.masked',checkExisting=False)       
    #myproc.runProcedure("/home/isgcdata/data/EWYCPOJ01.fa.masked",sequencetype='genomic DNA', lsidprefix='EWYCPOJ01.masked',checkExisting=False)       
    #myproc.runProcedure("/home/isgcdata/data/EWYCPOJ02.fa.masked",sequencetype='genomic DNA', lsidprefix='EWYCPOJ02.masked',checkExisting=False)       
    #myproc.runProcedure("/home/isgcdata/data/EWZ7IHI01.fa.masked",sequencetype='genomic DNA', lsidprefix='EWZ7IHI01.masked',checkExisting=False)       
    #myproc.runProcedure("/home/isgcdata/data/EWZ7IHI02.fa.masked",sequencetype='genomic DNA', lsidprefix='EWZ7IHI02.masked',checkExisting=False)       
    #myproc.runProcedure("/home/isgcdata/data/EWZ7IHI03.fa.masked",sequencetype='genomic DNA', lsidprefix='EWZ7IHI03.masked',checkExisting=False)       
    #myproc.runProcedure("/home/isgcdata/data/EWZ7IHI04.fa.masked",sequencetype='genomic DNA', lsidprefix='EWZ7IHI04.masked',checkExisting=False)       
    #for filename in [ 
    #    'EW47OUJ01',  'EXA8GTI01',  'EXC4CAE01',  'EXERRTD01',
    #    'EW47OUJ02',  'EXA8GTI02',  'EXC4CAE02',  'EXERRTD02'
    #]:
    #for filename in [ 
    #    'EXH74BZ01' , 'EXH74BZ02',  'EXRRBZD01',  'EXRRBZD02'
    #]:
    #    myproc.runProcedure("/home/isgcdata/data/%s.fa.masked"%filename,sequencetype='genomic DNA', lsidprefix='%s.masked'%filename,checkExisting=False)       
    for filename in [ 
        'EX018UA01','EX018UA02', 'EX4TC4D01', 'EX4TC4D02', 'EX585T301', 'EX585T302'   
    ]:
        myproc.runProcedure("/home/isgcdata/data/%s.fa.masked"%filename,sequencetype='genomic DNA', lsidprefix='%s.masked'%filename,checkExisting=False)       




def linkSpotToSequenceMain():
    connection=databaseModule.getConnection()
    myproc = linkSpotToSequenceProcedure(connection)
    #myproc.runProcedure("????")

def linkSpotToGeneMain():
    connection=databaseModule.getConnection()
    myproc = linkSpotToGeneProcedure(connection)
    ##myproc.runProcedure("Agilent.012694_D_20051010.gal","/home/nutrigen/data/Whole_Mouse_Genome_complete_annotations.csv")
    #myproc.runProcedure("print 135 OV_20K.txt","/home/sheepgen/data/microarray/print128annotation.csv",spotnamedbcolumn='accession',spotnamecolumn='estname',geneidcolumnname="human else mouse else rat else nrprotein", creategenes=True,\
    #                 fieldnamesrow=2,datastartsrow=3)
    ##myproc.runProcedure("Clonetrac print 128 ovine 20K.txt","/home/sheepgen/data/microarray/print128annotation.csv",spotnamedbcolumn='accession',spotnamecolumn='estname',geneidcolumnname="human else mouse else rat else nrprotein", creategenes=True,\
    #                 fieldnamesrow=2,datastartsrow=3)
    return


def loadFeatureMain():
    connection=databaseModule.getConnection()
    myproc = loadCSVFeaturesProcedure(connection)
    ##myproc.runProcedure("c:/working/possum/possumbuildinfo.csv","CS44",comment="Import of ESTs as mRNA features of contigs")
    ##myproc.runProcedure("c:/working/possum/CS44snp_results.csv","CS44",comment="Import of CS44 SNPs")
    #myproc.runProcedure("/home/possumbase/data/cs44orfs.seq.csv","CS44",comment="Import of CS44 ORFs")

    

    
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
    #return
    #createProtocolMain()
    loadSequenceMain()
    #linkSpotToSequenceMain()
    #linkSpotToGeneMain()
    #loadFeatureMain()
if __name__ == "__main__":
   main()


