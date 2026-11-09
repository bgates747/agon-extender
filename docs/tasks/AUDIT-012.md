# AUDIT-012 — Audit current candidates against pinned firmware defaults

## Executive summary

Smith directs an immediate compatibility audit of current test and production candidates against the selected VDPlet and MOS defaults. Freeze this task in Git and publish it before performing the audit. Record evidence and necessary exceptions without claiming that source inspection proves hardware qualification.

## Scope and direction

1. VDPlet v0.1.2-alpha is the default for testing and deployments on Alexe, Olimex and Console8. Use the release firmware and verify its SHA256SUMS; it includes the UART RX recovery fix.
2. Eirene MOS 3.1.0_uart0_rc_3 is the test default for Alexe and Console8: release ZIP `mos-rc3.bin`, 100879 bytes, SHA-256 `d7a51147f3381cd68d56f3fbe4605434a897dfae1b049269afeba09ec2b7eb50`.
3. Olimex uses the selected VDPlet release and latest approved integrated EMOS incorporating current Eirene enhancements; the Olimex scheduling agent maintains these defaults. Explicitly identify and justify necessary firmware exceptions in scheduling requests.
4. Existing test, deployment, physical custody and hardware permissions remain in force. This audit does not itself authorize new test scope, unsupported firmware changes, promotion or a bypass of existing stop boundaries.

## Work and evidence

1. [ ] Commit and push this task and its TODO entry before audit work, preserving unrelated work.
2. [ ] Inventory current test and production candidates across the affected owners and devices, including frozen plans and actual component requirements. Coordinate with owners through existing authorized channels; identify scope and source of each inventory.
3. [ ] Compare each candidate's required VDP, MOS/EMOS, APIs, modes, transport and device constraints to its applicable default. Verify relevant release artifacts and checksum evidence; classify each as evidence-supported compatible, incompatible, inherently different justified exception, or unknown/unqualified. Distinguish source/host evidence from physical qualification and installed identity from selected default.
4. [ ] Record an actor-explicit candidate table, evidence, material limitations and required owner actions. Preserve frozen test artifacts; identify necessary adaptations and explain each exception. Update affected current instructions or owner requests within ownership and authorization boundaries.
5. [ ] Record results and outstanding dependencies in the dated development log, notify relevant owners and keep unresolved items here until answered. Do not claim all candidates audited while any owner's inventory remains unknown.

## Dependencies and boundaries

VDPlet release: https://github.com/bgates747/agon-vdplet/releases/tag/v0.1.2-alpha. Eirene release: https://github.com/bgates747/eirene-mos/releases/tag/3.1.0_uart0_rc_3. Olimex selection and retained EMOS inventory are in `docs/olimex-firmware-standard.json` and `docs/olimex-emos-functions.md`; complete Extender production selection remains `production/current.yaml`. No test, flash, reset or production promotion follows merely from an audit finding. Preserve all prior evidence and unrelated uncommitted work.
