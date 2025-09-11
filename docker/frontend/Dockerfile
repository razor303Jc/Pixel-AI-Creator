# Multi-stage build for React frontend
FROM node:18-alpine AS builder

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install all dependencies (including dev dependencies for build)
RUN npm install

# Copy source code and build
COPY . .
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy built app from builder stage
COPY --from=builder /app/build /usr/share/nginx/html

# Copy custom nginx config
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port
EXPOSE 3000

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
