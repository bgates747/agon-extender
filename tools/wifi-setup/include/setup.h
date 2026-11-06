/* SPDX-License-Identifier: GPL-3.0-only */
#ifndef WIFI_SETUP_H
#define WIFI_SETUP_H
#include <stddef.h>
#include <stdint.h>
#include <stdio.h>
#define WS_REPLY 2048
#define WS_LINE 512
#define WS_OK 0
#define WS_CONFIG 2
#define WS_CANCEL 3
#define WS_MODEM 4
#define WS_TIMEOUT 5
#define WS_PROTOCOL 6
#define WS_LOG 7
#define WS_CLOCK 8
struct ws_config {
 char ssid[33],password[65],host[64];
 unsigned port,baud,tick_hz,command_seconds,join_seconds,bbs_seconds;
};
struct ws_io {
 void *ctx;
 uint32_t (*now)(void *);
 int (*escape)(void *);
 int (*receive)(void *); /* -1 empty, 0..255 byte */
 int (*transmit)(void *,unsigned char); /* 1 sent, 0 busy, -1 closed */
 void (*idle)(void *);
 int (*message)(void *,const char *); /* durable log + display; nonzero success */
};
struct ws_state {
 struct ws_config cfg;
 struct ws_io io;
 char line[WS_LINE],reply[WS_REPLY],batch[WS_REPLY],ip[48],mac[48];
 size_t line_n,reply_n,batch_n;
 unsigned ipd_left,ipd_frames;
 uint32_t last_clock,still_polls;
 int ok,send_ok,prompt,closed,error,failed,secret,uncertain,data_pending,connected;
};
void ws_defaults(struct ws_config *);
struct ws_reader {void *ctx;int (*next)(void *);}; /* -1 EOF, -2 I/O error */
int ws_read_config(const struct ws_reader *,struct ws_config *,char *,size_t,int (*)(void *),void *);
int ws_run(struct ws_state *,const struct ws_config *,const struct ws_io *);
#endif
