#include "rle2.hpp"
#include <vector>
#include <random>
#include <cassert>
int main(){std::mt19937 g(0x524c4532);for(unsigned trial=0;trial<100000;++trial){
 size_t n=g()%256;std::vector<uint8_t>s(n),d(g()%512);
 for(auto &v:s)v=uint8_t(g());
 if(n>=14 && g()%2){std::memcpy(s.data(),"Cmpr",4);rle2::put32(s.data()+4,g()%512);std::memcpy(s.data()+8,"RLE2\1\0",6);}
 auto q=rle2::decode(s.data(),s.size(),d.data(),d.size());
 auto q2=rle2::decode_words(s.data(),s.size(),d.data(),d.size());assert(q.status==q2.status&&q.bytes==q2.bytes);
 for(auto &v:s)v=uint8_t((v&63)|(g()%2?192:0));
 std::vector<uint8_t>a(n+14),b(n+14),round(n);
 auto x=rle2::encode(s.data(),n,a.data(),a.size());auto y=rle2::encode_words(s.data(),n,b.data(),b.size());
 assert(x&&y&&x.bytes==y.bytes&&!std::memcmp(a.data(),b.data(),x.bytes));
 auto z=rle2::decode(a.data(),x.bytes,round.data(),n);assert(z&&z.bytes==n&&round==s);
}}
