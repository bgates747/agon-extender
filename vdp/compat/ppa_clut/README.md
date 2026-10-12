# PPA CLUT compatibility component

RESEARCH-007's exact six-file upstream-derived backport, promoted for reusable
build integration. `backport.json` pins original/derived hashes and upstream
provenance; `clut-backport.patch` retains Espressif Apache-2.0 file licensing.
`scripts/p4_ppa_clut.py` generates a project-local driver component and two HAL
header overlays. The base ESP-IDF checkout remains read-only. Both consumer and
PPA component must place the overlay before stock HAL include paths. Selection
is explicit (`--indexed-ppa`); ordinary builds do not receive the override.

Frozen sample/benchmark evidence remains under docs/tasks/RESEARCH-007. The
compatibility files here are now maintained build inputs, not a separate SDK.
