// pulse.cpp
// definitions of pulse classes

#ifndef PULSE_H_
#define PULSE_H_


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

	}

    Pulse(unsigned long ticlength) // constructor for specified number of tics
	{
	if (ticlength > MAXSAMPLES)
	    {
	    tics = 0; // If tics = 0 -> error
	    datap = 0; // pointer NULL
	    writep = 0; // pointer NULL
	    ios = 0;
	    cout << "Pulse too long!! The output of ticlength =" << ticlength
		    << endl;
	    }
	else
	    {
	    tics = ticlength;

	    datap = new AD9852Reg[tics];
	    writep = new DDSIOWriteReg[tics]; // note that in general this can be longer than datap
	    ios = 0;
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

class PEnd2: public Pulse // To End a pulse
    {
public:
    PEnd2() :
	Pulse((unsigned long) 1)
	{
	// TODO: Rewrite using registers
	// Set frequency = 0
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

class PConstant: public Pulse // Constant "pulse"
    {
public:

    PConstant(double length, double freq, double power) :
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
	    registers.CtrlReg.ClrAcc  = 0; //    14	Clear Accumulators                 0    Reset phase
	    registers.CtrlReg.PLLMult = REFMULT;
	    registers.UpdateCtrlReg(); //   Must do this each time the control registers change
	    registers.SetFreq1(Hz2FreqWord(freq)); // set frequency
	    //registers.SetFreq2(Hz2FreqWord(freq)); // set frequency
	    //cout << "OSKMult = " << dec << Pow2AmpWord(power) << endl;
	    registers.SetOSKMult(Pow2AmpWord(power)); // constant amplitude
	    datap[0] = registers; // parse the registers and store
	    }


	 writep[0] = DDSIOWriteReg(datap[0]);
	 if (writep[0].Words[7].RawIO==0){
	 writep[0].Words[7] = DDSIOWord(DIP, IOLOAD, 0, 0x23, 0, 10, 1);}

	 writep[0].Words[8] = DDSIOWord(DIP, IOLOAD, 0, 0x21, datap[0].Raw().data[0x21], 8, 1);
	 writep[0].Words[9] = DDSIOWord(DIP, IOLOAD, 0, 0x22, datap[0].Raw().data[0x22], 9, 1);
	 writep[0].Words[10] = DDSIOWord(DIP, IOLOAD, 0, 0x23, 0, 10, 1);
	 writep[0].Words[11] = DDSIOWord(DIP, IOLOAD, 0, 0x23, 0, 11, 1);
	 writep[0].Words[12] = DDSIOWord(DIP, IOLOAD, 0, 0x23, 0, 12, 1);
	 writep[0].Words[13] = DDSIOWord(DIP, IOLOAD, 0, 0x23, 0, 13, 1);
	 writep[0].Words[14] = DDSIOWord(DIP, IOLOAD, 0, 0x23, 0, 14, 1);
	 writep[0].Words[15] = DDSIOWord(DIP, IOUPDATE, 0, 0x1f, 0, 15, 1); // force to write the mode code (since it is zero by default)

	 writep[0].changes = 16;
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
class PBlackman: public Pulse // Blackman "pulse"， sweep amp only.
    {
public:
    PBlackman(double length, double freq, double powmax) :
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
		 writep[0].Words[8] = DDSIOWord(DIP, IOLOAD, 0, 0x21, datap[0].Raw().data[0x21], 8, 1);
		 writep[0].Words[9] = DDSIOWord(DIP, IOLOAD, 0, 0x22, datap[0].Raw().data[0x22], 9, 1);
		 writep[0].Words[10] = DDSIOWord(DIP, IOLOAD, 0, 0x23, 0, 10, 1);
		 writep[0].Words[11] = DDSIOWord(DIP, IOLOAD, 0, 0x23, 0, 11, 1);
		 writep[0].Words[12] = DDSIOWord(DIP, IOLOAD, 0, 0x23, 0, 12, 1);
		 writep[0].Words[13] = DDSIOWord(DIP, IOLOAD, 0, 0x23, 0, 13, 1);
		 writep[0].Words[14] = DDSIOWord(DIP, IOLOAD, 0, 0x23, 0, 14, 1);
		 writep[0].Words[15] = DDSIOWord(DIP, IOUPDATE, 0, 0x1f, 0, 15, 1); // force to write the mode code (since it is zero by default)

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
	registers.CtrlReg.PLLRange = 1;
	registers.CtrlReg.ClrAcc1 = 0; // reset accumulator
	//registers.CtrlReg.ClrAcc = 1;
	registers.UpdateCtrlReg(); //   Must do this each time the control registers change
	// Set data register values (other than freq and amp)
	//registers.SetPhaseAdj1(0);
	//registers.SetPhaseAdj2(0);

	registers.SetFreq1(Hz2FreqWord(freq - HSR)); // Starting frequency
	registers.SetRampClk(RR2Word(1.0 / RAMPRATE));
	datap[0] = registers;
	writep[0] = DDSIOWriteReg(datap[0]);
	registers.CtrlReg.ClrAcc1 = 0; // reset accumulator
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

/*class PPiStar: public Pulse // PiStar pulse sequence
 {
 // need to create a sequence of 3 pulses with appropriate pause between
 // Pi/2 wait Pi wait Pi/2
 public:
 double RabiFreq;
 };*/

#endif //wrapper

