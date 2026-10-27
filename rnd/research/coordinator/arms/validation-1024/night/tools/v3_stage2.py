#!/usr/bin/env python3
"""V3 layer 2 stage 2 (runs ON THE MINI inside mini_queue.sh, 0 LLM): turn-2 requests from the turn-1 traces, history as ChatScreen sends it.
usage: python3 -I v3_stage2.py <job dir>   reads job.json stage2 {template, from_group, group}, out/<from_group>/traces.jsonl -> req/<group>.requests.jsonl
ChatScreen (rs-SEFIX = rs-RC src/ui-android/ChatScreen.tsx l.565-570): priorMessages = messages with text.length > 0; the last VERBATIM_MESSAGE_COUNT (6)
as {role, text} (assistant text through stripThinking: reasoning is off, nothing to strip); history = {summary: sessionSummary (null before turn 7), turns}.
The adapter passes item.history.turns as AnswerContext.history {summary: null, turns} (be/trace.ts answerContext). Turn-1 text = trace answer.text, i.e.
exactly what the user saw (banner line and [n] markers included). A failed / empty turn-1 answer leaves only the user turn (the app's text.length > 0 filter)."""
import json, sys, os
J = sys.argv[1]; M = json.load(open(J + "/job.json")); S2 = M["stage2"]
T1 = {}
for l in open(f"{J}/out/{S2['from_group']}/traces.jsonl"):
    if l.strip(): t = json.loads(l); T1[t["itemId"]] = t
out, miss = [], 0
for l in open(f"{J}/{S2['template']}"):
    r = json.loads(l); it = r["item"]; prev = it.pop("prevId")
    t = T1.get(prev); a = ((t or {}).get("answer") or {}).get("text") or ""
    q1 = (t or {}).get("question")
    if not q1: sys.exit(f"turn-1 trace missing for {prev}")
    turns = [{"role": "user", "text": q1}] + ([{"role": "assistant", "text": a}] if a else [])
    miss += not a
    it["history"] = {"turns": turns[-6:]}
    out.append(json.dumps(r, ensure_ascii=False))
p = f"{J}/req/{S2['group']}.requests.jsonl"; open(p + ".tmp", "w").write("\n".join(out) + "\n"); os.replace(p + ".tmp", p)
print(f"stage2 {len(out)} requests, empty turn-1 answers {miss}")
