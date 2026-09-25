#!/bin/bash
# Retained 100 ms Pi pulse, parameterized for local configuration.
# Requires the commissioned transistor circuit; do not guess GPIO selection.
set -euo pipefail
chip=${1:?gpiochip name required}
gpio=${2:?GPIO number required}
[[ $chip =~ ^gpiochip[0-9]+$ && $gpio =~ ^[0-9]+$ && $gpio -le 53 ]] || exit 2
trap 'pinctrl set "$gpio" ip pd' EXIT
trap 'exit 130' INT
trap 'exit 143' TERM HUP
timeout --kill-after=1s 2s gpioset -c "$chip" -C agon-reset -b pull-down -t 100ms,0 "$gpio=1"
pinctrl set "$gpio" ip pd
