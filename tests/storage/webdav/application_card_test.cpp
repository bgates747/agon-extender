#include "extender/storage/application/engine.hpp"
#include "extender/storage/application/mailbox.hpp"
#include <cassert>
#include <filesystem>
#include <fstream>
#include <vector>
extern "C" {
#include "sdapp.h"
void fs_root(const char *);
}
using agon::extender::storage::application::Engine;
static std::string root,spool;
static std::unique_ptr<Engine> engine;
static std::uint8_t response[240];
static unsigned responseN,token,ticks;
extern "C" uint32_t sdapp_clock(void){return ticks++;}
extern "C" unsigned sdapp_link(unsigned op,const uint8_t *p,unsigned n,uint8_t *out,unsigned cap,unsigned *got) {
 *got=0;
 if(op==4){assert(cap==4&&!engine);engine=std::make_unique<Engine>(root,spool,123,++token);sd_put32(out,token);*got=4;return 0;}
 if(op==3){engine.reset();return 0;}
 assert(engine);
 if(op==2){assert(!responseN);responseN=engine->process(p,n,response);assert(responseN);return 0;}
 assert(op==1&&cap>=responseN);std::memcpy(out,response,responseN);*got=responseN;responseN=0;return 0;
}
static std::string read(const std::string &p){std::ifstream f(p,std::ios::binary);return {std::istreambuf_iterator<char>(f),{}};}
int main(){
 char dir[]="/tmp/app-card-XXXXXX";assert(mkdtemp(dir));std::string base=dir;
 root=base+"/p4";spool=root+"/spool";
 std::filesystem::create_directories(spool);std::filesystem::create_directory(base+"/agon");
 fs_root((base+"/agon").c_str());
 std::string bytes;for(unsigned i=0;i<4097;++i)bytes+=char(i*17+3);
 {std::ofstream f(root+"/source.bin",std::ios::binary);f<<bytes;}
 assert(emos_file_transfer(3,"/source.bin","/received.bin",0,nullptr,nullptr)==EMOS_FILE_OK);
 assert(read(base+"/agon/received.bin")==bytes);
 assert(std::filesystem::is_empty(spool));
 assert(emos_file_transfer(4,"/received.bin","/sent.bin",0,nullptr,nullptr)==EMOS_FILE_OK);
 assert(read(root+"/sent.bin")==bytes);assert(std::filesystem::is_empty(spool));
 assert(emos_file_transfer(4,"/received.bin","/sent.bin",1,nullptr,nullptr)==EMOS_FILE_OK);
 assert(read(root+"/sent.bin")==bytes);assert(std::filesystem::is_empty(spool));
 {std::ofstream f(root+"/empty.bin");}
 assert(emos_file_transfer(3,"/empty.bin","/empty.bin",0,nullptr,nullptr)==EMOS_FILE_OK);
 assert(emos_file_transfer(4,"/empty.bin","/empty-copy.bin",0,nullptr,nullptr)==EMOS_FILE_OK);
 assert(std::filesystem::file_size(root+"/empty-copy.bin")==0);
 assert(std::filesystem::is_empty(spool));
 agon::extender::storage::application::Mailbox q;std::uint8_t hello[48]{};
 sd_header(hello,4,1,1,1,0,28);hello[44]=2;hello[46]=1;sd_seal(hello);
 assert(q.receive(hello,48,1,true)&&!q.owned);
 assert(q.receive(hello,48,2,false)&&q.owned&&q.requestSize==48);
 auto saved=q.request[8];hello[8]++;sd_seal(hello);
 assert(q.receive(hello,48,3,false)&&q.request[8]==saved); // no overwrite
 std::filesystem::remove_all(base);
 puts("real application helper + checked Agon engine + P4 spool/card: both directions and overwrite pass");
}
