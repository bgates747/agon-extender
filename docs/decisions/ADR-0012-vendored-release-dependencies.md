# ADR-0012 — Vendor exact release dependencies for the VDP firmware

- Status: Accepted
- Completeness: Complete
- Date: 2026-08-20
- Related task: SETUP-003

## Context

The project effectively vendors the official VDP source because it must retain
a P4 compatibility delta and incorporate future upstream releases deliberately.
Official VDP `v2.16.0` also declares three source dependencies:

- AgonPlatform/vdp-gl tag `all-the-plots`;
- ESP32Time version range `^2.0.0`; and
- CRC version range `^1.0.3`.

The vdp-gl reference was initially mistaken for a moving branch because Git URL
fragment syntax can name either a branch or tag. Inspection of the official
remote refs established that `all-the-plots` is an immutable tag at
`ac2dd5986daf496c43ae8e7fe41836274aec54a0`.

The two PlatformIO version ranges can resolve to different releases over time.
Network resolution therefore cannot reproduce a build solely from the VDP tag.
Git submodules could pin source, but they add another checkout state, recursive
clone/update requirements, detached dependency worktrees, and avoidable agent
and contributor workflow complexity.

## Decision

1. Vendor the complete source required from vdp-gl, ESP32Time, and CRC in this
   repository. Do not use Git submodules for these dependencies.
2. Place third-party dependency trees under `vdp/vendor/`, separated by
   upstream project.
3. Select only an official immutable tag or published release for each
   dependency. Record its tag/version and immutable commit where the upstream
   uses Git.
4. For the `v2.16.0` baseline, use vdp-gl tag `all-the-plots` at
   `ac2dd5986daf496c43ae8e7fe41836274aec54a0`.
5. Resolve the exact official tagged versions of ESP32Time and CRC under
   SETUP-003 before importing them. Do not retain the compatible version ranges
   as active build inputs.
6. Record each dependency in project version metadata with:
   - upstream name and repository;
   - tag or published version;
   - immutable commit when applicable;
   - imported tree or package hash;
   - license and required notices;
   - associated official VDP release; and
   - complete local modification status.
7. Preserve vendored source structure, filenames, formatting, and license
   notices. Do not refactor vendored dependencies for local style.
8. Prefer project-owned adapters and wrappers over edits to vendored source.
   Any unavoidable vendored-source patch must be minimal, annotated, and
   represented in a mechanically auditable compatibility delta.
9. Configure PlatformIO to consume only the vendored copies for qualified and
   release builds. Such builds must not silently fetch or upgrade these
   dependencies from Git or a package registry.
10. Treat dependency updates as explicit reviewed changes tied to an official
    VDP baseline update or a separately justified dependency update. Never
    accept an incidental resolver upgrade.

## Rationale

1. A complete repository checkout is simpler and more reliable for humans,
   agents, automation, and archival recovery than a repository plus submodule
   state.
2. Exact vendored source makes builds independent of moving branches, changing
   package indexes, compatible-version resolution, and network availability.
3. Keeping third-party trees under one `vdp/vendor/` boundary avoids clutter at
   the project root and makes ownership obvious.
4. Immutable release identities and tree hashes integrate naturally with the
   artifact/version system established by SETUP-002.
5. Preserving dependency source unchanged supports license auditing and future
   comparison with upstream releases.

## Consequences

1. The Git repository will be larger and will contain third-party source.
2. License texts, notices, source availability obligations, and provenance
   records become part of every dependency import and update.
3. Updating a dependency requires an explicit source import, metadata update,
   compatibility-delta review, and build qualification.
4. PlatformIO configuration must prevent vendored libraries from competing with
   globally cached or remotely resolved copies.
5. Repository history will retain old dependency source, which is accepted in
   exchange for deterministic builds and a self-contained project checkout.
