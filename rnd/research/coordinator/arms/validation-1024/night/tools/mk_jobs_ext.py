#!/usr/bin/env python3
"""ADDENDUM-2 mini extension (jobs 11-16), 0 LLM. Derives every request from the jobs mk_jobs.py already wrote (night/jobs/<job>/req), so kit, env,
settings and persona stay byte-identical except seed / persona / runId / arm. mk_jobs.py is not edited (its sha 3a5f1775 is cited by V3L2-criterion.md).
usage: python3 -I mk_jobs_ext.py   -> night/jobs/<new job>/..., night/jobs-ext.json (order)
Job 16 (v2-splus-s44, v2-s-s44, ON only) carries not_after "2026-10-24 08:30": mini_queue.sh skips a job whose start would be at or after it."""
import json, os, glob, re
A = "<workspace>/rnd/research/coordinator/arms"; VD = A + "/validation-1024"; N = VD + "/night"; FE = N + "/fetched"
rd = lambda f: [json.loads(l) for l in open(f) if l.strip()]
SP = json.load(open(VD + "/v2/personas/splus.json"))
SPS = {"personaSystemPrompt": SP["personaSystemPrompt"], "personaStyleReminder": SP["personaStyleReminder"]}
P2 = json.load(open(VD + "/v2/personas/p2.json")); P2S = {"personaSystemPrompt": P2["personaSystemPrompt"], "personaStyleReminder": P2["personaStyleReminder"]}
def to_splus(s, P=None):
    s = dict(s); s.pop("personalityId", None); s.pop("personaSystemPrompt", None); s.pop("personaStyleReminder", None); s.update(P or SPS); return s
def to_s(s):
    s = dict(s); s.pop("personaSystemPrompt", None); s.pop("personaStyleReminder", None); s["personalityId"] = "succinct"; return s
def derive(src, name, seed=None, persona=None, groups=None, suite="", reference=None, not_after=None, tree=None, env=None):
    M = json.load(open(f"{N}/jobs/{src}/job.json")); d = f"{N}/jobs/{name}"; os.makedirs(d + "/req", exist_ok=True)
    for f in glob.glob(d + "/req/*"): os.remove(f)
    def tf(r, g):
        r = json.loads(json.dumps(r)); c = r["config"]
        if persona == "SP": c["settings"] = to_splus(c["settings"])
        if persona == "S": c["settings"] = to_s(c["settings"])
        if persona == "P2": c["settings"] = to_splus(c["settings"], P2S)
        if seed is not None: r["seed"] = seed
        c["arm"] = re.sub(r"\+v1024-.*$", "", c["arm"]) + "+v1024-" + name; r["runId"] = f"v1024-{name}-{g}"; return r
    n, gl = 0, []
    for f in sorted(glob.glob(f"{N}/jobs/{src}/req/*.requests.jsonl")):
        g = os.path.basename(f)[:-len(".requests.jsonl")]
        if groups and not re.sub(r"^\d\d-", "", g).startswith(groups): continue
        rows = [tf(r, g) for r in rd(f)]
        assert all(x["config"] == rows[0]["config"] for x in rows)
        open(f"{d}/req/{g}.requests.jsonl", "w").write("".join(json.dumps(x, ensure_ascii=False) + "\n" for x in rows)); n += len(rows); gl.append(g)
    st2 = M.get("stage2")
    if st2:
        rows = [tf(r, st2["group"]) for r in rd(f"{N}/jobs/{src}/{st2['template']}")]
        for r, o in zip(rows, rd(f"{N}/jobs/{src}/{st2['template']}")): r["item"] = o["item"]  # keep prevId for v3_stage2.py
        open(f"{d}/{st2['template']}", "w").write("".join(json.dumps(x, ensure_ascii=False) + "\n" for x in rows)); n += len(rows)
    meta = dict(M, name=name, suite=suite, persona=persona or M["persona"], reference=reference, groups=gl, n_requests=n, derived_from=src,
                seed=seed, not_after=not_after, **({"tree": tree} if tree else {}), **({"env": env} if env else {}))
    json.dump(meta, open(d + "/job.json", "w"), indent=1); return meta
J = [derive("v2-s", "v2-s-s43", seed=43, suite="V2-s43", reference=FE + "/v2-s"),
     derive("v2-splus", "v2-splus-s43", seed=43, suite="V2-s43", reference=FE + "/v2-splus"),
     derive("s5-packproof", "s5-packproof-splus", persona="SP", groups="on", suite="S5-splus", reference=FE + "/s5-packproof"),
     derive("s4-main-s42", "s4-main-splus-s42", persona="SP", suite="S4-splus", reference=FE + "/s4-main-s42/out/00-main/traces.jsonl"),
     derive("v3-s", "v3-s-s43", seed=43, suite="V3L2-s43", reference=FE + "/v3-s"),
     derive("s10-topics", "s10-topics-splus", persona="SP", suite="S10-splus", reference=FE + "/s10-topics/out/00-topics/traces.jsonl"),
     derive("v2-splus", "v2-splus-s44", seed=44, groups="on", suite="V2-s44", reference=FE + "/v2-splus", not_after="2026-10-24 08:30"),
     derive("v2-s", "v2-s-s44", seed=44, groups="on", suite="V2-s44", reference=FE + "/v2-s", not_after="2026-10-24 08:30")]
# ADDENDUM-3: 17 v3-s-carry (rs-RC-STICKY, env rcsticky = rc + RS_STICKY=2 + carry dump/prev map; the tree's adapter hands turn 2 the turn-1 sources as
# history.rsSticky, as replay-sticky.ts does), 18 v2-p2 (V2 seed 42 ON/OFF, two-paragraph Succinct, v2/personas/p2.json). Both after job 16.
J.append(derive("v3-s", "v3-s-carry", persona="S", suite="V3L2-carry", reference=FE + "/v3-s", tree="rs-RC-STICKY", env="rcsticky"))
json.dump({x["id"]: x["turn1"] for x in json.load(open(A + "/retbench/items/f8-48.json"))}, open(N + "/jobs/v3-s-carry/prev.json", "w"), indent=1)
J.append(derive("v2-s", "v2-p2", persona="P2", suite="V2-p2", reference=FE + "/v2-s"))
json.dump(dict(order=[j["name"] for j in J], jobs=J), open(N + "/jobs-ext.json", "w"), indent=1)
for j in J: print(f"{j['name']:20s} {j['suite']:10s} groups {len(j['groups']):2d} requests {j['n_requests']}")
print("total ext", sum(j["n_requests"] for j in J))
