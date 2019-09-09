#
# This module implements classes relating to bio subjects , samples and protocols
#
from types import *

from obmodule import getNewObid,getObjectRecord
from brdfExceptionModule import brdfException
from opmodule import op
from obmodule import ob,canonicalDate
import logging
import os
import globalConf

modulelogger = logging.getLogger('biosubjectmodulelogger')
#hdlr = logging.FileHandler('c:/temp/nutrigenomicsforms.log')
hdlr = logging.FileHandler(os.path.join(globalConf.LOGPATH,'biosubjectmodule.log'))
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
modulelogger.addHandler(hdlr) 
modulelogger.setLevel(logging.INFO)      




class bioSubjectOb (ob ):
    """ bioSubjectOb objects represent biosubjects such as RNA , DNA etc"""
    def __init__(self):
        ob.__init__(self)

    def initFromDatabase(self, identifier, connection):
        """ method for initialising an object from database - arg can be an integer obid, or a string importProcedureName"""
          
        # initialise base fields from ob table
        ob.initFromDatabase(self, identifier,"bioSubjectOb",connection)

        # now get the complete object
        self.databaseFields = getObjectRecord(connection, "bioSubjectOb", self.databaseFields['obid'])
        
        self.obState.update({'ERROR' : 0 , 'NEW' : 0, 'MESSAGE' : "initialised from database OK"})

    def initNew(self,connection):
        """ method to initialise a new biosubject object """
        self.databaseFields = {
            'obid' : getNewObid(connection) ,
            'subjectname' : None,
            'xreflsid' : None,
            'strain' : None,
            'subjectdescription' : None,
            'subjectspeciesname' : None,
            'dob' : None,
            'sex' : None         
        } 
        self.obState.update({'DB_PENDING' : 1})

    def insertDatabase(self,connection):
        """ method used by bioSubject object to save itself to database  """

        if self.databaseFields['dob'] != None:
            #print "***** rawdate for subject is %s"%self.databaseFields['dob']
            self.databaseFields['dob'] = canonicalDate(self.databaseFields['dob'])
            #print "***** canonicaldate for subject is %s"%self.databaseFields['dob']

            
        sql = """
        insert into biosubjectOb(obid,subjectname,xreflsid,strain,subjectDescription,subjectspeciesname,
        dob,sex)
        values (%(obid)s,%(subjectname)s,%(xreflsid)s,%(strain)s,%(subjectdescription)s,%(subjectspeciesname)s,
        to_date(%(dob)s,'dd-mm-yyyy'),%(sex)s)
        """            
        #print "executing " + sql%self.databaseFields
        insertCursor = connection.cursor()
        insertCursor.execute(sql,self.databaseFields)
        connection.commit()
        insertCursor.close()
        self.obState.update({'NEW' : 0 , 'ERROR' : 0, 'DB_PENDING' : 0, 'MESSAGE' : "database insert OK"})
        
    def updateDatabase(self,connection):
        """ method used by bioSubject object to save itself to database  """

        if self.databaseFields['dob'] != None:
            #print "***** rawdate for subject is %s"%self.databaseFields['dob']
            self.databaseFields['dob'] = canonicalDate(self.databaseFields['dob'])
            #print "***** canonicaldate for subject is %s"%self.databaseFields['dob']

            
        sql = """
        UPDATE biosubjectOb
            SET subjectname         = %(subjectname)s,
                xreflsid            = %(xreflsid)s,
                strain              = %(strain)s,
                subjectDescription  = %(subjectdescription)s,
                subjectspeciesname  = %(subjectspeciesname)s,
                dob                 = to_date(%(dob)s,'dd-mm-yyyy'),
                sex                 = %(sex)s
            WHERE obid=%(obid)s
        """            
        #print "executing " + sql%self.databaseFields
        insertCursor = connection.cursor()
        insertCursor.execute(sql,self.databaseFields)
        connection.commit()
        insertCursor.close()
        self.obState.update({'NEW' : 0 , 'ERROR' : 0, 'DB_PENDING' : 0, 'MESSAGE' : "database update OK"})

    def addFact(self,connection,argfactNameSpace, argattributeDate, argattributeName, argattributeValue):
        factFields = {
            'bioSubjectOb' : self.databaseFields['obid'],
            'factNameSpace' : argfactNameSpace,
            'attributeDate' : argattributeDate,
            'attributeName' : argattributeName,
            'attributeValue' : argattributeValue }

        # first check if this fact is already in the db - if it is do not duplicate
        sql = """
        select biosubjectob from bioSubjectFact where
        biosubjectob = %(bioSubjectOb)s and
        factNameSpace = %(factNameSpace)s and
        attributeName = %(attributeName)s and
        attributeValue = %(attributeValue)s
        """
        insertCursor = connection.cursor()
        modulelogger.info("checking for fact using %s"%(sql%factFields))
        insertCursor.execute(sql,factFields)
        insertCursor.fetchone()
        modulelogger.info("rowcount = %s"%insertCursor.rowcount)
        if insertCursor.rowcount == 0:        
            sql = """
            insert into bioSubjectFact(biosubjectob,factNameSpace, attributeName, attributeValue)
            values(%(bioSubjectOb)s,%(factNameSpace)s,%(attributeName)s,%(attributeValue)s)
            """
            modulelogger.info("executing %s"%(sql%factFields))
            insertCursor.execute(sql,factFields)
            connection.commit()
            insertCursor.close()
            self.obState.update({'NEW' : 0 , 'DB_PENDING' : 0, 'ERROR' : 0, 'MESSAGE' : "database insert OK"})
        else:
            insertCursor.close()
          


class bioSampleOb (ob ):
    """ bioSampleOb objects represent biosamples such as RNA , DNA etc"""
    def __init__(self):
        ob.__init__(self)

        self.AboutMe['default'][0]['heading'] = 'BRDF Sample Object'
        self.AboutMe['default'][0]['text'] = """
        This page displays a biosample object from the BRDF database.

        In the BRDF database schema, sample objects are stored in a table called
        biosampleob. Various types of sample can be stored in this table - for example,
        RNA extract, clone, 2D Gel spot, Histology, Blood Sample.
        </p>
        The type of sample is stored in the sampletype field of this table.
        The current set of sample types that are supported in this database are recorded in an ontology called
        BIOSAMPLE_TYPES. (You can browse this ontology by selecting ONTOLOGIES from the drop down list
        of search types on the main page, and entering BIOSAMPLE_TYPES as the search phrase)
        <p/>
        A Sample object in the BRDF database may have relationships with other types of object
        in the database. For example, the sampling process itself will involve a relationship between a biosubject
        from which the sample was obtained, one or more lab resources (kits etc) , and a sampling protocol.
        Once the sample is used - for example in a microarray or rtPCR experiment, or a genotype experiment,
        or a sequencing experiment, then each of these involves an additional relationship to other objects
        in the BRDF database.
        
        All of the possible relationships that a sample object may have with other objects in the database
        are depicted by icons in the information map section of the page.

        The icon is composed of the biosampleob symbol connected to the symbols for the related objects
        by horizontal lines. Where the database does not yet contain any related objects for a sample,
        the icon for that relationship is greyed out.
        <p/>
        We may store various types of facts about a given sample object. Each type of fact supported by the
        BRDF is depicted by a line connecting the biosample symbol , to a square box labelled info,
        with the type of fact appearing to the right of the icon. Where the database does not yet contain any facts
        of a given type for a sequence object, the info icon is greyed out. (Currently the only details table
        is a general purpose one which allows you to store arbitrary key-value pairs. Specialist details tables
        can be added as required , and icons representing these tables will then automatically appear
        on biosample BRDF pages)
        """                                

    def initFromDatabase(self, identifier, connection):
        """ method for initialising an object from database - arg can be an integer obid, or a string importProcedureName"""
          
        # initialise base fields from ob table
        ob.initFromDatabase(self, identifier,"bioSampleOb",connection)

        # now get the complete object
        self.databaseFields = getObjectRecord(connection, "bioSampleOb", self.databaseFields['obid'])
        
        self.obState.update({'ERROR' : 0 , 'NEW' : 0, 'MESSAGE' : "initialised from database OK"})

    def initNew(self,connection):
        """ method to initialise a new biosample object """
        self.databaseFields = {
            'obid' : getNewObid(connection) ,
            'samplename' : None,
            'xreflsid' : None,
            'sampletype' : None,
            'sampledate' : None,
            'sampletissue' : None,
            'sampledescription' : None,
            'samplestorage' : None,
            'samplecount' : None,
            'sampleweight' : None,
            'sampleweightunit' : None,
            'samplevolume' : None,
            'samplevolumeunit' : None,
            'sampledrymatterequiv' : None,
            'sampledmeunit' : None
        } 
        self.obState.update({'DB_PENDING' : 1})        

    def insertDatabase(self,connection):
        """ method used by bioSample object to save itself to database  """

        if self.databaseFields['sampledate'] != None:
            self.databaseFields['sampledate'] = canonicalDate(self.databaseFields['sampledate'])
            
        
        sql = """
        insert into biosampleOb(obid,samplename,xreflsid,sampletype,sampledate,sampletissue,
            sampledescription,samplestorage,samplecount,sampleweight,sampleweightunit,samplevolume,
            samplevolumeunit,sampledrymatterequiv,sampledmeunit)
        values (%(obid)s,%(samplename)s,%(xreflsid)s,%(sampletype)s,to_date(%(sampledate)s,'dd-mm-yyyy'),
        %(sampletissue)s,%(sampledescription)s,%(samplestorage)s, %(samplecount)s,%(sampleweight)s,%(sampleweightunit)s,%(samplevolume)s,
            %(samplevolumeunit)s,%(sampledrymatterequiv)s,%(sampledmeunit)s)
        """
        #print "executing " + sql%self.databaseFields
        insertCursor = connection.cursor()
        insertCursor.execute(sql,self.databaseFields)
        connection.commit()
        insertCursor.close()
        self.obState.update({'NEW' : 0 , 'ERROR' : 0, 'DB_PENDING' : 0, 'MESSAGE' : "database insert OK"})


    # this creates a link to a parent sample or subject
    def createSamplingFunction(self, connection, biosubjectob, xreflsid, bioprotocolob = None, \
                               labBookReference = None, samplingComment = None, parentsampleob = None, checkExisting = False,voptypeid = None):
        """ method used to relate this sample to a subject and optionally a protocol """

        # check we do not have two parents
        if biosubjectob != None and parentsampleob != None:
            raise brdfException("error can't specify both parent subject and parent sample")

        # check we have a parent
        if biosubjectob == None and parentsampleob == None:
            raise brdfException("error must specify a parent sample or subject")

        functionDetails = {
            'biosampleob' : self.databaseFields['obid'],
            'biosubjectob' : eval({False : "biosubjectob.databaseFields['obid']",True : "None"}[ biosubjectob == None ]),
            'bioprotocolob' : eval({False : "bioprotocolob.databaseFields['obid']",True : "None"}[ bioprotocolob == None ]),
            'labBookReference' : labBookReference,
            'samplingComment' : samplingComment,
            'xreflsid' : xreflsid,
            'parentsampleob' : eval({False : "parentsampleob.databaseFields['obid']",True : "None"}[ parentsampleob == None ]),
            'voptypeid' : voptypeid
        }        
        
        insertCursor = connection.cursor()

        doInsert = True
        if checkExisting:
            if parentsampleob != None:
                sql = """
                select obid from biosamplingfunction where
                parentsample = %(parentsampleob)s and biosampleob = %(biosampleob)s
                """
            elif biosubjectob != None:
                sql = """
                select obid from biosamplingfunction where
                biosubjectob = %(biosubjectob)s and biosampleob = %(biosampleob)s
                """                    

            modulelogger.info("createsamplingfunction checking for existing link using %s"%sql%functionDetails)
            insertCursor.execute(sql,functionDetails)
            insertCursor.fetchone()

            if insertCursor.rowcount >= 1:
                doInsert = False

        if doInsert:
            sql = """
            insert into biosamplingfunction(biosampleob,biosubjectob,xreflsid,bioprotocolob,labBookReference,
                samplingComment, parentsample,voptypeid)
            values(%(biosampleob)s,%(biosubjectob)s,%(xreflsid)s,%(bioprotocolob)s,%(labBookReference)s,
                %(samplingComment)s, %(parentsampleob)s, %(voptypeid)s)
            """

            insertCursor.execute(sql,functionDetails)
            connection.commit()
            
        insertCursor.close()
        self.obState.update({'NEW' : 0 , 'ERROR' : 0, 'DB_PENDING' : 0, 'MESSAGE' : "sampling function insert OK"})


    # this creates a link to a child sample-fraction(creating the sample-fraction record if necessary)
    def getSampleFraction(self, connection, fractionDetailsDict = {"xreflsid" : None}, bioprotocolob = None, \
                               labBookReference = None, samplingComment = None):
        """this method retrieves or creates a child sample record - the fraction - and sets up a link to it """

        # check whether the child already exists
        modulelogger.info("in getSampleFraction with %s"%str(fractionDetailsDict))
        fraction = bioSampleOb()
        try:
            fraction.initFromDatabase(fractionDetailsDict["xreflsid"],connection)                
        except brdfException:
            if fraction.obState['ERROR'] == 1:

                
                fraction.initNew(connection)

                # if the details we are inheriting from have an obid, remove it
                if 'obid' in fractionDetailsDict:
                    del fractionDetailsDict['obid']

                fraction.databaseFields.update(fractionDetailsDict)
                fraction.insertDatabase(connection)
                print 'inserted' + str(fraction)
                doLink = True


        # link the child to the parent (i.e. to this object), if not already linked        
        samplinglsid = "%s:%s"%(self.databaseFields["samplename"],fraction.databaseFields["samplename"])

        # this creates a link from the child back to the parent - i.e. to this object
        fraction.createSamplingFunction(connection, None, samplinglsid, bioprotocolob, labBookReference , samplingComment , \
                                        self , checkExisting = True, voptypeid = 100)
        

        return fraction


    def addFact(self,connection,argfactNameSpace, argattributeName, argattributeValue):
        factFields = {
            'bioSampleOb' : self.databaseFields['obid'],
            'factNameSpace' : argfactNameSpace,
            'attributeName' : argattributeName,
            'attributeValue' : argattributeValue }

        # first check if this fact is already in the db - if it is do not duplicate
        sql = """
        select biosampleob from bioSampleFact where
        biosampleob = %(bioSampleOb)s and
        factNameSpace = %(factNameSpace)s and
        attributeName = %(attributeName)s and
        attributeValue = %(attributeValue)s
        """
        insertCursor = connection.cursor()
        modulelogger.info("checking for fact using %s"%(sql%factFields))
        insertCursor.execute(sql,factFields)
        insertCursor.fetchone()
        modulelogger.info("rowcount = %s"%insertCursor.rowcount)
        if insertCursor.rowcount == 0:        
            sql = """
            insert into bioSampleFact(biosampleob,factNameSpace, attributeName, attributeValue)
            values(%(bioSampleOb)s,%(factNameSpace)s,%(attributeName)s,%(attributeValue)s)
            """
            modulelogger.info("executing %s"%(sql%factFields))
            insertCursor.execute(sql,factFields)
            connection.commit()
            insertCursor.close()
            self.obState.update({'NEW' : 0 , 'DB_PENDING' : 0, 'ERROR' : 0, 'MESSAGE' : "database insert OK"})
        else:
            insertCursor.close()

          


class bioSamplingFunction (op ):
    """ bioSamplingFunction represent biosampling sessions , as opposed to the actual samples, and is an op"""
    def __init__(self):
        op.__init__(self)

    def initFromDatabase(self, identifier, connection):
        """ method for initialising an object from database - arg can be an integer obid, or a string importProcedureName"""
          
        # initialise base fields from ob table
        ob.initFromDatabase(self, identifier,"bioSamplingFunction",connection)

        # now get the complete object
        self.databaseFields = getObjectRecord(connection, "bioSamplingFunction", self.databaseFields['obid'])
        
        self.obState.update({'ERROR' : 0 , 'NEW' : 0, 'MESSAGE' : "initialised from database OK"})

class bioSampleAliquotFact (op ):
    def __init__(self):
        op.__init__(self)

    def initFromDatabase(self, identifier, connection):
        """ method for initialising an object from database"""
          
        # initialise base fields from ob table
        ob.initFromDatabase(self, identifier,"bioSampleAliquotFact",connection)

        # now get the complete object
        self.databaseFields = getObjectRecord(connection, "bioSampleAliquotFact", self.databaseFields['obid'])
        
        self.obState.update({'ERROR' : 0 , 'NEW' : 0, 'MESSAGE' : "initialised from database OK"})        


class pedigreeLink (op ):
    """ pedigree link """
    def __init__(self):
        op.__init__(self)

    def initFromDatabase(self, identifier, connection):
        """ method for initialising an object from database"""
          
        # initialise base fields from ob table
        ob.initFromDatabase(self, identifier,"pedigreeLink",connection)

        # now get the complete object
        self.databaseFields = getObjectRecord(connection, "pedigreeLink", self.databaseFields['obid'])
        
        self.obState.update({'ERROR' : 0 , 'NEW' : 0, 'MESSAGE' : "initialised from database OK"})        

 
        
class bioSampleList (ob ):
    """ bioSampleOb objects represent biosamples such as RNA , DNA etc"""
    def __init__(self):
        ob.__init__(self)

    def initFromDatabase(self, identifier, connection):
        # first init base class - this will get obid
        ob.initFromDatabase(self, identifier, "bioSampleList", connection)

        # now get the complete object
        self.databaseFields = getObjectRecord(connection, "bioSampleList", self.databaseFields['obid'])


        # for this object type we need to get the members of the list
        sql = "select biosampleob from biosamplelistmembershiplink where biosamplelist = %s " % self.databaseFields['obid']
        #print "executing " + sql        
        obCursor = connection.cursor()
        obCursor.execute(sql)
        obFieldValues = obCursor.fetchall()
        self.databaseFields.update({'biosamples' : [item[0] for item in obFieldValues]})
        obCursor.close()


        
        self.obState.update({'ERROR' : 0 , 'NEW' : 0, 'MESSAGE' : "initialised from database OK"})


    def initNew(self,connection):
        """ method to initialise a new biosample object """
        self.databaseFields = {
            'obid' : getNewObid(connection),
            'xreflsid' : None,
            'listname' : None,
            'maxmembership' : None,
            'listcomment' : None
        } 
        self.obState.update({'DB_PENDING' : 1})

    def insertDatabase(self,connection):
        """ method used by bioSampleList object to save itself to database  """
            
        sql = """
           insert into biosamplelist
           (obid,listname,xreflsid,maxmembership,listcomment)
           values (%(obid)s,%(listname)s,%(xreflsid)s,%(maxmembership)s,%(listcomment)s)
           """
        modulelogger.info("executing %s"%(sql%self.databaseFields))
        insertCursor = connection.cursor()
        insertCursor.execute(sql,self.databaseFields)
        connection.commit()
        insertCursor.close()
        self.obState.update({'NEW' : 0 , 'ERROR' : 0, 'DB_PENDING' : 0, 'MESSAGE' : "database insert OK"})


    def addSample(self,connection,bioSample,inclusionComment=''):
        """ method for adding a sample to an existing samplelist """

        #check type
        if bioSample.__class__.__name__ != "bioSampleOb":
            self.obState.update({'ERROR' : 1 , 'MESSAGE' : "addSample called with arg type" + bioSample.__class__.__name__ + " - should be bioSampleOb"})
            raise brdfException, self.ObState['MESSAGE']

        # check list is in appropriate state
        if [self.obState[state] for state in ("NEW" , "DB_PENDING", "ERROR")] != [0,0,0]:
            self.obState.update({'MESSAGE' : "bioSampleList state does not permit adding a bioSample"})
            raise brdfException, self.obState['MESSAGE']

        self.obState.update({'DB_PENDING' : 1 , 'MESSAGE' : "adding sample"})

        sql = "insert into bioSampleListMembershipLink(biosamplelist,biosampleob,inclusionComment) \
                      values (%(biosamplelist)s,%(biosampleob)s,%(inclusionComment)s)"

        membershipFields= {\
            'biosamplelist' : self.databaseFields['obid'] ,
            'biosampleob' : bioSample.databaseFields['obid'],
            'inclusionComment' : inclusionComment
            }

        #print "executing " + sql%membershipFields
        
        insertCursor = connection.cursor()
        insertCursor.execute(sql,membershipFields)
        connection.commit()
        insertCursor.close()
        self.obState.update({'NEW' : 0 , 'DB_PENDING' : 0, 'MESSAGE' : "biosample added OK"})



class batchOb (ob ):
    """ batchOb objects represent batches """
    def __init__(self):
        ob.__init__(self)

        self.AboutMe['default'][0]['heading'] = 'BRDF Batch Object'
        self.AboutMe['default'][0]['text'] = """
        """                                

    def initFromDatabase(self, identifier, connection):
        """ method for initialising an object from database"""
          
        # initialise base fields from ob table
        ob.initFromDatabase(self, identifier,"batchOb",connection)

        # now get the complete object
        self.databaseFields = getObjectRecord(connection, "batchOb", self.databaseFields['obid'])
        
        self.obState.update({'ERROR' : 0 , 'NEW' : 0, 'MESSAGE' : "initialised from database OK"})

    def initNew(self,connection):
        """ method to initialise a new biosample object """
        self.databaseFields = {
            'obid' : getNewObid(connection) ,
            'batchname' : None,
            'xreflsid' : None,
            'batchtype' : None,
            'batchname' : None,
            'membershipcount' : 0,
            'batchdescription' : None,
            'batchkeywords' : None,
            'batchstatus' : None
        } 
        self.obState.update({'DB_PENDING' : 1})        

    def insertDatabase(self,connection):
        """ method used by batch object to save itself to database  """

        sql = """
        insert into batchOb(obid,batchname,xreflsid,batchtype,
        membershipcount,batchdescription,batchkeywords,batchstatus)
        values (%(obid)s,%(batchname)s,%(xreflsid)s,%(batchtype)s,
        %(membershipcount)s,%(batchdescription)s,%(batchkeywords)s,%(batchstatus)s)
        """
        #print "executing " + sql%self.databaseFields
        insertCursor = connection.cursor()
        insertCursor.execute(sql,self.databaseFields)
        connection.commit()
        insertCursor.close()
        self.obState.update({'NEW' : 0 , 'ERROR' : 0, 'DB_PENDING' : 0, 'MESSAGE' : "database insert OK"})

    def addNarration(self, connection, narrativenamespace, narrationname = None, narration = None, narrationdate = None , batchstatus = 0):
        """ method used to add a narration to a batch """
        sql = """
        insert into batchNarrativeFact(batchOb, narrativenamespace, narrationname, narration, narrationdate, batchstatus)
        values(%(batchob)s, %(narrativenamespace)s, %(narrationname)s, %(narration)s, %(narrationdate)s, %(batchstatus)s)
        """        
        insertCursor = connection.cursor()
        insertCursor.execute(sql,{"batchOb" : self.databaseFields["obid"], "narrativenamespace" : narrativenamespace, "narrationname" : narrationname, \
                                  "narration" : narration , "narrationdate" : narrationdate  , "batchstatus" : batchstatus })
        connection.commit()
        insertCursor.close()
        self.obState.update({'NEW' : 0 , 'ERROR' : 0, 'DB_PENDING' : 0, 'MESSAGE' : "sampling function insert OK"})



    def addFact(self,connection,argfactNameSpace, argattributeName, argattributeValue):
        factFields = {
            'batchOb' : self.databaseFields['obid'],
            'factNameSpace' : argfactNameSpace,
            'attributeName' : argattributeName,
            'attributeValue' : argattributeValue }

        # first check if this fact is already in the db - if it is do not duplicate
        sql = """
        select batchOb from batchFact where
        batchOb = %(batchOb)s and
        factNameSpace = %(factNameSpace)s and
        attributeName = %(attributeName)s and
        attributeValue = %(attributeValue)s
        """
        insertCursor = connection.cursor()
        modulelogger.info("checking for fact using %s"%(sql%factFields))
        insertCursor.execute(sql,factFields)
        insertCursor.fetchone()
        modulelogger.info("rowcount = %s"%insertCursor.rowcount)
        if insertCursor.rowcount == 0:        
            sql = """
            insert into batchFact(batchOb,factNameSpace, attributeName, attributeValue)
            values(%(batchOb)s,%(factNameSpace)s,%(attributeName)s,%(attributeValue)s)
            """
            modulelogger.info("executing %s"%(sql%factFields))
            insertCursor.execute(sql,factFields)
            connection.commit()
            insertCursor.close()
            self.obState.update({'NEW' : 0 , 'DB_PENDING' : 0, 'ERROR' : 0, 'MESSAGE' : "database insert OK"})
        else:
            insertCursor.close()


    # Changed memberob from type object to int. Helps if you add a member which does have no object representation. Helge: 15/10/2009
    def addBatchMember(self,connection, memberob = None, memberxref = None, membershiptype = "Batch Member", inclusioncomment = None, \
                       batchorder = None, addeddate = None, addedby = None, voptypeid = None, checkExisting = True) :
        # if necessary check if this member is already in the db - if it is do not duplicate
        doInsert = True

        detailsDict = {
            "xreflsid" : "%s%s"%(self.databaseFields["xreflsid"],{True : '', False : ":%s"%memberxref}[memberxref == None]),
            "batchob" : self.databaseFields["obid"],
            "memberob" : memberob,
            "memberxref" : memberxref,
            "membershiptype" : membershiptype,
            "inclusioncomment" :  inclusioncomment,
            "batchorder" : batchorder,
            "addeddate" : addeddate,
            "addedby" : addedby,
            "voptypeid" : voptypeid
        }


        insertCursor = connection.cursor()

        if checkExisting:
            if memberob != None:
                sql = """
                select memberob from batchNamedMembershipLink where
                batchob = %(batchob)s and memberob = %(memberob)s
                """
            elif memberxref == None:
                sql = """
                select memberob from batchNamedMembershipLink where
                batchob = %(batchob)s and memberxref = %(memberxref)s
                """
            else:
                raise brdfException("addBatchMember : must specify an internal or external member identifier")
                
            modulelogger.info("checking for batchmember using %s"%(sql%detailsDict))
            insertCursor.execute(sql, detailsDict)
            insertCursor.fetchone()
            modulelogger.info("rowcount = %s"%insertCursor.rowcount)
            if insertCursor.rowcount > 0:
                doInsert = False

        if doInsert:
            # set the listmembership type based on known list types, if we are not given a type
            #if voptype == None:
            #    if self.databaseFields['membershiptype'] == "something":
            #        queryDict['voptypeid'] = some op

            sql = """
            insert into batchNamedMembershipLink(xreflsid, batchob,memberob,memberxref,inclusioncomment,voptypeid, membershiptype, batchorder, addeddate, addedby)
            values(%(xreflsid)s,%(batchob)s,%(memberob)s,%(memberxref)s,%(inclusioncomment)s,%(voptypeid)s, %(membershiptype)s, %(batchorder)s, %(addeddate)s, %(addedby)s)            
            """
            modulelogger.info("executing %s"%(sql%detailsDict))
            insertCursor.execute(sql,detailsDict)
            connection.commit()
            self.obState.update({'NEW' : 0 , 'DB_PENDING' : 0, 'ERROR' : 0, 'MESSAGE' : "database insert OK"})

            
            # add to in-memory copies
            self.databaseFields['membershipcount'] += 1

            sql = """
            update batchob set membershipcount = %(membershipcount)s
            where
            obid = %(obid)s
            """
            insertCursor.execute(sql,self.databaseFields)
            connection.commit()
        

        insertCursor.close()
        
        
        




        

                

# oops ! defined in studymodule
#class bioProtocolOb (ob ):
#    """ bioProtocolOb objects represent bioprotocols """
#    def __init__(self):
#        ob.__init__(self)
#
#    def initFromDatabase(self, identifier, connection):
#    
#        # first init base class - this will get obid
#        ob.initFromDatabase(self, identifier, "bioProtocolOb", connection)
#
#        # now get the complete object
#        self.databaseFields = getObjectRecord(connection, "bioProtocolOb", self.databaseFields['obid'])
#        self.obState.update({'ERROR' : 0 , 'NEW' : 0, 'MESSAGE' : "initialised from database OK"})         
        
