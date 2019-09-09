#!/usr/bin/env python


from types import *
import string
import sys
import exceptions
import commands
import os
import re


class myException(exceptions.Exception):
    def __init__(self,args=None):
        self.args = args

def main():
    os.linesep = '\n' # for a Unix file

    if len(sys.argv) < 3:
       print "Useage : gblast2wrapper.py textinput1=myfile gblastdatabase=mydb"
       sys.exit(1)

    # get and parse command line args
    argDict = dict([ re.split('=',arg) for arg in sys.argv if re.search('=',arg) != None ])

    if 'textinput1' in argDict:
       argDict['infile'] = argDict['textinput1'] # presented like this when called from brdf

    if 'gblastdatabase' in argDict:
       argDict['db'] = argDict['gblastdatabase'] # presented like this when called from brdf


    cmd = "/var/www/cgi-bin/auth/dbupdate/gblast2 %(infile)s %(db)s"%argDict

    status, output = commands.getstatusoutput(cmd)

    print output



if __name__ == "__main__" :
    main()
