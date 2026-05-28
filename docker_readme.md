# Development (override auto-loaded, runserver + live reload)

docker compose up

# Production (override ignored, gunicorn)

docker compose -f docker-compose.yml up
