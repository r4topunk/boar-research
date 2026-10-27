"""G1-SWA5 readout (0 LLM, 0 judge). Reads the three phone result dirs and applies the frozen criterion
(arms/g1-swa5/G1-SWA5-criterion.md).
  python3 -I compare_swa5.py [results_dir] [--json out.json]
results_dir default: <workspace>/handoff/pixel8-2026-10-20/bench/results (expects swa5-g-default, swa5-g-full,
swa5-q17-default with rows.jsonl, bench.json, logcat.txt as boar_bench.py pulls them).
Per turn: error markers (row error/timeout/outcome error), empty answer, garbled flag, tier/route, and for Gemma the
first-32-token identity default vs full (tokens = whitespace-split words of the answer text: the bench keeps no token
ids; documented proxy). Per run: logcat markers (same patterns as step 0), session wiring check (sessionLog history
messages = 2 x (turn - 1)), prompt tokens per completion."""
import json, re, sys, pathlib
B = pathlib.Path("<workspace>")
args = [a for a in sys.argv[1:] if not a.startswith("--")]
RES = pathlib.Path(args[0]) if args else B / "handoff/pixel8-2026-10-20/bench/results"
JOUT = sys.argv[sys.argv.index("--json") + 1] if "--json" in sys.argv else None
IDS = [l.strip() for l in open(B / "rnd/research/coordinator/ruler/ids/swa5.ids") if l.strip() and not l.startswith("#")]
ARMS = ["swa5-g-default", "swa5-g-full", "swa5-q17-default"]
N_TOK = 32
LOG_PATS = {
    "memory_slot": re.compile(r"memory slot", re.I),
    "llama_decode": re.compile(r"llama_decode"),
    "kv_error": re.compile(r"(?=.*kv)(?=.*(error|fail))", re.I),
    "decode_failed": re.compile(r"failed to decode|decode.*failed", re.I),
}

def garbled(t):
    if not t: return False
    bad = sum(1 for c in t if c == "�" or (ord(c) < 32 and c not in "\n\t\r"))
    if bad / len(t) >= 0.05: return True
    w = t.split(); grams = {}
    for i in range(len(w) - 3):
        g = tuple(w[i:i + 4]); grams[g] = grams.get(g, 0) + 1
    return max(grams.values(), default=0) >= 4

def load(rid):
    d = RES / rid
    if not (d / "rows.jsonl").exists(): return None
    rows = {}
    for l in (d / "rows.jsonl").read_text(encoding="utf-8", errors="replace").splitlines():
        if l.strip():
            r = json.loads(l); rows[r["queryId"]] = r  # answeredAnyway re-asks are rejected in sessions
    bench = json.loads((d / "bench.json").read_text() or "{}") if (d / "bench.json").exists() else {}
    log = (d / "logcat.txt").read_text(encoding="utf-8", errors="replace") if (d / "logcat.txt").exists() else ""
    marks = {k: sum(1 for ln in log.splitlines() if p.search(ln)) for k, p in LOG_PATS.items()}
    slog = {s["id"]: s for s in bench.get("sessionLog") or []}
    turns = []
    for i in IDS:
        r = rows.get(i); s = slog.get(i, {})
        txt = (r or {}).get("answer") or ""
        tn = int(i.rsplit("-t", 1)[1])
        err = r is None or bool(r.get("error")) or bool(r.get("timedOut")) or r.get("outcome") in ("error", "failed")
        turns.append({"id": i, "turn": tn, "present": r is not None, "error": err, "empty": r is not None and not txt.strip(),
                      "garbled": garbled(txt), "tier": (r or {}).get("tier"), "tokensGenerated": (r or {}).get("tokensGenerated"),
                      "historyMessages": s.get("historyMessages"), "wired": s.get("historyMessages") == 2 * (tn - 1),
                      "head": txt.split()[:N_TOK], "text": txt})
    return {"rid": rid, "turns": turns, "logMarkers": marks, "engine": bench.get("engine", {}).get("treeHash", "")[:12],
            "overrides": bench.get("engineOverrides"), "llamaInits": bench.get("llamaInits"),
            "promptN": [c.get("promptN") for c in bench.get("completions") or []]}

R = {a: load(a) for a in ARMS}
missing = [a for a in ARMS if R[a] is None]
if missing: print("MISSING result dirs:", ", ".join(missing))
out = {"arms": {}, "verdict": None}
for a in ARMS:
    x = R[a]
    if not x: continue
    t = x["turns"]
    s = {"markers_rows": sum(r["error"] for r in t), "empty": sum(r["empty"] for r in t), "garbled": sum(r["garbled"] for r in t),
         "logMarkers": x["logMarkers"], "wired": f"{sum(r['wired'] for r in t)}/{len(t)}", "engine": x["engine"],
         "swa_full_applied": [i.get("applied", {}).get("swa_full") for i in (x["llamaInits"] or [])]}
    out["arms"][a] = s
    print(f"{a}: tree {s['engine']} wired {s['wired']} row-markers {s['markers_rows']} empty {s['empty']} garbled {s['garbled']} log {s['logMarkers']} swa_full {s['swa_full_applied']}")
    for r in t:
        print(f"  {r['id']} tier={r['tier']} tok={r['tokensGenerated']} hist={r['historyMessages']} err={int(r['error'])} empty={int(r['empty'])} garbled={int(r['garbled'])} | {' '.join(r['head'][:12])}")
if R["swa5-g-default"] and R["swa5-g-full"]:
    D = {r["id"]: r for r in R["swa5-g-default"]["turns"]}; F = {r["id"]: r for r in R["swa5-g-full"]["turns"]}
    t1 = [i for i in IDS if i.endswith("-t1")]; later = [i for i in IDS if not i.endswith("-t1")]
    t1_same = sum(D[i]["head"] == F[i]["head"] for i in t1)
    same = sum(D[i]["head"] == F[i]["head"] for i in later)
    # Descriptive (pre-declared): divergence onsets = turns that differ at 32 tokens although every earlier turn of the
    # session had byte-identical full answer text in both arms (identical history -> identical prompt).
    onsets = 0
    for sess in sorted({i.rsplit("-t", 1)[0] for i in IDS}):
        ids = [i for i in IDS if i.startswith(sess + "-t")]
        for k, i in enumerate(ids):
            if k and all(D[j]["text"] == F[j]["text"] for j in ids[:k]) and D[i]["head"] != F[i]["head"]: onsets += 1
    print(f"identity @{N_TOK} words: turn 1 {t1_same}/{len(t1)}, turns 2-5 {same}/{len(later)} (divergent {len(later) - same}); onsets with identical history {onsets}")
    g = out["arms"]["swa5-g-default"]
    hits = g["markers_rows"] + g["empty"] + g["garbled"] + sum(g["logMarkers"].values())
    q = out["arms"].get("swa5-q17-default")
    qhits = None if q is None else q["markers_rows"] + q["empty"] + q["garbled"] + sum(q["logMarkers"].values())
    wired_ok = all(out["arms"][a]["wired"] == f"{len(IDS)}/{len(IDS)}" for a in out["arms"])
    void_identity = t1_same < len(t1)
    div = len(later) - same
    if not wired_ok:
        verdict = "INVALID (session history not wired on every turn: rerun with a fresh requestId)"
    elif hits >= 1 or (not void_identity and div >= 2 and qhits == 0):
        verdict = "CONFIRMED (bug bites): NOTE-3 requires swa_full:true or llama.rn >= rc.7; tier single-turn until fixed"
    elif hits == 0 and (void_identity or same >= 7):
        verdict = "KILLED (5-turn sessions clean on rc.4)" + (" [identity clause VOID: turn 1 differs, markers decided]" if void_identity else "")
    else:
        verdict = "INCONCLUSIVE (no marker, divergence %d/8 without a clean 1.7B control or between the clauses)" % div
    out.update(identity={"turn1_same": t1_same, "later_same": same, "later_n": len(later), "onsets": onsets, "void": void_identity},
               gemma_hits=hits, q17_hits=qhits, verdict=verdict)
    print("VERDICT:", verdict)
if JOUT:
    for a in out["arms"]: pass
    pathlib.Path(JOUT).write_text(json.dumps({**out, "turns": {a: [{k: v for k, v in r.items() if k != "head"} for r in R[a]["turns"]] for a in ARMS if R[a]}}, indent=1))
