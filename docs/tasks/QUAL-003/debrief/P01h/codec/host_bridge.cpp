#include "rle2.hpp"
extern "C" int encode(const unsigned char*s,size_t n,unsigned char*d,size_t cap,size_t*out,int opaque){auto r=rle2::encode(s,n,d,cap,opaque);*out=r.bytes;return int(r.status);}
extern "C" int decode(const unsigned char*s,size_t n,unsigned char*d,size_t cap,size_t*out){auto r=rle2::decode(s,n,d,cap);*out=r.bytes;return int(r.status);}

extern "C" int encode_fast(const unsigned char*s,size_t n,unsigned char*d,size_t cap,size_t*out,int opaque){auto r=rle2::encode_fast(s,n,d,cap,opaque);*out=r.bytes;return int(r.status);}

extern "C" int encode_words(const unsigned char*s,size_t n,unsigned char*d,size_t cap,size_t*out,int opaque){auto r=rle2::encode_words(s,n,d,cap,opaque);*out=r.bytes;return int(r.status);}
extern "C" int decode_words(const unsigned char*s,size_t n,unsigned char*d,size_t cap,size_t*out){auto r=rle2::decode_words(s,n,d,cap);*out=r.bytes;return int(r.status);}
