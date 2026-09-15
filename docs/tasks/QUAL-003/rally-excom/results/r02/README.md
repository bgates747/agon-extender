# Direct bitmap and triangle probe r02

## Executive summary

Both displays returned identical68pixel samples, with all16fixed expectations
per path passing. Raw triangle clipping and a directly drawn clipped bitmap did
not reproduce the reported game error. No performance or full-game claim.

Fixture source2d08daf. Paired raw CSVs and comparison.json retained. Installed
pre-E09 firmware unchanged. Exact binary identity remains in local run03 staged
manifest and will accompany this tranche's final report. The collector elapsed
32.65s excludes initial test time and includes SD retrieval: not rendering time.

Next trace boundary: current LookupRoad emits section::draw's buffered matrix
program, not the older Road::quad direct triangles. Reproduce that exact stream.
Official stock types.h casts negative float fixed-point results directly to
unsigned; this is a CPU-portability hypothesis, not a demonstrated fault yet.
