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

# Install debugging tools
RUN apk add --no-cache bash curl

# Create necessary directories first
RUN mkdir -p /usr/share/nginx/html /etc/nginx/templates

# Copy built assets from builder stage to the nginx html directory
# This is the critical part - make sure the Angular app files are copied correctly
COPY --from=builder /app/dist/dialysis-app/* /usr/share/nginx/html/

# Copy nginx configuration
COPY nginx.conf /etc/nginx/templates/default.conf.template

# Set default BACKEND_URL value
ENV BACKEND_URL=http://pd-management-backend

# Copy the entrypoint script
COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

# Add a healthcheck that verifies the /health endpoint
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:80/health || exit 1

# Expose port 80
EXPOSE 80

# Use the entrypoint script
ENTRYPOINT ["/docker-entrypoint.sh"]