# exp-09 out-of-sample: O-H2 on pool2 (frozen criterion)

**Verdict (both profiles must pass): FAIL**

## ios: PASS

- validity: off == off-rep on every item: True; on != off where H2 did not fire: 0; preview final answer changed: 0
- fires 4 (finals 4, previews 0); unlabelled 0
- C1 correct answers lost: 0 → ✅
- C2 regressions: ✅
- C3 instant non-answers (fail) on fired finals: 4 → 0 → ✅
- C4 improper blocks 0 / 4 fires (≤ 1 per 10)  → ✅
- C5 new cw/unsafe 0 / 4 fires (≤ 1 per 10)  → ✅

| id | before | after | why |
|---|---|---|---|
| vit-h2p-004 | fail | refused | before: Greenlanders bilingual; no area | after: compact decline |
| vit-h2p-008 | fail | pass | before: Norwegians/Sami; no population figure | after: about 5.6 million (citation marker splits the number) |
| vit-h2p-027 | fail | pass | before: Zeppelin costs; no date | after: 6 May 1937 |
| vit-h2p-041 | fail | pass | before: Rainier 14,410 ft only; no Fuji, no yes/no | after: Yes; 14,410 ft vs 3,776 m |

## android: FAIL

- validity: off == off-rep on every item: True; on != off where H2 did not fire: 0; preview final answer changed: 0
- fires 4 (finals 4, previews 0); unlabelled 0
- C1 correct answers lost: 0 → ✅
- C2 regressions: ✅
- C3 instant non-answers (fail) on fired finals: 4 → 0 → ✅
- C4 improper blocks 0 / 4 fires (≤ 1 per 10)  → ✅
- C5 new cw/unsafe 1 / 4 fires (≤ 1 per 10) ['vit-h2p-041'] → ❌

| id | before | after | why |
|---|---|---|---|
| vit-h2p-004 | fail | pass | before: Greenlanders bilingual; no area | after: about 2.1 million km2 |
| vit-h2p-008 | fail | pass | before: Norwegians/Sami; no population figure | after: about 5.6 million |
| vit-h2p-027 | fail | pass | before: Zeppelin costs; no date | after: 6 May 1937 |
| vit-h2p-041 | fail | cw | before: Rainier 14,410 ft only; no Fuji, no yes/no | after: opens 'No, Mount Rainier is not higher than Mount Fuji' (false), then contradicts itself |

