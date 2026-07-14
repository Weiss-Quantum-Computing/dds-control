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
from scipy.optimize import curve_fit


DelTempFiles = 1 # Clean up after we're done?

# define some constants
FilenameHead = 'Cool_Cal'   	 # filenames will start with this (can include directory, but use forward slash)
FileComment  = 'Cool\n'  	 	 # Comment line at head of pulse files (must end with \n)
print (FileComment)


f4new =58644387.8708 - 1.2e3 + 0.5e3 -8.2e3+7e3 -0.6e3+1.8e3 + 1.0e3-4e3 +0e3


##################################################
### CLOCK TRANSITION FREQ: 60.0068MHz ############
##################################################

def fitfunc(x,a,b,c,d,p1,p2,p3):
	return a*np.cos(2*math.pi*x*0.060+p1)+b*np.cos(2*math.pi*0.120+p2)+c*np.cos(2*math.pi*x*0.18+p3)
#~ y =[0,0.3, 1.9, 1.5, 1.5,1.7,1.2,1.6,1.4,0.9,-0.1,-0.5,-0.3,-0.5,-0.3,-0.1,0.1] # after 5pm
#~ y = [0,0.7,1.3,2.1,2.6,2.8,2.4,3.2,2.8,3.1,1.2,1.2,0.3,0.4,-0.1,0.3,-0.2]	# before 5pm
y = [0, 0.9, 1.8, 1.3, 2.2, 2.2, 2, 2.4, 2.1, 1.0, 0.6, -0.5, -0.1, -0.6, -0.5, -0.5, -0.5 ] # before 5pm 2017.10.17

x =  np.linspace(0, 16, num=17, endpoint=True)
popt, pcov = curve_fit(fitfunc, x, y)

def frec(time):
	print fitfunc(time-math.floor(time/16.67)*16.67,*popt)*1000
	return fitfunc(time-math.floor(time/16.67)*16.67,*popt)*1000
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
	subprocess.call(['C:\Users\Yang\Documents\Data\DDScontrol\NewDDS2-Cooling2.0-Cal.exe', 'ArbTemp'])
	
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
subprocess.call(['C:\Users\Yang\Documents\Data\DDScontrol\NewDDS2-Cooling2.0-Cal.exe', 'dummy'])
#~ os.system('copy RAWGate C:\Users\Yang\Documents\Eclipse\CameraGUI\release\DDSaddress.txt')
copyfile('RAWdummy','C:/Users/Yang/Documents/Eclipse/CameraGUI/release/DDSdummy.txt')
copyfile('RAWdummy','C:/Users/Yang/Documents/Eclipse/CameraGUI/debug/DDSdummy.txt')
copyfile('RAWdummy','C:/Users/Yang/Documents/Eclipse/CameraGUI/DDSdummy.txt')
	