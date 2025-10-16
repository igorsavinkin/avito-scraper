Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Avito Parser - Setup Script" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "[1/4] Creating virtual environment..." -ForegroundColor Green
python -m venv venv
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to create virtual environment" -ForegroundColor Red
    Read-Host -Prompt "Press Enter to exit"
    exit 1
}
Write-Host "Done!" -ForegroundColor Green
Write-Host ""

Write-Host "[2/4] Activating virtual environment..." -ForegroundColor Green
& .\venv\Scripts\Activate.ps1
Write-Host "Done!" -ForegroundColor Green
Write-Host ""

Write-Host "[3/4] Upgrading pip..." -ForegroundColor Green
python -m pip install --upgrade pip
if ($LASTEXITCODE -ne 0) {
    Write-Host "WARNING: Failed to upgrade pip, continuing anyway..." -ForegroundColor Yellow
}
Write-Host "Done!" -ForegroundColor Green
Write-Host ""

Write-Host "[4/4] Installing dependencies..." -ForegroundColor Green
python -m pip install selenium beautifulsoup4 webdriver-manager
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to install dependencies" -ForegroundColor Red
    Read-Host -Prompt "Press Enter to exit"
    exit 1
}

Write-Host ""
Write-Host "Installing lxml (optional, may take time)..." -ForegroundColor Green
python -m pip install lxml
if ($LASTEXITCODE -ne 0) {
    Write-Host "WARNING: lxml installation failed, will use html.parser instead" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Installation Complete!" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "To activate the virtual environment, run:" -ForegroundColor Yellow
Write-Host "  .\venv\Scripts\Activate.ps1" -ForegroundColor White
Write-Host ""
Write-Host "To run the parser:" -ForegroundColor Yellow
Write-Host "  python main.py" -ForegroundColor White
Write-Host ""

Read-Host -Prompt "Press Enter to continue"

