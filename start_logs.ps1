$containers = docker ps --format "{{.Names}}" | Where-Object {$_ -notlike "*minio*" -and $_ -notlike "*mailhog*"}

foreach ($container in $containers) {
    Start-Process PowerShell -ArgumentList "-NoExit", "docker logs -f $container"
    Start-Sleep -Milliseconds 300
}

Write-Host "Открыто $($containers.Count) окон с логами контейнеров" -ForegroundColor Green