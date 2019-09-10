#
# This module processes some batch imports into the sheepGenomics database , and also contains
# a couple of other misc batch reproting scripts
#
#

import sys
import types
import databaseModule
import csv
import re
import string
import logging
import os
from datetime import date

# platform dependent module search path. (This can't be done in
# a .pth because we do not always want this imported)
#sys.path.append('C:/Python23/lib/site-packages/agbrdf')
import globalConf

# 8/2009
# before any of the brdf modules are loaded, reset the
# logging path if required. Usually python modules are only
# imported once therefore subsequent modules that import
# globalConf will pick up our setting. (It is possible for
# modules to specifically reload a module - if any do this then
# they will pick up the original log path and this section will
# not work)
if __name__ == "__main__":  # (so this block will only execute if this module is being run, not if it is being imported)
    # get and parse command line args
    argDict = dict([ re.split('=',arg) for arg in sys.argv if re.search('=',arg) != None ])
    print "using %s"%str(argDict)

    if 'logpath' in argDict:
       # check it exists and is a directory
       if not os.path.isdir(argDict["logpath"]):
          print "logpath %(logpath)s should be an existing (writeable) directory"%argDict
          sys.exit(1)

    globalConf.LOGPATH=argDict["logpath"]

    print  "(logging reset to %s)"%globalConf.LOGPATH

import agbrdfConf


import logging
import htmlModule
from brdfExceptionModule import brdfException
from annotationModule import uriOb
from GFFParsers import GeneralGFFParser, GFFFileParser
from obmodule import getNewObid
from sequenceModule import bioSequenceOb
from geneticModule import geneticOb, geneticLocationFact
from GFFUtils import transformGappedCoords, loadSequenceFeatures
from listModule import obList
from studyModule import bioDatabaseOb,bioProtocolOb,databaseSearchStudy, genotypeStudy
from ontologyModule import ontologyOb,populate_gene_info_synoyms
from labResourceModule import labResourceOb, geneticTestFact
from dataImportModule import dataSourceOb,importProcedureOb
from biosubjectmodule import bioSubjectOb, bioSampleOb
from dbProcedures import dbprocedure,loadSequenceProcedure,annotateCDSFromDBORFS,loadFeaturesProcedure
from geneIndexProcedures import loadGeneinfo



# set up logger if we want logging
batchmodulelogger = logging.getLogger('sheepbatch')
batchmodulehdlr = logging.FileHandler(os.path.join(globalConf.LOGPATH,'agbrdfBatches.log'))
#hdlr = logging.FileHandler('c:/temp/agbrdfforms.log')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
batchmodulehdlr.setFormatter(formatter)
batchmodulelogger.addHandler(batchmodulehdlr)
batchmodulelogger.setLevel(logging.INFO)




def loadGFFFeatures(infile, lsidprefix):
    """ load features from a GFF file like this :

    BLp19_L3_34	genezilla	mRNA	55	437	.	+	.	mRNA BLp19_L3_34_gz1
    BLp19_L3_34	genezilla	CDS	55	179	17.87	+	0	mRNA BLp19_L3_34_gz1
    BLp19_L3_34	genezilla	CDS	416	437	17.23	+	2	mRNA BLp19_L3_34_gz1
    BLp19_L3_36	genezilla	mRNA	337	655	.	-	.	mRNA BLp19_L3_36_gz1
    BLp19_L3_36	genezilla	CDS	337	360	15.34	-	0	mRNA BLp19_L3_36_gz1

    - which the GFF parser will load as (e.g.)

{'Description': ['mRNA BLp19_L3_34_gz1'], 'Reference': 'BLp19_L3_34',
'GFFFileType': 'genezilla', 'Accession': 'BLP19_L3_34', 'Score': '.', 'Unused1': '.',
'FeatureStart': '55', 'FeatureStop': '437', 'GFFRecordType': 'mRNA', 'Strand': '+'}

{'Description': ['mRNA BLp19_L3_34_gz1'], 'Reference': 'BLp19_L3_34',
'GFFFileType': 'genezilla', 'Accession': 'BLP19_L3_34', 'Score': '17.87', 'Unused1': '0',
'FeatureStart': '55', 'FeatureStop': '179', 'GFFRecordType': 'CDS', 'Strand': '+'}

{'Description': ['mRNA BLp19_L3_34_gz1'], 'Reference': 'BLp19_L3_34',
'GFFFileType': 'genezilla', 'Accession': 'BLP19_L3_34', 'Score': '17.23',
'Unused1': '2', 'FeatureStart': '416', 'FeatureStop': '437', 'GFFRecordType': 'CDS',
'Strand': '+'}

    """

    parser = GeneralGFFParser(infile)
    connection=databaseModule.getConnection()

    # query the database to retrieve all the relevant targets 
    sql = """
        select
           upper(xreflsid),
           xreflsid,
           obid
        from
           biosequenceob
        where
           xreflsid like '""" + lsidprefix + "%%'"

    print "executing %s"%sql           
    linkcursor = connection.cursor()
    linkcursor.execute(sql)

    # make a dictionary of seqs for lookup - key is upper case xreflsid, value is a tuple of (xreflsid,obid)
    targetDict = dict([ (mytuple[0],(mytuple[1],mytuple[2])) for mytuple in linkcursor.fetchall() ])
    print targetDict

    parser.parse()

    gffRecord = parser.nextRecord()

    while (parser.parserState['EOF'],parser.parserState['ERROR']) == (0,0):

        if string.upper("AFT.%s"%gffRecord['Accession']) not in targetDict:
            print "skipping AFT.%s as not in database"%gffRecord['Accession']
        else:
            print "processing %s"%str(gffRecord)

            # need to insert cds as lower case
            if gffRecord['GFFRecordType'] == 'CDS':
                gffRecord['GFFRecordType'] = 'cds'
                


            obid = getNewObid(connection)

            sql = """
                insert into bioSequenceFeatureFact(obid,biosequenceob,xreflsid,featuretype,featurestrand,featurestart,featurestop,featurecomment,
                evidence,featurelength)
                values(%(obid)s,%(biosequenceob)s,%(xreflsid)s,%(featuretype)s,%(featurestrand)s,%(featurestart)s,%(featurestop)s,%(featurecomment)s,
                %(evidence)s,%(featurelength)s)
                """
            print "executing %s"%(sql%{
                'obid' : obid,
                'biosequenceob' : targetDict[string.upper("AFT.%s"%gffRecord['Accession'])][1],
                'xreflsid' : "%s.%s"%(targetDict[string.upper("AFT.%s"%gffRecord['Accession'])][0],gffRecord['GFFRecordType']), 
                'featuretype' : gffRecord['GFFRecordType'],
                'featurestrand' : {'+' : 1, '-' : -1}[gffRecord['Strand']],
                'featurestart' : gffRecord['FeatureStart'],
                'featurestop' : gffRecord['FeatureStop'],
                'featurecomment' : gffRecord['Description'],
                'evidence' : "%(GFFFileType)s %(Score)s %(Unused1)s"%gffRecord,
                'featurelength' : int(gffRecord['FeatureStop']) - int(gffRecord['FeatureStart'])
                })

            
            linkcursor.execute(sql,{
                'obid' : obid,
                'biosequenceob' : targetDict[string.upper("AFT.%s"%gffRecord['Accession'])][1],
                'xreflsid' : "%s.%s"%(targetDict[string.upper("AFT.%s"%gffRecord['Accession'])][0],gffRecord['GFFRecordType']), 
                'featuretype' : gffRecord['GFFRecordType'],
                'featurestrand' : {'+' : 1, '-' : -1}[gffRecord['Strand']],
                'featurestart' : gffRecord['FeatureStart'],
                'featurestop' : gffRecord['FeatureStop'],
                'featurecomment' : string.join(gffRecord['Description']),
                'evidence' : "%(GFFFileType)s %(Score)s %(Unused1)s"%gffRecord,
                'featurelength' : int(gffRecord['FeatureStop']) - int(gffRecord['FeatureStart'])
                })

            connection.commit()

        gffRecord = parser.nextRecord()

        

    if parser.parserState['ERROR'] ==1 :
        print str(parser.parserState)


def loadGFFGeneTracks(filename,startline=1,lsidprefix = 'NCBI' , mapname = 'Btau_3.0'  , speciesname = 'Bos taurus', taxid = 9616):
    """
example :

BTA1	NCBI_GENE	gene	27290	28224	.	+	.	Gene LOC787305; fastadesc "hypothetical protein LOC787305"
BTA1	NCBI_GENE	gene	37236	38165	.	+	.	Gene LOC787328; fastadesc "hypothetical protein LOC787328"
BTA1	NCBI_GENE	gene	40518	42175	.	+	.	Gene LOC787356; fastadesc "hypothetical protein LOC787356"
BTA1	NCBI_GENE	gene	61890	62822	.	-	.	Gene LOC518213; fastadesc "similar to olfactory receptor 1160"
BTA1	NCBI_GENE	gene	82163	83119	.	-	.	Gene LOC787394; fastadesc "hypothetical protein LOC787394"
BTA1	NCBI_GENE	gene	102427	158259	.	-	.	Gene LOC507243; fastadesc "similar to chloride intracellular channel 6"
BTA1	NCBI_GENE	gene	241056	241601	.	-	.	Gene LOC618840; fastadesc "similar to chromobox homolog 3"


which the GFF parser will load like this :


{'Description': ['Gene LOC787305', 'fastadesc hypothetical protein LOC787305'], 'Reference': 'BTA1', 'GFFFileType': 'NCBI_GENE', 'Accession': 'LOC787305', 'Score': '.', 'Unused1': '.', 'FeatureStart': '27290', 'FeatureStop': '28224', 'GFFRecordType': 'gene', 'Strand': '+'}
{'Description': ['Gene LOC787328', 'fastadesc hypothetical protein LOC787328'], 'Reference': 'BTA1', 'GFFFileType': 'NCBI_GENE', 'Accession': 'LOC787328', 'Score': '.', 'Unused1': '.', 'FeatureStart': '37236', 'FeatureStop': '38165', 'GFFRecordType': 'gene', 'Strand': '+'}
{'Description': ['Gene LOC787356', 'fastadesc hypothetical protein LOC787356'], 'Reference': 'BTA1', 'GFFFileType': 'NCBI_GENE', 'Accession': 'LOC787356', 'Score': '.', 'Unused1': '.', 'FeatureStart': '40518', 'FeatureStop': '42175', 'GFFRecordType': 'gene', 'Strand': '+'}
{'Description': ['Gene LOC518213', 'fastadesc similar to olfactory receptor 1160'], 'Reference': 'BTA1', 'GFFFileType': 'NCBI_GENE', 'Accession': 'LOC518213', 'Score': '.', 'Unused1': '.', 'FeatureStart': '61890', 'FeatureStop': '62822', 'GFFRecordType': 'gene', 'Strand': '-'}
{'Description': ['Gene LOC787394', 'fastadesc hypothetical protein LOC787394'], 'Reference': 'BTA1', 'GFFFileType': 'NCBI_GENE', 'Accession': 'LOC787394', 'Score': '.', 'Unused1': '.', 'FeatureStart': '82163', 'FeatureStop': '83119', 'GFFRecordType': 'gene', 'Strand': '-'}
"""
    # get database connection
    connection=databaseModule.getConnection()
    insertCursor = connection.cursor()

    # get all the targets in memory
    sql = """
    select split_part(xreflsid,'.',2) , obid , xreflsid from
    geneticob
    """
    insertCursor.execute(sql)
    targets = insertCursor.fetchall()
    targetDict = {}
    for row in targets:
        targetDict.update({
            row[0] : (row[1],row[2])
        })

   
    gffparser = GFFFileParser(filename)
    # read ahead
    gffparser.parse()
    gffDict =  gffparser.nextRecord()

    recordCount = 0
    while (gffparser.parserState["EOF"], gffparser.parserState["ERROR"])== (0,0):    
        recordCount += 1

        print str(gffDict)

        #if we do not have the gene set up then create it
        if gffDict['Accession'] not in targetDict:
            gene = geneticOb()
            gene.initNew(connection)
            gene.databaseFields.update( {
                'xreflsid' : "NCBI.%s"%gffDict['Accession'],
                'geneticobname' :   gffDict['Accession'],
                'geneticobtype' : 'Gene',
                'geneticobdescription' : re.sub('fastadesc','',gffDict['Description'][1]),
                'geneticobsymbols' :   gffDict['Accession'],
                'obcomment' : 'Created as part of import of NCBI Bovine gene positions'
            })
            gene.insertDatabase(connection)
            targetDict[gffDict['Accession']] = (gene.databaseFields['obid'],gene.databaseFields['xreflsid'])
                

            

        # insert the location
        sql = """
                insert into geneticlocationfact(
                xreflsid,geneticob,speciesname,speciestaxid,
                strand,locationstart,locationstop,
                chromosomename,
                mapname) values (                
                %(xreflsid)s,%(geneticob)s,%(speciesname)s,%(speciestaxid)s,
                %(strand)s,%(locationstart)s,%(locationstop)s,
                %(chromosomename)s,
                %(mapname)s)
        """
        insertCursor.execute(sql,{
                'xreflsid' : "%s.location"%(targetDict[gffDict['Accession']][1]),
                'geneticob' : targetDict[gffDict['Accession']][0],
                'speciesname' : 'Bos taurus',
                'speciestaxid' : 9913,
                'strand' : gffDict['Strand'],
                'locationstart' : gffDict['FeatureStart'],
                'locationstop' : gffDict['FeatureStop'],
                'chromosomename' : gffDict['Reference'],
                'evidence' : gffDict['GFFFileType'],
                'mapname' : mapname
                })
        connection.commit()
        gffDict =  gffparser.nextRecord()

    if gffparser.parserState["ERROR"] != 0:
        print str(gffparser.parserState)
        

    insertCursor.close()
    connection.close()


def loadAffyProbes(infile,lsidprefix,targetdatasourcename):
    """ a load of AffyProbes from a file like this :

    Probe Set ID	probe x	probe y	probe interrogation position	probe sequence	target strandedness
AFFX-Bt-A00196-1_s_at	336	349	1297	GAAGCAACGCGTAAACTCGACCCGA	Antisense
AFFX-Bt-A00196-1_s_at	450	475	1325	GTCCGATCACCTGCGTCAATGTAAT	Antisense
AFFX-Bt-A00196-1_s_at	201	225	1341	CAATGTAATGTTCTGCGACGCTCAC	Antisense
AFFX-Bt-A00196-1_s_at	22	49	1391	ATGTGCTGTGCCTGAACCGTTATTA	Antisense

(See also fungal array : 
Probe Set Name	Probe X	Probe Y	Probe Interrogation Position	Probe Sequence	Target Strandedness	Probe Type	Reference Sequence Name	Start Pos	End Pos
CS3700406800001_at	10	1	36	CTGAAGGAAAGTCCCCTTATTGCCT	Antisense	PM	CS3700406800001	24	48
CS32000001FFA1A.2.R_at	12	1	51	CATCCCGGTTTATAGAATTTTATTG	Antisense	PM	CS32000001FFA1A.2.R	39	63
CS32000001FFB1D.2_at	14	1	38	CCGAAACCCCATATTATTATTCAGG	Antisense	PM	CS32000001FFB1D.2	26	50)


    Each of these probes is loaded and initialised with an AffyTarget - AffyProbe relationship, and we
    also load the probsets as microarrayspotfacts at this time, together with spotfact-sequence link.
    The LSID of the probe is the LSID of the target , with the interrogation position attached.
    These probes are not initialised as microarray spot facts - this is a seperate update.

example : 

loadAffyProbes("/home/sheepgen/data/microarray/Bovine_probe_tab","Affymetrix.Bovine.ProbeSet","/data/home/seqstore/agbrdf/bovine/Bovine_consensus")
"""
    
    reader = open(infile, "rb")
    connection=databaseModule.getConnection()


    # create a data import - this needs an importProcedure and a dataSource
    # get or create the import procedure
    importProcedure = importProcedureOb()        
    try:
        importProcedure.initFromDatabase("agresearchbatches.loadAffyProbes",connection)
    except brdfException:
        importProcedure.initNew(connection)
        importProcedure.databaseFields.update ( {
            'xreflsid' : "agresearchbatches.loadAffyProbes",
             'procedurename' : "agresearchbatches.loadAffyProbes",
        })
        importProcedure.insertDatabase(connection)        


    dataSource = dataSourceOb()
    dataSource.initNew(connection,'Tab delimited text')
    dataSource.databaseFields.update({
        'xreflsid' : infile,
        'numberoffiles' : 1
    })        
    dataSource.insertDatabase(connection)

    
        
    rowCount = 0

    # query the database to retrieve all the relevant targets - these have the same name
    # as the probesets
    # - e.g. 
#   obid   |              sequencename
#----------+----------------------------------------
# 41793541 | consensus:Bovine:BtAffx.1.14.S1_at
# 41793539 | consensus:Bovine:Bt.9877.1.S1_at
# 41793537 | consensus:Bovine:BtAffx.1.1.S1_at

    sql = """
        select
           b.obid,
           replace(split_part(b.sequencename,':',3),';','') as sequencename
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
       


    linkedtargets=[]    
    probesets = []
    for row in reader:
        #if rowCount%500 == 1:
        row = row.strip()
        print "processing row %s"%rowCount
        print row
        rowCount += 1
        if rowCount == 1:
            fieldNames = re.split('\t',row)
            fieldNames = [item.lower() for item in fieldNames]
            print fieldNames
            continue
        dataFields = re.split('\t',row)
        fieldDict=dict(zip(fieldNames,dataFields))

        # handle variations in column headings
        if 'probe set name' not in fieldDict:
            if 'probe set id' in fieldDict:
                fieldDict['probe set name'] = fieldDict['probe set id']
            else:
                raise brdfException("error : input file does not contains 'probe set id' or 'probe set name'")

        # insert the probe sequence
        bioSequence = bioSequenceOb()
        bioSequence.initNew(connection)
        bioSequence.databaseFields.update(fieldDict)
        bioSequence.databaseFields['seqlength'] = len(fieldDict['probe sequence'])
        bioSequence.databaseFields['seqstring'] = fieldDict['probe sequence']
        bioSequence.databaseFields['sequencetype'] = 'Affy Probe Oligo'
        bioSequence.databaseFields['xreflsid'] = "%(probe set name)s.%(probe interrogation position)s"%fieldDict
        bioSequence.insertDatabase(connection)

        # link to data source
        dataSource.addImportFunction(bioSequence,importProcedure,connection)


        # insert details
        for factName in ['Probe X','Probe Y','Probe Interrogation Position','Target Strandedness','Probe Type','Reference Sequence Name','Start Pos','End Pos']:
            factName = factName.lower()
            if factName in fieldDict:
                bioSequence.addFact(connection,'Affy Probe Details',factName,fieldDict[factName],checkExisting=False)

        # link the probe to the target
        # for example trying to link consensus:Bovine:Bt.1000.1.S1_at; to Bt.1000.1.S1_at
        for targetseq in targetseqs:
            if fieldDict['probe set name'] == targetseq[1]:
                print "linking %s"%(targetseq[1])
                linkedtargets.append(targetseq[1])
                # in case this  did not work , the update below can be done in a batch file. First , do the following
                # update : 
                # update biosequenceob set obkeywords = split_part(xreflsid,'_at',1)||'_at' where sequencetype =  'Affy Probe Oligo';
                # 
                # then the following SQL will generate the batch update : 
                # batch file : 
#                select 'insert into predicatelink(subjectob,objectob,xreflsid,predicate,voptypeid) ' ||
#                    'values('||
#                    bp.obid||','||
#                    bt.obid||','||
#                    ''''||
#                    bt.xreflsid||':'||bp.xreflsid||
#                    ''','''||
#                    'AFFYPROBE-AFFYTARGET' ||
#                    ''',377)'
#                from
#                    biosequenceob bp join biosequenceob bt on
#                    bt.xreflsid like 'Affymetrix.Bovine%' and
#                    bt.sequencetype = 'mRNA SEQUENCE' and
#                    bp.sequencetype = 'Affy Probe Oligo' and
#                    bt.xreflsid  = 'Affymetrix.Bovine.consensus:Bovine:'||bp.obkeywords;
                sql="""
                    insert into predicatelink(subjectob,objectob,xreflsid,predicate,voptypeid)
                    values(%(subjectob)s,%(objectob)s,%(xreflsid)s,'AFFYPROBE-AFFYTARGET',377)
                    """
                linkcursor.execute(sql,{'subjectob' : bioSequence.databaseFields['obid'], 'objectob' : targetseq[0] , 'xreflsid' : '%s:%s'%(targetseq[1],bioSequence.databaseFields['xreflsid'])})
                connection.commit()        
            
    connection.close()    


        

def loadFungalAffyProbes(infile,lsidprefix,targetdatasourcename):
    """ a load of AffyProbes from a file like this :
Probe Set Name	Probe X	Probe Y	Probe Interrogation Position	Probe Sequence	Target Strandedness	Probe Type	Reference Sequence Name	Start Pos	End Pos
CS3700406800001_at	10	1	36	CTGAAGGAAAGTCCCCTTATTGCCT	Antisense	PM	CS3700406800001	24	48
CS32000001FFA1A.2.R_at	12	1	51	CATCCCGGTTTATAGAATTTTATTG	Antisense	PM	CS32000001FFA1A.2.R	39	63
CS32000001FFB1D.2_at	14	1	38	CCGAAACCCCATATTATTATTCAGG	Antisense	PM	CS32000001FFB1D.2	26	50
    Each of these probes is loaded and initialised with an AffyTarget - AffyProbe relationship, and we
    also load the probsets as microarrayspotfacts at this time, together with spotfact-sequence link.
    The LSID of the probe is the LSID of the target , with the interrogation position attached.
    These probes are not initialised as microarray spot facts - this is a seperate update.
"""
    
    reader = open(infile, "rb")
    connection=databaseModule.getConnection()
        
    rowCount = 0

    # query the database to retrieve all the relevant targets - these have the same name
    # as the probesets
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

    print "got %d seqs"%linkcursor.rowcount
       


    linkedtargets=[]    
    probesets = []
    for row in reader:
        #if rowCount%500 == 1:
        row = row.strip()
        print "processing row %s"%rowCount
        print row
        rowCount += 1
        if rowCount == 1:
            fieldNames = re.split('\t',row)
            print fieldNames
            continue
        dataFields = re.split('\t',row)
        fieldDict=dict(zip(fieldNames,dataFields))

        # insert the probe sequence
        bioSequence = bioSequenceOb()
        bioSequence.initNew(connection)
        bioSequence.databaseFields.update(fieldDict)
        bioSequence.databaseFields['seqlength'] = len(fieldDict['Probe Sequence'])
        bioSequence.databaseFields['seqstring'] = fieldDict['Probe Sequence']
        bioSequence.databaseFields['sequencetype'] = 'Affy Probe Oligo'
        bioSequence.databaseFields['xreflsid'] = "%(Probe Set Name)s.%(Probe Interrogation Position)s"%fieldDict
        bioSequence.insertDatabase(connection)

        # insert details
        for factName in ['Probe X','Probe Y','Probe Interrogation Position','Target Strandedness','Probe Type','Reference Sequence Name','Start Pos','End Pos']:
            bioSequence.addFact(connection,'Affy Probe Details',factName,fieldDict[factName],checkExisting=False)

        # link the probe to the target
        for targetseq in targetseqs:
            if fieldDict['Probe Set Name'] == targetseq[1]:
                print "linking %s"%(targetseq[1])
                linkedtargets.append(targetseq[1])
                sql="""
                    insert into predicatelink(subjectob,objectob,xreflsid,predicate,voptypeid)
                    values(%(subjectob)s,%(objectob)s,%(xreflsid)s,'AFFYPROBE-AFFYTARGET',377)
                    """
                linkcursor.execute(sql,{'subjectob' : bioSequence.databaseFields['obid'], 'objectob' : targetseq[0] , 'xreflsid' : '%s:%s'%(targetseq[1],bioSequence.databaseFields['xreflsid'])})
                connection.commit()        
            
        rowCount += 1

        """
        note that currently the updatwes to set up the array from this are done seperately as follows :

        /*
* set up a labresource record for the array as a whole
*/
insert into labresourceob (
 xreflsid,
 obkeywords,
 resourcename,
 resourcetype,
 resourcedescription
) values (
 'Affymetrix.Lp19-Lpa530240N (AgResearch Fungal Array)',
 'Affymetrix.Lp19-Lpa530240N (AgResearch Fungal Array)',
 'Affymetrix.Lp19-Lpa530240N (AgResearch Fungal Array)',
 'microarray',
 'Affymetrix Fungal Array at 6/2007');

/*
* set up microarray spot facts for each probe-set.
* These are obtained from the target sequences
*/
update biosequenceob set sequencedescription = 'Target sequence for Affymetrix array p19-Lpa530240N'
where xreflsid like 'AFT.%_at' and
length(sequencedescription) = 0;

insert into microarrayspotfact(
 xreflsid       ,
 labresourceob  ,
 accession
)
select
   lr.xreflsid||'.'||bs.sequencename,
   lr.obid,
   bs.sequencename
from
   labresourceob lr join biosequenceob bs on
   lr.xreflsid = 'Affymetrix.Lp19-Lpa530240N (AgResearch Fungal Array)' and
   bs.xreflsid like 'AFT.%_at' and
   bs.sequencetype = 'mRNA SEQUENCE' ;


/*
 generate update 
to set up the probeset-probe link
*/

update biosequenceob set obkeywords = substring( xreflsid from '(.*_at)\..*$' ) where sequencetype = 'Affy Probe Oligo';
                select 'insert into predicatelink(subjectob,objectob,xreflsid,predicate,voptypeid) ' ||
                    'values('||
                    bp.obid||','||
                    msf.obid||','||
                    ''''||
                    bp.xreflsid||':'||msf.xreflsid||
                    ''','''||
                    'AFFYPROBE-ARRAYPROBESET' ||
                    ''',378);'
                from
                    biosequenceob bp join microarrayspotfact msf on
                    bp.sequencetype = 'Affy Probe Oligo' and
                    msf.accession  = bp.obkeywords;


/*
 generate update 
to set up an ARRAYSPOT-SEQUENCE link between the spots and the target sequences
*/


                select 'insert into predicatelink(subjectob,objectob,xreflsid,predicate,voptypeid) ' ||
                    'values('||
                    msf.obid||','||
                    bp.obid||','||
                    ''''||
                    msf.xreflsid||':'||bp.xreflsid||
                    ''','''||
                    'ARRAYSPOT-SEQUENCE' ||
                    ''',265);'
                from
                    biosequenceob bp join microarrayspotfact msf on
                    bp.sequencedescription = 'Target sequence for Affymetrix array p19-Lpa530240N' and
                    msf.accession  = bp.sequencename;                 
   


   """

    connection.close()





def loadFungalAffyAnnotation(infile,targetdatasourcename):
    """ a load of AffyProbes from a CSV file like this :
Reference Sequence Name	Probe Set Name	Description	Species (a priori)	Species classification (E=endophyte, R=ryegrass, G=Glomeromycetes, B=bacterial control, U=unknown, Junk=not detectable)	Orientation (a priori: F=forward, R=reverse, U=unknown)	Original Sequence Length	Cross-hyb Sequences (# cross-hyb probes, average # conserved bases per cross-hyb probe)	GenBank Protein ID 4/9/06	GenBank Protein Description	GenBank Protein EValue	RefSeq Nucleotide IDs, top 5 hits (31/10/06)	Entrez Gene IDs (31/10/06)	Fusarium Genome Database ID 6/9/06	Fusarium Genome Database Description	Fusarium Genome Database Evalue	CPS NRPS Blast Hit ID(s)	CPS NRPS Blast Hit Desc(s)	CPS NRPS Blast Hit Evalue(s)	InterproScan Hit ID(s) 7/9/06	InterproScan Hit Description(s)	GO Molecular Function ID(s)	GO Molecular Function Description(s)	GO Biological Process ID(s)	GO Biological Process Description(s)	GO Cellular Component ID(s)	GO Cellular Component Description(s)	SignalP Signal Peptide Probability (S)	SignalP Signal Peptide Length	keyword	source	submitter	E_RG, PMA calls	FL1-F, PMA calls	LP19F, PMA calls	54-1, PMA calls	ACKO42, PMA calls	FL1-T, PMA calls	FL1-L, PMA calls	G9, PMA calls	LP19L, PMA calls	NC25KO, PMA calls
00009PSPCR0000001	00009PSPCR0000001_s_at	NRPS degenerate PCR contig	Fungal	E	F	270	Lp19_ADCY_sn1 (11 25)	CAB64345	adenylate cyclase, ACY [Metarhizium anisopliae var. anisopliae]	3.00E-39	XM_960187; XM_365053; XM_329422; XM_381410; XM_501072	3881413; 2680942; 2711296; 2782516; 2907024	fg12289	probable adenylate cyclase, Contig fg_contig_1.62	1.00E-40				IPR001054	Adenylyl cyclase class-3/4/guanylyl cyclase	GO:0016849; GO:0016740	phosphorus-oxygen lyase activity; transferase activity	GO:0009190; GO:0007242	cyclic nucleotide biosynthesis; intracellular signaling cascade			0.511	20		NRPS degenerate PCR contigs	Christine Voisey	AAA	PPP	APP	AAA	AAA	AAA	AAA	AAA	AAA	AAA
00009PSPCR0000002	00009PSPCR0000002_at	NRPS degenerate PCR contig	Fungal	E	F	431		AAL22238	putative protease [Salmonella typhimurium LT2] ref|NP_462279.1| putative protease [Salmonella typhimurium LT2]	1.00E-13											GO:0008233	peptidase activity								NRPS degenerate PCR contigs	Christine Voisey	AAA	AAA	AAA	AAA	AAA	AAA	AAA	AAA	AAA	AAA
00009PSPCR0000003.R	00009PSPCR0000003.R_at	NRPS degenerate PCR contig;  reverse complemented	Fungal	E	U	386					XM_326675; XM_956456; XM_363056; XM_654756; XM_748863	2708408; 3877672; 2678872; 2875486; 3510729															0.828	64		NRPS degenerate PCR contigs	Christine Voisey	PAA	PPP	APP	PPP	PPA	PPP	PPP	PPP	AAP	PPP
00009PSPCR0000003	00009PSPCR0000003_at	NRPS degenerate PCR contig	Fungal	Junk	U	386					XM_326675; XM_956456; XM_363056; XM_654756; XM_748863	2708408; 3877672; 2678872; 2875486; 3510729															0.828	64		NRPS degenerate PCR contigs	Christine Voisey	AAA	AAA	AAA	AAA	AAA	AAA	AAA	AAA	AAA	AAA"""


    reader = csv.reader(open(infile, "rb"))
    connection=databaseModule.getConnection()

    # query the database to retrieve all the relevant targets - these have the same name
    # as the probesets
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


    # query the database to retrieve all the GO terms
    sql = """
        select
           otf.termname,
           otf.obid
        from
           ontologytermfact otf
        where
           xreflsid like 'Ontology.GO.%'
        """

    print "executing %s"%sql              
    linkcursor = connection.cursor()
    linkcursor.execute(sql)
    goterms = linkcursor.fetchall()
    goDict = dict(goterms)

    # initialise ontologies
    gofunction = ontologyOb()
    gofunction.initFromDatabase('Ontology.GO.Molecular Function',connection)
    goprocess = ontologyOb()
    goprocess.initFromDatabase('Ontology.GO.Biological Process',connection)
    gocomponent = ontologyOb()
    gocomponent.initFromDatabase('Ontology.GO.Cellular Component',connection)
    
    


    ####### get / set up all the database search studies involved
    # first set up databases.....
    genbanknr = bioDatabaseOb()
    try:
        genbanknr.initFromDatabase('NCBI.Non-redundant Protein (NR)',connection)
    except brdfException:
        if genbanknr.obState['ERROR'] == 1:
            # could not find so create
            genbanknr.initNew(connection)
            genbanknr.databaseFields.update ( {
                    'xreflsid' : 'NCBI.Non-redundant Protein (NR)',
                    'databasename' : 'NCBI Non-redundant Protein (NR)',
                    'databasedescription' : 'All non-redundant GenBank CDS translations+PDB+SwissProt+PIR+PRF excluding environmental samples  ',
                    'databasetype' : 'Protein Sequence database'                            
            })
            genbanknr.insertDatabase(connection)
        else:
            # some other error - re-raise
            raise brdfException, genbanknr.obState['MESSAGE']


    fungalrefseqs = bioDatabaseOb()
    try:
        fungalrefseqs.initFromDatabase('NCBI.Fungal mRNA Refseqs',connection)
    except brdfException:
        if fungalrefseqs.obState['ERROR'] == 1:
            # could not find so create
            fungalrefseqs.initNew(connection)
            fungalrefseqs.databaseFields.update ( {
                    'xreflsid' : 'NCBI.Fungal mRNA Refseqs',
                    'databasename' : 'NCBI Fungal mRNA Refseqs',
                    'databasedescription' : 'NCBI Fungal mRNA Refseqs',
                    'databasetype' : 'Nucleotide Sequence database'                            
            })
            fungalrefseqs.insertDatabase(connection)
        else:
            # some other error - re-raise
            raise brdfException, fungalrefseqs.obState['MESSAGE']


    fusariumgenome = bioDatabaseOb()
    try:
        fusariumgenome.initFromDatabase('MIPS.Fusarium Genome Predicted Proteins',connection)
    except brdfException:
        if fusariumgenome.obState['ERROR'] == 1:
            # could not find so create
            fusariumgenome.initNew(connection)
            fusariumgenome.databaseFields.update ( {
                    'xreflsid' : 'MIPS.Fusarium Genome Predicted Proteins',
                    'databasename' : 'MIPS Fusarium Genome Predicated Proteins Database',
                    'databasedescription' : 'MIPS Fusarium Genome Predicated Proteins Database',
                    'databasetype' : 'Protein Sequence database'                            
            })
            fusariumgenome.insertDatabase(connection)
        else:
            # some other error - re-raise
            raise brdfException, fusariumgenome.obState['MESSAGE']


    cpsnrps = bioDatabaseOb()
    try:
        cpsnrps.initFromDatabase('CPS NRPS Predicted Proteins',connection)
    except brdfException:
        if cpsnrps.obState['ERROR'] == 1:
            # could not find so create
            cpsnrps.initNew(connection)
            cpsnrps.databaseFields.update ( {
                    'xreflsid' : 'CPS NRPS Predicted Proteins',
                    'databasename' : 'CPS NRPS Predicted Proteins',
                    'databasedescription' : 'CPS NRPS Predicted Proteins',
                    'databasetype' : 'Protein Sequence database'                            
            })
            cpsnrps.insertDatabase(connection)
        else:
            # some other error - re-raise
            raise brdfException, cpsnrps.obState['MESSAGE']


    interpro = bioDatabaseOb()
    try:
        interpro.initFromDatabase('Interpro',connection)
    except brdfException:
        if interpro.obState['ERROR'] == 1:
            # could not find so create
            interpro.initNew(connection)
            interpro.databaseFields.update ( {
                    'xreflsid' : 'Interpro',
                    'databasename' : 'Interpro',
                    'databasedescription' : 'InterPro is a database of protein families, domains and functional sites in which identifiable features found in known proteins can be applied to unknown protein sequences',
                    'databasetype' : 'Protein Family database'                            
            })
            interpro.insertDatabase(connection)
        else:
            # some other error - re-raise
            raise brdfException, interpro.obState['MESSAGE']                

    ########################### end setup of databases ###########################333
        

    # set up the database search studies if required - first the protocols
    blastxprotocol = bioProtocolOb()
    try:
        blastxprotocol.initFromDatabase('protocol.blastx.Standard AgResearch cross species blastx protocol',connection)
    except brdfException:
        if blastxprotocol.obState['ERROR'] == 1:
            # could not find so create
            blastxprotocol.initNew(connection)
            blastxprotocol.databaseFields.update ( {
                    'xreflsid' : 'protocol.blastx.Standard AgResearch cross species blastx protocol',
                    'protocolname' : 'Standard AgResearch cross species blastx protocol',
                    'protocoltype' : 'BLAST SEARCH',
                    'protocoldescription' : 'Standard AgResearch cross species blastx protocol',
                    'protocoltext' : 'parameters = -e 1.0e-6 -v 5 -b 5'         
            })
            blastxprotocol.insertDatabase(connection)
        else:
            # some other error - re-raise
            raise brdfException, blastxprotocol.obState['MESSAGE']


    # set up the database search studies if required - first the protocols
    blastnprotocol = bioProtocolOb()
    try:
        blastnprotocol.initFromDatabase('protocol.blastn.Standard AgResearch cross species blastn protocol',connection)
    except brdfException:
        if blastnprotocol.obState['ERROR'] == 1:
            # could not find so create
            blastnprotocol.initNew(connection)
            blastnprotocol.databaseFields.update ( {
                    'xreflsid' : 'protocol.blastn.Standard AgResearch cross species blastn protocol',
                    'protocolname' : 'Standard AgResearch cross species blastn protocol',
                    'protocoltype' : 'BLAST SEARCH',
                    'protocoldescription' : 'Standard AgResearch cross species blastn protocol',
                    'protocoltext' : 'parameters = -e 1.0e-6 -v 5 -b 5'         
            })
            blastnprotocol.insertDatabase(connection)
        else:
            # some other error - re-raise
            raise brdfException, blastnprotocol.obState['MESSAGE']


    # set up the database search studies if required - first the protocols
    iprscanprotocol = bioProtocolOb()
    try:
        iprscanprotocol.initFromDatabase('protocol.iprscan.Standard AgResearch cross species iprscan protocol',connection)
    except brdfException:
        if iprscanprotocol.obState['ERROR'] == 1:
            # could not find so create
            iprscanprotocol.initNew(connection)
            iprscanprotocol.databaseFields.update ( {
                    'xreflsid' : 'protocol.iprscan.Standard AgResearch cross species iprscan protocol',
                    'protocolname' : 'Standard AgResearch cross species iprscan protocol',
                    'protocoltype' : 'BLAST SEARCH',
                    'protocoldescription' : 'Standard AgResearch cross species iprscan protocol',
                    'protocoltext' : 'parameters = -e 1.0e-6 -v 5 -b 5'         
            })
            iprscanprotocol.insertDatabase(connection)
        else:
            # some other error - re-raise
            raise brdfException, iprscanprotocol.obState['MESSAGE']        

        

        



    ############################### end setup of protocols ############################        
        

    genbankblastx = databaseSearchStudy()
    try:
        genbankblastx.initFromDatabase('database search.AFT.Microarray Annotation.Genbank NR Protein Blast',connection)
    except brdfException:
        if genbankblastx.obState['ERROR'] == 1:
            # could not find so create
            genbankblastx.initNew(connection)
            genbankblastx.databaseFields.update ( {
                    'biodatabaseob' : genbanknr.databaseFields['obid'],
                    'bioprotocolob' : blastxprotocol.databaseFields['obid'],
                    'xreflsid' : 'database search.AFT.Microarray Annotation.Genbank NR Protein Blast',
                    'studyname' : 'AFT Microarray Annotation Genbank NR Protein Blast',
                    'studytype' : 'Blast',
                    'rundate' : '01-10-2006',
                    'runby' : 'Anar Khan'         
            })
            genbankblastx.insertDatabase(connection)
        else:
            # some other error - re-raise
            raise brdfException, genbankblastx.obState['MESSAGE']

    refseqblastn = databaseSearchStudy()
    try:
        refseqblastn.initFromDatabase('database search.AFT.Microarray Annotation.Genbank Fungal Refseq Blast',connection)
    except brdfException:
        if refseqblastn.obState['ERROR'] == 1:
            # could not find so create
            refseqblastn.initNew(connection)
            refseqblastn.databaseFields.update ( {
                    'biodatabaseob' : fungalrefseqs.databaseFields['obid'],
                    'bioprotocolob' : blastnprotocol.databaseFields['obid'],
                    'xreflsid' : 'database search.AFT.Microarray Annotation.Genbank Fungal Refseq Blast',
                    'studyname' : 'AFT Microarray Annotation Genbank Fungal Refseq Blast',
                    'studytype' : 'Blast',
                    'rundate' : '01-10-2006',
                    'runby' : 'Anar Khan'         
            })
            refseqblastn.insertDatabase(connection)
        else:
            # some other error - re-raise
            raise brdfException, refseqblastn.obState['MESSAGE']


    fusariumblastx = databaseSearchStudy()
    try:
        fusariumblastx.initFromDatabase('database search.AFT.Microarray Annotation.MIPS Fusarium Genome Predicted Protein Blast',connection)
    except brdfException:
        if fusariumblastx.obState['ERROR'] == 1:
            # could not find so create
            fusariumblastx.initNew(connection)
            fusariumblastx.databaseFields.update ( {
                    'biodatabaseob' : fusariumgenome.databaseFields['obid'],
                    'bioprotocolob' : blastxprotocol.databaseFields['obid'],
                    'xreflsid' : 'database search.AFT.Microarray Annotation.MIPS Fusarium Genome Predicted Protein Blast',
                    'studyname' : 'AFT Microarray Annotation MIPS Fusarium Genome Predicted Protein Blast',
                    'studytype' : 'Blast',
                    'rundate' : '01-10-2006',
                    'runby' : 'Anar Khan'         
            })
            fusariumblastx.insertDatabase(connection)
        else:
            # some other error - re-raise
            raise brdfException, fusariumblastx.obState['MESSAGE']


    cpsnrpsblastx = databaseSearchStudy()
    try:
        cpsnrpsblastx.initFromDatabase('database search.AFT.Microarray Annotation.CPS NRPS Predicted Protein Blast',connection)
    except brdfException:
        if cpsnrpsblastx.obState['ERROR'] == 1:
            # could not find so create
            cpsnrpsblastx.initNew(connection)
            cpsnrpsblastx.databaseFields.update ( {
                    'biodatabaseob' : cpsnrps.databaseFields['obid'],
                    'bioprotocolob' : blastxprotocol.databaseFields['obid'],
                    'xreflsid' : 'database search.AFT.Microarray Annotation.CPS NRPS Predicted Protein Blast',
                    'studyname' : 'AFT Microarray Annotation CPS NRPS Predicted Protein Blast',
                    'studytype' : 'Blast',
                    'rundate' : '01-10-2006',
                    'runby' : 'Anar Khan'         
            })
            cpsnrpsblastx.insertDatabase(connection)
        else:
            # some other error - re-raise
            raise brdfException, cpsnrpsblastx.obState['MESSAGE']


    iprscan = databaseSearchStudy()
    try:
        iprscan.initFromDatabase('database search.AFT.Microarray Annotation.IPRScan Interpro Scan',connection)
    except brdfException:
        if iprscan.obState['ERROR'] == 1:
            # could not find so create
            iprscan.initNew(connection)
            iprscan.databaseFields.update ( {
                    'biodatabaseob' : interpro.databaseFields['obid'],
                    'bioprotocolob' : iprscanprotocol.databaseFields['obid'],
                    'xreflsid' : 'database search.AFT.Microarray Annotation.IPRScan Interpro Scan',
                    'studyname' : 'AFT Microarray Annotation IPRScan Interpro Scan',
                    'studytype' : 'Interpro IPRSCAN',
                    'rundate' : '01-10-2006',
                    'runby' : 'Anar Khan'         
            })
            iprscan.insertDatabase(connection)
        else:
            # some other error - re-raise
            raise brdfException, iprscan.obState['MESSAGE']        
        
    ######################## end setup of database search studies ###################33
    

    rowcount = 0
    annotatedtargets=[]
    for row in reader:
        rowcount += 1
        if rowcount ==1:
            fieldNames = row
            continue
        fieldDict = dict(zip(fieldNames,[item.strip() for item in row]))

        # link the probe to the target
        for targetseq in targetseqs:
            if fieldDict['Probe Set Name'] == targetseq[1]:
                print "annotating %s"%(targetseq[1])
                annotatedtargets.append(targetseq[1])

                #for factname in ['Description','Species (a priori)',\
                #    'Species classification (E=endophyte, R=ryegrass, G=Glomeromycetes, B=bacterial control, U=unknown, Junk=not detectable)',\
                #                 'Orientation (a priori: F=forward, R=reverse, U=unknown)','Original Sequence Length',\
                #                 'Cross-hyb Sequences (# cross-hyb probes, average # conserved bases per cross-hyb probe)',\
                #                 'GenBank Protein ID 4/9/06','GenBank Protein Description','GenBank Protein EValue',\
                #                 'RefSeq Nucleotide IDs, top 5 hits (31/10/06)','Entrez Gene IDs (31/10/06)',\
                #                 'Fusarium Genome Database ID 6/9/06','Fusarium Genome Database Description',\
                #                 'Fusarium Genome Database Evalue','CPS NRPS Blast Hit ID(s)','CPS NRPS Blast Hit Desc(s)',\
                #                 'CPS NRPS Blast Hit Evalue(s)','InterproScan Hit ID(s) 7/9/06','InterproScan Hit Description(s)',\
                #                 'GO Molecular Function ID(s)','GO Molecular Function Description(s)','GO Biological Process ID(s)',\
                #                 'GO Biological Process Description(s)','GO Cellular Component ID(s)','GO Cellular Component Description(s)',\
                #                 'SignalP Signal Peptide Probability (S)','SignalP Signal Peptide Length','keyword','source','submitter',\
                #                 'E_RG, PMA calls','FL1-F, PMA calls','LP19F, PMA calls','54-1, PMA calls','ACKO42, PMA calls',\
                #                 'FL1-T, PMA calls','FL1-L, PMA calls','G9, PMA calls','LP19L, PMA calls','NC25KO, PMA calls']:
                # annotate things that are currently generic facts
                for factname in ['Description','Species (a priori)',\
                    'Species classification (E=endophyte, R=ryegrass, G=Glomeromycetes, B=bacterial control, U=unknown, Junk=not detectable)',\
                                 'Orientation (a priori: F=forward, R=reverse, U=unknown)','Original Sequence Length',\
                                 'Cross-hyb Sequences (# cross-hyb probes, average # conserved bases per cross-hyb probe)',\
                                 'E_RG, PMA calls','FL1-F, PMA calls','LP19F, PMA calls','54-1, PMA calls','ACKO42, PMA calls',\
                                 'FL1-T, PMA calls','FL1-L, PMA calls','G9, PMA calls','LP19L, PMA calls','NC25KO, PMA calls',\
                                 'source','submitter']:
                                
                    print "annotating %s"%factname
                    biosequence = bioSequenceOb()
                    biosequence.initFromDatabase(targetseq[0],connection)
                    biosequence.addFact(connection,'Affy Annotation',factname,fieldDict[factname])


                    # update keywords
                    if len(fieldDict['keyword']) > 1:
                        sql = """
                        update biosequenceob set obkeywords = %(keyword)s
                        where obid = %(obid)s
                        """
                        linkcursor.execute(sql,{'keyword' : fieldDict['keyword'], 'obid' : biosequence.databaseFields['obid']})
                        connection.commit()
                    
                    

                # add the Genbank blast hit
                if len(fieldDict['GenBank Protein ID 4/9/06']) > 1:
                    genbanknrhit  = bioSequenceOb()
                    genbanknrhitlsid = 'NCBI.%s'%fieldDict['GenBank Protein ID 4/9/06']
                    try:
                        genbanknrhit.initFromDatabase(genbanknrhitlsid,connection)
                    except brdfException:
                        if genbanknrhit.obState['ERROR'] == 1:
                        # could not find so create
                            genbanknrhit.initNew(connection)
                            genbanknrhit.databaseFields.update ( {
                                 'xreflsid' : genbanknrhitlsid,
                                 'sequencename' :  fieldDict['GenBank Protein ID 4/9/06'],
                                 'sequencetype' : 'PROTEIN SEQUENCE',
                                 'sequencedescription' : fieldDict['GenBank Protein Description']
                            })
                            genbanknrhit.insertDatabase(connection)
                        else:
                            raise brdfException, genbanknrhit.obState['MESSAGE']
                    genbankblastx.addHit(connection, querysequence=biosequence.databaseFields['obid'], hitsequence=genbanknrhit.databaseFields['obid'],\
                                         queryxreflsid = biosequence.databaseFields['xreflsid'], hitxreflsid = genbanknrhit.databaseFields['xreflsid'], \
                                         hitevalue = float(fieldDict['GenBank Protein EValue']))

                # add the Refseq hits
                if len(fieldDict['RefSeq Nucleotide IDs, top 5 hits (31/10/06)']) > 1:
                    hits = re.split(';',fieldDict['RefSeq Nucleotide IDs, top 5 hits (31/10/06)'])
                    genes = re.split(';',fieldDict['Entrez Gene IDs (31/10/06)'])
                    hits = [item.strip() for item in hits]

                    # if the length of genes is less than the length of hits then try removing any XM_ records from
                    # hits - though this is not guaranteed. This was a bug in the annotation file
                    if len(genes) != len(hits):
                        batchmodulelogger.info("warning processing refseqhits - genes and hits mismatch : %s and %s "%(str(hits),str(genes)))
                        batchmodulelogger.info("....removing XM_ records to try to fix.....")
                        hits = [hit for hit in hits if re.search('^XM_',hit) == None]
                        if len(hits) != len(genes):
                            batchmodulelogger.info("....unable to fix, giving up - no hits will be inserted")
                            hits = []
                            genes = []
                         
                    for i in range(0 , len(hits)):
                        hit = hits[i]
                        refseqhit  = bioSequenceOb()
                        refseqhitlsid = 'NCBI.%s'%hit
                        try:
                            refseqhit.initFromDatabase(refseqhitlsid,connection)
                        except brdfException:
                            if refseqhit.obState['ERROR'] == 1:
                            # could not find so create
                                refseqhit.initNew(connection)
                                refseqhit.databaseFields.update ( {
                                     'xreflsid' : refseqhitlsid,
                                     'sequencename' :  hit,
                                     'sequencetype' : 'mRNA Reference Sequence',
                                     'sequencedescription' : 'Entrez geneid %s '%(genes[i])
                                })
                                refseqhit.insertDatabase(connection)
                            else:
                                raise brdfException, refseqhit.obState['MESSAGE']
                            
                        refseqblastn.addHit(connection, querysequence=biosequence.databaseFields['obid'], hitsequence=refseqhit.databaseFields['obid'],\
                                         queryxreflsid = biosequence.databaseFields['xreflsid'], hitxreflsid = refseqhit.databaseFields['xreflsid'],\
                                            observationcomment = "Hit number %s out of %s top refseq hits"%(i+1,len(hits)))

                # add the Fusarium blast hit
                if len(fieldDict['Fusarium Genome Database ID 6/9/06']) > 1:
                    fusariumhit  = bioSequenceOb()
                    fusariumlsid = 'MIPS.%s'%fieldDict['Fusarium Genome Database ID 6/9/06']
                    try:
                        fusariumhit.initFromDatabase(fusariumlsid,connection)
                    except brdfException:
                        if fusariumhit.obState['ERROR'] == 1:
                        # could not find so create
                            fusariumhit.initNew(connection)
                            fusariumhit.databaseFields.update ( {
                                 'xreflsid' : fusariumlsid,
                                 'sequencename' :  fieldDict['Fusarium Genome Database ID 6/9/06'],
                                 'sequencetype' : 'PROTEIN SEQUENCE',
                                 'sequencedescription' : fieldDict['Fusarium Genome Database Description']
                            })
                            fusariumhit.insertDatabase(connection)
                        else:
                            raise brdfException, fusariumhit.obState['MESSAGE']
                    fusariumblastx.addHit(connection, querysequence=biosequence.databaseFields['obid'], hitsequence=fusariumhit.databaseFields['obid'],\
                                         queryxreflsid = biosequence.databaseFields['xreflsid'], hitxreflsid = fusariumhit.databaseFields['xreflsid'], \
                                         hitevalue = float(fieldDict['Fusarium Genome Database Evalue']))

                # add the cps nrps hits
                if len(fieldDict['CPS NRPS Blast Hit ID(s)']) > 1:
                    hits = re.split(';',fieldDict['CPS NRPS Blast Hit ID(s)'])
                    descriptions = re.split(';',fieldDict['CPS NRPS Blast Hit Desc(s)'])
                    if len(descriptions) < len(hits):
                        descriptions += (len(hits)-len(descriptions)) * [None] 
                    evalues = re.split(';',fieldDict['CPS NRPS Blast Hit Evalue(s)'])
                    if len(evalues) < len(hits):
                        evalues += (len(hits)-len(evalues)) * [None]                     
                    hits = [item.strip() for item in hits]
                    for i in range(0 , len(hits)):
                        hit = hits[i]
                        cpsnrpshit  = bioSequenceOb()
                        cpsnrpshitlsid = 'CPS NRPS.%s'%hit
                        try:
                            cpsnrpshit.initFromDatabase(cpsnrpshitlsid,connection)
                        except brdfException:
                            if cpsnrpshit.obState['ERROR'] == 1:
                            # could not find so create
                                cpsnrpshit.initNew(connection)
                                cpsnrpshit.databaseFields.update ( {
                                     'xreflsid' : cpsnrpshitlsid,
                                     'sequencename' :  hit,
                                     'sequencetype' : 'PROTEIN SEQUENCE',
                                     'sequencedescription' : descriptions[i]
                                })
                                cpsnrpshit.insertDatabase(connection)
                            else:
                                raise brdfException, cpsnrpshit.obState['MESSAGE']
                            
                        cpsnrpsblastx.addHit(connection, querysequence=biosequence.databaseFields['obid'], hitsequence=cpsnrpshit.databaseFields['obid'],\
                                         queryxreflsid = biosequence.databaseFields['xreflsid'], hitxreflsid = cpsnrpshit.databaseFields['xreflsid'],\
                                            observationcomment = "Hit number %s out of %s hits"%(i+1,len(hits)),\
                                             hitevalue = evalues[i])


                # add the interpro hits
                if len(fieldDict['InterproScan Hit ID(s) 7/9/06']) > 1:
                    hits = re.split(';',fieldDict['InterproScan Hit ID(s) 7/9/06'])
                    descriptions = re.split(';',fieldDict['InterproScan Hit Description(s)'])
                    hits = [item.strip() for item in hits]
                    for i in range(0 , len(hits)):
                        hit = hits[i]
                        interprohit  = bioSequenceOb()
                        interprohitlsid = 'Interpro.%s'%hit
                        try:
                            interprohit.initFromDatabase(interprohitlsid,connection)
                        except brdfException:
                            if interprohit.obState['ERROR'] == 1:
                            # could not find so create
                                interprohit.initNew(connection)
                                interprohit.databaseFields.update ( {
                                     'xreflsid' : interprohitlsid,
                                     'sequencename' :  hit,
                                     'sequencetype' : 'PROTEIN SEQUENCE MODEL',
                                     'sequencedescription' : descriptions[i]
                                })
                                interprohit.insertDatabase(connection)
                            else:
                                raise brdfException, interprohit.obState['MESSAGE']
                            
                        iprscan.addHit(connection, querysequence=biosequence.databaseFields['obid'], hitsequence=interprohit.databaseFields['obid'],\
                                         queryxreflsid = biosequence.databaseFields['xreflsid'], hitxreflsid = interprohit.databaseFields['xreflsid'],\
                                            observationcomment = "Hit number %s out of %s hits"%(i+1,len(hits)))                      


                    


                # link to GO terms : molecular function
                if len(fieldDict['GO Molecular Function ID(s)']) > 1:
                    goterms = re.split(';',fieldDict['GO Molecular Function ID(s)'])
                    goterms = [item.strip() for item in goterms]
                    godescriptions = re.split(';',fieldDict['GO Molecular Function Description(s)'])
                    for i in range(0,len(goterms)):
                        goterm = goterms[i]
                        if goterm not in goDict:
                            goDict[goterm] = gofunction.addTerm(connection,goterm, checkexisting = False, \
                                                        termdescription = godescriptions[i])[0]
                        sql = """
                        insert into predicatelink( xreflsid , voptypeid , subjectob , objectob , predicate )
                        values(%(xreflsid)s , %(voptypeid)s , %(subjectob)s , %(objectob)s , %(predicate)s)
                        """
                        linkcursor.execute(sql,{'xreflsid' : "%s.%s"%(biosequence.databaseFields['xreflsid'],goterm),\
                                               'voptypeid' : 395, 'subjectob' : biosequence.databaseFields['obid'],\
                                               'objectob' : goDict[goterm], 'predicate' : 'GO_ASSOCIATION'})
                        connection.commit()

                # link to GO terms : biological process
                if len(fieldDict['GO Biological Process ID(s)']) > 1:
                    goterms = re.split(';',fieldDict['GO Biological Process ID(s)'])
                    goterms = [item.strip() for item in goterms]
                    godescriptions = re.split(';',fieldDict['GO Biological Process Description(s)'])
                    for i in range(0,len(goterms)):
                        goterm = goterms[i]
                        if goterm not in goDict:
                            goDict[goterm] = goprocess.addTerm(connection,goterm, checkexisting = False, \
                                                        termdescription = godescriptions[i])[0]
                        sql = """
                        insert into predicatelink( xreflsid , voptypeid , subjectob , objectob , predicate )
                        values(%(xreflsid)s , %(voptypeid)s , %(subjectob)s , %(objectob)s , %(predicate)s)
                        """
                        linkcursor.execute(sql,{'xreflsid' : "%s.%s"%(biosequence.databaseFields['xreflsid'],goterm),\
                                               'voptypeid' : 395, 'subjectob' : biosequence.databaseFields['obid'],\
                                               'objectob' : goDict[goterm], 'predicate' : 'GO_ASSOCIATION'})
                        connection.commit()


                # link to GO terms : cellular component
                if len(fieldDict['GO Cellular Component ID(s)']) > 1:
                    goterms = re.split(';',fieldDict['GO Cellular Component ID(s)'])
                    goterms = [item.strip() for item in goterms]
                    godescriptions = re.split(';',fieldDict['GO Cellular Component Description(s)'])
                    for i in range(0,len(goterms)):
                        goterm = goterms[i]
                        if goterm not in goDict:
                            goDict[goterm] = gocomponent.addTerm(connection,goterm, checkexisting = False, \
                                                        termdescription = godescriptions[i])[0]
                        sql = """
                        insert into predicatelink( xreflsid , voptypeid , subjectob , objectob , predicate )
                        values(%(xreflsid)s , %(voptypeid)s , %(subjectob)s , %(objectob)s , %(predicate)s)
                        """
                        linkcursor.execute(sql,{'xreflsid' : "%s.%s"%(biosequence.databaseFields['xreflsid'],goterm),\
                                               'voptypeid' : 395, 'subjectob' : biosequence.databaseFields['obid'],\
                                               'objectob' : goDict[goterm], 'predicate' : 'GO_ASSOCIATION'})
                        connection.commit()

                # add signalP feature if there
                if len(fieldDict['SignalP Signal Peptide Probability (S)']) > 1:
                    biosequence.addFeature( connection,{
                        'featuretype' : 'sig_peptide',
                        'featurelength' : fieldDict['SignalP Signal Peptide Length'],
                        'evidence' : "SignalP probability %s"%fieldDict['SignalP Signal Peptide Probability (S)']
                    })
        
                    
def loadGenstatNormalisation(experimentid, inputFile,fileformat="CSV"):
    """ this imports normalised data into the database , where the original data was already in the brdf so that
    we already have the experimentid and spotid
     e.g. it looks like this
Experimentid,Spotid,Intensity,clogRatio,WtlogRatio
114901,11192,12.4371,     0.31329,    0.984447
114901,11193,13.1423,    0.166673,    0.492682
114901,11194,11.9109,   -0.220962,   -0.731742
114901,11195,11.6664,   -0.126501,   -0.408359
114901,11196,11.4054,   -0.256195,   -0.791584
114901,11197,11.0995,   -0.630122,    -2.01806
114901,11198,11.4477,   0.0768177,     0.23488
114901,11199,11.7328,    -0.22068,    -0.72133
    """

    connection=databaseModule.getConnection()
    insertCursor = connection.cursor()

    #get the observationid's for this experiment, for all spots, for speed
    sql = """
    select
        microarrayspotfact,
        obid
    from
        microarrayobservation
    where
        microarraystudy = %s
    """
    insertCursor.execute(sql%experimentid)
    observationDict = dict(insertCursor.fetchall())
    if len(observationDict) == 0:
        raise brdfException("no observations found for this experiment")
    

    # open the input file
    if fileformat.lower() == 'csv':
       reader = csv.reader(open(inputFile, "rb"))
    else:
       reader = open(inputFile, "rb")
    rowCount = 0
    for row in reader:
        if fileformat.lower != 'csv':
            row = re.split('\s+',row)
        if len(row) < 3:
            break
        rowCount += 1
        if rowCount == 1:
            fieldNames = [item.lower().strip() for item in row]

            print "fieldNames = %s"%str(fieldNames)
        else:
            print "processing row %s"%rowCount

            # strip spaces
            row = [eval({True : 'item.strip()' , False : 'None'}[item != None]) for item in row]

            # handle asterisk missing values
            row = [eval({True : 'None' , False : 'item'}[item == '*']) for item in row]

            fieldDict=dict(zip(fieldNames,row))

            # handle alternate column headings
            if "experimentid!" in fieldDict and "experimentid" not in fieldDict:
                fieldDict["experimentid"] = fieldDict["experimentid!"]

            if "spotid!" in fieldDict and "spotid" not in fieldDict:
                fieldDict["spotid"] = fieldDict["spotid!"]

            if "logratio" in fieldDict and "wtlogratio" not in fieldDict:
                fieldDict["wtlogratio"] = fieldDict["logratio"]
    

            # check experiment matches
            if experimentid != int(fieldDict['experimentid']):
                raise brdfException("Error - experiment %s  found in file does not match experiment %s called"%(fieldDict['experimentid'],experimentid))

            sql = """
            insert into microarrayobservationfact(microarrayobservation, factnamespace, attributename, attributevalue )
            values(%(microarrayobservation)s, 'NORMALISED VALUE', 'Intensity', %(intensity)s )
            """
            insertCursor.execute(sql,{
                'microarrayobservation' : observationDict[int(fieldDict['spotid'])],
                'intensity' : fieldDict['intensity']
            })
            sql = """
            insert into microarrayobservationfact(microarrayobservation, factnamespace, attributename, attributevalue )
            values(%(microarrayobservation)s, 'NORMALISED VALUE', 'clogRatio', %(clogratio)s )
            """
            insertCursor.execute(sql,{
                'microarrayobservation' : observationDict[int(fieldDict['spotid'])],
                'clogratio' : fieldDict['clogratio']
            })

            # we may not always have wtlogratio
            if 'wtlogratio' in fieldDict:
                sql = """
                insert into microarrayobservationfact(microarrayobservation, factnamespace, attributename, attributevalue )
                values(%(microarrayobservation)s, 'NORMALISED VALUE', 'WtlogRatio', %(wtlogratio)s )
                """
                insertCursor.execute(sql,{
                    'microarrayobservation' : observationDict[int(fieldDict['spotid'])],
                    'wtlogratio' : fieldDict['wtlogratio']
                })

            connection.commit()
            
                        
    connection.close()    

def loadSNPChip(infile, labresourcename, labresourcedescription, datastartsrow=3, fieldnamesrow=2):
    """ load genetic tests from a file like this :
    
Markers for  AllMarkers
Marker Key	Marker ID	Chromosome	Position	Flanking 5' Sequence	Variation	Flanking 3' Sequence
126	BTA-100056	7	46015530	CCAGGCAAGAACACTGGAGTGGGTTGCCATTTCCTTCTCCAGGGGGACAG	T/A	TGAGGCCACTGCAATTCAGTGCGACCACCTCTAGGACAGG	Norwegian Red
262	BTA-101051	11	5669564	CCAATGGGAGAGGCTGGCAGGAGGGAAGAGAGAGAGGGGTTAGGTAGATC	T/A	TCCTTACTCCATTCATTGGTATTTGCTGAAAACTGTGTTT	Holstein


    """

    reader = file(infile)
    connection=databaseModule.getConnection()
    insertCursor = connection.cursor()

    currentTest = geneticTestFact()
    currentProtocol = bioProtocolOb()
    currentLabResource = labResourceOb()


    rownum = 0


    # log the data source and data import
    print "logging data source...."
    importProcedure = importProcedureOb()
    importprocedurelsid = 'importProcedure.agresearchBatches.loadSNPChip'
    try :
        importProcedure.initFromDatabase(importprocedurelsid,connection)
    except brdfException:
        # not found so create it
        importProcedure.initNew(connection)
        importProcedure.databaseFields.update ({
            'xreflsid' : importprocedurelsid,
            'procedurename' : 'loadSNPChip'
        })
        importProcedure.insertDatabase(connection)

    dataSource = dataSourceOb()
    datasourcelsid = infile
    try :
        dataSource.initFromDatabase(datasourcelsid,connection)
    except brdfException:
        # not found so create it  
        dataSource.initNew(connection, \
                datasourcetype='Tab delimited text', \
                physicalsourceuri = infile)
        dataSource.insertDatabase(connection)



    # log the SNP chip as a whole
    labresourcelsid = labresourcename
    try:
        currentLabResource.initFromDatabase(labresourcelsid,connection)
    except brdfException, msg:
        if currentLabResource.obState['ERROR'] == 1:
            currentLabResource.initNew(connection,'genotype snp')
            currentLabResource.databaseFields.update( \
            { 'resourcename' : labresourcelsid,
              'resourcetype' : 'Genotype SNP chip',
              'xreflsid' : labresourcelsid,
              'resourcedescription' : labresourcedescription
            })
            currentLabResource.insertDatabase(connection)

                
            print 'created lab resource %s'%currentLabResource.databaseFields['xreflsid']
        else:
            raise brdfException, currentLabResource.obState['MESSAGE']



    # record import
    dataSource.addImportFunction(currentLabResource,importProcedure,connection)                  



    for row in reader:
        rownum += 1

        fields = re.split('\t',row)
        fields = [item.strip() for item in fields]

        if rownum == fieldnamesrow:
            fieldNames = [item.lower() for item in fields]
            fieldNames.append('breed')
            print str(fieldNames)
            continue
        elif rownum < datastartsrow:
            continue

        fieldDict = dict(zip(fieldNames,fields))

        print str(fieldDict)

        # create a genetic test fact
        # get or create the current genetic test fact 
        genetictestfactlsid = 'genetic test.%s.%s'%(currentLabResource.databaseFields['xreflsid'], fieldDict['marker id'])
        currentTest.initNew(connection)
        currentTest.databaseFields.update( 
        {
                'obid' : getNewObid(connection) ,
                'accession' : fieldDict['marker id'],
                'xreflsid' : genetictestfactlsid , 
                'labresourceob' : currentLabResource.databaseFields['obid'],
                'testtype'  : 'SNP',
                'locusname' : fieldDict['marker id'],
                'testdescription' : "Marker id %(marker id)s at %(chromosome)s:%(position)s breed %(breed)s variation %(variation)s"%fieldDict,
                'variation' : fieldDict['variation']
        })
        currentTest.insertDatabase(connection)
        print 'created genetic test %s'%currentTest.databaseFields['xreflsid']

        # add a genetic location fact
        sql = """
        insert into
        geneticlocationfact(
           xreflsid,genetictestfact,mapname,speciestaxid,speciesname,
           locusname,chromosomename,locationstart,locationstop,evidence,voptypeid)
        values( %(xreflsid)s,%(genetictestfact)s,%(mapname)s,%(speciestaxid)s,%(speciesname)s,
           %(locusname)s,%(chromosomename)s,%(locationstart)s,%(locationstop)s,%(evidence)s,%(voptypeid)s)
        """
        locationDict = {
            'xreflsid' : "%s.%s"%(genetictestfactlsid,'Btau3'),
            'genetictestfact' : currentTest.databaseFields['obid'],
            'mapname' : 'Btau_3.0',
            'speciestaxid' : 9917,
            'speciesname' : 'Bos taurus',
            'locusname' : fieldDict['marker id'],
            'chromosomename' : "BTA%s"%fieldDict['chromosome'],
            'locationstart' : fieldDict['position'],
            'locationstop' : fieldDict['position'],
            'evidence' : 'Chip spec file',
            'voptypeid' : 177
        }

        print "executing %s"%sql%locationDict

        insertCursor.execute(sql,locationDict)
        connection.commit()


        # add the attached facts

        for fact in ["marker key","flanking 5' sequence","flanking 3' sequence","breed"]:
            sql = """
            insert into genetictestfact2(genetictestfact,factnamespace,attributename,attributevalue)
            values(%(genetictestfact)s,%(factnamespace)s,%(attributename)s,%(attributevalue)s)
            """
            print "executing %s"%(sql%{
                'genetictestfact' : currentTest.databaseFields['obid'],
                'factnamespace' : 'SNP details',
                'attributename' : fact,
                'attributevalue' : fieldDict[fact]
            })
            insertCursor.execute(sql,{
                'genetictestfact' : currentTest.databaseFields['obid'],
                'factnamespace' : 'SNP details',
                'attributename' : fact,
                'attributevalue' : fieldDict[fact]
            })
            connection.commit()

        # if possible link to a dbSNP URI - e.g. rs29019317 is http://www.ncbi.nlm.nih.gov/SNP/snp_ref.cgi?rs=29019317
        match = re.search('^rs(\d+)$',fieldDict['marker id']) 
        if match != None:
            if len(match.groups()) >= 1:
                rsNum = match.groups()[0]
            
                uri = uriOb()
                uri.initNew(connection)
                uri.databaseFields.update(
                {
                    'createdby' : 'system',
                    'uristring' : 'http://www.ncbi.nlm.nih.gov/SNP/snp_ref.cgi?rs=%s'%rsNum,
                    'xreflsid' : 'http://www.ncbi.nlm.nih.gov/SNP/snp_ref.cgi?rs=%s'%rsNum,
                    'visibility' : 'public'
                })
                uri.insertDatabase(connection)
                uri.createLink(connection,currentTest.databaseFields['obid'],'Link to dbSNP for rs%s'%rsNum,'system')
                                 
                         

    insertCursor.close()
    connection.close()


def loadSNPChipResults(infile, chiplsid, datastartsrow=3, fieldnamesrow=2):
    """ load genetic tests from a file like this :
    
Genotypes  of  all Animals in the database downloaded on 2007-06-18 19:40:50
Animal  Marker_key      Variation       Genotype
CHL00013        BTA-137262      A/C     AC
GIR00006        BES1_Contig517_1400     A/G     GG
HFD00005        BTA-137262      A/C     AC
ANG00004        BTA-137262      A/C     CC
ANG00012        BTA-137262      A/C     CC
ANG00020        BTA-137262      A/C     AC
BRM00001        BTA-137262      A/C     CC
BRM00014        BTA-137262      A/C     CC
BRM00028        BTA-137262      A/C     AC
BRM00038        BTA-137262      A/C     AC
CHL00008        BTA-137262      A/C     AA
CHL00016        BTA-137262      A/C     AC
CHL00024        BTA-137262      A/C     CC

    """

    reader = file(infile)
    connection=databaseModule.getConnection()
    insertCursor = connection.cursor()
    

    # get all the genetictests on this chip
    sql = """
    select
       gtf.accession,
       gtf.obid,
       gtf.variation
    from
       genetictestfact gtf join labresourceob l on
       l.xreflsid = '%s' and
       gtf.labresourceob = l.obid
    """%chiplsid
    print "getting tests using %s"%sql
    insertCursor.execute(sql)

    # create a dictionary with accession as key, and a tuple of
    # obid and variation as value
    snpDict=dict([(row[0], (row[1],row[2])) for row in insertCursor.fetchall()])
    

    # this procedure loads the subjects and samples as we go
    sampleDict = {}
    studyDict = {}


    rownum = 0


    # log the data source and data import
    print "logging data source...."
    importProcedure = importProcedureOb()
    importprocedurelsid = 'importProcedure.agresearchBatches.loadSNPChipResults'
    try :
        importProcedure.initFromDatabase(importprocedurelsid,connection)
    except brdfException:
        # not found so create it
        importProcedure.initNew(connection)
        importProcedure.databaseFields.update ({
            'xreflsid' : importprocedurelsid,
            'procedurename' : 'loadSNPChipResults'
        })
        importProcedure.insertDatabase(connection)

    dataSource = dataSourceOb()
    datasourcelsid = infile
    try :
        dataSource.initFromDatabase(datasourcelsid,connection)
    except brdfException:
        # not found so create it  
        dataSource.initNew(connection, \
                datasourcetype='Tab delimited text', \
                physicalsourceuri = infile)
        dataSource.insertDatabase(connection)

    # try to get the protocol
    currentProtocol = bioProtocolOb()    
    protocollsid = "GenotypeProtocol.Bovine SNP chip protocol"
    try:
        currentProtocol.initFromDatabase(protocollsid,connection)
    except:
        # could not find so create
        currentProtocol.initNew(connection)
        currentProtocol.databaseFields.update( \
        { 'protocolname' : 'Bovine SNP chip protocol',
            'xreflsid' : protocollsid,
            'protocoltype' : 'GENOTYPE',
            'protocoldescription' : 'Protocol used in Bovine SNP chip genotyping'
        })
        currentProtocol.insertDatabase(connection)
        print 'inserted' + str(currentProtocol)


    # try to obtain the labresource we are to link the sequence to.
    currentLabResource = labResourceOb()
    labresourcelsid = chiplsid
    currentLabResource.initFromDatabase(labresourcelsid,connection)


    for row in reader:
        rownum += 1

        fields = re.split('\t',row)
        fields = [item.strip() for item in fields]

        if rownum == fieldnamesrow:
            fieldNames = [item.lower() for item in fields]
            print str(fieldNames)
            continue
        elif rownum < datastartsrow:
            continue

        fieldDict = dict(zip(fieldNames,fields))

        if rownum%500 == 1:
            print str(fieldDict)

        # check we know about this test
        if fieldDict['marker_key'] not in snpDict:
            raise brdfException("Error : %s not in db at row %s"%(fieldDict['marker_key'],rownum))

        # see whether we have this sample
        if fieldDict['animal'] not in sampleDict:
            # create subject
            currentSubject=bioSubjectOb()
            currentSubject.initNew(connection)
            currentSubject.databaseFields.update( \
                {'subjectname' : fieldDict['animal'] ,
                 'xreflsid' : fieldDict['animal']
                 })
            currentSubject.insertDatabase(connection)
            print 'inserted' + str(currentSubject)


            currentSample = bioSampleOb()
            currentSample.initNew(connection)
            currentSample.databaseFields.update( \
                {   
                    'xreflsid' : "%s.sample"%fieldDict['animal'] ,
                    'sampledescription' : 'unknown sample used for genotype',
                    'sampletype' : 'Blood Sample'
                })
            currentSample.insertDatabase(connection)
            #currentSample.createSamplingFunction(connection, currentSubject.databaseFields['obid'],
            #                                         "%s.sampling"%currentSample.databaseFields['xreflsid'])
            currentSample.createSamplingFunction(connection, currentSubject,
                                                     "%s.sampling"%currentSample.databaseFields['xreflsid'])
            sampleDict[fieldDict['animal']] = currentSample.databaseFields['obid']
                    

        # check that the variation reported is the same as the variation recorded for the test
        if snpDict[fieldDict['marker_key']][1] != fieldDict['variation']:
            batchmodulelogger.info("warning : variation does not match that in database for row %s (%s)"%(rownum,fieldDict['marker_key']))

        # set up the study - one per subject
        studylsid = 'genotypestudy.%s.%s.%s'%(fieldDict['animal'],protocollsid,labresourcelsid)
        if studylsid not in studyDict:
            currentStudy = genotypeStudy()
            currentStudy.initNew(connection,(currentLabResource,currentSample,currentProtocol))
            currentStudy.databaseFields.update( 
                {
                    'studytype' : 'SNP Marker',
                    'xreflsid' : studylsid
                })
            currentStudy.insertDatabase(connection)
            studyDict[studylsid] = currentStudy.databaseFields['obid']

        # add the observation
        sql = """
        insert into genotypeobservation(
                xreflsid ,
                genotypestudy ,
                genetictestfact,
                genotypeobserved)
        values(
                %(xreflsid)s ,
                %(genotypestudy)s ,
                %(genetictestfact)s,
                %(genotypeobserved)s 
        )"""
        insertCursor.execute(sql,{
            'xreflsid' : "%s.%s"%(studylsid,fieldDict['marker_key']),
            'genotypestudy' : studyDict[studylsid],
            'genetictestfact' : snpDict[fieldDict['marker_key']][0],
            'genotypeobserved' : fieldDict['genotype']
        })
        connection.commit()
                
    insertCursor.close()
    connection.close()


def loadContigExpression(infile):
    """ this loads expression information into the expression table for sequences that are
    contigs, from a file like :
"250506CS3900132800002","     2=OSI(1) OVMG(1) "
"250506CS3901328000001","     5=PUBSHEEP0306(5) "
"250506CS3901328100001","     2=PUBSHEEP0306(2) "    
- SQL used to extract this from Oracle database : 

select 
   externalname,
   agplsqlutils.getLibraryExpressionStringfor(sequenceid) libExpression
from 
   agsequence
where
   source = 'CS44' 

    """
    reader = csv.reader(open(infile, "rb"))
    connection=databaseModule.getConnection()
    insertCursor = connection.cursor()
        
    rowCount = 0
        
    
    fieldNames = ["sequencename","expression"]
    for row in reader:
        rowCount += 1

        if rowCount == 1:
            continue

        print "processing row %s"%row
        row = [item.strip() for item in row]
        fieldDict=dict(zip(fieldNames,row))        

        # get the sequence
        sequence = bioSequenceOb()

        # check sequence exists
        sequencelsid = "CS34.%s"%fieldDict['sequencename']
        try :
            sequence.initFromDatabase(sequencelsid,connection)
        except brdfException,msg:
            if sequence.obState['ERROR'] == 1:
                print "could not get %s"%sequencelsid
                continue
            else:
                print sequence.obState['MESSAGE']
                return
          
        
        libstring=re.split('=',fieldDict["expression"])[1]
        print "libstring=%s"%libstring
        libs = re.split('\s+',libstring)
        for lib in libs:
            tokens = re.split('[\(\)]',lib)
            libname = tokens[0]
            libcount = tokens[1]
            print tokens
            
            expressionlsid = "%s.TissueExpression"%sequence.databaseFields['xreflsid']
            sql = """
            insert into geneticexpressionfact(
 xreflsid ,
 voptypeid    ,
 biosequenceob ,
 expressionmapname ,
 expressionmaplocus ,
 speciesname        ,
 speciestaxid       ,
 expressionamount   ,
 evidence           )
            values(
 %(xreflsid)s,
 %(voptypeid)s    ,
 %(biosequenceob)s ,
 %(expressionmapname)s ,
 %(expressionmaplocus)s ,
 %(speciesname)s        ,
 %(speciestaxid)s       ,
 %(expressionamount)s   ,
 %(evidence)s
             )
             """
            expressionDict = {
                 'xreflsid' : expressionlsid,
                 'voptypeid'  :  196,
                 'biosequenceob' : sequence.databaseFields['obid'],
                 'expressionmapname' : 'AgResearch CS34 Contig',
                 'expressionmaplocus' : libname,
                 'speciesname' : 'Bos taurus'       ,
                 'speciestaxid'  :    9913  ,
                 'expressionamount' :  libcount ,
                 'evidence' : 'EST Contig'}
            print "executing %s"%(sql%expressionDict)
            insertCursor.execute(sql,expressionDict)
            connection.commit()
            
            
    insertCursor.close()
    connection.close()    


def loadSequenceMain():
    connection=databaseModule.getConnection()
    myproc = loadSequenceProcedure(connection)
    #myproc.runProcedure("/home/seqstore/agbrdf/trichoderma_reesei.fasta",sequencetype='genomic DNA', lsidprefix='Trichoderma.reesei',checkExisting=False)
    #myproc.runProcedure("/home/seqstore/agbrdf/cs39annotated.fa",sequencetype='mRNA SEQUENCE', lsidprefix='CS39',checkExisting=False)
    #myproc.runProcedure("/home/seqstore/agbrdf/cs19annotated.seq",sequencetype='mRNA SEQUENCE', lsidprefix='CS19',checkExisting=False)
    #myproc.runProcedure("/home/seqstore/agbrdf/cs19orfs.seq",sequencetype='PROTEIN SEQUENCE', lsidprefix='CS19.ORF',checkExisting=False)
    #myproc.runProcedure("/home/seqstore/agbrdf/agbovine.seq",sequencetype='mRNA SEQUENCE', lsidprefix='AgResearch.Bovine',checkExisting=False)
    #return
    #myproc.runProcedure("/home/seqstore/agbrdf/nauman/bovine_glean5_cds.fa",sequencetype='mRNA SEQUENCE', lsidprefix='Btau4.GLEAN.DNA',checkExisting=False)
    #myproc.runProcedure("/home/seqstore/agbrdf/nauman/bovine_glean5_pep.fa",sequencetype='PROTEIN SEQUENCE', lsidprefix='Btau4.GLEAN.PEP',checkExisting=False)
    #myproc.runProcedure("/data/home/seqstore/agbrdf/bovine/Bovine_consensus",sequencetype='mRNA SEQUENCE', lsidprefix='Affymetrix',checkExisting=False)
    #myproc.runProcedure("/data/home/seqstore/agbrdf/bovine/Bovine_control",sequencetype='mRNA SEQUENCE', lsidprefix='Affymetrix',checkExisting=False)
    #myproc.runProcedure("/data/home/seqstore/agbrdf/bovine/Bovine_target",sequencetype='Affy Target Oligo', lsidprefix='Affymetrix',checkExisting=False)
    #myproc.runProcedure("/data/home/seqstore/agbrdf/sheepEST.fa",sequencetype='mRNA SEQUENCE', lsidprefix='AgResearch.Ovine',checkExisting=False)
    #myproc.runProcedure("/home/seqstore/agbrdf/cs37.fa",sequencetype='mRNA SEQUENCE', lsidprefix='CS37',checkExisting=False)
    #myproc.runProcedure("/home/seqstore/agbrdf/cs37orfs.seq",sequencetype='PROTEIN SEQUENCE', lsidprefix='CS37.ORF',checkExisting=False)
    #myproc.runProcedure("/data/agbio/spool/cs35.seq",sequencetype='mRNA SEQUENCE', lsidprefix='CS35',checkExisting=False)
    #myproc.runProcedure("/data/agbio/spool/cs20.seq",sequencetype='mRNA SEQUENCE', lsidprefix='CS20',checkExisting=False)
    #myproc.runProcedure("/data/agbio/spool/cs14.seq",sequencetype='mRNA SEQUENCE', lsidprefix='CS14',checkExisting=False)
    #myproc.runProcedure("/home/seqstore/agbrdf/cs51.seq",sequencetype='mRNA SEQUENCE', lsidprefix='CS51',checkExisting=False, format="Tab delimited")
    #myproc.runProcedure("/data/home/seqstore/agbrdf/parasite/cs46acontigs.seq",sequencetype='mRNA SEQUENCE', lsidprefix='CS46a',checkExisting=False)
    #myproc.runProcedure("/data/home/seqstore/agbrdf/parasite/cs46bcontigs.seq",sequencetype='mRNA SEQUENCE', lsidprefix='CS46B',checkExisting=False)
    #myproc.runProcedure("/data/home/seqstore/agbrdf/parasite/cs46asinglets.seq",sequencetype='mRNA SEQUENCE', lsidprefix='CS46A',checkExisting=False)
    #myproc.runProcedure("/data/home/seqstore/agbrdf/parasite/cs46bsinglets.seq",sequencetype='mRNA SEQUENCE', lsidprefix='CS46B',checkExisting=False)
    #myproc.runProcedure("/data/databases/flatfile/bfiles/agbrdf/temp/Macropus_eugenii.Meug_1.0.55.pep.all.fa",sequencetype='PROTEIN SEQUENCE', lsidprefix='ENSEMBL.Macropus_eugenii',checkExisting=False)
    #myproc.runProcedure("/data/databases/flatfile/bfiles/agbrdf/temp/redo.fa",sequencetype='PROTEIN SEQUENCE', lsidprefix='ENSEMBL.Macropus_eugenii',checkExisting=False)
    #myproc.runProcedure("/data/databases/flatfile/bfiles/agbrdf/temp/nine_mam_orthodb_prots.fa",sequencetype='PROTEIN SEQUENCE', lsidprefix='ENSEMBL.orthodb',checkExisting=False)
    #myproc.runProcedure("/data/agbio/spool/whitcloverEST.seq",sequencetype='mRNA SEQUENCE', lsidprefix='AgResearch.WhiteClover',checkExisting=False)
    #myproc.runProcedure("/data/databases/flatfile/bfiles/agbrdf/temp/Ornithorhynchus_anatinus.OANA5.55.pep.all.fa",sequencetype='PROTEIN SEQUENCE', lsidprefix='ENSEMBL.Ornithorhynchus_anatinus',checkExisting=False)
    #myproc.runProcedure("/ngseqdata/deer/xdata/s_7_sample50000.fa.masked",sequencetype='genomic DNA', lsidprefix='Deer.Illumina',checkExisting=False)
    #myproc.runProcedure("/ngseqdata/deer/xdata/r1.fa",sequencetype='genomic DNA', lsidprefix='Deer.Illumina',checkExisting=False)
    #myproc.runProcedure("/ngseqdata/deer/xdata/r2.fa",sequencetype='genomic DNA', lsidprefix='Deer.Illumina',checkExisting=False)
    #myproc.runProcedure("/ngseqdata/deer/xdata/s_7_sample200000.fa.masked",sequencetype='genomic DNA', lsidprefix='Deer.Illumina',checkExisting=False)
    #myproc.runProcedure("/data/databases/flatfile/bfiles/agbrdf/temp/all_human_placental_ESTs.fa",sequencetype='mRNA SEQUENCE', lsidprefix='ENSEMBL.Homo_sapiens',checkExisting=False)
    #myproc.runProcedure("/data/databases/flatfile/bfiles/agbrdf/temp/all_human_placental_ESTs.fa",sequencetype='mRNA SEQUENCE', lsidprefix='ENSEMBL.Homo_sapiens',checkExisting=False)
    #myproc.runProcedure("/data/databases/flatfile/bfiles/agbrdf/temp/BPLA_BPLC_ests.fa",sequencetype='mRNA SEQUENCE', lsidprefix='AgResearch.Bovine',checkExisting=True)
    #myproc.runProcedure("/data/databases/flatfile/bfiles/agbrdf/temp/Taeniopygia_guttata_taeGut3_2_4_56_pep_all.fa",sequencetype='PROTEIN SEQUENCE', lsidprefix='ENSEMBL.Zebrafinch',checkExisting=False)
    #myproc.runProcedure("/data/databases/flatfile/bfiles/agbrdf/temp/ArrayExpress_placenta_prots.fa",sequencetype='PROTEIN SEQUENCE', lsidprefix='ENSEMBL.ArrayExpress.Placenta',checkExisting=False)
    #myproc.runProcedure("/ngseqdata/deer/est/all/bucket_brigade/round_2/final_cap3_output/final_contigs_blast_results/renamed_contigs.fa",sequencetype='mRNA SEQUENCE', lsidprefix='CS60',checkExisting=False)
    #myproc.runProcedure("/ngseqdata/deer/est/all/bucket_brigade/round_2/final_cap3_output/final_contigs_blast_results/renamed_singlets.fa",sequencetype='mRNA SEQUENCE', lsidprefix='CS60',checkExisting=False)
    #myproc.runProcedure("/data/home/seqstore/deer/10031.fa",sequencetype='mRNA SEQUENCE', lsidprefix='CS60',checkExisting=False) # fixed CS60 cluster
    #myproc.runProcedure("/data/home/seqstore/deer/10031renamed.fa",sequencetype='mRNA SEQUENCE', lsidprefix='CS60',checkExisting=False) # fixed CS60 cluster
    #myproc.runProcedure("/data/home/seqstore/deer/10031singlets.fa",sequencetype='mRNA SEQUENCE', lsidprefix='CS60',checkExisting=False) # singlets
    #myproc.runProcedure("/data/agbio/spool/ryegrassESTExtract.fa",sequencetype='mRNA SEQUENCE', lsidprefix='AgResearch.Ryegrass',checkExisting=False) 
    myproc.runProcedure("/data/databases/flatfile/bfiles/agbrdf/skua/assemblyContigs.fa",sequencetype='genomic DNA', lsidprefix='SKUA',checkExisting=False) 


def annotateCDSMain():
    connection=databaseModule.getConnection()
    myproc = annotateCDSFromDBORFS(connection)
    myproc.runProcedure(28264508,'Misc.Bacteria',targetseqtype ='genomic DNA')

def loadFeatureMain():
    connection=databaseModule.getConnection()
    myproc = loadFeaturesProcedure(connection)
    #myproc.runProcedure("/home/seqstore/agbrdf/cs35orfs.fa.csv","CS35",comment="Import of ORFs as features")
    #myproc.runProcedure("/home/seqstore/agbrdf/cs35buildinfo.csv","CS35",comment="Import of ESTs as mRNA features of CS35 contigs")
    #myproc.runProcedure("/home/seqstore/agbrdf/cs19assembly.csv","CS19",comment="Import of ESTs as mRNA features of contigs")
    #myproc.runProcedure("/home/seqstore/agbrdf/cs39buildinfo.csv","CS39",comment="Import of ESTs as mRNA features of CS39 contigs")
    #myproc.runProcedure("/home/seqstore/agbrdf/cs37buildinfo.csv","CS37",comment="Import of ESTs as mRNA features of CS37 contigs")
    #myproc.runProcedure("/home/seqstore/agbrdf/cs37orfs.seq.csv","CS37",comment="Import of ORFs as features")
    #myproc.runProcedure("/home/seqstore/agbrdf/miscresults/cs37SNP.csv","CS37",comment="Import of CS37 SNPs",evidence="CS37 ACE file analysis (DSimon)")
    #myproc.runProcedure("/home/seqstore/agbrdf/cs39orfs.csv","CS39",comment="Import of ORFs as features")
    #myproc.runProcedure("/home/seqstore/agbrdf/miscresults/cs37SNP.csv","CS37",comment="Import of CS37 SNPs",evidence="CS37 ACE file analysis (DSimon)")
    #myproc.runProcedure("/home/seqstore/agbrdf/miscresults/cs20snp.csv","CS20",comment="Import of CS20 SNPs",evidence="SNooPy (Mark Schreiber)")
    #myproc.runProcedure("/home/seqstore/agbrdf/miscresults/cs20buildinfo.csv","CS20",comment="Import of CS20 contig membership details",evidence="cap3")
    #myproc.runProcedure("/home/seqstore/agbrdf/miscresults/cs20orfs.csv","CS20",comment="Import ORFs as features")
    #myproc.runProcedure("/home/seqstore/agbrdf/cs51orfs.fa.csv","CS51",comment="Import CS51 ORFs as features")
    #myproc.runProcedure("/home/seqstore/agbrdf/miscresults/CS51snp.txt","CS51",comment="Import of CS51 SNPs",evidence="SNooPy (Mark Schreiber)",format="Tab delimited")
    #myproc.runProcedure("/home/seqstore/agbrdf/miscresults/cs51buildinfo.csv","CS51",comment="Import of CS51 contig membership details",evidence="cap3",format="CSV")
    #myproc.runProcedure("/home/seqstore/agbrdf/parasite/cs46acontigs.csv","CS46A",comment="Import of Reads as mRNA features of CS46A contigs")
    #myproc.runProcedure("/home/seqstore/agbrdf/parasite/cs46bcontigs.csv","CS46B",comment="Import of Reads as mRNA features of CS46B contigs")
    #myproc.runProcedure("/home/seqstore/contigalignments1.csv","CS60",comment="Import of Reads as mRNA features of CS60 contigs")
    #myproc.runProcedure("/data/home/seqstore/deer/10031contigalignments.csv","CS60",comment="Import of Reads as mRNA features of CS60 contigs for cluster 10031")
    myproc.runProcedure("/data/home/seqstore/deer/singletalignments.csv","CS60",comment="re-import of Reads as mRNA features of CS60 contigs for singletons")




def main():
    connection=databaseModule.getConnection()

    #loadFeatureMain()
    #return


    loadSequenceMain()
    return


    loadFeatureMain()
    return


    loadSequenceMain()
    return


    loadFeatureMain()
    return

    loadSequenceMain()
    return


    loadFeatureMain()
    return

    loadSequenceMain()
    return

    loadFeatureMain()
    return

    loadSequenceFeatures(connection,"/home/seqstore/agbrdf/miscresults/CS37dumped_region_mRNA.gff",referenceLSIDprefix = 'Rice Genome', createNewRefs = True, evidence = "Blat Top Hit")
    return
  
    loadFeatureMain()
    return

    loadSequenceMain()
    return

    loadFeatureMain()
    return


    loadSequenceMain()
    return

    loadFeatureMain()
    return

    
    connection=databaseModule.getConnection()
    #loadSequenceFeatures(connection,"/data/home/seqstore/agbrdf/454_class_B.gff",referenceLSIDprefix = 'OARv1', createNewRefs = True, evidence = "ISGC 2008 Class B SNPs")
    loadSequenceFeatures(connection,"/data/home/seqstore/agbrdf/454_class_C.gff",referenceLSIDprefix = 'OARv1', createNewRefs = True, evidence = "ISGC 2008 Class C SNPs")
    return
    #loadSequenceFeatures(connection,"/data/home/seqstore/agbrdf/selectedSnpsFinal.gff",referenceLSIDprefix = 'OARv1', createNewRefs = True, evidence = "60K Chip Selected SNPs")
    #return

    loadSequenceMain()
    return
    loadContigExpression("/data/home/seqstore/agbrdf/cs34expression.csv")
    return
    connection=databaseModule.getConnection()
    populate_gene_info_synoyms(connection)
    return

        

    loadFeatureMain()
    return
    #loadAffyProbes("/data/home/seqstore/agbrdf/bovine/Bovine_probe_tab","Affymetrix.Bovine.ProbeSet","/data/home/seqstore/agbrdf/bovine/Bovine_consensus")
    #return

    loadSequenceMain()
    #connection=databaseModule.getConnection()
    #loadGeneinfo(connection,"/data/home/seqstore/agbrdf/print114geneinfo.csv","spliced transcript",doupdates=True,linksequences=False)
    #loadGeneinfo(connection,"/data/home/seqstore/agbrdf/SKIPgeneinfo.csv","spliced transcript",doupdates=True,linksequences=False)
    #loadGeneinfo(connection,"/data/home/seqstore/agbrdf/SKIPgeneinfo.csv","spliced transcript",doupdates=True,linksequences=False)
    #return
    return

    #loadFeatureMain()
    #return

    #annotateCDSMain()
    #return

    loadSequenceMain()
    return


    
    #loadSNPChip("/data/home/seqstore/agbrdf/genotype/AllMarkers", "Bovine 30K SNP chip (2006/2007)", "Bovine 30K SNP chip (2006/2007)", datastartsrow=3, fieldnamesrow=2)
    loadSNPChipResults("/data/home/seqstore/agbrdf/genotype/ALL_Genotypes", "Bovine 30K SNP chip (2006/2007)", datastartsrow=3, fieldnamesrow=2)
    return

    #loadSequences("C:/working/agbrdf/seq.csv","mRNA SEQUENCE","AgResearch.CS39")
    #loadFungalAffyProbes("M:/projects/agbrdf/data/AFT/AFT Affymetrix Chip/probeSequences.txt","AFT.ProbeSet","M:/projects/agbrdf/data/AFT/AFT Affymetrix Chip/Lp19-Lpa530240N.sif")
    #loadFungalAffyAnnotation("/data/home/seqstore/agbrdf/probeSetAnnotations.csv","/home/seqstore/agbrdf/Lp19-Lpa530240N.sif")

    # sue mcoard experiments : 
    ###loadGenstatNormalisation(114901, '/data/home/seqstore/agbrdf/sue/114901_Spots.csv')
    ##loadGenstatNormalisation(135658,'/data/home/seqstore/agbrdf/sue/135658_Spots.csv')
    ##loadGenstatNormalisation(156397,'/data/home/seqstore/agbrdf/sue/156397_Spots.csv')
    ##loadGenstatNormalisation(177136,'/data/home/seqstore/agbrdf/sue/177136_Spots.csv')
    ##loadGenstatNormalisation(218614,'/data/home/seqstore/agbrdf/sue/218614_Spots.csv')
    ##loadGenstatNormalisation(239353,'/data/home/seqstore/agbrdf/sue/239353_Spots.csv')
    ##loadGenstatNormalisation(260103,'/data/home/seqstore/agbrdf/sue/260103_Spots.csv')
    ##loadGenstatNormalisation(280883,'/data/home/seqstore/agbrdf/sue/280883_Spots.csv')
    ##loadGenstatNormalisation(301624,'/data/home/seqstore/agbrdf/sue/301624_Spots.csv')
    ##loadGenstatNormalisation(31934,'/data/home/seqstore/agbrdf/sue/31934_Spots.csv')
    ##loadGenstatNormalisation(322363,'/data/home/seqstore/agbrdf/sue/322363_Spots.csv')
    ##loadGenstatNormalisation(343102,'/data/home/seqstore/agbrdf/sue/343102_Spots.csv')
    ##loadGenstatNormalisation(384580,'/data/home/seqstore/agbrdf/sue/384580_Spots.csv')
    ##loadGenstatNormalisation(405319,'/data/home/seqstore/agbrdf/sue/405319_Spots.csv')
    ##loadGenstatNormalisation(426058,'/data/home/seqstore/agbrdf/sue/426058_Spots.csv')
    ##loadGenstatNormalisation(446797,'/data/home/seqstore/agbrdf/sue/446797_Spots.csv')
    ##loadGenstatNormalisation(467536,'/data/home/seqstore/agbrdf/sue/467536_Spots.csv')
    ##loadGenstatNormalisation(488275,'/data/home/seqstore/agbrdf/sue/488275_Spots.csv')
    ##loadGenstatNormalisation(509014,'/data/home/seqstore/agbrdf/sue/509014_Spots.csv')
    ##loadGenstatNormalisation(52676,'/data/home/seqstore/agbrdf/sue/52676_Spots.csv')
    ##loadGenstatNormalisation(529753,'/data/home/seqstore/agbrdf/sue/529753_Spots.csv')
    ##loadGenstatNormalisation(550492,'/data/home/seqstore/agbrdf/sue/550492_Spots.csv')
    ##loadGenstatNormalisation(571231,'/data/home/seqstore/agbrdf/sue/571231_Spots.csv')
    ##loadGenstatNormalisation(591970,'/data/home/seqstore/agbrdf/sue/591970_Spots.csv')
    ##loadGenstatNormalisation(612709,'/data/home/seqstore/agbrdf/sue/612709_Spots.csv')
    ##loadGenstatNormalisation(633448,'/data/home/seqstore/agbrdf/sue/633448_Spots.csv')
    ##loadGenstatNormalisation(654187,'/data/home/seqstore/agbrdf/sue/654187_Spots.csv')
    ##loadGenstatNormalisation(674926,'/data/home/seqstore/agbrdf/sue/674926_Spots.csv')
    ##loadGenstatNormalisation(695665,'/data/home/seqstore/agbrdf/sue/695665_Spots.csv')
    ##loadGenstatNormalisation(716404,'/data/home/seqstore/agbrdf/sue/716404_Spots.csv')
    ##loadGenstatNormalisation(73419,'/data/home/seqstore/agbrdf/sue/73419_Spots.csv')
    ##loadGenstatNormalisation(737143,'/data/home/seqstore/agbrdf/sue/737143_Spots.csv')
    ##loadGenstatNormalisation(94158,'/data/home/seqstore/agbrdf/sue/94158_Spots.csv')
    ##loadGenstatNormalisation(363841,'/data/home/seqstore/agbrdf/sue/extract17lowscan_results.csv')
    ##loadGenstatNormalisation(197875,'/data/home/seqstore/agbrdf/sue/slide13lowscan Results.csv')
    ##loadGenstatNormalisation(757882,'/data/home/seqstore/agbrdf/sue/757882_Spots.csv')

    #loadGFFFeatures('/home/seqstore/agbrdf/AFT_AffyChip_genePredictions.gff', 'AFT')

    ##loadGenstatNormalisation(1370105,'/data/home/seqstore/agbrdf/lisa/1370105_Spots.txt','fixed width')
    ##loadGenstatNormalisation(1391612,'/data/home/seqstore/agbrdf/lisa/1391612_Spots.txt','fixed width')
    ##loadGenstatNormalisation(1413119,'/data/home/seqstore/agbrdf/lisa/1413119_Spots.txt','fixed width')
    ##loadGenstatNormalisation(1434626,'/data/home/seqstore/agbrdf/lisa/1434626_Spots.txt','fixed width')
    ##loadGenstatNormalisation(1456133,'/data/home/seqstore/agbrdf/lisa/1456133_Spots.txt','fixed width')
    ##loadGenstatNormalisation(1477640,'/data/home/seqstore/agbrdf/lisa/1477640_Spots.txt','fixed width')
    ##loadGenstatNormalisation(1499147,'/data/home/seqstore/agbrdf/lisa/1499147_Spots.txt','fixed width')
    ##loadGenstatNormalisation(1520654,'/data/home/seqstore/agbrdf/lisa/1520654_Spots.txt','fixed width')
    ##loadGenstatNormalisation(1542161,'/data/home/seqstore/agbrdf/lisa/1542161_Spots.txt','fixed width')
    ##loadGenstatNormalisation(1563668,'/data/home/seqstore/agbrdf/lisa/1563668_Spots.txt','fixed width')
    ##loadGenstatNormalisation(1585175,'/data/home/seqstore/agbrdf/lisa/1585175_Spots.txt','fixed width')
    ##loadGenstatNormalisation(1606682,'/data/home/seqstore/agbrdf/lisa/1606682_Spots.txt','fixed width')
    ##loadGenstatNormalisation(1628189,'/data/home/seqstore/agbrdf/lisa/1628189_Spots.txt','fixed width')
    ##loadGenstatNormalisation(1649696,'/data/home/seqstore/agbrdf/lisa/1649696_Spots.txt','fixed width')
    ##loadGenstatNormalisation(1671203,'/data/home/seqstore/agbrdf/lisa/1671203_Spots.txt','fixed width')
    ##loadGenstatNormalisation(1692710,'/data/home/seqstore/agbrdf/lisa/1692710_Spots.txt','fixed width')
    ##loadGenstatNormalisation(1714217,'/data/home/seqstore/agbrdf/lisa/1714217_Spots.txt','fixed width')
    ##loadGenstatNormalisation(1735724,'/data/home/seqstore/agbrdf/lisa/1735724_Spots.txt','fixed width')
    ##loadGenstatNormalisation(1757231,'/data/home/seqstore/agbrdf/lisa/1757231_Spots.txt','fixed width')
    ##loadGenstatNormalisation(1778738,'/data/home/seqstore/agbrdf/lisa/1778738_Spots.txt','fixed width')
    ##loadGenstatNormalisation(1800245,'/data/home/seqstore/agbrdf/lisa/1800245_Spots.txt','fixed width')
    ##loadGenstatNormalisation(1821752,'/data/home/seqstore/agbrdf/lisa/1821752_Spots.txt','fixed width')
    ##loadGenstatNormalisation(1843259,'/data/home/seqstore/agbrdf/lisa/1843259_Spots.txt','fixed width')
    ##loadGenstatNormalisation(1864766,'/data/home/seqstore/agbrdf/lisa/1864766_Spots.txt','fixed width')
    ##loadGenstatNormalisation(1886273,'/data/home/seqstore/agbrdf/lisa/1886273_Spots.txt','fixed width')
    ##loadGenstatNormalisation(1907780,'/data/home/seqstore/agbrdf/lisa/1907780_Spots.txt','fixed width')
    ##loadGenstatNormalisation(1929287,'/data/home/seqstore/agbrdf/lisa/1929287_Spots.txt','fixed width')
    ##loadGenstatNormalisation(1950794,'/data/home/seqstore/agbrdf/lisa/1950794_Spots.txt','fixed width')
    ##loadGenstatNormalisation(1972301,'/data/home/seqstore/agbrdf/lisa/1972301_Spots.txt','fixed width')
    ##loadGenstatNormalisation(1993808,'/data/home/seqstore/agbrdf/lisa/1993808_Spots.txt','fixed width')
    ##loadGenstatNormalisation(2015315,'/data/home/seqstore/agbrdf/lisa/2015315_Spots.txt','fixed width')
    ##loadGenstatNormalisation(2036822,'/data/home/seqstore/agbrdf/lisa/2036822_Spots.txt','fixed width')
    ##loadGenstatNormalisation(2058329,'/data/home/seqstore/agbrdf/lisa/2058329_Spots.txt','fixed width')
    ##loadGenstatNormalisation(2079836,'/data/home/seqstore/agbrdf/lisa/2079836_Spots.txt','fixed width')
    ##loadGenstatNormalisation(2146573,'/data/home/seqstore/agbrdf/lisa/2146573_Spots.txt','fixed width')
    ##loadGenstatNormalisation(2168080,'/data/home/seqstore/agbrdf/lisa/2168080_Spots.txt','fixed width')
    ##loadGenstatNormalisation(2302516,'/data/home/seqstore/agbrdf/sue/muscle032007/normalisation/2302516_Spots.txt','fixed width')
    ##loadGenstatNormalisation(2323255,'/data/home/seqstore/agbrdf/sue/muscle032007/normalisation/2323255_Spots.txt','fixed width')
    ##loadGenstatNormalisation(2675827,'/data/home/seqstore/agbrdf/sue/muscle032007/normalisation/2675827_Spots.txt','fixed width')
    ##loadGenstatNormalisation(2696566,'/data/home/seqstore/agbrdf/sue/muscle032007/normalisation/2696566_Spots.txt','fixed width')
    ##loadGenstatNormalisation(2717305,'/data/home/seqstore/agbrdf/sue/muscle032007/normalisation/2717305_Spots.txt','fixed width')
    ##loadGenstatNormalisation(2738044,'/data/home/seqstore/agbrdf/sue/muscle032007/normalisation/2738044_Spots.txt','fixed width')

    #loadGenstatNormalisation(2343994,'/data/home/seqstore/agbrdf/sue/muscle032007/normalisation/2343994_Spots.txt','fixed width')
    #loadGenstatNormalisation(2364733,'/data/home/seqstore/agbrdf/sue/muscle032007/normalisation/2364733_Spots.txt','fixed width')
    #loadGenstatNormalisation(2385472,'/data/home/seqstore/agbrdf/sue/muscle032007/normalisation/2385472_Spots.txt','fixed width')
    #loadGenstatNormalisation(2406211,'/data/home/seqstore/agbrdf/sue/muscle032007/normalisation/2406211_Spots.txt','fixed width')
    #loadGenstatNormalisation(2426950,'/data/home/seqstore/agbrdf/sue/muscle032007/normalisation/2426950_Spots.txt','fixed width')
    #loadGenstatNormalisation(2447689,'/data/home/seqstore/agbrdf/sue/muscle032007/normalisation/2447689_Spots.txt','fixed width')
    #loadGenstatNormalisation(2468428,'/data/home/seqstore/agbrdf/sue/muscle032007/normalisation/2468428_Spots.txt','fixed width')
    #loadGenstatNormalisation(2489167,'/data/home/seqstore/agbrdf/sue/muscle032007/normalisation/2489167_Spots.txt','fixed width')
    #loadGenstatNormalisation(2509906,'/data/home/seqstore/agbrdf/sue/muscle032007/normalisation/2509906_Spots.txt','fixed width')
    #loadGenstatNormalisation(2530645,'/data/home/seqstore/agbrdf/sue/muscle032007/normalisation/2530645_Spots.txt','fixed width')
    #loadGenstatNormalisation(2551384,'/data/home/seqstore/agbrdf/sue/muscle032007/normalisation/2551384_Spots.txt','fixed width')
    #loadGenstatNormalisation(2572123,'/data/home/seqstore/agbrdf/sue/muscle032007/normalisation/2572123_Spots.txt','fixed width')
    #loadGenstatNormalisation(2592862,'/data/home/seqstore/agbrdf/sue/muscle032007/normalisation/2592862_Spots.txt','fixed width')
    #loadGenstatNormalisation(2613601,'/data/home/seqstore/agbrdf/sue/muscle032007/normalisation/2613601_Spots.txt','fixed width')
    #loadGenstatNormalisation(2634340,'/data/home/seqstore/agbrdf/sue/muscle032007/normalisation/2634340_Spots.txt','fixed width')
    #loadGenstatNormalisation(2655079,'/data/home/seqstore/agbrdf/sue/muscle032007/normalisation/2655079_Spots.txt','fixed width')
    #loadGenstatNormalisation(2758783,'/data/home/seqstore/agbrdf/sue/muscle032007/normalisation/2758783_Spots.txt','fixed width')
    #loadGenstatNormalisation(2779522,'/data/home/seqstore/agbrdf/sue/muscle032007/normalisation/2779522_Spots.txt','fixed width')
    #loadGenstatNormalisation(2800261,'/data/home/seqstore/agbrdf/sue/muscle032007/normalisation/2800261_Spots.txt','fixed width')
    #loadGenstatNormalisation(2821000,'/data/home/seqstore/agbrdf/sue/muscle032007/normalisation/2821000_Spots.txt','fixed width')
    #loadGenstatNormalisation(2841739,'/data/home/seqstore/agbrdf/sue/muscle032007/normalisation/2841739_Spots.txt','fixed width')
    #loadGenstatNormalisation(2862478,'/data/home/seqstore/agbrdf/sue/muscle032007/normalisation/2862478_Spots.txt','fixed width')
    #loadGenstatNormalisation(2883217,'/data/home/seqstore/agbrdf/sue/muscle032007/normalisation/2883217_Spots.txt','fixed width')
    #loadGenstatNormalisation(2903956,'/data/home/seqstore/agbrdf/sue/muscle032007/normalisation/2903956_Spots.txt','fixed width')
    #loadGenstatNormalisation(2924695,'/data/home/seqstore/agbrdf/sue/muscle032007/normalisation/2924695_Spots.txt','fixed width')
    #loadGenstatNormalisation(2945434,'/data/home/seqstore/agbrdf/sue/muscle032007/normalisation/2945434_Spots.txt','fixed width')
    #loadGenstatNormalisation(2966173,'/data/home/seqstore/agbrdf/sue/muscle032007/normalisation/2966173_Spots.txt','fixed width')
    #loadGenstatNormalisation(2986912,'/data/home/seqstore/agbrdf/sue/muscle032007/normalisation/2986912_Spots.txt','fixed width')
    #loadGenstatNormalisation(3007651,'/data/home/seqstore/agbrdf/sue/muscle032007/normalisation/3007651_Spots.txt','fixed width')
    #loadGenstatNormalisation(3028390,'/data/home/seqstore/agbrdf/sue/muscle032007/normalisation/3028390_Spots.txt','fixed width')

    loadGenstatNormalisation(3049130,'/data/home/seqstore/agbrdf/sue/muscle032007/normalisation/3049130_Spots.txt','fixed width')
    loadGenstatNormalisation(3069869,'/data/home/seqstore/agbrdf/sue/muscle032007/normalisation/3069869_Spots.txt','fixed width')
    loadGenstatNormalisation(3090608,'/data/home/seqstore/agbrdf/sue/muscle032007/normalisation/3090608_Spots.txt','fixed width')
    loadGenstatNormalisation(3111347,'/data/home/seqstore/agbrdf/sue/muscle032007/normalisation/3111347_Spots.txt','fixed width')
    loadGenstatNormalisation(3132086,'/data/home/seqstore/agbrdf/sue/muscle032007/normalisation/3132086_Spots.txt','fixed width')
    loadGenstatNormalisation(3152825,'/data/home/seqstore/agbrdf/sue/muscle032007/normalisation/3152825_Spots.txt','fixed width')
    loadGenstatNormalisation(3173564,'/data/home/seqstore/agbrdf/sue/muscle032007/normalisation/3173564_Spots.txt','fixed width')
    loadGenstatNormalisation(3194303,'/data/home/seqstore/agbrdf/sue/muscle032007/normalisation/3194303_Spots.txt','fixed width')
    loadGenstatNormalisation(3215042,'/data/home/seqstore/agbrdf/sue/muscle032007/normalisation/3215042_Spots.txt','fixed width')
    loadGenstatNormalisation(3235781,'/data/home/seqstore/agbrdf/sue/muscle032007/normalisation/3235781_Spots.txt','fixed width')
    loadGenstatNormalisation(3256520,'/data/home/seqstore/agbrdf/sue/muscle032007/normalisation/3256520_Spots.txt','fixed width')
    loadGenstatNormalisation(3277259,'/data/home/seqstore/agbrdf/sue/muscle032007/normalisation/3277259_Spots.txt','fixed width')
    loadGenstatNormalisation(3297998,'/data/home/seqstore/agbrdf/sue/muscle032007/normalisation/3297998_Spots.txt','fixed width')
    loadGenstatNormalisation(3318737,'/data/home/seqstore/agbrdf/sue/muscle032007/normalisation/3318737_Spots.txt','fixed width')
    loadGenstatNormalisation(3339476,'/data/home/seqstore/agbrdf/sue/muscle032007/normalisation/3339476_Spots.txt','fixed width')
    loadGenstatNormalisation(3360215,'/data/home/seqstore/agbrdf/sue/muscle032007/normalisation/3360215_Spots.txt','fixed width')
    loadGenstatNormalisation(3380954,'/data/home/seqstore/agbrdf/sue/muscle032007/normalisation/3380954_Spots.txt','fixed width')
    loadGenstatNormalisation(3401693,'/data/home/seqstore/agbrdf/sue/muscle032007/normalisation/3401693_Spots.txt','fixed width')
    loadGenstatNormalisation(3422432,'/data/home/seqstore/agbrdf/sue/muscle032007/normalisation/3422432_Spots.txt','fixed width')


    #loadGFFGeneTracks('/data/home/seqstore/agbrdf/nauman/NCBI_genes.gff')

    
if __name__ == "__main__":
   main()
