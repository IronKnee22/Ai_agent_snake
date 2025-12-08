@echo off
setlocal

echo ============================================
echo   INSTALATOR PORTABLE PYTHON + UV
echo   Funguje na Windows bez admin prav
echo ============================================
echo.

set PYTHON_ZIP=python-3.12.0-embed-amd64.zip
set PY_URL=https://www.python.org/ftp/python/3.12.0/%PYTHON_ZIP%
set GETPIP_URL=https://bootstrap.pypa.io/get-pip.py

echo === KROK 1: Stahuji portable Python 3.12 ===
curl -L %PY_URL% -o %PYTHON_ZIP%
if %errorlevel% neq 0 (
    echo CHYBA: Nepodarilo se stahnout Python.
    pause
    exit /b
)

echo === KROK 2: Rozbaluji Python ===
mkdir python312 >nul 2>&1
tar -xf %PYTHON_ZIP% -C python312

echo === KROK 3: Povoluji nacitani site-packages ===
echo import site>>python312\python312._pth

echo === KROK 4: Stahuji get-pip.py ===
curl -L %GETPIP_URL% -o get-pip.py
if %errorlevel% neq 0 (
    echo CHYBA: Nepodarilo se stahnout get-pip.py.
    pause
    exit /b
)

echo === KROK 5: Instalace pip pomoci get-pip.py ===
python312\python.exe get-pip.py
if %errorlevel% neq 0 (
    echo CHYBA: get-pip selhalo.
    pause
    exit /b
)

echo === KROK 6: Instalace UV ===
python312\python.exe -m pip install uv
if %errorlevel% neq 0 (
    echo CHYBA: Balicek uv nejde nainstalovat.
    pause
    exit /b
)

REM Úklid stazenych souboru
del %PYTHON_ZIP%
del get-pip.py

echo.
echo ============================================
echo   HOTOVO! Pripraveno.
echo   Nyni spustte soubor HRAT.bat
echo ============================================
echo.
pause