# exp-40: Gríma false correction + Japan crypto noise (Sonar, 2026-10-03 night; 2 h box)

TL;DR:
- **Gríma (b): no retrieval or alias fix works.**
  - The 4B, with the engine's own prompt and 3 seeds per context, denies the killing **15/15**: no context, kit A, rv2, rv2.2, and even the book sentence alone ("Saruman reveals crimes that Wormtongue has done, causing Wormtongue to turn on Saruman and kill him").
  - It even contradicts itself: "Gríma Wormtongue does not kill Saruman; it is Wormtongue who turns on and kills Saruman". This is a premise-denial reflex → Compass's premise guard (a).
  - An alias would also need top100k (2.5 GB) + a redirect-alias index, since kit A has no LOTR article. **Not worth it.**
  - Data: `answers.jsonl`, `gen.mts`, `contexts.json`.
- **Japan (c): a crypto-kit gate.** Crypto-kit chunks (EIPs/specs/ethereum.org/BIPs labels, or `pack:boar-crypto:` ids, incl. its Wikipedia crypto articles) need one of:
  - a crypto cue (CRYPTO_CUE);
  - a capitalised coin ticker (UST, LUNA…; added for Terra);
  - a chunk title that shares a term with the question.
- **Replay** (65 v0.1 EN + V-exact, places + detector, `--event-source-text`): only 3 contexts change.
  - vx-001 loses "Stablecoin" (the fix);
  - vx-002 loses "NSA cryptography";
  - vit-cry-006 loses generic DeFi/ZK ethereum.org pages.
  - The cue-less crypto items (PeerDAS, d/acc, Glamsterdam, Terra) are unchanged. Gold sentence unchanged. Routing tests 521/521.
- **Patches:** `cryptogate-on-tf1.patch` (delta); `tf2-on-cut2.patch` = cut2-norv2 + citation fix + exp-39 travel/food fixes + this gate.
