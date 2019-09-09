#
# This module provides global variables that may need to be
# changed on install. Note that there is an include path in
# some modules that may also need to be changed
#
from types import *
import sys
import os
import globalConf


sys.path.append(os.path.join(globalConf.INSTALLPATH,'agresearch'))

# this is the sheepgenomics web image path relative to globalConf.IMAGEPATH
# Note that different brdf instances must have different image paths -
# can't use a single image directory, because there may be name
# collisions between the dynamically generates images
#
###### path to images ######
# dos dev machine :
IMAGEFILEPATH="agresearch/agresearchWeb/images"
# linux dev machine :
#IMAGEPATH="sheep/html/images"
IMAGEURLPATH="agresearch/agresearchWeb/images"

##### home #################
# dos dev machine :
HOMEPATH="agresearch/agresearchWeb/index.htm"
# linux dev :
#HOMEPATH="sheep/html/index.htm"


###### BASE ###############
BASEPATH="/var/www/agresearch/html/"

###### CGI path ###########
# dos dev
CGIPATH="cgi-bin/agresearch"
# linux dev
#CGIPATH="cgi-bin/sheepgenomics"

###### Page path ##########
# dos dev
PAGEPATH="http://localhost/agresearch/agresearchWeb/"
# linux dev
#PAGEPATH="http://devsheepgenomics.agresearch.co.nz/"

######  Under construction ######
# dos dev
UNDERCONSTRUCTION="zz_contents.htm"
# linux dev
#UNDERCONSTRUCTION="zz_contents.htm"



        
