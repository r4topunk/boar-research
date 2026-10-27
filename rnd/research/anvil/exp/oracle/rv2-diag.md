# rv2 L1 KILL: hand-read of 18 items + what Q450 gives the 4B that rv2 doesn't (Anvil, 2026-10-03; joint reading with Sonar)

**Inputs (read-only):**
- `boar-eval/runs/kiln/rv2-l1/`: R = rv2 + top100k, s42/s43; A = bounty1 kit, s43 for answers. For R, the last `sources` event with text is what the 4B saw.
- judge.v1 rationales.
- `anvil/exp/oracle/ctx-Q450.jsonl` + Q450 judgments (1 rep).
- Per-item comparison: `anvil/exp/rv2-diag/compare.py` → `rows.jsonl`.

## TL;DR
- **rv2 gets the right article more often but feeds the 4B the wrong part of it, plus noise.**
  - Gold article present in R's sources: 25/45 items with a Wikipedia gold article. Absent on 20.
  - When present, R mostly hands over **lead/overview chunks** (Brazil "largest country in South America", Kenya history), not the **facet** the question asks for (population, official languages, independence date).
  - Q450 picks the facet passage from the whole article, often from a facet sub-article (Demographics of Brazil/Russia, Languages of Singapore, Economy of Montenegro), and carries **no off-topic windows**.
- **Losses come from 3 mechanisms:**
  1. a partial fragment overrides a correct memory answer;
  2. numbers in context, but the 4B reasons badly over them;
  3. off-topic windows displace a good kit passage or add noise (Quadratic equation for quadratic funding; Ruhr/ISRO/Mumbai airport for "countries bigger than India").
- **Five of the 12 losers are mostly seed noise.**
- **Wins come from one thing:** the right lead/fact passage filled a gap.
- **Unreachable for any Wikipedia pack:** on 6 of the 18 items, Q450's context is entirely web pages (space.com, Snopes, Gitcoin, travel blogs, Livescience, a-z-animals). On those, Q450's edge isn't buyable with packs.

## Per item (R − A per Sonar; labels: a fragment overrides memory · b reasoning over numbers in context · c off-topic/wrong window displaced a good passage or added noise · d style · e judge/seed noise · f right window filled a gap)
| item | label | evidence (what the 4B saw → what it said) |
|---|---|---|
| lan-rsn-002 Baikal/Burj | **b** (+c) | Saw "maximum depth of 1,642 metres" and the Burj lead, plus a Eurasian Economic Union window → "its top would still be about 829.8 meters above the lake's surface… So yes". A, with no context, reasoned it correctly ("below the surface by roughly 814 m"). Q450 (with a Guinness "deepest lake" passage) 0.70 |
| lan-cmp-001 Brazil vs Russia | **b + c** | Saw "Foreign relations of Russia" + Brazil/Russia **leads** (area, not population) → "No, Brazil does not have more people than Russia… Brazil has about 212 million. Therefore, Brazil has a larger population". Q450 had *Demographics of Brazil/Russia* ("203 million in 2022") → 0.87 |
| lan-exp-003 Kenya | **a** | 4 Kenya windows (history, lead, cities), none on languages → "the official language is English" (drops Swahili). A from memory: "English and Swahili" |
| vit-hum-002 Mozi/Mencius | **e** (+a) | Saw Mohism/Confucianism windows, none on Mencius's attack → "Mencius did not directly attack Mozi". A said the same; R 1.0 vs A 2.0 is mostly judge spread. Q450 (Mozi article) 0.29 also fails: a knowledge gap in both |
| vit-cry-003 EIP-4444 | **b** | Saw "Historical blocks… occupy more than 400GB" → "reduce storage needs from hundreds of GB to tens of GB" / "under 100GB". The number was in context and it misread it. Q450 (2025 web sources on partial expiry) 0.55 |
| lan-ref-002 Civil War | **e** (+a) | s43 = A (4.0). s42 picked up "May 26, 1865" from the lead → "ended on May 26… with… the abolition of slavery" (judge: debatable end date) |
| vit-cry-006 quadratic funding | **c** | Windows: the post author paper, Referendum, **Quadratic equation ×2** → "can lead to inefficient funding allocations" (loses A's collusion weakness) |
| vit-trv-003 Chiang Mai–Pai | **c** (+e) | Saw Wikivoyage Chiang Mai "Go next" (no Pai) + a night-market window → "about 120 km… 2–2.5 hours" / "1.5 to 2 hours". Q450 had the route-advice web pages → 0.71 (web-only gold) |
| lan-exp-001 Singapore | **c** (+e) | R's 3 windows were all about **languages**. The history passage A's kit had ("independent on 9 August 1965") was displaced → s42 "independence… on June 3, 1965" (wrong). s43 was better than A |
| vit-cry-011 Terra | **e** | Good windows (Stablecoin, Do Kwon, Terra) → answer ≈ A's quality; small delta |
| lan-cmp-003 bigger than India | **c** (+e) | Windows ISRO, Mumbai airport, Ruhr ×2 (pure noise) → memory answer, partly wrong ("Russia, Canada, and China"). A also contradicts itself |
| lan-rsn-001 Great Wall | **e** | Right windows (Great Wall, Moon myth) → same answer as A; the gap is judge spread |
| lan-exp-006 Kilimanjaro | **f** | Lead "large dormant volcano in Tanzania… highest… free-standing" → correct, cited. (2 of its 5 windows are **reference-list junk**: "Retrieved 3 January 2019. 85. ↑ …") |
| lan-ref-003 Moon before 1970 | **f** (+new error) | List of Apollo astronauts → "Yes" (A said "No", wrong), but adds "six of the twelve… by 1970" (should be four) |
| lan-ref-005 Rio 2016 | **f** (+e) | 2016 Olympics lead + closing ceremony → adds dates. A was already right |
| lan-cmp-005 crocodiles | **f** | Saltwater crocodile article → sizes and weights; "largest living reptiles" |
| lan-exp-002 Montenegro | **f** | Lead (Podgorica, June 2006 independence) + "Unilateral euro adoption" window → capital/currency/independence right |
| lan-exp-005 Sahara | **f** | Sahara lead "9,200,000 km²" → size and more countries. Output shows "**9 [2].2 million**": a citation marker inserted **inside a number** (engine bug, also in A: "9 [2].4 million") |

## What Q450 gives the 4B that rv2 doesn't
1. **The facet passage, not the lead.** Q450 ranks every ~120-word window of the gold articles by the question and lands on population/languages/independence/euro. rv2's windows cluster on leads and history. Facet sub-articles (Demographics of …, Languages of …, Economy of …) carry most of Q450's comparison/number answers.
2. **No noise.** Q450 = 3 windows from 1–3 gold documents. rv2 mixes in wrong-article windows (Quadratic equation, Ruhr, Foreign relations of Russia) and reference-list chunks. The 4B uses whatever numbers it sees, and noisy or partial numbers flip correct memory answers (lan-cmp-001, lan-rsn-002, lan-exp-003).
3. **More words of the right kind:** 284 vs 216 words p50 (R after its clean step). Size alone is a small factor: R1500 vs R450 was only +0.02.
4. **Sources outside Wikipedia:** on 6/18 of these items, Q450's whole context is web pages no pack holds. Part of Q450's 0.567 is unreachable for rv2 by construction.
5. **Ordering is not the issue:** when R has a gold window it is usually rank 1 (19/25).

## Suggested fixes (for Sonar's next rv iteration; Anvil can L0 any of them on ctx data)
- **Facet-aware window choice within an article:** score windows by the question's facet terms (population, language, capital, currency, independence, height, depth), not the lead by default. Add facet sub-articles (Demographics/Languages/Economy/Geography of X) to the top-100k selection.
- **Noise gate:** drop a window whose article title shares no entity with the question (Quadratic equation ≠ quadratic funding; Ruhr ∉ India). Strip reference/bibliography sections at pack build ("Retrieved …", "↑").
- **Protect on-subject kit passages from displacement** (Singapore's history window).
- **Engine bug:** `citations:added` puts `[n]` inside numbers ("9 [2].2 million"). Snap insertions to sentence or clause ends.
