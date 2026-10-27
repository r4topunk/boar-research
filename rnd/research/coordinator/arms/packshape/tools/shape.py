#!/usr/bin/env python3
"""PACKSHAPE shaper (0 LLM; criterion ../PACKSHAPE-criterion.md). Reads the boar-factbook v3proto pack read-only (same source
text, licence, url, attribution, aliases, page_id) and writes builder input for boar-factbook-shaped:
  <out>/factbook.jsonl (one doc per entry), <out>/manifest.json, <out>/provenance.json (per article: section heading -> source unit ids),
  <out>/stats.json. Optional --control writes the UNSHAPED text (pipeline identity check) instead.
Rules (frozen in the criterion):
  R1 lead = one-line summary sentence from Key facts fields only (no heading, first chunk = article lead).
  R2 Key facts lines -> 4 field groups (basics / people / government and economy / climate and code).
  R3 every other Factbook field (one paragraph of 'Label (sub): value' lines) -> one group; a field under 12 words merges
     with the next field of the same category (at most 3 fields, at most 60 words).
  R4 a line -> one sentence "<Country>'s <label> is|are <value>."; yearly series of one field -> one sentence; notes ->
     "Note on <Country>'s <label>: ..."; long values split only at '; ' into "<Country> (<label>): <part>." sentences.
  R5 Background prose: sentences (split after [a-z0-9)%] or two capitals + .!?); a sentence without the country name gets "<Country>: " in front.
  R6 group heading "## <Country>: <group>"; sentences packed in order, <= 120 words and <= 950 chars per chunk, else "(2)", "(3)".
Usage: python3 -I shape.py <outdir> [--control]"""
import json, re, sys, os, hashlib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import fbread
MAXW, MAXC = 120, 950
KF_GROUPS = [("capital, population and area", ["Official name", "Capital", "Time zone", "Location", "Area", "Population"]),
             ("languages, religions and people", ["Languages", "Religions", "Ethnic groups", "Life expectancy at birth"]),
             ("government, currency and economy", ["Government type", "Independence", "Currency", "GDP (official exchange rate)", "Real GDP per capita"]),
             ("climate and internet code", ["Climate", "Internet country code"])]
KF_LABEL = {"Independence": "independence date"}
def split_label(line):
    """'Label (sub: x): value' -> (label incl. parens, value); the first ': ' outside parentheses."""
    d = 0
    for i, ch in enumerate(line):
        if ch == "(": d += 1
        elif ch == ")": d = max(0, d - 1)
        elif ch == ":" and d == 0 and line[i + 1:i + 2] == " ": return line[:i].strip(), line[i + 2:].strip()
    return None, line.strip()
def lower1(s):
    w = s.split(" ", 1)[0]
    return s if (len(w) > 1 and w[:2].isupper()) else s[:1].lower() + s[1:]
def verb(phrase):
    head = phrase.split(" (", 1)[0].split(" - ")[-1].strip().split(" ")[-1].lower()
    return "are" if head.endswith("s") and not head.endswith(("ss", "us", "is")) else "is"
def end(s): s = s.rstrip(); return s if s.endswith((".", "!", "?")) else s + "."
def poss(c): return c + ("'" if c.endswith("s") else "'s")
def nwords(s): return len(s.split())
def line_sentences(C, field, label, val):
    """One source line -> sentences (R4). field = paragraph's top label; label = full label of the line."""
    sub = label[len(field):].strip() if label.startswith(field) else ""
    sub = sub[1:-1].strip() if sub.startswith("(") and sub.endswith(")") else sub
    last = sub.split(":")[-1].strip() if sub else ""
    if last and val.lower().startswith(last.lower() + ": "): val = val[len(last) + 2:]
    if sub.lower() == "note" or val.lower().startswith(("note: ", "note - ")):
        v = re.sub(r"^note\s*[:-]\s*", "", val, flags=re.I)
        return [end(f"Note on {poss(C)} {lower1(field)}: {v}")]
    phrase = lower1(label)
    parts = [p for p in val.split("; ")] if nwords(val) > 40 and "; " in val else [val]
    out = [end(f"{poss(C)} {phrase} {verb(phrase)} {parts[0]}")]
    out += [end(f"{C} ({phrase}): {p}") for p in parts[1:]]
    return out
YEAR = re.compile(r"^(.*?)\s*((?:19|20)\d\d)$")
def field_sentences(C, para):
    """A category paragraph (one Factbook field) -> (field name, sentences)."""
    lines = [l for l in para.split("\n") if l.strip()]
    parsed = [split_label(l) for l in lines]
    field = parsed[0][0] or ""
    field = re.sub(r"\s*\(.*$", "", field) if field else field
    sents, series = [], []
    def flush():
        if not series: return
        vals = [v if re.search(r"(19|20)\d\d", v) else f"{v} in {y}" for y, v in series]
        ph = lower1(field)
        sents.append(end(f"{poss(C)} {ph} {'were' if verb(ph) == 'are' else 'was'} " + (vals[0] if len(vals) == 1 else ", ".join(vals[:-1]) + " and " + vals[-1])))
        series.clear()
    for (lab, val), raw in zip(parsed, lines):
        if lab is None:
            flush(); sents.append(end(f"{C} ({lower1(field)}): {val}")); continue
        sub = lab[len(field):].strip() if lab.startswith(field) else ""
        m = YEAR.match(sub[1:-1].strip()) if sub.startswith("(") and sub.endswith(")") else None
        if m and (m.group(1).strip() == "" or m.group(1).strip().lower() in field.lower() or field.lower() in m.group(1).strip().lower()):
            series.append((m.group(2), val)); continue
        flush(); sents += line_sentences(C, field, lab, val)
    flush()
    return field, sents
def prose_sentences(C, names, para):
    ss = re.split(r"(?:(?<=[a-z0-9\)%][.!?])|(?<=[A-Z]{2}[.!?]))\s+(?=[A-Z\"'(])", para.strip())
    return [s if any(n.lower() in s.lower() for n in names) else f"{C}: {s}" for s in ss if s.strip()]
def cut(C, s):
    """R6b: one sentence over MAXW words / MAXC chars -> pieces at '; ' or ', ' (else a space) <= 100 words / 800 chars;
    pieces after the first start with '<Country> (continued): '."""
    if nwords(s) <= MAXW and len(s) <= MAXC: return [s]
    out, rest = [], s
    while nwords(rest) > 100 or len(rest) > 800:
        w = rest.split(" "); lim = min(100, len(w)); head = " ".join(w[:lim])
        while len(head) > 800: lim -= 5; head = " ".join(w[:lim])
        k = max(head.rfind("; "), head.rfind(", "))
        k = k + 1 if k > len(head) // 3 else len(head)
        out.append(head[:k].rstrip(" ;,")); rest = f"{C} (continued): " + rest[k:].lstrip(" ;,")
    out.append(rest); return [end(x) for x in out]
def pack(heading, sents, units, C=""):
    """R6: sentences -> sections <= MAXW words / MAXC chars; returns [(heading, text, units)]."""
    out, cur, n = [], [], 0
    sents = [p for s in sents for p in cut(C, s)]
    for s in sents:
        if cur and (nwords(" ".join(cur + [s])) > MAXW or len(" ".join(cur + [s])) > MAXC): out.append(cur); cur = []
        cur.append(s)
    if cur: out.append(cur)
    return [(heading if i == 0 else f"{heading} ({i + 1})", " ".join(c), units) for i, c in enumerate(out)]
def shape(a):
    C = a["title"]; names = [C] + [x for x in a["aliases"] if len(x) > 3]
    body = re.sub(r"^# [^\n]*\n+", "", a["text"])
    parts = re.split(r"\n\n(?=## )", body)
    kf, secs = {}, []
    if parts and parts[0].startswith("Key facts:"):
        for i, l in enumerate(parts[0].split("\n")[1:]):
            lab, val = split_label(l)
            if lab: kf[lab] = (val, f"kf:{i}")
        parts = parts[1:]
    # R1 lead
    g = lambda k: kf.get(k, (None,))[0]
    lead = f"{C}"
    bits = []
    if g("Government type"): bits.append(f"is a {g('Government type')}")
    if g("Location"): bits.append(f"{'' if bits else 'is '}in {g('Location')}")
    s = f"{C} " + " ".join(bits) if bits else f"{C} is a Factbook entry"
    tail = [x for x in [f"capital {g('Capital')}" if g("Capital") else None, f"population {g('Population')}" if g("Population") else None, f"area {g('Area')}" if g("Area") else None] if x]
    lead = end(s + (", with " + ", ".join(tail) if tail else ""))
    lead_units = [kf[k][1] for k in ("Government type", "Location", "Capital", "Population", "Area") if k in kf]
    sections = []
    for gname, keys in KF_GROUPS:
        ks = [k for k in keys if k in kf]
        if not ks: continue
        ss = [end(f"{poss(C)} {KF_LABEL.get(k, lower1(k))} {verb(KF_LABEL.get(k, k))} {kf[k][0]}") for k in ks]
        sections += pack(f"{C}: {gname}", ss, [kf[k][1] for k in ks], C)
    for p in parts:
        m = re.match(r"## ([^\n]*)\n+", p); cat = m.group(1).strip(); rest = p[m.end():]
        paras = [x for x in rest.split("\n\n") if x.strip()]
        if cat == "Background":
            ss, us = [], []
            for j, x in enumerate(paras): ss += prose_sentences(C, names, x); us.append(f"{cat}:{j}")
            sections += pack(f"{C}: background", ss, us, C); continue
        fl = [(field_sentences(C, x), f"{cat}:{j}") for j, x in enumerate(paras)]
        k = 0
        while k < len(fl):
            grp = [fl[k]]; k += 1
            while k < len(fl) and len(grp) < 3 and nwords(" ".join(s for (f, ss), u in grp for s in ss)) < 12 and nwords(" ".join(s for (f, ss), u in grp + [fl[k]] for s in ss)) <= 60:
                grp.append(fl[k]); k += 1
            names_ = [f for (f, ss), u in grp]
            title = names_[0] if len(names_) == 1 else (" and ".join(names_) if len(names_) == 2 else f"{names_[0]}, {names_[1]} and {names_[2]}")
            sections += pack(f"{C}: {title}", [s for (f, ss), u in grp for s in ss], [u for _, u in grp], C)
    text = f"# {C}\n\n{lead}\n\n" + "\n\n".join(f"## {h}\n\n{t}" for h, t, u in sections)
    prov = {"": lead_units}; prov.update({h: u for h, t, u in sections})
    return text, prov, lead, sections
def main():
    out = sys.argv[1]; control = "--control" in sys.argv; os.makedirs(out, exist_ok=True)
    A = fbread.articles(); docs, prov, man, st = [], {}, [], dict(articles=0, sections=0, words=[], chars=0, over_words=0)
    for a in A:
        if control: text = a["text"]
        else:
            text, pv, lead, secs = shape(a); prov[a["title"]] = pv
            st["sections"] += len(secs); st["words"] += [nwords(t) for h, t, u in secs]; st["over_words"] += sum(nwords(t) > MAXW for h, t, u in secs)
        st["articles"] += 1; st["chars"] += len(text)
        d = dict(page_id=a["page_id"], title=a["title"], text=text, source="factbook", url=a["url"], license=a["license"], attribution=a["attribution"], aliases=a["aliases"], views=a["views"], infoboxes=None)
        docs.append(d); man.append(dict(page_id=a["page_id"], title=a["title"], source="factbook", url=a["url"], license=a["license"]))
    with open(f"{out}/factbook.jsonl", "w") as f:
        for d in docs: f.write(json.dumps(d, ensure_ascii=False) + "\n")
    json.dump(man, open(f"{out}/manifest.json", "w"), ensure_ascii=False)
    if not control: json.dump(prov, open(f"{out}/provenance.json", "w"), ensure_ascii=False)
    w = st.pop("words"); st.update(words_median=sorted(w)[len(w) // 2] if w else None, words_max=max(w) if w else None,
                                   jsonl_sha256=hashlib.sha256(open(f"{out}/factbook.jsonl", "rb").read()).hexdigest())
    json.dump(st, open(f"{out}/stats.json", "w"), indent=1); print(json.dumps(st))
if __name__ == "__main__": main()
