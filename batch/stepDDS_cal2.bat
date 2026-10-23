@echo off
rem Syntax: stepDDS_cal2.bat List
rem   List = the compile list the script writes (one point name per line), NOT the .lst run list.
rem Compiles every point with NewDDS2-Cooling2.0-Cal.exe and writes [point]-final.txt = reset + RAWCool + RAW[point].
rem RAWCool may be absent (deleting it is the cooling-off switch); the rest must exist.
rem Stops with exit code 1, before writing any final file, when a required part is missing
rem or a compile fails (copy a+b+c silently skips a missing source, so a final file would
rem otherwise lack that block and every later shot would be off by one trigger).
setlocal
set DDSDIR=C:\Users\Yang\Documents\Data\DDScontrol
set CALEXE=%DDSDIR%\NewDDS2-Cooling2.0-Cal.exe
if "%~1"=="" (echo Usage: stepDDS_cal2.bat List)&(exit /b 1)
if /I "%~x1"==".lst" (echo ERROR: "%~1" is the experiment run list. Pass the compile list "List".)&(exit /b 1)
if not exist "%~1" (echo ERROR: compile list "%~1" not found.)&(exit /b 1)
copy "%DDSDIR%\reset" reset
if not exist reset (echo ERROR: no reset preamble here - nothing assembled.)&(exit /b 1)
if exist RAWCool (echo RAWCool present: cooling block spliced into every final file) else (echo RAWCool absent: no cooling block)
rem (goto, not exit /b, inside the loop: an exit /b followed by more commands in a
rem  parenthesized block loses its exit code when the bat is run by cmd /c or subprocess)
for /F "usebackq tokens=1" %%i in ("%~1") do (
    if exist RAW%%i del RAW%%i
    "%CALEXE%" %%i
    if errorlevel 1 (set POINT=%%i)&(goto :compilefailed)
    if not errorlevel 0 (set POINT=%%i)&(goto :compilefailed)
    if not exist RAW%%i (set POINT=%%i)&(goto :compilefailed)
)
for /F "usebackq tokens=1" %%i in ("%~1") do copy reset+RAWCool+RAW%%i %%i-final.txt
for /F "usebackq tokens=1" %%i in ("%~1") do del RAW%%i %%i
exit /b 0
:compilefailed
echo ERROR: compiling %POINT% failed or wrote no RAW%POINT% - nothing assembled.
exit /b 1
