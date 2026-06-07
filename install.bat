@echo off
chcp 65001 > nul
setlocal

echo ===== INSTALACE PROJEKTU =====

python --version > nul 2>&1
if errorlevel 1 (
    echo Python není dostupný. Nainstalujte Python 3.10 nebo novější.
    pause
    exit /b 1
)

if not exist ".venv" (
    echo Vytvářím virtuální prostředí .venv...
    python -m venv .venv
) else (
    echo Virtuální prostředí .venv už existuje.
)

call .venv\Scripts\activate.bat

echo Aktualizuji pip...
python -m pip install --upgrade pip

echo Instaluji projekt včetně vývojových závislostí...
python -m pip install -e ".[dev]"
if errorlevel 1 (
    echo Instalace selhala. Zkontrolujte zprávy výše.
    pause
    exit /b 1
)

echo Instalace je hotová.
pause
