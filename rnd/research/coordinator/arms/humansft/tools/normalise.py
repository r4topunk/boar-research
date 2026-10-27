#!/usr/bin/env python3
"""HUMANSFT normalise (criterion 83d4e9d0...). Reads the raw downloads, writes humansft-pool.jsonl with
{id, source, question, passages[{title, text}], answer, answerable, words} and prints per-source counts.
Selection (per criterion):
  clapnq: train answerable (first non-empty output answer) + train unanswerable (answer "", answerable=false).
  hagrid: train answers with informative==1 AND every sentence labelled attributable==1 (labels are int or "1");
          one row per qualifying answer; passages = quotes in list order (the answer's [k] cites the k-th quote).
  dolly:  category closed_qa; passage = context (no title in file).
words = whitespace words of the answer after removing HAGRID citation markers ("[k]", "[1, 2]", "[1-6]", "[1 and 2]") (the stored answer keeps them).
Filters, in order: bench (v0.1 exclusion list, same as FTDATA sample_passages_1k.py: 65 titles + v0.1 question
texts) then length (answerable 20-220 words; unanswerable <= 40).
Bench rule: drop if any passage title is a bench title or appears (>= 4 chars, word-bounded) in a v0.1 question text,
or if the row's question contains a bench title (>= 4 chars, word-bounded) or equals a v0.1 question.
HAGRID and Dolly carry no passage titles, so only the question test applies to them (deviation, recorded).
Usage: python3 -I normalise.py <raw_root> <bench_v0.1_dir> <out_pool.jsonl> <out_counts.json>"""
import json, re, statistics, sys
from pathlib import Path
import urllib.parse

CITE = re.compile(r"\s*\[\s*\d+(?:\s*(?:,|-|\u2013|and)\s*\d+)*\s*\]")  # [k], [1, 2], [1,2,3], [1-6], [1 and 2]


def bench_exclusions(bench):  # copied from arms/ftdata/tools/sample_passages_1k.py (unchanged logic)
    titles, qtexts = set(), []
    for line in (bench / "questions.public.jsonl").read_text().splitlines():
        if not line.strip():
            continue
        q = json.loads(line)
        qtexts.append(q["question"].lower())
        for u in q.get("reference_sources", []):
            m = re.search(r"wiki(?:pedia|voyage)\.org/wiki/([^#?\s]+)", u)
            if m:
                titles.add(urllib.parse.unquote(m.group(1)).replace("_", " ").lower())
    for g in (bench / "gold").glob("*.json"):
        if g.name == "sources.json":
            continue
        d = json.loads(g.read_text())
        for k in ("city", "wikivoyage"):
            v = d.get(k) if isinstance(d, dict) else None
            if isinstance(v, str):
                titles.add(v.replace("_", " ").lower())
    return titles, qtexts


def wb(t):
    return re.compile(r"\b" + re.escape(t) + r"\b")


def jl(p):
    return [json.loads(l) for l in p.read_text().splitlines() if l.strip()]


def is1(v):
    return str(v) == "1"


def rows(raw):
    for r in jl(raw / "clapnq/clapnq_train_answerable.jsonl"):
        ans = next((o["answer"] for o in r["output"] if o["answer"].strip()), "")
        yield {"id": f"clapnq-{r['id']}", "source": "clapnq", "question": r["input"],
               "passages": [{"title": p["title"], "text": p["text"]} for p in r["passages"]],
               "answer": ans, "answerable": True}
    for r in jl(raw / "clapnq/clapnq_train_unanswerable.jsonl"):
        yield {"id": f"clapnq-{r['id']}", "source": "clapnq", "question": r["input"],
               "passages": [{"title": p["title"], "text": p["text"]} for p in r["passages"]],
               "answer": "", "answerable": False}
    for r in jl(raw / "hagrid/train.jsonl"):
        for j, a in enumerate(r["answers"]):
            if is1(a.get("informative")) and a["sentences"] and all(is1(s.get("attributable")) for s in a["sentences"]):
                yield {"id": f"hagrid-{r['query_id']}-{j}", "source": "hagrid", "question": r["query"],
                       "passages": [{"title": "", "text": q["text"]} for q in r["quotes"]],
                       "answer": a["answer"], "answerable": True}
    for i, r in enumerate(jl(raw / "dolly/databricks-dolly-15k.jsonl")):
        if r["category"] == "closed_qa":
            yield {"id": f"dolly-{i:05d}", "source": "dolly", "question": r["instruction"],
                   "passages": [{"title": "", "text": r["context"]}], "answer": r["response"], "answerable": True}


def main():
    raw, bench, out, cnt = map(Path, sys.argv[1:5])
    titles, qtexts = bench_exclusions(bench)
    tpats = [wb(t) for t in sorted(titles) if len(t) >= 4]
    qset = set(qtexts)

    def bench_hit(r):
        for p in r["passages"]:
            t = p["title"].lower()
            if t and (t in titles or (len(t) >= 4 and any(wb(t).search(q) for q in qtexts))):
                return True
        q = r["question"].lower()
        return q in qset or any(p.search(q) for p in tpats)

    counts, pool, prew = {}, [], {}
    for r in rows(raw):
        r["words"] = len(CITE.sub("", r["answer"]).split())
        k = f"{r['source']}/{'ans' if r['answerable'] else 'unans'}"
        c = counts.setdefault(k, {"selected": 0, "bench_dropped": 0, "after_bench": 0, "length_dropped": 0, "kept": 0})
        c["selected"] += 1
        if bench_hit(r):
            c["bench_dropped"] += 1; continue
        c["after_bench"] += 1
        prew.setdefault(k, []).append(r["words"])
        ok = 20 <= r["words"] <= 220 if r["answerable"] else r["words"] <= 40
        if not ok:
            c["length_dropped"] += 1; continue
        c["kept"] += 1
        pool.append(r)
    ids = [r["id"] for r in pool]
    assert len(ids) == len(set(ids)), "duplicate ids"
    out.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in pool))
    for k, w in prew.items():  # words of after-bench rows, before the length filter (inclusive quartiles)
        q = statistics.quantiles(w, n=4, method="inclusive")
        counts[k]["words_pre_length_p25_med_p75"] = [q[0], statistics.median(w), q[2]]
    res = {"bench_titles": len(titles), "bench_questions": len(qtexts), "counts": counts, "pool_rows": len(pool)}
    cnt.write_text(json.dumps(res, indent=1) + "\n")
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
