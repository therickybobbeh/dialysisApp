# Multi-stage build for Angular application
# Stage 1: Node builder image
FROM node:18-alpine AS builder

# Set working directory
WORKDIR /app

# Copy package.json and package-lock.json for better caching
COPY package.json package-lock.json ./

# Install dependencies with npm ci for reproducible builds
RUN npm ci

# Copy the rest of the source code
COPY . .

# Build the Angular application with production optimizations
RUN npm run build -- --configuration production --output-path=/app/dist

# Stage 2: Nginx runtime
FROM nginx:1.25-alpine

# Copy nginx.conf directly to the conf.d directory
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy built assets from builder stage
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy a startup script to replace environment variables in the nginx config
COPY --from=builder /app/src/environments/environment.prod.js /usr/share/nginx/html/environments/

# Create a startup script to inject environment variables
RUN echo '#!/bin/sh \n\
envsubst < /etc/nginx/conf.d/default.conf > /etc/nginx/conf.d/default.conf.tmp \n\
mv /etc/nginx/conf.d/default.conf.tmp /etc/nginx/conf.d/default.conf \n\
nginx -g "daemon off;"' > /docker-entrypoint.sh && \
chmod +x /docker-entrypoint.sh

# Create required directories with proper permissions for non-root operation
RUN mkdir -p /tmp/nginx/client-body && \
    mkdir -p /var/run && \
    mkdir -p /var/cache/nginx && \
    chmod -R 777 /var/run && \
    chmod -R 777 /var/cache/nginx && \
    chmod -R 777 /tmp/nginx && \
    chmod -R 777 /etc/nginx/conf.d && \
    # Update nginx config to use accessible paths
    sed -i 's!/var/run/nginx.pid!/tmp/nginx.pid!g' /etc/nginx/nginx.conf && \
    sed -i 's!user nginx!#user nginx!g' /etc/nginx/nginx.conf && \
    sed -i 's!/var/cache/nginx!/tmp/nginx/cache!g' /etc/nginx/nginx.conf && \
    # Create non-root user
    addgroup -g 1000 -S appgroup && \
    adduser -u 1000 -S appuser -G appgroup && \
    chown -R appuser:appgroup /usr/share/nginx/html /etc/nginx/conf.d /docker-entrypoint.sh

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:80/health || exit 1

# Switch to non-root user
USER appuser

# Expose port 80
EXPOSE 80

# Start with our entrypoint script
CMD ["/docker-entrypoint.sh"]