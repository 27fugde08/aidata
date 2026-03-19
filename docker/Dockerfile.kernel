# AIOS Kernel Dockerfile (2025 Production Ready)
# Stage 1: Runtime Base
FROM python:3.10-slim as base

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app:/app/core_kernel/src

# Install system dependencies for Video Processing & OpenCV
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    libsm6 \
    libxext6 \
    libgl1-mesa-glx \
    libglib2.0-0 \
    build-essential \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Stage 2: Dependencies
FROM base as builder
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Stage 3: Final Image
FROM builder
# Copy the entire project
COPY . .

# Ensure storage directories exist
RUN mkdir -p storage/db storage/logs storage/outputs storage/temp logs

# Expose the API port
EXPOSE 8000

# Command to run the application using manage.py
# Using --host 0.0.0.0 to allow external connections from Docker bridge
CMD ["python", "manage.py", "runserver", "--host", "0.0.0.0", "--port", "8000", "--no-reload"]
