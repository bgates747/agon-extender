# PPA CLUT compatibility component

RESEARCH-007's exact six-file upstream-derived backport, promoted for reusable
build integration. `backport.json` pins original/derived hashes and upstream
provenance; `clut-backport.patch` retains Espressif Apache-2.0 file licensing.
`scripts/p4_ppa_clut.py` generates project-local PPA driver and HAL components,
copying the selected SDK components and replacing only the six pinned files.
The base ESP-IDF checkout remains read-only. Overriding the owning HAL component
makes every consumer, including esp-dl, use the same type definitions. A PPA-only
include overlay proved insufficient: other components can select stock HAL first.
Selection is explicit (`--indexed-ppa`); ordinary builds receive no override.

Frozen sample/benchmark evidence remains under docs/tasks/RESEARCH-007. The
compatibility files here are now maintained build inputs, not a separate SDK.
