#include "game_timing.hpp"
#include <agon/vdp.h>
int main(){if(!gt::init())return 1;do{gt::loop_begin();gt::drawing_begin();vdp_gcol(0,gt::frame%64);vdp_filled_rectangle(10,10,100,100);gt::drawing_end();waitvblank();}while(!gt::loop_end());bool ok=gt::save("draw.csv");printf("Timing %s: draw.csv\n",ok?"complete":"failed");return ok?0:1;}
