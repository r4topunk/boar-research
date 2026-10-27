#!/usr/bin/env python3
"""LOCALGATE candidate 2: Laya (noul) on the same sample. NOT YET RUN (install pending r4to's own OK).
Run with the localgate venv:  ../.venv/bin/python -I laya_gate.py --form A|B --type has_fact|quote_supports
  A = full jev state {rationale_1, rationale_2, text}, truncated by laya to the checkpoint's max_len (printed from config).
  B = compact: missing-fact sentences heuristically extracted from the rationales (cue-word filter, <= 120 words) + chunk text,
      max_len 512. Same instruction + criteria wording as jev. Never prints state text.
Writes blind/localgate/laya<form>-<type>.jsonl {rid, type, p_local, ms}; then: analyze.py --engine qwen --engine layaA --engine layaB
"""
import argparse, json, re, sys, time
sys.path.insert(0, __import__("os").path.dirname(__import__("os").path.abspath(__file__)))
D = "<private held-out dir>"
Q = {
 "has_fact": ("Does `text` state the specific fact, figure, name, step or mechanism that `rationale_1` or `rationale_2` say the system answer is missing?",
   {"true": "`text` contains the concrete content (fact, figure, name, step or mechanism) the judge says the answer lacks",
    "false": "`text` is about something else, only touches the topic in general terms, or lacks the specific content the judge says is missing"}),
 "quote_supports": ("Does `text` contain, in its own words, the specific value, name, date or step that `rationale_1` or `rationale_2` say is missing or wrong in the system answer, not merely the topic?",
   {"true": "`text` states the concrete value, name, date or step itself",
    "false": "`text` only discusses the topic, or lacks the specific value, name, date or step"}),
}
QB = {t: (i.replace("`rationale_1` or `rationale_2` say", "`missing` says").replace("the judge says", "`missing` says"),
          {k: v.replace("the judge says", "`missing` says") for k, v in c.items()}) for t, (i, c) in Q.items()}
CUE = re.compile(r"\b(miss(es|ing)?|lack(s|ing)?|omit(s|ted)?|absent|does(n't| not) (mention|state|give|include|name|explain|provide)|fail(s|ed)? to|should (have|include|mention)|wrong|incorrect|inaccurate|actually|in fact|correct (answer|value|figure)|reference (answer )?(says|states|gives|includes))\b", re.I)
def compact(st):
    sents = [s.strip() for r in (st.get("rationale_1", ""), st.get("rationale_2", "")) for s in re.split(r"(?<=[.!?])\s+", r or "") if s.strip()]
    keep = [s for s in sents if CUE.search(s)] or sents[:2]
    words = " ".join(dict.fromkeys(keep)).split()[:120]
    return {"missing": " ".join(words), "text": st.get("text", "")}
ap = argparse.ArgumentParser(); ap.add_argument("--form", choices=["A", "B"], required=True); ap.add_argument("--type", required=True, choices=list(Q))
ap.add_argument("--checkpoint", default="english"); ap.add_argument("--batch", type=int, default=16); a = ap.parse_args()
from laya import Router
router = Router(max_loaded=1)
rows = [json.loads(l) for l in open(f"{D}/sample.jsonl")]; rows = [r for r in rows if r["type"] == a.type]
ins, crit = (Q if a.form == "A" else QB)[a.type]
qs = {"q": {"type": "noul", "instructions": ins, "criteria": crit}}
reqs = [{"state": (r["state"] if a.form == "A" else compact(r["state"])), "questions": qs, "model": a.checkpoint, **({"max_len": 512} if a.form == "B" else {})} for r in rows]
router.predict({"x": "warm-up"}, qs, model=a.checkpoint)
try:
    ag = router._agents if hasattr(router, "_agents") else None
    print("checkpoint", a.checkpoint, "config max_len:", getattr(next(iter(ag.values())), "max_len", "n/a") if ag else "see router config")
except Exception: print("checkpoint", a.checkpoint, "max_len: unknown")
t0 = time.time(); res = router.predict_batch(reqs, batch_size=a.batch); dt = time.time() - t0
ms = round(1000 * dt / max(1, len(rows)))
with open(f"{D}/laya{a.form}-{a.type}.jsonl", "w") as fo:
    for r, x in zip(rows, res): fo.write(json.dumps(dict(rid=r["rid"], type=a.type, p_local=float(x["answers"]["q"]["noul"]), ms=ms)) + "\n")
print(json.dumps(dict(form=a.form, type=a.type, n=len(rows), seconds=round(dt, 1), req_per_s=round(len(rows) / dt, 2))))
