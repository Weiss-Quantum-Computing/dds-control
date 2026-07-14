@echo off
copy "C:\Users\Yang\Documents\Data\DDScontrol\reset" reset
for /F "usebackq tokens=1" %%i in (%1) do C:\Users\Yang\Documents\Data\DDScontrol\NewDDS2-Cooling2.0-Cal-V2.exe %%i
for /F "usebackq tokens=1" %%i in (%1) do copy reset+RAW%%i %%i-final.txt
for /F "usebackq tokens=1" %%i in (%1) do del RAW%%i %%i 
rem for /F "usebackq tokens=1" %%i in (%1) do del RAW%%i  