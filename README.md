# BRDF

A postgres based database framework

## Development Environment

The BRDF development environment enables running of the application
within a Docker container, which is built from the bundled Dockerfile.

The script `run-dev-brdf` is run within the top-level directory of
this repo, and starts the container, listening on port (10000 + UID).
The following environment variables must be set before running the
script:

- BRDF_DATABASE_HOST
- BRDF_DATABASE_NAME
- BRDF_DATABASE_USER
- BRDF_DATABASE_PASSWORD


## Containerization

The `agresearch/brdf` container is built from `agresearch/caddy`,
because the interface to the Python scripts is old-school CGI, which
means the scripts must be installed into the same container as the
webserver.

### Building

To build the caddy container:
```
$ git clone https://github.com/abiosoft/caddy-docker.git
$ cd caddy-docker
$ docker build --build-arg version=1.0.3 --build-arg plugins=cgi --build-arg enable_telemetry=false -t agresearch/caddy:1.0.3-cgi .
```

To push the caddy container:
```
$ docker login
$ docker push agresearch/caddy:1.0.3-cgi
```

To build the brdf container (using a tag which corresponds to a git
tag, e.g. `dev1`):
```
$ git clone https://github.com/AgResearch/brdf.git
$ cd brdf
$ docker build -t agresearch/brdf:dev1 . && docker tag agresearch/brdf:dev1 agresearch/brdf:latest
```

To push the brdf container (assuming `docker login` has been run as above)
```
$ docker push agresearch/brdf:dev1 && docker push agresearch/brdf:latest
```

### Dependencies

Dependencies are installed into the container in the following ways.

#### Alpine Linux packages

The following packages are installed into the container from their Alpine Linux packages:

+ python2
+ py-egenix-mx-base
+ py-imaging
+ py-psycopg2

#### NPM Modules

The following packages are installed into the container using NPM, as defined in `package.json`.

+ dojo (note: 1.3.2 not available on NPM, so 1.6.5 has been used)
+ digit

## Schema

The schema has now been split using a [script](scripts/split-postgres-schema),
into the subdirectory of schema.  The original non-split schema is in
the parent directory.

The whole schema can be loaded from the fragments via `db.sql`.
Once this is tested, the all-in-one schema should probably be deleted.
