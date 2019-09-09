#!/usr/bin/perl
use GD;
use GD::Polyline;
use Getopt::Long;

GetOptions ('file=s' => \$FILE,
            'out=s' => \$OUTFILE,
            'iframe=s' => \$IFRAMEFILE,
            'urls=s'   => \$URLS,
            'difffile=s' => \$DIFFFILE,
            'verbose' => \$VERBOSE,
            'fontsize=i' => \$FONTSIZE,
            'contig=s' => \$CONTIG,
            );

unless (defined $FILE and defined $OUTFILE and defined $IFRAMEFILE and defined $FONTSIZE and defined $URLS and defined $CONTIG){ die <<USAGE;
Usage: perl $0 -file CLP0001001240-cE15_20030319.ace -out test.png -difffile testdiff.png -fontsize 10 -iframe iframe.php -urls urls.list -contig Contig00028


Options:
-file <ace file-name>         Filename for the .ace file
-out <output file-name>       Filename for the generated .png image
-difffile <diff file-name>    Filename for the generated diff .png image
-iframe <iframe file-name>    Filename for the inline frame file
-urls <url list file-name>    Filename for list of urls for the image map. Should be tab-seperated e.g. seqid	http://www.someurl.com?name=
-verbose 				      Show debugging information
-fontsize                     Font size in points from 5 - 24. 10 works well.
-contig                       Name of the contig to draw from the .ace file

Parse an .ace file and render a PNG image.
USAGE
}

$af = $FILE;
$outfilename = $OUTFILE;
$difffilename = $DIFFFILE;
my$cn = $CONTIG;
my $PROCESS_DATA = -1;
# read the url list into a hash
my%urlhash = ();
open(URLS,$URLS) or die $!;
while(<URLS>){
	chomp;
	my($n,$u) = split("\t",$_);
	$u =~ s/\n//;
	$urlhash{$n} = $u;
}
close URLS;

# need to set this to a true-type font on the relevant server!!!
# I'm just borrowing the ones Python uses.
$FONT = "/usr/lib64/python2.4/site-packages/matplotlib/mpl-data/fonts/ttf/VeraMono.ttf";
$FW =  $FONTSIZE * .8;
$FH = $FONTSIZE * 1.2 ;

$base_gap = $FW + 1;   # width allowed for each char

$longest_contig_name = -1;

my@COARRAY = ();
my@BQARRAY = ();
my@RDARRAY = ();
my@RDID = ();
my%SENSE = ();
my%OFFSET = ();

&do_ace($af,$cn);

# Global variables used
#
#		COARRAY BQARRAY are same length, almost same index
#		There is no BQ entry if the CO entry is "*", meaning gap
#     @COARRAY			contains consensus sequence 1 char per index
#     @BQARRAY			contains quality array 1 number per index.
#
#		RDID RDARRAY same length, indexed by read number
#     @RDID			names of the reads
#     @RDARRAY			array of array references, each element of
#				RDARRAY points to an array which contains 
#				the read sequence 1 char per index
#
#		SENSE and OFFSET hash tables indexed by rdid (read name)
#     %SENSE			sense of each read
#     %OFFSET			offset of read wrt consensus, may be negative

#
# do_ace gathers all the contig info into the arrays and hashes
# described above.
#
sub do_ace {
    my $af = shift;
    my $contig_name = shift;
    open(ACE, "<$af") or die "couldn't open ace file: $!\n";

    $/ = "";				# break on blank lines, not newlines
    while (<ACE>) {
	chomp;
		if (/^CO\s+(\w+)\s+(\d+)\s+(\d+)/) {
print "debug1\n";
		    &ace_array if $PROCESS_DATA == 1;			# process previous contig if it's the required $CONTIG e.g Contig00028
		    my $coline = $_;
		    $coid = $1;			# contig ID
		    if($coid =~ /($contig_name)/){
				$PROCESS_DATA = 1;
				# reinitialize all arrays and hashes to null
				@COARRAY = ();
				@BQARRAY = ();
				@RDARRAY = ();
				@RDID = ();
				%SENSE = ();
				%OFFSET = ();
				$minbase =  100000;
    			$maxbase = -100000;
			}
		    next unless $coid =~ /($contig_name)/;
		    print "saw $coid\t$PROCESS_DATA\n";
		    my $colen = $2;		# length of consensus seq
		    my $coreadn = $3;		# number of reads in contig
		    $coline =~ s/^CO.*\n?//;	# remove the first line (^CO)
		    $coline =~ s/\s+//go;		# remove whitespace
		    @COARRAY = split (//, $coline);
		}
		if (/^BQ/) {			# base quality info
		    my $bqline = $_;		# save line for editing
		    $bqline =~ s/^BQ.*\n?//;	# remove the first line (^BQ)
		    $bqline =~ s/^\s+//;	# remove leading whitespace
		    @BQARRAY = split (/\s+/, $bqline);
		} 
		if (/^RD\s+(\S+)\s+(\d+)\s+(\d+)\s+(\d+)/) {
		    my $rdid = $1;
		    my $rdlen = $2;
		    push (@RDID, $rdid);
	
		    my $end = $OFFSET{$rdid} + $rdlen;
		    if ($end > $maxbase) {$maxbase = $end;}
	
		    my $rdline = $_;
		    $rdline =~ s/^RD.*\n?//;		# remove the first line (^RD)
		    $rdline =~ s/\s+//go;		# remove whitespace
		    my @rdarray = split (//, $rdline);
		    push(@RDARRAY, [@rdarray]);		# array of arrays
		}
		if (/^AF/) {
		    my @afarray = split "\n";		# may be many lines of AF
		    my $afele;
		    foreach $afele (@afarray) {
				my ($afmarker, $afid, $afsense, $afoffset);
				($afmarker, $afid, $afsense, $afoffset) = split ' ', $afele;
				last if ($afmarker ne "AF");
				# save sense and offset according to afid (read name)
				$SENSE{$afid} = $afsense;
				$OFFSET{$afid} =  $afoffset;
				$IMG_OFFSET{$afid} =  ($afoffset * $base_gap) - $base_gap + 1;
				if($afoffset < $minbase) { $minbase = $afoffset; }
		    }
		}
	# all other lines are ignored
    }

    close(ACE);

    &ace_array if $PROCESS_DATA == 1;				# process last contig
}

sub ace_array {
	print "doing ace_array\n";
	if (not defined($coid)) {return;}		# first time, nothing to do

	    print "#### BEGIN ace_array ####\n"if ($VERBOSE);
	    print "CO info: $coid $colen $coreadn \n"if ($VERBOSE);
	    print "COARRAY size = $#COARRAY\n"if ($VERBOSE);		#, COARRAY = @COARRAY\n\n";
	    print "BQARRAY size = $#BQARRAY\n"if ($VERBOSE);		#, BQARRAY = @BQARRAY\n\n";
	    print "RDID size = $#RDID, RDID = @RDID\n\n"if ($VERBOSE);
	    print "RDARRAY size = $#RDARRAY\n"if ($VERBOSE);		#, RDARRAY = @RDARRAY\n\n";
	    foreach $rdarray (@RDARRAY) {
			print "rdarray = @$rdarray\n\n"if ($VERBOSE);
	    }
	    for ($i = 0; $i <= $#RDARRAY; $i++) {
			$rar  = $RDARRAY[$i];
			@rdarray = @$rar;
			# for now generate gel on left
			for ($j = 0; $j <= $#rdarray; $j++) {
			    $l = $rdarray[$j];
			    print "$l "if ($VERBOSE);
			}
			print "\n\n"if ($VERBOSE);
	    }

	    @sensearray = sort keys %SENSE;
	    foreach $sense (@sensearray) {
			print "sense{$sense} = $SENSE{$sense}\n"if ($VERBOSE);
			$longest_contig_name = length($sense) if (length($sense) > $longest_contig_name);
	    }
	    @offsetarray = sort keys %OFFSET;
	    foreach $offset (@offsetarray) {
			print "offset{$offset} = $OFFSET{$offset}\n"if ($VERBOSE);
	    }

		# calculate left padding based on longest contig name length

		my$pad_left = ($FW * $longest_contig_name+4) + 20;
	    print "minbase, maxbase, longest_contig_name, pad_left = $minbase, $maxbase, $longest_contig_name, $pad_left\n"if ($VERBOSE);

	    print "#### END ace_array ####\n"if ($VERBOSE);

	    

	&gd_contig($outfilename,-1, $pad_left);			# create the contig image
	&gd_contig($difffilename,1, $pad_left);			# create the contig diff image

	print "exiting\n";
	exit;
}

#
# gd_contig creates a new contig image
#
sub gd_contig{
	my$outfilename = shift;
	my$do_diff = shift;
	my$pl = shift;
	print "printing $outfilename, pl= $pl\n";
    # These are needed now to figure the height of the image
    $scaleh = $FH * 5;#30;					# scale height
    $consensush = $FH * 5;#30;					# consensus height
    $traceh = $FH * 5;#30;                         # quality trace height
    $csh = $scaleh + $consensush + $traceh;			# bottom of consensus

    $width  = ($maxbase - $minbase) * $base_gap;		# minbase can be negative
    $height = $csh + $FH * ($#RDID + 1) + 4;	# scale + consensus + each read
    my $im = new GD::Image($width + $pl + 20, $height);

	# first color allocated will be background
	$white = $im->colorAllocate(255, 255, 255);
	$black = $im->colorAllocate(0, 0, 0);
	$gray = $im->colorAllocate(165, 165, 165);
	$lightgray = $im->colorAllocate(180, 180, 180);

	# same colors as Chromas trace viewer
	$Acolor = $black = $im->colorAllocate(0,0,0);        # A
    $Ccolor = $blue = $im->colorAllocate(0,0,255);       # C
    $Gcolor = $red = $im->colorAllocate(255,0,0);        # G
    $Tcolor = $green = $im->colorAllocate(0,255,0);      # T
    $Ncolor = $magenta = $im->colorAllocate(255,0,255);  # N
	$Ucolor = $Xcolor = $dgray = $im->colorAllocate(127, 127, 127);

    # initialize letter to color lookup hash table
    $colorhash{"A"} = $Acolor;
    $colorhash{"a"} = $Acolor;
    $colorhash{"C"} = $Ccolor;
    $colorhash{"c"} = $Ccolor;
    $colorhash{"G"} = $Gcolor;
    $colorhash{"g"} = $Gcolor;
    $colorhash{"T"} = $Tcolor;
    $colorhash{"t"} = $Tcolor;
    $colorhash{"N"} = $Ncolor;
    $colorhash{"n"} = $Ncolor;
    $colorhash{"X"} = $Xcolor;
    $colorhash{"x"} = $Xcolor;
    $colorhash{"*"} = $Ucolor;

    gd_quality($im,$pl);		# draw quality trace
    gd_consensus($im,$pl);		# draw scale and consensus
    gd_reads($im,$do_diff,$pl);			# draw all reads

    open(PNG, ">$outfilename") || die "open $outfilename $!\n";
    # make sure we are writing to a binary stream
    binmode PNG;
    print PNG $im->png;
    close PNG;
}

#
# draw quality plot
#
sub gd_quality {
    my$im = shift;
    my$pl = shift;
    print "doing quality\n";
    print "pad_left= $pl\n";

    # Add consensus name to upper left corner
#    $im->string($FONT, 6, $scaleh + 44, "QUALITY:", $black);
#    $im->string($FONT, $pad_left - 25, $csh - 5 - 1 - 5, "  0 -", $black);
#    $im->string($FONT, $pad_left - 25, $csh - $consensush - 5, ">30 -", $black);
    $im->stringFT($black,$FONT,$FONTSIZE,0,6, $scaleh + 44, "QUALITY:" );
    $im->stringFT($black,$FONT,$FONTSIZE,0, $pl - 25, $csh - 5 - 1 - 5, "  0-" );
    $im->stringFT($black,$FONT,$FONTSIZE,0, $pl - 25, $csh - $consensush - 5, ">30-");

    # Add consensus image underneath scale
    $q = 0;						# BQ array index
    $polyline = new GD::Polyline;
    for ($i = 0, $m = 0; $i <= $#COARRAY; $i++, $m += $base_gap) {
		$l = $COARRAY[$i];				# get letter			# get color
		# allow 200 pixels for the name field
		$x = $pl + $m - $minbase;
		$y = $csh - 5;
		if ($l eq "*") {				# gap has no BQ
		    $bq = 0;
		} else {
		    $bq = $BQARRAY[$q];				# get the bq value
		}
		# calculate the height of the bar based on the quality in BQARRAY
		# minimum height is 5, maximum 30
		if ($bq < 5) {$y = $csh - 5 - 1;}
		if ($bq > 30) {$y = $csh - $consensush;}
		if (($bq >= 5) && ($bq <= 30) ) {
		    $y = $csh - $bq;
		}
		#print "i = $i, q = $q, CO = $COARRAY[$i], BQ = $bq, y = $y\n";
		$polyline->addPt($x,$y);
		$q++ unless ($l eq "*");
    }
    $im->polyline($polyline,$black);
}



#
# creates consensus and scale at top of image
#
sub gd_consensus {
    $im = shift;
    my$pl = shift;
    print "doing consensus, pl = $pl\n";
    # Add scale to top of image and vertical bars every 10 bp
    for ($i = 0; $i < $maxbase * $base_gap; $i+=(10 * $base_gap)) {
	$x = $pl - $minbase + $i - 2;			# why 2?
#	$im->stringUp($FONT, $x + 3, $scaleh - 5, $i/$base_gap, $black);
	$im->stringFT($black,$FONT,$FONTSIZE,120, $x, $scaleh - 5, sprintf("%d",$i/$base_gap) );
	$im->line($x + 2, $scaleh - 9, $x + 2, $height, $gray);
    }
    $im->line($pl - $minbase, $scaleh - 2, $pl + ($maxbase *$base_gap) , $scaleh - 2, $red);

    # Add consensus name to upper left corner
    $im->stringFT($black,$FONT,$FONTSIZE,0, 6, $scaleh + 0, $coid );
    $im->stringFT($black,$FONT,$FONTSIZE,0, 6, $scaleh + 14, "CONSENSUS:");

    # Add consensus image underneath scale
    $q = 0;						# BQ array index
    for ($i = 0, $m = 0; $i <= $#COARRAY; $i++, $m += $base_gap) {
		$l = $COARRAY[$i];				# get letter
		$colorindex = $colorhash{$l};			# get color
		$x = $pl + $m - $minbase;
		$y = $csh - 5;
		if ($l eq "*") {				# gap has no BQ
		    $bq = 0;
		} else {
		    $bq = $BQARRAY[$q];				# get the bq value
		}
		# calculate the height of the bar based on the quality in BQARRAY
		# minimum height is 5, maximum 30
		if ($bq < 5) {$y = $csh - 5;}
		if ($bq > 30) {$y = $csh - $consensush;}
		if (($bq >= 5) && ($bq <= 30) ) {
		    $y = $csh - $bq;
		}
		#print "i = $i, q = $q, CO = $COARRAY[$i], BQ = $bq, y = $y\n";
		$im->stringFT($colorindex,$FONT,$FONTSIZE,0,$x, $scaleh + 14,$l );	# paint base char
		$q++ unless ($l eq "*");
    }
}

#
# Go through RDARRAY arrays to generate the read images
#
sub gd_reads {
    my $im = shift;
    my $do_diff = shift;
    my $pl = shift;
	print "doing reads, pl = $pl\n";
    my ($i, $j);
    my@mapdata = ();
	push(@mapdata,'<map id ="mymap" name="mymap">');

    # Add reads to image
    for ($i = 0; $i <= $#RDARRAY; $i++) {
		my ($rar, $rdid, $y, $fg, $offset, @rdarray);
		# put the name on the left, allowing 200 pixels
		$rar  = $RDARRAY[$i];		# this needs two statements
		@rdarray = @$rar;
		$rdid = $RDID[$i];			# name (ID) of THIS read
		$y = $csh +2 + $i * $FH;
		# use dark-gray fg for normal sequences, blue fg for reverse complemented
		$fg = $SENSE{$rdid} eq "C" ? $blue : $dgray;
		$arr = $SENSE{$rdid} eq "C" ? "<<" : ">>";
		$im->stringFT($fg,$FONT,$FONTSIZE,0, 6, $y, $arr.$rdid );

		#
		# draw read image itself
		#
		$offset = $pl + $IMG_OFFSET{$rdid};		# offset for THIS read
		for ($j = 0, $k = 0; $j <= $#rdarray * $base_gap; $j++, $k+= $base_gap) {
		    my ($l, $y, $y1, $y2, $x, $colorindex);
		    $l = $rdarray[$j];				# get letter
		    $y = $csh + 1;
		    $y1 = $y + $i * $FH;
		    $y2 = $csh + 9 + $i * $FH;
		    $x = $k - $minbase + $offset - 1;
		    $colorindex = $colorhash{$l};		# get color
			# paint base char
			if($x > $pl){
			    if($do_diff >= 1){
					#     char($font,$x,$y,$char,$color)
					$im->stringFT($lightgray,$FONT,$FONTSIZE,0,$x, $y1,$l );
					$im->stringFT($colorindex,$FONT,$FONTSIZE,0,$x, $y1,$l ) unless $l eq $COARRAY[$j + $OFFSET{$rdid}-1];
				}else{
					$im->stringFT($colorindex,$FONT,$FONTSIZE,0,$x, $y1,$l );
				}
			}
		}

			# print iframe containing map
			if($do_diff >= 1){
				$map_ax = $offset;
				$map_ay = $y - $FH;
				$map_bx = $k - $minbase + $offset - 1;
				$map_by = $y;
				$mapline = map_line($map_ax,$map_ay,$map_bx,$map_by,$urlhash{$rdid}.$rdid,"_blank",$rdid);
				push(@mapdata,  $mapline );
			}
		}
	# print iframe containing map
	if($do_diff >= 1){
		push(@mapdata,"</map>");
		my$map = join("\n",@mapdata);
    	print_iframe($IFRAMEFILE,$map) ;
	}

}

sub print_iframe{
	my($mapfilename,$mapdata) = @_;
	open(MAP,">$mapfilename") or die $!;
	print MAP <<DATA;
<HTML>
<HEAD>
</HEAD>
<BODY>
<IMG SRC='<?php echo \$_GET[\"img\"]; ?>' BORDER=0  USEMAP='#mymap'>
   $mapdata
 </BODY>
</HTML>
DATA
    close MAP;
}



sub map_line{
	my($ax,$ay,$bx,$by,$href,$target,$alt) = @_;
	$target = "_blank" unless defined $target;
	$alt = "" unless defined $alt;
	return "    <area shape ='rect' coords ='$ax,$ay,$bx,$by' href ='$href' target ='$target' alt='$alt' />";
}
