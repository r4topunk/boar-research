"""facts r11 = builder output (build_asset.py r11: currency + Nobel fixes, 2026-10-23) + the FACTS-R10 audited hand fixes, which still stand
(emergency numbers, India, Pakistan, three currency renames). Usage: python3 -I build_r11.py <build_asset.py output> <out facts.v1.json>
Each fix asserts the builder's value first, so a fix never lands on an unexpected row. Differences from build_r10.py: the Nobel 1988 (Mahfouz alone)
and 2026 (Anne Carson) rows now come from the builder (nobel_r11.json), so they are asserted instead of written."""
import json, sys

src, out = sys.argv[1], sys.argv[2]
raw = open(src, encoding="utf-8").read()
d = json.loads(raw)
E = {e["q"]: e for e in d["entities"]}

def fix(q, field, old, new):
    e = E[q]
    assert e.get(field) == old, (q, field, e.get(field))
    if new is None:
        e.pop(field)
    else:
        e[field] = new

# 1. Nobel Prize in Literature: 1988 Mahfouz alone, 2026 Anne Carson (announced 2026-10-08, after the 10-06 snapshot); both from the r11 builder
win = E["Q37922"]["win"]
assert win["2026"] == ["Anne Carson"] and win["1988"] == ["Naguib Mahfouz"] and win["1999"] == ["Günter Grass"]  # builder (r11), not by hand

# 2. Pakistan: Rawalpindi was the interim capital 1959-1967 (Wikidata now carries the end date)
fix("Q843", "cap", ["Islamabad", "Rawalpindi"], ["Islamabad"])

# 3. India: 2020 estimate (1.326 bn) put India below China; official projection for 2026 (MoHFW)
fix("Q668", "pop", [1326093247, 2020], [1429404000, 2026])

# 4-8. Emergency numbers
fix("Q842", "emerg", [["112", "emergency medical services, fire department, police"], ["968", ""]],
    [["112", "emergency medical services, fire department, police"], ["9999", ""]])  # Oman: 968 is the calling code
fix("Q712", "emerg", [["000", ""], ["911", ""], ["919", "police"]],
    [["910", "fire department"], ["911", ""], ["917", "police"]])  # Fiji (TAF): 000 not a Fiji number, 919 = Crime Stoppers
fix("Q224", "emerg", [["93", "fire department"], ["94", "emergency medical services"], ["112", ""], ["192", "police"]],
    [["112", ""], ["192", "police"], ["193", "fire department"], ["194", "emergency medical services"]])  # Croatia (HAKOM)
fix("Q1013", "emerg", [["112", "police"], ["114", "emergency medical services"], ["115", "fire department"]],
    [["121", "emergency medical services"], ["122", "fire department"], ["123", "police"], ["124", "police"]])  # Lesotho
fix("Q686", "emerg", [["11", "police"], ["112", ""], ["113", "fire department"]],
    [["111", "police"], ["112", "emergency medical services"], ["113", "fire department"]])  # Vanuatu (TRBR)

# 9-11. Currency names that are no longer current
fix("Q419", "cur", ["Nuevo sol"], ["Peruvian sol"])  # renamed by Law 30381 (2015)
fix("Q717", "cur", ["sovereign bolivar"], ["Venezuelan bolívar"])  # bolívar soberano became the bolívar digital (2021-10-01)
fix("Q414", "cur", ["Argentine convertible peso"], ["Argentine peso"])  # "convertible" was the 1992-2001 regime

d["build"] = "r11"
d["source"] = d["source"] + "; r10 audit fixes 2026-10-21 (see CHANGES-r10.md); r11 builder fixes 2026-10-23 (currency, Nobel 1988; see ENGFIX-FACTS-2026-10-23.md)"
json.dump(d, open(out, "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
