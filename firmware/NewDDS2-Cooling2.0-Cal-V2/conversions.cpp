/*
 * conversions.cpp
 *
 *  Created on: Aug 3, 2010
 *      Author: Ted Corcovilos
 */

// unit and format conversions for the NewDDS code
// Define some utility functions (mostly conversions)
#include <string>
#include <fstream>
#include <sstream>
#include <stdlib.h>
#include "DDSconstants.h"
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
    // 2026-11: + 1e-6 before the floor. tic * INTCLOCK is a whole number (300 for the AFP ramp clock) that
    // comes out a hair above or below it depending on the compiler's floating point: the lab's MinGW exe
    // writes 299 (register 0x1c = 0x2b), a 64-bit build of the same source 298. With the margin every
    // build writes what the lab's exe always has.
    return ((uint64_t) floor(tic * INTCLOCK - 1 + 1e-6L));
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

unsigned short int Phase2PhaseWord(double phase) // Convert phase (units of pi) into phase word
    {
    int output;
    output = int(0x2000*phase) % 0x4000;  // PhaseWord ranges from 0x0000 to 0x3FFF
    return output;
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

// ---- amplitude table from a file (2026-11) -------------------------------------------------
// The built-in conversion below (2015) tabulates the amplitude fraction against the POWER and joins
// the points with cubic pieces, starting at (0 W, 0). Below its first point, 16.2 mW, the amplitude
// comes out nearly proportional to the power, where a linear chain needs sqrt(power): a pulse typed
// at 3 mW got word 40 where the square-root law gives 88, and every shaped pulse passes through
// that region in its wings. The pieces do not join smoothly either (the slope doubles at 66 mW),
// and the word was rounded down.
// A table file replaces all of that, and can be remeasured without rebuilding this program:
//
//     # anything after a '#' is a comment
//     version 1
//     interpolation sqrt-linear
//     rounding nearest
//     0          0
//     0.0162181  0.05
//     ...                        power in W, amplitude fraction (word / 4095)
//     5.188      1
//
// The three keyword lines are required, each once, with exactly these values (they say what this
// program does with the numbers; another value is refused, not guessed at). The points: the first
// is 0 0, powers and fractions both strictly rising, fractions at most 1, 2 to 500 points.
// The conversion: fraction = straight lines between the points against sqrt(power), so a chain
// that is linear in the word needs nothing more than its two end points; word = 4095 x fraction
// rounded to the nearest. 0 W (or less, or NaN) is word 0; the top power or more is the top word.
// ddsgui/ampword.py of Freq-Scan-GUI is the same conversion in Python, compared word for word.
const int AMPTABLEMAX = 500;
static int ampTableN = 0; // points in use; 0 = the built-in table
static double ampTableU[AMPTABLEMAX]; // sqrt(power in W)
static double ampTableY[AMPTABLEMAX]; // amplitude fraction
static double ampTableTopW = 0; // the last point's power
static string ampTableName = "";

static bool AmpNumber(const string & token, double & value) // the whole token is one finite number
    {
    char * end = 0;
    value = strtod(token.c_str(), &end);
    return (token.size() > 0 && *end == 0 && value == value && value - value == 0);
    }

int LoadAmpTable(const char * path, string & message)
    {
    ampTableN = 0;
    ifstream file(path);
    if (!file.is_open())
	{
	message = "cannot open the file";
	return -1;
	}
    static double power[AMPTABLEMAX], fraction[AMPTABLEMAX];
    int points = 0, version = 0, interpolation = 0, rounding = 0;
    string line;
    unsigned int number = 0;
    ostringstream why;
    while (getline(file, line))
	{
	number++;
	string::size_type hash = line.find('#');
	if (hash != string::npos)
	    line.erase(hash);
	istringstream words(line);
	string first, second, third;
	if (!(words >> first))
	    continue; // blank or comment
	if (!(words >> second) || (words >> third))
	    {
	    why << "line " << number << ": expected two items (a keyword and its value, or a power and a fraction)";
	    message = why.str();
	    return -1;
	    }
	if (first == "version" || first == "interpolation" || first == "rounding")
	    {
	    int & seen = (first == "version") ? version : (first == "interpolation") ? interpolation : rounding;
	    const char * wanted = (first == "version") ? "1" : (first == "interpolation") ? "sqrt-linear" : "nearest";
	    if (seen)
		{
		why << "line " << number << ": '" << first << "' is given twice";
		message = why.str();
		return -1;
		}
	    if (second != wanted)
		{
		why << "line " << number << ": '" << first << " " << second << "' is not known to this program (it knows '"
		    << first << " " << wanted << "')";
		message = why.str();
		return -1;
		}
	    seen = 1;
	    continue;
	    }
	double p, f;
	if (!AmpNumber(first, p) || !AmpNumber(second, f))
	    {
	    why << "line " << number << ": '" << first << " " << second << "' is not a power and a fraction";
	    message = why.str();
	    return -1;
	    }
	if (points >= AMPTABLEMAX)
	    {
	    why << "more than " << AMPTABLEMAX << " points";
	    message = why.str();
	    return -1;
	    }
	if (points == 0 && !(p == 0 && f == 0))
	    {
	    why << "line " << number << ": the first point must be 0 0";
	    message = why.str();
	    return -1;
	    }
	if (points > 0 && !(p > power[points-1] && f > fraction[points-1]))
	    {
	    why << "line " << number << ": powers and fractions must both rise from point to point";
	    message = why.str();
	    return -1;
	    }
	if (!(f <= 1))
	    {
	    why << "line " << number << ": the fraction is above 1";
	    message = why.str();
	    return -1;
	    }
	power[points] = p;
	fraction[points] = f;
	points++;
	}
    if (!version || !interpolation || !rounding)
	{
	message = string("the line '") + (!version ? "version 1" : !interpolation ? "interpolation sqrt-linear" : "rounding nearest")
		+ "' is missing";
	return -1;
	}
    if (points < 2)
	{
	message = "fewer than 2 points";
	return -1;
	}
    for (int i = 0; i < points; i++)
	{
	ampTableU[i] = sqrt(power[i]);
	ampTableY[i] = fraction[i];
	}
    ampTableTopW = power[points-1];
    ampTableName = path;
    ampTableN = points;
    return 1;
    }

double AmpTableTop()
    {
    return (ampTableN > 0 ? ampTableTopW : (double) POWMAX);
    }

string AmpTableDescription()
    {
    ostringstream text;
    if (ampTableN > 0)
	text << "Amplitude conversion: table file " << ampTableName << " (" << ampTableN
	     << " points, 0 to " << ampTableTopW << " W; straight lines against sqrt(power), nearest word)";
    else
	text << "Amplitude conversion: built-in 2015 table (cubic pieces against power, word rounded down)";
    return text.str();
    }

static unsigned int AmpWordFromTable(double power) // the table file's conversion
    {
    if (!(power > 0)) // also NaN
	return (0);
    volatile double u = sqrt(power); // volatile: a plain double, whatever the FPU's own precision
    int jl = 0, ju = ampTableN - 1;
    if (u >= ampTableU[ju])
	return ((unsigned int) floor(4095.0 * ampTableY[ju] + 0.5));
    while (ju - jl > 1)
	{
	int jm = (ju + jl) >> 1;
	if (u >= ampTableU[jm])
	    jl = jm;
	else
	    ju = jm;
	}
    volatile double t = (u - ampTableU[jl]) / (ampTableU[ju] - ampTableU[jl]);
    volatile double y = ampTableY[jl] + (ampTableY[ju] - ampTableY[jl]) * t;
    volatile double w = 4095.0 * y + 0.5;
    return ((unsigned int) floor(w));
    }

unsigned int Pow2AmpWord(double pow) //convert power in watts to 12-bit Amplitude Word (remember amp ~ pow^0.5)

    {  /* Using calibration data of 20100914 */
    if (ampTableN > 0) // 2026-11: a table file is in use (LoadAmpTable); else the built-in table below, as before
	return (AmpWordFromTable(pow));
/*
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
*/

    /*
     * x are the power and y are the DDS amplitude settings */
   // const double x[12]= {0, 64.565, 257.040, 579.429, 1035.142, 1621.810, 2233.572, 2630.572, 2864.178, 2930.893, 2964.831,3054.921};

    //const double POWER=pow/POWMAX;

    /// calibration on 2011------------------begin----------------------------------------
   // const double x[11]= {0,139.6368361,517.606832,1135.010816,2162.718524,3411.929116,4920.395357,5807.644175,6123.503917,6324.118514,6382.634862}; //4-11-2011

   // const double y[11]= {0,   0.05,     0.1,    0.15,      0.2,     0.25,      0.3,     0.35,      0.4,     0.45,     0.5}; //4-11-2011
    /* d^2y/dx^2 (approximated numerically from above x and y): */
    //const double y2[12]={0, -4.00431e-6, -4.06644e-7, -1.16627e-7, -4.69904e-8, -5.83426e-9, 8.78769e-8, 2.78197e-7, 3.56388e-6, 1.43823e-5, 1.01685e-6, 0};  //4-6-2011
    //const double y2[11]={0,-8.72423E-07,-1.0308E-07,-3.93071E-08,-7.57751E-09,-4.989E-09,1.93744E-08,1.69468E-07,3.52141E-07,4.67121E-06,2.72701E-07};  /* First search through x to find the right interval */  //4-11-2011

   // double temp, aa, bb, cc, dd;
   // unsigned int ju, jm, jl;
   // ju = 12; jl = 0; jm = 0;  //ju=12; 4-6-2011
   // pow = pow*1000;
    /// calibration on 2011-------------------end--------------------------------------------


    /// calibration on 2015------------------begin----------------------------------------
    // Note: x[0] should be exactly zero, otherwise the interpolation will fail
    const double x[21]= {
	    0.0
	   , 16.21810097
	   , 66.0693448
	   , 149.6235656
	   , 275.4228703
	   , 413.047502
	   , 616.5950019
	   , 810.9610579
	   , 1083.926914
	   , 1327.394458
	   , 1678.804018
	   , 1972.422736
	   , 2398.832919
	   , 2691.534804
	   , 3162.27766
	   , 3531.831698
	   , 4120.975191
	   , 4415.704474
	   , 4841.723676
	   , 4988.844875
	   , 5188.000389
    };
    const double y[21]= {
	    0
	    ,0.05
	    ,0.1
	    ,0.15
	    ,0.2
	    ,0.25
	    ,0.3
	    ,0.35
	    ,0.4
	    ,0.45
	    ,0.5
	    ,0.55
	    ,0.6
	    ,0.65
	    ,0.7
	    ,0.75
	    ,0.8
	    ,0.85
	    ,0.9
	    ,0.95
	    ,1
    };

    const double y2[21]={
	    0
	   , -6.29706E-05
	   , -6.06527E-06
	   , -1.91977E-06
	   , -2.59289E-07
	   , -6.89764E-07
	   , 5.83225E-08
	   , -3.17006E-07
	   , 8.59475E-08
	   , -2.12084E-07
	   , 8.68326E-08
	   , -1.47302E-07
	   , 1.48973E-07
	   , -1.69252E-07
	   , 6.9221E-08
	   , -1.05204E-07
	   , 1.91834E-07
	   , -1.45076E-07
	   , 7.7639E-07
	   , -5.1286E-07
	   , 2.33752E-08
    };

    double temp, aa, bb, cc, dd;
       unsigned int ju, jm, jl;
       ju = 20; jl = 0; jm = 0;  // last index of the 21-point table (was 22, which read past x[]/y[]); ju=12; 4-6-2011
       pow = pow*1000;

    // Clamp to the table (review G2-11.1, G2-11.2). Below x[0] the spline extrapolated to a
    // negative fraction that wrapped to a huge unsigned word, so any negative power (even
    // -1e-17 W from a float difference) played at FULL amplitude; above x[20] the search
    // read past the arrays. !(pow > 0) also catches NaN. In-table powers are unchanged.
    if (!(pow > 0))
	return (0);
    if (pow >= x[20])
	return (4095);

    /// calibration on 2015------------------begin----------------------------------------



       /* Convert to mW */
    /* Find place in table: */
    /* Step through method: */
    /* while (pow > x[jm])+

	{
	jm++;
	if (jm > ju) break;
	}
    jl = jm; ju = jm+1;*/

    /* Bisection method: */
    while (ju - jl > 1) {
	jm = (ju+jl) >> 1; // take mean of ju and jl, round down to integer
	if (pow >=x[jm]) // test point and move boundary
	    jl = jm;
	else
	    ju = jm;
    }
    /* now pow should be between x[jl] and x[ju] */
    /* cubic spline interpolation: */
    /* for linear, set cc = 0 and dd = 0 */

	aa = (x[ju]-pow)/(x[ju]-x[jl]);
    bb = 1-aa;
    cc = (aa*aa*aa-aa)*(x[ju]-x[jl])*(x[ju]-x[jl])/6;
    dd = (bb*bb*bb-bb)*(x[ju]-x[jl])*(x[ju]-x[jl])/6;
    temp = y[jl]*aa+y[ju]*bb+y2[jl]*cc+y2[ju]*dd;


    /*cout << "pow: " << pow << " x[jl]: " << x[jl]<< " x[ju]: " << x[ju] << " percent: " << temp <<endl;*/
    unsigned int amp;
    amp = (unsigned int)floor(4095*temp);

 //   amp = (unsigned int)floor(4095*POWER);
//cout<<"output power is: "<<amp<<endl;
    return (amp);
    }

/*double AmpWord2Pow(unsigned int amp) // Convert amplitude word to power in Watts (remember pow ~ amp^2)
    {
    return (Volts2Pow(AmpWord2Volts(amp)));
    }*/

unsigned long Time2Tics(double seconds)
    {
    // 2026-11: + 1e-6 tic before the floor. A length typed on the pulse's own grid (7 us for a square pulse,
    // 0.504 ms for an AFP) reaches here as a double a hair BELOW the whole number of tics about one time in
    // three, and the bare floor then played one step less than typed: 6 us for 7, 62 AFP tics for 63, and a
    // 2 us Blackman was refused as 'below 2 us'. The lengths the lab's sequences use (0.12, 0.2, 0.36, 0.68,
    // 0.71, 0.96, 2.88, 3, 10 ms) were not among them. A length between grid points is floored as before.
    return ((unsigned long) floor(seconds * FIFOCLOCK / 8.0 + 1e-6)); //8 is the maximum number of registers need to be changed
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
