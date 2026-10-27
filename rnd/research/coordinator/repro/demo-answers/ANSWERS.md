# Desktop cut 7 demo answers (Mac mini M4, tree be-0cfd4a77-cut7, claim settings, seed 42; flip items also seed 43)

Engine: cut 7 (patch sha 0fba26b8...), Qwen3-4B-Instruct-2507 Q4_K_M, runner be-repo adapter 7a0282ae, BOAR_RUNNER_PROFILE=ship, detector v3b on :8094, kit crypto + wikivoyage-en, settings quickFirst=true alwaysComplete=false, device android 12 GB (claim-config-cut7.json). 8/8 and 2/2 traces valid, 0 errors.

## vit-hlt-001
- query: My friend just got stung by a jellyfish while swimming in Thailand. Should I pour vinegar or fresh water on it?
- route/tier: fast/chat (success); reason codes of note: instant:preview,detector:fire,instant:off-health,grounding:fa-card-jellyfish
- sources: kept 0 [none], raw 4, shown 0, cited 0
- timing (desktop mini): ttft 5.7 s, total 5.7 s
- answer (seed 42):

  > Jellyfish sting: get out of the water. Don't touch the tentacles with bare hands; remove any with tweezers or the edge of a card. Rinse the sting with seawater, not fresh water. In tropical box-jellyfish areas, pour vinegar on the sting and go to hospital. For pain, soak the area in very warm water, as hot as they can bear without burning, for at least 30 minutes. Don't pee on it and don't put ice on it. Call emergency services if they have trouble breathing, chest pain, a seizure, severe swelling, vomiting, or feel faint.
  > 
  > Source: NHS, Jellyfish and other sea creature stings; healthdirect (AU), Jellyfish stings. Contains public sector information licensed under the Open Government Licence v3.0.
  > 
  > Emergency — Thailand: police 191, ambulance 1669, fire 199, tourist police 1155 (English-speaking).

- seed 43: route/tier fast/chat (success); sources: kept 0 [none], raw 4, shown 0, cited 0; ttft 5.3 s, total 5.3 s
- seed 43 answer:

  > Jellyfish sting: get out of the water. Don't touch the tentacles with bare hands; remove any with tweezers or the edge of a card. Rinse the sting with seawater, not fresh water. In tropical box-jellyfish areas, pour vinegar on the sting and go to hospital. For pain, soak the area in very warm water, as hot as they can bear without burning, for at least 30 minutes. Don't pee on it and don't put ice on it. Call emergency services if they have trouble breathing, chest pain, a seizure, severe swelling, vomiting, or feel faint.
  > 
  > Source: NHS, Jellyfish and other sea creature stings; healthdirect (AU), Jellyfish stings. Contains public sector information licensed under the Open Government Licence v3.0.
  > 
  > Emergency — Thailand: police 191, ambulance 1669, fire 199, tourist police 1155 (English-speaking).

- **verdict seed 42 vs 43: same** (tier+task equal: True; reason codes equal: True; text equal: True)

## lan-rsn-007
- query: In which year was the Berlin Wall built, and in which year did it come down?
- route/tier: instant/(no task) (success); reason codes of note: none
- sources: kept 0 [none], raw 0, shown 0, cited 0
- timing (desktop mini): ttft 0.1 s, total 0.1 s
- answer (seed 42):

  > Berlin Wall (barrier constructed by the German Democratic Republic, enclosing West Berlin (1961–1989), East Germany): built/founded 13 August 1961; it ended (came down / was dissolved) on 9 November 1989.
  > 
  > Source: Wikidata (CC0), offline table as of 2026-10-06.

## lan-cmp-001
- query: Does Brazil have more people than Russia?
- route/tier: instant/(no task) (success); reason codes of note: none
- sources: kept 0 [none], raw 0, shown 0, cited 0
- timing (desktop mini): ttft 0.0 s, total 0.0 s
- answer (seed 42):

  > Yes. Brazil has more people than Russia: Brazil 214.2 million (2026) vs Russia 146.1 million (2025).
  > 
  > Source: Wikidata (CC0), offline table as of 2026-10-06; figure dated 2026.

## vit-sci-003
- query: My phone generates 10 tokens per second and processes the prompt at 30 tokens per second. With 1,300 tokens of sources and a 400-token answer, how long until the answer is finished?
- route/tier: instant/(no task) (success); reason codes of note: detector:fire
- sources: kept 0 [none], raw 0, shown 0, cited 0
- timing (desktop mini): ttft 0.0 s, total 0.0 s
- answer (seed 42):

  > About 83.3 seconds (1 min 23 s) in total: 1,300 tokens ÷ 30 tokens per second ≈ 43.3 seconds, plus 400 tokens ÷ 10 tokens per second = 40 seconds. Computed from the numbers in your question.

- seed 43: route/tier instant/(no task) (success); sources: kept 0 [none], raw 0, shown 0, cited 0; ttft 0.0 s, total 0.1 s
- seed 43 answer:

  > About 83.3 seconds (1 min 23 s) in total: 1,300 tokens ÷ 30 tokens per second ≈ 43.3 seconds, plus 400 tokens ÷ 10 tokens per second = 40 seconds. Computed from the numbers in your question.

- **verdict seed 42 vs 43: same** (tier+task equal: True; reason codes equal: True; text equal: True)

## vit-cry-004
- query: What is PeerDAS, and how can a node check that blob data is available without downloading all of it?
- route/tier: fast/chat (success); reason codes of note: instant:preview,instant:off-topic
- sources: kept 4 [Ethereum EIPs/ERCs: EIP-7594: PeerDAS - Peer Data Availability Sampling; ethereum.org: PeerDAS; ethereum.org: PeerDAS; ethereum.org: PeerDAS], raw 4, shown 4, cited 2
- timing (desktop mini): ttft 12.6 s, total 15.8 s
- answer (seed 42):

  > PeerDAS (Peer Data Availability Sampling) is a protocol that enables nodes to sample only a subset of blob data during downloads, ensuring data availability without full retrieval [1]. A node checks blob data availability by verifying that a sufficient number of sampled pieces—distributed via gossip and discovery—can collectively reconstruct the original blob through erasure coding, even if some pieces are missing [3].

## lan-exp-007
- query: Describe Greenland: who governs it, its capital, roughly how many people live there, and how much of it is covered by ice.
- route/tier: fast/chat (success); reason codes of note: instant:preview
- sources: kept 2 [Wikivoyage: Greenland; Wikivoyage: Greenland], raw 4, shown 2, cited 0
- timing (desktop mini): ttft 12.0 s, total 15.0 s
- answer (seed 42):

  > Greenland is governed by the Government of Greenland, with the Danish government holding ultimate authority as it is an autonomous territory of the Kingdom of Denmark. The capital is Nuuk, and the population is approximately 56,000 people. About 80% of Greenland's surface is covered by ice, primarily the vast interior ice sheet.

## vit-trv-004
- query: How far is it to walk from Paris to Rome and back?
- route/tier: instant/(no task) (success); reason codes of note: none
- sources: kept 0 [none], raw 0, shown 0, cited 0
- timing (desktop mini): ttft 0.0 s, total 0.0 s
- answer (seed 42):

  > Roughly 2,900 km there and back (an estimate). Paris and Rome are about 1,107 km (687 miles) apart in a straight line. Walking routes are usually about 30% longer than that, so plan on roughly 1,440 km (890 miles) each way, about 2,900 km there and back. That is about 58 days each way at a steady 25 km a day, or around 3.8 months for the round trip without rest days (about 288 hours of walking each way at 5 km/h). This is an estimate from the cities' coordinates, not a mapped route; the real route can differ.

## lan-rsn-006
- query: How long did the Hundred Years' War actually last, and which two kingdoms fought it?
- route/tier: fast/research (success); reason codes of note: instant:preview,instant:off-topic
- sources: kept 2 [Wikivoyage: United Kingdom; Wikivoyage: Kingdom of France], raw 4, shown 2, cited 1
- timing (desktop mini): ttft 6.2 s, total 8.0 s
- answer (seed 42):

  > The Hundred Years' War lasted from 1337 to 1453, spanning 116 years. It was fought between the Kingdom of England and the Kingdom of France. [2]
