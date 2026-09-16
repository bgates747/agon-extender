// P01h candidate only: header-dispatched RLE2, leaving official TVC path below.
// No legacy decoder is reused. Publish only after complete bounded decoding.
if (sourceBuffer.empty()) return;
uint8_t prefix[4]{};size_t prefix_n=0;
for (auto const &block:sourceBuffer) {
 for(size_t i=0;i<block->size() && prefix_n<4;++i)prefix[prefix_n++]=block->getBuffer()[i];
 if(prefix_n==4)break;
}
if(prefix_n==4 && std::memcmp(prefix,"Cmpr",4)==0) {
 size_t total=0;
 for(auto const &block:sourceBuffer){if(block->size()>1048590-total)return;total+=block->size();}
 if(total<14)return;
 auto packed=make_shared_psram<BufferStream>(total);
 if(!packed || !packed->getBuffer())return;
 size_t offset=0;
 for(auto const &block:sourceBuffer){std::memcpy(packed->getBuffer()+offset,block->getBuffer(),block->size());offset+=block->size();}
 auto h=rle2::inspect(packed->getBuffer(),total);
 if(!h || !h.bytes || h.bytes>1048576)return;
 auto output=make_shared_psram<BufferStream>(h.bytes);
 if(!output || !output->getBuffer())return;
 auto decoded=rle2::decode_words(packed->getBuffer(),total,output->getBuffer(),h.bytes);
 if(!decoded)return;
 // sourceBuffer can refer to destination: all source use finishes before clear.
 bufferClear(bufferId);buffers[bufferId].push_back(output);
 return;
}
