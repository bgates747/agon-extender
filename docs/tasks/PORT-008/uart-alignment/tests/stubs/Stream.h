#pragma once
#include <cstddef>
#include <cstdint>
class Stream {
 unsigned timeout_{1000};
public:
 virtual ~Stream()=default;
 virtual int available()=0;virtual int read()=0;virtual int peek()=0;virtual void flush()=0;
 virtual size_t write(uint8_t)=0;virtual size_t write(const uint8_t*,size_t)=0;
 virtual size_t readBytes(char *p,size_t n) {size_t used=0;while(used<n){int c=read();if(c<0)break;p[used++]=char(c);}return used;}
 virtual size_t readBytes(uint8_t*p,size_t n){return readBytes(reinterpret_cast<char*>(p),n);}
 void setTimeout(unsigned n){timeout_=n;}unsigned getTimeout()const{return timeout_;}
};
