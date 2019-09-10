# BRDF

A postgres based database framework

## Development Environment

The BRDF development environment enables running of the application
within a Docker container, which is built from the bundled Dockerfile.

The script `run-dev-brdf` is run within the top-level directory of
this repo, and starts the container, listening on port (10000 + UID).
The following environment variables must be set before running the
script:

- BRDF_DATABASE
- BRDF_DATABASE_USER
- BRDF_DATABASE_PASSWORD


## Schema

The schema has now been split using a [script](scripts/split-postgres-schema),
into the subdirectory of schema.  The original non-split schema is in
the parent directory.

The whole schema can be loaded from the fragments via `db.sql`.
Once this is tested, the all-in-one schema should probably be deleted.

## Container Dependencies

Dependencies are installed in various ways.

### Alpine Linux packages

The following packages are installed into the container from their Alpine Linux packages:

+ python2
+ py-egenix-mx-base
+ py-imaging
+ py-psycopg2

### NPM Modules

The following packages are installed into the container using NPM, as defined in `package.json`.

+ dojo (note: 1.3.2 not available on NPM, so 1.6.5 has been used)
+ digit
