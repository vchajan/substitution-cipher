@echo off
setlocal
chcp 65001 >nul

cd /d "%~dp0"

if not exist ".venv\Scripts\activate.bat" (
    echo Virtuální prostředí .venv nebylo nalezeno.
    echo Nejdříve spusťte install.bat.
    pause
    exit /b 1
)

echo Aktivuju virtuální prostředí...
call ".venv\Scripts\activate.bat"
if errorlevel 1 goto error

echo.
echo Referenční matice: Krakatit
echo Restarty: 2
echo Iterace na restart: 10000
echo Celkem iterací na jeden ciphertext: 20000
echo.

echo Kontroluji vstupní a výstupní soubory...
python scripts\validate_assignment_files.py
if errorlevel 1 goto error

if not exist "data\ciphertexts" (
    echo Složka data\ciphertexts nebyla nalezena.
    echo Vytvořte ji a vložte do ní ciphertexty ze zadání.
)

if not exist "data\processed\TM_ref_krakatit.npy" (
    echo Referenční matice z Krakatitu nebyla nalezena.
    echo Vytvářím referenční matice...
    if exist "scripts\build_combined_reference_matrix.py" (
        python scripts\build_combined_reference_matrix.py
    ) else (
        python scripts\build_reference_matrix.py
    )
)
if errorlevel 1 goto error

echo Spouštím testy...
pytest
if errorlevel 1 goto error

echo Spouštím finální dešifrování...
python scripts\decrypt_samples.py --matrix data\processed\TM_ref_krakatit.npy --iterations 10000 --restarts 2
if errorlevel 1 goto error

echo Vyhodnocuji výstupy...
python scripts\evaluate_outputs.py
if errorlevel 1 goto error

echo.
echo Běh je hotový.
echo Pokud nejsou k dispozici žádné ciphertexty, je předchozí hláška v pořádku.
pause
exit /b 0

:error
echo.
echo Běh selhal. Zkontrolujte zprávy výše.
pause
exit /b 1
