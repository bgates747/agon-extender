// Host ABI around the maintained P4 lease and native key mapping for the
// bounded EMOS emulator peer. Neither USB hardware nor ESP-IDF is emulated.
#include "extender/transport/console_session.hpp"
#include "extender/input/usb_cli_keyboard.hpp"
static agon::extender::transport::ConsoleSession session;
extern "C" bool console_peer_request(const uint8_t *p,uint32_t now,uint32_t nonce,uint8_t *reply) {
  return session.request(p,now,nonce,reply);
}
extern "C" bool console_peer_active() {return session.active();}
extern "C" bool console_peer_key(uint8_t character,uint8_t *packet) {
  for(unsigned modifiers:{0,2})for(unsigned usage=4;usage<57;++usage) {
    auto key=agon::extender::input::mapUsbCliKey(usage,modifiers,1);
    if(key.keycode!=character || !key.virtual_key)continue;
    packet[0]=0x81;packet[1]=4;packet[2]=key.keycode;packet[3]=key.modifiers;
    packet[4]=key.virtual_key;packet[5]=1;return true;
  }
  return false;
}
