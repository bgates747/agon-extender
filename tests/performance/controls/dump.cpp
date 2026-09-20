#include "game_timing.hpp"
int main(){gt::sv=mos_sysvars();mos_setkbvector(graphics_callback,0);bool ok=gt::request(10,0);mos_setkbvector(nullptr,0);return ok?0:1;}
