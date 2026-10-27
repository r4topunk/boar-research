"""PACK-NIST: string check of the vx-002 rubric facts in the built pack (0 LLM). Prints, per needle, the number of
articles containing it and up to 3 titles. Usage: .venv python -I vexact_strings.py"""
import sys, os, re, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from selftest_common import Pack
p = Pack("boar-nist-crypto")
rows = p.rows()
texts = {aid: (title, p.text(aid)) for aid, src, title, *_ in rows}
NEEDLES = {
 "ML-DSA (FIPS 204)": r"ML-DSA", "CRYSTALS-Dilithium": r"CRYSTALS-Dilithium", "SLH-DSA (FIPS 205)": r"SLH-DSA",
 "SPHINCS+": r"SPHINCS\+", "Falcon / FN-DSA": r"FALCON|Falcon|FN-DSA", "XMSS (SP 800-208)": r"XMSS", "LMS (SP 800-208)": r"\bLMS\b",
 "hash-based": r"[Hh]ash-[Bb]ased", "lattice-based": r"[Ll]attice-[Bb]ased",
 "RSA/ECDSA quantum-vulnerable (IR 8547 Table 2)": r"Quantum-vulnerable digital signature algorithms",
 "Shor's algorithm": r"\bShor(?:'s|’s)?\b", "stateful / state management": r"[Ss]tateful",
 "ML-DSA believed secure vs quantum computer": r"ML-DSA is believed\s+to be secure",
}
out = {}
for k, rx in NEEDLES.items():
    hits = [t for t, x in texts.values() if re.search(rx, x)]
    out[k] = {"articles": len(hits), "examples": hits[:3]}
    print(f"{k:50s} {len(hits):4d}  {hits[:2]}")
json.dump(out, open(os.path.join(os.path.dirname(__file__), "../aggregates/vexact-vx002-strings.json"), "w"), indent=1)
