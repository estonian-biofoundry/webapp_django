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

COPY . .

RUN adduser --disabled-password --no-create-home appuser && \
    mkdir -p /app/media /app/staticfiles && \
    chown -R appuser:appuser /app

USER appuser

EXPOSE 8000

# Tell the container to execute your entrypoint script first
ENTRYPOINT ["/app/entrypoint.sh"]

# Tell the container the main production command to boot Django via Gunicorn
CMD ["gunicorn", "core.wsgi:application", "--bind", "0.0.0.0:10000"]