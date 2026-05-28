FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
# Copy the code into the container
COPY . .

# Set up the production system user, create required folders, and enforce permissions
RUN adduser --disabled-password --no-create-home appuser && \
    mkdir -p /app/media /app/staticfiles && \
    chown -R appuser:appuser /app && \
    chmod +x /app/entrypoint.sh

# Switch securely to the restricted user context
USER appuser

# Expose the internal port
EXPOSE 8000

# Fire off the entrypoint and start command
ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["gunicorn", "core.wsgi:application", "--bind", "0.0.0.0:10000"]