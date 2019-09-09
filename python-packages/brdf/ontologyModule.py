#
# This module implements classes associated with the workflow module
#
#
from obmodule import getNewObid,getObjectRecord
from brdfExceptionModule import brdfException
from obmodule import ob
from opmodule import op
import logging
import os
import globalConf

ontologymodulelogger = logging.getLogger('ontologymodule')
ontologymodulehdlr = logging.FileHandler(os.path.join(globalConf.LOGPATH,'ontologymodule.log'))
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
ontologymodulehdlr.setFormatter(formatter)
ontologymodulelogger.addHandler(ontologymodulehdlr) 
ontologymodulelogger.setLevel(logging.INFO)   


    

class ontologyOb ( ob ) :
    """ ontology Ob """
    def __init__(self):
        ob.__init__(self)

        self.AboutMe['default'][0]['heading'] = 'BRDF Ontology Object'
        self.AboutMe['default'][0]['text'] = """
        This page displays an ontology object from the BRDF database.
        <p>
        Ontologies are used extensively in the brdf schema to provide controlled
        vocabularies for database fields, and many on-insert and on-update triggers
        reference these ontologies.
        <p>
        Scientific ontologies such as Gene Ontologies, lists of Unigene accessions and taxonomy
        lists are also handled in the schema as ontologies.
        <p>
        Ontologies are also used to document system internals such as column names - there
        is an ontology for each table in the schema (these ontologies have names beginning
        with BRDF_)
        <p>
        Each ontology is described by a master record in the ontologyob table , while each term in the
        ontology is stored in a details table called ontologytermfact, represented in the information map
        by a line joining the ontology symbol, to a square box labelled info - clicking on this
        link will list all the terms in the ontology.
        <p>
        Each term in an ontology is a database object in its own right, and comments and hyperlinks may be
        attached to a term in an ontology as with any database object.
        """

    def initNew(self,connection):      
        self.obState.update({'NEW' : 1, 'DB_PENDING' : 1})

        self.databaseFields = {
            'obid' : getNewObid(connection) ,
            'ontologyname' : None,
            'ontologydescription' : None,
            'xreflsid' : None,
            'ontologycomment' : None
        }                         


    def initFromDatabase(self, identifier, connection):
        """ method for initialising ontologyOb from database"""

        # first init base class - this will get obid
        ob.initFromDatabase(self, identifier, "ontologyOb", connection)


        # now get the complete object
        self.databaseFields = getObjectRecord(connection, "ontologyOb", self.databaseFields['obid'])
        self.obState.update({'ERROR' : 0 , 'NEW' : 0, 'MESSAGE' : "initialised from database OK"})

    def insertDatabase(self,connection):
        """ method used by ontology object to save itself to database  """
        sql = """
        insert into ontologyob(obid,ontologyname,ontologydescription,xreflsid,ontologycomment)
        values(%(obid)s,%(ontologyname)s,%(ontologydescription)s,%(xreflsid)s,%(ontologycomment)s)
        """
        #print "executing " + sql%self.databaseFields
        insertCursor = connection.cursor()
        insertCursor.execute(sql,self.databaseFields)
        connection.commit()
        insertCursor.close()
        self.obState.update({'NEW' : 0 , 'ERROR' : 0, 'DB_PENDING' : 0, 'MESSAGE' : "database insert OK"})
        return

    def addTerm(self,connection,termname, checkexisting = True, termdescription = None, unitname=None,termcode=None):
        """ this method can be used to add a term to an ontology. The method will
        check that the term does not already exist, and will only add it if it does
        not exist, if the checkexisting parameter is True (set False if importing and
        sure there is no existing data, as this will speed up the transaction)
        """
        termDict = {
            'ontologyob' : self.databaseFields['obid'],
            'xreflsid' : "%s.%s"%(self.databaseFields['xreflsid'],termname),
            'termname' : termname,
            'termdescription' : termdescription,
            'unitname':  unitname,
            'termcode' : termcode
            }

        insertCursor = connection.cursor()
        if checkexisting:
            # if required check if this term is already in the db - if it is do not duplicate
            sql = """
            select obid from ontologytermfact where
            ontologyob = %(ontologyob)s and
            termname  = %(termname)s """
            ontologymodulelogger.info("checking for term using %s"%(sql%termDict))
            insertCursor.execute(sql,termDict)
            row = insertCursor.fetchone()
            ontologymodulelogger.info("rowcount = %s"%insertCursor.rowcount)
            if insertCursor.rowcount > 0:
                insertCursor.close()
                return (row[0],False) 

        # do the insert
        termDict.update ({
            'obid' : getNewObid(connection)
        })        
        sql = """
        insert into ontologytermfact(obid,ontologyob,xreflsid,termname,termdescription,
        unitname,termcode)
        values(%(obid)s,%(ontologyob)s,%(xreflsid)s,%(termname)s,
        %(termdescription)s,%(unitname)s,%(termcode)s)
        """
        ontologymodulelogger.info("executing %s"%(sql%termDict))
        insertCursor.execute(sql,termDict)
        connection.commit()
        insertCursor.close()
        self.obState.update({'NEW' : 0 , 'DB_PENDING' : 0, 'ERROR' : 0, 'MESSAGE' : "database insert OK"})
        return (termDict['obid'],True)
    
    

class ontologyTermFact ( op ) :
    """ ontologyTermFact """
    def __init__(self):
        op.__init__(self)

        self.AboutMe['default'][0]['heading'] = 'BRDF Ontology Term Object'
        self.AboutMe['default'][0]['text'] = """
        This page displays a term in an ontology.
        <p>
        Ontologies are used extensively in the brdf schema to provide controlled
        vocabularies for database fields, and many on-insert and on-update triggers
        reference these ontologies.
        <p>
        Scientific ontologies such as Gene Ontologies, lists of Unigene accessions and taxonommy
        lists are also handled in the schema as ontologies.
        <p>
        Ontologies are also used to document system internals such as column names - there
        is an ontology for each table in the schema (these ontologies have names beginning
        with BRDF_), and each column is a term in the ontology.
        <p>
        Each ontology is described by a master record in the ontologyob table , while each term in the
        ontology is stored in a details table called ontologytermfact, represented in the information map
        by a line joining the ontology symbol, to a square box labelled info.
        <p> From this page you can
        click the ontology symbol (an open book) in the information map, to go up one level to the
        ontology containing this term. From the master ontology page you can then click the info link in the
        information map, to report all the other terms in the ontology that are siblings of the one displayed
        on this page.
        <p>
        Each term in an ontology is a database object in its own right, and comments and hyperlinks may be
        attached to a term in an ontology as with any database object.
        <p>
        Terms may be further annotated using the ontologytermfact1 table, which records arbitrary key-value
        atttributes of individual terms.
        """
        


    def initFromDatabase(self, identifier, connection):
        """ method for initialising ontologyTermFact from database"""

        # first init base class - this will get obid
        ob.initFromDatabase(self, identifier, "ontologyTermFact", connection)


        # now get the complete object
        self.databaseFields = getObjectRecord(connection, "ontologyTermFact", self.databaseFields['obid'])
        self.obState.update({'ERROR' : 0 , 'NEW' : 0, 'MESSAGE' : "initialised from database OK"})        
        
