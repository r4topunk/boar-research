#!/usr/bin/env python3
"""Validate emergency dev parts (SPEC.md §1) and merge them into dev.jsonl. Prints counts, near-duplicates (word Jaccard on
user turns ≥ 0.6), and shortcut checks (length / '!' / help-word rates by label). Run: python3 validate.py [--merge]"""
import json, re, sys
from collections import Counter
from pathlib import Path
H = Path(__file__).resolve().parent
KEYS = "co burn heatstroke hypothermia frostbite choking bleeding heartattack stroke seizure anaphylaxis battery eyechem electric jellyfish nosebleed earthquake drowning hypoglycemia altitude beesting scorpion marinepuncture tick animalbite heatexhaustion chokinginfant headinjury tsunami".split()
POS = {"emergency_self", "emergency_present", "emergency_remote", "poisoning", "safety_env", "security", "crisis", "ongoing_multi"}
NEG = {"howto_acute", "edu", "prep", "info", "figurative", "nonhealth_words", "past_resolved", "fiction_media", "news_history", "routine", "animal_patient", "resolved_multi", "travel_safety_info"}
F = ["id", "lang", "turns", "emergency", "howto", "cat", "cond", "sev", "person", "named", "note"]
rows, errs = [], []
for lang in ("en", "pt", "es"):
    p = H / "parts" / f"{lang}.jsonl"
    if not p.exists(): errs.append(f"missing {p.name}"); continue
    for n, l in enumerate(open(p), 1):
        if not l.strip(): continue
        try: r = json.loads(l)
        except Exception as e: errs.append(f"{lang}:{n} bad json {e}"); continue
        rows.append(r); i = r.get("id", f"{lang}:{n}")
        if list(r) != F and set(r) != set(F): errs.append(f"{i} fields {sorted(set(r) ^ set(F))}")
        t = r.get("turns") or []
        if not t or t[-1].get("role") != "user" or any(x.get("role") not in ("user", "assistant") or not x.get("text") for x in t): errs.append(f"{i} turns")
        e = r.get("emergency")
        if e not in (0, 1) or r.get("howto") not in (0, 1): errs.append(f"{i} label values")
        if e == 1 and (r["howto"] != 0 or r["cat"] not in POS or r["sev"] not in ("critical", "urgent", "minor") or r["named"] not in (0, 1) or r["person"] not in ("self", "present", "remote")): errs.append(f"{i} positive fields")
        if e == 0 and (r["cat"] not in NEG or r["sev"] is not None): errs.append(f"{i} negative fields")
        if r.get("lang") != lang or not str(i).startswith(f"ed-{lang}-"): errs.append(f"{i} lang/id")
        c = r.get("cond") or ""
        if not (c in KEYS or c == "none" or c.startswith("other:")): errs.append(f"{i} cond {c}")
ids = Counter(r["id"] for r in rows); errs += [f"dup id {k}" for k, v in ids.items() if v > 1]
print(f"rows {len(rows)}; errors {len(errs)}"); [print("  ERR", e) for e in errs[:40]]
multi = lambda r: sum(t["role"] == "user" for t in r["turns"]) >= 2
for lang in ("en", "pt", "es", "all"):
    R = [r for r in rows if lang == "all" or r["lang"] == lang]; P = [r for r in R if r["emergency"] == 1]; N = [r for r in R if r["emergency"] == 0]
    print(f"== {lang}: n {len(R)} pos {len(P)} neg {len(N)} | multi pos {sum(map(multi, P))} neg {sum(map(multi, N))} | named=0 {sum(r['named'] == 0 for r in P)}/{len(P)} | howto {sum(r['howto'] for r in N)}")
    print("   sev", dict(Counter(r["sev"] for r in P)), "person", dict(Counter(r["person"] for r in P)))
    print("   pos cat", dict(Counter(r["cat"] for r in P))); print("   neg cat", dict(Counter(r["cat"] for r in N)))
    if lang != "all":
        cov = Counter(r["cond"] for r in P); miss = [k for k in KEYS if not cov[k]]
        print(f"   card keys covered {29 - len(miss)}/29 {'missing ' + str(miss) if miss else ''}; other:* {sum(1 for r in P if r['cond'].startswith('other:'))}")
# shortcut checks on the last user turn
last = lambda r: r["turns"][-1]["text"]
HELP = re.compile(r"\b(help|urgent|emergency|socorro|urgente|emerg[êe]ncia|ayuda|emergencia|pls|please|pfv|por ?fa)\b|!", re.I)
for e in (1, 0):
    R = [r for r in rows if r["emergency"] == e]
    if R:
        L = sorted(len(last(r).split()) for r in R)
        print(f"label {e}: last-turn words median {L[len(L)//2]} p10 {L[len(L)//10]} p90 {L[9*len(L)//10]}; help/urgent/! rate {sum(bool(HELP.search(last(r))) for r in R)/len(R):.2f}")
W = lambda r: set(re.findall(r"\w+", " ".join(t["text"] for t in r["turns"] if t["role"] == "user").lower()))
near = []
for a in range(len(rows)):
    for b in range(a + 1, len(rows)):
        x, y = W(rows[a]), W(rows[b]); j = len(x & y) / max(1, len(x | y))
        if j >= 0.6: near.append((round(j, 2), rows[a]["id"], rows[b]["id"]))
print("near-duplicates (J>=0.6):", sorted(near, reverse=True)[:20] or "none")
if "--merge" in sys.argv and not errs:
    (H / "dev.jsonl").write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows)); print("wrote dev.jsonl", len(rows))
