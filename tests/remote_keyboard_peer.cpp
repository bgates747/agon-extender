// Host qualification bridge to the actual portable engine. Caller locks access.
#include <cstdio>
#include "extender/input/remote_keyboard.hpp"
using namespace agon::extender::input;
static RemoteKeyboard keyboard;
extern "C" {
void key_begin(unsigned boot){keyboard.begin(boot);}
void key_admit(unsigned locale){keyboard.boundary();keyboard.admit(locale);}
void key_physical(unsigned usage,unsigned down){auto k=mapUsbCliKey(usage,0,1);k.down=down;keyboard.physicalKey(k);keyboard.physicalNeutral(!down);}
unsigned key_post(const unsigned char *p,unsigned n,unsigned now){return keyboard.post(p,n,now);}
unsigned key_take(unsigned char *p,unsigned now){
 ProcessedKey k;if(!keyboard.take(k,now))return 0;
 // Same stock packet consumed by EMOS; hardware serializer is qualified by
 // processed_keyboard_test and the eventual physical receiver observation.
 p[0]=0x81;p[1]=4;p[2]=k.keycode;p[3]=k.modifiers;p[4]=k.virtual_key;p[5]=k.down;return 6;
}
unsigned key_status(char *p,unsigned capacity,unsigned now){
 const auto s=keyboard.status(now);
 return std::snprintf(p,capacity,
  "{\"protocol\":1,\"boot\":%u,\"session\":%u,\"sequence\":%u,\"emitted\":%u,"
  "\"accepted\":%u,\"discarded\":%u,\"pending\":%u,\"held\":%u,\"locale\":%u,\"ready\":%s,\"physical_neutral\":%s,\"caps\":%s,\"reason\":%u}",
  s.boot,s.session,s.sequence,s.emitted,s.accepted,s.discarded,s.pending,s.held,s.locale,s.ready?"true":"false",
  s.physical_neutral?"true":"false",s.caps?"true":"false",unsigned(s.reason));
}
}
