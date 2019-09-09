##############################################################
# This module contains the base class and module level
# variables and functions for the biological resource description
# framework
#
# Author AgResearch NZ Ltd 6/2005
##############################################################

############# change log #####################################
# AMcC 15/1/2007 query that retrives external links modified to exclude "system" links - uses new linktype column of urilink table
# AMcC 14/3/2008 "external links" renamed "other resources" - note that in the security procedures module, it is still known as "external links"


from types import *
from brdfExceptionModule import brdfException
import logging
from imageModule import makeOpGlyph, makeBarGraph
import globalConf
import os
from datetime import date
from mx.DateTime import Parser
from htmlModule import tidyout, defaultMenuJS, dynamicMenuJS
import databaseModule
import re

# imports needed for the display functions
#from labResourceModule import microarraySpotFact


# shifted below as causes circular import problems
#from displayProcedures import getSampleFactDisplay,getGenepixThumbnailDisplay,getSpotExpressionDisplay,getExpressionMapDisplay,getInlineURL,getAlleleFrequencyDisplay,getSequenceAnnotationBundle,getAffyProbeGraphs
from securityProcedures import getLSIDRuleBasedPermission



""" logging - comment out when not required """
# set up logger if we want logging
obmodulelogger = logging.getLogger('obModule')
obmodulehdlr = logging.FileHandler(os.path.join(globalConf.LOGPATH,'brdf_obModule.log'))
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
obmodulehdlr.setFormatter(formatter)
obmodulelogger.addHandler(obmodulehdlr) 
obmodulelogger.setLevel(logging.INFO)        



""" --------- module methods ------------"""


# this method converts any date format to the canonical brdf form
# (as assumed in various database inserts) dd-mm-yyyy
def canonicalDate(instring, minYear = 0):
    #return (Parser.DateFromString(instring)).strftime("%d-%m-%Y")
    # gave up on this parser and did my own
    fields = [int(item) for item in re.split('[\-/\.]',instring)]
    if fields[2] < minYear:
        fields[2] += minYear
    return "%02d-%02d-%04d"%tuple(fields)

def canonicalToday():
    return date.today().isoformat()


def getNewObid(connection):
    """ this method gets a new obid from the obid sequence in the database """
    sql = "select nextval('ob_obidseq')"
    obidCursor = connection.cursor()
    obidCursor.execute(sql)
    obidTuple = obidCursor.fetchone()
    if obidCursor.rowcount != 1:
        raise brdfException, "getNewObid failed using " + sql
    obidCursor.close()
    return obidTuple[0]



def getObjectRecord(connection, tablename, obid):
    """ This method is a convenience template method used by the initFromDatabase method
    of many objects - it simply obtains a record from the specified table and returns in a dictionary"""

    sql = "select * from " + tablename + " where obid = " + str(obid)
    obCursor = connection.cursor()
    obCursor.execute(sql)
    obFieldValues = obCursor.fetchone()
    if obCursor.rowcount != 1:
        raise brdfException, "getObjectRecord : unable to find one unique object using " + sql
    fieldNames = [item[0] for item in obCursor.description]
    obCursor.close()


    return dict(zip(fieldNames,obFieldValues))


def getColumnAliases(connection, tablename):
    """ This method gets any columns aliases that have been defined """

    
    sql = """
    select lower(otf.termname), otf2.attributeValue from
    (ontologytermfact otf join ontologyob o
    on otf.ontologyob = o.obid) join
    ontologytermfact2 otf2 on otf2.ontologytermid = otf.obid
    where
    o.ontologyname = 'BRDFTABLE_%s' and
    otf2.factnamespace = 'DISPLAY' and
    otf2.attributeName = 'DISPLAYNAME'
    """%tablename.lower()
    obCursor = connection.cursor()
    obCursor.execute(sql)
    obFieldValues = obCursor.fetchall()
    columnAliases= None
    if obCursor.rowcount >0 :
        columnAliases = dict(obFieldValues)
        #obmodulelogger.info(str(columnAliases))
    obCursor.close()
    


    return columnAliases




def getDatafields(connection, tablename):
    """ This method returns the data fields in a table as a list. The data fields include
    obid, xreflsid and obkeywords but exclude the following information fields and system fields:
    
    obtypeid createddate  createdby 
    lastupdateddate  lastupdatedby  checkedout
    checkedoutby  checkoutdate statuscode
    tableoid cmax xmax cmin xmin oid ctid obid

    The current implementation is postgres dependant - there is probably
    a better (i.e. more portable) way.
    """
    #exclusions = ['obtypeid','createddate','createdby' ,\ 
    #    'lastupdateddate','lastupdatedby','checkedout' ,\
    #    'checkedoutby','checkoutdate','statuscode' ,\
    #    'tableoid','cmax','xmax','cmin','xmin','oid','ctid','obid' ]
    exclusions = ['obtypeid','createddate','createdby',
        'lastupdateddate','lastupdatedby','checkedout',
        'checkedoutby','checkoutdate','statuscode',
        'tableoid','cmax','xmax','cmin','xmin','oid','ctid']

    # note that where the table is in another schema, this requires stripping the
    # schemaname. Not sure what happens if two tables with the same name in
    # different schema !
    typename = tablename
    tokens = re.split('\.',tablename)
    if len(tokens) > 1:
        typename = tokens[1]

    sql = """
    select
       pga.attname
    from
       pg_attribute pga, pg_type pgt
    where
      lower(pgt.typname) = lower('%s') and
      pga.attrelid = pgt.typrelid and
      substr(pga.attname,1,1) != '.'"""%typename

    

    #obmodulelogger.info("---------- debug -------------")
    

    obCursor = connection.cursor()
    obCursor.execute(sql)
    dataFields = obCursor.fetchall()
    if obCursor.rowcount == 0:
        raise brdfException, "getDatafields : unable to get fields using  " + sql
    dataFields = [ item[0] for item in dataFields if item[0].lower() not in exclusions]
    obCursor.close()
    return dataFields


def getObTypeName(connection, typeid):
    """ this method returns the type name of an object given its type numeric number """
    sql = "select getObTypeName(%s)"%typeid
    obCursor = connection.cursor()
    obCursor.execute(sql)
    obField = obCursor.fetchone()
    obCursor.close()
    return obField[0]


def getObTypeid(connection, typename):
    """ this method returns the type id of an object given its type name """
    sql = "select getObTypeId('%s')"%typename
    obCursor = connection.cursor()
    obCursor.execute(sql)
    obField = obCursor.fetchone()
    obCursor.close()
    return obField[0]


def getInstanceBaseType(connection, instanceid):
    """ this method returns the base type of a give instance of an object. Note that an object may
    also have a virtual type - this method does not return the virtual type"""
    sql = "select obtypeid from ob where obid = %s"%instanceid
    obCursor = connection.cursor()
    obCursor.execute(sql)
    obField = obCursor.fetchone()
    obCursor.close()
    return obField[0]

# updated 1/11/2012 to handle cases where we pass a table that is a subject of virtual types.
# this is a hack and need to check behaviour if we do actually want to get
# the metada for the virtual type that sits on a table
#def getObTypeMetadata(connection , typeid):
def getObTypeMetadata(connection , typeid, is_virtual = False):
    """ this method gets the contents of the obtype table for a given typeid """

    if isinstance(typeid,IntType) :
        sql = "select * from obtype where obtypeid = %s"%typeid
    elif isinstance(typeid, StringTypes):
        # update 1/11/2012 We can have virtual types in a table.
        #sql = "select * from obtype where lower(tablename) = lower('%s')"%typeid
        sql = "select * from obtype where lower(tablename) = lower('%s') and isvirtual = %s"%(typeid, is_virtual)
    else:
        self.obState.update({'ERROR' : 1 , 'MESSAGE' : "getObTypeMetadata requires integer or string type identifier"})
        raise brdfException, self.obState['MESSAGE']

    obCursor = connection.cursor()
    obCursor.execute(sql)
    obFieldValues = obCursor.fetchone()
    if obCursor.rowcount != 1:
        raise brdfException, "getObTypeMetadata : unable to find one unique metadata record using " + sql
    fieldNames = [item[0] for item in obCursor.description]
    obCursor.close()
    return  dict(zip(fieldNames,obFieldValues))

    

def getOpDefinition(connection, typeid):
    """ This method gets the definition of an op - i.e. what objects are involved in the
    relation. It is a list of dictionaries - each dictionary  a record from the query below, defining
    an ob, with one dictionary for each ob in the relation. Note that there are some fields that are extracted here
    that apply to the relation as a whole"""
    sql = """
    select
      optypesig.obtypeid as "optypeid",
      obtype.displayname as "obdisplay",
      obtype.displayurl as "obdisplayurl",
      obtype.tablename as "obtablename",
      opinfo.tablename as "optablename",
      obtype.obtypeid as "obtypeid",
      obtype.owner as "obowner",
      optypesig.optablecolumn ,
      opinfo.isvirtual,
      opinfo.isdynamic,
      1 as "instancecount",
      opinfo.namedinstances
    from
      obtype, obtype opinfo, optypesignature optypesig
    where
      optypesig.obtypeid = %s and
      opinfo.obtypeid = optypesig.obtypeid and 
      obtype.obtypeid = optypesig.argobtypeid
    """
    # example output :
 #optypeid |     obdisplay     |   obtablename   |   optablename   | obtypeid |  optablecolumn  | isvirtual | instancecount
#----------+-------------------+-----------------+-----------------+----------+-----------------+-----------+---------------
#      240 | Lab Resource List | labResourcelist | microarrayStudy |       75 | labResourceList | f         |             1
#      240 | BioProtocol       | bioProtocolOb   | microarrayStudy |       95 | bioProtocolOb   | f         |             1
#      240 | BioSample List    | bioSampleList   | microarrayStudy |      102 | biosamplelist   | f         |             1

# optypeid |    obdisplay    |    obtablename     |  optablename  | obtypeid | optablecolumn | isvirtual | instancecount
#----------+-----------------+--------------------+---------------+----------+---------------+-----------+---------------
#      265 | Sequence        | bioSequenceOb      | predicatelink |      115 | object        | t         |             1
#      265 | Microarray Spot | microarraySpotFact | predicatelink |      235 | subject       | t         |             1
#  optypeid | obdisplay |  obdisplayurl   |  obtablename  |  optablename  | obtypeid | obowner | optablecolumn | isvirtual | isdynami
# | instancecount
#----------+-----------+-----------------+---------------+---------------+----------+---------+---------------+-----------+---------
#-+---------------
#      376 | Sequence  | biosequence.gif | bioSequenceOb | predicatelink |      115 | core    | objectob      | t         | f
# |             1
#      376 | Sequence  | biosequence.gif | bioSequenceOb | predicatelink |      115 | core    | subjectob     | t         | f
# |             1
      
            
    sql = sql%typeid
    #obmodulelogger.info("getting op definition using %s"%sql)
    obCursor = connection.cursor()
    obCursor.execute(sql)
    links = obCursor.fetchall()
    fieldNames = [item[0] for item in obCursor.description]
    obCursor.close()
    #self.metadataFields.update({'linkedobjects' : [item[0:6] for item in links]})
    opdefinition = [dict(zip(fieldNames,item)) for item in links]
    return opdefinition



def getOpMembership(connection, opdefinition, obtypeid, obid):
    """ this method is given an op definition and an ob and its type and determines whether the
    ob is referred to in an instance of the op.
    It will update the opdefinition to include a boolen for each term in the op, indicating whether
    that term refers to the ob. It also returns a reference count, counting how maany references to the
    ob occurr.
    """

    # get the name of the column.
    # opdefinition is a list of dictionaries as aboe - e.g.
    # [{'instancecount': 1, 'obdisplay': 'Lab Resource List', 'obtablename': 'labResourcelist',
    #'obtypeid': 75, 'isvirtual': , 'optablecolumn': 'labResourceList', 'optypeid': 240},
    #{'instancecount': 1, 'obdisplay': 'BioProtocol', 'obtablename': 'bioProtocolOb', 'obtypeid':
    #95, 'isvirtual': , 'optablecolumn': 'bioProtocolOb', 'optypeid': 240}, {'instancecount': 1,
    #'obdisplay': 'BioSample List', 'obtablename': 'bioSampleList', 'obtypeid': 102, 'isvirtual': ,
    #'optablecolumn': 'biosamplelist', 'optypeid': 240}]
    #
    # Note that if the op is a virtual op, then we need to check the voptypeid column
    # 

    #if not opdefinition[0]['isvirtual']:
    existenceResult = 0
    if opdefinition[0]['isdynamic']:
        existenceResult = None
    elif opdefinition[0]['isvirtual']:
        # 8/12/2006 this next line is incorrect when the opdefinition refers to a particular
        # object type more than once
        #mydict = [mydict for mydict in opdefinition if mydict['obtypeid'] == obtypeid][0]
        for mydict in [mydict for mydict in opdefinition if mydict['obtypeid'] == obtypeid]:
            obmodulelogger.info("finding relation membership using %s"%str(mydict))
            mydict.update({'obid' : obid }) 
            sql = """
            select 1 where exists (select %(optablecolumn)s from
            %(optablename)s where
            %(optablecolumn)s = %(obid)s and voptypeid = %(optypeid)s)"""%mydict
            #sql = "select 1"
            obmodulelogger.info("executing : " + sql)
            obCursor = connection.cursor()
            obCursor.execute(sql)
            existencetest = obCursor.fetchone()
            mydict['referencecount'] = obCursor.rowcount
            #print "getOpMembership dict after assignment : %s"%str(mydict)
            existenceResult += obCursor.rowcount        
    else:
        #mydict = [mydict for mydict in opdefinition if mydict['obtypeid'] == obtypeid][0]
        for mydict in [mydict for mydict in opdefinition if mydict['obtypeid'] == obtypeid]:
            mydict.update({'obid' : obid }) 
            sql = """
            select 1 where exists (select %(optablecolumn)s from
            %(optablename)s where
            %(optablecolumn)s = %(obid)s)"""%mydict
            #sql = "select 1"
            obmodulelogger.info("executing : " + sql)            
            obCursor = connection.cursor()
            obCursor.execute(sql)
            existencetest = obCursor.fetchone()
            mydict['referencecount'] = obCursor.rowcount
            existenceResult += obCursor.rowcount

    #elsif opdefinition[0]['optablename'] = 'predicatelink:
    
    #else
    #    existenceResult = 0

    obmodulelogger.info("getOpMembership returning %s"%str(existenceResult))
    return existenceResult



def getObRelations(connection, typeid, excludevirtual = False):
    """ this method gets all ops whose signature includes a given ob type, possibly excluding virtual ops"""
    if not excludevirtual:
        sql = """
                select distinct
                  optypesig.obtypeid as "optypeid",
                  obtype.displayname as "opdisplay"
                from
                  obtype , optypesignature optypesig
               where
                  optypesig.argobtypeid = %s  and
                  obtype.obtypeid = optypesig.obtypeid and
                  obtype.owner = 'core'
                """
    else:
        sql = """
                select distinct
                  optypesig.obtypeid as "optypeid",
                  obtype.displayname as "opdisplay"
                from
                  obtype opdetails, obtype , optypesignature optypesig
               where
                  optypesig.argobtypeid = %s  and
                  obtype.obtypeid = optypesig.obtypeid and
                  obtype.owner = 'core' and
                  opdetails.obtypeid = optypesig.obtypeid and
                  not opdetails.isvirtual
                """        



        
    # example output
    #optypeid |      opdisplay
    #----------+----------------------
    #  175 | Genetic Location
    #  190 | Genetic Function
    #  195 | Genetic Expression
    #  200 | Genetic Fact
    #  201 | Gene Product Link
    #  202 | Gene Regulation Link
    #  196 | Genetic Variation    

    sql = sql%typeid
    obCursor = connection.cursor()
    obCursor.execute(sql)
    obmodulelogger.info("executing sql to get relations : %s"%sql)
    relations = obCursor.fetchall()
    #fieldNames = [item[0] for item in obCursor.description]
    #obCursor.close()
    obrelations = dict(relations)
    return obrelations


def getJoinQuery(connection,joinParameters):
    """ this method uses the metadata stored in tables such as obtype and optype,
    to construct a query to retrieve records linked to a given starting record - e.g. we are given an
    ob and an op that we know links to another ob and we wish to retrieve the ob records for that
    other object."""

    obmodulelogger.info("join parameters : " + str(joinParameters))

    joinTitle = ""


    # this is the join done from the definition of a relation , that appears at the top of the page
    if joinParameters.has_key('joininstance') and  joinParameters.has_key('jointype') and joinParameters.has_key('totype'):
        # Example :
        #
        # select
        #    *
        # from
        #    biosamplelist bl, microarraystudy ms
        # where
        #    ms.obid = 204847 and
        #    bl.obid = ms.biosamplelist
        opDefinition = getOpDefinition(connection,int(joinParameters['jointype']))
        opMetadata = getObTypeMetadata(connection,int(joinParameters['jointype']))

        # information about the target type
        toTypeMetadata = getObTypeMetadata(connection,int(joinParameters['totype']))

        sqlTemplate = """
            select
                %(targetcols)s
            from
                %(targettable)s target, %(optable)s optable
            where
                optable.obid = %(joininstance)s and
                target.obid = optable.%(optablesourcecolumn)s
            """

            
        #optablesourcecolumn is obtained by
        #(1) find the table name of the totype
        #(2) look this up in the op definition
        sqlDict={}
        sqlDict['optablesourcecolumn'] = \
                   [record['optablecolumn'] for record in opDefinition if \
                  record['obtablename'].lower() == toTypeMetadata['tablename'].lower() ][0]

        sqlDict['joininstance'] = joinParameters['joininstance']

        sqlDict['targettable'] = toTypeMetadata['tablename']
        sqlDict['optable'] = opMetadata['tablename']

        # get the data fields to extract - first as a list then format
        dataFields = getDatafields(connection,sqlDict['targettable'])


                    
        obmodulelogger.info(str(dataFields))
        #sqlDict['targetcols'] = reduce(lambda x,y:x+","+y,["target.%s"%field for field in dataFields])
        sqlDict['targetcols'] = reduce(lambda x,y:x+","+y,["target.\"%s\""%field for field in dataFields])


        joinInstance = ob()
        joinInstance.initFromDatabase(int(joinParameters['joininstance']),opMetadata['obtypeid'],connection)
        joinTitle = "%s objects related to \"%s\" (%s)"%(toTypeMetadata['displayname'],joinInstance.databaseFields['xreflsid'],opMetadata['displayname'])

        # save the metadata to use in the report headings
        #self.opMetadata = opMetadata
        #self.toTypeMetadata = toTypeMetadata


        
        #obmodulelogger.info("---------- debug -------------")
        #obmodulelogger.info(" executing : ")
        #obmodulelogger.info(sqlTemplate%sqlDict)


    # as above, but if the relation is a unary fact relation
    elif joinParameters.has_key('joininstance') and  joinParameters.has_key('jointype'):
        # Example :
        #
        # select
        #    *
        # from
        #    microarrayspotfact
        # where
        #    ms.obid = 204847 
        opDefinition = getOpDefinition(connection,int(joinParameters['jointype']))
        opMetadata = getObTypeMetadata(connection,int(joinParameters['jointype']))
        toTypeMetadata = opMetadata

        sqlTemplate = """
            select
                %(targetcols)s
            from
                %(optable)s target
            where
                target.obid = %(joininstance)s 
            """

        
        sqlDict={}

        sqlDict['joininstance'] = joinParameters['joininstance']
        sqlDict['optable'] = opMetadata['tablename']

        # get the data fields to extract - first as a list then format
        dataFields = getDatafields(connection,sqlDict['optable'])
        obmodulelogger.info(str(dataFields))
        #sqlDict['targetcols'] = reduce(lambda x,y:x+","+y,["target.%s"%field for field in dataFields])
        sqlDict['targetcols'] = reduce(lambda x,y:x+","+y,["target.\"%s\""%field for field in dataFields])

        # save the metadata to use in the report headings
        #self.opMetadata = opMetadata
        #self.toTypeMetadata = toTypeMetadata


        
        #obmodulelogger.info("---------- debug -------------")
        #obmodulelogger.info(" executing : ")
        #obmodulelogger.info(sqlTemplate%sqlDict)
        joinInstance = ob()
        joinInstance.initFromDatabase(int(joinParameters['joininstance']),opMetadata['obtypeid'],connection)
        joinTitle = "%s Facts (%s)"%(opMetadata['displayname'],joinInstance.databaseFields['xreflsid'])
        
    
    elif joinParameters.has_key('jointype') and  joinParameters.has_key('fromob') and joinParameters.has_key('totype'):
        # example of query
        # select
        #   bio.sequencename
        # from
        #   biosequenceob bio,geneproductlink gpl
        # where
        #   gpl.geneticob = 48907 and
        #   bio.obid = gpl.biosequenceob

        # get the relation definition used in the join
        opDefinition = getOpDefinition(connection,int(joinParameters['jointype']))
        obmodulelogger.info("handling join : %s"%str(joinParameters))
        obmodulelogger.info("using opDefinition %s"%str(opDefinition))
        opMetadata = getObTypeMetadata(connection,int(joinParameters['jointype']))

        # information about the target type
        toTypeMetadata = getObTypeMetadata(connection,int(joinParameters['totype']))

        # instantiate the source object to get information about it
        fromOb = ob()
        fromOb.initFromDatabase(int(joinParameters['fromob']),'ob',connection)
        fromOb.initMetadata(connection)
            
        sqlTemplate = """
            select
                %(targetcols)s
            from
                %(targettable)s target, %(optable)s linktable
            where
                linktable.%(optablesourcecolumn)s = %(fromob)s and
                target.obid = linktable.%(optabletargetcolumn)s"""

        sqlTemplate1 = """
            select
                %(targetcols)s
            from
                %(targettable)s target, %(optable)s linktable
            where
                """    # used for making unions     

            
        #optablesourcecolumn is obtained by
        #(1) find the table name of the fromob
        #(2) look this up in the op definition
        sqlDict = {}
        sqlDict['optablesourcecolumn'] = \
                   [record['optablecolumn'] for record in opDefinition if \
                 record['obtablename'].lower() == fromOb.metadataFields['tablename'].lower() ]
        potentialSources = sqlDict['optablesourcecolumn'] 
        if len(sqlDict['optablesourcecolumn']) > 1:
            # this will be the case when the relation involves more than one instance of a type - for example
            # a relation between a biosequence and a biosequence. In this case we need to obtain reference counts
            # to try to decide which is the source column
            obmodulelogger.info("in getJoinQuery using opdefinition = %s"%str(opDefinition))
            membership = getOpMembership(connection, opDefinition, int(fromOb.metadataFields['obtypeid']), int(joinParameters['fromob']))
            obmodulelogger.info("...after call to getOpMembership : %s"%str(opDefinition))
            potentialSources = [record['optablecolumn'] for record in opDefinition if \
                 record['obtablename'].lower() == fromOb.metadataFields['tablename'].lower() and record['referencecount'] > 0]
            sqlDict['optablesourcecolumn'] = potentialSources[0] # but if there is more than one we will do a bit more below
        else:
            sqlDict['optablesourcecolumn'] = sqlDict['optablesourcecolumn'][0]
            
        sqlDict['fromob'] = joinParameters['fromob']
        sqlDict['jointype'] = joinParameters['jointype']

        #optabletargetcolumn is obtained by
        #(3) find the table name of the to-type (this also gives linktable above)
        #(4) look this up in the opdefinition
        # if 
        sqlDict['optable'] = opDefinition[0]['optablename']
        sqlDict['optabletargetcolumn'] = \
                   [record['optablecolumn'] for record in opDefinition if \
                  record['obtablename'].lower() == toTypeMetadata['tablename'].lower()]
        if len(sqlDict['optabletargetcolumn']) > 1:
            # this will be the case when the relation involves more than one instance of a type - for example
            # a relation between a biosequence and a biosequence. In this case we try to use reference counts -
            # i.e. if the column does not refer to this object then it is good to choose for a target

            membership = getOpMembership(connection, opDefinition, int(joinParameters['totype']), int(joinParameters['fromob']))
            potentialTargets = [record['optablecolumn'] for record in opDefinition if \
                  record['obtablename'].lower() == toTypeMetadata['tablename'].lower() and record['referencecount'] == 0]
            

            if len(potentialTargets) == 0:
                # this means that this object is present in the relation table in all columns, and it is
                # not possible to decide a sensible target column. In that case we again need to do a union of queries
                # , to link from all instances of this object
                potentialTargets = [record['optablecolumn'] for record in opDefinition if \
                    record['obtablename'].lower() == toTypeMetadata['tablename'].lower()]                
            if len(potentialTargets) == 1 and len(potentialSources) == 1:
                sqlDict['optabletargetcolumn'] = potentialTargets[0]
            elif len(potentialTargets) > 1 or len(potentialSources) > 1 :
                # if we get more than one plausible target , use a union of queries to get all targets
                obmodulelogger.info("more than one plausible target in getJoinQuery - making union of queries (note - this is untested !)")
                setop = ""
                unioncount = 0
                sqlTemplate = ""
                for optablesourcecolumn in potentialSources:
                    for optabletargetcolumn in potentialTargets:
                        if optabletargetcolumn == optablesourcecolumn:
                            continue
                        sqlTemplate +=  setop
                        setop = " union "
                        unioncount += 1
                        sqlTemplate += sqlTemplate1
                        sqlTemplate += """linktable.%%(optablesourcecolumn%s)s = %%(fromob)s and
                                      target.obid = linktable.%%(optabletargetcolumn%s)s"""%(unioncount,unioncount)
                        sqlDict['optabletargetcolumn%s'%unioncount] = optabletargetcolumn
                        sqlDict['optablesourcecolumn%s'%unioncount] = optablesourcecolumn
                        
                obmodulelogger.info("resulting union template : %s"%str(sqlTemplate))
            elif len(potentialTargets) == 0:
                raise brdfException("Error - impossible branch(1) reached in getJoinQuery")                        
        else:
            sqlDict['optabletargetcolumn'] = sqlDict['optabletargetcolumn'][0]

        # if this is a virtual op  - i.e. it shares this op table with other ops - then
        # we will futher need to restrict the rows using the voptypeid column
        if opDefinition[0]['isvirtual']:
            sqlTemplate += """
            and linktable.voptypeid = %(jointype)s"""                        

        sqlDict['targettable'] = toTypeMetadata['tablename']

        # get the data fields for the target object to extract - first as a list then format
        targetDataFields = getDatafields(connection,sqlDict['targettable'])
        linkDataFields = getDatafields(connection,sqlDict['optable'])
        #dataFields = getDatafields(connection,sqlDict['targettable'])

        
        obmodulelogger.info("targetDataFields=%s"%str(targetDataFields))
        obmodulelogger.info("linkDataFields=%s"%str(linkDataFields))
        obmodulelogger.info("sqlDict=%s"%str(sqlDict))

        #sqlDict['targetcols'] = \
        #    reduce(lambda x,y:x+","+y,["target.%s"%field for field in targetDataFields]) + "," + \
        #    reduce(lambda x,y:x+","+y,["linktable.%s"%field for field in linkDataFields])                              
        sqlDict['targetcols'] = \
            reduce(lambda x,y:x+","+y,["target.\"%s\""%field for field in targetDataFields]) + "," + \
            reduce(lambda x,y:x+","+y,["linktable.\"%s\""%field for field in linkDataFields])                              
             

        #joinInstance = ob()
        #joinInstance.initFromDatabase(int(joinParameters['joininstance']),opMetadata['obtypeid'],connection)
        joinTitle = "%s objects related to \"%s\" (%s), via %s"%(toTypeMetadata['displayname'],fromOb.databaseFields['xreflsid'],fromOb.metadataFields['displayname'],\
                                                                 opMetadata['displayname'])
      

    # join to an op table
    elif joinParameters.has_key('jointype') and  joinParameters.has_key('fromob') :
        # example of query
        # select
        #   bio.sequencename
        # from
        #   biosequenceob bio,geneproductlink gpl
        # where
        #   gpl.geneticob = 48907 and
        #   bio.obid = gpl.biosequenceob

        # get the relation definition used in the join
        opDefinition = getOpDefinition(connection,int(joinParameters['jointype']))
        opMetadata = getObTypeMetadata(connection,int(joinParameters['jointype']))
        toTypeMetadata = opMetadata


        # instantiate the source object to get information about it
        fromOb = ob()
        fromOb.initFromDatabase(int(joinParameters['fromob']),'ob',connection)
        fromOb.initMetadata(connection)
            
        sqlTemplate = """
            select
                %(targetcols)s
            from
                %(optable)s target
            where
                target.%(optablesourcecolumn)s = %(fromob)s """

        sqlTemplate1 = """
            select
                %(targetcols)s
            from
                %(optable)s target
            where """
            
        #optablesourcecolumn is obtained by
        #(1) find the table name of the fromob
        #(2) look this up in the op definition
        #obmodulelogger.info(str(opDefinition))
        #obmodulelogger.info(str(fromOb.metadataFields))

        potentialSources =  [record['optablecolumn'] for record in opDefinition if \
                 record['obtablename'].lower() == fromOb.metadataFields['tablename'].lower()]
        
        obmodulelogger.info(str(potentialSources))
        
        
        sqlDict = {
            "jointype" : joinParameters['jointype']
        }
        
        #sqlDict['optablesourcecolumn'] = \
        #           [record['optablecolumn'] for record in opDefinition if \
        #         record['obtablename'].lower() == fromOb.metadataFields['tablename'].lower()][0]

        if len(potentialSources) == 1:
            sqlDict['optablesourcecolumn'] = potentialSources[0]
        elif len(potentialSources) > 1 :
            # if we get more than one plausible target , use a union of queries to get all targets
            obmodulelogger.info("more than one plausible source in getJoinQuery - making union of queries")
            setop = ""
            unioncount = 0
            sqlTemplate = ""
            for optablesourcecolumn in potentialSources:
                sqlTemplate +=  setop
                setop = " union "
                unioncount += 1
                sqlTemplate += sqlTemplate1
                sqlTemplate += """ target.%%(optablesourcecolumn%s)s = %%(fromob)s """%unioncount
                sqlDict['optablesourcecolumn%s'%unioncount] = optablesourcecolumn
                    
            obmodulelogger.info("resulting union template : %s"%str(sqlTemplate))
        else:
            raise brdfException("Error - impossible branch(2) reached in getJoinQuery")                 
            

        # if this is a virtual op  - i.e. it shares this op table with other ops - then
        # we will futher need to restrict the rows using the voptypeid column
        if opDefinition[0]['isvirtual']:
            sqlTemplate += """
            and voptypeid = %(jointype)s"""            

        
        sqlDict['fromob'] = joinParameters['fromob']



        #optabletargetcolumn is obtained by
        #(3) find the table name of the to-type (this also gives linktable above)
        #(4) look this up in the opdefinition
        sqlDict['optable'] = opDefinition[0]['optablename']


        # get the data fields to extract - first as a list then format
        dataFields = getDatafields(connection,sqlDict['optable'])
        obmodulelogger.info(str(dataFields))
        #sqlDict['targetcols'] = reduce(lambda x,y:x+","+y,["target.%s"%field for field in dataFields])
        sqlDict['targetcols'] = reduce(lambda x,y:x+","+y,["target.\"%s\""%field for field in dataFields])

        joinTitle = "%s related to \"%s\" (%s)"%(opMetadata['displayname'], fromOb.databaseFields['xreflsid'],fromOb.metadataFields['displayname'])                        
        
        
    else :
        raise brdfException, "please specify a join - fields received were <br/> " + reduce(lambda x,y:x+y ,[key + '=' + str(value) + '<br/>' for key,value in joinParameters.items()])
                
    return (sqlTemplate,sqlDict,opMetadata,toTypeMetadata,joinTitle)

    
    
""" ---------- module classes ------------"""



    
class ob (object ):
    """ base class for all brdf ob objects. An ob object mainly consists simply of a
    dictionary containing the database fields from the ob table. An object can be initialised
    to different stages - here is a complete initialisation sequence from the database :

        dbconnection=PgSQL.connect(host=sessionhost,database=sessiondatabase, \
        user=sessionuser,password=sessionpassword)
        study = microarrayStudy()                               # new uninitialised object
        study.initFromDatabase(experimentName,dbconnection)     # basic data from database
        study.initMetadata(dbconnection)                        # also get metadata
        study.discoverLinks(dbconnection)                       # also discover links

    - depending on the purpose, it may not be necessary to obtain metadata and links (so
    doing this would waste time)

    """
    def __init__(self):
        """ ob constructor does very little """ 
        # call base class constructor
        object.__init__(self)

        # these resources are used to contruct call-backs and for images that
        # are created on-the-fly. They will be initialised by the cgi instance thaht
        # instantiates this object - the values assigned here are just for development and
        # are not actually used when an object is constructed by the instance scripts
        self.homeurl="dummy value will be initialised by instance code"
        self.fetcher="dummy value will be initialised by instance code"
        self.imageurl="dummy value will be initialised by instance code"
        self.imageurl="dummy value will be initialised by instance code"        
        self.imagepath="dummy value will be initialised by instance code"
        self.jointomemberurl="dummy value will be initialised by instance code"
        self.jointonullurl="dummy value will be initialised by instance code"        
        self.jointooburl="dummy value will be initialised by instance code"
        self.joinfacturl="dummy value will be initialised by instance code"
        self.addCommentURL="dummy value will be initialised by instance code"
        self.addLinkURL="dummy value will be initialised by instance code"
        self.editURL="dummy value will be initialised by instance code"
        self.linkAnalysisProcedureURL="dummy value will be initialised by instance code"
        self.padlocktext="Restricted Access"
        self.padlockurl="none"
        self.username="nobody"
        self.tools = {}
        self.columnAliases=None

        self.obState = {
            'NEW' : 1,
            'METADATA' : 0,
            'LINKS' : 0,
            'COMMENTS' : 0,
            'DYNAMIC_DISPLAYS' : 0,
            'VIRTUAL_DYNAMIC_DISPLAYS' : 0,
            'HYPERLINKS' : 0,
            'LISTMEMBERSHIP' : 0,
            'ERROR' : 0,
            'OP' : 0,
            'DB_PENDING' : 0,
            'MESSAGE' : '',
            'SECURITY_POLICIES' : 0,
            'DYNAMIC_ANALYSES' : 0,
            'INTERFACE_CONFIGURATION' : 0
            }

        self.compressionLevel = 0 # this is used so users can hint to try to compress data - especially LSIDs,
                                  # and is set on an instance by instance basis. Default is 0, no compression. Level 1
                                  # compresses LSIDs (and in some cases avoids storing them)
        
        # set up logger if we want logging
        #self.logger = logging.getLogger('myapp')
        #hdlr = logging.FileHandler('c:/temp/brdf_obModule.log')
        #formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
        #hdlr.setFormatter(formatter)
        #self.logger.addHandler(hdlr) 
        #self.logger.setLevel(logging.INFO)


        # the AboutMe dictionary , contains sections of text describing the
        # object. The dictionary is structured in three layers :
        # layer 1 is indexed by the view that is in force, since the description
        #    depends on the view
        # layer 2 is indexed by a number used to control the order of the sections
        # layer 3 contains details of the section, at least the section name and text
        # Subclasses of ob, such as biosequenceOb etc, will add paragraphs as they wish
        # to the AboutMe dictionary, to customise the description as appropriate. Also,
        # specific instances of the brdf can override the text as whole to insert
        # localised descriptions
        self.AboutMe = {
            'geneindex' : {
                0 : {
                    'sectionname' : 'Object_Description',
                    'heading' : '',
                    'text' : ''  # subclasses fill in this if they can
                },
                5 : {
                    'sectionname' : 'Gene_Index_View',
                    'heading' : 'Gene Index View',
                    'text' : """
                        The Gene Index view integrates data from a number of tables into a single gene-centric view
                        """
                }
            },
            'default' : {
                0 : {
                    'sectionname' : 'Object_Description',
                    'heading' : '',
                    'text' : ''  # subclasses fill in this if they can
                },
                5 : {
                    'sectionname' : 'Page_Usage',
                    'heading' : 'Page Usage',
                    'text' : """
                        Using this page you can
                        <ul>
                        <li> attach free text comments
                        <li> attach links to external files or web pages , either on the web or on your own
                             intranet
                        <li> click links in the information map to run simple reports that list related
                         records , together with hyperlinks so that you can navigate to those records
                        </ul>
                        """
                },
                10 : {
                    'sectionname' : 'Description of the Default BRDF Database Page',
                    'heading' : 'Description of the Default BRDF Database Page',
                    'text' : """
                    The default page view includes the following sections : 
                    """
                }, # a dictionary for each section                
                15 : {
                    'sectionname' : 'Information_Summary',
                    'heading' : '<ul> Information Summary </ul>',
                    'text' : """
                    <ul>
                    The information summary displays the core database fields recorded for this object. Note that these
                    core fields are usually few in number, and related solely to the object itself - for example, its name,
                    storage location etc. Most of the information of interest is stored either in details tables (called fact tables in the
                    brdf schema) , linked to the object, or in tables corresponding to related objects in the database. These details tables and
                    relationships are depicted in the Information Map section of the page.
                    </ul>
                    """
                }, # a dictionary for each section
                20 : {
                    'sectionname' : 'Information_Map',
                    'heading' : '<ul> Information Map </ul>',
                    'text' : """
                    <ul>
                    The information map displays the possible types of relationship an object can
                    have with other objects in the BRDF database schema,  and also the possible types of
                    factual details about an object that can be stored in related details tables. 
                    <p/>
                    Where a given object is related to one or more other objects in the database, this is depicted
                    by an icon , in which symbols representing each of the objects in the relationship are connected
                    together by horizontal lines. If you click on a symbol, a simple report will be displayed, listing
                    all of that type of  object,  that are related via the relationship depicted.
                    <p/>
                    (If there are no instances of a depicted relation currently in the database, the icon is greyed out)
                    <p/>
                    Where a given type of fact is stored about an object, in a specific seperate details table linked to
                    the main object, this is depicted by a line connecting the object symbol , to a square box
                    labelled info, with the type of fact appearing to the right of the icon. If you click on the square
                    info box, a simple report will be displayed listing all the details records of that type, related to
                    your object
                    <p/>
                    (Where the database does not yet contain any facts of a given type for an object, the info icon is greyed out)
                    <p/>
                    When additional details tables are added to the schema , as may be required for specific projects,
                    icons depicting the new data dimensions will automatically be added to the information map.
                    </ul>
                    """
                }, # a dictionary for each section
                25 : {
                    'sectionname' : 'Record Status',
                    'heading' : '<ul> Record Status </ul>',
                    'text' : """
                    <ul>
                    The record status section shows database housekeeping information, such as the date the record
                    was created, date last updated and whether the record has been checked out.
                    </ul>
                    """
                } # a dictionary for each section                    
            } # a dictionary for each view
        } # AboutMe dictionary

        self.theme = {
            "object heading class" : "brdftop1",
            #"section heading class" : "sectionheading2"
            "section heading class" : "sectionheading"
        }

    def makeAboutMe(self,context):
        """ This method renders the AboutMe dictionary as HTML """
        if context in self.AboutMe:
            AboutMe = self.AboutMe[context]
        else:
            AboutMe = self.AboutMe['default']


        doc = ""
        # make table of contents
        toc = "<h2> BRDF Page Help Contents </h2> <p/> <ul>"
        sections = AboutMe.keys()
        sections.sort()
        for sectionnumber in sections:
            sectionDict = AboutMe[sectionnumber]
            if len(sectionDict['text']) > 0:
                # if the heading is indented by a <ul> , do not make it
                # an item
                if re.search('<ul>',sectionDict['heading'],re.IGNORECASE):
                    toc += '<b><i>%s</i></b>\\n'%(sectionDict['heading'])
                else:
                    toc += '<li><b><i>%s</i></b></li>\\n'%(sectionDict['heading'])

        toc += '</ul>'

        doc += toc

        # make sections
        for sectionnumber in sections:
            sectionDict = AboutMe[sectionnumber]
            if len(sectionDict['text']) > 0:
                text = re.sub('\n',' ',sectionDict['text'])
                doc += '<p/><h3> %s </h3><p/>%s\\n'%(sectionDict['heading'],text)
    
        return doc

    def initFromExternalData(self,dataSource):
        """ method for initialising an object from external data - a dataSourceOb """
        self.obState.update({'ERROR' : 1 , 'MESSAGE' : "initFromExternalData unimplemented for " + self.__class__.__name__})
        raise brdfException, self.obState['MESSAGE']

    def initNew(self):
        """ method for initialising a new object with basic fields such as obid """
        self.obState.update({'ERROR' : 1 , 'MESSAGE' : "initNew unimplemented for " + self.__class__.__name__})
        raise brdfException, self.obState['MESSAGE']
    
                                
    def initFromDatabase(self, identifier, identifiertype, connection):
        """ method for initialising an object from database - this just does minimal initialisation,
        to obtain the basic information from the ob table. Most objects first call this method to get an
        obid, then do the remainder of the initialisation to obtain a conplete object
            !!!! it is important to note that obid is not unique in the ob table due to inheritance. The
            combination of obid + obtypeid is unique
        9/2013 no it isn't ! Need to look more into this. in the meantime a workaround is to ignore
        multiple rows in the obtable

        """

        if not (isinstance(identifier,IntType) or isinstance(identifier, StringTypes)): 
            self.obState.update({'ERROR' : 1 , 'MESSAGE' : "initFromDatabase requires integer or string object identifier"})
            raise brdfException, self.obState['MESSAGE']      
        
        idClause = " xreflsid = %(identifier)s"

        if isinstance(identifier, IntType):
            idClause = " obid = %(identifier)s"

        typeClause = " obtypeid = getObTypeid(%(identifiertype)s)"
        if isinstance(identifiertype, IntType):
            typeClause = " obtypeid = %(identifiertype)s"

        if str(identifiertype).lower() == 'ob':
            sql = "select * from ob where " + idClause
        else:
            sql = "select * from ob where " + idClause + " and " + typeClause

        obmodulelogger.info("initFromDatabase trying %s"%(sql%{'identifier' : identifier, 'identifiertype' : identifiertype}))
        obCursor = connection.cursor()
        obCursor.execute(sql,{'identifier' : identifier, 'identifiertype' : identifiertype})

        obFieldValues = obCursor.fetchone()
        if obCursor.rowcount == 0:
            self.obState.update({'ERROR' : 1 , 'MESSAGE' : "initFromDatabase unable to find one object using " + sql})
            obmodulelogger.info(str(self.obState))
            raise brdfException, self.obState['MESSAGE']
        elif obCursor.rowcount > 1:
            #self.obState.update({'ERROR' : 2 , 'MESSAGE' : "initFromDatabase found more than one object using " + sql})
            obmodulelogger.info("Warning ! initFromDatabase found more than one object using %s (- but this is possible due to inheritance)"%sql)
            #raise brdfException, self.obState['MESSAGE']
        
        fieldNames = [item[0] for item in obCursor.description]
        obCursor.close()


        self.databaseFields = dict(zip(fieldNames,obFieldValues))

        self.databaseFields['tablename'] = getObTypeName(connection,int(self.databaseFields['obtypeid']))


        # do a lite initialisation of the metadata only relating to the ob base-class - mainly just to grab the displayurl for an ob
        self.metadataFields = getObTypeMetadata(connection,getObTypeid(connection,'ob')) 
        
        self.obState.update({'ERROR' : 0 , 'NEW' : 0, 'MESSAGE' : "initialised from database OK"})

    def initMetadata(self, connection):
        if self.obState['NEW'] == 1:
            self.obState.update({'ERROR' : 1 , 'MESSAGE' : "cannot get metadata until object is initialised with initFromDatabase"})
            raise brdfException, self.obState['MESSAGE']
            
        self.metadataFields = getObTypeMetadata(connection,self.databaseFields['obtypeid'])
        self.obState.update({'METADATA' : 1, 'MESSAGE' : "metadata initialised from database OK"})

        # check that API and database are consistent as regards whether this is an op or not
        #.................... this check turned off 11/2005 - ops can be obs ................
        #if self.obState['OP'] == 1:
        #    if not self.metadataFields['isop']:
        #        self.obState.update({'ERROR' : 1 , 'MESSAGE' : "fatal error - created as op but database says I am an ob"})
        #        raise brdfException, self.obState['MESSAGE']
        #else:
        #    if self.metadataFields['isop']:
        #        self.obState.update({'ERROR' : 1 , 'MESSAGE' : "fatal error - created as ob but database says I am an op"})
        #        raise brdfException, self.obState['MESSAGE']


    def initComments(self, connection):
        """ this method gets all comments on this object"""
        sql = """
                select
                   c.obid,
                   '<pre>'||c.commentstring||'</pre>' as commentstring,
                   CASE WHEN cl.commentdate is null THEN '1 JAN 01'
                   ELSE cl.commentdate END,
                   CASE WHEN cl.commentby is null THEN 'nobody'
                   ELSE cl.commentby END,
                   cl.style_bgcolour
                from
                   commentob c, commentlink cl
                where
                   cl.ob = %s and
                   c.obid = cl.commentob    
             """
        sql = sql%self.databaseFields['obid']
        obmodulelogger.info('executing SQL to retrieve comments : %s'%sql)        
        
        commentCursor = connection.cursor()
        commentCursor.execute(sql)
        self.commentFields = commentCursor.fetchall()


        # some classes reference the comment table directly, via a virtual op defined
        # on the table. For example the genotypeobservation class table has a virtual op
        # defined on it which provides a relation between the genotypeobservation class and the
        # comment class.
        #
        # this needs some more work - it is incomplete as at 7/2009
        #if self.obState['LINKS'] == 1:
        #    obmodulelogger.info("checking for comment links via virtual ops")
        #    linkinfo = (None, None)
        #
        #    for opdef in self.relatedOpDefinitions.values(): # this is a list
        #        linkinfo = (None,None) # will contain
        #        for obdef in opdef: # this is a dict like {'obowner': 'core', 'obdisplay': 'Comment', 'obtablename': 'CommentOb', 'obtypeid': 40, 'isdynamic': <PgBoolean instance at 0x25cb60: Value: False>, 'obdisplayurl': 'comment.jpg', 'namedinstances': <PgBoolean instance at 0x25cb6c: Value: True>, 'isvirtual': <PgBoolean instance at 0x25cb6c: Value: True>, 'instancecount': 1, 'optablecolumn': 'obid', 'optablename': 'commentOb', 'optypeid': 384}
        #            if obdef["obtablename"].lower() == "commentob":
        #                linkinfo[1] = obdef["optablecolumn"] # will always be obid -  but a value indicates the link is to a oomment
        #            elif obdef["obtablename"].lower() == self.metadataFields["tablename"].lower():
        #                linkinfo[0] = obdef["optablecolumn"] # which is the foreign key to the comment table
        #
        #        if linkinfo[0] != None and linkinfo[1] != None:
        #            break # we assume there is only a single comment-related virtual op defined on the table and we have found it.
        #                  # - nothing really to stop there being more , however we do not look for them (currently)
        #
        #    if linkinfo[0] != None and linkinfo[1] != None:
        #        # construct and execute a query to retrieve the comments
        #        None
        
        if commentCursor.rowcount > 0:        
            self.obState.update({'COMMENTS' : commentCursor.rowcount , 'MESSAGE' : "comments initialised from database OK"})

        commentCursor.close()


    def initDisplayFunctions(self, connection):
        """ this method gets all the dynamic display functions that involve this object. These are used by the
        object to display itself. 
        """
        sql = """
        select
            df.invocation,
            df.functioncomment,
            dp.xreflsid,
            dp.procedurename,
            ds.datasourcename,
            ds.physicalsourceuri,
            ds.datasourcetype,
            df.voptypeid,
            dp.proceduredescription,
            df.invocationorder,
            df.obid,
            ds.obid
        from
            (displayfunction df join displayprocedureob dp on
            df.displayprocedureob = dp.obid) left outer join
            datasourceob ds on ds.obid = df.datasourceob
        where
            df.ob = %(obid)s
        order by
            dp.proceduredescription,
            df.invocationorder
        """
        obmodulelogger.info('executing SQL to retrieve dynamic display functions : %s'%str(sql%self.databaseFields))        
        displayCursor = connection.cursor()
        displayCursor.execute(sql,self.databaseFields)
        self.displayFunctions = displayCursor.fetchall()
        if displayCursor.rowcount > 0:        
            self.obState.update({'DYNAMIC_DISPLAYS' : displayCursor.rowcount , 'MESSAGE' : "dynamic displays initialised from database OK"})
        displayCursor.close()
        obmodulelogger.info(str(self.displayFunctions))


    def initAnalysisFunctions(self, connection):
        """ this method gets all the dynamic analysis functions that are attached to this object
        """
        sql = """
        select
            af.invocation,
            af.functioncomment,
            ap.xreflsid,
            ap.procedurename,
            ap.proceduretype,
            af.datasourcelist,
            af.voptypeid,
            ap.proceduredescription,
            af.invocationorder,
            af.obid,
            af.datasourceob,
            coalesce(getdatasourcecharfact(af.datasourceob,'Dynamic Content Configuration','Web Prompt'),
               concatdatasourcefacts(af.datasourcelist,'Dynamic Content Configuration','Web Prompt')) as webprompt
        from
            (analysisfunction af join analysisprocedureob ap on
            af.analysisprocedureob = ap.obid) left outer join
            datasourcelist dl on dl.obid = af.datasourcelist
        where
            af.ob = %(obid)s
        order by
            ap.proceduredescription,
            af.invocationorder
        """
        obmodulelogger.info('executing SQL to retrieve dynamic analysis functions : %s'%str(sql%self.databaseFields))        
        analysisCursor = connection.cursor()
        analysisCursor.execute(sql,self.databaseFields)
        self.analysisFunctions = analysisCursor.fetchall()
        if analysisCursor.rowcount > 0:        
            self.obState.update({'DYNAMIC_ANALYSES' : analysisCursor.rowcount , 'MESSAGE' : "dynamic analyses initialised from database OK"})
        analysisCursor.close()

        if self.analysisFunctions == None:
            self.analysisFunctions = []
            
        obmodulelogger.info(str(self.analysisFunctions))
        



    def initProtections(self, connection):


        # get policies attached to all objects
        sql = """
        select
            invocation
        from
            securityfunction
        where
            obtypeid = 0
        """
        obmodulelogger.info('executing SQL to retrieve security functions (1): %s'%sql )       
        securityCursor = connection.cursor()
        securityCursor.execute(sql)
        self.securityFunctions = securityCursor.fetchall()        
        if securityCursor.rowcount > 0:        
            self.obState.update({'SECURITY_POLICIES' : securityCursor.rowcount , 'MESSAGE' : "security policies for all objects initialised from database OK"})


        # get policies for this object type  if we know what type we are
        if self.obState['METADATA'] == 1:
            sql = """
            select
                invocation
            from
                securityfunction
            where
                applytotype = %(obtypeid)s and
                ob is null
            """
            obmodulelogger.info('executing SQL to retrieve security functions (2): %s'%(sql%self.metadataFields) )
            securityCursor.execute(sql,self.metadataFields)
            self.securityFunctions += securityCursor.fetchall()            
            if securityCursor.rowcount > 0:
                self.obState.update({'SECURITY_POLICIES' : len(self.securityFunctions) , 'MESSAGE' : "security policies for type initialised from database OK"})
            

        # get policies for this object
        if self.obState['METADATA'] == 1:
            sql = """
                select
                    invocation
                from
                    securityfunction
                where
                    ob = %(obid)s 
            """
            obmodulelogger.info('executing SQL to retrieve security functions (3): %s'%(sql%self.databaseFields) )
            securityCursor.execute(sql,self.databaseFields)
            self.securityFunctions += securityCursor.fetchall()            
            if securityCursor.rowcount > 0:
                self.obState.update({'SECURITY_POLICIES' : len(self.securityFunctions) , 'MESSAGE' : "security policies for object instance initialised from database OK"})
          
        securityCursor.close()
        obmodulelogger.info(str(self.securityFunctions))



    #
    # this method may be deprecated (as at 8/2009) - relates to the dynamic forms work - i.e. forms based on the
    # datasource lists - but not sure how we weant to proceed yet
    #
    def initUserInterfaces(self, connection, interfaceType="HTML"):

        # initialise parts of the user interface that are decided at run-time, such as interface
        # elements for updating the database

        # get data source collections 
        mytype = type(self).__name__
        sql = """
        select distinct
           datasourcelist
        from
           datasourcelistfact
        where
           factnamespace = 'Class Bindings' and
           attributename = 'Class' and
           attributevalue = lower(%(mytype)s)
        """
        obmodulelogger.info('executing SQL to retrieve class element collections : %s'%sql )       
        interfaceCursor = connection.cursor()
        interfaceCursor.execute(sql)
        self.interfaces = interfaceCursor.fetchall()        
        self.obState.update({'INTERFACE_CONFIGURATION' : interfaceCursor.rowcount , 'MESSAGE' : "interface configured from database OK"})
        obmodulelogger.info(str(self.obState))
        
        
    def runDisplayFunctions(self,connection,context="default",procedureList = None, functionList = None, runVirtual = True, runNonVirtual = True):
        """ This method allows a call to be made to this object to get it to run
        either all instances of a given list of display procedures, or all specific
        displayProcedure instances - i.e. all functions.
        """
        from displayProcedures import getSampleFactDisplay,getGenepixThumbnailDisplay,getSpotExpressionDisplay,getExpressionMapDisplay,getInlineURL,getAlleleFrequencyDisplay,getSequenceAnnotationBundle,getAffyProbeGraphs,getInlineTable
        result = ''
        obmodulelogger.info("runDisplayFunctions : obstate = %s"%str(self.obState))
        if self.obState['DYNAMIC_DISPLAYS'] > 0:
            obmodulelogger.info('running non virtual display functions , procedures = %s, functions=%s'%(str(procedureList),str(functionList)))
            for displayFunction in self.displayFunctions:
                obmodulelogger.info("checking %s"%displayFunction)
                runit = False
                if procedureList != None:
                    if displayFunction[2] in procedureList or str(displayFunction[2]) in procedureList:
                        runit = True
                if functionList != None:
                    if displayFunction[10] in functionList or str(displayFunction[10]) in functionList:
                        runit = True

                if runit:
                    obmodulelogger.info("running %s"%displayFunction)
                    myResult = eval(displayFunction[0])
                    result += myResult

        if self.obState['VIRTUAL_DYNAMIC_DISPLAYS'] > 0:
            obmodulelogger.info('running virtual display functions , procedures = %s, functions=%s'%(str(procedureList),str(functionList)))
            for displayFunction in self.virtualDisplayFunctions:
                obmodulelogger.info("checking %s"%displayFunction)
                runit = False
                if procedureList != None:
                    if displayFunction[2] in procedureList or str(displayFunction[2]) in procedureList:
                        runit = True
                if functionList != None:
                    if displayFunction[10] in functionList or str(displayFunction[10]) in functionList:                    
                        runit = True

                if runit:
                    obmodulelogger.info("running %s"%displayFunction)
                    myResult = eval(displayFunction[0])
                    result += myResult                    
                    
        return result
                        

    def runSecurityFunctions(self,context="default",resourcename=""):
        """ this method runs all security functions and calculates a result
        that is an AND of all of them
        """
        result = True

        if self.obState['NEW'] == 1:
            return result
        else:
            obmodulelogger.info("runSecurityFunctions : obstate = %s"%str(self.obState))
            if self.obState['SECURITY_POLICIES'] > 0:
                obmodulelogger.info('running security policies')
                for securityFunction in self.securityFunctions:
                    if len(securityFunction) > 0:
                        obmodulelogger.info("running %s"%securityFunction)
                        result = result and eval(securityFunction[0])
                    
                    
        return result


    def runAnalysisFunctions(self,connection,context="default",procedureList = None, functionList = None, runVirtual = True, runNonVirtual = True,\
                             dynamicDataSources=None):
        """ This method allows a call to be made to this object to get it to run
        either all instances of a given list of analysis procedures, or all specific
        analysisProcedure instances - i.e. all analysis functions of a given type that are attached.

        The dynamic datasources parameter  allows interactive information to be
        passed to the function invocation - the variable dynamicDataSources
        needs to be referenced at run time.
        """
    
        from analysisModule import runProcedure
        result = ''
        obmodulelogger.info("runAnalysisFunctions : obstate = %s"%str(self.obState))
        if self.obState['DYNAMIC_ANALYSES'] > 0:
            obmodulelogger.info('running non virtual analysis functions , procedures = %s, functions=%s'%(str(procedureList),str(functionList)))
            for analysisFunctionInstance in self.analysisFunctions:

                # (note that the name "analysisFunctionInstance" is usually referenced in the procedure call that is evaluated)
                obmodulelogger.info("checking %s"%analysisFunctionInstance)
                runit = False
                if procedureList != None:
                    if analysisFunctionInstance[2] in procedureList or str(analysisFunctionInstance[2]) in procedureList:
                        runit = True
                if functionList != None:
                    if analysisFunctionInstance[9] in functionList or str(analysisFunctionInstance[9]) in functionList:
                        runit = True

                if runit:
                    obmodulelogger.info("running %s"%analysisFunctionInstance)
                    myResult = eval(analysisFunctionInstance[0])
                    result += myResult

        return result



    def initHyperLinks(self, connection):
        """ this method gets all hyperlinks attached to this object"""
        sql = """
                select
                   u.uristring,
                   CASE WHEN ul.displaystring is null then ''
                   ELSE ul.displaystring END,
                   CASE WHEN u.createdby is null THEN 'system'
                   ELSE u.createdby END,
                   u.uritype,
                   u.obid,
                   u.visibility,
                   ul.iconpath,
                   ul.iconattributes,
                   CASE WHEN ul.linktype is null then 'URL'
                   ELSE ul.linktype END
                from
                   uriob u, urilink ul
                where
                   ul.ob = %s and
                   u.obid = ul.uriob and
                   ((u.visibility is null or
                   u.visibility = 'public') or
                   (u.visibility = 'private' and
                   upper(u.createdby) = upper('%s'))) 
             """

        
        sql = sql%(self.databaseFields['obid'],self.username)
        obmodulelogger.info('executing SQL to retrieve hyperlinks : %s'%sql)        
        
        uriCursor = connection.cursor()
        uriCursor.execute(sql)
        self.uriFields = uriCursor.fetchall()
        # exclude system links
        self.uriFields = [record for record in self.uriFields if record[8].lower() != 'system']
        if len(self.uriFields) > 0:        
            self.obState.update({'HYPERLINKS' : len(self.uriFields) , 'MESSAGE' : "hyperlinks initialised from database OK"})

        uriCursor.close()

        # if this is a geneticob then get links attached to the location fact - e.g.
        # entrez gene links are attached to the location 
        if self.metadataFields['obtypedescription'].upper() == 'GENETICOB':
            sql = """
                select
                   u.uristring,
                   ul.displaystring,
                   CASE WHEN u.createdby is null THEN 'system'
                   ELSE u.createdby END,
                   u.uritype,
                   u.obid,
                   u.visibility,
                   ul.iconpath,
                   ul.iconattributes,
                   CASE WHEN ul.linktype is null then 'URL'
                   ELSE ul.linktype END                   
                from
                   uriob u,  urilink ul, geneticlocationfact glf
                where
                   glf.geneticob = %s and
                   ul.ob = glf.obid and
                   u.obid = ul.uriob and
                   ((u.visibility is null or
                   u.visibility = 'public') or
                   (u.visibility = 'private' and
                   upper(u.createdby) = upper('%s'))) 
             """
        
            sql = sql%(self.databaseFields['obid'],self.username)
            obmodulelogger.info('executing SQL to retrieve hyperlinks : %s'%sql)        
            uriCursor = connection.cursor()
            uriCursor.execute(sql)
            geneuri = uriCursor.fetchall()
            geneuri = [record for record in geneuri if record[8].lower() != 'system']
            
            if len(geneuri) > 0: 
                self.uriFields += geneuri
                self.obState.update({'HYPERLINKS' : len(self.uriFields) , 'MESSAGE' : "hyperlinks initialised from database OK"})

            uriCursor.close()


    def initListMembership(self, connection):
        """ this method gets all lists that this object is a member of """
        sql = """
                select distinct
                   l.obid,
                   l.listdefinition,
                   l.currentmembership,
                   to_char(l.createddate,'dd-mm-yyyy') as createddate    ,
                   l.listtype,
                   l.displayurl,
                   l.createddate
                from
                   oblist l join listmembershiplink lm
                   on lm.ob = %(obid)s and
                   l.obid = lm.oblist and
                   l.membershipvisibility = 'public'
                order by
                   l.createddate
             """

        
        sql = sql%self.databaseFields
        obmodulelogger.info('executing SQL to retrieve  : %s'%sql)        
        
        listCursor = connection.cursor()
        listCursor.execute(sql)
        self.listMembership = listCursor.fetchall()
        if listCursor.rowcount > 0:        
            self.obState.update({'LISTMEMBERSHIP' : listCursor.rowcount , 'MESSAGE' : "list membership  initialised from database OK"})

        listCursor.close()
         

    def discoverLinks(self, connection):
        """ this method obtains
        1) if this is an op, its definition - i.e. the objects involved in the relation
        2) if this is an ob, all optypes that include this ob in their signatire

        It is a dictionary keyed by the op type, with value a list of 
 dictionaries.

 Each element of the dictionary defines one of the classes in the 
 op signature - for example the entry for op 384 is a list of 
 two dictionaries - one describing the comment class the other 
 descibing the genotype observation class

 {384: [{'obowner': 'core', 'obdisplay': 'genotypeObservation', 'obtablename': 'genotypeObservation', 'obtypeid': 300, 'isdynamic': <PgBoolean instance at 0x25cb60: Value: False>, 'obdisplayurl': 'snp.png', 'namedinstances': <PgBoolean instance at 0x25cb6c: Value: True>, 'isvirtual': <PgBoolean instance at 0x25cb6c: Value: True>, 'instancecount': 1, 'optablecolumn': 'commentedob', 'optablename': 'commentOb', 'optypeid': 384}, 
        {'obowner': 'core', 'obdisplay': 'Comment', 'obtablename': 'CommentOb', 'obtypeid': 40, 'isdynamic': <PgBoolean instance at 0x25cb60: Value: False>, 'obdisplayurl': 'comment.jpg', 'namedinstances': <PgBoolean instance at 0x25cb6c: Value: True>, 'isvirtual': <PgBoolean instance at 0x25cb6c: Value: True>, 'instancecount': 1, 'optablecolumn': 'obid', 'optablename': 'commentOb', 'optypeid': 384}], 
  310: [{'obowner': 'core', 'obdisplay': 'genotypeObservation', 'obtablename': 'genotypeObservation', 'obtypeid': 300, 'isdynamic': <PgBoolean instance at 0x25cb60: Value: False>, 'obdisplayurl': 'snp.png', 'namedinstances': <PgBoolean instance at 0x25cb60: Value: False>, 'isvirtual': <PgBoolean instance at 0x25cb60: Value: False>, 'instancecount': 1, 'optablecolumn': 'genotypeObservation', 'optablename': 'genotypeObservationFact', 'optypeid': 310}]
 }        
        """

        
        if self.obState['METADATA'] == 0:
            self.obState.update({'ERROR' : 1 , 'MESSAGE' : "cannot discover links until object metadata is initialised"})

        if self.obState['OP'] == 1 :
            self.obState.update({'MESSAGE' : "discoverLinks : I am an op - getting obs"})
            self.metadataFields['opdefinition'] = getOpDefinition(connection,self.metadataFields['obtypeid'])

            # update the instancecount of each of the linked objects
            
 
        # now we get all the operations whose signature include the type of this object
        self.metadataFields['obrelations'] = getObRelations(connection,self.metadataFields['obtypeid'])
        obmodulelogger.info("obrelations found : %s"%str(self.metadataFields['obrelations']))


        # later on (e.g. asHTML) we will need , in turn , the definitions of all these operations - get
        # these now and cache .Note that the following call is really this : 
        relatedOpDefinitions = [ (optypeid , getOpDefinition(connection,optypeid) ) for optypeid in self.metadataFields['obrelations'].keys() ]


        # sort the related op definitions so that the "fact" ops are first - i.e. we sort by the length of the
        # second member of the tuple
        #relatedOpDefinitions.sort(\
        #    lambda x,y:len(x[1]) - len(y[1]) )


        # sort the returned lists , so that this object appears as the first object
        # in the list of objects involved in the relationship
        for opDefinition in relatedOpDefinitions:
            opDefinition[1].sort(\
                            lambda x,y : abs(x['obtypeid'] - self.metadataFields['obtypeid']) - \
                            abs(y['obtypeid'] - self.metadataFields['obtypeid']) )        
        
        #obmodulelogger.info("---------- debug -------------")
        #obmodulelogger.info(relatedOpDefinitions)

        self.relatedOpDefinitions = dict(relatedOpDefinitions)
        obmodulelogger.info("related op definitions found (before prune) : %s"%str(self.relatedOpDefinitions))

        self.relatedOpInstanceCounts = [ (optypeid, getOpMembership(connection, self.relatedOpDefinitions[optypeid], \
                                                                    self.metadataFields['obtypeid'],self.databaseFields['obid'])) \
                                          for optypeid in self.metadataFields['obrelations'].keys() ]
                                          
        self.relatedOpInstanceCounts = dict(self.relatedOpInstanceCounts)
        obmodulelogger.info("relatedOpInstanceCounts = %s"%str(self.relatedOpInstanceCounts))

        # now prune out all virtual ops that have an instance count of zero.
        # recall that for each optype, the relatedOpDefinitions dictionary contains a list of dictionaries,
        # each dictionary containing details of one of the objects in the relation, but also some
        # repeated information about the relation as a whole - e.g. isvirtual (this is because the
        # dictionaries are obtained from a SQL query). So to check if a relation is virtual , we can just check the
        # isvirtual element in the first dictionary in the list.

        # for the remaining virtual ops , prune those non-virtual ops that use the same
        # base table as a virtual op - i.e. virtual ops override their base op classes
        
        virtualTypes = [optype for optype in self.relatedOpDefinitions.keys() if self.relatedOpDefinitions[optype][0]['isvirtual']]
        for optype in virtualTypes:
            if self.relatedOpInstanceCounts[optype] == 0:
                obmodulelogger.info("pruning %s as no instances"%optype)
                
                del self.relatedOpDefinitions[optype]
                del self.relatedOpInstanceCounts[optype]          
            else:
                obmodulelogger.info("instance count of %s in type %s is %s"%(self.databaseFields['obid'],optype,self.relatedOpInstanceCounts[optype]))

                deletetypes = [deleteoptype for deleteoptype in self.relatedOpDefinitions.keys() \
                               if ((not self.relatedOpDefinitions[deleteoptype][0]['isvirtual']) and \
                                  (self.relatedOpDefinitions[deleteoptype][0]['optablename'] == self.relatedOpDefinitions[optype][0]['optablename'])) ]
                obmodulelogger.info("overriding :  %s"%str(deletetypes))
                for deletetype in deletetypes:
                    del self.relatedOpDefinitions[deletetype]
                    del self.relatedOpInstanceCounts[deletetype]

        obmodulelogger.info("related op definitions found (after prune and adding reference counts) : %s"%str(self.relatedOpDefinitions))
        
                    

        self.obState.update({'LINKS' : 1, 'MESSAGE' : "links initialised from database OK"})                                






    def insertDatabase(self,connection):
        """ method for saving a new object to the database  """
        self.obState.update({'ERROR' : 1 , 'MESSAGE' : "insertDatabase unimplemented for " + self.__class__.__name__})
        raise brdfException, self.obState['MESSAGE']

    def updateDatabase(self,connection):
        """ method for submitting updates of an existing object, to the database """
        self.obState.update({'ERROR' : 1 , 'MESSAGE' : "updateDatabase unimplemented for " + self.__class__.__name__})
        raise brdfException, self.obState['MESSAGE']

    def getColumnAlias(self,columnname):
        """method to get any column name alias that is available - if none, just return what was
        passed in """
        alias = columnname
        if self.columnAliases != None:
            if columnname.lower() in self.columnAliases:
                alias = self.columnAliases[columnname.lower()]
        return alias

    def myToolsPanel(self, table, width=800,context='default'):
        """ descendants of the ob class will usually override this method rather than the
        entire asHTMLRows method - this method supplies the contents of the summary
        panel
        """
        return None
    
    def myHTMLSummary(self, table, width=800,context='default'):
        """ descendants of the ob class will usually override this method rather than the
        entire asHTMLRows method - this method supplies the contents of the summary
        panel
        """
        FieldItems = [item for item in self.databaseFields.items() if not isinstance(item[1],ListType)]


        # format values that are likely to be long text by using <pre></pre> preserve text formatting
        for i in range(0,len(FieldItems)):
            item = FieldItems[i]
            if item[1] == None:
                continue            
            if item[0].lower() in ['commentstring','description','comment','obcomment','protocoltext'] and item[1] != None:
                if re.search('\<pre\>',item[1],re.IGNORECASE) == None:
                    FieldItems[i] = (item[0],"<pre>%s</pre>"%item[1])
                
            

                
        ListItems = [item for item in self.databaseFields.items() if isinstance(item[1],ListType) and len(item[1]) > 0]           
        ListDictionaryItems = [item for item in ListItems if isinstance(item[1][0],DictType)]
        ListOtherItems = [item for item in ListItems if not isinstance(item[1][0],DictType)]        
        nonSystemFieldRows =  reduce(lambda x,y:x+y, ['<tr><td class=fieldname>'+self.getColumnAlias(key)+'</td><td class=fieldvalue>'+tidyout(str(value), 512, 1,'')[0]+'</td></tr>\n' \
        #nonSystemFieldRows =  reduce(lambda x,y:x+y, ['<tr><td class=fieldname>'+self.getColumnAlias(key)+'</td><td class=fieldvalue>'+str(value)+'</td></tr>\n' \
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


        # if there are any displayprocedures attached to this object, now run those.
        # development of code for display of dna concentration
        # example of call :
        # myGraphHTML = eval('getSampleFactDisplay(obid=self.databaseFields["obid"], usercontext="default", fetcher=self.fetcher, imagepath=self.imagepath, \
        #                tempimageurl=self.tempimageurl, sectionheading="Genotype Sample Summaries - Concentration",graphtitle1="Concentration",graphtitle2="(ng/ul)",\
        #                 barwidth=10,factnamespace="Genotype Sample", attributename="Concentration (ng/ul)")')
        
        # some of these require a connection
        connection = databaseModule.getConnection()
        if self.obState['DYNAMIC_DISPLAYS'] > 0:
            from displayProcedures import getSampleFactDisplay,getGenepixThumbnailDisplay,getSpotExpressionDisplay,getExpressionMapDisplay,getInlineURL,getAlleleFrequencyDisplay,getSequenceAnnotationBundle,getAffyProbeGraphs,getInlineTable
            obmodulelogger.info('running non-virtual display functions')
            for displayFunction in self.displayFunctions:
                # exclude virtual functions - these will be instantiated in specific contexts or subclasses
                if displayFunction[7] == None:
                    obmodulelogger.info('running %s'%displayFunction[0])
                    myGraphHTML = eval(displayFunction[0])
                    table += myGraphHTML
                    
           
        #initDisplayFunctions(self)
                                  
        
        
        obmodulelogger.info('listing dictionaries')
        # if we have formatted dictionaries , output these first , they are usually the most interesting
        # content of the object
        if len(ListDictionaryRows) >  0:
            table += ListDictionaryRows

        obmodulelogger.info('listing fields')
        # next the field rows
        table += nonSystemFieldRows

        obmodulelogger.info('listing lists')
        # next the other lists
        if len(ListOtherRows) > 0:
            table += ListOtherRows

        return table

    def myHTMLEditRows(self, table, width=800,context='default'):
        """ descendants of the ob class will usually override this method rather than the
        entire asHTMLEditor method - this method supplies the contents of the summary
        panel
        """
        EditItems = [item for item in self.databaseFields.items() if not isinstance(item[1],ListType)]
        editHTML = ""
        for key, value in EditItems:
            # figure out interface element to use
            if len(value) > 80 or '\r' in value or '\n' in value:
                editHTML = """
                <tr>
                <td class=fieldname>%(key)s</td>
                <td class=fieldvalue> <textarea name = %(key)s rows=4 cols=40>%(value)s</textarea> </td>
                </tr>
                """%{'key' : key, 'value' : value}
            else:
                editHTML = """
                <tr>
                <td class=fieldname>%(key)s</td>
                <td class=fieldvalue><input name=%(key) type=text size=%(size)s value=%(value)s</td>
                </tr>
                """%{'key' : key, 'value' : value, 'size' : size}
            
        nonSystemFieldRows =  reduce(lambda x,y:x+y, ['<tr><td class=fieldname>'+self.getColumnAlias(key)+'</td><td class=fieldvalue>'+tidyout(str(value), 512, 1,'')[0]+'</td></tr>\n' \
        #nonSystemFieldRows =  reduce(lambda x,y:x+y, ['<tr><td class=fieldname>'+self.getColumnAlias(key)+'</td><td class=fieldvalue>'+str(value)+'</td></tr>\n' \
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

        obmodulelogger.info('listing fields')
        # next the field rows
        table += nonSystemFieldRows


        return table

    

    def myExternalLinks(self, heading , table, width=800,context='default'):
        """ descendants of the ob class will usually override this method rather than the
        entire asHTMLRows method - this method supplies the contents of the html links panel
        """
#        heading += """
#           <img src="%s%s" width=10/><a href="#externallinks" class=menuitem> Related Resources </a>
#        """%(self.imageurl,"space.gif")

        # if appropriate , check permissions
        linkAccess = True
        if self.obState['SECURITY_POLICIES'] > 0:
            linkAccess = self.runSecurityFunctions(context,"external links") # this controls access to the related resources panel
            #summaryAccess = False
        if linkAccess:        
            

            uriRows = ''
            mapNamePrefix="linkout%d"
            mapIndex=0
            for urituple in self.uriFields:
                mapIndex += 1
                if urituple[6] == None:
                    if urituple[2] != 'system' :
                        uriRow = None
                        if urituple[8] != None:
                            if str.lower(urituple[8]) == 'download link':
                                uriRow =  "<tr><td><button type=button class=\"CSSDownloadButton\" onclick=\"window.open('" + urituple[0] + "'); return true;\">" + urituple[1] + "</button></td></tr>\n"
                        if uriRow == None:
                            uriRow =  '<tr><td><a href="'+urituple[0]+\
                               '" target="externallink">'+urituple[1]+'</a></td><td>(added by '+urituple[2] + ')</td></tr>\n'
                        uriRows += uriRow
                    else:
                        uriRows +=  '<tr><td colspan="2"><a href="'+urituple[0]+\
                           '" target="externallink">'+urituple[1]+'</a></tr>\n'
                else:
                    mapName=mapNamePrefix%mapIndex

                    # attempt to convert the icon attributes, stored using python dictionary or list syntax, to string for html tag
                    attributeString="height=32 width=32"
                    attributeDict = None
                    if urituple[7] != None:
                        try:
                            attributeDict = eval(urituple[7])

                            # sometimes attributes are stored as (e.g.) '(32,32)' or '[32,32]'
                            if isinstance(attributeDict,ListType) or isinstance(attributeDict,TupleType):
                                attributeDict = {
                                    "height"  :attributeDict[0],
                                    "width" : attributeDict[1]
                                }
                            attributeString = reduce(lambda x,y:x+' '+y+'='+str(attributeDict[y]),attributeDict.keys(),'')
                        except:
                            None
                            
                    hotspot="0,0,32,32"
                    # attempt to refine hotspot, look for height= width= attributes
                    if attributeDict != None:
                        ucDict = dict([(key.upper(), attributeDict[key]) for key in attributeDict.keys()])
                        try :
                            hotspot="0,0,%s,%s"%(ucDict["WIDTH"],ucDict["HEIGHT"])
                        except:
                            None
                        

                    if urituple[2] != 'system' :
                        uriRows += """<tr><td><img src="%s" %s halign="center" usemap="#%s" border="0"/>
                            <map name="%s" id="%s">
                            <area href="%s"
                            shape="rect"
                            coords="%s"
                            alt="%s"
                            target=%s/>
                            </map>                
                            </td><td>(added by %s)</td></tr>\n"""%\
                            (urituple[6],attributeString,mapName,mapName,mapName,urituple[0],hotspot,urituple[1],mapName,urituple[2])
                    else:
                        uriRows += """<tr><td colspan="2"><img src="%s" %s halign="center" usemap="#%s" border="0"/>
                            <map name="%s" id="%s">
                            <area href="%s"
                            shape="rect"
                            coords="%s"
                            alt="%s"
                            target=%s/>
                            </map>                
                            </td></tr>\n"""%\
                            (urituple[6],attributeString,mapName,mapName,mapName,urituple[0],hotspot,urituple[1],mapName)

                        
                    
                        

                

            #uriRows =  reduce(lambda x,y:x+y, ['<tr><td>added by '+urituple[2] + '</td><td><a href="'+urituple[0]+\
            #                                           '" target="externallink">'+urituple[1]+'</a></td></tr>\n' \
            #                                           for urituple in self.uriFields])

                    #<img src="/sheep/html/tmp/1923715962.gif" halign="center" usemap="#1923715962" border="0"/>
                    #<p/>
                    
                    #<map name="1923715962" id="1923715962">
                    #<area href="/cgi-bin/sheepgenomics/join.py?context=geneindex&totype=240&jointype=250&joininstance=224584"
                    #shape="rect"
                    #coords="0,0,32,32"
                    #alt="Link to related information"/>
                    #</map>



                                                       
            uriRows = '<tr><td colspan="2"><table border="0">' + uriRows + '</table></td></tr>'                                                   

            table += """
                <tr class=%s>
                <td colspan=2>
                <table class=%s>
                <tr>            
                <td align=left >
                <a name="externallinks" class=whiteheading>
                Related Resources
                </a>
                </td>
                <td align=right>
                <a class=menuitem_small href="#top"> Top </a>
                </td>
                </tr>
                </table>
                </td>            
                </tr>
                """%(self.theme["section heading class"],self.theme["section heading class"])

            table += uriRows
        else:
            table += """
                <tr class=%s>
                <td colspan=2>
                <table class=%s>
                <tr>
                <td colspan=2 >
                <a name="externallinks" class=whiteheading>
                Related Resources
                </a>
                </td>
                </tr>
                <tr>
                <td colspan=2 align=left>
                <img src=%s alt="%s"/>
                </td>
                </tr>                
                </table>
                </td>
                </tr>                
                """%(self.theme["section heading class"],self.theme["section heading class"],self.padlockurl,self.padlocktext)            
            
        return (heading, table)
        
        
    def getMenuBarHTML(self, metadata, context) :
        """ method for displaying the HTML of the fancy menu-bar """

        return '<span class="CSSMenuTitle" onmouseout="leaveField(this);" onmouseover="hoverField(this);showEditMenu(this);">Edit</span>'\
        '<span class="CSSMenuTitle" onmouseout="leaveField(this);" onmouseover="hoverField(this);showAnnotateMenu(this);">Annotate</span>'\
        '<span class="CSSMenuTitle" onmouseout="leaveField(this);" onmouseover="hoverField(this);showViewMenu(this);">View</span>'\
        '<span class="CSSMenuTitle" onmouseout="leaveField(this);" onmouseover="hoverField(this);showToolsMenu(this);">Tools</span>'\
        '<span class="CSSMenuTitle" onmouseout="leaveField(this);" onmouseover="hoverField(this);showHelpMenu(this);">Help</span>'
    

    def getMenuBarJS(self, metadata, context) :
        """ method for displaying the JavaScript of the fancy menu-bar """
        #Edit | Annotate | View | Tools | Help
        #Get the "defaultMenuJS" and "dynamicMenuJS" strings from htmlModule, and populate with helpchunk
        
        if metadata == 1 :
            helpchunk = "return brdfpopup(\"%s\",\"%s\")"%('%s %s'%(self.metadataFields['displayname'],self.databaseFields['obid']),self.makeAboutMe(context))
        else :
            helpchunk = "return brdfpopup(\"%s\",\"%s\")"%('BRDF Object %s'%self.databaseFields['obid'],self.makeAboutMe(context))
        
        menuDict = {'helpchunk' : helpchunk,
                    'addCommentURL' : self.addCommentURL%(context,self.databaseFields['obid'],self.databaseFields['xreflsid']),
                    'addLinkURL' : self.addLinkURL%(context,self.databaseFields['obid'],self.databaseFields['xreflsid'])}
        
        return defaultMenuJS%(dynamicMenuJS%menuDict)
        
        
    def asHTMLTableRows(self,title='',width="90%",context='default'):
        """ method for rendering this object as rows in a  table examples :
        http://localhost/cgi-bin/nutrigenomics/fetch.py?context=dump&obid=340337
        An object may be only partly instantiated - e.g. no metadata, or no links -
        so the code tests the state of the object at various points, and will
        only output as appropriate to the state of the object"""

        if context == 'geneindex':
            width=900

        # the structure of the databaseFields dictionary is
        # name:value
        # where value is either a scalar field or a list. If it is a list
        # it is probably a list of dictionaries, one per record of some details table
        # 
        # We need to format differently, depending on what the value is - some values contain
        # nested structure. Currently we treat scalar values, Lists-of-dictionaries and Lists-of-Other
        FieldItems = [item for item in self.databaseFields.items() if not isinstance(item[1],ListType)]
        ListItems = [item for item in self.databaseFields.items() if isinstance(item[1],ListType) and len(item[1]) > 0]        
        ListDictionaryItems = [item for item in ListItems if isinstance(item[1][0],DictType)]
        ListOtherItems = [item for item in ListItems if not isinstance(item[1][0],DictType)]
        #self.logger.info("ListDictionaryItems length = %s"%len(ListDictionaryItems))
        
        FieldItems.sort()
        ListDictionaryItems.sort()
        ListOtherItems.sort()


        systemFieldRows =  reduce(lambda x,y:x+y, ['<tr><td class=fieldname>'+ self.getColumnAlias(key)+'</td><td class=fieldvalue>'+str(value)+'</td></tr>\n' \
                                                   for key,value in FieldItems if key in ( \
                                        'obid','obtypeid','xreflsid','createddate','createdby','lastupdateddate',\
                                        'lastupdatedby','checkedout','checkedoutby','checkoutdate','obkeywords','statuscode') and self.getColumnAlias(key) != None])
        systemFieldRows = '<tr><td class=inside colspan="2"><table class=inside border="0">' + systemFieldRows + '</table></td></tr>'                                                   

        if title == '':
            if self.obState['METADATA'] == 1:
                title=self.metadataFields['displayname'] + ' : ' + self.databaseFields['xreflsid']
            else:
                title=self.databaseFields['xreflsid']
        
        menuHTML = self.getMenuBarHTML(self.obState['METADATA'],context)

        thisfetcher = "%s?obid=%s&context=default"%(self.fetcher, self.databaseFields["xreflsid"])
        heading = """
        <table class=brdftop1 cellpadding="0" cellspacing="0" width='%s' border=1>
        <tr class="%s"><td colspan="2">
            <table><tr><td>
                <img src="%s" usemap="#obtypelink" border="0" height="42" width="42"/>
            </td><td halign=center>
                <a name="top"/><h1><b>%s</b></h1></a><p/>
            </td></tr>
            <tr><td colspan="2">
                %s
            </td></tr></table>
            &nbsp;
            &nbsp;
            &nbsp;
            <a href="%s" class=menuitem_small> Home </a>
            &nbsp;
            &nbsp;
            &nbsp;
            <a href="%s" class=menuitem_small> Link To This </a>
            
        </td></tr>
        """%(str(width),self.theme["object heading class"],self.imageurl+self.metadataFields['displayurl'],title,menuHTML,self.homeurl,thisfetcher)

        table = ""


        if context in ['default','summary','geneindex']:

            summaryType=""
            if context == 'geneindex':
                summaryType = "(Gene Index View)"
                
            # now do the information summary
            obmodulelogger.info('setting up heading')
#            heading += """
#            <img src="%s%s" width=10/><a class=menuitem href="#informationsummary"> Information Summary </a>
#            """%(self.imageurl,"space.gif")            


            # if appropriate , check permissions
            summaryAccess = True
            if self.obState['SECURITY_POLICIES'] > 0:
                summaryAccess = self.runSecurityFunctions(context,"information summary")
            #summaryAccess = False
            if summaryAccess:

                table += """
                <tr class=%s>
                <td colspan=2>
                <table class=%s>
                <tr>
                <td align=left >
                <a name="informationsummary" class=whiteheading>
                Information Summary %s
                </a>
                </td>
                </tr>
                </table>
                </td>
                </tr>
                """%(self.theme["section heading class"],self.theme["section heading class"],summaryType)

                table =  self.myHTMLSummary(table, width,context)
            # access to summary OK
            else:
                table += """
                <tr class=%s>
                <td colspan=2>
                <table class=%s>
                <tr>
                <td colspan=2 >
                <a name="informationsummary" class=whiteheading>
                Information Summary 
                </a>
                </td>
                </tr>
                <tr>
                <td colspan=2 align=left>
                <img src=%s alt="%s"/>
                </td>
                </tr>                
                </table>
                </td>
                </tr>                
                """%(self.theme["section heading class"],self.theme["section heading class"],self.padlockurl,self.padlocktext)
                
        # if they wanted the summary



        # tools panel if applicable
        if context in ['default','summary','geneindex']:
            toolsHTML = self.myToolsPanel(table, width,context)
            if toolsHTML != None:
  
                # do the tools panel
                obmodulelogger.info('setting up tools panel')
#                heading += """
#                <img src="%s%s" width=10/><a class=menuitem href="#tools"> Tools </a>
#                """%(self.imageurl,"space.gif")            


                # if appropriate , check permissions
                toolsAccess = True
                if self.obState['SECURITY_POLICIES'] > 0:
                    toolsAccess = self.runSecurityFunctions(context,"tools")
                #summaryAccess = False
                if toolsAccess:


                    table += """
                    <tr class=%s>
                    <td colspan=2>
                    <table class=%s>
                    <tr>
                    <td align=left >
                    <a name="tools" class=whiteheading>
                    Tools %s
                    </a>
                    </td>
                    <td align=right>
                    <a class="CSSEditButton" href=%s>Edit</a>
                    <a class="CSSCommentButton" href="%s" target="AddComment">Add Comment</a>
                    <a class="CSSAddLinkButton" href="%s" target="AddHyperLink">Add Hyperlink</a>            
                    <a href="#top" class=menuitem_small> Top </a>
                    </td>
                    </tr>
                    </table>
                    </td>
                    </tr>
                    """%(self.theme["section heading class"],self.theme["section heading class"],summaryType,self.underConstructionURL,\
                         self.addCommentURL%(context,self.databaseFields['obid'],\
                                             self.databaseFields['xreflsid']),\
                         self.addLinkURL%(context,self.databaseFields['obid'],self.databaseFields['xreflsid'])) 

                    table =  self.myHTMLSummary(table, width,context)
                else:
                    table += """
                    <tr class=%s>
                    <td colspan=2>
                    <table class=%s>
                    <tr>
                    <td colspan=2 >
                    <a name="tools" class=whiteheading>
                    Tools 
                    </a>
                    </td>
                    </tr>
                    <tr>
                    <td colspan=2 align=left>
                    <img src=%s alt="%s"/>
                    </td>
                    </tr>                
                    </table>
                    </td>
                    </tr>                
                    """%(self.theme["section heading class"],self.theme["section heading class"],self.padlockurl,self.padlocktext)
                
        # if they wanted the summary



        # do comment section
        if context in ['default','summary','geneindex'] and self.obState['COMMENTS'] > 0:
            obmodulelogger.info('setting up comment heading using %s'%str(self.commentFields))
#            heading += """
#               <img src="%s%s" width=10/><a href="#comments" class=menuitem> Comments </a>
#            """%(self.imageurl,"space.gif")
            


            commentRows =  reduce(lambda x,y:x+y, ['<tr><td>by '+commenttuple[3]+ ' on ' + commenttuple[2].strftime("%d/%m/%y")+'</td><td bgcolor='+commenttuple[4]+'><b><i>'+commenttuple[1]+'</i></b></td></tr>\n' \
                                                   for commenttuple in self.commentFields])
            commentRows = '<tr><td colspan="2"><table border="0">' + commentRows + '</table></td></tr>'

            table += """
            <tr class=%s>
            <td colspan=2>
            <table class=%s>
            <tr>            
            <!-- <tr bgcolor=#388fbd> -->
            <td align=left >
            <a name="comments" class=whiteheading>
            Comments
            </a>
            </td>
            <td align=right>
            <a class="CSSCommentButton" href="%s" target="AddComment">Add Comment</a>              
            <a href="#top" class=menuitem_small> Top </a>          
            </td>
            </tr>
            </table>
            </td>            
            </tr>
            """%(self.theme["section heading class"],self.theme["section heading class"],self.addCommentURL%(context,self.databaseFields['obid'],\
                                     self.databaseFields['xreflsid']))

            table += commentRows


        # do hyperlinks section
        if context in ['default','summary','geneindex'] and self.obState['HYPERLINKS'] > 0:
            obmodulelogger.info('setting up hyperlinks using %s'%str(self.uriFields))
            (heading,table) = self.myExternalLinks(heading ,table, width,context)



        # do listmembership section
        if context in ['default','summary','geneindex'] and self.obState['LISTMEMBERSHIP'] > 0:
            obmodulelogger.info('setting up list membership using %s'%str(self.listMembership))
#            heading += """
#               <img src="%s%s" width=10/><a href="#listmembership" class=menuitem> List Membership </a>
#            """%(self.imageurl,"space.gif")

            listRows =  """
            <tr>
               <th>List Description </th>
               <th>Membership Count </th>
               <th>Date Created</th>
            </tr>
            """

            # we filter the list display to only show "informative" lists, and avoid duplication
            # note that the list is sorted by date so the code below will result in the latest
            # searches being displayed
            listDict={}
            for listtuple in self.listMembership:
                if listtuple[1] != None:                    
                    listhash = listtuple[1].strip().lower()
                    listhash = re.sub('archived : ','',listhash)
                    listhash = re.sub('search.*for\s','',listhash)
                    listhash = re.sub('\(.*\)','',listhash)
                    listhash = re.sub('\s+','',listhash)
                    listhash = re.sub('%','',listhash)
                    if len(listhash) > 2:
                        listDict[listhash] = listtuple
            obmodulelogger.info("Using informative list membership of : %s"%str(listDict))


            for listtuple in listDict.values():
                listRows += """
                <tr>
                    <td> <img src=%s height=32 width=32 alt="List type : %s"/> <a href=%s?obid=%s&context=default target=%s>%s</a></td>
                    <td> %s </td>
                    <td> %s </td>
                </tr>
                """%(os.path.join(self.imageurl,listtuple[5]),listtuple[4],self.fetcher,listtuple[0],listtuple[0],listtuple[1],listtuple[2],listtuple[3])
                    
            
            listRows = '<tr><td colspan="2"><table border="1">' + listRows + '</table></td></tr>'                                                   

            table += """
            <tr class=%s>
            <td colspan=2>
            <table class=%s>
            <tr>            
            <td align=left >
            <a name="listmembership" class=whiteheading>
            List Membership
            </a>
            </td>
            <td align=right>
            <a class=menuitem_small href="#top"> Top </a>
            </td>
            </tr>
            </table>
            </td>            
            </tr>
            """%(self.theme["section heading class"],self.theme["section heading class"])

            table += listRows
            
        

        #if we can obtain links to show the structure of this object, and related objects, output these first.
        if self.obState['LINKS'] == 1:

            #self.logger.info("hello2")
            

            
            # map the relations involving this object. For each we obtain its definition and display it
            if context in ['default']:
#                heading += """
#                    <img src="%s%s" width=10/><a class=menuitem href="#informationmap"> Information Map </a>
#                """%(self.imageurl,"space.gif")


                mapAccess = True
                if self.obState['SECURITY_POLICIES'] > 0:
                    mapAccess = self.runSecurityFunctions(context,"information map")
                #mapAccess = False
                if mapAccess:                
                    ##### this section shifted so it lives under the information map
                    # First handle the case if this is an op - we emit a glyph that gives the definition of this op - but only
                    # bother if this is a binary or greater relation. Actually this is not quite right as means you can't click
                    # up to the parent object from a named fact (for example , up to the ontology from an ontology term) - leave it for now though
                    opGlyphHTML = ""
                    if self.metadataFields['isop']:
                        # assemble the relation descriptor for this relation. This consists of a tuple
                        # of tuples, each tuple being the name and instance count of a member object
                        if self.metadataFields['opdefinition'] != None:
                            obdescriptors = [ (linkedob['obdisplay'], linkedob['instancecount'],\
                                           os.path.join(self.imagepath,linkedob['obdisplayurl']))  \
                                        for linkedob in self.metadataFields['opdefinition'] ]
                        #if len(obdescriptors) > 1:      # if you want to suppress the glyph for fact tables - but a nuisance if you do this
                        if True:
                            (myGlyphName,myGlyphMap) = makeOpGlyph(linkText=self.metadataFields["displayname"], imageDirectory=self.imagepath, obs=obdescriptors, instanceCount = 1,linkFirstObject=True,namedInstances=False)


                            linkCount = 1
                            for linkedob in self.metadataFields['opdefinition']:
                                link = self.jointomemberurl%(context,linkedob['obtypeid'],self.metadataFields['obtypeid'],self.databaseFields['obid'])
                                myGlyphMap = myGlyphMap.replace("__link%s__"%linkCount , link)
                                linkCount += 1

                            # handle fact table - there is an additional link, for the box
                            #if len(self.metadataFields['opdefinition']) == 1:
                            #    link = self.jointonullurl%(context,self.metadataFields['obtypeid'],self.databaseFields['obid'])
                            #    myGlyphMap = myGlyphMap.replace("__link%s__"%linkCount , link)
                            #    linkCount += 1                    
                        
                    
                            myGlyphHTML= """
                            <tr>
                            <td colspan=2 align=right>
                            <p/>
                            <img src="%s%s" halign="center" usemap="#%s" border="0"/>
                            <p/>
                            %s
                            </td> 
                            </tr>
                            """
                            opGlyphHTML = myGlyphHTML%(self.tempimageurl,myGlyphName,myGlyphName.split('.')[0],myGlyphMap)
                            #table +=  myGlyphHTML                
                            ##### end shifted section
                    
                    
                    glyphSectionHeading= """
                      <tr class=%s>
                      <td colspan=2>
                      <table class=%s>
                      <tr>                  
                      <td align=left>
                      <a name="informationmap" class=whiteheading>
                      Information Map
                      </a>
                      </td>
                      <td align=right>
                      <a href="#top" class=menuitem_small> Top </a>
                      </td>
                      </tr>
                      </table>
                      </td>                  
                      </tr>                
                     """%(self.theme["section heading class"],self.theme["section heading class"])
                    allGlyphHTML = ""

                    obmodulelogger.info('getting relation URLs....')

                    # we need to take the related op definitions in the most presentable order.
                    # Currently , this means the "fact" definitions at the top - i.e. in order
                    # of complexity of the op.
                    optypes = self.relatedOpDefinitions.keys()
                    optypes.sort(\
                        lambda x,y: len(self.relatedOpDefinitions[x])  - len(self.relatedOpDefinitions[y]) )
                                        
                        
                    glyphCount = 0
                    for optypeid in optypes:
                        glyphCount += 1
                        obdescriptors = [ (linkedob['obdisplay'], linkedob['instancecount'],\
                                           os.path.join(self.imagepath,linkedob['obdisplayurl']))  \
                                       for linkedob in self.relatedOpDefinitions[optypeid] ]
                        # note that in the following line , the namedinstances attribute is actually an attribute of the relation as
                        # a whole - for convenience it is stored in each record of the opdefinition
                        linkrelationinstance = self.relatedOpDefinitions[optypeid][0]['namedinstances']
                        # do not link trivial relations. Currently, this means predicate links. 
                        if self.relatedOpDefinitions[optypeid][0]['optablename'] in ('predicatelink'):
                            linkrelationinstance = False


                        # if this is a list , and there is a virtual relation defined, then do not link
                        # any non-virtual relations. Virtual relations on lists , link to the correctly
                        # typed underlying table, while non-virtual relations link to the ob table. This
                        # link to the ob table is very slow to instantiate and is not informative
                            
                        (myGlyphName,myGlyphMap) = makeOpGlyph(linkText=self.metadataFields['obrelations'][optypeid], imageDirectory=self.imagepath, obs=obdescriptors,\
                                                  instanceCount=self.relatedOpInstanceCounts[optypeid],namedInstances=linkrelationinstance)

                        obmodulelogger.info('mapped relations OK for %s'%optypeid)
                        obmodulelogger.info(myGlyphName)
                        obmodulelogger.info(myGlyphMap)
                    


                        linkCount = 1                                
                                
                        for linkedob in self.relatedOpDefinitions[optypeid]:
                            link = self.jointooburl%(context,linkedob['obtypeid'],self.databaseFields['obid'],optypeid)
                            myGlyphMap = myGlyphMap.replace("__link%s__"%linkCount , link)
                            linkCount += 1
             
                        # handle fact table - there is an additional link, for the box
                        if len(obdescriptors) == 1:
                            link = self.joinfacturl%(context,self.databaseFields['obid'],optypeid)
                            myGlyphMap = myGlyphMap.replace("__link%s__"%linkCount , link)
                            linkCount += 1                        

                        # handle ops that have named instances - there is an additional link to the
                        # op instance itself, when users click on relation name
                        if self.relatedOpDefinitions[optypeid][0]['namedinstances']:
                            link = self.jointoopurl%(context,self.databaseFields['obid'],optypeid)
                            myGlyphMap = myGlyphMap.replace("__link%s__"%linkCount , link)
                            linkCount += 1
                            
                        
                        # if this is either a fact or a link - i.e. len(self.relatedOpDefinitions[optypeid]) <= 2 - then
                        # we output two glyphs per row
                        if len(self.relatedOpDefinitions[optypeid]) <= 2 :
                            if glyphCount%2 == 1 :
                                myGlyphHTML= """
                                    <tr>
                                    <td align=left>
                                    <img src="%s%s" halign="left" usemap="#%s" border="0"/>
                                    <p/>
                                    %s
                                    </td>
                                """
                            else:
                                myGlyphHTML= """
                                    <td align=left>
                                    <img src="%s%s" halign="left" usemap="#%s" border="0"/>
                                    <p/>
                                    %s
                                    </td>
                                    </tr>
                                """                            
                                
                        else:
                            myGlyphHTML= """
                                    <tr>
                                    <td colspan=2 align=left>
                                    <img src="%s%s" halign="left" usemap="#%s" border="0"/>
                                    <p/>
                                    %s
                                    </td>
                                    </tr>"""
                        myGlyphHTML = myGlyphHTML%(self.tempimageurl,myGlyphName,myGlyphName.split('.')[0],myGlyphMap)
                        allGlyphHTML +=  myGlyphHTML                
                    
                    
                    
                    # for all the ops

                    allGlyphHTML += """
                    </td>
                    </tr>
                    """
                    table +=  glyphSectionHeading + "<tr><td colspan=2><table><tr><td>" + opGlyphHTML + allGlyphHTML + "</td></tr></table></td></tr>"
                    #table +=   allGlyphHTML               
                # if access to the information map is allowed
                else:
                    table += """
                    <tr class=%s>
                    <td colspan=2>
                    <table class=%s>
                    <tr>
                    <td colspan=2 >
                    <a name="informationmap" class=whiteheading>
                    Information Map 
                    </a>
                    </td>
                    </tr>
                    <tr>
                    <td colspan=2 align=left>
                    <img src=%s alt="%s"/>
                    </td>
                    </tr>                
                    </table>
                    </td>
                    </tr>                
                    """%(self.theme["section heading class"],self.theme["section heading class"],self.padlockurl,self.padlocktext)                
            # if the view wanted the glyphs
        # if the object has been initialised with link info
            



        

        # if they want the record status
        if context in ['default']:
            obmodulelogger.info('listing system fields')
            # next system field
#            heading += """
#               <img src="%s%s" width=10/><a href="#recordstatus" class=menuitem> Record Status </a>
#            """%(self.imageurl,"space.gif")                  
            table += """
            <tr class=%s>
            <td colspan=2>
            <table class=%s>
            <tr>            
            <!-- <td colspan=2 align=left> -->
            <td align=left> 
            <a name="recordstatus" class=whiteheading>
            Record Status
            </a>
            </td>
            <td align=right>
            <!--<a class="CSSCheckOutButton" href=%s>Check Out Record</a>-->
            <a href="#top" class=menuitem_small> Top </a>
            </td>
            </tr>
            </table>
            </td>            
            </tr>"""%(self.theme["section heading class"],self.theme["section heading class"],self.underConstructionURL)
            table += systemFieldRows
        # if they want record status
            
        

        # if metadata wanted in view
        ##### turned off 5/2006 - there is no such view as database summary currently ######
        if context in ['databaseview']:
            obmodulelogger.info('listing metadata')
            # if metadata is available, format and append that
            if self.obState['METADATA'] == 1:
#                heading += """
#                <img src="%s%s" width=10/><a href="#databaseinformation" class=menuitem> Database Information </a>
#                """%(self.imageurl,"space.gif")     
                metadataRows = reduce(lambda x,y:x+y, ['<tr><td class=fieldname>'+key+'</td><td class=fieldvalue>'+str(value)+'</td></tr>\n' for key,value in self.metadataFields.items()])
                metadataRows = '<tr><td class=inside colspan="2"><table class=inside border="0">' + metadataRows + '</table></td></tr>'
                table += """
                <tr bgcolor=#388fbd>
                <td colspan=2>
                <table class=%s>
                <tr>                
                <td colspan=2 align=center>
                <a name="databaseinformation" class=menuitem>
                Database Information
                </a>
                <a href="#top" class=menuitem_small> Top </a>
                </td>
                </tr>
                </table>
                </td>                
                </tr>"""            
                table += metadataRows
            # if we have metadata
        # if we wanted metadata


        #heading += "</td>\n</tr>\n"
        oldmap = """
            <map name="obtypelink" id="obtypelink">
            <area href="zz_contents.htm"
            shape="rect"
            coords="0,0,42,42"
            alt="Describe this object"
            target="obdescription"/>
            </map>"""
        if self.obState['METADATA'] == 1:
            map = """
                <map name="obtypelink" id="obtypelink">
                <area nohref
                shape="rect"
                coords="0,0,42,42"
                alt="Click To Describe this object"
                target="obdescription" onclick="return brdfpopup('%s','%s')"/>
                </map>"""%('%s %s'%(self.metadataFields['displayname'],self.databaseFields['obid']),self.makeAboutMe(context))
        else:
            map = """
                <map name="obtypelink" id="obtypelink">
                <area nohref
                shape="rect"
                coords="0,0,42,42"
                alt="Click To Describe this object"
                target="obdescription" onclick="return brdfpopup('%s','%s')"/>
                </map>"""%('BRDF Object %s'%self.databaseFields['obid'],self.makeAboutMe(context))                                  

#        heading += """
#               <img src="%s%s" width=10/><a href="%s" class=menuitem> Home </a>
#            """%(self.imageurl,"space.gif",self.homeurl)                 
#        
#        heading += "</td></tr></table></td>\n</tr>\n"
        
        table = heading + table
            
        table += '</table>\n'
        obmodulelogger.info('done setting up HTML - returning table : ')

        #obmodulelogger.info(table)

        
        return table + map


    def asHTMLEditor(self,title='',width=800,context='edit'):
        # example http://devnbrowse.agresearch.co.nz/cgi-bin/nutrigenomics/fetch.py?obid=11868194&context=edit&target=ob
        """ method for rendering this object as an edit form"""


        # 
        # We need to format differently, depending on what the value is - some values contain
        # nested structure. Currently we treat scalar values, Lists-of-dictionaries and Lists-of-Other
        FieldItems = [item for item in self.databaseFields.items() if not isinstance(item[1],ListType)]
        ListItems = [item for item in self.databaseFields.items() if isinstance(item[1],ListType) and len(item[1]) > 0]        
        ListDictionaryItems = [item for item in ListItems if isinstance(item[1][0],DictType)]
        ListOtherItems = [item for item in ListItems if not isinstance(item[1][0],DictType)]
        
        FieldItems.sort()
        ListDictionaryItems.sort()
        ListOtherItems.sort()


        systemFieldRows =  reduce(lambda x,y:x+y, ['<tr><td class=fieldname>'+ self.getColumnAlias(key)+'</td><td class=fieldvalue>'+str(value)+'</td></tr>\n' \
                                                   for key,value in FieldItems if key in ( \
                                        'obid','obtypeid','xreflsid','createddate','createdby','lastupdateddate',\
                                        'lastupdatedby','checkedout','checkedoutby','checkoutdate','obkeywords','statuscode') and self.getColumnAlias(key) != None])
        systemFieldRows = '<tr><td class=inside colspan="2"><table class=inside border="0">' + systemFieldRows + '</table></td></tr>'                                                   

        if title == '':
            if self.obState['METADATA'] == 1:
                title="Editing  %s : %s"%(self.metadataFields['displayname'] , self.databaseFields['xreflsid'])
            else:
                title="Editing : %(xreflsid)s"%self.databaseFields
                
        heading = """
        <table class=brdftop1 cellpadding="0" cellspacing="0" width='%s' border=1>
        <tr class="%s"><td colspan="2">
            <table><tr><td>
                <img src="%s" usemap="#obtypelink" border="0" height="42" width="42"/>
            </td><td halign=center>
                <a name="top"/><h1><b>%s</b></h1></a><p/>
            </td></tr>
            </table>
        </td></tr>
        """%(str(width),self.theme["object heading class"],self.imageurl+self.metadataFields['displayurl'],title)

        table = ""


        if context in ['edit']:

            summaryType=""
            if context == 'geneindex':
                summaryType = "(Gene Index View)"
                
            # now do the information summary
            obmodulelogger.info('setting up heading')
            editAccess = False
            if self.obState['SECURITY_POLICIES'] > 0:
                editAccess = self.runSecurityFunctions(context,"edit_%(displayname)s"%self.metadataFields)
            if editAccess:
                table += """
                <tr class=%s>
                <td colspan=2>
                <table class=%s>
                <tr>
                <td align=left >
                <a name="editable" class=whiteheading>
                %s
                </a>
                </td>
                </tr>
                </table>
                </td>
                </tr>
                """%(self.theme["section heading class"],self.theme["section heading class"],title)

                table =  self.myHTMLEditor(table, width,context)
            # access to edit OK
            else:
                table += """
                <tr class=%s>
                <td colspan=2>
                <table class=%s>
                <tr>
                <td colspan=2 >
                <a name="edittable" class=whiteheading>
                %s
                </a>
                </td>
                </tr>
                <tr>
                <td colspan=2 align=left>
                <img src=%s alt="%s"/>
                </td>
                </tr>                
                </table>
                </td>
                </tr>                
                """%(self.theme["section heading class"],self.theme["section heading class"],title,self.padlockurl,self.padlocktext)
                
        
        table = heading + table
            
        table += '</table>\n'
        obmodulelogger.info('done setting up HTML - returning table : ')

        #obmodulelogger.info(table)

        
        return table 
    

    
        

        
