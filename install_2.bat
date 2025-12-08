@echo off
setlocal

echo ============================================
echo   INSTALATOR: Python + UV + C++ Knihovny
echo ============================================
echo.

set PYTHON_ZIP=python-3.12.0-embed-amd64.zip
set PY_URL=https://www.python.org/ftp/python/3.12.0/%PYTHON_ZIP%
set GETPIP_URL=https://bootstrap.pypa.io/get-pip.py
set VCREDIST_URL=https://aka.ms/vs/17/release/vc_redist.x64.exe

echo === KROK 0: Kontrola a instalace Visual C++ Redistributable ===
echo (Nutne pro fungovani AI mozku - PyTorch)
echo Stahuji vc_redist.x64.exe...
curl -L %VCREDIST_URL% -o vc_redist.x64.exe

if %errorlevel% neq 0 (
    echo [VAROVANI] Nepodarilo se stahnout C++ knihovny.
    echo Zkusime pokracovat, ale muze to spadnout.
) else (
    echo Instaluji C++ knihovny...
    echo (Vyskoci okno, nic nedelejte, instalace je automaticka)
    REM /install /passive /norestart zajisti, ze to probiha tise
    vc_redist.x64.exe /install /passive /norestart
    
    echo C++ knihovny nainstalovany.
    del vc_redist.x64.exe
)

echo.
echo === KROK 1: Stahuji portable Python 3.12 ===
if not exist "python312" (
    curl -L %PY_URL% -o %PYTHON_ZIP%
    echo Rozbaluji Python...
    mkdir python312 >nul 2>&1
    tar -xf %PYTHON_ZIP% -C python312
    
    echo Povoluji nacitani site-packages...
    echo import site>>python312\python312._pth
    del %PYTHON_ZIP%
) else (
    echo Python uz je stazeny. Preskakuji.
)

echo.
echo === KROK 2: Instalace nastroju (UV) ===
curl -L %GETPIP_URL% -o get-pip.py
python312\python.exe get-pip.py
python312\python.exe -m pip install uv
del get-pip.py

echo.
echo ============================================
echo   HOTOVO! Pripraveno.
echo   Nyni spustte soubor HRAT.bat
echo ============================================
echo.
pause