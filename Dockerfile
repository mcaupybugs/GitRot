# GitRot - Multi-service Dockerfile
# Runs both Next.js frontend and FastAPI backend in a single container

# Stage 1: Build Next.js frontend
FROM node:20-alpine AS frontend-builder

WORKDIR /app/frontend

# Copy package files
COPY gitrot-frontend/package*.json ./

# Install dependencies
RUN npm ci --only=production

# Copy source code
COPY gitrot-frontend/ ./

# Build the Next.js application
RUN npm run build

# Stage 2: Python base with both services
FROM python:3.11-slim AS production

# Install system dependencies with improved error handling
RUN apt-get update --allow-releaseinfo-change \
    && apt-get install -y --no-install-recommends \
    git \
    curl \
    supervisor \
    ca-certificates \
    gnupg \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* /var/cache/apt/archives/* \
    && curl -fsSL https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key | gpg --dearmor -o /usr/share/keyrings/nodesource.gpg \
    && echo "deb [signed-by=/usr/share/keyrings/nodesource.gpg] https://deb.nodesource.com/node_20.x nodistro main" > /etc/apt/sources.list.d/nodesource.list \
    && apt-get update \
    && apt-get install -y --no-install-recommends nodejs \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* /var/cache/apt/archives/* \
    && npm install -g npm@latest

# Create non-root user for security
RUN groupadd -r gitrot && useradd -r -g gitrot gitrot

# Create app directory
WORKDIR /app

# Copy Python requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy Python application files
COPY *.py ./
COPY static/ ./static/
COPY templates/ ./templates/
COPY examples/ ./examples/

# Copy built Next.js application from frontend-builder stage
COPY --from=frontend-builder /app/frontend/.next ./gitrot-frontend/.next
COPY --from=frontend-builder /app/frontend/public ./gitrot-frontend/public
COPY --from=frontend-builder /app/frontend/package*.json ./gitrot-frontend/
COPY --from=frontend-builder /app/frontend/next.config.ts ./gitrot-frontend/
COPY gitrot-frontend/src ./gitrot-frontend/src

# Install Next.js production dependencies
WORKDIR /app/gitrot-frontend
RUN npm ci --only=production

# Return to app directory
WORKDIR /app

# Create supervisord configuration
RUN mkdir -p /var/log/supervisor

# Create supervisor configuration file
COPY <<EOF /etc/supervisor/conf.d/supervisord.conf
[supervisord]
nodaemon=true
user=root
logfile=/var/log/supervisor/supervisord.log
pidfile=/var/run/supervisord.pid

[program:fastapi]
command=uvicorn fastapi_app:app --host 0.0.0.0 --port 8000
directory=/app
autostart=true
autorestart=true
stderr_logfile=/var/log/supervisor/fastapi_err.log
stdout_logfile=/var/log/supervisor/fastapi_out.log
environment=PYTHONPATH="/app",GIT_PYTHON_REFRESH="quiet"
user=gitrot

[program:nextjs]
command=npm start
directory=/app/gitrot-frontend
autostart=true
autorestart=true
stderr_logfile=/var/log/supervisor/nextjs_err.log
stdout_logfile=/var/log/supervisor/nextjs_out.log
environment=PORT="3000",NODE_ENV="production"
user=gitrot

[unix_http_server]
file=/var/run/supervisor.sock

[supervisorctl]
serverurl=unix:///var/run/supervisor.sock

[rpcinterface:supervisor]
supervisor.rpcinterface_factory = supervisor.rpcinterface:make_main_rpcinterface
EOF

# Change ownership of app directory to gitrot user
RUN chown -R gitrot:gitrot /app \
    && chown -R gitrot:gitrot /var/log/supervisor \
    && chmod -R 755 /app

# Create startup script
COPY <<EOF /app/start.sh
#!/bin/bash
set -e

echo "🚀 Starting GitRot Application..."
echo "📡 FastAPI will be available on port 8000"
echo "🎨 Next.js will be available on port 3000"

# Set Git environment variables
export GIT_PYTHON_REFRESH=quiet
export GIT_PYTHON_GIT_EXECUTABLE=\$(which git)

# Start supervisor
exec /usr/bin/supervisord -c /etc/supervisor/conf.d/supervisord.conf
EOF

# Make startup script executable
RUN chmod +x /app/start.sh

# Create healthcheck script
COPY <<EOF /app/healthcheck.sh
#!/bin/bash
# Health check for both services
curl -f http://localhost:8000/health || exit 1
curl -f http://localhost:3000/ || exit 1
EOF

RUN chmod +x /app/healthcheck.sh

# Expose ports
EXPOSE 3000 8000

# Add health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD /app/healthcheck.sh

# Set environment variables
ENV PYTHONPATH=/app
ENV NODE_ENV=production
ENV PORT=3000
ENV GIT_PYTHON_REFRESH=quiet

# Start the application
CMD ["/app/start.sh"]
