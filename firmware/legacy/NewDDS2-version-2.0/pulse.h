// pulse.cpp
// definitions of pulse classes

#ifndef PULSE_H_
#define PULSE_H_

#ifndef CONVERSIONS_H_
#include "conversions.h"
#endif

#ifndef AD9852DATA_H_
#include "ad9852data.h"
#endif

// pulse class contains basic description of a pulse


class Pulse
// This is the parent of the other pulse classes.
// Probably no reason to ever use this directly.
// Constructor: Pulse pulse (double length); length is in seconds
    {
    // data members
    /*
     unsigned __int64 f1; // Frequency1 in units of EPSF (only 40 bits used)
     unsigned __int64 f2; // Frequency2 in units of EPSF (only 40 bits used)
     unsigned __int64 df; // Delta f word in units of EPSF (only 40 bits used)
     char kind; // type of pulse
     */
private:
   // DDSIOWord * comp;  // pointer to compressed DDSIO data
public:
    AD9852Reg * datap; // Pointer to data, TODO: would AD985REG be better here?
    DDSIOWriteReg * writep; // Pointer to write form
    unsigned int ios; // number of io operations
    unsigned long tics; // length of pulse in clock tics

    // methods
    double Length(void) // length of pulse in seconds
	{
	return ((double) tics / INTCLOCK);

	}
    /*void SetLength(double length) // Set length in s
	{
	tics = (unsigned long) floor(length * INTCLOCK);
	}*/
    /*void DDSIOWriteReg DDSIO()
     {
     return;
     };*/
    Pulse() // default constructor has length 1 tic (should I just throw an error here?)
	{
	tics = 1;
	datap = new AD9852Reg[1];
	writep = new DDSIOWriteReg[1];
	//comp = NULL;
	ios = writep[1].changes;
#ifdef _DEBUG
	cout << "Pulse class default constructor" << endl;
#endif
	}
    Pulse(unsigned long ticlength) // constructor for specified number of tics
	{
	cout << "Entering Pulse" << endl;
	if (ticlength > MAXSAMPLES)
	    {
		tics = 0; // If tics = 0 -> error
		datap = 0; // pointer NULL
		writep = 0; // pointer NULL
		ios = 0;
		cout<<"Pulse too long!! The output of ticlength ="<<ticlength<<endl;
	    }
	else
	    {
	tics = ticlength;

	datap = new AD9852Reg[tics];
	writep = new DDSIOWriteReg[tics]; // note that in general this can be longer than datap
	ios = 0;
	for (unsigned int ii=0;ii<tics;ii++)
	    {
		ios += writep[ii].changes;
	    }
#ifdef _DEBUG
	cout << "Pulse class integer constructor: tics = " << dec << tics << endl;
#endif
	    }
	}
    ~Pulse() // destructor
	{
	delete[] datap; datap = NULL; // delete data and null out pointers
	delete[] writep; writep = NULL;
	//delete[] comp; comp = NULL;
	}
    Pulse operator+(const Pulse & second)  // + will concatenate pulses
	{
	    unsigned long newtics;
	    newtics = tics + second.tics;
	    Pulse outpulse(newtics);
	    for (unsigned long ii=0;ii<tics;ii++)
		{
		    outpulse.datap[ii] = datap[ii];
		    outpulse.writep[ii] = writep[ii];
		}
	    outpulse.datap[tics] = second.datap[0];
	    outpulse.writep[tics] = DDSIOWriteReg(second.datap[0],datap[tics-1]);
	    for (unsigned long ii=0;ii<second.tics+1;ii++)
		{
		    outpulse.datap[ii+tics] = second.datap[ii];
		    outpulse.writep[ii+tics] = second.writep[ii];
		}
	    outpulse.ios = 0;
	    for (unsigned int ii=0;ii<outpulse.tics;ii++)
		{
		    outpulse.ios += outpulse.writep[ii].changes;
		}
	    return outpulse ;
	}
    Pulse operator*(unsigned long mult) // Scalar multiplication = duplication
	{
	    Pulse outpulse(tics*mult);
	    for (unsigned long ii=0;ii<mult;ii++)
		{
		for (unsigned long jj=0;jj<tics;jj++)
		    {
			outpulse.datap[ii*tics+jj] = datap[jj];
			outpulse.writep[ii*tics+jj] = writep[jj];
		    }
		if (ii != 0)
		    {
			outpulse.writep[ii*tics] = DDSIOWriteReg(datap[0],datap[tics-1]); // bridge the gaps
		    }
		}
	    outpulse.ios = 0;
	    for (unsigned int ii=0;ii<outpulse.tics;ii++)
		{
		    outpulse.ios += outpulse.writep[ii].changes;
		}
	    return(outpulse);
	}
    Pulse operator=(Pulse A)
	{
	Pulse output;
	output.ios=A.ios;
	output.tics=A.tics;
	output.datap = new AD9852Reg[tics];
	output.writep = new DDSIOWriteReg[tics]; // note that in general this can be longer than datap
       for(unsigned int ii=0; ii<tics;ii++)
	   {
	   output.datap[ii]=A.datap[ii];
	   output.writep[ii]=A.writep[ii];
	   }
	return output;
	}


    DDSIOWord * Compressed() // change output to DDSIOWord[]
	    {
		DDSIOWord * comp;
		//cout << "ios=" << ios <<endl;
		comp = new DDSIOWord[ios];
		unsigned int iocount = 0;
		//cout <<"test"<< endl;

		for (unsigned int ii=0;ii<tics;ii++)
		    {
			for (unsigned char jj=0;jj<writep[ii].changes;jj++)
			    {
				if (iocount > ios)
				    {
					cout <<"Error: iocount too big in Compressed()"<< endl;
				    }
				comp[iocount].RawIO = writep[ii].Words[jj].RawIO ;
				comp[iocount].Time = ii;
				iocount++;
			    }
		    }
#ifdef _DEBUG
		cout << "Compressed() iocount: " << dec << iocount << endl;
#endif
		return comp;
	    }
    };
class PConstant: public Pulse // Constant "pulse"
    {
public:

    PConstant(double length, double freq, double amp) :
	Pulse(Time2Tics(length))
	{
	AD9852Reg registers;

	//                                    Bits	Function                       Default  Reason for change
	registers.CtrlReg.OSKEn = 1; //     5	OSK enable                         0    Enable amplitude control
	registers.CtrlReg.OSKInt=0;
	registers.CtrlReg.IOUpClk = 0; //     8	IO update clock in/out             0    Turn on!
	registers.CtrlReg.Mode[0] = 0;
	registers.CtrlReg.Mode[1] = 0;
	registers.CtrlReg.Mode[2] = 0; //   9-11	Output operating mode             000 (Single tone)
	registers.CtrlReg.ClrAcc = 0; //    14	Clear Accumulators                 0    Reset phase
	registers.CtrlReg.PLLMult=0x1E;
	registers.UpdateCtrlReg(); //   Must do this each time the control registers change

	registers.SetFreq1(Hz2FreqWord(freq)); // set frequency
	registers.SetOSKMult(Pow2AmpWord(amp)); // set amplitude

	datap[0] = registers; // parse the registers and store
	writep[0] = DDSIOWriteReg(datap[0]);

	for (unsigned int ii = 1; ii < tics; ii++) // loop to generate AD9852Raw data (change amp, freq inside this loop)
	    {
	  //  writep[ii] = DDSIOWriteReg(); // initialize
	    writep[ii].changes = 0;  // change this to be 0 for a cut-off
	    writep[ii].Words[0] = DDSIOWord(DIP,IOLATCH,0,0x23,0,ii);  // do nothing
	    writep[ii].Words[1] = DDSIOWord(DIP,IOLATCH,0,0x23,0,ii);  // do nothing
	    datap[ii] = datap[0]; // copy value from t=0
	    }
	ios = 0;
	for (unsigned int ii=0;ii<tics;ii++)
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
    PSquare(double length, double freq, double amp) :
	Pulse(Time2Tics(length) + 1)
	{
	// inherited values: tics, datap
	Frequency = freq;
	Amplitude = amp;
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
	registers.SetOSKMult(Pow2AmpWord(amp)); // set amplitude
	datap[0] = registers; // parse the registers and store
	writep[0] = DDSIOWriteReg(datap[0]);

	for (unsigned int ii = 1; ii < (tics - 1); ii++) // loop to generate AD9852Raw data (change amp, freq inside this loop)
	    {
		writep[ii] = DDSIOWriteReg(); // initialize
		writep[ii].changes = 1;
		writep[ii].Words[0] = DDSIOWord(DIP,IOLATCH,0,0,0,ii);  // do nothing
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
class PBlackman: public Pulse // Blackman "pulse" Typical Chirp Mode
    {
public:
    //double Frequency;
    //double Power;
    PBlackman(double length, double freq, double maxpow) :
	//Pulse(Time2Tics(length/2)) // assume 2 io cycles per amplitude why???
          Pulse(Time2Tics(length))
	{
	    AD9852Reg registers;
	    // Set control register values (only those that vary from default values)
	    //                                    Bits	Function                       Default  Reason for change
	    registers.CtrlReg.OSKEn = 1; //     5	OSK enable                         0    Enable amplitude control
	    registers.CtrlReg.OSKInt=0;
	    registers.CtrlReg.IOUpClk = 0; //     8	IO update clock in/out             0    Turn on!
	    registers.CtrlReg.Mode[0] = 1;
	    registers.CtrlReg.Mode[1] = 1;
	    registers.CtrlReg.Mode[2] = 0; //   9-11	Output operating mode             000   chirp mode
	    //registers.CtrlReg.ClrAcc = 1; //    14	Clear Accumulators                 0    Reset phase
	    registers.CtrlReg.PLLMult=0x1E;
	    registers.CtrlReg.PLLRange=1;
	    registers.UpdateCtrlReg(); //   Must do this each time the control registers change
	    // Set data register values (other than freq and amp)
	    //registers.SetPhaseAdj1(0);
	    //registers.SetPhaseAdj2(0);
	    //registers.SetFreq1  (set this inside the loop)
	    //registers.SetFreq2(0);
	    //registers.SetDeltaFreq(0);
	    //registers.SetUpdateClk
	    //registers.SetRampClk
	    //registers.SetOSKMult   (set inside the loop)
	    //registers.SetOSKRamp
	    //registers.SetCtrlDAC

	    // tic = 0 case needs to set all regs
	    registers.SetFreq1(Hz2FreqWord(freq)); // initial frequency  ?? shall delete?
	    //registers.SetOSKMult(0); // initial amplitude (zero in this case)

	    datap[0] = registers;
	    writep[0] = DDSIOWriteReg(datap[0]);

	    for (unsigned int ii = 1; ii < tics; ii++) // loop to generate AD9852Raw data starting from second tic (change amp, freq inside this loop)
		{

		double amp;
		//Pulse frequency shape follows:
		//registers.SetFreq1(Hz2FreqWord(freq)); // set frequency
		// Pulse amplitude shape follows:

		//amp = Pow2Volts(maxpow) * (0.42 - 0.5 * cos(2.0 * PI * ii
		//	/ ((double) tics - 1)) + 0.08 * cos(4.0 * PI * ii
		//	/ ((double) tics - 1)));


		amp=Pow2Volts(maxpow)*ii/(double)tics;  // Triangle Pulse
		registers.SetOSKMult(Volts2AmpWord(amp)); // set amplitude
		registers.Time = ii;

		datap[ii] = registers; // parse the registers and store



		writep[ii].Words[0]= DDSIOWord(DIP, IOLOAD, 0, 0x21, datap[ii].Raw().data[0x21], 0);
		writep[ii].Words[1]= DDSIOWord(DIP, IOLOAD, 0, 0x22, datap[ii].Raw().data[0x22], 1);
		writep[ii].Words[7]= DDSIOWord(DIP, IOUPDATE, 0, 0x23, datap[ii].Raw().data[0x23], 7);

		//writep[ii] = DDSIOWriteReg(datap[ii], datap[ii-1]); // only record changes
		// HACK:
		writep[ii].changes=8;  // assume that both amplitude registers change, to keep timing sane
		}

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

class PInit: public Pulse // Placeholder pulse to initialize DDS data bus
// length will always be 1.
    {
public:
    PInit() :
	Pulse((unsigned long) 1) // Syntax is OK, despite editor complaints
	{
          writep[0].changes = 1;
          ios = 1;
          writep[0].Words[0] = DDSIOWord(DIP,IORESET,0,0x23,0,0);  // call master reset
          }
    };

class PEnd: public Pulse // To End a pulse
    {
public:
    PEnd() :
	Pulse((unsigned long) 1)
	{
                        writep[0].Words[0] = DDSIOWord(DIP, IOLOAD, 0, 0x04, 0, 0);
                        writep[0].Words[1] = DDSIOWord(DIP, IOLOAD, 0, 0x05, 0, 1);
                        writep[0].Words[2] = DDSIOWord(DIP, IOLOAD, 0, 0x06, 0, 2);
                        writep[0].Words[3] = DDSIOWord(DIP, IOLOAD, 0, 0x07, 0, 3);
                        writep[0].Words[4] = DDSIOWord(DIP, IOLOAD, 0, 0x08, 0, 4);
                        writep[0].Words[5] = DDSIOWord(DIP, IOLOAD, 0, 0x09, 0, 5);
                        writep[0].Words[6] = DDSIOWord(DIP, IOLOAD, 0, 0x21, 0, 6);
        	    	writep[0].Words[7] = DDSIOWord(DIP, IOLOAD, 0, 0x22, 0, 7);
        	    	writep[0].Words[8] = DDSIOWord(DIP, IOUPDATE, 0, 0x23, 0, 8);
        	        ios = 9;
                       writep[0].changes = 9;
	}
    };


class PAdiabatic: public Pulse // adiabatic sweeping for now, just do a linear chirp
    {
public:
    //double Frequency;
    //double Power;
    PAdiabatic(double length, double freq, double HSR, double maxpow) : //HSR Half frequency Sweeping Range
	//Pulse(Time2Tics(length/2)) // assume 2 io cycles per amplitude why???
          Pulse(Time2Tics(length))
	{
	    AD9852Reg registers;
	    // Set control register values (only those that vary from default values)
	    //                                    Bits	Function                       Default  Reason for change
	    registers.CtrlReg.OSKEn = 1; //     5	OSK enable                         0    Enable amplitude control
	    registers.CtrlReg.OSKInt=0;
	    registers.CtrlReg.IOUpClk = 0; //     8	IO update clock in/out             0    Turn on!
	    registers.CtrlReg.Mode[0] = 1;
	    registers.CtrlReg.Mode[1] = 1;
	    registers.CtrlReg.Mode[2] = 0; //   9-11	Output operating mode             000   chirp mode
	    //registers.CtrlReg.ClrAcc = 1; //    14	Clear Accumulators                 0    Reset phase
	    registers.CtrlReg.PLLMult=0x1E;
	    registers.CtrlReg.PLLRange=1;
	    registers.UpdateCtrlReg(); //   Must do this each time the control registers change
	    // Set data register values (other than freq and amp)
	    //registers.SetPhaseAdj1(0);
	    //registers.SetPhaseAdj2(0);
	    //registers.SetFreq1  (set this inside the loop)
	    //registers.SetFreq2(0);
	    //registers.SetDeltaFreq(0);
	    //registers.SetUpdateClk
	    //registers.SetRampClk
	    //registers.SetOSKMult   (set inside the loop)
	    //registers.SetOSKRamp
	    //registers.SetCtrlDAC

	    // tic = 0 case needs to set all regs
	    registers.SetFreq1(Hz2FreqWord(freq-HSR)); // Staring frequency, put in the loop?

	    //registers.SetOSKMult(0); // initial amplitude (zero in this case)
	    registers.SetRampClk(RR2Word(1.0/RAMPRATE));
	    datap[0] = registers;
	    writep[0] = DDSIOWriteReg(datap[0]);

	    for (unsigned int ii = 1; ii < tics; ii++) // loop to generate AD9852Raw data starting from second tic (change amp, freq inside this loop)
		{
		double amp;
		double chirp;
		registers.Time = ii;

                amp=Pow2Volts(maxpow)*pow(sin(PI*ii/tics),2);
		registers.SetOSKMult(Volts2AmpWord(amp)); // set amplitude
		//registers.SetOSKMult(Volts2AmpWord(Pow2Volts(maxpow)));  // constant amplitude

		chirp= Freq1(freq-HSR,HSR,(double)ii/tics)-Freq1(freq-HSR,HSR,(double)(ii-1)/tics);
		//chirp=((double)freq-HSR+ii*2*HSR/tics)-((double)freq-HSR+(ii-1)*2*HSR/tics);  // linear chirp
          	chirp=(double)chirp/(length/tics*RAMPRATE); //???

		registers.SetDeltaFreq(Hz2FreqWord(chirp)); // set frequency
                datap[ii] = registers; // parse the registers and store

                writep[ii].Words[0]= DDSIOWord(DIP, IOLOAD, 0, 0x21, datap[ii].Raw().data[0x21], 0);
                writep[ii].Words[1]= DDSIOWord(DIP, IOLOAD, 0, 0x22, datap[ii].Raw().data[0x22], 1);
                writep[ii].Words[2]= DDSIOWord(DIP, IOLOAD, 0, 0x10, datap[ii].Raw().data[0x10], 2);
                writep[ii].Words[3]= DDSIOWord(DIP, IOLOAD, 0, 0x11, datap[ii].Raw().data[0x11], 3);
                writep[ii].Words[4]= DDSIOWord(DIP, IOLOAD, 0, 0x12, datap[ii].Raw().data[0x12], 4);
                writep[ii].Words[5]= DDSIOWord(DIP, IOLOAD, 0, 0x13, datap[ii].Raw().data[0x13], 5);
                writep[ii].Words[6]= DDSIOWord(DIP, IOLOAD, 0, 0x14, datap[ii].Raw().data[0x14], 6);
                writep[ii].Words[7]= DDSIOWord(DIP, IOUPDATE, 0, 0x15, datap[ii].Raw().data[0x15], 7);

		//writep[ii] = DDSIOWriteReg(datap[ii], datap[ii-1]); // only record changes

		writep[ii].changes=8;  // assume that both amplitude registers change, to keep timing sane
		}

	    ios = 0;
	    for (unsigned int ii=0;ii<tics;ii++)
		{
		    ios += writep[ii].changes;
		}
	    }

	};
#endif //wrapper
