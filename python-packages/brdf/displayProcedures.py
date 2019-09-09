#-----------------------------------------------------------------------+
# Name:		displayProcedures.py           				|
#									|
# Description:	classes that implements display procedures              |
#		                                                        |
#                                                                	|
#=======================================================================|
# Copyright 2005 by AgResearch (NZ).					|
# All rights reserved.							|
#									|
#=======================================================================|
# Revision History:							|
#									|
# Date      Ini Description						|
# --------- --- ------------------------------------------------------- |
# 11/2005    AFM  initial version                                       |
#-----------------------------------------------------------------------+
import sys
from types import *
import csv
import re
import os
import math
import random
from datetime import date
import globalConf
#import agbrdfConf #<------------------ !!!!!!!!!! for testing only , remove !!!!!!!!!!!!!!!!!!!!
from brdfExceptionModule import brdfException
from imageModule import makeOpGlyph, makeBarGraph,getJPEGThumbs,getColourScheme
from annotationModule import uriOb
import databaseModule
import logging
import os.path
import commands
import string
import copy


# set up logger if we want logging
displaymodulelogger = logging.getLogger('displayProcedures')
displaymodulehdlr = logging.FileHandler(os.path.join(globalConf.LOGPATH,'displayprocedures.log'))
#hdlr = logging.FileHandler('c:/temp/sheepgenomicsforms.log')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
displaymodulehdlr.setFormatter(formatter)
displaymodulelogger.addHandler(displaymodulehdlr) 
displaymodulelogger.setLevel(logging.INFO)        

""" --------- module variables ----------"""


""" --------- module methods ------------"""

def marshallBfile(sourcefolder='',sourcefilename='', targetfolder='', targetfilename = ''):
    """ this method is used to marshall an uploaded file (BFile), from the achive folder containing it,
    to the temp directory from which it will be made accessible to the user.
    It returns the temp file name
    """

    BUFSIZE=2048

    # check source file exists - exception if not
    source = os.path.join(sourcefolder,sourcefilename)
    if not os.path.exists(source):
        raise brdfException("marshallBfile : %s does not exist"%source)

    # get suffix
    suffix = ''
    basename = os.path.basename(sourcefilename)
    tokens = re.split('\.',basename)
    if len(tokens) > 0:
        suffix = tokens[-1]
        

    
    # calculate the hash of the args which will be the temp file name
    if len(targetfilename)  > 0:
        tempfilename = targetfilename
    else:
        tempfilename = "%s.%s"%(str(abs(hash(  sourcefolder+sourcefilename+targetfolder+targetfilename))), suffix)


    target = os.path.join(targetfolder,tempfilename)


    displaymodulelogger.info("marshallBFile is checking if  %s => %s"%(source,target))

    # see if the temp file exists
    if not os.path.exists(target):
        fin = None
        fout = None
        try:
            displaymodulelogger.info("marshallBFile is copying %s -> %s"%(source,target))
            fin = file(source,"rb")
            fout = file(target,"wb")
            buf = fin.read(BUFSIZE)
            while len(buf) > 0:
                fout.write(buf)
                buf = fin.read(BUFSIZE)
        finally:
            if fin != None:
                fin.close()
            if fout != None:
                fout.close()


    return tempfilename
                
            

def marshallDataSource(datasourceob=None, targetfolder='', targetfilename = '', uncompress=False, bin="/usr/bin", sourcefilename=''):
    """ this method is similar to the marshallBFile method , however this method obtains the
    source or archive file name from the database. If the uncompress option is set it will try to uncompress the
    source to obtain the temp file, rather than copy it.

    Change Log :

    9/8/2012 modified so can obtain all file and path namees from the database - added

    datasourcename = will be interpreted as targetfilename, i.e. the base name of the file in an archive
    datasourcecontent = will be interpreted as the full path in the archive 
    
    """

    connection=databaseModule.getConnection()
    dataCursor=connection.cursor()
    sql ="""
    select
    physicalsourceuri,
    datasourcename,
    datasourcecontent
    from
    datasourceob
    where
    obid = %s"""%datasourceob
    dataCursor.execute(sql)
    source = dataCursor.fetchone()
    sourceArchive = source[0]
    sourceFile = sourcefilename
    if sourceFile == '' and source[1] != None:
        sourceFile = source[1]
    sourceFilePath = source[2]
    
    
    connection.close()

    if not uncompress:
        
        BUFSIZE=2048

        # check source archive exists - exception if not
        if not os.path.exists(sourceArchive):
            raise brdfException("marshallDataSource : %s does not exist"%sourceArchive)

        # get suffix
        suffix = ''
        basename = os.path.basename(sourceArchive)
        tokens = re.split('\.',basename)
        if len(tokens) > 0:
            suffix = tokens[-1]
            

        
        # calculate the hash of the args which will be the temp file name
        if len(targetfilename)  > 0:
            tempfilename = targetfilename
        elif sourceFile != None:
            tempfilename = sourceFile
        else:
            tempfilename = "%s.%s"%(str(abs(hash(  sourceArchive+targetfolder+targetfilename))), suffix)


        target = os.path.join(targetfolder,tempfilename)


        displaymodulelogger.info("marshallDataSource is checking if  %s => %s"%(sourceArchive,target))

        # see if the temp file exists
        if not os.path.exists(target):
            fin = None
            fout = None
            try:
                displaymodulelogger.info("marshallDataSource is copying %s -> %s"%(sourceArchive,target))
                fin = file(sourceArchive,"rb")
                fout = file(target,"wb")
                buf = fin.read(BUFSIZE)
                while len(buf) > 0:
                    fout.write(buf)
                    buf = fin.read(BUFSIZE)
            finally:
                if fin != None:
                    fin.close()
                if fout != None:
                    fout.close()

                

        return tempfilename
    else:
        # try .gz and .zip  - give up if not these, just do a non-compressed process
        prog = ""
        args = ""
        target = ""
        if re.search('\.gz$',sourceArchive) != None:
            prog = "gunzip"
            args = " -c %s > %s"
            target = re.split('\.gz',sourceArchive)[0]
        elif re.search('\.zip$',sourceArchive) != None:
            # if there is no sourcefilename then we just unzip the archive
            # if there is a source filename then we extract that file out of the archive
            if len(sourceFile) == 0:
                prog = "unzip"
                args = " -p %s > %s"
                target = targetfilename
                if len(target) == 0:
                    target = re.split('\.zip',sourceArchive)[0]                
            else:
                prog = "unzip"
                args = " -p %s %s > %s"
                target = targetfilename
                if len(target) == 0:            
                    target = sourceFile
                
                
        else:
            return marshallDataSource(datasourceob, targetfolder, targetfilename , uncompress=False)

        tempfilename = os.path.basename(target)
        target = os.path.join(targetfolder,tempfilename)

        if not os.path.exists(target):        

            # uncompress
            prog = os.path.join(bin,prog)
            cmd = prog + args
            if len(sourceFile) == 0:
                cmd = cmd%(sourceArchive,target)
            else:
                if sourceFilePath != None:
                    cmd = cmd%(sourceArchive,sourceFilePath, target)
                else:
                    cmd = cmd%(sourceArchive,sourceFile, target)
                

            displaymodulelogger.info("marshallDataSource is executing %s"%cmd)
            status, output = commands.getstatusoutput(cmd)
            displaymodulelogger.info("Output: %s"%output)
            displaymodulelogger.info("Status: %s"%status)
            displaymodulelogger.info("Returning: %s"%tempfilename)

        
        return tempfilename


def compileSFFFile(connection, outfolder='',  shellscript= './appendsfffile.sh', shell="/bin/sh", tempfolder="/tmp" , readDict = {}, \
            commentlogger = None, datasource = None, fileuri=None, filenamebase = 'base'):
    """ this method takes a dictionary keyed by sff filename , with values
    being a tuple of reads in that file to extract.

    An external script is called which iterates through each file,
    calling an external script to accumulate an SFF file.

    Example of successive calls to the external script :

./appendsfffile.sh  sffacc1.txt  /data/bfiles/isgcdata/romney180_05/Baylor.E0C6VPL01.sff.gz  outfile.sff /tmp
./appendsfffile.sh  sffacc2.txt  /data/bfiles/isgcdata/romney180_05/Baylor.E0FD4S102.sff.gz  outfile.sff /tmp
    

    """

    displaymodulelogger.info("in compileSFFFile")
    displaymodulelogger.info("request : " + str(readDict))

    # calculate the outfile name ( a hash of the list of reads) , and
    # see if it already exists
    #base = str(abs(hash( str(readDict) + hashconstant) ))
    base = filenamebase

    outfilename = "%s.sff"%base
    outfilepath = os.path.join(outfolder,outfilename)
    if os.path.exists(outfilepath):
        displaymodulelogger.info("error compiled file %s already exists"%outfilepath)
        raise brdfException("error in compileSFFFile - compiled file %s already exists"%outfilepath)
 

    displaymodulelogger.info("compileSFFFile is generating %s"%(outfilename))


    #link the final file to the datasource ob
    if datasource != None:
        if fileuri != None:
            fileuri.databaseFields.update(
            {
              'createdby' : 'system',
              'uristring' : '/cgi-bin/isgcdata/getFile.py?datasource=%s'%datasource.databaseFields['obid'],
              'xreflsid'  : '/cgi-bin/isgcdata/getFile.py?datasource=%s'%datasource.databaseFields['obid'],
              'visibility' : 'public'
            })
            fileuri.insertDatabase(connection)
            fileuri.createLink(connection,datasource.databaseFields['obid'],'Link to Custom SFF file','system',\
                 iconpath='/images/enlrg-flowgram.gif',iconattributes='(32,74)')

    

    # file does not exist, so create it...
    filecount = 0
    print "<pre>"
    for sfffile in readDict:
        print "adding reads from %s (file %d of %d ) "%(sfffile, filecount+1, len(readDict))
        if commentlogger != None:
            commentlogger.appendText(connection, "adding reads from %s (file %d of %d ) "%(sfffile, filecount+1, len(readDict)))
        filecount += 1

        displaymodulelogger.info("compileSFFFile is processing %s"%(sfffile))


        # if necessary write the accessions file
        accessionfilename = "%s_%d.acc"%(base,filecount)
        accessionfilepath = os.path.join(tempfolder,  accessionfilename ) 
        displaymodulelogger.info("writing %s"%accessionfilepath)   
        file = open(accessionfilepath,"w")
        for seqread in readDict[sfffile]:
            file.write(seqread)
            file.write("\n")
        file.close()        
        

        cmd = '%(shell)s %(shellscript)s %(accessionfilename)s %(sfffile)s %(outfilename)s %(outfolder)s %(tempfolder)s'%{
           'shellscript' : shellscript,
           'accessionfilename' : accessionfilename,
           'sfffile' : sfffile,
           'outfilename' : outfilename,
           'shell' : shell,
           'outfolder' : outfolder,
           'tempfolder' : tempfolder
        }

        displaymodulelogger.info("compileSFFFilet is executing %s"%cmd)
        status, output = commands.getstatusoutput(cmd)
        displaymodulelogger.info("Output: %s"%output)
        displaymodulelogger.info("Status: %s"%status)
        # log any error messages
        if re.search("error",output,re.IGNORECASE)  or re.search("warning",output,re.IGNORECASE) != None:
            commentlogger.appendText(connection,output)
            print output
            
            
    print "</pre>"


    commentlogger.appendText(connection,"== Finished compilation ==")
        
    


def shellDataSource(datasourceob=None, targetfolder='', targetfilename = '', uncompress=False, bin="/usr/bin",shellscript = "./ssfinfo -i "):
    """
    this method calls a script on a server which takes as an argument a filename corresponding to the datasource.
    it first marshalls the data source to a temp file , then calls the shell script with the temp filename as
    an argument
    """

    tempfile = marshallDataSource(datasourceob, targetfolder, targetfilename , uncompress, bin)


    cmd = '/bin/sh %(shellscript)s  %(tempfile)s '%{
       'shellscript' : shellscript,
       'tempfile' : tempfile
    }

    displaymodulelogger.info("getSequenceTraceViewPanel is executing %s"%cmd)
    status, output = commands.getstatusoutput(cmd)
    displaymodulelogger.info("Output: %s"%output)
    displaymodulelogger.info("Status: %s"%status)


    tempimagefile = output.strip()    

    if re.search('^ERROR',tempimagefile) != None:
        resultHTML="""
                    <tr>
                    <td colspan="2" class=tableheading>
                    %s
                    </td>
                    </tr>
        """%tempimagefile
    else:
        resultHTML = """
                    <tr>
                    <td colspan="2" class=tableheading> 
                    %(sectionheading)s
                    </td>
                    </tr>
                """%{
                'sectionheading' : sectionheading
                }


        inlineHTML= """
                        <tr>
                        <td colspan=2 align=center>
                        <p/>
                        <iframe src="%(tempimageurl)s%(tempimagefile)s" align="center" width="%(width)s" height="%(height)s"></iframe>
                        <p/>
                        </td>
                        </tr>
                """
        inlineHTML = inlineHTML%{
                'tempimageurl' : tempimageurl,
               'tempimagefile' : tempimagefile,
               'height' : height + 40,
               'width' : width,
               'sectionheading' : sectionheading
        }

        resultHTML += inlineHTML


    return resultHTML





        


def getSampleFactDisplay(obid=None, factnamespace=None, attributename = None, usercontext="default", fetcher=None, imagepath=None, tempimageurl=None, sectionheading=None,graphtitle1=None,graphtitle2=None,\
                         barwidth=10):
    sql="""
        select
           bs.obid,
           bs.xreflsid,
           bs.samplename,
           getsamplecharfact(bs.obid, %(factnamespace)s, %(attributename)s)
        from
           biosamplingfunction bsf join biosampleob bs on
           bsf.biosubjectob = %(obid)s and
           bs.obid = bsf.biosampleob
        order by
           bs.xreflsid
           """
    displaymodulelogger.info("executing %s"%str(sql%{'obid' : obid, 'factnamespace' : factnamespace, 'attributename' : attributename}))
    connection = databaseModule.getConnection()
    dataCursor = connection.cursor()
    dataCursor.execute(sql,{'obid' : obid, 'factnamespace' : factnamespace, 'attributename' : attributename})
    rows = dataCursor.fetchall()
    dimensionData = []
    for row in rows :
        dataTuple = [None,row[2],fetcher + "?context=%s&obid=%s&target=ob"%(usercontext,row[0])]
        try:
            dataTuple[0] = float(row[3])
        except ValueError:
            None
        dimensionData.append(dataTuple)
    displaymodulelogger.info(str(dimensionData))

    # only make output if we got any data
    myGraphHTML = ""
    if len([item for item in dimensionData if item[0] != None]) > 0:
        (myGraphName,myGraphMap) = makeBarGraph(imageDirectory=imagepath,datatuples=dimensionData,currenttuple=None,label1=graphtitle1,\
                                                        label2=graphtitle2,\
                                                        barwidth=barwidth)
        myGraphHTML= """
                        <tr>
                        <td colspan=2 align=center>
                        <p/>
                        <img src="%s%s" halign="center" usemap="#%s" border="0"/>
                        <p/>
                        %s
                        </td>
                        </tr>
                        """
        myGraphHTML = myGraphHTML%(tempimageurl,myGraphName,myGraphName.split('.')[0],myGraphMap)
        htmlWrapper = """
            <tr> <td colspan="2" class=tableheading> 
            %s
            </td>
            </tr>
            """%sectionheading           
        myGraphHTML = htmlWrapper + myGraphHTML

        
    return myGraphHTML



def getGenepixThumbnailDisplay(jpegfilename=None,usercontext="default", xy=("0","0"),fetcher=None, imagepath=None, tempimageurl=None, sectionheading=None,\
                         xyoffset=(0,0),thumbcount=3,thumbdimensions=(20,20),zoomincrement=50,pixelsize=10):
    """
    This procedure is attached to gene expression studies that use the Genepix GPR format, using a virtual
    function so that ir is called by the spot objects
    """

    # test code
    #mythumbs = getJPEGThumbs(imageDirectory=imagepath,filename=jpgfilename,xy=(150,150),xyoffset=(0,0),thumbcount=3)
    #mythumbs = getJPEGThumbs(imageDirectory=imagepath,filename=jpegfilename,xy=(int(xy[0]), int(xy[1])),xyoffset=xyoffset,pixelsize=pixelsize,\
    #                         thumbcount=3,thumbdimensions=thumbdimensions,zoomincrement=zoomincrement)
    try:
        mythumbs = getJPEGThumbs(imageDirectory=imagepath,filename=jpegfilename,xy=(int(xy[0]), int(xy[1])),xyoffset=xyoffset,pixelsize=pixelsize,\
                             thumbcount=3,thumbdimensions=thumbdimensions,zoomincrement=zoomincrement)
    except Exception, msg:
        myImageHTML = """
            <tr> <td colspan="2" class=tableheading> 
            %s
            </td>
            </tr>
            <tr> <td colspan="2">
            Error - unable to get thumbnail : %s
            </td>
            </tr>
            """%(sectionheading  , msg)
        return myImageHTML
    
    
    myImageHTML = """
                        <tr>
                        <td colspan=2 align=center>
                        <table>
                        <tr>
                        """
    for thumb in mythumbs:
        myImageHTML += '<td><img src="%s%s" halign="center" border="0"></td>'%(tempimageurl,thumb)

    myImageHTML += """
                        </tr>
                        </table>
                        </td>
                        </tr>    
    """
    htmlWrapper = """
            <tr> <td colspan="2" class=tableheading> 
            %s
            </td>
            </tr>
            """%sectionheading           
    myImageHTML = htmlWrapper + myImageHTML
    return myImageHTML


def getGenepixThumbnailDisplayTable(jpegfilenamelist=None,usercontext="default", experimentlist=None,xyrawdatarecordindex=5,microarrayspotfact=None,fetcher=None, imagepath=None, tempimageurl=None, sectionheading=None,\
                         xyoffsetlist=(0,0),thumbcount=3,thumbdimensions=(20,20),zoomincrement=50,pixelsizelist=None,columns=4):
    """
    This procedure is a mutiple image version of getGenepixThumbnailDisplay, to display a grid of spot images
    """

    

    if not (len(jpegfilenamelist) == len(xyoffsetlist)):
        raise brdfException("error - length mismatch in args to getGenepixThumbnailDisplayTable")


    # get the XY positions, using the list of experiments we have been given , the spot id and the index into the
    # raw data record ,where the XY position lives
    sql="""
        select
           ges.obid,
           mo.rawdatarecord,
           ges.xreflsid
        from
           geneexpressionstudy ges join microarrayobservation  mo on 
           mo.microarraystudy = ges.obid and 
           mo.microarrayspotfact = %(spot)s  
           """%{
               'spot' : microarrayspotfact
           }
    displaymodulelogger.info("executing %s"%sql)
    connection = databaseModule.getConnection()
    dataCursor = connection.cursor()
    dataCursor.execute(sql)
    rows = dataCursor.fetchall()
    #displaymodulelogger.info("getGenepixThumbnailDisplayTable : retrieved %s"%str(rows))
    xydict=dict(zip( [row[0] for row in rows],[re.split("\t",row[1])[5:7] for row in rows]))
    experimentnames = dict(zip( [row[0] for row in rows],[row[2] for row in rows]))
    connection.close()
    

    myImageHTML = """
                        <tr>
                        <td colspan=2 align=center>
                        <table border="yes">
                        """

    for imagecount in range(0,len(jpegfilenamelist)):
        if imagecount%columns == 0 :
            myImageHTML += "<tr>\n"              

        mythumbs = getJPEGThumbs(imageDirectory=imagepath,filename=jpegfilenamelist[imagecount],xy=(int(xydict[experimentlist[imagecount]][0]), int(xydict[experimentlist[imagecount]][1])),xyoffset=xyoffsetlist[imagecount],pixelsize=pixelsizelist[imagecount],\
                             thumbcount=3,thumbdimensions=thumbdimensions,zoomincrement=zoomincrement)
    
    

        myImageHTML += "<td valign=center><table><tr>"
        for thumb in mythumbs:
            myImageHTML += '<td halign="center" valign="center"><img src="%s%s" alt="%s" halign="center" valign="center" border="1"></td>'%(tempimageurl,thumb,experimentnames[experimentlist[imagecount]])
        myImageHTML += "</tr></table><br/>%s</td>"%experimentnames[experimentlist[imagecount]]

        if imagecount%columns == columns-1:
            myImageHTML += "</tr>\n"                



    # wrap up non rectangular tables
    if len(jpegfilenamelist)%columns != 0:
        for imagecount in range(len(jpegfilenamelist)%columns, columns):
            myImageHTML += "<td></td>"
        myImageHTML += "</tr>"
        
        

    
    myImageHTML += """
                        </table>
                        </td>
                        </tr>    
    """

    
    htmlWrapper = """
            <tr> <td colspan="2" class=tableheading> 
            %s
            </td>
            </tr>
            """%sectionheading           
    myImageHTML = htmlWrapper + myImageHTML
    return myImageHTML




def getSpotExpressionDisplay(obid=None, usercontext="default", fetcher=None, imagepath=None, tempimageurl=None, sectionheading=None,\
                         barwidth=10,displayNormalisedData= False):

    """ this method can be linked as a display procedure to objects such as genes and sequences"""    
    connection = databaseModule.getConnection()
    dataCursor = connection.cursor()


    # get the array type and lsid of the spot
    sql = """
        select
           d.datasourcetype,
           msf.xreflsid
        from
           ((microarrayspotfact msf join labresourceob lr
           on lr.obid = msf.labresourceob ) left outer join
           importfunction if on if.ob = lr.obid ) left outer join
           datasourceob d on d.obid = if.datasourceob
        where
           msf.obid = %s
           """%obid
    displaymodulelogger.info("executing %s"%str(sql))
    dataCursor.execute(sql)
    spotDetails  = dataCursor.fetchone()


    if spotDetails[0] in ['GALFile','AgResearchArrayExtract1','GALFile_noheader']:
        #sql = """
        #            select mo.gpr_logratio,
        #            mo.xreflsid,
        #            mo.obid,
        #            (mo.gpr_dye1foregroundmean + mo.gpr_dye2foregroundmean)/2.0 as averagefg
        #            from
        #            microarrayobservation mo 
        #            where
        #            microarrayspotfact = %s order by
        #mo.xreflsid"""%obid
        sql = """
                select
                mo.gpr_logratio,
                mo.xreflsid,
                mo.obid,
                (mo.gpr_dye1foregroundmean + mo.gpr_dye2foregroundmean)/2.0 as averagefg,
                ges.xreflsid as studylsid,
                substr(ges.studydescription,1,30) as studydescription
                from
                (geneexpressionstudy ges join microarrayobservation mo
                on
                ges.obid = mo.microarraystudy) left outer join geneexpressionstudyfact gesf on
                gesf.geneexpressionstudy = ges.obid and
                gesf.factnamespace = 'BRDF Default Interface Configuration' and
                gesf.attributename = 'Bar graph experiment order'
                where
                microarrayspotfact = %s order by
                to_number(gesf.attributevalue,'999999'), mo.xreflsid"""%obid
        displaymodulelogger.info("executing %s"%str(sql))
        dataCursor.execute(sql)
        datatuples = dataCursor.fetchall()
        displaymodulelogger.info("..done executing have data")



        observationids = [ item[2] for item in datatuples ]
        # each tuple contain a fetch URL - initialise this
        logratiodatatuples = [ (item[0],item[1], fetcher + "?context=%s&obid=%s&target=ob"%(usercontext,item[2])) \
                                    for item in datatuples ]

        myimagehtml = ""              
        if dataCursor.rowcount > 0:
            (myGraphName,myGraphMap) = makeBarGraph(imageDirectory=imagepath,datatuples=logratiodatatuples,currenttuple=None,label1="All raw LogRatios",label2="for this spot",barwidth=5)
            myGraphHTML= """
                            <tr>
                            <td colspan=2 align=left>
                            <p/>
                            <img src="%s%s" halign="left" usemap="#%s" border="0"/>
                            <p/>
                            %s
                            </td>
                            </tr>
                            """
            myGraphHTML = myGraphHTML%(tempimageurl,myGraphName,myGraphName.split('.')[0],myGraphMap)
            myimagehtml += """
                    <tr> <td colspan="2" class=tableheading> 
                    %s
                    </td>
                    </tr>
            """%sectionheading                    
            myimagehtml +=  myGraphHTML


            # graph the intensities
            intensitydatatuples = [ (int(item[3]),item[1], fetcher + "?context=%s&obid=%s&target=ob"%(usercontext,item[2])) \
                                    for item in datatuples ]
                        
            (myGraphName,myGraphMap) = makeBarGraph(imageDirectory=imagepath,datatuples=intensitydatatuples,currenttuple=None,label1="All average foreground",label2="intensities for this spot",barwidth=5)
            myGraphHTML= """
                            <tr>
                            <td colspan=2 align=left>
                            <p/>
                            <img src="%s%s" halign="left" usemap="#%s" border="0"/>
                            <p/>
                            %s
                            </td>
                            </tr>
            """
            myGraphHTML = myGraphHTML%(tempimageurl,myGraphName,myGraphName.split('.')[0],myGraphMap)
            myimagehtml +=  myGraphHTML




            # we now see whether there are any normalised values that we should graph.
            # the available normalised values are stored in an ontology called
            # MICROARRAY_NORMALISED_VALUES.
            if displayNormalisedData:
                sql = """
                        select otf.termName , otf.unitname from
                        ontologyob ot join ontologytermfact otf
                        on otf.ontologyob = ot.obid
                        where
                        ot.ontologyname = 'MICROARRAY_NORMALISED_VALUES'
                        order by otf.termName
                """
                displaymodulelogger.info("getting normalised data point names using %s"%sql)
                dataCursor.execute(sql)
                datapoints = dataCursor.fetchall()
                for (datapoint, datatype) in datapoints:
                    # obtain the data points - we re-use the above array of data tuples, since they
                    # contain the correct tooltips and urls - just change the data point value
                    skipdatapoint = False
                    for iobservation in range(0, len(observationids)):
                        sql = """
                                select case when attributeValue is null then '' else attributeValue end
                                from microarrayobservationfact
                                where
                                microarrayobservation = %s and
                                factNameSpace = 'NORMALISED VALUE' and
                                attributeName = '%s'
                        """%(observationids[iobservation],datapoint)
                        displaymodulelogger.info("getting normalised data points using %s"%sql)
                        dataCursor.execute(sql)
                        datapointvalue=dataCursor.fetchone()

                            
                        if dataCursor.rowcount == 1:
                            if len(datapointvalue[0]) == 0:
                                datatuples[iobservation] = \
                                            (None, datatuples[iobservation][1], logratiodatatuples[iobservation][2])   
                            else:
                                datatuples[iobservation] = \
                                            (float(datapointvalue[0]), datatuples[iobservation][1], logratiodatatuples[iobservation][2])   
                        else:
                            skipdatapoint = True
                            displaymodulelogger.info("skipping data point - query returned no rows")
                            break # we got nothing for this observation - incomplete dataset, give up
                                

                    # if all values missing, skip the whole data point
                    notMissing = [ datatuple[0] for datatuple in datatuples if datatuple[0] != None]
                    if len(notMissing) ==0:
                        skipdatapoint = True


                    if not skipdatapoint:
                        (myGraphName,myGraphMap) = makeBarGraph(imageDirectory=imagepath,datatuples=datatuples,currenttuple=None,label1="Normalisation:",label2=datapoint,barwidth=5)
                        myGraphHTML= """
                                    <tr>
                                       <td colspan=2 align=left>
                                       <p/>
                                           <img src="%s%s" halign="left" usemap="#%s" border="0"/>
                                       <p/>
                                       %s
                                       </td>
                                       </tr>
                                       """
                        myGraphHTML = myGraphHTML%(tempimageurl,myGraphName,myGraphName.split('.')[0],myGraphMap)
                        myimagehtml +=  myGraphHTML

            

            dataCursor.close()
            connection.close()


    elif re.search('(\.)*Affymetrix\.',spotDetails[1],re.IGNORECASE) != None:
        sql = """
        select
         mo.affy_meanpm,
         mo.affy_meanmm,
         mo.affy_stddevpm,
         mo.affy_stddevmm,
         mo.affy_count,
         mo.xreflsid,
         mo.obid
        from
        microarrayobservation mo 
        where
        microarrayspotfact = %s order by
        mo.xreflsid"""%obid
        displaymodulelogger.info("executing %s"%str(sql))
        dataCursor.execute(sql)
        datatuples = dataCursor.fetchall()
        displaymodulelogger.info("..done executing have data")


        observationids = [ item[6] for item in datatuples ]
        # each tuple contain a fetch URL - initialise this
        pmdatatuples = [ (item[0],item[5], fetcher + "?context=%s&obid=%s&target=ob"%(usercontext,item[6])) \
                            for item in datatuples ]
        #datatuples = [(item[0],item[1]) for item in datatuples]

        myimagehtml = ""                              
        if dataCursor.rowcount > 0:
            # PM means
            (myGraphName,myGraphMap) = makeBarGraph(imageDirectory=imagepath,datatuples=pmdatatuples,currenttuple=None,label1="All Probeset mean PM",label2="for this probeset",barwidth=5)
            myGraphHTML= """
                <tr>
                <td colspan=2 align=left>
                <p/>
                <img src="%s%s" halign="left" usemap="#%s" border="0"/>
                <p/>
                %s
                </td>
                </tr>
                """
            myGraphHTML = myGraphHTML%(tempimageurl,myGraphName,myGraphName.split('.')[0],myGraphMap)
            myimagehtml += """
            <tr> <td colspan="2" class=tableheading> 
            %s
            </td>
            </tr>
            """%sectionheading                   
            myimagehtml +=  myGraphHTML


            #PM standard deviations
            pmdatatuples = [ (item[2],item[5], fetcher + "?context=%s&obid=%s&target=ob"%(usercontext,item[6])) \
                            for item in datatuples ]                
            (myGraphName,myGraphMap) = makeBarGraph(imageDirectory=imagepath,datatuples=pmdatatuples,currenttuple=None,label1="All Probeset stddev PM",label2="for this probeset",barwidth=5)
            myGraphHTML= """
                <tr>
                <td colspan=2 align=left>
                <p/>
                <img src="%s%s" halign="left" usemap="#%s" border="0"/>
                <p/>
                %s
                </td>
                </tr>
                """
            myGraphHTML = myGraphHTML%(tempimageurl,myGraphName,myGraphName.split('.')[0],myGraphMap)               
            myimagehtml +=  myGraphHTML                

            dataCursor.close()
            connection.close()

    return myimagehtml




def getExpressionMapDisplay(obid=None, obtype='biosequenceob', usercontext="default", fetcher=None, imagepath=None, tempimageurl=None, sectionheading=None,\
                         barwidth=10,displayNormalisedData=False,graphTitle1="",graphTitle2=""):



        # see if there is any expression information available for which we can draw a map
        sql = """
        select          
            expressionmapname , 
            expressionmaplocus ,
            expressionamount
        from
            geneticexpressionfact
        where
            %s = %s
        order by
            expressionmapname
        """
        displaymodulelogger.info("executing %s"%sql%(obid,obtype))
        connection = databaseModule.getConnection()                                  
        expressionCursor=connection.cursor()
        expressionCursor.execute(sql%(obid,obtype))
        rows = expressionCursor.fetchall()
        expressionmaps={}
        for row in rows:
            if row[0] not in expressionmaps:
                expressionmaps[row[0]] = {}
            expressionmaps[row[0]].update( {
                row[1] : row[2]
            })
        displaymodulelogger.info("expression maps : %s"%str(expressionmaps))


        myimagehtml = ""
        # for each map , obtain map information including drawing instructions
        for expressionmap in expressionmaps.keys():
            sql = """
            select
               obid,
               attributevalue
            from
               ontologyob o join ontologyfact otf on
               o.ontologyname = %(mapname)s and

               otf.ontologyob = o.obid and
               otf.factnamespace = 'Display Settings' and
               otf.attributename = 'Expression Graph Type'
            """
            displaymodulelogger.info("executing %s"%sql%{ 'mapname' : expressionmap })
            expressionCursor.execute(sql,{ 'mapname' : expressionmap })
            rows = expressionCursor.fetchall()
            if expressionCursor.rowcount != 1:
                continue

            displaymodulelogger.info("Expression map info : %s"%str(rows))
            graphType = rows[0][1]

            # get the expression data
            sql = """
            select
               termname,
               termdescription,
               obid
            from
               ontologytermfact
            where
               ontologyob = %s
            """%rows[0][0]
            displaymodulelogger.info("executing %s"%sql)
            expressionCursor.execute(sql)
            rows = expressionCursor.fetchall()
            mapDomainDict = dict(zip( [row[0] for row in rows], [(row[1],row[2]) for row in rows] ) )
            displaymodulelogger.info("map domain :  %s"%str(mapDomainDict))

            # we only support a bar graph at the moment
            # prepare the arguments to the imageModule method for drawing a bar graph
            mapData=[]
            for mapDomainItem in mapDomainDict.keys():
                dataTuple = [0,mapDomainDict[mapDomainItem][0],fetcher + "?context=%s&obid=%s&target=ob"%(usercontext,mapDomainDict[mapDomainItem][1]),mapDomainItem]
                #displaymodulelogger.info("checking if %s in %s"%(mapDomainItem,str(expressionmap)))
                if mapDomainItem in expressionmaps[expressionmap]:
                    dataTuple[0] = expressionmaps[expressionmap][mapDomainItem]
                dataTuple = tuple(dataTuple)
                mapData.append(dataTuple)

            displaymodulelogger.info(str(mapData))
            #graphImageFile = makeBarGraph("c:/temp/",mapData,\
            #currenttuple=None,label1="Tissue Expression for",label2=self.databaseFields['sequencename'],\
            #barwidth=20,colourScheme=0)
            (myGraphName,myGraphMap) = makeBarGraph(imageDirectory=imagepath,datatuples=mapData,currenttuple=None,label1=graphTitle1,\
                                                    label2=graphTitle2,\
                                                    barwidth=20,colourScheme=0)
            myGraphHTML= """
                        <tr>
                        <td colspan=2 align=left>
                        <p/>
                        <img src="%s%s" halign="left" usemap="#%s" border="0"/>
                        <p/>
                        %s
                        </td>
                        </tr>
                        """
            myGraphHTML = myGraphHTML%(tempimageurl,myGraphName,myGraphName.split('.')[0],myGraphMap)

            myimagehtml += """
                <tr> <td colspan="2" class=tableheading> 
                %s
                </td>
                </tr>
            """%sectionheading                    
            myimagehtml +=  myGraphHTML


        return myimagehtml

def getAlleleFrequencyDisplay(genetictestfact=None, usercontext="default", fetcher=None, imagepath=None, tempimageurl=None, sectionheading=None,\
                         barwidth=60,graphTitle1="",graphTitle2="", sqltorun=None):

        if sqltorun == None:
            sql = """
            select
               genotypeobserved,
               count(*)
            from
               genotypeobservation
            where
               genetictestfact = %s
            group by
               genotypeobserved
            order by
               1
            """
        else:
            sql = sqltorun
        displaymodulelogger.info("executing %s"%(sql%genetictestfact))
        connection = databaseModule.getConnection()                                  
        genotypeCursor=connection.cursor()
        genotypeCursor.execute(sql%genetictestfact)
        alleles = [(item[1],"Count=%s"%item[1],"","  %s"%item[0]) for item in genotypeCursor.fetchall()]
        displaymodulelogger.info(str(alleles))
        (myGraphName,myGraphMap) = makeBarGraph(imageDirectory=imagepath,datatuples=alleles,currenttuple=None,label1=graphTitle1,\
                                                    label2=graphTitle2,\
                                                    barwidth=barwidth,colourScheme=None)
        myGraphHTML= """
                        <tr>
                        <td colspan=2 align=left>
                        <p/>
                        <img src="%s%s" halign="left" usemap="#%s" border="0"/>
                        <p/>
                        %s
                        </td>
                        </tr>
                        """
        myGraphHTML = myGraphHTML%(tempimageurl,myGraphName,myGraphName.split('.')[0],myGraphMap)

        myimagehtml = """
                <tr> <td colspan="2" class=tableheading> 
                %s
                </td>
                </tr>
            """%sectionheading                    
        myimagehtml +=  myGraphHTML


        return myimagehtml
    


def getSequenceAnnotationBundle(connection, obid=None, obtype='biosequenceob', usercontext="default", fetcher=None, imagepath=None, tempimageurl=None, \
                              panelTitle1="",panelTitle2="",panelFooter="",bundleType = "DBHITS,GO",databaseSearchList = None, topHits = 1, databaseQueryID = None,includeUserFlags = False, sqlBundleDict = None):
    """
    this display procedure is used to dynamically attach an annotation bundle to an object. The reasons for
    using dynamically  attached display procedures, rather than customising the myHTMLSummary method are :

    a) dynamic displays can be attached to any object - for example annotation could be attached to both an Affy target sequence
    , all its probes , and the original sequence. Or it could be attached to a genetic object.

    b) run-time performance can be improved because many of the lookups involved in attaching the bundle
    can be done at the time the bundle is attached, rather than at run-time. Those sequences with no
    annotation have no annotation display bundle attached and so do not incurr cost of looking up
    annotation that is not there.

    c) code is more modular , so that the same code that enhances the display of a sequence object
    can also be used to enhance the display of a gene object in (say) the sheepgenomics "gene index" view

    Disadvantages of using dynamically attached bundles are the additional maintenance involved in
    attaching them. Attaching these modules involves a distinct database procedure in the dbProcedures module.

    There are several different bundle types.

    1. Type 1 displays GO associations and top database hits. The arguments to this method
    include 
    
    * standard arguments obid=None, obtype='biosequenceob', usercontext="default", fetcher=None, imagepath=None, tempimageurl=None, \
                              panelTitle1="",panelTitle2=""
    * For the database top hits
       - a list of database search study ids
       - number of top hits to display
       - optionally, the query sequence to look up , to obtain the top hits

    * for the go associations....
    """

                             
    annotationCursor=connection.cursor()
    annotationHTML=""
    userflagDict = {}


    bundled = [item.strip().upper() for item in re.split(',',bundleType)]
    if 'DBHITS' in bundled:
        # if we are to display userFlags, then query the user flags ontology to get all the flags and their icons
        if includeUserFlags:
            sql = """
            select
               upper(termname),attributevalue,termdescription
            from
               (ontologytermfact otf join ontologyob o on
               o.xreflsid = 'ontology.DATABASESEARCHUSERFLAGS_ONTOLOGY' and
               otf.ontologyob = o.obid) join
               ontologytermfact2 otf2 on otf2.ontologytermid = otf.obid
            """
            annotationCursor.execute(sql)
            userflags  = annotationCursor.fetchall()
            if userflags != None:
                displaymodulelogger.info("userflags to use = %s"%str(userflags))
                userflagDict= dict([(item[0],(item[1],item[2])) for item in userflags])

        dbHitsHeading = panelTitle1
        if dbHitsHeading == None:
            dbHitsHeading = 'Database Search Results'
        annotationHTML+="""
        <TH colspan="2" style="BACKGROUND: silver ; color:white; font-size:16pt" align=left>Sequence Annotation : %s</TH></tr>
        """%dbHitsHeading        
        # process DB-HITS

        # for each database

        for searchid in databaseSearchList:
            
            # get any hits from this database
            querysequence = databaseQueryID
            if querysequence == None:
                querysequence = obid
            sql = """
            select
                dso.querysequence      , 
                dso.hitsequence        , 
                dso.queryxreflsid      , 
                dso.hitxreflsid        , 
                bs.sequencedescription     , 
                dso.hitlength          , 
                dso.hitevalue,
                bs.sequencename    ,
                dso.userflags           
            from
                databasesearchobservation dso join biosequenceob bs on
                bs.obid = dso.hitsequence
            where
                databasesearchstudy = %s and dso.querysequence = %s
            """
            displaymodulelogger.info("executing %s"%sql%(searchid, querysequence))

            annotationCursor.execute(sql%(searchid,querysequence))
            hits = annotationCursor.fetchall()            

            
                
            # for each obtain the database name, description 
            sql = """
            select
                databasename,
                databasedescription,
                databasetype,
                bd.obid 
            from
                biodatabaseob bd join databasesearchstudy ds on
                bd.obid = ds.biodatabaseob 
            where
                ds.obid = %s 
            """
            displaymodulelogger.info("executing %s"%(sql%searchid))
            connection = databaseModule.getConnection()                                  
            annotationCursor=connection.cursor()
            annotationCursor.execute(sql%searchid)
            databasedetails = annotationCursor.fetchall()
            displaymodulelogger.info("details : %s"%str(databasedetails))

            # get the URL to use for retrieving accessions
            sql = """
            select
                u.uristring 
            from
                (biodatabaseob bd join urilink ul on
                ul.ob = bd.obid ) join
                uriob u on u.obid = ul.uriob and
                u.xreflsid = bd.xreflsid||'.retrieveaccessionurl'
            where
                bd.obid = %s 
            """
            displaymodulelogger.info("executing %s"%(sql%databasedetails[0][3]))
            connection = databaseModule.getConnection()                                  
            annotationCursor=connection.cursor()
            annotationCursor.execute(sql%databasedetails[0][3])
            accessionretrievaldetails = annotationCursor.fetchall()

            # get the home URL
            sql = """
            select
                ul.iconpath,
                u.uristring,
                ul.iconattributes            
            from
                (biodatabaseob bd  join urilink ul on
                ul.ob = bd.obid ) join
                uriob u on u.obid = ul.uriob and
                u.xreflsid = bd.xreflsid||'.homeurl'
            where
                bd.obid = %s 
            """
            displaymodulelogger.info("executing %s"%(sql%databasedetails[0][3]))
            connection = databaseModule.getConnection()                                  
            annotationCursor=connection.cursor()
            annotationCursor.execute(sql%databasedetails[0][3])
            homedetails = annotationCursor.fetchall()           
            
            
            if len(homedetails) > 0:
                databaseHTML= """
                            <tr>
                            <td colspan=2 align=left>
                            <img src="%(displayurl)s" halign="right" border="0" usemap="#%(mapname)s" title="%(databasename)s : %(databasedescription)s"/>
                            <map name="%(mapname)s" id="%(mapname)s">
                            <area href="%(homeurl)s"
                            shape="rect"
                            coords="0,0,%(coords)s"
                            alt="%(databasename)s : %(databasedescription)s"
                            target = "%(databasename)s"/>
                            </map>
                            </td>
                            </tr>
                        """%({
                            'homeurl' : homedetails[0][1],
                            'mapname' : str(abs(hash(databasedetails[0][0]))),
                            'databasename' : databasedetails[0][0],
                            'databasedescription' : databasedetails[0][1],
                            'displayurl' : "%s"%(homedetails[0][0]),
                            'coords' : re.sub('\)','',re.sub('\(','',str(homedetails[0][2])))
                            })
            else:
                databaseHTML = """
                            <tr>
                            <td colspan=2 align=left>
                            <img src="%(displayurl)s" halign="right" border="0" width="100" height="50"/>
                            <b> %(databasename)s </b> :  %(databasedescription)s
                            </td>
                            </tr>                
                """%({
                            'databasename' : databasedetails[0][0],
                            'databasedescription' : databasedetails[0][1],
                            'displayurl' : "%s/%s"%(tempimageurl,'bioDatabase.jpg'),
                            })
            annotationHTML += databaseHTML

            displaymodulelogger.info("processing hits : %s"%str(hits))
            if len(hits) == 0:
                hitHTML = """
                        <tr>
                        <td colspan=2 align="left">
                        <pre>
                        * * * No hits found for this search * * *
                        </pre>
                        </td>
                        </tr>                
                """
                annotationHTML += hitHTML
                
            else:
                for hit in hits:
                    displayFields = {
                        'hitlink' : eval({True : '"""<a href="%s" target="%s %s"> %s </a>"""%((accessionretrievaldetails[0][0]%hit[7]),databasedetails[0][0],hit[7],hit[7])', False : 'hit[7]' }[len(accessionretrievaldetails) > 0]),
                        'hitdescription' : hit[4],
                        'hiteval' : hit[6],
                        'hitquery' : hit[2],
                        'userflags' : hit[8]
                    }

                    # go through an replace the userflags with their icons if available - if not we do not 
                    # even display them
                    if displayFields['userflags'] != None:
                        flags = re.split(',',displayFields['userflags'])
                        newText = ''
                        for flag in flags:
                            if flag.upper() in userflagDict: 
                                newText += '<img src=%s%s width=32 height=32 alt="%s" />'%( tempimageurl,userflagDict[ flag.upper()][0], userflagDict[ flag.upper()][1])
                            else:
                                newText += ""
                                #newText += "%s "%flag
                        displayFields['userflags'] = newText
                        displayFields['spacer'] = "<img src=%s%s width=30/>"%(tempimageurl,"space.gif")
                        
              
                    if displayFields['userflags'] == None:
                        hitHTML = """
                            <tr>
                            <td align=left>
                            %(hitlink)s
                            </td>
                            <td align=left>
                            %(hitdescription)s   (eval=%(hiteval)s)
                            </td>                        
                            </tr>
                            """%displayFields
                    else:
                        hitHTML = """
                            <tr>
                            <td align=left>
                            %(hitlink)s
                            </td>
                            <td align=left>
                            <table>
                            <tr>
                            <td> %(hitdescription)s   (eval=%(hiteval)s) </td>
                            <td align=right> %(spacer)s %(userflags)s </td>
                            </tr>
                            </table>
                            </td>
                            </tr>
                            """%displayFields


                    annotationHTML += hitHTML

    # handle GO bundled
    if 'GO' in bundled:
        annotationHTML+="""
        <TH colspan="2" style="BACKGROUND: silver ; color:white; font-size:16pt" align=left>Sequence Annotation : Gene Ontology</TH><tr>
        """        

            
        # get all the GO ontologies
        sql = """
                select
                    obid,
                    xreflsid,
                    ontologyname
                from
                    ontologyob
                where
                    upper(xreflsid) like '%%.GO.%%'
            """

        displaymodulelogger.info("executing %s"%sql)

        annotationCursor.execute(sql)
        ontologies = annotationCursor.fetchall()            

            
                
        # for each obtain the database name, description
        for ontology in ontologies:

            # get any hits from this database
            querysequence = databaseQueryID
            if querysequence == None:
                querysequence = obid
            sql = """
            select
                otf.termname      , 
                otf.termdescription   
            from
                predicatelink p join ontologytermfact otf on
                p.subjectob = %s and predicate = 'GO_ASSOCIATION' and p.objectob = otf.obid and
                otf.ontologyob = %s
                """
            displaymodulelogger.info("executing %s"%sql%(querysequence, ontology[0]))

            annotationCursor.execute(sql%(querysequence, ontology[0]))
            associations = annotationCursor.fetchall()                        

            # get the URL to use for retrieving accessions
            sql = """
            select
                u.uristring 
            from
                (ontologyob o join urilink ul on
                ul.ob = o.obid ) join
                uriob u on u.obid = ul.uriob and
                u.xreflsid = o.xreflsid||'.retrieveaccessionurl'
            where
                o.obid = %s 
            """
            displaymodulelogger.info("executing %s"%(sql%ontology[0]))
            connection = databaseModule.getConnection()                                  
            annotationCursor=connection.cursor()
            annotationCursor.execute(sql%ontology[0])
            accessionretrievaldetails = annotationCursor.fetchall()            

            # get the home URL
            sql = """
            select
                ul.iconpath,
                u.uristring,
                ul.iconattributes     
            from
                (ontologyob o join urilink ul on
                ul.ob = o.obid ) join
                uriob u on u.obid = ul.uriob and
                u.xreflsid = o.xreflsid||'.homeurl'
            where
                o.obid = %s 
            """
            displaymodulelogger.info("executing %s"%(sql%ontology[0]))
            connection = databaseModule.getConnection()                                  
            annotationCursor=connection.cursor()
            annotationCursor.execute(sql%ontology[0])
            homedetails = annotationCursor.fetchall()                        

            # construct the heading for this section            
            if len(homedetails) > 0:
                ontologyHTML= """
                            <tr>
                            <td colspan=2 align=left>
                            <img src="%(displayurl)s" halign="right" border="0" usemap="#%(mapname)s" title="%(ontologyname)s"/> <b> %(ontologyname)s </b>
                            <map name="%(mapname)s" id="%(mapname)s">
                            <area href="%(homeurl)s"
                            shape="rect"
                            coords="0,0,%(coords)s"
                            alt="%(ontologyname)s"
                            target = "%(ontologyname)s"/>
                            </map>
                            </td>
                            </tr>
                        """%({
                            'homeurl' : homedetails[0][1],
                            'mapname' : str(abs(hash(ontology[1]))),
                            'ontologyname' : ontology[2],
                            'displayurl' : "%s"%(homedetails[0][0]),
                            'coords' : re.sub('\)','',re.sub('\(','',str(homedetails[0][2])))
                            })
            else:
                ontologyHTML = """
                            <tr>
                            <td colspan=2 align=left>
                            <img src="%(displayurl)s" halign="right" border="0" width="100" height="50"/>
                            <b> %(ontologyname)s </b>
                            </td>
                            </tr>                
                """%({
                            'ontologyname' : ontology[2],
                            'displayurl' : "%s"%('bioDatabase.jpg'),
                            })
            annotationHTML += ontologyHTML
            #annotationHTML += databaseHTML

            displaymodulelogger.info("processing associations : %s"%str(hits))
            if len(associations) == 0:
                hitHTML = """
                        <tr>
                        <td colspan=2 align="left">
                        <pre>
                        * * * No associations found with this ontology * * *
                        </pre>
                        </td>
                        </tr>                
                """
                annotationHTML += hitHTML
                
            else:
                for association in associations:
                    displayFields = {
                        'associationlink' : eval({True : '"""<a href="%s" target="%s %s"> %s </a>"""%((accessionretrievaldetails[0][0]%association[0]),ontology[2],association[0],association[0])', False : 'association[0]' }[len(accessionretrievaldetails) > 0]),
                        'termdescription' : association[1]
                    }
              
                    hitHTML = """
                            <tr>
                            <td align=left>
                            %(associationlink)s
                            </td>
                            <td align=left>
                            %(termdescription)s
                            </td>                        
                            </tr>
                        """%displayFields
                    annotationHTML += hitHTML



    # handle a bundle that is simply the results of a SQL query that is passed in
    if 'SQL' in bundled:
        annotationHTML+="""
        <tr> <td colspan="2" class=tableheading>%s</td></tr>
        """%panelTitle1        


        sql = sqlBundleDict['sqlcode']
        displaymodulelogger.info("executing %s"%sql)
        annotationCursor.execute(sql)
        annotationRecords  = annotationCursor.fetchall()
        fieldNames = [item[0] for item in annotationCursor.description]

        recordHTML = ""
        if len(annotationRecords) > 0:
            displaymodulelogger.info("processing SQL bundle records")
            if len(annotationRecords) == 0:
                recordHTML = """
                        <tr>
                        <td colspan=2 align="left">
                        <pre>
                        * * * No Records Found * * *
                        </pre>
                        </td>
                        </tr>                
                """
                annotationHTML += recordHTML
                
            else:
                for record in annotationRecords:
                    recordHTML += """
                    <tr>
                    <td colspan=2 align=left/>
                    <table>
                    """

                    recordDict = dict(zip(fieldNames,record))
                    for field in fieldNames:
                        recordHTML += """
                            <tr>
                            <td class=fieldname align=left>
                            %s
                            </td>
                            <td align=left>
                            %s
                            </td>
                            </tr>
                        """%(field,recordDict[field])

                    recordHTML += """
                    </table>
                    </td>
                    </tr>
                    """
                annotationHTML += recordHTML
                if panelFooter != None:
                    annotationHTML += """
                        <tr> <td colspan="2" class=tableheading>%s</td></tr>
                        """%panelFooter
    
    annotationCursor.close()
    return annotationHTML


def getInlineTable(connection, obid=None, obtype='biosubjectob', usercontext="default", fetcher=None, imagepath=None, tempimageurl=None, \
                              panelTitle1="",panelTitle2="",panelFooter="",tableType = "SQL",sqlDict={},formatDict={}):
    """
    this display procedure is used to dynamically attach a table of information to an object. You can pass
    in HTML templates in formatDict['contextTemplate'] and formatDict['recordTemplate']  into which the results will
    be merged, using the convention that :

    within contextTemplate :
    
    __records__ will contain the results if interpolating the concatenated records

    within recordTemplate :
    
    __[group]col1__ __[group]col2__ etc will receive column names / data values from the SQL query.

    Where the the form groupcolN is used , then this will cause the
    row concerned to be output only for each new value of that variable, and also
    the code will attempt to interpolate a value into a variable __groupcount__ on the conclusion of each
    group.

    for example  :

<!-- would be part of contextTemplate -->
<table border cellspacing=0 cellpadding=5 rules=groups>
<!-- <table border cellspacing=0 cellpadding=5 rules=all>  -->
<!-- <table border cellspacing=0 cellpadding=5 rules=rows> -->
<caption align=bottom>Kumquat versus poked eye</caption> 
<thead>
   <tr>
      <td colspan=2 rowspan=2>
      <th colspan=2 align=center> Preference
   </tr>
   <tr>
      <th> Eating Kumquats </th>
      <th> Poke in the Eye </th>
   </tr>
</thead>
<tfoot>
   <tr>
      <td colspan=4 align=center>
      Note : eyepokes did not result in permanent injury
   </tr>
</tfoot>
<tbody>

<!-- from here would be part of record Template -->
   <tr align=center>
      <th rowspan=2> Gender
      <th> Male
      <td> 73%
      <td> 27%
   </tr>
   <tr align=center>
      <th> Female
      <td> 16%
      <td> 84%
   </tr>
<!-- end of record template -->

</tbody>
</table>    

    
    <th rowspan=2> Gender

    """

    
    tableHTML = ""
    if tableType == 'SQL':
        tableCursor = connection.cursor()
        
        tableHTML+="""
        <tr> <td colspan="2" class=tableheading>%s</td></tr>
        """%panelTitle1        


        sql = sqlDict['sqlcode']
        displaymodulelogger.info("executing %s"%sql)
        tableCursor.execute(sql)
        tableRecords  = tableCursor.fetchall()
        fieldNames = [item[0] for item in tableCursor.description]
        tableCursor.close()


        # assign default templates
        if 'contextTemplate' not in formatDict:
            contextTemplate = """
<table border cellspacing=0 cellpadding=3>
__heading__
__records__
</table>                
            """
            heading = """
            <tr>
            %s
            </tr>
            """%reduce(lambda x,y : x+"<td><b>%s</b></td>"%y, fieldNames,"")
            contextTemplate = re.sub("__heading__",heading,contextTemplate) 
        else:
            contextTemplate = formatDict["contextTemplate"]
            

        if "recordTemplate" not in formatDict:
            recordTemplate = """
            <tr>
            %s
            </tr>
            """%reduce(lambda x,y : x+"<td>__col%s__</td>"%y, range(1,len(fieldNames)+1),"")


        # process the context template
        contextHTML = contextTemplate
        for columnPatternPair in [("__col%s__"%i, fieldNames[i-1]) for i in range(1,len(fieldNames)+1)]:
            contextHTML = re.sub(columnPatternPair[0],columnPatternPair[1],contextHTML)

        lastRecord = None
        lastGroupCount = None
        currentGroupCount = 0
        recordsHTML = ""
        for record in tableRecords:
            recordHTML = copy.deepcopy(recordTemplate)
            for colIndex in range(1,len(fieldNames)+1):
                # bind standard column
                recordHTML = re.sub("__col%s__"%colIndex,{False : str(record[colIndex-1]), True : ''}[record[colIndex-1] == None], recordHTML)

                if re.search("__groupcol%s__"%colIndex,recordHTML) != None:
                    # process group descriptor, which indicated by __groupcolN__ pattern
                    # split text into lines - we only output a line containing a groupcol,
                    # at the start of the group
                    inlines = re.split("\n",recordHTML)
                    outlines = []
                    for line in inlines:
                        if re.search("__groupcol%s__"%colIndex,line) == None:
                            # output non-grouping markup lines
                            outlines.append(line)
                        else:
                            if lastRecord == None:
                                # first record  - output group markup
                                outlines.append(re.sub("__groupcol%s__"%colIndex,{False : str(record[colIndex-1]), True : ''}[record[colIndex-1] == None], line))
                                currentGroupCount += 1
                            else:
                                if record[colIndex-1] != lastRecord[colIndex-1]:
                                    # new group - output group markup
                                    outlines.append(re.sub("__groupcol%s__"%colIndex,{False : str(record[colIndex-1]), True : ''}[record[colIndex-1] == None], line))
                                    lastGroupCount = currentGroupCount
                                    currentGroupCount = 1
                                else:
                                    # same group - no markup
                                    currentGroupCount += 1

                    # rejoin the markup
                    recordHTML = string.join(outlines,"\n")

            # accumulate output and set any groupcount
            recordsHTML += recordHTML
            if lastGroupCount != None:
                recordsHTML = re.sub("__groupcount__",lastGroupCount,recordsHTML)
                lastGroupCount = None


        contextHTML = re.sub("__records__",recordsHTML,contextHTML)

        tableHTML+="""
        <tr> <td colspan="2" class=inlinetable>
        %s
        </td></tr>
        """%contextHTML
        
        if panelFooter != None:
            tableHTML += """
                    <tr> <td colspan="2" class=tableheading>%s</td></tr>
                    """%panelFooter
    
    return tableHTML



def getInlineURL(obid=None, obtype='biosequenceob', usercontext="default", fetcher=None, imagepath=None, tempimageurl=None, sectionheading=None,\
                         method="iframe",uristring = "",height=400,width=800, align="left", linkuri=None, slideinterval=5, imgheight=None, imgwidth=None):

    """this  method takes a URL and returns HTML which will result in the display of that URL in-line in a page.
    There are two methods :
    (1) iframe - the URL is simply wrapped in an iframe tag and the HTML returned
    (2) imagegrab - the URL (assumed to resolve to an image) is opened by the server and the bytestream read and
        cached. The HTML returned by this method contains a reference to the cached file.
    """
    # make list versions if necessary
    uristringList = uristring
    linkuriList = linkuri
    if isinstance(uristring,StringType):
        uristringList = [uristring]
        if linkuri != None:
            if isinstance(linkuri,StringType):
                linkuriList = len(uristringList) * [linkuri]
        else:
            linkuriList = len(uristringList) * [""]
    else:
        if linkuri != None:
            if isinstance(linkuri,StringType):
                linkuriList = len(uristringList) * [linkuri]
        else:
            linkuriList = len(uristringList) * [""]


    displaymodulelogger.info("uristringList : %s"%str(uristringList))


                
                
    resultHTML=""
    if method == 'iframe' :
        inlineHTML= """
                        <tr>
                        <td colspan=2 align=center>
                        <p/>
                        <iframe src="%(uristring)s" align="%(align)s" width="%(width)s" height="%(height)s"></iframe>
                        <p/>
                        </td>
                        </tr>
                        """
        inlineHTML = inlineHTML%{
            'uristring' : uristringList[0],
            'height' : height,
            'width' : width,
            'align' : align,
            'linkuri' : linkuriList[0],
        }

        if len(linkuriList[0]) < 5:
            resultHTML = """
                    <tr> <td colspan="2" class=tableheading> 
                    %(sectionheading)s
                    </td>
                    </tr>
                """%{
                'sectionheading' : sectionheading
                }
        else:
            resultHTML = """
                    <tr> <td colspan="2" class=tableheading> 
                    <a href="%(linkuri)s" target="inlinelink" > %(sectionheading)s </a>
                    </td>
                    </tr>
                """%{
                'sectionheading' : sectionheading,
                'linkuri' : linkuriList[0]
                }         
            
        resultHTML +=  inlineHTML
    elif method == 'img' :
        # get an id for the image element
        id = abs(hash(str(random.randint(1,10))))
        if len(linkuriList[0]) < 5:
            if imgheight == None or imgwidth == None:
                inlineHTML= """
                        <tr>
                        <td colspan=2 align=%(align)s>
                        <p/>
                        <img id="%(id)s" src="%(uristring)s" galleryimg="no"/>
                        <p/>
                        </td>
                        </tr>
                        """
            else:
                inlineHTML= """
                        <tr>
                        <td colspan=2 align=%(align)s>
                        <p/>
                        <img id="%(id)s" src="%(uristring)s" width="%(width)s height="%(height)s" galleryimg="no"/>
                        <p/>
                        </td>
                        </tr>
                        """
            inlineHTML = inlineHTML%{
               'uristring' : uristringList[0],
               'height' : imgheight,
               'width' : imgwidth,
               'align' : align,
               'linkuri' : linkuriList[0],
               'id' : id
            }
            resultHTML = """
                    <tr> <td colspan="2" class=tableheading>
                    %(sectionheading)s
                    </td>
                    </tr>
                """%{
                'sectionheading' : sectionheading
                }
        else:
            if imgwidth == None or imgheight == None:
                inlineHTML= """
                        <tr>
                        <td colspan=2 align=%(align)s>
                        <p/>
                        <a href="%(linkuri)s" title="%(sectionheading)s" target="inlinelink"> <img id="%(id)s" src="%(uristring)s galleryimg="no" border="0"> </a> 
                        <!-- <img src="%(uristring)s"/>  -->
                        <p/>
                        </td>
                        </tr>
                        """
            else:
                inlineHTML= """
                        <tr>
                        <td colspan=2 align=%(align)s>
                        <p/>
                        <a href="%(linkuri)s" title="%(sectionheading)s" target="inlinelink"> <img id="%(id)s" src="%(uristring)s  width="%(width)s height="%(height)s"  galleryimg="no" border="0"> </a>
                        <!-- <img src="%(uristring)s"/>  -->
                        <p/>
                        </td>
                        </tr>
                        """
                
            inlineHTML = inlineHTML%{
               'uristring' : uristringList[0],
               'height' : imgheight,
               'width' : imgwidth,
               'linkuri' : linkuriList[0],
               'align' : align,
               'sectionheading' : sectionheading,
               'id' : id
            }
            resultHTML = """
                    <tr> <td colspan="2" class=tableheading>
                    %(sectionheading)s 
                    </td>
                    </tr>
                """%{
                'sectionheading' : sectionheading,
                'linkuri' : linkuriList[0]
                }

        # if the array of images is > 0 then add Javascript to roll the images
        if len(uristringList) > 1:
            jsfragment = """
        <script type="text/javascript">
        var timer = %(slideinterval)s;

        var photos = %(photos)s;

        var img,count=1;

        function startSlideshow() {
           img = document.getElementById('%(id)s');
           window.setTimeout('cueNextSlide()',timer * 1000);
        }


        function cueNextSlide() {
           var next = new Image();

           next.onerror = function() {
              alert('Error loading image');
           };

           next.onload = function() {
              img.src = next.src;
              img.alt = photos[count][1];

              //img.width = next.width;
              //img.height = next.height;

              if (++count == photos.length) { count = 0; }
              window.setTimeout('cueNextSlide()', timer*1000);

            }

            next.src = photos[count][0];
        }

        function addLoadListener(fn){
            if(typeof window.addEventListener !='undefined')    window.addEventListener('load',fn,false);
            else if(typeof document.addEventListener !='undefined')    document.addEventListener('load',fn,false);
            else if(typeof window.attachEvent !='undefined')    window.attachEvent('onload',fn);
            else{
                var oldfn=window.onload
                if(typeof window.onload !='function')    window.onload=fn;
                else    window.onload=function(){oldfn();fn();}
            }
        }


        addLoadListener(startSlideshow); //does not work (object expected)
        //addLoadListener('startSlideshow()');  // does not work (object expected)
        //mmmmaddLoadListener(startSlideshow());  // does not work (object expected)
        </script>
        """%{
            'photos' : [list(item) for item in zip(uristringList,linkuriList)],
            'id' : id,
            'slideinterval' : slideinterval
            }
            resultHTML += jsfragment

        resultHTML +=  inlineHTML



    return resultHTML




    

def getGOTermPanelOrig(obid=None, obtype='biosequenceob', usercontext="default", fetcher=None, imagepath=None, tempimageurl=None, \
                              databaseLSID=None, panelTitle1="",panelTitle2=""):

    """ this method retuns markup to display hits from a given database search study """

        # see if there is any expression information available for which we can draw a map
    sql = """
        select          
            expressionmapname , 
            expressionmaplocus ,
            expressionamount
        from
            geneticexpressionfact
        where
            %s = %s
        order by
            expressionmapname
        """
    displaymodulelogger.info("executing %s"%sql%(obid,obtype))
    connection = databaseModule.getConnection()                                  
    expressionCursor=connection.cursor()
    expressionCursor.execute(sql%(obid,obtype))
    rows = expressionCursor.fetchall()
    expressionmaps={}
    for row in rows:
        if row[0] not in expressionmaps:
            expressionmaps[row[0]] = {}
        expressionmaps[row[0]].update( {
            row[1] : row[2]
        })
    displaymodulelogger.info("expression maps : %s"%str(expressionmaps))


    myimagehtml = ""
    # for each map , obtain map information including drawing instructions
    for expressionmap in expressionmaps.keys():
        sql = """
        select
            obid,
            attributevalue
        from
            ontologyob o join ontologyfact otf on
            o.ontologyname = %(mapname)s and

            otf.ontologyob = o.obid and
            otf.factnamespace = 'Display Settings' and
            otf.attributename = 'Expression Graph Type'
        """
        displaymodulelogger.info("executing %s"%sql%{ 'mapname' : expressionmap })
        expressionCursor.execute(sql,{ 'mapname' : expressionmap })
        rows = expressionCursor.fetchall()
        if expressionCursor.rowcount != 1:
            continue

        displaymodulelogger.info("Expression map info : %s"%str(rows))
        graphType = rows[0][1]

        # get the expression data
        sql = """
            select
               termname,
               termdescription,
               obid
            from
               ontologytermfact
            where
               ontologyob = %s
            """%rows[0][0]
        displaymodulelogger.info("executing %s"%sql)
        expressionCursor.execute(sql)
        rows = expressionCursor.fetchall()
        mapDomainDict = dict(zip( [row[0] for row in rows], [(row[1],row[2]) for row in rows] ) )
        displaymodulelogger.info("map domain :  %s"%str(mapDomainDict))

        # we only support a bar graph at the moment
        # prepare the arguments to the imageModule method for drawing a bar graph
        mapData=[]
        for mapDomainItem in mapDomainDict.keys():
            dataTuple = [0,mapDomainDict[mapDomainItem][0],fetcher + "?context=%s&obid=%s&target=ob"%(usercontext,mapDomainDict[mapDomainItem][1]),mapDomainItem]
            #displaymodulelogger.info("checking if %s in %s"%(mapDomainItem,str(expressionmap)))
            if mapDomainItem in expressionmaps[expressionmap]:
                 dataTuple[0] = expressionmaps[expressionmap][mapDomainItem]
            dataTuple = tuple(dataTuple)
            mapData.append(dataTuple)

        displaymodulelogger.info(str(mapData))
        #graphImageFile = makeBarGraph("c:/temp/",mapData,\
        #currenttuple=None,label1="Tissue Expression for",label2=self.databaseFields['sequencename'],\
        #barwidth=20,colourScheme=0)
        (myGraphName,myGraphMap) = makeBarGraph(imageDirectory=imagepath,datatuples=mapData,currenttuple=None,label1=graphTitle1,\
                                                    label2=graphTitle2,\
                                                    barwidth=20,colourScheme=0)
        myGraphHTML= """
                        <tr>
                        <td colspan=2 align=left>
                        <p/>
                        <img src="%s%s" halign="left" usemap="#%s" border="0"/>
                        <p/>
                        %s
                        </td>
                        </tr>
                    """
        myGraphHTML = myGraphHTML%(tempimageurl,myGraphName,myGraphName.split('.')[0],myGraphMap)

        myimagehtml += """
                <tr> <td colspan="2" class=tableheading> 
                %s
                </td>
                </tr>
            """%sectionheading                    
        myimagehtml +=  myGraphHTML


    return myimagehtml


def TestgetSequenceTraceViewPanel(connection, obid=None, obtype='biosequenceob', usercontext="default", fetcher=None, imagepath=None, tempimageurl=None, \
         sectionheading=None, method = "traceviewer.sh", width = 800 , height = 400):
    """
    this method calls a script on a server which creates a png image of a traceview. It then
    returns an in-line frame referring to the newly created image file, so that the
    trace view is scrollable. The underlying Perl script is called (e.g.) as follows :
    

Usage: perl $0 -h 400 -f 1188_13_14728111_16654_48544_080.ab1 -o test2.png
or perl $0 --height 400 --file 1188_13_14728111_16654_48544_080.ab1 --out test2.png

Options:
--height <pixels> Set height of image (${\HEIGHT} pixels default)
--file <trace file-name> Filename for the ABI trace file
--out <output file-name> Filename for the generated .png image
    
    """


    # !!!!! test code only !!!!! :
    tempimagefile = "test.png"    


    # call teh shell script that creates the image








    resultHTML = """
                    <tr>
                    <td colspan="2" class=tableheading> 
                    %(sectionheading)s
                    </td>
                    </tr>
                """%{
                'sectionheading' : sectionheading
                }


    inlineHTML= """
                        <tr>
                        <td colspan=2 align=center>
                        <p/>
                        <iframe src="%(tempimageurl)s%(tempimagefile)s" align="center" width="%(width)s" height="%(height)s"></iframe>
                        <p/>
                        </td>
                        </tr>
                """
    inlineHTML = inlineHTML%{
                'tempimageurl' : tempimageurl,
               'tempimagefile' : tempimagefile,
               'height' : height + 40,
               'width' : width,
               'sectionheading' : sectionheading
    }

    resultHTML += inlineHTMLace
    return resultHTML


# updated 6/2009 to support zip archive where there is no infile.
def getSequenceTraceViewPanel(connection, obid=None, obtype='biosequenceob', usercontext="default", fetcher=None, imagepath=None, tempimageurl=None, sectionheading=None,\
                         shellscript = "./traceviewer.sh", graphicsprog = './traceviewer.pl', displayFunction = None, height = 200, width=800 , left = None, right = None, size = None, extractpath='/tmp'):
    """
    this method calls a script on a server which creates a png image of a traceview. It then
    returns an in-line frame referring to the newly created image file, so that the
    trace view is scrollable.
    
    The method is passed the displayFunction tuple which includes the following fields :

    
            df.invocation,
            df.functioncomment,
            dp.xreflsid,
            dp.procedurename,
            ds.datasourcename,
            ds.physicalsourceuri,
            ds.datasourcetype,
            df.voptypeid,
            dp.proceduredescription,
            df.invocationorder,
            df.obid,
            ds.obid

    """

    infile = displayFunction[5]

    if infile == None:
        if displayFunction[11] != None:
            # if the infile does not exist then attempt to marshall it from the datasource if that exists and is of the correct type

            from dataImportModule import dataSourceOb
            
            datasource = dataSourceOb()
            displaymodulelogger.info("initialising datasource using id %s"%displayFunction[11])
            datasource.initFromDatabase(displayFunction[11], connection)

            newtracefile = False
            tracefilepath = os.path.join(extractpath, datasource.databaseFields['datasourcename'])    
            if re.search("Executable", datasource.databaseFields['datasourcetype'], re.IGNORECASE ) != None:

                # see if we need to get the file
                infile = tracefilepath

                if not os.path.exists(tracefilepath) :
                    
                    displaymodulelogger.info("executing datasource for %s"%tracefilepath) 
                    (status, output) = datasource.execute(connection, format=None, outfile = None)
                    if status != 0:
                        raise brdfException("Error code %s returned from execute of %s"%(status, datasource.databaseFields['datasourcecontent']))            
                    displaymodulelogger.info("writing %s"%tracefilepath)   
                    file = open(tracefilepath,"w")
                    file.write(output)
                    file.close()
                    newtracefile = True
            else:
                raise brdfException("unsupported datasource type in getSequenceTraceViewPanel")
        else:
            raise brdfException("no tracefile of tracefile archive specification is available")
            
            
    
        
    outfolder = imagepath
    outfilename = "%s.png"%abs(hash(infile))
    height = height 
    left = left
    right = right
    graphicsprog = './traceviewer.pl'

    cmd = '/bin/sh %(shellscript)s  %(infile)s %(outfolder)s %(outfilename)s %(height)s %(left)s %(right)s %(size)s %(graphicsprog)s'%{
       'infile' : infile,
       'outfolder' : outfolder,
       'outfilename' : outfilename,
       'height' : height,
       'left' : left,
       'right' : right,
       'size' : size,
       'graphicsprog' : graphicsprog,
       'shellscript' : shellscript
    }

    displaymodulelogger.info("getSequenceTraceViewPanel is executing %s"%cmd)
    status, output = commands.getstatusoutput(cmd)
    displaymodulelogger.info("Output: %s"%output)
    displaymodulelogger.info("Status: %s"%status)


    tempimagefile = output.strip()    

    if re.search('^ERROR',tempimagefile) != None:
        resultHTML="""
                    <tr>
                    <td colspan="2" class=tableheading>
                    %s
                    </td>
                    </tr>
        """%tempimagefile
    else:
        resultHTML = """
                    <tr>
                    <td colspan="2" class=tableheading> 
                    %(sectionheading)s
                    </td>
                    </tr>
                """%{
                'sectionheading' : sectionheading
                }


        inlineHTML= """
                        <tr>
                        <td colspan=2 align=center>
                        <p/>
                        <iframe src="%(tempimageurl)s%(tempimagefile)s" align="center" width="%(width)s" height="%(height)s"></iframe>
                        <p/>
                        </td>
                        </tr>
                """
        inlineHTML = inlineHTML%{
                'tempimageurl' : tempimageurl,
               'tempimagefile' : tempimagefile,
               'height' : height + 40,
               'width' : width,
               'sectionheading' : sectionheading
        }

        resultHTML += inlineHTML


    return resultHTML


def getContigAlignmentViewPanel(connection, obid=None, obtype='biosequenceob', usercontext="default", fetcher=None, imagepath=None, tempimageurl=None, extractpath = '/tmp', sectionheading=None,\
                         shellscript = "./contigviewer.sh", contigid = "Contig1", displayFunction = None, fontsize=10, height = 200, width=800 , left = None, right = None, size = None):
    """
    this method calls a script on a server which creates resources required for
    a DHTML contig view page - e.g. including two images and Javascript code
    to support multiple views.

    ACE files are usually stored in zip files. Each zip file is defined as a datasource.

    The association between these data sources and the contigs for which the display is to be made ,
    is provided by the entries in the display function table.
    
    The method is passed the displayFunction tuple which includes the following fields :

            df.invocation,
            df.functioncomment,
            dp.xreflsid,
            dp.procedurename,
            ds.datasourcename,
            ds.physicalsourceuri,
            ds.datasourcetype,
            df.voptypeid,
            dp.proceduredescription,
            df.invocationorder,
            df.obid,
            ds.obid



    example of calling the current script :

    
    
    """

    # get an instance of the datasource - if it is executable then we can just execute it to marshall the required files

    from dataImportModule import dataSourceOb
    
    datasource = dataSourceOb()
    displaymodulelogger.info("initialising datasource using id %s"%displayFunction[11])
    datasource.initFromDatabase(displayFunction[11], connection)

    newacefile = False
    acefilepath = os.path.join(extractpath, datasource.databaseFields['datasourcename'])    
    if re.search("Executable",datasource.databaseFields['datasourcetype']) != None:

        # see if we need to get the file    
        if not os.path.exists(acefilepath) :
            
            displaymodulelogger.info("executing datasource for %s"%acefilepath) 
            (status, output) = datasource.execute(connection, format=None, outfile = None)
            if status != 0:
                resultHTML = """
                <tr>
                <td>
                Error code %s returned from execute of %s
                </td>
                </tr>
                """%(status, datasource.databaseFields['datasourcecontent'])
                # changed 14/9/2012 - don't want to throw an exception 
                #raise brdfException("Error code %s returned from execute of %s"%(status, datasource.databaseFields['datasourcecontent']))            
            displaymodulelogger.info("writing %s"%acefilepath)   
            file = open(acefilepath,"w")
            file.write(output)
            file.close()
            newacefile = True        
    else:
        # may do something along these lines....
        #marshallDataSource(datasourceob = displayFunction[10], targetfolder='/tmp', targetfilename = 'CLP0008090528-cF4_20030121.ace', uncompress=True, bin="/usr/bin", sourcefilename='seqdata/forage/LP/C/Seqdata/0008/090/ace/edit_dir/CLP0008090528-cF4_20030121.ace')
        raise brdfException("unsupported datasource type in getContigAlignmentViewPanel")       

    # calculate an image name
    hashConstant = '0'
    outfolder = imagepath
    filebasename = str(abs(hash(acefilepath + hashConstant + str(obid) + str(height) + str(width) + str(displayFunction))))

    
    outfilename1 = "%s.png"%str(abs(hash(acefilepath + hashConstant + str(obid) + str(height) + str(width) + str(displayFunction))))
    outfilename2 = "%s_diff.png"%str(abs(hash(acefilepath + hashConstant + str(obid) + str(height) + str(width) + str(displayFunction))))
    iframefile = "%s.php"%str(abs(hash(acefilepath + hashConstant + str(obid) + str(height) + str(width) + str(displayFunction))))
    urlsfile = "%s.list"%str(abs(hash(acefilepath + hashConstant + str(obid) + str(height) + str(width) + str(displayFunction))))

    outpath1 = os.path.join(imagepath,outfilename1)
    outpath2 = os.path.join(imagepath,outfilename2)
    iframepath = os.path.join(imagepath,iframefile)
    urlspath = os.path.join(imagepath,urlsfile)

    # the urlsfile is not currently used - but the script needs it
    if not os.path.exists(urlspath):
        file=open(urlspath,"w")
        file.write("")
        file.close()
 


    cmd = '/bin/sh %(shellscript)s  %(infile)s %(outfilename1)s %(outfilename2)s %(fontsize)s %(iframepath)s %(urlspath)s %(contigid)s'%{
       'shellscript' : shellscript,
       'infile' : acefilepath,
       'outfilename1' : outpath1,
       'outfilename2' : outpath2,
       'fontsize' : fontsize,
       'contigid' : contigid,
       'iframepath' : iframepath,
       'urlspath' : urlspath
    }

    displaymodulelogger.info("getContigAlignmentViewPanel is executing %s"%cmd)
    status, output = commands.getstatusoutput(cmd)
    displaymodulelogger.info("Output: %s"%output)
    displaymodulelogger.info("Status: %s"%status)


    tempimagefiles = output.strip()    

    if re.search('^ERROR',tempimagefiles) != None:
        resultHTML="""
                    <tr>
                    <td colspan="2" class=tableheading>
                    %s
                    </td>
                    </tr>
        """%tempimagefiles
    else:
        resultHTML = """
                    <tr>
                    <td colspan="2" class=tableheading> 
                    %(sectionheading)s
                    </td>
                    </tr>
                """%{
                'sectionheading' : sectionheading
                }


        inlineHTML= """
                        <tr>
                        <td colspan=2 align=center>
                        <p/>
                        <iframe src="%(tempimageurl)s%(outfilename2)s" align="center" width="%(width)s" height="%(height)s"></iframe>
                        <p/>
                        </td>
                        </tr>
                        <tr>
                        <td colspan=2 align=center>
                        <p/>
                        <iframe src="%(tempimageurl)s%(outfilename1)s" align="center" width="%(width)s" height="%(height)s"></iframe>
                        <p/>
                        </td>
                        </tr>                        
                """
        inlineHTML = inlineHTML%{
               'tempimageurl' : tempimageurl,
               'outfilename1' : outfilename1,
               'outfilename2' : outfilename2,
               'height' : height + 40,
               'width' : width,
               'sectionheading' : sectionheading
        }

        resultHTML += inlineHTML


    return resultHTML






def getGraphicFeaturePanel(connection, obid=None, obtype='biosequenceob', referencelength = 0, usercontext="default", fetcher=None, imagepath=None, tempimageurl=None, \
                              sectionheading="",shellscript = "./featureviewer.sh", graphicsprog = './featureviewer.pl', displayFunction = None,\
                           panelType = "DEFAULT",includeDatabaseSearchList = None,excludeDatabaseSearchList=None,\
                           maxhitcount=5,includefeatureTypes=None,excludeFeatureTypes=None,\
                           width=700,height=300,align="left"):

    """ this method will create a graphical feature image using features from the given reference sequence, and will
    return HTML to display the feature. Here is an example of the input format required by the external process

[general]
bases = 1..1734
height = 12
glyph = segments
connector = dashed
description = 1
font2color = gray
label = 1
stranded  = 1

[genomic_DNA]
bgcolor = blue
key = Genomic DNA

[READ]
bgcolor = pink

[promoter]
bgcolor = yellow
key = Promoter Regions

[STS]
glyph = diamond
bgcolor = brown
ket = STS

[TATA_signal]
glyph = transcript2
bgcolor = orange
key = TATA Signals

[BLASTN_ag_est]
bgcolor = lime
key = Blast against AgR ESTs


[BLASTN_nt]
bgcolor= red
key = Blast against nt

genomic_DNA	CTR0036000916-cF5_20040726	+	1-1734
promoter	promoter	+	827-1116
STS	STS1	.	1440-1440 first
STS	STS2	.	1510-1510 second
STS	STS3	.	1525-1525 third
STS	STS4	.	1545-1545
STS	STS5	.	1558-1558
STS	STS6	.	1605-1605
TATA_signal	TATA_signal	+	1083-1083
READ	FTRC101558B12-g0RSP_20030602	+	1-730
READ	FTRC101558B12-b0FSP_20030602	-	632-1314
READ	FTRC001007E03-b0FSP_20020423	-	1168-1655
READ	FTRC101471K11-g0RSP_20030127	+	784-1374
READ	FTRC101471K11-b0FSP_20030127	-	1192-1735
BLASTN_nt	gb|AC152053.34|	-	1218-1260	"M truncatula clone mth2-35e5; score: 61.9"
BLASTN_nt	gb|AC171267.17|	+	1218-1260	"M truncatula clone mth2-17i7; score: 61.9"
BLASTN_nt	gb|AC157779.22|	+	1206-1258	"M truncatula chromosome 6 clone mth2-156d20; score: 58"
BLASTN_nt	emb|CU137665.1|	+	1218-1266	"M truncatula chromosome 5 clone mth2-152c15; score: 58"
BLASTN_nt	emb|CR932963.2|	+	1218-1266	"M truncatula chromosome 5 clone mth2-115p22; score: 58"
BLASTN_nt	emb|CU302344.1|	+	1218-1260	"M truncatula chromosome 5 clone mte1-12c12; score: 54"
BLASTN_nt	gb|AC148775.2|	+	1218-1260	"M truncatula chromosome 2 clone mth2-62i21; score: 54"
BLASTN_nt	gb|CP000260.1|	+	1305-1342	"S pyogenes MGAS10270; score: 52"
BLASTN_ag_est	00082906WCC3A51WX1	-	1204-1266	"score: 117"
BLASTN_ag_est	99110402WCH4061GXX	-	1206-1276	"score: 101"
BLASTN_ag_est	00121416WCD62EE1I2	+	1206-1258	"score: 89.7"

    The method is passed the displayFunction tuple which includes the following fields :

            df.invocation,
            df.functioncomment,
            dp.xreflsid,
            dp.procedurename,
            ds.datasourcename,
            ds.physicalsourceuri,
            ds.datasourcetype,
            df.voptypeid,
            dp.proceduredescription,
            df.invocationorder,
            df.obid,
            ds.obid



generic  a rectangle 
arrow an arrow 
diamond a point-like feature represented as a triangle 
segments a multi-segmented feature such as an alignment 
triangle a point-like feature represented as a diamond 
transcript a gene model 
transcript2 a slightly different representation of a gene model 


    """


    ######### fist we need to marshall the featuers and blast hits into a gff file ############

    featureCursor=connection.cursor()

    # get more sequence details
    sql = """
    select xreflsid from biosequenceob where obid = %(obid)s
    """
    displaymodulelogger.info("executing %s"%(sql%{'obid' : obid}))
    featureCursor.execute(sql,{'obid' : obid})
    referencelsid = featureCursor.fetchone()[0]


    seqdatapacket = """
[general]
bases = 1..%s
height = 12
glyph = generic
connector = dashed
description = 1
font2color = gray
label = 1
stranded  = 1

[reference]
bgcolor = blue
key = %s


"""%(referencelength,referencelsid)
#[blast]
#bgcolor = lime
#key = blast



    featkeypacket = ""
    featkeypacketdict = {}    
    featdatapacket = ""
    resultHTML = """
                    <tr>
                    <td colspan="2" class=tableheading> 
                    %(sectionheading)s
                    </td>
                    </tr>
                """%{
                'sectionheading' : sectionheading
                }    

    sql = """
    select
        bsf.obid,
        bsf.biosequenceob,
        b.xreflsid,
        b.seqlength,
        bsf.featuretype,
        CASE WHEN bsf.featurestrand = -1 THEN '-'
        WHEN bsf.featurestrand = +1 THEN '+'
        ELSE '.' END as "featurestrand",
        bsf.featurestart,
        bsf.featurestop,
        bsf.featurecomment,
        bsf.evidence,
        bsf.featurelength,
        CASE WHEN bsf.featureaccession is null then
        bsf.featuretype ELSE bsf.featureaccession END as "featureaccession"
        
    from
        biosequencefeaturefact bsf join biosequenceob b on
        b.obid = %(obid)s and 
        bsf.biosequenceob = b.obid
    order by
        featurestart,
        featurestrand,
        featuretype"""

    displaymodulelogger.info("executing %s"%(sql%{'obid' : obid}))     

    featureCursor.execute(sql,{'obid' : obid})
    features = featureCursor.fetchall()
    fieldNames = [item[0].lower() for item in featureCursor.description]
    rowcount=0

    # get a color scheme
    colourScheme = getColourScheme(200) # we will not need this many - this is an upper bound
    for feature in features:
        rowcount += 1
        featDict = dict(zip(fieldNames, feature))

        if featDict['featuretype'] not in featkeypacketdict:
           # work out what glyph to use. This will need some customisation
           glyph='generic'
           glyphsize=""
           if abs(featDict['featurestop'] - featDict['featurestart']) < 2:
              glyph = 'triangle'
              glyphsize = 'point = 1'
           elif abs(featDict['featurestop'] - featDict['featurestart']) < 5:
              glyph = 'diamond'
              glyphsize = 'point = 1'
           else:
              glyph = 'segments'
               
           featDict.update({
              'glyph' : glyph,
              'glyphsize' : glyphsize,
              'bgcolor' : "#%02x%02x%02x"%colourScheme[abs(hash(featDict['featuretype']))%len(colourScheme)]
           }) 

           featkeypacketdict[ featDict['featuretype'] ] = """
[%(featuretype)s]
glyph = %(glyph)s
bgcolor = %(bgcolor)s
key = %(featuretype)s        
%(glyphsize)s
        """%featDict

           featkeypacket += featkeypacketdict[ featDict['featuretype'] ]

        featdatapacket += """
%(featuretype)s\t%(featureaccession)s\t%(featurestrand)s\t%(featurestart)s-%(featurestop)s
        """%featDict        



    # get blast hits - query centric
    # BLASTN_nt       gb|AC152053.34| -       1218-1260       "M truncatula clone mth2-35e5; score: 61.9"
    # BLASTN_nt       gb|AC171267.17| +       1218-1260       "M truncatula clone mth2-17i7; score: 61.9"
    sql = """
            select
                bs.sequencedescription     ,
                bs.sequencename,
                bs.xreflsid,
                dso.hitlength          ,
                dso.hitevalue,
                s.score,
                s.queryfrom,
                s.queryto,
                CASE WHEN s.hitstrand > 0 and s.hitstrand is not null then '+'
                WHEN s.hitstrand < 0 and s.hitstrand is not null then '-'
                WHEN s.queryframe < 0 and s.hitstrand is null THEN '-'
                WHEN s.queryframe > 0 and s.hitstrand is null THEN '+'
                ELSE '.' END as "featurestrand",
                CASE WHEN bd.databasetype = 'Protein Sequence database' then 'protein_hit'
                WHEN bd.databasetype = 'Nucleotide Sequence database' then 'nucleotide_hit'
                ELSE 'nucleotide_hit' END as "hittype",
                dso.databasesearchstudy
            from
                (((databasesearchobservation dso join biosequenceob bs
                on bs.obid = dso.hitsequence and dso.querysequence = %s) join sequencealignmentfact s on
                s.databasesearchobservation = dso.obid) join databasesearchstudy ds on
                ds.obid = dso.databasesearchstudy ) join biodatabaseob bd on bd.obid = ds.biodatabaseob
            order by 
                dso.hitevalue 
            """
    displaymodulelogger.info("executing %s"%(sql%obid))

    featureCursor.execute(sql%obid)
    hits = featureCursor.fetchall()
    hitcount = len(hits)
    fieldNames = [item[0].lower() for item in featureCursor.description]
    displaymodulelogger.info("retrieved %s query-centric alignments"%len(hits))


    hitdatapacket = ""
    nucleotidehits = False
    proteinhits = False

    for hit in hits:
        hitDict = dict(zip(fieldNames,hit))

        # filter includes and excludes
        # filter includes and excludes
        displaymodulelogger.info("checking %s in exclude list %s"%(hitDict['databasesearchstudy'], str(excludeDatabaseSearchList)))
        if excludeDatabaseSearchList != None:
            if hitDict['databasesearchstudy'] in excludeDatabaseSearchList:
                continue
        displaymodulelogger.info("checking %s in include list %s"%(hitDict['databasesearchstudy'], str(includeDatabaseSearchList)))
        if includeDatabaseSearchList != None:
            if len(includeDatabaseSearchList) > 0:
                if hitDict['databasesearchstudy'] not in includeDatabaseSearchList:
                    continue


        if hitDict["hittype"] == "nucleotide_hit":
            nucleotidehits = True
        elif hitDict["hittype"] == "protein_hit":
            proteinhits = True

    
        # BLASTN_nt       gb|AC152053.34| -       1218-1260       "M truncatula clone mth2-35e5; score: 61.9"
        hitdatapacket += """
%(hittype)s\t%(sequencename)s\t%(featurestrand)s\t%(queryfrom)s-%(queryto)s\t"%(xreflsid)s; score %(score)s ; evalue %(hitevalue)s;"
        """%hitDict


    # get blast hits - hit centric
    # BLASTN_nt       gb|AC152053.34| -       1218-1260       "M truncatula clone mth2-35e5; score: 61.9"
    # BLASTN_nt       gb|AC171267.17| +       1218-1260       "M truncatula clone mth2-17i7; score: 61.9"
    sql = """
            select
                bs.sequencedescription     ,
                bs.sequencename,
                bs.xreflsid,
                dso.hitevalue,
                s.score,
                s.hitfrom as queryfrom,
                s.hitto as queryto,
                CASE WHEN s.hitstrand > 0 and s.hitstrand is not null then '+'
                WHEN s.hitstrand < 0 and s.hitstrand is not null then '-'
                WHEN s.queryframe < 0 and s.hitstrand is null THEN '-'
                WHEN s.queryframe > 0 and s.hitstrand is null THEN '+'
                ELSE '.' END as "featurestrand",
                CASE WHEN bd.databasetype = 'Protein Sequence database' then 'protein_hit'
                WHEN bd.databasetype = 'Nucleotide Sequence database' then 'nucleotide_hit'
                ELSE 'nucleotide_hit' END as "hittype",
                dso.databasesearchstudy
            from
                (((databasesearchobservation dso join biosequenceob bs
                on bs.obid = dso.querysequence and dso.hitsequence = %s) join sequencealignmentfact s on
                s.databasesearchobservation = dso.obid) join databasesearchstudy ds on
                ds.obid = dso.databasesearchstudy ) join biodatabaseob bd on bd.obid = ds.biodatabaseob
            order by
                dso.hitevalue 
            """
    displaymodulelogger.info("executing %s"%(sql%obid))

    featureCursor.execute(sql%obid)
    hits = featureCursor.fetchall()
    hitcount += len(hits)

    fieldNames = [item[0].lower() for item in featureCursor.description]
    displaymodulelogger.info("retrieved %s hit centric alignments"%len(hits))


    for hit in hits:
        hitDict = dict(zip(fieldNames,hit))

        # filter includes and excludes
        displaymodulelogger.info("checking %s in exclude list %s"%(hitDict['databasesearchstudy'], str(excludeDatabaseSearchList)))
        if excludeDatabaseSearchList != None:
            if hitDict['databasesearchstudy'] in excludeDatabaseSearchList:
                continue
        displaymodulelogger.info("checking %s in include list %s"%(hitDict['databasesearchstudy'], str(includeDatabaseSearchList)))
        if includeDatabaseSearchList != None:
            if len(includeDatabaseSearchList) > 0:
                if hitDict['databasesearchstudy'] not in includeDatabaseSearchList:
                    continue


        if hitDict["hittype"] == "nucleotide_hit":
            nucleotidehits = True
        elif hitDict["hittype"] == "protein_hit":
            proteinhits = True


        # BLASTN_nt       gb|AC152053.34| -       1218-1260       "M truncatula clone mth2-35e5; score: 61.9"
        hitdatapacket += """
%(hittype)s\t%(sequencename)s\t%(featurestrand)s\t%(queryfrom)s-%(queryto)s\t"%(xreflsid)s; score %(score)s ; evalue %(hitevalue)s;"
        """%hitDict


    if hitcount > 0:
        if proteinhits:
            seqdatapacket += """

[protein_hit]
bgcolor = magenta
key = protein_hit

"""

        if nucleotidehits:
            seqdatapacket += """

[nucleotide_hit]
bgcolor = green
key = nucleotide_hit

"""

    # need this to make the complete sequence display
    refdatapacket = """
reference       reference       +       1-%s
    """%referencelength



    # check if the gff file exists , if it does then do not redo it
    hashconstant = '23' # can use this to force a new file
    base = str(abs(hash( str(obid) + str(seqdatapacket) + str(featkeypacket) + str(featdatapacket) + str(hitdatapacket) + str(refdatapacket) + hashconstant))) 
    gfffilename = base + ".gff"
    mapfilename = base + ".map"
    imagefilename = base + ".png"
    gfffilepath = os.path.join(imagepath,  gfffilename ) 
    newgff = False
    if not os.path.exists(gfffilepath) :
        displaymodulelogger.info("writing %s"%gfffilepath)   
        file = open(gfffilepath,"w")
        file.write(seqdatapacket+featkeypacket+refdatapacket+featdatapacket+hitdatapacket)
        file.close()
        newgff = True


    ######### now call the script to make the image ############
    #./featureviewer.sh  width mapfilename imagefilename gfffilename tempimagefolder prog"
    # re-draw the image if we need to 
    imagefilepath = os.path.join(imagepath,imagefilename)
    if (not os.path.exists(imagefilepath)) or newgff :
        cmd = '/bin/sh %(shellscript)s  %(width)s %(mapfilename)s %(imagefilename)s %(gfffilename)s %(imagepath)s %(graphicsprog)s'%{
          'width' : width,
          'mapfilename' : mapfilename,
          'imagefilename' : imagefilename,
          'gfffilename' : gfffilename,
          'imagepath' : imagepath,
          'graphicsprog' : graphicsprog,
          'shellscript' : shellscript
        }

        displaymodulelogger.info("getGraphicFeaturePanel is executing %s"%cmd)
        status, output = commands.getstatusoutput(cmd)
        displaymodulelogger.info("Output: %s"%output)
        displaymodulelogger.info("Status: %s"%status)


        tempimagefile = output.strip()
    else:
        tempimagefile = imagefilename


    # get the size of the image - for convenience this is stored in the map file like this :
    #<!-- 1000 x 178 -->
    displaymodulelogger.info("getting feature image size")
    mapfilepath = os.path.join(imagepath,  mapfilename )
    if  os.path.exists(mapfilepath):
        file = open(mapfilepath,"r")
    else:
        resultHTML="""
                    <tr>
                    <td colspan="2" class=tableheading>
                    Sorry, unable to draw contig image - missing image file %s
                    </td>
                    </tr>
        """%mapfilepath
        return resultHTML


    recordcount = 0
    imageheight = None
    imagewidth = None
    for record in file:
        recordcount += 1
        record.strip()
        if recordcount < 3 and re.search('^\<\!--.*--\>$',record) != None:
           displaymodulelogger.info("using %s"%record)
           match=re.search('(\d+)\s*x\s*(\d+)',record)
           if len(match.groups()) == 2:
              (imagewidth,imageheight) = [int(item) for item in match.groups()]
              displaymodulelogger.info("parsed %s %s"%(imagewidth,imageheight))
           break
        elif recordcount >=3:
           break

    file.close()
    if imageheight != None:
        height = imageheight
    if imagewidth != None:
        width = imagewidth



    if re.search('^ERROR',tempimagefile) != None:
        resultHTML="""
                    <tr>
                    <td colspan="2" class=tableheading>
                    %s
                    </td>
                    </tr>
        """%tempimagefile
    else:
        resultHTML = """
                    <tr>
                    <td colspan="2" class=tableheading>
                    %(sectionheading)s
                    </td>
                    </tr>
                """%{
                'sectionheading' : sectionheading
                }


        inlineHTML= """
                        <tr>
                        <td colspan=2 align=left>
                        <p/>
                        <iframe src="%(tempimageurl)s%(tempimagefile)s" align="%(align)s" width="%(width)s" height="%(height)s"></iframe>
                        <p/>
                        </td>
                        </tr>
                """
        inlineHTML = inlineHTML%{
               'tempimageurl' : tempimageurl,
               'tempimagefile' : tempimagefile,
               'height' : height + 40,
               'width' : width,
               'align' : align,
               'sectionheading' : sectionheading
        }

        resultHTML += inlineHTML


    return resultHTML


def getAffyProbeGraphs(connection, ob=None, obtype='microarrayspotfact', usercontext="default", fetcher=None, imagepath=None, tempimageurl=None, \
                              sectionheading="",shellscript = "./getAffyProbeGraphs.sh", Rscript = './getAffyProbeGraphs.r', displayFunction = None,\
                           panelType = "DEFAULT",includeExperimentList = None,excludeExperimentList=None,\
                           width=1200,height=1200, imagetype="jpeg", normRscript='./getAffyNormProbeGraphs.r',includeMM=False, yscale="linear"):

    """ this method will create a graph of Affy probes , using the experiments indicated.
    Example of the input file required by the method :
    
"pN"    "probe.number"  "Slide" "pm.intensity"  "mm.intensity"
"11"    "CS37003138FFFFB_at"    1       "X54.1.CEL"     110     281
"122218"        "CS37003138FFFFB_at"    2       "X54.1.CEL"     244     185.300003051758
"122219"        "CS37003138FFFFB_at"    3       "X54.1.CEL"     1011    106
"122220"        "CS37003138FFFFB_at"    4       "X54.1.CEL"     132     104
"122221"        "CS37003138FFFFB_at"    5       "X54.1.CEL"     186     124
"122222"        "CS37003138FFFFB_at"    6       "X54.1.CEL"     618.5   321
"122223"        "CS37003138FFFFB_at"    7       "X54.1.CEL"     171     96.5
"122224"        "CS37003138FFFFB_at"    8       "X54.1.CEL"     185     127
"122225"        "CS37003138FFFFB_at"    9       "X54.1.CEL"     492     624
"122226"        "CS37003138FFFFB_at"    10      "X54.1.CEL"     203     202.800003051758
"122227"        "CS37003138FFFFB_at"    11      "X54.1.CEL"     801     367
"261124"        "CS37003138FFFFB_at"    1       "X54.4.CEL"     143.5   555
"261125"        "CS37003138FFFFB_at"    2       "X54.4.CEL"     253     209
"261126"        "CS37003138FFFFB_at"    3       "X54.4.CEL"     1229    108
"261127"        "CS37003138FFFFB_at"    4       "X54.4.CEL"     187     120.800003051758
"261128"        "CS37003138FFFFB_at"    5       "X54.4.CEL"     224.300003051758        158
"261129"        "CS37003138FFFFB_at"    6       "X54.4.CEL"     1090    429.299987792969
"261130"        "CS37003138FFFFB_at"    7       "X54.4.CEL"     301.5   212.800003051758
"261131"        "CS37003138FFFFB_at"    8       "X54.4.CEL"     327     162
"261132"        "CS37003138FFFFB_at"    9       "X54.4.CEL"     850.799987792969        1315
"261133"        "CS37003138FFFFB_at"    10      "X54.4.CEL"     286     291
"261134"        "CS37003138FFFFB_at"    11      "X54.4.CEL"     982     502
"400031"        "CS37003138FFFFB_at"    1       "X54.5.CEL"     173     424
"400032"        "CS37003138FFFFB_at"    2       "X54.5.CEL"     308.5   266
"400033"        "CS37003138FFFFB_at"    3       "X54.5.CEL"     1529    126
"400034"        "CS37003138FFFFB_at"    4       "X54.5.CEL"     217.5   121
"400035"        "CS37003138FFFFB_at"    5       "X54.5.CEL"     230     129.800003051758
"400036"        "CS37003138FFFFB_at"    6       "X54.5.CEL"     1150    468
"400037"        "CS37003138FFFFB_at"    7       "X54.5.CEL"     344.5   382
"400038"        "CS37003138FFFFB_at"    8       "X54.5.CEL"     326.5   175
"400039"        "CS37003138FFFFB_at"    9       "X54.5.CEL"     820     1551
"400040"        "CS37003138FFFFB_at"    10      "X54.5.CEL"     268.299987792969        270
"400041"        "CS37003138FFFFB_at"    11      "X54.5.CEL"     1391    536
"538938"        "CS37003138FFFFB_at"    1       "ACKO42.1.CEL"  101     184.800003051758
"538939"        "CS37003138FFFFB_at"    2       "ACKO42.1.CEL"  129.300003051758        122
"538940"        "CS37003138FFFFB_at"    3       "ACKO42.1.CEL"  221.800003051758        65.8000030517578
"538941"        "CS37003138FFFFB_at"    4       "ACKO42.1.CEL"  84      63
"538942"        "CS37003138FFFFB_at"    5       "ACKO42.1.CEL"  109.300003051758        88
"538943"        "CS37003138FFFFB_at"    6       "ACKO42.1.CEL"  386     224
"538944"        "CS37003138FFFFB_at"    7       "ACKO42.1.CEL"  168     130
"538945"        "CS37003138FFFFB_at"    8       "ACKO42.1.CEL"  86.5    65
etc
etc

    """


    ######### fist we need to marshall the probe values into a data file ############
    displaymodulelogger.info("starting getAffyProbeGraphs")     

### !!!!!!!!!!!!!! dummy value for testing !!!!!!
    dummyData = \
"""
"pN"	"probe.number"	"Slide"	"pm.intensity"	"mm.intensity"
"11"	"CS37003138FFFFB_at"	1	"X54.1.CEL"	110	281
"122218"	"CS37003138FFFFB_at"	2	"X54.1.CEL"	244	185.300003051758
"122219"	"CS37003138FFFFB_at"	3	"X54.1.CEL"	1011	106
"122220"	"CS37003138FFFFB_at"	4	"X54.1.CEL"	132	104
"122221"	"CS37003138FFFFB_at"	5	"X54.1.CEL"	186	124
"122222"	"CS37003138FFFFB_at"	6	"X54.1.CEL"	618.5	321
"122223"	"CS37003138FFFFB_at"	7	"X54.1.CEL"	171	96.5
"122224"	"CS37003138FFFFB_at"	8	"X54.1.CEL"	185	127
"122225"	"CS37003138FFFFB_at"	9	"X54.1.CEL"	492	624
"122226"	"CS37003138FFFFB_at"	10	"X54.1.CEL"	203	202.800003051758
"122227"	"CS37003138FFFFB_at"	11	"X54.1.CEL"	801	367
"261124"	"CS37003138FFFFB_at"	1	"X54.4.CEL"	143.5	555
"261125"	"CS37003138FFFFB_at"	2	"X54.4.CEL"	253	209
"261126"	"CS37003138FFFFB_at"	3	"X54.4.CEL"	1229	108
"261127"	"CS37003138FFFFB_at"	4	"X54.4.CEL"	187	120.800003051758
"261128"	"CS37003138FFFFB_at"	5	"X54.4.CEL"	224.300003051758	158
"261129"	"CS37003138FFFFB_at"	6	"X54.4.CEL"	1090	429.299987792969
"261130"	"CS37003138FFFFB_at"	7	"X54.4.CEL"	301.5	212.800003051758
"261131"	"CS37003138FFFFB_at"	8	"X54.4.CEL"	327	162
"261132"	"CS37003138FFFFB_at"	9	"X54.4.CEL"	850.799987792969	1315
"261133"	"CS37003138FFFFB_at"	10	"X54.4.CEL"	286	291
"261134"	"CS37003138FFFFB_at"	11	"X54.4.CEL"	982	502
"400031"	"CS37003138FFFFB_at"	1	"X54.5.CEL"	173	424
"400032"	"CS37003138FFFFB_at"	2	"X54.5.CEL"	308.5	266
"400033"	"CS37003138FFFFB_at"	3	"X54.5.CEL"	1529	126
"400034"	"CS37003138FFFFB_at"	4	"X54.5.CEL"	217.5	121
"400035"	"CS37003138FFFFB_at"	5	"X54.5.CEL"	230	129.800003051758
"400036"	"CS37003138FFFFB_at"	6	"X54.5.CEL"	1150	468
"400037"	"CS37003138FFFFB_at"	7	"X54.5.CEL"	344.5	382
"400038"	"CS37003138FFFFB_at"	8	"X54.5.CEL"	326.5	175
"400039"	"CS37003138FFFFB_at"	9	"X54.5.CEL"	820	1551
"400040"	"CS37003138FFFFB_at"	10	"X54.5.CEL"	268.299987792969	270
"400041"	"CS37003138FFFFB_at"	11	"X54.5.CEL"	1391	536
"538938"	"CS37003138FFFFB_at"	1	"ACKO42.1.CEL"	101	184.800003051758
"538939"	"CS37003138FFFFB_at"	2	"ACKO42.1.CEL"	129.300003051758	122
"538940"	"CS37003138FFFFB_at"	3	"ACKO42.1.CEL"	221.800003051758	65.8000030517578
"538941"	"CS37003138FFFFB_at"	4	"ACKO42.1.CEL"	84	63
"538942"	"CS37003138FFFFB_at"	5	"ACKO42.1.CEL"	109.300003051758	88
"538943"	"CS37003138FFFFB_at"	6	"ACKO42.1.CEL"	386	224
"538944"	"CS37003138FFFFB_at"	7	"ACKO42.1.CEL"	168	130
"538945"	"CS37003138FFFFB_at"	8	"ACKO42.1.CEL"	86.5	65
"1094574"	"CS37003138FFFFB_at"	9	"E.RG.4.CEL"	762	1059.30004882812
"1094575"	"CS37003138FFFFB_at"	10	"E.RG.4.CEL"	492.299987792969	435.5
"1094576"	"CS37003138FFFFB_at"	11	"E.RG.4.CEL"	1209.5	460.5
"1233473"	"CS37003138FFFFB_at"	1	"E.RG.5.CEL"	210.300003051758	553
"1233474"	"CS37003138FFFFB_at"	2	"E.RG.5.CEL"	477	256.5
"1233475"	"CS37003138FFFFB_at"	3	"E.RG.5.CEL"	2074	108
"1233476"	"CS37003138FFFFB_at"	4	"E.RG.5.CEL"	551	183
"1233477"	"CS37003138FFFFB_at"	5	"E.RG.5.CEL"	402.799987792969	178
"1233478"	"CS37003138FFFFB_at"	6	"E.RG.5.CEL"	779	427
"1233479"	"CS37003138FFFFB_at"	7	"E.RG.5.CEL"	682	278.299987792969
"1233480"	"CS37003138FFFFB_at"	8	"E.RG.5.CEL"	364	155
"1233481"	"CS37003138FFFFB_at"	9	"E.RG.5.CEL"	711.799987792969	923.5
"1233482"	"CS37003138FFFFB_at"	10	"E.RG.5.CEL"	673	519
"1233483"	"CS37003138FFFFB_at"	11	"E.RG.5.CEL"	936	417.5
"1372380"	"CS37003138FFFFB_at"	1	"FL1.T.3.CEL"	141	279
"1372381"	"CS37003138FFFFB_at"	2	"FL1.T.3.CEL"	218	204.5
"1372382"	"CS37003138FFFFB_at"	3	"FL1.T.3.CEL"	1528.80004882812	109.5
"1372383"	"CS37003138FFFFB_at"	4	"FL1.T.3.CEL"	189	129.300003051758
"1372384"	"CS37003138FFFFB_at"	5	"FL1.T.3.CEL"	268	125.300003051758
"1372385"	"CS37003138FFFFB_at"	6	"FL1.T.3.CEL"	1040.80004882812	537
"1372386"	"CS37003138FFFFB_at"	7	"FL1.T.3.CEL"	372.299987792969	244
"1372387"	"CS37003138FFFFB_at"	8	"FL1.T.3.CEL"	278	158
"1372388"	"CS37003138FFFFB_at"	9	"FL1.T.3.CEL"	753	1092
"1372389"	"CS37003138FFFFB_at"	10	"FL1.T.3.CEL"	337	343
"1372390"	"CS37003138FFFFB_at"	11	"FL1.T.3.CEL"	986.5	307.299987792969
"1511287"	"CS37003138FFFFB_at"	1	"FL1.T.4.CEL"	151.5	352
"1511288"	"CS37003138FFFFB_at"	2	"FL1.T.4.CEL"	275	216
"1511289"	"CS37003138FFFFB_at"	3	"FL1.T.4.CEL"	1893	104.5
"
"538946"	"CS37003138FFFFB_at"	9	"ACKO42.1.CEL"	283	482.299987792969
"538947"	"CS37003138FFFFB_at"	10	"ACKO42.1.CEL"	132	140
"538948"	"CS37003138FFFFB_at"	11	"ACKO42.1.CEL"	272	97
"677845"	"CS37003138FFFFB_at"	1	"ACKO42.4.CEL"	114.300003051758	189
"677846"	"CS37003138FFFFB_at"	2	"ACKO42.4.CEL"	262	170
"677847"	"CS37003138FFFFB_at"	3	"ACKO42.4.CEL"	304	61
"677848"	"CS37003138FFFFB_at"	4	"ACKO42.4.CEL"	78	59
"677849"	"CS37003138FFFFB_at"	5	"ACKO42.4.CEL"	135.5	116
"677850"	"CS37003138FFFFB_at"	6	"ACKO42.4.CEL"	908	410
"677851"	"CS37003138FFFFB_at"	7	"ACKO42.4.CEL"	304.799987792969	240
"677852"	"CS37003138FFFFB_at"	8	"ACKO42.4.CEL"	144	72
"677853"	"CS37003138FFFFB_at"	9	"ACKO42.4.CEL"	573	528
"677854"	"CS37003138FFFFB_at"	10	"ACKO42.4.CEL"	227	268.799987792969
"677855"	"CS37003138FFFFB_at"	11	"ACKO42.4.CEL"	497	204.800003051758
"816752"	"CS37003138FFFFB_at"	1	"ACKO42.5.CEL"	91	131
"816753"	"CS37003138FFFFB_at"	2	"ACKO42.5.CEL"	107	95
"816754"	"CS37003138FFFFB_at"	3	"ACKO42.5.CEL"	333.799987792969	69.3000030517578
"816755"	"CS37003138FFFFB_at"	4	"ACKO42.5.CEL"	132	91
"816756"	"CS37003138FFFFB_at"	5	"ACKO42.5.CEL"	135	110.300003051758
"816757"	"CS37003138FFFFB_at"	6	"ACKO42.5.CEL"	652	321.799987792969
"816758"	"CS37003138FFFFB_at"	7	"ACKO42.5.CEL"	240.300003051758	176
"816759"	"CS37003138FFFFB_at"	8	"ACKO42.5.CEL"	93	76
"816760"	"CS37003138FFFFB_at"	9	"ACKO42.5.CEL"	459.299987792969	693.5
"816761"	"CS37003138FFFFB_at"	10	"ACKO42.5.CEL"	137	139
"816762"	"CS37003138FFFFB_at"	11	"ACKO42.5.CEL"	524	341.299987792969
"955659"	"CS37003138FFFFB_at"	1	"E.RG.1.CEL"	155.5	379
"955660"	"CS37003138FFFFB_at"	2	"E.RG.1.CEL"	219	218
"955661"	"CS37003138FFFFB_at"	3	"E.RG.1.CEL"	1349	116.300003051758
"1094574"	"CS37003138FFFFB_at"	9	"E.RG.4.CEL"	762	1059.30004882812
"1094575"	"CS37003138FFFFB_at"	10	"E.RG.4.CEL"	492.299987792969	435.5
"1094576"	"CS37003138FFFFB_at"	11	"E.RG.4.CEL"	1209.5	460.5
"1233473"	"CS37003138FFFFB_at"	1	"E.RG.5.CEL"	210.300003051758	553
"1233474"	"CS37003138FFFFB_at"	2	"E.RG.5.CEL"	477	256.5
"1233475"	"CS37003138FFFFB_at"	3	"E.RG.5.CEL"	2074	108
"1233476"	"CS37003138FFFFB_at"	4	"E.RG.5.CEL"	551	183
"1233477"	"CS37003138FFFFB_at"	5	"E.RG.5.CEL"	402.799987792969	178
"1233478"	"CS37003138FFFFB_at"	6	"E.RG.5.CEL"	779	427
"1233479"	"CS37003138FFFFB_at"	7	"E.RG.5.CEL"	682	278.299987792969
"1233480"	"CS37003138FFFFB_at"	8	"E.RG.5.CEL"	364	155
"1233481"	"CS37003138FFFFB_at"	9	"E.RG.5.CEL"	711.799987792969	923.5
"1233482"	"CS37003138FFFFB_at"	10	"E.RG.5.CEL"	673	519
"1233483"	"CS37003138FFFFB_at"	11	"E.RG.5.CEL"	936	417.5
"1372380"	"CS37003138FFFFB_at"	1	"FL1.T.3.CEL"	141	279
"1372381"	"CS37003138FFFFB_at"	2	"FL1.T.3.CEL"	218	204.5
"1372382"	"CS37003138FFFFB_at"	3	"FL1.T.3.CEL"	1528.80004882812	109.5
"1372383"	"CS37003138FFFFB_at"	4	"FL1.T.3.CEL"	189	129.300003051758
"1372384"	"CS37003138FFFFB_at"	5	"FL1.T.3.CEL"	268	125.300003051758
"1372385"	"CS37003138FFFFB_at"	6	"FL1.T.3.CEL"	1040.80004882812	537
"1372386"	"CS37003138FFFFB_at"	7	"FL1.T.3.CEL"	372.299987792969	244
"1372387"	"CS37003138FFFFB_at"	8	"FL1.T.3.CEL"	278	158
"1372388"	"CS37003138FFFFB_at"	9	"FL1.T.3.CEL"	753	1092
"1372389"	"CS37003138FFFFB_at"	10	"FL1.T.3.CEL"	337	343
"1372390"	"CS37003138FFFFB_at"	11	"FL1.T.3.CEL"	986.5	307.299987792969
"1511287"	"CS37003138FFFFB_at"	1	"FL1.T.4.CEL"	151.5	352
"1511288"	"CS37003138FFFFB_at"	2	"FL1.T.4.CEL"	275	216
"1511289"	"CS37003138FFFFB_at"	3	"FL1.T.4.CEL"	1893	104.5
"
"955662"	"CS37003138FFFFB_at"	4	"E.RG.1.CEL"	67.3000030517578	64
"955663"	"CS37003138FFFFB_at"	5	"E.RG.1.CEL"	246	122
"955664"	"CS37003138FFFFB_at"	6	"E.RG.1.CEL"	433	263
"955665"	"CS37003138FFFFB_at"	7	"E.RG.1.CEL"	293	125.800003051758
"955666"	"CS37003138FFFFB_at"	8	"E.RG.1.CEL"	207	117.5
"955667"	"CS37003138FFFFB_at"	9	"E.RG.1.CEL"	452	567
"955668"	"CS37003138FFFFB_at"	10	"E.RG.1.CEL"	230	213
"955669"	"CS37003138FFFFB_at"	11	"E.RG.1.CEL"	571	326
"1094566"	"CS37003138FFFFB_at"	1	"E.RG.4.CEL"	184	340
"1094567"	"CS37003138FFFFB_at"	2	"E.RG.4.CEL"	421	268.299987792969
"1094568"	"CS37003138FFFFB_at"	3	"E.RG.4.CEL"	1751	118
"1094569"	"CS37003138FFFFB_at"	4	"E.RG.4.CEL"	88.3000030517578	66.3000030517578
"1094570"	"CS37003138FFFFB_at"	5	"E.RG.4.CEL"	305	167.800003051758
"1094571"	"CS37003138FFFFB_at"	6	"E.RG.4.CEL"	862	549.799987792969
"1094572"	"CS37003138FFFFB_at"	7	"E.RG.4.CEL"	438	219
"1094573"	"CS37003138FFFFB_at"	8	"E.RG.4.CEL"	330	170.800003051758
"1094574"	"CS37003138FFFFB_at"	9	"E.RG.4.CEL"	762	1059.30004882812
"1094575"	"CS37003138FFFFB_at"	10	"E.RG.4.CEL"	492.299987792969	435.5
"1094576"	"CS37003138FFFFB_at"	11	"E.RG.4.CEL"	1209.5	460.5
"1233473"	"CS37003138FFFFB_at"	1	"E.RG.5.CEL"	210.300003051758	553
"1233474"	"CS37003138FFFFB_at"	2	"E.RG.5.CEL"	477	256.5
"1233475"	"CS37003138FFFFB_at"	3	"E.RG.5.CEL"	2074	108
"1233476"	"CS37003138FFFFB_at"	4	"E.RG.5.CEL"	551	183
"1233477"	"CS37003138FFFFB_at"	5	"E.RG.5.CEL"	402.799987792969	178
"1233478"	"CS37003138FFFFB_at"	6	"E.RG.5.CEL"	779	427
"1233479"	"CS37003138FFFFB_at"	7	"E.RG.5.CEL"	682	278.299987792969
"1233480"	"CS37003138FFFFB_at"	8	"E.RG.5.CEL"	364	155
"1233481"	"CS37003138FFFFB_at"	9	"E.RG.5.CEL"	711.799987792969	923.5
"1233482"	"CS37003138FFFFB_at"	10	"E.RG.5.CEL"	673	519
"1233483"	"CS37003138FFFFB_at"	11	"E.RG.5.CEL"	936	417.5
"1372380"	"CS37003138FFFFB_at"	1	"FL1.T.3.CEL"	141	279
"1372381"	"CS37003138FFFFB_at"	2	"FL1.T.3.CEL"	218	204.5
"1372382"	"CS37003138FFFFB_at"	3	"FL1.T.3.CEL"	1528.80004882812	109.5
"1372383"	"CS37003138FFFFB_at"	4	"FL1.T.3.CEL"	189	129.300003051758
"1372384"	"CS37003138FFFFB_at"	5	"FL1.T.3.CEL"	268	125.300003051758
"1372385"	"CS37003138FFFFB_at"	6	"FL1.T.3.CEL"	1040.80004882812	537
"1372386"	"CS37003138FFFFB_at"	7	"FL1.T.3.CEL"	372.299987792969	244
"1372387"	"CS37003138FFFFB_at"	8	"FL1.T.3.CEL"	278	158
"1372388"	"CS37003138FFFFB_at"	9	"FL1.T.3.CEL"	753	1092
"1372389"	"CS37003138FFFFB_at"	10	"FL1.T.3.CEL"	337	343
"1372390"	"CS37003138FFFFB_at"	11	"FL1.T.3.CEL"	986.5	307.299987792969
"1511287"	"CS37003138FFFFB_at"	1	"FL1.T.4.CEL"	151.5	352
"1511288"	"CS37003138FFFFB_at"	2	"FL1.T.4.CEL"	275	216
"1511289"	"CS37003138FFFFB_at"	3	"FL1.T.4.CEL"	1893	104.5
"1511290"	"CS37003138FFFFB_at"	4	"FL1.T.4.CEL"	217	106
"1511291"	"CS37003138FFFFB_at"	5	"FL1.T.4.CEL"	275	139.800003051758
"1511292"	"CS37003138FFFFB_at"	6	"FL1.T.4.CEL"	1012	412
"1511293"	"CS37003138FFFFB_at"	7	"FL1.T.4.CEL"	453	423
"1511294"	"CS37003138FFFFB_at"	8	"FL1.T.4.CEL"	297.299987792969	141
"1511295"	"CS37003138FFFFB_at"	9	"FL1.T.4.CEL"	695	1025
"1511296"	"CS37003138FFFFB_at"	10	"FL1.T.4.CEL"	261	356.299987792969
"1511297"	"CS37003138FFFFB_at"	11	"FL1.T.4.CEL"	1379	471
"1650194"	"CS37003138FFFFB_at"	1	"FL1.T.6.CEL"	152	325
"1650195"	"CS37003138FFFFB_at"	2	"FL1.T.6.CEL"	319	284
"1650196"	"CS37003138FFFFB_at"	3	"FL1.T.6.CEL"	1118.30004882812	119
"1650197"	"CS37003138FFFFB_at"	4	"FL1.T.6.CEL"	202	114
"1650198"	"CS37003138FFFFB_at"	5	"FL1.T.6.CEL"	288	152.300003051758
"1650199"	"CS37003138FFFFB_at"	6	"FL1.T.6.CEL"	857	395
"1650200"	"CS37003138FFFFB_at"	7	"FL1.T.6.CEL"	380	355.799987792969
"1650201"	"CS37003138FFFFB_at"	8	"FL1.T.6.CEL"	334	169.5
"1650202"	"CS37003138FFFFB_at"	9	"FL1.T.6.CEL"	654	964
"1650203"	"CS37003138FFFFB_at"	10	"FL1.T.6.CEL"	265	314
"1650204"	"CS37003138FFFFB_at"	11	"FL1.T.6.CEL"	1249	488.299987792969
"1789101"	"CS37003138FFFFB_at"	1	"FL1L.3.CEL"	98	179
"1789102"	"CS37003138FFFFB_at"	2	"FL1L.3.CEL"	155	142.300003051758
"1789103"	"CS37003138FFFFB_at"	3	"FL1L.3.CEL"	206	89.8000030517578
"1789104"	"CS37003138FFFFB_at"	4	"FL1L.3.CEL"	82.3000030517578	68
"1789105"	"CS37003138FFFFB_at"	5	"FL1L.3.CEL"	145	113.800003051758
"1789106"	"CS37003138FFFFB_at"	6	"FL1L.3.CEL"	465	178
"1789107"	"CS37003138FFFFB_at"	7	"FL1L.3.CEL"	160	90
"1789108"	"CS37003138FFFFB_at"	8	"FL1L.3.CEL"	91	84
"1789109"	"CS37003138FFFFB_at"	9	"FL1L.3.CEL"	229	295
"1789110"	"CS37003138FFFFB_at"	10	"FL1L.3.CEL"	135	143
"1789111"	"CS37003138FFFFB_at"	11	"FL1L.3.CEL"	446.799987792969	202.800003051758
"1928008"	"CS37003138FFFFB_at"	1	"FL1L.5.CEL"	196	272
"1928009"	"CS37003138FFFFB_at"	2	"FL1L.5.CEL"	268	200
"1928010"	"CS37003138FFFFB_at"	3	"FL1L.5.CEL"	718.799987792969	97
"1928011"	"CS37003138FFFFB_at"	4	"FL1L.5.CEL"	156	107
"1928012"	"CS37003138FFFFB_at"	5	"FL1L.5.CEL"	189.5	117
"1928013"	"CS37003138FFFFB_at"	6	"FL1L.5.CEL"	498	296
"1928014"	"CS37003138FFFFB_at"	7	"FL1L.5.CEL"	252	125
"1928015"	"CS37003138FFFFB_at"	8	"FL1L.5.CEL"	180	92
"1928016"	"CS37003138FFFFB_at"	9	"FL1L.5.CEL"	392.5	500
"1928017"	"CS37003138FFFFB_at"	10	"FL1L.5.CEL"	243	214
"1928018"	"CS37003138FFFFB_at"	11	"FL1L.5.CEL"	628	273
"2066915"	"CS37003138FFFFB_at"	1	"FL1L.6.CEL"	115	254.5
"2066916"	"CS37003138FFFFB_at"	2	"FL1L.6.CEL"	212.5	175
"2066917"	"CS37003138FFFFB_at"	3	"FL1L.6.CEL"	1592	84
"2066918"	"CS37003138FFFFB_at"	4	"FL1L.6.CEL"	211	116
"2066919"	"CS37003138FFFFB_at"	5	"FL1L.6.CEL"	177	102
"2066920"	"CS37003138FFFFB_at"	6	"FL1L.6.CEL"	538	266
"2066921"	"CS37003138FFFFB_at"	7	"FL1L.6.CEL"	248	138
"2066922"	"CS37003138FFFFB_at"	8	"FL1L.6.CEL"	199.300003051758	115
"2066923"	"CS37003138FFFFB_at"	9	"FL1L.6.CEL"	482	677
"2066924"	"CS37003138FFFFB_at"	10	"FL1L.6.CEL"	229.5	245.800003051758
"2066925"	"CS37003138FFFFB_at"	11	"FL1L.6.CEL"	579	287
"2205822"	"CS37003138FFFFB_at"	1	"FLIF.1.CEL"	145	191
"2205823"	"CS37003138FFFFB_at"	2	"FLIF.1.CEL"	243	271.5
"2205824"	"CS37003138FFFFB_at"	3	"FLIF.1.CEL"	107	217
"2205825"	"CS37003138FFFFB_at"	4	"FLIF.1.CEL"	121.5	115
"2205826"	"CS37003138FFFFB_at"	5	"FLIF.1.CEL"	170	165.800003051758
"2205827"	"CS37003138FFFFB_at"	6	"FLIF.1.CEL"	1380	408
"2205828"	"CS37003138FFFFB_at"	7	"FLIF.1.CEL"	110.5	125.5
"2205829"	"CS37003138FFFFB_at"	8	"FLIF.1.CEL"	219	231
"2205830"	"CS37003138FFFFB_at"	9	"FLIF.1.CEL"	562	994.5
"2205831"	"CS37003138FFFFB_at"	10	"FLIF.1.CEL"	225	391
"2205832"	"CS37003138FFFFB_at"	11	"FLIF.1.CEL"	554	301.5
"2344729"	"CS37003138FFFFB_at"	1	"FLIF.2.CEL"	108.300003051758	112
"2344730"	"CS37003138FFFFB_at"	2	"FLIF.2.CEL"	192	196
"2344731"	"CS37003138FFFFB_at"	3	"FLIF.2.CEL"	88	142
"2344732"	"CS37003138FFFFB_at"	4	"FLIF.2.CEL"	111.300003051758	112
"2344733"	"CS37003138FFFFB_at"	5	"FLIF.2.CEL"	125	115.800003051758
"2344734"	"CS37003138FFFFB_at"	6	"FLIF.2.CEL"	881	255
"2344735"	"CS37003138FFFFB_at"	7	"FLIF.2.CEL"	118	98
"2344736"	"CS37003138FFFFB_at"	8	"FLIF.2.CEL"	151	172.800003051758
"2344737"	"CS37003138FFFFB_at"	9	"FLIF.2.CEL"	323.799987792969	601
"2344738"	"CS37003138FFFFB_at"	10	"FLIF.2.CEL"	202	242
"2344739"	"CS37003138FFFFB_at"	11	"FLIF.2.CEL"	370	256.799987792969
"2483636"	"CS37003138FFFFB_at"	1	"FLIF.3.CEL"	134	156
"2483637"	"CS37003138FFFFB_at"	2	"FLIF.3.CEL"	240	298.799987792969
"2483638"	"CS37003138FFFFB_at"	3	"FLIF.3.CEL"	103	157
"2483639"	"CS37003138FFFFB_at"	4	"FLIF.3.CEL"	101	96.5
"2483640"	"CS37003138FFFFB_at"	5	"FLIF.3.CEL"	139	137
"2483641"	"CS37003138FFFFB_at"	6	"FLIF.3.CEL"	972	305
"2483642"	"CS37003138FFFFB_at"	7	"FLIF.3.CEL"	104	96
"2483643"	"CS37003138FFFFB_at"	8	"FLIF.3.CEL"	179	161.300003051758
"2483644"	"CS37003138FFFFB_at"	9	"FLIF.3.CEL"	413	718
"2483645"	"CS37003138FFFFB_at"	10	"FLIF.3.CEL"	199	262
"2483646"	"CS37003138FFFFB_at"	11	"FLIF.3.CEL"	473	354.5
"2622543"	"CS37003138FFFFB_at"	1	"G9.3.CEL"	103	246
"2622544"	"CS37003138FFFFB_at"	2	"G9.3.CEL"	196	121.800003051758
"2622545"	"CS37003138FFFFB_at"	3	"G9.3.CEL"	860.799987792969	68
"2622546"	"CS37003138FFFFB_at"	4	"G9.3.CEL"	77	59
"2622547"	"CS37003138FFFFB_at"	5	"G9.3.CEL"	122.5	80
"2622548"	"CS37003138FFFFB_at"	6	"G9.3.CEL"	359.5	180.800003051758
"2622549"	"CS37003138FFFFB_at"	7	"G9.3.CEL"	238.5	114.5
"2622550"	"CS37003138FFFFB_at"	8	"G9.3.CEL"	97	65.8000030517578
"2622551"	"CS37003138FFFFB_at"	9	"G9.3.CEL"	225	280
"2622552"	"CS37003138FFFFB_at"	10	"G9.3.CEL"	157	130
"2622553"	"CS37003138FFFFB_at"	11	"G9.3.CEL"	417	154
"2761450"	"CS37003138FFFFB_at"	1	"G9.4.CEL"	264.799987792969	756
"2761451"	"CS37003138FFFFB_at"	2	"G9.4.CEL"	488	273
"2761452"	"CS37003138FFFFB_at"	3	"G9.4.CEL"	1328.80004882812	87
"2761453"	"CS37003138FFFFB_at"	4	"G9.4.CEL"	335	116
"2761454"	"CS37003138FFFFB_at"	5	"G9.4.CEL"	348.799987792969	160
"2761455"	"CS37003138FFFFB_at"	6	"G9.4.CEL"	572	247
"2761456"	"CS37003138FFFFB_at"	7	"G9.4.CEL"	607.799987792969	197
"2761457"	"CS37003138FFFFB_at"	8	"G9.4.CEL"	400	162.300003051758
"2761458"	"CS37003138FFFFB_at"	9	"G9.4.CEL"	549	645
"2761459"	"CS37003138FFFFB_at"	10	"G9.4.CEL"	567	417.5
"2761460"	"CS37003138FFFFB_at"	11	"G9.4.CEL"	854	303
"2900357"	"CS37003138FFFFB_at"	1	"G9.6.CEL"	154	270
"2900358"	"CS37003138FFFFB_at"	2	"G9.6.CEL"	282	195
"2900359"	"CS37003138FFFFB_at"	3	"G9.6.CEL"	569.5	57.5
"2900360"	"CS37003138FFFFB_at"	4	"G9.6.CEL"	140	83
"2900361"	"CS37003138FFFFB_at"	5	"G9.6.CEL"	241	115
"2900362"	"CS37003138FFFFB_at"	6	"G9.6.CEL"	328	211
"2900363"	"CS37003138FFFFB_at"	7	"G9.6.CEL"	448	167
"2900364"	"CS37003138FFFFB_at"	8	"G9.6.CEL"	135	64.3000030517578
"2900365"	"CS37003138FFFFB_at"	9	"G9.6.CEL"	289	349
"2900366"	"CS37003138FFFFB_at"	10	"G9.6.CEL"	249.300003051758	173
"2900367"	"CS37003138FFFFB_at"	11	"G9.6.CEL"	298	133.300003051758
"3039264"	"CS37003138FFFFB_at"	1	"LP19F.1.CEL"	76.3000030517578	82.3000030517578
"3039265"	"CS37003138FFFFB_at"	2	"LP19F.1.CEL"	106.5	150
"3039266"	"CS37003138FFFFB_at"	3	"LP19F.1.CEL"	87	91
"3039267"	"CS37003138FFFFB_at"	4	"LP19F.1.CEL"	75	81.3000030517578
"3039268"	"CS37003138FFFFB_at"	5	"LP19F.1.CEL"	90	88.8000030517578
"3039269"	"CS37003138FFFFB_at"	6	"LP19F.1.CEL"	176	138
"3039270"	"CS37003138FFFFB_at"	7	"LP19F.1.CEL"	74.3000030517578	67
"3039271"	"CS37003138FFFFB_at"	8	"LP19F.1.CEL"	101	105.300003051758
"3039272"	"CS37003138FFFFB_at"	9	"LP19F.1.CEL"	130	154
"3039273"	"CS37003138FFFFB_at"	10	"LP19F.1.CEL"	86	90
"3039274"	"CS37003138FFFFB_at"	11	"LP19F.1.CEL"	145	141
"3178171"	"CS37003138FFFFB_at"	1	"LP19F.2.CEL"	99.3000030517578	85
"3178172"	"CS37003138FFFFB_at"	2	"LP19F.2.CEL"	127.300003051758	121
"3178173"	"CS37003138FFFFB_at"	3	"LP19F.2.CEL"	53	57
"3178174"	"CS37003138FFFFB_at"	4	"LP19F.2.CEL"	56	56.2999992370605
"3178175"	"CS37003138FFFFB_at"	5	"LP19F.2.CEL"	89	94.3000030517578
"3178176"	"CS37003138FFFFB_at"	6	"LP19F.2.CEL"	416	155
"3178177"	"CS37003138FFFFB_at"	7	"LP19F.2.CEL"	86.3000030517578	87
"3178178"	"CS37003138FFFFB_at"	8	"LP19F.2.CEL"	83.5	76.3000030517578
"3178179"	"CS37003138FFFFB_at"	9	"LP19F.2.CEL"	61	83.5
"3178180"	"CS37003138FFFFB_at"	10	"LP19F.2.CEL"	66	81
"3178181"	"CS37003138FFFFB_at"	11	"LP19F.2.CEL"	106	80.5
"3317078"	"CS37003138FFFFB_at"	1	"LP19F.3.CEL"	103	134.300003051758
"3317079"	"CS37003138FFFFB_at"	2	"LP19F.3.CEL"	158	146
"3317080"	"CS37003138FFFFB_at"	3	"LP19F.3.CEL"	113.300003051758	111
"3317081"	"CS37003138FFFFB_at"	4	"LP19F.3.CEL"	90	89.3000030517578
"3317082"	"CS37003138FFFFB_at"	5	"LP19F.3.CEL"	132	104
"3317083"	"CS37003138FFFFB_at"	6	"LP19F.3.CEL"	654	233.300003051758
"3317084"	"CS37003138FFFFB_at"	7	"LP19F.3.CEL"	89.8000030517578	93
"3317085"	"CS37003138FFFFB_at"	8	"LP19F.3.CEL"	137	130
"3317086"	"CS37003138FFFFB_at"	9	"LP19F.3.CEL"	227	266
"3317087"	"CS37003138FFFFB_at"	10	"LP19F.3.CEL"	106	144.800003051758
"3317088"	"CS37003138FFFFB_at"	11	"LP19F.3.CEL"	238	182.300003051758
"3455985"	"CS37003138FFFFB_at"	1	"LP19L.2.CEL"	140	310.299987792969
"3455986"	"CS37003138FFFFB_at"	2	"LP19L.2.CEL"	256	231
"3455987"	"CS37003138FFFFB_at"	3	"LP19L.2.CEL"	2212.5	107
"3455988"	"CS37003138FFFFB_at"	4	"LP19L.2.CEL"	231	122
"3455989"	"CS37003138FFFFB_at"	5	"LP19L.2.CEL"	306	158
"3455990"	"CS37003138FFFFB_at"	6	"LP19L.2.CEL"	653	398
"3455991"	"CS37003138FFFFB_at"	7	"LP19L.2.CEL"	361	167
"3455992"	"CS37003138FFFFB_at"	8	"LP19L.2.CEL"	309.799987792969	124
"3455993"	"CS37003138FFFFB_at"	9	"LP19L.2.CEL"	655	1019.79998779297
"3455994"	"CS37003138FFFFB_at"	10	"LP19L.2.CEL"	358.799987792969	361
"3455995"	"CS37003138FFFFB_at"	11	"LP19L.2.CEL"	737.299987792969	305
"3594892"	"CS37003138FFFFB_at"	1	"LP19L.3.CEL"	109	193.300003051758
"3594893"	"CS37003138FFFFB_at"	2	"LP19L.3.CEL"	171.5	143
"3594894"	"CS37003138FFFFB_at"	3	"LP19L.3.CEL"	202	56
"3594895"	"CS37003138FFFFB_at"	4	"LP19L.3.CEL"	69	67.8000030517578
"3594896"	"CS37003138FFFFB_at"	5	"LP19L.3.CEL"	148	132
"3594897"	"CS37003138FFFFB_at"	6	"LP19L.3.CEL"	487	238
"3594898"	"CS37003138FFFFB_at"	7	"LP19L.3.CEL"	349.5	158
"3594899"	"CS37003138FFFFB_at"	8	"LP19L.3.CEL"	142	102
"3594900"	"CS37003138FFFFB_at"	9	"LP19L.3.CEL"	602	780
"3594901"	"CS37003138FFFFB_at"	10	"LP19L.3.CEL"	84	81
"3594902"	"CS37003138FFFFB_at"	11	"LP19L.3.CEL"	613	148
"3733799"	"CS37003138FFFFB_at"	1	"LP19L.5.CEL"	126.300003051758	234
"3733800"	"CS37003138FFFFB_at"	2	"LP19L.5.CEL"	249.5	186
"3733801"	"CS37003138FFFFB_at"	3	"LP19L.5.CEL"	1281	114
"3733802"	"CS37003138FFFFB_at"	4	"LP19L.5.CEL"	156.5	109
"3733803"	"CS37003138FFFFB_at"	5	"LP19L.5.CEL"	271.5	130
"3733804"	"CS37003138FFFFB_at"	6	"LP19L.5.CEL"	517.5	304
"3733805"	"CS37003138FFFFB_at"	7	"LP19L.5.CEL"	227	142.300003051758
"3733806"	"CS37003138FFFFB_at"	8	"LP19L.5.CEL"	227	131
"3733807"	"CS37003138FFFFB_at"	9	"LP19L.5.CEL"	549	764.799987792969
"3733808"	"CS37003138FFFFB_at"	10	"LP19L.5.CEL"	288	277
"3733809"	"CS37003138FFFFB_at"	11	"LP19L.5.CEL"	574	250
"3872706"	"CS37003138FFFFB_at"	1	"NC25KO.1.CEL"	106	235.800003051758
"3872707"	"CS37003138FFFFB_at"	2	"NC25KO.1.CEL"	227	213
"3872708"	"CS37003138FFFFB_at"	3	"NC25KO.1.CEL"	477	103
"3872709"	"CS37003138FFFFB_at"	4	"NC25KO.1.CEL"	154	112
"3872710"	"CS37003138FFFFB_at"	5	"NC25KO.1.CEL"	198.800003051758	146
"3872711"	"CS37003138FFFFB_at"	6	"NC25KO.1.CEL"	1101	498.299987792969
"3872712"	"CS37003138FFFFB_at"	7	"NC25KO.1.CEL"	221	290
"3872713"	"CS37003138FFFFB_at"	8	"NC25KO.1.CEL"	247	140
"3872714"	"CS37003138FFFFB_at"	9	"NC25KO.1.CEL"	762	1342
"3872715"	"CS37003138FFFFB_at"	10	"NC25KO.1.CEL"	208	278
"3872716"	"CS37003138FFFFB_at"	11	"NC25KO.1.CEL"	1164	355
"4011613"	"CS37003138FFFFB_at"	1	"NC25KO.2.CEL"	112	153
"4011614"	"CS37003138FFFFB_at"	2	"NC25KO.2.CEL"	202	195.5
"4011615"	"CS37003138FFFFB_at"	3	"NC25KO.2.CEL"	665	104.300003051758
"4011616"	"CS37003138FFFFB_at"	4	"NC25KO.2.CEL"	128	124
"4011617"	"CS37003138FFFFB_at"	5	"NC25KO.2.CEL"	170	135.800003051758
"4011618"	"CS37003138FFFFB_at"	6	"NC25KO.2.CEL"	700	382
"4011619"	"CS37003138FFFFB_at"	7	"NC25KO.2.CEL"	194	133.300003051758
"4011620"	"CS37003138FFFFB_at"	8	"NC25KO.2.CEL"	255.300003051758	178
"4011621"	"CS37003138FFFFB_at"	9	"NC25KO.2.CEL"	644	966
"4011622"	"CS37003138FFFFB_at"	10	"NC25KO.2.CEL"	184	280.5
"4011623"	"CS37003138FFFFB_at"	11	"NC25KO.2.CEL"	918.5	334
"4150520"	"CS37003138FFFFB_at"	1	"NC25KO.3.CEL"	111	126.5
"4150521"	"CS37003138FFFFB_at"	2	"NC25KO.3.CEL"	203	155
"4150522"	"CS37003138FFFFB_at"	3	"NC25KO.3.CEL"	721	95.5
"4150523"	"CS37003138FFFFB_at"	4	"NC25KO.3.CEL"	170	121
"4150524"	"CS37003138FFFFB_at"	5	"NC25KO.3.CEL"	148.800003051758	120
"4150525"	"CS37003138FFFFB_at"	6	"NC25KO.3.CEL"	624.299987792969	330.5
"4150526"	"CS37003138FFFFB_at"	7	"NC25KO.3.CEL"	197	113
"4150527"	"CS37003138FFFFB_at"	8	"NC25KO.3.CEL"	208	139.300003051758
"4150528"	"CS37003138FFFFB_at"	9	"NC25KO.3.CEL"	585.5	828
"4150529"	"CS37003138FFFFB_at"	10	"NC25KO.3.CEL"	201.300003051758	207
"4150530"	"CS37003138FFFFB_at"	11	"NC25KO.3.CEL"	877	243.300003051758    
"""
    #spotCursor=connection.cursor()
    resultHTML = """
                    <tr>
                    <td colspan="2" class=tableheading> 
                    %(sectionheading)s
                    </td>
                    </tr>
                """%{
                'sectionheading' : sectionheading
                }    

    # get the raw data for each observation in the list
    graphData = """"pN"\t"probe.number"\t"Slide"\t"pm.intensity"\t"mm.intensity" """
    normalisedgraphData  = """"pN"\t"probe.number"\t"Slide"\t"pm.intensity"\t"mm.intensity" """
    spotCursor = connection.cursor()
    if includeExperimentList == None:
        # at some point we could add code to graph all experiments - though probably not
        # useful, and would need to include information about sorting them
        raise brdfException("getAffyProbeGraphs : missing experimentlist option is not currently supported")
    else:
        for experiment in includeExperimentList:
            sql = """
                select
                    mo.obid,
                    ges.studyname,
                    mo.rawdatarecord
                from
                    microarrayobservation mo join geneexpressionstudy ges on
                    mo.microarrayspotfact = %(microarrayspot)s and
                    mo.microarraystudy = %(microarraystudy)s and
                    ges.obid = mo.microarraystudy
                """%{
                    "microarrayspot" : ob.databaseFields['obid'],
                    "microarraystudy" : experiment
                    }
            displaymodulelogger.info("executing %s"%sql)     
            spotCursor.execute(sql)
            rawdata = spotCursor.fetchone()
            displaymodulelogger.info("got %s"%str(rawdata))
            datatuples = eval(rawdata[2])
            experimentname = rawdata[1]
            probenumber = 1
            # raw data record looks like this :
            #[('CS3700301900001_copy11_s_at1', '2705', '6459'), ('CS3700301900001_copy11_s_a
            #t2', '2972.30004882813', '7484'), ('CS3700301900001_copy11_s_at3', '5004', '7009
            #.5'), ('CS3700301900001_copy11_s_at4', '1197.5', '5591'), ('CS3700301900001_copy
            #11_s_at5', '1217', '6425'), ('CS3700301900001_copy11_s_at6', '1855', '4264'), ('
            #CS3700301900001_copy11_s_at7', '860', '4835'), ('CS3700301900001_copy11_s_at8', 
            #'1346', '4059'), ('CS3700301900001_copy11_s_at9', '1503.30004882813', '4609'), (
            #'CS3700301900001_copy11_s_at10', '603', '4203')]
            #
            # need to wrte out like this :
            #"""
            #"pN"	"probe.number"	"Slide"	"pm.intensity"	"mm.intensity"
            #"11"	"CS37003138FFFFB_at"	1	"X54.1.CEL"	110	281
            #"122218"	"CS37003138FFFFB_at"	2	"X54.1.CEL"	244	185.300003051758
            #"122219"	"CS37003138FFFFB_at"	3	"X54.1.CEL"	1011	106
            #"""



            # attempt to get a normalisation factor
            sql = """
               select getAffyProbeNormalisationFactor(%(experiment)s,%(microarrayspot)s)
            """%{
                'experiment' : experiment,
                'microarrayspot' : ob.databaseFields['obid']
            }
            displaymodulelogger.info("executing %s"%sql)
            spotCursor.execute(sql)
            normalisationFactor = spotCursor.fetchone()
            displaymodulelogger.info("cursor returned normalisation factor = %s"%normalisationFactor)
            if normalisationFactor == None:
                normalisationFactor = None;
            elif normalisationFactor[0] == None:
                normalisationFactor = None;
            else:
                normalisationFactor = float(normalisationFactor[0])
                
            displaymodulelogger.info("got norm factor = %s"%normalisationFactor)
            
            
            for mytuple in datatuples:
                graphData += """
"%(pn)s"\t"%(probe)s"\t%(probenumber)s\t"%(experimentname)s"\t%(pm)s\t%(mm)s"""% {
                    "pn" : rawdata[0] + probenumber - 1,
                    "probe" : ob.databaseFields['accession'],
                    "probenumber" : probenumber,
                    "experimentname" : experimentname,
                    "pm" : mytuple[2],
                    "mm" : mytuple[1]
                }
                probenumber += 1

            if normalisationFactor != None:
                for mytuple in datatuples:

                    # test whether we get a normalised value and if not then break and
                    # indicate no normalised data available...
                    
                    normalisedgraphData += """
    "%(pn)s"\t"%(probe)s"\t%(probenumber)s\t"%(experimentname)s"\t%(pm)s\t%(mm)s"""% {
                        "pn" : rawdata[0] + probenumber - 1,
                        "probe" : ob.databaseFields['accession'],
                        "probenumber" : probenumber,
                        "experimentname" : experimentname,
                        "pm" : "%6.1f"%(float(mytuple[2])*normalisationFactor),
                        "mm" : "%6.1f"%(float(mytuple[1])*normalisationFactor)
                    }
                    probenumber += 1
                
        graphData += "\n"
                    
                    
            
    # check if the data file exists , if it does then do not redo it
    hashconstant = '23' # can use this to force a new file
    base = str(abs(hash( str(ob.databaseFields['xreflsid']) + str(datatuples) + str(includeExperimentList) + str(normRscript) + str(includeMM) + str(yscale) + hashconstant)))
    nbase = "n%s"%base
    #base = "test"
    datafilename = base + ".txt"
    ndatafilename = nbase + ".txt"
    if imagetype.lower() == 'jpeg':
        imagefilename = base + ".jpg"
    else:
        imagefilename = base + ".png"

    datafilepath = os.path.join(imagepath,  datafilename )
    ndatafilepath = os.path.join(imagepath,  ndatafilename )
    newdata = False
    if not os.path.exists(datafilepath) :
        displaymodulelogger.info("writing %s"%datafilepath)   
        file = open(datafilepath,"w")
        file.write(graphData)
        file.close()
        newdata = True
    if (normalisationFactor != None) and (not os.path.exists(ndatafilepath)) :
        displaymodulelogger.info("writing %s"%ndatafilepath)   
        file = open(ndatafilepath,"w")
        file.write(normalisedgraphData)
        file.close()
        newdata = True
        
    ######### now call the script to make the image ############
    # example : ./getAffyProbeGraphs.sh ./getAffyProbeGraphs.r ../html/tmp/CS37003138FFFFB_at.txt test.jpg 1200 1200 jpeg /tmp CS37003138FFFFB_at
    # re-draw the image if we need to
    imagefilepath = os.path.join(imagepath,imagefilename)


    if (not os.path.exists(imagefilepath)) or newdata :
        if normalisationFactor != None:
            cmd = '/bin/sh %(shellscript)s  %(Rscript)s  %(datafilename)s %(imagefilename)s %(height)s %(width)s %(imagetype)s %(imagepath)s %(plotname)s %(ndatafilename)s "False" %(yscale)s'%{
              'shellscript' : shellscript,
              'Rscript' : normRscript,
              'datafilename' : datafilename,
              'imagefilename' : imagefilename,
              'height' : height,
              'width' : width,
              'imagetype' : imagetype,
              'imagepath' : imagepath,
              'plotname' :  ob.databaseFields['accession'],
              'ndatafilename' : ndatafilename,
              'yscale' : yscale
            }
        else:
            cmd = '/bin/sh %(shellscript)s  %(Rscript)s  %(datafilename)s %(imagefilename)s %(height)s %(width)s %(imagetype)s %(imagepath)s %(plotname)s "None" %(includeMM)s %(yscale)s'%{
              'shellscript' : shellscript,
              'Rscript' : Rscript,
              'datafilename' : datafilename,
              'imagefilename' : imagefilename,
              'height' : height,
              'width' : width,
              'imagetype' : imagetype,
              'imagepath' : imagepath,
              'plotname' :  ob.databaseFields['accession'],
              'includeMM' : includeMM,
              'yscale' : yscale
            }            
            


        displaymodulelogger.info("getAffyProbeGraphs is executing %s"%cmd)
        status, output = commands.getstatusoutput(cmd)
        displaymodulelogger.info("Output: %s"%output)
        displaymodulelogger.info("Status: %s"%status)


        tempimagefile = output.strip()
    else:
        tempimagefile = imagefilename


    if re.search('^ERROR',tempimagefile) != None:
        resultHTML="""
                    <tr>
                    <td colspan="2" class=tableheading>
                    %s
                    </td>
                    </tr>
        """%tempimagefile
    else:
        resultHTML = """
                    <tr>
                    <td colspan="2" class=tableheading>
                    %(sectionheading)s
                    </td>
                    </tr>
                """%{
                'sectionheading' : sectionheading
                }


        inlineHTML= """
                        <tr>
                        <td colspan=2 align=center>
                        <p/>
                        <img src="%(tempimageurl)s%(tempimagefile)s" align="center" width="%(width)s" height="%(height)s"></img>
                        <p/>
                        </td>
                        </tr>
                """
        inlineHTML = inlineHTML%{
               'tempimageurl' : tempimageurl,
               'tempimagefile' : tempimagefile,
               'height' : height + 40,
               'width' : width,
               'sectionheading' : sectionheading
        }

        resultHTML += inlineHTML


    return resultHTML


def main():
    #AgilentHyperlinkMain()
    #HyperlinkSimilarExpressionMain()
    #myReader = csvSpotReader("c:/working/microarray/jyexps.csv")
    #spot =  myReader.nextSpot()
    #while spot != None:
    #    print spot
    #    print myReader.nextProfile()
    #    spot =  myReader.nextSpot()
    #    
    #print getSpotExpressionDisplay(1502, usercontext="default", fetcher="", imagepath="", tempimageurl="", sectionheading="Gene Expression from Clonetrac print 128 ovine 20K.txt.BC2.BR1.C6.R23",barwidth=10)
    #createProtocolMain()
    #marshallBfile("C:/working/pgc","orion-genomics-logo.gif", "c:/temp", targetfilename = '')
    #connection = databaseModule.getConnection()
    #getSequenceTraceViewPanel(connection, obid=None, obtype='biosequenceob', usercontext="default", fetcher=None, imagepath='/tmp', tempimageurl=None, sectionheading=None,\
    #  shellscript = "./traceviewer.sh", graphicsprog = './traceviewer.pl', displayFunction = \
    #  (0,0,0,0,0,0,'/data/databases/flatfile/bfiles/pgc/tracefiles/orion/pt1/1188_10_f_48515/traces/1188_10_14726942_16654_48515_016.ab1.gz'), height = 200, \
    #  left = 'CAATAGTAAGGGTGCTGCCGTGCCAC', right='AggtcaactTTGgctgttgtCTTG', size=678)

    #print getAlleleFrequencyDisplay(genetictestfact=1128578, usercontext="default", fetcher=None, imagepath="c:/temp", tempimageurl=None, sectionheading="",\
    #                     barwidth=10,graphTitle1="",graphTitle2="")
    #print getAffyProbeGraphs(None, obid=4470805, obtype="microarrayspotfact", usercontext="default", fetcher=None, imagepath="/tmp", tempimageurl=None, sectionheading="Probe Contrast Plots for Affymetrix.Lp19-Lpa530240N (AgResearch Fungal Array).CS37003138FFFFB_at " ,shellscript = "./getAffyProbeGraphs.sh", Rscript = "./getAffyProbeGraphs.r",panelType = "DEFAULT",includeExperimentList = None,excludeExperimentList=None,width=1200, height=1200, imagetype="jpeg")
    #compileSFFFile(outfolder='/tmp', outfilename = 'test1.sff', shellscript= './appendsfffile.sh', sh="/bin/sh", \
    #               readDict = {
    #                   '/data/bfiles/isgcdata/romney180_05/Baylor.E0C6VPL01.sff.gz' :['E0C6VPL01C2GZJ','E0C6VPL01DNJV2', 'E0C6VPL01DWC6B'],
    #                   '/data/bfiles/isgcdata/romney180_05/Baylor.E0FD4S102.sff.gz' :['E0FD4S102F9J6J','E0FD4S102F4KAQ', 'E0FD4S102GGUFE']
    #                })
    marshallDataSource(datasourceob=11703621, targetfolder='/tmp', targetfilename = 'CLP0008090528-cF4_20030121.ace', uncompress=True, bin="/usr/bin", sourcefilename='seqdata/forage/LP/C/Seqdata/0008/090/ace/edit_dir/CLP0008090528-cF4_20030121.ace')
  


        
if __name__ == "__main__":
   main()


