# Dockerfile for Railway deployment
# Railway will use this if Nixpacks fails

FROM node:18-alpine AS frontend-builder

# Install pnpm
RUN npm install -g pnpm@8

# Install Python
RUN apk add --no-cache python3 py3-pip

WORKDIR /app

# Copy entire frontend directory structure first
COPY polish-finance-platform/ ./polish-finance-platform/

# Install frontend dependencies
WORKDIR /app/polish-finance-platform/polish-finance-app
RUN ls -la pnpm-lock.yaml 2>&1 || echo "WARNING: pnpm-lock.yaml not found" && \
    if [ -f pnpm-lock.yaml ]; then \
        echo "Found pnpm-lock.yaml, using --frozen-lockfile"; \
        pnpm install --frozen-lockfile; \
    else \
        echo "No pnpm-lock.yaml, generating new one"; \
        pnpm install; \
    fi

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


