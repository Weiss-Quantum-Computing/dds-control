# Write pulse files for NewDDS2-version3.exe
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
FilenameHead = 'Phasescan'   # filenames will start with this (can include directory, but use forward slash)
FileComment = 'Cool\n'  # Comment line at head of pulse files (must end with \n)
print (FileComment)


################ 2018.08.06 #####################
f4= 	61287983.7+29.021e3	# 4,4->3,3     	   
f2p= 60981138.82-2.5e3+12.4e3		+12.7e3			# 3,3->42	   
f1p =60590952.61-1.1e3+7.4e3		+7.6e3		# 4,2->3,1         
f0p = 60198904.8+2.6e3+2.5e3		+2.5e3			# 3,1->4,0           
fclock=60006762.1922+0.08749786e3 -0.15e3-0.06e3  -0.49015465e3	 # 2015.08.26

f4newH = 56595100 
f4newL = f4newH + 2.032e6 + 46e3 + 290   # low field to check the unexplained spin echo phase shift 2025.01.23
f4new = f4newH 


# f4newH for magnetic field measurement 
f4newx = 57615738.1 - 2.3e3 + 5.75e3 + 0e3   	     # for field  (956, 0, -38)
f4newy = 57615738.1  - 43.4e3 + 6e3    # for field  (0, 975, -38)
#~ print(f4new)
print(f4new)

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
f3P1to4P1new = get_uw_freq(1,1)[0]
f4P1to3P2new = get_uw_freq(1,2)[0]
f3P2to4P3new = get_uw_freq(3,2)[0]
f3P2to4P2new = get_uw_freq(2,2)[0]
f4P3to3P3new = get_uw_freq(3,3)[0]

f33to42new = get_uw_freq(-2,-3)[0] + 620 
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

####################################

fUW = get_uw_freq2()[0]

####################################
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
test = 5e3	# 2017.02.03 Debug DDS
# used for Ramsey spec. 
Frequency0 = fUW + 10    #20220408 to account for error in 20220407
fRF = 289444.698965
fjump = -260
#~ Frequency0 = f4new 
#~ Frequency0 = f42to31new
#~ Frequency0 = fclock

print(Frequency0)
# used to scan the chirp frequency
#~ StartingFrequency = -0.280e3 #fclock+dfZeeman+40e30.2410
#~ StoppingFrequency=  -0.180e3

#~ StartingFrequency = Frequency0 - 0e3  #fclock+dfZeeman+40e30.2410
#~ StoppingFrequency= Frequency0 + 0e3

#~ StartingFrequency = f3P1to4P1newH - 0e3  #fclock+dfZeeman+40e30.2410
#~ StoppingFrequency= f3P1to4P1newH + 0e3

#~ StartingFrequency = f42to31new #fclock+dfZeeman+40e30.2410
#~ StoppingFrequency= f42to31new

#~ StartingFrequency = f4new 	#fclock+dfZeeman+40e30.2410
#~ StoppingFrequency= f4new

StartPhase = 0.0
EndPhase = 2.0
NumberOfPoints = 11

P=0.1
hsr =-8e3
DetRepeats =1	#24	# h3w many detection pulse do you want to repeat
##################################################
### CLOCK TRANSITION FREQ: 60.0068MHz ############
##################################################
#~ delta=StartingFrequency-fclock0
#~ print(StartingFrequency)6

#~ FrequencyStepSize =2e3			# 
NumberOfRepeats   = 1000		# Number of times to repeat the scan

# define the detection pulse-0..09
# Typical square pulse
#~ DetectionPulseType   = 2		# 1 for AFP, 2 for Blackman, 9 for CW (no ending), 22 Composite Pi  3 square pulse(phase coherence)
#~ DetectionPulseLength = 0.06		# 0.240	#0.120*2
#~ DetectionPulsePower  = 0.038*(64/36)
#~ DetectionPulsePower  =Pclock_Pi_120us

#~ DetectionPulseHSR    = 1	#-4e3	 # Hz (only used for AFP pulses) 
# For Blackman and CW pulses, "HSR" is the phase in units of pi

#~ DetectionPulseType   =1		# 1 for AFP, 2 for Blackman, 9 for CW (no ending), 22 Composite Pi  3 square pulse(phase coherence)
#~ DetectionPulseLength =3		# 0.240	#0.120*2
#~ DetectionPulsePower  = 0.05

#~ DetectionPulseHSR    =-4e3	#-4e3	 # Hz (only used for AFP pulses) 

# Dummy square for timing 
#~ DetectionPulseType2   = 3		# 1 for AFP, 2 for Blackman, 9 for CW (no ending), 22 Composite Pi  3 square pulse(phase coherence)
#~ DetectionPulseLength2 = 2.51 + (33.33 - 16.67)/2   		# typ 0.12 
#~ DetectionPulsePower2  = 0 	
#~ DetectionPulseHSR2    = 0

#~ # Square for two photon transition  2021.09.29
DetectionPulseType   = 3		# 1 for AFP, 2 for Blackman, 9 for CW (no ending), 22 Composite Pi  3 square pulse(phase coherence)  16 squared pulse with frequency jump
DetectionPulseLength = 0.72		# typ 0.12 
DetectionPulsePower  = 3.10
DetectionPulseHSR    = 0		# 0Hz for blackman

# Blackman for clock transition
#~ DetectionPulseType   = 2		# 1 for AFP, 2 for Blackman, 9 for CW (no ending), 22 Composite Pi  3 square pulse(phase coherence)
#~ DetectionPulseLength = 0.12		# typ 0.12 
#~ DetectionPulsePower  = 0.135	# 0.306 corresponds to 0.12 ms Blackman pulse for f4new transition (was 0.318, updated after replacing the power supply in early April 2022)   		
#~ DetectionPulseHSR    = 0		# 0Hz for blackman

#~ # Blackman for stretched states
#~ DetectionPulseType   = 2		# 1 for AFP, 2 for Blackman, 9 for CW (no ending), 22 Composite Pi  3 square pulse(phase coherence)
#~ DetectionPulseLength = 0.12		# typ 0.12 
#~ DetectionPulsePower  = 0.477/4	# 0.306 corresponds to 0.12 ms Blackman pulse for f4new transition (was 0.318, updated after replacing the power supply in early April 2022)   		
#~ DetectionPulseHSR    = 0		# 0Hz for blackman

# Blackman for |3, -3> -----> |4,-2>
#~ DetectionPulseType	= 2		# 1 for AFP, 2 for Blackman, 9 for CW (no ending), 22 Composite Pi  3 square pulse(phase coherence)
#~ DetectionPulseLength	= 0.36	# typ 0.24 (smallest transition matrix element)
#~ DetectionPulsePower	= 2.4/4		#  Pi pulse power
#~ DetectionPulseHSR	= 0		# 0Hz for blackman

# Blackman for |4, -2> -----> |3,-1>
#~ DetectionPulseType	= 2		# 1 for AFP, 2 for Blackman, 9 for CW (no ending), 22 Composite Pi  3 square pulse(phase coherence)
#~ DetectionPulseLength	= 0.12	# typ 0.12 
#~ DetectionPulsePower	= 0.74/4	# typ 0.68 for Pi pulse  0.165 for pi/2 pulse
#~ DetectionPulseHSR	= 0		# 0Hz for blackman

# Blackman for |3, -1> -----> |4,0>
#~ DetectionPulseType   = 2		# 1 for AFP, 2 for Blackman, 9 for CW (no ending), 22 Composite Pi  3 square pulse(phase coherence)
#~ DetectionPulseLength = 0.12		# typ 0.12 
#~ DetectionPulsePower  = 2.35		#  Changes between 3.156 and 3.406 (319mV p-p DDS)
#~ DetectionPulseHSR    = 0		# 0Hz for blackman

#~ # Blackman for |4,1> -----> |3,1>
#~ DetectionPulseType   = 2		# 1 for AFP, 2 for Blackman, 9 for CW (no ending), 22 Composite Pi  3 square pulse(phase coherence)
#~ DetectionPulseLength = 0.12		# typ 0.12 
#~ DetectionPulsePower  = 0.678		#  Default 1.194 
#~ DetectionPulseHSR    = 0		# 0Hz for blackman

#~Blackman for |4, 1> -----> |3,2>
#~ DetectionPulseType   = 2		# 1 for AFP, 2 for Blackman, 9 for CW (no ending), 22 Composite Pi  3 square pulse(phase coherence)
#~ DetectionPulseLength = 0.24		# typ 0.24  
#~ DetectionPulsePower  = 1.05		#  Changes between 3.156 and 3.406 (319mV p-p DDS)
#~ DetectionPulseHSR    = 0		# 0Hz for blackman

#~ # Blackman for |3, 2> -----> |4,3>
#~ DetectionPulseType   = 2		# 1 for AFP, 2 for Blackman, 9 for CW (no ending), 22 Composite Pi  3 square pulse(phase coherence)
#~ DetectionPulseLength = 0.12		# typ 0.12 
#~ DetectionPulsePower  = 0.62		#  0.62
#~ DetectionPulseHSR    = 0		# 0Hz for blackman

# Blackman for |4, 3> -----> |3,3>
#~ DetectionPulseType   = 2		# 1 for AFP, 2 for Blackman, 9 for CW (no ending), 22 Composite Pi  3 square pulse(phase coherence)
#~ DetectionPulseLength = 0.12		# typ 0.12 
#~ DetectionPulsePower  = 1.64		#  0.62
#~ DetectionPulseHSR    = 0		# 0Hz for blackman

# Collision
#~ CollisionLength = 10.51

#EmptyPulseLength for Supertime Spin Echo
#~ EmptyPulseLength = 0.2

# Test the short-term B field stablilty
# Blackman for |4,1> -----> |3,2>
#~ DetectionPulseType   = 2		 # 1 for AFP, 2 for Blackman, 9 for CW (no ending), 22 Composite Pi  3 square pulse(phase coherence)
#~ DetectionPulseLength = 0.12		 # typ 0.12 
#~ DetectionPulsePower  = 3.156         # 0.306 corresponds 10 kHz for 4,1 to 3,2 transition   	0.306*28/3 	Changes between 3.156 and 3.406
#~ DetectionPulseHSR    = 0		 # 0Hz for blackman

#~ # Blackman for |4,1> -----> |3,1>
#~ DetectionPulseType   = 2		# 1 for AFP, 2 for Blackman, 9 for CW (no ending), 22 Composite Pi  3 square pulse(phase coherence)
#~ DetectionPulseLength = 0.12		# typ 0.12 
#~ DetectionPulsePower  = 1.194/4	#  Changes between 3.156 and 3.406 (319mV p-p DDS)
#~ DetectionPulseHSR    = 0		# 0Hz for blackman

# Blackman for |4,-4> -----> |3,-3>
#~ DetectionPulseType   = 2		 # 1 for AFP, 2 for Blackman, 9 for CW (no ending), 22 Composite Pi  3 square pulse(phase coherence)
#~ DetectionPulseLength = 0.12		 # typ 0.12 
#~ DetectionPulsePower  = 0.306/4         # 0.306 corresponds 10 kHz for 4,1 to 3,2 transition   	0.306*28/3 	Changes between 3.156 and 3.406
#~ DetectionPulseHSR    = 0		 # 0Hz for blackman

#~ DetectionPulseLength3 = 2.52

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

#~ FreqM1Xafter = fc+ 17e3
#~ FreqM1Yafter = fc+ 17e3

# calculate some stuff
PhaseStepSize = 1 
if StartPhase == EndPhase:
	PhaseStepSize = 1
else:
	PhaseStepSize = (EndPhase - StartPhase)*(NumberOfPoints-1)**(-1)	
	
Phase = np.arange(StartPhase,EndPhase+PhaseStepSize/2.0, \
                      PhaseStepSize) # in Pi
		
print(Phase)
NumberOfFiles = len(Phase)

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
#~ writer.writerow([f4new,	 -8e3, 3.0, 0.038*64/36, 1, '4,-4 -> 3,-3']) 

#~ writer.writerow([fclock,		0, 0.06, Pclock_Pi_120us, 	 2, 'pi/2']) 

##### initiated 2018.02.02 #####
#~ writer.writerow([f4newH, -8e3, 3.0, 0.16*64/36, 1, '4,-4 -> 3,-3']) 
#~ writer.writerow([f4newH, -8e3, 3.0, 0.16*64/36, 1, '4,-4 -> 3,-3']) 
writer.writerow([f4new, -6e3, 3.0, P44to33new*64/36, 1, '4,-4 -> 3,-3']) 
writer.writerow([f4new-19e3, -4e3, 3.0, 0.06, 1, '4,-4 -> 3,-3'])  # used for clearing X  hotter atoms
writer.writerow([f4new-17e3, -4e3, 3.0, 0.06, 1, '4,-4 -> 3,-3'])  # used for clearing Y hotter atoms
writer.writerow([f4new-15e3, -4e3, 3.0, 0.06, 1, '4,-4 -> 3,-3'])  # used for clearing Z hotter atoms
writer.writerow([f33to42new, -6e3, 3.0, P33to42new*3, 1, '3,-3 -> 4,-2']) 
writer.writerow([f42to31new, -6e3, 3.0, P42to31new*3, 1, '4,-2 -> 3,-1']) 
#~ writer.writerow([f31to40newH, 0e3, 0.12, 2.35/4, 2, '3,-1 -> 4,0'])  # Pi/2 pulse for stretched state transition 3,-1 -> 4,0 
#~ writer.writerow([f31to40newH, 0e3, 0.12, 2.35, 2, '3,-1 -> 4,0'])  # Pi pulse for stretched state transition 3,-1 -> 4,0 
#~ writer.writerow([f42to31newH, 0e3, 0.12, 0.571/4, 2, '4,-2 -> 3,-1'])  # Pi/2 pulse for stretched state transition 3,-1 -> 4,0 
#~ writer.writerow([f42to31newH, 0e3, 0.12, 0.571, 2, '3,-1 -> 4,0'])  # Pi pulse for stretched state transition 3,-1 -> 4,0 
#~ writer.writerow([f4newH, 0e3, 0.12, 0.306/4, 2,  '4,-4 -> 3,-3'])  # Pi/2 pulse for stretched state transition 4,-4 --> 3,-3 
#~ writer.writerow([f4newH, 0e3, 0.12, 0.306, 2,  '4,-4 -> 3,-3'])  # Pi pulse for stretched state transition 4,-4 --> 3,-3 
#~ writer.writerow([f33to43new, -8e3, 3.0, P33to43new*64/36, 1, '3,-3 -> 4,-3']) 
#~ writer.writerow([f43to32new, -6e3, 3.0, P43to32new, 1, '4,-3 -> 3,-2']) 
#~ writer.writerow([f32to41new, -6e3, 3.0, P32to41new, 1, '3,-2 -> 4,-1']) 

#~ writer.writerow([58.0e6, 0.0, 3.0, 0., 1, 'Dummy']) # Dummy pulse
#~ writer.writerow([f33to42new, -6e3, 3.0, P33to42new*36/16, 1, '3,-3 -> 4,-2']) 
#~ writer.writerow([f42to31new, -6e3, 3.0, P42to31new*36/16, 1, '4,-2 -> 3,-1'])
#~ writer.writerow([Frequency0, 0, 0.8, 0.318*14, 3, '3,-1 -> 4,1']) #for square 2-photon 
#~ writer.writerow([f31to40new, -6e3, 3.0, P31to40new*36/16, 1, '3,-1 -> 4,0'])
#~ writer.writerow([f40to3P1newH, -8e3, 3.0, P40to3P1new*64/36, 1, '4,0 -> 3,1'])
#~ writer.writerow([f3P1to4P1newH, -8e3, 3.0, P3P1to4P1new*64/36, 1, '3,1 -> 4,1'])
#~ writer.writerow([f4P1to3P2newH, -8e3, 3.0, P4P1to3P2new*64/36, 1, '4,1 -> 3,2'])
#~ writer.writerow([fclock,		-8e3, 3.0, Pclock*64/36, 	 1, '4,0 -> 3,0']) 
#~ writer.writerow([f42to31new, -8e3, 3.0, P42to31new*64/36, 1, '4,-2 -> 3,-1']) 
#~ writer.writerow([f4new, 	-8e3, 3.0, 0.038*64/36, 1, '4,-4 -> 3,-3']) 

#~ num4repeats = 384
#~ for i in range(0,num4repeats):  # x_x_(-x)_(-x)
	#~ writer.writerow([fclock,		0, 0.12, Pclock_Pi_120us, 	 2, 'pi'])
	#~ writer.writerow([fclock,		0, 0.12, Pclock_Pi_120us, 	 2, 'pi']) 	
	#~ writer.writerow([fclock,		1, 0.12, Pclock_Pi_120us, 	 2, 'pi']) 
	#~ writer.writerow([fclock,		1, 0.12, Pclock_Pi_120us, 	 2, 'pi']) 
#~ for i in range(0,num4repeats):  # x_-x)
	#~ writer.writerow([fclock,		0.0, 0.12, Pclock_Pi_120us, 	 2, 'pi'])	
	#~ writer.writerow([fclock,		1.0, 0.12, Pclock_Pi_120us, 	 2, 'pi']) 
	
#~ for i in range(0,num4repeats):  # y_y_(-y)_(-y)
	#~ writer.writerow([fclock,		0.5, 0.12, Pclock_Pi_120us, 	 2, 'pi'])
	#~ writer.writerow([fclock,		0.5, 0.12, Pclock_Pi_120us, 	 2, 'pi']) 	
	#~ writer.writerow([fclock,		1.5, 0.12, Pclock_Pi_120us, 	 2, 'pi']) 
	#~ writer.writerow([fclock,		1.5, 0.12, Pclock_Pi_120us, 	 2, 'pi']) 

#~ for i in range(0,num4repeats):  # XY4
	#~ writer.writerow([fclock,		0, 0.12, Pclock_Pi_120us, 	 2, 'pi'])
	#~ writer.writerow([fclock,		0.5, 0.12, Pclock_Pi_120us, 	 2, 'pi']) 	
	#~ writer.writerow([fclock,		0, 0.12, Pclock_Pi_120us, 	 2, 'pi']) 
	#~ writer.writerow([fclock,		0.5, 0.12, Pclock_Pi_120us, 	 2, 'pi']) 

#~ for i in range(0,num4repeats/2):  # XY8
	#~ writer.writerow([fclock,		0, 0.12, Pclock_Pi_120us, 	 2, 'pi'])
	#~ writer.writerow([fclock,		0.5, 0.12, Pclock_Pi_120us, 	 2, 'pi']) 	
	#~ writer.writerow([fclock,		0, 0.12, Pclock_Pi_120us, 	 2, 'pi']) 
	#~ writer.writerow([fclock,		0.5, 0.12, Pclock_Pi_120us, 	 2, 'pi']) 
	#~ writer.writerow([fclock,		0.5, 0.12, Pclock_Pi_120us, 	 2, 'pi'])
	#~ writer.writerow([fclock,		0., 0.12, Pclock_Pi_120us, 	 2, 'pi']) 	
	#~ writer.writerow([fclock,		0.5, 0.12, Pclock_Pi_120us, 	 2, 'pi']) 
	#~ writer.writerow([fclock,		0., 0.12, Pclock_Pi_120us, 	 2, 'pi']) 
	
	
#~ for i in range(0,num4repeats/4):  # XY16
	#~ writer.writerow([fclock,		0, 0.12, Pclock_Pi_120us, 	 2, 'pi'])
	#~ writer.writerow([fclock,		0.5, 0.12, Pclock_Pi_120us, 	 2, 'pi']) 	
	#~ writer.writerow([fclock,		0, 0.12, Pclock_Pi_120us, 	 2, 'pi']) 
	#~ writer.writerow([fclock,		0.5, 0.12, Pclock_Pi_120us, 	 2, 'pi']) 
	#~ writer.writerow([fclock,		0.5, 0.12, Pclock_Pi_120us, 	 2, 'pi'])
	#~ writer.writerow([fclock,		0., 0.12, Pclock_Pi_120us, 	 2, 'pi']) 	
	#~ writer.writerow([fclock,		0.5, 0.12, Pclock_Pi_120us, 	 2, 'pi']) 
	#~ writer.writerow([fclock,		0., 0.12, Pclock_Pi_120us, 	 2, 'pi']) 
	
	#~ writer.writerow([fclock,		1, 0.12, Pclock_Pi_120us, 	 2, 'pi'])
	#~ writer.writerow([fclock,		1.5, 0.12, Pclock_Pi_120us, 	 2, 'pi']) 	
	#~ writer.writerow([fclock,		1, 0.12, Pclock_Pi_120us, 	 2, 'pi']) 
	#~ writer.writerow([fclock,		1.5, 0.12, Pclock_Pi_120us, 	 2, 'pi']) 
	#~ writer.writerow([fclock,		1.5, 0.12, Pclock_Pi_120us, 	 2, 'pi'])
	#~ writer.writerow([fclock,		1., 0.12, Pclock_Pi_120us, 	 2, 'pi']) 	
	#~ writer.writerow([fclock,		1.5, 0.12, Pclock_Pi_120us, 	 2, 'pi']) 
	#~ writer.writerow([fclock,		1., 0.12, Pclock_Pi_120us, 	 2, 'pi']) 
	
#~ # additional XY8
#~ writer.writerow([fclock,		0, 0.12, Pclock_Pi_120us, 	 2, 'pi'])
#~ writer.writerow([fclock,		0.5, 0.12, Pclock_Pi_120us, 	 2, 'pi']) 	
#~ writer.writerow([fclock,		0, 0.12, Pclock_Pi_120us, 	 2, 'pi']) 
#~ writer.writerow([fclock,		0.5, 0.12, Pclock_Pi_120us, 	 2, 'pi']) 
#~ writer.writerow([fclock,		0.5, 0.12, Pclock_Pi_120us, 	 2, 'pi'])
#~ writer.writerow([fclock,		0., 0.12, Pclock_Pi_120us, 	 2, 'pi']) 	
#~ writer.writerow([fclock,		0.5, 0.12, Pclock_Pi_120us, 	 2, 'pi']) 
#~ writer.writerow([fclock,		0., 0.12, Pclock_Pi_120us, 	 2, 'pi']) 

#~ writer.writerow([fclock,		-6e3, 3.0, Pclock, 	 1, '4,0 -> 3,0']) 
#~ writer.writerow([f41to30new, -6e3, 3.0, P41to30new, 1, '3,0-> 4,-1'])
#~ writer.writerow([f42to31new, -6e3, 3.0, 0.169, 1, '3,-1 -> 4,-2']) 


##### initiated 2018.02.02 #####
#~ writer.writerow([f4new, -6e3, 3.0, 0.038, 1, '4,-4 -> 3,-3']) 
#~ writer.writerow([f33to43new, -6e3, 3.0, P33to43new, 1, '3,-3 -> 4,-3']) 
#~ writer.writerow([f43to32new, -6e3, 3.0, P43to32new, 1, '4,-3 -> 3,-2']) 
#~ writer.writerow([f32to41new, -6e3, 3.0, P32to41new, 1, '3,-2 -> 4,-1']) 

#~ writer.writerow([58.0e6, 0.0, 3.0, 0., 1, 'Dummy']) # Dummy pulse
#~ writer.writerow([f33to42new, -6e3, 3.0, P33to42new, 1, '3,-3 -> 4,-2']) 
#~ writer.writerow([f42to31new, -6e3, 3.0, P42to31new, 1, '4,-2 -> 3,-1']) 
#~ writer.writerow([f31to40new, -6e3, 3.0, P31to40new, 1, '3,-1 -> 4,0']) 

#~ writer.writerow([fclock,		-6e3, 3.0, Pclock, 	 1, '4,0 -> 3,0']) 
#~ writer.writerow([f41to30new, -6e3, 3.0, P41to30new, 1, '3,0-> 4,-1'])
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

os.system('copy '+Coolfilename+' Gate')
#os.system('C:\Users\Yang\Documents\Data\DDScontrol\NewDDS2-Cooling2.0-Cal.exe Cool')
subprocess.call(['C:\Users\Yang\Documents\Data\DDScontrol\NewDDS2-Cooling2.0-Cal.exe', 'Gate'])
print('After making Cool')

# begin loop to write the detection pulse files    
measfile = open(MeasListFilename, "wb")                  
measfile.write(FileComment)                  
writerm = csv.writer(measfile, dialect='excel-tab')
for i in xrange(0,len(Phase)):
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
    #~ for x in xrange(0,DetRepeats):
        #~ writer.writerow([StartingFrequency, \
                        #~ Phase[i], \
                        #~ DetectionPulseLength, \
                        #~ DetectionPulsePower, \
                        #~ DetectionPulseType, \
                        #~ 'Measure'])
	#~ writer.writerow([f31to40new, -8e3, 3.0, P31to40new*64/36, 1, '3,-1 -> 4,0'])
	#~ writer.writerow([f42to31new3msAfterResync, -8e3, 3.0, P32to41new*64/36, 1, '4,-2 -> 3,-1']) 
	
    #~ pulsefile.close() # Close the pulse file
    #~ writerm.writerow([Filenames[i]])
    #~ for x in xrange(0,DetRepeats):
        #~ writerm.writerow([StartingFrequency, \
                        #~ Phase[i], \
                        #~ DetectionPulseLength, \
                        #~ DetectionPulsePower, \
                        #~ DetectionPulseType, \
                         #~ 'Measure'])
	#~ writerm.writerow([f31to40new, -8e3, 3.0, P31to40new*64/36, 1, '3,-1 -> 4,0'])
	#~ writerm.writerow([f42to31new3msAfterResync, -8e3, 3.0, P32to41new*64/36, 1, '4,-2 -> 3,-1']) 
	
	
    #~ for x in xrange(0,DetRepeats):
	#~ writer.writerow([StartingFrequency, \
			#~ Phase[i], \
			#~ DetectionPulseLength, \
			#~ DetectionPulsePower, \
			#~ DetectionPulseType, \
			#~ 'Measure'])
	#~ writer.writerow([f33to42newH, -8e3, 3.0, P33to42new*64/36, 1, '3,-3 -> 4,-2']) 
	#~ writer.writerow([f42to31newH, -8e3, 3.0, P42to31new*64/36, 1, '4,-2 -> 3,-1']) 
	#~ writer.writerow([f33to42newH, -8e3, 3.0, P33to42new*64/36, 1, '3,-3 -> 4,-2']) 
	#~ writer.writerow([f31to40newH, -8e3, 3.0, P31to40new*64/36, 1, '3,-1 -> 4,0'])
	#~ writer.writerow([f42to31newH, -8e3, 3.0, P42to31new*64/36, 1, '4,-2 -> 3,-1']) 
	#~ writer.writerow([f4P1to3P2newH, -8e3, 3.0, P4P1to3P2new*64/36, 1, '4,1 -> 3,2'])
	#~ writer.writerow([f3P2to4P3newH, -8e3, 3.0, P4P1to3P2new*64/36, 1, '3,2 -> 4,3'])
			
	#~ pulsefile.close() # Close the pulse file
	#~ writerm.writerow([Filenames[i]])
    #~ for x in xrange(0,DetRepeats):
	#~ writerm.writerow([StartingFrequency, \
			#~ Phase[i], \
			#~ DetectionPulseLength, \
			#~ DetectionPulsePower, \
			#~ DetectionPulseType, \
			#~ 'Measure'])
	#~ writerm.writerow([f33to42newH, -8e3, 3.0, P33to42new*64/36, 1, '3,-3 -> 4,-2']) 
	#~ writerm.writerow([f42to31newH, -8e3, 3.0, P42to31new*64/36, 1, '4,-2 -> 3,-1']) 
	#~ writerm.writerow([f33to42newH, -8e3, 3.0, P33to42new*64/36, 1, '3,-3 -> 4,-2']) 
	#~ writerm.writerow([f31to40newH, -8e3, 3.0, P31to40new*64/36, 1, '3,-1 -> 4,0'])
	#~ writerm.writerow([f42to31newH, -8e3, 3.0, P42to31new*64/36, 1, '4,-2 -> 3,-1']) 
	
	
# used for checking the coherence to 42 with DDS timing
    #~ for x in xrange(0,DetRepeats):
        #~ writer.writerow([Frequency0, \
                        #~ 0, \
                        #~ DetectionPulseLength, \
                        #~ DetectionPulsePower, \
                        #~ DetectionPulseType, \
                        #~ 'Measure'])
	#~ writer.writerow([Frequency0 + fjump, \
                        #~ 0, \
                        #~ DetectionPulseLength2, \
                        #~ 0, \
                        #~ 3, \
                        #~ 'Measure'])
	#~ writer.writerow([f4P1to3P2newH, 0, 0.12,3.406, 2, '4,1 -> 3,2'])
	#~ writer.writerow([Frequency0 + fRF, 0, CollisionLength,0, 2, '4,1 -> 3,2'])
	#~ writer.writerow([f4P1to3P2newH, 1, 0.12,3.406, 2, '4,1 -> 3,2'])
	#~ writer.writerow([Frequency0  + fjump , \
                        #~ 0, \
                        #~ DetectionPulseLength2, \
                        #~ 0, \
                        #~ 3, \
                        #~ 'Measure'])
	#~ writer.writerow([Frequency0, \
                        #~ 0, \
                        #~ DetectionPulseLength, \
                        #~ DetectionPulsePower, \
                        #~ DetectionPulseType, \
                        #~ 'Measure'])
	#~ writer.writerow([Frequency0 + fjump , \
                        #~ 0, \
                        #~ DetectionPulseLength2, \
                        #~ 0, \
                        #~ 3, \
                        #~ 'Measure'])
	#~ writer.writerow([f4P1to3P2newH, 0, 0.12,3.406, 2, '4,1 -> 3,2'])
	#~ writer.writerow([Frequency0 + fRF, 0, CollisionLength,0, 2, '4,1 -> 3,2'])
	#~ writer.writerow([f4P1to3P2newH, 1, 0.12,3.406, 2, '4,1 -> 3,2'])
	#~ writer.writerow([Frequency0  + fjump , \
                        #~ 0, \
                        #~ DetectionPulseLength2, \
                        #~ 0, \
                        #~ 3, \
                        #~ 'Measure'])
        #~ writer.writerow([Frequency0, \
                        #~ Phase[i], \
                        #~ DetectionPulseLength, \
                        #~ DetectionPulsePower, \
                        #~ DetectionPulseType, \
                        #~ 'Measure'])
	#~ writer.writerow([f42to31newH, -8e3, 3.0, P42to31new*64/36, 1, '4,-2 -> 3,1'])
	#~ writer.writerow([f4P1to3P2newH, -8e3, 3.0, P4P1to3P2new*64/36, 1, '4,1 -> 3,2'])
	#~ writer.writerow([f3P2to4P3newH, -8e3, 3.0, P3P2to4P3new*64/36, 1, '3,2 -> 4,3'])	
    #~ pulsefile.close() # Close the pulse file
    #~ writerm.writerow([Filenames[i]])
    #~ for x in xrange(0,DetRepeats):
	#~ writerm.writerow([Frequency0, \
                        #~ 0, \
                        #~ DetectionPulseLength, \
                        #~ DetectionPulsePower, \
                        #~ DetectionPulseType, \
                        #~ 'Measure'])
	#~ writerm.writerow([Frequency0  + fjump , \
                        #~ 0, \
                        #~ DetectionPulseLength2, \
                        #~ 0, \
                        #~ 3, \
                        #~ 'Measure'])
	#~ writerm.writerow([f4P1to3P2newH, 0, 0.12,3.406, 2, '4,1 -> 3,2'])
	#~ writerm.writerow([Frequency0 + fRF, 0, CollisionLength,0, 2, '4,1 -> 3,2'])
	#~ writerm.writerow([f4P1to3P2newH, 1, 0.12,3.406, 2, '4,1 -> 3,2'])
	#~ writerm.writerow([Frequency0  + fjump , \
                        #~ 0, \
                        #~ DetectionPulseLength2, \
                        #~ 0, \
                        #~ 3, \
                        #~ 'Measure'])
	#~ writerm.writerow([Frequency0, \
                        #~ 0, \
                        #~ DetectionPulseLength, \
                        #~ DetectionPulsePower, \
                        #~ DetectionPulseType, \
                        #~ 'Measure'])
	#~ writerm.writerow([Frequency0 + fjump , \
                        #~ 0, \
                        #~ DetectionPulseLength2, \
                        #~ 0, \
                        #~ 3, \
                        #~ 'Measure'])
	#~ writerm.writerow([f4P1to3P2newH, 0, 0.12,3.406, 2, '4,1 -> 3,2'])
	#~ writerm.writerow([Frequency0 + fRF, 0, CollisionLength,0, 2, '4,1 -> 3,2'])
	#~ writerm.writerow([f4P1to3P2newH, 1, 0.12,3.406, 2, '4,1 -> 3,2'])
	#~ writerm.writerow([Frequency0  + fjump , \
                        #~ 0, \
                        #~ DetectionPulseLength2, \
                        #~ 0, \
                        #~ 3, \
                        #~ 'Measure'])
        #~ writerm.writerow([Frequency0, \
                        #~ Phase[i], \
                        #~ DetectionPulseLength, \
                        #~ DetectionPulsePower, \
                        #~ DetectionPulseType, \
                        #~ 'Measure'])
	#~ writerm.writerow([f42to31newH, -8e3, 3.0, P42to31new*64/36, 1, '4,-2 -> 3,1'])
	#~ writerm.writerow([f4P1to3P2newH, -8e3, 3.0, P4P1to3P2new*64/36, 1, '4,1 -> 3,2'])
	#~ writerm.writerow([f3P2to4P3newH, -8e3, 3.0, P3P2to4P3new*64/36, 1, '3,2 -> 4,3'])


    #~ for x in xrange(0,DetRepeats):
        #~ writer.writerow([Frequency1, \
                        #~ DetectionPulseHSR, \
                        #~ DetectionPulseLength, \
                        #~ DetectionPulsePower, \
                        #~ DetectionPulseType, \
                        #~ 'Measure'])
	#~ writer.writerow([Frequency1, \
                        #~ DetectionPulseHSR, \
                        #~ DetectionPulseLength3, \
                        #~ 0, \
                        #~ DetectionPulseType, \
                        #~ 'Measure'])
	#~ writer.writerow([Frequency1, \
                        #~ DetectionPulseHSR, \
                        #~ DetectionPulseLength, \
                        #~ 0.306, \
                        #~ DetectionPulseType, \
                        #~ 'Measure'])
	#~ writer.writerow([Frequency1, \
                        #~ DetectionPulseHSR, \
                        #~ DetectionPulseLength3, \
                        #~ 0, \
                        #~ DetectionPulseType, \
                        #~ 'Measure'])
	#~ writer.writerow([Frequency1, \
                        #~ Phase[i], \
                        #~ DetectionPulseLength, \
                        #~ DetectionPulsePower, \
                        #~ DetectionPulseType, \
                        #~ 'Measure'])
	#~ writer.writerow([f3P2to4P3newH, -8e3, 3.0, P4P1to3P2new*64/36, 1, '3,2 -> 4,3'])
	#~ writer.writerow([f4P1to3P2newH, -8e3, 3.0, P4P1to3P2new*64/36, 1, '4,1 -> 3,2'])
    #~ pulsefile.close() # Close the pulse file
    #~ writerm.writerow([Filenames[i]])
    #~ for x in xrange(0,DetRepeats):
	#~ writerm.writerow([Frequency1, \
                        #~ DetectionPulseHSR, \
                        #~ DetectionPulseLength, \
                        #~ DetectionPulsePower, \
                        #~ DetectionPulseType, \
                        #~ 'Measure'])
	#~ writerm.writerow([Frequency1, \
                        #~ DetectionPulseHSR, \
                        #~ DetectionPulseLength3, \
                        #~ 0, \
                        #~ DetectionPulseType, \
                        #~ 'Measure'])
	#~ writerm.writerow([Frequency1, \
                        #~ DetectionPulseHSR, \
                        #~ DetectionPulseLength, \
                        #~ 0.306, \
                        #~ DetectionPulseType, \
                        #~ 'Measure'])
	#~ writerm.writerow([Frequency1, \
                        #~ DetectionPulseHSR, \
                        #~ DetectionPulseLength3, \
                        #~ 0, \
                        #~ DetectionPulseType, \
                        #~ 'Measure'])
	#~ writerm.writerow([Frequency1, \
                        #~ Phase[i], \
                        #~ DetectionPulseLength, \
                        #~ DetectionPulsePower, \
                        #~ DetectionPulseType, \
                        #~ 'Measure'])
	#~ writerm.writerow([f3P2to4P3newH, -8e3, 3.0, P4P1to3P2new*64/36, 1, '3,2 -> 4,3'])
	#~ writerm.writerow([f4P1to3P2newH, -8e3, 3.0, P4P1to3P2new*64/36, 1, '4,1 -> 3,2'])


#~ # used for checking the coherence to 42 with SUPERTIME
    #~ for x in xrange(0,DetRepeats):
        #~ writer.writerow([Frequency1, \
                        #~ 0, \
                        #~ DetectionPulseLength, \
                        #~ DetectionPulsePower, \
                        #~ DetectionPulseType, \
                        #~ 'Measure'])
	#~ writer.writerow([f3P1to4P1newH, 0, 0.12,0.83*0, 2, '4,1 -> 3,2'])
	#~ writer.writerow([Frequency0-295, \
			#~ 0, \
			#~ 0.02, \
			#~ 0, \
			#~ 3, \
			#~ 'Measure'])
	#~ writer.writerow([Frequency1, 0, 0.12,0.66, 2, '4,-2 -> 3,-1'])
	#~ writer.writerow([Frequency0-295, \
                        #~ 0, \
                        #~ 0.02, \
                        #~ 0, \
                        #~ 3, \
                        #~ 'Measure'])
	#~ writer.writerow([Frequency0, \
                        #~ 0.0, \
                        #~ DetectionPulseLength, \
                        #~ DetectionPulsePower, \
                        #~ DetectionPulseType, \
                        #~ 'Measure'])
	#~ writer.writerow([f3P1to4P1newH, 0, 0.12,0.83*0, 2, '4,1 -> 3,2'])
	#~ writer.writerow([Frequency0-295, \
                        #~ 0, \
                        #~ 0.02, \
                        #~ 0, \
                        #~ 3, \
                        #~ 'Measure'])
	#~ writer.writerow([f3P1to4P1newH, 1, 0.12,0.83*0, 2, '4,1 -> 3,2'])
	#~ writer.writerow([Frequency0-295, \
                        #~ 0, \
                        #~ 0.02, \
                        #~ 0, \
                        #~ 3, \
                        #~ 'Measure'])
        #~ writer.writerow([Frequency1, \
                        #~ Phase[i], \
                        #~ DetectionPulseLength, \
                        #~ DetectionPulsePower, \
                        #~ DetectionPulseType, \
                        #~ 'Measure'])
	#~ writer.writerow([f33to42new, -8e3, 3.0, P33to42new*64/36, 1, '3,-3 -> 4,-2']) 
	#~ writer.writerow([f31to40new, -8e3, 3.0, P31to40new*64/36, 1, '3,-1 -> 4,0'])
	#~ writer.writerow([f42to31new, -8e3, 3.0, P42to31new*64/36, 1, '4,-2 -> 3,-1']) 
	#~ writer.writerow([f42to31new, -8e3, 3.0, P42to31new*64/36, 1, '4,-2 -> 3,1'])
	#~ writer.writerow([f4P1to3P2new, -8e3, 3.0, P4P1to3P2new*64/36, 1, '4,1 -> 3,2'])
	#~ writer.writerow([f3P2to4P3new, -8e3, 3.0, P3P2to4P3new*64/36, 1, '3,2 -> 4,3'])	
    #~ pulsefile.close() # Close the pulse file
    
    #~ writerm.writerow([Filenames[i]])
    #~ for x in xrange(0,DetRepeats):
	#~ writerm.writerow([Frequency0, \
                        #~ 0, \
                        #~ DetectionPulseLength, \
                        #~ DetectionPulsePower, \
                        #~ DetectionPulseType, \
                        #~ 'Measure'])
	#~ writerm.writerow([f3P1to4P1newH, 0, 0.12,0.83*0, 2, '4,1 -> 3,2'])
	#~ writerm.writerow([Frequency0-295, \
			#~ 0, \
			#~ 0.02, \
			#~ 0, \
			#~ 3, \
			#~ 'Measure'])
	#~ writerm.writerow([f3P1to4P1newH, 1, 0.12,0.83*0, 2, '4,1 -> 3,2'])
	#~ writerm.writerow([Frequency0, \
                        #~ 0, \
                        #~ DetectionPulseLength, \
                        #~ DetectionPulsePower, \
                        #~ DetectionPulseType, \
                        #~ 'Measure'])
	#~ writerm.writerow([f3P1to4P1newH, 0, 0.12,0.83*0, 2, '4,1 -> 3,2'])
	#~ writerm.writerow([Frequency0-295, \
			#~ 0, \
			#~ 0.02, \
			#~ 0, \
			#~ 3, \
			#~ 'Measure'])
	#~ writerm.writerow([f3P1to4P1newH, 1, 0.12,0.83*0, 2, '4,1 -> 3,2'])
	#~ writerm.writerow([Frequency0-295, \
			#~ 0, \
			#~ 0.02, \
			#~ 0, \
			#~ 3, \
			#~ 'Measure'])
        #~ writerm.writerow([Frequency0, \
                        #~ Phase[i], \
                        #~ DetectionPulseLength, \
                        #~ DetectionPulsePower, \
                        #~ DetectionPulseType, \
                        #~ 'Measure'])
	#~ writerm.writerow([f42to31new, -8e3, 3.0, P42to31new*64/36, 1, '4,-2 -> 3,1'])
	#~ writerm.writerow([f4P1to3P2new, -8e3, 3.0, P4P1to3P2new*64/36, 1, '4,1 -> 3,2'])
	#~ writerm.writerow([f3P2to4P3new, -8e3, 3.0, P3P2to4P3new*64/36, 1, '3,2 -> 4,3'])


#~ # used for checking the coherence to 42 with SUPERTIME
    for x in xrange(0,DetRepeats):
        writer.writerow([Frequency0, \
                        0, \
                        DetectionPulseLength, \
                        DetectionPulsePower, \
                        DetectionPulseType, \
                        'Measure'])
	writer.writerow([f3P1to4P1new, 0, 0.12, 0.678, 2, '4,1 -> 3,1'])
	#~ writer.writerow([f3P2to4P3new, 0, 0.12,0.64, 2, '4,1 -> 3,2'])
	#~ writer.writerow([f4P3to3P3new, 0, 0.24,0.262, 2, '4,1 -> 3,2'])
	#~ writer.writerow([f42to31new, 0, 0.12, 0.73, 2, '4,1 -> 3,2'])
	#~ writer.writerow([f33to42new, 0, 0.36,1.43, 2, '4,1 -> 3,2'])
	#~ writer.writerow([Frequency0-295, \
			#~ 0, \
			#~ 0.02, \
			#~ 0, \
			#~ 3, \
			#~ 'Measure'])
	writer.writerow([f3P1to4P1new, 0, 0.12, 0.678, 2, '4,1 -> 3,1'])
	#~ writer.writerow([f4P3to3P3new, 1, 0.24,0.262, 2, '4,1 -> 3,2'])
	#~ writer.writerow([f3P2to4P3new, 1, 0.12,0.64, 2, '4,1 -> 3,2'])
	#~ writer.writerow([f4P1to3P2new, 1, 0.24, 0.80, 2, '4,1 -> 3,1'])
	#~ writer.writerow([f33to42new, 1, 0.36,1.43, 2, '4,1 -> 3,2'])
	#~ writer.writerow([f42to31new, 1, 0.12, 0.73, 2, '4,1 -> 3,2'])
	#~ writer.writerow([Frequency0-295, \
                        #~ 0, \
                        #~ 0.02, \
                        #~ 0, \
                        #~ 3, \
                        #~ 'Measure'])
	writer.writerow([Frequency0, \
                        0.0, \
                        DetectionPulseLength, \
                        DetectionPulsePower, \
                        DetectionPulseType, \
                        'Measure'])
	writer.writerow([f3P1to4P1new, 0, 0.12, 0.678, 2, '4,1 -> 3,1'])
	#~ writer.writerow([f4P1to3P2new, 0, 0.24, 0.80, 2, '4,1 -> 3,1'])
	#~ writer.writerow([f3P2to4P3new, 0, 0.12,0.64, 2, '4,1 -> 3,2'])
	#~ writer.writerow([f4P3to3P3new, 0, 0.24,0.262, 2, '4,1 -> 3,2'])
	#~ writer.writerow([f42to31new, 0, 0.12, 0.73, 2, '4,1 -> 3,2'])
	#~ writer.writerow([f33to42new, 0, 0.36,1.43, 2, '4,1 -> 3,2'])
	#~ writer.writerow([Frequency0-295, \
                        #~ 0, \
                        #~ 0.02, \
                        #~ 0, \
                        #~ 3, \
                        #~ 'Measure'])
	writer.writerow([f3P1to4P1new, 0, 0.12, 0.678, 2, '4,1 -> 3,1'])
	#~ writer.writerow([f4P3to3P3new, 1, 0.24,0.262, 2, '4,1 -> 3,2'])
	#~ writer.writerow([f3P2to4P3new, 1, 0.12,0.64, 2, '4,1 -> 3,2'])
	#~ writer.writerow([f4P1to3P2new, 1, 0.24, 0.80, 2, '4,1 -> 3,1'])
	#~ writer.writerow([f33to42new, 1, 0.36,1.43, 2, '4,1 -> 3,2'])
	#~ writer.writerow([f42to31new, 1, 0.12, 0.73, 2, '4,1 -> 3,2'])
	#~ writer.writerow([Frequency0-295, \
                        #~ 0, \
                        #~ 0.02, \
                        #~ 0, \
                        #~ 3, \
                        #~ 'Measure'])
        writer.writerow([Frequency0, \
                        Phase[i], \
                        DetectionPulseLength, \
                        DetectionPulsePower, \
                        DetectionPulseType, \
                        'Measure'])
	#~ writer.writerow([f33to42new, -6e3, 3.0, P33to42new*64/36, 1, '3,-3 -> 4,-2']) 
	writer.writerow([f42to31new, -8e3, 3.0, P42to31new*64/36, 1, '4,-2 -> 3,-1']) 
	#~ writer.writerow([f42to31new, -6e3, 3.0, P42to31new*64/36, 1, '4,-2 -> 3,1'])
	writer.writerow([f4P1to3P2new, -6e3, 3.0, P4P1to3P2new*64/36, 1, '4,1 -> 3,2'])
	writer.writerow([f3P2to4P3new, -6e3, 3.0, P3P2to4P3new*64/36, 1, '3,2 -> 4,3'])	
	#~ writer.writerow([f31to40new, -6e3, 3.0, P31to40new*4, 1, '3,-1 -> 4,0'])
	#~ writer.writerow([f42to31new, -6e3, 3.0, P42to31new*4, 1, '4,-2 -> 3,-1']) 
	#~ writer.writerow([f33to42new, 1, 0.36,1.43, 2, '4,1 -> 3,2'])
	#~ writer.writerow([f42to31new, 1, 0.12,0.82, 2, '4,1 -> 3,2'])
    pulsefile.close() # Close the pulse file
    
    writerm.writerow([Filenames[i]])
    for x in xrange(0,DetRepeats):
	writerm.writerow([Frequency0, \
                        0, \
                        DetectionPulseLength, \
                        DetectionPulsePower, \
                        DetectionPulseType, \
                        'Measure'])
	#~ writerm.writerow([f4P1to3P2new, 0, 0.24,1.05, 2, '4,1 -> 3,2'])
	#~ writerm.writerow([f3P2to4P3new, 0, 0.12,0.62, 2, '4,1 -> 3,2'])
	#~ writerm.writerow([f4P3to3P3new, 0, 0.12,1.64, 2, '4,1 -> 3,2'])
	#~ writerm.writerow([f42to31new, 0, 0.12,0.74, 2, '4,1 -> 3,2'])
	#~ writerm.writerow([f33to42new, 0, 0.24,3.5, 2, '4,1 -> 3,2'])
	#~ writerm.writerow([Frequency0-295, \
			#~ 0, \
			#~ 0.02, \
			#~ 0, \
			#~ 3, \
			#~ 'Measure'])
	#~ writerm.writerow([f4P3to3P3new, 1, 0.12,1.64, 2, '4,1 -> 3,2'])
	#~ writerm.writerow([f3P2to4P3new, 1, 0.12,0.62, 2, '4,1 -> 3,2'])
	#~ writerm.writerow([f4P1to3P2new, 1, 0.24,1.05, 2, '4,1 -> 3,2'])
	#~ writerm.writerow([f33to42new, 1, 0.24,3.5, 2, '4,1 -> 3,2'])
	#~ writerm.writerow([f42to31new, 1, 0.12,0.74, 2, '4,1 -> 3,2'])
	writerm.writerow([Frequency0, \
                        0.5, \
                        DetectionPulseLength, \
                        DetectionPulsePower*4, \
                        DetectionPulseType, \
                        'Measure'])
	#~ writerm.writerow([f4P1to3P2new, 0, 0.24,1.05, 2, '4,1 -> 3,2'])
	#~ writerm.writerow([f3P2to4P3new, 0, 0.12,0.62, 2, '4,1 -> 3,2'])
	#~ writerm.writerow([f4P3to3P3new, 0, 0.12,1.64, 2, '4,1 -> 3,2'])
	#~ writerm.writerow([f42to31new, 0, 0.12,0.74, 2, '4,1 -> 3,2'])
	#~ writerm.writerow([f33to42new, 0, 0.24,3.5, 2, '4,1 -> 3,2'])
	#~ writerm.writerow([Frequency0-295, \
			#~ 0, \
			#~ 0.02, \
			#~ 0, \
			#~ 3, \
			#~ 'Measure'])
	#~ writerm.writerow([f4P3to3P3new, 1, 0.12,1.64, 2, '4,1 -> 3,2'])
	#~ writerm.writerow([f3P2to4P3new, 1, 0.12,0.62, 2, '4,1 -> 3,2'])
	#~ writerm.writerow([f4P1to3P2new, 1, 0.24,1.05, 2, '4,1 -> 3,2'])
	#~ writerm.writerow([f33to42new, 1, 0.24,3.5, 2, '4,1 -> 3,2'])
	#~ writerm.writerow([f42to31new, 1, 0.12,0.74, 2, '4,1 -> 3,2'])
	#~ writerm.writerow([Frequency0-295, \
			#~ 0, \
			#~ 0.02, \
			#~ 0, \
			#~ 3, \
			#~ 'Measure'])
        writerm.writerow([Frequency0, \
                        Phase[i], \
                        DetectionPulseLength, \
                        DetectionPulsePower, \
                        DetectionPulseType, \
                        'Measure'])
	#~ writerm.writerow([f42to31new, -8e3, 3.0, P42to31new*64/36, 1, '4,-2 -> 3,1'])
	#~ writerm.writerow([f4P1to3P2new, -8e3, 3.0, P4P1to3P2new*64/36, 1, '4,1 -> 3,2'])
	#~ writerm.writerow([f3P2to4P3new, -8e3, 3.0, P3P2to4P3new*64/36, 1, '3,2 -> 4,3'])

# used for check coherence with stretched states
    #~ for x in xrange(0,DetRepeats):
        #~ writer.writerow([f4newH, \
                        #~ 0, \
                        #~ DetectionPulseLength, \
                        #~ DetectionPulsePower, \
                        #~ DetectionPulseType, \
                        #~ 'Measure'])
	#~ writer.writerow([f4newH, \
                        #~ 0, \
                        #~ DetectionPulseLength, \
                        #~ DetectionPulsePower*4, \
                        #~ DetectionPulseType, \
                        #~ 'Measure'])
        #~ writer.writerow([f4newH, \
                        #~ Phase[i], \
                        #~ DetectionPulseLength, \
                        #~ DetectionPulsePower, \
                        #~ DetectionPulseType, \
                        #~ 'Measure'])
	#~ writer.writerow([f33to42newH, -8e3, 3.0, P33to42new*64/36, 1, '3,-3 -> 4,-2']) 
	#~ writer.writerow([f42to31newH, -8e3, 3.0, P42to31new*64/36, 1, '4,-2 -> 3,-1']) 
    #~ pulsefile.close() # Close the pulse file
    
    #~ writerm.writerow([Filenames[i]])
    #~ for x in xrange(0,DetRepeats):
        #~ writerm.writerow([f4newH, \
                        #~ 0, \
                        #~ DetectionPulseLength, \
                        #~ DetectionPulsePower, \
                        #~ DetectionPulseType, \
                        #~ 'Measure'])
	#~ writerm.writerow([f4newH, \
                        #~ 0, \
                        #~ DetectionPulseLength, \
                        #~ DetectionPulsePower*4, \
                        #~ DetectionPulseType, \
                        #~ 'Measure'])
        #~ writerm.writerow([f4newH, \
                        #~ Phase[i], \
                        #~ DetectionPulseLength, \
                        #~ DetectionPulsePower, \
                        #~ DetectionPulseType, \
                        #~ 'Measure'])
	#~ writerm.writerow([f33to42newH, -8e3, 3.0, P33to42new*64/36, 1, '3,-3 -> 4,-2']) 
	#~ writerm.writerow([f42to31newH, -8e3, 3.0, P42to31new*64/36, 1, '4,-2 -> 3,-1']) 
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