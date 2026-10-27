#!/bin/bash
# References v2, Codex half (F2). Run by r4to on the MacBook with his ChatGPT CLI login. bash run-codex.sh check|pilot|all|status
set -euo pipefail
cd "$(dirname "$0")"
unset OPENAI_API_KEY OPENAI_BASE_URL
want_crit=$(cat REFS-V2-criterion.sha256 | cut -d' ' -f1)
have_crit=$(shasum -a 256 REFS-V2-criterion.md | cut -d' ' -f1)
[ "$want_crit" = "$have_crit" ] || { echo "x criterion sha mismatch"; exit 2; }
grep -q 72d274c2070ed33538011cd0bef95307d3d1e515b9111df3430b1850d88f0edf REFS-V2-criterion.md
[ "$(shasum -a 256 tools/gen_refs_v2.mjs | cut -d' ' -f1)" = 72d274c2070ed33538011cd0bef95307d3d1e515b9111df3430b1850d88f0edf ] || { echo "x generator sha mismatch"; exit 2; }
command -v codex >/dev/null || { echo "x codex not on PATH"; exit 2; }
case "${1:-}" in
  check)  codex --version; codex login status; node tools/gen_refs_v2.mjs --family codex --dry-run ;;
  pilot)  node tools/gen_refs_v2.mjs --family codex --conc 1 --ids "$(head -1 pilot.ids)" ;;
  all)    node tools/gen_refs_v2.mjs --family codex --conc "${CONC:-2}" 2>&1 | tee -a gen-codex.log ;;
  status) node tools/gen_refs_v2.mjs --family codex --dry-run; python3 -I tools/check_refs_v2.py codex || true ;;
  *) echo "usage: bash run-codex.sh check|pilot|all|status"; exit 1 ;;
esac
