#-----------------------------------------------------------------------+
# Name:		agresearchPages.py             				|
#									|
# Description:	classes that implement agresearch webpages    	                |
#		                                                        |
#                                                                	|
#=======================================================================|
# Copyright 2006 by AgResearch (NZ).					|
# All rights reserved.							|
#									|
#=======================================================================|
# Revision History:							|
#									|
# Date      Ini Description						|
# --------- --- ------------------------------------------------------- |
# 3/2006    AFM  initial version                                        |
#-----------------------------------------------------------------------+
import sys
from types import *
import databaseModule
from datetime import date
import globalConf
import agbrdfConf
import os
import re
import string

# platform dependent module search path. (This can't be done in
# a .pth because we do not always want this imported)
#sys.path.append('C:/Python23/lib/site-packages/agresearch')


# constants - these are to be obtained from a config file 
fetcher="/%s/fetch.py"%agbrdfConf.CGIPATH
waiter="/%s/wait.py"%agbrdfConf.CGIPATH
displayfetcher="/%s/fetchDisplay.py"%agbrdfConf.CGIPATH
analysisfetcher="/%s/fetchAnalysis.py"%agbrdfConf.CGIPATH
imageurl="/%s/"%agbrdfConf.IMAGEURLPATH
tempimageurl="/%s/"%agbrdfConf.TEMPIMAGEURLPATH
imagepath=os.path.join(globalConf.IMAGEFILEPATH,agbrdfConf.IMAGEFILEPATH)
jointomemberurl="/%s/"%agbrdfConf.CGIPATH + "join.py?context=%s&totype=%s&jointype=%s&joininstance=%s"
jointonullurl="/%s/"%agbrdfConf.CGIPATH + "join.py?context=%s&jointype=%s&joininstance=%s"       
jointooburl="/%s/"%agbrdfConf.CGIPATH + "join.py?context=%s&totype=%s&fromob=%s&jointype=%s&joinhash=1"
joinfacturl="/%s/"%agbrdfConf.CGIPATH + "join.py?context=%s&fromob=%s&jointype=%s&joinhash=2"
jointoopurl=joinfacturl
addCommentURL="/%s/"%agbrdfConf.CGIPATH + "form.py?context=%s&formname=commentform&formstate=insert&aboutob=%s&aboutlsid=%s"
addLinkURL="/%s/"%agbrdfConf.CGIPATH + "form.py?context=%s&formname=uriform&formstate=insert&aboutob=%s&aboutlsid=%s"
#editURL="/%s/"%agbrdfConf.CGIPATH + "form.py?formname=AgResearchSequenceSubmissionForm&formstate=edit&obid=%s"
editURL=os.path.join(agbrdfConf.PAGEPATH,agbrdfConf.UNDERCONSTRUCTION) # re-set below on a type by type basis
homeurl="/%s"%agbrdfConf.HOMEPATH
underConstructionURL=os.path.join(agbrdfConf.PAGEPATH,agbrdfConf.UNDERCONSTRUCTION)
waitURL=os.path.join(agbrdfConf.IMAGEURLPATH,agbrdfConf.WAITGLYPH)
padlockurl="%s%s"%(imageurl,agbrdfConf.PADLOCK)


objectDumpURL="/%s/"%agbrdfConf.CGIPATH + "fetch.py?obid=%s&context=%s"
listChunkLink="/%s/"%agbrdfConf.CGIPATH + 'fetch.py?obid=%s&context=briefsearchsummarypage&bookmark=%s&target=ob&childview=%s&page=%s'

brdfCSSLink=agbrdfConf.BRDF_CSS_LINK




import logging
import htmlModule
from listModule import obList
from obmodule import ob,getObTypeMetadata,getOpDefinition,getDatafields,getJoinQuery,getColumnAliases,getInstanceBaseType,getObTypeName
from geneticModule import geneticOb, geneticLocationFact, geneticFunctionFact
from studyModule import geneExpressionStudy, bioProtocolOb, phenotypeStudy, phenotypeObservation, microarrayObservation,\
                 bioDatabaseOb,databaseSearchStudy,databaseSearchObservation,genotypeStudy,genotypeObservation
from biosubjectmodule import bioSampleOb, bioSubjectOb, bioSamplingFunction, bioSampleList
from dataImportModule import dataSourceOb, importProcedureOb, importFunction,dataSourceList
from sequenceModule import bioSequenceOb, bioSequenceFeatureFact, sequencingFunction,sequenceAlignmentFact,bioLibraryOb,librarySequencingFunction
from labResourceModule import microarraySpotFact, labResourceOb, labResourceList, microarrayFact,geneticTestFact
from workFlowModule import workFlowOb, workFlowStageOb
from ontologyModule import ontologyOb, ontologyTermFact
from annotationModule import commentOb, uriOb
from analysisModule import analysisProcedureOb
from brdfExceptionModule import brdfException
from htmlModule import tidyout


# set up logger if we want logging
agresearchpagemodulelogger = logging.getLogger('pages')
pagemodulehdlr = logging.FileHandler(os.path.join(globalConf.LOGPATH,'agresearchpages.log'))
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
pagemodulehdlr.setFormatter(formatter)
agresearchpagemodulelogger.addHandler(pagemodulehdlr) 
agresearchpagemodulelogger.setLevel(logging.INFO)        

""" --------- module variables ----------"""

reportSQLDict = { \
    # basic report on a list of spots :
    'defaultmicroarrayreport' : """
select
   ms.xreflsid as experiment,
   msf.gal_name as accession,
   g.geneticobname as gene,
   f.functioncomment as description,
   mo.gpr_logratio as raw_logratio,
   mo.norm_logratio as normalised_logratio
from
   ((((((listmembershiplink lml join microarrayspotfact msf on lml.ob = msf.obid ) join microarrayobservation mo  on 
   mo.microarrayspotfact = msf.obid ) join
   (geneexpressionstudy ms join listmembershiplink elml on
   elml.ob = ms.obid) on
   mo.microarraystudy = ms.obid)
   left outer join 
   (biosequenceob bs left outer join geneproductlink gp on 
   gp.biosequenceob = bs.obid ) on 
   msf.GAL_Name = bs.sequenceName ) 
   left outer join 
   geneticob g on 
   g.obid = gp.geneticob)
   left outer join 
   geneticlocationfact l on
   l.geneticob = g.obid)
   left outer join
   geneticfunctionfact f on 
   f.geneticob = g.obid
where
   lml.oblist = %(spotlistid)s and
   elml.oblist = %(experimentlistid)s
order by msf.gal_name, ms.xreflsid
   """,
    'flankinggenereport1': """
select 
   distinct
   g.xreflsid as genelsid,
   g.geneticobsymbols,
   g.geneticobdescription,
   glseq.speciesname,
   glseq.entrezgeneid,
   b1.sequencetype as Type,
   gl1.chromosomename as Chromosome,
   gl1.locationstart as flankingGeneStart,
   gl1.locationstop as flankingGeneStop,
   gl1.evidence as locationEvidence,
   gl1.xreflsid as locationLSID,
   gl1.mapname as "Map Name"
from 
   ((((((listmembershiplink lml join geneproductlink gpl on gpl.geneticob = lml.ob)
   left outer join geneticlocationfact gl0 on gl0.biosequenceob = gpl.biosequenceob) left outer join
   geneticlocationfact gl1 on gl1.mapname = gl0.mapname and gl1.chromosomename = gl0.chromosomename and 
   gl1.locationstart >= gl0.locationstart - %(flanking)s and gl1.locationstart <= gl0.locationstop
   + %(flanking)s ) left outer join geneproductlink gpl1 on
   gpl1.biosequenceob = gl1.biosequenceob ) left outer join
   geneticob g on g.obid = gpl1.geneticob ) left outer join geneticlocationfact glseq on
   glseq.biosequenceob = gl1.biosequenceob and
   glseq.mapname is null) join biosequenceob b1 on 
   b1.obid = gl1.biosequenceob
where
   lml.oblist = %(listid)s and
   gl0.mapname = '%(mapname)s'
union
select
   g1.xreflsid as genelsid,
   g1.geneticobsymbols,
   g1.geneticobdescription,
   gl.speciesname,
   gl.entrezgeneid,
   '' as Type,
   gl1.chromosomename as Chromosome,
   gl1.locationstart as flankingGeneStart,
   gl1.locationstop as flankingGeneStop,
   gl1.evidence as locationEvidence,
   gl1.xreflsid as locationLSID,
   gl1.mapname as "Map Name"
from
   ((listmembershiplink lml join geneticlocationfact gl on gl.geneticob = lml.ob) left outer join 
   geneticlocationfact gl1 on gl1.mapname = gl.mapname and gl1.chromosomename = gl.chromosomename and
   gl1.locationstart >= gl.locationstart - %(flanking)s and gl1.locationstart <= gl.locationstop
   + %(flanking)s ) join geneticob g1 on
   g1.obid = gl1.geneticob 
where
   lml.oblist = %(listid)s and
   gl.mapname = '%(mapname)s'
%(orderbyclause)s
union
select
   g1.xreflsid as genelsid,
   g1.locusname,
   g1.testdescription,
   gl.speciesname,
   gl.entrezgeneid,
   '' as Type,
   gl1.chromosomename as Chromosome,
   gl1.locationstart as flankingGeneStart,
   gl1.locationstop as flankingGeneStop,
   gl1.evidence as locationEvidence,
   gl1.xreflsid as locationLSID,
   gl1.mapname as "Map Name"
from
   ((listmembershiplink lml join geneticlocationfact gl on gl.geneticob = lml.ob) left outer join
   geneticlocationfact gl1 on gl1.mapname = gl.mapname and gl1.chromosomename = gl.chromosomename and
   gl1.locationstart >= gl.locationstart - %(flanking)s and gl1.locationstart <= gl.locationstop
   + %(flanking)s ) join genetictestfact g1 on
   g1.obid = gl1.genetictestfact
where
   lml.oblist = %(listid)s and
   gl.mapname = '%(mapname)s'
%(orderbyclause)s
    """,
    'flankinggenereport2': """
select 
   g.xreflsid as genelsid,
   g.geneticobsymbols,
   g.geneticobdescription,
   glseq.speciesname,
   glseq.entrezgeneid,
   b1.sequencetype as Type,
   gl1.chromosomename as Chromosome,
   gl1.locationstart as flankingGeneStart,
   gl1.locationstop as flankingGeneStop,
   gl1.evidence as locationEvidence,
   gl1.xreflsid as locationLSID,
   gl1.mapname as "Map Name"
from 
   (((geneticlocationfact gl1 left outer join geneproductlink gpl1 on
   gpl1.biosequenceob = gl1.biosequenceob ) left outer join
   geneticob g on g.obid = gpl1.geneticob) left outer join geneticlocationfact glseq on
   glseq.biosequenceob = gl1.biosequenceob and
   glseq.mapname is null) join biosequenceob b1 on 
   b1.obid = gl1.biosequenceob
where
   gl1.mapname = '%(mapname)s' and
   gl1.chromosomename = '%(chromosome)s' and
   (gl1.locationstart between %(mapstart)s and %(mapstop)s or
    gl1.locationstop between %(mapstart)s and %(mapstop)s)
union
select 
   g.xreflsid as genelsid,
   g.geneticobsymbols,
   g.geneticobdescription,
   gl.speciesname,
   gl.entrezgeneid,
   '' as Type,
   gl.chromosomename as Chromosome,
   gl.locationstart as flankingGeneStart,
   gl.locationstop as flankingGeneStop,
   gl.evidence as locationEvidence,
   gl.xreflsid as locationLSID,
   gl.mapname as "Map Name"
from 
   (geneticlocationfact gl join geneticob g on
   gl.geneticob = g.obid) 
where
   gl.mapname = '%(mapname)s' and
   gl.chromosomename = '%(chromosome)s' and
   (gl.locationstart between %(mapstart)s and %(mapstop)s or
    gl.locationstop between %(mapstart)s and %(mapstop)s )
%(orderbyclause)s
union
select
   g.xreflsid as genelsid,
   g.locusname,
   g.testdescription,
   gl.speciesname,
   gl.entrezgeneid,
   '' as Type,
   gl.chromosomename as Chromosome,
   gl.locationstart as flankingGeneStart,
   gl.locationstop as flankingGeneStop,
   gl.evidence as locationEvidence,
   gl.xreflsid as locationLSID,
   gl.mapname as "Map Name"
from
   (geneticlocationfact gl join genetictestfact g on
   gl.genetictestfact = g.obid)
where
   gl.mapname = '%(mapname)s' and
   gl.chromosomename = '%(chromosome)s' and
   (gl.locationstart between %(mapstart)s and %(mapstop)s or
    gl.locationstop between %(mapstart)s and %(mapstop)s )
%(orderbyclause)s
    """,
    'flankinggenereport3': """
select 
   distinct
   g.xreflsid as genelsid,
   g.geneticobsymbols,
   g.geneticobdescription,
   glseq.speciesname,
   glseq.entrezgeneid,
   b1.sequencetype as Type,
   gl1.chromosomename as Chromosome,
   gl1.locationstart as flankingGeneStart,
   gl1.locationstop as flankingGeneStop,
   gl1.evidence as locationEvidence,
   gl1.xreflsid as locationLSID,
   gl1.mapname as "Map Name",
   l.listdefinition as "Parent Query"
from 
   (((((((listmembershiplink lml join oblist l on lml.oblist = l.obid) join geneproductlink gpl on gpl.geneticob = lml.ob)
   left outer join geneticlocationfact gl0 on gl0.biosequenceob = gpl.biosequenceob) left outer join
   geneticlocationfact gl1 on gl1.mapname = gl0.mapname and gl1.chromosomename = gl0.chromosomename and 
   gl1.locationstart >= gl0.locationstart - %(flanking)s and gl1.locationstart <= gl0.locationstop
   + %(flanking)s ) left outer join geneproductlink gpl1 on
   gpl1.biosequenceob = gl1.biosequenceob ) left outer join
   geneticob g on g.obid = gpl1.geneticob ) left outer join geneticlocationfact glseq on
   glseq.biosequenceob = gl1.biosequenceob and
   glseq.mapname is null) join biosequenceob b1 on 
   b1.obid = gl1.biosequenceob
where
   lml.oblist in %(listclause)s and
   gl0.mapname = '%(mapname)s'
union
select
   g1.xreflsid as genelsid,
   g1.geneticobsymbols,
   g1.geneticobdescription,
   gl.speciesname,
   gl.entrezgeneid,
   '' as Type,
   gl1.chromosomename as Chromosome,
   gl1.locationstart as flankingGeneStart,
   gl1.locationstop as flankingGeneStop,
   gl1.evidence as locationEvidence,
   gl1.xreflsid as locationLSID,
   gl1.mapname as "Map Name",
   l.listdefinition as "Parent Query"
from
   (((listmembershiplink lml join oblist l on lml.oblist = l.obid) join geneticlocationfact gl on gl.geneticob = lml.ob) left outer join 
   geneticlocationfact gl1 on gl1.mapname = gl.mapname and gl1.chromosomename = gl.chromosomename and
   gl1.locationstart >= gl.locationstart - %(flanking)s and gl1.locationstart <= gl.locationstop
   + %(flanking)s ) join geneticob g1 on
   g1.obid = gl1.geneticob 
where
   lml.oblist in %(listclause)s and
   gl.mapname = '%(mapname)s'
%(orderbyclause)s
union
select
   g1.xreflsid as genelsid,
   g1.locusname,
   g1.testdescription,
   gl.speciesname,
   gl.entrezgeneid,
   '' as Type,
   gl1.chromosomename as Chromosome,
   gl1.locationstart as flankingGeneStart,
   gl1.locationstop as flankingGeneStop,
   gl1.evidence as locationEvidence,
   gl1.xreflsid as locationLSID,
   gl1.mapname as "Map Name",
   l.listdefinition as "Parent Query"
from
   (((listmembershiplink lml join oblist l on lml.oblist = l.obid) join geneticlocationfact gl on gl.geneticob = lml.ob) left outer join
   geneticlocationfact gl1 on gl1.mapname = gl.mapname and gl1.chromosomename = gl.chromosomename and
   gl1.locationstart >= gl.locationstart - %(flanking)s and gl1.locationstart <= gl.locationstop
   + %(flanking)s ) join genetictestfact g1 on
   g1.obid = gl1.genetictestfact
where
   lml.oblist in %(listclause)s and
   gl.mapname = '%(mapname)s'
%(orderbyclause)s
    """,
    'genstatmicroarrayextract1' : """
select
    mo.microarraystudy as "Experimentid!",
    msf.obid as "Spotid!",
    msf.blocknumber as "Slide_block!",
    msf.blockrow as "Slide_row!",
    msf.blockcolumn  as "Slide_col!",
    msf.metarow as "Metarow!",
    msf.metacolumn as "Metacol!",
    mo.rawdatarecord
from
    microarrayspotfact msf join microarrayobservation mo
    on mo.microarraystudy = %(microarraystudy)s and
    msf.obid = mo.microarrayspotfact
    """,
    'microarraysummary1' : """
select
    mo.microarraystudy as "Experimentid!",
    msf.obid as "Spotid!",
    msf.blocknumber as "Slide_block!",
    msf.blockrow as "Slide_row!",
    msf.blockcolumn  as "Slide_col!",
    msf.metarow as "Metarow!",
    msf.metacolumn as "Metacol!",
    mo.rawdatarecord
from
    microarrayspotfact msf join microarrayobservation mo
    on mo.microarraystudy = %(microarraystudy)s and
    msf.obid = mo.microarrayspotfact
    """,
    'genstatnormalisationextract1' : """
select
    ms.xreflsid as "ExperimentName!",
    mo.microarraystudy as "Experimentid!",
    msf.accession as "EST!",
    msf.obid as "Spotid!",
    msf.blocknumber as "Slide_block!",
    msf.blockrow as "Slide_row!",
    msf.blockcolumn  as "Slide_col!",
    msf.metarow as "Metarow!",
    msf.metacolumn as "Metacol!",
    getMicroarrayObservationNumFact(mo.obid,'NORMALISED VALUE','clogRatio','*') as clogRatio,
    getMicroarrayObservationNumFact(mo.obid,'NORMALISED VALUE','Intensity','*') as Intensity
from
    (microarrayspotfact msf join microarrayobservation mo
    on mo.microarraystudy = %(microarraystudy)s and
    msf.obid = mo.microarrayspotfact) join geneexpressionstudy ms on 
    ms.obid = mo.microarraystudy
    """,
    'sequencereport1': """
select
   bs.xreflsid || ' ' || bs.sequencedescription as idline,
   bs.seqstring
 from
   biosequenceob bs join listmembershiplink lml on 
   lml.oblist = %s and bs.obid = lml.ob
    """,
    'sequencereport2': """
select
   bs.xreflsid || ' ' || bs.sequencedescription as idline,
   bs.seqstring
 from
   ((biosequenceob bs0 join listmembershiplink lml on 
   lml.oblist = %s and bs0.obid = lml.ob)
   join databasesearchobservation dso on dso.hitsequence = lml.ob)
   join biosequenceob bs on bs.obid = dso.querysequence
    """  ,
    'gbsreport1' :
    """
select
   l.listname as run,
   g.flowcell,
   g.lane ,
   g.barcode,
   g.sample ,
   g.qc_sampleid,
   g.platename ,
   g.platerow ,
   g.platecolumn ,
   g.libraryprepid,
   g.counter ,
   g.comment ,
   g.enzyme ,
   g.species ,
   g.numberofbarcodes,
   g.bifo ,
   g.control ,
   g.fastq_link,
   y.tag_count,
   y.read_count,
   y.callrate,
   y.sampdepth
from
   (((gbskeyfilefact as g join gbsYieldFact as y on
   g.sample = y.sampleid and
   g.flowcell = y.flowcell and
   g.lane = y.lane) join biosampleob as b on b.obid = g.biosampleob)
   join biosamplelistmembershiplink as m on m.biosampleob = b.obid)
   join biosamplelist as l on 
   l.obid = m.biosamplelist where %s
union
select
   l.listname as run,
   g.flowcell,
   g.lane ,
   g.barcode,
   g.sample ,
   g.qc_sampleid,
   g.platename ,
   g.platerow ,
   g.platecolumn ,
   g.libraryprepid,
   g.counter ,
   g.comment ,
   g.enzyme ,
   g.species ,
   g.numberofbarcodes,
   g.bifo ,
   g.control ,
   g.fastq_link,
   y.tag_count,
   y.read_count,
   y.callrate,
   y.sampdepth
from
   (((gbskeyfilefact as g join gbsYieldFact as y on
   g.qc_sampleid = y.sampleid and
   g.flowcell = y.flowcell and
   g.lane = y.lane) join biosampleob as b on b.obid = g.biosampleob)
   join biosamplelistmembershiplink as m on m.biosampleob = b.obid)
   join biosamplelist as l on
   l.obid = m.biosamplelist where %s
    """,
    'gbsreport2' :
    """
select
   l.listname as run,
   g.flowcell,
   g.lane ,
   g.barcode,
   g.sample ,
   g.qc_sampleid,
   g.platename ,
   g.platerow ,
   g.platecolumn ,
   g.libraryprepid,
   g.counter ,
   g.comment ,
   g.enzyme ,
   g.species ,
   g.numberofbarcodes,
   g.bifo ,
   g.control ,
   g.fastq_link,
   y.tag_count,
   y.read_count,
   y.callrate,
   y.sampdepth
from
   (((gbskeyfilefact as g left outer join gbsYieldFact as y on
   g.sample = y.sampleid and
   g.flowcell = y.flowcell and
   g.lane = y.lane) join biosampleob as b on b.obid = g.biosampleob)
   join biosamplelistmembershiplink as m on m.biosampleob = b.obid)
   join biosamplelist as l on 
   l.obid = m.biosamplelist where %s
union
select
   l.listname as run,
   g.flowcell,
   g.lane ,
   g.barcode,
   g.sample ,
   g.qc_sampleid,
   g.platename ,
   g.platerow ,
   g.platecolumn ,
   g.libraryprepid,
   g.counter ,
   g.comment ,
   g.enzyme ,
   g.species ,
   g.numberofbarcodes,
   g.bifo ,
   g.control ,
   g.fastq_link,
   y.tag_count,
   y.read_count,
   y.callrate,
   y.sampdepth
from
   (((gbskeyfilefact as g left outer join gbsYieldFact as y on
   g.qc_sampleid = y.sampleid and
   g.flowcell = y.flowcell and
   g.lane = y.lane) join biosampleob as b on b.obid = g.biosampleob)
   join biosamplelistmembershiplink as m on m.biosampleob = b.obid)
   join biosamplelist as l on
   l.obid = m.biosamplelist where %s
    """,
   'unblind_report': 
   """
select distinct  
   sample,
   qc_sampleid
from 
   ((gbskeyfilefact as g join biosampleob as b on b.obid = g.biosampleob )
   join biosamplelistmembershiplink as m on m.biosampleob = b.obid )
   join biosamplelist as l on 
   l.obid = m.biosamplelist
where %s
order by 
   1
   """
    }

# page schema
report_microarrayextract1 = """
<!doctype html public "-//w3c//dtd html 4.0 transitional//en"><html>
<head>
<title> AgResearch Microarray Extracts </title>
<link rel="stylesheet" type="text/css" href="/css/forms.css">
<script type="text/javascript">

var bgColour = "";
var alreadySubmitted = false;

function checkAll() {   
   if (simplereport.experiments.value == "") {
      highLight(simplereport.experiments,"You must select one or more experiments");
      return false;         
   }
   else {
      lowLight(simplereport.experiments);      
   }

   if(trim(simplereport.reportmenu.value) == "flagsummary1" ) {
      if (simplereport.outputformat.value != "html") {
         highLight(simplereport.outputformat,"Only HTML format is supported for the flag summary report");
         return false;
      }
      else {
         lowLight(simplereport.experiments);
      }
   }




   // finally , set the submitted flag
   alreadySubmitted = true;


   return true;
}

function highLight(item,message) {
   if(bgColour == "")
      eval("bgColour = item.style.background");
   eval("item.style.background = 'red'");
   window.alert(message);
   item.focus();
} // assume IE

function lowLight(item) {
   //eval("item.style.background = '" + bgColour + "'");
   eval("item.style.background = 'white'");
}
/*
* a function to trim leading and trailing spaces
* from a string
*/
function trim(strval) {
   var start=-1;
   var end=-1;

   if(strval == null)
      return null;
   if(strval == "")
      return strval;

   for(i=0; i < strval.length; i++) {
      if(strval.charAt(i) != " ") {
         if(start == -1)
            start = i;
         end = i;
      }
   }

   if(start == -1)
      return "";
   else
      return strval.substring(start,1 + end);
}


function checkFloatRange(item, low, high) {
   if(isNaN(item.value))
      return false;
   if(high == null && low == null)
      return true;
   else if(high == null && parseFloat(item.value) < low)
      return false;
   else if(low == null && parseFloat(item.value) > high)
      return false;
   else if(parseFloat(item.value) < low || parseFloat(item.value) > high)
      return false;
   else 
      return true;   
}

function setValueByName(fieldName, toValue) {
   document.forms[0].elements[fieldName].value = toValue;
}

// this function can be used to focus on a field given its name
function focusByName(fieldName) {
   document.forms[0].elements[fieldName].focus();
}

// this function wil return the value of a field given its name
function getValueByName(fieldName) {
   return document.forms[0].elements[fieldName].value;
}

// this function wil return a field given its name
function getItemByName(fieldName) {
   return document.forms[0].elements[fieldName];
}

function setReportTitle() {
   if(simplereport.reportmenu.value=="genstatmicroarrayextract1") {
      simplereport.reporttitle.value="AgResearch Microarray Extract";
   }
   return true;
}



</script>


</head>
<body>
<form name="simplereport" method="post" onSubmit="return checkAll()" enctype="multipart/form-data" action="/cgi-bin/report.py" target="simpleReportListing" >
<input type="hidden" name="context" value="report"/>
<table border="true">
<tr> 
   <td colspan="2"> 
      <h1 class="top"> AgResearch Microarray Extracts </h1>
      <h2>Microarray Report Menu</h2>
   </td>
<tr>   
   <td class="fieldname"> <p class="fieldname"> Choose a report      </p>
   </td>
   <td class="input">
      <select name="reportmenu" onChange='return setReportTitle()'>
         <option value="genstatmicroarrayextract1" selected>Microarray Extract for Genstat Normalisation
         <option value="flagsummary1">Summarise Raw Microarray Data Flags
         <option value="genstatnormalisationextract1" >Extract of (Genstat) Normalised data
      </select><br/>
   </td>
</tr>
<tr>   
   <td class="fieldname"> <p class="fieldname"> Report Parameters 
   </td>
   <td  class="input">
   Report Title : 
   <input name="reporttitle" type="text" size="80" value="Microarray Extract"/>
   <p/>
   <font size="-1"><i>(In the following fields you may choose one or more items. To choose more than one item hold the control
   key down and click to select. To select a block , select first item then hold down the shift key and select the second item) </i></font>
   <p/>
   Select which experiments to extract  
   __experimentListHTML__
   </td>
</tr>
<tr> 
   <td class="fieldname"> <p class="fieldname"> Output options
   </td>
   <td  class="input">
   Sort by 
   <select name="orderbyclause">
   <option value=""> No sort
   </select>
   <br/>
   Output Format<select name="outputformat"  onChange='simplereport.filename.value="extract." + simplereport.outputformat.value; return true;'    >
   <option value="html"> html
   <option value="csv" selected> csv
   </select>   
   Output To<select name="outputto">
   <option value="browser"> Browser
   <option value="file" selected> File
   </select>
   File name<input name="filename" type="text" value="extract.csv" length="40"/>
   <br/>
   If you wish to limit the number of rows returned, enter limit (e.g. for test) :
   <input name="maxrows" type="text" value="" length="10"/>
   
</tr>
<tr>
   <td colspan="2">
   <p class="footer">
   <input type="submit" value="Run report"/>
   </p>
    </td>
</tr>
</table>

</form>
</body>
</html>"""


report_locusreports = """
<!doctype html public "-//w3c//dtd html 4.0 transitional//en"><html>
<head>
<title> Genetic/Genomic Map Reporting </title>
<link rel="stylesheet" type="text/css" href="/css/forms.css">
</head>
<body>
<form name="simplereport" method="post" enctype="multipart/form-data" action="/cgi-bin/report.py" target="simpleReportListing" >
<input type="hidden" name="context" value="report"/>
<table border="true" width=100%%>
<tr> 
   <td colspan="2"> 
      <h1 class="top"> Genetic/Genomic Map Reporting </h1>
      <pre>
      This report allows you to batch-extract features from maps, and generate hyperlinks for browsers and sequence retrieval.
      To specify your extract you can :
      
      * Specify a coordinate range
          or
      * Choose a project-list of genes. All features flanking these genes will be extracted
          or
      * Choose a previous search list. All features flanking genes from this list will be extracted
          or
      * Paste in a list of gene names or keywords. Each will be used to search the database, and features flanking
        genes found in the search will be extracted
        
      </pre>
   </td>
<tr>   
   <td class="fieldname"> <p class="fieldname"> Choose a report      </p>
   </td>
   <td class="input">
      <select name="reportmenu">
         <option value="flankinggenereport1">Flanking Genes
      </select><br/>
   </td>
</tr>
<tr>   
   <td class="fieldname"> <p class="fieldname"> Choose a map     </p>
   </td>
   <td class="input">
      <select name="mapname">
         <option value="Btau_3.0">Btau 3.0 Bovine Genome
      </select><br/>
   </td>
</tr>
<tr>   
   <td colspan="2" class="sectionheading"> <p class="fieldname"> Specify your extract using one of the following panels : </p>
   </td>
<tr>
   <td colspan="2" class="input">
      
      <input type="radio" name="cohortmethod" value="coordinate" checked/> Coordinate option : <br>
      Extract all genes and sequences that are between 
      <input name="mapposition0" type="input" value="10000000"/>
      and
      <input name="mapposition1" type="input" value="20000000"/>
     <select name="positionunit">
         <option value="1" selected>bases
         <option value="1000">Kilobases
         <option value="1000000">Megabases
      </select>      
      on chromosome
      <select name="chromosome">
 <optgroup label="Sheep">
 <option value="OAR1">OAR1
 <option value="OAR2">OAR2
 <option value="OAR3">OAR3
 <option value="OAR4">OAR4
 <option value="OAR5">OAR5
 <option value="OAR6">OAR6
 <option value="OAR7">OAR7
 <option value="OAR8">OAR8
 <option value="OAR9">OAR9
 <option value="OAR10">OAR10
 <option value="OAR11">OAR11
 <option value="OAR12">OAR12
 <option value="OAR13">OAR13
 <option value="OAR14">OAR14
 <option value="OAR15">OAR15
 <option value="OAR16">OAR16
 <option value="OAR17">OAR17
 <option value="OAR18">OAR18
 <option value="OAR19">OAR19
 <option value="OAR20">OAR20
 <option value="OAR21">OAR21
 <option value="OAR22">OAR22
 <option value="OAR23">OAR23
 <option value="OAR24">OAR24
 <option value="OAR25">OAR25
 <option value="OAR26">OAR26
 <option value="OARX">OARX
 </optgroup>      
<optgroup label="Cow">
<option value="BTA1">BTA1
<option value="BTA2">BTA2
 <option value="BTA3">BTA3
 <option value="BTA4">BTA4
 <option value="BTA5">BTA5
 <option value="BTA6">BTA6
 <option value="BTA7">BTA7
 <option value="BTA8">BTA8
 <option value="BTA9">BTA9
 <option value="BTA10">BTA10
 <option value="BTA11">BTA11
 <option value="BTA12">BTA12
 <option value="BTA13">BTA13
 <option value="BTA14">BTA14
 <option value="BTA15">BTA15
 <option value="BTA16">BTA16
 <option value="BTA17">BTA17
 <option value="BTA18">BTA18
 <option value="BTA19">BTA19
 <option value="BTA20">BTA20
 <option value="BTA21">BTA21
 <option value="BTA22">BTA22
 <option value="BTA23">BTA23
 <option value="BTA24">BTA24
 <option value="BTA25">BTA25
 <option value="BTA26">BTA26
 <option value="BTA27">BTA27
 <option value="BTA28">BTA28
 <option value="BTA29">BTA29
 <option value="BTA30">BTA30
 </optgroup>
      </select>
      <p/>
      <hr>
      <p/>
    <input type="radio" name="cohortmethod" value="candidategenelist"/> Gene Project-List option - extract all features flanking all
    genes in the following project list<br>
      %(candidategeneListHTML)s
      ...within a flanking distance of <input name="candidateflankingdistance" type="input" value="10"/>
     <select name="candidateflankingunit">
         <option value="1">bases
         <option value="1000" selected>Kilobases
         <option value="1000000">Megabases
      </select>
      <p/>
      <hr>
      <p/>
    <input type="radio" name="cohortmethod" value="genelist"/> Genes on search list option - extract all features flanking all
    genes that were found in one of the following searches<br>
      %(geneListHTML)s
      ...within a flanking distance of <input name="listflankingdistance" type="input" value="10"/>
     <select name="listflankingunit">
         <option value="1">bases
         <option value="1000" selected >Kilobases
         <option value="1000000">Megabases
      </select>
      <p/>
      <font size="-1"> <i> (note - search lists are automatically created simply by using the main search page) </i> </font>      
      <p/>      
      <hr>
      <p/>
    <input type="radio" name="cohortmethod" value="genesymbollist"/> Gene Symbols and KeywordsOption - paste in a list of 
    one or more search strings (these can be gene symbols, keywords, refseq accessions...) - each will be used to search the database,
    and flanking features will be reported <br>
    <textarea rows="5" cols="30" name="genesymbols"></textarea>
      ...within a flanking distance of <input name="symbolsflankingdistance" type="input" value="10"/>
     <select name="symbolsflankingunit">
         <option value="1">bases
         <option value="1000" selected >Kilobases
         <option value="1000000">Megabases
      </select>
      <br/>(Each search will report at most <input type="text" name="symbolshitlimit" value="5" size="4"> hits)
      <p/>

   </td>
</tr>
<tr> 
   <td class="fieldname"> <p class="fieldname"> Output options
   </td>
   <td  class="input">
   Sort by 
   <select name="orderbyclause">
   <option value=""> No sort
   <option value=" order by gl1.chromosomename, gl1.locationstart "> Chromosome and location
   </select>
   Output Format<select name="outputformat"  onChange='simplereport.filename.value="extract." + simplereport.outputformat.value; return true;'    >
   <option value="html" selected> html
   <option value="csv"> csv
   <!-- <option value="gff"> gff  -->
   </select>      
   <br/>
   Output to : 
   <select name="outputto">
   <option value="browser" selected> Browser
   <option value="file"> File
   </select>
   File name : 
   <input name="filename" type="text" value="" length="40"/>
   <br/>
   If you wish to limit the number of rows returned, enter limit (e.g. for test) :
   <input name="maxrows" type="text" value="" length="10"/>
   <p>
   <b> Hyperlink Templates </b> :  You can have hyperlinks automatically generated and output in your report, by pasting
   templates into the following fields. When the report is run, your template will be used to generate a hyperlink
   by substituting one or more of agbrdf lsid , gene symbol, chromosome number, start and stop positions into the $LSID, $GENE, $CHRNUM, $CHRSTART and $CHRSTOP placeholders
   in the template. You can also apply an offset to the start and stop positions as indicated. For example, this could
   be used to generate a URL to retrieve upstream sequence from a given gene. Text before the http: prefix will be used as the
   display text of the link.
   Examples of possible templates are given - you may modify these, add additional links , or delete these
   <textarea name="urltemplates" rows="7" cols="120" wrap="off">
   AgResearch Gbrowse for $GENE http://gbrowse.agresearch.co.nz/cgi-bin/gbrowse/bta3/?name=$GENE
   AgResearch Gbrowse $CHRNUM:$CHRSTART..$CHRSTOP http://gbrowse.agresearch.co.nz/cgi-bin/gbrowse/bta3/?name=$CHRNUM%%3A$CHRSTART..$CHRSTOP
   AgResearch GBrowse  with selected bovine tracks $CHRNUM:$CHRSTART..$CHRSTOP  http://gbrowse.agresearch.co.nz/cgi-bin/gbrowse/bta3/?start=$CHRSTART;stop=$CHRSTOP;ref=$CHRNUM;width=1024;version=;label=GMAP_BOVINE_REFSEQ-NCBI_GENE-GMAP_HS_REFSEQS_LOW;
   AgResearch GBrowse sequence retrievel $CHRNUM:$CHRSTART..$CHRSTOP  http://gbrowse.agresearch.co.nz/cgi-bin/gbrowse/bta3/?name=$CHRNUM:$CHRSTART..$CHRSTOP;plugin=BatchDumper;BatchDumper.fileformat=fasta;BatchDumper.format=text;plugin_do=Go 
   CSIRO GBrowse $CHRNUM:$CHRSTART..$CHRSTOP http://www.livestockgenomics.csiro.au/perl/gbrowse.cgi/bova3/?name=$CHRNUM:$CHRSTART..$CHRSTOP
   AgResearch BRDF $LSID http://agbrdf.agresearch.co.nz/cgi-bin/fetch.py?obid=$LSID&context=default&target=ob
   </textarea>
   <br/>
   $CHRSTART is <select name="startis">
   <option value="locationstart"> locationstart 
   <option value="locationstop"> locationstop
   </select>
   $CHRSTOP is <select name="stopis">
   <option value="locationstart"> locationstart
   <option value="locationstop"> locationstop
   </select>
   Start offset : <input name="urlstartoffset" size="10" value="-1000"/>
   Stop offset : <input name="urlstopoffset" size="10" value="+1000"/>
   <p/>
   <font size="-1"> Example : to generate URL to extract 1500bp upstream sequence, both $CHRSTART and $CHRSTOP set to locationstart, and offsets are -1500 and -1 </font>
   <p/>
   Would you like contents of URL to be in-line in your report ? 
   <select name="inlineurl">
   <option value="no" selected/> No
   <option value="yes" /> Yes
   </select>
<tr>
   <td colspan="2">
   <p class="footer">
   <input type="submit" value="Run report"/>
   </p>
    </td>
</tr>
</table>

<a href="mailto:alan.mcculloch@agresearch.co.nz;jason.mitchell@agresearch.co.nz?Subject=Bioinformatics Database Request"/> Contact us </a>

</form>
</body>
</html>"""

report_snpreports = """
<!doctype html public "-//w3c//dtd html 4.0 transitional//en"><html>
<head>
<title> SNP Reporting </title>
<link rel="stylesheet" type="text/css" href="/css/forms.css">
</head>
<body>
<form name="simplereport" method="post" enctype="multipart/form-data" action="/cgi-bin/report.py" target="simpleReportListing" >
<input type="hidden" name="context" value="report"/>
<table border="true" width=100%%>
<tr> 
   <td colspan="2"> 
      <h1 class="top"> SNP Reporting </h1>
      <pre>
      This report allows you to extract annotation of SNPs , such as allele frequencies etc        
      </pre>
   </td>
<tr>   
   <td class="fieldname"> <p class="fieldname"> Choose a report      </p>
   </td>
   <td class="input">
      <select name="reportmenu">
         <option value="snpannotation1">Allele frequencies and indexes
      </select><br/>
   </td>
</tr>
<tr>   
   <td colspan="2" class="sectionheading"> <p class="fieldname"> Select which classes of animal you want reported </p>
   </td>
</tr>
<tr>
   <td colspan="2">
      %(animalListHTML)s
   </td>
</tr>
<tr> 
   <td class="fieldname"> <p class="fieldname"> Output options
   </td>
   <td  class="input">
   Sort by 
   <select name="orderbyclause">
   <option value=""> No sort
   </select>
   Output Format<select name="outputformat"  onChange='simplereport.filename.value="extract." + simplereport.outputformat.value; return true;'    >
   <option value="html" selected> html
   <option value="csv"> csv
   </select>      
   <br/>
   Output to : 
   <select name="outputto">
   <option value="browser" selected> Browser
   <option value="file"> File
   </select>
   File name : 
   <input name="filename" type="text" value="" length="40"/>
   <br/>
   If you wish to limit the number of rows returned, enter limit (e.g. for test) :
   <input name="maxrows" type="text" value="" length="10"/>
   </td>
</tr>
<tr>
   <td colspan="2">
   <p class="footer">
   <input type="submit" value="Run report"/>
   </p>
    </td>
</tr>
</table>

<a href="mailto:alan.mcculloch@agresearch.co.nz;jason.mitchell@agresearch.co.nz?Subject=Bioinformatics Database Request"/> Contact us </a>

</form>
</body>
</html>"""


report_sequenceextracts = """
<!doctype html public "-//w3c//dtd html 4.0 transitional//en"><html>
<head>
<title> Sequence Download Reports </title>
<link rel="stylesheet" type="text/css" href="/css/forms.css">


<script type="text/javascript">

var bgColour = "";
var alreadySubmitted = false;

function checkAll() {   

   if (simplereport.cohortmethod[2].checked) {
      if (simplereport.sequencelistids.value == "") {
         highLight(simplereport.sequencelistids,"You must select one or more searches");
         return false;
      }
      else {
         lowLight(simplereport.sequencelistids);
      }
   }
   else if (simplereport.cohortmethod[0].checked) {
      if (simplereport.candidatesequencelistids.value == "") {
         highLight(simplereport.candidatesequencelistids,"You must select one or more project lists");
         return false;
      }
      else {
         lowLight(simplereport.sequencelistids);
      }
   }
   else if (simplereport.cohortmethod[1].checked) {
      /*
      if (trim(simplereport.sequencenameslistname.value) == "") {
         highLight(simplereport.sequencenameslistname,"You must enter a name for your list");
         return false;
      }
      else {
         lowLight(simplereport.sequencenameslistname);
      }
      */

      strarray = simplereport.sequencenames.value.split("\\r");
      if (strarray.length < 1) {
         highLight(simplereport.sequencenames,"You must enter at least one name");
         return false;
      }
      else {
         lowLight(simplereport.sequencenames);
      }

      if (trim(strarray[0]).length < 5) {
         highLight(simplereport.sequencenames,"You must enter one or more name patterns, each of which is not less than 5 characters");
         return false;
      }
      else {
         lowLight(simplereport.sequencenames);
      }
   }

   // finally , set the submitted flag
   alreadySubmitted = true;


   return true;
}

function highLight(item,message) {
   if(bgColour == "")
      eval("bgColour = item.style.background");
   eval("item.style.background = 'red'");
   window.alert(message);
   item.focus();
} // assume IE

function lowLight(item) {
   //eval("item.style.background = '" + bgColour + "'");
   eval("item.style.background = 'white'");
}
/*
* a function to trim leading and trailing spaces
* from a string
*/
function trim(strval) {
   var start=-1;
   var end=-1;

   if(strval == null)
      return null;
   if(strval == "")
      return strval;

   for(i=0; i < strval.length; i++) {
      if(strval.charAt(i) != " ") {
         if(start == -1)
            start = i;
         end = i;
      }
   }

   if(start == -1)
      return "";
   else
      return strval.substring(start,1 + end);
}


function checkFloatRange(item, low, high) {
   if(isNaN(item.value))
      return false;
   if(high == null && low == null)
      return true;
   else if(high == null && parseFloat(item.value) < low)
      return false;
   else if(low == null && parseFloat(item.value) > high)
      return false;
   else if(parseFloat(item.value) < low || parseFloat(item.value) > high)
      return false;
   else 
      return true;   
}

function setValueByName(fieldName, toValue) {
   document.forms[0].elements[fieldName].value = toValue;
}

// this function can be used to focus on a field given its name
function focusByName(fieldName) {
   document.forms[0].elements[fieldName].focus();
}

// this function wil return the value of a field given its name
function getValueByName(fieldName) {
   return document.forms[0].elements[fieldName].value;
}

// this function wil return a field given its name
function getItemByName(fieldName) {
   return document.forms[0].elements[fieldName];
}

function setReportTitle() {
   if(simplereport.reportmenu.value=="genstatmicroarrayextract1") {
      simplereport.reporttitle.value="AgResearch Microarray Extract";
   }
   return true;
}



</script>





</head>
<body>
<form name="simplereport" onSubmit="return checkAll()" method="post" enctype="multipart/form-data" action="/cgi-bin/report.py" target="simpleReportListing" >
<input type="hidden" name="context" value="report"/>
<table border="true" width=100%%>
<tr> 
   <td colspan="2"> 
      <h1 class="top"> Sequence Downloads </h1>
      This report allows you to download sequence data. You can specify the sequences to download <br/>
      either by selecting a project or search list, or pasting
      in lists of sequence names 
   </td>
<tr>   
   <td class="fieldname"> <p class="fieldname"> Choose a report      </p>
   </td>
   <td class="input">
      <select name="reportmenu">
         <option value="sequencereport1" selected >Download Sequence
      </select><br/>
      Use repeat annotaton to mask sequence : <input name="maskrepeats" type="checkbox" value="True"/> 
      Mask using X (default is lower case) : <input name="use_x" type="checkbox" value="True"/> 
      <br/>
   <input type=checkbox name="hits_in_list" value="True"/> My list includes hit sequences (e.g. NCBI) <font size="-1"> (if you check this the report will also look for query seqs that hit items in your list - this will be slower) </font>
   </td>
</tr>
<tr>   
   <td colspan="2" class="sectionheading" bgcolor="lightgreen"> <p class="fieldname"> Specify which sequences to download </p>
   <i>(In the following fields you may choose one or more items. To choose more than one item hold the control
   key down and click to select. To select a block , select first item then hold down the shift key and select the second item) </i>

   </td>
<tr>
   <td colspan="2" class="input">
      <input type="radio" name="cohortmethod" value="candidatesequencelist" checked/> Project-List option - extract sequences from one or more of the following batches<br>
      %(candidategeneListHTML)s
      <p/>
      <hr/>
      <input type="radio" name="cohortmethod" value="sequencenames"/> Sequence name / keyword list option - paste a list of sequence names to extract into the following field <font size="-1"> <i> (Click the help link for examples of entries you can enter in lists) </i> <font> <br/>
      <textarea rows="5" cols="60" name="sequencenames"></textarea><br/>
      <br/>
      List name : <input name="sequencenameslistname" type="text" size="60"/>
      <br/><font size="-1"> <i>(If you enter a list name , you will be able to select this list subsequently from the items in the search list option below) </font> <br/>
      Match no more than <select name="sequencenamematchlimit">
      <option value="5000"> 5000 </option>
      </select>
      sequences (submit multiple extract requests if you wish to extract more) 
      <p/>
      <hr/>
      <input type="radio" name="cohortmethod" value="sequencelist"/> Search list option - extract all sequences in one or more of the following search result lists<br>
      %(geneListHTML)s
      <p/>
      <font size="-1"> <i> (note - search lists are automatically created and listed here simply by using the main search page </br>      
      Search lists may contain sequences that were hits in blast searches as well as sheep query sequence. Where
      you select a list that contains a hit sequence - for example , a list consisting of a Btau3 contig accession - this report
      will extract all the sheep queries that have hit that sequence)
      <p/>      
   </td>
</tr>
<tr>   
   <td colspan="2" class="sectionheading" bgcolor="lightgreen"> <p class="fieldname"> Specify a filter</p>
   </td>
<tr>
   <td colspan="2" class="input">
   <select name="blastruns">
   <option value=""> (No filters currently available) </option>
   </select>
   </td>
</tr>
<tr> 
   <td class="fieldname" bgcolor="lightgreen"> <p class="fieldname"> Output options
   </td>
   <td  class="input">
   Sort by 
   <select name="orderbyclause">
   <option value=""> No sort
   <option value=" order by ?? "> ??
   </select>
   Output Format<select name="outputformat"  onChange='simplereport.filename.value="extract." + simplereport.outputformat.value; return true;'    >
   <option value="FASTA" selected> FASTA
   <option value="html"> html
   <option value="csv"> csv
   <!-- <option value="gff"> gff  -->
   </select>      
   <br/>
   Output to : 
   <select name="outputto">
   <option value="browser" selected> Browser
   <option value="file"> File
   </select>
   File name : 
   <input name="filename" type="text" value="" length="40"/>
   <br/> 
   If you wish to limit the number of rows returned, enter limit (e.g. for test) :
   <input name="maxrows" type="text" value="" length="10"/>
<tr>
   <td colspan="2">
   <p class="footer">
   <input type="submit" value="Run report"/>
   </p>
    </td>
</tr>
</table>

<a href="mailto:alan.mcculloch@agresearch.co.nz;jason.mitchell@agresearch.co.nz?Subject=Bioinformatics Database Request"/> Contact us </a>

</form>
</body>
</html>"""

report_gbsextracts = """
<!doctype html public "-//w3c//dtd html 4.0 transitional//en"><html>
<head>
<title> GBS Reports </title>
<link rel="stylesheet" type="text/css" href="/css/forms.css">


<script type="text/javascript">

var bgColour = "";
var alreadySubmitted = false;

function checkAll() {   

   if (simplereport.cohortmethod[0].checked) {
      if (simplereport.species.value == "") {
         highLight(simplereport.species,"Please select one or more species or choose a different option");
         return false;
      }
      else {
         lowLight(simplereport.species);
      }
   }
   else if (simplereport.cohortmethod[1].checked) {
      if (trim(simplereport.samples.value) == "") {
         highLight(simplereport.samples,"Please enter one or more samples or choose a diffeent option");
         return false;
      }
      else {
         lowLight(simplereport.samples);
      }
   }
   else if (simplereport.cohortmethod[2].checked) {
      if (simplereport.runs.value == "") {
         highLight(simplereport.runs,"Please select one or more runs or choose a diffeent option");
         return false;
      }
      else {
         lowLight(simplereport.runs);
      }
   }

   // finally , set the submitted flag
   alreadySubmitted = true;


   return true;
}

function highLight(item,message) {
   if(bgColour == "")
      eval("bgColour = item.style.background");
   eval("item.style.background = 'red'");
   window.alert(message);
   item.focus();
} // assume IE

function lowLight(item) {
   //eval("item.style.background = '" + bgColour + "'");
   eval("item.style.background = 'white'");
}
/*
* a function to trim leading and trailing spaces
* from a string
*/
function trim(strval) {
   var start=-1;
   var end=-1;

   if(strval == null)
      return null;
   if(strval == "")
      return strval;

   for(i=0; i < strval.length; i++) {
      if(strval.charAt(i) != " ") {
         if(start == -1)
            start = i;
         end = i;
      }
   }

   if(start == -1)
      return "";
   else
      return strval.substring(start,1 + end);
}


function checkFloatRange(item, low, high) {
   if(isNaN(item.value))
      return false;
   if(high == null && low == null)
      return true;
   else if(high == null && parseFloat(item.value) < low)
      return false;
   else if(low == null && parseFloat(item.value) > high)
      return false;
   else if(parseFloat(item.value) < low || parseFloat(item.value) > high)
      return false;
   else 
      return true;   
}

function setValueByName(fieldName, toValue) {
   document.forms[0].elements[fieldName].value = toValue;
}

// this function can be used to focus on a field given its name
function focusByName(fieldName) {
   document.forms[0].elements[fieldName].focus();
}

// this function wil return the value of a field given its name
function getValueByName(fieldName) {
   return document.forms[0].elements[fieldName].value;
}

// this function wil return a field given its name
function getItemByName(fieldName) {
   return document.forms[0].elements[fieldName];
}

function setReportTitle() {
   if(simplereport.reportmenu.value=="genstatmicroarrayextract1") {
      simplereport.reporttitle.value="AgResearch Microarray Extract";
   }
   return true;
}



</script>


</head>
<body>
<form name="simplereport" onSubmit="return checkAll()" method="post" enctype="multipart/form-data" action="/cgi-bin/report.py" target="simpleReportListing" >
<input type="hidden" name="context" value="report"/>
<table border="true" width=100%%>
<tr> 
   <td colspan="2"> 
      <h1 class="top"> GBS Downloads </h1>
   </td>
<tr>   
   <td class="fieldname"> <p class="fieldname"> Choose a report      </p>
   </td>
   <td class="input">
      <select name="reportmenu">
         <option value="gbsreport1" selected >Download GBS Yield Stats
         <option value="unblind_report">Unblind/Blind samples 
         <option value="gbsreport2" >Download Keyfile and any Yield Stats available
      </select>
  </td>
</tr>
<tr>   
   <td colspan="2" class="sectionheading" bgcolor="lightgreen"> <p class="fieldname"> Specify which samples to download </p>
   <i>(In the following fields you may choose one or more items. To choose more than one item hold the control
   key down and click to select. To select a block , select first item then hold down the shift key and select the second item) </i>

   </td>
<tr>
   <td colspan="2" class="input">
      <input type="radio" name="cohortmethod" value="speciesnames" checked/> Species names option - select one or more of the following species namerd<br>
      %(speciesListHTML)s
      <p/>
      <hr/>
      <input type="radio" name="cohortmethod" value="samplenames"/> Sample names option - paste a list of one or more sample names into the following field <font size="-1"> <i> (Click the help link for examples of entries you can enter in lists) </i> <font> <br/>
      <textarea rows="5" cols="60" name="samples"></textarea><br/>
      <p/>
      <hr/>
      <input type="radio" name="cohortmethod" value="runnames"/> Run names option - select one or more of the following runs<br>
      %(runListHTML)s
      <br/>
      <p/>      
   </td>
</tr>
<tr>   
   <td colspan="2" class="sectionheading" bgcolor="lightgreen"> <p class="fieldname"> Specify a filter</p>
   </td>
<tr>
   <td colspan="2" class="input">
   List samples where 
   <select name="filter_field">
   <option value=""/> 
   <option value="callrate"> Call Rate</option>
   <option value="sampdepth"> Sample Depth  </option>
   <option value="tag_count"> Tag Count </option>
   <option value="read_count"> Read Count </option>
   </select>
   is 
   <select name="filter_relation">
   <option value=""> </option>   
   <option value="<"> Less than </option>
   <option value=">="> Greater than or equal  </option>
   </select>
   than
   <input name="filter_bound" type="text" value="" length="20"/>   
   </td> 
</tr>
<tr> 
   <td class="fieldname" bgcolor="lightgreen"> <p class="fieldname"> Output options
   </td>
   <td  class="input">
   Sort by 
   <select name="orderbyclause">
   <option value=""> No sort
   <option value=" order by ?? "> ??
   </select>
   Output Format<select name="outputformat"  onChange='simplereport.filename.value="extract." + simplereport.outputformat.value; return true;'    >
   <option value="csv"> csv
   <option value="txt"> tab delimited
   </select>      
   <br/>
   Output to : 
   <select name="outputto">
   <option value="browser" selected> Browser
   <option value="file"> File
   </select>
   File name : 
   <input name="filename" type="text" value="" length="40"/>
   <br/> 
   If you wish to limit the number of rows returned, enter limit (e.g. for test) :
   <input name="maxrows" type="text" value="" length="10"/>
<tr>
   <td colspan="2">
   <p class="footer">
   <input type="submit" value="Run report"/>
   </p>
    </td>
</tr>
</table>

<a href="mailto:alan.mcculloch@agresearch.co.nz?Subject=GBS Database Request"/> Contact us </a>

</form>
</body>
</html>"""



""" --------- module methods ------------"""
def getReportHeader(title="", heading="", fieldNames="", outputformat = 'html',needContentType=True,onlyContentType=False):
    agresearchpagemodulelogger.info("formatting report for fields %s outputformat %s"%(str(fieldNames),outputformat))
    page = ""
    if needContentType or onlyContentType:
       page = "Content-Type: text/html\n\n" + htmlModule.HTMLdoctype
    if onlyContentType:
       return page
    if outputformat == 'html':
        page += '<html>\n<header>\n<title>\n' + title + '</title>\n' + htmlModule.getStyle() + '</header>\n<body>\n'
        #page += '<table with=90% border="1">\n<tr>\n<td><h2 halign="center">'+heading+'</h2><p>'
        page += '<table with=90% border="1">\n<tr>\n<td><p>'
        page += '<tr> <td colspan=%s> %s </td></tr>'%(len(fieldNames) , heading)
        page += '<tr>' + reduce(lambda x,y: x + '<td><b>' + str(y) + '</b></td>' , fieldNames,'') + '</tr>'
    elif outputformat == 'csv':
        page += heading + "\n"
        page += reduce(lambda x,y: x + '"' + str(y) + '",' , fieldNames,'')
        page = re.sub(',$','',page)
    elif outputformat == 'dat':
        page += heading + "\n"
        page += reduce(lambda x,y: x + str(y) + '\t' , fieldNames,'')
        page = re.sub(',\t$','',page)        
    else:
        page += heading
        
    return page


#def getDownloadHeader(fileName):
#    page =\
#"""Content-Type: text/plain; name="%s"
#Content-Description: %s
#Content-Disposition: attachment; filename="%s"
#"""%(fileName,fileName,fileName)    
#    return page


def getDownloadHeader(fileName="",title="", heading="",fieldNames="", outputformat = 'html',needContentType=True,onlyContentType=False):
    page = ""
    if needContentType or onlyContentType:
       page =\
"""Content-Type: text/plain; name="%s"
Content-Description: %s
Content-Disposition: attachment; filename="%s"
"""%(fileName,fileName,fileName)
    #page += "Content-Type: text/html\n\n" + htmlModule.HTMLdoctype
       page += "Content-Type: text/html\n\n"
   
    if onlyContentType:
       return page

    if outputformat == 'html':    
        page += '<html>\n<header>\n<title>\n' + title + '</title>\n' +  htmlModule.getStyle() + ' </header>\n<body>\n'
        ##page += '<table with=90% border="1">\n<tr>\n<td><h2 halign="center">'+heading+'</h2><p>'
        page += '<table with=90% border="1">\n<tr>\n<td><p>'
        page += '<tr> <td colspan=%s> %s </td></tr>'%(len(fieldNames) , heading)
        page += '<tr>' + reduce(lambda x,y: x + '<td><b>' + str(y) + '</b></td>' , fieldNames,'') + '</tr>'
    elif outputformat == 'csv':
        page += reduce(lambda x,y: x + '"' + str(y) + '",' , fieldNames,'')
        page = re.sub(',$','',page)
    elif outputformat in ('dat','txt'):
        page += reduce(lambda x,y: x + str(y) + '\t' , fieldNames,'')
        page = re.sub('\t$','',page)                

    #page = "Content-Type: application/x-download\n\n"
    #page += "Content-Disposition: attachment; filename=test.dl;\n\n"
    
    return page



def getReportFooter(rowCount,message=''):
    page = '<p><p>\n'
    page += '<p></td>\n</tr>\n</table>\n'
    if rowCount != None:
        page += '<p/><p/>%s Rows Returned<p/>'%rowCount
    page += '<b>%s</b>'%message    
    page += '</body>\n</html>\n'
    return page

def errorPage(message):
    print htmlModule.pageWrap("Error",message,cssLink=brdfCSSLink)

def getMetaRedirect(address,name,context="report"):
    # if the address has leading and trailing " characters, remove these
    address = re.sub("\"$","",re.sub("^\"","",address))    

    page = "Content-Type: text/html\n\n" + htmlModule.HTMLdoctype
    if context == "report":
       page += """
 <html>
<head>
<title>AgResearch Report Redirect</title>
<meta http-equiv="refresh" content="5; url=%s">
</head>

<body bgcolor="#D2CBB0">

<p align="center">
<br>
You are being redirected to your report output at %s<br>
If you are not redirected, please click on the link below:<br>
<b>
<a href="%s">Report output :  %s </a>
</body>
</html>"""%(address,name,address,name)
    elif context == "join":
       page += """
<html>
<head>
<title>AgResearch Retrieve Redirect</title>
<meta http-equiv="refresh" content="0; url=%s">
</head>

<body>
<a href="%s">(Retrieving from  :  %s) </a>
</body>
</html>"""%(address,address,address)


    return page


def getManualRedirect(address,name,context="report"):
    # if the address has leading and trailing " characters, remove these
    address = re.sub("\"$","",re.sub("^\"","",address))

    page = "Content-Type: text/html\n\n" + htmlModule.HTMLdoctype
    if context == "report":
       page += """
 <html>
<head>
<title>AgResearch Report Redirect</title>
</head>

<body bgcolor="#D2CBB0">

<p align="center">
<br>
You are being redirected to your report output at %s<br>
If you are not redirected, please click on the link below:<br>
<b>
<a href="%s">Report output :  %s </a>
</body>
</html>"""%(name,address,name)
    elif context == "bfile":
       page += """
<html>
<head>
<title>AgResearch Retrieve Redirect</title>
</head>

<body>
The file you have requested is available from the link below.
<p/>
To access your file you may either
<ul>
   <li> Click the link below to open the file in the program associated with the file type
   <li> Right click the link and choose "save as" , to save the file (e.g. if you do not have
        a program associated with this type of file)
</ul>
<a href="%s">%s</a>
</body>
</html>"""%(address,address)


    return page

    
    


""" --------- classes -------------------"""
######################################################################
#
# base class for agresearch pages
#
######################################################################
class page (object) :
    def __init__(self):
        object.__init__(self)

        self.pageState = {
            'ERROR' : 0,
            'MESSAGE' : ''}        

        
######################################################################
#
# This page calls the database search engine and returns
# a page of links to search result lists
#
######################################################################
class searchResultPage ( page ):
    """ class for geneSummaryPage  """
    def __init__(self, argDict):
        page.__init__(self)
        self.argDict = argDict
        self.metaSearchTypes = {
            'NCBI' : 'http://www.ncbi.nlm.nih.gov/gquery/gquery.fcgi?term=%s',
            'AgResearch Medicago Genome Browser' : 'http://gbrowse.agresearch.co.nz/cgi-bin/gbrowse/medicago1stJan2006/?name=%s'
        }
            
                 
        if not self.argDict.has_key('queryString'):
            self.pageState.update({'ERROR' : 1, 'MESSAGE' : "please specify a query - fields received were <br/> " + reduce(lambda x,y:x+y ,[key + '=' + str(value) + '<br/>' for key,value in self.argDict.items()]) })
            errorPage(self.pageState['MESSAGE'])
        else:
            if self.argDict['queryString'] != None:
                self.argDict.update( {
                    'queryString' : self.argDict['queryString'].strip()
                })
            self.doSearch()

       

    def doSearch(self):

        # set up database connection
        #print "connecting using " + databaseModule.host + " , " + databaseModule.database
        
       	connection=databaseModule.getConnection()        
        searchCursor=connection.cursor()


        # if we are to search everything then we execute a series of searches of each type of object. Each
        # Search returns an obList object - these are put into a dictionary
        self.resultsDict={}

        self.searchTypes = {
            'Genetic Tables' : 'geneticob',
            'Microarray Spots' : 'microarrayspotfact',
            'Past Searches' : 'oblist',
            'Data Files Submitted' : 'datasourceob',
            'Data Files Imported' : 'datasourceob',            
            'DataSource Lists' : 'datasourcelist',            
            'Sample Lists' : 'biosamplelist',            
            'Work Flows' : 'workflowob',
            'Work Flow Stages' : 'workflowstageob',
            'Ontologies' : 'ontologyob',
            'Ontology Terms' : 'ontologytermfact',
            'Microarray Experiments' : 'geneexpressionstudy',
            'Genotype Experiments' : 'genotypeStudy',
            'Genetic Tests' : 'geneticTestFact',
            'Genetic Test Runs' : 'genotypeObservation',
            'BioSequences' : 'biosequenceob',
            'BioSubjects' : 'biosubjectob',
            'BioSamples' : 'biosampleob',
            'All Lab Resources' : 'labresourceob' ,
            'BioSampling' : 'biosamplingfunction',
            'Comments' : 'commentOb',
            'External Links' : 'uriOb',
            'Phenotype Studies' : 'phenotypeStudy',
            'Project Lists' : 'oblist',
            'Microarray Series' : 'oblist',
            'Protocols' : 'bioprotocolob',
            'Microarrays' : 'labresourceob',
            'Databases' : 'bioDatabaseOb',
            'Database Searches' : 'databaseSearchStudy',
            'Libraries' : 'biolibraryob',
            'Library Sequencing' : 'librarysequencingfunction' ,
            'Analysis Procedures' : 'analysisprocedureob',
            'Contributed Data Tables' : 'datasourceob'}

        siteSearchTypes = {
            'AgResearch Cattle Sequences' : 'biosequenceob'
        }

        # some searches are redirected to external sites
        if self.argDict['obTypeName'] in self.metaSearchTypes.keys():
            # save the search as a URI ob
            uri = uriOb()
            uri.initNew(connection)
            uri.databaseFields.update(
                {
                    'createdby' : self.argDict['REMOTE_USER'],
                    'uristring' : self.metaSearchTypes[self.argDict['obTypeName']]%self.argDict['queryString'],
                    'xreflsid' : self.metaSearchTypes[self.argDict['obTypeName']]%self.argDict['queryString'],
                    'visibility' : 'public',
                    'uricomment' : 'external search of %s for %s'%(self.argDict['obTypeName'],self.argDict['queryString'])
                }
            )
            uri.insertDatabase(connection)
            connection.close()            
            return

        for obTypeName in self.searchTypes.keys():
            # exclude past searches (from 8/2006)
            if obTypeName == 'Past Searches' and self.argDict['obTypeName'] == 'All Tables':
                continue

            # set the max list contents depending on type 
            if 'maxhits' not in self.argDict:
                self.argDict['maxhits'] = 1000
            if obTypeName == 'BioSequences':
                self.argDict['maxhits'] = 20000


            if self.argDict['obTypeName'] == 'All Tables' or self.argDict['obTypeName'] == obTypeName or \
                (self.argDict['obTypeName'] == 'Past Searches' and obTypeName == 'External Links'):
                self.argDict.update({'typeName' : obTypeName})
                engineQuery="select getSearchResultList(%(queryString)s,'SYSTEM',%(maxhits)s,%(typeName)s,0)"
                agresearchpagemodulelogger.info('executing engine query %s'%(engineQuery%self.argDict))
                searchCursor.execute(engineQuery,self.argDict)
                obFieldValues = searchCursor.fetchone()
                if searchCursor.rowcount != 1:
                    self.pageState.update({'ERROR' : 1, 'MESSAGE' : "no query result"})
                    errorPage(self.pageState['MESSAGE'])                
                else:
                    connection.commit()     
                    resultList=obList()
                    typeMetadata = getObTypeMetadata(connection,self.searchTypes[obTypeName])
                    resultList.listAboutLink = imageurl + typeMetadata['displayurl']
                    agresearchpagemodulelogger.info('initialising list from id %s'%obFieldValues[0])
                    resultList.initFromDatabase(obFieldValues[0],connection)
                    agresearchpagemodulelogger.info('list has %s'%str(resultList.databaseFields['listitems']))
                    self.resultsDict[obTypeName] = resultList

        for obTypeName in siteSearchTypes.keys():

            # set the max list contents depending on type
            if self.argDict['maxhits'] < 20000 and obTypeName == 'AgResearch Cattle Sequences':
                self.argDict['maxhits'] = 20000

            if self.argDict['obTypeName'] == obTypeName: 
                agresearchpagemodulelogger.info('invoking site search engine for %s'%obTypeName)
                self.argDict.update({'typeName' : obTypeName})
                engineQuery="select getSiteSearchResultList(%(queryString)s,'SYSTEM',1000,%(typeName)s,0)"
                agresearchpagemodulelogger.info('executing site engine query %s'%(engineQuery%self.argDict))
                searchCursor.execute(engineQuery,self.argDict)
                obFieldValues = searchCursor.fetchone()
                if searchCursor.rowcount != 1:
                    self.pageState.update({'ERROR' : 1, 'MESSAGE' : "no query result"})
                    errorPage(self.pageState['MESSAGE'])
                else:
                    connection.commit()
                    resultList=obList()
                    typeMetadata = getObTypeMetadata(connection,siteSearchTypes[obTypeName])
                    resultList.listAboutLink = imageurl + typeMetadata['displayurl']
                    agresearchpagemodulelogger.info('initialising list from id %s'%obFieldValues[0])
                    resultList.initFromDatabase(obFieldValues[0],connection)
                    agresearchpagemodulelogger.info('list has %s'%str(resultList.databaseFields['listitems']))
                    self.resultsDict[obTypeName] = resultList

            
        if not self.argDict.has_key('typeName'):
            self.pageState.update({'ERROR' : 1, 'MESSAGE' : "unsupported object for query (" + self.argDict['obTypeName'] + ")"})
            errorPage(self.pageState['MESSAGE'])                   

        searchCursor.close()
        connection.close()
        
    def asHTML(self):
        # we ask each list object to display itself. The lists of results are stored in self.resultsDict
        # 
        # Before doing this we need to update the list with bases for callback URL's that it will
        # use in the display.
        #
        # first enhance each result set with a base URL which can be used to retrieve the object.
        # Each result is an obList that contains a list of tuples called databaseFields.listitems. Each
        # tuple is (obid,listorder,xreflsid), and we expand this to be (obid,listorder,xreflsid,url)

        if self.argDict['obTypeName'] in self.metaSearchTypes.keys():
            return getMetaRedirect(self.metaSearchTypes[self.argDict['obTypeName']]%self.argDict['queryString'],self.argDict['obTypeName']) 
                
        for list in self.resultsDict.values():
            agresearchpagemodulelogger.info(list.databaseFields['listitems'])
            list.databaseFields.update({'listitems' : [tuple + (objectDumpURL%(str(tuple[0]),self.argDict['viewName']),) for tuple in list.databaseFields['listitems']] })

        # next add a base URL for retrieving the next chunk, and an item separator
        for list in self.resultsDict.values():
            list.listChunkLink = listChunkLink

        # customise some lists by splitting them into sub-lists - for example split sequences
        # into NCBI and other sequences, and also by species. Currently this is done using the
        # LSID of the sequence, however various more complicated rules could be used.

        # convenience function for appending a list in a dictionary
        def inspendDict( mydict, key, value ) : 
           if key in mydict:
              mydict[key].append(value)
           else:
              mydict[key] = [value]

        for obTypeName in self.resultsDict.keys():
            if obTypeName in ("Data Files Submitted" , "Data Files Imported"):


                # first we shall see if a list of lists already exists - if so just retrieve it. If not then we will need to
                # check whether it needs to be constructed. Note that it may not exist for a valid reason - i.e.
                # there is only one subclass of sequence object
                metaxreflsid = "Meta List for search of %s for %s"%(obTypeName, self.argDict['queryString'])
                metaList=obList()
                connection=databaseModule.getConnection()
                try:
                    metaList.initFromDatabase(metaxreflsid,connection)

                    # a couple of additional initialisation steps are needed which are not done
                    # by the object itself (lists do not know what sort of thing they contain !)
                    typeMetadata = getObTypeMetadata(connection,self.searchTypes[obTypeName])
                    metaList.listAboutLink = imageurl + typeMetadata['displayurl']
                    
                except brdfException:
                    if metaList.obState['ERROR'] == 1: # not found
                        agresearchpagemodulelogger.info('refining search results....')
                        # we examine all items in the list and assign each to a dictionary. Each item is
                        # represented by a tuple containing
                        # l.ob,
                        # l.listorder,
                        # l.obxreflsid,
                        # l.membershipcomment
                        # ....other stuff
                        # re-init the list to get all items in it.

                        classDict = {}
                        for membertuple in self.resultsDict[obTypeName].databaseFields['alllistitems']:
                            #agresearchpagemodulelogger.info("checking %s"%str(membertuple))
                            if re.search("\.cdf$",membertuple[2],re.IGNORECASE) != None:
                                inspendDict(classDict, "Affymetirx CDF (Chip definition) Files", membertuple)
                            elif re.search("\.cel$",membertuple[2],re.IGNORECASE) != None:
                                inspendDict(classDict, "Affymetrix CEL files", membertuple)
                            elif re.search("\.csv$",membertuple[2],re.IGNORECASE) != None:
                                inspendDict(classDict, "csv files", membertuple)
                            elif re.search("\.pdf$",membertuple[2],re.IGNORECASE) != None:
                                inspendDict(classDict, "pdf files", membertuple)
                            elif re.search("\.ppt$",membertuple[2],re.IGNORECASE) != None:
                                inspendDict(classDict, "ppt (powerpoint) files", membertuple)
                            elif re.search("\.R$",membertuple[2],re.IGNORECASE) != None:
                                inspendDict(classDict, "R script files", membertuple)
                            elif re.search("\.Rdata$",membertuple[2],re.IGNORECASE) != None:
                                inspendDict(classDict, "Rdata files ", membertuple)
                            elif re.search("\.Rout$",membertuple[2],re.IGNORECASE) != None:
                                inspendDict(classDict, "Rout files", membertuple)
                            elif re.search("\.txt$",membertuple[2],re.IGNORECASE) != None:
                                inspendDict(classDict, "txt files", membertuple)
                            elif re.search("\.xls$",membertuple[2],re.IGNORECASE) != None:
                                inspendDict(classDict, "xls (Excel) files", membertuple)
                            elif re.search("\.gpr$",membertuple[2],re.IGNORECASE) != None:
                                inspendDict(classDict, "gpr (Genepix GPR) files", membertuple)
                            elif re.search("\.fa$",membertuple[2],re.IGNORECASE) != None:
                                inspendDict(classDict, "fa (fasta) files", membertuple)
                            elif re.search("\.fasta$",membertuple[2],re.IGNORECASE) != None:
                                inspendDict(classDict, "fasta files", membertuple)
                            elif re.search("\.seq$",membertuple[2],re.IGNORECASE) != None:
                                inspendDict(classDict, "seq (fasta) files", membertuple)
                            elif re.search("\.gal$",membertuple[2],re.IGNORECASE) != None:
                                inspendDict(classDict, "gal (microarray GAL) files", membertuple)
                            elif re.search("\.gff$",membertuple[2],re.IGNORECASE) != None:
                                inspendDict(classDict, "gff (features) files", membertuple)
                            else:
                                inspendDict(classDict, "Other", membertuple)

                        agresearchpagemodulelogger.info("refined classes result : %s"%str(classDict))

                        # if the class dictionary contains just one item then do nothing -
                        # return list as is. If it contains more than one item then
                        # we replace the current list with a list-of-lists.
                        if len(classDict) > 1:

                            # we need a list-of-lists 
                            typeMetadata = getObTypeMetadata(connection,self.searchTypes[obTypeName])
                            metaList.listAboutLink = imageurl + typeMetadata['displayurl']
                            agresearchpagemodulelogger.info('initialising meta-list')
                            metaList.initNew(connection)
                            metaList.databaseFields.update ({
                                    'xreflsid' : "Meta List for search of %s for %s"%(obTypeName, self.argDict['queryString']),
                                    'listname' : "Meta List for search of %s for %s"%(obTypeName, self.argDict['queryString']),
                                    'listdefinition' : "Meta List for search of %s for %s"%(obTypeName, self.argDict['queryString']),
                                    'listitems' : [],
                                    'alllistitems' : [],
                                    'listtype' : 'META LIST'
                            })
                            metaList.insertDatabase(connection)                    
                            agresearchpagemodulelogger.info("metaList initialised as : "+str(metaList.databaseFields))
                            
                            
                            # make new sublists for each class of sequence - these will be members of the main list
                            for classItem in classDict.keys():
                                classList = obList()
                                classList.initNew(connection)
                                classList.databaseFields.update ({
                                    'xreflsid' : "%s"%(classItem),
                                    'listname' : "%s"%(classItem),
                                    'listdefinition' : "%s : %s"%(self.argDict['queryString'], classItem),
                                    'listtype' : 'DATASOURCE_LIST'
                                })
                                classList.insertDatabase(connection)
                                agresearchpagemodulelogger.info("adding members to class list %(xreflsid)s"%classList.databaseFields)
                                classList.databaseFields['listitems'] = classDict[classItem] 
                                classList.databaseFields['alllistitems'] = classDict[classItem] 
                                classList.saveMembershipList(connection, checkExisting = False)

                                # add the class list to the metalist
                                metaList.addListMember(classList,classItem,connection,voptype=None,checkExisting = False)


                    else:
                        # some other error - re-raise
                        raise brdfException, metaList.obState['MESSAGE']


                connection.close()
                # if we have a valid meta list , then complete initialisation and
                # make it the top level list. 
                if metaList.obState['ERROR'] == 0:
                    # update the list with fetch URL's for each member. In this case the members are lists and they need
                    # to open themselves in briefsearchsummary mode - the URL looks like 
                    # http://agbrdf.agresearch.co.nz/cgi-bin/fetch.py?obid=54083355&context=briefsearchsummarypage&bookmark=162375&target=ob&childview=default&page=1
                    # the template being 
                    # listChunkLink="/%s/"%agbrdfConf.CGIPATH + 'fetch.py?obid=%s&context=briefsearchsummarypage&bookmark=%s&target=ob&childview=%s&page=%s'
                    #metaList.databaseFields.update({'listitems' : [tuple + (objectDumpURL%(str(tuple[0]),'briefsearchsummarypage'),) for tuple in metaList.databaseFields['listitems']] })        
                    metaList.databaseFields.update({'listitems' : [tuple + (listChunkLink%(str(tuple[0]),1,'default',0),) for tuple in metaList.databaseFields['listitems']] })        
                    agresearchpagemodulelogger.info("metaList contains : "+str(metaList.databaseFields))
                    self.resultsDict[obTypeName] = metaList ############### UNCOMMENT THIS TO MAKE IT WORK
                    

                
                
            if obTypeName == "BioSequences":
            #if obTypeName in  ["BioSequences", "AgResearch Cattle Sequences"]:
            #    if obTypeName == "AgResearch Cattle Sequences":
            #        obTypeName = "BioSequences"


                # first we shall see if a list of lists already exists - if so just retrieve it. If not then we will need to
                # check whether it needs to be constructed. Note that it may not exist for a valid reason - i.e.
                # there is only one subclass of sequence object
                metaxreflsid = "Meta List for search of %s for %s"%(obTypeName, self.argDict['queryString'])
                metaList=obList()
                connection=databaseModule.getConnection()
                try:
                    metaList.initFromDatabase(metaxreflsid,connection)

                    # a couple of additional initialisation steps are needed which are not done
                    # by the object itself (lists do not know what sort of thing they contain !)
                    typeMetadata = getObTypeMetadata(connection,self.searchTypes[obTypeName])
                    metaList.listAboutLink = imageurl + typeMetadata['displayurl']
                    
                except brdfException:
                    if metaList.obState['ERROR'] == 1: # not found
                        agresearchpagemodulelogger.info('refining search results....')
                        # we examine all items in the list and assign each to a dictionary. Each item is
                        # represented by a tuple containing
                        # l.ob,
                        # l.listorder,
                        # l.obxreflsid,
                        # l.membershipcomment
                        # ....other stuff
                        # re-init the list to get all items in it.

                        classDict = {}
                        for membertuple in self.resultsDict[obTypeName].databaseFields['alllistitems']:
                            #agresearchpagemodulelogger.info("checking %s"%str(membertuple))
                            if re.search("^CS34\.",membertuple[2]) != None:
                                inspendDict(classDict, "CS34 Cattle Contigs", membertuple)
                            elif re.search("^CS20\.",membertuple[2]) != None:
                                inspendDict(classDict, "CS20 Cattle Contigs", membertuple)
                            elif re.search("^CS14\.",membertuple[2]) != None:
                                inspendDict(classDict, "CS14 Cattle Contigs", membertuple)
                            elif re.search("^AgResearch\.Bovine\.",membertuple[2]) != None:
                                inspendDict(classDict, "AgResearch Cattle ESTs", membertuple)
                            elif re.search("^Btau4\.GLEAN\.DNA",membertuple[2]) != None:
                                inspendDict(classDict, "Btau4 GLEAN Gene models", membertuple)
                            elif re.search("^CS19\.",membertuple[2]) != None:
                                inspendDict(classDict, "CS19 Deer Contigs", membertuple)
                            elif re.search("^CS37\.",membertuple[2]) != None:
                                inspendDict(classDict, "CS37 Ryegrass Contigs", membertuple)
                            elif re.search("^CS35\.",membertuple[2]) != None:
                                inspendDict(classDict, "CS35 White Clover Contigs", membertuple)
                            elif re.search("^CS39\.",membertuple[2]) != None:
                                inspendDict(classDict, "CS39 Sheep Contigs", membertuple)
                            elif re.search("^AgResearch\.Ovine\.",membertuple[2]) != None:
                                inspendDict(classDict, "AgResearch Sheep ESTs", membertuple)
                            elif re.search("^Hort\.",membertuple[2]) != None:
                                inspendDict(classDict, "HortResearch Sequences", membertuple)
                            elif re.search("^UniProt\.",membertuple[2]) != None:
                                inspendDict(classDict, "UniProt Sequences", membertuple)
                            elif re.search("^Interpro\.",membertuple[2]) != None:
                                inspendDict(classDict, "Interpro Accessions", membertuple)
                            elif re.search("^NCBI\.",membertuple[2]) != None:
                                inspendDict(classDict, "NCBI Sequences", membertuple)
                            elif re.search("^DFCI\.OsGI\.",membertuple[2]) != None:
                                inspendDict(classDict, "DFCI Rice Gene index seqs", membertuple)
                            elif re.search("^DFCI\.TaGI\.",membertuple[2]) != None:
                                inspendDict(classDict, "DFCI Wheat Gene index seqs", membertuple)
                            elif re.search("^DFCI\.",membertuple[2]) != None:
                                inspendDict(classDict, "DFCI Cattle Gene index seqs", membertuple)
                            elif re.search("^Affymetrix\.target\:Bovine",membertuple[2]) != None:
                                inspendDict(classDict, "Affymetrix Bovine Array Target sequence", membertuple)
                            elif re.search("^Affymetrix\.consensus\:Bovine",membertuple[2]) != None:
                                inspendDict(classDict, "Affymetrix Bovine Array Consensus sequence", membertuple)
                            elif re.search("^AFT.*_at$",membertuple[2]) != None:
                                inspendDict(classDict, "AFT Affy array target sequence", membertuple)
                            elif re.search("^CS37.*_at\.\d+$",membertuple[2]) != None:
                                inspendDict(classDict, "AFT Affy array probe oligo sequence", membertuple)
                            elif re.search("^AFT.",membertuple[2]) != None:
                                inspendDict(classDict, "Other AFT Sequences", membertuple)
                            else:
                                # 11/2011 parse out the leading dotted token and classify by that
                                #agresearchpagemodulelogger.info("searching %s using %s"%(membertuple[2], "^(\S+)\."))
                                mymatch = re.search("^([^\.]+)\.", membertuple[2])
                                if mymatch != None:
                                    category = mymatch.groups()[0]
                                    inspendDict(classDict, category , membertuple)
                                else:
                                    inspendDict(classDict, "Other", membertuple)

                        agresearchpagemodulelogger.info("refined classes result : %s"%str(classDict))

                        # if the class dictionary contains just one item then do nothing -
                        # return list as is. If it contains more than one item then
                        # we replace the current list with a list-of-lists.
                        if len(classDict) > 1:

                            # we need a list-of-lists 
                            typeMetadata = getObTypeMetadata(connection,self.searchTypes[obTypeName])
                            metaList.listAboutLink = imageurl + typeMetadata['displayurl']
                            agresearchpagemodulelogger.info('initialising meta-list')
                            metaList.initNew(connection)
                            metaList.databaseFields.update ({
                                    'xreflsid' : "Meta List for search of %s for %s"%(obTypeName, self.argDict['queryString']),
                                    'listname' : "Meta List for search of %s for %s"%(obTypeName, self.argDict['queryString']),
                                    'listdefinition' : "Meta List for search of %s for %s"%(obTypeName, self.argDict['queryString']),
                                    'listitems' : [],
                                    'alllistitems' : [],
                                    'listtype' : 'META LIST'
                            })
                            metaList.insertDatabase(connection)                    
                            agresearchpagemodulelogger.info("metaList initialised as : "+str(metaList.databaseFields))
                            
                            
                            # make new sublists for each class of sequence - these will be members of the main list
                            for classItem in classDict.keys():
                                classList = obList()
                                classList.initNew(connection)
                                classList.databaseFields.update ({
                                    'xreflsid' : "%s"%(classItem),
                                    'listname' : "%s"%(classItem),
                                    'listdefinition' : "%s : %s"%(self.argDict['queryString'], classItem),
                                    'listtype' : 'BIOSEQUENCE_LIST'
                                })
                                classList.insertDatabase(connection)
                                agresearchpagemodulelogger.info("adding members to class list %(xreflsid)s"%classList.databaseFields)
                                classList.databaseFields['listitems'] = classDict[classItem] 
                                classList.databaseFields['alllistitems'] = classDict[classItem] 
                                classList.saveMembershipList(connection, checkExisting = False)

                                # add the class list to the metalist
                                metaList.addListMember(classList,classItem,connection,voptype=None,checkExisting = False)


                    else:
                        # some other error - re-raise
                        raise brdfException, metaList.obState['MESSAGE']


                connection.close()
                # if we have a valid meta list , then complete initialisation and
                # make it the top level list. 
                if metaList.obState['ERROR'] == 0:
                    # update the list with fetch URL's for each member. In this case the members are lists and they need
                    # to open themselves in briefsearchsummary mode - the URL looks like 
                    # http://agbrdf.agresearch.co.nz/cgi-bin/fetch.py?obid=54083355&context=briefsearchsummarypage&bookmark=162375&target=ob&childview=default&page=1
                    # the template being 
                    # listChunkLink="/%s/"%agbrdfConf.CGIPATH + 'fetch.py?obid=%s&context=briefsearchsummarypage&bookmark=%s&target=ob&childview=%s&page=%s'
                    #metaList.databaseFields.update({'listitems' : [tuple + (objectDumpURL%(str(tuple[0]),'briefsearchsummarypage'),) for tuple in metaList.databaseFields['listitems']] })        
                    metaList.databaseFields.update({'listitems' : [tuple + (listChunkLink%(str(tuple[0]),1,'default',0),) for tuple in metaList.databaseFields['listitems']] })        
                    agresearchpagemodulelogger.info("metaList contains : "+str(metaList.databaseFields))
                    self.resultsDict[obTypeName] = metaList ############### UNCOMMENT THIS TO MAKE IT WORK
                    


        # if there is only one list with one object , then just open it
        if len(self.resultsDict.values()) == 1:
            if len(list.databaseFields['listitems']) == 1:
                fetchob = list.databaseFields['listitems'][0][0]
                self.argDict.update({
                    'obid' : fetchob,
                    'context' : self.argDict['viewName'],
                    'target': 'ob'                    
                })
                obpage = fetchPage(self.argDict)
                try:
                    obpage.doFetch()
                    print obpage.asHTML()
                    return
                except brdfException, msg:
                    obpage.pageState.update({'ERROR' : 1, 'MESSAGE' : str(msg) })
                    errorPage(str(msg))
                    return
        
            
        if self.pageState['ERROR'] == 0:
            results = self.resultsDict.items()
            content = '<table border=yes width=90%>\n'
            for resultType,resultList in results:
                pagecount = int(.9999 + resultList.databaseFields['currentmembership']*1.0/resultList.chunkSize*1.0)
                content +=  resultList.asHTMLTableRow(title="%s (page 1 of %d)"%(resultType,pagecount),width='90%',context='briefsearchsummary', view=self.argDict['viewName'])
            content += '</table>'

            return  htmlModule.pageWrap("Result of search of : " + self.argDict['obTypeName'] + " for <b>" + self.argDict['queryString'] + "</b>",content,cssLink=brdfCSSLink)
        else:
            return ""



######################################################################
#
# This page fetches a single object from the database - this is the response to
# a URL "get" along the lines of
# http://localhost/cgi-bin/agresearch/fetch.py?context=dump&obid=2406
#
######################################################################

class fetchPage ( page ):
    """ class for fetchPage  """
    def __init__(self, argDict):
        page.__init__(self)
        self.argDict = argDict
        agresearchpagemodulelogger.info("fetchPage : %s",str(argDict))
        if not self.argDict.has_key('obid'):
            self.pageState.update({'ERROR' : 1, 'MESSAGE' : "please specify a query - fields received were <br/> " + reduce(lambda x,y:x+y ,[key + '=' + str(value) + '<br/>' for key,value in self.argDict.items()]) })
            errorPage(self.pageState['MESSAGE'])
        else:
            try:
                self.doFetch()
            except brdfException, msg:
                self.pageState.update({'ERROR' : 1, 'MESSAGE' : str(msg) })

    def doFetch(self):

        # set up database connection
        #print "connecting using " + databaseModule.host + " , " + databaseModule.database
        
       	connection=databaseModule.getConnection()        
        searchCursor=connection.cursor()        


        # fetch the object as an ob, to get its type
        self.myObject = ob()

        # test whether we might have an lsid rather than an obid
        try:
           self.myObject.initFromDatabase(int(self.argDict['obid']),'ob',connection)
        except:
           # try assuming we have an lsid
           try:
              self.myObject.initFromDatabase(self.argDict['obid'],'ob',connection)
              self.argDict['obid'] = self.myObject.databaseFields['obid']
           except:
              raise brdfException("object not found : %s" % self.argDict['obid'])


        # this is defined globally in this module , but apparently needs to be defined locally as well 
        # - the python interpreter seems to dislike defaulting to the global 
        # version, if there is a block of code that defines a local version, so you can 
        # get self = <agresearchPages.fetchPage object>, self.myObject = <labResourceModule.labResourceOb object>, 
        # self.myObject.editURL = 'dummy value will be initialised by instance code', 
        # global editURL = 'http://agbrdfdev.agresearch.co.nz/zz_contents.htm' 
        # UnboundLocalError: local variable 'editURL' referenced before assignment 
        # args = ("local variable 'editURL' referenced before assignment",) 

        editURL=os.path.join(agbrdfConf.PAGEPATH,agbrdfConf.UNDERCONSTRUCTION) # re-set below on a type by type basis

        if self.myObject.databaseFields['tablename'] == 'geneticob':
            self.myObject = geneticOb()
            self.myObject.username=self.argDict['REMOTE_USER']
            self.myObject.initFromDatabase(int(self.argDict['obid']),connection)
            self.myObject.initMetadata(connection)
            self.myObject.discoverLinks(connection)
            self.myObject.initComments(connection)
            self.myObject.initHyperLinks(connection)                        
            self.myObject.initListMembership(connection)                 
            self.myObject.initDisplayFunctions(connection)
        elif self.myObject.databaseFields['tablename'] == 'oblist':
            self.myObject = obList()
            self.myObject.username=self.argDict['REMOTE_USER']
            if 'bookmark' in self.argDict:
                self.myObject.initFromDatabase(int(self.argDict['obid']),connection,self.argDict['bookmark'])
            else:
                self.myObject.initFromDatabase(int(self.argDict['obid']),connection)
            self.myObject.initMetadata(connection)
            self.myObject.discoverLinks(connection)            
            self.myObject.initComments(connection)
            self.myObject.initHyperLinks(connection)                        
            self.myObject.initListMembership(connection)                 
            self.myObject.initAnalysisFunctions(connection)
            self.myObject.initProtections(connection)
            if self.myObject.databaseFields['listtype'] == 'BIOSEQUENCE_LIST':
                self.myObject.fastaURL="/%s/"%agbrdfConf.CGIPATH + "fetch.py?obid=%s&context=fasta&target=ob"
                self.myObject.genbankURL="/%s/"%agbrdfConf.CGIPATH + "fetch.py?obid=%s&context=genbank&target=ob"
        elif self.myObject.databaseFields['tablename'] == 'geneexpressionstudy':
            self.myObject = geneExpressionStudy()
            self.myObject.username=self.argDict['REMOTE_USER']
            self.myObject.initFromDatabase(int(self.argDict['obid']),connection)
            self.myObject.initMetadata(connection)
            self.myObject.discoverLinks(connection)
            self.myObject.initComments(connection)
            self.myObject.initHyperLinks(connection)                        
            self.myObject.initListMembership(connection)                 
            self.myObject.initAnalysisFunctions(connection)
            self.myObject.initProtections(connection)
        elif self.myObject.databaseFields['tablename'] == 'genotypestudy':
            self.myObject = genotypeStudy()
            self.myObject.username=self.argDict['REMOTE_USER']
            self.myObject.initFromDatabase(int(self.argDict['obid']),connection)
            self.myObject.initMetadata(connection)
            self.myObject.discoverLinks(connection)
            self.myObject.initComments(connection)
            self.myObject.initHyperLinks(connection)
            self.myObject.initListMembership(connection)
        elif self.myObject.databaseFields['tablename'] == 'microarrayspotfact':
            self.myObject = microarraySpotFact()
            self.myObject.username=self.argDict['REMOTE_USER']
            self.myObject.initFromDatabase(int(self.argDict['obid']),connection)
            self.myObject.initMetadata(connection)
            self.myObject.discoverLinks(connection)
            self.myObject.initComments(connection)
            self.myObject.initHyperLinks(connection)                        
            self.myObject.initListMembership(connection)                 
            self.myObject.initDisplayFunctions(connection)      
            self.myObject.initProtections(connection)
        elif self.myObject.databaseFields['tablename'] == 'genetictestfact':
            self.myObject = geneticTestFact()
            self.myObject.username=self.argDict['REMOTE_USER']
            self.myObject.initFromDatabase(int(self.argDict['obid']),connection)
            self.myObject.initMetadata(connection)
            self.myObject.discoverLinks(connection)
            self.myObject.initComments(connection)
            self.myObject.initHyperLinks(connection)
            self.myObject.initListMembership(connection)
            self.myObject.initDisplayFunctions(connection)      
        elif self.myObject.databaseFields['tablename'] == 'biosampleob':
            self.myObject = bioSampleOb()
            self.myObject.username=self.argDict['REMOTE_USER']
            self.myObject.initFromDatabase(int(self.argDict['obid']),connection)
            self.myObject.initMetadata(connection)
            self.myObject.discoverLinks(connection)
            self.myObject.initComments(connection)
            self.myObject.initHyperLinks(connection)                        
            self.myObject.initListMembership(connection)                 
        elif self.myObject.databaseFields['tablename'] == 'biosamplingfunction':
            self.myObject = bioSamplingFunction()
            self.myObject.username=self.argDict['REMOTE_USER']
            self.myObject.initFromDatabase(int(self.argDict['obid']),connection)
            self.myObject.initMetadata(connection)
            self.myObject.discoverLinks(connection)
            self.myObject.initComments(connection)
            self.myObject.initHyperLinks(connection)
            self.myObject.initListMembership(connection)                 
        elif self.myObject.databaseFields['tablename'] == 'sequencingfunction':
            self.myObject = sequencingFunction()
            self.myObject.username=self.argDict['REMOTE_USER']
            self.myObject.initFromDatabase(int(self.argDict['obid']),connection)
            self.myObject.initMetadata(connection)
            self.myObject.discoverLinks(connection)
            self.myObject.initComments(connection)
            self.myObject.initHyperLinks(connection)
            self.myObject.initListMembership(connection)                 
        elif self.myObject.databaseFields['tablename'] == 'importfunction':
            self.myObject = importFunction()
            self.myObject.username=self.argDict['REMOTE_USER']
            self.myObject.initFromDatabase(int(self.argDict['obid']),connection)
            self.myObject.initMetadata(connection)
            self.myObject.discoverLinks(connection)
            self.myObject.initComments(connection)
            self.myObject.initHyperLinks(connection)                       
            self.myObject.initListMembership(connection)                 
        elif self.myObject.databaseFields['tablename'] == 'biosubjectob':
            self.myObject = bioSubjectOb()
            self.myObject.username=self.argDict['REMOTE_USER']
            self.myObject.initFromDatabase(int(self.argDict['obid']),connection)
            self.myObject.initMetadata(connection)
            self.myObject.discoverLinks(connection)
            self.myObject.initComments(connection)
            self.myObject.initHyperLinks(connection)                        
            self.myObject.initListMembership(connection)                 
        elif self.myObject.databaseFields['tablename'] == 'datasourceob':
            self.myObject = dataSourceOb()
            self.myObject.username=self.argDict['REMOTE_USER']
            self.myObject.initFromDatabase(int(self.argDict['obid']),connection)
            self.myObject.initMetadata(connection)
            self.myObject.discoverLinks(connection)
            self.myObject.initComments(connection)
            self.myObject.initHyperLinks(connection)
            self.myObject.initListMembership(connection)                 
            self.myObject.initAnalysisFunctions(connection)
            self.myObject.initRelatedAnalysisFunctions(connection)
            self.myObject.initProtections(connection)
            self.myObject.linkAnalysisProcedureURL="/%s/"%agbrdfConf.CGIPATH + "form.py?formname=linkAnalysisProcedureForm&formstate=edit&context=default&obid=%(obid)s&xreflsid=%(xreflsid)s"%self.myObject.databaseFields
        elif self.myObject.databaseFields['tablename'] == 'datasourcelist':
            self.myObject = dataSourceList()
            self.myObject.username=self.argDict['REMOTE_USER']
            self.myObject.initFromDatabase(int(self.argDict['obid']),connection)
            self.myObject.initMetadata(connection)
            self.myObject.discoverLinks(connection)
            self.myObject.initComments(connection)
            self.myObject.initHyperLinks(connection)
            self.myObject.initListMembership(connection)
            self.myObject.initAnalysisFunctions(connection)
            self.myObject.initProtections(connection)
        elif self.myObject.databaseFields['tablename'] == 'importprocedureob':
            self.myObject = importProcedureOb()
            self.myObject.username=self.argDict['REMOTE_USER']
            self.myObject.initFromDatabase(int(self.argDict['obid']),connection)
            self.myObject.initMetadata(connection)
            self.myObject.discoverLinks(connection)
            self.myObject.initComments(connection)
            self.myObject.initHyperLinks(connection)                        
            self.myObject.initListMembership(connection)                 
        elif self.myObject.databaseFields['tablename'] == 'biosequenceob':
            self.myObject = bioSequenceOb()
            self.myObject.username=self.argDict['REMOTE_USER']

            # 12/2011 support genomic seqs in database
            if self.argDict["context"] in ["fasta","genbank"]:
                self.myObject.MAX_INLINE_SEQUENCE_LENGTH = 1000000
                self.myObject.MAX_INLINE_FEATURE_COUNT = 1000
            self.myObject.initFromDatabase(int(self.argDict['obid']),connection)
            self.myObject.initMetadata(connection)
            self.myObject.discoverLinks(connection)
            self.myObject.initComments(connection)
            self.myObject.initHyperLinks(connection)                        
            self.myObject.initListMembership(connection)                 
            self.myObject.initDisplayFunctions(connection)      
            self.myObject.initProtections(connection)
            self.myObject.initAnalysisFunctions(connection)
            editURL="/%s/"%agbrdfConf.CGIPATH + "form.py?formname=AgResearchSequenceSubmissionForm&formstate=edit&obid=%s"
            self.myObject.fastaURL="/%s/"%agbrdfConf.CGIPATH + "fetch.py?obid=%s&context=fasta&target=ob"
            self.myObject.genbankURL="/%s/"%agbrdfConf.CGIPATH + "fetch.py?obid=%s&context=genbank&target=ob"
        elif self.myObject.databaseFields['tablename'] == 'workflowob':
            self.myObject = workFlowOb()
            self.myObject.username=self.argDict['REMOTE_USER']
            self.myObject.initFromDatabase(int(self.argDict['obid']),connection)
            self.myObject.initMetadata(connection)
            self.myObject.discoverLinks(connection)
            self.myObject.initComments(connection)
            self.myObject.initHyperLinks(connection)                        
            self.myObject.initListMembership(connection)                 
        elif self.myObject.databaseFields['tablename'] == 'workflowstageob':
            self.myObject = workFlowStageOb()
            self.myObject.username=self.argDict['REMOTE_USER']
            self.myObject.initFromDatabase(int(self.argDict['obid']),connection)
            self.myObject.initMetadata(connection)
            self.myObject.discoverLinks(connection)
            self.myObject.initComments(connection)
            self.myObject.initHyperLinks(connection)                        
            self.myObject.initListMembership(connection)                 
        elif self.myObject.databaseFields['tablename'] == 'ontologyob':
            self.myObject = ontologyOb()
            self.myObject.username=self.argDict['REMOTE_USER']
            self.myObject.initFromDatabase(int(self.argDict['obid']),connection)
            self.myObject.initMetadata(connection)
            self.myObject.discoverLinks(connection)
            self.myObject.initComments(connection)
            self.myObject.initHyperLinks(connection)                        
            self.myObject.initListMembership(connection)                 
        elif self.myObject.databaseFields['tablename'] == 'ontologytermfact':
            self.myObject = ontologyTermFact()
            self.myObject.username=self.argDict['REMOTE_USER']
            self.myObject.initFromDatabase(int(self.argDict['obid']),connection)
            self.myObject.initMetadata(connection)
            self.myObject.discoverLinks(connection)
            self.myObject.initComments(connection)
            self.myObject.initHyperLinks(connection)                        
            self.myObject.initListMembership(connection)                 
        elif self.myObject.databaseFields['tablename'] == 'labresourceob':
            self.myObject = labResourceOb()
            self.myObject.username=self.argDict['REMOTE_USER']
            self.myObject.initFromDatabase(int(self.argDict['obid']),connection)
            self.myObject.initMetadata(connection)
            self.myObject.discoverLinks(connection)
            self.myObject.initComments(connection)
            self.myObject.initHyperLinks(connection)                        
            self.myObject.initListMembership(connection)                 
            self.myObject.initAnalysisFunctions(connection)
            self.myObject.initProtections(connection)
        elif self.myObject.databaseFields['tablename'] == 'labresourcelist':
            self.myObject = labResourceList()
            self.myObject.username=self.argDict['REMOTE_USER']
            self.myObject.initFromDatabase(int(self.argDict['obid']),connection)
            self.myObject.initMetadata(connection)
            self.myObject.discoverLinks(connection)
            self.myObject.initComments(connection)
            self.myObject.initHyperLinks(connection)                        
            self.myObject.initListMembership(connection)                 
        elif self.myObject.databaseFields['tablename'] == 'biosequencefeaturefact':
            self.myObject = bioSequenceFeatureFact()
            self.myObject.username=self.argDict['REMOTE_USER']
            self.myObject.initFromDatabase(int(self.argDict['obid']),connection)
            self.myObject.initMetadata(connection)
            self.myObject.discoverLinks(connection)
            self.myObject.initComments(connection)
            self.myObject.initHyperLinks(connection)                        
            self.myObject.initListMembership(connection)                 
        elif self.myObject.databaseFields['tablename'] == 'geneticlocationfact':
            self.myObject = geneticLocationFact()
            self.myObject.username=self.argDict['REMOTE_USER']
            self.myObject.initFromDatabase(int(self.argDict['obid']),connection)
            self.myObject.initMetadata(connection)
            self.myObject.discoverLinks(connection)
            self.myObject.initComments(connection)
            self.myObject.initHyperLinks(connection)                        
            self.myObject.initListMembership(connection)                 
            self.myObject.initDisplayFunctions(connection)
        elif self.myObject.databaseFields['tablename'] == 'geneticfunctionfact':
            self.myObject = geneticFunctionFact()
            self.myObject.username=self.argDict['REMOTE_USER']
            self.myObject.initFromDatabase(int(self.argDict['obid']),connection)
            self.myObject.initMetadata(connection)
            self.myObject.discoverLinks(connection)
            self.myObject.initComments(connection)
            self.myObject.initHyperLinks(connection)                        
            self.myObject.initListMembership(connection)                 
        elif self.myObject.databaseFields['tablename'] == 'microarrayfact':
            self.myObject = microarrayFact()
            self.myObject.username=self.argDict['REMOTE_USER']
            self.myObject.initFromDatabase(int(self.argDict['obid']),connection)
            self.myObject.initMetadata(connection)
            self.myObject.discoverLinks(connection)
            self.myObject.initComments(connection)
            self.myObject.initHyperLinks(connection)                        
            self.myObject.initListMembership(connection)                 
        elif self.myObject.databaseFields['tablename'] == 'bioprotocolob':
            self.myObject = bioProtocolOb()
            self.myObject.username=self.argDict['REMOTE_USER']
            self.myObject.initFromDatabase(int(self.argDict['obid']),connection)
            self.myObject.initMetadata(connection)
            self.myObject.discoverLinks(connection)
            self.myObject.initComments(connection)
            self.myObject.initHyperLinks(connection)                        
            self.myObject.initListMembership(connection)                 
        elif self.myObject.databaseFields['tablename'] == 'biosamplelist':
            self.myObject = bioSampleList()
            self.myObject.username=self.argDict['REMOTE_USER']
            self.myObject.initFromDatabase(int(self.argDict['obid']),connection)
            self.myObject.initMetadata(connection)
            self.myObject.discoverLinks(connection)
            self.myObject.initComments(connection)
            self.myObject.initHyperLinks(connection)
            self.myObject.initListMembership(connection)                 
        elif self.myObject.databaseFields['tablename'] == 'phenotypestudy':
            self.myObject = phenotypeStudy()
            self.myObject.username=self.argDict['REMOTE_USER']                          
            self.myObject.initFromDatabase(int(self.argDict['obid']),connection)
            self.myObject.initMetadata(connection)
            self.myObject.discoverLinks(connection)
            self.myObject.initComments(connection)
            self.myObject.initHyperLinks(connection)
            self.myObject.initListMembership(connection)                 
        elif self.myObject.databaseFields['tablename'] == 'commentob':
            self.myObject = commentOb()
            self.myObject.username=self.argDict['REMOTE_USER']                          
            self.myObject.initFromDatabase(int(self.argDict['obid']),connection)
            self.myObject.initMetadata(connection)
            self.myObject.discoverLinks(connection)
            self.myObject.initComments(connection)
            self.myObject.initHyperLinks(connection)            
            self.myObject.initListMembership(connection)                 
        elif self.myObject.databaseFields['tablename'] == 'phenotypeobservation':
            self.myObject = phenotypeObservation()
            self.myObject.username=self.argDict['REMOTE_USER']                          
            self.myObject.initFromDatabase(int(self.argDict['obid']),connection)
            self.myObject.initMetadata(connection)
            self.myObject.discoverLinks(connection)
            self.myObject.initComments(connection)
            self.myObject.initHyperLinks(connection)
            self.myObject.initListMembership(connection)                 
        elif self.myObject.databaseFields['tablename'] == 'genotypeobservation':
            self.myObject = genotypeObservation()
            self.myObject.username=self.argDict['REMOTE_USER']
            self.myObject.initFromDatabase(int(self.argDict['obid']),connection)
            self.myObject.initMetadata(connection)
            self.myObject.discoverLinks(connection)
            self.myObject.initComments(connection)
            self.myObject.initHyperLinks(connection)
            self.myObject.initListMembership(connection)
        elif self.myObject.databaseFields['tablename'] == 'microarrayobservation':
            self.myObject = microarrayObservation()
            self.myObject.username=self.argDict['REMOTE_USER']                          
            self.myObject.initFromDatabase(int(self.argDict['obid']),connection)
            self.myObject.initMetadata(connection)
            self.myObject.discoverLinks(connection)
            self.myObject.initComments(connection)
            self.myObject.initHyperLinks(connection)            
            self.myObject.initListMembership(connection)                 
            self.myObject.initProtections(connection)                 
        elif self.myObject.databaseFields['tablename'] == 'uriob':
            self.myObject = uriOb()
            self.myObject.username=self.argDict['REMOTE_USER']                          
            self.myObject.initFromDatabase(int(self.argDict['obid']),connection)
            self.myObject.initMetadata(connection)
            self.myObject.discoverLinks(connection)
            self.myObject.initComments(connection)
            self.myObject.initHyperLinks(connection)                        
            self.myObject.initListMembership(connection)                 
        elif self.myObject.databaseFields['tablename'] == 'biodatabaseob':
            self.myObject = bioDatabaseOb()
            self.myObject.username=self.argDict['REMOTE_USER']                          
            self.myObject.initFromDatabase(int(self.argDict['obid']),connection)
            self.myObject.initMetadata(connection)
            self.myObject.discoverLinks(connection)
            self.myObject.initComments(connection)
            self.myObject.initHyperLinks(connection)           
            self.myObject.initListMembership(connection)
        elif self.myObject.databaseFields['tablename'] == 'databasesearchstudy':
            self.myObject = databaseSearchStudy()
            self.myObject.username=self.argDict['REMOTE_USER']                          
            self.myObject.initFromDatabase(int(self.argDict['obid']),connection)
            self.myObject.initMetadata(connection)
            self.myObject.discoverLinks(connection)
            self.myObject.initComments(connection)
            self.myObject.initHyperLinks(connection)           
            self.myObject.initListMembership(connection)
        elif self.myObject.databaseFields['tablename'] == 'databasesearchobservation':
            self.myObject = databaseSearchObservation()
            self.myObject.username=self.argDict['REMOTE_USER']                          
            self.myObject.initFromDatabase(int(self.argDict['obid']),connection)
            self.myObject.initMetadata(connection)
            self.myObject.discoverLinks(connection)
            self.myObject.initComments(connection)
            self.myObject.initHyperLinks(connection)           
            self.myObject.initListMembership(connection)                        
        elif self.myObject.databaseFields['tablename'] == 'sequencealignmentfact':
            self.myObject = sequenceAlignmentFact()
            self.myObject.username=self.argDict['REMOTE_USER']
            self.myObject.initFromDatabase(int(self.argDict['obid']),connection)
            self.myObject.initMetadata(connection)
            self.myObject.discoverLinks(connection)
            self.myObject.initComments(connection)
            self.myObject.initHyperLinks(connection)
            self.myObject.initListMembership(connection)
        elif self.myObject.databaseFields['tablename'] == 'genetictestfact':
            self.myObject = geneticTestFact()
            self.myObject.username=self.argDict['REMOTE_USER']                          
            self.myObject.initFromDatabase(int(self.argDict['obid']),connection)
            self.myObject.initMetadata(connection)
            self.myObject.discoverLinks(connection)
            self.myObject.initComments(connection)
            self.myObject.initHyperLinks(connection)           
            self.myObject.initListMembership(connection)
        elif self.myObject.databaseFields['tablename'] == 'genotypestudy':
            self.myObject = genotypeStudy()
            self.myObject.username=self.argDict['REMOTE_USER']                          
            self.myObject.initFromDatabase(int(self.argDict['obid']),connection)
            self.myObject.initMetadata(connection)
            self.myObject.discoverLinks(connection)
            self.myObject.initComments(connection)
            self.myObject.initHyperLinks(connection)           
            self.myObject.initListMembership(connection)                      
        elif self.myObject.databaseFields['tablename'] == 'biolibraryob':
            self.myObject = bioLibraryOb()
            self.myObject.username=self.argDict['REMOTE_USER']
            self.myObject.initFromDatabase(int(self.argDict['obid']),connection)
            self.myObject.initMetadata(connection)
            self.myObject.discoverLinks(connection)
            self.myObject.initComments(connection)
            self.myObject.initHyperLinks(connection)
        elif self.myObject.databaseFields['tablename'] == 'librarysequencingfunction':
            self.myObject = librarySequencingFunction()
            self.myObject.username=self.argDict['REMOTE_USER']
            self.myObject.initFromDatabase(int(self.argDict['obid']),connection)
            self.myObject.initMetadata(connection)
            self.myObject.discoverLinks(connection)
            self.myObject.initComments(connection)
            self.myObject.initHyperLinks(connection)
        elif self.myObject.databaseFields['tablename'] == 'analysisprocedureob':
            self.myObject = analysisProcedureOb()
            self.myObject.username=self.argDict['REMOTE_USER']
            self.myObject.initFromDatabase(int(self.argDict['obid']),connection)
            self.myObject.initMetadata(connection)
            self.myObject.discoverLinks(connection)
            self.myObject.initComments(connection)
            self.myObject.initHyperLinks(connection)
            self.myObject.initListMembership(connection)
            self.myObject.initAnalysisFunctions(connection)
            editURL="/%s/"%agbrdfConf.CGIPATH + "form.py?formname=editAnalysisProcedureForm&formstate=edit&context=default&obid=%(obid)s&xreflsid=%(xreflsid)s"%self.myObject.databaseFields


        # intialise the ob with the call back URL paths for this instance of the brdf
        if self.myObject.obState['METADATA'] == 1:
            self.myObject.columnAliases = getColumnAliases(connection, self.myObject.metadataFields['tablename'])
            
            

        # intialise the ob with the call back URL paths for this instance of the brdf
        self.myObject.fetcher=fetcher
        self.myObject.waiter=waiter
        self.myObject.displayfetcher=displayfetcher
        self.myObject.analysisfetcher=analysisfetcher
        self.myObject.imageurl=imageurl
        self.myObject.tempimageurl=tempimageurl
        self.myObject.imagepath=imagepath
        self.myObject.jointomemberurl=jointomemberurl
        self.myObject.jointonullurl=jointonullurl
        self.myObject.jointooburl=jointooburl
        self.myObject.joinfacturl=joinfacturl
        self.myObject.jointoopurl=jointoopurl
        self.myObject.addCommentURL=addCommentURL
        self.myObject.addLinkURL=addLinkURL
        self.myObject.homeurl=homeurl
        self.myObject.underConstructionURL=underConstructionURL        
        self.myObject.waitURL=waitURL
        self.myObject.padlockurl=padlockurl
        self.myObject.editURL=editURL
        
        
        connection.close()
        
    def asHTML(self):
        # tell the object where the basehref is
        self.myObject.basehref=agbrdfConf.CGIPATH
        if self.argDict['context'] ==  'briefsearchsummarypage' and isinstance(self.myObject,obList):
            # add fetch URL for each object
            self.myObject.databaseFields.update({'listitems' : [tuple + (objectDumpURL%(str(tuple[0]),self.argDict['childview']),) for tuple in self.myObject.databaseFields['listitems']] })
            self.myObject.listChunkLink = listChunkLink

            # we need to display an icon for the list. We base this on the type of the first element in the
            # list.
            connection=databaseModule.getConnection()
            exampleMetadata = getObTypeMetadata(connection,getInstanceBaseType(connection,self.myObject.databaseFields['listitems'][0][0]))
            connection.close()            
            self.myObject.listAboutLink = imageurl + exampleMetadata['displayurl']

            pagecount = int(.9999 + self.myObject.databaseFields['currentmembership']*1.0/self.myObject.chunkSize*1.0)

            content = '<table border=yes width=90%>\n'

            content +=  self.myObject.asHTMLTableRow(title="%s (page %d of %d)"%(exampleMetadata['displayname'],int(self.argDict['page'])+1,pagecount),width='90%',context=self.argDict['context'],view=self.argDict['childview'],page=str(int(self.argDict['page'])+1))
            content += '</table>'
 
            return htmlModule.pageWrap(" ",content,cssLink=brdfCSSLink)
        else:
            #return  htmlModule.pageWrap(" ",self.myObject.asHTMLTableRows(context=self.argDict['context']))
            return htmlModule.pageWrap(" ",self.myObject.asHTMLTableRows(context=self.argDict['context']), menuJS=self.myObject.getMenuBarJS(metadata=self.myObject.obState['METADATA'],context=self.argDict['context']),cssLink=brdfCSSLink)


    def asGenbank(self):
        # example : http://agbrdf.agresearch.co.nz/cgi-bin/fetch.py?obid=CS37.231105CS3700262300001&context=genbank&target=ob
        agresearchpagemodulelogger.info("handling Genbank request for object type %s"%self.myObject.metadataFields['tablename'])
        gbresult = ''
        if self.myObject.metadataFields['tablename'] == 'bioSequenceOb':
            gbresult = htmlModule.genbankContentHeader

            sql = """
            select getgenbankrecord(%(xreflsid)s)
            """
            connection = databaseModule.getConnection()
            gbcursor = connection.cursor()
            gbcursor.execute(sql,self.myObject.databaseFields)
            seqs = gbcursor.fetchone()
            if seqs != None:
                gbresult = htmlModule.genbankContentHeader +  seqs[0]
            else:
                gbresult = textContentHeader + "error , no record returned for  %(xreflsid)s" % self.myObject.databaseFields

            gbcursor.close()
            connection.close()
        elif self.myObject.metadataFields['tablename'] == 'Oblist':
            agresearchpagemodulelogger.info("rendering list as Genbank...")
            if self.myObject.databaseFields['listtype'] == 'BIOSEQUENCE_LIST':
                connection = databaseModule.getConnection()
                gbcursor = connection.cursor()
                biosequence = bioSequenceOb()
                gbresult = htmlModule.genbankContentHeader
                for membertuple in self.myObject.databaseFields['alllistitems']:
                    biosequence.initFromDatabase(int(membertuple[0]),connection)
                    sql = """
                    select getgenbankrecord(%(xreflsid)s)
                    """
                    gbcursor.execute(sql,biosequence.databaseFields)
                    seqs = gbcursor.fetchone()
                    if seqs != None:
                        gbresult += htmlModule.genbankContentHeader +  seqs[0]
                gbcursor.close()
                connection.close()
        return gbresult


    def asFASTA(self):
        # example : http://agbrdf.agresearch.co.nz/cgi-bin/fetch.py?obid=CS37.231105CS3700262300001&context=fasta&target=ob
        agresearchpagemodulelogger.info("handling FASTA request for object type %s"%self.myObject.metadataFields['tablename'])
        fastaresult = ''
        if self.myObject.metadataFields['tablename'] == 'bioSequenceOb':
            agresearchpagemodulelogger.info("interpolating using %s"%str(self.myObject.databaseFields))
         
            (outline,pos) = tidyout(self.myObject.databaseFields['seqstring'], 60, 0, '\n', False)
            fastaresult = htmlModule.fastaContentHeader + \
		      (">%(xreflsid)s %(sequencedescription)s\n"%self.myObject.databaseFields)  + \
                      outline +\
                      htmlModule.fastaContentFooter
        elif self.myObject.metadataFields['tablename'] == 'Oblist':
            agresearchpagemodulelogger.info("rendering list as FASTA...")
            if self.myObject.databaseFields['listtype'] in ['BIOSEQUENCE_LIST','USER_PROJECT_LIST']:
                # 23/3/2010 # if the list size is > 1000 do it faster...
                connection = databaseModule.getConnection()
                seqcount = 0
                if self.myObject.databaseFields['currentmembership'] > 1000:
                    fastaresult = ""
                    filename = self.myObject.databaseFields["listname"] + ".fa"
                    print htmlModule.fastaListDownloadHeader%(filename,filename,filename)
                    sql = """
                    select
                       xreflsid,
                       sequencedescription,
                       seqstring
                    from
                       biosequenceob b join listmembershiplink l  on
                       b.obid = l.ob
                    where
                       l.oblist = %(obid)s
                    """
                    seqcursor = connection.cursor()
                    agresearchpagemodulelogger.info("executing %s"%(sql%self.myObject.databaseFields))
                    seqcursor.execute(sql, self.myObject.databaseFields)
                    seq = seqcursor.fetchone()
                    while seq != None:
                        (outline,pos) = tidyout(seq[2], 60, 0, '\n', False)
                        print  ((">%s %s\n"%(seq[0],seq[1]))  + outline )
                        seq = seqcursor.fetchone()
                        seqcount += 1
                        if seqcount%100 == 1:
                            agresearchpagemodulelogger.info("seqcount = %s"%seqcount)
                else:
                    biosequence = bioSequenceOb()
                    # 14/3/2010 changed lists to be file download
                    #fastaresult = htmlModule.fastaContentHeader
                    filename = self.myObject.databaseFields["listname"] + ".fa"
                    fastaresult = htmlModule.fastaListDownloadHeader%(filename,filename,filename)
                    for membertuple in self.myObject.databaseFields['alllistitems']:
                        biosequence.initFromDatabase(int(membertuple[0]),connection)
                        if biosequence.databaseFields['seqstring'] != None:
                            (outline,pos) = tidyout(biosequence.databaseFields['seqstring'], 60, 0, '\n', False)
                        else:
                            (outline,pos) = ("",0)
                        fastaresult += ((">%(xreflsid)s %(sequencedescription)s\n"%biosequence.databaseFields)  + outline + "\n")
                    #fastaresult += htmlModule.fastaContentFooter

        return fastaresult

    # some objects such as SQL data sources may be executed and will print a report
    def execute(self):
        canExecute = False
        if  self.myObject.metadataFields['tablename'].lower() == 'datasourceob':
            if self.myObject.databaseFields["datasourcetype"] in ("SQL","Executable"):
                canExecute = True
            elif re.search("Executable",self.myObject.databaseFields["datasourcetype"]) != None:
                canExecute = True

        if canExecute:
            connection=databaseModule.getConnection()
            self.myObject.execute(connection)
        else:
            errorPage("Cannot execute %s : %s "%(self.myObject.databaseFields["xreflsid"], str(self.myObject.metadataFields)))


######################################################################
#
# This page fetches a join from the database.
# Joins are usually requested by clicking on an icon in the information
# map  -either
#
# Linked Ob table : Ob ---> Ob
# http://localhost/cgi-bin/sheepgenomics/fetch.py?context=join&totype=64&fromob=876786&jointype=78
#
# or
#
# Fact table : Ob --->
# http://localhost/cgi-bin/sheepgenomics/fetch.py?context=join&fromob=876786&jointype=78
#
# or
# 
# Op (relation) table :
# http://localhost/cgi-bin/sheepgenomics/join.py?context=join&totype=102&jointype=240&joininstance=204847
#
# The first form means that we are to execute a query that returns all objects of type totype, that
# are involved in a relation of type jointype, that include object whose id is obtype
#
# Example :
# fromob=48907  (GeneticOb)
# jointype= 201 (GeneProductLink)
# totype = 115 (bioSequence )
#
# select
#   bio.sequencename
# from
#   biosequenceob bio,geneproductlink gpl
# where
#   gpl.geneticob = 48907 and
#   bio.obid = gpl.biosequenceob
#
#
# The second form means that we are to execute a query that returns all records from the
# jointype table that include the instance obtype
#
#
# The third for is when the "current" object is an op, and means we are to
# retrieve all objects of type totype, that are involved in the joininstance
# of the jointype - e.g. as in the above example, retrieve the biosample list
# associated with the given microarray study
#
# Example :
#
# select
#    *
# from
#    biosamplelist bl, geneexpressionstudy ms
# where
#    ms.obid = 204847 and
#    bl.obid = ms.biosamplelist
# 
# 
#
######################################################################


class joinPage ( page ):
    """ class for fetchPage  """
    def __init__(self, argDict):
        page.__init__(self)
        self.argDict = argDict

        if not 'delivery' in self.argDict:
            self.argDict['delivery']='preview'        

    
        try:
            connection=databaseModule.getConnection()
            self.doJoin(connection)
        finally:
            connection.close()
        
    def doJoin(self, connection):
        
        (sqlquery,sqlbinding,opmeta,obmeta,joinTitle) = getJoinQuery(connection, self.argDict)
        
        joinCursor = connection.cursor()
        sql = sqlquery%sqlbinding
        agresearchpagemodulelogger.info('executing ' + sql)

        joinCursor.execute(sql)
        joinRecord  = joinCursor.fetchone()
        if joinRecord is not None:
            joinRecord  = list(joinRecord)

        rowCount = 0
        fieldNames = [item[0] for item in joinCursor.description]


        # now construct heading
        pagebuff = ""
        fetchob = None

        if obmeta['displayname'] != opmeta['displayname']:
            reportHeading = """
            <h2 align=center> %s  </h2> <p/>
            <h3 align=center> as at %s </h3>"""\
                     %(joinTitle,date.isoformat(date.today()))                        
#            reportHeading = """
#            <h1 align=center>Linked Details</h1>
#                    <h2 align=center> %s , in %s </h2> <p/>
#                    <h3 align=center> as at %s </h3>"""\
#                                %(obmeta['displayname'],opmeta['displayname'],date.isoformat(date.today()))
        else:
            reportHeading = """
            <h2 align=center> %s  </h2> <p/>
            <h3 align=center> as at %s </h3>"""\
                     %(joinTitle,date.isoformat(date.today()))                                    
#            <h1 align=center>Linked Details</h1>
#                    <h2 align=center> %s </h2> <p/>
#                    <h3 align=center> as at %s </h3>"""\
#                                %(opmeta['displayname'],date.isoformat(date.today()))            
            
        #print getReportHeader('Join',reportHeading,fieldNames)
        header = ""
        if self.argDict['delivery'] == 'download':
            header = getDownloadHeader('brdfreport.html','Join',reportHeading,fieldNames)
        else:
            header = getReportHeader('Join',reportHeading,fieldNames)
        agresearchpagemodulelogger.info("sending header : \n %s"%header)
        #print header
        pagebuff += header


        while joinRecord != None:
            rowCount += 1
            # fields called obid are hyperlinked
            # http://localhost/cgi-bin/Nutrigenomics/fetch.py?context=dump&obid=1053&target=ob
            # http://localhost/cgi-bin/nutrigenomics/fetch.py            
            if 'obid' in fieldNames:
                for i in range(0,len(fieldNames)):
                    if fieldNames[i] == 'obid':
                        if i==0:
                            fetchob = joinRecord[i]
                        joinRecord[i] = '<a href="'+fetcher + "?context=%s&obid=%s&target=ob"%(self.argDict['context'],joinRecord[i]) + '">%s</a>'%joinRecord[i]
            
            record = '<tr>'
            record+=reduce(lambda x,y: x+'<td>'+str(y)+'</td>', joinRecord,'')

            # we buffer the first record. If we get to a second record we print
            # the buffer and then do no further buffering
            if rowCount == 1:
                pagebuff += record+'</tr>\n'
            elif rowCount == 2:
                print(pagebuff)
                print(record+'</tr>\n')
            else:
                print(record+'</tr>\n')


            if self.argDict['delivery'] == 'preview':
                if rowCount >= globalConf.JOIN_ROW_LIMIT:
                    break
                
            joinRecord  = joinCursor.fetchone()
            if joinRecord is not None:
                joinRecord  = list(joinRecord)


        # if we only got one row we redirect to the redirecturl if we were able to get one
        if rowCount == 1 and fetchob != None:
            agresearchpagemodulelogger.info("join is redirecting to %s"%fetchob)
            self.argDict.update({
                    'obid' : fetchob,
                    'target': 'ob',
                    'REMOTE_USER' : eval({True : "self.argDict['REMOTE_USER']" , False : "'nobody'"}['REMOTE_USER' in self.argDict])
                })
            obpage = fetchPage(self.argDict)
            obpage.doFetch()
            print obpage.asHTML()            

        # else we are not redirecting...
        else:
            # if just one or none row , output is buffered so output it
            if rowCount <=  1:
                print(pagebuff)

            # ..do footer processing
            footer = ""
            if rowCount >= globalConf.JOIN_ROW_LIMIT:
                # if the type of join has been described as hash 1 then we append a URL that allows
                # the user to download the entire dataset. The URL is the same as that which called this
                # method but with a different delivery
                footer="(Rows reported have been limited to %d)"%globalConf.JOIN_ROW_LIMIT
                if 'joinhash' in self.argDict:
                    if self.argDict['joinhash'] == '1':
                        #jointooburl="/%s/"%nutrigenomicsConf.CGIPATH + "join.py?context=%s&totype=%s&fromob=%s&jointype=%s&joinhash=1"
                        footer += "<a href=" + \
                              jointooburl%(self.argDict['context'],self.argDict['totype'],self.argDict['fromob'],\
                              self.argDict['jointype']) + "&delivery=download" + \
                              "> click here to download complete report </a><br/> Note that HTML reports can be opened directly by Excel"
                    elif self.argDict['joinhash'] == '2':
                        #join.py?context=%s&fromob=%s&jointype=%s&joinhash=2
                        footer += "<a href=" + \
                              joinfacturl%(self.argDict['context'],self.argDict['fromob'],self.argDict['jointype']) + \
                              "&delivery=download" + \
                              "> click here to download complete report </a><br/> Note that HTML reports can be opened directly by Excel"                    
                    
            
            print getReportFooter(rowCount,footer)


######################################################################
#
# This page presents and executes simple reports
#
######################################################################

class simpleReportPage ( page ):
    """ class for simpleReportPage  """
    def __init__(self, argDict):
        page.__init__(self)
        self.argDict = argDict
        agresearchpagemodulelogger.info("simpleReportPage initialised with %s"%str(self.argDict))

    def displayReportPage(self):
        """ method to display a report page, including dynamic population of lists """
        if self.argDict['page'] == 'report_microarrayextract1':
            try :
                connection=databaseModule.getConnection()
                listCursor = connection.cursor()
                sql = """
                    select ges.obid, ges.xreflsid ,ds.datasourcetype from
                    (geneexpressionstudy ges join importfunction if on if.ob = ges.obid)
                    join datasourceob ds on ds.obid = if.datasourceob
                    order by xreflsid
                """
                listCursor.execute(sql)
                listTuples = listCursor.fetchall()
                if listCursor.rowcount == 0:
                    experimentListHTML='<font color="red"><i>no experiments in database</i></font>'
                else:
                    experimentListHTML = '<select name="experiments" multiple size=10>\n' + \
                               reduce(lambda x,y:x+'<option value="%s"/> %s \n'%(y[0],"%s          (%s id=%s)"%(y[1],y[2],y[0])) ,listTuples,'') + \
                               '</select>\n'
                print "Content-Type: text/html\n\n"
                reportText = re.sub('__experimentListHTML__',experimentListHTML,report_microarrayextract1)    
                print reportText
            finally:
                listCursor.close()        
                if connection != None:
                    connection.close()
        elif self.argDict['page'] == 'report_locusreports':
            # open a query to get lists of genes
            try:
           	connection=databaseModule.getConnection()            	
                listCursor = connection.cursor()
                sql = """
                select obid,listdefinition,currentmembership from oblist where listtype = 'SEARCH_RESULT' and listdefinition like '%Search of Genetic Tables%' and
                currentmembership > 0 order by createddate desc
                """
                listCursor.execute(sql)
                listTuples = listCursor.fetchall()
                if listCursor.rowcount == 0:
                    geneListHTML='<font color="red"><i>no gene lists available - to create a list , just execute a search from the main page</i></font>'
                else:
                    geneListHTML = '<select name="genelistid">\n' + \
                               reduce(lambda x,y:x+'<option value="%s"/> %s (count=%s)\n'%(y[0],y[1],y[2]) ,listTuples,'') + \
                               '</select>\n'

                sql = """
                select obid,listdefinition,currentmembership from oblist where listtype in ('BIOSEQUENCE_LIST','USER_PROJECT_LIST') and
                currentmembership > 0 order by createddate desc
                """
                listCursor.execute(sql)
                listTuples = listCursor.fetchall()
                if listCursor.rowcount == 0:
                    candidategeneListHTML='<font color="red"><i>no candidate gene lists are currently available </i></font>'
                else:
                    candidategeneListHTML = '<select name="candidategenelistid">\n' + \
                               reduce(lambda x,y:x+'<option value="%s"/> %s (count=%s)\n'%(y[0],y[1],y[2]) ,listTuples,'') + \
                               '</select>\n'                    
                    
            finally:
                listCursor.close()        
                if connection != None:
                    connection.close()                
            
            print "Content-Type: text/html\n\n" 
            print report_locusreports%({'geneListHTML' : geneListHTML, 'candidategeneListHTML' : candidategeneListHTML })
         
        elif self.argDict['page'] == 'report_snpreports':
            try:
           	connection=databaseModule.getConnection()            	
                listCursor = connection.cursor()
                sql = """
                select xreflsid,listdefinition,currentmembership from oblist where listtype = 'USER_PROJECT_LIST' and listdefinition like 'Animals%' and
                currentmembership > 0 order by createddate desc
                """
                listCursor.execute(sql)
                listTuples = listCursor.fetchall()
                if listCursor.rowcount == 0:
                    animalListHTML='<font color="red"><i>no animal lists available</i></font>'
                else:
                    animalListHTML = '<select name="animallists" multiple size=10>\n' + \
                               reduce(lambda x,y:x+'<option value="%s"/> %s (count=%s)\n'%(y[0],y[1],y[2]) ,listTuples,'') + \
                               '</select>\n'
                    
            finally:
                listCursor.close()        
                if connection != None:
                    connection.close()                
            
            print "Content-Type: text/html\n\n" 
            print report_snpreports%({'animalListHTML' : animalListHTML })

        elif self.argDict['page'] == 'report_sequenceextractreports':
            # open a query to get lists of genes
            try:
           	connection=databaseModule.getConnection()            	
                listCursor = connection.cursor()
                sql = """
                select obid,listdefinition,currentmembership,to_char(createddate,'dd-mm-yyyy') as createddate from oblist where listtype = 'SEARCH_RESULT' and 
                (listdefinition like '%Search of BioSequences%' or listdefinition like 'Sequence List:%' ) and
                currentmembership > 0 order by obid desc
                """
                agresearchpagemodulelogger.info("executing %s"%sql)

                listCursor.execute(sql)
                listTuples = listCursor.fetchall()

                # get rid of ones we do not want
                #listTuples = [item for item in listTuples if re.search('Search of BioSequences for %',item[1]) == None]
                #listTuples = [item for item in listTuples if item[2] < 1000]

                # eliminate duplicates
                listTupleDefs = {}
                nrlistTuples = []
                for mytuple in listTuples:
                   if mytuple[1] not in listTupleDefs:
                      listTupleDefs[mytuple[1]] = None
                      nrlistTuples.append(mytuple)

                listTuples = nrlistTuples


                if listCursor.rowcount == 0:
                    geneListHTML='<font color="red"><i>no sequence lists available - to create a list , just execute a search from the main page</i></font>'
                else:
                    geneListHTML = '<select name="sequencelistids" multiple size=5>\n' + \
                               reduce(lambda x,y:x+'<option value="%s"/> %s (count=%s ,date=%s)\n'%(y[0],y[1],y[2],y[3]) ,listTuples,'') + \
                               '</select>\n'

                sql = """
                select obid,listdefinition,currentmembership ,to_char(createddate,'dd-mm-yyyy') as createddate from oblist where listtype = 'BIOSEQUENCE_LIST' and
                currentmembership > 0 order by obid desc
                """
                listCursor.execute(sql)
                listTuples = listCursor.fetchall()
                if listCursor.rowcount == 0:
                    candidategeneListHTML='<font color="red"><i>no project lists are currently available </i></font>'
                else:
                    candidategeneListHTML = '<select name="candidatesequencelistids" multiple size=5 onChange=\'simplereport.filename.value="extract." + simplereport.outputformat.value; return true;\'>\n' + \
                               reduce(lambda x,y:x+'<option value="%s"/> %s (count=%s, date=%s)\n'%(y[0],y[1],y[2],y[3]) ,listTuples,'') + \
                               '</select>\n'

                    
            finally:
                listCursor.close()        
                if connection != None:
                    connection.close()                
            
            print "Content-Type: text/html\n\n" 
            print report_sequenceextracts%({'geneListHTML' : geneListHTML, 'candidategeneListHTML' : candidategeneListHTML })


        elif self.argDict['page'] == 'report_gbsreports':
            # open a query to get a list of species
            try:
           	connection=databaseModule.getConnection()            	
                listCursor = connection.cursor()
                sql = """
                select lower(species), count(*) from gbskeyfilefact
                where length(case when species is null then '' else ltrim(rtrim(species)) end) > 0
                group by 1 order by 1
                """
                agresearchpagemodulelogger.info("executing %s"%sql)

                listCursor.execute(sql)
                listTuples = listCursor.fetchall()


                if listCursor.rowcount == 0:
                    speciesListHTML='<font color="red"><i>no species available</i></font>'
                else:
                    speciesListHTML = '<select name="species" multiple size=5>\n' + \
                               reduce(lambda x,y:x+'<option value="%s"/> %s (count=%s)\n'%(y[0],y[0],y[1]) ,listTuples,'') + \
                               '</select>\n'
            finally:
                listCursor.close()        
                if connection != None:
                    connection.close()

            # open a query to get a list of runs
            try:
           	connection=databaseModule.getConnection()            	
                listCursor = connection.cursor()
                #sql = """
                #select listname, createddate from biosamplelist where listcomment = 'AgResearch Hiseq Run' order by createddate desc
                #"""
                sql = """
                select listname, createddate from biosamplelist where listcomment = 'AgResearch Hiseq Run' order by 1
                """
                agresearchpagemodulelogger.info("executing %s"%sql)

                listCursor.execute(sql)
                listTuples = listCursor.fetchall()


                if listCursor.rowcount == 0:
                    runListHTML='<font color="red"><i>no runs available</i></font>'
                else:
                    runListHTML = '<select name="runs" multiple size=5>\n' + \
                               reduce(lambda x,y:x+'<option value="%s"/> %s (created=%s)\n'%(y[0],y[0],y[1]) ,listTuples,'') + \
                               '</select>\n'
            finally:
                listCursor.close()        
                if connection != None:
                    connection.close()
                    
            
            print "Content-Type: text/html\n\n" 
            print report_gbsextracts%({'speciesListHTML' : speciesListHTML, 'runListHTML' : runListHTML})

        else:
            errorPage("unknown report request : %s" % self.argDict['page'])

    def doReport(self):
        if self.argDict['reportmenu'] == 'snpannotation1':
            try:
           	connection=databaseModule.getConnection()        	
                reportCursor=connection.cursor()


                if not isinstance(self.argDict['animallists'],ListType):
                    self.argDict['animallists'] = re.split('\n',self.argDict['animallists'])
                    self.argDict['animallists'] = [item.strip() for item in self.argDict['animallists'] if len(item.strip()) > 1]

                maxRows = None
                if 'maxrows' in self.argDict:
                    if re.search('^\s*\d+\s*$',self.argDict['maxrows']) != None:
                       maxRows = int(self.argDict['maxrows'])

                if 'orderbyclause' not in self.argDict:
                    self.argDict.update( {
                       'orderbyclause' : ""
                    })
                if 'outputformat' not in self.argDict:
                    self.argDict.update( {
                       'outputformat' : "html"
                    })

                self.argDict.update( {
                   'classes' : reduce(lambda x,y:x+ '  ' + y,self.argDict['animallists']),
                   'datestamp' : date.isoformat(date.today())
                })



                # set up readable fieldnames
                #fieldNameDict = {
                #}


                # send content type now as this report can time out
                if self.argDict['outputto'] == 'browser':
                    print getReportHeader(onlyContentType=True)
                else:
                    print getDownloadHeader(self.argDict['filename'],onlyContentType=True)


                    
                
                # construct the query - there is a set of 7 columns for each animal class :
                # af(a)
                # af(c)
                # af(g)
                # af(t)
                # maf
                # mafallele
                #
                # Then there is a further column that sums the
                # individual breeds to calculate the following index 
                # The index is that which minimises the sum of squares estimate of the individual breed deviation from a minor allele frequency (MAF)
                # of 0.5 e.g. say a breed has a MAF for SNP A of 0.4 then this would be (0.5-0.4)^2
                # i.e. SNP index =sum across all breeds [0.5-MAF(breed)]^2
                #
                # the allele frequencies are stored in a fact table attached to the
                # genetictestact table , with the xreflsid of the animal list as
                # the factnamespace, and the attribute name being AF_A, AF_G etc
                alleleFrequencyKeys = {
                    "A" : "AF_A",
                    "C" : "AF_C",
                    "G" : "AF_G",
                    "T" : "AF_T",
                    "Unknown" : "AF_Unknown"
                }
                sql = """
                select
                   accession,
                   'http://agbrdf.agresearch.co.nz/cgi-bin/fetch.py?obid='||xreflsid||'&context=default&target=ob' as url,
                   variation,
                """
                for animallist in self.argDict['animallists']:
                    for allele in ['A' , 'C' , 'G' , 'T', 'Unknown']:
                        #sql += """
                        #case when getgenetictestfact2char(obid, '%s', '%s') is null then '0'
                        #else getgenetictestfact2char(obid, '%s', '%s') end as "%s : %s",
                        sql += """
                        getAlleleFrequency(obid, '%s', '%s') as "%s : %s",
                        """%(animallist,allele,animallist, allele)
                    sql += """
                        0 as "%s : MA",
                        '' as "%s : MAF",
                        """%(animallist, animallist)
                sql += """
                0 as mafmoment,
                0 as nclasses,
                0 as mafmomentmean,
                0 as makey
                from
                genetictestfact
                """
                #where xreflsid in ('genetic test.Bovine 30K SNP chip (2006/2007).BTA-107541','genetic test.Bovine 30K SNP chip (2006/2007).BTA-110081')

                agresearchpagemodulelogger.info("executing %s"%str(sql))
                #errorPage(sql)
                reportCursor.execute(sql)                    
                    
                fieldNames = [item[0] for item in reportCursor.description]


                # now construct heading
                reportHeading = """
                    <h1 align=center>SNP Report </h1>
                    <h2 align=center> Animal Classes : %(classes)s
                    <h3 align=center> as at %(datestamp)s </h3>
                """%self.argDict

              
                
                if maxRows != None:
                   reportHeading += "<h3> (Rows limited to %s) </h3>"%maxRows


                
                reportFieldValues = reportCursor.fetchone()


                if self.argDict['outputto'] == 'browser':
                    print getReportHeader(self.argDict['reportmenu'],reportHeading,fieldNames,self.argDict['outputformat'],needContentType=False)
                else:    
                    print getDownloadHeader(self.argDict['filename'],self.argDict['reportmenu'],reportHeading,fieldNames,self.argDict['outputformat'],needContentType=False)

                rowCount = 0
                if self.argDict['outputto'] == 'browser' and self.argDict['outputformat'] != 'html':
                    print '<pre>'                   
                while reportFieldValues != None:
                    fieldDict = dict(zip(fieldNames,reportFieldValues))
                    if maxRows != None:
                        if rowCount >= maxRows:
                            break
                    rowCount += 1

                    # calculate summary stats across classes for this SNP

                    mafmoment = 0.0
                    nclasses = 0
                    makey = ''
                    makeysep=''
                    for animallist in self.argDict['animallists']:
                        AllalleleCounts = [fieldDict["%s : %s"%(animallist,allele)] for allele in ['A' , 'C' , 'G' , 'T', "Unknown"]]
                        alleleCounts = [fieldDict["%s : %s"%(animallist,allele)] for allele in ['A' , 'C' , 'G' , 'T']]
                        alleleCounts = [item for item in alleleCounts if item > 0]
                        if len(alleleCounts) > 0:
                            #maf = min(alleleCounts) / (1.0* reduce(lambda x,y : x+y,AllalleleCounts))
                            maf = min(alleleCounts) / (1.0* reduce(lambda x,y : x+y,alleleCounts))
                            ma = [allele for allele in ['A' , 'C' , 'G' , 'T'] if fieldDict["%s : %s"%(animallist,allele)] == min(alleleCounts)]
                            ma = reduce(lambda x,y:x+y, ma)
                            makey += '%s%s'%(makeysep,ma)
                            makeysep='.'
                            mafmoment += (maf-.5)**2.0
                            nclasses += 1
                            fieldDict["%s : MAF"%(animallist)] = "%4.3f"%maf
                            fieldDict["%s : MA"%(animallist)] = ma
                        else:
                            fieldDict["%s : MAF"%(animallist)] = "-"
                            fieldDict["%s : MA"%(animallist)] = "-"
                    fieldDict['nclasses'] = nclasses
                    fieldDict['mafmoment'] = "%4.3f"%mafmoment
                    if nclasses > 0:
                        fieldDict['mafmomentmean'] = "%4.4f"%(mafmoment / (1.0 * nclasses))
                    else:
                        fieldDict['mafmomentmean'] = '-'
                    fieldDict['makey'] = makey
                    record = '<tr>'
                    if self.argDict['outputformat'] == 'html':
                        fieldDict['url'] = """<a href="%(url)s">%(accession)s</a>"""%fieldDict
                        record+=reduce(lambda x,y: x+'<td>'+str(y)+'</td>', [fieldDict[field] for field in fieldNames],'')
                        print(record+'</tr>\n')   
                    elif self.argDict['outputformat'] == 'csv':
                        record=reduce(lambda x,y: x+'"%s",'%y, [fieldDict[field] for field in fieldNames],'')
                        print record

                    reportFieldValues = reportCursor.fetchone()


                if self.argDict['outputto'] == 'browser':
                    print getReportFooter(rowCount)

                if self.argDict['outputto'] == 'browser' and self.argDict['outputformat'] != 'html':
                    print '</pre>'   


            finally:
                reportCursor.close()        
                if connection != None:
                    connection.close()
        
        
        elif self.argDict['reportmenu'] == 'flankinggenereport1':
            # example URL for linking to this report :
            # http://localhost/cgi-bin/agbrdf/report.py?page=report_locusreports&context=page
            # http://devsheepgenomics.agresearch.co.nz/cgi-bin/sheepgenomics/report.py?reportmenu=flankinggenereport1&cohortmethod=coordinate&mapname=vsheep1.1&mapposition0=10000000&mapposition1=20000000&chromosome=OAR1&context=report&outputto=browser&positionunit=1
            try:
           	connection=databaseModule.getConnection()        	
                reportCursor=connection.cursor()


                if not isinstance(self.argDict['genesymbols'],ListType):
                    self.argDict['genesymbols'] = re.split('\n',self.argDict['genesymbols'])
                    self.argDict['genesymbols'] = [item.strip() for item in self.argDict['genesymbols'] if len(item.strip()) > 1]
                if not isinstance(self.argDict['urltemplates'],ListType):
                    self.argDict['urltemplates'] = re.split('\n',self.argDict['urltemplates'])
                    self.argDict['urltemplates'] = [item.strip() for item in self.argDict['urltemplates'] if len(item.strip()) > 1]

                maxRows = None
                if 'maxrows' in self.argDict:
                    if re.search('^\s*\d+\s*$',self.argDict['maxrows']) != None:
                       maxRows = int(self.argDict['maxrows'])

                if 'orderbyclause' not in self.argDict:
                    self.argDict.update( {
                       'orderbyclause' : " order by gl1.chromosomename, gl1.locationstart "
                    })
                if 'outputformat' not in self.argDict:
                    self.argDict.update( {
                       'outputformat' : "html"
                    })


                # set up readable fieldnames
                fieldNameDict = {
                    'genelsid' : 'Links',
                    'geneticobsymbols' : 'Symbol',
                    'geneticobdescription' : 'Description',
                    'speciesname' : 'Species' ,
                    'entrezgeneid' : 'Entrez Geneid' ,
                    'chromosome' : 'Chromosome' ,
                    'flankinggenestart' : 'Start',
                    'flankinggenestop' : 'Stop',
                    'locationevidence' : 'Evidence',
                    'locationlsid' : 'Location ID'
                }


                # send content type now as this report can time out
                if self.argDict['outputto'] == 'browser':
                    print getReportHeader(onlyContentType=True)
                else:
                    print getDownloadHeader(self.argDict['filename'],onlyContentType=True)


                    
                
                # execute the report query
                if self.argDict['cohortmethod'] == 'genelist':
                    sql = "select listdefinition,obid from oblist where obid = %(genelistid)s"
                    reportCursor.execute(sql,self.argDict)
                    reportFieldValues=reportCursor.fetchone()
                    geneListName = "%s (id=%s)"%tuple(reportFieldValues)
                    self.argDict.update( {
                       'geneListName' : geneListName,
                       'datestamp' : date.isoformat(date.today()),
                       'flanking' : eval(self.argDict['listflankingdistance'] + '*' + self.argDict['listflankingunit']),
                       'listid' : self.argDict['genelistid']
                    })                          
                    sql = reportSQLDict['flankinggenereport1']%self.argDict
                    agresearchpagemodulelogger.info("executing %s"%sql)        
                    reportCursor.execute(sql)
              
                elif self.argDict['cohortmethod'] == 'candidategenelist':
                    sql = "select listdefinition,obid from oblist where obid = %(candidategenelistid)s"
                    reportCursor.execute(sql,self.argDict)
                    reportFieldValues=reportCursor.fetchone()
                    geneListName = "%s (id=%s)"%tuple(reportFieldValues)
                    self.argDict.update( {
                       'geneListName' : geneListName,
                       'datestamp' : date.isoformat(date.today()),
                       'flanking' : eval(self.argDict['candidateflankingdistance'] + '*' + self.argDict['candidateflankingunit']),
                       'listid' : self.argDict['candidategenelistid']
                    })                          
                    sql = reportSQLDict['flankinggenereport1']%self.argDict
                    agresearchpagemodulelogger.info("executing %s"%sql)        
                    reportCursor.execute(sql)         
                elif self.argDict['cohortmethod'] == 'coordinate':
                    self.argDict.update( {
                       'datestamp' : date.isoformat(date.today()),
                       'mapstart' : eval(self.argDict['mapposition0'] + '*' + self.argDict['positionunit']),
                       'mapstop' : eval(self.argDict['mapposition1'] + '*' + self.argDict['positionunit'])
                    })                           
                    sql = reportSQLDict['flankinggenereport2']%self.argDict
                    agresearchpagemodulelogger.info("executing %s"%sql)        
                    reportCursor.execute(sql)
                elif self.argDict['cohortmethod'] == 'genesymbollist':
                    self.argDict.update( {
                       'datestamp' : date.isoformat(date.today()),
                       'flanking' : eval(self.argDict['symbolsflankingdistance'] + '*' + self.argDict['symbolsflankingunit'])
                    })


                    # we need to call the search engine to obtain lists of genes that match the symbol list
                    agresearchpagemodulelogger.info("executing searches on symbols %s"%str(self.argDict['genesymbols'])) 
                    resultLists = []
                    for symbol in self.argDict['genesymbols']:
                        searchCursor = connection.cursor()
                        engineQuery="select getSearchResultList(%(symbol)s,'SYSTEM',%(symbolshitlimit)s,'Genetic Tables',0)"
                        agresearchpagemodulelogger.info("executing select getSearchResultList(%(symbol)s,'SYSTEM',%(symbolshitlimit)s,'Genetic Tables',0)"%{'symbol' : symbol,'symbolshitlimit' : self.argDict['symbolshitlimit']})
                        searchCursor.execute(engineQuery,{'symbol' : symbol, 'symbolshitlimit' : self.argDict['symbolshitlimit']})
                        resultLists.append(searchCursor.fetchone()[0])
                        connection.commit()
                    searchCursor.close()
                    listClause =  re.sub('\]',')',re.sub('\[','(',str(resultLists)))
                    agresearchpagemodulelogger.info('listClause=%s'%listClause)

                    self.argDict.update( {
                        'listclause' : listClause
                    })
                    
                    sql = reportSQLDict['flankinggenereport3']%self.argDict
                    agresearchpagemodulelogger.info("executing %s"%sql)        
                    reportCursor.execute(sql)                    
                    
                fieldNames = [eval({True : 'fieldNameDict[item[0]]' , False : 'item[0]'}[item[0] in fieldNameDict]) for item in reportCursor.description]


                # now construct heading
                if self.argDict['cohortmethod'] == 'genelist':
                    reportHeading = """
                        <h1 align=center>Genetic/GenomicMap Report - Features flanking genes in a specified search list</h1>
                        <h2 align=center> Search list : %(geneListName)s  Flanking distance : %(flanking)s
                        Using map : %(mapname)s </h2> <p/>
                        <h3 align=center> as at %(datestamp)s </h3>
                    """%self.argDict
                elif self.argDict['cohortmethod'] == 'candidategenelist':
                    reportHeading = """
                        <h1 align=center>Genetic / Genomic Map Report - Features flanking genes on a user project list</h1>
                        <h2 align=center> Candidate list : %(geneListName)s  Flanking distance : %(flanking)s
                        Using map : %(mapname)s </h2> <p/>
                        <h3 align=center> as at %(datestamp)s </h3>
                    """%self.argDict                    
                elif self.argDict['cohortmethod'] == 'coordinate':
                    reportHeading = """
                        <h1 align=center>Genetic / Genomic Map Report - Features in a specific region on a map</h1>
                        <h2 align=center> Map : %(mapname)s  Chromosome : %(chromosome)s Between : %(mapstart)s  and %(mapstop)s</h2> <p/>
                        <h3 align=center> as at %(datestamp)s </h3>
                    """%self.argDict
                elif self.argDict['cohortmethod'] == 'genesymbollist':
                    reportHeading = """
                        <h1 align=center>Genetic / Genomic Map Report - Features flanking genes from list of symbols/ keywords</h1>
                        <h2 align=center> Symbol/Keyword list : %(genesymbols)s  Flanking distance : %(flanking)s
                        Using map : %(mapname)s </h2> <p/>
                        <h3 align=center> as at %(datestamp)s </h3>
                    """%self.argDict                          
                
                if maxRows != None:
                   reportHeading += "<h3> (Rows limited to %s) </h3>"%maxRows


                
                reportFieldValues = reportCursor.fetchone()


                if self.argDict['outputto'] == 'browser':
                    print getReportHeader(self.argDict['reportmenu'],reportHeading,fieldNames,self.argDict['outputformat'],needContentType=False)
                else:    
                    print getDownloadHeader(self.argDict['filename'],self.argDict['reportmenu'],reportHeading,fieldNames,self.argDict['outputformat'],needContentType=False)

                rowCount = 0
                while reportFieldValues != None:
                    if maxRows != None:
                        if rowCount >= maxRows:
                            break
                    rowCount += 1

                    record = '<tr>'
                    # hyperlink the first entry which is the gene LSID, to the sheep gene index - e.g.
                    #https://sgpbioinformatics.agresearch.co.nz/cgi-bin/sheepgenomics/fetch.py?obid=2122903&context=geneindex&target=ob
                    # ( also they do not like the geneticob prefix so get rid of it)
                    #if reportFieldValues[0] != None:
                    #    sgilink = """<a href="https://gbrowse.agresearch.co.nz/cgi-bin/sheepgenomics/fetch.py?obid=%s&context=geneindex&target=ob"target="sgipage">%s</a>"""\
                    #              %(reportFieldValues[0],string.join(  re.split('\.',reportFieldValues[0])[1:],'.'))
                    #    reportFieldValues[0] = sgilink
                    #
                    # hyperlink to genome maps
                    # example :
                    # https://sgpbioinformatics.agresearch.co.nz/cgi-bin/sheepgenomics/search.py?viewName=default&obTypeName=Virtual%20Sheep&queryString=OAR1:30420000..30420000
                    #reportFieldValues[0] = "(no links specified)"                    
                    if  self.argDict['urltemplates'] != None:
                        urlset = ''
                        urlcount = 0
                        if len(self.argDict['urltemplates']) >= 1:
                            for urlspec in self.argDict['urltemplates']:
                                urlspec = urlspec.strip()

                                if len(urlspec) == 0:
                                    continue
                                urlcount += 1

                                agresearchpagemodulelogger.info(urlspec)

                                # split into the URL and the display string
                                url = "http:%s"%re.split('http:',urlspec)[1]
                                display = ""
                                if len(re.split('http:',urlspec)) >=2:
                                    display = re.split('http:',urlspec)[0].strip()
                                if len(display) == 0:
                                    display = url

                                # set the reference for the offset
                                startfieldindex = {
                                   'locationstart' : 7,
                                   'locationstop' : 8
                                }[self.argDict['startis']]
                                stopfieldindex = {
                                   'locationstart' : 7,
                                   'locationstop' : 8
                                }[self.argDict['stopis']]


                                
                                
                                if reportFieldValues[6] != None:
                                    url = re.sub('\$CHRNUM',reportFieldValues[6],url)
                                    display = re.sub('\$CHRNUM',reportFieldValues[6],display)
                                    
                                if reportFieldValues[startfieldindex] != None:
                                    chrstart = eval("%s + %s"%(reportFieldValues[startfieldindex], self.argDict['urlstartoffset']))
                                    url = re.sub('\$CHRSTART',str(chrstart),url)
                                    display = re.sub('\$CHRSTART',str(chrstart),display)

                                    if  reportFieldValues[stopfieldindex] != None:
                                        chrstop = eval("%s + %s"%(reportFieldValues[stopfieldindex], self.argDict['urlstopoffset']))
                                        url = re.sub('\$CHRSTOP',str(chrstop),url)
                                        display = re.sub('\$CHRSTOP',str(chrstop),display)
                                        
                                    else:
                                        chrstop = eval("%s + %s"%(reportFieldValues[startfieldindex], self.argDict['urlstopoffset']))
                                        url = re.sub('\$CHRSTOP',str(chrstop),url)
                                        display = re.sub('\$CHRSTOP',str(chrstop),display)

                                if reportFieldValues[1] != None:
                                    gene = re.split('\s+',reportFieldValues[1])[0]
                                    url = re.sub('\$GENE',gene,url)
                                    display = re.sub('\$GENE',gene,display)                                    

                                if reportFieldValues[0] != None:
                                    lsid = reportFieldValues[0]
                                    display = re.sub('\$LSID',lsid,display)
                                    lsid = re.sub('\s','%20',lsid)
                                    url = re.sub('\$LSID',lsid,url)


                                if self.argDict['inlineurl'] != 'yes':
                                    urlset +=  "<a href=%s target=%s>%s</a></br><hr>"%(url,urlcount,display)
                                else:
                                    urlset +=  "<iframe src=%s></iframe></br><hr>"%(url)

                        reportFieldValues[0] = urlset        
                                                    
                            #reportFieldValues[0] += "</table>"
                        #if reportFieldValues[10] in mapURLs:
                        #    linktuple= (reportFieldValues[5],eval("%s - 50000"%reportFieldValues[6]), eval("%s + 50000"%reportFieldValues[6]))
                        #    maplink="<a href=" + mapURLs[reportFieldValues[10]]%linktuple + " target=mapbrowser>" + \
                        #        str(reportFieldValues[6]) + "</a>"
                        #    reportFieldValues[6] = maplink

                    if self.argDict['outputformat'] == 'html':
                        record+=reduce(lambda x,y: x+'<td>'+str(y)+'</td>', reportFieldValues,'')
                        print(record+'</tr>\n')   
                    elif self.argDict['outputformat'] == 'csv':
                        record=reduce(lambda x,y: '"%s"'%x+','+'"%s"'%y, reportFieldValues,'')
                        print record

                    reportFieldValues = reportCursor.fetchone()


                if self.argDict['outputto'] == 'browser':
                    print getReportFooter(rowCount)

                if self.argDict['outputto'] == 'browser' and self.argDict['outputformat'] != 'html':
                    print '</pre>'   


            finally:
                reportCursor.close()        
                if connection != None:
                    connection.close()
        
        elif self.argDict['reportmenu'] == 'genstatmicroarrayextract1':
#
# example genstat extract :
#
#Experimentid!,Experimentname!,Spotid!,Slide_block!,Slide_col!,Slide_row!,Metarow!,Metacol!,ROW!,COL!,EST!,SpotCode!,X!,Y!,Dia,F1Median,F1Mean,F1SD,B1Median,B1Mean,B1SD,B1_PCT_GT_1SD,B1_PCT_GT_2SD,F1_PCT_SAT,F2Median,F2Mean,F2SD,B2Median,B2Mean,B2SD,B2_PCT_GT_1SD,B2_PCT_GT_2SD,F2_PCT_SAT,Ratio_of_Medians,Ratio_of_Means,Median_of_Ratios,Mean_of_Ratios,Ratios_SD,Rgn_Ratio,Rgn_R_SQUARED,F_Pixels,B_Pixels,Sum_of_Medians,Sum_of_Means,Log_Ratio,F1_Median_minus_B1,F2_Median_minus_B2,F1_Mean_minus_B1,F2_Mean_minus_B2,Flags,spotGPRId$
# 
#2159,"107-14 high",883030,1,1,1,1,1,1,1,"kx27PArr56b09",1,780,12490,80,2141,2135,645,724,732,136,100,94,0,1953,2047,513,1045,1071,196,96,87,0,1.561,1.408,1.51,1.446,1.629,1.373,0.767,55,248,2325,2413,0.642,1417,908,1411,1002,0,"kx27PArr56b09"
#2159,"107-14 high",883006,1,2,1,1,1,1,2,"kx27PArr56b05",1,940,12480,100,20946,23989,15169,761,778,148,100,100,0,6985,6621,3238,1055,1084,251,100,100,0,3.404,4.173,4.011,3.972,1.327,4.449,0.95,88,347,26115,28794,1.767,20185,5930,23228,5566,0,"kx27PArr56b05"
#2159,"107-14 high",882982,1,3,1,1,1,1,3,"kx27PArr56b01",1,1100,12480,100,2324,2536,996,754,765,136,100,100,0,2614,3015,1241,1042,1072,229,100,97,0,0.999,0.903,0.89,0.936,1.453,0.868,0.835,81,353,3142,3755,-0.002,1570,1572,1782,1973,0,"kx27PArr56b01"
#2159,"107-14 high",882958,1,4,1,1,1,1,4,"kx19FLrr56h09",1,1250,12480,90,3970,4090,1595,742,768,160,100,100,0,4230,4492,1719,1030,1058,208,100,100,0,1.009,0.967,0.97,0.976,1.246,0.953,0.942,53,300,6428,6810,0.013,3228,3200,3348,3462,0,"kx19FLrr56h09"
#2159,"107-14 high",882934,1,5,1,1,1,1,5,"kx19FLrr56h05",1,1420,12480,90,2996,2916,882,748,787,237,100,100,0,2947,2877,873,1072,1120,326,93,90,0,1.199,1.201,1.161,1.223,1.498,1.148,0.86,60,303,4123,3973,0.262,2248,1875,2168,1805,0,"kx19FLrr56h05"
#
# This report assumes the following ontology has been set up :
#insert into ontologyob(ontologyName,  xreflsid , ontologyDescription )
#values('Agilent.012694_D_20050902.gal DataFields','Agilent.012694_D_20050902.gal.ontology','This ontology provides mappings of fieldnames from the GPR and GAL files to other formats');
#insert into ontologyTermFact(ontologyOb,termName, termDescription) select obid,'Primer' from ontologyOb where ontologyName = 'Agilent.012694_D_20050902.gal DataFields';
#insert into ontologyTermFact(ontologyOb,termName) select obid,'Forward Primer' from ontologyOb where ontologyName = 'LABRESOURCE_TYPES';
#insert into ontologyTermFact(ontologyOb,termName) select obid,'Reverse Primer' from ontologyOb where ontologyName = 'LABRESOURCE_TYPES';
#insert into ontologyTermFact(ontologyOb,termName) select obid,'Cloning Vector' from ontologyOb where ontologyName = 'LABRESOURCE_TYPES';
#insert into ontologyTermFact(ontologyOb,termName) select obid,'Sequencing Vector' from ontologyOb where ontologyName = 'LABRESOURCE_TYPES';
#insert into ontologyTermFact(ontologyOb,termName) select obid,'Genotype SNP' from ontologyOb where ontologyName = 'LABRESOURCE_TYPES';
#commit;
# gpr fields
#gpr_block gpr_column gpr_row gpr_name gpr_id gpr_x gpr_y gpr_dia. gpr_f635 median gpr_f635 mean gpr_f635 sd gpr_b635 median gpr_b635 mean gpr_b635 sd gpr_% > b635+1sd gpr_% > b635+2sd gpr_f635 % sat. gpr_f532 median gpr_f532 mean gpr_f532 sd gpr_b532 median gpr_b532 mean gpr_b532 sd gpr_% > b532+1sd gpr_% > b532+2sd gpr_f532 % sat. gpr_ratio of medians gpr_ratio of means gpr_median of ratios gpr_mean of ratios gpr_ratios sd gpr_rgn ratio gpr_rgn rsquared gpr_f pixels gpr_b pixels gpr_sum of medians gpr_sum of means gpr_log ratio gpr_f635 median - b635 gpr_f532 median - b532 gpr_f635 mean - b635 gpr_f532 mean - b532 gpr_flags


#
            try:
           	connection=databaseModule.getConnection()        	
                reportCursor=connection.cursor()


                if re.search('^\s*\d+\s*$',self.argDict['maxrows']) != None:
                    maxRows = int(self.argDict['maxrows'])
                else:
                    maxRows = None
                

                # make sure multi-select fields are multi
                if not isinstance(self.argDict['experiments'],ListType):
                    self.argDict['experiments'] = [int(item) for item in [self.argDict['experiments']]]

                # now construct heading
                if self.argDict['outputto'] == 'browser':
                    if maxRows == None:
                        reportHeading = """
                        <h1 align=center>Report : %s</h1>
                        <h2 align=center> Limits : Experiments %s </h2>
                        <h3 align=center> as at %s </h3>"""\
                                    %(self.argDict['reportmenu'],self.argDict['experiments'],date.isoformat(date.today()))
                    else:
                        reportHeading = """
                        <h1 align=center>Report : %s</h1>
                        <h2 align=center> Limits : Experiments %s </h2>
                        <h2 align=center> <font color="red"> Rows limited to %s </font> </h2>                      
                        <h3 align=center> as at %s </h3>"""\
                                    %(self.argDict['reportmenu'],self.argDict['experiments'],maxRows,date.isoformat(date.today()))
                else:
                    if maxRows == None:
                        #reportHeading = """Report : %s Limits : Experiments %s  : as at %s"""\
                        #            %(self.argDict['reportmenu'],self.argDict['experiments'],date.isoformat(date.today()))
                        reportHeading = ""
                        
                    else:
                        reportHeading = """Report : %s Limits : Experiments %s  : Rows limited to %s : as at %s"""\
                                    %(self.argDict['reportmenu'],self.argDict['experiments'],maxRows,date.isoformat(date.today()))

                reportFieldNames = ['Experimentid!','Experimentname!','Spotid!','Slide_block!','Slide_col!','Slide_row!',\
                                    'Metarow!','Metacol!','ROW!','COL!','EST!','SpotCode!','X!','Y!','Dia','F1Median',\
                                    'F1Mean','F1SD','B1Median','B1Mean','B1SD','B1_PCT_GT_1SD','B1_PCT_GT_2SD','F1_PCT_SAT',\
                                    'F2Median','F2Mean','F2SD','B2Median','B2Mean','B2SD','B2_PCT_GT_1SD','B2_PCT_GT_2SD','F2_PCT_SAT',\
                                    'Ratio_of_Medians','Ratio_of_Means','Median_of_Ratios','Mean_of_Ratios','Ratios_SD','Rgn_Ratio',\
                                    'Rgn_R_SQUARED','F_Pixels','B_Pixels','Sum_of_Medians','Sum_of_Means','Log_Ratio','F1_Median_minus_B1',\
                                    'F2_Median_minus_B2','F1_Mean_minus_B1','F2_Mean_minus_B2','Flags','spotGPRId$']


            

                experimentCount = 0
                globalrowCount = 0
                for experiment in self.argDict['experiments']:


                    study = geneExpressionStudy()
                    study.initFromDatabase(int(experiment),connection)
                    rawFieldNames = re.split('\t',study.databaseFields['GPRColumnHeadings'])

                                
                    # execute the report query
                    query = reportSQLDict[self.argDict['reportmenu']]%{
                        'microarraystudy' : experiment
                    }
                    agresearchpagemodulelogger.info("genstatmicroarrayextract executing %s"%str(query))
                    
                    reportCursor.execute(query)
                    fieldNames = [item[0] for item in reportCursor.description]

                    if experimentCount == 0:
                        if self.argDict['outputto'] == 'browser':
                            print getReportHeader(self.argDict['reportmenu'],reportHeading,reportFieldNames,self.argDict['outputformat'])
                        else:    
                            print getDownloadHeader(self.argDict['filename'],self.argDict['reportmenu'],reportHeading,reportFieldNames,self.argDict['outputformat'])                        
       

                    reportFieldValues = reportCursor.fetchone()

                    experimentCount += 1


                    
                    # if output is to file , head up each experiment
                    #if self.argDict['outputto'] == 'file' :
                    #    print "BEGIN experiment %s"%study.databaseFields['xreflsid']
                    
                    rowCount = 0
                    while reportFieldValues != None:
                        if maxRows != None:
                            if rowCount >= maxRows:
                                break
                        rowCount += 1
                        globalrowCount += 1

                        reportDict = dict(zip(fieldNames,reportFieldValues))
                        rawFieldDict = dict(zip(rawFieldNames,[item.strip() for item in re.split('\t',reportDict['rawdatarecord'])]))
                        agresearchpagemodulelogger.info(str(rawFieldDict))

                        # update the reportDict with values from the raw data record
                        reportDict.update({
                            'Experimentname!' : '"%s"'%study.databaseFields['xreflsid'],
                            'ROW!' : rawFieldDict['gpr_row'],
                            'COL!' : rawFieldDict['gpr_column'],
                            'EST!' : rawFieldDict['gpr_name'],
                            'SpotCode!' : 1,
                            'X!' : rawFieldDict['gpr_x'],
                            'Y!' : rawFieldDict['gpr_y'],
                            'Dia' : rawFieldDict['gpr_dia.'],
                            'F1Median' : rawFieldDict['gpr_f635 median'],
                            'F1Mean' : rawFieldDict['gpr_f635 mean'],
                            'F1SD' : rawFieldDict['gpr_f635 sd'],
                            'B1Median' : rawFieldDict['gpr_b635 median'],
                            'B1Mean' : rawFieldDict['gpr_b635 mean'],
                            'B1SD' : rawFieldDict['gpr_b635 sd'],
                            'B1_PCT_GT_1SD' : rawFieldDict['gpr_% > b635+1sd'],
                            'B1_PCT_GT_2SD' : rawFieldDict['gpr_% > b635+2sd'],
                            'F1_PCT_SAT' : rawFieldDict['gpr_f635 % sat.'],
                            'F2Median' : rawFieldDict['gpr_f532 median'],
                            'F2Mean' : rawFieldDict['gpr_f532 mean'],
                            'F2SD' : rawFieldDict['gpr_f532 sd'],
                            'B2Median' : rawFieldDict['gpr_b532 median'],
                            'B2Mean' : rawFieldDict['gpr_b532 mean'],
                            'B2SD' : rawFieldDict['gpr_b532 sd'],
                            'B2_PCT_GT_1SD' : rawFieldDict['gpr_% > b532+1sd'],
                            'B2_PCT_GT_2SD' : rawFieldDict['gpr_% > b532+2sd'],
                            'F2_PCT_SAT' : rawFieldDict['gpr_f532 % sat.'],
                            'Ratio_of_Medians' : eval({True : "rawFieldDict['gpr_ratio of medians']", False : "'gpr_ratio of medians:GPR Parse Error'"}['gpr_ratio of medians' in rawFieldDict]),
                            'Ratio_of_Means' : eval({True : "rawFieldDict['gpr_ratio of means']", False : "'gpr_ratio of means:GPR Parse Error'"}['gpr_ratio of means' in rawFieldDict]),
                            'Median_of_Ratios' : eval({True : "rawFieldDict['gpr_median of ratios']", False : "'gpr_median of ratios:GPR Parse Error'"}['gpr_median of ratios' in rawFieldDict]),
                            'Mean_of_Ratios' : eval({True : "rawFieldDict['gpr_mean of ratios']", False : "'gpr_mean of ratios:GPR Parse Error'"}['gpr_mean of ratios' in rawFieldDict]),
                            'Ratios_SD' : eval({True : "rawFieldDict['gpr_ratios sd']", False : "'gpr_ratios sd:GPR Parse Error'"}['gpr_ratios sd' in rawFieldDict]),
                            'Rgn_Ratio' : eval({True : "rawFieldDict['gpr_rgn ratio']", False : "'gpr_rgn ratio:GPR Parse Error'"}['gpr_rgn ratio' in rawFieldDict]),
                            'Rgn_R_SQUARED' : eval({True : "rawFieldDict['gpr_rgn rsquared']", False : "'gpr_rgn rsquared:GPR Parse Error'"}['gpr_rgn rsquared' in rawFieldDict]),
                            'F_Pixels' : rawFieldDict['gpr_f pixels'],
                            'B_Pixels' : rawFieldDict['gpr_b pixels'],
                            'Sum_of_Medians' : eval({True : "rawFieldDict['gpr_sum of medians']", False : "'gpr_sum of medians:GPR Parse Error'"}['gpr_sum of medians' in rawFieldDict]),
                            'Sum_of_Means' : eval({True : "rawFieldDict['gpr_sum of means']", False : "'gpr_sum of means:GPR Parse Error'"}['gpr_sum of means' in rawFieldDict]),
                            'Log_Ratio' : eval({True : "rawFieldDict['gpr_log ratio']", False : "'gpr_log ratio:GPR Parse Error'"}['gpr_log ratio' in rawFieldDict]),
                            'F1_Median_minus_B1' : rawFieldDict['gpr_f635 median - b635'],
                            'F2_Median_minus_B2' : rawFieldDict['gpr_f532 median - b532'],
                            'F1_Mean_minus_B1' : rawFieldDict['gpr_f635 mean - b635'],
                            'F2_Mean_minus_B2' : rawFieldDict['gpr_f532 mean - b532'],
                            'Flags' : rawFieldDict['gpr_flags'],
                            'spotGPRId$' : rawFieldDict['gpr_id']
                        })

                        # now apply various rules to attempt to parse values using different field names
                        # some fields are named with a suffix (635/532)
                        for key in reportDict.keys():
                            if isinstance(reportDict[key],StringType):
                                keyTokens = re.split(':',reportDict[key])
                                if len(keyTokens) >= 2:
                                    if keyTokens[1]  == 'GPR Parse Error':
                                        if keyTokens[0] == 'gpr_rgn rsquared':
                                           altname = 'gpr_rgn r2 (635/532)'
                                        else:
                                           altname = "%s (635/532)"%keyTokens[0]
                                        reportDict[key] = eval({True : "rawFieldDict[altname]", False : "'%s:GPR Parse Error'%altname"}[altname in rawFieldDict])
                                        # try (532/635) if we still can't parse
                                        if re.search('\:GPR Parse Error',reportDict[key]):
                                            altname = "%s (532/635)"%keyTokens[0]
                                            reportDict[key] = eval({True : "rawFieldDict[altname]", False : "'%s:GPR Parse Error'%altname"}[altname in rawFieldDict])
     


                                

                        #,COL!,EST!,SpotCode!,X!,Y!,Dia,F1Median,F1Mean,F1SD,B1Median,B1Mean,B1SD,B1_PCT_GT_1SD,B1_PCT_GT_2SD,F1_PCT_SAT,F2Median,F2Mean,F2SD,B2Median,B2Mean,B2SD,B2_PCT_GT_1SD,B2_PCT_GT_2SD,F2_PCT_SAT,Ratio_of_Medians,Ratio_of_Means,Median_of_Ratios,Mean_of_Ratios,Ratios_SD,Rgn_Ratio,Rgn_R_SQUARED,F_Pixels,B_Pixels,Sum_of_Medians,Sum_of_Means,Log_Ratio,F1_Median_minus_B1,F2_Median_minus_B2,F1_Mean_minus_B1,F2_Mean_minus_B2,Flags,spotGPRId$
                        # #gpr_block gpr_column gpr_row gpr_name gpr_id gpr_x gpr_y gpr_dia. gpr_f635 median gpr_f635 mean gpr_f635 sd gpr_b635 median gpr_b635 mean gpr_b635 sd gpr_% > b635+1sd gpr_% > b635+2sd gpr_f635 % sat. gpr_f532 median gpr_f532 mean gpr_f532 sd gpr_b532 median gpr_b532 mean gpr_b532 sd gpr_% > b532+1sd gpr_% > b532+2sd gpr_f532 % sat. gpr_ratio of medians gpr_ratio of means gpr_median of ratios gpr_mean of ratios gpr_ratios sd gpr_rgn ratio gpr_rgn rsquared gpr_f pixels gpr_b pixels gpr_sum of medians gpr_sum of means gpr_log ratio gpr_f635 median - b635 gpr_f532 median - b532 gpr_f635 mean - b635 gpr_f532 mean - b532 gpr_flags

                        reportFieldValues = [reportDict[field] for field in reportFieldNames]
                        
                        if self.argDict['outputformat'] == 'html':
                            record = '<tr>'
                            record+=reduce(lambda x,y: x+'<td>'+str(y)+'</td>', reportFieldValues,'')
                            print(record+'</tr>\n')
                        elif self.argDict['outputformat'] == 'csv':
                            record=reduce(lambda x,y: x+','+str(y), reportFieldValues,'')
                            record = re.sub('^,','',record)
                            print record
                        
                        reportFieldValues = reportCursor.fetchone()


                if self.argDict['outputto'] == 'browser':
                    print getReportFooter(globalrowCount)

            finally:
                reportCursor.close()        
                if connection != None:
                    connection.close()

                    
        elif self.argDict['reportmenu'] == 'flagsummary1':
        # this report executes the same query as the raw extract, but summarises the information
#
# example genstat extract :
#
#Experimentid!,Experimentname!,Spotid!,Slide_block!,Slide_col!,Slide_row!,Metarow!,Metacol!,ROW!,COL!,EST!,SpotCode!,X!,Y!,Dia,F1Median,F1Mean,F1SD,B1Median,B1Mean,B1SD,B1_PCT_GT_1SD,B1_PCT_GT_2SD,F1_PCT_SAT,F2Median,F2Mean,F2SD,B2Median,B2Mean,B2SD,B2_PCT_GT_1SD,B2_PCT_GT_2SD,F2_PCT_SAT,Ratio_of_Medians,Ratio_of_Means,Median_of_Ratios,Mean_of_Ratios,Ratios_SD,Rgn_Ratio,Rgn_R_SQUARED,F_Pixels,B_Pixels,Sum_of_Medians,Sum_of_Means,Log_Ratio,F1_Median_minus_B1,F2_Median_minus_B2,F1_Mean_minus_B1,F2_Mean_minus_B2,Flags,spotGPRId$
# 
#2159,"107-14 high",883030,1,1,1,1,1,1,1,"kx27PArr56b09",1,780,12490,80,2141,2135,645,724,732,136,100,94,0,1953,2047,513,1045,1071,196,96,87,0,1.561,1.408,1.51,1.446,1.629,1.373,0.767,55,248,2325,2413,0.642,1417,908,1411,1002,0,"kx27PArr56b09"
#2159,"107-14 high",883006,1,2,1,1,1,1,2,"kx27PArr56b05",1,940,12480,100,20946,23989,15169,761,778,148,100,100,0,6985,6621,3238,1055,1084,251,100,100,0,3.404,4.173,4.011,3.972,1.327,4.449,0.95,88,347,26115,28794,1.767,20185,5930,23228,5566,0,"kx27PArr56b05"
#2159,"107-14 high",882982,1,3,1,1,1,1,3,"kx27PArr56b01",1,1100,12480,100,2324,2536,996,754,765,136,100,100,0,2614,3015,1241,1042,1072,229,100,97,0,0.999,0.903,0.89,0.936,1.453,0.868,0.835,81,353,3142,3755,-0.002,1570,1572,1782,1973,0,"kx27PArr56b01"
#2159,"107-14 high",882958,1,4,1,1,1,1,4,"kx19FLrr56h09",1,1250,12480,90,3970,4090,1595,742,768,160,100,100,0,4230,4492,1719,1030,1058,208,100,100,0,1.009,0.967,0.97,0.976,1.246,0.953,0.942,53,300,6428,6810,0.013,3228,3200,3348,3462,0,"kx19FLrr56h09"
#2159,"107-14 high",882934,1,5,1,1,1,1,5,"kx19FLrr56h05",1,1420,12480,90,2996,2916,882,748,787,237,100,100,0,2947,2877,873,1072,1120,326,93,90,0,1.199,1.201,1.161,1.223,1.498,1.148,0.86,60,303,4123,3973,0.262,2248,1875,2168,1805,0,"kx19FLrr56h05"
#
# This report assumes the following ontology has been set up :
#insert into ontologyob(ontologyName,  xreflsid , ontologyDescription )
#values('Agilent.012694_D_20050902.gal DataFields','Agilent.012694_D_20050902.gal.ontology','This ontology provides mappings of fieldnames from the GPR and GAL files to other formats');
#insert into ontologyTermFact(ontologyOb,termName, termDescription) select obid,'Primer' from ontologyOb where ontologyName = 'Agilent.012694_D_20050902.gal DataFields';
#insert into ontologyTermFact(ontologyOb,termName) select obid,'Forward Primer' from ontologyOb where ontologyName = 'LABRESOURCE_TYPES';
#insert into ontologyTermFact(ontologyOb,termName) select obid,'Reverse Primer' from ontologyOb where ontologyName = 'LABRESOURCE_TYPES';
#insert into ontologyTermFact(ontologyOb,termName) select obid,'Cloning Vector' from ontologyOb where ontologyName = 'LABRESOURCE_TYPES';
#insert into ontologyTermFact(ontologyOb,termName) select obid,'Sequencing Vector' from ontologyOb where ontologyName = 'LABRESOURCE_TYPES';
#insert into ontologyTermFact(ontologyOb,termName) select obid,'Genotype SNP' from ontologyOb where ontologyName = 'LABRESOURCE_TYPES';
#commit;
# gpr fields
#gpr_block gpr_column gpr_row gpr_name gpr_id gpr_x gpr_y gpr_dia. gpr_f635 median gpr_f635 mean gpr_f635 sd gpr_b635 median gpr_b635 mean gpr_b635 sd gpr_% > b635+1sd gpr_% > b635+2sd gpr_f635 % sat. gpr_f532 median gpr_f532 mean gpr_f532 sd gpr_b532 median gpr_b532 mean gpr_b532 sd gpr_% > b532+1sd gpr_% > b532+2sd gpr_f532 % sat. gpr_ratio of medians gpr_ratio of means gpr_median of ratios gpr_mean of ratios gpr_ratios sd gpr_rgn ratio gpr_rgn rsquared gpr_f pixels gpr_b pixels gpr_sum of medians gpr_sum of means gpr_log ratio gpr_f635 median - b635 gpr_f532 median - b532 gpr_f635 mean - b635 gpr_f532 mean - b532 gpr_flags


#
            try:
           	connection=databaseModule.getConnection()        	
                reportCursor=connection.cursor()


                if re.search('^\s*\d+\s*$',self.argDict['maxrows']) != None:
                    maxRows = int(self.argDict['maxrows'])
                else:
                    maxRows = None
                

                # make sure multi-select fields are multi
                if not isinstance(self.argDict['experiments'],ListType):
                    self.argDict['experiments'] = [int(item) for item in [self.argDict['experiments']]]

                # now construct heading
                if self.argDict['outputto'] == 'browser':
                    if maxRows == None:
                        reportHeading = """
                        <h1 align=center>Report : %s</h1>
                        <h2 align=center> Limits : Experiments %s </h2>
                        <h3 align=center> as at %s </h3>"""\
                                    %(self.argDict['reportmenu'],self.argDict['experiments'],date.isoformat(date.today()))
                    else:
                        reportHeading = """
                        <h1 align=center>Report : %s</h1>
                        <h2 align=center> Limits : Experiments %s </h2>
                        <h2 align=center> <font color="red"> Rows limited to %s </font> </h2>                      
                        <h3 align=center> as at %s </h3>"""\
                                    %(self.argDict['reportmenu'],self.argDict['experiments'],maxRows,date.isoformat(date.today()))
                else:
                    if maxRows == None:
                        #reportHeading = """Report : %s Limits : Experiments %s  : as at %s"""\
                        #            %(self.argDict['reportmenu'],self.argDict['experiments'],date.isoformat(date.today()))
                        reportHeading = ""
                        
                    else:
                        reportHeading = """Report : %s Limits : Experiments %s  : Rows limited to %s : as at %s"""\
                                    %(self.argDict['reportmenu'],self.argDict['experiments'],maxRows,date.isoformat(date.today()))


                experimentCount = 0
                globalrowCount = 0
                reportstats = {}


                standardFlags = ['0','-100','-50','50','100']
                reportFieldNames = ['Slide'] + ['Flag : %s'%flag for flag in standardFlags]

                if self.argDict['outputto'] == 'browser':
                    print getReportHeader(self.argDict['reportmenu'],reportHeading,reportFieldNames,self.argDict['outputformat'])
                else:    
                    print getDownloadHeader(self.argDict['filename'],self.argDict['reportmenu'],reportHeading,reportFieldNames,self.argDict['outputformat'])                        
                for experiment in self.argDict['experiments']:


                    study = geneExpressionStudy()
                    study.initFromDatabase(int(experiment),connection)
                    rawFieldNames = re.split('\t',study.databaseFields['GPRColumnHeadings'])

                                
                    # execute the report query
                    query = reportSQLDict['microarraysummary1']%{
                        'microarraystudy' : experiment
                    }
                    agresearchpagemodulelogger.info("genstatmicroarrayextract executing %s"%str(query))
                    
                    reportCursor.execute(query)
                    fieldNames = [item[0] for item in reportCursor.description]

                    reportFieldValues = reportCursor.fetchone()

                    experimentCount += 1

                    
                    rowCount = 0
                    slidestats = {
                        'Flags' : {}
                    }
                    while reportFieldValues != None:
                        if maxRows != None:
                            if rowCount >= maxRows:
                                break
                        rowCount += 1
                        globalrowCount += 1

                        reportDict = dict(zip(fieldNames,reportFieldValues))
                        rawFieldDict = dict(zip(rawFieldNames,[item.strip() for item in re.split('\t',reportDict['rawdatarecord'])]))
                        #rawFieldDict = dict(zip(rawFieldNames,re.split('\t',reportDict['rawdatarecord'])))
                        agresearchpagemodulelogger.info(str(rawFieldDict))

                        # update the reportDict with values from the raw data record
                        reportDict.update({
                            'Experimentname!' : '"%s"'%study.databaseFields['xreflsid'],
                            'ROW!' : rawFieldDict['gpr_row'],
                            'COL!' : rawFieldDict['gpr_column'],
                            'EST!' : rawFieldDict['gpr_name'],
                            'SpotCode!' : 1,
                            'X!' : rawFieldDict['gpr_x'],
                            'Y!' : rawFieldDict['gpr_y'],
                            'Dia' : rawFieldDict['gpr_dia.'],
                            'F1Median' : rawFieldDict['gpr_f635 median'],
                            'F1Mean' : rawFieldDict['gpr_f635 mean'],
                            'F1SD' : rawFieldDict['gpr_f635 sd'],
                            'B1Median' : rawFieldDict['gpr_b635 median'],
                            'B1Mean' : rawFieldDict['gpr_b635 mean'],
                            'B1SD' : rawFieldDict['gpr_b635 sd'],
                            'B1_PCT_GT_1SD' : rawFieldDict['gpr_% > b635+1sd'],
                            'B1_PCT_GT_2SD' : rawFieldDict['gpr_% > b635+2sd'],
                            'F1_PCT_SAT' : rawFieldDict['gpr_f635 % sat.'],
                            'F2Median' : rawFieldDict['gpr_f532 median'],
                            'F2Mean' : rawFieldDict['gpr_f532 mean'],
                            'F2SD' : rawFieldDict['gpr_f532 sd'],
                            'B2Median' : rawFieldDict['gpr_b532 median'],
                            'B2Mean' : rawFieldDict['gpr_b532 mean'],
                            'B2SD' : rawFieldDict['gpr_b532 sd'],
                            'B2_PCT_GT_1SD' : rawFieldDict['gpr_% > b532+1sd'],
                            'B2_PCT_GT_2SD' : rawFieldDict['gpr_% > b532+2sd'],
                            'F2_PCT_SAT' : rawFieldDict['gpr_f532 % sat.'],
                            'Ratio_of_Medians' : eval({True : "rawFieldDict['gpr_ratio of medians']", False : "'gpr_ratio of medians:GPR Parse Error'"}['gpr_ratio of medians' in rawFieldDict]),
                            'Ratio_of_Means' : eval({True : "rawFieldDict['gpr_ratio of means']", False : "'gpr_ratio of means:GPR Parse Error'"}['gpr_ratio of means' in rawFieldDict]),
                            'Median_of_Ratios' : eval({True : "rawFieldDict['gpr_median of ratios']", False : "'gpr_median of ratios:GPR Parse Error'"}['gpr_median of ratios' in rawFieldDict]),
                            'Mean_of_Ratios' : eval({True : "rawFieldDict['gpr_mean of ratios']", False : "'gpr_mean of ratios:GPR Parse Error'"}['gpr_mean of ratios' in rawFieldDict]),
                            'Ratios_SD' : eval({True : "rawFieldDict['gpr_ratios sd']", False : "'gpr_ratios sd:GPR Parse Error'"}['gpr_ratios sd' in rawFieldDict]),
                            'Rgn_Ratio' : eval({True : "rawFieldDict['gpr_rgn ratio']", False : "'gpr_rgn ratio:GPR Parse Error'"}['gpr_rgn ratio' in rawFieldDict]),
                            'Rgn_R_SQUARED' : eval({True : "rawFieldDict['gpr_rgn rsquared']", False : "'gpr_rgn rsquared:GPR Parse Error'"}['gpr_rgn rsquared' in rawFieldDict]),
                            'F_Pixels' : rawFieldDict['gpr_f pixels'],
                            'B_Pixels' : rawFieldDict['gpr_b pixels'],
                            'Sum_of_Medians' : eval({True : "rawFieldDict['gpr_sum of medians']", False : "'gpr_sum of medians:GPR Parse Error'"}['gpr_sum of medians' in rawFieldDict]),
                            'Sum_of_Means' : eval({True : "rawFieldDict['gpr_sum of means']", False : "'gpr_sum of means:GPR Parse Error'"}['gpr_sum of means' in rawFieldDict]),
                            'Log_Ratio' : eval({True : "rawFieldDict['gpr_log ratio']", False : "'gpr_log ratio:GPR Parse Error'"}['gpr_log ratio' in rawFieldDict]),
                            'F1_Median_minus_B1' : rawFieldDict['gpr_f635 median - b635'],
                            'F2_Median_minus_B2' : rawFieldDict['gpr_f532 median - b532'],
                            'F1_Mean_minus_B1' : rawFieldDict['gpr_f635 mean - b635'],
                            'F2_Mean_minus_B2' : rawFieldDict['gpr_f532 mean - b532'],
                            'Flags' : rawFieldDict['gpr_flags'],
                            'spotGPRId$' : rawFieldDict['gpr_id']
                        })

                        # now apply various rules to attempt to parse values using different field names
                        # some fields are named with a suffix (635/532)
                        for key in reportDict.keys():
                            if isinstance(reportDict[key],StringType):
                                keyTokens = re.split(':',reportDict[key])
                                if len(keyTokens) >= 2:
                                    if keyTokens[1]  == 'GPR Parse Error':
                                        if keyTokens[0] == 'gpr_rgn rsquared':
                                           altname = 'gpr_rgn r2 (635/532)'
                                        else:
                                           altname = "%s (635/532)"%keyTokens[0]
                                        reportDict[key] = eval({True : "rawFieldDict[altname]", False : "'%s:GPR Parse Error'%altname"}[altname in rawFieldDict])

                                

                        #,COL!,EST!,SpotCode!,X!,Y!,Dia,F1Median,F1Mean,F1SD,B1Median,B1Mean,B1SD,B1_PCT_GT_1SD,B1_PCT_GT_2SD,F1_PCT_SAT,F2Median,F2Mean,F2SD,B2Median,B2Mean,B2SD,B2_PCT_GT_1SD,B2_PCT_GT_2SD,F2_PCT_SAT,Ratio_of_Medians,Ratio_of_Means,Median_of_Ratios,Mean_of_Ratios,Ratios_SD,Rgn_Ratio,Rgn_R_SQUARED,F_Pixels,B_Pixels,Sum_of_Medians,Sum_of_Means,Log_Ratio,F1_Median_minus_B1,F2_Median_minus_B2,F1_Mean_minus_B1,F2_Mean_minus_B2,Flags,spotGPRId$
                        # #gpr_block gpr_column gpr_row gpr_name gpr_id gpr_x gpr_y gpr_dia. gpr_f635 median gpr_f635 mean gpr_f635 sd gpr_b635 median gpr_b635 mean gpr_b635 sd gpr_% > b635+1sd gpr_% > b635+2sd gpr_f635 % sat. gpr_f532 median gpr_f532 mean gpr_f532 sd gpr_b532 median gpr_b532 mean gpr_b532 sd gpr_% > b532+1sd gpr_% > b532+2sd gpr_f532 % sat. gpr_ratio of medians gpr_ratio of means gpr_median of ratios gpr_mean of ratios gpr_ratios sd gpr_rgn ratio gpr_rgn rsquared gpr_f pixels gpr_b pixels gpr_sum of medians gpr_sum of means gpr_log ratio gpr_f635 median - b635 gpr_f532 median - b532 gpr_f635 mean - b635 gpr_f532 mean - b532 gpr_flags

                        
                        #if self.argDict['outputformat'] == 'html':
                        #    record = '<tr>'
                        #    record+=reduce(lambda x,y: x+'<td>'+str(y)+'</td>', reportFieldValues,'')
                        #    print(record+'</tr>\n')
                        #elif self.argDict['outputformat'] == 'csv':
                        #    record=reduce(lambda x,y: x+','+str(y), reportFieldValues,'')
                        #    record = re.sub('^,','',record)
                        #    print record

                        # summarise flags
                        if reportDict['Flags'] not in slidestats['Flags']:
                            slidestats['Flags'][reportDict['Flags']] = 1
                        else: 
                            slidestats['Flags'][reportDict['Flags']] += 1
                        
                        
                        reportFieldValues = reportCursor.fetchone()
                    # end of while fieldvalues none block
                    reportstats[study.databaseFields['xreflsid']] = slidestats

                    # output record
                    record = '<tr><td>%s</td>\n'%study.databaseFields['xreflsid']
                    for flag in standardFlags:
                        if flag in slidestats['Flags'].keys():
                            record += '<td>%s</td>\n'%slidestats['Flags'][flag]
                        else:
                            record += '<td>0</td>\n'
                    record += '</tr>\n'
                    print(record)



                # end of for-experiment block

                #finally get all the flags found
                flagsFound = {}
                for stats in reportstats.values():
                    for flag in stats['Flags'].keys():
                        if flag not in flagsFound:
                            flagsFound[flag] = stats['Flags'][flag]
                        else:
                            flagsFound[flag] += stats['Flags'][flag]

                print getReportFooter(None,'Overall flag counts : %s'%str(flagsFound))



            finally:
                reportCursor.close()        
                if connection != None:
                    connection.close()

        elif self.argDict['reportmenu'] == 'genstatnormalisationextract1':
            try:
           	connection=databaseModule.getConnection()        	
                reportCursor=connection.cursor()


                if re.search('^\s*\d+\s*$',self.argDict['maxrows']) != None:
                    maxRows = int(self.argDict['maxrows'])
                else:
                    maxRows = None
                

                # make sure multi-select fields are multi
                if not isinstance(self.argDict['experiments'],ListType):
                    self.argDict['experiments'] = [int(item) for item in [self.argDict['experiments']]]

                # now construct heading
                if self.argDict['outputto'] == 'browser':
                    if maxRows == None:
                        reportHeading = """
                        <h1 align=center>Report : %s</h1>
                        <h2 align=center> Limits : Experiments %s </h2>
                        <h3 align=center> as at %s </h3>"""\
                                    %(self.argDict['reportmenu'],self.argDict['experiments'],date.isoformat(date.today()))
                    else:
                        reportHeading = """
                        <h1 align=center>Report : %s</h1>
                        <h2 align=center> Limits : Experiments %s </h2>
                        <h2 align=center> <font color="red"> Rows limited to %s </font> </h2>                      
                        <h3 align=center> as at %s </h3>"""\
                                    %(self.argDict['reportmenu'],self.argDict['experiments'],maxRows,date.isoformat(date.today()))
                else:
                    if maxRows == None:
                        #reportHeading = """Report : %s Limits : Experiments %s  : as at %s"""\
                        #            %(self.argDict['reportmenu'],self.argDict['experiments'],date.isoformat(date.today()))
                        reportHeading = ""
                        
                    else:
                        reportHeading = """Report : %s Limits : Experiments %s  : Rows limited to %s : as at %s"""\
                                    %(self.argDict['reportmenu'],self.argDict['experiments'],maxRows,date.isoformat(date.today()))


                experimentCount = 0
                globalrowCount = 0
                for experiment in self.argDict['experiments']:


                    study = geneExpressionStudy()
                    study.initFromDatabase(int(experiment),connection)

                                
                    # execute the report query
                    query = reportSQLDict[self.argDict['reportmenu']]%{
                        'microarraystudy' : experiment
                    }
                    agresearchpagemodulelogger.info("genstatnormalisationextract executing %s"%str(query))
                    
                    reportCursor.execute(query)
                    fieldNames = [item[0] for item in reportCursor.description]

                    if experimentCount == 0:
                        if self.argDict['outputto'] == 'browser':
                            print getReportHeader(self.argDict['reportmenu'],reportHeading,fieldNames,self.argDict['outputformat'])
                        else:    
                            print getDownloadHeader(self.argDict['filename'],self.argDict['reportmenu'],reportHeading,fieldNames,self.argDict['outputformat'])                        
       

                    reportFieldValues = reportCursor.fetchone()

                    experimentCount += 1

                    
                    rowCount = 0
                    while reportFieldValues != None:
                        if maxRows != None:
                            if rowCount >= maxRows:
                                break
                        rowCount += 1
                        globalrowCount += 1

                        reportDict = dict(zip(fieldNames,reportFieldValues))

                        
                        if self.argDict['outputformat'] == 'html':
                            record = '<tr>'
                            record+=reduce(lambda x,y: x+'<td>'+str(y)+'</td>', reportFieldValues,'')
                            print(record+'</tr>\n')
                        elif self.argDict['outputformat'] == 'csv':
                            record=reduce(lambda x,y: x+','+str(y), reportFieldValues,'')
                            record = re.sub('^,','',record)
                            print record
                        
                        reportFieldValues = reportCursor.fetchone()


                if self.argDict['outputto'] == 'browser':
                    print getReportFooter(globalrowCount)

            finally:
                reportCursor.close()        
                if connection != None:
                    connection.close()


        elif self.argDict['reportmenu'] == 'sequencereport1':
            # example URL for linking to this report :
            # http://localhost/cgi-bin/agbrdf/report.py?page=report_locusreports&context=page
            # http://devsheepgenomics.agresearch.co.nz/cgi-bin/sheepgenomics/report.py?reportmenu=flankinggenereport1&cohortmethod=coordinate&mapname=vsheep1.1&mapposition0=10000000&mapposition1=20000000&chromosome=OAR1&context=report&outputto=browser&positionunit=1
            try:
           	connection=databaseModule.getConnection()        	
                reportCursor=connection.cursor()


                if 'candidatesequencelistids' in self.argDict:
                    if not isinstance(self.argDict['candidatesequencelistids'],ListType):
                        self.argDict['candidatesequencelistids'] = re.split('\n',self.argDict['candidatesequencelistids'])
                        self.argDict['candidatesequencelistids'] = [item.strip() for item in self.argDict['candidatesequencelistids'] if len(item.strip()) > 1]
                else:
                    self.argDict['candidatesequencelistids'] = None

                if 'hits_in_list' not in self.argDict:
                    self.argDict['hits_in_list'] = 'False'

                if 'sequencelistids' in self.argDict:
                    if not isinstance(self.argDict['sequencelistids'],ListType):
                       self.argDict['sequencelistids'] = re.split('\n',self.argDict['sequencelistids'])
                       self.argDict['sequencelistids'] = [item.strip() for item in self.argDict['sequencelistids'] if len(item.strip()) > 1]
                if 'sequencenames' in self.argDict:
                    if not isinstance(self.argDict['sequencenames'],ListType):
                        self.argDict['sequencenames'] = re.split('\n',self.argDict['sequencenames'])
                        self.argDict['sequencenames'] = [item.strip() for item in self.argDict['sequencenames'] if len(item.strip()) > 1]

                if 'sequencenameslistname' not in  self.argDict:
                    self.argDict['sequencenameslistname'] = 'anonymous list'

                if len(self.argDict['sequencenameslistname'].strip()) == 0:
                    self.argDict['sequencenameslistname'] = 'anonymous list'

                if self.argDict['sequencenameslistname'] != 'anonymous list' : 
                    self.argDict['sequencenameslistname'] = 'Sequence List: %s'%self.argDict['sequencenameslistname']

                maxRows = None
                if 'maxrows' in self.argDict:
                    if re.search('^\s*\d+\s*$',self.argDict['maxrows']) != None:
                       maxRows = int(self.argDict['maxrows'])

                if 'orderbyclause' not in self.argDict:
                    self.argDict.update( {
                       'orderbyclause' : ""
                    })
                if 'outputformat' not in self.argDict:
                    self.argDict.update( {
                       'outputformat' : "FASTA"
                    })


                # send content type now as this report can time out
                if self.argDict['outputto'] == 'browser':
                    print getReportHeader(onlyContentType=True)
                else:
                    print getDownloadHeader(self.argDict['filename'],onlyContentType=True)


                self.argDict.update( {
                    'datestamp' : date.isoformat(date.today())
                })



                # execute the report queries
                sqllist=[]


                if self.argDict['cohortmethod'] == 'sequencelist':
                    for sequencelistid in self.argDict['sequencelistids']:
                        sqllist.append(reportSQLDict['sequencereport1']%sequencelistid) # this handles lists that contain query sequences
                        if self.argDict['hits_in_list'] == 'True':
                            sqllist.append(reportSQLDict['sequencereport2']%sequencelistid) # this handles lists that contain hit sequences
                            
                            
                elif self.argDict['cohortmethod'] == 'candidatesequencelist':
                    for sequencelistid in self.argDict['candidatesequencelistids']:
                        sqllist.append(reportSQLDict['sequencereport1']%sequencelistid) # this handles lists that contain query sequences
                        if self.argDict['hits_in_list'] == 'True':
                            sqllist.append(reportSQLDict['sequencereport2']%sequencelistid) # this handles lists that contain hit sequences

                elif self.argDict['cohortmethod'] == 'sql':
                    for sequencelistid in self.argDict['candidatesequencelistids']:
                        sqllist.append(reportSQLDict['sequencereport1']%sequencelistid) # this handles lists that contain query sequences
                        if self.argDict['hits_in_list'] == 'True':
                            sqllist.append(reportSQLDict['sequencereport2']%sequencelistid) # this handles lists that contain hit sequences



                elif self.argDict['cohortmethod'] == 'sequencenames':


                    # we need to call the search engine for each name, and build a list of sequences that match the list
                    agresearchpagemodulelogger.info("executing searches on sequencenames %s"%str(self.argDict['sequencenames'])) 

                    # execute the first query, which creates the list
                    engineQuery="select getSearchResultList(%(sequencename)s,'SYSTEM',%(sequencenamematchlimit)s,'Biosequences',0,0,%(sequencenameslistname)s)"
                    agresearchpagemodulelogger.info("executing getSearchResultList(%(sequencename)s,'SYSTEM',%(sequencenamematchlimit)s,'Biosequences',0,0,%(sequencenameslistname)s)"%{'sequencename' : self.argDict['sequencenames'][0],'sequencenamematchlimit' : self.argDict['sequencenamematchlimit'],\
                           'sequencenameslistname' : self.argDict['sequencenameslistname']})
                    reportCursor.execute(engineQuery,{'sequencename' : self.argDict['sequencenames'][0],'sequencenamematchlimit' : self.argDict['sequencenamematchlimit'],\
                           'sequencenameslistname' : self.argDict['sequencenameslistname']})
                    listid = reportCursor.fetchone()[0]
                    connection.commit()

                    # execute the rest
                    for sequencename in self.argDict['sequencenames'][1:]:
                        if len(sequencename.strip()) == 0:
                            continue;
                        engineQuery="select getSearchResultList(%(sequencename)s,'SYSTEM',%(sequencenamematchlimit)s,'Biosequences',0,%(listid)s)"
                        agresearchpagemodulelogger.info("executing getSearchResultList(%(sequencename)s,'SYSTEM',%(sequencenamematchlimit)s,'Biosequences',0,%(listid)s)"%{'sequencename' : sequencename,'sequencenamematchlimit' : self.argDict['sequencenamematchlimit'],\
                                                'listid' : listid})


                        reportCursor.execute(engineQuery,{'sequencename' : sequencename,'sequencenamematchlimit' : self.argDict['sequencenamematchlimit'],\
                                                'listid' : listid})
                        reportCursor.fetchone()[0]
                        connection.commit()

                    sqllist.append(reportSQLDict['sequencereport1']%listid) # this handles lists that contain query sequences
                    if self.argDict['hits_in_list'] == 'True':
                        sqllist.append(reportSQLDict['sequencereport2']%listid) # this handles lists that contain query sequences
                        

                agresearchpagemodulelogger.info("queries to execute : %s"%str(sqllist))

                # if the option to use repeatmasking has been selected, then edit the
                # queries to replace the reference to seqstring, but a function call to
                # return repeatmasked sequence
                if 'maskrepeats' in self.argDict:
                    if self.argDict['maskrepeats'] == 'True':
                        agresearchpagemodulelogger.info("rewriting queries to apply masking")
                        if 'use_x' in self.argDict:
                            for i in range(0,len(sqllist)):
                                sqllist[i] = re.sub("bs\.seqstring","markFeature(bs.obid,'repeat_region','X') as seqstring",sqllist[i])
                        else:
                            for i in range(0,len(sqllist)):
                                sqllist[i] = re.sub("bs\.seqstring","markFeature(bs.obid,'repeat_region','lowercase') as seqstring",sqllist[i])



                # execute the first query
                agresearchpagemodulelogger.info("executing %s"%sqllist[0])
                reportCursor.execute(sqllist[0])
                fieldNames = [item[0] for item in reportCursor.description]

                # now construct heading
                if self.argDict['cohortmethod'] == 'sequencelist':
                    reportHeading = """
                        <h1 align=center>Sequence download  - sequences in specified search list(s)</h1>
                        <h3 align=center> as at %(datestamp)s </h3>
                    """%self.argDict
                elif self.argDict['cohortmethod'] == 'candidatesequencelist':
                    reportHeading = """
                        <h1 align=center>Sequence download - sequences in specified project list(s)</h1>
                        <h3 align=center> as at %(datestamp)s </h3>
                    """%self.argDict                    
                elif self.argDict['cohortmethod'] == 'sequencenames':
                    reportHeading = """
                        <h1 align=center>Sequence download - sequences from pasted-in list </h1>
                        <h3 align=center> as at %(datestamp)s </h3>
                    """%self.argDict         
                
                FASTAheader=""
                if maxRows != None:
                    reportHeading += "<h3 align=center> (Rows limited to %s) </h3>"%maxRows
                    FASTAheader = "(Rows limited to %s)"%maxRows
                
                reportFieldValues = reportCursor.fetchone()


                if self.argDict['outputto'] == 'browser':
                    if self.argDict['outputformat'] == 'html':
                        print getReportHeader(self.argDict['reportmenu'],reportHeading,fieldNames[1:],self.argDict['outputformat'],needContentType=False)
                    elif self.argDict['outputformat'] == 'FASTA':
                        print getReportHeader("",FASTAheader,"",self.argDict['outputformat'],needContentType=False)
                    else:
                        print getReportHeader(self.argDict['reportmenu'],reportHeading,fieldNames,self.argDict['outputformat'],needContentType=False)

                else:    
                    if self.argDict['outputformat'] == 'html':
                        print getDownloadHeader(self.argDict['filename'],self.argDict['reportmenu'],reportHeading,fieldNames[1:],self.argDict['outputformat'],needContentType=False)
                    elif self.argDict['outputformat'] == 'FASTA':
                        print getDownloadHeader(self.argDict['filename'],"",FASTAheader,"",self.argDict['outputformat'],needContentType=False)
                    else:
                        print getDownloadHeader(self.argDict['filename'],self.argDict['reportmenu'],reportHeading,fieldNames,self.argDict['outputformat'],needContentType=False)
                       

                rowCount = 0
                queryNumber = 0
                lineend = '\n'
                if self.argDict['outputto'] == 'browser' and self.argDict['outputformat'] != 'html':
                    print '<pre>'   
                while True:

                    while reportFieldValues != None:
                        reportFieldDict = dict(zip(fieldNames,reportFieldValues))

                        # skip seqs with no sequence
                        if reportFieldDict['seqstring'] != None:
                            if len(reportFieldDict['seqstring']) > 0:
    
                                if maxRows != None:
                                    if rowCount >= maxRows:
                                        break
                                rowCount += 1


                                if self.argDict['outputformat'] == 'html':
                                    record+=reduce(lambda x,y: x+'<td>'+str(y)+'</td>', reportFieldValues,'')
                                    print(record+'</tr>\n')   
                                elif self.argDict['outputformat'] == 'csv':
                                    record = reduce(lambda x,y: x + '"' + str(y) + '",' , reportFieldValues,'')
                                    print record
                                elif self.argDict['outputformat'] == 'FASTA':
                                    if self.argDict['outputto'] == 'browser':
                                        print ">%s"%reportFieldDict['idline']
                                        (outline,currentpos) = tidyout(reportFieldDict['seqstring'], 60, 0, lineend)
                                    else:
                                        print ">%s"%reportFieldDict['idline']
                                        (outline,currentpos) = tidyout(reportFieldDict['seqstring'], 60, 0, lineend,False)

                                    print outline


                        reportFieldValues = reportCursor.fetchone()

                    queryNumber += 1
                    if queryNumber >= len(sqllist):
                        break
                    agresearchpagemodulelogger.info("executing %s"%sqllist[queryNumber])
                    reportCursor.execute(sqllist[queryNumber])
                    reportFieldValues = reportCursor.fetchone()
                    #agresearchpagemodulelogger.info(str(reportFieldValues))

                if self.argDict['outputto'] == 'browser':
                    print getReportFooter(rowCount)

                if self.argDict['outputto'] == 'browser' and self.argDict['outputformat'] != 'html':
                    print '</pre>'   


            finally:
                reportCursor.close()        
                if connection != None:
                    connection.close()

        elif self.argDict['reportmenu'] in  ['gbsreport1','gbsreport2']:
            # example URL for linking to this report :
            # http://localhost/cgi-bin/agbrdf/report.py?page=report_locusreports&context=page
            # http://devsheepgenomics.agresearch.co.nz/cgi-bin/sheepgenomics/report.py?reportmenu=flankinggenereport1&cohortmethod=coordinate&mapname=vsheep1.1&mapposition0=10000000&mapposition1=20000000&chromosome=OAR1&context=report&outputto=browser&positionunit=1
            try:
           	connection=databaseModule.getConnection()        	
                reportCursor=connection.cursor()



                if 'species' in self.argDict:
                    if not isinstance(self.argDict['species'],ListType):
                       self.argDict['species'] = re.split('\n',self.argDict['species'])
                       self.argDict['species'] = [item.strip() for item in self.argDict['species'] if len(item.strip()) > 1]
                if 'samples' in self.argDict:
                    if not isinstance(self.argDict['samples'],ListType):
                        self.argDict['samples'] = re.split('\n',self.argDict['samples'])
                        self.argDict['samples'] = [item.strip() for item in self.argDict['samples'] if len(item.strip()) > 1]
                if 'runs' in self.argDict:
                    if not isinstance(self.argDict['runs'],ListType):
                        self.argDict['runs'] = re.split('\n',self.argDict['runs'])
                        self.argDict['runs'] = [item.strip() for item in self.argDict['runs'] if len(item.strip()) > 1]                        



                maxRows = None
                if 'maxrows' in self.argDict:
                    if re.search('^\s*\d+\s*$',self.argDict['maxrows']) != None:
                       maxRows = int(self.argDict['maxrows'])

                if 'orderbyclause' not in self.argDict:
                    self.argDict.update( {
                       'orderbyclause' : ""
                    })
                if 'outputformat' not in self.argDict:
                    self.argDict.update( {
                       'outputformat' : "FASTA"
                    })


                # send content type now as this report can time out
                if self.argDict['outputto'] == 'browser':
                    print getReportHeader(onlyContentType=True)
                else:
                    print getDownloadHeader(self.argDict['filename'],onlyContentType=True)


                self.argDict.update( {
                    'datestamp' : date.isoformat(date.today())
                })



                # execute the report queries
                sqllist=[]


                filter_clause = ""
                if self.argDict['filter_field'] in ('callrate','sampdepth','tag_count','read_count'):
                    if self.argDict['filter_relation'] in ("<", ">="):
                        if len(self.argDict['filter_bound']) > 0:
                            try:
                                x=float(self.argDict['filter_bound'].strip())
                                filter_clause = " and %(filter_field)s %(filter_relation)s %(filter_bound)s"%self.argDict
                            except:
                                None
                                
                self.argDict.update({"filter_clause" : filter_clause})
                if self.argDict['cohortmethod'] == 'samplenames':
                    samples_sql_clause_list = ",".join(["'%s'"%sample for sample in self.argDict['samples']])
                    #samples_sql_clause = " sampleid in ( %s )"%samples_sql_clause + filter_clause
                    samples_sql_clause = " sample in ( %s )"%samples_sql_clause_list + filter_clause
                    sampleids_sql_clause = " sampleid in ( %s )"%samples_sql_clause_list + filter_clause
                    sqllist.append(reportSQLDict[self.argDict['reportmenu']]%(samples_sql_clause, sampleids_sql_clause))  
                elif self.argDict['cohortmethod'] == 'speciesnames':
                    species_sql_clause = ",".join(["'%s'"%species for species in self.argDict['species']]) 
                    species_sql_clause = " lower(species) in ( %s )"%species_sql_clause + filter_clause
                    sqllist.append(reportSQLDict[self.argDict['reportmenu']]%(species_sql_clause,species_sql_clause))
                elif self.argDict['cohortmethod'] == 'runnames':
                    runs_sql_clause = ",".join(["'%s'"%run for run in self.argDict['runs']]) 
                    runs_sql_clause = " listname in ( %s )"%runs_sql_clause + filter_clause
                    sqllist.append(reportSQLDict[self.argDict['reportmenu']]%(runs_sql_clause,runs_sql_clause))

 
                agresearchpagemodulelogger.info("queries to execute : %s"%str(sqllist))


                # execute the first query
                agresearchpagemodulelogger.info("executing %s"%sqllist[0])
                reportCursor.execute(sqllist[0])
                fieldNames = [item[0] for item in reportCursor.description]

                # now construct heading

                if self.argDict['cohortmethod'] == 'samplenames':
                    reportHeading = """
                        <h1 align=center>GBS download for specified samples %(filter_clause)s</h1>
                        <h3 align=center> as at %(datestamp)s </h3>
                    """%self.argDict
                elif self.argDict['cohortmethod'] == 'speciesnames':
                    reportHeading = """
                        <h1 align=center>GBS download for specified species %(filter_clause)s</h1>
                        <h3 align=center> as at %(datestamp)s </h3>
                    """%self.argDict
                elif self.argDict['cohortmethod'] == 'runnames':
                    reportHeading = """
                        <h1 align=center>GBS download for specified runs %(filter_clause)s</h1>
                        <h3 align=center> as at %(datestamp)s </h3>
                    """%self.argDict
 
                if maxRows != None:
                    reportHeading += "<h3 align=center> (Rows limited to %s) </h3>"%maxRows
                    FASTAheader = "(Rows limited to %s)"%maxRows
                
                reportFieldValues = reportCursor.fetchone()


                if self.argDict['outputto'] == 'browser':
                    if self.argDict['outputformat'] == 'html':
                        print getReportHeader(self.argDict['reportmenu'],reportHeading,fieldNames[1:],self.argDict['outputformat'],needContentType=False)
                    else:
                        print getReportHeader(self.argDict['reportmenu'],reportHeading,fieldNames,self.argDict['outputformat'],needContentType=False)

                else:    
                    if self.argDict['outputformat'] == 'html':
                        print getDownloadHeader(self.argDict['filename'],self.argDict['reportmenu'],reportHeading,fieldNames[1:],self.argDict['outputformat'],needContentType=False)
                    elif self.argDict['outputformat'] == 'csv':
                        print getDownloadHeader(self.argDict['filename'],self.argDict['reportmenu'],reportHeading,fieldNames,self.argDict['outputformat'],needContentType=False)
	            else:
                        print getDownloadHeader(self.argDict['filename'],self.argDict['reportmenu'],reportHeading,fieldNames,self.argDict['outputformat'],needContentType=False)
                        
                       

                rowCount = 0
                queryNumber = 0
                lineend = '\n'
                if self.argDict['outputto'] == 'browser' and self.argDict['outputformat'] != 'html':
                    print '<pre>'   
                while True:

                    while reportFieldValues != None:
                        reportFieldDict = dict(zip(fieldNames,reportFieldValues))


                        if maxRows != None:
                            if rowCount >= maxRows:
                                break
                        rowCount += 1


                        if self.argDict['outputformat'] == 'html':
                            record+=reduce(lambda x,y: x+'<td>'+str(y)+'</td>', reportFieldValues,'')
                            print(record+'</tr>\n')   
                        elif self.argDict['outputformat'] == 'csv':
                            record = reduce(lambda x,y: x + '"' + str(y) + '",' , reportFieldValues,'')
                            print record
                        elif self.argDict['outputformat'] == 'txt':
                            record = '\t'.join([str(item) for item in reportFieldValues])
                            print record


                        reportFieldValues = reportCursor.fetchone()

                    queryNumber += 1
                    if queryNumber >= len(sqllist):
                        break
                    agresearchpagemodulelogger.info("executing %s"%sqllist[queryNumber])
                    reportCursor.execute(sqllist[queryNumber])
                    reportFieldValues = reportCursor.fetchone()
                    #agresearchpagemodulelogger.info(str(reportFieldValues))

                if self.argDict['outputto'] == 'browser':
                    print getReportFooter(rowCount)

                if self.argDict['outputto'] == 'browser' and self.argDict['outputformat'] != 'html':
                    print '</pre>'   


            finally:
                reportCursor.close()        
                if connection != None:
                    connection.close()    
    

        elif self.argDict['reportmenu'] == 'unblind_report':
            # example URL for linking to this report :
            # http://localhost/cgi-bin/agbrdf/report.py?page=report_locusreports&context=page
            # http://devsheepgenomics.agresearch.co.nz/cgi-bin/sheepgenomics/report.py?reportmenu=flankinggenereport1&cohortmethod=coordinate&mapname=vsheep1.1&mapposition0=10000000&mapposition1=20000000&chromosome=OAR1&context=report&outputto=browser&positionunit=1
            try:
           	connection=databaseModule.getConnection()        	
                reportCursor=connection.cursor()



                if 'species' in self.argDict:
                    if not isinstance(self.argDict['species'],ListType):
                       self.argDict['species'] = re.split('\n',self.argDict['species'])
                       self.argDict['species'] = [item.strip() for item in self.argDict['species'] if len(item.strip()) > 1]
                if 'samples' in self.argDict:
                    if not isinstance(self.argDict['samples'],ListType):
                        self.argDict['samples'] = re.split('\n',self.argDict['samples'])
                        self.argDict['samples'] = [item.strip() for item in self.argDict['samples'] if len(item.strip()) > 1]
                if 'runs' in self.argDict:
                    if not isinstance(self.argDict['runs'],ListType):
                        self.argDict['runs'] = re.split('\n',self.argDict['runs'])
                        self.argDict['runs'] = [item.strip() for item in self.argDict['runs'] if len(item.strip()) > 1]                        



                maxRows = None
                if 'maxrows' in self.argDict:
                    if re.search('^\s*\d+\s*$',self.argDict['maxrows']) != None:
                       maxRows = int(self.argDict['maxrows'])

                if 'orderbyclause' not in self.argDict:
                    self.argDict.update( {
                       'orderbyclause' : ""
                    })
                if 'outputformat' not in self.argDict:
                    self.argDict.update( {
                       'outputformat' : "FASTA"
                    })


                # send content type now as this report can time out
                if self.argDict['outputto'] == 'browser':
                    print getReportHeader(onlyContentType=True)
                else:
                    print getDownloadHeader(self.argDict['filename'],onlyContentType=True)


                self.argDict.update( {
                    'datestamp' : date.isoformat(date.today())
                })



                # execute the report queries
                sqllist=[]


                filter_clause = ""
                if self.argDict['filter_field'] in ('callrate','sampdepth','tag_count','read_count'):
                    if self.argDict['filter_relation'] in ("<", ">="):
                        if len(self.argDict['filter_bound']) > 0:
                            try:
                                x=float(self.argDict['filter_bound'].strip())
                                filter_clause = " and %(filter_field)s %(filter_relation)s %(filter_bound)s"%self.argDict
                            except:
                                None
                                
                self.argDict.update({"filter_clause" : filter_clause})
                if self.argDict['cohortmethod'] == 'samplenames':
                    samples_sql_clause = ",".join(["'%s'"%sample for sample in self.argDict['samples']])
                    samples_sql_clause = " sample in ( %s ) or qc_sampleid in ( %s ) or split_part(qc_sampleid, '-', 1) in ( %s ) "%(samples_sql_clause,samples_sql_clause,samples_sql_clause) + filter_clause
                    sqllist.append(reportSQLDict['unblind_report']%samples_sql_clause)  
                elif self.argDict['cohortmethod'] == 'speciesnames':
                    species_sql_clause = ",".join(["'%s'"%species for species in self.argDict['species']]) 
                    species_sql_clause = " lower(species) in ( %s )"%species_sql_clause + filter_clause
                    sqllist.append(reportSQLDict['unblind_report']%(species_sql_clause))
                elif self.argDict['cohortmethod'] == 'runnames':
                    runs_sql_clause = ",".join(["'%s'"%run for run in self.argDict['runs']]) 
                    runs_sql_clause = " listname in ( %s )"%runs_sql_clause + filter_clause
                    sqllist.append(reportSQLDict['unblind_report']%(runs_sql_clause))

 
                agresearchpagemodulelogger.info("queries to execute : %s"%str(sqllist))


                # execute the first query
                agresearchpagemodulelogger.info("executing %s"%sqllist[0])
                reportCursor.execute(sqllist[0])
                fieldNames = [item[0] for item in reportCursor.description]

                # now construct heading

                if self.argDict['cohortmethod'] == 'samplenames':
                    reportHeading = """
                        <h1 align=center>Unblind report for specified samples %(filter_clause)s</h1>
                        <h3 align=center> as at %(datestamp)s </h3>
                    """%self.argDict
                elif self.argDict['cohortmethod'] == 'speciesnames':
                    reportHeading = """
                        <h1 align=center>Unblind report for specified species %(filter_clause)s</h1>
                        <h3 align=center> as at %(datestamp)s </h3>
                    """%self.argDict
                elif self.argDict['cohortmethod'] == 'runnames':
                    reportHeading = """
                        <h1 align=center>Unblind report for specified runs %(filter_clause)s</h1>
                        <h3 align=center> as at %(datestamp)s </h3>
                    """%self.argDict
 
                if maxRows != None:
                    reportHeading += "<h3 align=center> (Rows limited to %s) </h3>"%maxRows
                    FASTAheader = "(Rows limited to %s)"%maxRows
                
                reportFieldValues = reportCursor.fetchone()


                if self.argDict['outputto'] == 'browser':
                    if self.argDict['outputformat'] == 'html':
                        print getReportHeader(self.argDict['reportmenu'],reportHeading,fieldNames[1:],self.argDict['outputformat'],needContentType=False)
                    else:
                        print getReportHeader(self.argDict['reportmenu'],reportHeading,fieldNames,self.argDict['outputformat'],needContentType=False)

                else:    
                    if self.argDict['outputformat'] == 'html':
                        print getDownloadHeader(self.argDict['filename'],self.argDict['reportmenu'],reportHeading,fieldNames[1:],self.argDict['outputformat'],needContentType=False)
                    elif self.argDict['outputformat'] == 'csv':
                        print getDownloadHeader(self.argDict['filename'],self.argDict['reportmenu'],reportHeading,fieldNames,self.argDict['outputformat'],needContentType=False)
	            else:
                        print getDownloadHeader(self.argDict['filename'],self.argDict['reportmenu'],reportHeading,fieldNames,self.argDict['outputformat'],needContentType=False)
                        
                       

                rowCount = 0
                queryNumber = 0
                lineend = '\n'
                if self.argDict['outputto'] == 'browser' and self.argDict['outputformat'] != 'html':
                    print '<pre>'   
                while True:

                    while reportFieldValues != None:
                        reportFieldDict = dict(zip(fieldNames,reportFieldValues))


                        if maxRows != None:
                            if rowCount >= maxRows:
                                break
                        rowCount += 1


                        if self.argDict['outputformat'] == 'html':
                            record+=reduce(lambda x,y: x+'<td>'+str(y)+'</td>', reportFieldValues,'')
                            print(record+'</tr>\n')   
                        elif self.argDict['outputformat'] == 'csv':
                            record = reduce(lambda x,y: x + '"' + str(y) + '",' , reportFieldValues,'')
                            print record
                        elif self.argDict['outputformat'] == 'txt':
                            record = '\t'.join([str(item) for item in reportFieldValues])
                            print record


                        reportFieldValues = reportCursor.fetchone()

                    queryNumber += 1
                    if queryNumber >= len(sqllist):
                        break
                    agresearchpagemodulelogger.info("executing %s"%sqllist[queryNumber])
                    reportCursor.execute(sqllist[queryNumber])
                    reportFieldValues = reportCursor.fetchone()
                    #agresearchpagemodulelogger.info(str(reportFieldValues))

                if self.argDict['outputto'] == 'browser':
                    print getReportFooter(rowCount)

                if self.argDict['outputto'] == 'browser' and self.argDict['outputformat'] != 'html':
                    print '</pre>'   


            finally:
                reportCursor.close()        
                if connection != None:
                    connection.close()    
    
class testPage ( page ):

    def __init__(self,argDict):
        page.__init__(self)
        self.argDict = argDict
    
    def asHTML(self):
        print "Content-Type: text/html"     # HTML is following
        print                               # blank line, end of headers

        print "<html>\n"
        print "<head>\n"
        print "<TITLE>agresearch Test Page</TITLE>"
        print "</head>\n"
        print "<body>\n"
        print "<H1>AgResearch Test Page</H1>"
        for key in self.argDict.keys():
            print key + " = " + str(self.argDict[key]) + "<br/>\n"
        print "</body>\n"
        print "</html>\n"



def main():
    testFields = {'obTypeName' : 'ALL', 'queryString':'mutase'}
    

class testPage ( page ):

    def __init__(self,argDict):
        page.__init__(self)
        self.argDict = argDict
    
    def asHTML(self):
        print "Content-Type: text/html"     # HTML is following
        print                               # blank line, end of headers

        print "<html>\n"
        print "<head>\n"
        print "<TITLE>agresearch Test Page</TITLE>"
        print "</head>\n"
        print "<body>\n"
        print "<H1>AgResearch Test Page</H1>"
        for key in self.argDict.keys():
            print key + " = " + str(self.argDict[key]) + "<br/>\n"
        print "</body>\n"
        print "</html>\n"



def main():
    #testFields = {'obTypeName' : 'ALL', 'queryString':'mutase'}
    #test = testPage(testFields)
    #search = searchResultPage(testFields)
    #print search.asHTML()
    #print test.asHTML()
    #try :
        #page=geneSummaryPage()
        #htmlChunk = page.asHTML(304);
        #page.close()
    #except :
    #    errorPage("Error creating geneSummaryPage")
    #return   
    reportParms = { 'outputformat': 'csv', 'orderbyclause': '', 'maxrows': '', 'filename': 'snpbreeds1.csv', 'animallists': ['Cattle.Breed.ANG', 'Cattle.Breed.ANO', 'Cattle.Breed.BMA', 'Cattle.Breed.BRM', 'Cattle.Breed.BSW', 'Cattle.Breed.BUF', 'Cattle.Breed.CHL', 'Cattle.Breed.GIR', 'Cattle.Breed.GNS', 'Cattle.Breed.HFD', 'Cattle.Breed.HOL', 'Cattle.Breed.JER', 'Cattle.Breed.LMS', 'Cattle.Breed.NDA', 'Cattle.Breed.NEL', 'Cattle.Breed.NRC', 'Cattle.Breed.PMT', 'Cattle.Breed.RGU', 'Cattle.Breed.RMG', 'Cattle.Breed.SGT', 'Cattle.Breed.SHK'], 'reportmenu': 'snpannotation1', 'context': 'report', 'outputto': 'file'}
    page = simpleReportPage(reportParms)
    page.doReport()
        

if __name__ == "__main__":
   main()


