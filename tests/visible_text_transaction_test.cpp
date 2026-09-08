#include "visible_text_transaction.hpp"
#include <cassert>
#include <vector>
using T=VisibleTextTransaction;
std::vector<unsigned char> bytes={'H','i',13,10,23,0,0xCA,23,0,0x80,0xA7};
const unsigned char ack[]={0x80,1,0xA7};
T request(){T t;for(auto b:bytes)t.receive(b);return t;}
void parse(T &t){assert(t.begin());for(auto b:bytes){assert(t.peek()==b);assert(t.read()==b);}assert(t.read()==-1);}
int main(){
 {auto t=request();parse(t);for(auto b:ack)assert(t.write(b)==1);assert(t.finish());assert(!t.begin());assert(!t.available());}
 {T t;t.receive(12);assert(!t.failure && !t.begin());assert(!t.finish());}
 {auto t=request();t.receive(0);assert(t.failure && !t.begin());}
 for(auto bad:{0,22,127,255}){T t;t.receive(bad);assert(t.failure && !t.begin());}
 {auto t=request();assert(!t.write(0x80));assert(t.failure);}
 {auto t=request();parse(t);assert(!t.write(0));assert(t.failure);}
 {auto t=request();parse(t);assert(t.write(0x80));assert(!t.finish());}
 {auto t=request();assert(t.begin());for(auto b:ack)t.write(b);assert(!t.finish());}
 {auto t=request();parse(t);for(auto b:ack)t.write(b);assert(!t.write(0));assert(!t.finish());}
 {T t;for(unsigned i=0;i<T::text_limit;++i)t.receive('X');for(auto b:T::suffix)t.receive(b);t.receive(0xA7);assert(t.begin());}
 {T t;for(unsigned i=0;i<=T::text_limit;++i)t.receive('X');assert(t.failure);}
 {T t;for(auto b:T::suffix)t.receive(b);assert(t.failure);}
 {T t;t.receive(31);t.receive(23);assert(!t.begin());t.receive(22);for(auto b:T::suffix)t.receive(b);t.receive(0xA6);assert(t.begin());}
 for(unsigned n=1;n<bytes.size();++n){T t;for(unsigned i=0;i<n;++i)t.receive(bytes[i]);assert(!t.begin());}
 for(unsigned i=4;i<bytes.size();++i){auto altered=bytes;altered[i]=0;T t;for(auto b:altered)t.receive(b);if(bytes[i])assert(!t.begin());}
}
