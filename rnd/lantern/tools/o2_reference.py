#!/usr/bin/env python3
"""O2 'refuse on weak support': NON-NORMATIVE reference implementation of rnd/lantern/o2-weak-support-spec.md.
No LLM: regexes + title normalization + one scan of the used passages' text. EN + PT.

decide(question, passages) -> {"in_scope", "kind", "subjects", "used", "action": "keep"|"refuse", "reason"}
  passages: list of {"title": str, "text": str|None}  (the passages the answer cites; if it cites none, all
            passages that were in the prompt, see spec §3.3)
"""
import re, unicodedata

# ---- §3.1 scope: numeric / superlative / comparative / list questions -----------------------------------------
SUPERL_EN = r"(most|least|largest|biggest|smallest|tallest|highest|lowest|heaviest|lightest|longest|shortest|oldest|" \
            r"youngest|deepest|fastest|richest|poorest|densest|hottest|coldest|busiest)"
SUPERL_PT = r"(?:o|a|os|as) (?:\w+ )?(?:mais|menos) \w+ d[oa]s? \w+|(?:o|a|os|as) (?:mais|menos) \w+|(?:o|a|os|as) (?:maior|menor)(?:es)?"
SUPERL = SUPERL_EN  # used for passage scans (passages are EN in all current packs)
COMPAR_EN = r"(larger|bigger|smaller|taller|shorter|heavier|lighter|older|younger|longer|more populous|more densely|" \
            r"more|fewer|less|exceed\w*|outnumber\w*)"
COMPAR_PT = r"mais \w+(?: \w+)? (?:que|do que)|maior(?:es)? (?:que|do que)|menor(?:es)? (?:que|do que)|ultrapass\w*|" \
            r"mais (?:pesad|alt|populos|grand|long|antig)\w*"
NUMERIC = r"(how (many|much|far|long|tall|high|big|old|heavy|often|deep|wide)|population|populated|height|" \
          r"weigh\w*|distance|area of|density|number of|what year|which year|when did|when was|how fast|" \
          r"quant[oa]s?|população|altura|distância|peso|em que ano|quando)"
RX_SUPERL = re.compile(r"\b(" + SUPERL_EN + r"|" + SUPERL_PT + r")\b", re.I)
RX_COMPAR = re.compile(r"\b(" + COMPAR_EN + r"|" + COMPAR_PT + r")\b", re.I)
RX_NUMERIC = re.compile(r"\b" + NUMERIC + r"\b", re.I)
NOT_PLURAL = {"is", "was", "has", "does", "this", "its", "pais", "mais"}
RX_LISTQ = re.compile(r"^\s*(?:which|what|quais|que)\s+(\w{3,}(?:s|es))\b", re.I)   # "which countries…", "quais países…"
RX_WHY = re.compile(r"^\s*(why|how did|how does|how do|explain|por que|porque|como)\b", re.I)

def list_noun(q):
    m = RX_LISTQ.match(q)
    return m.group(1) if m and m.group(1).lower() not in NOT_PLURAL else None

def classify(q):
    """-> 'list' | 'superlative' | 'comparative' | 'numeric' | None (out of scope)."""
    if RX_WHY.match(q):
        return None                     # causal/explanatory ("why did Terra collapse in 2022?")
    two_sided = bool(re.search(r"\b(or|than|ou|que|vs\.?|versus)\b", q, re.I))
    sup, comp = RX_SUPERL.search(q), RX_COMPAR.search(q)
    if list_noun(q) and (sup or comp):
        return "list"
    if sup and not (comp and two_sided and not re.search(r"\b" + SUPERL_EN + r"\b", q, re.I)):
        return "superlative"
    if comp and two_sided:
        return "comparative"
    if RX_NUMERIC.search(q):
        return "numeric"
    return None

# ---- §3.2 subjects -----------------------------------------------------------------------------------------
QWORDS = {"what", "which", "who", "how", "is", "are", "was", "were", "did", "does", "do", "could", "can", "tell", "when",
          "where", "why", "i", "if", "my", "with", "and", "qual", "quais", "quem", "como", "quando", "onde", "quanto",
          "quantos", "quantas", "o", "a", "os", "as", "the", "in"}
JOIN = {"of", "the", "de", "da", "do", "dos", "das"}
ATTR = {"population", "populations", "larger", "bigger", "heavier", "taller", "smaller", "more", "densely", "populated",
        "weigh", "weighs", "be", "is", "are", "an", "a", "the", "which", "heavier", "populacao", "mais", "pesados",
        "pesadas", "altos", "altas", "sao", "e"}

def norm(s):
    s = unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode().lower()
    s = re.sub(r"'s\b|’s\b", "", s)
    return re.sub(r"[^a-z0-9]+", " ", s).strip()

def stem(w):
    for suf in ("ies", "es", "s"):
        if w.endswith(suf) and len(w) > len(suf) + 2:
            return w[: -len(suf)] + ("y" if suf == "ies" else "")
    return w

def named_entities(q):
    """Quoted spans + capitalized spans (not sentence-initial) + codes like EIP-7251 / ERC-20."""
    ents = [m.group(1) for m in re.finditer(r"(?<!\w)['\"‘“]([^'\"’”]{3,40})['\"’”]", q)]
    toks = re.findall(r"[\w\-’']+|[^\w\s]", q)
    cur, sent_start = [], True
    for i, t in enumerate(toks):
        code = re.fullmatch(r"[A-Z]{2,}-?\d+[A-Za-z]*", t)
        cap = (t[:1].isupper() and not sent_start) or code or (t[:1].isupper() and sent_start and norm(t) not in QWORDS
                                                                 and i + 1 < len(toks) and toks[i + 1][:1].isupper())
        if cap and norm(t) not in QWORDS:
            cur.append(t)
        elif cur and t.lower() in JOIN and i + 1 < len(toks) and toks[i + 1][:1].isupper():
            cur.append(t)
        else:
            if cur: ents.append(" ".join(cur)); cur = []
        sent_start = t in {".", "?", "!"} or (i == 0 and False)
        if i == 0: sent_start = False
    if cur: ents.append(" ".join(cur))
    return [e for e in dict.fromkeys(ents) if norm(e) and norm(e) not in QWORDS]

def comparison_sides(q):
    ents = named_entities(q)
    if len(ents) >= 2:
        return ents[:2]
    ql = re.sub(r"[?!.,]", " ", q.lower())
    parts = re.split(r"\b(?:or|than|ou|que|do que|vs|versus)\b", ql, maxsplit=1)
    if len(parts) != 2:
        return ents
    left = [w for w in norm(parts[0]).split() if w not in ATTR and w not in QWORDS and w != "which"][-2:]
    right = [w for w in norm(parts[1]).split() if w not in ATTR and w not in QWORDS][:3]
    right = [w for w in right if not re.fullmatch(r"\w+er|\w+est", w) or w in ("deer",)][:2]
    return [" ".join(x) for x in (left, right) if x]

def superlative_class(q):
    m = re.search(r"\b" + SUPERL_EN + r"\s+(?:\w+ed\s+|\w+ous\s+|living\s+|land\s+|known\s+)?(\w+)", q, re.I)
    if m and norm(m.group(2)) not in ATTR | {"in", "of", "world", "r0"}:
        return m.group(2)
    m = re.search(r"\b(\w+) (?:mais|menos) \w+", q, re.I)                     # PT: "o animal mais alto"
    if m and norm(m.group(1)) not in QWORDS | ATTR:
        return m.group(1)
    return list_noun(q)

def subjects(q, kind):
    if kind == "comparative":
        return {"mode": "all", "terms": comparison_sides(q)}
    if kind == "list":
        return {"mode": "class", "terms": [list_noun(q)]}
    ents = [e for e in named_entities(q) if not re.fullmatch(r"R0|R₀", e)]
    if kind == "superlative" and not ents:
        c = superlative_class(q)
        return {"mode": "class", "terms": [c] if c else []}
    if not ents and re.search(r"\bworld\b|\bmundo\b", q, re.I):
        ents = ["world"]
    if kind == "numeric" and len(ents) >= 2 and re.search(r"\bfrom\b.+\bto\b|\bbetween\b|\bde\b.+\ba\b|\bentre\b", q, re.I) \
            and not named_entities(q)[0].startswith(("EIP", "ERC")):
        return {"mode": "all", "terms": ents[:2]}
    return {"mode": "any", "terms": ents}

# ---- §3.3/3.4 matching -------------------------------------------------------------------------------------
PREFIX = re.compile(r"^(Wikivoyage|Ethereum EIPs/ERCs|ethereum\.org|Ethereum specs|Bitcoin BIPs)[^:]*:\s*")

def title_covers(term, title):
    """Aboutness: the passage's article title contains the subject (token-subsequence match after normalization
    and plural stemming). Part-of relations are NOT coverage: 'Kantō region' does not cover 'Japan'."""
    t = [stem(w) for w in norm(PREFIX.sub("", title)).split()]
    s = [stem(w) for w in norm(term).split() if w not in ("the", "a", "an")]
    if not s or not t:
        return False
    return any(t[i:i + len(s)] == s for i in range(len(t) - len(s) + 1)) or \
           any(s[i:i + len(t)] == t for i in range(len(s) - len(t) + 1))

NARROW = re.compile(r"\b(in|of) (the )?(north|south|east|west|central)?\s*([A-Z][\w-]+|arab world|the americas|region|genus|family|deer family)\b")

def passage_asserts_superlative(text, cls, dims=None):
    """The passage states '<dim> <class>' ('the tallest living animal', 'most populous country') unqualified:
    not 'one of the …', no narrower scope ('… in North America', '… of deer', '… in the Arab world')."""
    if not text or not cls or not dims:
        return False
    c = stem(norm(cls))
    rx = re.compile(r"\b(?:" + "|".join(re.escape(d) for d in dims) + r")\b(?:\W+\w+){0,2}?\W+" + re.escape(c) + r"\w*", re.I)
    for sent in re.split(r"(?<=[.!?])\s+", text):
        for m in rx.finditer(sent):
            before = sent[max(0, m.start() - 20): m.start()].lower()
            if "one of" in before or re.search(r"(second|third|fourth|fifth|sixth|seventh|eighth|ninth|tenth|eleventh|twelfth|\d+(st|nd|rd|th))[- ]*$", before):
                continue                                   # "one of the most…", "the eleventh most populous country"
            if NARROW.search(sent[m.end(): m.end() + 60]) or re.search(r"\bof\s+(?:the\s+)?\w+\s*$", sent[m.start(): m.end()]):
                continue
            return True
    return False

def class_level_title(cls, title):
    t = norm(PREFIX.sub("", title)); c = stem(norm(cls))
    return stem(t) == c or re.search(r"^list of\b.*\b" + re.escape(c), t) is not None or \
        re.search(r"\b" + re.escape(c) + r"\w* by (population|height|area|size|weight)\b", t) is not None or \
        t in ("world population", "largest organisms", "list of largest animals")

SUP_DIMS = [(r"populous|populated|population|popula", ["most populous", "most populated", "largest population"]),
            (r"tall|height|alt[oa]", ["tallest"]), (r"heav|weigh|pesad", ["heaviest", "largest"]),
            (r"big|large|size|grand|maior", ["largest", "biggest"]), (r"dens", ["most densely", "densest", "highest population density"]),
            (r"long|comprid", ["longest"]), (r"high|elev", ["highest", "tallest"]), (r"old|antig", ["oldest"])]

def dims_for(q):
    for pat, d in SUP_DIMS:
        if re.search(pat, q, re.I):
            return d
    return None

def dominates(text, side, dims):
    """'<side> is/are the [world's] <dim> …' in a passage about that side, not 'one of the …', no narrower scope."""
    if not text or not dims or not norm(side):
        return False
    sd = stem(norm(side).split()[-1])
    rx = re.compile(r"\b" + re.escape(sd) + r"\w*\b[^.]{0,40}?\b(?:is|are|was|were)\s+(?:the\s+)?(?:world's\s+)?(?:" +
                    "|".join(re.escape(d) for d in dims) + r")\b", re.I)
    for sent in re.split(r"(?<=[.!?])\s+", text):
        m = rx.search(sent)
        if m and "one of" not in sent[max(0, m.start() - 5): m.end()].lower() and not NARROW.search(sent[m.end(): m.end() + 120]):
            return True
    return False

DIM = {"heavier": ["heaviest", "largest"], "bigger": ["largest", "biggest"], "larger": ["largest", "biggest"],
       "taller": ["tallest"], "more populous": ["most populous"], "more densely": ["most densely"]}

def decide(question, passages):
    kind = classify(question)
    if kind is None:
        return {"in_scope": False, "action": "keep", "reason": "out of scope"}
    subj = subjects(question, kind)
    titles = [p["title"] for p in passages]
    res = {"in_scope": True, "kind": kind, "subjects": subj, "used": titles}
    if not passages:
        return {**res, "in_scope": False, "action": "keep", "reason": "no passages in the prompt: the app's existing no-source gate decides"}
    terms = subj["terms"]
    if subj["mode"] == "any":
        if not terms:
            return {**res, "action": "keep", "reason": "no subject extracted (fail-open)"}
        ok = any(title_covers(t, ti) for t in terms for ti in titles)
        return {**res, "action": "keep" if ok else "refuse", "reason": "subject covered" if ok else f"no used passage is about {terms}"}
    if subj["mode"] == "all":
        missing = [t for t in terms if not any(title_covers(t, ti) for ti in titles)]
        if not missing:
            return {**res, "action": "keep", "reason": "all sides covered"}
        dims = dims_for(question)
        covered = [t for t in terms if t not in missing]
        for p in passages:
            for c in covered:
                if title_covers(c, p["title"]) and dominates(p.get("text"), c, dims):
                    return {**res, "action": "keep", "reason": f"side(s) {missing} uncovered, but '{p['title']}' states '{c}' is the {dims[0] if dims else 'superlative'} (unqualified)"}
        return {**res, "action": "refuse", "reason": f"side(s) {missing} not covered by any used passage"}
    # class mode (superlative over a class, or list question)
    cls = terms[0] if terms else None
    if cls and any(class_level_title(cls, ti) for ti in titles):
        return {**res, "action": "keep", "reason": "class/list-level passage"}
    if any(passage_asserts_superlative(p.get("text"), cls, dims_for(question)) for p in passages):
        return {**res, "action": "keep", "reason": "a used passage states the superlative over the class, unqualified"}
    return {**res, "action": "refuse", "reason": f"no used passage is class-level for '{cls}' or states the superlative unqualified"}
