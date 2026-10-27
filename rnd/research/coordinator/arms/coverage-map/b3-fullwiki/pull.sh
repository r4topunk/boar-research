#!/bin/bash
W=<workspace>/rnd/research/coordinator/arms/coverage-map/b3-fullwiki
rsync -a --include='main.B3_*' --exclude='*' MINI_HOST:boar/kiln/b3/replay/ $W/replay/
rsync -a --include='pool.*.json' --exclude='*' MINI_HOST:boar/kiln/b3/out/ $W/pool/
rsync -a --include='pool.*.log' --exclude='*' MINI_HOST:boar/kiln/b3/logs/ $W/logs/
rsync -a MINI_HOST:boar/kiln/b3/logs/run.log $W/logs/run.log
