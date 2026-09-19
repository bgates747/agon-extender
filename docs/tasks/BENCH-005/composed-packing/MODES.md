# Non-50-Hz mode inventory

Source: official Agon Screen-Modes.md, cross-check installed agon_screen.h. Listed support is not a new hardware qualification. Mode7 is special teletext.

| Mode | Pixels | Colours | Hz | Double buffered | RGB222 bytes |
|---:|---|---:|---:|---|---:|
| 0 | 640×480 | 16 | 60 | False | 307200 |
| 1 | 640×480 | 4 | 60 | False | 307200 |
| 2 | 640×480 | 2 | 60 | False | 307200 |
| 3 | 640×240 | 64 | 60 | False | 153600 |
| 4 | 640×240 | 16 | 60 | False | 153600 |
| 5 | 640×240 | 4 | 60 | False | 153600 |
| 6 | 640×240 | 2 | 60 | False | 153600 |
| 7 | 640×480 | 16 | 60 | False | 307200 |
| 8 | 320×240 | 64 | 60 | False | 76800 |
| 9 | 320×240 | 16 | 60 | False | 76800 |
| 10 | 320×240 | 4 | 60 | False | 76800 |
| 11 | 320×240 | 2 | 60 | False | 76800 |
| 12 | 320×200 | 64 | 70 | False | 64000 |
| 13 | 320×200 | 16 | 70 | False | 64000 |
| 14 | 320×200 | 4 | 70 | False | 64000 |
| 15 | 320×200 | 2 | 70 | False | 64000 |
| 16 | 800×600 | 4 | 60 | False | 480000 |
| 17 | 800×600 | 2 | 60 | False | 480000 |
| 18 | 1024×768 | 2 | 60 | False | 786432 |
| 19 | 1024×768 | 4 | 60 | False | 786432 |
| 20 | 512×384 | 64 | 60 | False | 196608 |
| 21 | 512×384 | 16 | 60 | False | 196608 |
| 22 | 512×384 | 4 | 60 | False | 196608 |
| 23 | 512×384 | 2 | 60 | False | 196608 |
| 24 | 640×512 | 16 | 60 | False | 327680 |
| 25 | 640×512 | 4 | 60 | False | 327680 |
| 26 | 640×512 | 2 | 60 | False | 327680 |
| 27 | 640×256 | 64 | 60 | False | 163840 |
| 28 | 640×256 | 16 | 60 | False | 163840 |
| 29 | 640×256 | 4 | 60 | False | 163840 |
| 30 | 640×256 | 2 | 60 | False | 163840 |
| 129 | 640×480 | 4 | 60 | True | 307200 |
| 130 | 640×480 | 2 | 60 | True | 307200 |
| 132 | 640×240 | 16 | 60 | True | 153600 |
| 133 | 640×240 | 4 | 60 | True | 153600 |
| 134 | 640×240 | 2 | 60 | True | 153600 |
| 136 | 320×240 | 64 | 60 | True | 76800 |
| 137 | 320×240 | 16 | 60 | True | 76800 |
| 138 | 320×240 | 4 | 60 | True | 76800 |
| 139 | 320×240 | 2 | 60 | True | 76800 |
| 140 | 320×200 | 64 | 70 | True | 64000 |
| 141 | 320×200 | 16 | 70 | True | 64000 |
| 142 | 320×200 | 4 | 70 | True | 64000 |
| 143 | 320×200 | 2 | 70 | True | 64000 |
| 145 | 800×600 | 2 | 60 | True | 480000 |
| 146 | 1024×768 | 2 | 60 | True | 786432 |
| 149 | 512×384 | 16 | 60 | True | 196608 |
| 150 | 512×384 | 4 | 60 | True | 196608 |
| 151 | 512×384 | 2 | 60 | True | 196608 |
| 153 | 640×512 | 4 | 60 | True | 327680 |
| 154 | 640×512 | 2 | 60 | True | 327680 |
| 156 | 640×256 | 16 | 60 | True | 163840 |
| 157 | 640×256 | 4 | 60 | True | 163840 |
| 158 | 640×256 | 2 | 60 | True | 163840 |

Historical numbering aliases (VDU23,0,193; unrelated to EMOS Legacy routing): 0→1024×768×2 at60Hz; 1→512×384×16 at60Hz; 2→320×200×64 at75Hz; 3→640×480×16 at60Hz. No extra raster geometry/depth; alias2 has separate timing. No 50Hz modes occur in this installed switch.

All frames are composed first. Palette cardinality after composition determines packing eligibility, not this nominal Colours column. Browser request cap remains60 even for70/75Hz sources.
