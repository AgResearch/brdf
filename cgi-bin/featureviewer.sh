#!/bin/sh
#
# this script is a wrapper for the perl featureviewer script - it is usually called
# by the brdf database. Minimal arg checking etc - assumes the database knows
# what its doing.
# It will print to standard output either the name of the image  created,
# or the string ERROR plus an error message 
#example  : ./featureviewer.sh  700 my_map.txt my_image.png test0.gff
#example of calling the perl script : ./featureviewer.pl  -w 700 -m my_map.txt -i my_image.png -n my_test_map -f test0.gff
# or ./featureviewer.pl  -w 700 -m my_map.txt -i my_image.png -f test0.gff

# check source gff file exists
WIDTH=$1
MAPFILENAME=$2
IMAGEFILENAME=$3
GFFFILENAME=$4
TEMPIMAGEFOLDER=$5
PROG=$6

# check args
if [ -z "$6" ]; then
   echo "ERROR : useage ./featureviewer.sh  width mapfilename imagefilename gfffilename tempimagefolder prog"
   exit 1
fi

# see if target name already exists and if so , just return it
TARGET=$TEMPIMAGEFOLDER/$IMAGEFILENAME
#echo "checking $TARGET"
if [ -f $TARGET ]; then
   echo $IMAGEFILENAME
   exit 0
fi

MAPTARGET=$TEMPIMAGEFOLDER/$MAPFILENAME
GFFTARGET=$TEMPIMAGEFOLDER/$GFFFILENAME

# see if the source file exists 
if [ ! -f $GFFTARGET ]; then
   echo "ERROR : $GFFTARGET not found"
   exit 1
fi

$PROG -w $WIDTH -m $MAPTARGET -i $TARGET -f $GFFTARGET


# check target now exists
if [ ! -f $TARGET ]; then
   echo "ERROR  : target does not exist after $PROG -w $WIDTH -m $MAPTARGET -i $TARGET -f $GFFFILENAME"
   #exit 1
   exit 0
else
   echo $IMAGEFILENAME
   exit 0
fi
