#!/usr/bin/env python3
"""FTDATA pilot fidelity filter (deterministic, per FTDATA-PILOT-criterion.md).
Checks per example: (1) every number in the answer (digit runs incl. years, decimals) appears in the passages after
folding thousands separators/spaces ("1,234" / "1 234" -> "1234"); (2) 120-220 words; (3) no refusal; (4) no URL.
Writes pilot-50.jsonl ({id, source_titles, passages, question, answer, numbers_checked, pass, reason, seconds} + extras)
and prints pass rate, median seconds/example, tokens/example, failure causes by count.
Usage: python3 fidelity_filter.py [passages.jsonl] [teacher-raw.jsonl] [pilot-50.jsonl]
"""
import json, re, statistics, sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
P = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / "passages-50.jsonl"
T = Path(sys.argv[2]) if len(sys.argv) > 2 else HERE / "teacher-raw.jsonl"
O = Path(sys.argv[3]) if len(sys.argv) > 3 else HERE / "pilot-50.jsonl"

# URL = scheme, "www.", or a domain followed by a path. Bare domains used as names ("Ready.gov") and e-mail
# addresses copied from the passages are not URLs here; STRICT_URL (any bare domain) is reported as a sensitivity count.
URL = re.compile(r"https?://|\bwww\.|\b[\w-]+(?:\.[\w-]+)*\.(?:com|org|gov|net|io|edu|int|info)/\S", re.I)
STRICT_URL = re.compile(r"https?://|\bwww\.|\b[\w-]+\.(?:com|org|gov|net|io|edu|int|info)\b", re.I)
REFUSAL = re.compile(r"\b(I can(?:no|')t (?:help|answer|provide)|I'm unable to|I am unable to|I won't|as an AI|"
                     r"cannot answer (?:this|the question)|the passages do not (?:contain|provide) (?:any|enough) information to answer)", re.I)


def fold(s):
    # 1,234 -> 1234 ; 1 234 / 1 234 / 1 234 -> 1234 (digit-group separators only)
    return re.sub(r"(?<=\d)[,    ](?=\d{3}(?!\d))", "", s)


NUM = re.compile(r"\d+(?:\.\d+)*")  # maximal digit/dot run: "0.5.17" is one token, "3.5" one, "1990" one


def numbers(s):
    return NUM.findall(fold(s))


def in_passages(n, ptxts):
    # found if it appears as a whole number token in the folded OR the raw passages (folding can wrongly join
    # adjacent numbers such as "under 25 110 kr" -> "25110")
    pat = re.compile(r"(?<![\d.])(?<!\d\.)" + re.escape(n) + r"(?!\d|\.\d)")
    return any(pat.search(t) for t in ptxts)


def check(answer, passages):
    reasons, checked = [], []
    raw = "\n".join(p["title"] + "\n" + p["text"] for p in passages)
    ptxt = (fold(raw), raw)
    missing = []
    for n in numbers(answer):
        ok = in_passages(n, ptxt)
        checked.append({"n": n, "found": ok})
        if not ok:
            missing.append(n)
    if missing:
        reasons.append("number_not_in_passages:" + ",".join(sorted(set(missing))))
    w = len(answer.split())
    if w < 120:
        reasons.append(f"too_short:{w}")
    elif w > 220:
        reasons.append(f"too_long:{w}")
    if REFUSAL.search(answer):
        reasons.append("refusal")
    if URL.search(answer):
        reasons.append("url")
    return checked, reasons, w


def strict_url(answer):
    return STRICT_URL.search(answer) is not None


def main():
    pas = {r["id"]: r for r in map(json.loads, P.read_text().splitlines()) if r}
    raw = {r["id"]: r for r in map(json.loads, T.read_text().splitlines()) if r}
    out, causes, secs, toks = [], Counter(), [], []
    for i, base in pas.items():
        t = raw.get(i)
        rec = {"id": i, "pack": base["pack"], "source_titles": base["source_titles"], "passages": base["passages"],
               "qtype": t and t["qtype"], "question": t and t["question"], "answer": t and t["answer"]}
        if not t or not t["answer_call"]["ok"]:
            rec.update(numbers_checked=[], pass_=False, reason=["teacher_failed"], seconds=None, tokens=None, words=0)
            causes["teacher_failed"] += 1
        else:
            checked, reasons, w = check(t["answer"], base["passages"])
            qc, ac = t["question_call"], t["answer_call"]
            s = round(qc["seconds"] + ac["seconds"], 2)
            tk = {k: qc["tokens"][k] + ac["tokens"][k] for k in ac["tokens"]}
            rec.update(numbers_checked=checked, pass_=not reasons, reason=reasons, seconds=s,
                       seconds_question=qc["seconds"], seconds_answer=ac["seconds"], tokens=tk, words=w)
            rec["strict_url"] = strict_url(t["answer"])
            secs.append(s); toks.append(tk)
            for r in reasons:
                causes[r.split(":")[0]] += 1
        rec["pass"] = rec.pop("pass_")
        out.append(rec)
    O.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in out))
    n_pass = sum(r["pass"] for r in out)
    tot = lambda k: statistics.mean(t[k] for t in toks) if toks else 0  # noqa: E731
    summary = {
        "n": len(out), "pass": n_pass, "pass_rate": round(n_pass / len(out), 3),
        "median_seconds_per_example": statistics.median(secs) if secs else None,
        "p90_seconds": sorted(secs)[int(0.9 * (len(secs) - 1))] if secs else None,
        "tokens_per_example_mean": {k: round(tot(k), 1) for k in ("input", "cache_creation", "cache_read", "output")},
        "tokens_per_example_total_mean": round(sum(tot(k) for k in ("input", "cache_creation", "cache_read", "output")), 1),
        "words_median": statistics.median(r["words"] for r in out if r["words"]),
        "failure_causes": dict(causes.most_common()),
        "sensitivity_strict_url_pass": sum(r["pass"] and not r.get("strict_url") for r in out),
        "pass_by_pack": {p: f"{sum(r['pass'] for r in out if r['pack'] == p)}/{sum(r['pack'] == p for r in out)}"
                         for p in dict.fromkeys(r["pack"] for r in out)},
    }
    print(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main()
