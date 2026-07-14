# Write pulse files for NewDDS2-version3.exe
# Ted Corcovilos 20110308 (Rewrite for easier changes)
# NB: Check that all 'float' numbers contain an explicit decimal point

# import libraries

import sys, math
import csv         # for writing the pulse files
import numpy as np # to calculate the frequency steps
import os, subprocess          # calls to operating system
import string      # string manipulation

DelTempFiles = 1 # Clean up after we're done?

# define some constants
FilenameHead = 'Rabi'   # filenames will start with this (can include directory, but use forward slash)
FileComment = 'CoolTransfer\n'  # Comment line at head of pulse files (must end with \n)
print (FileComment)

################ 2018.08.06 ######################
f4= 	61287983.7+29.021e3	# 4,4->3,3   	   
f2p= 60981138.82-2.5e3+12.4e3		+12.7e3			# 3,3->42	   
f1p =60590952.61-1.1e3+7.4e3		+7.6e3		# 4,2->3,1         
f0p = 60198904.8+2.6e3+2.5e3		+2.5e3			# 3,1->4,0           
fclock = 60006297.8708+0.4e3-0.17047265e3+0.2e3-0.140e3	 # 2015.08.26

f4new = 58670667.8708 - 11e3+1e3 - 0.6e3 + 5.65e3 +1.27e3 - 5.05e3 +0.23 + 1.23e3 +1.21e3
#~ f4new = 58661697.8708+1.2e3-2.9e3+0.5e3-1.4e3+0.9e3+0.6e3-2e3-1330e3+53.8e3-0.4e3	#high field (double)

##### initiated on 2018.02.02 #####
##### microwave horn rotated and powers updated on 2018.02.06#########

f33to43new = 58919197.8708+0.5e3-0.5e3+2.1e3
#~ f43to32new = f4new + 383.4e3 + 1.0e3	+ 1.2e3			# 20180611
#~ f32to41new = f4new + 770.0e3 - 0.9e3 +1.7e3				# 20180611
#~ f41to30new = f4new + 1152.7e3 +1.4e3					# 20180611
fclock = 60006297.8708+0.4e3
fclock = 60006297.8708+0.4e3-0.17047265e3+0.2e3		# updated 20180731

#redefine frequencies in an invariant way: 44->33->42->31->40 path	# 20180613
f33to43new = (fclock-f4new)*1/7+f4new
f43to32new = (fclock-f4new)*2/7+f4new
f32to41new = (fclock-f4new)*4/7+f4new + 1.2e3 
f41to30new = (fclock-f4new)*6/7+f4new

f33to42new = f43to32new
f42to31new = f32to41new
f31to40new = f41to30new

# 44->33->42->31->40->30->41->32: the last freq has -1.2kHz correction compared to f32to41new # 20180613

P33to43new = 0.1445

P43to32new = 0.0405
P32to41new = 0.169 	# 20180613
#~ P41to30new = 0.098
P41to30new = 0.075	# 20180613

P33to42new = 0.507	# 20180608 
P42to31new = 0.098	# 20180608 
#~ P31to40new = 0.098
P31to40new = 0.075	# 20180611

Pclock = 0.061		# 20180612 added, for AFP

Pclock_Pi_240us = 0.1976 	# for Blackman 
##### initiated 2018.02.02 #####
 
HideUnusedSettings = 1
if (HideUnusedSettings == 1):
	#~ deltaf = 52.6316e3    #  f0 - f304M1 for matching the uwave phase, 2014.05.07
	f304P1=60060974-0.45e3-1.4e3		 # 30->4,1, low field 
	#~ P3040_200us_Pi=0.4096  # 2014-7-14, low field 
	#~ P3040_200us_Pi= 0.366  # 2014-8-11
	P3040_200us_Pi= 0.40328# 2014-8-27

	#~ P3040_200us_Pi=0.4 # 2014-7-14, low field 

	P304P1_200us=0.71  #2014-7-7
	P304P1_150us=1.332  #2014-7-8
	P304P1_100us=3.11  #2014-7-23
	P304P1_300us=0.308  #2014-7-24
	P3P14P1_150us=0.637  # 2014-8-12

	#~ dfZeeman= 53.097e3+1.25e3-14.7e3	#+  Zeeman spliting	# 2014.9.3
	#~ dfadd =  26.0e3   # AC shift due to addressing beam
	#~ dfZeeman=60e3	#+  Zeeman spliting	# 2014.91.5
	P3P14P1_150us=	0.784	#  2014.10.13
	P3040_200us_Pi=0.52   #  2014.9.26
	#~ dfZeeman	=65.3e3	#+  Zeeman spliting	# 2014.9.26
	#~ dfZeeman	=60.150e3	#+  Zeeman spliting	# 2014.10.11
	#~ dfZeeman=187180.6078 #2014.10.14 Strong Field
	#~ dfZeeman2 =375876.97216 #2014.10.14 Strong Field

	#~ dfZeeman=87.814e3  # Zeeman spliting	# 2014.10.15

	#~ dfZeeman=95854.96 # Zeeman spliting	# 2014.11.13
	dfZeeman=93347.06 # Zeeman spliting	# 2015.1.20
	#~ P3P14P1_120us=2.074 # 2014.11.16
	P3P14P1_120us=2.232 # 2014.11.26
	P4433_240= 0.1886547
	P4433_120= 0.831744
	#~ dfZeeman=371040  # for strong B field, 2015.3.17 
	dfZeeman=192920 +1.4e3 # for normal B field #2015.5.24
	dfZeeman=192920 +1.4e3-1.9e3 # for normal B field #2015.7.13
	dfZeeman=197785.83  # 2015.8.27
	# define the scan range
	#H beam shifte to the minus direction
test = 5e3	# 2017.02.03 Debug DDS


StartingFrequency = f4new	#+dfZeeman#+dfZeeman	# fclock# +dfZeeman-10e3#+7.5e3#*2#	-0.5e3	#fclock+2*dfZeeman		#+delta#-0.43e3#+0.7e3#+1.7e3 #61.378e6 #60.190e6 #59.995e6  #60.180e6 # Hz
StoppingFrequency = f4new	#+dfZeeman#+dfZeeman	#fclock # +dfZeeman-10e3#+7.5e3#*2#	-0.5e3	#fclock+2*dfZeeman		#+delta#-0.43e3#+0.7e3# +1.7e3#61.378e6  #60.210e6 #60.015e6  #60.210e6 
# 61.387e6 is the resonace of unshifted atoms
DetRepeats =9	# how many detection pulse do you want to repeat

##################################################
### CLOCK TRANSITION FREQ: 60.0068MHz ############
##################################################

FrequencyStepSize =2.0e3 # Hz
NumberOfRepeats   = 100		# Number of times to repeat the scan

# define the detection pulse
# Typical square pulse
DetectionPulseType   =1	#   # 1 for AFP, 2 for Blackman, 3 for CW (numbers like NewDDS)
DetectionPulseLength =1		  #0.15 #0.07*9 #0.15 #0.15 # 0.2 #0.2 # 3#0.2 # 0.2 #3#0.2 #6.0 # ms
DetectionPulsePower  =2.5	#2.94# 0.125 #0.125 #0.1 #0.4#1.5#0.96#0.24#0.96#0.16#
DetectionPulseHSR    = -12e3	#-4.0e3 #.0e3 #4.0e3 # Hz (only used for AFP pulses)


DetectionPulseType   =2		#1 for AFP, 2 for Blackman, 3 for CW (numbers like NewDDS)
DetectionPulseLength =0.12		#0.15 #0.07*9 #0.15 #0.15 # 0.2 #0.2 # 3#0.2 # 0.2 #3#0.2 #6.0 # ms
DetectionPulsePower  =0.3		#2.94# 0.125 #0.125 #0.1 #0.4#1.5#0.96#0.24#0.96#0.16#
DetectionPulseHSR    = 0		#-4.0e3 #.0e3 #4.0e3 # Hz (only used for AFP pulses)



#~ Power =  5.5*((np.arange(0.850, 0.870,0.002))**2)
#~ print(Power)
#~ Power = DetectionPulsePower*((np.arange(0.99, 1.01,  0.002)**2))
#~ Power = DetectionPulsePower*((np.arange(0.0, 1.02,  0.1)**2))
Power = DetectionPulsePower*((np.arange(0.9, 1.1,  0.02)**2))
#~ Power = DetectionPulsePower*((np.arange(0.6,   1.01, 0.04))**2)
print Power

# Typical AFP parameters below:
# DetectionPulseType   = 1  # 1 for AFP, 2 for Blackman, 3 fs	or square, 4 for end, 9 for CW
# DetectionPulseLength = 3 # ms
# DetectionPulsePower  = 6. # W
# DetectionPulseHSR    = 6.0e3 # Hz (only used for AFP pulses)

# Typical Blackman parameters below:
# DetectionPulseType   = 2   # 1 for AFP, 2 for Blackman, 3 for square (numbers like NewDDS)
# DetectionPulseLength = 0.3 # ms
# DetectionPulsePower  = 0.282 # W
# DetectionPulseHSR    = 4.0e3 # Hz (only used for AFP pulses)

# Some typical values

#~ fc   =   	61.405400e6   # base freq for cooling
#~ fc   = 	f4
# last updated: 2015-3-16
AFPPower1   = 1.6*0.2 # W
AFPPower2   = 1.6*0.8 # W
AFPLength 	 = 3.0 # ms
AFPHSR0    = -4.0e3      
AFPHSR1    = -6.0e3 # Hz
AFPHSR2    = -8.0e3 # Hz

fc     =  		61359552.7+3.4e3    #4-01-2015
FreqM1X = fc+ 15e3   #13.3e3-2e3   #10.2e3	# Hz, -1 sideband
FreqM2X = fc+ 30e3   #27.8e3-2e3  #22.3e3   # Hz, -2 sideband
FreqM1Y = fc+ 17e3	#10.7e3-2e3 #14.9e3    # Hz, -1 sideband
FreqM2Y = fc+ 32e3 	#-2e3 #29.5e3   # Hz, -2 sideband
FreqM1Z = fc+ 12e3   #	12.4e3-2e3  #8.5e3 # Hz, -1 sideband
FreqM2Z = fc+ 25e3   #28.4e3-2e3  #19.1e3 # Hz, -2 sideband

#~ FreqM1ZS = fc+8e3  # final -1 pulse

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
ScanFilename = FilenameHead+'.scan'
	
ListFilename = FilenameHead +'.lst'
print (ListFilename)

# Write Cooling file
pulsefile = open(Coolfilename, "wb") # open pulse file
pulsefile.write(FileComment) # write comment line
writer = csv.writer(pulsefile, dialect='excel-tab') # define the file format

#########################################################

#~ writer.writerow([58.0e6, 0.0, 10.0, 0., 1, 'Dummy']) # Dummy pulse

##### initiated 2018.02.02 #####
#~ writer.writerow([f4new, -8e3, 3.0, 0.038*64/36, 1, '4,-4 -> 3,-3']) 
#~ writer.writerow([f33to43new, -8e3, 3.0, P33to43new*64/36, 1, '3,-3 -> 4,-3']) 
#~ writer.writerow([f43to32new, -6e3, 3.0, P43to32new, 1, '4,-3 -> 3,-2']) 
#~ writer.writerow([f32to41new, -6e3, 3.0, P32to41new, 1, '3,-2 -> 4,-1']) 

#~ writer.writerow([58.0e6, 0.0, 3.0, 0., 1, 'Dummy']) # Dummy pulse
#~ writer.writerow([f33to42new, -8e3, 3.0, P33to42new*64/36, 1, '3,-3 -> 4,-2']) 
#~ writer.writerow([f42to31new, -8e3, 3.0, P42to31new*64/36, 1, '4,-2 -> 3,-1']) 
#~ writer.writerow([f31to40new, -8e3, 3.0, P31to40new*64/36, 1, '3,-1 -> 4,0'])
#~ writer.writerow([fclock,		-8e3, 3.0, Pclock*64/36, 	   1, '4,0 -> 3,0']) 
#~ writer.writerow([f42to31new, -8e3, 3.0, P42to31new*64/36, 1, '4,-2 -> 3,-1']) 
#~ writer.writerow([f4new, 	-8e3, 3.0, 0.038*64/36, 	   1, '4,-4 -> 3,-3']) 


##### initiated 2018.02.02 #####

#~ writer.writerow([0.1e6, 0.0, 0.04 , 3.214944  ,      3, 'PI']) # 
#~ writer.writerow([0.1e6, 0.0, 0.040 , 3.223734   ,      3, 'PI']) # 
#~ writer.writerow([0.1e6, 0.0, 0.040 , 3.232536  ,      3, 'PI']) # 
#~ writer.writerow([0.1e6, 0.0, 0.040 ,3.24135  ,      3, 'PI']) # 
#~ writer.writerow([0.1e6, 0.0, 0.040 , 3.250176   ,      3, 'PI']) # 
#~ writer.writerow([0.1e6, 0.0, 0.040 , 3.259014  ,      3, 'PI']) # 
#~ writer.writerow([0.1e6, 0.0, 0.040 ,3.267864 ,      3, 'PI']) # 

#########################################################


pulsefile.close() # Close the cooling pulse file

os.system('copy '+Coolfilename+' Gate')
#os.system('C:\Users\Yang\Documents\Data\DDScontrol\NewDDS2-Cooling2.0-Cal.exe Cool')
subprocess.call(['C:\Users\Yang\Documents\Data\DDScontrol\NewDDS2-Cooling2.0-Cal.exe', 'Gate'])
print('After making Cool')

# begin loop to write the detection pulse files    
measfile = open(MeasListFilename, "wb")                  
measfile.write(FileComment)                  
writerm = csv.writer(measfile, dialect='excel-tab')
#for i in xrange(0,len(Frequency)):
for i in xrange(0,len(Power)):
    print('Making pulsefile '+Filenames[i])
    pulsefile = open(Filenames[i], "wb") # open pulse file
    pulsefile.write(FileComment) # write comment line
    writer = csv.writer(pulsefile, dialect='excel-tab') # define the file format

    for x in xrange(0,DetRepeats):
        writer.writerow([StartingFrequency, \
			DetectionPulseHSR, \
			DetectionPulseLength, \
			Power[i], \
			DetectionPulseType, \
			'Measure'])
    pulsefile.close() # Close the pulse file
    writerm.writerow([Filenames[i]])
    for x in xrange(0,DetRepeats):
        writerm.writerow([StartingFrequency, \
                        DetectionPulseHSR, \
                        DetectionPulseLength, \
                        Power[i], \
                        DetectionPulseType, \
                        'Measure'])
measfile.close()    

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
subprocess.call(["C:\Users\Yang\Documents\Data\DDScontrol\stepDDS_cal3.bat", "List"])
#print('After batch file')
#os.system("C:\Users\Yang\Documents\Eclipse\NewDDS2-Cooling2.0\pulsefiles\stepDDS_copy.bat List")
#os.system("C:\Users\Yang\Documents\Eclipse\NewDDS2-Cooling2.0\pulsefiles\stepDDS_delete.bat List")
#os.system("del Cool List RAWCool")
if DelTempFiles == 1 :
	os.system("del Cool List reset")

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