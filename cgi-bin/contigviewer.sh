#!/bin/sh
#
# this script is a wrapper for the perl contigviewer script - it is usually called
# by the brdf database. Minimal arg checking etc - assumes the database knows
# what its doing. 
# It will print to standard output either the name of the image  created,
# or the string ERROR plus an error message 
#
# Eample of calling the perl script : 
# perl Ag_ace_draw.pl -file cluster.1125.seq.cap.ace  -out cluster1125.png -difffile cluster1125diff.png -fontsize 10 -iframe iframe.php -urls urls1.list -contig Contig2 -verbose
#  
SOURCE=$1
OUTPUTNAME1=$2
OUTPUTNAME2=$3
FONTSIZE=$4
IFRAME=$5
URLS=$6
CONTIG=$7


SCRIPT=./Ag_ace_draw.pl
TEMP=/tmp


# check args
if [ -z "$6" ]; then
   echo "ERROR : useage contigviewer.sh sourcefilename imagename imagename2 fontsize iframename urlsname contignumber "
   exit 1
fi

# see if target name already exists and if so , just return it
#echo "checking $TARGET"
if [ -f $OUTPUTNAME1 ]; then
   if [ -f  $OUTPUTNAME2 ]; then
      echo $OUTPUTNAME1 $OUTPUTNAME2
      exit 0
   fi
fi

# see if the source file exists 
if [ ! -f $SOURCE ]; then
   echo "ERROR : $SOURCE not found"
   exit 1
fi


echo "executing $SCRIPT -file $SOURCE  -out $OUTPUTNAME1 -difffile $OUTPUTNAME2 -fontsize $FONTSIZE -iframe $IFRAME -urls $URLS -contig $CONTIG "
$SCRIPT -file $SOURCE  -out $OUTPUTNAME1 -difffile $OUTPUTNAME2 -fontsize $FONTSIZE -iframe $IFRAME -urls $URLS -contig $CONTIG


# check target now exists
if [ ! -f $OUTPUTNAME1 ]; then
   echo "ERROR  : target does not exist after $SCRIPT -file $SOURCE  -out $OUTPUTNAME1 -difffile $OUTPUTNAME2 -fontsize $FONTSIZE -iframe $IFRAME -urls $URLS -contig $CONTIG"
   exit 1
else
   echo $OUTPUTNAME1 $OUTPUTNAME2
   exit 0
fi
