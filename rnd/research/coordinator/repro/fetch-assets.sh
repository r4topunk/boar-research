#!/usr/bin/env bash
# Download (or just check with --check) the public assets of the BOAR claim build and verify size + sha256.
# Layout under ${BOAR_EVAL_BASE_DIR} (default $HOME/boar) matches the runner defaults, so no extra env vars are needed:
#   shared-models/                      the two GGUFs (+ emergency-detector/ if you have it, see BOM.md)
#   shared-data/packs/                  boar-wikivoyage-en.sqlite
#   shared-data/crypto/                 boar-crypto.sqlite
# Usage: fetch-assets.sh [--check] [--places] [--deep]
#   --check   HEAD requests only (no download); compares Content-Length with the expected size
#   --places  also the optional places kit (world-places + 9 area tiles, ~43 MB)
#   --deep    also the deep research model Qwen3.6-35B-A3B (12.3 GB)
set -euo pipefail
BASE="${BOAR_EVAL_BASE_DIR:-$HOME/boar}"; CHECK=0; PLACES=0; DEEP=0
for a in "$@"; do case "$a" in --check) CHECK=1;; --places) PLACES=1;; --deep) DEEP=1;; *) echo "unknown $a" >&2; exit 2;; esac; done
HF=https://huggingface.co
PK=$HF/datasets/r4topunk/boar-packs/resolve
# dest|url|bytes|sha256
ROWS=(
"shared-models/Qwen3-4B-Instruct-2507-Q4_K_M.gguf|$HF/unsloth/Qwen3-4B-Instruct-2507-GGUF/resolve/a06e946bb6b655725eafa393f4a9745d460374c9/Qwen3-4B-Instruct-2507-Q4_K_M.gguf|2497281120|3605803b982cb64aead44f6c1b2ae36e3acdb41d8e46c8a94c6533bc4c67e597"
"shared-models/bge-small-en-v1.5-q8_0.gguf|$HF/CompendiumLabs/bge-small-en-v1.5-gguf/resolve/d32f8c040ea3b516330eeb75b72bcc2d3a780ab7/bge-small-en-v1.5-q8_0.gguf|36806944|ec38e8da142596baa913124ae50550de284b6916bf59577ef2f0cb9660c2f514"
"shared-data/crypto/boar-crypto.sqlite|$PK/a55c1ec8a5fe8bbda99c4197c33474637bef1958/topics/boar-crypto.sqlite|36093952|ae9fbd2c7a46a46a815d46d0283e7b192adb4c342b38a2adc4881e8f9d8831fb"
"shared-data/packs/boar-wikivoyage-en.sqlite|$PK/9557c7b2a50a1c37fdf36d41db4cd0fdc8c33c0b/wiki/en/boar-wikivoyage-en.sqlite|351092736|ff8595e32f56b8b84e20464afd8bf88532d47d2d82d799e3df8489440004b66e"
)
[[ $PLACES == 1 ]] && ROWS+=(
"shared-data/places-kit/world-places.sqlite|$PK/0d75f30fc9d439a7b4e3685c6fcd5a34236f33f6/places/world-places.sqlite|22962176|215ce4663b2f79dbf25e9cacab90cd8aa0a8711721663a733cb53bc49d972892"
"shared-data/places-kit/t-N35E139.sqlite|$PK/0d75f30fc9d439a7b4e3685c6fcd5a34236f33f6/places/tiles/t-N35E139.sqlite|9900032|8fcd37b72ae7dba42c6a2370d38e5bf298d18555dfc2fbb49ab02394d7ed06ad"
"shared-data/places-kit/t-N35E140.sqlite|$PK/0d75f30fc9d439a7b4e3685c6fcd5a34236f33f6/places/tiles/t-N35E140.sqlite|663552|2cb90347fa86e9fdea9caf5435400bc11919b7f483e92245cb21d3bef30cbaf0"
"shared-data/places-kit/t-N38W010.sqlite|$PK/0d75f30fc9d439a7b4e3685c6fcd5a34236f33f6/places/tiles/t-N38W010.sqlite|1781760|45b508b5103740385249d184d30c2ba1640fb10ef5d49fa6f923fa299da86e80"
"shared-data/places-kit/t-N39W001.sqlite|$PK/0d75f30fc9d439a7b4e3685c6fcd5a34236f33f6/places/tiles/t-N39W001.sqlite|1093632|63400daccad2d117e3a862f197d124677dbea847735c23bfc1798594b0945710"
"shared-data/places-kit/t-N41E044.sqlite|$PK/0d75f30fc9d439a7b4e3685c6fcd5a34236f33f6/places/tiles/t-N41E044.sqlite|585728|a492031adcdcb3503d7bfeb4c54f152b4a48140c8389f84b47515088cc63e173"
"shared-data/places-kit/t-N46E014.sqlite|$PK/0d75f30fc9d439a7b4e3685c6fcd5a34236f33f6/places/tiles/t-N46E014.sqlite|724992|269ea2889ea3849c69b0c7b99da1496e2b45ccaf21a000f8b0a70894a79a5014"
"shared-data/places-kit/t-N50E019.sqlite|$PK/0d75f30fc9d439a7b4e3685c6fcd5a34236f33f6/places/tiles/t-N50E019.sqlite|1040384|bea75d9be0c80ab7b920e246e8c03ae5600e31e4b38aa91913e59eecfa974500"
"shared-data/places-kit/t-N52E013.sqlite|$PK/0d75f30fc9d439a7b4e3685c6fcd5a34236f33f6/places/tiles/t-N52E013.sqlite|3706880|0accffdf1c50070b4fbf26194694903bc16682ed17fe596fc03b3590943b5d11"
"shared-data/places-kit/t-S14W072.sqlite|$PK/0d75f30fc9d439a7b4e3685c6fcd5a34236f33f6/places/tiles/t-S14W072.sqlite|208896|b6f769d6fc652bb5241386d53ba42ec8eed0736e0e701639213a6c66cf8433c2"
)
[[ $DEEP == 1 ]] && ROWS+=("shared-models/Qwen3.6-35B-A3B-UD-Q2_K_XL.gguf|$HF/unsloth/Qwen3.6-35B-A3B-GGUF/resolve/a483e9e6cbd595906af30beda3187c2663a1118c/Qwen3.6-35B-A3B-UD-Q2_K_XL.gguf|12290628576|96b9c0af5c77a4ecaabe3983175112b5ece763261c1ece12b2494b692a70dad7")
rc=0
for row in "${ROWS[@]}"; do
  IFS='|' read -r dest url bytes sha <<< "$row"; f="$BASE/$dest"
  if [[ $CHECK == 1 ]]; then
    len="$(curl -sIL "$url" | awk 'tolower($1)=="content-length:"{l=$2} END{gsub("\r","",l); print l}')"
    [[ "$len" == "$bytes" ]] && echo "OK    $dest (HEAD size $bytes)" || { echo "DIFF  $dest (HEAD $len, expected $bytes)"; rc=1; }
    continue
  fi
  mkdir -p "$(dirname "$f")"
  if [[ -f "$f" ]] && [[ "$(shasum -a 256 "$f" | cut -d' ' -f1)" == "$sha" ]]; then echo "have  $dest"; continue; fi
  curl -fL --retry 3 -o "$f.part" "$url"
  got="$(shasum -a 256 "$f.part" | cut -d' ' -f1)"
  if [[ "$got" == "$sha" ]]; then mv "$f.part" "$f"; echo "ok    $dest"; else rm -f "$f.part"; echo "SHA MISMATCH $dest got $got" >&2; rc=1; fi
done
exit $rc
