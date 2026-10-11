#!/usr/bin/env python3
"""FWBUG-015: isolated IDF5.5.5 teardown fix; never edit the pinned SDK.

The last group release gates DW-GDMA registers. Its shared IRQ dispatcher must
be joined first, or even an unrelated shared IRQ can read the gated status reg.
Pinned upstream: b774170ff46c393eeb5e495ea37936038d3f4f4f.
Remove when a selected SDK supplies equivalent IRQ-before-clock lifetime order,
with mode-transition regression. No DMA transfer or renderer behavior changes.
"""
import hashlib
import sys
from pathlib import Path

def derive(source):
    assert hashlib.sha256(source).hexdigest() == "ace979c51265cd782d061c1dc157530fb13f8e8cc834234df6c50eb2fe2a349f", "unreviewed DW-GDMA source"
    old = """    if (chan->group) {
        channel_unregister_from_group(chan);
    }
    if (chan->intr) {
        esp_intr_free(chan->intr);
    }
"""
    new = """    /* FWBUG-015: join the shared ISR before the last group can gate its
     * status-register clock. IDF5.5.5 released that clock before freeing IRQ. */
    if (chan->intr) {
        esp_intr_free(chan->intr);
    }
    if (chan->group) {
        channel_unregister_from_group(chan);
    }
"""
    text = source.decode()
    assert text.count(old) == 1, "unexpected channel_destroy inventory"
    return text.replace(old, new)

if __name__ == "__main__":
    source, target = map(Path, sys.argv[1:])
    text = derive(source.read_bytes())
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text)
