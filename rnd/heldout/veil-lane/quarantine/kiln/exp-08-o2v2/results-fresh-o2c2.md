# exp-08 out-of-sample: O2 v2c on 23 new fresh items (o2c2)

- Determinism off vs off-rep: 23/23; counterfactual breaks: 0  → run VALID
- v2c hits: 3; OFF labels of hits: pass 1, cw 2, fail 0, refused 0, unlabelled 0 
- Δcw attributable on these items: -8.7 pp; Δpass: -4.3 pp
- **Fresh gate (§5: new false refusals ≤ 1 per 10 hits): 1/3 → FAIL**

| id | OFF label (hand / Jev) | reason code | OFF passages | OFF answer (start) |
|---|---|---|---|---|
| vit-o2c-023 | **pass** (pass / pass) | grounding:o2-off-subject | Wikivoyage: Architecture; Burj Khalifa | The Burj Khalifa is taller than Merdeka 118 [1]. The Burj Khalifa stands at 828 meters tall, while Merdeka 118 |
| vit-o2c-024 | **cw** (cw / cw) | grounding:o2-off-subject | Taipei 101; Wikivoyage: Architecture; Taipei 101 | Taipei 101 is taller than the Shanghai Tower [5]. Taipei 101 stands at 508 meters, while the Shanghai Tower is |
| vit-o2c-025 | **cw** (cw / cw) | grounding:o2-off-subject | Petronas Towers; Petronas Towers; Wikivoyage: Skyscrapers | The Petronas Towers in Kuala Lumpur, Malaysia, are taller than the Lotte World Tower in Seoul, South Korea. Th |
