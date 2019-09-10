#
# This module provides database related constants, methods, and
# classes. It is intended to be modified when a brdf instance is installed.
# to use the specific database name, host etc. This is the only place
# where these need to be updated
#
import re
import sys
import types
from  SparseMatrix import sparse, dot
import csv
import logging
import os

import globalConf

############################
# Set up logging
############################
logger = logging.getLogger('tiler')
hdlr = logging.FileHandler(os.path.join(globalConf.LOGPATH,'tiler.log'))
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr) 
logger.setLevel(logging.INFO)     



class graphsparse(sparse):
    """
    This class is a sparse adjacency matrix. Each element of the graph is itself a dictionary
    """

def isGraphSparse(x):
    return hasattr(x,'__class__') and x.__class__ is graphsparse


def getPairedBAC(infile,outfile):
    """ obtain paired BACS from a file of BES positions like this :
    
  samplename  |                    xreflsid                     | locationstart | locationstop
--------------+-------------------------------------------------+---------------+--------------
 CH243-338A8  | NCBI.CH243-338A8.DU479959.location.vsheep1.2.1  |        140192 |       140364
 CH243-338A8  | NCBI.CH243-338A8.DU481531.location.vsheep1.2.1  |        315054 |       315296
 CH243-432F19 | NCBI.CH243-432F19.DU230943.location.vsheep1.2.1 |       1515744 |      1515931
 CH243-304H20 | NCBI.CH243-304H20.DU492527.location.vsheep1.2.1 |       1520210 |      1520954
 CH243-398N20 | NCBI.CH243-398N20.DU216873.location.vsheep1.2.1 |       1528096 |      1528212
 CH243-254C16 | NCBI.CH243-254C16.DU418481.location.vsheep1.2.1 |       1528222 |      1530067
 CH243-310D3  | NCBI.CH243-310D3.DU494296.location.vsheep1.2.1  |       1573438 |      1573767
 CH243-482F23 | NCBI.CH243-482F23.DU187799.location.vsheep1.2.1 |       1573493 |      1574109
 CH243-308G14 | NCBI.CH243-308G14.DU500443.location.vsheep1.2.1 |       1606029 |      1606147

    Example SQL query


    select
        s.samplename,
        glf.xreflsid,
        glf.locationstart,
        glf.locationstop
    from
        (geneticlocationfact glf join sequencingfunction sf on
        glf.biosequenceob = sf.biosequenceob and
        glf.chromosomename = 'OAR26' and
        glf.mapname = 'vsheep1.2.1') join biosampleob s on
        sf.biosampleob = s.obid and
        s.sampletype = 'Genomic Clone' 
    order by
        glf.locationstart,glf.locationstop        
 
"""

 
    reader = open(infile,"r")
    rowcount = 0
    pairedDict={}
    for row in reader:
        #print row
        if re.search('--',row) != None:
            continue
        rowcount += 1
        if rowcount == 1:
            fieldNames = re.split('\s+\|\s+',row.strip())
            continue
        else:
            row = re.split('\s+\|\s+',row.strip())

        fieldDict = dict(zip(fieldNames,row))
        fieldDict['locationstart'] = int(fieldDict['locationstart'])
        fieldDict['locationstop'] = int(fieldDict['locationstop'])

        # if BAC not in paired dict add
        if fieldDict['samplename'] not in pairedDict:
            pairedDict[fieldDict['samplename']] = [min(fieldDict['locationstart'],fieldDict['locationstop'])]
        else:
            if len(pairedDict[fieldDict['samplename']]) != 1:
                raise brdfException("error - incoherent BAC %s"%fieldDict['samplename'])
            
            pairedDict[fieldDict['samplename']].append(max(fieldDict['locationstart'],fieldDict['locationstop']))
            pairedDict[fieldDict['samplename']].sort()

    # sort the dictionary of pairs, by start
    keys = pairedDict.keys()
    keys.sort(lambda x,y:pairedDict[x][0] - pairedDict[y][0])

    writer=open(outfile,"w")
    rowcount = 0
    for bac in keys:
        rowcount += 1
        #print bac
        #print str(pairedDict[bac])
        writer.write("%s,%s,%s,%s\n"%(bac,pairedDict[bac][0],pairedDict[bac][1],rowcount))
        #print "%s,%s,%s"%(bac,pairedDict[bac][0],pairedDict[bac][1])

    writer.close()



def loadSparse(infile,startrow,endrow,startOverlaps={}):
    """ This method sets up an adjacency matrix from an ordered extract of tiles and tile start and stop
    positions that looks (e.g.) like this :
CH243-338A8,140192,315296,1
CH243-432F19,1515744,1661945,2
CH243-304H20,1520210,1707923,3
CH243-398N20,1528096,1724646,4
CH243-254C16,1528222,1672884,5
CH243-310D3,1573438,1815520,6
CH243-482F23,1573493,1841884,7
(where the start and stop are the endpoints of two different BACs)


    In this matrix, adjacency means that there is an overlap. The adjacency is not symmetric - e.g.

    a ---------
         b--------
             c----------
             d----------


    then in the adjacency graph a->b->c->d and d->c

    The algorithm is to add and remove BACS , sorted by start , to a list. As each BAC is added,
    any adjacency between that BAC and others in the list is calculated and set up.
    Then each existing member of the list is checked to see whether its end point
    is before the start point of the BAC just added. If it is , then it can be removed, as it
    cannot overlap with a any future BACS."""
    
    
    a = graphsparse()
    reader = csv.reader(open(infile,"r"))
    overlapDict = startOverlaps

    rowcount = 0
    for row in reader:
        rowcount += 1

        if rowcount > endrow:
            break

        if rowcount < startrow:
            continue

        
        #print row

        (tile,start,stop,tilenumber) = (row[0],int(row[1]),int(row[2]),int(row[3]))
 
        # add this tile to the overlap list
        overlapDict[tile] = (start,stop,tilenumber)
            
        # for each element of the overlap
        for item in overlapDict.keys():

            if item == tile:
                continue
        
            # if the end of the existing element is before the start of the new element, remove it
            if overlapDict[item][1] < start:
                del overlapDict[item]
                continue
                
            # if the start of the new element is >= the existing element start, and <= existing stop , set up existing -> new
            # unless we have new->existing (we do not want circular paths)
            if start >= overlapDict[item][0] and start <= overlapDict[item][1]:
                #print "making overlap %s --> %s"%(item,bac)
                if (tilenumber, overlapDict[item][2]) not in a:
                    a[(overlapDict[item][2],tilenumber)] = {'d' : 1}
            # if the start of the new element == the start of the existing element , set up new - > existing, unless
            # we have existing->new (we do not want circular paths)
            if start == overlapDict[item][0]:
                if (overlapDict[item][2], tilenumber) not in a:
                    #print "make overlap %s --> %s"%(bac,item)
                    a[(tilenumber,overlapDict[item][2])] = {'d' : 1}

        if rowcount%50 == 0:
            logger.info("loadSpare : rowcount, adjacency matrix size : %s , %s"%(rowcount,len(a)))


    return (a,overlapDict)


def loadMetaSparse(danglingpaths,danglingoverlaps):
    """
    this method loads a sparse adjacency matrix with paths and overlaps
    from a sub-tiling done by sub_tile.Example value danglingPaths :
    [[((35, 50), {'d': 3})], [((50, 100), {'d': 9})]]
    Example value of dangling overlaps :
    [{'CH243-11H10': (3101309, 3243812, 47), 'CH243-159B13': (3114847, 3243814, 48), 'CH243-325N1': (3184419, 3418496, 50),
    'CH243-476J14': (3176772, 3371812, 49), 'CH243-500F7': (3043348, 3243827, 46)}, {'CH243-191P20': (4599292, 4763919, 100),
    'CH243-434J18': (4548331, 4763919, 99), 'CH243-96N11': (4444509, 4599985, 94), 'CH243-216N9': (4447923, 4638997, 95),
    'CH243-190O3': (4460157, 4645298, 96), 'CH243-169G22': (4542222, 4696724, 98), 'CH243-108C18': (4443957, 4653780, 93),
    'CH243-379K11': (4524684, 4671614, 97)}]
    """
    a = graphsparse()
    for ibundle in range(0,len(danglingpaths)):
        pathbundle = danglingpaths[ibundle]

        # add all paths in the pathbundle
        for path in pathbundle:
            a[path[0]] = path[1]

    for ibundle in range(0,len(danglingoverlaps)):        
        overlapdict = danglingoverlaps[ibundle]



        # for each tile
        for tile in overlapdict.keys():
            (start,stop,tilenumber) = (overlapdict[tile][0],overlapdict[tile][1],overlapdict[tile][2])
            
            # for each element of the overlap
            for item in overlapdict.keys():
            
                if item == tile:
                    continue
        
                # if the end of the existing element is before the start of the new element, remove it
                if overlapdict[item][1] < start:
                    del overlapdict[item]
                    continue
                
                # if the start of the new element is >= the existing element start, and <= existing stop , set up existing -> new
                # unless we have new->existing (we do not want circular paths)
                if start >= overlapdict[item][0] and start <= overlapdict[item][1]:
                    #print "making overlap %s --> %s"%(item,bac)
                    if (tilenumber, overlapdict[item][2]) not in a:
                        a[(overlapdict[item][2],tilenumber)] = {'d' : 1}
                # if the start of the new element == the start of the existing element , set up new - > existing, unless
                # we have existing->new (we do not want circular paths)
                if start == overlapdict[item][0]:
                    if (overlapdict[item][2], tilenumber) not in a:
                        #print "make overlap %s --> %s"%(bac,item)
                        a[(tilenumber,overlapdict[item][2])] = {'d' : 1}
                        

    logger.info("Metasparse : %s"%str(a.out))
    return a
               
                         
        

def tilegraphdot(a,b,producttype = 'STANDARD SCALAR'):
    """
    defines the product of two matrices each of which is an adjacency
    matrix of BACs, where adjacency means the BACS overlap.

    In a simple adjacency matrix for a directed graph, each element (i,j) is either 1 or 0 ,
    depending on whether there is a directed edge linking element i to element j

    Rather than store 1 or 0 , you may store a probability for a link.

    More generally , a link my have other attributes such as length, as well as a probability
    weighting , so that you may

    In the BAC adjacency matrix , each element is a dictionary which stores
    attributes of the link.
    """

    
    if producttype == 'STANDARD SCALAR':
        """ this product is a standard dot product of two vectors """
        if isGraphSparse(a) and isGraphSparse(b):
            #if a.size()[1] != b.size()[0]:
                #print '**Warning shapes do not match in dot(sparse, sparse)'
            new = graphsparse({})
            n = min([a.size()[1], b.size()[0]])
            for i in range(a.size()[0]):
                for j in range(b.size()[1]):
                    sum = 0.
        	    for k in range(n):
                        elementa = a.get((i,k),None)
                        elementb = b.get((k,j),None)
                        if elementa != None and elementb != None:
                            sum += elementa['d']*elementb['d']
                    if sum != 0.:
                        new[(i,j)] = {'d' : sum}
	return new
    elif producttype == 'MINIMUM DISTANCE':
        """ this product implements a dot product which will result in the minimum
        distance between two points being calculated. In this "product", the usual
        multipliction a x b becomes addition a + b, and the usual addition a+b becomes min(a,b)
        """
        if isGraphSparse(a) and isGraphSparse(b):
            #if a.size()[1] != b.size()[0]:
                #print '**Warning shapes do not match in dot(sparse, sparse)'
            new = graphsparse({})
            n = min([a.size()[1], b.size()[0]])
            for i in range(a.size()[0]):
                for j in range(b.size()[1]):
                    sum = None
        	    for k in range(n):
                        elementa = a.get((i,k),None)
                        elementb = b.get((k,j),None)
                        if elementa != None and elementb != None:
                            if sum != None:
                                sum = min ( sum , (elementa['d'] + elementb['d']))
                            else:
                                sum = elementa['d'] + elementb['d']
                    if sum != None:
                        existingelement = a.get((i,j),None)
                        if existingelement != None:
                            new[(i,j)] = {'d' : min(sum,existingelement['d']) }
                        else:
                            new[(i,j)] = {'d' : sum}
                    else:
                        existingelement = a.get((i,j),None)
                        if existingelement != None:
                            new[(i,j)] = {'d' : existingelement['d'] }

                        
                            
            return new        
    else:
	raise TypeError, 'in dot'


def tracebackstep(p,a,i,j,producttype):
    """
    This method takes a product matrix p, typically representing minium paths ,
    (or maximum path-scores, or whatever the objective function is) , obtained by "multiplying"
    up (using a suitable definition of multiplication, such that product matrices contain
    minimal paths) a matrix a of path lengths between points - and executes a traceback to
    recover a minimum (/maximum etc) scoring path between points i and j.

    It is assumed that the matrix has converged, so that each entry (i,j) represents a minimum
    path length between points i and j

    Then for element (i,j) , i.e. d(i-----> j) , the first step of the traceback must be
    to find k such that i -----> k ----> j where p(i,k) + a(k,j) = p(i,j).

    (Since the part of the minimal path up to the penultimate element must itself be minimal
    - if it were not then we could replace it with the length of the minimal path to reduce
    the length to the final element, contradicting the assumption that we are tracing back the
    minimum path)

    We then repeat the process for p(i,k).

    This will lead to tracing back a series of elements of matrix a, to reoover the minimum path.
    """

    if i == j:
        return None


    logger.info("starting traceback")
            
    logger.info("seeking trace step from %d to %d"%(i,j))
    tracestep = None
    if producttype == 'MINIMUM DISTANCE':
        """In this "product", the usual
        multipliction a x b becomes addition a + b, and the usual addition a+b becomes min(a,b)"""

        #Loop over k through entries p(i,k) in p
        for k in range(0,1+p.size()[0]):
            testback = ( p.get((i,k),None) , a.get((k,j),None) , p.get((i,j),None) )
            #print("trying %d-->%d-->%d : %s + %s = %s "%((i,k,j)+testback))
            testback = [element for element in testback if element != None]
            if len(testback) == 3:
                if (testback[0]['d'] + testback[1]['d']) == testback[2]['d']:
                    tracestep = k
                    break

        if tracestep == None:
            # see if we can find a single step in the a matrix
            testback = ( a.get((i,j),None) , p.get((i,j),None) )
            testback = [element for element in testback if element != None]
            if testback[0]['d'] == testback[1]['d']:
                tracestep = i
            
        
    logger.info("finished traceback")
    
    return tracestep


def traceback(p,a,i,j,producttype = 'MINIMUM DISTANCE'):
    tracebackpath = [j]

    nextstep = tracebackstep(p,a,i,j,producttype)

    while nextstep != None:
        tracebackpath.append(nextstep)
        nextstep = tracebackstep(p,a,i,nextstep,producttype)

    return tracebackpath
                    
                    
        

def sub_tile(pairfilename=None, startrow=None, endrow=None, a=None, subStartOverlaps={}):
    # this method constucts a tiling path that may be a sub-path of
    # a longer tiling path. If a is passed in , then this is used as the adjacency
    # matrix, otherwise the adjacency matrix is loaded from source data
    # It loads at most maxrec records from the sorted
    # adjacency file , calculates longest minimum tiling paths, then
    # returns a data structure containig the following :
    # 1. accumulated record count
    # 2. completed minimum paths
    # 3. incompleted minimum paths
    # 4. the set of overlaps as at the end point.
    logger.info("\n\nstarting sub_tile")
    logger.info("DEBUG : subStartOverlaps = %s"%str(subStartOverlaps))

    
    if a == None:
        (a,danglingOverlaps) = loadSparse(pairfilename,startrow,endrow, startOverlaps=subStartOverlaps)
    else:
        danglingOverlaps = {}



    #logger.info("startOverlaps : %s"%str(startOverlaps))
    logger.info("dangling overlaps : %s"%str(danglingOverlaps))
    #a.out()
    #basictestmain2()
    b = tilegraphdot(a,a,'MINIMUM DISTANCE')
    #b.out()
    lastkeys = b.keys()
    logger.info("calculating paths...")
    iterationcount = 0
    while True:
        iterationcount += 1
        logger.info("Step %s"%iterationcount)
        b = tilegraphdot(b,a,'MINIMUM DISTANCE')
        #b.out()
        logger.info("Matrix size : %s"%len(b))
        newkeys = b.keys()
        if newkeys == lastkeys:
            logger.info("converged")
            break
        else:
            lastkeys=newkeys

    #b.out()

    # find the distinct dangling paths 
    paths=b.keys()
    paths.sort(lambda x,y:x[1]-y[1])
    logger.info("all paths : %s"%str(paths))
    #endpaths = [item for item in paths if item[1] not in [item[0] for item in paths]]


    # dangling paths, are those that have an end BAC that is in the dangling overlap set, or a start tile that
    # is in the startOverlaps. Note that there is some redundancy in the dangling paths - e.g. we may have
    # 35->46 , 46->50 and 35->50 as dangling paths, but we can't removethe first two , because it may be that
    # we need 46 to join up to a dangling path in the next chunk.
    danglingpaths1 = [item for item in paths if item[1] in [ditem[2] for ditem in danglingOverlaps.values()]]
    logger.info("dangling paths (1): %s"%str(danglingpaths1))
    danglingpaths2 = [item for item in paths if item[1] in [ditem[2] for ditem in subStartOverlaps.values()]]
    logger.info("dangling paths (2): %s"%str(danglingpaths2))    
    danglingpaths = danglingpaths1 + danglingpaths2

    #
    # this section incorrectly reduced the redundancy of the dangling paths
    #logger.info("dangling paths (all): %s"%str(danglingpaths))
    #danglingpaths = [item for item in danglingpaths if item[0] not in [ditem[1] for ditem in paths]]
    #logger.info("dangling paths (filtered 1): %s"%str(danglingpaths))
    #danglingpaths = [item for item in danglingpaths if item[1] not in [ditem[0] for ditem in paths]]
    #logger.info("dangling paths (filtered 2): %s"%str(danglingpaths))
    danglingdict=zip(danglingpaths,[b[path] for path in danglingpaths])

    

    # complete paths are those that have an end BAC that is not a start BAC, and a start bac that is not an end bac, and whose
    # tiles are not in the start overlap set, or the dangling overlap set
    completedpaths = [item for item in paths if item[1] not in [ditem[0] for ditem in paths]]
    logger.info("completed paths (1): %s"%str(completedpaths))
    completedpaths = [item for item in completedpaths if item[0] not in [ditem[1] for ditem in paths]]
    logger.info("completed paths (2): %s"%str(completedpaths))    
    completedpaths = [item for item in completedpaths if item not in danglingpaths]
    logger.info("completed paths (3): %s"%str(completedpaths))    

    # when processing a metafile, there may be multiple completedpaths for a given end path.
    # Therefore filter completedpaths to obtain maximal end paths

    completedpathsdict={}
    for path in completedpaths:
        if path[1] not in completedpathsdict:
            completedpathsdict[path[1]] = path[0]
        else:
            if path[0] < completedpathsdict[path[1]]:
                completedpathsdict[path[1]] = path[0]

    completedpaths = [(item[1],item[0]) for item in completedpathsdict.items()]
    completedpaths.sort(lambda x,y:x[0]-y[0])

            
    
    logger.info("completed paths : %s"%str(completedpaths))


    logger.info("""
    tracing back completed paths...
    -------------------------------
    """)
    completedTracebacks = []
    for path in completedpaths:
        logger.info("tracing path %s"%str(path))
        tilingpath=traceback(b,a,path[0],path[1])
        logger.info("tiling path index : %s"%str(tilingpath))
        completedTracebacks.append(tilingpath)


    logger.info("""
    tracing back dangling paths...
    ------------------------------
    """)
    danglingTracebacks = []
    for path in danglingpaths:
        logger.info("tracing path %s"%str(path))
        tilingpath=traceback(b,a,path[0],path[1])
        logger.info("tiling path index : %s"%str(tilingpath))
        danglingTracebacks.append(tilingpath)

        

    #get which BACs
    #reader = csv.reader(open(pairfilename,"r"))
    #tilingDict = {}
    #for row in reader:
    #    (bac,start,stop,bacnumber) = (row[0],int(row[1]),int(row[2]),int(row[3]))
    #    if bacnumber in tilingpath:
    #        tilingDict[bacnumber] = row
    #
    #print "tiling path : "
    #for bacnumber in tilingpath:
    #    print tilingDict[bacnumber]    
    

    return (endrow,completedpaths,danglingdict,completedTracebacks,danglingTracebacks,danglingOverlaps)




def tilemain(infilename,pairfilename,outfile,redopairfile=True):
    #infile="C:/working/sheepgenomics/bactiling/oar26bes.dat"

    logger.info("""
=========================================
Beginning tile session
infile=%s
pairfilename=%s
outfile=%s
=========================================
"""%(infilename,pairfilename,outfile))
    if redopairfile:
        getPairedBAC(infilename,pairfilename)

    completedpaths=[]
    danglingpaths=[]
    completedtracebacks = []
    danglingtracebacks = []
    danglingoverlaps = []

    #filesize = 1531
    chunksize = 50
    subdanglingOverlaps = {}
    for chunknumber in range(0,31):
        (cumulativeCount,subcompletedpaths,subdanglingpaths,subcompletedTracebacks,subdanglingTracebacks,subdanglingOverlaps) = \
                            sub_tile(pairfilename,chunksize*chunknumber,chunksize*(1+chunknumber),subStartOverlaps=subdanglingOverlaps.copy())        
        completedpaths.append(subcompletedpaths)
        danglingpaths.append(subdanglingpaths)
        completedtracebacks.append(subcompletedTracebacks)
        danglingtracebacks.append(subdanglingTracebacks)
        danglingoverlaps.append(subdanglingOverlaps.copy())        


    logger.info("Completed sub-Paths : %s"%str(completedpaths))
    logger.info("Dangling sub-Paths : %s"%str(danglingpaths))
    logger.info("Completed sub-Tracebacks : %s"%str(completedtracebacks))
    logger.info("Dangling sub-Tracebacks : %s"%str(danglingtracebacks))
    logger.info("Dangling sub-Overlaps : %s"%str(danglingoverlaps))


    # we now need to find a meta-tiling path through the dangling paths
    logger.info("""
    Starting metatile
    -----------------
    """)    
    logger.info("\n\nSetting up metapairfile")
    a=loadMetaSparse(danglingpaths,danglingoverlaps)
    (junk,metacompletedpaths,metadanglingpaths,metacompletedtracebacks,metadanglingtracebacks,metadanglingoverlaps)=sub_tile(a=a)

    logger.info("Completed meta-Paths : %s"%str(metacompletedpaths))
    logger.info("Dangling meta-Paths : %s"%str(metadanglingpaths))
    logger.info("Completed meta-Tracebacks : %s"%str(metacompletedtracebacks))
    logger.info("Dangling meta-Tracebacks : %s"%str(metadanglingtracebacks))
    logger.info("Dangling meta-Overlaps : %s"%str(metadanglingoverlaps))


    # process the metatracebacks. Each metatraceback is a connected series of dangling tracebacks from each
    # sub-tiling, so that we need to glue together the subtracebacks
    # example of metatracebacks :
    # [[100, 50, 35]]
    # example of dangling sub-tracebacks :
    # Dangling sub-Tracebacks : [[[50, 46, 37, 35]], [[100, 93, 92, 87, 80, 76, 72, 68, 60, 50]]]
    logger.info("Starting metatraceback")
    for metatraceback in metacompletedtracebacks:
        logger.info("processing metatraceback %s"%str(metatraceback))

        # initialiase completed traceback
        completedtraceback=[metatraceback[0]]
        for itileid in range(0,len(metatraceback)-1):
            endtile=metatraceback[itileid]
            starttile=metatraceback[itileid+1]
            logger.info("looking for traceback from %s to %s"%(endtile,starttile))

            # find a dangling sub-traceback from endtile to starttile
            for chunk in danglingtracebacks:
                for subtraceback in chunk:
                    if (endtile,starttile) == (subtraceback[0],subtraceback[-1]):
                        logger.info("....found %s"%str(subtraceback))
                        completedtraceback += subtraceback[1:]
                        break

        completedtracebacks.append([completedtraceback])

    completedtracebacks = [item for item in completedtracebacks if len(item) > 0]
    logger.info("*** All Completed Tracebacks : %s"%str(completedtracebacks))  
    completedtracebacks.sort(lambda x,y:x[0][0]-y[0][0])


    # write the completed tiling paths to a file
    logger.info("Merging tile definitions and writing tiling paths")
    reader = csv.reader(open(pairfilename,"r"))
    writer=open(outfile,"w")
    writer.write("*** All Completed Tracebacks : %s"%str(completedtracebacks))

    # get just the tile defintions we need
    tilingDict = {}
    for row in reader:
        (tilename,start,stop,tileid) = (row[0],int(row[1]),int(row[2]),int(row[3]))
        for chunk in completedtracebacks:
            for tilingpath in chunk:
                if tileid in tilingpath:
                    tilingDict[tileid] = row
    logger.info(tilingDict)

    pathcount = 0
    for chunk in completedtracebacks:
        for tilingpath in chunk:
            pathcount += 1
            writer.write("""
Tiling path : %s
----------------
""" %pathcount)
            tilingpath.reverse()
            for tileid in tilingpath:
                writer.write(str(tilingDict[tileid])+'\n')

    writer.close()

    logger.info("""
=========================================
Completed tile session
=========================================
""")    

          


if __name__ == "__main__":
    #tilemain("C:/working/sheepgenomics/bactiling/oar26bes.dat","c:/temp/paired.txt","c:/temp/oar26tilingpaths.txt",False)
    tilemain("/data/home/seqstore/agbrdf/tiling/oar26bes.dat","/data/home/seqstore/agbrdf/tiling/paired.txt","/data/home/seqstore/agbrdf/tiling/oar26tilingpaths.txt",False)
"""
Test results on OAR26

2 chunks 50 each
================

*** All Completed Tracebacks : [[[25, 14, 9, 2], [34, 27, 26]], [], [100, 93, 92, 87, 80, 76, 72, 68, 60, 50, 46, 37, 35]]


1 chunk 100
===========

Completed sub-Tracebacks : [[[25, 14, 9, 2], [34, 27, 26]]]
Dangling sub-Tracebacks : [[[100, 93, 92, 87, 80, 76, 72, 68, 60, 50, 46, 37, 35]]]

*** All Completed Tracebacks : [[[25, 14, 9, 2], [34, 27, 26]], [100, 93, 92, 87, 80, 76, 72, 68, 60, 50, 46, 37, 35]]


4 chunks 25 each
================
*** All Completed Tracebacks : [[], [[34, 27, 26]], [], [], [25, 14, 9, 2], [100, 93, 92, 87, 80, 76, 75, 70, 64, 50, 46, 37, 35]]
"""







############################# older test functions #######################
def basictestmain2():
    a = graphsparse()
    b = graphsparse()

    print 'a.__doc__=',a.__doc__


    """
    Example graph  :

        1           1         4
    a -------> b -------> c------d
      -------------------> 
             3
               b----------------->d
                         2
    """
   
    a[(10,11)] = {'d' : 1.0}
    a[(11,12)] = {'d' : 1.0}
    a[(12,13)] = {'d' : 4.0}
    a[(10,12)] = {'d' : 3.0}
    a[(11,13)] = {'d' : 2.0}
    #a[(0,3)] = {'d' : 1.0}

    # if we wish to calculate path with minimum links, then replace all d with 1
    for key in a.keys():
        a[key]['d'] = 1

    a.out()

    b = tilegraphdot(a,a,'MINIMUM DISTANCE')

    b.out()

    b = tilegraphdot(b,a,'MINIMUM DISTANCE')

    b.out()

    b = tilegraphdot(b,a,'MINIMUM DISTANCE')

    b.out()

    print "executing traceback"
    tracebackpath = traceback(b,a,10,13,producttype = 'MINIMUM DISTANCE')
    print tracebackpath


    

    
    
    return



def basictestmain1():
    a = sparse()
    b = sparse()

    print 'a.__doc__=',a.__doc__

    a[(0,0)] = 2.0
    a[(1,1)] = 2.0

    a.out()

    b[(0,0)] = 1.0
    b[(0,1)] = 2.0
    b[(1,0)] = 3.0
    b[(1,1)] = 4.0

    b.out()

    c = dot(a,b)

    c.out()

    

    return
    
    



            

    



    
