#!/bin/sh
#
# this script is a wrapper for an R Affy Probe graph script - it is usually called
# by the brdf database. Minimal arg checking etc - assumes the database knows
# what its doing.
# It will print to standard output either the name of the image  created,
# or the string ERROR plus an error message 
#example  : ./getAffyProbeGraphs.sh ./getAffyProbeGraphs.r ../html/tmp/CS37003138FFFFB_at.txt test.jpg 1200 1200 jpeg /tmp  CS37003138FFFFB_at
#example of calling the R script : 
# Rscript --vanilla getAffyProbeGraphs.r i=CS37003138FFFFB_at.txt o=test.jpg h=1200 w=1200 f=jpeg m=CS37003138FFFFB_at

PROG=$1
DATAFILENAME=$2
IMAGEFILENAME=$3
HEIGHT=$4
WIDTH=$5
IMAGETYPE=$6
TEMPIMAGEFOLDER=$7
PLOTNAME=$8
NDATAFILENAME=$9 #optional normalised data
shift
INCLUDEMM=$9
shift
YSCALE=$9

RSCRIPT="Rscript --vanilla "

# check args
if [ -z "$7" ]; then
   echo "ERROR : useage "
   exit 1
fi

# see if target name already exists and if so , just return it
TARGET=$TEMPIMAGEFOLDER/$IMAGEFILENAME
#echo "checking $TARGET"
if [ -f $TARGET ]; then
   echo $IMAGEFILENAME
   exit 0
fi

# see if the source file exists 
DATAFILE=$TEMPIMAGEFOLDER/$DATAFILENAME
if [ ! -f $DATAFILE ]; then
   echo "ERROR : $DATAFILE not found"
   exit 1
fi

# if there is a normalised data file , check it
if [ ! -z "$NDATAFILENAME" ]; then
   if [ $NDATAFILENAME != "None" ]; then
      NDATAFILE=$TEMPIMAGEFOLDER/$NDATAFILENAME
      if [ ! -f $NDATAFILE ]; then
         echo "ERROR : $NDATAFILE not found"
         exit 1
      fi
   else
      NDATAFILENAME=""
   fi
fi


export DISPLAY=localhost:999
env > /tmp/debug.tmp

if [ -z "$NDATAFILENAME" ]; then
    echo "executing $RSCRIPT  $PROG i=$DATAFILE o=$TARGET h=$HEIGHT w=$WIDTH f=$IMAGETYPE m=$PLOTNAME yscale=$YSCALE"  >> /tmp/debug.tmp
    $RSCRIPT  $PROG i=$DATAFILE o=$TARGET h=$HEIGHT w=$WIDTH f=$IMAGETYPE m=$PLOTNAME yscale=$YSCALE
else
    echo "executing $RSCRIPT  $PROG i=$DATAFILE o=$TARGET h=$HEIGHT w=$WIDTH f=$IMAGETYPE m=$PLOTNAME n=$NDATAFILE yscale=$YSCALE" >> /tmp/debug.tmp
    $RSCRIPT  $PROG i=$DATAFILE o=$TARGET h=$HEIGHT w=$WIDTH f=$IMAGETYPE m=$PLOTNAME n=$NDATAFILE yscale=$YSCALE
fi


# check target now exists
if [ ! -f $TARGET ]; then
   echo "ERROR  : target does not exist after $RSCRIPT  $PROG i=$DATAFILE o=$TARGET h=$HEIGHT w=$WIDTH f=$IMAGETYPE"
   exit 1
else
   echo $IMAGEFILENAME
   exit 0
fi
