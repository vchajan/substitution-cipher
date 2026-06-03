@echo off
setlocal

cd /d "%~dp0"

if not exist ".venv\Scripts\activate.bat" (
    echo Virtual environment .venv was not found.
    echo Please run install.bat first.
    pause
    exit /b 1
)

echo Activating virtual environment...
call ".venv\Scripts\activate.bat"
if errorlevel 1 goto error

echo Building reference matrix...
python scripts\build_reference_matrix.py
if errorlevel 1 goto error

echo Running tests...
pytest
if errorlevel 1 goto error

echo Running final decryption with 20000 iterations...
python scripts\decrypt_samples.py --iterations 20000
if errorlevel 1 goto error

echo.
echo Run is complete.
echo If no ciphertext files are available, the message above is expected.
pause
exit /b 0

:error
echo.
echo Run failed. Check the messages above.
pause
exit /b 1
