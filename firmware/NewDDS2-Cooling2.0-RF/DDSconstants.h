// some constants for the NewDDS program

#ifndef DDSCONSTANTS_H_
#define DDSCONSTANTS_H_
#ifndef __int64
// needed to make NIDAQmx.h work
#define __int64 long long
#endif
#include <stdint.h>
#include <math.h>
#include <NIDAQmx.h>
#include <string>
using namespace std;


// Clocks
const long double	FIFOCLOCK	= 1000000 ;// (1 MHz) Frequency of data update clock
const long double	EXTCLOCK	= 10000000;//20000000.0 ;// (10 MHz) Frequency of external clock in Hzconst int		REFMULT 	= 30;//15; // (30) Multiplier between external clock and DDS clockconst long double	INTCLOCK	= EXTCLOCK*REFMULT; // (300 MHz) Internal clock frequency
const long double	RAMPRATE	= EXTCLOCK*0.01; // (1 MHz) RampRate clock frequency
const bool              PLLRANGE        = 1; // 0 for < 200MHz, 1 for > 200 MHz
// Conversion factors
const uint64_t		FMAX		= 0x0000FFFFFFFFFFFFULL; // (2^48-1) Max frequency in units of epsf (need factor of 1/2?)const long double	EPSF		= INTCLOCK/FMAX; // Minimum frequency step in Hz (~1 uHz)//const long double	POWMAX		= 0.001156  ;// Max power in W (Calibrated using scope with 50 Ohm terminator)
const long double	POWMAX		= 6.38  ;// Max power in W (Calibrated using spectrum analyzer after final amplifier)
//const long double	POWMAX		= 0.745  ;// Max power in W (Calibrated using spectrum analyzer after final amplifier)
//const long double	VOLTMAX		= sqrt(POWMAX*50.0*2);// Max pk-pk amplitude in V (from above, assuming 50 Ohm load)
const long double	VOLTMAX		= 1;// Max pk-pk amplitude in V (from above, assuming 50 Ohm load)const long double	PI		= ((long double)4.0)*atan((long double)1.0); // Pi

// DDS card constants
const long double	DIP		= 0x00  ;// DIP setting of DDS board "000100" (may make variable in future)
const unsigned char	IORESET		= 0; // define constants for IO "options"
const unsigned char	IOLOAD		= 1; // define constants for IO "options"
const unsigned char	IOUPDATE	= 2; // define constants for IO "options"
const unsigned char	IOLATCH		= 3; // define constants for IO "options"
//const long double	PCICLOCK	= 1.0e6; // PCI clock rate (borrowed from Kunyan's code)
const unsigned int	MAXSAMPLES	= 150000000; // Maximum number of samples for DAQ card was 150000
//const float		IOTIMEOUT	= 300.0; // Timeout (waiting for trigger) length in seconds
const float		IOTIMEOUT	= -1; // -1 = Infinite wait

// Input file constants
//const string		DEFAULTFILENAME = "Pulse parameters.xls"; // default filename if not specified on command line
const string            DEFAULTFILENAME = "Pulse parameters.txt"; // default filename
const unsigned int      PULSEPARASIZE   = 5;     //number of parameters to specify a pulse
const unsigned int      MAXPULSES       = 10000;   // maximum number of pulses to read
const unsigned int      MAXDATA         = 250000;   // maximum number of data to read
#endif //wrapper
