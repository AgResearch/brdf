#
# This module implements classes relating to data forms
#
########################  change log ########################
from types import *


import globalConf
import agbrdfConf # !!!!!!! remove - only for testing
import databaseModule # !!!!!! remove - only for testing


import csv
from brdfExceptionModule import brdfException
from opmodule import op
from obmodule import ob
#from dataImportModule import dataSourceOb, importFunction, importProcedureOb, labResourceImportFunction,microarrayExperimentImportFunction,\
#      databaseSearchImportFunction, dataSourceList
from dataImportModule import dataSourceOb, importFunction, importProcedureOb, dataSourceList



from htmlModule import tidyout, defaultMenuJS, HTMLdoctype, getStyle
import os
import sys
import logging
import string
import re
from datetime import date
from databaseModule import getConnection



dataformsmodulelogger = logging.getLogger('dataformsmodule')
#hdlr = logging.FileHandler('c:/temp/nutrigenomicsforms.log')
dataformsmodulehdlr = logging.FileHandler(os.path.join(globalConf.LOGPATH,'dataformsmodule.log'))
dataformsmoduleformatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
dataformsmodulehdlr.setFormatter(dataformsmoduleformatter)
dataformsmodulelogger.addHandler(dataformsmodulehdlr) 
dataformsmodulelogger.setLevel(logging.INFO)                                                      


class basicForm ( dataSourceList ):
    """ a basic form provides a single record  interface """
    def __init__(self):
        dataSourceList.__init__(self)

    def initFromDatabase(self, identifier, connection):  
        dataSourceList.initFromDatabase(self, identifier, connection)


        # retrieve form-level details
        sql= """
        select
           factnamespace,
           attributename,
           attributevalue
        from
           datasourcelistfact
        where
           datasourcelist = %(obid)s
        """
        dataformsmodulelogger.info("executing %s to obtain form level details"%str(sql%self.databaseFields))
        formCursor = connection.cursor()
        formCursor.execute(sql,self.databaseFields)
        details = formCursor.fetchall()
        self.formDict = {}
        for detail in details:
            if detail[0] not in self.formDict:
                self.formDict[detail[0]] = {detail[1] : detail[2]}
            else:                
                self.formDict[detail[0]][detail[1]] = detail[2]
        
        


        # the form interface is made up of the interface of each data source , together with a 
        # form template on which these are laid out. (Note that you could also control layout by
        # setting up null "data sources" in the collection that are not form elements. However
        # there is no point since layout code can be included in the interface code of each source.
        template = ""

        # get each data source element in the collection. Elements may be of the following type :
        #
        # "Form Element"  - one or more form elements as specified in the attributes of the source
        # "SQL" - a query that will be executed and the results presented in-line in the form. This datasource may
        #         also have associated form element attributes into which the results of the query will be
        #         merged./ The query is execute in the context of a given object - i.e. the query may refer to
        #         the obid or xreflsid of an object






        

        sql = """
        select
           dlm.obid,
           ds.xreflsid,
           ds.datasourcetype,
           ds.obid,
           dlm.listorder,
           dlm.xreflsid
        from
           datasourceob ds join datasourcenamedlistmembershiplink dlm on
           ds.obid = dlm.datasourceob
        where
           dlm.datasourcelist = %(obid)s
        order by
           dlm.listorder
        """
        dataformsmodulelogger.info("executing %s to obtain form interface"%str(sql%{"obid" : self.databaseFields["obid"]}))
        formCursor = connection.cursor()
        formCursor.execute(sql,{"obid" : self.databaseFields["obid"]})
        self.interfaceDict = {}
        elements = formCursor.fetchall()

        # we could get each data source to initialise itself from the database as a class
        # however this would be fairly inefficient, and most of the information we need
        # is related to the collection as a whole => just query the db directly for
        # all of the data source attributes
        if formCursor.rowcount > 0:
            self.interfaceDict = dict( [(item[0],{
                "xreflsid" : item[1],
                "datasourcetype" : item[2],
                "elementid" : item[3],
                "listorder" : int(item[4]),
                "interface" : {},
                "boundinterface" : {},
                "bindings" : {},
                "references" : {}, # will contain reference_type : [element1, element2, etc ]
                "interfacelsid" : item[5] 
            }) for item in elements] )        

        # retrieve interface and other info associated with each data source element
        sql= """
        select
           factnamespace,
           attributename,
           attributevalue
        from
           datasourcefact
        where
           datasourceob = %(elementid)s
        """
        for interface in self.interfaceDict:
            dataformsmodulelogger.info("executing %s to obtain form interface configuration"%str(sql%self.interfaceDict[interface]))
            formCursor = connection.cursor()
            formCursor.execute(sql,self.interfaceDict[interface])
            details = formCursor.fetchall()
            for detail in details:
                if detail[0] not in self.interfaceDict[interface]["interface"]:
                    self.interfaceDict[interface]["interface"][detail[0]] = {}
                    self.interfaceDict[interface]["interface"][detail[0]][detail[1]] = detail[2]
                else:
                    self.interfaceDict[interface]["interface"][detail[0]][detail[1]] = detail[2]


        # retrieve database and class bindings , which are attributes of the membership of each
        # element in a specific collection
        sql= """
        select
           factnamespace,
           attributename,
           attributevalue
        from
           datasourcenamedlistmembershiplinkfact
        where
           datasourcenamedlistmembershiplink = %s
        """
        for interface in self.interfaceDict:
            dataformsmodulelogger.info("executing %s to obtain datasource element bindings"%str(sql%interface))
            formCursor = connection.cursor()
            formCursor.execute(sql%interface)
            bindings = formCursor.fetchall()
            for binding in bindings:
                if binding[0] not in self.interfaceDict[interface]["bindings"]:
                    self.interfaceDict[interface]["bindings"][binding[0]] = {}
                    if binding[0] == "Interface Bindings":
                        self.interfaceDict[interface]["bindings"][binding[0]] = {"valuetext" : ""} # default empty string for data value text
                    self.interfaceDict[interface]["bindings"][binding[0]][binding[1]] = binding[2]
                else:
                    self.interfaceDict[interface]["bindings"][binding[0]][binding[1]] = binding[2]



        # retrieve references between form elements. Note that associations are between the
        # membership links, not between the data sources.
        sql = """
        select
           subjectob ,        
           predicate ,
           objectob 
        from
           (datasourcenamedlistmembershiplink dlm join
           predicatelink p on dlm.obid = p.subjectob)
        where
           dlm.datasourcelist = %(obid)s
        """
        dataformsmodulelogger.info("executing %s to obtain references"%str(sql%{"obid" : self.databaseFields["obid"]}))
        formCursor = connection.cursor()
        formCursor.execute(sql,{"obid" : self.databaseFields["obid"]})
        references = formCursor.fetchall()        
           
        for interface in self.interfaceDict:
            for reference in references:
                if reference[0] == interface:
                    if reference[1] not in self.interfaceDict[interface]["references"]:                    
                        self.interfaceDict[interface]["references"][reference[1]] = []
                    self.interfaceDict[interface]["references"][reference[1]].append(reference[2]) 


    def getInterface(self, connection, interfaceType="HTML", container={}):
        """ This method returns a bound interface - i.e. interface elements are interpolated with
        whatever data bindings are set up in the interface dictionary. What is in this
        structure depends on whether the bindInterfaceToObjects method as been called
        
        """

        dataformsmodulelogger.info("constructing abstract interface using interface dictionary %s"%self.interfaceDict)
        elements = self.interfaceDict.keys()
        elements.sort(lambda x,y:self.interfaceDict[x]["listorder"]-self.interfaceDict[y]["listorder"])

        result =""
        for elementKey in elements:
            element = self.interfaceDict[elementKey]
            dataformsmodulelogger.info("using %s"%str(element))
            
            if "Interface" in element["interface"]:
                if interfaceType in element["interface"]["Interface"]: # interface refers to the whole collection of interface info
                                                                       # related to the data source. Within that , "Interface" refers
                                                                       # to the specific HTML or other interface code

                    # "hard coded" bindings : bind the element to this interface
                    boundInterface = element["interface"]["Interface"][interfaceType]
                    boundInterface = re.sub("elementidtext","element"+str(elementKey),boundInterface) # elementid's are the obids of the datasource elements

                    # bindings that are specified in the database table. These consist of
                    # key value pairs where the key is a string in the interface to be replaced , and
                    # a value is a replacement string. This allows us to have (e.g.) a single
                    # interface for a genotype, but have different labels, help text etc , for the
                    # different contexts in which this interface appears.

                    if "Interface Bindings" in element["bindings"]:
                        for target in element["bindings"]["Interface Bindings"].keys():
                            dataformsmodulelogger.info("binding %s with %s"%(target, element["bindings"]["Interface Bindings"][target]))
                            boundInterface = re.sub(target,str(element["bindings"]["Interface Bindings"][target]),boundInterface)
                    

                    # another "hard-coded" binding. This could be overridden simply by including a substitute-rule for "valuetext" in the
                    if "Interface Bindings" in element["bindings"]:
                        boundInterface = re.sub("valuetext",str(element["bindings"]["Interface Bindings"]["valuetext"]),boundInterface) # this can be overriden by inserting specific bindings in the form config
                    

                    result += '<p/>' + boundInterface

                    
        interface = "" # replace with writes to a StringBuffer one day
        if len(container) > 0:
            for i in range(0,len(container["content"])):
                if container["contentDescriptor"][i] != "data":
                    interface += container["content"][i]
                else:
                    interface += result


        # do form level bindings
        interface = re.sub("formidtext","form"+str(self.databaseFields["obid"]),interface) # formid is the id of the collection

                    
                        
        return interface
    
        

    def bindInterfaceToObjects(self, connection, objectDict = {}):
        """
            this binds an interface using one or more  object instances. Note that as well
           as binding the data elements in the collection, with values from the
           object , the binding will also include a payload of state related internals such as object
           status (e.g. whether it is a new or existing object etc), object id (if it has been created), object lsid etc
           
           The binding involves the following :
         
         * the data values provided by the object instances 
           are used to bind matching data source elements, using the database
           binding information that is part of the collection. 
        
         * a data source element may be associated with other data sources in the collection in various
           ways. For example one data source may provide a lookup list for another. Each such association is
           processed. All queries are executed in the context of the object instance that has been
           provided. Note that the object used to bind the interface here may not be the 
           same type as the class to which the interface is usually bound. For example
           the object here may be a factory class , binding an interface for acquisition of 
           a factory product. For example - a genotype study class may here be used to 
           bind an interface that will be used to submit a new genotype observation - the interface will
           require a foreign key binding refering to the genotype study
         
         * database bindings
         * class bindings
         * associated datasources 
        
         arguments :
         interface = optionally , the unbound interface to be processed. If None, then an abstract interface is requested
         objectDict = a dictionary of one or more object specifiers like this : {className1 : obid1, className2 : obid2, etc}
         """
            
        dataformsmodulelogger.info("Bindig interface from object using %s"%str(self.interfaceDict))


        objectInstanceDict = {}
        # "className" : instance


        # instantiate the objects the we have found we need
        for className in objectDict:
            dataformsmodulelogger.info("creating object with new %s()"%className)

            # include any class imports we need here
            from studyModule import genotypeObservation, genotypeStudy
            from annotationModule import commentOb
            from listModule import obList,geneExpressionExperimentSeriesFact,namedListMembershipLink
            from dataImportModule import dataSourceOb
            from analysisModule import analysisProcedureOb

            
            objectInstanceDict[className] = eval("%s()"%className)
            objectInstanceDict[className].initFromDatabase(objectDict[className],connection)

            # apply the data from the object to all interfaces with direct bindings to this object class
            for elementid in self.interfaceDict:
                if "Class Bindings" in self.interfaceDict[elementid]["bindings"]:
                    if "Data Element" in self.interfaceDict[elementid]["bindings"]["Class Bindings"]:
                        (className, fieldName) = re.split("\.",self.interfaceDict[elementid]["bindings"]["Class Bindings"]["Data Element"])
                        if className in objectInstanceDict:
                            # we have a class binding and class instance current interface. If there is not an Interface slot for the
                            # data value then create one (the interface value slot is created dynamically if there are other
                            # interface bindings defined - but in case there are no others - e.g. a hidden field - then we may not
                            # have the value slot)
                            if "Interface Bindings" not in self.interfaceDict[elementid]["bindings"]:
                                self.interfaceDict[elementid]["bindings"]["Interface Bindings"] = {"valuetext"  : ""}

                            if "valuetext" not in self.interfaceDict[elementid]["bindings"]["Interface Bindings"]:
                                self.interfaceDict[elementid]["bindings"]["Interface Bindings"]["valuetext"]  = ""
                                
                                
                            
                            if fieldName in objectInstanceDict[className].databaseFields:
                                self.interfaceDict[elementid]["bindings"]["Interface Bindings"]["valuetext"] = objectInstanceDict[className].databaseFields[fieldName]

                                # propagate this to any other interfaces which reference this one via a foreign key *if* these other
                                # instances are either empty or have the valuetext placeholder
                                dataformsmodulelogger.info(" checking foreigh key references")
                                for clientelementid in self.interfaceDict:
                                    if "Foreign Key Reference To" in self.interfaceDict[clientelementid]["references"]:
                                        if elementid in self.interfaceDict[clientelementid]["references"]["Foreign Key Reference To"]:
                                            #If there is not an Interface slot for the
                                            # data value then create one (the interface value slot is created dynamically if there are other
                                            # interface bindings defined - but in case there are no others - e.g. a hidden field - then we may not
                                            # have the value slot)
                                            if "Interface Bindings" not in self.interfaceDict[clientelementid]["bindings"]:
                                                self.interfaceDict[clientelementid]["bindings"]["Interface Bindings"] = {"valuetext"  : ""}
                                                self.interfaceDict[clientelementid]["bindings"]["Interface Bindings"]["valuetext"] = objectInstanceDict[className].databaseFields[fieldName]
                                            elif "valuetext" in self.interfaceDict[clientelementid]["bindings"]["Interface Bindings"]:
                                                #dataformsmodulelogger.info("debug : %s"%str( self.interfaceDict[clientelementid]["bindings"]["Interface Bindings"]["valuetext"] ))
                                                if len(str(self.interfaceDict[clientelementid]["bindings"]["Interface Bindings"]["valuetext"])) == 0 or \
                                                      str(self.interfaceDict[clientelementid]["bindings"]["Interface Bindings"]["valuetext"]) == "valuetext" : 
                                                    self.interfaceDict[clientelementid]["bindings"]["Interface Bindings"]["valuetext"] = objectInstanceDict[className].databaseFields[fieldName]
                                                
                            else:
                                dataformsmodulelogger.info("warning : binding spec exists for %s.%s but the class does not contain this field !"%(className, fieldName))


        # process other foreign key references - for example there may be "hardcoded" references
        for elementid in self.interfaceDict:
            for clientelementid in self.interfaceDict:
                if "Foreign Key Reference To" in self.interfaceDict[clientelementid]["references"]:
                    if elementid in self.interfaceDict[clientelementid]["references"]["Foreign Key Reference To"]:

                        #If there is not an Interface slot for the
                        # data value then create one (the interface value slot is created dynamically if there are other
                        # interface bindings defined - but in case there are no others - e.g. a hidden field - then we may not
                        # have the value slot)
                        if "Interface Bindings" not in self.interfaceDict[clientelementid]["bindings"]:
                            self.interfaceDict[clientelementid]["bindings"]["Interface Bindings"] = {"valuetext"  : ""}

                        if "Interface Bindings" not in self.interfaceDict[elementid]["bindings"]:
                            self.interfaceDict[elementid]["bindings"]["Interface Bindings"] = {"valuetext"  : ""}
                        

                        dataformsmodulelogger.info("checking reference from %s to %s"%(clientelementid, elementid))
                        if len(str(self.interfaceDict[clientelementid]["bindings"]["Interface Bindings"]["valuetext"])) == 0 or \
                            str(self.interfaceDict[clientelementid]["bindings"]["Interface Bindings"]["valuetext"]) == "valuetext" : 
                                self.interfaceDict[clientelementid]["bindings"]["Interface Bindings"]["valuetext"] = self.interfaceDict[elementid]["bindings"]["Interface Bindings"]["valuetext"]


    def commitDataBundle(self, connection, dataBundle, bundleType="Form Submission", transactionDict = {}, objectDict={}):
        
        """

        This method commits records into the database, from a data bundle
        from this form.

        Example of a Form Submission data bundle :
        
        'REMOTE_USER': 'nobody',
        'element545': '2009-06-14',
        'element544': 'C/G',
        'element549': 'C/G',
        'formstate': 'submit_insert',
        'element545_displayed_': '6/14/2009',
        'formname': 'Form.GenotypeObservation.1'}

        The interfaceDict dictionary contains database bindings for each element, of the form
        table.column

        The transactions argument specifies , for each class, whether the transaction is an update or an insert.
        - e.g. {"genotypeObsevation" : "insert" , "genotypeStudy" : None}
        or, to manually specify the order of inserts :
        {"genotypeObsevation" : "insert" , "commentob" : "insert", "genotypeStudy" : None}

        The default is to insert.

        Enumerate the database bindings available : 
        """
        dataformsmodulelogger.info("Handling transactions : %s"%transactionDict)

        #dataformsmodulelogger.info("Using Data bundle : %s"%dataBundle) # memory error for large files


        dataformsmodulelogger.info("Using interface : %s"%self.interfaceDict)


        dataformsmodulelogger.info("Creating objects from data bundle")


        objectDataDict = {}
        # will contain
        # "className" : {"instance" : object, "databaseFields" : { "elementname" : value }}        
        for elementid in self.interfaceDict:
            #bundleid = "element%s"%elementid 
            bundleid = self.interfaceDict[elementid]["interfacelsid"] # static forms usually use lsid based bundle id's
            altbundleid = "element%s"%elementid  # dynamic forms usually use obid based bundle id's
            
            if "Class Bindings" in self.interfaceDict[elementid]["bindings"]:
                if "Data Element" in self.interfaceDict[elementid]["bindings"]["Class Bindings"]:
                    # try old style bundleid if bundleid not found 
                    if bundleid not in dataBundle:
                        (bundleid, altbundleid)  = ( altbundleid , bundleid)
                        
                    if bundleid in dataBundle: 
                        #dataformsmodulelogger.info("found data value %s in %s to bind to %s"%(dataBundle[bundleid],bundleid,self.interfaceDict[elementid]["bindings"]["Class Bindings"]["Data Element"])) # blows memory for large-file-upload bundle members
                        dataformsmodulelogger.info("found data value in %s to bind to %s"%(bundleid,self.interfaceDict[elementid]["bindings"]["Class Bindings"]["Data Element"]))
                        
                        tokens = re.split("\.",self.interfaceDict[elementid]["bindings"]["Class Bindings"]["Data Element"])
                        if len(tokens) != 2:
                            dataformsmodulelogger.info("bad data element specifier : %s"%self.interfaceDict[elementid]["bindings"]["Class Bindings"]["Data Element"])
                            raise brdfException("bad data element specifier : %s"%self.interfaceDict[elementid]["bindings"]["Class Bindings"]["Data Element"])
                        (className, fieldName) = tokens

                        databaseData = dataBundle[bundleid]
                        instanceData  = None 
                        if isinstance(dataBundle[bundleid],ListType):
                            databaseData = dataBundle[bundleid][0]
                            instanceData = dataBundle[bundleid]
                        if className not in objectDataDict:
                            objectDataDict[className] = {
                                "instance" : None,
                                "instanceData" : {fieldName : instanceData} ,
                                "databaseFields" : {fieldName : databaseData}
                            }
                        else:
                            objectDataDict[className]["databaseFields"][fieldName] = databaseData
                            objectDataDict[className]["instanceData"][fieldName] = instanceData                            
                    else:
                        # for example this would happen for a hidden field that is bound to an obid, and is metioned in the
                        # class bindings but not received in the data bundle
                        dataformsmodulelogger.info("no data value found for %s (expecting from %s or %s )"%\
                                                   (self.interfaceDict[elementid]["bindings"]["Class Bindings"]["Data Element"],bundleid,altbundleid ))
                else:
                    if bundleid in dataBundle or altbundleid in dataBundle:
                        dataformsmodulelogger.info("warning, data value found (%s) but no database bindings for %s"%(dataBundle[bundleid], bundleid))
            else:
                if bundleid in dataBundle or altbundleid in dataBundle:
                    dataformsmodulelogger.info("warning, data value found (%s) but no database bindings for %s"%(dataBundle[bundleid], bundleid))

        dataformsmodulelogger.info("processing transactions from factory objectDataDict : %s"%str(objectDataDict))



        # At this point we have form data that
        # * was bound when the form was constructed - this initialised some values such as existintg foreign keys
        # * has been organised into classes in the objectDataDict structure.
        #
        # There may still be unresolved bindings - for example references to obid's of classes not yet constructed ; internal
        # references within a class (to be avoided as un-normalised) These
        # can be patched up on the way through - however we will need to process things in the correct order. This order
        # can be worked out by looking at dependencies :
        dependencyOrderDict = {}
        dataformsmodulelogger.info("using reference dependencies to derive transaction order")
        for elementid in self.interfaceDict:
            for clientelementid in self.interfaceDict:
                if "Foreign Key Reference To" in self.interfaceDict[clientelementid]["references"]:
                    if elementid in self.interfaceDict[clientelementid]["references"]["Foreign Key Reference To"]:
                        if "Class Bindings" in self.interfaceDict[elementid]["bindings"] and "Class Bindings" in self.interfaceDict[clientelementid]["bindings"]:
                            if "Data Element" in self.interfaceDict[elementid]["bindings"]["Class Bindings"] and  "Data Element" in self.interfaceDict[clientelementid]["bindings"]["Class Bindings"]:
                                (eclassName, efieldName) = re.split("\.",self.interfaceDict[elementid]["bindings"]["Class Bindings"]["Data Element"])
                                if eclassName not in dependencyOrderDict:
                                    dependencyOrderDict[eclassName] = 0
                                (ceclassName, cefieldName) = re.split("\.",self.interfaceDict[clientelementid]["bindings"]["Class Bindings"]["Data Element"])
                                dataformsmodulelogger.info("using dependency of %s.%s on %s.%s"%(ceclassName, cefieldName, eclassName, efieldName))
                                if ceclassName not in dependencyOrderDict:
                                    dependencyOrderDict[ceclassName] = dependencyOrderDict[eclassName] + 1
                                else:
                                    dependencyOrderDict[ceclassName] = max( dependencyOrderDict[ceclassName], dependencyOrderDict[eclassName] + 1)

                                # resolve any dependencies that we can now
                                if ceclassName in objectDataDict and eclassName in objectDataDict:
                                    if 'databaseFields' in objectDataDict[ceclassName] and 'databaseFields' in objectDataDict[eclassName] :
                                        if cefieldName in objectDataDict[ceclassName]['databaseFields'] and efieldName in objectDataDict[eclassName]['databaseFields']:
                                            if objectDataDict[eclassName]['databaseFields'][efieldName] != None:
                                                if re.search("valuetext",str(objectDataDict[eclassName]['databaseFields'][efieldName])) == None:

                                                    dataformsmodulelogger.info("pre-insert processing field reference from %s.%s (=%s) to %s.%s (=%s)"%(ceclassName, cefieldName, objectDataDict[ceclassName]['databaseFields'][cefieldName], eclassName, efieldName, objectDataDict[eclassName]['databaseFields'][efieldName]))

                                                    if objectDataDict[ceclassName]['databaseFields'][cefieldName] == None:                                                
                                                        objectDataDict[ceclassName]['databaseFields'][cefieldName]=objectDataDict[eclassName]['databaseFields'][efieldName] 
                                                    elif re.search("valuetext",str(objectDataDict[ceclassName]['databaseFields'][cefieldName])) != None:
                                                        objectDataDict[ceclassName]['databaseFields'][cefieldName] = re.sub("valuetext",objectDataDict[eclassName]['databaseFields'][efieldName],objectDataDict[ceclassName]['databaseFields'][cefieldName])
                                                    elif len(str(objectDataDict[ceclassName]['databaseFields'][cefieldName])) == 0:
                                                        objectDataDict[ceclassName]['databaseFields'][cefieldName]=objectDataDict[eclassName]['databaseFields'][efieldName] 
                                    
                                                            
        dataformsmodulelogger.info("will apply dependency ordering using : %s"%str(dependencyOrderDict))

        def transSort(className1, className2):
            if className1 in dependencyOrderDict and className2 in dependencyOrderDict:
                return dependencyOrderDict[className1] - dependencyOrderDict[className2]
            elif className1 in dependencyOrderDict :
                return -1
            elif className2 in dependencyOrderDict :
                return 1
            else:
                return 0


        # there may be classes mentioned in the transaction specfication that are not yet
        # in the objectDataDict - e.g. "internal" classes such as for link tables, which
        # are referred to by references but which do not need to have user interface elements.
        #- therefore add any classes referred to in the transactions specification, to the
        # objectDataDict
        for className in transactionDict:
            if className not in objectDataDict:
                objectDataDict[className] = {
                    "instance" : None,
                    "instanceData" : {} ,
                    "databaseFields" : {}
                }


        objectDataDictKeys = objectDataDict.keys()
                    
        objectDataDictKeys.sort(transSort)

        dataformsmodulelogger.info("applying transactions for classes in order : %s"%str(objectDataDictKeys))
                        
        for className in objectDataDictKeys:
    
            transactions = None
            if className in transactionDict :
                transactions = transactionDict[className]

            if not isinstance(transactions,ListType):
                transactions = [transactions]
                

            for transaction in transactions:
                dataformsmodulelogger.info("processing transaction %s for class %s"%(transaction, className))
                if transaction == "insert":
                    dataformsmodulelogger.info("creating object with new %s()"%className)

                    # include any class imports we need here
                    from studyModule import genotypeObservation, genotypeStudy
                    from annotationModule import commentOb
                    from listModule import obList, geneExpressionExperimentSeriesFact, namedListMembershipLink
                    from dataImportModule import dataSourceOb
                    from analysisModule import analysisProcedureOb

                    # if we have multiple records for the same class, then the classname key has a modifier, as per
                    # classname:record - hence we parse the classname using a regexp
                    match = re.search("(\w+)[:]*",className)
                    RclassName = match.groups()[0]
                    objectDataDict[className]["instance"] = eval("%s()"%RclassName)
                    objectDataDict[className]["instance"].initNew(connection)

                    dataformsmodulelogger.info("updating database fields of new object from data bundle")
                    objectDataDict[className]["instance"].databaseFields.update(objectDataDict[className]["databaseFields"])

                    dataformsmodulelogger.info("committing the new object %s"%str(objectDataDict[className]["instance"].databaseFields))                
                    objectDataDict[className]["instance"].insertDatabase(connection)

                    dataformsmodulelogger.info("adding instance data ")
                    objectDataDict[className]["instance"].instanceData = objectDataDict[className]["instanceData"]

                    dataformsmodulelogger.info("adding form settings ")
                    objectDataDict[className]["instance"].formSettings = self.formDict

                    dataformsmodulelogger.info("passing on form callbacks ")
                    objectDataDict[className]["instance"].fetcher = self.fetcher
                    
                    
                    # check references to see if any clients of this new class need to be updated
                    dataformsmodulelogger.info("re-checking reference dependencies after insert")

                    # for every interface get the class
                    for elementid in self.interfaceDict:
                        if "Class Bindings" in self.interfaceDict[elementid]["bindings"]: 
                            if "Data Element" in self.interfaceDict[elementid]["bindings"]["Class Bindings"] :
                                (eclassName, efieldName) = re.split("\.",self.interfaceDict[elementid]["bindings"]["Class Bindings"]["Data Element"])

                                # if the class is the same as the class just commited then check all potential clients
                                if eclassName == className:
                                    dataformsmodulelogger.info("checking potential clients of %s.%s"%(eclassName, efieldName))

            
                                    for clientelementid in self.interfaceDict:
                                        if "Foreign Key Reference To" in self.interfaceDict[clientelementid]["references"]:
                                            if elementid in self.interfaceDict[clientelementid]["references"]["Foreign Key Reference To"]:
                                                dataformsmodulelogger.info("processing key reference from client %s to master %s"%(clientelementid, elementid))

                                                (ceclassName, cefieldName) = re.split("\.",self.interfaceDict[clientelementid]["bindings"]["Class Bindings"]["Data Element"])
                                                dataformsmodulelogger.info("propagating field reference %s from inserted class %s to class %s"%(cefieldName, className, ceclassName))

                                                if ceclassName not in objectDataDict:
                                                    dataformsmodulelogger.info("While checking references, client class %s (field %s) not found in objectDataDict - assuming this  is an internal interface-less field - adding to data bundle"%(ceclassName, cefieldName))
                                                    objectDataDict[ceclassName] = {
                                                        "instance" : None,
                                                        "instanceData" : {} ,
                                                        "databaseFields" : {cefieldName : ""}
                                                    }

                                                if cefieldName not in objectDataDict[ceclassName]['databaseFields']:
                                                    objectDataDict[ceclassName]['databaseFields'][cefieldName]=objectDataDict[className]['instance'].databaseFields[efieldName]
                                                elif objectDataDict[ceclassName]['databaseFields'][cefieldName] == None:
                                                    objectDataDict[ceclassName]['databaseFields'][cefieldName]=objectDataDict[className]['instance'].databaseFields[efieldName]                                                     
                                                elif re.search("valuetext",str(objectDataDict[ceclassName]['databaseFields'][cefieldName])) != None:
                                                    objectDataDict[ceclassName]['databaseFields'][cefieldName] = re.sub("valuetext",objectDataDict[className]['instance'].databaseFields[efieldName],objectDataDict[ceclassName]['databaseFields'][cefieldName])
                                                elif len(str(objectDataDict[ceclassName]['databaseFields'][cefieldName])) == 0:
                                                    objectDataDict[ceclassName]['databaseFields'][cefieldName]=objectDataDict[className]['instance'].databaseFields[efieldName] 

                    
                elif transaction == "update":
                    # try to get the user doing the update
                    objectDataDict[className]["databaseFields"]["lastupdatedby"] = ""
                    if "REMOTE_USER" in dataBundle:
                        objectDataDict[className]["databaseFields"]["lastupdatedby"] = dataBundle["REMOTE_USER"]
                        
                    # include any class imports we need here
                    from studyModule import genotypeObservation, genotypeStudy

                    if className not in objectDict:
                        raise brdfException("update transaction requested for class %s but no existing object of this class supplied"%className)
                    
                    objectDataDict[className]["instance"] = eval("%s()"%className)
                    objectDataDict[className]["instance"].initFromDatabase(objectDict[className], connection)

                    dataformsmodulelogger.info("update database field")
                    objectDataDict[className]["instance"].databaseFields.update(objectDataDict[className]["databaseFields"])
                    
                    dataformsmodulelogger.info("committing %s"%str(objectDataDict[className]["instance"].databaseFields))                
                    objectDataDict[className]["instance"].updateDatabase(connection)                
                elif transaction == None:
                    brdfException("skipping null transaction in commitDataBundle for %s"%className)
                else:
                    if objectDataDict[className]["instance"] != None:
                        dataformsmodulelogger.info("trying %s.%s() for instance"%(className,transaction))
                        eval('objectDataDict[className]["instance"].%s()'%(transaction))
                    else:
                        raise brdfException("transaction %s requested on %s but no instance available"%(transaction,className))


        return objectDataDict

        

def main():

    connection=databaseModule.getConnection()

    myform = basicForm()
    
    myform.initFromDatabase("Form.GenotypeObservation.1",connection)

    containerDict = {
        "flavour" : "DoJo",
        "contentDescriptor" : ["","data",""],
        "content" : [
            """<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>            
   <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
   <link id="themeStyles" rel="stylesheet" href="/agbrdf/html/js/dojo-release-1.2.3/dijit/themes/tundra/tundra.css"> 
  

   <script type="text/javascript" src="/agbrdf/html/js/dojo-release-1.2.3/dojo/dojo.js" 
		djConfig="parseOnLoad: true, isDebug: false, debugAtAllCosts: false" >
   </script>
   <script type="text/javascript"> 
		//dojo.require("dojo.parser");
		//dojo.require("dijit.form.parser");
                //dojo.require("dijit.form.TextBox");
                dojo.require("dijit.form.Form");                
                dojo.require("dijit.form.ValidationTextBox");
		dojo.require("dijit.form.DateTextBox");
                dojo.require("dijit.form.Button");
                dojo.require("dijit.form.Textarea");
                dojo.require("dijit.layout.ContentPane");
                dojo.require("dijit.layout.BorderContainer");

   </script>
   <style type="text/css">
		@import "/agbrdf/html/js/dojo-release-1.2.3/dojo/resources/dojo.css";
		@import "/agbrdf/html/js/dojo-release-1.2.3/dijit/themes/tundra/tundra.css";
		html, body { height: 90%; width: 90%; padding: 5px; margin: 5px; border: 0; }
		#main { height: 100%; width: 100%; border: 0; }
		#header { margin: 0px; }
		#leftAccordion { width: 25%; }
		#bottomTabs { height: 40%; }

   </style>
   </head>
<body class="tundra">
<div id="myform" class="formContainer" dojoType="dijit.layout.BorderContainer" style="border: 1px solid black; padding: 5px">
<form action="/cgi-bin/agbrdf/dojoform.py" method="post" id="formidtext" name="brdfForm"  dojoType="dijit.form.Form">


<div dojoType="dijit.layout.ContentPane" splitter=true style="width: 100%; height: 350px; padding: 5px;" >
""",

            None,
            """
</div>
</form>
</div>

</body>
</html>
"""
            ]}
        
    print myform.getInterface(connection, container=containerDict )
    
        
if __name__ == "__main__":
   main()
        

    
        
        

        

        

