#include "game_timing.hpp"
#include <agon/vdp.h>
int main(){if(!gt::init())return 1;do{gt::loop_begin();gt::drawing_begin();gt::drawing_end();waitvblank();}while(!gt::loop_end());bool ok=gt::save("empty.csv");printf("Timing %s: empty.csv\n",ok?"complete":"failed");return ok?0:1;}
