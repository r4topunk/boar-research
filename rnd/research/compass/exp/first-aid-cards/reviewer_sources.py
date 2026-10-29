"""Source rows for the Opus reviewer's additions (2026-10-03), fetched raw with curl and converted locally
(snapshots-rev/*.txt; every quote is an exact substring, checked by check_reviewer_sources()). EXTRA maps
(card, edit 'where') -> cite ids appended to that edit in every language."""
from pathlib import Path
H = Path(__file__).resolve().parent
SR = {
 "STROKE-BEFAST": ("CDC, Signs and Symptoms of Stroke", "https://www.cdc.gov/stroke/signs-symptoms/index.html",
                   "If you think someone may be having a stroke, B.E. F.A.S.T. and do the following test: B—Balance Loss: Ask the person if they are feeling off-balance or dizzy. E—Eye (Vision) Changes: Ask the person if they have trouble seeing normally.", "ok (curl)", "cdc-stroke"),
 "DROWN-WARM-SJA": ("St John Ambulance (UK), Drowning", "https://www.sja.org.uk/get-advice/first-aid-advice/breathing-difficulties/drowning/",
                    "[quote withheld (copyright); see url]", "ok (curl)", "sja-drowning"),
 "HYPO-SUGARY-NHS": ("NHS, Low blood sugar (hypoglycaemia)", "https://www.nhs.uk/conditions/low-blood-sugar-hypoglycaemia/",
                     "[NHS quote withheld]", "ok (curl); supports 'regular (not diet or zero)' only indirectly, via 'sugary'", "nhs-hypo"),
 "CHOKE-ADULT-SJA": ("St John Ambulance (UK), Adult choking", "https://www.sja.org.uk/get-advice/first-aid-advice/choking/adult-choking/",
                     "[quote withheld (copyright); see url]", "ok (curl); NHS has no adult choking page (404), SJA used instead", "sja-adult-choking"),
 "HEAD-VOMIT-HD": ("healthdirect (AU), Head injuries", "https://www.healthdirect.gov.au/head-injuries",
                   "[quote withheld (copyright); see url]", "ok (curl)", "hd-headinjury"),
 "SEA-CHEST-MEDL": ("MedlinePlus (US National Library of Medicine), Stingray", "https://medlineplus.gov/ency/article/002849.htm",
                    "[MedlinePlus encyclopedia (A.D.A.M.) quote withheld; see url]", "ok (curl)", "medl-stingray"),
}
EXTRA = {("drowning", "new step after 3"): ["DROWN-WARM-SJA"], ("hypoglycemia", "step 1 (replace)"): ["HYPO-SUGARY-NHS"],
         ("choking", "step 3 (replace)"): ["CHOKE-ADULT-SJA"], ("headinjury", "call (replace)"): ["HEAD-VOMIT-HD"],
         ("marinepuncture", "call (replace)"): ["SEA-CHEST-MEDL"]}

def check_reviewer_sources():
    bad = [k for k, v in SR.items() if not v[2].startswith("[") and v[2] not in (H / "snapshots-rev" / (v[4] + ".txt")).read_text()]  # withheld rows (v1.1.2) are not checked
    return bad
