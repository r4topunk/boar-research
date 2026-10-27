#!/usr/bin/env python3
"""FTDATA pilot teacher: two `claude -p` calls per example (model opus, all tools disabled, no MCP, no settings,
custom system prompt, CLI login auth; API-key env vars are stripped from the child env).
  call 1 (question): sees ONLY the gold passages, writes one natural user question of a seeded type.
  call 2 (answer):   sees ONLY the question + all passages (gold + any distractor), answers per the criterion.
Wall seconds and token usage are recorded per call. Sequential, 2 s gap, one retry per call, then failed.
Resumable: ids already in the output are skipped. Usage: python3 teach.py [passages.jsonl] [teacher-raw.jsonl]
"""
import json, os, random, subprocess, sys, time
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
INP = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / "passages-50.jsonl"
OUT = Path(sys.argv[2]) if len(sys.argv) > 2 else HERE / "teacher-raw.jsonl"
SEED, GAP_S, TIMEOUT_S = 46, 2, 300
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
- Write 120 to 220 words of plain prose (no headings, no bullet lists, no URLs).
- Every number, date and name you write must be taken from the passages, written as it appears there. Do not compute
  or estimate new numbers.
- If the question asks for something the passages do not contain, say that it is "not in the passages" and answer
  the rest.
- Some passages may be unrelated to the question; ignore them.

Passages:
{passages}

Question: {question}

Answer:"""


def fmt(ps):
    return "\n\n".join(f"[{i + 1}] {p['title']}\n{p['text']}" for i, p in enumerate(ps))


def call(system, prompt):
    env = {k: v for k, v in os.environ.items() if k not in STRIP}
    last = None
    for attempt in (1, 2):
        t0 = time.time()
        try:
            r = subprocess.run(CMD + ["--system-prompt", system], input=prompt, capture_output=True, text=True,
                               timeout=TIMEOUT_S, env=env, cwd="/tmp")
            sec = round(time.time() - t0, 2)
            d = json.loads(r.stdout)
            if d.get("is_error") or not (d.get("result") or "").strip():
                raise RuntimeError(f"is_error={d.get('is_error')} subtype={d.get('subtype')} result={str(d.get('result'))[:200]}")
            u = d.get("usage", {})
            return {"ok": True, "text": d["result"].strip(), "seconds": sec, "attempts": attempt,
                    "tokens": {"input": u.get("input_tokens", 0), "cache_creation": u.get("cache_creation_input_tokens", 0),
                               "cache_read": u.get("cache_read_input_tokens", 0), "output": u.get("output_tokens", 0)},
                    "model": list(d.get("modelUsage", {}).keys()),
                    "web_requests": u.get("server_tool_use", {}), "num_turns": d.get("num_turns")}
        except Exception as e:  # noqa: BLE001
            last = f"{type(e).__name__}: {e}"[:400]
            time.sleep(GAP_S * 3)
    return {"ok": False, "error": last, "seconds": None, "attempts": 2}


def main():
    rows = [json.loads(l) for l in INP.read_text().splitlines() if l.strip()]
    done = {json.loads(l)["id"] for l in OUT.read_text().splitlines() if l.strip()} if OUT.exists() else set()
    rng = random.Random(SEED)
    types = [TYPES[i % 4] for i in range(len(rows))]
    rng.shuffle(types)
    for row, qtype in zip(rows, types):
        if row["id"] in done:
            continue
        gold = [p for p in row["passages"] if p["role"] == "gold"]
        q = call(Q_SYSTEM, Q_PROMPT.format(qtype=qtype, qhint=Q_HINTS[qtype], passages=fmt(gold)))
        time.sleep(GAP_S)
        a = call(A_SYSTEM, A_PROMPT.format(passages=fmt(row["passages"]), question=q.get("text", ""))) if q["ok"] else \
            {"ok": False, "error": "question call failed", "seconds": None, "attempts": 0}
        rec = {"id": row["id"], "qtype": qtype, "question_call": q, "answer_call": a,
               "question": q.get("text"), "answer": a.get("text")}
        with OUT.open("a") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
        print(row["id"], qtype, q.get("seconds"), a.get("seconds"), a["ok"], flush=True)
        time.sleep(GAP_S)


if __name__ == "__main__":
    main()
