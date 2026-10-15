// Offline adapter for the maintained VDP TurboVega codec. Every encoding is
// decoded and compared before emitting bytes. Host-only build; no bench access.
#include <vector>
#include <fstream>
#include <iterator>
#include <cstdio>
#include <cstdlib>
void *ps_malloc(size_t size) { return std::malloc(size); }
void heap_caps_free(void *p) { std::free(p); }
void debug_log(const char *, ...) {}
#include "compression-host.h"
void compressed(void *context, uint8_t value) {
 auto *state=static_cast<CompressionData*>(context);
 static_cast<std::vector<uint8_t>*>(state->context)->push_back(value);
}
bool decompressed(void *context, uint8_t value) {
 auto *state=static_cast<DecompressionData*>(context);
 auto *output=static_cast<std::vector<uint8_t>*>(state->context);
 if(output->size()>=state->orig_size)return false;
 output->push_back(value);return true;
}
int main(int argc,char **argv) {
 if(argc!=3)return 2;
 std::ifstream in(argv[1],std::ios::binary);
 if(!in)return 3;
 std::vector<uint8_t> raw((std::istreambuf_iterator<char>(in)),{}),coded,decoded;
 CompressionData encoder;agon_init_compression(&encoder,&coded,compressed);
 for(auto byte:raw)agon_compress_byte(&encoder,byte);
 agon_finish_compression(&encoder);
 DecompressionData decoder;agon_init_decompression(&decoder,&decoded,decompressed,raw.size());
 for(auto byte:coded)agon_decompress_byte(&decoder,byte);
 if(raw!=decoded)return 4;
 CompressionFileHeader header={{'C','m','p'},'T',static_cast<uint32_t>(raw.size())};
 std::ofstream out(argv[2],std::ios::binary);
 out.write(reinterpret_cast<char*>(&header),sizeof(header));
 out.write(reinterpret_cast<char*>(coded.data()),coded.size());return out?0:5;
}
