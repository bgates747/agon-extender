#include "game_timing.hpp"
#include <agon/vdp.h>
int main(){gt::sv=mos_sysvars();mos_setkbvector(graphics_callback,0);gt::frame=120;bool ok=gt::save("nur.csv");printf("Timing %s: nur.csv\n",ok?"complete":"failed");return ok?0:1;}
