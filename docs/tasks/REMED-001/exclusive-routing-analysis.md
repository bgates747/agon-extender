# Exclusive-mode transparent command-routing analysis

- Parent task: [REMED-001](../REMED-001.md), Work 2.c
- Open decision: SETUP-005-D001
- Scope: untouched VDU command routing in Exclusive Compatible and Exclusive
  Extended modes
- State: Accepted task-local routing decision
- Prepared: 2026-08-23
- Accepted: 2026-08-23

## Question to resolve

How can untouched applications and MOS itself continue using the stock VDU ABI
while the selected exclusive mode sends all ordinary audio/video commands to
EDP rather than the onboard VDP?

This analysis selects only the logical interception and backend boundary. It
does not select mode lifecycle, response ingress, physical Compatible wiring,
parallel link framing, input relaying, or fallback timing.

## Official path

MOS `v3.0.2` has two distinct sources of ordinary VDU output that converge only
at `UART0_serial_PUTCH`:

```text
application RST.LIL 10h --------------------+
application RST.LIL 18h byte loop ----------+--> UART0_serial_PUTCH --> onboard VDP
MOS C runtime putch / printf / boot output --+
```

The fixed low-ROM entries jump to `_rst_10_handler` and `_rst_18_handler` in
`src_startup/vectors16.asm`. Both handlers call `UART0_serial_PUTCH` directly.
The C runtime `_putch`/`putch` implementation in `src/serial.asm` also calls
`UART0_serial_PUTCH` directly. This path carries MOS startup synchronization,
boot messages, command-line output, and other MOS-generated VDU traffic.

Consequently:

1. replacing or wrapping only `RST.LIL 10h` and `RST.LIL 18h` misses MOS's own
   output;
2. changing `UART0_serial_PUTCH` itself would incorrectly redefine the raw
   UART0 device rather than the VDU destination;
3. application loaders or wrappers cannot capture MOS output or arbitrary
   untouched binaries; and
4. an optional resident EDU service cannot safely or officially replace the
   fixed restart ABI.

## Required logical boundary

Introduce one MOS-owned **VDU output dispatcher** between all semantic VDU
producers and the physical backend:

```text
RST.LIL 10h ---------+
RST.LIL 18h ---------+--> MOS VDU dispatcher --> selected VDU backend
MOS putch / printf ---+

raw MOS UART APIs ---------------------------> their named UART unchanged
```

The dispatcher is a system-mode facility, not part of the optional EDU service.
It must preserve the documented restart ABI and ordinary MOS output semantics.
Raw UART0 and UART1 APIs retain their explicit device meaning except where a
selected mode reserves a UART and reports that conflict through the later
lifecycle/capability policy.

The logical backend map is:

| Mode | Ordinary VDU backend |
|---|---|
| Legacy | Stock UART0/onboard VDP |
| Exclusive Compatible | EDP stock-UART backend; exact eZ80 UART, signals, and circuit remain Work 2.k plus a later hardware review |
| Exclusive Extended | EDP eight-bit forward-parallel backend; link framing remains below the VDU stream |
| Dual | Stock UART0/onboard VDP; EDP remains separately EDU-addressed |

The same stock VDU byte stream reaches the same retained EDP parser in both
exclusive modes. Only the selected transport adapter differs.

## Dispatcher operations

A byte-only function is logically sufficient but risks making the selected
high-speed transport pointless. The boundary should therefore define both:

1. **write byte** — used by `RST.LIL 10h`, MOS `putch`, and other single-byte
   producers; and
2. **write stream** — used by `RST.LIL 18h`, preserving counted and delimited
   behavior while allowing a backend to transfer blocks efficiently.

A backend may implement stream writing as a byte loop where appropriate. The
parallel backend may use a true block path. Optimization must not alter the
byte sequence visible to the EDP parser.

The dispatcher must preserve:

- `RST.LIL 10h` input and register behavior;
- `RST.LIL 18h` counted and delimiter modes, pointer normalization, stopping
  conditions, and resulting registers;
- exact byte order across single-byte and stream calls;
- command continuation across call boundaries;
- blocking, flow-control, timeout, and failure behavior selected for the mode;
- separation between semantic VDU output and raw UART access; and
- an invalid/uninitialized-mode behavior defined by D002 rather than guessed by
  a transport backend.

Mode changes cannot occur in the middle of a stream or while either parser has
a partial command. D002 must define quiescence, parser reset, and transition
rules; Work 2.c only establishes the dispatcher through which those rules act.

## Startup and physical-input intersection

Official VDP `v2.16.0` waits in `VDUStreamProcessor::wait_eZ80()` until it
receives General Poll. Only then does its normal processing loop—including
keyboard and mouse handling—start. MOS `v3.0.2` likewise blocks in
`wait_ESP32()` until a General Poll response arrives, then sends the full-duplex
feature setting and key-state request.

This creates two separate exclusive-mode startup needs:

1. EDP must receive the authoritative General Poll and become the compatibility
   display processor; and
2. the onboard VDP must still receive a controlled initialization sequence so
   that it can serve as the v1 physical keyboard/mouse owner.

Sending one uncontrolled startup stream to both processors is prohibited. The
MOS integration therefore needs a private, explicitly owned onboard-VDP control
route for bootstrap and later delegated input-device configuration. Any
onboard mode or other response generated during bootstrap must not race with or
overwrite the final EDP-authoritative state.

D002 owns exact startup order, reset, failure, and fallback. D003 owns response
classification and parser ingress. D007 owns the onboard bootstrap/configuration
route and processed-input relay. This finding is a dependency of all three and
must not be hidden inside the transport implementation.

## Alternatives

### A. MOS-owned VDU dispatcher — recommended

Amend MOS so every semantic VDU producer uses a mode-selected backend while
the public restart entry points and raw UART APIs retain their identities.

- **Strengths:** captures untouched applications and MOS output; preserves the
  existing ABI; needs no Agon soldering; creates one auditable routing point;
  supports both exclusive transports without duplicating application logic;
  permits efficient block output; and can coordinate startup and failure with
  MOS-owned state.
- **Costs:** exclusive modes require an Extender-enabled MOS image; the project
  must maintain and rebase a narrow MOS patch; mode selection must be available
  before startup synchronization; reserved UART/GPIO conflicts require explicit
  policy; and every supported MOS release needs qualification.
- **Boundary:** the patch routes bytes only. It must not become a second VDU
  parser or write response semantics by hand.

### B. Hardware interposition or UART0 switching — reject for Rev 1 routing

Physically switch or intercept the stock UART0 path so existing MOS continues
writing UART0 while hardware selects onboard VDP or EDP.

- **Strengths:** leaves MOS VDU code untouched and captures every UART0 byte.
- **Costs:** requires access to the onboard UART path, switching and isolation,
  input/response arbitration, power/reset safety, and likely board modification
  or soldering; it does not naturally provide the selected parallel-forward
  Extended transport; and failures can electrically wedge the stock machine.
- **Disposition:** not the product routing architecture. Hardware still must be
  designed for the selected Compatible endpoint after firmware requirements,
  but it need not interpose on UART0.

### C. Runtime ROM shadowing or patching — reject

Attempt to remap or patch the low restart handlers at runtime.

- **Strengths:** could theoretically redirect application restart calls.
- **Costs:** no safe supported mechanism has been established; it misses MOS C
  `putch` unless separately patched; ownership and restoration are fragile; and
  failures threaten the whole machine.

### D. Resident hook, loader, wrapper, or binary rewrite — out of scope as an
independent Extender owner

Intercept calls from cooperating applications or rewrite selected binaries.

- **Strengths:** linked code remains useful as an opt-in EMOS API binding or a
  narrowly qualified application wrapper.
- **Costs:** cannot capture arbitrary untouched software or MOS-generated
  output, safely own persistent UART/GPIO/vector state, or arbitrate multiple
  clients. Direct Extender activation under stock MOS is unsupported and cannot
  satisfy Dual or either exclusive-mode contract.

### E. Compile-time-only MOS backend — useful implementation stage, not final
lifecycle

Build separate MOS images with one fixed VDU backend.

- **Strengths:** smallest initial implementation and deterministic early tests;
  avoids an immature runtime transition mechanism.
- **Costs:** cannot by itself deliver the accepted four-mode runtime product and
  does not define failure or fallback.
- **Disposition:** permissible as a bounded implementation/qualification stage.
  D002 still owns the final selection and transition model.

## Staged architecture direction

The Author accepted a two-stage direction on 2026-08-23:

1. **First-round exclusive routing:** implement the narrow Extender-enabled MOS
   modification selected by Work 2.c for both Exclusive Compatible and
   Exclusive Extended. Favor the shortest auditable route to exclusive EDP
   ownership while preserving the stock application ABI.
2. **Later cooperative Dual integration:** pursue a modular MOS service system
   capable of registering optional services and combining only the facilities
   a user selects. Its primary Extender purpose is to make Dual operation
   genuinely cooperative through explicit arbitration and namespaced ownership,
   rather than allowing onboard VDP and EDP integrations to collide over
   exclusive MOS resources.

The second stage is aspirational and does not gate the first. **Dual mode**
remains the formal operating-mode name; “cooperative” describes the desired
quality of its later system integration rather than creating or renaming a mode.

This direction is aligned with the official MOS Modules proposal rather than a
purely local invention. Current official documentation states that MOS 3.0 has
no module system but describes a future design that may:

- divide always-present Core MOS from runtime-loaded modules;
- load modules in the `0x0B0000`–`0x0B7FFF` moslet/module area;
- provide API calls, star commands, C functions, drivers, and unified-I/O
  implementations;
- permit user-provided modules; and
- register APIs or services so incompatible implementations do not claim the
  same identifier.

Executable-header support for “module safe” and “module compatible” programs
already anticipates that future. Exact module ABI, residency, dispatch,
registration, coexistence, and upstream status are not finalized. Extender
should therefore monitor and preferably collaborate with the upstream design
and avoid cementing a conflicting local ABI. The durable aspirational work now
lives in [MOS-001](../MOS-001.md); this Q01 record preserves only the
decision and its provenance.

## Source findings and patch surface

The smallest evidenced MOS source surface is:

| Official MOS `v3.0.2` source | Material fact |
|---|---|
| `src_startup/vectors16.asm` | Fixed restart entries; RST 10 and each RST 18 byte call `UART0_serial_PUTCH`. |
| `src/serial.asm` | `_putch`/`putch` also calls `UART0_serial_PUTCH`; raw UART0/1 TX, RX, blocking operations, CTS behavior, and serial flags live here. |
| `main.c` | Initializes both UART peripherals, sends General Poll through `putch`, waits indefinitely for response, then sends feature and keyboard-state commands. |
| `src/uart.c` | Configures UART0 on Port D with hardware RTS/CTS and UART1 on Port C with its distinct GPIO/flow-control behavior. |
| `src/interrupts.asm` | UART0 receive ISR feeds the stock VDP packet parser directly. Response routing remains D003 rather than D001. |

An eventual patch should add a dedicated dispatcher unit and replace only the
semantic VDU call sites. It should not fold dispatch logic into the generic raw
UART implementation. Exact files and symbols remain implementation-task work,
not an authorization from this analysis.

## Work 2.c question register

Questions are asked and disposed one at a time. Work 2.c closes only after each
is accepted, rejected with a replacement, or deferred to its named owner.

### `W2C-Q01` — System-level routing family

- **Status:** Accepted (2026-08-23)
- **Question:** Adopt an Extender-enabled MOS VDU dispatcher as the supported
  transparent routing architecture for both exclusive modes, while rejecting
  hardware UART0 interposition, runtime ROM patching, and application wrappers
  as ways to satisfy the untouched-software guarantee?
- **Recommendation:** Accept. This is the only evidenced option that captures
  both application restart calls and MOS-generated output without requiring
  users to modify their Agon hardware.
- **Consequence:** Dual, Exclusive Compatible, and Exclusive Extended require a
  compatible EMOS build. Stock MOS remains sufficient only for Legacy, where
  Extender is inactive.
- **Disposition:** Adopt the Extender-enabled MOS VDU dispatcher as the
  supported transparent routing family for both exclusive modes. The first
  implementation follows this path of least resistance. Reject hardware UART0
  interposition, runtime ROM patching, resident hooks, and application wrappers
  as substitutes for EMOS ownership. Preserve linked wrappers only as EMOS API
  bindings. Track a later MOS Modules-aligned service
  architecture as the aspirational path to genuinely cooperative operation;
  [MOS-001](../MOS-001.md) owns that work and the unresolved relationship
  to Dual mode.

### `W2C-Q02` — Dispatcher coverage and abstraction

- **Status:** Accepted (2026-08-23)
- **Question:** Route `RST.LIL 10h`, `RST.LIL 18h`, and MOS C-runtime
  `putch`/`printf` through one MOS-owned VDU dispatcher with byte and stream
  operations, while leaving raw UART0/UART1 APIs device-specific?
- **Recommendation:** Accept. This is the narrowest complete interception point
  and preserves a block path for Extended performance.
- **Disposition:** Route `RST.LIL 10h`, `RST.LIL 18h`, and MOS C-runtime
  `putch`/`printf` through one MOS-owned semantic VDU dispatcher. Require byte
  and stream operations so backends can preserve the application byte stream
  without forcing the Extended transport through a per-byte implementation.
  Keep raw UART0 and UART1 APIs tied to their named physical devices; any mode
  that reserves one must report that availability separately rather than
  silently redefining the API.

### `W2C-Q03` — Mode-to-backend mapping

- **Status:** Accepted (2026-08-23)
- **Question:** Fix the logical map as Legacy/Dual to onboard UART0, Exclusive
  Compatible to the future EDP stock-UART backend, and Exclusive Extended to
  the EDP forward-parallel backend, with both exclusive backends delivering one
  identical stock byte stream to the retained EDP parser?
- **Recommendation:** Accept. Physical endpoint and framing choices remain in
  Works 2.k–2.l and later hardware work.
- **Disposition:** Map Legacy and Dual ordinary VDU to the onboard VDP over
  UART0, Exclusive Compatible ordinary VDU to the future EDP stock-UART
  backend, and Exclusive Extended ordinary VDU to the EDP forward-parallel
  backend. Both exclusive backends deliver an identical application-visible
  byte stream to the same retained EDP parser. Defer Compatible circuitry and
  Extended link framing to their explicit later owners.

### `W2C-Q04` — Controlled onboard-VDP side channel

- **Status:** Accepted with Rev 1 intermediary constraint (2026-08-23)
- **Question:** Require MOS integration in both exclusive modes to retain a
  private, explicit onboard-VDP control route used only for physical-input
  bootstrap and accepted delegated configuration, never as a mirrored ordinary
  VDU path?
- **Recommendation:** Accept the requirement and defer exact startup,
  response-drain, configuration, and relay mechanics to D002, D003, and D007.
  Without some controlled initialization, the stock onboard VDP remains in
  `wait_eZ80()` and cannot fulfill its accepted v1 input role.
- **Disposition:** Retain a private MOS-owned onboard-VDP control route in both
  exclusive modes for physical-input bootstrap and accepted delegated
  configuration only. Never mirror ordinary VDU to that route. In Rev 1 all
  communication between onboard VDP and EDP is relayed by MOS/eZ80 software;
  there is no direct processor-to-processor electrical or protocol link. Exact
  startup, response classification, configuration, and event relay remain with
  D002, D003, and D007. [LINK-001](../LINK-001.md) owns the separate post-v1
  aspiration for a possible bidirectional high-speed link, with SPI only a
  candidate.

### `W2C-Q05` — Compile-time staging

- **Status:** Accepted (2026-08-23)
- **Question:** Permit fixed-backend MOS builds for early deterministic
  implementation and qualification, without treating them as resolution of
  the final mode lifecycle?
- **Recommendation:** Accept. This reduces early variables while D002 retains
  authority over the product's discovery, selection, transition, and fallback
  contract.
- **Disposition:** Permit fixed-backend MOS builds as explicit developmental
  and qualification staging artifacts. Separate onboard, Compatible, and
  Extended builds isolate each backend and are necessary to establish the Rev
  1 functionality targets before runtime switching adds another failure
  dimension. They neither constitute the final product mode lifecycle nor
  weaken D002's transactional activation, fallback, and recovery requirements.

## Accepted lifecycle dependency

The Author established the following D002 requirement while accepting Q03:

- requesting a mode whose required Extender-enabled MOS hooks, EDP firmware
  capability, resident/TSR-like support, MOS Module, transport backend, or other
  prerequisite is absent must fail cleanly and leave the current mode and
  routing unchanged;
- activation must not publish the new mode or redirect ordinary VDU until all
  required components have passed capability and readiness checks;
- a partially installed or incompatible support stack must report a bounded,
  comprehensible failure and must not strand MOS output on an unavailable
  backend; and
- on stock MOS, an Extender-specific star command or API being absent and
  producing the normal `Invalid command` or unavailable-API result is an
  acceptable graceful failure. Stock MOS supports no active Extender mode.

Exact commands, capability exchange, rollback, timeouts, and fallback behavior
remain D002 / REMED-001 Work 2.d. This accepted invariant constrains that later
design without selecting its mechanism.

## Work 2.c disposition

The Author accepted Q01–Q05 on 2026-08-23. SETUP-005-D001 is resolved by the
MOS-owned VDU dispatcher, complete semantic-output coverage, four-mode backend
map, controlled onboard-VDP side channel, Rev 1 MOS/eZ80 intermediary boundary,
and fixed-backend staging allowance recorded above. Normative promotion remains
REMED-001 Work 2.m; this acceptance authorizes no implementation.
