#!/usr/bin/env python3
"""FTDATA 1k fidelity filter (deterministic, per FTDATA-1K-criterion.md, sha 1a6b43dc...). NEW file; the pilot's
fidelity_filter.py v2 is imported unchanged for the number/URL/refusal checks (maximal digit/dot tokens, folded OR raw
passages, bare domains not URLs, strict-URL sensitivity count). Added for the 1k:
  (1) word bar 120-200 after trim; trim rule: 201-230 words -> cut at the last sentence boundary with <= 200 words
      (trimmed=true); > 230 words -> too_long (no trim); a 201-230 answer with no boundary <= 200 words -> too_long.
  (2) disclaimer phrases counted per answer (case-insensitive): "not in the passages", "passages do not",
      "passages don't" (straight or curly apostrophe); > 1 phrase fails ("disclaimers").
All checks (numbers, words, refusal, URL, disclaimers) run on the final (possibly trimmed) answer.
Usage: python3 fidelity_filter_1k.py [--completed-only] [passages-1k.jsonl] [teacher-raw-1k.jsonl] [ftdata-1k.jsonl]
  --completed-only: score only ids present in the teacher file (stop-rule checkpoints / partial file at a stop).
"""
import json, re, statistics, sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fidelity_filter import numbers, in_passages, fold, URL, STRICT_URL, REFUSAL  # noqa: E402  (pilot v2, unchanged)

HERE = Path(__file__).resolve().parent.parent
MIN_W, MAX_W, TRIM_MAX = 120, 200, 230
DISCLAIMER = re.compile(r"not in the passages|passages do not|passages don['’]t", re.I)
SENT_END = re.compile(r"[.!?][\"'”’)\]]*(?=\s|$)")
ABBREV = re.compile(r"(?:[A-Za-z]\.)+|(?:Mr|Mrs|Ms|Dr|St|Mt|Ft|vs|No|Jr|Sr|Inc|Co|Ltd|approx|ca|Gen|Col|Lt|Sgt|Capt|Rev)\.", re.I)


def trim(text):
    """Return (answer, trimmed, raw_words). Trim only 201-230-word answers, at the last sentence end <= 200 words."""
    w = len(text.split())
    if w <= MAX_W or w > TRIM_MAX:
        return text, False, w
    best = None
    for m in SENT_END.finditer(text):
        last = text[:m.start() + 1].split()[-1].lstrip("\"'“‘([")
        if ABBREV.fullmatch(last.rstrip("\"'”’)]")):  # "U.S." / "e.g." / "Dr." / initials: not a sentence end
            continue
        if len(text[:m.end()].split()) <= MAX_W:
            best = m.end()
        else:
            break
    if best is None:
        return text, False, w
    return text[:best].rstrip(), True, w


def check(answer_raw, passages):
    answer, trimmed, raw_w = trim(answer_raw)
    reasons, checked, missing = [], [], []
    raw = "\n".join(p["title"] + "\n" + p["text"] for p in passages)
    ptxt = (fold(raw), raw)
    for n in numbers(answer):
        ok = in_passages(n, ptxt)
        checked.append({"n": n, "found": ok})
        if not ok:
            missing.append(n)
    if missing:
        reasons.append("number_not_in_passages:" + ",".join(sorted(set(missing))))
    w = len(answer.split())
    if w < MIN_W:
        reasons.append(f"too_short:{w}")
    elif w > MAX_W:
        reasons.append(f"too_long:{raw_w}")
    if REFUSAL.search(answer):
        reasons.append("refusal")
    if URL.search(answer):
        reasons.append("url")
    disc = len(DISCLAIMER.findall(answer))
    if disc > 1:
        reasons.append(f"disclaimers:{disc}")
    return {"answer": answer, "trimmed": trimmed, "words": w, "answer_words_raw": raw_w, "numbers_checked": checked,
            "disclaimers": disc, "reason": reasons, "pass": not reasons, "strict_url": STRICT_URL.search(answer) is not None}


def evaluate(base, t):
    rec = {"id": base["id"], "source_titles": base["source_titles"], "pack": base["pack"], "qtype": t and t["qtype"],
           "passages": base["passages"], "question": t and t["question"], "answer": t and t["answer"]}
    if not t or not t["answer_call"]["ok"] or not t["question_call"]["ok"]:
        rec.update(words=0, trimmed=False, numbers_checked=[], disclaimers=0, **{"pass": False},
                   reason=["teacher_failed"], seconds=None, tokens=None)
        return rec
    c = check(t["answer"], base["passages"])
    qc, ac = t["question_call"], t["answer_call"]
    rec.update(answer=c["answer"], words=c["words"], trimmed=c["trimmed"], numbers_checked=c["numbers_checked"],
               disclaimers=c["disclaimers"], **{"pass": c["pass"]}, reason=c["reason"],
               seconds=round(qc["seconds"] + ac["seconds"], 2),
               tokens={k: qc["tokens"][k] + ac["tokens"][k] for k in ac["tokens"]},
               answer_words_raw=c["answer_words_raw"], strict_url=c["strict_url"],
               seconds_question=qc["seconds"], seconds_answer=ac["seconds"],
               web_requests=sum(sum((x.get("web_requests") or {}).values()) for x in (qc, ac)),
               attempts=qc.get("attempts", 1) + ac.get("attempts", 1), rate_limit_retries=qc.get("rl_retries", 0) + ac.get("rl_retries", 0))
    return rec


def summarize(out):
    n = len(out)
    ok = [r for r in out if r["seconds"] is not None]
    passing = [r for r in out if r["pass"]]
    secs = sorted(r["seconds"] for r in ok)
    tok = lambda k: round(statistics.mean(r["tokens"][k] for r in ok), 1) if ok else 0  # noqa: E731
    causes = Counter(x.split(":")[0] for r in out for x in r["reason"])
    nums = [c for r in ok for c in r["numbers_checked"]]
    by = lambda key: {v: f"{sum(r['pass'] for r in out if r[key] == v)}/{sum(r[key] == v for r in out)}"  # noqa: E731
                      for v in dict.fromkeys(r[key] for r in out)}
    ws = sorted(r["answer_words_raw"] for r in ok)
    return {
        "n": n, "teacher_ok": len(ok), "pass": len(passing), "pass_rate": round(len(passing) / n, 3) if n else None,
        "disclaimer_rate_passing": round(sum(r["disclaimers"] > 0 for r in passing) / len(passing), 3) if passing else None,
        "disclaimer_answers_all": f"{sum(r['disclaimers'] > 0 for r in ok)}/{len(ok)}",
        "disclaimer_phrases_total": sum(r["disclaimers"] for r in ok),
        "trimmed": sum(r["trimmed"] for r in ok), "trimmed_passing": sum(r["trimmed"] for r in passing),
        "median_seconds_per_example": statistics.median(secs) if secs else None,
        "p90_seconds": secs[int(0.9 * (len(secs) - 1))] if secs else None, "max_seconds": secs[-1] if secs else None,
        "tokens_per_example_mean": {k: tok(k) for k in ("input", "cache_creation", "cache_read", "output")},
        "tokens_per_example_total_mean": round(sum(tok(k) for k in ("input", "cache_creation", "cache_read", "output")), 1),
        "raw_words_min_med_max": [ws[0], ws[len(ws) // 2], ws[-1]] if ws else None,
        "final_words_median_passing": statistics.median(r["words"] for r in passing) if passing else None,
        "failure_causes": dict(causes.most_common()),
        "numbers_checked": len(nums), "numbers_missing": sum(not c["found"] for c in nums),
        "answers_with_numbers": sum(bool(r["numbers_checked"]) for r in ok),
        "sensitivity_strict_url_pass": sum(r["pass"] and not r.get("strict_url") for r in out),
        "web_requests": sum(r.get("web_requests", 0) for r in ok),
        "rate_limit_retries": sum(r.get("rate_limit_retries", 0) for r in ok),
        "pass_by_pack": by("pack"), "pass_by_qtype": by("qtype"),
    }


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    completed_only = "--completed-only" in sys.argv
    P = Path(args[0]) if len(args) > 0 else HERE / "passages-1k.jsonl"
    T = Path(args[1]) if len(args) > 1 else HERE / "teacher-raw-1k.jsonl"
    O = Path(args[2]) if len(args) > 2 else HERE / "ftdata-1k.jsonl"
    pas = [json.loads(l) for l in P.read_text().splitlines() if l.strip()]
    raw = {r["id"]: r for r in (json.loads(l) for l in T.read_text().splitlines() if l.strip())}
    out = [evaluate(b, raw.get(b["id"])) for b in pas if not completed_only or b["id"] in raw]
    O.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in out))
    print(json.dumps(summarize(out), indent=1))


if __name__ == "__main__":
    main()
