param([switch]$BackendOnly, [switch]$FrontendOnly)
$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path $PSScriptRoot -Parent
$backendPath = Join-Path $projectRoot 'backend'
$pythonPath = Join-Path $backendPath '.venv/Scripts/python.exe'
if (-not $FrontendOnly) {
    if (-not (Test-Path -LiteralPath $pythonPath)) {
        throw 'Crie backend/.venv e instale backend/requirements-dev.txt. Consulte docs/PRISMA_RUNBOOK.md.'
    }
    Push-Location $backendPath
    try {
        & $pythonPath -m alembic upgrade head
        if ($LASTEXITCODE -ne 0) { throw 'Migração não concluída.' }
        & $pythonPath -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
    } finally { Pop-Location }
}
if ($FrontendOnly) {
    Push-Location (Join-Path $projectRoot 'frontend')
    try { npm run dev } finally { Pop-Location }
}
