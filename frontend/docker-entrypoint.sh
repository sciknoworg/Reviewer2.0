#!/bin/sh
# Runs as one of nginx's /docker-entrypoint.d/ startup scripts, before nginx
# itself is started by the base image's own entrypoint.
set -e

envsubst '${API_BASE_URL}' < /usr/share/nginx/html/js/config.js.template > /usr/share/nginx/html/js/config.js
