# Direct ExCom text capture

## Executive summary

GET `/screen/text` samples the P4 display through the existing VDP glyph reader.
It never connects to `/video` or replaces its viewer. The host helper handles
202/polling and prints text. Capture is non-atomic; live drawing, blinking cursor,
changed fonts/colours and retained edge exclusions may produce unknown cells.
ASCII is returned; other glyph codes are represented by `?`.

Run from Extender:

```sh
.venv/bin/python scripts/screen_text.py --url http://EXTENDER_ADDRESS
```

HTTP queues capture; the VDU owner samples eight cells per parser iteration.
Context/dimension changes abort with 409. One outstanding capture is shared;
use one text reader at a time. HTTP returns 202 until ready, then consumes the
result with 200. A timed-out reader can retry to retrieve its pending result.
No eZ80 command, SD file or UART reply is generated. In Legacy the P4 retains
its own display; this endpoint does not read the mainboard's screen.

Host test:

```sh
g++ -std=c++17 -fsanitize=address,undefined -I . -I docs/tasks/BENCH-006/tests docs/tasks/BENCH-006/tests/capture.cpp -o /tmp/agon-screen-text-test
/tmp/agon-screen-text-test
```

Hardware evidence is recorded in RESULTS.md. Build derives from the retained
pair-RLE candidate to preserve installed codecs and fullscreen assets. Only text
capture integration changes. Private manifests/source overlays remain under
agents/screen-text; pair-RLE remains the rollback image.
