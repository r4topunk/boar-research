# SMALLCLS: a small model as the search refiner (2026-10-19; criterion 132fa1f0; 0 judge, 0 paid; MacBook CPU, temp 0)

| system | A acc S30 | A acc FRESH | A emergency recall FRESH | A false alarms (40) | B acc S30 | B acc FRESH | p50 per call |
|---|---|---|---|---|---|---|---|
| hand rules (saferoute hazardTerms / engine E' section) | 21/30 | 45/85 | **7/45** | 2 | 9/24 | n/a | 0 |
| Qwen3-1.7B (no thinking) | 14/30 | 54/85 | **38/45** | **0** | 11/24 | 16/42 | 256 ms |
| Qwen3-4B-Instruct-2507 | 19/30 | 70/85 | 43/45 | 2 | 12/24 | 35/42 | 580 ms |

Verdict by the frozen rule: NOT ADOPTED as a whole. Q17 passes the A clause (+0.106 >= +0.10, false alarms 0 <= 4) but fails B (11/24 < 0.80; gas-leak item wrong). M4 also fails B on S30 (12/24) although it reaches 35/42 on the fresh set.
Reading:
- The hand hazard list was fit to the 30 items and does not generalise: emergency recall 7/45 on fresh wording ("the ground is shaking"). A small-model classifier fixes that at 0 false alarms; this is the strongest finding and the A part is worth building (classifier -> hazard search terms, replacing or backing up the list).
- Section choice is the hard part at 1.7B (38-46 %); the 4B does it well on fresh items (83 %). S30 gold sections are noisy (gold = heading above the first quoted sentence, sometimes a "Before" section for a "now" question), so S30 B understates both models.
- Unsafe items: chemical shelter-in-place correct for both models (the engine quoted the wrong section); gas leak wrong for both ("Natural Gas" vs "Know How to Shut Off Utilities" / fire extinguisher); 911 item has no section task.
Next (proposed): A-only adoption = Qwen3-1.7B or 4B hazard classifier feeding saferoute's search terms; B by the 4B with the corrected gold on a re-labelled set, or keep extracts off for danger items and let the answering model read the page.

## Correction (REVIEW-DIRECTION-2026-10-19, coordinator re-check)
"Recall 38/45" is emergency DETECTION (predicted any hazard), not the right hazard: right hazard on FRESH emergencies = Q17 14/45, M4 32/45, hand list 7/45 (it fires on 7). Feeding the 1.7B's label into search would mislabel 24/45 (heat stroke and frostbite -> Home Fires, gas leak -> Household Chemical). Only the 4B is a candidate for the hazard label.
