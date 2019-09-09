#
# this module contains a number of constants useful for generating HTML
#
# sources for images :
# Excel
# http://archive.museophile.org/images/gif/
# http://webpages.marshall.edu/images/
# http://www.accessexcellence.org/RC/VL/GG/index.html
# http://academy.d20.co.edu/kadets/lundberg/dna.html
#
#
from datetime import date
import re

NCBIEntrezGeneLink="http://www.ncbi.nlm.nih.gov/entrez/query.fcgi?db=gene&cmd=Retrieve&dopt=full_report&list_uids=%s"
NCBITaxonomyLink="http://www.ncbi.nlm.nih.gov/Taxonomy/Browser/wwwtax.cgi?id=%s"

genbankContentHeader = "Content-Type: chemical/seq-na-genbank\n\n"
textContentHeader = "Content-Type: text/html\n\n"
fastaContentHeader = """Content-Type: text/html

<html>
<body>
<pre>
"""
fastaContentFooter = """
</pre>
</body>
</html>
"""
fastaListDownloadHeader = """Content-Type: text/plain; name="%s"
Content-Description: %s
Content-Disposition: attachment; filename="%s"

"""


oldoldHTMLdoctype = '<!doctype html public "-//w3c//dtd html 4.0 transitional//en">'
oldHTMLdoctype = """
<?xml version = "1.0"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
   "httpd://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
"""
#
# Warning !!!! this doctype seems to cause problems for Javascript in Firefox.
# It is retained because a number of pages were designed using it, and 
# removing the DOCtype from the page causes all the font sizes to 
# bloat. We probably need to revisit this - for example, we may need to 
# rejig the stylesheets so that we can remove the Doctype header
#
#
HTMLdoctype = """
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
   "httpd://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
"""


CSSHelpButton = """
a.CSSHelpButton
{
    border:1px solid;
    border-color:#ffc8a4 #7d3302 #3f1a01 #ff9a57;
    padding:0px 3px 0px 3px;
    font:bold 10px verdana,sans-serif; 
    color:#FFFFFF; background-color:#ff0000;
    text-decoration:none;
    margin:0px;
}
"""
CSSDownloadButton = """
a.CSSDownloadButton
{
    border:1px solid;
    border-color:#ffc8a4 #7d3302 #3f1a01 #ff9a57;
    padding:0px 3px 0px 3px;
    font:bold 10px verdana,sans-serif; 
    color:#FFFFFF; background-color:#ff0000;
    text-decoration:none;
    margin:0px;
}
"""
CSSEditButton = """
a.CSSEditButton
{
    border:1px solid;
    border-color:#ffc8a4 #7d3302 #3f1a01 #ff9a57;
    padding:0px 3px 0px 3px;
    font:bold 10px verdana,sans-serif; 
    color:#FFFFFF; background-color:#ff6600;
    text-decoration:none;
    margin:0px;
}
"""
CSSCommentButton = """
a.CSSCommentButton
{
    border:1px solid;
    border-color:#ffc8a4 #7d3302 #3f1a01 #ff9a57;
    padding:0px 3px 0px 3px;
    font:bold 10px verdana,sans-serif; 
    color:#FFFFFF; background-color:#001188;
    text-decoration:none;
    margin:0px;
}
"""
CSSCheckOutButton = """
a.CSSCheckOutButton
{
    border:1px solid;
    border-color:#ffc8a4 #7d3302 #3f1a01 #ff9a57;
    padding:0px 3px 0px 3px;
    font:bold 10px verdana,sans-serif; 
    color:#FFFFFF; background-color:#079909;
    text-decoration:none;
    margin:0px;
}
"""
CSSAddLinkButton = """
a.CSSAddLinkButton
{
    border:1px solid;
    border-color:#ffc8a4 #7d3302 #3f1a01 #ff9a57;
    padding:0px 3px 0px 3px;
    font:bold 10px verdana,sans-serif; 
    color:#FFFFFF; background-color:#800207;
    text-decoration:none;
    margin:0px;
}
"""
CSSToggleSectionButton = """
a.CSSToggleSectionButton
{
    border:1px solid;
    padding:0px 3px 0px 3px;
    font:bold 10px verdana,sans-serif; 
    text-decoration:none;
    margin:0px;
}
"""
CSSMenus = """
span.CSSMenuTitle
{
    border:1px solid;
    border-color:#ffc8a4 #7d3302 #3f1a01 #ff9a57;
    font:bold 10px verdana,sans-serif;
    color:#FFFFFF; background-color:#ff6600;
    text-decoration:none;
    margin:0px;
    cursor:pointer;
    padding:3px;
    position: relative;
}

span.CSSMenuTitleHover
{
    border:1px solid;
    border-color:#3f1a01 #ff9a57 #ffc8a4 #7d3302;
    font:bold 10px verdana,sans-serif;
    color:#FFFFFF; background-color:#ff6600;
    text-decoration:none;
    margin:0px;
    cursor:pointer;
    padding:3px;
    position: relative;
}

a.CSSMenuOption
{
    border:1px solid;
    border-color:#ffc8a4 #7d3302 #3f1a01 #ff9a57;
    font:10px verdana,sans-serif;
    color:#FFFFFF; background-color:#ff6600;
    text-decoration:none;
    margin:0px;
    cursor:pointer;
    padding:3px;
    position: relative;
}

a.CSSMenuOptionHover
{
    border:1px solid;
    border-color:#3f1a01 #ff9a57 #ffc8a4 #7d3302;
    font:10px verdana,sans-serif;
    color:#FFFFFF; background-color:#ff6600;
    text-decoration:none;
    margin:0px;
    cursor:pointer;
    padding:3px;
    position: relative;
}
"""


#### in-line CSS elements removed 4/2009 ####
defaultBRDFStyle = ""

DeprecateddefaultBRDFStyle = """
BODY.old {
        FONT-SIZE: 90%; FONT-FAMILY: Arial, Helvetica, sans-serif; BACKGROUND: #f0f9ff ;    
}
BODY {
        FONT-SIZE: 90%; FONT-FAMILY: Arial, Helvetica, sans-serif; BACKGROUND: #f0f9ff ;    
}
TD {
        FONT-SIZE: 90%; FONT-FAMILY: Arial, Helvetica, sans-serif 
}
TD.inside {
        FONT-SIZE: 100%; FONT-FAMILY: Arial, Helvetica, sans-serif
}
TD.fieldvalue {
        FONT-SIZE: 95%; FONT-FAMILY: Arial, Helvetica, sans-serif; BACKGROUND-COLOR: #f0f9ff
}
TD.fieldname {
        FONT-SIZE: 95%; FONT-FAMILY: Arial, Helvetica, sans-serif; BACKGROUND-COLOR:  #90aefe 
}
TD.tableheading {
        FONT-SIZE: 120%; FONT-FAMILY: Arial, Helvetica, sans-serif; COLOR: #640064 ; BACKGROUND-COLOR: antiquewhite 
}
TR.brdftop2 { background-color: #ffbb11
}
TR.brdftop1 { background-color: #3366CC
}

P {
        FONT-SIZE: 100%; FONT-FAMILY: Arial, Helvetica, sans-serif ; 
}
UL {
        FONT-SIZE: 100%; FONT-FAMILY: Arial, Helvetica, sans-serif
}
OL {
        FONT-SIZE: 100%; FONT-FAMILY: Arial, Helvetica, sans-serif
}
H1 {
        FONT-WEIGHT: normal; FONT-SIZE: 170%; COLOR: #388fbd; FONT-FAMILY: Arial, Helvetica, sans-serif
}
H1 {
        FONT-WEIGHT: normal; FONT-SIZE: 170%; COLOR: #388fbd; FONT-FAMILY: Arial, Helvetica, sans-serif ; BACKGROUND-COLOR: #CCDCDC
}
H2 {
        FONT-WEIGHT: normal; FONT-SIZE: 160%; FONT-FAMILY: Arial, Helvetica, sans-serif
}
H3 {
        FONT-WEIGHT: normal; FONT-SIZE: 150%; FONT-FAMILY: Arial, Helvetica, sans-serif
}
H3.section {
        FONT-WEIGHT: normal; FONT-SIZE: 150%; FONT-FAMILY: Arial, Helvetica, sans-serif; BACKGROUND-COLOR: #CCDCDC
}
H4 {
        FONT-WEIGHT: normal; FONT-SIZE: 130%; FONT-FAMILY: Arial, Helvetica, sans-serif
}
H5 {
        FONT-WEIGHT: normal; FONT-SIZE: 110%; FONT-FAMILY: Arial, Helvetica, sans-serif
}
H6 {
        FONT-SIZE: 90%; FONT-FAMILY: Arial, Helvetica, sans-serif
}
TABLE.old {
        BORDER-RIGHT: 0px; BORDER-TOP: 0px; BORDER-LEFT: 0px; BORDER-BOTTOM: 0px; BACKGROUND-COLOR: antiquewhite
}
TABLE.inside {
        BORDER-STYLE: none ;
}
TABLE.sequence_submission_inside {
  border-collapse: collapse 
}
TABLE.sequence_submission_outside {
        border-right: thin groove #CCDCDC ; BORDER-TOP: thin groove #CCDCDC ;  BORDER-LEFT: thin groove #CCDCDC ;
        BORDER-BOTTOM: thin groove #CCDCDC 
}
TABLE.defaultbrdfcard { 
}
TABLE.brdftop1 {
    BORDER-COLLAPSE: collapse ;  border-color: #388FBD ;
}

td.outside  {
    padding-left: 10px;
    padding-right: 10px;
    padding-top: 10px;
    padding-bottom: 10px;
}
.required	 {
     color: red
}
.whiteheading {
        FONT-SIZE: 120%;  WIDTH: 100%; COLOR: #ffffff;  FONT-FAMILY: Arial, Helvetica, sans-serif; FONT-STYLE: normal; text-decoration: none;
}
.menuitem {
        FONT-SIZE: 120%;  WIDTH: 100%; COLOR: #ffffff;  FONT-FAMILY: Arial, Helvetica, sans-serif; FONT-STYLE: normal; text-decoration: none;
        }
.menuitem:hover {
        FONT-SIZE: 120%;  WIDTH: 100%; COLOR: #ffffff;  FONT-FAMILY: Arial, Helvetica, sans-serif; FONT-STYLE: normal; TEXT-DECORATION: underline
}        
.menuitem_small {
        WIDTH: 100%; COLOR: #ffffff;  FONT-FAMILY: Arial, Helvetica, sans-serif; FONT-STYLE: normal; text-decoration: none;
        }
.menuitem_small:hover {
        FONT-SIZE: 100%;  WIDTH: 100%; COLOR: #ffffff;  FONT-FAMILY: Arial, Helvetica, sans-serif; FONT-STYLE: normal; TEXT-DECORATION: underline
        }

.sectionheading {
        FONT-WEIGHT: bold; FONT-SIZE: 115%; WIDTH: 100%; FONT-FAMILY: Arial, Helvetica, sans-serif; BACKGROUND-COLOR: #388fbd
}

.sectionheading2 {
        FONT-WEIGHT: bold; FONT-SIZE: 115%; WIDTH: 100%; FONT-FAMILY: Arial, Helvetica, sans-serif; BACKGROUND-COLOR: #1111FF
}


.hiddentext {display:none ;  border-left: thick solid #388fbd ; margin-left:30px ; padding-left:10px } 

"""

AjaxJS = """
<script language="JavaScript1.2">

//SectionHeading
// A group of functions to support AJAX style interactive fetches of
// displays for an object.
//

// this method takes a URL, a list of queries, and the name of an 
// HTML element (e.g. div tag) which will be where the result is written.
// It then executes in turn an AJAX style post for each query, setting 
// the asynchronous flag to false so that the stream of results is 
// serialised. Each result is appended to the indicated result position
// in the doc
// SEE ALSO BELOW POLYMORPH
function DeprecatedxmlhttpMultiPost(strURL,queryArray,resultelementname,waitbanner,waitURL,caller) {
    //window.alert("in xmlhttpMultiPost");
    var xmlHttpReq = false;
    var self = this;
    var queryCount = 0;
    var buttonvalue = "" ;

    self.buttonvalue=caller.value;

    // Mozilla/SafariSectionHeading
    if (window.XMLHttpRequest) {
        self.xmlHttpReq = new XMLHttpRequest();
    }
    // IE
    else if (window.ActiveXObject) {
        self.xmlHttpReq = new ActiveXObject("Microsoft.XMLHTTP");
    }

    updatepage('<img src="/'+waitbanner+'" />',resultelementname);
    caller.value = "Processing request , please wait...";
    caller.disabled = true;

    
    
    self.xmlHttpReq.open('POST', waitURL);
    self.xmlHttpReq.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
    self.xmlHttpReq.onreadystatechange = function() {
        for(self.queryCount = 0; self.queryCount < queryArray.length; self.queryCount++) {

            if (queryArray.length == 1) {
                self.xmlHttpReq.open('POST', strURL, true);             // asynchronous if only one query
            }
            else {
                self.xmlHttpReq.open('POST', strURL, false);            // synchronous if multiple queries
            }

            //self.xmlHttpReq.open('POST', strURL, false);
            self.xmlHttpReq.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
            self.xmlHttpReq.onreadystatechange = function() {
                if (self.xmlHttpReq.readyState == 4) {
                     //window.alert("calling update page");
                     if (self.queryCount == 0 || queryArray.length == 1) {
                         updatepage(self.xmlHttpReq.responseText,resultelementname,"replace");
                     }
                     else {
                         updatepage(self.xmlHttpReq.responseText,resultelementname,"add");
                     }      
                }
            }
            // this function
            self.xmlHttpReq.send(queryArray[self.queryCount]);
        }
        caller.value = self.buttonvalue;
        caller.disabled = false;

    }
    self.xmlHttpReq.send("dummy=1");
}



//RUSSELL'S refactored version
function xmlhttpMultiPost(strURL,queryArray,resultelementname,waitbanner,waitURL,caller) {

	var xmlHttpReq;
	var numQueries = queryArray.length;
	var resultNum = 1;
    	var buttonValue = caller.value;

	caller.disabled = true;
    	caller.value = "Processing request , please wait...";
 	updatepage('<img src="/'+waitbanner+'" />',resultelementname);   	
	

	// setup the request
	try{
		// Opera 8.0+, Firefox, Safari
		xmlHttpReq= new XMLHttpRequest();
	} catch (e){
		// Internet Explorer Browsers
		try{
			xmlHttpReq= new ActiveXObject("Msxml2.XMLHTTP");
		} catch (e) {
			try{
				xmlHttpReq= new ActiveXObject("Microsoft.XMLHTTP");
			} catch (e){
				// Something went wrong
				alert("Your browser broke!");
				return false;
			}
		}
	}


	// Create a function that will receive data sent from the server
	// only needs to be done once!
	xmlHttpReq.onreadystatechange = function(){
		if(xmlHttpReq.readyState == 4){
		    if(xmlHttpReq.status == 200){
			if (resultNum  == 1) {
                         updatepage(xmlHttpReq.responseText,resultelementname,"replace");
			    resultNum++;
                     }
                     else {
                         updatepage(xmlHttpReq.responseText,resultelementname,"add");
			    resultNum++;
                     }
		    }else{alert("There was a problem retrieving the xml data:\\n" + 
					xmlHttpReq.status + ":\t" + xmlHttpReq.statusText + 
					"\\n" + xmlHttpReq.responseText);}
		}//end xmlHttpReq.readyState
	}//end xmlHttpReq.onreadystatechange


	//process all the queries and send by POST
	// http://www.openjs.com/articles/ajax_xmlhttp_using_post.php
	for(queryCount = 0; queryCount < numQueries ; queryCount++) {
	     if (numQueries  == 1) {
		// asynchronous if only one query
              xmlHttpReq.open('POST', ".."+strURL, true);
            }
            else {
		// synchronous if multiple queries
              xmlHttpReq.open('POST', ".."+strURL, false);
            }

	    //Send the proper header information along with the request
	    xmlHttpReq.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
	    xmlHttpReq.setRequestHeader("Content-length", queryArray[queryCount].length);
	    xmlHttpReq.setRequestHeader("Connection", "close");

	    xmlHttpReq.send(queryArray[queryCount]); 

	    //handle request timeouts.e.g. Retry or inform user.
	    var requestTimer = setTimeout(function() {
	        if ( callInProgress(xmlHttpReq) ) {
		     xmlHttpReq.abort();
	            updatepage("<h2>Error: request timed out.</h2>",resultelementname,"replace");
	            caller.value = buttonValue;
                   caller.disabled = false;
	        }
	    }, 10000); //10 seconds


	}//end for loop


	//disabled button untill all queries are completed
	if(resultNum == numQueries){
	    caller.value = buttonValue;
           caller.disabled = false;
	}

}//end function xmlhttpMultiPost()






//.... this version does not assume it is being called by a button...SEE ALSO ABOVE POLYMORPH
function xmlhttpMultiPost(strURL,queryArray,resultelementname,waitbanner,waitURL) {
    //window.alert("in xmlhttpMultiPost");
    var xmlHttpReq = false;
    var self = this;
    var queryCount = 0;
    var buttonvalue = "" ;

    // Mozilla/SafariSectionHeading
    if (window.XMLHttpRequest) {
        self.xmlHttpReq = new XMLHttpRequest();
    }
    // IE
    else if (window.ActiveXObject) {
        self.xmlHttpReq = new ActiveXObject("Microsoft.XMLHTTP");
    }

    updatepage('<img src="/'+waitbanner+'" />',resultelementname,"replace");

    //window.alert("query length=" + queryArray.length);
    
    
    self.xmlHttpReq.open('POST', waitURL);
    self.xmlHttpReq.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
    self.xmlHttpReq.onreadystatechange = function() {
        for(self.queryCount = 0; self.queryCount < queryArray.length; self.queryCount++) {
            //window.alert("opening : " + strURL);

            
            if (queryArray.length == 1) {
                self.xmlHttpReq.open('POST', strURL, true);             // asynchronous if only one query
            }
            else {
                self.xmlHttpReq.open('POST', strURL, false);            // synchronous if multiple queries
            }

            //self.xmlHttpReq.open('POST', strURL, false);


            
            self.xmlHttpReq.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
            self.xmlHttpReq.onreadystatechange = function() {
                //window.alert("ready state = " + self.xmlHttpReq.readyState);
                if (self.xmlHttpReq.readyState == 4) {
                     //window.alert("calling update page with response " + self.xmlHttpReq.responseText);
                     if (self.queryCount == 0 || queryArray.length == 1) {
                         updatepage(self.xmlHttpReq.responseText,resultelementname,"replace");
                     }
                     else {
                         updatepage(self.xmlHttpReq.responseText,resultelementname,"add");
                     }      
                }
            }
            //window.alert("sending " + queryArray[self.queryCount]);
            self.xmlHttpReq.send(queryArray[self.queryCount]);
        }
    }
    self.xmlHttpReq.send("dummy=1");
}




//
// This method simply inserts a given fragment in the indicated position
//
function updatepage(str,targetelement,mode){
    if(mode == "add") {
        document.getElementById(targetelement).innerHTML += str;
    }
    else {
        document.getElementById(targetelement).innerHTML = str;
    }
}


//
// this method martials options from a multi-select box, into an array
// and then calls another method to do the actual xmlhttp AJAX stuff
// queryLeader would typically be (e.g. )
// "displayprocedure=blah&amp;obid="
// This polymorph assumes it is being called from a button - see other polymorph below
function multipost(url,selectname,resultelementname,queryleader,waitbanner,waiturl,caller) {
   //window.alert("in multipost");
   var self = this;
   var queryArray=new Array();
   var queryCount = 0;

   
   for(var i=0 ; i < document.getElementById(selectname).options.length; i++) {
      if (document.getElementById(selectname).options[i].selected ) {
         payload = getDynamicData(document.getElementById(selectname).options[i].value)
         queryArray[queryCount] = queryleader+escape(document.getElementById(selectname).options[i].value)+payload;
         queryCount += 1
      }
   }
   if(queryCount == 0) {
      window.alert("Please select at least one procedure to run");
      return false;
   }   
   JavaScript:xmlhttpMultiPost(url,queryArray,resultelementname,waitbanner,waiturl,caller);
}


// This polymorph does not assume it is being called from a button - see other polymorph above
function multipost(url,selectname,resultelementname,queryleader,waitbanner,waiturl) {
   //window.alert("in multipost");
   var self = this;
   var queryArray=new Array();
   var queryCount = 0;
   
   for(var i=0 ; i < document.getElementById(selectname).options.length; i++) {
      if (document.getElementById(selectname).options[i].selected ) {
         //window.alert("adding " + queryleader+escape(document.getElementById(selectname).options[i].value));
         payload = getDynamicData(document.getElementById(selectname).options[i].value)         
         queryArray[queryCount] = queryleader+escape(document.getElementById(selectname).options[i].value)+payload;
         queryCount += 1
      }
   }

   if(queryCount == 0) {
      window.alert("Please select at least one procedure to run");
      return false;
   }
   JavaScript:xmlhttpMultiPost(url,queryArray,resultelementname,waitbanner,waiturl);
}


// this assumes that for each element of the query array, there is an HTML element with
// id equal to that element, with child elements containing data to be posted.
// Typically this would consist of a form section for each query element, containing
// data fields such as text areas, input fields, radio boxes.
// These data input elements are the HTML equivalent of "prompting" for the values required
// to execute the query.
//
// Each div section contains one or more data elements. Each data element corresponds to
// a datasource object that is bound to the query. Each of these datasource objects
// knows how to construct its data element from information stored in an associated fact table,
// and the complete div section is contructed by the initAnalysisFunctions method - i.e.
// this is constructed as part of the object creation, for use in rendering the object
//
function getDynamicData(queryinstance) {

    //window.alert("in getDynamicData with queryinstance "+ queryinstance);
    payload="";
    formid = "form"+queryinstance;
    myform = document.getElementById(formid);
    if(myform == null) {
       return payload;
    }
    //window.alert("processing form " + formid);
    if(document.forms[formid].elements != null) {
       for(i=0 ; i < document.forms[formid].elements.length ; i++ ) {
          if(document.forms[formid].elements[i].type == "textarea") {
             datasource = document.forms[formid].elements[i].id;
             payload += "&datasource" + datasource + "=" + document.forms[formid].elements[i].value ;
          }
          else if(document.forms[formid].elements[i].type == "select-multiple") {
             datasource = document.forms[formid].elements[i].id;
             payload += "&datasource" + datasource + "=";
             for(j=0 ; j < document.forms[formid].elements[i].options.length ; j++) {
                if(document.forms[formid].elements[i].options[j].selected) {
                   payload += document.forms[formid].elements[i].options[j].value;
                   payload += "\\r\\n";
                }
             }
          }
          else if(document.forms[formid].elements[i].type == "select-one") {
             datasource = document.forms[formid].elements[i].id;
             payload += "&datasource" + datasource + "=";
             payload += document.forms[formid].elements[i].value;
          }
       }
    }

    //window.alert(payload);

   return payload;
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

function toggleVisibility(caller, divid) {
    if(document.getElementById(divid).style.display == 'none'){
      document.getElementById(divid).style.display = 'block';
    }else{
      document.getElementById(divid).style.display = 'none';
    }
}

</script>
"""

defaultMenuJS=r"""
    <SCRIPT language="JavaScript1.2">
    var mywindow=null;
    var myhelpcontent="";
    var brdfpopupinstance = 0;
    function brdfpopup(heading,content) {
       if(brdfpopupinstance == 0) {
           mywindow=window.open("","Describe","status=0,toolbar=0,menubar=0,scrollbars=1,width=800,height=600,resizable=1");
           mywindow.moveTo(100,100);
           // pagewrap the content
           mywindow.document.write('<html><head><title>' + heading + '</title>\n');
           mywindow.document.write('<style type= "text/css">\n');
           mywindow.document.write('BODY { FONT-SIZE: 90%%; FONT-FAMILY: Arial, Helvetica, sans-serif; BACKGROUND: #f0f9ff; }\n');
           mywindow.document.write('</style></head>\n');
           mywindow.document.write('<body>\n');
           mywindow.document.write('<button onclick="self.close()">Close</button>');
           mywindow.document.write('<p/>');
           mywindow.document.write(content);
           mywindow.document.write('<button onclick="self.close()">Close</button>');
           mywindow.document.write('<p/></body></html>\n');
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
    
    
    var isIE = navigator.appName.indexOf('Microsoft') > -1;

    function findPos(obj) {
        var curleft = curtop = 0;
        if (obj.offsetParent) {
            do {
                curleft += obj.offsetLeft;
                curtop += obj.offsetTop;
            } while (obj = obj.offsetParent);
        }
        return [curleft,curtop];
    }
    
    
    var menuCount = 0;
    
    function showEditMenu(menuObj){showMenu(menuObj, "Edit", editItemArray);}
    function showAnnotateMenu(menuObj){showMenu(menuObj, "Annotate", annotateItemArray);}
    function showViewMenu(menuObj){showMenu(menuObj, "View", viewItemArray);}
    function showToolsMenu(menuObj){showMenu(menuObj, "Tools", toolsItemArray);}
    function showHelpMenu(menuObj){showMenu(menuObj, "Help", helpItemArray);}
    
    function showMenu(menuObj, menuName, itemArray) {
        divId = "menuDiv_"+menuName;
        hideMenu();
        var hw = findPos(menuObj);
        var w = hw[0] - 2;
        var h = hw[1] - 1;
        if (isIE) {w=hw[0]-4;h=hw[1];}
        h += menuObj.offsetHeight;
        //Create a Div at the bottom of this button, to display the menu
        var myDiv = document.createElement("div");
        myDiv.style.position = "absolute";
        myDiv.style.top = h.toString() + "px";
        myDiv.style.left = w.toString() + "px";
        myDiv.id = divId;
        
        var tbl = document.createElement("table");
        tbl.border = 0;
        tbl.style.cursor = "pointer";
        tbl.style.borderCollapse = "collapse";
        tbl.cellPadding = "2px";
        if (isIE) {tbl.cellPadding = "4px";}
        
        for (i=0; i< itemArray.length; i++) {
            var cell = tbl.insertRow(i).insertCell(0);
            cell.innerHTML = "<a class='CSSMenuOption' onmouseout='leaveField(this);' onmouseover='hoverField(this);'onClick='" + 
                             itemArray[i][0] + "'>" + itemArray[i][1] + "</a>";
        }
        
        myDiv.appendChild(tbl);
        document.body.appendChild(myDiv);
        menuCount++;

        
        //modify the padding in each anchor so that it pads out the width of the column!
        for (i=0; i< tbl.rows.length; i++) {
            var anc = tbl.rows[i].cells[0].childNodes[0];
            var tWidth = tbl.offsetWidth + 4;
            var aWidth = anc.offsetWidth + 5;
            if (isIE) {tWidth=tbl.offsetWidth;}
            if (tWidth > (aWidth+3)) anc.style.paddingRight = (tWidth-aWidth) + "px";
        }
    }
    
    function hideMenu() {
        while (menuCount > 0) {
            var tbl = document.body;
            tbl.removeChild(tbl.lastChild);
            menuCount--;
        }
    }
    
    var checkIt;
    function delayedHideMenu(obj) {
        if (isNaN(checkIt)==false) clearTimeout(checkIt);
        checkIt = setTimeout("hideMenu()", 500);
    }
    function cancelHideMenu() {
        clearTimeout(checkIt);
    }
    
    function hoverField(fld) {fld.className = fld.className + "Hover";cancelHideMenu();}
    function leaveField(fld) {fld.className = fld.className.substring(0,fld.className.indexOf("Hover"));delayedHideMenu();}

    %s
    </SCRIPT>
"""

dynamicMenuJS=r"""
    function unavailable(opt) {
        hideMenu();
        window.alert("Sorry, there are no options for this menu - please contact Alan McCulloch " + 
                     "(alan.mcculloch@agresearch.co.nz) if you want to be able to " + opt + " this object.");
    }

    function helpButton() {
        hideMenu();
        %(helpchunk)s;
    }
    
    function annotateButton(link) {
        hideMenu();
        return location.href=link;
    }
        
    var editItemArray = new Array();
    editItemArray[0] = new Array("unavailable(\"edit\");","No options available");
    
    var annotateItemArray = new Array();
    annotateItemArray[0] = new Array("annotateButton(\"%(addCommentURL)s\");","Add Comment");
    annotateItemArray[1] = new Array("annotateButton(\"%(addLinkURL)s\");","Add Hyperlink");
    
    var viewItemArray = new Array();
    viewItemArray[0] = new Array("unavailable(\"view\");","No options available");
    
    var toolsItemArray = new Array();
    toolsItemArray[0] = new Array("unavailable(\"use tools on\");","No options available");
        
    var helpItemArray = new Array();
    helpItemArray[0] = new Array("helpButton();","Help");
"""

def contentWrap(text, doctype=HTMLdoctype):
    page = "Content-Type: text/html\n\n" + doctype
    page += text
    return page


def getStyle(style="default"):
    css = '<style type= "text/css">' + \
    CSSEditButton + CSSCommentButton + CSSCheckOutButton +\
    CSSAddLinkButton + defaultBRDFStyle + '</style>'
    return css

def pageWrap(heading,text,doctype=HTMLdoctype,menuJS="", cssLink=""):
    page = "Content-Type: text/html\n\n" + doctype
    page += '<html>\n<head>\n<title>\n' + heading + '</title>\n'
    #page += '<style type= "text/css">'
#    page += CSSEditButton
#    page += CSSCommentButton
#    page += CSSCheckOutButton
#    page += CSSAddLinkButton
#    page += CSSHelpButton
    page += defaultBRDFStyle # this is deprecated and now only adds an empty string
    #page += '</style>'
    page += cssLink
    page += AjaxJS
    page += menuJS
    page += '</head>\n<body class="tundra">\n'
    page += '<table class=defaultbrdfcard width=90% align=center>\n<tr>\n<td><h2>'+heading+'</h2><p>'    
    page += text
    page += '<p><p>\n'
    page += '<i>'+date.isoformat(date.today())+'</i>\n'
    page += '<p></td>\n</tr>\n</table>\n'    
    page += '</body>\n</html>\n'
    return page




def tidyout(line, linewidth, currentpos, lineend, autoStyle=True):
    """ This method is used to pour a string into a rectangular shape. It is given
    which column we are up to in the shape, the linewidth and the string. It returns
    a string with the correct lineend string  inserted (e.g. could be \n or <br/> etc),
    and an updated column position in case we need to call this again.
    If autoFont is set to true then this method will make decisions about which font
    to use - for example if its looks like a DNA sequence, it will use courier small"""
    openStyle = ''
    closeStyle = ''
    url=False
    if autoStyle:
        # format things tha look like bio sequences
        if len(line) > 40:
            if re.search('^[A-Z]+$',line.upper()) != None:
                # looks like a sequence
                openStyle = '<pre>'
                closeStyle = '</pre>'
                lineend = '<br/>'
                

        # format things that look like URL's
        if re.search('^http[s]*\:\/',line) != None:
            url=True
            result = '<a href="%s" target=urllinkout> %s </a>'%(line,line)
        

    if not url:
        result=openStyle
        for i in range(0,len(line)):
            if currentpos == linewidth:
                result += lineend
                currentpos = 0            
            result += line[i:i+1]
            currentpos += 1

            #print currentpos
        result += closeStyle
        
    return (result,currentpos)
