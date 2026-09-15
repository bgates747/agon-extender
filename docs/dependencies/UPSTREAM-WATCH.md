# Upstream watch and tagged-release integration

The authoritative import baseline is always an official tagged release under
ADR-0011. Moving branches, nightlies, issues, and pull requests are advisory
signals only; they never become build or qualification identities.

## Informational watch

Review upstream `main`, published nightly activity, release notes, open issues,
bug reports, and material pull-request discussion frequently enough that likely
porting changes remain small. Record the exact observed commit and upstream
issue or pull-request identifiers. Preserve concise maintainer rationale,
reported symptoms, rejected approaches, and expected behavior as review
context, clearly distinguished from source facts and project decisions.

An informational watch may prepare tests or flag a likely adapter change. It
must not update vendored source, the declared build profile, or a qualified
baseline.

## Tagged-release reconciliation

1. Establish a reviewed immutable source baseline for the new official tag and
   all resolved release dependencies.
2. Build and validate the old and new schema-2 graphs independently. Supply the
   old graph as the new generator's `--prior-graph`; every newly appearing file
   defaults to unresolved selection until explicitly reviewed.
3. Run `compare-tagged-releases.py` with the two graphs. Never compare against a
   moving checkout.
4. Dispose every Tier A item before accepting the new baseline. Review Tiers B,
   C, and D in order; no changed file may disappear from the report.
5. Refresh stale reviewed source spans, accepted selection mappings, adapters,
   tests, and documentation. Re-run graph validation and deterministic
   regeneration.
6. Import and qualify only after the tagged comparison is reviewed and the
   normal project gates are satisfied.

Attention tiers are:

- A — build/selection boundaries, new or removed files, public headers,
  licenses, unresolved changes, and stale reviewed evidence;
- B — selected target closure;
- C — excluded or unselected source connected to that closure; and
- D — isolated unselected content, still visible and reviewed.

Hash-equal moves are reported only as rename candidates. Identity continuity
requires Git or reviewed source evidence; the comparator does not invent it.

## Numeric adaptation gate

Every VDP import must follow [numeric-upstream-import-r01](../procedures/numeric-upstream-import-r01.md).
Run the numeric regression entry point and reconcile its bounded review
fingerprints, then perform fresh compiler-backed conversion enumeration and
target/hardware validation. Hash updates alone do not satisfy review.
