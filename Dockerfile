# Dockerfile for Railway deployment
FROM node:18-alpine AS frontend-builder

# Install pnpm (use latest version to match lockfile)
RUN npm install -g pnpm@latest

# Install Python
RUN apk add --no-cache python3 py3-pip

WORKDIR /app

# Copy entire frontend directory structure (all files including src/lib/)
COPY polish-finance-platform/polish-finance-app/ ./polish-finance-platform/polish-finance-app/

# Install frontend dependencies
WORKDIR /app/polish-finance-platform/polish-finance-app

# Verify src/lib files are copied (debug)
RUN echo "=== Checking src/lib files ===" && \
    ls -la src/lib/ 2>&1 || echo "src/lib not found" && \
    echo "=== Files in src/lib ===" && \
    ls -la src/lib/*.ts 2>&1 || echo "No .ts files found"

# Install dependencies - always use --no-frozen-lockfile to avoid version issues
RUN pnpm install --no-frozen-lockfile

# Build frontend
RUN pnpm run build:prod

# Install Python dependencies (use --break-system-packages for Docker containers)
WORKDIR /app
COPY code/requirements.txt ./code/
# Force pip to use --break-system-packages (required for Python 3.11+ in Alpine)
RUN pip install --no-cache-dir --break-system-packages -r code/requirements.txt || \
    (echo "⚠️  pip install failed, retrying..." && pip install --no-cache-dir --break-system-packages -r code/requirements.txt)

# Copy Python code
COPY code/ ./code/
COPY data/ ./data/

# Expose ports
EXPOSE 4173 8000 8001

# Start command (Railway will override this)
CMD ["sh", "-c", "cd polish-finance-platform/polish-finance-app && pnpm run start"]
