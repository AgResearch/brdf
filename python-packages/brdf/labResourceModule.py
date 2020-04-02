#
# This class corresponds to the labResourceOb database  table
# which is used to represent lab resources such as microarrays,
# primers etc.
#

from types import *
from obmodule import getNewObid,getObjectRecord
from brdfExceptionModule import brdfException
from obmodule import ob
from opmodule import op
from htmlModule import tidyout
from imageModule import makeBarGraph 
from displayProcedures import getExpressionMapDisplay,getGenepixThumbnailDisplayTable,getSequenceAnnotationBundle,getAffyProbeGraphs
import os
import globalConf
import databaseModule
import re
import logging


""" logging - comment out when not required """
# set up logger if we want logging
labresourcemodulelogger = logging.getLogger('labresource')
labresourcehdlr = logging.FileHandler(os.path.join(globalConf.LOGPATH,'brdf_labresource.log'))
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
labresourcehdlr.setFormatter(formatter)
labresourcemodulelogger.addHandler(labresourcehdlr) 
labresourcemodulelogger.setLevel(logging.INFO)        



class labResourceOb ( ob ) :
    """ lab rsource object - arrays, primers etc """
    def __init__(self):
        ob.__init__(self)

        self.AboutMe['default'][0]['heading'] = 'BRDF Lab Resource Object'
        self.AboutMe['default'][0]['text'] = """
        This page displays a lab resource object from the BRDF database.
        <p/>
        In the BRDF database schema, the term lab resources refers to standard
        molecular biology reagents such as primers and vectors, but is also used to
        refer to quite different resources - such as entire microarray chips, and
        genetic tests.
        <p/>
        The master record for a lab resource is stored in the labresourceob table.
        <p/>
        Which type of lab resource the master record relates to , is recorded in the
        resourcetype field of this table. The current set of types that are supported in this
        database are recorded in an ontology called LABRESOURCE_TYPES. (You can browse this ontology
        by selecting ONTOLOGIES from the drop down list of search types on the main page, and entering
        LABRESOURCE_TYPES as the search phrase)
        <p/>
        The master table labresourceob thus provides a simple unified searchable manifest of lab resources that
        have been recorded as part of submitting various experiments (including sequencing) to the database -
        whether vectors, primers, microarrays, genetic tests or other reagents.
        <p/>
        The details needing to be stored for each type of resource depend entirely on the
        type of resource - for example a primer requires at least the sequence of the primer ;
        for a microarray, details include the location and contents of each spot on the
        microarray. The details of each resource are stored in a details (or fact) table, linked
        to the master table. Thus details of what spots are on a microarray , are stored in a
        table called microarrayspotfact linked to the labresourceob master record ; details of
        a genetic test - such as the dbSNP accession number , alleles etc, are stored in a table
        called genetictestfact linked to the labresourceob master record. In addition, there is a table
        called labresourcefact that is linked to the labresourceob master , that can be used to store
        arbitrary key-value pairs, to record custom details of a labresource.
        <p/>
        Since it is reasonably common to need to record multiple lab resources as part of
        submitting an experiment (for example, both forward and reverse primers), the tables
        labresourcelist and labresourcelistmembershiplink exist to support a many to many
        relationship between experiments and lab resources (a given lab resource may be related to
        many experiments, and a given experiment may involve many lab resources).
        <p/>
        A Lab Resource Object (and a Lab Resource List) in the BRDF database may have relationships with
        other types of object in the database. For example, a microarray , together with a sample
        and a protocol together define a microarray hybridisation ; a vector together with a sample and a
        biosequence define a sequencing experiment. All of the possible relationships that a
        labresource object may have with other objects in the database are depicted by icons in the information
        map section of the page.
        <p/>
        The icon is composed of the labresourceob symbol connected to the symbols for the related objects
        by horizontal lines. Where the database does not yet contain any related objects for a labresource,
        the icon for that relationship is greyed out.
        <p/>
        Thus for example to report all microarray hybridisations that have used a given
        microarray , simply click on the BioSampleList symbol that appears in the
        icon labelled Gene Expression Study. This will report all the biosamples that are
        related to the given microarray, by virtue of being part of a microarray experiment. The
        report will include hyperlinks both to the biosamples themselves , and the records corresponding
        to the hybridisationm experiments.
        <p/>
        Below is a brief description of each item appearing in the current information map :
        <ul>
           <li> Lab Resource List : The icon is made of a line connecting the Lab Resource symbol to the
           Lab Resource List symbol. This icon depicts membership of the lab resource you are looking at ,
           in various lists. Clicking on the Lab Resource List symbol will report all lists that
           the lab resource is a member of.
           <li> Gene Expression Study : The icon is made of a line connecting the Lab Resource symbol, to
           symbols for a Lab Resource List, a Bio Protocol and a Bio Sample List. The icon depicts the
           BRDF model of a gene expression study, which is that it is a relation between one or more
           bio samples, one or more lab resources and a protocol. (The reason that both a lab resource
           and a lab resource list appear in the icon is that for convenience we sometimes do not bother
           creating a list , where an experiment only involves a single lab resource)
           <p>
           Clicking on the BioSampleList symbol that appears in this icon will report all the BioSampleLists
           that are related to the given microarray, by virtue of being part of a microarray experiment. The
           report will include hyperlinks both to the biosample lists themselves , and the records corresponding
           to the hybridisationm experiments. (Biosample lists appear in this relation rather than biosamples,
           because for many microarray experiments, more than one sample is used in the experiment)
           <li> Sequencing Details : The icon is made of a line connecting the Lab Resource symbol, to
           symbols for a Lab Resource List, a Bio Sample and a Sequence. The icon depicts the
           BRDF model of a sequencing experiment, which is that it is a relation between one 
           bio sample, one or more lab resources and a sequence. (The reason that both a lab resource
           and a lab resource list appear in the icon is that for convenience we sometimes do not bother
           creating a list , where the sequencing only involves a single lab resource)
           <li> Genotype Study : The icon is made of a line connecting the Lab Resource symbol, to
           symbols for a Lab Resource List, a Bio Sample and a Sequence. The icon depicts the
           BRDF model of a genotype experiment, which is that it is a relation between one or more 
           biosamples, one or more lab resources and a protocol. (The reason that both a lab resource
           and a lab resource list appear in the icon is that for convenience we sometimes do not bother
           creating a list , where the sequencing only involves a single lab resource)
           <li> Biological Sample : The icon is made of a line connecting the Lab Resource symbol, to
           symbols for a Biosample, a Bio Subject and a Protocol. The icon depicts the
           BRDF model of a sampling activity, which is that it is a relation between one biosubject
           (e.g. a plant, cow, sheep, human etc) , one or more lab resources , one bio sample record and
           a protocol. (The reason that both a lab resource and a lab resource list appear in the icon
           is that for convenience we sometimes do not bother
           creating a list , where the sequencing only involves a single lab resource)
        </ul>
        <p/>
        As discussed above we may store various types of facts about a given lab resource - for example, spots
        of a microarray , or details about a SNP or SSR for a genetic test. Each type of fact supported by the
        BRDF is depicted by a line connecting the sequence symbol , to a square box labelled info, with the type of
        fact appearing to the right of the icon. Where the database does not yet contain any facts
        of a given type for a lab resource object, the info icon is greyed out. Thus for example the
        Microarray Spot icon is greyed out if you are looking at the lab resource record for a primer.
        </p>
        Thus for example , to report all the spots on a microarray, you simply click the square info
        box labelled microarray spot.
        """                        
        


    def initFromDatabase(self, identifier, connection):
        """ method for initialising labResourceOb from database"""

        # first init base class - this will get obid
        ob.initFromDatabase(self, identifier, "labResourceOb", connection)


        # now get the complete object
        self.databaseFields = getObjectRecord(connection, "labResourceOb", self.databaseFields['obid'])
        self.obState.update({'ERROR' : 0 , 'NEW' : 0, 'MESSAGE' : "initialised from database OK"})
        
    def initNew(self,connection,resourcetype,xreflsid='',obkeywords='',resourcedescription=''):
        """ method to initialise a new labResourceModule object """
        self.databaseFields = \
            {
                'obid' : getNewObid(connection) ,
                'xreflsid' : xreflsid , 
                'obkeywords' : obkeywords ,
                'resourcetype' : resourcetype , 
                'resourcename' : xreflsid ,
                'resourcedescription' : resourcedescription ,
                'resourcesequence' : None
              }
        self.obState.update({'DB_PENDING' : 1})

    def initFromExternalData(self,dataSource):
        """ method for initialising a dataSource object from external data - a dataSourceOb """        
        if dataSource.__class__.__name__ != "dataSourceOb":
            self.obState.update({'ERROR' : 1 , 'MESSAGE' : "initFromExternalData called with arg type" + dataSource.__class__.__name__ + " - should be dataSourceOb"})
            raise brdfException, self.ObState['MESSAGE']    

    def insertDatabase(self,connection):
        """ method used by labResource object to save itself to database  """
        sql = """
        insert into labResourceOb(obid,xreflsid,obkeywords,resourcetype,
            resourcename,resourcedescription,resourcesequence) 
           values (%(obid)s,%(xreflsid)s,%(obkeywords)s,%(resourcetype)s,
           %(resourcename)s,%(resourcedescription)s,%(resourcesequence)s)"""
        insertCursor = connection.cursor()
        insertCursor.execute(sql,self.databaseFields)
        connection.commit()
        insertCursor.close()
        self.obState.update({'NEW' : 0 , 'DB_PENDING' : 0, 'ERROR' : 0, 'MESSAGE' : "database insert OK"})

    def addFact(self,connection,argfactNameSpace, argattributeName, argattributeValue):
        factFields = {
            'labResourceOb' : self.databaseFields['obid'],
            'factNameSpace' : argfactNameSpace,
            'attributeName' : argattributeName,
            'attributeValue' : argattributeValue }

        # first check if this fact is already in the db - if it is do not duplicate
        sql = """
        select labresourceob from labResourceFact where
        labresourceob = %(labResourceOb)s and
        factNameSpace = '%(factNameSpace)s' and
        attributeName = '%(attributeName)s' and
        attributeValue = '%(attributeValue)s'
        """
        insertCursor = connection.cursor()
        labresourcemodulelogger.info("checking for fact using %s"%(sql%factFields))
        insertCursor.execute(sql%factFields)
        insertCursor.fetchone()
        labresourcemodulelogger.info("rowcount = %s"%insertCursor.rowcount)
        if insertCursor.rowcount == 0:        
            sql = """
            insert into labResourceFact(labresourceob,factNameSpace, attributeName, attributeValue)
            values(%(labResourceOb)s,%(factNameSpace)s,%(attributeName)s,%(attributeValue)s)
            """
            labresourcemodulelogger.info("executing %s"%(sql%factFields))
            insertCursor.execute(sql,factFields)
            connection.commit()
            insertCursor.close()
            self.obState.update({'NEW' : 0 , 'DB_PENDING' : 0, 'ERROR' : 0, 'MESSAGE' : "database insert OK"})
        else:
            insertCursor.close()
        
        
        


    
class labResourceFact (op) :
    def __init__(self, obtuple=None):
        op.__init__(self,obtuple)

    def initFromExternalData(self,dataSource):
        """ method for initialising a dataSource object from external data - a dataSourceOb """        
        if dataSource.__class__.__name__ != "dataSourceOb":
            self.obState.update({'ERROR' : 1 , 'MESSAGE' : "initFromExternalData called with arg type" + dataSource.__class__.__name__ + " - should be dataSourceOb"})
            raise brdfException, self.ObState['MESSAGE']    
        
        #print "labResourceOb is initialising from externaldata"

class microarraySpotFact (op) :
    def __init__(self, obid=None):
        op.__init__(self)

        if obid != None:
            con = databaseModule.getConnection()
            self.initFromDatabase(obid, con)
            con.close()        

    def initFromDatabase(self, identifier, connection):
        """ method for initialising microarraySpotFact from database"""

        # first init base class - this will get obid
        ob.initFromDatabase(self, identifier, "microarraySpotFact", connection)

        # now get the complete object
        self.databaseFields = getObjectRecord(connection, "microarraySpotFact", self.databaseFields['obid'])
        self.obState.update({'ERROR' : 0 , 'NEW' : 0, 'MESSAGE' : "initialised from database OK"})


        # obtain display procedures that are linked to the parent study object , and have the virtual flag set
        sql = """
        select
            df.invocation,
            df.functioncomment,
            dp.xreflsid,
            dp.procedurename,
            ds.datasourcename,
            ds.physicalsourceuri,
            ds.datasourcetype,
            df.voptypeid
        from
            (displayfunction df join displayprocedureob dp on
            df.displayprocedureob = dp.obid) left outer join
            datasourceob ds on ds.obid = df.datasourceob
        where
            df.ob = %(labresourceob)s and
            df.voptypeid is not null
        """
        labresourcemodulelogger.info('executing SQL to retrieve virtual dynamic display functions : %s'%str(sql%self.databaseFields))
        displayCursor = connection.cursor()
        displayCursor.execute(sql,self.databaseFields)
        self.virtualDisplayFunctions = displayCursor.fetchall()
        labresourcemodulelogger.info(str(self.virtualDisplayFunctions))
        if displayCursor.rowcount > 0:
            self.obState.update({'VIRTUAL_DYNAMIC_DISPLAYS' : displayCursor.rowcount , 'MESSAGE' : "virtual dynamic displays initialised from database OK"})        
        


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


        # un  virtual display functions - these are now obtained as part of object initialisation
        #sql = """
        #select
        #    df.invocation,
        #    df.functioncomment,
        #    dp.xreflsid,
        #    dp.procedurename,
        #    ds.datasourcename,
        #    ds.physicalsourceuri,
        #    ds.datasourcetype,
        #    df.voptypeid
        #from
        #    (displayfunction df join displayprocedureob dp on
        #    df.displayprocedureob = dp.obid) left outer join
        #    datasourceob ds on ds.obid = df.datasourceob
        #where
        #    df.ob = %(labresourceob)s and
        #    df.voptypeid is not null
        #"""
        #labresourcemodulelogger.info('executing SQL to retrieve dynamic display functions : %s'%str(sql%self.databaseFields))
        connection = databaseModule.getConnection()
        #displayCursor = connection.cursor()
        #displayCursor.execute(sql,self.databaseFields)
        #displayFunctions = displayCursor.fetchall()
        #labresourcemodulelogger.info(str(displayFunctions))
        # test code :
        #myGraphHTML = eval('getGenepixThumbnailDisplay(jpegfilename="C:/working/zaneta/9072 ratio 1 mid scan .jpg",xy=re.split("\t",self.databaseFields["rawdatarecord"])[5:7],usercontext=context,fetcher=self.fetcher, imagepath=self.imagepath, tempimageurl=self.tempimageurl, sectionheading="Spot Images" ,pixelsize=10,xyoffset=(780, 12780),thumbcount=3,thumbdimensions=(20,20),zoomincrement=50)')
        #table += myGraphHTML
        for displayFunction in self.virtualDisplayFunctions:
            labresourcemodulelogger.info("executing following display code : %s"%displayFunction[0])
            myGraphHTML = eval(displayFunction[0])
            table += myGraphHTML

            
                                  

        labresourcemodulelogger.info('checking whether graphic can be made of expression values')

        # if the data source type for this microarray experiment is GALFile then we try
        # to graph the logratios and intensities from all observations of this spot. If it is
        # CSV from Affy CEL File the we try to graph Affy stats
        connection = databaseModule.getConnection()
        graphCursor = connection.cursor()
        sql= """
        select
           d.datasourcetype
        from
           ((microarrayspotfact msf join labresourceob lr
           on lr.obid = msf.labresourceob ) join
           importfunction if on if.ob = lr.obid ) join
           datasourceob d on d.obid = if.datasourceob
        where
           msf.obid = %s
           """%self.databaseFields['obid']
        labresourcemodulelogger.info("executing %s"%str(sql))
        graphCursor.execute(sql)
        record=graphCursor.fetchone()
        if graphCursor.rowcount == 1:
            if record[0] in ['GALFile','AgResearchArrayExtract1','GALFile_noheader']:

                # get and graph the log ratios from all observations related to this spot.
                sql = """
                select
                mo.gpr_logratio,
                mo.xreflsid,
                mo.obid,
                (mo.gpr_dye1foregroundmean + mo.gpr_dye2foregroundmean)/2.0 as averagefg,
                ges.xreflsid as studylsid,
                substr(ges.studydescription,1,30) as studydescription
                from
                geneexpressionstudy ges join microarrayobservation mo
                on
                ges.obid = mo.microarraystudy
                where
                microarrayspotfact = %s order by
                mo.xreflsid"""%self.databaseFields['obid']
                labresourcemodulelogger.info("executing %s"%str(sql))
                graphCursor.execute(sql)
                datatuples = graphCursor.fetchall()
                labresourcemodulelogger.info("..done executing have data")


                observationids = [ item[2] for item in datatuples ]
                # each tuple contain a fetch URL - initialise this
                logratiodatatuples = [ (item[0],item[1], self.fetcher + "?context=%s&obid=%s&target=ob"%(context,item[2])) \
                                for item in datatuples ]

                #datatuples = [(item[0],item[1]) for item in datatuples]
                    
                if graphCursor.rowcount > 0:

                    # construct a multi-select list that can be used to select thumbnails to display
                    # (if they are available)
                    selectlisttuples = ["<option value=%s> %s %s (%s)</option>"%(item[2], item[4], item[5],item[2]) for item in datatuples]
                    selectlisthtml = """
                    <tr>
                    <td colspan=2 align=center>
                    <!-- <input value="Go" type="button" onclick='multipost("/cgi-bin/sheepgenomics/simple-ajax-example.py","experiments","fetcheddisplays","displayprocedure=34&amp;option=")'></p> -->
                    <font size="-1"> (to select multiple experiments press the control key and click. To select a block use the shift key and click) </font> <p/>
                    <select name="experiments" id="experiments" multiple size=4>
                    """\
                    +reduce(lambda x,y:x+y+'\n',selectlisttuples,'')\
                    + """
                    </select>
                    <p/>
                    <input value="Retrieve spot thumbnails for selected experiments" type="button" id="getspots" onclick='multipost("%s","experiments","fetcheddisplays","context=%s&amp;displayprocedure=displayProcedures.getGenepixThumbnailDisplay&amp;obid=","%s","%s",this)'></p>         
                    <p/>
                    </td>
                    </tr>
                    """%(self.displayfetcher,context,self.waitURL,self.waiter)
                    #<input value="Retrieve spot thumbnails for selected experiments" type="button" onclick='multipost("/cgi-bin/sheepgenomics/fetchDisplay.py","experiments","fetcheddisplays","context=%s&amp;displayprocedure=displayProcedures.getGenepixThumbnailDisplay&amp;obid=")'></p>                                        

                    
                    (myGraphName,myGraphMap) = makeBarGraph(imageDirectory=self.imagepath,datatuples=logratiodatatuples,currenttuple=None,label1="All raw LogRatios",label2="for this spot",barwidth=5)
                    myGraphHTML= """
                        <tr>
                        <td colspan=2 align=center>
                        <p/>
                        <img src="%s%s" halign="center" usemap="#%s" border="0"/>
                        <p/>
                        %s
                        </td>
                        </tr>
                        """
                    myGraphHTML = myGraphHTML%(self.tempimageurl,myGraphName,myGraphName.split('.')[0],myGraphMap)
                    table += """
                <tr> <td colspan="2" class=tableheading> 
                %s
                </td>
                </tr>
                """%"All observed raw logratios and intensities for this gene, in experiments using this chip"                    
                    table +=  myGraphHTML



                # graph the intensities
                intensitydatatuples = [ (int(item[3]),item[1], self.fetcher + "?context=%s&obid=%s&target=ob"%(context,item[2])) \
                                for item in datatuples ]
                #datatuples = [(item[0],item[1]) for item in datatuples]
                    
                if graphCursor.rowcount > 0:
                    (myGraphName,myGraphMap) = makeBarGraph(imageDirectory=self.imagepath,datatuples=intensitydatatuples,currenttuple=None,label1="All average foreground",label2="intensities for this spot",barwidth=5)
                    myGraphHTML= """
                        <tr>
                        <td colspan=2 align=center>
                        <p/>
                        <img src="%s%s" halign="center" usemap="#%s" border="0"/>
                        <p/>
                        %s
                        </td>
                        </tr>
                        """
                    myGraphHTML = myGraphHTML%(self.tempimageurl,myGraphName,myGraphName.split('.')[0],myGraphMap)
                    table +=  myGraphHTML


                    table += """
                <tr> <td colspan="2" class=tableheading> 
                %s
                </td>
                </tr>
                """%"Review selected experiments"                    
                    table +=   selectlisthtml
                    table += """
                    <tr>
                    <td>
                    <div id="fetcheddisplays">
                    </div>
                    </td>
                    </tr>
                    """




                # we now see whether there are any normalised values that we should graph.
                # the available normalised values are stored in an ontology called
                # MICROARRAY_NORMALISED_VALUES.
                sql = """
                select otf.termName , otf.unitname from
                ontologyob ot join ontologytermfact otf
                on otf.ontologyob = ot.obid
                where
                ot.ontologyname = 'MICROARRAY_NORMALISED_VALUES'
                order by otf.termName
                """
                labresourcemodulelogger.info("getting normalised data point names using %s"%sql)
                graphCursor.execute(sql)
                datapoints = graphCursor.fetchall()
                graphHTML=""
                for (datapoint, datatype) in datapoints:
                    # obtain the data points - we re-use the above array of data tuples, since they
                    # contain the correct tooltips and urls - just change the data point value
                    skipdatapoint = False
                    for iobservation in range(0, len(observationids)):
                        sql = """
                        select case when attributeValue is null then '' else attributeValue end
                        from microarrayobservationfact
                        where
                        microarrayobservation = %s and
                        factNameSpace = 'NORMALISED VALUE' and
                        attributeName = '%s'
                        """%(observationids[iobservation],datapoint)
                        labresourcemodulelogger.info("getting normalised data points using %s"%sql)
                        graphCursor.execute(sql)
                        datapointvalue=graphCursor.fetchone()

                        
                        if graphCursor.rowcount == 1:
                            if datapointvalue[0] == None:
                                datatuples[iobservation] = \
                                    (None, datatuples[iobservation][1], logratiodatatuples[iobservation][2])
                            elif len(datapointvalue[0]) == 0:
                                datatuples[iobservation] = \
                                    (None, datatuples[iobservation][1], logratiodatatuples[iobservation][2])   
                            else:
                                datatuples[iobservation] = \
                                    (float(datapointvalue[0]), datatuples[iobservation][1], logratiodatatuples[iobservation][2])   
                        else:
                            skipdatapoint = True
                            labresourcemodulelogger.info("skipping data point - query returned no rows")
                            break # we got nothing for this observation - incomplete dataset, give up
                            

                    # if all values missing, skip the whole data point
                    notMissing = [ datatuple[0] for datatuple in datatuples if datatuple[0] != None]
                    if len(notMissing) ==0:
                        skipdatapoint = True


                    if not skipdatapoint:
                        (myGraphName,myGraphMap) = makeBarGraph(imageDirectory=self.imagepath,datatuples=datatuples,currenttuple=None,label1="Normalisation:",label2=datapoint,barwidth=5)
                        myGraphHTML= """
                                <tr>
                                <td colspan=2 align=center>
                                <p/>
                                <img src="%s%s" halign="center" usemap="#%s" border="0"/>
                                <p/>
                                %s
                                </td>
                                </tr>
                                """
                        myGraphHTML = myGraphHTML%(self.tempimageurl,myGraphName,myGraphName.split('.')[0],myGraphMap)
                        graphHTML+=myGraphHTML

                table += """
                <tr> <td colspan="2" class=tableheading> 
                %s
                </td>
                </tr>
                    """%"All normalised values available for this gene, in experiments using this chip"                    
                table +=  graphHTML

                        

        # Affy arrays are imported in several steps, and the array itself is not linked to
        # a source file. We can distinguish Affy arrays because the lsid of this spot will begin with
        # affymetrix
        elif re.search('(\.)*Affymetrix\.',self.databaseFields['xreflsid'],re.IGNORECASE) != None:
            labresourcemodulelogger.info("attempting to display Affy experiment results")

            sql = """
            select
             mo.affy_meanpm,
             mo.affy_meanmm,
             mo.affy_stddevpm,
             mo.affy_stddevmm,
             mo.affy_count,
             mo.xreflsid,
             mo.obid
            from
            microarrayobservation mo 
            where
            microarrayspotfact = %s order by
            mo.xreflsid"""%self.databaseFields['obid']
            labresourcemodulelogger.info("executing %s"%str(sql))
            graphCursor.execute(sql)
            datatuples = graphCursor.fetchall()
            labresourcemodulelogger.info("..done executing have data")


            observationids = [ item[6] for item in datatuples ]
            # each tuple contain a fetch URL - initialise this
            pmdatatuples = [ (item[0],item[5], self.fetcher + "?context=%s&obid=%s&target=ob"%(context,item[6])) \
                                for item in datatuples ]
            #datatuples = [(item[0],item[1]) for item in datatuples]
                    
            if graphCursor.rowcount > 0:
                # PM means
                (myGraphName,myGraphMap) = makeBarGraph(imageDirectory=self.imagepath,datatuples=pmdatatuples,currenttuple=None,label1="All Probeset mean PM",label2="for this probeset",barwidth=5)
                myGraphHTML= """
                    <tr>
                    <td colspan=2 align=center>
                    <p/>
                    <img src="%s%s" halign="center" usemap="#%s" border="0"/>
                    <p/>
                    %s
                    </td>
                    </tr>
                    """
                myGraphHTML = myGraphHTML%(self.tempimageurl,myGraphName,myGraphName.split('.')[0],myGraphMap)
                table += """
                <tr> <td colspan="2" class=tableheading> 
                %s
                </td>
                </tr>
                """%"All observed probeset means and standard deviations for this probeset, across experiments using this chip"                    
                table +=  myGraphHTML


                #PM standard deviations
                pmdatatuples = [ (item[2],item[5], self.fetcher + "?context=%s&obid=%s&target=ob"%(context,item[6])) \
                                for item in datatuples ]                
                (myGraphName,myGraphMap) = makeBarGraph(imageDirectory=self.imagepath,datatuples=pmdatatuples,currenttuple=None,label1="All Probeset stddev PM",label2="for this probeset",barwidth=5)
                myGraphHTML= """
                    <tr>
                    <td colspan=2 align=center>
                    <p/>
                    <img src="%s%s" halign="center" usemap="#%s" border="0"/>
                    <p/>
                    %s
                    </td>
                    </tr>
                    """
                myGraphHTML = myGraphHTML%(self.tempimageurl,myGraphName,myGraphName.split('.')[0],myGraphMap)               
                table +=  myGraphHTML                

                
        graphCursor.close()
        if self.obState['DYNAMIC_DISPLAYS'] > 0:
            labresourcemodulelogger.info('running non-virtual display functions')
            for displayFunction in self.displayFunctions:
                # exclude virtual functions - these will be instantiated in specific contexts or subclasses
                if displayFunction[7] == None:
                    labresourcemodulelogger.info('running %s'%displayFunction[0])
                    myGraphHTML = eval(displayFunction[0])
                    table += myGraphHTML        

        
        labresourcemodulelogger.info('listing dictionaries')
        # if we have formatted dictionaries , output these first , they are usually the most interesting
        # content of the object
        if len(ListDictionaryRows) >  0:
            table += ListDictionaryRows

        labresourcemodulelogger.info('listing fields')
        # next the field rows
        table += nonSystemFieldRows

        labresourcemodulelogger.info('listing lists')
        # next the other lists
        if len(ListOtherRows) > 0:
            table += ListOtherRows

        return table



        

class geneticTestFact (op) :
    def __init__(self):
        op.__init__(self)

    def initNew(self,connection):
        """ method to initialise a new geneticTestFact object """
        self.databaseFields = \
            {
                'obid' : getNewObid(connection) ,
                'accession' : None,
                'xreflsid' : None , 
                'labresourceob' : None,
                'testtype'  : None,
                'locusname' : None,
                'testdescription' : None,
                'variation' : None
            }
        self.obState.update({'DB_PENDING' : 1})
        

    def initFromDatabase(self, identifier, connection):
        """ method for initialising geneticTestFact from database"""

        # first init base class - this will get obid
        ob.initFromDatabase(self, identifier, "geneticTestFact", connection)

        # now get the complete object
        self.databaseFields = getObjectRecord(connection, "geneticTestFact", self.databaseFields['obid'])
        self.obState.update({'ERROR' : 0 , 'NEW' : 0, 'MESSAGE' : "initialised from database OK"})

    def insertDatabase(self,connection):
        insertCursor = connection.cursor()
        """ method used by geneticTestFact object to save itself to database  """
        sql = """
            insert into genetictestfact(
            obid,
            xreflsid,
            labresourceob ,
            testtype  ,
            locusname ,
            accession    ,
            testdescription ,
            variation)
            values(
            %(obid)s,%(xreflsid)s,%(labresourceob)s,%(testtype)s,%(locusname)s,
            %(accession)s,%(testdescription)s,%(variation)s)
        """
        #print "executing %s"%(sql%self.databaseFields)
        insertCursor.execute(sql,self.databaseFields)
        connection.commit()     
        insertCursor.close()
        self.obState.update({'NEW' : 0 , 'DB_PENDING' : 0, 'ERROR' : 0, 'MESSAGE' : "database insert OK"})
        

        

class microarrayFact (op) :
    def __init__(self):
        op.__init__(self)

    def initFromDatabase(self, identifier, connection):
        """ method for initialising microarrayFact from database"""

        # first init base class - this will get obid
        ob.initFromDatabase(self, identifier, "microarrayFact", connection)

        # now get the complete object
        self.databaseFields = getObjectRecord(connection, "microarrayFact", self.databaseFields['obid'])
        self.obState.update({'ERROR' : 0 , 'NEW' : 0, 'MESSAGE' : "initialised from database OK"})                



class labResourceList (op) :
    def __init__(self):
        op.__init__(self)

    def initNew(self,connection,listname='',xreflsid='',obkeywords=''):
        """ method to initialise a new labResourceList Module object """
        self.databaseFields = \
            { 'listname' : listname, 'obid' : getNewObid(connection) , 'xreflsid' : xreflsid , \
            'obkeywords' : obkeywords 
              }
        self.obState.update({'DB_PENDING' : 1, 'ERROR' : 0})

    def initFromDatabase(self, identifier, connection):
        """ method for initialising labResourceList from database"""

        # first init base class - this will get obid
        ob.initFromDatabase(self, identifier, "labResourceList", connection)

        # now get the complete object
        self.databaseFields = getObjectRecord(connection, "labResourceList", self.databaseFields['obid'])

        # for this object type we need to get the members of the list
        sql = "select labresourceob from labresourcelistmembershiplink where labresourcelist = %s " % self.databaseFields['obid']
        #print "executing " + sql        
        obCursor = connection.cursor()
        obCursor.execute(sql)
        obFieldValues = obCursor.fetchall()
        self.databaseFields.update({'labresources' : [item[0] for item in obFieldValues]})
        obCursor.close()

        self.obState.update({'ERROR' : 0 , 'NEW' : 0, 'DB_PENDING' : 0, 'MESSAGE' : "initialised from database OK"})              

        

    def insertDatabase(self,connection):
        """ method used by labResourceList object to save itself to database  """
        sql = "insert into labResourceList(obid,xreflsid,obkeywords,listname) \
                      values (%(obid)s,%(xreflsid)s,%(obkeywords)s,%(listname)s)"
        insertCursor = connection.cursor()
        insertCursor.execute(sql,self.databaseFields)
        connection.commit()
        insertCursor.close()
        self.obState.update({'NEW' : 0 , 'DB_PENDING' : 0, 'MESSAGE' : "database insert OK"})        

    def addLabResource(self,connection,labResource,inclusionComment=''):
        """ method for adding a labResource to an existing labResourceList """

        #check type
        if labResource.__class__.__name__ != "labResourceOb":
            self.obState.update({'ERROR' : 1 , 'MESSAGE' : "addLabResource called with arg type" + labResource.__class__.__name__ + " - should be labResourceOb"})
            raise brdfException, self.ObState['MESSAGE']

        # check list is in appropriate state
        if [self.obState[state] for state in ("NEW" , "DB_PENDING", "ERROR")] != [0,0,0]:
            self.obState.update({'MESSAGE' : "labResourceList state does not permit adding a labResource"})
            raise brdfException, self.obState['MESSAGE']

        self.obState.update({'DB_PENDING' : 1 , 'MESSAGE' : "adding lab resource"})

        sql = "insert into labResourceListMembershipLink(labresourcelist,labresourceob,inclusionComment) \
                      values (%(labresourcelist)s,%(labresourceob)s,%(inclusionComment)s)"

        membershipFields= {\
            'labresourcelist' : self.databaseFields['obid'] ,
            'labresourceob' : labResource.databaseFields['obid'],
            'inclusionComment' : inclusionComment
            }

        #print "executing " + sql%membershipFields
        
        insertCursor = connection.cursor()
        insertCursor.execute(sql,membershipFields)
        connection.commit()
        insertCursor.close()
        self.obState.update({'NEW' : 0 , 'DB_PENDING' : 0, 'MESSAGE' : "lab resource added OK"})



class functionalAssayFact (op) :
    def __init__(self):
        op.__init__(self)

    def initNew(self,connection):
        """ method to initialise a new functional assay fact object """
        self.databaseFields = \
            {
                'obid' : getNewObid(connection) ,
                'assayName' : None,
                'xreflsid' : None , 
                'labresourceob' : None,
                'assaytype'  : None,
                'assaydescription' : None      
            }
        self.obState.update({'DB_PENDING' : 1})
        

    def initFromDatabase(self, identifier, connection):
        """ method for initialising functionalAssayFact from database"""

        # first init base class - this will get obid
        ob.initFromDatabase(self, identifier, "functionalAssayFact", connection)

        # now get the complete object
        self.databaseFields = getObjectRecord(connection, "functionalAssayFact", self.databaseFields['obid'])
        self.obState.update({'ERROR' : 0 , 'NEW' : 0, 'MESSAGE' : "initialised from database OK"})

    def insertDatabase(self,connection):
        insertCursor = connection.cursor()
        """ method used by functionalAssayFact object to save itself to database  """
        sql = """
            insert into functionalassayfact(
            obid,
            xreflsid,
            labresourceob ,
            assayname ,
            assaytype,
            assaydescription )
            values(
            %(obid)s,%(xreflsid)s,%(labresourceob)s,%(assayname)s,
            %(assaytype)s,%(assaydescription)s)
        """
        #print "executing %s"%(sql%self.databaseFields)
        insertCursor.execute(sql,self.databaseFields)
        connection.commit()     
        insertCursor.close()
        self.obState.update({'NEW' : 0 , 'DB_PENDING' : 0, 'ERROR' : 0, 'MESSAGE' : "database insert OK"})
        
        

        

        
        


        
        

        
        

        


