#include <stdint.h>

typedef struct { int open; } FIL;
typedef uint32_t uint24_t;
enum { FA_WRITE = 2, FA_CREATE_NEW = 4 };
uint8_t ffs_fopen(FIL *file, const char *name, uint8_t mode);
uint8_t ffs_fclose(FIL *file);
