CREATE ROLE pastebin_rw LOGIN PASSWORD 'devsecret';
CREATE ROLE pastebin_ro LOGIN PASSWORD 'devsecret';

CREATE DATABASE pastebin;
GRANT CONNECT, TEMP ON DATABASE pastebin TO pastebin_rw;
GRANT CONNECT, TEMP ON DATABASE pastebin TO pastebin_ro;

\connect pastebin

ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT, INSERT, UPDATE ON TABLES TO pastebin_rw;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO pastebin_ro;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT USAGE, SELECT ON SEQUENCES TO pastebin_rw;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON SEQUENCES TO pastebin_ro;

-- Keep track of migrations in this table
CREATE TABLE schema_migrations(
    version text primary key,
    timestamp timestamptz default now()
);
