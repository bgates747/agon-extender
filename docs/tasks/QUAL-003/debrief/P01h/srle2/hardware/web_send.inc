  // The HTTP task owns scratch and sends; the snapshot lease is immutable.
  // No graphics lock is acquired for compression. Failed/busy entropy coding
  // retains a valid raw/RLE2 choice, and every selected message is complete.
  std::array<OpaqueMessageSegment,2> compressed{};
  uint8_t compressed_header[40];
  auto segments=view.segments.data();size_t count=view.segment_count;
  size_t transmitted=view.total_bytes;
  bool chose_rle2=false;
  if((rle2_requested||srle2_requested) && rle2_scratch && count==2 && segments[0].size==32) {
    auto h=segments[0].data;const auto n=segments[1].size;
    const size_t width=size_t(h[12])|(size_t(h[13])<<8);
    const size_t height=size_t(h[14])|(size_t(h[15])<<8);
    if(std::memcmp(h,"EVF1",4)==0 && h[6]==2 && width<=512 && height<=384 && n<=196608 && n==width*height && rle2::get32(h+16)==width && rle2::get32(h+20)==n){
      auto begin=esp_timer_get_time();auto encoded=rle2::encode_auto(segments[1].data,n,rle2_scratch,196622,true);
      rle2_encode_us+=esp_timer_get_time()-begin;++rle2_attempts;
      if(encoded && encoded.bytes<n){
        std::memcpy(compressed_header,h,32);compressed_header[2]='R';
        compressed[0]={compressed_header,32};compressed[1]={rle2_scratch,encoded.bytes};
        segments=compressed.data();count=2;transmitted=32+encoded.bytes;++rle2_frames;chose_rle2=true;
      }
      if(encoded && srle2_requested && srle2_scratch){
        size_t bytes=0;begin=esp_timer_get_time();
        const int status=p4_szip(0,rle2_scratch,encoded.bytes,srle2_scratch,393244,&bytes);
        srle2_encode_us+=esp_timer_get_time()-begin;++srle2_attempts;
        if(status)++srle2_failures;
        if(!status && 40+bytes<transmitted){
          if(chose_rle2)--rle2_frames;
          std::memcpy(compressed_header,h,32);compressed_header[2]='S';compressed_header[5]=40;
          rle2::put32(compressed_header+32,bytes);rle2::put32(compressed_header+36,encoded.bytes);
          compressed[0]={compressed_header,40};compressed[1]={srle2_scratch,bytes};
          segments=compressed.data();count=2;transmitted=40+bytes;++srle2_frames;
        }
      }
    }
  }
