#!/usr/bin/env python3
"""HDMI-002: timestamp the pinned copy helper without changing its operations.

ESP-IDF5.5.5 b774170f is a read-only input. The derivative exists only in an
explicit rolling build. Remove this temporary probe when the deadline cause is
resolved. DMA-to-callback still includes IRQ delivery and driver cleanup.
"""
from pathlib import Path
import hashlib,sys
BASE_SHA256='6174cb19c4630769fe2dc9ed37f3d17abacc2d99d9743f1a35a0eb278e12e702'
def derive(source:bytes)->str:
    if hashlib.sha256(source).hexdigest()!=BASE_SHA256:
        raise ValueError('unreviewed fbcpy SDK source')
    text=source.decode()
    replacements=[
        ('#include "esp_async_fbcpy.h"','#include "esp_async_fbcpy.h"\n#include "strip_probe.h"'),
        ('    // submit the DMA2D request','    agon_scanout_copy_phase(mcp->cb_args, 0); // descriptors/cache complete\n\n    // submit the DMA2D request'),
        ('    dma2d_channel_handle_t tx_chan = NULL;','    agon_scanout_copy_phase(mcp->cb_args, 1); // pool admitted the job\n    dma2d_channel_handle_t tx_chan = NULL;'),
        ('    dma2d_start(tx_chan);','    agon_scanout_copy_phase(mcp->cb_args, 2); // before either channel starts\n    dma2d_start(tx_chan);'),
        ('    if (mcp->memcpy_done_cb) {','    agon_scanout_copy_phase(mcp->cb_args, 3); // EOF callback, after driver cleanup\n    if (mcp->memcpy_done_cb) {'),
    ]
    for old,new in replacements:
        if text.count(old)!=1:raise ValueError('fbcpy probe anchor changed: '+old)
        text=text.replace(old,new)
    return text
if __name__=='__main__':
    source,target=map(Path,sys.argv[1:]);text=derive(source.read_bytes())
    target.parent.mkdir(parents=True,exist_ok=True);target.write_text(text)
