@echo off
title QuantyCoin Core Suite v3.0
echo =========================================================
echo             QuantyCoin (QTY) Core Suite Launcher v3.0
echo =========================================================
if exist "dist\bin\suite\QuantyCoinSuite.exe" (
    echo Starting QuantyCoin Cyberpunk Combined Suite...
    start "" "dist\bin\suite\QuantyCoinSuite.exe"
) else (
    echo Launching QuantyCoin Combined Suite via Python...
    python -m ui.suite_gui
)
