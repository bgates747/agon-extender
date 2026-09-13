// Host bridge around the actual P4 queue. Electrical/RTOS behavior is not modeled.
#include "extender/storage/sd_service.hpp"
static agon::extender::storage::SdService service;
extern "C" {
unsigned peer_post(const unsigned char *p,unsigned n,unsigned char *out,unsigned *length,unsigned now) {
    return service.post(p,n,out,*length,now);
}
unsigned peer_take(unsigned char *out,unsigned now) { return service.take(out,now); }
void peer_receive(const unsigned char *p,unsigned n,unsigned now) { service.receive(p,n,now); }
unsigned peer_online(unsigned now) { return service.online(now); }
unsigned peer_boot(void) { return service.boot(); }
unsigned peer_pending(void) { return service.pending(); }
}
