#include "extender/storage/fast/engine.hpp"
#include "extender/storage/sd_service.hpp"
#include <cassert>
#include <filesystem>
#include <fstream>
#include <vector>
extern "C" {
void fs_root(const char *);
void fs_fault(unsigned,unsigned);
unsigned fs_read_bytes();
int service_init_mode(const char *,std::uint32_t,int);
unsigned service_request(const std::uint8_t *,unsigned,std::uint8_t *);
void service_stop();
}
using namespace agon::extender::storage;
using namespace agon::extender::storage::fast;
struct Peer : Link {
  SdService queue;
  unsigned token=0,ticks=0,exchanges=0,failAt=0,corruptAt=0,resetAt=0;
  std::vector<unsigned> operations;
  Peer() {
    unsigned char p[20];sd_header_mode(p,SD_PRESENCE,101,0,0,0,0,1);sd_seal(p);
    assert(queue.receive(p,20,ticks));token=queue.claim(ticks);assert(token);
  }
  bool exchange(const std::uint8_t *p,unsigned n,std::uint8_t *out,unsigned &size) override {
    assert(p[2]==2 && !sd_u32(p+16));
    ++exchanges;operations.push_back(p[12]);
    if(exchanges==resetAt)queue.transportLost();
    if(exchanges==failAt)return false;
    if(!queue.owns(token))return false;
    assert(queue.post(p,n,out,size,ticks)==409); // another HTTP client cannot interleave
    assert(queue.postOwned(token,p,n,out,size,ticks)==202);
    std::uint8_t request[240],response[240];
    unsigned got=queue.take(request,ticks);assert(got==n);
    auto reply=service_request(request,got,response);assert(reply);
    if(exchanges==corruptAt)response[8]^=1;
    // Wrong-identity response cannot satisfy the actual P4 queue.
    if(!queue.receive(response,reply,++ticks))return false;
    return queue.postOwned(token,p,n,out,size,ticks)==200;
  }
};
std::vector<unsigned char> content(size_t size){
  std::vector<unsigned char> b(size);
  for(size_t i=0;i<size;++i)b[i]=(i*97+i/256)&255;
  return b;
}
FILE *spool(const std::vector<unsigned char>& b){
  FILE *f=tmpfile();assert(f);
  if(!b.empty())assert(fwrite(b.data(),1,b.size(),f)==b.size());rewind(f);return f;
}
void setup(const std::filesystem::path &root){
  service_stop();std::filesystem::remove_all(root);std::filesystem::create_directories(root/"test");
  fs_root(root.c_str());assert(service_init_mode("/test",101,1));
}
int main(int argc,char **argv){
  assert(argc==2);std::filesystem::path root=argv[1];
  for(unsigned size:{0U,1U,211U,212U,213U,65537U,1100000U}){
    setup(root);auto bytes=content(size);FILE *f=spool(bytes);Peer peer;
    Plan p{"/test/file",123,size,101,true,true};Engine engine(peer,55);
    auto done=engine.run(p,f);fclose(f);
    assert(done.error==Ok&&done.bytes==size&&done.size==size);
    assert(done.records==4+(size+211)/212); // HELLO BEGIN FINISH ACTIVATE
    assert(fs_read_bytes()==20); // activation reads metadata only, no payload verification
    for(auto op:peer.operations)assert(op!=SD_READ);
    std::ifstream in(root/"test/file",std::ios::binary);
    std::vector<unsigned char> actual((std::istreambuf_iterator<char>(in)),{});assert(actual==bytes);
    peer.queue.release(peer.token);
    Peer receiver;FILE *download=tmpfile();assert(download);
    Plan get{"/test/file",124,0,101,false,false};Engine reader(receiver,56);
    auto result=reader.run(get,download);assert(result.error==Ok&&result.bytes==size);
    rewind(download);std::vector<unsigned char> out(size);
    if(size)assert(fread(out.data(),1,size,download)==size);assert(out==bytes);fclose(download);
  }
  // Local truncation preserves a partial remote stage and does not activate it.
  setup(root);Peer shortPeer;auto bytes=content(211);FILE *f=spool(bytes);
  Plan p{"/test/short",125,212,101,true,true};Engine shortEngine(shortPeer,60);
  assert(shortEngine.run(p,f).error==Local);fclose(f);assert(!std::filesystem::exists(root/"test/short"));
  assert(std::filesystem::exists(root/"test/short.p17part"));
  // Explicit remote write error and disk-full short writes both remain failures.
  for(unsigned fault:{3U,8U,5U}){
    setup(root);Peer peer;f=spool(content(4096));fs_fault(fault,fault==5?2:1);
    Engine engine(peer,61);auto r=engine.run(Plan{"/test/fault",126,4096,101,true,true},f);
    assert(r.error==Remote&&r.remoteStatus==SD_FILE_ERROR&&r.filesystem);fclose(f);
    assert(!std::filesystem::exists(root/"test/fault"));
  }
  for(unsigned mode=0;mode<3;++mode){
    setup(root);Peer peer;f=spool(content(1024));
    if(mode==0)peer.failAt=3;if(mode==1)peer.corruptAt=3;if(mode==2)peer.resetAt=3;
    Engine engine(peer,62);auto r=engine.run(Plan{"/test/lost",127,1024,101,true,true},f);
    assert(r.error==Transport&&peer.exchanges==3);fclose(f);
    assert(!std::filesystem::exists(root/"test/lost"));
    peer.queue.release(peer.token);assert(!peer.queue.pending());
  }
  // P4-local full media is distinct from a remote FatFS error.
  setup(root);{std::ofstream file(root/"test/source");file<<"payload";}
  FILE *full=fopen("/dev/full","wb");assert(full);setbuf(full,nullptr);
  Peer fullPeer;Engine fullEngine(fullPeer,63);
  assert(fullEngine.run(Plan{"/test/source",128,0,101,false,false},full).error==Local);fclose(full);
  // Reject an over-quota remote file after STAT, before copying its payload.
  std::filesystem::resize_file(root/"test/source",Quota+1);
  Peer hugePeer;Engine hugeEngine(hugePeer,64);f=tmpfile();assert(f);
  assert(hugeEngine.run(Plan{"/test/source",129,0,101,false,false},f).error==TooLarge);
  assert(hugePeer.operations.size()==2);fclose(f);
  // Old listener presence cannot be claimed; token never survives a boot change.
  SdService q;unsigned char b[240]{},o[240]{};unsigned n=0;
  sd_header_mode(b,SD_PRESENCE,101,0,0,0,0,0);sd_seal(b);assert(q.receive(b,20,0));assert(!q.claim(0));
  sd_header_mode(b,SD_PRESENCE,101,0,0,0,0,1);sd_seal(b);assert(q.receive(b,20,0));
  auto first=q.claim(0);assert(first);sd_put32(b+4,102);sd_seal(b);assert(q.receive(b,20,1));
  auto second=q.claim(1);assert(second&&second!=first);q.release(first);assert(q.owns(second));
  assert(q.postOwned(first,b,20,o,n,1)==503&&n==0);
  service_stop();std::filesystem::remove_all(root);
}
