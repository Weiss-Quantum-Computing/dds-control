#~ # Write pulse files for NewDDS2-version3.exe
# Ted Corcovilos 20110308 (Rewrite for easier changes)
# NB: Check that all 'float' numbers contain an explicit decimal point

# import libraries

import sys, math
import csv         # for writing the pulse files
import numpy as np # to calculate the power steps
import os, subprocess          # calls to operating system
import string      # string manipulation
from scipy.optimize import fsolve  # solve for magnetic field by transition frequncy

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
FilenameHead = 'Powerscan-RF'   # filenames will start with this (can include directory, but use forward slash)
FileComment = 'Cool\n'  # Comment line at head of pulse files (must end with \n)
print('Pulse file comment line: ' + FileComment.strip())


################ 2019.05.02 #####################
#~ f4= 	61287983.7+29.021e3	# 4,4->3,3     	   
#~ f2p= 60981138.82-2.5e3+12.4e3		+12.7e3			# 3,3->42	   
#~ f1p =60590952.61-1.1e3+7.4e3		+7.6e3		# 4,2->3,1         
#~ f0p = 60198904.8+2.6e3+2.5e3		+2.5e3			# 3,1->4,0           
#~ fclock=60006762.1922+0.08749786e3 -0.15e3-0.06e3  -0.49015465e3	 # 2015.08.26
  

f4new = 56595100 + 160

# f4newH for magnetic field measurement 
f4newx = 57615738.1 - 2.3e3 + 5.75e3 + 0e3   	     # for field  (956, 0, -38)
f4newy = 57615738.1  - 43.4e3 + 6e3    # for field  (0, 975, -38)
#~ print(f4new)
print('f4new (4,-4 -> 3,-3 transition) = %.1f Hz' % f4new)

#~ f4new =f4new+1e3
#~ f4new = 58661697.8708+1.2e3-2.9e3+0.5e3-1.4e3+0.9e3+0.6e3-2e3-1330e3+53.8e3-0.4e3	#high field (double)
 
##### initiated on 2018.02.02 #####
##### microwave horn rotated and powers updated on 2018.02.06#########
fclock = 60006297.8708+0.4e3-0.17047265e3+0.2e3-0.140e3+0.215e3		# updated 20180806


#~ f31to40newH = (fclock-f4newH)*6/7+f4newH  # Definition value
#~ f31to40newH =f4newH +2.92797e6                           # theoretical value under the high field
# 20180803
f32to41newShortSpinEcho = (fclock-f4new)*4/7+f4new + 1.2e3 -3.21e3+0.3e3+0.1e3+0.1e3
f42to31newShortSpinEcho = f32to41newShortSpinEcho

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
Pclock_Pi_120us =0.8019 	# for Blackman 
Pclock_Pi_200us  = 0.2843	# for Blackman  20180801
Pclock_Pi_80us  = 1.8578	# for Blackman  20180801
Pclock_PiHalf_80us  = 1.8415	# for Blackman  20180801
Pclock_Pi_120us =0.8150
##### initiated 2018.02.02 #####

########################
# --- Breit-Rabi calibration -------------------------------------------
# Physics: the Cs-133 ground state (6S1/2, nuclear spin I = 7/2) has two
# hyperfine levels F = 3 and F = 4, split by fhfs = 9.192631770 GHz. In a
# magnetic field B each level fans out into Zeeman sublevels mf; the
# Breit-Rabi formula gives every sublevel energy exactly. With the
# dimensionless field parameter x = (gJ - gI)*muB*B/fhfs:
#     f(F,mf; B) = fhfs * [ -1/16 + mf*gI*muB*B/fhfs +/- (1/2)*sqrt(1 + 4*mf*x/8 + x^2) ]
# (+ for F = 4, - for F = 3). B is found from the measured stretched
# transition f4new; here it yields the RF frequency fRF.
delta2 = 215e3          # Hz, detuning of the 2-photon uw/rf pair
gI  = -0.000398853      # Cs-133 nuclear g-factor
gJ  = 2.0025403         # 6S1/2 electronic g-factor
muB = 1.3996246e6       # Bohr magneton / h, in Hz/G
b_trial = 1.393         # G, initial guess for the B-field solve
fhfs = 9.192631770e9    # Hz, Cs hyperfine splitting (exact)
fmix = 9.1326249676e9   # Hz, mixer LO (microwave = DDS + fmix)
f4newHLower = f4new

def flevel(F, mf, B):
    """Breit-Rabi energy (Hz) of ground-state sublevel |F, mf> at field B (G). F must be 3 or 4."""
    if F == 4:
        sign = +1.0
    elif F == 3:
        sign = -1.0
    else:
        raise ValueError('flevel: F must be 3 or 4, got %r' % (F,))
    x = (gJ - gI) * muB * B / fhfs
    return fhfs * (-1.0/16.0 + mf * gI * muB * B / fhfs \
        + sign * 1.0/2.0 * math.sqrt(1 + 4 * mf * x / 8 + x**2))

def get_b_field(z):
    """Residual for fsolve: zero when field z[0] reproduces the measured f4new."""
    B = z[0]
    residual = np.empty((1))
    residual[0] = flevel(4, -4, B) - flevel(3, -3, B) - f4new - fmix
    return residual

def get_uw_freq():
    """DDS frequency of the 2-photon microwave leg |3,0> -> |4,1> at B_field."""
    return flevel(4, 1, B_field) - flevel(3, 0, B_field) - fmix - delta2

def get_rf_freq():
    """RF frequency between |3,0> and |3,-1> at B_field, offset by delta2."""
    return flevel(3, -1, B_field) - flevel(3, 0, B_field) - delta2

# Solve the Breit-Rabi B field once, up front, with a convergence check.
B_field, _brinfo, _brier, _brmsg = fsolve(get_b_field, b_trial, full_output=True)
if _brier != 1:
    print('ERROR: B-field solve did not converge (ier=%d): %s' % (_brier, _brmsg))
    print('Check that f4new (=%f) is correct.' % f4new)
    sys.exit(1)
B_field = B_field[0]
print('Solved magnetic field B = %.4f G (from f4new)' % B_field)

fRF = get_rf_freq()
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
    # The cubic is fitted for 280-300 kHz and has a real root (a pole of the scale) at
    # 232.4 kHz: outside the range it silently extrapolates, e.g. 2.5x at 250 kHz (review
    # G2-3.1 / G2-5.1). Refuse instead of writing an unmeasured power.
    if np.min(f) < 280e3 or np.max(f) > 300e3:
        sys.exit('ERROR: rf_Power_Calib is calibrated for 280-300 kHz only, asked for '
                 '%.0f-%.0f Hz. Change the RF frequency or extend the calibration.'
                 % (np.min(f), np.max(f)))
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
test = 5e3	# 2017.02.03 Debug DDS
 
P= 0.94/4              # 1.545 Pi pulse, 0.37 Pi/2 pulse
StartingPower =  P - 0.025	#fclock+dfZeeman+40e30.2410
StoppingPower = P + 0.025
PowerStepSize = .005

#~ Frequency = f44to43newH -1.3e3 -delta2 + 1.9e3
centralF =  fRF - 23 	#on 20220407
Frequency = centralF
print(Frequency)
#~ Frequency = 279407.3148

#fclock+dfZeeman+60e3..
n = 5 	# number of pulses
hsr =-8e3
DetRepeats =1	#24	# h3w many detection pulse do you want to repeat
##################################################
### CLOCK TRANSITION FREQ: 60.0068MHz ############
##################################################
#~ delta=StartingFrequency-fclock0
#~ print(StartingFrequency)6

NumberOfRepeats   = 1000		# Number of times to repeat the scan

# define the detection pulse-0..09
# Typical square pulse
DetectionPulseType   = 2		# 1 for AFP, 2 for Blackman, 9 for CW (no ending), 22 Composite Pi  3 square pulse(phase coherence)
DetectionPulseLength = 0.7		# 0.240	#0.120*2
#~ DetectionPulsePower  =P31to40new
#~ DetectionPulsePower  =Pclock_Pi_120us
#~ DetectionPulsePower  = Pclock_Pi_240us
# DetectionPulsePower  = 0.2	# // AFP 3ms HSR -6e3   default 0.2
#~ DetectionPulsePower  = 0.25


DetectionPulseHSR    = 0		#-4e3	 # Hz (only used for AFP pulses) 
# For Blackman and CW pulses, "HSR" is the phase in units of pi


# Blackman
#~ DetectionPulseType   = 2		# 1 for AFP, 2 for Blackman, 9 for CW (no ending), 22 Composite Pi  3 square pulse(phase coherence)
#~ DetectionPulseLength = 0.12		# typ 0.12 
#~ DetectionPulsePower  = 0.318 		
#~ DetectionPulseHSR    = 0		# 0Hz for blackman

# Dummy Blackman for timing 
DetectionPulseType2   = 2		# 1 for AFP, 2 for Blackman, 9 for CW (no ending), 22 Composite Pi  3 square pulse(phase coherence)
DetectionPulseLength2 = 13		#  0.03 accounts for the chirp part of the uwave pulse 5% * 0.6 ms
DetectionPulsePower2  = 0.0 		
DetectionPulseHSR2    = 0


# Typical AFP parameters below:
# DetectionPulseType   = 1  # 1 for AFP, 2 for Blackman, 3 fs	or square, 4 for end, 9 for CW
# DetectionPulseLength = 3 # ms
# DetectionPulsePower  = 0.08 # W (must stay below 5.188 W, the top of the power table)
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
Power = np.arange(StartingPower, StoppingPower+PowerStepSize/2.0, \
                      PowerStepSize) # in W

NumberOfFiles = len(Power)

if NumberOfFiles > 1:
	print('Power scan: %.4f to %.4f W, %d points (step %.4f W)' \
		% (Power[0], Power[-1], NumberOfFiles, Power[1]-Power[0]))
else:
	print('Single-point power scan at %.4f W' % Power[0])

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

# Write Cooling file
print('Writing cooling pulse file ' + Coolfilename)
pulsefile = open(Coolfilename, "wb") # open pulse file
pulsefile.write(FileComment) # write comment line
writer = csv.writer(pulsefile, dialect='excel-tab') # define the file format
# Order of parameters: [Freq, HSR, Length, Power, Type, Comment]


writer.writerow([58.0e6, 0.0, 10.0, 0., 1, 'Dummy']) # Dummy pulse



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

# No Gate here (review G2-4.2 / G2-5.2): the RF bats assemble reset + RAW<point> only, so a
# compiled Gate was never played and its RAWGate was left for a later MW scan to splice.
# The Coolfilename file above is kept as the record of the pre-scan rows; to play such rows,
# put them in each point file (as the per-point Dummy already is).

# begin loop to write the detection pulse files    
measfile = open(MeasListFilename, "wb")                  
measfile.write(FileComment)                  
writerm = csv.writer(measfile, dialect='excel-tab')
def writerow_both(w, row):  # write one pulse row to both the given pulse file writer and the meas log
	w.writerow(row)
	writerm.writerow(row)
for i in xrange(0,len(Power)):
#~ for i in xrange(0,len(Phase)):
    print('Writing pulse file %s: power %.4f W' % (Filenames[i], Power[i]))
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
  





#~ ##For only one pulse##    
    #~ for x in xrange(0,DetRepeats):
        #~ writer.writerow([0, 0.0, 10.0, 0., 1, 'Dummy']) # Dummy pulse
	#~ writer.writerow([Frequency, \
                        #~ DetectionPulseHSR, \
                        #~ DetectionPulseLength, \
                        #~ Power[i], \
                        #~ DetectionPulseType, \
                        #~ 'Measure'])
    #~ pulsefile.close() # Close the pulse file
    #~ writerm.writerow([Filenames[i]])
    #~ for x in xrange(0,DetRepeats):
	#~ writerm.writerow([0, 0.0, 10.0, 0., 1, 'Dummy']) # Dummy pulse
        #~ writerm.writerow([Frequency, \
                        #~ DetectionPulseHSR, \
                        #~ DetectionPulseLength, \
                        #~ Power[i], \
                        #~ DetectionPulseType, \
                         #~ 'Measure'])
			 
			 
			 

#~ ##For n pulses##
    writerm.writerow([Filenames[i]])  # meas-log header: which point file these rows belong to

    ##### PRE-PULSES: insert fixed pulses BEFORE the scanned pulse here #####
    # Written once per file; NOT repeated by n or DetRepeats.
    # Use writerow_both(writer, ...) so the pulse file and the meas log stay in sync. Example:
    #~ writerow_both(writer, [f33to43new, -8e3, 3.0, P33to43new*64/36, 1, '3,-3 -> 4,-3'])
    ##### END PRE-PULSES #####

    for x in xrange(0, DetRepeats):
        writerow_both(writer, [0, 0.0, 10.0, 0., 1, 'Dummy'])  # dummy/timing pulse before each detection block
        for y in xrange(0, n):
            writerow_both(writer, [Frequency, DetectionPulseHSR, DetectionPulseLength, \
                           rf_Power_Calib(Frequency)*Power[i], DetectionPulseType, 'Measure'])

        ##### POST-PULSES: insert fixed pulses AFTER the scanned pulse here #####
        # Inside the DetRepeats loop, so these repeat with each detection block.
        # Move one indent left (outside the x loop) to write them only once per file.
        #~ writerow_both(writer, [f42to31new, -8e3, 3.0, P42to31new*64/36, 1, '4,-2 -> 3,-1'])
        ##### END POST-PULSES #####

    pulsefile.close() # Close the pulse file
			 
			 
		
#~ # used for scanning the frequency jump 
    #~ for x in xrange(0,DetRepeats):
        #~ writer.writerow([0, 0.0, 10.0, 0., 1, 'Dummy']) # Dummy pulse
	#~ writer.writerow([Frequency, \
                        #~ DetectionPulseHSR, \
                        #~ DetectionPulseLength, \
                        #~ Power[i], \
                        #~ DetectionPulseType, \
                        #~ 'Measure'])
	#~ writer.writerow([Frequency, \
                        #~ DetectionPulseHSR2, \
                        #~ DetectionPulseLength2, \
                        #~ DetectionPulsePower2, \
                        #~ DetectionPulseType, \
                        #~ 'Measure'])
	#~ writer.writerow([Frequency, \
                        #~ DetectionPulseHSR, \
                        #~ DetectionPulseLength, \
                        #~ Power[i], \
                        #~ DetectionPulseType, \
                        #~ 'Measure'])
    #~ pulsefile.close() # Close the pulse file
    #~ writerm.writerow([Filenames[i]])
    #~ for x in xrange(0,DetRepeats):
	#~ writerm.writerow([0, 0.0, 10.0, 0., 1, 'Dummy']) # Dummy pulse
        #~ writerm.writerow([Frequency, \
                        #~ DetectionPulseHSR, \
                        #~ DetectionPulseLength, \
                        #~ Power[i], \
                        #~ DetectionPulseType, \
                         #~ 'Measure'])
	#~ writerm.writerow([Frequency, \
                        #~ DetectionPulseHSR2, \
                        #~ DetectionPulseLength2, \
                        #~ DetectionPulsePower2, \
                        #~ DetectionPulseType, \
                        #~ 'Measure'])
        #~ writerm.writerow([Frequency, \
                        #~ DetectionPulseHSR, \
                        #~ DetectionPulseLength, \
                        #~ Power[i], \
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
print('Compiling %d pulse files (stepDDS_cal3_RF-V2.bat)...' % NumberOfFiles)
check_pulse_files(Filenames + [Coolfilename])
rc = subprocess.call([os.path.join(DDSDIR, 'stepDDS_cal3_RF-V2.bat'), 'List'])
if rc != 0:
	print('ERROR: stepDDS_cal3_RF-V2.bat failed with exit %d. Aborting.' % rc)
	sys.exit(1)
#print('After batch file')
#os.system("C:\Users\Yang\Documents\Eclipse\NewDDS2-Cooling2.0\pulsefiles\stepDDS_copy.bat List")
#os.system("C:\Users\Yang\Documents\Eclipse\NewDDS2-Cooling2.0\pulsefiles\stepDDS_delete.bat List")
#os.system("del Cool List RAWCool")
if DelTempFiles == 1 :
	print('Deleting temp files: %s, List, reset' % Coolfilename)
	os.system("del "+Coolfilename+" List reset")	

listfile = open(ListFilename, "wb")
for j in xrange(0,NumberOfRepeats):
    for i in Filenames:
        listfile.write(i+'-final.txt\n')
listfile.close()                 
            
print('Scan list %s: %d files x %d repeats = %d scans total' \
	% (ListFilename, NumberOfFiles, NumberOfRepeats, NumberOfFiles*NumberOfRepeats))
                    
os.system('copy "%s" "%s.py"' % (sys.argv[0], FilenameHead)) # save a copy of this python file (quoted: paths may hold spaces)
os.system("copy "+FilenameHead+".lst last-RF.lst") # copy list file to last.lst
os.system("copy "+FilenameHead+".scan last-RF.scan") # copy scan file to last.lst
print('Done. Script copied to %s.py; list/scan files copied to last-RF.lst and last-RF.scan.' % FilenameHead)