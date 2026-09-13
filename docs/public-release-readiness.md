# Public repository readiness

Reviewed 2026-09-13 at `5ad7a73`, including the pending license rename and
`social-preview.png`. This is a publication-readiness review, not a general
firmware or hardware qualification. The review itself changed no visibility
settings. Later on the same date, the Author explicitly directed publication;
both firmware repositories are now public. The Author subsequently approved
committing and pushing the reviewed publication material.

## Findings

### 1. Required EMOS source availability — resolved

The README requires EMOS for all supported operation. An unauthenticated
request to `https://api.github.com/repos/bgates747/agon-emos` returned 404.
The same check returned public metadata for `mos-agondev` and `agon-utils`.
A 404 does not distinguish a private repository from an absent or renamed one.

Subsequent authenticated check on 2026-09-13 confirmed that
`bgates747/agon-emos` exists, uses branch `main`, and is **private**. Its origin
matches that URL. The community guide now identifies this access limit and
distinguishes the public EDP source under Extender's `vdp/` from the separate
EMOS source. The Author subsequently directed making EMOS public; the GitHub
visibility change succeeded and was independently verified without authentication.
Both firmware repositories are now public, and the community guide links them.

The source-access issue is resolved. A reproducible setup still needs the
compatible revisions and complete build instructions described below.

### 2. The public setup path is incomplete

The README has no end-to-end developer setup/build instructions.
`scripts/vdp-pio.sh` requires `.venv/bin/pio`, but `requirements-dev.txt` does
not install PlatformIO. The current SD guide refers readers to local bench
and environment guidance; its linked commissioning document records a specific
operator's card handover, rollback payloads, and Pi flashing workflow.
Those records are useful provenance but are not a newcomer installation guide.

Document prerequisites, a tested PlatformIO version, Python setup, the correct
firmware environment, companion revisions, wiring, build outputs, installation,
and recovery. Explain that `p4-canary` is the PlatformIO default while the
accepted console uses `p4-console`. Candidate preparation also requires clean
committed inputs (`scripts/prepare_console.py`). Validate the resulting guide
in a clean checkout before describing it as reproducible.

### 3. Network trust requirements are too far from the SD startup instructions

`docs/mainboard-sd.md` starts the service with `RUN . /`, granting whole-card
scope. `sdRpcHandler` in
`vdp/video/extender/network/wired_network_service.cpp` receives unauthenticated
plain-HTTP requests. The guide correctly says the session identifier is not
authentication, but the explicit trusted-LAN/TLS limitation is in the browser
asset README (`vdp/video/extender/web/README.md`).

Put the trusted-network requirement and unauthenticated read/write scope beside
the public startup example. Explain how to select a restricted directory.
This is a documentation finding about the existing development interface;
publishing source does not itself expose a running device.

### 4. Two existing checks fail

- `scripts/validate-version-records.py` fails on
  `hardware/designs/light2-harness-r02/profile.yaml:12`: expected connectivity
  SHA-256 `560ab589c9f0bbf63ecc17e747eff15208fb672723489c3b4755d7d9fea6b79c`,
  actual `c68e4d4ffa2211cb18d3d558b3c88393cb1583d431e9258b6e78e7a10a6eda6f`.
  Investigate the frozen record's history and intended authority before
  changing a hash. This failure stops that validator, so subsequent records
  have not all been validated by this run.
- `python3 tests/browser_network_containment_test.py` fails with macOS Clang:
  the unconditional `HTTP_POST` test constant at line 29 is unused in the
  non-SD configuration, and `-Werror` promotes that warning to an error.
  Scope the constant to the configuration that uses it, then rerun both cases.

These are reproducibility/integrity issues, not evidence from this review of a
runtime firmware failure.

### 5. Capability wording needs qualification

README's “Core Functionality” section promises initial network audio and gives
parallel throughput figures. `TODO.md` explicitly defers PORT-004 audio and
holds wider PORT-008 parallel/hardware qualification. The README already calls
the project experimental and distinguishes scoped SD acceptance from release;
make that distinction equally clear beside individual capability claims.
Label future audio and the scope/provenance of measured parallel performance.

### 6. Social-image upload export — prepared locally

The original `social-preview.png` is preserved unchanged in the root:
1536 × 1024 pixels, 2,008,452 bytes. GitHub requires a social-preview upload
under 1 MB and recommends 1280 × 640 pixels. The subsequently prepared
`social-preview-upload.png` is 1280 × 640 and 880,042 bytes. It mechanically
scales the original to 960 × 640 and adds 160-pixel black side bars, preserving
the whole composition without cropping or stretching. The original is unchanged.
The file must also be selected in repository Settings → Social preview;
committing it alone does not configure the preview.

Source: [GitHub social-preview documentation](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/customizing-your-repositorys-social-media-preview).

## Security and privacy checks

Gitleaks 8.30.1 was downloaded from its official GitHub release and verified
against that release's checksum file. Default rules were used without a custom
allowlist, with redacted reports stored outside the repository.

- `gitleaks git --log-opts=--all .`: scanner reported 180 commits examined,
  approximately 212 MB scanned, and 44 findings. The non-shallow local repository
  has 181 reachable commits; the scanner's reported count is recorded as-is.
- `gitleaks dir .`: approximately 154 MB scanned and 44 findings.
- Every finding was inspected against its source line (using its recorded
  commit for history findings). All were file SHA-256 values with key/API-like
  filenames or generated graph edge identifiers involving keyboard symbols.
  No confirmed credential was found. No broad suppression was added.
- A tracked-text scan found no RFC1918 IPv4 addresses or credential assignments
  matching the reviewed patterns. The two files containing `/Users/` or
  `/home/` paths are unchanged vendored vdp-gl documentation/tool instructions.
- Reachable history contains one author identity using a personal Gmail address.
  Publishing history exposes that address. Development and commissioning notes
  also preserve operator dialogue and bench history.
- An additional scan of 7,651 historical text blobs found the same two
  vendored local-path files and one historical private-IP match in
  `tests/browser_network_containment_test.py`. Inspection at `5e8ebf5` shows
  simulated network addresses in an origin-admission test; that code was later
  removed. No other historical text files matched these path/IP patterns.

Secret scanners do not prove the absence of every secret. This review did not
visually inspect all 458 tracked PNG/JPEG/WebP files, the schematic PDF, or
binary captures. Remote-only refs and unreachable Git objects were not audited.

## Licensing and checks that passed

- Root `LICENSE` matches the existing complete vendored GPLv3 text byte-for-byte.
  `LICENSING.md` preserves the original GPL-3.0-only policy and attribution rules.
- License files are present for agon-vdp (MIT), CRC (MIT), ESP32Time (MIT),
  vdp-gl (GPLv3), and the Nurples include snapshot (Unlicense).
- Sampled FabGL-derived scanline files retain upstream notices. The 15 files
  in the Nurples snapshot manifest all match their recorded SHA-256 values.
  This is a notice/inventory check, not exhaustive license clearance for every
  font, asset, generated file, or downloaded build dependency.
- `python3 -m unittest discover -s tests -p 'test_sd*.py'`: 10 tests passed,
  including native SD service/client checks.
- `scripts/validate-hardware-objects.py`: passed, 41 objects.
- Validators used an isolated temporary environment with the repository's
  pinned PyYAML 6.0.3 and jsonschema 4.25.1. System Python initially lacked YAML.
- Local Markdown destination checks passed for README, OWNERSHIP, LICENSING,
  the SD operating guide, and this review (anchors/external links excluded).

## Publication decision

The scan found no confirmed credential requiring rotation or history removal.
Address the findings above before announcing a reproducible release; source
publication can still be explicitly presented as experimental development.
A contribution guide and private security-reporting channel would also help
outside users. No full firmware build, installation, hardware test, history
rewrite, commit, push, or publication was performed during this review.

Subsequent Author-directed action: GitHub visibility was changed to public and
verified through the unauthenticated API. See [TRS-80-002](tasks/TRS-80-002.md)
for the community guide, sample kits and image export approved for publication.
