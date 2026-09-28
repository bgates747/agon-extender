// Private F6 payload reader, called only at a real VDU 23,0 command boundary.
#pragma once
#include <cstdint>
namespace agon::extender::storage {
template<class Read, class Receive> bool readEnvelope(Read read, Receive receive) {
  int length=read();
  if(length<0)return false;
  std::uint8_t packet[240];
  for(int i=0;i<length;++i) {
    int byte=read();
    if(byte<0)return false;
    if(i<240)packet[i]=std::uint8_t(byte);
  }
  // Invalid lengths still consume their whole declared body, never as VDU.
  if(length>=20 && length<=240)receive(packet,unsigned(length));
  return true;
}
}
