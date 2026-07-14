// pulse.cpp
// definitions of pulse classes

#ifndef PULSE_H_
#define PULSE_H_

#include "DDSconstants.h"
#include "conversions.h"
#include "ad9852data.h"
#include<math.h>

class Pulse
// This is the parent of the other pulse classes.
// Probably no reason to ever use this directly.
// Constructor: Pulse pulse (double length); length is in seconds
    {
public:
    AD9852Reg * datap; // Pointer to data
    DDSIOWriteReg * writep; // Pointer to write form
    unsigned int ios; // number of io operations
    unsigned long tics; // length of pulse in clock tics
    unsigned long capacity; // allocated size of datap/writep (>= tics); used by Append() for amortized growth

    // methods
    double Length(void) // length of pulse in seconds
	{
	return ((double) tics / INTCLOCK);
	}

    Pulse() // default constructor has length 1 tic (should I just throw an error here?)
	{
	tics = 1;
	datap = new AD9852Reg[1];
	writep = new DDSIOWriteReg[1];
	//ios = 40;


	for(unsigned int jj = 0; jj < 16; jj++)
	{
	    writep[0].Words[jj] = DDSIOWord(DIP, IORESET,  0, 0x23, 0, jj, 1); // call master reset and hold at least longer than 10 clock cycles
	    writep[0].changes = 16;
	}


            ios = writep[0].changes;
            capacity = tics;

	}

    Pulse(unsigned long ticlength) // constructor for specified number of tics
	{
	if (ticlength > MAXSAMPLES)
	    {
	    tics = 0; // If tics = 0 -> error
	    datap = 0; // pointer NULL
	    writep = 0; // pointer NULL
	    ios = 0;
	    capacity = 0;
	    cout << "Pulse too long!! The output of ticlength =" << ticlength
		    << endl;
	    }
	else
	    {
	    tics = ticlength;

	    datap = new AD9852Reg[tics];
	    writep = new DDSIOWriteReg[tics]; // note that in general this can be longer than datap
	    ios = 0;
	    capacity = tics;
	    for (unsigned int ii = 0; ii < tics; ii++)
		{
		ios += writep[ii].changes;
		}
	    }
	}

    ~Pulse() // destructor
	{
	delete[] datap;
	datap = NULL; // delete data and null out pointers
	delete[] writep;
	writep = NULL;
	}

    Pulse operator+(const Pulse & second) // + will concatenate pulses
	{
	unsigned long newtics;
	newtics = tics + second.tics;
	Pulse outpulse(newtics);
	for (unsigned long ii = 0; ii < tics; ii++)
	    {
	    outpulse.datap[ii] = datap[ii];
	    outpulse.writep[ii] = writep[ii];
	    }

	for (unsigned long jj = 0; jj < (second.tics); jj++)
	    {
	    outpulse.datap[jj + tics] = second.datap[jj];
	    outpulse.writep[jj + tics] = second.writep[jj];
	    }
	outpulse.ios = ios + second.ios;
	return outpulse;
	}

    void Append(const Pulse & seg) // append seg onto the end of *this, in place.
	// Unlike operator+, this grows the buffer geometrically (like std::vector)
	// instead of reallocating+copying the whole prefix on every call, so building
	// a pulse train of N segments is O(total tics) instead of O(N^2).
	{
	unsigned long needed = tics + seg.tics;
	if (needed > capacity)
	    {
	    unsigned long newcap = needed * 2; // amortized doubling
	    AD9852Reg * newdatap = new AD9852Reg[newcap];
	    DDSIOWriteReg * newwritep = new DDSIOWriteReg[newcap];
	    for (unsigned long ii = 0; ii < tics; ii++)
		{
		newdatap[ii] = datap[ii];
		newwritep[ii] = writep[ii];
		}
	    delete[] datap;
	    delete[] writep;
	    datap = newdatap;
	    writep = newwritep;
	    capacity = newcap;
	    }
	for (unsigned long jj = 0; jj < seg.tics; jj++)
	    {
	    datap[tics + jj] = seg.datap[jj];
	    writep[tics + jj] = seg.writep[jj];
	    }
	tics = needed;
	ios += seg.ios;
	}

    Pulse operator*(unsigned long mult) // Scalar multiplication = duplication
	{
	Pulse outpulse(tics * mult);
	for (unsigned long ii = 0; ii < mult; ii++)
	    {
	    for (unsigned long jj = 0; jj < tics; jj++)
		{
		outpulse.datap[ii * tics + jj] = datap[jj];
		outpulse.writep[ii * tics + jj] = writep[jj];
		}
	    if (ii != 0)
		{
		outpulse.writep[ii * tics] = DDSIOWriteReg(datap[0], datap[tics
			- 1]); // bridge the gaps
		}
	    }
	outpulse.ios = 0;
	for (unsigned int ii = 0; ii < outpulse.tics; ii++)
	    {
	    outpulse.ios += outpulse.writep[ii].changes;
	    }
	return (outpulse);
	}

    Pulse& operator=(Pulse A) // This guy is a little weird.  It doesn't work for simple A = B.
	{
	ios = A.ios;
	tics = A.tics;
	delete[] datap;
	datap = NULL; // delete old data
	delete[] writep;
	writep = NULL;
	datap = new AD9852Reg[tics];
	writep = new DDSIOWriteReg[tics]; // note that in general this can be longer than datap
	for (unsigned int ii = 0; ii < tics; ii++)
	    {
	    datap[ii] = A.datap[ii];
	    writep[ii] = A.writep[ii];
	    }
	return *this;
	}

    DDSIOWord * Compressed() // change output to DDSIOWord[]
	{
	DDSIOWord * comp;
	comp = new DDSIOWord[ios];
	unsigned int iocount = 0;

	for (unsigned int ii = 0; ii < tics; ii++)
	    {
	    for (unsigned char jj = 0; jj < writep[ii].changes; jj++)
		{
		if (iocount > ios)
		    {
		    cout << "Error: iocount too big in Compressed()" << endl;
		    }
		comp[iocount].RawIO = writep[ii].Words[jj].RawIO;
		comp[iocount].Time = ii;
		iocount++;
		}
	    }
	return comp;
	}
    };

class PInit: public Pulse // Placeholder pulse to initialize DDS data bus
    {
public:
    //PInit() :
    PInit() :
	Pulse((unsigned long) 0) // Syntax is OK, despite editor complaints
	{
   	//writep[0].Words[2] = DDSIOWord(DIP, IOUPDATE, 0, 0x22, 0, 7, 0); //self-mask signal writes 0 here
    	//writep[0].changes = 3;
	//ios = 3;
	}
    };
	/*Pulse((unsigned long) 1 ) // Syntax is OK, despite editor complaints
	{
	AD9852Reg registers;
	// set all registers to some default values
	registers.CtrlReg.OSKEn    = 1; //     5	OSK enable                         0    Enable amplitude control
	registers.CtrlReg.OSKInt   = 0;
	registers.CtrlReg.IOUpClk  = 0; //     8	IO update clock in/out             0    Turn on!
	registers.CtrlReg.Mode[0]  = 0;
	registers.CtrlReg.Mode[1]  = 0;
	registers.CtrlReg.Mode[2]  = 0; //   9-11	Output operating mode             000   single tone mode
	registers.CtrlReg.PLLMult  = REFMULT;
	registers.CtrlReg.PLLRange = 1;
	registers.UpdateCtrlReg(); //
	registers.SetFreq1(0);
	registers.SetFreq2(0);
	registers.SetRampClk(0);
	registers.SetOSKMult(0);
	datap[0] = registers;
	writep[0] = DDSIOWriteReg(datap[0]);
	ios = 40; // force all registers to be loaded for PInit;
	       //    writep[1].Words[0] = DDSIOWord(DIP, IOLOAD, 0, 0x23, 0, 0, 1);


	}
    };*/

class PEnd: public Pulse // To End a pulse
    {
public:
    PEnd() :
	Pulse((unsigned long) 1)
	{
	// TODO: Rewrite using registers
	// Set frequency = 0
	writep[0].Words[0] = DDSIOWord(DIP, IOLOAD, 0, 0x04, 0, 0, 1);
	writep[0].Words[1] = DDSIOWord(DIP, IOLOAD, 0, 0x05, 0, 1, 1);
	writep[0].Words[2] = DDSIOWord(DIP, IOLOAD, 0, 0x06, 0, 2, 1);
	writep[0].Words[3] = DDSIOWord(DIP, IOLOAD, 0, 0x07, 0, 3, 1);
	writep[0].Words[4] = DDSIOWord(DIP, IOLOAD, 0, 0x08, 0, 4, 1);
	writep[0].Words[5] = DDSIOWord(DIP, IOLOAD, 0, 0x09, 0, 5, 1);
	// Set amplitude = 0
	writep[0].Words[6] = DDSIOWord(DIP, IOLOAD, 0, 0x21, 0, 6, 1);
	writep[0].Words[7] = DDSIOWord(DIP, IOUPDATE, 0, 0x22, 0, 7, 0); //self-mask signal writes 0 here
	//writep[0].Words[7] = DDSIOWord(DIP, IOUPDATE, 0, 0x22, 0, 7, 1); //self-mask signal writes 0 here
	ios = 8;
	writep[0].changes = 8;
	}
    };

class PEndC: public Pulse // To End a pulse without clearing phase, i.e., phase coherent
    {
public:
    PEndC() :
	Pulse((unsigned long) 1)
	{
	writep[0].Words[0] = DDSIOWord(DIP, IOLOAD, 0, 0x21, 0, 0, 1);
	writep[0].Words[1] = DDSIOWord(DIP, IOUPDATE, 0, 0x22, 0, 1, 0); //self-mask signal writes 0 here
	ios = 2;
	writep[0].changes = 2;
	}
    };


class PEnd2: public Pulse // To End a AFP pulse
    {
public:
    PEnd2() :
	Pulse((unsigned long) 1)
	{
	// TODO: Rewrite using registers
	// Set delta frequency = 0
	writep[0].Words[0] = DDSIOWord(DIP, IOLOAD, 0, 0x10, 0, 0, 1);
	writep[0].Words[1] = DDSIOWord(DIP, IOLOAD, 0, 0x11, 0, 1, 1);
	writep[0].Words[2] = DDSIOWord(DIP, IOLOAD, 0, 0x12, 0, 2, 1);
	writep[0].Words[3] = DDSIOWord(DIP, IOLOAD, 0, 0x13, 0, 3, 1);
	writep[0].Words[4] = DDSIOWord(DIP, IOLOAD, 0, 0x14, 0, 4, 1);
	writep[0].Words[5] = DDSIOWord(DIP, IOLOAD, 0, 0x15, 0, 5, 1);
	writep[0].Words[6] = DDSIOWord(DIP, IOLOAD, 0, 0x1f, 0x46, 6, 1);
	// Set amplitude = 0
	writep[0].Words[7] = DDSIOWord(DIP, IOLOAD, 0, 0x21, 0, 7, 1);
	writep[0].Words[8] = DDSIOWord(DIP, IOUPDATE, 0, 0x22, 0, 8, 0); //self-mask signal writes 0 here
	//writep[0].Words[7] = DDSIOWord(DIP, IOUPDATE, 0, 0x22, 0, 7, 1); //self-mask signal writes 0 here
	ios = 9;
	writep[0].changes = 9;
	}
    };

class PConstant: public Pulse // Constant "pulse"   // changed  2015-5-6, increase timing resolution to 1 us
    {
public:

    PConstant(double length, double freq, double phase, double power) :
	Pulse(1+Time2Tics(8*length))
	{
	    {
	    AD9852Reg registers;
	    //                                    Bits	Function                       Default  Reason for change
	    registers.CtrlReg.OSKEn   = 1; //     5	OSK enable                         0    Enable amplitude control
	    registers.CtrlReg.OSKInt  = 0;
	    registers.CtrlReg.IOUpClk = 0; //     8	IO update clock in/out             0    Turn on!
	    // Set mode to single tone
	    registers.CtrlReg.Mode[0] = 0;
	    registers.CtrlReg.Mode[1] = 0;
	    registers.CtrlReg.Mode[2] = 0; //   9-11	Output operating mode             000 (Single tone)
	    registers.CtrlReg.ClrAcc  = 0; // 2013/9/2, testing uwave coherence
	    //registers.CtrlReg.ClrAcc  = 1; //    14	Clear Accumulators                 0    Reset phase
	    registers.CtrlReg.ClrAcc1 = 0;
	    registers.CtrlReg.PLLMult = REFMULT;
	    registers.UpdateCtrlReg(); //   Must do this each time the control registers change
	    registers.SetFreq1(Hz2FreqWord(freq)); // set frequency
	    //registers.SetFreq2(Hz2FreqWord(freq)); // set frequency
	    //cout << "OSKMult = " << dec << Pow2AmpWord(power) << endl;
	    registers.SetPhaseAdj1(Phase2PhaseWord(phase)); // set phase
	    registers.SetOSKMult(Pow2AmpWord(power)); // constant amplitude
	    datap[0] = registers; // parse the registers and store
	    }

//	    char PhaseByteLow = char(Phase2PhaseWord(phase) & 0x00FF);
//	    char PhaseByteHigh = char(Phase2PhaseWord(phase) & 0xFF00 >> 8); // MSB first;

	 writep[0] = DDSIOWriteReg(datap[0]);

	 // Manually write all of the data:
	 // Frequency:
	 writep[0].Words[0] = DDSIOWord(DIP, IOLOAD, 0, 0x04, datap[0].Raw().data[0x04], 0, 1);
	 writep[0].Words[1] = DDSIOWord(DIP, IOLOAD, 0, 0x05, datap[0].Raw().data[0x05], 1, 1);
	 writep[0].Words[2] = DDSIOWord(DIP, IOLOAD, 0, 0x06, datap[0].Raw().data[0x06], 2, 1);
	 writep[0].Words[3] = DDSIOWord(DIP, IOLOAD, 0, 0x07, datap[0].Raw().data[0x07], 3, 1);
	 writep[0].Words[4] = DDSIOWord(DIP, IOLOAD, 0, 0x08, datap[0].Raw().data[0x08], 4, 1);
	 writep[0].Words[5] = DDSIOWord(DIP, IOLOAD, 0, 0x09, datap[0].Raw().data[0x09], 5, 1);
	 // Power:
	 writep[0].Words[6] = DDSIOWord(DIP, IOLOAD, 0, 0x21, datap[0].Raw().data[0x21], 6, 1);
	 writep[0].Words[7] = DDSIOWord(DIP, IOLOAD, 0, 0x22, datap[0].Raw().data[0x22], 7, 1);
	 // Control bits:
	 writep[0].Words[8] = DDSIOWord(DIP, IOLOAD, 0, 0x1d, datap[0].Raw().data[0x1d], 8, 1);
	 writep[0].Words[9] = DDSIOWord(DIP, IOLOAD, 0, 0x1e, datap[0].Raw().data[0x1e], 9, 1);
	 writep[0].Words[10] = DDSIOWord(DIP, IOLOAD, 0, 0x1f, datap[0].Raw().data[0x1f], 10, 1);
	 writep[0].Words[11] = DDSIOWord(DIP, IOLOAD, 0, 0x20, datap[0].Raw().data[0x20], 11, 1);
	 //writep[0].Words[12] = DDSIOWord(DIP, IOLOAD, 0, 0x00, PhaseByteHigh, 12, 1); // set phase
	 //writep[0].Words[13] = DDSIOWord(DIP, IOUPDATE, 0, 0x01, PhaseByteLow, 13, 1);
//	 writep[0].Words[12] = DDSIOWord(DIP, IOLOAD, 0, 0x00, 0, 12, 1); // set phase
//	 writep[0].Words[13] = DDSIOWord(DIP, IOUPDATE, 0, 0x01, 0, 13, 1);
	 writep[0].Words[12] = DDSIOWord(DIP, IOLOAD, 0, 0x00, datap[0].Raw().data[0x00], 12, 1); //write phase
	 writep[0].Words[13] = DDSIOWord(DIP, IOLOAD, 0, 0x01, datap[0].Raw().data[0x01], 13, 1); //write phase
	 writep[0].Words[14] = DDSIOWord(DIP, IOLOAD, 0, 0x1f, 0, 14, 1);
	 writep[0].Words[15] = DDSIOWord(DIP, IOUPDATE, 0, 0x23, 0, 15, 1); // force to write the mode code (since it is zero by default)
	 writep[0].changes = 16;
	 /*
	 if (writep[0].Words[7].RawIO==0){
	 writep[0].Words[7] = DDSIOWord(DIP, IOLOAD, 0, 0x23, 0, 7, 1);}
	 writep[0].Words[8] = DDSIOWord(DIP, IOLOAD, 0, 0x21, datap[0].Raw().data[0x21], 8, 1);
	 writep[0].Words[9] = DDSIOWord(DIP, IOLOAD, 0, 0x22, datap[0].Raw().data[0x22], 9, 1);
	 writep[0].Words[10] = DDSIOWord(DIP, IOLOAD, 0, 0x23, 0, 10, 1);
	 writep[0].Words[11] = DDSIOWord(DIP, IOLOAD, 0, 0x23, 0, 11, 1);
	 writep[0].Words[12] = DDSIOWord(DIP, IOLOAD, 0, 0x23, 0, 12, 1);
	 writep[0].Words[13] = DDSIOWord(DIP, IOLOAD, 0, 0x23, 0, 13, 1);
	 writep[0].Words[14] = DDSIOWord(DIP, IOLOAD, 0, 0x23, 0, 14, 1);
	 writep[0].Words[15] = DDSIOWord(DIP, IOUPDATE, 0, 0x1f, 0, 15, 1); // force to write the mode code (since it is zero by default)

	 writep[0].changes = 16;
	 */
	// What does the code below do?
	for (unsigned int ii = 1; ii < tics; ii++) // loop to generate AD9852Raw data (change amp, freq inside this loop)
	    {
	    writep[ii].Words[0] = DDSIOWord(DIP, IOUPDATE, 0, 0x23, 0, 7, 1); //do nothing
	    writep[ii].changes =1 ;
	    }
	ios = 0;
	for (unsigned int ii = 0; ii < tics; ii++)
	    {
	    ios += writep[ii].changes;
	    }
	// HACK: move wait to first data word
	//writep[0].Words[0].SetMask(0);
	}
    };

class PCORPSE: public Pulse // Corpse sequence, 2015-5-7 power: pi pulse power, time: pi/3 time
    {
public:

    PCORPSE(double length, double freq, double phase, double power) :

    Pulse(1+13*Time2Tics(4*length))
	{      unsigned long ticsPart=Time2Tics(4*length);


	    AD9852Reg registers;
	    //                                    Bits	Function                       Default  Reason for change
	    registers.CtrlReg.OSKEn   = 1; //     5	OSK enable                         0    Enable amplitude control
	    registers.CtrlReg.OSKInt  = 0;
	    registers.CtrlReg.IOUpClk = 0; //     8	IO update clock in/out             0    Turn on!
	    // Set mode to single tone
	    registers.CtrlReg.Mode[0] = 0;
	    registers.CtrlReg.Mode[1] = 0;
	    registers.CtrlReg.Mode[2] = 0; //   9-11	Output operating mode             000 (Single tone)
	    registers.CtrlReg.ClrAcc  = 0; // 2013/9/2, testing uwave coherence
	    //registers.CtrlReg.ClrAcc  = 1; //    14	Clear Accumulators                 0    Reset phase
	    registers.CtrlReg.ClrAcc1 = 0;
	    registers.CtrlReg.PLLMult = REFMULT;
	    registers.UpdateCtrlReg(); //   Must do this each time the control registers change
	    registers.SetFreq1(Hz2FreqWord(freq)); // set frequency
	    double phaseOffset=phase;   // this would be a global phase offset applied to every single pulse defined here
	    registers.SetPhaseAdj1(Phase2PhaseWord(0.0+phaseOffset)); // set phase
	    registers.SetOSKMult(Pow2AmpWord(power)); // constant amplitude
	    datap[0] = registers; // parse the registers and store



	 writep[0] = DDSIOWriteReg(datap[0]);

	 // Manually write all of the data:
	 // Frequency:
	 writep[0].Words[0] = DDSIOWord(DIP, IOLOAD, 0, 0x04, datap[0].Raw().data[0x04], 0, 1);
	 writep[0].Words[1] = DDSIOWord(DIP, IOLOAD, 0, 0x05, datap[0].Raw().data[0x05], 1, 1);
	 writep[0].Words[2] = DDSIOWord(DIP, IOLOAD, 0, 0x06, datap[0].Raw().data[0x06], 2, 1);
	 writep[0].Words[3] = DDSIOWord(DIP, IOLOAD, 0, 0x07, datap[0].Raw().data[0x07], 3, 1);
	 writep[0].Words[4] = DDSIOWord(DIP, IOLOAD, 0, 0x08, datap[0].Raw().data[0x08], 4, 1);
	 writep[0].Words[5] = DDSIOWord(DIP, IOLOAD, 0, 0x09, datap[0].Raw().data[0x09], 5, 1);
	 // Power:
	 writep[0].Words[6] = DDSIOWord(DIP, IOLOAD, 0, 0x21, datap[0].Raw().data[0x21], 6, 1);
	 writep[0].Words[7] = DDSIOWord(DIP, IOLOAD, 0, 0x22, datap[0].Raw().data[0x22], 7, 1);
	 // Control bits:
	 writep[0].Words[8] = DDSIOWord(DIP, IOLOAD, 0, 0x1d, datap[0].Raw().data[0x1d], 8, 1);
	 writep[0].Words[9] = DDSIOWord(DIP, IOLOAD, 0, 0x1e, datap[0].Raw().data[0x1e], 9, 1);
	 writep[0].Words[10] = DDSIOWord(DIP, IOLOAD, 0, 0x1f, datap[0].Raw().data[0x1f], 10, 1);
	 writep[0].Words[11] = DDSIOWord(DIP, IOLOAD, 0, 0x20, datap[0].Raw().data[0x20], 11, 1);

	 writep[0].Words[12] = DDSIOWord(DIP, IOLOAD, 0, 0x00, datap[0].Raw().data[0x00], 12, 1); //write phase
	 writep[0].Words[13] = DDSIOWord(DIP, IOLOAD, 0, 0x01, datap[0].Raw().data[0x01], 13, 1); //write phase
	 writep[0].Words[14] = DDSIOWord(DIP, IOLOAD, 0, 0x1f, 0, 14, 1);
	 writep[0].Words[15] = DDSIOWord(DIP, IOUPDATE, 0, 0x23, 0, 15, 1); // force to write the mode code (since it is zero by default)
	 writep[0].changes = 16;


	// first pulse: 7/3 pi around x
	for (unsigned int ii = 1; ii <7*ticsPart+1; ii++) //
	    {
	    writep[ii].Words[0] = DDSIOWord(DIP, IOLOAD, 0, 0x23, 0, 0, 1);
	    writep[ii].Words[1] = DDSIOWord(DIP, IOUPDATE, 0, 0x23, 0, 1, 1); //do nothing
	    writep[ii].changes = 2;
	    }

	// second pulse: 5/3 pi around -x
	for (unsigned int ii = 7*ticsPart+1; ii < 12*ticsPart+1; ii++)
	    {

	    registers.SetPhaseAdj1(Phase2PhaseWord(1.0+phaseOffset)); // set phase
	    registers.Time = ii;

	    datap[ii] = registers; // parse the registers and store

	    if(ii==7*ticsPart+1){
	    writep[ii].Words[0] = DDSIOWord(DIP, IOLOAD, 0, 0x00, datap[ii].Raw().data[0x00], 0, 1); //write phase
	    writep[ii].Words[1] = DDSIOWord(DIP, IOUPDATE, 0, 0x01, datap[ii].Raw().data[0x01], 1, 1); //write phase
	    }
	    else{
	    writep[ii].Words[0] = DDSIOWord(DIP, IOLOAD, 0, 0x23, 0, 0, 1);
	    writep[ii].Words[1] = DDSIOWord(DIP, IOUPDATE, 0, 0x23, 0, 1, 1); //do nothing
	    }
	    writep[ii].changes = 2;
	    }

	// third pulse: 1/3 pi around x
	for (unsigned int ii = 12*ticsPart+1; ii < 13*ticsPart+1; ii++)
	    {

	    registers.SetPhaseAdj1(Phase2PhaseWord(phaseOffset)); // set phase
	    registers.Time = ii;

	    datap[ii] = registers; // parse the registers and store

	    if(ii==12*ticsPart+1){
	    writep[ii].Words[0] = DDSIOWord(DIP, IOLOAD, 0, 0x00, datap[ii].Raw().data[0x00], 0, 1); //write phase
	    writep[ii].Words[1] = DDSIOWord(DIP, IOUPDATE, 0, 0x01, datap[ii].Raw().data[0x01], 1, 1); //write phase
	    }
	    else{
	    writep[ii].Words[0] = DDSIOWord(DIP, IOLOAD, 0, 0x23, 0, 0, 1);
	    writep[ii].Words[1] = DDSIOWord(DIP, IOUPDATE, 0, 0x23, 0, 1, 1); //do nothing
	    }
	    writep[ii].changes = 2;
	    }




	ios = 0;
	for (unsigned int ii = 0; ii < tics; ii++)
	    {
	    ios += writep[ii].changes;
	    }

	}
    };


class PBB1: public Pulse // BB1 protocol square pulse, 2015-4-27, input pulse parameters are for a single pi/2 pulse
    {
public:

    PBB1(double length, double freq, double phase, double power) :

    Pulse(1+10*Time2Tics(4*length))
	{      unsigned long ticsPart=Time2Tics(4*length);


	    AD9852Reg registers;
	    //                                    Bits	Function                       Default  Reason for change
	    registers.CtrlReg.OSKEn   = 1; //     5	OSK enable                         0    Enable amplitude control
	    registers.CtrlReg.OSKInt  = 0;
	    registers.CtrlReg.IOUpClk = 0; //     8	IO update clock in/out             0    Turn on!
	    // Set mode to single tone
	    registers.CtrlReg.Mode[0] = 0;
	    registers.CtrlReg.Mode[1] = 0;
	    registers.CtrlReg.Mode[2] = 0; //   9-11	Output operating mode             000 (Single tone)
	    registers.CtrlReg.ClrAcc  = 0; // 2013/9/2, testing uwave coherence
	    //registers.CtrlReg.ClrAcc  = 1; //    14	Clear Accumulators                 0    Reset phase
	    registers.CtrlReg.ClrAcc1 = 0;
	    registers.CtrlReg.PLLMult = REFMULT;
	    registers.UpdateCtrlReg(); //   Must do this each time the control registers change
	    registers.SetFreq1(Hz2FreqWord(freq)); // set frequency
	    double phaseOffset=phase;   // this would be a global phase offset applied to every single pulse defined here
	    registers.SetPhaseAdj1(Phase2PhaseWord(0.0+phaseOffset)); // set phase
	    registers.SetOSKMult(Pow2AmpWord(power)); // constant amplitude
	    datap[0] = registers; // parse the registers and store



	 writep[0] = DDSIOWriteReg(datap[0]);

	 // Manually write all of the data:
	 // Frequency:
	 writep[0].Words[0] = DDSIOWord(DIP, IOLOAD, 0, 0x04, datap[0].Raw().data[0x04], 0, 1);
	 writep[0].Words[1] = DDSIOWord(DIP, IOLOAD, 0, 0x05, datap[0].Raw().data[0x05], 1, 1);
	 writep[0].Words[2] = DDSIOWord(DIP, IOLOAD, 0, 0x06, datap[0].Raw().data[0x06], 2, 1);
	 writep[0].Words[3] = DDSIOWord(DIP, IOLOAD, 0, 0x07, datap[0].Raw().data[0x07], 3, 1);
	 writep[0].Words[4] = DDSIOWord(DIP, IOLOAD, 0, 0x08, datap[0].Raw().data[0x08], 4, 1);
	 writep[0].Words[5] = DDSIOWord(DIP, IOLOAD, 0, 0x09, datap[0].Raw().data[0x09], 5, 1);
	 // Power:
	 writep[0].Words[6] = DDSIOWord(DIP, IOLOAD, 0, 0x21, datap[0].Raw().data[0x21], 6, 1);
	 writep[0].Words[7] = DDSIOWord(DIP, IOLOAD, 0, 0x22, datap[0].Raw().data[0x22], 7, 1);
	 // Control bits:
	 writep[0].Words[8] = DDSIOWord(DIP, IOLOAD, 0, 0x1d, datap[0].Raw().data[0x1d], 8, 1);
	 writep[0].Words[9] = DDSIOWord(DIP, IOLOAD, 0, 0x1e, datap[0].Raw().data[0x1e], 9, 1);
	 writep[0].Words[10] = DDSIOWord(DIP, IOLOAD, 0, 0x1f, datap[0].Raw().data[0x1f], 10, 1);
	 writep[0].Words[11] = DDSIOWord(DIP, IOLOAD, 0, 0x20, datap[0].Raw().data[0x20], 11, 1);

	 writep[0].Words[12] = DDSIOWord(DIP, IOLOAD, 0, 0x00, datap[0].Raw().data[0x00], 12, 1); //write phase
	 writep[0].Words[13] = DDSIOWord(DIP, IOLOAD, 0, 0x01, datap[0].Raw().data[0x01], 13, 1); //write phase
	 writep[0].Words[14] = DDSIOWord(DIP, IOLOAD, 0, 0x1f, 0, 14, 1);
	 writep[0].Words[15] = DDSIOWord(DIP, IOUPDATE, 0, 0x23, 0, 15, 1); // force to write the mode code (since it is zero by default)
	 writep[0].changes = 16;


	// first pulse: pi/2 around 0
	for (unsigned int ii = 1; ii <ticsPart+1; ii++) //
	    {
	    writep[ii].Words[0] = DDSIOWord(DIP, IOLOAD, 0, 0x23, 0, 0, 1);
	    writep[ii].Words[1] = DDSIOWord(DIP, IOUPDATE, 0, 0x23, 0, 1, 1); //do nothing
	    writep[ii].changes = 2;
	    }

	// second pulse: pi around phi_1
	for (unsigned int ii = ticsPart+1; ii < 3*ticsPart+1; ii++)
	    {

	    registers.SetPhaseAdj1(Phase2PhaseWord(PHI1/PI+phaseOffset)); // set phase
	    registers.Time = ii;

	    datap[ii] = registers; // parse the registers and store

	    if(ii==ticsPart+1){
	    writep[ii].Words[0] = DDSIOWord(DIP, IOLOAD, 0, 0x00, datap[ii].Raw().data[0x00], 0, 1); //write phase
	    writep[ii].Words[1] = DDSIOWord(DIP, IOUPDATE, 0, 0x01, datap[ii].Raw().data[0x01], 1, 1); //write phase
	    }
	    else{
	    writep[ii].Words[0] = DDSIOWord(DIP, IOLOAD, 0, 0x23, 0, 0, 1);
	    writep[ii].Words[1] = DDSIOWord(DIP, IOUPDATE, 0, 0x23, 0, 1, 1); //do nothing
	    }
	    writep[ii].changes = 2;
	    }

	// third pulse: 2*pi around 3*phi_1
	for (unsigned int ii = 3*ticsPart+1; ii < 7*ticsPart+1; ii++)
	    {

	    registers.SetPhaseAdj1(Phase2PhaseWord(3*PHI1/PI+phaseOffset)); // set phase
	    registers.Time = ii;

	    datap[ii] = registers; // parse the registers and store

	    if(ii==3*ticsPart+1){
	    writep[ii].Words[0] = DDSIOWord(DIP, IOLOAD, 0, 0x00, datap[ii].Raw().data[0x00], 0, 1); //write phase
	    writep[ii].Words[1] = DDSIOWord(DIP, IOUPDATE, 0, 0x01, datap[ii].Raw().data[0x01], 1, 1); //write phase
	    }
	    else{
	    writep[ii].Words[0] = DDSIOWord(DIP, IOLOAD, 0, 0x23, 0, 0, 1);
	    writep[ii].Words[1] = DDSIOWord(DIP, IOUPDATE, 0, 0x23, 0, 1, 1); //do nothing
	    }
	    writep[ii].changes = 2;
	    }

	// fourth pulse: pi around phi_1
	for (unsigned int ii = 7*ticsPart+1; ii < 9*ticsPart+1; ii++)
	    {

	    registers.SetPhaseAdj1(Phase2PhaseWord(PHI1/PI+phaseOffset)); // set phase
	    registers.Time = ii;

	    datap[ii] = registers; // parse the registers and store

	    if(ii==7*ticsPart+1){
	    writep[ii].Words[0] = DDSIOWord(DIP, IOLOAD, 0, 0x00, datap[ii].Raw().data[0x00], 0, 1); //write phase
	    writep[ii].Words[1] = DDSIOWord(DIP, IOUPDATE, 0, 0x01, datap[ii].Raw().data[0x01], 1, 1); //write phase
	    }
	    else{
	    writep[ii].Words[0] = DDSIOWord(DIP, IOLOAD, 0, 0x23, 0, 0, 1);
	    writep[ii].Words[1] = DDSIOWord(DIP, IOUPDATE, 0, 0x23, 0, 1, 1); //do nothing
	    }
	    writep[ii].changes = 2;
	    }

	// fifth pulse: pi/2 around 0
	for (unsigned int ii = 9*ticsPart+1; ii < 10*ticsPart+1; ii++)
	    {

	    registers.SetPhaseAdj1(Phase2PhaseWord(0+phaseOffset)); // set phase
	    registers.Time = ii;

	    datap[ii] = registers; // parse the registers and store

	    if(ii==9*ticsPart+1){
	    writep[ii].Words[0] = DDSIOWord(DIP, IOLOAD, 0, 0x00, datap[ii].Raw().data[0x00], 0, 1); //write phase
	    writep[ii].Words[1] = DDSIOWord(DIP, IOUPDATE, 0, 0x01, datap[ii].Raw().data[0x01], 1, 1); //write phase
	    }
	    else{
	    writep[ii].Words[0] = DDSIOWord(DIP, IOLOAD, 0, 0x23, 0, 0, 1);
	    writep[ii].Words[1] = DDSIOWord(DIP, IOUPDATE, 0, 0x23, 0, 1, 1); //do nothing
	    }
	    writep[ii].changes = 2;
	    }


	ios = 0;
	for (unsigned int ii = 0; ii < tics; ii++)
	    {
	    ios += writep[ii].changes;
	    }

	}
    };


class PBB12: public Pulse // BB1 protocol,Blackman pulse 2015-4-28, input pulse parameters are for a single pi/2 pulse
    {
public:

    PBB12(double length, double freq, double phase, double powmax) :

    Pulse(1+10*Time2Tics(4*length))
	{      unsigned long ticsPart=Time2Tics(4*length);


	    AD9852Reg registers;
	    //                                    Bits	Function                       Default  Reason for change
	    registers.CtrlReg.OSKEn   = 1; //     5	OSK enable                         0    Enable amplitude control
	    registers.CtrlReg.OSKInt  = 0;
	    registers.CtrlReg.IOUpClk = 0; //     8	IO update clock in/out             0    Turn on!
	    // Set mode to single tone
	    registers.CtrlReg.Mode[0] = 0;
	    registers.CtrlReg.Mode[1] = 0;
	    registers.CtrlReg.Mode[2] = 0; //   9-11	Output operating mode             000 (Single tone)
	    registers.CtrlReg.ClrAcc  = 0; // 2013/9/2, testing uwave coherence
	    //registers.CtrlReg.ClrAcc  = 1; //    14	Clear Accumulators                 0    Reset phase
	    registers.CtrlReg.ClrAcc1 = 0;
	    registers.CtrlReg.PLLMult = REFMULT;
	    registers.UpdateCtrlReg(); //   Must do this each time the control registers change
	    registers.SetFreq1(Hz2FreqWord(freq)); // set frequency
	    double phaseOffset=phase;   // this would be a global phase offset applied to every single pulse defined here
	    registers.SetPhaseAdj1(Phase2PhaseWord(0.0+phaseOffset)); // set phase
	    //registers.SetOSKMult(Pow2AmpWord(powmax)); // constant amplitude
	    datap[0] = registers; // parse the registers and store



	 writep[0] = DDSIOWriteReg(datap[0]);

	 // Manually write all of the data:
	 // Frequency:
	 writep[0].Words[0] = DDSIOWord(DIP, IOLOAD, 0, 0x04, datap[0].Raw().data[0x04], 0, 1);
	 writep[0].Words[1] = DDSIOWord(DIP, IOLOAD, 0, 0x05, datap[0].Raw().data[0x05], 1, 1);
	 writep[0].Words[2] = DDSIOWord(DIP, IOLOAD, 0, 0x06, datap[0].Raw().data[0x06], 2, 1);
	 writep[0].Words[3] = DDSIOWord(DIP, IOLOAD, 0, 0x07, datap[0].Raw().data[0x07], 3, 1);
	 writep[0].Words[4] = DDSIOWord(DIP, IOLOAD, 0, 0x08, datap[0].Raw().data[0x08], 4, 1);
	 writep[0].Words[5] = DDSIOWord(DIP, IOLOAD, 0, 0x09, datap[0].Raw().data[0x09], 5, 1);
	 // Power:
	 writep[0].Words[6] = DDSIOWord(DIP, IOLOAD, 0, 0x21, datap[0].Raw().data[0x21], 6, 1);
	 writep[0].Words[7] = DDSIOWord(DIP, IOLOAD, 0, 0x22, datap[0].Raw().data[0x22], 7, 1);
	 // Control bits:
	 writep[0].Words[8] = DDSIOWord(DIP, IOLOAD, 0, 0x1d, datap[0].Raw().data[0x1d], 8, 1);
	 writep[0].Words[9] = DDSIOWord(DIP, IOLOAD, 0, 0x1e, datap[0].Raw().data[0x1e], 9, 1);
	 writep[0].Words[10] = DDSIOWord(DIP, IOLOAD, 0, 0x1f, datap[0].Raw().data[0x1f], 10, 1);
	 writep[0].Words[11] = DDSIOWord(DIP, IOLOAD, 0, 0x20, datap[0].Raw().data[0x20], 11, 1);

	 writep[0].Words[12] = DDSIOWord(DIP, IOLOAD, 0, 0x00, datap[0].Raw().data[0x00], 12, 1); //write phase
	 writep[0].Words[13] = DDSIOWord(DIP, IOLOAD, 0, 0x01, datap[0].Raw().data[0x01], 13, 1); //write phase
	 writep[0].Words[14] = DDSIOWord(DIP, IOLOAD, 0, 0x1f, 0, 14, 1);
	 writep[0].Words[15] = DDSIOWord(DIP, IOUPDATE, 0, 0x23, 0, 15, 1); // force to write the mode code (since it is zero by default)
	 writep[0].changes = 16;


	// first pulse: pi/2 around 0
	for (unsigned int ii = 1; ii <ticsPart+1; ii++) //
	    {
	    double power;

	    	    power = powmax * pow(0.42 - 0.5 * cos(2.0 * PI * ii
	    		    / ((double) ticsPart - 1)) + 0.08 * cos(4.0 * PI * ii
	    		    / ((double) ticsPart - 1)),2); // power is amplitude squared

	    	registers.SetOSKMult(Pow2AmpWord(power)); // set amplitude
	    	registers.SetPhaseAdj1(Phase2PhaseWord(PHI1/PI+phaseOffset)); // set phase
	        registers.Time = ii;

	        datap[ii] = registers; // parse the registers and store

	    if(ii==1){
	    writep[ii].Words[0] = DDSIOWord(DIP, IOLOAD, 0, 0x23, 0, 0, 1);
	    writep[ii].Words[1] = DDSIOWord(DIP, IOUPDATE, 0, 0x23, 0, 1, 1); //match timing
	    writep[ii].Words[2] = DDSIOWord(DIP, IOLOAD, 0, 0x21,datap[ii].Raw().data[0x21], 2, 1);
	    writep[ii].Words[3] = DDSIOWord(DIP, IOUPDATE, 0, 0x22,datap[ii].Raw().data[0x22], 3, 1);
	    writep[ii].changes = 4;
	    }
	    else{
	    writep[ii].Words[0] = DDSIOWord(DIP, IOLOAD, 0, 0x21,datap[ii].Raw().data[0x21], 0, 1);
	    writep[ii].Words[1] = DDSIOWord(DIP, IOUPDATE, 0, 0x22,datap[ii].Raw().data[0x22], 1, 1);
	    writep[ii].changes = 2;
	    }


	    }

	// second pulse: pi around phi_1
	for (unsigned int ii = ticsPart+1; ii < 3*ticsPart+1; ii++)
	    {
	    double power;

	    	    	    power = powmax * pow(0.42 - 0.5 * cos(2.0 * PI * ii
	    	    		    / ((double) ticsPart - 1)) + 0.08 * cos(4.0 * PI * ii
	    	    		    / ((double) ticsPart - 1)),2); // power is amplitude squared

	    registers.SetOSKMult(Pow2AmpWord(power)); // set amplitude
	    registers.SetPhaseAdj1(Phase2PhaseWord(PHI1/PI+phaseOffset)); // set phase
	    registers.Time = ii;

	    datap[ii] = registers; // parse the registers and store

	    if(ii==ticsPart+1){
	    writep[ii].Words[0] = DDSIOWord(DIP, IOLOAD, 0, 0x00, datap[ii].Raw().data[0x00], 0, 1); //write phase
	    writep[ii].Words[1] = DDSIOWord(DIP, IOUPDATE, 0, 0x01, datap[ii].Raw().data[0x01], 1, 1); //write phase
	    writep[ii].Words[2] = DDSIOWord(DIP, IOLOAD, 0, 0x21,datap[ii].Raw().data[0x21], 2, 1);
	    writep[ii].Words[3] = DDSIOWord(DIP, IOUPDATE, 0, 0x22,datap[ii].Raw().data[0x22], 3, 1);
	    writep[ii].changes = 4;
	    }
	    else{
	    writep[ii].Words[0] = DDSIOWord(DIP, IOLOAD, 0, 0x21,datap[ii].Raw().data[0x21], 0, 1);
	    writep[ii].Words[1] = DDSIOWord(DIP, IOUPDATE, 0, 0x22,datap[ii].Raw().data[0x22], 1, 1);
	    writep[ii].changes = 2;
	    }
	    }

	// third pulse: 2*pi around 3*phi_1
	for (unsigned int ii = 3*ticsPart+1; ii < 7*ticsPart+1; ii++)
	    {
	    double power;

	    	    	    power = powmax * pow(0.42 - 0.5 * cos(2.0 * PI * ii
	    	    		    / ((double) ticsPart - 1)) + 0.08 * cos(4.0 * PI * ii
	    	    		    / ((double) ticsPart - 1)),2); // power is amplitude squared

	    registers.SetOSKMult(Pow2AmpWord(power)); // set amplitude
	    registers.SetPhaseAdj1(Phase2PhaseWord(3*PHI1/PI+phaseOffset)); // set phase
	    registers.Time = ii;

	    datap[ii] = registers; // parse the registers and store

	    if(ii==3*ticsPart+1){
	    writep[ii].Words[0] = DDSIOWord(DIP, IOLOAD, 0, 0x00, datap[ii].Raw().data[0x00], 0, 1); //write phase
	    writep[ii].Words[1] = DDSIOWord(DIP, IOUPDATE, 0, 0x01, datap[ii].Raw().data[0x01], 1, 1); //write phase
	    writep[ii].Words[2] = DDSIOWord(DIP, IOLOAD, 0, 0x21,datap[ii].Raw().data[0x21], 2, 1);
	    writep[ii].Words[3] = DDSIOWord(DIP, IOUPDATE, 0, 0x22,datap[ii].Raw().data[0x22], 3, 1);
	    writep[ii].changes = 4;
	    }
	    else{
	    writep[ii].Words[0] = DDSIOWord(DIP, IOLOAD, 0, 0x21,datap[ii].Raw().data[0x21], 0, 1);
	    writep[ii].Words[1] = DDSIOWord(DIP, IOUPDATE, 0, 0x22,datap[ii].Raw().data[0x22], 1, 1);
	    writep[ii].changes = 2;
	    }
	    }

	// fourth pulse: pi around phi_1
	for (unsigned int ii = 7*ticsPart+1; ii < 9*ticsPart+1; ii++)
	    {
	    double power;

	    	    	    power = powmax * pow(0.42 - 0.5 * cos(2.0 * PI * ii
	    	    		    / ((double) ticsPart - 1)) + 0.08 * cos(4.0 * PI * ii
	    	    		    / ((double) ticsPart - 1)),2); // power is amplitude squared

	    registers.SetOSKMult(Pow2AmpWord(power)); // set amplitude
	    registers.SetPhaseAdj1(Phase2PhaseWord(PHI1/PI+phaseOffset)); // set phase
	    registers.Time = ii;

	    datap[ii] = registers; // parse the registers and store

	    if(ii==7*ticsPart+1){
	    writep[ii].Words[0] = DDSIOWord(DIP, IOLOAD, 0, 0x00, datap[ii].Raw().data[0x00], 0, 1); //write phase
	    writep[ii].Words[1] = DDSIOWord(DIP, IOUPDATE, 0, 0x01, datap[ii].Raw().data[0x01], 1, 1); //write phase
	    writep[ii].Words[2] = DDSIOWord(DIP, IOLOAD, 0, 0x21,datap[ii].Raw().data[0x21], 2, 1);
	    writep[ii].Words[3] = DDSIOWord(DIP, IOUPDATE, 0, 0x22,datap[ii].Raw().data[0x22], 3, 1);
	    writep[ii].changes = 4;
	    }
	    else{
	    writep[ii].Words[0] = DDSIOWord(DIP, IOLOAD, 0, 0x21,datap[ii].Raw().data[0x21], 0, 1);
	    writep[ii].Words[1] = DDSIOWord(DIP, IOUPDATE, 0, 0x22,datap[ii].Raw().data[0x22], 1, 1);
	    writep[ii].changes = 2;
	    }
	    }

	// fifth pulse: pi/2 around 0
	for (unsigned int ii = 9*ticsPart+1; ii < 10*ticsPart+1; ii++)
	    {
	    double power;

	    	    	    power = powmax * pow(0.42 - 0.5 * cos(2.0 * PI * ii
	    	    		    / ((double) ticsPart - 1)) + 0.08 * cos(4.0 * PI * ii
	    	    		    / ((double) ticsPart - 1)),2); // power is amplitude squared

	    registers.SetOSKMult(Pow2AmpWord(power)); // set amplitude
	    registers.SetPhaseAdj1(Phase2PhaseWord(0+phaseOffset)); // set phase
	    registers.Time = ii;

	    datap[ii] = registers; // parse the registers and store

	    if(ii==9*ticsPart+1){
	    writep[ii].Words[0] = DDSIOWord(DIP, IOLOAD, 0, 0x00, datap[ii].Raw().data[0x00], 0, 1); //write phase
	    writep[ii].Words[1] = DDSIOWord(DIP, IOUPDATE, 0, 0x01, datap[ii].Raw().data[0x01], 1, 1); //write phase
	    writep[ii].Words[2] = DDSIOWord(DIP, IOLOAD, 0, 0x21,datap[ii].Raw().data[0x21], 2, 1);
	    writep[ii].Words[3] = DDSIOWord(DIP, IOUPDATE, 0, 0x22,datap[ii].Raw().data[0x22], 3, 1);
	    writep[ii].changes = 4;
	    }
	    else{
	    writep[ii].Words[0] = DDSIOWord(DIP, IOLOAD, 0, 0x21,datap[ii].Raw().data[0x21], 0, 1);
	    writep[ii].Words[1] = DDSIOWord(DIP, IOUPDATE, 0, 0x22,datap[ii].Raw().data[0x22], 1, 1);
	    writep[ii].changes = 2;
	    }
	    }


	ios = 0;
	for (unsigned int ii = 0; ii < tics; ii++)
	    {
	    ios += writep[ii].changes;
	    }

	}
    };


class PBlackman: public Pulse // Blackman "pulse"， sweep amp only.
    {
public:
    PBlackman(double length, double freq, double phase, double powmax) :
        // phase is in units of pi (e.g. phase = 1 -> pi phase shift)
	//Pulse(1+4*Time2Tics(length))
	Pulse(1+Time2Tics(4*length))  //2014-5-7
	    {
	AD9852Reg registers;
	// Set control register values (only those that vary from default values)
	//                                    Bits	Function                       Default  Reason for change
	registers.CtrlReg.OSKEn    = 1; //     5	OSK enable                         0    Enable amplitude control
	registers.CtrlReg.OSKInt   = 0;
	registers.CtrlReg.IOUpClk  = 0; //     8	IO update clock in/out             0    Turn on!
	// Set mode to single tone
	registers.CtrlReg.Mode[0]  = 0;
	registers.CtrlReg.Mode[1]  = 0;
	registers.CtrlReg.Mode[2]  = 0; //   9-11	Output operating mode             000   single tone mode
	registers.CtrlReg.PLLMult  = REFMULT;
	registers.CtrlReg.PLLRange = 1;
	registers.CtrlReg.ClrAcc1 = 0; // Don't reset accumulators
	registers.CtrlReg.ClrAcc = 0; // Don't reset accumulators
	registers.UpdateCtrlReg(); //   Must do this each time the control registers change

	registers.SetFreq1(Hz2FreqWord(freq)); // initial frequency
	registers.SetPhaseAdj1(Phase2PhaseWord(phase)); // Set phase

	cout<<"phase is "<<phase<<"pi"<<endl;
	datap[0] = registers;
	writep[0] = DDSIOWriteReg(datap[0]);

		 // Manually write all of the data:
		 // Frequency:
		 writep[0].Words[0] = DDSIOWord(DIP, IOLOAD, 0, 0x04, datap[0].Raw().data[0x04], 0, 1);
		 writep[0].Words[1] = DDSIOWord(DIP, IOLOAD, 0, 0x05, datap[0].Raw().data[0x05], 1, 1);
		 writep[0].Words[2] = DDSIOWord(DIP, IOLOAD, 0, 0x06, datap[0].Raw().data[0x06], 2, 1);
		 writep[0].Words[3] = DDSIOWord(DIP, IOLOAD, 0, 0x07, datap[0].Raw().data[0x07], 3, 1);
		 writep[0].Words[4] = DDSIOWord(DIP, IOLOAD, 0, 0x08, datap[0].Raw().data[0x08], 4, 1);
		 writep[0].Words[5] = DDSIOWord(DIP, IOLOAD, 0, 0x09, datap[0].Raw().data[0x09], 5, 1);
		 // Power:
		 writep[0].Words[6] = DDSIOWord(DIP, IOLOAD, 0, 0x21, datap[0].Raw().data[0x21], 6, 1);
		 writep[0].Words[7] = DDSIOWord(DIP, IOLOAD, 0, 0x22, datap[0].Raw().data[0x22], 7, 1);
		 // Control bits:
		 writep[0].Words[8] = DDSIOWord(DIP, IOLOAD, 0, 0x1d, datap[0].Raw().data[0x1d], 8, 1);
		 writep[0].Words[9] = DDSIOWord(DIP, IOLOAD, 0, 0x1e, datap[0].Raw().data[0x1e], 9, 1);
		 writep[0].Words[10] = DDSIOWord(DIP, IOLOAD, 0, 0x1f, datap[0].Raw().data[0x1f], 10, 1);
		 writep[0].Words[11] = DDSIOWord(DIP, IOLOAD, 0, 0x20, datap[0].Raw().data[0x20], 11, 1);
		 writep[0].Words[12] = DDSIOWord(DIP, IOLOAD, 0, 0x00, datap[0].Raw().data[0x00], 12, 1); //write phase
		 writep[0].Words[13] = DDSIOWord(DIP, IOLOAD, 0, 0x01, datap[0].Raw().data[0x01], 13, 1); //write phase
		 //writep[0].Words[12] = DDSIOWord(DIP, IOLOAD, 0, 0x23, 0, 12, 1);
		 //writep[0].Words[13] = DDSIOWord(DIP, IOLOAD, 0, 0x23, 0, 13, 1);
		 writep[0].Words[14] = DDSIOWord(DIP, IOLOAD, 0, 0x23, 0, 14, 1);
		 //writep[0].Words[14] = DDSIOWord(DIP, IOLOAD, 0, 0x1f, 0, 14, 1);
		 writep[0].Words[15] = DDSIOWord(DIP, IOUPDATE, 0, 0x23, 0, 15, 1); // force to write the mode code (since it is zero by default)
		 writep[0].changes = 16;


	for (unsigned int ii = 1; ii < tics; ii++) // loop to generate AD9852Raw data starting from second tic (change amp, freq inside this loop)
	    {
	    double power;
	    //Pulse frequency shape follows:
	    //registers.SetFreq1(Hz2FreqWord(freq)); // set frequency
	    // Pulse amplitude shape follows:
	    power = powmax * pow(0.42 - 0.5 * cos(2.0 * PI * ii
		    / ((double) tics - 1)) + 0.08 * cos(4.0 * PI * ii
		    / ((double) tics - 1)),2); // power is amplitude squared

	   // power=1.0; //HACK, 2013090 to mimic square pulse

	    //  amp=Pow2Volts(maxpow)*ii/(double)tics;  // Triangle Pulse (for debug)
	    registers.SetOSKMult(Pow2AmpWord(power)); // set amplitude
	    registers.Time = ii;

	    datap[ii] = registers; // parse the registers and store


	    writep[ii].Words[0] = DDSIOWord(DIP, IOLOAD, 0, 0x21,
		    datap[ii].Raw().data[0x21], 0, 1);
	    writep[ii].Words[1] = DDSIOWord(DIP, IOUPDATE, 0, 0x22,
		    datap[ii].Raw().data[0x22], 1, 1);
	    /*writep[ii].Words[2] = DDSIOWord(DIP, IOUPDATE, 0, 0x23,
		    datap[ii].Raw().data[0x23], 2, 1);
	    writep[ii].Words[3] = DDSIOWord(DIP, IOUPDATE, 0, 0x23,
		    datap[ii].Raw().data[0x23], 3, 1);
	    writep[ii].Words[4] = DDSIOWord(DIP, IOUPDATE, 0, 0x23,
		    datap[ii].Raw().data[0x23], 4, 1);
	    writep[ii].Words[5] = DDSIOWord(DIP, IOUPDATE, 0, 0x23,
		    datap[ii].Raw().data[0x23], 5, 1);
	    writep[ii].Words[6] = DDSIOWord(DIP, IOUPDATE, 0, 0x23,
		    datap[ii].Raw().data[0x23], 6, 1);
	    writep[ii].Words[7] = DDSIOWord(DIP, IOUPDATE, 0, 0x23,
		    datap[ii].Raw().data[0x23], 7, 1);
*/
	    //writep[ii] = DDSIOWriteReg(datap[ii], datap[ii-1]); // only record changes
	    // HACK:
	    writep[ii].changes = 2; // assume that both amplitude registers change, to keep timing sane
	    }
	ios = 0;
	for (unsigned int ii = 0; ii < tics; ii++)
	    {
	    ios += writep[ii].changes;
	    }
	}
    };

class PFollower: public Pulse // Blackman "pulse"， with the same freq as the previous one, but a variable phase
    {
public:
    PFollower(double length, double freq, double phase, double powmax) :
        // phase is in units of pi (e.g. phase = 1 -> pi phase shift)
	Pulse(1+4*Time2Tics(length))
	{
	AD9852Reg registers;
	registers.SetPhaseAdj1(Phase2PhaseWord(phase)); // Set phase
	datap[0] = registers;

	cout<<"phase is "<<phase<<"pi"<<endl;

		 writep[0].Words[0] = DDSIOWord(DIP, IOLOAD, 0, 0x00, datap[0].Raw().data[0x00], 12, 1); //write phase
		 writep[0].Words[1] = DDSIOWord(DIP, IOUPDATE, 0, 0x01, datap[0].Raw().data[0x01], 13, 1); //write phase
		 writep[0].changes = 2;

	for (unsigned int ii = 1; ii < tics; ii++) // loop to generate AD9852Raw data starting from second tic (change amp, freq inside this loop)
	    {
	    double power;
	    //Pulse frequency shape follows:
	    //registers.SetFreq1(Hz2FreqWord(freq)); // set frequency
	    // Pulse amplitude shape follows:
	    power = powmax * pow(0.42 - 0.5 * cos(2.0 * PI * ii
		    / ((double) tics - 1)) + 0.08 * cos(4.0 * PI * ii
		    / ((double) tics - 1)),2); // power is amplitude squared

	   // power=1.0; // check
	    //  amp=Pow2Volts(maxpow)*ii/(double)tics;  // Triangle Pulse (for debug)
	    registers.SetOSKMult(Pow2AmpWord(power)); // set amplitude
	    registers.Time = ii;

	    datap[ii] = registers; // parse the registers and store


	    writep[ii].Words[0] = DDSIOWord(DIP, IOLOAD, 0, 0x21,
		    datap[ii].Raw().data[0x21], 0, 1);
	    writep[ii].Words[1] = DDSIOWord(DIP, IOUPDATE, 0, 0x22,
		    datap[ii].Raw().data[0x22], 1, 1);
	    writep[ii].changes = 2; // assume that both amplitude registers change, to keep timing sane
	    }

	ios = 0;
	for (unsigned int ii = 0; ii < tics; ii++)
	    {
	    ios += writep[ii].changes;
	    }
	}
    };

class PAdiabatic: public Pulse // adiabatic sweeping, scan both amp and freq
    {
public:
    PAdiabatic(double length, double freq, double HSR, double powmax) : //HSR Half frequency Sweeping Range
	Pulse(Time2Tics(length))
	{
	AD9852Reg registers;
	// Set control register values (only those that vary from default values)
	//                                    Bits	Function                       Default  Reason for change
	registers.CtrlReg.OSKEn    = 1; //     5	OSK enable                         0    Enable amplitude control
	registers.CtrlReg.OSKInt   = 0;
	registers.CtrlReg.IOUpClk  = 0; //     8	IO update clock in/out             0    Turn on!
	// Set mode to chirp
	registers.CtrlReg.Mode[0]  = 1;
	registers.CtrlReg.Mode[1]  = 1;
	registers.CtrlReg.Mode[2]  = 0; //   9-11	Output operating mode             000   chirp mode
	registers.CtrlReg.PLLMult  = REFMULT;
	registers.CtrlReg.PLLRange = PLLRANGE;
	//registers.CtrlReg.ClrAcc1 = 1; // reset accumulator
	registers.CtrlReg.ClrAcc = 1;
	registers.UpdateCtrlReg(); //   Must do this each time the control registers change
	// Set data register values (other than freq and amp)
	//registers.SetPhaseAdj1(0);
	//registers.SetPhaseAdj2(0);


	registers.SetFreq1(Hz2FreqWord(freq - HSR)); // Starting frequency
	registers.SetRampClk(RR2Word(1.0 / RAMPRATE));
	datap[0] = registers;
	writep[0] = DDSIOWriteReg(datap[0]);
	// Begin hack to fix missing words 20110221
	writep[0].Words[0] = DDSIOWord(DIP, IOLOAD, 0, 0x04,
	   datap[0].Raw().data[0x04], 0, 1);
	writep[0].Words[1] = DDSIOWord(DIP, IOLOAD, 0, 0x05,
	   datap[0].Raw().data[0x05], 1, 1);
	writep[0].Words[2] = DDSIOWord(DIP, IOLOAD, 0, 0x06,
	   datap[0].Raw().data[0x06], 2, 1);
	writep[0].Words[3] = DDSIOWord(DIP, IOLOAD, 0, 0x07,
	   datap[0].Raw().data[0x07], 3, 1);
	writep[0].Words[4] = DDSIOWord(DIP, IOLOAD, 0, 0x08,
	   datap[0].Raw().data[0x08], 4, 1);
	writep[0].Words[5] = DDSIOWord(DIP, IOLOAD, 0, 0x09,
	   datap[0].Raw().data[0x09], 5, 1);
	writep[0].Words[6] = DDSIOWord(DIP, IOLOAD, 0, 0x1b,
	   datap[0].Raw().data[0x1b], 6, 1);
	writep[0].Words[7] = DDSIOWord(DIP, IOLOAD, 0, 0x1c,
	   datap[0].Raw().data[0x1c], 7, 1);
	writep[0].Words[8] = DDSIOWord(DIP, IOLOAD, 0, 0x1e,
	   datap[0].Raw().data[0x1e], 8, 1);
	writep[0].Words[9] = DDSIOWord(DIP, IOLOAD, 0, 0x1f,
	   datap[0].Raw().data[0x1f], 9, 1);

	 writep[0].Words[10] = DDSIOWord(DIP, IOLOAD, 0, 0x00, 0, 10, 1); //zero phase
	 writep[0].Words[11] = DDSIOWord(DIP, IOUPDATE, 0, 0x01, 0, 11, 1); //zero phase
	 writep[0].Words[12] = DDSIOWord(DIP, IOLOAD, 0, 0x1f, 0x06, 12, 1);
	 writep[0].Words[13] = DDSIOWord(DIP, IOLOAD, 0, 0x23, 0, 13, 1);
	 writep[0].Words[14] = DDSIOWord(DIP, IOLOAD, 0, 0x23, 0, 14, 1);

	writep[0].Words[15] = DDSIOWord(DIP, IOUPDATE, 0, 0x20,
			    datap[0].Raw().data[0x20], 15, 1);

	writep[0].changes = 16;
	// End hack to fix missing words
	//cout << "Debug: AFP init word changes: " << dec << int(writep[0].changes)  << endl;

	//registers.CtrlReg.ClrAcc1 = 0; // reset accumulator, commented at 20110525

	//registers.CtrlReg.ClrAcc = 0;
	//datap[1] = registers;
	//writep[1] = DDSIOWriteReg(datap[1]);
	//writep[1].Words[9] = DDSIOWord(DIP, IOLOAD, 0, 0x1f,0x06   , 9, 1);
	for (unsigned int ii = 1; ii < tics; ii++) // loop to generate AD9852Raw data starting from second tic (change amp, freq inside this loop)
	    {
	    double power;
	    double chirp;
	    double tau;
	    registers.Time = ii;
	    tau = double(ii)/double(tics);

	   //power=powmax*pow(sech(4.852*(2*double(ii)/double(tics)-1)),2);//from the minimum power, pulse length should be around 3ms.
	   //power=powmax*pow(sech(4.852*(2*tau-1)),2);//from the minimum power, pulse length should be around 3ms.
	   //power=powmax*pow(sech(4.852*(2*tau-1)),4);//from the minimum power, pulse length should be around 3ms.
	    power = powmax * pow(sin(PI * (double(ii)-1.0) / (double(tics)-1.0)), 4);
	    registers.SetOSKMult(Pow2AmpWord(power)); // set amplitude

	    //chirp = Freq2(freq - HSR, HSR,  (double(ii)-0.0) / (double(tics)-1.0)) - Freq2(freq
	    //    - HSR, HSR, (double(ii) - 1.0) / (double(tics)-1.0));
	    chirp = Freq1(freq - HSR, HSR,  (double(ii)-0.0) / (double(tics)-1.0)) - Freq1(freq
	    	        - HSR, HSR, (double(ii) - 1.0) / (double(tics)-1.0));
	    //chirp=((double)freq-HSR+ii*2*HSR/tics)-((double)freq-HSR+(ii-1)*2*HSR/tics);  // linear chirp (debug)
	    chirp = (double) chirp / (length / (tics-1) * RAMPRATE); //??? why choose RAMPRATE clock to be that value?

	    registers.SetDeltaFreq(Hz2FreqWord(chirp)); // set frequency
	    datap[ii] = registers; // parse the registers and store

	    writep[ii].Words[0] = DDSIOWord(DIP, IOLOAD, 0, 0x21,
		    datap[ii].Raw().data[0x21], 0, 1);
	    writep[ii].Words[1] = DDSIOWord(DIP, IOLOAD, 0, 0x22,
		    datap[ii].Raw().data[0x22], 1, 1);
	    writep[ii].Words[2] = DDSIOWord(DIP, IOLOAD, 0, 0x10,
		    datap[ii].Raw().data[0x10], 2, 1);
	    writep[ii].Words[3] = DDSIOWord(DIP, IOLOAD, 0, 0x11,
		    datap[ii].Raw().data[0x11], 3, 1);
	    writep[ii].Words[4] = DDSIOWord(DIP, IOLOAD, 0, 0x12,
		    datap[ii].Raw().data[0x12], 4, 1);
	    writep[ii].Words[5] = DDSIOWord(DIP, IOLOAD, 0, 0x13,
		    datap[ii].Raw().data[0x13], 5, 1);
	    writep[ii].Words[6] = DDSIOWord(DIP, IOLOAD, 0, 0x14,
		    datap[ii].Raw().data[0x14], 6, 1);
	    writep[ii].Words[7] = DDSIOWord(DIP, IOUPDATE, 0, 0x15,
		    datap[ii].Raw().data[0x15], 7, 1);

	    //writep[ii] = DDSIOWriteReg(datap[ii], datap[ii-1]); // only record changes

	    writep[ii].changes = 8; // assume that both amplitude registers change, to keep timing sane
	    }
	ios = 0;
	for (unsigned int ii = 0; ii < tics; ii++)
	    {
	    ios += writep[ii].changes;
	    }
	}
    };

class PSquare: public Pulse // Constant "pulse"
    {
public:
    double Frequency;
    double Amplitude;
    PSquare(double length, double freq, double pow) :
	Pulse(Time2Tics(length) + 1)
	{
	// inherited values: tics, datap
	Frequency = freq;
	Amplitude = pow;
	AD9852Reg registers;
	// Set control register values (only those that vary from default values)
	//                                    Bits	Function                       Default  Reason for change
	registers.CtrlReg.OSKEn = 1; //     5	OSK enable                         0    Enable amplitude control
	registers.CtrlReg.IOUpClk = 1; //     8	IO update clock in/out             0    Turn on!
	registers.CtrlReg.Mode[1] = 0;
	registers.CtrlReg.Mode[2] = 0;
	registers.CtrlReg.Mode[3] = 0; //   9-11	Output operating mode             000 (Single tone)
	registers.CtrlReg.ClrAcc = 1; //    14	Clear Accumulators                 0    Reset phase
	registers.UpdateCtrlReg(); //   Must do this each time the control registers change
	// Set data register values (other than freq and amp)
	registers.SetPhaseAdj1(0);
	registers.SetPhaseAdj2(0);
	//registers.SetFreq1  (set this inside the loop)
	registers.SetFreq2(0);
	registers.SetDeltaFreq(0);
	//registers.SetUpdateClk
	//registers.SetRampClk
	//registers.SetOSKMult   (set inside the loop)
	//registers.SetOSKRamp
	//registers.SetCtrlDAC
	registers.SetFreq1(Hz2FreqWord(freq)); // set frequency
	registers.SetOSKMult(Pow2AmpWord(pow)); // set amplitude
	datap[0] = registers; // parse the registers and store
	writep[0] = DDSIOWriteReg(datap[0]);

	for (unsigned int ii = 1; ii < (tics - 1); ii++) // loop to generate AD9852Raw data (change amp, freq inside this loop)
	    {
		writep[ii] = DDSIOWriteReg(); // initialize
		writep[ii].changes = 1;
		writep[ii].Words[0] = DDSIOWord(DIP,IOLATCH,0,0,0,ii,1);  // do nothing
	    }
	//registers.SetFreq1(0);
	registers.SetOSKMult(0); // reset amplitude to zero at end of pulse
	datap[tics - 1] = registers;
	writep[tics -1] = DDSIOWriteReg(datap[tics-1],datap[tics-2]);
	ios = 0;
	for (unsigned int ii=0;ii<tics;ii++)
	    {
		ios += writep[ii].changes;
	    }
	}
    };

/*
class PPi: public PBlackman
    {
public:
    double RabiFreq; // Rabi Frequency at Power (in Hz)
    PPi(double rabi, double freq, double maxpow) :
	PBlackman((0.5 / rabi) / 0.30265, freq, maxpow) // 0.30265 from integrating power of Blackman pulse
	{
	RabiFreq = rabi;
	}
    };

class PPiHalf: public PBlackman
    {
public:
    double RabiFreq; // Rabi Frequency at Power (in Hz)
    PPiHalf(double rabi, double freq, double maxpow) :
	PBlackman((0.25 / rabi) / 0.30265, freq, maxpow) // 0.30265 from integrating power of Blackman pulse
	{
	RabiFreq = rabi;
	}
    };
*/
class PPiHalf: public Pulse // Blackman pulse with pi/2 phase shift
 {
public:
    PPiHalf(double length, double freq, double powmax) :
	Pulse(Time2Tics(length))
	{
	AD9852Reg registers;
	// Set control register values (only those that vary from default values)
	//                                    Bits	Function                       Default  Reason for change
	registers.CtrlReg.OSKEn    = 1; //     5	OSK enable                         0    Enable amplitude control
	registers.CtrlReg.OSKInt   = 0;
	registers.CtrlReg.IOUpClk  = 0; //     8	IO update clock in/out             0    Turn on!
	// Set mode to single tone
	registers.CtrlReg.Mode[0]  = 0;
	registers.CtrlReg.Mode[1]  = 0;
	registers.CtrlReg.Mode[2]  = 0; //   9-11	Output operating mode             000   single tone mode
	registers.CtrlReg.PLLMult  = REFMULT;
	registers.CtrlReg.PLLRange = 1;
	registers.CtrlReg.ClrAcc1 = 0;
	registers.UpdateCtrlReg(); //   Must do this each time the control registers change

	registers.SetFreq1(Hz2FreqWord(freq)); // initial frequency

	datap[0] = registers;
	writep[0] = DDSIOWriteReg(datap[0]);

		 // Manually write all of the data:
		 // Frequency:
		 writep[0].Words[0] = DDSIOWord(DIP, IOLOAD, 0, 0x04, datap[0].Raw().data[0x04], 0, 1);
		 writep[0].Words[1] = DDSIOWord(DIP, IOLOAD, 0, 0x05, datap[0].Raw().data[0x05], 1, 1);
		 writep[0].Words[2] = DDSIOWord(DIP, IOLOAD, 0, 0x06, datap[0].Raw().data[0x06], 2, 1);
		 writep[0].Words[3] = DDSIOWord(DIP, IOLOAD, 0, 0x07, datap[0].Raw().data[0x07], 3, 1);
		 writep[0].Words[4] = DDSIOWord(DIP, IOLOAD, 0, 0x08, datap[0].Raw().data[0x08], 4, 1);
		 writep[0].Words[5] = DDSIOWord(DIP, IOLOAD, 0, 0x09, datap[0].Raw().data[0x09], 5, 1);
		 // Power:
		 writep[0].Words[6] = DDSIOWord(DIP, IOLOAD, 0, 0x21, datap[0].Raw().data[0x21], 6, 1);
		 writep[0].Words[7] = DDSIOWord(DIP, IOLOAD, 0, 0x22, datap[0].Raw().data[0x22], 7, 1);
		 // Control bits:
		 writep[0].Words[8] = DDSIOWord(DIP, IOLOAD, 0, 0x1d, datap[0].Raw().data[0x1d], 8, 1);
		 writep[0].Words[9] = DDSIOWord(DIP, IOLOAD, 0, 0x1e, datap[0].Raw().data[0x1e], 9, 1);
		 writep[0].Words[10] = DDSIOWord(DIP, IOLOAD, 0, 0x1f, datap[0].Raw().data[0x1f], 10, 1);
		 writep[0].Words[11] = DDSIOWord(DIP, IOLOAD, 0, 0x20, datap[0].Raw().data[0x20], 11, 1);
		 writep[0].Words[12] = DDSIOWord(DIP, IOLOAD, 0, 0x00, 0x0F, 12, 1); //pi/2 phase
		 writep[0].Words[13] = DDSIOWord(DIP, IOLOAD, 0, 0x01, 0xFF, 13, 1); //pi/2 phase
		 writep[0].Words[14] = DDSIOWord(DIP, IOLOAD, 0, 0x23, 0, 14, 1);
		 writep[0].Words[15] = DDSIOWord(DIP, IOUPDATE, 0, 0x23, 0, 15, 1); // force to write the mode code (since it is zero by default)
		 writep[0].changes = 16;

	for (unsigned int ii = 1; ii < tics; ii++) // loop to generate AD9852Raw data starting from second tic (change amp, freq inside this loop)
	    {
	    double power;

	    power = powmax * pow(0.42 - 0.5 * cos(2.0 * PI * ii
		    / ((double) tics - 1)) + 0.08 * cos(4.0 * PI * ii
		    / ((double) tics - 1)),2); // power is amplitude squared

	    //  amp=Pow2Volts(maxpow)*ii/(double)tics;  // Triangle Pulse (for debug)
	    registers.SetOSKMult(Pow2AmpWord(power)); // set amplitude
	    registers.Time = ii;

	    datap[ii] = registers; // parse the registers and store

	    writep[ii].Words[0] = DDSIOWord(DIP, IOLOAD, 0, 0x21,
		    datap[ii].Raw().data[0x21], 0, 1);
	    writep[ii].Words[1] = DDSIOWord(DIP, IOLOAD, 0, 0x22,
		    datap[ii].Raw().data[0x22], 1, 1);
	    writep[ii].Words[2] = DDSIOWord(DIP, IOUPDATE, 0, 0x23,
		    datap[ii].Raw().data[0x23], 2, 1);
	    writep[ii].Words[3] = DDSIOWord(DIP, IOUPDATE, 0, 0x23,
		    datap[ii].Raw().data[0x23], 3, 1);
	    writep[ii].Words[4] = DDSIOWord(DIP, IOUPDATE, 0, 0x23,
		    datap[ii].Raw().data[0x23], 4, 1);
	    writep[ii].Words[5] = DDSIOWord(DIP, IOUPDATE, 0, 0x23,
		    datap[ii].Raw().data[0x23], 5, 1);
	    writep[ii].Words[6] = DDSIOWord(DIP, IOUPDATE, 0, 0x23,
		    datap[ii].Raw().data[0x23], 6, 1);
	    writep[ii].Words[7] = DDSIOWord(DIP, IOUPDATE, 0, 0x23,
		    datap[ii].Raw().data[0x23], 7, 1);

	    //writep[ii] = DDSIOWriteReg(datap[ii], datap[ii-1]); // only record changes
	    // HACK:
	    writep[ii].changes = 8; // assume that both amplitude registers change, to keep timing sane
	    }
	ios = 0;
	for (unsigned int ii = 0; ii < tics; ii++)
	    {
	    ios += writep[ii].changes;
	    }
	}
    };

class PPiHalfCW: public Pulse // Constant "pulse"
    {
public:

    PPiHalfCW(double length, double freq, double power) :
	Pulse(Time2Tics(length))
	{
	    {
	    AD9852Reg registers;
	    //                                    Bits	Function                       Default  Reason for change
	    registers.CtrlReg.OSKEn   = 1; //     5	OSK enable                         0    Enable amplitude control
	    registers.CtrlReg.OSKInt  = 0;
	    registers.CtrlReg.IOUpClk = 0; //     8	IO update clock in/out             0    Turn on!
	    // Set mode to single tone
	    registers.CtrlReg.Mode[0] = 0;
	    registers.CtrlReg.Mode[1] = 0;
	    registers.CtrlReg.Mode[2] = 0; //   9-11	Output operating mode             000 (Single tone)
	    registers.CtrlReg.ClrAcc  = 1; //    14	Clear Accumulators                 0    Reset phase
	    registers.CtrlReg.PLLMult = REFMULT;
	    registers.UpdateCtrlReg(); //   Must do this each time the control registers change
	    registers.SetFreq1(Hz2FreqWord(freq)); // set frequency
	    //registers.SetFreq2(Hz2FreqWord(freq)); // set frequency
	    //cout << "OSKMult = " << dec << Pow2AmpWord(power) << endl;
	    registers.SetOSKMult(Pow2AmpWord(power)); // constant amplitude
	    datap[0] = registers; // parse the registers and store
	    }


	 writep[0] = DDSIOWriteReg(datap[0]);

	 // Manually write all of the data:
	 // Frequency:
	 writep[0].Words[0] = DDSIOWord(DIP, IOLOAD, 0, 0x04, datap[0].Raw().data[0x04], 0, 1);
	 writep[0].Words[1] = DDSIOWord(DIP, IOLOAD, 0, 0x05, datap[0].Raw().data[0x05], 1, 1);
	 writep[0].Words[2] = DDSIOWord(DIP, IOLOAD, 0, 0x06, datap[0].Raw().data[0x06], 2, 1);
	 writep[0].Words[3] = DDSIOWord(DIP, IOLOAD, 0, 0x07, datap[0].Raw().data[0x07], 3, 1);
	 writep[0].Words[4] = DDSIOWord(DIP, IOLOAD, 0, 0x08, datap[0].Raw().data[0x08], 4, 1);
	 writep[0].Words[5] = DDSIOWord(DIP, IOLOAD, 0, 0x09, datap[0].Raw().data[0x09], 5, 1);
	 // Power:
	 writep[0].Words[6] = DDSIOWord(DIP, IOLOAD, 0, 0x21, datap[0].Raw().data[0x21], 6, 1);
	 writep[0].Words[7] = DDSIOWord(DIP, IOLOAD, 0, 0x22, datap[0].Raw().data[0x22], 7, 1);
	 // Control bits:
	 writep[0].Words[8] = DDSIOWord(DIP, IOLOAD, 0, 0x1d, datap[0].Raw().data[0x1d], 8, 1);
	 writep[0].Words[9] = DDSIOWord(DIP, IOLOAD, 0, 0x1e, datap[0].Raw().data[0x1e], 9, 1);
	 writep[0].Words[10] = DDSIOWord(DIP, IOLOAD, 0, 0x1f, datap[0].Raw().data[0x1f], 10, 1);
	 writep[0].Words[11] = DDSIOWord(DIP, IOLOAD, 0, 0x20, datap[0].Raw().data[0x20], 11, 1);
	 writep[0].Words[12] = DDSIOWord(DIP, IOLOAD, 0, 0x00, 0x0F, 12, 1); //pi/2 phase
	 writep[0].Words[13] = DDSIOWord(DIP, IOUPDATE, 0, 0x01, 0xFF, 13, 1); //pi/2 phase
	 //writep[0].Words[12] = DDSIOWord(DIP, IOLOAD, 0, 0x23, 0, 12, 1);
	 //writep[0].Words[13] = DDSIOWord(DIP, IOLOAD, 0, 0x23, 0, 13, 1);
	 writep[0].Words[14] = DDSIOWord(DIP, IOLOAD, 0, 0x1f, 0, 14, 1);
	 writep[0].Words[15] = DDSIOWord(DIP, IOUPDATE, 0, 0x23, 0, 15, 1); // force to write the mode code (since it is zero by default)
	 writep[0].changes = 16;
	 /*
	 if (writep[0].Words[7].RawIO==0){
	 writep[0].Words[7] = DDSIOWord(DIP, IOLOAD, 0, 0x23, 0, 7, 1);}
	 writep[0].Words[8] = DDSIOWord(DIP, IOLOAD, 0, 0x21, datap[0].Raw().data[0x21], 8, 1);
	 writep[0].Words[9] = DDSIOWord(DIP, IOLOAD, 0, 0x22, datap[0].Raw().data[0x22], 9, 1);
	 writep[0].Words[10] = DDSIOWord(DIP, IOLOAD, 0, 0x23, 0, 10, 1);
	 writep[0].Words[11] = DDSIOWord(DIP, IOLOAD, 0, 0x23, 0, 11, 1);
	 writep[0].Words[12] = DDSIOWord(DIP, IOLOAD, 0, 0x23, 0, 12, 1);
	 writep[0].Words[13] = DDSIOWord(DIP, IOLOAD, 0, 0x23, 0, 13, 1);
	 writep[0].Words[14] = DDSIOWord(DIP, IOLOAD, 0, 0x23, 0, 14, 1);
	 writep[0].Words[15] = DDSIOWord(DIP, IOUPDATE, 0, 0x1f, 0, 15, 1); // force to write the mode code (since it is zero by default)

	 writep[0].changes = 16;
	 */
	// What does the code below do?
	for (unsigned int ii = 1; ii < tics; ii++) // loop to generate AD9852Raw data (change amp, freq inside this loop)
	    {
	    writep[ii].Words[0] = DDSIOWord(DIP, IOLOAD, 0, 0x23, 0, 0, 1);
	    writep[ii].Words[1] = DDSIOWord(DIP, IOLOAD, 0, 0x23, 0, 1, 1);
	    writep[ii].Words[2] = DDSIOWord(DIP, IOLOAD, 0, 0x23, 0, 2, 1);
	    writep[ii].Words[3] = DDSIOWord(DIP, IOLOAD, 0, 0x23, 0, 3, 1);
	    writep[ii].Words[4] = DDSIOWord(DIP, IOLOAD, 0, 0x23, 0, 4, 1);
	    writep[ii].Words[5] = DDSIOWord(DIP, IOLOAD, 0, 0x23, 0, 5, 1);
	    writep[ii].Words[6] = DDSIOWord(DIP, IOLOAD, 0, 0x23, 0, 6, 1);
	    writep[ii].Words[7] = DDSIOWord(DIP, IOUPDATE, 0, 0x23, 0, 7, 1); //do nothing
	    writep[ii].changes = 8;
	    }
	ios = 0;
	for (unsigned int ii = 0; ii < tics; ii++)
	    {
	    ios += writep[ii].changes;
	    }
	// HACK: move wait to first data word
	//writep[0].Words[0].SetMask(0);
	}
    };

class PStarCW: public Pulse // a composite pi star pulse of CW
    {
public:

    PStarCW(double length, double freq, double power) :
	Pulse(2+3*Time2Tics(length))
	{
	    {
	    AD9852Reg registers;
	    registers.CtrlReg.OSKEn   = 1; //     5	OSK enable                         0    Enable amplitude control
	    registers.CtrlReg.OSKInt  = 0;
	    registers.CtrlReg.IOUpClk = 0; //     8	IO update clock in/out             0    Turn on!
	    registers.CtrlReg.Mode[0] = 0;
	    registers.CtrlReg.Mode[1] = 0;
	    registers.CtrlReg.Mode[2] = 0; //   9-11	Output operating mode             000 (Single tone)
	    registers.CtrlReg.ClrAcc  = 1; //    14	Clear Accumulators                 0    Reset phase
	    registers.CtrlReg.PLLMult = REFMULT;
	    registers.UpdateCtrlReg(); //   Must do this each time the control registers change
	    registers.SetFreq1(Hz2FreqWord(freq)); // set frequency
	    registers.SetOSKMult(Pow2AmpWord(power)); // constant amplitude
	    datap[0] = registers; // parse the registers and store
	    }


	 writep[0] = DDSIOWriteReg(datap[0]);

	 // Manually write all of the data:
	 // Frequency:
	 writep[0].Words[0] = DDSIOWord(DIP, IOLOAD, 0, 0x04, datap[0].Raw().data[0x04], 0, 1);
	 writep[0].Words[1] = DDSIOWord(DIP, IOLOAD, 0, 0x05, datap[0].Raw().data[0x05], 1, 1);
	 writep[0].Words[2] = DDSIOWord(DIP, IOLOAD, 0, 0x06, datap[0].Raw().data[0x06], 2, 1);
	 writep[0].Words[3] = DDSIOWord(DIP, IOLOAD, 0, 0x07, datap[0].Raw().data[0x07], 3, 1);
	 writep[0].Words[4] = DDSIOWord(DIP, IOLOAD, 0, 0x08, datap[0].Raw().data[0x08], 4, 1);
	 writep[0].Words[5] = DDSIOWord(DIP, IOLOAD, 0, 0x09, datap[0].Raw().data[0x09], 5, 1);
	 // Power:
	 writep[0].Words[6] = DDSIOWord(DIP, IOLOAD, 0, 0x21, datap[0].Raw().data[0x21], 6, 1);
	 writep[0].Words[7] = DDSIOWord(DIP, IOLOAD, 0, 0x22, datap[0].Raw().data[0x22], 7, 1);
	 // Control bits:
	 writep[0].Words[8] = DDSIOWord(DIP, IOLOAD, 0, 0x1d, datap[0].Raw().data[0x1d], 8, 1);
	 writep[0].Words[9] = DDSIOWord(DIP, IOLOAD, 0, 0x1e, datap[0].Raw().data[0x1e], 9, 1);
	 writep[0].Words[10] = DDSIOWord(DIP, IOLOAD, 0, 0x1f, datap[0].Raw().data[0x1f], 10, 1);
	 writep[0].Words[11] = DDSIOWord(DIP, IOLOAD, 0, 0x20, datap[0].Raw().data[0x20], 11, 1);
	 writep[0].Words[12] = DDSIOWord(DIP, IOLOAD, 0, 0x00, 0x00, 12, 1); //zero phase
	 writep[0].Words[13] = DDSIOWord(DIP, IOUPDATE, 0, 0x01, 0x00, 13, 1); // zero phase
	 writep[0].Words[14] = DDSIOWord(DIP, IOLOAD, 0, 0x1f, 0, 14, 1);
	 writep[0].Words[15] = DDSIOWord(DIP, IOUPDATE, 0, 0x23, 0, 15, 1); // force to write the mode code (since it is zero by default)
	 writep[0].changes = 16;

	for (unsigned int ii = 1; ii < Time2Tics(length); ii++) // loop to generate AD9852Raw data (change amp, freq inside this loop)
	    {
	    writep[ii].Words[0] = DDSIOWord(DIP, IOLOAD, 0, 0x23, 0, 0, 1);
	    writep[ii].Words[1] = DDSIOWord(DIP, IOLOAD, 0, 0x23, 0, 1, 1);
	    writep[ii].Words[2] = DDSIOWord(DIP, IOLOAD, 0, 0x23, 0, 2, 1);
	    writep[ii].Words[3] = DDSIOWord(DIP, IOLOAD, 0, 0x23, 0, 3, 1);
	    writep[ii].Words[4] = DDSIOWord(DIP, IOLOAD, 0, 0x23, 0, 4, 1);
	    writep[ii].Words[5] = DDSIOWord(DIP, IOLOAD, 0, 0x23, 0, 5, 1);
	    writep[ii].Words[6] = DDSIOWord(DIP, IOLOAD, 0, 0x23, 0, 6, 1);
	    writep[ii].Words[7] = DDSIOWord(DIP, IOUPDATE, 0, 0x23, 0, 7, 1); //do nothing
	    writep[ii].changes = 8;
	    }
	ios = 0;
	for (unsigned int ii = 0; ii < Time2Tics(length); ii++)
	    {
	    ios += writep[ii].changes;
	    }

	//second pulse
	writep[Time2Tics(length)].Words[0] = DDSIOWord(DIP, IOLOAD, 0, 0x23, 0, 0, 1);
	writep[Time2Tics(length)].Words[1] = DDSIOWord(DIP, IOLOAD, 0, 0x23, 0, 1, 1);
	writep[Time2Tics(length)].Words[2] = DDSIOWord(DIP, IOLOAD, 0, 0x23, 0, 2, 1);
	writep[Time2Tics(length)].Words[3] = DDSIOWord(DIP, IOLOAD, 0, 0x23, 0, 3, 1);
	writep[Time2Tics(length)].Words[4] = DDSIOWord(DIP, IOLOAD, 0, 0x23, 0, 4, 1);
	writep[Time2Tics(length)].Words[5] = DDSIOWord(DIP, IOLOAD, 0, 0x23, 0, 5, 1);
	writep[Time2Tics(length)].Words[6] = DDSIOWord(DIP, IOLOAD, 0, 0x00, 0x0f, 6, 1); //pi/2 phase
	writep[Time2Tics(length)].Words[7] = DDSIOWord(DIP, IOUPDATE, 0, 0x01, 0xff, 7, 1); //pi/2 phase
	 writep[Time2Tics(length)].changes = 8;
	//ios += 8;

	for (unsigned int ii = Time2Tics(length)+1; ii < 2*Time2Tics(length)+1; ii++) // loop to generate AD9852Raw data (change amp, freq inside this loop)
		    {
		    writep[ii].Words[0] = DDSIOWord(DIP, IOLOAD, 0, 0x23, 0, 0, 1);
		    writep[ii].Words[1] = DDSIOWord(DIP, IOLOAD, 0, 0x23, 0, 1, 1);
		    writep[ii].Words[2] = DDSIOWord(DIP, IOLOAD, 0, 0x23, 0, 2, 1);
		    writep[ii].Words[3] = DDSIOWord(DIP, IOLOAD, 0, 0x23, 0, 3, 1);
		    writep[ii].Words[4] = DDSIOWord(DIP, IOLOAD, 0, 0x23, 0, 4, 1);
		    writep[ii].Words[5] = DDSIOWord(DIP, IOLOAD, 0, 0x23, 0, 5, 1);
		    writep[ii].Words[6] = DDSIOWord(DIP, IOLOAD, 0, 0x23, 0, 6, 1);
		    writep[ii].Words[7] = DDSIOWord(DIP, IOUPDATE, 0, 0x23, 0, 7, 1); //do nothing
		    writep[ii].changes = 8;
		    }

	for (unsigned int ii = Time2Tics(length); ii < 2*Time2Tics(length)+1; ii++)
		    {
		    ios += writep[ii].changes;
		    }
	//third pulse
	int start=2*Time2Tics(length)+1;
	writep[Time2Tics(length)].Words[0] = DDSIOWord(DIP, IOLOAD, 0, 0x23, 0, 0, 1);
		writep[start].Words[1] = DDSIOWord(DIP, IOLOAD, 0, 0x23, 0, 1, 1);
		writep[start].Words[2] = DDSIOWord(DIP, IOLOAD, 0, 0x23, 0, 2, 1);
		writep[start].Words[3] = DDSIOWord(DIP, IOLOAD, 0, 0x23, 0, 3, 1);
		writep[start].Words[4] = DDSIOWord(DIP, IOLOAD, 0, 0x23, 0, 4, 1);
		writep[start].Words[5] = DDSIOWord(DIP, IOLOAD, 0, 0x23, 0, 5, 1);
		writep[start].Words[6] = DDSIOWord(DIP, IOLOAD, 0, 0x00, 0x00, 6, 1); //zero phase
		writep[start].Words[7] = DDSIOWord(DIP, IOUPDATE, 0, 0x01, 0x00, 7, 1);
		writep[start].changes = 8;

		for (unsigned int ii = start+1; ii <  start+1+Time2Tics(length); ii++) // loop to generate AD9852Raw data (change amp, freq inside this loop)
			    {
			    writep[ii].Words[0] = DDSIOWord(DIP, IOLOAD, 0, 0x23, 0, 0, 1);
			    writep[ii].Words[1] = DDSIOWord(DIP, IOLOAD, 0, 0x23, 0, 1, 1);
			    writep[ii].Words[2] = DDSIOWord(DIP, IOLOAD, 0, 0x23, 0, 2, 1);
			    writep[ii].Words[3] = DDSIOWord(DIP, IOLOAD, 0, 0x23, 0, 3, 1);
			    writep[ii].Words[4] = DDSIOWord(DIP, IOLOAD, 0, 0x23, 0, 4, 1);
			    writep[ii].Words[5] = DDSIOWord(DIP, IOLOAD, 0, 0x23, 0, 5, 1);
			    writep[ii].Words[6] = DDSIOWord(DIP, IOLOAD, 0, 0x23, 0, 6, 1);
			    writep[ii].Words[7] = DDSIOWord(DIP, IOUPDATE, 0, 0x23, 0, 7, 1); //do nothing
			    writep[ii].changes = 8;
			    }

		for (unsigned int ii = start; ii < start+1+Time2Tics(length); ii++)
			    {
			    ios += writep[ii].changes;
			    }

	}
    };

class PStarBlackman: public Pulse // A composite pi star pulse of Blackman
    {
public:
    PStarBlackman(double length1, double length2, double freq, double powmax) :
	Pulse(1+4*(2*Time2Tics(length1)+Time2Tics(length2)))  //
	{
	AD9852Reg registers;
	registers.CtrlReg.OSKEn    = 1; //     5	OSK enable                         0    Enable amplitude control
	registers.CtrlReg.OSKInt   = 0;
	registers.CtrlReg.IOUpClk  = 0; //     8	IO update clock in/out             0    Turn on!
	registers.CtrlReg.Mode[0]  = 0;
	registers.CtrlReg.Mode[1]  = 0;
	registers.CtrlReg.Mode[2]  = 0; //   9-11	Output operating mode             000   single tone mode
	registers.CtrlReg.PLLMult  = REFMULT;
	registers.CtrlReg.PLLRange = 1;
	registers.CtrlReg.ClrAcc = 1;
	registers.UpdateCtrlReg(); //   Must do this each time the control registers change

	registers.SetFreq1(Hz2FreqWord(freq)); // initial frequency

	datap[0] = registers;
	writep[0] = DDSIOWriteReg(datap[0]);

		 // Manually write all of the data:
		 // Frequency:
		 writep[0].Words[0] = DDSIOWord(DIP, IOLOAD, 0, 0x04, datap[0].Raw().data[0x04], 0, 1);
		 writep[0].Words[1] = DDSIOWord(DIP, IOLOAD, 0, 0x05, datap[0].Raw().data[0x05], 1, 1);
		 writep[0].Words[2] = DDSIOWord(DIP, IOLOAD, 0, 0x06, datap[0].Raw().data[0x06], 2, 1);
		 writep[0].Words[3] = DDSIOWord(DIP, IOLOAD, 0, 0x07, datap[0].Raw().data[0x07], 3, 1);
		 writep[0].Words[4] = DDSIOWord(DIP, IOLOAD, 0, 0x08, datap[0].Raw().data[0x08], 4, 1);
		 writep[0].Words[5] = DDSIOWord(DIP, IOLOAD, 0, 0x09, datap[0].Raw().data[0x09], 5, 1);
		 // Power:
		 writep[0].Words[6] = DDSIOWord(DIP, IOLOAD, 0, 0x21, datap[0].Raw().data[0x21], 6, 1);
		 writep[0].Words[7] = DDSIOWord(DIP, IOLOAD, 0, 0x22, datap[0].Raw().data[0x22], 7, 1);
		 // Control bits:
		 writep[0].Words[8] = DDSIOWord(DIP, IOLOAD, 0, 0x1d, datap[0].Raw().data[0x1d], 8, 1);
		 writep[0].Words[9] = DDSIOWord(DIP, IOLOAD, 0, 0x1e, datap[0].Raw().data[0x1e], 9, 1);
		 writep[0].Words[10] = DDSIOWord(DIP, IOLOAD, 0, 0x1f, datap[0].Raw().data[0x1f], 10, 1);
		 writep[0].Words[11] = DDSIOWord(DIP, IOLOAD, 0, 0x20, datap[0].Raw().data[0x20], 11, 1);
		 writep[0].Words[12] = DDSIOWord(DIP, IOLOAD, 0, 0x00, 0, 12, 1); //zero phase
		 writep[0].Words[13] = DDSIOWord(DIP, IOUPDATE, 0, 0x01, 0, 13, 1); //zero phase
		 //writep[0].Words[12] = DDSIOWord(DIP, IOLOAD, 0, 0x23, 0, 12, 1);
		 //writep[0].Words[13] = DDSIOWord(DIP, IOLOAD, 0, 0x23, 0, 13, 1);
		 writep[0].Words[14] = DDSIOWord(DIP, IOLOAD, 0, 0x1f, 0, 14, 1);
		 writep[0].Words[15] = DDSIOWord(DIP, IOUPDATE, 0, 0x23, 0, 15, 1); // force to write the mode code (since it is zero by default)
		 writep[0].changes = 16;

		 ios = 0;

		 /* first pulse */
		unsigned int tic1=4*Time2Tics(length1);
		unsigned int tic2=4*Time2Tics(length2);

	for (unsigned int ii = 1; ii < tic1+1; ii++) // loop to generate AD9852Raw data starting from second tic (change amp, freq inside this loop)
	    {
	    double power;
	    // Pulse amplitude shape follows:
	    power = powmax * pow(0.42 - 0.5 * cos(2.0 * PI * ii
		    / ((double) tic1 )) + 0.08 * cos(4.0 * PI * ii
		    / ((double) tic1 )),2); // power is amplitude squared

	    registers.SetOSKMult(Pow2AmpWord(power)); // set amplitude
	    registers.Time = ii;

	    datap[ii] = registers; // parse the registers and store

	    writep[ii].Words[0] = DDSIOWord(DIP, IOLOAD, 0, 0x21,
		    datap[ii].Raw().data[0x21], 0, 1);
	    writep[ii].Words[1] = DDSIOWord(DIP, IOUPDATE, 0, 0x22,
		    datap[ii].Raw().data[0x22], 1, 1);

	    writep[ii].changes = 2; // assume that both amplitude registers change, to keep timing sane
	    }



	/* second pulse */
	for (unsigned int ii = tic1+1; ii <  tic1+tic2+1; ii++) // loop to generate AD9852Raw data starting from second tic (change amp, freq inside this loop)
	    {
	    double power;
	    // Pulse amplitude shape follows:
	    power = powmax * pow(0.42 - 0.5 * cos(2.0 * PI * (ii-tic1)
		    / ((double) tic2 )) + 0.08 * cos(4.0 * PI * (ii-tic1)
		    / ((double) tic2 )),2); // power is amplitude squared

	    registers.SetOSKMult(Pow2AmpWord(power)); // set amplitude
	    registers.Time = ii;

	    datap[ii] = registers; // parse the registers and store

	    if(ii==tic1+1)
	    		{
	    	    writep[ii].Words[0] = DDSIOWord(DIP, IOLOAD, 0, 0x00, 0x10, 0, 1);   // pi/2 phase shift
	    	    writep[ii].Words[1] = DDSIOWord(DIP, IOLOAD, 0, 0x01, 0x00, 1, 1);
		    writep[ii].Words[2] = DDSIOWord(DIP, IOLOAD, 0, 0x21, datap[ii].Raw().data[0x21], 2, 1);
		    writep[ii].Words[3] = DDSIOWord(DIP, IOUPDATE, 0, 0x22, datap[ii].Raw().data[0x22], 3, 1);
		    writep[ii].changes = 4;
	    		}
	    	    else
	    		{
        	    writep[ii].Words[0] = DDSIOWord(DIP, IOLOAD, 0, 0x21, datap[ii].Raw().data[0x21], 0, 1);
	    	    writep[ii].Words[1] = DDSIOWord(DIP, IOUPDATE, 0, 0x22, datap[ii].Raw().data[0x22], 1, 1);
	    	    writep[ii].changes = 2;
	    		}

	    }


	/*third pulse*/
	for (unsigned int ii =  tic1+tic2+1; ii <  2*tic1+tic2+1; ii++) // loop to generate AD9852Raw data starting from second tic (change amp, freq inside this loop)
		    {
		    double power;
		    // Pulse amplitude shape follows:
		    power = powmax * pow(0.42 - 0.5 * cos(2.0 * PI * (ii-(tic1+tic2))
			    / ((double) tic1 )) + 0.08 * cos(4.0 * PI * (ii-(tic1+tic2))
			    / ((double) tic1 )),2); // power is amplitude squared

		    registers.SetOSKMult(Pow2AmpWord(power)); // set amplitude
		    registers.Time = ii;

		    datap[ii] = registers; // parse the registers and store

		    if(ii==tic1+tic2+1)
		    		{
		    	    writep[ii].Words[0] = DDSIOWord(DIP, IOLOAD, 0, 0x00, 0, 0, 1);   // 0 phase shift
		    	    writep[ii].Words[1] = DDSIOWord(DIP, IOLOAD, 0, 0x01, 0, 1, 1);
			    writep[ii].Words[2] = DDSIOWord(DIP, IOLOAD, 0, 0x21, datap[ii].Raw().data[0x21], 2, 1);
			    writep[ii].Words[3] = DDSIOWord(DIP, IOUPDATE, 0, 0x22, datap[ii].Raw().data[0x22], 3, 1);
			    writep[ii].changes = 4;
		    		}
		    	    else
		    		{
	        	    writep[ii].Words[0] = DDSIOWord(DIP, IOLOAD, 0, 0x21, datap[ii].Raw().data[0x21], 0, 1);
		    	    writep[ii].Words[1] = DDSIOWord(DIP, IOUPDATE, 0, 0x22, datap[ii].Raw().data[0x22], 1, 1);
		    	    writep[ii].changes = 2;
		    		}

	/*write changes*/
	for (unsigned int ii = 0; ii < tics; ii++)
	    {
	    ios += writep[ii].changes;
	    }
	}
    }
};


class PRamsey: public Pulse // Ramsey sequence: 2 Blackman pulses separated by a wait.
    {
public:
    PRamsey(double length, double freq,  double wait,double powmax) :
	Pulse(1+2*4*Time2Tics(length)+4*Time2Tics(wait))
	{
        unsigned long ticspulses = 4*Time2Tics(length); // Length of pulses in tics
        unsigned long ticswait = 4*Time2Tics(wait); // Length of wait in tics
	AD9852Reg registers;
	// Set control register values (only those that vary from default values)
	//                                    Bits	Function                       Default  Reason for change
	registers.CtrlReg.OSKEn    = 1; //     5	OSK enable                         0    Enable amplitude control
	registers.CtrlReg.OSKInt   = 0;
	registers.CtrlReg.IOUpClk  = 0; //     8	IO update clock in/out             0    Turn on!
	// Set mode to single tone
	registers.CtrlReg.Mode[0]  = 0;
	registers.CtrlReg.Mode[1]  = 0;
	registers.CtrlReg.Mode[2]  = 0; //   9-11	Output operating mode             000   single tone mode
	registers.CtrlReg.PLLMult  = REFMULT;
	registers.CtrlReg.PLLRange = 1;
	//registers.CtrlReg.ClrAcc1 = 0;
	registers.CtrlReg.ClrAcc = 1;
	registers.UpdateCtrlReg(); //   Must do this each time the control registers change

	registers.SetFreq1(Hz2FreqWord(freq)); // initial frequency

	datap[0] = registers;
	writep[0] = DDSIOWriteReg(datap[0]);

		 // Manually write all of the data:
		 // Frequency:
		 writep[0].Words[0] = DDSIOWord(DIP, IOLOAD, 0, 0x04, datap[0].Raw().data[0x04], 0, 1);
		 writep[0].Words[1] = DDSIOWord(DIP, IOLOAD, 0, 0x05, datap[0].Raw().data[0x05], 1, 1);
		 writep[0].Words[2] = DDSIOWord(DIP, IOLOAD, 0, 0x06, datap[0].Raw().data[0x06], 2, 1);
		 writep[0].Words[3] = DDSIOWord(DIP, IOLOAD, 0, 0x07, datap[0].Raw().data[0x07], 3, 1);
		 writep[0].Words[4] = DDSIOWord(DIP, IOLOAD, 0, 0x08, datap[0].Raw().data[0x08], 4, 1);
		 writep[0].Words[5] = DDSIOWord(DIP, IOLOAD, 0, 0x09, datap[0].Raw().data[0x09], 5, 1);
		 // Power:
		 writep[0].Words[6] = DDSIOWord(DIP, IOLOAD, 0, 0x21, datap[0].Raw().data[0x21], 6, 1);
		 writep[0].Words[7] = DDSIOWord(DIP, IOLOAD, 0, 0x22, datap[0].Raw().data[0x22], 7, 1);
		 // Control bits:
		 writep[0].Words[8] = DDSIOWord(DIP, IOLOAD, 0, 0x1d, datap[0].Raw().data[0x1d], 8, 1);
		 writep[0].Words[9] = DDSIOWord(DIP, IOLOAD, 0, 0x1e, datap[0].Raw().data[0x1e], 9, 1);
		 writep[0].Words[10] = DDSIOWord(DIP, IOLOAD, 0, 0x1f, datap[0].Raw().data[0x1f], 10, 1);
		 writep[0].Words[11] = DDSIOWord(DIP, IOLOAD, 0, 0x20, datap[0].Raw().data[0x20], 11, 1);
		 writep[0].Words[12] = DDSIOWord(DIP, IOLOAD, 0, 0x00, 0, 12, 1); //zero phase
		 writep[0].Words[13] = DDSIOWord(DIP, IOUPDATE, 0, 0x01, 0, 13, 1); //zero phase
		 //writep[0].Words[12] = DDSIOWord(DIP, IOLOAD, 0, 0x23, 0, 12, 1);
		 //writep[0].Words[13] = DDSIOWord(DIP, IOLOAD, 0, 0x23, 0, 13, 1);
		 writep[0].Words[14] = DDSIOWord(DIP, IOLOAD, 0, 0x1f, 0, 14, 1);
		 writep[0].Words[15] = DDSIOWord(DIP, IOUPDATE, 0, 0x23, 0, 15, 1); // force to write the mode code (since it is zero by default)
		 writep[0].changes = 16;


        // First pulse
	for (unsigned int ii = 1; ii < ticspulses+1; ii++)
	    {
	    double power;
	    power = powmax * pow(0.42 - 0.5 * cos(2.0 * PI * ii
		    / ((double) ticspulses )) + 0.08 * cos(4.0 * PI * ii
		    / ((double) ticspulses )),2); // power is amplitude squared

	    //  amp=Pow2Volts(maxpow)*ii/(double)tics;  // Triangle Pulse (for debug)
	    registers.SetOSKMult(Pow2AmpWord(power)); // set amplitude
	    registers.Time = ii;

	    datap[ii] = registers; // parse the registers and store

	    writep[ii].Words[0] = DDSIOWord(DIP, IOLOAD, 0, 0x21,
		    datap[ii].Raw().data[0x21], 0, 1);
	    writep[ii].Words[1] = DDSIOWord(DIP, IOUPDATE, 0, 0x22,
		    datap[ii].Raw().data[0x22], 1, 1);

	    writep[ii].changes = 2; // assume that both amplitude registers change, to keep timing sane
	    }
        // Wait
	for (unsigned int ii = ticspulses+1; ii < ticspulses+ticswait+1; ii++) // loop to generate AD9852Raw data starting from second tic (change amp, freq inside this loop)
	    {
	   // registers.SetOSKMult(0); // set amplitude to zero
	    registers.Time = ii;
	   // datap[ii] = registers; // parse the registers and store
	    writep[ii].Words[0] = DDSIOWord(DIP, IOLOAD, 0, 0x21,
		    0, 0, 1);
	    writep[ii].Words[1] = DDSIOWord(DIP, IOUPDATE, 0, 0x22,
		   0, 1, 1);
	    // HACK:
	    writep[ii].changes = 2; // assume that both amplitude registers change, to keep timing sane
	    }
        // Second pulse (exactly like the first)
	for (unsigned int ii = ticspulses+ticswait+1; ii < 2*ticspulses+ticswait+1; ii++) // loop to generate AD9852Raw data starting from second tic (change amp, freq inside this loop)
	    {
	    double power;
	    //Pulse frequency shape follows:
	    //registers.SetFreq1(Hz2FreqWord(freq)); // set frequency
	    // Pulse amplitude shape follows:
	    power = powmax * pow(0.42 - 0.5 * cos(2.0 * PI * (ii- ticspulses-ticswait)
		    / ((double) ticspulses )) + 0.08 * cos(4.0 * PI * (ii- ticspulses-ticswait)
		    / ((double) ticspulses )),2); // power is amplitude squared

	    //  amp=Pow2Volts(maxpow)*ii/(double)tics;  // Triangle Pulse (for debug)
	    registers.SetOSKMult(Pow2AmpWord(power)); // set amplitude
	    registers.Time = ii;

	    datap[ii] = registers; // parse the registers and store


	    writep[ii].Words[0] = DDSIOWord(DIP, IOLOAD, 0, 0x21,
		    datap[ii].Raw().data[0x21], 0, 1);
	    writep[ii].Words[1] = DDSIOWord(DIP, IOUPDATE, 0, 0x22,
		    datap[ii].Raw().data[0x22], 1, 1);

	    writep[ii].changes = 2; // assume that both amplitude registers change, to keep timing sane
	    }

	// Count data words:
	ios = 0;
	for (unsigned int ii = 0; ii < tics; ii++)
	    {
	    ios += writep[ii].changes;
	    }
	}
    };

class PEcho: public Pulse // Echo sequence: pi/2+wait+pi+wait+pi/2
    {
public:
    PEcho(double length, double freq,  double wait,double powmax) :
	Pulse(1+4*(4*Time2Tics(length)+2*Time2Tics(wait)))
	{
        unsigned long ticsPiHalf = 4*Time2Tics(length); // Length of pi/2 pulses
        unsigned long ticsPi = 2*4*Time2Tics(length);   // Length of pi pulses
        unsigned long ticswait = 4*Time2Tics(wait);     // Length of wait in tics
	AD9852Reg registers;
	// Set control register values (only those that vary from default values)
	//                                    Bits	Function                       Default  Reason for change
	registers.CtrlReg.OSKEn    = 1; //     5	OSK enable                         0    Enable amplitude control
	registers.CtrlReg.OSKInt   = 0;
	registers.CtrlReg.IOUpClk  = 0; //     8	IO update clock in/out             0    Turn on!
	// Set mode to single tone
	registers.CtrlReg.Mode[0]  = 0;
	registers.CtrlReg.Mode[1]  = 0;
	registers.CtrlReg.Mode[2]  = 0; //   9-11	Output operating mode             000   single tone mode
	registers.CtrlReg.PLLMult  = REFMULT;
	registers.CtrlReg.PLLRange = 1;
	//registers.CtrlReg.ClrAcc1 = 0;
	registers.CtrlReg.ClrAcc = 1;
	registers.UpdateCtrlReg(); //   Must do this each time the control registers change

	registers.SetFreq1(Hz2FreqWord(freq)); // initial frequency

	datap[0] = registers;
	writep[0] = DDSIOWriteReg(datap[0]);

		 // Manually write all of the data:
		 // Frequency:
		 writep[0].Words[0] = DDSIOWord(DIP, IOLOAD, 0, 0x04, datap[0].Raw().data[0x04], 0, 1);
		 writep[0].Words[1] = DDSIOWord(DIP, IOLOAD, 0, 0x05, datap[0].Raw().data[0x05], 1, 1);
		 writep[0].Words[2] = DDSIOWord(DIP, IOLOAD, 0, 0x06, datap[0].Raw().data[0x06], 2, 1);
		 writep[0].Words[3] = DDSIOWord(DIP, IOLOAD, 0, 0x07, datap[0].Raw().data[0x07], 3, 1);
		 writep[0].Words[4] = DDSIOWord(DIP, IOLOAD, 0, 0x08, datap[0].Raw().data[0x08], 4, 1);
		 writep[0].Words[5] = DDSIOWord(DIP, IOLOAD, 0, 0x09, datap[0].Raw().data[0x09], 5, 1);
		 // Power:
		 writep[0].Words[6] = DDSIOWord(DIP, IOLOAD, 0, 0x21, datap[0].Raw().data[0x21], 6, 1);
		 writep[0].Words[7] = DDSIOWord(DIP, IOLOAD, 0, 0x22, datap[0].Raw().data[0x22], 7, 1);
		 // Control bits:
		 writep[0].Words[8] = DDSIOWord(DIP, IOLOAD, 0, 0x1d, datap[0].Raw().data[0x1d], 8, 1);
		 writep[0].Words[9] = DDSIOWord(DIP, IOLOAD, 0, 0x1e, datap[0].Raw().data[0x1e], 9, 1);
		 writep[0].Words[10] = DDSIOWord(DIP, IOLOAD, 0, 0x1f, datap[0].Raw().data[0x1f], 10, 1);
		 writep[0].Words[11] = DDSIOWord(DIP, IOLOAD, 0, 0x20, datap[0].Raw().data[0x20], 11, 1);
		 writep[0].Words[12] = DDSIOWord(DIP, IOLOAD, 0, 0x00, 0, 12, 1); //zero phase
		 writep[0].Words[13] = DDSIOWord(DIP, IOUPDATE, 0, 0x01, 0, 13, 1); //zero phase
		 //writep[0].Words[12] = DDSIOWord(DIP, IOLOAD, 0, 0x23, 0, 12, 1);
		 //writep[0].Words[13] = DDSIOWord(DIP, IOLOAD, 0, 0x23, 0, 13, 1);
		 writep[0].Words[14] = DDSIOWord(DIP, IOLOAD, 0, 0x1f, 0, 14, 1);
		 writep[0].Words[15] = DDSIOWord(DIP, IOUPDATE, 0, 0x23, 0, 15, 1); // force to write the mode code (since it is zero by default)
		 writep[0].changes = 16;


        // First pulse (pi/2)
	for (unsigned int ii = 1; ii < ticsPiHalf+1; ii++)
	    {
	    double power;
	    power = powmax * pow(0.42 - 0.5 * cos(2.0 * PI * ii
		    / ((double) ticsPiHalf )) + 0.08 * cos(4.0 * PI * ii
		    / ((double) ticsPiHalf )),2); // power is amplitude squared

	    registers.SetOSKMult(Pow2AmpWord(power)); // set amplitude
	    registers.Time = ii;

	    datap[ii] = registers; // parse the registers and store

	    if(ii==1){
	    writep[ii].Words[0] = DDSIOWord(DIP, IOLOAD, 0, 0x23, 0, 0, 1); // keep timing right
	    writep[ii].Words[1] = DDSIOWord(DIP, IOLOAD, 0, 0x23, 0, 1, 1); //
	    writep[ii].Words[2] = DDSIOWord(DIP, IOLOAD, 0, 0x21,
		    datap[ii].Raw().data[0x21], 2, 1);
	    writep[ii].Words[3] = DDSIOWord(DIP, IOUPDATE, 0, 0x22,
		    datap[ii].Raw().data[0x22], 3, 1);
	    writep[ii].changes = 4;}
	    else{
            writep[ii].Words[0] = DDSIOWord(DIP, IOLOAD, 0, 0x21,
				    datap[ii].Raw().data[0x21], 0, 1);
	    writep[ii].Words[1] = DDSIOWord(DIP, IOUPDATE, 0, 0x22,
				    datap[ii].Raw().data[0x22], 1, 1);
	    writep[ii].changes = 2;
	    }
	    }

        // First Wait
	for (unsigned int ii = ticsPiHalf+1; ii < ticsPiHalf+ticswait+1; ii++)
	    {
	    registers.Time = ii;
	    writep[ii].Words[0] = DDSIOWord(DIP, IOLOAD, 0, 0x21,
		    0, 0, 1);
	    writep[ii].Words[1] = DDSIOWord(DIP, IOUPDATE, 0, 0x22,
		   0, 1, 1);
	    writep[ii].changes = 2;
	    }

        // Second pulse (Pi)
	for (unsigned int ii = ticsPiHalf+ticswait+1; ii < ticsPiHalf+ticswait+ticsPi+1; ii++)
	    {
	    double power;

	    power = powmax * pow(0.42 - 0.5 * cos(2.0 * PI * (ii- ticsPiHalf-ticswait)
		    / ((double)  ticsPi )) + 0.08 * cos(4.0 * PI * (ii- ticsPiHalf-ticswait)
		    / ((double)  ticsPi )),2); // power is amplitude squared

	    registers.SetOSKMult(Pow2AmpWord(power)); // set amplitude
	    registers.Time = ii;

	    datap[ii] = registers;

	    writep[ii].Words[0] = DDSIOWord(DIP, IOLOAD, 0, 0x21,
		    datap[ii].Raw().data[0x21], 0, 1);
	    writep[ii].Words[1] = DDSIOWord(DIP, IOUPDATE, 0, 0x22,
		    datap[ii].Raw().data[0x22], 1, 1);

	    writep[ii].changes = 2;
	    }

        // Second Wait
	for (unsigned int ii = ticsPiHalf+ticswait+ticsPi+1; ii < ticsPiHalf+2*ticswait+ticsPi+1; ii++)
	    {
	    registers.Time = ii;
	    writep[ii].Words[0] = DDSIOWord(DIP, IOLOAD, 0, 0x21,
		    0, 0, 1);
	    writep[ii].Words[1] = DDSIOWord(DIP, IOUPDATE, 0, 0x22,
		   0, 1, 1);
	    writep[ii].changes = 2;
	    }

        // Third pulse pulse
	for (unsigned int ii = ticsPiHalf+2*ticswait+ticsPi+1; ii < 2*ticsPiHalf+2*ticswait+ticsPi+1; ii++)
	    {
	    double power;

	    power = powmax * pow(0.42 - 0.5 * cos(2.0 * PI * (ii- ticsPiHalf-2*ticswait-ticsPi)
		    / ((double) ticsPiHalf )) + 0.08 * cos(4.0 * PI * (ii- ticsPiHalf-2*ticswait-ticsPi)
		    / ((double) ticsPiHalf )),2); // power is amplitude squared

	    registers.SetOSKMult(Pow2AmpWord(power)); // set amplitude
	    registers.Time = ii;

	    datap[ii] = registers;

	    if(ii==ticsPiHalf+2*ticswait+ticsPi+1){
	    //writep[ii].Words[0] = DDSIOWord(DIP, IOLOAD, 0, 0x00, 0x1f, 0, 1);   // pi phase shift
	    //writep[ii].Words[1] = DDSIOWord(DIP, IOLOAD, 0, 0x01, 0xff, 1, 1);
	    writep[ii].Words[0] = DDSIOWord(DIP, IOLOAD, 0, 0x23, 0, 0, 1);    // keep timing right
	    writep[ii].Words[1] = DDSIOWord(DIP, IOLOAD, 0, 0x23, 0, 1, 1);    //
	    writep[ii].Words[2] = DDSIOWord(DIP, IOLOAD, 0, 0x21,
		    datap[ii].Raw().data[0x21], 2, 1);
	    writep[ii].Words[3] = DDSIOWord(DIP, IOUPDATE, 0, 0x22,
		    datap[ii].Raw().data[0x22], 3, 1);
	    writep[ii].changes = 4;}
	    else{
            writep[ii].Words[0] = DDSIOWord(DIP, IOLOAD, 0, 0x21,
				    datap[ii].Raw().data[0x21], 0, 1);
	    writep[ii].Words[1] = DDSIOWord(DIP, IOUPDATE, 0, 0x22,
				    datap[ii].Raw().data[0x22], 1, 1);
	    writep[ii].changes = 2;
	    }
	    }
	// Count data words:
	ios = 0;
	for (unsigned int ii = 0; ii < tics; ii++)
	    {
	    ios += writep[ii].changes;
	    }
	}
    };

class POff: public Pulse // Pulse to power down the DDS, at end of sequence
    {
public:
    POff() :
	Pulse((unsigned long) 1)
	{
	// TODO: Rewrite using registers
	// Set frequency = 0
    AD9852Reg registers;
    //                                    Bits	Function                       Default  Reason for change
    registers.CtrlReg.OSKEn   = 0; //     5	OSK enable                         0    Enable amplitude control
    registers.CtrlReg.OSKInt  = 0;
    registers.CtrlReg.IOUpClk = 0; //     8	IO update clock in/out             0    Turn on!
    // Set mode to single tone
    registers.CtrlReg.Mode[0] = 0;
    registers.CtrlReg.Mode[1] = 0;
    registers.CtrlReg.Mode[2] = 0; //   9-11	Output operating mode             000 (Single tone)
    registers.CtrlReg.ClrAcc  = 1; //    14	Clear Accumulators                 0    Reset phase
    registers.CtrlReg.ClrAcc1 = 0;
    registers.CtrlReg.PLLMult = REFMULT;
    registers.CtrlReg.PowComp = 1; // Power off comparator
    registers.CtrlReg.PowCtlDAC = 1; // Power off control DAQ
    registers.CtrlReg.PowDAC = 1; // Power off DAQ
    registers.CtrlReg.PowDig = 1; // Power off digital
    registers.CtrlReg.Halt = 1; // Halt!
    registers.UpdateCtrlReg(); //   Must do this each time the control registers change
    registers.SetFreq1(0); // set frequency
    //registers.SetFreq2(Hz2FreqWord(freq)); // set frequency
    //cout << "OSKMult = " << dec << Pow2AmpWord(power) << endl;
    registers.SetPhaseAdj1(0); // set phase
    registers.SetOSKMult(0); // constant amplitude
    datap[0] = registers; // parse the registers and store

    writep[0] = DDSIOWriteReg(datap[0]);

 // Manually write all of the data:
 // Frequency:
 writep[0].Words[0] = DDSIOWord(DIP, IOLOAD, 0, 0x04, datap[0].Raw().data[0x04], 0, 1);
 writep[0].Words[1] = DDSIOWord(DIP, IOLOAD, 0, 0x05, datap[0].Raw().data[0x05], 1, 1);
 writep[0].Words[2] = DDSIOWord(DIP, IOLOAD, 0, 0x06, datap[0].Raw().data[0x06], 2, 1);
 writep[0].Words[3] = DDSIOWord(DIP, IOLOAD, 0, 0x07, datap[0].Raw().data[0x07], 3, 1);
 writep[0].Words[4] = DDSIOWord(DIP, IOLOAD, 0, 0x08, datap[0].Raw().data[0x08], 4, 1);
 writep[0].Words[5] = DDSIOWord(DIP, IOLOAD, 0, 0x09, datap[0].Raw().data[0x09], 5, 1);
 // Power:
 writep[0].Words[6] = DDSIOWord(DIP, IOLOAD, 0, 0x21, datap[0].Raw().data[0x21], 6, 1);
 writep[0].Words[7] = DDSIOWord(DIP, IOLOAD, 0, 0x22, datap[0].Raw().data[0x22], 7, 1);
 // Control bits:
 writep[0].Words[8] = DDSIOWord(DIP, IOLOAD, 0, 0x1d, datap[0].Raw().data[0x1d], 8, 1);
 writep[0].Words[9] = DDSIOWord(DIP, IOLOAD, 0, 0x1e, datap[0].Raw().data[0x1e], 9, 1);
 writep[0].Words[10] = DDSIOWord(DIP, IOLOAD, 0, 0x1f, datap[0].Raw().data[0x1f], 10, 1);
 writep[0].Words[11] = DDSIOWord(DIP, IOLOAD, 0, 0x20, datap[0].Raw().data[0x20], 11, 1);
 //writep[0].Words[12] = DDSIOWord(DIP, IOLOAD, 0, 0x00, PhaseByteHigh, 12, 1); // set phase
 //writep[0].Words[13] = DDSIOWord(DIP, IOUPDATE, 0, 0x01, PhaseByteLow, 13, 1);
 writep[0].Words[12] = DDSIOWord(DIP, IOLOAD, 0, 0x00, 0, 12, 1); // set phase
 writep[0].Words[13] = DDSIOWord(DIP, IOUPDATE, 0, 0x01, 0, 13, 1);
 writep[0].Words[14] = DDSIOWord(DIP, IOLOAD, 0, 0x1f, 0, 14, 1);
 writep[0].Words[15] = DDSIOWord(DIP, IOUPDATE, 0, 0x23, 0, 15, 1); // force to write the mode code (since it is zero by default)
 writep[0].changes = 16;

if (writep[0].Words[7].RawIO==0){
 writep[0].Words[7] = DDSIOWord(DIP, IOLOAD, 0, 0x23, 0, 7, 1);}
 writep[0].Words[8] = DDSIOWord(DIP, IOLOAD, 0, 0x21, datap[0].Raw().data[0x21], 8, 1);
 writep[0].Words[9] = DDSIOWord(DIP, IOLOAD, 0, 0x22, datap[0].Raw().data[0x22], 9, 1);
 writep[0].Words[10] = DDSIOWord(DIP, IOLOAD, 0, 0x1d, datap[0].Raw().data[0x1d], 10, 1);
 writep[0].Words[11] = DDSIOWord(DIP, IOLOAD, 0, 0x1e, datap[0].Raw().data[0x1e], 11, 1);
 writep[0].Words[12] = DDSIOWord(DIP, IOLOAD, 0, 0x1f, datap[0].Raw().data[0x1f], 12, 1);
 writep[0].Words[13] = DDSIOWord(DIP, IOLOAD, 0, 0x20, datap[0].Raw().data[0x20], 13, 1);
 writep[0].Words[14] = DDSIOWord(DIP, IOLOAD, 0, 0x23, 0, 14, 1);
 writep[0].Words[15] = DDSIOWord(DIP, IOUPDATE, 0, 0x1f, 0, 15, 1); // force to write the mode code (since it is zero by default)

 writep[0].changes = 16;
	writep[0].Words[0] = DDSIOWord(DIP, IOLOAD, 0, 0x04, 0, 0, 1);
	writep[0].Words[1] = DDSIOWord(DIP, IOLOAD, 0, 0x05, 0, 1, 1);
	writep[0].Words[2] = DDSIOWord(DIP, IOLOAD, 0, 0x06, 0, 2, 1);
	writep[0].Words[3] = DDSIOWord(DIP, IOLOAD, 0, 0x07, 0, 3, 1);
	writep[0].Words[4] = DDSIOWord(DIP, IOLOAD, 0, 0x08, 0, 4, 1);
	writep[0].Words[5] = DDSIOWord(DIP, IOLOAD, 0, 0x09, 0, 5, 1);
	// Set amplitude = 0
	writep[0].Words[6] = DDSIOWord(DIP, IOLOAD, 0, 0x21, 0, 6, 1);
	writep[0].Words[7] = DDSIOWord(DIP, IOUPDATE, 0, 0x22, 0, 7, 0); //self-mask signal writes 0 here
	//writep[0].Words[7] = DDSIOWord(DIP, IOUPDATE, 0, 0x22, 0, 7, 1); //self-mask signal writes 0 here
	ios = 8;
	writep[0].changes = 8;
	}
    };


class PRamseyPhase: public Pulse // Ramsey sequence: 2 Blackman pulses separated by a variable wait and phase, the pulse length is
				    //   calculated through a fixed pi-pulse area in the DDSconstants via power
    {
public:
    PRamseyPhase(double wait, double freq,  double phase,double powmax) :
	Pulse(1+2*4*Time2Tics(PIPULSEAREA/2/sqrt(powmax))+4*Time2Tics(wait))
	{
	double	length	= PIPULSEAREA/2/sqrt(powmax);
        unsigned long ticspulses = 4*Time2Tics(length); // Length of pulses in tics
        unsigned long ticswait = 4*Time2Tics(wait); // wait time
	AD9852Reg registers;
	// Set control register values (only those that vary from default values)
	//                                    Bits	Function                       Default  Reason for change
	registers.CtrlReg.OSKEn    = 1; //     5	OSK enable                         0    Enable amplitude control
	registers.CtrlReg.OSKInt   = 0;
	registers.CtrlReg.IOUpClk  = 0; //     8	IO update clock in/out             0    Turn on!
	// Set mode to single tone
	registers.CtrlReg.Mode[0]  = 0;
	registers.CtrlReg.Mode[1]  = 0;
	registers.CtrlReg.Mode[2]  = 0; //   9-11	Output operating mode             000   single tone mode
	registers.CtrlReg.PLLMult  = REFMULT;
	registers.CtrlReg.PLLRange = 1;
	//registers.CtrlReg.ClrAcc1 = 0;
	registers.CtrlReg.ClrAcc = 1;
	registers.UpdateCtrlReg(); //   Must do this each time the control registers change

	registers.SetFreq1(Hz2FreqWord(freq)); // initial frequency

	datap[0] = registers;
	writep[0] = DDSIOWriteReg(datap[0]);

		 // Manually write all of the data:
		 // Frequency:
		 writep[0].Words[0] = DDSIOWord(DIP, IOLOAD, 0, 0x04, datap[0].Raw().data[0x04], 0, 1);
		 writep[0].Words[1] = DDSIOWord(DIP, IOLOAD, 0, 0x05, datap[0].Raw().data[0x05], 1, 1);
		 writep[0].Words[2] = DDSIOWord(DIP, IOLOAD, 0, 0x06, datap[0].Raw().data[0x06], 2, 1);
		 writep[0].Words[3] = DDSIOWord(DIP, IOLOAD, 0, 0x07, datap[0].Raw().data[0x07], 3, 1);
		 writep[0].Words[4] = DDSIOWord(DIP, IOLOAD, 0, 0x08, datap[0].Raw().data[0x08], 4, 1);
		 writep[0].Words[5] = DDSIOWord(DIP, IOLOAD, 0, 0x09, datap[0].Raw().data[0x09], 5, 1);
		 // Power:
		 writep[0].Words[6] = DDSIOWord(DIP, IOLOAD, 0, 0x21, datap[0].Raw().data[0x21], 6, 1);
		 writep[0].Words[7] = DDSIOWord(DIP, IOLOAD, 0, 0x22, datap[0].Raw().data[0x22], 7, 1);
		 // Control bits:
		 writep[0].Words[8] = DDSIOWord(DIP, IOLOAD, 0, 0x1d, datap[0].Raw().data[0x1d], 8, 1);
		 writep[0].Words[9] = DDSIOWord(DIP, IOLOAD, 0, 0x1e, datap[0].Raw().data[0x1e], 9, 1);
		 writep[0].Words[10] = DDSIOWord(DIP, IOLOAD, 0, 0x1f, datap[0].Raw().data[0x1f], 10, 1);
		 writep[0].Words[11] = DDSIOWord(DIP, IOLOAD, 0, 0x20, datap[0].Raw().data[0x20], 11, 1);
		 writep[0].Words[12] = DDSIOWord(DIP, IOLOAD, 0, 0x00, 0, 12, 1); //zero phase
		 writep[0].Words[13] = DDSIOWord(DIP, IOUPDATE, 0, 0x01, 0, 13, 1); //zero phase
		 //writep[0].Words[12] = DDSIOWord(DIP, IOLOAD, 0, 0x23, 0, 12, 1);
		 //writep[0].Words[13] = DDSIOWord(DIP, IOLOAD, 0, 0x23, 0, 13, 1);
		 writep[0].Words[14] = DDSIOWord(DIP, IOLOAD, 0, 0x1f, 0, 14, 1);
		 writep[0].Words[15] = DDSIOWord(DIP, IOUPDATE, 0, 0x23, 0, 15, 1); // force to write the mode code (since it is zero by default)
		 writep[0].changes = 16;


        // First pulse
	for (unsigned int ii = 1; ii < ticspulses+1; ii++)
	    {
	    double power;
	    power = powmax * pow(0.42 - 0.5 * cos(2.0 * PI * ii
		    / ((double) ticspulses )) + 0.08 * cos(4.0 * PI * ii
		    / ((double) ticspulses )),2); // power is amplitude squared

	    //  amp=Pow2Volts(maxpow)*ii/(double)tics;  // Triangle Pulse (for debug)
	    registers.SetOSKMult(Pow2AmpWord(power)); // set amplitude
	    registers.Time = ii;

	    datap[ii] = registers; // parse the registers and store

	    writep[ii].Words[0] = DDSIOWord(DIP, IOLOAD, 0, 0x21,
		    datap[ii].Raw().data[0x21], 0, 1);
	    writep[ii].Words[1] = DDSIOWord(DIP, IOUPDATE, 0, 0x22,
		    datap[ii].Raw().data[0x22], 1, 1);

	    writep[ii].changes = 2; // assume that both amplitude registers change, to keep timing sane
	    }

        // Wait
	for (unsigned int ii = ticspulses+1; ii < ticspulses+ticswait+1; ii++) // loop to generate AD9852Raw data starting from second tic (change amp, freq inside this loop)
	    {
	   // registers.SetOSKMult(0); // set amplitude to zero
	    registers.Time = ii;
	   // datap[ii] = registers; // parse the registers and store
	    writep[ii].Words[0] = DDSIOWord(DIP, IOLOAD, 0, 0x21,
		    0, 0, 1);
	    writep[ii].Words[1] = DDSIOWord(DIP, IOUPDATE, 0, 0x22,
		   0, 1, 1);
	    // HACK:
	    writep[ii].changes = 2; // assume that both amplitude registers change, to keep timing same
	    }

        // Second pulse (exactly like the first, with a phase shift)
	for (unsigned int ii = ticspulses+ticswait+1; ii < 2*ticspulses+ticswait+1; ii++) // loop to generate AD9852Raw data starting from second tic (change amp, freq inside this loop)
	    {
	    double power;
	    //Pulse frequency shape follows:
	    //registers.SetFreq1(Hz2FreqWord(freq)); // set frequency
	    // Pulse amplitude shape follows:
	    power = powmax * pow(0.42 - 0.5 * cos(2.0 * PI * (ii- ticspulses-ticswait)
		    / ((double) ticspulses )) + 0.08 * cos(4.0 * PI * (ii- ticspulses-ticswait)
		    / ((double) ticspulses )),2); // power is amplitude squared

	    //  amp=Pow2Volts(maxpow)*ii/(double)tics;  // Triangle Pulse (for debug)
	    registers.SetOSKMult(Pow2AmpWord(power)); // set amplitude
	    registers.Time = ii;
	    registers.SetPhaseAdj1(Phase2PhaseWord(phase)); // Set phase
	    datap[ii] = registers; // parse the registers and store

	    if(ii == ticspulses+ticswait+1)
		{
		writep[ii].Words[0] = DDSIOWord(DIP, IOLOAD, 0, 0x00, datap[ii].Raw().data[0x00], 12, 1); //write phase
		writep[ii].Words[1] = DDSIOWord(DIP, IOLOAD, 0, 0x01, datap[ii].Raw().data[0x01], 13, 1); //write phase
		writep[ii].Words[2] = DDSIOWord(DIP, IOLOAD, 0, 0x21,datap[ii].Raw().data[0x21], 0, 1);
		writep[ii].Words[3] = DDSIOWord(DIP, IOUPDATE, 0, 0x22, datap[ii].Raw().data[0x22], 1, 1);
		writep[ii].changes = 4; // assume that both amplitude registers change, to keep timing same
		}
	    else
		{
		writep[ii].Words[0] = DDSIOWord(DIP, IOLOAD, 0, 0x21,datap[ii].Raw().data[0x21], 0, 1);
		writep[ii].Words[1] = DDSIOWord(DIP, IOUPDATE, 0, 0x22,datap[ii].Raw().data[0x22], 1, 1);
		writep[ii].changes = 2; // assume that both amplitude registers change, to keep timing same
		}



	    }

	// Count data words:
	ios = 0;
	for (unsigned int ii = 0; ii < tics; ii++)
	    {
	    ios += writep[ii].changes;
	    }
	}
    };


class PStar: public Pulse // composite pi pulse, defined 2013-8-27, length and powmax are for pi-pulse
    {
public:
    PStar(double length, double freq, double phase, double powmax) :  //"phase" is not used,
    //Pulse(1+4*4*Time2Tics(length))
    Pulse(1+Time2Tics(4*4*length))   //2014-5-7
	{
    //unsigned long ticsPart=4*Time2Tics(length);
    unsigned long ticsPart=Time2Tics(4*length); //2014-5-7
    AD9852Reg registers;
    	// Set control register values (only those that vary from default values)
    	//                                    Bits	Function                       Default  Reason for change
    	registers.CtrlReg.OSKEn    = 1; //     5	OSK enable                         0    Enable amplitude control
    	registers.CtrlReg.OSKInt   = 0;
    	registers.CtrlReg.IOUpClk  = 0; //     8	IO update clock in/out             0    Turn on!
    	// Set mode to single tone
    	registers.CtrlReg.Mode[0]  = 0;
    	registers.CtrlReg.Mode[1]  = 0;
    	registers.CtrlReg.Mode[2]  = 0; //   9-11	Output operating mode             000   single tone mode
    	registers.CtrlReg.PLLMult  = REFMULT;
    	registers.CtrlReg.PLLRange = 1;
    	registers.CtrlReg.ClrAcc1 = 0; // Don't reset accumulators
    	registers.CtrlReg.ClrAcc = 0; // Don't reset accumulators
    	registers.UpdateCtrlReg(); //   Must do this each time the control registers change

    	registers.SetFreq1(Hz2FreqWord(freq)); // initial frequency
    	registers.SetPhaseAdj1(Phase2PhaseWord(phase)); // Set phase

    	cout<<"phase is "<<phase<<"pi"<<endl;
    	datap[0] = registers;
    	writep[0] = DDSIOWriteReg(datap[0]);

    		 // Manually write all of the data:
    		 // Frequency:
    		 writep[0].Words[0] = DDSIOWord(DIP, IOLOAD, 0, 0x04, datap[0].Raw().data[0x04], 0, 1);
    		 writep[0].Words[1] = DDSIOWord(DIP, IOLOAD, 0, 0x05, datap[0].Raw().data[0x05], 1, 1);
    		 writep[0].Words[2] = DDSIOWord(DIP, IOLOAD, 0, 0x06, datap[0].Raw().data[0x06], 2, 1);
    		 writep[0].Words[3] = DDSIOWord(DIP, IOLOAD, 0, 0x07, datap[0].Raw().data[0x07], 3, 1);
    		 writep[0].Words[4] = DDSIOWord(DIP, IOLOAD, 0, 0x08, datap[0].Raw().data[0x08], 4, 1);
    		 writep[0].Words[5] = DDSIOWord(DIP, IOLOAD, 0, 0x09, datap[0].Raw().data[0x09], 5, 1);
    		 // Power:
    		 writep[0].Words[6] = DDSIOWord(DIP, IOLOAD, 0, 0x21, datap[0].Raw().data[0x21], 6, 1);
    		 writep[0].Words[7] = DDSIOWord(DIP, IOLOAD, 0, 0x22, datap[0].Raw().data[0x22], 7, 1);
    		 // Control bits:
    		 writep[0].Words[8] = DDSIOWord(DIP, IOLOAD, 0, 0x1d, datap[0].Raw().data[0x1d], 8, 1);
    		 writep[0].Words[9] = DDSIOWord(DIP, IOLOAD, 0, 0x1e, datap[0].Raw().data[0x1e], 9, 1);
    		 writep[0].Words[10] = DDSIOWord(DIP, IOLOAD, 0, 0x1f, datap[0].Raw().data[0x1f], 10, 1);
    		 writep[0].Words[11] = DDSIOWord(DIP, IOLOAD, 0, 0x20, datap[0].Raw().data[0x20], 11, 1);
    		 writep[0].Words[12] = DDSIOWord(DIP, IOLOAD, 0, 0x00, datap[0].Raw().data[0x00], 12, 1); //write phase
    		 writep[0].Words[13] = DDSIOWord(DIP, IOLOAD, 0, 0x01, datap[0].Raw().data[0x01], 13, 1); //write phase
    		 //writep[0].Words[12] = DDSIOWord(DIP, IOLOAD, 0, 0x23, 0, 12, 1);
    		 //writep[0].Words[13] = DDSIOWord(DIP, IOLOAD, 0, 0x23, 0, 13, 1);
    		 writep[0].Words[14] = DDSIOWord(DIP, IOLOAD, 0, 0x23, 0, 14, 1);
    		 //writep[0].Words[14] = DDSIOWord(DIP, IOLOAD, 0, 0x1f, 0, 14, 1);
    		 writep[0].Words[15] = DDSIOWord(DIP, IOUPDATE, 0, 0x23, 0, 15, 1); // force to write the mode code (since it is zero by default)
    		 writep[0].changes = 16;

        // First pulse (pi/2),
	for (unsigned int ii = 1; ii < ticsPart+1; ii++)
	    {
	    double power;
	    power = powmax * pow(0.42 - 0.5 * cos(2.0 * PI * ii
		    / ((double) ticsPart )) + 0.08 * cos(4.0 * PI * ii
		    / ((double) ticsPart )),2); // power is amplitude squared

	    //power=1.0;  // check, 2011-11-4

	    registers.SetOSKMult(Pow2AmpWord(power)); // set amplitude
	    registers.Time = ii;

	    datap[ii] = registers; // parse the registers and store

	    if(ii==1){
	    writep[ii].Words[0] = DDSIOWord(DIP, IOLOAD, 0, 0x23, 0, 0, 1); // keep timing right
	    writep[ii].Words[1] = DDSIOWord(DIP, IOLOAD, 0, 0x23, 0, 1, 1); //
	    writep[ii].Words[2] = DDSIOWord(DIP, IOLOAD, 0, 0x21,  datap[ii].Raw().data[0x21], 2, 1);
	    writep[ii].Words[3] = DDSIOWord(DIP, IOUPDATE, 0, 0x22,datap[ii].Raw().data[0x22], 3, 1);
	    writep[ii].changes = 4;}
	    else{
            writep[ii].Words[0] = DDSIOWord(DIP, IOLOAD, 0, 0x21,datap[ii].Raw().data[0x21], 0, 1);
	    writep[ii].Words[1] = DDSIOWord(DIP, IOUPDATE, 0, 0x22,datap[ii].Raw().data[0x22], 1, 1);
	    writep[ii].changes = 2;
	    }
	    }

        // Second pulse (Pi)  power: scaled, phase:1/2 pi
	for (unsigned int ii = ticsPart+1; ii < 3*ticsPart+1; ii++)
	    {
	    double power;
	    double scaleFactor = 3.88349514563; //4-26-2014  //9.0279377;//6.43377;  //(to account for the power imbalance in driving different transitions and matrix elements difference)
	    //double scaleFactor =  3.16075767621;  // 5-20-2014, not good
	    //scaleFactor=1.0/scaleFactor;
	    power = scaleFactor*powmax * pow(0.42 - 0.5 * cos(2.0 * PI * (ii- ticsPart)
		    / ((double)  ticsPart )) + 0.08 * cos(4.0 * PI * (ii- ticsPart)
		    / ((double)  ticsPart )),2); // power is amplitude squared

	    //power=1.0;  // check, 2011-11-4

	    registers.SetOSKMult(Pow2AmpWord(power)); // set amplitude
	    registers.Time = ii;

	    datap[ii] = registers;

	    if(ii == ticsPart+1)
		{
		writep[ii].Words[0] = DDSIOWord(DIP, IOLOAD, 0, 0x00, 0x10, 0, 1); //pi/2 phase
		writep[ii].Words[1] = DDSIOWord(DIP, IOLOAD, 0, 0x01, 0x00, 1, 1); //pi/2 phase
		writep[ii].Words[2] = DDSIOWord(DIP, IOLOAD, 0, 0x21,datap[ii].Raw().data[0x21], 2, 1);
		writep[ii].Words[3] = DDSIOWord(DIP, IOUPDATE, 0, 0x22, datap[ii].Raw().data[0x22], 3, 1);
		writep[ii].changes = 4; // assume that both amplitude registers change, to keep timing same
		}
	    else
		{
		writep[ii].Words[0] = DDSIOWord(DIP, IOLOAD, 0, 0x21,datap[ii].Raw().data[0x21], 0, 1);
		writep[ii].Words[1] = DDSIOWord(DIP, IOUPDATE, 0, 0x22,datap[ii].Raw().data[0x22], 1, 1);
		writep[ii].changes = 2; // assume that both amplitude registers change, to keep timing same
		}

	    }


        // Third pulse pulse, power: 1/4, phase: 0 pi (absolute phase)
	for (unsigned int ii = 3*ticsPart+1; ii < 4*ticsPart+1; ii++)
	    {
	    double power;

	    power = powmax * pow(0.42 - 0.5 * cos(2.0 * PI * (ii- 2*ticsPart)
		    / ((double) ticsPart )) + 0.08 * cos(4.0 * PI * (ii- 2*ticsPart)
		    / ((double) ticsPart )),2); // power is amplitude squared

	    //power=1.0;  // check, 2011-11-4

	    registers.SetOSKMult(Pow2AmpWord(power)); // set amplitude
	    registers.Time = ii;

	    datap[ii] = registers;

	    if(ii==3*ticsPart+1)
		{
		writep[ii].Words[0] = DDSIOWord(DIP, IOLOAD, 0, 0x00, 0x00, 0, 1); //0 phase
		writep[ii].Words[1] = DDSIOWord(DIP, IOLOAD, 0, 0x01, 0x00, 1, 1); //0 phase
		writep[ii].Words[2] = DDSIOWord(DIP, IOLOAD, 0, 0x21,datap[ii].Raw().data[0x21], 2, 1);
		writep[ii].Words[3] = DDSIOWord(DIP, IOUPDATE, 0, 0x22, datap[ii].Raw().data[0x22], 3, 1);
		writep[ii].changes = 4; // assume that both amplitude registers change, to keep timing same
		}
	    else
		{
		writep[ii].Words[0] = DDSIOWord(DIP, IOLOAD, 0, 0x21,datap[ii].Raw().data[0x21], 0, 1);
		writep[ii].Words[1] = DDSIOWord(DIP, IOUPDATE, 0, 0x22,datap[ii].Raw().data[0x22], 1, 1);
		writep[ii].changes = 2; // assume that both amplitude registers change, to keep timing same
		}
	    }
	// Count data words:
	ios = 0;
	for (unsigned int ii = 0; ii < tics; ii++)
	    {
	    ios += writep[ii].changes;
	    }
	}
    };
#endif //wrapper
