// Olimex DevKit SD1 mounting follows OLIMEX/ESP32-P4-DevKit commit
// 26705d36407a07324348927dfd30fbf4ffc1d94c sdmmc example. No format path.
// Separate HTTP task prevents long card operations occupying the video server.
#include "http.hpp"
#include "files.hpp"
#include <dirent.h>
#include <esp_http_server.h>
#include <esp_vfs_fat.h>
#include <driver/sdmmc_host.h>
#include <sdmmc_cmd.h>
#include <sd_pwr_ctrl_by_on_chip_ldo.h>
#include <esp_log.h>
#include <cstring>
namespace agon::extender::local_sd {
namespace {
constexpr const char *root="/p4sd";
httpd_handle_t server=nullptr;
sdmmc_card_t *card=nullptr;
sd_pwr_ctrl_handle_t power=nullptr;
bool attempted=false;
esp_err_t mountError=ESP_OK;
bool mount(){
  if(attempted)return card!=nullptr;
  attempted=true;
  sd_pwr_ctrl_ldo_config_t ldo{};ldo.ldo_chan_id=4;
  mountError=sd_pwr_ctrl_new_on_chip_ldo(&ldo,&power);if(mountError!=ESP_OK)return false;
  sdmmc_host_t host=SDMMC_HOST_DEFAULT();host.pwr_ctrl_handle=power;
  sdmmc_slot_config_t slot=SDMMC_SLOT_CONFIG_DEFAULT();slot.width=4;
  slot.clk=GPIO_NUM_43;slot.cmd=GPIO_NUM_44;slot.d0=GPIO_NUM_39;
  slot.d1=GPIO_NUM_40;slot.d2=GPIO_NUM_41;slot.d3=GPIO_NUM_42;
  slot.flags|=SDMMC_SLOT_FLAG_INTERNAL_PULLUP;
  esp_vfs_fat_sdmmc_mount_config_t cfg{};cfg.format_if_mount_failed=false;
  cfg.max_files=4;cfg.allocation_unit_size=16384;
  mountError=esp_vfs_fat_sdmmc_mount(root,&host,&slot,&cfg,&card);
  if(mountError!=ESP_OK){card=nullptr;sd_pwr_ctrl_del_on_chip_ldo(power);power=nullptr;}
  ESP_LOGI("p4_sd","Mount: %s (format disabled)",esp_err_to_name(mountError));
  return card!=nullptr;
}
esp_err_t error(httpd_req_t *r,const char *status,const char *message){httpd_resp_set_hdr(r,"Cache-Control","no-store");httpd_resp_set_hdr(r,"Connection","close");httpd_resp_set_status(r,status);httpd_resp_set_type(r,"text/plain");esp_err_t sent=httpd_resp_sendstr(r,message);return status[0]>='4'?ESP_FAIL:sent;}
bool path(httpd_req_t *r,std::string &out){
  char query[768],value[744];
  if(httpd_req_get_url_query_str(r,query,sizeof(query))!=ESP_OK||
     httpd_query_key_value(query,"path",value,sizeof(value))!=ESP_OK)return false;
  std::string decoded;if(!decodePath(value,decoded))return false;out=std::string(root)+decoded;return true;
}
esp_err_t status(httpd_req_t *r){
  bool ready=mount();char body[220];
  snprintf(body,sizeof(body),"{\"mounted\":%s,\"mount_error\":%s,\"capacity_bytes\":%llu,\"format_enabled\":false}",
    ready?"true":"false",jsonString(esp_err_to_name(mountError)).c_str(),
    ready?(unsigned long long)card->csd.capacity*card->csd.sector_size:0ULL);
  httpd_resp_set_type(r,"application/json");return httpd_resp_sendstr(r,body);
}
esp_err_t list(httpd_req_t *r){
  std::string name;if(!path(r,name))return error(r,"400 Bad Request","Invalid absolute path");
  if(!mount())return error(r,"503 Service Unavailable","SD mount failed; no formatting; reboot after correcting card");
  DIR *dir=opendir(name.c_str());if(!dir)return error(r,"404 Not Found","Directory unavailable");
  httpd_resp_set_type(r,"application/json");esp_err_t result=httpd_resp_sendstr_chunk(r,"[");bool first=true;
  while(result==ESP_OK){errno=0;dirent *e=readdir(dir);if(!e){if(errno)result=ESP_FAIL;break;}
    if(!strcmp(e->d_name,".")||!strcmp(e->d_name,".."))continue;
    struct stat st{};std::string full=name+(name.back()=='/'?"":"/")+e->d_name;
    if(stat(full.c_str(),&st)){result=ESP_FAIL;break;}
    std::string entry=(first?"":",")+std::string("{\"name\":")+jsonString(e->d_name)+",\"directory\":"+(S_ISDIR(st.st_mode)?"true":"false")+",\"size\":"+std::to_string(st.st_size)+"}";
    first=false;result=httpd_resp_send_chunk(r,entry.data(),entry.size());
  }
  closedir(dir);if(result!=ESP_OK)return ESP_FAIL;
  if(httpd_resp_sendstr_chunk(r,"]")!=ESP_OK)return ESP_FAIL;
  return httpd_resp_send_chunk(r,nullptr,0);
}
esp_err_t get(httpd_req_t *r){
  std::string name;if(!path(r,name))return error(r,"400 Bad Request","Invalid absolute path");
  if(!mount())return error(r,"503 Service Unavailable","SD unavailable");
  struct stat st{};if(stat(name.c_str(),&st)||!S_ISREG(st.st_mode))return error(r,"404 Not Found","File unavailable");
  FILE *f=fopen(name.c_str(),"rb");if(!f)return error(r,"500 Internal Server Error","Open failed");
  httpd_resp_set_type(r,"application/octet-stream");char data[4096];esp_err_t result=ESP_OK;size_t n;
  while((n=fread(data,1,sizeof(data),f))!=0){result=httpd_resp_send_chunk(r,data,n);if(result!=ESP_OK)break;}
  if(ferror(f))result=ESP_FAIL;
  if(fclose(f))result=ESP_FAIL;
  return result==ESP_OK?httpd_resp_send_chunk(r,nullptr,0):ESP_FAIL;
}
esp_err_t put(httpd_req_t *r){
  char intent[4];if(httpd_req_get_hdr_value_len(r,"Origin")||httpd_req_get_hdr_value_str(r,"X-Extender-Storage",intent,sizeof(intent))!=ESP_OK||strcmp(intent,"1"))return error(r,"403 Forbidden","Explicit CLI write intent required");
  if(!httpd_req_get_hdr_value_len(r,"Content-Length") || httpd_req_get_hdr_value_len(r,"Transfer-Encoding"))return error(r,"411 Length Required","Use a fixed Content-Length, not chunked upload");
  std::string name;if(!path(r,name)||name==std::string(root)+"/")return error(r,"400 Bad Request","Invalid file path");
  if(r->content_len>512U*1024U*1024U)return error(r,"413 Content Too Large","Maximum upload 512 MiB");
  if(!mount())return error(r,"503 Service Unavailable","SD unavailable");
  Upload upload(name);if(!upload.open())return error(r,errno==EEXIST?"409 Conflict":"500 Internal Server Error","Destination or scratch exists, or parent unavailable");
  char data[4096];size_t left=r->content_len;
  while(left){int n=httpd_req_recv(r,data,left>sizeof(data)?sizeof(data):left);if(n<=0)return ESP_FAIL;if(!upload.write(data,n))return error(r,"500 Internal Server Error","Write failed");left-=n;}
  if(!upload.finish())return error(r,"500 Internal Server Error","Commit failed");
  return error(r,"201 Created","Stored; download and compare to verify");
}
}
bool startHttp() noexcept {
  if(server)return true;
  httpd_config_t cfg=HTTPD_DEFAULT_CONFIG();cfg.server_port=8080;cfg.ctrl_port=32769;
  cfg.max_uri_handlers=4;cfg.stack_size=8192;cfg.max_open_sockets=2;
  cfg.recv_wait_timeout=5;cfg.send_wait_timeout=5;
  if(httpd_start(&server,&cfg)!=ESP_OK)return false;
  const httpd_uri_t routes[]={
    {.uri="/status",.method=HTTP_GET,.handler=status,.user_ctx=nullptr},
    {.uri="/list",.method=HTTP_GET,.handler=list,.user_ctx=nullptr},
    {.uri="/file",.method=HTTP_GET,.handler=get,.user_ctx=nullptr},
    {.uri="/file",.method=HTTP_PUT,.handler=put,.user_ctx=nullptr}};
  for(auto &route:routes)if(httpd_register_uri_handler(server,&route)!=ESP_OK){httpd_stop(server);server=nullptr;return false;}
  return true;
}
}
