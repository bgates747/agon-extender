// Experiment-only native indexed PNG encoder: zlib APIs, no libpng defaults.
#include <zlib.h>
#include <cstdint>
#include <vector>
#include <cstring>
#include "../codec/rle2.hpp"
static void be(std::vector<uint8_t>&v,uint32_t n){for(int i=24;i>=0;i-=8)v.push_back(n>>i);}
static void chunk(std::vector<uint8_t>&v,const char*t,const std::vector<uint8_t>&d){be(v,d.size());size_t p=v.size();v.insert(v.end(),t,t+4);v.insert(v.end(),d.begin(),d.end());be(v,crc32(0,v.data()+p,4+d.size()));}
extern "C" size_t screen_rle(const uint8_t*s,size_t n,uint8_t*d,size_t cap){auto r=rle2::encode_auto(s,n,d,cap,true);return r?r.bytes:0;}
extern "C" size_t screen_unrle(const uint8_t*s,size_t n,uint8_t*d,size_t cap){auto r=rle2::decode(s,n,d,cap);return r?r.bytes:0;}
extern "C" size_t screen_png(const uint8_t*s,unsigned w,unsigned h,int level,int strategy,int filter,uint8_t*d,size_t cap){
 if(!w||!h||w>512||h>384||filter<0||filter>2)return 0;
 std::vector<uint8_t> rows((w+1)*h);
 for(unsigned y=0;y<h;y++){rows[y*(w+1)]=filter;for(unsigned x=0;x<w;x++){unsigned v=s[y*w+x];unsigned pred=filter==1?(x?s[y*w+x-1]:0):filter==2?(y?s[(y-1)*w+x]:0):0;rows[y*(w+1)+1+x]=v-pred;}}
 z_stream z{};if(deflateInit2(&z,level,Z_DEFLATED,15,8,strategy)!=Z_OK)return 0;
 std::vector<uint8_t> packed(deflateBound(&z,rows.size()));z.next_in=rows.data();z.avail_in=rows.size();z.next_out=packed.data();z.avail_out=packed.size();int status=deflate(&z,Z_FINISH);size_t n=z.total_out;deflateEnd(&z);if(status!=Z_STREAM_END)return 0;packed.resize(n);
 std::vector<uint8_t> v{137,80,78,71,13,10,26,10},ihdr,palette;
 be(ihdr,w);be(ihdr,h);ihdr.insert(ihdr.end(),{8,3,0,0,0});chunk(v,"IHDR",ihdr);
 for(unsigned c=0;c<64;c++){palette.push_back((c&3)*85);palette.push_back(((c>>2)&3)*85);palette.push_back(((c>>4)&3)*85);}chunk(v,"PLTE",palette);chunk(v,"IDAT",packed);chunk(v,"IEND",{});
 if(v.size()>cap)return 0;memcpy(d,v.data(),v.size());return v.size();
}
