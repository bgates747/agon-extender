// REMOTE-009: bulk HTTP and the admitted mainboard UART never wait on one
// another per record. One job retains the physical-card lease through staging
// and UART work; a separate P4 task drives the existing checksum-free carrier.
// No firmware/boot changes, auto-execution, background CLI admission or retry
// after reset. Failed files remain private for deliberate recovery.
#include "engine.hpp"
#include "http.hpp"
#if defined(AGON_EXTENDER_PARALLEL_UPLOAD)
#include "../../transport/p4_upload_coordinator.hpp"
#endif
#if defined(AGON_EXTENDER_NATIVE_BUILD)
// All native storage units retain the profile's selected-board provenance.
// Physical SD/power initialization remains owned by local/media.hpp.
#include "agon_extender_board_config.hpp"
#endif
#include "../local/media.hpp"
#include "../sd_target.hpp"
#include "../../display/rolling/task_memory.hpp"
#include <esp_random.h>
#include <esp_timer.h>
#include <atomic>
#include <cerrno>
#include <fcntl.h>
#include <memory>
#include <new>
#include <unistd.h>

namespace agon::extender::storage::fast {
namespace {
enum Phase : unsigned { Idle, Receiving, Queued, Running, Complete, Failed };
struct Snapshot {
  unsigned phase=Idle;
  std::uint32_t id=0;
  Progress progress{};
  std::uint64_t stageUs=0, mainboardUs=0;
};
portMUX_TYPE mutex=portMUX_INITIALIZER_UNLOCKED;
Snapshot state;
Plan plan;
std::uint32_t serverBoot=0;
std::atomic<bool> occupied{false};
std::string dataPath, statePath;
bool metadataOwned=false,dataOwned=false;
unsigned token=0;
std::unique_ptr<local_sd::MediaLease> lease;
Snapshot snapshot() {
  portENTER_CRITICAL(&mutex);auto s=state;portEXIT_CRITICAL(&mutex);return s;
}
void publish(const Snapshot &s) {
  portENTER_CRITICAL(&mutex);state=s;portEXIT_CRITICAL(&mutex);
}
// Only the owning handler/worker writes metadata. Sync at job boundaries,
// never after each UART record. Unknown existing files are never truncated.
bool metadata(const Snapshot &s) {
  int fd=open(statePath.c_str(),O_WRONLY|O_CREAT|(metadataOwned?O_TRUNC:O_EXCL),0600);
  if(fd<0)return false;
  metadataOwned=true;
  FILE *f=fdopen(fd,"w");
  if(!f){close(fd);return false;}
  bool ok=std::fprintf(f,"EXTFAST1\n%08lx\n%08lx\n%u\n%s\n%lu\n%lu\n%u\n%u\n%u\n",
    (unsigned long)serverBoot,(unsigned long)plan.id,unsigned(plan.upload),plan.path.c_str(),
    (unsigned long)s.progress.size,(unsigned long)s.progress.bytes,s.phase,
    s.progress.error,unsigned(plan.activate))>0;
  if(std::fflush(f)||fsync(fileno(f)))ok=false;
  if(std::fclose(f))ok=false;
  return ok;
}
esp_err_t reply(httpd_req_t *r,const char *status,const char *text) {
  httpd_resp_set_status(r,status);httpd_resp_set_hdr(r,"Cache-Control","no-store");
  return httpd_resp_sendstr(r,text);
}
bool header(httpd_req_t *r,const char *name,char *out,size_t n) {
  return httpd_req_get_hdr_value_len(r,name)>0 &&
         httpd_req_get_hdr_value_str(r,name,out,n)==ESP_OK;
}
bool number(const char *s,std::uint32_t &n) {
  if(std::strlen(s)!=8)return false;
  n=0;
  for(unsigned i=0;i<8;++i){char c=s[i];unsigned x;
    if(c>='0'&&c<='9')x=c-'0';else if(c>='a'&&c<='f')x=c-'a'+10;else return false;
    n=(n<<4)|x;
  }
  return n!=0;
}
bool identified(httpd_req_t *r) {
  char id[9]{},boot[9]{};std::uint32_t i=0,b=0;
  return header(r,"X-Extender-Job",id,sizeof(id)) && number(id,i) &&
    header(r,"X-Extender-Boot",boot,sizeof(boot)) && number(boot,b) &&
    i==snapshot().id && b==serverBoot && occupied.load();
}
esp_err_t status(httpd_req_t *r) {
  auto s=snapshot();char body[640];unsigned nativePhase=0,nativeOutcome=0;
#if defined(AGON_EXTENDER_PARALLEL_UPLOAD)
  auto &m=transport::uploadMailbox;
  if(m.job.load()==s.id) {
    nativePhase=m.status();
    if(nativePhase>=transport::P4UploadMailbox::returned)nativeOutcome=m.outcome.load();
  }
#endif
  int n=std::snprintf(body,sizeof(body),
    "{\"protocol\":1,\"boot\":%lu,\"id\":%lu,\"phase\":%u,\"bytes\":%lu,\"size\":%lu,"
    "\"records\":%lu,\"error\":%u,\"remote_status\":%u,\"filesystem\":%u,"
    "\"stage_us\":%llu,\"mainboard_us\":%llu,\"parallel_prepare_us\":%llu,"
    "\"parallel_active_ms\":%lu,\"parallel_handover_ms\":%lu,\"parallel_phase\":%u,\"parallel_outcome\":%u}",
    (unsigned long)serverBoot,(unsigned long)s.id,s.phase,(unsigned long)s.progress.bytes,
    (unsigned long)s.progress.size,(unsigned long)s.progress.records,s.progress.error,
    s.progress.remoteStatus,s.progress.filesystem,(unsigned long long)s.stageUs,
    (unsigned long long)s.mainboardUs,(unsigned long long)s.progress.parallelPrepareUs,
    (unsigned long)s.progress.parallelActiveMs,(unsigned long)s.progress.parallelHandoverMs,nativePhase,nativeOutcome);
  httpd_resp_set_type(r,"application/json");httpd_resp_set_hdr(r,"Cache-Control","no-store");
  return httpd_resp_send(r,body,n);
}
class QueueLink final : public Link {
#if defined(AGON_EXTENDER_PARALLEL_UPLOAD)
  std::uint64_t prepareUs_{};
#endif
public:
  bool exchange(const std::uint8_t *p,unsigned n,std::uint8_t *out,unsigned &size) override {
    const auto start=esp_timer_get_time();
#if defined(AGON_EXTENDER_PARALLEL_UPLOAD)
    const bool bulk=n==SD_HEADER+8 && p[12]==SD_PARALLEL_WRITE;
    if(bulk && !transport::uploadMailbox.offer())return false;
    const std::int64_t deadline=bulk?610000000LL:30000000LL;
#else
    const std::int64_t deadline=30000000LL;
#endif
    do {
      auto code=sdFastPost(token,p,n,out,size);
      if(code==200)return true;
      if(code!=202)return false;
      // Local task scheduling only. No HTTP polling, disk journal or host wait.
      vTaskDelay(1);
    } while(esp_timer_get_time()-start<deadline);
    return false;
  }
#if defined(AGON_EXTENDER_PARALLEL_UPLOAD)
  bool parallelUploads() const override { return true; }
  bool prepareUpload(FILE *file,std::uint32_t length,std::uint32_t id) override {
    auto &m=transport::uploadMailbox;
    const auto started=esp_timer_get_time();
    if(!m.load(file,length,id))return false;
    const auto began=esp_timer_get_time();
    while(esp_timer_get_time()-began<5000000) {
      auto phase=m.status();
      if(phase==transport::P4UploadMailbox::prepared){prepareUs_=esp_timer_get_time()-started;return true;}
      if(phase==transport::P4UploadMailbox::refused || phase==transport::P4UploadMailbox::cleanupFault)return false;
      vTaskDelay(1);
    }
    return false;
  }
  bool uploadReturned(Progress &p) const override {
    if(transport::uploadMailbox.status()!=transport::P4UploadMailbox::returned)return false;
    p.parallelPrepareUs=prepareUs_;
    p.parallelActiveMs=transport::uploadMailbox.activeMs;
    p.parallelHandoverMs=transport::uploadMailbox.handoverMs;
    return transport::uploadMailbox.status()==transport::P4UploadMailbox::returned &&
        transport::uploadMailbox.outcome.load()==unsigned(transport::P4ParallelUpload::Result::complete);
  }
  bool finishUpload() {
    auto &m=transport::uploadMailbox;
    if(m.status()==transport::P4UploadMailbox::free)return true;
    m.retire();const auto began=esp_timer_get_time();
    while(esp_timer_get_time()-began<10000000) {
      auto phase=m.status();
      if(phase==transport::P4UploadMailbox::free)return true;
      if(phase==transport::P4UploadMailbox::cleanupFault)return false;
      vTaskDelay(1);
    }
    return false;
  }
#endif
  void progress(const Progress &p) override {
    portENTER_CRITICAL(&mutex);state.progress=p;portEXIT_CRITICAL(&mutex);
  }
};
void worker(void *) {
  auto s=snapshot();s.phase=Running;publish(s);
  const auto started=esp_timer_get_time();
  FILE *f=std::fopen(dataPath.c_str(),plan.upload?"rb":"wb");
  // FILE buffering coalesces212/216-byte protocol records into ordinary SD I/O.
  std::unique_ptr<char[]> buffer(new(std::nothrow) char[8192]);
  if(f && buffer)std::setvbuf(f,buffer.get(),_IOFBF,8192);
  std::uint32_t boot=0;
  if(!f||!buffer)s.progress.error=Local;
  else if(!(token=sdFastClaim(boot)) || boot!=plan.boot)s.progress.error=Transport;
  else {
    QueueLink link;Engine engine(link,esp_random()|1U);s.progress=engine.run(plan,f);
#if defined(AGON_EXTENDER_PARALLEL_UPLOAD)
    (void)link.uploadReturned(s.progress);
    if(!link.finishUpload())s.progress.error=Transport;
#endif
  }
  if(f){
    if(!plan.upload && (std::fflush(f)||fsync(fileno(f))))s.progress.error=Local;
    if(std::fclose(f))s.progress.error=Local;
  }
  sdFastRelease(token);token=0;
  s.mainboardUs=esp_timer_get_time()-started;
  s.phase=s.progress.error?Failed:Complete;
  if(!metadata(s)){s.phase=Failed;s.progress.error=Local;}
  // FreeRTOS task deletion does not unwind C++ automatic objects.
  buffer.reset();
  lease.reset(); // terminal publication occurs only after UART/media handback
  publish(s);
  deleteVideoWorker(nullptr);
}
esp_err_t admit(httpd_req_t *r) {
  // Admission is explicit host intent, never a browser-origin side effect.
  if(httpd_req_get_hdr_value_len(r,"Origin"))return reply(r,"400 Bad Request","Origin not accepted");
  char id[9]{},boot[9]{},operation[4]{},path[121]{},activate[2]{};
  std::uint32_t job=0,instance=0;
  Plan candidate;
  if(!header(r,"X-Extender-Job",id,sizeof(id))||!number(id,job)||
     !header(r,"X-Extender-Boot",boot,sizeof(boot))||!number(boot,instance)||instance!=serverBoot||
     !header(r,"X-Extender-Operation",operation,sizeof(operation))||
     (std::strcmp(operation,"put")&&std::strcmp(operation,"get"))||
     !header(r,"X-Extender-Path",path,sizeof(path)))return reply(r,"400 Bad Request","Invalid job");
  candidate.upload=!std::strcmp(operation,"put");candidate.id=job;candidate.path=path;
  if(header(r,"X-Extender-Activate",activate,sizeof(activate))){
    if(std::strcmp(activate,"1"))return reply(r,"400 Bad Request","Invalid activation");
    candidate.activate=true;
  }
  if(r->content_len>Quota)return reply(r,"400 Bad Request","File exceeds32MiB staging limit");
  candidate.size=r->content_len;candidate.boot=1; // actual foreground boot below
  // This job API completes one file operation. A stage-only upload would leave
  // sdserve's session active after this worker relinquishes its private queue;
  // keep that two-step workflow in the existing session-owning RPC client.
  if((candidate.upload&&!candidate.activate)||(!candidate.upload&&r->content_len)||!valid(candidate))
    return reply(r,"400 Bad Request","Invalid file parameters; put requires activation");
  bool expected=false;
  if(!occupied.compare_exchange_strong(expected,true))return reply(r,"409 Conflict","A job is retained; inspect status");
  bool online,pending;unsigned protocol;
  sdStatus(std::uint32_t(esp_timer_get_time()/1000),online,pending,candidate.boot,protocol);
  lease.reset(new(std::nothrow) local_sd::MediaLease);
  std::string directory;
  if(!online||pending||protocol!=2||!lease||!(*lease)||!local_sd::prepareSpool(directory)){
    lease.reset();occupied=false;return reply(r,"503 Service Unavailable","Requires fast foreground listener and free P4 SD");
  }
  plan=std::move(candidate);metadataOwned=dataOwned=false;
  char leaf[40];std::snprintf(leaf,sizeof(leaf),"/fast-%08lx-%08lx",(unsigned long)serverBoot,(unsigned long)job);
  dataPath=directory+leaf+".data";statePath=directory+leaf+".state";
  Snapshot s;s.id=job;s.phase=Receiving;s.progress.size=plan.size;publish(s);
  const auto started=esp_timer_get_time();
  int fd=open(dataPath.c_str(),O_WRONLY|O_CREAT|O_EXCL,0600);
  dataOwned=fd>=0;
  FILE *f=fd<0?nullptr:fdopen(fd,"wb");if(fd>=0&&!f)close(fd);
  bool ok=f && metadata(s);
  char bytes[1024];std::uint32_t received=0;
  while(ok&&received<plan.size){
    int n=httpd_req_recv(r,bytes,std::min<std::uint32_t>(sizeof(bytes),plan.size-received));
    if(n<=0||esp_timer_get_time()-started>300000000LL||std::fwrite(bytes,1,n,f)!=unsigned(n)){ok=false;break;}
    received+=n;
  }
  if(f){if(std::fflush(f)||fsync(fileno(f)))ok=false;if(std::fclose(f))ok=false;}
  s.stageUs=esp_timer_get_time()-started;s.phase=ok?Queued:Failed;
  if(!ok)s.progress.error=Local;
  if(!metadataOwned||!metadata(s)){s.phase=Failed;s.progress.error=Local;}
  publish(s);
  if(s.phase==Failed){lease.reset();return reply(r,"500 Internal Server Error","Staging failed; inspect retained job");}
  // Scheduling control (REMOTE-009): the continuously runnable UART parser
  // owns core0 at priority3; a priority1 worker can only use core1's gaps.
  // Run the blocked file worker above that parser, below drawing/USB/output.
  // QueueLink still sleeps while awaiting replies; no busy loop or new wire
  // behavior. Physical A/B results must establish whether this changes rate.
  if(createVideoWorker(worker,"sd-fast",8192,nullptr,4,nullptr,tskNO_AFFINITY)!=pdPASS){
    s.phase=Failed;s.progress.error=Local;(void)metadata(s);lease.reset();publish(s);
    return reply(r,"503 Service Unavailable","Worker unavailable; job retained");
  }
  httpd_resp_set_status(r,"202 Accepted");return status(r);
}
esp_err_t data(httpd_req_t *r) {
  if(!identified(r)||snapshot().phase!=Complete||plan.upload)return reply(r,"409 Conflict","No completed download");
  local_sd::MediaLease access;if(!access)return reply(r,"503 Service Unavailable","P4 SD busy");
  FILE *f=std::fopen(dataPath.c_str(),"rb");if(!f)return reply(r,"500 Internal Server Error","Stage missing");
  httpd_resp_set_type(r,"application/octet-stream");httpd_resp_set_hdr(r,"Cache-Control","no-store");
  char bytes[1024];std::uint32_t at=0;bool ok=true;auto total=snapshot().progress.size;
  while(at<total){auto n=std::fread(bytes,1,std::min<std::uint32_t>(sizeof(bytes),total-at),f);
    if(!n||httpd_resp_send_chunk(r,bytes,n)!=ESP_OK){ok=false;break;}at+=n;
  }
  if(std::ferror(f))ok=false;
  if(std::fclose(f))ok=false;
  return ok?httpd_resp_send_chunk(r,nullptr,0):ESP_FAIL;
}
esp_err_t release(httpd_req_t *r) {
  if(httpd_req_get_hdr_value_len(r,"Origin")||!identified(r))return reply(r,"409 Conflict","Job identity mismatch");
  auto s=snapshot();char discard[2]{};
  if(s.phase!=Complete && !(s.phase==Failed&&header(r,"X-Extender-Discard",discard,sizeof(discard))&&!std::strcmp(discard,"1")))
    return reply(r,"409 Conflict","Job active or failed; explicit discard required");
  local_sd::MediaLease access;if(!access)return reply(r,"503 Service Unavailable","P4 SD busy");
  // Only paths created by this boot/job; no directory scan or recovery purge.
  if((dataOwned&&unlink(dataPath.c_str())&&errno!=ENOENT)||(metadataOwned&&unlink(statePath.c_str())&&errno!=ENOENT))
    return reply(r,"500 Internal Server Error","Stage cleanup failed; retained job");
  publish(Snapshot{});occupied=false;return reply(r,"200 OK","Released");
}
} // namespace
bool routes(httpd_handle_t server) {
  if(!serverBoot)serverBoot=esp_random()|1U;
  for(auto pair:{std::pair<httpd_method_t,esp_err_t(*)(httpd_req_t*)>{HTTP_GET,status},
                 {HTTP_POST,admit},{HTTP_DELETE,release}}){
    httpd_uri_t u{};u.uri="/sd/fast";u.method=pair.first;u.handler=pair.second;
    if(httpd_register_uri_handler(server,&u)!=ESP_OK)return false;
  }
  httpd_uri_t u{};u.uri="/sd/fast/data";u.method=HTTP_GET;u.handler=data;
  return httpd_register_uri_handler(server,&u)==ESP_OK;
}
} // namespace agon::extender::storage::fast
