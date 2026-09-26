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
 std::filesystem::remove_all(dir);
}
