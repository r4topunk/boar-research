#!/usr/bin/env python3
"""Card-condition mismatch check, feasibility on emergency-dev (Compass, 2026-10-03). For each positive dev item: the gold
card (its `cond`, if a card key) + the two health11 wrong-card confusions (altitude, chokinginfant) + one seeded random key;
Jev answers one boolean per pair "is this card the right one for this conversation?". Ground truth: gold = match, others
= mismatch; `other:*` items have no right card (all mismatch). Disk cache keyed by request hash. Run: python3 jev_pairs.py"""
import hashlib, json, os, random, sys, time, urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
H = Path(__file__).resolve().parent; C = H / "cache"; C.mkdir(exist_ok=True)
DEV = H.parent / "emergency-dev/dev.jsonl"; CARDS = json.load(open(H.parent / "first-aid-cards/conditionCards.v1.json"))["cards"]
KEYS = list(CARDS)
INSTR = ("Is the first-aid card `card` the right card to show for the situation described in `conversation` "
         "(the latest user message, in the context of the earlier ones)?")
CRIT = {"true": "The card's condition is the person's condition, or a closely related one whose steps are still correct and not harmful here.",
        "false": "The card is about a different condition, or a different kind of patient (for example an infant card for an adult), or its steps would be wrong, irrelevant or harmful for this situation."}
def ask(state, qs):
    body = json.dumps({"model": "typesafe-ai/jev", "state": state, "questions": qs}, ensure_ascii=False, sort_keys=True).encode()
    f = C / (hashlib.sha256(body).hexdigest() + ".json")
    if f.exists(): return json.load(open(f))
    for a in range(6):
        try:
            r = urllib.request.Request("https://ai-gateway.vercel.sh/v1/evaluate", data=body, headers={"authorization": "Bearer " + os.environ["VERCEL_AI_GATEWAY"], "content-type": "application/json"})
            out = json.load(urllib.request.urlopen(r, timeout=60)); json.dump(out, open(f, "w")); return out
        except Exception as e:
            time.sleep(min(8, 2 ** a))
    raise RuntimeError("jev failed")
rows = []
for l in open(DEV):
    r = json.loads(l)
    if r["emergency"] != 1: continue
    rnd = random.Random(r["id"])
    gold = r["cond"] if r["cond"] in CARDS else None
    cands = ([gold] if gold else []) + [k for k in ("altitude", "chokinginfant") if k != gold]
    cands.append(rnd.choice([k for k in KEYS if k not in cands]))
    rows.append((r, gold, cands))
def run(item):
    r, gold, cands = item
    conv = "\n".join(("User: " if t["role"] == "user" else "Assistant: ") + t["text"] for t in r["turns"])
    out = {}
    for k in cands:  # one question per request: the state carries one card, so no indexing into a list
        res = ask({"conversation": conv, "card": CARDS[k]["en"]}, {"right": {"type": "boolean", "instructions": INSTR, "criteria": CRIT}})
        out[k] = res["answers"]["right"]["probability"]
    return r["id"], gold, out
with ThreadPoolExecutor(8) as ex: res = list(ex.map(run, rows))
json.dump(res, open(H / "pairs.json", "w"), indent=0, ensure_ascii=False)
print("items", len(res), "pairs", sum(len(o) for _, _, o in res))
