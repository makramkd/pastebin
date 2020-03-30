FROM postgres:9.6-alpine as postgres-dev

# Setup migrations to run on startup if they haven't
COPY ./migrations/*.sql /docker-entrypoint-initdb.d/migrations/
COPY ./schema.sql /docker-entrypoint-initdb.d/1_schema.sql
