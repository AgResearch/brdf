#
# This module implements a number of simple parsers for sequence files
#
from types import *
import re
import string
from brdfExceptionModule import brdfException
from StringIO import StringIO

#-------------------- module variables ---------------------------



#-------------------- module classes  ----------------------------


class FastaParser ( object ):
    """
    This implements a lite parse, without dependency on other libraries, with a
    few custom features - such as being able to read in and sub-sequence a given
    sequence, without having to first load the whole sequence into memory. Also
    a simple compression algorithm is included
    """
    def __init__(self,infilename,compression=None, substart = None, substop=None):
        object.__init__(self)

        self.infilename = infilename
        self.compression = compression
        self.subcoords = (substart, substop)  # we will later assume we are given 1-based coords

        self.parserState = {
            "ERROR" : 1,
            "PRE" : 1,
            "IDLINE" : 0,
            "SEQUENCE" : 0,
            "EOF" : 0,
            "BUFFER_OCCUPIED" : 0,
            "PAST_SUBSEQUENCE" : 0,
            "MESSAGE" : ''
            }

        # we allow in-memory sequence objects
        if self.infilename.__class__.__name__ == "str":
            self.infile = open(self.infilename, "r")
        elif self.infilename.__class__.__name__ == "StringIO":
            self.infile = self.infilename
            

        self.parserState["ERROR"] = 0
        self.bufferedSeq = {
            "id" : "anonymous_sequence",
            "sequence" : StringIO(),
            "description" : ""
        }
        self.bufferedid = None
        self.linecount = 0
        self.basecount = 0
        
    def __del__(self):
        if self.infile != None:
            self.infile.close()
            self.infile = None
        
    def close(self):
        if self.infile != None:
            self.infile.close()
            self.infile = None
                
    def nextRecord(self):
        if self.parserState['ERROR'] == 1:
            return None

        while self.parserState["BUFFER_OCCUPIED"] == 0 and self.parserState["EOF"] == 1:
            return None
        
        # return the buffered sequence and fill the buffer
        while self.parserState["BUFFER_OCCUPIED"] == 0 and self.parserState["EOF"] == 0:
            self.fillBuffer()

        if self.parserState["BUFFER_OCCUPIED"] == 1:
            self.parserState["BUFFER_OCCUPIED"] = 0            
            self.bufferedSeq["sequence"] =self.bufferedSeq["sequence"].getvalue() 
            return self.bufferedSeq
        else:
            return None

        
        
    def fillBuffer(self):
        # if at the start get ID line. If we get some lines preceeding the ID line, then
        # these are assumed to be unnamed sequence and we fill the buffer with an unnamed sequence
        print "in fill buffer : %s"%str(self.parserState)
        if self.parserState["PRE"] == 1:
            # read until get ID line
            self.bufferedid = "anonymous_sequence"

            if self.subcoords[0] != None:
                self.bufferedid += " (extract from original sequence, from %s to %s)"%self.subcoords
                
            record = self.infile.readline()
            print "debug %s"%str(record)
            self.linecount += 1
            
            if record == "":
                self.parserState["EOF"] = 1
                self.parserState["BUFFER_OCCUPIED"] = 0

            #print "=1=>%s"%record                
            #while re.search('^\s*\>',record) == None:
            #    record = self.infile.readline()
            #    print "=2=>%s"%record
            #    self.linecount += 1
            #    
            #print "1%s"%record
            #if record == "":
            #    self.parserState["EOF"] = 1
            #    self.parserState["BUFFER_OCCUPIED"] = 0
            #    return
            #else:
            #    self.parserState["IDLINE"] = 1
            #    self.bufferedid = record.strip() + " (extract from original sequence, from %s to %s)"%self.subcoords
            #
            #record = self.infile.readline()
            #self.linecount += 1                
            while re.search('^\s*\>',record) == None:
                print "=3=>%s"%record
                if len(record.strip()) > 0:
                    record = record.strip()
                    #self.bufferedSeq["sequence"].write(record.strip())
                    self.basecount += len(record)
                    if self.subcoords[0] != None:
                        if not self.parserState["PAST_SUBSEQUENCE"]:
                            print "comparing %s and %s\n"%(self.basecount,self.subcoords[0])
                            if self.basecount >= self.subcoords[0]:
                                # if necessary chop off something from the start of the record
                                sublength = min(len(record), 1 + self.basecount - self.subcoords[0])
                                record = record[max(0,len(record) - sublength):]
                                print "=4=>%s"%record

                                # if necessary chop off something from the end
                                print "comparing %s and %s\n"%(self.basecount,self.subcoords[1])                                
                                if self.basecount > self.subcoords[1]:
                                    overhang = self.basecount - self.subcoords[1]
                                    sublength = max(0, len(record) - overhang)
                                    record = record[0:sublength]
                                    print "=5=>%s"%record

                                    self.parserState["PAST_SUBSEQUENCE"] = 1
                                
                                
                    if self.compression == None:
                        if self.parserState["PAST_SUBSEQUENCE"] < 2:
                            if linecount%1000 == 1:
                                print "=4=>writing %s"%record.strip()  
                            self.bufferedSeq["sequence"].write(record.strip())
                            if self.parserState["PAST_SUBSEQUENCE"] == 1:
                                self.parserState["PAST_SUBSEQUENCE"] = 2

                            
                    elif self.compression == 1:
                        crecord = re.sub('AAA','1',record.strip())
                        crecord = re.sub('AAC','2',crecord)
                        crecord = re.sub('AAG','3',crecord)
                        crecord = re.sub('AAT','4',crecord)
                        crecord = re.sub('ACA','5',crecord)
                        crecord = re.sub('ACC','6',crecord)
                        crecord = re.sub('ACG','7',crecord)
                        crecord = re.sub('ACT','8',crecord)
                        crecord = re.sub('AGA','9',crecord)
                        crecord = re.sub('NNNNNNNNNN','0',crecord)
                        if not self.parserState["PAST_SUBSEQUENCE"]:                        
                            self.bufferedSeq["sequence"].write(crecord)
                    else:  
                        raise brdfException("unhandled compression type requested")
                    self.parserState["BUFFER_OCCUPIED"] = 1
                    self.bufferedSeq["id"] = bufferedid
                
                record = self.infile.readline()
                self.linecount += 1
                if record == "" or record == None:
                    self.parserState["EOF"] = 1
                    return

            # we must have obtained the next id line or reached the end of the file. If the buffer is still not occupied , fill it
            self.parserState["ERROR"] = 0
            self.parserState["PRE"] = 0
            if self.parserState["EOF"] == 0:
                self.parserState["IDLINE"] = 1
            self.bufferedid = record.strip()
            if self.subcoords[0] != None:            
                self.bufferedid += " (extract from original sequence, from %s to %s)"%self.subcoords
            
            if self.parserState["BUFFER_OCCUPIED"] == 0:
                self.fillBuffer()
            return
            
        elif self.parserState["IDLINE"] == 1:
            # read sequence until get next id line or the end
            self.bufferedSeq["id"] = re.sub("^\>","",re.split('\s+',self.bufferedid)[0])
            self.bufferedSeq["description"] = string.join(  re.split('\s+',self.bufferedid)[1:],' ')
            self.bufferedSeq["sequence"] = StringIO()
            self.basecount = 0
            self.parserState["PAST_SUBSEQUENCE"] = 0


            record = self.infile.readline()
            print "debug:%s"%str(record)
            self.linecount += 1
            if record == "" or record == None:
                self.parserState["EOF"] = 1
                return            
            while re.search('^\s*\>',record) == None:
                #print "=6=>%s"%record
                if len(record.strip()) > 0:

                    record = record.strip()
                    #self.bufferedSeq["sequence"].write(record.strip())
                    self.basecount += len(record)
                    if self.subcoords[0] != None:
                        if not self.parserState["PAST_SUBSEQUENCE"]:
                            if self.basecount >= self.subcoords[0]:
                                # if necessary chop off something from the start of the record
                                sublength = min(len(record), 1 + self.basecount - self.subcoords[0])
                                record = record[max(0,len(record) - sublength):]

                                # if necessary chop off something from the end 
                                if self.basecount > self.subcoords[1]:
                                    overhang = self.basecount - self.subcoords[1]
                                    sublength = max(0, len(record) - overhang)
                                    record = record[0:sublength]
                                    self.parserState["PAST_SUBSEQUENCE"] = 1                    
                    
                    if self.compression == None:
                        if self.parserState["PAST_SUBSEQUENCE"] < 2:
                            #if self.linecount%1000 == 1:
                            #    print "=6=>writing %s"%record.strip()
                            self.bufferedSeq["sequence"].write(record.strip())
                            if self.parserState["PAST_SUBSEQUENCE"] == 1:
                                self.parserState["PAST_SUBSEQUENCE"] = 2
                            
                    elif self.compression == 1:
                       crecord = re.sub('AAA','1',record.strip())
                       crecord = re.sub('AAC','2',crecord)
                       crecord = re.sub('AAG','3',crecord)
                       crecord = re.sub('AAT','4',crecord)
                       crecord = re.sub('ACA','5',crecord)
                       crecord = re.sub('ACC','6',crecord)
                       crecord = re.sub('ACG','7',crecord)
                       crecord = re.sub('ACT','8',crecord)
                       crecord = re.sub('AGA','9',crecord)
                       crecord = re.sub('NNNNNNNNNN','0',crecord)
                       if not self.parserState["PAST_SUBSEQUENCE"]:                            
                           self.bufferedSeq["sequence"].write(crecord)
                    else:
                       raise brdfException("unhandled compression type requested")
                    self.parserState["BUFFER_OCCUPIED"] = 1
                    self.bufferedSeq["id"] = self.bufferedid
                    
                record = self.infile.readline()
                self.linecount += 1
                if self.linecount%1000 == 1:
                    print "linecount = %s "%self.linecount
                if record == "" or record == None:
                    self.parserState["EOF"] = 1
                    return

            # we must have obtained the next id line or reached the end of the file. 
            self.parserState["ERROR"] = 0
            self.parserState["PRE"] = 0
            if self.parserState["EOF"] == 0:
                self.parserState["IDLINE"] = 1
            self.bufferedid = record.strip()
            if self.subcoords[0] != None:            
                self.bufferedid += " (extract from original sequence, from %s to %s)"%self.subcoords
            
            if self.parserState["BUFFER_OCCUPIED"] == 0:
                self.fillBuffer()
            return
        else:
            raise brdfException("unhandled parser state in fasta parser")

def parseSequenceID(instring, target="name", hint="NCBI piped"):
    """ this method collects together rules for parsing out names
    from id's such as emb|CAA73169.1| dbj|BAD30339.1| etc
    """
    result = instring
    
    if instring == None:
        return result
    elif instring.strip() == "":
        return result
    if hint == "NCBI piped" :
        tokens = re.split("|",instring.strip())
        tokens = [item for item in tokens if len(item) > 2]
        result = tokens[-1]
        if target == "name":
            return re.split('\.',result)[0]
        else:
            return result
            
            

def main():
    test = StringIO(""">test
CAGCATGATAGCTAGACTAGGACTG
CGACTAGCATGC
""")
    #test.writelines("abcdef\n")
    #print test.getvalue()
    #x=test.readlines()
    #print x
    #return
    
    #test = "jkhkjh"
    #parser = FastaParser("c:/temp/test.seq",substart = 3, substop=10)
    parser = FastaParser(test,substart = 3, substop=10)
               
    #parser = FastaParser("c:/temp/test.seq")
    mywriter=file("c:/temp/sequence.dat","w")

    record = parser.nextRecord()
    while record != None:
        #print record
        mywriter.write("%(id)s\t%(sequence)s\n"%record)
        #print parser.parserState
        record = parser.nextRecord()

    mywriter.close()
            

    print str(parser.parserState)
        


if __name__ == "__main__":
   main()        

        
        
    

        
