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
    clock_t t1=clock();
    cout<<"Starting time(ms):"<<t1*1000/CLOCKS_PER_SEC<<endl;
    string filename=""; // name of input file
    unsigned int totalnum ; // count number of pulses
    Pulse pulse; // main pulse (formerly called "test")
    // must create 'pulse' before other Pulses so that the pulses get destroyed in proper order
    // (avoids crash on exit)
    PInit pint;
    PEnd pend;
    PEnd2 pend2;
    pulse = pulse + pint;



    // parse command line and extract filename
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
#ifdef _DEBUG
		/*cout << "Pulse " << dec << num << ", type: " << dec
		 << parameters[num][4] << endl;*/
		fdebug << "Pulse " << dec << num << ", type: " << dec
			<< parameters[num][4] << endl;
#endif
		if (int(parameters[num][4]) < 1 || int(parameters[num][4]) > 4) // Check pulse type in range
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
		pulse = (pulse + testA) + pend2;
		}
		break;

	    case 2: // Blackman pulse
		{
		cout << "Blackman, f0 = " << f0 << "Hz";
		cout << ", t = " << duration << "s";
		cout << ", Pmax = " << maxpow << "W" << endl;

		if (maxpow > POWMAX)
		    {
		    cout << "WARNING: Power exceeds maximum" << endl;
		    }
		PBlackman testB(duration, f0, maxpow);
		pulse = (pulse + testB) + pend;
		}
		break;


	    case 3: // CW pulse
		{
		cout << "CW pulse, f0 = " << f0 << "Hz";
		cout << ", t = " << duration << "s";
		cout << ", Pmax = " << maxpow << "W" << endl;

		if (maxpow > POWMAX)
		    {
		    cout << "WARNING: Power exceeds maximum" << endl;
		    }
		PConstant testC(duration, f0, maxpow);
		pulse = (pulse + testC) + pend;
 		//pulse = (pulse + testC) ;
		}
		break;

	    case 4: // End pulse
	   		{
	   		cout << "End Pulse " << endl;;
	   		PEnd testD;
	   		pulse = (pulse + testD) ;
	   		}
	   		break;
	    default:
		{
		num = 101;
		cout << "Undefined pulse type or end of pulse list." << endl;
		}
		}
	}
//    cout << "Number of pulses:" << dec << totalnum << endl;

    }


    DDSIOWord *compressed = pulse.Compressed(); // Compress the pulse to remove redundant IO writes

    int ioerror=0;

    uInt32 * outputarray;
    outputarray = new uInt32[pulse.ios];

    // Build outputarray of raw IO data (move this into IO?)
    for (unsigned int ii = 0; ii < pulse.ios; ii++)
	{
	outputarray[ii] = compressed[ii].RawIO;
	}

 //   cout << "begin reading." << endl;
    //read from cooling file

        uInt32 data[MAXLINE];
        int pulse_cool=0;
        ifstream ppFile;
        ppFile.open("Cool.txt");
       // char comments[80];


        	while(!ppFile.eof()) // end of file?
        			{
        	ppFile >> hex >> data[pulse_cool];
        	pulse_cool++;}
        	//ppFile.get(comments,79);
        	pulse_cool--;


//    cout<<pulse.ios<<endl;

     for(unsigned int i=0; i<pulse.ios ;i++)
	 {
	 data[i+pulse_cool]=outputarray[i];
	 }

    cout<<"Before update(ms):"<<clock()*1000/CLOCKS_PER_SEC<<endl;
  //  ioerror = IO(data, pulse.ios+pulse_cool);
  //   ioerror = IO(outputarray, pulse.ios);
    cout << "IO error status (0 = ok): " << dec << ioerror << endl;

//#ifdef _DEBUG
    // for Debug only: make DATA.TXT file
	{
	cout << "Begin file output" << endl;
	ofstream pFile;
	pFile.open("Cool.txt");
	for (unsigned int i = 0; i < pulse.ios; i++)
	    {
	    pFile << hex << outputarray[i] << endl;//"\t" << dec << i << endl;
	    }
	pFile.close();
	cout << "End file output" << endl;
	}
//#endif


	// clear dynamic variables
    delete[] outputarray; outputarray = NULL;


    return (0);
    } // end main

