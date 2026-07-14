// data classes related to AD9852 registers and the UT DDS board

#ifndef AD9852DATA_H_
#define AD9852DATA_H_


class DDSIOWord
    { // One I/O load for the DDS
public:
    uint32_t RawIO;
    uint32_t Time; // time label
    // layout of RawIO matches bus on DDS board
    // bits	hex mask	purpose
    // 0-5	0x00003F	register address
    // 6-7	0x0000C0	Key mode
    // 8-15	0x00FF00	Data
    // 16-17	0x030000	IO options
    // 18-23	0xFC0000	Board address (DIP setting)

    unsigned char ReadRegAddress()
	{
	return (RawIO & 0x0000003F);
	}

    unsigned char ReadRegValue()
	{
	return ((RawIO & 0x0000FF00) >> 8);
	}

    unsigned char ReadKeyMode()
	{
	return ((RawIO & 0x000000C0) >> 6);
	}

    unsigned char ReadIOMode()
	{
	return ((RawIO & 0x00030000) >> 16);
	}

    unsigned char ReadBoardAddress()
	{
	return ((RawIO & 0x00FC0000) >> 18);
	}

    void SetRegAddress(const unsigned char val)
	{
	// TODO: check range
	RawIO = (RawIO & ~0x0000003F) + (uint32_t) val;
	return;
	}

    void SetRegValue(const unsigned char val)
	{
	// TODO: check range
	RawIO = (RawIO & ~0x0000FF00) + ((uint32_t) val << 8);
	return;
	}

    void SetKeyMode(const unsigned char val)
	{
	// TODO: check range
	RawIO = (RawIO & ~0x000000C0) + ((uint32_t)val << 6);
	return;
	}

    void SetIOMode(const unsigned char val)
	{
	// TODO: check range
	RawIO = (RawIO & ~0x00030000) + ((uint32_t)val << 16);
	return;
	}

    void SetBoardAddress(const unsigned char val)
	{
	// TODO: check range
	RawIO = (RawIO & ~0x0000003F) + ((uint32_t)val << 18);
	return;
	}

    void SetMask(const unsigned char val)
  	{
  	// TODO: check range
  	RawIO = (RawIO & ~0x01000000) + ((uint32_t)val << 24);
  	return;
  	}

    DDSIOWord() // default constructor
	{
	RawIO = 0;
	Time = 0;
	}

    DDSIOWord(const unsigned char boardadd, const unsigned char iomode,
	    const unsigned char keymode, const unsigned char regadd,
	    const unsigned char regval, const uint32_t time, const unsigned char mask)
    // Preferred constructor
    // iomode = 0 (reset), 1 (load), 2 (load and output), 3 (do nothing)
	{
	// TODO: check ranges (maybe do this by explicit calls to "Set" methods above?)
	RawIO	=  (uint32_t) regadd
		+ ((uint32_t) keymode  << 6)
		+ ((uint32_t) regval   << 8)
		+ ((uint32_t) iomode   << 16)
		+ ((uint32_t) boardadd << 18)
		+((uint32_t) mask << 24);
	Time = time;
	}

    void Print() // Print value of Word to stdout (for debug)
	{
	    cout << "Reg " << hex << int(ReadRegAddress()) << ", Value " << hex << int(ReadRegValue());
	    cout << ", IO Mode " << dec << int(ReadIOMode()) << endl;
	    return;
	}
    };

class AD9852Raw
    {
public:
    unsigned char data[0x28]; // one char for each register
    uint32_t Time; // time label
    uint64_t Compare(const AD9852Raw raw) // temp has set bits for registers that are equal (40 regs total)
	{
	uint64_t temp = 0;
	bool test = 0;
	for (unsigned char ii = 0; ii < 0x28; ii++)
	    {
	    test = (data[ii] == raw.data[ii]); // TRUE if registers equal
	    temp += ((uint64_t) test) << ii;
	    }
	return (temp);
	}
    void Print()
	{
	    for (unsigned int i = 0; i<0x28; ++i)
		{
		    cout << "Reg " << hex << i << ", Value " << hex << data[i] << endl;
		}
	    return;
	}
    };

class AD9852Reg
    {
    //                       Bytes  Purpose
    unsigned char RegPhaseAdj1[2]; // 00-01	Phase Adj 1
    unsigned char RegPhaseAdj2[2]; // 02-03	Phase Adj 2
    unsigned char RegFreq1    [6]; // 04-09	Frequency Word 1
    unsigned char RegFreq2    [6]; // 0A-0F	Frequency Word 2
    unsigned char RegDeltaFreq[6]; // 10-15	Delta frequency
    unsigned char RegUpdateClk[4]; // 16-19	Update clock
    unsigned char RegRampClk  [3]; // 1A-1C	Ramp rate clock
    unsigned char RegCtrlReg  [4]; // 1D-20	Control Registers
    unsigned char RegOSKMult  [2]; // 21-22	Output shaped key multiplier (amplitude)
    unsigned char RegDontCare [2]; // 23-24  (Place holder)
    unsigned char RegOSKRamp     ; // 25     Output shaped key ramp rate
    unsigned char RegCtrlDAC  [2]; // 26-27  Control DAQ

public:
    // Define control register
    uint32_t Time; // time label
    class CtrlRegister // Control register
	{
    public:
	//                          Bit(octal)   Purpose                         Default
	bool SDO; //                000    serial port SDO, not used,         0
	bool SSB; //                001    serial port directio, not used,    0
	bool Res2; //               002    reserved,                          0
	bool Res3; //               003    reserved                           0
	bool OSKInt; //             004    OSK internal/external switch,      1
	bool OSKEn; //              005    OSK enable                         0
	bool BypassSinc; //         006    Bypass inv sinc filter,            0
	bool Res7; //               007    Reserved                           0
	bool IOUpClk; //            010    IO update clock in/out             0
	bool Mode[3]; //           011-013 Output operating mode             000
	bool Res12; //              014    reserved                           0
	bool Triangle;//            015    Triangle mode                      0
	bool ClrAcc; //             016    Clear Accumulators                 0
	bool ClrAcc1; //            017    Clear Acc 1 only                   0
	unsigned char PLLMult; //  020-024 PLL multiplier (5-bits)            4
	bool PLLBypass;//           025    PLL bypass                         1
	bool PLLRange; //           026    PLL range TRUE for > 200MHz        1
	bool Res23;//               027    reserved                           0
	bool PowDig;//              030    Power down digital                 0
	bool PowDAC;//              031    Power down DAC                     0
	bool PowCtlDAC;//           032    Power down control DAC             0
	bool Halt; //               033    Halt the AD9852                    0
	bool PowComp;//             034    Power down comparator              0
	bool Res29; //              035    reserved                           0
	bool Res30; //              036    reserved                           0
	bool Res31; //              037    reserved                           0
    public:
	CtrlRegister() // Initiate control register
	    {
	    //                    Bit   Purpose                         Default
	    SDO = 0; //            0    serial port SDO, not used,         0
	    SSB = 0; //            1    serial port directio, not used,    0
	    Res2 = 0; //           2    reserved,                          0
	    Res3 = 0; //           3    reserved                           0
	    OSKInt = 0; //         4    OSK internal/external switch,      1
	    OSKEn = 1; //          5    OSK enable                         0
	    BypassSinc = 0; //     6    Bypass inv sinc filter,            0
	    Res7 = 0; //           7    Reserved                           0
	    IOUpClk = 0; //        8    IO update clock in/out             0
	    Mode[0] = 0;
	    Mode[1] = 0;
	    Mode[2] = 0; //       9-11  Output operating mode             000
	    Res12 = 0; //          12   reserved                           0
	    Triangle = 0; //       13   Triangle mode                      0
	    ClrAcc = 0; //         14   Clear Accumulators                 0
	    ClrAcc1 = 0; //        15   Clear Acc 1 only                   0
	    PLLMult = 4; //      16-20  PLL multiplier (5-bits)            4
	    PLLBypass = 0;//       21   PLL bypass                         1
	    PLLRange = 1; //       22   PLL range TRUE for > 200MHz        1
	    Res23 = 0;//           23   reserved                           0
	    PowDig = 0;//          24   Power down digital                 0
	    PowDAC = 0;//          25   Power down DAC                     0
	    PowCtlDAC = 0;//       26   Power down control DAC             0
	    Halt = 0; //           27   Halt the AD9852                    0
	    PowComp = 0;//         28   Power down comparator              0
	    Res29 = 0; //          29   reserved                           0
	    Res30 = 0; //          30   reserved                           0
	    Res31 = 0; //          31   reserved                           0
	    }
	} CtrlReg;
    void UpdateCtrlReg() // Write CtrlReg onto RegCtrlReg (do after every change)
	{
	RegCtrlReg[3] = ((unsigned char) (CtrlReg.SDO))
		+ ((unsigned char) (CtrlReg.SSB)        << 1)
		+ ((unsigned char) (CtrlReg.OSKInt)     << 4) //    skip the reserves, since they're 0
		+ ((unsigned char) (CtrlReg.OSKEn)      << 5)
		+ ((unsigned char) (CtrlReg.BypassSinc) << 6);
	RegCtrlReg[2] = ((unsigned char) (CtrlReg.IOUpClk))
		+ ((unsigned char) (CtrlReg.Mode[0])  << 1)
		+ ((unsigned char) (CtrlReg.Mode[1])  << 2)
		+ ((unsigned char) (CtrlReg.Mode[2])  << 3)
		+ ((unsigned char) (CtrlReg.Triangle) << 5)
		+ ((unsigned char) (CtrlReg.ClrAcc)   << 6)
		+ ((unsigned char) (CtrlReg.ClrAcc1)  << 7);
	RegCtrlReg[1] = (CtrlReg.PLLMult)
		+ ((unsigned char) (CtrlReg.PLLBypass) << 5)
		+ ((unsigned char) (CtrlReg.PLLRange)  << 6);
	RegCtrlReg[0] = ((unsigned char) (CtrlReg.PowDig))
		+ ((unsigned char) (CtrlReg.PowDAC)    << 1)
		+ ((unsigned char) (CtrlReg.PowCtlDAC) << 2)
		+ ((unsigned char) (CtrlReg.Halt)      << 3)
		+ ((unsigned char) (CtrlReg.PowComp)   << 4);
	}
    // Convert this class to a RAW
    AD9852Raw Raw(void) // Convert AD9852Reg to a AD9852Raw for output
    // Does not set comopt
	{
	AD9852Raw raw;
	raw.data[0x00] = RegPhaseAdj1[0]; //
	raw.data[0x01] = RegPhaseAdj1[1]; //
	raw.data[0x02] = RegPhaseAdj2[0]; //
	raw.data[0x03] = RegPhaseAdj2[1]; //
	raw.data[0x04] = RegFreq1[0]; //
	raw.data[0x05] = RegFreq1[1]; //
	raw.data[0x06] = RegFreq1[2]; //
	raw.data[0x07] = RegFreq1[3]; //
	raw.data[0x08] = RegFreq1[4]; //
	raw.data[0x09] = RegFreq1[5]; //
	raw.data[0x0A] = RegFreq2[0]; //
	raw.data[0x0B] = RegFreq2[1]; //
	raw.data[0x0C] = RegFreq2[2]; //
	raw.data[0x0D] = RegFreq2[3]; //
	raw.data[0x0E] = RegFreq2[4]; //
	raw.data[0x0F] = RegFreq2[5]; //
	raw.data[0x10] = RegDeltaFreq[0]; //
	raw.data[0x11] = RegDeltaFreq[1]; //
	raw.data[0x12] = RegDeltaFreq[2]; //
	raw.data[0x13] = RegDeltaFreq[3]; //
	raw.data[0x14] = RegDeltaFreq[4]; //
	raw.data[0x15] = RegDeltaFreq[5]; //
	raw.data[0x16] = RegUpdateClk[0]; //
	raw.data[0x17] = RegUpdateClk[1]; //
	raw.data[0x18] = RegUpdateClk[2]; //
	raw.data[0x19] = RegUpdateClk[3]; //
	raw.data[0x1A] = RegRampClk[0]; //
	raw.data[0x1B] = RegRampClk[1]; //
	raw.data[0x1C] = RegRampClk[2]; //
	raw.data[0x1D] = RegCtrlReg[0]; //
	raw.data[0x1E] = RegCtrlReg[1]; //
	raw.data[0x1F] = RegCtrlReg[2]; //
	raw.data[0x20] = RegCtrlReg[3]; //
	raw.data[0x21] = RegOSKMult[0]; //
	raw.data[0x22] = RegOSKMult[1]; //
	raw.data[0x23] = RegDontCare[0]; //
	raw.data[0x24] = RegDontCare[1]; //
	raw.data[0x25] = RegOSKRamp; //
	raw.data[0x26] = RegCtrlDAC[0]; //
	raw.data[0x27] = RegCtrlDAC[1]; //
	raw.Time = Time;
	return (raw);
	}

    // Set Commands
    // TODO: use real units?
    void SetPhaseAdj1(const unsigned short phase)
	{
	RegPhaseAdj1[0] = char(phase & 0xFF00 >> 8); // MSB first
	RegPhaseAdj1[1] = char(phase & 0x00FF);
	}
    void SetPhaseAdj2(const unsigned short phase)
	{
	RegPhaseAdj2[0] = char(phase & 0xFF00 >> 8);
	RegPhaseAdj2[1] = char(phase & 0x00FF);
	}
    void SetFreq1(const uint64_t freq)
	{
	RegFreq1[0] = (unsigned char) ((0x00FF0000000000ULL & freq) >> 0x28);
	RegFreq1[1] = (unsigned char) ((0x0000FF00000000ULL & freq) >> 0x20);
	RegFreq1[2] = (unsigned char) ((0x000000FF000000ULL & freq) >> 0x18);
	RegFreq1[3] = (unsigned char) ((0x00000000FF0000ULL & freq) >> 0x10);
	RegFreq1[4] = (unsigned char) ((0x0000000000FF00ULL & freq) >> 0x08);
	RegFreq1[5] = (unsigned char) ((0x000000000000FFULL & freq));
	}
    void SetFreq2(const uint64_t freq)
	{
	RegFreq2[0] = (unsigned char) ((0xFF0000000000ULL & freq) >> 0x28);
	RegFreq2[1] = (unsigned char) ((0x00FF00000000ULL & freq) >> 0x20);
	RegFreq2[2] = (unsigned char) ((0x0000FF000000ULL & freq) >> 0x18);
	RegFreq2[3] = (unsigned char) ((0x000000FF0000ULL & freq) >> 0x10);
	RegFreq2[4] = (unsigned char) ((0x00000000FF00ULL & freq) >> 0x08);
	RegFreq2[5] = (unsigned char) ((0x0000000000FFULL & freq));
	}
    void SetDeltaFreq(const uint64_t freq)
	{
	RegDeltaFreq[0] = (unsigned char) ((0xFF0000000000ULL & freq) >> 0x28);
	RegDeltaFreq[1] = (unsigned char) ((0x00FF00000000ULL & freq) >> 0x20);
	RegDeltaFreq[2] = (unsigned char) ((0x0000FF000000ULL & freq) >> 0x18);
	RegDeltaFreq[3] = (unsigned char) ((0x000000FF0000ULL & freq) >> 0x10);
	RegDeltaFreq[4] = (unsigned char) ((0x00000000FF00ULL & freq) >> 0x08);
	RegDeltaFreq[5] = (unsigned char) ((0x0000000000FFULL & freq));
	}
    void SetUpdateClk(const unsigned int tic)
	{
	RegUpdateClk[0] = (unsigned char) ((0xFF000000 & tic) >> 0x18);
	RegUpdateClk[1] = (unsigned char) ((0x00FF0000 & tic) >> 0x10);
	RegUpdateClk[2] = (unsigned char) ((0x0000FF00 & tic) >> 0x08);
	RegUpdateClk[3] = (unsigned char) ((0x000000FF & tic));
	}
    void SetRampClk(const unsigned int tic)
	{
	RegRampClk[0] = (unsigned char) ((0xFF0000 & tic) >> 0x10);
	RegRampClk[1] = (unsigned char) ((0x00FF00 & tic) >> 0x08);
	RegRampClk[2] = (unsigned char) ((0x0000FF & tic));
	}
    //void SetCtrlReg   (unsigned int32_t);
    void SetOSKMult(const unsigned short mult)
	{
	RegOSKMult[0] = (unsigned char) ((mult & 0xFF00) >> 8);
	RegOSKMult[1] = (unsigned char) (mult & 0x00FF);
	}
    //void SetDontCare  (unsigned   short dc);
    void SetOSKRamp(const unsigned char ramp)
	{
	RegOSKRamp = ramp;
	}
    void SetCtrlDAC(const unsigned short ct)
	{
	RegCtrlDAC[0] = (unsigned char) ((ct & 0xFF00) >> 8);
	RegCtrlDAC[1] = (unsigned char) (ct & 0x00FF);
	}

    /*void SetDDSAdd    (unsigned char add)
     {
     DDSAdd = add;
     return;
     }*/
    AD9852Reg() // initiate
	{
	ZeroArray(&RegPhaseAdj1[0], 2);
	ZeroArray(&RegPhaseAdj2[0], 2);
	ZeroArray(&RegFreq1[0], 6);
	ZeroArray(&RegFreq2[0], 6);
	ZeroArray(&RegDeltaFreq[0], 6);
	ZeroArray(&RegUpdateClk[0], 4);
	ZeroArray(&RegRampClk[0], 3);
	ZeroArray(&RegCtrlReg  [0],4);
	ZeroArray(&RegOSKMult[0], 2);
	ZeroArray(&RegDontCare[0], 2);
	RegOSKRamp = 0;
	ZeroArray(&RegCtrlDAC[0], 2);
	CtrlRegister CtrlReg;
	UpdateCtrlReg();
	Time = 0;
	}

    AD9852Reg(const char address) // overload in case we want multiple cards in the future
	{
	ZeroArray(&RegPhaseAdj1[0], 2);
	ZeroArray(&RegPhaseAdj2[0], 2);
	ZeroArray(&RegFreq1[0], 6);
	ZeroArray(&RegFreq2[0], 6);
	ZeroArray(&RegDeltaFreq[0], 6);
	ZeroArray(&RegUpdateClk[0], 4);
	ZeroArray(&RegRampClk[0], 3);
	ZeroArray(&RegCtrlReg  [0],4);
	ZeroArray(&RegOSKMult[0], 2);
	ZeroArray(&RegDontCare[0], 2);
	RegOSKRamp = 0;
	ZeroArray(&RegCtrlDAC[0], 2);
	CtrlRegister CtrlReg;
	UpdateCtrlReg();
	Time = 0;
	}

    // Read commands
    // TODO: should I make them use real units?
    unsigned short ReadPhaseAdj1(void)
	{
	return (((unsigned short) RegPhaseAdj1[0] << 8)
		+ (unsigned short) RegPhaseAdj1[1]);
	}

    unsigned short ReadPhaseAdj2(void)
	{
	return (((unsigned short) RegPhaseAdj2[0] << 8)
		+ (unsigned short) RegPhaseAdj2[1]);
	}

    uint64_t ReadFreq1(void)
	{
	return (  ((uint64_t) RegFreq1[0] << 050)
		+ ((uint64_t) RegFreq1[1] << 040)
		+ ((uint64_t) RegFreq1[2] << 030)
		+ ((uint64_t) RegFreq1[3] << 020)
		+ ((uint64_t) RegFreq1[4] << 010)
		+  (uint64_t) RegFreq1[5]);
	}

    uint64_t ReadFreq2(void)
	{
	return (  ((uint64_t) RegFreq2[0] << 050)
		+ ((uint64_t) RegFreq2[1] << 040)
		+ ((uint64_t) RegFreq2[2] << 030)
		+ ((uint64_t) RegFreq2[3] << 020)
		+ ((uint64_t) RegFreq2[4] << 010)
		+  (uint64_t) RegFreq2[5]);
	}

    uint64_t ReadDeltaFreq(void)
	{
	return (  ((uint64_t) RegDeltaFreq[0] << 050)
		+ ((uint64_t) RegDeltaFreq[1] << 040)
		+ ((uint64_t) RegDeltaFreq[2] << 030)
		+ ((uint64_t) RegDeltaFreq[3] << 020)
		+ ((uint64_t) RegDeltaFreq[4] << 010)
		+  (uint64_t) RegDeltaFreq[5]);
	}

    unsigned int ReadUpdateClk(void)
	{
	return (  ((unsigned int) RegUpdateClk[0] << 030)
		+ ((unsigned int) RegUpdateClk[1] << 020)
		+ ((unsigned int) RegUpdateClk[2] << 010)
		+  (unsigned int) RegUpdateClk[3]);
	}

    unsigned int ReadRampClk(void)
	{
	return (  ((unsigned int) RegRampClk[0] << 020)
		+ ((unsigned int) RegRampClk[1] << 010)
		+  (unsigned int) RegRampClk[2]);
	}

    uint32_t ReadCtrlReg(void)
	{ // Should only need this for debugging
	return (  ((uint32_t) RegCtrlReg[0] << 030)
		+ ((uint32_t) RegCtrlReg[1] << 020)
		+ ((uint32_t) RegCtrlReg[2] << 010)
		+  (uint32_t) RegCtrlReg[3]);
	}

    unsigned short ReadOSKMult(void)
	{
	return ( ((unsigned short) RegOSKMult[0] << 8)
		+ (unsigned short) RegOSKMult[1]);
	}

    //unsigned   short ReadDontCare  (void);
    unsigned char ReadOSKRamp(void)
	{
	return (RegOSKRamp);
	}

    unsigned short ReadCtrlDAC(void)
	{
	return ( ((unsigned short) RegCtrlDAC[0] << 8)
		+ (unsigned short) RegCtrlDAC[1]);
	}

    void Print()
	{
	// TODO: Print values of each register in hex and real units if appropriate
	cout << "AARRGGH!" << endl;
	return;
	}
    };

class DDSIOWriteReg // creates a block of DDSIO from a AD9852Raw or AD9852Reg
    {
public:
    DDSIOWord Words[0x29];   // one "Word" per register + one update command

    unsigned char changes; // number of changes relative to previous
    DDSIOWriteReg(const AD9852Raw raw) // constructor with Raw
	{
	changes = 0;
	unsigned char lastchange = 0;
	for (unsigned int ii = 0; ii < 0x28; ii++)
	    {
	    if (raw.data[ii] != 0)
		{
		Words[changes] = DDSIOWord(DIP, IOLOAD, 0, ii, raw.data[ii],
			raw.Time, 1); // write to address "DIP"
		changes++;
		lastchange = ii;
		}
	    }
	Words[changes - 1] = DDSIOWord(DIP, IOUPDATE, 0, lastchange,
		raw.data[lastchange], raw.Time, 1); // copy last command, but change mode to update
	}

    DDSIOWriteReg(AD9852Reg reg) // constructor with Reg
	{
	changes = 0;
	unsigned char lastchange = 0;
	for (unsigned int ii = 0; ii < 0x28; ii++)
	    {
	    if(reg.Raw().data[ii]!=0)
	      {
	      Words[changes] = DDSIOWord(DIP, IOLOAD, 0, ii, reg.Raw().data[ii], reg.Raw().Time,1); // write to address "DIP"
	      changes++;
	      lastchange=ii;
	      }
	    }
	Words[changes-1] = DDSIOWord(DIP, IOUPDATE, 0, lastchange, reg.Raw().data[lastchange], reg.Raw().Time,1); // copy last command, but change mode to update
	}

    DDSIOWriteReg(AD9852Reg current, AD9852Reg prev) // only write those registers which have changed relative to previous
	{
	changes = 0;
	unsigned char lastchange = 0;
	for (unsigned char ii = 0; ii < 0x28; ii++) //step through registers
	    {
	    if (current.Raw().data[ii] != prev.Raw().data[ii])
		{
		Words[changes] = DDSIOWord(DIP, IOLOAD, 0, ii,
			current.Raw().data[ii], current.Raw().Time, 1);
		changes++;
		lastchange = ii;
		}
	    }
	Words[changes] = DDSIOWord(DIP, IOUPDATE, 0, lastchange,
		current.Raw().data[lastchange], current.Raw().Time, 1);
	for (unsigned char ii = changes + 1; ii < 0x28; ii++) // fill in blanks
	    {
	    Words[ii] = DDSIOWord(DIP, IOLATCH, 0, 0, 0, current.Raw().Time, 1); // Do nothing
	    }
	}

    DDSIOWriteReg() // default constructor
	{
	AD9852Reg defreg;
	unsigned char lastchange = 0;
	changes = 0;
	for (unsigned int ii = 0; ii < 0x28; ii++)
	    {
	    if (defreg.Raw().data[ii] != 0)
		{
		Words[changes] = DDSIOWord(DIP, IOLOAD, 0, ii,
			defreg.Raw().data[ii], defreg.Raw().Time, 1); // write to address "DIP"
		changes++;
		lastchange = ii;
		}
	    }
	Words[changes - 1] = DDSIOWord(DIP, IOUPDATE, 0, lastchange,
		defreg.Raw().data[lastchange], defreg.Raw().Time, 1);
	}

    void Print()
	{
	cout << "Reg changes: " << dec << int(changes) << endl;
	for (unsigned int i = 0; i < changes; ++i)
	    {
	    Words[i].Print();
	    }
	return;
	}
    };

#endif // wrapper
