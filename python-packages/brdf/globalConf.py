# These global variables used to be changed for different installs,
# but are now all taken from environment variables.

from os import environ

IMAGEFILEPATH = environ['BRDF_IMAGEFILEPATH']

##### path for log files ##########
LOGPATH = environ['BRDF_LOGPATH']

JOIN_ROW_LIMIT = 200
