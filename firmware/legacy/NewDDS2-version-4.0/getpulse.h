/*
 * getpulse.h
 *
 *  Created on: Aug 3, 2010
 *      Author: Yang
 */

#ifndef GETPULSE_H_
#define GETPULSE_H_

#include "libxl.h" // for reading Excel files
#include "DDSconstants.h"
#include <iostream>
#include <string>

int GetPulse(const char* filename, const unsigned maxp, long double parms[MAXPULSES][PULSEPARASIZE]);

#endif /* GETPULSE_H_ */
