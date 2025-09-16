# frontend/Dockerfile
FROM node:20-alpine

# Set working directory
WORKDIR /app

# Copy only package files first (better caching for npm install)
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy source code
COPY . .

# Expose Vite default port
EXPOSE 5173

# Run dev server with host binding
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]