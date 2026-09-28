# BUILD-001 B01-01 — Native ESP-IDF and Arduino-component précis

Status: complete for design review, 2026-09-28. This précis is bounded to the
contracts needed to replace the P4 PlatformIO/SCons outer build. It does not
select new product behavior or upgrade the pinned framework versions.

## Selected compatibility baseline

The current P4 build contains ESP-IDF 5.5.5, Arduino-ESP32 3.3.11 and the
RISC-V GCC 14.2.0 toolchain. Arduino-ESP32 3.3.11 is published in Espressif's
component registry, supports ESP32-P4 and declares ESP-IDF `>=5.3,<6.2`.
Therefore the current ESP-IDF 5.5.5 and Arduino-ESP32 3.3.11 pair is within the
component's declared compatibility range; BUILD-001 does not need a framework
upgrade merely to move build authority.

Sources:

- [Arduino as an ESP-IDF component](https://docs.espressif.com/projects/arduino-esp32/en/latest/esp-idf_component.html)
- [Arduino-ESP32 3.3.11 registry record](https://components.espressif.com/components/espressif/arduino-esp32/versions/3.3.11/versions)
- [Arduino-ESP32 3.3.11 dependency contract](https://components.espressif.com/components/espressif/arduino-esp32/versions/3.3.11/dependencies)

The Arduino documentation explicitly supports installing Arduino-ESP32 through
the IDF Component Manager. It also requires `CONFIG_FREERTOS_HZ=1000` and offers
two lifecycle choices: Arduino supplies `app_main()` and invokes `setup()` and
`loop()`, or project code supplies `app_main()` and calls `initArduino()`. The
current P4 configuration selects `CONFIG_AUTOSTART_ARDUINO=y`, core 1 and a
1,000-Hz FreeRTOS tick; retaining that lifecycle is the least behavioral change.

## Native build contracts

ESP-IDF's build system treats application code and libraries as CMake
components registered with `idf_component_register`. `SRCS` supplies an exact
source list, `INCLUDE_DIRS` and `PRIV_INCLUDE_DIRS` establish header visibility,
and `REQUIRES` or `PRIV_REQUIRES` declare component dependencies. Native CMake
produces `compile_commands.json`, project metadata, an ELF, flash images and a
linker map from the same build graph. This removes the present split where
CMake describes unused `.obj` nodes while SCons separately compiles and links
`.o` nodes.

[ESP-IDF 5.5.5 build-system documentation](https://docs.espressif.com/projects/esp-idf/en/v5.5.5/esp32p4/api-guides/build-system.html)
documents these component and artifact contracts. `SDKCONFIG_DEFAULTS` can name
one or more defaults files; later files take precedence. An explicit generated
`SDKCONFIG` path per build directory prevents one profile's effective values
from contaminating another profile.

The component manager reads `idf_component.yml`, resolves transitive
dependencies, downloads managed source and generates `dependencies.lock`.
Espressif documents that the lock contains exact versions and component hashes,
should not be hand-edited, and should be committed when dependencies are
registry or Git dependencies rather than machine-local Kconfig paths:

- [IDF Component Manager](https://docs.espressif.com/projects/esp-idf/en/latest/esp32/api-guides/tools/idf-component-manager.html)
- [`dependencies.lock` reference](https://docs.espressif.com/projects/idf-component-manager/en/latest/reference/dependencies_lock.html)

ESP-IDF exposes the `DEPENDENCIES_LOCK` build property before `project()`, so
the project can bind a checked-in lock to the selected profile. BUILD-001 should
use one lock for each materially different managed dependency closure rather
than allow builds to rewrite one shared lock.

## Tool acquisition and isolation

ESP-IDF 5.5.5's official tools installer reads the release's `tools/tools.json`
and installs its declared compiler, CMake, Ninja and related tools. The
`IDF_TOOLS_PATH` variable places that state outside the default user-global
directory, and the installer can create a matching Python environment. The
project wrapper should set a project-scoped tools path and invoke the exact
pinned ESP-IDF checkout instead of sourcing an operator's ambient environment.

Source: [ESP-IDF 5.5.5 downloadable tools](https://docs.espressif.com/projects/esp-idf/en/v5.5.5/esp32p4/api-guides/tools/idf-tools.html).

The source acquisition itself also needs an immutable identity. The design
therefore pins the official ESP-IDF `v5.5.5` tag plus its resolved commit and
submodule identities, and pins Arduino-ESP32 exactly as registry component
`espressif/arduino-esp32==3.3.11`. The generated component lock records the
registry archive's component hash. A separately retained cache may support
offline builds, but the cache is not an authority and must validate against the
locks before use.

## Conclusions for B01-01

B01-R01 [x] Arduino-ESP32 3.3.11 can be retained as a managed ESP-IDF component;
its declared IDF range includes 5.5.5 and its target set includes ESP32-P4.

B01-R02 [x] Preserve Arduino autostart, core affinity and the 1,000-Hz tick in
the first native build. Changing to a project-owned `app_main()` is a separate
lifecycle change with no migration benefit.

B01-R03 [x] Pin ESP-IDF source and tools independently: the IDF tag/commit and
submodules define framework source, while the release's tools metadata and a
project-scoped `IDF_TOOLS_PATH` define executable tools.

B01-R04 [x] Declare Arduino and the existing selected managed dependencies in
the application component manifest. Commit solver-generated profile lock files
and validate that their component versions and hashes match the accepted
closure.

B01-R05 [x] Give every profile its own build directory, effective `sdkconfig`
and dependency lock. Reusing generated configuration across profiles is not
permitted.

B01-R06 [x] Treat native `compile_commands.json` as canonical only after a
validator proves that its project translation units correspond to the objects
actually linked into the ELF. Native CMake makes that proof tractable but does
not eliminate the need to perform it.

## Known limits

The latest Arduino documentation currently illustrates 3.3.12, not the pinned
3.3.11. The registry's exact 3.3.11 metadata is therefore the version-specific
compatibility authority used here. The first native dependency solve must be
compared with the retained P4 lock because adding Arduino as a managed component
can make transitive dependencies explicit that PlatformIO previously supplied
through its framework package.

No fresh-machine installation, offline-cache reconstruction, native build or
hardware behavior was tested during B01-01. Those remain B01-04 through B01-06.
