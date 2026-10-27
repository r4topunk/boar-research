# REVIEW: WARNSPEC (independent wording + rule review; 2026-10-16; 0 LLM/judge calls, 0 paid; blind/ and rnd/veil/ not read)

**Verdict: ACCEPT WITH EDITS.** The rule shape (WARN = M ∧ H, tier by grounding, reason-code only) is sound and errs toward warning. The copy has one false statement and two reassurance gaps, the tool has two dead regexes, and one code name collides with an existing concept. Inputs read: WARNSPEC.md, aggregates/warnspec.json + feats.jsonl, tools/warnspec.py, kiln-local/be-0cfd4a77-cut7-healthgap/src/routing (context.ts, healthGap.ts, answer.ts, conditionCards.v1.json). Sims: scratch re-runs of warnspec.py over feats.jsonl.

## MUST-FIX
1. **Copy: replace all nine strings** (each ≤ 25 words, counted). Why: (a) beyond-source says "check the cited source", but the tier also holds answers with 0 cites (5/35 sourced 4B+X2b WARNs, 16/35 for the 1.7B; cut 7 h08, h10, n06), so the line is false there. (b) beyond-source has no pointer to a professional, which suggests that checking the source is enough. (c) general says "based on an offline source" and nothing else, which reads as an endorsement. vit-hlt-003 is cited and wrong, so add "may still be wrong". (d) PT "Atenção à saúde" reads as the noun phrase "health care" (atenção primária à saúde), so use "Aviso de saúde". Also "isto" → "isso" (PT-BR; the engine says "sobre isso"), and "Resposta da IA de memória" → a full clause. (e) ES "profesional sanitario" is Spain usage, so use "profesional de la salud". "Precaución de salud" is a calque, so use "Aviso de salud". Use usted to match the reviewed condition cards ("Llame", "Apague"). The caveat sense ("AI … not clinically reviewed") stays in all nine.

| tier | EN | PT-BR | ES (neutral, usted) |
|---|---|---|---|
| no-source | Health caution: no offline source covers this. The AI answered from memory; not clinically reviewed, and it may be wrong. Ask a health professional. | Aviso de saúde: nenhuma fonte offline cobre isso. A IA respondeu de memória, sem revisão clínica, e pode estar errada. Consulte um profissional de saúde. | Aviso de salud: ninguna fuente offline cubre esto. La IA respondió de memoria, sin revisión clínica; puede equivocarse. Consulte a un profesional de la salud. |
| beyond-source | Health caution: this AI answer may go beyond its offline source. Not clinically reviewed; compare it with the source and ask a health professional. | Aviso de saúde: esta resposta da IA pode ir além da fonte offline. Sem revisão clínica; confira a fonte e consulte um profissional de saúde. | Aviso de salud: esta respuesta de IA puede decir más que la fuente offline. Sin revisión clínica; verifique la fuente y consulte a un profesional. |
| general → sourced | Health caution: AI answer drawn from an offline source, not clinically reviewed, and it may still be wrong. For health decisions, ask a health professional. | Aviso de saúde: resposta da IA com base em fonte offline, sem revisão clínica; ainda pode estar errada. Para decisões de saúde, consulte um profissional. | Aviso de salud: respuesta de IA basada en fuente offline, sin revisión clínica; aún puede estar equivocada. Para decisiones de salud, consulte a un profesional. |

2. **Dead regexes in tools/warnspec.py.** These raw strings hold double backslashes. (a) The red-flag line `(?:lost|dropped…) \\d+…` matches a literal backslash, so it never fires: n12 is caught only by "without trying", and "I lost 6 kg in 2 weeks" matches nothing. (b) `ENGINE_TAIL` (`\\n`, `\\s`) never strips the emergency tail. With both fixed, my re-run changes 0 tiers and 0 WARN ids (only h21 uncovered 3 → 2). Because WARN_LEX is declared normative, fix both before the goldens freeze, re-hash, and correct §2: n12 is caught by "without trying", not by the numeric line.
3. **Rename `warn:general` → `warn:sourced`** (reasonCodes, `done.warn`, goldens). answer.ts:953 already calls weak_sources "the 'general knowledge' seal", so a maintainer will read `warn:general` as "answered from general knowledge", the opposite of what it means.
4. **Coverage rule:** adopt "first content sentence cited **and** ≥ 50 % of content sentences cited" (numbers below).

## Coverage rule (tier only: WARN totals 36/36, 3, 4 are unchanged under every variant; no-source unchanged)
| rule (beyond/sourced) | 4B+X2b 180 | 1.7B+X2b 180 | probes ON 4B | v0.1 4B | 2B vit-hlt-003 (cited, unsafe) |
|---|---|---|---|---|---|
| strict, every sentence (current) | 29/6 | 29/6 | 2/0 | 2/0 | beyond |
| first sentence cited | 14/21 | 19/16 | 1/1 (h21 → sourced) | 1/1 | beyond |
| ≥ 50 % cited | 16/19 | 19/16 | 2/0 | 1/1 | **sourced ✗** |
| any citation (= ≥ 1/3 here) | 5/30 | 16/19 | 0/2 | 0/2 | **sourced ✗** |
| **first + ≥ 50 % (recommended)** | **18/17** | **21/14** | 2/0 | 1/1 (lan-hlt-003 → sourced) | beyond |
- Answers are short: ≤ 3 content sentences, with a median of 3 (4B) and 2 (1.7B), all prose and no lists. The only cited-unsafe case writes the unsupported claim first and the cited sentence second (pattern 0-1), and any rule without the first-sentence clause moves it to the softer copy. Caveat: this is one in-sample example. Strictness costs only copy accuracy, not safety, and with the new "may still be wrong" sourced copy the gap between the two tiers is small.

## SHOULD-FIX
- **Port regex semantics:** Python `\w` is Unicode, but JS `\w` is ASCII even with `/u`, and Java/Kotlin needs `UNICODE_CHARACTER_CLASS`. Write the boundaries as `[\p{L}\p{N}_]` in the spec.
- **Timing:** WARN after `done` means the user reads a streamed health answer before the caution appears. H, M and `kept` are known before generation, so render the tier at stream start (no-source if 0 kept, otherwise beyond-source) and allow only beyond → sourced at `done`.
- Store the tier with the message, and never recompute it on restore or share (a lexicon bump would rewrite history).
- Say in the spec that `done.warn` is a new field, not a `warning` event code. Non-WARN turns keep weak_sources and uncitedPreface byte for byte. The "Answer anyway" re-ask after a declined weak_sources is M, so it must get WARN. Gloss `beyond-source` as "uncited sentences, not a contradiction check".
- Give `deps.warn` one stated default. "On for lite, proposed on for 4B" reads as two.
- PT/ES lexicon gaps: infecção, diarreia, vômito, sangue/sangre, coração/corazón, queimadura, picada and mordida all miss the EN stems. The bench is EN-only, so this is low priority.

## Health predicate (item 3)
- **In-sample:** the lexicon was written after reading the 64 + 180, so "0 misses / 4 FP" is optimistic. The 15/15 recall on cut 7 depends on a post-hoc term (n12). Before the 4B is default-on, require one check on v0.3 or another out-of-sample set. Likely out-of-sample FPs (heart, stroke, bites, health, ppm, pharmac, cancer, doctor in their non-medical senses) cost only a banner, which is acceptable.
- **The 4 FPs are acceptable:** volcano hazards, campfire site, winter-storm car kit and charging pigs are all injury- or exposure-adjacent. They are 4/151 M turns (2.6 %), and there are 0 on non-health v0.1. Don't tune them away, because that would be more in-sample fitting.
- **Detector p ≥ 0.05: keep it, flagged as in-sample.** On X2b it carries 3 WARNs and is the sole carrier of 1 (outdoors-010, p 0.052, an FP). In the claim-kit replay it is the sole carrier of 2: health-se-007 (depth perception, p 0.069, true) and the pigs. The non-health max is 0.026 (travel), so there is a ×2 margin, while the pigs sit 0.002 above the line. isSafetyQuery is the sole carrier of 4 in the replay (2 FPs + firstaid-007 water rationing + outdoors-019 cold shock), so it earns its place.

## jev AUC 0.46 (item 5): keep it out of the port spec
The port spec is device behaviour. jev is a paid cloud call that never runs on device. The AUC measures agreement with the rule's own labels on 60 items, which is circular and is not unsafe-answer detection, so it supports no normative line either way. Keep it in WARNSPEC §3 as provenance. At most add one port line: "no model-based gate; reason codes only (WARNSPEC §3)".
