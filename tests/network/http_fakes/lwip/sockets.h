#pragma once
#include <cstddef>
int fake_send(int,const char*,size_t,int);
int lwip_close(int);
#define send fake_send
