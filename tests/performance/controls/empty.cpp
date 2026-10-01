#include "game_timing.hpp"
#include <agon/vdp.h>
int main(int argc,char**argv){const char*result=argc>1?argv[1]:"empty.csv";if(!gt::init())return 1;do{gt::loop_begin();gt::drawing_begin();gt::drawing_end();waitvblank();}while(!gt::loop_end());gt::boundary();bool ok=gt::save(result);printf("Timing %s: %s\n",ok?"complete":"failed",result);return ok?0:1;}
