@echo off
title QuantyCoin Core Suite QTY2 (Native Qt6 Desktop)
echo =========================================================
echo       QuantyCoin (QTY2) Native Desktop Suite Launcher
echo =========================================================
if exist "dist\bin\suite\QuantyCoinSuite.exe" (
    echo Starting QuantyCoin Native Desktop Suite...
    start "" "dist\bin\suite\QuantyCoinSuite.exe"
) else if exist "dist\windows\QuantyCoinSuite.exe" (
    echo Starting QuantyCoin Native Desktop Suite...
    start "" "dist\windows\QuantyCoinSuite.exe"
) else (
    echo Launching QuantyCoin Native Master Suite via Python...
    python quanty_suite_app.py
)
