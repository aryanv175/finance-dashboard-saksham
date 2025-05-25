# frontend/Dockerfile
FROM node:18-alpine

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci --only=production

# Copy source code
COPY . .

# Build the application
RUN npm run build

# Expose the port
EXPOSE 4173

# Command to run the application
CMD ["npm", "run", "preview", "--", "--host", "0.0.0.0"]