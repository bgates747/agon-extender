// Historical command65: consume one CmpS layer. Two calls unpack SRLE2.
if(prefix_n==4 && std::memcmp(prefix,"CmpS",4)==0) {
 size_t total=0;
 for(auto const &block:sourceBuffer){if(block->size()>2097152-total)return;total+=block->size();}
 if(total<14)return;
 auto packed=make_shared_psram<BufferStream>(total);if(!packed||!packed->getBuffer())return;
 size_t offset=0;for(auto const &block:sourceBuffer){std::memcpy(packed->getBuffer()+offset,block->getBuffer(),block->size());offset+=block->size();}
 auto p=packed->getBuffer();uint32_t n=uint32_t(p[4])|uint32_t(p[5])<<8|uint32_t(p[6])<<16|uint32_t(p[7])<<24;
 if(!n||n>1048590)return;
 auto decoded=make_shared_psram<BufferStream>(n);if(!decoded||!decoded->getBuffer())return;
 size_t written=0;if(p4_szip(1,p,total,decoded->getBuffer(),n,&written)||written!=n)return;
 bufferClear(bufferId);buffers[bufferId].push_back(decoded);return;
}
