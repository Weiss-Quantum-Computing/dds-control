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
XCH = 1 # picomotor channel for 'X' direction
YCH = 2 # picomotor channel for 'Y' direction
XSTEPS = 1000*25 # number of steps in X (25 is scaling factor needed by the software )
YSTEPS = 1000*25 # number of steps in Y (this gives ~ 1/8 turn motion)

def main():
    #ser = serial.Serial() # create serial port object
    print('Initializing...')
    devs = initialize() # open serial port and initialize driver
    # initialize port
    if devs < 0: # check for error conditions
        L.LdcnShutdown() # close the serial port
        return devs #exit
    print('Devices found: {0:d}'.format(devs))
    print('Port open successfully')
    movelist = [[XCH,0]] #list of moves [channel,position](move happens before experiment sequence)
    coordlist = [[0,0]] # coordinate list, start at the origin, just for reference
    steps = generatespiral(MAXSIZE,movelist,coordlist)
    print ("Spiral size {0:d}, contains {1:d} steps and {2:d} shots".format(MAXSIZE,steps+1,REPEATS*(1+steps)))
    print movelist # print the move commands for debugging
    #return
    print coordlist # print the coordinates list for debugging
    #L.LdcnShutdown()
    #return
    #ser.close() # close serial port
    totalshots = 0
    for m in xrange(0,steps+1):
        print("Step {0:d} of {1:d}, {2:s}".format(m+1,steps+1,coordlist[m]))
        #ser.write(movelist[m])
        
        # move the picomotor
        L.LdcnNoOp(DRIVER) # ping the driver
	L.StepGetPos(DRIVER) # read position
        L.StepSetOutputs(DRIVER,movelist[m][0]) # Choose motor
        L.StepStopMotor(DRIVER,9) #stop smoothly, motor on
	L.StepSetParam(DRIVER,MULT+4,0,0,0,0,0)
        L.StepSetOutputs(DRIVER,movelist[m][0]) # Choose motor
        L.StepResetPos(DRIVER) # Reset position counter to zero (Do we need this?)
	L.LdcnNoOp(DRIVER)
        L.StepGetPos(DRIVER)
	print("Moving channel {0:d} by {1:d} steps.".format(movelist[m][0],movelist[m][1]))
        #Beep(500,300)
	L.StepLoadTraj(DRIVER,7,movelist[m][1],VEL,MAXACCEL,0) #load motion
        L.ServoStartMotion(DRIVER)
        #while (L.LdcnGetStat(DRIVER) & 1): # wait while moving (Status bit 0 is high)
	sleep(MOVEWAIT) 
	L.LdcnNoOp(DRIVER)
        print("Steps moved: {0:d}".format(L.StepGetPos(DRIVER)))
        L.StepStopMotor(DRIVER,8) #stop smoothly, motor off
	
        for s in xrange(0,REPEATS):
            totalshots = totalshots + 1
            print("Shot {0:d} of {1:d}, total {2:d}".format(s+1,REPEATS,totalshots,REPEATS*steps))
            subprocess.check_call(DDSCMD) #call the DDS executable and wait
	    sleep(0.3)
    print("Sequence complete, {0:d} shots total".format(totalshots))
    print("Moving back to origin")
    # move the picomotor
    L.StepSetOutputs(DRIVER,XCH) # Choose motor
    L.StepStopMotor(DRIVER,9) #stop smoothly, motor on
    L.StepSetParam(DRIVER,MULT+4,0,0,0,0,0)
    L.StepResetPos(DRIVER) # Reset position counter to zero (Do we need this?)
    #Beep(500,300)
    L.StepLoadTraj(DRIVER,7,-1*coordlist[steps][0]*XSTEPS,VEL,MAXACCEL,0) #load motion
    print("Moving channel {0:d} by {1:d} steps.".format(XCH,-1*coordlist[steps][0]*XSTEPS))
    L.ServoStartMotion(DRIVER)
    #while (L.LdcnGetStat(DRIVER) & 1): # wait while moving (Status bit 0 is high)
    sleep(abs(coordlist[steps][0])*MOVEWAIT) 
    L.LdcnNoOp(DRIVER)
    print("Steps moved: {0:d}".format(L.StepGetPos(DRIVER)))
    L.StepStopMotor(DRIVER,8) #stop smoothly, motor off
    L.StepSetOutputs(DRIVER,YCH) # Choose motor
    L.StepStopMotor(DRIVER,9) #stop smoothly, motor on
    L.StepSetParam(DRIVER,MULT+4,0,0,0,0,0)
    L.StepResetPos(DRIVER) # Reset position counter to zero (Do we need this?)
    #Beep(500,300)
    L.StepLoadTraj(DRIVER,7,-1*coordlist[steps][1]*YSTEPS,VEL,MAXACCEL,0) #load motion
    print("Moving channel {0:d} by {1:d} steps.".format(YCH,-1*coordlist[steps][0]*YSTEPS))
    L.ServoStartMotion(DRIVER)
    #while (L.LdcnGetStat(DRIVER) & 1): # wait while moving (Status bit 0 is high)
    sleep(abs(coordlist[steps][1])*MOVEWAIT) 
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
    main()