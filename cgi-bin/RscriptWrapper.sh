#!/bin/sh
#
# The only reason this exists, is to enable the set-up of the X11 display before R starts -
# there is an X11() function inside R that is supposed to do this but there
# is a bug in some versions of R whereby this does not work and you need to
# setup in the shell
#
export DISPLAY=localhost:999
/usr/bin/Rscript --vanilla $*
