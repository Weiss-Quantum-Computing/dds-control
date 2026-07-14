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
FilenameHead = 'Coolscan'   # filenames will start with this
FileComment = 'Cool\n'  # Comment line at head of pulse files (must end with \n)
print (FileComment)

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

# Generate file names
Filenames = range(0,NumberOfFiles)
for i in xrange(0,NumberOfFiles):
    Filenames[i] = FilenameHead + '-%03d'% (i+1)
MeasListFilename = FilenameHead+'-Meas'
ScanFilename = FilenameHead+'.scan'
ListFilename = FilenameHead +'.lst'
print (ListFilename)

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

    # Meas log: filename, the scanned sideband(s), and the detection row
    writerm.writerow([Filenames[i]])
    if ScanMode == 'axis':
        writerm.writerow([Freqs['M1'+ScanAxis], ScanOffsets[i], AFPLength, AFPPower0, 1, 'M1'+ScanAxis+' scanned'])
        writerm.writerow([Freqs['M2'+ScanAxis], 2.0*ScanOffsets[i], AFPLength, AFPPower1, 1, 'M2'+ScanAxis+' scanned'])
    else:
        writerm.writerow([ScannedFreq, ScanOffsets[i], AFPLength, AFPPower0, 1, ScanSideband+' scanned'])
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
subprocess.call([r"C:\Users\Yang\Documents\Data\DDScontrol\stepDDS_coolscan.bat", "List"])

if DelTempFiles == 1 :
    os.system("del List reset")

listfile = open(ListFilename, "wb")
for j in xrange(0,NumberOfRepeats):
    for i in Filenames:
        listfile.write(i+'-final.txt\n')
listfile.close()

print("%d files"%(NumberOfFiles))
print("%d repeats"%(NumberOfRepeats))
print("%d scans total"%(NumberOfFiles*NumberOfRepeats))
print("Scanned %s from fc%+g to fc%+g Hz"%(ScanLabel, StartingOffset, StoppingOffset))

os.system("copy "+sys.argv[0]+" "+FilenameHead+".py") # save a copy of this python file
os.system("copy "+FilenameHead+".lst last.lst") # copy list file to last.lst
os.system("copy "+FilenameHead+".scan last.scan") # copy scan file to last.scan
