# Communications source audit r01

The existing owners provide useful byte-stream and network foundations, but
neither the accuracy mixed-leg interface nor an actual rejected-pulse event
counter exists in the reviewed fixed-filter path. Portable fixture code can
proceed independently; hardware readiness cannot be inferred from it.

## Reviewed references

1. Official MOS v3.0.2, commit `8336409351ee5314e02801a7b72a4f1bb5282519`,
   and VDP v2.16.0, commit `c7ac293d2aa81ddfa693390549bcd909069c8fc3`,
   were clean at their exact release tags. Documentation commit
   `f9806bd3cbff6ed5d1c08bef1d51fed11764b86b` describes RST18 stream
   output, MOS file write counts and buffered VDU command0/2. No reference edits.
2. Maintained `vdp/video/extender/transport/parallel_vdu_stream.hpp` and
   `console_stream.hpp` connect an8192-byte receive/return queue and4096-byte
   admitted block store to the existing parser. Provisional reverse bytes are
   consumed only after owner completion. START/POLL/STOP are session-bound.
3. Owned EMOS `src/emos_exext.c` provides ordinary RST10/18 byte streams through
   EMOS-owned ExExt,4096-byte outgoing batching and512-byte receive assembly.
   UART carries control while ordinary VDU/replies use parallel in that mode.
   This is a better performance-source donor than pretending opaque NM messages
   already provide ordinary VDU routing. Its historical build is not current.
4. `include/agon/net.h` and `net_parallel.h` expose distinct UART/parallel NM
   compositions with128 opaque bytes, static lifetime and positive release.
   Their current selection does not support arbitrary mixed-leg replies or a
   permanent UART NACK channel through a terminal carrier fault.

## GPIO filter observability

1. Reviewed ESP-IDF commit `b774170ff46c393eeb5e495ea37936038d3f4f4f`,
   `components/esp_driver_gpio/include/driver/gpio_filter.h`,
   `src/gpio_pin_glitch_filter.c`, P4 `hal/gpio_ll.h`, and both hw_ver1/hw_ver3
   `soc/io_mux_struct.h` and `soc/gpio_struct.h` register descriptions.
2. The fixed pin filter rejects pulses shorter than two IO-MUX sample clocks.
   Its API creates/enables/disables/deletes a filter; there is no suppression
   counter or event callback. The fixed-filter low-level operation sets the
   IO-MUX `filter_en` bit. No rejected-pulse counter was found for that path.
3. The GPIO analog-comparator `zero_det_filter_cnt` register is a different
   peripheral function. Its name is not evidence of rejected digital VALID or
   CLOCK pulses. Do not read it and label it the required count.
4. Record actual fixed-filter state/configuration and supported post-filter
   counters, plus separately named software rejection reasons and timestamps.
   Hardware rejected-pulse count is unavailable in this reviewed path, not zero.
   Exact pulse-time correlation remains unfulfilled without another qualified
   internal observation technique. No extra sensor, raw counter tap, changed
   filter or source-invented hardware hook is selected by this audit.

## Next owner integration

Before any resident code change, bind a diagnostic mode/route/service which
can positively retire a parallel transfer and then carry NACK/RETRY via UART1.
Preserve the existing no-uncertain-replay rules and exact production providers.
VDU streaming needs a parser-bound observer and safe resource baseline; opaque
NM echo alone will not prove real VDU delivery. Resource fit and the complete
matched firmware pair remain implementation gates, not reasons to block the
independent protocol, peer, journal, corpus and analyser work.
