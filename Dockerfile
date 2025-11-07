# Dockerfile for Railway deployment
# Railway will use this if Nixpacks fails

FROM node:18-alpine AS frontend-builder

# Install pnpm (use latest version to match lockfile)
RUN npm install -g pnpm@latest

# Install Python
RUN apk add --no-cache python3 py3-pip

WORKDIR /app

# Copy entire frontend directory structure first
COPY polish-finance-platform/ ./polish-finance-platform/

# Install frontend dependencies
WORKDIR /app/polish-finance-platform/polish-finance-app
# Debug: show what files are present
RUN echo "=== Files in current directory ===" && \
    ls -la && \
    echo "=== Checking for pnpm-lock.yaml ===" && \
    test -f pnpm-lock.yaml && echo "✅ pnpm-lock.yaml EXISTS" || echo "❌ pnpm-lock.yaml NOT FOUND"
# Install dependencies (lockfile exists, use it)
RUN pnpm install --frozen-lockfile

# Build frontend
RUN pnpm run build:prod

# Install Python dependencies
WORKDIR /app
COPY code/requirements.txt ./code/
RUN pip install --no-cache-dir -r code/requirements.txt

# Copy Python code
COPY code/ ./code/
COPY data/ ./data/

# Expose ports
EXPOSE 4173 8000 8001

# Start command (Railway will override this)
CMD ["sh", "-c", "cd polish-finance-platform/polish-finance-app && pnpm run start"]


