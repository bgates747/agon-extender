// Executes the actual HTTP admission/worker/cleanup with fake SDK scheduling.
// No socket, emulator, board, firmware installation or network access.
#include "extender/storage/fast/http.cpp"
#include <cassert>
#include <filesystem>
#include <fstream>
extern "C" {
void fs_root(const char *);
int service_init_mode(const char *,std::uint32_t,int);
unsigned service_request(const std::uint8_t *,unsigned,std::uint8_t *);
void service_stop();
}
using namespace agon::extender;
using namespace agon::extender::storage;
using namespace agon::extender::storage::fast;
TaskFunction_t pendingWorker=nullptr;
std::string spoolDir;
bool missingMedia=false;
namespace agon::extender::local_sd {
bool prepareSpool(std::string &out) noexcept{out=spoolDir;return !missingMedia;}
const char *mediaRoot() noexcept{return spoolDir.c_str();}
}
void processQueue(){
  std::uint8_t req[240],out[240];auto now=std::uint32_t(esp_timer_get_time()/1000);
  unsigned n=sdTake(req,now);
  if(n){auto size=service_request(req,n,out);assert(size);sdReceive(out,size,now);}
}
void presence(unsigned boot=101){
  std::uint8_t b[20];sd_header_mode(b,SD_PRESENCE,boot,0,0,0,0,1);sd_seal(b);
  sdReceive(b,20,std::uint32_t(esp_timer_get_time()/1000));
}
httpd_req_t request(unsigned id,const char *op="put",const char *path="/test/file",std::string payload="abc"){
  httpd_req_t r;r.body=payload;r.content_len=payload.size();char a[9],b[9];
  snprintf(a,sizeof(a),"%08x",id);snprintf(b,sizeof(b),"%08x",serverBoot);
  r.headers={{"X-Extender-Job",a},{"X-Extender-Boot",b},{"X-Extender-Operation",op},
             {"X-Extender-Path",path},{"X-Extender-Activate","1"}};
  if(!strcmp(op,"get"))r.headers.erase("X-Extender-Activate");return r;
}
void runWorker(){assert(pendingWorker);auto f=pendingWorker;pendingWorker=nullptr;f(nullptr);}
void drop(unsigned id,bool discard=false){
  auto r=request(id);if(discard)r.headers["X-Extender-Discard"]="1";
  release(&r);assert(r.status=="200 OK");assert(snapshot().phase==Idle);
}
int main(int argc,char **argv){
  assert(argc==2);std::filesystem::path root=argv[1];
  std::filesystem::create_directories(root/"test");std::filesystem::create_directories(root/"spool");
  spoolDir=(root/"spool").string();fs_root(root.c_str());assert(service_init_mode("/test",101,1));
  routes(reinterpret_cast<void *>(1));presence();
  auto r=request(1);admit(&r);assert(r.status=="202 Accepted"&&snapshot().phase==Queued);
  auto other=request(2);admit(&other);assert(other.status=="409 Conflict");
  auto premature=request(1);release(&premature);assert(premature.status=="409 Conflict");
  runWorker();assert(snapshot().phase==Complete&&snapshot().progress.bytes==3);
  assert(!local_sd::mediaOwned.test_and_set());local_sd::mediaOwned.clear(); // worker handed card back
  drop(1);
  auto get=request(3,"get","/test/file","");admit(&get);runWorker();assert(snapshot().phase==Complete);
  auto served=request(3);data(&served);assert(served.response=="abc");
  auto broken=request(3);broken.failSend=true;assert(data(&broken)==ESP_FAIL);
  assert(snapshot().phase==Complete);drop(3);
  // A lost foreground boot between admission and worker entry must not execute.
  auto reset=request(4);admit(&reset);presence(102);runWorker();
  assert(snapshot().phase==Failed&&snapshot().progress.error==Transport);
  auto noDiscard=request(4);release(&noDiscard);assert(noDiscard.status=="409 Conflict");drop(4,true);
  service_stop();assert(service_init_mode("/test",103,1));presence(103);
  // P4 missing/busy storage rejects before starting any mainboard work.
  missingMedia=true;auto absent=request(5);admit(&absent);assert(absent.status=="503 Service Unavailable");
  assert(!occupied);missingMedia=false;
  {local_sd::MediaLease owner;auto busy=request(5);admit(&busy);assert(busy.status=="503 Service Unavailable");assert(!occupied);}
  // An interrupted HTTP upload creates no mainboard job, retains local stage.
  auto partial=request(6);partial.failRead=true;admit(&partial);
  assert(snapshot().phase==Failed&&!pendingWorker);drop(6,true);
  // Unknown colliding files must survive even explicit failed-job discard.
  char leaf[70];snprintf(leaf,sizeof(leaf),"/fast-%08lx-%08x.data",(unsigned long)serverBoot,7);
  auto unknown=spoolDir+leaf;{std::ofstream f(unknown);f<<"keep me";}
  auto collision=request(7);admit(&collision);assert(snapshot().phase==Failed);drop(7,true);
  assert(std::filesystem::exists(unknown));
  // Origin, traversal and excessive HTTP lengths fail before admission.
  auto origin=request(8);origin.headers["Origin"]="http://other";admit(&origin);assert(origin.status=="400 Bad Request");
  auto stageOnly=request(8);stageOnly.headers.erase("X-Extender-Activate");admit(&stageOnly);assert(stageOnly.status=="400 Bad Request");
  auto invalid=request(9,"put","/test/../file");admit(&invalid);assert(invalid.status=="400 Bad Request");
  auto giant=request(10);giant.content_len=UINT64_C(0x100000000);admit(&giant);assert(giant.status=="400 Bad Request");
  service_stop();std::filesystem::remove_all(root);
}
