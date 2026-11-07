"""Read the actual AgonDev linker map; this binary wrapper emits no ELF.

Keep the witness and all static application storage inside the selected SAVE
window. This is a linked layout check, not a measured stack or IRQ claim.
"""
import re


def layout(text):
    def one(pattern):
        found = re.findall(pattern, text, re.MULTILINE)
        if len(found) != 1:
            raise ValueError('Missing or ambiguous native map symbol')
        return int(found[0], 16)

    witness = one(r'^\s+0x([0-9a-fA-F]+)\s+_async_witness\s*$')
    bss_end = one(r'^\s+0x([0-9a-fA-F]+)\s+bss_end = \.\s*$')
    stack = one(r'^\s+0x([0-9a-fA-F]+)\s+__stack = .*\s*$')
    # Native ABI packs this retained witness to 32 bytes: seven uint32_t and
    # four uint8_t fields. The checked source is frozen with the actual map.
    if not (0x40000 <= witness and witness + 32 <= bss_end <= 0x50000 < stack):
        raise ValueError('Native static storage exceeds the 64 KiB SAVE window')
    return dict(witness=witness, witness_bytes=32, bss_end=bss_end,
                stack_origin=stack, measured_stack_peak=False)
