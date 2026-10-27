#!/usr/bin/env python3
"""RULER-FINAL judge inputs (0 LLM; never prints item or answer text): work/v04/lite-s42.jsonl (harness-lite conv) -> work/v04/traces/lite-s42.traces.jsonl.
Per turn: path (calc / calc-model / exposure / health-fixed / model). Refusal z per turn = health-fixed (HealthGate's fixed safe text = the RC's fixed
refusal string); item z iff every turn refused (spec 2.1); in multi-turn items a refused turn keeps its text and is marked ' [declined]' (spec 6.3).
The AnswerNote line is drawn by the chat under model-written answers, never inside the text: logged (warningLine), nothing stripped.
usage: python3 -I rf_traces.py -> + aggregates/rf-gen.json"""
import json, os, hashlib, collections
A = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); V = A + "/work/v04"
rd = lambda f: [json.loads(l) for l in open(f) if l.strip()]
rows = []; paths = collections.Counter()
for r in rd(V + "/lite-s42.jsonl"):
    ts = r["turns"]; zs = [t["path"] == "health-fixed" for t in ts]; paths.update(t["path"] for t in ts)
    ans = ts[0]["shownText"] if len(ts) == 1 else "\n\n".join(f"[Turn {t['turn']}]\n{t['shownText']}{' [declined]' if z else ''}" for t, z in zip(ts, zs))
    rows.append(dict(itemId=r["id"], runId="nrc-v04-lite-b4ef94f3-s42", answer=dict(text=ans), error=None if ans.strip() else "empty answer",
                     engine=dict(arm="BOARLITE-b4ef94f3-s42", commit="b4ef94f3"),
                     ruler=dict(kept=all(t["keptN"] > 0 for t in ts), keptTurns=[t["keptN"] > 0 for t in ts], refusedZ=all(zs), refusedTurns=zs,
                                warningLine=any(t.get("answerNote") for t in ts), paths=[t["path"] for t in ts], portTurns=[t.get("portTurn") for t in ts],
                                appended=[t.get("appendedN", 0) for t in ts], nTurns=len(ts), tokens=[t.get("tokens_predicted") for t in ts],
                                capHit=[t.get("stopped_limit") for t in ts], recapRoute=[t.get("recapRoute") for t in ts])))
os.makedirs(V + "/traces", exist_ok=True); p = V + "/traces/lite-s42.traces.jsonl"
open(p, "w").write("".join(json.dumps(x, ensure_ascii=False) + "\n" for x in rows))
st = dict(n=len(rows), sha=hashlib.sha256(open(p, "rb").read()).hexdigest(), turn_paths=dict(paths), z_items=sum(x["ruler"]["refusedZ"] for x in rows),
          refused_turns=sum(sum(x["ruler"]["refusedTurns"]) for x in rows), kept_items=sum(x["ruler"]["kept"] for x in rows),
          note_items=sum(x["ruler"]["warningLine"] for x in rows), port_turns=sum(bool(t) for x in rows for t in x["ruler"]["portTurns"]),
          appended_turns=sum(a > 0 for x in rows for a in x["ruler"]["appended"]), cap_hits=sum(bool(c) for x in rows for c in x["ruler"]["capHit"]),
          recap_turns=sum(bool(c) for x in rows for c in x["ruler"]["recapRoute"]), empty=sum(bool(x["error"]) for x in rows))
json.dump(st, open(A + "/aggregates/rf-gen.json", "w"), indent=1); print(json.dumps(st, indent=1))
