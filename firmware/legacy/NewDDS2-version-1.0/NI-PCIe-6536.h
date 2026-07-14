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
#ifndef ___nidaqmx_h___
#include <NIDAQmx.h>  // Header for NI library
#endif

/* TODO:
 * All of the direct IO will happen here.
 * Another possibility is to put methods directly in the Pulse class
 */

/* README
 * Some tricks required to make this work:
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
 * 	a.	-L.. -lnidaq
 * 	b.	may also need to define __int64 = long long
 */

#define DAQmxErrChk(functionCall) if( DAQmxFailed(error=(functionCall)) ) goto Error; else


int IO(const uInt32 * DataArray,const int sample_num) // FIXME: this function declaration is just a placeholder
    {
    //const int sample_num=150000;
    int error = 0;
    TaskHandle taskHandle = 0;
    char errBuff[2048] = {'\0'};
    int32 written;
    float Timeout = 10.0;
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
    cout << "NIDAQmx Version: " << dec << majver << "." << minver << "." << upver << endl;
#endif
    DAQmxErrChk( DAQmxCreateTask       ("",&taskHandle));
#ifdef _DEBUG
    cout << "DAQmx Task created" << endl;
#endif
      DAQmxErrChk( DAQmxCreateDOChan     (taskHandle,"Dev1/port0:2","",DAQmx_Val_ChanForAllLines)); // was port0:3
//    DAQmxErrChk( DAQmxCreateDOChan     (taskHandle,"Dev1/port0_32","DOChan",DAQmx_Val_ChanForAllLines));//? not sure about the syntax
#ifdef _DEBUG
    cout << "DAQmx DO channel created" << endl;
#endif

//    DAQmxErrChk( DAQmxTaskControl      (taskHandle,DAQmx_Val_Task_Commit));
#ifdef _DEBUG
    cout << "DAQmx Task control created" << endl;
#endif
      DAQmxErrChk( DAQmxCfgSampClkTiming (taskHandle,"/Dev1/PFI4",1.0e6,DAQmx_Val_Rising,DAQmx_Val_FiniteSamps,sample_num)); //sample clock on REQ1
//    DAQmxErrChk( DAQmxCfgSampClkTiming (taskHandle,"",1.0e6,DAQmx_Val_Rising,DAQmx_Val_FiniteSamps,sample_num)); //sample clock on REQ1
//    DAQmxErrChk( DAQmxCfgSampClkTiming (taskHandle,"/Dev1/PFI4",1.0e6,DAQmx_Val_Rising,DAQmx_Val_FiniteSamps,sample_num)); //sample clock on REQ1

    //      DAQmxErrChk( DAQmxCfgImplicitTiming(taskHandle,DAQmx_Val_FiniteSamps,sample_num) );


#ifdef _DEBUG
    cout << "DAQmx sample clock created" << endl;
#endif
    // FIXME!! something wicked this way comes, the NIDAQmx error -88700 (ta da!)
    /*********************************************/
    // DAQmx Write/Start
    /*********************************************/
    // suggestion from NI forums:
    //DAQmxErrChk ( DAQmxStartTask (taskHandle) ); // didn't help
    cout << "Preparing to send " << sample_num << "samples to DIO board" << endl;

    DAQmxErrChk ( DAQmxWriteDigitalU32  (taskHandle,sample_num,FALSE,Timeout,DAQmx_Val_GroupByScanNumber,DataArray,&written,NULL));
//    printf("%d samples written to on-board FIFO\n",written);
    cout << dec << written << " samples written to on-board FIFO" << endl;

    DAQmxErrChk (DAQmxStartTask(taskHandle));

    Error:
    if( DAQmxFailed(error) )
    DAQmxGetExtendedErrorInfo(errBuff,2048);
    if( taskHandle!=0 )
	{
	/*********************************************/
	// DAQmx Stop/Clear
	/*********************************************/

	DAQmxWaitUntilTaskDone(taskHandle,10.0);  //seems this line is ignored by the program, why?

	DAQmxGetWriteTotalSampPerChanGenerated(taskHandle,&generated);
//	printf("%d samples output successfully\n",generated);
	cout << dec << generated << " samples output successfully" << endl;
	DAQmxStopTask(taskHandle);
	DAQmxClearTask(taskHandle);
	}
    if( DAQmxFailed(error) )
    //printf("DAQmx Error: %s\n",errBuff);
	cout << "DAQmx Error: " << errBuff << endl;
    return error;
    }

#endif /* NI_PCIE_6536_H_ */
