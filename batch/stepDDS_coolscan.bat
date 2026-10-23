@echo off
rem Syntax: stepDDS_coolscan.bat List
rem   List = the compile list written by Coolscan.py, NOT the .lst run list.
rem Compiles every point (a complete cooling + detection file) with the Cal-V2 compiler and
rem writes [point]-final.txt = reset + RAW[point]. Stops with exit code 1, before writing any
rem final file, when the reset preamble is missing or a compile fails.
setlocal
set DDSDIR=C:\Users\Yang\Documents\Data\DDScontrol
set CALEXE=%DDSDIR%\NewDDS2-Cooling2.0-Cal-V2.exe
if "%~1"=="" (echo Usage: stepDDS_coolscan.bat List)&(echo   Pass the compile list "List" written by Coolscan.py, NOT the .lst run list)&(exit /b 1)
if /I "%~x1"==".lst" (echo ERROR: "%~1" is the experiment run list. Pass the compile list "List" written by Coolscan.py.)&(exit /b 1)
if not exist "%~1" (echo ERROR: compile list "%~1" not found.)&(exit /b 1)
rem In DDScontrol itself the copy below would be onto the master reset, and the script's
rem clean-up would then delete the only copy (review G2-2.1).
for %%d in ("%DDSDIR%") do set DDSFULL=%%~fd
if /I "%CD%"=="%DDSFULL%" (echo ERROR: run from a data folder below DDScontrol, not in DDScontrol itself.)&(exit /b 1)
copy "%DDSDIR%\reset" reset
if not exist reset (echo ERROR: no reset preamble here - nothing assembled.)&(exit /b 1)
rem (goto, not exit /b, inside the loop: an exit /b followed by more commands in a
rem  parenthesized block loses its exit code when the bat is run by cmd /c or subprocess)
for /F "usebackq tokens=1" %%i in ("%~1") do if "%%~xi"=="" (
    echo Compiling %%i
    if exist RAW%%i del RAW%%i
    "%CALEXE%" %%i > %%i.log
    if errorlevel 1 (set POINT=%%i)&(goto :compilefailed)
    if not errorlevel 0 (set POINT=%%i)&(goto :compilefailed)
    if not exist RAW%%i (set POINT=%%i)&(goto :compilefailed)
)
for /F "usebackq tokens=1" %%i in ("%~1") do if "%%~xi"=="" copy reset+RAW%%i %%i-final.txt > nul
for /F "usebackq tokens=1" %%i in ("%~1") do if "%%~xi"=="" del RAW%%i %%i
exit /b 0
:compilefailed
echo ERROR: compiling %POINT% failed or wrote no RAW%POINT%, see %POINT%.log - nothing assembled.
exit /b 1
