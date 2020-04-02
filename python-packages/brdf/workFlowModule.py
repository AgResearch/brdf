#
# This module implements classes associated with the workflow module
#
#
from obmodule import getNewObid,getObjectRecord
from brdfExceptionModule import brdfException
from obmodule import ob
from opmodule import op


class staffOb (ob) :
    """ workFlow Ob """
    def __init__(self):
        ob.__init__(self)


    def initFromDatabase(self, identifier, connection):
        """ method for initialising staffOb from database"""

        # first init base class - this will get obid
        ob.initFromDatabase(self, identifier, "staffOb", connection)


        # now get the complete object
        self.databaseFields = getObjectRecord(connection, "staffOb", self.databaseFields['obid'])
        self.obState.update({'ERROR' : 0 , 'NEW' : 0, 'MESSAGE' : "initialised from database OK"})

    def initNew(self,connection):
        """ method to initialise a new biosubject object """
        self.databaseFields = {
            'obid' : getNewObid(connection) ,
            'loginname' :  None,
            'fullname' :   None,
            'emailaddress' : None,  
            'mobile' : None, 
            'phone' :  None,
            'title' : None,
            'staffcomment' : None,
            'xreflsid' : None
        } 
        self.obState.update({'DB_PENDING' : 1})

        

    def insertDatabase(self,connection):
        """ method used by staffOb object to save itself to database  """
        sql = """
        insert into staffOb(obid,loginname,fullname,emailaddress,mobile,phone,staffcomment,xreflsid)
        values (%(obid)s,%(loginname)s,%(fullname)s,%(emailaddress)s,%(mobile)s,%(phone)s,%(staffcomment)s,%(xreflsid)s)
        """
        #print "executing " + sql%self.databaseFields
        insertCursor = connection.cursor()
        insertCursor.execute(sql,self.databaseFields)
        connection.commit()
        insertCursor.close()
        self.obState.update({'NEW' : 0 , 'ERROR' : 0, 'DB_PENDING' : 0, 'MESSAGE' : "database insert OK"})
    

class workFlowOb ( ob ) :
    """ workFlow Ob """
    def __init__(self):
        ob.__init__(self)


    def initFromDatabase(self, identifier, connection):
        """ method for initialising workFlowOb from database"""

        # first init base class - this will get obid
        ob.initFromDatabase(self, identifier, "workFlowOb", connection)


        # now get the complete object
        self.databaseFields = getObjectRecord(connection, "workFlowOb", self.databaseFields['obid'])
        self.obState.update({'ERROR' : 0 , 'NEW' : 0, 'MESSAGE' : "initialised from database OK"})


class workFlowStageOb ( ob ) :
    """ workFlowStage Ob """
    def __init__(self):
        ob.__init__(self)


    def initFromDatabase(self, identifier, connection):
        """ method for initialising workFlowStageOb from database"""

        # first init base class - this will get obid
        ob.initFromDatabase(self, identifier, "workFlowStageOb", connection)


        # now get the complete object
        self.databaseFields = getObjectRecord(connection, "workFlowStageOb", self.databaseFields['obid'])
        self.obState.update({'ERROR' : 0 , 'NEW' : 0, 'MESSAGE' : "initialised from database OK"})        

class workStageVisitFact ( op ) :
    """ workStageVisitFact Op """
    def __init__(self):
        op.__init__(self)


    def initFromDatabase(self, identifier, connection):
        """ method for initialising workStageVisitFact from database"""

        # first init base class - this will get obid
        op.initFromDatabase(self, identifier, "workStageVisitFact", connection)


        # now get the complete object
        self.databaseFields = getObjectRecord(connection, "workStageVisitFact", self.databaseFields['obid'])
        self.obState.update({'ERROR' : 0 , 'NEW' : 0, 'MESSAGE' : "initialised from database OK"})        

