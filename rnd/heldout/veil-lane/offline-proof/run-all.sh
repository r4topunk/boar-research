#!/usr/bin/env bash
# Reproduce the reference audit: 2 competitors + 3 local BOAR test builds (+ the published BOAR release), with controls.
# Negative controls (must be NO-NETWORK-BY-CONSTRUCTION): a competitor team, a competitor team, BOAR offline.
# Positive controls (must be NETWORK-CAPABLE): BOAR downloader, BOAR main release, BOAR published v1.0.0.
# Release gate: every PUBLISHED/distributed APK must NOT be signed with an Android debug / public key.
# Determinism: a second run must produce byte-identical JSON.
#
#   bash run-all.sh                       # local set only
#   FETCH_PUBLISHED=1 bash run-all.sh     # also downloads UPSTREAM_REPO/boar-app v1.0.0 (123 MB, temp dir, deleted after)
#   PUBLISHED_APK=/path/boar.apk bash run-all.sh
set -euo pipefail
here=$(cd "$(dirname "$0")" && pwd)
boar=${BOAR_ROOT:-$(cd "$here/../../.." && pwd)}
out=${OUT:-$here/reports}
tag=${PUBLISHED_TAG:-v1.0.0}

dl=""
if [[ "${FETCH_PUBLISHED:-0}" == 1 && -z "${PUBLISHED_APK:-}" ]]; then
  dl=$(mktemp -d)
  gh release download "$tag" -R UPSTREAM_REPO/boar-app -p '*.apk' -p '*.sha256' -D "$dl"
  (cd "$dl" && shasum -a 256 -c ./*.sha256)
  PUBLISHED_APK=$(ls "$dl"/*.apk | head -1)
fi
trap '[[ -n "$dl" ]] && rm -rf "$dl"' EXIT

declare -a apks=(
  "$boar/competitors/competitor-a-1.0.0.apk|NO-NETWORK-BY-CONSTRUCTION"
  "$boar/competitors/<competitor-b-artifacts>/competitor-b-1.1.10.apk|NO-NETWORK-BY-CONSTRUCTION"
  "$boar/builds/android/boar-integration-1928502d-offline-arm64.apk|NO-NETWORK-BY-CONSTRUCTION"
  "$boar/builds/android/boar-integration-b7e31b7-downloader-arm64.apk|NETWORK-CAPABLE"
  "$boar/builds/android/boar-main-9898b35-release-arm64.apk|NETWORK-CAPABLE"
)
[[ -n "${PUBLISHED_APK:-}" ]] && apks+=("$PUBLISHED_APK|NETWORK-CAPABLE")
paths=(); for e in "${apks[@]}"; do paths+=("${e%%|*}"); done

python3 "$here/audit_apk.py" "${paths[@]}" --out "$out" || true   # exit 1 is expected (positive controls)

fail=0
for e in "${apks[@]}"; do
  p=${e%%|*}; want=${e##*|}; stem=$(basename "$p" .apk)
  got=$(python3 -c 'import json,sys;print(json.load(open(sys.argv[1]))["verdict"])' "$out/$stem.json")
  if [[ "$got" == "$want" ]]; then echo "ok   $stem: $got"; else echo "FAIL $stem: got '$got', want '$want'"; fail=1; fi
done

# Release gate (fail-closed): the distributed APK must carry the project's own key, never CN=Android Debug.
if [[ -n "${PUBLISHED_APK:-}" ]]; then
  if python3 "$here/audit_apk.py" "$PUBLISHED_APK" --out "$(mktemp -d)" --require-release-key >/dev/null 2>&1 || [[ $? -ne 3 ]]; then
    echo "ok   release gate: $(basename "$PUBLISHED_APK") is not debug/public-key signed"
  else
    echo "FAIL release gate: $(basename "$PUBLISHED_APK") is signed with a debug/public key"; fail=1
  fi
else
  echo "skip release gate (no PUBLISHED_APK; set FETCH_PUBLISHED=1)"
fi

tmp=$(mktemp -d)
python3 "$here/audit_apk.py" "${paths[@]}" --out "$tmp" >/dev/null 2>&1 || true
for p in "${paths[@]}"; do
  stem=$(basename "$p" .apk)
  cmp -s "$out/$stem.json" "$tmp/$stem.json" || { echo "FAIL non-deterministic: $stem"; fail=1; }
done
rm -rf "$tmp"
[[ $fail -eq 0 ]] && echo "RESULT: controls pass, output deterministic" || { echo "RESULT: FAIL"; exit 1; }
