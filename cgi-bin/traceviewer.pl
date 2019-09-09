#!/usr/bin/perl -w
use ABI;

use GD::Graph::lines;
use GD::Graph::colour;
use GD::Graph::Data;

use Data::Dumper;


use Getopt::Long;

use constant HEIGHT => 300;

GetOptions ('h|height=i' => \$HEIGHT,
            'f|file=s' => \$FILE,
            'o|out=s' => \$OUTFILE,
            'l|left=s' => \$LEFT_SEQ,
            'r|right=s' => \$RIGHT_SEQ,
            's|size=i' => \$SIZE,
            ) || die <<USAGE;
Usage: perl $0 -h 400 -f 1188_13_14728111_16654_48544_080.ab1 -o test2.png -l actacgtacgta -r atgatcgtacgtac -s 678
or perl $0 --height 200 --file 1188_13_14728111_16654_48544_080.ab1 --out test2.png --left actacgtacgta --right atgatcgtacgtac --size 678

Options:
--height <pixels> Set height of image (${\HEIGHT} pixels default)
--file <trace file-name> Filename for the ABI trace file
--out <output file-name> Filename for the generated .png image
--left <left end sequence>
--right <right end sequence>
--size <size of clipped fasta sequence>

Parse an ABI trace file and render a PNG image.
See http://search.cpan.org/dist/ABI/ABI.pm
    or
    http://search.cpan.org/~bwarfield/GDGraph-1.44/Graph.pm
USAGE

my $height = $HEIGHT || HEIGHT;
my $file = $FILE;
my $outfile = $OUTFILE;

my $abi = ABI->new(-file=> $file);

my @trace_a = $abi->get_trace("A"); # Get the raw traces for "A"
my @trace_c = $abi->get_trace("C"); # Get the raw traces for "C"
my @trace_g = $abi->get_trace("G"); # Get the raw traces for "G"
my @trace_t = $abi->get_trace("T"); # Get the raw traces for "T"

my @base_calls = $abi->get_base_calls(); # Get the base calls
my $sequence =$abi->get_sequence();
@bp = split(//, $sequence);



# iterate over array
$size = $abi->get_trace_length();
for ($i=0,$count = 0; $i<$size; $i++) {
     if(grep(/\b$i\b/, @base_calls)){
       $bases[$i] = $bp[$count];
       $count++;
     }else{
       $bases[$i] = ' ';
     }
}

# create the data. see GD::Graph::Data for details of the format
my @data = (\@bases, \@trace_a, \@trace_c, \@trace_g, \@trace_t, );

my $graph = new GD::Graph::lines($abi->get_trace_length(),$height);
   $graph->set(
   title => $abi->get_sample_name(),
	y_max_value => $abi->get_max_trace() + 50,
	x_max_value => $abi->get_trace_length(),
	t_margin => 5,
    b_margin => 5,
    l_margin => 5,
    r_margin => 5,
    x_ticks => 0,
    text_space => 0,
	line_width 	=> 1,
	transparent	=> 0,
	b_margin => 30,
	t_margin => 35,
	x_plot_values => 0,
	interlaced => 1,
);

# allocate some colors for drawing the bases
#use colors same as Chromas
$graph->set( dclrs => [ qw( green blue black red pink) ] );
#plot the data
my $gd = $graph->plot(\@data);

$black = $gd->colorAllocate(0,0,0);       # A
$blue = $gd->colorAllocate(0,0,255);      # C
$red = $gd->colorAllocate(255,0,0);       # G
$green = $gd->colorAllocate(0,255,0);     # T
$magenta =$gd->colorAllocate(255,0,255);  # N
$white = $gd->colorAllocate(255,255,255);  # undefined aren't drawn
$gray = $gd->colorAllocate(210,210,210);
%colors = ("A", $green, "C", $blue, "G",$black, "T", $red, "N", $magenta, " ",$white);

#$start_base = index(lc($sequence),lc($LEFT_SEQ));
$start_base = find_match($sequence,$LEFT_SEQ);

#if($end_base = rindex(lc($sequence),lc($RIGHT_SEQ)) > 0){
$end_base = find_match($sequence,$RIGHT_SEQ, 1);
if($end_base){
 $end_base += length($RIGHT_SEQ);
}


# get the coords of the features on the image
@coords = $graph->get_hotspot(1);
$size = @coords;
$printed_num = 1;
$basecount = 0;

# draw the colored bases and scale at top and bottom of image
for ($i=0,$count = 0; $i<$size; $i++) {
  $c = $coords[$i];
  (undef, $xs, undef, undef, undef, undef) = @$c;
  $base = $bases[$i];
  if($base =~ /[ACGTN]/){
   if($start_base == $basecount){$start_base_coord = $xs;}
   if($end_base == $basecount){$end_base_coord = $xs;}
   $basecount++;
   $printed_num = 0;
  }
  # print the bases top and bottom
  $gd->string(GD::Font->Small(),$xs,20,$base,$colors{$base});
  $gd->string(GD::Font->Small(),$xs,$height - 30,$base,$colors{$base});

  if($basecount > 0 && $basecount % 10 == 0 && $printed_num == 0){
    if($LEFT_SEQ){
      $gd->string(GD::Font->Small(),$xs,5,$basecount - $start_base - 1,$black);
      $gd->string(GD::Font->Small(),$xs,$height - 15,$basecount - $start_base - 1,$black);
      $printed_num = 1;
    }else{
      $gd->string(GD::Font->Small(),$xs,5,$basecount,$black);
      $gd->string(GD::Font->Small(),$xs,$height - 15,$basecount,$black);
      $printed_num = 1;
    }
  }
  $top_right_corner = $xs;
}

# only draw the clipped region if the calculated size is + or - 6bp
if(($end_base - $start_base) - $SIZE <= 6 && ($end_base - $start_base) - $SIZE >= -6 ){
  # draw the clipped regions as gray
  $gd->filledRectangle(38,35,$start_base_coord - 1,$height - 33,$gray) if $LEFT_SEQ;
  $gd->filledRectangle($end_base_coord,35,$top_right_corner,$height - 33,$gray) if $RIGHT_SEQ && $end_base > 0;
  
  # need to re-plot the data over the grayed out area
  $graph->plot(\@data) if $LEFT_SEQ || $RIGHT_SEQ;
}

#print the graph
open(OUT, ">$outfile") or die "can't open output file: $outfile\n";
binmode OUT;
print OUT $gd->png;
close OUT;


sub find_match{
  my $sequence = shift;
  my $query = shift;
  my $last = shift;
  return -1 if length($query) < 6;
   # try exact match
    my $match_pos = do_regex($query, $sequence,$last);
    return $match_pos if $match_pos > 0;
    ########################
    # try matching every second base starting from the second base
       # make the regexp - e.g. it will be .C.T.C.G.etc , matching every second symbol
       my $pattern = $query;
       for( my $i =0 ; $i < length($query); $i += 1){
          if ($i % 2 == 0) {
             substr($pattern,$i,1)  = ".";
          }
       }
    my $match_pos = do_regex($pattern, $sequence,$last);
    return $match_pos if $match_pos > 0;
    ########################
    # try matching every second base starting from the first base
       # make the regexp - e.g. it will be C.T.C.G.etc , matching every second symbol
       my $pattern = $query;
       for( my $i =0 ; $i < length($query); $i += 1){
          if ($i % 2 == 1) {
             substr($pattern,$i,1)  = ".";
          }
       }
    my $match_pos = do_regex($pattern, $sequence,$last);
    return $match_pos if $match_pos > 0;
    ########################
    # try matching every third base starting from the first base
       # make the regexp - e.g. it will be C..T..G..T etc , matching every second symbol
       my $pattern = $query;
       for( my $i =0 ; $i < length($query); $i += 1){
          if ($i % 3 != 0) {
             substr($pattern,$i,1)  = ".";
          }
       }
    my $match_pos = do_regex($pattern, $sequence,$last);
    return $match_pos if $match_pos > 0;
    ########################
    # try matching every third base starting from the second base
       # make the regexp - e.g. it will be .C..T..C..G.etc , matching every second symbol
       my $pattern = $query;
       for( my $i =0 ; $i < length($query); $i += 1){
          if ($i % 3 != 1) {
             substr($pattern,$i,1)  = ".";
          }
       }
    my $match_pos = do_regex($pattern, $sequence,$last);
    return $match_pos if $match_pos > 0;
    ########################
    # try matching every third base starting from the third base
       # make the regexp - e.g. it will be ..C..T..C..G..etc , matching every second symbol
       my $pattern = $query;
       for( my $i =0 ; $i < length($query); $i += 1){
          if ($i % 3 != 2) {
             substr($pattern,$i,1)  = ".";
          }
       }
    my $match_pos = do_regex($pattern, $sequence,$last);
    return $match_pos if $match_pos > 0;
    ########################
     # not found
       return -1;

}

sub do_regex(){
	my $query = shift;
	my $sequence = shift;
    my $last = shift;
    my $result = -1;
    if($last){
      while($sequence =~ m/($query)/ig){
        $result = (pos($sequence)-length($query));
        }
    }else{
    	if($sequence =~ m/($query)/ig){
            $result = pos($sequence)-length($query) ;
    	}
    }
    return $result;
}
