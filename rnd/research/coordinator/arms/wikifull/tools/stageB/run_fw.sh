#!/bin/bash
cd <runner>/kiln/packs/builder
printf "%s\n" 05 06 07 08 09 10 11 12 13 14 | xargs -P 1 -I{} /opt/homebrew/bin/node scripts/wikifullb_fw_ids.mjs <runner>/kiln/wikifull-b/work/fw {}
echo ALLDONE
