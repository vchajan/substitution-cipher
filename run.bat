@echo off
setlocal
chcp 65001 >nul

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

echo.
echo Referenční matice: Krakatit
echo Restarty: 2
echo Iterace na restart: 10000
echo Celkem iterací na jeden ciphertext: 20000
echo.

echo Validating assignment files...
python scripts\validate_assignment_files.py
if errorlevel 1 goto error

if not exist "data\ciphertexts" (
    echo Ciphertext directory data\ciphertexts was not found.
    echo Create it and place assignment ciphertext files there.
)

if not exist "data\processed\TM_ref_krakatit.npy" (
    echo Krakatit reference matrix was not found.
    echo Building reference matrices...
    if exist "scripts\build_combined_reference_matrix.py" (
        python scripts\build_combined_reference_matrix.py
    ) else (
        python scripts\build_reference_matrix.py
    )
)
if errorlevel 1 goto error

echo Running tests...
pytest
if errorlevel 1 goto error

echo Running final decryption...
python scripts\decrypt_samples.py --matrix data\processed\TM_ref_krakatit.npy --iterations 10000 --restarts 2
if errorlevel 1 goto error

echo Evaluating outputs...
python scripts\evaluate_outputs.py
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
