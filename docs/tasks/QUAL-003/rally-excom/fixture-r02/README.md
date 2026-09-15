# RXPROBE r02 — bitmap clip and triangle strip

Extends the frozen r01 probe with current Rally's RoadTop104 boundary, a solid
32x104RGBA8888 bitmap drawn directly at(-12,0) under viewport(0,24,319,103),
and Stream::quad's paired filled-triangle sequence with a negative left edge.
Four pages are drawn/swapped. Four fixed expected pixels per page test HUD and
bitmap clipping; thirteen pixels on road row210 per page are paired observations.
Expected999/999/999means compare Legacy to ExCom, not an expected physical colour.
The fixture terminal mismatch count alone does not assess these paired samples.

Use the same mode136/startup/deployment discipline as r01. Fresh CSV names are
required. Source, binary hashes and results remain separate from r01. No timing,
traffic, game loop or firmware alteration is included. Host build is only a
compile check; physical Legacy comparison is the reference validation.
