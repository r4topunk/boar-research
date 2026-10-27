"""Grading v2 overrides (sprint 2, 2026-09-30): tighter must/forbid after the first real iPhone run.
Questions are unchanged; only `grading` changes. Applied by build_evalset.py after all items are built."""
JAPAN = {"k": 2, "terms": ["tokyo", "honshu", "hokkaido", "kyushu", "shikoku", "yen", r"re:\b12[2-6](\.\d+)?\s*million",
         "emperor", "prime minister", "constitutional monarchy", "national diet", "archipelago"]}
AMAZON = {"k": 2, "terms": ["south america", "brazil", r"re:\b(nine|9) (countries|nations)", "biodiversity", "amazon river",
          r"re:\b(5\.5|6|7) million (km|square)", "largest", "deforestation", "tropical"]}
NOT_2018_WINNER = r"re:\b(?!france\b)[a-z]+ won the (2018 )?(fifa )?world cup"
G = {
 "vit-fa-001": {"must_k": JAPAN, "forbid": [["is a country in europe", "density of 330 km²", "density of 330 km2", "rapid population growth"]], "refuse_ok": False},
 "vit-fa-028": {"must_k": JAPAN, "forbid": [["is a country in europe", "density of 330 km²", "rapid population growth"]], "refuse_ok": False},
 "vit-fa-002": {"must_k": {"k": 2, "terms": ["buenos aires", "spanish", "patagonia", "peron", "peronism", "justicialist", "aconcagua",
                "peso", "andes", "south america", r"re:(second|eighth)[- ]largest"]}, "refuse_ok": False},
 "vit-fa-017": {"must_k": {"k": 2, "terms": ["ottawa", "confederation", "1867", "english", "french", "king charles", "king george",
                "monarchy", "provinces", "quebec", "north america", r"re:second[- ]largest"]}, "refuse_ok": False},
 "vit-fa-019": {"must_k": AMAZON, "refuse_ok": False},
 "vit-fa-030": {"must_k": AMAZON, "refuse_ok": False},
 "vit-fa-003": {"must_any": [[r"re:\b12[2-7](\.\d+)?\s*million"]], "forbid": [["1.4 billion", r"re:\b(330|200) million"]], "refuse_ok": False},
 "vit-fa-004": {"must_any": [[r"re:^\s*no\b", r"re:nigeria('s population)? (is|has) (larger|bigger|greater|more)", "nigeria is more populous",
                r"re:japan('s population)? (is|has) (smaller|fewer|less)"]],
                "forbid": [[r"re:japan('s population)? (is|has) (larger|bigger|greater|more)", "japan has more people", r"re:^\s*yes\b"]], "refuse_ok": False},
 "vit-fa-005": {"must_any": [[r"re:^\s*no\b", r"re:elephants? (is|are) (bigger|larger|heavier)"]],
                "forbid": [["yes, rhinos are bigger", r"re:rhinos? (is|are) (bigger|larger) than elephants", r"re:^\s*yes\b"]], "refuse_ok": False},
 "vit-fa-006": {"must_any": [[r"re:^\s*yes\b", "heaviest animal", r"re:blue whales? (can |could |would |may )?(weigh|be) (more|heavier)",
                r"re:\b(1[5-9]\d|200)\s*(t|tonnes|tons|metric tons)\b"]],
                "forbid": [["dinosaurs were heavier than any whale", r"re:^\s*no\b"]], "refuse_ok": False},
 "vit-fa-007": {"must_any": [["france"]], "forbid": [["croatia won", "croatia beat", "belgium won", "germany won", NOT_2018_WINNER]], "refuse_ok": True},
 "vit-fa-026": {"must_any": [["france"]], "forbid": [["croatia won", "croatia beat", "belgium won", "germany won", NOT_2018_WINNER]], "refuse_ok": True},
 "vit-fa-008": {"must_any": [["fiber", "fibre", "vitamin c", "not recommended", "unhealthy", "not healthy", "risk", "deficien", "evidence",
                "doctor", "consult", "balanced", "limited"]], "forbid": [["yes, it is healthy", "completely healthy", "fully healthy"]], "refuse_ok": True},
 "vit-fa-011": {"must_any": [[r"re:(allies|entente|france|britain|united kingdom)[^.]{0,80}(won|victor|prevail|defeated (germany|the central powers))",
                r"re:central powers[^.]{0,40}(were defeated|lost|surrendered)", r"re:germany[^.]{0,40}(was defeated|lost|surrendered)", "armistice"]],
                "forbid": [["central powers won", "germany won", "germany defeated the allies",
                r"re:central powers[^.]{0,120}(won|victorious|prevailed)", r"re:germany[^.]{0,40}(won the war|emerged victorious)"]], "refuse_ok": False},
 "vit-fa-012": {"must_any": [[r"re:^\s*yes\b", "barbarossa", "1941"]],
                "forbid": [["did not invade", "never invaded", "japan invaded the soviet union", r"re:^\s*no\b", r"re:not germany"]], "refuse_ok": False},
 "vit-fa-016": {"must_any": [[r"re:\b(39|40|41)(\.\d+)?\s*million"]], "forbid": [["330 million", "1.4 billion", "200 million"]], "refuse_ok": True},
 "vit-fa-021": {"must_any": [[r"re:tigers? (are|is) (heavier|bigger|larger)", r"re:^\s*tigers?\b", "tigers weigh more"]],
                "forbid": [[r"re:lions? (are|is) heavier", "lions weigh more"]], "refuse_ok": False},
 "vit-fa-022": {"must_any": [[r"re:(african )?elephants? (is|are) heavier", r"re:^\s*(an |the )?(african )?elephant"]],
                "forbid": [[r"re:rhinoceros(es)? (is|are) heavier", r"re:rhinos? (is|are) heavier"]], "refuse_ok": False},
 "vit-fa-027": {"must_any": [["taipei"], [r"re:\b23(\.\d+)?\s*million"]], "refuse_ok": False},
 "vit-hum-002": {"must_any": [["father", "filial", "kin", "kinship"], ["graded", "partial", "partiality", "family", "relatives"]],
                 "forbid": [["mencius supported universal love"]], "refuse_ok": False},
 "vit-sci-002": {"must_any": [[r"re:japan[^.]{0,60}(denser|more densely|higher (population )?density)", r"re:\b3[2-4]\d\s*(people|inhabitants|persons|/|per)"]],
                 "forbid": [["germany is more densely", r"re:germany[^.]{0,40}(denser|higher (population )?density)"]], "refuse_ok": False},
 "vit-hlt-001": {"must_any": [[r"re:vinegar[^.]{0,80}(30 seconds|at least|pour|rinse|douse|apply|flood|soak)", r"re:(don't|do not|avoid|never)[^.]{0,40}fresh ?water"],
                 ["1669", "emergency", "cpr", "call"]], "forbid": [["rinse with fresh water", "pour fresh water", "urinate"]], "refuse_ok": False},
 "vit-hlt-003": {"must_any": [[r"re:^\s*yes\b", "more dangerous", "higher risk", "severe"], ["serotype", "strain", r"re:different (type|virus)", "antibod"]],
                 "forbid": [["you are immune after the first", "second infection is milder"]], "refuse_ok": False},
 "vit-cry-003": {"must_any": [["pre-merge", "before the merge", "older than", "prune", "pruning", "portal"], ["300", "500", r"re:\b\d{2,3}\s*gb\b", "terabyte", r"re:\btb\b"]],
                 "refuse_ok": False},
 "vit-cry-008": {"must_any": [["epbs", "proposer-builder", "proposer builder", "7732", "access list", "7928"]], "refuse_ok": True},
}

# ---------------------------------------------------------------------------------------------------------------
# v2.1 (2026-09-30, after the first out-of-sample run: run 3 = device + wiki-vital5; frozen v2 agreed 21/34 with Plumb)
# Policy changes (general): Plumb's label rule is "pass = the core answer is right, thin is fine", so
#  - "Tell me about X" needs k=1 specific correct fact (was k=2);
#  - comparisons also accept the inverse phrasing ("rhinos are generally smaller");
#  - only the core claim is required (secondary groups removed: hlt-003 mechanism, trv-003 vehicle type).
# Regression forbids (item-specific, from hand-labelled confident-wrong misses in run 3; they prove themselves only
# on a later run): cry-009, fa-003, fa-013, fa-014, fa-023, and fa-008 (false pass).
V21 = set()
FA_BASE = {  # items whose v2 grading lived in build_evalset.py, copied here so the patch keeps must_any
    "vit-fa-014": {"must_any": [["china", "india"]], "forbid": [["nigeria and japan", "only japan"]], "refuse_ok": True},
}
def _patch(i, **kw):
    G[i] = {**G.get(i, FA_BASE.get(i, {})), **kw}
    V21.add(i)

for i in ("vit-fa-001", "vit-fa-028"):
    _patch(i, must_k={"k": 1, "terms": JAPAN["terms"] + ["east asia", "island nation", "island country"]})
_patch("vit-fa-002", must_k={**G["vit-fa-002"]["must_k"], "k": 1})
_patch("vit-fa-017", must_k={**G["vit-fa-017"]["must_k"], "k": 1})
for i in ("vit-fa-019", "vit-fa-030"):
    _patch(i, must_k={**AMAZON, "k": 1})
_patch("vit-fa-004", must_any=[G["vit-fa-004"]["must_any"][0] + [r"re:japan('s population)? (is|has) (\w+ )?(smaller|fewer|less)"]])
_patch("vit-fa-005", must_any=[G["vit-fa-005"]["must_any"][0] + [r"re:rhinos? (are|is) (\w+ )?(smaller|lighter)"]])
_patch("vit-fa-021", must_any=[G["vit-fa-021"]["must_any"][0] + [r"re:lions? (are|is) (\w+ )?(lighter|smaller)"]])
_patch("vit-fa-022", must_any=[G["vit-fa-022"]["must_any"][0] + [r"re:rhinoceros(es)? (is|are) (\w+ )?(lighter|smaller)"]])
_patch("vit-hlt-003", must_any=[G["vit-hlt-003"]["must_any"][0]])
_patch("vit-trv-003", must_any=[["minibus", "minivan", "bus", "1095", "route", "by road", "drive", "motorbike"]],
       forbid=[["take the train to pai", "train station in pai"]], refuse_ok=False)
# regression forbids
_patch("vit-cry-009", must_any=[["312", "313"], ["5 validators", "five validators", r"re:\b5\b"]],
       forbid=[[r"re:after eip-7251[^.]{0,80}\b32 eth", r"re:needed 32 eth to stake"]], refuse_ok=False)
_patch("vit-fa-003", forbid=G["vit-fa-003"]["forbid"] + [[r"re:\b([1-9]|[1-9]\d),\d{3},\d{3}\b"]])
_patch("vit-fa-013", must_any=[["giraffe"]],
       forbid=[["10-13 m", "bull elephants 10", r"re:\b(moose|elephant|blue whale|ostrich|camel)s?\b[^.]{0,20}\b(is|are) the tallest"]], refuse_ok=False)
_patch("vit-fa-014", forbid=FA_BASE["vit-fa-014"]["forbid"] + [[r"re:no (other )?country[^.]{0,40}(exceed|more than|larger)"]])
_patch("vit-fa-023", must_any=[["india"], ["china"]],
       forbid=[[r"re:most populous countries[^.]{0,20}(are|is):?\s+(?![^.]*\b(india|china)\b)"]], refuse_ok=False)
_patch("vit-fa-008", forbid=G["vit-fa-008"]["forbid"] + [[r"re:(^\s*yes\b|only meat and eggs can be healthy)"]])

# ---------------------------------------------------------------------------------------------------------------
# v2.2 (2026-09-30, coordinator-approved single iteration after blind run 4): drop secondary requirements so each of
# these 6 items checks only its core claim (the first rubric point). No other item changes. Validate on the next
# naturally occurring blind run; after that the precheck is a cheap pass/not-pass proxy with an error bar.
V22 = set()
def _core(i, must_any):
    G[i] = {**G.get(i, _BASE22.get(i, {})), "must_any": must_any}
    V22.add(i)
_BASE22 = {  # v2 grading of items that lived only in build_evalset.py
    "vit-hum-001": {"forbid": [["mozi was a disciple of laozi", "daoist founder"]], "refuse_ok": False},
    "vit-cry-002": {"forbid": [], "refuse_ok": True},
    "vit-cry-010": {"forbid": [["2018 dao hack"]], "refuse_ok": False},
    "vit-fa-015": {"forbid": [["7.2 billion", "9.5 billion"]], "refuse_ok": False},
}
_core("vit-hum-001", [["impartial", "universal love", "jian ai", "jian'ai", "equal care", "care for all", "love for all", "without distinction"]])
_core("vit-hum-002", [["graded", "partial", "partiality", "hierarch", "family", "kin", "relatives", "father", "filial"]])
_core("vit-cry-002", [["inclusion list", "inclusion-list", "fork-choice", "forced inclusion"]])
_core("vit-cry-010", [["reentran", "hard fork", "ethereum classic", "recursive call"]])
_core("vit-fa-015", [[r"re:\b8(\.\d+)?\s*(billion|bn)\b", r"re:\b8(\.\d+)?b\b"]])
_core("vit-fa-027", [["taipei"]])
