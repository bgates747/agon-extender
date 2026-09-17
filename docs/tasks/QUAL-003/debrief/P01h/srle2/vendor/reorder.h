#ifndef REORDER_H

#include "port.h"

void reorder(unsigned char *in, unsigned char *out, uint4 length, uint recordsize);

void unreorder(unsigned char *in, unsigned char *out, uint4 length, uint recordsize);

#endif // REORDER_H