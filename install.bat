@echo off
setlocal

cd /d "%~dp0"

echo Installing project...

if not exist ".venv\Scripts\python.exe" (
    echo Creating virtual environment .venv...
    python -m venv .venv
    if errorlevel 1 goto error
) else (
    echo Virtual environment .venv already exists.
)

echo Activating virtual environment...
call ".venv\Scripts\activate.bat"
if errorlevel 1 goto error

echo Updating pip...
python -m pip install --upgrade pip
if errorlevel 1 goto error

echo Installing project with development dependencies...
python -m pip install -e ".[dev]"
if errorlevel 1 goto error

echo.
echo Installation is complete.
pause
exit /b 0

:error
echo.
echo Installation failed. Check the messages above.
pause
exit /b 1
