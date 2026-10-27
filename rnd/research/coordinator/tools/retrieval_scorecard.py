#!/usr/bin/env python3
"""Retrieval failure scorecard: deterministic, from existing traces + judgments. No engine runs, no judge calls.

Every gold item (bench gold/sources.json) gets exactly one bucket per run, checked in this order:
  B1 coverage     no gold title exists in any loaded pack/corpus (scorer-normalised match)
  B2 ranking      gold in a pack, but not in retrieval.raw
  B3 dropped      gold in raw but absent from the pre-answer sources (B3-drop), or in the pre-answer sources but
                  absent from answer.shown and answer.cited (B3-hidden)
  B4 reader-fail  gold reached the prompt and judged correctness <= 2
  B5 reader-ok    gold reached the prompt and judged correctness >= 4
  B6 ambiguous    gold reached the prompt and correctness in (2, 4), or the answer declined, or unjudged
Multi-gold items: a stage counts as reached when ANY gold title reaches it.
"Pre-answer sources" and title matching follow boar-eval/scorers/retrieval.py: the last `sources` event in
trace.events (fallback retrieval.kept, which is emptied on decline); titles casefold + whitespace-collapse; a bare
gold title also matches a library-prefixed title ("Wikivoyage: Singapore"). Correctness = mean of
mapped.boar.correctness over the judged orders (both orders).

Usage (defaults reproduce RETRIEVAL-SCORECARD-2026-10-06):
  python3 -I retrieval_scorecard.py \
     --run s44=TRACES.jsonl,JUDGMENTS.jsonl --run s45=...  [--cross s42=TRACES,JUDGMENTS] \
     [--pack a.sqlite ...] [--corpus-json c.json ...] [--out-md X.md] [--out-csv X.csv] [--k 5]
Primary runs (--run) feed the TL;DR/table; --cross runs appear in the bucket table and agreement line only.
stdlib + sqlite3 only. Packs are opened read-only (mode=ro)."""
import argparse
import csv
import hashlib
import io
import json
import os
import re
import sqlite3
import sys
from collections import Counter, OrderedDict

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))  # /…/boar
P = lambda *a: os.path.join(ROOT, *a)

DEF_QUESTIONS = P("boar-eval/bench/v0.1/questions.public.jsonl")
DEF_GOLD = P("boar-eval/bench/v0.1/gold/sources.json")
CT = "boar-eval/runs/kiln/cryptotruth"
DEF_RUNS = [f"ctl-s44={P(CT, 'ctl-v01-s44.traces.jsonl')},{P(CT, 'ctl-v01-s44.judgments.v1-med.jsonl')}",
            f"ctl-s45={P(CT, 'ctl-v01-s45.traces.jsonl')},{P(CT, 'ctl-v01-s45.judgments.v1-med.jsonl')}"]
DEF_CROSS = [f"cut6-s42={P('blind/bench-v02/runs-cut6/cut6-v01-s42.traces.jsonl')},"
             f"{P('blind/bench-v02/runs-cut6/cut6-v01-s42.judgments.jsonl')}"]
# Kit packs pinned by the traces' config.kit (sha256-checked below) + the "essential" seed corpora that the
# desktop-node adapter links from the engine tree (adapter.ts setupAppRetrieval: assets/corpus/corpus.json is the
# bundled min corpus; corpus-standard/corpus-full are linked when --corpus essential). The wt/cryptotruth copies
# are byte-identical to the 0cfd4a77 git blobs; the detmax patch touches no src/rag/seedCorpus|packs|manifest file.
DEF_PACKS = [P("shared-data/crypto/boar-crypto.sqlite"), P("shared-data/packs/boar-wikivoyage-en.sqlite")]
DEF_CORPORA = [P("wt/cryptotruth/assets/corpus", f) for f in ("corpus.json", "corpus-standard.json", "corpus-full.json")]
DEF_MD = P("rnd/research/coordinator/RETRIEVAL-SCORECARD-2026-10-06.md")
DEF_CSV = P("rnd/research/coordinator/RETRIEVAL-SCORECARD-2026-10-06.items.csv")

BUCKETS = OrderedDict([("B1", "coverage"), ("B2", "ranking"), ("B3", "dropped"), ("B4", "reader-fail"),
                       ("B5", "reader-ok"), ("B6", "ambiguous")])

# ------------------------------------------------------------------ title matching (copied from scorers/retrieval.py)
_LIB = re.compile(r"^[^:]{2,40}:\s+")


def norm(s):
    return " ".join(str(s or "").split()).casefold()


def bare(t):
    return _LIB.sub("", str(t or ""), count=1)


def match(gold, ref):
    if isinstance(ref, str):
        ref = {"title": ref}
    title, _, section = gold.partition("#")
    rt = ref.get("title")
    if norm(title) != norm(rt) and (_LIB.match(title) or norm(title) != norm(bare(rt))):
        return False
    return not section or norm(section) == norm(ref.get("section"))


def hit(golds, refs):
    return [g for g in golds if any(match(g, r) for r in refs)]


def pre_answer_sources(t):
    for e in reversed(t.get("events") or []):
        if e.get("type") == "sources" and isinstance(e.get("sources"), list):
            return [s if isinstance(s, dict) else {"title": s} for s in e["sources"]], "sources-event"
    return t["retrieval"]["kept"], "kept"


# ------------------------------------------------------------------ pack lookup
def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def loose(s):
    return re.sub(r"[^0-9a-z]+", "", norm(s))


class PackIndex:
    """Gold-title lookup over SQLite packs (articles/redirects tables) and JSON corpora ([{title,…}])."""

    def __init__(self, packs, corpora):
        self.sources = []  # (label, path, sha256, n_titles)
        self.dbs = []
        for p in packs:
            con = sqlite3.connect(f"file:{p}?mode=ro", uri=True)
            n = con.execute("select count(*) from articles").fetchone()[0]
            name = dict(con.execute("select key, value from meta").fetchall()).get("name", "")
            self.dbs.append((os.path.basename(p), con))
            self.sources.append((os.path.basename(p), p, sha256(p), n, name))
        self.json_titles = []
        for c in corpora:
            titles = [d.get("title", "") for d in json.load(open(c, encoding="utf-8"))]
            self.json_titles.append((os.path.basename(c), titles, {norm(t): t for t in titles}))
            self.sources.append((os.path.basename(c), c, sha256(c), len(titles), "seed corpus (Wikipedia)"))

    def lookup(self, gold):
        """-> (status, where, detail). status: exact | normalised | near-miss | absent."""
        g = bare(gold.partition("#")[0])
        found, near = [], []
        for label, con in self.dbs:
            for (t,) in con.execute("select title from articles where title = ? collate nocase", (g,)):
                if t == g:
                    found.append(("exact", label, t))
                elif norm(t) == norm(g):
                    found.append(("normalised", label, t))
            for (t,) in con.execute("select title from articles where title like ? escape '\\' limit 5",
                                    (g.replace("%", "\\%").replace("_", "\\_") + " (%",)):
                near.append((label, t))
            for (r, t) in con.execute("select r.title, a.title from redirects r join articles a on a.id = r.article_id "
                                      "where r.title = ? limit 3", (g,)):
                if norm(t) != norm(g):
                    near.append((label, f"redirect {r} -> {t}"))
        for label, titles, by in self.json_titles:
            if g in titles:
                found.append(("exact", label, g))
            elif norm(g) in by:
                found.append(("normalised", label, by[norm(g)]))
            else:
                lg = loose(g)
                for t in titles:
                    if loose(t) == lg or norm(t).startswith(norm(g) + " ("):
                        near.append((label, t))
        if found:
            kinds = {k for k, _, _ in found}
            st = "exact" if "exact" in kinds else "normalised"
            det = "; ".join(sorted({f"{lab}:{t}" if k == 'exact' else f"{lab}:{t} (case)" for k, lab, t in found}))
            return st, sorted({lab for _, lab, _ in found}), det
        if near:
            return "near-miss", sorted({lab for lab, _ in near}), "; ".join(f"{lab}:{t}" for lab, t in near[:4])
        return "absent", [], ""


# ------------------------------------------------------------------ helpers
STOP = set("""a an the and or of in on at to for from by with without about as is are was were be been being do does
did doing have has had what which who whom whose when where why how this that these those it its i me my we our you your
he she they them their his her not no yes can could should would will shall may might must than then there here into
over under between vs versus more most less least very much many some any all each both either neither one two three
first second explain give tell describe compare quick overview main bigger smaller better best good like just get got
also kind type way ways other others own same such only about after before during while if so but because per what's
does doesn't did didn't isn't aren't wasn't weren't i'm i'd i'll it's""".split())


def words(s):
    out = set()
    for w in re.findall(r"[a-z0-9]+", str(s or "").casefold()):
        if len(w) < 3 or w in STOP:
            continue
        out.add(w[:-1] if len(w) > 4 and w.endswith("s") else w)
    return out


def read_jsonl(path):
    with open(path, encoding="utf-8") as f:
        return [json.loads(l) for l in f if l.strip()]


def correctness(judgments):
    by = {}
    for j in judgments:
        if j.get("ok") is False:
            continue
        c = ((j.get("mapped") or {}).get("boar") or {}).get("correctness")
        if isinstance(c, (int, float)):
            by.setdefault(j["queryId"], []).append(c)
    return {k: (sum(v) / len(v), v) for k, v in by.items()}


def context_codes(t):
    for c in (t.get("route") or {}).get("reasonCodes") or []:
        m = re.match(r"context:(\d+)->(\d+)", c)
        if m:
            return int(m.group(1)), int(m.group(2))
    return None, None


def prompt_tokens(t):
    for e in reversed(t.get("events") or []):
        if e.get("kind") == "generation" and e.get("promptTokens") is not None:
            return e["promptTokens"]
    return (t.get("timing") or {}).get("promptTokens")


def uniq(xs):
    seen, out = set(), []
    for x in xs:
        if x not in seen:
            seen.add(x)
            out.append(x)
    return out


# ------------------------------------------------------------------ scoring
def score_run(label, traces_path, judgments_path, items, gold, packidx, gold_status, k):
    traces = {}
    for t in read_jsonl(traces_path):
        if t.get("itemId") in items:
            traces[t["itemId"]] = t  # last wins
    corr = correctness(read_jsonl(judgments_path)) if judgments_path else {}
    rows = []
    for qid, q in items.items():
        t = traces.get(qid)
        g = gold.get(qid) or []
        row = OrderedDict(run=label, item=qid, category=q.get("category"), grading=(q.get("grading") or {}).get("type") if isinstance(q.get("grading"), dict) else q.get("grading"),
                          question=q.get("question"))
        if t is None:
            row.update(bucket="no-trace")
            rows.append(row)
            continue
        ret = t["retrieval"]
        raw, kept, dropped = ret.get("raw") or [], ret.get("kept") or [], ret.get("dropped") or []
        pre, pre_from = pre_answer_sources(t)
        a = t.get("answer") or {}
        shown, cited = a.get("shown") or [], a.get("cited") or []
        c = corr.get(qid)
        cmean = round(c[0], 2) if c else None
        qwords = words(q.get("question")) | set().union(*(words(x) for x in g)) if g else words(q.get("question"))
        pre_titles = uniq(r.get("title") for r in pre)
        off = [x for x in pre_titles if not (words(bare(x)) & qwords)]
        ctx_in, ctx_out = context_codes(t)
        route = t.get("route") or {}
        row.update(route_task=route.get("task"), route_tier=route.get("tier"),
                   n_raw=len(raw), n_kept=len(kept), n_dropped=len(dropped), n_pre=len(pre), pre_from=pre_from,
                   n_pre_offtopic=len(off), any_pre_offtopic=int(bool(off)),
                   context_in=ctx_in, context_out=ctx_out, prompt_tokens=prompt_tokens(t),
                   declined=int(bool(a.get("declined"))), weak_sources=int(bool(a.get("weakSources"))),
                   correctness=cmean, correctness_orders="/".join(str(x) for x in (c[1] if c else [])),
                   n_gold=len(g))
        if g:
            in_pack = [x for x in g if gold_status[x][0] in ("exact", "normalised")]
            in_raw, in_raw_k = hit(g, raw), hit(g, raw[:k])
            in_pre = hit(g, pre)
            in_kept = hit(g, kept)
            in_shown = hit(g, list(shown) + list(cited))
            in_cited = hit(g, cited)
            reached = [x for x in in_pre if x in in_shown]
            if not in_pack:
                b, why = "B1", ("near-miss: " + " | ".join(gold_status[x][2] for x in g if gold_status[x][0] == "near-miss")
                                if any(gold_status[x][0] == "near-miss" for x in g) else "absent")
            elif not in_raw:
                b, why = "B2", ("B2-empty-raw" if not raw else "B2-not-ranked") + " (in pack: " + ", ".join(in_pack) + ")"
            elif not in_pre:
                b, why = "B3", "B3-drop (raw -> not in pre-answer sources)"
            elif not reached:
                b, why = "B3", "B3-hidden (in prompt, not shown/cited)"
            elif a.get("declined"):
                b, why = "B6", "declined with gold in sources"
            elif cmean is None:
                b, why = "B6", "unjudged"
            elif cmean <= 2:
                b, why = "B4", ""
            elif cmean >= 4:
                b, why = "B5", ""
            else:
                b, why = "B6", "correctness 3-band"
            row.update(bucket=b, bucket_note=why, recall_at_k=round(len(in_raw_k) / len(g), 3),
                       gold="|".join(g), gold_in_pack="|".join(in_pack), gold_in_raw="|".join(in_raw),
                       gold_in_pre="|".join(in_pre), gold_in_kept="|".join(in_kept),
                       gold_in_shown_or_cited="|".join(in_shown), gold_cited="|".join(in_cited))
        else:
            row.update(bucket="no-gold", bucket_note="", recall_at_k=None)
        row.update(raw_titles="|".join(uniq(r.get("title") for r in raw)), pre_titles="|".join(pre_titles),
                   offtopic_titles="|".join(off), reason_codes="|".join(route.get("reasonCodes") or []))
        rows.append(row)
    kit = None
    any_t = next(iter(traces.values()), None)
    if any_t:
        kit = (any_t.get("config") or {}).get("kit")
    return rows, kit, any_t


# ------------------------------------------------------------------ report
def pct(n, d):
    return f"{100 * n / d:.0f}%" if d else "-"


def mean(xs):
    xs = [x for x in xs if x is not None]
    return sum(xs) / len(xs) if xs else None


def render_md(runs, cross, packidx, gold, gold_status, k, kits, meta):
    L = []
    w = L.append
    prim = [lab for lab, _ in runs]
    allruns = runs + cross
    gold_rows = {lab: [r for r in rows if r.get("n_gold")] for lab, rows in allruns}
    cnt = {lab: Counter(r["bucket"] for r in gold_rows[lab]) for lab, _ in allruns}
    tot = Counter()
    for lab in prim:
        tot.update(cnt[lab])
    n_prim = sum(len(gold_rows[lab]) for lab in prim)
    largest = max(BUCKETS, key=lambda b: tot[b])
    eng, mod = tot["B2"] + tot["B3"], tot["B4"]
    rec = {lab: mean(r["recall_at_k"] for r in gold_rows[lab]) for lab, _ in allruns}
    w("# Retrieval failure scorecard (2026-10-06)")
    w("")
    w(f"Deterministic, from existing traces + judgments (no engine runs, no judge calls). Generator: "
      f"`rnd/research/coordinator/tools/retrieval_scorecard.py` (re-run: `python3 -I` on it, defaults = this report). "
      f"Per-row data: `RETRIEVAL-SCORECARD-2026-10-06.items.csv`.")
    w("")
    w("## TL;DR")
    w(f"- Largest bucket: **{largest} {BUCKETS[largest]}** = {tot[largest]}/{n_prim} item-runs "
      f"({pct(tot[largest], n_prim)}) over {' + '.join(prim)} (39 gold items each).")
    w(f"- Counts per run: " + "; ".join(f"**{lab}** " + " ".join(f"{b}={cnt[lab][b]}" for b in BUCKETS)
                                         for lab, _ in allruns) + ".")
    w(f"- Engine-fixable B2+B3 = {eng} vs model-limited B4 = {mod} (primary runs pooled): "
      f"**B2+B3 {'exceeds' if eng > mod else 'does not exceed'} B4**"
      f" ({tot['B2']} ranking + {tot['B3']} dropped vs {tot['B4']} reader-fail). Per run: "
      + ", ".join(f"{lab} {cnt[lab]['B2'] + cnt[lab]['B3']} vs {cnt[lab]['B4']}" for lab, _ in allruns)
      + f" (of {len(gold_rows[prim[0]])}). Largest engine bucket: B2 ranking.")
    w(f"- recall@{k} (scorer rule, raw[:{k}]) over the 39 gold items: " +
      ", ".join(f"{lab} {rec[lab]:.3f}" for lab, _ in allruns) + ".")
    cov = sum(1 for x in gold_status.values() if x[0] in ("exact", "normalised"))
    ncov_items = sum(1 for qid, g in gold.items() if any(gold_status[x][0] in ("exact", "normalised") for x in g))
    w(f"- Coverage: {cov}/{len(gold_status)} distinct gold titles exist in the loaded packs; {ncov_items}/{len(gold)} "
      f"gold items have at least one. Gold titles are Wikipedia articles; the kit has no general Wikipedia pack (5,300 "
      f"seed-corpus articles + Wikivoyage + crypto), so most \"in pack\" hits are the Wikivoyage namesake (scorer rule).")
    w(meta["tldr_extra"])
    w("")
    w("## Bucket table (gold items, one bucket per item per run)")
    w("")
    w("| Bucket | meaning | " + " | ".join(lab for lab, _ in allruns) + " | pooled primary | mean corr (primary) |")
    w("|---|---|" + "---|" * len(allruns) + "---|---|")
    desc = {"B1": "no gold title in any loaded pack", "B2": "gold in pack, not in raw",
            "B3": "gold in raw, lost before prompt / not shown", "B4": "gold in prompt, correctness <= 2",
            "B5": "gold in prompt, correctness >= 4", "B6": "gold in prompt, correctness 3-band / declined"}
    for b in BUCKETS:
        w(f"| {b} {BUCKETS[b]} | {desc[b]} | " + " | ".join(str(cnt[lab][b]) for lab, _ in allruns)
          + f" | {tot[b]} ({pct(tot[b], n_prim)}) | "
          + (lambda m: "-" if m is None else f"{m:.2f}")(mean(r.get("correctness") for lab in prim for r in gold_rows[lab]
                                                               if r["bucket"] == b)) + " |")
    sub = Counter()
    for lab in prim:
        for r in gold_rows[lab]:
            if r["bucket"] in ("B1", "B2", "B3", "B6"):
                sub[(r["bucket"], r["bucket_note"].split(":")[0].split(" (")[0])] += 1
    w("")
    w("Sub-reasons (pooled primary): " + "; ".join(f"{b} {n}: {c}" for (b, n), c in sorted(sub.items())) + ".")
    # stability
    if len(prim) >= 2:
        a, b2 = prim[0], prim[1]
        ba = {r["item"]: r["bucket"] for r in gold_rows[a]}
        bb = {r["item"]: r["bucket"] for r in gold_rows[b2]}
        same = sum(1 for i in ba if ba[i] == bb.get(i))
        w(f"Seed stability: {a} vs {b2} same bucket on {same}/{len(ba)} items.")
        for clab, _ in cross:
            bc = {r["item"]: r["bucket"] for r in gold_rows[clab]}
            s1 = sum(1 for i in ba if ba[i] == bc.get(i))
            w(f"Cross-check {clab}: same bucket as {a} on {s1}/{len(ba)} items.")
    w("")
    w("## Per category (all 60 items; bucket, off-topic and corr columns pool the primary runs)")
    w("")
    w("| category | items | gold items | B1 | B2 | B3 | B4 | B5 | B6 | mean corr | any off-topic source |")
    w("|---|---|---|---|---|---|---|---|---|---|---|")
    allrows = [r for lab in prim for r in dict(allruns)[lab]]
    cats = sorted({r["category"] for r in allrows})
    for c in cats:
        rs = [r for r in allrows if r["category"] == c]
        gc = Counter(r["bucket"] for r in rs if r.get("n_gold"))
        nit = len(rs) // len(prim)
        ngi = sum(1 for r in rs if r.get("n_gold")) // len(prim)
        mc = mean(r.get("correctness") for r in rs)
        off = sum(r.get("any_pre_offtopic", 0) for r in rs)
        w(f"| {c} | {nit} | {ngi} | " + " | ".join(str(gc[b]) for b in BUCKETS)
          + f" | {mc:.2f} | {off}/{len(rs)} |" if mc is not None else
          f"| {c} | {nit} | {ngi} | " + " | ".join(str(gc[b]) for b in BUCKETS) + f" | - | {off}/{len(rs)} |")
    offall = sum(r.get("any_pre_offtopic", 0) for r in allrows)
    w("")
    w(f"Off-topic heuristic (pre-answer source title shares no content word with the question or gold titles): "
      f"{offall}/{len(allrows)} item-runs carry at least one; mean pre-answer sources "
      f"{mean(r.get('n_pre') for r in allrows):.2f}, raw {mean(r.get('n_raw') for r in allrows):.2f}, "
      f"prompt tokens {mean(r.get('prompt_tokens') for r in allrows):.0f}.")
    w("")
    w("## 10 most instructive items")
    w("")
    for line in meta["instructive"]:
        w(line)
    w("")
    w("## Packs used and where \"gold exists in pack\" was checked")
    w("")
    w("Desktop-node adapter (`boar-eval/adapters/desktop-node/runner/adapter.ts`, `resolveKit` + `setupAppRetrieval`) "
      "loads the request's `config.kit` packs (`<id>.sqlite` in BOAR_EVAL_PACK_DIRS, sha256-pinned) plus, with "
      "`--corpus essential` (all three runs), the engine tree's seed corpora `assets/corpus/{corpus,corpus-standard,"
      "corpus-full}.json`. Kit in the traces: " + ", ".join(f"`{x['id']}` {x['sha256'][:12]}" for x in kits) + ".")
    w("")
    w("| source | articles | sha256 (12) | kit pin ok | checked file |")
    w("|---|---|---|---|---|")
    pins = {x["id"]: x["sha256"] for x in kits}
    for label, path, h, n, name in packidx.sources:
        pid = label.replace(".sqlite", "")
        ok = ("yes" if pins.get(pid) == h else "MISMATCH") if pid in pins else "n/a (engine 0cfd4a77 blob)"
        w(f"| {label} ({name}) | {n} | {h[:12]} | {ok} | `{os.path.relpath(path, ROOT)}` |")
    w("")
    w("Lookup: `articles.title` (exact, then NOCASE + whitespace normalisation = the scorer's rule) on each SQLite "
      "pack, read-only; titles of each JSON corpus. Near-misses (not counted as present): `Gold (qualifier)` titles, "
      "punctuation-only differences, and `redirects` rows pointing to a differently titled article.")
    w("")
    st = Counter(v[0] for v in gold_status.values())
    w(f"Gold title status ({len(gold_status)} distinct): " + ", ".join(f"{k2} {v}" for k2, v in sorted(st.items())) + ".")
    for x, (s, where, det) in sorted(gold_status.items()):
        if s in ("normalised", "near-miss"):
            w(f"- `{x}`: {s} ({det})")
    w("")
    w("## What engine work would move which bucket")
    w("")
    for line in meta["levers"]:
        w(line)
    w("")
    w("## UNKNOWN / caveats")
    for line in meta["caveats"]:
        w(line)
    return "\n".join(L) + "\n"


def short(s, n=60):
    s = str(s or "")
    return s if len(s) <= n else s[: n - 1] + "…"


def instructive(runs, gold_status, n=10):
    """Deterministic pick: per-bucket quotas (B3 2, B2 3, B4 2, B1 2, B6 1, then fill), bucket stable across the
    primary runs first; B2 ranked by raw titles adjacent to the gold (shared word), B1 by off-topic prompt sources."""
    by = {}
    for lab, rows in runs:
        for r in rows:
            if r.get("n_gold"):
                by.setdefault(r["item"], []).append(r)
    quota = OrderedDict([("B3", 2), ("B2", 3), ("B4", 2), ("B1", 2), ("B6", 1), ("B5", 0)])

    def key(qid, rs):
        r = rs[0]
        stable = len({x["bucket"] for x in rs}) == 1
        gw = set().union(*(words(x) for x in r["gold"].split("|")))
        adj = sum(1 for x in r["raw_titles"].split("|") if x and words(bare(x)) & gw)
        score = {"B2": -adj, "B1": -int(r.get("n_pre_offtopic") or 0)}.get(r["bucket"], 0)
        return (0 if stable else 1, score, qid)

    ranked = {b: sorted((key(q, rs), q, rs) for q, rs in by.items() if rs[0]["bucket"] == b) for b in quota}
    picked = []
    for b, qn in quota.items():
        picked += [(q, rs) for _, q, rs in ranked[b][:qn]]
    rest = [(k2, q, rs) for b in quota for k2, q, rs in ranked[b] if q not in {p for p, _ in picked}]
    picked += [(q, rs) for _, q, rs in sorted(rest, key=lambda x: x[0])][: max(0, n - len(picked))]
    picked = picked[:n]
    lines = []
    for qid, rs in picked:
        r = rs[0]
        bs = "/".join(x["bucket"] for x in rs)
        cs = "/".join("-" if x.get("correctness") is None else f"{x['correctness']:g}" for x in rs)
        raw = short(", ".join(uniq(bare(x) for x in r["raw_titles"].split("|") if x)) or "(nothing)", 70)
        pre = short(", ".join(uniq(bare(x) for x in r["pre_titles"].split("|") if x)) or "(nothing)", 50)
        note = r["bucket_note"]
        lines.append(f"- `{qid}` [{r['category']}] {bs}, corr {cs}: gold `{r['gold']}` -> raw: {raw}; "
                     f"prompt: {pre}." + (f" ({short(note, 90)})" if note else ""))
    return lines


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--run", action="append", help="label=TRACES[,JUDGMENTS] (primary; repeatable)")
    ap.add_argument("--cross", action="append", help="label=TRACES[,JUDGMENTS] (cross-check; repeatable)")
    ap.add_argument("--no-cross", action="store_true")
    ap.add_argument("--questions", default=DEF_QUESTIONS)
    ap.add_argument("--gold", default=DEF_GOLD)
    ap.add_argument("--pack", action="append", help="SQLite pack (repeatable)")
    ap.add_argument("--corpus-json", action="append", help="JSON corpus [{title,…}] (repeatable)")
    ap.add_argument("--k", type=int, default=5)
    ap.add_argument("--out-md", default=DEF_MD)
    ap.add_argument("--out-csv", default=DEF_CSV)
    a = ap.parse_args(argv)

    def parse(specs):
        out = []
        for s in specs:
            lab, _, paths = s.partition("=")
            tp, _, jp = paths.partition(",")
            out.append((lab, tp, jp or None))
        return out

    run_specs = parse(a.run or DEF_RUNS)
    cross_specs = [] if a.no_cross else parse(a.cross or ([] if a.run else DEF_CROSS))
    items = OrderedDict((q["id"], q) for q in read_jsonl(a.questions))
    gold = {k2: v for k2, v in json.load(open(a.gold, encoding="utf-8")).items() if not k2.startswith("_") and v}
    gold = {k2: v for k2, v in gold.items() if k2 in items}
    packidx = PackIndex(a.pack or DEF_PACKS, a.corpus_json or DEF_CORPORA)
    gold_status = {x: packidx.lookup(x) for g in gold.values() for x in g}

    runs, cross, kits = [], [], []
    for specs, dst in ((run_specs, runs), (cross_specs, cross)):
        for lab, tp, jp in specs:
            rows, kit, _ = score_run(lab, tp, jp, items, gold, packidx, gold_status, a.k)
            dst.append((lab, rows))
            if kit and not kits:
                kits = kit
            if kit and kit != kits:
                print(f"warning: {lab} kit differs from the first run's kit: {kit}", file=sys.stderr)

    allrows = [r for _, rows in runs + cross for r in rows]
    fields = []
    for r in allrows:
        for f in r:
            if f not in fields:
                fields.append(f)
    buf = io.StringIO()
    wr = csv.DictWriter(buf, fieldnames=fields, lineterminator="\n")
    wr.writeheader()
    for r in allrows:
        wr.writerow(r)
    with open(a.out_csv, "w", encoding="utf-8") as f:
        f.write(buf.getvalue())

    # computed narrative pieces
    prim = runs
    pooled = Counter(r["bucket"] for _, rows in prim for r in rows if r.get("n_gold"))
    b3d = sum(1 for _, rows in prim for r in rows if r.get("bucket") == "B3" and r["bucket_note"].startswith("B3-drop"))
    b3h = sum(1 for _, rows in prim for r in rows if r.get("bucket") == "B3" and r["bucket_note"].startswith("B3-hidden"))
    n_gold_rows = sum(pooled.values())
    reached = pooled["B4"] + pooled["B5"] + pooled["B6"]
    meta = {}
    meta["tldr_extra"] = (f"- Gold reached the prompt in {reached}/{n_gold_rows} item-runs; when it did, the 4B "
                          f"answered right (B5) {pooled['B5']} times and wrong (B4) {pooled['B4']}.")
    meta["instructive"] = instructive(prim, gold_status)
    meta["levers"] = [
        f"- **B1 coverage ({pooled['B1']}) -> packs, not engine.** Only a Wikipedia pack (or adding the gold articles "
        f"to the seed corpora) moves it. Near-miss B1s are title-format gaps (Wikivoyage destination vs the Wikipedia "
        f"article), still pack work.",
        f"- **B2 ranking ({pooled['B2']}) -> retrieval engine.** Title/lead boost for an exact entity match (the gold "
        f"title is a query n-gram in most of these), FTS+vector fusion weights, raising k, per-article dedup so one "
        f"article cannot fill all k slots (see repeated `Lisbon Airport` x4).",
        f"- **B3 dropped ({pooled['B3']}: {b3d} drop, {b3h} hidden) -> gates/context packing.** Off-topic/grounding "
        f"gates (`grounding:off-topic-dropped-N`), context budget (`context:A->B`), citation pruning "
        f"(`citations:removed-N`). Cheapest engine lever when non-zero: the right passage was already retrieved.",
        f"- **B4 reader-fail ({pooled['B4']}) -> model / prompt.** Gold was in the prompt and the 4B still scored <= 2: "
        f"bigger/deep tier, better passage selection inside the article (section-level chunks), or answer prompt.",
        f"- **B5/B6 ({pooled['B5']}/{pooled['B6']})** are not retrieval losses; B6 is mostly the correctness-3 band.",
        "- Upside check: mean correctness is already " + ", ".join(
            f"{b} {m:.2f}" for b, m in ((b, mean(r.get("correctness") for _, rows in prim for r in rows
                                                if r.get("bucket") == b)) for b in ("B2", "B3")) if m is not None)
        + " (the 4B answers many of these from parametric memory). B3 items and their gate codes: " + "; ".join(sorted({
            f"`{r['item']}` " + ",".join(c for c in r["reason_codes"].split("|") if "dropped" in c or "card" in c)
            for _, rows in prim for r in rows if r.get("bucket") == "B3"})) + ".",
        f"- Ceiling arithmetic: engine work (B2+B3) can at most promote {pooled['B2'] + pooled['B3']} of "
        f"{n_gold_rows} gold item-runs into the prompt; B1 ({pooled['B1']}) is unreachable without packs.",
    ]
    meta["caveats"] = [
        "- Gold exists for 39/60 items only; the 21 others (crypto, honesty, danger, food, travel-local…) have no "
        "bucket, only the descriptive fields in the CSV.",
        "- The ctl judgments are `judge.v1-med` reused from text-identical speedpack answers (prep.json); treated as "
        "the judgments of these traces.",
        "- Correctness = mean of both orders; 3-band includes 3.5 and 2.5 is B4 only if <= 2 (2.5 -> B6).",
        "- Section-level gold is not used (no gold entry has `#section`); a hit on the gold article counts even if the "
        "retrieved chunk is an irrelevant section.",
        "- Off-topic is a lexical heuristic on titles; it flags `Wikivoyage: Narva` for Singapore correctly but also "
        "flags legit titles that share no word with the question.",
        "- UNKNOWN: whether the seed corpora were fully indexed on the runner (we assume seedKnowledgeBaseIfEmpty "
        "indexed all 5,300 titles); pack presence is title-level, not chunk-level.",
    ]
    md = render_md(runs, cross, packidx, gold, gold_status, a.k, kits, meta)
    with open(a.out_md, "w", encoding="utf-8") as f:
        f.write(md)
    print(f"wrote {a.out_md} ({md.count(chr(10))} lines) and {a.out_csv} ({len(allrows)} rows)")
    for lab, rows in runs + cross:
        c = Counter(r["bucket"] for r in rows if r.get("n_gold"))
        print(lab, " ".join(f"{b}={c[b]}" for b in BUCKETS), "n_gold", sum(c.values()))


if __name__ == "__main__":
    main()
