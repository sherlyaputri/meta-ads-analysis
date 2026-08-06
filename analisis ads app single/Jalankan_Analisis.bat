@echo off
echo ========================================================
echo MEMULAI ANALISIS META ADS WAHANA EXPRESS
echo ========================================================
echo.

cd /d "C:\Users\Wahana Express\Documents\wahana\Analisis ads"
"%LOCALAPPDATA%\Programs\Python\Python312\python.exe" analysis_fixed.py

echo.
echo ========================================================
echo Analisis Selesai! Silakan cek folder 'analysis_output'
echo ========================================================
pause
