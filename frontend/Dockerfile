# Use Node.js for building Next.js
FROM node:18 AS builder

WORKDIR /app

# Copy package.json and package-lock.json
COPY package.json package-lock.json ./
RUN npm install

# Copy everything (fix missing files issue)
COPY . .

# Build the Next.js app
RUN npm run build

# Use a lightweight image for running the app
FROM node:18 AS runner
WORKDIR /app

# Copy built files
COPY --from=builder /app/.next .next
COPY --from=builder /app/public public
COPY --from=builder /app/package.json package.json
COPY --from=builder /app/node_modules node_modules

# Set environment variables
ENV NODE_ENV=production

# Expose the port
EXPOSE 3000

# Start the app
CMD ["npm", "start"]
