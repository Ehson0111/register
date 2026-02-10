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


# Запуск User Service
Start-Service -ServiceName "User Service" -Path "D:\django\crm\services\user-service" -Command "python manage.py runserver 0.0.0.0:8004"

Start-Service -ServiceName "calendar" -Path "D:\django\crm\services\calendar" -Command "python manage.py runserver 0.0.0.0:8006"

# Запуск Contact Service
Start-Service -ServiceName "Contact Service" -Path "D:\django\crm\services\contact_service" -Command "python manage.py runserver 0.0.0.0:8005"

Start-Service -ServiceName "Marketing" -Path "D:\django\crm\services\marketing" -Command "python manage.py runserver 0.0.0.0:8007"

Start-Service -ServiceName "docements" -Path "D:\django\crm\services\documents" -Command "python manage.py runserver 0.0.0.0:8008"
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
Write-Host "Frontend: http://localhost:3000" -ForegroundColor Cyan

