"""
Copyright 2007 AgResearch (NZ)

This module implements a dynamic programmming algorithm for finding optimal tiling paths
through a set of overlapping one dimensional tiles.

Starting with a set of tiles each having a start and stop position in some coordinate system
(e.g. a set of BAC clones , with positions on some reference genome), overlaps are calculated and 
loaded into a sparse matrix implementation of a directed graph data structure , with tiles
connected by a vertex if they overlap, each vertex having a cost assigned, which is
to be minimised. A cost of 1 will give shortest path. Other costs can be assigned
to optimise according to different objectives - for example, to minimise the uncertainty of
the path, if the tile positions are uncertain and some confidence measure for the
position is available.

Iterated sparse matrix multiplication on the graph gives the cost of the optimal path between
any two tiles, and a traceback through the final converged matrix gives the optimal
path.

The module supports calculation of second or third paths that are optimal relative to
a given primary path in some way - for example, a second path where overlaps are staggered
relative to the first path.  This is done by adjusting the cost attached to each vertex ,
to include the position of that vertex relative to a given primary path. (This can be thought of 
as projecting the vertex onto the primary path, to obtain a projected length of the vertex)

The sparse matrix module used (http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/52275) was
developed by Alexander Pletzer



"""
import re
import sys
import types
from  SparseMatrix import sparse, dot
import csv
import logging
import os
import math

import globalConf

############################
# Set up logging
############################
logger = logging.getLogger('tiler')
hdlr = logging.FileHandler(os.path.join(globalConf.LOGPATH,'tiler.log'))
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
bareformatter = logging.Formatter('%(message)s')
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

    Example SQL query of the brdf database to extract this : 


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

def getProjectionPath(infile):
    """ this method loads a tiling path previously calculated, from a file like this :


 ---------------------------------------------------------------   
*** All Completed Tracebacks : [[[25, 14, 9, 2], [34, 27, 26]], [[50, 46, 37, 35]]]

***GFF for paths***

reference = OAR26

tiling-pathA        CH243-432F19_2 1515744..1661945
tiling-pathA        CH243-78C21_9 1644813..1870023
tiling-pathA        CH243-262D21_14 1842421..2107267
tiling-pathA        CH243-141C23_25 2011852..2274015
tiling-pathA        CH243-54B4_26 2339622..2477720
tiling-pathA        CH243-206K6_27 2348438..2510356
tiling-pathA        CH243-345J19_34 2488592..2654689
tiling-pathA        CH243-241F18_35 2720297..2874966
tiling-pathA        CH243-140E2_37 2808427..3045839
tiling-pathA        CH243-500F7_46 3043348..3243827
tiling-pathA        CH243-325N1_50 3184419..3418496


[tiling-pathA]
glyph = generic
connector = dashed
bump = 1

etc
-------------------------------------------------------------------

.....into a sorted array of tuples like this :

['CH243-432F19', '1515744', '1661945', '2']
['CH243-78C21', '1644813', '1870023', '9']
['CH243-262D21', '1842421', '2107267', '14']
['CH243-141C23', '2011852', '2274015', '25']
['CH243-54B4', '2339622', '2477720', '26']
['CH243-206K6', '2348438', '2510356', '27']
['CH243-345J19', '2488592', '2654689', '34']
['CH243-241F18', '2720297', '2874966', '35']
['CH243-140E2', '2808427', '3045839', '37']
['CH243-500F7', '3043348', '3243827', '46']
['CH243-325N1', '3184419', '3418496', '50']
['CH243-477N24', '3372071', '3539433', '60']


   """
    reader=open(infile,"r")

    logger.info("loading projection path")
    path =[]
    for row in reader:
        if re.search("\d\s*\.\.\s*\d",row) != None:
            tokens1 = re.split('\s+',row.strip())
            tokens2 = re.split('_',tokens1[1])
            tokens3 = re.split('\s*\.\.\s*',tokens1[2])
            path.append([ tokens2[0], tokens3[0], tokens3[1], tokens2[1] ])


    logger.info("loaded %s records"%len(path))
    path.sort(lambda x,y:int(x[1]) - int(y[1]))

    return path

    
        


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


    then in the adjacency graph a->b->c->d and d->c but we do not enter b->a etc.


    However in

        a ---------
                b--------
            c----------------


    we add a->c->b and also a->b->c

    

    The algorithm is to add and remove tiles , sorted by start , to a list. As each tile is added,
    any adjacency between that tile and others in the list is calculated and set up.
    Then each existing member of the list is checked to see whether its end point
    is before the start point of the tile just added. If it is , then it can be removed, as it
    cannot overlap with a any future tiles (since the file ew are reading is assumed to be sorted by start)."""
    
    
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

            # if the start of the new element is >= the existing element start and the end is <= the
            # existing stop - i.e. the new is contained in existing - then set up both existing->new and new->existing
            if start >= overlapDict[item][0] and stop <= overlapDict[item][1]:
                # existing -> new
                a[(overlapDict[item][2],tilenumber)] = {'d' : 1, 's' : (overlapDict[item][0],stop )}
                # new -> existing
                a[(tilenumber,overlapDict[item][2])] = {'d' : 1, 's' : (start, overlapDict[item][1])}                  
            # else if the start of the new element is >= the existing element start, and <= existing stop , set up existing -> new,
            # and also new -> existing if new start = existing start
            elif start >= overlapDict[item][0] and start <= overlapDict[item][1]:
                a[(overlapDict[item][2],tilenumber)] = {'d' : 1, 's' : (overlapDict[item][0],stop )}
                # if the start of the new element == the start of the existing element , set up new - > existing 
                if start == overlapDict[item][0]:
                    a[(tilenumber,overlapDict[item][2])] = {'d' : 1, 's' :  (start, overlapDict[item][1])}

        if rowcount%50 == 0:
            logger.info("loadSparse : rowcount, adjacency matrix size : %s , %s"%(rowcount,len(a)))


    return (a,overlapDict)



def loadProjectedSparse(infile,startrow,endrow,projectionPath,startOverlaps={},  projectionType = "STAGGERED1"):
    """ see loadSparse - this does exactly the same type of setup , apart from
    the distance measure assigned.

    Here , the distance is based on a projection of the pair of tiles onto
    the projectionPath.

    The default projection, "STAGGERED" , results in a distance measure that will
    give a path that is staggered relative to the given path.

    The projection path is an array of tuples like this :

['CH243-432F19', '1515744', '1661945', '2']
['CH243-78C21', '1644813', '1870023', '9']
['CH243-262D21', '1842421', '2107267', '14']
['CH243-141C23', '2011852', '2274015', '25']

   - sorted by start point

   The staggered projection calculates a distance between two
   overlapping tiles, such that when the overlap is equidistant from
   two overlaps in the projection path , it is a minimum, while if it
   coincides with an overlap in the projection path, then it is a maximum.

   The formula used to do this is currently :

   d =            abs((ol - olp0)**2 - (ol-olp1)**2)
         sqrt    ----------------------------------
                         (olp1-olp0)**2

   d = d**K

    Where

    olp0 = next lower bracketing overlap in the projection path
    olp1= next higher bracketing overlap in the projection path
    ol = the overlap to which we are assigning a distance

    The above will evaluate to 0 when ol is equidistant from olp0 and olp1, and
    to 1 when it coincides with olp0 or olp1

    K is a parameter used to control the compromise between path length , and
    how staggered it is. Higher values of K will result in longer paths, but
    with better "staggered coverage"

    """
    
    
    a = graphsparse()
    reader = csv.reader(open(infile,"r"))
    overlapDict = startOverlaps
    projectionTileNumbers = [int(item[3]) for item in projectionPath]

    rowcount = 0
    for row in reader:
        rowcount += 1

        if rowcount > endrow:
            break

        if rowcount < startrow:
            continue

        
        #print row

        (tile,start,stop,tilenumber) = (row[0],int(row[1]),int(row[2]),int(row[3]))

        if tilenumber in projectionTileNumbers:
            continue
 
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


            # if the start of the new element is >= the existing element start and the end is <= the
            # existing stop - i.e. the new is contained in existing - then set up both existing->new and new->existing
            if start >= overlapDict[item][0] and stop <= overlapDict[item][1]:
                if projectionType == 'STAGGERED1':
                    a[(overlapDict[item][2],tilenumber)] = {
                        'd' : projectOverlap(ol=(overlapDict[item][0],overlapDict[item][1],start,stop),path=projectionPath),
                        's' : (overlapDict[item][0],stop )
                    }
                    a[(tilenumber,overlapDict[item][2])] = {
                        'd' : projectOverlap(ol=(start,stop,overlapDict[item][0],overlapDict[item][1]),path=projectionPath),
                        's' : (start, overlapDict[item][1])
                    }                  
            # else if the start of the new element is >= the existing element start, and <= existing stop , set up existing -> new,
            # and also new -> existing if new start = existing start
            elif start >= overlapDict[item][0] and start <= overlapDict[item][1]:
                if projectionType == 'STAGGERED1':
                    a[(overlapDict[item][2],tilenumber)] = {
                        'd' : projectOverlap(ol=(overlapDict[item][0],overlapDict[item][1],start,stop),path=projectionPath),
                        's' : (overlapDict[item][0],stop )
                    }
                # if the start of the new element == the start of the existing element , set up new - > existing
                if start == overlapDict[item][0]:
                    if projectionType == 'STAGGERED1':
                        a[(tilenumber,overlapDict[item][2])] = {
                            'd' : projectOverlap(ol=(start,stop,overlapDict[item][0],overlapDict[item][1]),path=projectionPath),
                            's' :  (start, overlapDict[item][1])
                        }                  
    
        
        if rowcount%50 == 0:
            logger.info("loadSparse : rowcount, adjacency matrix size : %s , %s"%(rowcount,len(a)))


    return (a,overlapDict)

def projectOverlap(ol,path,projectionType='STAGGERED',scalefactor=10000):
    """ this implements projections as required by loadProjectedSparse.
   The staggered projection calculates a distance between two
   overlapping tiles, such that when the overlap is equidistant from
   two overlaps in the projection path , it is a minimum, while if it
   coincides with an overlap in the projection path, then it is a maximum.

   The formula used to do this is currently :

   d =            abs((ol - olp0)**2 - (ol-olp1)**2)
         sqrt    ----------------------------------
                         (olp1-olp0)**2

   d = d**K

    Where

    olp0 = next lower bracketing overlap in the projection path
    olp1= next higher bracketing overlap in the projection path
    ol = the overlap to which we are assigning a distance

    The above will evaluate to 0 when ol is equidistant from olp0 and olp1, and
    to 1 when it coincides with olp0 or olp1

    K is a parameter used to control the compromise between path length , and
    how staggered it is. Higher values of K will result in longer paths, but
    with better "staggered coverage"
    

    """
    K=2.875 # this value seems to be OK
    #K=2.95 - this value or larger tends to make redundant paths
    #print "projecting %s on %s"%(ol,path)
    d = 1.0
    if projectionType == "STAGGERED":
        myol = (float(ol[0]),float(ol[1]),float(ol[2]),float(ol[3]))
        olcenter = (myol[1] + myol[2])/2.0



        lplcenter = None
        uplcenter = None
        tile0 = None
        tile1 = None
        tile2 = None
        """
        --------        ------------
            ---------------                               <----- bracketing overlaps in projection path
              ^          ^   = (lplcenter, uplcenter)        

        tile0   tile1     tile2


              --------
                  --------                                <----- overlap , for which we want to calculated
                    ^ = olcenter                                  a "distance" between the two tiles, by projecting
                                                                  onto the projection path in some way (in this case
                                                                  in a way such that the "projected distance" between the
                                                                  two tiles is less if the overlap is offset relative to
                                                                  overlaps in the main path
        """                                                     
        for tile in path:
            tile0 = tile1
            tile1 = tile2
            tile2 = (float(tile[1]),float(tile[2]))
            if tile0 != None and tile1 != None and tile2 != None:
                lplcenter = (float(tile0[1]) + float(tile1[0]))/2.0
                uplcenter = (float(tile1[1]) + float(tile2[0]))/2.0

                #print "ol=%s   tile0=%s   tile1=%s   tile2=%s\n"%(ol,tile0,tile1,tile2)

                #print "*****testing %s < %s < %s"%(lplcenter , olcenter ,uplcenter)

                if lplcenter < olcenter < uplcenter:
                    d = math.sqrt(abs((olcenter - lplcenter)**2.0 - (olcenter - uplcenter) **2.0) / (uplcenter - lplcenter)**2.0)
                    break;
                elif lplcenter > olcenter:
                    break

        d = d**K

        #print "d=%s"%d
        # we return integer distance otherwise trace-back may fail due to imprecision - also
        # distance must be at least 1

        d = max(1,int(d * scalefactor))
        
        return d
        #return d 
        



def loadMetaSparse(danglingpaths,danglingoverlaps):
    """
    this method loads a sparse adjacency matrix with paths and overlaps
    from a sub-tiling done by sub_tile.Example value danglingPaths :
    [[((38, 40), {'s': (2856817, 3114972), 'd': 0.030580209171824305}), ((36, 38), {'s': (2720297, 3049679), 'd': 0.48959272247274066}), ((36, 39), {'s': (2720297, 3042618), 'd': 0.48539542326312141}), ((36, 40), {'s': (2720297, 3114972), 'd': 0.47089802814880111}), ((39, 38), {'s': (2869965, 3049679), 'd': 0.0041972992096192731}), ((38, 39), {'s': (2856817, 3042618), 'd': 0.027023686714959208}), ((39, 40), {'s': (2869965, 3114972), 'd': 0.019619904803113077})]]
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
                #if overlapdict[item][1] < start:
                #    del overlapdict[item]
                #    continue                

                # if the start of the new element is >= the existing element start and the end is <= the
                # existing stop - i.e. the new is contained in existing - then set up both existing->new and new->existing
                if start >= overlapdict[item][0] and stop <= overlapdict[item][1]:
                    # existing -> new
                    a[(overlapdict[item][2],tilenumber)] = {'d' : 1, 's' : (overlapdict[item][0],stop )}
                    # new -> existing
                    a[(tilenumber,overlapdict[item][2])] = {'d' : 1, 's' : (start, overlapdict[item][1])}                    
        

                
                # if the start of the new element is >= the existing element start, and <= existing stop , set up existing -> new
                if start >= overlapdict[item][0] and start <= overlapdict[item][1]:
                    a[(overlapdict[item][2],tilenumber)] = {'d' : 1,  's' : (overlapdict[item][0],stop )}
                # if the start of the new element == the start of the existing element , set up new - > existing,
                if start == overlapdict[item][0]:
                    a[(tilenumber,overlapdict[item][2])] = {'d' : 1, 's' :  (start, overlapdict[item][1])}
                        

    #logger.info("Metasparse matrix : "
    #matlog(a)
    return a
               
                         
        

def tilegraphdot(a,b,producttype = 'STANDARD SCALAR'):
    """
    defines the product of two matrices each of which is an adjacency
    matrix of tiles, where adjacency means the tiles overlap.

    In a simple adjacency matrix for a directed graph, each element (i,j) is either 1 or 0 ,
    depending on whether there is a directed edge linking element i to element j

    Rather than store 1 or 0 , you may store a probability for a link.

    More generally , a link my have other attributes such as length, as well as a probability
    weighting.

    In the tile adjacency matrix , each element is a dictionary which stores
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
                    span=None
        	    for k in range(n):
                        elementa = a.get((i,k),None)
                        elementb = b.get((k,j),None)
                        if elementa != None and elementb != None:
                            if span == None:
                                span=(elementa['s'][0],elementb['s'][1])
                            if sum != None:
                                #if i == 145 and j == 209 and sum > (elementa['d'] + elementb['d']):
                                #    print "*** improved using 145 -> %s -> 209 : %s****"%(k,elementa['d'] + elementb['d'])                                
                                sum = min ( sum , (elementa['d'] + elementb['d']))
                            else:
                                sum = elementa['d'] + elementb['d']
                                #if i == 145 and j == 209:
                                #    print "*** found 145 -> %s -> 209 : %s****"%(k,sum)
                    if sum != None:
                        existingelement = a.get((i,j),None)
                        if existingelement != None:
                            #if i == 145 and j == 209 and sum < existingelement['d']:
                            #    print "*** (145,209) : replaced %s with %s ****"%(existingelement['d'],sum)    
                            new[(i,j)] = {'d' : min(sum,existingelement['d']) , 's' : span}
                        else:
                            new[(i,j)] = {'d' : sum, 's' : span}
                    else:
                        existingelement = a.get((i,j),None)
                        if existingelement != None:
                            new[(i,j)] = {'d' : existingelement['d'] , 's' : existingelement['s']}

                        
                            
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
    the length to the final element, contradicting the assumption that the matrix has converged to
    a set of minimal lengths)
    
    We then repeat the process for p(i,k).

    This will lead to tracing back a series of elements of matrix a, to recover the minimum path.
    """

    if i == j:
        return None


    #logger.info("starting traceback")
            
    #logger.info("seeking trace step from %d to %d"%(i,j))
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
            if len(testback) ==2:
                if testback[0]['d'] == testback[1]['d']:
                    tracestep = i

                """
                  File "C:\Python23\Lib\site-packages\sheepgenomics\tiler.py", line 677, in tracebackstep
    if testback[0]['d'] == testback[1]['d']:
IndexError: list index out of range"""
            
        
    #logger.info("finished traceback")
    
    return tracestep


def traceback(p,a,i,j,producttype = 'MINIMUM DISTANCE'):
    #logger.info("tracing back %s to %s"%(i,j))
    tracebackpath = [j]

    nextstep = tracebackstep(p,a,i,j,producttype)

    while nextstep != None:
        tracebackpath.append(nextstep)
        nextstep = tracebackstep(p,a,i,nextstep,producttype)

    return tracebackpath
                    
                    
        

def sub_tile(pairfilename=None, startrow=None, endrow=None, a=None, subStartOverlaps={}, projectedpathfile = None):
    """ this method constucts a tiling path that may be a sub-problem of
     a larger tiling problem - e.g. for a large dataset , chunks of 200 or so records will
     be loaded, each chunk will be sub-tiled, and then join information will be used to
     do a meta-tile of the results of the sub-tiling of the chunks.
     If a is passed in , then this is used as the adjacency
     matrix, otherwise the adjacency matrix is loaded from source data
     It loads at most maxrec records from the sorted
     adjacency file , solves the subtiling problem, then
     returns a data structure containig both completed and "dangling" paths,
     any dangling overlaps , completed tracebacks. The "dangling" info will be
     saved by the calling routine and used at the end in the meta-tiling process.
     """
    logger.info("\n\nstarting sub_tile")
    dictlog(subStartOverlaps,"initial overlaps (subStartOverlaps)")

    if projectedpathfile == None:
        if a == None:
            (a,danglingOverlaps) = loadSparse(pairfilename,startrow,endrow, startOverlaps=subStartOverlaps.copy())
        else:
            danglingOverlaps = {}
    else:
        if a == None:
            projectionPath = getProjectionPath(projectedpathfile)
            (a,danglingOverlaps) = loadProjectedSparse(pairfilename,startrow,endrow,projectionPath,startOverlaps={},  projectionType = "STAGGERED1")
            #a.out()
        else:
            danglingOverlaps = {}
    #matlog(a)
        



    #logger.info("startOverlaps : %s"%str(startOverlaps))
    dictlog(danglingOverlaps,"terminal dangling  overlaps (danglingOverlaps) : ")

    
    #a.out()
    #basictestmain2()
    b = tilegraphdot(a,a,'MINIMUM DISTANCE')
    #b.out()
    #lastkeys = b.keys()
    lastb = b
    logger.info("calculating paths...")
    iterationcount = 0
    while True:
        iterationcount += 1
        logger.info("Step %s"%iterationcount)
        b = tilegraphdot(b,a,'MINIMUM DISTANCE')
        #b.out()
        logger.info("Matrix size : %s"%len(b))

        if b == lastb:
            logger.info("converged")
            break
        else:
            lastb=b
        
        #newkeys = b.keys()
        #if newkeys == lastkeys:
        #    logger.info("converged")
        #    break
        #else:
        #    lastkeys=newkeys

    #b.out()
    matlog(b,"Converged matrix")
 

    # find the distinct completed and dangling paths 
    paths=[item for item in b.keys() if item[0] != item[1]]
    #logger.info("all paths : %s"%str(paths))


    # dangling paths, are those that have an end tile that is in the dangling overlap set, or a start tile that
    # is in the startOverlaps. Note that there is some redundancy in the dangling paths - e.g. we may have
    # 35->46 , 46->50 and 35->50 as dangling paths, but we can't removethe first two , because it may be that
    # we need 46 to join up to a dangling path in the next chunk.
    logger.info("getting dangling paths")
    danglingpaths1 = [item for item in paths if item[1] in [ditem[2] for ditem in danglingOverlaps.values()]]
    #logger.info("dangling paths (1): %s"%str(danglingpaths1))
    danglingpaths2 = [item for item in paths if item[0] in [ditem[2] for ditem in subStartOverlaps.values()]]
    arraylog(danglingpaths2,"DEBUG : dangling paths2")    
    danglingpaths = danglingpaths1 + danglingpaths2

    #
    danglingdict=zip(danglingpaths,[b[path] for path in danglingpaths])

    

    # complete paths are those that have an end tile that is not a start tile of a forward path to
    # another tile with a more positive upper bound ; and with a start tile that is not the end tile of
    # a path to a tile with a less positive lower bound. Then we need to remove apparently completed
    # paths , that have a tile in the dangling set
    logger.info("getting completed paths (1) ")
    logger.info("sorting paths by upper bound")
    paths.sort(lambda x,y:b[x]['s'][1]-b[y]['s'][1])

    
    completedpaths = {}

    for path in paths:
        # loop through each path. Each path is first checked to see if it annihilates any
        # existing completed path, then is added as a candidate completed path. The paths are sorted
        # so that a given path in the list can annihilate a previous path in the list - since it will have
        # the same or greater end point, but not a future path in the list.
        for completedpath in completedpaths.keys():
            # if the start tile of the candidate path is the same as the end tile of
            # the "completed" path, and the upper bound of the candidate path is greater than
            # the upper bound of the "completed" path, then the "completed path" is not complete and
            # is removed.
            if path[0] == completedpath[1]:
                if b[path]['s'][1] > b[completedpath]['s'][1]:
                    del completedpaths[completedpath]

        # add path to "completed paths" (it will probably be removed later !)
        completedpaths[path] = None                        


        
    
    #completedpaths = [item for item in paths if item[1] not in [ditem[0] for ditem in paths]]
    #logger.info("completed paths (1): %s"%str(completedpaths.keys()))
    #logger.info("sorting paths by lower bound")
    #paths.sort(lambda x,y:b[y]['s'][0]-b[x]['s'][0])
    for path in paths:
        # loop through each path. Each path is checked to see if it annihilates any
        # completed path. We do not need to sort this time as we are not adding paths to the
        # candidate list, only annihilating
        for completedpath in completedpaths.keys():
            # if the end tile of the candidate path is the same as the start tile of
            # the "completed" path, and the lower bound of the candidate path is less than
            # the lower bound of the "completed" path, then the "completed path" is not complete and
            # is removed.
            if path[1] == completedpath[0]:
                if b[path]['s'][0] < b[completedpath]['s'][0]:
                    del completedpaths[completedpath]

    #logger.info("completed paths (2): %s"%str(completedpaths.keys()))  


    # the above allows redundant complete paths, that end on two different tiles with the same
    # upper bound, and two different tiles with the same lower bound
    logger.info("Checking for redundant paths...") 
    nrcompletedpaths = {}
    for path1 in completedpaths.keys():
        foundCopy = False
        # loop through each path and see if it 
        for path2 in nrcompletedpaths.keys():
            if b[path1]['s'][1] == b[path2]['s'][1] and b[path1]['s'][0] == b[path2]['s'][0]:
                foundCopy = True
                #logger.info("found identical paths %s and %s"%(str(path1),str(path2)))
                break
                           
        if not foundCopy:
            nrcompletedpaths[path1] = None

    completedpaths = nrcompletedpaths
            
    
    #logger.info("completed paths (3): %s"%str(completedpaths.keys()))
    # remove completed paths that are dangling paths
    completedpaths = [item for item in completedpaths if item not in danglingpaths] # note that this makes completedpaths back into an array
    #logger.info("completed paths (4): %s"%str(completedpaths))    

    # when processing a subtile, completed paths in the above sense are also maximal paths. When processing
    # a metatile, completed paths in the above sense are not also maximal paths, as the connecting
    # edges are not present.
    # For each path , remove it if it is contained in a larger path, to obtain maximal completed paths


    maximalpaths={}

    # sort completedpaths so annhialation works - we sort them by the length from start to end ascending ,
    # so that a given path may annihilate previous paths but not future ones
    completedpaths.sort(lambda x,y:(b[x]['s'][1] - b[x]['s'][0]) - (b[y]['s'][1] - b[y]['s'][0]))
    for path in completedpaths:
        # loop through each path. Each path is first checked to see if it annihilates - i.e. contains - any
        # existing maximal path, then is added as a candidate maximal path
        for maximalpath in maximalpaths.keys():
            # if the start tile of the candidate path is the same as the end tile of
            # the "completed" path, and the upper bound of the candidate path is greater than
            # the upper bound of the "completed" path, then the "completed path" is not complete and
            # is removed.
            #print "comparing %s with %s "%(str(b[path]['s']) , str(b[maximalpath]['s']))
            if b[path]['s'][0] <= b[maximalpath]['s'][0] and b[path]['s'][1] >= b[maximalpath]['s'][1] and \
                path != maximalpath:
                #print ("deleting %s"%str(b[maximalpath]['s']) )
                del maximalpaths[maximalpath]

        # add path to "completed paths" (it will probably be removed later !)
        maximalpaths[path] = None

    completedpaths = maximalpaths.keys()
    completedpaths.sort(lambda x,y:x[0]-y[0])        

            
    
    #logger.info("completed paths : %s"%str(completedpaths))


    logger.info("""
    tracing back completed paths...
    -------------------------------
    """)
    completedTracebacks = []
    for path in completedpaths:
        #logger.info("tracing path %s"%str(path))
        tilingpath=traceback(b,a,path[0],path[1])
        #logger.info("tiling path index : %s"%str(tilingpath))
        completedTracebacks.append(tilingpath)


    logger.info("""
    tracing back dangling paths...
    ------------------------------
    """)
    danglingTracebacks = []
    for path in danglingpaths:
        #logger.info("tracing path %s"%str(path))
        tilingpath=traceback(b,a,path[0],path[1])
        #logger.info("tiling path index : %s"%str(tilingpath))
        danglingTracebacks.append(tilingpath)

    logger.info("\n\ndone sub_tile")        

    return (endrow,completedpaths,danglingdict,completedTracebacks,danglingTracebacks,danglingOverlaps)




def tilemain(infilename,pairfilename,outfile,redopairfile=True,projectedtiling=False, projectedpathfile=None,gffReference=None,gffFeature=None,featureColour="blue"):
    #infile="C:/working/sheepgenomics/bactiling/oar26bes.dat"
    """ this method calls the sub_tile method to solve a series of sub-tiling problems, then
    uses the results of these together with join information to do a final meta-tiling to
    complete the solution of the main tiling problem
    """

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


    # do all the sub_tilings
    #filesize = 1531
    #chunksize = 250
    #chunksize = 100
    chunksize = 400    
    subdanglingOverlaps = {}
    for chunknumber in range(0,4):
        (cumulativeCount,subcompletedpaths,subdanglingpaths,subcompletedTracebacks,subdanglingTracebacks,subdanglingOverlaps) = \
                            sub_tile(pairfilename,chunksize*chunknumber,chunksize*(1+chunknumber),subStartOverlaps=subdanglingOverlaps.copy(),projectedpathfile = projectedpathfile)
        #(cumulativeCount,subcompletedpaths,subdanglingpaths,subcompletedTracebacks,subdanglingTracebacks,subdanglingOverlaps) = \
        #                    sub_tile(pairfilename,150,250,subStartOverlaps=subdanglingOverlaps.copy(),projectedpathfile = projectedpathfile)    
        
        completedpaths.append(subcompletedpaths)
        danglingpaths.append(subdanglingpaths)
        completedtracebacks.append(subcompletedTracebacks)
        danglingtracebacks.append(subdanglingTracebacks)
        danglingoverlaps.append(subdanglingOverlaps.copy())        


    arraylog(completedpaths,"Completed sub-Paths (completedpaths)")
    arraylog(danglingpaths,"Dangling sub-Paths (danglingpaths)")
    arraylog(completedtracebacks,"Completed sub-Tracebacks (completedtracebacks)")
    arraylog(danglingtracebacks,"Dangling sub-Tracebacks (danglingtracebacks)")
    arrayofdictlog(danglingoverlaps,"Dangling sub-Overlaps (danglingoverlaps)")


    # we now need to find a meta-tiling path through the dangling paths
    logger.info("""
    Starting metatile
    -----------------
    """)    
    logger.info("\n\nSetting up metapairfile")
    a=loadMetaSparse(danglingpaths,danglingoverlaps)
    matlog(a,"Meta-sparse matrix after loadMetaSparse")
    (junk,metacompletedpaths,metadanglingpaths,metacompletedtracebacks,metadanglingtracebacks,metadanglingoverlaps)=sub_tile(a=a)


    arraylog(metacompletedpaths,"Meta Completed sub-Paths (metacompletedpaths)")
    arraylog(metadanglingpaths,"Meta Dangling sub-Paths (metadanglingpaths)")
    arraylog(metacompletedtracebacks,"Meta Completed sub-Tracebacks (metacompletedtracebacks)")
    arraylog(metadanglingtracebacks,"Meta Dangling sub-Tracebacks (metadanglingtracebacks)")
    arrayofdictlog(metadanglingoverlaps,"Meta Dangling sub-Overlaps (metadanglingoverlaps)")
    
    #logger.info("Completed meta-Paths : %s"%str(metacompletedpaths))
    #logger.info("Dangling meta-Paths : %s"%str(metadanglingpaths))
    #logger.info("Completed meta-Tracebacks : %s"%str(metacompletedtracebacks))
    #logger.info("Dangling meta-Tracebacks : %s"%str(metadanglingtracebacks))
    #logger.info("Dangling meta-Overlaps : %s"%str(metadanglingoverlaps))


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
    arraylog(completedtracebacks,"*** All Completed Tracebacks (completedtracebacks) : ")  
    completedtracebacks.sort(lambda x,y:x[0][0]-y[0][0])


    # write the completed tiling paths to a file
    logger.info("Merging tile definitions and writing tiling paths")
    reader = csv.reader(open(pairfilename,"r"))
    writer=open(outfile,"w")
    writer.write("*** All Completed Tracebacks : %s"%str(completedtracebacks))

    writer.write("\n\n***GFF for paths***\n\n")

    writer.write("reference = %s\n"%gffReference)

    # get just the tile defintions we need
    tilingDict = {}
    for row in reader:
        (tilename,start,stop,tileid) = (row[0],int(row[1]),int(row[2]),int(row[3]))
        for chunk in completedtracebacks:
            for tilingpath in chunk:
                if tileid in tilingpath:
                    tilingDict[tileid] = row
    #logger.info(tilingDict)

    pathcount = 0
    for chunk in completedtracebacks:
        for tilingpath in chunk:
            pathcount += 1
            tilingpath.reverse()
            for tileid in tilingpath:
                writer.write("""
%s        %s_%s %s..%s"""%(gffFeature,tilingDict[tileid][0], tilingDict[tileid][3] , tilingDict[tileid][1], tilingDict[tileid][2]))



    writer.write("""


[%s]
glyph = generic
connector = dashed
bump = 1
color = %s
"""%(gffFeature,featureColour))


    writer.close()

    logger.info("""
=========================================
Completed tile session
=========================================
""")



def makeGFF(infile,outfile,gffReference,gffFeature,featureColour):
    """ covert the original output format , to GFF. Original output format :
    *** All Completed Tracebacks : [[[25, 14, 9, 2], [34, 27, 26]], [[100, 93, 92, 87, 80, 76, 72, 68, 60, 50, 46, 37, 35]], [[125, 122, 118, 113, 104, 101, 100, 93], [140, 136, 132, 131, 127, 126], [143, 141]], [[200, 190, 186, 179, 171, 161, 153, 144]], [[220, 216, 210, 206, 202, 190]], [[650, 642, 635, 632, 628, 618, 607, 603, 600, 583, 568, 560, 550, 546, 525, 521, 517, 502, 498, 490, 483, 477, 466, 461, 452, 442, 437, 434, 427, 414, 403, 400, 385, 371, 365, 362, 359, 354, 350, 341, 327, 310, 292, 283, 270, 263, 257, 249, 240, 237, 234, 226, 221]], [[678, 666, 657, 653, 650, 642]], [[708, 702, 700, 690]], [[750, 745, 741, 738, 728, 722, 717, 712, 710, 709, 706, 700, 690, 687, 684, 679]], [[797, 789, 777, 769, 764, 755, 752, 750, 745]], [[850, 837, 832, 819, 808, 804, 802, 798]], [[863, 857, 850, 837]], [[900, 894, 891, 887, 882, 879, 868, 864]], [[904, 900, 894]], [[1250, 1235], [1266, 1264, 1263, 1261, 1256, 1251]], [[1250, 1235, 1228, 1221, 1216, 1214, 1211, 1208, 1201, 1191, 1186, 1178, 1171, 1165, 1154, 1138, 1128, 1123, 1121, 1118, 1115, 1113, 1107, 1100, 1092, 1088, 1080, 1072, 1064, 1055, 1050, 1035, 1024, 1014, 1008, 1004, 1000, 994, 991, 982, 976, 965, 955, 949, 948, 942, 937, 927, 915, 908, 905]], [[1300, 1296, 1286, 1281, 1272, 1269, 1264, 1263, 1261, 1256, 1251]], [[1319, 1317, 1311, 1301, 1300, 1296], [1340, 1332, 1329, 1328, 1322, 1320]], [[1350, 1345, 1342, 1341]], [[1371, 1365, 1356, 1353, 1350, 1345]], [[1400, 1395, 1393, 1390, 1387, 1385, 1380, 1378, 1373]], [[1441, 1436, 1431, 1428, 1423, 1413, 1409, 1407, 1401, 1400, 1395]], [[1500, 1495, 1492, 1489, 1480, 1476, 1473, 1466, 1463, 1462, 1460, 1454, 1449, 1443]], [[1529, 1523, 1515, 1514, 1512, 1506, 1503, 1502, 1500, 1495]], [[1531, 1530]]]
Tiling path : 1
----------------
['CH243-432F19', '1515744', '1661945', '2']
['CH243-78C21', '1644813', '1870023', '9']
['CH243-262D21', '1842421', '2107267', '14']
['CH243-141C23', '2011852', '2274015', '25']

Tiling path : 2
----------------
['CH243-54B4', '2339622', '2477720', '26']
['CH243-206K6', '2348438', '2510356', '27']
['CH243-345J19', '2488592', '2654689', '34']

Tiling path : 3
----------------
['CH243-241F18', '2720297', '2874966', '35']
['CH243-140E2', '2808427', '3045839', '37']
['CH243-500F7', '3043348', '3243827', '46']
['CH243-325N1', '3184419', '3418496', '50']
['CH243-477N24', '3372071', '3539433', '60']
['CH243-272D1', '3538621', '3670581', '68']
['CH243-320K13', '3608636', '3775020', '72']
"""

    reader = open(infile,"r")
    writer=open(outfile,"w")
    writer.write("reference = %s\n"%gffReference)

    # get just the tile defintions we need
    tilingDict = {}
    for row in reader:
        if re.search('^\[',row) != None:
            mytuple = eval(row)
            writer.write("""
%s        %s_%s %s..%s"""%(gffFeature,mytuple[0], mytuple[3] , mytuple[1], mytuple[2]))



    writer.write("""


[%s]
glyph = generic
connector = dashed
bump = 1
color = %s
"""%(gffFeature,featureColour))


    writer.close()


def matlog(mat,heading=""):
    """ list a sparse tiling matrix tidily to a logger """
    logger.info("=== Begin Listing sparse matrix : %s.... === "%heading)
    hdlr.setFormatter(bareformatter)
    coords=[item for item in mat.keys()]
    coords.sort(lambda x,y:x[0]-y[0])
    logstr = ""
    for i in range(0,len(coords)):
        logstr += "%s : %s ,"%(coords[i],mat[coords[i]])
        if i%3 == 2:
            logger.info(logstr)
            logstr = ""
    hdlr.setFormatter(formatter)
    logger.info("=== End Listing sparse matrix === \n")    


def dictlog(mydict,heading=""):
    """ list a dictionary tidily to a logger """
    logger.info("=== Begin Listing dictionary : %s.... ==="%heading)
    hdlr.setFormatter(bareformatter)    
    for key in mydict.keys():
        logger.info("%s : %s"%(key,str(mydict[key])))
    hdlr.setFormatter(formatter)
    logger.info("=== End Listing dictionary ===")


def arraylog(myarray,heading=""):
    """ list an array tidily to a logger """
    logger.info("=== Begin Listing array : %s.... ==="%heading)
    hdlr.setFormatter(bareformatter)    
    for element in myarray:
        logger.info(str(element))
    hdlr.setFormatter(formatter)
    logger.info("=== End Listing array ===")        


def arrayofdictlog(myarray,heading=""):
    """ list a dictionary tidily to a logger """
    logger.info("=== Begin listing array of dictionaries : %s.... ==="%heading)
    for mydict in myarray:
        dictlog(mydict)
    logger.info("=== End listing array of dictionaries ===")
    
    

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

    

          


if __name__ == "__main__":

    #tilemain("/data/home/seqstore/agbrdf/tiling/oar26bes.dat","/data/home/seqstore/agbrdf/tiling/paired26.txt","/data/home/seqstore/agbrdf/tiling/oar26tilingpaths.txt",False,gffReference="OAR26",gffFeature="tiling-pathA2",featureColour="brown")
    tilemain("/data/home/seqstore/agbrdf/tiling/oar26bes.dat","/data/home/seqstore/agbrdf/tiling/paired26.txt","/data/home/seqstore/agbrdf/tiling/oar26offsettilingpaths.txt",\
             False,projectedtiling=True, projectedpathfile="/data/home/seqstore/agbrdf/tiling/oar26tilingpaths1405chunked.gff",gffReference="OAR26",gffFeature="tiling-pathB",featureColour="lightgreen")


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







############################# older test and utility functions #######################


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
    
    



            

    



    
