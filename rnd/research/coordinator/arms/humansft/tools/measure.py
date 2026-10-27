#!/usr/bin/env python3
"""HUMANSFT deterministic measures (criterion 83d4e9d0...) on the ANSWERABLE rows of humansft-pool.jsonl, per source.
 (b) numeric fidelity: share of answers with 0 foreign numbers. Number regex = arms/ftdata/tools/fidelity_filter.py
     (maximal digit/dot runs after folding thousands separators; found if present as a whole token in the folded OR
     raw passages). BUG FIX vs that file: its passage pattern began with (?<![\\d.]), so a number preceded by "." in
     the passages (".5", "U.S.1990", "end.1990") was never matched. Here the lookbehind is (?<!\\d)(?<!\\d\\.):
     still no match inside "3.5" for "5", but a "." not preceded by a digit no longer blocks the match.
     HAGRID citation markers ("[k]", "[1, 2]", "[1,2,3]", "[1-6]", "[1 and 2]") are removed before the check
     (they index quotes, not facts); the narrow "[k]"-only strip is reported as b_zero_foreign_share_narrow_cite.
     Passage text includes the title, as in the FTDATA filter. Bar: >= 0.98 per source.
 (d) extractiveness: share of answer word tokens (\\w+, lower-cased, citations removed) present in the passages'
     token set; median per source (report only).
 (e) words median / p25 / p75 per source (inclusive quartiles; report only).
Usage: python3 -I measure.py <pool.jsonl> <foreign-numbers.csv> <measures.json>"""
import csv, json, re, statistics, sys
from pathlib import Path

CITE = re.compile(r"\s*\[\s*\d+(?:\s*(?:,|-|\u2013|and)\s*\d+)*\s*\]")  # [k], [1, 2], [1,2,3], [1-6], [1 and 2]
NUM = re.compile(r"\d+(?:\.\d+)*")
TOK = re.compile(r"\w+")
CITE_NARROW = re.compile(r"\s*\[\d+\]")


def fold(s):  # identical to fidelity_filter.py
    return re.sub(r"(?<=\d)[,    ](?=\d{3}(?!\d))", "", s)


def numbers(s):
    return NUM.findall(fold(s))


def in_passages(n, ptxts):  # FIXED lookbehind (see docstring)
    pat = re.compile(r"(?<!\d)(?<!\d\.)" + re.escape(n) + r"(?!\d|\.\d)")
    return any(pat.search(t) for t in ptxts)


def in_passages_buggy(n, ptxts):  # original, for the bug-fix delta count only
    pat = re.compile(r"(?<![\d.])(?<!\d\.)" + re.escape(n) + r"(?!\d|\.\d)")
    return any(pat.search(t) for t in ptxts)


def q3(xs):
    q = statistics.quantiles(xs, n=4, method="inclusive")
    return {"p25": q[0], "median": statistics.median(xs), "p75": q[2]}


def main():
    pool, csv_out, js_out = map(Path, sys.argv[1:4])
    rows = [json.loads(l) for l in pool.read_text().splitlines() if l.strip()]
    per, foreign = {}, []
    for r in rows:
        if not r["answerable"]:
            continue
        s = per.setdefault(r["source"], {"n": 0, "zero_foreign": 0, "zero_foreign_buggy": 0, "zero_foreign_narrow": 0, "with_numbers": 0,
                                         "numbers": 0, "foreign_numbers": 0, "ext": [], "words": []})
        ans = CITE.sub("", r["answer"])
        raw = "\n".join((p["title"] + "\n" if p["title"] else "") + p["text"] for p in r["passages"])
        pt = (fold(raw), raw)
        nums = numbers(ans)
        miss = [n for n in nums if not in_passages(n, pt)]
        miss_b = [n for n in nums if not in_passages_buggy(n, pt)]
        an = CITE_NARROW.sub("", r["answer"])
        s["zero_foreign_narrow"] += all(in_passages(n, pt) for n in numbers(an))
        s["n"] += 1; s["numbers"] += len(nums); s["foreign_numbers"] += len(miss)
        s["with_numbers"] += bool(nums); s["zero_foreign"] += not miss; s["zero_foreign_buggy"] += not miss_b
        if miss:
            foreign.append({"id": r["id"], "source": r["source"], "foreign": " ".join(sorted(set(miss))),
                            "answer": ans[:300].replace("\n", " ")})
        at = TOK.findall(ans.lower())
        ps = set(TOK.findall(raw.lower()))
        s["ext"].append(sum(t in ps for t in at) / len(at) if at else 0.0)
        s["words"].append(r["words"])
    out = {}
    for src, s in sorted(per.items()):
        out[src] = {"answerable_rows": s["n"], "rows_with_numbers": s["with_numbers"], "number_tokens": s["numbers"],
                    "foreign_number_tokens": s["foreign_numbers"],
                    "b_zero_foreign_share": round(s["zero_foreign"] / s["n"], 4),
                    "b_bar_0.98": s["zero_foreign"] / s["n"] >= 0.98,
                    "b_zero_foreign_share_with_original_bug": round(s["zero_foreign_buggy"] / s["n"], 4),
                    "b_zero_foreign_share_narrow_cite": round(s["zero_foreign_narrow"] / s["n"], 4),
                    "d_extractive_median": round(statistics.median(s["ext"]), 4),
                    "e_words": q3(s["words"])}
    out["unanswerable_rows"] = {src: sum(1 for r in rows if r["source"] == src and not r["answerable"])
                                for src in sorted({r["source"] for r in rows})}
    with csv_out.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["id", "source", "foreign", "answer"])
        w.writeheader(); w.writerows(foreign)
    js_out.write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
