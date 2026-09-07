# Stock MOS application and external-interface traces — W3/W4

[AUDIT-004](../AUDIT-004.md), recorded 2026-09-07. This bounded source trace
covers `AUDIT-004-A001`–`AUDIT-004-A011` and
`AUDIT-004-X001`–`AUDIT-004-X003`, including their transport references
`AUDIT-004-T005`–`AUDIT-004-T007`. The
[communication inventory](communication-inventory.md) owns these stable IDs.

Evidence uses stock MOS v3.0.2 at
`8336409351ee5314e02801a7b72a4f1bb5282519` and the official-document snapshot
`f9806bd3cbff6ed5d1c08bef1d51fed11764b86b`, unchanged from the
[W1 selection](baseline-and-research-map.md). Relevant official API, keyboard,
CLI, variable, executable, and storage documentation was read before following
the source paths below. The project-owned MOS fork is excluded.

**Evidence level:** implementation observations from the selected source, with
documented contracts and discrepancies identified separately. No firmware was
built or exercised. Peripheral device implementations and physical wiring are
not proved by these traces. Application calls are same-eZ80 software boundaries;
only their downstream dependencies use physical transports. Primary UART/VDP
receiver details remain in the companion primary-path trace rather than being
duplicated here. W4 table and producer reconciliation added the explicitly
identified corrections below. The Author accepted the bounded audit on
2026-09-07; the [review overview](README.md) records its scope.

## AUDIT-004-A001 — API dispatch and C-function lookup

1. An application supplies the API selector in `A` through `RST 08h`.
   `_rst_08_handler` calls `mos_api` and returns with `RET.L`. `mos_api` selects
   the ordinary or FatFS table; direct unavailable/out-of-range entries reach
   `mos_api_not_implemented`, returning `A=23` and `HL=23`. Arguments and results
   are registers, pointers and caller-owned buffers, not a serialized message.
   MOS wrappers convert selected 16-bit pointers using `MB`; their individual
   conversion rules, rather than one universal wrapper, govern each API.
   [Documentation: RST/API calling convention][D-API];
   [dispatch and tables][M-API], [RST handler][M-VEC].
2. `mos_getfunction` dispatches to `mos_api_getfunction`. The implementation
   initializes `HL=0`, rejects nonzero `MB` with `A=20`, then rejects nonzero
   flags `C` with `A=19`. With `MB=0,C=0`, an index `B` outside the 18-entry
   table (`0x00`–`0x11`) returns **`A=19,HL=0`**. Valid entries return the stored
   24-bit address and `A=0`; reserved entries `0x03`/`0x04` contain zero and
   therefore return a null address with success. The routine tests `MB`, not
   the CPU's ADL state directly; its documented ADL-only use presumes the MOS
   calling convention. [Lookup and pointer table][M-FUNCTION].
3. **AUDIT-004-E09 resolved:** the documentation's out-of-range status `20`
   disagrees with the selected release's observable return path `19`. The
   outer RST handler does not replace that result. This is source evidence,
   not an executed API test. A successful function lookup also says nothing
   about a later device operation: applications must honor the returned
   function's C prototype, arguments, lifetime and result contract.
   [Documented lookup][D-API], [C ABI and function catalogue][D-C].
4. **W4 table reconciliation:** the ordinary table has 128 slots, with 60
   non-stub entries and 68 direct unavailable entries. The FatFS table has 39
   slots (`0x80`–`0xA6`), with seven pure unavailable wrappers and 32 live
   wrappers. A live wrapper need not perform device I/O on every invocation;
   several only inspect caller-owned file state. API `0xA4` also reaches the
   unavailable return after a live operation, as detailed under X003, so
   status `23` alone does not prove that no storage operation occurred.
   Selectors `0xA7`–`0xFF` fail the table bounds check. [Tables and guard][M-TABLES].

## AUDIT-004-A002 — Byte/block VDU output

1. `RST 10h` forwards `A` to `UART0_serial_PUTCH`. `RST 18h` walks caller memory
   and calls the same byte routine, either for the nonzero `BC` length or until
   it encounters the `A` delimiter when `BC=0`. The delimiter is not sent.
   The C `putch` wrapper also calls this routine. MOS does not copy the entire
   command into a software transmit queue or validate a complete VDU command
   at these entry points. [RST loops][M-VEC], [byte path][M-SER].
2. `UART0_serial_PUTCH` checks the open bit, conditionally waits for CTS, and
   retries `UART0_serial_TX` until that routine accepts the byte. The lower
   routine has a `TX_WAIT=16384` iteration bound, but the caller retries it;
   neither CTS waiting nor the outer transmit operation has an overall
   timeout. Acceptance means writing the UART holding register, not confirming
   that VDP parsed or completed the command. The RST block loop does not abort
   on the closed-UART carry result. Downstream framing/pacing belongs to
   `AUDIT-004-T001` and the selected primary operation. [Transmit paths][M-SER].
3. The entry points supply no transaction lock around a multi-byte VDU
   command. Calling another routine that emits VDU bytes while a command is
   incomplete can insert those bytes into the same stream; the RTC API
   documentation explicitly warns about this situation. Source calls remain
   in the caller's context; interrupt-driven receive handling continues when
   the caller permits interrupts. [RTC refresh caveat][D-API].
4. An incidental return-value discrepancy is visible: the RST 18h length
   loop finishes with `LD A,B; OR C`, leaving `A=0`, while the documentation
   says it returns the last character. The delimiter path does return the
   delimiter. This observation does not change the transmitted bytes or
   authorize a correction. [Documented RST 18h result][D-API], [loop][M-VEC].

## AUDIT-004-A003 — Binary state, key map and result flags

1. `mos_api_sysvars`/`mos_api_getkbmap` return pointers to `_sysvars`/`_keymap`
   in MOS RAM; C functions `0x10`/`0x11` return the same addresses in `HL`.
   The VDP does not share that memory. MOS's UART0 interrupt and packet
   handlers copy incoming payload data into the corresponding fields;
   `keyboard_handler` updates the bitmap. The VBLANK handler independently
   updates `_clock`. These producers correspond to primary results/events
   `AUDIT-004-P006`–`AUDIT-004-P015` and `AUDIT-004-P024`.
   [Accessors][M-API], [RAM layout][M-GLOB], [interrupts][M-IRQ],
   [packet consumers][M-PROTO], [key-map consumer][M-KEY].
2. `mos_api_clear_vdp_flags` reads, masks and writes the shared flag byte.
   `mos_api_wait_vdp_flags` calls `wait_VDP(mask)`, which succeeds when
   `(flags & mask) == mask`, or returns `15` after 250,000 polling iterations.
   Success returns zero; a zero mask succeeds immediately. The documentation's
   approximate one second is a delay-loop estimate, not a measured timing
   guarantee or a UART receive timeout. Waiting does not clear flags, consume
   a result, validate its age, or reset the receiver. [Flag APIs][M-API],
   [`wait_VDP`][M-WAIT], [documented usage][D-API].
3. This is latest-state publication, not an event queue or request-ID protocol.
   Callers can observe an already-set flag unless they clear it before sending
   their request. The accessors do not make multi-field reads into coherent
   snapshots; the clear operation contains no interrupt exclusion around its
   read/modify/write. A reader must not infer a new result or an atomic snapshot
   from receiving the pointer. Startup clears the globals area; ordinary
   application return does not reset these results. [State producers][M-PROTO],
   [startup initialization][M-INIT].

## AUDIT-004-A004 — Keyboard retrieval and line editing

1. The public assembly `mos_api_getkey` captures `_keycount`, waits for it to
   change, then waits again if `_keydown` is false. On a key-down event it
   returns the current `_keyascii`. It waits for a subsequent event rather
   than draining a queued character. No time limit or cancel parameter is
   present. The similarly named internal C `mos_getkey` instead waits for
   nonzero `keyascii` and clears that byte after reading it; these are distinct
   implementations. [Public API][M-API], [internal C helper][M-MOS],
   [keyboard documentation][D-KEY].
2. `mos_api_editline` supplies the caller's buffer, length and flags to
   `mos_EDITLINE`. The editor requests mode information, emits display edits
   through `putch`, and `waitKey` waits for a changed event count with key-down
   state. The normal exit is CR or Escape; the return key reaches the caller
   in `A`. Buffer capacity reserves one byte for termination. Flags select
   clearing, tab completion, hotkeys and history; file/command completion adds
   storage and named-variable dependencies. [Wrapper][M-API],
   [editor and `waitKey`][M-EDITOR], [API flags][D-API].
3. The editor's mode-query helper calls `wait_VDP` but discards its result;
   the overall input wait is unbounded and depends on working reverse keyboard
   delivery. Missing VDP traffic is not turned into a separate editor error.
   Shared-state overwrite/coalescing and event-counter wrap are possible
   consequences of this latest-event design, not measured loss rates.
   [Mode query, key wait and edit loop][M-EDITOR].

## AUDIT-004-A005 — Keyboard packet callback

1. `mos_api_setkbvector` stores the caller's address in `_user_kbvector`; any
   nonzero `C` replaces its upper address byte with `MB`. Zero clears the
   callback when supplied as an actual zero pointer. The documented caller
   obligation is to clear the callback before the program exits.
   [Registration contract][D-API], [registration implementation][M-API].
2. `_uart0_handler` enters with interrupts disabled and saves `AF/BC/DE/HL`.
   When the parser dispatches a keyboard packet, `vdp_protocol_KEY` pushes a
   return address and jumps to the registered callback with `DE` pointing to
   `_vdp_protocol_data`. It calls the callback **before** publishing key ASCII,
   modifiers, down state, event count and virtual code, and before updating the
   key map/reset handling. The pointer is the reusable packet payload buffer,
   not a newly allocated packet including wire header/length. [ISR][M-IRQ],
   [callback and subsequent publication][M-PROTO].
3. The callback runs within that receive interrupt. A callback that waits for
   another ordinary UART0 interrupt cannot obtain that progress while
   interrupts remain disabled; it must return for the normal handler to
   finish. The interrupt wrapper does not save `IX/IY`, so arbitrary callback
   register use is not automatically protected. There is no callback timeout,
   per-application ownership token, or automatic unregister in the normal
   executable-return path. Initialization clears the callback with the globals
   area. [ISR][M-IRQ], [return bridge][M-MISC], [startup][M-INIT].

## AUDIT-004-A006 — Interrupt-vector registration

`mos_api_setintvector` forwards the vector byte and full callback address
through `mos_SETINTVECTOR` to `_set_vector`. `_set_vector` saves the interrupt
enable state, disables interrupts while updating the second jump table, returns
the previous handler address, and restores the saved enable state. The selected
CPU interrupt subsequently reaches the application through the vector/jump
tables. The setter contains no bounds/alignment check on the supplied vector
and no handler lifetime management; the caller supplies a valid vector and
appropriate interrupt routine. Startup initializes the table to default
handlers; `main` installs MOS's selected handlers. This is a stock hook, not an
Extender authorization to replace EMOS-owned transports. [API contract][D-API],
[wrapper][M-API], [C bridge][M-MOS], [table update][M-VEC],
[MOS handler installation][M-MAIN].

## AUDIT-004-A007 — RTC convenience operations

1. `mos_GETRTC` calls `mos_UNPACKRTC(...,1)`, formats the unpacked time, and
   returns string length. `mos_UNPACKRTC` refreshes before unpacking for flag
   bit 0, unpacks the existing six-byte `_rtc` data if a destination is given,
   and refreshes after unpacking for bit 1. Flags zero perform only local
   unpacking, with no freshness check. [API and C wrappers][M-API],
   [RTC convenience functions][M-RTCAPI], [packed data handling][M-CLOCK].
2. `rtc_update` does nothing if `rtc_enable` is zero. Otherwise it clears the
   RTC result flag, emits `23,0,VDP_rtc,0` through MOS UART output, and calls
   `wait_VDP(0x20)`. MOS's RTC packet consumer publishes the returned data and
   flag. `rtc_update` returns `void` and ignores timeout status, so callers can
   unpack/format previously held data after a response timeout. The wait bound
   begins after emitting the request; it does not bound a blocked transmitter.
   [Request helper][M-CLOCK], [RTC packet consumer][M-PROTO],
   [polling wait][M-WAIT].
3. **Documentation discrepancy:** bit 1 is documented as refresh-after-unpack
   without waiting. Both refresh positions actually call the same waiting
   `rtc_update`, so bit 1 also waits when RTC is enabled. If both bits are set,
   the implementation issues two refresh requests. `mos_SETRTC` emits the
   setting command and six caller bytes without a separate completion wait.
   There is no request-specific result/timeout exposed by these convenience
   calls. [Documented flags][D-API], [implementation][M-RTCAPI].

## AUDIT-004-A008 — CLI and scripts

1. `main` obtains a line through `mos_input`, invokes `mos_exec(...,true)` on
   CR, stores `Sys$ReturnCode`, and prints an error for a nonzero command
   result. An application calling `mos_oscli` reaches `mos_OSCLI`, which uses
   `mos_exec(...,false)`, stores the same return variable, and returns the
   result. Automatic fallback for unknown commands is restricted to moslets
   for that false context, rather than the full run path. Built-in commands
   are still dispatched according to the command table. [CLI loop][M-MAIN],
   [command dispatch and `mos_OSCLI`][M-MOS], [documented CLI][D-MOS].
2. Built-in `VDU` and `Echo` ultimately emit bytes on the same A002 path;
   `Time` invokes RTC helpers; file commands use X003. Alias expansion and
   commands inside `Exec`/`Obey` remain calls into the same dispatcher.
   `mos_cmdOBEY` reads its file into a 256-byte line buffer, substitutes
   arguments, dispatches each line and stops/report its line on a nonzero
   result. A depth check bounds command recursion; it is not an overall
   execution timeout. Earlier successful script commands are not rolled back.
   [Commands and script implementation][M-MOS], [operator contracts][D-CLI].
3. After storage/state initialization, the enabled boot-config path tries
   `!boot.obey`, then `autoexec.obey`, then `autoexec.txt` on file-not-found;
   keyboard Shift state suppresses this path. The script/CLI interface depends
   on VDP input/output and, when used, storage and named variables. It supplies
   no general recovery from an arbitrary command that blocks in those services.
   [Boot path][M-MAIN], [boot-script and soft-boot documentation][D-MOS].
4. **W4 command-table reconciliation:** the selected table contains 45 normal
   command names reaching 36 handlers. The additional `RUN_MOS_TESTS` entry
   requires `DEBUG > 0`, whereas the selected source defines `DEBUG=0`.
   `Disc` is a normal table entry without a corresponding command heading in
   the selected official catalogue. Its `mos_cmdDISC` handler sets
   `sdcardDelay=TRUE`; `SD_delayDisc` uses that flag to add a software delay to
   SD-driver operations. This configures X003, with no additional transport.
   The driver's nominal delay comment is not measured timing evidence.
   [Command table][M-COMMANDS], [debug selection][M-DEFINES],
   [setter][M-DISC], [driver use][M-SDDELAY], [official catalogue][D-CLI].

## AUDIT-004-A009 — Named variables and code getters/setters

1. Application API wrappers or CLI commands call `setVarVal`/`readVarVal`.
   MOS owns a linked registry of names, types and values. Strings/macros and
   numeric values are local data; code variables invoke stock C getters or
   setters in the caller's context. `setVarVal` rejects public creation of
   code-type variables; stock startup registers those internally. Reads can
   allocate an expanded string and copy it into the caller's buffer; reported
   length and status describe that operation, not a device acknowledgement.
   [Named-variable documentation][D-NVAR], [registry operations][M-NVAR].
2. `mos_setupSystemVariables` registers `Keyboard`/`Console` as write-only
   code variables. Their setters parse a number and emit
   `23,0,setting,value & 0xFF`; they return parser/dispatch success without
   waiting for a VDP setting acknowledgement. Date/time getters and setters
   use A007/`rtc_update`, making a nominal variable operation a potential VDP
   exchange. Code-variable expansion can first call a getter to determine
   length and again to obtain its value. Ordinary named variables remain
   distinct from A003 binary state. [Setters and registration][M-NVARSET],
   [`expandVariable` and update dispatch][M-NVAR].
3. Allocation/type/name errors are returned through the variable API.
   Read-only stock code variables ignore attempted updates with success;
   public deletion preserves code variables. The registry operations add no
   lock or timeout around arbitrary nested device work. Startup rebuilds the
   registry and scripts can reapply persistent configuration; this RAM registry
   itself is not a persistent file store. [Registry behavior][M-NVAR],
   [initialization][M-MAIN].

## AUDIT-004-A010 — Executable launch and return

MOS resolves/loads the selected file, chooses the ordinary or moslet load area,
then `mos_execMode` checks the `MOS` marker and reads the mode byte.
`mos_runBin` selects `_exec16` or `_exec24`, rejecting other modes. The assembly
bridge supplies execution address and parameter pointer, sets/restores `MB`,
and calls through its RAM bridge. The program's return reaches the MOS caller;
that caller owns reporting the status. This is a local execution ABI plus
X003 storage, not another processor link. There is no general program execution
timeout, resource rollback, callback unregister or UART1 close in the return
bridge. Advanced-header/module prose must not imply implementation beyond the
selected marker/mode check. [Executable documentation][D-EXEC],
[`mos_runBin`, `mos_runBinFile`, `mos_execMode`][M-MOS],
[execution bridge][M-MISC].

## AUDIT-004-A011 — Reset and crash entry

1. The reset vector disables interrupts, enters mixed mode and jumps to
   `__init`. That startup code reinitializes GPIO/peripherals, interrupt
   vectors, MOS globals and the C environment before entering `main`.
   This resets MOS's software state; it is not proof of resetting the VDP,
   an external device or every physical power domain. [Reset vector][M-VEC],
   [startup][M-INIT], [C initialization][M-CSTART].
2. MOS `keyboard_reset` recognizes the selected Delete codes with Ctrl+Alt
   modifiers and jumps to address zero on the matching release event. It
   depends on normal VDP keyboard delivery reaching that handler. A stalled
   VDP, disabled receive interrupts or a nonreturning keyboard callback can
   prevent this route. [Key handling][M-KEY], [documented Soft Boot][D-MOS].
3. `_on_crash` disables interrupts, saves registers, emits a report using the
   ordinary RST output paths, then enables interrupts and waits through API
   key input for `r`/`R`. It restores saved registers and uses plain `RET`,
   explicitly assuming accidental entry from ADL code. Output can block before
   that later `EI`; the report is not an independent emergency console or a
   guarantee of recovery from arbitrary damaged stack/transport state.
   [Crash-report contract][D-API], [implementation][M-CRASH].

## AUDIT-004-X001 / AUDIT-004-T005 — External UART1

1. Application `mos_uopen` or C function `0x08` supplies a `UART` structure to
   `open_UART1`. MOS programs divisor, frame settings, FIFO reset/enable and
   the supplied interrupt mask, then sets the UART1-open flag and returns zero.
   The source computes the divisor from the requested baud rate without
   validating a zero/unsupported rate or all structure fields. `main` installs
   no UART1 receive driver; an application requesting receive interrupts must
   install its own handler. [API contract][D-API], [configuration][M-UART],
   [structure][M-UARTH], [default MOS interrupt setup][M-MAIN].
2. PC0/PC1 are selected for alternate serial function. For `FCTL_HW`, MOS
   configures **PC3 as GPIO input**, records the flow-control flag, and
   `UART1_wait_CTS` polls it until low. `open_UART1` does not select PC2 RTS
   output and writes `UART1_MCTL=0`. Thus this stock service's named hardware
   flow-control option establishes a transmit CTS gate, not a demonstrated
   automatic bidirectional RTS/CTS implementation. Actual PC2 state depends
   on prior initialization/use. Processor signal capability and Light 2 pin
   routing need separate hardware evidence. [Configuration][M-UART],
   [CTS wait][M-SER], [board-exposure documentation][D-GPIO].
3. `mos_ugetc` polls UART1 receive-ready and returns a byte/carry; an open
   port with no data waits indefinitely. `mos_uputc` conditionally waits for
   CTS and retries bounded lower-level transmit attempts indefinitely until
   the byte is accepted. Closed calls return no-carry. No MOS software RX/TX
   queue or framing/overrun error return is supplied by these character APIs;
   the configured hardware FIFO and any application ISR own their respective
   buffering. An application ISR that also reads the receive register must
   coordinate with polling reads. [Character wrappers][M-API],
   [polling and transmit routines][M-SER].
4. `close_UART1` disables interrupts and resets line/modem/FIFO controls,
   clearing UART1 flags. It does not restore PC pin mux registers or a
   registered application handler. The application owns external-message
   framing, acknowledgements, flow-control policy beyond that CTS gate, and
   handler cleanup. An operation already inside a polling wait does not
   repeatedly recheck the open flag. Physical baud/electrical limits and the
   external device implementation are outside this source-only trace.
   [Close/open][M-UART], [wait loops][M-SER].

## AUDIT-004-X002 / AUDIT-004-T006 — External I2C master

1. API wrappers pass frequency/address/count/buffer into `mos_I2C_*`.
   `mos_I2C_OPEN` power-cycles/configures the controller and selects a frequency
   code; `main` owns installation of `_i2c_handler`, despite comments in open
   and close suggesting registration happens there. The public operations
   reject addresses above 127 and clamp byte counts to 32; a zero-length read
   immediately succeeds. [Documented API][D-API], [driver][M-I2C],
   [constants][M-I2CH], [interrupt installation][M-MAIN].
2. MOS waits for its shared `i2c_role` to become idle, installs the caller's
   buffer pointer/count, builds address plus R/W bit and requests START with
   interrupts enabled. The ISR sends the address, transmits/receives successive
   bytes directly through that pointer, issues ACK/NACK as appropriate, then
   requests STOP and marks the role idle. There is one shared transaction
   context, not a queue. The caller waits while its master role is active and
   returns `i2c_error`. Slave-mode/status entries are routed to the
   unimplemented/STOP handler; they do not establish a supported slave API.
   [Foreground transaction][M-I2C], [ISR state machine][M-IRQ].
3. Address NACK, data NACK, arbitration loss and bus error map to codes
   1/2/4/8. Foreground waiting uses `get_timer0() > I2C_TIMEOUTMS`, where the
   constant is 2000 and `get_timer0` reads raw timer data registers, not an
   accumulated millisecond clock. The timer is configured with a nominal
   one-millisecond reload. This does **not** establish a reliable two-second
   elapsed deadline. Timeout exits reuse NACK/arbitration codes instead of a
   distinct timeout result. [Error/timeout paths][M-I2C], [constant][M-I2CH],
   [timer implementation][M-TIMER].
4. Recovery has additional limits: `I2C_handletimeout` resets control and
   calls `init_I2C`, which clears message size and restores default frequency
   but does not clear `i2c_role`. The ISR's STOP loop waits for the hardware
   STOP bit to clear while interrupts remain disabled, with no software bound;
   a foreground timeout cannot run while that ISR is stuck. Close disables
   the controller but does not unregister the handler or clear all transaction
   state. These observations preclude claiming guaranteed bus recovery here.
   Device-specific messages, repeated-start requirements, measured timing and
   electrical bus recovery remain unverified. [Reset/open/close][M-I2C],
   [STOP and error handlers][M-IRQ].

## AUDIT-004-X003 / AUDIT-004-T007 — Files, sectors and SD/SPI

1. MOS file APIs resolve names and use up to eight MOS file handles;
   `mos_FREAD`/`mos_FWRITE` pass caller buffers to FatFS and return transferred
   byte counts on success, or zero on invalid handle/error. Direct FatFS APIs
   instead accept FatFS objects and return their own result/count forms.
   Several higher-level APIs therefore collapse error detail; one uniform
   success/error ABI must not be inferred across storage calls.
   [File/API distinctions][D-API], [MOS handles and I/O][M-MOS],
   [configured handle count][M-CONFIG], [FatFS wrappers][M-API].
2. Bundled FatFS reaches `disk_initialize`/`disk_read`/`disk_write`, which call
   `SD_init`/`SD_readBlocks`/`SD_writeBlocks`. The SD driver drives card-select,
   command packets and data over the SPI routines; individual read/write
   blocks use CMD17/CMD24. `_init_spi` configures PB7/PB6/PB3 as MOSI/MISO/clock,
   PB4 as card-select, and PB2 as a high GPIO output; it programs SPI master
   control and divisor 3. These are source register choices, not a verified
   board-routing or electrical-speed result. [FatFS caller][M-FF],
   [disk adapter][M-DISK], [SD driver][M-SD], [SPI driver][M-SPI].
3. **AUDIT-004-E10 resolved:** `SD_readBlocks` and `SD_writeBlocks` take a
   16-bit **block count**, with each block **512 bytes**. Their loops call a
   single-block routine, increment the sector by one, advance the caller
   buffer by `SD_BLOCK_LEN=512`, and decrement count by one. A zero count
   returns success without transferring blocks. The C-function documentation
   calling the count “bytes” is inconsistent with this selected implementation.
   The raw register API also passes this count through, after the unlock
   wrapper. [Documentation][D-C], [raw API][D-API],
   [block loops and `SD_updateIOVars`][M-SD], [C wrapper][M-SDH].
4. **Additional stock defect:** API `0x73`, dispatched as `sd_api_writeblocks`,
   calls `_SD_readBlocks_API`, exactly as `0x72` does. For a valid unlock
   record and nonzero count this enters the **read** path and fills the caller
   buffer from the card; it does not invoke the write wrapper. The separately
   defined `SD_writeBlocks_API` calls the write driver correctly, but this
   public API entry does not reach it. C-function lookup `0x02` correctly
   returns `_SD_writeBlocks`, and `disk_write` also calls the write driver;
   those paths are distinct. This is a direct dispatch trace, not a bench
   result or a proposed source correction. [API entries][M-SDAPI],
   [unlock wrappers][M-SDH], [function table][M-FUNCTION],
   [FatFS disk write][M-DISK].
5. SD initialization retries card setup and checks its returned status.
   Read-token and write-response/busy waits use timer macros with configured
   100/250 millisecond values; actual elapsed timing and device compatibility
   are not measured. SPI byte waiting is itself iteration-limited, with no
   separate propagated SPI timeout status. Multi-block failure can occur
   after earlier blocks/buffer changes; neither SD nor MOS provides a
   transaction rollback. `disk_status` always returns zero and `disk_ioctl`
   returns success without implementing their comments' status/control work,
   so those returns do not prove media presence or physical synchronization.
   `mos_mount` offers explicit remounting, not transparent recovery from card
   removal. [SD loops][M-SD], [timer macros][M-MACRO], [SPI waits][M-SPI],
   [disk stubs][M-DISK], [mount][M-MOS].
6. **Primary-link dependency:** the selected FatFS configuration has
   `FF_FS_NORTC=0`. Its `GET_FATTIME` calls `get_fattime`, and that function
   calls `rtc_update` before packing file timestamps. Consequently operations
   such as file creation/synchronization can emit RTC requests on
   `AUDIT-004-T001` and wait through A007; the storage path is not wholly
   independent of VDP traffic. Raw SD block operations do not call this
   timestamp helper. FatFS is configured for fixed 512-byte sectors,
   `FF_FS_TINY=1`, `FF_FS_REENTRANT=0` and `FF_FS_LOCK=0`; these configured
   buffering/locking choices do not authorize simultaneous uncoordinated
   filesystem and raw-sector access. [FatFS configuration][M-FFCONF],
   [timestamp callers][M-FF], [`get_fattime`][M-DISK], [RTC helper][M-CLOCK].
   W4 also confirmed a separate pathname dependency: `resolvePath` calls
   `expandMacro` unless `RESOLVE_OMIT_EXPAND` is set; `gsRead` expands a
   `MOS_VAR_CODE` value through `expandVariable`. A pathname containing a
   date/time code variable can therefore invoke A009/A007/P012 before a read
   or other file operation. This traffic does not depend on creating a file
   timestamp. [Path expansion][M-PATH], [code-variable expansion][M-GS],
   [registered RTC getters][M-NVARSET].
7. **W4 unavailable-operation reconciliation:** the seven pure FatFS stubs
   are `0x87` (forward), `0x88` (expand), `0x8C` (fprintf), `0x9D` (chdrive),
   `0xA0` (mkfs), `0xA1` (fdisk) and `0xA5` (setcp). In particular, `0x87`
   does not establish a file-to-callback output path. C-function lookup
   `0x05` separately exposes the live `_f_printf`; its file output belongs
   to X003, unlike MOS console `printf` output through A002. The selected
   FatFS configuration disables forward/expand/mkfs and multi-partition
   support, fixes the code page, and enables string functions. API-shaped
   names do not establish support for every upstream FatFS feature.
   [Forward/expand stubs][M-FFSTUB1], [fprintf stub][M-FFSTUB2],
   [chdrive stub][M-FFSTUB3], [mkfs/fdisk stubs][M-FFSTUB4],
   [setcp stub][M-SETLABEL], [C function table][M-FUNCTION],
   [configuration][M-FFCONF].
8. **W4 additional stock defect:** `0xA4` (`ffs_api_setlabel`) calls
   `_f_setlabel`, copies its result to `A`, then restores `HL` without a
   `RET`. Execution falls into `ffs_api_setcp`, which returns `A=HL=23`
   through `mos_api_not_implemented`. The volume-label operation can therefore
   take effect before the wrapper reports that the operation is unavailable;
   the wrapper also discards a FatFS error result. This is a live storage path
   with an incorrect final status, not another pure stub. No card operation
   or firmware correction was performed to validate this source observation.
   [Wrapper fallthrough][M-SETLABEL], [unavailable return][M-TABLES].

## Evidence limits and handoff

All 14 assigned path families have been followed through their MOS entry and
result/effect boundary. The trace resolves E09/E10 and records additional
behavior that differs from documentation or has limited recovery. It does not
certify every MOS API, every malformed input, every FatFS operation, peripheral
electrical behavior or a third-party application/device protocol. Existing
primary path IDs identify the associated VDP endpoints; no new circuit,
transport, build or qualification identity is created. Held hardware work
remains held. No source correction is included.

## Pinned evidence

[D-API]: https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/API.md
[D-C]: https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/C-Functions.md
[D-KEY]: https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/Keyboard.md
[D-MOS]: https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/MOS.md
[D-CLI]: https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/Star-Commands.md
[D-NVAR]: https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/System-Variables.md
[D-EXEC]: https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/Executables.md
[D-GPIO]: https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/GPIO.md
[M-API]: https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src/mos_api.asm
[M-TABLES]: https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src/mos_api.asm#L156-L350
[M-SETLABEL]: https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src/mos_api.asm#L2185-L2197
[M-FFSTUB1]: https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src/mos_api.asm#L1783-L1786
[M-FFSTUB2]: https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src/mos_api.asm#L1844-L1845
[M-FFSTUB3]: https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src/mos_api.asm#L2091-L2092
[M-FFSTUB4]: https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src/mos_api.asm#L2123-L2126
[M-FUNCTION]: https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src/mos_api.asm#L2306-L2360
[M-SDAPI]: https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src/mos_api.asm#L2240-L2281
[M-VEC]: https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src_startup/vectors16.asm
[M-SER]: https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src/serial.asm
[M-UART]: https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src/uart.c
[M-UARTH]: https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src/uart.h
[M-IRQ]: https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src/interrupts.asm
[M-PROTO]: https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src/vdp_protocol.asm
[M-GLOB]: https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src_startup/globals.asm
[M-KEY]: https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src/keyboard.asm
[M-MOS]: https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src/mos.c
[M-COMMANDS]: https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src/mos.c#L91-L140
[M-DEFINES]: https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src/defines.h#L32
[M-DISC]: https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src/mos.c#L619-L622
[M-SDDELAY]: https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src/sd.asm#L186-L204
[M-PATH]: https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src/mos_file.c#L218-L277
[M-GS]: https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src/mos_sysvars.c#L486-L550
[M-WAIT]: https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src/mos.c#L3130-L3155
[M-RTCAPI]: https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src/mos.c#L2994-L3036
[M-CLOCK]: https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src/clock.c
[M-EDITOR]: https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src/mos_editor.c
[M-NVAR]: https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src/mos_sysvars.c
[M-NVARSET]: https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src/mos.c#L3360-L3445
[M-MAIN]: https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/main.c
[M-CONFIG]: https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src/config.h
[M-MISC]: https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src/misc.asm
[M-INIT]: https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src_startup/init_params_f92.asm
[M-CSTART]: https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src_startup/cstartup.asm
[M-CRASH]: https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src/crash.asm
[M-I2C]: https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src/i2c.c
[M-I2CH]: https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src/i2c.h
[M-TIMER]: https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src/timer.c
[M-SD]: https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src/sd.asm
[M-SDH]: https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src/sd.h
[M-SPI]: https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src/spi.asm
[M-DISK]: https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src_fatfs/diskio.c
[M-MACRO]: https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src/macros.inc
[M-FF]: https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src_fatfs/ff.c
[M-FFCONF]: https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src_fatfs/ffconf.h
