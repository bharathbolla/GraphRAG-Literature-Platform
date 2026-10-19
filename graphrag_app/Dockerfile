# Multi-stage lightweight Linux container for Google Cloud Run
FROM python:3.11-slim

WORKDIR /app

# Optimize Python execution environment
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8080

# Install system utilities
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code and static assets
COPY . .

# Expose container port (Cloud Run automatically passes PORT)
EXPOSE 8080

# Start production ASGI server with Uvicorn
CMD exec uvicorn main:app --host 0.0.0.0 --port ${PORT}
