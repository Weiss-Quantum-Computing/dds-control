# AddressingSearch.py
# Ted Corcovilos 20130128
# Move picomotors to do a grid search for the addressing lens
# TODO add support for multiple controllers
# TODO add support for PI translation stage
# Using absolute position coodinates, need to test

import serial, sys, subprocess
from time import sleep
import ldcnlib as L #wrappers for ldcn library (picomotor DLL control)
#from winsound import Beep

# Constants
# Search parameters
DDSCMD = r'C:\Users\Yang\Documents\Data\DDScontrol\NewDDS2-Cooling2.0.exe C:\Users\Yang\Documents\Data\DDScontrol\20130125\address005-001-final.txt' #command to send to OS for running the DDS once
REPEATS = 3 # number of shots at each picomotor position
MAXSIZE = 9 # max edge size of the search pattern

# Picomotor constants
PORT = "COM1" # Serial port name (e.g. "COM1")
BAUD = 19200 # Serial port baud rate (see picomotor manual)
DRIVER = 1 # picomotor driver address
WAIT = 0.2 # wait time after commands in s
MOVEWAIT = 2 #wait for motor to move

# motion parameters (see also initialize() below)
MAXACCEL = 255 # maximum acceleration (0-255, default = 255)
VEL = 187 # velocity (0-250, default = 250)
MULT = 0 # multiplier for VEL (0=8x, 1=4x, 2=2x, 3=1x)

# Channels: A = 0, B = 1, C = 2
ZCH = 2
YCH = 0 # picomotor channel for 'X' direction
XCH = 1 # picomotor channel for 'Y' direction

XMOVE=0 #minus moves down
ZMOVE=0

XSTEPS = 0*200*25 #XMOVE*70*25 # number of steps in X (25 is scaling factor needed by the software )
YSTEPS = 1*1000*25 # number of steps in Y (this gives ~ 1/3 turn motion)
ZSTEPS =  0*1000*25 # 500*25~ 1/8 of a turn

def main(argv):
    #print("argv:")
    #print argv
    x = XSTEPS
    y = YSTEPS
    z = ZSTEPS
    #ser = serial.Serial() # create serial port object
    print('Initializing...')
    devs = initialize() # open serial port and initialize driver
    # initialize port
    if devs < 0: # check for error conditions
        L.LdcnShutdown() # close the serial port
        return devs #exit
    print('Devices found: {0:d}'.format(devs))
    print('Port open successfully')
    # move the picomotor
    L.StepSetOutputs(DRIVER,ZCH) # Choose motor
    L.StepStopMotor(DRIVER,9) #stop smoothly, motor on
    L.StepSetParam(DRIVER,MULT+4,0,0,0,0,0)
    L.StepResetPos(DRIVER) # Reset position counter to zero (Do we need this?)
    #Beep(500,300)
    L.StepLoadTraj(DRIVER,7,z,VEL,MAXACCEL,0) #load motion
    print("Moving channel {0:d} by {1:d} steps.".format(ZCH,z))
    L.ServoStartMotion(DRIVER)
    #while (L.LdcnGetStat(DRIVER) & 1): # wait while moving (Status bit 0 is high)
    sleep(abs(z)*MOVEWAIT/5000) 
    L.LdcnNoOp(DRIVER)
    print("Steps moved: {0:d}".format(L.StepGetPos(DRIVER)))
    L.StepStopMotor(DRIVER,8) #stop smoothly, motor off
    L.StepSetOutputs(DRIVER,XCH) # Choose motor
    L.StepStopMotor(DRIVER,9) #stop smoothly, motor on
    L.StepSetParam(DRIVER,MULT+4,0,0,0,0,0)
    L.StepResetPos(DRIVER) # Reset position counter to zero (Do we need this?)
    #Beep(500,300)
    L.StepLoadTraj(DRIVER,7,x,VEL,MAXACCEL,0) #load motion
    print("Moving channel {0:d} by {1:d} steps.".format(XCH,x))
    L.ServoStartMotion(DRIVER)
    #while (L.LdcnGetStat(DRIVER) & 1): # wait while moving (Status bit 0 is high)
    sleep(abs(x*MOVEWAIT/5000)) 
    L.LdcnNoOp(DRIVER)
    print("Steps moved: {0:d}".format(L.StepGetPos(DRIVER)))
    L.StepStopMotor(DRIVER,8) #stop smoothly, motor off
    L.StepSetOutputs(DRIVER,YCH) # Choose motor
    L.StepStopMotor(DRIVER,9) #stop smoothly, motor on
    L.StepSetParam(DRIVER,MULT+4,0,0,0,0,0)
    L.StepResetPos(DRIVER) # Reset position counter to zero (Do we need this?)
    #Beep(500,300)
    L.StepLoadTraj(DRIVER,7,y,VEL,MAXACCEL,0) #load motion
    print("Moving channel {0:d} by {1:d} steps.".format(YCH,y))
    L.ServoStartMotion(DRIVER)
    #while (L.LdcnGetStat(DRIVER) & 1): # wait while moving (Status bit 0 is high)
    sleep(abs(y)*MOVEWAIT/5000) 
    L.LdcnNoOp(DRIVER)
    print("Steps moved: {0:d}".format(L.StepGetPos(DRIVER)))
    L.StepStopMotor(DRIVER,8) #stop smoothly, motor off

    L.LdcnShutdown() # close the serial port
    return

def initialize():
    # initialize the serial port and picomotor controller
    # returns ser if successful, error code otherwise
    L.LdcnShutdown() #close any open sessions
    sleep(1)
    devs = L.LdcnInit(PORT, BAUD) # try to init using last used baud rate
    if devs == 0:
        devs = L.LdcnFullInit(PORT,BAUD) # Try again, scanning all baud rates
    if devs == 0: # if still nothing found, fail
        L.LdcnShutdown()
        print('No devices found.  Exiting...') 
        return -1
    # Try to talk to driver
    if (L.LdcnNoOp(DRIVER)==0):
        print('Communication error.  Exiting...')
        return -2
    if (L.StepSetParam(DRIVER,MULT+4,0,0,0,0,0)==0): # Set step modes
        print('Unable to set parameters.  Exiting...')
        return -3
    L.StepResetPos(DRIVER) # reset positions
    L.LdcnDefineStatus(DRIVER, 1) # set status byte to "position"
    #
    #try:
    #    ser.port = PORT
    #    ser.baudrate = BAUD
    #    ser.timeout = 3
    #    ser.open()
    #except Exception, err:
    #    sys.stderr.write('ERROR opening serial port: %s\n' % str(err))
    #    print('ERROR opening serial port: %s\n' % str(err))
    #    return err
    # begin picomotor initialization sequence
    #ser.write("INI"+ENDLINE) #initialize controller
    #sleep(WAIT)
    #ser.write("DEF"+ENDLINE) #set all parameters to default values
    #sleep(WAIT)
    #ser.write("ACC A{0} {1}={2}".format(DRIVER,XCH,MAXACCEL)+ENDLINE)
    #sleep(WAIT)
    #ser.write("ACC A{0} {1}={2}".format(DRIVER,YCH,MAXACCEL)+ENDLINE)
    #sleep(WAIT)
    #ser.write("VEL A{0} {1}={2}".format(DRIVER,XCH,VEL)+ENDLINE)
    #sleep(WAIT)
    #ser.write("VEL A{0} {1}={2}".format(DRIVER,YCH,VEL)+ENDLINE)
    #sleep(WAIT)
    return devs

def generatespiral(size,movelist,coordlist):
    # generate a list containing the moves for a square spiral with maximum side "size"
    # returns the number of steps in the sequence
    sign = 1
    steps = 0
    x = 0
    y = 0
    for s in xrange(0,size):
        sign = -sign 
        for i in xrange(0,s):
            x += sign
            coordlist.append([x,y])
            movelist.append([XCH,sign*XSTEPS])
            #movelist.append([XCH,x*XSTEPS])
            #movelist.append("CHL A{0}={1}\n\rREL {0}={2} G".format(DRIVER,XCH,sign*XSTEPS)+ENDLINE)
            steps = steps +1
        for i in xrange(0,s):
            y += sign
            coordlist.append([x,y])
            movelist.append([YCH,sign*YSTEPS])
            #movelist.append([YCH,y*YSTEPS])
            #movelist.append("CHL A{0}={1}\n\rREL {0}={2} G".format(DRIVER,YCH,sign*YSTEPS)+ENDLINE)
            steps = steps + 1
    return steps

if __name__ == "__main__":
    main(sys.argv)