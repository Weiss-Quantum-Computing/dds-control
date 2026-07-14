// unit and format conversions for the NewDDS code
// Define some utility functions (mostly conversions)

#ifndef CONVERSIONS_H_
#define CONVERSIONS_H_

#include "DDSconstants.h" // load constants if not already loaded
#include <stdio.h>
#include <iostream>
#include <iomanip>
#include <string>

void ZeroArray(unsigned char* reg, unsigned long len); // Zero out a char array "reg" of length "len"

void ZeroArray(long double * reg, unsigned long len); // Zero out a float array "reg" of length "len"

long double FreqWord2Hz(uint64_t f); // convert frequency word to Hz

uint64_t RR2Word(long double tic); // Convert Hz to 40-bit frequency word (WARNING: rounding error)

uint64_t Hz2FreqWord(long double fhz); // Convert Hz to 40-bit frequency word (WARNING: rounding error)

unsigned short int Phase2PhaseWord(double phase); // Convert phase (units of pi) to 12-bit phase word

double Watts2dBm(double watts); // convert power in Watts to dBm

double dBm2Watts(double dbm); // convert power in dBm to Watts

double Pow2Volts(double pow);

double Volts2Pow(double volts);

//unsigned int Volts2AmpWord(double volts); //convert amp in volts to 12-bit Amplitude Word (remember amp ~ pow^0.5)

//double AmpWord2Volts(unsigned int amp); // Convert amplitude word to power in Watts (remember pow ~ amp^2)

unsigned int Pow2AmpWord(double pow); //convert power in watts to 12-bit Amplitude Word (remember amp ~ pow^0.5)

//double AmpWord2Pow(unsigned int amp); // Convert amplitude word to power in Watts (remember pow ~ amp^2)

unsigned long Time2Tics(double seconds);

double Tics2Time(unsigned long tics);

double sgn(double x);

double Freq1(double f0, double HSR, double tau); //adiabatic sweeping
double Freq2(double f0, double HSR, double tau); //adiabatic sweeping
double tanh(double x);
double sech(double x);
#endif // wrapper
