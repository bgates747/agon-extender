# Direct ExCom text capture

## Executive summary

Implementation and bounded physical review are complete. Routine retrieval,
HTTP behavior and current limitations are maintained in the
[screen-text guide](../../screen-text.md); this silo retains implementation
checks and the identified [hardware result](RESULTS.md). Legacy readback remains
deferred in [the task](../BENCH-006.md).

## Retained local check

Host test:

```sh
g++ -std=c++17 -fsanitize=address,undefined -I . -I docs/tasks/BENCH-006/tests docs/tasks/BENCH-006/tests/capture.cpp -o /tmp/agon-screen-text-test
/tmp/agon-screen-text-test
```

The recorded build derived from the retained
pair-RLE candidate to preserve installed codecs and fullscreen assets. Only text
capture integration changed. Private manifests/source overlays remain under
agents/screen-text; pair-RLE was the preserved rollback image for that run, not a current selection.
