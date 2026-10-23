#####################################################################
#   Coolscan.py -- scan ONE cooling sideband frequency to optimize cooling.
#
#   Unlike Freqscan.py (fixed cooling, scanned detection), this script
#   scans a cooling frequency and keeps the detection pulse FIXED.
#   Each scan point gets its own complete pulse file
#   (cooling + gate + detection), compiled per point.  Finals are built
#   as reset+RAW<point> by stepDDS_coolscan.bat -- the shared
#   RAWCool/RAWGate are NOT used, so no stale precompiled cooling can
#   leak into the scan.
#
#   Requires the O(n) recompiled NewDDS2-Cooling2.0-Cal-V2.exe
#   (2026-07-10) -- with the old exe each point's compile is minutes.
#
#   Cooling sequence copied from Cool_Cal.py (values of 2017.12.07).
#   created 20260710
#####################################################################

# import libraries
import sys, math
import csv         # for writing the pulse files
import numpy as np # to calculate the frequency steps
import os, subprocess          # calls to operating system

DelTempFiles = 1 # Clean up after we are done?

# define some constants
DDSDIR = r'C:\Users\Yang\Documents\Data\DDScontrol'  # lab-specific path; edit for another install
# Refuse to run in DDScontrol itself: the clean-up at the end deletes 'reset', which there
# is the master copy that every bat splices into the final files (review G2-2.1).
if os.path.normcase(os.path.abspath(os.getcwd())) == os.path.normcase(DDSDIR):
    sys.exit('ERROR: run this script from a data folder below DDScontrol, not in ' + DDSDIR)
# Refuse rows the compilers would turn into garbage before anything is compiled (review
# G2-2.4): the same limits as ddsgui (config.POWMAX_W) and the rebuilt Cal/Cal-V2 compilers.
POWMAX_W = 5.188  # W, top of the compilers' power calibration table (Pow2AmpWord)
def check_pulse_files(names):
    known = (-1, 1, 2, 22, 3, 33, 66, 661, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17)
    bad = []
    for name in names:
        if not os.path.exists(name):  # e.g. no Gate file in this script; the bat checks the rest
            continue
        for n, line in enumerate(open(name, 'rb').read().splitlines()[1:], 2):
            cells = line.split('\t')
            if len(cells) < 5:
                continue
            length, power, ptype = float(cells[2]), float(cells[3]), int(float(cells[4]))
            if ptype == 0:  # end of the pulse list for the compiler
                break
            if ptype not in known:
                bad.append('%s line %d: unknown pulse type %d' % (name, n, ptype))
            if not (0.0 <= power < POWMAX_W):
                bad.append('%s line %d: power %r W is outside 0 <= P < %g W' % (name, n, power, POWMAX_W))
            if ptype not in (-1, 4, 10) and not (length > 0.0):
                bad.append('%s line %d: length %r ms is not positive' % (name, n, length))
    if bad:
        print('ERROR: %d bad pulse row(s); stopping before they are compiled into final files:' % len(bad))
        for b in bad[:20]:
            print('  ' + b)
        sys.exit(1)
FilenameHead = 'Coolscan'   # filenames will start with this
FileComment = 'Cool\n'  # Comment line at head of pulse files (must end with \n)
print('Pulse file comment line: ' + FileComment.strip())

##################################################
#######  Reference frequency (from Cool_Cal.py / Freqscan.py) #######
f4newH = 56595100
f4new = f4newH + 481
fc = f4new

#######  Baseline sideband offsets from fc, Hz (Cool_Cal.py, updated 2017.12.07) #######
BaseOffsets = {
    'M1X': 18.5e3,
    'M2X': 37e3,
    'M1Y': 15e3,
    'M2Y': 30e3,
    'M1Z': 12e3,
    'M2Z': 24e3,
    }

##################################################
#######  THE SCAN #######
# ScanMode 'axis'  : scan one axis's -1 and -2 sidebands together,
#                    M1 = fc + offset, M2 = fc + 2*offset (offset = trap frequency)
# ScanMode 'single': scan only ScanSideband, all others fixed
ScanMode = 'axis'
ScanAxis = 'X'          # 'X','Y' or 'Z' (used when ScanMode == 'axis')
ScanSideband = 'M1X'    # one of: 'M1X','M2X','M1Y','M2Y','M1Z','M2Z' (used when ScanMode == 'single')

if ScanMode == 'axis':
    if ScanAxis not in ('X','Y','Z'):
        print ('ERROR: ScanAxis must be X, Y or Z')
        sys.exit(1)
    ScanLabel = 'M1%s+M2%s' % (ScanAxis, ScanAxis)
    CenterOffset = BaseOffsets['M1'+ScanAxis]
elif ScanMode == 'single':
    if ScanSideband not in BaseOffsets:
        print ('ERROR: ScanSideband must be one of ' + ','.join(BaseOffsets.keys()))
        sys.exit(1)
    ScanLabel = ScanSideband
    CenterOffset = BaseOffsets[ScanSideband]
else:
    print ('ERROR: ScanMode must be axis or single')
    sys.exit(1)

# scanned offset is the -1 sideband offset from fc (the trap frequency in axis mode)
StartingOffset = CenterOffset - 4e3   # Hz from fc
StoppingOffset = CenterOffset + 4e3   # Hz from fc
NumberOfPoints = 17

NumberOfRepeats = 1000  # Number of times to repeat the scan

if StartingOffset == StoppingOffset:
    OffsetStepSize = 1e3
else:
    OffsetStepSize = (StoppingOffset - StartingOffset)/(NumberOfPoints-1)

ScanOffsets = np.arange(StartingOffset, StoppingOffset+OffsetStepSize/2.0, \
                        OffsetStepSize) # in Hz, offsets from fc

##################################################
#######  Cooling pulse parameters (Cool_Cal.py, last updated 2015-6-7) #######
AFPPower0   = 0.1*(0.075/0.1)
AFPPower1   = 0.19*(0.075/0.1)
AFPPower2   = 0.64*(0.075/0.1)
AFPLength   = 3.0 # ms
AFPHSR0     = -4.0e3
AFPHSR1     = -6.0e3 # Hz
AFPHSR2     = -6.0e3 # Hz

numcool = 30    # cycles in the main cooling loop
numcool2 = 10   # cycles in the second (HSR2) loop

##################################################
#######  FIXED detection pulse (edit for your thermometry point) #######
# For sideband thermometry set DetectionFrequency to fc - (axis sideband),
# e.g. fc - 20e3 for the X red sideband; fc for the carrier.
DetectionFrequency  = f4new - 20e3
DetectionPulseType  = 1     # 1 for AFP, 2 for Blackman, 9 for CW, 22 Composite Pi, 3 square
DetectionPulseLength = 3.0
DetectionPulsePower = 0.08
DetectionPulseHSR   = -4e3  # Hz (only used for AFP pulses)
DetRepeats = 1      # how many detection pulses to repeat

##################################################

NumberOfFiles = len(ScanOffsets)

if NumberOfFiles > 1:
	print('Offset scan: %.4f to %.4f Hz, %d points (step %.4f Hz)' \
		% (ScanOffsets[0], ScanOffsets[-1], NumberOfFiles, ScanOffsets[1]-ScanOffsets[0]))
else:
	print('Single-point offset scan at %.4f Hz' % ScanOffsets[0])

# Generate file names
Filenames = range(0,NumberOfFiles)
for i in xrange(0,NumberOfFiles):
    Filenames[i] = FilenameHead + '-%03d'% (i+1)
MeasListFilename = FilenameHead+'-Meas'
ScanFilename = FilenameHead+'.scan'
ListFilename = FilenameHead +'.lst'

measfile = open(MeasListFilename, "wb")
measfile.write(FileComment)
writerm = csv.writer(measfile, dialect='excel-tab')

# begin loop: one COMPLETE pulse file (cooling+gate+detection) per scan point
for i in xrange(0,NumberOfFiles):
    ScannedFreq = fc + ScanOffsets[i]
    # this point's six sideband frequencies: baseline, with the scanned one(s) replaced
    Freqs = {}
    for key in BaseOffsets:
        Freqs[key] = fc + BaseOffsets[key]
    if ScanMode == 'axis':
        Freqs['M1'+ScanAxis] = fc + ScanOffsets[i]
        Freqs['M2'+ScanAxis] = fc + 2.0*ScanOffsets[i]
    else:
        Freqs[ScanSideband] = ScannedFreq

    print('Making pulsefile '+Filenames[i]+', '+ScanLabel+', offset = %g Hz'%(ScanOffsets[i]))
    pulsefile = open(Filenames[i], "wb") # open pulse file
    pulsefile.write(FileComment) # write comment line
    writer = csv.writer(pulsefile, dialect='excel-tab')
    # Order of parameters: [Freq, HSR, Length, Power, Type, Comment]

    writer.writerow([58.0e6, 0.0, 10.0, 0., 1, 'Dummy']) # Dummy pulse

    ####### cooling sequence (copied from Cool_Cal.py) #######
    for j in xrange(0,numcool): # Typical cooling sequence (-2, -1)
        writer.writerow([Freqs['M2X'], AFPHSR1, AFPLength, AFPPower1, 1, 'X-2 pulse %d'%(j+1)])
        writer.writerow([Freqs['M1X'], AFPHSR0, AFPLength, AFPPower0, 1, 'X-1 pulse %d'%(j+1)])
        writer.writerow([Freqs['M2Y'], AFPHSR1, AFPLength, AFPPower1, 1, 'Y-2 pulse %d'%(j+1)])
        writer.writerow([Freqs['M1Y'], AFPHSR0, AFPLength, AFPPower0, 1, 'Y-1 pulse %d'%(j+1)])
        writer.writerow([Freqs['M2Z'], AFPHSR1, AFPLength, AFPPower1, 1, 'Z-2 pulse %d'%(j+1)])
        writer.writerow([Freqs['M1Z'], AFPHSR0, AFPLength, AFPPower0, 1, 'Z-1 pulse %d'%(j+1)])

    for j in xrange(0,numcool2): # second loop (HSR2 on the -1 pulses)
        writer.writerow([Freqs['M2X'], AFPHSR1, AFPLength, AFPPower1, 1, 'X-2 pulse %d'%(j+1)])
        writer.writerow([Freqs['M1X'], AFPHSR2, AFPLength, AFPPower0, 1, 'X-1 pulse %d'%(j+1)])
        writer.writerow([Freqs['M2Y'], AFPHSR1, AFPLength, AFPPower1, 1, 'Y-2 pulse %d'%(j+1)])
        writer.writerow([Freqs['M1Y'], AFPHSR2, AFPLength, AFPPower0, 1, 'Y-1 pulse %d'%(j+1)])
        writer.writerow([Freqs['M2Z'], AFPHSR1, AFPLength, AFPPower1, 1, 'Z-2 pulse %d'%(j+1)])
        writer.writerow([Freqs['M1Z'], AFPHSR2, AFPLength, AFPPower0, 1, 'Z-1 pulse %d'%(j+1)])

    ####### gate / transfer pulses (fixed; add rows here if needed) #######
    #~ writer.writerow([f33to43new, -8e3, 3.0, P33to43new*64/36, 1, '3,-3 -> 4,-3'])

    ####### FIXED detection pulse #######
    for x in xrange(0,DetRepeats):
        writer.writerow([DetectionFrequency, \
                        DetectionPulseHSR, \
                        DetectionPulseLength, \
                        DetectionPulsePower, \
                        DetectionPulseType, \
                        'Measure'])

    pulsefile.close() # Close the pulse file

    # Meas log: filename, the scanned sideband(s), and the detection row. The sideband rows are
    # real pulse rows (HSR and power as played in the first cooling loop; the -1 pulses use
    # AFPHSR2 in the second loop); the scan offset goes in the comment, not in the HSR column
    # where it used to be (review G2-7.3).
    writerm.writerow([Filenames[i]])
    if ScanMode == 'axis':
        writerm.writerow([Freqs['M1'+ScanAxis], AFPHSR0, AFPLength, AFPPower0, 1,
                          'M1'+ScanAxis+' scanned, offset %r Hz' % ScanOffsets[i]])
        writerm.writerow([Freqs['M2'+ScanAxis], AFPHSR1, AFPLength, AFPPower1, 1,
                          'M2'+ScanAxis+' scanned, offset %r Hz' % (2.0*ScanOffsets[i])])
    else:
        _m2 = ScanSideband.startswith('M2')
        writerm.writerow([ScannedFreq, AFPHSR1 if _m2 else AFPHSR0, AFPLength,
                          AFPPower1 if _m2 else AFPPower0, 1,
                          ScanSideband+' scanned, offset %r Hz' % ScanOffsets[i]])
    writerm.writerow([DetectionFrequency, DetectionPulseHSR, DetectionPulseLength, \
                      DetectionPulsePower, DetectionPulseType, 'Measure'])

measfile.close()

# Write list file (input to the bat)
listfile = open('List', "wb")
for i in Filenames:
    listfile.write(i+'\n')
listfile.close()

# Write scan file
scanfile = open(ScanFilename, "wb")
scanfile.write(FilenameHead+'\n')
scanfile.write(str(NumberOfFiles)+'\n')
scanfile.write(str(NumberOfRepeats)+'\n')
scanfile.close()

# Compile every point and build finals as reset+RAW<point>
print('Compiling %d pulse files (stepDDS_coolscan.bat)...' % NumberOfFiles)
check_pulse_files(Filenames)
rc = subprocess.call([os.path.join(DDSDIR, 'stepDDS_coolscan.bat'), 'List'])
if rc != 0:
	print('ERROR: stepDDS_coolscan.bat failed with exit %d. Aborting.' % rc)
	sys.exit(1)

if DelTempFiles == 1 :
    os.system("del List reset")

listfile = open(ListFilename, "wb")
for j in xrange(0,NumberOfRepeats):
    for i in Filenames:
        listfile.write(i+'-final.txt\n')
listfile.close()

print('Scan list %s: %d files x %d repeats = %d scans total' \
	% (ListFilename, NumberOfFiles, NumberOfRepeats, NumberOfFiles*NumberOfRepeats))
print("Scanned %s from fc%+g to fc%+g Hz"%(ScanLabel, StartingOffset, StoppingOffset))

os.system('copy "%s" "%s.py"' % (sys.argv[0], FilenameHead)) # save a copy of this python file (quoted: paths may hold spaces)
os.system("copy "+FilenameHead+".lst last.lst") # copy list file to last.lst
os.system("copy "+FilenameHead+".scan last.scan") # copy scan file to last.scan
print('Done. Script copied to %s.py; list/scan files copied to last.lst and last.scan.' % FilenameHead)
