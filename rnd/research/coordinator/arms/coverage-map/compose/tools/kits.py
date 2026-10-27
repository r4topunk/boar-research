"""COMPOSE kits (criterion sha 2d071770). Base K3 = the 3-pack kit {crypto, wikivoyage, simplewiki}; N adds the criterion's packs in its order.
File choice = the files kit.K3/K3CM/KSE use in coverage-map/replay (v3proto for simplewiki, factbook, medlineplus, firstaid, qa-health/travel/outdoors)."""
S = "<workspace>/shared-data/"
BASE = [S + "crypto/boar-crypto.sqlite", S + "packs/boar-wikivoyage-en.sqlite", S + "packs/v3proto/boar-simplewiki-en.sqlite"]
STEPS = {2: [S + "packs/wave3/qa-cooking-se.sqlite", S + "packs/wave3/qa-money-se.sqlite"],
         4: [S + "packs/v3proto/boar-factbook.sqlite", S + "packs/v3proto/boar-medlineplus-en.sqlite"],
         6: [S + "packs/v3proto/boar-firstaid-en.sqlite", S + "packs/wave4/boar-visa-en.sqlite"],
         8: [S + "packs/v3proto/qa-health-se.sqlite", S + "packs/v3proto/qa-travel-se.sqlite"],
         10: [S + "packs/v3proto/qa-outdoors-se.sqlite", S + "packs/wiki-vital5.sqlite"]}
def kit(n):
    k = list(BASE)
    for s in sorted(STEPS):
        if s <= n: k += STEPS[s]
    return k
if __name__ == "__main__":
    import sys
    print(",".join(kit(int(sys.argv[1]))))
