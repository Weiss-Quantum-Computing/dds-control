#ldcnlib.py wrappers for the ldcnlib.dll to control the picomotors
# Ted Corcovilos 20130128
# ldcnlib.dll should be in the same directory as this file
# The library file and documentatoin may be downloaded
# from http://www.logosolinc.com/software.htm
# or ftp://download.newport.com (in the New Focus folder (as of 20130128))

import ctypes as C
#from ctypes.wintypes import * # variable type definitions

ldcn = C.windll.LoadLibrary("LDCNLIB") # load the library DLL file

#define some aliases and define the parameter types for safety

LdcnFullInit = ldcn.LdcnFullInit
LdcnFullInit.argtypes = [C.c_char_p, C.c_uint16]
LdcnFullInit.restype = C.c_int16

LdcnInit = ldcn.LdcnInit
LdcnInit.argtypes = [C.c_char_p, C.c_uint16]
LdcnInit.restype = C.c_int16

LdcnDefineStatus = ldcn.LdcnDefineStatus
LdcnDefineStatus.argtypes = [C.c_uint8, C.c_uint8]
LdcnDefineStatus.restype = C.c_bool

LdcnGetStat = ldcn.LdcnGetStat
LdcnGetStat.argtypes = [C.c_uint8]
LdcnGetStat.restype = C.c_uint8

LdcnNoOp = ldcn.LdcnNoOp
LdcnNoOp.argtypes = [C.c_uint8]
LdcnNoOp.restype = C.c_bool

LdcnShutdown = ldcn.LdcnShutdown
LdcnShutdown.argtypes = []
LdcnShutdown.restype = None

StepLoadTraj = ldcn.StepLoadTraj
StepLoadTraj.argtypes = [C.c_uint8,C.c_uint8,C.c_int32,C.c_uint8,C.c_uint8,C.c_uint16]
StepLoadTraj.restype = C.c_bool

StepGetPos = ldcn.StepGetPos
StepGetPos.argtypes = [C.c_uint8]
StepGetPos.restype = C.c_int32

StepResetPos = ldcn.StepResetPos
StepResetPos.argtypes = [C.c_uint8]
StepResetPos.restype = C.c_bool

StepSetParam = ldcn.StepSetParam
StepSetParam.argtypes = [C.c_uint8,C.c_uint8,C.c_uint8,C.c_uint8,C.c_uint8,C.c_uint8,C.c_uint8]
StepSetParam.restype = C.c_bool

StepStopMotor = ldcn.StepStopMotor
StepStopMotor.argtypes = [C.c_uint8,C.c_uint8]
StepStopMotor.restype = C.c_bool

StepSetOutputs = ldcn.StepSetOutputs
StepSetOutputs.argtypes = [C.c_uint8,C.c_uint8]
StepSetOutputs.restype = C.c_bool

ServoStartMotion = ldcn.ServoStartMotion
ServoStartMotion.argtypes = [C.c_uint8]
ServoStartMotion.restype = C.c_bool


