# Use Python 3.11 as the base image
FROM python:3.11-slim-bookworm

# Install Node.js and other necessary tools
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    nodejs \
    npm \
    git \
    ripgrep \
    caddy \
    build-essential && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Create a virtual environment and activate it, installing necessary packages there
RUN python -m venv /opt/venv

# Activate the virtual environment, upgrade pip within it, and install markopolis
RUN /bin/sh -c ". /opt/venv/bin/activate && \
    pip install --upgrade pip && \
    pip install --no-cache-dir markopolis==1.1.3 && \
    pip show markopolis"

# Set up frontend
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./

# Build frontend

ARG MARKOPOLIS_API_KEY
ARG MARKOPOLIS_DOMAIN
ARG MARKOPOLIS_FRONTEND_URL
ARG MARKOPOLIS_MD_PATH
ARG VITE_MARKOPOLIS_API_KEY
ARG VITE_MARKOPOLIS_DOMAIN
ENV VITE_MARKOPOLIS_API_KEY=$MARKOPOLIS_API_KEY
ENV VITE_MARKOPOLIS_DOMAIN=$VITE_MARKOPOLIS_DOMAIN
ENV MARKOPOLIS_API_KEY=$MARKOPOLIS_API_KEY
ENV MARKOPOLIS_DOMAIN=$MARKOPOLIS_DOMAIN
ENV MARKOPOLIS_FRONTEND_URL=$MARKOPOLIS_FRONTEND_URL
ENV MARKOPOLIS_MD_PATH=$MARKOPOLIS_MD_PATH
RUN npm run build

# Copy Caddyfile
COPY Caddyfile /etc/caddy/Caddyfile

# Expose ports
EXPOSE 80 8000 3000

# Create a startup script
RUN echo '#!/bin/sh' > /start.sh && \
    echo 'echo "Node.js version:"' >> /start.sh && \
    echo 'node --version' >> /start.sh && \
    echo 'echo "Python version:"' >> /start.sh && \
    echo 'python --version' >> /start.sh && \
    echo 'echo "Markopolis installation:"' >> /start.sh && \
    echo '. /opt/venv/bin/activate && pip show markopolis' >> /start.sh && \
    echo '. /opt/venv/bin/activate' >> /start.sh && \
    echo 'markopolis run &' >> /start.sh && \
    echo 'caddy run --config /etc/caddy/Caddyfile &' >> /start.sh && \
    echo 'cd /app/frontend && node build' >> /start.sh && \
    chmod +x /start.sh

# Start services
CMD ["/bin/sh", "-c", ". /opt/venv/bin/activate && exec /start.sh"]
