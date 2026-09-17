#pragma once
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stddef.h>
void *sz_alloc(size_t);
void *sz_calloc(size_t,size_t);
void sz_free(void *);
_Noreturn void sz_fail(int);
int sz_get(void);
int sz_put(int);
int sz_unget(int,FILE *);
size_t sz_read(void *,size_t,size_t,FILE *);
size_t sz_write(const void *,size_t,size_t,FILE *);
#define malloc sz_alloc
#define calloc sz_calloc
#define free sz_free
#define exit(x) sz_fail(1)
#define abort() sz_fail(1)
#define getchar sz_get
#define putchar sz_put
#define ungetc sz_unget
#define fread sz_read
#define fwrite sz_write
#define fprintf(...) ((void)0)
