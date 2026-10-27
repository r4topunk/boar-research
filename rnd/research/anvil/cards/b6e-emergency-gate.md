# B6E: the 4B route gate's EMERGENCY label as the health detector
TL;DR: adding EMERGENCY as a third label to the B6 route gate (same forward, ≈ 0 extra cost) passed a detection-only blind replay on both blind sets (health-fresh2 90/90 danger, 6/60 hard negatives; health-fresh1 71/72, 2/48; lexical 23/90 + 9/60 and 32/72 + 11/48). **But Sonar's mmBERT v3b detector matches its recall with fewer false fires on the same sets (1/48, 2/60) and is answer-level blind-confirmed (scripted) on both tiers, so the B6E answer arm was KILLED by dominance.** B6E is shelved as the 0-MB fallback.
Lane: Anvil · Status: tested (blind detection PASS; answer arm killed, dominated) · Priority: C (fallback)
Axes moved:
- safety ↑ vs lexical (blind recall 43% → 97–100%); ≈ vs mmBERT v3b on recall, worse on hard negatives;
- latency: ≈ 0 extra on the 4B (the B6 gate's forward; +157 cached prefix tokens);
- resources: 0 MB, vs mmBERT's ~85 MB footprint and 16–35 ms per message on g75 (Forge).

Fits BOAR? Only on the 4B. On the 1.5B the gate prompts don't transfer: my label prompts got 105–137/185 on dev; Compass's yes/no prompt got 171/185 but 9/40 hard-negative fires.

Evidence:
| Set | B6E | mmBERT v3b engine | Lexical health9 |
|---|---|---|---|
| health-fresh2 blind, danger / HN | 90/90, 6/60 | 90/90, 2/60 | 23/90, 9/60 (detection only) |
| health-fresh1 blind, danger / HN | 71/72, 2/48 | 71/72 (near-dup), 1/48 | 32/72, 11/48 |
| Anvil dev pool 599, E / NOT / hard negatives | 180/185, 1/391, 0/40 | 182/185, 2/391, 0/40 | 121, 10, 10 |
| Compass emergency-dev 300, E / critical missed / strict FF / how-to | 169, 5, 22/100, 7/20 | 179, 0, 17/100, 14/20 | 41, —, 43/100, — |

- B6E's errors and v3b's are nearly disjoint (Compass dev):
  - **gate only:** pets, figurative, news;
  - **v3b only:** routine, resolved.
- A union adds at most 1 blind catch and only adds false fires.
- **B6E's weakness:** generic first-aid how-to ("como trata queimadura de água-viva?") scores p(EM) ≈ 0, so it goes to the model. Multi-turn status updates ("la ambulancia tarda 40 min") are missed too.
- Artifacts:
  - `exp/emergency-gate/`: pool, labels, prompts with pre-registered sha256s, runs;
  - `blind-replay/`: the frozen criterion d88d5efe and `replay.mts`;
  - `arm/`: the b6e engine patch 3753e524, L0 parity 735/735, the floors analysis, and the killed L2 criterion fc5df39a (never run).

Reuse:
- The **3-label verdict + cached-gate machinery**: one forward, verdict reused, calculator veto. It's ready if mmBERT can't ship on some device class.
- `b6-on-health12final.patch` (68f9868d…, units 1192/1192): the adopted B6 route gate on Sonar's final health stack, without B6E.

What would revive it: a device class where +85 MB is not affordable but the 4B runs, or mmBERT failing a fresh blind set (health-fresh3) where B6E holds.
