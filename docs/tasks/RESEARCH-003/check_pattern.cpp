#include <cstdio>
#include <cstdlib>
#include "firmware/src/pattern.h"
int main(){uint8_t *p=new uint8_t[N];for(unsigned i=0;i<64;++i){pattern(p,i);if(fwrite(p,1,N,stdout)!=N)return 1;}delete[]p;}
