#!/bin/sh
#
# this script is a wrapper for the perl traceviewer script - it is usually called
# by the brdf database. Minimal arg checking etc - assumes the database knows
# what its doing. Main purpose is to gunzip the trace file into a local folder
# It will print to standard output either the name of the image  created,
# or the string ERROR plus an error message 
#
# Useage : 
# traceviewer.sh sourcefilename tempimagefolder outputname height leftseq rightseq size
# example : traceviewer.sh /data/databases/flatfile/bfiles/pgc/tracefiles/orion/pt1/1188_10_f_48515/traces/1188_10_14726942_16654_48515_016.ab1.gz /var/www/pgc/html/tmp test.png 200 CAATAGTAAGGGTGCTGCC ggtcaactTTGgctgttgtCTTG 678 ./traceviewer.pl
#  
# check source file exists
SOURCE=$1
TEMPIMAGEFOLDER=$2
OUTPUTNAME=$3
HEIGHT=$4
LEFT=$5
RIGHT=$6
SIZE=$7
PROG=$8

GUNZIP="gunzip -f "
TEMP="/tmp"


# check args
if [ -z "$8" ]; then
   echo "ERROR : useage traceviewer.sh sourcefilename height leftseq rightseq size prog"
   exit 1
fi

# see if target name already exists and if so , just return it
TARGET=$TEMPIMAGEFOLDER/$OUTPUTNAME
#echo "checking $TARGET"
if [ -f $TARGET ]; then
   echo $OUTPUTNAME
   exit 0
fi

# see if the source file exists 
if [ ! -f $SOURCE ]; then
   echo "ERROR : $SOURCE not found"
   exit 1
fi

# maybe copy the file to temp and maybe unzip it
BASENAME=`basename $SOURCE .gz`
INFILE=$TEMP/$BASENAME

if [ ! -f $INFILE ]; then
   # try copying it
   cp $SOURCE $TEMP
   # try unzipping it
   $GUNZIP $TEMP/"$BASENAME".gz
fi


# create the image
#cp /data/databases/flatfile/bfiles/pgc/tracefiles/orion/pt1/1188_10_f_48515/traces/1188_10_14726942_16654_48515_016.ab1.gz .

#echo "executing $PROG -f $INFILE  -h $HEIGHT -o $TARGET --left $LEFT  --right $RIGHT -size $SIZE"
$PROG -f $INFILE  -h $HEIGHT -o $TARGET --left $LEFT  --right $RIGHT -size $SIZE 1>/dev/null 2>/dev/null


# check target now exists
if [ ! -f $TARGET ]; then
   echo "ERROR  : target does not exist after $PROG -f $INFILE  -h $HEIGHT -o $TARGET --left $LEFT  --right $RIGHT -size $SIZE"
   exit 1
else
   echo $OUTPUTNAME
   exit 0
fi
