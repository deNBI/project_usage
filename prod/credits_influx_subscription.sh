#!/bin/sh

influx -username "$INFLUXDB_ADMIN_USER" \
	-password "$INFLUXDB_ADMIN_PASSWORD" \
	-database "$INFLUXDB_DB" \
	-execute "create subscription \"credits\" on \"$INFLUXDB_DB\".\"autogen\" destinations all 'http://portal_credits:80'"
