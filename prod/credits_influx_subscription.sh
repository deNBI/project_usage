#!/bin/sh

influx -username "$INFLUXDB_ADMIN_USER" \
	-password "$INFLUXDB_ADMIN_PASSWORD" \
	-execute "create subscription \"credits\" on \"$INFLUXDB_DB\".\"autogen\" destinations all 'http://portal_credits:80'"
influx -username "$INFLUXDB_ADMIN_USER" \
	-password "$INFLUXDB_ADMIN_PASSWORD" \
	-execute "create database \"$CREDITS_HISTORY_DB\""
influx -username "$INFLUXDB_ADMIN_USER" \
	-password "$INFLUXDB_ADMIN_PASSWORD" \
	-execute "grant all on \"$CREDITS_HISTORY_DB\" to \"$INFLUXDB_USER\""
