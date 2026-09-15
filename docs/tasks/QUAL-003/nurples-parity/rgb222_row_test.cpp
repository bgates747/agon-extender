#include <array>
#include <cassert>
#include <cstdint>
#include <iostream>
#include "extender/display/rgb222_row.hpp"
int main() {
  alignas(8) std::array<std::uint8_t,1048> source{},destination{},expected{};
  unsigned cases=0;
  for(int width=0;width<=1024;width+=4)
    for(int from=0;from<4;++from) for(int to=0;to<4;++to)
      for(int seed=0;seed<16;++seed) {
        for(unsigned i=0;i<source.size();++i) source[i]=std::uint8_t(i*37+seed*19);
        destination.fill(0xa5);expected=destination;
        auto before=source;
        for(int x=0;x<width;++x) expected[8+to+x]=source[8+from+(x^2)]&63;
        agon::extender::display::normalizeRgb222Row(source.data()+8+from,destination.data()+8+to,width);
        assert(destination==expected && source==before);++cases;
      }
  std::cout << "RGB222 scalar equivalence/canaries/alignment=" << cases << " pass\n";
}
