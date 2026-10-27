#!/usr/bin/env python3
"""Level-0 scorer for chat-slice: did the system decide to SEARCH or not? Deterministic, no judge.

Input (one of):
  --traces RUN.traces.jsonl   engine traces (itemId|id, route.reasonCodes; an optional boolean `searched` wins)
  --decisions FILE.jsonl      {"id": ..., "search": true|false}  (L0 mechanism prototypes, e.g. baseline_l0.mjs)
Search is read from reason codes: searched = any "retrieve:" code that isn't "retrieve:skipped-*";
not searched = "retrieve:skipped-*", "answer:small-talk-*" or "answer:emergency-numbers" with no search code.
Anything else = undetermined (counted as a wrong decision and listed).

Metrics (items with expected_search yes/no; "either" items are reported, never scored):
  accuracy       = right decisions / scored items
  false-search   = searched among expected "no"
  missed-search  = not searched among expected "yes"
Per language and per kind. --json writes the summary; exit 0 always.

Secondary metric (needs answers: traces, or decisions rows with an "answer" field):
  lang_match     = reply language == user language, over every item with an answer. Reply language = lang_of() on the
                   final answer text: deterministic en/pt/es function-word + orthography vote (no model, no library),
                   after removing citation markers, URLs and the engine's fixed source-warning lines. "und" (no evidence
                   evidence or a tie) counts as a mismatch and is listed apart. Expected = item "reply_lang" if present,
                   else REPLY_LANG overrides (slice v0 kept byte-identical), else the item's "lang".
Usage: score_l0.py --slice slice.v0.jsonl (--traces T | --decisions D) [--json out.json] [--quiet]
"""
import argparse, collections, json, re, sys

# Items whose expected reply language differs from the user's language (slice v0 file kept unchanged; sha 836be86f…).
REPLY_LANG = {"cs-037": "pt"}  # "can you say that again in Portuguese?"

# Function words that are distinctive for one language (shared ones like de/que/a/o/no/se/para/como/por are left out).
_W = {
    "en": "the an and is are was were of to in on for with it its it's this that these you your you're i i'm i've can how what "
          "which who be by from at or not have has does help today tonight welcome thanks would like know there they he she "
          "his her we my if about more also just will got all good sure so but any some here than been should could".split(),
    "pt": "não você vc é um uma umas uns os da dos das em na nas nos num numa com mas também isso essa esse eu ele ela seu sua "
          "ao à pela pelo nem já há foi são ou tem têm quer posso ajudar obrigado obrigada olá oi tudo bem sim muito fico "
          "onde quando pode deste desta nesta neste aqui então".split(),
    "es": "el la los las del al en con un una unos unas es y pero más también eso esa ese yo él ella su sus lo le les hay fue "
          "son tiene tienes puedo ayudarte ayudar gracias hola sí muy nada qué cómo cuál dónde cuándo hasta desde aquí "
          "entonces puede usted tú necesitas".split(),
}
_WS = {k: set(v) for k, v in _W.items()}
_ORTHO = {"pt": re.compile(r"ção|ções|ã|õ|ç"), "es": re.compile(r"ñ|¿|¡|ión\b|iones\b")}
_ENGINE_LINES = re.compile(r"^(?:This answer is not from an offline source on this phone; check it before relying on it\.|"
                           r"Esta resposta não vem de uma fonte offline deste celular; confira antes de confiar nela\.|"
                           r"From the offline source:)\s*$", re.M)

def lang_of(text):
    """'en' | 'pt' | 'es' | 'und' for the dominant language of a reply. Deterministic."""
    t = _ENGINE_LINES.sub(" ", text or "")
    t = re.sub(r"\[\d+\]|https?://\S+", " ", t).lower()
    score = {k: 0 for k in _W}
    for w in re.findall(r"[a-záéíóúâêôãõçñü']+", t):
        for k in _W:
            score[k] += w in _WS[k]
            if k in _ORTHO and _ORTHO[k].search(w): score[k] += 1
    score["es"] += len(re.findall(r"[¿¡]", t))
    (l1, s1), (_, s2) = sorted(score.items(), key=lambda kv: -kv[1])[:2]
    return l1 if s1 > s2 else "und"

def searched_from_trace(t):
    if isinstance(t.get("searched"), bool): return t["searched"]
    codes = (t.get("route") or {}).get("reasonCodes") or t.get("reasonCodes") or []
    if any(c.startswith("retrieve:") and not c.startswith("retrieve:skipped") for c in codes): return True
    if any(c.startswith(("retrieve:skipped", "answer:small-talk", "answer:emergency-numbers")) for c in codes): return False
    return None

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--slice", required=True)
    g = ap.add_mutually_exclusive_group(required=True); g.add_argument("--traces"); g.add_argument("--decisions")
    ap.add_argument("--json"); ap.add_argument("--quiet", action="store_true"); a = ap.parse_args()
    items = [json.loads(l) for l in open(a.slice) if l.strip()]
    dec, ans = {}, {}
    for l in open(a.traces or a.decisions):
        if not l.strip(): continue
        r = json.loads(l); i = r.get("itemId") or r.get("id")
        dec[i] = searched_from_trace(r) if a.traces else r.get("search")
        txt = ((r.get("answer") or {}).get("text") if isinstance(r.get("answer"), dict) else r.get("answer"))
        if isinstance(txt, str): ans[i] = txt
    rows = []
    for it in items:
        s = dec.get(it["id"]); exp = it["expected_search"]
        ok = None if exp == "either" else (s is not None and s == (exp == "yes"))
        want = it.get("reply_lang") or REPLY_LANG.get(it["id"]) or it["lang"]
        got = lang_of(ans[it["id"]]) if it["id"] in ans else None
        rows.append({"id": it["id"], "lang": it["lang"], "kind": it["kind"], "expected": exp, "searched": s, "ok": ok, "missing": it["id"] not in dec,
                     "reply_lang_expected": want, "reply_lang": got, "lang_ok": None if got is None else got == want})
    def stats(rs):
        sc = [r for r in rs if r["ok"] is not None]; no = [r for r in sc if r["expected"] == "no"]; yes = [r for r in sc if r["expected"] == "yes"]
        f = lambda n, d: (round(n / d, 3) if d else None)
        return {"n": len(rs), "scored": len(sc), "accuracy": f(sum(r["ok"] for r in sc), len(sc)),
                "false_search": f(sum(r["searched"] is not False for r in no), len(no)), "n_no": len(no),
                "missed_search": f(sum(r["searched"] is not True for r in yes), len(yes)), "n_yes": len(yes),
                "either_searched": sum(r["searched"] is True for r in rs if r["expected"] == "either"), "n_either": sum(r["expected"] == "either" for r in rs),
                "undetermined": sum(r["searched"] is None for r in rs),
                "lang_match": f(sum(r["lang_ok"] is True for r in rs), sum(r["lang_ok"] is not None for r in rs)),
                "n_lang": sum(r["lang_ok"] is not None for r in rs), "lang_und": sum(r["reply_lang"] == "und" for r in rs)}
    out = {"all": stats(rows), "by_lang": {k: stats([r for r in rows if r["lang"] == k]) for k in sorted({r["lang"] for r in rows})},
           "by_kind": {k: stats([r for r in rows if r["kind"] == k]) for k in sorted({r["kind"] for r in rows})},
           "errors": [{k: r[k] for k in ("id", "lang", "kind", "expected", "searched")} for r in rows if r["ok"] is False],
           "lang_mismatches": [{"id": r["id"], "want": r["reply_lang_expected"], "got": r["reply_lang"]} for r in rows if r["lang_ok"] is False]}
    if a.json: json.dump(out, open(a.json, "w"), indent=1)
    pct = lambda x: "—" if x is None else f"{100 * x:.0f}%"
    print(f"{'group':12s} {'n':>3} {'acc':>5} {'false-search':>13} {'missed-search':>14} {'either→search':>14} {'undet':>6} {'lang-match':>11}")
    for name, s in [("ALL", out["all"])] + [(f"lang:{k}", v) for k, v in out["by_lang"].items()] + [(f"kind:{k}", v) for k, v in out["by_kind"].items()]:
        print(f"{name:12s} {s['n']:3d} {pct(s['accuracy']):>5} {pct(s['false_search']):>6} of {s['n_no']:<4d} {pct(s['missed_search']):>6} of {s['n_yes']:<4d} {s['either_searched']:>7}/{s['n_either']:<5d} {s['undetermined']:>5d} {pct(s['lang_match']):>5} of {s['n_lang']:<3d}")
    if not a.quiet and out["errors"]:
        print("errors:", " ".join(f"{e['id']}({e['lang']},{e['kind']},exp {e['expected']}, got {'search' if e['searched'] else 'none' if e['searched'] is False else '?'})" for e in out["errors"]))
    if not a.quiet and out["lang_mismatches"]:
        print("lang mismatches:", " ".join(f"{e['id']}({e['want']}→{e['got']})" for e in out["lang_mismatches"]))

if __name__ == "__main__":
    main()
