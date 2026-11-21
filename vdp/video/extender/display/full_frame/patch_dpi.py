"""Apply the full-frame stop hook only to the pinned IDF 5.5.5 DPI unit."""
import hashlib
from pathlib import Path
import sys


def derive(data):
    if hashlib.sha256(data).hexdigest() != "a0b13536fec34d3cc4a6324ab64bc9bb62fee4db39dec24133681bc3c17b8373":
        raise ValueError("unreviewed DPI driver")
    source = data.decode()
    edits = [
        ('#include <sys/param.h>', '#include <sys/param.h>\n#include <stdatomic.h>\n#include "hal/dw_gdma_ll.h"'),
        ('    uint8_t virtual_channel;', '    atomic_uint stop_state;\n    uint8_t virtual_channel;'),
        ('IRAM_ATTR\nstatic bool async_fbcpy_done_cb', '#include "dpi_stop.inc"\n\nIRAM_ATTR\nstatic bool async_fbcpy_done_cb'),
        ('    uint8_t fb_index = dpi_panel->cur_fb_index;', '''    if (atomic_load(&dpi_panel->stop_state) == DPI_DRAINING) {
        atomic_store(&dpi_panel->stop_state, DPI_EOF);
        return false;
    }
    if (atomic_load(&dpi_panel->stop_state) == DPI_EOF) return false;
    uint8_t fb_index = dpi_panel->cur_fb_index;'''),
        ('    dw_gdma_channel_enable_ctrl(dma_chan, true);',
         '    atomic_store(&dpi_panel->stop_state, DPI_RUNNING);\n    dw_gdma_channel_enable_ctrl(dma_chan, true);'),
    ]
    for old, new in edits:
        if source.count(old) != 1:
            raise ValueError(f"unexpected DPI source at {old!r}")
        source = source.replace(old, new)
    return source


if __name__ == "__main__":
    original, target = map(Path, sys.argv[1:])
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(derive(original.read_bytes()))
