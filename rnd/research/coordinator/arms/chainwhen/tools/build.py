#!/usr/bin/env python3
"""CHAINWHEN build (criterion adba95cb, 0 LLM): 150 RELGATE contexts -> D4 prompts exactly as PACKREAD build.py (style prefix + reminder swapped,
context byte-identical) = OFF; ON only for triggered items (G3 argmax from relgate/runs/m4.jsonl):
  pick > 1 -> picked source moved to [1], others renumbered in order; pick = 0 -> one note line appended to the user turn.
Skips: health packs (boar-firstaid-en, boar-medlineplus-en, qa-health-se) and n_src <= 2 (ON = OFF).
Writes ../data/prompts.jsonl, ../data/plan.json, ../data/ids-150.ids, ../data/ids-on.ids, ../data/renumber-examples.json, and the bench slice
boar-eval/bench/slices/chainwhen-v1 (questions + refs copied verbatim from bench/selftest/<pack>).
Usage: python3 -I build.py"""
import json, os, re, sys, hashlib, glob, collections
ROOT = "<workspace>"; ARMS = f"{ROOT}/rnd/research/coordinator/arms"; H = f"{ARMS}/chainwhen"
sys.path.insert(0, f"{H}/tools"); from prompts_lib import ARMS as PARMS
A = PARMS["D4"]; CUT = " You are BOAR, an offline AI research app"
HEALTH = {"boar-firstaid-en", "boar-medlineplus-en", "qa-health-se"}
NOTE = "Note: the offline sources above may not contain the answer. If they do not, say so plainly and give only what you are sure of."
CTX = "\n\nContext:\n"

def split_ctx(sysm):  # same split as relgate/tools/build_sets.py split_context
    i = sysm.find(CTX); ctx = sysm[i + len(CTX):]
    parts = re.split(r"(?:^|\n\n)\[(\d+)\] ", ctx)
    assert parts[0] == "", parts[0][:80]
    ch = [(int(parts[k]), parts[k + 1]) for k in range(1, len(parts), 2)]
    assert [n for n, _ in ch] == list(range(1, len(ch) + 1))
    assert sysm[:i] + CTX + "\n\n".join(f"[{n}] {b}" for n, b in ch) == sysm, "roundtrip"
    return sysm[:i], ch

def renumber(sysm, pick):
    head, ch = split_ctx(sysm); bodies = [b for _, b in ch]
    order = [pick - 1] + [k for k in range(len(bodies)) if k != pick - 1]
    return head + CTX + "\n\n".join(f"[{n + 1}] {bodies[k]}" for n, k in enumerate(order)), order

K = [json.loads(l) for l in open(f"{ARMS}/relgate/data/contexts.jsonl")]
G3 = {json.loads(l)["key"]: json.loads(l) for l in open(f"{ARMS}/relgate/runs/m4.jsonl") if '"G3"' in l}
G3 = {k: v for k, v in G3.items() if v["kind"] == "G3"}
SRC = {}
for f in glob.glob(f"{ARMS}/headpass-st/gen-x2b/st-*-cut7-headpassx2b-s42.prompts.jsonl"):
    pack = os.path.basename(f)[3:].split("-cut7")[0]
    Q = {json.loads(l)["question"]: json.loads(l)["id"] for l in open(f"{ROOT}/boar-eval/bench/selftest/{pack}/questions.jsonl")}
    for l in open(f):
        p = json.loads(l); SRC[Q[p["query"]]] = p["prompt"]
expl = {r["i"]: r for r in json.load(open(f"{H}/exploratory-g3rows.json"))}

rows, plan, ex = [], [], []
for k in sorted(K, key=lambda r: r["id"]):
    iid = k["id"]; pr = k["prompt"]
    assert pr == SRC[iid], f"context differs from source: {iid}"  # kill_if (as PACKREAD): context byte-identical to the engine prompt
    assert len(pr) == 2 and pr[0]["role"] == "system" and pr[1]["role"] == "user"
    sysm, user = pr[0]["content"], pr[1]["content"]
    i = sysm.index(CUT); j = user.rindex("\n\n(Response style:")
    sys_off = A["sys"] + A["ci"] + sysm[i:]; user_off = user[:j] + "\n\n(Response style: " + A["rem"] + ")"
    assert sys_off.endswith(sysm[sysm.index(CTX):])
    off = [{"role": "system", "content": sys_off}, {"role": "user", "content": user_off}]
    d = G3[f"{iid}|G3"]["digits"]; N = k["n_src"]
    pick = max(range(0, N + 1), key=lambda x: d.get(str(x), 0))  # argmax over the valid answers 0..n_src
    assert len(split_ctx(sysm)[1]) == N
    if k["pack"] in HEALTH: branch = "skip-health"
    elif N <= 2: branch = "skip-nsrc"
    elif pick == 1: branch = "pick1"
    elif pick == 0: branch = "pick0"
    else: branch = "pick>1"
    state = "no-fact" if not k["pos_nums"] else ("fact@1" if 1 in k["pos_nums"] else "fact-elsewhere")
    p = dict(id=iid, pack=k["pack"], n_src=N, pick=pick, branch=branch, state=state, pos_nums=k["pos_nums"],
             pick_is_fact=pick in k["pos_nums"], expl_pick=expl.get(iid, {}).get("pick"))
    rows.append(dict(id=iid, pack=k["pack"], arm="OFF", branch=branch, pick=pick, messages=off))
    if branch == "pick>1":
        new_sys, order = renumber(sys_off, pick)
        on = [{"role": "system", "content": new_sys}, {"role": "user", "content": user_off}]; p["order"] = [o + 1 for o in order]
        if len(ex) < 2:
            ex.append(dict(id=iid, pick=pick, before=sys_off[sys_off.index(CTX):], after=new_sys[new_sys.index(CTX):]))
    elif branch == "pick0":
        on = [off[0], {"role": "user", "content": user_off + "\n" + NOTE}]
    else:
        on = None
    if on:
        assert on != off
        rows.append(dict(id=iid, pack=k["pack"], arm="ON", branch=branch, pick=pick, messages=on))
    plan.append(p)

D = f"{H}/data"; os.makedirs(D, exist_ok=True)
open(f"{D}/prompts.jsonl", "w").write("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows))
open(f"{D}/ids-150.ids", "w").write("".join(p["id"] + "\n" for p in plan))
open(f"{D}/ids-on.ids", "w").write("".join(p["id"] + "\n" for p in plan if p["branch"] in ("pick>1", "pick0")))
json.dump(plan, open(f"{D}/plan.json", "w"), indent=0)
json.dump(ex, open(f"{D}/renumber-examples.json", "w"), indent=1, ensure_ascii=False)
c = collections.Counter(p["branch"] for p in plan)
print("items", len(plan), "gens", len(rows), dict(c))
print("pick vs exploratory pick agree", sum(p["pick"] == p["expl_pick"] for p in plan), "/", len(plan))
print("pick>1 by state", dict(collections.Counter(p["state"] for p in plan if p["branch"] == "pick>1")),
      "pick0 by state", dict(collections.Counter(p["state"] for p in plan if p["branch"] == "pick0")))

# bench slice: questions + refs copied verbatim from the per-pack self-tests
SL = f"{ROOT}/boar-eval/bench/slices/chainwhen-v1"; os.makedirs(f"{SL}/refs", exist_ok=True)
ids = [p["id"] for p in plan]; packs = sorted({p["pack"] for p in plan}); ql, rl = {}, {}
for pk in packs:
    for l in open(f"{ROOT}/boar-eval/bench/selftest/{pk}/questions.jsonl"): ql[json.loads(l)["id"]] = l if l.endswith("\n") else l + "\n"
    for l in open(f"{ROOT}/boar-eval/bench/selftest/{pk}/refs/refs.jsonl"): rl[json.loads(l)["id"]] = l if l.endswith("\n") else l + "\n"
qs = "".join(ql[i] for i in ids); rs = "".join(rl[i] for i in ids)
open(f"{SL}/questions.jsonl", "w").write(qs); open(f"{SL}/refs/refs.jsonl", "w").write(rs)
sha = lambda s: hashlib.sha256(s.encode()).hexdigest()
json.dump({"bench": "slice-chainwhen-v1", "questions": "questions.jsonl", "refs": "refs/refs.jsonl",
           "_note": "CHAINWHEN (rnd arms/chainwhen, criterion adba95cb): the 150 RELGATE contexts (9 pack self-tests with a cut7+X2b engine context); questions and refs copied verbatim from bench/selftest/<pack>; dev only"},
          open(f"{SL}/bench.json", "w"), indent=1)
json.dump({"bench": "slice-chainwhen-v1", "frozen": True, "n_items": len(ids), "n_ok": sum(json.loads(rl[i]).get("ok") is True for i in ids),
           "questions_sha256": sha(qs), "jsonl_sha256": sha(rs), "sources": [f"bench/selftest/{p}" for p in packs]}, open(f"{SL}/refs/MANIFEST.json", "w"), indent=1)
print("slice", SL, len(ids), "refs ok", sum(json.loads(rl[i]).get("ok") is True for i in ids))
