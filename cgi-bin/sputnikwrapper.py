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
       print "Useage : sputnikwrapper.py textinput1=myfile parameters=parms"
       sys.exit(1)

    # get and parse command line args
    argDict = dict([ re.split('=',arg) for arg in sys.argv if re.search('=',arg) != None ])

    if 'textinput1' in argDict:
       argDict['infile'] = argDict['textinput1'] # presented like this when called from brdf

    if 'parameters' in argDict:
       argDict['parameters'] = argDict['parameters'] # presented like this when called from brdf


    # ignoring parameters completely at the mo' !
    cmd = "/usr/local/bin/sputnik -a -F100 %(infile)s"%argDict
    print cmd

    status, output = commands.getstatusoutput(cmd)

    print output



if __name__ == "__main__" :
    main()
