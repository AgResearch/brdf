#
# This module implements lite home-made parsers and utils for GFF
# and other files
#
from types import *
import re
import string
from brdfExceptionModule import brdfException
from dataImportModule import dataSourceOb,importProcedureOb
from sequenceModule import bioSequenceOb
import csv
import sys

#-------------------- module variables ---------------------------

DEBUG = 1

#-------------------- module methods  ----------------------------

def debugPrint(astring):
    if DEBUG == 1:
        print astring
        

def tidyout(line, linewidth, currentpos):
    """ This method is used to pour a string into a rectangular shape. It is given
    which column we are up to in the shape, the linewidth and the string. It returns
    a string with the correct \n characters inserted, and an updated column
    position. """
    result=''
    for i in range(0,len(line)):
        if currentpos == linewidth:
            result += '\n'
            currentpos = 0            
        result += line[i:i+1]
        currentpos += 1

        #print currentpos
        
    return (result,currentpos)



def loadSequenceFeatures(connection, infile, referenceLSIDprefix = 'Btau4', referenceSequenceType = 'genomic DNA', createNewRefs = False,evidence=None):

    #connection=PgSQL.connect(host=databaseModule.host,database=databaseModule.database, \
    #    		   user=databaseModule.user,password=databaseModule.password)
    """ example :
BTA1    MEGABLAST       match   99682   99871   311     -       .       Match AW1_E0SBQCD02JF2QP; identity 96.32; evalue 4.5e-38; num_hits 3
BTA1    MEGABLAST       match   99707   99947   322     +       .       Match SBF1_EXH74BZ02F1DQO; identity 90.36; evalue 6.66666666667e-28; num_hits 3
BTA1    MEGABLAST       match   100730  100999  407     -       .       Match PD1_EZ5VH4B01D4SIG; identity 93.70; evalue 2e-111; num_hits 1
BTA1    MEGABLAST       match   100739  101006  412     -       .       Match Mer1_EYZIYZN02IGA8R; identity 94.40; evalue 5e-113; num_hits 1
BTA1    MEGABLAST       match   101282  101356  93.3    +       .       Match PD1_E0IYJTN02F8LZB; identity 88.16; evalue 1e-17; num_hits 1
BTA1    MEGABLAST       match   101573  101619  77.0    +       .       Match Mer1_EZAXSH301AYDDS; identity 95.74; evalue 1e-12; num_hits 1    
    """
    insertCursor = connection.cursor()    

    #GFFParser = GFFFileParser("c:/working/isgcdata/test.gff")
    GFFParser = GFFFileParser(infile)    
    
    # read ahead
    GFFParser.parse()

    debugPrint(str(GFFParser))
    
    recordCount = 0
    insertCount = 0

    referenceDict = {}
    

    importProcedure = importProcedureOb()        
    try:
        importProcedure.initFromDatabase("gffutils.loadSequenceFeatures",connection)
    except brdfException:
        importProcedure.initNew(connection)
        importProcedure.databaseFields.update ( {
            'xreflsid' : "dbprocedures.loadSequenceFeatures",
            'procedurename' : "dbprocedures.loadSequenceFeatures",
        })
        importProcedure.insertDatabase(connection)


    dataSource = dataSourceOb()
    dataSource.initNew(connection,"GFF")
    dataSource.databaseFields.update({
        'xreflsid' : infile,
        'numberoffiles' : 1
    })        
    dataSource.insertDatabase(connection)        


    # loop through reading the file
    featDict =  GFFParser.nextRecord()
    while GFFParser.parserState["EOF"] == 0:
        recordCount += 1

        #print "==featDict==>"+str(featDict)

        if recordCount%500 == 1:
            debugPrint("record %s"%recordCount)
            debugPrint(str(featDict))


        # check we have the required reference
        referenceLSID = "%s.%s"%(referenceLSIDprefix, featDict["Reference"])
        if referenceLSID not in referenceDict:

            bioSequence = bioSequenceOb()
            try:
                bioSequence.initFromDatabase(referenceLSID,connection)
            except brdfException, msg:
                if bioSequence.obState['ERROR'] != 1:
                    raise brdfException(msg)
                elif createNewRefs:         
                    bioSequence.initNew(connection)
                    bioSequence.databaseFields.update({
                        'xreflsid' : referenceLSID,
                        'sequencename' : featDict["Reference"],
                        'sequencetype' : referenceSequenceType
                        })
                    bioSequence.insertDatabase(connection)
                    insertCount += 1
                    dataSource.addImportFunction(bioSequence,importProcedure,connection)            
                else:
                    raise brdfException(msg)
                    

            dataSource.addImportFunction(bioSequence,importProcedure,connection)

            referenceDict[referenceLSID] = bioSequence.databaseFields['obid']
                    
        
        sql = """
        insert into BioSequenceFeatureFact(
            biosequenceob  ,
            xreflsid ,
            obkeywords, 
            featuretype,
            featurestart,
            featurestop,
            featurestrand,
            featurelength,
            featureaccession,
            featurecomment,
            score,
            evidence)
        values(
            %(obid)s,
            %(xreflsid)s,
            %(obkeywords)s,
            %(featuretype)s,
            %(featurestart)s,
            %(featurestop)s,
            %(featurestrand)s,
            %(featurelength)s,
            %(featureaccession)s,
            %(featurecomment)s,
            %(score)s,
            %(evidence)s )
        """
        
        sqlDict = {
            'obid' : referenceDict[referenceLSID],
            'xreflsid' : "%s.%s"%(referenceLSID, featDict["Accession"]),
            'obkeywords' : "%(GFFRecordType)s %(Accession)s"%featDict,
            'featuretype' : featDict["GFFRecordType"],
            'featurestart' : featDict["FeatureStart"],
            'featurestop' : featDict["FeatureStop"] ,
            'score' : featDict["Score"] ,
            'featurestrand' : {'+' : 1 , '-' : -1 , 1 : 1 , -1 : -1, 0 : 0 , '.' : 0 }[featDict["Strand"]] ,
            'featurelength' : 1 + featDict["FeatureStop"] - featDict["FeatureStart"],
            'featureaccession' : featDict['Accession'],
            'featurecomment' : featDict['Description'] ,
            'evidence' : evidence
        }

        #print "executing " + sql%sqlDict

        insertCursor.execute(sql,sqlDict)
        connection.commit()

        #print sql%sqlDict

        #if recordCount == 10 :
        #    break
        featDict =  GFFParser.nextRecord()

    insertCursor.close()
    connection.close()




def makeGBrowseDisplayCalls(infile,outfile):
    """ this method reads a GFF file and constructs inserts into the brdf displayfunction table ,
    containing calls that will display inline GBrowse images
    These look like :

    {'Description': ['mRNA 161106CS4401598900001_p1', 'exon_start 566',
    'exon_stop 702', ''], 'Reference': 'Chr1.450000001-455000000', 'GFFFileType':
    'GMAP_mondom4_cs44', 'Accession': '161106CS4401598900001', 'Score': '83.5',
    'Unused1': '.', 'FeatureStart': '4057526', 'FeatureStop': '4057662', 'GFFRecordType':
    'exon', 'Strand': '-'}

    Example : http://www.possumbase.org.nz/cgi-bin/gbrowse_img/mondom4?name=chr8:169050616..169253529;type=CONTIGS+HUMAN_REFSEQ+ENSEMBL+AG_POSSUM+CS44+XENO_REF_GENE+SSR+BCM_SNP;width=800;keystyle=between;grid=0

    and the link should be

    http://www.possumbase.org.nz/cgi-bin/gbrowse/mondom4/?start=169050616;stop=169253529;ref=chr8;width=1024;version=100;label=CONTIGS-HUMAN_REFSEQ-ENSEMBL-AG_POSSUM-CS44-XENO_REF_GENE-SSR-BCM_SNP;keystyle=between;grid=0
    """
    parser = GFFFileParser(infile)

    # set up the first mRNA record
    parser.parse()
    gffDict =  parser.nextRecord()
    writer = open(outfile,"w")
    bestMaps={}
    

    # loop through reading the file
    rowcount = 0
    while parser.parserState["ERROR"] == 0 and parser.parserState["EOF"] == 0:
        rowcount += 1
        if rowcount%500 ==1 :
            debugPrint("%d:%s"%(rowcount,str(gffDict)))
        #print str(gffDict)
        #print str(gffDict)
        if gffDict['GFFRecordType'] == 'mRNA' and re.search("_p1",gffDict['Description'][0]) != None:

            if gffDict["Accession"] not in bestMaps:
                bestMaps[gffDict["Accession"]] = gffDict
                gffDict.update({
                    'count' : 1
                })
            elif float(gffDict["Score"]) > float(bestMaps[gffDict["Accession"]]["Score"]):
                gffDict.update({
                    'count' : bestMaps[gffDict["Accession"]]['count'] +1
                })
                bestMaps[gffDict["Accession"]] = gffDict
        gffDict =  parser.nextRecord()

    for accession in bestMaps.keys():
        gffDict=bestMaps[accession]

        debugPrint(str(gffDict))
                    
        chromosome = re.split('\.',gffDict['Reference'])[0]
        start = int(gffDict['FeatureStart'])
        stop = int(gffDict['FeatureStop'])
        (start,stop) = (min(start,stop),max(start,stop))
        (start,stop) = (start - abs(stop-start)*.5 , stop + abs(stop-start) * .5)
        (start,stop) = (int(start),int(stop))
            
        reference = "%s:%s..%s"%(chromosome,start,stop)
            
        imageurl="http://www.possumbase.org.nz/cgi-bin/gbrowse_img/mondom4?name=%(reference)s;type=CONTIGS+HUMAN_REFSEQ+ENSEMBL+AG_POSSUM+CS44+XENO_REF_GENE+SSR+BCM_SNP;width=800;keystyle=between;grid=0"%{
            'reference' : reference
        }

        linkurl="http://www.possumbase.org.nz/cgi-bin/gbrowse/mondom4/?start=%(start)s;stop=%(stop)s;ref=%(chromosome)s;width=800;version=100;label=CONTIGS-HUMAN_REFSEQ-ENSEMBL-AG_POSSUM-CS44-XENO_REF_GENE-SSR-BCM_SNP;keystyle=between;grid=0"%{
            'start' : start,
            'stop' : stop,
            'chromosome' : chromosome
        }
            
        #print imageurl
        #print linkurl

        sql = """
insert into displayfunction(xreflsid, ob,displayprocedureob,invocation,functioncomment)
select 
   bs.xreflsid || '.' || dp.xreflsid,
   bs.obid,
   dp.obid,
   'getInlineURL(' || bs.obid || 
    ', obtype="biosequenceob", usercontext=context, fetcher=self.fetcher,imagepath=self.imagepath, tempimageurl=self.tempimageurl,method="img",sectionheading="AgResearch Opossum GBrowse for ' ||
    bs.xreflsid ||
    ' (best of %(count)s high scoring alignments)",uristring="%(imageurl)s"'||
    ',linkuri="%(linkurl)s")',
   'AgReseach Opossum GBRowse inline display for CS44 contigs'
from
   biosequenceob bs join displayprocedureob dp on
   bs.sequencename = '%(contigname)s' and
   dp.xreflsid = 'displayProcedures.getInlineURL' ;
   """% {
        'imageurl' : imageurl,
        'linkurl' : linkurl,
        'contigname' : gffDict['Accession'],
        'count' : gffDict['count']
        }
            #print sql
        writer.write(sql);
        

    writer.close()
        





def transformGappedCoords(instart, oldgap, newgap, gapendarray):
    """
    this method is used to take coordinates relative to a given pseudoChromosome, and
    recalculate them for a different gap size - for example we made a ChrUn with 5K gaps and
    needed later to change coordinates of mapped objects , to a chr with 10K gaps.

    e.g.

    instart = 3000000
    oldgap=5000
    newgap=10000
    gapendarray
    array of positions where gaps end - e.g. might be constructed from 


CHRUN   pseudochromosome        BCM_scaffold    1       2600833 .       .       .       BCM_UNscaffold ChrUn.1
CHRUN   pseudochromosome        BCM_scaffold    2605834 4363633 .       .       .       BCM_UNscaffold ChrUn.2
CHRUN   pseudochromosome        BCM_scaffold    4368634 5983670 .       .       .       BCM_UNscaffold ChrUn.3
CHRUN   pseudochromosome        BCM_scaffold    5988671 7539290 .       .       .       BCM_UNscaffold ChrUn.4
CHRUN   pseudochromosome        BCM_scaffold    7544291 9077187 .       .       .       BCM_UNscaffold ChrUn.5

    to give
    [2605833, 4368633, etc]
    """
    insertArray = [newgap-oldgap for gapend in gapendarray if gapend < instart]
    if len(insertArray) > 0:
        newstart = instart + reduce(lambda x,y : x+y, insertArray)
    else:
        newstart = instart
    return newstart


def unmakeChrUnMapping(transformfile,infile=sys.stdin,chrunname='BTAUN'):
    # this does the opposite of makeChrUnMapping
    # get the array of gap endings - NB these are 5K ones, so since we are working
    # from files that have been transformed to 10K gaps, modify the
    # ends to be 10K
    gapEndArray = []
    gapEndLeftOwnerArray=[]
    scaffoldLookup = {}
    recordCount = 0
    for record in transformfile:
        recordCount += 1
        fields = re.split('\s+',record)
        gapEndLeftOwnerArray.append(fields[-2])           
        #scaffoldLookup[fields[-2].upper()] = (int(fields[3]),int(fields[4]))
        scaffoldLookup[fields[-2].upper()] = int(fields[3]) +((recordCount-1) * 5000)      
        if int(fields[3]) > 1:
            gapEndArray.append(int(fields[3])-1 + ((recordCount-1) * 5000))


    #print zip(range(0,400),gapEndArray[0:400])

    # in the above, the left owner of a gap (end) is the scaffold
    # to the left of the gap

            
    transformfile.close()

    # remember we are reading through a file with 10K gapped coords
    recordCount = 0
    for record in infile:
        if len(record.strip()) < 1:
            continue
        #print "*****%s"%record
        recordCount += 1
        #if recordCount > 2:
        #    break
        if re.search(chrunname,record,re.I) != None:

            # find 
            fields=re.split('\t',record)
            start10k=int(fields[3])
            stop10k=int(fields[4])

            # obtain coords using the 5K gaps, which is the reference we are looking at.
            #start5k = transformGappedCoords(start10k,10000,5000,gapEndArray)
            #print "%s => %s"%(start10k,start5k)

            # now locate this in the gapend array. We find the next lowest gap end
            foundit = False
            for i in range(0,len(gapEndArray)):
                if start10k < gapEndArray[i]:
                    fields[0] = gapEndLeftOwnerArray[i]
                    fields[3] = 1+ start10k - scaffoldLookup[gapEndLeftOwnerArray[i].upper()]
                    fields[4] = str(fields[3] + stop10k-start10k)
                    fields[3] = str(fields[3])
                    foundit = True
                    break

            if foundit:
                newrecord = string.join(fields,"\t")
                debugPrint(newrecord)
            else:
                debugPrint("!!! could not find %s"%record)
        else:
            debugPrint("??????????%s"%record) 
    




def makeChrUnMapping(transformfile,infile=sys.stdin,chrunname='CHRUN'):
    # this reads through a GFF file containing the following
    #CHRUN.4	AgR_SSR                         	SSR                             	1167743	1167762	.                               	.                               	.                               	SSR BMS1583114; repeat_type dinucleotide ; motif AT ; score 18 ; length 20; seqid BMS1583114
    #CHRUN.4	AgR_SSR                         	SSR                             	1168689	1168714	.                               	.                               	.                               	SSR BMS1583115; repeat_type dinucleotide ; motif AT ; score 17 ; length 26; seqid BMS1583115
    #CHRUN.4	AgR_SSR                         	SSR                             	1175782	1175801	.                               	.                               	.                               	SSR BMS1583120; repeat_type dinucleotide ; motif AC ; score 18 ; length 20; seqid BMS1583120
    #CH
    # and does the folloeing
    # first - read in a 5 K GFF file of CHRUN accessions that looks like this :
    # CHRUN	pseudochromosome	BCM_scaffold	1	2600833	.	.	.	BCM_UNscaffold ChrUn.1
    #CHRUN	pseudochromosome	BCM_scaffold	2605834	4363633	.	.	.	BCM_UNscaffold ChrUn.2 
    #CHRUN	pseudochromosome	BCM_scaffold	4368634	5983670	.	.	.	BCM_UNscaffold ChrUn.3
    #
    # and index by upper case last token - also accumulate a transformarray
    #
    # now for each record, we look up the accession in the scaffoldLookup , and calculate the
    # 5K coords, then transform to the 10K coords, and output updated GFF
    
    

    # get the array of gap endings
    gapEndArray = []
    scaffoldLookup = {}
    for record in transformfile:
        fields = re.split('\s+',record)
        scaffoldLookup[fields[-2].upper()] = (int(fields[3]),int(fields[4]))
        if int(fields[3]) > 1:
            gapEndArray.append(int(fields[3])-1)
            
    transformfile.close()


    for record in infile:
        if re.search(chrunname,record,re.I) != None:
            fields=re.split('\t',record)
            oldstart=int(fields[3]) + scaffoldLookup[fields[0]][0] - 1
            oldstop=int(fields[4]) + scaffoldLookup[fields[0]][0] - 1
            newstart = transformGappedCoords(oldstart,5000,10000,gapEndArray)
            newstop = newstart + oldstop - oldstart
            fields[3] = str(newstart)
            fields[4] = str(newstop)
            fields[0] = 'BTAUN'
            newrecord = string.join(fields,'\t')
            debugPrint(newrecord)
        else:
            debugPrint("??????????%s"%record)
            

"""
    print "%s %s --> %s\n"%('BCM_UNscaffold ChrUn.1',1,transformGappedCoords(1, 5000, 10000, gapEndArray))
    print "%s %s --> %s\n"%('BCM_UNscaffold ChrUn.2',2605834,transformGappedCoords(2605834, 5000, 10000, gapEndArray))
    print "%s %s --> %s\n"%('BCM_UNscaffold ChrUn.50',59788888,transformGappedCoords(59788888, 5000, 10000, gapEndArray))
    print "%s %s --> %s\n"%('BCM_UNscaffold ChrUn.250',206876706,transformGappedCoords(206876706, 5000, 10000, gapEndArray))
    

    
    print "%s %s --> %s\n"%('BCM_UNscaffold ChrUn.2471',817524381,transformGappedCoords(817524381, 5000, 10000, gapEndArray))
    print "%s %s --> %s\n"%('BCM_UNscaffold ChrUn.500',336980057,transformGappedCoords(336980057, 5000, 10000, gapEndArray))    
    print "%s %s --> %s\n"%('BCM_UNscaffold ChrUn.1000', 521789959,transformGappedCoords( 521789959, 5000, 10000, gapEndArray))    


    
    print "%s %s --> %s\n"%('BCM_UNscaffold ChrUn.25000',1452091982,transformGappedCoords(1452091982, 5000, 10000, gapEndArray))
    print "%s %s --> %s\n"%('BCM_UNscaffold ChrUn.80000',1792627769,transformGappedCoords(1792627769, 5000, 10000, gapEndArray))
    print "%s %s --> %s\n"%('BCM_UNscaffold ChrUn.98058',1893301690,transformGappedCoords(1893301690, 5000, 10000, gapEndArray))
    print "%s %s --> %s\n"%('BCM_UNscaffold ChrUn.98057',1893295928,transformGappedCoords(1893295928, 5000, 10000, gapEndArray))    
    print "%s %s --> %s\n"%('160903CS1801001600001',1881608304,transformGappedCoords(1881608304, 5000, 10000, gapEndArray))    
    print "%s %s --> %s\n"%('160903CS1801045800001',1036609178,transformGappedCoords(1036609178, 5000, 10000, gapEndArray))
    print "%s %s --> %s\n"%('160903CS1801007800002',671284990,transformGappedCoords(671284990, 5000, 10000, gapEndArray))    
"""
    
    #print gapEndArray





    

def patchChrUnMapping(transformfile,infile=sys.stdin,chrunname='CHRUN'):

    # get the array of gap endings
    gapEndArray = []
    for record in transformfile:
        fields = re.split('\s+',record)
        if int(fields[3]) > 1:
            gapEndArray.append(int(fields[3])-1)
    transformfile.close()


    for record in infile:
        if re.search(chrunname,record,re.I) != None:
            fields=re.split('\t',record)
            oldstart=int(fields[3])
            oldstop=int(fields[4])
            newstart = transformGappedCoords(oldstart,5000,10000,gapEndArray)
            newstop = newstart + oldstop - oldstart
            fields[3] = str(newstart)
            fields[4] = str(newstop)
            newrecord = string.join(fields,'\t')
            print newrecord
        else:
            print record
            

"""
    print "%s %s --> %s\n"%('BCM_UNscaffold ChrUn.1',1,transformGappedCoords(1, 5000, 10000, gapEndArray))
    print "%s %s --> %s\n"%('BCM_UNscaffold ChrUn.2',2605834,transformGappedCoords(2605834, 5000, 10000, gapEndArray))
    print "%s %s --> %s\n"%('BCM_UNscaffold ChrUn.50',59788888,transformGappedCoords(59788888, 5000, 10000, gapEndArray))
    print "%s %s --> %s\n"%('BCM_UNscaffold ChrUn.250',206876706,transformGappedCoords(206876706, 5000, 10000, gapEndArray))
    

    
    print "%s %s --> %s\n"%('BCM_UNscaffold ChrUn.2471',817524381,transformGappedCoords(817524381, 5000, 10000, gapEndArray))
    print "%s %s --> %s\n"%('BCM_UNscaffold ChrUn.500',336980057,transformGappedCoords(336980057, 5000, 10000, gapEndArray))    
    print "%s %s --> %s\n"%('BCM_UNscaffold ChrUn.1000', 521789959,transformGappedCoords( 521789959, 5000, 10000, gapEndArray))    


    
    print "%s %s --> %s\n"%('BCM_UNscaffold ChrUn.25000',1452091982,transformGappedCoords(1452091982, 5000, 10000, gapEndArray))
    print "%s %s --> %s\n"%('BCM_UNscaffold ChrUn.80000',1792627769,transformGappedCoords(1792627769, 5000, 10000, gapEndArray))
    print "%s %s --> %s\n"%('BCM_UNscaffold ChrUn.98058',1893301690,transformGappedCoords(1893301690, 5000, 10000, gapEndArray))
    print "%s %s --> %s\n"%('BCM_UNscaffold ChrUn.98057',1893295928,transformGappedCoords(1893295928, 5000, 10000, gapEndArray))    
    print "%s %s --> %s\n"%('160903CS1801001600001',1881608304,transformGappedCoords(1881608304, 5000, 10000, gapEndArray))    
    print "%s %s --> %s\n"%('160903CS1801045800001',1036609178,transformGappedCoords(1036609178, 5000, 10000, gapEndArray))
    print "%s %s --> %s\n"%('160903CS1801007800002',671284990,transformGappedCoords(671284990, 5000, 10000, gapEndArray))    
"""
    
    #print gapEndArray
    




#-------------------- module classes  ----------------------------






class GeneralGFFFactory (object):
    """ class for making GFF files in various contexts """
    def __init__(self,infilename):
        object.__init__(self)

        self.infilename = infilename

        self.parserState = {
            "ERROR" : 1,
            "PRE" : 1,
            "ID" : 0,
            "SEQUENCE" : 0,
            "EOF" : 0,
            "BLANK" : 0,
            "MESSAGE" : ''
            }
        self.infile = open(self.infilename, "r")
        self.outgff = file("c:/temp/out.gff","wb")
        self.outseq = file("c:/temp/out.seq","wb")
        
        self.parserState["ERROR"] = 0
        
    def __del__(self):
        self.infile.close()
        self.outgff.close()
        self.outseq.close()


    def fastaToPseudoGFF(self,spacechar='N',spacecount=3):
        """ this method takes as input a FASTA file and makes a single GFF output
        file , with each sequence as a feature on a pseudo-reference - looking like this :
BTA10   chromosome      BCM_scaffold    1       84637   .       .       .       BCM_scaffold BTA10.1; way unoriented
BTA10   chromosome      BCM_scaffold    94638   191763  .       .       .       BCM_scaffold BTA10.2; way unoriented
BTA10   chromosome      BCM_scaffold    201764  248986  .       .       .       BCM_scaffold BTA10.3; way unoriented
BTA10   chromosome      BCM_scaffold    258987  304032  .       .       .       BCM_scaffold BTA10.4; way oriented
BTA10   chromosome      BCM_scaffold    314033  774774  .       .       .       BCM_scaffold BTA10.5; way oriented
BTA10   chromosome      BCM_scaffold    784775  821029  .       .       .       BCM_scaffold BTA10.6; way unoriented
"""
        template = "CHRUN\tpseudochromosome\tBCM_scaffold\t%s\t%s\t.\t.\t.\tBCM_UNscaffold %s\n"
        self.outseq.write(">CHRUN\n")
        fastalinesize = 10


        currentSequence = ''
        currentStart = 0
        currentStop = 0
        sequenceCount = 0
        currentLength = 0

        outpos = 0

        try:
            # read ahead until we get an id line
            record = self.infile.readline()

            while (re.search('^>',record) == None):
                record = self.infile.readline()

            if len(record) == 0:
                self.parserState['EOF'] = 1
                return

            # prepare first record and set states
            record = record.rstrip().lstrip()
            self.parserState['ID'] = 1
            self.parserState['PRE'] = 0

            # while we are not at the end and no error
            while self.parserState['ERROR'] == 0:
                # if current record is an id, and this is not the first one, then output
                # GFF and spacer sequence
                #print self.parserState
                #print sequenceCount
                if self.parserState['EOF'] == 1 or (self.parserState['ID'] == 1 and sequenceCount >0):

                    self.outgff.write(template%(currentStart,currentStop,currentSequence))   

                    (tidyseq,outpos) = tidyout(spacecount * spacechar,fastalinesize,outpos)
                    self.outseq.write(tidyseq)

                         
                        
                    #update current* and counts
                    currentStop += spacecount
                    currentStart = currentStop + 1
                    
                    currentSequence = record[1:]
                    currentLength = 0

                elif self.parserState['ID'] ==1:
                    currentSequence = record[1:]
                    currentStart = 1

                    
                            
                # else if a sequence record then update stats and output
                elif self.parserState['SEQUENCE'] == 1 :
                    # use the same fasta line size as the input when we come to output spacers
                    if sequenceCount == 0 and len(record) > 40:
                        fastalinesize = len(record)
                        
                    currentStop += len(record)
                    currentLength += len(record)

                    (tidyseq,outpos) = tidyout(record,fastalinesize,outpos)
                    self.outseq.write(tidyseq)
                    

                # exit if we are at end of file
                if self.parserState['EOF'] == 1:
                    break                    
        
                    
                # read another record and update state
                record = self.infile.readline()
                self.parserState.update({'SEQUENCE' : 0, 'ID' : 0, 'BLANK' : 0})

                    
                if len(record) == 0:
                    self.parserState['EOF'] = 1
                else:
                    record = record.lstrip().rstrip()

                    # if the line starts with >?, skip it
                    if re.search('^>\?',record) != None:
                        record = self.infile.readline()
                        record = record.lstrip().rstrip()

                    if len(record) == 0:
                        self.parserState['BLANK'] = 1
                    elif re.search('^>',record) != None:
                        self.parserState['ID'] = 1
                        sequenceCount += 1
                    else:
                        self.parserState['SEQUENCE'] = 1
                        

        finally:
            self.outgff.close()
            self.outseq.close()
            self.infile.close()

        print "done"


                    
    
class FindPatternParser (object):
    """ class for parsing FindPattern output. Example :
! FINDPATTERNS on @/usr/users/maqbooln/.seqlab-bifo3/findpatterns_ss1_77.list allowing 0 mismatches

! Using patterns from: /usr/users/maqbooln/.seqlab-bifo3/pattern_77.dat  December 20, 2005 09:46 ..


 mm6_dna_u000322.seq  ck: 5567  len: 11,001 ! mm6_dna_U000322 range=chr1:59978637-59989637 5'pad=0 3'pad=0 revComp=FALSE

Elf5-1                (A,C)GGAA(G,A)N(G,A)
                         (A)GGAA(G)N(G)
         2,458: GGGAA       AGGAAGGG       TTTTT

                         (A)GGAA(A)N(G)
         3,168: TAGGt       aggaaagg       taagg

                         (A)GGAA(A)N(G)
         3,579: AGAAA       AGGAAAGG       GAAGG

                         (C)GGAA(G)N(G)
         5,084: acctt       cggaagag       cagtc

                         (A)GGAA(A)N(A)
         6,170: aaCAA       AGGAAAGA       AAGAA

                         (C)GGAA(G)N(G)
         6,950: acctc       cggaagag       cagtc

                         (A)GGAA(A)N(G)
         8,188: ATGGA       AGGAAAAG       AATTT

                         (A)GGAA(A)N(G)
         8,307: TCTCC       AGGAAATG       ATATT

                         (A)GGAA(A)N(G)
         9,371: CCACC       AGGAAATG       TTGCt

                         (C)GGAA(A)N(G)
         9,813: AAACC       CGGAAATG       ATCTC


Elf5-1 /Rev           (T,C)N(T,C)TTCC(G,T)
                         (C)N(C)TTCC(G)
           808: gactg       ctcttccg       aaggt

                         (C)N(T)TTCC(T)
         1,742: TCAGA       CATTTCCT       AGAGC

                         (T)N(T)TTCC(G)
         2,183: ttttt       tttttccg       agaca

                         (T)N(C)TTCC(T)
         4,725: ACAAA       TCCTTCCT       CAAAA

         The parser iterates through each instance , returning a dictionary
         that contains query, patter, instance expression and instance position
"""
    def __init__(self,infilename):
        object.__init__(self)

        self.infilename = infilename

        self.parserState = {
            "ERROR" : 1,
            "PRE" : 1,
            "QUERY" : 0,
            "PATTERN" : 0,
            "INSTANCE" : 0,
            "POSITION" : 0,
            "BUFFER_FULL" : 0,
            "EOF" : 0,
            "" : None
            }
        self.infile = open(self.infilename, "r")
        self.parserState["ERROR"] = 0
        self.recordDict = {}        
        

        
    def __del__(self):
        self.infile.close()

    def parse(self):
        #record = self.infile.readline()
        self.parserState['PRE'] = 1
                
    def nextRecord(self):
        
        if [self.parserState[state] for state in ("ERROR", "EOF")] != [0,0]:
            return None
        while self.parserState['BUFFER_FULL'] == 0:
            record = self.infile.readline()

            #print "=====>%s"%record

            if len(record) == 0:
                self.parserState["EOF"] = 1
                return None            

            while (re.search('^\!',record) != None or len(record.strip()) == 0):
                #print "skipping " + record
                record = self.infile.readline()
                if len(record) == 0:
                    self.parserState["EOF"] = 1
                    return None                      

            rawRecord = record
            record = record.strip()

            if self.parserState['PRE'] == 1:
                if re.search('.*ck:.*len:',record) != None:
                    self.parserState.update( {
                        "PRE" : 0,
                        "QUERY" : 1,
                        })
                    self.recordDict['query'] = re.split("\!",record)[1]
                    self.recordDict['queryname'] = re.split("\s+",record)[0]
            elif self.parserState['QUERY'] == 1:
                patternTokens = re.split('\s+',record)
                self.recordDict['pattern_name'] = string.join(patternTokens[0 : -1],' ')
                self.recordDict['pattern_expression'] = patternTokens[-1]
                self.parserState.update( {
                        "QUERY" : 0,
                        "PATTERN" : 1,
                        })
            elif self.parserState['PATTERN'] == 1:
                self.recordDict['pattern_instance'] = record
                self.parserState.update( {
                        "PATTERN" : 0,
                        "INSTANCE" : 1
                        })
            elif self.parserState['INSTANCE'] == 1:
                positionTokens = re.split('\s+',record)
                self.recordDict['start'] = positionTokens[0].replace(":","")
                try: 
                    self.recordDict['start'] = int(self.recordDict['start'].replace(",",""))
                except ValueError, instance:
                    self.parserState['ERROR'] = 1
                    self.parserState['MESSAGE'] = str(instance) 
                    print instance
                    print record
                    print self.recordDict['start']
                    raise Exception
                
                self.recordDict['sequence'] = positionTokens[1:]
                self.recordDict['stop'] = self.recordDict['start'] + reduce(lambda x,y : x+len(y),self.recordDict['sequence'],0)
                self.recordDict['flankingstart'] = self.recordDict['start']
                self.recordDict['flankingstop'] = self.recordDict['stop']
                
                # adjust the start and stop so that the flanking sequence is not included in the calc
                self.recordDict['start'] = self.recordDict['flankingstart'] + len(self.recordDict['sequence'][0])
                self.recordDict['stop'] = self.recordDict['start'] + len(self.recordDict['sequence'][1])
                
                
                self.parserState.update( {
                        "INSTANCE" : 0,
                        "POSITION" : 1,
                        "BUFFER_FULL" : 1
                        })
            elif self.parserState['POSITION'] == 1:
                if re.search('^\w',rawRecord):
                    # we encountered a new pattern - these start on the first line
                    patternTokens = re.split('\s+',record)
                    self.recordDict.update( {
                        'pattern_name' :  string.join(patternTokens[0 : -1],' '),
                        'pattern_expression' :  patternTokens[-1],
                        'pattern_instance' : None,
                        'start' : None,
                        'sequence' : None })
                    self.parserState.update( {
                        "PATTERN" : 1,
                        "POSITION" : 0,                    
                        })
                elif re.search('.*ck:.*len:',record) != None:
                    # we encountered a new query
                    self.recordDict.update( {
                        'query' : re.split("\!",record)[1],
                        'pattern_name' :  None,
                        'pattern_expression' :  None,
                        'pattern_instance' : None,
                        'start' : None,
                        'sequence' : None })
                    self.parserState.update( {
                        "QUERY" : 1,
                        "POSITION" : 0,                    
                        })
                else:
                    # this must be another instance of a pattern
                    self.recordDict.update( {
                        'pattern_instance' : record,
                        'start' : None,
                        'sequence' : None })
                    self.parserState.update( {
                        "INSTANCE" : 1,
                        "POSITION" : 0                   
                        })
            # each parse type
        # until have read a position

        self.parserState.update( {
            "BUFFER_FULL" : 0
        })
        
                    
        return self.recordDict            
                    
                    
                    
                
    
class GeneralGFFParser ( object ):
    """ 
    class for parsing GFF files - doesn't do much yet, and not tested on very
    many different GFF files. Args :
    GFFType : internal typeid used to ditinguish types
    parseRules : a dictionary of regexps keyed by GFF fieldname. Mostly needed to parse the accession 
    """

    def __init__(self,infilename,GFFtype=1,parseRules={"Accession" : "^Match\s+\w+_(\w+);"}):
        object.__init__(self)

        self.infilename = infilename

        self.parserState = {
            "ERROR" : 1,
            "PRE" : 1,
            "BODY" : 0,
            "EOF" : 0,
            "MESSAGE" : '',
            "RECORD_TYPE" : None
            }
        self.infile = open(self.infilename, "r")
        self.parserState["ERROR"] = 0
        if GFFtype == 1:
            self.fieldNames = ['Reference','GFFFileType','GFFRecordType','FeatureStart','FeatureStop','Score','Strand','Unused1','Description']
        else:
            self.fieldNames = ['Reference','GFFFileType','GFFRecordType','FeatureStart','FeatureStop','Score','Strand','Unused1','Description']

        self.parseRules = parseRules
    
        

        
    def __del__(self):
        self.infile.close()

    def parse(self):
        #record = self.infile.readline()
        self.parserState['BODY'] = 1
        self.parserState['ERROR'] = 0        
                
    def nextRecord(self):
        if [self.parserState[state] for state in ("BODY" , "ERROR", "EOF")] != [1,0,0]:
            return

        record = self.infile.readline()

        self.rawRecord = record
        record = record.strip()
        #record = record.replace('Error','')

        if len(record) == 0:
            self.parserState["EOF"] = 1
            return None

        while len(re.split('\t',record)) != len(self.fieldNames) : 
            print "skipping " + record
            record = self.infile.readline()
            if len(record) == 0:
                self.parserState["EOF"] = 1
                return None

            
        #self.rawRecord = record
        #record = record.strip()
        #record = record.replace('Error','')

        if len(record) == 0:
            self.parserState["EOF"] = 1
            return None

        #debugPrint("==1=>" + record)
        fields = re.split('\t',record)
        fields = [item.replace('"','') for item in fields]
        #print "length = %s"%len(fields)

        fieldDict = dict(zip(self.fieldNames,fields))
        #debugPrint("==2=>" + str(fieldDict))
        fieldDict['Accession'] = re.search(self.parseRules["Accession"],fieldDict['Description'])
        if fieldDict['Accession'] != None:
            fieldDict['Accession'] = fieldDict['Accession'].groups()[0]

        # try to type the start and stop positions
        try:
            fieldDict['FeatureStart'] = int(fieldDict['FeatureStart'])
            fieldDict['FeatureStop'] = int(fieldDict['FeatureStop'])
        except Exception:
            None



        self.parserState['RECORD_TYPE'] = fieldDict['GFFRecordType']

        #debugPrint("==3==>" + str(fieldDict))
        
        return fieldDict


class GFFFileParser (GeneralGFFParser):
    def __init__(self,infilename):
        GeneralGFFParser.__init__(self,infilename)



def main():
    #makePatternGFF()
    #makeChrUn()
    #summariseCS18Mapping()
    #makeOvineBACSSRs()
    #makeCS18MappingGFF()
    #print transformGappedCoords(2605834, 5000, 10000, [2605833,4368633])
    #if len(sys.argv) < 2:
    #    chrun = 'ChrUN'
    #else:
    #    chrun = sys.argv[1]
        
    #patchChrUnMapping(file("c:\\temp\\pseudoChrUn.gff",'r'),infile=sys.stdin,chrunname=chrun)
    #makeChrUnMapping(file("c:\\temp\\pseudoChrUn.gff",'r'),infile=sys.stdin,chrunname=chrun)
    #unmakeChrUnMapping(file("c:\\temp\\pseudoChrUn.gff",'r'),infile=open("c:\\working\\russell\\test.gff"))
    #unmakeChrUnMapping(file("c:\\temp\\pseudoChrUn.gff",'r'),infile=sys.stdin,chrunname="CHRUN")
    #summariseCS34Mapping()
    #makeGBrowseDisplayCalls("c:/working/possum/CS44.gff","c:/working/possum/addGBrowseCalls.psql")
    loadSequenceFeatures(None,"c:/working/isgcdata/test.gff")
        
    


#
# parse a FindPattern output file and output a GFF file
#
def makePatternGFF():
    #outGFFtemplate = "mm6_chr1	findpattern	Elf5-1	59981100 59981107 . . 	.	FindPattern (A,C)GGAA(G,A)N(G,A);motif=AGGAAGGG"
  
    outGFFtemplate = "mm6_%s\tfindpattern\t%s\t%d\t%d\t.\t.\t.\tFindPattern %s;%s:%s;motif=%s;querystart=%d;context=%s\n"
    
    parser = FindPatternParser("c:/working/findpatterns_Elf5.find");
    parser.parse()

    record = parser.nextRecord()

    outgff = file("c:/working/out.gff","wb")
    try:
        while record != None:
            #print record
            # parse the chromosome and position from the query sequence
            # which looks like
            #mm6_dna_U001802 range=chr2:59457444-59468444 5'pad=0 3'pad=0 revComp=FALSE
            #print record
            queryTokens = re.split('range=',record['query'])
            #print queryTokens
            (musChr,musPos) = re.split(':',queryTokens[1])[0:2]
            musPos = re.split('\s+',musPos)[0]
            (musStart,musStop) = re.split('-',musPos)[0:2]
            (musStart,musStop) = (int(musStart),int(musStop))

            outgff.write(outGFFtemplate%(musChr,record['pattern_name'],record['start'] + musStart - 1, \
                        record['stop'] + musStart - 1, record['queryname'],record['pattern_expression'],record['pattern_instance'],\
                        record['sequence'][1],record['start'],reduce(lambda x,y:x+':'+y,record['sequence'])))
        
            record = parser.nextRecord()
    finally:
        outgff.close()



# method to create a GFF file that summarises the CS18mapping.
#
# The input file is a CSV file with the following format :
# accession,reciprocalgene,genetophit,BTChr,BTMap,
# Track,exonCount,exon<500,exon500-1000,exon>500,
# intron<500,intron500-1000,intron1000-5000,intron>5000,SNPDetails
#
#accession,reciprocalgene,genetophit,BTChr,BTMap,Track,exonCount,exon<500,exon500-1000,exon>500,intron<500,intron500-1000,intron1000-5000,intron>5000,SNPDetails,,,,,,,,,
#CONTIGNAME, RECIPROCALGENE_NAME, REFSEQGENE,,,,,,,,,,,,STATISTICS,,,,,,,,,
#160903CS18011370FFFFE, , ,,,,,,,,,,,,,,,,,,,,,
#160903CS18011435FFFFF, , ,Chr20,15780371-15780505,mRNA 160903CS18011435FFFFF_p1,1,1,,,,,,,,,,,,,,,,
#160903CS18039517FFFFE, , GAPVD1,Chr7,9360811-9377848,mRNA 160903CS18039517FFFFE_p1,3,3,,,,,1,1,,,,,,,,,,
#160903CS1802182500001, WDR21, WDR21A,Chr10,59475172-59489257,mRNA 160903CS1802182500001_p1,12,12,,,3,4,4,,ConsensusPos=357,SNP=a/g,Distr=a 0.60:g 0.40:c 0.00:t 0.00,Depth=5,TrueDepth=5,ConsensusLength=1700,ContigLength=1700,SNPCount=2,BP/SNP=0,GT200BP/SNP=0
#160903CS1802182500001, WDR21, WDR21A,Chr10,59475172-59489257,mRNA 160903CS1802182500001_p1,12,12,,,3,4,4,,ConsensusPos=649,SNP=g/t,Distr=a 0.00:g 0.50:c 0.00:t 0.50,Depth=4,TrueDepth=4,ConsensusLength=1700,ContigLength=1700,SNPCount=2,BP/SNP=0,GT200BP/SNP=0

#
#
# the output GFF file has the following structure :
#BTA1	GMAP_CS18	exon500	    4050041	4050579	.	.	.	accession 160903CS1801044400001;
#BTA1	GMAP_CS18	intron500   4060176	4060717	.	.	.	accession 160903CS1801044400001;
#BTA1	GMAP_CS18	SNP	    4060176	4060717	.	.	.	accession 160903CS1801044400002; Note 
#

def makeCS18MappingGFF():
    reader = csv.reader(open("M:/projects/SNP/ovine/cs18gmapAllsummary.csv", "rb"))
    #reader = csv.reader(open("M:/projects/SNP/ovine/test8.csv", "rb"))    
    outgff = file("c:/temp/out.gff","wb")
    lastAccession = ''
    
    
    rowCount = 1
    fieldNames = []
    for row in reader:
        if rowCount == 1:
            fieldNames = row
        else:
            fieldDict = dict(zip(fieldNames,row))
            if 'SNPDetails' not in fieldDict:
                fieldDict['SNPDetails']= ''
            if 'exon500-1000' not in fieldDict:
                fieldDict['exon500-1000']= ''
            if 'exon>1000' not in fieldDict:
                fieldDict['exon>1000']= ''
            if 'intron500-1000' not in fieldDict:
                fieldDict['intron500-1000']= ''
            if 'intron1000-5000' not in fieldDict:
                fieldDict['intron1000-5000']= ''
            if 'BTMap' not in fieldDict:
                fieldDict['BTMap']= ''                   
                
                
            fieldDict['snpstring'] = string.join(row[14:],',')
            #print fieldDict
            if len(re.split('-',fieldDict['BTMap']) ) == 2:
                fieldDict['start'] = re.split('-',fieldDict['BTMap'])[0]
                fieldDict['stop'] = re.split('-',fieldDict['BTMap'])[1]
                fieldDict['exon500'] = 0
                if re.search("\d+",fieldDict['exon500-1000']) != None  or re.search('\d+',fieldDict['exon>1000']) != None :
                    fieldDict['exon500'] = 1
                fieldDict['intron500'] = 0
                if re.search("\d+",fieldDict['intron500-1000']) != None or re.search("\d+",fieldDict['intron1000-5000']) > 0 :
                    fieldDict['intron500'] = 1
                if re.search("Consensus",fieldDict['SNPDetails']) != None:
                    #print "***%s**%s"%(fieldDict['accession'],fieldDict['SNPDetails'])
                    fieldDict['SNPNote'] = 'Note %s'%fieldDict['snpstring']
                else:
                    fieldDict['SNPNote'] = ''

                fieldDict['BTChr'] = fieldDict['BTChr'].replace('Chr','BTA')

                #output GFF
                if fieldDict['accession'] != lastAccession:
                    if fieldDict['exon500']> 0 :
                        outgff.write("%(BTChr)s\tGMAP_CS18\texon500\t%(start)s\t%(stop)s\t.\t.\t.\taccession %(accession)s\n"%fieldDict)
                    if fieldDict['intron500']> 0 :
                        outgff.write("%(BTChr)s\tGMAP_CS18\tintron500\t%(start)s\t%(stop)s\t.\t.\t.\taccession %(accession)s\n"%fieldDict)
                        
                if len(fieldDict['SNPNote'])> 0 :
                    outgff.write("%(BTChr)s\tGMAP_CS18\tSNP\t%(start)s\t%(stop)s\t.\t.\t.\taccession %(accession)s ; %(SNPNote)s\n"%fieldDict)                    
                    
            lastAccession = fieldDict['accession']
        rowCount += 1
                

    outgff.close()

        


#method to make a GFF file containing canonical Ovine BAC SSRs.
#
# Input is a GFF of sputnik SSR, and another of Tandyman SSR, as follows :
#
# DU532724	sputnik	spk	615	630	16	.	.	Accession DU532724-1; Note Motif AAAT, Length 16; Bova2 DU532724
# DU532701	sputnik	spk	422	442	21	.	.	Accession DU532701-1; Note Motif AGC, Length 21; Bova2 DU532701
#
# DU532634	tandy	tandy	181	229	24.5	.	.	Accession DU532634-1; Note Motif TA, Length 48; Bova2 DU532634
# DU532628	tandy	tandy	508	545	19	.	.	Accession DU532628-1; Note Motif AT, Length 37; Bova2 DU532628
#
# output is a merged GFF as follows
#
# DU532724      sputnik_tandy   ssr     615     630     16   .   .   Accession OAM00100001; Note putative SSR marker polymorphic status unknown ; Sputnik Motif AT, Position 615-630  ; Tandy note

#
#the algorithm is as follows :
#
# 1. Read all the sputnik SSR's into a dictionary, assigning OAM names as we
#    go.
#    The key of the dictionary will be the Bac accession name. The value will
#    be a list of dictionaries, each like : 
#    {'accession' : 'OAM001000001' , 'start' : 34, 'stop' : 40 , 'motif' : 'AT', 'tandynote', ''}  
def makeOvineBACSSRs():
    sputnikparser = GFFFileParser("M:\\projects\\sgp\\datacapture\\sheep_bacends.sputnik.gff")
    tandyparser = GFFFileParser("M:\\projects\\sgp\\datacapture\\sheep_bacends.tandyman.gff")
    outGFFtemplate = "%s\tsputnik_tandy\tssr\t%s\t%s\t%s\t.\t.\tAccession %s; Note putative SSR marker polymorphic status unknown Length %s  Score %s ; Sputnik Motif %s, Position %s-%s , Length %s; %s\n"
    tandyGFFtemplate = "%s\tsputnik_tandy\tssr\t%s\t%s\t%s\t.\t.\tAccession %s; Note putative SSR marker polymorphic status unknown Length %s Score %s ; Tandyman Motif %s, Position %s-%s , Length %s ; \n"
    nameTemplate = 'OAM%07d'  #  start with OAM1000001 and onwards

    sputnikDict = {}
    tandyDict = {}
    markerNumber = 1000001

    # read ahead
    sputnikparser.parse()
    gffDict =  sputnikparser.nextRecord()

    #print parser.parserState['MESSAGE']
    #{'Description': ['Accession DU532724-1', 'Note Motif AAAT, Length 16', 'Bova2 DU532724'],
    #'Reference': 'DU532724', 'GFFFileType': 'sputnik', 'Accession': 'DU532724', 'Score': '16',
    #'Unused1': '.', 'FeatureStart': '615', 'FeatureStop': '630', 'GFFRecordType': 'spk', 'Strand': '.'}

    # loop through reading the file
    while sputnikparser.parserState["EOF"] == 0:
        markerName = nameTemplate%markerNumber
        markerNumber += 1
        attributeDict= {
            'accession' : markerName,
            'start' : int(gffDict['FeatureStart']),
            'stop' : int(gffDict['FeatureStop']),
            'motif' : re.split('\s+',re.split(',',gffDict['Description'][1])[0])[2],
            'score' : gffDict['Score'],
            'tandynote' : ''
        }
        #print attributeDict
        if gffDict['Accession'] in sputnikDict:
            ssrList = sputnikDict[ gffDict['Accession'] ]
            ssrList.append(attributeDict)
            sputnikDict[ gffDict['Accession'] ] = ssrList
        else:
            sputnikDict[ gffDict['Accession'] ] = [ attributeDict ]
            
        gffDict =  sputnikparser.nextRecord()

        #if markerNumber > 1000502:
        #    break

    if sputnikparser.parserState["ERROR"] > 0:
        raise brdfException, sputnikparser.parserState['MESSAGE']


        
    # list some sputnik stats 

    print "**** Sputnik Stats *****"
    print "Distinct Number of BAC end with one or more SSR : %s"%len(sputnikDict)
    SSRFreq = [len(item) for item in sputnikDict.values()]
    freqbins = range(1,max(SSRFreq)+1)
    freqs = [ len([item for item in SSRFreq if item == freq]) for freq in freqbins ]
    freqDistribution = dict(zip(freqbins, freqs))
    print "Frequency Distribution of SSR's per BAC end"
    for freqbin in freqDistribution.keys():
        print "%s : %s"%(freqbin,freqDistribution[freqbin])
    #print freqDistribution

    # list accessions with multiple SSR
    for i in range(2,1+max(SSRFreq)):
        print "=======================Accessions with %s SSR (sputnik) ======================="%i
        for accession in sputnikDict.keys():
            if len(sputnikDict[accession]) == i:
                print accession
                #print sputnikDict[accession]


    # now read the tandy file - we compile the same stats as for the sputnik scan
    tandyparser.parse()
    gffDict =  tandyparser.nextRecord()

    #print parser.parserState['MESSAGE']
    #{'Description': ['Accession DU532724-1', 'Note Motif AAAT, Length 16', 'Bova2 DU532724'],
    #'Reference': 'DU532724', 'GFFFileType': 'sputnik', 'Accession': 'DU532724', 'Score': '16',
    #'Unused1': '.', 'FeatureStart': '615', 'FeatureStop': '630', 'GFFRecordType': 'spk', 'Strand': '.'}

    # loop through reading the file
    while tandyparser.parserState["EOF"] == 0:
        markerName = nameTemplate%markerNumber
        markerNumber += 1
        attributeDict= {
            'accession' : markerName,
            'start' : int(gffDict['FeatureStart']),
            'stop' : int(gffDict['FeatureStop']),
            'motif' : re.split('\s+',re.split(',',gffDict['Description'][1])[0])[2],
            'score' : gffDict['Score'],
            'sputnik': 0
        }
        #print attributeDict
        if gffDict['Accession'] in tandyDict:
            ssrList = tandyDict[ gffDict['Accession'] ]
            ssrList.append(attributeDict)
            tandyDict[ gffDict['Accession'] ] = ssrList
        else:
            tandyDict[ gffDict['Accession'] ] = [ attributeDict ]
            
        gffDict =  tandyparser.nextRecord()

        #if markerNumber > 1000502:
        #    break

    if tandyparser.parserState["ERROR"] > 0:
        raise brdfException, tandyparser.parserState['MESSAGE']

    # list some tandy stats 

    print "**** Tandy Stats *****"
    print "Distinct Number of BAC end with one or more SSR : %s"%len(tandyDict)
    SSRFreq = [len(item) for item in tandyDict.values()]
    freqbins = range(1,max(SSRFreq)+1)
    freqs = [ len([item for item in SSRFreq if item == freq]) for freq in freqbins ]
    freqDistribution = dict(zip(freqbins, freqs))
    print "Frequency Distribution of SSR's per BAC end"
    for freqbin in freqDistribution.keys():
        print "%s : %s"%(freqbin,freqDistribution[freqbin])
    #print freqDistribution

    # list accessions with multiple tandy SSR
    for i in range(2,1+max(SSRFreq)):
        print "=======================Accessions with %s SSR (tandy) ======================="%i
        for accession in tandyDict.keys():
            if len(tandyDict[accession]) == i:
                print accession
                #print sputnikDict[accession]

    # now merge the sputnik and tandy SSR files
    print "Merging Sputnik and Tandy"
    for bac in sputnikDict.keys():
        if bac in tandyDict:
            for sputnikssr in sputnikDict[bac]:
                if len(sputnikssr['tandynote']) < 2:
                    for tandyssr in tandyDict[bac]:
                        if (sputnikssr['start'] <= tandyssr['start'] <= sputnikssr['stop'] ) or \
                           (sputnikssr['start'] <= tandyssr['stop'] <= sputnikssr['stop'] ):
                            sputnikssr['tandynote'] = 'Tandyman Motif %s, Position=%s-%s, Length = %s, Score=%s'%(tandyssr['motif'],tandyssr['start'],tandyssr['stop'],1+tandyssr['stop']- tandyssr['start'], tandyssr['score'])
                            tandyssr['sputnik'] = 1                            

    # output the merged GFF
    outgff = file("c:/temp/out.gff","wb")
    for bac in sputnikDict.keys():
        for ssr in sputnikDict[bac]:
            outgff.write(outGFFtemplate%(bac,ssr['start'],ssr['stop'],ssr['score'],\
                                              ssr['accession'],1+ssr['stop']-ssr['start'],ssr['score'],ssr['motif'],ssr['start'],ssr['stop'],1+ssr['stop']-ssr['start'],ssr['tandynote']))

    # output any tandy SSR not already output
    for bac in tandyDict:
        for ssr in tandyDict[bac]:
            if ssr['sputnik'] == 0:
                outgff.write(tandyGFFtemplate%(bac,ssr['start'],ssr['stop'],ssr['score'],\
                                              ssr['accession'],1+ssr['stop']-ssr['start'],ssr['score'],ssr['motif'],ssr['start'],ssr['stop'],1+ssr['stop']-ssr['start']))

    outgff.close()
                
    
    #twoSSR = len([item for item in sputnikDict.values() if len(item) > 1])
    #print "%s BACs have > 1 SSR"%multiSSR
        
    

# method to make a ChrUn gff file
def makeChrUn():
    factory = GeneralGFFFactory("c:/temp/ChrUn.fa")
    factory.fastaToPseudoGFF('N',5000)
    #3factory = GeneralGFFFactory("c:/temp/test.seq")
    #factory.fastaToPseudoGFF('N',5)

    #colpos = 0
    #allstr = ''
    #for i in range(1,3):
    #    (mystr,colpos) = tidyout('abcdefgasdakjsdkahdajhdekadshkahd',5,colpos)
    #    allstr += mystr
    #
    #print allstr
        
    

def summariseCS18Mapping():
    # script to summarise a GFF file according to a spec from John McEwan, and merge
    # with a CSV file containing annotation.
    # This was as input to a SNP chip design , where they want to design primer pairs
    # to amplify either suitable length exons or introns
    # The basic idea is to categorise by length of exon and intron, using 
    # only the best mapping.

    exonLowerLengthStats = {}
    exonMidLengthStats = {}
    exonUpperLengthStats = {}
    
    exonLowerLength = 500   
    exonUpperLength = 1000


    intronLowerLengthStats = {}
    intronMidLength1Stats = {}
    intronMidLength2Stats = {}
    intronUpperLengthStats = {}

    intronLowerLength = 500
    intronMidLength = 1000
    intronUpperLength = 5000
    
    myExons=[]
    allAccessions = {}    

    TEST=False
    
    if TEST:
        parser = GFFFileParser("M:\\projects\\snp\\ovine\\test7.gff")
    else:
        #parser = GFFFileParser("M:\\projects\\snp\\ovine\GMAP_CS28.gff")
        #parser = GFFFileParser("M:\\projects\\snp\\ovine\\GMAP_CS18.gff")
        #parser = GFFFileParser("M:\\projects\\snp\\ovine\\ChrUn_cs18.gff")
        parser = GFFFileParser("M:\\projects\\snp\\ovine\\combinedplusUn.gff")        
        #parser = GFFFileParser("M:\\projects\\snp\\ovine\\test1.gff")
        #parser = GFFFileParser("M:\\projects\\snp\\ovine\\test2.gff")
        #parser = GFFFileParser("M:\\projects\\snp\\ovine\\test3.gff")        

    # set up the first mRNA record
    parser.parse()
    gffDict =  parser.nextRecord()
    
    currentAccessionmRNARecord = gffDict
    currentAccession = str(gffDict['Accession'])
    currentReference = str(gffDict['Reference'])
    currentScore = gffDict['Score']
    #allAccessions[currentAccession] = (currentAccessionmRNARecord['Score'],currentAccessionmRNARecord['Description'])

    # get the exon
    parser.parse()
    gffDict =  parser.nextRecord()

    # loop through reading the file
    while parser.parserState["ERROR"] == 0:    
        #debugPrint("gff file : %s"%gffDict)
        debugPrint("parser state %s"%parser.parserState)

        doSummary = False
        doReSummary = False

        # decide whether we need to summarise the alignments read up to this point
        if parser.parserState["EOF"] == 1 or parser.parserState["RECORD_TYPE"] == "mRNA":

            debugPrint("--->" + currentAccession)
            if currentAccession in allAccessions :
                if float(currentAccessionmRNARecord['Score']) > float(allAccessions[currentAccession][0]):
                    doReSummary = True

            else:
                doSummary = True

            if not (doSummary or doReSummary ) and parser.parserState["EOF"] == 0:
                currentAccessionmRNARecord = gffDict
                currentAccession = str(gffDict['Accession'])
                currentReference = str(gffDict['Reference'])
                currentScore = gffDict['Score']
                    
                    
        elif parser.parserState["RECORD_TYPE"] == "exon":
            debugPrint("********>" + str(gffDict))
            myExons.append( (int(gffDict['FeatureStart']), int(gffDict['FeatureStop'])) )
        else :
            raise brdfException, " error - unknown GFF Record type " + gffDict['GFFRecordType']
                

        # if we need to summarise the results to this point then do so          
        if doSummary or doReSummary:
            if doReSummary:

                # remove the existing entries in each of the stats lists
                for mydict in (exonUpperLengthStats, exonMidLengthStats, exonLowerLengthStats, \
                    intronUpperLengthStats, intronMidLength1Stats, intronMidLength2Stats, intronLowerLengthStats ):
                    if currentAccession in mydict :
                        del mydict[currentAccession]
                        
            allAccessions[currentAccession] = (currentScore,currentReference,currentAccessionmRNARecord['FeatureStart'],\
                                            currentAccessionmRNARecord['FeatureStop'],currentAccessionmRNARecord['Description'], len(myExons))

            # if we have some exons summarise
            if len(myExons) > 0:
                longExons = [exon  for exon in myExons if abs(exon[1] - exon[0]) > exonUpperLength]
                shortExons = [exon  for exon in myExons if abs(exon[1] - exon[0]) < exonLowerLength]
                midExons = [exon  for exon in myExons if abs(exon[1] - exon[0]) >= exonLowerLength and abs(exon[1] - exon[0]) <= exonUpperLength]
            
                if len(longExons) > 0:
                    debugPrint("adding %s to longExons"%currentAccession)
                    exonUpperLengthStats[currentAccession] = (len(longExons),currentScore,currentReference,currentAccessionmRNARecord['FeatureStart'],\
                                                              currentAccessionmRNARecord['FeatureStop'],currentAccessionmRNARecord['Description'])

                if len(shortExons) > 0 :
                    debugPrint("adding %s to shortExons"%currentAccession)                    
                    exonLowerLengthStats[currentAccession] = (len(shortExons),currentScore,currentReference,currentAccessionmRNARecord['FeatureStart'],\
                                                              currentAccessionmRNARecord['FeatureStop'],currentAccessionmRNARecord['Description'])

                if len(midExons) > 0 :
                    debugPrint("adding %s to midExons"%currentAccession)                                        
                    exonMidLengthStats[currentAccession] = (len(midExons),currentScore,currentReference,currentAccessionmRNARecord['FeatureStart'],\
                                                              currentAccessionmRNARecord['FeatureStop'],currentAccessionmRNARecord['Description'])

                # if we have more than one exon then summarise introns
                if len(myExons) > 1:
                    myExons.sort()
                    longIntrons = [myExons[i] for i in range(1,len(myExons)) if myExons[i][0] - myExons[i-1][1] >= intronUpperLength]
                    shortIntrons = [myExons[i] for i in range(1,len(myExons)) if myExons[i][0] - myExons[i-1][1] < intronLowerLength]
                    midIntrons1 = [myExons[i] for i in range(1,len(myExons)) if myExons[i][0] - myExons[i-1][1] >= intronLowerLength and
                                  myExons[i][0] - myExons[i-1][1] < intronMidLength]
                    midIntrons2 = [myExons[i] for i in range(1,len(myExons)) if myExons[i][0] - myExons[i-1][1] >= intronMidLength and
                                  myExons[i][0] - myExons[i-1][1] < intronUpperLength]
                    
                    if len(longIntrons) > 0:
                        intronUpperLengthStats[currentAccession] = (len(longIntrons),currentScore,currentReference,currentAccessionmRNARecord['FeatureStart'],\
                                                              currentAccessionmRNARecord['FeatureStop'],currentAccessionmRNARecord['Description'])
                        
                    if len(shortIntrons) > 0 :                        
                        intronLowerLengthStats[currentAccession] = (len(shortIntrons),currentScore,currentReference,currentAccessionmRNARecord['FeatureStart'],\
                                                              currentAccessionmRNARecord['FeatureStop'],currentAccessionmRNARecord['Description'])

                    if len(midIntrons1) > 0 :
                        intronMidLength1Stats[currentAccession] = (len(midIntrons1),currentScore,currentReference,currentAccessionmRNARecord['FeatureStart'],\
                                                              currentAccessionmRNARecord['FeatureStop'],currentAccessionmRNARecord['Description'])
                    if len(midIntrons2) > 0 :
                        intronMidLength2Stats[currentAccession] = (len(midIntrons2),currentScore,currentReference,currentAccessionmRNARecord['FeatureStart'],\
                                                              currentAccessionmRNARecord['FeatureStop'],currentAccessionmRNARecord['Description'])                        




            # if did a summary because we are at the end - break, else reset current accession and ref to the
            # mRNA record just read
            if parser.parserState["EOF"] == 1:
                break
            else:
                # reset the current mRNA record to the one just read
                currentAccessionmRNARecord = gffDict
                currentAccession = str(gffDict['Accession'])
                currentReference = str(gffDict['Reference'])
                currentScore = gffDict['Score']


        # if the current parserState is mRNA then we have summarised if required so can reset myExons
        if parser.parserState['RECORD_TYPE'] == "mRNA":
           myExons = []
           
        if parser.parserState["EOF"] == 1:
            break


        gffDict =  parser.nextRecord()

    if parser.parserState['ERROR'] != 0:
        print "error : " + parser.parserState['MESSAGE']
    else:
        if DEBUG:
            print "All Accessions : "
            print allAccessions
            print "exon upper : "
            print exonUpperLengthStats
            print "exon lower : "
            print exonLowerLengthStats
            print "exon mid : "
            print exonMidLengthStats

            print "intron upper : "
            print intronUpperLengthStats
            print "intron lower : "
            print intronLowerLengthStats
            print "intron mid1 : "
            print intronMidLength1Stats
            print "intron mid2 : "
            print intronMidLength2Stats

            for accession in allAccessions.keys():
                print accession
            



        #print "number of accessions : %s, number of mappings %s"% \
        #    (len(allAccessions),reduce(lambda x,y:x+y,allAccessions.values(),0))
        #print exonUpperLengthStats
        print "number of accessions : %s"%(len(allAccessions))
        print "number of accessions with exons > %s = %s, total exon count = %s: "%\
              (exonUpperLength,len(exonUpperLengthStats),reduce(lambda x,y:x+y[0],exonUpperLengthStats.values(),0))
        print "number of accessions with exons < %s = %s, total exon count = %s: "%\
              (exonLowerLength,len(exonLowerLengthStats),reduce(lambda x,y:x+y[0],exonLowerLengthStats.values(),0))
        print "number of accessions with exons between %s and %s = %s, total exon count = %s: "%\
              (exonLowerLength,exonUpperLength,len(exonMidLengthStats),reduce(lambda x,y:x+y[0],exonMidLengthStats.values(),0))

        print "number of accessions with introns > %s = %s, total intron count = %s: "%\
              (intronUpperLength,len(intronUpperLengthStats),reduce(lambda x,y:x+y[0],intronUpperLengthStats.values(),0))
        print "number of accessions with introns < %s = %s, total intron count = %s: "%\
              (intronLowerLength,len(intronLowerLengthStats),reduce(lambda x,y:x+y[0],intronLowerLengthStats.values(),0))
        print "number of accessions with introns between %s and %s = %s, total intron count = %s: "%\
              (intronLowerLength,intronMidLength,len(intronMidLength1Stats),reduce(lambda x,y:x+y[0],intronMidLength1Stats.values(),0))
        print "number of accessions with introns between %s and %s = %s, total intron count = %s: "%\
              (intronMidLength,intronUpperLength,len(intronMidLength2Stats),reduce(lambda x,y:x+y[0],intronMidLength2Stats.values(),0))
          

        # now we read and write the annotation CSV file, merging with the intron and exon
        # summaries obtained above
        outCSV = file("c:/temp/out5.csv","wb")
        

        reader = csv.reader(open("m:/projects/snp/ovine/cs18annotation.csv", "rb"))        

        dictFields = ['accession' ,'reciprocalgene' ,'genetophit' ,\
                           'BTChr' ,'BTMap' ,'Track' , 'exonCount' ,'exon<%s'%exonLowerLength,\
                           'exon%s-%s'%(exonLowerLength,exonUpperLength) , 'exon>%s'%exonUpperLength ,'intron<%s'%intronLowerLength ,\
                            'intron%s-%s'%(intronLowerLength,intronMidLength),'intron%s-%s'%(intronMidLength,intronUpperLength) ,\
                              'intron>%s'%intronUpperLength,\
                           'SNPDetails' ]

        outDict = dict(zip(dictFields,len(dictFields)*("",)))

        outCSVRecord = reduce(lambda x,y:str(x) + "," + str(y),dictFields,"")
        outCSV.write(outCSVRecord+"\n")
        
        for row in reader:
            if len(row) >= 7:
                #debugPrint(row)
                outDict = dict(zip(dictFields,len(dictFields)*("",)))   

                outDict['accession'] = string.upper(row[0])

                # remove the version numbers, as the GFF mapping did so
                outDict['accession'] = re.sub('\.\d+','',outDict['accession'])
                
                outDict['reciprocalgene'] = " "+row[4]
                outDict['genetophit'] = " "+row[8]
                if  outDict['accession'] in allAccessions:
                    #print "---->" + str(allAccessions[outDict['accession']])
                    outDict['BTChr'] = allAccessions[outDict['accession']][1]
                    #print allAccessions[outDict['accession']][2]
                    outDict['BTMap'] = "%s-%s"%(allAccessions[outDict['accession']][2], allAccessions[outDict['accession']][3])
                    #print outDict['BTMap']
                    outDict['Track'] = allAccessions[outDict['accession']][4][0]
                    outDict['exonCount'] = allAccessions[outDict['accession']][5]
                    if outDict['accession'] in exonLowerLengthStats:
                        outDict['exon<%s'%exonLowerLength] = exonLowerLengthStats[outDict['accession']][0]
                    if outDict['accession'] in exonMidLengthStats:
                        outDict['exon%s-%s'%(exonLowerLength,exonUpperLength)] = exonMidLengthStats[outDict['accession']][0]
                    if outDict['accession'] in exonUpperLengthStats:
                        outDict['exon>%s'%exonUpperLength] = exonUpperLengthStats[outDict['accession']][0]
                    if outDict['accession'] in intronLowerLengthStats:
                        outDict['intron<%s'%intronLowerLength] = intronLowerLengthStats[outDict['accession']][0]
                    if outDict['accession'] in intronMidLength1Stats:
                        outDict['intron%s-%s'%(intronLowerLength,intronMidLength)] = intronMidLength1Stats[outDict['accession']][0]
                    if outDict['accession'] in intronMidLength2Stats:
                        outDict['intron%s-%s'%(intronMidLength,intronUpperLength)] = intronMidLength2Stats[outDict['accession']][0]
                    if outDict['accession'] in intronUpperLengthStats:
                        outDict['intron>%s'%intronUpperLength] = intronUpperLengthStats[outDict['accession']][0]
                outDict['SNPDetails'] = row[3]

                outCSVRecord = reduce(lambda x,y:str(x) + "," + str(y),[outDict[key] for key in dictFields],"")
                outCSV.write(outCSVRecord+"\n")
                        
 
        #print row
        #reader.close()
        outCSV.close()



def summariseCS34Mapping():
    # script to summarise a GFF file of GMAP mappings, to output the
    # best map position for each contig
    myExons=[]
    allAccessions = {}        

    TEST=False
    DEBUG=False
    
    if TEST:
        parser = GFFFileParser("c:\\working\\orla\\test.gff")
    else:
        parser = GFFFileParser("c:\\working\\orla\\Btau_3.1_CS34.gff")        

    # set up the first mRNA record
    parser.parse()
    gffDict =  parser.nextRecord()
    
    currentAccessionmRNARecord = gffDict
    currentAccession = str(gffDict['Accession'])
    currentReference = str(gffDict['Reference'])
    currentScore = gffDict['Score']
    #allAccessions[currentAccession] = (currentAccessionmRNARecord['Score'],currentAccessionmRNARecord['Description'])

    # get the exon
    parser.parse()
    gffDict =  parser.nextRecord()

    # loop through reading the file
    while parser.parserState["ERROR"] == 0:    
        #debugPrint("gff file : %s"%gffDict)
        debugPrint("parser state %s"%parser.parserState)

        doSummary = False
        doReSummary = False

        # decide whether we need to summarise the alignments read up to this point
        if parser.parserState["EOF"] == 1 or parser.parserState["RECORD_TYPE"] == "mRNA":

            debugPrint("--->" + currentAccession)
            if currentAccession in allAccessions :
                if float(currentAccessionmRNARecord['Score']) > float(allAccessions[currentAccession][0]):
                    doReSummary = True

            else:
                doSummary = True

            if not (doSummary or doReSummary ) and parser.parserState["EOF"] == 0:
                currentAccessionmRNARecord = gffDict
                currentAccession = str(gffDict['Accession'])
                currentReference = str(gffDict['Reference'])
                currentScore = gffDict['Score']
                    
                    
        elif parser.parserState["RECORD_TYPE"] == "exon":
            debugPrint("********>" + str(gffDict))
            myExons.append( (int(gffDict['FeatureStart']), int(gffDict['FeatureStop'])) )
        else :
            raise brdfException, " error - unknown GFF Record type " + gffDict['GFFRecordType']
                

        # if we need to summarise the results to this point then do so          
        if doSummary or doReSummary:

                        
            allAccessions[currentAccession] = (currentScore,currentReference,currentAccessionmRNARecord['FeatureStart'],\
                                            currentAccessionmRNARecord['FeatureStop'],currentAccessionmRNARecord['Description'], len(myExons))


            # if did a summary because we are at the end - break, else reset current accession and ref to the
            # mRNA record just read
            if parser.parserState["EOF"] == 1:
                break
            else:
                # reset the current mRNA record to the one just read
                currentAccessionmRNARecord = gffDict
                currentAccession = str(gffDict['Accession'])
                currentReference = str(gffDict['Reference'])
                currentScore = gffDict['Score']


        # if the current parserState is mRNA then we have summarised if required so can reset myExons
        if parser.parserState['RECORD_TYPE'] == "mRNA":
           myExons = []
           
        if parser.parserState["EOF"] == 1:
            break

        gffDict =  parser.nextRecord()

    if parser.parserState['ERROR'] != 0:
        print "error : " + parser.parserState['MESSAGE']
    else:
        if DEBUG:
            print "All Accessions : "
            print allAccessions

            for accession in allAccessions.keys():
                print accession
            

        print "number of accessions : %s"%(len(allAccessions))
          

        # outout the summarised mappings
        outCSV = file("c:/temp/out.csv","wb")
        outCSV.write("contig,chr,start,stop,exonCount,score,description\n")
        for contig in allAccessions.keys():
            outCSV.write("\"%s\",\"%s\",%s,%s,%s,%s,\"%s\"\n"%(contig,allAccessions[contig][1],allAccessions[contig][2],allAccessions[contig][3],\
                                                allAccessions[contig][5],allAccessions[contig][0],\
                                                reduce(lambda x,y:x+" "+y,allAccessions[contig][4])))
        #outCSV.write(outCSVRecord+"\n")
                        
 
        #print row
        #reader.close()
        outCSV.close()                                

            

if __name__ == "__main__":
   main()        

        
        
    

    
