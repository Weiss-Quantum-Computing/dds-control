/*  pulse.cpp
	pulse class and related definitions
	Current version: 20100621 uses gcc compiler.
	*/

	/* Replacing this from Yang's code:
	static unsigned int KIND[10][10]; // Pulse shape (1) adiabatic sweeping (2) Blackman (3)square wave
	double F0[10][10]; //center frequency, 1uHz resolution
	double HSR[10][10]; // Half-frequency sweeping range
	double delta_F0[10][10]; // center frequency scanning range
    double AMP[10][10]; // Peak Amplitude, Min 0.0, Max 1.0 
	double delta_AMP[10][10];// Amplitude scanning range
	double Duration[10][10]; // duration for each pulse in one cycle, array, the front factor is in ms
	*/
	
// Define some constants for the AD9852 chip
// Need to check code for precision problems
// The AD9852 has a 40-bit frequency register, but standard C data types are only 32 bits
//
//
//#include "DDSfunc.h"
#include <stdio.h>
#include <math.h>
#include <iostream>
#include <fstream>
#include <iomanip>
#include <string>
using namespace std;
// My own includes.  Really these are just some code that
// I moved out to clean up this main file.
// TODO: change these to libraries or independent source files?
#include "DDSconstants.h" // some macros defining math and DDS constants
#include "conversions.h"  // some utility functions
#include "ad9852data.h"   // definitions of the AD9852-related classes
#include "pulse.h"        // definitions of pulse classes
#include "NI-PCIe-6536.h" // IO functions for PCIe-6536 card

#define DATAFILE "DATA.TXT" //huamn readable file
// TODO: add DDS board Address Bus bits

   /* Initiate Data Array
   Each line consists of (strobe mode[2 Hex], register address[2 Hex], data[2 Hex], I/O mode[2 Hex])

   Register addresses:
   00-01 Phase adjust 1
   02-03 Phase adjust 2
   04-09 Frequency 1
   0A-0F Frequency 2
   10-15 Delta frequency (for ramps)
   16-19 Update clock (for ramps)
   1A-1C Ramp rate clock
   1D-20 Control registers
   21-22 Shaped key multiplier (amplitude)
   23-24 Don't care
   25    Shaped key ramp rate
   26-27 Control DAC
   */
 

int main(void)
    {
    cout << "Hello World!" << endl;
#ifdef _DEBUG
    cout << "DEBUG mode!!" << endl;

#endif

    PInit pint;
    PEnd pend;
    //   PConstant testc(0.2,100.0, 0.01);
     //  PBlackman testc(0.2, 100.0, 0.01);
       PAdiabatic testc(0.2, 1000.0, 999.0, 0.01);
    Pulse test1 = pint + testc; // testing sum
    Pulse test = test1 + pend;

    if (test.tics == 0)
	{
	    cout << "Test pulse creation error" << endl;
	    return 1; // Error in creation of test
	}
    cout << "Test tics: " << dec << test.tics << endl;

    cout << "Amplitude v. Time:" << endl;
/*    for (unsigned int ii=0;ii<test.tics;ii++)
	{
	    cout << "Time: " << ii << ", Amp: " << test.datap[ii].ReadOSKMult() << endl;
	}*/
    cout << "Press ENTER to continue" << endl;
    getchar();

    cout << "IOs for test: " << dec << (int) test.ios << endl;
    cout << "IO dump for test:" << endl;

    DDSIOWord * compressed = test.Compressed(); ///////////////////////////////////recover from here

    cout << "Ready to test output.  Press ENTER to continue" << endl;
    getchar();
    int ioerror;
    // the following should be moved out to the IO function ////////////////////////////recover from here

    uInt32 * outputarray;
    outputarray = new uInt32[test.ios];


    for (unsigned int ii=0;ii<test.ios;ii++)
	{
	    outputarray[ii]=compressed[ii].RawIO;
//	    if (ii %  8 == 0)
//		{
//		cout << endl;
//		cout << "IO count = " << hex << showbase << ii <<":   ";
//		}
//	    cout << hex << noshowbase << setfill('0') << setw(8) << outputarray[ii] << "   ";
    	}
/*
    unsigned int counter =0;
    for (unsigned int ii=0;ii<test.tics;ii++)
    		    {
    			for (unsigned char jj=0;jj<test.writep[ii].changes;jj++)
    			    {

    				outputarray[counter] = test.writep[ii].Words[jj].RawIO ;
    			        counter++;
    			    }
    		    };
*/
    cout << endl;
    ioerror = IO(outputarray,test.ios);
    cout << "IO error status (0 = ok): " << dec << ioerror << endl;
    cout << "Done! Press ENTER." << endl;
#ifdef _DEBUG
    cout << "DEBUG mode!!" << endl;
#endif
    //FILE * pFile;
    //pFile = fopen (DATAFILE,"w");
    cout << "Begin file output" << endl;
    ofstream pFile;
    pFile.open(DATAFILE);

        for(unsigned int i=0;i<test.ios;i++)
    	{
    		//ss=HexN(Data[i],8);
    		// File format:  Hex value, binary value, decimal value, line number
    		//fprintf(pFile,"%u  %u\n",outputarray[i],i);
		pFile << hex << outputarray[i] << "   " << dec << i << endl;
    	}
        //fclose (pFile);
        pFile.close();
    cout << "End file output" << endl;

#ifndef _DEBUG
    cout << "Release version" << endl;
#endif
    //getchar();
    // cleaning up memory
    delete[] compressed; compressed = NULL;
//    cout << "compressed removed" << endl;
    delete[] outputarray; outputarray = NULL;
//    cout << "outputarray removed" << endl;
    return (0);
    }


/* TODO:

	0.	Store Raw as DDSIO[] (where? in Pulse? other?)
		a.	Insert strobes (iomode -> 1 -> 2 or use board v. 2.0 jumpers and pick iomode = 2 always)
	1.	Write pulse variants
		a.	X Initialization
		c.	X Square pulse, const freq
		d.	X Blackman pulse, const freq
		e.	X Pi pulse, Pi/2 pulse (variants of Blackman)
		f.	Pi* pulse (series of Blackmans)
		g.	Adiabatic fast passage (chirp and amp)
		h.	Shutdown (same as initialization?)
	2.	Write DeltaRegisters so we only send register changes to the board
	3.	Write sequence: pulse -> Registers -> DeltaRegisters ->RawIO
		a.	Initialization is different
		b.	Ramps also, if using the internal method
	4.	Debug previous sequence, compare to Yang's code output
	5.	Write board IO
	6.	Write file IO so that we don't need to recompile every time we change the pulses
*/

/* TODO: Some tidying up:
 * 	1.	add "const" identifiers in function calls where appropriate.
 * 	2.	Error trapping throughout
 */

/*	Sequence:
	1.	Initialize by setting DDSOpt = 0 for 5 tics
	2.	Load one chunk of data using DDSOpt = 1
		2a.	"chuck" = set of all register values
		2b.	Each chuck sent and then loaded with strobe up, strobe down sequence
	3.	Update output using DDSOpt = 2 (Don't care about data bits)
	4.	DDSOpt = 3 is for FSK/BPSK/Hold modes, where control is by external BNC
		4a.	Essentially this is a "hold" setting, likely default if you want nothing
			to change on a clock tic.
*/
