# Checks of the pulse compiler off the lab PC

`mac_check.py` builds `firmware/NewDDS2-Cooling2.0-Cal-V2` on a Mac and checks it; its docstring
says what and how. `stubs/` holds stand-ins for `windows.h`, `dos.h`, `conio.h` and `NIDAQmx.h`:
the compiler only reads a pulse file and writes a RAW file, it never calls the card.

    python3 firmware/tests/mac_check.py --lab "<Data>/DDS Control/20261117" --gui "<Freq-Scan-GUI>"

Needs clang++ and Rosetta (the build is x86_64 on purpose). This checks the source. The exe the lab
runs is built with MinGW on Windows: after a rebuild there, compare its RAW output with the
previous exe's on the same pulse file (`fc /b`) before using it.
