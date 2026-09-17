# Codec-screen experimental frame boundary r01

This loopback-only experiment does not alter production EVF/EVR/EVS contracts.
A complete WebSocket binary message is a32-byte EVC1 header plus payload.
Little-endian fields: magic0:4, version4=1, header5=32, codec6 (0raw,1RLE2,
2direct szip,3SRLE2,4indexed PNG), reserved7=0, sequence8:u32,
width12:u16,height14:u16, raw pixels16:u32, payload bytes20:u32,
reserved24:u64=0. Maximum geometry512×384; maximum payload2MiB.
Decoded composed pixels are opaque RGB222 indices (00BBGGRR).
Szip payload uses retained CmpS framing; SRLE2 expands to a complete Cmpr file.
PNG is8-bit indexed, exact64-entry RGB palette, no colour-management chunks.

Client grants one `frame` credit after decode/presentation. Server enforces
at most30Hz when pacing is enabled; unpaced step tests measure decoder cost.
A Worker bounds decoding to2seconds and is replaced on rejection. Invalid
messages preserve the last presented frame. Unknown codecs/settings fail;
raw is always an available sender choice. Szip orders0/3/4/6 and record sizes
1–8 (optionally incremental) are experiment-only additions. Unchanged production
decoders still accept only their previously qualified subset.
