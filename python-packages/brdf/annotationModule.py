#
# This module implements classes relating to annotation - comments, links
#
from types import *

from obmodule import ob, getNewObid,getObjectRecord
from brdfExceptionModule import brdfException
from opmodule import op

def makeComment(connection,OnOb,commentText,commentBy="system"):
    mycomment = commentOb()
    mycomment.initNew(connection)
    mycomment.databaseFields.update({
            "commentstring" : commentText,
            "createdby" : commentBy,
            "xreflsid" : "%(xreflsid)s:comment"%OnOb.databaseFields
            })
    mycomment.insertDatabase(connection)
    mycomment.createLink(connection, OnOb.databaseFields["obid"], commentBy)
    
            
def makeURL(connection,OnOb,urladdress,urltext,urlby="system"):
    myurl = uriOb()
    myurl.initNew(connection)
    myurl.databaseFields.update({
            "uristring" : urladdress,
            "createdby" : urlby,            
            "xreflsid" : urladdress
            })
    myurl.insertDatabase(connection)
    myurl.createLink(connection, OnOb.databaseFields["obid"], urltext, urlby)

class commentOb ( ob ) :
    """ comment objects """
    def __init__(self):
        ob.__init__(self)


    def initNew(self,connection):      
        self.obState.update({'NEW' : 1, 'DB_PENDING' : 1})

        self.databaseFields = {
            'obid' : getNewObid(connection) ,
            'createdby' : None,
            'commenttype' : None,
            'commentstring' : None,
            'xreflsid' : None,
            'visibility' : None,
            'commentedob' : None,
            'voptypeid' : None
        }


    def initFromDatabase(self, identifier, connection):
        """ method for initialising commentob from database """

        # first init base class - this will get obid
        ob.initFromDatabase(self, identifier, "commentOb", connection)

        # now get the complete object
        self.databaseFields = getObjectRecord(connection, "commentOb", self.databaseFields['obid'])

        # now get the objects this comment is linked to


        

    def insertDatabase(self,connection):
        """ method used by comment object to save itself to database  """
        sql = """
        insert into commentOb(obid,commentType, commentString,xreflsid,createdby,visibility,commentedob,voptypeid)
        values(%(obid)s,%(commenttype)s,%(commentstring)s,%(xreflsid)s,%(createdby)s,%(visibility)s,%(commentedob)s,%(voptypeid)s)
        """
        #print "executing " + sql%self.databaseFields
        insertCursor = connection.cursor()
        insertCursor.execute(sql,self.databaseFields)
        connection.commit()
        insertCursor.close()
        self.obState.update({'NEW' : 0 , 'ERROR' : 0, 'DB_PENDING' : 0, 'MESSAGE' : "database insert OK"})
        return

    def appendText(self,connection,newtext):
        """ method used by comment object to append text to comment  """
        sql = """
        update commentOb set commentString = commentString || '\r' || %(newtext)s
        where obid = %(obid)s
        """
        updateCursor = connection.cursor()
        updateCursor.execute(sql,{'newtext' : newtext, 'obid' : self.databaseFields['obid']})
        connection.commit()
        updateCursor.close()
        self.obState.update({'NEW' : 0 , 'ERROR' : 0, 'DB_PENDING' : 0, 'MESSAGE' : "database update OK"})
        return    


    def asHTMLTableRows(self,title='',width=600,context='default'):
        if context == 'default':
            return ob.asHTMLTableRows(self,title,width,context)
        elif context == 'briefsearchsummary':
            return ob.asHTMLTableRows(self,title,width,context)
        else:
            return ob.asHTMLTableRows(self,title,width,context)


    def createLink(self, connection, ob, commentby = None, style_bgcolour = "#EE9999"):
        """ method used to attach this comment to a database object """
        linkdetails = {
            'commentob' : self.databaseFields['obid'],
            'ob' : ob,
            'commentby' : commentby,
            'style_bgcolour' : style_bgcolour
        }
        sql = """
        insert into commentLink(commentob, ob, commentby,style_bgcolour)
        values(%(commentob)s,%(ob)s,%(commentby)s,%(style_bgcolour)s)
        """
        insertCursor = connection.cursor()
        insertCursor.execute(sql,linkdetails)
        connection.commit()
        insertCursor.close()
        self.obState.update({'NEW' : 0 , 'ERROR' : 0, 'DB_PENDING' : 0, 'MESSAGE' : "link insert OK"})
          
        
        
class uriOb ( ob ) :
    """ URL object """
    def __init__(self):
        ob.__init__(self)


    def initNew(self,connection):      
        self.obState.update({'NEW' : 1, 'DB_PENDING' : 1})

        self.databaseFields = {
            'obid' : getNewObid(connection) ,
            'createdby' : None,
            'uritype' : None,  # not currently initialised
            'uristring' : None,
            'xreflsid' : None,
            'visibility' : None,
            'uricomment' : None
        }


    def initFromDatabase(self, identifier, connection):
        """ method for initialising uriob from database """

        # first init base class - this will get obid
        ob.initFromDatabase(self, identifier, "uriOb", connection)

        # now get the complete object
        self.databaseFields = getObjectRecord(connection, "uriOb", self.databaseFields['obid'])

        # now get the objects this comment is linked to


        

    def insertDatabase(self,connection):
        """ method used by uri object to save itself to database  """
        sql = """
        insert into uriOb(obid,uriType, uriString,xreflsid,createdby,visibility,uricomment)
        values(%(obid)s,%(uritype)s,%(uristring)s,%(xreflsid)s,%(createdby)s,%(visibility)s,%(uricomment)s)
        """
        #print "executing " + sql%self.databaseFields
        insertCursor = connection.cursor()
        insertCursor.execute(sql,self.databaseFields)
        connection.commit()
        insertCursor.close()
        self.obState.update({'NEW' : 0 , 'ERROR' : 0, 'DB_PENDING' : 0, 'MESSAGE' : "database insert OK"})
        return


    def asHTMLTableRows(self,title='',width=600,context='default'):
        if context == 'default':
            return ob.asHTMLTableRows(self,title,width,context)
        elif context == 'briefsearchsummary':
            return ob.asHTMLTableRows(self,title,width,context)
        else:
            return ob.asHTMLTableRows(self,title,width,context)


    def createLink(self, connection, ob, displaystring, createdby = None,displayorder=0,iconpath=None,\
                   iconattributes=None,uricomment=None,linktype='URL'):
        """ method used to attach this uri to a database object """
        insertCursor = connection.cursor()

        linkdetails = {
            'uriob' : self.databaseFields['obid'],
            'ob' : ob,
            'displaystring' : displaystring,
            'createdby' : createdby,
            'displayorder' : displayorder,
            'iconpath' : iconpath,
            'uricomment' : uricomment,
            'linktype' : linktype,
            'iconattributes' : iconattributes
        }
        
        # check it is not already linked
        sql = """
        select uriob from urilink where
        uriob = %(uriob)s and
        ob = %(ob)s
        """
        insertCursor.execute(sql,linkdetails)
        rows=insertCursor.fetchone()
        if insertCursor.rowcount < 1:
            sql = """
            insert into uriLink(uriob, ob, displaystring, createdby,displayorder,iconpath,iconattributes,uricomment,linktype)
            values(%(uriob)s,%(ob)s,%(displaystring)s,%(createdby)s,%(displayorder)s,%(iconpath)s,%(iconattributes)s,%(uricomment)s,%(linktype)s)
            """
 
            insertCursor.execute(sql,linkdetails)
            connection.commit()
            self.obState.update({'NEW' : 0 , 'ERROR' : 0, 'DB_PENDING' : 0, 'MESSAGE' : "link insert OK"})

        insertCursor.close()
            

