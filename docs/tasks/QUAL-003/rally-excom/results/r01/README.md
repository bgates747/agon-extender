# Protected-page probe r01

## Executive summary

Legacy and ExCom each passed64/64pixel checks on installed pre-E09 firmware.
Basic protected HUD-region scrolling, alternating pages and negative-left
horizontal-span clipping did not reproduce the reported Rally errors. Advance
to direct bitmap clipping and road triangles. No performance conclusion.

Both CSVs are identical (including64matches and terminal success). Fixture
RXPROBE r01, source9e3f46a, binary11087bytes SHA256
cf3855ecfccf9fd2f3231d5ca654662bfaf7b532131c309d43d9985b92b93556.
Route and mode136 selected by temporary root startup; no firmware flash.
Current production Rally remains9e75196. Ignored run02 records preserve original
startup and older activation backup. Mainboard returned to Legacy SD service.
A brief P4 browser capture taken while awaiting completion is status evidence,
not a frame-rate benchmark or a framebuffer-only claim for the whole run.
The initial offline service check was premature: both tests completed without
intervention. Original startup restoration follows this diagnostic tranche.

This microprobe contains no car assets, full HUD font, triangle strips or
full-game dynamics; passing it does not establish those features' correctness.
