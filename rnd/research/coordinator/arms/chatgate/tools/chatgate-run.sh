#!/usr/bin/env bash
# CHATGATE: dev chat slices v0/v1/v2 (192 messages, history = earlier turns via item.history, as the adapter's multi-turn path / answerContext),
# cut 5 tree (be-0cfd4a77-cut5lite, CUT5-LITE patch 3b7a0dfa...), committed adapter deployed as be-repo, BOAR_RUNNER_PROFILE=ship (gate + detector on),
# node backend, seed 44, one pass, heavy lock. No judge, no blind/veil.
set -uo pipefail
B=<workspace>; E=$B/boar-eval; OUT=$E/runs/kiln/chatgate; C=$B/rnd/research/compass/chat-slice
MD=<runner>/shared-models/emergency-detector; P=<runner>/shared-data/poi/kit-vexact
mkdir -p $OUT; export HEAVY_CLASS=normal BOAR_EVAL_RUNNER_DIR=be-repo
PLACES=$P/world-places.sqlite,$P/t-N52E013.sqlite,$P/t-N38W010.sqlite,$P/t-N35E139.sqlite,$P/t-N35E140.sqlite
python3 - $C $OUT <<'PY'
import json, sys
C, OUT = sys.argv[1:3]
cfg = {"commit": "0cfd4a77", "arm": "cut5lite", "modelId": "qwen3-4b-instruct-2507-q4km", "settings": {"quickFirst": True, "alwaysComplete": False},
       "kit": [{"id": "boar-crypto", "sha256": "ae9fbd2c7a46a46a815d46d0283e7b192adb4c342b38a2adc4881e8f9d8831fb"}, {"id": "boar-wikivoyage-en", "sha256": "ff8595e32f56b8b84e20464afd8bf88532d47d2d82d799e3df8489440004b66e"}],
       "device": {"platform": "android", "ramGb": 12.0}, "seed": 44}
out = []
for p in ("slice.v0.jsonl", "v1-fresh/slice.v1.jsonl", "v2-fresh/slice.v2.jsonl"):
    for l in open(f"{C}/{p}"):
        r = json.loads(l)
        item = {"id": r["id"], "question": r["turns"][-1]["text"], "lang": r["lang"]}
        if len(r["turns"]) > 1: item["history"] = {"turns": [{"role": t["role"], "text": t["text"]} for t in r["turns"][:-1]]}
        out.append({"protocol": "1.0.0", "runId": "chatgate-s44", "item": item, "config": cfg, "seed": 44})
open(f"{OUT}/chatgate-s44.requests.jsonl", "w").write("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in out))
print(len(out), "requests")
PY
if ! <on the mini> "curl -sf http://127.0.0.1:8094/health" >/dev/null 2>&1; then
  <on the mini> "bash -c 'cd $MD && shasum -a 256 -c SHA256SUMS >/dev/null && nohup <runner>/spikes/llama-b11010/build-cpu/bin/llama-server -m $MD/sonar-mmbert-small-emergency-v3b-q8te4.gguf --embeddings --pooling mean -np 1 -t 2 -c 512 -b 512 -ub 512 --host 127.0.0.1 --port 8094 > <runner>/kiln/detector-8094.log 2>&1 < /dev/null &'" & SSHP=$!
  for i in $(seq 1 60); do <on the mini> "curl -sf http://127.0.0.1:8094/health" >/dev/null 2>&1 && break; sleep 2; done; kill $SSHP 2>/dev/null
fi
<on the mini> "curl -sf http://127.0.0.1:8094/health" >/dev/null 2>&1 && echo "detector up" || { echo "DETECTOR DOWN"; exit 1; }
echo "free before: $(<on the mini> "df -g ~ | awk 'NR==2{print \$4}'") GiB"
l=chatgate-s44
BOAR_RUNNER_PROFILE=ship BOAR_DETECTOR=mmbert BOAR_DETECTOR_URL=http://127.0.0.1:8094 BOAR_DETECTOR_HEAD=$MD/sonar-mmbert-small-emergency-v3b.head.json \
  $E/adapters/desktop-node/run.sh --commit 0cfd4a77 --arm cut5lite --requests $OUT/$l.requests.jsonl --out $OUT/$l.traces.jsonl --places $PLACES > $OUT/$l.runsh.out 2>&1
echo "$l rc=$? $(date +%H:%M) $(tail -1 $OUT/$l.runsh.out | cut -c1-120)"
<on the mini> "rm -rf <runner>/kiln/be-0cfd4a77-cut5lite/be-repo/runs/$l"
echo 'p=$(lsof -tiTCP:8094 -sTCP:LISTEN); [ -n "$p" ] && kill $p; echo detector stopped' | <on the mini> bash -s
echo "free after: $(<on the mini> "df -g ~ | awk 'NR==2{print \$4}'") GiB"
echo CHATGATE-GEN-DONE
