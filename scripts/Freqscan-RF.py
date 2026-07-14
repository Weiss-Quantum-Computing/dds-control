#~ # Write pulse files for NewDDS2-version3.exe
# Ted Corcovilos 20110308 (Rewrite for easier changes)
# NB: Check that all 'float' numbers contain an explicit decimal point

# import libraries

import sys, math
import csv         # for writing the pulse files
import numpy as np # to calculate the frequency steps
import os, subprocess          # calls to operating system
import string      # string manipulation
from scipy.optimize import fsolve  # solve for magnetic field by transition frequncy

DelTempFiles = 1 # Clean up after we're done?

# define some constants
FilenameHead = 'Freqscan-RF'   # filenames will start with this (can include directory, but use forward slash)
FileComment = 'Cool\n'  # Comment line at head of pulse files (must end with \n)
print (FileComment)


################ 2019.05.02 #####################
#~ f4= 	61287983.7+29.021e3	# 4,4->3,3     	   
#~ f2p= 60981138.82-2.5e3+12.4e3		+12.7e3			# 3,3->42	   
#~ f1p =60590952.61-1.1e3+7.4e3		+7.6e3		# 4,2->3,1         
#~ f0p = 60198904.8+2.6e3+2.5e3		+2.5e3			# 3,1->4,0           
#~ fclock=60006762.1922+0.08749786e3 -0.15e3-0.06e3  -0.49015465e3	 # 2015.08.26
f4newH = 56595100 
f4newL = f4newH + 2.032e6 + 46e3 + 290  # low field to check the unexplained spin echo phase shift 2025.01.23
f4new = f4newH -265

# f4newH for magnetic field measurement 
f4newx = f4new + 200e3 + 7e3 - 614 - 15e3 + 132	 # for field  (997, 0, -84)
f4newHy = 57615738.1  - 43.4e3 + 6e3    # for field  (0, 975, -38)
print(f4new)

#~ f4new =f4new+1e3
#~ f4new = 58661697.8708+1.2e3-2.9e3+0.5e3-1.4e3+0.9e3+0.6e3-2e3-1330e3+53.8e3-0.4e3	#high field (double)


####################################
# calculate B field and transition frequencies 2023.09.20
delta2 = 200e3
gI = -0.000398853
gJ = 2.0025403
muB = 1.3996246e6
b_trial = 1.393
fhfs = 9.192631770e9
fmix = 9.1326249676e9
# f4newHLower = f4newH -2e3  to avoid some resonances in the RF coil?

HideBRCal=1
if (HideBRCal==1):
	def flevel(F,mf,B):
	    """
	    Parameters
	    ----------
	    mF : Hyerfine sublevel
	    B : Magnetic field unit(G)
		DESCRIPTION
		This function uses Breit-Rabi formula to calculate energy level
	    Returns
	    The energy level as function of magnetic field
	    -------
	    """
	    if F == 4:
		    eqn = fhfs * ( -1.0/16.0 + mf * gI * muB * B/fhfs + \
		    1.0/2.0 * math.sqrt(1 + 4 * mf * (gJ - gI) * muB * B/(8*fhfs) + ( (gJ-gI) * muB * B / fhfs)**2))
	    elif F == 3:
		    eqn = fhfs*(-1.0/16.0 + mf*gI*muB*B/fhfs - \
				1.0/2.0 * math.sqrt(1 + 4 * mf * (gJ - gI) * muB * B/(8*fhfs) +\
					     ((gJ-gI) * muB * B / fhfs)**2))
	    else: print('wrong F number!')
	    
	    return eqn

	def get_b_field(z):

	    B = z[0]
	    F = np.empty((1))
	    F[0] = flevel(4, -4, B) - flevel(3, -3, B) - f4new - fmix 
	   
	    return F
	def get_uw_freq(mF4, mF3):    
	    """
	    Calculate the microwave frequency for microwave transition.
	    mF4 is the mf number for F= 4 state, likewise for mF3.
	    """
	    B = fsolve(get_b_field,1.39)
	    fuw = flevel(4, mF4, B) - flevel(3, mF3, B) - fmix
	    
	    return fuw
	    
	def get_uw_freq2():    
	    """
	    Calculate the microwave frequency for 2-photon transition.
	    """
	    B = fsolve(get_b_field,1.39)
	    fuw = flevel(4, 1, B) - flevel(3, 0, B) - fmix - delta2
	    
	    return fuw

	def get_rf_freq():    
	    
	    B = fsolve(get_b_field,1.39)
	    frf = flevel(3, -1, B) - flevel(3, 0, B) - delta2
	    
	    return frf

	####################################
	 

##### initiated on 2018.02.02 #####
##### microwave horn rotated and powers updated on 2018.02.06#########
fclock = 60006297.8708+0.4e3-0.17047265e3+0.2e3-0.140e3+0.215e3 + 0.72e3		# updated 20180806

# Define frequency with f4new and  Hyperfine splitting (fclock)        #20230920
f33to43new = get_uw_freq(-3,-3)[0]
f43to32new = get_uw_freq(-3,-2)[0]
f32to41new = get_uw_freq(-1,-2)[0] - 100
f41to30new = get_uw_freq(-1,-0)[0]
f40to3P1new = get_uw_freq(0,1)[0]
f3P1to4P1new = get_uw_freq(1,1)[0] - 110
f4P1to3P2new = get_uw_freq(1,2)[0]
f3P2to4P3new = get_uw_freq(3,2)[0]
f3P2to4P2new = get_uw_freq(2,2)[0]
f4P3to3P3new = get_uw_freq(3,3)[0]

f33to42new = get_uw_freq(-2,-3)[0]  - 100
f42to31new = get_uw_freq(-2,-1)[0]  
f31to40new = get_uw_freq(0,-1)[0]
f31to41new = get_uw_freq(-1,-1)[0]

#~ f31to40newH = (fclock-f4newH)*6/7+f4newH  # Definition value
#~ f31to40newH =f4newH +2.92797e6                           # theoretical value under the high field
# 20180803
f32to41newShortSpinEcho = (fclock-f4new)*4/7+f4new + 1.2e3 -3.21e3+0.3e3+0.1e3+0.1e3
f42to31newShortSpinEcho = f32to41newShortSpinEcho

# 44->33->42->31->40->30->41->32: the last freq has -1.2kHz correction compared to f32to41new # 20180613

P44to33new = 0.025
P33to43new = 0.1445
P43to32new = 0.0405
P32to41new = 0.169 	# 20180613
#~ P41to30new = 0.098
P41to30new = 0.075	# 20180613

P33to42new = 0.55	# 20180608 
P42to31new = 0.085	# 20180608 
#~ P31to40new = 0.098
P31to40new = 0.09	# 20180611
P40to3P1new = 0.075	# 20210910
P3P1to4P1new = 0.096 	# 20210910
P4P1to3P2new = 0.175
P3P2to4P3new = 0.0495

Pclock = 0.061		# 20180612 added, for AFP

Pclock_Pi_240us = 0.1976 	# for Blackman 
Pclock_Pi_120us =0.8019 	# for Blackman 
Pclock_Pi_200us  = 0.2843	# for Blackman  20180801
Pclock_Pi_80us  = 1.8578	# for Blackman  20180801
Pclock_PiHalf_80us  = 1.8415	# for Blackman  20180801
Pclock_Pi_120us =0.8150
P3P1to4P1_B = 0.318*7/15*1.2
##### initiated 2018.02.02 #####

def rf_Power_Calib(f):
    """
    Parameters
    ----------
    f : frequency of RF [Hz]  good for (280,300) kHz
        DESCRIPTION
        This function is used to cancel out RF power's dependence on frequency.
    Returns
    pscle : the power scale factor for frequency f
    -------
    """
    x = f * 1e-5 
    temp_scale = -253.547 + 286.518*x - 108.084*x**2 + 13.6582*x**3
    pscale = temp_scale**(-2)
    return pscale


####################

HideUnusedSettings = 1
if (HideUnusedSettings == 1):
	f11=60200304.8   # 3,1->4,1 calculated
	#~ deltaf = 52.6316e3    #  f0 - f304M1 for matching the uwave phase, 2014.05.07
	f304P1=60060974-0.45e3-1.4e3		 # 30->4,1, low field 
	#~ P3040_200us_Pi=0.4096  # 2014-7-14, low field 
	#~ P3040_200us_Pi= 0.366  # 2014-8-11
	#~ P3040_200us_Pi= 0.40328# 2014-8-27
	#~ P3040_200us_Pi=	0.409  # 2014-9-3
	P3040_200us_Pi=  0.442895829  # 9.15

	#~ P3040_200us_Pi=0.4 # 2014-7-14, low field 

	P304P1_200us=0.71  #2014-7-7
	P304P1_150us=1.332  #2014-7-8
	P304P1_100us=3.11  #2014-7-23
	P304P1_300us=0.308  #2014-7-24
	P3P14P1_150us=0.637  # 2014-8-12

	#~ P3P14P1_150usHalf= 0.2274 # 2014-9-5
	P3P14P1_150usHalf= 0.2146 # 2014-9-15

	#~ dfZeeman=39.674e3	#+  Zeeman spliting	# 2014.9.5
	dfadd =  26.0e3   # AC shift due to addressing beam
	#~ dfZeeman=60e3	#+  Zeeman spliting	# 2014.91.5

	delta=86.869e3 #  (For dfadd =  27e3) 2014.9.16


	#~ P3P14P1_150us=1.555  	# 2014-9-22
	#~ P304P1_300us=0.605   	# 2014-9-22
	#~ P3040_200us_Pi= 0.8	# 2014-9-22

	#~ P3040_200us_Pi=0.52   #  2014.9.26
	P3040_200us_Pi=0.4  # 2014.10.10
	P3040_200us_Pi= 0.4016  # 2014.10.15
	P3P14P1_150us=	0.8427	#  2014.9.26
	P3P14P1_80us=	3.33   # 2014.10.21
	P3P14P1_60us=	5.53   # 2014.10.21
	#~ P3P14P1_150us=	0.794	#  2014.10.14
	#~ P304P1_300us= 0.3655 	#  2014.9.26
	P304P1_300us=  	0.372  #  2014.10.16
	#~ dfZeeman	=65770#+  Zeeman spliting	# 2014.9.29
	#~ dfZeeman	=60.150e3	#+  Zeeman spliting	# 2014.10.11

	#~ dfZeeman=60.721e3  # Zeeman spliting	# 2014.10.13
	#~ dfZeeman=95854.96 # Zeeman spliting	# 2014.11.13
	#~ dfZeeman=187180.6078 #2014.10.14 Strong Field
	#~ dfZeeman2 =375876.97216 #2014.10.14 Strong Field
	#~ dfZeeman=187.146e3   # 2014.10.14  Zeeman
	#~ delta=dfZeeman	#+28e3	#-0.5e3

	#~ dfZeeman=93347.06 # Zeeman spliting	# 2015.1.20

	dfZeeman=200886-0.6e3	# for normal B field #2015.9.9
	#~ dfZeeman=371040 - 2.3e3  # for strong B field, 2015.3.17 

	#~ P304P1_150us=1.28         # 2014.9.29

	#~ P3040_200us_Pi= 0.4761  # 2014.11.4
	#~ P3040_100us_Pi=1.917  # 2014.11.6
	#~ P3040_200us_Pi=0.6889 # 2014.11.9
	#~ P3040_200us_Pi=0.6937  # 2014.11.13

	P304P1_300us=  	0.585  #  2014.11.13
	P3P14P1_120us=2.074 # 2014.11.16
	#~ P304P1_300us=  	0.5  #  2014.11.21

	P3P14P1_120us=2.232 # 2014.11.26
	P3040_200us_Pi=0.7396  # 2014.11.25
	P304P1_300us=  	0.47  #  2014.11.26
	P304P1_600us=  	0.2047 #2014.12.10
	P3040_200us_Pi=0.7656  # 2015.01.08
	P3040_100us_Pi=3.1819  # 2015.01.09
	P3040_50us_Pi_square = 2.9756  # 2015.01.09
	P3040_75us_Pi = 6.067  # 2015.01.09
	P3040_50us_Pi_square = 3.35315 # 2015.01.12
	#~ P3040_90us_Pi = 4.12168 # 2015.01.13
	#~ P3040_90us_Pi = 4.014 # 2015.01.14-0.125
	#~ P3040_90us_Pi = 4.0235 # 2015.01.15
	#~ P3040_90us_Pi =  3.85786313 #2015.04.24 normal B field 400mG

	P3040_90us_Pi= 3.3525#2015.05.7
	P3040_30us_Pi_Square=3.2  # 2015.5.10, pi pulse power for 30use pulse
	P3040_90us_Pi= 3.3525	#2015.05.7
	P3040_80us_Pi=2.84  # 2015-5-17

	P304P1_120us=1.738   # 2015.5.22
	P304P1_240us=0.396   # 2015.5.25

	#~ P4433_240= 0.1886547	# 2017.1.16
	#~ P4433_120= 0.831744 # 2017.1.16
	P4433_240=0.06	# 2017.5.11
	P4433_120= 0.1964 # 2017.10.16
	P4433_80 = 0.4667792 # 2017.10.26
	P304P1_300us=0.35  # 2015.9.1
	PM4433_240= 0.0678
fRF = get_rf_freq()[0]
test = 5e3	# 2017.02.03 Debug DDS
#~ centralF = f44to43newH -delta2 + 0.250e3 + 0.20e3 + 1.67e3 - 1.788e3 - 45

centralF = fRF  	#on 20220407

print(centralF)
#~ f44to43newH -1.3e3 -delta2 + 1.9e3

StartingFrequency =centralF - 2.5e3 #fclock+dfZeeman+40e30.2410
StoppingFrequency=centralF + 2.5e3

#~ StartingFrequency = 360e3	- 10e3 #fclock+dfZeeman+40e30.2410
#~ StoppingFrequency= 360e3	+10e3

#fclock+dfZeeman+60e3..
P=0.04
hsr =-8e3
DetRepeats =1	#24	# h3w many detection pulse do you want to repeat
##################################################
### CLOCK TRANSITION FREQ: 60.0068MHz ############
##################################################
#~ delta=StartingFrequency-fclock0
#~ print(StartingFrequency)

n= 1			#number of times to repeat the scanned pulse, but not any pulse before or after

FrequencyStepSize = 0.5e3			# 
NumberOfRepeats   = 1000		# Number of times to repeat the scan

# define the detection pulse-0..09
# Typical square pulse
DetectionPulseType   = 2		# 1 for AFP, 2 for Blackman, 9 for CW (no ending), 22 Composite Pi  3 square pulse(phase coherence)
DetectionPulseLength = 0.7		# 0.8
#~ DetectionPulsePower  =P31to40new
#~ DetectionPulsePower  =Pclock_Pi_120us

#~ DetectionPulsePower  = 0.225 		# // 0.373 Pi/2 pulse on 20210203
DetectionPulsePower  = 2.08		# 20240201  0.66
DetectionPulseHSR    = 0		#-4e3	 # Hz (only used for AFP pulse)

# for spin echo sequence
#~ DetectionPulseLength2 = 15.85 + 33.33 - 16.67		#For Ramsey
#~ DetectionPulseType2   = 3		# 1 for AFP, 2 for Blackman, 9 for CW (no ending), 22 Composite Pi  3 square pulse(phase coherence)
#~ DetectionPulseHSR2    = 0
#~ DetectionPulseHSR    = 0		#-4e3	 # Hz (only used for AFP pulses) 

# for Ramsey type (frequency jump)
DetectionPulseLength2 = 14		#For Ramsey
DetectionPulseType2   = 3		# 1 for AFP, 2 for Blackman, 9 for CW (no ending), 22 Composite Pi  3 square pulse(phase coherence)
DetectionPulseHSR2    = 0
	
# For Blackman and CW pulses, "HSR" is the phase in units of pi

# Blackman
#~ DetectionPulseType   = 2		# 1 for AFP, 2 for Blackman, 9 for CW (no ending), 22 Composite Pi  3 square pulse(phase coherence)
#~ DetectionPulseLength = 0.12		# typ 0.12 
#~ DetectionPulsePower  = 0.318 		
#~ DetectionPulseHSR    = 0		# 0Hz for blackman


#EmptyPulseLength for Supertime Spin Echo
EmptyPulseLength = 0.2


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

#~ Power = 15*((np.arange(0.55, 0.66,0.01))**2)
#~ print(Power)

#~ fc   =   	61.405400e6   # base freq for cooling
#~ fc   = 	f4
#~ fc   = 	f4

# last updated: 2015-4-29
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

# calculate some stuff
Frequency = np.arange(StartingFrequency, StoppingFrequency+FrequencyStepSize/2.0, \
                      FrequencyStepSize) # in Hz
print(rf_Power_Calib(Frequency))
NumberOfFiles = len(Frequency)

#~ Phase= np.arange (0,2.01,0.2)  #phase in units of pi
#~ NumberOfFile7+5coolis = len(Phase)

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
# Order of parameters: [Freq, HSR, Length, Power, Type, Comment]


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
#~ writer.writerow([fclock,		-8e3, 3.0, Pclock*64/36, 	 1, '4,0 -> 3,0']) 
#~ writer.writerow([f42to31new, -8e3, 3.0, P42to31new*64/36, 1, '4,-2 -> 3,-1']) 
#~ writer.writerow([f4new, 	-8e3, 3.0, 0.038*64/36, 1, '4,-4 -> 3,-3']) 

#~ writer.writerow([fclock,		0, 0.06, Pclock_Pi_120us, 	 2, '4,0 -> 3,0']) 
#~ writer.writerow([f41to30new, -8e3, 3.0, P41to30new*64/36, 1, '3,0-> 4,-1'])
#~ writer.writerow([f42to31new, -6e3, 3.0, 0.169, 1, '3,-1 -> 4,-2']) 

##### initiated 2018.02.02 #####


#~ P = 0.0
#~ writer.writerow([f4new, -8000, 3, 0.1,  1, '4,4->3,3'])
#~ for i in range(0,9):
	#~ writer.writerow([f4new, hsr, 3, 0.1,  1, '4,4->3,3']) # 2014.10.10, old power is 0.05W 
	#~ writer.writerow([f4new, hsr, 3, 0.1,  1, '4,4->3,3'])
#~ writer.writerow([f4new, hsr, 3, 0.1,  1, '4,4->3,3'])
#~ writer.writerow([f4new, -8000, 3, P,  1, '4,4->3,3'])
#~ writer.writerow([f2p, -6000, 3, 1.6*1.5*0.7,  1, '3,3->4,2']) # 2014.10.10: 1.5W 
#~ writer.writerow([f1p, -6000, 3, 1.6*0.3*0.7,  1, '4,2->3,1']) # 2014.10.10: 0.8W 
#~ writer.writerow([f0p, -6000, 3, 1.6*0.25*0.7,  1, '3,1->4,0']) # 2014.10.10: 025W 


#~ writer.writerow([fclock,0, 0.12,0,  2, 'dummy']) # 2014.10.10: 025W 

#~ for i in range(0,129):
	 #~ writer.writerow([fclock, 0, 0.03, P3040_30us_Pi_Square,  3, 'PI'])

#~ writer.writerow([fclock+dfZeeman, 0, 0.24, P304P1_240us,  2, 'test'])
#~ writer.writerow([fclock, -6000, 3, 1.6*0.7,  1, '3,0->4,0'])


pulsefile.close() # Close the cooling pulse file

#~ os.system('copy '+Coolfilename+' Gate')
#~ #os.system('C:\Users\Yang\Documents\Data\DDScontrol\NewDDS2-Cooling2.0-Cal.exe Cool')
#~ subprocess.call(['C:\Users\Yang\Documents\Data\DDScontrol\NewDDS2-Cooling2.0-Cal.exe', 'Gate'])
#~ print('After making Cool')

# begin loop to write the detection pulse files    
measfile = open(MeasListFilename, "wb")                  
measfile.write(FileComment)                  
writerm = csv.writer(measfile, dialect='excel-tab')
for i in xrange(0,len(Frequency)):
#~ for i in xrange(0,len(Phase)):
    print('Making pulsefile '+Filenames[i])
    pulsefile = open(Filenames[i], "wb") # open pulse file
    pulsefile.write(FileComment) # write comment line
    writer = csv.writer(pulsefile, dialect='excel-tab') # define the file format

    #~ # Measurement pulse
    #~ writer.writerow([StartingFrequency, \
                    #~ Phase[i], \
                    #~ DetectionPulseLength, \
                    #~ DetectionPulsePower, \
                    #~ DetectionPulseType, \
                    #~ 'Measure'])
    #~ pulsefile.close() # Close the pulse file
    #~ writerm.writerow([Filenames[i]])
    #~ writerm.writerow([StartingFrequency, \
                    #~ Phase[i], \
                    #~ DetectionPulseLength, \
                    #~ DetectionPulsePower, \
                    #~ DetectionPulseType, \
                    #~ 'Measure'])
    #~ writer.writerow([Frequency[i], 0.0, 7*0.04, 0.27, 2, 'Pi/2'])
    #~ writer.writerow([Frequency[i], 1.0, 5*0.04, 0.27, 2, 'Pi'])
    


#For Ramsey type 			 
    #~ for x in xrange(0,DetRepeats):
	#~ writer.writerow([0, 0.0, 10.0, 0., 1, 'Dummy']) # Dummy pulse
	#~ writer.writerow([Frequency[i], \
                        #~ DetectionPulseHSR, \
                        #~ DetectionPulseLength, \
                        #~ DetectionPulsePower, \
                        #~ DetectionPulseType, \
                        #~ 'Measure'])
	#~ writer.writerow([Frequency[i], \
                        #~ DetectionPulseHSR, \
                        #~ DetectionPulseLength2, \
                        #~ 0, \
                        #~ DetectionPulseType, \
                        #~ 'Measure'])
	#~ writer.writerow([Frequency[i], \
                        #~ DetectionPulseHSR2, \
                        #~ DetectionPulseLength, \
                        #~ DetectionPulsePower, \
                        #~ DetectionPulseType, \
                        #~ 'Measure'])
	#~ pulsefile.close() # Close the pulse file
	#~ writerm.writerow([Filenames[i]])
    #~ for x in xrange(0,DetRepeats):
	#~ writerm.writerow([0, 0.0, 10.0, 0., 1, 'Dummy']) # Dummy pulse
	#~ writerm.writerow([Frequency[i], \
                        #~ DetectionPulseHSR, \
                        #~ DetectionPulseLength, \
                        #~ DetectionPulsePower, \
                        #~ DetectionPulseType, \
                         #~ 'Measure'])
	#~ writerm.writerow([Frequency[i], \
                        #~ DetectionPulseHSR, \
                        #~ DetectionPulseLength2, \
                        #~ 0, \
                        #~ DetectionPulseType, \
                         #~ 'Measure'])
	#~ writerm.writerow([Frequency[i], \
                        #~ DetectionPulseHSR2, \
                        #~ DetectionPulseLength, \
                        #~ DetectionPulsePower, \
                        #~ DetectionPulseType, \
                         #~ 'Measure'])

#~ #For Spin Echo			 
    #~ for x in xrange(0,DetRepeats):
	#~ writer.writerow([0, 0.0, 10.0, 0., 1, 'Dummy']) # Dummy pulse
	#~ writer.writerow([Frequency[i], \
                        #~ DetectionPulseHSR, \
                        #~ DetectionPulseLength, \
                        #~ DetectionPulsePower, \
                        #~ DetectionPulseType, \
                        #~ 'Measure'])
	#~ writer.writerow([Frequency[i], \
                        #~ DetectionPulseHSR2, \
                        #~ DetectionPulseLength2, \
                        #~ 0, \
                        #~ DetectionPulseType, \
                        #~ 'Measure'])
	#~ writer.writerow([Frequency[i], \
                        #~ DetectionPulseHSR, \
                        #~ DetectionPulseLength, \
                        #~ 0.9, \
                        #~ DetectionPulseType, \
                        #~ 'Measure'])
	#~ writer.writerow([Frequency[i], \
                        #~ DetectionPulseHSR2, \
                        #~ DetectionPulseLength2, \
                        #~ 0, \
                        #~ DetectionPulseType, \
                        #~ 'Measure'])
	#~ writer.writerow([Frequency[i], \
                        #~ DetectionPulseHSR, \
                        #~ DetectionPulseLength, \
                        #~ DetectionPulsePower, \
                        #~ DetectionPulseType, \
                        #~ 'Measure'])
	#~ pulsefile.close() # Close the pulse file
	#~ writerm.writerow([Filenames[i]])
    #~ for x in xrange(0,DetRepeats):
	#~ writerm.writerow([0, 0.0, 10.0, 0., 1, 'Dummy']) # Dummy pulse
	#~ writerm.writerow([Frequency[i], \
                        #~ DetectionPulseHSR, \
                        #~ DetectionPulseLength, \
                        #~ DetectionPulsePower, \
                        #~ DetectionPulseType, \
                         #~ 'Measure'])
	#~ writerm.writerow([Frequency[i], \
                        #~ DetectionPulseHSR, \
                        #~ DetectionPulseLength2, \
                        #~ 0, \
                        #~ DetectionPulseType, \
                         #~ 'Measure'])
	#~ writerm.writerow([Frequency[i], \
                        #~ DetectionPulseHSR, \
                        #~ DetectionPulseLength, \
                        #~ 0.9, \
                        #~ DetectionPulseType, \
                        #~ 'Measure'])
	#~ writerm.writerow([Frequency[i], \
                        #~ DetectionPulseHSR2, \
                        #~ DetectionPulseLength2, \
                        #~ 0, \
                        #~ DetectionPulseType, \
                        #~ 'Measure'])
	#~ writerm.writerow([Frequency[i], \
                        #~ DetectionPulseHSR, \
                        #~ DetectionPulseLength, \
                        #~ DetectionPulsePower, \
                        #~ DetectionPulseType, \
                        #~ 'Measure'])
			
			
			
#~ #For n pulses######
    for x in xrange(0,DetRepeats):
	writer.writerow([0, 0.0, 10.0, 0., 1, 'Dummy']) # Dummy pulse
	for y in xrange(0,n):
		writer.writerow([Frequency[i], \
                        DetectionPulseHSR, \
                        DetectionPulseLength, \
                        rf_Power_Calib(Frequency[i])*DetectionPulsePower, \
                        DetectionPulseType, \
                        'Measure'])
    pulsefile.close() # Close the pulse file
    writerm.writerow([Filenames[i]])
    for x in xrange(0,DetRepeats):
	writerm.writerow([0, 0.0, 10.0, 0., 1, 'Dummy']) # Dummy pulse
	for y in xrange(0,n):
		writerm.writerow([Frequency[i], \
                        DetectionPulseHSR, \
                        DetectionPulseLength, \
			rf_Power_Calib(Frequency[i])*DetectionPulsePower, \
                        DetectionPulseType, \
                         'Measure'])
			 
		
		


#~ #For Spin Echo using SUPERTIME			 
    #~ for x in xrange(0,DetRepeats):
	#~ writer.writerow([0, 0.0, 10.0, 0., 1, 'Dummy']) # Dummy pulse
	#~ writer.writerow([Frequency[i], \
                        #~ DetectionPulseHSR, \
                        #~ DetectionPulseLength, \
                        #~ rf_Power_Calib(Frequency[i])*DetectionPulsePower, \
                        #~ DetectionPulseType, \
                        #~ 'Measure'])
	#~ writer.writerow([Frequency[i], \
                        #~ DetectionPulseHSR, \
                        #~ DetectionPulseLength, \
                        #~ 4*rf_Power_Calib(Frequency[i])*DetectionPulsePower, \
                        #~ DetectionPulseType, \
                        #~ 'Measure'])
	#~ writer.writerow([Frequency[i], \
                        #~ DetectionPulseHSR, \
                        #~ DetectionPulseLength, \
                        #~ rf_Power_Calib(Frequency[i])*DetectionPulsePower, \
                        #~ DetectionPulseType, \
                        #~ 'Measure'])
	#~ pulsefile.close() # Close the pulse file
	
	#~ writerm.writerow([Filenames[i]])
    #~ for x in xrange(0,DetRepeats):
	#~ writerm.writerow([0, 0.0, 10.0, 0., 1, 'Dummy']) # Dummy pulse
	#~ writerm.writerow([Frequency[i], \
                        #~ DetectionPulseHSR, \
                        #~ DetectionPulseLength, \
                        #~ DetectionPulsePower, \
                        #~ DetectionPulseType, \
                         #~ 'Measure'])
	#~ writerm.writerow([Frequency[i], \
                        #~ DetectionPulseHSR, \
                        #~ DetectionPulseLength, \
                        #~ 0.714, \
                        #~ DetectionPulseType, \
                        #~ 'Measure'])
	#~ writerm.writerow([Frequency[i], \
                        #~ DetectionPulseHSR, \
                        #~ DetectionPulseLength, \
                        #~ DetectionPulsePower, \
                        #~ DetectionPulseType, \
                        #~ 'Measure'])
		
		
		
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
subprocess.call(["C:\Users\Yang\Documents\Data\DDScontrol\stepDDS_cal3_RF-V2.bat", "List"])
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
os.system("copy "+FilenameHead+".lst last-RF.lst") # copy list file to last.lst
os.system("copy "+FilenameHead+".scan last-RF.scan") # copy scan file to last.lst