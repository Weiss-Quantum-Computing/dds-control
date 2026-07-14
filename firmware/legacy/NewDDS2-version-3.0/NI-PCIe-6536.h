/*
 * NI-PCIe-6536.h
 *
 *  Created on: Jun 23, 2010
 *      Author: Yang
 */

#ifndef NI_PCIE_6536_H_
#define NI_PCIE_6536_H_

#ifndef __int64
// needed to make NIDAQmx.h work
#define __int64 long long
#endif

#include <NIDAQmx.h>
#include "DDSconstants.h"
/*
 * All of the direct IO will happen here.
 * Another possibility is to put methods directly in the Pulse class
 */

/* README
 * Some tricks required to make this work:
 * (Update:  seems like "1." is unnecessary.  NIDAQmx.lib appears to work without conversion.)
 * 1.	If compiling with MinGW gcc, need to convert NIDAQmx.lib
 * 	from a VisualC++ library to a gcc library
 * 	a.	Basic info from:
 * 		http://forums.ni.com/t5/Multifunction-DAQ/Howto-use-NIDAQmx-with-mingw-gcc-3-4-2/m-p/294361
 * 		Type the commands below into cmd.exe prompt (make sure MinGW and Visual C++ are in PATH)
 * 	b.	dumpbin /exports NIDAQmx.lib > nidaq.exports
 * 	c.	echo LIBRARY nicaiu.dll > nidaq.defs
 * 	d.	echo EXPORTS >> nidaq.defs
 * 	e.	sed "1,/ordinal *name/d;/^$/d;/Summary$/,+100d;s/^ \+\([^ ]\+\)\( .*\|\)$/\\1/;s/^_\(.*\)$/\1/" nidaq.exports |sort >> nidaq.defs
 * 		(may have to run above line in cygwin)
 * 	f.	dlltool -l -d nidaq.defs -l libnidaq.a c:\WINDOWS\system32\nicaiu.dll
 * 	g.	make sure NIDAQmx.lib, libnidaq.a are in same folder as this file
 * 2.	Compiler options:
 * 	a.	-L.. -lnidaq (Update: use "-lNIDAQmx" instead)
 * 	b.	may also need to define __int64 = long long
 */

#define DAQmxErrChk(functionCall) if( DAQmxFailed(error=(functionCall)) ) goto Error; else


int IO(const uInt32 * DataArray,const int sample_num)
    {
    int error = 0;
    TaskHandle taskHandle = 0;
    char errBuff[2048] = {'\0'};
    int32 written;
//    float Timeout = 60.0; // Replaced with constant IOTIMEOUT from DDSconstants.h
    uint64_t generated;

    /*********************************************/
    // DAQmx Configure Code
    /*********************************************/
#ifdef _DEBUG
    uInt32 majver = 0;
    uInt32 minver = 0;
    uInt32 upver  = 0;
    DAQmxGetSysNIDAQMajorVersion(&majver);
    DAQmxGetSysNIDAQMinorVersion(&minver);
    DAQmxGetSysNIDAQUpdateVersion(&upver);
//    cout << "NIDAQmx Version: " << dec << majver << "." << minver << "." << upver << endl;
#endif
    DAQmxErrChk( DAQmxSetDigitalLogicFamilyPowerUpState ("Dev1",DAQmx_Val_3point3V));
    DAQmxErrChk( DAQmxCreateTask       ("",&taskHandle));
      DAQmxErrChk( DAQmxCreateDOChan     (taskHandle,"Dev1/port0:3","",DAQmx_Val_ChanForAllLines)); // was port0:3
      DAQmxErrChk( DAQmxCfgSampClkTiming (taskHandle,"/Dev1/PFI4",1.0e6,DAQmx_Val_Rising,DAQmx_Val_FiniteSamps,sample_num)); //sample clock on REQ1
//    DAQmxErrChk( DAQmxCfgSampClkTiming (taskHandle,"",1.0e6,DAQmx_Val_Rising,DAQmx_Val_FiniteSamps,sample_num)); //sample clock on REQ1


//    cout << "Preparing to send " << sample_num << " samples to DIO board" << endl;
 //     clock_t t5=clock();
//      cout<<"After initiation(ms):"<<(clock())*1000/CLOCKS_PER_SEC<<endl;
    DAQmxErrChk ( DAQmxWriteDigitalU32  (taskHandle,sample_num,FALSE,IOTIMEOUT,DAQmx_Val_GroupByScanNumber,DataArray,&written,NULL));

//    cout << dec << written << " samples written to on-board FIFO" << endl;

    DAQmxErrChk (DAQmxStartTask(taskHandle));

    if( taskHandle!=0 )
	{

//	cout << "Waiting for trigger (" << dec << IOTIMEOUT << "s max)..."<< endl;
	    clock_t t2=clock();
	    cout<<"Ending time(ms):"<<(t2)*1000/CLOCKS_PER_SEC<<endl;
	DAQmxErrChk (DAQmxWaitUntilTaskDone(taskHandle,IOTIMEOUT));
	DAQmxErrChk (DAQmxGetWriteTotalSampPerChanGenerated(taskHandle,&generated));

	cout << dec << generated << " samples output successfully" << endl;

	DAQmxErrChk (DAQmxStopTask(taskHandle));
	DAQmxErrChk (DAQmxClearTask(taskHandle));
	}
    Error:
    if( DAQmxFailed(error) )
    DAQmxGetExtendedErrorInfo(errBuff,2048);
    if( DAQmxFailed(error) )
	cout << "DAQmx Error: " << errBuff << endl;
    return error;
    }

#endif /* NI_PCIE_6536_H_ */
