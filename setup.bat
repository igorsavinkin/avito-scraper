@echo off
echo ========================================
echo   Avito Parser - Setup Script
echo ========================================
echo.

echo [1/4] Creating virtual environment...
python -m venv venv
if errorlevel 1 (
    echo ERROR: Failed to create virtual environment
    pause
    exit /b 1
)
echo Done!
echo.

echo [2/4] Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment
    pause
    exit /b 1
)
echo Done!
echo.

echo [3/4] Upgrading pip...
python -m pip install --upgrade pip
if errorlevel 1 (
    echo WARNING: Failed to upgrade pip, continuing anyway...
)
echo Done!
echo.

echo [4/4] Installing dependencies...
python -m pip install selenium beautifulsoup4 webdriver-manager
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo Installing lxml (optional, may take time)...
python -m pip install lxml
if errorlevel 1 (
    echo WARNING: lxml installation failed, will use html.parser instead
)

echo.
echo ========================================
echo   Installation Complete!
echo ========================================
echo.
echo To activate the virtual environment, run:
echo   venv\Scripts\activate.bat
echo.
echo To run the parser:
echo   python main.py
echo.
pause

