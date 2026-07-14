import serial, sys, subprocess
from time import sleep
import ldcnlib as L #wrappers for ldcn library (picomotor DLL control)

PORT = "COM7" # Serial port name (e.g. "COM1")
BAUD = 19200 # Serial port baud rate (see picomotor manual)
DRIVER = 1 # picomotor driver address
WAIT = 0.2 # wait time after commands in s
MOVEWAIT = 2 #wait for motor to move

def main(argv):

    devs = initialize() # open serial port and initialize driver
    # initialize port
    if devs < 0: # check for error conditions
        L.LdcnShutdown() # close the serial port
        return devs #exit
    print('Devices found: {0:d}'.format(devs))
    print('Port open successfully')
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
    
if __name__ == "__main__":
    main(sys.argv)