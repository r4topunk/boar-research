#!/usr/bin/env python3
"""R3 judge inputs (0 LLM; never prints item or answer text). judge.mjs traces per arm x seed from the generations:
  NATIVE-RC: work/v04/native-s<S>.jsonl (harness conv: answer = shown text; multi-turn '[Turn k]' blocks). No warning line, no refusal path (z = 0).
  ENGINE-RC: work/v04/engine-fetched/s<S>/out/t<k>/traces.jsonl. Per turn: the warning line (a first line ending "From the model's memory, may be wrong:")
             is stripped and logged (spec 3.1); refusal z per turn = answer.declined or the engine's fixed health decline (text starts
             "I don't have a reliable offline source"); multi-turn: '[Turn k]' blocks, a refused turn keeps its text and is marked ' [declined]' (spec 6.3);
             item z = 1 iff every turn refused (spec 2.1).
Writes work/v04/traces/<arm>-s<S>.traces.jsonl + aggregates/r3-gen.json (counts: z, warned, kept per turn, tokens, wall, recap-routed turns).
usage: python3 -I r3_traces.py"""
import json, os, glob, re, hashlib
A = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); V = A + "/work/v04"
rd = lambda f: [json.loads(l) for l in open(f) if l.strip()]
Q = {r["id"]: r for r in rd(V + "/bench/questions.jsonl")}
WARN = re.compile(r"^[^\n]*From the model's memory, may be wrong:\s*\n?")
REFUSE = "I don't have a reliable offline source"
os.makedirs(V + "/traces", exist_ok=True); stats = {}
def write(arm, S, rows):
    p = f"{V}/traces/{arm}-s{S}.traces.jsonl"
    open(p, "w").write("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows))
    return hashlib.sha256(open(p, "rb").read()).hexdigest()
for S in (42, 43):
    f = f"{V}/native-s{S}.jsonl"
    if os.path.exists(f):
        R = rd(f); rows = []
        for r in R:
            rows.append(dict(itemId=r["id"], runId=f"nrc-v04-native-s{S}", answer=dict(text=r["answer"]), error=None if r["answer"].strip() else "empty answer",
                             engine=dict(arm=f"NATIVE-RC-s{S}", commit="f1023b93"),
                             ruler=dict(kept=all(t["keptN"] > 0 for t in r["turns"]), keptTurns=[t["keptN"] > 0 for t in r["turns"]], refusedZ=False, warningLine=False,
                                        nTurns=r["nTurns"], tokens=[t["tokens_predicted"] for t in r["turns"]], wall=[t["wall_s"] for t in r["turns"]],
                                        recapRoute=[t["recapRoute"] for t in r["turns"]], capHit=[t["stopped_limit"] for t in r["turns"]])))
        stats[f"NATIVE-RC-s{S}"] = dict(n=len(rows), sha=write("native", S, rows), z=0, warned=0, kept_items=sum(r["ruler"]["kept"] for r in rows),
                                        recap_turns=sum(sum(r["ruler"]["recapRoute"]) for r in rows), cap_hits=sum(sum(r["ruler"]["capHit"]) for r in rows),
                                        empty=sum(bool(r["error"]) for r in rows), tok_p50=sorted(t for r in rows for t in r["ruler"]["tokens"])[len([1 for r in rows for t in r["ruler"]["tokens"]]) // 2])
    D = f"{V}/engine-fetched/s{S}/out"
    if os.path.exists(D + "/t1/traces.jsonl"):
        T = {}
        for k in (1, 2, 3):
            if os.path.exists(f"{D}/t{k}/traces.jsonl"):
                for t in rd(f"{D}/t{k}/traces.jsonl"): T.setdefault(t["itemId"], {})[k] = t
        rows = []; warned_turns = 0; ref_turns = 0
        for i in Q:
            turns = [T[i][k] for k in sorted(T.get(i, {}))]
            parts = []; zs = []; ws = []; kept = []; err = None
            for t in turns:
                a = t.get("answer") or {}; text = a.get("text") or ""
                m = WARN.match(text); w = bool(m); text = text[m.end():] if m else text
                z = bool(a.get("declined")) or text.strip().startswith(REFUSE)
                zs.append(z); ws.append(w); kept.append(bool((t.get("retrieval") or {}).get("kept"))); parts.append(text.strip())
                if t.get("error"): err = str(t["error"])[:200]
            warned_turns += sum(ws); ref_turns += sum(zs)
            n = len(Q[i]["question"].split("[Turn ")) - 1 if Q[i]["multiTurn"] else 1
            if len(turns) != n: err = err or f"turns {len(turns)} of {n}"
            ans = parts[0] if n == 1 and parts else "\n\n".join(f"[Turn {k + 1}]\n{p}{' [declined]' if zs[k] and n > 1 else ''}" for k, p in enumerate(parts))
            rows.append(dict(itemId=i, runId=f"nrc-v04-engine-s{S}", answer=dict(text=ans), error=err if err else (None if ans.strip() else "empty answer"),
                             engine=dict(arm=f"ENGINE-RC-s{S}", commit="rs-RC"),
                             ruler=dict(kept=all(kept) if kept else False, keptTurns=kept, refusedZ=bool(zs) and all(zs), refusedTurns=zs, warningLine=any(ws), warnedTurns=ws, nTurns=len(turns),
                                        tokens=[(t.get("timing") or {}).get("outputTokens") for t in turns], totalMs=[(t.get("timing") or {}).get("totalMs") for t in turns])))
        stats[f"ENGINE-RC-s{S}"] = dict(n=len(rows), sha=write("engine", S, rows), z=sum(r["ruler"]["refusedZ"] for r in rows), refused_turns=ref_turns, warned_turns=warned_turns,
                                        warned_items=sum(r["ruler"]["warningLine"] for r in rows), kept_items=sum(r["ruler"]["kept"] for r in rows), errors=sum(bool(r["error"]) for r in rows))
json.dump(stats, open(A + "/aggregates/r3-gen.json", "w"), indent=1); print(json.dumps(stats, indent=1))
