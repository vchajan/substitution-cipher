@echo off
chcp 65001 > nul
setlocal

echo ===== SPUŠTĚNÍ PROJEKTU =====

if not exist ".venv\Scripts\activate.bat" (
    echo Virtuální prostředí neexistuje. Nejdříve spusťte install.bat.
    pause
    exit /b 1
)

call .venv\Scripts\activate.bat

echo Referenční text: Válka s mloky
echo Referenční matice: models\TM_ref.npy
echo Počet iterací na ciphertext: 20000
echo Paralelní zpracování: automatický počet procesů

if exist "data\reference\valka_s_mloky_raw.txt" (
    echo Používám lokální data\reference\valka_s_mloky_raw.txt.
) else (
    echo Surový referenční text chybí, stahuji jej z českých Wikizdrojů...
    python scripts\download_reference_text.py
    if errorlevel 1 (
        echo Stažení se nepodařilo a lokální raw text není k dispozici.
        echo Zkontrolujte připojení k internetu nebo doplňte data\reference\valka_s_mloky_raw.txt ručně.
        pause
        exit /b 1
    )
)

echo Připravuji referenční text...
python scripts\prepare_reference_text.py
if errorlevel 1 goto failed

echo Vytvářím referenční matici...
python scripts\build_reference_matrix.py
if errorlevel 1 goto failed

echo Spouštím testy...
pytest
if errorlevel 1 goto failed

echo Kontroluji soubory zadání...
python scripts\validate_assignment_files.py
if errorlevel 1 goto failed

echo Spouštím dávkové dešifrování...
python scripts\decrypt_samples.py --matrix models\TM_ref.npy --input-directory data\ciphertexts --output-directory outputs --iterations 20000 --restarts 1 --workers 0
if errorlevel 1 goto failed

echo Vytvářím vyhodnocení...
python scripts\evaluate_outputs.py
if errorlevel 1 goto failed

echo Hotovo.
pause
exit /b 0

:failed
echo Běh skončil chybou. Zkontrolujte zprávy výše.
pause
exit /b 1
