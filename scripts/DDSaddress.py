

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
from shutil import copyfile


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


################ 2018.07.26######################
f4= 	61287983.7+29.021e3	# 4,4->3,3     	   
f2p= 60981138.82-2.5e3+12.4e3		+12.7e3			# 3,3->42	   
f1p =60590952.61-1.1e3+7.4e3		+7.6e3		# 4,2->3,1         
f0p = 60198904.8+2.6e3+2.5e3		+2.5e3			# 3,1->4,0           
fclock=60006762.1922+0.08749786e3 -0.15e3-0.06e3  -0.49015465e3 	 # 2015.08.26

f4new = 56643638.1	-57e3 - 5.65e3 + 1.5e3

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
#~ P4433_240= 0.1886547	# 2017.1.16
#~ P4433_120= 0.831744 # 2017.1.16
P4433_240=0.06	# 2017.5.11
P4433_120= 0.1964 # 2017.10.16
P4433_80 = 0.4667792 # 2017.10.26
P3040_200us_Pi=0.748225   # 2015.01.08
#~ P3040_90us_Pi = 4.0235 	 # 2015.01.15    
#~ P3040_90us_Pi =  4.1860494	# 2015.03.17   normal B field 400mG
#~ P3040_90us_Pi =  4.3518176  # 2015.03.17   high B field 800mG
StartingFrequency =f4new - 50e3 #+2*dfZeeman #f304M1-deltaf#fclock #-0.1e3  #f304M1-37.5e3     #fclock-0.25e3	#	f304M1-5e3#fclock-20e3#fPiStar-70e3#-15e3#fPiStar-15e3# f304M1-10e3#  -1e3#-2e3#-5e3#f403M1-10e3 #-100e3#f403M1#-30e3#-90e3#-40e3#-60e3 #.140e6#60.040e6#f304M1-18.5e3 #-10e3#-20e3#-10e3 #-10e3  #60.195e6# 60.195e6  # +20e3#60.3e6    #fm1-10e3  #61.360e6#59e6#-10e3#59.800e6   #-10e3#fclock-10e3      #+30e3#faddress	#-10e3	#faddress #-10e3#+25e3#fclock-10e3#+1.3e3    #61.196e6 #f4+20e3#61.150e6	#ftarget#60.1590e6 #59.995e6  #60.180e6 # Hz
StoppingFrequency=f4new - 50e3 #+2*dfZeeman  #f304M1-deltaf#fclock #+0.2e3  #f304M1-37.5e3     #fclock+0.25e3	#	f304M1+5e3#fclock+20e3#fPiStar-70e3#+15e3#f4+10e3#fPiStar+15e3# f304M1+10e3  #+10e3#04M1#+5e3#+10e3#03M1+5e3#-0.5e3#+1e3#+5e3#f403M1-10e3#+30e3   #+30e3#-40e3#f403M1#-70e3#-40e3#-20e3  #160e6#60.060e6#f304M1-17.5e3 #+10e3#+20e3#+10e3#+40e3  #+10e3  #f0#60.215e6#60.215e6    #f4+40e3#60.3e6  #f4#fm1+10e3  #61.400e6#59e6#f4#+10e3#59.820e6  #+10e3#fclock+10e3	 #+50e3#faddress	# faddress#+40e3 #10e3#+25e3#fclock+10e3 #+10e3#+1.3e3  #61.216e6 # f4+40e3#61.170e6   #60.170e6	#ftarget#60.1590e6 #60.159e6 #60.015e6  #60.210e6 
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
y = [0, 0.9, 1.8, 1.3, 2.2, 2.2, 2, 2.4, 2.1, 1.0, 0.6, -0.5, -0.1, -0.6, -0.5, -0.5, -0.5 ] # before 5pm 2017.10.17

x =  np.linspace(0, 16, num=17, endpoint=True)
popt, pcov = curve_fit(fitfunc, x, y)

def frec(time):
	print fitfunc(time-math.floor(time/16.67)*16.67,*popt)*1000
	return fitfunc(time-math.floor(time/16.67)*16.67,*popt)*1000
FrequencyStepSize =0.03e3 # Hz
NumberOfRepeats   = 11# Number of times to repeat the scan


# define the detection pulse
# Typical AFP pulse
#~ DetectionPulseType   =1	   	# 1 for AFP, 2 for Blackman, 9 for CW (no ending), 22 Composite Pi  3 square pulse(phase coherence)
#~ DetectionPulseLength =2	 #0.15   #0.15#0.4  #0.16# 	# ms
#~ DetectionPulsePower  =0.2		#P3040_200us_Pi  #P403M1200us  # P304M1400us*4   #  1.892#   # 1.5/9.0#P304M1#P403M1*4  #/36 #P304M1#P304M1#P3040_piHalf#P304M1#*P403M1#P403M1#0.20874 # 0.2125 #(4,1->3,0) # 0.0985# (for 44->33)  #2.4346 # (3,0->4,0)  #0.3456 #(4,1->3,0)   0.18 #(for 4,4->3,3, 0.2ms)
#~ DetectionPulseHSR     =-6e3		 # Hz (only used for AFP pulses) 
#~ # For Blackman and CW pulses, "HSR" is the phase in units of pi

# Blackman
DetectionPulseType   = 2		# 1 for AFP, 2 for Blackman, 9 for CW (no ending), 22 Composite Pi  3 square pulse(phase coherence)
DetectionPulseLength = 0.12		# typ 0.12 
DetectionPulsePower  = 0.306		
DetectionPulseHSR    = 0		# 0Hz for blackman

# Some typical values
# AFP pulse
# last updated: 2017-6-8
AFPPower0   =0.1		#1.6*0.2*0.7 # W
AFPPower1   =0.19		#1.6*0.2*0.7 # W
AFPPower2   =0.64		# 1.6*0.8*0.7 # W
AFPLength 	 = 3.0 # ms
AFPHSR0    = -4.0e3      
AFPHSR1    = -6.0e3 # Hz
AFPHSR2    = -8.0e3 # Hz

 
fc=f4new		 # 9.1.2015
FreqM1X = fc+ 15e3   #13.3e3-2e3   #10.2e3	# Hz, -1 sideband
FreqM2X = fc+ 30e3   #27.8e3-2e3  #22.3e3   # Hz, -2 sideband
FreqM1Y = fc+ 13e3	#10.7e3-2e3 #14.9e3    # Hz, -1 sideband
FreqM2Y = fc+ 26e3 	#-2e3 #29.5e3   # Hz, -2 sideband
FreqM1Z = fc+ 13e3   #	12.4e3-2e3  #8.5e3 # Hz, -1 sideband
FreqM2Z = fc+ 27e3   #28.4e3-2e3  #19.1e3 # Hz, -2 sideband



# BackupRabi-End

# calculate some stuff
#~ Frequency = np.arange(StartingFrequency, StoppingFrequency+FrequencyStepSize/2.0, \
                      #~ FrequencyStepSize) # in Hz
#~ NumberOfFiles = len(Frequency)

f = f4new - 0e3
#~ f = 58.0e6

print('Making pulsefile ')
pulsefile = open("Gate", "wb") # open pulse file
pulsefile.write(FileComment) # write comment line
writer = csv.writer(pulsefile, dialect='excel-tab')
for i in range(0,17):
	#~ for j in range(0,11):
		#~ print i
		#~ writer.writerow([f+j*2e3+frec(i),DetectionPulseHSR, DetectionPulseLength, DetectionPulsePower , DetectionPulseType, 'Measure'])
		
		#~ writer.writerow([f+frec(i),DetectionPulseHSR, DetectionPulseLength,pow((j/10.0),2)*0.91125 , DetectionPulseType, 'Measure'])
	#~ print pow((i/10.0),2)*0.5
	
	#~ writer.writerow([f+frec(i),DetectionPulseHSR, DetectionPulseLength, DetectionPulsePower, DetectionPulseType, 'Measure'])
	writer.writerow([f,DetectionPulseHSR, DetectionPulseLength, DetectionPulsePower*0, DetectionPulseType, 'Measure'])
	writer.writerow([f,DetectionPulseHSR, DetectionPulseLength, DetectionPulsePower, DetectionPulseType, 'Measure'])
	#~ writer.writerow([f+frec(i),0.5, DetectionPulseLength, DetectionPulsePower , DetectionPulseType, 'Measure'])
	#~ writer.writerow([f+frec(i),0, DetectionPulseLength/2, DetectionPulsePower , DetectionPulseType, 'Measure'])
	
#~ for i in range(-10,11):
	#~ for j in range(0,17):
		#~ print i
		#~ writer.writerow([f+i*0.5e3+frec(j),DetectionPulseHSR, DetectionPulseLength, DetectionPulsePower , DetectionPulseType, 'Measure'])

#~ for i in range(-10,11):
	#~ for j in range(0,17):
		#~ for k in range(0,11):
			#~ writer.writerow([f+i*0.5e3+frec(j)+k*2e3,DetectionPulseHSR, DetectionPulseLength, DetectionPulsePower , DetectionPulseType, 'Measure'])

#~ writer.writerow([20e3,DetectionPulseHSR, DetectionPulseLength, DetectionPulsePower, DetectionPulseType, 'Measure'])
#~ writer.writerow([50e3,DetectionPulseHSR, DetectionPulseLength, DetecionPulsePower, DetectionPulseType, 'Measure'])
#~ writer.writerow([f,DetectionPulseHSR, DetectionPulseLength, DetectionPulsePower, DetectionPulseType, 'Measure'])

pulsefile.close()
subprocess.call(['C:\Users\Yang\Documents\Data\DDScontrol\NewDDS2-Cooling2.0-Cal.exe', 'Gate'])
#~ os.system('copy RAWGate C:\Users\Yang\Documents\Eclipse\CameraGUI\release\DDSaddress.txt')
copyfile('RAWGate','C:/Users/Yang/Documents/Eclipse/CameraGUI/release/DDSaddress.txt')
copyfile('RAWGate','C:/Users/Yang/Documents/Eclipse/CameraGUI/debug/DDSaddress.txt')
copyfile('RAWGate','C:/Users/Yang/Documents/Eclipse/CameraGUI/DDSaddress.txt')


copyfile('RAWGate','C:/Users/Yang/Documents/Eclipse/CameraGUI_V2/release/DDSaddress.txt')
copyfile('RAWGate','C:/Users/Yang/Documents/Eclipse/CameraGUI_V2/debug/DDSaddress.txt')
copyfile('RAWGate','C:/Users/Yang/Documents/Eclipse/CameraGUI_V2/DDSaddress.txt')

pulsefile = open("dummy", "wb") # open pulse file
pulsefile.write(FileComment) # write comment line
writer = csv.writer(pulsefile, dialect='excel-tab')

writer.writerow([58.0e6,-6e3, DetectionPulseLength,DetectionPulsePower*0, DetectionPulseType, 'Measure']) 
#~ writer.writerow([f+frec(i),0, DetectionPulseLength, 0 , DetectionPulseType, 'Measure'])
#~ writer.writerow([f+frec(i),1, DetectionPulseLength/2,0 , DetectionPulseType, 'Measure'])
pulsefile.close()
subprocess.call(['C:\Users\Yang\Documents\Data\DDScontrol\NewDDS2-Cooling2.0-Cal.exe', 'dummy'])
#~ os.system('copy RAWGate C:\Users\Yang\Documents\Eclipse\CameraGUI\release\DDSaddress.txt')
copyfile('RAWdummy','C:/Users/Yang/Documents/Eclipse/CameraGUI/release/DDSadummy.txt')
copyfile('RAWdummy','C:/Users/Yang/Documents/Eclipse/CameraGUI/debug/DDSadummy.txt')
copyfile('RAWdummy','C:/Users/Yang/Documents/Eclipse/CameraGUI/DDSadummy.txt')

copyfile('RAWdummy','C:/Users/Yang/Documents/Eclipse/CameraGUI_V2/release/DDSadummy.txt')
copyfile('RAWdummy','C:/Users/Yang/Documents/Eclipse/CameraGUI_V2/debug/DDSadummy.txt')
copyfile('RAWdummy','C:/Users/Yang/Documents/Eclipse/CameraGUI_V2/DDSadummy.txt')



pulsefile = open("analysis", "wb") # open pulse file
pulsefile.write(FileComment) # write comment line
writer = csv.writer(pulsefile, dialect='excel-tab')

writer.writerow([f4new,-6e3, 3,0.2*0, 1, 'Measure'])	# analysis pulse
#~ writer.writerow([f+frec(i),0, DetectionPulseLength, 0 , DetectionPulseType, 'Measure'])
#~ writer.writerow([f+frec(i),1, DetectionPulseLength/2,0 , DetectionPulseType, 'Measure'])
pulsefile.close()
subprocess.call(['C:\Users\Yang\Documents\Data\DDScontrol\NewDDS2-Cooling2.0-Cal.exe', 'analysis'])
#~ os.system('copy RAWGate C:\Users\Yang\Documents\Eclipse\CameraGUI\release\DDSaddress.txt')
#~ os.system('copy RAWpostCool+RAWanalysis analysis.txt')	# with post cooling
os.system('copy RAWanalysis analysis.txt')	# without post cooling
copyfile('analysis.txt','C:/Users/Yang/Documents/Eclipse/CameraGUI/release/DDSanalysis.txt')
copyfile('analysis.txt','C:/Users/Yang/Documents/Eclipse/CameraGUI/debug/DDSanalysis.txt')
copyfile('analysis.txt','C:/Users/Yang/Documents/Eclipse/CameraGUI/DDSanalysis.txt')

copyfile('analysis.txt','C:/Users/Yang/Documents/Eclipse/CameraGUI_V2/release/DDSanalysis.txt')
copyfile('analysis.txt','C:/Users/Yang/Documents/Eclipse/CameraGUI_V2/debug/DDSanalysis.txt')
copyfile('analysis.txt','C:/Users/Yang/Documents/Eclipse/CameraGUI_V2/DDSanalysis.txt')

#os.system("del Cool List RAWCool")
if DelTempFiles == 1 :
	#~ os.system("del Cool List RAWCool reset")	
	os.system("del Cool List reset")	
	

	