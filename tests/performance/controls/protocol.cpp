#include "game_timing.hpp"
int main(){
 bool capability=gt::init();bool session=false,empty=false,order=false;
 if(capability){session=!gt::request(9,1);empty=gt::request(9,0)&&gt::value==0&&gt::count==0&&!gt::request(8,0,1);
 if(gt::request(5,0)){gt::send(6,1);gt::send(7,1);order=gt::request(9,0)&&gt::value==1&&gt::count==0;}}
 gt_prt_close();mos_setkbvector(nullptr,0);
 FILE*f=fopen("protocol.csv","w");if(!f)return 2;
 fprintf(f,"capability,session,empty,order\n%u,%u,%u,%u\n",capability,session,empty,order);fclose(f);
 printf("Protocol %s\n",capability&&session&&empty&&order?"complete":"failed");return capability&&session&&empty&&order?0:1;
}
