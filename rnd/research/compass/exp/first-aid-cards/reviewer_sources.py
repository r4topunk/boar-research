"""Source rows for the Opus reviewer's additions (2026-10-03), fetched raw with curl and converted locally
(snapshots-rev/*.txt; every quote is an exact substring, checked by check_reviewer_sources()). EXTRA maps
(card, edit 'where') -> cite ids appended to that edit in every language."""
from pathlib import Path
H = Path(__file__).resolve().parent
SR = {
 "STROKE-BEFAST": ("CDC, Signs and Symptoms of Stroke", "https://www.cdc.gov/stroke/signs-symptoms/index.html",
                   "If you think someone may be having a stroke, B.E. F.A.S.T. and do the following test: B—Balance Loss: Ask the person if they are feeling off-balance or dizzy. E—Eye (Vision) Changes: Ask the person if they have trouble seeing normally.", "ok (curl)", "cdc-stroke"),
 "DROWN-WARM-SJA": ("St John Ambulance (UK), Drowning", "https://www.sja.org.uk/get-advice/first-aid-advice/breathing-difficulties/drowning/",
                    "put them in the recovery position. You may also need to treat them for hypothermia by covering them with warm clothes and blankets.", "ok (curl)", "sja-drowning"),
 "HYPO-SUGARY-NHS": ("NHS, Low blood sugar (hypoglycaemia)", "https://www.nhs.uk/conditions/low-blood-sugar-hypoglycaemia/",
                     "Eat or drink something that will raise your blood sugar quickly, such as a small glass of fruit juice or sugary fizzy drink, 5 glucose or dextrose tablets, 4 large jelly babies, or 2 tubes of glucose gel.", "ok (curl); supports 'regular (not diet or zero)' only indirectly, via 'sugary'", "nhs-hypo"),
 "CHOKE-ADULT-SJA": ("St John Ambulance (UK), Adult choking", "https://www.sja.org.uk/get-advice/first-aid-advice/choking/adult-choking/",
                     "give five abdominal thrusts. To do this, stand behind them and put your arms around their waist. Place one hand in a clenched fist between their belly button and the bottom of their chest. With your other hand, grasp your fist and pull sharply inwards and upwards up to five times.", "ok (curl); NHS has no adult choking page (404), SJA used instead", "sja-adult-choking"),
 "HEAD-VOMIT-HD": ("healthdirect (AU), Head injuries", "https://www.healthdirect.gov.au/head-injuries",
                   "If you have a head injury and you vomit more than once, or you have a seizure (fit), seek emergency medical attention.", "ok (curl)", "hd-headinjury"),
 "SEA-CHEST-MEDL": ("MedlinePlus (US National Library of Medicine), Stingray", "https://medlineplus.gov/ency/article/002849.htm",
                    "A puncture to the person's chest or abdomen may lead to death.", "ok (curl)", "medl-stingray"),
}
EXTRA = {("drowning", "new step after 3"): ["DROWN-WARM-SJA"], ("hypoglycemia", "step 1 (replace)"): ["HYPO-SUGARY-NHS"],
         ("choking", "step 3 (replace)"): ["CHOKE-ADULT-SJA"], ("headinjury", "call (replace)"): ["HEAD-VOMIT-HD"],
         ("marinepuncture", "call (replace)"): ["SEA-CHEST-MEDL"]}

def check_reviewer_sources():
    bad = [k for k, v in SR.items() if v[2] not in (H / "snapshots-rev" / (v[4] + ".txt")).read_text()]
    return bad
