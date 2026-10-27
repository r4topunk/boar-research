"""QFORM matrix (0 LLM). python3 -I tools/matrix.py [replay.jsonl] [tag]
Reads items/qform.jsonl, items/facts.json, replay/<file>; writes aggregates/matrix[.<tag>].json and matrix[.<tag>].md.
Gold hit: a candidate whose title+body contains the normalised verbatim quote (lowercase, punctuation stripped, whitespace collapsed),
else its chunk id equals the gold's merged chunk id. Lists: raw = what retrieve() returned to the engine (engine k), wide = a separate
retrieve(q, 12) (rank/visibility only), kept = the engine's final `sources` event (after compress + grounding)."""
import json, math, os, random, re, statistics, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
rep_file = sys.argv[1] if len(sys.argv) > 1 else "replay/qform.replay.jsonl"
tag = sys.argv[2] if len(sys.argv) > 2 else ""
suffix = f".{tag}" if tag else ""
items = {}
for l in open(os.path.join(ROOT, "items/qform.jsonl")):
    d = json.loads(l); items[d["id"]] = d
facts = {f["fact_id"]: f for f in json.load(open(os.path.join(ROOT, "items/facts.json")))}
rep = {}
for l in open(os.path.join(ROOT, rep_file)):
    d = json.loads(l); rep[d["id"]] = d
PACKS = ["boar-factbook", "boar-firstaid-en", "boar-medlineplus-en", "boar-crypto", "boar-wikivoyage-en", "boar-visa-en"]
FORMS = list(range(9))
FNAME = {0: "F0 base", 1: "F1 entity-free", 2: "F2 keywords", 3: "F3 situational", 4: "F4 typos", 5: "F5 yes/no true", 6: "F6 false premise", 7: "F7 comparison", 8: "F8 follow-up"}

def norm(s):
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9]+", " ", s.lower())).strip()
def cid(c):
    m = re.search(r":(\d+)$", c["chunkId"]); return int(m.group(1)) if m else None
def hit_in(lst, quote_n, chunk_id):
    for i, c in enumerate(lst):
        if quote_n in norm(c["title"] + " " + c["body"]) or cid(c) == chunk_id:
            return i + 1
    return None

rows = []
for iid, it in items.items():
    f = facts[it["fact_id"]]; r = rep[iid]
    qn = norm(f["gold"]["quote"]); gc = f["gold"]["merged_chunk_id"]
    rk = hit_in(r["rawFull"], qn, gc); wk = hit_in(r["wideFull"], qn, gc); kk = hit_in(r["keptFull"], qn, gc)
    alt = [(norm(a["quote"]), a["merged_chunk_id"]) for a in f["gold"]["alt"]]
    ga = f["gold"]["merged_article_id"]
    art = lambda lst: any(re.search(r":a(\d+)$", c.get("docId") or "") and int(re.search(r":a(\d+)$", c["docId"]).group(1)) == ga for c in lst)
    kany = bool(kk) or any(hit_in(r["keptFull"], q, c) for q, c in alt)
    rany = bool(rk) or any(hit_in(r["rawFull"], q, c) for q, c in alt)
    rows.append({"id": iid, "pack": it["pack"], "fact_id": it["fact_id"], "form": it["form"], "question": it["question"],
                 "query": r["query"], "k": r["k"], "task": r["task"], "retrieved": bool(r["rawFull"]),
                 "n_raw": len(r["rawFull"]), "n_kept": len(r["keptFull"]),
                 "hit_raw": rk is not None, "hit_wide": wk is not None, "hit_kept": kk is not None,
                 "rank_raw": rk, "rank_wide": wk, "rank_kept": kk, "hit_kept_any": kany, "hit_raw_any": rany, "art_raw": art(r["rawFull"]), "art_kept": art(r["keptFull"]),
                 "top_score": r["rawFull"][0]["score"] if r["rawFull"] else None,
                 "kept_titles": [c["title"] for c in r["keptFull"]], "raw_titles": [c["title"] for c in r["rawFull"]],
                 "gold_title": f["gold"]["title"]})

def wilson(x, n, z=1.96):
    if n == 0: return (float("nan"),) * 2
    p = x / n; d = 1 + z * z / n
    c = p + z * z / (2 * n); h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return ((c - h) / d, (c + h) / d)
def boot_diff(a, b, B=2000, seed=11):
    """paired F0 - Fi on per-fact 0/1 vectors; percentile CI."""
    rng = random.Random(seed); n = len(a)
    d = [x - y for x, y in zip(a, b)]
    m = sum(d) / n
    bs = []
    for _ in range(B):
        s = 0
        for _ in range(n): s += d[rng.randrange(n)]
        bs.append(s / n)
    bs.sort()
    return m, bs[int(0.025 * B)], bs[int(0.975 * B) - 1]
def sel(form=None, pack=None):
    return [r for r in rows if (form is None or r["form"] == form) and (pack is None or r["pack"] == pack)]
def agg(rs):
    n = len(rs); x = sum(r["hit_kept"] for r in rs)
    lo, hi = wilson(x, n)
    ranks = [r["rank_wide"] for r in rs if r["rank_wide"]]
    sc = [r["top_score"] for r in rs if r["top_score"] is not None]
    return {"n": n, "hit_raw": sum(r["hit_raw"] for r in rs) / n, "hit_wide12": sum(r["hit_wide"] for r in rs) / n,
            "hit_kept": x / n, "hit_kept_n": x, "kept_ci": [lo, hi],
            "median_rank_wide12": statistics.median(ranks) if ranks else None, "n_gold_in_wide": len(ranks),
            "mean_top_score": sum(sc) / len(sc) if sc else None, "no_retrieval": sum(not r["retrieved"] for r in rs),
            "hit_kept_any": sum(r["hit_kept_any"] for r in rs) / n,
            "art_raw": sum(r["art_raw"] for r in rs) / n, "art_kept": sum(r["art_kept"] for r in rs) / n,
            "kept_but_not_raw": sum(r["hit_kept"] and not r["hit_raw"] for r in rs),
            "raw_not_kept": sum(r["hit_raw"] and not r["hit_kept"] for r in rs),
            "wide_not_raw": sum(r["hit_wide"] and not r["hit_raw"] for r in rs)}

out = {"replay": rep_file, "by_form": {}, "by_form_pack": {}, "drop_vs_F0": {}, "drop_vs_F0_pack": {}, "holes": [], "items": rows}
for k in FORMS:
    out["by_form"][k] = agg(sel(k))
    for p in PACKS: out["by_form_pack"][f"{k}|{p}"] = agg(sel(k, p))
def vec(form, pack=None, key="hit_kept"):
    rs = sorted(sel(form, pack), key=lambda r: r["fact_id"]); return [int(r[key]) for r in rs]
for key in ("hit_kept", "hit_raw", "hit_wide"):
    for k in FORMS[1:]:
        m, lo, hi = boot_diff(vec(0, None, key), vec(k, None, key))
        out["drop_vs_F0"][f"{key}|{k}"] = {"drop": m, "ci": [lo, hi]}
        for p in PACKS:
            m, lo, hi = boot_diff(vec(0, p, key), vec(k, p, key))
            out["drop_vs_F0_pack"][f"{key}|{k}|{p}"] = {"drop": m, "ci": [lo, hi]}
for k in FORMS[1:]:
    d = out["drop_vs_F0"][f"hit_kept|{k}"]
    if d["drop"] >= 0.20 and d["ci"][0] > 0: out["holes"].append({"form": k, "drop": d["drop"], "ci": d["ci"], "level": "pooled"})
    for p in PACKS:
        d = out["drop_vs_F0_pack"][f"hit_kept|{k}|{p}"]
        if d["drop"] >= 0.20 and d["ci"][0] > 0: out["holes"].append({"form": k, "pack": p, "drop": d["drop"], "ci": d["ci"], "level": "pack"})
json.dump(out, open(os.path.join(ROOT, f"aggregates/matrix{suffix}.json"), "w"), indent=1)

# ---------------------------------------------------------------- markdown
pc = lambda x: "-" if x is None else f"{100 * x:.0f}"
L = []
L.append(f"# QFORM matrix ({rep_file}, 0 LLM)\n")
L.append("hit@kept = gold chunk in the engine's final `sources` (a skipped/empty retrieval counts as a miss). raw = retrieve() result at the engine's k (3-4); wide = a separate retrieve(q, 12).\n")
L.append("## Per form (n 48)\n")
L.append("| form | hit@raw % | hit@wide12 % | hit@kept % | kept 95% CI (Wilson) | median gold rank (wide12) [n found] | mean top score | no retrieval |")
L.append("|---|---|---|---|---|---|---|---|")
for k in FORMS:
    a = out["by_form"][k]
    L.append(f"| {FNAME[k]} | {pc(a['hit_raw'])} | {pc(a['hit_wide12'])} | {pc(a['hit_kept'])} ({a['hit_kept_n']}/48) | {pc(a['kept_ci'][0])}-{pc(a['kept_ci'][1])} | {a['median_rank_wide12']} [{a['n_gold_in_wide']}] | {a['mean_top_score']:.3f} | {a['no_retrieval']} |")
L.append("\n## Secondary reads per form (n 48)\n")
L.append("| form | article@raw % | article@kept % (right article, any chunk) | hit@kept any of the self-test/authored facts % | kept lists empty |")
L.append("|---|---|---|---|---|")
for k in FORMS:
    a = out["by_form"][k]; ne = sum(1 for r in sel(k) if r["n_kept"] == 0)
    L.append(f"| {FNAME[k]} | {pc(a['art_raw'])} | {pc(a['art_kept'])} | {pc(a['hit_kept_any'])} | {ne} |")
L.append("\n## hit@kept % by form x pack (n 8 each)\n")
L.append("| form | " + " | ".join(p.replace("boar-", "") for p in PACKS) + " |")
L.append("|---|" + "---|" * len(PACKS))
for k in FORMS:
    L.append(f"| {FNAME[k]} | " + " | ".join(f"{pc(out['by_form_pack'][f'{k}|{p}']['hit_kept'])} ({out['by_form_pack'][f'{k}|{p}']['hit_kept_n']})" for p in PACKS) + " |")
L.append("\n## Paired drop F0 - Fi (points; bootstrap 95% CI over the 48 facts, B 2000, seed 11)\n")
L.append("| form | kept drop [CI] | raw drop [CI] | wide12 drop [CI] | hole (kept drop >= 20 and CI > 0) |")
L.append("|---|---|---|---|---|")
for k in FORMS[1:]:
    c = lambda key: (lambda d: f"{100*d['drop']:+.1f} [{100*d['ci'][0]:+.0f}, {100*d['ci'][1]:+.0f}]")(out["drop_vs_F0"][f"{key}|{k}"])
    hole = "YES" if any(h["form"] == k and h["level"] == "pooled" for h in out["holes"]) else "no"
    L.append(f"| {FNAME[k]} | {c('hit_kept')} | {c('hit_raw')} | {c('hit_wide')} | {hole} |")
L.append("\n## Paired kept drop F0 - Fi by pack (points; n 8, CIs wide)\n")
L.append("| form | " + " | ".join(p.replace("boar-", "") for p in PACKS) + " |")
L.append("|---|" + "---|" * len(PACKS))
for k in FORMS[1:]:
    L.append(f"| {FNAME[k]} | " + " | ".join((lambda d: f"{100*d['drop']:+.0f} [{100*d['ci'][0]:+.0f},{100*d['ci'][1]:+.0f}]")(out['drop_vs_F0_pack'][f'hit_kept|{k}|{p}']) for p in PACKS) + " |")
L.append("\n## Keep step vs raw (counts of 48 per form)\n")
L.append("| form | gold in wide12 not in raw (cut by k) | gold in raw not kept (keep step drops it) | kept but not raw |")
L.append("|---|---|---|---|")
for k in FORMS:
    a = out["by_form"][k]; L.append(f"| {FNAME[k]} | {a['wide_not_raw']} | {a['raw_not_kept']} | {a['kept_but_not_raw']} |")
# examples: misses where F0 hit, spread across forms
rng = random.Random(11)
cand = {}
for r in rows:
    if r["form"] == 0 or r["hit_kept"]: continue
    f0 = next(x for x in rows if x["fact_id"] == r["fact_id"] and x["form"] == 0)
    if f0["hit_kept"]: cand.setdefault(r["form"], []).append(r)
ex = []
order = [k for k in FORMS[1:] if k in cand]
for k in order: rng.shuffle(cand[k])
i = 0
while len(ex) < 10 and any(cand.values()):
    k = order[i % len(order)]; i += 1
    if cand.get(k): ex.append(cand[k].pop())
L.append("\n## 10 example misses (F0 hit @kept, this form missed)\n")
L.append("| id | form | question | engine search query | gold title | kept titles |")
L.append("|---|---|---|---|---|---|")
for r in ex:
    L.append(f"| {r['id']} | F{r['form']} | {r['question'][:90]} | {(r['query'] or 'NO RETRIEVAL')[:90]} | {r['gold_title'][:50]} | {'; '.join(t[:40] for t in r['kept_titles']) or '(none)'} |")
L.append("\n## Holes (pooled and per pack)\n")
for h in out["holes"]:
    L.append(f"- F{h['form']}{' / ' + h['pack'] if 'pack' in h else ''}: kept drop {100*h['drop']:.0f} points, CI [{100*h['ci'][0]:.0f}, {100*h['ci'][1]:.0f}] ({h['level']})")
if not out["holes"]: L.append("- none")
open(os.path.join(ROOT, f"aggregates/matrix{suffix}.md"), "w").write("\n".join(L) + "\n")
print("\n".join(L))
