#!/usr/bin/env python3
"""FTDATA-REJ: sentence-level rejection pass over the 982 passing rows of ftdata-1k.jsonl (criterion FTDATA-REJ-criterion.md,
sha a9136d94...). NEW file; ftdata-1k.jsonl and all pilot/1k tools are read-only inputs.
Verifier: `claude -p --model sonnet --effort low`, all tools disabled, no MCP, no settings, custom system prompt, CLI login
auth (API-key/gateway env stripped as in teach_1k.py), --output-format json. ONE call per example: user = passages (as the
teacher saw them) + the answer split into numbered sentences; output = JSON {"1":"S"|"U"|"C", ...}.
Sentence split = the 1k trim boundary rule (fidelity_filter_1k.SENT_END + ABBREV, imported unchanged).
Parse strictly (exact key set 1..n, values S/U/C); one retry on malformed JSON; transient 429/rate limit/overload:
back off 30/60/120 s, max 3 retries, logged; a rate-limit run > 10 min or any web request stops the run.
Subcommands:
  --write-prompt          write ../rej-prompt.txt + ../rej-prompt.sha256 (before any call)
  --split ID              print the numbered sentences of one example (no call)
  --calibrate             verifier on the 20 ids of review-sample-20.md -> ../rej-calib.jsonl; score vs ../calibration-map.json
  --run                   verifier on all 982 passing rows -> ../rej-raw.jsonl (checkpoint, resumable)
  --build                 ../rej-raw.jsonl -> ../ftdata-1k-rej.jsonl + summary; --sample -> ../review-sample-20b.md
"""
import hashlib, json, os, random, re, statistics, subprocess, sys, time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fidelity_filter_1k import SENT_END, ABBREV, check  # noqa: E402  (1k filter, unchanged)

HERE = Path(__file__).resolve().parent.parent
DATA = HERE / "ftdata-1k.jsonl"
DATA_SHA = "1df13cc68ec11d98d793ca4dfbb50ff13999ac2be2863fbd8d8b8f5417543b7d"
PROMPT_FILE, PROMPT_SHA = HERE / "rej-prompt.txt", HERE / "rej-prompt.sha256"
CALIB_OUT, CALIB_MAP, RAW_OUT = HERE / "rej-calib.jsonl", HERE / "calibration-map.json", HERE / "rej-raw.jsonl"
OUT, SAMPLE = HERE / "ftdata-1k-rej.jsonl", HERE / "review-sample-20b.md"
CALIB_IDS = ["ft1k-0112", "ft1k-0137", "ft1k-0160", "ft1k-0171", "ft1k-0200", "ft1k-0316", "ft1k-0330", "ft1k-0456",
             "ft1k-0527", "ft1k-0557", "ft1k-0571", "ft1k-0581", "ft1k-0686", "ft1k-0741", "ft1k-0744", "ft1k-0794",
             "ft1k-0827", "ft1k-0841", "ft1k-0911", "ft1k-0979"]  # review-sample-20.md (seed 48): BURNT for review
CLEAN_IDS = ["ft1k-0112", "ft1k-0686", "ft1k-0794", "ft1k-0841"]
MIN_KEEP_W, SAMPLE_SEED, SAMPLE_N = 100, 50, 20
GAP_S, TIMEOUT_S, RL_BACKOFF, RL_RUN_MAX_S = 1, 300, [30, 60, 120], 600
RL_PAT = re.compile(r"\b429\b|\b529\b|rate.?limit|usage limit|overloaded|too many requests", re.I)
STRIP = ["ANTHROPIC_API_KEY", "ANTHROPIC_AUTH_TOKEN", "ANTHROPIC_BASE_URL", "AI_GATEWAY_API_KEY", "VERCEL_AI_GATEWAY",
         "VERCEL_OIDC_TOKEN", "OPENAI_API_KEY"]
CMD = ["claude", "-p", "--model", "sonnet", "--effort", "low", "--tools", "", "--strict-mcp-config", "--setting-sources", "",
       "--no-session-persistence", "--output-format", "json"]

SYSTEM = """You are a strict fact-checker. You have no tools and no internet. You judge each numbered sentence of an answer ONLY against the passages given, never against your own knowledge.
Label every sentence with exactly one letter:
S = SUPPORTED: everything the sentence claims is stated in the passages or is a direct restatement of what they state.
U = UNSUPPORTED: some part of the sentence is not stated in the passages and does not follow directly from them. Borderline = UNSUPPORTED. The following all count as UNSUPPORTED: interpretive framing or characterisation; intensifiers or a stronger/weaker word than the passage uses; causal links or consequences not stated in the passages; placement, ranking, ordering or timing claims not stated; generalisations; added intent or purpose; joining facts from different passages into a link the passages do not make; facts or advice from outside knowledge.
C = CONTRADICTED: some part of the sentence conflicts with the passages. C takes precedence over U.
Conventions: pure connectives ("From there", "In this way") are not claims; arithmetic comparisons read directly off a passage table count as SUPPORTED.
Output ONLY a JSON object mapping every sentence number (as a string) to "S", "U" or "C", for example {"1":"S","2":"U","3":"C"}. No other text."""

USER = """Passages:
{passages}

Answer sentences to check:
{sentences}

Return the JSON object for sentences 1 to {n}."""


def prompt_text():
    return f"# system\n{SYSTEM}\n# user (template; {{passages}}, {{sentences}} and {{n}} are filled per example)\n{USER}"


def fmt(ps):  # identical to teach_1k.fmt (as the teacher saw them)
    return "\n\n".join(f"[{i + 1}] {p['title']}\n{p['text']}" for i, p in enumerate(ps))


def split(text):
    """Sentence spans [(start, end)] using the 1k trim boundary rule; trailing text without an end mark is one sentence."""
    spans, start = [], 0
    for m in SENT_END.finditer(text):
        last = text[:m.start() + 1].split()[-1].lstrip("\"'“‘([")
        if ABBREV.fullmatch(last.rstrip("\"'”’)]")):
            continue
        if text[start:m.end()].strip():
            spans.append((start, m.end()))
        start = m.end()
    if text[start:].strip():
        spans.append((start, len(text)))
    out = []
    for s, e in spans:  # strip leading whitespace into the separator
        seg = text[s:e]
        s2 = s + (len(seg) - len(seg.lstrip()))
        out.append((s2, e))
    return out


def sentences(text):
    return [text[s:e] for s, e in split(text)]


def rebuild(text, keep):
    """Join kept sentences, keeping the original whitespace that preceded each kept sentence (paragraph breaks)."""
    sp = split(text)
    parts, gaps = [], []
    for i, (s, e) in enumerate(sp):
        if i > 0:
            gaps.append(text[sp[i - 1][1]:s])  # whitespace gaps since the last kept sentence
        if not keep[i]:
            continue
        if parts:
            sep = "".join(gaps)
            parts.append("\n\n" if any("\n\n" in g for g in gaps) else ("\n" if "\n" in sep else " "))
        gaps = []
        parts.append(text[s:e])
    return "".join(parts).strip()


def hhmm():
    return subprocess.run(["date", "+%H:%M"], capture_output=True, text=True).stdout.strip()


def log(msg):
    print(f"[{hhmm()}] {msg}", flush=True)


class StopRun(Exception):
    pass


RL = {"run_start": None}


def parse(result, n):
    t = result.strip()
    t = re.sub(r"^```(?:json)?\s*|\s*```$", "", t).strip()
    d = json.loads(t)
    if not isinstance(d, dict):
        raise ValueError("not an object")
    if set(d.keys()) != {str(i) for i in range(1, n + 1)}:
        raise ValueError(f"key set mismatch: {sorted(d.keys())[:40]} vs 1..{n}")
    if any(v not in ("S", "U", "C") for v in d.values()):
        raise ValueError(f"bad values: {set(d.values())}")
    return {k: d[k] for k in sorted(d, key=int)}


def call(prompt, n):
    """One verifier call with strict parse; one retry on malformed JSON; 429 backoff. Returns record dict."""
    env = {k: v for k, v in os.environ.items() if k not in STRIP}
    rec = {"ok": False, "attempts": 0, "malformed": 0, "rl_retries": 0, "other_errors": 0, "seconds": [], "raw": []}
    while True:
        rec["attempts"] += 1
        t0, r = time.time(), None
        try:
            r = subprocess.run(CMD + ["--system-prompt", SYSTEM], input=prompt, capture_output=True, text=True,
                               timeout=TIMEOUT_S, env=env, cwd="/tmp")
            rec["seconds"].append(round(time.time() - t0, 2))
            d = json.loads(r.stdout)
            if d.get("is_error") or not (d.get("result") or "").strip():
                raise RuntimeError(f"is_error={d.get('is_error')} subtype={d.get('subtype')} result={str(d.get('result'))[:200]}")
            u = d.get("usage", {})
            web = u.get("server_tool_use", {}) or {}
            RL["run_start"] = None
            if sum(v for v in web.values() if isinstance(v, (int, float))) > 0:
                log(f"STOP: web request recorded {web}")
                raise StopRun("web_request")
            rec["model"] = list(d.get("modelUsage", {}).keys())
            rec["tokens"] = {"input": u.get("input_tokens", 0), "cache_creation": u.get("cache_creation_input_tokens", 0),
                             "cache_read": u.get("cache_read_input_tokens", 0), "output": u.get("output_tokens", 0)}
            rec["raw"].append(d["result"][:2000])
            try:
                rec["labels"] = parse(d["result"], n)
                rec["ok"] = True
                return rec
            except Exception as e:  # noqa: BLE001
                rec["malformed"] += 1
                log(f"malformed {rec['malformed']}/2: {type(e).__name__}: {str(e)[:160]}")
                if rec["malformed"] >= 2:
                    rec["error"] = f"malformed: {e}"[:300]
                    return rec
                time.sleep(GAP_S)
                continue
        except StopRun:
            raise
        except Exception as e:  # noqa: BLE001
            last = f"{type(e).__name__}: {e}"[:400]
            blob = last + ((r.stdout or "")[-2000:] + (r.stderr or "")[-2000:] if r is not None else "")
            if RL_PAT.search(blob):
                now = time.time()
                RL["run_start"] = RL["run_start"] or now
                if now - RL["run_start"] > RL_RUN_MAX_S:
                    log(f"STOP: rate-limit run > {RL_RUN_MAX_S} s ({last[:160]})")
                    raise StopRun("rate_limit_run")
                if rec["rl_retries"] < len(RL_BACKOFF):
                    wait = RL_BACKOFF[rec["rl_retries"]]
                    rec["rl_retries"] += 1
                    log(f"RATE-LIMIT retry {rec['rl_retries']}/3 in {wait} s: {last[:160]}")
                    time.sleep(wait)
                    continue
                rec["error"] = last
                log(f"RATE-LIMIT: 3 retries exhausted, call failed: {last[:160]}")
                return rec
            rec["other_errors"] += 1
            log(f"call error {rec['other_errors']}/2: {last[:200]}")
            if rec["other_errors"] >= 2:
                rec["error"] = last
                return rec
            time.sleep(GAP_S * 5)


def verify(row):
    sents = sentences(row["answer"])
    body = "\n".join(f"{i}. {s}" for i, s in enumerate(sents, 1))
    prompt = USER.format(passages=fmt(row["passages"]), sentences=body, n=len(sents))
    c = call(prompt, len(sents))
    return {"id": row["id"], "n_sentences": len(sents), "sentences": sents, **c}


def check_prompt():
    sha = hashlib.sha256(prompt_text().encode()).hexdigest()
    if not PROMPT_SHA.exists() or PROMPT_SHA.read_text().split()[0] != sha or PROMPT_FILE.read_text() != prompt_text():
        sys.exit(f"prompt mismatch vs {PROMPT_SHA}: {sha}")
    if hashlib.sha256(DATA.read_bytes()).hexdigest() != DATA_SHA:
        sys.exit("ftdata-1k.jsonl sha mismatch")
    return sha


def load_rows():
    return [json.loads(l) for l in DATA.read_text().splitlines() if l.strip()]


def run_over(rows, out):
    done = {json.loads(l)["id"] for l in out.read_text().splitlines() if l.strip()} if out.exists() else set()
    for row in rows:
        if row["id"] in done:
            continue
        rec = verify(row)
        with out.open("a") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
        lab = "".join(rec.get("labels", {}).values()) if rec["ok"] else "FAIL"
        print(row["id"], rec["n_sentences"], rec["seconds"], rec["attempts"], lab, flush=True)
        time.sleep(GAP_S)


def calib_score():
    mp = json.loads(CALIB_MAP.read_text())
    res = {r["id"]: r for r in (json.loads(l) for l in CALIB_OUT.read_text().splitlines() if l.strip())}
    flagged = {(e["id"], e["sentence_no"]) for e in mp["claims"]}
    hit = {(i, s) for i, s in flagged if res[i]["ok"] and res[i]["labels"][str(s)] in "UC"}
    clean_tot = sum(res[i]["n_sentences"] for i in CLEAN_IDS)
    clean_uc = sum(1 for i in CLEAN_IDS if res[i]["ok"] for v in res[i]["labels"].values() if v in "UC")
    per = []
    for i in CALIB_IDS:
        r = res[i]
        f = sorted(s for j, s in flagged if j == i)
        uc = [int(k) for k, v in r.get("labels", {}).items() if v in "UC"]
        per.append({"id": i, "sentences": r["n_sentences"], "flagged": f, "verifier_uc": uc,
                    "flagged_hit": sorted(set(f) & set(uc)), "extra_uc": sorted(set(uc) - set(f)), "ok": r["ok"]})
    s = {"flagged_claims": len(mp["claims"]), "flagged_sentences": len(flagged), "flagged_hit": len(hit),
         "recall": round(len(hit) / len(flagged), 3), "clean_sentences": clean_tot, "clean_uc": clean_uc,
         "false_flag": round(clean_uc / clean_tot, 3), "calls_failed": sum(not res[i]["ok"] for i in CALIB_IDS),
         "malformed": sum(res[i]["malformed"] for i in CALIB_IDS), "rl_retries": sum(res[i]["rl_retries"] for i in CALIB_IDS)}
    s["pass"] = s["recall"] >= 0.70 and s["false_flag"] <= 0.25
    return s, per


def build():
    rows = {r["id"]: r for r in load_rows() if r["pass"]}
    raw = {r["id"]: r for r in (json.loads(l) for l in RAW_OUT.read_text().splitlines() if l.strip())}
    out = []
    for rid, row in rows.items():
        v = raw.get(rid)
        sents = sentences(row["answer"])
        rec = dict(row)
        rec["sentences_total"] = len(sents)
        if not v or not v["ok"]:
            rec.update(sentences_deleted=None, deleted_nos=None, answer_rej=None, words_rej=0, kept=False,
                       filter_rej_pass=False, filter_rej_reason=["verifier_failed"], verifier_ok=False)
            out.append(rec)
            continue
        assert v["sentences"] == sents, rid
        dele = [int(k) for k, lab in v["labels"].items() if lab in "UC"]
        keep = [str(i) not in {str(d) for d in dele} for i in range(1, len(sents) + 1)]
        ans = rebuild(row["answer"], keep)
        w = len(ans.split())
        c = check(ans, row["passages"]) if ans else {"pass": False, "reason": ["empty"]}
        rec.update(sentences_deleted=len(dele), deleted_nos=sorted(dele), labels=v["labels"], answer_rej=ans, words_rej=w,
                   kept=(w >= MIN_KEEP_W and 1 not in dele), filter_rej_pass=c["pass"], filter_rej_reason=c["reason"],
                   verifier_ok=True)
        out.append(rec)
    OUT.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in out))
    ok = [r for r in out if r["verifier_ok"]]
    kept = [r for r in out if r["kept"]]
    tot = sum(r["sentences_total"] for r in ok)
    dl = sum(r["sentences_deleted"] for r in ok)
    vr = list(raw.values())
    secs = [s for r in vr for s in r["seconds"]]
    from collections import Counter
    s = {"rows": len(out), "verifier_ok": len(ok), "verifier_failed": len(out) - len(ok), "kept": len(kept),
         "kept_filter_pass": sum(r["filter_rej_pass"] for r in kept),
         "kept_filter_fail_reasons": dict(Counter(x.split(":")[0] for r in kept for x in r["filter_rej_reason"])),
         "dropped_first_sentence": sum(1 for r in ok if 1 in r["deleted_nos"]),
         "dropped_lt100w": sum(1 for r in ok if r["words_rej"] < MIN_KEEP_W),
         "median_words_before_kept": statistics.median(r["words"] for r in kept) if kept else None,
         "median_words_after_kept": statistics.median(r["words_rej"] for r in kept) if kept else None,
         "median_words_after_all_ok": statistics.median(r["words_rej"] for r in ok) if ok else None,
         "sentences_total": tot, "sentences_deleted": dl, "pct_deleted": round(100 * dl / tot, 1) if tot else None,
         "label_counts": dict(Counter(lab for r in ok for lab in r["labels"].values())),
         "zero_deletion_examples": sum(r["sentences_deleted"] == 0 for r in ok),
         "pct_zero_deletion": round(100 * sum(r["sentences_deleted"] == 0 for r in ok) / len(ok), 1) if ok else None,
         "calls": sum(r["attempts"] for r in vr), "malformed": sum(r["malformed"] for r in vr),
         "rl_retries": sum(r["rl_retries"] for r in vr), "other_errors": sum(r["other_errors"] for r in vr),
         "median_call_s": statistics.median(secs) if secs else None, "sum_call_s": round(sum(secs), 1),
         "models": sorted({m for r in vr for m in r.get("model", [])})}
    print(json.dumps(s, indent=1))
    return out


def sample():
    rows = [json.loads(l) for l in OUT.read_text().splitlines() if l.strip()]
    pool = [r for r in rows if r["kept"] and r["id"] not in CALIB_IDS]
    pick = sorted(random.Random(SAMPLE_SEED).sample(pool, min(SAMPLE_N, len(pool))), key=lambda r: r["id"])
    out = [f"# FTDATA-REJ: review sample ({len(pick)} kept examples, seed {SAMPLE_SEED})", ""]
    for r in pick:
        out += [f"## {r['id']}", "", "**Passages:**", ""]
        for i, p in enumerate(r["passages"], 1):
            out += [f"[{i}] {p['title']}", "", "```text", p["text"], "```", ""]
        out += [f"**Question:** {r['question']}", "", "**Answer:**", "", "```text", r["answer_rej"], "```", ""]
    SAMPLE.write_text("\n".join(out))
    print(SAMPLE, len(pick), [r["id"] for r in pick])


def main():
    a = sys.argv[1:]
    if "--write-prompt" in a:
        PROMPT_FILE.write_text(prompt_text())
        PROMPT_SHA.write_text(hashlib.sha256(PROMPT_FILE.read_bytes()).hexdigest() + "  rej-prompt.txt\n")
        print(PROMPT_SHA.read_text().strip())
    elif "--split" in a:
        rid = a[a.index("--split") + 1]
        row = next(r for r in load_rows() if r["id"] == rid)
        for i, s in enumerate(sentences(row["answer"]), 1):
            print(f"{i}. {s}")
    elif "--calibrate" in a:
        sha = check_prompt()
        log(f"CALIBRATE start prompt sha {sha[:12]}")
        rows = {r["id"]: r for r in load_rows()}
        try:
            run_over([rows[i] for i in CALIB_IDS], CALIB_OUT)
        except StopRun as e:
            log(f"STOPPED ({e})"); sys.exit(3)
        s, per = calib_score()
        log("CALIBRATE done " + json.dumps(s))
        for p in per:
            print(json.dumps(p))
    elif "--score" in a:
        s, per = calib_score()
        print(json.dumps(s))
        for p in per:
            print(json.dumps(p))
    elif "--run" in a:
        sha = check_prompt()
        log(f"RUN start prompt sha {sha[:12]}")
        try:
            run_over([r for r in load_rows() if r["pass"]], RAW_OUT)
        except StopRun as e:
            log(f"STOPPED ({e})"); sys.exit(3)
        log("RUN done")
    elif "--build" in a:
        build()
    elif "--sample" in a:
        sample()


if __name__ == "__main__":
    main()
