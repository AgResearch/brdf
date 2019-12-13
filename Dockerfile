# Dockerfile for BRDF

FROM alpine AS builder
WORKDIR /build
COPY package.json .
RUN apk add --no-cache npm && npm install

# this old version of docker doesn't support args in image reference, bah!
# be careful to keep the next two lines in sync
ARG caddy_version=1.0.3-cgi
FROM agresearch/caddy:1.0.3-cgi
ARG caddy_version
LABEL maintainer "Simon Guest <simon.guest@tesujimath.org"
LABEL caddy_version ${caddy_version}

RUN apk add --no-cache python2 py-egenix-mx-base py-pillow py-psycopg2 rsync
COPY --from=builder /build/node_modules /srv/node_modules

# webserver config
COPY Caddyfile /etc/Caddyfile

# install BRDF
ARG rootfilepath=/var/www/agbrdf
ARG python_package_dst=/usr/lib/python2.7/site-packages
RUN mkdir -p $rootfilepath
COPY cgi-bin html $rootfilepath/
COPY python-packages/agbrdf* python-packages/brdf* $python_package_dst/
RUN mkdir -p $rootfilepath/html/tmp
COPY tmp_images /usr/src/brdf-tmp

# entrypoint
COPY entrypoint.sh /usr/local/bin/

# as per caddy Dockerfile:
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
CMD ["/bin/parent", "caddy", "--conf", "/etc/Caddyfile", "--log", "stdout", "--agree=$ACME_AGREE"]
