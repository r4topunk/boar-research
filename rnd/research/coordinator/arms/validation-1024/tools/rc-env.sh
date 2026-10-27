#!/bin/bash
# ENGINE-RC environment (VALIDATION 2026-10-24). Source it:  . rc-env.sh   (bash or zsh). Exports the exact env, kit and settings ENGINE-RC uses.
# RC_BOAR = workspace root (default the MacBook path; on the mini set RC_BOAR=<runner>/kiln-like root that holds kiln-local/, shared-data/, rnd/ with
# the same relative layout: kiln-local/rs-RC, kiln-local/w78pf-packs/*, kiln-local/shape-packs/shaped/boar-factbook.sqlite, the w78 sidecars dirs).
# ENGINE-RC = kiln-local/rs-RC = rs-SEFIX + W78-BINARY + W78B-DENSE + W78C-DENSE + W78-PACKFMT + bannerkept (see ../V0-V1-V3L1.md for shas).
RC_BOAR=${RC_BOAR:-<workspace>}
RC_ARMS=$RC_BOAR/rnd/research/coordinator/arms
export RC_TREE=$RC_BOAR/kiln-local/rs-RC
# SEFIX-124 search stack (and these two must be UNSET: RS_HEALTH_NOSOURCE_FALLBACK, RS_STICKY)
unset RS_HEALTH_NOSOURCE_FALLBACK RS_STICKY RS_X2B_BUDGET RS_RB_K RS_RB_COMPRESS RS_RB_CAP RS_DENSE_IVF RS_DENSE_Q RS_DENSE_QN
export RS_MERGE=gidf RS_SE_LEAD=0.78 RS_SE_MAXDF=0.25 RS_KEEP_NOPROPER=1
# W78 reading-cost stack, W78-PACKFMT PF32 arm: F1 lead through the binary path (32), stage-1 dense through the in-pack IVF lists (nprobe 32)
export RS_SE_LEAD_BIN=32 RS_SE_LEAD_BIN_DIR=$RC_ARMS/coverage-map/w78/sidecars RS_DENSE_Q_DIR=$RC_ARMS/coverage-map/w78/sidecars-c RS_DENSE_IVFP=32
# Kit = K13 (compose/tools/kits.py 10) with simplewiki + travel -> kiln-local/w78pf-packs (lead_ivf tables) and boar-factbook -> shaped v2
V3=$RC_BOAR/shared-data/packs/v3proto
export RC_PACKS="$RC_BOAR/shared-data/crypto/boar-crypto.sqlite,$RC_BOAR/shared-data/packs/boar-wikivoyage-en.sqlite,$RC_BOAR/kiln-local/w78pf-packs/boar-simplewiki-en.sqlite,$RC_BOAR/shared-data/packs/wave3/qa-cooking-se.sqlite,$RC_BOAR/shared-data/packs/wave3/qa-money-se.sqlite,$RC_BOAR/kiln-local/shape-packs/shaped/boar-factbook.sqlite,$V3/boar-medlineplus-en.sqlite,$V3/boar-firstaid-en.sqlite,$RC_BOAR/shared-data/packs/wave4/boar-visa-en.sqlite,$V3/qa-health-se.sqlite,$RC_BOAR/kiln-local/w78pf-packs/qa-travel-se.sqlite,$V3/qa-outdoors-se.sqlite,$RC_BOAR/shared-data/packs/wiki-vital5.sqlite"
# Settings: Succinct persona (the default id; retrieval ignores it, the app prompt uses it), Deep off (alwaysComplete false), quickFirst, head pass a2, X2b append-budget
export RC_SETTINGS='{"quickFirst":true,"alwaysComplete":false,"packHeadPass":"a2","packDense2":"append-budget","personalityId":"succinct"}'
export RC_MODEL=qwen3-1.7b-q4km
# NOT in ENGINE-RC: X2B-BUDGET, RETBENCH knobs (RS_RB_*), engfix-1023 route fixes (wt/engfix lineage).
