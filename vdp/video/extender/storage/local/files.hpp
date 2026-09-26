#pragma once
// P4-local file service primitives. No Agon protocol or board dependency.
#include <string>
#include <utility>
#include <cstdio>
#include <cerrno>
#include <fcntl.h>
#include <unistd.h>
#include <sys/stat.h>
namespace agon::extender::local_sd {
inline bool decodePath(const std::string &encoded, std::string &path) {
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
    if(lower.find(".ext-upload")!=std::string::npos)return false;
    start=end+1;
  }
  return path.back()!='/';
}
inline std::string jsonString(const std::string &s){
  std::string out="\""; const char *h="0123456789abcdef";
  for(unsigned char c:s){if(c=='"'||c=='\\'){out+='\\';out+=char(c);}else if(c<32||c>=127){out+="\\u00";out+=h[c>>4];out+=h[c&15];}else out+=char(c);}
  return out+'"';
}
// Single owning server task serializes all mutations. Other writers must acquire
// a future shared storage lease before integration; POSIX rename alone is not
// a portable atomic no-replace operation on FatFS.
class Upload {
 public:
  explicit Upload(std::string target):target_(std::move(target)),temp_(target_+".ext-upload"){}
  ~Upload(){if(file_)fclose(file_);if(owned_)unlink(temp_.c_str());}
  bool open(){struct stat st{};if(stat(target_.c_str(),&st)==0){errno=EEXIST;return false;}if(errno!=ENOENT)return false;
    int fd=::open(temp_.c_str(),O_WRONLY|O_CREAT|O_EXCL,0600);if(fd<0)return false;owned_=true;file_=fdopen(fd,"wb");if(!file_){::close(fd);return false;}return true;}
  bool write(const char *data,size_t n){return file_&&fwrite(data,1,n,file_)==n;}
  bool finish(){if(!file_)return false;bool ok=fflush(file_)==0;if(ok)ok=fsync(fileno(file_))==0;int closed=fclose(file_);file_=nullptr;if(!ok||closed)return false;
    struct stat st{};if(stat(target_.c_str(),&st)==0){errno=EEXIST;return false;}if(errno!=ENOENT)return false;
    if(rename(temp_.c_str(),target_.c_str()))return false;
    owned_=false;return true;}
 private:std::string target_,temp_;FILE *file_=nullptr;bool owned_=false;
};
}
