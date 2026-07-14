# Write pulse files for NewDDS2-version3.exe
# Ted Corcovilos 20110308 (Rewrite for easier changes)
# NB: Check that all 'float' numbers contain an explicit decimal point

# import libraries
import sys, math
import csv # for writing the pulse files
import numpy as np # to calculate the frequency steps
import os
import string

DelTempFiles = 1 # Clean up after we're done?

# define some constants
FilenameHead = 'power'   # filenames will start with this (can include directory, but use forward slash)
FileComment = '29 pulse cooling (-2,-1), clear hot, square detect AFP detect\n'  # Comment line at head of pulse files (must end with \n)
print (FileComment)

# define the scan range
#StartingFrequency = 58.596e6 # Hz
#StartingFrequency = 58.580e6 # Hz
#StoppingFrequency = 58.596e6
#FrequencyStepSize = 2.0e3 # Hz
NumberOfRepeats   = 1 # Number of times to repeat the scan

# define the detection pulse
DetectionPulseType   = 3   # 1 for AFP, 2 for Blackman, 3 for CW (numbers like NewDDS)
DetectionPulseLength = 0.240 # ms
DetectionPulsePower  = 0.060 # W
DetectionPulseHSR    = 4.0e3 # Hz (only used for AFP pulses)

Power = 6.*sqrt(np.arange(0, 1.01,0.05))

Freq = 58.575e6

# Typical Blackman parameters below:
# DetectionPulseType   = 2   # 1 for AFP, 2 for Blackman, 3 for CW (numbers like NewDDS)
# DetectionPulseLength = 0.3 # ms
# DetectionPulsePower  = 0.282 # W
# DetectionPulseHSR    = 4.0e3 # Hz (only used for AFP pulses)

# Some typical values
AFPPower = 0.7 # W
AFPLength = 3.0 # ms
AFPHSR = 4.0e3 # Hz
FreqP2 = 58.561e6 # Hz, +2 sideband
FreqP1 = 58.575e6 # Hz, +1 sideband
Freq0  = 58.589e6 # Hz, carrier
FreqM1 = 58.603e6 # Hz, -1 sideband
FreqM2 = 58.617e6 # Hz, -2 sideband

# calculate some stuff
Frequency = np.arange(StartingFrequency, StoppingFrequency+FrequencyStepSize/2.0, \
                      FrequencyStepSize) # in Hz
#NumberOfFiles = len(Frequency)
NumberOfFiles = len(Power)

# Generate file names
Filenames = range(0,NumberOfFiles)
for i in xrange(0,NumberOfFiles):
    Filenames[i] = FilenameHead + '-%03d'% (i+1) # +'.txt'
Coolfilename = FilenameHead+'-Cool'
MeasListFilename = FilenameHead+'-Meas'
	
ListFilename = FilenameHead +'.lst'
print (ListFilename)

# Write Cooling file
pulsefile = open(Coolfilename, "wb") # open pulse file
pulsefile.write(FileComment) # write comment line
writer = csv.writer(pulsefile, dialect='excel-tab') # define the file format
# Order of parameters: [Freq, HSR, Length, Power, Type, Comment]
writer.writerow([58.5e6, 0.0, 5.0, 0.0, 3, 'Dummy']) # Dummy pulse

####### Begin cooling sequence definition #######
# Typical cooling sequence (-2, -1)
# for i in xrange(0,24): #Cooling sequence
	# writer.writerow([FreqM2, 8.0e3, AFPLength, AFPPower, 1, 'X-2 pulse %d'%(i+1)]) # -2 cooling pulse
	# writer.writerow([FreqM1, 4.0e3, AFPLength, AFPPower, 1, 'X-1 pulse %d'%(i+1)]) # -1 cooling pulse
	# writer.writerow([FreqM2, 8.0e3, AFPLength, AFPPower, 1, 'Y-2 pulse %d'%(i+1)]) # -2 cooling pulse
	# writer.writerow([FreqM1, 4.0e3, AFPLength, AFPPower, 1, 'Y-1 pulse %d'%(i+1)]) # -1 cooling pulse
	# writer.writerow([FreqM2, 8.0e3, AFPLength, AFPPower, 1, 'Z-2 pulse %d'%(i+1)]) # -2 cooling pulse
	# writer.writerow([FreqM1, 4.0e3, AFPLength, AFPPower, 1, 'Z-1 pulse %d'%(i+1)]) # -1 cooling pulse
# for i in xrange(24,29): #last 5 cycles narrower -1 pulse
	# writer.writerow([FreqM2, 8.0e3, AFPLength, AFPPower, 1, 'X-2 pulse %d'%(i+1)]) # -2 cooling pulse
	# writer.writerow([FreqM1, 4.0e3, AFPLength, AFPPower, 1, 'X-1 pulse %d'%(i+1)]) # -1 cooling pulse
	# writer.writerow([FreqM2, 8.0e3, AFPLength, AFPPower, 1, 'Y-2 pulse %d'%(i+1)]) # -2 cooling pulse
	# writer.writerow([FreqM1, 4.0e3, AFPLength, AFPPower, 1, 'Y-1 pulse %d'%(i+1)]) # -1 cooling pulse
	# writer.writerow([FreqM2, 8.0e3, AFPLength, AFPPower, 1, 'Z-2 pulse %d'%(i+1)]) # -2 cooling pulse
	# writer.writerow([FreqM1, 4.0e3, AFPLength, AFPPower, 1, 'Z-1 pulse %d'%(i+1)]) # -1 cooling pulse
# Clear hot atoms sequence
# writer.writerow([Freq0,  AFPHSR, AFPLength, AFPPower, 1, 'Inversion']) #Invert F states
# writer.writerow([FreqP1, AFPHSR, AFPLength, AFPPower, 1, 'Clear X'])  # Transfer hot atoms to F=4
# writer.writerow([FreqP1, AFPHSR, AFPLength, 0.0,      1, 'Dummy'])   #wait
# writer.writerow([FreqP1, AFPHSR, AFPLength, AFPPower, 1, 'Clear Y']) #Transfer hot atoms to F=4
# writer.writerow([FreqP1, AFPHSR, AFPLength, 0.0,      1, 'Dummy'])   #wait
# writer.writerow([FreqP1, AFPHSR, AFPLength, AFPPower, 1, 'Clear Z']) #Transfer hot atoms to F=4
# # After clearing sequence all remaining atoms should be F=3 N=0
# # Heating sequence
# for i in xrange(0,6,2): # Heating sequence
	# writer.writerow([FreqM1, 4.0e3, AFPLength, AFPPower, 1, 'Heating pulse %d'%(i+1)]) # "-1" heating pulse
	# writer.writerow([FreqP1, 4.0e3, AFPLength, AFPPower, 1, 'Heating pulse %d'%(i+2)]) # +1 heating pulse
# writer.writerow([Freq0,  AFPHSR, AFPLength, AFPPower, 1, 'Inversion']) #Invert F states
# for i in xrange(0,10): #cooling
	# writer.writerow([FreqM2, 8.0e3, AFPLength, AFPPower, 1, 'X-2 pulse %d'%(i+1)]) # -2 cooling pulse
# #	writer.writerow([FreqM1, 4.0e3, AFPLength, AFPPower, 1, 'X-1 pulse %d'%(i+1)]) # -1cooling pulse
	# writer.writerow([FreqM1, 0.0e3, 0.3, 0.282, 3, 'X-1 pi pulse %d'%(i+1)]) # -1cooling pulse
	# writer.writerow([FreqM2, 8.0e3, AFPLength, AFPPower, 1, 'Y-2 pulse %d'%(i+1)]) # -2 cooling pulse
# #	writer.writerow([FreqM1, 4.0e3, AFPLength, AFPPower, 1, 'Y-1 pulse %d'%(i+1)]) # -1 cooling pulse
	# writer.writerow([FreqM1, 0.0e3, 0.3, 0.282, 3, 'X-1 pi pulse %d'%(i+1)]) # -1cooling pulse
	# writer.writerow([FreqM2, 8.0e3, AFPLength, AFPPower, 1, 'Z-2 pulse %d'%(i+1)]) # -2 cooling pulse
# #	writer.writerow([FreqM1, 4.0e3, AFPLength, AFPPower, 1, 'Z-1 pulse %d'%(i+1)]) # -1 cooling pulse
	# writer.writerow([FreqM1, 0.0e3, 0.3, 0.282, 3, 'X-1 pi pulse %d'%(i+1)]) # -1cooling pulse
pulsefile.close() # Close the cooling pulse file

os.system('copy '+Coolfilename+' Cool')
os.system('C:\Users\Yang\Documents\Data\DDScontrol\NewDDS2-Cooling2.0-Cal.exe Cool')

# begin loop to write the detection pulse files    
measfile = open(MeasListFilename, "wb")                  
measfile.write(FileComment)                  
writerm = csv.writer(measfile, dialect='excel-tab')
#for i in xrange(0,len(Frequency)):
for i in xrange(0,len(Power)):
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
    writer.writerow([Freq, \
                    DetectionPulseHSR, \
                    DetectionPulseLength, \
                    Power[i], \
                    DetectionPulseType, \
                    'Measure'])
    pulsefile.close() # Close the pulse file
    writerm.writerow([Filenames[i]])
    writerm.writerow([Freq, \
                    DetectionPulseHSR, \
                    DetectionPulseLength, \
                    Power[i], \
                    DetectionPulseType, \
                    'Measure'])
    # writerm.writerow([Frequency[i], \
                    # DetectionPulseHSR, \
                    # DetectionPulseLength, \
                    # DetectionPulsePower, \
                    # DetectionPulseType, \
                    # 'Measure'])
measfile.close()    

# begin to write the cooling pulse files   

						
# Write list file
listfile = open('List', "wb")
for i in Filenames:
    listfile.write(i+'\n')
listfile.close()


os.system("C:\Users\Yang\Documents\Data\DDScontrol\stepDDS_cal2.bat List")
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