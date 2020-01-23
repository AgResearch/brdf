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
COPY cgi-bin /var/www/agbrdf/cgi-bin/
COPY html /var/www/agbrdf/html/
COPY python-packages/agbrdf /usr/lib/python2.7/site-packages/agbrdf/
COPY python-packages/agbrdf.pth /usr/lib/python2.7/site-packages/
COPY python-packages/brdf /usr/lib/python2.7/site-packages/brdf/
COPY python-packages/brdf.pth /usr/lib/python2.7/site-packages/
RUN mkdir -p /var/www/agbrdf/html/tmp
COPY tmp_images /var/www/agbrdf/html/tmp/

# persistent, with initial contents as above
VOLUME /var/www/agbrdf/html/tmp

# as per caddy Dockerfile:
ENTRYPOINT ["/bin/parent", "caddy"]
CMD ["--conf", "/etc/Caddyfile", "--log", "stdout", "--agree=$ACME_AGREE"]
