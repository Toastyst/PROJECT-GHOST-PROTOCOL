@echo off
REM Wake the Ghost Protocol Console
REM This batch file sets up the environment and launches the Ghost Console

echo 👻 Waking the Ghost Protocol...
echo.

REM Change to the YoloClanker directory (where this batch file is located)
cd /d "%~dp0"
if errorlevel 1 (
    echo ERROR: Failed to change to YoloClanker directory
    pause
    exit /b 1
)
echo Current directory: %CD%
echo.

REM Check if virtual environment exists and activate it
if exist "venv\Scripts\activate.bat" (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
    if errorlevel 1 (
        echo ERROR: Failed to activate venv
        pause
        exit /b 1
    )
) else if exist ".venv\Scripts\activate.bat" (
    echo Activating virtual environment (.venv)...
    call .venv\Scripts\activate.bat
    if errorlevel 1 (
        echo ERROR: Failed to activate .venv
        pause
        exit /b 1
    )
) else (
    echo No virtual environment found. Using system Python.
)

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found in PATH
    echo Please ensure Python is installed and in your PATH
    pause
    exit /b 1
)
echo Python found: OK
echo.

REM Set Python path to include the src directory
set PYTHONPATH=%CD%\src;%PYTHONPATH%
echo PYTHONPATH set to: %PYTHONPATH%
echo.

REM Check if requirements are installed
echo Checking dependencies...
python -c "import rich" >nul 2>&1
if errorlevel 1 (
    echo Installing requirements...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ERROR: Failed to install requirements
        pause
        exit /b 1
    )
) else (
    echo Dependencies OK
)
echo.

REM Test import before launching
echo Testing imports...
python -c "from src.ghost_protocol.core.ghost_console import main" >nul 2>&1
if errorlevel 1 (
    echo ERROR: Import test failed
    python -c "from src.ghost_protocol.core.ghost_console import main"
    pause
    exit /b 1
)
echo Import test passed
echo.

REM Launch the Ghost Console
echo 🧙‍♂️ The Ghost awakens...
echo Press Ctrl+C to exit the Ghost Console
echo.
python src\ghost_protocol\core\ghost_console.py

REM Check exit code
if errorlevel 1 (
    echo.
    echo ERROR: Ghost Console exited with error code %errorlevel%
) else (
    echo.
    echo 👻 The Ghost rests peacefully...
)

REM Deactivate virtual environment if it was activated
if defined VIRTUAL_ENV (
    call deactivate
)

echo.
pause
