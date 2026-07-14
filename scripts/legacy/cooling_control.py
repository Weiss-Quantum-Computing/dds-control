# Write pulse files for NewDDS2-version3.exe
# Ted Corcovilos 20110308 (Rewrite for easier changes)
# NB: Check that all 'float' numbers contain an explicit decimal point

# TODO: Add variable for sweep type and case structures

# import libraries

import sys, math
import csv         # for writing the pulse files
import numpy as np # to calculate the frequency steps
import os, subprocess          # calls to operating system
import string      # string manipulation

DelTempFiles = 1 # Clean up after we're done?

# define some constants
FilenameHead = 'PIStar'   # filenames will start with this (can include directory, but use forward slash)
FileComment = 'Freq scan\n'  # Comment line at head of pulse files (must end with \n)
print (FileComment)
QubitFreq=60.0067642e6#+2000
PiFreq=59.804e6
# define the scan range
# StartingFrequency = 58.607e6 # Hz
# StoppingFrequency = 58.607e6 # Hz
# StartingFrequency = QubitFreq#-3e3 # Hz
# StoppingFrequency = QubitFreq#+3e3
StartingFrequency = 59.804e6-3e3 # Hz
StoppingFrequency = 59.804e6+3e3 # Hz
FrequencyStepSize = 1e3 # Hz
StartTime = 0.15 #ms
StopTime = 1.15 #ms
#TimeStepSize = 0.05 #ms
NumberOfRepeats   = 3 # Number of times to repeat the scan


# pulse types definition:
# 1. AFP; 2. Blackman; 3. square pulse; 4. End pulse 
# 5. pi star CW; 6. pi star Blackman; 7. Ramsey pulse; 8. Echo pulses

#Power = 6.*(np.arange(0, 1.01,0.1)**2)

Pi40To31=.15 # ms pi pulse for |4,0>--|3,1>
Pi30To41=.166 # 
# define the detection pulse
# Typical square pulse
DetectionPulseType   = 2
DetectionPulseLength = .15 # ms 0.06 for pi/2 
PulseLength = np.arange(0,.2405,.02)#np.arange(0.15/2, 0.15/2, .02) # ms
DetectionPulsePower  = 3.14    #  0.252 W
DetectionPulseHSR    = 0 # (Hz for AFP pulses, ms for Ramsey pulse waiting time, pi for Blackman)
#WaitTimes = np.arange(StartTime, StopTime+TimeStepSize/2, TimeStepSize)
#Phases = np.arange(0,2.1,0.25) # Phase from 0 to 2pi in steps of pi/4
#WaitTimes = np.arange(3,4.04,.1)

#Typical AFP parameters below:
# DetectionPulseType   = 1  # 1 for AFP, 2 for Blackman, 3 fs	or square (numbers like NewDDS)
# DetectionPulseLength = 3. # ms
# DetectionPulsePower  = 3. # W
# DetectionPulseHSR    = -4.0e3 # Hz (only used for AFP pulses)

# Typical Blackman parameters below:
# DetectionPulseType   = 2   # 1 for AFP, 2 for Blackman, 3 for square (numbers like NewDDS), 5 for pi star pulse
# DetectionPulseLength = 0.3 # ms
# DetectionPulsePower  = 0.282 # W
# DetectionPulseHSR    = 4.0e3 # Hz (only used for AFP pulses)

# Some typical values
# AFP pulse
AFPPower  = 3. # W
AFPLength = 3.0 # ms
AFPHSR    = -4.0e3 # Hz
# Square Pi pulse on -1 transition
PiPower    = 0.252 #W
PiLength   = 0.24 #ms
# Resonance frequencies
FreqP2 = 58.560e6 # Hz, +2 sideband
FreqP1 = 58.575e6 # Hz, +1 sideband
Freq0  = 58.590e6 # Hz, carrier
FreqM1 = 58.605e6 # Hz, -1 sideband
FreqM2 = 58.620e6 # Hz, -2 sideband

# calculate some stuff
Frequency = np.arange(StartingFrequency, StoppingFrequency+FrequencyStepSize/2.0, \
                       FrequencyStepSize) # in Hz
#NumberOfFiles = len(Frequency)
#NumberOfFiles = len(Power)
NumberOfFiles = len(PulseLength)
#NumberOfFiles = len(WaitTimes)
#NumberOfFiles = len(Phases)

# Generate file names
Filenames = range(0,NumberOfFiles)
#startPosition=int((StartingFrequency-58.0e6)/1000)
for i in xrange(0,NumberOfFiles):
    Filenames[i] = FilenameHead + '-%03d'% (i+1) # +'.txt'
#    Filenames[i] = FilenameHead + '-%03d'% (startPosition+i*FrequencyStepSize/1000) # +'.txt'
Coolfilename = FilenameHead+'-Cool'
MeasListFilename = FilenameHead+'-Meas'
ScanFilename = FilenameHead+'.scan'
	
ListFilename = FilenameHead +'.lst'
print (ListFilename)

# Write Cooling file
pulsefile = open(Coolfilename, "wb") # open pulse file
pulsefile.write(FileComment) # write comment line
writer = csv.writer(pulsefile, dialect='excel-tab') # define the file format
# Order of parameters: [Freq, HSR, Length, Power, Type, Comment]
writer.writerow([58.5e6, 0.0, 5.0, 0., 3, 'Dummy']) # Dummy pulse
#writer.writerow([1000, 1, 2.0, 0., 2, 'Dummy']) # Dummy pulse

####### Begin cooling sequence definition #######
# Typical cooling sequence (-2, -1)
for i in xrange(0,25): #Cooling sequence
	writer.writerow([58.622e6, -8.0e3, AFPLength, AFPPower, 1, 'X-2 pulse %d'%(i+1)]) # -2 cooling pulse
	writer.writerow([58.607e6, -6.0e3, AFPLength, AFPPower, 1, 'X-1 pulse %d'%(i+1)]) # -1 cooling pulse
	writer.writerow([58.624e6, -8.0e3, AFPLength, AFPPower, 1, 'Y-2 pulse %d'%(i+1)]) # -2 cooling pulse
	writer.writerow([58.608e6, -6.0e3, AFPLength, AFPPower, 1, 'Y-1 pulse %d'%(i+1)]) # -1 cooling pulse
	writer.writerow([58.623e6, -8.0e3, AFPLength, AFPPower, 1, 'Z-2 pulse %d'%(i+1)]) # -2 cooling pulse
	writer.writerow([58.607e6, -6.0e3, AFPLength, AFPPower, 1, 'Z-1 pulse %d'%(i+1)]) # -1 cooling pulse
for i in xrange(0,10): #last 10 cycles only -1 pulse
	writer.writerow([58.622e6, -8.0e3, AFPLength, AFPPower, 1, 'X-2 pulse %d'%(i+1)]) # -2 cooling pulse
	writer.writerow([58.607e6, -4.0e3, AFPLength, AFPPower, 1, 'X-1 pulse %d'%(i+1)]) # -1 cooling pulse
	writer.writerow([58.624e6, -8.0e3, AFPLength, AFPPower, 1, 'Y-2 pulse %d'%(i+1)]) # -2 cooling pulse
	writer.writerow([58.608e6, -4.0e3, AFPLength, AFPPower, 1, 'Y-1 pulse %d'%(i+1)]) # -1 cooling pulse
	writer.writerow([58.623e6, -8.0e3, AFPLength, AFPPower, 1, 'Z-2 pulse %d'%(i+1)]) # -2 cooling pulse
	writer.writerow([58.607e6, -4.0e3, AFPLength, AFPPower, 1, 'Z-1 pulse %d'%(i+1)]) # -1 cooling pulse

#Transfer to qubit states    
writer.writerow([58.591e6, -6.0e3, AFPLength, AFPPower, 1, '4-4 -> 3-3']) # 4-4 -> 3-3
writer.writerow([58.995e6, -6.0e3, AFPLength, AFPPower, 1, '3-3 -> 4-2']) # 3-3 -> 4-2
writer.writerow([59.400e6, -6.0e3, AFPLength, AFPPower, 1, '4-2 -> 3-1']) # 4-2 -> 3-1    
writer.writerow([59.804e6, -6.0e3, AFPLength, AFPPower, 1, '3-1 -> 4-0']) # 3-1 -> 4-0      
#writer.writerow([QubitFreq, 0, 0.12, DetectionPulsePower, 2, '4-0 -> 3-0']) # 4-0 -> 3-0      





#Echo pulses

#Clear hot atoms sequence

# writer.writerow([58.591e6, 6000., AFPLength, AFPPower, 1, 'Inversion']) #Invert F states
# writer.writerow([58.575e6, 6000., AFPLength, AFPPower, 1, 'Clear X'])  # Transfer hot atoms to F=4
# writer.writerow([58.575e6, 6000., AFPLength, AFPPower, 1, 'Clear Y']) #Transfer hot atoms to F=4
# writer.writerow([58.575e6, 6000., AFPLength, AFPPower, 1, 'Clear Z']) #Transfer hot atoms to F=4
# writer.writerow([58.591e6, 6000., AFPLength, AFPPower, 1, 'Inversion']) #F=3 to F=4

# Heating sequence

# for i in xrange(0,6,2): # Heating sequence
	# writer.writerow([FreqM1, 4.0e3, AFPLength, AFPPower, 1, 'Heating pulse %d'%(i+1)]) # "-1" heating pulse
	# writer.writerow([FreqP1, 4.0e3, AFPLength, AFPPower, 1, 'Heating pulse %d'%(i+2)]) # +1 heating pulse
#writer.writerow([58.588e6, 6.0e3, 10., AFPPower, 1, 'Inversion']) #Invert F states
#writer.writerow([FreqM1, 8.0e3, AFPLength, AFPPower, 1, 'Heating pulse %d'%(i+1)]) # "-1" heating pulse
#for i in xrange(0,1): #cooling
	#writer.writerow([FreqM2, -8.0e3, 3., AFPPower, 1, 'X-2 pulse %d'%(i+1)]) # -2 cooling pulse
	#writer.writerow([FreqM1, -4.0e3, 3., AFPPower, 1, 'X-1 pulse %d'%(i+1)]) # -1 cooling pulse
	#writer.writerow([FreqM2, -8.0e3, 3., AFPPower, 1, 'Y-2 pulse %d'%(i+1)]) # -2 cooling pulse
	#writer.writerow([FreqM1, -4.0e3, 3., AFPPower, 1, 'Y-1 pulse %d'%(i+1)]) # -1 cooling pulse
	#writer.writerow([FreqM2, -8.0e3, 3., AFPPower, 1, 'Z-2 pulse %d'%(i+1)]) # -2 cooling pulse
	#writer.writerow([FreqM1, -4.0e3, 3., AFPPower, 1, 'Z-1 pulse %d'%(i+1)]) # -1 cooling pulse
# for i in xrange(0,10): # Dummies
	# writer.writerow([FreqP1, AFPHSR, AFPLength, 0.0,      1, 'Dummy'])   #wait
	# writer.writerow([FreqP1, AFPHSR, AFPLength, 0.0,      1, 'Dummy'])   #wait
	# writer.writerow([FreqP1, AFPHSR, AFPLength, 0.0,      1, 'Dummy'])   #wait
	# writer.writerow([FreqP1, AFPHSR, AFPLength, 0.0,      1, 'Dummy'])   #wait
	# writer.writerow([FreqP1, AFPHSR, AFPLength, 0.0,      1, 'Dummy'])   #wait
	# writer.writerow([FreqP1, AFPHSR, AFPLength, 0.0,      1, 'Dummy'])   #wait

# First 2 pulses of spin echo sequence
#writer.writerow([QubitFreq, 0, DetectionPulseLength, DetectionPulsePower, 2, 'Pi/2 pulse'])  
#writer.writerow([QubitFreq, 0, DetectionPulseLength*2, DetectionPulsePower, 2, 'Pi pulse'])   

pulsefile.close() # Close the cooling pulse file

os.system('copy '+Coolfilename+' Cool')
#os.system('C:\Users\Yang\Documents\Data\DDScontrol\NewDDS2-Cooling2.0-Cal.exe Cool')
subprocess.call(['C:\Users\Yang\Documents\Data\DDScontrol\NewDDS2-Cooling2.0-Cal.exe', 'Cool'])
print('After making Cool')

# begin loop to write the detection pulse files    
measfile = open(MeasListFilename, "wb")                  
measfile.write(FileComment)                  
writerm = csv.writer(measfile, dialect='excel-tab')
for i in xrange(0,NumberOfFiles):
    pulsefile = open(Filenames[i], "wb") # open pulse file
    pulsefile.write(FileComment) # write comment line
    writer = csv.writer(pulsefile, dialect='excel-tab') # define the file format

    # # Measurement pulse
    # writer.writerow([Frequency[i], \
                    # DetectionPulseHSR, \
                    # DetectionPulseLength, \
                    # DetectionPulsePower, \
                    # DetectionPulseType, \
                    # 'Measure'])
    # writer.writerow([QubitFreq, \
                    # DetectionPulseHSR, \
                    # DetectionPulseLength, \
                    # Power[i], \
                    # DetectionPulseType, \
                    # 'Measure'])
    writer.writerow([PiFreq, \
                    DetectionPulseHSR, \
                    PulseLength[i], \
                    DetectionPulsePower, \
                    DetectionPulseType, \
                    'Measure'])
    # writer.writerow([QubitFreq, \
                     # WaitTimes[i], \
                     # DetectionPulseLength, \
                     # DetectionPulsePower, \
                     # DetectionPulseType, \
                     # 'Measure'])
    # writer.writerow([QubitFreq, \
                     # Phases[i], \
                     # DetectionPulseLength, \
                     # DetectionPulsePower, \
                     # DetectionPulseType, \
                     # 'Measure'])
    writer.writerow([PiFreq, 0, Pi40To31/2, DetectionPulsePower, 2, '3-1 -> 4-0']) # 3-1 -> 4-0
    writer.writerow([PiFreq, 0.5, Pi30To41, DetectionPulsePower, 2, '3-1 -> 4-0']) # 3-1 -> 4-0
    writer.writerow([PiFreq, 0, Pi40To31/2, DetectionPulsePower, 2, '3-1 -> 4-0']) # 3-1 -> 4-0
    pulsefile.close() # Close the pulse file
    writerm.writerow([Filenames[i]])
    # writerm.writerow([QubitFreq, \
                    # DetectionPulseHSR, \
                    # DetectionPulseLength, \
                    # Power[i], \
                    # DetectionPulseType, \
                    # 'Measure'])
    # writerm.writerow([Frequency[i], \
                    # DetectionPulseHSR, \
                    # DetectionPulseLength, \
                    # DetectionPulsePower, \
                    # DetectionPulseType, \
                    # 'Measure'])
    writerm.writerow([PiFreq, \
                    DetectionPulseHSR, \
                    PulseLength[i], \
                    DetectionPulsePower, \
                    DetectionPulseType, \
                    'Measure'])
    # writerm.writerow([QubitFreq, \
                     # WaitTimes[i], \
                     # DetectionPulseLength, \
                     # DetectionPulsePower, \
                     # DetectionPulseType, \
                     # 'Measure'])
    # writerm.writerow([QubitFreq, \
                     # Phases[i], \
                     # DetectionPulseLength, \
                     # DetectionPulsePower, \
                     # DetectionPulseType, \
                     # 'Measure'])
    writerm.writerow([PiFreq, 0, Pi40To31/2, DetectionPulsePower, 2, '3-1 -> 4-0']) # 3-1 -> 4-0
    writerm.writerow([PiFreq, 0.5, Pi30To41, DetectionPulsePower, 2, '3-1 -> 4-0']) # 3-1 -> 4-0
    writerm.writerow([PiFreq, 0, Pi40To31/2, DetectionPulsePower, 2, '3-1 -> 4-0']) # 3-1 -> 4-0
measfile.close()    

# for i in xrange(0,len(Frequency)):
    # print('Making pulsefile '+Filenames[i])
    # pulsefile = open(Filenames[i], "wb") # open pulse file
    # pulsefile.write(FileComment) # write comment line
    # writer = csv.writer(pulsefile, dialect='excel-tab') # define the file format

#    Measurement pulse
    # writer.writerow([Frequency[i], \
                    # DetectionPulseHSR, \
                    # DetectionPulseLength, \
                    # DetectionPulsePower, \
                    # DetectionPulseType, \
                    # 'Measure'])
    # pulsefile.close() # Close the pulse file
    # writerm.writerow([Filenames[i]])
    # writerm.writerow([Frequency[i], \
                    # DetectionPulseHSR, \
                    # DetectionPulseLength, \
                    # DetectionPulsePower, \
                    # DetectionPulseType, \
                    # 'Measure'])
# measfile.close()    

# begin to write the cooling pulse files   


# Write list file
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

#print('Current directory: '+os.getcwd())
subprocess.call(["C:\Users\Yang\Documents\Data\DDScontrol\stepDDS_cal2.bat", "List"])
#print('After batch file')
#os.system("C:\Users\Yang\Documents\Eclipse\NewDDS2-Cooling2.0\pulsefiles\stepDDS_copy.bat List")
#os.system("C:\Users\Yang\Documents\Eclipse\NewDDS2-Cooling2.0\pulsefiles\stepDDS_delete.bat List")
#os.system("del Cool List RAWCool")
if DelTempFiles == 1 :
	os.system("del Cool List RAWCool reset")	

listfile = open(ListFilename, "wb")
for j in xrange(0,NumberOfRepeats):
    for i in Filenames:
        listfile.write(i+'-final.txt\n')
listfile.close()                 
            
print("%d files"%(NumberOfFiles))
print("%d repeats"%(NumberOfRepeats))
print("%d scans total"%(NumberOfFiles*NumberOfRepeats))
                    
os.system("copy "+sys.argv[0]+" "+FilenameHead+".py") # save a copy of this python file
os.system("copy "+FilenameHead+".lst last.lst") # copy list file to last.lst
os.system("copy "+FilenameHead+".scan last.scan") # copy scan file to last.lst