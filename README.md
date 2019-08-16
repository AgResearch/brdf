A postgres based database framework

The schema has now been split using a [script](scripts/split-postgres-schema),
into the subdirectory of schema.  The original non-split schema is in
the parent directory.

The whole schema can be loaded from the fragments via `db.sql`.
Once this is tested, the all-in-one schema should probably be deleted.
