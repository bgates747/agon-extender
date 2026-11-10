#pragma once
void net008_info(unsigned baud);
void net008_bench(unsigned old_baud,unsigned new_baud,unsigned milliseconds,const char *ip,unsigned port,unsigned nonce);

#include <cstdint>
#include <cstddef>
void net008_join(unsigned baud,const uint8_t *ssid,size_t ns,const uint8_t *password,size_t np);

void net008_loopback(unsigned baud,unsigned milliseconds,unsigned profile);
