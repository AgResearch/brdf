#
# This module provides global variables that may need to be
# changed on install. Note that there is an include path in
# some modules that may also need to be changed
#
from types import *
import sys
import os
import globalConf

# this is the sheepgenomics web image path relative to globalConf.IMAGEPATH
# Note that different brdf instances must have different image paths -
# can't use a single image directory, because there may be name
# collisions between the dynamically generates images
#
###### path to images ######
# dos dev machine :
#IMAGEFILEPATH="agbrdf/agbrdfWeb/tmp"
IMAGEFILEPATH="/var/www/agbrdf/html/tmp"
# linux dev machine :
#IMAGEPATH="sheep/html/images"
IMAGEURLPATH="images"
TEMPIMAGEURLPATH="tmp"

##### home #################
HOMEPATH="index.html"
#HOMEPATH="http://agbrdf.agresearch.co.nz/index.html"


###### BASE ###############
#BASEPATH="/var/www/agbrdf/html/"
BASEPATH="/var/www/agbrdf/html/"

###### CGI path ###########
# dos dev
#CGIPATH="cgi-bin/agbrdf"
# linux dev
CGIPATH="cgi-bin"

###### Page path ##########
# dos dev
#PAGEPATH="http://localhost/agbrdf/agbrdfWeb/"
# linux dev
PAGEPATH="http://agbrdf.agresearch.co.nz/"

######  Under construction ######
# dos dev
UNDERCONSTRUCTION="zz_contents.htm"
# linux dev
#UNDERCONSTRUCTION="zz_contents.htm"
WAITGLYPH="loading.gif"


AGRESEARCH_TRACEDIRECTORY_GET_PATH="\\\\impala\\agbrdfsequencesubmissiondev"
# not used PGC_TRACEDIRECTORY_PUT_PATH="/data/flatfile/sequence_submission/agbrdftraces"
AGRESEARCH_CREATE_FOLDER_SCRIPT="/usr/local/bin/makeseqsubfolder.sh"

PADLOCK="padlock.gif"


# these constants are used by the code that copies bfiles to the
# temp folder so that they can be accessed via web
BFILE_ROOT=""
BFILE_TEMPFOLDER="/var/www/agbrdf/html/tmp"
BFILE_TEMPURLPATH="/tmp"

BFILE_PUTPATH = '/data/databases/flatfile/uploads/agbrdf'
BFILE_GETPATH = '/cgi-bin/agbrdf/getFile.py?FolderName=%s'


# redefine the default CSS location
BRDF_CSS_LINK_ABS = """
<link rel="stylesheet" type="text/css"
href="?" />
"""
BRDF_CSS_LINK_BRDF = """
<link rel="stylesheet" type="text/css"
href="/css/brdf.css" />
"""

BRDF_CSS_LINK_DOJO = """
<link rel="stylesheet" type="text/css"
href="?" />
"""

BRDF_CSS_LINK_NULL = ""

BRDF_CSS_LINK = BRDF_CSS_LINK_BRDF

