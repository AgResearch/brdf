#!/usr/bin/env python
#
# test creating folders from web - folder should appear in 
#
# /data/databases/flatfile/sequence_submission/pgc
#

from types import *
import os

def contentWrap(text):
    HTMLdoctype = """
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
   "httpd://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
"""
    page = "Content-Type: text/html\n\n" + HTMLdoctype
    page += text
    return page


# execute this when testing as apache from command line
#result=os.spawnlp(os.P_WAIT, 'sh', 'sh', '/data/devwww/usr/local/bin/makeseqsubfolder.sh', 'test7', 'mccullocha') # old version 
print contentWrap('test of creating a file<br/> Result : <BR/> ')
#(myin,myout,myerr)=os.popen3('sh /data/devwww/usr/local/bin/makeseqsubfolder.sh test8 mccullocha') #does not work from web but does from CL
(myin,myout,myerr)=os.popen3('sh /usr/local/bin/makeseqsubfolder.sh test16 mccullocha') #does not work from web either but should
print myerr.readlines()
print myout.readlines()
myin.close()
myerr.close()
myout.close()




