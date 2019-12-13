#!/bin/sh

rsync -a /usr/src/brdf-tmp/ /var/www/agbrdf/html/tmp/
exec "$@"
