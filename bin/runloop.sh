#!/bin/sh -e
cd /var/www/sandtable
until $@; do
    echo "$1 crashed with exit code $?.  Respawning." >&2
    sleep 1
done
