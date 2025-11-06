FROM node:18-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install --production

# Copy application files
COPY . .

# Build the application (if needed)
# RUN npm run build

# Expose port
EXPOSE 3000

# Start the application
CMD ["npm", "start"]