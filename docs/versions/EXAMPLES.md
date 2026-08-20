# Versioning Examples

These examples are normative demonstrations of the rules in
[`README.md`](README.md). Hashes are shortened only in explanatory prose; real
manifests contain complete SHA-256 values.

## 1. Initial canary

The first SETUP-001 test program is an experimental artifact, not production
firmware. It predates the policy, so only its source identity is assigned
retrospectively:

```text
source identity: setup-001-canary-r01
build ID:        null (pre-policy; exact creation instant was not recorded)
run ID:          null (pre-policy; exact start instant was not recorded)
status:          rejected
```

The run found that the CPU remained at 360 MHz and therefore rejected `r01`.
The corrected source will be `setup-001-canary-r02`, not a rebuild falsely
carrying `r01`. A future correctly identified example would be:

```text
build ID: setup-001-canary-r02-b2026-08-21-14-03-07Z
run ID:   SETUP-001-2026-08-21-14-12-41Z
```

Those timestamps illustrate syntax only and do not claim that the future build
or run exists.

## 2. Wiring revision

Suppose `light2-harness-r01` assigns the eight data lines correctly but a
strobe wire is later moved to a different GPIO. The corrected harness is:

```text
light2-harness-r02
```

This is a revision because it changes a controlled physical connection. It is
not `v1.0.1`, and `console8-harness-r01` does not change: Console8 is a parallel
variant with its own lineage. A compatibility declaration lists each accepted
harness explicitly:

```yaml
requires:
  - artifact_id: light2-harness
    one_of:
      - light2-harness-r02
    variant: light2
    reason: Strobe must use the board profile's corrected GPIO.
```

## 3. Backward-compatible protocol extension

`forward-parallel-transport-v1.2.0` adds an optional capability query while
retaining every `v1.1.0` operation and encoding. This is a minor increment.
A compatible consumer can declare:

```yaml
requires:
  - artifact_id: forward-parallel-transport
    version_range:
      minimum: v1.1.0
      before: v2.0.0
    reason: Requires the v1 framing and accepts optional later v1 capabilities.
```

A bug correction that changes no command or encoding would instead produce
`v1.2.1`.

## 4. Incompatible protocol change

Changing the strobe polarity and packet framing would require existing senders
or receivers to change. The protocol becomes:

```text
forward-parallel-transport-v2.0.0
```

Its manifest declares the new electrical profile and does not claim v1
compatibility. Tests against a v1-only consumer are recorded under
`known_incompatible`; untested consumers remain `unqualified`.

## 5. Released firmware build

A release may look like:

```text
source identity: extender-vdp-v1.3.0
build ID:        extender-vdp-v1.3.0-b2027-02-14-16-30-05Z
filename:        extender-vdp-v1.3.0-b2027-02-14-16-30-05Z.bin
status:          released
```

The adjacent build manifest records the complete source commit, clean/dirty
state, toolchain, board profile, partition layout, compatibility requirements,
file size, and SHA-256. The firmware reports the same build ID through startup
and machine-readable diagnostics. A second binary from changed source or tools
receives a new build ID even if the source version remains `v1.3.0`.

## 6. Baseline and run convergence

An approved combination can be named `p4-light2-bringup-r01`. Its baseline
manifest might select:

```yaml
artifacts:
  - artifact_id: extender-vdp
    identity: extender-vdp-v0.4.0
    build_id: extender-vdp-v0.4.0-b2026-10-03-14-20-11Z
    variant: olimex-p4-devkit
  - artifact_id: light2-harness
    identity: light2-harness-r02
    build_id: null
    variant: light2
  - artifact_id: olimex-p4-devkit-profile
    identity: olimex-p4-devkit-profile-r03
    build_id: null
    variant: rev-d1-pre-v3
```

A qualification run references that baseline and adds specimen aliases,
instrument settings, exact MOS/VDP dependencies, observations, and evidence.
The private mapping from a specimen alias to a serial number or network address
stays in the ignored bench record.
