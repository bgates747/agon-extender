"""Isolate the standalone pair experiment in two pinned IDF 5.5.5 units."""
import hashlib
from pathlib import Path
import sys


def derive(original):
    data = original.read_bytes()
    source = data.decode()

    def replace(old, new):
        nonlocal source
        if source.count(old) != 1:
            raise ValueError(f"Expected one {old[:64]!r} in {original.name}")
        source = source.replace(old, new)

    if original.name == "esp_lcd_panel_dpi.c":
        expected = "a0b13536fec34d3cc4a6324ab64bc9bb62fee4db39dec24133681bc3c17b8373"
        replace("IRAM_ATTR\nstatic bool async_fbcpy_done_cb", '#include "pair_runtime.inc"\n\nIRAM_ATTR\nstatic bool async_fbcpy_done_cb')
        replace("    uint8_t fb_index = dpi_panel->cur_fb_index;", "    if (pair_on_frame(dpi_panel)) return false;\n    uint8_t fb_index = dpi_panel->cur_fb_index;")
        replace("    if (intr_status & MIPI_DSI_BRG_LL_EVENT_UNDERRUN) {", "    if ((intr_status & MIPI_DSI_BRG_LL_EVENT_UNDERRUN) && pair_on_underrun()) return;\n    if (intr_status & MIPI_DSI_BRG_LL_EVENT_UNDERRUN) {")
        replace("        .on_full_trans_done = mipi_dsi_dma_trans_done_cb,", "        .on_full_trans_done = mipi_dsi_dma_trans_done_cb,\n        .on_block_trans_done = pair_on_block,\n        .on_invalid_block = pair_on_invalid,")
    elif original.name == "dw_gdma.c":
        expected = "ace979c51265cd782d061c1dc157530fb13f8e8cc834234df6c50eb2fe2a349f"
        replace("void dw_gdma_channel_default_isr(void *args)\n{", """extern uint32_t pair_irq_enter(void *channel);
extern void pair_irq_status(uint32_t status);
extern void pair_irq_leave(uint32_t entered);
void dw_gdma_channel_default_isr(void *args)
{
    uint32_t pair_entered = pair_irq_enter(args);""")
        replace("    // call user callbacks", "    if (pair_entered) pair_irq_status(intr_status);\n    // call user callbacks")
        replace("    if (need_yield) {\n        portYIELD_FROM_ISR();", "    if (pair_entered) pair_irq_leave(pair_entered);\n    if (need_yield) {\n        portYIELD_FROM_ISR();")
    else:
        raise ValueError(original)
    if hashlib.sha256(data).hexdigest() != expected:
        raise ValueError(f"Unreviewed SDK source: {original.name}")
    return source


if __name__ == "__main__":
    src, target = map(Path, sys.argv[1:])
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(derive(src))
