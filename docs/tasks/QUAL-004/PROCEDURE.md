# QUAL-004 run procedure

## Executive summary

Two mainboard scanout captures and two fresh matching P4 snapshot generations
are required for each static scene. Compare every pixel in canonical BBGGRR.
Timing during serial extraction is not a rendering benchmark.

1. Build isolated diagnostic with build_mainboard.py; freeze stock hashes and
   image manifest. Back up actual installed mainboard flash, independently verify,
   check partition compatibility, then write/verify only the diagnostic app.
2. Use one continuously owned debug serial reader at115200 baud. Opening the
   port can reset VDP; perform normal eZ80 readmission after opening. No P4 flash.
3. Stage fixture and generated scene files beneath /test/qual004 using verified
   SD service activation/readback. Startup configures both routes to mode20,
   returns Legacy and starts SD service. Preserve actual previous startup bytes.
4. Run run_hardware.py from repository root with a private common module on
   PYTHONPATH. That module supplies R (private state directory), URL, admitted
   cli(), and the established keyboard/SD clients. It contains machine-specific
   information and is not tracked. Preserve hashes of that adapter with the run.
5. Each mainboard scene is replayed twice; diagnostic op EE has a unique token.
   Validate all384 rows, widths, row checksums and successful terminal status.
   Repeat images must match. Exit scene with ESC only after capture completion.
6. P4 receives identical scene bytes, then host requests four immutable images.
   Ignore initial retained images; last two generations must be distinct and
   pixel-identical. Neither browser scaling nor rendering is involved.
7. Report mismatches as failures, not implementation work. On acquisition errors,
   retain evidence, investigate capture/setup first. Mark unimplemented features
   separately. No mask/crop/tolerance may turn differing pixels into a pass.
8. At end restore backed-up VDP app erase sectors and exact startup bytes,
   independently verify, reset/readmit if necessary and leave usable Legacy CLI.
   No audio alert, no experimental push. Record any incomplete restoration.

The serial row tap currently covers64-colour scanout only. Static raster effects
are eligible if repeats match; time-varying effects require coherent-frame
capture and are deferred. Optional lower-depth support is diagnostic capture
work, never permission to implement missing video APIs.

Before the first image run, after SD staging completes and the SD service exits,
independently verify the P4 application against the preserved r43 image using
esptool verify_flash. This writes no flash but resets P4, so wait for application
startup and reset/readmit eZ80 into the preserved test startup before continuing.
A changed P4 boot counter since the previous session makes this fresh identity
check preferable to relying solely on historical restoration records.
