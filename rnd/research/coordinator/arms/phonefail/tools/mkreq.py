"""PHONEFAIL request maker (0 LLM calls). Config = the pr1+warn tree (kiln-local/be-cut7-warn, commit 8ac9eb7a = wt/pr1 HEAD; WARN unset -> deps.warn off,
no NUMGUARD switch in this adapter -> deps.numguard off, as in the app's answerService), modelId qwen3-4b-instruct-2507-q4km, seed 42,
kit = claim kit (boar-crypto + boar-wikivoyage-en) + boar-firstaid-en + boar-simplewiki-en + boar-factbook (published shas).
  wave1: python3 -I mkreq.py wave1 <probes> <out>        -> every probe without 'prev' + the follow-up turns 2 standalone (id suffix -solo)
  wave2: python3 -I mkreq.py wave2 <probes> <out> <wave1 traces> -> probes with 'prev': history = [user prev question, assistant prev answer.text]
History format = the LONGSESSION adapter format (item.history.turns, role/text), the app's buildChatHistory window (<= 6 messages) holds it."""
import json, sys
KIT = [{"id": "boar-crypto", "sha256": "ae9fbd2c7a46a46a815d46d0283e7b192adb4c342b38a2adc4881e8f9d8831fb"},
       {"id": "boar-wikivoyage-en", "sha256": "ff8595e32f56b8b84e20464afd8bf88532d47d2d82d799e3df8489440004b66e"},
       {"id": "boar-firstaid-en", "sha256": "8cfab0b47ec8c5cb32840b24df1054c4df1a08d600d063c95c022c58eb5bf558"},
       {"id": "boar-factbook", "sha256": "c585435354a413d04790882c4e2263f725b1024c067febad3f2a99783e663447"},
       {"id": "boar-simplewiki-en", "sha256": "c751768b75f91258c896a131e49743c58609cceb711c6d8fdd713671c63adabe"}]
CFG = {"commit": "8ac9eb7a", "arm": "pr1+warn", "modelId": "qwen3-4b-instruct-2507-q4km", "settings": {"quickFirst": True, "alwaysComplete": False},
       "kit": KIT, "device": {"platform": "android", "ramGb": 12}}
mode, pp, out = sys.argv[1:4]
P = [json.loads(l) for l in open(pp) if l.strip()]; byid = {p["id"]: p for p in P}
def req(item, run): return {"protocol": "1.0.0", "runId": run, "item": item, "config": CFG, "seed": 42}
rows = []
if mode == "wave1":
    for p in P:
        if "prev" not in p: rows.append(req({"id": p["id"], "question": p["question"], "lang": "en"}, "phonefail-w1-s42"))
        elif p["cls"] == "followup": rows.append(req({"id": p["id"] + "-solo", "question": p["question"], "lang": "en"}, "phonefail-w1-s42"))
else:
    ans = {}
    for l in open(sys.argv[4]):
        t = json.loads(l)
        if not t.get("error"): ans[t["itemId"]] = (t.get("answer") or {}).get("text", "")
    for p in P:
        if "prev" not in p: continue
        a = ans.get(p["prev"], "").strip()
        if not a: sys.exit(f"missing answer for {p['prev']}")
        rows.append(req({"id": p["id"], "question": p["question"], "lang": "en",
                         "history": {"turns": [{"role": "user", "text": byid[p["prev"]]["question"]}, {"role": "assistant", "text": a}]}}, "phonefail-w2-s42"))
open(out, "w").write("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows)); print(mode, out, len(rows))
