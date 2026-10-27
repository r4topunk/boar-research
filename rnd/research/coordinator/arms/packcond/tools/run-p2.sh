#!/usr/bin/env bash
# PACKCOND P2: gate (jev, cap $0.38) -> replay (0 LLM, outputs under blind/) -> report. Run from anywhere.
set -euo pipefail
T="$(cd "$(dirname "$0")" && pwd)"
python3 "$T/packcond_p2.py" gate "$@"
python3 "$T/packcond_p2.py" replay
python3 "$T/packcond_p2.py" report
