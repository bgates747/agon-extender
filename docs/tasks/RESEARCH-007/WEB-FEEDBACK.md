# User-relayed web-agent feedback — indexed framebuffer

Received 2026-10-09. Source: Author pasted feedback from another web-based agent;
no independent source links or measurements supplied. Preserved as a research
lead, not an authoritative hardware description. The pasted memory table's
broken formatting is normalized below; the proposal is otherwise retained.

> Oh, bollocks indeed. We may have spent considerable effort optimizing something that could have remained one byte per pixel all along.
>
> And yes, 8-bit indexed color could be an excellent internal framebuffer format for Extender.
>
> You'd have three palette configurations:
>
> - Agon 16: Original 16-color palette, indices 0–15.
> - Agon 64: Original 64-color palette, indices 0–63.
> - Custom 256: All 256 indices available, with programmable RGB values.
>
> The important distinction is that palette size and framebuffer bit depth needn't be the same thing. All three can use an 8-bit framebuffer, even when only 16 or 64 colors are available.
>
> At 320×240:
>
> | Format | Framebuffer |
> |---|---:|
> | RGB888 | 225 KiB|
> | RGB565 | 150 KiB|
> | Indexed 8-bit | 75 KiB|
>
> And palette animation becomes wonderfully cheap. Change the CLUT rather than rewriting thousands of pixels.
>
> There's one architectural detail I'd have Codex investigate before changing anything: whether the PPA can efficiently expand L8 to RGB565 as part of the existing rendering pipeline, or whether it introduces an additional full-frame conversion pass.
>
> If the PPA conversion proves expensive, a CPU lookup table remains an option.
>
> I'd also preserve the existing Agon VDU semantics. The internal representation can change without applications knowing anything about it, provided color selection, plotting, transparency and palette commands retain their expected behavior.
>
> One caveat: an 8-bit indexed framebuffer cannot represent every existing true-color Agon graphics operation without quantization or a separate true-color path. I'd retain RGB888 or RGB565 as an optional mode rather than eliminate them.
>
> But for the original Agon 16- and64-color modes? This sounds like a very natural fit.
>
> And it raises a tantalizing possibility: send the indexed framebuffer directly to the Pico 2 and perform palette expansion there. That halves the P4-to-Pico bandwidth compared with RGB565, while avoiding the PPA conversion entirely.
>
> The Pico's HSTX output still needs appropriately encoded pixel data, but a 256-entry RGB lookup table is trivial for the RP2350.
>
> That might be the biggest win of the entire exercise.

See [RESEARCH-007](../RESEARCH-007.md) for the bounded investigation and gates.
