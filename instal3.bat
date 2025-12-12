@echo off
set VC=vc_redist.x64.exe

echo === 1) Stahuji oficialni Microsoft VC++ Redistributable ===
curl -L https://aka.ms/vs/17/release/vc_redist.x64.exe -o %VC%

echo === 2) Extrahuji instalator jako archiv ===
mkdir vcredist_extracted
expand %VC% -F:* vcredist_extracted >nul

echo === 3) Hledam CAB archivy ===
cd vcredist_extracted

for %%f in (*.cab) do (
    echo Rozbaluji %%f ...
    expand "%%f" -F:* ..\dll_output >nul
)

cd ..

echo === 4) Kopiruji potrebne DLL do Pythonu ===
set DST=python312

for %%d in (dll_output\*.dll) do (
    echo Kopiruji %%~nxd ...
    copy "%%d" "%DST%" >nul
)

echo Hotovo!
echo DLL jsou v python312\ a nepotrebuje to admina.
pause
