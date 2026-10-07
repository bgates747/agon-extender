# Initial interactive demo — 2026-10-02

## Executive summary

Installed the experimental P4-PC playground r03 candidate with bounded physical
checks passing. It leaves the orbit animation running and Ethernet active.
Subsequent Author review reports mostly black HDMI and only audio pops;
physical video/audio output is not accepted. Further diagnosis is active.
No Extender production selection or Agon firmware changed.

| Check | Result |
|---|---|
| Native ARM host build | ESP-IDF 5.5.5 build passed |
| Factory rollback | Complete 16 MiB read, device digest matched |
| Candidate flash | Bootloader, partition table, app independently verified |
| Boot | Correct r03 identity, 360 MHz CPU, 32 MiB PSRAM test pass |
| HDMI initialization | 1280x720 RGB888; physical appearance awaits Author |
| Ethernet | DHCP obtained; 30/30 Pi pings, 0% loss, mean 1.040 ms |
| Serial interaction | Commands complete without resetting through Linux client |
| Scenes | Nine orbit/bounce/bars switches acknowledged |
| Pause/resume | Update counter held at 3 while paused, advanced to 7 after resume |
| Audio | 440 Hz/3 s tone and C-major melody completed; listening awaits Author |
| SD | Root listing passed; no format or file-write test invoked |
| Event task stack | Minimum remaining 5504 bytes during bounded checks |

Build: `p4pc-playground-r03-b2026-10-03-03-06-28Z`.
Sources and control instructions: [P4-PC playground](../../../vdp/p4pc-demo/README.md).
Machine endpoints, backup hashes and evidence paths: ignored `HARDWARE.local.md`.
Candidate archive retains exact source, dependency lock, SDK configuration,
firmware segments, ELF/map, hashes, boot and check logs.

## Limits and corrections

1. The first candidate overflowed the inherited event stack while logging;
   the second exposed animation/CPU starvation. Both informative failures and
   remedies are recorded in the task; r03 passed the bounded checks above.
2. The initial host serial helper toggled modem lines on open. The maintained
   Linux helper avoids those transitions and requires a command-specific reply.
3. HDMI scanout timing is not rendering throughput. Animation sleeps at least
   33 ms between updates; actual updates depend on rendering/lock time. No
   presentation FPS, latency or full peripheral qualification is claimed.
4. Audio uses the analog codec/headset jack; stereo separation and HDMI audio
   are not tested. No microphone is required or tested.
5. This experimental entry point is intentionally separate from Extender
   firmware. Agon remains disconnected, and EMOS contracts remain unchanged.

## r04 physical observations

With direct CPU-written framebuffer bars selected and LVGL refresh paused,
the Author still sees mostly blank HDMI with only brief unrecognizable images.
No stable colour bars or animation have been demonstrated. The framebuffer
contains the intended nonzero bar data; that software observation does not
prove correct HDMI transmission.

At codec volume 65, the Author heard a quiet sustained tone for approximately
five seconds from the requested 440 Hz test. Duration and audibility passed
by observation; frequency accuracy, output level and fidelity are unmeasured.
The earlier r03 audio failure is therefore not the current audio result.

The original factory image was subsequently restored in full and independently
verified before reset. Serial confirms the original application/ELF identity
and HDMI initialization. The Author confirmed its BOOT prompt stays visible.
The r04 experiment remains preserved; r05 was subsequently installed.

## r05 display-only result

Build `p4pc-playground-r05-b2026-10-03-03-27-56Z` was independently verified,
booted to READY and answered USB info with scene 2, zero animation updates,
no IP and SD unmounted. Ethernet, SD and audio initialization were inactive.
The Author subsequently reported a dark screen; possible flashes could not be
identified or distinguished from reboot effects. Visual result: failed.

The retained USB sample supports application responsiveness at capture time;
it does not prove continuous stability after that sample. No crash loop is
established. The exact factory control passes where the rebuilt display-only
experiment fails. Display initialization, configuration and SDK/driver differences
remain investigative candidates. r05 was subsequently replaced by the accepted matched-timing r06 experiment.
See the [current task state](../P4PC-001.md); prior failure evidence is retained.

## r06 matched-timing experiment

Build `p4pc-playground-r06-b2026-10-03-23-36-20Z` passed the ARM64 native build,
exact-segment verification and explicit boot/USB checks. Complete r05 rollback
was device-verified before replacement; the factory backup is unchanged.
Startup selects direct framebuffer bars with display timing calculated at
59.979 Hz and peripherals inactive. Author subsequently confirmed steady bars and moving orbital circles, but
reported poor animation rate. The widgets slideshow hit LVGL allocation-assertion
starvation; failure evidence is retained. Actual refresh is unmeasured and
animation quality remains unaccepted. See current task state for the fix.

## Subsequent r08/r09 rendering result

The Author reports r08 looks much better but requests a frame-rate benchmark.
Installed r09's [timed result](BENCHMARK.md) measures 12 completed LVGL render
passes/s and approximately 60 panel completions/s for the 24-circle 720p scene.
The widgets slideshow subsequently passed a ten-second software check at
approximately 4.7 render passes/s with about 1 MB pool headroom; the Author confirms visibly changing widgets. These are standalone experimental results, not production or
60-animated-fps acceptance. Verified factory and preceding-image rollback remain.
