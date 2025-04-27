#!/bin/sh

echo "Configuring nginx with envsubst..."
envsubst '${BACKEND_URL}' < /etc/nginx/templates/default.conf.template > /etc/nginx/conf.d/default.conf

echo "Starting nginx..."
nginx -g 'daemon off;'