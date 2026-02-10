@echo off
echo ========================================
echo    REINICIANDO VIGAS APP
echo ========================================
echo.
echo Aguarde enquanto o aplicativo reinicia...
echo.
taskkill /F /IM python.exe /FI "WINDOWTITLE eq *vigas*" 2>nul
timeout /t 2 >nul
python vigas_app.py
