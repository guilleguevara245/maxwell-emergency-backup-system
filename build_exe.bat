@echo off
REM ============================================================
REM  Compila Maxwell a un .exe autocontenido usando Nuitka.
REM  Se ejecuta en Windows, parado en la carpeta del proyecto.
REM ============================================================

echo Instalando/actualizando Nuitka...
python -m pip install --upgrade nuitka

echo.
echo Compilando Maxwell (puede tardar varios minutos la primera vez,
echo Nuitka va a descargar un compilador de C portable si hace falta)...
echo.

python -m nuitka ^
    --onefile ^
    --assume-yes-for-downloads ^
    --windows-console-mode=force ^
    --windows-icon-from-ico=assets\maxwell_icon.ico ^
    --include-data-dir=assets=assets ^
    --output-dir=dist ^
    --output-filename=Maxwell.exe ^
    --company-name="Guillermo Guevara" ^
    --product-name="Maxwell Emergency Backup System" ^
    --file-version=1.0.0.0 ^
    --product-version=1.0.0.0 ^
    main.py

echo.
echo Listo. El ejecutable quedo en dist\Maxwell.exe
echo (ya incluye la carpeta assets adentro, no hace falta copiarla aparte)
pause
