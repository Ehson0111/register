param(
    [string]$BridgeSecret = "crm-onec-bridge-secret-2026",
    [string]$OnecBaseUrl = "http://127.0.0.1/1c/odata/standard.odata/",
    [string]$OnecUsername = "",
    [string]$OnecPassword = "",
    [string]$HealthcheckPath = '$metadata',
    [string]$UseHealthcheck = "false",
    [double]$RestartSettleSeconds = 1.0,
    [int]$LimitRetryAttempts = 3,
    [double]$LimitRetryDelaySeconds = 1.5,
    [string]$AppPoolName = "",
    [string]$RestartCommand = "",
    [string]$ProcessName = "w3wp",
    [string]$BridgeHost = "0.0.0.0",
    [int]$Port = 8013
)

function Convert-ToBooleanString {
    param([string]$Value)

    if ($null -eq $Value) {
        $Value = ""
    }
    $normalized = $Value.Trim().ToLowerInvariant()
    if ($normalized -in @("1", "true", "yes", "y", "on")) {
        return "true"
    }
    if ($normalized -in @("0", "false", "no", "n", "off", "")) {
        return "false"
    }
    throw "Invalid boolean value '$Value'. Use true/false or 1/0."
}

$useHealthcheckValue = Convert-ToBooleanString -Value $UseHealthcheck

$env:ONEC_BRIDGE_SECRET = $BridgeSecret
$env:ONEC_BASE_URL = $OnecBaseUrl
$env:ONEC_USERNAME = $OnecUsername
$env:ONEC_PASSWORD = $OnecPassword
$env:ONEC_HEALTHCHECK_PATH = $HealthcheckPath
$env:ONEC_USE_HEALTHCHECK = $useHealthcheckValue
$env:ONEC_RESTART_SETTLE_SECONDS = "$RestartSettleSeconds"
$env:ONEC_LIMIT_RETRY_ATTEMPTS = "$LimitRetryAttempts"
$env:ONEC_LIMIT_RETRY_DELAY_SECONDS = "$LimitRetryDelaySeconds"
$env:ONEC_APP_POOL_NAME = $AppPoolName
$env:ONEC_RESTART_COMMAND = $RestartCommand
$env:ONEC_PROCESS_NAME = $ProcessName
$env:ONEC_BRIDGE_HOST = $BridgeHost
$env:ONEC_BRIDGE_PORT = "$Port"

Write-Host "Starting 1C bridge on $BridgeHost`:$Port" -ForegroundColor Green
Write-Host "1C OData URL: $OnecBaseUrl" -ForegroundColor Cyan
Write-Host "Healthcheck enabled: $useHealthcheckValue" -ForegroundColor Cyan
if ($AppPoolName) {
    Write-Host "Restart mode: app pool '$AppPoolName'" -ForegroundColor Yellow
} elseif ($RestartCommand) {
    Write-Host "Restart mode: custom command" -ForegroundColor Yellow
} else {
    Write-Host "Restart mode: process '$ProcessName'" -ForegroundColor Yellow
}

python server.py
