#!/usr/bin/env python3
"""Checks cards.json (DRAFT first-aid cards, EN/PT/ES) and writes REVIEW.md, the review sheet for r4to.
1. Citations: every step and every call line cites ≥ 1 source id; every id exists in cards.json "sources" with a
   verbatim quote and URL. Steps citing only '† summary-only' sources are listed.
2. Safety rules v0.9.1 (current; rounds 1–3 were first checked under v0.8.2, round 4 under v0.8.5/v0.8.6): per card and language, the card's own rule list ∪ the rules selected by topic on the card's
   topic line (rules_by_topic), checked on the full card text. Must be 0 unsafe; 'review' hits are listed.
   The CO card must also pass co-leave-and-call (omission rule: leave + call both present).
Exit 1 on any failure. Run: python3 check_cards.py [--round N]  (N=1 → REVIEW.md, N≥2 → REVIEW-N.md; checks run on all cards)
"""
import importlib.util, json, sys
from pathlib import Path

H = Path(__file__).resolve().parent
S82 = H.parent / "safety-v091"  # current rules (v0.9.1)
spec = importlib.util.spec_from_file_location("sc", S82 / "safety_check.v0.9.1.py")
sc = importlib.util.module_from_spec(spec); spec.loader.exec_module(sc)
S = sc.load(rules_path=S82 / "rules.v0.9.1.json", overlay_path=S82 / "overlay.v0.4.json")
D = json.load(open(H / "cards.json"))
ROUND = int(sys.argv[sys.argv.index("--round") + 1]) if "--round" in sys.argv else 1
REVIEW = H / ("REVIEW.md" if ROUND == 1 else f"REVIEW-{ROUND}.md")
RCARDS = [c for c in D["cards"] if c.get("round", 1) == ROUND]
SRC = D["sources"]
fails, notes, rows = [], [], []
LANGS = ("en", "pt", "es")


def card_text(c):
    return "\n".join([c["title"]] + [s["text"] for s in c["steps"]] + [c["call"]["text"]])


for card in D["cards"]:
    for lang in LANGS:
        c = card["langs"].get(lang)
        if not c:
            fails.append(f"{card['id']}/{lang}: missing language"); continue
        for k, s in enumerate(c["steps"] + [c["call"]]):
            where = f"{card['id']}/{lang}/{'call' if k == len(c['steps']) else f'step{k + 1}'}"
            if not s.get("cites"):
                fails.append(f"{where}: no citation")
            for cid in s.get("cites", []):
                if cid not in SRC:
                    fails.append(f"{where}: unknown source id {cid}")
                elif not SRC[cid].get("quote") or not SRC[cid].get("url"):
                    fails.append(f"{where}: source {cid} has no quote/url")
            if s.get("cites") and all(SRC.get(cid, {}).get("flag", "").startswith("†") for cid in s["cites"]):
                notes.append(f"{where}: only summary-only (†) sources")
        for k, s_ in enumerate(card.get("alt_steps", {}).get(lang, [])):
            if not s_.get("cites"): fails.append(f"{card['id']}/{lang}/alt{k + 1}: no citation")
            for cid in s_.get("cites", []):
                if cid not in SRC: fails.append(f"{card['id']}/{lang}/alt{k + 1}: unknown source id {cid}")
        rules = sorted(set(card.get("rules", [])) | set(sc.rules_by_topic(card["topic"][lang], S)))
        alt = "\n".join(x["text"] for x in card.get("alt_steps", {}).get(lang, []))
        hits = sc.check(card_text(c) + ("\n" + alt if alt else ""), rules, S)
        uns = [h for h in hits if h.get("status", "unsafe") == "unsafe"]
        rev = [h for h in hits if h.get("status") == "review"]
        for h in uns:
            fails.append(f"{card['id']}/{lang}: UNSAFE {h['rule']}: {h.get('match')} | {h.get('sentence', '')[:100]}")
        for h in rev:
            notes.append(f"{card['id']}/{lang}: review {h['rule']}: {h['sentence'][:100]}")
        rows.append((card["id"], lang, len(rules), len(uns), len(rev)))

with open(REVIEW, "w") as f:
    f.write(f"# First-aid cards{' round ' + str(ROUND) if ROUND > 1 else ''}: review sheet for r4to ({D['version']}, DRAFT, NOT FOR SHIPPING)\n\n")
    f.write("TL;DR: " + D["status"] + "\n\n")
    f.write("How to review: for each card, read the EN steps against the quotes below them, then PT and ES. "
            "Tick a box only if you accept the wording as is; write any change next to it. "
            "**Nothing ships without your sign-off** (and the clinical + native-speaker reviews listed at the end).\n\n")
    f.write(f"Automatic checks (check_cards.py): citations on every step = {'PASS' if not [x for x in fails if 'cit' in x or 'source' in x] else 'FAIL'}; "
            f"safety rules v0.9.1 = {'PASS (0 unsafe in all ' + str(len(rows)) + ' card-language texts, all rounds)' if not [x for x in fails if 'UNSAFE' in x] else 'FAIL'}.\n\n")
    for card in RCARDS:
        f.write(f"## {card['id']}: {card['condition']}\n")
        if card.get("covers"):
            f.write(f"Covers: {card['covers']}\n\n")
        if card.get("review_flags"):
            f.write("**Decisions for you:** " + " ".join(f"({i + 1}) {x}" for i, x in enumerate(card["review_flags"])) + "\n\n")
        for lang in LANGS:
            c = card["langs"][lang]
            f.write(f"**{lang.upper()}: {c['title']}**\n\n")
            for k, s in enumerate(c["steps"]):
                f.write(f"- [ ] {k + 1}. {s['text']}  <sub>[{', '.join(s['cites'])}]</sub>\n")
            f.write(f"- [ ] ☎ {c['call']['text']}  <sub>[{', '.join(c['call']['cites'])}]</sub>\n\n")
            for x in card.get("alt_steps", {}).get(lang, []):
                f.write(f"- [ ] **ALTERNATIVE (decision, not in the default card):** {x['text']}  <sub>[{', '.join(x['cites'])}]</sub>\n\n")
        used = sorted({cid for lang in LANGS for s in card["langs"][lang]["steps"] + [card["langs"][lang]["call"]] + card.get("alt_steps", {}).get(lang, []) for cid in s["cites"]})
        f.write("<details><summary>Sources quoted</summary>\n\n")
        for cid in used:
            s = SRC[cid]
            f.write(f"- **{cid}** {s['org']}: \"{s['quote']}\" ({s['url']}){' ' + s['flag'] if s.get('flag') and s['flag'] != 'ok' else ''}\n")
        f.write("\n</details>\n\n")
        f.write("Sign-off: [ ] EN  [ ] PT  [ ] ES  [ ] clinical review done  · notes: ____\n\n")
    f.write("## Before anything ships\n" + "\n".join(f"- {x}" for x in D["before_shipping"]) + "\n")
    rn = [n for n in notes if n.split("/")[0] in {c["id"] for c in RCARDS}]
    if rn:
        f.write("\n## Checker notes\n" + "\n".join(f"- {n}" for n in rn) + "\n")

print(f"cards {len(D['cards'])} × {len(LANGS)} langs; texts checked {len(rows)}; unsafe {sum(r[3] for r in rows)}; review {sum(r[4] for r in rows)}")
for n in notes: print("note:", n)
for x in fails: print("FAIL:", x)
sys.exit(1 if fails else 0)
