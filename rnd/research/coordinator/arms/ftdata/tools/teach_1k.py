#!/usr/bin/env python3
"""FTDATA 1k teacher (copy of the pilot teach.py; criterion FTDATA-1K-criterion.md sha 1a6b43dc...): two `claude -p` calls per example (model opus, all tools disabled, no MCP, no settings,
custom system prompt, CLI login auth; API-key env vars are stripped from the child env).
  call 1 (question): sees ONLY the gold passages, writes one natural user question of a seeded type.
  call 2 (answer):   sees ONLY the question + all passages (gold + any distractor), answers per the criterion.
Wall seconds and token usage are recorded per call. Sequential, 2 s gap, one retry per call, then failed.
Resumable: ids already in the output are skipped. Usage: python3 teach_1k.py [passages.jsonl] [teacher-raw.jsonl]
1k changes vs pilot: A_PROMPT edits (1) 120-200 words + "never more than 200 words", (2) disclaimer instruction replaced;
qtype shuffle seed 47; transient 429/rate-limit/overload: back off 30/60/120 s, max 3 retries per call, logged;
stop rule checked after 100 completed examples and every 200 after (pass < 0.60, median > 30 s), plus any web request
or a rate-limit run > 10 min (checked on every call); prompt sha verified against ../prompt-1k.sha256 before the run.
`python3 teach_1k.py --write-prompt` writes ../prompt-1k.txt and ../prompt-1k.sha256.
"""
import hashlib, re
import json, os, random, statistics, subprocess, sys, time
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
ARGS = [a for a in sys.argv[1:] if not a.startswith("--")]
INP = Path(ARGS[0]) if len(ARGS) > 0 else HERE / "passages-1k.jsonl"
OUT = Path(ARGS[1]) if len(ARGS) > 1 else HERE / "teacher-raw-1k.jsonl"
PROMPT_FILE, PROMPT_SHA = HERE / "prompt-1k.txt", HERE / "prompt-1k.sha256"
SEED, GAP_S, TIMEOUT_S = 47, 2, 300
RL_BACKOFF = [30, 60, 120]  # seconds before retry 1/2/3 on a transient 429 / rate limit / overload
RL_RUN_MAX_S = 600
CHECKPOINTS = {100, 300, 500, 700, 900}
RL_PAT = re.compile(r"\b429\b|\b529\b|rate.?limit|usage limit|overloaded|too many requests", re.I)
TYPES = ["fact", "explanation", "comparison", "how-to"]
STRIP = ["ANTHROPIC_API_KEY", "ANTHROPIC_AUTH_TOKEN", "ANTHROPIC_BASE_URL", "AI_GATEWAY_API_KEY", "VERCEL_AI_GATEWAY",
         "VERCEL_OIDC_TOKEN", "OPENAI_API_KEY"]
CMD = ["claude", "-p", "--model", "opus", "--tools", "", "--strict-mcp-config", "--setting-sources", "",
       "--no-session-persistence", "--output-format", "json"]

Q_SYSTEM = "You write evaluation questions. You have no tools. Output only the question, nothing else."
Q_PROMPT = """Below are passages from an offline encyclopedia/travel/technical/preparedness library.
Write ONE natural English question that a curious user of an offline research assistant might type, which can be
answered well from these passages alone. Question type: {qtype} ({qhint}).
Rules: do not mention "the passage", "the text" or "the article"; name the subject explicitly; one sentence; no
yes/no question; the answer should need several facts from the passages.

{passages}

Output only the question."""
Q_HINTS = {"fact": "asks for specific facts such as who/what/when/where/how many",
           "explanation": "asks why or how something works or happened",
           "comparison": "asks to compare two things, periods, options or aspects mentioned in the passages",
           "how-to": "asks how to do, plan or prepare for something; if the passages are not practical, ask how something is done or used"}

A_SYSTEM = "You are a careful research assistant. You have no tools and no internet. You answer only from the passages given."
A_PROMPT = """Answer the user's question using ONLY the passages below. Do not use outside knowledge.
- Write 120 to 200 words of plain prose (no headings, no bullet lists, no URLs); never more than 200 words.
- Every number, date and name you write must be taken from the passages, written as it appears there. Do not compute
  or estimate new numbers.
- Answer only what is asked. If a part of the question is not covered by the passages, leave it out; do not announce
  what is missing.
- Some passages may be unrelated to the question; ignore them.

Passages:
{passages}

Question: {question}

Answer:"""


def fmt(ps):
    return "\n\n".join(f"[{i + 1}] {p['title']}\n{p['text']}" for i, p in enumerate(ps))


class StopRun(Exception):
    pass


RL = {"run_start": None}


def hhmm():
    return subprocess.run(["date", "+%H:%M"], capture_output=True, text=True).stdout.strip()


def log(msg):
    print(f"[{hhmm()}] {msg}", flush=True)


def call(system, prompt):
    env = {k: v for k, v in os.environ.items() if k not in STRIP}
    last, other_fails, rl_retries, attempt = None, 0, 0, 0
    while True:
        attempt += 1
        t0 = time.time()
        r = None
        try:
            r = subprocess.run(CMD + ["--system-prompt", system], input=prompt, capture_output=True, text=True,
                               timeout=TIMEOUT_S, env=env, cwd="/tmp")
            sec = round(time.time() - t0, 2)
            d = json.loads(r.stdout)
            if d.get("is_error") or not (d.get("result") or "").strip():
                raise RuntimeError(f"is_error={d.get('is_error')} subtype={d.get('subtype')} result={str(d.get('result'))[:200]}")
            u = d.get("usage", {})
            web = u.get("server_tool_use", {}) or {}
            RL["run_start"] = None
            if sum(v for v in web.values() if isinstance(v, (int, float))) > 0:
                log(f"STOP: web request recorded {web}")
                raise StopRun("web_request")
            return {"ok": True, "text": d["result"].strip(), "seconds": sec, "attempts": attempt, "rl_retries": rl_retries,
                    "tokens": {"input": u.get("input_tokens", 0), "cache_creation": u.get("cache_creation_input_tokens", 0),
                               "cache_read": u.get("cache_read_input_tokens", 0), "output": u.get("output_tokens", 0)},
                    "model": list(d.get("modelUsage", {}).keys()),
                    "web_requests": web, "num_turns": d.get("num_turns")}
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
                if rl_retries < len(RL_BACKOFF):
                    wait = RL_BACKOFF[rl_retries]
                    rl_retries += 1
                    log(f"RATE-LIMIT retry {rl_retries}/3 in {wait} s: {last[:160]}")
                    time.sleep(wait)
                    continue
                log(f"RATE-LIMIT: 3 retries exhausted, call failed: {last[:160]}")
                return {"ok": False, "error": last, "seconds": None, "attempts": attempt, "rl_retries": rl_retries}
            other_fails += 1
            log(f"call error {other_fails}/2: {last[:200]}")
            if other_fails >= 2:
                return {"ok": False, "error": last, "seconds": None, "attempts": attempt, "rl_retries": rl_retries}
            time.sleep(GAP_S * 3)


def prompt_text():
    return f"# system\n{A_SYSTEM}\n# user (template; {{passages}} and {{question}} are filled per example)\n{A_PROMPT}"


def checkpoint(rows_by_id, final=False):
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from fidelity_filter_1k import evaluate, summarize
    raw = [json.loads(l) for l in OUT.read_text().splitlines() if l.strip()]
    s = summarize([evaluate(rows_by_id[t["id"]], t) for t in raw])
    fire = []
    if s["pass_rate"] < 0.60:
        fire.append("pass<0.60")
    if s["median_seconds_per_example"] is None or s["median_seconds_per_example"] > 30:
        fire.append("median>30s")
    if s["web_requests"] > 0:
        fire.append("web_request")
    verdict = ("FINAL " if final else "") + ("STOP " + ",".join(fire) if fire else "CONTINUE")
    log(f"CHECKPOINT n={s['n']} pass={s['pass']}/{s['n']}={s['pass_rate']} median_s={s['median_seconds_per_example']} "
        f"web={s['web_requests']} rl_retries={s['rate_limit_retries']} disclaimer_rate_passing={s['disclaimer_rate_passing']} "
        f"trimmed={s['trimmed']} causes={s['failure_causes']} -> {verdict}")
    if fire and not final:
        raise StopRun(",".join(fire))


def main():
    if "--write-prompt" in sys.argv:
        PROMPT_FILE.write_text(prompt_text())
        PROMPT_SHA.write_text(hashlib.sha256(PROMPT_FILE.read_bytes()).hexdigest() + "  prompt-1k.txt\n")
        print(PROMPT_SHA.read_text().strip())
        return
    sha = hashlib.sha256(prompt_text().encode()).hexdigest()
    if PROMPT_SHA.read_text().split()[0] != sha or PROMPT_FILE.read_text() != prompt_text():
        sys.exit(f"prompt mismatch vs {PROMPT_SHA}: {sha}")
    log(f"START prompt sha {sha[:12]} out={OUT.name}")
    rows = [json.loads(l) for l in INP.read_text().splitlines() if l.strip()]
    rows_by_id = {r["id"]: r for r in rows}
    done = {json.loads(l)["id"] for l in OUT.read_text().splitlines() if l.strip()} if OUT.exists() else set()
    rng = random.Random(SEED)
    types = [TYPES[i % 4] for i in range(len(rows))]
    rng.shuffle(types)
    completed = len(done)
    try:
        for row, qtype in zip(rows, types):
            if row["id"] in done:
                continue
            one(row, qtype)
            completed += 1
            if completed in CHECKPOINTS:
                checkpoint(rows_by_id)
    except StopRun as e:
        log(f"STOPPED ({e}) after {completed} completed examples; no restart (criterion stop rule)")
        sys.exit(3)
    checkpoint(rows_by_id, final=True)
    log(f"DONE {completed} completed")


def one(row, qtype):
    gold = [p for p in row["passages"] if p["role"] == "gold"]
    q = call(Q_SYSTEM, Q_PROMPT.format(qtype=qtype, qhint=Q_HINTS[qtype], passages=fmt(gold)))
    time.sleep(GAP_S)
    a = call(A_SYSTEM, A_PROMPT.format(passages=fmt(row["passages"]), question=q.get("text", ""))) if q["ok"] else \
        {"ok": False, "error": "question call failed", "seconds": None, "attempts": 0}
    rec = {"id": row["id"], "qtype": qtype, "question_call": q, "answer_call": a,
           "question": q.get("text"), "answer": a.get("text")}
    with OUT.open("a") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    print(row["id"], qtype, q.get("seconds"), a.get("seconds"), a["ok"], len((a.get("text") or "").split()), flush=True)
    time.sleep(GAP_S)


if __name__ == "__main__":
    main()
