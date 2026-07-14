@echo off
rem Syntax: repeatDDS.bat filename number
set EXEFILE="C:\Users\Yang\Documents\Data\DDScontrol\NewDDS2-Cooling2.0.exe"
for /L %%i in (1,1,%2) do (echo Run %%i of %2)&&(%EXEFILE% %1)
