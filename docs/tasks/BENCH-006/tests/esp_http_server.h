#pragma once
#include <string>
using esp_err_t=int;
struct httpd_req_t { std::string status="200 OK",body; };
inline void httpd_resp_set_hdr(httpd_req_t*,const char*,const char*){}
inline void httpd_resp_set_type(httpd_req_t*,const char*){}
inline void httpd_resp_set_status(httpd_req_t*r,const char*s){r->status=s;}
inline int httpd_resp_send(httpd_req_t*r,const char*s,size_t n){r->body.assign(s,n);return 0;}
inline int httpd_resp_sendstr(httpd_req_t*r,const char*s){r->body=s;return 0;}
