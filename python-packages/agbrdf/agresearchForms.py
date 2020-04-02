#-----------------------------------------------------------------------+
# Name:     agresearchForms.py                                          |
#                                                                       |
# Description:  classes that implement AgResearch data entry forms      |
#                                                                       |
#=======================================================================|
# Copyright 2005 by AgResearch (NZ).                                    |
# All rights reserved.                                                  |
#                                                                       |
#=======================================================================|
# Revision History:                                                     |
#                                                                       |
# Date      Ini Description                                             |
# --------- --- ------------------------------------------------------- |
# 3/2006    AFM  initial version                                        |
# 2/2007    JSM  updated with microarray submission pages               |
#-----------------------------------------------------------------------+
import sys
import types
import databaseModule
import csv
import re
import os
import string
import copy
from datetime import date, datetime
import globalConf
# 8/2009
# before any of the brdf modules are loaded, reset the
# logging path if required. Usually python modules are only
# imported once therefore subsequent modules that import
# globalConf will pick up our setting. (It is possible for
# modules to specifically reload a module - if any do this then
# they will pick up the original log path and this section will
# not work)
if __name__ == "__main__":  # (so this block will only execute if this module is being run, not if it is being imported)
    # get and parse command line args
    argDict = dict([ re.split('=',arg) for arg in sys.argv if re.search('=',arg) != None ])
    print "using %s"%str(argDict)

    if 'logpath' in argDict:
       # check it exists and is a directory
       if not os.path.isdir(argDict["logpath"]):
          print "logpath %(logpath)s should be an existing (writeable) directory"%argDict
          sys.exit(1)

    globalConf.LOGPATH=argDict["logpath"]

    print  "(logging reset to %s)"%globalConf.LOGPATH
import agbrdfConf
from brdfExceptionModule import brdfException
from annotationModule import commentOb, uriOb
from biosubjectmodule import bioSubjectOb, bioSampleOb, bioSampleList
from studyModule import phenotypeStudy, geneExpressionStudy, bioProtocolOb, microarrayObservation,bioDatabaseOb, databaseSearchStudy
from dataImportModule import dataSourceOb, importFunction, importProcedureOb, labResourceImportFunction,microarrayExperimentImportFunction,\
      databaseSearchImportFunction
from workFlowModule import staffOb
from agresearchPages import errorPage
from labResourceModule import labResourceOb, labResourceList
from listModule import obList, predicateLink
from sessionModule  import getFullName
from analysisModule import analysisProcedureOb
from obmodule import getNewObid
from types import ListType

import logging
import htmlModule
from sequenceModule import bioSequenceOb
from htmlModule import contentWrap

fetcher="/%s/fetch.py"%agbrdfConf.CGIPATH

brdfCSSLink=agbrdfConf.BRDF_CSS_LINK



# set up logger if we want logging
formmodulelogger = logging.getLogger('agbrdfForms')
formmodulehdlr = logging.FileHandler(os.path.join(globalConf.LOGPATH,'agbrdfforms.log'))
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
formmodulehdlr.setFormatter(formatter)
formmodulelogger.addHandler(formmodulehdlr) 
formmodulelogger.setLevel(logging.INFO)        

""" --------- module variables ----------"""

# constants
fetcher="/%s/fetch.py"%agbrdfConf.CGIPATH
listfetcher="/%s/fetchSelectList.py"%agbrdfConf.CGIPATH
waiter="/%s/wait.py"%agbrdfConf.CGIPATH
displayfetcher="/%s/fetchDisplay.py"%agbrdfConf.CGIPATH
analysisfetcher="/%s/fetchAnalysis.py"%agbrdfConf.CGIPATH
imageurl="/%s/"%agbrdfConf.IMAGEURLPATH
tempimageurl="/%s/"%agbrdfConf.TEMPIMAGEURLPATH
imagepath=os.path.join(globalConf.IMAGEFILEPATH,agbrdfConf.IMAGEFILEPATH)
homeurl="/%s"%agbrdfConf.HOMEPATH
underConstructionURL=os.path.join('/',agbrdfConf.UNDERCONSTRUCTION)
waitURL=os.path.join(agbrdfConf.IMAGEURLPATH,agbrdfConf.WAITGLYPH)
padlockurl="%s%s"%(imageurl,agbrdfConf.PADLOCK)


#
#<meta http-equiv="Content-Language" content="en-nz">
#<meta http-equiv="Content-Type" content="text/html; charset=windows-1252">
#
forms_AgResearchSequenceSubmissionForm = """
<html>
<head>
<title>AgResearch Sequence Submission</title>
<style>
<!--
INPUT.submit_button {background-color:red; font-size: 14pt; font-weight: bold; color: yellow }
__defaultBRDFStyle__
__CSSToggleSectionButton__

--></style>
<script type="text/javascript">

var isOpera = navigator.userAgent.indexOf('Opera') > -1;
var isIE = navigator.userAgent.indexOf('MSIE') > 1 && !isOpera;
var isMoz = navigator.userAgent.indexOf('Mozilla/5.') == 0 && !isOpera;

//================================================================//
var primer_count = 1;

// initialise the saved border in case they do not make any errors 
//var oldborder = sequenceSubmission.project.style.border;
var oldborder = "2px solid #CCDCDC"

function primer_information_text(id){ return '<input name="PIT_'+id+'">';}

function primer_sequence_text(id){ return '<input  name="PST_'+id+'">';}

function primer_information(id){ return '<select name="PI_'+id+'">'+
				'<option selected value="forward">Forward Primer</option>'+
				'<option value="reverse">Reverse Primer</option>'+
				'</select>';
				}

  function addPrimersRow(tableID) {
    var table = document.getElementById(tableID);
    var row = table.insertRow(table.rows.length);
        var cell = row.insertCell(0);
        cell.vAlign="top"
        cell.innerHTML = primer_information(primer_count);
        var cell = row.insertCell(1);
        cell.vAlign="top"
        cell.innerHTML = primer_information_text(primer_count);
        var cell = row.insertCell(2);
        cell.vAlign="top"
        cell.innerHTML = primer_sequence_text(primer_count);
        primer_count++;
 }

//================================================================//

var vector_count = 1;

function vector_information_text(id){ return '<input name="VIT_'+id+'">';}

function vector_information(id){ return '<input name="VI_'+id+'">';}

  function addVectorRow(tableID) {
    var table = document.getElementById(tableID);
    var row = table.insertRow(table.rows.length);
        var cell = row.insertCell(0);
        cell.vAlign="top"
        cell.innerHTML = vector_information(vector_count);
        var cell = row.insertCell(1);
        cell.vAlign="top"
        cell.innerHTML = vector_information_text(vector_count);
        vector_count++;
 }

//================================================================//

var source_count = 1;

function source_modifier_text(id){ return '<input name="SMV_'+id+'">';}

function source_modifier(id){ return '<select name="SM_'+id+'">'+
				'<option value="NONE" selected>&nbsp;</option>'+
				'<option>Anamorph</option>'+
				'<option>Authority</option>'+
				'<option>Biotype</option>'+
				'<option>Biovar</option>'+
				'<option>Breed</option>'+
				'<option>Cell-line</option>'+
				'<option>Cell-type</option>'+
				'<option>Chemovar</option>'+
				'<option>Clone</option>'+
				'<option>Clone-lib</option>'+
				'<option>Collected By</option>'+
				'<option>Collection Date</option>'+
				'<option>Country</option>'+
				'<option>Cultivar</option>'+
				'<option>Dev-stage</option>'+
				'<option>Ecotype</option>'+
				'<option>Forma</option>'+
				'<option>Forma Specialis</option>'+
				'<option>Frequency</option>'+
				'<option>Genotype</option>'+
				'<option>Germline</option>'+
				'<option>Haplotype</option>'+
				'<option>Identified By</option>'+
				'<option>Isolate</option>'+
				'<option>Lab-host</option>'+
				'<option>Lat-Lon</option>'+
				'<option>Natural-host</option>'+
				'<option>Pathovar</option>'+
				'<option>Plasmid-name</option>'+
				'<option>Plastid-name</option>'+
				'<option>Pop-variant</option>'+
				'<option>Proviral</option>'+
				'<option>Rearranged</option>'+
				'<option>Segment</option>'+
				'<option>Serogroup</option>'+
				'<option>Serotype</option>'+
				'<option>Serovar</option>'+
				'<option>Sex</option>'+
				'<option>Specimen-voucher</option>'+
				'<option>Strain</option>'+
				'<option>Sub-species</option>'+
				'<option>Subclone</option>'+
				'<option>Substrain</option>'+
				'<option>Subtype</option>'+
				'<option>Synonym</option>'+
				'<option>Teleomorph</option>'+
				'<option>Tissue-lib</option>'+
				'<option>Tissue-type</option>'+
				'<option>Type</option>'+
				'<option>Variety</option>'+
				'</select>';
}

  function addSourceModifiersRow(tableID) {
    var table = document.getElementById(tableID);
    var row = table.insertRow(table.rows.length);
        var cell = row.insertCell(0);
        cell.vAlign="top"
        cell.innerHTML = source_modifier(source_count);
        var cell = row.insertCell(1);
        cell.vAlign="top"
        cell.innerHTML = source_modifier_text(source_count);
        source_count++;
 }

 //================================================================//

var feature_count = 1;

function feature_strand(id){
	//return 'forward <input type="radio" value="V_'+id+'_forward" checked name="forward_reverse_'+id+'"> reverse <input type="radio" value="V_'+id+'_reverse" name="forward_reverse_'+id+'"></b>';
	return 'forward <input type="radio" value="1" checked name="forward_reverse_'+id+'"> reverse <input type="radio" value="-1" name="forward_reverse_'+id+'"></b>';	
}

function feature_loc(id){
	return 'start <input type=text name="feature_start_'+id+'" width=40> stop <input type=text width=40 name="feature_stop_'+id+'" size="20">';
}

function feature_type(id){ return '<select name="feature_type_'+id+'" onchange="addSpecifyInput(\\'feature_type_'+id+'\\',\\'cds_extra_'+id+'\\',\\'cds\\')"  >'+
                '<option></option>'+
		'<option>attenuator</option>'+
		'<option>C_region</option>'+
		'<option>CAAT_signal</option>'+
		'<option value="cds">CDS</option>'+
		'<option>conflict</option>'+
		'<option>D-loop</option>'+
		'<option>D_segment</option>'+
		'<option>enhancer</option>'+
		'<option>exon</option>'+
		'<option>gap</option>'+
		'<option>GC_signal</option>'+
		'<option>gene</option>'+
		'<option>iDNA</option>'+
		'<option>intron</option>'+
		'<option>J_segment</option>'+
		'<option>LTR</option>'+
		'<option>mat_peptide</option>'+
		'<option>misc_binding</option>'+
		'<option>misc_difference</option>'+
		'<option>misc_feature</option>'+
		'<option>misc_recomb</option>'+
		'<option>misc_RNA</option>'+
		'<option>misc_signal</option>'+
		'<option>misc_structure</option>'+
		'<option>modified_base</option>'+
		'<option>mRNA</option>'+
		'<option>N_region</option>'+
		'<option>old_sequence</option>'+
		'<option>operon</option>'+
		'<option>oriT</option>'+
		'<option>polyA_signal</option>'+
		'<option>polyA_site</option>'+
		'<option>precursor_RNA</option>'+
		'<option>prim_transcript</option>'+
		'<option>primer_bind</option>'+
		'<option>promoter</option>'+
		'<option>protein_bind</option>'+
		'<option>RBS</option>'+
		'<option>repeat_region</option>'+
		'<option>repeat_unit</option>'+
		'<option>rep_origin</option>'+
		'<option>rRNA</option>'+
		'<option>S_region</option>'+
		'<option>satellite</option>'+
		'<option>scRNA</option>'+
		'<option>sig_peptide</option>'+
		'<option>snRNA</option>'+
		'<option>snoRNA</option>'+
		'<option>source</option>'+
		'<option>stem_loop</option>'+
		'<option>STS</option>'+
		'<option>TATA_signal</option>'+
		'<option>terminator</option>'+
		'<option>transit_peptide</option>'+
		'<option>tRNA</option>'+
		'<option>unsure</option>'+
		'<option>V_region</option>'+
		'<option>V_segment</option>'+
		'<option>variation</option>'+
		'<option>3&#39;clip</option>'+
		'<option>3&#39;UTR</option>'+
		'<option>5&#39;clip</option>'+
		'<option>5&#39;UTR</option>'+
		'<option>-10_signal</option>'+
		'<option>-35_signal</option>'+
		'</select>'+
		'<span id="cds_extra_'+id+'" style="display:none;">'+
		'<table width="25%">'+
		'<tr><td width="18%">Gene Name:</td><td><input type=text name="geneName_'+id+'" width=40></td></tr>'+
		'<tr><td width="18%">Allele:</td><td><input type=text name="allele_'+id+'" width=40></td></tr>'+
		'<tr><td width="18%">Gene Description:</td><td><input type=text name="geneDesc_'+id+'" width=40></td></tr>'+
		'<tr><td width="18%">PseudoGene?:</td><td><input type=checkbox name="pseudogene_'+id+'"></td></tr>'+
		'<tr><td width="18%">Partial Ends:</td><td><select name="partial_'+id+'"><option selected>no</option><option>3&#39;</option><option>5&#39;</option><option>both</option></select></td></tr>'+
		'<tr><td colspan=2 ><em>A complete coding region includes both a valid start codon and the stop codon. If the coding region is not complete, select the appropriate partial end.</em></td></tr>'+
		'</table>'
		'</span>';
	}


 function addFeatureRow(tableID) {
  var table = document.getElementById(tableID);
    var row = table.insertRow(table.rows.length);
        var cell = row.insertCell(0);
        cell.vAlign="top"
        cell.innerHTML = feature_type(feature_count);
        var cell = row.insertCell(1);
        cell.vAlign="top"
        cell.innerHTML = feature_strand(feature_count);
        var cell = row.insertCell(2);
        cell.vAlign="top"
        cell.innerHTML = feature_loc(feature_count);
        feature_count++;
 }

//================================================================//



 function addSpecifyInput(selOpt,id, term){
  sel = document.getElementById(selOpt);
 el = document.getElementById(id)//;
 	if(sel.value == term){
	  el.style.display = '';
 	}else{
 	el.style.display = 'none';
 	}
 }

 function toggleSection(id){
 	 el = document.getElementById(id);
	 var display = el.style.display ? '' : 'none';
	 el.style.display = display;
 }


//=================================================================//
var bgColour = "";
var alreadySubmitted = false;

function checkAll() {
   // make sure we have not already submitted this form
   //if(alreadySubmitted) {
   //   window.alert("This Form has already been submitted, please wait");
   //   return false;
   //}


   // check the other values

   if(trim(sequenceSubmission.submitted_by.value) == "") {
      highLight(sequenceSubmission.submitted_by,"Please enter your name");
      return false;
   }
   else {
      lowLight(sequenceSubmission.sequence_name);
   }

   if(trim(sequenceSubmission.sequence_name.value) == "") {
      highLight(sequenceSubmission.sequence_name,"Please enter a sequence name");
      return false;
   }
   else {
      lowLight(sequenceSubmission.sequence_name);
   }

   if(trim(sequenceSubmission.sequence_description.value) == "") {
      highLight(sequenceSubmission.sequence_description,"Please enter a sequence description");
      return false;
   }
   else {
      lowLight(sequenceSubmission.sequence_description);
   }   

   
   if(trim(sequenceSubmission.mol_type.value) == "") {
      highLight(sequenceSubmission.mol_type,"Please choose a molecule type");
      return false;
   }
   else {
      lowLight(sequenceSubmission.mol_type);
   }

   if(trim(sequenceSubmission.mol_type.value) == "other") {
      highLight(sequenceSubmission.mol_type,"Sorry, 'other' molecule type not currently supported - please choose a different molecule type or contact support");
      return false;
   }
   else {
      lowLight(sequenceSubmission.mol_type);
   }   


   if(trim(sequenceSubmission.DNA_seq.value) == "") {
      highLight(sequenceSubmission.DNA_seq,"Please enter the sequence");
      return false;
   }
   else {
      lowLight(sequenceSubmission.DNA_seq);
   }


   if(trim(sequenceSubmission.sourceName.value) != "" && sequenceSubmission.existingSource.value != "") {
      highLight(sequenceSubmission.existingSource,"You have selected both an existing source and also entered a new one - please clear one of these fields");
      return false;
   }
   else {
      lowLight(sequenceSubmission.existingSource);
   }


   if (!  validateSequence(false)) {
      return false;
   }

   

   // finally , set the submitted flag
   alreadySubmitted = true;


   return true;
}

function highLight(item,message) {
  highLightBorder(item, message);
  // if(bgColour == "")
  //    eval("bgColour = item.style.background");
  // eval("item.style.background = 'red'");
   
   item.focus();
} // assume IE

// as above but just highlight border
function highLightBorder(item, message) {
  //window.alert(item.style.border);
  //oldborder = item.style.border;
  item.style.border="2px solid #FF0000";
  window.alert(message);
}

function lowLight(item) {
  return lowLightBorder(item);
   //eval("item.style.background = '" + bgColour + "'");
  // eval("item.style.background = 'white'");
}
// as above but just highlight border
function lowLightBorder(item) {
   item.style.border=oldborder;
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

function toggleSection(elementid) {
	elementid.style.display = (elementid.style.display == "block" ) ? "none" : "block";
	return false;
}

// -------------------- validation functions for checking sequence from rs -----------------

function validateSequence(confirm){
	if(trim(sequenceSubmission.DNA_seq.value) == "") {
           highLight(sequenceSubmission.DNA_seq,"Please enter the sequence");
           return false;
        }
        else {
           lowLight(sequenceSubmission.DNA_seq);
        }
        lowLight(sequenceSubmission.DNA_seq);
	//sequence = document.blast.sequence.value;
	sequence = sequenceSubmission.DNA_seq.value;
	//grab the first line
	pattern = /.+/;
	firstLine = pattern.exec(sequence);

	//check it for a fasta header or common chars found in a sequence ID
	pattern = /\>/;
	var result;
	if((result = pattern.exec(firstLine)) != null){
		highLight(sequenceSubmission.DNA_seq,"Please remove FASTA header. This can be included in the Sequence Description field above");
              textboxSelect(sequenceSubmission.DNA_seq,0,firstLine.toString().length+1);
		return false;
        }

	// change the regex to suit. don't forget new-line chars
	pattern = /[^agcturymkswbdhvn\\n\\r\\s]/mi; //multiline and case insensitive
	var result
	if((result = pattern.exec(sequence)) != null){
		highLight(sequenceSubmission.DNA_seq,"Invalid character '"+sequence.charAt(result.index)+"' in sequence at index "+result.index+
			". Only the following IUPAC nucleotide characters are valid within the sequence: "+
			"agcturymkswbdhvnAGCTURYMKSWBDHVN");
		textboxSelect(sequenceSubmission.DNA_seq,result.index,result.index+1);
		return false;
	}
       lowLight(sequenceSubmission.DNA_seq);
       lowLight(sequenceSubmission.DNA_seq_length);

	//only count valid characters
	pattern = /[agcturymkswbdhvn]/gmi;
	result = sequence.match(pattern);
       seqlen = sequenceSubmission.DNA_seq_length.value;
	actualseqlen = result.length;
	if (seqlen == actualseqlen ){
           if(confirm) {
              alert("Sequence looks OK");
           }
	    return true;
	 }else{
                highLight(sequenceSubmission.DNA_seq_length,"Invalid sequence length entered."+
	      "You entered "+seqlen +
	      " But the sequence is actually "+actualseqlen+" bp long");
             textboxSelect(sequenceSubmission.DNA_seq_length,0,seqlen.length)
	 }
}

function textboxSelect (oTextbox, iStart, iEnd) {
          if (isIE) {
              var oRange = oTextbox.createTextRange();
              oRange.moveStart("character", iStart);
              oRange.moveEnd("character", -oTextbox.value.length + iEnd);
              oRange.select();
          } else if (isMoz){
              oTextbox.setSelectionRange(iStart, iEnd);
          }
	oTextbox.focus();
}

var mywindow=null;
var myhelpcontent="";
var brdfpopupinstance = 0;
function brdfpopup(heading,content) {
   if(brdfpopupinstance == 0) {
       mywindow=window.open("","Describe","status=0,toolbar=0,menubar=0,scrollbars=1,width=800,height=600,resizable=1");
       mywindow.moveTo(100,100);
       // pagewrap the content
       mywindow.document.write('<html><head><title>' + heading + '</title>\\n');
       mywindow.document.write('<style type= "text/css">\\n');
       mywindow.document.write('BODY { FONT-SIZE: 90%; FONT-FAMILY: Arial, Helvetica, sans-serif; BACKGROUND: #f0f9ff ; }\\n');
       mywindow.document.write('</style></head>\\n');
       mywindow.document.write('<body>\\n');
       mywindow.document.write('<button type="button" onclick="self.close()">Close</button>');
       mywindow.document.write('<p/>');
       mywindow.document.write(content);
       mywindow.document.write('<p/></body>\\n');
       mywindow.document.write('<button type="button" onclick="self.close()">Close</button>');
       brdfpopupinstance = 1;
       return true;
    }
    else {
        brdfpopupinstance = 0;
        mywindow.close();
        brdfpopupinstance = 0;
        brdfpopup(heading,content);
        return true;
    }
}





</script>
</head>

<body bgcolor="#f7f5e0">

<form name="sequenceSubmission" onSubmit="return checkAll()" action="form.py"  target="_blank" method="POST">
<input type="hidden" name="sessionid" value="__sessionid__"/>
<input type="hidden" name="formstate" value="__formstate__"/>
<input type="hidden" name="formname" value="AgResearchSequenceSubmissionForm"/>
<input type="hidden" name="obid" value=""/>
<input type="hidden" name="aboutlsid" value=""/>
<input type="hidden" name="context" value=""/>


<table class="sequence_submission_outside" width="70%">
<tr>
<td class="outside">
<table class="sequence_submission_inside" id="table7">
        <tr>
                <td colspan="2" halign="right">
                <button type="button" onclick="return brdfpopup('Sequence Submssion','__helptext__')\">Help</button>
        </tr>
	<tr>
		<td colspan="2" >
		<h1 class="section">AgResearch Sequence Submission</h1>
<pre>
<b>
<font color="red">
Note - this form is currently being upgraded to include an additonal PCR section allowing
users to specify PCR cycles used.
</font>
</pre>
		</td>
	</tr>
	<!--
	<tr>
		<td  colspan="2" cellspacing="0" cellpadding="0" width="100%" bgcolor="#339966">
		<h2><a name="add_info2"><font color="#FFCC66">General Submission Information</font></a></h2>
		</td>
	</tr>
	-->
	<tr>
		<td colspan="2" ><span style="letter-spacing: 1pt"><i>(Fields in red are required)</i></span></td>
	</tr>
	<tr>
		<td class="required" width="18%"><label>Your name:</label> </td>
		<td ><input size="50" name="submitted_by" type="text" value="__submitted_by__"></td>
	</tr>
	<tr>
		<td class="required" width="18%"><label>Your email address:</label></td>
		<td ><input size="50" name="submitter_email_address" type="text" value="__submitter_email_address__"> </td>
	</tr>
	<tr>
		<td  width="18%" valign="top"><label>Milestone this submission
		relates to</label><b>:<br>
&nbsp;</b></td>
		<td  valign="top">
		<select name="project" onchange="addSpecifyInput('project','milestone_specify', 'other')">
		<option selected value="76" name="76">76</option>
		<option value="77" name="77">77</option>
		<option value="77A" name="77A">77A</option>
		<option value="78" name="78">78</option>
		<option value="79" name="79">79</option>
		<option value="80" name="80">80</option>
		<option value="81" name="81">81</option>
		<option value="82" name="82">82</option>
		<option value="83" name="83">83</option>
		<option value="84" name="84">84</option>
		<option value="85" name="85">85</option>
		<option value="86" name="86">86</option>
		<option value="87" name="87">87</option>
		<option value="88" name="88">88</option>
		<option value="89" name="89">89</option>
		<option value="90" name="90">90</option>
		<option value="91" name="91">91</option>
		<option value="92" name="92">92</option>
		<option value="93" name="93">93</option>
		<option value="94" name="94">94</option>
		<option value="95" name="95">95</option>
		<option value="96" name="96">96</option>
		<option value="97" name="97">97</option>
		<option value="98" name="98">98</option>
		<option value="99" name="99">99</option>
		<option value="100" name="100">100</option>
		<option value="101" name="101">101</option>
		<option value="102" name="102">102</option>
		<option value="103" name="103">103</option>
		<option value="104" name="104">104</option>
		<option value="105" name="105">105</option>
		<option value="106" name="106">106</option>
		<option value="107" name="107">107</option>
		__existingProjects__
		<option value="other">Other.....</option>
		</select><span id="milestone_specify" style="display:none;"> Please specify:
		<input class="detail" size="30" name="projectother"></span> </td>
	</tr>
	<!--
	<tr>
		<td colspan="2" cellspacing="0" cellpadding="0" width="100%" bgcolor="#339966">
		<h2><a name="add_info1"><font color="#FFCC66">Source Details</font></a></h2>
		</td>
	</tr>
	-->
	<tr>
		<td colspan="2" valign="top">
		<h3 class=section>Sequence Summary/Definition Information</h3>
		<p><label class=required>Sequence Name:</label><a name="pmod0"><input size="91" name="sequence_name"></a></p>
		<p><label class=required>Sequence Description:</label><textarea name="sequence_description" cols="75" rows="1"></textarea></p>
                <!--
		<p><label>Examples:</label> <select name="sequence_description_example" size="1">
		<option>Arabidopsis thaliana mitochondrial pyruvate dehydrogenase E1 alpha
		subunit mRNA, complete cds; nuclear gene for mitochondrial product.
		</option>
		<option>Cloning vector pRB223, complete sequence</option>
		<option>Arabidopsis thaliana ecotype Columbia microsatellite CT12 sequence
		</option>
		</select> <br>
                -->
&nbsp;</p>

		<!-- <hr color="#336699" width="75%" size="1"> -->
		<h3 class=section>Molecule Type</h3>
		<a><label class=required>What kind of molecule did you sequence?</label>
		<select name="mol_type" onchange="addSpecifyInput('mol_type','mol_type_specify','other')">
		<option value="" selected>Please select one</option>
		<option value="genomic DNA">genomic DNA</option>
		<option value="cDNA to mRNA">cDNA to mRNA</option>
		<option value="genomic RNA">genomic RNA</option>
		<option value="pre-mRNA">pre-mRNA</option>
		<option value="tRNA">tRNA</option>
		<option value="rRNA">rRNA</option>
		<option value="snRNA">snRNA</option>
		<option value="scRNA">scRNA</option>
		<option value="other">Other.....</option>
		</select> <span id="mol_type_specify" style="display:none;">Please specify:
		<input class="detail" size="30" name="mol_type_other"> </span></a>
		<p><a name="topology"><label>Topology:</label> 
		<select name="topology">
		<option selected>Linear</option>
		<option>Circular</option>
		</select> </a></p>

		<!-- <hr color="#336699" width="75%" size="1"> -->
		<h3 class=section >Organism Details</h3> 
		<p><a name="org">
		</a></p>
		</td>
	</tr>
	<tr>
		<td valign="top"><a name="org" class="required">
		<label>Organism name (if not in the list, choose "other" and enter name in pop-up field) : </label>&nbsp; </a><br>
&nbsp;</td>
		<td  valign="top"><a name="org">
		<select size="1" name="org_name" onchange="addSpecifyInput('org_name','organism_specify', 'other')">
		<option>Trifolium arvense</option>
		<option>Trifolium occidentale</option>
		<option>Trifolium pratense</option>
		<option selected>Trifolium repens</option>
		__existingSpecies__
		<option value="other">Other</option>
		</select></a><span id="organism_specify" style="display:none;">Please specify:<input size="40" name="org_name_other"></span></td>
	</tr>
	<tr>
		<td  colspan="2" valign="top">
		<p><b>Note:</b> Please enter <strong>either</strong> the binomial &#39;Genus
		species&#39; name <strong>or</strong> a complete descriptive name. Any additional
		source organism description (clone, isolate, strain, cultivar, etc) should
		be entered using the modifiers below. </p>
		<p><b>Note:</b> If sequence is identical in multiple sources (ie: different
		geographies/specimens/isolates/strains),<br>
		then each sequence from each source must be a <b>separate submission</b>.
		</p>

		<!-- <hr color="#336699" width="75%" size="1"> -->
                <h3 class=section><button type="button" onClick="return toggleSection('sample_details');">Sample Details....</button></h3>
                <div id='sample_details' class='hiddentext' style="display:none;">
		You may choose from the following list of samples already defined....  
		<p>
		Samples already defined :
		<select name = "existingSource">
		<option value="" selected> (n/a)
		__existingSources__
		</select>
		<p>
		If you want to name a new sample , enter the name :
		<input type="text" name="sourceName" value="" size="80"/>
		
		<p>
		Source modifiers
		<p>		
		<table id="modifier_table">
			<tr>
				<th nowrap align=left><label>Source Modifier</label></th>
				<th nowrap align=left><label>Value</label></th>
			</tr>
			<tr>
				<td>
				<script>document.write(source_modifier('0'));</script>
				</td>
				<td>
				<script>document.write(source_modifier_text('0'));</script>
				</td>
			</tr>
		</table>
                <button type="button" onclick="addSourceModifiersRow('modifier_table');">Add More Modifiers</button>        

		<!-- <hr color="#336699" width="75%" size="1"> -->
                </div>

                <h3 class=section><button type="button" onClick="return toggleSection('primer_info');">Primer Information....</button></h3>
                <div id='primer_info' class='hiddentext' style="display:none;">
		You may choose from the following lists of forward and reverse primers already submitted, and/or 
		enter a new Primer. <p> <i> (To select more than once primer, hold the control key down and click the selection) </i>
		<p>
		Forward Primers previously submitted :
		<select name = "existingForwardPrimer" multiple size=5>
		<option value="">(none)</option>
		__existingForwardPrimers__
		</select>
                <p>
		Reverse primers previously submitted :
		<select name = "existingReversePrimer" multiple size=5>
		<option value="">(none)</option>		
		__existingReversePrimers__
		</select>		
		
		<p>
	        ...or enter new primers	
		<p>		
		<table id="primers_table">
			<tr>
				<th nowrap align=left><label>Primer Type</label></th>
				<th nowrap align=left><label>Primer Name</label></th>
				<th nowrap align=left><label>Primer Sequence <em>&nbsp;&nbsp;( please ensure these are submitted in the 5' to 3' direction )</em></label></th>
			</tr>
			<tr>
				<td>
				<script>document.write(primer_information('0'));</script>
				</td>
				<td>
				<script>document.write(primer_information_text('0'));</script>
				</td>
				<td>
				<script>document.write(primer_sequence_text('0'));</script>
				</td>
			</tr>
		</table>
                <button type="button" onclick="addPrimersRow('primers_table');">Add More Primers</button>        

		<!-- <hr color="#336699" width="75%" size="1"> -->
                </div>
                <h3 class=section><button type="button" onClick="return toggleSection('vector_info');">Vector Information....</button></h3>
                <div id='vector_info' class='hiddentext' style="display:none;">
		You may choose from the following list of vectors already submitted, and/or 
		enter a new Vector
                <p> <i> (To select more than once vector, hold the control key down and click the selection) </i>
                <p>

		<p>
		Vectors previously submitted : <select name = "existingVector" multiple size=5>
                <option value="">(none)</option>
		__existingVectors__
		</select>
		<p>
		If you want to enter one or more new vectors use the following fields :
		<p>
		
		<table id="vectors_table">
			<tr>
				<th nowrap align=left><label>Vector Name</label></th>
				<th nowrap align=left><label>Priming Information</label></th>
			</tr>
			<tr>
				<td>
				<script>document.write(vector_information('0'));</script>
				</td>
				<td>
				<script>document.write(vector_information_text('0'));</script>
				</td>
			</tr>
		</table>
                <button type="button" onclick="addVectorRow('vectors_table');">Add More Vectors....</button>        
                </div>

		<!-- <hr color="#336699" width="75%" size="1"> -->
                <h3 class=section><button type="button" name="seqFeatBtn" style="" onClick="return toggleSection('feature_info');">Sequence Features....</button></h3>
                <script>if(isIE){getItemByName('seqFeatBtn').style.width="180px";}</script> 
                <div id='feature_info' class='hiddentext' style="display:none;">
		<div align="left">
			<table border="0" width="100%" id="feature_table">
				<tr>
					<td valign="top" width="25%">
					<b>Feature type:</b></td>
					<td valign="top" width="25%">
					<b>Strand: </b>
					</td>
					<td valign="top" width="50%">
					<b>Feature Location:</b></td>
				</tr>
				<tr>
					<td valign="top" width="25%">
					<script>document.write(feature_type('0'));</script>
					</td>
					<td valign="top" width="25%">
					<script>document.write(feature_strand('0'));</script>
					</td>
					<td valign="top" width="50%">
					<script>document.write(feature_loc('0'));</script>
					</td>
				</tr>
			</table>
                    <button type="button" onclick="addFeatureRow('feature_table');">Add More Features....</button>

		<!-- <hr color="#336699" width="75%" size="1"> -->
		</div>
                </div>
                
                <h3 class=section><button type="button" onClick="return toggleSection('PCR_details');">PCR Details....</button></h3>
                    <div id='PCR_details' class='hiddentext' style="display:none;">
            
            <p>
            <font color=red><b>This Section is not yet functional; it is here for testing purposes</b></font>
        <table>
        <tr><td>
            <p>PCR Machine:
        </td><td>
            <select name="PCR_machine" onchange="if(this.value=='Other'){focusByName('new_PCR_machine');}">
            <option value="" selected> (n/a)
            <option value="ABI 9800 Fast Thermal Cycler">ABI 9800 Fast Thermal Cycler
            <option value="BioRad iCycler iQ">BioRad iCycler iQ
            <option value="Cepheid Smart Cycler II">Cepheid Smart Cycler II
            <option value="Eppendorf Mastercycler ep System">Eppendorf Mastercycler ep System
            <option value="Perkin Elmer DNA Thermal cycler">Perkin Elmer DNA Thermal cycler
            <option value="Roche LightCycler 480 Quantitative Realtime PCR">Roche LightCycler 480 Quantitative Realtime PCR
            <option value="Stratagenes MX3000P QPCR System">Stratagenes MX3000P QPCR System
            <option value="Other">Other
            </select>
        </td><td>
            &nbsp;Other PCR Machine (not in list): <input name="new_PCR_machine">
        </td></tr>
        <tr><td align=left style="padding:0 0 0 20">
            Heated lid?:
        </td><td>
            <select name="heated_lid">
            <option value="" selected>
            <option value="yes">Yes
            <option value="no">No
            </select>
        </td></tr>
        <tr><td align=left style="padding:0 0 0 20">
            Hot Start?:
        </td><td colspan=2>
            <select name="heated_lid" onChange="if(this.value=='yes'){focusByName('hot_start_type');}">
            <option value="" selected>
            <option value="yes">Yes
            <option value="no">No
            </select>
            &nbsp; If so, what type: <input name="hot_start_type" size=40>
        </td></tr>
        <tr><td>&nbsp;</td></tr>
        </table>
        
                Reaction Components:
        <table id="preComponentTable">
        <tr><td align=left style="padding:0 0 0 20">
            <p>Taq Polymerase:
        </td><td>
            <select name="taq_polymerase" onchange="if(this.value=='Other'){focusByName('new_taq_polymerase');}">
            <option value="" selected> (n/a)
            <option value="ABI AmpliTaq DNA Polymerase">Applied Biosystems AmpliTaq DNA Polymerase
            <option value="Bioline Biolase DNA Polymerase">Bioline Biolase DNA Polymerase
            <option value="Bioline Taq DNA Polymerase">Bioline Taq DNA Polymerase
            <option value="Eppendorf Taq Polymerase">Eppendorf Taq Polymerase 
            <option value="eEnzyme LLC BioTherm Taq DNA Polymerase">eEnzyme LLC BioTherm Taq DNA Polymerase
            <option value="eEnzyme LLC SupraTaq DNA Polymerase">eEnzyme LLC SupraTaq DNA Polymerase
            <option value="Invitrogen Taq DNA Polymerase Native">Invitrogen Taq DNA Polymerase Native
            <option value="Lucigen EconoTaq DNA Polymerase">Lucigen EconoTaq DNA Polymerase
            <option value="MCLAB Taq DNA Polymerase">MCLAB Taq DNA Polymerase
            <option value="Promega aTaq DNA Polymerase">Promega aTaq DNA Polymerase
            <option value="Promega GoTaq DNA Polymerase">Promega GoTaq DNA Polymerase
            <option value="Promega GoTaq Flexi DNA Polymerase">Promega GoTaq Flexi DNA Polymerase
            <option value="Stratagene Taq DNA Polymerase">Stratagene Taq DNA Polymerase
            <option value="YB-TAQ DNA Polymerase">YB-TAQ DNA Polymerase
            <option value="Other">Other
            </select>
        </td><td>
            &nbsp;Other Taq Polymerase (not in list): <input name="new_taq_polymerase">
        </td></tr>
        <tr><td align=left style="padding:0 0 0 20">
            Reaction Volume:
        </td><td>
            <input name="reaction_volume" size=5> (&micro;l)
        </td></tr>
        <tr><td align=left style="padding:0 0 0 20">
            Oil Added?:
        </td><td>
            <select name="oil_added">
            <option value="" selected>
            <option value="yes">Yes
            <option value="no">No
            </select>
        </td></tr>
        <tr><td>&nbsp;</td></tr>
        </table>
        
            <table id="componentTable">
            <tr><th align=left style="padding:0 0 0 20">
                Component Name
            </th><th>
                Component Concentration
            </th></tr>
            <tr><td align=left style="padding:0 0 0 20">
                <script>document.write(component_name('0','combo'));</script>
            </td><td>
                <script>document.write(component_value('0'));</script>
            </td></tr>
            <tr><td align=left style="padding:0 0 0 20">
                <button type=button name="addCompsBtn" onClick="addReactionComponentRow('componentTable');">Add More Components...</button>
            </td><td>
                <button type=button name="resetCompsBtn" onClick="resetReactionComponentRows('componentTable');">Reset component name fields</button>
            </td></tr>
            </table>
            <br>

            <table id="cyclingTable">
            <tr><td colspan=5>
                Cycling parameters:
            </td></tr>
            
            <tr>
               <td style="padding:10 0 10 0" align="center"><b>Phase</b></td>
               <td style="padding:10 0 10 0" align="center"><b>I</b></td>
               <td style="padding:10 0 10 0" align="center"><b>II</b></td>
               <td style="padding:10 0 10 0" align="center"><b>III</b></td>
               <td style="padding:10 0 10 0" align="center"><b>IV</b></td>
            </tr>
            
            <tr>
               <td align=left style="padding:0 20 0 20">Temp (&deg;C)</td>
            </tr>
            <tr>
               <td align=left style="padding:0 20 10 20">Time (m:s)</td>
            </tr>

            <tr>
               <td align=left style="padding:0 20 0 20">Temp (&deg;C)</td>
            </tr>
            <tr>
               <td align=left style="padding:0 20 10 20">Time (m:s)</td>
            </tr>

            <tr>
               <td align=left style="padding:0 20 0 20">Temp (&deg;C)</td>
            </tr>
            <tr>
               <td align=left style="padding:0 20 10 20">Time (m:s)</td>
            </tr>

            <tr>
               <td align=left style="padding:0 20 0 20">Temp (&deg;C)</td>
            </tr>
            <tr>
               <td align=left style="padding:0 20 10 20">Time (m:s)</td>
            </tr>

            <tr>
               <td align=left style="padding:0 20 0 20"><b>Cycles</b></td>
            </tr>
            </table>
            <br>
            
            <script>
            for (i=1;i<10;i++){
               for(j=0; j<4; j++){
                  addCycleCell(i);
               }
            }
            </script>
            
            <p>
            <button type=button name="addPhaseBtn" onClick="i=0;while(addCycleCell(i)){i++;}">Add Another Phase</button><br>
            <button type=button name="otherInfoBtn" onClick="toggleSection('other_info');">Specify Other Info...?</button><br>
            
            <div id="other_info" style="display: none;">
               Other Info:<br>
               <textarea id="other_info_comment" rows="5" cols="60">(Please enter any information here that is not captured by the other fields of the form.)</textarea>
            </div>
            <p>
            DNA Sequencing info:<br>
            <textarea name="DNA_sequencing_info" rows="5" cols="60"></textarea>
    
            <!-- <hr color="#336699" width="75%" size="1"> -->
                    </div>
            <script>if(isIE){
               getItemByName('otherInfoBtn').style.width="180px";
               getItemByName('addCompsBtn').style.width="180px";
               getItemByName('resetCompsBtn').style.width="191px";}
            </script> 
        
		</td>
		<p></p>
	</tr>
	<!--
	<tr>
		<td  colspan="2" cellspacing="0" cellpadding="0" width="100%" bgcolor="#339966">
		<h2><a name="add_info0"><font color="#FFCC66">Input Data Sequence</font></a></h2>
		</td>
	</tr>
	-->
	<tr>
		<td  colspan="2">
		<h3 class=section><font color="red">Enter DNA Sequence</font></h3>
		<i><b>Important</b></i><font color="red">:</font>
		<ul>
			<li>Use single letter IUPAC code, raw sequence only. </li>
			<li>Sequence must be at least 50 bp in length </li>
			<li>Sequence must be biologically contiguous and not contain any internal
			unknown/unsequenced spacers. </li>
		</ul>
		<p><a name="seqlen"><label>Sequence length in nucleotides:</label>
		<input value="100" name="DNA_seq_length"> </a><b><br>
		</b><textarea name="DNA_seq" rows="10" cols="90"></textarea></p>
                <button type="button" onClick="return validateSequence(true);">Validate Sequence</button> (this will not submit the form)</p>

		<!-- <hr color="#336699" width="75%" size="1"> -->
		<h3 class=section>Additional Information</h3>
		<p>Enter any other biological information for which there is no place on
		the form , or any pertinent instructions that will help process your submission. </p>
		<p><textarea name="additional_comments" rows="4" cols="120"></textarea> </p>
		<p >&nbsp;</p>
		</td>
	</tr>
	<tr>
		<td  colspan="2" >
		<h3 class=section>Post-Processing</h3>
		</td>
	</tr>
	<tr>
		<td  width="18%">
		<p><label>Do you need a directory to upload trace or other files associated with this sequence ?</label><b> </b>
		</p>
		</td>
		<td ><select size="1" name="ftpdir_yes_no">
		<option >Yes</option>
		<option selected >No</option>
		</select></td>
	</tr>
<!--
	<tr>
		<td  width="18%"><label>Number of files you will upload:</label></td>
		<td ><input size="5" value="0" name="filecount"> <input size="5" value="0" type="hidden" name="filecount"></td>
	</tr>
        
-->
	<!--
	<tr>
		<td  width="18%">
		<p><label>Reasons for submission of data to ftp site</label><b> </b></p>
		</td>
		<td >
		<table  id="table10">
			<tr>
				<td>pass on data to colleague </td>
				<td >
				<input type="checkbox" value="false" name="submission_colleague">
				</td>
			</tr>
			<tr>
				<td>archive files on server </td>
				<td >
				<input type="checkbox" value="false" name="submission_archive">
				</td>
			</tr>
			<tr>
				<td>data to be imported into relational database </td>
				<td >
				<input type="checkbox" value="false" name="submission_import">
				</td>
			</tr>
			<tr>
				<td colspan="2">if other specify :
				<input class="detail" size="50" name="submission_reason_other"> </td>
			</tr>
		</table>
		</td>
	</tr>
	-->
        <!--
	<tr>
		<td colspan="2">
		<input type="checkbox" checked value="blastagainst_NCBInr" name="blastagainst_NCBInr"> Blast
		against NCBI NR Protein
		<input type="checkbox" checked value="blastagainst_nt" name="blastagainst_nt"> Blast
		against NCBI nt
        -->
	<!--
		<p><input type="checkbox" value="tracks_medicago" name="add_gbrowse_track"> Display as
		track on Medicago Genome Browser </p>
		<p>Notes:<br>
&nbsp;<textarea name="post_processing_instructions" rows="3" cols="50"></textarea>
		</p>
		</td>
	-->
	</tr>
	<!--
	<tr>
		<td  width="18%">
		<p><label>Notification addresses for this data</label><b> <br>
		</b>The following addresses will receive notification of this submission,
		including description and processing instructions. Clear , replace or add
		addresses as required, one per line.<br>
		Emails will be sent <b>5 minutes</b> after submission.</p>
		</td>
		<td ><textarea rows="6" cols="50" name="post_submission_notify">anar.khan@agresearch.co.nz
</textarea></td>
	</tr>
	-->
	<!--
	<tr>
		<td  colspan="2"><hr>When you have completed the form,
		click the button below. If you have pasted in sequence data this be uploaded
		and processed as you have requested. If you have asked for an ftp directory
		for file upload , then a folder will be created on the server specifically
		for your submission, and a web page will be returned displaying a link to
		the new folder. Clicking on this link should open a file explorer window.
		You can then copy and paste your files straight into the new folder. (Or
		you may use some other ftp client if you prefer)
		<p>Once you have submitted your files to the server, they will be backed
		up to tape within 24 hours of the submission. This includes files submitted
		solely for the purpose of exchange with a colleague. </p>
		<p>The information you have provided on this form will also be recorded
		in the agresearch relational database </p>
		</td>
	</tr>
	-->
	<tr>
		<td colspan="2">
                <script>document.write('<input type="submit" value="Submit" class="submit_button">');</script>
		</td>
	</tr>
</table>
</td>
</tr>
</table>
</form>

</body>

</html>
"""
    
forms_commentForm = """
<!doctype html public "-//w3c//dtd html 4.0 transitional//en"><html>
<head>
<title> AgResearch BRDF Database  - Add Comments </title>
<link rel="stylesheet" type="text/css" href="/css/forms.css">
</head>
<body>
<form name="insertcomment" method="post" enctype="multipart/form-data" action="form.py"> 

<input type="hidden" name="formname" value="commentform"/>
<input type="hidden" name="sessionid" value="%s"/>
<input type="hidden" name="obid" value="%s"/>
<input type="hidden" name="aboutlsid" value="%s"/>
<input type="hidden" name="formstate" value="%s"/>
<input type="hidden" name="context" value="%s"/>
<table border="true">
<tr> 
   <td colspan="2"> 
      <h1 class="top"> AgResearch Data Management</h1>
      <h2>Comment on %s</h2>
   </td>
<tr>
<tr>
      <td colspan="2">
      Comment Text
      <textarea name="commentstring" rows="5" cols="80"></textarea>      
      </td>
</tr>
<tr>
      <td colspan="2">
      Comment Display
      <table border=0>
      <tr>
      <td bgcolor="#EE9999"> <b><i> Comment Text </i></b></td>
      <td> <input name="style_bgcolour" type="radio" value="#EE9999" checked> </td>
      <tr>
      <td bgcolor="#99EE99"> <b><i> Comment Text </i></b></td>
      <td> <input name="style_bgcolour" type="radio" value="#99EE99" > </td>
      <tr>
      <td bgcolor="#9999EE"> <b><i> Comment Text </i></b></td>
      <td> <input name="style_bgcolour" type="radio" value="#9999EE" > </td>
      <tr>
      <td bgcolor="#EEEE99"> <b><i> Comment Text </i></b></td>
      <td> <input name="style_bgcolour" type="radio" value="#EEEE99" > </td>
      <tr>
      <td bgcolor="#EE99EE"> <b><i> Comment Text </i></b></td>
      <td> <input name="style_bgcolour" type="radio" value="#EE99EE" > </td>
      <tr>
      <td bgcolor="#99EEEE"> <b><i> Comment Text </i></b></td>
      <td> <input name="style_bgcolour" type="radio" value="#99EEEE" > </td>            
      </tr>
      </table>

      </td>
</tr>
<tr>
      <td colspan="2">
      Visibility of this comment
      <select name="visibility">
        <option value="private"> Private </option>
        <option value="public" selected> Public </option>
      </select>
      </td>
</tr>
<tr>
      <td >
         <p >Notification instructions for this update
      </td>
      <td class="input">
         <table  class="input">
            <tr>
            <td class="input">
            <p>
            The following addresses will receive notification of this data update
            </p>
            Clear , replace or add addresses as required, one per line
            </td>
            </tr>
            <tr>
            <td class="input">
               <textarea rows="6" cols="50">
santa.claus@north.pole.planet
               </textarea>
            </td>
	    <tr>
            <td class="input">
            Emails will be sent 
            <select name="emaildelay">
            <option value="0" selected> on submission of this form
            <option value="5"> 5 minutes after submission of this form
            <option value="30"> 30 minutes after submission of this forom
            <option value="60"> 60 minutes after submission of this forom
            </select>
            </td>
            </tr>
            </tr>
         </table>
      </td>
    </tr>
<tr>
   <td colspan="2">
   <p class="footer">
   <input type="submit" value="Submit Comment"/>
   </p>
    </td>
</tr>
</table>

<a href="mailto:alan.mcculloch@agresearch.co.nz;jason.mitchell@agresearch.co.nz?Subject=Agbrdf Portal Request"/> Contact us </a>

</form>
</body>
</html>"""


forms_uriForm = """
<!doctype html public "-//w3c//dtd html 4.0 transitional//en"><html>
<head>
<title> AgResearch Data Management - Attach Hyperlink </title>
<link rel="stylesheet" type="text/css" href="/css/forms.css">
</head>
<body>
<form name="insertcomment" method="post" enctype="multipart/form-data" action="form.py">
<input type="hidden" name="formname" value="uriform"/>
<input type="hidden" name="sessionid" value="%s"/>
<input type="hidden" name="obid" value="%s"/>
<input type="hidden" name="aboutlsid" value="%s"/>
<input type="hidden" name="formstate" value="%s"/>
<input type="hidden" name="context" value="%s"/>
<table border="true">
<tr> 
   <td colspan="2"> 
      <h1 class="top"> AgResearch Data Management</h1>
      <h2>Attach Hyperlink to %s</h2>
   </td>
<tr>
<tr>
      <td colspan="2">
      URI string - the address to look up
      <input name="uristring" type="text" size="80" value=""/>
      <br/>
      <pre>
      examples :

      link to NCBI : http://ncbi.nlm.nih.gov/nucleotide?val=NM_015435
      link to SGP database object : http://localhost/cgi-bin/agbrdf/fetch.py?obid=48813&context=default&target=ob
      link to a local file : file:///m:/projects/brdf/BRDFDatabaseSchema.doc
      
      </pre>
      </td>
</tr>
<tr>
      <td colspan="2">
      Display String - the text that should appear on the page 
      <input name="displaystring" type="text" size="80" value=""/>
      <br/>
      <pre>
      examples :

      link to NCBI : <a href="http://ncbi.nlm.nih.gov/gene?val=CARD15" target="external"> CARD15 at NCBI </a>
      link to agresearch database object : <a href="https://sgpbioinformatics.agresearch.co.nz/cgi-bin/agresearch/fetch.py?obid=425478&context=default&target=ob" target="external"> TRPM1 </a>
      link to a local file : <a href="file:///m:/projects/brdf/BRDFDatabaseSchema.doc" target="external"> BRDF Schema on my m:\ drive </a>
      
      </pre>
      </td>
</tr>
<tr>
      <td colspan="2">
      Visibility of this hyperlink
      <select name="visibility">
        <option value="private"> Private </option>
        <option value="public" selected> Public </option>
      </select>
      </td>
</tr>
<tr>
   <td colspan="2">
   <p class="footer">
   <input type="submit" value="Submit Hyperlink"/>
   </p>
    </td>
</tr>
</table>

<a href="mailto:alan.mcculloch@agresearch.co.nz;jason.mitchell@agresearch.co.nz?Subject=Agbrdf Portal Request"/> Contact us </a>

</form>
</body>
</html>"""


forms_editAnalysisProcedureForm = """
<!doctype html public "-//w3c//dtd html 4.0 transitional//en"><html>
<head>
<title> AgResearch BRDF Database  - Edit Analysis Procedure Code </title>
<link rel="stylesheet" type="text/css" href="/css/forms.css">
</head>
<body>
<form name="insertcomment" method="post" enctype="multipart/form-data" action="form.py">

<input type="hidden" name="formname" value="editAnalysisProcedureForm"/>
<input type="hidden" name="sessionid" value="%(sessionid)s"/>
<input type="hidden" name="obid" value="%(obid)s"/>
<input type="hidden" name="xreflsid" value="%(xreflsid)s"/>
<input type="hidden" name="formstate" value="%(formstate)s"/>
<input type="hidden" name="context" value="%(context)s"/>
<table border="true">
<tr> 
   <td colspan="2"> 
      <h1 class="top"> AgResearch Application Management</h1>
      <h2>Editing Procedure : %(procedurename)s</h2>
   </td>
<tr>
<tr>
   <td>
<DL>
<DT>Record Created by %(createdby)s on %(createddate)s
<DT>Last Updated by %(lastupdatedby)s on %(lastupdateddate)s
<DT>Author %(author)s on %(authordate)s
</DL>
   </td>
</tr>
<tr>
      <td colspan="2">
      Source Code
      <p/>
      <textarea name="sourcecode" rows="40" cols="150">%(sourcecode)s</textarea>      
      </td>
</tr>
<tr>
      <td colspan="2">
      Annotation of changes
      <p/>
      Please enter comments describing your changes - be as detailed as you can or consider appropriate
      <p/>
      <textarea name="procedurecomment" rows="10" cols="80"></textarea>
      <p/>
      previous comments :
      <pre>
      %(oldcomments)s
      </pre>
      </td>
</tr>
<tr>
      <td colspan="2">
      Presentation Template
      <p/>
      <textarea name="presentationtemplate" rows="40" cols="132">%(presentationtemplate)s</textarea>
      </td>
</tr>
<tr>
      <td colspan="2">
      Input / Output
      <p/>
      Number of data input files <input type="text" name="textincount" value="1" size="2"/>
      <p/>
      Number of data output files <input type="text" name="textoutcount" value="1" size="2"/>
      <p/>
      Number of image output files <input type="text" name="imageoutcount" value="1" size="2"/>
      </td>
</tr>
<tr>
      <td colspan="2">
      Management of changes
      <p/>
      Version control :  <select name="versioning">
      <option value="overwrite" selected> update this procedure
      <option value="newprocedure"> store this as a new procedure  
      </select>
      <p/>
      enter new procedure details if applicable  
      <p/>
      new procedure name : <input type="text" name="newprocedurename" size="80" value=""/>
      <p/> 
      new procedure description : <input type="text" name="newproceduredescription" size="130" value=""/>
      <p/>
      <select name="newproceduretype">
      new procedure type : <option value="R procedure"> R script
      </select>
      <p/>
      Keep History <input type=checkbox name="keep_history" checked> (recommended for major changes - this will allow rollback)
      </td>
<tr>
      <td colspan="2">
      Security
      <p/>      
      Visibility of source code for this version
      <select name="readpermission">
        <option value="private"> Private - source code only visible to submitter </option>
        <option value="public" selected> Public - always visible </option>
        <option value="protected"> Restricted to submitter and those in the following list...
      </select>
      <p/>
      <textarea name="readaccesslist" rows="4" cols="40"></textarea>
      <p/>
      Maintenance of source code for this version
      <select name="writepermission">
        <option value="private" selected> Private - source code can only be updated by submitter </option>
        <option value="public"> Public - anybody can update. (Note : all updates will be moderated)</option>
        <option value="protected"> Restricted - only submitter and those in the following list can update. (Note : updates will be moderated if listed user not prior-approved)</option>
      </select>
      <p/>
      <textarea name="writeaccesslist" rows="4" cols="40"></textarea>
      </td>
</tr>
<tr>
   <td colspan="2">
   <p class="footer">
   <input type="submit" value="Submit Update"/>
   </p>
    </td>
</tr>
</table>

<a href="mailto:alan.mcculloch@agresearch.co.nz;jason.mitchell@agresearch.co.nz?Subject=Agbrdf Portal Request"/> Contact us </a>

</form>
</body>
</html>"""



forms_linkAnalysisProcedureForm = """
<!doctype html public "-//w3c//dtd html 4.0 transitional//en"><html>
<head>
<title> AgResearch BRDF Database  - Link Analysis Procedure Code </title>
<link rel="stylesheet" type="text/css" href="/css/forms.css">
</head>
<body>
<form name="insertcomment" method="post" enctype="multipart/form-data" action="form.py">

<input type="hidden" name="formname" value="editAnalysisProcedureForm"/>
<input type="hidden" name="sessionid" value="%(sessionid)s"/>
<input type="hidden" name="obid" value="%(obid)s"/>
<input type="hidden" name="xreflsid" value="%(xreflsid)s"/>
<input type="hidden" name="formstate" value="%(formstate)s"/>
<input type="hidden" name="context" value="%(context)s"/>
<table border="true">
<tr> 
   <td colspan="2"> 
      <h1 class="top"> AgResearch Application Management</h1>
      <h2>Add Analysis to  : %(datasourceob)s</h2>
   </td>
<tr>
<tr>
      <td colspan="2">
      Choose Analysis to add
      <p/>
      __analysisprocedureselect__
      </td>
</tr>
<tr>
      <td colspan="2">
      Customise Output
      <p/>
      Output heading <input type="text" name="sectionheading" value="" size="80"/>
      </td>
</tr>
<tr>
   <td colspan="2">
   <p class="footer">
   <input type="submit" value="Submit Update"/>
   </p>
    </td>
</tr>
</table>

<a href="mailto:alan.mcculloch@agresearch.co.nz;jason.mitchell@agresearch.co.nz?Subject=Agbrdf Portal Request"/> Contact us </a>

</form>
</body>
</html>"""


forms_defineArrayHeatMapForm = """
<!doctype html public "-//w3c//dtd html 4.0 transitional//en"><html>
<head>
<title> AgReseach Microarray Database  - Define Heat Map </title>
<link rel="stylesheet" type="text/css" href="/css/forms.css">
</head>
<body>
<form name="microarrayheatmap" method="post" enctype="multipart/form-data" action="form.py">

<input type="hidden" name="formname" value="defineArrayHeatMapForm"/>
<input type="hidden" name="sessionid" value="%(sessionid)s"/>
<input type="hidden" name="obid" value="%(obid)s"/>
<input type="hidden" name="formstate" value="%(formstate)s"/>
<input type="hidden" name="context" value="%(context)s"/>
<table border="true">
<tr> 
   <td colspan="2"> 
      <h1 class="top"> Define Microarray Heatmap </h1>
      <h2>Heatmap Procedure : %(procedurename)s : %(proceduredescription)s</h2>
   </td>
<tr>
<tr>
   <td>
   Choose Heatmap procedure :
   <select name="procedurename">
   <option name="simpleheatmapmaker.r"> simpleheatmapmaker.r
   </select>
   </td>
</tr>

<tr>
   <td>
   Specify a name for your heatmap :
   <input name="heatmapname" size="40" value=""/>
   </td>
</tr>


<tr>
      <td colspan="2">
      Select arrays and slides  : 
      __arrayselect__
      </td>
</tr>
<tr>
      <td colspan="2">
      <div id="arrayslides_div">
      </div>
      </td>
</tr>
<tr>
      <td colspan="2">
      Paste in a list of array probes 
      <textarea name="arrayprobes" rows=15 cols=80></textarea>
      </td>
</tr>
<tr>
   <td colspan="2">
   <p class="footer">
   <input type="submit" value="Submit heatmap definition"/>
   </p>
   </td>
</tr>
</table>

<a href="mailto:alan.mcculloch@agresearch.co.nz?Subject=Microarray Database Request"/> Contact us </a>

</form>
</body>
</html>"""


form_fileSubmissionForm = r"""
<head>
<title> AgResearch Bioinformatics File Upload</title>
<link rel="stylesheet" type="text/css" href="/css/forms.css">
<base target="_self">
<script type="text/javascript">
//<!--this is used to hide the javascipt in older browsers

var file_count = 1;

function setFileCount(count){
   var field = document.getElementById("fileCount");
   field.setAttribute("value", count);
}

function FileDescText(id){ return 'Description ' +id+ ': \n';}
function FileDescField(id){ return '<INPUT name=desc'+id+' size=65></INPUT>\n';}

function FileText(id){ return 'File '+(id)+': \n';}
function FileField(id){ return '<INPUT type=File name=file'+id+' size=35></INPUT>\n';}

function FileTypeText(id){ return 'Type of file ' + id + ': \n';}
function FileTypeField(id){ return '<select name="type' +id+ '" >\n' +
             '<option value="" selected>\n' +
             '<option value="exp">Experimental Data\n' +
             '<option value="meta">Metadata\n' +
             '<option value="derived">Derived Data\n' +
             '<option value="measure">Animal Measurements\n' +
             '<option value="docs">Documents\n' +
             '<option value="image">Image\n' +
             '<option value="Other">Other\n' +
          '</select>\n';}

function addFileRow(tableID) {
    var table = document.getElementById(tableID);
    var row = table.insertRow(table.rows.length);
        var cell = row.insertCell(0);
        cell.vAlign="top";
        cell.innerHTML = FileDescText(file_count+1);
        var cell = row.insertCell(1);
        cell.vAlign="top";
        cell.colSpan="2";
        cell.innerHTML = FileDescField(file_count+1);
        var cell = row.insertCell(2);
        cell.vAlign="top";
        cell.innerHTML = "&nbsp";
    var row = table.insertRow(table.rows.length);
        var cell = row.insertCell(0);
        cell.vAlign="top";
        cell.innerHTML = FileText(file_count+1);
        var cell = row.insertCell(1);
        cell.vAlign="top";
        cell.innerHTML = FileField(file_count+1);
        var cell = row.insertCell(2);
        cell.vAlign="top";
        cell.innerHTML = FileTypeText(file_count+1);
        var cell = row.insertCell(3);
        cell.vAlign="top";
        cell.innerHTML = FileTypeField(file_count+1);
        file_count++;
        setFileCount(file_count);
}

function checkAll() {
   //submittedby field
   if(trim(generalsubmission.submittedby.value) == "") {
      highLight(generalsubmission.submittedby,"Please enter your name");
      return false;
   }
   else {
      lowLight(generalsubmission.submittedby);
   }   
   
   //emailaddress field
   if(trim(generalsubmission.emailaddress.value) == "") {
      highLight(generalsubmission.emailaddress,"Please enter your email address");
      return false;
   }
   else {
      lowLight(generalsubmission.emailaddress);
   }   
   
   //projectID and otherProject fields
   if(trim(generalsubmission.projectID.value) == "" && trim(generalsubmission.otherProject.value) =="") {
      lowLight(generalsubmission.otherProject);
      highLight(generalsubmission.projectID,"Please select a project. If your project is not listed, select \"Other\" " +
      "and enter the code into the \"Other Project\" field. In the future this code will appear in the dropdown box.");
      return false;
   }
   else if (trim(generalsubmission.projectID.value) == "Other" && trim(generalsubmission.otherProject.value) =="") {
      lowLight(generalsubmission.projectID);
      highLight(generalsubmission.otherProject,"Please enter your project code into the \"Other Project\" field.");
      return false;
   }
   else if (trim(generalsubmission.projectID.value) == "" && trim(generalsubmission.otherProject.value) !="") {
      lowLight(generalsubmission.otherProject);
      highLight(generalsubmission.projectID,"Please select \"Other\" from the dropdown box.");
      return false;
   }
   else if (trim(generalsubmission.projectID.value) != "Other" && trim(generalsubmission.otherProject.value) !="") {
      lowLight(generalsubmission.projectID);
      highLight(generalsubmission.otherProject,"Please remove the value from the \"Other Project\".");
      return false;
   }
   else {
      lowLight(generalsubmission.projectID);
      lowLight(generalsubmission.otherProject);
   }
   
   //sub-prog field
   if(trim(generalsubmission.subProgram.value) == "") {
      highLight(generalsubmission.subProgram,"Please enter a sub-program.");
      return false;
   }
   else {
      lowLight(generalsubmission.subProgram);
   }
   
   //reason field
   if(trim(generalsubmission.reason.value) == "") {
      highLight(generalsubmission.reason,"Please enter a reason for submission.");
      return false;
   }
   else {
      lowLight(generalsubmission.reason);
   }
   
   //folder field
   if(trim(generalsubmission.folder.value) == "" && trim(generalsubmission.newFolder.value) =="") {
      lowLight(generalsubmission.newFolder);
      highLight(generalsubmission.folder,"Please select a submission name. If your want to create a new submission, " +
      "select \"New Submission\" and enter the submission name into the \"New Submission\" field. In the future this " +
      "submission-name will appear in the dropdown box.");
      return false;
   }
   else if (trim(generalsubmission.folder.value) == "New Submission" && trim(generalsubmission.newFolder.value) =="") {
      lowLight(generalsubmission.folder);
      highLight(generalsubmission.newFolder,"Please enter the new submission name into the \"New Submission\" field.");
      return false;
   }
   else if (trim(generalsubmission.folder.value) == "" && trim(generalsubmission.newFolder.value) !="") {
      lowLight(generalsubmission.newFolder);
      highLight(generalsubmission.folder,"Please select \"New Submission\" from the dropdown box.");
      return false;
   }
   else if (trim(generalsubmission.folder.value) != "New Submission" && trim(generalsubmission.newFolder.value) !="") {
      lowLight(generalsubmission.folder);
      highLight(generalsubmission.newFolder,"Please remove the value from the \"New Submission\" field.");
      return false;
   }
   else if (trim(generalsubmission.newFolder.value).match(/[^\w ]/) != null) {
      lowLight(generalsubmission.folder);
      highLight(generalsubmission.newFolder,"You may only name your submission using the characters 'A-Z', 'a-z', '0-9', '_' and spaces.");
      return false;
   }
   else {
      lowLight(generalsubmission.folder);
      lowLight(generalsubmission.newFolder);
   }
   
   //The loop below just checks that the file-desc, file and file-type fields 
   //are either all filled in, or none are.
   for (j=0; j<file_count; j++) {
      var theDesc = eval("document.generalsubmission.desc"+(j+1));
      var theFile = eval("document.generalsubmission.file"+(j+1));
      var theType = eval("document.generalsubmission.type"+(j+1));
      lowLight(theDesc);
      lowLight(theFile);
      lowLight(theType);
      if ((trim(theDesc.value) == '' && trim(theFile.value) == '' && trim(theType.value) == '') ||
          (trim(theDesc.value) != '' && trim(theFile.value) != '' && trim(theType.value) != '')) {
         //Do Nothing
      } else if (trim(theDesc.value) == '') {
         highLight(theDesc,"Please enter a description.");
         return false;
      } else if (trim(theFile.value) == '') {
         highLight(theFile,"Please select a file.");
         return false;
      } else if (trim(theType.value) == '') {
         highLight(theType,"Please enter a file type.");
         return false;
      }
   }

   //fileDesc field
   if(trim(generalsubmission.desc1.value) == "") {
      highLight(generalsubmission.desc1,"Please enter a description of the file.");
      return false;
   }
   else {
      lowLight(generalsubmission.desc1);
   }   
   
   //file field
   if(trim(generalsubmission.file1.value) == "") {
      highLight(generalsubmission.file1,"You must insert a file location.");
      return false;
   }
   else {
      lowLight(generalsubmission.file1);
   }
   
   //fileType field
   if(trim(generalsubmission.type1.value) == "") {
      highLight(generalsubmission.type1,"Please enter a value for the type of file.");
      return false;
   }
   else {
      lowLight(generalsubmission.type1);
   }
   
   //desc field
   if(trim(generalsubmission.description.value) == "") {
      highLight(generalsubmission.description,"Please enter a description of the file(s)");
      return false;
   }
   else {
      lowLight(generalsubmission.description);
   }
   
   //setFileCount();
   btn = document.getElementById("submitButton");
   btn.value = "Uploading Files, please wait...";
   btn.disabled = true;
   return true;

}
 
function highLight(item,message) {
   eval("item.style.background = 'red'");
   window.alert(message);
   item.focus();
}

function lowLight(item) {
   eval("item.style.background = 'white'");
}

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

var purpose = '<p class="fieldname"><b>Files to submit</b>';
   
function showLowerText(selectObj) {
   var table = document.getElementById('Outer_table');
   var numRows = table.rows.length;
   var value = selectObj.selectedIndex;
   if (value == 0 ) {
      for (i = 7; i < numRows; i++) {
         var row = table.rows[i];
         row.style.display = "none";
      }
   }
   else {
      if (value == 4 ) {
         purpose = '<p class="fieldname"><b>File metadata to record</b>';
         table.rows[8].cells[0].innerHTML = purpose;
      }
      else {
         purpose = '<p class="fieldname"><b>Files to submit</b>';
         table.rows[8].cells[0].innerHTML = purpose;
      }
      
      for (i = 7; i < numRows; i++) {
         var row = table.rows[i];
         row.style.display = "";
      }
   }
}

var folderArray = new Array();
folderArray[""] = ["New Submission"];
folderArray["Other"] = ["New Submission"];
__Array_Entries__

function updateFolder(selectObj) {
   var idx = selectObj.selectedIndex;
   var foldr = selectObj.options[idx].value;
   var list = folderArray[foldr];
   var box = document.forms[0].folder;
   while (box.length > 0) {
      box.remove(0);
   }
   
   for (i = -1; i < list.length; i++) {
         newOpt = document.createElement("option");
      if (i == -1) {
         newOpt.text = '';
         newOpt.value = '';
         newOpt.selected = true;
      } else {
         newOpt.text = list[i];
         newOpt.value = list[i];
      }
      var browserName = navigator.appName;
      if (browserName == "Netscape" || browserName == "Opera") { 
         box.add(newOpt, null);
      }
      else if (browserName=="Microsoft Internet Explorer") {
         box.add(newOpt);
      }
   }
}

//this is used to hide the javascipt in older browsers-->
</script>
</head>
<body>
<form name="generalsubmission" onSubmit="return checkAll();" method="post" enctype="multipart/form-data" action="form.py">
<input type="hidden" name="sessionid" value="0"/>
<input type="hidden" name="formname" value="fileSubmissionForm"/>
<input type="hidden" name="fileCount" id="fileCount" value="1"/>
<table border="true" id="Outer_table">
   <tr> 
      <td colspan="2"> 
         <h1 class="top"> AgResearch Bioinformatics File Upload Form</h1>
      </td>
   </tr>
   <tr>
      <td colspan="2" class="fieldname">
       <p>This form is for uploading files and documents to the AgResearch Bioinformatics server.
          Uploaded files can be linked online to analysis scripts executed on the bioinformatics server, and
          you and others can annotate these files with comments and search for files by keyword
      </td>
   </tr>
   <tr>
      <td class="fieldname">
         <p class="fieldname"><b>Your name</b>
      </td>
      <td class="input">
          <input name="submittedby" value="__submitted_by__" size="50" type="text"/>
      </td>
   </tr>
   <tr>
      <td class="fieldname">
         <p class="fieldname"><b>Your email address</b>
      </td>
      <td class="input">
          <input name="emailaddress" value="__submitter_email_address__" size="50" type="text"/>
      </td>
   </tr>    
   <tr>
      <td class="fieldname">
         <p class="fieldname"><b>Project ID</b>
      </td>
      <td class="input">
          <select name="projectID" onchange="updateFolder(this)">
             <option value="" selected>
             __EXISTING_PROJECTS__
             <option value="Other">Other
          </select>
          &nbsp;&nbsp; Other project (not in list): 
          <input name="otherProject" value="" size="40"/>
      </td>
   </tr>    
   <tr>
      <td class="fieldname">
         <p class="fieldname"><b>Section:</b>
      </td>
      <td class="input">
         <SELECT name="subProgram">
            <OPTION value="" selected>
            <OPTION value="Animal Genomics">Animal Genomics
            <OPTION value="Plant Genomics">Plant Genomics
            <OPTION value="Food Safety">Food Safety
            <OPTION value="Animal Health">Animal Health
            <OPTION value="Bioinformatics">Bioinformatics
         </SELECT>
      </td>
   </tr>
   <tr>   
      <td class="fieldname"> 
         <p class="fieldname"><b>Purpose of submitting data</b>
      </td>
      <td class="input">
         <SELECT name="reason" onchange="showLowerText(this)">
            <OPTION value="" selected>Please select an option:
            <OPTION value="transformation">Data Transformation
            <OPTION value="colleague">pass on data to colleague
            <OPTION value="archive">archive files on server
            <OPTION value="import">data to be imported into database
            <OPTION value="meta">record only file meta-data (i.e. don't upload the actual file)
         </SELECT>
       </td>
   </tr>
   <tr style="display: none">
      <td>
         <p class="fieldname"><b>Submission (Folder) name</b></p>
      </td>
      <td>
         <SELECT name="folder">
            <OPTION value="" selected>
            <OPTION value="New Submission">New Submission
         </SELECT>
         &nbsp;&nbsp; New submission (not in list):
         <input name="newFolder" value="" size="40">
      </td>
   </tr>
   <tr style="display: none">
      <td>
         <script>document.write(purpose)</script>
      </td>
      <td>
         <table id="File_table" align=left border=0 style="background-color:lightblue">
            <tr>
               <td><script>document.write(FileDescText('1'))</script></td>
               <td colspan="2"><script>document.write(FileDescField('1'))</script></td>
               <td align="right">
                  <button type="button" id="addButton" onclick="addFileRow('File_table');">Add Another File</button>
               </td>
            </tr>
            <tr>
               <td><script>document.write(FileText('1'))</script></td>
               <td><script>document.write(FileField('1'))</script></td>
               <td><script>document.write(FileTypeText('1'))</script></td>
               <td><script>document.write(FileTypeField('1'))</script></td>
            </tr>
         </table>
      </td>
   </tr>
   <tr style="display: none">
      <td>
         <p class="fieldname"><b>Description of this data</b>
      </td>
      <td>
         <textarea name="description" cols="50" rows="3"></textarea>
      </td>
   </tr>
   <tr style="display: none">
      <td>
         <p class="fieldname"><b>Processing instructions for this data</b>
      </td>
      <td>
         <textarea name="instructions" cols="50" rows="3"></textarea>
      </td>
   </tr>
   <tr style="display: none">
      <td colspan="2">
      <script>document.write('<p class="footer"><input id="submitButton" type="submit" value="Upload Files" class="submit_button">');</script>
      </td>
   </tr>
</table>
</form>
</body>
</html>"""


form_microarrayProtocolForm = r"""
<html>
<head>
<title>AgResearch - Microarray Upload Form</title>
<style>
body        {margin-top: 1cm ; margin-bottom: 1cm; margin-left: 5%; margin-right: 5%; 
        font-family: arial, helvetica, geneva, sans-serif;BACKGROUND: #f0f9ff}

p        {margin-top: .3cm ; margin-bottom: .3cm; margin-left: .4cm; margin-right: .4cm; 
        font-family: arial, helvetica, geneva, sans-serif}
p.fieldname     {margin-top: .3cm ; margin-bottom: .3cm; margin-left: .4cm; margin-right: .4cm; 
        font-family: arial, helvetica, geneva, sans-serif}
p.footer    {text-align: center ; margin-top: 0.5cm ; margin-bottom: 0.5cm; font-family: arial, helvetica, geneva, sans-serif}

b.b        {font-family: arial, helvetica, geneva, sans-serif; font-weight: 700; color: #424b50}
ul        {font-family: arial, helvetica, geneva, sans-serif}
ol        {font-family: arial, helvetica, geneva, sans-serif}
dl        {font-family: arial, helvetica, geneva, sans-serif}

th              {font-family: arial, helvetica, geneva, sans-serif; font-weight: 400}

h1        {text-align: center; color: #388fbd; 
        font-family: arial, helvetica, geneva, sans-serif}
h1.new          {text-align: center; color: #4d585e;
                font-family: arial, helvetica, geneva, sans-serif}
h1.b1           {margin-top: 0.5cm; text-align: center; color:#2d59b2;
                font-family: arial, helvetica, geneva, sans-serif}
h1.b2           {margin-top: 0.5cm; text-align: center; color:#1d7db5;
                font-family: arial, helvetica, geneva, sans-serif}
h1.top        {margin-top: 0.5cm; text-align: center; color: blue;
        font-family: arial, helvetica, geneva, sans-serif}

h2        {text-align: center; font-family: arial, helvetica, geneva, sans-serif}
h3        {font-family: arial, helvetica, geneva, sans-serif}
h4        {font-family: arial, helvetica, geneva, sans-serif}
h5        {font-family: arial, helvetica, geneva, sans-serif}
h6        {font-family: arial, helvetica, geneva, sans-serif}
a         {font-family: arial, helvetica, geneva, sans-serif}

table       {background-color: antiquewhite}

input.detail       {margin-left: 1cm}

textarea.detail    {margin-left: 1cm}

td        {font-family: arial, helvetica, geneva, sans-serif}
td.fieldname    {font-family: arial, helvetica, geneva, sans-serif}

tr          {background-color: #FF9292}
.plainTable        {background-color: #FF9292}
a:hover     {color: blue; text-decoration: underline }

.color0          {border: solid black; border-width: 5px; width: 80px; height: 80px}
.color1          {background-color: #FF9292; border: solid black; border-width: 1px; cursor: pointer; width: 88px; height: 88px}
.color2          {background-color: #FFDA92; border: solid black; border-width: 1px; cursor: pointer; width: 88px; height: 88px}
.color3          {background-color: #FFFF92; border: solid black; border-width: 1px; cursor: pointer; width: 88px; height: 88px}
.color4          {background-color: #B1FF92; border: solid black; border-width: 1px; cursor: pointer; width: 88px; height: 88px}
.color5          {background-color: #92E7FF; border: solid black; border-width: 1px; cursor: pointer; width: 88px; height: 88px}
.color6          {background-color: #9C92FF; border: solid black; border-width: 1px; cursor: pointer; width: 88px; height: 88px}
.color7          {background-color: #F392FF; border: solid black; border-width: 1px; cursor: pointer; width: 88px; height: 88px}

.arrow           {font-size: 200%; width: 40px}
</style>
<script language="JavaScript">

var alreadySubmitted = false;

function checkAll() {
   // make sure we have not already submitted this form
   if(alreadySubmitted) {
      window.alert("This Form has already been submitted, please wait");
      return false;
   }

   // check the protocolName is populated, and doesn't match any existing ones
   var duplicatedName = false;
   var ar = document.arrayform.protocol;
   var prot = document.arrayform.protocolName;
   for (j=0; j < ar.length; j++) {
      if (ar[j].value == trim(prot.value)) {
         duplicatedName = true;
         break;
      }
   }
   if (duplicatedName) {
      highLight(prot,"You must specify a unique Protocol name.");
      return false;
   } else if (trim(prot.value).match(/[']/) != null) {
      highLight(prot,"Sorry, but you cannot use an apostrophe in the Protocol name. " + 
      "If you need one, you could use a back-tick, \"`\" (which should be just to the left of the \"1\" key).");
      return false;
   } else {
      lowLight(prot);
   }

// This version is removed, as the "other type" field has removed.
//   // check the protocolType is selected, and if "Other", then the "Other Type" field is populated.
//   if (document.arrayform.protocolType.value == "" && document.arrayform.otherType.value == "") {
//      lowLight(document.arrayform.otherType);
//      highLight(document.arrayform.protocolType,"You must select a Protocol type.");
//      return false;
//   }
//   else if (document.arrayform.protocolType.value == "Other" && document.arrayform.otherType.value == "") {
//      lowLight(document.arrayform.protocolType);
//      highLight(document.arrayform.otherType,"You must enter a new Protocol type.");
//      return false;
//   }
//   else if (document.arrayform.protocolType.value != "Other" && document.arrayform.otherType.value != "") {
//      lowLight(document.arrayform.otherType);
//      highLight(document.arrayform.protocolType,"If entering a new Protocol type, you need to select \"Other\" from the list.");
//      return false;
//   }
//   else {
//      lowLight(document.arrayform.protocolType);
//      lowLight(document.arrayform.otherType);
//   }
   
   // check the protocolType is selected
   if (document.arrayform.protocolType.value == "") {
      highLight(document.arrayform.protocolType,"You must select a Protocol type.");
      return false;
   }
   else {
      lowLight(document.arrayform.protocolType);
   }
   
   //check that they've entered something into the description field.
   if (trim(document.arrayform.protocolDesc.value) == "(Please enter a description here)") {
      highLight(document.arrayform.protocolDesc,"Please enter a description of the Protocol.");
      return false;
   }else if (trim(document.arrayform.protocolDesc.value).length <= 30) {
      highLight(document.arrayform.protocolDesc,"Please enter a longer description of the Protocol (i.e. > 30 characters). Spaces at the start and end do not count.");
      return false;
   }
   else {
      lowLight(document.arrayform.protocolDesc);
   }   

   // finally, set the submitted flag
   btn = document.getElementById("submitButton");
   btn.value = "Submitting, please wait...";
   btn.disabled = true;
   
   alreadySubmitted = true;
   return true;
}

function highLight(item,message) {
   item.style.background = 'red';
   window.alert(message);
   item.focus();
} // assume IE

function lowLight(item) {
   item.style.background = '';
}

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

function goToPage(pageName) {
   return location.href="form.py?formname=" + pageName;
}

</script>
</head><body>
<FORM name="arrayform" onSubmit="return checkAll();" METHOD="POST" ENCTYPE="multipart/form-data" ACTION="/cgi-bin/agbrdf/form.py" >
<input type="HIDDEN" name="formname" value="microarrayProtocolForm"/>
<input type="HIDDEN" name="sessionid" value="0"/>
<table border="true" id="Top_table" width=100%>
   <tr> 
      <td colspan="2"> 
         <h1 class="top">AgResearch Microarray Upload Form</h1>
      </td>
   </tr>
   <tr> 
      <td colspan="2"> 
         <table align=center class=plainTable style="border-width: 0">
            <tr align=center valign=middle>
               <td class=color0 title="Define one or more protocols if required">
                  <img src="/images/protocol.gif" border="0" height="42" width="42"/>
                  <br>Protocol
               </td>
               <td class=arrow>
                  &rarr;
               </td>
               <td class=color2 title="Define one or more experimental subjects if required" onclick="goToPage('MicroarrayForm2.htm');">
                  <img src="/images/sheep.gif" border="0" height="42" width="42"/>
                  <br>Subject
               </td>
               <td class=arrow>
                  &rarr;
               </td>
               <td class=color3 title="Define one or more samples if required" onclick="goToPage('MicroarrayForm3.htm');">
                  <img src="/images/eppendorf.gif" border="0" height="42" width="42"/>
                  <br>Sample
               </td>
               <td class=arrow>
                  &rarr;
               </td>
               <td class=color4 title="Submit Files" onclick="goToPage('MicroarrayForm4.htm');">
                  <img src="/images/microarray.jpg" border="0" height="42" width="42"/>
                  <br>Files
               </td>
               <td class=arrow>
                  &rarr;
               </td>
               <td class=color5 title="Define Series" onclick="goToPage('MicroarrayForm5.htm');">
                  <img src="/images/series.gif" border="0" height="42" width="42"/>
                  <br>Series
               </td>
               <td class=arrow>
                  &rarr;
               </td>
               <td class=color6 title="Define contrasts" onclick="goToPage('MicroarrayForm6.htm');">
                  <img src="/images/contrast.gif" border="0" height="42" width="42"/>
                  <br>Contrasts
               </td>
               <td class=arrow>
                  &rarr;
               </td>
               <td class=color7 title="Submit related documents (if any)" onclick="goToPage('MicroarrayForm7.htm');">
                  <img src="/images/documents.gif" border="0" height="42" width="42"/>
                  <br>Documents
               </td>
            </tr>
         </table>
      </td>
   </tr>
</table>

<br>

<table border="true" id="Outer_table" width=100%>
   <tr>
      <td colspan=2>
         <div style="text-align: center; font-size: 150%; font-weight: bold; line-height: 2">Protocol</div>
         <div style="text-align: left; font-size: 90%; font-weight: normal;">
            Define any protocols you have used with this form. If all your protocols are in the list below, 
            click Next to go to the next form</div>
      </td>
   </tr>
   
   <tr>
      <td class="fieldname" width=17%>
         <p class="fieldname"><b>Existing protocols:</b>
      </td>
      <td width=83%>
          <select name="protocol" size=10>
             <option value="">
             <!--__EXISTING_PROTOCOLS__-->
          </select>
          <button style="margin: 70px 10px;" type=button onClick="goToPage('MicroarrayForm2.htm')">Next &gt;</button>
      </td>
   </tr>


   <tr>
      <td colspan=2>
         <p style="text-align: left; font-size: 120%; font-weight: bold; text-decoration: underline;">New Protocol</p>
      </td>
   </tr>
   <tr>
      <td class="fieldname" width=17%>
         <p class="fieldname"><b>Protocol name:</b>
      </td>
      <td class="input" width=83%>
          <input name="protocolName" value="" size="50" type="text"/>
      </td>
   </tr>
   <tr>
      <td class="fieldname" width=17%>
         <p class="fieldname"><b>Protocol type:</b>
      </td>
      <td class="input" width=83%>
         <select name="protocolType" >
            <option value="" selected>
            <!--__EXISTING_PROTOCOL_TYPES__-->
            <!--option value="Other">Other-->
         </select>
         <!--&nbsp;&nbsp; Other type (not in list): 
         <input name="otherType" value="" size="40"/-->
      </td>
   </tr>    

   <tr>
      <td>
         <p><b>Description of this protocol:</b>
      </td>
      <td>
     <textarea name="protocolDesc" title="Please enter a description here" type="textarea" rows="4" cols="72">(Please enter a description here)</textarea> 
      </td>
   </tr>
   

   <tr>
      <td colspan=2>
         <p><i>Please <a href="mailto:alan.mcculloch@agresearch.co.nz;jason.mitchell@agresearch.co.nz?subject=Microarray Suggestion">email us</a> with any suggestions for improvements to this form.</i>
      </td>
   </tr>
   <tr>
      <td colspan=2 align=center>
         <p><input id="submitButton" type="submit" value="Submit Protocol">
      </td>
   </tr>
</table>
</FORM>
</body>
</html>
"""

form_microarraySubjectForm = r"""
<html>
<head>
<title>AgResearch - Microarray Upload Form</title>
<style>
body        {margin-top: 1cm ; margin-bottom: 1cm; margin-left: 5%; margin-right: 5%; 
        font-family: arial, helvetica, geneva, sans-serif;BACKGROUND: #f0f9ff}

p        {margin-top: .3cm ; margin-bottom: .3cm; margin-left: .4cm; margin-right: .4cm; 
        font-family: arial, helvetica, geneva, sans-serif}
p.fieldname     {margin-top: .3cm ; margin-bottom: .3cm; margin-left: .4cm; margin-right: .4cm; 
        font-family: arial, helvetica, geneva, sans-serif}
p.footer    {text-align: center ; margin-top: 0.5cm ; margin-bottom: 0.5cm; font-family: arial, helvetica, geneva, sans-serif}

b.b        {font-family: arial, helvetica, geneva, sans-serif; font-weight: 700; color: #424b50}
ul        {font-family: arial, helvetica, geneva, sans-serif}
ol        {font-family: arial, helvetica, geneva, sans-serif}
dl        {font-family: arial, helvetica, geneva, sans-serif}

th              {font-family: arial, helvetica, geneva, sans-serif; font-weight: 400}

h1        {text-align: center; color: #388fbd; 
        font-family: arial, helvetica, geneva, sans-serif}
h1.new          {text-align: center; color: #4d585e;
                font-family: arial, helvetica, geneva, sans-serif}
h1.b1           {margin-top: 0.5cm; text-align: center; color:#2d59b2;
                font-family: arial, helvetica, geneva, sans-serif}
h1.b2           {margin-top: 0.5cm; text-align: center; color:#1d7db5;
                font-family: arial, helvetica, geneva, sans-serif}
h1.top        {margin-top: 0.5cm; text-align: center; color: blue;
        font-family: arial, helvetica, geneva, sans-serif}

h2        {text-align: center; font-family: arial, helvetica, geneva, sans-serif}
h3        {font-family: arial, helvetica, geneva, sans-serif}
h4        {font-family: arial, helvetica, geneva, sans-serif}
h5        {font-family: arial, helvetica, geneva, sans-serif}
h6        {font-family: arial, helvetica, geneva, sans-serif}
a         {font-family: arial, helvetica, geneva, sans-serif}

table       {background-color: antiquewhite}

input.detail       {margin-left: 1cm}

textarea.detail    {margin-left: 1cm}

td        {font-family: arial, helvetica, geneva, sans-serif}
td.fieldname    {font-family: arial, helvetica, geneva, sans-serif}

tr          {background-color: #FFDA92}
.plainTable        {background-color: #FFDA92}
a:hover     {color: blue; text-decoration: underline }

.color0          {border: solid black; border-width: 5px; width: 80px; height: 80px}
.color1          {background-color: #FF9292; border: solid black; border-width: 1px; cursor: pointer; width: 88px; height: 88px}
.color2          {background-color: #FFDA92; border: solid black; border-width: 1px; cursor: pointer; width: 88px; height: 88px}
.color3          {background-color: #FFFF92; border: solid black; border-width: 1px; cursor: pointer; width: 88px; height: 88px}
.color4          {background-color: #B1FF92; border: solid black; border-width: 1px; cursor: pointer; width: 88px; height: 88px}
.color5          {background-color: #92E7FF; border: solid black; border-width: 1px; cursor: pointer; width: 88px; height: 88px}
.color6          {background-color: #9C92FF; border: solid black; border-width: 1px; cursor: pointer; width: 88px; height: 88px}
.color7          {background-color: #F392FF; border: solid black; border-width: 1px; cursor: pointer; width: 88px; height: 88px}

.arrow           {font-size: 200%; width: 40px}
</style>
<script language="JavaScript">

var alreadySubmitted = false;

function checkAll() {
   // make sure we have not already submitted this form
   if(alreadySubmitted) {
      window.alert("This Form has already been submitted, please wait");
      return false;
   }

   // check the SubjectId is populated, and doesn't match any existing ones
   var duplicatedName = false;
   var ar = document.arrayform.subject;
   var subj = document.arrayform.SubjectId;
   for (i=0; i < ar.length; i++) {
      if (ar[i].value == trim(subj.value)) {
         duplicatedName = true;
      }
   }
   if (duplicatedName) {
      highLight(subj,"You must specify a unique Subject Id.");
      return false;
   } else if (trim(subj.value).match(/[']/) != null) {
      highLight(subj,"Sorry, but you cannot use an apostrophe in the Subject Id. " + 
      "If you need one, you could use a back-tick, \"`\" (which should be just to the left of the \"1\" key).");
      return false;
   } else {
      lowLight(subj);
   }

   // check that species is populated.
   if (trim(document.arrayform.species.value) == "") {
      highLight(document.arrayform.species,"You must enter a species.");
      return false;
   }
   else {
      lowLight(document.arrayform.species);
   }
   
   // check that sex is populated.
   if (document.arrayform.sex.value == "") {
      highLight(document.arrayform.sex,"You must specify a sex.");
      return false;
   }
   else {
      lowLight(document.arrayform.sex);
   }
   
   // check that DOB is populated.
   if (document.arrayform.ageDay.value == "") {
      highLight(document.arrayform.ageDay,"You must specify a complete DOB.");
      return false;
   }
   else {
      lowLight(document.arrayform.ageDay);
   }
   if (document.arrayform.ageMonth.value == "") {
      highLight(document.arrayform.ageMonth,"You must specify a complete DOB.");
      return false;
   }
   else {
      lowLight(document.arrayform.ageMonth);
   }
   if (document.arrayform.ageYear.value == "") {
      highLight(document.arrayform.ageYear,"You must specify a complete DOB.");
      return false;
   }
   else {
      lowLight(document.arrayform.ageYear);
   }
   
   //check that they've entered valid subjectAttributes.
   for (var i=0; i<subject_att_count; i++) {
      var san = eval("document.arrayform.SAN_"+i);
      var sav = eval("document.arrayform.SAV_"+i);
      var sau = eval("document.arrayform.SAU_"+i);
      lowLight(san);
      lowLight(sav);
      lowLight(sau);
      if (san.value == "NONE" && trim(sav.value) == "" && sau.value == "NONE") {
         //It's OK that none of these are filled out - or is it? does there need to be a minimum number of attributes?
      } else if (san.value == "NONE") {
         highLight(san,"Please select an attribute name.");
         return false;
      } else if (trim(sav.value) == "") {
         highLight(sav,"Please enter a value for the attribute.");
         return false;
      } else if (sau.value == "NONE") {
         highLight(sau,"Please select a unit for the attribute.");
         return false;
      } else if (sau.value != "NONE" && trim(sav.value) != "") {
         if (sau.value == 'string' || sau.value == 'ratio' || sau.value == 'Other') {
            //Don't do anything - since we don't care what value they put in - they can even put in date or numeric strings.
         } else if (sau.value == 'date') {
            var dat = trim(sav.value).match(/^(\d{4})[-\/\s_.]{1}(\d{2})[-\/\s_.]{1}(\d{2})$/);
            if (dat == null) {
               highLight(sav,"Date must be in the format \"YYYY-MM-DD\".");
               return false;
            } else if (dat.length != 4) {
               highLight(sav,"Unknown error with date! ");
               return false;
            } else {
               var day = dat[3];
           var month = dat[2];
           var year = dat[1];
           var thisYear = (new Date()).getFullYear();
           if (year < "1980" || year > thisYear) {
              highLight(sav,"Please enter a year between 1980 and this year (" + thisYear + ").");
              return false;
           }
           else if (month == "00" || month > "12") {
              highLight(sav,"Please enter a valid number for the month.");
              return false;
           }
           else if (day == "00" || day > "31") {
              highLight(sav,"Please enter a valid number of days.");
              return false;
           }
           else if ((month == "09" || month == "04" || month == "06" || month == "11") && day == "31") {
              highLight(sav,"There are only 30 days in " + monthArray[month-1] + ". Please correct the date.");
              return false;
           }
           else if (month == "02" && (day == "31" || day == "30" ||day == "29") && year%4 != "0") {
              highLight(sav,"There are only 28 days in February in " + year + ". Please correct the date.");
              return false;
           }
           else if (month == "02" && (day == "31" || day == "30") && year%4 == "0") {
              highLight(sav,"There are only 29 days in February in " + year + ". Please correct the date.");
              return false;
           }
            }
         } else {//must be a numeric value
            var str = trim(sav.value).match(/^\d+\.?\d*$|^\.\d+$/);
            if (str == null) {
               highLight(sav,"Value must be a Number.");
           return false;
        }
         }
      }
   }

   // finally, set the submitted flag
   btn = document.getElementById("submitButton");
   btn.value = "Submitting, please wait...";
   btn.disabled = true;
   
   alreadySubmitted = true;
   return true;
}

function highLight(item,message) {
   item.style.background = 'red';
   window.alert(message);
   item.focus();
} // assume IE

function lowLight(item) {
   item.style.background = '';
}

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

function goToPage(pageName) {
   return location.href="form.py?formname=" + pageName;
}

//================================================================//

var subject_att_count = 1;

function subject_Att_Time(id){ 
   return '<input name="SAT_'+id+'" title="Optional field; be as accurate as you wish (YYYY-MM-DD hh:mm:ss)" size=25>';
}

function subject_Att_Val(id){ return '<input name="SAV_'+id+'">';}

function subject_Att_Unit(id){ 
   returnStr = '<select name="SAU_'+id+'"';
   if(id == 'newAttUnits') { 
      returnStr += 'onChange="updateNewAttAllowable()"';
   } else {
      returnStr += 'onChange="setDefaultAttValue(this, \''+id+'\')"';
   }
   returnStr += '>' +
              '<option value="NONE" selected>' +
              '<option value="string">Text-string' +
              '<option value="date">Date' +
              '<option value="integer">Whole-number' +
              '<option value="number">Decimal-number' +
              '<option value="kilograms">Kilograms' +
              '<option value="grams">Grams' +
              '<option value="milligrams">Milligrams' +
              '<option value="deg-celsius">Degrees Celsius' +
              '<option value="millilitres">Millilitres' +
              '<option value="microlitres">Microlitres' +
              '<option value="millimetres">Millimetres' +
              '<option value="milliseconds">Milliseconds' +
              '<option value="ratio">Ratio' +
              '<option value="ng/ul">ng/ul' +
              '<option value="Other">Other' +
              '</select>';
   return returnStr;
}

var Att_Name_Str1 = '<select name="SAN_';
var Att_Name_Str2 = '">'+
            '<option value="NONE" selected>&nbsp;</option>'+
            '<option>Anamorph</option>'+
            '<option>Authority</option>'+
            '<option>Biotype</option>'+
            '<option>Biovar</option>'+
            '<option>Breed</option>'+
            '<option>Cell-line</option>'+
            '<option>Cell-type</option>'+
            '<option>Chemovar</option>'+
            '<option>Clone</option>'+
            '<option>Clone-lib</option>'+
            '<option>Collected By</option>'+
            '<option>Collection Date</option>'+
            '<option>Country</option>'+
            '<option>Cultivar</option>'+
            '<option>Dev-stage</option>'+
            '<option>Ecotype</option>'+
            '<option>Forma</option>'+
            '<option>Forma Specialis</option>'+
            '<option>Frequency</option>'+
            '<option>Genotype</option>'+
            '<option>Germline</option>'+
            '<option>Haplotype</option>'+
            '<option>Identified By</option>'+
            '<option>Isolate</option>'+
            '<option>Lab-host</option>'+
            '<option>Lat-Lon</option>'+
            '<option>Natural-host</option>'+
            '<option>Pathovar</option>'+
            '<option>Phenotype</option>'+
            '<option>Plasmid-name</option>'+
            '<option>Plastid-name</option>'+
            '<option>Pop-variant</option>'+
            '<option>Proviral</option>'+
            '<option>Rearranged</option>'+
            '<option>Segment</option>'+
            '<option>Serogroup</option>'+
            '<option>Serotype</option>'+
            '<option>Serovar</option>'+
            '<option>Specimen-voucher</option>'+
            '<option>Strain</option>'+
            '<option>Sub-species</option>'+
            '<option>Subclone</option>'+
            '<option>Substrain</option>'+
            '<option>Subtype</option>'+
            '<option>Synonym</option>'+
            '<option>Teleomorph</option>'+
            '<option>Tissue-lib</option>'+
            '<option>Tissue-type</option>'+
            '<option>Type</option>'+
            '<option>Variety</option>'+
            '</select>';

function subject_Att_Name(id){ return Att_Name_Str1+id+Att_Name_Str2;}

function setDefaultAttValue(sau, num) {
   var sav = eval("document.arrayform.SAV_"+num);
   if (sau.value == "date") {
      sav.title = '(YYYY-MM-DD)';
      if (sav.value == '') sav.value = 'YYYY-MM-DD';
   } else {
      if (sav.value == 'YYYY-MM-DD') sav.value = '';
      sav.title = '';
   }
}

function addAttributeRow(tableID) {
   var table = document.getElementById(tableID);
   var row = table.insertRow(table.rows.length);
   var cell = row.insertCell(0);
   cell.vAlign="top"
   cell.innerHTML = subject_Att_Name(subject_att_count);
   //Check that the col doesn't need any new attributes added!
   cell = row.insertCell(1);
   cell.vAlign="top"
   cell.innerHTML = subject_Att_Val(subject_att_count);
   cell = row.insertCell(2);
   cell.vAlign="top"
   cell.innerHTML = subject_Att_Unit(subject_att_count);
   cell = row.insertCell(3);
   cell.vAlign="top"
   cell.innerHTML = subject_Att_Time(subject_att_count);
   subject_att_count++;
   document.arrayform.subjectAttCount.value = subject_att_count;
}

function showAttTable() {
   if(document.getElementById("attTable")){
      var attTable = document.getElementById("attTable")
      if (attTable.style.display == "none") {
      window.alert("Please enter the details of the new attribute in the section below. When you click \"Add Attribute\" " + 
      "the new attribute will be added to the drop-down box of Attribute Names.");
         attTable.style.display = "";
         document.arrayform.addAtt.focus();
         document.arrayform.newAttName.focus();
      } else {
         attTable.style.display = "none";
         eval("document.arrayform.SAN_"+(subject_att_count-1)+".focus()");
      }
   }
}

var new_att_type = "String";
function updateNewAttAllowable() {
   var attUnit = document.arrayform.SAU_newAttUnits.value;
   if (attUnit == 'string' || attUnit == 'ratio' || attUnit == 'Other' || attUnit == 'NONE') {
      document.arrayform.newAttAllowable.style.display = "";
      document.getElementById("maxNum").style.display = "none";
      document.getElementById("minNum").style.display = "none";
      document.getElementById("maxDate").style.display = "none";
      document.getElementById("minDate").style.display = "none";
      new_att_type = "String";
   } else if (attUnit == 'date') {
      document.arrayform.newAttAllowable.style.display = "none";
      document.getElementById("maxNum").style.display = "none";
      document.getElementById("minNum").style.display = "none";
      document.getElementById("maxDate").style.display = "";
      document.getElementById("minDate").style.display = "";
      new_att_type = "Date";
   } else {
      document.arrayform.newAttAllowable.style.display = "none";
      document.getElementById("maxNum").style.display = "";
      document.getElementById("minNum").style.display = "";
      document.getElementById("maxDate").style.display = "none";
      document.getElementById("minDate").style.display = "none";
      new_att_type = "Num";
   }
}

var num_new_attrs = 0;
function addNewAttribute() {
   var valType = Array();
   var name = Array();
   if (new_att_type == "String") {
      valType[0] = trim(document.arrayform.newAttAllowable.value);
      name[0] = "newAttAllowable" + num_new_attrs;
   } else if (new_att_type == "Date") {
      valType[0] = trim(document.arrayform.maxAllowableDay.value);
      valType[1] = trim(document.arrayform.maxAllowableMonth.value);
      valType[2] = trim(document.arrayform.maxAllowableYear.value);
      valType[3] = trim(document.arrayform.minAllowableDay.value);
      valType[4] = trim(document.arrayform.minAllowableMonth.value);
      valType[5] = trim(document.arrayform.minAllowableYear.value);
      name[0] = "newMaxAllowableDay" + num_new_attrs;
      name[1] = "newMaxAllowableMonth" + num_new_attrs;
      name[2] = "newMaxAllowableYear" + num_new_attrs;
      name[3] = "newMinAllowableDay" + num_new_attrs;
      name[4] = "newMinAllowableMonth" + num_new_attrs;
      name[5] = "newMinAllowableYear" + num_new_attrs;
   } else { //new_att_type is "Num"
      valType[0] = trim(document.arrayform.maxAllowable.value);
      valType[1] = trim(document.arrayform.minAllowable.value);
      name[0] = "newMaxAttAllowable" + num_new_attrs;
      name[1] = "newMinAttAllowable" + num_new_attrs;
   }
   var attName = trim(document.arrayform.newAttName.value);
   var attUnit = document.arrayform.SAU_newAttUnits.value;
   var attDesc = trim(document.arrayform.newAttDesc.value);
   //var attAllowable = trim(document.arrayform.newAttAllowable.value);
   var testingError = '0';
   if (attName == '') {
      highLight(document.arrayform.newAttName,'You need to specify a name for the new attribute.');
      testingError = '1';
   } else if (attUnit == 'NONE') {
      highLight(document.arrayform.SAU_newAttUnits,'You need to select the type of unit for the new attribute.');
      testingError = '1';
   } else if (attDesc == '(Please enter a description here)' || attDesc == '') {
      highLight(document.arrayform.newAttDesc,'You need to enter a brief description for the new attribute.');
      testingError = '1';
      
   } else if (new_att_type == "String" && valType[0] == '(Enter each value\nOn a new line)') {
      highLight(document.arrayform.newAttAllowable,'If you don\'t want to specify allowable values, leave the allowable-values field blank.');
      testingError = '1';
   } else if (new_att_type == "Num" && parseInt(valType[0]) < parseInt(valType[1])) {
      highLight(document.arrayform.maxAllowable,'You need to swap Max and Min Values - Max Value needs to be greater than Min Value.');
      testingError = '1';
   } else if (new_att_type == "Date") {
      //Need to test if Max > Min (Dates are validated by checkDateValid(), below).
      lowLight(document.arrayform.maxAllowableYear);
      lowLight(document.arrayform.minAllowableYear);
      lowLight(document.arrayform.maxAllowableMonth);
      lowLight(document.arrayform.minAllowableMonth);
      lowLight(document.arrayform.maxAllowableDay);
      lowLight(document.arrayform.minAllowableDay);
      if (valType[0] == '' && valType[1] == '' && valType[2] == '' && 
          valType[3] == '' && valType[4] == '' && valType[5] == '') {
         //Do nothing - just checking that at least one of these are set, and if so, process logic below.
      } else if (valType[0] == '') {
         highLight(document.arrayform.maxAllowableDay,'If setting a max and min date, you need to select values for all boxes.');
         testingError = '1';
      } else if (valType[1] == '') {
         highLight(document.arrayform.maxAllowableMonth,'If setting a max and min date, you need to select values for all boxes.');
         testingError = '1';
      } else if (valType[2] == '') {
         highLight(document.arrayform.maxAllowableYear,'If setting a max and min date, you need to select values for all boxes.');
         testingError = '1';
      } else if (valType[3] == '') {
         highLight(document.arrayform.minAllowableDay,'If setting a max and min date, you need to select values for all boxes.');
         testingError = '1';
      } else if (valType[4] == '') {
         highLight(document.arrayform.minAllowableMonth,'If setting a max and min date, you need to select values for all boxes.');
         testingError = '1';
      } else if (valType[5] == '') {
         highLight(document.arrayform.minAllowableYear,'If setting a max and min date, you need to select values for all boxes.');
         testingError = '1';
      } else if (valType[2] < valType[5]) {
         highLight(document.arrayform.maxAllowableYear,'You need to swap Max and Min Dates - Max Date needs to be greater than Min Date.');
         testingError = '1';
      } else if (valType[2] == valType[5]) {
         if (valType[1] < valType[4]) {
            highLight(document.arrayform.maxAllowableMonth,'You need to swap Max and Min Dates - Max Date needs to be greater than Min Date.');
            testingError = '1';
         } else if (valType[1] == valType[4]) {
            if (valType[0] < valType[3]) {
           highLight(document.arrayform.maxAllowableDay,'You need to swap Max and Min Dates - Max Date needs to be greater than Min Date.');
               testingError = '1';
            }
         }
      }
   } 
   if (testingError == '0') {
      lowLight(document.arrayform.newAttName);
      lowLight(document.arrayform.SAU_newAttUnits);
      lowLight(document.arrayform.newAttDesc);
      lowLight(document.arrayform.newAttAllowable);
      lowLight(document.arrayform.maxAllowable);
      fail = "False";
      box = eval("document.arrayform.SAN_0");
      for (i=0; i<box.length; i++) {
         if (box.options[i].text == attName){
            fail = "True";
         }
      }
      if (fail == "True") {
         window.alert("The Attribute '" + attName + "' is already entered");
      } else {
         //Need to take the values in the fields and set them to hidden fields in this form so they'll be entered in the db...
         var newAttName = document.createElement('INPUT');
         newAttName.type = "HIDDEN";
         newAttName.name = "newAttName" + num_new_attrs;
         newAttName.value = attName;
         document.arrayform.appendChild(newAttName);
         
         var newAttUnit = document.createElement('INPUT');
         newAttUnit.type = "HIDDEN";
         newAttUnit.name = "newAttUnit" + num_new_attrs;
         newAttUnit.value = attUnit;
         document.arrayform.appendChild(newAttUnit);
         
         var newAttDesc = document.createElement('INPUT');
         newAttDesc.type = "HIDDEN";
         newAttDesc.name = "newAttDesc" + num_new_attrs;
         newAttDesc.value = attDesc;
         document.arrayform.appendChild(newAttDesc);
      
         for (i=0; i<valType.length; i++) {
            var newAttAllowable = document.createElement('INPUT');
            newAttAllowable.type = "HIDDEN";
            newAttAllowable.name = name[i];
            newAttAllowable.value = valType[i];
            document.arrayform.appendChild(newAttAllowable);
         }
         
         //...then add an entry to the attribute list and give it focus...
         for (i=0; i<subject_att_count; i++) {
            var comboBox = eval("document.arrayform.SAN_"+i);
            //window.alert("combobox has length of " + comboBox.length + "\nAttribute has name " + attName);
            var newOpt = document.createElement("option");
            newOpt.text = attName;
            newOpt.value = attName;
            //newOpt.selected = true;
            
            var browserName = navigator.appName;
            if (browserName == "Netscape" || browserName == "Opera") { 
               comboBox.add(newOpt, null);
            }
            else if (browserName=="Microsoft Internet Explorer") {
               comboBox.add(newOpt);
            }

            if (comboBox.selectedIndex == 0) { 
               comboBox.options[comboBox.length-1].selected = "True";
            }
         }
         
         //Also need to add the value to the string which is used to populate new "attribute name" combo boxes.
         //var regexp = /<\/select>/g;
         Att_Name_Str2 = Att_Name_Str2.replace(/<\/select>/g, "<option>"+attName+"<\/option></select>");
         
         //...then reset the "newAtt" fields so the user can add more and won't have to delete their previous entries.
         document.arrayform.newAttName.value = '';
         document.arrayform.SAU_newAttUnits.selectedIndex = '0';
         document.arrayform.newAttDesc.value = '(Please enter a description here)';
         document.arrayform.newAttAllowable.value = '(Enter each value\nOn a new line)';
         document.arrayform.maxAllowable.value = '';
         document.arrayform.minAllowable.value = '';
         document.arrayform.maxAllowableYear.selectedIndex = '0';
         document.arrayform.minAllowableYear.selectedIndex = '0';
         document.arrayform.maxAllowableMonth.selectedIndex = '0';
         document.arrayform.minAllowableMonth.selectedIndex = '0';
         document.arrayform.maxAllowableDay.selectedIndex = '0';
         document.arrayform.minAllowableDay.selectedIndex = '0';
         showAttTable(); //(i.e. hide the table)
         num_new_attrs++;
      }
   }
}

//================================================================//

var monthArray = ["January","February","March","April","May","June","July","August","September","October","November","December"];

function ageFields(prefix) {
   outputString = '<select name="' + prefix + 'Day" onChange="checkDateValid(\'' + prefix + '\')"><option value="">Day';
   //Adding strings for days
   for (i = 1;i < 32; i++) {
      outputString += '<option value="' + i + '">' + i;
   }
   outputString += '</select>\n<select name="' + prefix + 'Month" onChange="checkDateValid(\'' + prefix + '\')"><option value="">Month';
   for (i = 0;i < 12; i++) {
      outputString += '<option value="' + (i+1) + '">' + monthArray[i];
   }
   outputString += '</select>\n<select name="' + prefix + 'Year" onChange="checkDateValid(\'' + prefix + '\')"><option value="">Year';
   var start = new Date();
   var startYear = start.getFullYear();
   for (i = startYear;i >= 1980; i--) {
      outputString += '<option value="' + i + '">' + i;
   }
   outputString += '</select>\n';
   return outputString;
}

function checkDateValid(prefix) {
   var dayField = eval('document.arrayform.' + prefix + 'Day');
   var day = dayField.value;
   var monthField = eval('document.arrayform.' + prefix + 'Month');
   var month = monthArray[monthField.value-1];
   var yearField = eval('document.arrayform.' + prefix + 'Year');
   var year = yearField.value;
   if ((month == "September" || month == "April" || month == "June" || month == "November") && day == "31") {
      window.alert("There are only 30 days in " + month + ".");
      dayField.value = "30";
   }
   else if (month == "February" && (day == "31" || day == "30" ||day == "29") && year%4 != "0") {
      window.alert("There are only 28 days in February in " + year + ".");
      dayField.value = "28";   
   }
   else if (month == "February" && (day == "31" || day == "30") && year%4 == "0") {
      window.alert("There are only 29 days in February in " + year + ".");
      dayField.value = "29";   
   }
}

//================================================================//

</script>
</head><body>
<FORM name="arrayform" onSubmit="return checkAll();" METHOD="POST" ENCTYPE="multipart/form-data" ACTION="/cgi-bin/agbrdf/form.py" >
<input type="HIDDEN" name="formname" value="microarraySubjectForm"/>
<input type="HIDDEN" name="sessionid" value="0"/>
<input type="HIDDEN" name="subjectAttCount" value="1"/>
<table border="true" id="Top_table" width=100%>
   <tr>
      <td colspan="2">
         <h1 class="top">AgResearch Microarray Upload Form</h1>
      </td>
   </tr>
   <tr>
      <td colspan="2"> 
         <table align=center class=plainTable style="border-width: 0">
            <tr align=center valign=middle>
               <td class=color1 title="Define one or more protocols if required" onclick="goToPage('MicroarrayForm1.htm');">
                  <img src="/images/protocol.gif" border="0" height="42" width="42"/>
                  <br>Protocol
               </td>
               <td class=arrow>
                  &rarr;
               </td>
               <td class=color0 title="Define one or more experimental subjects if required">
                  <img src="/images/sheep.gif" border="0" height="42" width="42"/>
                  <br>Subject
               </td>
               <td class=arrow>
                  &rarr;
               </td>
               <td class=color3 title="Define one or more samples if required" onclick="goToPage('MicroarrayForm3.htm');">
                  <img src="/images/eppendorf.gif" border="0" height="42" width="42"/>
                  <br>Sample
               </td>
               <td class=arrow>
                  &rarr;
               </td>
               <td class=color4 title="Submit Files" onclick="goToPage('MicroarrayForm4.htm');">
                  <img src="/images/microarray.jpg" border="0" height="42" width="42"/>
                  <br>Files
               </td>
               <td class=arrow>
                  &rarr;
               </td>
               <td class=color5 title="Define Series" onclick="goToPage('MicroarrayForm5.htm');">
                  <img src="/images/series.gif" border="0" height="42" width="42"/>
                  <br>Series
               </td>
               <td class=arrow>
                  &rarr;
               </td>
               <td class=color6 title="Define contrasts" onclick="goToPage('MicroarrayForm6.htm');">
                  <img src="/images/contrast.gif" border="0" height="42" width="42"/>
                  <br>Contrasts
               </td>
               <td class=arrow>
                  &rarr;
               </td>
               <td class=color7 title="Submit related documents (if any)" onclick="goToPage('MicroarrayForm7.htm');">
                  <img src="/images/documents.gif" border="0" height="42" width="42"/>
                  <br>Documents
               </td>
            </tr>
         </table>
      </td>
   </tr>
</table>

<br>

<table border="true" id="Outer_table" width=100%>
   <tr>
      <td colspan=2 >
         <div style="text-align: center; font-size: 150%; font-weight: bold; line-height: 2">Subject</div>
         <div style="text-align: left; font-size: 90%; font-weight: normal;">
            Define any experimental subjects you have used with this form. If your subjects are in the list below, 
            click Next to go to the next form</div>
      </td>
   </tr>
   
   <tr>
      <td class="fieldname" width=17%>
         <p class="fieldname"><b>Existing subjects:</b>
      </td>
      <td width=83%>
          <select name="subject" size=10>
             <option value="">
             <!--__EXISTING_SUBJECTS__-->
          </select>
          <button style="margin: 70px 10px;" type=button onClick="goToPage('MicroarrayForm3.htm')">Next &gt;</button>
      </td>
   </tr>


   <tr>
      <td colspan=2>
         <p style="text-align: left; font-size: 120%; font-weight: bold; text-decoration: underline;">New Subject</p>
      </td>
   </tr>
   <tr>
      <td class="fieldname" width=17%>
         <p class="fieldname"><b>Subject Id:</b>
      </td>
      <td class="input" width=83%>
          <input name="SubjectId" value="" size="50" type="text"/>
      </td>
   </tr>
   <tr>
      <td class="fieldname" width=17%>
         <p class="fieldname"><b>Species:</b>
      </td>
      <td class="input" width=83%>
         <input name="species" value="" size="50" type="text"/>
      </td>
   </tr>    
   <tr>
      <td class="fieldname" width=17%>
         <p class="fieldname"><b>Sex:</b>
      </td>
      <td class="input" width=83%>
          <select name="sex">
             <option value="">
             <option value="M">Male
             <option value="F">Female
             <option value="U">Unknown
          </select>
      </td>
   </tr>    
   <tr>
      <td class="fieldname" width=17%>
         <p class="fieldname"><b>DOB:</b>
      </td>
      <td class="input" width=83%>
         <script>document.write(ageFields('age'));</script>
      </td>
   </tr>    

   <tr>
      <td>
         <p><b>Subject attributes:</b>
      </td>
      <td>
     <table id="attributes_table" class=plainTable>
        <tr>
           <th nowrap align=left><label>Attribute Name</label></th>
           <th nowrap align=left><label>Attribute Value</label></th>
           <th nowrap align=left><label>Attribute Units</label></th>
           <th nowrap align=left><label>Attribute Time Stamp</label></th>
           </tr>
        <tr>
           <td>
           <script>document.write(subject_Att_Name('0'));</script>
           </td>
           <td>
           <script>document.write(subject_Att_Val('0'));</script>
           </td>
           <td>
           <script>document.write(subject_Att_Unit('0'));</script>
           </td>
           <td>
           <script>document.write(subject_Att_Time('0'));</script>
           </td>
        </tr>
     </table>
         <button type=button onclick="addAttributeRow('attributes_table');">Record More Attributes</button>
         <button type=button onclick="showAttTable();">Define a new Attribute</button>
      </td>
   </tr>
   

   <tr>
      <td colspan=2>
         <p><i>Please <a href="mailto:alan.mcculloch@agresearch.co.nz;jason.mitchell@agresearch.co.nz?subject=Microarray Suggestion">email us</a> with any suggestions for improvements to this form.</i>
      </td>
   </tr>
   <tr>
      <td colspan=2 align=center>
         <p><input id="submitButton" type="submit" value="Submit Subject">
      </td>
   </tr>
</table>
<br>
<table id="attTable" style="display: none;" border="true">
   <tr>
      <td colspan=2 align=center>
         <p style="text-align: center; font-size: 120%; font-weight: bold; text-decoration: underline;">Define a new Attribute</p>
      </td>
   </tr>
   <tr>
      <td class="fieldname">
         <p class="fieldname"><b>Attribute Name:</b>
      </td>
      <td class="input">
         <input name="newAttName" value="" size="20" type="text"/>
      </td>
   </tr>
   <tr>
      <td class="fieldname">
         <p class="fieldname"><b>Attribute Unit:</b>
      </td>
      <td class="input">
         <script>document.write(subject_Att_Unit('newAttUnits'));</script>
      </td>
   </tr>
   <tr>
      <td class="fieldname">
         <p class="fieldname"><b>Attribute Desc:</b>
      </td>
      <td class="input">
     <textarea name="newAttDesc" title="Please enter a description here" type="textarea" rows="4" cols="40">(Please enter a description here)</textarea> 
      </td>
   </tr>
   <tr>
      <td class="fieldname">
         <p class="fieldname"><b>Allowable Values:</b>
      </td>
      <td class="input">
     <textarea name="newAttAllowable" title="Enter each value on a new line" type="textarea" rows="4" cols="45">(Enter each value
On a new line)</textarea> 
         <p id="maxNum" style="display: none;">Maximum Value: <input name="maxAllowable" value="" type="text"/>
         <p id="minNum" style="display: none;">Minimum Value: &nbsp;<input name="minAllowable" value="" type="text"/>
         <p id="maxDate" style="display: none;">Maximum Value: <script>document.write(ageFields('maxAllowable'));</script>
         <p id="minDate" style="display: none;">Minimum Value: &nbsp;<script>document.write(ageFields('minAllowable'));</script>
      </td>
   </tr>
   <tr>
      <td colspan=2 align=center>
         <p><input name="addAtt" type="button" value="Add Attribute" onClick="addNewAttribute();">
      </td>
   </tr>
</table>
</FORM>
</body>
</html>
"""

form_microarraySampleForm = r"""
<html>
<head>
<title>AgResearch - Microarray Upload Form</title>
<style>
body        {margin-top: 1cm ; margin-bottom: 1cm; margin-left: 5%; margin-right: 5%; 
        font-family: arial, helvetica, geneva, sans-serif;BACKGROUND: #f0f9ff}

p        {margin-top: .3cm ; margin-bottom: .3cm; margin-left: .4cm; margin-right: .4cm; 
        font-family: arial, helvetica, geneva, sans-serif}
p.fieldname     {margin-top: .3cm ; margin-bottom: .3cm; margin-left: .4cm; margin-right: .4cm; 
        font-family: arial, helvetica, geneva, sans-serif}
p.footer    {text-align: center ; margin-top: 0.5cm ; margin-bottom: 0.5cm; font-family: arial, helvetica, geneva, sans-serif}

b.b        {font-family: arial, helvetica, geneva, sans-serif; font-weight: 700; color: #424b50}
ul        {font-family: arial, helvetica, geneva, sans-serif}
ol        {font-family: arial, helvetica, geneva, sans-serif}
dl        {font-family: arial, helvetica, geneva, sans-serif}

th              {font-family: arial, helvetica, geneva, sans-serif; font-weight: 400}

h1        {text-align: center; color: #388fbd; 
        font-family: arial, helvetica, geneva, sans-serif}
h1.new          {text-align: center; color: #4d585e;
                font-family: arial, helvetica, geneva, sans-serif}
h1.b1           {margin-top: 0.5cm; text-align: center; color:#2d59b2;
                font-family: arial, helvetica, geneva, sans-serif}
h1.b2           {margin-top: 0.5cm; text-align: center; color:#1d7db5;
                font-family: arial, helvetica, geneva, sans-serif}
h1.top        {margin-top: 0.5cm; text-align: center; color: blue;
        font-family: arial, helvetica, geneva, sans-serif}

h2        {text-align: center; font-family: arial, helvetica, geneva, sans-serif}
h3        {font-family: arial, helvetica, geneva, sans-serif}
h4        {font-family: arial, helvetica, geneva, sans-serif}
h5        {font-family: arial, helvetica, geneva, sans-serif}
h6        {font-family: arial, helvetica, geneva, sans-serif}
a         {font-family: arial, helvetica, geneva, sans-serif}

table       {background-color: antiquewhite}

input.detail       {margin-left: 1cm}

textarea.detail    {margin-left: 1cm}

td        {font-family: arial, helvetica, geneva, sans-serif}
td.fieldname    {font-family: arial, helvetica, geneva, sans-serif}

tr          {background-color: #FFFF92}
.plainTable     {background-color: #FFFF92}
a:hover     {color: blue; text-decoration: underline }

.color0          {border: solid black; border-width: 5px; width: 80px; height: 80px}
.color1          {background-color: #FF9292; border: solid black; border-width: 1px; cursor: pointer; width: 88px; height: 88px}
.color2          {background-color: #FFDA92; border: solid black; border-width: 1px; cursor: pointer; width: 88px; height: 88px}
.color3          {background-color: #FFFF92; border: solid black; border-width: 1px; cursor: pointer; width: 88px; height: 88px}
.color4          {background-color: #B1FF92; border: solid black; border-width: 1px; cursor: pointer; width: 88px; height: 88px}
.color5          {background-color: #92E7FF; border: solid black; border-width: 1px; cursor: pointer; width: 88px; height: 88px}
.color6          {background-color: #9C92FF; border: solid black; border-width: 1px; cursor: pointer; width: 88px; height: 88px}
.color7          {background-color: #F392FF; border: solid black; border-width: 1px; cursor: pointer; width: 88px; height: 88px}

.arrow           {font-size: 200%; width: 40px}
</style>
<script language="JavaScript">

var alreadySubmitted = false;

function checkAll() {
   // make sure we have not already submitted this form
   if(alreadySubmitted) {
      window.alert("This Form has already been submitted, please wait");
      return false;
   }

   // check the sampleName is populated, and doesn't match any existing ones
   var duplicatedName = false;
   var ar = document.arrayform.sample;
   var samp = document.arrayform.sampleName;
   for (i=0; i < ar.length; i++) {
      if (ar[i].value == trim(samp.value)) {
         duplicatedName = true;
      }
   }
   if (duplicatedName) {
      highLight(samp,"You must specify a unique Sample name.");
      return false;
   } else if (trim(samp.value).match(/[']/) != null) {
      highLight(samp,"Sorry, but you cannot use an apostrophe in the Sample name. " + 
      "If you need one, you could use a back-tick, \"`\" (which should be just to the left of the \"1\" key).");
      return false;
   } else {
      lowLight(samp);
   }

   // check the sampleType is selected
   if (document.arrayform.sampleType.value == "") {
      highLight(document.arrayform.sampleType,"You must select a Sample type.");
      return false;
   } else {
      lowLight(document.arrayform.sampleType);
   }
   
   // check the Tissue Type is selected.
   if (document.arrayform.Tissue.value == "") {
      highLight(document.arrayform.Tissue,"Please select a tissue for this sample.");
      return false;
   } else {
      lowLight(document.arrayform.Tissue);
   }   
   
   //check that they've entered at least one attribute, and that it has valid input (depending on units).
   for (var i=0; i<sample_att_count; i++) {
      var san = eval("document.arrayform.SAN_"+i);
      var sav = eval("document.arrayform.SAV_"+i);
      var sau = eval("document.arrayform.SAU_"+i);
      lowLight(san);
      lowLight(sav);
      lowLight(sau);
      if (san.value == "NONE" && trim(sav.value) == "" && sau.value == "NONE") {
         //It's OK that none of these are filled out - or is it? does there need to be a minimum number of attributes?
      } else if (san.value == "NONE") {
         highLight(san,"Please select an attribute name.");
         return false;
      } else if (trim(sav.value) == "") {
         highLight(sav,"Please enter a value for the attribute.");
         return false;
      } else if (sau.value == "NONE") {
         highLight(sau,"Please select a unit for the attribute.");
         return false;
      } else if (sau.value != "NONE" && trim(sav.value) != "") {
         if (sau.value == 'string' || sau.value == 'ratio' || sau.value == 'Other') {
            //Don't do anything - since we don't care what value they put in - they can even put in date or numeric strings.
         } else if (sau.value == 'date') {
            var dat = trim(sav.value).match(/^(\d{4})[-\/\s_.]{1}(\d{2})[-\/\s_.]{1}(\d{2})$/);
            if (dat == null) {
               highLight(sav,"Date must be in the format \"YYYY-MM-DD\".");
               return false;
            } else if (dat.length != 4) {
               highLight(sav,"Unknown error with date! ");
               return false;
            } else {
               var day = dat[3];
           var month = dat[2];
           var year = dat[1];
           var thisYear = (new Date()).getFullYear();
           if (year < "1980" || year > thisYear) {
              highLight(sav,"Please enter a year between 1980 and this year (" + thisYear + ").");
              return false;
           }
           else if (month == "00" || month > "12") {
              highLight(sav,"Please enter a valid number for the month.");
              return false;
           }
           else if (day == "00" || day > "31") {
              highLight(sav,"Please enter a valid number of days.");
              return false;
           }
           else if ((month == "09" || month == "04" || month == "06" || month == "11") && day == "31") {
              highLight(sav,"There are only 30 days in " + monthArray[month-1] + ". Please correct the date.");
              return false;
           }
           else if (month == "02" && (day == "31" || day == "30" ||day == "29") && year%4 != "0") {
              highLight(sav,"There are only 28 days in February in " + year + ". Please correct the date.");
              return false;
           }
           else if (month == "02" && (day == "31" || day == "30") && year%4 == "0") {
              highLight(sav,"There are only 29 days in February in " + year + ". Please correct the date.");
              return false;
           }
            }
         } else {//must be a numeric value
            var str = trim(sav.value).match(/^\d+\.?\d*$|^\.\d+$/);
            if (str == null) {
               highLight(sav,"Value must be a Number.");
           return false;
        }
         }
      }
   }
   
   //check that they've entered something into the description field.
   if (trim(document.arrayform.sampleDesc.value) == "(Please enter a description here)") {
      highLight(document.arrayform.sampleDesc,"Please enter a description of the Sample.");
      return false;
   }else if (document.arrayform.sampleDesc.value.length <= 30) {
      highLight(document.arrayform.sampleDesc,"Please enter a longer description of the Sample (i.e. > 30 characters).");
      return false;
   } else {
      lowLight(document.arrayform.sampleDesc);
   }   

   // check that a subject is selected.
   if (document.arrayform.subject.selectedIndex == -1) {
      highLight(document.arrayform.subject,"Please select a subejct for this sample.");
      return false;
   } //else if (document.arrayform.subject.value == "") {
   var count = 0;
   var blank = 0;
   var other = 0;
   for (i=0; i<document.arrayform.subject.length; i++) {
      var opt = document.arrayform.subject.options[i];
      if (opt.selected) {
         if (opt.value == "") blank = 1;
         else if (opt.value == "Other") other = 1;
         count++;
      }
   }
   if (blank == 1) {
      if (count > 1) {
         highLight(document.arrayform.subject,"Please de-select the blank subject option.");
         return false;
      } else {
         highLight(document.arrayform.subject,"Please select a subejct for this sample.");
         return false;
      }
   }else if (other == 1) {
      highLight(document.arrayform.AddSubj,"Please add a subject in the subject form");
      return false;
   } else {
      lowLight(document.arrayform.subject);
      lowLight(document.arrayform.AddSubj);
   }   
   
   // check that a protocol is selected.
   if (document.arrayform.protocol.value == "") {
      highLight(document.arrayform.protocol,"Please select a protocol for this sample.");
      return false;
   }else if (document.arrayform.protocol.value == "Other") {
      highLight(document.arrayform.AddProto,"Please add a protocol in the protocol form");
      return false;
   } else {
      lowLight(document.arrayform.protocol);
      lowLight(document.arrayform.AddProto);
   }   
   
   // finally, set the submitted flag
   btn = document.getElementById("submitButton");
   btn.value = "Submitting, please wait...";
   btn.disabled = true;
   
   alreadySubmitted = true;
   return true;
}

function highLight(item,message) {
   item.style.background = 'red';
   window.alert(message);
   item.focus();
} // assume IE

function lowLight(item) {
   item.style.background = '';
}

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

function goToPage(pageName) {
   return location.href="form.py?formname=" + pageName;
}

function otherSelected(box, btn) {
   lowLight(box);
   lowLight(btn);
   btn.style.display='none';
   if (box.selectedIndex != -1) {
      if (btn.name == 'AddProto' && box.options[box.selectedIndex].value == 'Other') {
         highLight(box,'You need to add a protocol in the Protocol form!');
         btn.style.display='';
         btn.focus();
      } else if (btn.name == 'AddSubj') {
         for (i=0; i<box.length; i++) {
            if (box.options[i].value == "Other" & box.options[i].selected) {
               highLight(box,'You need to add a subject in the Subject form!');
           btn.style.display='';
               btn.focus();
            }
         }
      }
   }
}

//================================================================//

var sample_att_count = 1;

function sample_Att_Time(id){ 
   return '<input name="SAT_'+id+'" title="Optional field; be as accurate as you wish (YYYY-MM-DD hh:mm:ss)" size=25>';
}

function sample_Att_Val(id){ return '<input name="SAV_'+id+'">';}

function sample_Att_Unit(id){
   returnStr = '<select name="SAU_'+id+'"';
   if(id == 'newAttUnits') {
      returnStr += 'onChange="updateNewAttAllowable()"';
   } else {
      returnStr += 'onChange="setDefaultAttValue(this, \''+id+'\')"';
   }
   returnStr += '>' +
              '<option value="NONE" selected>' +
              '<option value="string">Text-string' +
              '<option value="date">Date' +
              '<option value="integer">Whole-number' +
              '<option value="number">Decimal-number' +
              '<option value="kilograms">Kilograms' +
              '<option value="grams">Grams' +
              '<option value="milligrams">Milligrams' +
              '<option value="deg-celsius">Degrees Celsius' +
              '<option value="millilitres">Millilitres' +
              '<option value="microlitres">Microlitres' +
              '<option value="millimetres">Millimetres' +
              '<option value="milliseconds">Milliseconds' +
              '<option value="ratio">Ratio' +
              '<option value="ng/ul">ng/ul' +
              '<option value="Other">Other' +
              '</select>';
   return returnStr;
}

var Att_Name_Str1 = '<select name="SAN_';
var Att_Name_Str2 = '">'+
            '<option value="NONE" selected>&nbsp;</option>'+
            '<option>Anamorph</option>'+
            '<option>Authority</option>'+
            '<option>Biotype</option>'+
            '<option>Biovar</option>'+
            '<option>Breed</option>'+
            '<option>Cell-line</option>'+
            '<option>Cell-type</option>'+
            '<option>Chemovar</option>'+
            '<option>Clone</option>'+
            '<option>Clone-lib</option>'+
            '<option>Collected By</option>'+
            '<option>Collection Date</option>'+
            '<option>Country</option>'+
            '<option>Cultivar</option>'+
            '<option>Dev-stage</option>'+
            '<option>Ecotype</option>'+
            '<option>Forma</option>'+
            '<option>Forma Specialis</option>'+
            '<option>Frequency</option>'+
            '<option>Genotype</option>'+
            '<option>Germline</option>'+
            '<option>Haplotype</option>'+
            '<option>Identified By</option>'+
            '<option>Isolate</option>'+
            '<option>Lab-host</option>'+
            '<option>Lat-Lon</option>'+
            '<option>Natural-host</option>'+
            '<option>Pathovar</option>'+
            '<option>Phenotype</option>'+
            '<option>Plasmid-name</option>'+
            '<option>Plastid-name</option>'+
            '<option>Pop-variant</option>'+
            '<option>Proviral</option>'+
            '<option>Rearranged</option>'+
            '<option>Segment</option>'+
            '<option>Serogroup</option>'+
            '<option>Serotype</option>'+
            '<option>Serovar</option>'+
            //'<option>Sex</option>'+
            '<option>Specimen-voucher</option>'+
            '<option>Strain</option>'+
            '<option>Sub-species</option>'+
            '<option>Subclone</option>'+
            '<option>Substrain</option>'+
            '<option>Subtype</option>'+
            '<option>Synonym</option>'+
            '<option>Teleomorph</option>'+
            '<option>Tissue-lib</option>'+
            '<option>Tissue-type</option>'+
            '<option>Type</option>'+
            '<option>Variety</option>'+
            '</select>';

function sample_Att_Name(id) { return Att_Name_Str1+id+Att_Name_Str2;}

function setDefaultAttValue(sau, num) {
   var sav = eval("document.arrayform.SAV_"+num);
   if (sau.value == "date") {
      sav.title = '(YYYY-MM-DD)';
      if (sav.value == '') sav.value = 'YYYY-MM-DD';
   } else {
      sav.title = '';
      if (sav.value == 'YYYY-MM-DD') sav.value = '';
   }
}

function addAttributeRow(tableID) {
   var table = document.getElementById(tableID);
   var row = table.insertRow(table.rows.length);
   var cell = row.insertCell(0);
   cell.vAlign="top"
   cell.innerHTML = sample_Att_Name(sample_att_count);
   //Check that the col doesn't need any new attributes added!
   cell = row.insertCell(1);
   cell.vAlign="top"
   cell.innerHTML = sample_Att_Val(sample_att_count);
   cell = row.insertCell(2);
   cell.vAlign="top"
   cell.innerHTML = sample_Att_Unit(sample_att_count);
   cell = row.insertCell(3);
   cell.vAlign="top"
   cell.innerHTML = sample_Att_Time(sample_att_count);
   sample_att_count++;
   document.arrayform.sampleAttCount.value = sample_att_count;
}

function showAttTable() {
   if(document.getElementById("attTable")){
      var attTable = document.getElementById("attTable")
      if (attTable.style.display == "none") {
      window.alert("Please enter the details of the new attribute in the section below. When you click \"Add Attribute\" " + 
      "the new attribute will be added to the drop-down box of Attribute Names.");
         attTable.style.display = "";
         document.arrayform.addAtt.focus();
         document.arrayform.newAttName.focus();
      } else {
         attTable.style.display = "none";
         eval("document.arrayform.SAN_"+(sample_att_count-1)+".focus()");
      }
   }
}

var new_att_type = "String";
function updateNewAttAllowable() {
   var attUnit = document.arrayform.SAU_newAttUnits.value;
   if (attUnit == 'string' || attUnit == 'ratio' || attUnit == 'Other' || attUnit == 'NONE') {
      document.arrayform.newAttAllowable.style.display = "";
      document.getElementById("maxNum").style.display = "none";
      document.getElementById("minNum").style.display = "none";
      document.getElementById("maxDate").style.display = "none";
      document.getElementById("minDate").style.display = "none";
      new_att_type = "String";
   } else if (attUnit == 'date') {
      document.arrayform.newAttAllowable.style.display = "none";
      document.getElementById("maxNum").style.display = "none";
      document.getElementById("minNum").style.display = "none";
      document.getElementById("maxDate").style.display = "";
      document.getElementById("minDate").style.display = "";
      new_att_type = "Date";
   } else {
      document.arrayform.newAttAllowable.style.display = "none";
      document.getElementById("maxNum").style.display = "";
      document.getElementById("minNum").style.display = "";
      document.getElementById("maxDate").style.display = "none";
      document.getElementById("minDate").style.display = "none";
      new_att_type = "Num";
   }
}

var num_new_attrs = 0;
function addNewAttribute() {
   var valType = Array();
   var name = Array();
   if (new_att_type == "String") {
      valType[0] = trim(document.arrayform.newAttAllowable.value);
      name[0] = "newAttAllowable" + num_new_attrs;
   } else if (new_att_type == "Date") {
      valType[0] = trim(document.arrayform.maxAllowableDay.value);
      valType[1] = trim(document.arrayform.maxAllowableMonth.value);
      valType[2] = trim(document.arrayform.maxAllowableYear.value);
      valType[3] = trim(document.arrayform.minAllowableDay.value);
      valType[4] = trim(document.arrayform.minAllowableMonth.value);
      valType[5] = trim(document.arrayform.minAllowableYear.value);
      name[0] = "newMaxAllowableDay" + num_new_attrs;
      name[1] = "newMaxAllowableMonth" + num_new_attrs;
      name[2] = "newMaxAllowableYear" + num_new_attrs;
      name[3] = "newMinAllowableDay" + num_new_attrs;
      name[4] = "newMinAllowableMonth" + num_new_attrs;
      name[5] = "newMinAllowableYear" + num_new_attrs;
   } else { //new_att_type is "Num"
      valType[0] = trim(document.arrayform.maxAllowable.value);
      valType[1] = trim(document.arrayform.minAllowable.value);
      name[0] = "newMaxAttAllowable" + num_new_attrs;
      name[1] = "newMinAttAllowable" + num_new_attrs;
   }
   var attName = trim(document.arrayform.newAttName.value);
   var attUnit = document.arrayform.SAU_newAttUnits.value;
   var attDesc = trim(document.arrayform.newAttDesc.value);
   //var attAllowable = trim(document.arrayform.newAttAllowable.value);
   var testingError = '0';
   if (attName == '') {
      highLight(document.arrayform.newAttName,'You need to specify a name for the new attribute.');
      testingError = '1';
   } else if (attUnit == 'NONE') {
      highLight(document.arrayform.SAU_newAttUnits,'You need to select the type of unit for the new attribute.');
      testingError = '1';
   } else if (attDesc == '(Please enter a description here)' || attDesc == '') {
      highLight(document.arrayform.newAttDesc,'You need to enter a brief description for the new attribute.');
      testingError = '1';
      
   } else if (new_att_type == "String" && valType[0] == '(Enter each value\nOn a new line)') {
      highLight(document.arrayform.newAttAllowable,'If you don\'t want to specify allowable values, leave the allowable-values field blank.');
      testingError = '1';
   } else if (new_att_type == "Num" && parseInt(valType[0]) < parseInt(valType[1])) {
      highLight(document.arrayform.maxAllowable,'You need to swap Max and Min Values - Max Value needs to be greater than Min Value.');
      testingError = '1';
   } else if (new_att_type == "Date") {
      //Need to test if Max > Min (Dates are validated by checkDateValid(), below).
      lowLight(document.arrayform.maxAllowableYear);
      lowLight(document.arrayform.minAllowableYear);
      lowLight(document.arrayform.maxAllowableMonth);
      lowLight(document.arrayform.minAllowableMonth);
      lowLight(document.arrayform.maxAllowableDay);
      lowLight(document.arrayform.minAllowableDay);
      if (valType[0] == '' && valType[1] == '' && valType[2] == '' && 
          valType[3] == '' && valType[4] == '' && valType[5] == '') {
         //Do nothing - just checking that at least one of these are set, and if so, process logic below.
      } else if (valType[0] == '') {
         highLight(document.arrayform.maxAllowableDay,'If setting a max and min date, you need to select values for all boxes.');
         testingError = '1';
      } else if (valType[1] == '') {
         highLight(document.arrayform.maxAllowableMonth,'If setting a max and min date, you need to select values for all boxes.');
         testingError = '1';
      } else if (valType[2] == '') {
         highLight(document.arrayform.maxAllowableYear,'If setting a max and min date, you need to select values for all boxes.');
         testingError = '1';
      } else if (valType[3] == '') {
         highLight(document.arrayform.minAllowableDay,'If setting a max and min date, you need to select values for all boxes.');
         testingError = '1';
      } else if (valType[4] == '') {
         highLight(document.arrayform.minAllowableMonth,'If setting a max and min date, you need to select values for all boxes.');
         testingError = '1';
      } else if (valType[5] == '') {
         highLight(document.arrayform.minAllowableYear,'If setting a max and min date, you need to select values for all boxes.');
         testingError = '1';
      } else if (valType[2] < valType[5]) {
         highLight(document.arrayform.maxAllowableYear,'You need to swap Max and Min Dates - Max Date needs to be greater than Min Date.');
         testingError = '1';
      } else if (valType[2] == valType[5]) {
         if (valType[1] < valType[4]) {
            highLight(document.arrayform.maxAllowableMonth,'You need to swap Max and Min Dates - Max Date needs to be greater than Min Date.');
            testingError = '1';
         } else if (valType[1] == valType[4]) {
            if (valType[0] < valType[3]) {
           highLight(document.arrayform.maxAllowableDay,'You need to swap Max and Min Dates - Max Date needs to be greater than Min Date.');
               testingError = '1';
            }
         }
      }
   } 
   if (testingError == '0') {
      lowLight(document.arrayform.newAttName);
      lowLight(document.arrayform.SAU_newAttUnits);
      lowLight(document.arrayform.newAttDesc);
      lowLight(document.arrayform.newAttAllowable);
      lowLight(document.arrayform.maxAllowable);
      fail = "False";
      box = eval("document.arrayform.SAN_0");
      for (i=0; i<box.length; i++) {
         if (box.options[i].text == attName){
            fail = "True";
         }
      }
      if (fail == "True") {
         window.alert("The Attribute '" + attName + "' is already entered");
      } else {
         //Need to take the values in the fields and set them to hidden fields in this form so they'll be entered in the db...
         var newAttName = document.createElement('INPUT');
         newAttName.type = "HIDDEN";
         newAttName.name = "newAttName" + num_new_attrs;
         newAttName.value = attName;
         document.arrayform.appendChild(newAttName);
         
         var newAttUnit = document.createElement('INPUT');
         newAttUnit.type = "HIDDEN";
         newAttUnit.name = "newAttUnit" + num_new_attrs;
         newAttUnit.value = attUnit;
         document.arrayform.appendChild(newAttUnit);
         
         var newAttDesc = document.createElement('INPUT');
         newAttDesc.type = "HIDDEN";
         newAttDesc.name = "newAttDesc" + num_new_attrs;
         newAttDesc.value = attDesc;
         document.arrayform.appendChild(newAttDesc);
      
         for (i=0; i<valType.length; i++) {
            var newAttAllowable = document.createElement('INPUT');
            newAttAllowable.type = "HIDDEN";
            newAttAllowable.name = name[i];
            newAttAllowable.value = valType[i];
            document.arrayform.appendChild(newAttAllowable);
         }
         
         //...then add an entry to the attribute list and give it focus...
         for (i=0; i<sample_att_count; i++) {
            var comboBox = eval("document.arrayform.SAN_"+i);
            //window.alert("combobox has length of " + comboBox.length + "\nAttribute has name " + attName);
            var newOpt = document.createElement("option");
            newOpt.text = attName;
            newOpt.value = attName;
            //newOpt.selected = true;
            
            var browserName = navigator.appName;
            if (browserName == "Netscape" || browserName == "Opera") { 
               comboBox.add(newOpt, null);
            }
            else if (browserName=="Microsoft Internet Explorer") {
               comboBox.add(newOpt);
            }

            if (comboBox.selectedIndex == 0) { 
               comboBox.options[comboBox.length-1].selected = "True";
            }
         }
         
         //Also need to add the value to the string which is used to populate new "attribute name" combo boxes.
         //var regexp = /<\/select>/g;
         Att_Name_Str2 = Att_Name_Str2.replace(/<\/select>/g, "<option>"+attName+"<\/option></select>");
         
         //...then reset the "newAtt" fields so the user can add more and won't have to delete their previous entries.
         document.arrayform.newAttName.value = '';
         document.arrayform.SAU_newAttUnits.selectedIndex = '0';
         document.arrayform.newAttDesc.value = '(Please enter a description here)';
         document.arrayform.newAttAllowable.value = '(Enter each value\nOn a new line)';
         document.arrayform.maxAllowable.value = '';
         document.arrayform.minAllowable.value = '';
         document.arrayform.maxAllowableYear.selectedIndex = '0';
         document.arrayform.minAllowableYear.selectedIndex = '0';
         document.arrayform.maxAllowableMonth.selectedIndex = '0';
         document.arrayform.minAllowableMonth.selectedIndex = '0';
         document.arrayform.maxAllowableDay.selectedIndex = '0';
         document.arrayform.minAllowableDay.selectedIndex = '0';
         showAttTable(); //(i.e. hide the table)
         num_new_attrs++;
      }
   }
}

//================================================================//

monthArray = ["January","February","March","April","May","June","July","August","September","October","November","December"];

function ageFields(prefix) {
   outputString = '<select name="' + prefix + 'Day" onChange="checkDateValid(\'' + prefix + '\')"><option value="">Day';
   //Adding strings for days
   for (i = 1;i < 32; i++) {
      outputString += '<option value="' + i + '">' + i;
   }
   outputString += '</select>\n<select name="' + prefix + 'Month" onChange="checkDateValid(\'' + prefix + '\')"><option value="">Month';
   for (i = 0;i < 12; i++) {
      outputString += '<option value="' + (i+1) + '">' + monthArray[i];
   }
   outputString += '</select>\n<select name="' + prefix + 'Year" onChange="checkDateValid(\'' + prefix + '\')"><option value="">Year';
   var start = new Date();
   var startYear = start.getFullYear();
   for (i = startYear;i >= 1980; i--) {
      outputString += '<option value="' + i + '">' + i;
   }
   outputString += '</select>\n';
   return outputString;
}

function checkDateValid(prefix) {
   var dayField = eval('document.arrayform.' + prefix + 'Day');
   var day = dayField.value;
   var monthField = eval('document.arrayform.' + prefix + 'Month');
   var month = monthArray[monthField.value-1];
   var yearField = eval('document.arrayform.' + prefix + 'Year');
   var year = yearField.value;
   if ((month == "September" || month == "April" || month == "June" || month == "November") && day == "31") {
      window.alert("There are only 30 days in " + month + ".");
      dayField.value = "30";
   } else if (month == "February" && (day == "31" || day == "30" ||day == "29") && year%4 != "0") {
      window.alert("There are only 28 days in February in " + year + ".");
      dayField.value = "28";   
   } else if (month == "February" && (day == "31" || day == "30") && year%4 == "0") {
      window.alert("There are only 29 days in February in " + year + ".");
      dayField.value = "29";   
   }
}

//function addNewTissue() {
//   var fail = "False";
//   var box = document.arrayform.Tissue;
//   var newType = trim(window.prompt("Please enter the name of the tissue type that you want to add to the list:"));
//   if (newType != null && newType != '') {
//      for (var i=0; i<box.length; i++) {
//         testStr = trim(box.options[i].text);
//         if (testStr.toLowerCase() == newType.toLowerCase()){
//            fail = "True";
//            break;
//         }
//      }
//      if (fail == "True") {
//         window.alert("The Attribute '" + newType + "' is already entered");
//      } else {
//         var newOpt = document.createElement("option");
//         newOpt.text = newType;
//         newOpt.value = newType;
//         
//         var browserName = navigator.appName;
//         if (browserName == "Netscape" || browserName == "Opera") { 
//            box.add(newOpt, null);
//            box.options[box.length-1].selected = "True";
//         }
//         else if (browserName=="Microsoft Internet Explorer") {
//            box.add(newOpt);
//            box.options[box.length-1].selected = "True";
//         }
//      }
//   }
//}

//================================================================//

</script>
</head><body>
<FORM name="arrayform" onSubmit="return checkAll();" METHOD="POST" ENCTYPE="multipart/form-data" ACTION="/cgi-bin/agbrdf/form.py" >
<input type="HIDDEN" name="sessionid" value="0"/>
<input type="HIDDEN" name="formname" value="microarraySampleForm"/>
<input type="HIDDEN" name="sampleAttCount" value="1"/> 
   
<table border="true" id="Top_table" width=100%>
   <tr> 
      <td colspan="2"> 
         <h1 class="top">AgResearch Microarray Upload Form</h1>
      </td>
   </tr>
   <tr> 
      <td colspan="2"> 
         <table align=center class=plainTable style="border-width: 0">
            <tr align=center valign=middle>
               <td class=color1 title="Define one or more protocols if required" onclick="goToPage('MicroarrayForm1.htm');">
                  <img src="/images/protocol.gif" border="0" height="42" width="42"/>
                  <br>Protocol
               </td>
               <td class=arrow>
                  &rarr;
               </td>
               <td class=color2 title="Define one or more experimental subjects if required" onclick="goToPage('MicroarrayForm2.htm');">
                  <img src="/images/sheep.gif" border="0" height="42" width="42"/>
                  <br>Subject
               </td>
               <td class=arrow>
                  &rarr;
               </td>
               <td class=color0 title="Define one or more samples if required">
                  <img src="/images/eppendorf.gif" border="0" height="42" width="42"/>
                  <br>Sample
               </td>
               <td class=arrow>
                  &rarr;
               </td>
               <td class=color4 title="Submit Files" onclick="goToPage('MicroarrayForm4.htm');">
                  <img src="/images/microarray.jpg" border="0" height="42" width="42"/>
                  <br>Files
               </td>
               <td class=arrow>
                  &rarr;
               </td>
               <td class=color5 title="Define Series" onclick="goToPage('MicroarrayForm5.htm');">
                  <img src="/images/series.gif" border="0" height="42" width="42"/>
                  <br>Series
               </td>
               <td class=arrow>
                  &rarr;
               </td>
               <td class=color6 title="Define contrasts" onclick="goToPage('MicroarrayForm6.htm');">
                  <img src="/images/contrast.gif" border="0" height="42" width="42"/>
                  <br>Contrasts
               </td>
               <td class=arrow>
                  &rarr;
               </td>
               <td class=color7 title="Submit related documents (if any)" onclick="goToPage('MicroarrayForm7.htm');">
                  <img src="/images/documents.gif" border="0" height="42" width="42"/>
                  <br>Documents
               </td>
            </tr>
         </table>
      </td>
   </tr>
</table>
<br>
<table border="true" id="Outer_table" width=100%>
   <tr>
      <td colspan=2 >
         <div style="text-align: center; font-size: 150%; font-weight: bold; line-height: 2">Sample</div>
         <div style="text-align: left; font-size: 90%; font-weight: normal;">
            Define any samples you have used in your experiment with this form. If all your samples are in 
            the list below, click Next to go to the next form</div>
      </td>
   </tr>
   
   <tr>
      <td class="fieldname" width=17%>
         <p class="fieldname"><b>Existing samples:</b>
      </td>
      <td width=83%>
          <select name="sample" size=10>
             <option value="">
             <!--__EXISTING_SAMPLES__-->
          </select>
          <button style="margin: 70px 10px;" type=button onClick="goToPage('MicroarrayForm4.htm')">Next &gt;</button>
      </td>
   </tr>
   <tr>
      <td colspan=2>
         <p style="text-align: left; font-size: 120%; font-weight: bold; text-decoration: underline;">New Sample</p>
      </td>
   </tr>
   <tr>
      <td class="fieldname" width=17%>
         <p class="fieldname"><b>Sample name:</b>
      </td>
      <td class="input" width=83%>
          <input name="sampleName" value="" size="50" type="text"/>
      </td>
   </tr>
   <tr>
      <td class="fieldname" width=17%>
         <p class="fieldname"><b>Sample type:</b>
      </td>
      <td class="input" width=83%>
         <select name="sampleType" >
            <option value="" selected>
            <!--__EXISTING_BIOSAMPLE_TYPES__-->
         </select>
         <!--&nbsp;&nbsp; Other type (not in list): 
         <input name="otherType" value="" size="40"/-->
      </td>
   </tr>    
   <tr>
      <td class="fieldname" width=17%>
         <p class="fieldname"><b>Sample tissue:</b>
      </td>
      <td class="input" width=83%>
         <select name="Tissue" >
            <option value="" selected>
            <!--__EXISTING_TISSUE_TYPES__-->
         </select>
         <!--&nbsp;&nbsp;<button type=button onclick="addNewTissue();">Define new Tissue</button-->
      </td>
   </tr>    
   <tr>
      <td>
         <p><b>Sample attributes:</b>
      </td>
      <td>
     <table id="attributes_table" class=plainTable>
        <tr>
           <th nowrap align=left><label>Attribute Name</label></th>
           <th nowrap align=left><label>Attribute Value</label></th>
           <th nowrap align=left><label>Attribute Units</label></th>
           <th nowrap align=left><label>Attribute TimeStamp</label></th>
           </tr>
        <tr>
           <td><script>document.write(sample_Att_Name('0'));</script></td>
           <td><script>document.write(sample_Att_Val('0'));</script></td>
           <td><script>document.write(sample_Att_Unit('0'));</script></td>
           <td><script>document.write(sample_Att_Time('0'));</script></td>
        </tr>
     </table>
         <button type=button onclick="addAttributeRow('attributes_table');">Record More Attributes</button>
         <button type=button onclick="showAttTable();">Define a new Attribute</button>
      </td>
   </tr>
   <tr>
      <td>
         <p><b>Sample description:</b>
      </td>
      <td>
     <textarea name="sampleDesc" title="Please enter a description here" type="textarea" rows="4" cols="72">(Please enter a description here)</textarea> 
      </td>
   </tr>
   <tr>
      <td>
         <p><b>Experimental subject(s):</b>
      </td>
      <td>
          <select name="subject" title="Select one or many subjects" onChange="otherSelected(this, AddSubj)" multiple=true size="5">
             <option value="" selected>
             <!--__EXISTING_SUBJECTS__-->
             <option value="Other">Other
          </select>
          <button name="AddSubj" style="display: none;" type=button onClick="goToPage('MicroarrayForm2.htm');">Add Subject</button>
      </td>
   </tr>
   <tr>
      <td>
         <p><b>Protocols used in sampling:</b>
      </td>
      <td>
          <select name="protocol" onChange="otherSelected(this, AddProto)">
             <option value="" selected>
             <!--__EXISTING_PROTOCOLS__-->
             <option value="Other">Other
          </select>
          <button name="AddProto" style="display: none;" type=button onClick="goToPage('MicroarrayForm1.htm');">Add Protocol</button>
      </td>
   </tr>
   <tr><td colspan=2>
   <P><i>
   Please <a href="mailto:alan.mcculloch@agresearch.co.nz;jason.mitchell@agresearch.co.nz?subject=Microarray Suggestion">email us</a> with any suggestions for improvements to this form.
   </i>
   </td></tr>
   <tr>
      <td colspan=2 align=center>
         <p><input id="submitButton" type="submit" value="Submit Sample">
      </td>
   </tr>
</table>
<br>
<table id="attTable" style="display: none;" border="true">
   <tr>
      <td colspan=2 align=center>
         <p style="text-align: center; font-size: 120%; font-weight: bold; text-decoration: underline;">Define a new Attribute</p>
      </td>
   </tr>
   <tr>
      <td class="fieldname">
         <p class="fieldname"><b>Attribute Name:</b>
      </td>
      <td class="input">
         <input name="newAttName" value="" size="20" type="text"/>
      </td>
   </tr>
   <tr>
      <td class="fieldname">
         <p class="fieldname"><b>Attribute Unit:</b>
      </td>
      <td class="input">
         <script>document.write(sample_Att_Unit('newAttUnits'));</script>
      </td>
   </tr>
   <tr>
      <td class="fieldname">
         <p class="fieldname"><b>Attribute Desc:</b>
      </td>
      <td class="input">
     <textarea name="newAttDesc" title="Please enter a description here" type="textarea" rows="4" cols="45">(Please enter a description here)</textarea> 
      </td>
   </tr>
   <tr>
      <td class="fieldname">
         <p class="fieldname"><b>Allowable Values:</b>
      </td>
      <td class="input">
     <textarea name="newAttAllowable" title="Enter each value on a new line" type="textarea" rows="4" cols="45">(Enter each value
On a new line)</textarea> 
         <p id="maxNum" style="display: none;">Maximum Value: <input name="maxAllowable" value="" type="text"/>
         <p id="minNum" style="display: none;">Minimum Value: &nbsp;<input name="minAllowable" value="" type="text"/>
         <p id="maxDate" style="display: none;">Maximum Value: <script>document.write(ageFields('maxAllowable'));</script>
         <p id="minDate" style="display: none;">Minimum Value: &nbsp;<script>document.write(ageFields('minAllowable'));</script>
      </td>
   </tr>
   <tr>
      <td colspan=2 align=center>
         <p><input name="addAtt" type="button" value="Add Attribute" onClick="addNewAttribute();">
      </td>
   </tr>
</table>
</FORM>
</body>
</html>
"""

form_microarrayFileForm = r"""
<html>
<head>
<title>AgResearch - Microarray Upload Form</title>
<style>
body        {margin-top: 1cm ; margin-bottom: 1cm; margin-left: 5%; margin-right: 5%; 
        font-family: arial, helvetica, geneva, sans-serif;BACKGROUND: #f0f9ff}

p        {margin-top: .3cm ; margin-bottom: .3cm; margin-left: .4cm; margin-right: .4cm; 
        font-family: arial, helvetica, geneva, sans-serif}
p.fieldname     {margin-top: .3cm ; margin-bottom: .3cm; margin-left: .4cm; margin-right: .4cm; 
        font-family: arial, helvetica, geneva, sans-serif}
p.footer    {text-align: center ; margin-top: 0.5cm ; margin-bottom: 0.5cm; font-family: arial, helvetica, geneva, sans-serif}

b.b        {font-family: arial, helvetica, geneva, sans-serif; font-weight: 700; color: #424b50}
ul        {font-family: arial, helvetica, geneva, sans-serif}
ol        {font-family: arial, helvetica, geneva, sans-serif}
dl        {font-family: arial, helvetica, geneva, sans-serif}

th              {font-family: arial, helvetica, geneva, sans-serif; font-weight: 400}

h1        {text-align: center; color: #388fbd; 
        font-family: arial, helvetica, geneva, sans-serif}
h1.new          {text-align: center; color: #4d585e;
                font-family: arial, helvetica, geneva, sans-serif}
h1.b1           {margin-top: 0.5cm; text-align: center; color:#2d59b2;
                font-family: arial, helvetica, geneva, sans-serif}
h1.b2           {margin-top: 0.5cm; text-align: center; color:#1d7db5;
                font-family: arial, helvetica, geneva, sans-serif}
h1.top        {margin-top: 0.5cm; text-align: center; color: blue;
        font-family: arial, helvetica, geneva, sans-serif}

h2        {text-align: center; font-family: arial, helvetica, geneva, sans-serif}
h3        {font-family: arial, helvetica, geneva, sans-serif}
h4        {font-family: arial, helvetica, geneva, sans-serif}
h5        {font-family: arial, helvetica, geneva, sans-serif}
h6        {font-family: arial, helvetica, geneva, sans-serif}
a         {font-family: arial, helvetica, geneva, sans-serif}

table       {background-color: antiquewhite}

input.detail       {margin-left: 1cm}

textarea.detail    {margin-left: 1cm}

td        {font-family: arial, helvetica, geneva, sans-serif}
td.fieldname    {font-family: arial, helvetica, geneva, sans-serif}

tr          {background-color: #B1FF92}
.plainTable        {background-color: #B1FF92}
a:hover     {color: blue; text-decoration: underline }

.color0          {border: solid black; border-width: 5px; width: 80px; height: 80px}
.color1          {background-color: #FF9292; border: solid black; border-width: 1px; cursor: pointer; width: 88px; height: 88px}
.color2          {background-color: #FFDA92; border: solid black; border-width: 1px; cursor: pointer; width: 88px; height: 88px}
.color3          {background-color: #FFFF92; border: solid black; border-width: 1px; cursor: pointer; width: 88px; height: 88px}
.color4          {background-color: #B1FF92; border: solid black; border-width: 1px; cursor: pointer; width: 88px; height: 88px}
.color5          {background-color: #92E7FF; border: solid black; border-width: 1px; cursor: pointer; width: 88px; height: 88px}
.color6          {background-color: #9C92FF; border: solid black; border-width: 1px; cursor: pointer; width: 88px; height: 88px}
.color7          {background-color: #F392FF; border: solid black; border-width: 1px; cursor: pointer; width: 88px; height: 88px}

.arrow           {font-size: 200%; width: 40px}
</style>
<script language="JavaScript">

var alreadySubmitted = false;

function checkAll() {
   // make sure we have not already submitted this form
   if(alreadySubmitted) {
      window.alert("This Form has already been submitted, please wait");
      return false;
   }

   //submittedby field
   if(trim(document.arrayform.submittedby.value) == "") {
      highLight(document.arrayform.submittedby,"Please enter your name");
      return false;
   } else {
      lowLight(document.arrayform.submittedby);
   }   
   
   //emailaddress field
   if(trim(document.arrayform.emailaddress.value) == "") {
      highLight(document.arrayform.emailaddress,"Please enter your email address");
      return false;
   } else {
      lowLight(document.arrayform.emailaddress);
   }   
   
   //projectID and otherProject fields
   if(trim(document.arrayform.projectID.value) == "" && trim(document.arrayform.otherProject.value) =="") {
      lowLight(document.arrayform.otherProject);
      highLight(document.arrayform.projectID,"Please select a project. If your project is not listed, select \"Other\" " +
      "and enter the code into the \"Other Project\" field. In the future this code will appear in the dropdown box.");
      return false;
   } else if (trim(document.arrayform.projectID.value) == "Other" && trim(document.arrayform.otherProject.value) =="") {
      lowLight(document.arrayform.projectID);
      highLight(document.arrayform.otherProject,"Please enter your project code into the \"Other Project\" field.");
      return false;
   } else if (trim(document.arrayform.projectID.value) == "" && trim(document.arrayform.otherProject.value) !="") {
      lowLight(document.arrayform.otherProject);
      highLight(document.arrayform.projectID,"Please select \"Other\" from the dropdown box.");
      return false;
   } else if (trim(document.arrayform.projectID.value) != "Other" && trim(document.arrayform.otherProject.value) !="") {
      lowLight(document.arrayform.projectID);
      highLight(document.arrayform.otherProject,"Please remove the value from the \"Other Project\".");
      return false;
   } else {
      lowLight(document.arrayform.projectID);
      lowLight(document.arrayform.otherProject);
   }
   
   //sub-prog field
   if(trim(document.arrayform.subProgram.value) == "") {
      highLight(document.arrayform.subProgram,"Please enter a sub-program.");
      return false;
   } else {
      lowLight(document.arrayform.subProgram);
   }
   
   //reason field
   if(trim(document.arrayform.reason.value) == "") {
      highLight(document.arrayform.reason,"Please enter a reason for submission.");
      return false;
   } else {
      lowLight(document.arrayform.reason);
   }
   
   //expName field
   var expN = document.arrayform.expName;
   var oExp = document.arrayform.otherExp;
   if(expN.value == "" && trim(oExp.value) == "") {
      lowLight(oExp);
      highLight(expN,"Please select an experiment name. If your want to create a new name, " +
      "select \"New Experiment\" and enter the experiment name into the \"New Name\" field. After you submit " +
      "the form, this name will be available in the dropdown box for future uploads.");
      return false;
   } else if (expN.value == "New Experiment" && trim(oExp.value) == "") {
      lowLight(expN);
      highLight(oExp,"Please enter the new experiment name into the \"New Name\" field.");
      return false;
   } else if (expN.value == "" && trim(oExp.value) != "") {
      lowLight(oExp);
      highLight(expN,"Please select \"New Experiment\" from the dropdown box.");
      return false;
   } else if (expN.value != "New Experiment" && trim(oExp.value) != "") {
      lowLight(expN);
      highLight(oExp,"Please remove the value from the \"New Experiment\" field.");
      return false;
   } else if (trim(oExp.value).match(/[^\w ]/) != null) {
      highLight(oExp,"You may only name your experiment using the characters 'A-Z', 'a-z', '0-9', '_' and spaces.");
      return false;
   } else {
      lowLight(expN);
      lowLight(oExp);
   }


   for (var i=0; i<file_count; i++) {
      //Check Array selected (& one day, if it matches the number of channels)
      var arCh = eval("document.arrayform.arrayChannels"+i);
      if (arCh.value == '') {
         highLight(arCh,"You must select the number of channels.");
         return false;
      } else {
         lowLight(arCh);
      }
      var arCo = eval("document.arrayform.arrayCombo"+i);
      if (arCo.value == '') {
         highLight(arCo,"You must select the type of array. If you can't find the right one, select \"Other\".");
         return false;
      } else {
         lowLight(arCo);
      }
      
      //Check all channel-samples are selected
      var chOpts = ['pinkSample','greenSample','blueSample','yellowSample'];
      for (j=0; j<arCh.value; j++) {
         var ch = eval("document.arrayform."+chOpts[j]+i);
         if (ch.value == '') {
            highLight(ch,"You must select a sample for each channel.");
            return false;
         } else {
            lowLight(ch);
         }
      }
      
      // check the gpr filename out
      var file = eval("document.arrayform.external_filename"+i);
      var fileType = eval("document.arrayform.IMPORT_TYPE"+i);
      var regex = trim(file.value).match(/^.+\.(gpr|chp)$/i);
      if (trim(file.value) == "") {
         highLight(file,"You must specify a file to be uploaded");
         return false;
      } else if (regex == null) {
         highLight(file,"Your file doesn't appear to be a GenePix GPR or Affymetrix CHP file. These are the only filetypes accepted.");
         return false;
      } else if (regex != null) {
         if (regex[1].toLowerCase() == 'gpr' && fileType.value == 'DNASEQUENCE_MICROARRAY_CHP') {
            highLight(fileType,"Your file is a GenePix GPR file. Please select this file type.");
            return false;
         } else if (regex[1].toLowerCase() == 'chp' && fileType.value == 'DNASEQUENCE_MICROARRAY_GPR') {
            highLight(fileType,"Your file is a Affymetrix CHP file. Please select this file type.");
            return false;
         } else {
            lowLight(file);
            lowLight(fileType);
         }
      }
      
      //if GPR, check that checksum is selected (need to set up checksum for Affy Array files)
      var chkSum = eval("document.arrayform.checkSum"+i);
      if (regex != null && regex[1].toLowerCase() == 'gpr' && trim(chkSum.value) == '') {
         highLight(chkSum,"You need to enter a checksum to ensure that the file has been uploaded correctly.");
         return false;
      } else if (trim(chkSum.value) != '') {
         regex2 = trim(chkSum.value).match(/^-?\d+\.?\d*$|^-?\.\d+$/);
         if (regex2 == null) {
            highLight(chkSum,"The checksum doesn't appear to be a number!");
            return false;
         } else {
            lowLight(chkSum);
         }
      } else {
         lowLight(chkSum);
      }
      
      //check the desc field has been edited && is > 30 chars long
      var desc = eval("document.arrayform.experiment_description"+i);
      if (trim(desc.value) == "(Please enter a description here)") {
         highLight(desc,"Please enter a description of the Experiment.");
         return false;
      }else if (trim(desc.value).length <= 30) {
         highLight(desc,"Please enter a longer description of the Experiment (i.e. > 30 characters).");
         return false;
      } else {
         lowLight(desc);
      }
      
      //??? check if any "other files" have been added???
      //The loop below just checks that the file and filetype fields are either both filled in, or neither are.
      for (j=0; j<other_file_count[i]; j++) {
         var imgFile = eval("document.arrayform.file"+i+"_"+j);
         var imgFileType = eval("document.arrayform.fileType"+i+"_"+j);
         if (trim(imgFile.value) == '' && trim(imgFileType.value) != '') {
            highLight(imgFile,"Please enter a file.");
            lowLight(imgFileType);
            return false;
         } else if (trim(imgFile.value) != '' && trim(imgFileType.value) == '') {
            highLight(imgFileType,"Please enter a file type.");
            lowLight(imgFile);
            return false;
         } else {
            lowLight(imgFile);
            lowLight(imgFileType);
         }
      }
   }

   // finally, set the submitted flag
   btn = document.getElementById("submitButton");
   btn.value = "Submitting, please wait...";
   btn.disabled = true;
   
   alreadySubmitted = true;
   return true;
}

function highLight(item,message) {
   item.style.background = 'red';
   window.alert(message);
   item.focus();
} // assume IE

function lowLight(item) {
   item.style.background = '';
}

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


function fileTableLine1(id) {
   return 'Select number of channels: <select id="arrayChannels'+id+'" name="arrayType'+id+'" SIZE=1 onChange="setChannelNumber(this.value, \'channels'+id+'\');">' +
        //'<option value="">' +
        '<option value="1"> Single-channel array' +
        '<option value="2" selected> Two-channel array' +
        '<option value="4"> Four-channel array' +
         '</select>' +
         '<br>Which Array?:' +
         '<select id="arrayCombo'+id+'" name="arrayName'+id+'" SIZE=1>' +
        '<OPTION value="" selected>' +
        '<OPTION value="A-AFFY-16">Affymetrix GeneChip Arabidopsis Genome [AG1]' +
        '<OPTION value="A-AFFY-2">Affymetrix GeneChip Arabidopsis Genome [ATH1-121501]' +
        '<OPTION value="A-AGIL-4">Agilent Arabidopsis 2 Oligo Microarray [G4136A]' +
        '<OPTION value="A-AGIL-12">Agilent Arabidopsis 3 Oligo Microarray [G4142A]' +
        '<OPTION value="A-AFFY-60">Affymetrix GeneChip C. elegans Genome Array [Celegans]' +
        '<OPTION value="A-AFFY-38">Affymetrix GeneChip Zebrafish Genome Array [Zebrafish]' +
        '<OPTION value="A-AFFY-17">Affymetrix GeneChip Drosophila Genome [DrosGenome1]' +
        '<OPTION value="A-AFFY-35">Affymetrix GeneChip Drosophila Genome 2.0 Array [Drosophila_2]' +
        '<OPTION value="A-AFFY-50">Affymetrix GeneChip Drosophila Tiling Array Set - Forward Array (G6 scanner)' +
        '<OPTION value="A-AFFY-52">Affymetrix GeneChip Drosophila Tiling Array Set - Forward Array [Dm35b_MF_v02]' +
        '<OPTION value="A-AFFY-53">Affymetrix GeneChip Drosophila Tiling Array Set - Reverse Array [Dm35b_MR_v02]' +
        '<OPTION value="A-AFFY-29">Affymetrix GeneChip E.coli Antisense Genome Array [Ecoli_ASv2]' +
        '<OPTION value="A-AFFY-28">Affymetrix GeneChip E.coli Genome (Sense) [Ecoli]' +
        '<OPTION value="A-AFFY-56">Affymetrix GeneChip E.coli Genome 2.0 Array [E_coli_2]' +
        '<OPTION value="A-MEXP-129">MWG E. coli K12 V2 Array' +
        '<OPTION value="A-TOXM-10">[ILSI] Clontech Atlas Glass Human 1.0 [#7900]' +
        '<OPTION value="A-AFFY-65">Affymetrix GeneChip Human Mapping 10K 2.0 Array Xba 142' +
        '<OPTION value="A-AFFY-64">Affymetrix GeneChip Human Mapping 10K Array Xba 131' +
        '<OPTION value="A-AFFY-32">Affymetrix GeneChip HuGeneFL Array [HuGeneFL]' +
        '<OPTION value="A-AFFY-41">Affymetrix GeneChip Human Genome Focus Array [HG-Focus]' +
        '<OPTION value="A-AFFY-33">Affymetrix GeneChip Human Genome HG-U133A [HG-U133A]' +
        '<OPTION value="A-AFFY-34">Affymetrix GeneChip Human Genome HG-U133B [HG-U133B]' +
        '<OPTION value="A-AFFY-44">Affymetrix GeneChip Human Genome U133 Plus 2.0 [HG-U133_Plus_2]' +
        '<OPTION value="A-AFFY-37">Affymetrix GeneChip Human Genome U133A 2.0 [HG-U133A_2]' +
        '<OPTION value="A-AFFY-9">Affymetrix GeneChip Human Genome U95A [HG_U95A]' +
        '<OPTION value="A-AFFY-1">Affymetrix GeneChip Human Genome U95Av2 [HG_U95Av2]' +
        '<OPTION value="A-AFFY-10">Affymetrix GeneChip Human Genome U95B [HG_U95B]' +
        '<OPTION value="A-AFFY-11">Affymetrix GeneChip Human Genome U95C [HG_U95C]' +
        '<OPTION value="A-AFFY-12">Affymetrix GeneChip Human Genome U95D [HG_U95D]' +
        '<OPTION value="A-AFFY-13">Affymetrix GeneChip Human Genome U95E [HG_U95E]' +
        '<OPTION value="A-AFFY-54">Affymetrix GeneChip Human X3P Array [U133_X3P]' +
        '<OPTION value="A-MEXP-287">Agilent Human 1 cDNA Microarray - Langland layout' +
        '<OPTION value="A-MEXP-132">Agilent Human 1 cDNA Microarray [G4100A]' +
        '<OPTION value="A-AGIL-9">Agilent Human 1A Microarray(V2)[G4110B]' +
        '<OPTION value="A-AGIL-7">Agilent Human 1B Microarray [G4111A]' +
        '<OPTION value="A-MEXP-97">Agilent Human Oligo 22K Array 60-25mer' +
        '<OPTION value="A-AGIL-11">Agilent Whole Human Genome Oligo Microarray [G4112A]' +
        '<OPTION value="A-MEXP-218">Agilent Whole Human Genome Oligo Microarray [G4112A] (non-Agilent scanners)' +
        '<OPTION value="A-AGIL-14">Agilent Human 1A Oligo (60-mer) Microarray (2004 annotation) [G4110A]' +
        '<OPTION value="A-AGIL-3">Agilent Human 1A Oligo (60-mer) Microarray (pre 2004 annotation) [G4110A]' +
        '<OPTION value="A-MEXP-166">Amersham CodeLink UniSet Human 10K II Bioarray' +
        '<OPTION value="A-MEXP-162">Amersham CodeLink UniSet Human 10K I Bioarray' +
        '<OPTION value="A-MEXP-131">Clontech Atlas Glass Human 3.8 Array' +
        '<OPTION value="A-MEXP-304">Dessen Agilent Whole Human Genome oligo array' +
        '<OPTION value="A-GEHB-1">GE Healthcare/Amersham Biosciences CodeLink Human Whole Genome Bioarray' +
        '<OPTION value="A-GEHB-2">GE Healthcare/Amersham Biosciences CodeLink UniSet Human 20K I Bioarray' +
        '<OPTION value="A-MEXP-196">IGR Agilent P_IGR_001 Human 22K v1' +
        '<OPTION value="A-MEXP-133">MWG Pan Human 10K Array A' +
        '<OPTION value="A-MEXP-126">RFCGR_HGMP_Human_Hs_Clone_Av1' +
        '<OPTION value="A-MEXP-63">RFCGR_HGMP_Human_Hs_Clone_Av2' +
        '<OPTION value="A-MEXP-52">RFCGR_HGMP_Human_Hs_SGC_Av1' +
        '<OPTION value="A-MEXP-53">RFCGR_HGMP_Human_Hs_SGC_Bv1' +
        '<OPTION value="A-MEXP-265">Sanger H. sapiens Encode chip 25.3K ENCODE1.1.1' +
        '<OPTION value="A-MEXP-510">Sanger H. sapiens Whole Genome Tile Path 26.6k v1' +
        '<OPTION value="A-MEXP-511">Sanger H. sapiens Whole Genome Tile Path 26.6k v2' +
        '<OPTION value="A-SNGR-5">Sanger Institute H. sapiens 10K array, Hver1.2.1' +
        '<OPTION value="A-MEXP-522">Sanger Institute H. sapiens 10K array, Hver1.3.1' +
        '<OPTION value="A-MEXP-210">Sanger Institute H. sapiens 15K array, Hver2.1.1' +
        '<OPTION value="A-SNGR-3">Sanger Institute H. sapiens 5K-1 array, Hver1.1.1' +
        '<OPTION value="A-SNGR-4">Sanger Institute H. sapiens 5K-2 array, Hver1.1.2' +
        '<OPTION value="A-MEXP-204">Sanger Institute H. sapiens Chr1-TP-2 12k v2' +
        '<OPTION value="A-MEXP-156">Sanger Institute H. sapiens Encode chip 21.6K ENCODE2.1.1' +
        '<OPTION value="A-MEXP-215">Sanger Institute H. sapiens Encode chip 31.2K ENCODE3.1.1' +
        '<OPTION value="A-MEXP-345">Sanger-Nimblegen Human array painting array_Case 1' +
        '<OPTION value="A-MEXP-344">Sanger-Nimblegen Human array painting array_Cases 2-4' +
        '<OPTION value="A-UHNC-4">UHN Homo sapiens 1.7k2 array' +
        '<OPTION value="A-UHNC-1">UHN Homo sapiens 1.7k3 array' +
        '<OPTION value="A-UHNC-2">UHN Homo sapiens 1.7k4 array' +
        '<OPTION value="A-UHNC-8">UHN Homo sapiens 1.7k7 array' +
        '<OPTION value="A-UHNC-7">UHN Homo sapiens 1.7k8 array' +
        '<OPTION value="A-UHNC-5">UHN Homo sapiens 19k4 array' +
        '<OPTION value="A-UHNC-6">UHN Homo sapiens 19k6 array' +
        '<OPTION value="A-UHNC-13">UHN Homo sapiens CGI12k1' +
        '<OPTION value="A-UHNC-9">UHN Homo sapiens DSH19k2 Part A' +
        '<OPTION value="A-UHNC-10">UHN Homo sapiens DSH19k2 Part B' +
        '<OPTION value="A-UHNC-11">UHN Homo sapiens DSH19k3 Part A' +
        '<OPTION value="A-UHNC-12">UHN Homo sapiens DSH19k3 Part B' +
        '<OPTION value="A-AFFY-31">Affymetrix GeneChip Barley Genome [Barley1]' +
        '<OPTION value="A-MEXP-174">Washington Rhesus Macaque 11K Agilent oligo array' +
        '<OPTION value="A-AFFY-23">Affymetrix GeneChip Mouse Expression Array MOE430A [MOE430A]' +
        '<OPTION value="A-AFFY-24">Affymetrix GeneChip Mouse Expression Array MOE430B [MOE430B]' +
        '<OPTION value="A-AFFY-45">Affymetrix GeneChip Mouse Genome 430 2.0 [Mouse430_2]' +
        '<OPTION value="A-AFFY-36">Affymetrix GeneChip Mouse Genome 430A 2.0 [Mouse430A_2]' +
        '<OPTION value="A-AFFY-14">Affymetrix GeneChip Murine 11K Genome [Mu11KsubA]' +
        '<OPTION value="A-AFFY-15">Affymetrix GeneChip Murine 11K Genome [Mu11KsubB]' +
        '<OPTION value="A-AFFY-3">Affymetrix GeneChip Murine Genome U74A [MG_U74A]' +
        '<OPTION value="A-AFFY-6">Affymetrix GeneChip Murine Genome U74Av2 [MG_U74Av2]' +
        '<OPTION value="A-AFFY-4">Affymetrix GeneChip Murine Genome U74B [MG_U74B]' +
        '<OPTION value="A-AFFY-7">Affymetrix GeneChip Murine Genome U74Bv2 [MG_U74Bv2]' +
        '<OPTION value="A-AFFY-5">Affymetrix GeneChip Murine Genome U74C [MG_U74C]' +
        '<OPTION value="A-AFFY-8">Affymetrix GeneChip Murine Genome U74Cv2 [MG_U74Cv2]' +
        '<OPTION value="A-MEXP-72">Agilent cDNA 10K Mouse Array (G4104A)' +
        '<OPTION value="A-AGIL-8">Agilent Mouse Microarray [G4121A]' +
        '<OPTION value="A-MEXP-89">Agilent Mouse Oligo (Tox) G4121A' +
        '<OPTION value="A-AGIL-13">Agilent Whole Mouse Genome [G4122A]' +
        '<OPTION value="A-AGIL-2">Agilent Mouse (Development) Oligo (60-mer) Microarray [G4120A]' +
        '<OPTION value="A-MEXP-73">Amersham CodeLink Uniset Mouse I Bioarray' +
        '<OPTION value="A-MEXP-32">HGMP, M.musculus 6.1k array 1' +
        '<OPTION value="A-CBIL-5">Incyte MouseGEM 1.14, 1.16, 1.26' +
        '<OPTION value="A-MEXP-198">NIA Agilent Mouse 22K Microarray v2.0 (Development 60-mer Oligo)' +
        '<OPTION value="A-MEXP-199">NIA Agilent Mouse 44K Microarray v1.0 (Development-Toxicology 60-mer Oligo)' +
        '<OPTION value="A-MEXP-163">NIA Agilent Mouse 44K Microarray v2.0 (Whole Genome 60-mer Oligo)' +
        '<OPTION value="A-MEXP-200">NIA Agilent Mouse 44K Microarray v2.1 (Whole Genome 60-mer Oligo)' +
        '<OPTION value="A-MEXP-62">RFCGR_HGMP_Mouse_Mm_Immuno_Av2' +
        '<OPTION value="A-MEXP-64">RFCGR_HGMP_Mouse_Mm_NIA_Av2' +
        '<OPTION value="A-MEXP-65">RFCGR_HGMP_Mouse_Mm_NIA_Bv2' +
        '<OPTION value="A-MEXP-165">RFCGR_HGMP_Mouse_Mm_SGC_Av1' +
        '<OPTION value="A-MEXP-54">RFCGR_HGMP_Mouse_Mm_SGC_Av2' +
        '<OPTION value="A-SNGR-16">Sanger Institute M. musculus array, Mver1.1.1' +
        '<OPTION value="A-SNGR-17">Sanger Institute M. musculus array, Mver1.2.1' +
        '<OPTION value="A-UHNC-14">UHN Mus musculus 15kv1 array' +
        '<OPTION value="A-UHNC-3">UHN Mus musculus 15kv3 array' +
        '<OPTION value="A-AGIL-10">Agilent Rice Microarray [G4138A]' +
        '<OPTION value="A-AFFY-30">Affymetrix GeneChip P. aeruginosa Genome[Pae_G1a]' +
        '<OPTION value="A-MEXP-34">RFCGR_HGMP_Rat_Rn_SGC_Av1' +
        '<OPTION value="A-AFFY-42">Affymetrix GeneChip S. cerevisiae Tiling' +
        '<OPTION value="A-SGRP-1">Sanger Institute PSU Salmonella Enterica. Array' +
        '<OPTION value="A-AFFY-46">Affymetrix GeneChip SARS Resequencing Array' +
        '<OPTION value="A-SGRP-2">Sanger Institute PSU Schistosoma mansoni EST Array' +
        '<OPTION value="A-SNGR-6">Sanger Institute S. pombe array 1 template 1.2' +
        '<OPTION value="A-SNGR-7">Sanger Institute S. pombe array 2.1.1 template 2.2' +
        '<OPTION value="A-SNGR-8">Sanger Institute S. pombe array 2.2.1 template 3.2' +
        '<OPTION value="A-SNGR-9">Sanger Institute S. pombe array 3.1.1 template 4' +
        '<OPTION value="A-SNGR-10">Sanger Institute S. pombe array 3.1.1 template 4.1' +
        '<OPTION value="A-SNGR-11">Sanger Institute S. pombe array 3.1.1 template 4.2' +
        '<OPTION value="A-SNGR-12">Sanger Institute S. pombe array 3.1.1 template 4.3' +
        '<OPTION value="A-SNGR-13">Sanger Institute S. pombe array 3.1.1 template 5.1' +
        '<OPTION value="A-SNGR-14">Sanger Institute S. pombe array 3.1.1 template 5.2' +
        '<OPTION value="A-SNGR-15">Sanger Institute S. pombe array 3.1.1 template 5.3' +
        '<OPTION value="A-MEXP-528">Sanger Institute S. pombe array 3.1.1 template 5.4' +
        '<OPTION value="A-MEXP-529">Sanger Institute S. pombe array 3.1.1 template 5.5' +
        '<OPTION value="A-MEXP-530">Sanger Institute S. pombe array 3.1.1 template 5.6' +
        '<OPTION value="A-MEXP-531">Sanger Institute S. pombe array 3.1.1 template 5.7' +
        '<OPTION value="A-SNGR-2">Sanger Institute S. pombe array version 2, Pver2.1.1' +
        '<OPTION value="A-SNGR-1">Sanger Institute S. pombe array version 2.2.1' +
        '<OPTION value="A-AFFY-57">Affymetrix GeneChip Wheat Genome Array [wheat]' +
        '<OPTION value="A-AFFY-62">Affymetrix GeneChip Xenopus laevis Genome Array [Xenopus_laevis]' +
        '<OPTION value="A-MEXP-349">Sanger T31 Xenopus tropicalis 6528 v2.1' +
        '<OPTION value="A-AFFY-61">Affymetrix GeneChip ENCODE01 Forward Array' +
        '<OPTION value="A-AFFY-67">Affymetrix GeneChip ENCODE01 Reverse Array' +
        '<OPTION value="A-MEXP-328">CNIO-Agilent_Hs_CLL_1.9K' +
        '<OPTION value="A-TOXM-9">[ILSI] Clontech Atlas Rat Toxicology II [#7732]' +
        '<OPTION value="A-TOXM-7">[ILSI] Incyte Rat GEM 1.04 Microarray' +
        '<OPTION value="A-TOXM-6">[ILSI] Incyte Rat GEM 3.03 Microarray' +
        '<OPTION value="A-MEXP-47">AAT Rat HepatoChip' +
        '<OPTION value="A-AFFY-25">Affymetrix GeneChip Rat Expression Array RAE230A [RAE230A]' +
        '<OPTION value="A-AFFY-26">Affymetrix GeneChip Rat Expression Array RAE230B [RAE230B]' +
        '<OPTION value="A-AFFY-43">Affymetrix GeneChip Rat Genome 230 2.0 [Rat230_2]' +
        '<OPTION value="A-AFFY-18">Affymetrix GeneChip Rat Genome U34A [RG_U34A]' +
        '<OPTION value="A-AFFY-19">Affymetrix GeneChip Rat Genome U34B [RG_U34B]' +
        '<OPTION value="A-AFFY-20">Affymetrix GeneChip Rat Genome U34C [RG_U34C]' +
        '<OPTION value="A-AFFY-22">Affymetrix GeneChip Rat Neurobiology U34 [RN_U34]' +
        '<OPTION value="A-AFFY-21">Affymetrix GeneChip Rat Toxicology U34 [RT_U34]' +
        '<OPTION value="A-AGIL-6">Agilent  Rat Oligo Microarray [G4130A]' +
        '<OPTION value="A-MEXP-338">Agilent Rat Oligo Microarray G4130A non-Agilent scanner' +
        '<OPTION value="A-MEXP-124">Amersham CodeLink UniSet Rat I Bioarray' +
        '<OPTION value="A-MEXP-22">Incyte RatGEM 1.01' +
        '<OPTION value="A-MEXP-11">Incyte RatGEM 1.04' +
        '<OPTION value="A-MEXP-18">Incyte RatGEM 1.05' +
        '<OPTION value="A-AFFY-47">Affymetrix GeneChip Yeast Genome 2.0 Array [Yeast_2]' +
        '<OPTION value="A-AFFY-27">Affymetrix GeneChip Yeast Genome S98 [YG_S98]' +
        '<OPTION value="other">Other' +
         '</select>';
}

function fileTableLine2(id) {
   return '<table width=100% id="channels'+id+'">' +
         '<tr><th bgcolor="pink" width=25%>CY5 sample</th>' +
            '<th bgcolor="lightgreen" width=25%>CY3 sample</th>' +
            '<th bgcolor="deepskyblue" width=25% style="display: none">Blue sample</th>' +
            '<th bgcolor="#FFFF60" width=25% style="display: none">Yellow sample</th>' +
         '</tr><tr>' +
            '<td align=center bgcolor="pink" width=25%>' +
            '<select name="pinkSample'+id+'">' +
            '<option value="" selected>' +
            <!--__EXISTING_SAMPLES__-->
            '</td>' +
            '<td align=center bgcolor="lightgreen" width=25%>' +
            '<select name="greenSample'+id+'">' +
            '<option value="" selected>' +
            <!--__EXISTING_SAMPLES__-->
            '</td>' +
            '<td align=center bgcolor="deepskyblue" width=25% style="display: none">' +
            '<select name="blueSample'+id+'">' +
            '<option value="" selected>' +
            <!--__EXISTING_SAMPLES__-->
            '</td>' +
            '<td align=center bgcolor="#FFFF60" width=25% style="display: none">' +
            '<select name="yellowSample'+id+'">' +
            '<option value="" selected>' +
            <!--__EXISTING_SAMPLES__-->
            '</td>' +
         '</tr>' +
      '</table>';
}

function fileTableLine3(id) {
   return '<INPUT TYPE="file" NAME="external_filename'+id+'" SIZE=80>' + 
          '&nbsp; File Type: ' +
          '<select name = "IMPORT_TYPE'+id+'" SIZE=1 >' +
            '<option value="DNASEQUENCE_MICROARRAY_GPR" SELECTED>GenePix GPR file' +
            '<option value="DNASEQUENCE_MICROARRAY_CHP">Affymetrix CHP file' +
         '</select><br>' +
         '<i align=right style="font-size: 80%">(if other file type, <a href="mailto:alan.mcculloch@agresearch.co.nz;jason.mitchell@agresearch.co.nz?subject=New Microarray Format">please email us</a> full details of format)&nbsp;</i>';

}

function fileTableLine4(id) {
   return '<input name="checkSum'+id+'" SIZE=16 type="text" value=""> ' +
      '<select name="checkSumType'+id+'" size="1">' +
      '<option value="F2_Mean_minus_B2">  F532 Mean - B532 (one of the last columns in GPR file)' +
      '</select>' +
      '<br><i style="font-size: 80%"> (This will be used to check that the database receives all of your results correctly.' +
      'You can calculate it simply by summing all the ch1/ch2 ratio values in your data, in Excel) </i>';
}

function fileTableLine5(id) {
   return '<table class=plainTable id="Inner_table'+id+'">' +
         '<tr><td>' +
            addImageField(id, 0) +
         '</td></tr>' +
       '</table> <button type=button onClick="addImage('+id+')" title="This will add more fields for uploading additional files">Add another file</button>';
}

function fileTableLine6(id) {
   return '<textarea name="experiment_description'+id+'" title="Please enter a description here" type="textarea" rows="4" cols="72">(Please enter a description here)</textarea>';
}


var file_count = 1;
var other_file_count = new Array();
other_file_count[0] = 1;

function addFileBlock() {
   var newInput = document.createElement("input");
   newInput.name = "otherFileCount" + file_count;
   newInput.id = "otherFileCount" + file_count;
   newInput.type = "HIDDEN";
   newInput.value = "1";
   other_file_count[file_count] = 1;
   
   document.arrayform.appendChild(newInput);
   
   var outerTable = document.getElementById('Outer_table');
   var outerRow = outerTable.rows[8];
   var outerCell = outerRow.cells[0];
   
   var table = document.createElement("table");
      table.id = "File_table" + (file_count);
      table.width = "98%";
      table.align = "center";
   outerCell.appendChild(table);
   outerCell.appendChild(document.createElement("br"));
   var row = table.insertRow(table.rows.length);
      var cell = row.insertCell(0);
      cell.vAlign="top";
      cell.innerHTML = '<p><b>Type of Microarray:</b>';
      cell = row.insertCell(1);
      cell.vAlign="top";
      cell.innerHTML = fileTableLine1(file_count);
   row = table.insertRow(table.rows.length);
      cell = row.insertCell(0);
      cell.vAlign="top";
      cell.colSpan = "2";
      cell.innerHTML = fileTableLine2(file_count);
   row = table.insertRow(table.rows.length);
      cell = row.insertCell(0);
      cell.vAlign="top";
      cell.innerHTML = '<p><b>Results File:</b>';
      cell.width = "21%";
      cell = row.insertCell(1);
      cell.vAlign="top";
      cell.innerHTML = fileTableLine3(file_count);
   row = table.insertRow(table.rows.length);
      cell = row.insertCell(0);
      cell.vAlign="top";
      cell.innerHTML = '<p><b>Checksum:</b>';
      cell = row.insertCell(1);
      cell.vAlign="top";
      cell.innerHTML = fileTableLine4(file_count);
   row = table.insertRow(table.rows.length);
      cell = row.insertCell(0);
      cell.vAlign="top";
      cell.innerHTML = '<p><b>Other File(s):</b>';
      cell = row.insertCell(1);
      cell.vAlign="top";
      cell.innerHTML = fileTableLine5(file_count);
   row = table.insertRow(table.rows.length);
      cell = row.insertCell(0);
      cell.vAlign="top";
      cell.innerHTML = '<p><b>Description of this experiment:</b>';
      cell = row.insertCell(1);
      cell.vAlign="top";
      cell.innerHTML = fileTableLine6(file_count);
   file_count++;
   document.arrayform.fileCount.value = file_count;
}

function setChannelNumber(comboValue, tableID) {
   var val = comboValue;
   var table = document.getElementById(tableID);
   
   if (val == 1) { //1-channel array
      var row = table.rows[0];
      var col = row.cells[1];
      col.style.display = "none";
      col = row.cells[2];
      col.style.display = "none";
      col = row.cells[3];
      col.style.display = "none";
      row = table.rows[1];
      col = row.cells[1];
      col.style.display = "none";
      col = row.cells[2];
      col.style.display = "none";
      col = row.cells[3];
      col.style.display = "none";
   }
   else if (val == 2) { //2-channel array
      var row = table.rows[0];
      var col = row.cells[1];
      col.style.display = "";
      col = row.cells[2];
      col.style.display = "none";
      col = row.cells[3];
      col.style.display = "none";
      row = table.rows[1];
      col = row.cells[1];
      col.style.display = "";
      col = row.cells[2];
      col.style.display = "none";
      col = row.cells[3];
      col.style.display = "none";
   }
   else if (val == 4) { //4-channel array
      var row = table.rows[0];
      var col = row.cells[1];
      col.style.display = "";
      col = row.cells[2];
      col.style.display = "";
      col = row.cells[3];
      col.style.display = "";
      row = table.rows[1];
      col = row.cells[1];
      col.style.display = "";
      col = row.cells[2];
      col.style.display = "";
      col = row.cells[3];
      col.style.display = "";
   }
}

function goToPage(pageName) {
   return location.href="form.py?formname=" + pageName;
}

function addImageField(outer_id, inner_id) {
   return '<INPUT TYPE="file" NAME="file' + outer_id + '_' + inner_id + '" SIZE=80>' + 
'            &nbsp;File Type:' +
'            <select name="fileType' + outer_id + '_' + inner_id + '">' +
'            <option value="" selected>' +
'            <optGroup label="Image Files">' +
'            <option value="RedImage">Red Image' +
'            <option value="GreenImage">Green Image' +
'            <option value="CombinedImage">Combined Image' +
'            <option value="OtherImage">Other Image File' +
'            <optGroup label="Other Files">' +
'            <option value="exp">Experimental Data\n' +
'            <option value="meta">Metadata\n' +
'            <option value="derived">Derived Data\n' +
'            <option value="docs">Documents\n' +
'            <option value="Other">Other\n';
}

function addImage(id) {
   var table = document.getElementById("Inner_table" + id);
   var row = table.insertRow(table.rows.length);
   var cell = row.insertCell(0);
   cell.vAlign="top";
   cell.innerHTML = addImageField(id, other_file_count[id]);
   other_file_count[id]++;
   var newInput = document.getElementById("otherFileCount" + id);
   newInput.value = other_file_count[id];
}

function checkMeta(box) {
   if (box.value == "meta") {
      response = window.confirm("This option will not upload any of the files, only information about them. Are you sure you want to do this?");
      if (response == false) {
         box.selectedIndex = '0';
      }
   }
}

var folderArray = new Array();
folderArray[""] = ["New Experiment"];
folderArray["Other"] = ["New Experiment"];
<!--__Array_Entries__-->

function updateFolder(selectObj) {
   var idx = selectObj.selectedIndex;
   var foldr = selectObj.options[idx].value;
   var list = folderArray[foldr];
   var box = document.forms[0].expName;
   while (box.length > 0) {
      box.remove(0);
   }
   
   for (i = -1; i < list.length; i++) {
         newOpt = document.createElement("option");
      if (i == -1) {
         newOpt.text = '';
         newOpt.value = '';
         newOpt.selected = true;
      } else {
         newOpt.text = list[i];
         newOpt.value = list[i];
      }
      var browserName = navigator.appName;
      if (browserName == "Netscape" || browserName == "Opera") { 
         box.add(newOpt, null);
      }
      else if (browserName=="Microsoft Internet Explorer") {
         box.add(newOpt);
      }
   }
}


</script>
</head><body>
<FORM name="arrayform" onSubmit="return checkAll();" METHOD="POST" ENCTYPE="multipart/form-data" ACTION="/cgi-bin/agbrdf/form.py">
<input type="HIDDEN" name="formname" value="microarrayFileForm"/>
<input type="HIDDEN" name="sessionid" value="0"/>
<input type="HIDDEN" name="fileCount" value="1"/>
<input type="HIDDEN" id="otherFileCount0" name="otherFileCount0" value="1"/>
<table border="true" id="Top_table" width=100%>
   <tr> 
      <td colspan="2"> 
         <h1 class="top">AgResearch Microarray Upload Form</h1>
      </td>
   </tr>
   <tr> 
      <td colspan="2"> 
         <table align=center class=plainTable style="border-width: 0">
            <tr align=center valign=middle>
               <td class=color1 title="Define one or more protocols if required" onclick="goToPage('MicroarrayForm1.htm');">
                  <img src="/images/protocol.gif" border="0" height="42" width="42"/>
                  <br>Protocol
               </td>
               <td class=arrow>
                  &rarr;
               </td>
               <td class=color2 title="Define one or more experimental subjects if required" onclick="goToPage('MicroarrayForm2.htm');">
                  <img src="/images/sheep.gif" border="0" height="42" width="42"/>
                  <br>Subject
               </td>
               <td class=arrow>
                  &rarr;
               </td>
               <td class=color3 title="Define one or more samples if required" onclick="goToPage('MicroarrayForm3.htm');">
                  <img src="/images/eppendorf.gif" border="0" height="42" width="42"/>
                  <br>Sample
               </td>
               <td class=arrow>
                  &rarr;
               </td>
               <td class=color0 title="Submit Files">
                  <img src="/images/microarray.jpg" border="0" height="42" width="42"/>
                  <br>Files
               </td>
               <td class=arrow>
                  &rarr;
               </td>
               <td class=color5 title="Define Series" onclick="goToPage('MicroarrayForm5.htm');">
                  <img src="/images/series.gif" border="0" height="42" width="42"/>
                  <br>Series
               </td>
               <td class=arrow>
                  &rarr;
               </td>
               <td class=color6 title="Define contrasts" onclick="goToPage('MicroarrayForm6.htm');">
                  <img src="/images/contrast.gif" border="0" height="42" width="42"/>
                  <br>Contrasts
               </td>
               <td class=arrow>
                  &rarr;
               </td>
               <td class=color7 title="Submit related documents (if any)" onclick="goToPage('MicroarrayForm7.htm');">
                  <img src="/images/documents.gif" border="0" height="42" width="42"/>
                  <br>Documents
               </td>
            </tr>
         </table>
      </td>
   </tr>
</table>

<br>

<table border="true" id="Outer_table" width=100%>
   <tr>
      <td colspan=2 >
         <div style="text-align: center; font-size: 150%; font-weight: bold; line-height: 2">Microarray</div>
         <div style="text-align: left; font-size: 90%; font-weight: normal;">
            Upload data-files and related image-files using this form</div>
      </td>
   </tr>
   
   <tr>
      <td class="fieldname" width=17%>
         <p class="fieldname"><b>Your name:</b>
      </td>
      <td class="input" width=83%>
          <input name="submittedby" value="__submitted_by__" size="50" type="text"/>
      </td>
   </tr>
   <tr>
      <td class="fieldname">
         <p class="fieldname"><b>Your email address:</b>
      </td>
      <td class="input">
          <input name="emailaddress" value="__submitter_email_address__" size="50" type="text"/>
      </td>
   </tr>    
   <tr>
      <td class="fieldname">
         <p class="fieldname"><b>Project ID:</b>
      </td>
      <td class="input">
         <select name="projectID" onchange="updateFolder(this)">
            <option value="" selected>
             <!--__EXISTING_PROJECTS__-->
             <option value="Other">Other
         </select>
         &nbsp;&nbsp; Other project (not in list): 
         <input name="otherProject" value="" size="40"/>
      </td>
   </tr>    
   <tr>
      <td class="fieldname">
         <p class="fieldname"><b>Sub-Program:</b>
      </td>
      <td class="input">
         <SELECT name="subProgram">
            <OPTION value="" selected>
            <OPTION value="Coretech">Coretech
            <OPTION value="Muscle">Muscle
            <OPTION value="Parasite">Parasite
            <OPTION value="Wool">Wool
            <OPTION value="Reproduction">Reproduction
         </SELECT>
      </td>
   </tr>
   <tr>   
      <td class="fieldname"> 
         <p class="fieldname"><b>Purpose of submitting data</b>
      </td>
      <td class="input">
         <SELECT name="reason" onchange="checkMeta(this)">
            <OPTION value="" selected>Please select an option:
            <OPTION value="colleague">pass on data to colleague
            <OPTION value="archive">archive files on server
            <OPTION value="import">data to be imported into database
            <OPTION value="meta">record only file meta-data (i.e. don't upload the actual file)
         </SELECT>
       </td>
   </tr>
   <tr>
      <td class="fieldname">
         <p class="fieldname"><b>Experiment Name:</b>
      </td>
      <td class="input">
         <SELECT name="expName">
            <OPTION value="" selected>
            <!--__EXISTING_EXPERIMENT__-->
            <OPTION value="New Experiment">New Experiment
         </SELECT><br>
         New Name (if not in list): 
         <input name="otherExp" value="" size="115"/>
      </td>
   </tr>



   <tr>
      <td colspan=2>
         <span style="font-size: 150%; font-weight: bold; line-height: 2">Microarray File Details:</span>
      </td>
   </tr>
   
   <tr>
      <td colspan=2>
         <p align=right><button type="button" id="addButton" onclick="addFileBlock();" 
         title="This will add another set of fields to the bottom of the page">Add another microarray file</button> </p>
         <table align=center width=98% id='File_table0'>
        <tr><td><p><b>Type of Microarray:</b></td>
            <td><script>document.write(fileTableLine1('0'));</script></td></tr>
        <tr><td colspan=2><script>document.write(fileTableLine2('0'));</script></td></tr>       
        <tr><td width=21%><p><b>Results File:</b></td>
            <td><script>document.write(fileTableLine3('0'));</script></td></tr>
        <tr><td><p><b>Checksum:</b></td>
            <td><script>document.write(fileTableLine4('0'));</script></td></tr>
        <tr><td><p><b>Other File(s):</b></td>
            <td><script>document.write(fileTableLine5('0'));</script></td></tr>
        <tr><td><p><b>Description of this experiment:</b></td>
            <td><script>document.write(fileTableLine6('0'));</script></td></tr>
         </table>
         <br>
      </td>
   </tr>
   


<tr><td colspan=2>
<P>
<i>
Please <a href="mailto:alan.mcculloch@agresearch.co.nz;jason.mitchell@agresearch.co.nz?subject=Microarray Suggestion">
email us</a> with any suggestions for improvements to this form.
</i>

</td></tr>
   <tr>
      <td colspan=2 align=center>
         <p><input id="submitButton" type="submit" value="Submit Experiment">
      </td>
   </tr>
</table>
</FORM>
</body>
</html>
"""

form_microarraySeriesForm = r"""
<html>
<head>
<title>AgResearch - Microarray Upload Form</title>
<style>
body        {margin-top: 1cm ; margin-bottom: 1cm; margin-left: 5%; margin-right: 5%; 
        font-family: arial, helvetica, geneva, sans-serif;BACKGROUND: #f0f9ff}

p        {margin-top: .3cm ; margin-bottom: .3cm; margin-left: .4cm; margin-right: .4cm; 
        font-family: arial, helvetica, geneva, sans-serif}
p.fieldname     {margin-top: .3cm ; margin-bottom: .3cm; margin-left: .4cm; margin-right: .4cm; 
        font-family: arial, helvetica, geneva, sans-serif}
p.footer    {text-align: center ; margin-top: 0.5cm ; margin-bottom: 0.5cm; font-family: arial, helvetica, geneva, sans-serif}

b.b        {font-family: arial, helvetica, geneva, sans-serif; font-weight: 700; color: #424b50}
ul        {font-family: arial, helvetica, geneva, sans-serif}
ol        {font-family: arial, helvetica, geneva, sans-serif}
dl        {font-family: arial, helvetica, geneva, sans-serif}

th              {font-family: arial, helvetica, geneva, sans-serif; font-weight: 400}

h1        {text-align: center; color: #388fbd; 
        font-family: arial, helvetica, geneva, sans-serif}
h1.new          {text-align: center; color: #4d585e;
                font-family: arial, helvetica, geneva, sans-serif}
h1.b1           {margin-top: 0.5cm; text-align: center; color:#2d59b2;
                font-family: arial, helvetica, geneva, sans-serif}
h1.b2           {margin-top: 0.5cm; text-align: center; color:#1d7db5;
                font-family: arial, helvetica, geneva, sans-serif}
h1.top        {margin-top: 0.5cm; text-align: center; color: blue;
        font-family: arial, helvetica, geneva, sans-serif}

h2        {text-align: center; font-family: arial, helvetica, geneva, sans-serif}
h3        {font-family: arial, helvetica, geneva, sans-serif}
h4        {font-family: arial, helvetica, geneva, sans-serif}
h5        {font-family: arial, helvetica, geneva, sans-serif}
h6        {font-family: arial, helvetica, geneva, sans-serif}
a         {font-family: arial, helvetica, geneva, sans-serif}

table       {background-color: antiquewhite}

input.detail       {margin-left: 1cm}

textarea.detail    {margin-left: 1cm}

td        {font-family: arial, helvetica, geneva, sans-serif}
td.fieldname    {font-family: arial, helvetica, geneva, sans-serif}

tr          {background-color: #92E7FF}
.plainTable        {background-color: #92E7FF}
a:hover     {color: blue; text-decoration: underline }

.color0          {border: solid black; border-width: 5px; width: 80px; height: 80px}
.color1          {background-color: #FF9292; border: solid black; border-width: 1px; cursor: pointer; width: 88px; height: 88px}
.color2          {background-color: #FFDA92; border: solid black; border-width: 1px; cursor: pointer; width: 88px; height: 88px}
.color3          {background-color: #FFFF92; border: solid black; border-width: 1px; cursor: pointer; width: 88px; height: 88px}
.color4          {background-color: #B1FF92; border: solid black; border-width: 1px; cursor: pointer; width: 88px; height: 88px}
.color5          {background-color: #92E7FF; border: solid black; border-width: 1px; cursor: pointer; width: 88px; height: 88px}
.color6          {background-color: #9C92FF; border: solid black; border-width: 1px; cursor: pointer; width: 88px; height: 88px}
.color7          {background-color: #F392FF; border: solid black; border-width: 1px; cursor: pointer; width: 88px; height: 88px}

.arrow           {font-size: 200%; width: 40px}
</style>
<script language="JavaScript">

var alreadySubmitted = false;

function checkAll() {
   // make sure we have not already submitted this form
   if(alreadySubmitted) {
      window.alert("This Form has already been submitted, please wait");
      return false;
   }

   // check the series name fields are entered correctly
   var serN = document.arrayform.seriesName;
   var oSer = document.arrayform.otherSeries;
   if(serN.value == "" && trim(oSer.value) == "") {
      lowLight(oSer);
      highLight(serN,"Please select a series name. If your want to create a new name, " +
      "select \"New Series\" and enter the series name into the \"New Name\" field. After you submit " +
      "the form, this name will be available in the dropdown box in the future.");
      return false;
   } else if (serN.value == "new" && trim(oSer.value) == "") {
      lowLight(serN);
      highLight(oSer,"Please enter the new series name into the \"New Name\" field.");
      return false;
   } else if (serN.value == "" && trim(oSer.value) != "") {
      lowLight(oSer);
      highLight(serN,"Please select \"New Series\" from the dropdown box.");
      return false;
   } else if (serN.value != "new" && trim(oSer.value) != "") {
      lowLight(serN);
      highLight(oSer,"Please remove the value from the \"New Series\" field.");
      return false;
   } else if (trim(oSer.value).match(/[^\w ]/) != null) {
      highLight(oSer,"You may only name your series using the characters " +
               "'A-Z', 'a-z', '0-9' and '_', and spaces.");
      return false;
   } else {
      lowLight(serN);
      lowLight(oSer);
   }
   
   //check that they've entered something into the description field.
   if (document.arrayform.seriesDesc.value == "(Please enter a description here)") {
      highLight(document.arrayform.seriesDesc,"Please enter a description of the Series.");
      return false;
   }else if (document.arrayform.seriesDesc.value .length <= 30) {
      highLight(document.arrayform.seriesDesc,"Please enter a longer description of the Series (i.e. > 30 characters).");
      return false;
   }
   else {
      lowLight(document.arrayform.seriesDesc);
   }
   
   //Check that they've selected a submitter.
   if (document.arrayform.submitter.value == "") {
      highLight(document.arrayform.submitter,"You need to select a submitter - this populates the submission-names box.");
      return false;
   } else {
      lowLight(document.arrayform.submitter);
   }

   //Check that they've selected submissions.
   if (document.arrayform.submissions.value == "" || document.arrayform.submissions.value == "Select a submitter") {
      highLight(document.arrayform.submissions,"You need to select a submission - this populates the file-names box.");
      return false;
   } else {
      lowLight(document.arrayform.submissions);
   }
   
   //Check that they've selected some files.
   if (document.arrayform.files.value == "") {
      highLight(document.arrayform.files,"You need to select a file/files to add to the series.");
      return false;
   } else {
      var box = document.arrayform.files;
      lowLight(box);
      var counter = 0;
      for (i=1; i<box.length; i++) {
         if (box.options[i].selected && box.options[i].value != 'Select a submission') {
            counter++;
         }
      }
      if (counter == 0) {
         highLight(box,'You need to select a file/files for this series!');
         return false;
      } else {
         lowLight(box);
      }
   }
   
   // finally, set the submitted flag
   btn = document.getElementById("submitButton");
   btn.value = "Submitting, please wait...";
   btn.disabled = true;
   
   alreadySubmitted = true;
   return true;
}

function highLight(item,message) {
   item.style.background = 'red';
   window.alert(message);
   item.focus();
} // assume IE

function lowLight(item) {
   item.style.background = '';
}

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

function goToPage(pageName) {
   return location.href="form.py?formname=" + pageName;
}

var subArray = new Array();
subArray[""] = ["Select a submitter"];
<!--__EXISTING_SUBMITTERS_ARRAY__-->

var fileArray = new Array();
fileArray[""] = ["Select a submission"];
<!--__EXISTING_FILE_ARRAY__-->

function setSubmissionNames(userName) {
   var subs = subArray[userName];
   var sub = document.arrayform.submissions;
   var files = document.arrayform.files;
   var res = 1
   if (sub.selectedIndex > 0) {
      res = window.confirm("Are you sure that you want to select a different submitter? " + 
      "Any selected submissions/files will be lost.")
   }
   if (res == 1) {
      while (sub.length > 0) {sub.remove(0);}
      while (files.length > 0) {files.remove(0);}
   
      for (i = 0; i < subs.length; i++) {
         newOpt = document.createElement("option");
//         if (i == -1) {
//            newOpt.text = '';
//            newOpt.value = '';
//            newOpt.selected = true;
//         } else {
            newOpt.text = subs[i];
            newOpt.value = subs[i];
//         }
         var browserName = navigator.appName;
         if (browserName == "Netscape" || browserName == "Opera") { 
            sub.add(newOpt, null);
         } else if (browserName=="Microsoft Internet Explorer") {
            sub.add(newOpt);
         }
      }

      newOpt = document.createElement("option");
      newOpt.text = '';
      newOpt.value = '';
      newOpt.selected = true;
      newOpt2 = document.createElement("option");
      newOpt2.text = 'Select a submission';
      newOpt2.value = 'Select a submission';

      var browserName = navigator.appName;
      if (browserName == "Netscape" || browserName == "Opera") { 
         files.add(newOpt, null);
         files.add(newOpt2, null);
      } else if (browserName=="Microsoft Internet Explorer") {
         files.add(newOpt);
         files.add(newOpt2);
      }  
   }
}

function setFileNames(subName) {
   var subs = fileArray[subName];
   var sub = document.arrayform.files;
   while (sub.length > 0) {
      sub.remove(0);
   }
   
   for (i = 0; i < subs.length; i++) {
         newOpt = document.createElement("option");
//      if (i == -1) {
//         newOpt.text = '';
//         newOpt.value = '';
//         newOpt.selected = true;
//      } else {
         newOpt.text = subs[i];
         newOpt.value = subs[i];
//      }
      var browserName = navigator.appName;
      if (browserName == "Netscape" || browserName == "Opera") { 
         sub.add(newOpt, null);
      } else if (browserName=="Microsoft Internet Explorer") {
         sub.add(newOpt);
      }
   }
}

</script>
</head><body>
<FORM name="arrayform" onSubmit="return checkAll();" METHOD="POST" ENCTYPE="multipart/form-data" ACTION="/cgi-bin/agbrdf/form.py" >
<input type="HIDDEN" name="formname" value="microarraySeriesForm"/>
<input type="HIDDEN" name="sessionid" value="0"/>
   
<table border="true" id="Top_table" width=100%>
   <tr> 
      <td colspan="2"> 
         <h1 class="top">AgResearch Microarray Upload Form</h1>
      </td>
   </tr>
   <tr> 
      <td colspan="2"> 
         <table align=center class=plainTable style="border-width: 0">
            <tr align=center valign=middle>
               <td class=color1 title="Define one or more protocols if required" onclick="goToPage('MicroarrayForm1.htm');">
                  <img src="/images/protocol.gif" border="0" height="42" width="42"/>
                  <br>Protocol
               </td>
               <td class=arrow>
                  &rarr;
               </td>
               <td class=color2 title="Define one or more experimental subjects if required" onclick="goToPage('MicroarrayForm2.htm');">
                  <img src="/images/sheep.gif" border="0" height="42" width="42"/>
                  <br>Subject
               </td>
               <td class=arrow>
                  &rarr;
               </td>
               <td class=color3 title="Define one or more samples if required" onclick="goToPage('MicroarrayForm3.htm');">
                  <img src="/images/eppendorf.gif" border="0" height="42" width="42"/>
                  <br>Sample
               </td>
               <td class=arrow>
                  &rarr;
               </td>
               <td class=color4 title="Submit Files" onclick="goToPage('MicroarrayForm4.htm');">
                  <img src="/images/microarray.jpg" border="0" height="42" width="42"/>
                  <br>Files
               </td>
               <td class=arrow>
                  &rarr;
               </td>
               <td class=color0 title="Define Series">
                  <img src="/images/series.gif" border="0" height="42" width="42"/>
                  <br>Series
               </td>
               <td class=arrow>
                  &rarr;
               </td>
               <td class=color6 title="Define contrasts" onclick="goToPage('MicroarrayForm6.htm');">
                  <img src="/images/contrast.gif" border="0" height="42" width="42"/>
                  <br>Contrasts
               </td>
               <td class=arrow>
                  &rarr;
               </td>
               <td class=color7 title="Submit related documents (if any)" onclick="goToPage('MicroarrayForm7.htm');">
                  <img src="/images/documents.gif" border="0" height="42" width="42"/>
                  <br>Documents
               </td>
            </tr>
         </table>
      </td>
   </tr>
</table>

<br>

<table border="true" id="Outer_table" width=100%>
   <tr>
      <td colspan=2 >
         <div style="text-align: center; font-size: 150%; font-weight: bold; line-height: 2">Series</div>
         <div style="text-align: left; font-size: 90%; font-weight: normal;">
            Group any related submissions or experiments together into a series with this form</div>
      </td>
   </tr>
   
   <tr>
      <td class="fieldname" width=17%>
         <p class="fieldname"><b>Series Name:
      </td>
      <td class="input">
         <SELECT name="seriesName" width=83%>
            <OPTION value="" selected>
            <!--__EXISTING_SERIES__-->
            <OPTION value="new">New Series
         </SELECT><br>
         New Name (if not in list): 
         <input name="otherSeries" value="" size="100"/>
      </td>
   </tr>
   <tr>
      <td>
         <p><b>Series description:</b>
      </td>
      <td>
     <textarea name="seriesDesc" title="Please enter a description here" type="textarea" rows="4" cols="72">(Please enter a description here)</textarea> 
      </td>
   </tr>
   <tr>
      <td class="fieldname" width=17%>
         <p class="fieldname"><b>Submitter's Name:</b>
      </td>
      <td class="input" width=83%>
         <select name="submitter" onChange="setSubmissionNames(this.value)">
            <option value="">
            <!--__EXISTING_SUBMITTERS__-->
         </select>
      </td>
   </tr>    
   <tr>
      <td class="fieldname" width=17%>
         <p class="fieldname"><b>Experiment Names:</b>
      </td>
      <td class="input" width=83%>
         <select name="submissions" onChange="setFileNames(this.value)">
            <option value="" selected>
            <option value="Select a submitter">Select a submitter
         </select>
      </td>
   </tr>    
   <tr>
      <td class="fieldname" width=17%>
         <p class="fieldname"><b>Submission (File) Names:</b>
      </td>
      <td class="input" width=83%>
         <select name="files" multiple>
            <option value="" selected>
            <option value="Select a submission">Select a submission
         </select>
      </td>
   </tr>


<tr><td colspan=2>
<P>
<i>
Please <a href="mailto:alan.mcculloch@agresearch.co.nz;jason.mitchell@agresearch.co.nz?subject=Microarray Suggestion">email us</a> with any suggestions for improvements to this form.
</i>

</td></tr>
   <tr>
      <td colspan=2 align=center>
         <p><input id="submitButton" type="submit" value="Submit Series">
      </td>
   </tr>
</table>
</FORM>
</body>
</html>
"""

form_microarrayContrastForm = r"""
<html>
<head>
<title>AgResearch - Microarray Upload Form</title>
<style>
body        {margin-top: 1cm ; margin-bottom: 1cm; margin-left: 5%; margin-right: 5%; 
        font-family: arial, helvetica, geneva, sans-serif;BACKGROUND: #f0f9ff}

p        {margin-top: .3cm ; margin-bottom: .3cm; margin-left: .4cm; margin-right: .4cm; 
        font-family: arial, helvetica, geneva, sans-serif}
p.fieldname     {margin-top: .3cm ; margin-bottom: .3cm; margin-left: .4cm; margin-right: .4cm; 
        font-family: arial, helvetica, geneva, sans-serif}
p.footer    {text-align: center ; margin-top: 0.5cm ; margin-bottom: 0.5cm; font-family: arial, helvetica, geneva, sans-serif}

b.b        {font-family: arial, helvetica, geneva, sans-serif; font-weight: 700; color: #424b50}
ul        {font-family: arial, helvetica, geneva, sans-serif}
ol        {font-family: arial, helvetica, geneva, sans-serif}
dl        {font-family: arial, helvetica, geneva, sans-serif}

th              {font-family: arial, helvetica, geneva, sans-serif; font-weight: 400}

h1        {text-align: center; color: #388fbd; 
        font-family: arial, helvetica, geneva, sans-serif}
h1.new          {text-align: center; color: #4d585e;
                font-family: arial, helvetica, geneva, sans-serif}
h1.b1           {margin-top: 0.5cm; text-align: center; color:#2d59b2;
                font-family: arial, helvetica, geneva, sans-serif}
h1.b2           {margin-top: 0.5cm; text-align: center; color:#1d7db5;
                font-family: arial, helvetica, geneva, sans-serif}
h1.top        {margin-top: 0.5cm; text-align: center; color: blue;
        font-family: arial, helvetica, geneva, sans-serif}

h2        {text-align: center; font-family: arial, helvetica, geneva, sans-serif}
h3        {font-family: arial, helvetica, geneva, sans-serif}
h4        {font-family: arial, helvetica, geneva, sans-serif}
h5        {font-family: arial, helvetica, geneva, sans-serif}
h6        {font-family: arial, helvetica, geneva, sans-serif}
a         {font-family: arial, helvetica, geneva, sans-serif}

table       {background-color: antiquewhite}

input.detail       {margin-left: 1cm}

textarea.detail    {margin-left: 1cm}

td        {font-family: arial, helvetica, geneva, sans-serif}
td.fieldname    {font-family: arial, helvetica, geneva, sans-serif}

tr          {background-color: #9C92FF}
.plainTable        {background-color: #9C92FF}
a:hover     {color: blue; text-decoration: underline }

.color0          {border: solid black; border-width: 5px; width: 80px; height: 80px}
.color1          {background-color: #FF9292; border: solid black; border-width: 1px; cursor: pointer; width: 88px; height: 88px}
.color2          {background-color: #FFDA92; border: solid black; border-width: 1px; cursor: pointer; width: 88px; height: 88px}
.color3          {background-color: #FFFF92; border: solid black; border-width: 1px; cursor: pointer; width: 88px; height: 88px}
.color4          {background-color: #B1FF92; border: solid black; border-width: 1px; cursor: pointer; width: 88px; height: 88px}
.color5          {background-color: #92E7FF; border: solid black; border-width: 1px; cursor: pointer; width: 88px; height: 88px}
.color6          {background-color: #9C92FF; border: solid black; border-width: 1px; cursor: pointer; width: 88px; height: 88px}
.color7          {background-color: #F392FF; border: solid black; border-width: 1px; cursor: pointer; width: 88px; height: 88px}

.arrow           {font-size: 200%; width: 40px}
</style>
<script language="JavaScript">

var alreadySubmitted = false;

function checkAll() {
   // make sure we have not already submitted this form
   if(alreadySubmitted) {
      window.alert("This Form has already been submitted, please wait");
      return false;
   }

   //Check that if a value is entered into one of the fields in a row, that they're all entered.
   for (i=0; i<statement_count; i++) {
      var sub1 = eval("document.arrayform.submission"+i+"_1");
      var sub2 = eval("document.arrayform.submission"+i+"_2");
      var fil1 = eval("document.arrayform.file"+i+"_1");
      var fil2 = eval("document.arrayform.file"+i+"_2");
      var con = eval("document.arrayform.contrast"+i);
      lowLight(sub1);
      lowLight(sub2);
      lowLight(fil1);
      lowLight(fil2);
      lowLight(con);
      if (sub1.value == "" && sub2.value == "" && con.value == "") {
         if (i == 0) {
            highLight(sub1,"If submitting a contrast, you must use the first set of fields.");
            return false;
         }
      }
      else if (sub1.value == "") {
         highLight(sub1,"You must select a submission folder.");
         return false;
      }
      else if (fil1.value == "" || fil1.value == "Select an experiment") {
         highLight(fil1,"You must select a submission file.");
         return false;
      }
      else if (con.value == "") {
         highLight(con,"You must select a type of contrast.");
         return false;
      }
      else if (sub2.value == "") {
         highLight(sub2,"You must select a submission folder.");
         return false;
      }
      else if (fil2.value == "" || fil2.value == "Select an experiment") {
         highLight(fil2,"You must select a submission file.");
         return false;
      }
      else if (sub1.value == sub2.value && fil1.value == fil2.value) {
         highLight(fil2,"You must select two different submissions.");
         return false;
      }
   }
   
   // finally, set the submitted flag
   btn = document.getElementById("submitButton");
   btn.value = "Submitting, please wait...";
   btn.disabled = true;
   
   alreadySubmitted = true;
   return true;
}

function highLight(item,message) {
   item.style.background = 'red';
   window.alert(message);
   item.focus();
} // assume IE

function lowLight(item) {
   item.style.background = '';
}

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

function goToPage(pageName) {
   return location.href="form.py?formname=" + pageName;
}

var fileArray = new Array();
fileArray[""] = ["Select an experiment"];
<!--__EXISTING_FILE_ARRAY__-->

function setFileNames(subName, id, fieldNum) {
   var subs = fileArray[subName];
   var sub = eval('document.arrayform.file'+id+'_'+fieldNum);
   while (sub.length > 0) {
      sub.remove(0);
   }
   
   for (i = 0; i < subs.length; i++) {
         newOpt = document.createElement("option");
         newOpt.text = subs[i];
         newOpt.value = subs[i];
      var browserName = navigator.appName;
      if (browserName == "Netscape" || browserName == "Opera") { 
         sub.add(newOpt, null);
      } else if (browserName=="Microsoft Internet Explorer") {
         sub.add(newOpt);
      }
   }
}

function addSubField(id, fieldNum) {
   return '<select name="submission' + id + '_' + fieldNum + '" onChange="setFileNames(this.value,'+id+','+fieldNum+')">' +
'            <option value="" selected>' +
<!--__EXISTING_SUBMISSIONS__-->
'         </select>';
}

function addFileField(id, fieldNum) {
   return '<select name="file' + id + '_' + fieldNum + '">' +
'            <option value="Select an experiment">Select an experiment' +
'         </select>';
}

var contrastFields1 = '<select name="contrast';
var contrastFields2 = '">' +
'            <option value="" selected>' +
'            <option value="Dye-swap">Dye-swap' +
'            <option value="High-res Scan">High-res Scan' +
<!--__EXISTING_CONTRASTS__-->
'         </select>';

function addContrastField(id) {
   return contrastFields1+id+contrastFields2;
}

function addNewContrast() {
   var fail = "False";
   var box = eval("document.arrayform.contrast0");
   var newContrast = trim(window.prompt("Please enter the new contrast:", ""));
   if (newContrast != null && newContrast != '') {
      for (j=0; j<box.length; j++) {
         testStr = trim(box.options[j].text);
         if (testStr.toLowerCase() == newContrast.toLowerCase()){
            fail = "True";
            break;
         }
      }
      if (fail == "True") {
         window.alert("The Attribute '" + newContrast + "' is already entered");
      } else {
         for (i=0; i<statement_count; i++) {
            box = eval("document.arrayform.contrast"+i);
            var newOpt = document.createElement("option");
            newOpt.text = newContrast;
            newOpt.value = newContrast;
            
            var browserName = navigator.appName;
            if (browserName == "Netscape" || browserName == "Opera") { 
               box.add(newOpt, null);
               box.options[box.length-1].selected = "True";
            } 
            else if (browserName=="Microsoft Internet Explorer") {
               box.add(newOpt);
               box.options[box.length-1].selected = "True";
            }
         }
         //Also need to add the value to the string which is used to populate new "attribute name" combo boxes.
         contrastFields2 = contrastFields2.replace(/<\/select>/g, "<option>"+newContrast+"<\/option></select>");
      }
   }
}

var statement_count = 1;

function setFileCount(count){
   var field = document.arrayform.fileCount;
   field.setAttribute("value", count);
}

function addStatement() {
   var table = document.getElementById("Inner_table");
   var row = table.insertRow(table.rows.length);
   var cell = row.insertCell(0);
   cell.innerHTML = '&nbsp;';
   row = table.insertRow(table.rows.length);
   cell = row.insertCell(0);
   cell.vAlign="top";
   cell.innerHTML = addSubField(statement_count,'1') + ' ' + addFileField(statement_count,'1');
   row = table.insertRow(table.rows.length);
   cell = row.insertCell(0);
   cell.vAlign="top";
   cell.innerHTML = ' &nbsp; is a &nbsp;' + addContrastField(statement_count) + ' &nbsp; of &nbsp; ';
   row = table.insertRow(table.rows.length);
   cell = row.insertCell(0);
   cell.vAlign="top";
   cell.innerHTML = addSubField(statement_count,'2') + ' ' + addFileField(statement_count,'2');
   statement_count++;
   setFileCount(statement_count);
}

</script>
</head><body>
<FORM name="arrayform" onSubmit="return checkAll();" METHOD="POST" ENCTYPE="multipart/form-data" ACTION="/cgi-bin/agbrdf/form.py" >
<input type="HIDDEN" name="formname" value="microarrayContrastForm"/>
<input type="HIDDEN" name="sessionid" value="0"/>
<input type="HIDDEN" name="fileCount" value="1"/>
   
<table border="true" id="Top_table" width=100%>
   <tr> 
      <td colspan="2"> 
         <h1 class="top">AgResearch Microarray Upload Form</h1>
      </td>
   </tr>
   <tr> 
      <td colspan="2"> 
         <table align=center class=plainTable style="border-width: 0">
            <tr align=center valign=middle>
               <td class=color1 title="Define one or more protocols if required" onclick="goToPage('MicroarrayForm1.htm');">
                  <img src="/images/protocol.gif" border="0" height="42" width="42"/>
                  <br>Protocol
               </td>
               <td class=arrow>
                  &rarr;
               </td>
               <td class=color2 title="Define one or more experimental subjects if required" onclick="goToPage('MicroarrayForm2.htm');">
                  <img src="/images/sheep.gif" border="0" height="42" width="42"/>
                  <br>Subject
               </td>
               <td class=arrow>
                  &rarr;
               </td>
               <td class=color3 title="Define one or more samples if required" onclick="goToPage('MicroarrayForm3.htm');">
                  <img src="/images/eppendorf.gif" border="0" height="42" width="42"/>
                  <br>Sample
               </td>
               <td class=arrow>
                  &rarr;
               </td>
               <td class=color4 title="Submit Files" onclick="goToPage('MicroarrayForm4.htm');">
                  <img src="/images/microarray.jpg" border="0" height="42" width="42"/>
                  <br>Files
               </td>
               <td class=arrow>
                  &rarr;
               </td>
               <td class=color5 title="Define Series" onclick="goToPage('MicroarrayForm5.htm');">
                  <img src="/images/series.gif" border="0" height="42" width="42"/>
                  <br>Series
               </td>
               <td class=arrow>
                  &rarr;
               </td>
               <td class=color0 title="Define contrasts">
                  <img src="/images/contrast.gif" border="0" height="42" width="42"/>
                  <br>Contrasts
               </td>
               <td class=arrow>
                  &rarr;
               </td>
               <td class=color7 title="Submit related documents (if any)" onclick="goToPage('MicroarrayForm7.htm');">
                  <img src="/images/documents.gif" border="0" height="42" width="42"/>
                  <br>Documents
               </td>
            </tr>
         </table>
      </td>
   </tr>
</table>

<br>

<table border="true" id="Outer_table" width=100%>
   <tr>
      <td colspan="2">
         <div style="text-align: center; font-size: 150%; font-weight: bold; line-height: 2">Contrasts</div>
         <div style="text-align: left; font-size: 90%; font-weight: normal;">
            Use this form to capture relationships between slides, e.g. slide A is a dye-swap of slide B etc</div>
      </td>
   </tr>
   
   <tr>
      <td class="fieldname" width=23%>
         <p class="fieldname"><b>Specify contrast statements:</b>
      </td><td>
         <table class=plainTable id="Inner_table">
            <tr><td>
               <script>document.write(addSubField('0','1'));</script>
               <script>document.write(addFileField('0','1'));</script>
            </td></tr>
            <tr><td>
               &nbsp; is a &nbsp;
               <script>document.write(addContrastField('0'));</script>
               &nbsp; of &nbsp;
            </td></tr>
            <tr><td>
               <script>document.write(addSubField('0','2'));</script>
               <script>document.write(addFileField('0','2'));</script>
            </td></tr>
         </table>
         <button type=button onClick="addStatement()">Add another statement</button> &nbsp; 
         <button type=button onClick="addNewContrast()">Add another contrast type</button>
      </td>
   </tr>    

<tr><td colspan="2">
<P>
<i>
Please <a href="mailto:alan.mcculloch@agresearch.co.nz;jason.mitchell@agresearch.co.nz?subject=Microarray Suggestion">email us</a> with any suggestions for improvements to this form.
</i>

</td></tr>
   <tr>
      <td align=center colspan="2">
         <p><input id="submitButton" type="submit" value="Submit Contrast(s)">
      </td>
   </tr>
</table>
</FORM>
</body>
</html>"""

form_microarrayDocumentForm = r"""
<html>
<head>
<title>AgResearch - Microarray Upload Form</title>
<style>
body        {margin-top: 1cm ; margin-bottom: 1cm; margin-left: 5%; margin-right: 5%; 
        font-family: arial, helvetica, geneva, sans-serif;BACKGROUND: #f0f9ff}

p        {margin-top: .3cm ; margin-bottom: .3cm; margin-left: .4cm; margin-right: .4cm; 
        font-family: arial, helvetica, geneva, sans-serif}
p.fieldname     {margin-top: .3cm ; margin-bottom: .3cm; margin-left: .4cm; margin-right: .4cm; 
        font-family: arial, helvetica, geneva, sans-serif}
p.footer    {text-align: center ; margin-top: 0.5cm ; margin-bottom: 0.5cm; font-family: arial, helvetica, geneva, sans-serif}

b.b        {font-family: arial, helvetica, geneva, sans-serif; font-weight: 700; color: #424b50}
ul        {font-family: arial, helvetica, geneva, sans-serif}
ol        {font-family: arial, helvetica, geneva, sans-serif}
dl        {font-family: arial, helvetica, geneva, sans-serif}

th              {font-family: arial, helvetica, geneva, sans-serif; font-weight: 400}

h1        {text-align: center; color: #388fbd; 
        font-family: arial, helvetica, geneva, sans-serif}
h1.new          {text-align: center; color: #4d585e;
                font-family: arial, helvetica, geneva, sans-serif}
h1.b1           {margin-top: 0.5cm; text-align: center; color:#2d59b2;
                font-family: arial, helvetica, geneva, sans-serif}
h1.b2           {margin-top: 0.5cm; text-align: center; color:#1d7db5;
                font-family: arial, helvetica, geneva, sans-serif}
h1.top        {margin-top: 0.5cm; text-align: center; color: blue;
        font-family: arial, helvetica, geneva, sans-serif}

h2        {text-align: center; font-family: arial, helvetica, geneva, sans-serif}
h3        {font-family: arial, helvetica, geneva, sans-serif}
h4        {font-family: arial, helvetica, geneva, sans-serif}
h5        {font-family: arial, helvetica, geneva, sans-serif}
h6        {font-family: arial, helvetica, geneva, sans-serif}
a         {font-family: arial, helvetica, geneva, sans-serif}

table       {background-color: antiquewhite}

input.detail       {margin-left: 1cm}

textarea.detail    {margin-left: 1cm}

td        {font-family: arial, helvetica, geneva, sans-serif}
td.fieldname    {font-family: arial, helvetica, geneva, sans-serif}

tr          {background-color: #F392FF}
.plainTable        {background-color: #F392FF}
a:hover     {color: blue; text-decoration: underline }

.color0          {border: solid black; border-width: 5px; width: 80px; height: 80px}
.color1          {background-color: #FF9292; border: solid black; border-width: 1px; cursor: pointer; width: 88px; height: 88px}
.color2          {background-color: #FFDA92; border: solid black; border-width: 1px; cursor: pointer; width: 88px; height: 88px}
.color3          {background-color: #FFFF92; border: solid black; border-width: 1px; cursor: pointer; width: 88px; height: 88px}
.color4          {background-color: #B1FF92; border: solid black; border-width: 1px; cursor: pointer; width: 88px; height: 88px}
.color5          {background-color: #92E7FF; border: solid black; border-width: 1px; cursor: pointer; width: 88px; height: 88px}
.color6          {background-color: #9C92FF; border: solid black; border-width: 1px; cursor: pointer; width: 88px; height: 88px}
.color7          {background-color: #F392FF; border: solid black; border-width: 1px; cursor: pointer; width: 88px; height: 88px}

.arrow           {font-size: 200%; width: 40px}
</style>
<script language="JavaScript">

var alreadySubmitted = false;

function checkAll() {
   // make sure we have not already submitted this form
   if(alreadySubmitted) {
      window.alert("This Form has already been submitted, please wait");
      return false;
   }
   var ser = document.arrayform.series;
   var sub = document.arrayform.submissions;
   var fil = document.arrayform.file;
   lowLight(ser);
   lowLight(sub);
   lowLight(fil);
   
   // check they've selected one of the series or the submissions, and a file
   if (sub.value == '' && ser.value == '') {
      highLight(ser,"You must select a submission or series to link the file to.");
      return false;
   } else if (sub.value != '' && ser.value != '') { //Should never happen...
      highLight(ser,"You must select either a submission or a series to link the file to " + 
                "- you cannot link both at the same time.");
      return false;
   } else if (sub.value != '' && fil.value == '') {
      highLight(fil,"You must select a file from this submission folder to link the file to.");
      return false;
   } else {
      for (var i=0; i<file_count; i++) {
         file = eval("document.arrayform.fileList"+(i+1));
         fold = eval("document.arrayform.submissions"+(i+1));
         if (fold.value != '' && file.value == '') {
            highLight(file,"You must select a file to link to the series or submission.");
            return false;
         } else {
            lowLight(file);
         }
      }
   }

   // finally, set the submitted flag
   btn = document.getElementById("submitButton");
   btn.value = "Submitting, please wait...";
   btn.disabled = true;
   
   alreadySubmitted = true;
   return true;
}

function highLight(item,message) {
   item.style.background = 'red';
   window.alert(message);
   item.focus();
} // assume IE

function lowLight(item) {
   item.style.background = '';
}

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

function goToPage(pageName) {
   return location.href="form.py?formname=" + pageName;
}

var fileArray = new Array();
fileArray[""] = ["Select an experiment"];
<!--__EXISTING_FILE_ARRAY__-->

var fileArray2 = new Array();
fileArray2[""] = ["Select an experiment"];
<!--__EXISTING_FILES__-->

function setFileNames(subName, pos) {
  if (pos == 'x') {
   var subs = fileArray[subName];
   var sub = document.arrayform.file;
   while (sub.length > 0) {
      sub.remove(0);
   }
   
   for (i = 0; i < subs.length; i++) {
         newOpt = document.createElement("option");
         newOpt.text = subs[i];
         newOpt.value = subs[i];
      var browserName = navigator.appName;
      if (browserName == "Netscape" || browserName == "Opera") { 
         sub.add(newOpt, null);
      } else if (browserName=="Microsoft Internet Explorer") {
         sub.add(newOpt);
      }
   }
  } else {
   var subs = fileArray2[subName];
   var sub = eval('document.arrayform.fileList'+pos);
   while (sub.length > 0) {
      sub.remove(0);
   }
   
   for (i = 0; i < subs.length; i++) {
         newOpt = document.createElement("option");
         newOpt.text = subs[i];
         newOpt.value = subs[i];
      var browserName = navigator.appName;
      if (browserName == "Netscape" || browserName == "Opera") { 
         sub.add(newOpt, null);
      } else if (browserName=="Microsoft Internet Explorer") {
         sub.add(newOpt);
      }
   }
  }
}

function checkCombos(box, pos) {
   if (box.name == 'series') {
      var sub = document.arrayform.submissions;
      var fil = document.arrayform.file;
      if (sub.value != '') {
         var res = window.confirm("Are you sure you want to clear the submission & file fields and select this series?");
         if (res == 1) {
            sub.selectedIndex = 0;
            setFileNames(sub.value, pos);
         } else {
            box.selectedIndex = 0;
         }
      }
   } else if (box.name == 'submissions') {
      var ser = document.arrayform.series;
      if (ser.value != '') {
         var res = window.confirm("Are you sure you want to clear the series field and select this submission?");
         if (res == 1) {
            ser.selectedIndex = 0;
         } else {
            box.selectedIndex = 0;
         }
      }
      setFileNames(box.value, pos);
   } else if (box.name == ('submissions'+pos)) {
      setFileNames(box.value, pos);
   }
}

//================================================================//

var file_count = 1;

function setFileCount(count){
   var field = document.arrayform.fileCount;
   field.setAttribute("value", count);
}

function fileRowText(id) {
   return 'Folder: <select name="submissions'+id+'" onChange="checkCombos(this, '+id+')">' +
          '   <option value="" selected>' +
          <!--__EXISTING_FILE_FOLDERS__-->
          '</select><br>File: &nbsp; &nbsp; &nbsp;' +
          '<select name="fileList' + id + '" >' +
          '<option value="Select an experiment" selected>Select an experiment' +
          '</select>';
}

function addFileRow(TableID) {
   var table = document.getElementById(TableID);
   var row = table.insertRow(table.rows.length);
   var cell = row.insertCell(0);
   cell.vAlign="top"
   cell.innerHTML = fileRowText(file_count+1);
   file_count++;
   setFileCount(file_count);
}

//================================================================//

</script>
</head><body>
<FORM name="arrayform" onSubmit="return checkAll();" METHOD="POST" ENCTYPE="multipart/form-data" ACTION="/cgi-bin/agbrdf/form.py" >
<input type="HIDDEN" name="formname" value="microarrayDocumentForm"/>
<input type="HIDDEN" name="sessionid" value="0"/>
<input type="HIDDEN" name="fileCount" value="1"/>
   
<table border="true" id="Top_table" width=100%>
   <tr> 
      <td colspan="2"> 
         <h1 class="top">AgResearch Microarray Upload Form</h1>
      </td>
   </tr>
   <tr> 
      <td colspan="2"> 
         <table align=center class=plainTable style="border-width: 0">
            <tr align=center valign=middle>
               <td class=color1 title="Define one or more protocols if required" onclick="goToPage('MicroarrayForm1.htm');">
                  <img src="/images/protocol.gif" border="0" height="42" width="42"/>
                  <br>Protocol
               </td>
               <td class=arrow>
                  &rarr;
               </td>
               <td class=color2 title="Define one or more experimental subjects if required" onclick="goToPage('MicroarrayForm2.htm');">
                  <img src="/images/sheep.gif" border="0" height="42" width="42"/>
                  <br>Subject
               </td>
               <td class=arrow>
                  &rarr;
               </td>
               <td class=color3 title="Define one or more samples if required" onclick="goToPage('MicroarrayForm3.htm');">
                  <img src="/images/eppendorf.gif" border="0" height="42" width="42"/>
                  <br>Sample
               </td>
               <td class=arrow>
                  &rarr;
               </td>
               <td class=color4 title="Submit Files" onclick="goToPage('MicroarrayForm4.htm');">
                  <img src="/images/microarray.jpg" border="0" height="42" width="42"/>
                  <br>Files
               </td>
               <td class=arrow>
                  &rarr;
               </td>
               <td class=color5 title="Define Series" onclick="goToPage('MicroarrayForm5.htm');">
                  <img src="/images/series.gif" border="0" height="42" width="42"/>
                  <br>Series
               </td>
               <td class=arrow>
                  &rarr;
               </td>
               <td class=color6 title="Define contrasts" onclick="goToPage('MicroarrayForm6.htm');">
                  <img src="/images/contrast.gif" border="0" height="42" width="42"/>
                  <br>Contrasts
               </td>
               <td class=arrow>
                  &rarr;
               </td>
               <td class=color0 title="Submit related documents (if any)">
                  <img src="/images/documents.gif" border="0" height="42" width="42"/>
                  <br>Documents
               </td>
            </tr>
         </table>
      </td>
   </tr>
</table>

<br>

<table border="true" id="Outer_table" width=100%>
   <tr>
      <td colspan=2 >
         <div style="text-align: center; font-size: 150%; font-weight: bold; line-height: 2">Documents</div>
         <div style="text-align: left; font-size: 90%; font-weight: normal;">
            Use this form to link already-uploaded documents to either a series or a submission</div>
      </td>
   </tr>
   
   <tr>
      <td class="fieldname" width=17%>
         <p class="fieldname"><b>Series name:</b>
      </td>
      <td class="input" width=83%>
         <select name="series" onChange="checkCombos(this, 'x')">
            <option value="" selected>
            <!--__EXISTING_SERIES__-->
         </select>
      </td>
   </tr>
   <tr>
      <td class="fieldname">
         <p class="fieldname"><b>Submission name:</b>
      </td>
      <td class="input">
         <select name="submissions" onChange="checkCombos(this, 'x')">
            <option value="" selected>
            <!--__EXISTING_SUBMISSIONS__-->
         </select>
         
         <select name="file">
            <option value="Select an experiment">Select an experiment
         </select>
      </td>
   </tr>
   
   <tr>
      <td>
         <p><b>Use File:</b> <i>(uploaded with <a href="/cgi-bin/agbrdf/form.py?formname=fileSubmissionForm">File Upload form</a>)</i>
      </td>
      <td>
         <button type="button" id="addButton" onclick="addFileRow('fileTable')">Add Another File</button>
         <table id="fileTable" class="plainTable">
            <tr>
               <td>
                  <script>document.write(fileRowText('1'));</script>
               </td>
            </tr>
         </table>
      </td>
   </tr>


<tr><td colspan=2>
<P>
<i>
Please <a href="mailto:alan.mcculloch@agresearch.co.nz;jason.mitchell@agresearch.co.nz?subject=Microarray Suggestion">email us</a> with any suggestions for improvements to this form.
</i>

</td></tr>
   <tr>
      <td colspan=2 align=center>
         <p><input id="submitButton" type="submit" value="Link Documents">
      </td>
   </tr>
</table>
</FORM>
</body>
</html>
"""



""" --------- module methods ------------"""

def _mkdir(newdir):
    """Found this Code snippet at: 
    http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/82465
    works the way a good mkdir should :)
        - already exists, silently complete
        - regular file in the way, raise an exception
        - parent directory(ies) does not exist, make them as well
    """
    if os.path.isdir(newdir):
        pass
    elif os.path.isfile(newdir):
        raise OSError("a file with the same name as the desired " \
                      "dir, '%s', already exists." % newdir)
    else:
        head, tail = os.path.split(newdir)
        if head and not os.path.isdir(head):
            _mkdir(head)
        #print "_mkdir %s" % repr(newdir)
        if tail:
            os.mkdir(newdir)
            



""" --------- classes -------------------"""
######################################################################
#
# base class for agresearch forms
#
######################################################################
class form (object) :
    def __init__(self):
        object.__init__(self)

        # stamp the maximum obid to assist with rollbacks
        connection=databaseModule.getConnection()
        stampCursor = connection.cursor()
        sql = "SELECT last_value FROM ob_obidseq" #Formerly "select max(obid) from ob" but it was WAY too slow!
        stampCursor.execute(sql)
        maxobid = stampCursor.fetchone()
        formmodulelogger.info("Form obid stamp : max obid = %s"%maxobid[0])

        

        self.formState = {
            'ERROR' : 0,
            'MESSAGE' : '',
            'MODE' : 'INSERT'}

        # the AboutMe dictionary , contains sections of text describing the
        # form. The dictionary is structured in three layers :
        # layer 1 is indexed by the view that is in force, since the description
        #    depends on the view
        # layer 2 is indexed by a number used to control the order of the sections
        # layer 3 contains details of the section, at least the section name and text
        # Subclasses of form, such as sequence submission form etc, will add paragraphs as they wish
        # to the AboutMe dictionary, to customise the description as appropriate. Also,
        # specific instances of the brdf can override the text as whole to insert
        # localised descriptions
        self.AboutMe = {
            'insert' : {
                0 : {
                    'sectionname' : 'Form_Description',
                    'heading' : 'Form Description',
                    'text' : """ ** sorry no help for this form is currently available ** """  # subclasses fill in this if they can
                } # a dictionary for each section
            } # a dictionary for each view
        } # AboutMe dictionary


    def makeAboutMe(self,context):
        """ This method renders the AboutMe dictionary as HTML """
        if context in self.AboutMe:
            AboutMe = self.AboutMe[context]
        else:
            AboutMe = self.AboutMe['insert']


        doc = ""
        # make table of contents
        toc = "<h2> Contents </h2> <p/> <ul>"
        sections = AboutMe.keys()
        sections.sort()
        for sectionnumber in sections:
            sectionDict = AboutMe[sectionnumber]
            if len(sectionDict['text']) > 0:
                # if the heading is indented by a <ul> , do not make it
                # an item
                if re.search('<ul>',sectionDict['heading'],re.IGNORECASE):
                    toc += '<b><i>%s</i></b>'%(sectionDict['heading'])
                else:
                    toc += '<li><b><i>%s</i></b></li>'%(sectionDict['heading'])

        toc += '</ul>'

        doc += toc

        # make sections
        for sectionnumber in sections:
            sectionDict = AboutMe[sectionnumber]
            if len(sectionDict['text']) > 0:
                text = re.sub('\n',' ',sectionDict['text'])
                doc += '<p/><h3> %s </h3><p/>%s'%(sectionDict['heading'],text)

        #formmodulelogger.info(doc)

        return doc


######################################################################
#
# This forms handles submissions of 
# sequence data
#
######################################################################
class AgResearchSequenceSubmissionForm ( form ):
    """ class for sequence submission Form  """
    def __init__(self, dataDict):
        formmodulelogger.info("in constructor of sequenceSubmissionForm")
        form.__init__(self)


        self.AboutMe['insert'][0] = {
                    'sectionname' : 'Form_Description',
                    'heading' : 'Form Description',
                    'text' : """
                This form may be used to submit sequences to the PG database, together with
                related information about the subjects and samples involved in the sequencing,
                and the lab resources (primers, vectors) that were used. All of the subjects , samples
                and lab resources submitted can be re-used in future submissions. Submitting this
                information to the database will build up a searchable repository of subjects, samples
                ,sequences and lab resources. The database maintains links between these items so
                that it is easy (for example) to report on all sequencing that has been done
                from a given subject, or using a given vector or primer.
                <p/>
                You can also record sequence features in the features section below.
                <p/>
                Any files associated with the sequence can be submitted by specifying that
                you require an upload folder. These will be linked to the sequence they relate
                to
                <p/>
                Once a sequence has been submitted to the database, free text comments can be attached
                to the sequence. You can also attach hyperlinks to sequences - for example, to
                external records such as NCBI nucleotide, protein or gene.
                <p/>
                Comments and hyperlinks can also be attached to other records such as primers, vectors
                , subjects and samples.
                <p/>
                We will in the future support various export formats such as Genbank , so that
                sequences can be ported to packages such as Vector NTI, which provide
                graphical sequence feature displays.
                  """
        } # customise AboutMe dictionary for this form
        self.AboutMe['insert'][5] = {
                    'sectionname' : 'Known_Bugs',
                    'heading' : 'Known Bugs',
                    'text' : """
                    <ul>
                       <li> When adding a feature the positions entered are currently not validated. Entering
                       an invalid number will cause the submission to fail ; positions that are outside the
                       sequence are accepted. This will be fixed soon.
                    </ul>
                    If you encounter any problems please <a href=&quot;mailto:alan.mcculloch@agresearch.co.nz?CC=anar.khan@agresearch.co.nz;russell.smithies@agresearch.co.nz&Subject=AgResearch Genomics Sequence Submission Form Bug Report&quot;> contact us </a> including full details and a screen dump or web-page save
                    """
        } # customise AboutMe dictionary for this form





        self.dataDict = dataDict
        formmodulelogger.info(str(self.dataDict))
        if dataDict['formstate'] == "insert":
            if "sessionid" not in dataDict:
                try:
                   print self.asInsertForm()
                except brdfException , msg:
                   print htmlModule.pageWrap("Error creating form","The following error was reported (usually this means your login name is not set up in the database ) : <p> %s"%msg,cssLink=brdfCSSLink)
    
            else:
                formmodulelogger.info("calling processFormData")
                self.processFormData()
        

    def processFormData(self):
        formmodulelogger.info(str(self.dataDict))
       	connection=databaseModule.getConnection()
        

        # get or create the person submitting the form
        submitter = staffOb()
        try:
            submitter.initFromDatabase("agresearch.%s"%self.dataDict['submitted_by'],connection)
        except brdfException:
            if submitter.obState['ERROR'] == 1:
                # could not find so create
                submitter.initNew(connection)
                submitter.databaseFields.update ( {
                    'xreflsid' : "agresearch.%s"%self.dataDict['submitted_by'],
                    'loginname' :  self.dataDict['submitted_by'],                
                    'emailaddress' : eval({True : "self.dataDict['submitter_email_address']" , False : "None"}['submitter_email_address' in self.dataDict])
                })
                submitter.insertDatabase(connection)
            else:
                # some other error - re-raise
                raise brdfException, submitter.obState['MESSAGE']
                

        # get or create the default location for storing files
        sql="""
        select attributeValue
        from
        stafffact
        where
        staffOb = %s and
        factnamespace = 'AGRESEARCH' and
        attributename = 'UPLOAD_PATH'
        """%submitter.databaseFields['obid']
        pathCursor = connection.cursor()
        formmodulelogger.info("executing %s"%sql)
        pathCursor.execute(sql)
        pathRecord = pathCursor.fetchone()
        if pathCursor.rowcount != 1:
            # insert the default path
            pathFields = {
                'staffob' : submitter.databaseFields['obid'],
                'factnamespace' : 'AGRESEARCH' ,
                'attributename' : 'UPLOAD_PATH',
                #'attributevalue' : os.path.join(agbrdfConf.AGRESEARCH_TRACEDIRECTORY_GET_PATH,submitter.databaseFields['loginname'])
                'attributevalue' : agbrdfConf.AGRESEARCH_TRACEDIRECTORY_GET_PATH
            }
            sql = """
            insert into stafffact(staffob,factnamespace,attributename,attributevalue)
            values(%(staffob)s,%(factnamespace)s,%(attributename)s,%(attributevalue)s)
            """
            pathCursor.execute(sql,pathFields)
            uploadPath = pathFields['attributevalue']
        else:
            uploadPath = pathRecord[0]

        formmodulelogger.info("uploadPath=%s"%uploadPath)

        

        #name the sequence and create the sequence object 
        # - name is submittedname.version, with version
        # guaranteed unique
        version = 1
        sequenceName = "%s.%s"%(self.dataDict['sequence_name'],str(version))
        sequence = bioSequenceOb()
        try :
            sequence.initFromDatabase("agresearch.%s"%sequenceName,connection)
        except brdfException:
            sequence.initNew(connection)
            sequence.databaseFields.update( {
                'xreflsid' : "agresearch.%s"%sequenceName
            })

        maxVersions = 100
        while sequence.obState['NEW'] == 0 and version < maxVersions:
            version += 1
            sequenceName = "%s.%s"%(self.dataDict['sequence_name'],str(version))
            sequence = bioSequenceOb()
            try :
                sequence.initFromDatabase("agresearch.%s"%sequenceName,connection)
            except brdfException:
                sequence.initNew(connection)
                sequence.databaseFields.update( {
                    'xreflsid' : "agresearch.%s"%sequenceName
                })                

        if version >= maxVersions or sequence.obState['NEW'] == 0:
            raise brdfException("Error : unable to obtain new sequence using the name %s - exceeded 100 versions, choose another name !"%self.dataDict['sequence_name'])

        sequence.databaseFields.update ({
            'sequencename' : sequenceName,
            'sequencetype' : self.dataDict['mol_type'],
            'seqstring' : re.sub('\s','',self.dataDict['DNA_seq'].strip()),
            'sequencetopology' : self.dataDict['topology'],
            'sequencedescription' : self.dataDict['sequence_description'],
            'seqcomment' : eval({True : "self.dataDict['additional_comments']" , False : "None"}['additional_comments' in self.dataDict]),
            'seqlength' : len(re.sub('\s','',self.dataDict['DNA_seq'].strip()))
            #'seqlength' : eval({ False : "self.dataDict.get('seqlen',len(re.sub('\s','',self.dataDict['DNA_seq'].strip())))", True : "self.dataDict['DNA_seq_length']"}\
            #                   ['DNA_seq_length' in self.dataDict])
        })

        sequence.insertDatabase(connection)


        # get or create a listob representing the project
        projectname = self.dataDict['project']
        if 'projectother' in self.dataDict:
            projectname = self.dataDict['projectother']
        projectlsid = "agresearch.project.%s"%projectname
            
        project = obList()
        try:
            project.initFromDatabase(projectlsid,connection)
        except brdfException:
            project.initNew(connection)
            project.databaseFields.update ( {
                'xreflsid' : projectlsid,
                'listtype' : 'USER_PROJECT_LIST',
                'listname' : projectname,
                'listcomment' : ' This project list created as part of sequence submission, for %s'%sequence.databaseFields['xreflsid'] 
            })
            project.insertDatabase(connection)
        project.addListMember(sequence,"added as part of sequence submission",connection)
        

        # create a data import - this needs an importProcedure and a dataSource
        # get or create the import procedure
        importProcedure = importProcedureOb()        
        try:
            importProcedure.initFromDatabase("agresearch.forms.sequenceSubmissionForm",connection)
        except brdfException:
            importProcedure.initNew(connection)
            importProcedure.databaseFields.update ( {
                'xreflsid' : "agresearch.forms.sequenceSubmissionForm",
                'procedurename' : "forms.sequenceSubmissionForm",
                'procedurecomment' : "main sequence submission form for AgResearch from 3/2006"
            })
            importProcedure.insertDatabase(connection)        

        # set up data source and import 
        dataSource = dataSourceOb()
        submissionName = "%s.%s"%(submitter.databaseFields['xreflsid'],sequenceName)

        # assemble the submission reasons into a readable string
        submissionReasons = {
            'transformation' : 'data transformation',
            'submission_colleague' : 'pass on data to colleague',
            'submission_archive' : 'archive files on server',
            'submission_import' : 'data to be imported into relational database',
            'submission_reason_other' : eval({False : "None", True : "self.dataDict['submission_reason_other']"}['submission_reason_other' in self.dataDict])
        }
            
        submissionReason = string.join([submissionReasons[item] for item in ['submission_colleague','submission_archive','submission_import','submission_reason_other'] \
                            if item in self.dataDict],' : ')
        dataSource.initNew(connection,'Other')
        dataSource.databaseFields.update({
            'xreflsid' : submissionName,
            'numberoffiles' : eval({ True : "self.dataDict['filecount']", False : "None" }['filecount' in self.dataDict])
        })
        
        dataSource.insertDatabase(connection)
        dataImport = importFunction()
        dataImport.initNew(connection)
        dataImport.databaseFields.update ({
            'xreflsid' : "%s.%s"%(submissionName,"import"),
            'datasourceob' : dataSource.databaseFields['obid'],
            'importprocedureob' : importProcedure.databaseFields['obid'],
            'ob' : sequence.databaseFields['obid'],
            'processinginstructions' : self.dataDict.get('post_processing_instructions',''),
            'notificationaddresses' : self.dataDict.get('post_submission_notify',''),
            'submissionreasons' : submissionReason                
        })
        dataImport.insertDatabase(connection)


        # set up the biosubject
        subject = bioSubjectOb()
        organism = self.dataDict['org_name']
        if 'org_name_other' in self.dataDict:
            organism = self.dataDict['org_name_other']
        subjectlsid = 'agresearch.%s'%organism
        try :
            subject.initFromDatabase(subjectlsid,connection)
        except brdfException:
            subject.initNew(connection)
            subject.databaseFields.update( {
                'xreflsid' : subjectlsid,
                'subjectname' : subjectlsid,
                'subjectdescription' : 'AgResearch sequence submission (dummy) bio subject record',
                'subjectspeciesname' : organism
            })
            subject.insertDatabase(connection)


        # set up the biosample

        # first see whether they have selected an existing sample
        if 'existingSource' in self.dataDict:
            sample = bioSampleOb()
            sample.initFromDatabase(self.dataDict['existingSource'],connection)
        else:
            version = 1
            maxVersions = 1000000
            sample = bioSampleOb()
            if 'sourceName' in self.dataDict:
                samplelsid = "agresearch.%s.%s.%s"%(organism,self.dataDict['sourceName'],str(version))
            else:
                samplelsid = "agresearch.%s.%s.%s"%(organism,"unnamed sample",str(version))

            
            try :
                sample.initFromDatabase(samplelsid,connection)
            except brdfException:
                None
            while sample.obState['NEW'] == 0 and version < maxVersions:
                version += 1
                if 'sourceName' in self.dataDict:
                    samplelsid = "agresearch.%s.%s.%s"%(organism,self.dataDict['sourceName'],str(version))
                else:
                    samplelsid = "agresearch.%s.%s.%s"%(organism,"unnamed sample",str(version))
                sample = bioSampleOb()   
                try :
                    sample.initFromDatabase(samplelsid,connection)
                except brdfException:
                    None

            if version > maxVersions:
                  raise brdfException("Error , unable to create sample as exceeded 10 versions")
            sample.initNew(connection)
            sample.databaseFields.update( {
                  'xreflsid' : samplelsid,
                  'samplename' : samplelsid,
                  'sampletype' : 'Other',
                  'sampledescription' : 'sample created by sequence submission'                  
            })
            sample.insertDatabase(connection)
            sample.createSamplingFunction(connection, subject, "%s.sampling"%samplelsid)           

            
        # attach the source modifiers (the function that adds these checks and will not add the same
        # one twice
        for i in range(20):
            modifierName = 'SM_%s'%i
            modifierValue = 'SMV_%s'%i
            if modifierName in self.dataDict and modifierValue in self.dataDict:
                sample.addFact(connection,'AGRESEARCH',self.dataDict[modifierName],self.dataDict[modifierValue])


        

        # set up the labresource list
        labList = labResourceList()
        labresourcelistlsid = "%s.labresourcelist"%sequence.databaseFields['xreflsid']
        labList.initNew(connection)
        labList.databaseFields.update( {
            'xreflsid' : labresourcelistlsid,
            'listname' : labresourcelistlsid
        })
        labList.insertDatabase(connection)            
            

        # set up each lab resource and add to list
        
        labResource = labResourceOb()

        # first , if they have selected existing ones , add to the list

        # process all existing vectors selected - this handles single selects
        if 'existingVector' in self.dataDict:
            labResource.initFromDatabase(self.dataDict['existingVector'],connection)
            labList.addLabResource(connection,labResource)
        # process all existing vectors selected - this handles multiple selects
        for i in range(10):
            fieldName = 'existingVector_%s'%i
            if fieldName in self.dataDict:
                labResource.initFromDatabase(self.dataDict[fieldName],connection)
                labList.addLabResource(connection,labResource)            

            


        # process all existing primers selected - this handles single selects
        fieldName = 'existingForwardPrimer'
        if fieldName in self.dataDict:
            labResource.initFromDatabase(self.dataDict[fieldName],connection)
            labList.addLabResource(connection,labResource)
        fieldName = 'existingReversePrimer'
        if fieldName in self.dataDict:
            labResource.initFromDatabase(self.dataDict[fieldName],connection)
            labList.addLabResource(connection,labResource)                    
        
        
        # process all existing primers selected - this handles multiple selects
        for i in range(10):
            fieldName = 'existingForwardPrimer_%s'%i
            if fieldName in self.dataDict:
                labResource.initFromDatabase(self.dataDict[fieldName],connection)
                labList.addLabResource(connection,labResource)
        for i in range(10):
            fieldName = 'existingReversePrimer_%s'%i
            if fieldName in self.dataDict:
                labResource.initFromDatabase(self.dataDict[fieldName],connection)
                labList.addLabResource(connection,labResource)
                
            
            
            
        for i in range(10):
            vectorName = 'VI_%s'%i
            vectorPrimer = 'VIT_%s'%i
            if vectorName in self.dataDict:
                labresourcelsid = 'agresearch.%s'%self.dataDict[vectorName]
                try :
                    labResource.initFromDatabase(labresourcelsid,connection)
                except brdfException:
                    labResource.initNew(connection,'Sequencing Vector',labresourcelsid,'agresearch vector %s'%self.dataDict[vectorName],\
                                        'AgResearch sequencing vector')
                    labResource.insertDatabase(connection)
                if vectorPrimer in self.dataDict:
                    labResource.addFact(connection,'Primer','Priming Information',self.dataDict[vectorPrimer])
                labList.addLabResource(connection,labResource)

            primerDirection = 'PI_%s'%i
            primerName = 'PIT_%s'%i
            primerSequence = 'PST_%s'%i
            if primerName in self.dataDict or primerSequence in self.dataDict :

                if primerName not in self.dataDict:
                    self.dataDict.update ({
                        primerName : "%s.%s primer"%(sequence.sequencename,self.dataDict[primerDirection])
                    })
                labresourcelsid = 'agresearch.%s'%self.dataDict[primerName]
                
                primerType = 'Forward Primer'
                if self.dataDict[primerDirection] == 'reverse':
                    primerType = 'Reverse Primer'
                    
                try :
                    labResource.initFromDatabase(labresourcelsid,connection)
                except brdfException:
                    labResource.initNew(connection,primerType,labresourcelsid,'agresearch primer %s'%self.dataDict[primerName],\
                                        'AgResearch primer')
                    
                    if primerSequence in self.dataDict:
                        labResource.databaseFields.update ({
                            'resourcesequence' : self.dataDict[primerSequence]
                        })
                    
                    labResource.insertDatabase(connection)
                         
                    
                labList.addLabResource(connection,labResource)


        for i in range(10):
            featuretype = 'feature_type_%s'%i
            featurestrand = 'forward_reverse_%s'%i
            featurestart = 'feature_start_%s'%i
            featurestop = 'feature_stop_%s'%i
             
            if featuretype in self.dataDict:
                sequence.addFeature ( connection , {
                    'featuretype' : eval({True : 'self.dataDict[featuretype]', False : 'None'}[featuretype in self.dataDict]),
                    'featurestrand' : eval({True : 'int(self.dataDict[featurestrand])', False : 'None'}[featurestrand in self.dataDict]),
                    'featurestart' : eval({True : 'int(self.dataDict[featurestart])', False : 'None'}[featurestart in self.dataDict]),
                    'featurestop' : eval({True : 'int(self.dataDict[featurestop])', False : 'None'}[featurestop in self.dataDict])
                 })
                
                
                        
        

        # set up sequencing function - note that we set the virtual type to 285, which is
        # a version of the sequencingfunction that only includes reference to a labresourcelist,
        # not a labresourceob.
        sequence.createSequencingFunction(connection,sample, \
                                          "%s.sequencing"%sequence.databaseFields['xreflsid'],\
                                          None, labList,None,submitter.databaseFields['loginname'],None,285)


        #formmodulelogger.info(htmlModule.pageWrap("","Sequence %s has been saved"% \
        #                          ('<a href="'+fetcher + "?context=default&obid=%s&target=ob"%(sequence.databaseFields['obid']) + '">%s</a>'%\
        #                       sequence.databaseFields['xreflsid'])))


        # if they require an upload directory , set it up and create the link
        uploadtext=""
        if self.dataDict['ftpdir_yes_no'] == "Yes":
            uploadlsid = "%s.upload"%sequence.databaseFields['xreflsid']
            # first sanitise the filename as required
            uploadfolder  = re.sub('[^a-zA-Z0-9]','_',uploadlsid)
            #formmodulelogger.info("trying to create upload folder %s for sequence lsid %s submitted by %s"%(uploadfolder,uploadlsid,self.dataDict['submitted_by']))
            #result=os.spawnlp(os.P_WAIT, 'sh', 'sh', agbrdfConf.AGRESEARCH_CREATE_FOLDER_SCRIPT, uploadfolder, self.dataDict['submitted_by'])
            command = 'sh %s %s %s'%(agbrdfConf.AGRESEARCH_CREATE_FOLDER_SCRIPT, uploadfolder, self.dataDict['submitted_by'])
            formmodulelogger.info("trying to create upload folder using : %s"%command)
            (myin,myout,myerr)=os.popen3(command) 
            errorOutput = myerr.readlines()
            standardOutput = myout.readlines()
            myin.close()
            myerr.close()
            myout.close()

            errorText = ""
            if len(errorOutput) > 0:
               errorText = """
               <p> <font color="red"> Warning </font>
               The server encountered a problem creating the folder for submission of your files - error
               messages reported are below.
               Please contact bioinformatics support to report this problem. (The folder can be manually
               created in the meantime)
               <p>
               %s
               """%errorOutput
               

            formmodulelogger.info("error output : %s\n"%errorOutput)
            formmodulelogger.info("standard output : %s\n"%standardOutput)

            try:
                uploadlink = uriOb()
                uploadlink.initFromDatabase(uploadlsid,connection)
            except brdfException:
                uploadlink.initNew(connection)
                uploadlink.databaseFields.update(
                {
                    'createdby' : 'system',
                    'uristring' : os.path.join(uploadPath,uploadfolder),
                    'xreflsid' : uploadlsid ,
                    'uricomment' : 'This is the path to an upload folder for sequence %s'%sequence.databaseFields['xreflsid']
                })
                uploadlink.insertDatabase(connection)
                uploadlink.createLink(connection,sequence.databaseFields['obid'],"Uploaded Files"\
                                      ,'system')
                uploadlink.createLink(connection,dataSource.databaseFields['obid'],"Uploaded Files"\
                                      ,'system')
            uploadtext = """
            <li><p>To access the upload folder you requested, click <a href="%s" target="uploadpage" > Here </a>
            <p/>
            (Note that your upload folder is also available any time from a link in the database record page
            for your sequence)
            <p/>
            %s
            """%(uploadlink.databaseFields['uristring'],errorText) 

            #uploadtext = """
            #<li><p>To access the upload folder you requested, click the above link, then click External Links - this will
            #contain a link to the new folder. Click this to access the folder in file explorer, then drop your files into
            #the folder
            #<p>
            #%s
            #"""%(errorText)
            
                                 
            

        # do some checks and append comments on anything we find
        warnings=""
        if int(sequence.databaseFields['seqlength']) != int(self.dataDict.get('DNA_seq_length',0)):
            comment = commentOb()
            comment.initNew(connection)
            comment.databaseFields.update(
            {
                'createdby' : 'system',
                'commentstring' : "Sequence submission warning - sequence length(%s) does not equal the sequence length entered (%s)"%\
                        (sequence.databaseFields['seqlength'],self.dataDict.get('DNA_seq_length',0)),
                'xreflsid' : "%s.comment"%sequence.databaseFields['xreflsid']
            })
            comment.insertDatabase(connection)
            comment.createLink(connection,sequence.databaseFields['obid'],'system','#EDA7A7')
            warnings="<li><p>Note that one or more problems with the submission were noted - click on the above link, then click comments"
            
        response = htmlModule.pageWrap("","Sequence %s has been saved<p/><ul>%s%s</ul>"% \
                                  ('<a href="'+fetcher + "?context=default&obid=%s&target=ob"%sequence.databaseFields['obid'] + '">%s</a>'%\
                               sequence.databaseFields['xreflsid'], warnings,uploadtext),cssLink=brdfCSSLink)
        formmodulelogger.info("sending response : \n%s"%response)
        print response
        
        connection.close()        
        

    # method to return a response to the user
    def asResponseHTML(self):
        return " *** test response ***"

    # method to return a form to the user for editing an submission
    def asEditForm(self):
        return " *** test response ***"

    # method to return a response to the user
    def asInsertForm(self):
        formmodulelogger.info("in asInsertForm")
        connection=databaseModule.getConnection()
        self.dataDict['sessionid'] = "0"


        # obtain the list of existing projects
        sql = """
        select listname from oblist where xreflsid like 'agresearch.%' and listtype = 'USER_PROJECT_LIST'
        order by
        xreflsid
        """
        queryCursor = connection.cursor()
        queryCursor.execute(sql)
        projects = queryCursor.fetchall()
        existingProjects = reduce(lambda x,y : x + '<option value="%s"> %s' %(y[0],y[0]),projects,"")
        queryCursor.close()

        # obtain the list of existing organisms
        sql = """
        select subjectspeciesname from biosubjectob where xreflsid like 'agresearch.%'
        order by
        xreflsid
        """
        queryCursor = connection.cursor()
        queryCursor.execute(sql)
        species = queryCursor.fetchall()
        existingSpecies = reduce(lambda x,y : x + '<option value="%s"> %s' %(y[0],y[0]),species,"")
        queryCursor.close()
        
        

        # obtain the list of existing vectors
        sql = """
        select xreflsid,resourcename from labresourceob where resourcetype = 'Sequencing Vector'
        order by
        xreflsid
        """
        queryCursor = connection.cursor()
        queryCursor.execute(sql)
        vectors = queryCursor.fetchall()
        existingVectors = reduce(lambda x,y : x + '<option value="%s"> %s' %tuple(y),vectors,"")
        queryCursor.close()


        # obtain the list of existing primers
        #sql = """
        #select
        #    xreflsid,
        #    resourcename || ' : ' || substr(lrf2.attributeValue,1,20) || '...' 
        #from
        #    (labresourceob lr join labresourcefact lrf1 on
        #    lrf1.labresourceob = lr.obid and
        #    lrf1.attributeName = 'Direction' and 
        #    lrf1.attributeValue = 'forward') left outer join labresourcefact lrf2 on
        #    lrf2.labresourceob = lr.obid and
        #    lrf2.attributeName = 'Sequence'
        #where
        #   lr.resourcetype = 'Primer'
        #order by
        #   lr.resourcename
        #"""
        sql = """
        select
            xreflsid,
            resourcename || ' : ' || substr(resourcesequence,1,20)|| '...' 
        from
            labresourceob lr
        where
           lr.resourcetype =  'Forward Primer'
        order by
           lr.resourcename
        """        
        queryCursor = connection.cursor()
        queryCursor.execute(sql)
        primers = queryCursor.fetchall()
        existingForwardPrimers = reduce(lambda x,y : x + '<option value="%s"> %s</option>' %tuple(y),primers,"")


        #sql = """
        #select
        #    xreflsid,
        #    resourcename || ' : ' || substr(lrf2.attributeValue,1,20) || '...' 
        #from
        #    (labresourceob lr join labresourcefact lrf1 on
        #    lrf1.labresourceob = lr.obid and
        #    lrf1.attributeName = 'Direction' and 
        #    lrf1.attributeValue = 'reverse') left outer join labresourcefact lrf2 on
        #    lrf2.labresourceob = lr.obid and
        #    lrf2.attributeName = 'Sequence'
        #where
        #   lr.resourcetype = 'Primer'
        #order by
        #   lr.resourcename
        #"""
        sql = """
        select
            xreflsid,
            resourcename || ' : ' || substr(resourcesequence,1,20)|| '...' 
        from
            labresourceob lr
        where
           lr.resourcetype =  'Reverse Primer'
        order by
           lr.resourcename
        """                

        queryCursor.execute(sql)
        primers = queryCursor.fetchall()
        existingReversePrimers = reduce(lambda x,y : x + '<option value="%s"> %s' %tuple(y),primers,"")
        queryCursor.close()


        # obtain the list of existing sources
        sql = """
        select
            bs.xreflsid,
            bs.samplename
        from
            biosampleob bs
        where
            split_part(bs.xreflsid,'.',1) = 'agresearch'
        order by
            createddate desc
        """
        queryCursor = connection.cursor()
        queryCursor.execute(sql)
        sources = queryCursor.fetchall()
        existingSources = reduce(lambda x,y : x + '<option value="%s"> %s' %tuple(y),sources,"")

        
        
        
        myform=re.sub('__sessionid__',self.dataDict['sessionid'],forms_AgResearchSequenceSubmissionForm)
        myform=re.sub('__formstate__','insert',myform)
        myform=re.sub('__submitted_by__',self.dataDict['REMOTE_USER'],myform)
        myform=re.sub('__submitter_email_address__',"%s@agresearch.co.nz"%self.dataDict['REMOTE_USER'],myform)
        myform=re.sub('__existingVectors__',existingVectors,myform)
        myform=re.sub('__existingForwardPrimers__',existingForwardPrimers,myform)
        myform=re.sub('__existingReversePrimers__',existingReversePrimers,myform)
        myform=re.sub('__existingSources__',existingSources,myform)
        myform=re.sub('__defaultBRDFStyle__',htmlModule.defaultBRDFStyle,myform)
        myform=re.sub('__CSSToggleSectionButton__',htmlModule.CSSToggleSectionButton,myform)
        myform=re.sub('__existingSpecies__',existingSpecies,myform)
        myform=re.sub('__existingProjects__',existingProjects,myform)        
        myform=re.sub('__helptext__',self.makeAboutMe('insert'),myform)

        
        return contentWrap(myform,"")
        #connection.close()




        

######################################################################
#
# This forms handles submissions of 
# a form containing a comment
#
######################################################################
class commentForm ( form ):
    """ class for commentForm  """
    def __init__(self, dataDict):
        form.__init__(self)
        self.dataDict = dataDict
        if dataDict['formstate'] == "insert":
            if "sessionid" not in dataDict:
                print self.asInsertForm()
            else:
                self.processFormData()
        

    def processFormData(self):
       	connection=databaseModule.getConnection()        
        #insertCursor = connection.cursor()
        #insertCursor.close()
        #connection.close()
        comment = commentOb()
        comment.initNew(connection)
        comment.databaseFields.update(
            {
                'createdby' : self.dataDict['REMOTE_USER'],
                'commentstring' : self.dataDict['commentstring'],
                'xreflsid' : "%s.comment"%self.dataDict['aboutlsid'],
                'visibility' : self.dataDict['visibility']
            }
        )
        comment.insertDatabase(connection)
        comment.createLink(connection,self.dataDict['obid'],self.dataDict['REMOTE_USER'],self.dataDict['style_bgcolour'])
        connection.close()
                                 
        print htmlModule.pageWrap("","Comment on %s has been saved"% \
                              ('<a href="'+fetcher + "?context=%s&obid=%s&target=ob"%(self.dataDict['context'],self.dataDict['obid']) + '">%s</a>'%\
                               self.dataDict['aboutlsid']),cssLink=brdfCSSLink)
        

    # method to return a response to the user
    def asResponseHTML(self):
        return " *** test response ***"

    # method to return a response to the user
    def asEditForm(self):
        return " *** test response ***"

    # method to return a response to the user
    def asInsertForm(self):
        # obtain session token
        # get databaseFields
        self.dataDict['sessionid'] = 0
        
        
        return htmlModule.pageWrap("",forms_commentForm%(self.dataDict['sessionid'],\
                    self.dataDict['aboutob'],self.dataDict['aboutlsid'],"insert",self.dataDict['context'],self.dataDict['aboutlsid']),cssLink=brdfCSSLink)
        #connection.close()



######################################################################
#
# This forms handles submissions of 
# a form updating source code 
# example : /cgi-bin/form.py?context=default&formname=editAnalysisProcedureForm&formstate=edit&obid=41745371
######################################################################
class editAnalysisProcedureForm ( form ):
    """ class for commentForm  """
    def __init__(self, dataDict):
        form.__init__(self)
        self.dataDict = dataDict
        if dataDict['formstate'] == "edit":
            if "sessionid" not in dataDict:
                print self.asEditForm()
            else:
                self.processFormData()
        

    def processFormData(self):
        formmodulelogger.info("processing submitted data : %s"%str(self.dataDict))

        formmodulelogger.info("checking security policy for transaction %(versioning)s for %(REMOTE_USER)s"%self.dataDict)
        # implement !
        connection=databaseModule.getConnection()

        # saving and reading from the database , we need to manipulate a security polci dictionary.
        # Here is what is looks like : 
        policyDict = {
            "read" : [
                ("deny" , {
                    "__xreflsid__" : None
                    }),
                ("allow" , {
                    "__xreflsid__" : "nobody"
                    })
                ],
            "write" : [
                ("deny" , {
                    "__xreflsid__" : None
                    }),
                ("allow" , {
                    "__xreflsid__" : "nobody"
                    })
                ]
        }


        if self.dataDict["versioning"] == "overwrite":
                
                
                    
            analysisProcedure = analysisProcedureOb()
            analysisProcedure.initFromDatabase(self.dataDict['xreflsid'],connection)
            formmodulelogger.info("About to update procedure code : %s"%str(analysisProcedure.databaseFields))


            if "keep_history" in self.dataDict:
                history  = copy.deepcopy(analysisProcedure)
                history.databaseFields['obid'] = getNewObid(connection)
                history.databaseFields['xreflsid'] = "__%s_%s"%(history.databaseFields['xreflsid'], datetime.now().strftime("%Y-%m-%d:%H:%M:%S"))
                history.insertDatabase(connection)

                # a standard comment is attached to all versioned procedures - if it does not exist
                # create it, else attach the comment to this version.
                comment = commentOb()
                try :
                    comment.initFromDatabase("History.analysisProcedurOb.DefaultComment", connection)
                except brdfException:
                    if comment.obState['ERROR'] == 1:
                        comment.initNew(connection)
                        comment.databaseFields.update(
                        {
                            'xreflsid' : 'History.analysisProcedurOb.DefaultComment',
                            'commentstring' : """
                            *********************************************************
                            NOTE : this version of the procedure has been superceded.
                            *********************************************************
                            """
                        })
                        comment.insertDatabase(connection)
                comment.createLink(connection,history.databaseFields['obid'],self.dataDict['REMOTE_USER'],"#EE9999")



                # the history record has a link to the live record. If there is not a URI for the live
                # record then make one
                uri = uriOb()
                try:
                    uri.initFromDatabase("%s.uri"%analysisProcedure.databaseFields["xreflsid"],connection)
                except brdfException:
                    if uri.obState["ERROR"] == 1:
                        uri.initNew(connection)
                        uri.databaseFields.update(
                            {
                            'createdby' : self.dataDict['REMOTE_USER'],
                            'uristring' : fetcher + "?context=default&obid=%s&target=ob"%(analysisProcedure.databaseFields["xreflsid"]),
                            'xreflsid' : "%s.uri"%analysisProcedure.databaseFields["xreflsid"]
                        })
                        uri.insertDatabase(connection)
                uri.createLink(connection,history.databaseFields['obid'],"Link to Current Version of this Procedure",self.dataDict['REMOTE_USER'])


                # a chain of versions if maintained via predicatelinks. Link this history record to the
                # previous latest version. Obtain this crudely via string search and ordering of obid -
                # not quite as rigorous as (e.g.) a graph based query traversing the predicate links
                predicateCursor = connection.cursor()
                sql = """
                select
                   obid,
                   xreflsid
                from
                   analysisProcedureOb
                where
                   xreflsid like   '__' || %(xreflsid)s  || '_%%'
                order by
                   createddate, obid
                """
                formmodulelogger.info("versioning : executing %s"%(sql%analysisProcedure.databaseFields))
                predicateCursor.execute(sql,analysisProcedure.databaseFields)
                formmodulelogger.info("versioning : done executing %s"%(sql%analysisProcedure.databaseFields))

                versions = predicateCursor.fetchall()
                if predicateCursor.rowcount > 1:
                    formmodulelogger.info("(previous versions found)")
                    formmodulelogger.info(str(versions))
                    lastversion = versions[-2]
                    sql = """
                    insert into predicatelink(xreflsid,subjectob,objectob,predicate,voptypeid)
                    values('%s.link',%s,%s,'PREVIOUS-VERSION',383)
                    """%(lastversion[1], lastversion[0], history.databaseFields['obid'])
                    formmodulelogger.info("versioning : executing %s"%sql)
                    predicateCursor.execute(sql)
                    connection.commit()
                else:
                    formmodulelogger.info("(no previous versions found)")
                    lastversion = (analysisProcedure.databaseFields['obid'],analysisProcedure.databaseFields['xreflsid'])
                    sql = """
                    insert into predicatelink(xreflsid,subjectob,objectob,predicate,voptypeid)
                    values('%s.link',%s,%s,'PREVIOUS-VERSION',383)
                    """%(lastversion[1], lastversion[0], history.databaseFields['obid'])
                    formmodulelogger.info("versioning : executing %s"%sql)
                    predicateCursor.execute(sql)
                    connection.commit()

            # -------- end of section maintaining history --------
                    
                    
            analysisProcedure.databaseFields.update(self.dataDict)
            analysisProcedure.databaseFields['lastupdatedby'] = self.dataDict["REMOTE_USER"]
            analysisProcedure.updateDatabase(connection)
            print htmlModule.pageWrap("","Source code for %s has been saved"% \
                              ('<a href="'+fetcher + "?context=%s&obid=%s&target=ob"%(self.dataDict['context'],self.dataDict['obid']) + '">%s</a>'%\
                               self.dataDict['xreflsid']),cssLink=brdfCSSLink)
        elif self.dataDict["versioning"] == "newprocedure":
            analysisProcedure = analysisProcedureOb()

            # check that there is nothing with this name
            sql = """
            select procedurename from analysisprocedureob where
            procedurename = %(newprocedurename)s
            """
            checkCursor=connection.cursor()
            checkCursor.execute(sql,self.dataDict) 
            if checkCursor.rowcount > 0:
                print htmlModule.pageWrap("","There is an existing procedure called %(newprocedurename)s - please choose another name"%self.dataDict,cssLink=brdfCSSLink)
                connection.close()
                return

            analysisProcedure.initNew(connection)            
            analysisProcedure.databaseFields['xreflsid'] = self.dataDict["newprocedurename"]
            analysisProcedure.databaseFields['sourcecode'] = self.dataDict["sourcecode"]
            analysisProcedure.databaseFields['createdby'] = self.dataDict["REMOTE_USER"]
            analysisProcedure.databaseFields['author'] = self.dataDict["REMOTE_USER"]
            analysisProcedure.databaseFields['authordate'] = date.today().strftime("%Y-%m-%d") 
            analysisProcedure.databaseFields['lastupdatedby'] = self.dataDict["REMOTE_USER"]
            analysisProcedure.databaseFields['procedurename'] = self.dataDict["newprocedurename"]
            analysisProcedure.databaseFields['proceduretype'] = self.dataDict["newproceduretype"]
            analysisProcedure.databaseFields['proceduredescription'] = self.dataDict["newproceduredescription"]
            analysisProcedure.databaseFields['presentationtemplate'] = self.dataDict["presentationtemplate"]
            analysisProcedure.databaseFields['textincount'] = self.dataDict["textincount"]
            analysisProcedure.databaseFields['textoutcount'] = self.dataDict["textoutcount"]
            analysisProcedure.databaseFields['imageoutcount'] = self.dataDict["imageoutcount"]



            
            analysisProcedure.databaseFields['xreflsid'] = self.dataDict["newprocedurename"]
            analysisProcedure.insertDatabase(connection)
            print htmlModule.pageWrap("","Source code for %s has been saved"% \
                              ('<a href="'+fetcher + "?context=%s&obid=%s&target=ob"%(self.dataDict['context'],analysisProcedure.databaseFields['obid']) + '">%s</a>'%\
                               analysisProcedure.databaseFields['xreflsid']),cssLink=brdfCSSLink)
            connection.close()
        else:
            print htmlModule.pageWrap("","The versioning option selected is not currently supported",cssLink=brdfCSSLink)

        

    # method to return a response to the user
    def asResponseHTML(self):
        return " *** test response ***"

    # method to return a response to the user
    def asInsertForm(self):
        return " *** test response ***"

    # method to return a response to the user
    def asEditForm(self):
        # obtain session token
        # get databaseFields

        self.dataDict['sessionid'] = 0

        # obtain the sourcecode to edit
        connection=databaseModule.getConnection()
        editCursor = connection.cursor()
        sql = """
           select 
              xreflsid,
              createddate,
              createdby,
              lastupdateddate,
              lastupdatedby,
              author,
              authordate,
              sourcecode,
              presentationtemplate,
              procedurename,
              procedurecomment as oldcomments
           from
              analysisprocedureob
           where
              obid = %(obid)s
        """
        editCursor.execute(sql,self.dataDict)
        record = editCursor.fetchone()
        if editCursor.rowcount != 1:
           errorPage("error - could not find procedure %(obid)s to edit"%dataDict)

        self.dataDict.update( dict(zip([item[0] for item in editCursor.description],record)))

        # entityize the presentation template markup
        self.dataDict["presentationtemplate"] = re.sub("<","&lt;",self.dataDict["presentationtemplate"])
        self.dataDict["presentationtemplate"] = re.sub(">","&gt;",self.dataDict["presentationtemplate"])

        return htmlModule.pageWrap("",forms_editAnalysisProcedureForm%self.dataDict,cssLink=brdfCSSLink)
        #connection.close()



######################################################################
#
# This forms handles submissions of 
# a form containing a microarray heatmap definition 
# example : /cgi-bin/form.py?context=default&formname=defineArrayHeatMapForm&formstate=edit&obid=45276430
######################################################################
class defineArrayHeatMapForm( form ):
    """ class for define heapmap form  """
    def __init__(self, dataDict):
        form.__init__(self)
        self.dataDict = dataDict
        if dataDict['formstate'] == "edit":
            if "sessionid" not in dataDict:
                print self.asEditForm()
            else:
                self.processFormData()
        

    def processFormData(self):
        formmodulelogger.info("processing submitted data : %s"%str(self.dataDict))

        formmodulelogger.info("checking security policy for transaction for %(REMOTE_USER)s"%self.dataDict)
        # implement !
        connection=databaseModule.getConnection()

        # get an instance of the analysis procedure
        analysisProcedure = analysisProcedureOb()
        analysisProcedure.initFromDatabase(int(self.dataDict['obid']), connection)

        # marshall the selected slides for setup of datasource. Selected slides are list-values of 
        # fields named like array_ etc etc 
        slides = "slide\n"
        for field in self.dataDict.keys():
            if re.search('^array_',field) != None:
                slides += reduce(lambda x,y: x+'\n'+y, tuple(self.dataDict[field]))

        self.dataDict['slides'] = slides
        formmodulelogger.info("setting up slides data source using %s"%slides)

        # create the slides data source
        rowsource = dataSourceOb()
        try :
            rowsource.initFromDatabase('%(procedurename)s.%(heatmapname)s.rows'%self.dataDict,connection)
            errorPage('%(procedurename)s.%(heatmapname)s.rows already exists - please choose a different name for this data source '%self.dataDict)
            connection.close()
            return
        except brdfException:
            if rowsource.obState['ERROR'] == 1:
                # could not find so create
                rowsource.initNew(connection,'Tab delimited text')
                rowsource.databaseFields.update ( {
                    'xreflsid' : '%(procedurename)s.%(heatmapname)s.rows'%self.dataDict,
                    'datasourcename' :  '%(procedurename)s.%(heatmapname)s.rows'%self.dataDict,
                    'datasourcetype' : 'Tab delimited text' ,
                    'datasourcecomment' : 'Included slides for %(procedurename)s.%(heatmapname)s'%self.dataDict,
                    'datasourcecontent' : slides 
                })
                rowsource.insertDatabase(connection)
            else:
                # some other error - re-raise
                raise brdfException, rowsource.obState['MESSAGE']

        # create the spot accessions datasource
        example = """
 OMGB11019059HT
 OCS411053079HT
 OMGB11020055HT
 OSAA047057HT
 OSTA140084HT
 OSAA047058HT
 OSTA141004HT
 OSAA047070HT
 OSTA141005HT
 OSAA047071HT
 OSTA141010HT
 OCS411042007HT
 OFM1032001HT
 OCS411042009HT
 OFM1032005HT
 OCS411042012HT
 OFM1032007HT
"""
          
        accessions = re.split('[\n\r]+',self.dataDict['arrayprobes'])
        if accessions != None: 
            if len(accessions) > 0:

                # marshall the accessions for setup of datasource. 
                accessioncontent = "accession\n"
                accessioncontent += reduce(lambda x,y: x+'\n'+y, tuple([item.strip() for item in accessions if len(item.strip()) > 0]))

                self.dataDict['accessions'] = accessioncontent
                formmodulelogger.info("setting up genes data source using %s"%accessioncontent)

                # create the slides data source
                colsource = dataSourceOb()
                try :
                    colsource.initFromDatabase('%(procedurename)s.%(heatmapname)s.cols'%self.dataDict,connection)
                    errorPage('%(procedurename)s.%(heatmapname)s.cols already exists - please choose a different name for this data source '%self.dataDict)
                    connection.close()
                except brdfException:
                    if colsource.obState['ERROR'] == 1:
                        # could not find so create
                        colsource.initNew(connection,'Tab delimited text')
                        colsource.databaseFields.update ( {
                            'xreflsid' : '%(procedurename)s.%(heatmapname)s.cols'%self.dataDict,
                            'datasourcename' :  '%(procedurename)s.%(heatmapname)s.cols'%self.dataDict,
                            'datasourcetype' : 'Tab delimited text' ,
                            'datasourcecomment' : 'Included slides for %(procedurename)s.%(heatmapname)s'%self.dataDict,
                            'datasourcecontent' : accessioncontent
                        })
                        colsource.insertDatabase(connection)
                    else:
                        # some other error - re-raise
                        raise brdfException, colsource.obState['MESSAGE']

        # create the data source 
        sql = """
        select 
           msf.accession ,
           ges.xreflsid as slide,
           mo.gpr_logratio as logratio
        from 
           geneexpressionstudy 
        """
          
        # create the datasourcelist

        # add the analysis function
   
        # return a link to the analysis function
        print htmlModule.pageWrap("","Heat Map definition using %s has been saved - you can run the heatmap from this link"% \
             ('<a href="'+fetcher + "?context=%s&obid=%s&target=ob"%(self.dataDict['context'],analysisProcedure.databaseFields['obid']) + '">%s</a>'%\
             analysisProcedure.databaseFields['xreflsid']),cssLink=brdfCSSLink)


        # etc etc         

    # method to return a response to the user
    def asResponseHTML(self):
        return " *** test response ***"

    # method to return a response to the user
    def asInsertForm(self):
        return " *** test response ***"

    # method to return a response to the user
    def asEditForm(self):
        # obtain session token
        # get databaseFields

        self.dataDict['sessionid'] = 0

        connection=databaseModule.getConnection()
        editCursor = connection.cursor()        

        # obtain the name of the procedure to display
        sql = """
        select
           procedurename,
           proceduredescription
        from
           analysisprocedureob
        where
           obid = %(obid)s
        """
        editCursor.execute(sql,self.dataDict)
        procedure = editCursor.fetchone()
        self.dataDict.update( {
            "procedurename" : procedure[0],
            "proceduredescription" : procedure[1]
        })

        myform = forms_defineArrayHeatMapForm%self.dataDict
            
    
        # obtain the list of arrays to choose from 
        sql = """
           select 
              obid,
              xreflsid as resourcedescription
           from
              labresourceob
           where
              resourcetype = 'microarray'
           order by
              1
        """
        editCursor.execute(sql)
        records = editCursor.fetchall()
        arraysHTML=reduce(lambda x,y:x+("<option value=%s />%s\n"%tuple(y)),records,'')
        editCursor.close()
        connection.close()




        #  function multipost(url,selectname,resultelementname,queryleader,waitbanner,waiturl) {
        #arrayselectHTML = """
        #<select name="arrayselect" id="arrayselect" multiple size=21 onChange="window.alert('hello'); return true;" >""" + \
        #arrayselect  + \
        #'</select>\n'


        #  function multipost(url,selectname,resultelementname,queryleader,waitbanner,waiturl) {
        arrayselectHTML = """
        <select name="arrayselect" id="arrayselect" multiple size=21 onChange="multipost('%s','arrayselect','arrayslides_div','listname=arrayslides&amp;obid=','%s','%s'); return true;" >
        """%(listfetcher,waitURL,waiter) + \
        arraysHTML  + \
        '</select>\n'

        myform=re.sub('__arrayselect__',arrayselectHTML,myform)

        return htmlModule.pageWrap("",myform,cssLink=brdfCSSLink)
        #connection.close()




######################################################################
#
# This forms handles submissions of 
# a form containing a URI to be linked to a database object
#
######################################################################
class uriForm ( form ):
    """ class for uriForm  """
    def __init__(self, dataDict):
        form.__init__(self)
        self.dataDict = dataDict
        if dataDict['formstate'] == "insert":
            if "sessionid" not in dataDict:
                print self.asInsertForm()
            else:
                self.processFormData()
        

    def processFormData(self):
       	connection=databaseModule.getConnection()        
        #insertCursor = connection.cursor()
        #insertCursor.close()
        #connection.close()
        uri = uriOb()
        uri.initNew(connection)
        uri.databaseFields.update(
            {
                'createdby' : self.dataDict['REMOTE_USER'],
                'uristring' : self.dataDict['uristring'],
                'xreflsid' : "%s.uri"%self.dataDict['aboutlsid'],
                'visibility' : self.dataDict['visibility']
            }
        )
        uri.insertDatabase(connection)
        uri.createLink(connection,self.dataDict['obid'],self.dataDict['displaystring'],self.dataDict['REMOTE_USER'])
        connection.close()
                                 
        print htmlModule.pageWrap("","URI has been saved and attached to %s "% \
                              ('<a href="'+fetcher + "?context=%s&obid=%s&target=ob"%(self.dataDict['context'],self.dataDict['obid']) + '">%s</a>'%\
                               self.dataDict['aboutlsid']),cssLink=brdfCSSLink)
        

    # method to return a response to the user
    def asResponseHTML(self):
        return " *** test response ***"

    # method to return a response to the user
    def asEditForm(self):
        return " *** test response ***"

    # method to return a response to the user
    def asInsertForm(self):
        # obtain session token
        # get databaseFields

        self.dataDict['sessionid'] = 0
        
        
        return htmlModule.pageWrap("",forms_uriForm%(self.dataDict['sessionid'],\
                    self.dataDict['aboutob'],self.dataDict['aboutlsid'],"insert",self.dataDict['context'],self.dataDict['aboutlsid']),cssLink=brdfCSSLink)
        #connection.close()



######################################################################
#
# This forms handles submissions of 
# a form containing a microarray extract in AgResearch csv format
#
######################################################################
class microarrayAgResearchForm ( form ):
    """ class for microarray definitions supplied as CSV files  """
    def __init__(self, dataDict):
        form.__init__(self)
        self.dataDict = dataDict


    def processData(self):

        # set up the database dbconnection
        dbconnection=databaseModule.getConnection() 


        #create and initialise the array , data source and import session
        # objects

        # first get the import Procedure
        importProcedure = importProcedureOb()
        importprocedurelsid = 'importProcedure.microarrayAgResearchForm'
        try :
            importProcedure.initFromDatabase(importprocedurelsid,dbconnection)
        except brdfException:
            # not found so create it
            importProcedure.initNew(dbconnection)
            importProcedure.databaseFields.update ({
                'xreflsid' : importprocedurelsid,
                'procedurename' : 'microarrayAgResearchForm'
            })
            importProcedure.insertDatabase(dbconnection)
            
    
        resource = labResourceOb()
        resource.initNew(connection = dbconnection,\
                     resourcetype = self.dataDict["resourcetype"], \
                     xreflsid = self.dataDict['xreflsid'], \
                     resourcedescription = self.dataDict['resourcedescription'] )
   
    
        dataSource = dataSourceOb()
        dataSource.initNew(connection=dbconnection, \
                       datasourcetype=self.dataDict['datasourcetype'], \
                       physicalsourceuri = self.dataDict['physicalsourceuri'])

    
        importSession = labResourceImportFunction()
        importSession.initNew(connection=dbconnection, \
                          obtuple=(dataSource,importProcedure,resource))
                          
        importSession.runArrayImport(dbconnection)


        dbconnection.close()

    
    # method to return a response to the user
    def asResponseHTML(self):
        return " *** test response ***"

    # method to return a response to the user
    def asEditForm(self):
        return " *** test response ***"

    # method to return a response to the user
    def asInsertForm(self):
        return " *** test response ***"



######################################################################
#
# This forms handles the submission of the file-submission form.
#
######################################################################
class fileSubmissionForm ( form ):
    """ class for fileSubmissionForm  """
    def __init__(self, dataDict):
        formmodulelogger.info("in constructor of fileSubmissionForm")
        form.__init__(self)
        self.dataDict = dataDict
        #Need to comment out this logger, as it makes MASSIVE log entries for the 
        #rather Large JPEG files that we're uploading!!! -JSM 18/9/06
        #formmodulelogger.info(str(self.dataDict))
#        if dataDict['formstate'] == "insert":
        if "sessionid" not in dataDict:
            print self.asInsertForm()
        else:
            formmodulelogger.info("calling processFormData")
            self.processFormData()

    def processFormData(self):
        """
        Key/value pairs are:
        formname : fileSubmissionForm
        fileCount : 3
        submittedby : Jason Mitchell
        emailaddress : jason.mitchell@agresearch.co.nz
        projectID : Other
        otherProject : Ag.123
        subProgram : Coretech
        reason : import
        folder : FolderName_20060705093800
        desc1 : File1 - a log file from Acrobat Reader 7
        file1.value : Fri 02/06/2006 13:07:58.13 
            Removing "C:\Documents and Settings\All Users\NewFolder1" (ReturnCode=0) 
            Removing "C:\Documents and Settings\All Users\Start Menu\NewFolder1" (ReturnCode=0) 
            Removing "C:\Documents and Settings\All Users\Start Menu\Programs\NewFolder1" (ReturnCode=0) 
            Removing "C:\Documents and Settings\All Users\Start Menu\Programs\Startup\Adobe Reader Speed Launch.lnk" (ReturnCode=0) 
            Modify registry "HKLM\Software\Adobe\Acrobat Reader\7.0\FeatureLockdown" (ReturnCode=0) 
            Modify registry "HKLM\Software\AgResearch\Adobe Acrobat Reader" (ReturnCode=0)
        file1.filename : acrobat7.log
        type1 : Other
        desc2 : 2nd File - log file from something else
        file2.value : Tue 04/07/2006 17:33:03.21 
            SPSS_LMHOST variable not found. 
            SigmaPlot License Server (Addition). 
            Enviroment Variable SPSS_LMHOST will be created. 
            SPSS_LMHOST added with value @147.158.67.4 at 17:33:03.29.
        file2.filename : SigmaPlotPatch.log
        type2 : meta
        desc3 :
        file3.value :
        file3.filename :
        type3 :
        description : Two files, that contain some data. But really, they're just two 
            log files used for testing purposes. I've added a third (empty) file too!
        processing_instructions : Once you've submitted this form, take the text output 
            and copy it into the python script so you can see what the variables, etc 
            look like."""
        
        #formmodulelogger.info(str(self.dataDict))
        connection=databaseModule.getConnection()
           
#        htmlString = "Key/value pairs are:\n<br>"
#        for key in self.dataDict:
#            htmlString += key + " : " + str(self.dataDict[key]) + "<br>"
#        print htmlModule.pageWrap('',htmlString,'')
#        return
#        
        test = (self.dataDict.has_key('submittedby') and self.dataDict['submittedby'] != '' \
        and self.dataDict.has_key('emailaddress') and self.dataDict['emailaddress'] != '' \
        and self.dataDict.has_key('projectID') and self.dataDict['projectID'] != '' \
        and self.dataDict.has_key('subProgram') and self.dataDict['subProgram'] != '' \
        and self.dataDict.has_key('reason') and self.dataDict['reason'] != '' \
        and self.dataDict.has_key('folder') and self.dataDict['folder'] != '' \
        and self.dataDict.has_key('description') and self.dataDict['description'] != '')
        
        loopTest = []
        for i in range(int(self.dataDict['fileCount'])):
            testArray = [False,False,False,False]
            loopTest.append(False)
            if self.dataDict.has_key('desc'+str(i+1)) and self.dataDict['desc'+str(i+1)] != '' :
                testArray[0] = True
            if self.dataDict.has_key('file'+str(i+1)+'.filename') and self.dataDict['file'+str(i+1)+'.filename'] != '' :
                testArray[1] = True
            if self.dataDict.has_key('file'+str(i+1)) and self.dataDict['file'+str(i+1)] != '' :
                testArray[2] = True
            if self.dataDict.has_key('type'+str(i+1)) and self.dataDict['type'+str(i+1)] != '' :
                testArray[3] = True
            if (testArray[0] == True and testArray[1] == True and testArray[2] == True and testArray[3] == True) \
            or (testArray[0] == False and testArray[1] == False and testArray[2] == False and testArray[3] == False) :
                loopTest[i] = True
        
        if loopTest.count(False) > 0 :
            if loopTest.count(False) == 1 :
                pos = loopTest.index(False)
                formmodulelogger.info("submission not setup; not all file fields set in form!")
                htmlResp = '''<strong>ERROR in submission:</strong><br>\n
                Your submission did not have all the required fields filled in for file number '''+str(pos)+'''!<br> &nbsp; &nbsp;
                <button type=button onClick="location.href='form.py?formname=fileSubmissionForm'">Try again</button>
                '''
                if self.dataDict['file'+str(pos+1)+'.filename'] != '' and self.dataDict['file'+str(pos+1)] == '' :
                    htmlResp = '''<strong>ERROR in submission:</strong><br>\n
                    Your file-submission does not appear to have a valid file given for position '''+str(pos)+'''!<br> &nbsp; &nbsp;
                    <button type=button onClick="location.href='form.py?formname=fileSubmissionForm'">Try again</button>
                    '''
                print htmlModule.pageWrap('',htmlResp,'',cssLink=brdfCSSLink)
            else :
                pos = ''
                for i in range(len(loopTest)) :
                    if loopTest[i] == False :
                        pos = ' '+i+','
                pos = pos.strip(',')
                formmodulelogger.info("submission not setup; not all file fields set in form!")
                htmlResp = '''<strong>ERROR in submission:</strong><br>\n
                Your submission did not have all the required fields filled in for the files at positions:
                '''+pos+'''. If you can't seem to see where the "missing field(s)" is/are, the problem may be that 
                the file is named incorrectly.<br> &nbsp; &nbsp;
                <button type=button onClick="location.href='form.py?formname=fileSubmissionForm'">Try again</button>
                '''
                print htmlModule.pageWrap('',htmlResp,'',cssLink=brdfCSSLink)
                
        if loopTest.count(False) == 0 and test :
            # get or create the person submitting the form
            submitter = staffOb()
            try:
                submitter.initFromDatabase(self.dataDict['REMOTE_USER'],connection)
            except brdfException:
                if submitter.obState['ERROR'] == 1:
                    # could not find so create
                    submitter.initNew(connection)
                    submitter.databaseFields.update ( {
                        'xreflsid' : self.dataDict['REMOTE_USER'],
                        'loginname' :  self.dataDict['REMOTE_USER'],                
                        'emailaddress' : self.dataDict['REMOTE_USER'],
                        'fullname' : self.dataDict['submittedby']
                    })
                    submitter.insertDatabase(connection)
                else:
                    # some other error - re-raise
                    raise brdfException, submitter.obState['MESSAGE']
                    
            # Need to populate oblistfact table with relevant facts for this upload.
            projID = self.dataDict['projectID']
            if projID == 'Other' :
                projID = self.dataDict['otherProject']
    
            # set folder-defaults
            foldername = os.path.join(projID, self.dataDict['folder'])
            if self.dataDict['folder'] == 'New Submission' :
                foldername = os.path.join(projID, self.dataDict['newFolder'])
            folderlsid = "DATASOURCE UPLOAD.%s"%foldername
    
            # get or create the default location for storing files
            uploadPath = os.path.join(agbrdfConf.BFILE_PUTPATH, foldername)
            formmodulelogger.info("uploadPath=%s"%uploadPath)
            downloadPath = agbrdfConf.BFILE_GETPATH%foldername
            formmodulelogger.info("downloadPath=%s"%downloadPath)
    
    
            # import the file-data into the database
            maxCounter = int(self.dataDict['fileCount'])
            datasourceList = list()
            keywords = self.dataDict['folder']
            if keywords == 'New Submission' :
                keywords = self.dataDict['newFolder']
            renamedFiles = []
            for i in range(maxCounter) :
                filename = self.dataDict['file'+str(i+1)+'.filename']
                if filename != '' :
                    dataSource = dataSourceOb()
                    actualFile = self.dataDict['file'+str(i+1)]
                    descFile = self.dataDict['desc'+str(i+1)]
                    typeFile = self.dataDict['type'+str(i+1)]
                    
                    # Need to remove the folder prefixes if present (since Firefox
                    # doesn't include them, but IE6 does!)
                    slashCount = filename.count('\\')
                    if slashCount > 0 :
                        filename = filename.split('\\')[slashCount]
                    source = os.path.join(uploadPath,filename)
                    newFilename = ''
                    
                    #Need to save this file to the server.
                    fileSize = 0
                    if self.dataDict['reason'] != 'meta' :
                        _mkdir(uploadPath)
                        if os.path.isfile(source):
                            #File already exists!!!
                            #Need to ensure that if there's more than one '.', it won't screw things up,
                            # since we're putting the '(1)' before the last '.'
                            if filename.count('.') == 0 :
                                for j in range(1,100) :
                                    newFilename = filename+'('+str(j)+')'
                                    source = os.path.join(uploadPath,newFilename)
                                    if not os.path.isfile(source):
                                        break
                            else :
                                splitName = filename.split('.')
                                newStart = ''
                                for j in range(len(splitName)-1) :
                                    newStart += splitName[j]+'.'
                                newStart = newStart.rstrip('.')
                                for j in range(1,100) :
                                    newFilename = newStart+'('+str(j)+').'+splitName[len(splitName)-1]
                                    source = os.path.join(uploadPath,newFilename)
                                    if not os.path.isfile(source):
                                        break
                                
                            renamedFiles.append([filename,newFilename])
                        output = file(source, 'wb')
                        output.write(actualFile)
                        #Find out filesize
                        output.flush()
                        fileSize = output.tell()
                        output.close()
                    
                    keywords += ' ' + filename
                    if newFilename != '' :
                        keywords += ' ' + newFilename
                        filename = newFilename
                    
                    sizeFile = ''
                    physURI = ''
                    if fileSize != 0 :
                        physURI = source
                        fileSizeFloat = float(fileSize)
                        if (fileSize/(1024*1024) > 1):
                            sizeFile = '%.2f'%(fileSizeFloat/(1024*1024)) + "MB"
                        elif (fileSize/1024 > 1):
                            sizeFile = '%.2f'%(fileSizeFloat/1024) + "KB"
                        else :
                            sizeFile = str(fileSize) + "B"
                    dataSource.initNew(connection,datasourcetype='Other', physicalsourceuri=source)
                    dataSource.databaseFields.update({
                        'createdby' : self.dataDict['REMOTE_USER'],
                        'datasourcename' : filename,
                        'datasupplier' : self.dataDict['REMOTE_USER'],
                        'datasupplieddate' : date.today().isoformat(),
                        'physicalsourceuri' : physURI
                    })
                    
                    dataSource.insertDatabase(connection)
                    
                    dataSource.addFact(connection, argfactNameSpace='DATASOURCE_UPLOAD', argattributeName='File_Desc', argattributeValue=descFile, checkExisting=True)
                    dataSource.addFact(connection, argfactNameSpace='DATASOURCE_UPLOAD', argattributeName='File_Type', argattributeValue=typeFile, checkExisting=True)
                    if sizeFile != '' :
                        dataSource.addFact(connection, argfactNameSpace='DATASOURCE_UPLOAD', argattributeName='File_Size', argattributeValue=sizeFile, checkExisting=True)
                    
                    
                    datasourceList.append(dataSource)
    
    
                    # create a link to the file from the web-server
                    uploadlink = uriOb()
                    #uploadlink.initFromDatabase(uploadlsid,connection)
                    uploadlink.initNew(connection)
                    uploadlink.databaseFields.update({
                        'createdby' : self.dataDict['REMOTE_USER'],
                        'uristring' : downloadPath+'&FileName='+filename,
                        'xreflsid' : 'DATASOURCE_UPLOAD.'+foldername+'.'+filename+'.URI',
                        'visibility' : 'public',
                        'uricomment' : 'Web-address of the uploaded file, stored locally at %s'%source
                    })
                    uploadlink.insertDatabase(connection)
                    uploadlink.createLink(connection,dataSource.databaseFields['obid']\
                                          ,'Web-address of the uploaded file, stored locally at %s'%source\
                                          ,self.dataDict['REMOTE_USER'])
    
    
    
            # get or create a listob to group all files into one list (if >1 file)
            fileList = obList()
            
            # assemble the submission reasons into a readable string
            submissionReasons = {
                'transformation' : 'data transformation',
                'colleague' : 'pass on data to colleague',
                'archive' : 'archive files on server',
                'import' : 'data to be imported into database',
                'meta' : 'record only file meta-data'
            }
            submissionReason = submissionReasons[self.dataDict['reason']]
            
            #Don't want to try to init from db, as this makes list items for submissions
            # of the same name confused - if you upload to one folder, then later upload 
            # to the same folder again, the obListFact table won't show relationships 
            # correctly. Therefore, don't initFromDB for this!
    #        try:
    #            fileList.initFromDatabase(folderlsid,connection)
    #        except brdfException:
    #            fileList.initNew(connection)
    #            fileList.databaseFields.update ( {
    #                'xreflsid' : folderlsid,
    #                'createdby' : self.dataDict['REMOTE_USER'],
    #                'obkeywords' : keywords,
    #                'listname' : foldername,
    #                'listtype' : 'DATASOURCE_UPLOAD_LIST',
    #                'listdefinition' : 'List of files from the same file-upload',
    #                'currentmembership' : len(datasourceList),
    #                'listcomment' : 'This file list created as part of file submission' 
    #            })
    #            fileList.insertDatabase(connection)
            fileList.initNew(connection)
            fileList.databaseFields.update ( {
                'xreflsid' : folderlsid,
                'createdby' : self.dataDict['REMOTE_USER'],
                'obkeywords' : keywords,
                'listname' : foldername,
                'listtype' : 'DATASOURCE_UPLOAD_LIST',
                'listdefinition' : 'List of files from the same file-upload',
                'currentmembership' : len(datasourceList),
                'listcomment' : 'This file list created as part of file submission' 
            })
            fileList.insertDatabase(connection)
                
            # After files have been inesrted into db, add to fileList
            allFiles = ''
            for i in range(len(datasourceList)) :
                fileList.addListMember(datasourceList[i],"File %s added to DATASOURCE_UPLOAD_LIST %s"% \
                (datasourceList[i].databaseFields['datasourcename'],folderlsid),connection)
                allFiles += ' &nbsp; &nbsp; ' + datasourceList[i].databaseFields['datasourcename'] + '<br>\n'
            
            fileList.addFact(connection, argfactNameSpace='DATASOURCE_UPLOAD', argattributeName='Project_ID', argattributeValue=projID.upper(), checkExisting=True)
            fileList.addFact(connection, argfactNameSpace='DATASOURCE_UPLOAD', argattributeName='SubProgram', argattributeValue=self.dataDict['subProgram'], checkExisting=True)
            fileList.addFact(connection, argfactNameSpace='DATASOURCE_UPLOAD', argattributeName='Reason', argattributeValue=submissionReason, checkExisting=True)
            fileList.addFact(connection, argfactNameSpace='DATASOURCE_UPLOAD', argattributeName='Folder_Name', argattributeValue=foldername, checkExisting=True)
            fileList.addFact(connection, argfactNameSpace='DATASOURCE_UPLOAD', argattributeName='Description', argattributeValue=self.dataDict['description'], checkExisting=True)
            fileList.addFact(connection, argfactNameSpace='DATASOURCE_UPLOAD', argattributeName='Instructions', argattributeValue=self.dataDict['instructions'], checkExisting=True)
            
    
    
    
            # do some checks and append comments on anything we find
            warnings=""
            if self.dataDict['REMOTE_USER'] != self.dataDict['emailaddress']:
                comment = commentOb()
                comment.initNew(connection)
                comment.databaseFields.update({
                    'createdby' : 'system',
                    'commentstring' : "Warning - the email address given, '%s', doesn't match the user's login, '%s'"% \
                            (self.dataDict['emailaddress'], self.dataDict['REMOTE_USER']),
                    'xreflsid' : "%s.comment"%folderlsid
                })
                comment.insertDatabase(connection)
                comment.createLink(connection,fileList.databaseFields['obid'],'system','#EDA7A7')
                warnings+="<li>The system has noted that the email address given does not match your login, and this fact has been recorded in the database.\n"
            
            for i in range(len(renamedFiles)) :
                comment = commentOb()
                comment.initNew(connection)
                comment.databaseFields.update({
                    'createdby' : 'system',
                    'commentstring' : "Warning - the uploaded file '%s' was already found in the submission folder '%s'. The file was therefore renamed to '%s' in this folder."% \
                            (renamedFiles[i][0], foldername, renamedFiles[i][1]),
                    'xreflsid' : "%s.comment"%folderlsid
                })
                comment.insertDatabase(connection)
                comment.createLink(connection,fileList.databaseFields['obid'],'system','#EDA7A7')
                warnings+="<li>The file you attempted to upload, '%s', was already found in the submission folder '%s'. The file was therefore renamed to '%s'.\n"% \
                        (renamedFiles[i][0], foldername, renamedFiles[i][1])
                
            htmlResp = "Files:<br> %s have been saved to the server, and can be accessed at:<br>\n\
            &nbsp; &nbsp; <a href=\"%s\">%s</a><br>\n%s"% (allFiles,downloadPath,downloadPath,warnings)
            response = htmlModule.pageWrap('',htmlResp,'',cssLink=brdfCSSLink)
            formmodulelogger.info("sending response : \n%s"%htmlResp)
            print response
        else :
            formmodulelogger.info("submission not setup; not all regular fields set in form!")
            htmlResp = '''<strong>ERROR in submission:</strong><br>\n
            Your submission did not have all the required fields filled in!<br> &nbsp; &nbsp;
            <button type=button onClick="location.href='form.py?formname=fileSubmissionForm'">Try again</button>
            '''
            print htmlModule.pageWrap('',htmlResp,'',cssLink=brdfCSSLink)
        
        connection.close()        
        

    # method to return a response to the user
    def asResponseHTML(self):
        return " *** test response ***"

    # method to return a form to the user for editing an submission
    def asEditForm(self):
        return " *** test response ***"

    # method to return a response to the user
    def asInsertForm(self):
        formmodulelogger.info("in asInsertForm")
        connection=databaseModule.getConnection()
        # this would be called from a hyperlink like this :
        #https://sgpbioinformatics.agresearch.co.nz/cgi-bin/agbrdf/form.py?
        #context=default&formname=commentform&formstate=insert&aboutob=445360&aboutlsid=entrezgene.human.AKT3
        # obtain session token
        # get databaseFields

        self.dataDict['sessionid'] = "0"


        # obtain the user's fullname
        fullname = ''
        sql = "select fullname from staffob where xreflsid = '%s'"%self.dataDict['REMOTE_USER']
        queryCursor = connection.cursor()
        queryCursor.execute(sql)
        nameList = queryCursor.fetchall()
        if len(nameList) == 1:
            fullname = nameList[0][0]
        queryCursor.close()

        # obtain the list of existing projects
        previousProjs = []
        #previousProjs = [['SFG.005A'],['SFG.017'],['SG.107'],['SG.205'],['SG.206'],['SG.109'],['SG.103']]
        # Original SG groups
        #previousProjs = [['SFG.005A'],['SFP.017'],['SG.117'],['SG.206'],['SG.109'],['SGP.014'],['SGP.205']]
        
        sql = """
        select distinct attributevalue from oblistfact 
        where factNameSpace='DATASOURCE_UPLOAD' 
        and attributeName='Project_ID'
        """
        queryCursor = connection.cursor()
        queryCursor.execute(sql)
        projects = queryCursor.fetchall()
        for i in range(len(projects)) :
            if previousProjs.count(projects[i]) == 0 :
                previousProjs.append(projects[i])
        previousProjs.sort()
        existingProjects = reduce(lambda x,y : x + '<option value="%s">%s\n'%(y[0],y[0]),previousProjs,"")
        queryCursor.close()
        
        # obtain the list of existing folders
        sql = """
        select distinct listname from oblist 
        where xreflsid like 'DATASOURCE UPLOAD.%' 
        and listtype = 'DATASOURCE_UPLOAD_LIST'
        """
        queryCursor = connection.cursor()
        queryCursor.execute(sql)
        folders = queryCursor.fetchall()
#        existingFolders = reduce(lambda x,y : x + '<option value="%s">%s'%(y[0],y[0]),folders,"")
        folderArray = ''
        for proj in previousProjs :
            folderArray += 'folderArray["%s"] = ['%proj[0]
            for fold in folders :
                if fold[0].startswith(proj[0]) :
                    p,f = os.path.split(fold[0])
                    folderArray += '"%s",'%f
            folderArray += '"New Submission"];\n'
        queryCursor.close()
        
        myform=re.sub('__submitted_by__',fullname,form_fileSubmissionForm)
        myform=re.sub('__submitter_email_address__',"%s"%self.dataDict['REMOTE_USER'],myform)
        myform=re.sub('__EXISTING_PROJECTS__',existingProjects,myform)
        myform=re.sub('__Array_Entries__',folderArray,myform)

        
        return "Content-Type: text/html\n\n"+myform
        #connection.close()



######################################################################
#
# This form handles submissions of protocols from the microarray forms
#
######################################################################
class microarrayProtocolForm ( form ):
    """ class for microarrayProtocolForm """
    def __init__(self, dataDict):
        formmodulelogger.info("in constructor of microarrayProtocolForm")
        form.__init__(self)
        self.dataDict = dataDict
        
        if "sessionid" not in dataDict:
            print self.asInsertForm()
        else:
            formmodulelogger.info("calling processFormData")
            self.processData()
    
    def processData(self):
        # set up the database dbconnection
        dbconnection=databaseModule.getConnection()
        
        #save the data in the form to the bioProtocolOb table
        if self.dataDict.has_key('protocolName') and self.dataDict['protocolName'] != '' \
        and self.dataDict.has_key('protocolType') and self.dataDict['protocolType'] != '' \
        and self.dataDict.has_key('protocolDesc') and self.dataDict['protocolDesc'] != '' :
            formmodulelogger.info("setting up bioProtocol")
            bioProtocol = bioProtocolOb()
            bioProtocollsid = 'microarrayBioProtocol.' + self.dataDict['protocolName']
            bioProtocol.initNew(dbconnection)
            bioProtocol.databaseFields.update ({
                    'xreflsid' : bioProtocollsid,
                    'protocolname' : self.dataDict['protocolName'].strip(),
                    'protocoltype' : self.dataDict['protocolType'],
                    'protocoldescription' : self.dataDict['protocolDesc'].strip()
            })
            bioProtocol.insertDatabase(dbconnection)
            
            formmodulelogger.info("bioProtocol setup; xreflsid = " + bioProtocollsid)
            
            htmlResp = '''<p><strong>BioProtocol "%s" has been saved to the server.</strong>\n
            <p>Would you like to add another protocol, or go forward to add a subject?<p> &nbsp; &nbsp;
            <button type=button onClick="location.href='form.py?formname=MicroarrayForm1.htm'">Add Another</button> &nbsp; &nbsp;
            <button type=button onClick="location.href='form.py?formname=MicroarrayForm2.htm'">Go Forward</button>
            ''' % bioProtocollsid
            print htmlModule.pageWrap('',htmlResp,'',cssLink=brdfCSSLink)
        else :
            formmodulelogger.info("bioProtocol not setup; not all fields set in form!")
            htmlResp = '''<strong>ERROR in submission:</strong><br>\n
            Your protocol did not have all the required fields filled in!<br> &nbsp; &nbsp;
            <button type=button onClick="location.href='form.py?formname=MicroarrayForm1.htm'">Try again</button>
            '''
            print htmlModule.pageWrap('',htmlResp,'',cssLink=brdfCSSLink)
        
        dbconnection.close()
        
    
    # method to return a response to the user
    def asResponseHTML(self):
        return " *** test response ***"
    
    # method to return a response to the user
    def asEditForm(self):
        return " *** test response ***"
    
    # method to return a response to the user
    def asInsertForm(self):
        formmodulelogger.info("in asInsertForm")
        connection=databaseModule.getConnection()
        self.dataDict['sessionid'] = "0"

        # obtain the list of existing protocols and protocol types
        existingProts = ''
        existingTypes = ''
        
        sql = """
        select distinct protocolname from bioprotocolob 
        where xreflsid like 'microarrayBioProtocol.%'
        """
        queryCursor = connection.cursor()
        queryCursor.execute(sql)
        for val in queryCursor.fetchall() :
            existingProts += '<option value="%s">%s\n'%(val[0],val[0])
        queryCursor.close()
        
        sql = """
        select termname from ontologytermfact where
        ontologyob = (select obid from ontologyOb where ontologyName = 'BIOPROTOCOL_TYPES')
        """
        queryCursor = connection.cursor()
        queryCursor.execute(sql)
        for val in queryCursor.fetchall() :
            existingTypes += '<option value="%s">%s\n'%(val[0],val[0])
        queryCursor.close()
        
        myform=re.sub('<!--__EXISTING_PROTOCOLS__-->',existingProts,form_microarrayProtocolForm)
        myform=re.sub('<!--__EXISTING_PROTOCOL_TYPES__-->',existingTypes,myform)
        formmodulelogger.info("protocolForm:\n"+myform)
        

        return contentWrap(myform)
    


######################################################################
#
# This form handles submissions of subjects from the microarray forms
#
######################################################################
class microarraySubjectForm ( form ):
    """ class for microarraySubjectForm """
    def __init__(self, dataDict):
        formmodulelogger.info("in constructor of microarraySubjectForm")
        form.__init__(self)
        self.dataDict = dataDict
    
        if "sessionid" not in dataDict:
            print self.asInsertForm()
        else:
            formmodulelogger.info("calling processFormData")
            self.processData()
    
    def processData(self):
#        htmlResp = "Output from the form is:<br>\n"
#        for key in self.dataDict.keys() :
#            htmlResp += "Key = '" + key + "', value = '" + self.dataDict[key] + "'<br>\n"
#        htmlResp += '<br>To test whether the button will work:<br>&nbsp; &nbsp; \
#        <button type=button onClick="location.href=\'MicroarrayForm1.htm\'">Go to page 1</button>\
#        <button type=button onClick="back()">Go back one page</button>'
#        
#        print htmlModule.pageWrap('',htmlResp,'')
        
        # Set up the database dbconnection
        dbconnection=databaseModule.getConnection()
        
        # Save the data in the form to the bioSubjectOb table
        if self.dataDict.has_key('SubjectId') and self.dataDict['SubjectId'] != '' \
        and self.dataDict.has_key('ageDay') and self.dataDict['ageDay'] != '' \
        and self.dataDict.has_key('ageMonth') and self.dataDict['ageMonth'] != '' \
        and self.dataDict.has_key('ageYear') and self.dataDict['ageYear'] != '' \
        and self.dataDict.has_key('species') and self.dataDict['species'] != '' \
        and self.dataDict.has_key('sex') and self.dataDict['sex'] != '' :
            formmodulelogger.info("setting up bioSubject")
            bioSubject = bioSubjectOb()
            bioSubjectlsid = 'microarrayBioSubject.' + self.dataDict['SubjectId']
            bioSubjectDOB = self.dataDict['ageDay'] + "-" + self.dataDict['ageMonth'] + "-" + self.dataDict['ageYear']
            bioSubject.initNew(dbconnection)
            bioSubject.databaseFields.update ({
                'subjectname' : self.dataDict['SubjectId'],
                'xreflsid' : bioSubjectlsid,
                'subjectspeciesname' : self.dataDict['species'],
                'sex' : self.dataDict['sex'],
                'dob' : bioSubjectDOB
            })
            
            formmodulelogger.info("setting up bioSubjectFacts")
            # Iterate through attributes and put into holder
            attHolder = list()
            for i in range(int(self.dataDict["subjectAttCount"])) :
                argattributeDate = ""
                argattributeName = ""
                argattributeValue = ""
                if self.dataDict.has_key("SAT_" + str(i)) and self.dataDict["SAT_" + str(i)] != '' :
                    argattributeDate = self.dataDict["SAT_" + str(i)]
                if self.dataDict.has_key("SAN_" + str(i)) and self.dataDict["SAN_" + str(i)] != '' \
                and self.dataDict.has_key("SAV_" + str(i)) and self.dataDict["SAV_" + str(i)] != '' :
                    argattributeName = self.dataDict["SAN_" + str(i)]
                    argattributeValue = self.dataDict["SAV_" + str(i)]
                    if argattributeName == "Strain" :
                        bioSubject.databaseFields.update ({'strain' : argattributeValue})
                    else :
                        attHolder.append([argattributeDate, argattributeName, argattributeValue])
            
            bioSubject.insertDatabase(dbconnection)
            
            # Insert attributes as "facts"
            for att in attHolder :
                bioSubject.addFact(dbconnection,"MicroarraySubject_Upload", att[0], att[1], att[2])
            
            formmodulelogger.info("bioSubject setup; xreflsid = " + bioSubjectlsid)
            htmlResp = '''<p><strong>BioSubject %s has been saved to the server.</strong>\n
            <p>Would you like to add another subject, or go forward to add a sample?<p> &nbsp; &nbsp;
            <button type=button onClick="location.href='form.py?formname=MicroarrayForm2.htm'">Add Another</button> &nbsp; &nbsp;
            <button type=button onClick="location.href='form.py?formname=MicroarrayForm3.htm'">Go Forward</button>
            ''' % bioSubjectlsid
            print htmlModule.pageWrap('',htmlResp,'',cssLink=brdfCSSLink)
        else :
            formmodulelogger.info("bioSubject not setup; not all fields set in form!")
            htmlResp = '''<strong>ERROR in submission:</strong><br>\n
            Your subject did not have all the required fields filled in!<br> &nbsp; &nbsp;
            <button type=button onClick="location.href='form.py?formname=MicroarrayForm2.htm'">Try again</button>
            '''
            print htmlModule.pageWrap('',htmlResp,'',cssLink=brdfCSSLink)
            
        dbconnection.close()
        
    
    # method to return a response to the user
    def asResponseHTML(self):
        return " *** test response ***"
    
    # method to return a response to the user
    def asEditForm(self):
        return " *** test response ***"
    
    # method to return a response to the user
    def asInsertForm(self):
        formmodulelogger.info("in asInsertForm")
        connection=databaseModule.getConnection()
        self.dataDict['sessionid'] = "0"
        
        # obtain the list of existing protocols and protocol types
        existingSubs = ''
#        existingAtts = ''
        
        sql = """
        select distinct subjectname from biosubjectob
        where xreflsid like 'microarrayBioSubject.%'
        """
        queryCursor = connection.cursor()
        queryCursor.execute(sql)
        for val in queryCursor.fetchall() :
            existingSubs += '<option value="%s">%s\n'%(val[0],val[0])
        queryCursor.close()
        
#        sql = """
#        select termname from ontologytermfact where
#        ontologyob = (select obid from ontologyOb where ontologyName = 'ATTRIBUTE_TYPES')
#        """
#        queryCursor = connection.cursor()
#        queryCursor.execute(sql)
#        for val in queryCursor.fetchall() :
#            existingAtts += '<option value="%s">%s\n'%(val[0],val[0])
#        queryCursor.close()

        myform=re.sub('<!--__EXISTING_SUBJECTS__-->',existingSubs,form_microarraySubjectForm)
#        myform=re.sub('<!--__EXISTING_ATTRIBUTES__-->',existingAtts,myform)
        
        return contentWrap(myform)
    


######################################################################
#
# This form handles submissions of samples from the microarray forms
#
######################################################################
class microarraySampleForm ( form ):
    """ class for microarraySampleForm """
    def __init__(self, dataDict):
        formmodulelogger.info("in constructor of microarraySampleForm")
        form.__init__(self)
        self.dataDict = dataDict
    
        if "sessionid" not in dataDict:
            print self.asInsertForm()
        else:
            formmodulelogger.info("calling processFormData")
            self.processData()
    
    def processData(self):
        # Set up the database dbconnection
        dbconnection=databaseModule.getConnection()
        
        # Save the data in the form to the bioSampleOb table
        if self.dataDict.has_key('sampleName') and self.dataDict['sampleName'] != '' \
        and self.dataDict.has_key('sampleType') and self.dataDict['sampleType'] != '' \
        and self.dataDict.has_key('Tissue') and self.dataDict['Tissue'] != '' \
        and self.dataDict.has_key('sampleDesc') and self.dataDict['sampleDesc'] != '' \
        and self.dataDict.has_key('subject') and self.dataDict['subject'] != '' \
        and self.dataDict.has_key('protocol') and self.dataDict['protocol'] != '' :
            formmodulelogger.info("setting up bioSample")
            bioSample = bioSampleOb()
            bioSamplelsid = 'microarrayBioSample.' + self.dataDict['sampleName']
            bioSample.initNew(dbconnection)
            bioSample.databaseFields.update ({
                'samplename' : self.dataDict['sampleName'],
                'xreflsid' : bioSamplelsid,
                'sampletype' : self.dataDict['sampleType'],
                'sampletissue' : self.dataDict['Tissue'],
                'sampledescription' : self.dataDict['sampleDesc']
            })
            
            bioSample.insertDatabase(dbconnection)
            
            formmodulelogger.info("setting up bioSampleFacts")
            # Insert attributes as "facts"
            for i in range(int(self.dataDict["sampleAttCount"])) :
                argattributeName = ""
                argattributeValue = ""
                if self.dataDict.has_key("SAN_" + str(i)) and self.dataDict["SAN_" + str(i)] != '' \
                and self.dataDict.has_key("SAV_" + str(i)) and self.dataDict["SAV_" + str(i)] != '' :
                    argattributeName = self.dataDict["SAN_" + str(i)]
                    argattributeValue = self.dataDict["SAV_" + str(i)]
                    bioSample.addFact(dbconnection,"MicroarraySample_Upload", argattributeName, argattributeValue)
    
            subj = self.dataDict["subject"]
            if type(subj) == ListType :
                for i in range(len(subj)):
                    bioSubject = bioSubjectOb()
                    bioSubject.initFromDatabase('microarrayBioSubject.' + subj[i].value, dbconnection)
                    bioProtocol = bioProtocolOb()
                    bioProtocol.initFromDatabase('microarrayBioProtocol.' + self.dataDict["protocol"], dbconnection)
                    bioSampleFunclsid = bioSamplelsid+".sampling"
                    bioSample.createSamplingFunction(dbconnection, bioSubject, bioSampleFunclsid, bioProtocol)
            else :
                bioSubject = bioSubjectOb()
                bioSubject.initFromDatabase('microarrayBioSubject.' + subj, dbconnection)
                bioProtocol = bioProtocolOb()
                bioProtocol.initFromDatabase('microarrayBioProtocol.' + self.dataDict["protocol"], dbconnection)
                bioSampleFunclsid = bioSamplelsid+".sampling"
                bioSample.createSamplingFunction(dbconnection, bioSubject, bioSampleFunclsid, bioProtocol)

            formmodulelogger.info("bioSample setup; xreflsid = " + bioSamplelsid)
            htmlResp = '''<p><strong>BioSample %s has been saved to the server.</strong>\n
            <p>Would you like to add another sample, or go forward to add a file?<p> &nbsp; &nbsp;
            <button type=button onClick="location.href='form.py?formname=MicroarrayForm3.htm'">Add Another</button> &nbsp; &nbsp;
            <button type=button onClick="location.href='form.py?formname=MicroarrayForm4.htm'">Go Forward</button>
            ''' % bioSamplelsid
            print htmlModule.pageWrap('',htmlResp,'',cssLink=brdfCSSLink)
        else :
            formmodulelogger.info("bioSample not setup; not all fields set in form!")
            htmlResp = '''<strong>ERROR in submission:</strong><br>\n
            Your sample did not have all the required fields filled in!<br> &nbsp; &nbsp;
            <button type=button onClick="location.href='form.py?formname=MicroarrayForm3.htm'">Try again</button>
            '''
            print htmlModule.pageWrap('',htmlResp,'',cssLink=brdfCSSLink)
                        
        dbconnection.close()
        
    
    # method to return a response to the user
    def asResponseHTML(self):
        return " *** test response ***"
    
    # method to return a response to the user
    def asEditForm(self):
        return " *** test response ***"
    
    # method to return a response to the user
    def asInsertForm(self):
        formmodulelogger.info("in asInsertForm")
        connection=databaseModule.getConnection()
        self.dataDict['sessionid'] = "0"

        # obtain the list of existing protocols and protocol types
        existingSamples = ''
        existingTypes = ''
        existingTissues = ''
        existingSubjects = ''
        existingProtocols = ''
        
        sql = """
        select distinct samplename from biosampleob
        where xreflsid like 'microarrayBioSample.%'
        """
        queryCursor = connection.cursor()
        queryCursor.execute(sql)
        for val in queryCursor.fetchall() :
            existingSamples += '<option value="%s">%s\n'%(val[0],val[0])
        queryCursor.close()
        
        sql = """
        select termname from ontologytermfact where
        ontologyob = (select obid from ontologyOb where ontologyName = 'BIOSAMPLE_TYPES')
        """
        queryCursor = connection.cursor()
        queryCursor.execute(sql)
        for val in queryCursor.fetchall() :
            existingTypes += '<option value="%s">%s\n'%(val[0],val[0])
        queryCursor.close()
        
        sql = """
        select termname from ontologytermfact where
        ontologyob = (select obid from ontologyOb where ontologyName = 'BIOSAMPLE_TISSUES')
        """
        queryCursor = connection.cursor()
        queryCursor.execute(sql)
        for val in queryCursor.fetchall() :
            existingTissues += '<option value="%s">%s\n'%(val[0],val[0])
        queryCursor.close()

        sql = """
        select distinct subjectname from biosubjectob 
        where xreflsid like 'microarrayBioSubject.%'
        """
        queryCursor = connection.cursor()
        queryCursor.execute(sql)
        for val in queryCursor.fetchall() :
            existingSubjects += '<option value="%s">%s\n'%(val[0],val[0])
        queryCursor.close()

        sql = """
        select distinct protocolname from bioprotocolob 
        where xreflsid like 'microarrayBioProtocol.%'
        """
        queryCursor = connection.cursor()
        queryCursor.execute(sql)
        for val in queryCursor.fetchall() :
            existingProtocols += '<option value="%s">%s\n'%(val[0],val[0])
        queryCursor.close()
        
        myform=re.sub('<!--__EXISTING_SAMPLES__-->',existingSamples,form_microarraySampleForm)
        myform=re.sub('<!--__EXISTING_BIOSAMPLE_TYPES__-->',existingTypes,myform)
        myform=re.sub('<!--__EXISTING_TISSUE_TYPES__-->',existingTissues,myform)
        myform=re.sub('<!--__EXISTING_SUBJECTS__-->',existingSubjects,myform)
        myform=re.sub('<!--__EXISTING_PROTOCOLS__-->',existingProtocols,myform)
        
        return contentWrap(myform)
    


######################################################################
#
# This form handles submissions of files from the microarray forms
#
######################################################################
class microarrayFileForm ( form ):
    """ class for microarrayFileForm """
    def __init__(self, dataDict):
        formmodulelogger.info("in constructor of microarrayFileForm")
        form.__init__(self)
        self.dataDict = dataDict
        
        if "sessionid" not in dataDict:
            print self.asInsertForm()
        else:
            formmodulelogger.info("calling processFormData")
#            logString = ''
#            for key in self.dataDict.keys() :
#                logString += "key='"+key+"',  \tvalue='"+self.dataDict[key]+"'\n"
#            formmodulelogger.info("self.dataDict() contains:\n"+logString)
            self.processData()
    
    def processData(self):
        # Set up the database dbconnection
        dbconnection=databaseModule.getConnection()
        
#        htmlString = "Key/value pairs are:\n<br>"
#        for key in self.dataDict:
#            htmlString += key + " : " + str(self.dataDict[key]) + "<br>"
#        print htmlModule.pageWrap('',htmlString,'')
#        return
#        
        loopTest = []
        for i in range(int(self.dataDict['fileCount'])):
            otherTestArray = []
            if self.dataDict.has_key('otherFileCount'+str(i)) :
                for j in range(int(self.dataDict['otherFileCount'+str(i)])) :
                    tempArray = [False,False]
                    if self.dataDict.has_key('file'+str(i)+'_'+str(j)+'.filename') \
                    and self.dataDict['file'+str(i)+'_'+str(j)+'.filename'] != '' :
                        tempArray[0] = True
                    if self.dataDict.has_key('file'+str(i)+'_'+str(j)) \
                    and self.dataDict['file'+str(i)+'_'+str(j)] != '' :
                        tempArray[1] = True
                    
                    if (tempArray[0] == True and tempArray[1] == True) \
                    or (tempArray[0] == False and tempArray[1] == False) :
                        otherTestArray.append(True)
                    else :
                        otherTestArray.append(False)
            
            if otherTestArray.count(False) > 0 :
                pos = otherTestArray.index(False)
                formmodulelogger.info("submission not setup; error in image-file fields!")
                htmlResp = '''<strong>ERROR in submission:</strong><br>\n
                Your submission has an error in the "Other File" field(s) for submission number '''+(i+1)+'''.
                Other File number '''+(pos+1)+''' doesn't seem to exist, or has zero file-size!<br> &nbsp; &nbsp;
                <button type=button onClick="location.href='form.py?formname=MicroarrayForm4.htm'">Try again</button>
                '''
                print htmlModule.pageWrap('',htmlResp,'',cssLink=brdfCSSLink)
                break
            
            testArray = [False,False]
            loopTest.append(False)
            if self.dataDict.has_key('external_filename'+str(i)+'.filename') \
            and self.dataDict['external_filename'+str(i)+'.filename'] != '' :
                testArray[0] = True
            if self.dataDict.has_key('external_filename'+str(i)) \
            and self.dataDict['external_filename'+str(i)] != '' :
                testArray[1] = True

            if testArray[0] == True and testArray[1] == True :
                loopTest[i] = True
        
        if loopTest.count(False) > 0 :
            if loopTest.count(False) == 1 :
                pos = loopTest.index(False)
                formmodulelogger.info("submission not setup; not all file fields set in form!")
                htmlResp = '''<strong>ERROR in submission:</strong><br>\n
                Your submission did not have all the required fields filled in for file number '''+str(pos)+'''!<br> &nbsp; &nbsp;
                <button type=button onClick="location.href='form.py?formname=MicroarrayForm4.htm'">Try again</button>
                '''
                if self.dataDict['external_filename'+str(pos)+'.filename'] != '' \
                and self.dataDict['external_filename'+str(pos)] == '' :
                    htmlResp = '''<strong>ERROR in submission:</strong><br>\n
                    Your file-submission does not appear to have a valid file given for position '''+str(pos)+'''!<br> &nbsp; &nbsp;
                    <button type=button onClick="location.href='form.py?formname=MicroarrayForm4.htm'">Try again</button>
                    '''
                print htmlModule.pageWrap('',htmlResp,'',cssLink=brdfCSSLink)
            else :
                pos = ''
                for i in range(len(loopTest)) :
                    if loopTest[i] == False :
                        pos = ' '+int(i)+','
                pos = pos.strip(',')
                formmodulelogger.info("submission not setup; not all file fields set in form!")
                htmlResp = '''<strong>ERROR in submission:</strong><br>\n
                Your submission did not have all the required fields filled in for the files at positions:
                '''+pos+'''. If you can't seem to see where the "missing field(s)" is/are, the problem may be that 
                the file is named incorrectly.<br> &nbsp; &nbsp;
                <button type=button onClick="location.href='form.py?formname=MicroarrayForm4.htm'">Try again</button>
                '''
                print htmlModule.pageWrap('',htmlResp,'',cssLink=brdfCSSLink)
        #Set up information in the "header" - the info related to all files.
        elif self.dataDict.has_key('projectID') and self.dataDict['projectID'] != '' \
        and self.dataDict.has_key('subProgram') and self.dataDict['subProgram'] != '' \
        and self.dataDict.has_key('reason') and self.dataDict['reason'] != '' \
        and self.dataDict.has_key('expName') and self.dataDict['expName'] != '' \
        and self.dataDict.has_key('arrayName0') and self.dataDict['arrayName0'] != '' \
        and self.dataDict.has_key('pinkSample0') and self.dataDict['pinkSample0'] != '' \
        and self.dataDict.has_key('external_filename0') and self.dataDict['external_filename0'] != '' \
        and self.dataDict.has_key('experiment_description0') and self.dataDict['experiment_description0'] != '' :
            projID = self.dataDict['projectID']
            if projID == 'Other' :
                projID = self.dataDict['otherProject']
            
            # set folder-defaults
            foldername = os.path.join(projID, self.dataDict['expName'])
            if self.dataDict['expName'] == 'New Experiment' :
                foldername = os.path.join(projID, self.dataDict['otherExp'])
            folderlsid = "DATASOURCE UPLOAD.%s"%foldername
            
            # get or create the default location for storing files
            uploadPath = os.path.join(agbrdfConf.BFILE_PUTPATH, foldername)
            formmodulelogger.info("uploadPath=%s"%uploadPath)
            downloadPath = agbrdfConf.BFILE_GETPATH%foldername
            formmodulelogger.info("downloadPath=%s"%downloadPath)
            
            formmodulelogger.info("setting up staff")
            # get or create the person submitting the form
            submitter = staffOb()
            try:
                submitter.initFromDatabase(self.dataDict['REMOTE_USER'],dbconnection)
            except brdfException:
                if submitter.obState['ERROR'] == 1:
                    # could not find so create
                    submitter.initNew(dbconnection)
                    submitter.databaseFields.update ( {
                        'xreflsid' : self.dataDict['REMOTE_USER'],
                        'loginname' :  self.dataDict['REMOTE_USER'],                
                        'emailaddress' : self.dataDict['REMOTE_USER'],
                        'fullname' : self.dataDict['submittedby']
                    })
                    submitter.insertDatabase(dbconnection)
                else:
                    # some other error - re-raise
                    raise brdfException, submitter.obState['MESSAGE']
            formmodulelogger.info("set up staff")
            
            #Need to create a list to add output variables to.
            respList = []
            
            #Now start populating the database with the info from each set of files.
            for id in range(int(self.dataDict["fileCount"])) :
                if self.dataDict.has_key("external_filename" + str(id) + '.filename') \
                and self.dataDict["external_filename" + str(id) + '.filename'] != '' :
                    
                    formmodulelogger.info("setting up bioSampleList" + str(id))
                    sampleArray = list()
                    samplesNames = ['pinkSample','greenSample','blueSample','yellowSample'];
                    for i in range(int(self.dataDict['arrayType'+str(id)])):
                        sampleArray.append(self.dataDict[samplesNames[i] + str(id)])
                    # Before saving the data in the form to the geneExpressionStudy
                    #table, we'll need to create the biosampleList and labResourceList
                    sampleList = bioSampleList()
                    samplelistlsid = "microarraySampleList"
                    for i in range(len(sampleArray)) :
                        samplelistlsid += "." + sampleArray[i]
                    try :
                        sampleList.initFromDatabase(samplelistlsid,dbconnection)
                    except brdfException:
                        if sampleList.obState['ERROR'] == 1:
                            sampleList.initNew(dbconnection)
                            sampleList.databaseFields.update( {
                                'xreflsid' : samplelistlsid,
                                'listname' : samplelistlsid
                            })
                            sampleList.insertDatabase(dbconnection)
                        else:
                            raise brdfException, sampleList.obState['MESSAGE']            
                    for i in range(len(sampleArray)) :
                        sample = bioSampleOb()
                        #Shouldn't need try/catch, since all Samples are populated from the db.
                        sample.initFromDatabase("microarrayBioSample."+sampleArray[i], dbconnection)
                        sampleList.addSample(dbconnection,sample)
                    formmodulelogger.info("set up bioSampleList" + str(id))
                    
                    formmodulelogger.info("setting up labResourceOb" + str(id))
                    # Since we've only got one labResource (the type of microarray)
                    #we don't need to make a list.
                    labResource = labResourceOb()
                    labResourcelsid = "microarrayLabResource." + self.dataDict["arrayName" + str(id)]
                    try :
                        labResource.initFromDatabase(labResourcelsid,dbconnection)
                    except brdfException:
                        if labResource.obState['ERROR'] == 1:
                            labResource.initNew(dbconnection,"microarray",xreflsid=labResourcelsid)
                            labResource.insertDatabase(dbconnection)
                        else:
                            raise brdfException, labResource.obState['MESSAGE']            
                    formmodulelogger.info("set up labResourceOb" + str(id))
                    
                    # create a data import - this needs an importProcedure and a dataSource
                    formmodulelogger.info("setting up importProcedure" + str(id))
                    # get or create the import procedure
                    importProcedure = importProcedureOb()        
                    try:
                        importProcedure.initFromDatabase("importProcedure.microarrayFileForm",dbconnection)
                    except brdfException:
                        importProcedure.initNew(dbconnection)
                        importProcedure.databaseFields.update ( {
                            'xreflsid' : "importProcedure.microarrayFileForm",
                            'procedurename' : "microarrayFileForm"
                        })
                        importProcedure.insertDatabase(dbconnection)        
                    formmodulelogger.info("set up importProcedure" + str(id))
            
                    # Now process files...
                    #Need to process all "additional" files, plus results file!
                    formmodulelogger.info("setting up dataSource" + str(id))
                    # set up data source and import 
                    # import the file-data into the database
                    maxCounter = int(self.dataDict['otherFileCount' + str(id)]) + 1
                    datasourceList = []
                    keywords = self.dataDict['expName']
                    if keywords == 'New Experiment' :
                        keywords = self.dataDict['otherExp']
                    renamedFiles = []
                    gprFile = 'gprPlaceholder'
                    #Need to set the studylsid so that the file has the correct name - if duplicate!
                    studylsid = 'microarrayStudy.'+foldername+'.'
                    for i in range(maxCounter) :
                        if (i == (maxCounter - 1) and self.dataDict.has_key('external_filename'+str(id)+'.filename') \
                            and self.dataDict['external_filename' + str(id)+'.filename'] != '' ) or \
                            (i != (maxCounter - 1) and self.dataDict.has_key('file'+str(id)+'_'+str(i)+'.filename') \
                            and self.dataDict['file'+str(id)+'_'+str(i)+'.filename'] != '' ):
                            dataSource = dataSourceOb()
                            filename = self.dataDict['external_filename'+str(id)+'.filename']
                            actualFile = self.dataDict['external_filename'+str(id)]
                            typeFile = self.dataDict['IMPORT_TYPE'+str(id)]
                            checkSum = ''
                            checkSumType = ''
                            if i != (maxCounter - 1) :
                                filename = self.dataDict['file'+str(id)+'_'+str(i)+'.filename']
                                actualFile = self.dataDict['file'+str(id)+'_'+str(i)]
                                typeFile = self.dataDict['fileType'+str(id)+'_'+str(i)]
                            if i == (maxCounter - 1) \
                            and self.dataDict.has_key('checkSum'+str(id)) and self.dataDict['checkSum'+str(id)] != '' \
                            and self.dataDict.has_key('checkSumType'+str(id)) and self.dataDict['checkSumType'+str(id)] != '' :
                                checkSum = self.dataDict['checkSum'+str(id)]
                                checkSumType = self.dataDict['checkSumType'+str(id)]
                            
                            # Need to remove the folder prefixes if present (since Firefox
                            # doesn't include them, but IE6 does!)
                            slashCount = filename.count('\\')
                            if slashCount > 0 :
                                filename = filename.split('\\')[slashCount]
                            source = os.path.join(uploadPath,filename)
                            newFilename = ''
                            
                            #Need to save this file to the server.
                            fileSize = 0
                            if self.dataDict['reason'] != 'meta' :
                                _mkdir(uploadPath)
#                                formmodulelogger.info("File source: '" + source + \
#                                                      "'\nuploadPath: '" + uploadPath + \
#                                                      "'\nfilename: '" + filename + \
#                                                      "'\nfile"+str(id)+"_"+str(i)+": '" + self.dataDict['file'+str(id)+'_'+str(i)+'.filename'] + \
#                                                      "'\nexternal_filename"+str(id)+": '" + self.dataDict['external_filename'+str(id)+'.filename'] + "'")
                                if os.path.isfile(source):
                                    #File already exists!!!
                                    #Need to ensure that if there's more than one '.', it won't screw things up,
                                    # since we're putting the '(1)' before the last '.'
                                    if filename.count('.') == 0 :
                                        for j in range(1,100) :
                                            newFilename = filename+'('+str(j)+')'
                                            source = os.path.join(uploadPath,newFilename)
                                            if not os.path.isfile(source):
                                                break
                                    else :
                                        splitName = filename.split('.')
                                        newStart = ''
                                        for j in range(len(splitName)-1) :
                                            newStart += splitName[j]+'.'
                                        newStart = newStart.rstrip('.')
                                        for j in range(1,100) :
                                            newFilename = newStart+'('+str(j)+').'+splitName[len(splitName)-1]
                                            source = os.path.join(uploadPath,newFilename)
                                            if not os.path.isfile(source):
                                                break
                                        
                                    renamedFiles.append([filename,newFilename])
                                output = file(source, 'wb')
                                output.write(actualFile)
                                #Find out filesize
                                output.flush()
                                fileSize = output.tell()
                                output.close()
                            
                            keywords += ' ' + filename
                            if newFilename != '' :
                                keywords += ' ' + newFilename
                                filename = newFilename
                            
                            #If this is the GPR file, add this (corrected) filename to the studylsid
                            if i == (maxCounter - 1) :
                                studylsid += filename
                            
                            sizeFile = ''
                            if fileSize != 0 :
                                fileSizeFloat = float(fileSize)
                                if (fileSize/(1024*1024) > 1):
                                    sizeFile = '%.2f'%(fileSizeFloat/(1024*1024)) + "MB"
                                elif (fileSize/1024 > 1):
                                    sizeFile = '%.2f'%(fileSizeFloat/1024) + "KB"
                                else :
                                    sizeFile = str(fileSize) + "B"
                            dataSource.initNew(dbconnection,datasourcetype='Other', physicalsourceuri=source)
                            dataSource.databaseFields.update({
                                'createdby' : self.dataDict['REMOTE_USER'],
                                'datasourcename' : filename,
                                'datasupplier' : self.dataDict['REMOTE_USER'],
                                'datasupplieddate' : date.today().isoformat(),
                                'physicalsourceuri' : source
                            })
                            
                            dataSource.insertDatabase(dbconnection)
                            
                            formmodulelogger.info("setting up dataSourceFacts" + str(id))
                            if checkSum != '' :
                                dataSource.addFact(dbconnection, argfactNameSpace='DATASOURCE_UPLOAD', argattributeName='checkSum', argattributeValue=checkSum, checkExisting=True)
                                dataSource.addFact(dbconnection, argfactNameSpace='DATASOURCE_UPLOAD', argattributeName='checkSum_Type', argattributeValue=checkSumType, checkExisting=True)
                            dataSource.addFact(dbconnection, argfactNameSpace='DATASOURCE_UPLOAD', argattributeName='File_Type', argattributeValue=typeFile, checkExisting=True)
                            if sizeFile != '' :
                                dataSource.addFact(dbconnection, argfactNameSpace='DATASOURCE_UPLOAD', argattributeName='File_Size', argattributeValue=sizeFile, checkExisting=True)
                            formmodulelogger.info("set up dataSourceFacts" + str(id))
                            
                            datasourceList.append(dataSource)
                            if i == (maxCounter - 1) :
                                gprFile = dataSource.databaseFields['obid']
                            
                            
                            # create a link to the file from the web-server
                            uploadlink = uriOb()
                            #uploadlink.initFromDatabase(uploadlsid,dbconnection)
                            uploadlink.initNew(dbconnection)
                            uploadlink.databaseFields.update({
                                'createdby' : self.dataDict['REMOTE_USER'],
                                'uristring' : downloadPath+'&FileName='+filename,
                                'xreflsid' : 'DATASOURCE_UPLOAD.'+foldername+'.'+filename+'.URI',
                                'visibility' : 'public',
                                'uricomment' : 'Web-address of the uploaded file, stored locally at %s'%source
                            })
                            uploadlink.insertDatabase(dbconnection)
                            uploadlink.createLink(dbconnection,dataSource.databaseFields['obid']\
                                                  ,'Web-address of the uploaded file, stored locally at %s'%source\
                                                  ,self.dataDict['REMOTE_USER'])
                            
                        
                    
                    formmodulelogger.info("setting up geneExpressionStudy" + str(id))
                    study = geneExpressionStudy()
                    study.initNew(dbconnection)
                    study.databaseFields.update ({
                        'xreflsid' : studylsid,
                        'studytype' : "treated vs untreated microarray", #I presume this is right?
                        #'labresourcelist' : None, #Not using "list"; using "ob"
                        'biosamplelist' : sampleList.databaseFields['obid'],
                        #'bioprotocolob' : None, # Not used - optional parameter.
                        'labresourceob' : labResource.databaseFields['obid'],
                        'studydescription' : self.dataDict["experiment_description" + str(id)],
                        'createdby' : submitter.databaseFields['xreflsid']
                    })
                 
                    study.insertDatabase(dbconnection)
                    formmodulelogger.info("set up geneExpressionStudy" + str(id))
                    
                    formmodulelogger.info("setting up geneExpressionStudyFacts" + str(id))
                    # Insert attributes as "facts"
                    study.addFact(dbconnection, 'MicroarrayFileSubmission', 'ExperimentName', foldername)
                    study.addFact(dbconnection, 'MicroarrayFileSubmission', 'ProjectID', projID)
                    study.addFact(dbconnection, 'MicroarrayFileSubmission', 'SubProgram', self.dataDict["subProgram"])
                    formmodulelogger.info("set up geneExpressionStudyFacts" + str(id))
                                        
                    # get or create a listob to group all files into one list (if >1 file)
                    fileList = obList()
                    
                    # assemble the submission reasons into a readable string
                    submissionReasons = {
                        'transformation' : 'data transformation',
                        'colleague' : 'pass on data to colleague',
                        'archive' : 'archive files on server',
                        'import' : 'data to be imported into database',
                        'meta' : 'record only file meta-data'
                    }
                    submissionReason = submissionReasons[self.dataDict['reason']]
                    
                    fileList.initNew(dbconnection)
                    fileList.databaseFields.update ( {
                        'xreflsid' : folderlsid,
                        'createdby' : self.dataDict['REMOTE_USER'],
                        'obkeywords' : keywords,
                        'listname' : foldername,
                        'listtype' : 'DATASOURCE_UPLOAD_LIST',
                        'listdefinition' : 'List of files from the same file-upload',
                        'currentmembership' : len(datasourceList),
                        'listcomment' : 'This file list created as part of file submission' 
                    })
                    fileList.insertDatabase(dbconnection)
                        
                    # After files have been inesrted into db, add to fileList
                    allFiles = ''
                    for i in range(len(datasourceList)) :
                        fileList.addListMember(datasourceList[i],"File %s added to DATASOURCE_UPLOAD_LIST %s"% \
                        (datasourceList[i].databaseFields['datasourcename'],folderlsid),dbconnection)
                        allFiles += ' &nbsp; &nbsp; ' + datasourceList[i].databaseFields['datasourcename'] + '<br>\n'
                    
                    fileList.addFact(dbconnection, argfactNameSpace='DATASOURCE_UPLOAD', argattributeName='Project_ID', argattributeValue=projID, checkExisting=True)
                    fileList.addFact(dbconnection, argfactNameSpace='DATASOURCE_UPLOAD', argattributeName='SubProgram', argattributeValue=self.dataDict['subProgram'], checkExisting=True)
                    fileList.addFact(dbconnection, argfactNameSpace='DATASOURCE_UPLOAD', argattributeName='Reason', argattributeValue=submissionReason, checkExisting=True)
                    fileList.addFact(dbconnection, argfactNameSpace='DATASOURCE_UPLOAD', argattributeName='Folder_Name', argattributeValue=foldername, checkExisting=True)
                    
                    
                    # do some checks and append comments on anything we find
                    warnings=""
                    if self.dataDict['REMOTE_USER'] != self.dataDict['emailaddress']:
                        comment = commentOb()
                        comment.initNew(dbconnection)
                        comment.databaseFields.update({
                            'createdby' : 'system',
                            'commentstring' : "Warning - the email address given, '%s', doesn't match the user's login, '%s'"% \
                                    (self.dataDict['emailaddress'], self.dataDict['REMOTE_USER']),
                            'xreflsid' : "%s.comment"%folderlsid
                        })
                        comment.insertDatabase(dbconnection)
                        comment.createLink(dbconnection,fileList.databaseFields['obid'],'system','#EDA7A7')
                        warnings+="<li>The system has noted that the email address given does not match your login, and this fact has been recorded in the database.\n"
                    
                    for i in range(len(renamedFiles)) :
                        comment = commentOb()
                        comment.initNew(dbconnection)
                        comment.databaseFields.update({
                            'createdby' : 'system',
                            'commentstring' : "Warning - the uploaded file '%s' was already found in the submission folder '%s'. The file was therefore renamed to '%s' in this folder."% \
                                    (renamedFiles[i][0], foldername, renamedFiles[i][1]),
                            'xreflsid' : "%s.comment"%folderlsid
                        })
                        comment.insertDatabase(dbconnection)
                        comment.createLink(dbconnection,fileList.databaseFields['obid'],'system','#EDA7A7')
                        warnings+="<li>The file you attempted to upload, '%s', was already found in the submission folder '%s'. The file was therefore renamed to '%s'.\n"% \
                                (renamedFiles[i][0], foldername, renamedFiles[i][1])
                    
                    formmodulelogger.info("setting up importFunction" + str(id))
                    dataImport = importFunction()
                    dataImport.initNew(dbconnection)
                    dataImport.databaseFields.update ({
                        'xreflsid' : "import." + studylsid,
                        'datasourceob' : gprFile,
                        'importprocedureob' : importProcedure.databaseFields['obid'],
                        'ob' : study.databaseFields['obid'] #,
                        #'processinginstructions' : self.dataDict.get('post_processing_instructions',''),
                        #'submissionreasons' : submissionReason
                    })
    
                    dataImport.insertDatabase(dbconnection)
                    formmodulelogger.info("set up importFunction" + str(id))
                    
                    respList.append(((allFiles),(downloadPath),(warnings)))
                    
            str1 = ''
            str2 = respList[0][1]
            str3 = ''
            for i in range(len(respList)) :
                str1 += respList[i][0]
                str3 += respList[i][2]
            htmlResp = '''<p>The following files have been saved to the server:<br> %s
            <p>These can be accessed at:<br>\n
            &nbsp; &nbsp; <a href=\"%s\">%s</a><br>\n%s<br>
            <p>Would you like to go back to the microarray submission page, or forward to group the 
            submissions into a series?<p> &nbsp; &nbsp;
            <button type=button onClick="location.href='form.py?formname=MicroarrayForm4.htm'">Go Back</button> &nbsp; &nbsp;
            <button type=button onClick="location.href='form.py?formname=MicroarrayForm5.htm'">Go Forward</button>
            '''% (str1,str2,str2,str3)
            formmodulelogger.info("sending response : \n%s"%htmlResp)
            print htmlModule.pageWrap('',htmlResp,'',cssLink=brdfCSSLink)
        else :
            insertString = ''
            if self.dataDict.has_key('projectID') : 
                insertString += "prejectID: " + self.dataDict['projectID'] + "<br>"
            if self.dataDict.has_key('subProgram') : 
                insertString += "subProgram: " + self.dataDict['subProgram'] + "<br>"
            if self.dataDict.has_key('reason') : 
                insertString += "reason: " + self.dataDict['reason'] + "<br>"
            if self.dataDict.has_key('expName') : 
                insertString += "expName: " + self.dataDict['expName'] + "<br>"
            if self.dataDict.has_key('arrayName0') : 
                insertString += "arrayName0: " + self.dataDict['arrayName0'] + "<br>"
            if self.dataDict.has_key('pinkSample0') : 
                insertString += "pinkSample0: " + self.dataDict['pinkSample0'] + "<br>"
            if self.dataDict.has_key('external_filename0') : 
                insertString += "external_filename0: " + self.dataDict['external_filename0'] + "<br>"
            if self.dataDict.has_key('experiment_description0') : 
                insertString += "experiment_description0: " + self.dataDict['experiment_description0'] + "<br>"
            formmodulelogger.info("bioSample not setup; not all fields set in form!")
            htmlResp = '''<strong>ERROR in submission:</strong><br>\n
            Your submission did not have all the required fields filled in!<br>%s<br> &nbsp; &nbsp;
            <button type=button onClick="location.href='form.py?formname=MicroarrayForm4.htm'">Try again</button>
            '''%insertString
            print htmlModule.pageWrap('',htmlResp,'',cssLink=brdfCSSLink)

        dbconnection.close()
        
    
    # method to return a response to the user
    def asResponseHTML(self):
        return " *** test response ***"
    
    # method to return a response to the user
    def asEditForm(self):
        return " *** test response ***"
    
    # method to return a response to the user
    def asInsertForm(self):
        formmodulelogger.info("in asInsertForm")
        connection=databaseModule.getConnection()
        self.dataDict['sessionid'] = "0"

        # obtain the user's fullname
        fullname = ''
        sql = "select fullname from staffob where xreflsid = '%s'"%self.dataDict['REMOTE_USER']
        queryCursor = connection.cursor()
        queryCursor.execute(sql)
        nameList = queryCursor.fetchall()
        if len(nameList) == 1:
            fullname = nameList[0][0]
        queryCursor.close()

        # obtain the list of existing projects
        previousProjs = [['SFG.005A'],['SFG.017'],['SG.107'],['SG.205'],['SG.206'],['SG.109'],['SG.103']]
        
        sql = """
        select distinct attributevalue from oblistfact 
        where factNameSpace='DATASOURCE_UPLOAD' 
        and attributeName='Project_ID'
        """
        queryCursor = connection.cursor()
        queryCursor.execute(sql)
        projects = queryCursor.fetchall()
        for i in range(len(projects)) :
            if previousProjs.count(projects[i]) == 0 :
                previousProjs.append(projects[i])
        previousProjs.sort()
        existingProjects = reduce(lambda x,y : x + '<option value="%s">%s\n'%(y[0],y[0]),previousProjs,"")
        queryCursor.close()
        
        # obtain the list of existing folders
        sql = """
        select distinct listname from oblist 
        where xreflsid like 'DATASOURCE UPLOAD.%' 
        and listtype = 'DATASOURCE_UPLOAD_LIST'
        """
        queryCursor = connection.cursor()
        queryCursor.execute(sql)
        folders = queryCursor.fetchall()
        folderArray = ''
        for proj in previousProjs :
            folderArray += 'folderArray["%s"] = ['%proj[0]
            for fold in folders :
                if fold[0].startswith(proj[0]) :
                    p,f = os.path.split(fold[0])
                    folderArray += '"%s",'%f
            folderArray += '"New Experiment"];\n'
        queryCursor.close()

        existingSamples = ''
        sql = """
        select distinct samplename from biosampleob
        where xreflsid like 'microarrayBioSample.%'
        """
        queryCursor = connection.cursor()
        queryCursor.execute(sql)
        for val in queryCursor.fetchall() :
            existingSamples += '\'<option value="%s">%s\' +\n'%(val[0],val[0])
        queryCursor.close()
        
        myform=re.sub('__submitted_by__',fullname,form_microarrayFileForm)
        myform=re.sub('__submitter_email_address__',"%s"%self.dataDict['REMOTE_USER'],myform)
        myform=re.sub('<!--__EXISTING_PROJECTS__-->',existingProjects,myform)
        myform=re.sub('<!--__Array_Entries__-->',folderArray,myform)
        myform=re.sub('<!--__EXISTING_SAMPLES__-->',existingSamples,myform)
        
        return contentWrap(myform)
    


######################################################################
#
# This form handles submiossions of series from the microarray forms,
# which links multiple file-submissions together into a series.
#
######################################################################
class microarraySeriesForm ( form ):
    """ class for microarraySeriesForm """
    def __init__(self, dataDict):
        formmodulelogger.info("in constructor of microarraySeriesForm")
        form.__init__(self)
        self.dataDict = dataDict
        
        if "sessionid" not in dataDict:
            print self.asInsertForm()
        else:
            formmodulelogger.info("calling processFormData")
            self.processData()
   
    def processData(self):
        # set up the database dbconnection
        dbconnection=databaseModule.getConnection()

        if self.dataDict.has_key('seriesName') and self.dataDict['seriesName'] != '' \
        and self.dataDict.has_key('seriesDesc') and self.dataDict['seriesDesc'] != '' \
        and self.dataDict.has_key('submitter') and self.dataDict['submitter'] != '' \
        and self.dataDict.has_key('submissions') and self.dataDict['submissions'] != '' \
        and self.dataDict.has_key('files') and self.dataDict['files'] != '' :
        
            seriesName = self.dataDict['seriesName']
            if seriesName == "new" :
                seriesName = self.dataDict['otherSeries']
            serieslsid = 'MICROARRAY_SERIES.' + seriesName
            keywords = seriesName + " " + self.dataDict['submissions']
            description = self.dataDict["seriesDesc"]

            #Put all of the submissions into a separate list object
            submissionList = []
            subs = self.dataDict['files']
            if type(subs) != ListType :
                submissionList.append(subs)
                keywords += " " + subs
            else :
                for sub in subs :
                    submissionList.append(sub.value)
                    keywords += " " + sub.value
            
            #Create the obList for the series and populate it with the data from the form
            seriesList = obList()
            try:
                seriesList.initFromDatabase(serieslsid,dbconnection)
            except brdfException:
                seriesList.initNew(dbconnection)
                seriesList.databaseFields.update({
                    'xreflsid' : serieslsid,
                    'createdby' : self.dataDict['REMOTE_USER'],
                    'obkeywords' : keywords,
                    'listname' : seriesName,
                    'listtype' : 'MICROARRAY_SERIES_LIST',
                    'listdefinition' : 'List of microarray submissions that form a series',
                    'currentmembership' : len(submissionList),
                    'listcomment' : description,
                    'displayurl' : 'microarray.jpg'
                })
                seriesList.insertDatabase(dbconnection)
            
            for sub in submissionList :
                study = geneExpressionStudy()
                studylsid = 'microarrayStudy.'+self.dataDict['submissions']+'.'+sub
                study.initFromDatabase(studylsid.replace('\\', '\\\\'), dbconnection)
                seriesList.addListMember(study, "File %s added to MICROARRAY_SERIES_LIST %s"% \
                        (sub,seriesName), dbconnection)
            
            formmodulelogger.info("Microarray Series setup; xreflsid = " + serieslsid)
            
            htmlResp = '''<p><strong>Microarray Series "%s" has been saved to the server.</strong>\n
            <p>Would you like to add another series, or go forward to add a contrast?<p> &nbsp; &nbsp;
            <button type=button onClick="location.href='form.py?formname=MicroarrayForm5.htm'">Add Another</button> &nbsp; &nbsp;
            <button type=button onClick="location.href='form.py?formname=MicroarrayForm6.htm'">Go Forward</button>
            ''' % serieslsid
            print htmlModule.pageWrap('',htmlResp,'',cssLink=brdfCSSLink)
        else :
            formmodulelogger.info("Microarray Series not setup; not all fields set in form!")
            htmlResp = '''<strong>ERROR in submission:</strong><br>\n
            Your microarray series did not have all the required fields filled in!<br> &nbsp; &nbsp;
            <button type=button onClick="location.href='form.py?formname=MicroarrayForm5.htm'">Try again</button>
            '''
            print htmlModule.pageWrap('',htmlResp,'',cssLink=brdfCSSLink)
        
        dbconnection.close()
        
    
    # method to return a response to the user
    def asResponseHTML(self):
        return " *** test response ***"
    
    # method to return a response to the user
    def asEditForm(self):
        return " *** test response ***"
    
    # method to return a response to the user
    def asInsertForm(self):
        formmodulelogger.info("in asInsertForm")
        connection=databaseModule.getConnection()
        self.dataDict['sessionid'] = "0"

        # obtain the list of existing protocols and protocol types
        existingSeries = ''
        existingSubmitters = ''
        submissionArray = ''
        fileArray = ''
        
        # obtain a list of existing series
        sql = """
        select distinct listname from obList
        where listtype = 'MICROARRAY_SERIES_LIST'
        """
        queryCursor = connection.cursor()
        queryCursor.execute(sql)
        for val in queryCursor.fetchall() :
            existingSeries += '<option value="%s">%s\n'%(val[0],val[0])
        queryCursor.close()

        # obtain the list of users who have submitted files
        sql = """
        select distinct fullname from datasourceob, staffob
        where datasourceob.xreflsid like '/data/upload/agbrdf/%'
        and staffob.xreflsid = datasourceob.createdby
        """
        queryCursor = connection.cursor()
        queryCursor.execute(sql)
        users = queryCursor.fetchall()
        queryCursor.close()
        for user in users :
            existingSubmitters += '<option value="%s">%s\n'%(user[0],user[0])
            sql = """select distinct listname from oblist, staffob
            where oblist.listtype = 'DATASOURCE_UPLOAD_LIST'
            and staffob.xreflsid = oblist.createdby
            and staffob.fullname = '""" + user[0].replace("'", r"\'") + "'"
            submissionArray += 'subArray["'+user[0].replace("'", r"\'")+'"] = ["'
            queryCursor = connection.cursor()
            queryCursor.execute(sql)
            subs = queryCursor.fetchall()
            queryCursor.close()
            for sub in subs :
                submissionArray += '","' + sub[0].replace('\\', '\\\\\\\\')
                sql = """select distinct datasourcename 
                from geneexpressionstudy g, importfunction i, datasourceob d
                where g.obid = i.ob
                and i.datasourceob = d.obid
                and g.xreflsid like 'microarrayStudy.""" + sub[0].replace('\\', '\\\\\\\\') + "%%'"
                fileArray += 'fileArray["'+sub[0].replace('\\', '\\\\\\\\')+'"] = ["'
                queryCursor = connection.cursor()
                queryCursor.execute(sql)
                files = queryCursor.fetchall()
                queryCursor.close()
                for file in files :
                    fileArray += '","' + file[0]
                fileArray += '"];\n'
                
            submissionArray += '"];\n'
        
        myform=re.sub('<!--__EXISTING_SERIES__-->',existingSeries,form_microarraySeriesForm)
        myform=re.sub('<!--__EXISTING_SUBMITTERS__-->',existingSubmitters,myform)
        myform=re.sub('<!--__EXISTING_SUBMITTERS_ARRAY__-->',submissionArray,myform)
        myform=re.sub('<!--__EXISTING_FILE_ARRAY__-->',fileArray,myform)

        return contentWrap(myform)
    


######################################################################
#
# This form handles submiossions of series from the microarray forms,
# which links multiple file-submissions together into a series.
#
######################################################################
class microarrayContrastForm ( form ):
    """ class for microarrayContrastForm """
    def __init__(self, dataDict):
        formmodulelogger.info("in constructor of microarrayContrastForm")
        form.__init__(self)
        self.dataDict = dataDict
        
        if "sessionid" not in dataDict:
            print self.asInsertForm()
        else:
            formmodulelogger.info("calling processFormData")
            self.processData()
   
    def processData(self):
        # set up the database dbconnection
        dbconnection=databaseModule.getConnection()
        
        if self.dataDict.has_key('submission0_1') and self.dataDict['submission0_1'] != '' \
        and self.dataDict.has_key('submission0_2') and self.dataDict['submission0_2'] != '' \
        and self.dataDict.has_key('file0_1') and self.dataDict['file0_1'] != '' \
        and self.dataDict.has_key('file0_2') and self.dataDict['file0_2'] != '' \
        and self.dataDict.has_key('contrast0') and self.dataDict['contrast0'] != '' :
            formmodulelogger.info("setting up Contrast(s)")
            successString = ''
            errorString = ''
            
            for i in range(int(self.dataDict['fileCount'])) :
                formmodulelogger.info("setting up Contrast #"+str(i+1))
                subjlsid = 'microarrayStudy.'+self.dataDict['submission'+str(i)+'_1']+ \
                          '.'+self.dataDict['file'+str(i)+'_1']
                objlsid = 'microarrayStudy.'+self.dataDict['submission'+str(i)+'_2']+ \
                           '.'+self.dataDict['file'+str(i)+'_2']

#                contrasts = {
#                    'Dye-swap' : 'DYE-REVERSAL',
#                    'Low-res Scan' : 'LOW-INTENSITY-SCAN',
#                    'High-res Scan' : 'HIGH-INTENSITY-SCAN'
#                }
#                contrast = contrasts[self.dataDict['contrast'+str(i)]]
                contrast = self.dataDict['contrast'+str(i)]

                if self.dataDict['submission'+str(i)+'_1'] == '' \
                and self.dataDict['submission'+str(i)+'_2'] == '' \
                and self.dataDict['file'+str(i)+'_1'] == 'Select an experiment' \
                and self.dataDict['file'+str(i)+'_2'] == 'Select an experiment' :
                    pass
                elif self.dataDict['submission'+str(i)+'_1'] == self.dataDict['submission'+str(i)+'_2'] \
                and self.dataDict['file'+str(i)+'_1'] == self.dataDict['file'+str(i)+'_2'] :
                    formmodulelogger.info("Contrast not setup; both files are the same!!")
                    errorString += '<strong>ERROR in contrast number '+str(i+1)+''':</strong>\n
                    <br>A contrast must be created between two different files, but you've 
                    selected the same file for both.
                    <br>Submission 1 is : %s
                    <br>Submission 2 is : %s
                    <br>Contrast Type is : %s
                    <p>\n'''%(subjlsid, objlsid, contrast)
                else :
                    sub = geneExpressionStudy()
                    ob = geneExpressionStudy()
                    sub.initFromDatabase(subjlsid.replace('\\', '\\\\'),dbconnection)
                    ob.initFromDatabase(objlsid.replace('\\', '\\\\'),dbconnection)
                    
                    predicate = predicateLink()
                    predicatelsid = 'Contrast.'+contrast+'.'+subjlsid+'.'+objlsid
                    formmodulelogger.info("predicatelsid = '%s'"%predicatelsid)
                    try :
                        predicate.initFromDatabase(predicatelsid.replace('\\', '\\\\'),dbconnection)
                        formmodulelogger.info("Contrast not setup; one already created!!")
                        errorString += '<strong>ERROR in contrast number '+str(i+1)+''':</strong>\n
                        <br>A contrast of this type has already been created between the two specified files!
                        <br>Submission 1 is : %s
                        <br>Submission 2 is : %s
                        <br>Contrast Type is : %s
                        <p>\n'''%(subjlsid, objlsid, contrast)
                    except brdfException:
                        if predicate.obState['ERROR'] == 1:
                            #formmodulelogger.info("predicate ERROR: %s"%predicate.obState['MESSAGE'])
                            predicate.initNew(dbconnection)
                            predicate.databaseFields.update ({
                                    'xreflsid' : predicatelsid,
                                    'createdby' : self.dataDict['REMOTE_USER'],
                                    #'obkeywords' : None,
                                    'subjectob' : sub.databaseFields['obid'],
                                    'objectob' : ob.databaseFields['obid'],
                                    'predicatecomment' : contrast
                            })
                            predicate.insertDatabase(dbconnection)
                            successString += 'Contrast number '+str(i+1)+''' was successfully saved to the server.<p>\n'''
                            formmodulelogger.info("Contrast setup; xreflsid = " + predicatelsid)
                    
                        
            if errorString == '' :
                htmlResp = '''<p><strong>All contrasts have successfully been saved to the server.</strong>\n
                <p>Would you like to add another contrast, or go forward to add a document?<p> &nbsp; &nbsp;
                <button type=button onClick="location.href='form.py?formname=MicroarrayForm6.htm'">Add Another</button> &nbsp; &nbsp;
                <button type=button onClick="location.href='form.py?formname=MicroarrayForm7.htm'">Go Forward</button>
                '''
            else :
                htmlResp = '''<p><strong>%s</strong>\n<p>%s
                Would you like to add another contrast, or go forward to add a document?<p> &nbsp; &nbsp;
                <button type=button onClick="location.href='form.py?formname=MicroarrayForm6.htm'">Add Another</button> &nbsp; &nbsp;
                <button type=button onClick="location.href='form.py?formname=MicroarrayForm7.htm'">Go Forward</button>
                ''' % (successString, errorString)
            print htmlModule.pageWrap('',htmlResp,'',cssLink=brdfCSSLink)
        else :
            formmodulelogger.info("Contrast not setup; not all fields set in form!")
            htmlResp = '''<strong>ERROR in submission:</strong><br>\n
            Your contrast did not have all the required fields filled in!<br> &nbsp; &nbsp;
            <button type=button onClick="location.href='form.py?formname=MicroarrayForm6.htm'">Try again</button>
            '''
            print htmlModule.pageWrap('',htmlResp,'',cssLink=brdfCSSLink)
        
        dbconnection.close()
        
    
    # method to return a response to the user
    def asResponseHTML(self):
        return " *** test response ***"
    
    # method to return a response to the user
    def asEditForm(self):
        return " *** test response ***"
    
    # method to return a response to the user
    def asInsertForm(self):
        formmodulelogger.info("in asInsertForm")
        connection=databaseModule.getConnection()
        self.dataDict['sessionid'] = "0"

        # obtain the list of existing protocols and protocol types
        existingContrasts = ''
        existingSubmissions = ''
        fileArray = ''
        
        # obtain a list of existing series
        sql = """
        select termname from ontologytermfact where
        ontologyob = (select obid from ontologyOb where ontologyName = 'CONTRAST_TYPES')
        """
        queryCursor = connection.cursor()
        queryCursor.execute(sql)
        for val in queryCursor.fetchall() :
            existingContrasts += '\'<option value="%s">%s\'+\n'%(val[0],val[0])
        queryCursor.close()
        
        # obtain the list of users who have submitted files
        sql = """select distinct listname from oblist, staffob
        where oblist.listtype = 'DATASOURCE_UPLOAD_LIST'
        and staffob.xreflsid = oblist.createdby"""
        queryCursor = connection.cursor()
        queryCursor.execute(sql)
        subs = queryCursor.fetchall()
        queryCursor.close()
        for sub in subs :
            existingSubmissions += '\'<option value="%s">%s\'+\n'%(sub[0].replace('\\', '\\\\\\\\'),sub[0].replace('\\', '\\\\\\\\'))
            sql = """select distinct datasourcename 
            from geneexpressionstudy g, importfunction i, datasourceob d
            where g.obid = i.ob
            and i.datasourceob = d.obid
            and g.xreflsid like 'microarrayStudy.""" + sub[0].replace('\\', '\\\\\\\\') + "%%'"
            fileArray += 'fileArray["'+sub[0].replace('\\', '\\\\\\\\')+'"] = ["'
            queryCursor = connection.cursor()
            queryCursor.execute(sql)
            files = queryCursor.fetchall()
            queryCursor.close()
            for file in files :
                fileArray += '","' + file[0]
            fileArray += '"];\n'
        
        myform=re.sub('<!--__EXISTING_CONTRASTS__-->',existingContrasts,form_microarrayContrastForm)
        myform=re.sub('<!--__EXISTING_SUBMISSIONS__-->',existingSubmissions,myform)
        myform=re.sub('<!--__EXISTING_FILE_ARRAY__-->',fileArray,myform)

        return contentWrap(myform)
    


######################################################################
#
# This form handles submiossions of series from the microarray forms,
# which links multiple file-submissions together into a series.
#
######################################################################
class microarrayDocumentForm ( form ):
    """ class for microarrayDocumentForm """
    def __init__(self, dataDict):
        formmodulelogger.info("in constructor of microarrayDocumentForm")
        form.__init__(self)
        self.dataDict = dataDict
        
        if "sessionid" not in dataDict:
            print self.asInsertForm()
        else:
            formmodulelogger.info("calling processFormData")
            self.processData()
   
    def processData(self):
        # set up the database dbconnection
        dbconnection=databaseModule.getConnection()
        
        if ((self.dataDict.has_key('series') and self.dataDict['series'] != '') \
        or (self.dataDict.has_key('submissions') and self.dataDict['submissions'] != '' \
        and self.dataDict.has_key('file') and self.dataDict['file'] != '')) :
#        and self.dataDict.has_key('submissions1') and self.dataDict['submissions1'] != '' \
#        and self.dataDict.has_key('fileList1') and self.dataDict['fileList1'] != '' :
            formmodulelogger.info("linking Document(s)")
            successString = ''
            errorString = ''
            docList = obList()
            if self.dataDict.has_key('series') and self.dataDict['series'] != '' :
                #Link the documents to the series
                docList.initFromDatabase('MICROARRAY_SERIES.'+self.dataDict['series'],dbconnection)
            elif self.dataDict.has_key('submissions') and self.dataDict['submissions'] != '' \
            and self.dataDict.has_key('file') and self.dataDict['file'] != '':
                #Link the documents to the submission
                docList.initFromDatabase("DATASOURCE UPLOAD."+self.dataDict['submissions'].replace('\\', '\\\\'),dbconnection)
                    
            for i in range(int(self.dataDict['fileCount'])) :
                formmodulelogger.info("linking Document #"+str(i+1))
                
                if self.dataDict['submissions'+str(i+1)] == '' \
                and self.dataDict['fileList'+str(i+1)] == 'Select an experiment' :
                    pass
                elif self.dataDict['submissions'+str(i+1)] != '' and self.dataDict['fileList'+str(i+1)] == '' :
                    formmodulelogger.info("Document not linked; file not selected!!")
                    errorString += '<strong>ERROR in document number '+str(i+1)+''':</strong>\n
                    <br>The folder was selected, but  the file was not.
                    <br>Submission Folder is : %s
                    <br>Submission File is : %s
                    <p>\n'''%(self.dataDict['submissions'+str(i+1)], self.dataDict['fileList'+str(i+1)])
                else :
                    existingFiles = []
                    sql = """
                    select distinct obxreflsid from listMemberShipLink
                    where oblist = """+str(docList.databaseFields['obid'])
                    queryCursor = dbconnection.cursor()
                    queryCursor.execute(sql)
                    for res in queryCursor.fetchall() :
                        existingFiles.append(res[0])
                    queryCursor.close()
                    
                    thisFile = dataSourceOb()
                    uploadPath = os.path.join(agbrdfConf.BFILE_PUTPATH, self.dataDict['submissions'+str(i+1)])
                    filelsid = os.path.join(uploadPath,self.dataDict['fileList'+str(i+1)])
                    if existingFiles.count(filelsid) == 0 :
                        thisFile.initFromDatabase(filelsid.replace('\\', '\\\\'),dbconnection)
                        docList.addListMember(thisFile,"File %s added to this existing list via the microarray document form"% \
                                              thisFile.databaseFields['datasourcename'],dbconnection)
                        successString += 'Document number '+str(i+1)+''' was successfully linked.<p>\n'''
                        formmodulelogger.info("Document linked; xreflsid = " + filelsid)
                    else :
                        formmodulelogger.info("Document already linked to list!!")
                        errorString += '<strong>ERROR in document number '+str(i+1)+''':</strong>\n
                        <br>This file is already associated with the list!
                        <br>Submission Folder is : %s
                        <br>Submission File is : %s
                        <p>\n'''%(self.dataDict['submissions'+str(i+1)], self.dataDict['fileList'+str(i+1)])
                        
                        
            if errorString == '' :
                htmlResp = '''<p><strong>All documents have successfully been linked.</strong>\n
                <p>Would you like to link more documents, or go back to the protocol screen?<p> &nbsp; &nbsp;
                <button type=button onClick="location.href='form.py?formname=MicroarrayForm7.htm'">Link Another</button> &nbsp; &nbsp;
                <button type=button onClick="location.href='form.py?formname=MicroarrayForm1.htm'">Go back to Protocol</button>
                '''
            else :
                htmlResp = '''<p><strong>%s</strong>\n<p>%s
                Would you like to link more documents, or go back to the protocol screen?<p> &nbsp; &nbsp;
                <button type=button onClick="location.href='form.py?formname=MicroarrayForm7.htm'">Link Another</button> &nbsp; &nbsp;
                <button type=button onClick="location.href='form.py?formname=MicroarrayForm1.htm'">Go back to Protocol</button>
                ''' % (successString, errorString)
            print htmlModule.pageWrap('',htmlResp,'',cssLink=brdfCSSLink)
        else :
            formmodulelogger.info("Document not linked; not all fields set in form!")
            htmlResp = '''<strong>ERROR in submission:</strong><br>\n
            You did not have all the required fields filled in!<br> &nbsp; &nbsp;
            <button type=button onClick="location.href='form.py?formname=MicroarrayForm7.htm'">Try again</button>
            '''
            print htmlModule.pageWrap('',htmlResp,'',cssLink=brdfCSSLink)
        
        dbconnection.close()
        
    
    # method to return a response to the user
    def asResponseHTML(self):
        return " *** test response ***"
    
    # method to return a response to the user
    def asEditForm(self):
        return " *** test response ***"
    
    # method to return a response to the user
    def asInsertForm(self):
        formmodulelogger.info("in asInsertForm")
        connection=databaseModule.getConnection()
        self.dataDict['sessionid'] = "0"

        # obtain the list of existing protocols and protocol types
        existingSeries = ''
        existingSubmissions = ''
        fileArray = ''
        existingFileFolders = ''
        fileArray2 = ''
        
        # obtain a list of existing series
        sql = """
        select distinct listname from obList
        where listtype = 'MICROARRAY_SERIES_LIST'
        """
        queryCursor = connection.cursor()
        queryCursor.execute(sql)
        for val in queryCursor.fetchall() :
            existingSeries += '<option value="%s">%s\n'%(val[0],val[0])
        queryCursor.close()
        
        # obtain the list of users who have submitted files
        sql = """select distinct listname from oblist, staffob
        where oblist.listtype = 'DATASOURCE_UPLOAD_LIST'
        and staffob.xreflsid = oblist.createdby"""
        queryCursor = connection.cursor()
        queryCursor.execute(sql)
        subs = queryCursor.fetchall()
        queryCursor.close()
        for sub in subs :
            existingSubmissions += '<option value="%s">%s\n'%(sub[0].replace('\\', '\\\\'),sub[0].replace('\\', '\\\\'))
            existingFileFolders += '\'<option value="%s">%s\'+\n'%(sub[0].replace('\\', '\\\\\\\\'),sub[0].replace('\\', '\\\\\\\\'))
            sql = """select distinct datasourcename 
            from geneexpressionstudy g, importfunction i, datasourceob d
            where g.obid = i.ob
            and i.datasourceob = d.obid
            and g.xreflsid like 'microarrayStudy.""" + sub[0].replace('\\', '\\\\\\\\') + "%%'"
            fileArray += 'fileArray["'+sub[0].replace('\\', '\\\\\\\\')+'"] = ["'
            queryCursor = connection.cursor()
            queryCursor.execute(sql)
            files = queryCursor.fetchall()
            queryCursor.close()
            for file in files :
                fileArray += '","' + file[0]
            fileArray += '"];\n'
        
            # obtain a list of existing files
            sql = """
            select distinct datasourceName from datasourceOb
            where xreflsid like '%%""" + sub[0].replace('\\', '\\\\\\\\') + "%%'"
            fileArray2 += 'fileArray2["'+sub[0].replace('\\', '\\\\\\\\')+'"] = ["'
            queryCursor = connection.cursor()
            queryCursor.execute(sql)
            for val in queryCursor.fetchall() :
                fileArray2 += '","' + val[0]
            queryCursor.close()
            fileArray2 += '"];\n'
        
        myform=re.sub('<!--__EXISTING_SERIES__-->',existingSeries,form_microarrayDocumentForm)
        myform=re.sub('<!--__EXISTING_SUBMISSIONS__-->',existingSubmissions,myform)
        myform=re.sub('<!--__EXISTING_FILE_ARRAY__-->',fileArray,myform)
        myform=re.sub('<!--__EXISTING_FILE_FOLDERS__-->',existingFileFolders,myform)
        myform=re.sub('<!--__EXISTING_FILES__-->',fileArray2,myform)

        return contentWrap(myform)
    




######################################################################
#
# This forms handles submissions of 
# a form containing GPR file 
#
######################################################################
class microarrayGPRForm ( form ):
    """ class for microarray GPR form  """
    def __init__(self, dataDict):
        form.__init__(self)
        self.dataDict = dataDict


    def processData(self):

        # set up the database dbconnection
        dbconnection=databaseModule.getConnection() 


        #create and initialise the array , data source and import session
        # objects

        # first get the import Procedure
        importProcedure = importProcedureOb()
        importprocedurelsid = 'importProcedure.microarrayGPRForm'
        try :
            importProcedure.initFromDatabase(importprocedurelsid,dbconnection)
        except brdfException:
            # not found so create it
            importProcedure.initNew(dbconnection)
            importProcedure.databaseFields.update ({
                'xreflsid' : importprocedurelsid,
                'procedurename' : 'microarrayGPRForm'
            })
            importProcedure.insertDatabase(dbconnection)
            
    
        # initialise the biosamplelist 
        sampleList = bioSampleList()
        try :
            sampleList.initFromDatabase(self.dataDict['samplelistlsid'],dbconnection)
        except brdfException:
            sampleList.initNew(dbconnection)
            sampleList.databaseFields.update ({
                'xreflsid' : self.dataDict['samplelistlsid'],
                'listname' : self.dataDict['samplelistname'],
                'listcomment' : ' Note that this list needs to be linked to the samples in it (not done yet at 28/3/2006)'
            })
            sampleList.insertDatabase(dbconnection)

        
        microarray = labResourceOb()
        microarray.initFromDatabase(self.dataDict['microarraylsid'], dbconnection)


                
        # check we do not already have this
        study = geneExpressionStudy()
        try :
            study.initFromDatabase(self.dataDict['geneexpressionstudylsid'], dbconnection)
        except :
            None

        print study.obState
            
        if study.obState['NEW'] != 1:
            raise brdfException , "Error -  %s has already been set up"%self.dataDict['geneexpressionstudylsid']
        
        study.initNew(dbconnection)
        study.databaseFields.update({
            'xreflsid' : self.dataDict['geneexpressionstudylsid'],
            'labresourceob' : microarray.databaseFields['obid'],
            'studytype' : self.dataDict['studytype'],
            'biosamplelist' : sampleList.databaseFields['obid'],
            'studydescription' : self.dataDict['studydescription']
        })
        study.insertDatabase(dbconnection)

        print "setting up data source"
        dataSource = dataSourceOb()
        dataSource.initNew(connection=dbconnection, \
                       datasourcetype="GPRFile", \
                       physicalsourceuri = self.dataDict['physicalsourceuri'])
        print dataSource.databaseFields['obid']
        dataSource.insertDatabase(dbconnection)

        # set up import Function
        importFunction = microarrayExperimentImportFunction()
        importFunction.initNew(dbconnection,(dataSource,importProcedure,study))

        importFunction.runExperimentImport(dbconnection,miameDict=self.dataDict['miamefacts'],overrideGALNamecheck = self.dataDict['overrideGALNamecheck'])

        dbconnection.close()

        print importFunction.obState['MESSAGE']


    
    # method to return a response to the user
    def asResponseHTML(self):
        return " *** test response ***"

    # method to return a response to the user
    def asEditForm(self):
        return " *** test response ***"

    # method to return a response to the user
    def asInsertForm(self):
        return " *** test response ***"



######################################################################
#
# This forms handles submissions of 
# a form containing Affy CEL csv data 
#
######################################################################
class microarrayAffyForm ( form ):
    """ class for microarray Affy form  """
    def __init__(self, dataDict):
        form.__init__(self)
        self.dataDict = dataDict


    def processData(self):

        # set up the database dbconnection
        dbconnection=databaseModule.getConnection() 


        #create and initialise the array , data source and import session
        # objects

        # first get the import Procedure
        importProcedure = importProcedureOb()
        importprocedurelsid = 'importProcedure.microarrayAffyForm'
        try :
            importProcedure.initFromDatabase(importprocedurelsid,dbconnection)
        except brdfException:
            # not found so create it
            importProcedure.initNew(dbconnection)
            importProcedure.databaseFields.update ({
                'xreflsid' : importprocedurelsid,
                'procedurename' : 'microarrayAffyForm'
            })
            importProcedure.insertDatabase(dbconnection)
            
    
        # initialise the biosamplelist 
        sampleList = bioSampleList()
        try :
            sampleList.initFromDatabase(self.dataDict['samplelistlsid'],dbconnection)
        except brdfException:
            sampleList.initNew(dbconnection)
            sampleList.databaseFields.update ({
                'xreflsid' : self.dataDict['samplelistlsid'],
                'listname' : self.dataDict['samplelistname'],
                'listcomment' : ' Note that this list needs to be linked to the samples in it'
            })
            sampleList.insertDatabase(dbconnection)

        
        microarray = labResourceOb()
        microarray.initFromDatabase(self.dataDict['microarraylsid'], dbconnection)


                
        # check we do not already have this
        study = geneExpressionStudy()
        try :
            study.initFromDatabase(self.dataDict['geneexpressionstudylsid'], dbconnection)
        except :
            None

        print study.obState
            
        if study.obState['NEW'] != 1:
            raise brdfException , "Error -  %s has already been set up"%self.dataDict['geneexpressionstudylsid']
        
        study.initNew(dbconnection)
        study.databaseFields.update({
            'xreflsid' : self.dataDict['geneexpressionstudylsid'],
            'studyname' : self.dataDict['geneexpressionstudylsid'],
            'labresourceob' : microarray.databaseFields['obid'],
            'studytype' : self.dataDict['studytype'],
            'biosamplelist' : sampleList.databaseFields['obid'],
            'studydescription' : self.dataDict['studydescription']
        })
        study.insertDatabase(dbconnection)

        print "setting up data source"
        dataSource = dataSourceOb()
        dataSource.initNew(connection=dbconnection, \
                       datasourcetype=self.dataDict['datasourcetype'], \
                       physicalsourceuri = self.dataDict['physicalsourceuri'])
        print dataSource.databaseFields['obid']
        dataSource.insertDatabase(dbconnection)

        # set up import Function
        importFunction = microarrayExperimentImportFunction()
        importFunction.initNew(dbconnection,(dataSource,importProcedure,study))
        importFunction.runExperimentImport(dbconnection,lsidprefix=self.dataDict['microarraylsid'])

        dbconnection.close()

        print importFunction.obState['MESSAGE']


    
    # method to return a response to the user
    def asResponseHTML(self):
        return " *** test response ***"

    # method to return a response to the user
    def asEditForm(self):
        return " *** test response ***"

    # method to return a response to the user
    def asInsertForm(self):
        return " *** test response ***"    
    


######################################################################
#
# This forms handles submissions of 
# a form containing microarray data exported from AgResearch Oracle database
#
######################################################################
class microarrayExportForm ( form ):
    """ class for microarray GPR form  """
    def __init__(self, dataDict):
        form.__init__(self)
        self.dataDict = dataDict


    def processData(self):

        # set up the database dbconnection
        dbconnection=databaseModule.getConnection() 


        #create and initialise the array , data source and import session
        # objects

        # first get the import Procedure
        importProcedure = importProcedureOb()
        importprocedurelsid = 'importProcedure.microarrayExportForm'
        try :
            importProcedure.initFromDatabase(importprocedurelsid,dbconnection)
        except brdfException:
            # not found so create it
            importProcedure.initNew(dbconnection)
            importProcedure.databaseFields.update ({
                'xreflsid' : importprocedurelsid,
                'procedurename' : 'microarrayExportForm'
            })
            importProcedure.insertDatabase(dbconnection)
            
    
        # initialise the biosamplelist 
        sampleList = bioSampleList()
        try :
            sampleList.initFromDatabase(self.dataDict['samplelistlsid'],dbconnection)
        except brdfException:
            sampleList.initNew(dbconnection)
            sampleList.databaseFields.update ({
                'xreflsid' : self.dataDict['samplelistlsid'],
                'listname' : self.dataDict['samplelistname'],
                'listcomment' : ' Note that this list needs to be linked to the samples in it'
            })
            sampleList.insertDatabase(dbconnection)

        
        microarray = labResourceOb()
        microarray.initFromDatabase(self.dataDict['microarraylsid'], dbconnection)


                
        # check we do not already have this
        study = geneExpressionStudy()
        try :
            study.initFromDatabase(self.dataDict['geneexpressionstudylsid'], dbconnection)
        except :
            None

        print study.obState
            
        if study.obState['NEW'] != 1:
            raise brdfException , "Error -  %s has already been set up"%self.dataDict['geneexpressionstudylsid']
        
        study.initNew(dbconnection)
        study.databaseFields.update({
            'xreflsid' : self.dataDict['geneexpressionstudylsid'],
            'labresourceob' : microarray.databaseFields['obid'],
            'studytype' : self.dataDict['studytype'],
            'biosamplelist' : sampleList.databaseFields['obid'],
            'studydescription' : self.dataDict['studydescription']
        })
        study.insertDatabase(dbconnection)

        print "setting up data source"
        dataSource = dataSourceOb()
        dataSource.initNew(connection=dbconnection, \
                       datasourcetype=self.dataDict["datasourcetype"], \
                       physicalsourceuri = self.dataDict['physicalsourceuri'])
        print dataSource.databaseFields['obid']
        dataSource.insertDatabase(dbconnection)

        # set up import Function
        importFunction = microarrayExperimentImportFunction()
        importFunction.initNew(dbconnection,(dataSource,importProcedure,study))

        importFunction.runExperimentImport(dbconnection,miameDict=self.dataDict['miamefacts'],arraylsid = self.dataDict['arraylsid'])

        dbconnection.close()

        print importFunction.obState['MESSAGE']


    
    # method to return a response to the user
    def asResponseHTML(self):
        return " *** test response ***"

    # method to return a response to the user
    def asEditForm(self):
        return " *** test response ***"

    # method to return a response to the user
    def asInsertForm(self):
        return " *** test response ***"









def GPRMainAgResearch(cy5sampledata,cy3sampledata,file ,studydescription, importParms, organism='unknown'):
    """ this method is used to import microarray experiments from GPR files, with minimal 
    metadata, e.g. from the AgResearch Oracle database.
    Note that the calls to this method can be generated from the Oracle database as follows : 
select
    '    GPRMainAgResearch({ '||
    '"samplename" : "CY5.' || CY5TISSUEDESCR || '",' ||
    '"sampletissue" : "'|| CY5SAMPLEDESCR ||'",' ||
    '"sampletreatment" : "'||CY5TREATMENTDESCR||'"' ||
    '},'||
    '{'||
    '"samplename" : "CY3.' || CY3TISSUEDESCR || '",' ||
    '"sampletissue" : "'|| CY3SAMPLEDESCR ||'",' ||
    '"sampletreatment" : "'||CY3TREATMENTDESCR||'"' ||
    '},'||
    '"'||RESULTSDATAFILENAME||'",'||
    '"""'||longdescr||'""")'
from
   microarray_experiment
where
   experimentid in (:stringlist)
    """


    connection=databaseModule.getConnection()

    
    # set up the biosubject. Note that actually probably need > 1 subject, but at the moment
    # we do not know what the subject was so we use the unknown sheep
    subject = bioSubjectOb()
    subjectlsid = 'AgResearch.%s'%organism
    try :
        subject.initFromDatabase(subjectlsid,connection)
    except brdfException:
        if subject.obState['ERROR'] == 1:
            subject.initNew(connection)
            subject.databaseFields.update( {
                    'xreflsid' : subjectlsid,
                    'subjectname' : subjectlsid,
                    'subjectdescription' : 'AgResearch dummy subject record, where id of subject unknown',
                    'subjectspeciesname' : organism
            })
            subject.insertDatabase(connection)
        else:
            raise brdfException, subject.obState['MESSAGE']

    # set up the samples
    cy5sample = bioSampleOb()
    cy5samplelsid = '%s.%s'%(subject.databaseFields['xreflsid'],cy5sampledata['samplename'])
    try :
        cy5sample.initFromDatabase(cy5samplelsid,connection)
    except brdfException:
        if cy5sample.obState['ERROR'] == 1:
            cy5sample.initNew(connection)
            cy5sample.databaseFields.update(cy5sampledata)
            cy5sample.databaseFields.update( {
                    'xreflsid' : cy5samplelsid,
                    'sampletype' : 'mRNA extract for microarray experiment'
            })
            cy5sample.insertDatabase(connection)
        else:
            raise brdfException, cy5sample.obState['MESSAGE']


    cy3sample = bioSampleOb()
    cy3samplelsid = '%s.%s'%(subject.databaseFields['xreflsid'],cy3sampledata['samplename'])
    try :
        cy3sample.initFromDatabase(cy3samplelsid,connection)
    except brdfException:
        if cy3sample.obState['ERROR'] == 1:
            cy3sample.initNew(connection)
            cy3sample.databaseFields.update(cy3sampledata)
            cy3sample.databaseFields.update( {
                    'xreflsid' : cy3samplelsid,
                    'sampletype' : 'mRNA extract for microarray experiment'
            })
            cy3sample.insertDatabase(connection)
        else:
            raise brdfException, cy3sample.obState['MESSAGE']


    # set up the sample list
    sampleList = bioSampleList()
    samplelistlsid = "agresearch.microarraysamplelist.cy5:%s_cy3:%s"%(cy5sampledata['samplename'],cy3sampledata['samplename'])
    try :
        sampleList.initFromDatabase(samplelistlsid,connection)
    except brdfException:
        if sampleList.obState['ERROR'] == 1:
            sampleList.initNew(connection)
            sampleList.databaseFields.update( {
                'xreflsid' : samplelistlsid,
                'listname' : samplelistlsid
            })
            sampleList.insertDatabase(connection)
            sampleList.addSample(connection,cy5sample)
            sampleList.addSample(connection,cy3sample)
        else:
            raise brdfException, sampleList.obState['MESSAGE']            

    #update the importParms
    importParms.update({
            'physicalsourceuri' : os.path.join(importParms['physicalsourcepath'], file),
            'samplelistlsid' : samplelistlsid,
            'samplelistname' : samplelistlsid,
            'geneexpressionstudylsid' : "GeneExpressionStudy.microarray.%s"%file,
            'miamefacts' : {
                'CY3SampleLSID' : cy3samplelsid,
                'CY5SampleLSID' : cy5samplelsid,
                'CY3SampleTreatment' : cy3sampledata['sampletreatment'],
                'CY5SampleTreatment' : cy5sampledata['sampletreatment']
            },
            'studydescription' : studydescription
    })

            
    connection.commit()
    myform = microarrayGPRForm(importParms)
    myform.processData()



######################################################################
#
# This forms handles submissions of 
# a form containing GAL file 
#
######################################################################
class microarrayGALForm ( form ):
    """ class for microarray GAL form  """
    def __init__(self, dataDict):
        form.__init__(self)
        self.dataDict = dataDict


    def processData(self):

        # set up the database dbconnection
        dbconnection=databaseModule.getConnection() 


        #create and initialise the array , data source and import session
        # objects

        # first get the import Procedure
        importProcedure = importProcedureOb()
        importprocedurelsid = 'importProcedure.microarrayGALForm'
        try :
            importProcedure.initFromDatabase(importprocedurelsid,dbconnection)
        except brdfException:
            # not found so create it
            importProcedure.initNew(dbconnection)
            importProcedure.databaseFields.update ({
                'xreflsid' : importprocedurelsid,
                'procedurename' : 'microarrayGALForm'
            })
            importProcedure.insertDatabase(dbconnection)
            
    
        resource = labResourceOb()
        resource.initNew(connection = dbconnection,\
                     resourcetype = self.dataDict["resourcetype"], \
                     xreflsid = self.dataDict['xreflsid'], \
                     resourcedescription = self.dataDict['resourcedescription'] )
   
    
        dataSource = dataSourceOb()
        dataSource.initNew(connection=dbconnection, \
                       datasourcetype=self.dataDict['datasourcetype'], \
                       physicalsourceuri = self.dataDict['physicalsourceuri'])

    
        importSession = labResourceImportFunction()
        importSession.initNew(connection=dbconnection, \
                          obtuple=(dataSource,importProcedure,resource))
                          
        # 2/2011 not needed for all imports 
        importSession.headerDict = {
           'gal_type' : 'Agilent (GEO)',
           'gal_blockcount' : 0,
           'gal_blocktype' : 0,
           'gal_block1' : 0
        }

        importSession.runArrayImport(dbconnection)


        dbconnection.close()

    
    # method to return a response to the user
    def asResponseHTML(self):
        return " *** test response ***"

    # method to return a response to the user
    def asEditForm(self):
        return " *** test response ***"

    # method to return a response to the user
    def asInsertForm(self):
        return " *** test response ***"


######################################################################
#
# This forms handles submissions of 
# blast runs to the database
#
######################################################################
class databaseSearchImportForm ( form ):
    """ class for blast import form  """
    def __init__(self, dataDict):
        form.__init__(self)
        self.dataDict = dataDict
        formmodulelogger.info("databaseSearchImportForm initialised with %s"%str(dataDict))


    def processData(self):

        # set up the database dbconnection
        dbconnection=databaseModule.getConnection() 


        #create and initialise the array , data source and import session
        # objects

        # first get the import Procedure
        importProcedure = importProcedureOb()
        importprocedurelsid = 'importProcedure.blastImportForm'
        try :
            importProcedure.initFromDatabase(importprocedurelsid,dbconnection)
        except brdfException:
            # not found so create it
            importProcedure.initNew(dbconnection)
            importProcedure.databaseFields.update ({
                'xreflsid' : importprocedurelsid,
                'procedurename' : 'blastImportForm'
            })
            importProcedure.insertDatabase(dbconnection)
            
    
        # initialise the biodatabase - should already be set up but if not create
        blastDatabase = bioDatabaseOb()
        try:
            blastDatabase.initFromDatabase(self.dataDict['databaselsid'],dbconnection)
        except brdfException:
            if blastDatabase.obState['ERROR'] == 1:
                # could not find so create
                blastDatabase.initNew(dbconnection)
                blastDatabase.databaseFields.update ( {
                    'xreflsid' : self.dataDict['databaselsid'],
                    'databasename' : self.dataDict['databaselsid']    ,
                    'databasetype' : 'Protein Sequence database'
                })
                blastDatabase.insertDatabase(dbconnection)
            else:
                # some other error - re-raise
                raise brdfException, blastDatabase.obState['MESSAGE']


        # initialise the database search protocol - should already be set up but if not create
        blastProtocol = bioProtocolOb()
        try:
            blastProtocol.initFromDatabase(self.dataDict['blastprotocollsid'],dbconnection)
        except brdfException:
            if blastProtocol.obState['ERROR'] == 1:
                # could not find so create
                blastProtocol.initNew(dbconnection)
                blastProtocol.databaseFields.update ( {
                    'xreflsid' : self.dataDict['blastprotocollsid'],
                    'protocolname' : self.dataDict['blastprotocollsid'],
                    'protocoltype' : 'BLAST SEARCH'
                })
                blastProtocol.insertDatabase(dbconnection)
            else:
                # some other error - re-raise
                raise brdfException, blastProtocol.obState['MESSAGE']            

                
        # create a database search study
        studylsid = "DatabaseSearch.%s.%s"%(blastDatabase.databaseFields['xreflsid'],blastProtocol.databaseFields['xreflsid'])
        study = databaseSearchStudy()
        try :
            study.initFromDatabase(studylsid, dbconnection)
            study.updateDatabase(dbconnection)
        except brdfException, msg :
            if study.obState['ERROR'] == 1:
                study.initNew(dbconnection)
                study.databaseFields.update({
                    'xreflsid' : studylsid,
                    'studytype' : self.dataDict['studytype'],
                    'studyname' : studylsid,
                    'bioprotocolob' : blastProtocol.databaseFields['obid'],
                    'biodatabaseob' : blastDatabase.databaseFields['obid'],
                    'studydescription' : self.dataDict['studydescription']
                })
                study.insertDatabase(dbconnection)
            else:
                raise brdfException(msg)


        # set up the data source
        dataSource = dataSourceOb()
        dataSource.initNew(connection=dbconnection, \
                       datasourcetype=self.dataDict['datasourcetype'], \
                       physicalsourceuri = self.dataDict['physicalsourceuri'])
        dataSource.insertDatabase(dbconnection)




        # set up import Function
        importFunction = databaseSearchImportFunction()
        importFunction.initNew(dbconnection,(dataSource,importProcedure,study))
        importFunction.insertDatabase(dbconnection)


        # assign default values
        if 'annotateGenomeMapping' not in self.dataDict:
            self.dataDict['annotateGenomeMapping'] = False
            
        if 'hitimportlimit' in self.dataDict and self.dataDict['annotateGenomeMapping']:
            importFunction.runStudyImport(dbconnection,querylsidprefix=self.dataDict['queryPrefix'], \
                                      subjectlsidprefix=self.dataDict['hitPrefix'], \
                                      subjectparseregexp=self.dataDict['hitAccessionRegexp'],\
                                      checkExistingHits = self.dataDict['checkExistingHits'],\
                                      createMissingQueries = self.dataDict['createMissingQueries'],\
                                      createMissingHits = self.dataDict['createMissingHits'],\
                                      newQuerySequenceType = self.dataDict['querySequenceType'],\
                                      newHitSequenceType = self.dataDict['hitSequenceType'],\
                                      queryparseregexp=self.dataDict['queryAccessionRegexp'],\
                                      fieldNamesRow=self.dataDict['fieldNamesRow'], \
                                      fileFormat=self.dataDict['fileFormat'], \
                                      hitimportlimit=self.dataDict['hitimportlimit'],\
                                      alignmentimportlimit=self.dataDict['alignmentimportlimit'],\
                                      hspcountforrepeat=self.dataDict['hspcountforrepeat'],\
                                      adjustedevaluecutoff =self.dataDict['adjustedevaluecutoff'],\
                                      singlehitevaluecutoff =self.dataDict['singlehitevaluecutoff'],\
                                      locationMapDetails = self.dataDict['locationMapDetails'],\
                                      annotateGenomeMapping = self.dataDict['annotateGenomeMapping'],\
                                      queryTableColumn = self.dataDict['queryTableColumn'],\
                                      cacheQueryList = self.dataDict['cacheQueryList'],\
                                      cacheHitList = self.dataDict['cacheHitList'])
        elif 'hitimportlimit' in self.dataDict:
            importFunction.runStudyImport(dbconnection,querylsidprefix=self.dataDict['queryPrefix'], \
                                      subjectlsidprefix=self.dataDict['hitPrefix'], \
                                      subjectparseregexp=self.dataDict['hitAccessionRegexp'],\
                                      checkExistingHits = self.dataDict['checkExistingHits'],\
                                      createMissingQueries = self.dataDict['createMissingQueries'],\
                                      createMissingHits = self.dataDict['createMissingHits'],\
                                      newQuerySequenceType = self.dataDict['querySequenceType'],\
                                      newHitSequenceType = self.dataDict['hitSequenceType'],\
                                      queryparseregexp=self.dataDict['queryAccessionRegexp'],\
                                      fieldNamesRow=self.dataDict['fieldNamesRow'], \
                                      fileFormat=self.dataDict['fileFormat'], \
                                      hitimportlimit=self.dataDict['hitimportlimit'],\
                                      alignmentimportlimit=self.dataDict['alignmentimportlimit'],\
                                      annotateGenomeMapping = self.dataDict['annotateGenomeMapping'])

	else:
            importFunction.runStudyImport(dbconnection,querylsidprefix=self.dataDict['queryPrefix'], \
                                      subjectlsidprefix=self.dataDict['hitPrefix'], \
                                      subjectparseregexp=self.dataDict['hitAccessionRegexp'],\
                                      checkExistingHits = self.dataDict['checkExistingHits'],\
                                      createMissingQueries = self.dataDict['createMissingQueries'],\
                                      createMissingHits = self.dataDict['createMissingHits'],\
                                      newQuerySequenceType = self.dataDict['querySequenceType'],\
                                      newHitSequenceType = self.dataDict['hitSequenceType'],\
                                      queryparseregexp=self.dataDict['queryAccessionRegexp'],\
                                      fieldNamesRow=self.dataDict['fieldNamesRow'], \
                                      fileFormat=self.dataDict['fileFormat'])





        dbconnection.close()

        print importFunction.obState['MESSAGE']


    
    # method to return a response to the user
    def asResponseHTML(self):
        return " *** test response ***"

    # method to return a response to the user
    def asEditForm(self):
        return " *** test response ***"

    # method to return a response to the user
    def asInsertForm(self):
        return " *** test response ***"

def AgResearchExportMain(cy5sampledata,cy3sampledata,file ,studydescription,arraylsid,experimentid):

    connection=databaseModule.getConnection()

    # set up the cy5 biosubject. 
    cy5subject = bioSubjectOb()
    organism = 'Ovis aries'
    subjectDict = cy5sampledata['samplesubject']
    subjectlsid = 'AgResearch.%s'%subjectDict['name']
    try :
        cy5subject.initFromDatabase(subjectlsid,connection)
    except brdfException:
        if cy5subject.obState['ERROR'] == 1:
            cy5subject.initNew(connection)
            cy5subject.databaseFields.update( {
                    'xreflsid' : subjectlsid,
                    'subjectname' : subjectDict['name'],
                    'subjectspeciesname' : organism,
                    'sex' : subjectDict['sex']
            })
            cy5subject.insertDatabase(connection)
        else:
            raise brdfException, cy5subject.obState['MESSAGE']        
    

    # set up the samples
    cy5sample = bioSampleOb()
    cy5samplelsid = '%s.%s'%(cy5subject.databaseFields['xreflsid'],cy5sampledata['samplename'])
    try :
        cy5sample.initFromDatabase(cy5samplelsid,connection)
    except brdfException:
        if cy5sample.obState['ERROR'] == 1:
            cy5sample.initNew(connection)
            cy5sample.databaseFields.update(cy5sampledata)
            cy5sample.databaseFields.update( {
                    'xreflsid' : cy5samplelsid,
                    'sampletype' : 'mRNA extract for microarray experiment'
            })
            cy5sample.insertDatabase(connection)
            cy5sample.createSamplingFunction(connection, cy5subject, "%s.sampling"%cy5samplelsid)            
        else:
            raise brdfException, cy5sample.obState['MESSAGE']

        # link to the cy5 animal - create if necessary

    # set up the cy3 biosubject. 
    cy3subject = bioSubjectOb()
    organism = 'Bos taurus'
    subjectDict = cy3sampledata['samplesubject']
    subjectlsid = 'AgResearch.%s'%subjectDict['name']
    try :
        cy3subject.initFromDatabase(subjectlsid,connection)
    except brdfException:
        if cy3subject.obState['ERROR'] == 1:
            cy3subject.initNew(connection)
            cy3subject.databaseFields.update( {
                    'xreflsid' : subjectlsid,
                    'subjectname' : subjectDict['name'],
                    'subjectspeciesname' : organism,
                    'sex' : subjectDict['sex']
            })
            cy3subject.insertDatabase(connection)
        else:
            raise brdfException, cy3subject.obState['MESSAGE']        


    cy3sample = bioSampleOb()
    cy3samplelsid = '%s.%s'%(cy3subject.databaseFields['xreflsid'],cy3sampledata['samplename'])
    try :
        cy3sample.initFromDatabase(cy3samplelsid,connection)
    except brdfException:
        if cy3sample.obState['ERROR'] == 1:
            cy3sample.initNew(connection)
            cy3sample.databaseFields.update(cy3sampledata)
            cy3sample.databaseFields.update( {
                    'xreflsid' : cy3samplelsid,
                    'sampletype' : 'mRNA extract for microarray experiment'
            })
            cy3sample.insertDatabase(connection)
            cy3sample.createSamplingFunction(connection, cy3subject, "%s.sampling"%cy3samplelsid)
        else:
            raise brdfException, cy3sample.obState['MESSAGE']


        


    # set up the sample list
    sampleList = bioSampleList()
    samplelistlsid = "%s:%s"%(cy5samplelsid,cy3samplelsid)
    try :
        sampleList.initFromDatabase(samplelistlsid,connection)
    except brdfException:
        if sampleList.obState['ERROR'] == 1:
            sampleList.initNew(connection)
            sampleList.databaseFields.update( {
                'xreflsid' : samplelistlsid,
                'listname' : samplelistlsid
            })
            sampleList.insertDatabase(connection)
            sampleList.addSample(connection,cy5sample)
            sampleList.addSample(connection,cy3sample)
        else:
            raise brdfException, sampleList.obState['MESSAGE']            
            
    importParms = {
            'samplelistlsid' : samplelistlsid,
            'samplelistname' : samplelistlsid,
            'microarraylsid' : arraylsid,
            'geneexpressionstudylsid' : "GeneExpressionStudy.microarray.%s"%file,
            'datasourcetype' : "AgResearchArrayExport1",
            'physicalsourceuri' : "/home/seqstore/agbrdf/arrayport/%s"%file,
            'studytype' : 'treated vs untreated microarray',
            'miamefacts' : {
                'CY3SampleLSID' : cy3samplelsid,
                'CY5SampleLSID' : cy5samplelsid,
                'CY3SampleTreatment' : cy3sampledata['sampletreatment'],
                'CY5SampleTreatment' : cy5sampledata['sampletreatment'],
                'experimentid' : experimentid
            },
            'studydescription' : studydescription,
            'experimentid' : experimentid,
            'arraylsid' : arraylsid
    }    

    connection.commit()
    myform = microarrayExportForm(importParms)
    myform.processData()

    
    
    
def BlastImportMain():

#-rw-r----- 1 seqstore users 15109546 Jun 13 11:30 Bovine_target.fa_BTGI.091806.csv
#-rw-r----- 1 seqstore users  9054560 Jun 13 11:30 Bovine_target.fa_cs34.seq.csv
#-rw-r----- 1 seqstore users  1896634 Jun 13 11:30 Bovine_target_vs_bovine_glean5_cds.csv
#-rw-r----- 1 seqstore users  5684155 Jun 13 11:30 Bovine_target_vs_bt.fna.csv
#-rw-r----- 1 seqstore users  5186565 Jun 13 11:30 Bovine_target_vs_hs.fna.csv
#-rw-r----- 1 seqstore users  3313895 Jun 13 11:30 Bovine_target_vs_mouse.fna.csv
#-rw-r----- 1 seqstore users 12651268 Jun 13 10:42 NR0001.csv
#-rw-r----- 1 seqstore users 12685515 Jun 13 10:42 NR0002.csv
#-rw-r----- 1 seqstore users 12719722 Jun 13 10:42 NR0003.csv
#-rw-r----- 1 seqstore users 12723283 Jun 13 10:42 NR0004.csv
#/data/home/seqstore/agbrdf/affy
# example of query name in file : target:Bovine:Bt.1187.1.S1_at;
# example of query lsid in db : Affymetrix.target:Bovine:Bt.1187.1.S1_at
# cs39.seq_nr.csv
# sheepEST.fa_hs.fna.csv

#835,"gi|62851719|gb|DN881764.1|DN881764","ref|NM_018657.3|",3,3178,"ref|NM_018657.3| Homo sapiens myoneurin (MYNN), mRNA","51.9","1e-44",27,50,31,0,372,521,27 28,2877,""
#835,"gi|62851719|gb|DN881764.1|DN881764","ref|NM_018657.3|",3,3178,"ref|NM_018657.3| Homo sapiens myoneurin (MYNN), mRNA","51.9","1e-44",18,28,22,0,507,590,28 64,2947,""
#"gi|126723152|ref|NM_001082285.1|"
#"gi|2707658|gb|AF029933.1|"
#"gi|1150519|emb|Z49747.1|"
#"gi|105300307|dbj|AB235199.1|"
#dbj
#emb
#gb
#ref

#-rw-r----- 1 seqstore users 159385394 Oct  1 17:03 mammVSplatypus_paralign_tab.out
#-rw-r----- 1 seqstore users  74190538 Oct  1 17:03 platypusVSmamm_paralign_tab.out
#-rw-r----- 1 seqstore users  45516105 Sep 14 09:59 wallabyVSmamm_paralign_tab.out

#ENSBTAP00000023671 Btar:1k48 EOG7001QQ  gi|undefined    gnl|BL_ORD_ID|17661 ENSOANP00000001749 pep:novel ultracontig:OANA5:Ultra70:1086099:1099311:1 gene:ENSOANG00000001101 transcript:ENSOANT00000001750    287     1186    0       284     242     247     5       12      12      291     12      287
#ENSBTAP00000023671 Btar:1k48 EOG7001QQ  gi|undefined    gnl|BL_ORD_ID|17662 ENSOANP00000001750 pep:novel ultracontig:OANA5:Ultra70:1087657:1099223:1 gene:ENSOANG00000001101 transcript:ENSOANT00000001751    197     988     0       215     196     196     1       18      77      291     1       197

#HWW-T7500-010_0001_7_1_100_1080hash0slash1      Chr27   92.93   99      7       0       1       99      29586119        29586217        8e-34   147
#HWW-T7500-010_0001_7_1_100_1080hash0slash2      Chr27   95.79   95      4       0       6       100     29586260        29586166        5e-36   154
#HWW-T7500-010_0001_7_1_100_1104hash0slash1      Chr27   95.00   100     5       0       1       100     2759377 2759278 5e-37   158
#
# s_7_sample200000.fa.masked_umd3.results.rewritten

#[seqstore@impala agbrdf]$ head /data/databases/flatfile/bfiles/agbrdf/temp/human_estsVS_placentation_candidates.out.parsed
#873,"gnl|UG|Hs#S15583008","ENSP00000264870",1,732,"ENSP00000264870 Hsap:bvtc EOG7RFM27","531","1e-153",259,266,260,0,76,873,1,266,""
#818,"gnl|UG|Hs#S15583113","ENSP00000299421",2,452,"ENSP00000299421 Hsap:fjbn EOG78D12N","286","1e-103",148,195,149,0,233,817,46,240,""
#818,"gnl|UG|Hs#S15583113","ENSP00000299421",1,452,"ENSP00000299421 Hsap:fjbn EOG78D12N","286","1e-103",44,44,44,0,97,228,1,44,""
#865,"gnl|UG|Hs#S15583170","ENSP00000223061",3,449,"ENSP00000223061 Hsap:ttj3 EOG7Q8551","351","1e-98",171,219,174,0,3,659,80,298,""

#-rw-r----- 1 seqstore users 193058713 Nov 23 19:13 /data/databases/flatfile/bfiles/agbrdf/temp/all_human_placental_ESTs.fa
#-rw-r--r-- 1 seqstore users   1070159 Dec  2 10:32 /data/databases/flatfile/bfiles/agbrdf/temp/human_estsVS_placentation_candidates.out.parsed
#-rwxr--r-- 1 seqstore users   1525244 Nov 18 09:56 /data/databases/flatfile/bfiles/agbrdf/temp/placentation_candidates_human_edited_blast_ESTs_out.parsed
#-rwxr--r-- 1 seqstore users    543052 Oct 14 10:51 /data/databases/flatfile/bfiles/agbrdf/temp/placentation_candidates_human_edited.fa
#[seqstore@impala agbrdf]$ vi


#490,"ENSP00000373166","gnl|UG|Hs#S29180925","Minus / Plus",583,"gnl|UG|Hs#S29180925 DA857259 PLACE7 Homo sapiens cDNA clone PLACE7008508 5', mRNA sequence /cl
#one=PLACE7008508 /clone_end=5' /gb=DA857259 /gi=82333909 /ug=Hs.594171 /len=583 /lib=18484","406","1e-113",193,193,0,197,389,3,581,""
#490,"ENSP00000373166","gnl|UG|Hs#S15532584","Minus / Minus",1051,"gnl|UG|Hs#S15532584 BX334473 Homo sapiens PLACENTA COT 25-NORMALIZED Homo sapiens cDNA clone
# CS0DI003YM14 3-PRIME, mRNA sequence /clone=CS0DI003YM14 /clone_end=3' /gb=BX334473 /gi=46281015 /ug=Hs.25544 /len=1051 /lib=13021","202","4e-70",101,180,3,22
#9,405,427,966,""

#[seqstore@impala agbrdf]$ head /data/databases/flatfile/bfiles/agbrdf/temp/bov_estsVs_placentation_candidates.out.parsed
#364,"000420BPLA002360HT","ENSP00000363064",1,570,"ENSP00000363064 Hsap:z37t EOG7B8JNP","132","3e-33",56,109,72,0,37,363,222,330,""
#364,"000420BPLA002360HT","ENSP00000363064",1,570,"ENSP00000363064 Hsap:z37t EOG7B8JNP","132","1e-28",49,105,65,0,37,351,162,266,""
#364,"000420BPLA002360HT","ENSP00000363064",1,570,"ENSP00000363064 Hsap:z37t EOG7B8JNP","132","1e-21",42,109,60,2,37,363,252,358,""
#[seqstore@impala agbrdf]$
#[seqstore@impala agbrdf]$
#[seqstore@impala agbrdf]$ head /data/databases/flatfile/bfiles/agbrdf/temp/placentation_candidatesVS_bov_ests.out.parsed
#503,"ENSP00000371347","000326BPLA999094HT","Minus / Plus",608,"000326BPLA999094HT ","126","2e-31",76,185,15,331,500,4,549,""
#342,"ENSP00000368183","000416BPLA001189HT","Minus / Plus",381,"000416BPLA001189HT ","227","5e-62",110,123,0,1,123,13,381,""
#570,"ENSP00000363064","000420BPLA002360HT","Minus / Plus",364,"000420BPLA002360HT ","126","2e-31",56,109,0,222,330,37,363,""

#[seqstore@impala agbrdf]$ head  -3 /data/databases/flatfile/bfiles/agbrdf/temp/ZFinchVsAE_prots.tab.out
#ENSTGUP00000000650 pep:known chromosome:taeGut3.2.4:LG5:10219:13106:1 gene:ENSTGUG00000000642 transcript:ENSTGUT00000000661     gi|undefined    gnl|BL_ORD_ID|1270 ENSG00000145819|ENSP00000389216    235     130     9e-10   121     34      59      2       6       13      129     16      134
#ENSTGUP00000000650 pep:known chromosome:taeGut3.2.4:LG5:10219:13106:1 gene:ENSTGUG00000000642 transcript:ENSTGUT00000000661     gi|undefined    gnl|BL_ORD_ID|514 ENSG00000075884|ENSP00000295095     475     119     4e-08   103     35      52      3       12      16      111     348     445
#ENSTGUP00000017630 pep:novel chromosome:taeGut3.2.4:24_random:721:4535:-1 gene:ENSTGUG00000017353 transcript:ENSTGUT00000018032 gi|undefined    gnl|BL_ORD_ID|165 ENSG00000084463|ENSP00000261167     641     130     8e-09   140     48      52      5       19      186     325     400     520
#[seqstore@impala agbrdf]$ head -3 /data/databases/flatfile/bfiles/agbrdf/temp/AExpress_protsVSZFinch.tab.out
#ENSG00000013275|ENSP00000157812 gi|undefined    gnl|BL_ORD_ID|8801 ENSTGUP00000012822 pep:known chromosome:taeGut3.2.4:5:44619152:44627430:1 gene:ENSTGUG00000012452 transcript:ENSTGUT00000012968    439     1005    0       369     186     282     1       2       46      412     63      431
#ENSG00000013275|ENSP00000157812 gi|undefined    gnl|BL_ORD_ID|8498 ENSTGUP00000010738 pep:known chromosome:taeGut3.2.4:5:21423762:21430899:1 gene:ENSTGUG00000010400 transcript:ENSTGUT00000010851    426     810     1e-87   400     159     246     1       20      38      417     26      425
#ENSG00000013275|ENSP00000157812 gi|undefined    gnl|BL_ORD_ID|9008 ENSTGUP00000013497 pep:known chromosome:taeGut3.2.4:5:59829413:59839999:-1 gene:ENSTGUG00000013103 transcript:ENSTGUT00000013650   361     795     6e-86   353     154     230     0       0       61      413     1       353

#[seqstore@impala agbrdf]$ head /data/databases/flatfile/bfiles/agbrdf/temp/PlatypusVsAExpressProts.tab.out
#ENSOANP00000028580 pep:novel supercontig:OANA5:Contig216494:3:359:1 gene:ENSOANG00000022395 transcript:ENSOANT00000032376       gi|undefined    gnl|BL_ORD_ID|354 ENSG00000171944|ENSP00000303469     316     112     1e-07   72      26      37      0       0       1       72      61      132
#ENSOANP00000005996 pep:novel supercontig:OANA5:Contig219926:14:367:-1 gene:ENSOANG00000003782 transcript:ENSOANT00000005998     gi|undefined    gnl|BL_ORD_ID|52 ENSG00000105329|ENSP00000221930      390     188     2e-16   93      43      60      2       6       18      109     27      114
#ENSOANP00000017723 pep:known supercontig:OANA5:Contig126960:108:317:1 gene:ENSOANG00000011188 transcript:ENSOANT00000017726     gi|undefined    gnl|BL_ORD_ID|1

#-rwxrwxrwx 1 smithiesr  users 3.8M Dec 10 09:22 /data/agbio/spool/cs39.bt.csv.gz*
#-rwxrwxrwx 1 smithiesr  users 3.4M Dec 10 09:22 /data/agbio/spool/cs39.hs.csv.gz*
#-rwxrwxrwx 1 smithiesr  users  16M Dec 10 09:22 /data/agbio/spool/est.bt.csv.gz*
#-rwxrwxrwx 1 smithiesr  users  17M Dec 10 09:22 /data/agbio/spool/est.hs.csv.gz*

#/data/home/seqstore/agbrdf/blastresults
#-rw-r----- 1 seqstore users 123762014 Nov  7 21:43 EG01Contigs.masked_vs_plantprotein_FF_e-20.csv
#-rw-r----- 1 seqstore users   3728589 Nov  7 21:43 EG01Contigs.masked_vs_plantrna_FF_e-20.csv
#-rw-r----- 1 seqstore users 161945225 Nov  7 21:43 EG01Contigs_vs_plantprotein_FF_e-20.csv
#-rw-r----- 1 seqstore users  21048776 Nov  7 21:43 EG01Contigs_vs_plantrna_FF_e-20.csv
#-rw-r----- 1 seqstore users 195735638 Nov  7 21:43 EG01Singlets.masked_vs_plantprotein_FF_e-20.csv
#-rw-r----- 1 seqstore users   7575989 Nov  7 21:43 EG01Singlets.masked_vs_plantrna_FF_e-20.csv
#-rw-r----- 1 seqstore users 260223271 Nov  7 21:43 EG01Singlets_vs_plantprotein_FF_e-20.csv
#-rw-r----- 1 seqstore users 145839952 Nov  7 21:43 EG01Singlets_vs_plantrna_FF_e-20.csv
#-rw-r----- 1 seqstore users  49028243 Nov  7 21:43 EO01Contigs.masked_vs_plantprotein_FF_e-20.csv
#-rw-r----- 1 seqstore users   1783120 Nov  7 21:43 EO01Contigs.masked_vs_plantrna_FF_e-20.csv
#-rw-r----- 1 seqstore users  63686579 Nov  7 21:43 EO01Contigs_vs_plantprotein_FF_e-20.csv
#-rw-r----- 1 seqstore users   6989931 Nov  7 21:43 EO01Contigs_vs_plantrna_FF_e-20.csv
#-rw-r----- 1 seqstore users 131642644 Nov  7 21:43 EO01Singlets.masked_vs_plantprotein_FF_e-20.csv
#-rw-r----- 1 seqstore users   4480133 Nov  7 21:43 EO01Singlets.masked_vs_plantrna_FF_e-20.csv
#-rw-r----- 1 seqstore users 161644257 Nov  7 21:43 EO01Singlets_vs_plantprotein_FF_e-20.csv
#-rw-r----- 1 seqstore users  74417688 Nov  7 21:43 EO01Singlets_vs_plantrna_FF_e-20.csv
# 93048 -rw-r--r-- 1 seqstore    users   95178779 Oct 12 16:06 kerry_TR_BrickCresults.csv
# 97644 -rw-r--r-- 1 seqstore    users   99883300 Oct 12 16:05 kerry_TR_3320results.csv

    importParms = {
        'queryPrefix' : 'kerry_TR_BrickC',
        'hitPrefix' : 'NCBI',
        'hitAccessionRegexp' :   ('^tpg\|(\w+)\.?\d*\|?','^tpd\|(\w+)\.?\d*\|?','^gb\|(\w+)\.?\d*\|?','^ref\|(\w+)\.?\d*\|?','^emb\|(\w+)\.?\d*\|?','^dbj\|(\w+)\.?\d*\|?'), # example : ref|NM_001075746.1|,
        'queryAccessionRegexp' : None,
        'checkExistingHits' : False,
        'createMissingQueries' : False,
        'createMissingHits' : True,
        'querySequenceType' : 'mRNA SEQUENCE',
        'hitSequenceType' : 'PROTEIN SEQUENCE',
        'databaselsid' : 'NCBI.Plant Protein Refseqs',
        'blastprotocollsid' : 'Protocol.blastx.clover transcriptomes against plant protein refseqs',
        'datasourcetype' : 'blastx_agresearch_csv',
        'physicalsourceuri' : '/tmp/kerry_TR_BrickCresults.csv',
        'studytype' : 'Blast',
        'studydescription' : 'Blastx of 2012 clover transcriptomes against Plant Protein Refseqs',
        'fieldNamesRow' : 0,
        'fileFormat' : 'csv',
        'hitimportlimit' : 5,
        'alignmentimportlimit' : 5
    }

    myform = databaseSearchImportForm(importParms)
    myform.processData()
    return


    importParms = {
        'queryPrefix' : 'kerry_TR_3320',
        'hitPrefix' : 'NCBI',
        'hitAccessionRegexp' :   ('^tpg\|(\w+)\.?\d*\|?','^tpd\|(\w+)\.?\d*\|?','^gb\|(\w+)\.?\d*\|?','^ref\|(\w+)\.?\d*\|?','^emb\|(\w+)\.?\d*\|?','^dbj\|(\w+)\.?\d*\|?'), # example : ref|NM_001075746.1|,
        'queryAccessionRegexp' : None,
        'checkExistingHits' : False,
        'createMissingQueries' : False,
        'createMissingHits' : True,
        'querySequenceType' : 'mRNA SEQUENCE',
        'hitSequenceType' : 'PROTEIN SEQUENCE',
        'databaselsid' : 'NCBI.Plant Protein Refseqs',
        'blastprotocollsid' : 'Protocol.blastx.clover transcriptomes against plant protein refseqs',
        'datasourcetype' : 'blastx_agresearch_csv',
        'physicalsourceuri' : '/tmp/kerry_TR_3320results.csv',
        'studytype' : 'Blast',
        'studydescription' : 'Blastx of 2012 clover transcriptomes against Plant Protein Refseqs',
        'fieldNamesRow' : 0,
        'fileFormat' : 'csv',
        'hitimportlimit' : 5,
        'alignmentimportlimit' : 5
    }

    myform = databaseSearchImportForm(importParms)
    myform.processData()
    return


    importParms = {
        'queryPrefix' : 'kerry_TA',
        'hitPrefix' : 'NCBI',
        'hitAccessionRegexp' :   ('^tpg\|(\w+)\.?\d*\|?','^tpd\|(\w+)\.?\d*\|?','^gb\|(\w+)\.?\d*\|?','^ref\|(\w+)\.?\d*\|?','^emb\|(\w+)\.?\d*\|?','^dbj\|(\w+)\.?\d*\|?'), # example : ref|NM_001075746.1|,
        'queryAccessionRegexp' : None,
        'checkExistingHits' : False,
        'createMissingQueries' : False,
        'createMissingHits' : True,
        'querySequenceType' : 'mRNA SEQUENCE',
        'hitSequenceType' : 'PROTEIN SEQUENCE',
        'databaselsid' : 'NCBI.Plant Protein Refseqs',
        'blastprotocollsid' : 'Protocol.blastx.clover transcriptomes against plant protein refseqs',
        'datasourcetype' : 'blastx_agresearch_csv',
        #'physicalsourceuri' : '/data/home/seqstore/agbrdf/blastresults/EO01Contigs.masked_vs_plantprotein_FF_e-20.csv',
        'physicalsourceuri' : '/tmp/kerry_TAresults.csv',
        'studytype' : 'Blast',
        'studydescription' : 'Blastx of 2012 clover transcriptomes against Plant Protein Refseqs',
        'fieldNamesRow' : 0,
        'fileFormat' : 'csv',
        'hitimportlimit' : 5,
        'alignmentimportlimit' : 5
    }

    myform = databaseSearchImportForm(importParms)
    myform.processData()
    return


    importParms = {
        'queryPrefix' : 'SKUA',
        'hitPrefix' : 'NCBI',
        'hitAccessionRegexp' :   ('^tpg\|(\w+)\.?\d*\|?','^tpd\|(\w+)\.?\d*\|?','^gb\|(\w+)\.?\d*\|?','^ref\|(\w+)\.?\d*\|?','^emb\|(\w+)\.?\d*\|?','^dbj\|(\w+)\.?\d*\|?'), # example : ref|NM_001075746.1|,
        'queryAccessionRegexp' : None,
        'checkExistingHits' : True,
        'createMissingQueries' : False,
        'createMissingHits' : True,
        'querySequenceType' : 'genomic DNA',
        'hitSequenceType' : 'PROTEIN SEQUENCE',
        'databaselsid' : 'NCBI.Plant Protein Refseqs',
        'blastprotocollsid' : 'Protocol.blastx.Masked SKUA EOleifera against Plant Protein Refseqs Evalue 1.0e-20',
        'datasourcetype' : 'blastx_agresearch_csv',
        #'physicalsourceuri' : '/data/home/seqstore/agbrdf/blastresults/EO01Contigs.masked_vs_plantprotein_FF_e-20.csv',
        'physicalsourceuri' : '/data/home/seqstore/agbrdf/blastresults/EO01Singlets.masked_vs_plantprotein_FF_e-20.csv',
        'studytype' : 'Blast',
        'studydescription' : 'Blastx of Masked EOleifera GT contigs against Plant Protein Refseqs Evalue 1.0e-20',
        'fieldNamesRow' : 0,
        'fileFormat' : 'csv',
        'hitimportlimit' : 2,
        'alignmentimportlimit' : 2
    }

    myform = databaseSearchImportForm(importParms)
    myform.processData()
    return

    importParms = {
        'queryPrefix' : 'SKUA',
        'hitPrefix' : 'NCBI',
        'hitAccessionRegexp' :   ('^tpg\|(\w+)\.?\d*\|?','^tpd\|(\w+)\.?\d*\|?','^gb\|(\w+)\.?\d*\|?','^ref\|(\w+)\.?\d*\|?','^emb\|(\w+)\.?\d*\|?','^dbj\|(\w+)\.?\d*\|?'), # example : ref|NM_001075746.1|,
        'queryAccessionRegexp' : None,
        'checkExistingHits' : True,
        'createMissingQueries' : False,
        'createMissingHits' : True,
        'querySequenceType' : 'genomic DNA',
        'hitSequenceType' : 'mRNA SEQUENCE',
        'databaselsid' : 'NCBI.Plant mRNA Refseqs',
        'blastprotocollsid' : 'Protocol.blastn.Masked SKUA EOleifera against Plant mRNA Refseqs Evalue 1.0e-20',
        'datasourcetype' : 'blastn_agresearch_csv',
        #'physicalsourceuri' : '/data/home/seqstore/agbrdf/blastresults/EO01Contigs.masked_vs_plantrna_FF_e-20.csv',
        'physicalsourceuri' : '/data/home/seqstore/agbrdf/blastresults/EO01Singlets.masked_vs_plantrna_FF_e-20.csv',
        'studytype' : 'Blast',
        'studydescription' : 'Blastn of Masked EOleifera GT contigs against Plant mRNA Refseqs Evalue 1.0e-20',
        'fieldNamesRow' : 0,
        'fileFormat' : 'csv',
        'hitimportlimit' : 2,
        'alignmentimportlimit' : 2
    }

    myform = databaseSearchImportForm(importParms)
    myform.processData()
    return


    importParms = {
        'queryPrefix' : 'SKUA',
        'hitPrefix' : 'NCBI',
        'hitAccessionRegexp' :   ('^tpg\|(\w+)\.?\d*\|?','^tpd\|(\w+)\.?\d*\|?','^gb\|(\w+)\.?\d*\|?','^ref\|(\w+)\.?\d*\|?','^emb\|(\w+)\.?\d*\|?','^dbj\|(\w+)\.?\d*\|?'), # example : ref|NM_001075746.1|,
        'queryAccessionRegexp' : None,
        'checkExistingHits' : True,
        'createMissingQueries' : False,
        'createMissingHits' : True,
        'querySequenceType' : 'genomic DNA',
        'hitSequenceType' : 'PROTEIN SEQUENCE',
        'databaselsid' : 'NCBI.Plant Protein Refseqs',
        'blastprotocollsid' : 'Protocol.blastx.SKUA EOleifera against Plant Protein Refseqs Evalue 1.0e-20',
        'datasourcetype' : 'blastx_agresearch_csv',
        #'physicalsourceuri' : '/data/home/seqstore/agbrdf/blastresults/EO01Contigs_vs_plantprotein_FF_e-20.csv',
        'physicalsourceuri' : '/data/home/seqstore/agbrdf/blastresults/EO01Singlets_vs_plantprotein_FF_e-20.csv',
        'studytype' : 'Blast',
        #'studydescription' : 'Blastx of EOleifera GT contigs against Plant Protein Refseqs Evalue 1.0e-20',
        'studydescription' : 'Blastx of EOleifera GT singlets against Plant Protein Refseqs Evalue 1.0e-20',
        'fieldNamesRow' : 0,
        'fileFormat' : 'csv',
        'hitimportlimit' : 2,
        'alignmentimportlimit' : 2
    }

    myform = databaseSearchImportForm(importParms)
    myform.processData()
    return



    importParms = {
        'queryPrefix' : 'SKUA',
        'hitPrefix' : 'NCBI',
        'hitAccessionRegexp' :   ('^tpg\|(\w+)\.?\d*\|?','^tpd\|(\w+)\.?\d*\|?','^gb\|(\w+)\.?\d*\|?','^ref\|(\w+)\.?\d*\|?','^emb\|(\w+)\.?\d*\|?','^dbj\|(\w+)\.?\d*\|?'), # example : ref|NM_001075746.1|,
        'queryAccessionRegexp' : None,
        'checkExistingHits' : True,
        'createMissingQueries' : False,
        'createMissingHits' : True,
        'querySequenceType' : 'genomic DNA',
        'hitSequenceType' : 'mRNA SEQUENCE',
        'databaselsid' : 'NCBI.Plant mRNA Refseqs',
        'blastprotocollsid' : 'Protocol.blastn.SKUA EOleifera against Plant mRNA Refseqs Evalue 1.0e-20',
        'datasourcetype' : 'blastn_agresearch_csv',
        #'physicalsourceuri' : '/data/home/seqstore/agbrdf/blastresults/EO01Contigs_vs_plantrna_FF_e-20.csv',
        'physicalsourceuri' : '/data/home/seqstore/agbrdf/blastresults/EO01Singlets_vs_plantrna_FF_e-20.csv',
        'studytype' : 'Blast',
        'studydescription' : 'Blastn of EOleifera GT contigs against Plant mRNA Refseqs Evalue 1.0e-20',
        'fieldNamesRow' : 0,
        'fileFormat' : 'csv',
        'hitimportlimit' : 2,
        'alignmentimportlimit' : 2
    }

    myform = databaseSearchImportForm(importParms)
    myform.processData()
    return


    importParms = {
        'queryPrefix' : 'SKUA',
        'hitPrefix' : 'NCBI',
        'hitAccessionRegexp' :   ('^tpg\|(\w+)\.?\d*\|?','^tpd\|(\w+)\.?\d*\|?','^gb\|(\w+)\.?\d*\|?','^ref\|(\w+)\.?\d*\|?','^emb\|(\w+)\.?\d*\|?','^dbj\|(\w+)\.?\d*\|?'), # example : ref|NM_001075746.1|,
        'queryAccessionRegexp' : None,
        'checkExistingHits' : True,
        'createMissingQueries' : False,
        'createMissingHits' : True,
        'querySequenceType' : 'genomic DNA',
        'hitSequenceType' : 'PROTEIN SEQUENCE',
        'databaselsid' : 'NCBI.Plant Protein Refseqs',
        'blastprotocollsid' : 'Protocol.blastx.Masked SKUA EGuineensis against Plant Protein Refseqs Evalue 1.0e-20',
        'datasourcetype' : 'blastx_agresearch_csv',
        #'physicalsourceuri' : '/data/home/seqstore/agbrdf/blastresults/EG01Contigs.masked_vs_plantprotein_FF_e-20.csv',
        'physicalsourceuri' : '/data/home/seqstore/agbrdf/blastresults/EG01Singlets.masked_vs_plantprotein_FF_e-20.csv',
        'studytype' : 'Blast',
        'studydescription' : 'Blastx of Masked EGuineensis GT contigs against Plant Protein Refseqs Evalue 1.0e-20',
        'fieldNamesRow' : 0,
        'fileFormat' : 'csv',
        'hitimportlimit' : 2,
        'alignmentimportlimit' : 2
    }

    myform = databaseSearchImportForm(importParms)
    myform.processData()

    importParms = {
        'queryPrefix' : 'SKUA',
        'hitPrefix' : 'NCBI',
        'hitAccessionRegexp' :   ('^tpg\|(\w+)\.?\d*\|?','^tpd\|(\w+)\.?\d*\|?','^gb\|(\w+)\.?\d*\|?','^ref\|(\w+)\.?\d*\|?','^emb\|(\w+)\.?\d*\|?','^dbj\|(\w+)\.?\d*\|?'), # example : ref|NM_001075746.1|,
        'queryAccessionRegexp' : None,
        'checkExistingHits' : True,
        'createMissingQueries' : False,
        'createMissingHits' : True,
        'querySequenceType' : 'genomic DNA',
        'hitSequenceType' : 'mRNA SEQUENCE',
        'databaselsid' : 'NCBI.Plant mRNA Refseqs',
        'blastprotocollsid' : 'Protocol.blastn.Masked SKUA EGuineensis against Plant mRNA Refseqs Evalue 1.0e-20',
        'datasourcetype' : 'blastn_agresearch_csv',
        #'physicalsourceuri' : '/data/home/seqstore/agbrdf/blastresults/EG01Contigs.masked_vs_plantrna_FF_e-20.csv',
        'physicalsourceuri' : '/data/home/seqstore/agbrdf/blastresults/EG01Singlets.masked_vs_plantrna_FF_e-20.csv',
        'studytype' : 'Blast',
        'studydescription' : 'Blastn of Masked EGuineensis GT contigs against Plant mRNA Refseqs Evalue 1.0e-20',
        'fieldNamesRow' : 0,
        'fileFormat' : 'csv',
        'hitimportlimit' : 2,
        'alignmentimportlimit' : 2
    }

    myform = databaseSearchImportForm(importParms)
    myform.processData()


    importParms = {
        'queryPrefix' : 'SKUA',
        'hitPrefix' : 'NCBI',
        'hitAccessionRegexp' :   ('^tpg\|(\w+)\.?\d*\|?','^tpd\|(\w+)\.?\d*\|?','^gb\|(\w+)\.?\d*\|?','^ref\|(\w+)\.?\d*\|?','^emb\|(\w+)\.?\d*\|?','^dbj\|(\w+)\.?\d*\|?'), # example : ref|NM_001075746.1|,
        'queryAccessionRegexp' : None,
        'checkExistingHits' : True,
        'createMissingQueries' : False,
        'createMissingHits' : True,
        'querySequenceType' : 'genomic DNA',
        'hitSequenceType' : 'PROTEIN SEQUENCE',
        'databaselsid' : 'NCBI.Plant Protein Refseqs',
        'blastprotocollsid' : 'Protocol.blastx.SKUA EGuineensis against Plant Protein Refseqs Evalue 1.0e-20',
        'datasourcetype' : 'blastx_agresearch_csv',
        #'physicalsourceuri' : '/data/home/seqstore/agbrdf/blastresults/EG01Contigs_vs_plantprotein_FF_e-20.csv',
        'physicalsourceuri' : '/data/home/seqstore/agbrdf/blastresults/EG01Singlets_vs_plantprotein_FF_e-20.csv',
        'studytype' : 'Blast',
        'studydescription' : 'Blastx of EGuineensis GT contigs against Plant Protein Refseqs Evalue 1.0e-20',
        'fieldNamesRow' : 0,
        'fileFormat' : 'csv',
        'hitimportlimit' : 2,
        'alignmentimportlimit' : 2
    }

    myform = databaseSearchImportForm(importParms)
    myform.processData()

    importParms = {
        'queryPrefix' : 'SKUA',
        'hitPrefix' : 'NCBI',
        'hitAccessionRegexp' :   ('^tpg\|(\w+)\.?\d*\|?','^tpd\|(\w+)\.?\d*\|?','^gb\|(\w+)\.?\d*\|?','^ref\|(\w+)\.?\d*\|?','^emb\|(\w+)\.?\d*\|?','^dbj\|(\w+)\.?\d*\|?'), # example : ref|NM_001075746.1|,
        'queryAccessionRegexp' : None,
        'checkExistingHits' : True,
        'createMissingQueries' : False,
        'createMissingHits' : True,
        'querySequenceType' : 'genomic DNA',
        'hitSequenceType' : 'mRNA SEQUENCE',
        'databaselsid' : 'NCBI.Plant mRNA Refseqs',
        'blastprotocollsid' : 'Protocol.blastn.SKUA EGuineensis against Plant mRNA Refseqs Evalue 1.0e-20',
        'datasourcetype' : 'blastn_agresearch_csv',
        #'physicalsourceuri' : '/data/home/seqstore/agbrdf/blastresults/EG01Contigs_vs_plantrna_FF_e-20.csv',
        'physicalsourceuri' : '/data/home/seqstore/agbrdf/blastresults/EG01Singlets_vs_plantrna_FF_e-20.csv',
        'studytype' : 'Blast',
        'studydescription' : 'Blastn of EGuineensis GT contigs against Plant mRNA Refseqs Evalue 1.0e-20',
        'fieldNamesRow' : 0,
        'fileFormat' : 'csv',
        'hitimportlimit' : 2,
        'alignmentimportlimit' : 2
    }

    myform = databaseSearchImportForm(importParms)
    myform.processData()
    return


    importParms = {
        'queryPrefix' : 'AgResearch.Bovine',
        'hitPrefix' : 'NCBI',
        'hitAccessionRegexp' : ('^\w*\|(\w+)\.?\d*\|','^pir\|\|(\w+)\.?\d*' , '^prf\|\|(\w+)\.?\d*'),
        'queryAccessionRegexp' : None,
        'checkExistingHits' : True,
        'createMissingQueries' : True,
        'createMissingHits' : True,
        'querySequenceType' : 'PROTEIN SEQUENCE',
        'hitSequenceType' : 'PROTEIN SEQUENCE',
        'databaselsid' : 'NCBI.Non-redundant Protein (NR)',
        'blastprotocollsid' : 'Protocol.blastp.Bovine EST and Contig translations against NR',
        'datasourcetype' : 'blastx_agresearch_csv',
        'physicalsourceuri' : 'heldBack.fa.allnohitprots_nr.csv',
        'studytype' : 'Blast',
        'studydescription' : 'Blastp of Bovine EST and Contig translations against NCBI nr',
        'fieldNamesRow' : 0,
        'fileFormat' : 'csv'
    }

    myform = databaseSearchImportForm(importParms)
    myform.processData()
    return


    importParms = {
        'queryPrefix' : 'OAGI',
        'hitPrefix' : 'NCBI',
        'hitAccessionRegexp' : ('^\w*\|(\w+)\.?\d*\|','^pir\|\|(\w+)\.?\d*' , '^prf\|\|(\w+)\.?\d*'),
        'queryAccessionRegexp' : None,
        'checkExistingHits' : False,
        'createMissingQueries' : True,
        'createMissingHits' : True,
        'querySequenceType' : 'PROTEIN SEQUENCE',
        'hitSequenceType' : 'PROTEIN SEQUENCE',
        'databaselsid' : 'NCBI.Non-redundant Protein (NR)',
        'blastprotocollsid' : 'Protocol.blastp.OAGI protein translations against NR',
        'datasourcetype' : 'blastx_agresearch_csv',
        'physicalsourceuri' : '/data/agbio/spool/all_oagi_nohitprots.fa_nr.csv',
        'studytype' : 'Blast',
        'studydescription' : 'Blastp of OAGI protein translations against NCBI nr',
        'fieldNamesRow' : 0,
        'fileFormat' : 'csv'
    }

    myform = databaseSearchImportForm(importParms)
    myform.processData()
    return


    importParms = {
        'queryPrefix' : 'CS60',
        'hitPrefix' : 'NCBI',
        'hitAccessionRegexp' : ('^\w*\|(\w+)\.?\d*\|','^pir\|\|(\w+)\.?\d*' , '^prf\|\|(\w+)\.?\d*'),
        'queryAccessionRegexp' : None,
        'checkExistingHits' : False,
        'createMissingQueries' : False,
        'createMissingHits' : True,
        'querySequenceType' : 'DNA SEQUENCE',
        'hitSequenceType' : 'PROTEIN SEQUENCE',
        'databaselsid' : 'NCBI.Non-redundant Protein (NR)',
        'blastprotocollsid' : 'Protocol.blastx.AgResearch CS60 deer EST contigs against NR',
        'datasourcetype' : 'blastx_agresearch_csv',
        #'physicalsourceuri' : '/data/home/seqstore/agbrdf/blastresults/cs60.fa_nr.csv',
        #'physicalsourceuri' : '/data/home/seqstore/agbrdf/blastresults/10031.fa_nr.csv',
        #'physicalsourceuri' : '/data/home/seqstore/agbrdf/blastresults/10031renamed.fa_nr.csv',
        'physicalsourceuri' : '/data/home/seqstore/agbrdf/blastresults/10031singlets.fa_nr.csv',
        'studytype' : 'Blast',
        'studydescription' : 'Blastx of Deer CS60 EST contigs against NCBI nr',
        'fieldNamesRow' : 0,
        'fileFormat' : 'csv'
    }

    myform = databaseSearchImportForm(importParms)
    myform.processData()
    return


    importParms = {
        'queryPrefix' : 'CS60',
        'hitPrefix' : 'NCBI',
        'hitAccessionRegexp' :   ('^ref\|(\w+)\.?\d*\|?', '^gi\|\d+\|ref\|(\w+)\.?\d*\|?'), # example : ref|NM_001075746.1|,
        'queryAccessionRegexp' : None,
        'checkExistingHits' : False,
        'createMissingQueries' : False,
        'createMissingHits' : True,
        'querySequenceType' : 'mRNA SEQUENCE',
        'hitSequenceType' : 'mRNA SEQUENCE',
        'databaselsid' : 'NCBI.Bovine mRNA Refseqs',
        'blastprotocollsid' : 'Protocol.blastn.Deer CS60 Contigs against Bovine Refseqs',
        'datasourcetype' : 'blastn_agresearch_csv',
        #'physicalsourceuri' : '/tmp/renamed_singlets.fa_bt.fna.csv',
        #'physicalsourceuri' : '/data/home/seqstore/agbrdf/blastresults/10031.fa_bt.fna.csv',
        #'physicalsourceuri' : '/data/home/seqstore/agbrdf/blastresults/10031renamed.fa_bt.fna.csv',
        'studytype' : 'Blast',
        'studydescription' : 'Blastn of Deer CS60 EST contigs against Bovine refseqs',
        'fieldNamesRow' : 0,
        'fileFormat' : 'csv'
    }

    myform = databaseSearchImportForm(importParms)
    myform.processData()
    return


    importParms = {
        'queryPrefix' : 'CS60',
        'hitPrefix' : 'NCBI',
        'hitAccessionRegexp' :   ('^ref\|(\w+)\.?\d*\|?', '^gi\|\d+\|ref\|(\w+)\.?\d*\|?'), # example : ref|NM_001075746.1|,
        'queryAccessionRegexp' : None,
        'checkExistingHits' : False,
        'createMissingQueries' : False,
        'createMissingHits' : True,
        'querySequenceType' : 'mRNA SEQUENCE',
        'hitSequenceType' : 'mRNA SEQUENCE',
        'databaselsid' : 'NCBI.Bovine mRNA Refseqs',
        'blastprotocollsid' : 'Protocol.blastn.Deer CS60 Contigs against Bovine Refseqs',
        'datasourcetype' : 'blastn_agresearch_csv',
        'physicalsourceuri' : '/tmp/cs60btrefseq.csv',
        'studytype' : 'Blast',
        'studydescription' : 'Blastn of Deer CS60 EST contigs against Bovine refseqs',
        'fieldNamesRow' : 0,
        'fileFormat' : 'csv'
    }

    myform = databaseSearchImportForm(importParms)
    myform.processData()
    return



    importParms = {
        'queryPrefix' : 'AgResearch.Ovine',
        'hitPrefix' : 'NCBI',
        'hitAccessionRegexp' :   ('^ref\|(\w+)\.?\d*\|?', '^gi\|\d+\|ref\|(\w+)\.?\d*\|?'), # example : ref|NM_001075746.1|,
        'queryAccessionRegexp' : None,
        'checkExistingHits' : False,
        'createMissingQueries' : False,
        'createMissingHits' : True,
        'querySequenceType' : 'mRNA SEQUENCE',
        'hitSequenceType' : 'mRNA SEQUENCE',
        'databaselsid' : 'NCBI.Human mRNA Refseqs',
        'blastprotocollsid' : 'Protocol.blastn.Sheep ESTs against Human Refseqs',
        'datasourcetype' : 'blastn_agresearch_csv',
        'physicalsourceuri' : '/data/agbio/spool/est.hs.csv',
        'studytype' : 'Blast',
        'studydescription' : 'Blastn of AgResearch Sheep ESTs against Human mRNA refseqs',
        'fieldNamesRow' : 0,
        'fileFormat' : 'csv'
    }

    myform = databaseSearchImportForm(importParms)
    myform.processData()
    return


    importParms = {
        'queryPrefix' : 'AgResearch.Ovine',
        'hitPrefix' : 'NCBI',
        'hitAccessionRegexp' :   ('^ref\|(\w+)\.?\d*\|?', '^gi\|\d+\|ref\|(\w+)\.?\d*\|?'), # example : ref|NM_001075746.1|,
        'queryAccessionRegexp' : None,
        'checkExistingHits' : False,
        'createMissingQueries' : False,
        'createMissingHits' : True,
        'querySequenceType' : 'mRNA SEQUENCE',
        'hitSequenceType' : 'mRNA SEQUENCE',
        'databaselsid' : 'NCBI.Bovine mRNA Refseqs',
        'blastprotocollsid' : 'Protocol.blastn.Sheep ESTs against Bovine Refseqs',
        'datasourcetype' : 'blastn_agresearch_csv',
        'physicalsourceuri' : '/data/agbio/spool/est.bt.csv',
        'studytype' : 'Blast',
        'studydescription' : 'Blastn of AgResearch sheep ESTs against Bovine mRNA refseqs',
        'fieldNamesRow' : 0,
        'fileFormat' : 'csv'
    }
    myform = databaseSearchImportForm(importParms)
    myform.processData()
    return


    importParms = {
        'queryPrefix' : 'CS39',
        'hitPrefix' : 'NCBI',
        'hitAccessionRegexp' :   ('^ref\|(\w+)\.?\d*\|?', '^gi\|\d+\|ref\|(\w+)\.?\d*\|?'), # example : ref|NM_001075746.1|,
        'queryAccessionRegexp' : None,
        'checkExistingHits' : True,
        'createMissingQueries' : False,
        'createMissingHits' : True,
        'querySequenceType' : 'mRNA SEQUENCE',
        'hitSequenceType' : 'mRNA SEQUENCE',
        'databaselsid' : 'NCBI.Human mRNA Refseqs',
        'blastprotocollsid' : 'Protocol.blastn.CS39 Ovine EST contigs against Human Refseqs',
        'datasourcetype' : 'blastn_agresearch_csv',
        'physicalsourceuri' : '/data/agbio/spool/cs39.hs.csvredo',
        'studytype' : 'Blast',
        'studydescription' : 'Blastn of AgResearch CS39 EST contigs against Human mRNA refseqs',
        'fieldNamesRow' : 0,
        'fileFormat' : 'csv'
    }

    myform = databaseSearchImportForm(importParms)
    myform.processData()
    return


    importParms = {
        'queryPrefix' : 'CS39',
        'hitPrefix' : 'NCBI',
        'hitAccessionRegexp' :   ('^ref\|(\w+)\.?\d*\|?', '^gi\|\d+\|ref\|(\w+)\.?\d*\|?'), # example : ref|NM_001075746.1|,
        'queryAccessionRegexp' : None,
        'checkExistingHits' : False,
        'createMissingQueries' : False,
        'createMissingHits' : True,
        'querySequenceType' : 'mRNA SEQUENCE',
        'hitSequenceType' : 'mRNA SEQUENCE',
        'databaselsid' : 'NCBI.Bovine mRNA Refseqs',
        'blastprotocollsid' : 'Protocol.blastn.CS39 Ovine EST contigs against Bovine Refseqs',
        'datasourcetype' : 'blastn_agresearch_csv',
        'physicalsourceuri' : '/data/agbio/spool/cs39.bt.csv',
        'studytype' : 'Blast',
        'studydescription' : 'Blastn of AgResearch CS39 EST contigs against Bovine mRNA refseqs',
        'fieldNamesRow' : 0,
        'fileFormat' : 'csv'
    }

    myform = databaseSearchImportForm(importParms)
    myform.processData()
    return


    importParms = {
        'queryPrefix' : 'CS39',
        'hitPrefix' : 'NCBI',
        'hitAccessionRegexp' :   ('^ref\|(\w+)\.?\d*\|?', '^gi\|\d+\|ref\|(\w+)\.?\d*\|?'), # example : ref|NM_001075746.1|,
        'queryAccessionRegexp' : None,
        'checkExistingHits' : True,
        'createMissingQueries' : False,
        'createMissingHits' : True,
        'querySequenceType' : 'mRNA SEQUENCE',
        'hitSequenceType' : 'mRNA SEQUENCE',
        'databaselsid' : 'NCBI.Human mRNA Refseqs',
        'blastprotocollsid' : 'Protocol.blastn.CS39 Ovine EST contigs against Human Refseqs',
        'datasourcetype' : 'blastn_agresearch_csv',
        'physicalsourceuri' : '/data/agbio/spool/cs39.hs.csv',
        'studytype' : 'Blast',
        'studydescription' : 'Blastn of AgResearch CS39 EST contigs against Human mRNA refseqs',
        'fieldNamesRow' : 0,
        'fileFormat' : 'csv'
    }

    myform = databaseSearchImportForm(importParms)
    myform.processData()
    return



    importParms = {
        'hitPrefix' : 'ENSEMBL.ArrayExpress.Placenta',
        'queryPrefix' : 'ENSEMBL.Ornithorhynchus_anatinus',
        'hitAccessionRegexp' : ('^\S+\s+(\w+)\|\w+\s*',),
        'queryAccessionRegexp' : ('^(\w+)\s+',),
        'checkExistingHits' : False,
        'createMissingQueries' : False,
        'createMissingHits' : False,
        'querySequenceType' : 'PROTEIN SEQUENCE',
        'hitSequenceType' : 'PROTEIN SEQUENCE',
        'databaselsid' : 'ENSEMBL.ArrayExpress.Placenta',
        'blastprotocollsid' : 'Protocol.paralign.Platypus proteins against Array Express proteins',
        'datasourcetype' : 'paralignprot',
        'physicalsourceuri' : '/data/databases/flatfile/bfiles/agbrdf/temp/PlatypusVsAExpressProts.tab.out',
        #'physicalsourceuri' : '/tmp/test.out',
        'studytype' : 'Smith Waterman',
        'studydescription' : 'Paralign search of Platypus Proteins against Array Express Placental Proteins',
        'fieldNamesRow' : 0,
        'fileFormat' : 'tab'
    }
    myform = databaseSearchImportForm(importParms)
    myform.processData()
    return

    importParms = {
        'hitPrefix' : 'ENSEMBL.Ornithorhynchus_anatinus',
        'queryPrefix' : 'ENSEMBL.ArrayExpress.Placenta',
        'hitAccessionRegexp' : ('^\S+\s+(\w+)\s+',),
        'queryAccessionRegexp' : ('^(\w+)\|\w+\s*',),
        'checkExistingHits' : False,
        'createMissingQueries' : False,
        'createMissingHits' : False,
        'querySequenceType' : 'PROTEIN SEQUENCE',
        'hitSequenceType' : 'PROTEIN SEQUENCE',
        'databaselsid' : 'ENSEMBL.Ornithorhynchus_anatinus.Proteins',
        'blastprotocollsid' : 'Protocol.paralign.Array Express Proteins against Platypus',
        'datasourcetype' : 'paralignprot',
        'physicalsourceuri' : '/data/databases/flatfile/bfiles/agbrdf/temp/AExpress_protsVSplatypus.tab.out',
        #'physicalsourceuri' : '/tmp/test.out',
        'studytype' : 'Smith Waterman',
        'studydescription' : 'Paralign search of ArrayExpress proteins against Platypus Proteins',
        'fieldNamesRow' : 0,
        'fileFormat' : 'tab'
    }
    myform = databaseSearchImportForm(importParms)
    myform.processData()
    return

    importParms = {
        'hitPrefix' : 'ENSEMBL.ArrayExpress.Placenta',
        'queryPrefix' : 'ENSEMBL.Zebrafinch',
        'hitAccessionRegexp' : ('^\S+\s+(\w+)\|\w+\s*',),
        'queryAccessionRegexp' : ('^(\w+)\s+',),
        'checkExistingHits' : False,
        'createMissingQueries' : False,
        'createMissingHits' : False,
        'querySequenceType' : 'PROTEIN SEQUENCE',
        'hitSequenceType' : 'PROTEIN SEQUENCE',
        'databaselsid' : 'ENSEMBL.ArrayExpress.Placenta',
        'blastprotocollsid' : 'Protocol.paralign.Zebrafinch proteins against Array Express proteins',
        'datasourcetype' : 'paralignprot',
        'physicalsourceuri' : '/data/databases/flatfile/bfiles/agbrdf/temp/ZFinchVsAE_prots.tab.out',
        #'physicalsourceuri' : '/tmp/test.out',
        'studytype' : 'Smith Waterman',
        'studydescription' : 'Paralign search of ZebraFinch Proteins against Array Express Placental Proteins',
        'fieldNamesRow' : 0,
        'fileFormat' : 'tab'
    }
    myform = databaseSearchImportForm(importParms)
    myform.processData()
    return



    importParms = {
        'hitPrefix' : 'ENSEMBL.Zebrafinch',
        'queryPrefix' : 'ENSEMBL.ArrayExpress.Placenta',
        'hitAccessionRegexp' : ('^\S+\s+(\w+)\s+',),
        'queryAccessionRegexp' : ('^(\w+)\|\w+\s*',),
        'checkExistingHits' : False,
        'createMissingQueries' : False,
        'createMissingHits' : False,
        'querySequenceType' : 'PROTEIN SEQUENCE',
        'hitSequenceType' : 'PROTEIN SEQUENCE',
        'databaselsid' : 'ENSEMBL.Zebrafinch',
        'blastprotocollsid' : 'Protocol.paralign.Array Express Proteins against Zebrafinch proteins',
        'datasourcetype' : 'paralignprot',
        'physicalsourceuri' : '/data/databases/flatfile/bfiles/agbrdf/temp/AExpress_protsVSZFinch.tab.out',
        #'physicalsourceuri' : '/tmp/test.out',
        'studytype' : 'Smith Waterman',
        'studydescription' : 'Paralign search of ArrayExpress proteins against ZebraFinch Proteins',
        'fieldNamesRow' : 0,
        'fileFormat' : 'tab'
    }
    myform = databaseSearchImportForm(importParms)
    myform.processData()
    return


    importParms = {
        'hitPrefix' : 'ENSEMBL.orthodb',
        'queryPrefix' : 'AgResearch.Bovine',
        'hitAccessionRegexp' : None,
        'queryAccessionRegexp' : None,
        'checkExistingHits' : False,
        'createMissingQueries' : False,
        'createMissingHits' : False,
        'querySequenceType' : 'mRNA SEQUENCE',
        'hitSequenceType' : 'PROTEIN SEQUENCE',
        'databaselsid' : 'ENSEMBL.Orthodb.Proteins',
        'blastprotocollsid' : 'Protocol.blastx.AgResearch Bovine ESTs against Human Orthodb proteins',
        'datasourcetype' : 'blastx_agresearch_csv',
        'physicalsourceuri' : '/data/databases/flatfile/bfiles/agbrdf/temp/bov_estsVs_placentation_candidates.out.parsed',
        #'physicalsourceuri' : '/tmp/test.out',
        'studytype' : 'Blast',
        'studydescription' : 'blastx of Bovine placental ESTs against Human orthodb placentation candidates',
        'fieldNamesRow' : 0,
        'fileFormat' : 'csv'
    }


    myform = databaseSearchImportForm(importParms)
    myform.processData()
    return

    importParms = {
        'hitPrefix' : 'AgResearch.Bovine',
        'queryPrefix' : 'ENSEMBL.orthodb',
        'hitAccessionRegexp' : None,
        'queryAccessionRegexp' : None,
        'checkExistingHits' : False,
        'createMissingQueries' : False,
        'createMissingHits' : False,
        'querySequenceType' : 'PROTEIN SEQUENCE',
        'hitSequenceType' : 'mRNA SEQUENCE',
        'databaselsid' : 'AgResearch.Bovine EST',
        'blastprotocollsid' : 'Protocol.tblastn.Human Orthodb proteins against agResearch bovine ESTs',
        'datasourcetype' : 'blastn_agresearch_csv',
        'physicalsourceuri' : '/data/databases/flatfile/bfiles/agbrdf/temp/placentation_candidatesVS_bov_ests.out.parsed',
        #'physicalsourceuri' : '/tmp/test.out',
        'studytype' : 'Blast',
        'studydescription' : 'tblastn of Human orthodb placentation candidates against AgResearch bovine ESTs',
        'fieldNamesRow' : 0,
        'fileFormat' : 'csv'
    }

    myform = databaseSearchImportForm(importParms)
    myform.processData()
    return



    importParms = {
        'hitPrefix' : 'ENSEMBL.orthodb',
        'queryPrefix' : 'ENSEMBL.Homo_sapiens',
        'hitAccessionRegexp' : None,
        'queryAccessionRegexp' : None,
        'checkExistingHits' : False,
        'createMissingQueries' : False,
        'createMissingHits' : False,
        'querySequenceType' : 'mRNA SEQUENCE',
        'hitSequenceType' : 'PROTEIN SEQUENCE',
        'databaselsid' : 'ENSEMBL.Orthodb.Proteins',
        'blastprotocollsid' : 'Protocol.blastx.Human placental ESTs against Human Orthodb proteins',
        'datasourcetype' : 'blastx_agresearch_csv',
        'physicalsourceuri' : '/data/databases/flatfile/bfiles/agbrdf/temp/human_estsVS_placentation_candidates.out.parsed',
        #'physicalsourceuri' : '/tmp/test.out',
        'studytype' : 'Blast',
        'studydescription' : 'blastx of Human placental ESTs against Human orthodb placentation candidates',
        'fieldNamesRow' : 0,
        'fileFormat' : 'csv'
    }

    myform = databaseSearchImportForm(importParms)
    myform.processData()
    return

    importParms = {
        'queryPrefix' : None,
        'hitPrefix' : 'UMD3',
        'hitAccessionRegexp' : None,
        'queryAccessionRegexp' : None,
        'checkExistingHits' : False,
        'createMissingQueries' : False,
        'createMissingHits' : True,
        'querySequenceType' : 'genomic DNA',
        'hitSequenceType' : 'genomic DNA',
        'databaselsid' : 'Genome.UMD3',
        'databasetype' : 'Nucleotide Sequence database',
        'blastprotocollsid' : 'Protocol.megablast.Illumina Deer Blast-masked Cross Species megablast',
        'datasourcetype' : 'megablast_D3',
        'physicalsourceuri' : '/ngseqdata/deer/blast/condor/s_7_sample200000.fa.masked_umd3.results.rewritten',
        'studytype' : 'Blast',
        'studydescription' : 'Megablast of  a sample of 200000 paired deer reads against UMD3',
        'hitimportlimit' : 2,
        'alignmentimportlimit' : 2,
        'adjustedevaluecutoff' : 1.0e-10,
        'singlehitevaluecutoff' : 1.0e-3,
        'hspcountforrepeat' : 1000,
        'locationMapDetails'  : {'mapname' : 'UMD3', 'evidence' : 'Megablast (adjusted evalue)'},
        'annotateGenomeMapping' : True,
        'cacheQueryList' : False,
        'cacheHitList' : False,
        'fieldNamesRow' : -1,
        'fileFormat' : 'tab',
        'queryTableColumn' : 'sequencename'
    }

    myform = databaseSearchImportForm(importParms)
    myform.processData()
    return


    importParms = {
        'queryPrefix' : None,
        'hitPrefix' : 'UMD3',
        'hitAccessionRegexp' : None,
        'queryAccessionRegexp' : None,
        'checkExistingHits' : False,
        'createMissingQueries' : False,
        'createMissingHits' : True,
        'querySequenceType' : 'genomic DNA',
        'hitSequenceType' : 'genomic DNA',
        'databaselsid' : 'Genome.UMD3',
        'databasetype' : 'Nucleotide Sequence database',
        'blastprotocollsid' : 'Protocol.megablast.Illumina Deer Standard Cross Species megablast',
        'datasourcetype' : 'megablast_D3',
        'physicalsourceuri' : '/ngseqdata/deer/blast/condor/s_7_sample50000.fa.masked.results.rewritten',
        'studytype' : 'Blast',
        'studydescription' : 'Megblast of repeatmasked s_7_sample50000 against UMD3 genome (complete chromosomes)',
        'hitimportlimit' : 2,
        'alignmentimportlimit' : 2,
        'adjustedevaluecutoff' : 1.0e-10,
        'singlehitevaluecutoff' : 1.0e-3,
        'hspcountforrepeat' : 1000,
        'locationMapDetails'  : {'mapname' : 'UMD3', 'evidence' : 'Megablast (adjusted evalue)'},
        'annotateGenomeMapping' : True,
        'cacheQueryList' : False,
        'cacheHitList' : False,
        'fieldNamesRow' : -1,
        'fileFormat' : 'tab',
        'queryTableColumn' : 'sequencename'
    }

    myform = databaseSearchImportForm(importParms)
    myform.processData()
    return

    importParms = {
        'hitPrefix' : 'ENSEMBL.Ornithorhynchus_anatinus',
        'queryPrefix' : 'ENSEMBL.orthodb',
        'hitAccessionRegexp' : ('^\S+\s+(\w+)\s+',),
        'queryAccessionRegexp' : ('^(\w+)\s+',),
        'checkExistingHits' : False,
        'createMissingQueries' : False,
        'createMissingHits' : False,
        'querySequenceType' : 'PROTEIN SEQUENCE',
        'hitSequenceType' : 'PROTEIN SEQUENCE',
        'databaselsid' : 'ENSEMBL.Ornithorhynchus_anatinus.Proteins',
        'blastprotocollsid' : 'Protocol.paralign.Orthodb proteins against Platypus proteins',
        'datasourcetype' : 'paralignprot',
        'physicalsourceuri' : '/data/databases/flatfile/bfiles/agbrdf/temp/mammVSplatypus_paralign_tab.out',
        #'physicalsourceuri' : '/tmp/test.out',
        'studytype' : 'Smith Waterman',
        'studydescription' : 'Smith Waterman alignment of Orthodb proteins against Platypus Proteins',
        'fieldNamesRow' : 0,
        'fileFormat' : 'tab'
    }

    myform = databaseSearchImportForm(importParms)
    myform.processData()
    return


    importParms = {
        'hitPrefix' : 'ENSEMBL.orthodb',
        'queryPrefix' : 'ENSEMBL.Ornithorhynchus_anatinus',
        'hitAccessionRegexp' : ('^\S+\s+(\w+)\s+',),
        'queryAccessionRegexp' : ('^(\w+)\s+',),
        'checkExistingHits' : False,
        'createMissingQueries' : False,
        'createMissingHits' : False,
        'querySequenceType' : 'PROTEIN SEQUENCE',
        'hitSequenceType' : 'PROTEIN SEQUENCE',
        'databaselsid' : 'ENSEMBL.Orthodb.Proteins',
        'blastprotocollsid' : 'Protocol.paralign.Platypus proteins against Orthodb proteins',
        'datasourcetype' : 'paralignprot',
        'physicalsourceuri' : '/data/databases/flatfile/bfiles/agbrdf/temp/platypusVSmamm_paralign_tab.out',
        #'physicalsourceuri' : '/tmp/test.out',
        'studytype' : 'Smith Waterman',
        'studydescription' : 'Smith Waterman alignment of Platypus proteins against Orthodb Proteins',
        'fieldNamesRow' : 0,
        'fileFormat' : 'tab'
    }

    myform = databaseSearchImportForm(importParms)
    myform.processData()
    return


    importParms = {
        'queryPrefix' : 'ENSEMBL.Macropus_eugenii',
        'hitPrefix' : 'ENSEMBL.orthodb',
        'hitAccessionRegexp' : ('^\S+\s+(\w+)\s+',),
        'queryAccessionRegexp' : ('^(\w+)\s+',),
        'checkExistingHits' : False,
        'createMissingQueries' : False,
        'createMissingHits' : False,
        'querySequenceType' : 'PROTEIN SEQUENCE',
        'hitSequenceType' : 'PROTEIN SEQUENCE',
        'databaselsid' : 'ENSEMBL.Orthodb.Proteins',
        'blastprotocollsid' : 'Protocol.paralign.Wallaby proteins against Orthodb proteins',
        'datasourcetype' : 'paralignprot',
        'physicalsourceuri' : '/data/databases/flatfile/bfiles/agbrdf/temp/wallabyVSmamm_paralign_tab.out',
        #'physicalsourceuri' : '/tmp/test.out',
        'studytype' : 'Smith Waterman',
        'studydescription' : 'Smith Waterman alignment of Wallaby proteins against Orthodb Proteins',
        'fieldNamesRow' : 0,
        'fileFormat' : 'tab'
    }

    myform = databaseSearchImportForm(importParms)
    myform.processData()
    return


    importParms = {
        'queryPrefix' : 'CS46B',
        'hitPrefix' : 'NCBI',
        'hitAccessionRegexp' : ('^ref\|(\w+)\.?\d*\|?', '^gi\|\d+\|ref\|(\w+)\.?\d*\|?'),
        'queryAccessionRegexp' : None,
        'checkExistingHits' : True,
        'createMissingQueries' : False,
        'createMissingHits' : True,
        'querySequenceType' : 'mRNA SEQUENCE',
        'hitSequenceType' : 'mRNA SEQUENCE',
        'databaselsid' : 'NCBI.Invertebrate mRNA Refseqs',
        'blastprotocollsid' : 'Protocol.blastn.Teladorsagia circumcincta Transcript Contigs against Invertebrate Refseqs',
        'datasourcetype' : 'blastn_agresearch_csv',
        'physicalsourceuri' : '/data/home/seqstore/agbrdf/blastresults/cs46bcontigs.seq_invertebrate.rna.fna.csv',
        'studytype' : 'Blast',
        'studydescription' : 'blastn of Teladorsagia circumcincta Sequences against Invertebrate Refseqs',
        'fieldNamesRow' : 0
    }

    myform = databaseSearchImportForm(importParms)
    myform.processData()
    return


    importParms = {
        'queryPrefix' : 'CS39',
        'hitPrefix' : 'NCBI',
        'hitAccessionRegexp' : ('^\w*\|(\w+)\.?\d*\|','^pir\|\|(\w+)\.?\d*' , '^prf\|\|(\w+)\.?\d*'),
        'queryAccessionRegexp' : None,
        'checkExistingHits' : True,
        'createMissingQueries' : False,
        'createMissingHits' : True,
        'querySequenceType' : 'DNA SEQUENCE',
        'hitSequenceType' : 'PROTEIN SEQUENCE',
        'databaselsid' : 'NCBI.Non-redundant Protein (NR)',
        'blastprotocollsid' : 'Protocol.blastx.AgResearch CS39 sheep EST contigs against NR',
        'datasourcetype' : 'blastx_agresearch_csv',
        'physicalsourceuri' : '/data/home/seqstore/agbrdf/blastresults/cs39.seq_nr.csv',
        'studytype' : 'Blast',
        'studydescription' : 'Blastx of AgResearch CS39 sheep EST contigs against NCBI nr',
        'fieldNamesRow' : 0
    }

    myform = databaseSearchImportForm(importParms)
    myform.processData()
    return




    importParms = {
        'queryPrefix' : 'CS46A',
        'hitPrefix' : 'NCBI',
        'hitAccessionRegexp' : ('^ref\|(\w+)\.?\d*\|?', '^gi\|\d+\|ref\|(\w+)\.?\d*\|?'),
        'queryAccessionRegexp' : None,
        'checkExistingHits' : True,
        'createMissingQueries' : False,
        'createMissingHits' : True,
        'querySequenceType' : 'mRNA SEQUENCE',
        'hitSequenceType' : 'mRNA SEQUENCE',
        'databaselsid' : 'NCBI.Invertebrate mRNA Refseqs',
        'blastprotocollsid' : 'Protocol.blastn.Teladorsagia circumcincta Transcript Contigs against Invertebrate Refseqs',
        'datasourcetype' : 'blastn_agresearch_csv',
        'physicalsourceuri' : '/data/home/seqstore/agbrdf/blastresults/cs46acontigs.seq_invertebrate.rna.fna.csv',
        'studytype' : 'Blast',
        'studydescription' : 'blastn of Teladorsagia circumcincta Sequences against Invertebrate Refseqs',
        'fieldNamesRow' : 0
    }

    myform = databaseSearchImportForm(importParms)
    myform.processData()
    return




    importParms = {
        'queryPrefix' : 'CS51',
        'hitPrefix' : 'NCBI',
        'hitAccessionRegexp' : ('^\w*\|(\w+)\.?\d*\|','^pir\|\|(\w+)\.?\d*' , '^prf\|\|(\w+)\.?\d*'),
        'queryAccessionRegexp' : None,
        'checkExistingHits' : True,
        'createMissingQueries' : False,
        'createMissingHits' : True,
        'querySequenceType' : 'DNA SEQUENCE',
        'hitSequenceType' : 'PROTEIN SEQUENCE',
        'databaselsid' : 'NCBI.Non-redundant Protein (NR)',
        'blastprotocollsid' : 'Protocol.blastx.AgResearch CS51 sheep EST contigs against NR',
        'datasourcetype' : 'blastx_agresearch_csv',
        'physicalsourceuri' : '/data/home/seqstore/agbrdf/blastresults/cs51.seq_nr.csv',
        'studytype' : 'Blast',
        'studydescription' : 'Blastx of AgResearch CS51 sheep EST contigs against NCBI nr',
        'fieldNamesRow' : 0
    }

    myform = databaseSearchImportForm(importParms)
    myform.processData()
    return


    importParms = {
        'queryPrefix' : 'NCBI',
        'hitPrefix' : 'NCBI',
        'hitAccessionRegexp' : ('^ref\|(\w+)\.?\d*\|?', '^gi\|\d+\|ref\|(\w+)\.?\d*\|?'),
        'queryAccessionRegexp' : None,
        'checkExistingHits' : True,
        'createMissingQueries' : True,
        'createMissingHits' : True,
        'querySequenceType' : 'mRNA SEQUENCE',
        'hitSequenceType' : 'mRNA SEQUENCE',
        'databaselsid' : 'NCBI.Human mRNA Refseqs',
        'blastprotocollsid' : 'Protocol.tblastx.Rabbit Array Target Sequences against Human Refseqs',
        'datasourcetype' : 'blastx_agresearch_csv',
        'physicalsourceuri' : '/data/home/seqstore/agbrdf/blastresults/Oryctolagus_cuniculus.RABBIT.53.cdna.all.fa_hs.fna.csv',
        'studytype' : 'Blast',
        'studydescription' : 'Tblastx of Rabbit Array Target Sequences against Human Refseqs',
        'fieldNamesRow' : 0
    }

    myform = databaseSearchImportForm(importParms)
    myform.processData()
    return


    importParms = {
        'queryPrefix' : 'NCBI',
        'hitPrefix' : 'NCBI',
        'hitAccessionRegexp' : ('^ref\|(\w+)\.?\d*\|?', '^gi\|\d+\|ref\|(\w+)\.?\d*\|?'),
        'queryAccessionRegexp' : ('\|gb\|(\w+)\.?\d*\|?','\|ref\|(\w+)\.?\d*\|?','\|emb\|(\w+)\.?\d*\|?','\|dbj\|(\w+)\.?\d*\|?'),
        'checkExistingHits' : True,
        'createMissingQueries' : True,
        'createMissingHits' : True,
        'querySequenceType' : 'mRNA SEQUENCE',
        'hitSequenceType' : 'mRNA SEQUENCE',
        'databaselsid' : 'NCBI.Human mRNA Refseqs',
        'blastprotocollsid' : 'Protocol.tblastx.Rabbit Array Target Sequences against Human Refseqs',
        'datasourcetype' : 'blastx_agresearch_csv',
        'physicalsourceuri' : '/data/home/seqstore/agbrdf/blastresults/ncbi_rabbit.fa_hs.fna.csv',
        'studytype' : 'Blast',
        'studydescription' : 'Tblastx of Rabbit Array Target Sequences against Human Refseqs',
        'fieldNamesRow' : 0
    }

    myform = databaseSearchImportForm(importParms)
    myform.processData()
    return


    importParms = {
        'queryPrefix' : 'CS14',
        'hitPrefix' : 'NCBI',
        'hitAccessionRegexp' :   ('^ref\|(\w+)\.?\d*\|?', '^gi\|\d+\|ref\|(\w+)\.?\d*\|?'), # example : ref|NM_001075746.1|,
        'queryAccessionRegexp' : None,
        'checkExistingHits' : True,
        'createMissingQueries' : False,
        'createMissingHits' : True,
        'querySequenceType' : 'mRNA SEQUENCE',
        'hitSequenceType' : 'mRNA SEQUENCE',
        'databaselsid' : 'NCBI.Human mRNA Refseqs',
        'blastprotocollsid' : 'Protocol.blastn.CS14 Bovine EST contigs against Human Refseqs',
        'datasourcetype' : 'blastn_agresearch_csv',
        'physicalsourceuri' : '/data/home/seqstore/agbrdf/blastresults/cs14.seq_hs.fna.csv',
        'studytype' : 'Blast',
        'studydescription' : 'Blastn of AgResearch CS14 EST contigs against Human mRNA refseqs',
        'fieldNamesRow' : 0
    }

    myform = databaseSearchImportForm(importParms)
    myform.processData()

    return



    importParms = {
        'queryPrefix' : 'CS20',
        'hitPrefix' : 'NCBI',
        'hitAccessionRegexp' :   ('^ref\|(\w+)\.?\d*\|?', '^gi\|\d+\|ref\|(\w+)\.?\d*\|?'), # example : ref|NM_001075746.1|,
        'queryAccessionRegexp' : None,
        'checkExistingHits' : True,
        'createMissingQueries' : False,
        'createMissingHits' : True,
        'querySequenceType' : 'mRNA SEQUENCE',
        'hitSequenceType' : 'mRNA SEQUENCE',
        'databaselsid' : 'NCBI.Human mRNA Refseqs',
        'blastprotocollsid' : 'Protocol.blastn.CS20 Bovine EST contigs against Human Refseqs',
        'datasourcetype' : 'blastn_agresearch_csv',
        'physicalsourceuri' : '/data/home/seqstore/agbrdf/blastresults/cs20.seq_hs.fna.csv',
        'studytype' : 'Blast',
        'studydescription' : 'Blastn of AgResearch CS20 EST contigs against Human mRNA refseqs',
        'fieldNamesRow' : 0
    }

    myform = databaseSearchImportForm(importParms)
    myform.processData()

    return


    importParms = {
        'queryPrefix' : 'Affymetrix',
        'hitPrefix' : 'Btau4.GLEAN.DNA',
        'hitAccessionRegexp' :   None,
        'queryAccessionRegexp' : ('([^ ;]+)',),
        'checkExistingHits' : False,
        'createMissingQueries' : False,
        'createMissingHits' : False,
        'querySequenceType' : 'mRNA SEQUENCE',
        'hitSequenceType' : 'mRNA SEQUENCE',
        'databaselsid' : 'Btau4.GLEAN CDS',
        'blastprotocollsid' : 'Protocol.blastn.Bovine Affy chip Consensus against Btau4 GLEAN CDS',
        'datasourcetype' : 'blastn_agresearch_csv',
        'physicalsourceuri' : '/data/home/seqstore/agbrdf/blastresults/Bovine_consensus_bovine_glean5_cds_Nov08.csv',
        'studytype' : 'Blast',
        'studydescription' : 'Blastn of Bovine Affy chip consensus seqs against Btau4 GLEAN CDS',
        'fieldNamesRow' : 0
    }

    myform = databaseSearchImportForm(importParms)
    myform.processData()

    return


    importParms = {
        'queryPrefix' : 'CS39',
        'hitPrefix' : 'NCBI',
        'hitAccessionRegexp' : ('^\w*\|(\w+)\.?\d*\|','^pir\|\|(\w+)\.?\d*' , '^prf\|\|(\w+)\.?\d*'),
        'queryAccessionRegexp' : None,
        'checkExistingHits' : True,
        'createMissingQueries' : False,
        'createMissingHits' : True,
        'querySequenceType' : 'DNA SEQUENCE',
        'hitSequenceType' : 'PROTEIN SEQUENCE',
        'databaselsid' : 'NCBI.Non-redundant Protein (NR)',
        'blastprotocollsid' : 'Protocol.blastx.AgResearch CS39 sheep EST contigs against NR',
        'datasourcetype' : 'blastx_agresearch_csv',
        'physicalsourceuri' : '/data/home/seqstore/agbrdf/blastresults/cs39.seq_nr.csv',
        'studytype' : 'Blast',
        'studydescription' : 'Blastx of AgResearch CS39 sheep EST contigs against NCBI nr',
        'fieldNamesRow' : 0
    }

    myform = databaseSearchImportForm(importParms)
    myform.processData()
    return



    importParms = {
        'queryPrefix' : 'CS37',
        'hitPrefix' : 'NCBI',
        'hitAccessionRegexp' : ('^\w*\|(\w+)\.?\d*\|','^pir\|\|(\w+)\.?\d*' , '^prf\|\|(\w+)\.?\d*'),
        'queryAccessionRegexp' : None,
        'checkExistingHits' : True,
        'createMissingQueries' : False,
        'createMissingHits' : True,
        'querySequenceType' : 'DNA SEQUENCE',
        'hitSequenceType' : 'PROTEIN SEQUENCE',
        'databaselsid' : 'NCBI.Non-redundant Protein (NR)',
        'blastprotocollsid' : 'Protocol.blastx.AgResearch CS37 Ryegrass EST contigs against NR',
        'datasourcetype' : 'blastx_agresearch_csv',
        'physicalsourceuri' : '/data/home/seqstore/agbrdf/blastresults/cs37.seq_nr.csv',
        'studytype' : 'Blast',
        'studydescription' : 'Blastx of AgResearch CS37 ryegrass  EST contigs against NCBI nr',
        'fieldNamesRow' : 0
    }

    myform = databaseSearchImportForm(importParms)
    myform.processData()
    return


    importParms = {
        'queryPrefix' : 'CS37',
        'hitPrefix' : 'NCBI',
        'hitAccessionRegexp' : ('^gb\|(\w+)\.?\d*\|',), # example : gb|BJ214948.1|BJ214948
        'queryAccessionRegexp' : None,
        'checkExistingHits' : False,
        'createMissingQueries' : False,
        'createMissingHits' : True,
        'querySequenceType' : 'DNA SEQUENCE',
        'hitSequenceType' : 'DNA SEQUENCE',
        'databaselsid' : 'NCBI.Genbank',
        'blastprotocollsid' : 'Protocol.blastn.CS37 Ryegrass sequences against NCBI Wheat ESTs',
        'datasourcetype' : 'blastn_agresearch_csv',
        'physicalsourceuri' : '/data/home/seqstore/agbrdf/blastresults/cs37.seq_wheatseqs20102008.fa.csv',
        'studytype' : 'Blast',
        'studydescription' : 'Blastn of CS37 Ryegrass contigs against public Wheat ESTs',
        'fieldNamesRow' : 0
    }

    myform = databaseSearchImportForm(importParms)
    myform.processData()
    return


    importParms = {
        'queryPrefix' : 'CS37',
        'hitPrefix' : 'DFCI.FaGI',
        'hitAccessionRegexp' : None,
        'queryAccessionRegexp' : None,
        'checkExistingHits' : False,
        'createMissingQueries' : False,
        'createMissingHits' : True,
        'querySequenceType' : 'DNA SEQUENCE',
        'hitSequenceType' : 'DNA SEQUENCE',
        'databaselsid' : 'DFCI.Tall Fescue Gene Index',
        'blastprotocollsid' : 'Protocol.blastn.CS37 Ryegrass sequences against DFCI Tall Fescue',
        'datasourcetype' : 'blastn_agresearch_csv',
        'physicalsourceuri' : '/data/home/seqstore/agbrdf/blastresults/cs37.seq_Festuca_arundinacea.csv',
        'studytype' : 'Blast',
        'studydescription' : 'Blastn of CS37 Ryegrass contigs against DFCI Festuca_arundinacea (tall fescue) gene index',
        'fieldNamesRow' : 0
    }

    myform = databaseSearchImportForm(importParms)
    myform.processData()
    return



    importParms = {
        'queryPrefix' : 'CS37',
        'hitPrefix' : 'DFCI.TaGI',
        'hitAccessionRegexp' : None,
        'queryAccessionRegexp' : None,
        'checkExistingHits' : False,
        'createMissingQueries' : False,
        'createMissingHits' : True,
        'querySequenceType' : 'DNA SEQUENCE',
        'hitSequenceType' : 'DNA SEQUENCE',
        'databaselsid' : 'DFCI.Wheat Gene Index',
        'blastprotocollsid' : 'Protocol.blastn.CS37 Ryegrass sequences against DFCI Wheat',
        'datasourcetype' : 'blastn_agresearch_csv',
        'physicalsourceuri' : '/data/home/seqstore/agbrdf/blastresults/cs37.seq_Triticum_aestivum.csv',
        'studytype' : 'Blast',
        'studydescription' : 'Blastn of CS37 Ryegrass contigs against DFCI Triticum_aestivum (wheat) gene index',
        'fieldNamesRow' : 0
    }

    myform = databaseSearchImportForm(importParms)
    myform.processData()
    return


    importParms = {
        'queryPrefix' : 'CS37',
        'hitPrefix' : 'DFCI.OsGI',
        'hitAccessionRegexp' : None,
        'queryAccessionRegexp' : None,
        'checkExistingHits' : False,
        'createMissingQueries' : False,
        'createMissingHits' : True,
        'querySequenceType' : 'DNA SEQUENCE',
        'hitSequenceType' : 'DNA SEQUENCE',
        'databaselsid' : 'DFCI.Rice Gene Index',
        'blastprotocollsid' : 'Protocol.blastn.CS37 Ryegrass sequences against DFCI Rice',
        'datasourcetype' : 'blastn_agresearch_csv',
        'physicalsourceuri' : '/data/home/seqstore/agbrdf/blastresults/cs37.seq_Oryza_sativa.csv',
        'studytype' : 'Blast',
        'studydescription' : 'Blastn of CS37 Ryegrass contigs against DFCI Oryza sativa (rice) gene index',
        'fieldNamesRow' : 0
    }

    myform = databaseSearchImportForm(importParms)
    myform.processData()
    return


    importParms = {
        'queryPrefix' : 'AgResearch.Ovine',
        'hitPrefix' : 'NCBI',
        'hitAccessionRegexp' :   ('^ref\|(\w+)\.?\d*\|?', '^gi\|\d+\|ref\|(\w+)\.?\d*\|?'), # example : ref|NM_001075746.1|,
        'queryAccessionRegexp' : None,
        'checkExistingHits' : False,
        'createMissingQueries' : False,
        'createMissingHits' : True,
        'querySequenceType' : 'mRNA SEQUENCE',
        'hitSequenceType' : 'mRNA SEQUENCE',
        'databaselsid' : 'NCBI.Human mRNA Refseqs',
        'blastprotocollsid' : 'Protocol.blastn.Sheep ESTs against Human Refseqs',
        'datasourcetype' : 'blastn_agresearch_csv',
        'physicalsourceuri' : '/data/home/seqstore/agbrdf/sheepEST.fa_hs.fna.csv',
        'studytype' : 'Blast',
        'studydescription' : 'Blastn of AgResearch Sheep ESTs against Human mRNA refseqs',
        'fieldNamesRow' : 0
    }

    myform = databaseSearchImportForm(importParms)
    myform.processData()

    return


    importParms = {
        'queryPrefix' : 'CS39',
        'hitPrefix' : 'NCBI',
        'hitAccessionRegexp' : ('^\w*\|(\w+)\.?\d*\|','^pir\|\|(\w+)\.?\d*' , '^prf\|\|(\w+)\.?\d*'),
        'queryAccessionRegexp' : None,
        'checkExistingHits' : True,
        'createMissingQueries' : False,
        'createMissingHits' : True,
        'querySequenceType' : 'DNA SEQUENCE',
        'hitSequenceType' : 'PROTEIN SEQUENCE',
        'databaselsid' : 'NCBI.Non-redundant Protein (NR)',
        'blastprotocollsid' : 'Protocol.blastx.AgResearch CS39 sheep EST contigs against NR',
        'datasourcetype' : 'blastx_agresearch_csv',
        'physicalsourceuri' : '/data/home/seqstore/agbrdf/cs39.seq_nr.csv',
        'studytype' : 'Blast',
        'studydescription' : 'Blastx of AgResearch CS39 sheep EST contigs against NCBI nr',
        'fieldNamesRow' : 0
    }

    myform = databaseSearchImportForm(importParms)
    myform.processData()
    return


    importParms = {
        'queryPrefix' : 'CS39',
        'hitPrefix' : 'NCBI',
        'hitAccessionRegexp' :   ('^ref\|(\w+)\.?\d*\|?', '^gi\|\d+\|ref\|(\w+)\.?\d*\|?'), # example : ref|NM_001075746.1|,
        'queryAccessionRegexp' : None,
        'checkExistingHits' : True,
        'createMissingQueries' : False,
        'createMissingHits' : True,
        'querySequenceType' : 'mRNA SEQUENCE',
        'hitSequenceType' : 'mRNA SEQUENCE',
        'databaselsid' : 'NCBI.Human mRNA Refseqs',
        'blastprotocollsid' : 'Protocol.blastn.CS39 Bovine EST contigs against Human Refseqs',
        'datasourcetype' : 'blastn_agresearch_csv',
        'physicalsourceuri' : '/data/home/seqstore/agbrdf/cs39.seq_hs.fna.csv',
        'studytype' : 'Blast',
        'studydescription' : 'Blastn of AgResearch CS39 EST contigs against Human mRNA refseqs',
        'fieldNamesRow' : 0
    }

    myform = databaseSearchImportForm(importParms)
    myform.processData()

    return



    importParms = {
        'queryPrefix' : 'CS34',
        'hitPrefix' : 'NCBI',
        'hitAccessionRegexp' :   ('^ref\|(\w+)\.?\d*\|?', '^gi\|\d+\|ref\|(\w+)\.?\d*\|?'), # example : ref|NM_001075746.1|,
        'queryAccessionRegexp' : None,
        'checkExistingHits' : True,
        'createMissingQueries' : False,
        'createMissingHits' : True,
        'querySequenceType' : 'mRNA SEQUENCE',
        'hitSequenceType' : 'mRNA SEQUENCE',
        'databaselsid' : 'NCBI.Human mRNA Refseqs',
        'blastprotocollsid' : 'Protocol.blastn.CS34 Bovine EST contigs against Human Refseqs',
        'datasourcetype' : 'blastn_agresearch_csv',
        'physicalsourceuri' : '/data/home/seqstore/agbrdf/smfoldcontigs.fa.out.csv',
        'studytype' : 'Blast',
        'studydescription' : 'Blastn of AgResearch CS34 EST contigs against Human mRNA refseqs',
        'fieldNamesRow' : 0
    }

    myform = databaseSearchImportForm(importParms)
    myform.processData()

    return


    importParms = {
        'queryPrefix' : 'AgResearch.Bovine',
        'hitPrefix' : 'NCBI',
        'hitAccessionRegexp' :   ('^ref\|(\w+)\.?\d*\|?', '^gi\|\d+\|ref\|(\w+)\.?\d*\|?'), # example : ref|NM_001075746.1|,
        'queryAccessionRegexp' : None,
        'checkExistingHits' : True,
        'createMissingQueries' : False,
        'createMissingHits' : True,
        'querySequenceType' : 'mRNA SEQUENCE',
        'hitSequenceType' : 'mRNA SEQUENCE',
        'databaselsid' : 'NCBI.Human mRNA Refseqs',
        'blastprotocollsid' : 'Protocol.blastn.Bovine ESTs against Human mRNA refseqs',
        'datasourcetype' : 'blastn_agresearch_csv',
        'physicalsourceuri' : '/data/home/seqstore/agbrdf/smfold.fa.out.csv',
        'studytype' : 'Blast',
        'studydescription' : 'Blastn of AgResearch Cattle ESTs against Human mRNA refseqs',
        'fieldNamesRow' : 0
    }

    myform = databaseSearchImportForm(importParms)
    myform.processData()

    return



    importParms = {
        'queryPrefix' : 'CS34',
        'hitPrefix' : 'NCBI',
        'hitAccessionRegexp' :   ('^ref\|(\w+)\.?\d*\|?', '^gi\|\d+\|ref\|(\w+)\.?\d*\|?'), # example : ref|NM_001075746.1|,
        'queryAccessionRegexp' : None,
        'checkExistingHits' : True,
        'createMissingQueries' : False,
        'createMissingHits' : True,
        'querySequenceType' : 'mRNA SEQUENCE',
        'hitSequenceType' : 'mRNA SEQUENCE',
        'databaselsid' : 'NCBI.Human mRNA Refseqs',
        'blastprotocollsid' : 'Protocol.blastn.CS34 Bovine EST contigs against Human Refseqs',
        'datasourcetype' : 'blastn_agresearch_csv',
        'physicalsourceuri' : '/data/home/seqstore/agbrdf/smcontigs1.fa.out.csv',
        'studytype' : 'Blast',
        'studydescription' : 'Blastn of AgResearch CS34 EST contigs against Human mRNA refseqs',
        'fieldNamesRow' : 0
    }

    myform = databaseSearchImportForm(importParms)
    myform.processData()

    return


    importParms = {
        'queryPrefix' : 'AgResearch.Bovine',
        'hitPrefix' : 'NCBI',
        'hitAccessionRegexp' :   ('^ref\|(\w+)\.?\d*\|?', '^gi\|\d+\|ref\|(\w+)\.?\d*\|?'), # example : ref|NM_001075746.1|,
        'queryAccessionRegexp' : None,
        'checkExistingHits' : True,
        'createMissingQueries' : False,
        'createMissingHits' : True,
        'querySequenceType' : 'mRNA SEQUENCE',
        'hitSequenceType' : 'mRNA SEQUENCE',
        'databaselsid' : 'NCBI.Human mRNA Refseqs',
        'blastprotocollsid' : 'Protocol.blastn.Bovine ESTs against Human mRNA refseqs',
        'datasourcetype' : 'blastn_agresearch_csv',
        'physicalsourceuri' : '/data/home/seqstore/agbrdf/smmusclediff.fa.out.csv',
        'studytype' : 'Blast',
        'studydescription' : 'Blastn of AgResearch Cattle ESTs against Human mRNA refseqs',
        'fieldNamesRow' : 0
    }

    myform = databaseSearchImportForm(importParms)
    myform.processData()

    return


    importParms = {
        'queryPrefix' : 'AgResearch.Bovine',
        'hitPrefix' : 'NCBI',
        'hitAccessionRegexp' :   ('^ref\|(\w+)\.?\d*\|?', '^gi\|\d+\|ref\|(\w+)\.?\d*\|?'), # example : ref|NM_001075746.1|,
        'queryAccessionRegexp' : None,
        'checkExistingHits' : True,
        'createMissingQueries' : False,
        'createMissingHits' : True,
        'querySequenceType' : 'mRNA SEQUENCE',
        'hitSequenceType' : 'mRNA SEQUENCE',
        'databaselsid' : 'NCBI.Human mRNA Refseqs',
        'blastprotocollsid' : 'Protocol.blastn.Bovine ESTs against Human mRNA refseqs',
        'datasourcetype' : 'blastn_agresearch_csv',
        'physicalsourceuri' : '/data/home/seqstore/agbrdf/smliverdiff.fa.out.csv',
        'studytype' : 'Blast',
        'studydescription' : 'Blastn of AgResearch Cattle ESTs against Human mRNA refseqs',
        'fieldNamesRow' : 0
    }

    myform = databaseSearchImportForm(importParms)
    myform.processData()

    return



    importParms = {
        'queryPrefix' : None,
        'hitPrefix' : 'NCBI',
        'hitAccessionRegexp' : ('^\w*\|(\w+)\.?\d*\|','^pir\|\|(\w+)\.?\d*' , '^prf\|\|(\w+)\.?\d*'),
        'queryAccessionRegexp' : None,
        'checkExistingHits' : False,
        'createMissingQueries' : False,
        'createMissingHits' : True,
        'querySequenceType' : 'DNA SEQUENCE',
        'hitSequenceType' : 'PROTEIN SEQUENCE',
        'databaselsid' : 'NCBI.Non-redundant Protein (NR)',
        'blastprotocollsid' : 'Protocol.blastx.AgResearch CS39 sheep EST contigs against NR',
        'datasourcetype' : 'blastx_agresearch_csv',
        'physicalsourceuri' : '/data/home/seqstore/agbrdf/print139NoHits.fa_nr.csv',
        'studytype' : 'Blast',
        'studydescription' : 'Blastx of AgResearch CS39 sheep EST contigs against NCBI nr',
        'fieldNamesRow' : 0
    }

    myform = databaseSearchImportForm(importParms)
    myform.processData()
    return


    importParms = {
        'queryPrefix' : 'CS39',
        'hitPrefix' : 'OAR',
        'hitAccessionRegexp' :   None,
        'queryAccessionRegexp' : None,
        'checkExistingHits' : False,
        'createMissingQueries' : True,
        'createMissingHits' : True,
        'querySequenceType' : 'mRNA SEQUENCE',
        'hitSequenceType' : 'genomic DNA',
        'databaselsid' : 'SheepGenomeV1',
        'blastprotocollsid' : 'Protocol.blastn.CS39 ESTs against Sheep Genome',
        'datasourcetype' : 'blastn_agresearch_csv',
        'physicalsourceuri' : '/data/home/seqstore/agbrdf/cs39.seq.masked_OAR',
        'studytype' : 'Blast',
        'studydescription' : 'Blastn of CS39 sheep ESTs against Sheep Genome version 1',
        'fieldNamesRow' : 0
    }

    myform = databaseSearchImportForm(importParms)
    myform.processData()

    return



    importParms = {
        'queryPrefix' : 'Affymetrix',
        'hitPrefix' : 'NCBI',
        'hitAccessionRegexp' :   ('^ref\|(\w+)\.?\d*\|?', '^gi\|\d+\|ref\|(\w+)\.?\d*\|?'), # example : ref|NM_001075746.1|,
        'queryAccessionRegexp' : ('([^ ;]+)',),
        'checkExistingHits' : True,
        'createMissingQueries' : False,
        'createMissingHits' : True,
        'querySequenceType' : 'Affy Target Oligo',
        'hitSequenceType' : 'mRNA SEQUENCE',
        'databaselsid' : 'NCBI.Human mRNA Refseqs',
        'blastprotocollsid' : 'Protocol.blastn.Bovine Affy chip Targets against Human Refseqs',
        'datasourcetype' : 'blastn_agresearch_csv',
        'physicalsourceuri' : '/data/home/seqstore/agbrdf/affy/Bovine_target_vs_hs.fna.csv', 
        'studytype' : 'Blast',
        'studydescription' : 'Blastn of Affy chip Targets against Human Refseqs',
        'fieldNamesRow' : 0
    }

    myform = databaseSearchImportForm(importParms)
    myform.processData()

    return


    importParms = {
        'queryPrefix' : 'Affymetrix',
        'hitPrefix' : 'CS34',
        'hitAccessionRegexp' :   None,
        'queryAccessionRegexp' : ('([^ ;]+)',),
        'checkExistingHits' : True,
        'createMissingQueries' : False,
        'createMissingHits' : False,
        'querySequenceType' : 'Affy Target Oligo',
        'hitSequenceType' : 'mRNA SEQUENCE',
        'databaselsid' : 'AgResearch.CS34',
        'blastprotocollsid' : 'Protocol.blastn.Bovine Affy chip Targets against AgResearch CS34 contigs',
        'datasourcetype' : 'blastn_agresearch_csv',
        'physicalsourceuri' : '/data/home/seqstore/agbrdf/affy/Bovine_target.fa_cs34.seq.csv',
        'studytype' : 'Blast',
        'studydescription' : 'Blastn of Bovine Affy chip Targets against AgResearch Bovine CS34 Contigs',
        'fieldNamesRow' : 0
    }

    myform = databaseSearchImportForm(importParms)
    myform.processData()

    return



    importParms = {
        'queryPrefix' : 'Affymetrix',
        'hitPrefix' : 'Btau4.GLEAN.DNA',
        'hitAccessionRegexp' :   None,
        'queryAccessionRegexp' : ('([^ ;]+)',),
        'checkExistingHits' : True,
        'createMissingQueries' : False,
        'createMissingHits' : True,
        'querySequenceType' : 'Affy Target Oligo',
        'hitSequenceType' : 'mRNA SEQUENCE',
        'databaselsid' : 'Btau4.GLEAN CDS',
        'blastprotocollsid' : 'Protocol.blastn.Bovine Affy chip Targets against Btau4 GLEAN CDS',
        'datasourcetype' : 'blastn_agresearch_csv',
        'physicalsourceuri' : '/data/home/seqstore/agbrdf/affy/Bovine_target_vs_bovine_glean5_cds.csv',
        'studytype' : 'Blast',
        'studydescription' : 'Blastn of Bovine Affy chip Targets against Btau4 GLEAN CDS',
        'fieldNamesRow' : 0
    }

    myform = databaseSearchImportForm(importParms)
    myform.processData()

    return


    importParms = {
        'queryPrefix' : 'Affymetrix',
        'hitPrefix' : 'NCBI',
        'hitAccessionRegexp' :   ('^ref\|(\w+)\.?\d*\|?', '^gi\|\d+\|ref\|(\w+)\.?\d*\|?'), # example : ref|NM_001075746.1|,
        'queryAccessionRegexp' : ('([^ ;]+)',),
        'checkExistingHits' : True,
        'createMissingQueries' : False,
        'createMissingHits' : True,
        'querySequenceType' : 'Affy Target Oligo',
        'hitSequenceType' : 'mRNA SEQUENCE',
        'databaselsid' : 'NCBI.Bovine mRNA Refseqs',
        'blastprotocollsid' : 'Protocol.blastn.Bovine Affy chip Targets against Bovine Refseqs',
        'datasourcetype' : 'blastn_agresearch_csv',
        'physicalsourceuri' : '/data/home/seqstore/agbrdf/affy/Bovine_target_vs_bt.fna.csv',
        'studytype' : 'Blast',
        'studydescription' : 'Blastn of Bovine Affy chip Targets against Bovine Refseqs',
        'fieldNamesRow' : 0
    }

    myform = databaseSearchImportForm(importParms)
    myform.processData()

    return



    importParms = {
        'queryPrefix' : 'Affymetrix',
        'hitPrefix' : 'DFCI',
        'hitAccessionRegexp' :  None,
        'queryAccessionRegexp' : ('([^ ;]+)',),
        'checkExistingHits' : True,
        'createMissingQueries' : False,
        'createMissingHits' : True,
        'querySequenceType' : 'Affy Target Oligo',
        'hitSequenceType' : 'mRNA SEQUENCE',
        'databaselsid' : 'DFCI.Cattle Gene Index',
        'blastprotocollsid' : 'Protocol.blastn.Bovine Affy chip Targets against DFCI Cattle Gene Index',
        'datasourcetype' : 'blastn_agresearch_csv',
        'physicalsourceuri' : '/data/home/seqstore/agbrdf/affy/Bovine_target.fa_BTGI.091806.csv',
        'studytype' : 'Blast',
        'studydescription' : 'Bovine Affy chip Targets against DFCI Cattle Gene Index',
        'fieldNamesRow' : 0
    }

    myform = databaseSearchImportForm(importParms)
    myform.processData()

    return

    importParms = {
        'queryPrefix' : 'Affymetrix',
        'hitPrefix' : 'NCBI',
        'hitAccessionRegexp' :   ('^ref\|(\w+)\.?\d*\|?', '^gi\|\d+\|ref\|(\w+)\.?\d*\|?'), # example : ref|NM_001075746.1|,
        'queryAccessionRegexp' : ('([^ ;]+)',),
        'checkExistingHits' : True,
        'createMissingQueries' : False,
        'createMissingHits' : True,
        'querySequenceType' : 'Affy Target Oligo',
        'hitSequenceType' : 'mRNA SEQUENCE',
        'databaselsid' : 'NCBI.Mouse mRNA Refseqs',
        'blastprotocollsid' : 'Protocol.blastn.Bovine Affy chip Targets against Mouse Refseqs',
        'datasourcetype' : 'blastn_agresearch_csv',
        'physicalsourceuri' : '/data/home/seqstore/agbrdf/affy/Bovine_target_vs_mouse.fna.csv',
        'studytype' : 'Blast',
        'studydescription' : 'Blastn of Affy chip Targets against Mouse Refseqs',
        'fieldNamesRow' : 0
    }

    myform = databaseSearchImportForm(importParms)
    myform.processData()

    return

    importParms = {
        'queryPrefix' : 'Affymetrix',
        'hitPrefix' : 'NCBI',
        'hitAccessionRegexp' :   ('^ref\|(\w+)\.?\d*\|?', '^gi\|\d+\|ref\|(\w+)\.?\d*\|?'), # example : ref|NM_001075746.1|,
        'queryAccessionRegexp' : ('([^ ;]+)',),
        'checkExistingHits' : True,
        'createMissingQueries' : False,
        'createMissingHits' : True,
        'querySequenceType' : 'Affy Target Oligo',
        'hitSequenceType' : 'mRNA SEQUENCE',
        'databaselsid' : 'NCBI.Human mRNA Refseqs',
        'blastprotocollsid' : 'Protocol.blastn.Bovine Affy chip Targets against Human Refseqs',
        'datasourcetype' : 'blastn_agresearch_csv',
        'physicalsourceuri' : '/data/home/seqstore/agbrdf/affy/Bovine_target_vs_bt.fna.csv', #<----- oops !
        'studytype' : 'Blast',
        'studydescription' : 'Blastn of Affy chip Targets against Human Refseqs',
        'fieldNamesRow' : 0
    }

    myform = databaseSearchImportForm(importParms)
    myform.processData()

    return



    importParms = {
        'queryPrefix' : 'CS34',
        'hitPrefix' : 'NCBI',
        'hitAccessionRegexp' :   ('^ref\|(\w+)\.?\d*\|?', '^gi\|\d+\|ref\|(\w+)\.?\d*\|?'), # example : ref|NM_001075746.1|,
        'queryAccessionRegexp' : None,
        'checkExistingHits' : True,
        'createMissingQueries' : False,
        'createMissingHits' : True,
        'querySequenceType' : 'mRNA SEQUENCE',
        'hitSequenceType' : 'mRNA SEQUENCE',
        'databaselsid' : 'NCBI.Human mRNA Refseqs',
        'blastprotocollsid' : 'Protocol.blastn.CS34 Bovine EST contigs against Human Refseqs',
        'datasourcetype' : 'blastn_agresearch_csv',
        'physicalsourceuri' : '/data/home/seqstore/agbrdf/bovine/cs34.seq_hs.fna.csv',
        'studytype' : 'Blast',
        'studydescription' : 'Blastn of AgResearch CS34 EST contigs against Human mRNA refseqs',
        'fieldNamesRow' : 0
    }

    myform = databaseSearchImportForm(importParms)
    myform.processData()

    return


    importParms = {
        'queryPrefix' : 'AgResearch.Bovine',
        'hitPrefix' : 'NCBI',
        'hitAccessionRegexp' :   ('^ref\|(\w+)\.?\d*\|?', '^gi\|\d+\|ref\|(\w+)\.?\d*\|?'), # example : ref|NM_001075746.1|,
        'queryAccessionRegexp' : None,
        'checkExistingHits' : False,
        'createMissingQueries' : False,
        'createMissingHits' : True,
        'querySequenceType' : 'mRNA SEQUENCE',
        'hitSequenceType' : 'mRNA SEQUENCE',
        'databaselsid' : 'NCBI.Human mRNA Refseqs',
        'blastprotocollsid' : 'Protocol.blastn.Bovine ESTs against Human mRNA refseqs',
        'datasourcetype' : 'blastn_agresearch_csv',
        'physicalsourceuri' : '/data/home/seqstore/agbrdf/bovine/agbovine.seq_hs.fna.csv',
        'studytype' : 'Blast',
        'studydescription' : 'Blastn of AgResearch Cattle ESTs against Human mRNA refseqs',
        'fieldNamesRow' : 0
    }

    myform = databaseSearchImportForm(importParms)
    myform.processData()

    return


    importParms = {
        'queryPrefix' : 'CS34',
        'hitPrefix' : 'NCBI',
        'hitAccessionRegexp' :   ('^ref\|(\w+)\.?\d*\|?', '^gi\|\d+\|ref\|(\w+)\.?\d*\|?'), # example : ref|NM_001075746.1|,
        'queryAccessionRegexp' : None,
        'checkExistingHits' : False,
        'createMissingQueries' : False,
        'createMissingHits' : True,
        'querySequenceType' : 'mRNA SEQUENCE',
        'hitSequenceType' : 'mRNA SEQUENCE',
        'databaselsid' : 'NCBI.Bovine mRNA Refseqs',
        'blastprotocollsid' : 'Protocol.blastn.Bovine ESTs against CS34 Bos taurus mRNA refseqs',
        'datasourcetype' : 'blastn_agresearch_csv',
        'physicalsourceuri' : '/data/home/seqstore/agbrdf/bovine/cs34.seq_bt.fna.csv',
        'studytype' : 'Blast',
        'studydescription' : 'Blastn of AgResearch CS34 EST contigs against Bos taurus mRNA refseqs',
        'fieldNamesRow' : 0
    }

    myform = databaseSearchImportForm(importParms)
    myform.processData()

    return


    importParms = {
        'queryPrefix' : 'AgResearch.Bovine',
        'hitPrefix' : 'NCBI',
        'hitAccessionRegexp' :   ('^ref\|(\w+)\.?\d*\|?', '^gi\|\d+\|ref\|(\w+)\.?\d*\|?'), # example : ref|NM_001075746.1|,
        'queryAccessionRegexp' : None,
        'checkExistingHits' : False,
        'createMissingQueries' : False,
        'createMissingHits' : True,
        'querySequenceType' : 'mRNA SEQUENCE',
        'hitSequenceType' : 'mRNA SEQUENCE',
        'databaselsid' : 'NCBI.Bovine mRNA Refseqs',
        'blastprotocollsid' : 'Protocol.blastn.Bovine ESTs against Bos taurus mRNA refseqs',
        'datasourcetype' : 'blastn_agresearch_csv',
        'physicalsourceuri' : '/data/home/seqstore/agbrdf/bovine/agbovine.seq_bt.fna.csv',
        'studytype' : 'Blast',
        'studydescription' : 'Blastn of AgResearch Cattle ESTs against Bos taurus mRNA refseqs',
        'fieldNamesRow' : 0
    }

    myform = databaseSearchImportForm(importParms)
    myform.processData()

    return


    importParms = {
        'hitPrefix' : 'CS34',
        'queryPrefix' : 'Btau4.GLEAN.DNA',
        'hitAccessionRegexp' :  None,
        'queryAccessionRegexp' : None,
        'checkExistingHits' : False,
        'createMissingQueries' : False,
        'createMissingHits' : False,
        'querySequenceType' : 'mRNA SEQUENCE',
        'hitSequenceType' : 'mRNA SEQUENCE',
        'databaselsid' : 'AgResearch.CS34',
        'blastprotocollsid' : 'Protocol.blastn.Bovine CS34 Contigs against Btau4 GLEAN CDS',
        'datasourcetype' : 'blastn_agresearch_csv',
        'physicalsourceuri' : '/data/home/seqstore/agbrdf/nauman/bovine_glean5_cds.fa_cs34.seq.csv',
        'studytype' : 'Blast',
        'studydescription' : 'Reciprocal blastn of Btau4 GLEAN CDS against AgResearch CS34 Cattle EST contigs',
        'fieldNamesRow' : 0
    }

    myform = databaseSearchImportForm(importParms)
    myform.processData()

    return


    importParms = {
        'hitPrefix' : 'AgResearch.Bovine',
        'queryPrefix' : 'Btau4.GLEAN.DNA',
        'hitAccessionRegexp' :  None,
        'queryAccessionRegexp' : None,
        'checkExistingHits' : False,
        'createMissingQueries' : False,
        'createMissingHits' : False,
        'querySequenceType' : 'mRNA SEQUENCE',
        'hitSequenceType' : 'mRNA SEQUENCE',
        'databaselsid' : 'AgResearch.Bovine EST',
        'blastprotocollsid' : 'Protocol.blastn.Bovine ESTs against Btau4 GLEAN CDS',
        'datasourcetype' : 'blastn_agresearch_csv',
        'physicalsourceuri' : '/data/home/seqstore/agbrdf/nauman/bovine_glean5_cds.fa_agbovine.seq.csv',
        'studytype' : 'Blast',
        'studydescription' : 'Reciprocal Blastn of AgResearch Btau4 GLEAN CDS against Cattle ESTs',
        'fieldNamesRow' : 0
    }

    myform = databaseSearchImportForm(importParms)
    myform.processData()

    return



    importParms = {
        'queryPrefix' : 'AgResearch.Bovine',
        'hitPrefix' : 'Btau4.GLEAN.DNA',
        'hitAccessionRegexp' :  None,
        'queryAccessionRegexp' : None,
        'checkExistingHits' : False,
        'createMissingQueries' : False,
        'createMissingHits' : False,
        'querySequenceType' : 'mRNA SEQUENCE',
        'hitSequenceType' : 'mRNA SEQUENCE',
        'databaselsid' : 'Btau4.GLEAN CDS',
        'blastprotocollsid' : 'Protocol.blastn.Bovine ESTs against Btau4 GLEAN CDS',
        'datasourcetype' : 'blastn_agresearch_csv',
        'physicalsourceuri' : '/data/home/seqstore/agbrdf/nauman/agbovine.seq_bovine_glean5_cds.csv',
        'studytype' : 'Blast',
        'studydescription' : 'Blastn of AgResearch Cattle ESTs against Btau4 GLEAN CDS',
        'fieldNamesRow' : 0
    }

    myform = databaseSearchImportForm(importParms)
    myform.processData()

    return



    importParms = {
        'queryPrefix' : 'CS34',
        'hitPrefix' : 'Btau4.GLEAN.DNA',
        'hitAccessionRegexp' :  None,
        'queryAccessionRegexp' : None,
        'checkExistingHits' : False,
        'createMissingQueries' : False,
        'createMissingHits' : False,
        'querySequenceType' : 'mRNA SEQUENCE',
        'hitSequenceType' : 'mRNA SEQUENCE',
        'databaselsid' : 'Btau4.GLEAN CDS',
        'blastprotocollsid' : 'Protocol.blastn.Bovine CS34 Contigs against Btau4 GLEAN CDS',
        'datasourcetype' : 'blastn_agresearch_csv',
        'physicalsourceuri' : '/data/home/seqstore/agbrdf/nauman/cs34.seq_bovine_glean5_cds.csv',
        'studytype' : 'Blast',
        'studydescription' : 'Blastn of AgResearch CS34 Cattle EST contigs against Btau4 GLEAN CDS',
        'fieldNamesRow' : 0
    }

    myform = databaseSearchImportForm(importParms)
    myform.processData()

    return


    importParms = {
        'queryPrefix' : 'AFT',
        'hitPrefix' : 'Interpro',
        'hitAccessionRegexp' : None,
        'queryAccessionRegexp' : None,
        'checkExistingHits' : False,
        'createMissingQueries' : False,
        'createMissingHits' : True,
        'querySequenceType' : 'mRNA SEQUENCE',
        'hitSequenceType' : 'PROTEIN SEQUENCE MODEL',
        'databaselsid' : 'Interpro',
        'blastprotocollsid' : 'protocol.iprscan.Standard AgResearch fungal annotation iprscan protocol',
        'datasourcetype' : 'interpro_csv',
        'physicalsourceuri' : '/data/home/seqstore/agbrdf/interpro_fixed.csv',
        'studytype' : 'Interpro IPRSCAN',
        'studydescription' : 'Intepro iprscan of AFT chip-related sequences',
        'fieldNamesRow' : 1
    }


    myform = databaseSearchImportForm(importParms)
    myform.processData()

    return



    importParms = {
        'queryPrefix' : 'CS19',
        'hitPrefix' : 'NCBI',
        'hitAccessionRegexp' :  ('^gi\|\d+\|ref\|(\w+)\.?\d*\|?','^ref\|(\w+)\.?\d*\|?'), # example : gi|115496207|ref|NM_001075746.1|
        'queryAccessionRegexp' : None,
        'checkExistingHits' : False,
        'createMissingQueries' : False,
        'createMissingHits' : True,
        'querySequenceType' : 'mRNA SEQUENCE',
        'hitSequenceType' : 'mRNA SEQUENCE',
        'databaselsid' : 'NCBI.Bovine mRNA Refseqs',
        'blastprotocollsid' : 'Protocol.blastn.Standard Cervine Blastn protocol',
        'datasourcetype' : 'blastn_agresearch_csv',
        'physicalsourceuri' : '/data/home/seqstore/agbrdf/cs19.seq_bt.fna.csv',
        'studytype' : 'Blast',
        'studydescription' : 'Blastn of CS19 contigs against Bovine Refseqs',
        'fieldNamesRow' : 1
    }

    myform = databaseSearchImportForm(importParms)
    myform.processData()

    return




    importParms = {
        'queryPrefix' : 'CS19',
        'hitPrefix' : 'NCBI',
        'hitAccessionRegexp' :  ('^\w*\|(\w+)\.?\d*\|','^pir\|\|(\w+)\.?\d*' , '^prf\|\|(\w+)\.?\d*', '^sp\|\|(\w+)\.?\d*' ),
        'queryAccessionRegexp' : None,
        'checkExistingHits' : False,
        'createMissingQueries' : False,
        'createMissingHits' : True,
        'querySequenceType' : 'mRNA SEQUENCE',
        'hitSequenceType' : 'PROTEIN SEQUENCE',
        'databaselsid' : 'NCBI.Non-redundant Protein (NR)',
        'databasetype' : 'Protein sequence database',
        'blastprotocollsid' : 'Protocol.blastx.Standard Cervine Protein blast',
        'datasourcetype' : 'blastx_agresearch_csv',
        'physicalsourceuri' : '/data/home/seqstore/agbrdf/cs19nr.csv',
        'studytype' : 'Blast',
        'studydescription' : 'Blastx of all CS19 deer contigs against NR protein',
        'fieldNamesRow' : 1
    }

    myform = databaseSearchImportForm(importParms)
    myform.processData()

    return



    importParms = {
        'queryPrefix' : 'CS34',
        'hitPrefix' : 'NCBI',
        'hitAccessionRegexp' : ('^\w*\|(\w+)\.?\d*\|','^pir\|\|(\w+)\.?\d*' , '^prf\|\|(\w+)\.?\d*'),
        'queryAccessionRegexp' : None,
        'checkExistingHits' : False,
        'createMissingQueries' : False,
        'createMissingHits' : True,
        'querySequenceType' : 'DNA SEQUENCE',
        'hitSequenceType' : 'PROTEIN SEQUENCE',
        'databaselsid' : 'NCBI.Non-redundant Protein (NR)',
        'databasetype' : 'Protein sequence database',
        'blastprotocollsid' : 'Protocol.blastx.Standard Bovine Protein blast',
        'datasourcetype' : 'blastx_agresearch_csv',
        'physicalsourceuri' : '/home/seqstore/agbrdf/cs34.seq_nr.csv',
        'studytype' : 'Blast',
        'studydescription' : 'Blastx of Bovine CS34 EST contigs against NCBI nr'
    }



    importParms = {
        'queryPrefix' : 'Misc.Bacteria',
        'hitPrefix' : 'NCBI',
        'hitAccessionRegexp' :  ('^\w*\|(\w+)\.?\d*\|','^pir\|\|(\w+)\.?\d*' , '^prf\|\|(\w+)\.?\d*'),
        'queryAccessionRegexp' : None,
        'checkExistingHits' : False,
        'createMissingQueries' : False,
        'createMissingHits' : True,
        'querySequenceType' : 'PROTEIN SEQUENCE',
        'hitSequenceType' : 'PROTEIN SEQUENCE',
        'databaselsid' : 'NCBI.Non-redundant Protein (NR)',
        'blastprotocollsid' : 'Protocol.blastp.AFT Standard Blastp single top hit protocol',
        'datasourcetype' : 'blastx_agresearch_csv',
        'physicalsourceuri' : '/data/home/seqstore/agbrdf/B316ORFSall.csv',
        'studytype' : 'Blast',
        'studydescription' : 'Blastp of all ORFS of B316complete genome against NCBI NR Protein, restricting to top hit',
        'fieldNamesRow' : 1
    }


    myform = databaseSearchImportForm(importParms)
    myform.processData()

    return



    importParms = {
        'queryPrefix' : 'AFT',
        'hitPrefix' : 'NCBI',
        'hitAccessionRegexp' : None,
        'queryAccessionRegexp' : None,
        'checkExistingHits' : False,
        'createMissingQueries' : False,
        'createMissingHits' : True,
        'querySequenceType' : 'mRNA SEQUENCE',
        'hitSequenceType' : 'DNA SEQUENCE',
        'databaselsid' : 'NCBI.mRNA Refseqs',
        'blastprotocollsid' : 'Protocol.blastn.AFT Standard Blastn informative hits protocol',
        'datasourcetype' : 'blastn_agresearch_csv_moderated',
        'physicalsourceuri' : '/data/home/seqstore/agbrdf/fungal/chip_refseq_blastn.bls.tophit3.meaning2.csv',
        'studytype' : 'Blast',
        'studydescription' : 'Blastn of AFT chip-related sequences against NCBI mRNA refseqs, annotated with informative hits',
        'fieldNamesRow' : 1
    }


    myform = databaseSearchImportForm(importParms)
    myform.processData()

    return


    importParms = {
        'queryPrefix' : 'AFT',
        'hitPrefix' : 'MIPS',
        'hitAccessionRegexp' : None,
        'queryAccessionRegexp' : None,
        'checkExistingHits' : False,
        'createMissingQueries' : False,
        'createMissingHits' : True,
        'querySequenceType' : 'mRNA SEQUENCE',
        'hitSequenceType' : 'PROTEIN SEQUENCE',
        'databaselsid' : 'MIPS.Fusarium Genome Predicted Proteins',
        'blastprotocollsid' : 'Protocol.blastx.AFT Standard Blastx informative hits protocol',
        'datasourcetype' : 'blastx_agresearch_csv_moderated',
        'physicalsourceuri' : '/data/home/seqstore/agbrdf/fungal/FungalAffyChip_FGDB_blastx.csv',
        'studytype' : 'Blast',
        'studydescription' : 'Blastx of AFT chip-related sequences against MIPS Fusarium Genome Predicted Proteins, annotated with informative hits',
        'fieldNamesRow' : 1
    }


    myform = databaseSearchImportForm(importParms)
    myform.processData()

    return



    importParms = {
        'queryPrefix' : 'AFT',
        'hitPrefix' : 'NCBI',
        'hitAccessionRegexp' : None,
        'queryAccessionRegexp' : None,
        'checkExistingHits' : False,
        'createMissingQueries' : False,
        'createMissingHits' : True,
        'querySequenceType' : 'mRNA SEQUENCE',
        'hitSequenceType' : 'PROTEIN SEQUENCE',
        'databaselsid' : 'NCBI.Non-redundant Protein (NR)',
        'blastprotocollsid' : 'Protocol.blastx.AFT Standard Blastx informative hits protocol',
        'datasourcetype' : 'blastx_agresearch_csv_moderated',
        'physicalsourceuri' : '/data/home/seqstore/agbrdf/fungal/chip_nr_blastx.bls.tophit3.meaning2.csv',
        'studytype' : 'Blast',
        'studydescription' : 'Blastx of AFT chip-related sequences against NCBI nr, annotated with informative hits',
        'fieldNamesRow' : 1
    }



    myform = databaseSearchImportForm(importParms)
    myform.processData()

    return


    importParms = {
        'queryPrefix' : 'AFT',
        'hitPrefix' : 'NCBI',
        'hitAccessionRegexp' : None,
        'queryAccessionRegexp' : None,
        'checkExistingHits' : False,
        'createMissingQueries' : False,
        'createMissingHits' : True,
        'querySequenceType' : 'mRNA SEQUENCE',
        'hitSequenceType' : 'DNA SEQUENCE',
        'databaselsid' : 'NCBI.mRNA Refseqs',
        'blastprotocollsid' : 'Protocol.blastn.AFT Standard Blastn informative hits protocol',
        'datasourcetype' : 'blastn_agresearch_csv_moderated',
        'physicalsourceuri' : '/home/seqstore/agbrdf/fungal/chip_refseq_blastn.bls.tophit3.meaning2.csv',
        'studytype' : 'Blast',
        'studydescription' : 'Blastn of AFT chip-related sequences against mRNA Refseqs, annotated with informative hits',
        'fieldNamesRow' : 1
    }

    myform = databaseSearchImportForm(importParms)
    myform.processData()


    return


    importParms = {
        'queryPrefix' : 'AFT',
        'hitPrefix' : 'UniProt',
        'hitAccessionRegexp' : None,
        'queryAccessionRegexp' : None,
        'checkExistingHits' : False,
        'createMissingQueries' : False,
        'createMissingHits' : True,
        'querySequenceType' : 'mRNA SEQUENCE',
        'hitSequenceType' : 'PROTEIN SEQUENCE',
        'databaselsid' : 'UniProt.UniProtKB',
        'blastprotocollsid' : 'Protocol.blastx.AFT Standard Blastx informative hits protocol',
        'datasourcetype' : 'blastx_agresearch_csv_moderated',
        'physicalsourceuri' : '/data/home/seqstore/agbrdf/fungal/chip_uniprot_blastx.bls.tophit3.meaning2.csv',
        'studytype' : 'Blast',
        'studydescription' : 'Blastx of AFT chip-related sequences against UniProtKB, annotated with informative hits',
        'fieldNamesRow' : 1
    }



    myform = databaseSearchImportForm(importParms)
    myform.processData()    


    return

    importParms = {
        'queryPrefix' : 'CS34',
        'hitPrefix' : 'NCBI',
        'hitAccessionRegexp' : ('^\w*\|(\w+)\.?\d*\|','^pir\|\|(\w+)\.?\d*' , '^prf\|\|(\w+)\.?\d*'),
        'queryAccessionRegexp' : None,
        'checkExistingHits' : False,
        'createMissingQueries' : False,
        'createMissingHits' : True,
        'querySequenceType' : 'DNA SEQUENCE',
        'hitSequenceType' : 'PROTEIN SEQUENCE',
        'databaselsid' : 'NCBI.Non-redundant Protein (NR)',
        'databasetype' : 'Protein sequence database',
        'blastprotocollsid' : 'Protocol.blastx.Standard Bovine Protein blast',
        'datasourcetype' : 'blastx_agresearch_csv',
        'physicalsourceuri' : '/home/seqstore/agbrdf/cs34.seq_nr.csv',
        'studytype' : 'Blast',
        'studydescription' : 'Blastx of Bovine CS34 EST contigs against NCBI nr'
    }

    myform = databaseSearchImportForm(importParms)
    myform.processData()



    return




    importParms = {
        'queryPrefix' : 'CS34',
        'hitPrefix' : 'NCBI',
        'hitAccessionRegexp' :  ('^\w*\|(\w+)\.?\d*\|','^pir\|\|(\w+)\.?\d*' , '^prf\|\|(\w+)\.?\d*'),
        'queryAccessionRegexp' : None,
        'checkExistingHits' : False,
        'createMissingQueries' : False,
        'createMissingHits' : True,
        'querySequenceType' : 'mRNA SEQUENCE',
        'hitSequenceType' : 'DNA SEQUENCE',
        'databaselsid' : 'NCBI.Genbank',
        'blastprotocollsid' : 'Protocol.blastn.Standard Blastn protocol',
        'datasourcetype' : 'blastn_agresearch_csv',
        'physicalsourceuri' : 'C:/working/anar/chip_uniprot_blastx.bls.am.csv',
        'studytype' : 'Blast',
        'studydescription' : 'Blastn of CS34 contigs against Genbank'
    }


    myform = databaseSearchImportForm(importParms)
    myform.processData()

    return

    #importParms = {
    #    'queryPrefix' : 'AFT',
    #    'hitPrefix' : 'NCBI',
    #    'hitAccessionRegexp' : ('^gi\|\w+\|\w+\|(\w+)\.?\d*',),
    #    'queryAccessionRegexp' : None,
    #    'checkExistingHits' : False,
    #    'createMissingQueries' : False,
    #    'createMissingHits' : True,
    #    'querySequenceType' : 'genomic DNA',
    #    'hitSequenceType' : 'PROTEIN SEQUENCE',
    #    'databaselsid' : 'NCBI.Non-redundant Protein (NR)',
    #    'blastprotocollsid' : 'Protocol.blastx.Orthoblast blastx (genomic sequence against protein)',
    #    'datasourcetype' : 'blastx_agresearch_csv_nokeywords',
    #    'physicalsourceuri' : '/data/home/seqstore/agbrdf/fungalrefs_new.fa_nr.out.csv',
    #    'studytype' : 'Blast',
    #    'studydescription' : 'Orthoblast blastx of AFT genomic fungal sequences against NCBI nr'
    #}

    #importParms = {
    #    'queryPrefix' : 'Hort',
    #    'hitPrefix' : 'NCBI',
    #    'hitAccessionRegexp' : ('^\w*\|(\w+)\.?\d*\|','^pir\|\|(\w+)\.?\d*' , '^prf\|\|(\w+)\.?\d*'),
    #    'queryAccessionRegexp' : None,
    #    'checkExistingHits' : False,
    #    'createMissingQueries' : False,
    #    'createMissingHits' : True,
    #    'querySequenceType' : 'mRNA SEQUENCE',
    #    'hitSequenceType' : 'PROTEIN SEQUENCE',
    #    'databaselsid' : 'NCBI.Non-redundant Protein (NR)',
    #    'blastprotocollsid' : 'Protocol.blastx.AFT Standard Blastx protocol',
    #    'datasourcetype' : 'blastx_agresearch_csv',
    #    'physicalsourceuri' : '/home/seqstore/agbrdf/fungal/hort_fungalESTs_blastx_nr_output.csv',
    #    'studytype' : 'Blast',
    #    'studydescription' : 'Blastx of HORT fungal sequences against NCBI nr'
    #}







def AgResearchArrayMain():
    """ method for importing an extract that has been done from the Oracle database using the following code : 

select
   /*+ RULE */
   nvl(agplsqlutils.getSequenceName(altid_num),mps.contentid)  "EST",
   mps.spotid "SpotId",
   nvl(ags.genbankaccession, 'AGNZ'||to_char(mpsp.publishedid)) "publishedid",
   mps.dimension1 "rw",
   mps.dimension2 "cl",
   mps.dimension3 "metarw",
   mps.dimension4 "metacl",
   agplsqlutils.deVersion(agplsqlutils.dePipe(agplsqlutils.getTopDBSearchHit(altid_num,'NCBInr','hitid'))) "nr",
   agplsqlutils.getTopDBSearchHit(altid_num,'NCBInr','description') nrdescription ,
   agplsqlutils.getTopDBSearchHit(altid_num,'NCBInr','evalue') nrevalue ,
   g.symbol nr_gene,
   g.synonyms,
   g.geneid nr_geneid,
   pubplsqlutils.getGoString(pubplsqlutils.getGeneIdFromAccession(agplsqlutils.deVersion(agplsqlutils.dePipe(agplsqlutils.getTopDBSearchHit(altid_num,'NCBInr','hitid'))),10)) goAnnotation
from
   ops$seqstore.agsequence ags, microarray_productspotpub mpsp , pubstore.geneinfo g, microarray_productspot mps
where
   mps.arrayproductid = 39 and
   mpsp.spotid = mps.spotid and
   g.geneid(+) = pubplsqlutils.getGeneIdFromAccession(agplsqlutils.dePipe(agplsqlutils.getTopDBSearchHit(altid_num,'NCBInr','hitid')),10) and
   ags.sequenceid(+) = mps.altid_num

- note , previously was as follows (before 2/2008)

select
   /*+ RULE */
   nvl(agplsqlutils.getSequenceName(altid_num),mps.contentid)  "EST",
   mps.spotid "SpotId",
   mps.dimension1 "rw",
   mps.dimension2 "cl",
   mps.dimension3 "metarw",
   mps.dimension4 "metacl",
   agplsqlutils.deVersion(agplsqlutils.dePipe(agplsqlutils.getTopDBSearchHit(altid_num,'NCBInr','hitid'))) "nr",
   agplsqlutils.getTopDBSearchHit(altid_num,'NCBInr','description') nrdescription ,
   agplsqlutils.getTopDBSearchHit(altid_num,'NCBInr','evalue') nrevalue ,
   g.symbol nr_gene,
   g.synonyms,
   g.geneid nr_geneid,
   pubplsqlutils.getGoString(pubplsqlutils.getGeneIdFromAccession(agplsqlutils.deVersion(agplsqlutils.dePipe(agplsqlutils.getTopDBSearchHit(altid_num,'NCBInr','hitid'))),10)) goAnnotation
from
   pubstore.geneinfo g, microarray_productspot mps
where
   mps.arrayproductid = 44 and
   g.geneid(+) = pubplsqlutils.getGeneIdFromAccession(agplsqlutils.dePipe(agplsqlutils.getTopDBSearchHit(altid_num,'NCBInr','hitid')),10)
"""
    importParms = {
        'resourcetype' : "microarray",
        'xreflsid' : "Print70",
        'resourcedescription' :  """
Print 70 Ovine 11K 
        """,
        'datasourcetype' : "AgResearchArrayExtract1",
        'physicalsourceuri' : "/data/agbio/spool/print70extract.csv"
    }
    myform = microarrayAgResearchForm(importParms)
    myform.processData()

    return

    importParms = {
        'resourcetype' : "microarray",
        'xreflsid' : "Print67",
        'resourcedescription' :  """
Print 67
        """,
        'datasourcetype' : "AgResearchArrayExtract1",
        'physicalsourceuri' : "/data/home/seqstore/agbrdf/print67.csv"
    }
    myform = microarrayAgResearchForm(importParms)
    myform.processData()

    return

    importParms = {
        'resourcetype' : "microarray",
        'xreflsid' : "Print38",
        'resourcedescription' :  """
Print 38, TW 25K mixed
        """,
        'datasourcetype' : "AgResearchArrayExtract1",
        'physicalsourceuri' : "/data/home/seqstore/agbrdf/nauman/print38import.csv"
    }
    myform = microarrayAgResearchForm(importParms)
    myform.processData()

    return


    importParms = {
        'resourcetype' : "microarray",
        'xreflsid' : "Print48",
        'resourcedescription' :  """
Print48 , 22K mixed
32 pins , 26 rows and 27 columns per block
interspot distance 150um
        """,
        'datasourcetype' : "AgResearchArrayExtract1",
        'physicalsourceuri' : "/data/home/seqstore/agbrdf/nauman/print48import.csv"
    }
    myform = microarrayAgResearchForm(importParms)
    myform.processData()

    return


    importParms = {
        'resourcetype' : "microarray",
        'xreflsid' : "Print69",
        'resourcedescription' :  """
Print 69 23K array
32 pins  12x61 spots per pin 23424 spots
between spots centre 100um spot diameter 100um
        """,
        'datasourcetype' : "AgResearchArrayExtract1",
        'physicalsourceuri' : "/data/home/seqstore/agbrdf/nauman/print69import.csv"
    }
    myform = microarrayAgResearchForm(importParms)
    myform.processData()

    return



    importParms = {
        'resourcetype' : "microarray",
        'xreflsid' : "Print79",
        'resourcedescription' :  """
32 pins, 28 x and 27 y
interspot distance of 150 uM
        """,
        'datasourcetype' : "AgResearchArrayExtract1",
        'physicalsourceuri' : "/data/home/seqstore/agbrdf/nauman/print79import.csv"
    }
    myform = microarrayAgResearchForm(importParms)
    myform.processData()

    return



    importParms = {
        'resourcetype' : "microarray",
        'xreflsid' : "Print20",
        'resourcedescription' :  """
Print20, AM 12K mixed
        """,
        'datasourcetype' : "AgResearchArrayExtract1",
        'physicalsourceuri' : "/data/home/seqstore/agbrdf/nauman/print20import.csv"
    }
    myform = microarrayAgResearchForm(importParms)
    myform.processData()

    return


    importParms = {
        'resourcetype' : "microarray",
        'xreflsid' : "Print114",
        'resourcedescription' :  """
Print 114 polylysine 50
32 pins, 8x4 spots per pin
slide rows,cols=5,10 X rows=24,Y cols=27
spots=20736, 384 well plates=54
Block Column Spacing 150 Row spacing 150
        """,
        'datasourcetype' : "AgResearchArrayExtract1",
        'physicalsourceuri' : "/data/home/seqstore/agbrdf/sue/print114extract.csv"
    }
    myform = microarrayAgResearchForm(importParms)
    myform.processData()

    return

    importParms = {
        'resourcetype' : "microarray",
        'xreflsid' : "print136 ov 21k.txt", 
        'resourcedescription' :  """
Date	13/11/2006	   
Print	136 Ovine 20K	   
Slides	49 aminosilane slides	   
Slides 	rows 7	   
 Slide columns 7	   
Blocks	32	   
rows	8	   
columns	4	   
Block Spacing	4550	   
		   
384 well plates	56	   
# spots	21504	   
# rows X	24	   
# columns Y	28	   
spacing row	155	   
spacing column	155	   
Spot diam	100	 
        """,
        'datasourcetype' : "AgResearchArrayExtract1",
        'physicalsourceuri' : "/data/home/seqstore/agbrdf/lisa/print136.csv"
    }

    myform = microarrayAgResearchForm(importParms)
    myform.processData()    

def GALMain():

    importParms = {
        'resourcetype' : "microarray",
        'xreflsid' : "GPL7083-34008.txt",
        'resourcedescription' :  "Agilent-020908 Oryctolagus cuniculus (Rabbit) Oligo Microarray",
        'datasourcetype' : "GALFile",
        'physicalsourceuri' : "/data/tmp/GPL7083-34008.txt",
    }

    myform = microarrayGALForm(importParms)
    myform.processData()

    return


    importParms = {
        'resourcetype' : "microarray",
        'xreflsid' : "print113bov20k.txt",
        'resourcedescription' :  "print113bov20k.txt",
        'datasourcetype' : "GALFile_noheader",
        'physicalsourceuri' : "/data/home/seqstore/agbrdf/print113bov20k.txt"
    }

    myform = microarrayGALForm(importParms)
    myform.processData()

    return


    importParms = {
        'resourcetype' : "microarray",
        'xreflsid' : "print110 Bov20k.txt",
        'resourcedescription' :  "print110 Bov20k.txt",
        'datasourcetype' : "GALFile_noheader",
        'physicalsourceuri' : "/data/home/seqstore/agbrdf/print110 Bov20k.txt"
    }

    myform = microarrayGALForm(importParms)
    myform.processData()

    return


    importParms = {
        'resourcetype' : "microarray",
        'xreflsid' : "print 119 MRUM.txt",
        'resourcedescription' :  "print 119 MRUM.txt",
        'datasourcetype' : "GALFile_noheader",
        'physicalsourceuri' : "/data/home/seqstore/agbrdf/attwood/print 119 MRUM.txt"
    }

    myform = microarrayGALForm(importParms)
    myform.processData()

    return


    #importParms = {
    #    'resourcetype' : "microarray",
    #    'xreflsid' : "Agilent.011978_D_20030711.gal", 
    #    'resourcedescription' :  "Agilent Mouse microarray 011978_D_20030711.gal",
    #    'datasourcetype' : "GALFile",
    #    'physicalsourceuri' : "M:\\projects\\nutrigenomics\\brdf\\data\\011978_D_20030711.gal"
    #}
    #importParms = {
    #    'resourcetype' : "microarray",
    #    'xreflsid' : "Print 120 CPROT 17K.txt", 
    #    'resourcedescription' :  "Print 120 CPROT 17K.txt",
    #    'datasourcetype' : "GALFile_noheader",
    #    'physicalsourceuri' : "/data/home/seqstore/agbrdf/zaneta/Print 120 CPROT 17K.txt"
    #}    
    #importParms = {
    #    'resourcetype' : "microarray",
    #    'xreflsid' : "012391_D_20050902.gal", 
    #    'resourcedescription' :  "Agilent-012391 Whole Human Genome Oligo Microarray",
    #    'datasourcetype' : "GALFile",
    #    'physicalsourceuri' : "/data/home/seqstore/agbrdf/zaneta/rachel/012391_D_20050902.gal"
    #}        
    #importParms = {
    #    'resourcetype' : "microarray",
    #    'xreflsid' : "014850_D_20070207.gal",
    #    'resourcedescription' :  "Agilent-014850:Whole Human Genome Microarray 4x44K",
    #    'datasourcetype' : "GALFile",
    #    'physicalsourceuri' : "/data/home/seqstore/agbrdf/samnoel/014850_D_20070207.gal"
    #}
    importParms = {
        'resourcetype' : "microarray",
        'xreflsid' : "print 139 ov21K.txt",
        'resourcedescription' :  """
slide configuration	 		   
	3/07/2007	   
Date	139 Ovine 21K	   
Print			   
Slides 	54 aminosilane slides	   
Slide rows	6	   
Slide columns	9	   
Blocks	32	   
rows	8	   
columns	4	   
Block spacing	4550	   
	4550	   
			   
384 well plates	56	   
# spots	21504	   
# rows X	24	   
# columns Y	28	   
spacing row	155	   
spacing column	155	   
Spot diam	100	 
        """,
        'datasourcetype' : "GALFile_noheader",
        'physicalsourceuri' : "/data/home/seqstore/agbrdf/anne/print 139 ov21K.txt"
    }

    myform = microarrayGALForm(importParms)
    myform.processData()    


def AffyImportMain(subjectdata,sampledata,arraydata,filedata,experimentdata):
    """ This is a method used to call the Affy Import form from a script example call :
        AffyImportMain(subjectdata={'xreflsid' : 'SG215.Ovis aries','subjectname' : 'SG215.Ovis aries','subjectdescription' : 'Dummy sheep subject record, where id of sheep unknown','subjectspeciesname' : 'Ovis aries'}\,
        sampledata={"xreflsid" : "sg215.unknown", "samplename" : "sg215.unknown","sampletissue" : "unknown","sampletreatment" : "unknown","sampletype" : "mRNA extract for microarray experiment"},\
        arraydata={'xreflsid' : 'Affymetrix.Bovine Genome Array'},\
        filedata={'filename' : '4_controls_AFFS427' , 'physicalsourceuri' : 'C:\working\sheepgenomics\sg215\4_controls_AFFS427' , 'datasourcetype' : 'CSV from Affy CEL File'},\
        experimentdata={'studytype' : 'treated vs untreated microarray', 'studydescription' : 'unknown'})
        """
    
    connection=databaseModule.getConnection()

    
    # set up the biosubject. Note that actually probably need > 1 subject, but at the moment
    # we do not know what the subject was so we use the unknown sheep
    subject = bioSubjectOb()
    try :
        subject.initFromDatabase(subjectdata['xreflsid'],connection)
    except brdfException:
        if subject.obState['ERROR'] == 1:
            subject.initNew(connection)
            subject.databaseFields.update(subjectdata)
            subject.insertDatabase(connection)
        else:
            raise brdfException, subject.obState['MESSAGE']

    # set up the samples
    sample = bioSampleOb()
    try :
        sample.initFromDatabase(sampledata['xreflsid'],connection)
    except brdfException:
        if sample.obState['ERROR'] == 1:
            sample.initNew(connection)
            sample.databaseFields.update(sampledata)
            sample.insertDatabase(connection)
        else:
            raise brdfException, sample.obState['MESSAGE']


    # set up the sample list
    samplelist = bioSampleList()
    samplelistlsid = "%s.list"%sampledata["xreflsid"]
    try :
        samplelist.initFromDatabase(samplelistlsid,connection)
    except brdfException:
        if samplelist.obState['ERROR'] == 1:
            samplelist.initNew(connection)
            samplelist.databaseFields.update( {
                'xreflsid' : samplelistlsid,
                'listname' : samplelistlsid
            })
            samplelist.insertDatabase(connection)
            samplelist.addSample(connection,sample)
        else:
            raise brdfException, samplelist.obState['MESSAGE']            
            
    importParms = {
        'samplelistlsid' : samplelistlsid,
        'microarraylsid' : arraydata['xreflsid'],
        'geneexpressionstudylsid' : "GeneExpressionStudy.microarray.%s"%filedata['filename'],
        'datasourcetype' : filedata['datasourcetype'],
        'physicalsourceuri' : filedata['physicalsourceuri'],
        'studytype' : experimentdata['studytype'],
        'studydescription' : experimentdata['studydescription']
    }    

    connection.commit()
    myform = microarrayAffyForm(importParms)
    myform.processData()



def main():

    BlastImportMain()
    return

    GALMain()
    return

    BlastImportMain()
    return


    AgResearchArrayMain()
    return

    BlastImportMain()
    return


    #AgResearchExportMain({ "sampletissue" : "CY5.intestine","samplename" : "1003/01","sampletreatment" : "parasite resistant","samplesubject" : {"name" : "parasite resistant", "sex" : "F" }},{"sampletissue" : "CY3.intestine","samplename" : "1046/01","sampletreatment" : "parasite sensitive","samplesubject" : {"name" : "parasite sensitive", "sex" : "F" }},"605.csv","""Ovita parasite project.  Resistant versus susceptible animals""","Print67",605)
    #return
    AgResearchExportMain({ "sampletissue" : "CY5.Intestine","samplename" : "1001/01","sampletreatment" : "parasite susceptible","samplesubject" : {"name" : "parasite susceptible", "sex" : "F" }},{"sampletissue" : "CY3.Intestine","samplename" : "1004/01","sampletreatment" : "parasite resistant","samplesubject" : {"name" : "parasite resistant", "sex" : "F" }},"613.csv","""Ovita parasite resistance project.  Resistant versus susceptible animals.""","Print67",613)
    AgResearchExportMain({ "sampletissue" : "CY5.Intestine","samplename" : "1004/01","sampletreatment" : "parasite resistant","samplesubject" : {"name" : "parasite resistant", "sex" : "F" }},{"sampletissue" : "CY3.Intestine","samplename" : "1053/01","sampletreatment" : "parasite susceptible","samplesubject" : {"name" : "parasite susceptible", "sex" : "F" }},"615.csv","""Ovita parasite resistance project.  Resistant versus susceptible animals.""","Print67",615)
    AgResearchExportMain({ "sampletissue" : "CY5.Intestine","samplename" : "1035/01","sampletreatment" : "parasite resistant","samplesubject" : {"name" : "parasite resistant", "sex" : "F" }},{"sampletissue" : "CY3.Intestine","samplename" : "1031/01","sampletreatment" : "parasite susceptible","samplesubject" : {"name" : "parasite susceptible", "sex" : "F" }},"623.csv","""Ovita parasite resistance project.  Resistant versus susceptible animals.""","Print67",623)
    AgResearchExportMain({ "sampletissue" : "CY5.Intestine","samplename" : "1046/01","sampletreatment" : "parasite susceptible","samplesubject" : {"name" : "parasite susceptible", "sex" : "F" }},{"sampletissue" : "CY3.Intestine","samplename" : "1035/01","sampletreatment" : "parasite resistant","samplesubject" : {"name" : "parasite resistant", "sex" : "F" }},"624.csv","""Ovita parasite resistance project.  Resistant versus susceptible animals.""","Print67",624)
    AgResearchExportMain({ "sampletissue" : "CY5.Intestine","samplename" : "1044/01","sampletreatment" : "parasite resistant","samplesubject" : {"name" : "parasite resistant", "sex" : "F" }},{"sampletissue" : "CY3.Intestine","samplename" : "1001/01","sampletreatment" : "parasite susceptible","samplesubject" : {"name" : "parasite susceptible", "sex" : "F" }},"625.csv","""Ovita parasite resistance project.  Resistant versus susceptible animals.""","Print67",625)
    AgResearchExportMain({ "sampletissue" : "CY5.Intestine","samplename" : "1044/01","sampletreatment" : "parasite resistant","samplesubject" : {"name" : "parasite resistant", "sex" : "F" }},{"sampletissue" : "CY3.Intestine","samplename" : "1031/01","sampletreatment" : "parasite susceptible","samplesubject" : {"name" : "parasite susceptible", "sex" : "F" }},"626.csv","""Ovita parasite resistance project.  Resistant versus susceptible animals.""","Print67",626)
    AgResearchExportMain({ "sampletissue" : "CY5.Intestine","samplename" : "1053/01","sampletreatment" : "parasite susceptible","samplesubject" : {"name" : "parasite susceptible", "sex" : "F" }},{"sampletissue" : "CY3.Intestine","samplename" : "1044/01","sampletreatment" : "parasite resistant","samplesubject" : {"name" : "parasite resistant", "sex" : "F" }},"627.csv","""Ovita parasite resistance project.  Resistant versus susceptible animals.""","Print67",627)
    AgResearchExportMain({ "sampletissue" : "CY5.Intestine","samplename" : "1001/01","sampletreatment" : "parasite susceptible","samplesubject" : {"name" : "parasite susceptible", "sex" : "F" }},{"sampletissue" : "CY3.Intestine","samplename" : "1003/01","sampletreatment" : "parasite resistant","samplesubject" : {"name" : "parasite resistant", "sex" : "F" }},"628.csv","""Ovita parasite resistance project.  Resistant versus susceptible animals""","Print67",628)
    AgResearchExportMain({ "sampletissue" : "CY5.Intestine","samplename" : "1031/01","sampletreatment" : "parasite susceptible","samplesubject" : {"name" : "parasite susceptible", "sex" : "F" }},{"sampletissue" : "CY3.Intestine","samplename" : "1003/01","sampletreatment" : "parasite resistant","samplesubject" : {"name" : "parasite resistant", "sex" : "F" }},"629.csv","""Ovita parasite resistance project.  Resistant versus susceptibe animals.""","Print67",629)
    AgResearchExportMain({ "sampletissue" : "CY5.Intestine","samplename" : "1003/01","sampletreatment" : "parasite resistant","samplesubject" : {"name" : "parasite resistant", "sex" : "F" }},{"sampletissue" : "CY3.Intestine","samplename" : "1053/01","sampletreatment" : "parasite susceptible","samplesubject" : {"name" : "parasite susceptible", "sex" : "F" }},"630.csv","""Ovita parasite resistance project.  Resistant versus susceptible animals.""","Print67",630)
    AgResearchExportMain({ "sampletissue" : "CY5.Intestine","samplename" : "1031/01","sampletreatment" : "parasite susceptible","samplesubject" : {"name" : "parasite susceptible", "sex" : "F" }},{"sampletissue" : "CY3.Intestine","samplename" : "1004/01","sampletreatment" : "parasite resistant","samplesubject" : {"name" : "parasite resistant", "sex" : "F" }},"631.csv","""Ovita parasite resistance project.  Resistant versus susceptible animals.""","Print67",631)
    AgResearchExportMain({ "sampletissue" : "CY5.Intestine","samplename" : "1004/01","sampletreatment" : "parasite resistant","samplesubject" : {"name" : "parasite resistant", "sex" : "F" }},{"sampletissue" : "CY3.Intestine","samplename" : "1046/01","sampletreatment" : "parasite susceptible","samplesubject" : {"name" : "parasite susceptible", "sex" : "F" }},"632.csv","""Ovita parasite resistance project.  Resistant versus susceptible animals.""","Print67",632)
    AgResearchExportMain({ "sampletissue" : "CY5.Intestine","samplename" : "1035/01","sampletreatment" : "parasite resistant","samplesubject" : {"name" : "parasite resistant", "sex" : "F" }},{"sampletissue" : "CY3.Intestine","samplename" : "1001/01","sampletreatment" : "parasite susceptible","samplesubject" : {"name" : "parasite susceptible", "sex" : "F" }},"633.csv","""Ovita parasite resistance project.  Resistant versus susceptible animals.""","Print67",633)
    AgResearchExportMain({ "sampletissue" : "CY5.Intestine","samplename" : "1053/01","sampletreatment" : "parasite susceptible","samplesubject" : {"name" : "parasite susceptible", "sex" : "F" }},{"sampletissue" : "CY3.Intestine","samplename" : "1035/01","sampletreatment" : "parasite resistant","samplesubject" : {"name" : "parasite resistant", "sex" : "F" }},"634.csv","""Ovita parasite resistance project.  Resistant versus susceptible animals.""","Print67",634)
    AgResearchExportMain({ "sampletissue" : "CY5.Intestine","samplename" : "1046/01","sampletreatment" : "parasite susceptible","samplesubject" : {"name" : "parasite susceptible", "sex" : "F" }},{"sampletissue" : "CY3.Intestine","samplename" : "1044/01","sampletreatment" : "parasite resistant","samplesubject" : {"name" : "parasite resistant", "sex" : "F" }},"635.csv","""Ovita parasite resistance project.  Resistant versus susceptible animals.""","Print67",635)
    AgResearchExportMain({ "sampletissue" : "CY5.LIver","samplename" : "P-2186","sampletreatment" : "Susceptible","samplesubject" : {"name" : "Susceptible", "sex" : "F" }},{"sampletissue" : "CY3.Liver","samplename" : "O-2216","sampletreatment" : "Resistant","samplesubject" : {"name" : "Resistant", "sex" : "F" }},"644.csv","""Undosed ewes (not)treated with sporidesmin""","Print67",644)
    AgResearchExportMain({ "sampletissue" : "CY5.Liver","samplename" : "O-2195","sampletreatment" : "Resistant","samplesubject" : {"name" : "Resistant", "sex" : "F" }},{"sampletissue" : "CY3.Liver","samplename" : "P-2186","sampletreatment" : "Susceptible","samplesubject" : {"name" : "Susceptible", "sex" : "F" }},"645.csv","""Ewes undosed (treated with vehicle solution with no sporidesmin)""","Print67",645)
    AgResearchExportMain({ "sampletissue" : "CY5.Liver","samplename" : "P-2384","sampletreatment" : "Susceptible","samplesubject" : {"name" : "Susceptible", "sex" : "F" }},{"sampletissue" : "CY3.Liver","samplename" : "O-2216","sampletreatment" : "Resistant","samplesubject" : {"name" : "Resistant", "sex" : "F" }},"646.csv","""Ewes undosed - treated with vehicle solution with no sporidesmin""","Print67",646)
    AgResearchExportMain({ "sampletissue" : "CY5.Liver","samplename" : "P-2018","sampletreatment" : "Susceptible","samplesubject" : {"name" : "Susceptible", "sex" : "F" }},{"sampletissue" : "CY3.Liver","samplename" : "O-2195","sampletreatment" : "Resistant","samplesubject" : {"name" : "Resistant", "sex" : "F" }},"647.csv","""Ewes Undosed (treated with vehicle solution with no sporidesmin)""","Print67",647)
    AgResearchExportMain({ "sampletissue" : "CY5.Liver","samplename" : "O-2201","sampletreatment" : "Resistant","samplesubject" : {"name" : "Resistant", "sex" : "F" }},{"sampletissue" : "CY3.Liver","samplename" : "P-2018","sampletreatment" : "Susceptible","samplesubject" : {"name" : "Susceptible", "sex" : "F" }},"648.csv","""(Please enter a description here)""","Print67",648)
    AgResearchExportMain({ "sampletissue" : "CY5.Liver","samplename" : "P-2097","sampletreatment" : "Susceptible","samplesubject" : {"name" : "Susceptible", "sex" : "F" }},{"sampletissue" : "CY3.Liver","samplename" : "O-2201","sampletreatment" : "Resistant","samplesubject" : {"name" : "Resistant", "sex" : "F" }},"649.csv","""Ewes Undosed (treated with vehicle solution with no sporidesmin)""","Print67",649)
    AgResearchExportMain({ "sampletissue" : "CY5.Liver","samplename" : "P-2018","sampletreatment" : "Susceptible","samplesubject" : {"name" : "Susceptible", "sex" : "F" }},{"sampletissue" : "CY3.Liver","samplename" : "O-2286","sampletreatment" : "Resistant","samplesubject" : {"name" : "Resistant", "sex" : "F" }},"650.csv","""Ewes Undosed (treated with vehicle solution with no sporidesmin)""","Print67",650)
    AgResearchExportMain({ "sampletissue" : "CY5.Liver","samplename" : "P-2097","sampletreatment" : "Susceptible","samplesubject" : {"name" : "Susceptible", "sex" : "F" }},{"sampletissue" : "CY3.Liver","samplename" : "O-2195","sampletreatment" : "Resistant","samplesubject" : {"name" : "Resistant", "sex" : "F" }},"651.csv","""Ewes Undosed (treated with vehicle solution with no sporidesmin)""","Print67",651)
    AgResearchExportMain({ "sampletissue" : "CY5.Liver","samplename" : "O-2216","sampletreatment" : "Resistant","samplesubject" : {"name" : "Resistant", "sex" : "F" }},{"sampletissue" : "CY3.Liver","samplename" : "P-2018","sampletreatment" : "Susceptible","samplesubject" : {"name" : "Susceptible", "sex" : "F" }},"652.csv","""Ewes Undosed (treated with vehicle solution with no sporidesmin)""","Print67",652)
    AgResearchExportMain({ "sampletissue" : "CY5.Liver","samplename" : "O-2216","sampletreatment" : "Resistant","samplesubject" : {"name" : "Resistant", "sex" : "F" }},{"sampletissue" : "CY3.Liver","samplename" : "P-2018","sampletreatment" : "Susceptible","samplesubject" : {"name" : "Susceptible", "sex" : "F" }},"653.csv","""Ewes Undosed (treated with vehicle solution with no sporidesmin)""","Print67",653)
    AgResearchExportMain({ "sampletissue" : "CY5.Liver","samplename" : "O-2286","sampletreatment" : "Resistant","samplesubject" : {"name" : "Resistant", "sex" : "F" }},{"sampletissue" : "CY3.Liver","samplename" : "P-2097","sampletreatment" : "Susceptible","samplesubject" : {"name" : "Susceptible", "sex" : "F" }},"654.csv","""Ewes Undosed (treated with vehicle solution with no sporidesmin)""","Print67",654)
    AgResearchExportMain({ "sampletissue" : "CY5.Liver","samplename" : "O-2286","sampletreatment" : "Resistant","samplesubject" : {"name" : "Resistant", "sex" : "F" }},{"sampletissue" : "CY3.Liver","samplename" : "P-2384","sampletreatment" : "Susceptible","samplesubject" : {"name" : "Susceptible", "sex" : "F" }},"655.csv","""Ewes Undosed (treated with vehicle solution with no sporidesmin)""","Print67",655)
    AgResearchExportMain({ "sampletissue" : "CY5.Liver","samplename" : "O-2201","sampletreatment" : "Resistant","samplesubject" : {"name" : "Resistant", "sex" : "F" }},{"sampletissue" : "CY3.Liver","samplename" : "P-2186","sampletreatment" : "Susceptible","samplesubject" : {"name" : "Susceptible", "sex" : "F" }},"656.csv","""Ewes Undosed (treated with vehicle solution with no sporidesmin)""","Print67",656)
    AgResearchExportMain({ "sampletissue" : "CY5.LIver","samplename" : "P-2384","sampletreatment" : "Susceptible","samplesubject" : {"name" : "Susceptible", "sex" : "F" }},{"sampletissue" : "CY3.Liver","samplename" : "O-2201","sampletreatment" : "Resistant","samplesubject" : {"name" : "Resistant", "sex" : "F" }},"657.csv","""Ewes Undosed (treated with vehicle solution with no sporidesmin)""","Print67",657)
    AgResearchExportMain({ "sampletissue" : "CY5.Liver","samplename" : "O-2195","sampletreatment" : "Resistant","samplesubject" : {"name" : "Resistant", "sex" : "F" }},{"sampletissue" : "CY3.Liver","samplename" : "P-2384","sampletreatment" : "Susceptible","samplesubject" : {"name" : "Susceptible", "sex" : "F" }},"658.csv","""Ewes Undosed (treated with vehicle solution with no sporidesmin)""","Print67",658)
    AgResearchExportMain({ "sampletissue" : "CY5.Liver","samplename" : "O-2216","sampletreatment" : "Resistant","samplesubject" : {"name" : "Resistant", "sex" : "F" }},{"sampletissue" : "CY3.Liver","samplename" : "P-2097","sampletreatment" : "Susceptible","samplesubject" : {"name" : "Susceptible", "sex" : "F" }},"713.csv","""high scan of Ewes Undosed (given vehicle soln with no sporidesmin)""","Print67",713)
    AgResearchExportMain({ "sampletissue" : "CY5.Liver","samplename" : "P-2186","sampletreatment" : "Susceptible","samplesubject" : {"name" : "Susceptible", "sex" : "F" }},{"sampletissue" : "CY3.Liver","samplename" : "O-2216","sampletreatment" : "Resistant","samplesubject" : {"name" : "Resistant", "sex" : "F" }},"714.csv","""high scan of Ewes Undosed (given vehicle soln with no sporidesmin)""","Print67",714)
    AgResearchExportMain({ "sampletissue" : "CY5.Liver","samplename" : "P-2384","sampletreatment" : "Susceptible","samplesubject" : {"name" : "Susceptible", "sex" : "F" }},{"sampletissue" : "CY3.Liver","samplename" : "O-2216","sampletreatment" : "Resistant","samplesubject" : {"name" : "Resistant", "sex" : "F" }},"715.csv","""high scan of Ewes Undosed (given vehicle soln with no sporidesmin)""","Print67",715)
    AgResearchExportMain({ "sampletissue" : "CY5.Liver","samplename" : "O-2195","sampletreatment" : "Resistant","samplesubject" : {"name" : "Resistant", "sex" : "F" }},{"sampletissue" : "CY3.Liver","samplename" : "P-2186","sampletreatment" : "Susceptible","samplesubject" : {"name" : "Susceptible", "sex" : "F" }},"716.csv","""high scan of Ewes Undosed (given vehicle soln with no sporidesmin)""","Print67",716)
    AgResearchExportMain({ "sampletissue" : "CY5.Liver","samplename" : "O-2216","sampletreatment" : "Resistant","samplesubject" : {"name" : "Resistant", "sex" : "F" }},{"sampletissue" : "CY3.LIver","samplename" : "P-2018","sampletreatment" : "Susceptible","samplesubject" : {"name" : "Susceptible", "sex" : "F" }},"717.csv","""high scan of Ewes Undosed (given vehicle soln with no sporidesmin)""","Print67",717)
    AgResearchExportMain({ "sampletissue" : "CY5.Liver","samplename" : "P-2186","sampletreatment" : "Susceptible","samplesubject" : {"name" : "Susceptible", "sex" : "F" }},{"sampletissue" : "CY3.Liver","samplename" : "O-2286","sampletreatment" : "Resistant","samplesubject" : {"name" : "Resistant", "sex" : "F" }},"718.csv","""high scan of Ewes Undosed (given vehicle soln with no sporidesmin)""","Print67",718)
    AgResearchExportMain({ "sampletissue" : "CY5.Liver","samplename" : "P-2097","sampletreatment" : "Susceptible","samplesubject" : {"name" : "Susceptible", "sex" : "F" }},{"sampletissue" : "CY3.Liver","samplename" : "O-2201","sampletreatment" : "Resistant","samplesubject" : {"name" : "Resistant", "sex" : "F" }},"719.csv","""high scan of Ewes Undosed (given vehicle soln with no sporidesmin)""","Print67",719)
    AgResearchExportMain({ "sampletissue" : "CY5.Liver","samplename" : "O-2201","sampletreatment" : "Resistant","samplesubject" : {"name" : "Resistant", "sex" : "F" }},{"sampletissue" : "CY3.Liver","samplename" : "P-2186","sampletreatment" : "Susceptible","samplesubject" : {"name" : "Susceptible", "sex" : "F" }},"720.csv","""high scan of Ewes Undosed (given vehicle soln with no sporidesmin)""","Print67",720)
    AgResearchExportMain({ "sampletissue" : "CY5.Liver","samplename" : "P-2018","sampletreatment" : "Susceptible","samplesubject" : {"name" : "Susceptible", "sex" : "F" }},{"sampletissue" : "CY3.Liver","samplename" : "O-2286","sampletreatment" : "Resistant","samplesubject" : {"name" : "Resistant", "sex" : "F" }},"721.csv","""high scan of Ewes Undosed (given vehicle soln with no sporidesmin)""","Print67",721)
    AgResearchExportMain({ "sampletissue" : "CY5.Liver","samplename" : "O-2201","sampletreatment" : "Resistant","samplesubject" : {"name" : "Resistant", "sex" : "F" }},{"sampletissue" : "CY3.Liver","samplename" : "P-2018","sampletreatment" : "Susceptible","samplesubject" : {"name" : "Susceptible", "sex" : "F" }},"722.csv","""high scan of Ewes Undosed (given vehicle soln with no sporidesmin)""","Print67",722)
    AgResearchExportMain({ "sampletissue" : "CY5.Liver","samplename" : "P-2097","sampletreatment" : "Susceptible","samplesubject" : {"name" : "Susceptible", "sex" : "F" }},{"sampletissue" : "CY3.Liver","samplename" : "O-2195","sampletreatment" : "Resistant","samplesubject" : {"name" : "Resistant", "sex" : "F" }},"723.csv","""high scan of Ewes Undosed (given vehicle soln with no sporidesmin)""","Print67",723)
    AgResearchExportMain({ "sampletissue" : "CY5.Liver","samplename" : "P-2018","sampletreatment" : "Susceptible","samplesubject" : {"name" : "Susceptible", "sex" : "F" }},{"sampletissue" : "CY3.Liver","samplename" : "O-2195","sampletreatment" : "Resistant","samplesubject" : {"name" : "Resistant", "sex" : "F" }},"724.csv","""high scan of Ewes Undosed (given vehicle soln with no sporidesmin)""","Print67",724)
    AgResearchExportMain({ "sampletissue" : "CY5.Liver","samplename" : "P-2384","sampletreatment" : "Susceptible","samplesubject" : {"name" : "Susceptible", "sex" : "F" }},{"sampletissue" : "CY3.Liver","samplename" : "O-2201","sampletreatment" : "Resistant","samplesubject" : {"name" : "Resistant", "sex" : "F" }},"725.csv","""high scan of Ewes Undosed (given vehicle soln with no sporidesmin)""","Print67",725)
    AgResearchExportMain({ "sampletissue" : "CY5.Liver","samplename" : "O-2195","sampletreatment" : "Resistant","samplesubject" : {"name" : "Resistant", "sex" : "F" }},{"sampletissue" : "CY3.Liver","samplename" : "P-2384","sampletreatment" : "Susceptible","samplesubject" : {"name" : "Susceptible", "sex" : "F" }},"726.csv","""high scan of Ewes Undosed (given vehicle soln with no sporidesmin)""","Print67",726)
    AgResearchExportMain({ "sampletissue" : "CY5.Liver","samplename" : "O-2286","sampletreatment" : "Resistant","samplesubject" : {"name" : "Resistant", "sex" : "F" }},{"sampletissue" : "CY3.Liver","samplename" : "P-2097","sampletreatment" : "Susceptible","samplesubject" : {"name" : "Susceptible", "sex" : "F" }},"727.csv","""high scan of Ewes Undosed (given vehicle soln with no sporidesmin)""","Print67",727)
    AgResearchExportMain({ "sampletissue" : "CY5.Liver","samplename" : "O-2286","sampletreatment" : "Resistant","samplesubject" : {"name" : "Resistant", "sex" : "F" }},{"sampletissue" : "CY3.Liver","samplename" : "P-2384","sampletreatment" : "Susceptible","samplesubject" : {"name" : "Susceptible", "sex" : "F" }},"728.csv","""high scan of Ewes Undosed (given vehicle soln with no sporidesmin)""","Print67",728)
    AgResearchExportMain({ "sampletissue" : "CY5.Gall bladder","samplename" : "P-2369","sampletreatment" : "Susceptible","samplesubject" : {"name" : "Susceptible", "sex" : "F" }},{"sampletissue" : "CY3.Gall bladder","samplename" : "O-2277","sampletreatment" : "Resistant","samplesubject" : {"name" : "Resistant", "sex" : "F" }},"741.csv","""Dosed ewes with 0.03mg/kg sporidesmin: high scan""","Print67",741)
    AgResearchExportMain({ "sampletissue" : "CY5.Gall bladder","samplename" : "O-2081","sampletreatment" : "resistant","samplesubject" : {"name" : "resistant", "sex" : "F" }},{"sampletissue" : "CY3.Gall bladder","samplename" : "P-2329","sampletreatment" : "Susceptible","samplesubject" : {"name" : "Susceptible", "sex" : "F" }},"742.csv","""Dosed ewes with 0.03mg/kg sporidesmin: high scan""","Print67",742)
    AgResearchExportMain({ "sampletissue" : "CY5.Gall bladder","samplename" : "P-2329","sampletreatment" : "Susceptible","samplesubject" : {"name" : "Susceptible", "sex" : "F" }},{"sampletissue" : "CY3.Gall bladder","samplename" : "O-2277","sampletreatment" : "Resistant","samplesubject" : {"name" : "Resistant", "sex" : "F" }},"743.csv","""Dosed ewes with 0.03mg/kg sporidesmin: high scan""","Print67",743)
    AgResearchExportMain({ "sampletissue" : "CY5.Gall bladder","samplename" : "O-2277","sampletreatment" : "Resistant","samplesubject" : {"name" : "Resistant", "sex" : "F" }},{"sampletissue" : "CY3.Gall bladder","samplename" : "P-2099","sampletreatment" : "Susceptible","samplesubject" : {"name" : "Susceptible", "sex" : "F" }},"744.csv","""Dosed ewes with 0.03mg/kg sporidesmin: high scan""","Print67",744)
    AgResearchExportMain({ "sampletissue" : "CY5.Gall bladder","samplename" : "P-2099","sampletreatment" : "Susceptible","samplesubject" : {"name" : "Susceptible", "sex" : "F" }},{"sampletissue" : "CY3.Gall bladder","samplename" : "O-2081","sampletreatment" : "Resistant","samplesubject" : {"name" : "Resistant", "sex" : "F" }},"745.csv","""Dosed ewes with 0.03mg/kg sporidesmin: high scan""","Print67",745)
    AgResearchExportMain({ "sampletissue" : "CY5.Gall bladder","samplename" : "P-2369","sampletreatment" : "Susceptible","samplesubject" : {"name" : "Susceptible", "sex" : "F" }},{"sampletissue" : "CY3.Gall bladder","samplename" : "O-2033","sampletreatment" : "Resistant","samplesubject" : {"name" : "Resistant", "sex" : "F" }},"746.csv","""Dosed ewes with 0.03mg/kg sporidesmin: high scan""","Print67",746)
    AgResearchExportMain({ "sampletissue" : "CY5.Gall bladder","samplename" : "O-2047","sampletreatment" : "Resistant","samplesubject" : {"name" : "Resistant", "sex" : "F" }},{"sampletissue" : "CY3.Gall bladder","samplename" : "P-2369","sampletreatment" : "Susceptible","samplesubject" : {"name" : "Susceptible", "sex" : "F" }},"747.csv","""Dosed ewes with 0.03mg/kg sporidesmin: high scan""","Print67",747)
    AgResearchExportMain({ "sampletissue" : "CY5.Gall bladder","samplename" : "O-2033","sampletreatment" : "Resistant","samplesubject" : {"name" : "Resistant", "sex" : "F" }},{"sampletissue" : "CY3.Gall bladder","samplename" : "P-2010","sampletreatment" : "Susceptible","samplesubject" : {"name" : "Susceptible", "sex" : "F" }},"748.csv","""Dosed ewes with 0.03mg/kg sporidesmin: high scan""","Print67",748)
    AgResearchExportMain({ "sampletissue" : "CY5.Gall bladder","samplename" : "O-2047","sampletreatment" : "Resistant","samplesubject" : {"name" : "Resistant", "sex" : "F" }},{"sampletissue" : "CY3.Gall bladder","samplename" : "P-2329","sampletreatment" : "Susceptible","samplesubject" : {"name" : "Susceptible", "sex" : "F" }},"749.csv","""Dosed ewes with 0.03mg/kg sporidesmin: high scan""","Print67",749)
    AgResearchExportMain({ "sampletissue" : "CY5.Gall bladder","samplename" : "P-2329","sampletreatment" : "Susceptible","samplesubject" : {"name" : "Susceptible", "sex" : "F" }},{"sampletissue" : "CY3.Gall bladder","samplename" : "O-2033","sampletreatment" : "Resistant","samplesubject" : {"name" : "Resistant", "sex" : "F" }},"750.csv","""Dosed ewes with 0.03mg/kg sporidesmin: high scan""","Print67",750)
    AgResearchExportMain({ "sampletissue" : "CY5.Gall bladder","samplename" : "P-2099","sampletreatment" : "Susceptible","samplesubject" : {"name" : "Susceptible", "sex" : "F" }},{"sampletissue" : "CY3.Gall bladder","samplename" : "O-2047","sampletreatment" : "Resistant","samplesubject" : {"name" : "Resistant", "sex" : "F" }},"751.csv","""Dosed ewes with 0.03mg/kg sporidesmin: high scan""","Print67",751)
    AgResearchExportMain({ "sampletissue" : "CY5.Gall bladder","samplename" : "P-2010","sampletreatment" : "Susceptible","samplesubject" : {"name" : "Susceptible", "sex" : "F" }},{"sampletissue" : "CY3.Gall bladder","samplename" : "O-2047","sampletreatment" : "Resistant","samplesubject" : {"name" : "Resistant", "sex" : "F" }},"752.csv","""Dosed ewes with 0.03mg/kg sporidesmin: high scan""","Print67",752)
    AgResearchExportMain({ "sampletissue" : "CY5.Gall bladder","samplename" : "P-2099","sampletreatment" : "Susceptible","samplesubject" : {"name" : "Susceptible", "sex" : "F" }},{"sampletissue" : "CY3.Gall bladder","samplename" : "O-2033","sampletreatment" : "Resistant","samplesubject" : {"name" : "Resistant", "sex" : "F" }},"753.csv","""Dosed ewes with 0.03mg/kg sporidesmin: high scan""","Print67",753)
    AgResearchExportMain({ "sampletissue" : "CY5.Gall bladder","samplename" : "O-2277","sampletreatment" : "Resistant","samplesubject" : {"name" : "Resistant", "sex" : "F" }},{"sampletissue" : "CY3.Gall bladder","samplename" : "P-2010","sampletreatment" : "Susceptible","samplesubject" : {"name" : "Susceptible", "sex" : "F" }},"754.csv","""Dosed ewes with 0.03mg/kg sporidesmin: high scan""","Print67",754)
    AgResearchExportMain({ "sampletissue" : "CY5.Gall bladder","samplename" : "P-2010","sampletreatment" : "Susceptible","samplesubject" : {"name" : "Susceptible", "sex" : "F" }},{"sampletissue" : "CY3.Gall bladder","samplename" : "O-2081","sampletreatment" : "Resistant","samplesubject" : {"name" : "Resistant", "sex" : "F" }},"755.csv","""Dosed ewes with 0.03mg/kg sporidesmin: high scan""","Print67",755)
    AgResearchExportMain({ "sampletissue" : "CY5.Gall bladder","samplename" : "O-2081","sampletreatment" : "Resistant","samplesubject" : {"name" : "Resistant", "sex" : "F" }},{"sampletissue" : "CY3.Gall bladder","samplename" : "P-2369","sampletreatment" : "Susceptible","samplesubject" : {"name" : "Susceptible", "sex" : "F" }},"756.csv","""Dosed ewes with 0.03mg/kg sporidesmin: high scan""","Print67",756)
    AgResearchExportMain({ "sampletissue" : "CY5.liver","samplename" : "P-2186","sampletreatment" : "susceptible undosed","samplesubject" : {"name" : "susceptible undosed", "sex" : "F" }},{"sampletissue" : "CY3.liver","samplename" : "O-2286","sampletreatment" : "resistant undosed","samplesubject" : {"name" : "resistant undosed", "sex" : "F" }},"1263.csv","""FE-susceptible vs FE-resistant ewes undosed (treated with vehicle solution containing NO sporidesmin)""","Print67",1263)

    return



    BlastImportMain()
    return

    AgResearchArrayMain() # print 67
    return

    BlastImportMain()
    return

    importParms = {
            'microarraylsid' : "print110 Bov20k.txt",
            'datasourcetype' : "GPRFile",
            'physicalsourcepath' : "/data/databases/flatfile/bfiles/agbrdf/microarray/di",
            'studytype' : 'treated vs untreated microarray',
            'overrideGALNamecheck' : True
    }

    #GPRMainAgResearch({ "samplename" : "CY5.G2 863","sampletissue" : "muscle","sampletreatment" : "GG genotype  2hr post"},{"samplename" : "CY3.GC 0 891","sampletissue" : "muscle","sampletreatment" : "GC  time zero"},"110_45 exp 1.gpr","""Gene expression relating to meat tenderness in the Angus longissimus dorsi muscle at slaughter (time 0) versus 2hr post and calpain genotypes GG v CC""",importParms)
    GPRMainAgResearch({ "samplename" : "CY5.C0 890","sampletissue" : "muscle","sampletreatment" : "CC time zero"},{"samplename" : "CY3.C2 890","sampletissue" : "muscle","sampletreatment" : "CC time 2hr post"},"110_0027 exp 14.gpr","""Genes expressed in the Angus(longissimus dorsi) at slaughter (time 0) versus  2hr post plus calpain genotypes GG v CC relating to meat tenderness.""",importParms)
    GPRMainAgResearch({ "samplename" : "CY5.G2 865","sampletissue" : "muscle","sampletreatment" : "GG 2hr post "},{"samplename" : "CY3.G0 865","sampletissue" : "muscle","sampletreatment" : "GG time zero"},"110_30_exp 16.gpr","""Genes expressed in the Angus(longissimus dorsi) at slaughter (time 0) versus  2hr post plus calpain genotypes GG v CC relating to meat tenderness.""",importParms)
    GPRMainAgResearch({ "samplename" : "CY5.C2 905","sampletissue" : "muscle","sampletreatment" : "CC  time 2hr post"},{"samplename" : "CY3.G0 863","sampletissue" : "muscle","sampletreatment" : "GG time zero"},"110_33 exp17.gpr","""Genes expressed in the Angus(longissimus dorsi) at slaughter (time 0) versus  2hr post plus calpain genotypes GG v CC relating to meat tenderness.""",importParms)
    GPRMainAgResearch({ "samplename" : "CY5.G2 863","sampletissue" : "muscle","sampletreatment" : "GG  time 2hr post"},{"samplename" : "CY3.G0 863","sampletissue" : "muscle","sampletreatment" : "GG time zero"},"110_34 exp18.gpr","""Genes expressed in the Angus(longissimus dorsi) at slaughter (time 0) versus  2hr post plus calpain genotypes GG v CC relating to meat tenderness.""",importParms)
    GPRMainAgResearch({ "samplename" : "CY5.G0 860","sampletissue" : "muscle","sampletreatment" : "GG time zero"},{"samplename" : "CY3.C2 900","sampletissue" : "muscle","sampletreatment" : "CC time 2hr post"},"110_32 exp 20.gpr","""Genes expressed in the Angus(longissimus dorsi) at slaughter (time 0) versus  2hr post plus calpain genotypes GG v CC relating to meat tenderness.""",importParms)
    GPRMainAgResearch({ "samplename" : "CY5.G0 860","sampletissue" : "muscle","sampletreatment" : "GG  time zero"},{"samplename" : "CY3.G2 860","sampletissue" : "muscle","sampletreatment" : "GG  2hr post"},"110_36 exp 21.gpr","""Genes expressed in the Angus(longissimus dorsi) at slaughter (time 0) versus  2hr post plus calpain genotypes GG v CC relating to meat tenderness.""",importParms)
    GPRMainAgResearch({ "samplename" : "CY5.C2 890","sampletissue" : "muscle","sampletreatment" : "CC 2hr post"},{"samplename" : "CY3.C0 900","sampletissue" : "muscle","sampletreatment" : "CC  time zero"},"110_37 exp 22.gpr","""Genes expressed in the Angus(longissimus dorsi) at slaughter (time 0) versus  2hr post plus calpain genotypes GG v CC relating to meat tenderness.""",importParms)
    GPRMainAgResearch({ "samplename" : "CY5.C2 900","sampletissue" : "muscle","sampletreatment" : "CC  2hr post"},{"samplename" : "CY3.G2 863","sampletissue" : "muscle","sampletreatment" : "CC  2 hr post"},"110_38 exp 23.gpr","""Genes expressed in the Angus(longissimus dorsi) at slaughter (time 0) versus  2hr post plus calpain genotypes GG v CC relating to meat tenderness.""",importParms)
    GPRMainAgResearch({ "samplename" : "CY5.GC 0 891","sampletissue" : "muscle","sampletreatment" : "GC  time zero"},{"samplename" : "CY3.G0 860","sampletissue" : "muscle","sampletreatment" : "GG time zero"},"110_39 exp 24.gpr","""Genes expressed in the Angus(longissimus dorsi) at slaughter (time 0) versus  2hr post plus calpain genotypes GG v CC relating to meat tenderness.""",importParms)
    GPRMainAgResearch({ "samplename" : "CY5.C2 894","sampletissue" : "muscle","sampletreatment" : "CC  2hr post"},{"samplename" : "CY3.C0 890","sampletissue" : "muscle","sampletreatment" : "CC time zero"},"110_40 exp 8.gpr","""Genes expressed in the Angus(longissimus dorsi) at slaughter (time 0) versus  2hr post plus calpain genotypes GG v CC relating to meat tenderness.""",importParms)
    GPRMainAgResearch({ "samplename" : "CY5.G2 865","sampletissue" : "muscle","sampletreatment" : "GG  2hr post"},{"samplename" : "CY3.C2 905","sampletissue" : "muscle","sampletreatment" : "CC  2 hr post"},"110_31 exp 19.gpr","""Gene expression relating to meat tenderness in the Angus longissimus dorsi muscle at slaughter (time 0) versus 2hr post and calpain genotypes GG v CC """,importParms)
    GPRMainAgResearch({ "samplename" : "CY5.C0 900","sampletissue" : "muscle","sampletreatment" : "CC  time zero"},{"samplename" : "CY3.C2 900","sampletissue" : "muscle","sampletreatment" : "CC  2 hr post"},"110_28 exp15.gpr","""Gene expression relating to meat tenderness in the Angus longissimus dorsi muscle at slaughter (time 0) versus 2hr post and calpain genotypes GG v CC """,importParms)


    importParms = {
            'microarraylsid' : "print113bov20k.txt",
            'datasourcetype' : "GPRFile",
            'physicalsourcepath' : "/data/databases/flatfile/bfiles/agbrdf/microarray/di",
            'studytype' : 'treated vs untreated microarray',
            'overrideGALNamecheck' : True
    }


    GPRMainAgResearch({ "samplename" : "CY5.C0 894","sampletissue" : "muscle","sampletreatment" : "CC  time zero"},{"samplename" : "CY3.G2 865","sampletissue" : "muscle","sampletreatment" : "GG  2 hr post"},"113_31 epx 6.gpr","""Gene expression relating to meat tenderness in the Angus longissimus dorsi muscle at slaughter (time 0) versus 2hr post and calpain genotypes GG v CC """,importParms)
    GPRMainAgResearch({ "samplename" : "CY5.G2 860","sampletissue" : "muscle","sampletreatment" : "GG  2hr post"},{"samplename" : "CY3.C2 894","sampletissue" : "muscle","sampletreatment" : "CC 2 hr post"},"113_40 exp 2.gpr","""Gene expression relating to meat tenderness in the Angus longissimus dorsi muscle at slaughter (time 0) versus 2hr post and calpain genotypes GG v CC """,importParms)
    GPRMainAgResearch({ "samplename" : "CY5.GC2 891","sampletissue" : "muscle","sampletreatment" : "CC  2hr post"},{"samplename" : "CY3.G2 890","sampletissue" : "muscle","sampletreatment" : "CC2 hr post"},"113_41 exp 3.gpr","""Gene expression relating to meat tenderness in the Angus longissimus dorsi muscle at slaughter (time 0) versus 2hr post and calpain genotypes GG v CC """,importParms)
    GPRMainAgResearch({ "samplename" : "CY5.G0 865","sampletissue" : "muscle","sampletreatment" : "GG  time zero"},{"samplename" : "CY3.GC2 891","sampletissue" : "muscle","sampletreatment" : "GC 2 hr post"},"113_42 exp 4.gpr","""Gene expression relating to meat tenderness in the Angus longissimus dorsi muscle at slaughter (time 0) versus 2hr post and calpain genotypes GG v CC """,importParms)
    GPRMainAgResearch({ "samplename" : "CY5.C0 905","sampletissue" : "muscle","sampletreatment" : "CC  time zero"},{"samplename" : "CY3.G2 860","sampletissue" : "muscle","sampletreatment" : "GG 2 hr post"},"113_32 exp 7.gpr","""Gene expression relating to meat tenderness in the Angus longissimus dorsi muscle at slaughter (time 0) versus 2hr post and calpain genotypes GG v CC """,importParms)
    GPRMainAgResearch({ "samplename" : "CY5.GC2 891","sampletissue" : "muscle","sampletreatment" : "GC  2hr post"},{"samplename" : "CY3.GC 0  891","sampletissue" : "muscle","sampletreatment" : "GC  time zero"},"113_34 exp 9 .gpr","""Gene expression relating to meat tenderness in the Angus longissimus dorsi muscle at slaughter (time 0) versus 2hr post and calpain genotypes GG v CC """,importParms)
    GPRMainAgResearch({ "samplename" : "CY5.C0 890","sampletissue" : "muscle","sampletreatment" : "CC  time zero"},{"samplename" : "CY3.C0  905","sampletissue" : "muscle","sampletreatment" : "CC  time zero"},"113_35 exp 10.gpr","""Gene expression relating to meat tenderness in the Angus longissimus dorsi muscle at slaughter (time 0) versus 2hr post and calpain genotypes GG v CC """,importParms)
    GPRMainAgResearch({ "samplename" : "CY5.C2 905","sampletissue" : "muscle","sampletreatment" : "CC  2hr post"},{"samplename" : "CY3.C0  905","sampletissue" : "muscle","sampletreatment" : "CC  time zero"},"113_36 exp 11.gpr","""Gene expression relating to meat tenderness in the Angus longissimus dorsi muscle at slaughter (time 0) versus 2hr post and calpain genotypes GG v CC """,importParms)
    GPRMainAgResearch({ "samplename" : "CY5.C0 894","sampletissue" : "muscle","sampletreatment" : "CC  time zero"},{"samplename" : "CY3.C2 894","sampletissue" : "muscle","sampletreatment" : "CC  2 hr post"},"113_38 exp 12.gpr","""Gene expression relating to meat tenderness in the Angus longissimus dorsi muscle at slaughter (time 0) versus 2hr post and calpain genotypes GG v CC """,importParms)
    GPRMainAgResearch({ "samplename" : "CY5.G0 863","sampletissue" : "muscle","sampletreatment" : "GG time zero"},{"samplename" : "CY3.C0 894","sampletissue" : "muscle","sampletreatment" : "CC  time zero"},"113_39 exp 13.gpr","""Gene expression relating to meat tenderness in the Angus longissimus dorsi muscle at slaughter (time 0) versus 2hr post and calpain genotypes GG v CC """,importParms)
    GPRMainAgResearch({ "samplename" : "CY5.C0 900","sampletissue" : "muscle","sampletreatment" : "CC  time zero"},{"samplename" : "CY3.G0 865","sampletissue" : "muscle","sampletreatment" : "GG  time zero"},"113_37c exp 5.gpr","""Genes expressed in the Angus(longissimus dorsi) at slaughter (time 0) versus  2hr post plus calpain genotypes GG v CC relating to meat tenderness""",importParms)

    return


    GALMain()
    return


    BlastImportMain()
    return




    AgResearchExportMain({ "samplename" : "CY5.mammary tissue","sampletissue" : "696","sampletreatment" : "B","samplesubject" : {"name" : "696", "sex" : "F" }},{"samplename" : "CY3.mammary tissue","sampletissue" : "699","sampletreatment" : "A","samplesubject" : {"name" : "699", "sex" : "F" }},"2021.csv","""Mammary gland tissue, T72, Atropine vs GH experiment""","Print114",2021)
    AgResearchExportMain({ "samplename" : "CY5.mammary tissue","sampletissue" : "696","sampletreatment" : "B","samplesubject" : {"name" : "696", "sex" : "F" }},{"samplename" : "CY3.mammary tissue","sampletissue" : "699","sampletreatment" : "A","samplesubject" : {"name" : "699", "sex" : "F" }},"2022.csv","""Mammary gland tissue, T72, Atropine vs GH experiment""","Print114",2022)
    AgResearchExportMain({ "samplename" : "CY5.mammary tissue","sampletissue" : "701","sampletreatment" : "C","samplesubject" : {"name" : "701", "sex" : "F" }},{"samplename" : "CY3.mammary tissue","sampletissue" : "696","sampletreatment" : "B","samplesubject" : {"name" : "696", "sex" : "F" }},"2023.csv","""Mammary gland tissue, T72, Atropine vs GH experiment""","Print114",2023)
    AgResearchExportMain({ "samplename" : "CY5.mammary tissue","sampletissue" : "705","sampletreatment" : "a","samplesubject" : {"name" : "705", "sex" : "F" }},{"samplename" : "CY3.mammary tissue","sampletissue" : "701","sampletreatment" : "c","samplesubject" : {"name" : "701", "sex" : "F" }},"2024.csv","""Mammary gland tissue, T72, Atropine vs GH experiment""","Print114",2024)
    AgResearchExportMain({ "samplename" : "CY5.mammary tissue","sampletissue" : "697","sampletreatment" : "b","samplesubject" : {"name" : "697", "sex" : "F" }},{"samplename" : "CY3.mammary tissue","sampletissue" : "705","sampletreatment" : "A","samplesubject" : {"name" : "705", "sex" : "F" }},"2025.csv","""Mammary gland tissue, T72, Atropine vs GH experiment""","Print114",2025)
    AgResearchExportMain({ "samplename" : "CY5.mammary tissue","sampletissue" : "702","sampletreatment" : "c","samplesubject" : {"name" : "702", "sex" : "F" }},{"samplename" : "CY3.mammary tissue","sampletissue" : "697","sampletreatment" : "b","samplesubject" : {"name" : "697", "sex" : "F" }},"2026.csv","""(Mammary gland tissue, T72, Atropine vs GH experiment""","Print114",2026)
    AgResearchExportMain({ "samplename" : "CY5.mammary tissue","sampletissue" : "706","sampletreatment" : "a","samplesubject" : {"name" : "706", "sex" : "F" }},{"samplename" : "CY3.mammary tissue","sampletissue" : "702","sampletreatment" : "c","samplesubject" : {"name" : "702", "sex" : "F" }},"2027.csv","""Mammary gland tissue, T72, Atropine vs GH experiment""","Print114",2027)
    AgResearchExportMain({ "samplename" : "CY5.mammary tissue","sampletissue" : "698","sampletreatment" : "b","samplesubject" : {"name" : "698", "sex" : "F" }},{"samplename" : "CY3.mammary tissue","sampletissue" : "706","sampletreatment" : "a","samplesubject" : {"name" : "706", "sex" : "F" }},"2028.csv","""Mammary gland tissue, T72, Atropine vs GH experiment""","Print114",2028)
    AgResearchExportMain({ "samplename" : "CY5.mammary tissue","sampletissue" : "698","sampletreatment" : "b","samplesubject" : {"name" : "698", "sex" : "F" }},{"samplename" : "CY3.mammary tissue","sampletissue" : "706","sampletreatment" : "a","samplesubject" : {"name" : "706", "sex" : "F" }},"2029.csv","""Mammary gland tissue, T72, Atropine vs GH experiment""","Print114",2029)
    AgResearchExportMain({ "samplename" : "CY5.mammary tissue","sampletissue" : "703","sampletreatment" : "c","samplesubject" : {"name" : "703", "sex" : "F" }},{"samplename" : "CY3.mammary tissue","sampletissue" : "698","sampletreatment" : "b","samplesubject" : {"name" : "698", "sex" : "F" }},"2030.csv","""Mammary gland tissue, T72, Atropine vs GH experiment""","Print114",2030)
    AgResearchExportMain({ "samplename" : "CY5.mammary tissue","sampletissue" : "707","sampletreatment" : "a","samplesubject" : {"name" : "707", "sex" : "F" }},{"samplename" : "CY3.mammary tissue","sampletissue" : "703","sampletreatment" : "c","samplesubject" : {"name" : "703", "sex" : "F" }},"2031.csv","""Mammary gland tissue, T72, Atropine vs GH experiment""","Print114",2031)
    AgResearchExportMain({ "samplename" : "CY5.mammary tissue","sampletissue" : "701","sampletreatment" : "c","samplesubject" : {"name" : "701", "sex" : "F" }},{"samplename" : "CY3.mammary tissue","sampletissue" : "696","sampletreatment" : "b","samplesubject" : {"name" : "696", "sex" : "F" }},"2032.csv","""Mammary gland tissue, T72, Atropine vs GH experiment""","Print114",2032)
    AgResearchExportMain({ "samplename" : "CY5.mammary tissue","sampletissue" : "700","sampletreatment" : "b","samplesubject" : {"name" : "700", "sex" : "F" }},{"samplename" : "CY3.mammary tissue","sampletissue" : "707","sampletreatment" : "a","samplesubject" : {"name" : "707", "sex" : "F" }},"2033.csv","""Mammary gland tissue, T72, Atropine vs GH experiment""","Print114",2033)
    AgResearchExportMain({ "samplename" : "CY5.mammary tissue","sampletissue" : "704","sampletreatment" : "c","samplesubject" : {"name" : "704", "sex" : "F" }},{"samplename" : "CY3.mammary tissue","sampletissue" : "700","sampletreatment" : "b","samplesubject" : {"name" : "700", "sex" : "F" }},"2034.csv","""(Mammary gland tissue, T72, Atropine vs GH experiment""","Print114",2034)
    AgResearchExportMain({ "samplename" : "CY5.mammary tissue","sampletissue" : "699","sampletreatment" : "a","samplesubject" : {"name" : "699", "sex" : "F" }},{"samplename" : "CY3.mammary tissue","sampletissue" : "704","sampletreatment" : "c","samplesubject" : {"name" : "704", "sex" : "F" }},"2035.csv","""Mammary gland tissue, T72, Atropine vs GH experiment""","Print114",2035)
    AgResearchExportMain({ "samplename" : "CY5.mammary tissue","sampletissue" : "698","sampletreatment" : "b","samplesubject" : {"name" : "698", "sex" : "F" }},{"samplename" : "CY3.mammary tissue","sampletissue" : "699","sampletreatment" : "a","samplesubject" : {"name" : "699", "sex" : "F" }},"2036.csv","""Mammary gland tissue, T72, Atropine vs GH experiment""","Print114",2036)
    AgResearchExportMain({ "samplename" : "CY5.mammary tissue","sampletissue" : "704","sampletreatment" : "c","samplesubject" : {"name" : "704", "sex" : "F" }},{"samplename" : "CY3.mammary tissue","sampletissue" : "697","sampletreatment" : "b","samplesubject" : {"name" : "697", "sex" : "F" }},"2037.csv","""Mammary gland tissue, T72, Atropine vs GH experiment""","Print114",2037)
    AgResearchExportMain({ "samplename" : "CY5.mammary tissue","sampletissue" : "696","sampletreatment" : "b","samplesubject" : {"name" : "696", "sex" : "F" }},{"samplename" : "CY3.mammary tissue","sampletissue" : "706","sampletreatment" : "a","samplesubject" : {"name" : "706", "sex" : "F" }},"2038.csv","""Mammary gland tissue, T72, Atropine vs GH experiment""","Print114",2038)
    AgResearchExportMain({ "samplename" : "CY5.mammary tissue","sampletissue" : "701","sampletreatment" : "c","samplesubject" : {"name" : "701", "sex" : "F" }},{"samplename" : "CY3.mammary tissue","sampletissue" : "700","sampletreatment" : "b","samplesubject" : {"name" : "700", "sex" : "F" }},"2039.csv","""Mammary gland tissue, T72, Atropine vs GH experiment""","Print114",2039)
    AgResearchExportMain({ "samplename" : "CY5.mammary tissue","sampletissue" : "705","sampletreatment" : "a","samplesubject" : {"name" : "705", "sex" : "F" }},{"samplename" : "CY3.mammary tissue","sampletissue" : "703","sampletreatment" : "c","samplesubject" : {"name" : "703", "sex" : "F" }},"2040.csv","""Mammary gland tissue, T72, Atropine vs GH experiment""","Print114",2040)
    AgResearchExportMain({ "samplename" : "CY5.mammary tissue","sampletissue" : "700","sampletreatment" : "b","samplesubject" : {"name" : "700", "sex" : "F" }},{"samplename" : "CY3.mammary tissue","sampletissue" : "707","sampletreatment" : "a","samplesubject" : {"name" : "707", "sex" : "F" }},"2041.csv","""Mammary gland tissue, T72, Atropine vs GH experiment""","Print114",2041)
    AgResearchExportMain({ "samplename" : "CY5.mammary tissue","sampletissue" : "705","sampletreatment" : "a","samplesubject" : {"name" : "705", "sex" : "F" }},{"samplename" : "CY3.mammary tissue","sampletissue" : "701","sampletreatment" : "c","samplesubject" : {"name" : "701", "sex" : "F" }},"2042.csv","""Mammary gland tissue, T72, Atropine vs GH experiment""","Print114",2042)
    AgResearchExportMain({ "samplename" : "CY5.mammary tissue","sampletissue" : "697","sampletreatment" : "b","samplesubject" : {"name" : "697", "sex" : "F" }},{"samplename" : "CY3.mammary tissue","sampletissue" : "705","sampletreatment" : "a","samplesubject" : {"name" : "705", "sex" : "F" }},"2043.csv","""Mammary gland tissue, T72, Atropine vs GH experiment""","Print114",2043)
    AgResearchExportMain({ "samplename" : "CY5.mammary tissue","sampletissue" : "702","sampletreatment" : "c","samplesubject" : {"name" : "702", "sex" : "F" }},{"samplename" : "CY3.mammary tissue","sampletissue" : "697","sampletreatment" : "b","samplesubject" : {"name" : "697", "sex" : "F" }},"2044.csv","""(Mammary gland tissue, T72, Atropine vs GH experiment""","Print114",2044)
    AgResearchExportMain({ "samplename" : "CY5.mammary tissue","sampletissue" : "706","sampletreatment" : "a","samplesubject" : {"name" : "706", "sex" : "F" }},{"samplename" : "CY3.mammary tissue","sampletissue" : "702","sampletreatment" : "c","samplesubject" : {"name" : "702", "sex" : "F" }},"2045.csv","""Mammary gland tissue, T72, Atropine vs GH experiment""","Print114",2045)
    AgResearchExportMain({ "samplename" : "CY5.mammary tissue","sampletissue" : "703","sampletreatment" : "c","samplesubject" : {"name" : "703", "sex" : "F" }},{"samplename" : "CY3.mammary tissue","sampletissue" : "698","sampletreatment" : "b","samplesubject" : {"name" : "698", "sex" : "F" }},"2046.csv","""Mammary gland tissue, T72, Atropine vs GH experiment""","Print114",2046)
    AgResearchExportMain({ "samplename" : "CY5.mammary tissue","sampletissue" : "707","sampletreatment" : "a","samplesubject" : {"name" : "707", "sex" : "F" }},{"samplename" : "CY3.mammary tissue","sampletissue" : "703","sampletreatment" : "c","samplesubject" : {"name" : "703", "sex" : "F" }},"2047.csv","""Mammary gland tissue, T72, Atropine vs GH experiment""","Print114",2047)
    AgResearchExportMain({ "samplename" : "CY5.mammary tissue","sampletissue" : "704","sampletreatment" : "c","samplesubject" : {"name" : "704", "sex" : "F" }},{"samplename" : "CY3.mammary tissue","sampletissue" : "700","sampletreatment" : "b","samplesubject" : {"name" : "700", "sex" : "F" }},"2048.csv","""Mammary gland tissue, T72, Atropine vs GH experiment""","Print114",2048)
    AgResearchExportMain({ "samplename" : "CY5.mammary tissue","sampletissue" : "699","sampletreatment" : "a","samplesubject" : {"name" : "699", "sex" : "F" }},{"samplename" : "CY3.mammary tissue","sampletissue" : "704","sampletreatment" : "c","samplesubject" : {"name" : "704", "sex" : "F" }},"2049.csv","""Mammary gland tissue, T72, Atropine vs GH experiment""","Print114",2049)
    AgResearchExportMain({ "samplename" : "CY5.mammary tissue","sampletissue" : "698","sampletreatment" : "b","samplesubject" : {"name" : "698", "sex" : "F" }},{"samplename" : "CY3.mammary tissue","sampletissue" : "699","sampletreatment" : "a","samplesubject" : {"name" : "699", "sex" : "F" }},"2050.csv","""Mammary gland tissue, T72, Atropine vs GH experiment""","Print114",2050)
    AgResearchExportMain({ "samplename" : "CY5.mammary tissue","sampletissue" : "704","sampletreatment" : "c","samplesubject" : {"name" : "704", "sex" : "F" }},{"samplename" : "CY3.mammary tissue","sampletissue" : "697","sampletreatment" : "b","samplesubject" : {"name" : "697", "sex" : "F" }},"2051.csv","""Mammary gland tissue, T72, Atropine vs GH experiment""","Print114",2051)
    AgResearchExportMain({ "samplename" : "CY5.mammary tissue","sampletissue" : "707","sampletreatment" : "a","samplesubject" : {"name" : "707", "sex" : "F" }},{"samplename" : "CY3.mammary tissue","sampletissue" : "702","sampletreatment" : "c","samplesubject" : {"name" : "702", "sex" : "F" }},"2052.csv","""Mammary gland tissue, T72, Atropine vs GH experiment""","Print114",2052)
    AgResearchExportMain({ "samplename" : "CY5.mammary tissue","sampletissue" : "707","sampletreatment" : "a","samplesubject" : {"name" : "707", "sex" : "F" }},{"samplename" : "CY3.mammary tissue","sampletissue" : "702","sampletreatment" : "c","samplesubject" : {"name" : "702", "sex" : "F" }},"2053.csv","""Mammary gland tissue, T72, Atropine vs GH experiment""","Print114",2053)
    AgResearchExportMain({ "samplename" : "CY5.mammary tissue","sampletissue" : "696","sampletreatment" : "b","samplesubject" : {"name" : "696", "sex" : "F" }},{"samplename" : "CY3.mammary tissue","sampletissue" : "706","sampletreatment" : "a","samplesubject" : {"name" : "706", "sex" : "F" }},"2054.csv","""Mammary gland tissue, T72, Atropine vs GH experiment""","Print114",2054)
    AgResearchExportMain({ "samplename" : "CY5.mammary tissue","sampletissue" : "701","sampletreatment" : "c","samplesubject" : {"name" : "701", "sex" : "F" }},{"samplename" : "CY3.mammary tissue","sampletissue" : "700","sampletreatment" : "b","samplesubject" : {"name" : "700", "sex" : "F" }},"2055.csv","""Mammary gland tissue, T72, Atropine vs GH experiment""","Print114",2055)
    AgResearchExportMain({ "samplename" : "CY5.mammary tissue","sampletissue" : "705","sampletreatment" : "a","samplesubject" : {"name" : "705", "sex" : "F" }},{"samplename" : "CY3.mammary tissue","sampletissue" : "703","sampletreatment" : "c","samplesubject" : {"name" : "703", "sex" : "F" }},"2056.csv","""Mammary gland tissue, T72, Atropine vs GH experiment""","Print114",2056)

    return

    BlastImportMain()
    return

    #AffyImportMain(subjectdata={'xreflsid' : 'Unknown animal subject','subjectname' : 'Unknown animal subject','subjectdescription' : 'Dummy subject record, where animal unknown','subjectspeciesname' : 'Unknown'},\
    #     sampledata={'xreflsid' : 'Unknown animal subject', 'samplename' : 'Unknown animal subject','sampletissue' : 'unknown','sampletreatment' : 'unknown','sampletype' : 'mRNA extract for microarray experiment'},\
    #     arraydata={'xreflsid' : 'Affymetrix.Bovine Genome Array'},\
    #     filedata={'filename' : 'NR0001.csv' , 'physicalsourceuri' : '/data/home/seqstore/agbrdf/affy/NR0001.csv' , 'datasourcetype' : 'CSV from Affy CEL File'},\
    #     experimentdata={'studytype' : 'treated vs untreated microarray', 'studydescription' : 'unknown'})    
    AffyImportMain(subjectdata={'xreflsid' : 'Unknown animal subject','subjectname' : 'Unknown animal subject','subjectdescription' : 'Dummy subject record, where animal unknown','subjectspeciesname' : 'Unknown'},\
         sampledata={'xreflsid' : 'Unknown animal subject', 'samplename' : 'Unknown animal subject','sampletissue' : 'unknown','sampletreatment' : 'unknown','sampletype' : 'mRNA extract for microarray experiment'},\
         arraydata={'xreflsid' : 'Affymetrix.Bovine Genome Array'},\
         filedata={'filename' : 'NR0002.csv' , 'physicalsourceuri' : '/data/home/seqstore/agbrdf/affy/NR0002.csv' , 'datasourcetype' : 'CSV from Affy CEL File'},\
         experimentdata={'studytype' : 'treated vs untreated microarray', 'studydescription' : 'unknown'})    
    AffyImportMain(subjectdata={'xreflsid' : 'Unknown animal subject','subjectname' : 'Unknown animal subject','subjectdescription' : 'Dummy subject record, where animal unknown','subjectspeciesname' : 'Unknown'},\
         sampledata={'xreflsid' : 'Unknown animal subject', 'samplename' : 'Unknown animal subject','sampletissue' : 'unknown','sampletreatment' : 'unknown','sampletype' : 'mRNA extract for microarray experiment'},\
         arraydata={'xreflsid' : 'Affymetrix.Bovine Genome Array'},\
         filedata={'filename' : 'NR0003.csv' , 'physicalsourceuri' : '/data/home/seqstore/agbrdf/affy/NR0003.csv' , 'datasourcetype' : 'CSV from Affy CEL File'},\
         experimentdata={'studytype' : 'treated vs untreated microarray', 'studydescription' : 'unknown'})    
    AffyImportMain(subjectdata={'xreflsid' : 'Unknown animal subject','subjectname' : 'Unknown animal subject','subjectdescription' : 'Dummy subject record, where animal unknown','subjectspeciesname' : 'Unknown'},\
         sampledata={'xreflsid' : 'Unknown animal subject', 'samplename' : 'Unknown animal subject','sampletissue' : 'unknown','sampletreatment' : 'unknown','sampletype' : 'mRNA extract for microarray experiment'},\
         arraydata={'xreflsid' : 'Affymetrix.Bovine Genome Array'},\
         filedata={'filename' : 'NR0004.csv' , 'physicalsourceuri' : '/data/home/seqstore/agbrdf/affy/NR0004.csv' , 'datasourcetype' : 'CSV from Affy CEL File'},\
         experimentdata={'studytype' : 'treated vs untreated microarray', 'studydescription' : 'unknown'})    
    return


    importParms = {
            'microarraylsid' : "Microbial.Methanogen.print 119 MRUM.txt",
            'datasourcetype' : "GPRFile",
            'physicalsourcepath' : "/data/databases/flatfile/bfiles/agbrdf/microarray/microbial/12052008",
            'studytype' : 'treated vs untreated microarray',
            'overrideGALNamecheck' : True
    }

    GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"03a-C3b medium.gpr","""unavailable""",importParms)
    GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"C1a-O1b high.gpr","""unavailable""",importParms)
    GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"C1a-O1b low.gpr","""unavailable""",importParms)
    GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"C1a-O1b medium.gpr","""unavailable""",importParms)
    GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"c2a-o2b low.gpr","""unavailable""",importParms)
    GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"c2a-o2b medium.gpr","""unavailable""",importParms)
    GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"C2b-O2a high.gpr","""unavailable""",importParms)
    GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"c3a-o3b high.gpr","""unavailable""",importParms)
    GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"c3a-o3b low.gpr","""unavailable""",importParms)
    GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"c3a-o3b medium.gpr","""unavailable""",importParms)
    GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"o2a-c2b high.gpr","""unavailable""",importParms)
    GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"o2a-c2b low.gpr","""unavailable""",importParms)
    GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"o2a-c2b medium.gpr","""unavailable""",importParms)
    GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"o3a-c3b high.gpr","""unavailable""",importParms)
    GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"o3a-c3b low.gpr","""unavailable""",importParms)
    GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"slide 1_high.gpr","""unavailable""",importParms)
    GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"slide 1_low.gpr","""unavailable""",importParms)
    GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"slide 1_medium.gpr","""unavailable""",importParms)

    return


    #GALMain()
    #return


    importParms = {
            'microarraylsid' : "print 139 ov21K.txt",
            'datasourcetype' : "GPRFile",
            'physicalsourcepath' : "/data/databases/flatfile/bfiles/agbrdf/microarray/lisafan",
            'studytype' : 'treated vs untreated microarray',
            'overrideGALNamecheck' : False
    }

    GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"139-30 high 0.97.gpr","""unavailable""",importParms)
    GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"139-30 low.gpr","""unavailable""",importParms)
    GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"139-31 high 1.01.gpr","""unavailable""",importParms)
    GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"139-31 low 1.02.gpr","""unavailable""",importParms)
    GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"139-32 high 0.95.gpr","""unavailable""",importParms)
    GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"139-32 low 1.00.gpr","""unavailable""",importParms)
    GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"139-33 high 0.97.gpr","""unavailable""",importParms)
    GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"139-33 low 1.00.gpr","""unavailable""",importParms)
    GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"139-34 high 1.03.gpr","""unavailable""",importParms)
    GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"139-34 low 1.01.gpr","""unavailable""",importParms)
    GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"139-35 high 1.01.gpr","""unavailable""",importParms)
    GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"139-35 low 1.00.gpr","""unavailable""",importParms)
    GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"139-36 high 0.98.gpr","""unavailable""",importParms)
    GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"139-36 low 1.02.gpr","""unavailable""",importParms)
    GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"139-37 high 1.00.gpr","""unavailable""",importParms)
    GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"139-37 low 0.97.gpr","""unavailable""",importParms)
    GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"139-38 high 0.99.gpr","""unavailable""",importParms)
    GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"139-38 low 0.97.gpr","""unavailable""",importParms)
    GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"139-39 high 0.96.gpr","""unavailable""",importParms)
    GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"139-39 low 0.95.gpr","""unavailable""",importParms)
    GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"139-40 high 0.97.gpr","""unavailable""",importParms)
    GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"139-40 low 0.96.gpr","""unavailable""",importParms)
    GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"139-41 high 1.03.gpr","""unavailable""",importParms)
    GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"139-41 low 0.98.gpr","""unavailable""",importParms)
    GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"139-42 high 1.01.gpr","""unavailable""",importParms)
    GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"139-42 low 0.99.gpr","""unavailable""",importParms)
    GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"139-43 high 0.97.gpr","""unavailable""",importParms)
    GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"139-43 low 0.96.gpr","""unavailable""",importParms)
    GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"139-44 high 0.99.gpr","""unavailable""",importParms)
    GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"139-44 low 0.96.gpr","""unavailable""",importParms)
    GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"139-45 high 0.98.gpr","""unavailable""",importParms)
    GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"139-45 low 1.05.gpr","""unavailable""",importParms)

    return


    #AgResearchArrayMain() #print79
    #return

    BlastImportMain()
    return


    # Anne Oconnell exps
    importParms = {
            'microarraylsid' : "print 139 ov21K.txt",
            'datasourcetype' : "GPRFile",
            'physicalsourcepath' : "/data/databases/flatfile/bfiles/agbrdf/microarray/anneoconnell",
            'studytype' : 'treated vs untreated microarray',
            'overrideGALNamecheck' : False
    }
    # redo of one that was rescanned
    GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"p139 s29 R6 G5.gpr","""unavailable""",importParms)
    return

    #GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"p139 s10 R6 G3.gpr","""unavailable""",importParms)
    #GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"p139 s11 R7 G1.gpr","""unavailable""",importParms)
    #GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"p139 s12 R9 G1.gpr","""unavailable""",importParms)
    #GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"P139 S14 R3 G10.gpr","""unavailable""",importParms)
    #GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"P139 S15 R2 G9.gpr","""unavailable""",importParms)
    #GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"P139 S17 R3 G10.gpr","""unavailable""",importParms)
    #GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"P139 S19 R10 G4.gpr","""unavailable""",importParms)
    #GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"P139 S22 R10 G2.gpr","""unavailable""",importParms)
    #GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"p139 s23 R5 G10.gpr","""unavailable""",importParms)
    #GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"p139 s24 R3 G8.gpr","""unavailable""",importParms)
    #GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"p139 s25 R4 G9.gpr","""unavailable""",importParms)
    #GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"p139 s26 R2 G7.gpr","""unavailable""",importParms)
    #GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"p139 s27 R9 G3.gpr","""unavailable""",importParms)
    #GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"p139 s28 R8 G2.gpr","""unavailable""",importParms)
    ####GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"p139 s29 R6 G5.gpr","""unavailable""",importParms)
    GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"P139 S2 R5 G7.gpr","""unavailable""",importParms)
    GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"P139 S4 R1 G8.gpr","""unavailable""",importParms)
    GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"P139 S6 R7 G4.gpr","""unavailable""",importParms)
    GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"p139 s8 R8 G5.gpr","""unavailable""",importParms)

    return


    GALMain()
    return

    #AgResearchExportMain({ "sampletissue" : "CY5.mammary gland","samplename" : "6 hours","sampletreatment" : "cow #734","samplesubject" : {"name" : "cow 734", "sex" : "F" }},{"sampletissue" : "CY3.mammary gland","samplename" : "24 hours","sampletreatment" : "cow number #731","samplesubject" : {"name" : "cow 731", "sex" : "F" }},"80.csv","""(Please enter a description here)Temporal changes in mammary gland post-milking""","Print20",80)

    AgResearchExportMain({ "sampletissue" : "CY5.cow 428 alveolar 6hr post","samplename" : "75ug Trizol only","sampletreatment" : "Standard","samplesubject" : {"name" : "cow 428", "sex" : "F" }},{"sampletissue" : "CY3.cow 88 alveolar 24 hr post","samplename" : "75 ug  Trizol only","sampletreatment" : "Standard","samplesubject" : {"name" : "cow 88", "sex" : "F" }},"85.csv","""Post milking timcourse experiment with lactating Dairy cows.  Comparing 6 hours with 24 hours post milking""","Print20",85)
    AgResearchExportMain({ "sampletissue" : "CY5.cow 734 alveolar 6hr post","samplename" : "75ug RNA Trizol only","sampletreatment" : "6hr post milking","samplesubject" : {"name" : "cow 734", "sex" : "F" }},{"sampletissue" : "CY3.cow 731 alveolar 24 hr post","samplename" : "75 ug  RNA Trizol only","sampletreatment" : "24 hr post milking","samplesubject" : {"name" : "cow 731", "sex" : "F" }},"88.csv","""Post milking timecourse experiment with lactating Dairy cows.  Comparing 6 hours with 24 hours post milking  Cow 734 vs Cow 731""","Print20",88)
    AgResearchExportMain({ "sampletissue" : "CY5.cow 152 alveolar 6hr post","samplename" : "75ug RNA Trizol only","sampletreatment" : "6hr post milking","samplesubject" : {"name" : "cow 152", "sex" : "F" }},{"sampletissue" : "CY3.cow 703 alveolar 24 hr post","samplename" : "75 ug  RNA Trizol only","sampletreatment" : "24 hr post milking","samplesubject" : {"name" : "cow 703", "sex" : "F" }},"89.csv","""Post milking timecourse experiment with lactating Dairy cows.  Comparing 6 hours with 24 hours post milking  Cow 152 vs Cow 703""","Print20",89)
    AgResearchExportMain({ "sampletissue" : "CY5.cow 742 alveolar 6hr post","samplename" : "75ug RNA Trizol only","sampletreatment" : "6hr post milking","samplesubject" : {"name" : "cow 742", "sex" : "F" }},{"sampletissue" : "CY3.cow 533 alveolar 24 hr post","samplename" : "75 ug  RNA Trizol only","sampletreatment" : "24 hr post milking","samplesubject" : {"name" : "cow 533", "sex" : "F" }},"90.csv","""Post milking timecourse experiment with lactating Dairy cows.  Comparing 6 hours with 24 hours post milking  Cow 742 vs Cow 533""","Print20",90)
    AgResearchExportMain({ "sampletissue" : "CY5.cow 88 alveolar 24hr post","samplename" : "25ug RNA Trizol + RNAeasy","sampletreatment" : "24hr post milking","samplesubject" : {"name" : "cow 88", "sex" : "F" }},{"sampletissue" : "CY3.cow 428 alveolar 6 hr post","samplename" : "25 ug  RNA Trizol +RNAeasy","sampletreatment" : "6hr post milking","samplesubject" : {"name" : "cow 428", "sex" : "F" }},"91.csv","""Post milking timecourse experiment with lactating Dairy cows.  Comparing 6 hours with 24 hours post milking  Cow 88 (24 hr) vs Cow 428 (6 hr).  Reverse dye labels.  (some errors is est assignment)""","Print20",91)
    AgResearchExportMain({ "sampletissue" : "CY5.cow 533 alveolar 24hr post","samplename" : "25ug RNA Trizol + RNAeasy","sampletreatment" : "24hr post milking","samplesubject" : {"name" : "cow 533", "sex" : "F" }},{"sampletissue" : "CY3.cow 742 alveolar 6 hr post","samplename" : "25 ug  RNA Trizol +RNAeasy","sampletreatment" : "6hr post milking","samplesubject" : {"name" : "cow 742", "sex" : "F" }},"92.csv","""Post milking timecourse experiment with lactating Dairy cows.  Comparing 6 hours with 24 hours post milking  Cow 533 (24 hr) vs Cow 742(6 hr).  Reverse dye labels.  (some errors is est assignment)""","Print20",92)
    AgResearchExportMain({ "sampletissue" : "CY5.cow 703 alveolar 24hr post","samplename" : "25ug RNA Trizol + RNAeasy","sampletreatment" : "24hr post milking","samplesubject" : {"name" : "cow 703", "sex" : "F" }},{"sampletissue" : "CY3.cow 152 alveolar 6 hr post","samplename" : "25 ug  RNA Trizol +RNAeasy","sampletreatment" : "6hr post milking","samplesubject" : {"name" : "cow 152", "sex" : "F" }},"95.csv","""Post milking timecourse experiment with lactating Dairy cows.  Comparing 6 hours with 24 hours post milking  Cow 703 (24 hr) vs Cow 152(6 hr).  Reverse dye labels.  (some errors is est assignment)""","Print20",95)
    AgResearchExportMain({ "sampletissue" : "CY5.cow 734 alveolar 6hr post","samplename" : "75ug RNA Trizol + RNAeasy","sampletreatment" : "Standard","samplesubject" : {"name" : "cow 734", "sex" : "F" }},{"sampletissue" : "CY3.cow 731 alveolar 24 hr post","samplename" : "75 ug  RNA Trizol +RNAeasy","sampletreatment" : "Standard","samplesubject" : {"name" : "cow 731", "sex" : "F" }},"102.csv","""Post milking timcourse experiment with lactating Dairy cows.  Comparing 6 hours with 24 hours post milking""","Print20",102)
    AgResearchExportMain({ "sampletissue" : "CY5.cow 742 ","samplename" : "mammary alveolar RNA","sampletreatment" : "6hr post milking","samplesubject" : {"name" : "cow 742", "sex" : "F" }},{"sampletissue" : "CY3.cow 533 ","samplename" : "mammary alveolar RNA","sampletreatment" : "24 hr post milking","samplesubject" : {"name" : "cow 533", "sex" : "F" }},"103.csv","""Post milking timecourse experiment with lactating Dairy cows.  Comparing 6 hours with 24 hours post milking""","Print20",103)
    AgResearchExportMain({ "sampletissue" : "CY5.mammary gland","samplename" : "6 hours","sampletreatment" : "cow #152","samplesubject" : {"name" : "cow 152", "sex" : "F" }},{"sampletissue" : "CY3.mammary gland","samplename" : "24 hours","sampletreatment" : "cow number #703","samplesubject" : {"name" : "cow 703", "sex" : "F" }},"105.csv","""Lactation experiment for the dairy group""","Print20",105)
    AgResearchExportMain({ "sampletissue" : "CY5.mammary gland","samplename" : "6 hours","sampletreatment" : "cow #734","samplesubject" : {"name" : "cow 734", "sex" : "F" }},{"sampletissue" : "CY3.mammary gland","samplename" : "24 hours","sampletreatment" : "cow number #533","samplesubject" : {"name" : "cow 533", "sex" : "F" }},"106.csv","""Lactation experiment for the dairy group""","Print20",106)
    AgResearchExportMain({ "sampletissue" : "CY5.mammary gland","samplename" : "6 hours","sampletreatment" : "cow #742 plus antisense","samplesubject" : {"name" : "cow 742", "sex" : "F" }},{"sampletissue" : "CY3.mammary gland","samplename" : "24 hours","sampletreatment" : "cow number #703 plus antisense","samplesubject" : {"name" : "cow 703", "sex" : "F" }},"108.csv","""Lactation experiment for the dairy group""","Print20",108)
    AgResearchExportMain({ "sampletissue" : "CY5.mammary gland","samplename" : "6 hours","sampletreatment" : "cow #742","samplesubject" : {"name" : "cow 742", "sex" : "F" }},{"sampletissue" : "CY3.mammary gland","samplename" : "24 hours","sampletreatment" : "cow number #703","samplesubject" : {"name" : "cow 703", "sex" : "F" }},"109.csv","""Lactation experiment for the dairy group""","Print20",109)
    AgResearchExportMain({ "sampletissue" : "CY5.mammary gland","samplename" : "6 hours","sampletreatment" : "cow #742","samplesubject" : {"name" : "cow 742", "sex" : "F" }},{"sampletissue" : "CY3.mammary gland","samplename" : "24 hours","sampletreatment" : "cow number #533","samplesubject" : {"name" : "cow 533", "sex" : "F" }},"110.csv","""Lactation experiment for the dairy group""","Print20",110)
    AgResearchExportMain({ "sampletissue" : "CY5.mammary","samplename" : "6 hr post milking","sampletreatment" : "cow 691","samplesubject" : {"name" : "cow 691", "sex" : "F" }},{"sampletissue" : "CY3.mammary","samplename" : "24 hr hr post milking","sampletreatment" : "cow 88","samplesubject" : {"name" : "cow 88", "sex" : "F" }},"127.csv","""Post milking timecourse experiment with lactating Dairy cows.  Comparing 6 hours with 24 hours post milking  Cow 691 vs Cow 88""","Print20",127)
    AgResearchExportMain({ "sampletissue" : "CY5.mammary","samplename" : "6hr post milking","sampletreatment" : "cow 690","samplesubject" : {"name" : "cow 690", "sex" : "F" }},{"sampletissue" : "CY3.mammary","samplename" : "24hr hr post milking","sampletreatment" : "cow 643","samplesubject" : {"name" : "cow 643", "sex" : "F" }},"128.csv","""Post milking timecourse experiment with lactating Dairy cows.  Comparing 6 hours with 24 hours post milking  Cow 690 vs Cow 643""","Print20",128)
    AgResearchExportMain({ "sampletissue" : "CY5.mammary","samplename" : "24hr post milking","sampletreatment" : "cow 533","samplesubject" : {"name" : "cow 533", "sex" : "F" }},{"sampletissue" : "CY3.mammary","samplename" : "6 hr hr post milking","sampletreatment" : "cow 734","samplesubject" : {"name" : "cow 734", "sex" : "F" }},"129.csv","""Post milking timecourse experiment with lactating Dairy cows.  Comparing 6 hours with 24 hours post milking  Cow 734 vs Cow 533""","Print20",129)
    AgResearchExportMain({ "sampletissue" : "CY5.mammary","samplename" : "6 hr post milking","sampletreatment" : "cow 690","samplesubject" : {"name" : "cow 690", "sex" : "F" }},{"sampletissue" : "CY3.mammary","samplename" : "24 hr post milking","sampletreatment" : "cow 576","samplesubject" : {"name" : "cow 576", "sex" : "F" }},"130.csv","""Post milking timecourse experiment with lactating Dairy cows.  Comparing 6 hours with 24 hours post milking  Cow 690 vs Cow 576""","Print20",130)
    AgResearchExportMain({ "sampletissue" : "CY5.mammary","samplename" : "24 hr post milking","sampletreatment" : "cow 643","samplesubject" : {"name" : "cow 643", "sex" : "F" }},{"sampletissue" : "CY3.mammary","samplename" : "6hr hr post milking","sampletreatment" : "cow 691","samplesubject" : {"name" : "cow 691", "sex" : "F" }},"131.csv","""Post milking timecourse experiment with lactating Dairy cows.  Comparing 6 hours with 24 hours post milking  Cow 643 vs Cow 691""","Print20",131)
    AgResearchExportMain({ "sampletissue" : "CY5.mammary","samplename" : "6hr post milking","sampletreatment" : "cow 690 ","samplesubject" : {"name" : "cow 690 ", "sex" : "F" }},{"sampletissue" : "CY3.mammary","samplename" : "24hr post Milking","sampletreatment" : "cow 576 ","samplesubject" : {"name" : "cow 576 ", "sex" : "F" }},"132.csv","""Post milking timecourse experiment with lactating Dairy cows.  Comparing 6 hours with 24 hours post milking. Compare cow 690 6hr post V cow 576 24hr post milking.  ""","Print20",132)
    AgResearchExportMain({ "sampletissue" : "CY5.mammary","samplename" : "24 hr post milking","sampletreatment" : "cow 643","samplesubject" : {"name" : "cow 643", "sex" : "F" }},{"sampletissue" : "CY3.mammary","samplename" : "6hr hr post milking","sampletreatment" : "cow 691","samplesubject" : {"name" : "cow 691", "sex" : "F" }},"133.csv","""Post milking timecourse experiment with lactating Dairy cows.  Comparing 6 hours with 24 hours post milking  Cow 643 vs Cow 691""","Print20",133)
    AgResearchExportMain({ "sampletissue" : "CY5.mammary","samplename" : "6 hr post milking","sampletreatment" : "cow 691","samplesubject" : {"name" : "cow 691", "sex" : "F" }},{"sampletissue" : "CY3.mammary","samplename" : "24 hr post milking","sampletreatment" : "cow 643","samplesubject" : {"name" : "cow 643", "sex" : "F" }},"134.csv","""Post milking timecourse experiment with lactating Dairy cows.  Comparing 6 hours with 24 hours post milking  Cow 691 vs Cow 643""","Print20",134)
    AgResearchExportMain({ "sampletissue" : "CY5.mammary","samplename" : "6hr post milking","sampletreatment" : "cow 428","samplesubject" : {"name" : "cow 428", "sex" : "F" }},{"sampletissue" : "CY3.mammary","samplename" : "24 hr hr post milking","sampletreatment" : "cow 731","samplesubject" : {"name" : "cow 731", "sex" : "F" }},"135.csv","""Post milking timecourse experiment with lactating Dairy cows.  Comparing 6 hours with 24 hours post milking  Cow 428 vs Cow 731""","Print20",135)
    AgResearchExportMain({ "sampletissue" : "CY5.mammary","samplename" : "6 hr post milking","sampletreatment" : "cow 691","samplesubject" : {"name" : "cow 691", "sex" : "F" }},{"sampletissue" : "CY3.mammary","samplename" : "24 hr post milking","sampletreatment" : "cow 643","samplesubject" : {"name" : "cow 643", "sex" : "F" }},"136.csv","""Post milking timecourse experiment with lactating Dairy cows.  Comparing 6 hours with 24 hours post milking  Cow 691 vs Cow 643""","Print20",136)
    AgResearchExportMain({ "sampletissue" : "CY5.mammary","samplename" : "24 hr post milking","sampletreatment" : "cow 731","samplesubject" : {"name" : "cow 731", "sex" : "F" }},{"sampletissue" : "CY3.mammary","samplename" : "6 hr hr post milking","sampletreatment" : "cow 734","samplesubject" : {"name" : "cow 734", "sex" : "F" }},"137.csv","""Post milking timecourse experiment with lactating Dairy cows.  Comparing 6 hours with 24 hours post milking  Cow 734 vs Cow 731""","Print20",137)
    AgResearchExportMain({ "sampletissue" : "CY5.mammary","samplename" : "24 hr post milking","sampletreatment" : "cow 88","samplesubject" : {"name" : "cow 88", "sex" : "F" }},{"sampletissue" : "CY3.mammary","samplename" : "6hr hr post milking","sampletreatment" : "cow 428","samplesubject" : {"name" : "cow 428", "sex" : "F" }},"138.csv","""Post milking timecourse experiment with lactating Dairy cows.  Comparing 6 hours with 24 hours post milking  Cow 428 vs Cow 88""","Print20",138)
    AgResearchExportMain({ "sampletissue" : "CY5.mammary","samplename" : "24hr post milking","sampletreatment" : "cow 88","samplesubject" : {"name" : "cow 88", "sex" : "F" }},{"sampletissue" : "CY3.mammary","samplename" : "6 hr hr post milking","sampletreatment" : "cow 428","samplesubject" : {"name" : "cow 428", "sex" : "F" }},"139.csv","""Post milking timecourse experiment with lactating Dairy cows.  Comparing 6 hours with 24 hours post milking  Cow 428 vs Cow 88""","Print20",139)
    AgResearchExportMain({ "sampletissue" : "CY5.mammary","samplename" : "24 hr post milking","sampletreatment" : "cow 576","samplesubject" : {"name" : "cow 576", "sex" : "F" }},{"sampletissue" : "CY3.mammary","samplename" : "6hr hr post milking","sampletreatment" : "cow 152","samplesubject" : {"name" : "cow 152", "sex" : "F" }},"140.csv","""Post milking timecourse experiment with lactating Dairy cows.  Comparing 6 hours with 24 hours post milking  Cow 152 vs Cow 576""","Print20",140)

    return



    AgResearchArrayMain() #print20
    return

    BlastImportMain()
    return


    # Lisa Fan exps
    # !!! note that the check on name of the GAL file in the GPR files, against the array we 
    # specify here , has been overridden in this import due to the name in the GPR file having
    # an embedded space so that there was a trivial mismatch. It should not normallbe be overridden 
    # like this.
    importParms = {
            'microarraylsid' : "AgResearch.print136 ov 21k.txt",
            'datasourcetype' : "GPRFile",
            'physicalsourcepath' : "/data/databases/flatfile/bfiles/agbrdf/microarray/lisafan",
            'studytype' : 'treated vs untreated microarray',
            'overrideGALNamecheck' : True
    }
    GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"136-19 high 0.95.gpr","""unavailable""",importParms)
    GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"136-19 low 0.96.gpr","""unavailable""",importParms)
    GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"136-20 high 1.00.gpr","""unavailable""",importParms)
    GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"136-20 low 0.98.gpr","""unavailable""",importParms)
    GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"136-20 lower 0.93.gpr","""unavailable""",importParms)
    GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"136-21 high 1.02.gpr","""unavailable""",importParms)
    GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"136-21 low 1.00.gpr","""unavailable""",importParms)
    GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"136-21 lower 0.93.gpr","""unavailable""",importParms)
    GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"136-22 high 1.00.gpr","""unavailable""",importParms)
    GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"136-22 low 0.95.gpr","""unavailable""",importParms)
    GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"136-23 high 0.97.gpr","""unavailable""",importParms)
    GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"136-23 low 1.00.gpr","""unavailable""",importParms)
    GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"136-24 high 0.98.gpr","""unavailable""",importParms)
    GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"136-24 low 0.93.gpr","""unavailable""",importParms)
    GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"136-24 low 1.02.gpr","""unavailable""",importParms)
    GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"136-25 high 1.01.gpr","""unavailable""",importParms)
    GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"136-25 low 0.95.gpr","""unavailable""",importParms)
    GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"136-26 high 0.98.gpr","""unavailable""",importParms)
    GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"136-26 low 0.95.gpr","""unavailable""",importParms)
    return


    # Sam Noel exps
    AgResearchArrayMain()
    return

    importParms = {
            'microarraylsid' : "014850_D_20070207.gal",
            'datasourcetype' : "GPRFile",
            'physicalsourcepath' : "/data/databases/flatfile/bfiles/agbrdf/samnoel",
            'studytype' : 'treated vs untreated microarray',
    }

    #GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"2a high ratio 0.81 pmt 600 R 460 G scan 3.gpr","""unavailable""",importParms)
    #GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"2a high ratio 0.84 pmt 600 R 410 G scan 5.gpr","""unavailable""",importParms)
    #GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"2a  low ratio 0.58 pmt 550R 355 G scan 8.gpr","""unavailable""",importParms)
    #GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"2a  low ratio 1.15 pmt 550R 330 G scan 11.gpr","""unavailable""",importParms)
    #GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"2b high ratio 0.25 595 R 405G.gpr","""unavailable""",importParms)
    GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"2b low ratio 0.4 pmt 550R 340G.gpr","""unavailable""",importParms)
    GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"2c high ratio 0.15 pmt 600R 410G.gpr","""unavailable""",importParms)
    GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"2c Low ratio 0.65 pmt 550R 330G scan 2.gpr","""unavailable""",importParms)
    GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"2d High ratio 0.05 pmt 600R 410G.gpr","""unavailable""",importParms)
    GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"2d low scan ratio 0.31 pmt 550R 330G scan 2.gpr","""unavailable""",importParms)
    GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"2d low scan ratio 25.81 pmt 550R 300G scan 2.gpr","""unavailable""",importParms)
    GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"whole 1 high ratio 1.14 pmt 550R 545 G.gpr","""unavailable""",importParms)
    GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"whole 1 low ratio 0.45 pmt 400R 390 G.gpr","""unavailable""",importParms)
    GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"whole 2 high ratio 3.87 pmt 500R 310G.gpr","""unavailable""",importParms)
    GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"whole 3 high ratio 1.1-1.7 pmt 550R 500G scan 1.gpr","""unavailable""",importParms)
    GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"whole 3 low ratio 1.36 pmt 400R 320G scan 2.gpr","""unavailable""",importParms)
    GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"whole 4 high ratio 1.14 pmt 565R 560G.gpr","""unavailable""",importParms)
    GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"whole 4 low ratio 1.02 pmt 400R 390G.gpr","""unavailable""",importParms)
    GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"whole 5 high ratio 1.07 pmt 520R 570G.gpr","""unavailable""",importParms)
    GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"whole 5 low ratio 1.10 pmt 400R 430G circular features.gpr","""unavailable""",importParms)
    GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"whole 5 low ratio 1.10 pmt 400R 430G.gpr","""unavailable""",importParms)
    GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"whole 6 high ratio 1.14 pmt 546R 550G.gpr","""unavailable""",importParms)
    GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"whole 6 Low  ratio 1.03 pmt 390R400G.gpr","""unavailable""",importParms)
    GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"whole 7 high ratio 1.02 pmt 520R 560G.gpr","""unavailable""",importParms)
    GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"whole 7 low ratio 0.97 pmt 400R 430G.gpr","""unavailable""",importParms)
    GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"whole 8 high ratio 1.06 pmt 510R 550G circular .gpr","""unavailable""",importParms)
    GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"whole 8 high ratio 1.06 pmt 510R 550G.gpr","""unavailable""",importParms)
    GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"whole 8  low ratio 0.98 pmt 380R 410G.gpr","""unavailable""",importParms)


    return




    GALMain()
    return

    AgResearchArrayMain()
    return
    BlastImportMain()
    return

    AffyImportMain(subjectdata={'xreflsid' : 'AFT.Unknown fungal array/ryegrass subject','subjectname' : 'AFT.Unknown fungal array/ryegrass subject','subjectdescription' : 'Dummy subject record, where id of sheep unknown','subjectspeciesname' : 'Fungal/Ryegrass'},\
         sampledata={'xreflsid' : 'AFT.Unknown fungal array/ryegrass sample', 'samplename' : 'AFT.Unknown fungal array/ryegrass subject','sampletissue' : 'unknown','sampletreatment' : 'unknown','sampletype' : 'mRNA extract for microarray experiment'},\
         arraydata={'xreflsid' : 'Affymetrix.Lp19-Lpa530240N (AgResearch Fungal Array)'},\
         filedata={'filename' : 'FL1L-3.csv' , 'physicalsourceuri' : '/data/home/seqstore/agbrdf/fungal/FL1L-3.csv' , 'datasourcetype' : 'CSV from Affy CEL File'},\
         experimentdata={'studytype' : 'treated vs untreated microarray', 'studydescription' : 'unknown'})
    AffyImportMain(subjectdata={'xreflsid' : 'AFT.Unknown fungal array/ryegrass subject','subjectname' : 'AFT.Unknown fungal array/ryegrass subject','subjectdescription' : 'Dummy subject record, where id of sheep unknown','subjectspeciesname' : 'Fungal/Ryegrass'},\
         sampledata={'xreflsid' : 'AFT.Unknown fungal array/ryegrass sample', 'samplename' : 'AFT.Unknown fungal array/ryegrass subject','sampletissue' : 'unknown','sampletreatment' : 'unknown','sampletype' : 'mRNA extract for microarray experiment'},\
         arraydata={'xreflsid' : 'Affymetrix.Lp19-Lpa530240N (AgResearch Fungal Array)'},\
         filedata={'filename' : 'FL1L-5.csv' , 'physicalsourceuri' : '/data/home/seqstore/agbrdf/fungal/FL1L-5.csv' , 'datasourcetype' : 'CSV from Affy CEL File'},\
         experimentdata={'studytype' : 'treated vs untreated microarray', 'studydescription' : 'unknown'})
    AffyImportMain(subjectdata={'xreflsid' : 'AFT.Unknown fungal array/ryegrass subject','subjectname' : 'AFT.Unknown fungal array/ryegrass subject','subjectdescription' : 'Dummy subject record, where id of sheep unknown','subjectspeciesname' : 'Fungal/Ryegrass'},\
         sampledata={'xreflsid' : 'AFT.Unknown fungal array/ryegrass sample', 'samplename' : 'AFT.Unknown fungal array/ryegrass subject','sampletissue' : 'unknown','sampletreatment' : 'unknown','sampletype' : 'mRNA extract for microarray experiment'},\
         arraydata={'xreflsid' : 'Affymetrix.Lp19-Lpa530240N (AgResearch Fungal Array)'},\
         filedata={'filename' : 'FL1L-6.csv' , 'physicalsourceuri' : '/data/home/seqstore/agbrdf/fungal/FL1L-6.csv' , 'datasourcetype' : 'CSV from Affy CEL File'},\
         experimentdata={'studytype' : 'treated vs untreated microarray', 'studydescription' : 'unknown'})
    return









    BlastImportMain()
    return


    AffyImportMain(subjectdata={'xreflsid' : 'AFT.Unknown fungal array/ryegrass subject','subjectname' : 'AFT.Unknown fungal array/ryegrass subject','subjectdescription' : 'Dummy subject record, where id of sheep unknown','subjectspeciesname' : 'Fungal/Ryegrass'},\
         sampledata={'xreflsid' : 'AFT.Unknown fungal array/ryegrass sample', 'samplename' : 'AFT.Unknown fungal array/ryegrass subject','sampletissue' : 'unknown','sampletreatment' : 'unknown','sampletype' : 'mRNA extract for microarray experiment'},\
         arraydata={'xreflsid' : 'Affymetrix.Lp19-Lpa530240N (AgResearch Fungal Array)'},\
         filedata={'filename' : 'FLIF-2.csv' , 'physicalsourceuri' : '/data/home/seqstore/agbrdf/fungal/FLIF-2.csv' , 'datasourcetype' : 'CSV from Affy CEL File'},\
         experimentdata={'studytype' : 'treated vs untreated microarray', 'studydescription' : 'unknown'})    
    AffyImportMain(subjectdata={'xreflsid' : 'AFT.Unknown fungal array/ryegrass subject','subjectname' : 'AFT.Unknown fungal array/ryegrass subject','subjectdescription' : 'Dummy subject record, where id of sheep unknown','subjectspeciesname' : 'Fungal/Ryegrass'},\
         sampledata={'xreflsid' : 'AFT.Unknown fungal array/ryegrass sample', 'samplename' : 'AFT.Unknown fungal array/ryegrass subject','sampletissue' : 'unknown','sampletreatment' : 'unknown','sampletype' : 'mRNA extract for microarray experiment'},\
         arraydata={'xreflsid' : 'Affymetrix.Lp19-Lpa530240N (AgResearch Fungal Array)'},\
         filedata={'filename' : 'FLIF-3.csv' , 'physicalsourceuri' : '/data/home/seqstore/agbrdf/fungal/FLIF-3.csv' , 'datasourcetype' : 'CSV from Affy CEL File'},\
         experimentdata={'studytype' : 'treated vs untreated microarray', 'studydescription' : 'unknown'})    
    AffyImportMain(subjectdata={'xreflsid' : 'AFT.Unknown fungal array/ryegrass subject','subjectname' : 'AFT.Unknown fungal array/ryegrass subject','subjectdescription' : 'Dummy subject record, where id of sheep unknown','subjectspeciesname' : 'Fungal/Ryegrass'},\
         sampledata={'xreflsid' : 'AFT.Unknown fungal array/ryegrass sample', 'samplename' : 'AFT.Unknown fungal array/ryegrass subject','sampletissue' : 'unknown','sampletreatment' : 'unknown','sampletype' : 'mRNA extract for microarray experiment'},\
         arraydata={'xreflsid' : 'Affymetrix.Lp19-Lpa530240N (AgResearch Fungal Array)'},\
         filedata={'filename' : 'LP19F-1.csv' , 'physicalsourceuri' : '/data/home/seqstore/agbrdf/fungal/LP19F-1.csv' , 'datasourcetype' : 'CSV from Affy CEL File'},\
         experimentdata={'studytype' : 'treated vs untreated microarray', 'studydescription' : 'unknown'})    
    AffyImportMain(subjectdata={'xreflsid' : 'AFT.Unknown fungal array/ryegrass subject','subjectname' : 'AFT.Unknown fungal array/ryegrass subject','subjectdescription' : 'Dummy subject record, where id of sheep unknown','subjectspeciesname' : 'Fungal/Ryegrass'},\
         sampledata={'xreflsid' : 'AFT.Unknown fungal array/ryegrass sample', 'samplename' : 'AFT.Unknown fungal array/ryegrass subject','sampletissue' : 'unknown','sampletreatment' : 'unknown','sampletype' : 'mRNA extract for microarray experiment'},\
         arraydata={'xreflsid' : 'Affymetrix.Lp19-Lpa530240N (AgResearch Fungal Array)'},\
         filedata={'filename' : 'LP19F-2.csv' , 'physicalsourceuri' : '/data/home/seqstore/agbrdf/fungal/LP19F-2.csv' , 'datasourcetype' : 'CSV from Affy CEL File'},\
         experimentdata={'studytype' : 'treated vs untreated microarray', 'studydescription' : 'unknown'})    
    AffyImportMain(subjectdata={'xreflsid' : 'AFT.Unknown fungal array/ryegrass subject','subjectname' : 'AFT.Unknown fungal array/ryegrass subject','subjectdescription' : 'Dummy subject record, where id of sheep unknown','subjectspeciesname' : 'Fungal/Ryegrass'},\
         sampledata={'xreflsid' : 'AFT.Unknown fungal array/ryegrass sample', 'samplename' : 'AFT.Unknown fungal array/ryegrass subject','sampletissue' : 'unknown','sampletreatment' : 'unknown','sampletype' : 'mRNA extract for microarray experiment'},\
         arraydata={'xreflsid' : 'Affymetrix.Lp19-Lpa530240N (AgResearch Fungal Array)'},\
         filedata={'filename' : 'LP19F-3.csv' , 'physicalsourceuri' : '/data/home/seqstore/agbrdf/fungal/LP19F-3.csv' , 'datasourcetype' : 'CSV from Affy CEL File'},\
         experimentdata={'studytype' : 'treated vs untreated microarray', 'studydescription' : 'unknown'})    
    return























    #AffyImportMain(subjectdata={'xreflsid' : 'AFT.Unknown fungal array/ryegrass subject','subjectname' : 'AFT.Unknown fungal array/ryegrass subject','subjectdescription' : 'Dummy subject record, where id of sheep unknown','subjectspeciesname' : 'Fungal/Ryegrass'},\
    #     sampledata={'xreflsid' : 'AFT.Unknown fungal array/ryegrass sample', 'samplename' : 'AFT.Unknown fungal array/ryegrass subject','sampletissue' : 'unknown','sampletreatment' : 'unknown','sampletype' : 'mRNA extract for microarray experiment'},\
    #     arraydata={'xreflsid' : 'Affymetrix.Lp19-Lpa530240N (AgResearch Fungal Array)'},\
    #     filedata={'filename' : '54-1.csv' , 'physicalsourceuri' : '/data/home/seqstore/agbrdf/fungal/54-1.csv' , 'datasourcetype' : 'CSV from Affy CEL File'},\
    #     experimentdata={'studytype' : 'treated vs untreated microarray', 'studydescription' : 'unknown'})


    AffyImportMain(subjectdata={'xreflsid' : 'AFT.Unknown fungal array/ryegrass subject','subjectname' : 'AFT.Unknown fungal array/ryegrass subject','subjectdescription' : 'Dummy subject record, where id of sheep unknown','subjectspeciesname' : 'Fungal/Ryegrass'},\
         sampledata={'xreflsid' : 'AFT.Unknown fungal array/ryegrass sample', 'samplename' : 'AFT.Unknown fungal array/ryegrass subject','sampletissue' : 'unknown','sampletreatment' : 'unknown','sampletype' : 'mRNA extract for microarray experiment'},\
         arraydata={'xreflsid' : 'Affymetrix.Lp19-Lpa530240N (AgResearch Fungal Array)'},\
         filedata={'filename' : '54-4.csv' , 'physicalsourceuri' : '/data/home/seqstore/agbrdf/fungal/54-4.csv' , 'datasourcetype' : 'CSV from Affy CEL File'},\
         experimentdata={'studytype' : 'treated vs untreated microarray', 'studydescription' : 'unknown'})    


    AffyImportMain(subjectdata={'xreflsid' : 'AFT.Unknown fungal array/ryegrass subject','subjectname' : 'AFT.Unknown fungal array/ryegrass subject','subjectdescription' : 'Dummy subject record, where id of sheep unknown','subjectspeciesname' : 'Fungal/Ryegrass'},\
         sampledata={'xreflsid' : 'AFT.Unknown fungal array/ryegrass sample', 'samplename' : 'AFT.Unknown fungal array/ryegrass subject','sampletissue' : 'unknown','sampletreatment' : 'unknown','sampletype' : 'mRNA extract for microarray experiment'},\
         arraydata={'xreflsid' : 'Affymetrix.Lp19-Lpa530240N (AgResearch Fungal Array)'},\
         filedata={'filename' : 'FLIF-1.csv' , 'physicalsourceuri' : '/data/home/seqstore/agbrdf/fungal/FLIF-1.csv' , 'datasourcetype' : 'CSV from Affy CEL File'},\
         experimentdata={'studytype' : 'treated vs untreated microarray', 'studydescription' : 'unknown'})    
    AffyImportMain(subjectdata={'xreflsid' : 'AFT.Unknown fungal array/ryegrass subject','subjectname' : 'AFT.Unknown fungal array/ryegrass subject','subjectdescription' : 'Dummy subject record, where id of sheep unknown','subjectspeciesname' : 'Fungal/Ryegrass'},\
         sampledata={'xreflsid' : 'AFT.Unknown fungal array/ryegrass sample', 'samplename' : 'AFT.Unknown fungal array/ryegrass subject','sampletissue' : 'unknown','sampletreatment' : 'unknown','sampletype' : 'mRNA extract for microarray experiment'},\
         arraydata={'xreflsid' : 'Affymetrix.Lp19-Lpa530240N (AgResearch Fungal Array)'},\
         filedata={'filename' : 'NC25KO-1.csv' , 'physicalsourceuri' : '/data/home/seqstore/agbrdf/fungal/NC25KO-1.csv' , 'datasourcetype' : 'CSV from Affy CEL File'},\
         experimentdata={'studytype' : 'treated vs untreated microarray', 'studydescription' : 'unknown'})    
    AffyImportMain(subjectdata={'xreflsid' : 'AFT.Unknown fungal array/ryegrass subject','subjectname' : 'AFT.Unknown fungal array/ryegrass subject','subjectdescription' : 'Dummy subject record, where id of sheep unknown','subjectspeciesname' : 'Fungal/Ryegrass'},\
         sampledata={'xreflsid' : 'AFT.Unknown fungal array/ryegrass sample', 'samplename' : 'AFT.Unknown fungal array/ryegrass subject','sampletissue' : 'unknown','sampletreatment' : 'unknown','sampletype' : 'mRNA extract for microarray experiment'},\
         arraydata={'xreflsid' : 'Affymetrix.Lp19-Lpa530240N (AgResearch Fungal Array)'},\
         filedata={'filename' : 'NC25KO-2.csv' , 'physicalsourceuri' : '/data/home/seqstore/agbrdf/fungal/NC25KO-2.csv' , 'datasourcetype' : 'CSV from Affy CEL File'},\
         experimentdata={'studytype' : 'treated vs untreated microarray', 'studydescription' : 'unknown'})    
    AffyImportMain(subjectdata={'xreflsid' : 'AFT.Unknown fungal array/ryegrass subject','subjectname' : 'AFT.Unknown fungal array/ryegrass subject','subjectdescription' : 'Dummy subject record, where id of sheep unknown','subjectspeciesname' : 'Fungal/Ryegrass'},\
         sampledata={'xreflsid' : 'AFT.Unknown fungal array/ryegrass sample', 'samplename' : 'AFT.Unknown fungal array/ryegrass subject','sampletissue' : 'unknown','sampletreatment' : 'unknown','sampletype' : 'mRNA extract for microarray experiment'},\
         arraydata={'xreflsid' : 'Affymetrix.Lp19-Lpa530240N (AgResearch Fungal Array)'},\
         filedata={'filename' : 'NC25KO-3.csv' , 'physicalsourceuri' : '/data/home/seqstore/agbrdf/fungal/NC25KO-3.csv' , 'datasourcetype' : 'CSV from Affy CEL File'},\
         experimentdata={'studytype' : 'treated vs untreated microarray', 'studydescription' : 'unknown'})    

    AffyImportMain(subjectdata={'xreflsid' : 'AFT.Unknown fungal array/ryegrass subject','subjectname' : 'AFT.Unknown fungal array/ryegrass subject','subjectdescription' : 'Dummy subject record, where id of sheep unknown','subjectspeciesname' : 'Fungal/Ryegrass'},\
         sampledata={'xreflsid' : 'AFT.Unknown fungal array/ryegrass sample', 'samplename' : 'AFT.Unknown fungal array/ryegrass subject','sampletissue' : 'unknown','sampletreatment' : 'unknown','sampletype' : 'mRNA extract for microarray experiment'},\
         arraydata={'xreflsid' : 'Affymetrix.Lp19-Lpa530240N (AgResearch Fungal Array)'},\
         filedata={'filename' : 'LP19L-2.csv' , 'physicalsourceuri' : '/data/home/seqstore/agbrdf/fungal/LP19L-2.csv' , 'datasourcetype' : 'CSV from Affy CEL File'},\
         experimentdata={'studytype' : 'treated vs untreated microarray', 'studydescription' : 'unknown'})    

    AffyImportMain(subjectdata={'xreflsid' : 'AFT.Unknown fungal array/ryegrass subject','subjectname' : 'AFT.Unknown fungal array/ryegrass subject','subjectdescription' : 'Dummy subject record, where id of sheep unknown','subjectspeciesname' : 'Fungal/Ryegrass'},\
         sampledata={'xreflsid' : 'AFT.Unknown fungal array/ryegrass sample', 'samplename' : 'AFT.Unknown fungal array/ryegrass subject','sampletissue' : 'unknown','sampletreatment' : 'unknown','sampletype' : 'mRNA extract for microarray experiment'},\
         arraydata={'xreflsid' : 'Affymetrix.Lp19-Lpa530240N (AgResearch Fungal Array)'},\
         filedata={'filename' : 'LP19L-3.csv' , 'physicalsourceuri' : '/data/home/seqstore/agbrdf/fungal/LP19L-3.csv' , 'datasourcetype' : 'CSV from Affy CEL File'},\
         experimentdata={'studytype' : 'treated vs untreated microarray', 'studydescription' : 'unknown'})    
    AffyImportMain(subjectdata={'xreflsid' : 'AFT.Unknown fungal array/ryegrass subject','subjectname' : 'AFT.Unknown fungal array/ryegrass subject','subjectdescription' : 'Dummy subject record, where id of sheep unknown','subjectspeciesname' : 'Fungal/Ryegrass'},\
         sampledata={'xreflsid' : 'AFT.Unknown fungal array/ryegrass sample', 'samplename' : 'AFT.Unknown fungal array/ryegrass subject','sampletissue' : 'unknown','sampletreatment' : 'unknown','sampletype' : 'mRNA extract for microarray experiment'},\
         arraydata={'xreflsid' : 'Affymetrix.Lp19-Lpa530240N (AgResearch Fungal Array)'},\
         filedata={'filename' : 'LP19L-5.csv' , 'physicalsourceuri' : '/data/home/seqstore/agbrdf/fungal/LP19L-5.csv' , 'datasourcetype' : 'CSV from Affy CEL File'},\
         experimentdata={'studytype' : 'treated vs untreated microarray', 'studydescription' : 'unknown'})    
    AffyImportMain(subjectdata={'xreflsid' : 'AFT.Unknown fungal array/ryegrass subject','subjectname' : 'AFT.Unknown fungal array/ryegrass subject','subjectdescription' : 'Dummy subject record, where id of sheep unknown','subjectspeciesname' : 'Fungal/Ryegrass'},\
         sampledata={'xreflsid' : 'AFT.Unknown fungal array/ryegrass sample', 'samplename' : 'AFT.Unknown fungal array/ryegrass subject','sampletissue' : 'unknown','sampletreatment' : 'unknown','sampletype' : 'mRNA extract for microarray experiment'},\
         arraydata={'xreflsid' : 'Affymetrix.Lp19-Lpa530240N (AgResearch Fungal Array)'},\
         filedata={'filename' : 'G9-6.csv' , 'physicalsourceuri' : '/data/home/seqstore/agbrdf/fungal/G9-6.csv' , 'datasourcetype' : 'CSV from Affy CEL File'},\
         experimentdata={'studytype' : 'treated vs untreated microarray', 'studydescription' : 'unknown'})    
    AffyImportMain(subjectdata={'xreflsid' : 'AFT.Unknown fungal array/ryegrass subject','subjectname' : 'AFT.Unknown fungal array/ryegrass subject','subjectdescription' : 'Dummy subject record, where id of sheep unknown','subjectspeciesname' : 'Fungal/Ryegrass'},\
         sampledata={'xreflsid' : 'AFT.Unknown fungal array/ryegrass sample', 'samplename' : 'AFT.Unknown fungal array/ryegrass subject','sampletissue' : 'unknown','sampletreatment' : 'unknown','sampletype' : 'mRNA extract for microarray experiment'},\
         arraydata={'xreflsid' : 'Affymetrix.Lp19-Lpa530240N (AgResearch Fungal Array)'},\
         filedata={'filename' : 'G9-4.csv' , 'physicalsourceuri' : '/data/home/seqstore/agbrdf/fungal/G9-4.csv' , 'datasourcetype' : 'CSV from Affy CEL File'},\
         experimentdata={'studytype' : 'treated vs untreated microarray', 'studydescription' : 'unknown'})    
    AffyImportMain(subjectdata={'xreflsid' : 'AFT.Unknown fungal array/ryegrass subject','subjectname' : 'AFT.Unknown fungal array/ryegrass subject','subjectdescription' : 'Dummy subject record, where id of sheep unknown','subjectspeciesname' : 'Fungal/Ryegrass'},\
         sampledata={'xreflsid' : 'AFT.Unknown fungal array/ryegrass sample', 'samplename' : 'AFT.Unknown fungal array/ryegrass subject','sampletissue' : 'unknown','sampletreatment' : 'unknown','sampletype' : 'mRNA extract for microarray experiment'},\
         arraydata={'xreflsid' : 'Affymetrix.Lp19-Lpa530240N (AgResearch Fungal Array)'},\
         filedata={'filename' : 'G9-3.csv' , 'physicalsourceuri' : '/data/home/seqstore/agbrdf/fungal/G9-3.csv' , 'datasourcetype' : 'CSV from Affy CEL File'},\
         experimentdata={'studytype' : 'treated vs untreated microarray', 'studydescription' : 'unknown'})    

    AffyImportMain(subjectdata={'xreflsid' : 'AFT.Unknown fungal array/ryegrass subject','subjectname' : 'AFT.Unknown fungal array/ryegrass subject','subjectdescription' : 'Dummy subject record, where id of sheep unknown','subjectspeciesname' : 'Fungal/Ryegrass'},\
         sampledata={'xreflsid' : 'AFT.Unknown fungal array/ryegrass sample', 'samplename' : 'AFT.Unknown fungal array/ryegrass subject','sampletissue' : 'unknown','sampletreatment' : 'unknown','sampletype' : 'mRNA extract for microarray experiment'},\
         arraydata={'xreflsid' : 'Affymetrix.Lp19-Lpa530240N (AgResearch Fungal Array)'},\
         filedata={'filename' : 'FL1-T-3.csv' , 'physicalsourceuri' : '/data/home/seqstore/agbrdf/fungal/FL1-T-3.csv' , 'datasourcetype' : 'CSV from Affy CEL File'},\
         experimentdata={'studytype' : 'treated vs untreated microarray', 'studydescription' : 'unknown'})    
    AffyImportMain(subjectdata={'xreflsid' : 'AFT.Unknown fungal array/ryegrass subject','subjectname' : 'AFT.Unknown fungal array/ryegrass subject','subjectdescription' : 'Dummy subject record, where id of sheep unknown','subjectspeciesname' : 'Fungal/Ryegrass'},\
         sampledata={'xreflsid' : 'AFT.Unknown fungal array/ryegrass sample', 'samplename' : 'AFT.Unknown fungal array/ryegrass subject','sampletissue' : 'unknown','sampletreatment' : 'unknown','sampletype' : 'mRNA extract for microarray experiment'},\
         arraydata={'xreflsid' : 'Affymetrix.Lp19-Lpa530240N (AgResearch Fungal Array)'},\
         filedata={'filename' : 'FL1-T-4.csv' , 'physicalsourceuri' : '/data/home/seqstore/agbrdf/fungal/FL1-T-4.csv' , 'datasourcetype' : 'CSV from Affy CEL File'},\
         experimentdata={'studytype' : 'treated vs untreated microarray', 'studydescription' : 'unknown'})    
    AffyImportMain(subjectdata={'xreflsid' : 'AFT.Unknown fungal array/ryegrass subject','subjectname' : 'AFT.Unknown fungal array/ryegrass subject','subjectdescription' : 'Dummy subject record, where id of sheep unknown','subjectspeciesname' : 'Fungal/Ryegrass'},\
         sampledata={'xreflsid' : 'AFT.Unknown fungal array/ryegrass sample', 'samplename' : 'AFT.Unknown fungal array/ryegrass subject','sampletissue' : 'unknown','sampletreatment' : 'unknown','sampletype' : 'mRNA extract for microarray experiment'},\
         arraydata={'xreflsid' : 'Affymetrix.Lp19-Lpa530240N (AgResearch Fungal Array)'},\
         filedata={'filename' : 'FL1-T-6.csv' , 'physicalsourceuri' : '/data/home/seqstore/agbrdf/fungal/FL1-T-6.csv' , 'datasourcetype' : 'CSV from Affy CEL File'},\
         experimentdata={'studytype' : 'treated vs untreated microarray', 'studydescription' : 'unknown'})    

    AffyImportMain(subjectdata={'xreflsid' : 'AFT.Unknown fungal array/ryegrass subject','subjectname' : 'AFT.Unknown fungal array/ryegrass subject','subjectdescription' : 'Dummy subject record, where id of sheep unknown','subjectspeciesname' : 'Fungal/Ryegrass'},\
         sampledata={'xreflsid' : 'AFT.Unknown fungal array/ryegrass sample', 'samplename' : 'AFT.Unknown fungal array/ryegrass subject','sampletissue' : 'unknown','sampletreatment' : 'unknown','sampletype' : 'mRNA extract for microarray experiment'},\
         arraydata={'xreflsid' : 'Affymetrix.Lp19-Lpa530240N (AgResearch Fungal Array)'},\
         filedata={'filename' : 'E-RG-1.csv' , 'physicalsourceuri' : '/data/home/seqstore/agbrdf/fungal/E-RG-1.csv' , 'datasourcetype' : 'CSV from Affy CEL File'},\
         experimentdata={'studytype' : 'treated vs untreated microarray', 'studydescription' : 'unknown'})    
    AffyImportMain(subjectdata={'xreflsid' : 'AFT.Unknown fungal array/ryegrass subject','subjectname' : 'AFT.Unknown fungal array/ryegrass subject','subjectdescription' : 'Dummy subject record, where id of sheep unknown','subjectspeciesname' : 'Fungal/Ryegrass'},\
         sampledata={'xreflsid' : 'AFT.Unknown fungal array/ryegrass sample', 'samplename' : 'AFT.Unknown fungal array/ryegrass subject','sampletissue' : 'unknown','sampletreatment' : 'unknown','sampletype' : 'mRNA extract for microarray experiment'},\
         arraydata={'xreflsid' : 'Affymetrix.Lp19-Lpa530240N (AgResearch Fungal Array)'},\
         filedata={'filename' : 'E-RG-4.csv' , 'physicalsourceuri' : '/data/home/seqstore/agbrdf/fungal/E-RG-4.csv' , 'datasourcetype' : 'CSV from Affy CEL File'},\
         experimentdata={'studytype' : 'treated vs untreated microarray', 'studydescription' : 'unknown'})    
    AffyImportMain(subjectdata={'xreflsid' : 'AFT.Unknown fungal array/ryegrass subject','subjectname' : 'AFT.Unknown fungal array/ryegrass subject','subjectdescription' : 'Dummy subject record, where id of sheep unknown','subjectspeciesname' : 'Fungal/Ryegrass'},\
         sampledata={'xreflsid' : 'AFT.Unknown fungal array/ryegrass sample', 'samplename' : 'AFT.Unknown fungal array/ryegrass subject','sampletissue' : 'unknown','sampletreatment' : 'unknown','sampletype' : 'mRNA extract for microarray experiment'},\
         arraydata={'xreflsid' : 'Affymetrix.Lp19-Lpa530240N (AgResearch Fungal Array)'},\
         filedata={'filename' : 'E-RG-5.csv' , 'physicalsourceuri' : '/data/home/seqstore/agbrdf/fungal/E-RG-5.csv' , 'datasourcetype' : 'CSV from Affy CEL File'},\
         experimentdata={'studytype' : 'treated vs untreated microarray', 'studydescription' : 'unknown'})    

    AffyImportMain(subjectdata={'xreflsid' : 'AFT.Unknown fungal array/ryegrass subject','subjectname' : 'AFT.Unknown fungal array/ryegrass subject','subjectdescription' : 'Dummy subject record, where id of sheep unknown','subjectspeciesname' : 'Fungal/Ryegrass'},\
         sampledata={'xreflsid' : 'AFT.Unknown fungal array/ryegrass sample', 'samplename' : 'AFT.Unknown fungal array/ryegrass subject','sampletissue' : 'unknown','sampletreatment' : 'unknown','sampletype' : 'mRNA extract for microarray experiment'},\
         arraydata={'xreflsid' : 'Affymetrix.Lp19-Lpa530240N (AgResearch Fungal Array)'},\
         filedata={'filename' : '54-5.csv' , 'physicalsourceuri' : '/data/home/seqstore/agbrdf/fungal/54-5.csv' , 'datasourcetype' : 'CSV from Affy CEL File'},\
         experimentdata={'studytype' : 'treated vs untreated microarray', 'studydescription' : 'unknown'})    
    AffyImportMain(subjectdata={'xreflsid' : 'AFT.Unknown fungal array/ryegrass subject','subjectname' : 'AFT.Unknown fungal array/ryegrass subject','subjectdescription' : 'Dummy subject record, where id of sheep unknown','subjectspeciesname' : 'Fungal/Ryegrass'},\
         sampledata={'xreflsid' : 'AFT.Unknown fungal array/ryegrass sample', 'samplename' : 'AFT.Unknown fungal array/ryegrass subject','sampletissue' : 'unknown','sampletreatment' : 'unknown','sampletype' : 'mRNA extract for microarray experiment'},\
         arraydata={'xreflsid' : 'Affymetrix.Lp19-Lpa530240N (AgResearch Fungal Array)'},\
         filedata={'filename' : 'ACKO42-1.csv' , 'physicalsourceuri' : '/data/home/seqstore/agbrdf/fungal/ACKO42-1.csv' , 'datasourcetype' : 'CSV from Affy CEL File'},\
         experimentdata={'studytype' : 'treated vs untreated microarray', 'studydescription' : 'unknown'})    
    AffyImportMain(subjectdata={'xreflsid' : 'AFT.Unknown fungal array/ryegrass subject','subjectname' : 'AFT.Unknown fungal array/ryegrass subject','subjectdescription' : 'Dummy subject record, where id of sheep unknown','subjectspeciesname' : 'Fungal/Ryegrass'},\
         sampledata={'xreflsid' : 'AFT.Unknown fungal array/ryegrass sample', 'samplename' : 'AFT.Unknown fungal array/ryegrass subject','sampletissue' : 'unknown','sampletreatment' : 'unknown','sampletype' : 'mRNA extract for microarray experiment'},\
         arraydata={'xreflsid' : 'Affymetrix.Lp19-Lpa530240N (AgResearch Fungal Array)'},\
         filedata={'filename' : 'ACKO42-4.csv' , 'physicalsourceuri' : '/data/home/seqstore/agbrdf/fungal/ACKO42-4.csv' , 'datasourcetype' : 'CSV from Affy CEL File'},\
         experimentdata={'studytype' : 'treated vs untreated microarray', 'studydescription' : 'unknown'})    
    AffyImportMain(subjectdata={'xreflsid' : 'AFT.Unknown fungal array/ryegrass subject','subjectname' : 'AFT.Unknown fungal array/ryegrass subject','subjectdescription' : 'Dummy subject record, where id of sheep unknown','subjectspeciesname' : 'Fungal/Ryegrass'},\
         sampledata={'xreflsid' : 'AFT.Unknown fungal array/ryegrass sample', 'samplename' : 'AFT.Unknown fungal array/ryegrass subject','sampletissue' : 'unknown','sampletreatment' : 'unknown','sampletype' : 'mRNA extract for microarray experiment'},\
         arraydata={'xreflsid' : 'Affymetrix.Lp19-Lpa530240N (AgResearch Fungal Array)'},\
         filedata={'filename' : 'ACKO42-5.csv' , 'physicalsourceuri' : '/data/home/seqstore/agbrdf/fungal/ACKO42-5.csv' , 'datasourcetype' : 'CSV from Affy CEL File'},\
         experimentdata={'studytype' : 'treated vs untreated microarray', 'studydescription' : 'unknown'})    


    return


    #GALMain()
    #return
    importParms = {
            'microarraylsid' : "Print 120 CPROT 17K.txt",
            'datasourcetype' : "GPRFile",
            'physicalsourcepath' : "/home/seqstore/agbrdf/zaneta",
            'studytype' : 'treated vs untreated microarray',
    }

    #GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"s1a-w1b_highest (line to ave 2).gpr","""unavailable""",importParms)
    #GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"s1a-w1b_high (line to ave 2).gpr","""unavailable""",importParms)
    #GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"s1a-w1b_low (line to ave 2).gpr","""unavailable""",importParms)
    #GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"s1a-w1b_medium (line to ave 2).gpr","""unavailable""",importParms)
    #GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"s2a-w2b_highest (line to ave 2).gpr","""unavailable""",importParms)
    #GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"s2a-w2b_high (line to ave 2).gpr","""unavailable""",importParms)
    #GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"s2a-w2b_low (line to ave 2).gpr","""unavailable""",importParms)
    #GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"s2a-w2b_medium (line to ave 2).gpr","""unavailable""",importParms)
    #GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"s3a-w3b_highest (line to ave 2).gpr","""unavailable""",importParms)
    #GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"s3a-w3b_high (line to ave 2).gpr","""unavailable""",importParms)
    #GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"s3a-w3b_low (line to ave 2).gpr","""unavailable""",importParms)
    #GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"s3a-w3b_medium (line to ave 2).gpr","""unavailable""",importParms)
    #GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"w1a-s1b_(line to ave 2).gpr","""unavailable""",importParms)
    #GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"w2a-s2b_high (bad flaged).gpr","""unavailable""",importParms)
    #GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"w2a-s2b_highest (bad flag).gpr","""unavailable""",importParms)
    #GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"w2a-s2b_highest (no bad flag).gpr","""unavailable""",importParms)
    #GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"w2a-s2b_high (no bad flag).gpr","""unavailable""",importParms)
    #GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"w2a-s2b_low (bad flag).gpr","""unavailable""",importParms)
    #GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"w2a-s2b_low (no bad flag).gpr","""unavailable""",importParms)
    #GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"w2a-s2b_medium (bad flagged).gpr","""unavailable""",importParms)
    #GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"w2a-s2b_medium (no bad flagged).gpr","""unavailable""",importParms)
    #GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"w3a-s3b_highest (line to ave 2).gpr","""unavailable""",importParms)
    #GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"w3a-s3b_high.gpr","""unavailable""",importParms)
    #GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"w3a-s3b_low (line to ave 2).gpr","""unavailable""",importParms)
    #GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"w3a-s3b_medium.gpr","""unavailable""",importParms)

    #AgResearchArrayMain()
    #return

    #myform = AgResearchSequenceSubmissionForm(argDict)
    #myform.processData()

    #importParms = {
    #        'microarraylsid' : "AgResearch.print136 ov 21k.txt",
    #        'datasourcetype' : "GPRFile",
    #        'physicalsourcepath' : "/home/seqstore/agbrdf/lisa",
    #        'studytype' : 'treated vs untreated microarray',
    #}
    #GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"136-10 high.gpr","""unavailable""",importParms)
    #GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"136-10 low.gpr","""unavailable""",importParms)
    #GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"136-11 high.gpr","""unavailable""",importParms)
    #GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"136-11 low.gpr","""unavailable""",importParms)
    #GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"136-12 high.gpr","""unavailable""",importParms)
    #GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"136-12 low.gpr","""unavailable""",importParms)
    #GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"136-13 high.gpr","""unavailable""",importParms)
    #GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"136-13 low.gpr","""unavailable""",importParms)
    #GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"136-14 high.gpr","""unavailable""",importParms)
    #GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"136-14 low.gpr","""unavailable""",importParms)
    #GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"136-15 high.gpr","""unavailable""",importParms)
    #GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"136-15 low.gpr","""unavailable""",importParms)
    #GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"136-16 high.gpr","""unavailable""",importParms)
    #GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"136-16 low.gpr","""unavailable""",importParms)
    #GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"136-17 high.gpr","""unavailable""",importParms)
    #GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"136-17 low.gpr","""unavailable""",importParms)
    #GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"136-18 high.gpr","""unavailable""",importParms)
    #GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"136-18 low.gpr","""unavailable""",importParms)
    #GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"136-1 high.gpr","""unavailable""",importParms)
    #GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"136-1 low.gpr","""unavailable""",importParms)
    #GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"136-2 high.gpr","""unavailable""",importParms)
    #GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"136-2 low.gpr","""unavailable""",importParms)
    #GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"136-4 high 0.98.gpr","""unavailable""",importParms)
    #GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"136-4 low2.gpr","""unavailable""",importParms)
    #GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"136-5 high.gpr","""unavailable""",importParms)
    #GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"136-5 low.gpr","""unavailable""",importParms)
    #GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"136-6 high.gpr","""unavailable""",importParms)
    #GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"136-6 low.gpr","""unavailable""",importParms)
    #GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"136-7 high.gpr","""unavailable""",importParms)
    #GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"136-7 low 0.95.gpr","""unavailable""",importParms)
    #GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"136-8 high.gpr","""unavailable""",importParms)
    #GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"136-8 low.gpr","""unavailable""",importParms)
    #GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"136-9 high.gpr","""unavailable""",importParms)
    #GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"136-9 low.gpr","""unavailable""",importParms)
    #GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"136-3 low.gpr","""unavailable""",importParms)
    #GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"136-3 high redone.gpr","""unavailable""",importParms)
    importParms = {
            'microarraylsid' : "AgResearch.print 132 Bov20K.txt",
            'datasourcetype' : "GPRFile",
            'physicalsourcepath' : "/home/seqstore/agbrdf/sue/muscle032007",
            'studytype' : 'treated vs untreated microarray',
    }
    #GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"2007-01-12 T72 Slide 4 Low.gpr","""unavailable""",importParms)
    #GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"2007-01-12-T72 Slide 6 Low.gpr","""unavailable""",importParms)
    #GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"2007-01-15 Slide 5 Low Scan final.gpr","""unavailable""",importParms)
    #GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"2007-01-15-T72 Slide 1 Low.gpr","""unavailable""",importParms)
    #GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"2007-01-15-T72 Slide 2 Low.gpr","""unavailable""",importParms)
    #GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"2007-01-15-T72 Slide 3 Low Scan.gpr","""unavailable""",importParms)
    #GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"2007-01-16 T72 Slide 9 Low(2) Final.gpr","""unavailable""",importParms)
    #GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"2007-01-17 ST72 Slide 7 Low.gpr","""unavailable""",importParms)
    #GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"2007-01-17 T72 Slide 10 Low Final(2).gpr","""unavailable""",importParms)
    #GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"2007-01-17 T72 Slide 11 Low.gpr","""unavailable""",importParms)
    #GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"2007-01-17-T72 Slide 12 Low.gpr","""unavailable""",importParms)
    #GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"2007-01-17 T72 Slide 8 Low.gpr","""unavailable""",importParms)
    #GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"2007-01-18 T72 Slide 17 Low Final.gpr","""unavailable""",importParms)
    #GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"2007-01-23 Slide 14 T72 Low(2).gpr","""unavailable""",importParms)
    #GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"2007-01-23 Slide 16 T72 Low.gpr","""unavailable""",importParms)
    #GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"2007-01-23-T72 Slide 13 Low.gpr","""unavailable""",importParms)
    #GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"2007-01-24-T72 Slide 15 Low.gpr","""unavailable""",importParms)
    #GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"2007-01-24 T72 Slide 18 Low.gpr","""unavailable""",importParms)



    #GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"2007-01-12_0000 T72 Slide 4 Normal.gpr","""unavailable""",importParms)
    #GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"2007-01-12-T72 Slide 6 Normal.gpr","""unavailable""",importParms)
    #GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"2007-01-15-Slide 1 Normal.gpr","""unavailable""",importParms)
    #GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"2007-01-15-Slide 3 Normal Final.gpr","""unavailable""",importParms)
    #GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"2007-01-15-Slide 5 Normal Scan.gpr","""unavailable""",importParms)
    #GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"2007-01-15-T72 Slide 2 Normal Scan.gpr","""unavailable""",importParms)
    #GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"2007-01-16_0000 T72 Slide 8 Normal 0.92 Final.gpr","""unavailable""",importParms)
    #GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"2007-01-16-T72 Slide 9 Normal.gpr","""unavailable""",importParms)
    #GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"2007-01-17_0000 T72 Slide 10 Normal(2).gpr","""unavailable""",importParms)
    #GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"2007-01-17-T72 Slide 11 Normal.gpr","""unavailable""",importParms)
    #GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"2007-01-17-T72 Slide 12 Normal.gpr","""unavailable""",importParms)
    #GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"2007-01-18-T72 Slide 17 Normal.gpr","""unavailable""",importParms)
    #GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"2007-01-19-T72 Slide 14 Normal.gpr","""unavailable""",importParms)
    #GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"2007-01-23-T72 Slide 13 Normal.gpr","""unavailable""",importParms)
    #GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"2007-01-23-T72 Slide 18 Normal.gpr","""unavailable""",importParms)
    #GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"2007-01-24-T72 Slide 15 Normal.gpr","""unavailable""",importParms)
    #GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"2007-01-30_0000 Slide 16 Normal.gpr","""unavailable""",importParms)
    #GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"2007-01-30 Slide 7 redo for archive.gpr","""unavailable""",importParms)

    #GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"2007-01-17 Slide 10 T72 Ultra Low.gpr","""unavailable""",importParms)
    #GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"2007-01-17 Slide 11 T72 Ultra Low.gpr","""unavailable""",importParms)
    #GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"2007-01-17 Slide 7 T72 Ultra Low Final.gpr","""unavailable""",importParms)
    #GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"2007-01-17 Slide 8 T72 Ultra Low.gpr","""unavailable""",importParms)
    #GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"2007-01-17-T72 Slide 12 Ultra Low final.gpr","""unavailable""",importParms)
    #GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"2007-01-23 Slide 14 T72 Ultra Low.gpr","""unavailable""",importParms)
    #GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"2007-01-23 Slide 17 T72 Ultra Low 0.91.gpr","""unavailable""",importParms)
    #GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"2007-01-23-T72 Slide 13 Ultra Low.gpr","""unavailable""",importParms)
    #GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"2007-01-24 Slide 15 T72 Ultra Low.gpr","""unavailable""",importParms)
    #GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"2007-01-24 Slide 18 T72 Ultra Low(2).gpr","""unavailable""",importParms)
    #GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"2007-01-30 Slide 14 Ultra Low redo.gpr","""unavailable""",importParms)
    #GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"2007-01-30 Slide 16 Ultra Low Final.gpr","""unavailable""",importParms)
    #GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"2007-01-30 Slide 1 Ultra Low.gpr","""unavailable""",importParms)
    #GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"2007-01-30 Slide 2 Ultra Low Final.gpr","""unavailable""",importParms)
    #GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"2007-01-30 Slide 3 Ultra Low.gpr","""unavailable""",importParms)
    #GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"2007-01-30 Slide 4 Ultra Low Final.gpr","""unavailable""",importParms)
    #GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"2007-01-30 Slide 5 Ultra Low.gpr","""unavailable""",importParms)
    #GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"2007-01-30 Slide 6 Ultra Low.gpr","""unavailable""",importParms)
    #GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"2007-01-31 Slide 9 Ultra Low 0.87.gpr","""unavailable""",importParms)


    importParms = {
            'microarraylsid' : "012391_D_20050902.gal",
            'datasourcetype' : "GPRFile",
            'physicalsourcepath' : "/data/home/seqstore/agbrdf/zaneta/rachel",
            'studytype' : 'treated vs untreated microarray',
    }
    GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"68-high.gpr","""unavailable""",importParms,organism="unknown")
    GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"68-low.gpr","""unavailable""",importParms,organism="unknown")
    GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"68-medium.gpr","""unavailable""",importParms,organism="unknown")
    GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"69-high.gpr","""unavailable""",importParms,organism="unknown")
    GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"69-low.gpr","""unavailable""",importParms,organism="unknown")
    GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"69-medium.gpr","""unavailable""",importParms,organism="unknown")
    GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"70-high.gpr","""unavailable""",importParms,organism="unknown")
    GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"70-low.gpr","""unavailable""",importParms,organism="unknown")
    GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"70-medium.gpr","""unavailable""",importParms,organism="unknown")
    GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"71-high.gpr","""unavailable""",importParms,organism="unknown")
    GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"71-low.gpr","""unavailable""",importParms,organism="unknown")
    GPRMainAgResearch({ "samplename" : "CY5","sampletissue" : "unknown","sampletreatment" : "unknown"},{"samplename" : "CY3","sampletissue" : "unknown","sampletreatment" : "unknown"},"71-medium.gpr","""unavailable""",importParms,organism="unknown")

          



    return   
        
if __name__ == "__main__":
   main()


