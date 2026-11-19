# DDS Control

> **Status (2026-11-02): the scan scripts and the batch files are deprecated.**
> The lab now runs its DDS scans from the DDS control GUI
> ([Freq-Scan-GUI](https://github.com/Weiss-Quantum-Computing/Freq-Scan-GUI)),
> which writes, compiles, assembles and plays the pulse files itself. Those
> parts get no further updates here; make changes in the GUI instead.
>
> | Part | Status |
> |---|---|
> | `scripts/` Freqscan, Freqscan2, Freqscan-RF, Powerscan, Powerscan-RF, Phasescan, Phasescan-RF, Rabi, Rabi-RF, Coolscan, Cool_Cal | **deprecated** - replaced by the GUI's Freq / Power / Phase / Cooling scan panels |
> | `batch/*.bat` (stepDDS*, repeatDDS) | **deprecated** - the GUI assembles the final files and plays the run list itself |
> | `scripts/legacy/`, `firmware/legacy/` | reference only (unchanged) |
> | `firmware/NewDDS2-Cooling2.0-Cal-V2` (the pulse compiler) and `firmware/NewDDS2-Cooling2.0` / `-RF` (the run programs) | **still used** - the GUI runs these three exes; compiler fixes still belong here |
> | `firmware/NewDDS2-Cooling2.0-Cal` | **still used** by the scripts below |
> | `batch/reset` (the 16-word DDS reset preamble) | **still used** - the GUI starts every final file with it |
> | `scripts/` DDSaddress, DDSarb, DDScool, DDSpostcool, `scripts/hardware/AddressingSearch.py` | **still used** - they make the DDSaddress.txt / DDSarb.txt / DDSarbPartition.txt / DDScool*.txt pulse files CameraGui's addressing, arbitrary-pulse and cooling modes read; the GUI has no replacement for them yet |
>
> Every fix of the deprecated scripts that the GUI needs is in the GUI (audited
> 2026-11-02, the last one being the RF power flattening of `rf_Power_Calib`).
> `Daily2.py` (Daily-file-creation) no longer seeds the day folders with the
> scripts unless `SeedDDSScripts = 1`.

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
docs/                           programming guide, manual, setup drawing, LO synthesizer docs
```

`docs/uWaveSetup.png` is the original microwave chain. It shows an MVSR-9316 LO at
9.142625 GHz; the current LO is a Micro Lambda MLVS-2009AS (base model MLVS-0520AS)
at 9.1326249676 GHz (`FMIX`). The MLVS documents are:

- `MLVS-2009AS_spec.pdf` - the as-ordered spec sheet. External 10 MHz reference
  input level is 0 dBm ±6 dB (50 Ω), and RF output is +15 dBm minimum (not levelled).
- `MLVS-0520_datasheet.pdf` - the base-model datasheet (phase noise, options).
- `MLVS_outline_99-0101-001H.pdf` - outline drawing and pinout. J4 is REF OUT, J5 is
  REF IN, J6 is RF OUT; J1 pins 6 and 13 are the REF LOCK and RF LOCK status lines.

`docs/uWaveChain_2026-11-13.svg` is the microwave chain as built on 13 Nov 2026, the
current reference in place of `uWaveSetup.png`. It shows the power (dBm and Vpp) at
every point for the uW DDS at full scale (5.187) and for the BK 4063B AWG at 5 Vpp,
with each part's damage limit or 1 dB compression point. The AWG path is: BLK-89-S+
DC block, 29 dB pad, ZYSWA-2-50DR gated by Supertime, ZSWA-4-30DR held off while the
uW DDS self-timing is high, then ZX60-P103LN+, into the coupled port of a reversed
10 dB directional coupler ahead of the monitor coupler. Values marked "meas." are scope readings from that day; DDS and
AWG agree at the monitor (200-205 mVpp) and after the BLP-90 (+9.5 dBm, 1.88-1.91 Vpp).
From the SSB70100A mixer onward the levels are estimates, and the AM53 amplifier's
compression is still to be checked with the atoms.

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

## The amplitude table (Cal-V2, since November 2026)

`NewDDS2-Cooling2.0-Cal-V2.exe <pulse file> [amplitude table file]`

The compiler turns every power (W) into the AD9852's 12-bit amplitude word in `Pow2AmpWord`
(`conversions.cpp`). Its built-in table (2015) tabulates the amplitude fraction against the
*power* and starts at (0 W, 0), so below its first point, 16.2 mW, the amplitude comes out
nearly proportional to the power where a linear chain needs the square root: a pulse typed at
3 mW gets word 40 where the square-root law gives 88, and every Blackman or AFP pulse passes
through that region in its wings. Its cubic pieces do not join smoothly either (the slope
doubles at 66 mW) and the word is rounded down.

- **Without the second argument nothing changes**: the built-in table, the same words. The
  build of this source reproduces the lab's compiled files of 2026-11-17 byte for byte
  (`firmware/tests/mac_check.py --lab`).
- **With a table file** the conversion is: straight lines between the file's points against
  sqrt(power), the word rounded to the nearest. `firmware/amplitude_table.example.txt` shows
  the format (three required keyword lines, then `power_W fraction` points from `0 0`
  upwards). A file that is not a table, or a power above its last point, refuses the compile
  with exit 2; the built-in table is never used in its place in silence.
- A table file changes every pulse's area (the example file, which holds the 2015 points
  themselves, gives a 0.12 ms Blackman pi pulse 1.8 % more area and the 3 mW pulse 3 times
  more), so **pi powers are calibrated again** when a file goes in or changes.
- Freq-Scan-GUI passes `amplitude_table_MW.txt` / `amplitude_table_RF.txt` from the
  DDScontrol folder when the chain's file is there, and models both conversions in
  `ddsgui/ampword.py` (Preview shows the words before anything is compiled).
- The RF DDS is compiled by the same program, so without `amplitude_table_RF.txt` it gets the
  microwave chain's built-in table, compression correction included: against a square-root law
  through the word at 1 W the RF word is 6 % high at 4.8 W and 18 % low at 10 mW.
  `firmware/amplitude_table_RF.example.txt` is the table of a chain that is linear in the word
  (two points), to be replaced by a measured one.
- Only Cal-V2 has this. The Cal compiler (used by the addressing / arbitrary-pulse / cooling
  scripts) still has the built-in table alone.

Two rounding margins went in with it (`conversions.cpp`): `Time2Tics` played one step less
than typed for about one in three lengths on a pulse type's own grid (6 us for a typed 7 us
square pulse, 62 AFP tics for 0.504 ms); it now plays what is typed. None of the lengths in
the lab's current sequences was affected. `RR2Word` gets the same margin so that every build
writes the ramp-clock byte the lab's exe always has.

`firmware/tests/mac_check.py` builds the compiler on a Mac (x86_64 through Rosetta, with
stand-ins for `windows.h` and `NIDAQmx.h`) and runs these checks; see its docstring. It is a
check of the source, not a substitute for `fc /b` against the previous exe on the lab PC.

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
