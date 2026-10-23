# 20191115 DEVELOPING: this is a test script to generate a single file containing an arbitrary array of DDS pulses.
#	       (Currently, this file only resides in the DDS folder of 20191107.)
# 	       Typically, NewDDS2-Cooling2.0-Cal.exe calculates the pulse train and generate a single file with one single column.
# 	       It is not easy to split the pulses, so typically the pulse train contains the pulses in series without interruption.
# 	       Here the goals is to generate a file for all pulses that can be seperated into different parts in a long sequence, 
#	           with each pulse automatically split.
# 	       The original thought is to write the data into a new format: each row containing all the data for one pulse,
#		while the number of column represents the number of total pulses.
#	       The number of samples per row can vary.
#	       However, it turns out that it could be simpler: using still a single long column for all data of all pulses.
#	       Then make another file about the paritition of this long column data.
#               To achieve this, we still need to compile each pulse separately so we can read the number of samples per pulse.
# 20191209: Make this file join the daily DDS folder creation as DDScool.py & others.


# import libraries
import sys, math
import csv         # for writing the pulse files
import numpy as np # to calculate the frequency steps
import os, subprocess          # calls to operating system
import string      # string manipulation
import random
from shutil import copyfile
import time


DelTempFiles = 1 # Clean up after we're done?

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
def compile_raw(name):
	"""Compile pulse file <name> with the Cal compiler and return 'RAW' + name. Stops the script
	when the compile fails, so a RAW file left by an earlier run is never copied to CameraGUI
	(review G2-8.1)."""
	raw = 'RAW' + name
	if os.path.exists(raw):
		os.remove(raw)
	check_pulse_files([name])
	rc = subprocess.call([os.path.join(DDSDIR, 'NewDDS2-Cooling2.0-Cal.exe'), name])
	if rc != 0 or not os.path.exists(raw):
		sys.exit('ERROR: compiling %s failed (exit %d) or wrote no %s; nothing more is copied to CameraGUI.'
			% (name, rc, raw))
	return raw
FilenameHead = 'DDSarb'   # own name, not Cool_Cal's (unused here; review G2-8.3)
FileComment  = 'Cool\n'  	 	 # Comment line at head of pulse files (must end with \n)
print('Pulse file comment line: ' + FileComment.strip())


f4new =58644387.8708 - 1.2e3 + 0.5e3 -8.2e3+7e3 -0.6e3+1.8e3 + 1.0e3-4e3 +0e3


##################################################
### CLOCK TRANSITION FREQ: 60.0068MHz ############
##################################################

# (The line-synchronous field fit copied from Cool_Cal.py - fitfunc, the 2017 data, curve_fit,
#  frec - was removed here: nothing in this script used it; review G2-8.3.)
FrequencyStepSize =0.03e3 # Hz
NumberOfRepeats   = 11# Number of times to repeat the scan


# define the detection pulse
# Typical square pulse
DetectionPulseType   =1	   	# 1 for AFP, 2 for Blackman, 9 for CW (no ending), 22 Composite Pi  3 square pulse(phase coherence)
DetectionPulseLength =3	 	# ms; 0.15   #0.15#0.4  #0.16
DetectionPulsePower  =0.2
DetectionPulseHSR     =-6e3		 # Hz (only used for AFP pulses) 
# For Blackman and CW pulses, "HSR" is the phase in units of pi




Uarb = [
#~ [58.0e6, 0.0, 10.0, 0., 1, 'Dummy'], # Dummy pulse
[f4new,DetectionPulseHSR, DetectionPulseLength, DetectionPulsePower * 1, DetectionPulseType, 'Measure']
,[f4new,DetectionPulseHSR, DetectionPulseLength, DetectionPulsePower * 2, DetectionPulseType, 'Measure']
,[f4new,DetectionPulseHSR, DetectionPulseLength, DetectionPulsePower * 3, DetectionPulseType, 'Measure']
,[f4new,DetectionPulseHSR, DetectionPulseLength, DetectionPulsePower * 4, DetectionPulseType, 'Measure']
,[f4new,DetectionPulseHSR, DetectionPulseLength, DetectionPulsePower * 5, DetectionPulseType, 'Measure']
,[f4new,DetectionPulseHSR, DetectionPulseLength, DetectionPulsePower * 1, DetectionPulseType, 'Measure']
,[f4new,DetectionPulseHSR, DetectionPulseLength, DetectionPulsePower * 2, DetectionPulseType, 'Measure']
,[f4new,DetectionPulseHSR, DetectionPulseLength, DetectionPulsePower * 3, DetectionPulseType, 'Measure']
,[f4new,DetectionPulseHSR, DetectionPulseLength, DetectionPulsePower * 4, DetectionPulseType, 'Measure']
,[f4new,DetectionPulseHSR, DetectionPulseLength, DetectionPulsePower * 5, DetectionPulseType, 'Measure']
,[f4new,DetectionPulseHSR, DetectionPulseLength, DetectionPulsePower * 1, DetectionPulseType, 'Measure']
]




print('Making pulsefile ')

UarbRaw      = [ ] # a register of the Raw data (after compilation) for all pulses
UarbPartition = [ ] # a register for the paritition of the long concatenated Raw data into individual pulses

for i in xrange(0,len(Uarb)):
	Tstamp1 = time.time()*1000 # ms
	
	pulsefile = open("ArbTemp", "wb") # open pulse file
	pulsefile.write(FileComment) # write comment line
	writer = csv.writer(pulsefile, dialect='excel-tab')
	writer.writerow(Uarb[i])
	pulsefile.close()

	# the next line calls the .exe and takes most time on the order of > 100ms
	compile_raw('ArbTemp')
	
	# once the raw data file for each pulse is generated, read them into a local register here	
	RawData = []
	with open("RAWArbTemp", "rb") as f:
		for row in csv.reader(f):
			RawData.append(row[0])

	UarbRaw.append(RawData)
	
	Tstamp2 = time.time()*1000 # ms
	print 'pulse {0:d} process time (ms) = {1:.1f}'.format(i , Tstamp2 - Tstamp1)


Tstamp3 = time.time()*1000 # ms

pulsefile = open("RAWArb", "wb") # open pulse file
writer = csv.writer(pulsefile, dialect='excel')
for i in xrange(0,len(UarbRaw)):
	pulsesize =  len(UarbRaw[i])
	UarbPartition.append(pulsesize)
	for j in xrange(0,pulsesize):
		writer.writerow([ UarbRaw[i][j] ])
pulsefile.close()


# write another file regarding the partition of the long concatenated Raw data
pulsefile = open("RAWArbPartition", "wb") # open pulse file
writer = csv.writer(pulsefile, dialect='excel')
for i in xrange(0,len(UarbPartition)):
	writer.writerow([UarbPartition[i]])
pulsefile.close()
	
Tstamp4 = time.time()*1000 # ms
print 'final all pulses process time (ms) = {0:.1f}'.format(Tstamp4 - Tstamp3)
	
copyfile('RAWArb','C:/Users/Yang/Documents/Eclipse/CameraGUI/release/DDSarb.txt')
copyfile('RAWArb','C:/Users/Yang/Documents/Eclipse/CameraGUI/debug/DDSarb.txt')
copyfile('RAWArb','C:/Users/Yang/Documents/Eclipse/CameraGUI/DDSarb.txt')

copyfile('RAWArbPartition','C:/Users/Yang/Documents/Eclipse/CameraGUI/release/DDSarbPartition.txt')
copyfile('RAWArbPartition','C:/Users/Yang/Documents/Eclipse/CameraGUI/debug/DDSarbPartition.txt')
copyfile('RAWArbPartition','C:/Users/Yang/Documents/Eclipse/CameraGUI/DDSarbPartition.txt')




if DelTempFiles == 1 :
	#~ os.system("del Cool List RAWCool reset")	
	#~ os.system("del Cool List reset")
	os.remove("ArbTemp")
	os.remove("RAWArbTemp")
	
	
	
	

pulsefile = open("dummy", "wb") # open pulse file
pulsefile.write(FileComment) # write comment line
writer = csv.writer(pulsefile, dialect='excel-tab')
# Also create the very first dummy pulse here
writer.writerow([58.0e6, -6e3, 2, 0, 1, 'Measure']) 
#~ writer.writerow([f+frec(i),0, DetectionPulseLength, 0 , DetectionPulseType, 'Measure'])
#~ writer.writerow([f+frec(i),1, DetectionPulseLength/2,0 , DetectionPulseType, 'Measure'])
pulsefile.close()
compile_raw('dummy')
#~ os.system('copy RAWGate C:\Users\Yang\Documents\Eclipse\CameraGUI\release\DDSaddress.txt')
copyfile('RAWdummy','C:/Users/Yang/Documents/Eclipse/CameraGUI/release/DDSdummy.txt')
copyfile('RAWdummy','C:/Users/Yang/Documents/Eclipse/CameraGUI/debug/DDSdummy.txt')
copyfile('RAWdummy','C:/Users/Yang/Documents/Eclipse/CameraGUI/DDSdummy.txt')
	