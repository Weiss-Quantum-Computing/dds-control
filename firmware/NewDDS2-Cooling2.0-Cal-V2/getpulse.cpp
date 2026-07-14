/*
 * getpulse.cpp
 *
 *  Created on: Aug 3, 2010
 *      Author: Yang
 */
// TODO: Change this to read text file instead of Excel
#include "getpulse.h"
#include <fstream>
#include <iostream>
#include <iomanip>
#include <string>

//using namespace libxl;
using namespace std;
//#define USE_EXCEL  // For future use, for switching to text-file type input.
#ifdef USE_EXCEL
int GetPulse(const char* filename, const unsigned maxp,
	long double parms[MAXPULSES][PULSEPARASIZE])
    {
    /* GetPulse (filename, maxp)
     * Reads excel file for pulse definitions
     */
    // "maxp" is the max pulse number

    //unsigned int row = index;//read a specific pulse


    Book * book = xlCreateBook();
    if (book->load(filename)) //open the excel book

	{
	Sheet* sheet = book->getSheet(0); //get 1st sheet fromt the excel book
	if (sheet)
	    {
	    // loop over rows
	    for (unsigned int row = 0; row < maxp; ++row) // skip first row (headers)

		{
		for (unsigned int i = 0; i < PULSEPARASIZE; i++) //read PULSEPARASIZE parameters in the row

		    {
		    parms[row][i] = sheet->readNum(row+1, i); //the first cell index is 0,0
		    }
		if (parms[row][PULSEPARASIZE-1] == 0)
		    {
		    break; // pulse type 0 is end.
		    }
		}
	    }
	}
    else
	{
	cout << "ERROR: Unable to open " << filename << endl;
	return 1;
	}
    book->release();

    return 0;
    }
#endif

#ifndef USE_EXCEL
// This case uses tab-delimited text file
int GetPulse(const char* filename, const unsigned maxp,
	long double parms[MAXPULSES][PULSEPARASIZE])
    {
    ifstream pFile;
    pFile.open(filename);
    if (!pFile)
	{
	cout << "ERROR: Unable to open " << filename << endl;
	return 1;
	}
    //  discard first row (header)
	{
	char headers[256];
	pFile.getline(headers, 255, '\n');
//	cout << "headers: " << headers << endl;
	}
    for (unsigned int row = 0; row < maxp; ++row)
	{
	char comments[80];
	for (unsigned int column = 0; column < PULSEPARASIZE; ++column)
	    {
	    pFile >> parms[row][column]; // read one value
#ifdef _DEBUG
	    cout << dec << parms[row][column] << "  ";
#endif /* debug */
	    if (pFile.eof()) // end of file?
		{
		break;
		}
	    }
	pFile.get(comments,79);
#ifdef _DEBUG
	cout << comments;
	cout << endl;
#endif //debug
	if (pFile.eof() || parms[row][PULSEPARASIZE - 1] == 0) // end of file?
	    {
	    break;
	    }
	}
    return 0;
    }

#endif
