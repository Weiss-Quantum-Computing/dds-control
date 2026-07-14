@echo off
if "%~1"=="" (echo Usage: stepDDS_coolscan.bat List)&(echo   Pass the compile list "List" written by Coolscan.py, NOT the .lst run list)&(exit /b 1)
if /I "%~x1"==".lst" (echo ERROR: "%~1" is the experiment run list. Pass the compile list "List" written by Coolscan.py.)&(exit /b 1)
copy "C:\Users\Yang\Documents\Data\DDScontrol\reset" reset
for /F "usebackq tokens=1" %%i in (%1) do if "%%~xi"=="" (echo Compiling %%i & C:\Users\Yang\Documents\Data\DDScontrol\NewDDS2-Cooling2.0-Cal-V2.exe %%i > %%i.log)
for /F "usebackq tokens=1" %%i in (%1) do if "%%~xi"=="" copy reset+RAW%%i %%i-final.txt > nul
for /F "usebackq tokens=1" %%i in (%1) do if "%%~xi"=="" del RAW%%i %%i
