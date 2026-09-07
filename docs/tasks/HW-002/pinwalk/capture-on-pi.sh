#!/usr/bin/env bash
# Pi-side capture only: no GPIO output, processor reset, or firmware operation.
set -euo pipefail
run_dir=${1:?run directory required}
mode=${2:-capture}
scan=$(sigrok-cli --driver fx2lafw --scan)
printf '%s\n' "$scan"
mapfile -t devices < <(sed -n 's/^\(fx2lafw[^ ]*\) - .*/\1/p' <<<"$scan")
((${#devices[@]} == 1)) || { echo 'Expected exactly one fx2 analyzer.' >&2; exit 1; }
[[ "$mode" == check ]] && exit 0
mkdir "$run_dir"
{
    date -u --iso-8601=seconds
    sigrok-cli --version
    printf '%s\n' "$scan"
    printf 'samplerate_hz=100000\nsamples=6000000\nchannels=D0,D1,D2,D3,D4,D5,D6,D7\n'
} > "$run_dir/capture-environment.txt" 2>&1
sigrok-cli --driver "${devices[0]}" --config samplerate=100000 \
    --channels D0,D1,D2,D3,D4,D5,D6,D7 --samples 6000000 \
    --output-file "$run_dir/logic.sr" > "$run_dir/sigrok.log" 2>&1 &
pid=$!
trap 'kill "$pid" 2>/dev/null || true' EXIT
sleep 1
kill -0 "$pid" || { cat "$run_dir/sigrok.log" >&2; exit 1; }
printf '\nCapture process is running. Reset the Agon NOW, within 20 seconds.\n'
printf 'The boot fixture waits about five seconds, emits one walk, and returns to MOS.\n'
printf 'Do not reset it again during this 60-second capture.\n\n'
set +e
wait "$pid"
rc=$?
set -e
trap - EXIT
printf '%s\n' "$rc" > "$run_dir/capture-exit-code.txt"
(
    cd "$run_dir"
    sha256sum capture-environment.txt sigrok.log capture-exit-code.txt > SHA256SUMS
    if [[ -f logic.sr ]]; then sha256sum logic.sr >> SHA256SUMS; fi
)
exit "$rc"
