#!/usr/bin/env python3
"""VALIDATION 2026-10-24 mini queue: request files for every generation job (0 LLM, MacBook). Run at GO time, after rc-env.sh is final:
    bash -c '. ../../tools/rc-env.sh; python3 -I mk_jobs.py'        (needs RC_PACKS and RC_SETTINGS from rc-env.sh)
Writes night/jobs/<job>/req/<NN>-<group>.requests.jsonl, night/jobs/<job>/job.json (tree, packdir, env, persona, reference), night/jobs.json (order).
ADDENDUM-1 section 4 order: V2 (S, S+ x ON/OFF) -> S4 MAIN s42, s43 -> V3 layer 2 (S, S+; two stages) -> S5 PACKPROOF ON/OFF -> S7 seed 44 -> S10 topics -> B-k4comp40 19.
RC kit = each template kit entry whose id is in RC_PACKS gets the RC file's sha256 (simplewiki + travel = w78pf, boar-factbook = shaped v2); ids outside
RC_PACKS (qa-bitcoin-se, qa-ethereum-se) keep their pinned sha. OFF groups keep their template's removals. B-k4comp40 keeps the SEFIX-124 kit (candidate vs SEFIX-124)."""
import json, os, hashlib, sys
A = "<workspace>/rnd/research/coordinator/arms"; VD = A + "/validation-1024"; N = VD + "/night"
rd = lambda f: [json.loads(l) for l in open(f) if l.strip()]
def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 22), b""): h.update(b)
    return h.hexdigest()
if not os.environ.get("RC_PACKS") or not os.environ.get("RC_SETTINGS"): sys.exit("source tools/rc-env.sh first (RC_PACKS, RC_SETTINGS)")
RCP = {os.path.basename(p)[:-7]: p for p in os.environ["RC_PACKS"].split(",")}
cache = N + "/rc-kit.json"; old = json.load(open(cache)) if os.path.exists(cache) else {}
RCK = {}
for i, p in RCP.items():
    st = os.stat(p); k = f"{p}|{st.st_size}|{int(st.st_mtime)}"
    RCK[i] = old[i]["sha256"] if i in old and old[i].get("key") == k else sha(p)
    old[i] = dict(path=p, key=k, sha256=RCK[i])
json.dump(old, open(cache, "w"), indent=1)
RCS = json.loads(os.environ["RC_SETTINGS"])
SP = json.load(open(VD + "/v2/personas/splus.json"))
PERS = {"S": None, "SP": {"personaSystemPrompt": SP["personaSystemPrompt"], "personaStyleReminder": SP["personaStyleReminder"]}}
def rc_req(r, job, group, persona, seed=None, rc=True):
    r = json.loads(json.dumps(r)); c = r["config"]
    if rc:
        c["kit"] = [dict(k, sha256=RCK.get(k["id"], k["sha256"])) for k in c["kit"]]
        s = dict(RCS)
        if persona:  # literal override is exclusive with personalityId (adapter rule)
            s.pop("personalityId", None); s.update(persona)
        c["settings"] = s; c["arm"] = "ENGINE-RC+v1024-" + job
    else:
        c["arm"] = c["arm"] + "+v1024-" + job
    if seed is not None: r["seed"] = seed
    r["runId"] = f"v1024-{job}-{group}"
    return r
JOBS = []
def job(name, groups, tree="rs-RC", packdir="packs-rc", env="rc", reference=None, stage2=None, persona="S", suite=""):
    d = f"{N}/jobs/{name}"; os.makedirs(d + "/req", exist_ok=True)
    for f in os.listdir(d + "/req"): os.remove(f"{d}/req/{f}")
    n = 0
    for gi, (g, rows) in enumerate(groups):
        assert all(x["config"] == rows[0]["config"] for x in rows), (name, g, "one config per file (numeric equality, as the adapter: 12 == 12.0)")
        open(f"{d}/req/{gi:02d}-{g}.requests.jsonl", "w").write("".join(json.dumps(x, ensure_ascii=False) + "\n" for x in rows)); n += len(rows)
    meta = dict(name=name, suite=suite, tree=tree, packdir=packdir, env=env, persona=persona, reference=reference, stage2=stage2,
                groups=[f"{gi:02d}-{g}" for gi, (g, _) in enumerate(groups)], n_requests=n + (stage2 or {}).get("n", 0))
    json.dump(meta, open(d + "/job.json", "w"), indent=1); JOBS.append(meta); return meta
# V2: UXMATRIX 60 items x ON/OFF (115 = 60 ON + 55 OFF; the 5 gen-nopack items have ON = OFF, as UXMATRIX) x S / S+
UXI = A + "/uxmatrix/in/succinct"; UXG = sorted(f[:-len(".requests.jsonl")] for f in os.listdir(UXI) if f.endswith(".requests.jsonl"))
UXG = ["on"] + [g for g in UXG if g != "on"]
for p, jn in (("S", "v2-s"), ("SP", "v2-splus")):
    job(jn, [(g, [rc_req(r, jn, g, PERS[p]) for r in rd(f"{UXI}/{g}.requests.jsonl")]) for g in UXG], persona=p, suite="V2",
        reference={"S": A + "/uxmatrix/gen/succinct", "SP": VD + "/night/fetched/v2-s"}[p])
# S4: MAIN 97 Succinct s42, s43 (reference = SEFIX-124 answer traces)
for s in (42, 43):
    jn = f"s4-main-s{s}"
    job(jn, [("main", [rc_req(r, jn, "main", None) for r in rd(f"{A}/coverage-map/sefix/ans-req/sefix124-main-s{s}.requests.jsonl")])], suite="S4",
        reference=f"{A}/coverage-map/sefix/ans-traces/sefix124-main-s{s}.traces.jsonl")
# V3 layer 2: stage 1 = the 48 turn-1 questions (F0); stage 2 (built ON THE MINI from stage-1 traces by v3_stage2.py) = the 48 follow-ups with the
# app's history {summary: null, turns: [user F0, assistant F0 answer text as shown]}.
F8 = [x for x in rd(A + "/coverage-map/searchpar/r5/qform.chain.jsonl")]; CH = {x["id"]: x for x in F8}
P48 = json.load(open(A + "/retbench/items/f8-48.json"))
TPL = rd(f"{A}/coverage-map/sefix/ans-req/sefix124-main-s42.requests.jsonl")[0]
def item_req(i, q, job_, g, pers):
    r = json.loads(json.dumps(TPL)); r["item"] = {"id": i, "question": q, "lang": "en"}; return rc_req(r, job_, g, pers)
for p, jn in (("S", "v3-s"), ("SP", "v3-splus")):
    t1 = [item_req(x["turn1"], CH[x["turn1"]]["question"], jn, "turn1", PERS[p]) for x in P48]
    t2 = [item_req(x["id"], CH[x["id"]]["question"], jn, "turn2", PERS[p]) for x in P48]
    for x, r in zip(P48, t2): r["item"]["prevId"] = x["turn1"]  # stripped by v3_stage2.py (history is filled there)
    d = f"{N}/jobs/{jn}"; os.makedirs(d, exist_ok=True)
    open(d + "/turn2.template.jsonl", "w").write("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in t2))
    job(jn, [("turn1", t1)], persona=p, suite="V3L2", stage2=dict(template="turn2.template.jsonl", from_group="00-turn1", group="01-turn2", n=len(t2)),
        reference=None if p == "S" else VD + "/night/fetched/v3-s")
# S5: PACKPROOF 180 ON/OFF (360 generations) on ENGINE-RC (shaped factbook in the kit); reference = PACKPROOF 10-23 traces
PPI = A + "/packproof/in"; PPG = ["on-k13"] + sorted(f[:-15] for f in os.listdir(PPI) if f.endswith(".requests.jsonl") and f not in ("ident5.requests.jsonl", "on-k13.requests.jsonl"))
job("s5-packproof", [(g, [rc_req(r, "s5-packproof", g, None) for r in rd(f"{PPI}/{g}.requests.jsonl")]) for g in PPG], suite="S5", reference=A + "/packproof/gen")
# S7: seed 44 on the 60 UXMATRIX items ON (S); reference = V2 S ON (seed 42, same tree)
job("s7-uxm-on-s44", [("on", [rc_req(r, "s7-uxm-on-s44", "on", None, seed=44) for r in rd(f"{UXI}/on.requests.jsonl")])], suite="S7",
    reference=VD + "/night/fetched/v2-s/00-on")
# S10: 27 Research Topics, Succinct, wiki-vital5 only (topics27 recipe kit), RC tree + RC env; reference = TOPICS27-SUCCINCT traces
def topics_req(r):
    r = json.loads(json.dumps(r)); kit = r["config"]["kit"]; r2 = rc_req(r, "s10-topics", "topics", None); r2["config"]["kit"] = kit; return r2
job("s10-topics", [("topics", [topics_req(r) for r in rd(A + "/topics27/in/t27-succinct-s42.requests.jsonl")])], suite="S10",
    reference=A + "/topics27/gen-succinct/traces.jsonl")
# B-k4comp40: the 19 MAIN items whose kept set changed vs RETBENCH base; rs-RETBENCH + SEFIX-124 kit + RS_RB_K=4 RS_RB_COMPRESS=0.4; s42
rb = json.load(open(A + "/retbench/aggregates/B-k4comp40.json"))["main"]["kept_ids"]; base = json.load(open(A + "/retbench/aggregates/base.json"))["main"]["kept_ids"]
CH19 = sorted(i for i in base if rb[i] != base[i]); assert len(CH19) == 19
job("b-k4comp40-19", [("main19", [rc_req(r, "b-k4comp40-19", "main19", None, rc=False) for r in rd(f"{A}/coverage-map/sefix/ans-req/sefix124-main-s42.requests.jsonl") if r["item"]["id"] in CH19])],
    tree="rs-RETBENCH", packdir="packs-k13", env="rb", suite="B-k4comp40", reference=f"{A}/coverage-map/sefix/ans-traces/sefix124-main-s42.traces.jsonl")
json.dump(dict(order=[j["name"] for j in JOBS], rc_kit=RCK, rc_settings=RCS, splus_sha=SP["persona_sha256_adapter"], jobs=JOBS), open(N + "/jobs.json", "w"), indent=1)
for j in JOBS: print(f"{j['name']:16s} {j['suite']:10s} groups {len(j['groups']):2d} requests {j['n_requests']}")
print("total", sum(j["n_requests"] for j in JOBS))
