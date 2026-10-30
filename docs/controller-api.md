# Controller input for applications

Use the single public include `include/agon/controller.hpp` for normalized gamepad input in an ordinary AgonDev C++ application. Its routines are linked into the application; EMOS retains transport ownership. The include supplies named controls, native stick/trigger values, validity, conservative age and retained press counts without allocation or a MOSlet. This development API requires the matching reduced EMOS controller endpoint and has software/target-build coverage; the earlier physical installation still uses the older application gateway.

P4 or the host acquisition adapter owns physical controller decoding. The public include has no USB IDs, device report layouts, calibration UI or application-specific flight/game mappings. The on-hand F310's XInput-style controls define the normalized interface; the include alone does not make every controller compatible. See the [input guide](controller-input.md) for acquired-source support and the [transport contract](protocols/controller-emos.md) for exact bytes and ownership.

## AgonDev use

Add the repository's `include` directory to the C++ include path, or copy the maintained header unchanged into an application's `agon` include directory. The header contains its wire definitions and default MOS gateway binding; it needs no controller assembly file or linked controller service module.

```cpp
#include <agon/controller.hpp>

static agon::controller::Client<> pad;

bool start_controls() {
    return pad.open();
}

bool poll_controls(uint8_t& left_x, bool& button_a) {
    if (!pad.update()) {
        left_x = 128;
        button_a = false;
        return false;
    }
    const auto& input = pad.state();
    left_x = input.valid
        ? input.stick8(agon::controller::Axis::LeftX) : 128;
    button_a = input.down(agon::controller::Control::A);
    return true;
}

bool stop_controls() {
    return pad.close();
}
```

Keep `Client` and its buffers in ordinary application RAM, normally static storage below `0xB0000` and at/above `0x040000`. A local object on the MOS-owned call stack is unsuitable. EMOS excludes Core, MOSlet and interrupt callers. Call from foreground code with interrupts enabled, at complete VDU command boundaries. One admitted controller client is supported. The client is noncopyable and performs no allocation.

Before invocation, the operator must already have selected healthy Extender keyboard/UART admission and Legacy or ExCom through supported EMOS commands. The application include does not enable that admission, select a display route, configure UART/GPIO, install an ISR or load another executable. Controller and SD ownership remain independent.

| Method or field | Meaning |
|---|---|
| `open()` | Request admission; return false if the service is absent, incompatible, busy or unavailable |
| `update()` | Consume at most one reply, age retained state and request the next refresh when possible |
| `state()` | Return the last application-owned `State`; call `update()` at the application's input cadence to keep its validity/age current |
| `close()` | Attempt healthy wire close, then revoke local admission even when that send fails |
| `error` | Numeric gateway/content status; capture it when a method returns false |
| `error_operation` | New gateway operation 4 OPEN, 5 RECEIVE, 6 SEND or 7 CLOSE |

A successful OPEN admits transport; it does not guarantee a connected or valid controller source. `update()` returns true while normally waiting or while the source is invalid/stale. Applications must inspect `State.valid` before using input. Busy status 31 can accompany a successful update while waiting; it is not an automatic reconnect request. RECEIVE does not wait for a reply. Sending a refresh can encounter EMOS's existing bounded serializer/CTS wait.

A false update neutralizes controls and stops further automatic requests. Capture the failed status/operation before calling `close()`, which has its own result. Correct the cause, then explicitly close/open or restart the application; the client never reopens after a fault. The client renews a healthy lease at query 65000, before sequence exhaustion, while preserving source identity and counts. A refused nested OPEN does not close another admitted client.

## Normalized state

| State member or helper | Representation |
|---|---|
| `stick[4]` | Signed 16-bit left X, left Y, right X, right Y; range −32768..32767 |
| `trigger[2]` | Separate unsigned 8-bit left/right triggers; range 0..255 |
| `held` | Fifteen-bit normalized control mask |
| `down(Control)` | Held-state query, false whenever the sample is invalid |
| `presses[15]` | Observed down transitions, saturating at 65535 per control |
| `sequence` | Latest source state sequence |
| `source[16]` | Opaque P4 receiver/acquisition-session identity; no USB device identification |
| `generation` | Increments when an accepted source identity changes |
| `connected` | Source-active flag from P4; activity alone does not establish valid input |
| `valid` | Accepted input is valid and within the freshness bound |
| `age_ms` | Conservative nominal age bound; not calibrated input latency |
| `stick8(Axis)` | Optional unsigned 8-bit conversion of one native stick value |
| `axis8(value)` | Free conversion helper: −32768 → 0, 0 → 128, 32767 → 255 |

`Axis` names are `LeftX`, `LeftY`, `RightX` and `RightY`. The named control values are the mask/press-array indices below. The application decides dead zones, inversion, mapping, throttle, pause and other gameplay policy after normalization.

| Index | `Control` name | Index | `Control` name | Index | `Control` name |
|---:|---|---:|---|---:|---|
| 0 | `A` | 5 | `RightShoulder` | 10 | `RightStick` |
| 1 | `B` | 6 | `Back` | 11 | `Left` |
| 2 | `Y` | 7 | `Start` | 12 | `Right` |
| 3 | `X` | 8 | `Guide` | 13 | `Up` |
| 4 | `LeftShoulder` | 9 | `LeftStick` | 14 | `Down` |

P4 retains button/D-pad transitions between application polls. The library validates the complete result before accepting any transition, changes its acknowledgement only after accepting the complete fresh batch, and sends that acknowledgement in its next request. Short down/up taps therefore contribute to `presses` even when no display update observes the held state. Repeated transition IDs do not count twice. Malformed contents cannot commit a valid prefix or its acknowledgement.

An accepted source identity change clears the old count baseline and edge cursor. Source expiry/staleness preserves counts already observed for inspection while clearing validity, held controls, sticks and triggers. An explicit new OPEN resets application state; healthy transport renewal preserves it. Applications can keep a separate display/count baseline, as the viewer does for its R key, without discarding transport acknowledgement.

The library bounds age using P4's source age, raw EMOS round-trip/cache tick deltas and a separate two-unit phase allowance for each local interval. It also ages its retained sample on later updates. The nominal multiplier is 9 ms per MOS clock unit and the rejection threshold is 250 ms. Mainboard VBlank rate, clock quantization and transport scheduling limit interpretation: these values do not establish measured one-way or controller-to-display latency. The exact [freshness calculation](protocols/controller-emos.md#controller-reply-and-gateway-timing) belongs to the transport contract.

## Host-model binding

Host tests instantiate `Client<Binding>` with a small binding value. The binding exposes these methods; it may retain a pointer/reference to model state:

```cpp
struct Binding {
    bool available();
    uint32_t clock();
    uint32_t exchange(uint8_t* input, unsigned input_length,
                      uint8_t* output, unsigned output_capacity,
                      unsigned& received);
};

// Binding model_binding = ...;
// agon::controller::Client<Binding> pad(model_binding);
```

`clock()` returns a wrapping unsigned 32-bit count of nominal MOS clock units. The client handles unsigned clock wrap when aging retained samples. `exchange()` uses native host pointers, returns the gateway status, and reports the actual output length through `received`. On success, the output length must equal the requested capacity. Its input/output shapes and operations are exactly the [resident gateway table](protocols/controller-emos.md#resident-gateway); no model-specific controller decoder is substituted.

The default AgonDev binding selects the same existing gateway via register-preserving MOS calls. The [viewer builder](../tests/fixtures/controller/build.py) checks those constants against maintained EMOS `mos_api.inc`, checks both mechanical wire copies, builds the public header on AgonDev and records its hash. An external application copying the header should retain that matching EMOS/wire dependency check in its build process.

The standalone model and the actual P4/EMOS/public-client software pipeline run through:

```sh
.venv/bin/python tests/test_controller_pipeline.py
```

The tests replace physical boundaries. Passing them does not qualify hardware, input latency, every USB device or the application's renderer. The mode20 viewer's [fixture guide](../tests/fixtures/controller/README.md) describes its separate display lifecycle and physical evidence limits.

## Compatibility

The new client uses gateway operations 4–7 and receives 98 bytes: unchanged CIS2 bytes 0–95 followed by two raw timing bytes. The older client used operations 0–3 and received 96 bytes. Those application/EMOS combinations must not be mixed; the service name and availability discovery alone do not prove compatibility. The new endpoint refuses the old operations, and the old endpoint refuses the new OPEN.

P4's CI2 request and CIS2 96-byte physical UART reply are unchanged. A controller-enabled P4 implementing that carrier remains the transport peer; this API does not install or enable controller acquisition. The earlier physically reviewed viewer/EMOS combination remains historical evidence under its [frozen gateway contract](tasks/INPUT-005/CONTROLLER-GATEWAY-V1.md). New source remains an offline development result pending separately authorized identification, installation and physical review. Production selection is unchanged.
