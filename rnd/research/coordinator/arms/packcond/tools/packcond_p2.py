#!/usr/bin/env python3
"""PACKCOND P2: what packs NOT in the kit would cover (F0 via jev) + deep-tier replay F1/F2/crowding for the top-2 packs. Arm H s42; sets vpara, v02.
Reuses packcond_p1 (Pack for formatVersion-2 packs, plan inputs, questions); adds a formatVersion-1 pack (wiki-vital5: chunks.body).
Packs: vital5 (v1), prep (shared-data/preparedness-v3/boar-preparedness.sqlite; the path in the task does not exist in packs/), shard07 (gate-ref), top100k.
Stages: gate (jev, writes aggregates/packcond-p2-{set}.json), replay (0 LLM, outputs under blind/<set>/runs-packcond/), report (adds F1/F2/crowding to the aggregates).
Writes ONLY ids/titles/probabilities/counts to rnd; replay outputs (query text) stay under blind/.
usage: packcond_p2.py gate|replay|report [--dry-run] [--workers 6] [--budget 0.38]
"""
import sys, os, re, json, argparse, sqlite3, threading, hashlib, collections, time, subprocess
T = "<workspace>/rnd/research/coordinator/arms/packcond/tools"
sys.path.insert(0, T); sys.path.insert(0, "<workspace>/rnd/research/coordinator/arms/wikisection/tools")
import packcond_p1 as p1, section_gate as sg, anywhere_gate as ag
from concurrent.futures import ThreadPoolExecutor
ROOT = sg.ROOT; COORD = p1.COORD; OUT = f"{COORD}/arms/packcond/aggregates"
SD = f"{ROOT}/shared-data"
PACKS = {"vital5": (f"{SD}/packs/wiki-vital5.sqlite", 1), "prep": (f"{SD}/preparedness-v3/boar-preparedness.sqlite", 2),
         "shard07": (f"{SD}/gate-ref/boar-wiki-en-07.sqlite", 2), "top100k": (f"{SD}/packs/boar-wiki-en-top100k.sqlite", 2)}
SETS = {"vpara": dict(run=p1.RUNS[("H", "vpara")], blind="V-para", q="items.jsonl"),
        "v02": dict(run=p1.RUNS[("H", "v02")], blind="bench-v02", q="live/v0.2/questions.v02-new.jsonl")}
TH = 0.7; TOPK = 20; CAPC = 40; NT = 12; BATCH = 8; CAPCH = 2000
BASEKIT = f"{SD}/crypto/boar-crypto.sqlite,{SD}/packs/boar-wikivoyage-en.sqlite"

class PackV1:
    def __init__(s, path):
        s.db = sqlite3.connect(f"file:{path}?mode=ro", uri=True, check_same_thread=False); s.lk = threading.Lock()
        s.titles = {t.lower() for (t,) in s.db.execute("select distinct title from chunks")}
    def fts(s, q, n):
        with s.lk:
            try: return [r[0] for r in s.db.execute("select rowid from chunks_fts where chunks_fts match ? order by bm25(chunks_fts,2.0,1.0) limit ?", (q, n))]
            except sqlite3.OperationalError: return []
    def chunk(s, cid):
        with s.lk: r = s.db.execute("select title, body from chunks where id=?", (cid,)).fetchone()
        return (cid, r[0], r[1].strip()) if r else (None, "", "")

def openpack(n):
    path, fv = PACKS[n]; return PackV1(path) if fv == 1 else p1.Pack(path)

def plan_for(st):
    S = SETS[st]["run"]
    agg = json.load(open(f"{COORD}/arms/lossmap/aggregates/{S['agg']}"))["items"]; meta = {i["id"]: i for i in agg}
    rows = collections.defaultdict(list)
    for r in sg.read_jsonl(f"{S['dir']}/{S['j']}"):
        if r.get("ok"): rows[r["queryId"]].append(r)
    tr = {t["itemId"]: t for t in sg.read_jsonl(f"{S['dir']}/{S['t']}")}
    plan = []
    for qid in [i["id"] for i in agg]:
        rs = sorted(rows[qid], key=lambda r: r["order"])
        clean = meta[qid]["ratio"] >= 0.75  # same answer-support rule as P1
        r1 = rs[0]["verdict"]["rationale"][:2500]; r2 = rs[-1]["verdict"]["rationale"][:2500] if len(rs) > 1 else ""
        ans = ((tr[qid].get("answer") or {}).get("text") or "")[:3000]
        plan.append(dict(id=qid, clean=clean, r1=r1, r2=r2, ans=ans, meta=meta[qid]))
    return plan

def gate(a):
    key = os.environ.get("VERCEL_AI_GATEWAY") or os.environ.get("AI_GATEWAY_API_KEY")
    if not key and not a.dry_run: sys.exit("no gateway key")
    packs = {n: openpack(n) for n in PACKS}; spent = [0.0]; lock = threading.Lock(); skipped = [0]
    for st in SETS:
        S = SETS[st]["run"]; plan = plan_for(st); t0 = time.time()
        cd = f"{ROOT}/blind/{SETS[st]['blind']}/runs-packcond/cache"; os.makedirs(cd, exist_ok=True)
        def call(body):
            h = hashlib.sha256(json.dumps(body, sort_keys=True, ensure_ascii=False).encode()).hexdigest() + ".json"
            hit = os.path.exists(os.path.join(cd, h))
            if not hit and spent[0] >= a.budget: return None, hit, 0.0
            res, _ = sg.call(body, key, cd)
            c = 0.0 if hit else float(((res.get("providerMetadata") or {}).get("gateway") or {}).get("marketCost") or 0)
            with lock: spent[0] += c
            return res, hit, c
        def cands(p, P):
            ts = ag.terms([p["ans"]] if p["clean"] else [p["r1"], p["r2"]], NT)
            l1 = P.fts(ag.mq(ts), TOPK); l2 = P.fts(" ".join('"%s"' % w.replace('"', "") for w in ts[:4]), TOPK); out = []
            for x, y in zip(l1 + [None] * TOPK, l2 + [None] * TOPK):
                for c in (x, y):
                    if c is not None and c not in out: out.append(c)
            return out[:CAPC]
        def work(p):
            out = {}; req = 0
            for pn, P in packs.items():
                cl = []
                for cid in cands(p, P):
                    aid, t, txt = P.chunk(cid)
                    if txt: cl.append((cid, t, txt[:CAPCH]))
                recs = []; trunc = False
                for b in range(0, len(cl), BATCH):
                    sub = cl[b:b + BATCH]; ks = [f"c{i}" for i in range(len(sub))]
                    st_ = ({"answer": p["ans"]} if p["clean"] else {"rationale_1": p["r1"], "rationale_2": p["r2"]})
                    st_["chunks"] = {k: s[2] for k, s in zip(ks, sub)}
                    body = {"model": sg.MODEL, "state": st_, "questions": p1.questions("sup" if p["clean"] else "fact", ks)}
                    if a.dry_run: req += 1; continue
                    res, hit, c = call(body); req += 1
                    if res is None: trunc = True; continue
                    A = res["answers"]
                    for k, s in zip(ks, sub):
                        if p["clean"]: hp = qp = A[f"sup_{k}"]["probability"]
                        else: hp = A[f"has_{k}"]["probability"]; qp = A[f"quo_{k}"]["probability"]
                        recs.append(dict(chunk=s[0], article=s[1], p=round(hp, 3), q=round(qp, 3)))
                ver = [r for r in recs if r["p"] >= TH and r["q"] >= TH]
                out[pn] = dict(n_chunks=len(cl), max_p=max((r["p"] for r in recs), default=None), f0=bool(ver), f0_loose=any(r["p"] >= TH for r in recs),
                               hit_articles=sorted({r["article"] for r in ver})[:8], hits=[r for r in recs if r["p"] >= 0.6][:6], budget_truncated=trunc)
            return p, out, req
        with ThreadPoolExecutor(a.workers) as ex: res = list(ex.map(work, plan))
        req = sum(r[2] for r in res)
        if a.dry_run: print(f"{st}: items={len(plan)} requests={req}"); continue
        H = {i["id"]: i for i in json.load(open(f"{OUT}/packcond-H-{st}.json"))["items"]}
        items = []
        for p, out, _ in res:
            m = p["meta"]
            items.append(dict(id=p["id"], category=m["category"], mode="answer-support" if p["clean"] else "missing-fact", ratio=round(m["ratio"], 4),
                              p1_F0=H[p["id"]]["F0"], packs=out, F0_any=any(o["f0"] for o in out.values())))
        json.dump(dict(set=st, arm="H", seed=42, threshold=TH, cap_chunks=CAPC, cap_chars=CAPCH, batch=BATCH, model=sg.MODEL, packs={n: PACKS[n][0].replace(ROOT + "/", "") for n in PACKS},
                       gateway_cost_usd_cumulative=round(spent[0], 5), runtime_s=round(time.time() - t0), n=len(items), items=items), open(f"{OUT}/packcond-p2-{st}.json", "w"), indent=1)
        print(f"{st}: n={len(items)} req={req} cumulative_cost=${spent[0]:.4f} t={time.time()-t0:.0f}s")
    print("TOTAL", round(spent[0], 4))

def load_gate(st): return json.load(open(f"{OUT}/packcond-p2-{st}.json"))

def added_counts():
    c = collections.Counter()
    for st in SETS:
        for i in load_gate(st)["items"]:
            for pn, o in i["packs"].items():
                if o["f0"] and not i["p1_F0"]: c[pn] += 1
    return c

def top2():
    c = added_counts(); return [n for n, _ in c.most_common(2)]

def replay(a):
    tops = top2(); print("top2 by added coverage", tops, dict(added_counts()))
    env = dict(os.environ, BOAR_REPLAY_CACHE=f"{COORD}/arms/deepcovfb/cache")
    for st, S in SETS.items():
        G = load_gate(st); od = f"{ROOT}/blind/{S['blind']}/runs-packcond"; os.makedirs(od, exist_ok=True)
        allids = sorted({i["id"] for i in G["items"] if any(i["packs"][n]["f0"] for n in tops)})
        base = ["--deep", "--gate", "rules", "--tree", "wt/cut7", "--k", "6", "--pool", "20", "--questions", f"blind/{S['blind']}/{S['q']}"]
        jobs = [("base", BASEKIT, allids)] + [(n, BASEKIT + "," + PACKS[n][0].replace(ROOT + "/", ""), sorted(i["id"] for i in G["items"] if i["packs"][n]["f0"])) for n in tops]
        for lab, packs, ids in jobs:
            if not ids: continue
            cmd = [f"{COORD}/arms/deepcovfb/tools/replay-deep.sh"] + base + ["--ids", ",".join(ids), "--packs", packs.replace(SD, "shared-data"), "--out", f"{od}/replay-{lab}.jsonl"]
            r = subprocess.run(cmd, cwd=ROOT, env=env, capture_output=True, text=True)
            print(st, lab, "ids", len(ids), "rc", r.returncode, (r.stderr.strip().splitlines() or [""])[-1][:160])

_LIB = re.compile(r"^[^:]{2,40}:\s+")
norm = lambda s: " ".join(str(s or "").split()).casefold()
bare = lambda t: _LIB.sub("", str(t or ""), count=1)

def report(a):
    tops = top2(); packs = {n: openpack(n) for n in tops}
    for st, S in SETS.items():
        G = load_gate(st); od = f"{ROOT}/blind/{S['blind']}/runs-packcond"; res = {}
        load = lambda f: {r["id"]: r for r in map(json.loads, open(f))} if os.path.exists(f) else {}
        B = load(f"{od}/replay-base.jsonl")
        for n in tops:
            R = load(f"{od}/replay-{n}.jsonl"); P = packs[n]; PT = P.titles
            isp = lambda r: norm(bare(r.get("title"))) in PT or norm(r.get("title")) in PT
            items = {i["id"]: i for i in G["items"]}
            cov = [i for i in items.values() if i["packs"][n]["f0"] and i["id"] in R]
            f1 = f2 = fp = 0; rows = []; ks = ps = bs = 0
            for i in cov:
                r = R[i["id"]]; hit = {norm(bare(h)) for h in i["packs"][n]["hit_articles"]} | {norm(h) for h in i["packs"][n]["hit_articles"]}
                has = lambda L: any(norm(bare(x.get("title"))) in hit or norm(x.get("title")) in hit for x in L or [])
                a1, a2, a3 = has(r.get("raw")), has(r.get("kept")), has(r.get("pool"))
                f1 += a1; f2 += a2; fp += a3
                if r.get("k") is not None:
                    ks += len(r["kept"]); ps += sum(isp(x) for x in r["kept"])
                    if i["id"] in B: bs += sum(isp(x) for x in B[i["id"]]["kept"])
                rows.append(dict(id=i["id"], category=i["category"], retrieved=r.get("k") is not None, F1_raw=a1, F2_kept=a2, F1_pool20=a3, pack_kept_slots=sum(isp(x) for x in r["kept"]), n_kept=len(r["kept"])))
            res[n] = dict(n_covered=len(cov), n_covered_gate=sum(1 for i in items.values() if i["packs"][n]["f0"]), F1_raw=f1, F2_kept=f2, F1_pool20=fp,
                          kept_slots=ks, pack_attributed_kept_slots=ps, pack_share_of_kept=round(ps / max(1, ks), 3), base_replay_attributed_slots=bs, items=rows)
        G["replay_f1f2"] = dict(top2=tops, k=6, pool=20, tree="wt/cut7", gate="rules", kit="crypto+wikivoyage+pack", result=res)
        json.dump(G, open(f"{OUT}/packcond-p2-{st}.json", "w"), indent=1)
        print(st, json.dumps({n: {k: v for k, v in r.items() if k != "items"} for n, r in res.items()}))

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("stage", choices=["gate", "replay", "report"]); ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--workers", type=int, default=6); ap.add_argument("--budget", type=float, default=0.38); a = ap.parse_args()
    {"gate": gate, "replay": replay, "report": report}[a.stage](a)
