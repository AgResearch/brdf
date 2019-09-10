#!/usr/bin/python2.4
#
# This script is intended to process a zip archive containing a set of normalised data files
# that have been produced as one of the final steps in a microarray expt analysis - e.g.
# after final decisions about which scan intensities to use etc.  This is usually done as part of 
# the publication process. This script processes the data into a contributed data table 
# that is used. (From here,queries are executed that link the data to the array platform - e.g.
# so that the correct ID_REF column is extracted)
#
# It assumes that the zip archive has already been uploaded to the server using the standard
# upload web-page, so that there is already a datasource record set up for it - e.g.
# https://www.nbrowse.org.nz/cgi-bin/nutrigenomics/fetch.py?obid=/data/upload/nutrigen/NUTRIGENOMICS/T00GEO/T100RawAndNormalised.zip&context=default&target=ob
#
# Initial version : Alan McCulloch 8/2009 for the T100 series. (Previous T92 and T101 datasets
#     were imported using psql scripts)
#
# Change log : 
#


import sys
from types import *
import re
import os
import string
from datetime import date
import globalConf


#
# if this is being called (i.e. not just imported), then parse and check command 
# line arges, reset logging path (since imported modules will try to log to the 
# default path which is only writeable by apache)
#
if __name__ == "__main__":  # (so this block will only execute if this module is being run, not if it is being imported)
    if len(sys.argv) < 6:
       print "Useage : ./processGEONormalised.py logpath=mypath datasourcelsid=mylsid action=[test_import|do_import] format=[geo1 | other formats] datasetname=\"my short descriptive name\""
       print "Test Import Example : ./processGEONormalised.py logpath=log24082009 datasourcelsid=/data/upload/nutrigen/NUTRIGENOMICS/T00GEO/T100RawAndNormalised.zip action=test_import format=geo1 datasetname=\"GEO submission data for T100 experiment\""
       print "Do Import Example : ./processGEONormalised.py logpath=log24082009 datasourcelsid=/data/upload/nutrigen/NUTRIGENOMICS/T00GEO/T100RawAndNormalised.zip action=do_import format=geo1 datasetname=\"GEO submission data for T100 experiment\""
       print "Test Update Example : ./processGEONormalised.py logpath=log24082009 datasourcelsid=/data/upload/nutrigen/NUTRIGENOMICS/T00GEO/T100RawAndNormalised.zip action=test_update format=geo1 datasetname=\"GEO submission data for T100 experiment\" idtable=spotidmapT100"
       print "Do Update Example : ./processGEONormalised.py logpath=log24082009 datasourcelsid=/data/upload/nutrigen/NUTRIGENOMICS/T00GEO/T100RawAndNormalised.zip action=do_update format=geo1 datasetname=\"GEO submission data for T100 experiment\" idtable=spotidmapT100"
       print "Extract Example : ./processGEONormalised.py logpath=log24082009 datasourcelsid=/data/upload/nutrigen/NUTRIGENOMICS/T00GEO/T100RawAndNormalised.zip action=test_extract format=geo1 datasetname=\"GEO submission data for T100 experiment\""
       print "Extract Example : ./processGEONormalised.py logpath=log24082009 datasourcelsid=/data/upload/nutrigen/NUTRIGENOMICS/T00GEO/T100RawAndNormalised.zip action=do_extract format=geo1 datasetname=\"GEO submission data for T100 experiment\""
       print """
example geo1 format : 

Gene.Name       Gene.ID VALUE   CH1_SIG_MEAN    CH1_BKD_MEAN    CH2_SIG_MEAN    CH2_BKD_MEAN    NORM_INTENSITY
BrightCorner    BrightCorner    null    8190    373     724     521     11.2497468118058
BrightCorner    BrightCorner    null    7916    381     721     507     11.2222056731442
NegativeControl (-)3xSLv1       0.239288170150488       1236    414     511     517     9.634321254421
.
.
.
"""
       sys.exit(1)

    # get and parse command line args
    argDict = dict([ re.split('=',arg) for arg in sys.argv if re.search('=',arg) != None ])
    print "using %s"%str(argDict)

    if not 'logpath' in argDict:
       print "must specify path for logfiles"
       sys.exit(1)

    # check it exists and is a directory
    if not os.path.isdir(argDict["logpath"]):
       print "logpath %(logpath)s should be an existing (writeable) directory"%argDict
       sys.exit(1)

    globalConf.LOGPATH=argDict["logpath"]

    print  "(logging reset to %s)"%globalConf.LOGPATH

import agbrdfConf
import databaseModule
from dataImportModule import dataSourceOb
from brdfExceptionModule import brdfException


# config options
configs = {
   "geo1" : {
       "columns" : ["GENE.NAME","GENE.ID","VALUE","CH1_SIG_MEAN","CH1_BKD_MEAN","CH2_SIG_MEAN","CH2_BKD_MEAN","NORM_INTENSITY"],
       "insert_sql" : """
       insert into geosubmissiondata(
                sourcefile ,
                gene_name  ,
                spot_id    ,
                value  ,
                ch1_sig_mean ,
                ch1_bkd_mean ,
                ch2_sig_mean ,
                ch2_bkd_mean ,
                norm_intensity,
                filerecnum
       )
       values(%(geofile)s,%(GENE.NAME)s,%(GENE.ID)s,%(VALUE)s,%(CH1_SIG_MEAN)s,%(CH1_BKD_MEAN)s,%(CH2_SIG_MEAN)s,%(CH2_BKD_MEAN)s,%(NORM_INTENSITY)s,%(filerecnum)s)
     """,
     "update_sql1" : """
     update GEOSubmissionData set
     id_ref = (select
     gal_refnumber from %(idtable)s
     where %(idtable)s.recnum = GEOSubmissionData.filerecnum)
     where id_ref is null and voptypeid = (select obtypeid from obtype where displayname = '%(datasetname)s');
     """,
     "extract_sql1" : """
     select
     sourcefile,
     id_ref,
     Gene_Name,
     spot_id,
     VALUE,
     CH1_SIG_MEAN,
     CH1_BKD_MEAN,
     CH2_SIG_MEAN,
     CH2_BKD_MEAN,
     NORM_INTENSITY
     from
     GEOSubmissionData
     where voptypeid = (select obtypeid from obtype where displayname = '%(datasetname)s')
     order by
     sourcefile,
     id_ref
     """
   },
   "geo2" : {
       "columns" : ["PROBE.NAME", "GENE.NAME", "SYSTEMATIC.NAME", "X.CONTROL.TYPE", "VALUE", "CH1_SIG_MEAN", "CH1_BKD_MEAN", "CH2_SIG_MEAN", "CH2_BKD_MEAN", "GISFEATNONUNIFOL", "RISFEATNONUNIFOL", "GISFEATPOPNOL", "RISFEATPOPNOL"],
       "insert_sql" : """
       insert into geosubmissiondata(
                sourcefile ,
                spot_id,
                gene_name  ,
                genesymbol , 
                control_type,
                value  ,
                ch1_sig_mean ,
                ch1_bkd_mean ,
                ch2_sig_mean ,
                ch2_bkd_mean ,
                filerecnum,
                gisfeatnonunifol ,
                risfeatpopnol ,
                risfeatnonunifol ,
                gisfeatpopnol 
       )
       values(%(geofile)s,%(PROBE.NAME)s, %(GENE.NAME)s,%(SYSTEMATIC.NAME)s,%(X.CONTROL.TYPE)s,%(VALUE)s,%(CH1_SIG_MEAN)s,%(CH1_BKD_MEAN)s,%(CH2_SIG_MEAN)s,%(CH2_BKD_MEAN)s,%(filerecnum)s,%(GISFEATNONUNIFOL)s, %(RISFEATNONUNIFOL)s, %(GISFEATPOPNOL)s, %(RISFEATPOPNOL)s)
     """,
     "update_sql1" : """
     update GEOSubmissionData set
     id_ref = filerecnum where id_ref is null and voptypeid = (select obtypeid from obtype where displayname = '%(datasetname)s')
     """,
     "extract_sql1" : """
     select
     sourcefile,
     id_ref,
     Gene_Name,
     spot_id,
     genesymbol,
     VALUE,
     CH1_SIG_MEAN,
     CH1_BKD_MEAN,
     CH2_SIG_MEAN,
     CH2_BKD_MEAN,
     gisfeatnonunifol ,
     risfeatpopnol ,
     risfeatnonunifol ,
     gisfeatpopnol
     from
     GEOSubmissionData
     where voptypeid = (select obtypeid from obtype where displayname = '%(datasetname)s')
     order by
     sourcefile,
     id_ref
     """
   }

}


def processUpdates(args):

    print "in processUpdates"
    config = configs[args["format"]]

    connection=databaseModule.getConnection()
    updatecur = connection.cursor()

    for itemkey in config:
        if re.search("^update",itemkey) != None:
         
            sql = config[itemkey]%args

            print "executing %s"%sql

            if args["action"] == "test_update":
                print "(but only testing)"

            elif args["action"] == "do_update":
                updatecur.execute(sql)
                print "rowcount = %s"%updatecur.rowcount


    updatecur.close()
    connection.close()


#
# assumes the first column contains the name of the output file - i.e. 
# will break the extract on the first column , and output columns 2,....
#
def processExtracts(args):

    print "in processExtracts"
    config = configs[args["format"]]

    connection=databaseModule.getConnection()
    extractcur = connection.cursor()

    for itemkey in config:
        if re.search("^extract",itemkey) != None:

            sql = config[itemkey]%args

            print "executing %s"%sql

            if args["action"] == "test_extract":
                print "(but only testing)"

            elif args["action"] == "do_extract":
                extractcur.execute(sql)
                myrow=extractcur.fetchone()
                outfile = "%s.extract"%myrow[0]
                print "writing %s"%outfile
                mywriter = file(outfile,"w")
                colnames = [item[0] for item in extractcur.description]
                mywriter.write(reduce(lambda x,y:x+'\t'+y,colnames[1:]))
                mywriter.write("\n")
                while myrow != None:
                    if outfile != "%s.extract"%myrow[0]:
                        mywriter.close()
                        outfile = "%s.extract"%myrow[0]
                        mywriter = file(outfile,"w")
                        mywriter.write(reduce(lambda x,y:x+'\t'+y,colnames[1:]))
                        mywriter.write("\n")
                        print "writing %s"%outfile
                    mywriter.write(reduce(lambda x,y:str(x)+'\t'+str(y), [{True : '', False : item}[item == None] for item in myrow[1:]]))
                    mywriter.write("\n")
                    myrow=extractcur.fetchone()
                mywriter.close()



    extractcur.close()
    connection.close()

    
def processFiles(args):

    print "in processFiles processing %s"%str(args) 
    # create data source object and make it executable

    if "datasourcelsid" not in args or "action" not in args or "format" not in args:
        print "Useage : nutrigenomicsForms logpath=mypath datasourcelsid=mylsid"

    connection=databaseModule.getConnection()

    archive = dataSourceOb()

    archive.initFromDatabase(args["datasourcelsid"], connection)     

    print "archive initialised , with fields %s"%str(archive.databaseFields)

    # theoretically the datasourcetype should allow us to work out how to list contents but
    # users may have specified some random type, so work it out from the name
    if re.search("\.zip$",args["datasourcelsid"]) != None:
        print "(looks like a zip archive)"
    else:
        print "Sorry , only zip archives currently supported"
        sys.exit(1)



    print "getting archive contents using unzip -l  and parsing the output..."


    archive.databaseFields["datasourcetype"] = "Executable"
    #archive.databaseFields["datasourcecontent"] = 'unzip -l "%(physicalsourceuri)s"'%archive.databaseFields
    archive.databaseFields["datasourcecontent"] = 'unzip -c "%(physicalsourceuri)s" | grep inflating'%archive.databaseFields
    (errorcode, output) = archive.execute(connection,outfile=None)
    print "execute returned %s"%errorcode

    if errorcode != 0:
        print "exiting as execute returned error code"
        sys.exit(errorcode)

    print "archive contains : \n%s"%output

    # example : 
#  inflating: Normalized and raw data, reference as CH2, for slide IL-10week7sa75mediumfinal
#  inflating: Normalized and raw data, reference as CH2, for slide IL-10week7sa77mediumfinal
#  inflating: Normalized and raw data, reference as CH2, for slide IL-10week7sa78mediumfinal

    # get an array of files
    records  = re.split("\r*\n\r*",output)
    files = [re.split("inflating: ", record)[1].strip() for record in records]

    print "processing files : %s"%files


    insertCursor = connection.cursor()

    # for each file in the archive
    for geofile in files:
        
        # execute the datasource to extract the file contents
        print "processing %s"%geofile
        archive.databaseFields["datasourcecontent"] = 'unzip -p "%(physicalsourceuri)s" "%(geofile)s"'% {
                 "physicalsourceuri" : archive.databaseFields["physicalsourceuri"],
                 "geofile" : geofile
        }
        (errorcode, output) = archive.execute(connection,outfile=None)
        print "execute returned %s"%errorcode

        #if args["action"] == "test":
        #    print "file content : \n%s"%output

        # parse contents into records
        records  = [item.strip() for item in re.split("\r*\n\r*",output) if len(item.strip()) > 1]
        records = [re.split("\t",item) for item in records if len(re.split("\t",item)) > 1]

        print records[1:5]
        print ".\n.\n.\netc"
 

        # check the format of the contents  : column headngs
        format = configs[args["format"]]
        headings = [item.upper() for item in records[0]]
        headings = [re.sub('^"','',item.upper()) for item in headings]
        headings = [re.sub('"$','',item.upper()) for item in headings]
        print "verifying format %s"%format

        for field in headings:
            if field not in format["columns"]:
                print "error - unsupported column name %s (columns are : %s)"%(field, str(format["columns"]))
                sys.exit(1)

        print "data format looks OK"

        insertCount = 0
        filerecnum = 0
        for record in records[1:]:

            filerecnum += 1

            # translate "null" , "NULL" , "NA" etc
            record = [re.sub('^"','',item) for item in record]
            record = [re.sub('"$','',item) for item in record]
            record = [{True : None, False : item}[item.lower() in ("null","na",'"null"','"na"')] for item in record]

   

            fieldDict = dict(zip(headings,record)) 
            fieldDict["geofile"] = geofile
            fieldDict["filerecnum"] = filerecnum
            if args["action"] == "test_import":
                print("will update database with \n%s \n(but only testing)"%format["insert_sql"]%fieldDict)
                insertCount += 1
                if insertCount%10 == 9:
                    break
            else:
                insertCursor.execute(format["insert_sql"], fieldDict)
                insertCount += 1
                if insertCount%50 == 49:
                    print "inserted %s"%insertCount
                    connection.commit()


    if args["action"] == "do_import":
        connection.commit()
        # set up as a new type in contributed table
        print "installing data as contributed type %(datasetname)s..."%args
        sql = """
           select installContributedTable('GEOSubmissionData','%(datasetname)s','%(datasetname)s')
        """%args
        insertCursor.execute(sql)
     

    connection.commit()
    connection.close()



if __name__ == "__main__":
    if argDict["action"] in ['test_import','do_import']:   
        processFiles(argDict)
    elif argDict["action"] in ['test_update','do_update']:
        processUpdates(argDict)
    elif argDict["action"] in ['test_extract','do_extract']:
        processExtracts(argDict)
    else:
        print "unknown action %(action)s"%argDict

   





