# BRDF

A postgres based database framework

## Schema

The schema has now been split using a [script](scripts/split-postgres-schema),
into the subdirectory of schema.  The original non-split schema is in
the parent directory.

The whole schema can be loaded from the fragments via `db.sql`.
Once this is tested, the all-in-one schema should probably be deleted.

## Dependencies

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
