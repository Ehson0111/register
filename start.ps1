# start-all.ps1
Write-Host "Запуск всех микросервисов..." -ForegroundColor Green

# Функция для запуска команд в новых окнах PowerShell
function Start-Service {
    param(
        [string]$ServiceName,
        [string]$Path,
        [string]$Command
    )
    
    Write-Host "Запуск $ServiceName..." -ForegroundColor Yellow
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$Path'; $Command"
    Start-Sleep 2
}

# Запуск API Gateway
Start-Service -ServiceName "API Gateway" -Path "D:\django\crm\api-gateway" -Command "python manage.py runserver"

Start-Service -ServiceName "1C Bridge" -Path "D:\django\crm\services\onec_bridge" -Command "powershell -ExecutionPolicy Bypass -File .\start.ps1 -BridgeSecret 'crm-onec-bridge-secret-2026' -OnecBaseUrl 'http://127.0.0.1/1c/odata/standard.odata/' -OnecUsername '$env:ONEC_USERNAME' -OnecPassword '$env:ONEC_PASSWORD' -AppPoolName '$env:ONEC_APP_POOL_NAME' -RestartCommand '$env:ONEC_RESTART_COMMAND' -ProcessName 'w3wp' -BridgeHost '0.0.0.0'"


# Запуск User Service
Start-Service -ServiceName "User Service" -Path "D:\django\crm\services\user-service" -Command "python manage.py runserver 0.0.0.0:8004"

Start-Service -ServiceName "calendar" -Path "D:\django\crm\services\calendar" -Command "python manage.py runserver 0.0.0.0:8006"

# Запуск Contact Service
Start-Service -ServiceName "Contact Service" -Path "D:\django\crm\services\contact_service" -Command "python manage.py runserver 0.0.0.0:8005"

Start-Service -ServiceName "Marketing" -Path "D:\django\crm\services\marketing" -Command "python manage.py runserver 0.0.0.0:8007"

Start-Service -ServiceName "docements" -Path "D:\django\crm\services\documents" -Command "python manage.py runserver 0.0.0.0:8008"
Start-Service -ServiceName "payments" -Path "D:\django\crm\services\payments" -Command "$env:ONEC_TRANSPORT_MODE='bridge'; $env:ONEC_ODATA_BASE_URL='http://host.docker.internal/1c/odata/standard.odata/'; $env:ONEC_BRIDGE_URL='http://host.docker.internal:8013/invoke'; $env:ONEC_BRIDGE_SECRET='crm-onec-bridge-secret-2026'; python manage.py runserver 0.0.0.0:8012"
Start-Service -ServiceName "payments-retry-worker" -Path "D:\django\crm\services\payments" -Command "$env:ONEC_TRANSPORT_MODE='bridge'; $env:ONEC_ODATA_BASE_URL='http://host.docker.internal/1c/odata/standard.odata/'; $env:ONEC_BRIDGE_URL='http://host.docker.internal:8013/invoke'; $env:ONEC_BRIDGE_SECRET='crm-onec-bridge-secret-2026'; python manage.py process_invoice_retries --loop"
# Ждем немного перед запуском фронтенда 
Start-Sleep 5

# Запуск Vue.js фронтенда
Start-Service -ServiceName "Vue Frontend" -Path "D:\django\crm\frontend\vue-project" -Command "npm run dev"

Write-Host "Все сервисы запускаются..." -ForegroundColor Green
Write-Host "API Gateway: http://localhost:8000" -ForegroundColor Cyan
Write-Host "User Service: http://localhost:8004" -ForegroundColor Cyan
Write-Host "Contact Service: http://localhost:8005" -ForegroundColor Cyan
Write-Host "Calendar: http://localhost:8006" -ForegroundColor Cyan
Write-Host "marketing: http://localhost:8007" -ForegroundColor Cyan
Write-Host "docements: http://localhost:8008" -ForegroundColor Cyan
Write-Host "payments: http://localhost:8012" -ForegroundColor Cyan
Write-Host "1C Bridge: http://127.0.0.1:8013" -ForegroundColor Cyan
Write-Host "Frontend: http://localhost:3000" -ForegroundColor Cyan
 