@echo off
set EXEFILE="C:\Users\Yang\Documents\Data\DDScontrol\NewDDS2-Cooling2.0-RF.exe"
for /F "usebackq tokens=1" %%i in (%1) do %EXEFILE% %%i
