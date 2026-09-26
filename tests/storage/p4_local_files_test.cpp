#include "extender/storage/local/files.hpp"
#include <cassert>
#include <fstream>
#include <iterator>
#include <filesystem>
using namespace agon::extender::local_sd;
int main(){
 std::string path;
 for(auto bad:{"", "relative", "/../x", "/a/%2e%2e/x", "/a%00b", "/a%5cb", "/a//b", "/a/", "/a.", "/a%20", "/a.ext-upload", "/A.EXT-UPLOAD", "/a%252fb"})assert(!decodePath(bad,path));
 assert(decodePath("/",path)&&path=="/");assert(decodePath("/a%20b/x.bin",path)&&path=="/a b/x.bin");
 assert(jsonString("a\"\n")=="\"a\\\"\\u000a\"");
 char pattern[]="/tmp/p4sd-test-XXXXXX";char *dir=mkdtemp(pattern);assert(dir);
 std::string target=std::string(dir)+"/binary";std::string payload("\0\xff" "abc",5);
 {Upload u(target);assert(u.open());assert(u.write(payload.data(),payload.size()));assert(u.finish());}
 std::ifstream in(target,std::ios::binary);std::string read((std::istreambuf_iterator<char>(in)),{});assert(read==payload);
 {Upload u(target);assert(!u.open());assert(errno==EEXIST);} // no overwrite
 std::string partial=std::string(dir)+"/partial";
 {Upload u(partial);assert(u.open());assert(u.write("abc",3));} // disconnected before commit
 assert(!std::filesystem::exists(partial));assert(!std::filesystem::exists(partial+".ext-upload"));
 {std::ofstream stale(partial+".ext-upload");stale<<"keep";}
 {Upload u(partial);assert(!u.open());assert(errno==EEXIST);}
 assert(std::filesystem::file_size(partial+".ext-upload")==4); // never remove someone else's scratch
 {Upload u(std::string(dir)+"/missing/file");assert(!u.open());}
 {Upload u(std::string(dir)+"/empty");assert(u.open());assert(u.finish());}

 const std::string root(dir);
 auto contents = [](const std::string &p) {
   std::ifstream f(p, std::ios::binary);
   return std::string(std::istreambuf_iterator<char>(f), {});
 };
 {Upload u(target,true);assert(u.open());assert(u.write("new",3));} // interrupted replacement
 assert(contents(target)==payload);
 {Upload u(target,true);assert(u.open());assert(u.write("new",3));assert(u.finish());}
 assert(contents(target)=="new");assert(!std::filesystem::exists(target+".ext-backup"));
 {std::ofstream backup(target+".ext-backup");backup<<"old";}
 {Upload u(target,true);assert(!u.open());}
 assert(contents(target)=="new");assert(contents(target+".ext-backup")=="old");
 assert(makeDirectory(root,"/tree/a/b",true));
 assert(makeDirectory(root,"/tree/a/b",true));
 assert(!makeDirectory(root,"/tree/a/b",false));
 assert(!makeDirectory(root,"/binary/b",true));
 {Upload u(root+"/tree/a/b/log.txt");assert(u.open());std::string data(2047,'x');data+="needle";data+='\0';assert(u.write(data.data(),data.size()));assert(u.finish());}
 bool found=false;
 assert(containsText(root+"/tree/a/b/log.txt","needle",found)&&found);
 assert(containsText(root+"/tree/a/b/log.txt","absent",found)&&!found);
 assert(globMatch("*.TXT","log.txt"));assert(globMatch("l?g.*","log.txt"));assert(!globMatch("a*","log.txt"));
 assert(copyPath(root,"/tree","/clone",true,false));
 assert(contents(root+"/clone/a/b/log.txt")==contents(root+"/tree/a/b/log.txt"));
 assert(!copyPath(root,"/tree","/clone",true,false));
 assert(!copyPath(root,"/tree","/tree/nested",true,false));
 assert(!copyPath(root,"/tree","/TREE/nested",true,false));
 assert(!copyPath(root,"/tree","/newtree",false,false));
 assert(!movePath(root,"/tree","/tree/a"));
 assert(!movePath(root,"/","/elsewhere"));
 assert(movePath(root,"/clone","/renamed"));
 assert(!movePath(root,"/tree","/renamed"));
 unsigned count=0;
 auto visitor=[&](const std::string &, const struct stat &) {++count;return true;};
 assert(walk(root,"/renamed",true,visitor)&&count==3);
 assert(!removePath(root,"/renamed",false));
 assert(removePath(root,"/renamed",true));
 assert(!removePath(root,"/",true));
 assert(copyPath(root,"/binary","/copied",false,false));
 assert(!copyPath(root,"/binary","/copied",false,false));
 assert(copyPath(root,"/binary","/copied",false,true));
 assert(removePath(root,"/copied",false));
 std::string deep="/deep";
 for(unsigned n=0;n<maxDepth+2;++n){assert(makeDirectory(root,deep,true));deep+="/d";}
 count=0;assert(!walk(root,"/deep",true,visitor));assert(errno==ELOOP);
 assert(decodePath("/x.ext-backup",path,true));assert(!decodePath("/x.ext-backup",path));
 std::filesystem::remove_all(dir);
}
