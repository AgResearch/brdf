#
# This module provides global variables that may need to be
# changed on install. Note that there is an include path in
# some modules that may also need to be changed
#
from types import *
import sys
import os
import globalConf


sys.path.append(os.path.join(globalConf.INSTALLPATH,'htpgenotype'))

# this is the sheepgenomics web image path relative to globalConf.IMAGEPATH
# Note that different brdf instances must have different image paths -
# can't use a single image directory, because there may be name
# collisions between the dynamically generates images
#
###### path to images ######
# dos dev machine :
#IMAGEFILEPATH="htpgenotype/htpgenotypeWeb/tmp"
IMAGEFILEPATH="/var/www/htpgenotype/html/tmp"
# linux dev machine :
#IMAGEPATH="sheep/html/images"
IMAGEURLPATH="images"
TEMPIMAGEURLPATH="tmp"

##### home #################
HOMEPATH="index.html"
#HOMEPATH="http://htpgenotype.agresearch.co.nz/index.html"


###### BASE ###############
#BASEPATH="/var/www/htpgenotype/html/"
BASEPATH="/var/www/htpgenotype/html/"

###### CGI path ###########
# dos dev
#CGIPATH="cgi-bin/htpgenotype"
# linux dev
CGIPATH="cgi-bin"

###### Page path ##########
# dos dev
#PAGEPATH="http://localhost/htpgenotype/htpgenotypeWeb/"
# linux dev
PAGEPATH="http://htpgenotypedev.agresearch.co.nz/"

######  Under construction ######
# dos dev
UNDERCONSTRUCTION="zz_contents.htm"
# linux dev
#UNDERCONSTRUCTION="zz_contents.htm"
WAITGLYPH="loading.gif"


#### PGC constants #####
AGRESEARCH_TRACEDIRECTORY_GET_PATH="\\\\impala\\htpgenotypesequencesubmissiondev"
# not used PGC_TRACEDIRECTORY_PUT_PATH="/data/flatfile/sequence_submission/htpgenotypetraces"
AGRESEARCH_CREATE_FOLDER_SCRIPT="/usr/local/bin/makeseqsubfolder.sh"




        
