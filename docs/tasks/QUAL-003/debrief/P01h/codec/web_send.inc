  // HTTP task serializes negotiation, scratch use and complete sends. Snapshot
  // lease is immutable here; no graphics lock is acquired for compression.
  std::array<OpaqueMessageSegment,2> compressed{};
  uint8_t compressed_header[32];
  auto segments=view.segments.data();size_t count=view.segment_count;
  size_t transmitted=view.total_bytes;
  if(rle2_requested && rle2_scratch && count==2 && segments[0].size==32) {
    auto h=segments[0].data;const auto n=segments[1].size;
    const size_t width=size_t(h[12])|(size_t(h[13])<<8);
    const size_t height=size_t(h[14])|(size_t(h[15])<<8);
    if(std::memcmp(h,"EVF1",4)==0 && h[6]==2 && n<=196608 && n==width*height && rle2::get32(h+16)==width && rle2::get32(h+20)==n){
      auto begin=esp_timer_get_time();auto encoded=rle2::encode_fast(segments[1].data,n,rle2_scratch,196622,true);
      rle2_encode_us+=esp_timer_get_time()-begin;++rle2_attempts;
      if(encoded && encoded.bytes<n){
        std::memcpy(compressed_header,h,32);compressed_header[2]='R';
        compressed[0]={compressed_header,32};compressed[1]={rle2_scratch,encoded.bytes};
        segments=compressed.data();count=2;transmitted=32+encoded.bytes;++rle2_frames;
      }
    }
  }
  esp_err_t result = ESP_OK;
  for(size_t index=0;index<count;++index){
    httpd_ws_frame_t frame{};frame.fragmented=count>1;frame.final=index+1==count;
    frame.type=index==0?HTTPD_WS_TYPE_BINARY:HTTPD_WS_TYPE_CONTINUE;
    frame.payload=const_cast<uint8_t*>(segments[index].data);frame.len=segments[index].size;
    result=httpd_ws_send_frame_async(server,socket,&frame);if(result!=ESP_OK)break;
  }
