# Light 2 harness r02 test sheets and results

**On hold — incomplete (Author direction, 2026-09-07).** The present
hardware design, construction, and testing are paused pending review of stock
MOS/VDP communications and interface requirements. Full wiring of the r02
circuit as drawn is incomplete, and the complete circuit has not been tested.
The September 4 power-domain observations retain only their recorded scope.
The frozen candidate identity preserves the design checkpoint; it does not
claim design completion, complete assembly, or qualification. Earlier stage
instructions below are retained references and do not authorize further work.

This directory is the home for human construction test sheets and their
results for the [powered wiring order](../README.md), beside the
[circuit design](../../README.md). Task documents link here for the
measurements; they retain work tracking, decisions, review gates, and findings.

| Stage | Test sheet or result | Status |
| --- | --- | --- |
| 01 — Power domains | [2026-09-04 results](01-power-domains-results-2026-09-04.md) | Preliminary unpowered, single-domain, and dual-powered observations; not qualified |
| 02 — Startup and fail-safe bias | [Test sheet](02-startup-and-fail-safe-bias-network.md) | On hold; superseded draft with rejected resistor proposal; measurements blank |

Use the [result template](RESULT-TEMPLATE.md) for later lane and component
checks. Stage 01 retains its original r02 circuit identity; moving its result
does not make it a test of the proposed permanent additions.

## Keeping records

1. Identify the wiring-order step, accepted circuit revision, reference signal
   view, and cumulative wiring actually
   installed. Record omitted connections, permanent added parts, instruments,
   firmware, power sources, and cable state with the readings. A drawing alone
   is not an as-built record.
2. Keep the reusable sheet separate from each completed result. For a new
   controlled run, use its actual run ID in the result filename; link its
   manifest and raw evidence at the canonical repository-root
   `tests/runs/<RUN-ID>/` location. This directory does not replace that
   [version-policy evidence location](../../../../../docs/versions/README.md).
3. For exploratory observations without complete run provenance, preserve the
   actual date, source, and limitations. The stage-01 file retains historical
   evidence without inventing a compliant run ID. Do not overwrite an earlier
   result on a rerun; append dated corrections when necessary.
4. Draft sheets have no approved procedure identity. The Author approves the
   identity, revision, and applicable physical scope before a controlled run;
   qualified runs require clean committed inputs. Creating a sheet or moving
   a result does not change its approval or qualification status.

The [staged validation process](../../../../../docs/qualification/staged-circuit-validation.md)
governs this work. [HW-001](../../../../../docs/tasks/HW-001.md) owns construction
and input-state sufficiency; [QUAL-002](../../../../../docs/tasks/QUAL-002.md) owns
electrical review and evidence disposition; [PORT-008](../../../../../docs/tasks/PORT-008.md)
consumes the results when selecting the next transport component test.
