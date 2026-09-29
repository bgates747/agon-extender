# Historical hybrid build material

BUILD-001 replaced PlatformIO/SCons with native ESP-IDF/CMake as the sole
maintained P4 build authority. Files in this directory and `vdp/platformio.ini`
remain only to reproduce identified pre-cutover evidence, especially hybrid r61.
They are not a second current source/profile authority.

Routine builds use `scripts/build_p4.py` and `vdp/build/p4-profiles.json`.
`scripts/vdp-pio.sh` refuses execution unless the operator supplies the explicit
historical-use acknowledgement documented by that script. Frozen diagnostic
builders retain their owning task contracts; a future need must define a native
profile under a bounded task instead of silently reviving a hybrid environment.
