# Stage 1: Build Angular App
FROM node:18-alpine as builder

# Set working directory
WORKDIR /app

# Copy package files and install dependencies
COPY package*.json ./
RUN npm install

# Copy the rest of the app and build
COPY . .
RUN npm run build --prod

# Stage 2: Serve App with NGINX
FROM nginx:alpine

# Copy built files from builder stage to nginx html folder
COPY --from=builder /app/dist/your-angular-project-name /usr/share/nginx/html

# Optional: Replace default nginx config
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port
EXPOSE 80

# Start NGINX server
CMD ["nginx", "-g", "daemon off;"]