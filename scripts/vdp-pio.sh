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

if [[ ! -x "$pio" ]]; then
  echo "PlatformIO is unavailable at $pio" >&2
  echo "Install it in the project-local .venv before continuing." >&2
  exit 1
fi

if [[ ! -f "$config" ]]; then
  echo "VDP PlatformIO configuration is unavailable at $config" >&2
  exit 1
fi

printf 'PlatformIO: %s\nProject: %s\n' "$pio" "$project" >&2
cd -- "$project"
exec "$pio" "$@"
