#!/bin/bash
# FOTAPOL onboarding smoke: 5 K0 screen items (3 problems + 2 sentinels, the first of each list), LoRA then plain, sequential on the mini (gen slot lock).
D=<workspace>/rnd/research/coordinator/arms/fotapol-lora
OUT_BASE=$D/smoke bash $D/tools/gen_only.sh fotapol-smoke K0 $D/smoke/smoke5.ids $D/fotapol.env || exit 1
OUT_BASE=$D/smoke bash $D/tools/gen_only.sh plain-smoke K0 $D/smoke/smoke5.ids none
