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

RUN apk add --no-cache python2 py-egenix-mx-base py-pillow py-psycopg2
COPY --from=builder /build/node_modules /srv/node_modules

# as per caddy Dockerfile:
ENTRYPOINT ["/bin/parent", "caddy"]
CMD ["--conf", "/etc/Caddyfile", "--log", "stdout", "--agree=$ACME_AGREE"]
