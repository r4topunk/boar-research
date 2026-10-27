#!/bin/bash
# usage: conv-se.sh <site> <pack-id>   (converts dl/<site>.stackexchange.com.7z -> work/<pack-id>)
set -euo pipefail
export PATH=/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin
cd <runner>/kiln/packs
site=$1; id=$2
shasum -a 256 dl/$site.stackexchange.com.7z
s=$(date +%s)
node convert/convert.mjs stackexchange dl/$site.stackexchange.com.7z --out work/$id 2>&1 | tail -5
echo "convert seconds: $(( $(date +%s) - s ))"
node convert/validate.mjs work/$id
ls -la work/$id
