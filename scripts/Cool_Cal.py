#####################################################################
#   This file only calculates the cooling and transferring pulses, which can be then spliced into the whole gate sequence,  
#   last updated 2015-5-1,  Yang
#####################################################################

# import libraries
import sys, math
import csv         # for writing the pulse files
import numpy as np # to calculate the frequency steps
import os, subprocess          # calls to operating system
import string      # string manipulation
import random

from scipy.optimize import curve_fit
DelTempFiles = 0 # Clean up after we're done?

# define some constants
FilenameHead = 'Cool_Cal'   # filenames will start with this (can include directory, but use forward slash)
FileComment = 'Cool\n'  # Comment line at head of pulse files (must end with \n)
print (FileComment)

# BackupRabi-Begin

f304P1=60060974-0.45e3		 # 30->4,1, low field
#~ delta=54333.9062 +48.458e3   # 07-11-2014

df=2*53.097e3  #	+  48.6726e3	#7.16

#~ P3P14P1_150us=0.764  # 2014-7-7
P3P14P1_150us=0.637  # 2014-8-12
P304P1_150us=1.332  #2014-7-8
P304P1_100us=3.11  #2014-7-23

#~ P3040_200us_Pi=0.4096  # 2014-7-14, low field 
#~ P3040_200us_Pi= 0.4096 # 2014-8-10 
#~ P3040_200us_Pi = 0.366  # 2014-8-11
#~ P3040_200us_Pi=	0.409  # 2014-9-3
P3040_200us_Pi=  0.442895829  # 9.15
P3040_200us_Pi=   0.8	# 2014-9-22


################ 2018.08.07 ######################
f4= 	61287983.7+29.021e3	# 4,4->3,3     	   
f2p= 60981138.82-2.5e3+12.4e3		+12.7e3			# 3,3->42	   
f1p =60590952.61-1.1e3+7.4e3		+7.6e3		# 4,2->3,1         
f0p = 60198904.8+2.6e3+2.5e3		+2.5e3			# 3,1->4,0           
fclock=60006762.1922+0.08749786e3 -0.15e3-0.06e3  -0.49015465e3 	 # 2015.08.26

f4newH = 56595100 
f4newL = f4newH + 2.032e6 + 46e3   # low field to check the unexplained spin echo phase shift 2025.01.23
f4new = f4newH +481

#~ f4new = 58661697.8708+1.2e3-2.9e3+0.5e3-1.4e3+0.9e3+0.6e3-2e3-1330e3+53.8e3	#high field

P304P1_300us=0.308  #2014-7-24
#~ P3P14P1_150us=0.637  # 2014-8-12
P3P14P1_150us=0.612 # 2014-9-4
#~ P3P14P1_150usHalf= 0.2274 # 2014-9-5
P3P14P1_150usHalf= 0.2146 # 2014-9-15
#~ fclock=fclock-1e3


#~ P3P14P1_150us=1.555  # 2014-9-22
#~ P304P1_300us=0.605   	# 2014-9-22
#~ P3040_200us_Pi= 0.8	# 2014-9-22

#~ dfZeeman=60.0e3	#+  Zeeman spliting	# 2014.9.24
#~ dfZeeman2=120e3	#+  Zeeman spliting	# 2014.9.22 to match timing



#~ P3040_200us_Pi=0.52   #  2014.9.26
P3P14P1_150us=	0.8427	#  2014.9.26
#~ P3P14P1_150us=	0.784	#  2014.10.13
#~ P3P14P1_150us=	0.794	#  2014.10.14
#~ P304P1_300us= 0.3655 	#  2014.9.26
#~ dfZeeman	=65.3e3	#+  Zeeman spliting	# 2014.9.26
P304P1_150us=1.28         # 2014.9.29
#~ P3040_200us_Pi= 0.4  # 2014.10.10
P3040_200us_Pi= 0.4016  # 2014.10.15
#~ P3040_200us_Pi= 0.4217 # 2014.10.14 STRONG FIELD
#~ P304P1_300us= 0.3655 	#  2014.9.26
P304P1_300us=  	0.372  #  2014.10.16
#~ dfZeeman	=60.150e3	#+  Zeeman spliting	# 2014.10.11
#~ dfZeeman=87.814e3  # Zeeman spliting	# 2014.10.15
P3P14P1_60us=	5.53   # 2014.10.21
#~ dfZeeman=87.814e3+140.96  # Zeeman spliting	# 2014.10.22
#~ dfZeeman=95854.96 # Zeeman spliting	# 2014.11.13
#~ dfZeeman=93347.06 # Zeeman spliting	# 2015.1.20
dfZeeman=192920  # for normal B field #2015.3.11
#~ dfZeeman=371040 - 2.3e3  # for strong B field, 2015.3.17 

#~ P3040_200us_Pi=0.4356   # 2014.10.23
P3040_200us_Pi= 0.4761  # 2014.11.4
P3040_200us_Pi=0.4618   # 2014.11.5
P3040_100us_Pi=1.917  # 2014.11.6
P3040_200us_Pi=0.4802   # 2014.11.7  strong OP field
P3040_100us_Pi_Square=0.38   # 2014.11.7  strong OP field

P3040_200us_Pi=0.6937  # 2014.11.13
P3040_200us_Pi=0.7398  # 2014.11.25
P3P14P1_120us=2.074 # 2014.11.16
P304P1_300us=  	0.585  #  2014.11.13
#~ P3040_200us_Pi=0.6724  # spin echo one pi 2014.11.18

#~ P304P1_300us=  	0.5  #  2014.11.21

P3P14P1_120us=2.232 # 2014.11.26
P3040_200us_Pi=0.7396  # 2014.11.25
P304P1_300us=  	0.47  #  2014.11.26

P3040_200us_Pi=0.748225   # 2015.01.08
#~ P3040_90us_Pi = 4.0235 	 # 2015.01.15    
#~ P3040_90us_Pi =  4.1860494	# 2015.03.17   normal B field 400mG
#~ P3040_90us_Pi =  4.3518176  # 2015.03.17   high B field 800mG
StartingFrequency =fclock#+2*dfZeeman #f304M1-deltaf#fclock #-0.1e3  #f304M1-37.5e3     #fclock-0.25e3	#	f304M1-5e3#fclock-20e3#fPiStar-70e3#-15e3#fPiStar-15e3# f304M1-10e3#  -1e3#-2e3#-5e3#f403M1-10e3 #-100e3#f403M1#-30e3#-90e3#-40e3#-60e3 #.140e6#60.040e6#f304M1-18.5e3 #-10e3#-20e3#-10e3 #-10e3  #60.195e6# 60.195e6  # +20e3#60.3e6    #fm1-10e3  #61.360e6#59e6#-10e3#59.800e6   #-10e3#fclock-10e3      #+30e3#faddress	#-10e3	#faddress #-10e3#+25e3#fclock-10e3#+1.3e3    #61.196e6 #f4+20e3#61.150e6	#ftarget#60.1590e6 #59.995e6  #60.180e6 # Hz
StoppingFrequency=fclock#+2*dfZeeman  #f304M1-deltaf#fclock #+0.2e3  #f304M1-37.5e3     #fclock+0.25e3	#	f304M1+5e3#fclock+20e3#fPiStar-70e3#+15e3#f4+10e3#fPiStar+15e3# f304M1+10e3  #+10e3#04M1#+5e3#+10e3#03M1+5e3#-0.5e3#+1e3#+5e3#f403M1-10e3#+30e3   #+30e3#-40e3#f403M1#-70e3#-40e3#-20e3  #160e6#60.060e6#f304M1-17.5e3 #+10e3#+20e3#+10e3#+40e3  #+10e3  #f0#60.215e6#60.215e6    #f4+40e3#60.3e6  #f4#fm1+10e3  #61.400e6#59e6#f4#+10e3#59.820e6  #+10e3#fclock+10e3	 #+50e3#faddress	# faddress#+40e3 #10e3#+25e3#fclock+10e3 #+10e3#+1.3e3  #61.216e6 # f4+40e3#61.170e6   #60.170e6	#ftarget#60.1590e6 #60.159e6 #60.015e6  #60.210e6 
# 61.387e6 is the resonace of unshifted atoms
DetRepeats = 	1		# how many detection pulse do you want to repeat
P3040_90us_Pi =  3.85786313 #2015.04.24 normal B field 400mG
P3040_90us_Pi =  3.7276
##################################################
### CLOCK TRANSITION FREQ: 60.0068MHz ############
##################################################
def fitfunc(x,a,b,c,d,p1,p2,p3):
	return a*np.cos(2*math.pi*x*0.060+p1)+b*np.cos(2*math.pi*0.120+p2)+c*np.cos(2*math.pi*x*0.18+p3)
#~ y =[0,0.3, 1.9, 1.5, 1.5,1.7,1.2,1.6,1.4,0.9,-0.1,-0.5,-0.3,-0.5,-0.3,-0.1,0.1] # after 5pm
#~ y = [0,0.7,1.3,2.1,2.6,2.8,2.4,3.2,2.8,3.1,1.2,1.2,0.3,0.4,-0.1,0.3,-0.2]	# before 5pm
#~ y = [0, 0.9, 1.8, 1.3, 2.2, 2.2, 2, 2.4, 2.1, 1.0, 0.6, -0.5, -0.1, -0.6, -0.5, -0.5, -0.5 ] # before 5pm 2017.10.17
y = [0.85, 1.24, 2.23, 0.87, -0.39, 0.03, 0.06,0.51, 0.08, 0.12,  -0.62, -0.01, 1.66, 1.36, 0.51, 1.1, 0.85 ] # after 5pm 20191121
for i in xrange(0,17):
	y[i] += 0.39

x =  np.linspace(0, 16, num=17, endpoint=True)
popt, pcov = curve_fit(fitfunc, x, y)

def frec(time):
	#print fitfunc(time-math.floor(time/16.67)*16.67,*popt)*1000
	return fitfunc(time-math.floor(time/16.67)*16.67,*popt)*1000
FrequencyStepSize =0.03e3 # Hz
NumberOfRepeats   = 11# Number of times to repeat the scan


# define the detection pulse
# Typical square pulse
DetectionPulseType   =2 	 # 1 for AFP, 2 for Blackman, 9 for CW (no ending), 22 Composite Pi  3 square pulse(phase coherence)
DetectionPulseLength =0.045	 #0.15   #0.15#0.4  #0.16# 	# ms
DetectionPulsePower  = P3040_90us_Pi  	#P3040_200us_Pi  #P403M1200us  # P304M1400us*4   #  1.892#   # 1.5/9.0#P304M1#P403M1*4  #/36 #P304M1#P304M1#P3040_piHalf#P304M1#*P403M1#P403M1#0.20874 # 0.2125 #(4,1->3,0) # 0.0985# (for 44->33)  #2.4346 # (3,0->4,0)  #0.3456 #(4,1->3,0)   0.18 #(for 4,4->3,3, 0.2ms)
DetectionPulseHSR    =0# -6.0e3 # Hz (only used for AFP pulses) 
# For Blackman and CW pulses, "HSR" is the phase in units of pi


# Some typical values
# AFP pulse
# last updated: 2015-6-7 (2021720 used for TiSa cooling with 3 ms AFP pulses)
#~ AFPPower0   =0.00*(0.075/0.1)
#~ AFPPower1   =0.00*(0.075/0.1)	
#~ AFPPower2   =0.00*(0.075/0.1)	

AFPPower0   =0.1*(0.075/0.1)
AFPPower1   =0.19*(0.075/0.1)	
AFPPower2   =0.64*(0.075/0.1)		
AFPLength 	 = 3.0 # ms
AFPHSR0    = -4.0e3      
AFPHSR1    = -6.0e3 # Hz
AFPHSR2    = -6.0e3 # Hz


#Parameters for testing in deeper lattice for 3ms pulses
#~ AFPPower0   =0.245
#~ AFPPower1   =0.648
#~ AFPPower2   =0.64*(0.075/0.1)		
#~ AFPLength 	 = 3.0 # ms
#~ AFPHSR0    = -12.0e3      
#~ AFPHSR1    = -12.0e3 # Hz
#~ AFPHSR2    = -8.0e3 # Hz

# Check 20191226 to use the following settings
#Parameters for testing in deeper lattice for 1ms pulses
#Power = 1.4 for 10k, -2 sideband. 
#Power = 1 for 10k -1 sideband 
#scale other sweep ranges accordingly
#~ AFPPower0   =0.36*0.25*(10/6)**2
#~ AFPPower1   = 0.5*0.25 *(10/6)**2
#~ AFPPower0   =1.4
#~ AFPPower1   = 2.5
#~ AFPPower2   =0.8*0.25	
#~ AFPLength 	 =1 # ms
#~ AFPHSR0    = -10.0e3      
#~ AFPHSR1    = -10.0e3 # Hz
#~ AFPHSR2    = -6.0e3 # Hz

#Parameters for testing in deeper lattice for 1ms pulses (20210720 this block is used for 847 cooling)
#~ AFPPower0   =1.
#~ AFPPower1   = 1.4
#~ ##~ AFPPower0   =1.4
#~ ##~ AFPPower1   = 2.5
#~ AFPPower2   =0.8	
#~ AFPLength 	 = 1 # ms
#~ AFPHSR0    = -8.0e3      
#~ AFPHSR1    = -8.0e3 # Hz
#~ AFPHSR2    = -6.0e3 # Hz

#~ #Parameters for testing in deeper lattice for 2ms pulses
#~ #Power = 1.4 for 10k, -2 sideband. 
#~ #Power = 1 for 10k -1 sideband 
#~ #scale other sweep ranges accordingly
#~ AFPPower0   =0.36*0.25*(10/6)**2
#~ AFPPower1   = 0.5*0.25 *(10/6)**2
##~ AFPPower0   =1.4
##~ AFPPower1   = 2.5
#~ AFPPower2   =0.8*0.25	
#~ AFPLength 	 =2 # ms
#~ AFPHSR0    = -8.0e3      
#~ AFPHSR1    = -8.0e3 # Hz
#~ AFPHSR2    = -6.0e3 # Hz
 
fc=f4new
# updated 2017.12.07
FreqM1X = fc+ 18.5e3 #19.3e3 #20e3 #19.3e3		#	20.873e3	#19e3   	#13.3e3-2e3   	#10.2e3	# Hz, -1 sideband
FreqM2X = fc+ 37e3 #38.6e3 #40e3 #38.6e3		#	42.156e3	#38e3   	#27.8e3-2e3  	#22.3e3	# Hz, -2 sideband
FreqM1Y = fc+ 15e3 #15e3#16.4e3#16e3 #16.4e3		#	16.332e3	#17e3		#10.7e3-2e3 		#14.9e3	# Hz, -1 sideband
FreqM2Y = fc+ 30e3 #30e3#32.8e3#32e3 #32.8e3		#	32.566e3	#33e3 	#-2e3 		#29.5e3	# Hz, -2 sideband
FreqM1Z = fc+ 12e3 #12.4e3#13e3 #12.4e3		#	14.317e3   	#12.4e3-2e3	#8.5e3				# Hz, -1 sideband
FreqM2Z = fc+ 24e3 #24.8e3#26e3 #24.8e3		#	29.015e3   	#28.4e3-2e3	#19.1e3				# Hz, -2 sideband

#~ (20210720 this block is used for 847 cooling)						ASH USED:
#~ FreqM1X = fc+24e3  #23.5e3   #13.3e3-2e3   #10.2e3	# Hz, -1 sideband          	24
#~ FreqM2X = fc+48e3  #47e3   #27.8e3-2e3  #22.3e3   # Hz, -2 sideband			48
#~ FreqM1Y = fc+20e3  #19e3	#10.7e3-2e3 #14.9e3    # Hz, -1 sideband			20
#~ FreqM2Y = fc+40e3  #38e3	#-2e3 #29.5e3   # Hz, -2 sideband				40
#~ FreqM1Z = fc+ 19e3 #19.2e3  	#12.4e3-2e3  #8.5e3 # Hz, -1 sideband		19
#~ FreqM2Z = fc+ 38e3 #38.4 #28.4e3-2e3  #19.1e3 # Hz, -2 sideband			38


# BackupRabi-End

# calculate some stuff
#~ Frequency = np.arange(StartingFrequency, StoppingFrequency+FrequencyStepSize/2.0, \
                      #~ FrequencyStepSize) # in Hz
#~ NumberOfFiles = len(Frequency)

Phase= np.arange (0.0,0.01,0.25)  #phase in units of pi
NumberOfFiles = len(Phase)

#~ Power = P3040_90us_Pi*((np.arange(0.9, 1.1,0.01))**2)
#~ print(Power)

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
#writer.writerow([58.5e6, 0.0, 5.0, 0., 3, 'Dummy']) # Dummy pulse

writer.writerow([58.0e6, 0.0, 10.0, 0., 1, 'Dummy']) # Dummy pulse

####### Begin cooling sequence definition #######

numcool =30


#~ tstart = 52
#~ tx2 = 5	# 5 (was 3.5)
#~ ty1 = 7.7
#~ ty2= 12.7	# 12.7 (was 11.7)
#~ tz1 = 15.4
#~ tz2 = 20.4	# 20.4 (was 18.9)
#~ ttotal = 23.1
#~ t=0

# --- update on 20191122
tstart = 52
tx2 = 1.2
ty1 = 2.8
ty2= 4
tz1 = 5.6
tz2 = 6.8	
ttotal = 8.4
t=0
# --- update on 20191122


for i in xrange(0,numcool): # Typical cooling sequence (-2, -1)
	#~ t = tstart+i*ttotal
	#~ writer.writerow([FreqM2X+frec(t), AFPHSR2, AFPLength, AFPPower2, 1, 'X-2 pulse %d'%(i+1)]) # -2 cooling pulse
	#~ writer.writerow([FreqM1X+frec(t+tx2), AFPHSR1, AFPLength, AFPPower1, 1, 'X-1 pulse %d'%(i+1)]) # -1 cooling pulse
	#~ writer.writerow([FreqM2Y+frec(t+ty1), AFPHSR2, AFPLength,  AFPPower2, 1, 'Y-2 pulse %d'%(i+1)]) # -2 cooling pulse
	#~ writer.writerow([FreqM1Y+frec(t+ty2), AFPHSR1, AFPLength,  AFPPower1, 1, 'Y-1 pulse %d'%(i+1)]) # -1 cooling pulse
	#~ writer.writerow([FreqM2Z+frec(t+tz1), AFPHSR2, AFPLength, AFPPower2, 1, 'Z-2 pulse %d'%(i+1)]) # -2 cooling pulse
	#~ writer.writerow([FreqM1Z+frec(t+tz2), AFPHSR1, AFPLength, AFPPower1, 1, 'Z-1 pulse %d'%(i+1)]) # -1 cooling pulse
	
	#~ t = tstart+i*ttotal
	#~ writer.writerow([FreqM2X+frec(t), AFPHSR1, AFPLength, AFPPower1, 1, 'X-2 pulse %d'%(i+1)]) # -2 cooling pulse
	#~ writer.writerow([FreqM1X+frec(t+tx2), AFPHSR0, AFPLength, AFPPower0, 1, 'X-1 pulse %d'%(i+1)]) # -1 cooling pulse
	#~ writer.writerow([FreqM2Y+frec(t+ty1), AFPHSR1, AFPLength,  AFPPower1, 1, 'Y-2 pulse %d'%(i+1)]) # -2 cooling pulse
	#~ writer.writerow([FreqM1Y+frec(t+ty2), AFPHSR0, AFPLength,  AFPPower0, 1, 'Y-1 pulse %d'%(i+1)]) # -1 cooling pulse
	#~ writer.writerow([FreqM2Z+frec(t+tz1), AFPHSR1, AFPLength, AFPPower1, 1, 'Z-2 pulse %d'%(i+1)]) # -2 cooling pulse
	#~ writer.writerow([FreqM1Z+frec(t+tz2), AFPHSR0, AFPLength, AFPPower0, 1, 'Z-1 pulse %d'%(i+1)]) # -1 cooling pulse
	
	#no 60 Hz calib.
	writer.writerow([FreqM2X, AFPHSR1, AFPLength, AFPPower1, 1, 'X-2 pulse %d'%(i+1)]) # -2 cooling pulse
	writer.writerow([FreqM1X, AFPHSR0, AFPLength, AFPPower0, 1, 'X-1 pulse %d'%(i+1)]) # -1 cooling pulse
	writer.writerow([FreqM2Y, AFPHSR1, AFPLength,  AFPPower1, 1, 'Y-2 pulse %d'%(i+1)]) # -2 cooling pulse
	writer.writerow([FreqM1Y, AFPHSR0, AFPLength,  AFPPower0, 1, 'Y-1 pulse %d'%(i+1)]) # -1 cooling pulse
	writer.writerow([FreqM2Z, AFPHSR1, AFPLength, AFPPower1, 1, 'Z-2 pulse %d'%(i+1)]) # -2 cooling pulse
	writer.writerow([FreqM1Z, AFPHSR0, AFPLength, AFPPower0, 1, 'Z-1 pulse %d'%(i+1)]) # -1 cooling pulse
	
	#~ # with 60 Hz calib.
	#~ t = tstart+i*ttotal
	#~ writer.writerow([FreqM2X+frec(t), AFPHSR1, AFPLength, AFPPower1, 1, 'X-2 pulse %d'%(i+1)]) # -2 cooling pulse
	#~ writer.writerow([FreqM1X+frec(t+tx2), AFPHSR0, AFPLength, AFPPower0, 1, 'X-1 pulse %d'%(i+1)]) # -1 cooling pulse
	#~ writer.writerow([FreqM2Y+frec(t+ty1), AFPHSR1, AFPLength,  AFPPower1, 1, 'Y-2 pulse %d'%(i+1)]) # -2 cooling pulse
	#~ writer.writerow([FreqM1Y+frec(t+ty2), AFPHSR0, AFPLength,  AFPPower0, 1, 'Y-1 pulse %d'%(i+1)]) # -1 cooling pulse
	#~ writer.writerow([FreqM2Z+frec(t+tz1), AFPHSR1, AFPLength, AFPPower1, 1, 'Z-2 pulse %d'%(i+1)]) # -2 cooling pulse
	#~ writer.writerow([FreqM1Z+frec(t+tz2), AFPHSR0, AFPLength, AFPPower0, 1, 'Z-1 pulse %d'%(i+1)]) # -1 cooling pulse
	
for i in xrange(0,10): # Typical cooling sequence (-2, -1)

	
	#no 60 Hz calib.  Commented 20220301  
	writer.writerow([FreqM2X, AFPHSR1, AFPLength, AFPPower1, 1, 'X-2 pulse %d'%(i+1)]) # -2 cooling pulse
	writer.writerow([FreqM1X, AFPHSR2, AFPLength, AFPPower0, 1, 'X-1 pulse %d'%(i+1)]) # -1 cooling pulse
	writer.writerow([FreqM2Y, AFPHSR1, AFPLength,  AFPPower1, 1, 'Y-2 pulse %d'%(i+1)]) # -2 cooling pulse
	writer.writerow([FreqM1Y, AFPHSR2, AFPLength,  AFPPower0, 1, 'Y-1 pulse %d'%(i+1)]) # -1 cooling pulse
	writer.writerow([FreqM2Z, AFPHSR1, AFPLength, AFPPower1, 1, 'Z-2 pulse %d'%(i+1)]) # -2 cooling pulse
	writer.writerow([FreqM1Z, AFPHSR2, AFPLength, AFPPower0, 1, 'Z-1 pulse %d'%(i+1)]) # -1 cooling pulse
	
	#~ #no 60 Hz calib.
	#~ writer.writerow([FreqM2X, AFPHSR2, AFPLength, AFPPower1, 1, 'X-2 pulse %d'%(i+1)]) # -2 cooling pulse
	#~ writer.writerow([FreqM1X, AFPHSR2, AFPLength, AFPPower0, 1, 'X-1 pulse %d'%(i+1)]) # -1 cooling pulse
	#~ writer.writerow([FreqM2Y, AFPHSR2, AFPLength,  AFPPower1, 1, 'Y-2 pulse %d'%(i+1)]) # -2 cooling pulse
	#~ writer.writerow([FreqM1Y, AFPHSR2, AFPLength,  AFPPower0, 1, 'Y-1 pulse %d'%(i+1)]) # -1 cooling pulse
	#~ writer.writerow([FreqM2Z, AFPHSR2, AFPLength, AFPPower1, 1, 'Z-2 pulse %d'%(i+1)]) # -2 cooling pulse
	#~ writer.writerow([FreqM1Z, AFPHSR2, AFPLength, AFPPower0, 1, 'Z-1 pulse %d'%(i+1)]) # -1 cooling pulse
	
	#~ # with 60 Hz calib.
	#~ writer.writerow([FreqM2X+frec(t), AFPHSR2, AFPLength, AFPPower1, 1, 'X-2 pulse %d'%(i+1)]) # -2 cooling pulse
	#~ writer.writerow([FreqM1X+frec(t+tx2), AFPHSR2, AFPLength, AFPPower0, 1, 'X-1 pulse %d'%(i+1)]) # -1 cooling pulse
	#~ writer.writerow([FreqM2Y+frec(t+ty1), AFPHSR2, AFPLength,  AFPPower1, 1, 'Y-2 pulse %d'%(i+1)]) # -2 cooling pulse
	#~ writer.writerow([FreqM1Y+frec(t+ty2), AFPHSR2, AFPLength,  AFPPower0, 1, 'Y-1 pulse %d'%(i+1)]) # -1 cooling pulse
	#~ writer.writerow([FreqM2Z+frec(t+tz1), AFPHSR2, AFPLength, AFPPower1, 1, 'Z-2 pulse %d'%(i+1)]) # -2 cooling pulse
	#~ writer.writerow([FreqM1Z+frec(t+tz2), AFPHSR2, AFPLength, AFPPower0, 1, 'Z-1 pulse %d'%(i+1)]) # -1 cooling pulse

#~ writer.writerow([f4new+24e3, -6e3,3 , 0.2, 1, 'X-2 pulse %d'%(i+1)])
#~ for i in xrange(0,5): # Typical cooling sequence (-2, -1)

	#~ writer.writerow([FreqM2X, AFPHSR1, AFPLength, AFPPower1, 1, 'X-2 pulse %d'%(i+1)]) # -2 cooling pulse
	#~ writer.writerow([FreqM1X, AFPHSR0, AFPLength, AFPPower0, 1, 'X-1 pulse %d'%(i+1)]) # -1 cooling pulse
	#~ writer.writerow([FreqM2Y, AFPHSR1, AFPLength,  AFPPower1, 1, 'Y-2 pulse %d'%(i+1)]) # -2 cooling pulse
	#~ writer.writerow([FreqM1Y, AFPHSR0, AFPLength,  AFPPower0, 1, 'Y-1 pulse %d'%(i+1)]) # -1 cooling pulse
	#~ writer.writerow([FreqM2Z, AFPHSR1, AFPLength, AFPPower1, 1, 'Z-2 pulse %d'%(i+1)]) # -2 cooling pulse
	#~ writer.writerow([FreqM1Z, AFPHSR0, AFPLength, AFPPower0, 1, 'Z-1 pulse %d'%(i+1)]) # -1 cooling pulse
	
#~ ttotal2 = 12.6 	
#~ t = t+ttotal
#~ for i in xrange(0,10): #last 10 cycles only -1 pulse
	#~ t = t+i*ttotal2
	#~ writer.writerow([FreqM1X+frec(t), AFPHSR0, AFPLength, AFPPower0, 1, 'X-1 pulse %d'%(i+1)]) # -1 cooling pulse
	#~ writer.writerow([FreqM1Y+frec(t+4.2), AFPHSR0, AFPLength,  AFPPower0, 1, 'Y-1 pulse %d'%(i+1)]) # -1 cooling pulse
	#~ writer.writerow([FreqM1Z+frec(t+8.4), AFPHSR0, AFPLength, AFPPower0, 1, 'Z-1 pulse %d'%(i+1)]) # -1 cooling pulse
	
#~ for i in xrange(0,numcool): # Typical cooling sequence (-2, -1)
	
	#~ writer.writerow([FreqM2X, AFPHSR1, AFPLength, AFPPower1, 1, 'X-2 pulse %d'%(i+1)]) # -2 cooling pulse
	#~ writer.writerow([FreqM1X, AFPHSR0, AFPLength, AFPPower0, 1, 'X-1 pulse %d'%(i+1)]) # -1 cooling pulse
	#~ writer.writerow([FreqM2Y, AFPHSR1, AFPLength,  AFPPower1, 1, 'Y-2 pulse %d'%(i+1)]) # -2 cooling pulse
	#~ writer.writerow([FreqM1Y, AFPHSR0, AFPLength,  AFPPower0, 1, 'Y-1 pulse %d'%(i+1)]) # -1 cooling pulse
	#~ writer.writerow([FreqM2Z, AFPHSR1, AFPLength, AFPPower1, 1, 'Z-2 pulse %d'%(i+1)]) # -2 cooling pulse
	#~ writer.writerow([FreqM1Z, AFPHSR0, AFPLength, AFPPower0, 1, 'Z-1 pulse %d'%(i+1)]) # -1 cooling pulse

#~ for i in xrange(0,10): #last 10 cycles only -1 pulse
	#~ writer.writerow([FreqM1X, AFPHSR1, AFPLength, AFPPower1, 1, 'X-1 pulse %d'%(i+1)]) # -1 cooling pulse
	#~ writer.writerow([FreqM1X, AFPHSR1, AFPLength,  AFPPower1, 1, 'Y-1 pulse %d'%(i+1)]) # -1 cooling pulse
	#~ writer.writerow([FreqM1Z, AFPHSR1, AFPLength, AFPPower1, 1, 'Z-1 pulse %d'%(i+1)]) # -1 cooling pulse


####### Begin transfering sequence definition #######

#~ writer.writerow([f4, -6000, 3, 1.6*0.1*0.7,  1, '4,4->3,3']) # 2014.10.10, old power is 0.05W 
#~ writer.writerow([f2p, -6000, 3, 1.6*1.5*0.7,  1, '3,3->4,2']) # 2014.10.10: 1.5W 
#~ writer.writerow([f1p, -6000, 3, 1.6*0.3*0.7,  1, '4,2->3,1']) # 2014.10.10: 0.8W 
#~ writer.writerow([f0p, -6000, 3, 1.6*0.25*0.7,  1, '3,1->4,0']) # 2014.10.10: 025W 


#~ writer.writerow([fclock, -6000, 3, 1.6*0.7,  1, '3,0->4,0'])


#~ writer.writerow([StartingFrequency, 0.0, 0.1, 0., 2, 'Dummy']) # Dummy pulse


pulsefile.close() # Close the cooling pulse file

os.system('copy '+Coolfilename+' Cool')
#os.system('C:\Users\Yang\Documents\Data\DDScontrol\NewDDS2-Cooling2.0-Cal.exe Cool')
subprocess.call(['C:\Users\Yang\Documents\Data\DDScontrol\NewDDS2-Cooling2.0-Cal.exe', 'Cool'])
#~ os.system('copy RAWCool C:\Users\Yang\Documents\Eclipse\CameraGUI\release\DDScool.txt')
#~ os.system('copy RAWCool C:\Users\Yang\Documents\Eclipse\CameraGUI\DDScool.txt')

#~ print('Making pulsefile ')
#~ pulsefile = open("Gate", "wb") # open pulse file
#~ pulsefile.write(FileComment) # write comment line
#~ writer = csv.writer(pulsefile, dialect='excel-tab')

#~ writer.writerow([f4new,DetectionPulseHSR, DetectionPulseLength, DetectionPulsePower, DetectionPulseType, 'Measure'])
#~ subprocess.call(['C:\Users\Yang\Documents\Data\DDScontrol\NewDDS2-Cooling2.0-Cal.exe', 'Gate'])
#~ os.system('copy RAWGate C:\Users\Yang\Documents\Eclipse\CameraGUI\release\DDSaddress.txt')
#~ os.system('copy RAWGate C:\Users\Yang\Documents\Eclipse\CameraGUI\DDSaddress.txt')

#os.system("del Cool List RAWCool")
if DelTempFiles == 1 :
	#~ os.system("del Cool List RAWCool reset")	
	os.system("del Cool List reset")
	

	