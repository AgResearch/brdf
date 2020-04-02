#
# This module provides database related constants, methods, and
# classes. It is intended to be modified when a brdf instance is installed.
# to use the specific database name, host etc. This is the only place
# where these need to be updated
#
import os
import sys
import types
import psycopg2

# method for returning a connection - using TCP
def getConnection():
    connection = psycopg2.connect("host='%s' dbname='%s' user='%s' password='%s'" % (
        os.environ['BRDF_DATABASE_HOST'],
        os.environ['BRDF_DATABASE_NAME'],
        os.environ['BRDF_DATABASE_USER'],
        os.environ['BRDF_DATABASE_PASSWORD'],
    ))
    return connection
