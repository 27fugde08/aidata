# AIOS Universal App Dockerfile
# Builds a specific app from the 'apps/' directory as an independent service.
# Usage: docker build -f Dockerfile.app --build-arg APP_NAME=douyin_automation -t aios-douyin .

FROM python:3.10-slim

ARG APP_NAME
ENV APP_NAME=${APP_NAME}
ENV PYTHONPATH=/app

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    libsm6 \
    libxext6 \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy only the specific app's requirements first (for caching)
COPY apps/${APP_NAME}/requirements.txt /app/apps/${APP_NAME}/requirements.txt
RUN if [ -f /app/apps/${APP_NAME}/requirements.txt ]; then \
        pip install --no-cache-dir -r /app/apps/${APP_NAME}/requirements.txt; \
    fi

# Install common dependencies if needed (e.g., uvicorn, fastapi)
RUN pip install --no-cache-dir uvicorn fastapi

# Copy the specific app source code
# We copy it to /app/apps/<app_name> to preserve the import structure 'from apps.xxx import ...'
COPY apps/${APP_NAME} /app/apps/${APP_NAME}

# Create a simple entrypoint script that navigates to the app and runs it
RUN echo "#!/bin/sh\ncd /app/apps/${APP_NAME}\nuvicorn main:app --host 0.0.0.0 --port 8000" > /start.sh && chmod +x /start.sh

CMD ["/start.sh"]
