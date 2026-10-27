"""D2Q kits (criterion 83b06185): K13 = compose kit(10); D2Q = K13 with boar-factbook swapped for kiln-local/d2q-packs/boar-factbook.sqlite. usage: kits.py <K13|D2Q> [extra.sqlite]"""
import sys, importlib.util
s = importlib.util.spec_from_file_location("k", "<workspace>/rnd/research/coordinator/arms/coverage-map/compose/tools/kits.py"); k = importlib.util.module_from_spec(s); s.loader.exec_module(k)
D2Q = "<workspace>/kiln-local/d2q-packs/boar-factbook.sqlite"
def kit(name):
    base = k.kit(10); assert len(base) == 13
    if name == "K13": return base
    out = [D2Q if p.endswith("/v3proto/boar-factbook.sqlite") else p for p in base]; assert D2Q in out; return out
if __name__ == "__main__":
    print(",".join(kit(sys.argv[1]) + sys.argv[2:]))
