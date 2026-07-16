# PowerShell script to run FastAPI app locally for development.

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir
$BackendDir = Join-Path $ProjectRoot "backend"
$VenvDir = Join-Path $BackendDir "venv"
$ActivateScript = Join-Path $VenvDir "Scripts\Activate.ps1"

Write-Host "--------------------------------------------------------" -ForegroundColor Cyan
Write-Host "AAA - Adaptive AI FilmAura: Local Dev Startup" -ForegroundColor Cyan
Write-Host "--------------------------------------------------------" -ForegroundColor Cyan

# Verify virtual environment exists
if (-not (Test-Path $ActivateScript)) {
    Write-Error "Virtual environment activation script not found at $ActivateScript. Please ensure venv is configured."
    Exit 1
}

# Navigate to backend directory
Set-Location $BackendDir

# Ensure .env file exists
if (-not (Test-Path ".env")) {
    Write-Host "[!] .env file not found. Initializing from .env.example..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
}

# Activate venv
Write-Host "[*] Activating Python virtual environment..." -ForegroundColor Green
. $ActivateScript

# Run database migrations
Write-Host "[*] Checking and executing database migrations..." -ForegroundColor Green
try {
    alembic upgrade head
} catch {
    Write-Host "[!] Alembic migration failed. If database container is offline, this is normal." -ForegroundColor Yellow
}

# Run FastAPI server
Write-Host "[*] Starting Uvicorn reload server at http://127.0.0.1:8000..." -ForegroundColor Cyan
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
