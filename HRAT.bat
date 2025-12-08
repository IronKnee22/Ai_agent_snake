@echo off
title SNAKE AI TRENER
echo ========================================================
echo   SPOUSTIM AI TRENING...
echo   (Pri prvnim spusteni to muze chvili trvat,
echo    protoze se stahuji knihovny.)
echo ========================================================
echo.

if not exist "python312\python.exe" (
    echo [CHYBA] Nenalezen Python!
    echo Nejdriv musis spustit install.bat
    echo.
    pause
    exit /b
)

REM Spusteni hry pres UV
python312\python.exe -m uv run snake_ai.py

echo.
echo Hra skoncila.
pause