#pragma once
#define STRIP_BLOCKS 12
#define STRIP_ROLLING 1
#define STRIP_SLOTS 3
#define STRIP_REFILL_LIMIT_US ((12000 / STRIP_BLOCKS) * (STRIP_SLOTS - 1))
// Optional negative control; zero disables it. Not normal workload timing.
#define STRIP_INJECT_LATE_TAG 0
