# Options: Ethereum hooks that make BOAR's privacy verifiable without breaking offline

TL;DR: **Options only. Nothing here is implemented or decided.** The rule that keeps offline intact: *the chain is never in the read path*. The phone verifies offline, against hashes and keys it already holds. Ethereum is only where a third party (or the user, on a desktop, once) looks up **which** hashes and keys are the real ones. Ranked by value before the 2026-10-31 decision: (E0) make release signing fail-closed and publish `(apk sha256, cert sha256, audit report sha256)`, which needs no chain and is mandatory; (E2) ENS contenthash → IPFS release directory, cheap and on-theme; (E3) EAS build attestation, useful only once someone can rebuild. Signed pack manifests (E1) and revocation (E5) belong after the bounty. This builds on `review/BOAR_INFO_NODE.md` §3 (L1 content-addressed packs, L2 EAS provenance) and does not repeat it.

## Framing

- Verifiability is a stated Vitalik value: locally-running computation improves "verifiability", and he proposes "locally running watcher LLMs" checking apps ([privacy, 2025-04-14](https://vitalik.eth.limo/general/2025/04/14/privacy.html); [openness & verifiability, 2025-09-24](https://vitalik.eth.limo/general/2025/09/24/openness_and_verifiability.html); quotes via Lantern).
- A competitor team copy under `competitor-b` practices reproducibility: auditable `.patch` files over an unmodified llama.cpp pin, and deterministic pack builds (per Lantern). Vitalik's authorship is [I] (unsigned commits, generic email). Not opened by Veil.
- BOAR constraints: the APK must make no network requests during use (`BOUNTY_31.md`). Submissions "materially different from the version reviewed" risk disqualification (`review/ETH_NODE_INTEGRATION.md:104`). "a chain serve para coordenar, não fica no caminho da leitura" (`review/STAKED_KNOWLEDGE.md:69`).
- What exists today (`threat-model.md` §T3): sha256 of every model/pack (39/39 catalog entries) is pinned **inside the APK bundle**. So the whole chain of trust hangs on the APK's signer. The published v1.0.0 is signed with BOAR's own key (`CN=BOAR`, cert SHA-256 `7cf514f9…1f01`), but that fingerprint isn't published anywhere a user can check, and the release plugin silently falls back to the public debug key. Every option below assumes E0 first.

```
E0 (no chain):           BOAR release key, cert sha256 published, fail-closed build ─► APK ─► pinned sha256 ─► models/packs
+ E2/E3 (optional):      ENS name ─► IPFS CID of release dir ─► {APK, cert, audit report}
                         EAS attestations by builder + rebuilders ─► same APK sha256
+ E1 (post-bounty):      publisher key (pinned in APK) ─► signed pack manifest ─► new packs w/o app update
```

## Options

| # | Option | What a verifier does | Offline impact | Cost | Risk | Worth before 2026-10-31? |
|---|---|---|---|---|---|---|
| **E0** | (a) release build **fails closed** without `BOAR_UPLOAD_*` (no silent debug fallback in `withReleaseSigning.js`); (b) publish `apk_sha256`, **cert SHA-256 `7cf514f9ab8253cbd78eb7d112d66fd05c2ad27e6fc987bf8f3276a7eedf1f01`**, and the `offline-proof` report sha256 in README + GitHub release + claim post; (c) `run-all.sh` release gate refuses `CN=Android Debug` on any distributed APK (implemented: `--require-release-key`). No chain | `sha256sum boar.apk`, `python3 audit_apk.py boar.apk --require-release-key`, compare cert with README | none | ~1 h | key loss = no updates (back it up offline) | **Yes, mandatory.** Closes the MEDIUM process gap in the threat model |
| **E2** | ENS contenthash ([EIP-1577](https://eips.ethereum.org/EIPS/eip-1577)) on a BOAR subname → IPFS CIDv1 of a release directory `{apk, cert.txt, SUMMARY.md, *.json, SHA256SUMS}` | Resolve the name on a desktop (any ENS client or `eth.limo` gateway), `ipfs add --only-hash --cid-version=1 -r release/` locally, compare CIDs | none. Lookup happens off-phone, before install | 1 L1 tx (`setContenthash`) + pinning. UNKNOWN: exact gas at current prices, estimated at <$5 | pinning centralization (Vitalik's complaint: `ETH_NODE_INTEGRATION.md:73`). CID ≠ raw sha256 (UnixFS chunking), so publish both. Name-owner key becomes a trust root | **Yes, optional.** Cheap, on-theme, and the claim already uses IPFS for screenshots (`CLAIMS_31.md:3`). Must not change the APK |
| **E3** | EAS attestation ([attest.org](https://attest.org)) with schema `{gitCommit, apkSha256, certSha256, auditReportSha256, verdict}` on Base. Builder attests; **independent rebuilders** attest the same `apkSha256` | Read attestations for the APK hash; count independent attesters | none | schema + ~1 tx per release. UNKNOWN: fees on Base, estimated at cents | Without a reproducible build it only says "the builder says so", i.e. E0 with extra steps. Reads as "crypto in the app" (`BOAR_INFO_NODE.md` L2 risk) | **Weak.** Only if O4 (a reproducible rebuild) lands. The audit-report hash is the novel part |
| E3' | Non-Ethereum baseline: GitHub artifact attestation (Sigstore/SLSA provenance) from a CI build | `gh attestation verify boar.apk --repo …` | none | hours, **if** CI builds the APK. Today builds are local (`builds/android/`) | trust in GitHub + Sigstore | compare with E3. Cheaper if CI exists |
| **E1** | Signed pack/model manifest: publisher signs `{packId, sha256, size, sourceUrl, license, snapshot}` (EIP-191/[EIP-712](https://eips.ethereum.org/EIPS/eip-712) typed data). The APK pins the publisher **address**. The app verifies with secp256k1 `ecrecover`, fully offline (`@noble/curves`, a sibling of the `@noble/hashes` already in `package.json`) | App shows "signed by boar.eth-address 0x…" on import | none. Verification is local math | 1–2 days + key ceremony | key compromise lets an attacker sign bad packs. Needs rotation/revocation (E5). Adds a new dependency | **No.** Pinned sha256 already covers packs shipped with the APK. The value is packs published *after* the APK (sideload / SD card / Wi-Fi Direct, BOAR_INFO_NODE L1) |
| E5 | Revocation / transparency log: publisher posts each release and pack hash on-chain; revocations too | Desktop or downloader flavor checks before import | offline flavor cannot check (by design) | small contract or EAS revocations | stale view on offline phones; revocation only works where network exists | **No.** Post-bounty, with E1 |
| E6 | Publisher key discoverable via an ENS text record (e.g. `boar.pubkey`) so rotation doesn't need an app update | Desktop lookup | offline app still needs the new key delivered (pack or update) | trivial once E1 exists | same as E2 name-owner risk | **No.** Only with E1 |

## Why not more

- **On-chain anything in the offline APK** (light client, RPC) is impossible without INTERNET and would break P1. `ETH_NODE_INTEGRATION.md` §3 already routes that to a separate `node` variant.
- **Attesting "truth" of content**: out of scope. The promise stays "proveniência verificável, nunca verdade verificável" (`BOAR_INFO_NODE.md:91`).
- **Tokens/bonds** (`STAKED_KNOWLEDGE.md`): orthogonal to privacy verifiability, and a perception risk before the claim.

## Decision inputs (for the coordinator / r4to, not decided here)

| Question | Veil's read |
|---|---|
| Does any hook change the reviewed APK? | E0 changes no APK (build config + docs; the published v1.0.0 already has the right key). E2/E3 don't touch the APK. E1/E5/E6 do, so they come after the bounty |
| Minimum that closes the loop | E0 + a README table `(apk sha, cert sha, report sha)` + `audit_apk.py` one-liner. Measured by: a stranger reproduces the verdict and hash in under 5 minutes |
| On-theme extra with low risk | E2 with a subname (e.g. `boar.<owner>.eth`). UNKNOWN: which ENS name the team controls |

## Metric + next step

- **Metric:** options ranked by (offline impact = 0 for all) × cost × value. 1 mandatory (E0), 1 cheap optional (E2), 4 deferred.
- **Next step:** after T1 (fail-closed signing + published fingerprint) lands, draft the release-directory layout + `SHA256SUMS` so E2 is a single `setContenthash` if chosen.

## UNKNOWN

- Gas/fee figures for `setContenthash` on L1 and EAS on Base are estimates, not quoted from a live source.
- Which ENS names the team owns and who holds the keys.
- Whether BOAR's RN/Hermes build is reproducible. This decides whether E3 is worth anything.
- Whether judges care about any of this. The bounty text asks for GitHub reproducibility and documentation, not attestations (`BOUNTY_31.md`).
