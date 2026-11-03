#!/usr/bin/env python3
"""PORT-008 RU05-F01: keep whole-file TX descriptor arrays in P4 PSRAM.

Pinned IDF5.5.5/b774170 allocates two complete PARLIO descriptor arrays in
internal SRAM. That intentional default exhausts the matched HDMI composition
for1.1MB while payload PSRAM remains available. P4 PARLIO uses AXI-GDMA; the
same SDK tests AXI descriptor lists in external memory (test_gdma.c).
Select its existing storage flag, preserving allocator alignment, cache sync,
loop mounting, interrupts and destruction. Never edit the SDK or patch RX.
Remove after a selected driver exposes an equivalent descriptor-storage option
or the bounded carrier is replaced. External flash encryption retains the SDK's
explicit internal-memory fallback/refusal; it is not bypassed here.
"""
import hashlib
from pathlib import Path
import sys

UPSTREAM_SHA256 = 'e47fde7865ec9d9b869826ce0a1fcb9c1adf1b879ef2833c10ab96e01bf9eeb9'


def derive(source: bytes) -> str:
    if hashlib.sha256(source).hexdigest() != UPSTREAM_SHA256:
        raise ValueError('unreviewed PARLIO TX source')
    before = '''    gdma_link_list_config_t dma_link_config = {
        .item_alignment = PARLIO_DMA_DESC_ALIGNMENT,
        .num_items = num_dma_nodes,
    };'''
    after = '''    /* Extender PORT-008 RU05-F01: P4 AXI-GDMA supports PSRAM descriptors.
     * Keep both complete loop lists outside scarce scanout/internal SRAM.
     * gdma_new_link_list owns alignment/cache/encryption handling unchanged. */
#if !CONFIG_IDF_TARGET_ESP32P4
#error "Extender upload descriptor selection is P4-only"
#endif
    gdma_link_list_config_t dma_link_config = {
        .item_alignment = PARLIO_DMA_DESC_ALIGNMENT,
        .num_items = num_dma_nodes,
        .flags = { .items_in_ext_mem = true },
    };'''
    text = source.decode()
    if text.count(before) != 1:
        raise ValueError('expected exactly one PARLIO TX descriptor config')
    return text.replace(before, after)


if __name__ == '__main__':
    source, target = map(Path, sys.argv[1:])
    text = derive(source.read_bytes())
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text)
