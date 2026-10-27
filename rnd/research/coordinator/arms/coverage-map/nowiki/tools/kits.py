"""NOWIKI kits (criterion 5d40edcd): K13 = compose kit(10); NOWIKI drops simplewiki + vital5; NOWIKI2 also drops wikivoyage. usage: kits.py <K13|NOWIKI|NOWIKI2> [extra.sqlite]"""
import sys, importlib.util
s = importlib.util.spec_from_file_location("k", "<workspace>/rnd/research/coordinator/arms/coverage-map/compose/tools/kits.py"); k = importlib.util.module_from_spec(s); s.loader.exec_module(k)
DROP = {"K13": [], "NOWIKI": ["boar-simplewiki-en.sqlite", "wiki-vital5.sqlite"], "NOWIKI2": ["boar-simplewiki-en.sqlite", "wiki-vital5.sqlite", "boar-wikivoyage-en.sqlite"]}
def kit(name):
    base = k.kit(10); assert len(base) == 13
    out = [p for p in base if p.rsplit("/", 1)[1] not in DROP[name]]; assert len(out) == 13 - len(DROP[name]); return out
if __name__ == "__main__":
    print(",".join(kit(sys.argv[1]) + sys.argv[2:]))
