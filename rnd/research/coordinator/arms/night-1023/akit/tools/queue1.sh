#!/bin/bash
D=<workspace>/rnd/research/coordinator/arms/night-1023/akit
bash $D/tools/run_kit.sh KSE <workspace>/shared-data/packs/v3proto/qa-ethereum-se.sqlite,<workspace>/shared-data/packs/v3proto/qa-bitcoin-se.sqlite
bash $D/tools/run_kit.sh KSEN <workspace>/shared-data/packs/v3proto/qa-ethereum-se.sqlite,<workspace>/shared-data/packs/v3proto/qa-bitcoin-se.sqlite,<workspace>/shared-data/packs/wave4/boar-nist-crypto.sqlite
echo Q1DONE
