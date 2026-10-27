import json
I = []
def add(aid, cat, style, q, a, rub, facts):
    I.append({"article_id": aid, "category": cat, "style": style, "question": q, "answer": a, "rubric": rub,
              "in_pack_facts": [{"fact": f, "quote": s} for f, s in facts]})
add(33, "pq-signatures/ml-dsa", "direct",
 "What is ML-DSA and what hard math problem is it built on?",
 "ML-DSA, the Module-Lattice-Based Digital Signature Algorithm, is the signature scheme approved in NIST FIPS 204 (August 2024). Its security rests on the Module Learning With Errors problem, and it is believed to stay secure even against an attacker with a large-scale fault-tolerant quantum computer. It is believed to be strongly unforgeable, so it detects tampering and authenticates the signer, and it supports non-repudiation. It comes in three parameter sets with different security strengths and can replace older schemes such as those in FIPS 186-5.",
 ["Identifies ML-DSA as the lattice-based signature standard in FIPS 204", "Says it is based on the Module Learning With Errors problem", "Says it is believed secure against large-scale quantum computers", "Mentions three parameter sets or that it can replace FIPS 186-5 schemes", "Penalize: claiming ML-DSA is based on factoring or elliptic curves"],
 [("Based on MLWE", "which is based on the Module Learning With Errors problem [4]"),
  ("Three parameter sets", "ML-DSA is standardized with three")])
add(44, "pq-signatures/ml-dsa", "first-person",
 "My little device has no good random number source. Can I still produce ML-DSA signatures, and is there a catch?",
 "Yes. FIPS 204 by default uses a hedged signing procedure that mixes fresh randomness at signing time with a precomputed random value from the private key, but it also allows a fully deterministic variant for signers with no fresh randomness. The catch is that without randomness, side-channel attacks, especially fault attacks, are harder to mitigate, so the deterministic variant should not be used where such attacks are a concern and cannot be otherwise mitigated. Signatures from either variant are checked with the same verification algorithm.",
 ["Says a deterministic signing variant is permitted when no fresh randomness is available", "Explains the default hedged variant combines fresh and precomputed randomness", "Warns that the deterministic variant makes side-channel / fault attacks harder to mitigate", "Says the same verification works for both variants", "Penalize: saying ML-DSA cannot be used at all without a random number generator"],
 [("Deterministic variant allowed", "This document also permits a fully deterministic variant of the signing procedure in case the signer has"),
  ("Side-channel risk", "deterministic variant makes the risk of side-channel attacks (particularly fault attacks) more difficult to")])
add(53, "pq-signatures/ml-dsa", "direct",
 "When would someone use HashML-DSA instead of plain ML-DSA?",
 "HashML-DSA is the pre-hash version of ML-DSA in FIPS 204. It signs a digest of the message plus domain separation information instead of the message itself. It is meant for cases where hashing a large message inside the signing module would be too slow, for example when a platform has hardware hashing support but not for SHAKE256. In general the pure ML-DSA version is preferred, key generation is the same for both, and NIST recommends using each key pair for only one of the two versions. The context string can be up to 255 bytes.",
 ["Explains HashML-DSA signs a digest of the message (pre-hash)", "Gives the large-message performance / missing SHAKE256 hardware reason", "Says pure ML-DSA is generally preferred", "Mentions key reuse advice or the 255-byte context limit", "Penalize: claiming HashML-DSA is a different post-quantum algorithm family"],
 [("Pure preferred", "In general, the “pure”"),
  ("Context limit", "The context string has a maximum"),
  ("One version per key", "be used for one version or the other.")])
add(30, "pq-kem/ml-kem", "first-person",
 "I read that the final Kyber standard is a bit different from the competition version. What changed in ML-KEM compared to round three?",
 "FIPS 203 (ML-KEM) changes several details of the round-three CRYSTALS-Kyber specification. The shared secret key is now fixed at 256 bits instead of a variable length. Encapsulation and decapsulation use a different Fujisaki-Okamoto transform variant, so encapsulation no longer hashes the ciphertext into the shared secret. The extra step that hashed the initial randomness m was dropped because NIST-approved randomness generation is required. Explicit input checks were added, such as checking that the encapsulation key decodes correctly modulo q.",
 ["Says the shared secret key length is fixed at 256 bits", "Mentions the changed Fujisaki-Okamoto transform / no ciphertext hash in the shared secret", "Mentions removal of the hashing of the initial randomness m", "Mentions the added explicit input checking", "Penalize: claiming ML-KEM is a signature scheme"],
 [("256-bit shared secret", "specification, the length of the shared secret key is fixed to 256 bits."),
  ("Input checks added", "This specification includes explicit input checking steps that were not part of the third-round")])
add(23, "pq-kem/ml-kem", "imperative",
 "Explain what keys come out of ML-KEM key generation and which one I must keep secret.",
 "ML-KEM.KeyGen (Algorithm 19 in FIPS 203) takes no input, generates its own randomness and outputs an encapsulation key and a decapsulation key. The encapsulation key can be published, while the decapsulation key must stay private. The 64 bytes of seed material (d, z), two 32-byte random values, can be stored and later expanded into the keys, so the seed is sensitive and must be protected like the decapsulation key. Optional key pair checks exist, but they cannot prove the pair was properly generated.",
 ["Names the two outputs: encapsulation key and decapsulation key", "Says the encapsulation key may be public and the decapsulation key private", "Says the seed (d, z) must be protected like the decapsulation key", "Mentions that key pair checks do not guarantee proper generation", "Penalize: telling the user to publish the decapsulation key"],
 [("Public vs private", "While the encapsulation key can be made public, the decapsulation key shall remain private."),
  ("Seed is sensitive", "the decapsulation key, it is sensitive data and shall be treated with the same safeguards as a")])
add(73, "pq-signatures/slh-dsa", "direct",
 "Where does SLH-DSA come from, and how many algorithms were submitted to the NIST post-quantum competition?",
 "SLH-DSA, the stateless hash-based digital signature algorithm in FIPS 205, is the standardized form of SPHINCS+. NIST started its public Post-Quantum Cryptography Standardization process in 2016 because large quantum computers would break public-key schemes based on factoring and discrete logarithms. 82 candidate algorithms were submitted, and after three rounds NIST picked the first four for standardization; SPHINCS+ is one of them, with minor changes from its round-three Version 3.",
 ["Says SLH-DSA is the standardized SPHINCS+ (FIPS 205)", "Says the NIST PQC process began in 2016", "Gives 82 submitted candidates", "Mentions four algorithms selected after three rounds", "Penalize: saying SLH-DSA is a lattice-based scheme"],
 [("82 candidates", "for standardization. A total of 82 candidate algorithms were submitted to NIST for consideration."),
  ("SPHINCS+ renamed", "this standard, SPHINCS+ will be referred to as SLH-DSA for stateless hash-based digital signature")])
add(78, "pq-signatures/slh-dsa", "imperative",
 "List the main implementation rules a crypto module has to follow for SLH-DSA.",
 "FIPS 205 requires that key generation draw three fresh random n-byte values (PK.seed, SK.seed, SK.prf) from an approved random bit generator with at least 8n bits of security strength. Implementations must destroy local copies of inputs and sensitive intermediate data as soon as they are no longer needed. Where public-key validation is required, the public key must be checked to be 2n bytes, and a regenerated private key 4n bytes. Floating-point arithmetic must not be used because rounding errors can give wrong results.",
 ["Mentions fresh random values from an approved RBG for key generation", "Mentions destroying sensitive intermediate data", "Mentions key length checks (public key 2n bytes / private key 4n bytes)", "Mentions the ban on floating-point arithmetic", "Penalize: inventing a requirement to keep a signing state counter"],
 [("No floating point", "Floating-point arithmetic. Implementations of SLH-DSA shall not use floating-point arithmetic,"),
  ("Public key length", "shall verify that the public key is 2𝑛 bytes in length.")])
add(169, "stateful-hbs/winternitz", "first-person",
 "I'm trying to understand hash-based signatures. How does a Winternitz one-time signature actually sign each piece of the message?",
 "In the Winternitz scheme used by LMS and XMSS (NIST SP 800-208), the message is hashed and the digest is written as a base-b number. Each digit gets its own hash chain: a random secret value is the private key and hashing it b-1 times gives the public key. A digit of value N is signed by hashing the secret N times; the verifier hashes the signature the remaining times and compares with the public key. A checksum is also signed so an attacker cannot forge by increasing digits.",
 ["Says the digest is encoded as base-b digits, each signed with its own hash chain", "Says the public key is the secret hashed b-1 times and a digit N is signed by hashing N times", "Explains verification by finishing the chain and comparing to the public key", "Mentions the checksum that prevents forgeries", "Penalize: describing it as based on lattices or factoring"],
 [("Winternitz in LMS/XMSS", "Both LMS and XMSS make use of variants of the Winternitz signature scheme."),
  ("Checksum", "In order to protect against the above attack, the Winternitz signature scheme computes a")])
add(170, "stateful-hbs/merkle", "direct",
 "Why do XMSS and LMS use a Merkle tree instead of just publishing all the one-time public keys?",
 "Concatenating many one-time signature public keys into one long-term key would make that key unacceptably large. XMSS and LMS instead build a Merkle hash tree: each OTS public key is hashed into a leaf, leaves are hashed together in pairs level by level, and the single root becomes the short long-term public key. Each signature then carries a little extra data, the sibling hashes along the path, so a verifier can recompute the root and check that the one-time key belongs to it.",
 ["Says concatenating the one-time keys would give an unacceptably large public key", "Explains leaves are hashes of OTS public keys hashed in pairs up to a root", "Says the root is the long-term public key", "Says signatures include the authentication path / sibling hashes", "Penalize: claiming the Merkle tree removes the need to track state"],
 [("Too large otherwise", "simply concatenating the keys together, the resulting public key would be unacceptably large."),
  ("Root is public key", "root of the tree), which will be used as the long-term public key.")])
add(179, "stateful-hbs/parameters", "imperative",
 "Give me the XMSS parameter sets NIST approves with SHA-256 and their tree heights.",
 "SP 800-208 approves three XMSS parameter sets with SHA-256, all using WOTSP-SHA2_256 with n = 32, w = 16 and len = 67: XMSS-SHA2_10_256 (height 10), XMSS-SHA2_16_256 (height 16) and XMSS-SHA2_20_256 (height 20). Multi-tree XMSSMT sets range from total height 20 to 60 with 2 to 12 layers, for example XMSSMT-SHA2_20/2_256. RFC 8391 sets using SHAKE128, SHAKE256 and SHA-512 are not approved by this publication.",
 ["Names XMSS-SHA2_10_256, XMSS-SHA2_16_256 and XMSS-SHA2_20_256", "Gives heights 10, 16 and 20", "Mentions n = 32 / w = 16 / WOTSP-SHA2_256", "Mentions XMSSMT multi-tree sets or that SHAKE128/SHA-512 RFC 8391 sets are not approved", "Penalize: inventing parameter sets not in the tables"],
 [("Height-20 set", "XMSS-SHA2_20_256 · 0x00000003 · 32 · 16 · 67 · 20"),
  ("Some RFC sets not approved", "that use SHAKE128, SHAKE256, and SHA-512 are not approved for use by this")])
add(118, "classical-signatures/fips186-5", "first-person",
 "Before I start signing documents with ECDSA, what do I need to set up and what assurances should I get first?",
 "FIPS 186-5 says an intended signatory using ECDSA or EdDSA first obtains domain parameters, either generating them or getting them from another entity, and gets assurance they are valid (SP 800-89). It then obtains a key pair, generated itself or by a trusted party, which must be trusted not to masquerade as the owner. The owner then needs assurance that the public key is valid and that it really possesses the private key. Verifiers need assurance of identity, for example a certificate from a certification authority.",
 ["Says ECDSA/EdDSA need domain parameters with validity assurance (RSA does not)", "Mentions obtaining a key pair, possibly from a trusted party that must not masquerade", "Mentions public-key validity and private-key possession assurances (SP 800-89)", "Mentions identity assurance, e.g. a CA certificate", "Penalize: saying no setup is needed beyond generating a key"],
 [("RSA has no domain parameters", "Note that the RSA algorithm does not use domain parameters."),
  ("CA certificate example", "mutually trusted party. For example, a certification authority (CA) could sign credentials")])
add(130, "classical-signatures/ecdsa", "direct",
 "What is deterministic ECDSA and why would a device want it?",
 "ECDSA needs a new secret per-message number k for every signature, kept as secret as the private key. In deterministic ECDSA, specified in FIPS 186-5, k is derived from the message being signed and the private key, so the same message always gives the same signature. This protects against attacks where weak randomness in k reveals the private key, which makes it attractive for devices without a good source of quality random numbers.",
 ["Says ECDSA needs a fresh secret per-message number k", "Says deterministic ECDSA derives k from the message and the private key", "Says it protects against private-key leaks from poor randomness", "Mentions devices lacking quality random number sources", "Penalize: saying deterministic ECDSA is quantum resistant"],
 [("Definition", "Deterministic ECDSA is a variant of ECDSA where the per-message secret number is a function"),
  ("Device use", "Deterministic ECDSA may be desirable for devices that do not have a good source of quality")])
add(160, "classical-signatures/fips186-5", "first-person",
 "We still sign with DSA at work. Did FIPS 186-5 change anything for us?",
 "Yes. FIPS 186-5 no longer approves DSA for generating digital signatures; DSA may only be used to verify signatures created before the standard's implementation date, and its specification now lives only in FIPS 186-4. The revision also removed X9.31 RSA signatures, added its own ECDSA specification and a deterministic ECDSA, added EdDSA and its prehash version, allowed larger RSA moduli, and moved many elliptic curve details to SP 800-186, where binary curves are deprecated.",
 ["Says DSA is no longer approved for signature generation", "Says DSA may still verify older signatures", "Mentions EdDSA being added or deterministic ECDSA", "Mentions another change (X9.31 removal, SP 800-186 curves, larger RSA moduli)", "Penalize: saying DSA remains fully approved"],
 [("DSA not approved", "DSA is no longer approved for digital signature generation. DSA may be used to verify"),
  ("EdDSA added", "A new deterministic signature algorithm, EdDSA, is included, as is the prehash version.")])
add(206, "pq-transition/ir8547", "imperative",
 "Summarize what NIST's post-quantum transition report says it is trying to do.",
 "NIST IR 8547 (initial public draft, November 2024) is described as the first step of a broader strategy to guide the move to post-quantum cryptography. The transition means adopting new PQC algorithms and carefully deprecating, allowing controlled legacy use of, and eventually removing quantum-vulnerable algorithms that are widespread today. NIST notes the change is unprecedented in scale, will take substantial effort, needs public-private engagement, and aims for a clear roadmap and realistic timeline with minimal disruption to critical systems.",
 ["Says it is an initial step of a strategy for the PQC transition", "Mentions adopting PQC and deprecating/removing quantum-vulnerable algorithms", "Mentions the unprecedented scale or substantial effort", "Mentions roadmap / timeline / public-private engagement", "Penalize: presenting the draft as a final mandatory regulation"],
 [("Initial step", "This report serves as the initial step in a broader strategy to manage and guide the transition to"),
  ("Unprecedented scale", "transition to PQC is unprecedented in scale, it benefits from a level of awareness and")])
add(213, "pq-transition/ir8547", "direct",
 "By what year is the US government aiming to finish moving to post-quantum crypto?",
 "2035. National Security Memorandum 10 (NSM-10) sets 2035 as the main target for completing the migration of Federal systems to post-quantum cryptography, with the goal of mitigating as much quantum risk as feasible by then, as quoted in NIST IR 8547 (draft). NIST notes timelines may differ: systems with long-term confidentiality needs may need to move earlier, while legacy or lower-risk systems may move more slowly, but the overall goal is widespread PQC adoption by 2035.",
 ["Gives 2035 as the target", "Attributes it to National Security Memorandum 10 (NSM-10)", "Notes some systems may need earlier or later transitions", "Mentions the threat of a cryptographically relevant quantum computer", "Penalize: giving a different target year such as 2030 as the completion date"],
 [("NSM-10 2035", "National Security Memorandum 10 (NSM-10) establishes the year 2035 as the primary target"),
  ("Varying timelines", "However, it is important to recognize that migration timelines may")])
add(214, "pq-transition/ir8547", "first-person",
 "Our servers still use RSA and ECDSA signatures. When does NIST plan to stop allowing them?",
 "In the draft NIST IR 8547 timeline, RSA and ECDSA at 112 bits of security strength are deprecated after 2030 and disallowed after 2035; at 128 bits or more they are disallowed after 2035. EdDSA follows the same 2035 cut-off. Deprecated means usable but with risk the data owner must weigh; disallowed means no longer allowed. The listed replacements are ML-DSA (FIPS 204), SLH-DSA (FIPS 205) and the stateful LMS/HSS and XMSS schemes from SP 800-208.",
 ["Says 112-bit RSA/ECDSA are deprecated after 2030", "Says they are disallowed after 2035", "Explains deprecated vs disallowed", "Names post-quantum replacements (ML-DSA, SLH-DSA, LMS/XMSS)", "Penalize: claiming RSA is quantum resistant"],
 [("Deprecated 2030", "Deprecated after 2030"),
  ("Disallowed meaning", "- Disallowed means that the algorithm, key length/strength, parameter set, or scheme is")])
add(211, "pq-transition/use-cases", "imperative",
 "Explain why encrypted email and VPN traffic need post-quantum protection sooner than logins do.",
 "Encrypted data can be recorded now and decrypted later once a quantum computer exists, the 'harvest now, decrypt later' threat. NIST IR 8547 (draft) notes that network protocols like TLS and VPNs, and S/MIME email encryption, provide confidentiality, so their key establishment must be migrated with this threat in mind. Authentication is different: it only needs the algorithms to be secure at the moment it happens, so quantum-vulnerable authentication can remain until capable quantum computers appear, then must be disabled.",
 ["Explains the harvest-now-decrypt-later threat", "Applies it to TLS/VPN key establishment and/or email encryption", "Says authentication only needs to be secure at the time it is performed", "Says vulnerable authentication must be disabled once quantum computers arrive", "Penalize: saying authentication must be migrated before encryption"],
 [("Authentication differs", "Unlike with encryption, where there is a threat of “harvest now, decrypt later,” an"),
  ("Email encryption exposed", "applications providing data confidentiality, email encryption is subject to “harvest now, decrypt")])
add(215, "pq-transition/applications", "direct",
 "Could some systems like TLS have to drop quantum-vulnerable crypto before 2035?",
 "Yes. NIST IR 8547 (draft) says NIST's core algorithm standards may keep specifying quantum-vulnerable techniques until 2035, but application-specific standards and guidelines may set earlier transitions. NIST expects to prioritize moving to quantum-resistant key establishment to counter 'harvest now, decrypt later', especially in interactive protocols like TLS and IKE. Examples of such application documents include FIPS 201-3 for PIV credentials and SP 800-52 Revision 2 for TLS.",
 ["Says application-specific guidance may require earlier transitions than 2035", "Mentions prioritizing quantum-resistant key establishment", "Names TLS and/or IKE as priority protocols", "Gives an example document (FIPS 201-3 or SP 800-52 Rev. 2)", "Penalize: saying nothing can change before 2035"],
 [("Earlier transitions", "guidelines may specify earlier transitions for certain cryptographic algorithms, techniques, and"),
  ("TLS and IKE", "particularly in interactive protocols like TLS and IKE.")])
add(295, "glossary/hash", "imperative",
 "Define a cryptographic hash function the way NIST does and list the properties it should have.",
 "NIST defines a cryptographic hash function as a function that maps a bit string of arbitrary (though bounded) length to a fixed-length bit string. Approved hash functions, such as those in FIPS 180 and FIPS 202, are expected to have collision resistance, preimage resistance and second preimage resistance; some definitions describe them as one-way and collision-resistant. SP 800-152 adds that the hash value depends on the entire message and acts like a fingerprint of the file.",
 ["Says it maps arbitrary-length input to a fixed-length output", "Lists collision resistance", "Lists preimage and second preimage resistance (or one-way)", "Mentions approved functions in FIPS 180 / FIPS 202 or the fingerprint idea", "Penalize: describing a hash function as reversible encryption"],
 [("Fingerprint", "A hash function can be considered to be a fingerprint of the file or message."),
  ("Three properties", "3. Second preimage resistance (see Second preimage resistance).")])
add(452, "glossary/keys", "first-person",
 "My bank app mentions a 'secret key'. Does secret mean it's classified, and is it the same as a symmetric key?",
 "In NIST terms a secret key is a cryptographic key used with a secret-key, that is symmetric, algorithm, uniquely associated with one or more entities and not made public. NIST says a symmetric key is often called a secret key. The word 'secret' does not imply a government classification level; it means the key must be protected from disclosure, and FIPS 201 adds protection from substitution as well.",
 ["Says a secret key is used with a symmetric (secret-key) algorithm", "Says secret key and symmetric key are used as synonyms", "Says 'secret' does not imply a classification level", "Says the key must be protected from disclosure and is not made public", "Penalize: describing a secret key as the private half of a public-key pair only"],
 [("Not a classification", "The use of the term “secret” in this context does not imply a classification level, but rather implies the need to protect the key from disclosure."),
  ("Synonym", "A symmetric key is often called a secret key.")])
json.dump(I, open(__file__.replace(".py", ".json"), "w"))
with open(__file__.replace("draft-boar-nist-crypto.py", "draft-boar-nist-crypto.jsonl"), "w") as f:
    for r in I: f.write(json.dumps(r, ensure_ascii=False) + "\n")
print(len(I))
