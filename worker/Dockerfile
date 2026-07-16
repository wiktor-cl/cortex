FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml ./
COPY worker ./worker

RUN pip install --no-cache-dir .

ENV PYTHONUNBUFFERED=1

# Two processes share this image (see infra/docker-compose.yml):
#   worker-watcher -> python -m worker.watcher_main
#   worker-rq      -> rq worker ingestion --url redis://redis:6379/0
# No default CMD: the compose file picks one per service so a single image serves both roles.
