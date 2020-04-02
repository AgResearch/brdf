#
# This module implements classes relating to lists
#
from types import *
import logging

from obmodule import getNewObid,getObjectRecord
from brdfExceptionModule import brdfException
from opmodule import op
from obmodule import ob
from htmlModule import tidyout
import os
import re
import globalConf

listmodulelogger = logging.getLogger('listmodule')
listmodulehdlr = logging.FileHandler(os.path.join(globalConf.LOGPATH,'listmodule.log'))
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
listmodulehdlr.setFormatter(formatter)
listmodulelogger.addHandler(listmodulehdlr) 
listmodulelogger.setLevel(logging.INFO)        




#######################################################
# this class is a wrapper for the list object.
#######################################################

class obList ( ob ) :
    """ a list of objects """
    def __init__(self):
        ob.__init__(self)
        self.listChunkLink=None
        self.listAboutLink=' '
        self.fastaURL = None
        self.genbankURL = None
        



    def initNew(self,connection):

        self.databaseFields = {
            'obid' : getNewObid(connection) ,
            'xreflsid' : None,
            'listname' : None,
            'listtype' : None,
            'listdefinition' : None,
            'bookmark' : None,
            'maxmembership' : 1000000,
            'currentmembership' : 0,
            'listcomment' : None,
            'createdby' : None,
            'obkeywords' : None,
            'displayurl' : 'ob.gif',
            'listitems' : []  ,         # this is subject to chunk processing and will contain "pages" of items
            'alllistitems' : []        # this will contain all list items
            }
        self.chunkSize = 1000
        self.obState.update({'NEW' : 1})




    def initFromDatabase(self, identifier, connection, startAtItem = 0, maxItems = 15, asSet = True):
        """ method for initialising list from database,

        The asSet option causes the list to prune identical obids after loading - i.e. so that it ends
        up being a set (no duplcates) rather than a list. This is
        mainly as a workaround for the lack of adequate array support in the current postgres
        database  - in version 8.0.3 we can easily and efficiently ensure that we do not insert duplicate
        obids into a list, however this code does not work in 7.4.3 - the array assignments execute without
        error , however the code using these assignments does not produce expected results. Once the db is upgraded , then
        code like this can be used in the search function :

create function testarray(integer) returns integer as '
declare
   intarg alias for $1;
   intarray int[];
   result int;
begin
   intarray[0] := 2;
   intarray[1] := 4;
   intarray[2] := 6;
   intarray[3] := 8;
   if not intarg = ANY(intarray) then
      result = intarg;
   else
      result = 0;
   end if;
   return result;
END;
' LANGUAGE plpgsql;

(note that it is assumed we can't use naive SQL to avoid duplicate entries .....insert into .... and not in ....
due to the potential performance problems this would cause.

"""
        self.chunkSize = maxItems

        # first init base class - this will get obid
        ob.initFromDatabase(self, identifier, "obList", connection)

        # now get the complete object
        self.databaseFields = getObjectRecord(connection, "obList", self.databaseFields['obid'])

        # for this object type we need to get the members of the list. We get the obid and listorder for
        # up to maxItems members of the list, in the order specified by listOrder. 
        #sql = "select l.ob,l.listorder,o.xreflsid from ob o,listmembershiplink l where l.oblist = %s and l.listorder >= %s and o.obid = l.ob order by listorder" % (self.databaseFields['obid'],maxItems)
        if not asSet:        
            sql = """
            select
               l.ob,
               l.listorder,
               l.obxreflsid,
               l.membershipcomment
            from
               listmembershiplink l
            where
               l.oblist = %s and
               l.listorder >= %s
               order by listorder""" % (self.databaseFields['obid'],startAtItem)
        else:
            sql = """
            select
               l.ob,
               l.listorder,
               l.obxreflsid,
               l.membershipcomment
            from
               listmembershiplink l
            where
               l.oblist = %s 
               order by listorder""" % (self.databaseFields['obid'])
            
        listmodulelogger.info("list executing %s"%sql)
        
        
        obCursor = connection.cursor()
        obCursor.execute(sql)
        if not asSet:
            obFieldValues = obCursor.fetchall()
            self.databaseFields.update({'alllistitems' : [(item[0],item[1],item[2],item[3]) for item in obFieldValues]})
            #obFieldValues = obCursor.fetchmany(maxItems)
            self.databaseFields.update({'listitems' : [(item[0],item[1],item[2],item[3]) for item in obFieldValues[0:maxItems]]})
            self.obState.update({'LIST_MODE' : 'LIST'})            
        else:
        # if we are to make a set , then do so. A problem is that we do not know the size of the
        # set (as a set rather than as a list) - but this is needed by the user interface to
        # figure out how many pages to display - so need to get wholelist
            listmodulelogger.info("creating a set ")
            setDict = {}
            row = obCursor.fetchone()
            listmodulelogger.info("row count = %d"%obCursor.rowcount)
            listmodulelogger.info("fetched  %s"%str(row))
            self.databaseFields['alllistitems'] = []            
            # update 5/2012 - psycopg driver leaves rowcount set to
            # 1 when fetching past the last record :-(
            #while obCursor.rowcount == 1
            while obCursor.rowcount >= 1 and row != None:
                item  = tuple(row)
                self.databaseFields['alllistitems'].append(item)
                setDict[item[0]] = (item[1],item[2],item[3])
                row = obCursor.fetchone()

            # sort the set by list order and get a chunk, starting from startAtItem
            listmodulelogger.info("sorting and selecting bookmarks > %s chunk size %s"%(startAtItem,maxItems))
            setKeys = setDict.keys()
            setKeys.sort(lambda x,y:setDict[x][0] - setDict[y][0])
            chunkDict = {}
            for i in range(0,len(setDict)):
                #listmodulelogger.info("checking %s"%str(setDict[setKeys[i]]))
                if (int(setDict[setKeys[i]][0]) >= int(startAtItem)) and (len(chunkDict) < maxItems):
                    #listmodulelogger.info("selecting %s"%str(setDict[setKeys[i]]))
                    chunkDict[setKeys[i]] = setDict[setKeys[i]]

            #listmodulelogger.info(str(chunkDict))
            
                
            self.databaseFields.update(
                {
                    'listitems' : [(key,chunkDict[key][0],chunkDict[key][1],chunkDict[key][2]) for key in chunkDict.keys()],
                    'currentmembership' : len(setDict)
                })
            self.obState.update({'LIST_MODE' : 'SET'})


        obCursor.close()

        self.obState.update({'ERROR' : 0 , 'NEW' : 0, 'MESSAGE' : "initialised from database OK"})              
        
            
    def insertDatabase(self,connection):
        """ method used by list object  to save itself to database  """
        
        sql = """
        insert into oblist (obid, xreflsid, obkeywords,createdby,
            listname,listtype,listdefinition,bookmark,
            maxmembership,currentmembership,listcomment,displayurl)
        values (%(obid)s, %(xreflsid)s, %(obkeywords)s,%(createdby)s,
            %(listname)s,%(listtype)s,%(listdefinition)s,%(bookmark)s,
            %(maxmembership)s,%(currentmembership)s,%(listcomment)s,%(displayurl)s)
        """        
        #sql = """
        #insert into oblist (obid, xreflsid,
        #    listname,listtype,listdefinition,bookmark,
        #    maxmembership,currentmembership,listcomment)
        #values (%(obid)s, %(xreflsid)s,
        #    %(listname)s,%(listtype)s,%(listdefinition)s,%(bookmark)s,
        #    %(maxmembership)s,%(currentmembership)s,%(listcomment)s)
        #"""            
        listmodulelogger.info("executing " + sql%self.databaseFields)
        insertCursor = connection.cursor()
        insertCursor.execute(sql,self.databaseFields)
        connection.commit()
        insertCursor.close()
        self.obState.update({'NEW' : 0 , 'ERROR' : 0, 'DB_PENDING' : 0, 'MESSAGE' : "database insert OK"})


    def saveMembershipList(self,connection,voptype=None,checkExisting = True):
        # save the membership list of an object to the database
        insertCursor = connection.cursor()
        for (ob, listorder, obxreflsid, membershipcomment) in self.databaseFields['alllistitems']: #listmember is a tuple l.ob,l.listorder,l.obxreflsid,l.membershipcomment
            doInsert = True

            queryDict = {
                'oblist' : self.databaseFields['obid'],
                'ob' : ob,
                'obxreflsid' : obxreflsid,
                'membershipcomment' : membershipcomment,
                'voptypeid' : voptype
            }        

            if checkExisting:
                sql = """
                select ob from listmembershiplink where
                oblist = %(oblist)s and ob = %(ob)s
                """
                    
                listmodulelogger.info("checking for listmember using %s"%(sql%queryDict))
                insertCursor.execute(sql%queryDict)
                insertCursor.fetchone()
                listmodulelogger.info("rowcount = %s"%insertCursor.rowcount)
                if insertCursor.rowcount > 0:
                    doInsert = False

            if doInsert:
                # set the listmembership type based on known list types, if we are not given a type
                if voptype == None:
                    if self.databaseFields['listtype'] == "BIOSEQUENCE_LIST":
                        queryDict['voptypeid'] = 26
                    elif self.databaseFields['listtype'] == "BIOSUBJECT_LIST":
                        queryDict['voptypeid'] = 27
                    elif self.databaseFields['listtype'] == "DATASOURCE_LIST":
                        queryDict['voptypeid'] = 29                        

                sql = """
                insert into listmembershiplink(oblist,ob,obxreflsid,membershipcomment,voptypeid)
                values(%(oblist)s,%(ob)s,%(obxreflsid)s,%(membershipcomment)s,%(voptypeid)s)
                """
                listmodulelogger.info("executing %s"%(sql%queryDict))
                insertCursor.execute(sql,queryDict)
                connection.commit()
                self.obState.update({'NEW' : 0 , 'DB_PENDING' : 0, 'ERROR' : 0, 'MESSAGE' : "database insert OK"})

                self.databaseFields['currentmembership'] = len(self.databaseFields['alllistitems'])

                sql = """
                update oblist set currentmembership = %(currentmembership)s
                where
                obid = %(obid)s
                """
                insertCursor.execute(sql,self.databaseFields)
                connection.commit()
        

        insertCursor.close()
                


    def myHTMLSummary(self, table, width=800,context='default'):
        """ descendants of the ob class will usually override this method rather than the
        entire asHTMLRows method - this method supplies the contents of the summary
        panel
        """
        FieldItems = [item for item in self.databaseFields.items() if not isinstance(item[1],ListType)]
        ListItems = [item for item in self.databaseFields.items() if isinstance(item[1],ListType) and len(item[1]) > 0]           
        ListDictionaryItems = [item for item in ListItems if isinstance(item[1][0],DictType)]
        ListOtherItems = [item for item in ListItems if not isinstance(item[1][0],DictType)]        
        nonSystemFieldRows =  reduce(lambda x,y:x+y, ['<tr><td class=fieldname>'+self.getColumnAlias(key)+'</td><td class=fieldvalue>'+tidyout(str(value), 80, 1,'<br/>')[0]+'</td></tr>\n' \
                                                   for key,value in FieldItems if not key in ( \
                                        'obid','obtypeid','createddate','createdby','lastupdateddate',\
                                        'lastupdatedby','checkedout','checkedoutby','checkoutdate','obkeywords','statuscode') and self.getColumnAlias(key) != None])
        nonSystemFieldRows = '<tr><td class=inside colspan="2"><table class=inside border="0">' + nonSystemFieldRows + '</table></td></tr>'
        # Format output for values that are lists of dictionaries
        # in the next line, the inner reduction concatenates the keys and values for a dictionary - e.g. a single
        # function or location , for a gene object.
        # the next reduction out concatnates these for each dictionary in the list (i.e. each location, function or whatever etc)
        # the final reduction concatenates each category name with all the above - e.g function : location : etc     
        ListDictionaryRows = ''
        if len(ListDictionaryItems) > 0 :
            ListDictionaryRows =  reduce(lambda x,y:x+y, ['<tr><td><b>'+key +'</b></td><td>'+\
                                '<table>'+ \
                                    reduce(lambda x,y:x+y , [ \
                                        reduce(lambda x,y:x+y, ['<tr><td><i>'+nestedkey+'</i></td><td><b>'+\
                                                str(nestedvalue)+'</b></td></tr>\n' \
                                        for nestedkey,nestedvalue in nestedDict.items()]) + '<p/>' \
                                    for nestedDict in value ]) + \
                                '</table>' + \
                                '</td></tr>\n' \
                                  for key,value in ListDictionaryItems])
        ListOtherRows = ''
        if len(ListOtherItems) > 0:
            ListOtherRows = reduce(lambda x,y:x+y, ['<tr><td>'+key+'</td><td>'+str(value)+'</td></tr>\n' for key,value in ListOtherItems])


        if self.obState['DYNAMIC_ANALYSES'] > 0:
            #selectlisttuples = ["<option value=%s> %s : %s </option>"%(item[9], item[3], item[1]) for item in self.analysisFunctions ]
            selectlisttuples = ["<option value=%s selected> %s : %s </option>"%(item[9], item[3], item[1]) for item in [self.analysisFunctions[0]] ]
            if len(self.analysisFunctions) > 1:
                selectlisttuples = ["<option value=%s> %s : %s </option>"%(item[9], item[3], item[1]) for item in self.analysisFunctions[1:] ]
            
            selectlisthtml = """
            <tr>
            <td colspan=2 align=center>
            <font size="-1"> (to select multiple analyses press the control key and click. To select a block use the shift key and click) </font> <p/>
            <select name="analyses" id="analyses" multiple size=4>
            """\
            +reduce(lambda x,y:x+y+'\n',selectlisttuples,'')\
            + """
            </select>
            <p/>
            <input value="Run Analyses" type="button" id="runanalyses" onclick='multipost("%s","analyses","fetchedanalyses","context=%s&amp;obid=%s&amp;functioninstance=","%s","%s",this)'></p>         

            <p/>
            </td>
            </tr>
            """%(self.analysisfetcher,context,self.databaseFields['obid'],self.waitURL,self.waiter)

            table += """
                <tr> <td colspan="2" class=tableheading> 
                %s
                </td>
                </tr>
                """%"Run selected analyses"                    
            table +=   selectlisthtml
            table += """
                    <tr>
                    <td>
                    <div id="fetchedanalyses">
                    </div>
                    </td>
                    </tr>
                """            

        if self.obState['DYNAMIC_DISPLAYS'] > 0:
            listmodulelogger.info('running non-virtual display functions')
            for displayFunction in self.displayFunctions:
                # exclude virtual functions - these will be instantiated in specific contexts or subclasses
                if displayFunction[7] == None:
                    listmodulelogger.info('running %s'%displayFunction[0])
                    myGraphHTML = eval(displayFunction[0])
                    table += myGraphHTML        

        
        listmodulelogger.info('listing dictionaries')
        # if we have formatted dictionaries , output these first , they are usually the most interesting
        # content of the object
        if len(ListDictionaryRows) >  0:
            table += ListDictionaryRows

        listmodulelogger.info('listing fields')
        # next the field rows
        table += nonSystemFieldRows

        listmodulelogger.info('listing lists')
        # next the other lists
        if len(ListOtherRows) > 0:
            table += ListOtherRows

        return table
        

        

    def addListMember(self,targetob,comment,connection,voptype=None,checkExisting = True):
        # if necessary check if this feature is already in the db - if it is do not duplicate
        doInsert = True

        insertCursor = connection.cursor()

        queryDict = {
            'oblist' : self.databaseFields['obid'],
            'ob' : targetob.databaseFields['obid'],
            'obxreflsid' : targetob.databaseFields['xreflsid'],
            'membershipcomment' : comment,
            'voptypeid' : voptype
        }        

        if checkExisting:
            sql = """
            select ob from listmembershiplink where
            oblist = %(oblist)s and ob = %(ob)s
            """
                
            listmodulelogger.info("checking for listmember using %s"%(sql%queryDict))
            insertCursor.execute(sql%queryDict)
            insertCursor.fetchone()
            listmodulelogger.info("rowcount = %s"%insertCursor.rowcount)
            if insertCursor.rowcount > 0:
                doInsert = False

        if doInsert:
            # set the listmembership type based on known list types, if we are not given a type
            if voptype == None:
                if self.databaseFields['listtype'] == "BIOSEQUENCE_LIST":
                    queryDict['voptypeid'] = 26
                elif self.databaseFields['listtype'] == "BIOSUBJECT_LIST":
                    queryDict['voptypeid'] = 27

            sql = """
            insert into listmembershiplink(oblist,ob,obxreflsid,membershipcomment,voptypeid)
            values(%(oblist)s,%(ob)s,%(obxreflsid)s,%(membershipcomment)s,%(voptypeid)s)
            """
            listmodulelogger.info("executing %s"%(sql%queryDict))
            insertCursor.execute(sql,queryDict)
            connection.commit()
            self.obState.update({'NEW' : 0 , 'DB_PENDING' : 0, 'ERROR' : 0, 'MESSAGE' : "database insert OK"})

            
        # add to in-memory copies
        self.databaseFields['listitems'].append( (queryDict['ob'],len(self.databaseFields['listitems']) , queryDict['obxreflsid'], queryDict['membershipcomment']) )
        self.databaseFields['alllistitems'].append( (queryDict['ob'],len(self.databaseFields['alllistitems']) , queryDict['obxreflsid'], queryDict['membershipcomment']) )
        self.databaseFields['currentmembership'] += 1

        sql = """
        update oblist set currentmembership = %(currentmembership)s
        where
        obid = %(obid)s
        """
        insertCursor.execute(sql,self.databaseFields)
        connection.commit()
        

        insertCursor.close()



    def addWeakListMember(self,memberid,comment,connection,voptype=None,checkExisting = True):
        # if necessary check if this member is already in the db - if it is do not duplicate
        doInsert = True

        insertCursor = connection.cursor()

        queryDict = {
            'oblist' : self.databaseFields['obid'],
            'memberid' : memberid,
            'membershipcomment' : comment,
            'voptypeid' : voptype
        }        

        if checkExisting:
            sql = """
            select memberid from listmembershipfact where
            oblist = %(oblist)s and memberid = %(memberid)s
            """
                
            listmodulelogger.info("checking for listmember using %s"%(sql%queryDict))
            insertCursor.execute(sql%queryDict)
            insertCursor.fetchone()
            listmodulelogger.info("rowcount = %s"%insertCursor.rowcount)
            if insertCursor.rowcount > 0:
                doInsert = False

        if doInsert:
            # set the listmembership type based on known list types, if we are not given a type
            if voptype == None:
                if self.databaseFields['listtype'] == "BIOSEQUENCE_LIST":
                    queryDict['voptypeid'] = 26
                elif self.databaseFields['listtype'] == "BIOSUBJECT_LIST":
                    queryDict['voptypeid'] = 27

            sql = """
            insert into listmembershipfact(oblist,memberid,membershipcomment,voptypeid)
            values(%(oblist)s,%(memberid)s,%(membershipcomment)s,%(voptypeid)s)
            """
            listmodulelogger.info("executing %s"%(sql%queryDict))
            insertCursor.execute(sql,queryDict)
            connection.commit()
            self.obState.update({'NEW' : 0 , 'DB_PENDING' : 0, 'ERROR' : 0, 'MESSAGE' : "database insert OK"})

            
        # add to in-memory copies (do not distinguish strong from weak list membership
        self.databaseFields['listitems'].append( (None,len(self.databaseFields['listitems']) , queryDict['memberid'], queryDict['membershipcomment']) )
        self.databaseFields['alllistitems'].append( (None,len(self.databaseFields['alllistitems']) , queryDict['memberid'], queryDict['membershipcomment']) )
        self.databaseFields['currentmembership'] += 1

        sql = """
        update oblist set currentmembership = %(currentmembership)s
        where
        obid = %(obid)s
        """
        insertCursor.execute(sql,self.databaseFields)
        connection.commit()
        

        insertCursor.close()
               

    def asHTMLTableRow(self,title='',width=200,context='default',view='default',page=1):
        if context == 'default':
            return ob.asHTMLTableRows(self,title,600,context)    # oops ! there is no such method  - this method neve called in default context so far      
        elif context in ['briefsearchsummary','briefsearchsummarypage']:
            # the following standard fields from databaseFields are used to generate the table :
            #listdefinition mutase$1000$MICROARRAYSPOTFACT 
            #listitems [(772, 345, 'NM_011435','comment'), (1356, 346, 'AV261043','comment'), (3600, 347, 'AA120574'), (5795, 348, 'NM_016881'), (5821, 349, 'AA120574'), (6123, 350, 'AA120574'), (6376, 351, 'AK014332'), (7761, 352, 'NG_001501.1'), (8103, 353, 'AK004631'), (8246, 354, 'AA120574'), (8881, 355, 'AK009905'), (8915, 356, 'AA120574'), (11467, 357, 'AA120574'), (11476, 358, 'AA120574'), (11714, 359, 'BC002066'), (11899, 360, 'NM_007563'), (12366, 361, 'NM_016892'), (13103, 362, 'AK035507'), (13732, 363, 'AK036082'), (14487, 364, 'NM_013671')]
            #currentmembership
            #maxmembership
            #
            # in addition it is assumed that a field called url has been added to each tuple so that we have (e.g.)
            # [(772,345,'NM_011435',comment,'http://localhost/nutrigenomics/NuNZWeb/fetch.py?obid=772&context=dump')]
            
            #self.logger.info("about to format databaseFields : ")
            #self.logger.info(str(self.databaseFields))

            # get the object links to display
            if len(self.databaseFields['listitems']) > 0:
            #    if len([item for item in self.databaseFields['listitems'] if item[3] != None]) > 0:

               # this assumes the list membership has been kitted out with call-back URL's , i.e.
               # itemtuple[4]. Sanity check this callback
               def urlpatch(urlfrag):
                   if re.search("\&target\=ob",urlfrag) != None:
                       return ">"
                   else:
                       return "&target=ob>"
                    
               row =  """
               <table>
               <tr><td colspan="3"><table>
               """ + \
               reduce(lambda x,y:x+y, ['<tr><td><a href='+itemtuple[4]+urlpatch(itemtuple[4])+itemtuple[2]+'</a></td><td>' + \
               eval({True : "''", False : "itemtuple[3]"}[itemtuple[3] == None]) + \
               '</td></tr>\n'  for itemtuple in self.databaseFields['listitems']],'') + \
               """
               </table></td></tr>
               </table>
               """
            #    else:
            #        row = reduce(lambda x,y:x+y, ['&nbsp;&nbsp;&nbsp;<a href='+itemtuple[4]+'&target=ob>'+itemtuple[2]+'</a>\n'  for itemtuple in self.databaseFields['listitems']],'')
            #
            else:
               row = ''



            # get the link to the next chunk
            #
            # get the maximum value of listorder to construct a URL to retrive the next chunkSize items
            # is is assumed that a variable called nextChunkURL has been initialised in this object - e.g.
            # http://localhost/nutrigenomics/NuNZWeb/fetch.py?obid=%s&context=list&bookmark=%s
            if len(self.databaseFields['listitems']) > 0:
                maxListOrder = max([tuple[1] for tuple in self.databaseFields['listitems']])
            else:
                maxListOrder = None
                
            if len(self.databaseFields['listitems']) == self.chunkSize and self.listChunkLink != None :
                nextlink = '<a href="%s"> Next Page</a>'%(self.listChunkLink%(str(self.databaseFields['obid']),str(maxListOrder),view,page))
                nextdisplay = "Next Page"
                listmodulelogger.info("debug nextlink : %s"%nextlink)                
                #nextlink = "zzzz"
            else:
                nextlink = "(No more pages)"


            # if appropriate , set up URLs that will dump the list in FASTA or Genbank format
            listmodulelogger.info("checking for sequence list...")
            typeContent = ""
            if self.obState['METADATA'] > 0:
                if self.databaseFields['listtype'] == 'BIOSEQUENCE_LIST':
                    if self.fastaURL != None:
                        typeContent = """
                        <p/>
                        <a href="%s" target=fastaDump> Download entire list as FASTA </a>
                        """%self.fastaURL%self.databaseFields['obid']

                    if self.genbankURL != None:
                        typeContent += """
                        <p/>
                        <a href="%s"> Download entire list as Genbank / open in Viewer </a>
                        """%self.genbankURL%self.databaseFields['obid']
                        
                           
            table = """
               <tr>
               <td>
               <img src="%s" usemap="#obtypelink" border="0" height="42" width="42"/>
               </td>
               <td align=left>
               %s
               %s
               </td>
               <td align=left>
               <font size="-1">
               %s
               </font>
               </td>
               <td>
               %s
               </td>
               <td>
               %s
               </td>
               <!--
               <td>
               <a class="CSSEditButton" href="/zz_contents.htm">Add</a>
               </td>
               -->
               </tr>
               <map name="obtypelink" id="obtypelink">
               <area nohref
               shape="rect"
               coords="0,0,42,42"
               alt="Describe this object"
               target="obdescription"/>
               </map>
               """%(self.listAboutLink,title,typeContent,row,str(self.databaseFields['currentmembership']),nextlink)

            listmodulelogger.info("returning %s"%table)

                

            return table
        else:
            return ob.asHTMLTableRows(self,title,width,context)


    def addFact(self,connection,argfactNameSpace,argattributeName,argattributeValue,checkExisting=True):
        factFields = {
            'listOb' : self.databaseFields['obid'],
            'factNameSpace' : argfactNameSpace,
            'attributeName' : argattributeName,
            'attributeValue' : argattributeValue }

        doinsert = True
        insertCursor = connection.cursor()

        # first check if this fact is already in the db - if it is do not duplicate (if asked to do this)
        if checkExisting:
            sql = """
            select listOb from obListFact where
            listOb = %(listOb)s and
            factNameSpace = %(factNameSpace)s and
            attributeName = %(attributeName)s and
            attributeValue = %(attributeValue)s
            """
            #listmodulelogger.info("checking for fact using %s"%(sql%factFields))
            insertCursor.execute(sql,factFields)
            insertCursor.fetchone()
            #listmodulelogger.info("rowcount = %s"%insertCursor.rowcount)
            if insertCursor.rowcount == 0:
                doinsert = True
            else:
                doinsert = False

        if doinsert:
            sql = """
            insert into obListFact(listOb,factNameSpace, attributeName, attributeValue)
            values(%(listOb)s,%(factNameSpace)s,%(attributeName)s,%(attributeValue)s)
            """
            #listmodulelogger.info("executing %s"%(sql%factFields))
            insertCursor.execute(sql,factFields)
            connection.commit()
            insertCursor.close()
            self.obState.update({'NEW' : 0 , 'DB_PENDING' : 0, 'ERROR' : 0, 'MESSAGE' : "database insert OK"})
        else:
            insertCursor.close()




#
# fact extension of the basic list class to store gene expression experiments
class geneExpressionExperimentSeriesFact (op) :
    def __init__(self):
        op.__init__(self)

    def initNew(self,connection):

        self.databaseFields = {
            'obid' : getNewObid(connection) ,
            'xreflsid' : None,
            'createdby' : None,
            'obkeywords' : None,
            'listob' : None,
            'experimenttitle' : None,
            'experimentseriestype' : None,
            'experimentplatforms' : None,
            'experimentsummary' : None,
            'experimentdesign' : None,
            #'r_targetfile' : None,
            #'r_misc' : None,
            'contributors' : None
            }
        self.obState.update({'NEW' : 1, 'DB_PENDING' : 1})        

    def initFromDatabase(self, identifier, connection):
        """ method for initialising geneExpressionExperimentSeriesFact from database"""

        # first init base class - this will get obid
        ob.initFromDatabase(self, identifier, "geneExpressionExperimentSeriesFact", connection)

        # now get the complete object
        self.databaseFields = getObjectRecord(connection, "geneExpressionExperimentSeriesFact", self.databaseFields['obid'])

        self.obState.update({'ERROR' : 0 , 'NEW' : 0, 'DB_PENDING' : 0, 'MESSAGE' : "initialised from database OK"})

    def insertDatabase(self,connection):
        """ method used by object  to save itself to database  """
        
        sql = """
        insert into geneExpressionExperimentSeriesFact(obid,xreflsid,createdby,obkeywords,listob,
                experimenttitle,experimentseriestype,experimentplatforms, experimentsummary,
                experimentdesign,contributors) 
        values (%(obid)s,%(xreflsid)s,%(createdby)s,%(obkeywords)s,%(listob)s,%(experimenttitle)s,
                %(experimentseriestype)s,%(experimentplatforms)s,%(experimentsummary)s,
                %(experimentdesign)s,%(contributors)s)"""        
        listmodulelogger.info("executing " + sql%self.databaseFields)
        insertCursor = connection.cursor()
        insertCursor.execute(sql,self.databaseFields)
        connection.commit()
        insertCursor.close()
        self.obState.update({'NEW' : 0 , 'ERROR' : 0, 'DB_PENDING' : 0, 'MESSAGE' : "database insert OK"})


class namedListMembershipLink (op) :
    def __init__(self):
        op.__init__(self)

    def initNew(self,connection):

        self.databaseFields = {
            'obid' : getNewObid(connection) ,
            'xreflsid' : None,
            'oblist' : None,
            'ob' : None
            }
        self.obState.update({'NEW' : 1, 'DB_PENDING' : 1})        

    def initFromDatabase(self, identifier, connection):
        """ method for initialising namedListMembershipLink from database"""

        # first init base class - this will get obid
        ob.initFromDatabase(self, identifier, "namedListMembershipLink", connection)

        # now get the complete object
        self.databaseFields = getObjectRecord(connection, "namedListMembershipLink", self.databaseFields['obid'])

        self.obState.update({'ERROR' : 0 , 'NEW' : 0, 'DB_PENDING' : 0, 'MESSAGE' : "initialised from database OK"})

    def insertDatabase(self,connection):
        """ method used by object  to save itself to database  """
        
        sql = """
        insert into namedListMembershipLink(obid,xreflsid,oblist,ob)
        values (%(obid)s,%(xreflsid)s,%(oblist)s,%(ob)s)"""        
        listmodulelogger.info("executing " + sql%self.databaseFields)
        insertCursor = connection.cursor()
        insertCursor.execute(sql,self.databaseFields)
        connection.commit()
        insertCursor.close()
        self.obState.update({'NEW' : 0 , 'ERROR' : 0, 'DB_PENDING' : 0, 'MESSAGE' : "database insert OK"})
        

            
        
        
            
        
#######################################################
# this class is a wrapper for the predicateLink object.
#######################################################

class predicateLink ( ob ) :
    """ a link between objects """
    def __init__(self):
        ob.__init__(self)


    def initNew(self,connection):

        self.databaseFields = {
            'obid' : getNewObid(connection) ,
            'xreflsid' : None,
            'createdby' : None,
            'obkeywords' : None,
            'subjectob' : None,
            'objectob' : None,
            'predicate' : None,
            'predicatecomment' : None
            }
        self.obState.update({'NEW' : 1, 'DB_PENDING' : 1})


    def initFromDatabase(self, identifier, connection, startAtItem = 0, maxItems = 15, asSet = True):
        """ method for initialising predicateLink from database"""
        
        # first init base class - this will get obid
        ob.initFromDatabase(self, identifier, "predicateLink", connection)
        
        # now get the complete object
        self.databaseFields = getObjectRecord(connection, "predicateLink", self.databaseFields['obid'])
        self.obState.update({'NEW' : 0 , 'DB_PENDING' : 0, 'MESSAGE' : "init from database OK"})
        
    
    def insertDatabase(self,connection):
        """ method used by list object  to save itself to database  """
        
        sql = """
        insert into predicateLink (obid, xreflsid, obkeywords,createdby,
            subjectob,objectob,predicate,predicatecomment)
        values (%(obid)s, %(xreflsid)s, %(obkeywords)s,%(createdby)s,
            %(subjectob)s,%(objectob)s,%(predicate)s,%(predicatecomment)s)"""        
        listmodulelogger.info("executing " + sql%self.databaseFields)
        insertCursor = connection.cursor()
        insertCursor.execute(sql,self.databaseFields)
        connection.commit()
        insertCursor.close()
        self.obState.update({'NEW' : 0 , 'ERROR' : 0, 'DB_PENDING' : 0, 'MESSAGE' : "database insert OK"})
        
    
    def addFact(self,connection,argfactNameSpace,argattributeDate,argattributeName,argattributeValue,checkExisting=True):
        factFields = {
            'predicatelink' : self.databaseFields['obid'],
            'factNameSpace' : argfactNameSpace,
            'attributeDate' : argattributeDate,
            'attributeName' : argattributeName,
            'attributeValue' : argattributeValue }
        
        # first check if this fact is already in the db - if it is do not duplicate
        sql = """
        select predicateLink from predicateLinkFact where
        predicateLink = %(predicateLink)s and
        factNameSpace = %(factNameSpace)s and
        attributeDate = %(attributeDate)s and
        attributeName = %(attributeName)s and
        attributeValue = %(attributeValue)s
        """
        insertCursor = connection.cursor()
        listmodulelogger.info("checking for fact using %s"%(sql%factFields))
        insertCursor.execute(sql,factFields)
        insertCursor.fetchone()
        listmodulelogger.info("rowcount = %s"%insertCursor.rowcount)
        if insertCursor.rowcount == 0:
            sql = """
            insert into predicateLinkFact(predicateLink,factNameSpace,attributeDate,attributeName,attributeValue)
            values(%(predicateLink)s,%(factNameSpace)s,%(attributeDate)s,%(attributeName)s,%(attributeValue)s)
            """
            listmodulelogger.info("executing %s"%(sql%factFields))
            insertCursor.execute(sql,factFields)
            connection.commit()
            insertCursor.close()
            self.obState.update({'NEW' : 0 , 'DB_PENDING' : 0, 'ERROR' : 0, 'MESSAGE' : "database insert OK"})
        else:
            insertCursor.close()



class rowDictFilter(object):
    """ this is a class that can be used to filter a "row" that is passed in
    as a dictionary of keyvalue pairs - for example , a row from a sql query
    made into a dictionary with key = column name. The filter method will return
    true or false for a given argument dictionary. Essentially the idea is that this
    enables you to do the programmatic equivalent of

    col1=a and
    col2=b and
    col3 in (d,d) and
    col4=e

    etc
    etc
     - e.f. can be used to programatically filter the results of a SQL query
     where the columns being returned are the values of stored functions, so that a
     SQL where clause will not work very well.
    

    The "and dict" filter consists of a dictionary with keys corresponding to keys
    in the dictionary to be filtered. The values of the filter dictionary are tuples - the first
    element is the match operation, the second element is itself a tuple of one or
    more data elements.

    e.g.

    dataDict= {
    'sex' : 'M',
    'diagnosis'  : 'Y'
    }

    filterDict = {
    'sex' : ['is',('M')],
    'diagnosis' : ['is','('CD,'UC')]
    }

    - this would filter rows to select all males with a diagnosis of CD or UC

    (there are other match operations such as is not, is greater than etc etc)
    

    For each key in the filter, the value in the data dictionary is compared with the
    value in the filter dictionary. If all filter values match data values , then the
    filter will return true. If the filter dictionary contains a tuple for some key,
    then there is a match if any of the elements of the tuple match
    """
    
    def __init__(self, filterDict, filterType="exact match"):
        object.__init__(self)
        self.filterType = filterType
        self.filterDict = filterDict

    def filterRow(self, dataDict):
        filterResult = True

        for key in self.filterDict:
            rule = self.filterDict[key]
            if not type(rule[1]) is TupleType and not type(rule[1]) is ListType:
                rule[1] = (rule[1],)
            
            if rule[0] == 'is' :
                if key in dataDict:
                    if dataDict[key] not in rule[1]:
                        filterResult = False
            elif rule[0] == 'is not':
                if key in dataDict:
                    if dataDict[key] in rule[1]:
                        filterResult = False
            else:
                raise brdfException("filterRow : unsupported rule %s"%rule[0])

        return filterResult
    
                    
        
        
        

def main():
    return


if __name__ == "__main__":
   main()
        
