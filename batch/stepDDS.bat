@echo off
rem Syntax: stepDDS.bat last.lst   (the run list: one -final.txt per shot)
rem Plays every file of the run list with NewDDS2-Cooling2.0.exe. Stops at the first shot the run program
rem reports as failed (non-zero exit, e.g. a DAQmx error): the sequencer's triggers for that
rem shot would otherwise land on the next file and every later shot would be one trigger off.
setlocal
set EXEFILE="C:\Users\Yang\Documents\Data\DDScontrol\NewDDS2-Cooling2.0.exe"
if "%~1"=="" (echo Usage: stepDDS.bat last.lst)&(exit /b 1)
if not exist "%~1" (echo ERROR: run list "%~1" not found.)&(exit /b 1)
rem (goto, not exit /b, inside the loop: an exit /b followed by more commands in a
rem  parenthesized block loses its exit code when the bat is run by cmd /c or subprocess)
for /F "usebackq tokens=1" %%i in ("%~1") do (
    %EXEFILE% %%i
    if errorlevel 1 (set SHOT=%%i)&(goto :shotfailed)
    if not errorlevel 0 (set SHOT=%%i)&(goto :shotfailed)
)
exit /b 0
:shotfailed
echo ERROR: the run program failed on %SHOT% - run stopped here.
exit /b 1
