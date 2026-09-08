#include "visible_text_transaction.hpp"
#include <cassert>
using T=VisibleTextTransaction;
T request(){T t;for(auto b:T::request)t.receive(b);return t;}
void parse(T &t){assert(t.begin());for(auto b:T::request){assert(t.peek()==b);assert(t.read()==b);}assert(t.read()==-1);}
int main(){
 {auto t=request();parse(t);for(auto b:T::reply)assert(t.write(b)==1);assert(t.finish());assert(!t.begin());assert(!t.available());assert(t.produced==3);}
 {T t;assert(!t.begin());t.receive(12);assert(!t.failure);assert(!t.begin());assert(!t.finish());}
 {auto t=request();t.receive(0);assert(t.failure && !t.begin());}
 {T t;t.receive(42);assert(t.failure && !t.begin());}
 {auto t=request();assert(!t.write(0x80));assert(t.failure);}
 {auto t=request();parse(t);assert(!t.write(0));assert(t.failure);}
 {auto t=request();parse(t);assert(t.write(0x80));assert(!t.finish());}
 {auto t=request();assert(t.begin());for(auto b:T::reply)t.write(b);assert(!t.finish());}
 {auto t=request();parse(t);for(auto b:T::reply)t.write(b);assert(!t.write(0));assert(!t.finish());}
}
