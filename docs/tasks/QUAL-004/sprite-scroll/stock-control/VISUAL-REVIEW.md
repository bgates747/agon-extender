# Stock sprite visual review

Author requests a manual visual control of SS_INITIAL on the installed official
stock VDP v2.16.0. The host verifies existing player/input files and deploys this
startup; it must not invoke the scene before the Author is watching:

```text
SET KEYBOARD 1
EMOS KEYINPUT extender
EMOS LEGACY
VDU 22 20
LOAD /test/qual004/q4draw.bin
```

Once the monitor has settled, the Author enters:

```text
RUN . /test/qual004/SS_INITIAL.vdu
```

No capture token is supplied. The fixture itself does not change video modes.
This initial checkpoint is static: look for the striped background and two
software sprites, and report corruption, tearing or a freeze. Lack of sprite
motion is expected. A photo can retain visual anomalies; this is not an exact
pixel-comparison qualification. Escape exits the player. Reset reloads it without
running it. Original startup is preserved locally for subsequent restoration.

## Author observation — accepted visual control

Author reports red/green/blue/white vertical stripes; a red rectangular/X-like
sprite over the first white stripe from the left; and a cyan box/diagonal
pattern farther right over a red stripe. Image is stationary and stable, with
no apparent monitor/scanout disruption. This matches the intended initial scene.
Record SS_INITIAL as a human-observed stock visual pass. No photo or exact pixel
comparison was supplied. The Author subsequently sent Escape through the browser
and confirmed a clean return to MOS for this run.
The separate diagnostic capture failure remains unresolved. No additional scene
or bench operation follows automatically from this observation.
