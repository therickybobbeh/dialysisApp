#!/bin/sh

echo "Starting application setup..."
echo "Container environment:"
echo "BACKEND_URL: ${BACKEND_URL}"
echo "ENVIRONMENT: ${ENVIRONMENT}"

echo "Configuring nginx with envsubst..."
# Create the proper nginx configuration with environment variables
envsubst '${BACKEND_URL}' < /etc/nginx/templates/default.conf.template > /etc/nginx/conf.d/default.conf

# Check if index.html exists in expected location
if [ -f /usr/share/nginx/html/index.html ]; then
    echo "✅ Angular app index.html found"
    ls -la /usr/share/nginx/html/
else
    echo "⚠️ WARNING: index.html not found in /usr/share/nginx/html/"
    echo "Contents of /usr/share/nginx/html:"
    ls -la /usr/share/nginx/html/
    echo "Contents of /usr/share/nginx:"
    ls -la /usr/share/nginx/
fi

echo "Starting nginx..."
nginx -g 'daemon off;'