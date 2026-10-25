// HTTP admission binds the controller UDP sender to its real IPv4 source.
// IDF's dual-stack HTTP listener reports IPv4 clients as mapped IPv6 peers.
// Preserve network byte order; genuine IPv6 needs a separate UDP contract.
#pragma once
#include <cstdint>
#include <cstring>
#if defined(ESP_PLATFORM)
#include <lwip/sockets.h>
#else
#include <sys/socket.h>
#include <netinet/in.h>
#endif
namespace agon::extender::controller {
inline bool httpPeerIPv4(const sockaddr_storage &peer, socklen_t length,
                         std::uint32_t &address) noexcept {
  address=0;
  if(peer.ss_family==AF_INET && length>=sizeof(sockaddr_in)){
    sockaddr_in v4{};std::memcpy(&v4,&peer,sizeof(v4));
    address=v4.sin_addr.s_addr;return true;
  }
#if !defined(ESP_PLATFORM) || LWIP_IPV6
  if(peer.ss_family==AF_INET6 && length>=sizeof(sockaddr_in6)){
    sockaddr_in6 v6{};std::memcpy(&v6,&peer,sizeof(v6));
    const auto *bytes=reinterpret_cast<const std::uint8_t*>(&v6.sin6_addr);
    for(unsigned i=0;i<10;++i)if(bytes[i])return false;
    if(bytes[10]!=0xff || bytes[11]!=0xff)return false;
    std::memcpy(&address,bytes+12,sizeof(address));return true;
  }
#endif
  return false;
}
}
