@echo off
REM Wake the Ghost Protocol Console
REM This batch file sets up the environment and launches the Ghost Console

echo 👻 Waking the Ghost Protocol...
echo.

REM Change to the YoloClanker directory (where this batch file is located)
cd /d "%~dp0"

REM Check if virtual environment exists and activate it
if exist "venv\Scripts\activate.bat" (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
) else if exist ".venv\Scripts\activate.bat" (
    echo Activating virtual environment (.venv)...
    call .venv\Scripts\activate.bat
) else (
    echo No virtual environment found. Using system Python.
)

REM Set Python path to include the src directory
set PYTHONPATH=%CD%\src;%PYTHONPATH%

REM Check if requirements are installed
python -c "import rich" >nul 2>&1
if errorlevel 1 (
    echo Installing requirements...
    pip install -r requirements.txt
)

REM Launch the Ghost Console
echo.
echo 🧙‍♂️ The Ghost awakens...
echo.
python src\ghost_protocol\core\ghost_console.py

REM Deactivate virtual environment if it was activated
if defined VIRTUAL_ENV (
    call deactivate
)

echo.
echo 👻 The Ghost rests...
pause