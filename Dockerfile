FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies + supervisor
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    gcc \
    supervisor \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Set up production system user and directories
RUN adduser --disabled-password --no-create-home appuser && \
    mkdir -p /app/media /app/staticfiles && \
    chown -R appuser:appuser /app && \
    chmod +x /app/entrypoint.sh

# Copy supervisor config to your writeable app directory
COPY supervisord.conf /app/supervisord.conf

USER appuser

EXPOSE 8000

ENTRYPOINT ["/app/entrypoint.sh"]

# Point directly to the app directory configuration file
CMD ["supervisord", "-c", "/app/supervisord.conf"]