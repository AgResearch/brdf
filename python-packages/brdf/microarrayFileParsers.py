#
# This module implements a number of parsers for various
# microarray infiles - e.g. GAL infiles etc
#
from types import *
import re
import string

#-------------------- module variables ---------------------------



#-------------------- module classes  ----------------------------

#################################################################
# GAL and GPR File parsers
#
# GAL and GPR files both have a header section, with
# key=value
#
# then a tab separated body section.
#
# Both files can be handled by the same parser - though we define
# specific GAL and GPR parsers in case of future customisation requirements
#################################################################



class GeneralGParser ( object ):
    """ This class parsers the header and spot details from a GAL or GPRinfile. The header is parsed into
    a dictionary, then the file is left open so that calls to nextRecord return each row ( as a dictionary  - e.g.
    so can be passed straight to a SQL insert)"""
    def __init__(self,infilename):
        object.__init__(self)

        self.infilename = infilename

        self.parserState = {
            "ERROR" : 1,
            "PRE" : 1,
            "HEADER" : 0,
            "BODY" : 0,
            "EOF" : 0,
            "MESSAGE" : ''
            }
        self.infile = open(self.infilename, "r")
        self.parserState["ERROR"] = 0
        
    def __del__(self):
        self.infile.close()

    def parse(self):

        if [self.parserState[state] for state in ("BODY" , "ERROR", "EOF")] != [0,0,0]:
            self.parserState.comment="returned immediately from parse"
            return
        
        self.headerDict={}
        # open infile
        
        lineCount = 0
        while [self.parserState[state] for state in ("BODY" , "ERROR", "EOF")] == [0,0,0]:
            record = self.infile.readline()
            lineCount += 1
            self.comment = 'parse method read line ' + str(lineCount)

            record = record.strip().replace('"','')

            #print '***',lineCount, record
            if lineCount > 2 and self.parserState["HEADER"] == 0:
                self.parserState["HEADER"] = 1
                
            if self.parserState["HEADER"] == 1:
                fields = re.split('=',record)
                if len(fields) == 1:
                    self.columnHeadings = re.split('\t',record.lower())
                    self.columnHeadings = [self.fieldNameSuffix + item for item in self.columnHeadings]
                    

                    # the later GPR file formats have an annoying unicode squared symbol - get rid
                    self.columnHeadings = [re.sub('\xb2','squared',item) for item in self.columnHeadings]
                    self.columnHeadings = [item.strip() for item in self.columnHeadings]                    
                    self.parserState["BODY"] = 1
                    break
                else:
                    self.headerDict[string.lower(self.fieldNameSuffix+fields[0].strip())] = fields[1].strip()
                
    def nextRecord(self):
        if [self.parserState[state] for state in ("BODY" , "ERROR", "EOF")] != [1,0,0]:
            return
        
        record = self.infile.readline()
        if record == None:
            self.parserState["EOF"] = 1
            return None
            
        self.rawRecord = record.strip()
        record = record.strip()
        #record = record.replace('Error','') # postgres will insert empty strings as zero !

        if len(record) == 0:
            self.parserState["EOF"] = 1
            return None
        
        fields = re.split('\t',record)
        fields = [item.replace('"','') for item in fields]
        fields = [eval({True : 'None' , False : 'item'}[item == 'Error']) for item in fields]

        

        returnDict = dict(zip(self.columnHeadings,fields))
        returnDict.update( {
            'EMPTY' : None
        })

        return returnDict


class GALFileParser (GeneralGParser):
    """ This class parsers the header and spot details from a GAL file. The header is parsed into
    a dictionary, then the file is left open so that calls to nextRecord return each row ( as a dictionary  - e.g.
    so can be passed straight to a SQL insert)"""
    def __init__(self,infilename):
        GeneralGParser.__init__(self,infilename)
        self.fieldNameSuffix = 'gal_'

class GPRFileParser (GeneralGParser):
    """ This class parsers the header and spot details from a GPR file. The header is parsed into
    a dictionary, then the file is left open so that calls to nextRecord return each row ( as a dictionary  - e.g.
    so can be passed straight to a SQL insert)"""    
    def __init__(self,infilename):
        GeneralGParser.__init__(self,infilename)
        self.fieldNameSuffix = 'gpr_'




def main():
    parser = GALFileParser("/data/bfiles/possumbase/microarray/OpossumOligoPrint 141 22-04-08 tracking.gal")    
    #parser = GPRFileParser("c:/working/nutrigenomics/251269421240_2006-07-14_low 450_test.gpr")
    #parser = GALFileParser("c:\\working\zaneta\\012694_D_20050902.gal")    
    #parser = GPRFileParser("M:\\projects\\nutrigenomics\\brdf\\data\\experiments\\22944_1Av13A_low.gpr")
    #parser = GPRFileParser("c:\\working\\zaneta\\Pool 18 array high scan.gpr")    
    parser.parse()
    #print parser.parserState
    print parser.headerDict
    print parser.columnHeadings
    while parser.parserState["EOF"] == 0:
        print parser.nextRecord()
        break
    #print parser.rawRecord
    #print parser.nextRecord()
    #print parser.rawRecord


if __name__ == "__main__":
   main()        

        
        
    

        
