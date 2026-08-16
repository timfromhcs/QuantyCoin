@echo off
title QuantyCoin (QTY) Launcher
echo =========================================================
echo             QuantyCoin (QTY) Mainnet Launcher
echo =========================================================
if exist "src\qt\qty-qt.exe" (
    echo Starting QuantyCoin Qt GUI Wallet...
    start "" "src\qt\qty-qt.exe"
) else if exist "src\qtyd.exe" (
    echo Starting QuantyCoin Node Daemon...
    start "" "src\qtyd.exe" -upnp
) else (
    echo Binaries not found. Please build or download QuantyCoin binaries.
    pause
)
