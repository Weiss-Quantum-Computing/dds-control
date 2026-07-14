/*
 * conversions.cpp
 *
 *  Created on: Aug 3, 2010
 *      Author: Ted Corcovilos
 */

// unit and format conversions for the NewDDS code
// Define some utility functions (mostly conversions)
#include <string>
#include "conversions.h"
#include<math.h>
using namespace std;

void ZeroArray(unsigned char* reg, unsigned long len) // Zero out an char array "reg" of length "len"
    {
    for (unsigned long i = 0; i < len; i++)
	{
	reg[i] = 0;
	}
    }

void ZeroArray(long double * reg, unsigned long len) // Zero out an char array "reg" of length "len"
    {
    for (unsigned long i = 0; i < len; i++)
	{
	reg[i] = 0;
	}
    }

long double FreqWord2Hz(uint64_t f) // convert frequency word to Hz
    {
    long double conv = INTCLOCK / ((long double) (FMAX));
    long double tempf = conv * f;
    return (tempf);
    }

uint64_t RR2Word(long double tic) // Convert Hz to 40-bit frequency word (WARNING: rounding error)
    {
    return ((uint64_t) floor(tic * INTCLOCK - 1));
    }

uint64_t Hz2FreqWord(long double fhz) // Convert Hz to 40-bit frequency word (WARNING: rounding error)
    {
    uint64_t temp;
    if (fhz>0)
	{
	 temp = ((uint64_t) floor(fhz * FMAX / INTCLOCK));
	}
    else /* use two's complement to deal with negative frequency*/
	{
	 uint64_t temp2;
	 temp2 = ((uint64_t) floor(-1*fhz * FMAX / INTCLOCK));
	 temp = (0xFFFFFFFFFFFFFFFFULL-temp2)+1;
	}
    return temp;
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
    return (sqrt(pow * 50.0 * 2.0)); // assuming 50 ohm load
    }

double Volts2Pow(double volts)
    {
    return (volts * volts / 50.0 / 2.0); // assuming 50 ohm load
    }

/*unsigned int Volts2AmpWord(double volts) //convert amp in volts to 12-bit Amplitude Word (remember amp ~ pow^0.5)
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
	    return (int(floor(4095.0 * (volts / VOLTMAX))));
	    }
	}
    }*/

/*double AmpWord2Volts(unsigned int amp) // Convert amplitude word to power in Watts (remember pow ~ amp^2)
    {
    return ((double) amp / 4095.0 * VOLTMAX);
    }*/

unsigned int Pow2AmpWord(double pow) //convert power in watts to 12-bit Amplitude Word (remember amp ~ pow^0.5)
/* Using calibration data of 20100914 */
    {
	double x;
	unsigned int amp;
	const double Pmax = 0.745;
	const double x0 = 0.52;
	const double a0 = -5.496533e-1;
	const double a1 = 5.701423e-1;
	const double a2 = 9.360634e-2;
	const double a3 = 9.752135e-3;
	const double b0 = 6.609827e-1;
	const double b1 = 3.511512;
	const double b2 = 1.774716e-1;
	const double b3 = 5.085557e-1;
	if (pow > Pmax) return(4095); // clip at max
	if (pow <= 0 ) return(0); // clip at zero
	x = pow/Pmax;
	if (x < x0)
	    {
	    double lx = log(x);
	    amp = (unsigned int)floor(4095*exp(a3*lx*lx*lx+a2*lx*lx+a1*lx+a0));
	    }
	else
	    {
	    amp = (unsigned int)floor(4095*(b3+b2*tan(b1*(x-b0))));
	    }
    //unsigned int amp;
    //amp = (unsigned int)floor(4095*pow);
    return (amp);
    }

/*double AmpWord2Pow(unsigned int amp) // Convert amplitude word to power in Watts (remember pow ~ amp^2)
    {
    return (Volts2Pow(AmpWord2Volts(amp)));
    }*/

unsigned long Time2Tics(double seconds)
    {
    return ((unsigned long) floor(seconds * FIFOCLOCK / 8.0)); //8 is the maximum number of registers need to be changed
    }

double Tics2Time(unsigned long tics)
    {
    return ((double) tics * 8.0 / FIFOCLOCK);
    }

double sgn(double x)
    {
    if (x > 0.0)
	return 1.0;
    else if (x < 0.0)
	return -1.0;
    else
	return 0.0;
    }

double Freq1(double f0, double HSR, double tau) //adiabatic sweeping
    {
    if (tau <= 1.0 && tau >= 0.0)
	{
	return f0 + sgn(tau - 0.5) * HSR * sqrt(1 - pow(sin(PI * tau), 4));
	}
    else
	cout << "Error: tau out range [0,1]:" << dec << tau << endl;
    return 0.0;
    }
double Freq2(double f0, double HSR, double tau) //adiabatic sweeping
    {
    if (tau <= 1.0 && tau >= 0.0)
	{
	//return f0 +   HSR * (exp(2*tau*4.852-4.852)- exp(-2*tau*4.852+4.852))/( exp(2*tau*4.852-4.852)+ exp(-2*tau*4.852+4.852));
	//return (f0 +   HSR * (tanh(2*tau*4.852-4.852)));
	return (f0 + HSR*sgn(tau-0.5)*sqrt(1-pow(sech((2*tau-1)*4.852),4)));
	}
    else
	cout << "Error: tau out range [0,1]:" << dec << tau << endl;
    return 0.0;
    }
double sech(double x)
    {
    return (1.0/cosh(x));
    }
/*
double tanh(double x)
    {
    return ((exp(x)-exp(-x))/(exp(x)+exp(-x)));
    }
*/
