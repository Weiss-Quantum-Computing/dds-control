@echo off
rem Syntax: repeatDDS.bat filename number
rem Plays one final file [number] times. Stops at the first failed shot (non-zero exit of the
rem run program, e.g. a DAQmx error), as stepDDS.bat does.
setlocal
set EXEFILE="C:\Users\Yang\Documents\Data\DDScontrol\NewDDS2-Cooling2.0.exe"
if "%~2"=="" (echo Usage: repeatDDS.bat filename number)&(exit /b 1)
for /L %%i in (1,1,%2) do (
    echo Run %%i of %2
    %EXEFILE% "%~1"
    if errorlevel 1 (set RUN=%%i)&(goto :shotfailed)
    if not errorlevel 0 (set RUN=%%i)&(goto :shotfailed)
)
exit /b 0
:shotfailed
echo ERROR: the run program failed on run %RUN% of %2 - stopped here.
exit /b 1
