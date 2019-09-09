#
# This module implements classes relating to genetic objects
#
from types import *

from obmodule import getNewObid,getObjectRecord
from brdfExceptionModule import brdfException
from opmodule import op
from obmodule import ob
from random import randint
from displayProcedures import getSpotExpressionDisplay,getExpressionMapDisplay,getInlineURL
import databaseModule
import globalConf
import os
import logging
import re
import htmlModule

geneticmodulelogger = logging.getLogger('geneticmodulelogger')
#hdlr = logging.FileHandler('c:/temp/nutrigenomicsforms.log')
geneticmodulehdlr = logging.FileHandler(os.path.join(globalConf.LOGPATH,'geneticmodule.log'))
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
geneticmodulehdlr.setFormatter(formatter)
geneticmodulelogger.addHandler(geneticmodulehdlr) 
geneticmodulelogger.setLevel(logging.INFO)

#################### update history #######################################################################
# 22/2/2007 AMcC addition of geneticObList class - this is a clone of the oblist class from the listModule.
#



#######################################################
# this class is a wrapper for the list object.
#######################################################

class geneticOb ( ob ) :
    """ a list of objects """
    def __init__(self):
        ob.__init__(self)

        # add genetic-object specific help to the AboutMe dictionary that is inherited from
        # the ob base class
        self.AboutMe['geneindex'][0]['heading'] = 'Gene Index Objectives'
        self.AboutMe['geneindex'][0]['text'] = """
        This page presents a gene entry in the sheep gene index.
        <p>
        The sheep gene index is a database of sheep genes, with the following goals
        <ol>
<li> (ultimately) list all sheep genes 
<li> provide a complete nomenclature for each gene - e.g., list all aliases, and any other relevant nomenclature 
<li> provide an appropriate level of annotation of each gene, including functional, genetic (map), expression 
<li> provide an appropriate level of literature reference for each gene 
<li> provide an easy , flexible search capability of sheep genes (search by alias, function, location, homology etc)
<li> provide efficient procedures for merging, splitting and creating new gene index entries 
<li> provide gene-centric integration of data within the SheepGenomics bioinformatics database    
        </ol>        
        """
        self.AboutMe['geneindex'][5]['heading'] = 'Gene Index Data Sources'
        self.AboutMe['geneindex'][5]['text'] = """
        The sheep gene index has been built from the following sources
        <ol>
<li> NCBI Homologene
<li> NCBI Entrez Gene 
<li> NCBI Unigene 
<li> Sheep ESTs 
<li> Sheep QTL
<li> Sheep virtual genome
        </ol>        
        """
        self.AboutMe['geneindex'].update (
            { 10 : {
                'heading' : 'Gene Index Build Process',
                'text' : """
        <ul>
        <li> The initial sheep gene index (SGI) contains one entry for each NCBI Homologene accession that
        contains a homologous gene in any of :
        <p/>
        <ul>
           <li> H. sapiens
           <li> C. familiaris
           <li> M. musculus
           <li> R. norvegicus
        </ul>
        <p/>
        <li> For each of resulting SGI entries, selected relevant records from Entrez Gene and Unigene are retrieved
        for the homologous genes in each of the above 4 species, where available
        <p/>
        <li> Homologene records include links to probable homologues in Unigene, for a wider range of species
        than the main four species above. Where there is such a putative homolog in one of the species in the list
        below, then details of that Unigene and , if present, its parent Entrez gene record, are included
        in the gene index entry. 
        <p/>
        The Association Type field in the main table indicates which of the above types of association
        supports the homologue.  To emphasize that the association with the homologous genes making
        up the orginal homologene are stronger than those supported just by the tblastn links , the
        strongly associated records are highlighted with a light green background.
        <p/>
<table border=yes cellpadding=0 cellspacing=0 width=600>
 <tr>
  <th >TAXID</td>
  <th >UniGene prefix</td>
  <th >Species</td>
  <th >Common name</td>
 </tr>
 <tr>
  <td >31033</td>
  <td>Tru</td>
  <td>Takifugu rubripes</td>
  <td>torafugu;</td>
 </tr>
 <tr>
  <td >7955</td>
  <td>Dr</td>
  <td>Danio rerio</td>
  <td>zebra danio;zebra fish;zebrafish;</td>
 </tr>
 <tr>
  <td >8022</td>
  <td>Omy</td>
  <td>Oncorhynchus mykiss</td>
  <td>rainbow trout;</td>
 </tr>
 <tr>
  <td >8030</td>
  <td>Ssa</td>
  <td>Salmo salar</td>
  <td>Atlantic salmon;</td>
 </tr>
 <tr>
  <td >8078</td>
  <td>Fhe</td>
  <td>Fundulus heteroclitus</td>
  <td>Atlantic killifish;killifish;mummichog;</td>
 </tr>
 <tr>
  <td >8090</td>
  <td>Ola</td>
  <td>Oryzias latipes</td>
  <td>Japanese medaka;Japanese rice fish;</td>
 </tr>
 <tr>
  <td >8355</td>
  <td>Xl</td>
  <td>Xenopus laevis</td>
  <td>African clawed frog;clawed frog;</td>
 </tr>
 <tr>
  <td >8364</td>
  <td>Str</td>
  <td>Xenopus tropicalis</td>
  <td>western clawed frog;</td>
 </tr>
 <tr>
  <td >9031</td>
  <td>Gga</td>
  <td>Gallus gallus</td>
  <td>chicken;chickens;</td>
 </tr>
 <tr>
  <td >9541</td>
  <td>Mfa</td>
  <td>Macaca fascicularis</td>
  <td>crab eating macaque;crab-eating macaque;cynomolgus
  monkey;cynomolgus monkeys;long-tailed macaque;</td>
 </tr>
 <tr>
  <td >9544</td>
  <td>Mmu</td>
  <td>Macaca mulatta</td>
  <td>rhesus macaque;rhesus macaques;rhesus monkey;rhesus monkeys;</td>
 </tr>
 <tr>
  <td >9823</td>
  <td>Ssc</td>
  <td>Sus scrofa</td>
  <td>pig;pigs;swine;wild boar;</td>
 </tr>
 <tr>
  <td >9913</td>
  <td>Bt</td>
  <td>Bos taurus</td>
  <td>bovine;cattle;cow;domestic cattle;domestic cow;</td>
 </tr>
 <tr>
  <td >9940</td>
  <td>Oar</td>
  <td>Ovis aries</td>
  <td>domestic sheep;lambs;sheep;wild sheep;</td>
 </tr>
 <tr>
  <td >9986</td>
  <td >Ocu</td>
  <td >Oryctolagus cuniculus</td>
  <td >European rabbit;Japanese white rabbit;domestic
  rabbit;rabbit;rabbits;</td>
 </tr>
</table>
        </ul>
        """
                }
            }
        )        
        self.AboutMe['default'][0]['heading'] = 'BRDF Genetic Object'
        self.AboutMe['default'][0]['text'] = """
        This page displays a genetic object from the BRDF database.

        In the BRDF database schema, genetic objects are stored in a table called
        geneticob. Various types of genetic object can be stored in this table - for example,
        genes, SNPs, QTL, SSRs, pseudogenes, CDS , Homologenes. The type of a genetic object is
        recorded in the geneticobtype field of this table. The current set of types that are
        supported in this database are recorded in an ontology called GENETICOB_ONTOLOGY. (You can
        browse this ontology by selecting ONTOLOGIES from the drop down list of search types on the
        main page, and entering GENETICOB_ONTOLOGY as the search phrase)
        <p/>
        Genetic Location information is not recorded in the geneticob table - it is recorded
        in a seperate table called geneticlocationfact. You can review any location details available
        for a genetic object , by clicking the Genetic Location link on the genetic objectpage.
        <p/>
        (Location information is stored in a seperate table because a single genetic object may
        have multiple locations. For example, a gene may have multiple copies in one map ; even where
        a gene has only one copy , we may wish to store locations on different maps (linkage, RH,
        contig, scaffold, chromosome), or on different versions of a given type of map. Homologene
        genetic objects have different locations in different species)
        <p/>
        A Genetic Object in the BRDF database may have relationships with other types of object
        in the database - for example , a gene product relationship (e.g. mRNA transcript, or protein
        product) with a BRDF sequence object. All of the possible relationships that a genetic object may have
        with other objects in the database are depicted by icons in the information map section of the page.

        The icon is composed of the genetic ob symbol onnected to the symbol for the related object
        by a horizontal line. Where the database does not yet contain any related objects for a gene,
        the icon for that relationship is greyed out.
        <p/>
        We may store various types of facts about a given genetic object - for example, functional
        information ; expression information etc. Each type of fact supported by the BRDF is depicted
        by a line connecting the genetic symbol , to a square box labelled info, with the type of
        fact appearing to the right of the icon. Where the database does not yet contain any facts
        of a given type for a genetic object, the info icon is greyed out
        """                        


    def initNew(self,connection):      
        self.obState.update({'NEW' : 1, 'DB_PENDING' : 1})
        self.databaseFields = {
            'obid' : getNewObid(connection) ,        
            'xreflsid' : None,
            'obkeywords' : None,
            'geneticobname' : None,
            'geneticobtype' : None,
            'geneticobdescription' : None,
            'geneticobsymbols' : None,
            'obcomment'  : None }



    def initFromDatabase(self, identifier, connection):
        """ method for initialising geneticob from database """

        # first init base class - this will get obid
        ob.initFromDatabase(self, identifier, "geneticOb", connection)

        # now get the complete object
        self.databaseFields = getObjectRecord(connection, "geneticOb", self.databaseFields['obid'])

        # get location information. There may be several locations for a given gene.
        #sql = """
        #select
        # mapname  ,
        # maptype   ,
        # mapunit    ,
        # speciesname   ,      
        # speciestaxid  ,     
        # entrezgeneid  ,     
        # locusname     ,    
        # locustag      ,     
        # locussynonyms ,      
        # chromosomename ,    
        # strand         ,    
        # locationstart      ,
        # locationstring      ,
        # regionsize          ,
        # markers             ,
        # locationdescription ,
        # othermaplocation1   ,
        # evidence            ,
        # evidencescore       ,
        # evidencepvalue      
        #from
        #  geneticlocationfact
        #where
        #  geneticob = %(obid)s
        #"""
        #obCursor = connection.cursor()
        #obCursor.execute(sql,self.databaseFields)
        #allLocationFacts = obCursor.fetchall()
        #fieldNames = [item[0] for item in obCursor.description]
        #obCursor.close()        
        #self.databaseFields.update({'location' : [dict(zip(fieldNames,locationFact)) for locationFact in allLocationFacts]})

        # get function information. 
        sql = """
        select
         goterm,
         godescription,       
         functiondescription,
         functioncomment
        from
          geneticfunctionfact
        where
          geneticob = %(obid)s
        """
        obCursor = connection.cursor()
        obCursor.execute(sql,self.databaseFields)
        allFunctionFacts = obCursor.fetchall()
        fieldNames = [item[0] for item in obCursor.description]
        obCursor.close()
        if len(allFunctionFacts) > 0 :
            self.databaseFields.update({'function' : [dict(zip(fieldNames,functionFact)) for functionFact in allFunctionFacts]})


        # get expression information. 
        #sql = """
        #select
        # goterm,
        # godescription,
        # tissuetype   ,
        # lifecyclestage ,
        # cellularlocalisation ,
        # microarrayexperimentlsid ,
        # microarrayexperimentresultdescription ,
        # expressioncomment                   
        #from
        #  geneticexpressionfact
        #where
        #  geneticob = %(obid)s
        #"""
        #obCursor = connection.cursor()
        #obCursor.execute(sql,self.databaseFields)
        #allExpressionFacts = obCursor.fetchall()
        #fieldNames = [item[0] for item in obCursor.description]
        #obCursor.close()        
        #self.databaseFields.update({'expression' : [dict(zip(fieldNames,expressionFact)) for expressionFact in allExpressionFacts]})
        self.obState.update({'ERROR' : 0 , 'NEW' : 0, 'MESSAGE' : "initialised from database OK"})              
        
            
    def insertDatabase(self,connection):
        """ method used by genetic object  to save itself to database  """

        sql = """
        insert into geneticOb(obid,xreflsid,obkeywords,geneticobname,geneticobtype,
        geneticobdescription,geneticobsymbols,obcomment) values (
        %(obid)s,%(xreflsid)s,%(obkeywords)s,%(geneticobname)s,%(geneticobtype)s,
        %(geneticobdescription)s,%(geneticobsymbols)s,%(obcomment)s)"""
        
        #print "executing " + sql%self.databaseFields
        insertCursor = connection.cursor()
        insertCursor.execute(sql,self.databaseFields)
        connection.commit()
        insertCursor.close()
        self.obState.update({'NEW' : 0 , 'ERROR' : 0, 'DB_PENDING' : 0, 'MESSAGE' : "database insert OK"})
        return

    def updateDatabase(self,connection):
        """ method used by genetic object  to update itself to database  """

        sql = """
        update geneticOb set
        obkeywords = %(obkeywords)s,
        geneticobname = %(geneticobname)s,
        geneticobtype = %(geneticobtype)s,
        geneticobdescription = %(geneticobdescription)s,
        geneticobsymbols = %(geneticobsymbols)s,
        obcomment = %(obcomment)s
        where
        obid = %(obid)s
        """
     
        
        #print "executing " + sql%self.databaseFields
        updateCursor = connection.cursor()
        updateCursor.execute(sql,self.databaseFields)
        connection.commit()
        updateCursor.close()
        self.obState.update({'NEW' : 0 , 'ERROR' : 0, 'DB_PENDING' : 0, 'MESSAGE' : "database update OK"})
        return
    

    def createGeneProductLink(self, connection, biosequenceob, xreflsid, producttype = None, \
                               evidence = None ):
        """ method used to relate this gene to a product  """
        productDetails = {
            'geneticob' : self.databaseFields['obid'],
            'biosequenceob' : biosequenceob,
            'xreflsid' : xreflsid,
            'producttype' : producttype,
            'evidence' : evidence
        }
        sql = """
        insert into geneProductLink(geneticob,biosequenceob,xreflsid,
        producttype,evidence)
        values(%(geneticob)s,%(biosequenceob)s,%(xreflsid)s,
        %(producttype)s,%(evidence)s)
        """
        #print "executing %s"%(sql%productDetails)
        insertCursor = connection.cursor()
        insertCursor.execute(sql,productDetails)
        connection.commit()
        insertCursor.close()
        self.obState.update({'NEW' : 0 , 'ERROR' : 0, 'DB_PENDING' : 0, 'MESSAGE' : "gene product link insert OK"})


    def myExternalLinks(self, heading , table, width=800,context='default'):
        """ descendants of the ob class will usually override this method rather than the
        entire asHTMLRows method - this method supplies the contents of the html links panel
        """
        #heading += """
        #    <img src="%s%s" width=10/><a href="#externallinks" class=menuitem> External links </a>
        #"""%(self.imageurl,"space.gif")
            

        uriRows = ''
        mapNamePrefix="linkout%d"
        mapIndex=0
        for urituple in self.uriFields:
            # for the gene index context we do not show entre gene links as these are already
            # displayed
            if context == 'geneindex' and re.search('link to entrez gene',urituple[1],re.IGNORECASE) != None:
                continue
            mapIndex += 1
            if urituple[6] == None:
                if urituple[2] != 'system' :
                    uriRows +=  '<tr><td><a href="'+urituple[0]+\
                       '" target="externallink">'+urituple[1]+'</a></td><td>(added by '+urituple[2] + ')</td></tr>\n'
                else:
                    uriRows +=  '<tr><td colspan="2"><a href="'+urituple[0]+\
                       '" target="externallink">'+urituple[1]+'</a></tr>\n'
            else:
                mapName=mapNamePrefix%mapIndex

                # attempt to convert the icon attributes, stored using python dictionary syntax, to string for html tag
                attributeString="height=32 width=32"
                attributeDict = None
                if urituple[7] != None:
                    try:
                        attributeDict = eval(urituple[7])
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
            <tr class=sectionheading>
            <td colspan=2>
            <table class=sectionheading>
            <tr>            
            <td align=left >
            <a name="externallinks" class=whiteheading>
            External Links
            </a>
            </td>
            <td align=right>
            <a class=menuitem_small href="#top"> Top </a>
            </td>
            </tr>
            </table>
            </td>            
            </tr>
            """

        table += uriRows
        return (heading, table)
        
        
        
    


    def myHTMLSummary(self, table, width=800,context='default'):


        if context == 'geneindex':

            # currently the genes we report here are hard coded in the following
            # dictionary, which also records some other lookups we need
            indexTaxa = globalConf.taxTable
            
            # head up the table
            geneticRows = """
              <!-- this contines rows of the outer table we are living in  -->
              <tr>
              <td colspan=2 halign="top">

              <!-- each section of this will live in one row , in its own table -->
              <table width=100%% cellpadding="0" cellspacing="0" border="yes" style="background:white">
              <TR style="FONT-SIZE: 16pt; BACKGROUND: black; COLOR: red">
              <TH>%(geneticobsymbols)s </TH>
              <TH style="COLOR: white">%(geneticobdescription)s </TH></TR>
              <TR>
            """%self.databaseFields
        

            # obtain the gene symbol and source
            connection = databaseModule.getConnection()
            geneticCursor = connection.cursor()
            sql = """ select attributename , attributevalue from geneticfact where
            factnamespace = 'Nomenclature' and
            geneticob = %s
            """%self.databaseFields['obid']
            geneticCursor.execute(sql)
            rows = geneticCursor.fetchall()

            if len(rows) > 1:
                geneticDict = dict(rows)
                geneticRows += """
                  <TR>
                    <TH style="BACKGROUND: silver" align=middle>GENE Symbol: </TH>
                    <TD>%(Canonical symbol)s ( %(Canonical symbol source)s)</TD>
                  </TR>        
                """%geneticDict


            # obtain the titles
            sql = """
            select otf.termname
            from
            predicatelink p join ontologytermfact otf on
            p.subjectob = """ + str(self.databaseFields['obid']) + """ and p.predicate = 'PROVIDES_NOMENCLATURE' and
            p.predicatecomment like 'Link to titles%' and
            otf.ontologyob = p.objectob
            """
            geneticCursor.execute(sql)
            rows = geneticCursor.fetchall()

            if len(rows) >= 1:
                geneticRows += """
                <TR>
                <TH style="BACKGROUND: silver" align=middle rowSpan=%d>TITLES: </TH>"""%len(rows)

                for i in range(0,len(rows)):
                    if i > 0:
                        geneticRows += "<TR>"
                    geneticRows += """
                    <TD>%s</TD></TR>
                    """%(rows[i][0])

            # obtain the aliases
            sql = """
            select otf.termname
            from
            predicatelink p join ontologytermfact otf on
            p.subjectob = """ + str(self.databaseFields['obid']) + """ and p.predicate = 'PROVIDES_NOMENCLATURE' and
            p.predicatecomment like 'Link to aliases%' and
            otf.ontologyob = p.objectob
            """
            geneticCursor.execute(sql)
            rows = geneticCursor.fetchall()

            if len(rows) >= 1:
                geneticRows += """
                <TR>
                <TH style="BACKGROUND: silver" align=middle>ALIASES: </TH>
                <TD>"""
                for i in range(0,len(rows)):
                    if i > 0:
                        geneticRows += ",  "
                    geneticRows += (rows[i][0])
                geneticRows += "</TD></TR>"

            # type field - this is contained in the geneinfo namespace of the
            # fact table
            sql = """ select attributename , attributevalue from geneticfact where
            factnamespace = 'GeneInfo' and
            geneticob = %s
            """%self.databaseFields['obid']
            geneticCursor.execute(sql)
            rows = geneticCursor.fetchall()
            

            if len(rows) > 1:
                geneticDict.update(
                    dict(rows)
                )
                geneticRows += """
                <TR>
                <TH style="BACKGROUND: silver" align=middle>TYPE: </TH>
                <TD>%(Type Of Gene)s</TD></TR>
                """%geneticDict


            # begin the next section
            geneticRows += """
            <!-- finish the table of the previous gene index section -->
            </table>
            
            <!-- make new row in the outer table we live in -->
            <!-- no longer do this </td>
            </tr>
            <tr>
            <td colspan="2" halign="top"> -->
            <p/>

            <!-- each section lives in a table inside one of the outer table rows -->
            <table width=100%% cellpadding="0" cellspacing="0" border="yes" style="background:white">
            <!-- <tr>
            <th colspan="8" style="background:silver; color:white; font-size:16pt"> Information from <font color="green">H</font>omologene ,
            <font color="orange">U</font>nigene
            </th></tr> -->
            <tr style="background:#151b54 ; color:white" align="center">
            <th> Species</th><th>TaxID</th><th>GeneID</th><th>Symbol</th><th>Nuc.acc.</th><th>Prot.acc.</th><th>UnigeneID</th><th>Links
            </th></tr>
            """
            
            table += geneticRows

            # open a query to get rows like this :
            #H.sapiens  9606 9210 BMP15 NM_005448.1 NP_005439.1 Hs.532962 MIM PM  
            #P.troglodytes  9598 473873 - XM_529247.1 XP_529247.1 - PM STS  
            #C.familiaris  9615 491885 - XM_549005.1 XP_549005.1 - HGNC MIM
            #
            # first a query to get the distinct gene locii
            sql = """
            select
               gl.speciesname,
               gl.speciestaxid,
               gl.entrezgeneid,
               gl.locusname,
               gl.chromosomename,
               gl.locationstring,
               gl.evidence
            from
               geneticlocationfact gl
            where
               geneticob = %s"""%self.databaseFields['obid']
            geneticCursor.execute(sql)
            rows = geneticCursor.fetchall()
            fieldNames = [item[0] for item in geneticCursor.description]

            # construct a dictionary containing each of the above as a dictionary
            geneticDict = {}
            for loctuple in rows:
                mydict = dict(zip(fieldNames,loctuple))

                # careful to exclude cases where the evidence code is "Unigene Association" but
                # the species is one of the core build
                if mydict['speciestaxid'] == None:
                    continue
                if mydict['speciestaxid'] not in indexTaxa:
                    continue
                if indexTaxa[mydict['speciestaxid']]['homologene'] and mydict['evidence'] != 'Homologene Homolog':
                    continue

                
                # careful not to use the wrong entrez gene
                if mydict['speciestaxid'] in geneticDict:
                    # if the locus we have read is a proper homologene homolog it always is used
                    if mydict['evidence'] == 'Homologene Homolog':
                        geneticDict[mydict['speciestaxid']] =  mydict
                    else:
                        # we can do heuristic prioritisation based on the symbol. If the locusname in the
                        # existing entry , matches the canoncial symbol of this gene entry , then do nothing.
                        # else, if the possible replacement does match, then replace
                        if re.search(self.databaseFields['geneticobsymbols'],geneticDict[mydict['speciestaxid']]['locusname'] ,re.IGNORECASE) == None:
                            if re.search(self.databaseFields['geneticobsymbols'],mydict['locusname'],re.IGNORECASE) != None:
                                geneticDict[mydict['speciestaxid']] =  mydict
                else:
                    geneticDict[mydict['speciestaxid']] =  mydict
                    





            # get the reference sequence info via the gene product link
            sql = """
            select
               glf.entrezgeneid,
               bs.sequencename,
               bs.sequenceurl,
               gpl.producttype
            from
               ((geneticob g join geneproductlink gpl on gpl.geneticob = g.obid) join
               biosequenceob bs on bs.obid = gpl.biosequenceob  and bs.sequencetype
               in ('Protein Reference Sequence','mRNA Reference Sequence') and
               gpl.producttype in ('spliced transcript','protein') and
               gpl.evidence in ('NCBI Refseq','Homologene-Unigene-Entrez Gene asociation')) join geneticlocationfact glf on
               glf.biosequenceob = bs.obid and glf.evidence in (
               'NCBI Reference Sequence' , 'Unigene Association')
            where
               gpl.geneticob  = %s"""%self.databaseFields['obid']
            geneticmodulelogger.info("executing %s"%sql)
            geneticCursor.execute(sql)
            rows = geneticCursor.fetchall()
            fieldNames = [item[0] for item in geneticCursor.description]
            

            # construct a dictionary containing each of the above as a dictionary. Note that
            # this will arbitrarily use just one refseq of each type.
            # This is as per the current spec - which does not define this , but
            # the web interface and this query might need to be refined at some point.
            sequenceDict = {}
            for seqtuple in rows:
                mydict = dict(zip(fieldNames,seqtuple))
                if not int(mydict['entrezgeneid']) in sequenceDict:
                    sequenceDict[int(mydict['entrezgeneid'])] = {}
                    
                if mydict['producttype'] == 'spliced transcript':
                    # get the best nucleotide sequence to display - do not prefer anything over 
                    # an NM_ ; do not prefer anything over an XM except an NM ; never prefer 
                    existingseq = eval({ True : "sequenceDict[int(mydict['entrezgeneid'])]['nucrefseq']" , False : "None"}[ 'nucrefseq' in sequenceDict[int(mydict['entrezgeneid'])]   ])
                    useproduct = True 
                    if existingseq != None:
                        if len(existingseq) > 2:
                            if existingseq[0:2] == 'NM' or (\
                                existingseq[0:2] == 'XM' and re.search('^NM',mydict['sequencename']) == None):
                                useproduct = False
                            
                    if useproduct:
                        sequenceDict[int(mydict['entrezgeneid'])].update({
                            'nucrefseq' : mydict['sequencename'],
                            'nucrefsequrl' : mydict['sequenceurl']
                        })
                        
                elif mydict['producttype'] == 'protein':
                    # get the best protein sequence to display - do not prefer anything over 
                    # an NP_ ; do not prefer anything over an XP except an NP
                    existingseq = eval({ True : "sequenceDict[int(mydict['entrezgeneid'])]['protrefseq']" , False : "None"}[ 'protrefseq' in sequenceDict[int(mydict['entrezgeneid'])]   ])
                    useproduct = True 
                    if existingseq != None:
                        if len(existingseq) > 2:
                            if existingseq[0:2] == 'NP' or (\
                                existingseq[0:2] == 'XP' and re.search('^NP',mydict['sequencename']) == None):
                                useproduct = False
                            
                    if useproduct:                    
                        sequenceDict[int(mydict['entrezgeneid'])].update({
                            'protrefseq' : mydict['sequencename'],
                            'protrefsequrl' : mydict['sequenceurl']
                        })
            
            geneticmodulelogger.info(str(sequenceDict))



            # we need a sensibly ordered list of species
            taxids = indexTaxa.keys()
            taxids.sort(lambda x,y : indexTaxa[x]['sortorder'] - indexTaxa[y]['sortorder'])

            # we may need to lookup by Unigene cluster later
            indexTaxaByUnigene = dict(zip(\
                [indexTaxa[taxid]['unigeneprefix'] for taxid in taxids],\
                [{
                    'taxid' : taxid,
                    'taxname' : indexTaxa[taxid]['taxname']
                 } for taxid in taxids]))


            # get the unigene info via the nomenclature link
            sql = """
            select
               otf.termname,
               uri.uristring,
               otf2.attributevalue as entrezgeneid
            from
               ((((predicatelink pl join ontologyob ot on
               pl.objectob = ot.obid and
               pl.subjectob = %s and
               pl.predicate = 'PROVIDES_NOMENCLATURE' and
               pl.predicatecomment like 'Link to unigenes%%') join
               ontologytermfact otf on otf.ontologyob = ot.obid) join
               urilink uril on uril.ob = otf.obid) join
               uriob uri on uri.obid = uril.uriob) left outer join
               ontologytermfact2 otf2 on otf2.ontologytermid = otf.obid and 
               otf2.factnamespace = 'NCBI' and 
               otf2.attributename = 'geneid'
            """%self.databaseFields['obid']
            geneticmodulelogger.info("executing %s"%sql)
            geneticCursor.execute(sql)
            rows = geneticCursor.fetchall()
            #geneticmodulelogger.info("got %s"%str(rows))

            # make a dictionary with the unigene tax mnemonic prefixes as entries, and the
            # Unigene cluster name as key
            # note that where there is more than one unigene link this may result in the more
            # distant unigene being attached
            unigeneDict = {}
            for row in rows :
                #unigeneDict[re.split('\.',row[0])[0]] = (row[1],row[0])
                unigeneDict[row[0]] = {
                    "unigeneprefix" : re.split('\.',row[0])[0],
                    "urltuple" : (row[1],row[0]),
                    'entrezgeneid' : row[2]
                }

            geneticmodulelogger.info(str(unigeneDict))
                            


            # define colours for each entry type
            #colourDict = {
            #    'HG association' : "#%2x%2x%2x"%tuple([randint(160,254) for i in range(0,3)]),
            #    'UG and EG association' : "#%2x%2x%2x"%tuple([randint(160,254) for i in range(0,3)]),
            #    'UG association' : "#%2x%2x%2x"%tuple([randint(160,254) for i in range(0,3)]),
            #    'Symbol association' : "#%2x%2x%2x"%tuple([randint(160,254) for i in range(0,3)])
            #}
            colourDict = {
                'HG association' : "#c8f9f4",
                'UG and EG association' : "#ecf9cf",
                'UG association' : "#fdceeb",
                'Symbol association' : "#c1ced0"
            }


                

            # for each index taxa , update the dictionary we built up above,
            # with output fields and render as HTML
            for taxid in taxids:
                if taxid in geneticDict:
                    geneticDict[taxid].update({
                        'Species' : indexTaxa[taxid]['taxname'],
                        #'nucrefseq' : eval(  {True : "'<a href=%s target=refseq>%s</a>'%(sequenceDict[geneticDict[taxid]['entrezgeneid']]['nucrefsequrl'],sequenceDict[geneticDict[taxid]['entrezgeneid']]['nucrefseq'])", False : "'-'"}[(geneticDict[taxid]['entrezgeneid'] in sequenceDict)]),
                        #'protrefseq' : eval(  {True : "'<a href=%s target=refseq>%s</a>'%(sequenceDict[geneticDict[taxid]['entrezgeneid']]['protrefsequrl'],sequenceDict[geneticDict[taxid]['entrezgeneid']]['protrefseq'])", False : "'-'"}[(geneticDict[taxid]['entrezgeneid'] in sequenceDict)]),
                        #'unigenecluster' : eval( {True : "'<a href=%s target=unigene>%s</a>'%unigeneDict[indexTaxa[taxid]['unigeneprefix']]" , False : "'-'"}[ indexTaxa[taxid]['unigeneprefix'] in unigeneDict]),
                        'Homologene' : 'H', # deprecated
                        'Unigene' : eval( {True : "'U'", False : "''"}[ indexTaxa[taxid]['unigeneprefix'] in unigeneDict]), #deprecated
                        'xrefs' : '-'
                    })
                    if geneticDict[taxid]['entrezgeneid'] in sequenceDict:
                        if 'nucrefseq' in sequenceDict[geneticDict[taxid]['entrezgeneid']]:
                            geneticDict[taxid]['nucrefseq'] = '<a href=%s target=refseq>%s</a>'%(sequenceDict[geneticDict[taxid]['entrezgeneid']]['nucrefsequrl'],sequenceDict[geneticDict[taxid]['entrezgeneid']]['nucrefseq'])
                        else:
                            geneticDict[taxid]['nucrefseq'] = '-'
                            
                        if 'protrefseq' in sequenceDict[geneticDict[taxid]['entrezgeneid']]:
                            geneticDict[taxid]['protrefseq'] = '<a href=%s target=refseq>%s</a>'%(sequenceDict[geneticDict[taxid]['entrezgeneid']]['protrefsequrl'],sequenceDict[geneticDict[taxid]['entrezgeneid']]['protrefseq'])
                        else:
                            geneticDict[taxid]['protrefseq'] = '-'

                    if 'nucrefseq' not in geneticDict[taxid]:
                        geneticDict[taxid]['nucrefseq'] = '-'
                    if 'protrefseq' not in geneticDict[taxid]:
                        geneticDict[taxid]['protrefseq'] = '-'
                        

                    # add the unigene cluster. We match on both species and geneid (if a unigene is not associated with an entrez gene
                    # then we are not interested in it at this point )
                    for unigeneData in unigeneDict.values():
                        if unigeneData['unigeneprefix'] == indexTaxa[taxid]['unigeneprefix'] and \
                            unigeneData['entrezgeneid'] == str(geneticDict[taxid]['entrezgeneid']):
                            geneticDict[taxid]['unigenecluster'] = '<a href=%s target=unigene>%s</a>'%unigeneData['urltuple']

                    if 'unigenecluster' not in geneticDict[taxid]:
                        geneticDict[taxid]['unigenecluster'] = '-'
                              

                    # calculate the colour of the row. Entrez Locations that were linked via
                    # round tripping through Unigene , rather than directly, will have a different
                    # evidence code 
                    if geneticDict[taxid]['evidence'] == 'Homologene Homolog':
                        geneticDict[taxid].update({
                           'background' : colourDict['HG association']
                        })
                    elif geneticDict[taxid]['evidence'] == 'Unigene Association':
                        geneticDict[taxid].update({
                           'background' : colourDict['UG and EG association']
                        })
                    else:
                        geneticDict[taxid].update({
                           'background' : 'white'
                        })
                        
                        

                    #taxrow = """<tr align="center">
                    #   <th style="background:silver"> %(Species)s
                    #   </th><td style="background:%(background)s">%(speciestaxid)s</td><td style="background:%(background)s">%(entrezgeneid)s
                    #   </td><td style="background:%(background)s">%(locusname)s</td><td style="background:%(background)s">%(nucrefseq)s</td>
                    #   <td style="background:%(background)s">%(protrefseq)s</td><td style="background:%(background)s">%(unigenecluster)s</td>
                    #   <td style="background:%(background)s">%(xrefs)s</td></tr>
                    #    """%geneticDict[taxid]
                    geneticDict[taxid].update ( {
                        'taxurl' : htmlModule.NCBITaxonomyLink%geneticDict[taxid]['speciestaxid'],
                        'entrezgeneurl' :htmlModule.NCBIEntrezGeneLink%geneticDict[taxid]['entrezgeneid']
                    })
                    taxrow = """<tr align="center">
                       <th style="background:silver"> %(Species)s
                       </th><td style="background:%(background)s"><a href="%(taxurl)s" target=tax%(speciestaxid)s>%(speciestaxid)s</a></td>
                       <td style="background:%(background)s"><a href="%(entrezgeneurl)s" target=gene%(entrezgeneid)s> %(entrezgeneid)s </a></td>
                       <td style="background:%(background)s">%(locusname)s</td><td style="background:%(background)s">%(nucrefseq)s</td>
                       <td style="background:%(background)s">%(protrefseq)s</td><td style="background:%(background)s">%(unigenecluster)s</td>
                       <td style="background:%(background)s">%(xrefs)s</td></tr>
                        """%geneticDict[taxid]
                    
                    table += taxrow

            # begin the next part of the main section - this will list the Unigene only entries.
            # This section will present all Unigenes that are not already in the geneticDict table
            # but which are associated with this gene index entry
            mainUnigenes = [indexTaxa[taxid]['unigeneprefix'] for taxid in geneticDict.keys()]

            # for all unigenes we have associated with this entry
            for unigeneData in unigeneDict.values():
                # if this unigene not one of the core homologenes
                if not indexTaxa[int(indexTaxaByUnigene[unigeneData['unigeneprefix']]['taxid'])]['homologene']:
                    if unigeneData['unigeneprefix'] not in mainUnigenes:
                        rowDict = {
                            'speciestaxid' : indexTaxaByUnigene[unigeneData['unigeneprefix']]['taxid'],
                            'Species' : indexTaxaByUnigene[unigeneData['unigeneprefix']]['taxname'],
                            'background' : colourDict['UG association'],
                            'unigenecluster' : "<a href=%s target=unigene>%s</a>"%unigeneData['urltuple']   
                        }
                        rowDict.update ( {
                            'taxurl' : htmlModule.NCBITaxonomyLink%rowDict['speciestaxid']
                        })                        
                        #taxrow = """<tr align="center">
                        #<th style="background:silver"> %(Species)s
                        #</th><td style="background:%(background)s">%(speciestaxid)s</td>
                        #<td style="background:%(background)s">
                        #</td><td style="background:%(background)s"></td><td style="background:%(background)s"></td>
                        #<td style="background:%(background)s"></td><td style="background:%(background)s">%(unigenecluster)s</td>
                        #<td style="background:%(background)s"></td></tr>
                        #"""%rowDict
                        taxrow = """<tr align="center">
                        <th style="background:silver"> %(Species)s
                        </th><td style="background:%(background)s"><a href="%(taxurl)s" target=tax%(speciestaxid)s>%(speciestaxid)s</a></td>
                        <td style="background:%(background)s">
                        </td><td style="background:%(background)s"></td><td style="background:%(background)s"></td>
                        <td style="background:%(background)s"></td><td style="background:%(background)s">%(unigenecluster)s</td>
                        <td style="background:%(background)s"></td></tr>
                        """%rowDict                        
                        
                        table += taxrow
                    

            # output the next section - colour key
            table += """
            </table>
            <p/>            
            
            <TABLE width="100%%">
  <TBODY>
  <tr style="background:#151b54 ; color:white" align="center">
  <th> Colour key</th></tr>
  <TR style="FONT-SIZE: 8pt; BACKGROUND: %(HG association)s" align=left>
    <TD>Genes in this group are vertebrate members of the Homologene set of 
      homologues calculated by NCBI (See <A class="external text" 
      title=http://www.ncbi.nlm.nih.gov/entrez/query.fcgi?db=homologene 
      href="http://www.ncbi.nlm.nih.gov/entrez/query.fcgi?db=homologene" 
      rel=nofollow>Homologene</A>). Each Homologene entry is a group of 
      homologous EntrezGenes associated with each other using multiple lines of 
      evidence </TD></TR>
  <TR style="FONT-SIZE: 8pt; BACKGROUND: %(UG and EG association)s" align=left>
    <TD>Genes in this group are associated with the core Homologene set using 
      UniGene assignments. They too are EntrezGene entries, but coming from 
      organisms with incomplete genomes they are not yet included in the 
      Homologene clustering process. These have the advantage of the detailed 
      EntrezGene entry but are only associated with the Homologene set by 
      sequence comparison </TD></TR>
  <TR style="FONT-SIZE: 8pt; BACKGROUND: %(UG association)s" align=left>
    <TD>Members of this group are only represented by UniGene clusters. As 
      such their is no detailed EntrezGene entry but they may provided a useful 
      source of sequence information from an alternative species. They are 
      associated with the genes of the Homologene set by sequence comparison 
      only. </TD></TR>
  <TR style="FONT-SIZE: 8pt; BACKGROUND: %(Symbol association)s" align=left>
    <TD>Members of this group are added <B>purely</B> on the basis of having 
      the same Symbol. This is a very tenuous link and <B>should be treated with 
      caution</B> - these may <B>NOT</B> be true orthologues, however there are 
      some that are missed by all other means so we include them with this 
      warning </TD></TR></TBODY>"""%colourDict 



            # begin the next section - gene ontology
            geneticRows = """
            <!-- finish the table of the previous gene index section -->
            </table>

            <p/>            

            <table width="100%%" cellpadding="0" cellspacing="0" border="yes" style="background:white">
            <TBODY>
            <TR>
            <TH colspan="2" style="BACKGROUND: silver ; color:white; font-size:16pt" align=middle>Gene Ontology: </TH></tr>
            """
            sql = """
            select distinct
               uri.uristring,            
               otf.termname,
               otf.termdescription
            from
               ((ontologytermfact otf join predicatelink pl on
               otf.obid = pl.objectob and
               pl.subjectob = %s and
               pl.predicate = 'GO_ASSOCIATION' )
               join urilink uril on uril.ob = otf.obid) join
               uriob uri on uri.obid = uril.uriob
               """%self.databaseFields['obid']
            geneticmodulelogger.info("executing %s"%sql)
            geneticCursor.execute(sql)
            rows = geneticCursor.fetchall()
            fieldNames = [item[0] for item in geneticCursor.description]


            #for urituple in rows:
            #    geneticRows += """
            #    <tr><TD><a href=%s target=go>%s</a></TD><td>%s</td></TR>
            #    """%(urituple[0],urituple[1],urituple[2])

            geneticRows += """
                <tr clspan="2"><TD>** GO terms are being loaded and will be available soon **</td></TR>
                """
                

            table += geneticRows



            # begin the next section - KEGG
            #geneticRows = """
            #<!-- finish the table of the previous gene index section -->
            #</table>

            #<p/>

            #<table width="500" cellpadding="0" cellspacing="0" border="yes" style="background:white">
            #<TBODY>
            #<TR>
            #<TH style="BACKGROUND: silver ; color:white; font-size:16pt" align=middle>KEGG </TH>
            #<TD></TD></TR>
            #"""

            #table += geneticRows

            # begin the next section - we retrieve experimental expression data for the gene
            # we have
            # Hyperlinked Array Name
            # Hyperlinked Spot Name
            # Hyperlinked experiment descriptions

               
            geneticRows = """
            <!-- finish the table of the previous gene index section -->
            </table>

            <p/>

            <table width="100%%" cellpadding="0" cellspacing="0" border="yes" style="background:white">
            <TBODY>
            <TR>
            <TH colspan="2" style="BACKGROUND: silver ; color:white; font-size:16pt" align=middle>Expression : Microarray Experiments </TH>
            </TR>
            <tr style="background:#151b54 ; color:white" align="center">
            <th> Array </th><th>Spot ID</th></tr>
            """
            
            #sql = """
            #select
            #   msf.labresourceob as arrayob,
            #   lr.xreflsid as arraylsid,
            #   msf.obid as spotob,
            #   msf.xreflsid as spotlsid
            #from
            #   (microarrayspotfact msf join predicatelink pl on
            #   pl.subjectob = msf.obid and
            #   pl.objectob = %(obid)s and
            #   pl.predicate = 'ARRAYSPOT-GENE') join
            #   labresourceob lr on lr.obid = msf.labresourceob 
            #order by
            #   2,4
            #"""%self.databaseFields
            #geneticmodulelogger.info("executing %s"%sql)
            #geneticCursor.execute(sql)
            #rows = geneticCursor.fetchall()
            #fieldNames = [item[0] for item in geneticCursor.description]


            #for arraytuple in rows:
            #    geneticRows += """
            #    <tr><TD><a href=%s?obid=%s&context=default target=%s>%s</a></TD>
            #        <td><a href=%s?obid=%s&context=default target=%s>%s</a></td></TR>
            #    """%(self.fetcher,arraytuple[0],arraytuple[0],arraytuple[1],self.fetcher,arraytuple[2],arraytuple[2],arraytuple[3])            #
            #
            #table += geneticRows
            #geneticCursor.close()


            table += """
            <!-- finish the last gene index table -->
            </TABLE>"""


            table += """
            <!-- finish the row of the outer table we are living in -->
            </td></tr>
            """

            if self.obState['DYNAMIC_DISPLAYS'] > 0:
                geneticmodulelogger.info('running dynamic display functions')
                heading = ''
                for displayFunction in self.displayFunctions:
                    # exclude virtual functions - these will be instantiated in specific contexts or subclasses
                    if displayFunction[7] == None:
                        geneticmodulelogger.info('evaluating %s'%displayFunction[0])
                        # if we have a new display procedure heading , then issue this
                        if heading != displayFunction[8]:
                            heading = displayFunction[8]
                            table += """<table width="100%%" cellpadding="0" cellspacing="0" border="yes" style="background:white">
                                    <TBODY>
                                    <TR>
                                    <TH colspan="2" style="BACKGROUND: silver ; color:white; font-size:16pt" align=middle>%s </TH>
                                    </TR>
                                    """%heading
                            
                        myGraphHTML = eval(displayFunction[0])
                        table += myGraphHTML


            if self.obState['DYNAMIC_ANALYSES'] > 0:
                geneticmodulelogger.info('running dynamic analysis functions')
                heading = ''
                for analysisFunction in self.analysisFunctions:
                    # exclude virtual functions - these will be instantiated in specific contexts or subclasses
                    if analysisFunction[6] == None:
                        geneticmodulelogger.info('requesting  %s'%analysisFunction[2])
                        # if we have a new analysis procedure heading , then issue this
                        if heading != analysisFunction[7]:
                            heading = analysisFunction[7]
                            table += """<table width="100%%" cellpadding="0" cellspacing="0" border="yes" style="background:white">
                                    <TBODY>
                                    <TR>
                                    <TH colspan="2" style="BACKGROUND: silver ; color:white; font-size:16pt" align=middle>%s </TH>
                                    </TR>
                                    """%heading
                        geneticmodulelogger.info("running analysis instance : %s"%str(analysisFunction))
                        myAnalysisHTML = self.runAnalysisFunctions(connection,functionList = [analysisFunction[9]],context=context)
                        table += myAnalysisHTML                        


            return table

        else:
            return ob.myHTMLSummary(self, table, width,context)



    def asHTMLTableRows(self,title='',width=600,context='default',subcontext1='brief'):
        if context == 'default':
            return ob.asHTMLTableRows(self,title,width,context)
        elif context == 'briefsearchsummary':
            return ob.asHTMLTableRows(self,title,width,context)
                
        else:
            return ob.asHTMLTableRows(self,title,width,context)


class geneticLocationFact ( op ) :
    """ a list of objects """
    def __init__(self):
        op.__init__(self)


    def initNew(self,connection):    
        self.obState.update({'NEW' : 1, 'DB_PENDING' : 1})
        self.databaseFields = {
            'obid' : getNewObid(connection) ,        
            'xreflsid' : None,
            'geneticob' : None ,
            'biosequenceob' : None,
            'xreflsid' : None,
            'speciesname' : None  ,      
            'speciestaxid' : None  ,     
            'entrezgeneid' : None  ,     
            'locusname' : None  ,
            'evidence' : None,
            'voptypeid' : None,
            'locationstring' : None,
            'chromosomename' : None,
            'mapname' : None
        }

        
    def insertDatabase(self,connection):
        """ method used by genetic location object  to save itself to database  """

        sql = """
         insert into geneticlocationfact (
         obid,
         geneticob ,
         biosequenceob,
         xreflsid,
         speciesname  ,      
         speciestaxid  ,     
         entrezgeneid  ,     
         locusname  ,
         evidence,
         voptypeid,
         locationstring,
         chromosomename,
         mapname
         )
         values ( %(obid)s,%(geneticob)s, %(biosequenceob)s, %(xreflsid)s, %(speciesname)s, %(speciestaxid)s,%(entrezgeneid)s,
         %(locusname)s,%(evidence)s,%(voptypeid)s , %(locationstring)s, %(chromosomename)s, %(mapname)s)"""
        
        #print "executing " + sql%self.databaseFields
        insertCursor = connection.cursor()
        insertCursor.execute(sql,self.databaseFields)
        connection.commit()
        insertCursor.close()
        self.obState.update({'NEW' : 0 , 'ERROR' : 0, 'DB_PENDING' : 0, 'MESSAGE' : "database insert OK"})
        return


        
        

    def initFromDatabase(self, identifier, connection):
        """ method for initialising genetilocationFact from database """

        # first init base class - this will get obid
        ob.initFromDatabase(self, identifier, "geneticLocationFact", connection)

        # now get the complete object
        self.databaseFields = getObjectRecord(connection, "geneticLocationFact", self.databaseFields['obid'])

        # at some point maybe add retrieval of any associated feature attributs

        
class geneticFunctionFact ( op ) :
    """ a list of objects """
    def __init__(self):
        op.__init__(self)


    def initNew(self,connection):
        self.obState.update({'ERROR' : 1, 'MESSAGE' : 'initNew unimplemented for geneticFunctionFact'})
        raise brdfException, self.obState['MESSAGE'] 
        

    def initFromDatabase(self, identifier, connection):
        """ method for initialising geneticFunctionFact from database """

        # first init base class - this will get obid
        ob.initFromDatabase(self, identifier, "geneticFunctionFact", connection)

        # now get the complete object
        self.databaseFields = getObjectRecord(connection, "geneticFunctionFact", self.databaseFields['obid'])

        # at some point maybe add retrieval of any associated feature attributs


class geneticObList ( ob ) :
    """ a list of objects from the geneticob table. For example - candidate genes. Note that this class is
    a copy of the obList class """
    def __init__(self):
        ob.__init__(self)
        self.listChunkLink=None
        self.listAboutLink=' '



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

            'displayurl' : 'ob.gif'
            }
        self.obState.update({'NEW' : 1})




    def initFromDatabase(self, identifier, connection, startAtItem = 0, maxItems = 15, asSet = True):
        """ method for initialising list from database,

        The asSet option causes the list to prune identical obids after loading - i.e. so that it ends
        up being a set (no duplcates) rather than a list. This is mainly as a workaround for the lack 
        of adequate array support in the current postgres database  - in version 8.0.3 we can easily 
        and efficiently ensure that we do not insert duplicate obids into a list, however this code 
        does not work in 7.4.3 - the array assignments execute without error, however the code using 
        these assignments does not produce expected results. Once the db is upgraded, then code like 
        this can be used in the search function :

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
        ob.initFromDatabase(self, identifier, "geneticObList", connection)

        # now get the complete object
        self.databaseFields = getObjectRecord(connection, "geneticObList", self.databaseFields['obid'])

        # for this object type we need to get the members of the list. We get the obid and listorder for
        # up to maxItems members of the list, in the order specified by listOrder. 
        #sql = "select l.ob,l.listorder,o.xreflsid from ob o,listmembershiplink l where l.oblist = %s and l.listorder >= %s and o.obid = l.ob order by listorder" % (self.databaseFields['obid'],maxItems)
        if not asSet:        
            sql = """
            select
               l.geneticob,
               l.listorder,
               l.geneticobxreflsid,
               l.membershipcomment
            from
               geneticoblistmembershiplink l
            where
               l.geneticoblist = %s and
               l.listorder >= %s
               order by listorder""" % (self.databaseFields['obid'],startAtItem)
        else:
            sql = """
            select
               l.geneticob,
               l.listorder,
               l.geneticobxreflsid,
               l.membershipcomment
            from
               geneticoblistmembershiplink l
            where
               l.geneticoblist = %s 
               order by listorder""" % (self.databaseFields['obid'])
            
        geneticmodulelogger.info("genetic list executing %s"%sql)
        
        
        obCursor = connection.cursor()
        obCursor.execute(sql)
        if not asSet:
            obFieldValues = obCursor.fetchmany(maxItems)
            self.databaseFields.update({'listitems' : [(item[0],item[1],item[2],item[3]) for item in obFieldValues]})
            self.obState.update({'LIST_MODE' : 'LIST'})            
        else:
        # if we are to make a set , then do so. A problem is that we do not know the size of the
        # set (as a set rather than as a list) - but this is needed by the user interface to
        # figure out how many pages to display - so need to get wholelist
            setDict = {}
            row = obCursor.fetchone()
            while obCursor.rowcount == 1:
                item  = tuple(row)
                setDict[item[0]] = (item[1],item[2],item[3])
                row = obCursor.fetchone()

            # sort the set by list order and get a chunk, starting from startAtItem
            geneticmodulelogger.info("sorting and selecting bookmarks > %s chunk size %s"%(startAtItem,maxItems))
            setKeys = setDict.keys()
            setKeys.sort(lambda x,y:setDict[x][0] - setDict[y][0])
            chunkDict = {}
            for i in range(0,len(setDict)):
                #geneticmodulelogger.info("checking %s"%str(setDict[setKeys[i]]))
                if (int(setDict[setKeys[i]][0]) >= int(startAtItem)) and (len(chunkDict) < maxItems):
                    #geneticmodulelogger.info("selecting %s"%str(setDict[setKeys[i]]))
                    chunkDict[setKeys[i]] = setDict[setKeys[i]]

            #geneticmodulelogger.info(str(chunkDict))
            
                
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
        insert into geneticoblist (obid, xreflsid, obkeywords,createdby,
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
        geneticmodulelogger.info("executing " + sql%self.databaseFields)
        insertCursor = connection.cursor()
        insertCursor.execute(sql,self.databaseFields)
        connection.commit()
        insertCursor.close()
        self.obState.update({'NEW' : 0 , 'ERROR' : 0, 'DB_PENDING' : 0, 'MESSAGE' : "database insert OK"})



    def addListMember(self,targetob,comment,connection,membershipAnnotation = None):
        """ This method differs from a similar method in the generic oblist class as follows :
        * we check that the prospective members is a genetic ob
        * the update involves inserting an obid and an xreflsid
        * we support passing in annotation which will be inserted into the geneticoblistmembershiplinkfact table
        The format of the annotation should be an array of tuples as per
        (factnamespace, attributename, attributevalue)
        """
        # check that the target is a geneticOb
        if  targetob.__class__.__name__ != geneticOb.__name__ : 
            self.obState.update({'ERROR' : 1 , 'MESSAGE' : "target object is %s but elements of geneticObList must be genetic objects"%targetob.__class__.__name__})

            raise brdfException, self.obState['MESSAGE']               

        createdby = ''
        for subList in membershipAnnotation :
            if subList[1] == 'Submitted by' :
                createdby = subList[2]
                break
        
        # first check if this element is already in the list - if it is do not duplicate
        sql = """
        select geneticob from geneticoblistmembershiplink where
        geneticoblist = %(oblist)s and geneticob = %(ob)s
        """
        queryDict = {
            'oblist' : self.databaseFields['obid'],
            'ob' : targetob.databaseFields['obid'],
            'obxreflsid' : targetob.databaseFields['xreflsid'],
            'createdby' : createdby,
            'membershipcomment' : comment
        }
        insertCursor = connection.cursor()
        geneticmodulelogger.info("checking for listmember using %s"%(sql%queryDict))
        insertCursor.execute(sql%queryDict)
        insertCursor.fetchone()
        geneticmodulelogger.info("rowcount = %s"%insertCursor.rowcount)
        if insertCursor.rowcount == 0:

            # obtain an obid for the new record (we need to know it in case we have to add annotation
            newobid = getNewObid(connection)
            queryDict.update({
                'obid' : newobid,
                'xreflsid' : "%s.%s"%(self.databaseFields['xreflsid'],targetob.databaseFields['xreflsid'])
            })
            sql = """
            insert into geneticoblistmembershiplink(obid,xreflsid,createdby,geneticoblist,geneticob,geneticobxreflsid,membershipcomment)
            values(%(obid)s,%(xreflsid)s,%(createdby)s,%(oblist)s,%(ob)s,%(obxreflsid)s,%(membershipcomment)s)
            """
            geneticmodulelogger.info("executing %s"%(sql%queryDict))
            insertCursor.execute(sql,queryDict)
            connection.commit()


            # if we have annotation to insert then do so
            if membershipAnnotation != None:
                if len(membershipAnnotation) > 0:
                    for annotation in membershipAnnotation:
                        if len(annotation) != 3:
                            self.obState.update(
                                {'ERROR' : 1 ,
                                 'MESSAGE' : "genetic list membership annotation must be a tuple of (factnamespace, attributename, attributevalue) but we were given %s"%str(annotation)
                                })
                            raise brdfException, self.obState['MESSAGE']
                        factFields = {
                            'geneticoblistmembershiplink' : newobid,
                            'factNameSpace' : annotation[0],
                            'attributeName' : annotation[1],
                            'attributeValue' : annotation[2]
                        }
                        sql = """
                        insert into geneticoblistmembershiplinkfact(geneticoblistmembershiplink,factNameSpace,attributeName,attributeValue)
                        values(%(geneticoblistmembershiplink)s,%(factNameSpace)s,%(attributeName)s,%(attributeValue)s)
                        """
                        geneticmodulelogger.info("executing %s"%(sql%factFields))
                        insertCursor.execute(sql,factFields)
                        connection.commit()
                        
                           
        self.obState.update({'NEW' : 0 , 'DB_PENDING' : 0, 'ERROR' : 0, 'MESSAGE' : "database insert OK"})
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
               row =  """
               <table>
               <tr><td colspan="3"><table>
               """ + \
               reduce(lambda x,y:x+y, ['<tr><td><a href='+itemtuple[4]+'&target=ob>'+itemtuple[2]+'</a></td><td>' + \
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
                geneticmodulelogger.info("debug nextlink : %s"%nextlink)                
                #nextlink = "zzzz"
            else:
                nextlink = "(No more pages)"

               
               
            table = """
               <tr>
               <td>
               <img src="%s" usemap="#obtypelink" border="0" height="42" width="42"/>
               </td>
               <td align=left>
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
               """%(self.listAboutLink,title,row,str(self.databaseFields['currentmembership']),nextlink)

                

            return table
        else:
            return ob.asHTMLTableRows(self,title,width,context)



    def addFact(self,connection,argfactNameSpace,argattributeName,argattributeValue,checkExisting=True):
        """
            NB as at 2/2007 the geneticoblistfact table has not been created - this method is left in
            for when it is created (if ever). In the meantime calling it will fail.
        """
        factFields = {
            'geneticObList' : self.databaseFields['obid'],
            'factNameSpace' : argfactNameSpace,
            'attributeName' : argattributeName,
            'attributeValue' : argattributeValue }

        doinsert = True
        insertCursor = connection.cursor()

        # first check if this fact is already in the db - if it is do not duplicate (if asked to do this)
        if checkExisting:
            sql = """
            select geneticObList from geneticobListFact where
            geneticObList = %(geneticObList)s and
            factNameSpace = %(factNameSpace)s and
            attributeName = %(attributeName)s and
            attributeValue = %(attributeValue)s
            """
            #geneticmodulelogger.info("checking for fact using %s"%(sql%factFields))
            insertCursor.execute(sql,factFields)
            insertCursor.fetchone()
            #geneticmodulelogger.info("rowcount = %s"%insertCursor.rowcount)
            if insertCursor.rowcount == 0:
                doinsert = True
            else:
                doinsert = False

        if doinsert:
            sql = """
            insert into geneticobListFact(geneticObList,factNameSpace, attributeName, attributeValue)
            values(%(geneticObList)s,%(factNameSpace)s,%(attributeName)s,%(attributeValue)s)
            """
            #geneticmodulelogger.info("executing %s"%(sql%factFields))
            insertCursor.execute(sql,factFields)
            connection.commit()
            insertCursor.close()
            self.obState.update({'NEW' : 0 , 'DB_PENDING' : 0, 'ERROR' : 0, 'MESSAGE' : "database insert OK"})
        else:
            insertCursor.close()

class geneticObListMembershipLink ( op ) :
    """ a list of objects """
    def __init__(self):
        op.__init__(self)


    def initNew(self,connection):
        self.obState.update({'ERROR' : 1, 'MESSAGE' : 'initNew unimplemented for geneticObListMembershipLink - use addListMember method in geneticObList class.'})
        raise brdfException, self.obState['MESSAGE']


    def initFromDatabase(self, identifier, connection):
        """ method for initialising geneticObListMembershipLink from database """

        # first init base class - this will get obid
        ob.initFromDatabase(self, identifier, "geneticObListMembershipLink", connection)

        # now get the complete object
        self.databaseFields = getObjectRecord(connection, "geneticObListMembershipLink", self.databaseFields['obid'])


        
                    
            
def main():
    #
    # test code only
    #
    #set up database connection  and the top level cursor
    sessiondatabase = 'nutrigenomics'
    sessionuser='nutrigenomics'
    sessionpassword='nutrigenomics'
    sessionhost='localhost'


    dbconnection=databaseModule.getConnection()
    gene = geneticOb()
    gene.initFromDatabase(47509, dbconnection)

        
    print gene.asHTMLTableRows(title='test',width='60%',context='briefsearchsummary')
    print gene.databaseFields

    dbconnection.close()


    #try :
        #page=geneSummaryPage()
        #htmlChunk = page.asHTML(304);
        #page.close()
    #except :
    #    errorPage("Error creating geneSummaryPage")
    return


if __name__ == "__main__":
   main()
        
