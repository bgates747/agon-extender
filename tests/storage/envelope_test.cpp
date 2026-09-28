#include "extender/storage/envelope.hpp"
#include <cassert>
#include <vector>
int main() {
  for(int size=0;size<=255;++size) {
    std::vector<int> bytes{size};
    for(int i=0;i<size;++i)bytes.push_back(i%256);
    bytes.push_back(12); // Following VDU clear must remain untouched.
    unsigned pos=0,received=0;
    auto read=[&](){return pos<bytes.size()?bytes[pos++]:-1;};
    auto receive=[&](const std::uint8_t *p,unsigned n){
      ++received;assert(n==unsigned(size));for(unsigned i=0;i<n;++i)assert(p[i]==i%256);
    };
    assert(agon::extender::storage::readEnvelope(read,receive));
    assert(received==unsigned(size>=20&&size<=240));assert(read()==12);
    // Every truncated prefix must fail, without publishing partial data.
    for(int limit=0;limit<=size;++limit) {
      pos=received=0;
      auto shortRead=[&](){return pos<unsigned(limit)?bytes[pos++]:-1;};
      assert(!agon::extender::storage::readEnvelope(shortRead,receive));assert(!received);
    }
  }
}
