// Dedicated input WebSocket. Same-origin admission is intentional; the host RPC
// retains its no-Origin requirement. HTTP never writes UART or edits MOS state.
// This is a LAN endpoint, not authentication against a hostile LAN peer.
namespace {
struct BrowserSocket { uint32_t id; };
uint32_t browserSocketSequence{}; // HTTP task owns allocation
void freeBrowserSocket(void *value) {
  auto *socket=static_cast<BrowserSocket *>(value);
  input::remoteLocked([&](auto &r){r.browserDisconnect(socket->id);return 0;});
  delete socket;
}
esp_err_t browserKeyboardOpened(httpd_req_t *request) {
  if(++browserSocketSequence==0)++browserSocketSequence;
  auto *socket=new(std::nothrow) BrowserSocket{browserSocketSequence};
  if(!socket)return ESP_ERR_NO_MEM;
  request->sess_ctx=socket;request->free_ctx=freeBrowserSocket;return ESP_OK;
}
esp_err_t browserKeyboardHandler(httpd_req_t *request) {
  if(request->method==HTTP_GET) {
    char origin[192]{},host[160]{},expected[192]{};
    if(httpd_req_get_hdr_value_str(request,"Origin",origin,sizeof(origin))!=ESP_OK ||
       httpd_req_get_hdr_value_str(request,"Host",host,sizeof(host))!=ESP_OK)
      return httpd_resp_send_err(request,HTTPD_400_BAD_REQUEST,"Keyboard requires same origin");
    snprintf(expected,sizeof(expected),"http://%s",host);
    if(std::strcmp(origin,expected))
      return httpd_resp_send_err(request,HTTPD_400_BAD_REQUEST,"Keyboard origin mismatch");
    return ESP_OK;
  }
  auto *socket=static_cast<BrowserSocket *>(request->sess_ctx);
  if(!socket)return ESP_FAIL;
  httpd_ws_frame_t frame{};
  if(httpd_ws_recv_frame(request,&frame,0)!=ESP_OK)return ESP_FAIL;
  if(frame.type!=HTTPD_WS_TYPE_BINARY || frame.len!=16 || frame.fragmented)return ESP_FAIL;
  uint8_t body[16]{};frame.payload=body;
  if(httpd_ws_recv_frame(request,&frame,sizeof(body))!=ESP_OK)return ESP_FAIL;
  uint32_t generation{};
  unsigned result=input::remoteLocked([&](auto &r){
    return r.browserRequest(socket->id,body,sizeof(body),uint32_t(esp_timer_get_time()/1000),generation);
  });
  // Reply echoes sequence and replaces opcode with 0=accepted, 1=stale/invalid,
  // 2=not ready. Its generation is P4's, never the untrusted request's.
  body[0]='B';body[1]='K';body[2]=1;body[3]=result==200?0:result==503?2:1;
  for(unsigned i=0;i<4;++i)body[4+i]=uint8_t(generation>>(8*i));
  return httpd_ws_send_frame(request,&frame);
}
}
