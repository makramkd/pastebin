-- schema.sql
-- This file contains all the migrations to get the db up and running correctly.

\ir migrations/000_initialize.sql

\connect pastebin

\ir migrations/001_create_pastes.sql
