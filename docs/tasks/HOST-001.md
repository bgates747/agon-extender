# HOST-001 — New Oryx Pro Linux Lite migration

## Executive summary

Prepare replacement of Pop!_OS on the Author's **new Oryx Pro**, with Linux Lite
as the preferred distribution and as much installation work as practical managed
remotely by the agent. Earlier Ubuntu, Xubuntu, Linux Lite and other attempts
failed according to the Author; their causes have not yet been established.
Recover the relevant history before choosing another installation approach.

**State, 2026-10-09:** all 295 printed conversation pages reviewed; a private
précis records attempts, observed failures, advice without confirmed results and
source gaps. History review is complete within the printed source's limits.
The Author proposed dual boot, confirmed one SSD and authorized read-only SSH
inventory with a running action/result log. H03 is complete: the current layout
has no useful unallocated extent; existing root is unencrypted ext4. The private
inventory records current graphics, boot, storage and service evidence and its
limits. Original PDF bytes remain unchanged. The Author accepted an approximately equal ~1 TB per-OS budget after cleanup.
A private phased dual-boot plan now records sizes and planned verified home migration, a Lite-only swap file,
preservation, live access, offline resize and validation. Preservation and
installer/recovery preparation remain pending. No partition, boot configuration,
driver or OS change and no reboot occurred. An executable installation plan,
preservation requirements and
the Author's installation authorization are still required before changing the
host's operating system, partitions or boot configuration.

## Scope and ownership

1. The target is the new Oryx Pro, called the Pop!_OS box in this conversation.
   The old Oryx Pro and the Lenovo are separate machines. Do not transfer their
   graphics, boot or recovery findings to this target without independent proof.
2. Extender owns this task's work record and its development-host requirements.
   Reusable host/environment tools and accepted cross-project setup guidance
   remain owned by `agon-dev-env`; task-local prototypes may stay in the work
   directory during discovery. Do not duplicate canonical SSH configuration.
3. The agent prepares evidence, inventories, migration options and validation.
   The Author selects material installation and preservation decisions and
   supplies any necessary physical boot or recovery intervention. Identify the
   control host, target host, transport and recovery operator in the eventual
   installation plan; their exact mappings belong in the private records.
4. This task does not authorize Agon/P4 firmware changes, physical bench work,
   changes to another workstation, or public distribution of account exports.
5. Maintain a running chronological log of actions and their results at
   `HOST-001/private/RUNNING-LOG.md`, as requested on 2026-10-09. Retain exact
   read-only SSH scripts, output, per-probe statuses and hashed receipts in the
   private inventory; summarize sanitized milestones in the development log.

## Authorities and work location

1. [Canonical Codex instructions](../../../agon-dev-env/codex/AGENTS.md),
   [environment](../../../agon-dev-env/codex/environment.md) and
   [documentation conventions](../../../agon-dev-env/codex/documentation.md)
   govern host access, interpreter selection and reusable-tool ownership.
   Resolve the machine-local connection guide from the environment document.
2. [Task-directory conventions](README.md) govern this bounded work silo.
   [TODO](../../TODO.md) is the sole authoritative unfinished-work index.
3. [Work directory](HOST-001/README.md) indexes research, provisional tools and
   reviewed evidence. `HOST-001/private/` is ignored by Git and holds account
   exports, extracted transcripts, machine inventories and local receipts.
   Redact evidence deliberately before putting it in tracked files.
4. Preserve source exports unchanged and record their hashes when obtained.
   Extraction must preserve conversation/message identities and distinguish
   the displayed branch from alternate responses or edited-message branches.

## Initial evidence and limits

| Evidence | What it establishes | Limit |
|---|---|---|
| Author's current request | Linux Lite is preferred for the new Oryx Pro; previous distribution attempts failed | Current machine state and failure mechanisms remain unverified |
| Correct target's linked ChatGPT conversation | Author identifies it as the new Oryx Pro's installation history | The app reader returned only five recent exchanges, `hasMore: false` and no older-page cursor |
| Retrieved user report | A prior configuration failed while Kerbal launched during multitasking; the Author then intended to try Xubuntu | No recovered crash log or complete configuration identifies the cause |
| Shared conversation link | An additional history source was provided | Web retrieval failed; full conversation not recovered |
| Author-supplied printed conversation PDF | All 295 pages reviewed; private précis reconciles January installation attempts and outcomes | Collapsed installation output and an unavailable screenshot limit reconstruction; no alternate branches or subsequent Xubuntu/Pop!_OS outcome |
| Historical command output | Identifies laptop model and both GPUs; records NVIDIA failures despite loaded modules and a working AMD desktop on one distribution | Historical inventory only; not a current hardware/software verification or confirmed root cause |
| Current authorized SSH inventory | Single SSD; unencrypted ext4 root; no useful unallocated extent; NVIDIA currently enumerates with the open driver; boot/services/network captured | No offline consistency/shrink check, game/offload validation, recovery reboot or backup/restore check; exact details and exceptions remain private |

Earlier assistant diagnoses about PRIME, Wayland, NVIDIA, firmware, display
wiring or platform support are hypotheses until checked against this machine's
identity, official sources and retained diagnostics. A linked conversation's
title alone is not proof of hardware identity or a successful remedy.

## Research sources

1. Author-supplied [community export/extraction guide](https://community.openai.com/t/how-to-download-all-of-your-chatgpt-chats-and-extract-an-individual-chat-by-name-as-an-html-document/1394982),
   read 2026-10-09: describes requesting the account export, then using a
   standard-library Python script to select a conversation by title from its
   ZIP and produce HTML. The supplied script is a candidate, not an executed
   or validated project tool. Review branch selection, duplicate titles,
   attachments and output handling before reuse.
2. [Linux Lite installation manual](https://www.linuxliteos.com/manual/install.html):
   starting reference for live-media installation. Verify the selected release's
   current requirements, checksum and installer behavior when planning begins.
3. [OpenAI browser documentation](https://learn.chatgpt.com/docs/browser) and
   [browser integration](https://learn.chatgpt.com/docs/chrome-extension): possible
   history-reading alternatives. Documentation does not establish a working
   connection in this session. The built-in-browser request returned queued;
   no complete transcript was read through it.
4. Exact private conversation links and the target/old-machine distinction are
   recorded in `HOST-001/private/CONTEXT.md`, outside Git.

## Work plan

### H01 [x] Establish the task and work directory

Read the ten canonical `codex/` Markdown files and the applicable Extender
instructions, handbook and task conventions. Register this task in TODO,
create its work directory and private-data exclusion, and log the setup.

### H02 [x] Recover and reconcile the installation history

Completed 2026-10-09 against all 295 pages of the Author-supplied PDF. The private
`HOST-001/private/PRECIS.md` records the chronology with PDF page references,
confirmed observations, unverified advice and missing outcomes. The original PDF
and extracts remain ignored. This completion covers the visible printed source;
it does not assert complete attachments, expanded messages or alternate branches.
The Author initially requested a stop after the précis, then resumed discussion
and separately authorized H03. H04/H05 preparation subsequently began under further Author instructions;
no installation operation is implied by completing the history review.

The agent obtains the correct conversation's available text using an admitted
reader or an Author-provided account export. Inspect an export locally and
extract only the selected conversation rather than copying unrelated history
into tracked files. Match the known conversation ID as well as its title when
possible; do not silently pick the newest duplicate title. Record missing
messages and inaccessible attachments. Prepare a concise chronology separating
the Author's observations, command output, assistant proposals and confirmed
outcomes. Keep old Oryx Pro and Lenovo evidence separate.

### H03 [x] Verify the current target and its dependencies

Completed 2026-10-09 through authorized read-only SSH. The private
`HOST-001/private/inventory/SUMMARY.md` links retained commands, transcripts and
hashed receipts. Inventory covers machine/CPU/RAM, OS/kernel/current graphics,
boot/firmware, SSD partitions/encryption/capacity/health, networking/SSH,
connected displays, running services and shallow dependency directories.
Recorded a boot-default discrepancy and diagnostic exceptions without fixing
them. No gaming/offload or external-display test, reboot, offline filesystem
check, shrink estimate or persistent configuration change. Detailed repository
preservation and backup/restore verification remain H04.

After reading the canonical local connection guide and coordinating existing
host activity, the agent inventories the target through read-only access.
Record model/generation, CPU and both graphics devices if present, installed
OS/kernel/drivers, firmware/boot mode, storage/encryption, network interface,
display connections and workloads/services. Store unique identifiers and exact
network/filesystem mappings privately. Reconcile maintained environment records
and any already active migration/recovery work before proposing changes.

### H04 [ ] Prepare preservation and recovery

Planning checkpoint: Author accepted approximately equal ~1 TB per OS.
`HOST-001/private/DUAL-BOOT-PLAN.md` records the phased execution proposal,
capacity arithmetic, preservation/control gates and both-OS validation. Backup
destination and coverage remain pending; no resize or reboot performed.

The agent inventories data, repositories including uncommitted/untracked work,
application state, services, SSH configuration and restore dependencies. The
Author selects what must survive. Prepare backup verification and a practical
restore check; identify the target disk unambiguously in the private plan.
Record how the Author or an independent console can recover a failed boot or
lost network connection before proposing unattended execution.

### H05 [ ] Select a supported candidate and remote installation method

Media discovery, 2026-10-09: Author attached an existing multiboot USB; read-only
SSH inspection recorded device/mount identity, installer filenames and capacity
in `HOST-001/private/inventory/USB.md`. The Author subsequently selected Linux Lite 8.0 Final for evaluation and authorized
media preparation. The ISO was downloaded, matched against its official SHA-256,
copied onto the USB, flushed and verified; existing installers were preserved.
USB bootability and older image checksums remain unverified. This is preparation
evidence, not H05 completion or permission to install.

The agent reviews current System76, graphics-vendor and Linux Lite sources
against H02/H03, then presents the next unresolved decision with a recommendation
and tradeoffs. Compare live USB with prepared remote access, network boot, and
an independent remote console only where the hardware supports them. Verify
installer-side network/control access rather than assuming the existing
Pop!_OS SSH session survives reboot. Pin the selected ISO and checksum before
writing media. Define required physical assistance and rollback steps.

### H05-P — Authorized preparation while archive transfer runs

Author authorized these preparation steps on 2026-10-10. Maintain live transfer
and paused loose-file backup; no reboot, resize or installer execution.

1. [x] Capture current GPT geometry/raw backup, EFI files, firmware boot entries,
   Pop mount/boot/service configuration and package inventory into protected
   private recovery evidence on the control host. Hash the retained bundle.
2. [x] Inspect the verified ISO read-only: Calamares manual partitioning,
   EFI/bootloader paths, installed tools and published prelaunch workaround.
3. [x] Prepare a manually invoked live-only SSH helper and administrator public
   key on Ventoy, with recorded fingerprints and reconnect instructions. Test
   syntax and deployed hashes; runtime verification waits for actual live boot.
4. [x] Record the proposed equal split with byte/MiB units, unchanged partition
   starts and preservation rules; final geometry/feasibility waits for live boot.
5. [x] Record account UID/GID, data/profile/Steam locations and selective restore
   instructions; retain complete home archive and require verification before
   filesystem changes. Do not claim a prepared helper is tested live access.

Preparation completed 2026-10-10; private `HOST-001/private/prep/PREPARATION.md`
and `receipt.json` retain findings and hashes. Both scripts were syntax checked
and deployed hashes verified. Runtime live access, archive completion/sample
restore, offline resize and installer preview remain pending. No reboot,
installer launch or partition changes.

### H06 [ ] Execute the reviewed installation and validate

After the Author authorizes the concrete plan and H04/H05 are satisfied, the
agent and Author perform their named steps. Retain receipts for media identity,
disk selection, installation, boot, drivers and restored access. Validate XFCE
desktop operation, display layout, networking/SSH, required applications and
the prior reproducible failure triggers. The Author validates interactive
behavior. Treat boot success as one gate, not full workload acceptance.

### H07 [ ] Close out accepted operation

After Author acceptance, update maintained host guidance in its owning
repository, retain bounded evidence and recovery information, and resolve the
TODO item through the dated development log. Promote recurring tools out of
this task silo. Extender firmware production bundles and versions are not
changed merely by replacing a host operating system.

## Decision register

| ID | State / recommendation | Alternatives and tradeoffs | Prerequisites / downstream effect |
|---|---|---|---|
| H-D01 — Distribution/release | Author selected Linux Lite 8.0 Final (Ubuntu 26.04) for evaluation and authorized its placement on Ventoy; verified media prepared | Lite 8.2 RC1 is an optional later live comparison; Xubuntu 26.04 remains an XFCE alternative. No hardware success inferred from release labels | Official NVIDIA guidance requires open modules for the target GPU; verify actual ISO/kernel/driver and review installer issues. Private RELEASE-RESEARCH.md records sources; verified USB receipt retained; installation remains pending |
| H-D02 — Installation/control path | Unresolved. Recommend live USB plus verified installer-side remote access if supported | Network boot adds infrastructure; independent remote console requires suitable hardware; each changes local assistance and recovery needs | H03/H04 establish network and physical recovery; decides which steps the agent can perform remotely |
| H-D03 — Preservation/disk layout | Author proposed dual boot and confirmed one SSD; inventory confirms a shared-disk layout is required for that approach. Author accepted an approximately equal split between Pop and Lite; plan recorded | Proposed Pop and Lite ext4 roots approximately 995 GB each; Lite allocation includes its own proposed 32 GiB swap file; preserve existing EFI/recovery/Pop swap | H03 complete; H04 backup/restore and concrete allocation/recovery plan remain prerequisites. No resizing, formatting or installation authorized |

Present these decisions one at a time when their prerequisites are available.
Task registration itself does not settle any pending decision.

## Validation of task setup

2026-10-09: local task/work-directory links, the single TODO entry and whitespace
checks pass. Git confirms exclusion of the private context, account exports,
extracts, inventories and receipts. Reviewed the scoped diff and preserved
existing/concurrent work. No host installation, reboot, graphics change or bench
operation was performed for this setup. Changes remain uncommitted.

2026-10-09 SSH inventory: verified transcript hashes, private exclusions, local
record links and scoped whitespace. Read-only probes and recorded exceptions
are retained in the private running log; unrelated concurrent work preserved.
