# MOS flash remapping and future dual-VDP storage

## Executive summary

**AUDIT-005-F008: retain as a possible environment-switching technique, not
an SD-routing requirement or a present UART optimisation.** Relocating flash
can expose low RAM for another environment's vectors. It does not move an SD
controller between processors or make MOS position-independent. For two VDPs
requesting files, prefer one filesystem owner per physical card and routed,
serialized requests. No implementation, benchmark or hardware change was made.

## Evidence and scope

1. The [TRS-OS agent's evidence](../../../../agon-dev-env/cross-agent/mos_flash_remapping/trsos-mos-boundary-evidence.md)
   shows OSboot mapping MOS to FE0000 and RAM to banks00–07. The relocated MOS
   RST vector still jumps to001900, and the handler calls000220; direct entry
   into relocated stock MOS therefore does not work. MOS working addresses
   around0BC000 are inaccessible in that map. These are the other agent's Mac
   emulator observations, not a new Linux or hardware qualification.
2. Local official MOS v3.0.2, commit
   `8336409351ee5314e02801a7b72a4f1bb5282519`, confirms the mainboard file path:
   `src/mos_api.asm` calls FatFS; `src_fatfs/diskio.c::disk_read/disk_write`
   calls `SD_readBlocks/SD_writeBlocks`, implemented by eZ80 code in
   `src/sd.asm` and `src/spi.asm`. Changing FLASH_ADDR_U changes the eZ80's
   address map, not this electrical ownership. Its
   `src_startup/init_params_f92.asm` initializes flash/RAM mappings and stack.
3. The current EMOS `src_fatfs/ffconf.h` has `FF_FS_REENTRANT=0` and
   `FF_FS_LOCK=0`. Thus concurrent or interrupt-nested file calls are not a
   supported shortcut. A second filesystem instance caching the same card
   independently would also need explicit coherence; remapping supplies none.
4. [Accepted architecture](../../architecture.md) gives EDP ownership of its
   own P4 SD card, with EMOS requesting data over Extender transport. The
   mainboard card is separate. [Current sdserve](../../mainboard-sd.md) already
   relays host requests through P4 to eZ80/MOS, but is foreground Legacy-only;
   this is not background file service during Rally or a qualified Dual-mode
   storage broker.

## Applicability

| Future requirement | Value of remapping | Smaller direction to investigate when needed |
|---|---|---|
| Both VDPs consume files from mainboard SD | No intrinsic benefit: MOS remains the physical/filesystem owner | EMOS serializes file requests and routes returned bytes to the chosen VDP |
| Mainboard and P4 SD cards exposed to applications | Does not select a card or transport | Explicit device/provider selection; one filesystem owner per card |
| Another eZ80 environment owns low vectors but occasionally needs MOS | Potentially useful | A bounded context bridge restoring MOS's original map for a call |
| More interrupt/vector flexibility inside ordinary EMOS | Possible, but changes memory/ABI assumptions | First assess existing IM2 vectors and EMOS-owned handlers |

For a context bridge, execution must enter from memory valid in both mappings.
Preserve MOS RAM/heap and open-file state, both stacks, ADL/MADL/MB, interrupt
mode/vector ownership, and UART/SD state before and after each switch. Mapped
addresses must still refer to preserved physical bytes. Interrupts cannot
enter code or use stacks hidden by the temporary map. Long SD operations
cannot simply mask interrupts throughout: required UART/keyboard/clock service
and buffering must remain accounted for. These are design constraints, not a
demonstrated bridge. First proof would be a harmless MOS query and return,
followed by read-only file access; it is not an authorised next implementation.

For ordinary Dual-mode requests, the more relevant future question is how
EMOS schedules bounded foreground storage work while both VDP connections
remain serviced. Requests arriving through an interrupt should be handed to
the filesystem owner rather than recursively entering FatFS. Queue limits,
backpressure, file-handle ownership and partial/cancelled transfers need a
contract. No speed benefit is claimed without measurement.

## Disposition

Keep the idea for a concrete alternate-environment requirement; do not add it
to the current UART critical path or change accepted EMOS ownership. EMOS owns
any future context bridge and mainboard SD scheduling; Extender owns the
cross-device contract and EDP card service. The note's immediate assessment is
complete. No firmware, wiring, simulator or benchmark was touched. The Author
directed removal of the root AGENTS notice and resumption of the main task.
