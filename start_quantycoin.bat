@echo off
title QuantyCoin Core Suite v4.0
echo =========================================================
echo             QuantyCoin (QTY) Core Suite Launcher v4.0
echo =========================================================
if exist "dist\bin\suite\QuantyCoinSuite.exe" (
    echo Starting QuantyCoin Cyberpunk Combined Suite...
    start "" "dist\bin\suite\QuantyCoinSuite.exe"
) else if exist "dist\windows\QuantyCoinSuite.exe" (
    echo Starting QuantyCoin Cyberpunk Combined Suite...
    start "" "dist\windows\QuantyCoinSuite.exe"
) else (
    echo Launching QuantyCoin Combined Suite via Python...
    python quanty_suite_app.py
)
