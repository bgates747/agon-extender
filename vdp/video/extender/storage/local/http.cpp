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
#include <algorithm>
#if defined(AGON_EXTENDER_NATIVE_BUILD)
#include "agon_extender_board_config.hpp"
#endif
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
  sd_pwr_ctrl_ldo_config_t ldo{};
#if defined(AGON_EXTENDER_NATIVE_BUILD)
  ldo.ldo_chan_id=board::kSdLdo;
#else
  ldo.ldo_chan_id=4;
#endif
  mountError=sd_pwr_ctrl_new_on_chip_ldo(&ldo,&power);if(mountError!=ESP_OK)return false;
  sdmmc_host_t host=SDMMC_HOST_DEFAULT();host.pwr_ctrl_handle=power;
  sdmmc_slot_config_t slot=SDMMC_SLOT_CONFIG_DEFAULT();slot.width=4;
#if defined(AGON_EXTENDER_NATIVE_BUILD)
  slot.clk=gpio_num_t(board::kSdClk);slot.cmd=gpio_num_t(board::kSdCmd);slot.d0=gpio_num_t(board::kSdD0);
  slot.d1=gpio_num_t(board::kSdD1);slot.d2=gpio_num_t(board::kSdD2);slot.d3=gpio_num_t(board::kSdD3);
#else
  slot.clk=GPIO_NUM_43;slot.cmd=GPIO_NUM_44;slot.d0=GPIO_NUM_39;
  slot.d1=GPIO_NUM_40;slot.d2=GPIO_NUM_41;slot.d3=GPIO_NUM_42;
#endif
  slot.flags|=SDMMC_SLOT_FLAG_INTERNAL_PULLUP;
  esp_vfs_fat_sdmmc_mount_config_t cfg{};cfg.format_if_mount_failed=false;
  cfg.max_files=4;cfg.allocation_unit_size=16384;
  mountError=esp_vfs_fat_sdmmc_mount(root,&host,&slot,&cfg,&card);
  if(mountError!=ESP_OK){card=nullptr;sd_pwr_ctrl_del_on_chip_ldo(power);power=nullptr;}
  ESP_LOGI("p4_sd","Mount: %s (format disabled)",esp_err_to_name(mountError));
  return card!=nullptr;
}
esp_err_t reply(httpd_req_t *r, const char *status, const std::string &message) {
  httpd_resp_set_hdr(r, "Cache-Control", "no-store");
  httpd_resp_set_status(r, status);
  httpd_resp_set_type(r, "application/json");
  auto body = "{\"message\":" + jsonString(message) + "}";
  esp_err_t sent = httpd_resp_sendstr(r, body.c_str());
  // Error responses close the session: a rejected PUT may have unread data.
  return status[0] >= '4' ? ESP_FAIL : sent;
}
esp_err_t failure(httpd_req_t *r, bool partial = false) {
  int code = errno;
  const char *status = "500 Internal Server Error";
  if (code == ENOENT) status = "404 Not Found";
  else if (code == EEXIST || code == ENOTEMPTY || code == EBUSY) status = "409 Conflict";
  else if (code == EINVAL || code == ENAMETOOLONG || code == ELOOP || code == EISDIR || code == ENOTDIR) status = "400 Bad Request";
  else if (code == EPERM || code == EACCES) status = "403 Forbidden";
  else if (code == ENOSPC) status = "507 Insufficient Storage";
  return reply(r, status, std::string(strerror(code)) +
               (partial ? "; operation may be partially complete; inspect before retry" : ""));
}
struct Query {
  std::string raw;
  bool valid = true;
  explicit Query(httpd_req_t *r) {
    size_t n = httpd_req_get_url_query_len(r);
    if (n > 1900) { valid = false; return; }
    raw.resize(n + 1);
    if (n && httpd_req_get_url_query_str(r, &raw[0], raw.size()) != ESP_OK) valid = false;
    raw.resize(n);
  }
  std::string value(const char *key) {
    std::string out(raw.size() + 1, '\0');
    auto result = httpd_query_key_value(raw.c_str(), key, &out[0], out.size());
    if (result == ESP_ERR_NOT_FOUND) return "";
    if (result != ESP_OK) { valid = false; return ""; }
    out.resize(strlen(out.c_str()));
    return out;
  }
  bool flag(const char *key, bool fallback = false) {
    auto v = value(key);
    if (v.empty()) return fallback;
    if (v != "0" && v != "1") valid = false;
    return v == "1";
  }
  bool path(const char *key, std::string &out, bool internal = false) {
    if (!decodePath(value(key), out, internal)) valid = false;
    return valid;
  }
  std::string text(const char *key) {
    auto input = value(key); std::string out;
    auto hex = [](char c) -> int {
      if (c >= '0' && c <= '9') return c - '0';
      if (c >= 'a' && c <= 'f') return c - 'a' + 10;
      if (c >= 'A' && c <= 'F') return c - 'A' + 10;
      return -1;
    };
    for (size_t i = 0; i < input.size(); ++i) {
      unsigned char c = input[i];
      if (c == '%') {
        if (i + 2 >= input.size()) { valid = false; break; }
        int a = hex(input[++i]), b = hex(input[++i]);
        if (a < 0 || b < 0) { valid = false; break; }
        c = (a << 4) | b;
      } else if (c == '+') c = ' ';
      if (c < 32 || c >= 127) valid = false;
      out += char(c);
    }
    if (out.size() > 128) valid = false;
    return out;
  }
};
bool intent(httpd_req_t *r) {
  char value[4];
  return !httpd_req_get_hdr_value_len(r, "Origin") &&
    httpd_req_get_hdr_value_str(r, "X-Extender-Storage", value, sizeof(value)) == ESP_OK &&
    !strcmp(value, "1");
}
std::string info(const std::string &path, const struct stat &st) {
  auto name = path.substr(path.find_last_of('/') + 1);
  return "{\"path\":" + jsonString(path) + ",\"name\":" + jsonString(name) +
    ",\"directory\":" + (S_ISDIR(st.st_mode) ? "true" : "false") +
    ",\"size\":" + std::to_string(st.st_size) +
    ",\"modified\":" + std::to_string(st.st_mtime) + "}";
}
esp_err_t status(httpd_req_t *r) {
  bool ready = mount();
  uint64_t total = 0, free = 0;
  bool space = ready && esp_vfs_fat_info(root, &total, &free) == ESP_OK;
  auto body = std::string("{\"mounted\":") + (ready ? "true" : "false") +
    ",\"mount_error\":" + jsonString(esp_err_to_name(mountError)) +
    ",\"capacity_bytes\":" + std::to_string(ready ? uint64_t(card->csd.capacity) * card->csd.sector_size : 0) +
    ",\"filesystem_bytes\":" + (space ? std::to_string(total) : "null") +
    ",\"free_bytes\":" + (space ? std::to_string(free) : "null") + ",\"format_enabled\":false}";
  httpd_resp_set_type(r, "application/json");
  httpd_resp_set_hdr(r, "Cache-Control", "no-store");
  return httpd_resp_sendstr(r, body.c_str());
}
esp_err_t metadata(httpd_req_t *r) {
  Query q(r); std::string path;
  if (!q.path("path", path, true)) return reply(r, "400 Bad Request", "Invalid path");
  if (!mount()) return reply(r, "503 Service Unavailable", "SD unavailable");
  struct stat st{};
  if (stat((root + path).c_str(), &st)) return failure(r);
  httpd_resp_set_type(r, "application/json");
  httpd_resp_set_hdr(r, "Cache-Control", "no-store");
  return httpd_resp_sendstr(r, info(path, st).c_str());
}
esp_err_t listing(httpd_req_t *r) {
  Query q(r); std::string path;
  bool search = !strncmp(r->uri, "/search", 7);
  bool recursive = q.flag("recursive", search);
  auto pattern = q.text("name"), contains = q.text("contains");
  if (!q.path("path", path, true)) return reply(r, "400 Bad Request", "Invalid path/options");
  if (!mount()) return reply(r, "503 Service Unavailable", "SD unavailable");
  struct stat st{};
  if (stat((root + path).c_str(), &st)) return failure(r);
  if (!S_ISDIR(st.st_mode)) return reply(r, "400 Bad Request", "Directory required");
  httpd_resp_set_type(r, "application/json");
  httpd_resp_set_hdr(r, "Cache-Control", "no-store");
  if (httpd_resp_sendstr_chunk(r, "[")) return ESP_FAIL;
  bool first = true;
  auto visitor = [&](const std::string &child, const struct stat &item) {
    if (search && !globMatch(pattern.empty() ? "*" : pattern, child.substr(child.find_last_of('/') + 1))) return true;
    if (search && !contains.empty()) {
      if (!S_ISREG(item.st_mode)) return true;
      bool found;
      if (!containsText(root + child, contains, found)) return false;
      if (!found) return true;
    }
    auto entry = (first ? "" : ",") + info(child, item); first = false;
    return httpd_resp_send_chunk(r, entry.data(), entry.size()) == ESP_OK;
  };
  if (!walk(root, path, recursive, visitor)) return ESP_FAIL; // incomplete JSON => failure, not success
  if (httpd_resp_sendstr_chunk(r, "]")) return ESP_FAIL;
  return httpd_resp_send_chunk(r, nullptr, 0);
}
esp_err_t get(httpd_req_t *r) {
  Query q(r); std::string path;
  if (!q.path("path", path, true)) return reply(r, "400 Bad Request", "Invalid path");
  if (!mount()) return reply(r, "503 Service Unavailable", "SD unavailable");
  struct stat st{};
  if (stat((root + path).c_str(), &st)) return failure(r);
  if (!S_ISREG(st.st_mode)) return reply(r, "400 Bad Request", "Regular file required");
  FILE *f = fopen((root + path).c_str(), "rb");
  if (!f) return failure(r);
  httpd_resp_set_type(r, "application/octet-stream");
  httpd_resp_set_hdr(r, "Cache-Control", "no-store");
  char data[4096]; esp_err_t result = ESP_OK; size_t n;
  while ((n = fread(data, 1, sizeof(data), f)) != 0) {
    result = httpd_resp_send_chunk(r, data, n);
    if (result != ESP_OK) break;
  }
  if (ferror(f)) result = ESP_FAIL;
  if (fclose(f)) result = ESP_FAIL;
  return result == ESP_OK ? httpd_resp_send_chunk(r, nullptr, 0) : ESP_FAIL;
}
// Drain a rejected fixed-length upload before replying. Closing with unread TCP
// bytes can reset the peer while it is sending, hiding our useful HTTP error.
// Bound both declared size and socket receive timeout; never wait without limits.
bool drainUpload(httpd_req_t *r, size_t left) {
  if (left > 512U * 1024U * 1024U) return false;
  char data[4096];
  while (left) {
    int n = httpd_req_recv(r, data, std::min(left, sizeof(data)));
    if (n <= 0) return false;
    left -= n;
  }
  return true;
}
esp_err_t rejectUpload(httpd_req_t *r, const char *status, const char *message) {
  drainUpload(r, r->content_len);
  return reply(r, status, message);
}
esp_err_t put(httpd_req_t *r) {
  if (!intent(r)) return rejectUpload(r, "403 Forbidden", "Explicit CLI write intent required");
  if (!httpd_req_get_hdr_value_len(r, "Content-Length") || httpd_req_get_hdr_value_len(r, "Transfer-Encoding"))
    return rejectUpload(r, "411 Length Required", "Use a fixed Content-Length");
  Query q(r); std::string path; bool replace = q.flag("replace");
  if (!q.path("path", path) || path == "/") return rejectUpload(r, "400 Bad Request", "Invalid file path/options");
  if (spoolAncestor(path)) return rejectUpload(r, "403 Forbidden", "Private staging ancestor protected");
  if (r->content_len > 512U * 1024U * 1024U) return rejectUpload(r, "413 Content Too Large", "Maximum upload 512 MiB");
  if (!mount()) return rejectUpload(r, "503 Service Unavailable", "SD unavailable");
  Upload upload(root + path, replace);
  if (!upload.open()) {
    int saved = errno; drainUpload(r, r->content_len); errno = saved;
    return failure(r);
  }
  char data[4096]; size_t left = r->content_len;
  while (left) {
    int n = httpd_req_recv(r, data, std::min(left, sizeof(data)));
    if (n <= 0) return ESP_FAIL;
    left -= n;
    if (!upload.write(data, n)) {
      int saved = errno; drainUpload(r, left); errno = saved;
      return failure(r);
    }
  }
  if (!upload.finish()) return failure(r, true);
  return reply(r, "201 Created", "Stored");
}
esp_err_t mutate(httpd_req_t *r) {
  if (!intent(r)) return reply(r, "403 Forbidden", "Explicit CLI write intent required");
  Query q(r); std::string path, destination;
  bool recursive = q.flag("recursive"), parents = q.flag("parents"), replace = q.flag("replace");
  bool remove = r->method == HTTP_DELETE;
  bool copy = !strncmp(r->uri, "/copy", 5), move = !strncmp(r->uri, "/move", 5);
  if (!q.path("path", path, remove) || ((copy || move) && !q.path("to", destination)))
    return reply(r, "400 Bad Request", "Invalid path/options");
  if (spoolAncestor(path) || privateSpool(path) ||
      ((copy || move) && (spoolAncestor(destination) || privateSpool(destination))))
    return reply(r, "403 Forbidden", "Private staging namespace protected");
  if (path == "/" && (remove || copy || move)) return reply(r, "403 Forbidden", "Root mutation forbidden");
  if (move && replace) return reply(r, "400 Bad Request", "Move requires an absent destination");
  if (!mount()) return reply(r, "503 Service Unavailable", "SD unavailable");
  bool ok;
  if (remove) ok = removePath(root, path, recursive);
  else if (copy) ok = copyPath(root, path, destination, recursive, replace);
  else if (move) ok = movePath(root, path, destination);
  else ok = makeDirectory(root, path, parents);
  if (!ok) return failure(r, recursive || parents || replace);
  return reply(r, "200 OK", "Complete");
}
}
const char *mediaRoot() noexcept { return root; }
bool prepareSpool(std::string &directory) noexcept {
  if (!mount()) return false;
  for (const char *part : {"/tmp", "/tmp/extender", "/tmp/extender/spool"}) {
    std::string full = std::string(root) + part;
    if (mkdir(full.c_str(), 0777)) {
      struct stat st{};
      if (errno != EEXIST || stat(full.c_str(), &st) || !S_ISDIR(st.st_mode)) return false;
    }
  }
  directory=std::string(root)+"/tmp/extender/spool";
  return true;
}
template<esp_err_t (*Handler)(httpd_req_t *)>
esp_err_t guarded(httpd_req_t *request) {
  MediaLease lease;
  if (!lease) return reply(request, "503 Service Unavailable", "P4 card is owned by another operation");
  return Handler(request);
}
bool startHttp() noexcept {
  if (server) return true;
  httpd_config_t cfg = HTTPD_DEFAULT_CONFIG();
  cfg.server_port = 8080; cfg.ctrl_port = 32769;
  cfg.max_uri_handlers = 10; cfg.stack_size = 16384; cfg.max_open_sockets = 2;
  cfg.recv_wait_timeout = 5; cfg.send_wait_timeout = 5;
  if (httpd_start(&server, &cfg) != ESP_OK) return false;
  const httpd_uri_t routes[] = {
    {.uri="/status", .method=HTTP_GET, .handler=guarded<status>, .user_ctx=nullptr},
    {.uri="/stat", .method=HTTP_GET, .handler=guarded<metadata>, .user_ctx=nullptr},
    {.uri="/list", .method=HTTP_GET, .handler=guarded<listing>, .user_ctx=nullptr},
    {.uri="/search", .method=HTTP_GET, .handler=guarded<listing>, .user_ctx=nullptr},
    {.uri="/file", .method=HTTP_GET, .handler=guarded<get>, .user_ctx=nullptr},
    {.uri="/file", .method=HTTP_PUT, .handler=guarded<put>, .user_ctx=nullptr},
    {.uri="/entry", .method=HTTP_DELETE, .handler=guarded<mutate>, .user_ctx=nullptr},
    {.uri="/directory", .method=HTTP_POST, .handler=guarded<mutate>, .user_ctx=nullptr},
    {.uri="/copy", .method=HTTP_POST, .handler=guarded<mutate>, .user_ctx=nullptr},
    {.uri="/move", .method=HTTP_POST, .handler=guarded<mutate>, .user_ctx=nullptr}
  };
  for (auto &route : routes) {
    if (httpd_register_uri_handler(server, &route) != ESP_OK) {
      httpd_stop(server); server = nullptr; return false;
    }
  }
  return true;
}
}
