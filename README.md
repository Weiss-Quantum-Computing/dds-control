# DDS Control

Control software for a homemade Direct Digital Synthesis (DDS) source that
drives the microwave and RF pulse sequences of a cesium-133 atomic-physics
experiment (laser-cooled atoms in an optical lattice, hyperfine-manifold
addressing via an AD9852 DDS through a National Instruments PCIe-6536 digital
I/O card).

The suite spans three layers:

1. **Python pulse-sequence generators** (`scripts/`) compute frequencies,
   timings, and powers for each experiment and write plain-text pulse
   definition files.
2. **C++ pulse compilers** (`firmware/`, the `*-Cal*` projects) expand each
   pulse row into the raw 32-bit AD9852 register word stream (`RAW*` files).
3. **A C++ run program** (`firmware/NewDDS2-Cooling2.0`) loads a compiled
   sequence into the PCIe-6536 FIFO and plays it out under external triggers.

Windows batch files (`batch/`) glue these together, concatenating a reset
preamble, a cooling block, and per-point detection pulses into the final
files that get run.

## How a scan runs

```
Freqscan.py (etc.)                       # writes point pulse files + Cool/Gate
      │  calls
      ▼
NewDDS2-Cooling2.0-Cal-V2.exe <file>     # compiles each file -> RAW<file>
      │  stepDDS_*.bat concatenates
      ▼
reset + RAWCool + RAWGate + RAW<point>   ->  <point>-final.txt
      │  stepDDS.bat last.lst
      ▼
NewDDS2-Cooling2.0.exe <final>           # loads FIFO, waits for triggers
      │
      ▼
PCIe-6536  ->  AD9852 DDS  ->  microwave / RF chain  ->  atoms
```

Each pulse block ends with a self-timing mask that gates the FIFO update clock,
so every pulse plays only when the experiment's sequencer (Supertime) sends its
trigger. Trigger N plays pulse N in FIFO order.

## Repository layout

```
firmware/                       C++ sources (built with MinGW GCC via Eclipse CDT)
  NewDDS2-Cooling2.0/           run program: loads a final file into the DAQ FIFO
  NewDDS2-Cooling2.0-Cal/       pulse compiler (microwave)
  NewDDS2-Cooling2.0-Cal-V2/    pulse compiler + extra pulse types (12-17)
  NewDDS2-Cooling2.0-RF/        RF-channel variant
  legacy/                       earlier generations, for reference only - DO NOT BUILD:
                                most call IO() and play on the DAQ card directly, with the
                                2010-11 power tables (POWMAX 0.745 W) and, in version-3.0,
                                a 100 kHz FIFO clock; their Eclipse names are legacy-<folder>
                                so they cannot build a NewDDS2*.exe
scripts/                        Python pulse-sequence generators
  hardware/                     picomotor / serial-port helpers (ldcnlib, etc.)
  legacy/                       older cooling_control.py generation
batch/                          Windows orchestration (.bat) + binary reset preamble
docs/                           programming guide, manual, setup drawing
```

## Prerequisites

- **NI-DAQmx** (ANSI C Dev) — `NIDAQmx.h` / `NIDAQmx.lib`, from National
  Instruments. Required to build any firmware project. Not redistributed here.
- **MinGW GCC + Eclipse CDT** — the projects are managed-build Eclipse CDT
  projects targeting MinGW. `.project` / `.cproject` are included.
- **Python 2.7** with **numpy**, **scipy**, and **pyserial** — the generator
  scripts are Python 2 (print statements, `xrange`).
- **Ldcnlib.dll** (LDCN / New Focus picomotor library) — needed only by the
  `scripts/hardware/` picomotor tools. Download from the vendor; not
  redistributed here.
- **libxl** (optional) — only for the disabled `USE_EXCEL` path in
  `getpulse.cpp`; the default text-file build does not need it. See the
  `LIBXL_HEADERS_REMOVED.txt` notes in the affected firmware folders.

## Building the firmware (Eclipse)

Import a project, select the **Release** build configuration, then
Project → Clean → Build. Every current project's Eclipse name (`.project`) is its
folder name, and the `.cproject` files build `${ProjName}.exe`, so each builds to
`<folder>.exe` and needs no rename. (Until Oct 2026 the run program and the Cal
compiler were both named `NewDDS2` and both built `NewDDS2.exe`: copying the wrong
one to `NewDDS2-Cooling2.0.exe` would make `stepDDS.bat` compile every final file
instead of playing it, and `fc /b` would not notice. If a workspace still has the
old `NewDDS2` entries, remove them from the workspace (not from disk) and
re-import the folders.)

After building, verify a new compiler produces byte-identical output to the one
it replaces by running both on the same input and comparing the `RAW` files
(`fc /b`), before deploying anything that drives hardware.

## Notes

- The `*-Cal*` compilers here include a performance fix that builds the pulse
  train in O(total length) instead of O(n²) in pulse count, making long
  cooling sequences (and per-point cooling scans) practical to compile.
- `FIFOCLOCK` in `DDSconstants.h` (the DDS update-clock rate) must match the
  hardware; both current compilers are set to 1 MHz.
- **Paths are lab-specific.** The batch files and some scripts contain absolute
  paths (`C:\Users\Yang\Documents\Data\DDScontrol\...`) matching the original
  lab machine. Adjust these for any other installation.
- The Python scripts embed hand-tuned, dated calibration constants (transition
  frequencies, pulse powers) specific to the apparatus on the day they were
  used; treat them as starting points, not universal values.
