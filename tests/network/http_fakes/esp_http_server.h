#pragma once
#include <cstddef>
#include <cstdint>
#include <sys/types.h>
using esp_err_t=int;using httpd_handle_t=void*;
constexpr int ESP_OK=0,ESP_FAIL=-1,HTTP_GET=0,HTTPD_SOCK_ERR_TIMEOUT=-2,HTTPD_SOCK_ERR_FAIL=-3;
constexpr int HTTPD_WS_TYPE_TEXT=1,HTTPD_WS_TYPE_BINARY=2,HTTPD_WS_TYPE_CONTINUE=0,HTTPD_WS_TYPE_CLOSE=8,HTTPD_WS_CLIENT_WEBSOCKET=2;
struct httpd_req_t {void *user_ctx{};void *handle{};int socket{};};
struct httpd_ws_frame_t {int type{};bool fragmented{},final{};uint8_t *payload{};size_t len{};};
struct httpd_uri_t {const char *uri{};int method{};esp_err_t(*handler)(httpd_req_t*){};void *user_ctx{};bool is_websocket{};esp_err_t(*ws_post_handshake_cb)(httpd_req_t*){};};
struct httpd_config_t {
 unsigned server_port{},ctrl_port{},max_uri_handlers{},max_open_sockets{},stack_size{};
 int send_wait_timeout{};bool lru_purge_enable{};void *global_user_ctx{};void(*global_user_ctx_free_fn)(void*){};
 esp_err_t(*open_fn)(httpd_handle_t,int){};void(*close_fn)(httpd_handle_t,int){};
};
#define HTTPD_DEFAULT_CONFIG() httpd_config_t{}
int httpd_start(httpd_handle_t*,httpd_config_t*);
int httpd_stop(httpd_handle_t);
int httpd_register_uri_handler(httpd_handle_t,httpd_uri_t*);
int httpd_sess_set_send_override(httpd_handle_t,int,int(*)(httpd_handle_t,int,const char*,size_t,int));
int httpd_resp_send_500(httpd_req_t*);
int httpd_resp_set_type(httpd_req_t*,const char*);
int httpd_resp_set_hdr(httpd_req_t*,const char*,const char*);
int httpd_resp_set_status(httpd_req_t*,const char*);
int httpd_resp_sendstr(httpd_req_t*,const char*);
int httpd_resp_send(httpd_req_t*,const char*,ssize_t);
int httpd_sess_trigger_close(httpd_handle_t,int);
int httpd_req_to_sockfd(httpd_req_t*);
int httpd_ws_send_frame_async(httpd_handle_t,int,httpd_ws_frame_t*);
int httpd_ws_send_frame(httpd_req_t*,httpd_ws_frame_t*);
int httpd_ws_recv_frame(httpd_req_t*,httpd_ws_frame_t*,size_t);
int httpd_ws_get_fd_info(httpd_handle_t,int);
int httpd_queue_work(httpd_handle_t,void(*)(void*),void*);
void *httpd_get_global_user_ctx(httpd_handle_t);
