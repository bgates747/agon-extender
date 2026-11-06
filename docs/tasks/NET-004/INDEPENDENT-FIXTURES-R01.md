# Independent parallel qualification and conditional UART1 binding

Keep MechAgon moving after its one final parallel test while Extender owns the
remaining carrier diagnosis. Smith directly selects independent Extender
fixtures and interleaved bench scheduling on2026-11-06. No consumer transaction
is replayed and no failed transfer silently changes carrier.

## Current immediate work

N04-018.01 Record the accepted one-final-case/explicit-UART1 decision in task,
  ADR, current architecture and development log. Preserve the selected fresh
  unfiltered r12 control: any setup/admission/capture or execution failure stops
  that attempt, with exact nativeRUN/noRUN and full cleanup recorded. No extra
  generic echo/filter run belongs to MechAgon's final application attempt. [x]

N04-018.02 Prepare the smallest supported UART1 consumer binding from existing
  NET-003 public header/callback/carrier semantics. Reconcile exact EMOS/P4/SDK
  and RFC25 coexistence/ROM fit with component owners; do not assume installed
  netp-only ROM8270 exposes `ext.net`. Return concrete source/artifact facts to
  MechAgon. Deployment follows the actual final-case failure and a separately
  matched prepared combination, never an uncertain session fallback. Detailed
  compile selection: [UART1/RFC25 preparation](UART1-RFC25-R01.md). [x]

N04-018.03 Reuse the independent four-record echo appliance as the baseline
  and prepare a separate generic carrier/graphics-cycle fixture. Exercise
  one-byte and boundary-length records, repeated entry/return, foreground
  UART0 graphics between admitted blocks, first-error preservation and positive
  release. Keep game schema, renderer and consumer runtime out of this fixture.
  The [first ordinary graphics variant](CARRIER-GRAPHICS-CYCLE-R01.md) now
  compiles and passes its actual-leaf checks; repeated entry and guarded RFC25
  variants remain separate qualification under the
  [guarded RFC25 source plan](CARRIER-RFC25-CYCLE-R01.md). The [first physical batch](INDEPENDENT-RESULT-R01.md)
  passes plain and ordinary-graphics controls; it does not reproduce or clear
  the renderer fault. Static buffers, finite iteration/time caps and delayed result logging preserve
  useful evidence. Check mode/route/callback/cursor restoration. [ ]

N04-018.04 Finish the existing fixed VALID-filter candidate source/check/build
  tranche independently. Preserve strict edge/byte/DMA/deadline proof and the
  exact unfiltered baseline. Prepare the [finite unfiltered/filtered comparison](INDEPENDENT-PHYSICAL-R01.md)
  using Extender fixtures, with exact input/rollback and source pins, after
  MechAgon's selected unfiltered control. This is no second MechAgon attempt. [ ]

N04-018.05 Prepare all fixtures and checks while other agents own Olimex. When
  those agents are coding, coordinate normal fresh exclusive checkout for the
  prepared bounded tests, stop on unknown state, preserve evidence and complete
  exact restoration/full clean handback before release. Named priorities and
  actual active ownership persist; never commandeer a quiet lease or poll a
  consumer marked unmonitored. No fixture autorun/startup edit. [ ]

Host checks and waveform samples do not establish analog pulse origin or full
hardware qualification. Record raw counters separately from calibrated time.
Do not broaden beyond these carrier tests, change firmware guards/polarity,
extend deadlines to conceal a fault or add processor-link checksums.
