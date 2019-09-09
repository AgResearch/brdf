#!/usr/bin/perl
use GD;
use GD::Polyline;
use Getopt::Long;

GetOptions ('f|file=s' => \$FILE,
            'o|out=s' => \$OUTFILE,
            'g|gray|grey' => \$GRAYSCALE,
            'd|diff' => \$DIFF_ONLY,
            'v|verbose' => \$VERBOSE,
            );

unless ($FILE and $OUTFILE){ die <<USAGE;
Usage: perl $0 -file CLP0001001240-cE15_20030319.ace -out test.png
or     perl $0 -file CLP0001001240-cE15_20030319.ace -out test.png -gray -diff
or     perl $0 -f CLP0001001240-cE15_20030319.ace -o test.png -g -d -v

Options:
-file <ace file-name>   Filename for the .ace file
-out <output file-name> Filename for the generated .png image
-gray 					Output grayscale image
-diff 					Show differences only
-verbose 				Show debugging information

Parse an .ace file and render a PNG image.
USAGE
}

$af = $FILE;
$out = $OUTFILE;
$FONT = gdTinyFont;
$base_gap = 5;   # width allowed for each char
$pad_left;       # allow room for the contig name
$longest_contig_name = -1;

&do_ace($af);

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
    open(ACE, "<$af") or die "couldn't open ace file: $!\n";

    # need to be set every time through
    $minbase =  100000;
    $maxbase = -100000;

    $/ = "";				# break on blank lines, not newlines
    while (<ACE>) {
	chomp;
	if (/^CO\s+(\w+)\s+(\d+)\s+(\d+)/) {
	    &ace_array;			# process previous contig
	    my $coline = $_;
	    $coid = $1;			# contig ID
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
	    $longest_contig_name = length($rdid) if (length($rdid) > $longest_contig_name);
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
    # calculate left padding based on longest contig name length
    $pad_left = ($FONT->width * $longest_contig_name) + 10;

    &ace_array;					# process last contig
}

sub ace_array {
	if (not defined($coid)) {return;}		# first time, nothing to do
	if ($VERBOSE) {
	    print "#### BEGIN ace_array ####\n";
	    print "CO info: $coid $colen $coreadn \n";
	    print "COARRAY size = $#COARRAY\n";		#, COARRAY = @COARRAY\n\n";
	    print "BQARRAY size = $#BQARRAY\n";		#, BQARRAY = @BQARRAY\n\n";
	    print "RDID size = $#RDID, RDID = @RDID\n\n";
	    print "RDARRAY size = $#RDARRAY\n";		#, RDARRAY = @RDARRAY\n\n";
	    foreach $rdarray (@RDARRAY) {
			print "rdarray = @$rdarray\n\n";
	    }
	    for ($i = 0; $i <= $#RDARRAY; $i++) {
			$rar  = $RDARRAY[$i];
			@rdarray = @$rar;
			# for now generate gel on left
			for ($j = 0; $j <= $#rdarray; $j++) {
			    $l = $rdarray[$j];
			    print "$l ";
			}
			print "\n\n";
	    }

	    @sensearray = sort keys %SENSE;
	    foreach $sense (@sensearray) {
			print "sense{$sense} = $SENSE{$sense}\n";
	    }
	    @offsetarray = sort keys %OFFSET;
	    foreach $offset (@offsetarray) {
			print "offset{$offset} = $OFFSET{$offset}\n";
	    }
	    print "minbase, maxbase = $minbase, $maxbase\n";
	    print "#### END ace_array ####\n";
	}
	
	&gd_contig ();			# create the contig image
	# reinitialize all arrays and hashes to null
	@COARRAY = ();
	@BQARRAY = ();
	@RDARRAY = ();
	@RDID = ();
	%SENSE = ();
	%OFFSET = ();
	
	# reset for the next contig
	$minbase =  100000;
	$maxbase = -100000;
}

#
# gd_contig creates a new contig image
#
sub gd_contig{
    # These are needed now to figure the height of the image
    $scaleh = 30;					# scale height
    $consensush = 30;					# consensus height
    $traceh = 30;                         # quality trace height
    $csh = $scaleh + $consensush + $traceh;			# bottom of consensus

    $width  = ($maxbase - $minbase)*$base_gap;		# minbase can be negative
    $height = $csh + 10 * ($#RDID + 1) + 4;	# scale + consensus + each read
    $theight = @RDID + 1;			# height of thumbnail image
    my $im = new GD::Image($width + $pad_left + 20, $height);

	# first color allocated will be background
	$white = $im->colorAllocate(255, 255, 255);
	$black = $im->colorAllocate(0, 0, 0);
	$gray = $im->colorAllocate(165, 165, 165);
	$lightgray = $im->colorAllocate(230, 230, 230);

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

    gd_quality($im);		# draw quality trace
    gd_consensus($im);		# draw scale and consensus
    gd_reads($im);			# draw all reads

    if($GRAYSCALE){
		for (my $i = 0; $i < $im->colorsTotal(); $i++) {
			my ($r, $g, $b) = $im->rgb($i);
			my $_gray = grayscale($r,$g,$b);
			$im->colorDeallocate($i);
			$im->colorAllocate($_gray,$_gray,$_gray);
		}
	}

    open(PNG, ">$out") || die "open $out $!\n";
    # make sure we are writing to a binary stream
    binmode PNG;
    print PNG $im->png;
    close PNG;
}

#
# draw quality plot
#
sub gd_quality {
    $im = shift;

    # Add consensus name to upper left corner
    $im->string($FONT, 6, $scaleh + 44, "QUALITY:", $black);
    $im->string($FONT, $pad_left - 25, $csh - 5 - 1 - 5, "  0 -", $black);
    $im->string($FONT, $pad_left - 25, $csh - $consensush - 5, ">30 -", $black);

    # Add consensus image underneath scale
    $q = 0;						# BQ array index
    $polyline = new GD::Polyline;
    for ($i = 0, $m = 0; $i <= $#COARRAY; $i++, $m += $base_gap) {
		$l = $COARRAY[$i];				# get letter			# get color
		# allow 200 pixels for the name field
		$x = $pad_left + $m - $minbase;
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
    # Add scale to top of image and vertical bars every 10 bp
    for ($i = 0; $i < $maxbase * $base_gap; $i+=100) {
	$x = $pad_left - $minbase + $i - 2;			# why 2?
	$im->stringUp($FONT, $x + 3, $scaleh - 5, $i/$base_gap, $black);
	$im->line($x + 2, $scaleh - 9, $x + 2, $height, $gray);
    }
    $im->line($pad_left - $minbase, $scaleh - 2, $pad_left + ($maxbase *$base_gap) , $scaleh - 2, $red);

    # Add consensus name to upper left corner
    $im->string($FONT, 6, $scaleh + 0, $coid, $black);
    $im->string($FONT, 6, $scaleh + 14, "CONSENSUS:", $black);

    # Add consensus image underneath scale
    $q = 0;						# BQ array index
    for ($i = 0, $m = 0; $i <= $#COARRAY; $i++, $m += $base_gap) {
		$l = $COARRAY[$i];				# get letter
		$colorindex = $colorhash{$l};			# get color
		$x = $pad_left + $m - $minbase;
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
		$im->string($FONT,$x, $scaleh + 14,$l, $colorindex);	# paint base char
		$q++ unless ($l eq "*");
    }
}

#
# Go through RDARRAY arrays to generate the read images
#
sub gd_reads {
    my $im = shift;
    my ($i, $j);

    # Add reads to image
    for ($i = 0; $i <= $#RDARRAY; $i++) {
		my ($rar, $rdid, $y, $fg, $offset, @rdarray);
		# put the name on the left, allowing 200 pixels
		$rar  = $RDARRAY[$i];		# this needs two statements
		@rdarray = @$rar;
		$rdid = $RDID[$i];			# name (ID) of THIS read
		$y = $csh +2 + $i * 10;
		# use dark-gray fg for normal sequences, blue fg for reverse complemented
		$fg = $dgray;
		if ($SENSE{$rdid} eq "C") {$fg = $blue;}
		$im->string($FONT, 6, $y, $rdid, $fg);

		#
		# draw read image itself
		#
		$offset = $pad_left + $IMG_OFFSET{$rdid};		# offset for THIS read
		for ($j = 0, $k = 0; $j <= $#rdarray * $base_gap; $j++, $k+= $base_gap) {
		    my ($l, $y, $y1, $y2, $x, $colorindex);
		    $l = $rdarray[$j];				# get letter
		    $y = $csh + 1;
		    $y1 = $y + $i * 10;
		    $y2 = $csh + 9 + $i * 10;
		    $x = $k - $minbase + $offset - 1;
		    $colorindex = $colorhash{$l};		# get color
			# paint base char
		    if($DIFF_ONLY){
				$im->char($FONT,$x, $y1,$l, $lightgray);
				$im->char($FONT,$x, $y1,$l, $colorindex) unless $l eq $COARRAY[$j + $OFFSET{$rdid}-1];
			}else{
				$im->char($FONT,$x, $y1,$l, $colorindex);
			}
		}
    }
}

# grayscale subroutine
# http://www.perlmonks.org/?node_id=316174
sub grayscale {
	my ($r, $g,$b) = @_;
	my $s = 0.11 * $r + 0.59 * $g + 0.30 * $b;
	return int($s); 
}
