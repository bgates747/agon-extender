# Matched UART1 networking and guarded UART0 graphics

Prepare the explicit UART1 alternative so MechAgon's application work can
continue if its final parallel attempt fails. This is source/build preparation;
it does not select another parallel test or permit premature installation.

N04-018.02.1 Retain NET-003 public SDK and application-owned NM callback storage,
  chaining every non-NM packet to the actual previous mainboard callback.
  Positive RELEASE precedes vector restoration; refusal retains state. [x]

N04-018.02.2 Publish EMOS INTEG-023 and the smallest compile composition that
  retains guarded RFC25 without resident NETP. Preserve source-span bounds,
  admission/result/IFF/foreground checks, UART0 interrupt leaf and mandatory
  link validation. No new API or raw upstream RFC25 result assumption. [x]

N04-018.02.3 Use one fresh Pi compile reservation: identified EMOS build plus
  one clean full P4 build, serial compiler, expected twenty minutes and a fresh
  thirty-minute whole-tranche stop including owned cleanup. The previous
  independent VALID-filter tranche stopped at its original fifteen-minute
  bound and produced no deployable image; it is not resumed or extended.
  Require at least512MiB available RAM, temperature below80C, owned descendant
  identity tracking and no surviving children before release. No emulator,
  firmware install, device capture or network test in this compile tranche. [ ]

N04-018.02.4 Select the retained P4 source e14e0b8a with application networking
  enabled and parallel networking disabled. Keep board, display, controller,
  SD, USB and reset composition matched to the current full-feature candidate.
  Require clean identified source, build-wrapper validation and exact BIN/ELF/
  map/configuration/dependency hashes. EMOS source1c2ac3a retains guarded RFC25
  and UART-NM; prove complete ROM fit and actual callback/sysvars map. [ ]

N04-018.02.5 Return exact matched artifacts and callback-chain contract to
  MechAgon. Deploy only after the one final parallel attempt actually fails,
  completes its cleanup and yields a normal fresh admission/readiness record.
  Keep the installed unfiltered combination for the final parallel attempt.
  No hidden carrier fallback, uncertain payload replay or address guess. [ ]
