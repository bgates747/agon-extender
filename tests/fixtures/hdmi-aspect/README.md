# Mode-3 HDMI aspect review

The generated MOS command file draws a mode-3 geometry check using ordinary
EMOS-routed VDU output, then returns to a Legacy listener with the picture
retained. Startup must already select mode 3 and finish in Legacy. Invoke the
fixture separately at a verified CLI; it selects no mode and launches no game.

The white box occupies 96×48 logical pixels. Stock mode 3 repeats each row twice,
so its expected physical presentation is 96×96 pixels, square. Each colored
horizontal line occupies one logical row and should occupy two output rows.
The entire 640×240 logical border should be visible inside centered 640×480
presentation on the proven 848×480 HDMI carrier. Do not judge this fixture using
a square-logical-pixel assumption: mode 3's logical pixels are intentionally
non-square in the stock physical presentation.

Supply a complete `hdmi-aspect-r01-bTIMESTAMP` identity and the exact installed
firmware build ID to `generate.py`. It writes a fresh command file, never
replacing a prior artifact. Keep payload/source hashes in its local manifest.
Deploy maintained copies under `/extender`, retain evidence/startup backups
under `/agents/extender`, and restore ordinary startup before the final review.
No complete benchmark, performance improvement or visual acceptance is implied.
[HDMI-003](../../../docs/tasks/HDMI-003.md) owns the gate and evidence.
