// Pure ownership/scheduling rules shared by the DPI driver and its host test.
// A hardware descriptor is valid only while its specific slot generation is
// ready. Three physical slots are disjoint from the 12/15 logical blocks.
#pragma once
#include <stdbool.h>
#include <stdint.h>

enum { NR_ROWS = 32, NR_SLOTS = 3, NR_LIMIT_US = 1600 };
typedef struct { uint32_t frame; unsigned block; } nr_tag;
typedef struct { nr_tag tag; bool ready; } nr_slot;
typedef struct {
    unsigned count, retired;
    uint32_t frame;
    nr_slot slots[NR_SLOTS];
} nr_ring;

static inline bool nr_equal(nr_tag a, nr_tag b) {
    return a.frame == b.frame && a.block == b.block;
}
static inline nr_tag nr_advance(nr_tag tag, unsigned n, unsigned count) {
    tag.block += n;
    if (tag.block >= count) { tag.block -= count; ++tag.frame; }
    return tag;
}
static inline void nr_prime(nr_ring *r, unsigned count) {
    r->count = count; r->retired = 0; r->frame = 0;
    for (unsigned s = 0; s < NR_SLOTS; ++s) {
        r->slots[s] = (nr_slot){ .tag = {0, s}, .ready = true };
    }
}
static inline bool nr_ready(const nr_ring *r, nr_tag tag) {
    const nr_slot *slot = &r->slots[tag.block % NR_SLOTS];
    return slot->ready && nr_equal(slot->tag, tag);
}
static inline bool nr_retire(nr_ring *r, nr_tag *released, nr_tag *refill) {
    if (r->retired >= r->count) return false;
    *released = (nr_tag){r->frame,r->retired};
    if (!nr_ready(r,*released)) return false;
    *refill = nr_advance(*released,NR_SLOTS,r->count);
    r->slots[released->block % NR_SLOTS] = (nr_slot){.tag = *refill, .ready = false};
    ++r->retired;
    return true;
}
static inline bool nr_can_write(const nr_ring *r, nr_tag tag) {
    const nr_slot *slot = &r->slots[tag.block % NR_SLOTS];
    return !slot->ready && nr_equal(slot->tag,tag);
}
static inline bool nr_publish(nr_ring *r, nr_tag tag, uint64_t age_us) {
    if (age_us > NR_LIMIT_US || !nr_can_write(r,tag)) return false;
    r->slots[tag.block % NR_SLOTS].ready = true;
    return true;
}
static inline bool nr_may_sample(const nr_ring *r, nr_tag tag) {
    // Blocks 0 and 1 can retire in the preceding display frame. Stop here
    // until DMA entered the final block; issue drawing opportunity first.
    return tag.frame == r->frame || r->retired >= r->count - 1;
}
static inline bool nr_next_frame(nr_ring *r) {
    nr_tag first = {r->frame + 1u,0};
    if (r->retired != r->count || !nr_ready(r,first)) return false;
    r->frame = first.frame; r->retired = 0;
    return true;
}
