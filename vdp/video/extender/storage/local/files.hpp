#pragma once
// P4-local file service primitives. No Agon protocol or board dependency.
#include <string>
#include <utility>
#include <cstdio>
#include <cerrno>
#include <fcntl.h>
#include <unistd.h>
#include <sys/stat.h>
#include <dirent.h>
#include <cstring>
namespace agon::extender::local_sd {
inline bool decodePath(const std::string &encoded, std::string &path, bool allowReserved = false) {
  path.clear();
  auto hex=[](char c)->int {if(c>='0'&&c<='9')return c-'0'; if(c>='a'&&c<='f')return c-'a'+10; if(c>='A'&&c<='F')return c-'A'+10; return -1;};
  for(size_t i=0;i<encoded.size();++i){
    unsigned char c=encoded[i];
    if(c=='%'){if(i+2>=encoded.size())return false;int a=hex(encoded[++i]),b=hex(encoded[++i]);if(a<0||b<0)return false;c=(a<<4)|b;}
    if(c<32||c>=127||c=='\\'||c==':'||c=='*'||c=='?'||c=='"'||c=='<'||c=='>'||c=='|'||c=='%')return false;
    path+=char(c);
  }
  if(path.empty()||path.front()!='/'||path.size()>240)return false;
  if(path=="/")return true;
  size_t start=1;
  while(start<path.size()){
    auto end=path.find('/',start);if(end==std::string::npos)end=path.size();
    auto part=path.substr(start,end-start);
    if(part.empty()||part=="."||part==".."||part.back()=='.'||part.back()==' ')return false;
    std::string lower=part;for(char &c:lower)if(c>='A'&&c<='Z')c+=32;
    if(!allowReserved && (lower.find(".ext-upload")!=std::string::npos || lower.find(".ext-backup")!=std::string::npos))return false;
    start=end+1;
  }
  return path.back()!='/';
}
inline std::string jsonString(const std::string &s){
  std::string out="\""; const char *h="0123456789abcdef";
  for(unsigned char c:s){if(c=='"'||c=='\\'){out+='\\';out+=char(c);}else if(c<32||c>=127){out+="\\u00";out+=h[c>>4];out+=h[c&15];}else out+=char(c);}
  return out+'"';
}
// FatFS f_rename does not replace an existing destination (ESP-IDF 5.5.5
// components/fatfs/vfs/vfs_fat.c). Stage first, then use a retained backup.
// One server task owns mutations. This is NOT a power-loss-atomic transaction.
inline std::string folded(std::string s) {
  for (char &c : s) if (c >= 'A' && c <= 'Z') c += 'a' - 'A';
  return s;
}
inline bool reserved(const std::string &s) {
  auto lower = folded(s);
  return lower.find(".ext-upload") != std::string::npos ||
         lower.find(".ext-backup") != std::string::npos;
}
inline bool absent(const std::string &s) {
  struct stat st{};
  if (stat(s.c_str(), &st) == 0) { errno = EEXIST; return false; }
  return errno == ENOENT;
}
class Upload {
 public:
  explicit Upload(std::string target, bool replace = false)
      : target_(std::move(target)), temp_(target_ + ".ext-upload"),
        backup_(target_ + ".ext-backup"), replace_(replace) {}
  Upload(const Upload &) = delete;
  Upload &operator=(const Upload &) = delete;
  ~Upload() {
    int saved = errno;
    if (file_) fclose(file_);
    if (owned_) unlink(temp_.c_str());
    errno = saved;
  }
  bool open() {
    struct stat st{};
    if (stat(target_.c_str(), &st) == 0) {
      if (!replace_ || !S_ISREG(st.st_mode)) { errno = EEXIST; return false; }
    } else if (errno != ENOENT) return false;
    if (!absent(backup_)) return false;
    int fd = ::open(temp_.c_str(), O_WRONLY | O_CREAT | O_EXCL, 0600);
    if (fd < 0) return false;
    owned_ = true;
    file_ = fdopen(fd, "wb");
    if (!file_) { int saved = errno; ::close(fd); errno = saved; return false; }
    return true;
  }
  bool write(const char *data, size_t n) {
    return file_ && fwrite(data, 1, n, file_) == n;
  }
  bool finish() {
    if (!file_) { errno = EBADF; return false; }
    bool ok = fflush(file_) == 0;
    if (ok) ok = fsync(fileno(file_)) == 0;
    int saved = errno;
    int closed = fclose(file_); file_ = nullptr;
    if (!ok) { errno = saved ? saved : EIO; return false; }
    if (closed) return false;
    struct stat st{};
    bool exists = stat(target_.c_str(), &st) == 0;
    if (!exists && errno != ENOENT) return false;
    if (exists && (!replace_ || !S_ISREG(st.st_mode))) { errno = EEXIST; return false; }
    if (!absent(backup_)) return false;
    if (exists && rename(target_.c_str(), backup_.c_str())) return false;
    if (rename(temp_.c_str(), target_.c_str())) {
      int saved = errno;
      // If restoration also fails, the old bytes remain at backup_, never erased.
      if (exists) rename(backup_.c_str(), target_.c_str());
      errno = saved; return false;
    }
    owned_ = false;
    return !exists || unlink(backup_.c_str()) == 0;
  }
 private:
  std::string target_, temp_, backup_;
  FILE *file_ = nullptr;
  bool replace_, owned_ = false;
};

// Paths here are decoded card-relative absolute paths. Root mutation is barred.
// Case-fold relationships because the actual card filesystem is FAT.
inline bool relationshipOK(const std::string &src, const std::string &dst) {
  auto a = folded(src), b = folded(dst);
  if (a == "/" || b == "/" || a == b ||
      b.compare(0, a.size() + 1, a + "/") == 0 ||
      a.compare(0, b.size() + 1, b + "/") == 0) {
    errno = EINVAL; return false;
  }
  return true;
}
constexpr unsigned maxDepth = 16;
inline std::string join(const std::string &a, const std::string &b) {
  return a + (a.back() == '/' ? "" : "/") + b;
}
inline bool makeDirectory(const std::string &root, const std::string &path, bool parents) {
  if (path == "/") return true;
  if (!parents) return mkdir((root + path).c_str(), 0777) == 0;
  size_t end = 1;
  do {
    end = path.find('/', end);
    std::string part = root + path.substr(0, end);
    if (mkdir(part.c_str(), 0777)) {
      struct stat st{};
      if (errno != EEXIST || stat(part.c_str(), &st) || !S_ISDIR(st.st_mode)) return false;
    }
    if (end == std::string::npos) break;
    ++end;
  } while (true);
  return true;
}
// Iterators never retain complete trees. Depth is limited before opening another
// directory. Each callback returns false on output/client failure to stop work.
template<class Visitor>
bool walk(const std::string &root, const std::string &path, bool recursive,
          Visitor &visit, unsigned depth = 0) {
  if (depth > maxDepth) { errno = ELOOP; return false; }
  DIR *dir = opendir((root + path).c_str());
  if (!dir) return false;
  bool ok = true;
  while (ok) {
    errno = 0;
    dirent *entry = readdir(dir);
    if (!entry) { ok = errno == 0; break; }
    if (!strcmp(entry->d_name, ".") || !strcmp(entry->d_name, "..")) continue;
    std::string child = join(path, entry->d_name);
    struct stat st{};
    if (stat((root + child).c_str(), &st)) { ok = false; break; }
    if (!visit(child, st)) { ok = false; break; }
    if (recursive && S_ISDIR(st.st_mode)) ok = walk(root, child, true, visit, depth + 1);
  }
  int saved = errno; closedir(dir); errno = saved;
  return ok;
}
inline bool removePath(const std::string &root, const std::string &path,
                       bool recursive, unsigned depth = 0) {
  if (path == "/") { errno = EPERM; return false; }
  if (depth > maxDepth) { errno = ELOOP; return false; }
  const std::string full = root + path;
  struct stat st{};
  if (stat(full.c_str(), &st)) return false;
  if (!S_ISDIR(st.st_mode)) return unlink(full.c_str()) == 0;
  if (recursive) {
    // Reopen after each removal: no assumption about FAT directory offsets
    // remaining valid while entries are being removed.
    for (;;) {
      DIR *dir = opendir(full.c_str());
      if (!dir) return false;
      std::string child;
      errno = 0;
      while (auto *entry = readdir(dir)) {
        if (strcmp(entry->d_name, ".") && strcmp(entry->d_name, "..")) {
          child = join(path, entry->d_name); break;
        }
      }
      int saved = errno; closedir(dir); errno = saved;
      if (child.empty()) { if (saved) return false; break; }
      if (!removePath(root, child, true, depth + 1)) return false;
    }
  }
  return rmdir(full.c_str()) == 0;
}
inline bool copyFile(const std::string &src, const std::string &dst, bool replace) {
  FILE *in = fopen(src.c_str(), "rb");
  if (!in) return false;
  Upload out(dst, replace);
  bool ok = out.open();
  char data[4096];
  while (ok) {
    size_t n = fread(data, 1, sizeof(data), in);
    if (!n) { ok = !ferror(in); break; }
    ok = out.write(data, n);
  }
  int saved = errno;
  if (fclose(in)) { ok = false; saved = errno; }
  errno = saved;
  return ok && out.finish();
}
inline bool copyPath(const std::string &root, const std::string &src,
                     const std::string &dst, bool recursive, bool replace) {
  if (!relationshipOK(src, dst)) return false;
  struct stat st{};
  if (stat((root + src).c_str(), &st)) return false;
  if (!S_ISDIR(st.st_mode)) return copyFile(root + src, root + dst, replace);
  if (!recursive) { errno = EISDIR; return false; }
  // Directory copies create a new tree, never merge or replace an old tree.
  if (!absent(root + dst) || !makeDirectory(root, dst, false)) return false;
  auto visitor = [&](const std::string &path, const struct stat &item) {
    const std::string target = dst + path.substr(src.size());
    if (target.size() > 240) { errno = ENAMETOOLONG; return false; }
    if (reserved(path)) { errno = EBUSY; return false; }
    if (S_ISDIR(item.st_mode)) return makeDirectory(root, target, false);
    return copyFile(root + path, root + target, false);
  };
  return walk(root, src, true, visitor);
}
inline bool movePath(const std::string &root, const std::string &src, const std::string &dst) {
  return relationshipOK(src, dst) && absent(root + dst) &&
         rename((root + src).c_str(), (root + dst).c_str()) == 0;
}
// Iterative wildcard matching: no recursive/exponential pattern expansion.
inline bool globMatch(const std::string &pattern, const std::string &name) {
  auto p = folded(pattern), n = folded(name);
  size_t i = 0, j = 0, star = std::string::npos, retry = 0;
  while (j < n.size()) {
    if (i < p.size() && (p[i] == '?' || p[i] == n[j])) { ++i; ++j; }
    else if (i < p.size() && p[i] == '*') { star = i++; retry = j; }
    else if (star != std::string::npos) { i = star + 1; j = ++retry; }
    else return false;
  }
  while (i < p.size() && p[i] == '*') ++i;
  return i == p.size();
}
inline bool containsText(const std::string &file, const std::string &needle, bool &found) {
  found = false;
  FILE *in = fopen(file.c_str(), "rb");
  if (!in) return false;
  char chunk[2048]; std::string tail;
  while (size_t n = fread(chunk, 1, sizeof(chunk), in)) {
    tail.append(chunk, n);
    if (tail.find(needle) != std::string::npos) { found = true; break; }
    if (tail.size() >= needle.size()) tail.erase(0, tail.size() - (needle.empty() ? 0 : needle.size() - 1));
  }
  bool ok = !ferror(in);
  if (fclose(in)) ok = false;
  return ok;
}
}
