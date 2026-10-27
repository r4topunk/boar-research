"""PACKSHAPE kits: BASE = compose kits.py kit(10) (K13); SHAPED = K13 with v3proto/boar-factbook.sqlite -> the shaped file. usage: kits.py <BASE|SHAPED|FASHAPED> (FASHAPED: firstaid shaped, factbook original)"""
import sys, importlib.util
s = importlib.util.spec_from_file_location("k", "<workspace>/rnd/research/coordinator/arms/coverage-map/compose/tools/kits.py"); k = importlib.util.module_from_spec(s); s.loader.exec_module(k)
FB = "<workspace>/shared-data/packs/v3proto/boar-factbook.sqlite"; SH = "<workspace>/kiln-local/shape-packs/shaped/boar-factbook.sqlite"
FA = "<workspace>/shared-data/packs/v3proto/boar-firstaid-en.sqlite"; FASH = "<workspace>/kiln-local/shape-packs/fa-shaped/boar-firstaid-en.sqlite"
def kit(name):
    base = k.kit(10); assert len(base) == 13 and FB in base
    if name == "FASHAPED": assert FA in base; return [FASH if p == FA else p for p in base]
    return base if name == "BASE" else [SH if p == FB else p for p in base]
if __name__ == "__main__": print(",".join(kit(sys.argv[1])))
