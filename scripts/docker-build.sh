#!/usr/bin/env sh
set -e
cd "$(dirname "$0")/.."

export DOCKER_BUILDKIT=1
export COMPOSE_DOCKER_CLI_BUILD=1

echo "==> [1/2] Building django-base (pip once)..."
docker compose build django-base

echo "==> [2/2] Building application services..."
docker compose build \
  user-service contact-service calendar marketing documents \
  applications chat-service payments api-gateway tgbots frontend

echo "Done. Run: docker compose up"
