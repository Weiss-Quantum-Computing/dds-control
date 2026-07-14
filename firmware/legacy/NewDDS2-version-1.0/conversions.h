// unit and format conversions for the NewDDS code
// Define some utility functions (mostly conversions)

#ifndef CONVERSIONS_H_
#define CONVERSIONS_H_

#ifndef DDSCONSTANTS_H_
#include "DDSconstants.h" // load constants if not already loaded
#endif

void ZeroArray(unsigned char* reg, unsigned int len) // Zero out an char array "reg" of length "len"
    {
    for (unsigned int i = 0; i < len; i++)
	{
	reg[i] = 0;
	}
    }
long double FreqWord2Hz(uint64_t f) // convert frequency word to Hz
    {
    long double conv = INTCLOCK / ((long double) (FMAX)) ;
    long double tempf = conv * f;
    return (tempf);
    }
uint64_t Hz2FreqWord(long double fhz) // Convert Hz to 40-bit frequency word (WARNING: rounding error)
    {
    return ((uint64_t) floor(fhz  * FMAX / INTCLOCK));
    }
double Watts2dBm(double watts) // convert power in Watts to dBm
    {
    return (10.0 * log10(watts) + 30.0);
    }
double dBm2Watts(double dbm) // convert power in dBm to Watts
    {
    return (pow(10, (dbm / 10.0 - 3.0)));
    }
double Pow2Volts(double pow)
    {
    return (sqrt(pow * 50.0)); // assuming 50 ohm load
    }
double Volts2Pow(double volts)
    {
    return (volts * volts / 50.0); // assuming 50 ohm load
    }
unsigned int Volts2AmpWord(double volts) //convert amp in volts to 12-bit Amplitude Word (remember amp ~ pow^0.5)
    {
    // coerce value into range [0,0x0FFF]
    if (volts > VOLTMAX)
	{
	return (0x0FFF);
	}
    else
	{
	if (volts < 0)
	    {
	    return (0);
	    }
	else
	    {
	    return (int(floor(4096.0 * (volts / VOLTMAX))));
	    }
	}
    }
double AmpWord2Volts(unsigned int amp) // Convert amplitude word to power in Watts (remember pow ~ amp^2)
    {
    return ((double) amp / 4096.0 * VOLTMAX);
    }
unsigned int Pow2AmpWord(double pow) //convert power in watts to 12-bit Amplitude Word (remember amp ~ pow^0.5)
    {
    return (Volts2AmpWord(Pow2Volts(pow)));
    }
double AmpWord2Pow(unsigned int amp) // Convert amplitude word to power in Watts (remember pow ~ amp^2)
    {
    return (Volts2Pow(AmpWord2Volts(amp)));
    }
unsigned long Time2Tics(double seconds)
    {
    return ((unsigned long) floor(seconds * INTCLOCK));
    }
double Tics2Time(unsigned long tics)
    {
    return ((double) tics / INTCLOCK);
    }

#endif // wrapper
