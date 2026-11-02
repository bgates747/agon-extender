#pragma once
#include <algorithm>
#include <cstring>
#include <map>
#include <string>
using esp_err_t=int;
constexpr int ESP_OK=0,ESP_FAIL=-1;
enum httpd_method_t{HTTP_GET,HTTP_POST,HTTP_DELETE};
using httpd_handle_t=void *;
struct httpd_req_t{
  size_t content_len=0,read=0;
  std::map<std::string,std::string> headers;
  std::string body,response,status="200 OK";
  bool failRead=false,failSend=false;
};
struct httpd_uri_t{const char *uri;httpd_method_t method;esp_err_t(*handler)(httpd_req_t *);};
inline size_t httpd_req_get_hdr_value_len(httpd_req_t*r,const char*n){return r->headers[n].size();}
inline int httpd_req_get_hdr_value_str(httpd_req_t*r,const char*n,char*out,size_t size){
  auto s=r->headers[n];if(s.empty()||s.size()>=size)return ESP_FAIL;
  memcpy(out,s.c_str(),s.size()+1);return ESP_OK;
}
inline void httpd_resp_set_status(httpd_req_t*r,const char*s){r->status=s;}
inline void httpd_resp_set_hdr(httpd_req_t*,const char*,const char*){}
inline void httpd_resp_set_type(httpd_req_t*,const char*){}
inline int httpd_resp_send(httpd_req_t*r,const char*p,int n){if(p&&n>0)r->response.append(p,n);return ESP_OK;}
inline int httpd_resp_sendstr(httpd_req_t*r,const char*p){return httpd_resp_send(r,p,strlen(p));}
inline int httpd_resp_send_chunk(httpd_req_t*r,const char*p,int n){return r->failSend?ESP_FAIL:httpd_resp_send(r,p,n);}
inline int httpd_req_recv(httpd_req_t*r,char*p,unsigned n){
  if(r->failRead)return -1;
  n=std::min<size_t>(n,r->body.size()-r->read);memcpy(p,r->body.data()+r->read,n);r->read+=n;return n;
}
inline int httpd_register_uri_handler(httpd_handle_t,const httpd_uri_t*){return ESP_OK;}
