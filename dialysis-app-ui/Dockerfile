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
RUN npm run build -- --configuration production

# Stage 2: Nginx runtime
FROM nginx:1.25-alpine

# Copy built assets from builder stage
COPY --from=builder /app/dist/dialysis-app /usr/share/nginx/html

# Create environments directory for runtime configuration
RUN mkdir -p /usr/share/nginx/html/environments /etc/nginx/templates

# Copy our environment script for runtime config if it exists
COPY --from=builder /app/src/environments/environment.prod.js /usr/share/nginx/html/environments/ 2>/dev/null || :

# Install envsubst to process environment variables
RUN apk add --no-cache bash gettext

# Copy nginx.conf to templates directory
COPY nginx.conf /etc/nginx/templates/default.conf.template

# Set default BACKEND_URL value
ENV BACKEND_URL=http://pd-management-backend

# Create required directories with proper permissions for non-root operation
RUN mkdir -p /tmp/nginx/client-body && \
    mkdir -p /var/run && \
    mkdir -p /var/cache/nginx && \
    chmod -R 777 /var/run && \
    chmod -R 777 /var/cache/nginx && \
    chmod -R 777 /tmp/nginx && \
    chmod -R 777 /etc/nginx/conf.d && \
    chmod -R 777 /etc/nginx/templates && \
    # Update nginx config to use accessible paths
    sed -i 's!/var/run/nginx.pid!/tmp/nginx.pid!g' /etc/nginx/nginx.conf && \
    sed -i 's!user nginx!#user nginx!g' /etc/nginx/nginx.conf && \
    sed -i 's!/var/cache/nginx!/tmp/nginx/cache!g' /etc/nginx/nginx.conf

# COPY the new entrypoint
COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
  CMD wget -q -O - http://localhost:80/health || exit 1

# Expose port 80
EXPOSE 80

# Use the entrypoint script
ENTRYPOINT ["/docker-entrypoint.sh"]