/*-------------------------------------------------------------------*/
//      NewDDS2.0-Cooling
//	Sending data to DDS board
//	Current version: 2.0  uses gcc compiler (MinGW version).
//	Last modified 20110420, Yang.
/*-------------------------------------------------------------------*/





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

#include "NI-PCIe-6536.h" // IO functions for PCIe-6536 card
#define DATAFILE "DATA.TXT" //human readable file
#define DEBUGFILE "debug.txt" // file to dump some debug info
#include "time.h"




int main(int argc, char* argv[])
    {

    const string            DEFAULTFILENAME = "Pulse parameters.txt"; // default filename
    const unsigned int      MAXDATA         = 250000;   // maximum number of data to read

    string filename=""; // name of input file

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


    uInt32* data= new uInt32[100*MAXDATA]; //1000 would fail
   // uInt32 data[MAXDATA];
    unsigned int count=0;
    ifstream ppFile;
    ppFile.open(filename.c_str());

    while(!ppFile.eof())
    {

	if (count>100*MAXDATA-1)
	    {
		cout << "ERROR!  Pulse file length exceeds MAXDATA"  << endl;
		return 99;
	    }

    	ppFile >> hex >> data[count];
        count++;

    }
    ppFile.close();
    count--;
    int ioerror=0;
    cout<<"Before update(ms):"<<clock()*1000/CLOCKS_PER_SEC<<endl;
    ioerror = IO(data, count);
        cout << "IO error status (0 = ok): " << dec << ioerror << endl;

    delete [] data;

#ifdef _DEBUG
    // for Debug only: make DATA.TXT file
	{
	cout << "Begin file output" << endl;
	ofstream pFile;
	string str="RAW";
	str.append(filename);
	pFile.open(str.c_str());

	//pFile << pulse.ios << endl;
	for ( int i = 0; i < count; i++)
	    {
	    pFile << hex << data[i] << endl;//" " << dec << i << endl;
	    }
	pFile.close();
	cout << "End file output" << endl;
	}
#endif




    return (0);
    }

