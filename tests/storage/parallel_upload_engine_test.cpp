// Real P4 file engine/queue and candidate foreground SD policy. The physical
// receive callback is modeled; paired coordinators/raw CPU tests cover it apart.
#include "extender/storage/fast/engine.hpp"
#include "extender/storage/sd_service.hpp"
#include <cassert>
#include <filesystem>
#include <fstream>
#include <vector>
extern "C" {
#include "agon/mos.h"
void fs_root(const char *);
void fs_fault(unsigned,unsigned);
int service_init_mode(const char *,std::uint32_t,int);
unsigned service_request(const std::uint8_t *,unsigned,std::uint8_t *);
void service_stop();
void service_enable_parallel();
unsigned test_crc_calls();
}
using namespace agon::extender::storage;
using namespace agon::extender::storage::fast;
static std::vector<unsigned char> retained;
static unsigned bulkCalls;
extern "C" int service_parallel_receive(FIL *file,std::uint32_t total,
    std::uint32_t *written,std::uint8_t *error) {
  ++bulkCalls;assert(total==retained.size());*written=0;*error=0;
  while(*written<total){
    auto n=std::min(512U,total-*written);
    auto got=ffs_fwrite(file,reinterpret_cast<char *>(retained.data()+*written),n);
    *error=ffs_ferror(file);*written+=got;
    if(*error||got!=n){if(!*error)*error=FR_DISK_ERR;return SD_FILE_ERROR;}
  }
  return SD_OK;
}
struct Peer final : Link {
  SdService queue;
  unsigned token=0,ticks=0,failAt=0;
  bool selected=true,capability=true,allocationFailure=false,physicalFailure=false;
  std::vector<unsigned> operations;
  Peer(){
    unsigned char p[20];sd_header_mode(p,SD_PRESENCE,101,0,0,0,0,1);sd_seal(p);
    assert(queue.receive(p,20,0));token=queue.claim(0);assert(token);
  }
  bool parallelUploads() const override {return selected;}
  bool prepareUpload(FILE *f,std::uint32_t size,std::uint32_t) override {
    if(allocationFailure)return false;
    retained.resize(size);
    return fread(retained.data(),1,size,f)==size && fgetc(f)==EOF && !ferror(f);
  }
  bool uploadReturned() const override {return !physicalFailure;}
  bool exchange(const std::uint8_t *p,unsigned n,std::uint8_t *out,unsigned &size) override {
    operations.push_back(p[12]);if(operations.size()==failAt)return false;
    assert(queue.postOwned(token,p,n,out,size,ticks)==202);
    unsigned char request[240],response[240];assert(queue.take(request,ticks)==n);
    if(p[12]==SD_PARALLEL_WRITE){assert(queue.admitBulk(ticks,sd_u32(p+20),sd_u32(p+24)));ticks+=10000;}
    auto count=service_request(request,n,response);assert(count);
    if(p[12]==SD_HELLO&&!capability)sd_put16(response+26,sd_u16(response+26)&~128U);
    assert(queue.receive(response,count,++ticks));
    return queue.postOwned(token,p,n,out,size,ticks)==200;
  }
};
static std::vector<unsigned char> content(unsigned size){
  std::vector<unsigned char> b(size);for(unsigned i=0;i<size;++i)b[i]=(i*73+(i>>8)*19+17)&255;return b;
}
static FILE *spool(const std::vector<unsigned char>& data){
  FILE *f=tmpfile();assert(f);if(!data.empty())assert(fwrite(data.data(),1,data.size(),f)==data.size());rewind(f);return f;
}
static void setup(const std::filesystem::path &root){
  service_stop();std::filesystem::remove_all(root);std::filesystem::create_directories(root/"test");
  fs_root(root.c_str());assert(service_init_mode("/test",101,1));service_enable_parallel();retained.clear();bulkCalls=0;
}
int main(int argc,char **argv){
  assert(argc==2);std::filesystem::path root=argv[1];unsigned cases=0;
  for(unsigned size:{0U,1U,63U,64U,65U,512U,65535U,65536U,65537U,1100000U}){
    setup(root);auto bytes=content(size);auto f=spool(bytes);Peer peer;Engine e(peer,55);
    auto result=e.run(Plan{"/test/file",73,size,101,true,true},f);fclose(f);
    assert(!result.error&&result.bytes==size&&bulkCalls==(size?1U:0U));
    assert(result.records==(size?5U:4U));
    for(auto op:peer.operations)assert(op!=SD_WRITE);
    std::ifstream in(root/"test/file",std::ios::binary);
    std::vector<unsigned char> actual((std::istreambuf_iterator<char>(in)),{});assert(actual==bytes);
    assert(test_crc_calls()==0);++cases;
  }
  for(unsigned variant=0;variant<2;++variant){
    setup(root);Peer peer;if(variant)peer.selected=false;else peer.capability=false;
    auto f=spool(content(513));Engine e(peer,56);auto r=e.run(Plan{"/test/file",73,513,101,true,true},f);fclose(f);
    assert(!r.error&&!bulkCalls&&r.records==7); // UART chosen BEFORE admission
    for(auto op:peer.operations)assert(op!=SD_PARALLEL_WRITE);++cases;
  }
  for(unsigned failure=0;failure<5;++failure){
    setup(root);Peer peer;auto f=spool(content(65537));
    if(failure==0)peer.allocationFailure=true;
    if(failure==1)peer.failAt=3; // uncertain bulk request: no UART replay
    if(failure==2)peer.physicalFailure=true;
    if(failure==3)fs_fault(3,2); // payload short write after metadata succeeds
    if(failure==4)fs_fault(8,2); // payload device error after metadata succeeds
    Engine e(peer,57);auto r=e.run(Plan{"/test/file",73,65537,101,true,true},f);fclose(f);
    assert(r.error&&!std::filesystem::exists(root/"test/file"));
    for(auto op:peer.operations)assert(op!=SD_ACTIVATE&&op!=SD_WRITE);
    assert(test_crc_calls()==0);++cases;
  }
  service_stop();std::filesystem::remove_all(root);
  std::printf("PASS %u paired file-policy cases; full bytes, one bulk request, zero CRC calls and no partial activation\n",cases);
}
