# Быстрая сборка: сначала django-base, затем остальные сервисы (без pull с Docker Hub)
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $Root

$env:DOCKER_BUILDKIT = "1"
$env:COMPOSE_DOCKER_CLI_BUILD = "1"

Write-Host "==> [1/2] Building django-base (pip once)..." -ForegroundColor Cyan
docker compose build django-base
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

$apps = @(
  "user-service", "contact-service", "calendar", "marketing", "documents",
  "applications", "chat-service", "payments", "api-gateway", "tgbots", "frontend"
)

Write-Host "==> [2/2] Building application services..." -ForegroundColor Cyan
docker compose build @apps
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host "Done. Run: docker compose up" -ForegroundColor Green
