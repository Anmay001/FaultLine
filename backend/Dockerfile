FROM python:3.11-slim

# Install git, build essentials and system utilities
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user for secure sandbox operations
RUN groupadd -g 1000 faultline && \
    useradd -u 1000 -g faultline -m -s /bin/bash faultline

# Create sandbox directory with proper permissions
RUN mkdir -p /tmp/faultline /app/data && \
    chown -R faultline:faultline /tmp/faultline /app

WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ ./app

# Set ownership
RUN chown -R faultline:faultline /app

USER faultline

# Environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    SANDBOX_BASE_DIR=/tmp/faultline

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
