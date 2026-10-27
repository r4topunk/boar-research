#!/usr/bin/env python3
"""Regenerate handoff/questions.vitalik-lantern.jsonl (pipeline schema) from vitalik-evalset.jsonl."""
import json
from pathlib import Path
R = Path(__file__).resolve().parent.parent
with open(R / "handoff" / "questions.vitalik-lantern.jsonl", "w") as out:
    for d in map(json.loads, open(R / "vitalik-evalset.jsonl")):
        r = {"id": d["id"], "category": d["category"], "query": d["question"], "lang": "en", "notes": " / ".join(d["rubric"]),
             "source_url": d["vitalik_source"][0],
             "license": "original (question); see reference_sources" if d["origin"] == "vitalik-style" else "quoted from the cited source (question)"}
        for k in ("grading", "grading_version", "context", "origin", "source", "fa_case_id", "duplicate_of", "upstream_expect", "reference_sources", "why_1b_fails"):
            if k in d: r[k] = d[k]
        out.write(json.dumps(r, ensure_ascii=False) + "\n")
