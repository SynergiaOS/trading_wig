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
# Install dependencies (try frozen-lockfile first, fallback to regular install)
RUN if [ -f pnpm-lock.yaml ]; then \
        pnpm install --frozen-lockfile; \
    else \
        echo "⚠️  pnpm-lock.yaml not found, installing without lockfile"; \
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


