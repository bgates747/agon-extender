#!/usr/bin/env bash
# This file exists because the repository-local PlatformIO executable is above
# the actual project directory. PlatformIO project-selection options belong to
# particular subcommands and are not reliably accepted as global options, so
# the wrapper changes to vdp/ and otherwise passes the command through intact.
# See docs/decisions/ADR-0009-platformio-wrapper.md.
set -euo pipefail

repo_root=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
pio="$repo_root/.venv/bin/pio"
project="$repo_root/vdp"
config="$project/platformio.ini"
expected_arduino_version="3.3.11"
expected_arduino_archive="https://github.com/espressif/arduino-esp32/releases/download/3.3.11/esp32-core-3.3.11.tar.xz"

if [[ ! -x "$pio" ]]; then
  echo "PlatformIO is unavailable at $pio" >&2
  echo "Install it in the project-local .venv before continuing." >&2
  exit 1
fi

if [[ ! -f "$config" ]]; then
  echo "VDP PlatformIO configuration is unavailable at $config" >&2
  exit 1
fi

# pioarduino 55.03.311 may install the selected 3.3.11 archive under a
# content-addressed package directory only for the duration of dependency
# resolution, while an unrelated registry Arduino 2.x package occupies the
# canonical global path. Neither that path nor `pio pkg list` reliably reports
# the package that the next run will select. Fail closed if the tracked target
# loses its exact archive pin; the Phase F post-link validator separately
# proves that the resulting image identifies Arduino 3.3.11.
if [[ ${1:-} == "run" ]]; then
  if ! grep -Fq "$expected_arduino_archive" "$config"; then
    echo "The P4 target no longer pins the required Arduino framework $expected_arduino_version archive." >&2
    echo "Restore the reviewed archive pin before building; do not accept PlatformIO's registry fallback." >&2
    exit 1
  fi
fi

printf 'PlatformIO: %s\nProject: %s\n' "$pio" "$project" >&2
cd -- "$project"
exec "$pio" "$@"
