// Mac-only stub: types and no-op functions so the compiler-only path builds. Never touches hardware.
#ifndef STUB_NIDAQMX_H
#define STUB_NIDAQMX_H
#include <stdint.h>
#include <stdio.h>
#include <time.h>
typedef uint32_t uInt32; typedef int32_t int32; typedef uint64_t uInt64; typedef double float64; typedef void* TaskHandle;
#ifndef FALSE
#define FALSE 0
#endif
#define DAQmxFailed(e) ((e)<0)
#define DAQmx_Val_3point3V 0
#define DAQmx_Val_ChanForAllLines 0
#define DAQmx_Val_FiniteSamps 0
#define DAQmx_Val_GroupByScanNumber 0
#define DAQmx_Val_Rising 0
static inline int32 DAQmxGetSysNIDAQMajorVersion(uInt32*){return 0;}
static inline int32 DAQmxGetSysNIDAQMinorVersion(uInt32*){return 0;}
static inline int32 DAQmxGetSysNIDAQUpdateVersion(uInt32*){return 0;}
static inline int32 DAQmxSetDigitalLogicFamilyPowerUpState(const char*,int){return 0;}
static inline int32 DAQmxCreateTask(const char*,TaskHandle*){return 0;}
static inline int32 DAQmxCreateDOChan(TaskHandle,const char*,const char*,int){return 0;}
static inline int32 DAQmxCfgSampClkTiming(TaskHandle,const char*,double,int,int,uint64_t){return 0;}
static inline int32 DAQmxWriteDigitalU32(TaskHandle,int32,int,double,int,const uInt32*,int32*,void*){return 0;}
static inline int32 DAQmxStartTask(TaskHandle){return 0;}
static inline int32 DAQmxWaitUntilTaskDone(TaskHandle,double){return 0;}
static inline int32 DAQmxGetWriteTotalSampPerChanGenerated(TaskHandle,uint64_t*){return 0;}
static inline int32 DAQmxStopTask(TaskHandle){return 0;}
static inline int32 DAQmxClearTask(TaskHandle){return 0;}
static inline int32 DAQmxGetExtendedErrorInfo(char*,uInt32){return 0;}
#endif
