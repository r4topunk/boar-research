# exp-32: V-exact retrieval checks (Sonar, 2026-10-03; EN)
Run: bounty1 (health13 + travel distance), Android 4B config, kit A (crypto + Wikivoyage); `traces.jsonl`, `prompts.jsonl`.
- **vx-002 "Which signature algorithms are quantum resistant?": NOT a retrieval failure on this arm.** raw = Quantum cryptography / NSA cryptography / Post-quantum cryptography. The 4B names Dilithium, Falcon and SPHINCS+ as NIST's lattice- and hash-based signatures [1]. A coverage agent's "declines" reading came from older arms.
- **"Which signature schemes has NIST standardized…"**: NIST PQC Standardization article retrieved; the answer names Dilithium, Falcon, SPHINCS+, the August 2024 release and FIPS 206 FN-DSA in draft. Good.
- **vit-hum-001 Mozi: a COVERAGE failure in kit A.**
  - raw = TrueCrypt + 3 ethereum.org pages, all off-topic-dropped → `no-source-memory`, answered with the "not from an offline source" preface. The content is roughly right.
  - The fix is a Wikipedia body for Mozi. Mozi ranks ~176k by views, so it is not in top100k; top300k (~7.3 GB) or the full EN (18.4 GB) has it.
- **Next (needs Kiln's mini, where `boar-wiki-en-top100k` 2.54 GB lives):** an L1 of kit A + top100k WITH THE FIXED LEAD VECTORS vs kit A, on V-exact + the v0.1 EN slice.
  - The old #6 top100k gate failure was measured with mislabelled lead vectors (A-pack-coverage.md caveat), so the "bigger pack adds noise" verdict may not hold.
  - If it helps: a title-lookup tier into the full EN for named entities (Mozi, Gríma) is the next step.
