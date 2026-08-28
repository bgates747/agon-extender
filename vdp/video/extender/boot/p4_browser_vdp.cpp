// PORT-003 Phase F Arduino-sketch compilation bridge.
//
// ESP-IDF's hybrid application component does not perform Arduino's .ino
// prototype-generation pass. This exceptional translation unit supplies only
// those generated declarations, then compiles the retained upstream-named
// video.ino directly. Lifecycle and parser ownership remain in video.ino;
// future upstream comparisons therefore do not have a second copied setup or
// loop to reconcile.

#define AGON_EXTENDER_P4_BOOT 1

void processLoop(void *parameter);
void boot_screen();
void debug_log(char const *format, ...);
void force_debug_log(char const *format, ...);
void setConsoleMode(bool mode);
void startTerminal();
void stopTerminal();
void suspendTerminal();
bool processTerminal();
void print(char const *text);
void printFmt(char const *format, ...);

#include "../../video.ino"
