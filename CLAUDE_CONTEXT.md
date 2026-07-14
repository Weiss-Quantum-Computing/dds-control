# DDS Control — Context Briefing for Claude

Paste or reference this file at the start of a Claude Code session before
working on this project. It summarizes what the software does, what's
already been fixed and verified, what's still open, and the lab-specific
quirks that aren't obvious from reading the code cold.

Repo: https://github.com/Weiss-Quantum-Computing/dds-control (public)

## What this is

Control software for a homemade DDS (Direct Digital Synthesis) source
driving microwave/RF pulse sequences for a cesium-133 atomic-physics
experiment (laser-cooled atoms in an optical lattice; hyperfine-manifold
state manipulation via an AD9852 DDS through a National Instruments
PCIe-6536 digital I/O card). See `README.md` for the full architecture
diagram and repo layout — read that first for the pipeline shape
(Python generators → C++ pulse compiler → batch concatenation → C++ run
program → hardware).

Three layers, three skill domains: Python 2 pulse-sequence generators
(`scripts/`), C++ pulse compilers and the hardware-facing run program
(`firmware/`, built with MinGW GCC via Eclipse CDT on Windows), and DOS
batch orchestration (`batch/`) that glues them together. The lab machine
is Windows (7, at last check), and all paths in the batch files and some
scripts are hardcoded to `C:\Users\Yang\Documents\Data\DDScontrol\`.

## Fixes already applied — know these before touching the C++

**1. O(n²) → O(n) pulse-train assembly bug (the big one).**
`firmware/NewDDS2-Cooling2.0-Cal/pulse.h` and the `-Cal-V2` twin had a
`Pulse::operator+` that reallocated and copied the *entire* accumulated
pulse train on every single pulse added — building an N-pulse sequence
did O(N²) work. For long cooling sequences (or per-point cooling scans)
this made compiles take minutes. Fixed by adding a `capacity` member and
an `Append(const Pulse & seg)` method that grows the buffer with
amortized doubling (like `std::vector`), and changing every call site in
`NewDDS.cpp`'s main pulse-building loop from `pulse = (pulse + X) + Y;`
to `pulse.Append(X); pulse.Append(Y);`. `operator+`/`operator=`/`operator*`
are untouched, just unused in the hot path now. **Both `Cal` and `Cal-V2`
have this fix; verify any new/legacy compiler variant you touch doesn't
still have the old pattern** (`grep -n "pulse = (pulse" NewDDS.cpp` should
only hit commented-out lines).

**2. `FIFOCLOCK` constant mismatch caused a real, near-miss bug.**
`DDSconstants.h` defines the DDS update-clock rate used to convert pulse
durations to tic counts (`Time2Tics`). At one point the `Cal` project had
`500000.0` while `Cal-V2` and the actual deployed/hardware-matching value
was `1000000.0` — a factor-of-2 tic-count mismatch that produced a
*different but still well-formed* RAW output (caught via `fc /b` binary
diff against the previously-deployed exe, not by any compile error).
**This is why every compiler change here gets verified by a binary diff
against the previously-trusted exe on the same input file before
deployment** — a silent constant mismatch will not throw an error, it
will just quietly detune every pulse.

**3. `endl` → `'\n'` in the RAW-file write loop.** `endl` flushes the
stream on every line; with pulse trains now in the hundreds of thousands
of lines (after fix #1 made larger sequences practical), that flush storm
was adding ~4 seconds per compile for no reason. Also removed a
per-pulse `cout << "Reading pulse " << num` debug line that was similarly
expensive at scale. **Caveat: this second cosmetic edit was applied to
the Mac-side source but may not yet be present in whatever `.cpp` a lab
PC last built from** — check `grep -c 'Reading pulse.*num' NewDDS.cpp`
before assuming it's applied.

## Deployment / build gotchas (Windows + Eclipse CDT + MinGW)

- **Eclipse project name ≠ folder name for `NewDDS2-Cooling2.0-Cal`.**
  Its internal Eclipse project is named `NewDDS2`, so it builds to
  `NewDDS2.exe` — must be manually renamed to `NewDDS2-Cooling2.0-Cal.exe`
  before deploying. `Cal-V2`'s project name matches its folder and needs
  no rename.
- **Requires NI-DAQmx (ANSI C Dev SDK)** installed at
  `C:\Program Files\National Instruments\NI-DAQ\DAQmx ANSI C Dev\` — both
  `include/` and `lib/msvc/` are referenced in the `.cproject` files.
  Not bundled in this repo.
- **libxl headers were removed** from the compiler folders for public-repo
  licensing reasons (see `LIBXL_HEADERS_REMOVED.txt` in the affected
  folders) — they're only needed by the disabled `USE_EXCEL` path in
  `getpulse.cpp`, so the normal text-file build is unaffected.
- **Mac→Windows file transfer via non-native-filesystem drives (FAT32/
  exFAT USB sticks) creates `._<filename>` AppleDouble shadow files.**
  These get auto-added as bogus extra source files by Eclipse and produce
  bizarre "stray byte" / "'Mac' does not name a type" compile errors that
  look nothing like a real code problem. Fix: delete all `._*` files
  (`find ... -name '._*' -delete` on Mac, `del /S ._*.*` on Windows)
  before importing/building. This bit us once already — if you see
  garbage compiler errors mentioning a file named `._something.cpp`,
  this is almost certainly why.
- **Verification discipline for any compiler change:** build old vs new
  exe, run both on the *same* input pulse file, `fc /b` the two `RAW*`
  outputs — must report "no differences." Only then deploy. This has
  already caught one real bug (the FIFOCLOCK mismatch above); don't skip
  it for a change that "should" be a no-op.
- **The exes here never touch hardware directly.** The `Cal`/`Cal-V2`
  compilers only read a pulse-definition text file and write a `RAW*`
  file — `IO()` (the DAQmx call) is commented out in that code path. All
  binary-diff testing above is zero-risk to run repeatedly. Only
  `NewDDS2-Cooling2.0.exe` (the run program, launched by `stepDDS.bat`)
  actually writes to the DAQ card.

## Pipeline / batch-file conventions worth knowing

- `stepDDS_cal3-V2.bat`, `stepDDS_coolscan.bat`, etc. take a *compile
  list* (plain filenames, no extension) — NOT the `.lst` *run list*
  (which has `-final.txt` suffixes and repeat counts). Feeding a bat the
  wrong list either does nothing useful or, worse, tries to compile/
  delete files it shouldn't. `stepDDS_coolscan.bat` now has guards against
  this (rejects `.lst` arguments, skips any token with a file extension).
- Final pulse-sequence files are assembled as
  `reset + RAWCool + RAWGate + RAW<point>` (DOS `copy` concatenation) —
  `RAWCool`/`RAWGate` come from a *separate*, earlier precompile step
  (`Cool_Cal.py`), so a scan's cooling block is only as current as the
  last time that script ran. `Coolscan.py` (added in this project) breaks
  from this pattern deliberately: it compiles a complete cooling+detection
  block per scan point so a stale shared `RAWCool` can never leak in.
- Every pulse block ends with an end-marker (`pend`/`pend2`/`pendC`) that
  drops the DDS's self-timing mask, halting FIFO playback until the next
  external trigger. This is why triggers and pulses must correspond 1:1,
  and why a spurious extra trigger during an idle (low-duty-cycle)
  window can desync the whole sequence — long/high-duty-cycle sequences
  (like full cooling trains) are comparatively self-correcting because a
  stray trigger mostly lands *during* a pulse (where it's absorbed) rather
  than in idle time.
- All the Python generator scripts are Python 2 (print statements,
  `xrange`, mutable `range()` objects) and run on the lab Windows machine,
  not this Mac — treat "does it run" as "does it look right by inspection
  and dry-run simulation," not "did I execute it for real."

## Licensing status across the `Weiss-Quantum-Computing` org

MIT (2026, "Weiss Quantum Computing") has been added to: `dds-control`,
`Data-Analysis`, `Daily-file-creation`, `Freq-Scan-GUI`,
`Dipole-Coil-Noise-Calculations`, `Two_Photon_Transition`, `Cluster`.
`.github` already had it (2024, correct holder) — untouched.

**`CameraGui`** was transferred into the org from a personal account and
bundles genuine proprietary vendor SDK files (National Instruments
NI-DAQmx/NI-FPGA headers, and the Photometrics/Roper/Princeton PVCAM
camera SDK — all "All Rights Reserved"). It now has MIT +
`THIRD_PARTY_NOTICES.md` carving those files out, **and the repo has been
made private** specifically because of that bundled proprietary content
(public redistribution of vendor "all rights reserved" SDK headers is the
actual concern, not just a license-text mismatch). If you ever want it
public again, the vendor files need to come out first (replace with a
"install the NI-DAQmx / PVCAM SDK yourself" note in the README, same
pattern as the libxl removal in this repo).

**Open items, not yet resolved:**
- `WeissQCKicad` — MIT license's copyright holder currently reads
  "maadehaan" (personal name) instead of "Weiss Quantum Computing" — the
  rest of the org's repos say the latter. Needs a one-line fix if you
  want consistency.
- `DMD-Control-Software` — currently CC0 1.0 (public domain), not MIT.
  Deliberately left alone since CC0 is *more* permissive than MIT, so
  overwriting it would add restrictions the original author may not have
  intended. Needs a decision, not an automatic overwrite.
- `Peng-s-Files` — contains 4 `.zip` archives whose contents haven't been
  audited (can't inspect archive contents via the GitHub API without
  downloading). Filenames suggest the group's own control-software
  projects, but this hasn't been confirmed. Don't license-stamp or assume
  clean without checking, given the CameraGui precedent.

## General working style notes for this project

- This is real, actively-used lab hardware — treat "does the file
  compile/parse" and "does it touch hardware" as separate risk
  categories, and say explicitly which one any given check covers.
- Physics/calibration constants embedded in the Python scripts
  (transition frequencies, sideband offsets, pulse powers) are
  hand-tuned and dated by the actual experimenters — never "fix" or
  "simplify" these without being asked; they're not arbitrary.
- When in doubt about which of several similarly-named script/exe
  variants is "the current one," check file dates and cross-reference
  which `.bat`/`.py` actually invokes it — this codebase has ~15 years of
  copy-paste lineage (`Freqscan.py`, `Freqscan2.py`, `-RF` variants,
  `- Copy - <date>` files) and the newest-looking name is not always the
  one in active use.
