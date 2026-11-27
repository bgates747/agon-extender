#ifndef OLIMEX_REPORT_WRITER_H
#define OLIMEX_REPORT_WRITER_H

#include <stddef.h>

/* Check argv[1] before starting the workload. Pass the same token after it. */
int olx_report_token(const char *token);

/* Writes an OLXR1 envelope and payload to a new absolute SD path. Returns zero
 * only when every byte was written and the file closed successfully. */
int olx_report_save(const char *token, const char *path, const void *payload, size_t size);

#endif
