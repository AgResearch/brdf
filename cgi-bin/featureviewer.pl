#!/usr/bin/perl

use strict;

use Bio::Graphics::Panel;
use Bio::Graphics::Feature;
use Bio::Graphics::FeatureFile;

use Getopt::Long;

use Data::Dumper;


use constant WIDTH => 600;
use constant IMAGE => "image.png";
use constant MAP => "map.txt";
use constant MAP_NAME => time().'.map';

my ($WIDTH,$IMAGE,$MAP,$MAP_NAME, $FEATURES);

GetOptions ('w|width=i'  => \$WIDTH,
            'i|image=s'  => \$IMAGE,
            'm|map=s'    => \$MAP,
            'n|mapname=s' => \$MAP_NAME,
            'f|features=s' => \$FEATURES,
	   ) || die <<USAGE;
Usage:  perl $0 --width 800 --map my_map.txt --image my_image.png --mapname my_test_map --features features.gff
or      perl $0 -w 700 -m my_map.txt -i my_image.png -n my_test_map -f features.gff


 Options:
    --width   <pixels>           Set width of image (${\WIDTH} pixels default)
    --image   <image file-name>  Filename for the image (${\IMAGE}  default)
    --map     <map file-name>    Filename for the image-map (${\MAP}  default)
    --mapname <map name>         Name for the image-map (${\MAP_NAME}  (current time in epoch seconds) default)
    --features <features gff>    Filename of the feature file

Render a Bio::Graphics feature file and produce a PNG image and image map.
See the manual page for Bio::Graphics::FeatureFile for a
description of the file format.
USAGE

my @COLORS = qw(cyan blue red yellow green wheat turquoise orange);  # default colors
my $color = 0;      # position in color cycle

my $data = Bio::Graphics::FeatureFile->new(-file => $FEATURES);

# general configuration of the image here
my $width          = $WIDTH    || $data->setting(general => 'pixels')
                               || $data->setting(general => 'width')
                               || WIDTH;
$width -= 40; # subtract padding

my $image_filename = $IMAGE    || $data->setting(general => 'image_filename')
                               || IMAGE;
my $map_filename   = $MAP      || $data->setting(general => 'map_filename')
                               || MAP;
my $map_name       = $MAP_NAME || $data->setting(general => 'map_name')
                               || MAP_NAME;

my $start = $data->min;
my $stop  = $data->max;

# Use the order of the stylesheet to determine features.  Whatever is left
# over is presented in alphabetic order
my %types = map {$_=>1} $data->configured_types;

#my @configured_types   = grep {exists $data->features->{$_}} $data->configured_types;
my @configured_types = grep +{ exists $data->features->{$_} }, $data->configured_types;

my @unconfigured_types = sort grep {!exists $types{$_}}      $data->types;

# create the segment,the panel and the arrow with tickmarks
my $segment = Bio::Graphics::Feature->new(-start=>$start,-stop=>$stop);
my $panel = Bio::Graphics::Panel->new(-segment   => $segment,
				      -width     => $width,
                      -pad_left  => 20,
                      -pad_right => 20,
				      -key_style => 'between');
$panel->add_track($segment,-glyph=>'arrow',-tick=>2);

my @base_config = $data->style('general');

for my $type (@configured_types,@unconfigured_types) {
  my @config = ( -glyph   => 'segments',         # really generic
		 -bgcolor => $COLORS[$color++ % @COLORS],
		 -label   => 1,
		 -key     => $type,
		 @base_config,             # global
		 $data->style($type),  # feature-specificp
	       );
  my $features = $data->features($type);
  $panel->add_track($features,@config);

}
# add an extra ruler at the bottom
$panel->add_track($segment,-glyph=>'arrow',-tick=>2);

my $gd = $panel->gd;


#print image
open(PNG, ">$image_filename") or die "can't create png output file: $image_filename\n";
print PNG $gd->can('png') ? $gd->png : $gd->gif;
my($width,$height) = $gd->getBounds();
close PNG;

# print the map
open (IMAGEMAP, ">$map_filename") or die "can't create map output file: $map_filename\n";
print IMAGEMAP "<!-- $width x $height -->\n";
print IMAGEMAP $panel->create_web_map($map_name);
close IMAGEMAP;

1;
