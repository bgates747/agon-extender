# Source and licensing record

This is an accepted local installation, not a public binary release or a claim that
all redistribution obligations have been discharged. Keep both runtime and
source/support archives. Public publication remains gated.

| Material | Selected notice/source retained |
|---|---|
| Extender maintained code and packaging | Repository GPLv3 LICENSE; source archives at exact P4/package commits |
| Agon VDP retained source | License and provenance under `vdp/vendor/agon-vdp-release` plus maintained derivative source |
| vdp-gl, ESP32Time and CRC | Their original vendored LICENSE files, source and notices remain in Extender source archive |
| EMOS and listener | agon-emos source archive, root MIT notice and per-file notices; original authorship retained |
| MOS build machinery and runtime | mos-agondev source archive, including nanoprintf and source-level notices; no top-level LICENSE found, so public redistribution of this support tree requires explicit rights review |
| ESP-IDF, Arduino-ESP32 and selected managed components | Exact installed source trees retained in `p4-dependencies.tar.gz`; `dependency-notices.json` indexes notice paths and hashes without flattening names |
| Compilers and host Python | Not distributed; versions/compiler hash/build inputs recorded, tools obtained separately |

The dependency source snapshot excludes Python caches, object files and symbolic
links; build recipes pin external packages rather than embedding toolchain
binaries. This local snapshot is not advertised as a complete GPL corresponding-
source offer for public distribution. Before public publication, resolve the MOS
builder licensing gap, review selected linked library obligations and supply any
missing corresponding-source/tool inputs. No ownership of third-party code is
claimed, and source headers remain unmodified by packaging.

The accepted local runtime firmware embeds the commissioned private reset
endpoint. Its plaintext configuration is kept outside tracked records. The
archive contains no accounts, credentials, sudo policy or full-device backup. Do not publish operator configuration,
full-device backups or debug ELFs/logs containing local build paths.
