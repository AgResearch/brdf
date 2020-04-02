#
# this class parses Trace Archive XML records
# check arguments
#
import sys,os,string,fileinput,xml.sax.handler,re

#
# stream object for reading a trace archive XML file and
# returning packets for each TI
#
#
# example record :
"""
                <trace>
                        <trace_name>1099341291629</trace_name>
                        <center_name>JCVIJTC</center_name>
                        <submission_type>NEW</submission_type>
                        <species_code>TRICHOSURUS VULPECULA</species_code>
                        <strategy>EST</strategy>
                        <trace_type_code>EST</trace_type_code>
                        <source_type>GENOMIC</source_type>
                        <center_project>POSSUM</center_project>
                        <chemistry_type>TERMINATOR</chemistry_type>
                        <clip_quality_left>30</clip_quality_left>
                        <clip_quality_right>893</clip_quality_right>
                        <clip_vector_left>161</clip_vector_left>
                        <clip_vector_right>1147</clip_vector_right>
                        <clone_id>1061018603089</clone_id>
                        <insert_size>2000</insert_size>
                        <insert_stdev>400</insert_stdev>
                        <library_id>POSSUM_01-POSSUM-LIVER-2KB</library_id>
                        <plate_id>F042326</plate_id>
                        <program_id>KB 1.1.2, TRACE TUNER 2.0.1</program_id>
                        <run_date>Oct 25 2005  6:49PM</run_date>
                        <run_group_id>1064040448870</run_group_id>
                        <run_machine_id>DNA 400</run_machine_id>
                        <run_machine_type>ABI 3730XL</run_machine_type>
                        <seq_lib_id>POSSUM_01-POSSUM-LIVER-2KB</seq_lib_id>
                        <svector_code>PDNRLIB</svector_code>
                        <template_id>1061018603089</template_id>
                        <trace_end>FORWARD</trace_end>
                        <trace_format>ZTR</trace_format>
                        <well_id>A3</well_id>
                        <ncbi_trace_archive>
                                <ti>1096475691</ti>
                                <taxid>9337</taxid>
                                <basecall_length>1147</basecall_length>
                                <load_date>Dec 27 2005  1:52PM</load_date>
                        </ncbi_trace_archive>
                </trace>
                """

class NCBITIXMLStream(object):
    def __init__(self,filename):
        object.__init__(self)
        self.streamState = {
            'ERROR' : 0,
            'EOF' : 0
        }

        # open the file and set up the SAX handlers
        self.filename = filename
        self.resultHandler = simpleResultsHandlerClass()
        self.errorHandler = resultsErrorHandlerClass(self.resultHandler)
        self.infile = open(filename, 'r')
        self.recordCount = 0
        self.bufferedRecord = 'xx'

        # position the stream past the start tags ready to go
        while re.search('\<trace\>',self.bufferedRecord) == None and self.bufferedRecord != '':
            self.bufferedRecord = self.infile.readline()
            print "skipping %s"%self.bufferedRecord

        if self.bufferedRecord == '':
            self.streamState['EOF'] = 1

        

    def nextRecord(self):

        if self.streamState['EOF'] == 1:
            return None

        resultRecord = None
        currentTIRecord = None
        
        while self.streamState['EOF'] != 1:
            if re.search('\<\/trace\>',self.bufferedRecord) != None :
                resultRecord = currentTIRecord
                currentTIRecord = None
                self.recordCount += 1
                self.bufferedRecord = self.infile.readline()
                break
            elif re.search('\<trace\>',self.bufferedRecord) != None:
                currentTIRecord = NCBITIRecord()
                self.bufferedRecord = self.infile.readline()
                #print self.bufferedRecord
            elif re.search('trace_volume',self.bufferedRecord) != None:
                self.streamState['EOF'] = 1
            elif re.search('^\s+$',self.bufferedRecord) != None:
                self.bufferedRecord = self.infile.readline()
            else:
                #print self.resultHandler.currentElementRegister['currentelement']
                self.resultHandler.currentElementRegister['xmlerror1'] = None
                self.resultHandler.currentElementRegister['xmlerror2'] = None
                xml.sax.parseString(self.bufferedRecord,self.resultHandler, self.errorHandler)
                if self.resultHandler.currentElementRegister['currentelement'] != None and \
                    self.resultHandler.currentElementRegister['elementstate'] == 'CLOSED':
                    currentTIRecord.fields[self.resultHandler.currentElementRegister['currentelement']] = \
                            self.resultHandler.currentElementRegister['elementcontent']
                self.bufferedRecord = self.infile.readline()

            if self.bufferedRecord == '':
                self.streamState['EOF'] = 1

        return resultRecord

    def close(self):
        self.infile.close()
        
        
class NCBITIRecord(object):
    def __init__(self):
        self.fields = {}

        

class simpleResultsHandlerClass(xml.sax.handler.ContentHandler):

    def __init__(self):
        xml.sax.handler.ContentHandler.__init__(self)
        self.currentElementRegister = {
            'elementcontent'  : None,
            'currentelement' : None,
            'elementstate' : None
        }
    def startDocument(self):
        pass
        #print "*** in start Document ***"
    def startElement(self, name, attrs):
        self.currentElementRegister['elementcontent'] = None
        self.currentElementRegister['currentelement'] = name
        self.currentElementRegister['elementstate'] = 'OPENED'
        #print 'start %s'%name
        #print 'attrs=%s'%attrs
    def endElement(self, name):
        #self.currentElementRegister['elementcontent'] = None
        if name == self.currentElementRegister['currentelement']:
            self.currentElementRegister['elementstate'] = 'CLOSED'
        #print "end %s"%name
    def startElementNS( name, qname, attrs):
        print "!!!!!!!!!!!!!%s"%name

            
    def characters(self,content):
        #print "content=%s"%content
        if self.currentElementRegister['elementstate'] == 'OPENED':
            self.currentElementRegister['elementcontent'] = content
        self.currentElementRegister['elementstate'] = 'CONTENT'            

        
# make a SAX error handler 
class resultsErrorHandlerClass(xml.sax.handler.ErrorHandler):

    def __init__(self,resultHandler):
        #xml.sax.handler.ErrorHandler.__init__(self)
        self.resultHandler = resultHandler
        
    def error(self,arg):
        self.resultHandler.currentElementRegister['xmlerror1'] =arg

    # weird static method , cannot set state   
    def fatalError(arg1,arg2):
        None
        #print arg1
        #print arg2
        #self.resultHandler.currentElementRegister['xmlerror1'] = arg1
        #self.resultHandler.currentElementRegister['xmlerror2'] = arg2


def fasta2estfile():
    """ transform output like this
    >TYPE: EST!STATUS: NEW!CONT_NAME: Crawford Allan M.!CITATION: Establishment and operation of an Expressed Sequence Tag database for the Brushtail Possum (Trichosurus vulpecula) !LIBRARY: POSSUM_01-C-POSSUM-IMMUNE-2KB!EST#: IMMUNEF054261J14!SOURCE: JCVIJTC!CLONE: 1061020274868!INSERT: 2000!ERROR: 400!PLATE: F054261!ROW: J!COLUMN: 14!SEQ_PRIMER: M13-forward
GGGGTCCCCCCCTCCCGGCCAAGATGTCTGACATGGAGGATGATTTCATG
TGCGATGATGAGGAGGACTACGACCTGGAATACTCTGAAGATAGTAACTC
TGAACCAAATGTGGATTTGGAAAACCAGTACTACAATTCCAAAGCGTTGG
AGGAGGATGACCCAAAAGCAGCATTAAGCAGTTTCCAAAAGGTTTTGGAG
CTTGAAGGTGAAAAAGGAGAATGGGGATTTAAAGCACTGAAACAGATGAT
TAAAATAAACTTCAAGTTGACAAACTATCCAGAAATGATGAATAGATATA
AACAACTATTGACCTACATTCGGAGTGCAGTCACAAGGAATTATTCTGAA
AAGTCTATTAACTCTATTCTTGATTATATCTCTACTTCAAAACAGAATTC
TGATTTTTTATGTCAGATGGATTTACTGCAGGAATTCTATGAAACAACAC
TGGAAGCTCTGAAAGACGCTAAGAATGATAGGCTGTGGTTTAAGACAAAC
ACAAAGCTTGGAAAATTGTATCTAGAACGAGAAGAATATGGAAAGCTTCA
AAAAATTTTGCGCCAGTTGCATCAGTCATGCCAGACGGATGATGGAGAAG
ATGACCTTAAAAAGGGTACACAATTATTGGAAATTTATGCATTAGAAATT
CAAATGTATACAGCACAGAAAAATAACAAAAAACTTAAAGCATTGTATGA
ACAGTCACTGCACATCAAATCAGCCATCCCCCATCCACTGATCATGGGCG
TCATTAGAGAATGTGGCGGTAAAATGCACTTA
to the required estfile , by changing ! to line feeds and appending || between each record
"""
    estsPerFile = 5000
    fileCount = 1
    #inFile = file('k:\\spool-dir\possum\genbank\possum032006gb1.fa','r')
    inFile = file('k:\\spool-dir\possumestphase2gb1.fa','r')
    outFileTemplate = 'k:\\spool-dir\possum\possumestphase2%s.dat'
    outFile = file(outFileTemplate%fileCount,'w')
    recordCount = 0

    for record in inFile:
        if re.search('^>',record) != None:
            if recordCount  > 0:
                outFile.write('||\n')


                if recordCount%estsPerFile == 0:
                    outFile.close()
                    fileCount += 1
                    outFile = file(outFileTemplate%fileCount,'w')
                
                
            recordCount += 1
            record=re.sub('^COMMENT:','^COMMENT:\n',record)
            fields = record[1:].split('!')
            outRecord = string.join(fields[0:len(fields)],'\n')+'SEQUENCE:\n'
            outRecord = re.sub('COMMENT:','COMMENT:\n',outRecord)
            outFile.write(outRecord)
            #print 'SEQUENCE:'
        else:
            outFile.write(record)

    inFile.close()

                
def main():
    fasta2estfile()
    #makeLibAndESTFiles()
    
def makeLibAndESTFiles():
    """
    make the lib and est files for each library 
    """
    # open a stream to read the archive
    tissue = 'immune062006'
    tistream = NCBITIXMLStream("c:\\temp\\alanmcculloch\\TRACEINFO_%s.xml"%tissue)

    tirecord = tistream.nextRecord()

    libraries = {}

    # open the following output files :
    estRecordFile = file('c:\\temp\\possumESTFile%s.csv'%tissue,'w')
    
    
    while tirecord != None:
        if tirecord.fields['library_id'] not in libraries:
            libraries[tirecord.fields['library_id']] = {
                'TYPE' : 'Lib',
                'NAME' : tirecord.fields['library_id'],
                'ORGANISM' :  'Trichosurus vulpecula',
                'TISSUE' :  '??????? example : lactating mammary gland',
                'VECTOR' :  tirecord.fields['svector_code'],
                'V_TYPE' : 'plasmid',
                'DESCR' : '??????? example : Bovine lactating mammary gland cDNA library derived from tissue harvested from Jersey cow by'
            }
        else:
            if libraries[tirecord.fields['library_id']]['VECTOR'] != tirecord.fields['svector_code']:
                print "!!!!! Warning - vector changed in library %s !!!!!"%tirecord.fields['library_id']
                    
            
        #print "** Record %s **"%tistream.recordCount
        #print reduce(lambda x,y:x+"%s=%s\n"%(y[0],y[1]),tirecord.fields.items(),'')
        estRecord = {
            'TYPE' : 'EST',
            'SOURCE' : tirecord.fields['center_name'],
            'LIBRARY' : tirecord.fields['library_id'],
            'ESTNAME' :  "%s%s%s"%(tirecord.fields['library_id'].split('-')[-2],tirecord.fields['plate_id'],\
                                      tirecord.fields['well_id']),
            'TI' : tirecord.fields['ti'],
            'CLONE' : tirecord.fields['clone_id'],
            'INSERT' : tirecord.fields['insert_size'],
            'ERROR' : tirecord.fields['insert_stdev'],
            'PLATE' : tirecord.fields['plate_id'],
            'ROW' : tirecord.fields['well_id'][0],
            'COLUMN' : tirecord.fields['well_id'][1:],
            'TRACE' : tirecord.fields['trace_name']
        }

        if tirecord.fields['trace_end'] == 'FORWARD' :
            estRecord.update({
                'SEQ_PRIMER' : 'M13-forward'
            })
        elif tirecord.fields['trace_end'] == 'REVERSE' :
            estRecord.update({
                'SEQ_PRIMER' : 'M13-reverse'
            })

        estRecordFile.write("%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\n"%(estRecord['TYPE'],estRecord['SOURCE'],estRecord['LIBRARY'],\
            estRecord['ESTNAME'],estRecord['CLONE'], estRecord['INSERT'],estRecord['ERROR'],estRecord['PLATE'],\
            estRecord['ROW'],estRecord['COLUMN'],estRecord['TRACE'], estRecord['SEQ_PRIMER'],estRecord['TI']))
        
        tirecord = tistream.nextRecord()


    tistream.close()
    estRecordFile.close()

    # write the lib file
    libFile = file('c:\\temp\\possumLibFile%s.csv'%tissue,'w')
    for library in libraries.keys():
        libFile.write(reduce(lambda x,y:x+"%s:\t%s\n"%(y[0],y[1]),libraries[library].items(),''))
        libFile.write('||\n')

    libFile.close()



main()

    
