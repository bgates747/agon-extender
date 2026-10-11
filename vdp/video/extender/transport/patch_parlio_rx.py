#!/usr/bin/env python3
"""FWBUG-016: drain coalesced finite RX descriptors in pinned IDF5.5.5.

Upstream b774170ff46c393eeb5e495ea37936038d3f4f4f counts one descriptor per
DONE interrupt. A body/tail pair can complete before that interrupt is served;
EOF then exposes only the body count. Preserve its per-node cache/copy logic,
but visit every completed node before EOF. Never fabricate the requested count.
Only the explicit ExExt build derives this unit; the SDK is not edited.
Remove after a selected SDK supplies equivalent finite RX accounting and the
coalesced/short-transfer controls plus physical stream regression pass.
"""
import hashlib
import sys
from pathlib import Path

def derive(source):
    assert hashlib.sha256(source).hexdigest() == "500a7dbe012f7bf8d8de10c3be2b08d217247d8e9c091d2e02b18f9f03f8a5c7", "unreviewed PARLIO RX source"
    text = source.decode()
    name = "static bool parlio_rx_default_desc_done_callback("
    assert text.count(name) == 1
    text = text.replace(name, "static bool parlio_rx_one_desc_done_callback(")
    marker = "static esp_err_t parlio_rx_create_dma_link("
    assert text.count(marker) == 1
    wrapper = """/* FWBUG-016: DONE is a status bit, not a queue of descriptor events.
 * Finite body/tail completions can coalesce. Read actual noncached descriptor
 * ownership/length and retain upstream cache synchronization/partial callbacks.
 * Bound traversal and never wrap into an already-accounted finite node. */
static bool parlio_rx_default_desc_done_callback(gdma_channel_handle_t dma_chan,
                                                gdma_event_data_t *event_data,
                                                void *user_data)
{
    parlio_rx_unit_handle_t rx_unit = (parlio_rx_unit_handle_t)user_data;
    if (event_data->flags.abnormal_eof || rx_unit->curr_trans.flags.infinite) {
        return parlio_rx_one_desc_done_callback(dma_chan, event_data, user_data);
    }
    bool need_yield = false;
    for (uint32_t visited = 0; visited < rx_unit->node_num &&
         rx_unit->curr_node_id < rx_unit->node_num &&
         rx_unit->curr_trans.recv_bytes < rx_unit->curr_trans.tot_trans_size;
         ++visited) {
        gdma_lli_owner_t owner = GDMA_LLI_OWNER_DMA;
        if (gdma_link_get_owner(rx_unit->dma_link, rx_unit->curr_node_id, &owner) != ESP_OK ||
            owner != GDMA_LLI_OWNER_CPU ||
            !gdma_link_get_length(rx_unit->dma_link, rx_unit->curr_node_id)) {
            break;
        }
        uint32_t completed_node = rx_unit->curr_node_id;
        need_yield |= parlio_rx_one_desc_done_callback(dma_chan, event_data, user_data);
        if (completed_node + 1 == rx_unit->node_num) {
            /* Finite links end at NULL. Keep a consumed-chain sentinel even
             * after a short EOF, so a stale DONE cannot count that node twice.
             * parlio_rx_mount_transaction_buffer resets this index to zero. */
            rx_unit->curr_node_id = rx_unit->node_num;
        }
    }
    return need_yield;
}

"""
    return text.replace(marker, wrapper + marker)

if __name__ == "__main__":
    source, target = map(Path, sys.argv[1:])
    text = derive(source.read_bytes())
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text)
