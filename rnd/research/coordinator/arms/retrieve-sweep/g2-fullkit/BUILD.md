# G2-FULLKIT step 1: v3 sidecar builds (2026-10-22, mini M4, Metal, 0 LLM / 0 judge / 0 paid / 0 phone)

Script: mini/g2_sidecars.sh (copy at mini <runner>/kiln/g2_sidecars.sh; logs <runner>/kiln/g2-fullkit/{sidecars.log,sidecars.sha256,STATUS}). Adapted from kiln/headpass-x2/rebuild_sidecars.sh:
same lib (headpass-x2/lib, embedding.mjs 04ddbd4e = kp-lib b02832f9 = the 10-13 wt/packcond shas, checked at start), same sidecar_embed.mini.mjs (diffed vs arms/densechunk-st/tools/sidecar_embed.mjs:
only the BOAR_ROOT / BOAR_SIDECAR_LIB / BOAR_SIDECAR_CACHE path lines differ), tsx = be-0cfd4a77-cut7 repo, model bge-small-en-v1.5-q8_0 sha ec38e8da (checked), BOAR_EMBED_GPU=metal (the mini tool runs Metal, ~190-220 chunks/s).
Command: `<on the mini> 'cd <runner>/kiln; nohup bash g2_sidecars.sh > g2-fullkit/run.out 2>&1 < /dev/null &'` (PATH needs /opt/homebrew/bin: the first launch died on "env: node" and was restarted, no output lost).
Disk: mini 32 GiB free before, 31 after (floor 25).

| pack | chunks | build wall (mini) | v2 sha (source, unchanged) | v3 sha | v2 bytes | v3 bytes | delta |
|---|---|---|---|---|---|---|---|
| boar-visa-en | 10,830 | 60 s | d1dd0ffb58a8 | 2d6544045e97 | 11,231,232 | 11,657,216 | +3.8 % |
| boar-crypto | 54,998 | 284 s | ae9fbd2c7a46 | d1d3495df777 | 36,093,952 | 55,255,040 | +53.1 % |
| boar-wikivoyage-en | 548,051 | 2,464 s (222/s) | ff8595e32f56 | a183367ab835 | 351,092,736 | 575,864,832 | +64.0 % |
Total 2,808 s. The sidecar is a flat 388 B/chunk (int8 vec 384 + scale 4), so the byte cost scales with chunk count over pack size: wikivoyage +64 % (the criterion's +20...+25 % prediction was wrong; 548k x 388 B = 213 MB on a 351 MB pack).

Verification (verify_v3.py, verify.json; read-only, run on the MacBook copies): chunk_vecs rows = chunks rows = source chunks rows for all three (10,830 / 54,998 / 548,051), 0 chunks without a vector, 0 rows with len != 384 or scale <= 0,
meta embeddingModelSha256 identical to the source (ec38e8da1425), the only meta difference is the added key densechunk = bge-small-int8-v1, source pack sha recorded in sidecars.sha256 (mini) and verify.json.
Copy: scp mini -> MacBook shared-data/packs/v3proto/ ; sha256 equal on both sides for all three (2d654404..., d1d3495d..., a183367a...). Manifests written beside them (<pack>.sqlite.json); the stale 10-13 crypto/wikivoyage manifests were renamed *.stale-10-13.
Caches left on the mini: shared-data/packs/work/densechunk/{boar-visa-en,boar-crypto,boar-wikivoyage-en}.{i8,scales.f32,ids.i32} (sidecar rebuild is then seconds).
