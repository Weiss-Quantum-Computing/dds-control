/*     pulse.cpp
	pulse class and related definitions
	Current version: 3.0  uses gcc compiler (MinGW version).
	Last modified 20100804
	*/

//
/* TODO: Pulse types
 *	1.	Write pulse variants
 *		f.	Pi* pulse (series of Blackmans)
 */
/* TODO: Some tidying up:
 * 	1.	add "const" identifiers in function calls where appropriate.
 * 	2.	Error trapping throughout
 */
/*
 * TODO: interface
 * 	1.	(done!) Use tab-delimited text files instead of excel files
 * 	2.	(done!) Specify file name on command line.
 */


#include <stdio.h>
#include <math.h>
#include <iostream>
#include <fstream>
#include <iomanip>
#include <string>
#include <windows.h>
#include <NIDAQmx.h>
#include <time.h>
#include <dos.h>
#include <conio.h>
using namespace std;

#include "DDSconstants.h" // some macros defining math and DDS constants
#include "conversions.h"  // some utility functions
#include "ad9852data.h"   // definitions of the AD9852-related classes
#include "pulse.h"        // definitions of pulse classes
#include "NI-PCIe-6536.h" // IO functions for PCIe-6536 card
#include "getpulse.h"     // Read pulse data from a file
#define DATAFILE "DATA.TXT" //human readable file
#define DEBUGFILE "debug.txt" // file to dump some debug info
#include "time.h"


int main(int argc, char* argv[])
    {
   // clock_t t1=clock();
   // cout<<"Starting time(ms):"<<t1*1000/CLOCKS_PER_SEC<<endl;
    string filename=""; // name of input file
    // Debug: test calibration fits
/*        cout << "Table of power calibration:" << endl;
        for (unsigned int num = 0; num < 60; num++)
    	{
    	double temp;
    	temp = num*0.05;
    	cout << "Power = " << temp << " W, percent = "<< ((double) Pow2AmpWord(temp))/4096.0 << endl;
    	}
*/
    cout << "NewDDS2-Cooling2.0-Cal, version " << VERSION << endl;
    if (argc<2)
	{
//	    cout << "No input file specified.  Using default: " << DEFAULTFILENAME << endl;
	    filename = DEFAULTFILENAME;
	}
    else if (argc>2)
	{
	    cout << "Too many command line parameters." << endl;
	    cout << "Correct syntax: ";
	    cout << argv[0] << "filename" << endl;
	    return -1;
	}
    else // argc must be correct!
	{
	    filename = argv[1];
	    cout << "Using input file " << filename << endl;
	}


    unsigned int totalnum ; // count number of pulses
    Pulse pulse; // main pulse (formerly called "test")
    // must create 'pulse' before other Pulses so that the pulses get destroyed in proper order
    // (avoids crash on exit)
    PInit pint;
    PEnd pend;
    PEnd2 pend2;
    PEndC pendC;
    pulse.Append(pint);



    // parse command line and extract filename


#ifdef _DEBUG
    // open debug file
    ofstream fdebug;
    fdebug.open(DEBUGFILE);
    {
    time_t starttime = time(NULL);
    string times(ctime(&starttime));
    fdebug << "BEGIN " << times << endl;
    }
#endif

    { // start a frame to check that the file read code is self-contained
    long double parameters[MAXPULSES][PULSEPARASIZE]; //desired frequency and amplitude from file
    ZeroArray(&parameters[0][0],long(MAXPULSES)*long(PULSEPARASIZE)); // initialize array
//    cout << "Reading " << filename << endl;
    totalnum = 0;
    // Set parameter array
    if (GetPulse(filename.c_str(), MAXPULSES, parameters) == 0) // GetPulse succeeds
	    {

	    // This loop counts and prints out the pulses
	    for (unsigned int num = 0; num < MAXPULSES; num++)
		{//reading once takes ~9.5ms
		cout << "Reading pulse " << num << endl;
		if (int(parameters[num][4])==0/*int(parameters[num][4]) < 1 || int(parameters[num][4]) > 9)*/ )// Check pulse type in range
		    {
		    totalnum = num;
		    break;
		    }
		}
	    }
	else // GetPulse fails
	    {
	    cout << "Error reading pulse file" << endl;
	    cout << "Aborting." << endl;
	    return -1;
	    }

    cout << "Number of pulses:" << dec << totalnum << endl;

    // Create the Pulse train
    // These next variables are redundant, could be removed
    long double f0; //Center frequency, 1uHz resolution
    long double HSR; //Half-frequency sweeping range
    long double duration; //pulse duration
    long double maxpow; // maximum pulse power
    for (unsigned int num = 0; num < totalnum; num++)
        {
	f0       = parameters[num][0];
	HSR      = parameters[num][1];
	duration = parameters[num][2] * 0.001;
	maxpow   = parameters[num][3];
	cout << "Pulse " << dec << num+1 <<": ";
	switch (int(parameters[num][4]))
		{
	case -1: // Power off
	    {
	    cout << "Power off" << endl;
	    POff off;
	    pulse.Append(off);
	    }
	    break;
	case 1: // Adiabatic fast passage
		{
		cout << "Adiabatic, f0 = " << f0 << "Hz";
		cout << ", t = " << duration << "s";
		cout << ", Pmax = " << maxpow << "W";
		cout << ", HSR = "<< HSR << "Hz" << endl;

		if (maxpow > POWMAX)
		    {
		    cout << "WARNING: Power exceeds maximum" << endl;
		    }
		PAdiabatic testA(duration, f0, HSR, maxpow);
		pulse.Append(testA);
		pulse.Append(pend2);
		}
		break;

	    case 2: // Blackman pulse
		{
		cout << "Blackman, f0 = " << f0 << "Hz";
		cout << ", t = " << duration << "s";
		cout << ", phase = " << HSR <<"pi";
		cout << ", Pmax = " << maxpow << "W" << endl;

		if (maxpow > POWMAX)
		    {
		    cout << "WARNING: Power exceeds maximum" << endl;
		    }
		PBlackman testB(duration, f0, HSR, maxpow); // HSR = phase in units of pi
		pulse.Append(testB);
		pulse.Append(pendC); //phase coherent
		}
		break;

	    case 22: // PStar pulse, three pulse, not the same length, composite pi pulse, 2014-3-13
		{
		cout << "Composite Pi, f0 = " << f0 << "Hz";
		cout << ", t = " << duration << "s";
		cout << ", phase = " << HSR <<"pi";
		cout << ", Pmax = " << maxpow << "W" << endl;

		if (maxpow > POWMAX)
		    {
		    cout << "WARNING: Power exceeds maximum" << endl;
		    }
		PStar testBB(duration, f0, HSR, maxpow); // HSR = phase in units of pi
		pulse.Append(testBB);
		pulse.Append(pendC); //phase coherent
		}
		break;

	    case 3: // CW pulse
		{
		cout << "CW pulse, f0 = " << f0 << "Hz";
		cout << ", t = " << duration << "s";
		cout << ", phase = " << HSR <<"pi";
		cout << ", Pmax = " << maxpow << "W" << endl;
#ifdef _DEBUG
		fdebug << "CW pulse, f0 = " << f0;
		fdebug << ", t = " << duration;
		fdebug << ", phase = " << HSR <<"pi";
		fdebug << ", Pmax = " << maxpow << endl;
#endif
		if (maxpow > POWMAX)
		    {
		    cout << "WARNING: Power exceeds maximum" << endl;
		    }
		PConstant testC(duration, f0, HSR, maxpow); // HSR = phase in units of pi
		pulse.Append(testC);
		pulse.Append(pendC);   //2013/9/2, testing uwave coherence, coherence square pulse
 		//pulse = (pulse + testC) ;
		}
		break;

	    case 33: // CORPSE sequence  2015-5-8
		{
		cout << "BB1 pulse, f0 = " << f0 << "Hz";
		cout << ", t = " << duration << "s";
		cout << ", rotation = " << HSR <<"pi";
		cout << ", Pmax = " << maxpow << "W" << endl;

		if (maxpow > POWMAX)
		    {
		    cout << "WARNING: Power exceeds maximum" << endl;
		    }
		PCORPSE testCORPSE(duration, f0, HSR, maxpow); // HSR = phase in units of pi
		pulse.Append(testCORPSE);
		pulse.Append(pendC);

		}
		break;

	    case 66: // bb1 pi-pulse based on square  2015-4-27
		{
		cout << "BB1 pulse, f0 = " << f0 << "Hz";
		cout << ", t = " << duration << "s";
		cout << ", rotation = " << HSR <<"pi";
		cout << ", Pmax = " << maxpow << "W" << endl;

		if (maxpow > POWMAX)
		    {
		    cout << "WARNING: Power exceeds maximum" << endl;
		    }
		PBB1 testBB(duration, f0, HSR, maxpow); // HSR = phase in units of pi
		pulse.Append(testBB);
		pulse.Append(pendC);

		}
		break;

	    case 661: // bb1 pi-pulse based on Blackman  2015-4-28
		{
		cout << "BB1 pulse, f0 = " << f0 << "Hz";
		cout << ", t = " << duration << "s";
		cout << ", rotation = " << HSR <<"pi";
		cout << ", Pmax = " << maxpow << "W" << endl;

		if (maxpow > POWMAX)
		    {
		    cout << "WARNING: Power exceeds maximum" << endl;
		    }
		PBB12 testBB(duration, f0, HSR, maxpow); // HSR = phase in units of pi
		pulse.Append(testBB);
		pulse.Append(pendC);

		}
		break;

	    case 4: // End pulse
		{
	   		cout << "End Pulse " << endl;
	   		PEnd testD;
	   		pulse.Append(testD);
		}
	   		break;

	    case 5: // pi star CW
		{
	   	   	cout << "1/2 Pi Pulse " << endl;
	   	   	PStarCW testE(duration, f0, maxpow);
	   	   	pulse.Append(testE);
	   	   	pulse.Append(pend);
		}
	   	   	break;

	    case 6: // pi star Blackman
		{
	   	   	cout << "Pi Star Pulse " << endl;
	   	   	PStarBlackman testF(duration,HSR * 0.001, f0, maxpow);
	   	   	pulse.Append(testF);
	   	   	pulse.Append(pend);
		}
	   	   	break;
	    case 7: // Ramsey pulses
		{
		cout << "Ramsey, f0 = " << f0 << "Hz";
		cout << ", t = " << duration << "s";
		cout << ", Pmax = " << maxpow << "W";
		cout << ", wait = "<< HSR*0.001 << "s" << endl;

		if (maxpow > POWMAX)
		    {
		    cout << "WARNING: Power exceeds maximum" << endl;
		    }
		PRamsey testG(duration, f0, HSR*0.001, maxpow);
		pulse.Append(testG);
		pulse.Append(pend);
		}
		break;
	    case 8: // Echo pulses
	   	{
	   	cout << "Echo, f0 = " << f0 << "Hz";
	   	cout << ", t = " << duration << "s";
	   	cout << ", Pmax = " << maxpow << "W";
	   	cout << ", wait = "<< HSR*0.001 << "s" << endl;

	   	if (maxpow > POWMAX)
	   	    {
	   	    cout << "WARNING: Power exceeds maximum" << endl;
	   	    }
	   	PEcho testH(duration, f0, HSR*0.001, maxpow);
	   	pulse.Append(testH);
	   	pulse.Append(pend);
	   	}
	   	break;
	    case 9: // Constant pulse (doesn't end)
		{
		cout << "CW pulse, f0 = " << f0 << "Hz";
		cout << ", t = " << duration << "s";
		cout << ", phase = " << HSR <<"pi";
		cout << ", Pmax = " << maxpow << "W" << endl;

		if (maxpow > POWMAX)
		    {
		    cout << "WARNING: Power exceeds maximum" << endl;
		    }
		PConstant testI(duration, f0, HSR, maxpow); // HSR = phase in units of pi
		//pulse = (pulse + testC) + pend;
 		pulse.Append(testI);
		}
		break;
	    case 10: // RamseyPhase pulses, with a variable wait time and variable phase
		{
		cout << "RamseyPhase, f0 = " << f0 << "Hz";
		cout << ", wait time t = " << duration << "s";
		cout << ", Pmax = " << maxpow << "W";
		cout << ", phase = "<< HSR << "pi" << endl;

		if (maxpow > POWMAX)
		    {
		    cout << "WARNING: Power exceeds maximum" << endl;
		    }
		PRamseyPhase testJ(duration, f0, HSR, maxpow);
		pulse.Append(testJ);
		pulse.Append(pend);
		}
		break;
	    case 11: // Blackman follower pulse, variable amplitude and phase, same freq as previous one
		{
		cout << "Blackman follower, f0 = previous one";
		cout << ", duration  = " << duration << "s";
		cout << ", Pmax = " << maxpow << "W";
		cout << ", phase = "<< HSR << "pi" << endl;

		if (maxpow > POWMAX)
		    {
		    cout << "WARNING: Power exceeds maximum" << endl;
		    }
		PFollower testK(duration, f0, HSR, maxpow);
		pulse.Append(testK);
		pulse.Append(pendC);
		}
		break;

	    default:
		{
		num = 101;
		cout << "Undefined pulse type or end of pulse list." << endl;
		}
		}
	}
    cout << "Number of pulses: " << dec << totalnum << endl;

    }
//    clock_t t3=clock();
//        cout<<"After reading(ms):"<<t3*1000/CLOCKS_PER_SEC<<endl;

    DDSIOWord *compressed = pulse.Compressed(); // Compress the pulse to remove redundant IO writes
#ifdef _DEBUG
    cout << "Pulse definitions complete." << endl;
    //cout << "Ready to test output.  Press ENTER to continue." << endl;
    //getchar();
#endif
    int ioerror=0;

    uInt32 * outputarray;
    outputarray = new uInt32[pulse.ios];

    // Build outputarray of raw IO data (move this into IO?)
    for (unsigned int ii = 0; ii < pulse.ios; ii++)
	{
	outputarray[ii] = compressed[ii].RawIO;
	}

    cout<<"Number of data words: "<<dec<<pulse.ios<<endl;
    cout<<"FIFO clock rate: "<<dec<<FIFOCLOCK<< " Hz"<<endl;
 //   cout<<"Before update(ms):"<<clock()*1000/CLOCKS_PER_SEC<<endl;
   // ioerror = IO(outputarray, pulse.ios);
 //   cout << "IO error status (0 = ok): " << dec << ioerror << endl;


    // for Debug only: make DATA.TXT file
	{
	cout << "Begin file output" << endl;
	ofstream pFile;
	string str="RAW";
	str.append(filename);
	pFile.open(str.c_str());

	//pFile << pulse.ios << endl;
	for (unsigned int i = 16; i < pulse.ios; i++)
	    {
	    pFile << hex << outputarray[i] << '\n';   // jump the reset session
	    //dec << i << endl;
	    }
	pFile.close();
	cout << "End file output" << endl;
	}







    // clear dynamic variables
    delete[] outputarray; outputarray = NULL;



    return (0);
    } // end main

