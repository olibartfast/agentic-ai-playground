#!/usr/bin/env bash
# Probe OpenCode free-model reachability without polluting session history.
#
# Usage:
#   ./probe-free-models.sh [model-id ...]
#
# Accepts bare IDs or full opencode/<id> references. Prints MODEL, STATUS, and
# DETAIL columns. Does not modify configuration.

set -uo pipefail

timeout_s="${PROBE_TIMEOUT:-90}"
models=("$@")

if [ "${#models[@]}" -eq 0 ]; then
  models=(
    deepseek-v4.1-flash-free
    glm-5.3-flash-free
    minimax-m3.1-flash-free
    nemotron-3.5-super-vl-free
    nemotron-3.5-lightning-free
    nemotron-3-ultra-free
    longcat-2.5-free
    flint-40b-free
    beam-free
    mimo-v2.6-flash-free
    iceman-free
    big-pickle
    inkling-2-small-free
  )
fi

if ! command -v opencode >/dev/null 2>&1; then
  echo "opencode not found in PATH" >&2
  exit 127
fi

strip_ansi() {
  sed -E 's/\x1b\[[0-9;]*[A-Za-z]//g'
}

printf '%-38s %-14s %s\n' "MODEL" "STATUS" "DETAIL"

for raw in "${models[@]}"; do
  case "$raw" in
    opencode/*) id="$raw" ;;
    *) id="opencode/$raw" ;;
  esac

  out="$(timeout "$timeout_s" opencode run --archived --model "$id" \
    "Reply with exactly: OK" 2>&1)"
  rc=$?

  if [ "$rc" -eq 124 ]; then
    status="timeout"
    detail="no response in ${timeout_s}s"
  elif printf '%s' "$out" | grep -q 'Model unavailable'; then
    status="unavailable"
    detail="not in runtime catalog or not entitled"
  elif printf '%s' "$out" | grep -qi 'not available in your country'; then
    status="geo-blocked"
    detail="region restriction"
  elif [ "$rc" -eq 0 ]; then
    status="reachable"
    detail="probe completed"
  else
    status="error"
    detail="$(printf '%s\n' "$out" | strip_ansi | tail -n 1)"
  fi

  printf '%-38s %-14s %s\n' "$id" "$status" "$detail"
done
