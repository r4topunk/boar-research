#!/usr/bin/env python3 -I
"""usage: attribute.py <dropped.jsonl> <out.json>
For each dropped template (from dropped-templates.mjs) test whether the text around the seam matches a hole pattern
(same patterns as holes.py, STRONG set) with the match spanning the seam. Aggregates per template name."""
import sys, re, json
from collections import Counter, defaultdict
sys.path.insert(0, __import__("os").path.dirname(__import__("os").path.abspath(__file__)))
import importlib.util
spec = importlib.util.spec_from_file_location("holes", __import__("os").path.join(__import__("os").path.dirname(__import__("os").path.abspath(__file__)), "holes.py"))
h = importlib.util.module_from_spec(spec); spec.loader.exec_module(h)
PAT = {k: v for k, v in h.PATTERNS.items() if k in h.STRONG}
tot = Counter(); hit = Counter(); byp = defaultdict(Counter); ex = defaultdict(list)
for line in open(sys.argv[1]):
    d = json.loads(line); t = d["t"]; tot[t] += 1
    l = re.sub(r"[ \t]+", " ", d["l"]); r = re.sub(r"[ \t]+", " ", d["r"])
    if l.endswith(" ") and r.startswith(" "): r = r[1:]
    L = len(l); s = l + r
    for name, rx in PAT.items():
        m = next((m for m in rx.finditer(s) if m.start() < L < m.end()), None)
        if m:
            hit[t] += 1; byp[t][name] += 1
            if len(ex[t]) < 4: ex[t].append({"page": d["p"], "ctx": s[max(0, L - 60): L + 40] , "seam": L - max(0, L - 60), "pattern": name})
            break
FAM = [("lang/transl (foreign-language label)", r"^(lang|langx|lang-[a-z-]+|transl|translit|tlit|zh|script|nihongo|nastaliq|rtl-lang|korean|ko-hhrm|hangul|hanja|arabic|polytonic|cyrl|pinyin|hebrew|thai|vi-[a-z]+|ja-[a-z]+|nobold|lang-[a-z]+\\d?)$"),
       ("ipa/pronunciation", r"^(ipa|ipac|ipac-[a-z]+|ipa-[a-z]+|ipaс|respell|audio|listen|pron|pronunciation|ipa audio link|ipa-en)$"),
       ("convert/units", r"^(convert|cvt|km|km2|kmh|kmph|m|mi|mile|miles|ft|feet|foot|c|f|kg|lb|lbs|ha|acre|acres|sqmi|m2|mph|metre|meter|km/h|nowrap convert|val|sqkm|inch|in|cm|mm|l|gal|oz|tonne|ton|min|h|time)$"),
       ("currency", r"^(eur|rub|egp|php|usd|gbp|jpy|cny|inr|aud|cad|chf|nzd|thb|idr|krw|mxn|brl|zar|try|czk|huf|pln|sek|nok|dkk|rs|rm|us\\$|a\\$|nz\\$|£|€|¥)$"),
       ("iata/faa/airport code", r"^(iata|icao|faa lid|faa|airport code)$"),
       ("phone", r"^(phone|tel|fax|phonenumber|phone number)$"),
       ("coord/geo", r"^(coord|coord missing|coordinates|geo|location map\\+?|location map|marker)$"),
       ("ill/interlanguage link", r"^(ill|interlanguage link|link-interwiki|ill-wd)$"),
       ("date/birth/death", r"^(birth date( and age)?|death date( and age)?|birth-date|death-date|bda|dda|start date( and age)?|end date|birth year and age|bya|dob|dod|born|died|c\\.|circa|age)$"),
       ("wiki-markup/format (benign)", r"^(refn|r|sfn|efn|cite .*|reflist|main|see also|further|clear|-|!|\\*|nowrap|nbsp|nobr|sp|spaces|·|•|pagebanner|isPartOf|iscomplete|small|big|center|quote|blockquote|infobox.*)$")]
fam = defaultdict(lambda: [0, 0])
for t in tot:
    for n, rx in FAM:
        if re.match(rx, t, re.I): fam[n][0] += tot[t]; fam[n][1] += hit[t]; break
    else: fam["other"][0] += tot[t]; fam["other"][1] += hit[t]
famrows = sorted(([k, v[0], v[1]] for k, v in fam.items()), key=lambda x: -x[2])
rows = [{"template": t, "dropped": tot[t], "hole_at_seam": hit[t], "rate": hit[t] / tot[t], "patterns": dict(byp[t]), "examples": ex[t]} for t in tot]
rows.sort(key=lambda r: -r["hole_at_seam"])
json.dump({"families (name, dropped, hole_at_seam)": famrows, "total_dropped": sum(tot.values()), "total_hole_seams": sum(hit.values()), "templates": rows[:200]}, open(sys.argv[2], "w"), indent=1, ensure_ascii=False)
print("dropped", sum(tot.values()), "hole seams", sum(hit.values()))
print("FAMILIES", famrows)
for r in rows[:25]: print(f'{r["template"]:24} {r["hole_at_seam"]:7} / {r["dropped"]:7}  {r["patterns"]}')
