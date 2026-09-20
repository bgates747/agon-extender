#include "game_timing.hpp"
#include <agon/vdp.h>
int main(){bool ok=gt::init();mos_setkbvector(nullptr,0);printf("Timing capability %s\n",ok?"ready":"failed");return ok?0:1;}
