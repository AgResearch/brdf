#
# This module implements lite home-made parsers and utils for GFF
# and other files
#
from types import *
import re
import string
from brdfExceptionModule import brdfException
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
            return None

        record = self.infile.readline()
        #print record

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
        fields = [item.strip() for item in fields]

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
        
    


            

if __name__ == "__main__":
   main()        

        
        
    

    
