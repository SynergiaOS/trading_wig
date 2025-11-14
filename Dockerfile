# Dockerfile for Railway deployment
FROM node:18-alpine AS frontend-builder

# Install pnpm (use latest version to match lockfile)
RUN npm install -g pnpm@latest

# Install Python
RUN apk add --no-cache python3 py3-pip py3-virtualenv

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

# Install Python dependencies (use virtual environment to avoid PEP 668 restrictions)
WORKDIR /app
COPY code/requirements.txt ./code/
# Create Python virtual environment to isolate dependencies
RUN virtualenv /app/venv
# Activate virtual environment for all subsequent commands
ENV PATH="/app/venv/bin:$PATH"
# Install build tools and headers for packages with C extensions
RUN apk add --no-cache build-base python3-dev musl-dev libffi-dev openssl-dev postgresql-dev zlib-dev
# Install packages into virtual environment
RUN python -m pip install --no-cache-dir -r code/requirements.txt

# Copy Python code
COPY code/ ./code/
COPY data/ ./data/

# Expose ports
EXPOSE 4173 8000 8001

# Start command (Railway will override this)
CMD ["sh", "-c", "cd polish-finance-platform/polish-finance-app && pnpm run start"]
