# Frontend Dockerfile — Vite Dev Server (ForgeBody style)
FROM node:20-alpine

WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN npm install

# Copy source
COPY . .

# Build arg for API URL (default to backend service name)
ARG VITE_API_BASE_URL=http://backend:8001
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL

EXPOSE 5173

# Run Vite dev server (serves files directly, no build step)
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
