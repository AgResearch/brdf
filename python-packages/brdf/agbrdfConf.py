# These global variables used to be changed for different installs,
# but are now mostly taken from environment variables.

from os import environ

# Note that different brdf instances must have different image paths -
# can't use a single image directory, because there may be name
# collisions between the dynamically generates images
IMAGEFILEPATH = environ['BRDF_IMAGEFILEPATH_AGBRDF']
#

IMAGEURLPATH = "images"

TEMPIMAGEURLPATH = environ['BRDF_IMAGEURLPATH_AGBRDF']

##### home #################
HOMEPATH = "index.html"

###### CGI path ###########
CGIPATH = "cgi-bin"

######  Under construction ######
UNDERCONSTRUCTION = "zz_contents.htm"

WAITGLYPH = "loading.gif"

AGRESEARCH_TRACEDIRECTORY_GET_PATH = environ['BRDF_AGRESEARCH_TRACEDIRECTORY_GET_PATH']
AGRESEARCH_CREATE_FOLDER_SCRIPT = environ['BRDF_AGRESEARCH_CREATE_FOLDER_SCRIPT']

PADLOCK = "padlock.gif"

# these constants are used by the code that copies bfiles to the
# temp folder so that they can be accessed via web
BFILE_TEMPFOLDER = environ['BRDF_BFILE_TEMPFOLDER']
BFILE_TEMPURLPATH = environ['BRDF_BFILE_TEMPURLPATH']

BFILE_PUTPATH = environ['BRDF_BFILE_PUTPATH']
BFILE_GETPATH = environ['BRDF_BFILE_GETPATH']

BRDF_CSS_LINK = """
<link rel="stylesheet" type="text/css"
href="%s" />
""" % environ['BRDF_CSS']
