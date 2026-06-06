@echo off
setlocal
chcp 65001 >nul

cd /d "%~dp0"

echo Instaluji projekt...

if not exist ".venv\Scripts\python.exe" (
    echo Vytvářím virtuální prostředí .venv...
    python -m venv .venv
    if errorlevel 1 goto error
) else (
    echo Virtuální prostředí .venv už existuje.
)

echo Aktivuju virtuální prostředí...
call ".venv\Scripts\activate.bat"
if errorlevel 1 goto error

echo Aktualizuji pip...
python -m pip install --upgrade pip
if errorlevel 1 goto error

echo Instaluji projekt včetně vývojových závislostí...
python -m pip install -e ".[dev]"
if errorlevel 1 goto error

echo.
echo Instalace je hotová.
pause
exit /b 0

:error
echo.
echo Instalace selhala. Zkontrolujte zprávy výše.
pause
exit /b 1
