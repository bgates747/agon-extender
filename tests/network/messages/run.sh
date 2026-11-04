#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../../.."
exec .venv/bin/python tests/network/messages/run.py --output "${1:?supply a fresh evidence directory}"
