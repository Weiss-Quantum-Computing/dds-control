// some constants for the NewDDS program

#ifndef DDSCONSTANTS_H_
#define DDSCONSTANTS_H_

/*
#define	EXTCLOCK	10000000.0 // (10 MHz) Frequency of external clock in Hz
#define	REFMULT		30 // (300 MHz) Multiplier between external clock and DDS clock
#define INTCLOCK	300000000.0 // (300 MHz) Intenal clock frequency
#define FMAX		281474976710655ULL // (2^48-1) Max frequency in units of epsf (need factor of 1/2?)
#define EPSF		1.0658141036401502788066864013672e-6 // Minimum frequency step in Hz (~1 uHz)
#define DIP		4  // DIP setting of DDS board "000100" (may make variable in future)
#define POWMAX		0.0125  // Max power in W
#define VOLTMAX		0.790569415042 // Max amplitude in V (from above, assuming 50 Ohm load)
#define PI		3.141592653589793
*/

const long double	EXTCLOCK	= 10000000.0 ;// (10 MHz) Frequency  of external clock in Hzconst int		REFMULT 	= 30; // (30) Multiplier between external clock and DDS clockconst long double	INTCLOCK	= EXTCLOCK*REFMULT; // (300 MHz) Intenal clock frequencyconst uint64_t		FMAX		= 0x0000FFFFFFFFFFFFULL; // (2^48-1) Max frequency in units of epsf (need factor of 1/2?)const long double	EPSF		= INTCLOCK/FMAX; // Minimum frequency step in Hz (~1 uHz)const long double	DIP		= 0x04  ;// DIP setting of DDS board "000100" (may make variable in future)const long double	POWMAX		= 0.0125  ;// Max power in W (TODO: calibrate this, present value is from AD9852 specs)const long double	VOLTMAX		= sqrt(POWMAX*50.0);// Max amplitude in V (from above, assuming 50 Ohm load)const long double	PI		= 4*atan((long double)1); // Pi
const unsigned char	IORESET		= 0; // define constants for IO "options"
const unsigned char	IOLOAD		= 1; // define constants for IO "options"
const unsigned char	IOUPDATE	= 2; // define constants for IO "options"
const unsigned char	IOLATCH		= 3; // define constants for IO "options"
const long double	PCICLOCK	= 1.0e6; // PCI clock rate (borrowed from Kunyan's code)
const unsigned int	MAXSAMPLES	= 150000; // Maximum number of samples for DAQ card

#endif //wrapper
