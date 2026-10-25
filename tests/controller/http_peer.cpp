#include "extender/input/controller/http_peer.hpp"
#include <cassert>
#include <unistd.h>
using agon::extender::controller::httpPeerIPv4;
int main(){
  sockaddr_storage peer{};std::uint32_t address=0;
  sockaddr_in v4{};v4.sin_family=AF_INET;v4.sin_addr.s_addr=htonl(0x7f000001);
  std::memcpy(&peer,&v4,sizeof(v4));
  assert(httpPeerIPv4(peer,sizeof(v4),address)&&address==v4.sin_addr.s_addr);
  assert(!httpPeerIPv4(peer,sizeof(v4)-1,address));
  sockaddr_in6 mapped{};mapped.sin6_family=AF_INET6;
  auto *bytes=reinterpret_cast<std::uint8_t*>(&mapped.sin6_addr);
  bytes[10]=bytes[11]=0xff;std::memcpy(bytes+12,&v4.sin_addr.s_addr,4);
  std::memset(&peer,0,sizeof(peer));std::memcpy(&peer,&mapped,sizeof(mapped));
  assert(httpPeerIPv4(peer,sizeof(mapped),address)&&address==v4.sin_addr.s_addr);
  assert(!httpPeerIPv4(peer,sizeof(mapped)-1,address));
  auto genuine=mapped;reinterpret_cast<std::uint8_t*>(&genuine.sin6_addr)[0]=0x20;
  std::memcpy(&peer,&genuine,sizeof(genuine));assert(!httpPeerIPv4(peer,sizeof(genuine),address));
  peer.ss_family=AF_UNSPEC;assert(!httpPeerIPv4(peer,sizeof(peer),address));
  // Real IPv4 loopback connection accepted by an IPv6 socket, as on P4 HTTP.
  int listener=socket(AF_INET6,SOCK_STREAM,0);assert(listener>=0);
  int only=0;assert(setsockopt(listener,IPPROTO_IPV6,IPV6_V6ONLY,&only,sizeof(only))==0);
  assert(bind(listener,reinterpret_cast<sockaddr*>(&mapped),sizeof(mapped))==0);
  socklen_t n=sizeof(mapped);assert(getsockname(listener,reinterpret_cast<sockaddr*>(&mapped),&n)==0);
  assert(listen(listener,1)==0);v4.sin_port=mapped.sin6_port;
  int client=socket(AF_INET,SOCK_STREAM,0);assert(client>=0);
  assert(connect(client,reinterpret_cast<sockaddr*>(&v4),sizeof(v4))==0);
  n=sizeof(peer);int accepted=accept(listener,reinterpret_cast<sockaddr*>(&peer),&n);assert(accepted>=0);
  assert(peer.ss_family==AF_INET6); // The old admission check rejects this.
  assert(httpPeerIPv4(peer,n,address)&&address==v4.sin_addr.s_addr);
  close(accepted);close(client);close(listener);
}
