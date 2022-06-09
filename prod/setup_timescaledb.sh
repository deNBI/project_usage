#!/bin/bash
set -e

FILE=/docker-entrypoint-initdb.d/credits_db.dump

psql -v ON_ERROR_STOP=1 -U postgres -d credits_db <<-EOSQL
    ALTER ROLE postgres SET client_encoding TO 'utf8';
    ALTER ROLE postgres SET default_transaction_isolation TO 'read committed';
    ALTER ROLE postgres SET timezone TO 'UTC';
    GRANT ALL PRIVILEGES ON DATABASE credits_db TO postgres;
    CREATE EXTENSION IF NOT EXISTS timescaledb;
EOSQL

if test -f "$FILE"; then
echo "got here"
psql -v ON_ERROR_STOP=1 -U postgres -d credits_db <<-EOSQL
    SELECT timescaledb_pre_restore();
EOSQL
psql -U postgres --set ON_ERROR_STOP=on -d credits_db -f /docker-entrypoint-initdb.d/credits_db.dump
psql -v ON_ERROR_STOP=1 -U postgres -d credits_db <<-EOSQL
    SELECT timescaledb_post_restore();
EOSQL
fi
