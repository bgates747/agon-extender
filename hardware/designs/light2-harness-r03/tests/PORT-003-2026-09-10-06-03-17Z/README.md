# RGB222 P4 deployment verified

Console r06 passed flash/readback verification, candidate identity, native USB
keyboard enumeration and HTTP startup. HTTP assets match the candidate source.
An isolated Chromium client received and presented five 640×480 RGB222 frames,
then disconnected; HTTP remained available. The client is closed. These are
installation/startup checks, not slideshow throughput or sustained stability
qualification. EMOS and the Agon were not flashed or reset.

The first r05 deployment passed flash/readback but did not start HTTP despite
DHCP. Its unrestricted high-priority snapshot composition was replaced with
consumer-demand admission in r06. The decoder/UI remain those accepted in the
local visual review. Informative r05 logs remain in ignored local bench records.

The SD is safely unmounted with exactly these autoexec commands:

```
EMOS KEYINPUT extender
CD /mystuff/slideshow/64
```

`app.bin` and its assets already exist there and were not changed. The Author
owns mode selection and application launch. Refresh the P4-served browser page
to load the RGB222 decoder before connecting. No local preview frame rate is
claimed as P4 performance. See the owning PORT-003 task for remaining review.
