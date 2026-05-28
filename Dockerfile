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

# Copy supervisor config to the correct system path
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

USER appuser

EXPOSE 8000

# We use entrypoint only for handling one-time migrations/static collection on boot
ENTRYPOINT ["/app/entrypoint.sh"]

# Launch supervisor to run both Gunicorn and Celery together forever
CMD ["supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]