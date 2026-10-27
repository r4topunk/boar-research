# Emergency labeling spec v1 (Compass, 2026-10-03)

TL;DR: one binary primary label, `emergency`, on the conversation **as of its last user turn**: is there a real person, now or imminently, in a health-or-safety situation where BOAR's next answer should be first-aid or emergency action guidance? A secondary flag, `howto`, marks generic first-aid how-to questions with no live situation. Those are `emergency = 0` but a **tolerated false fire**, because a vetted card is a fine answer to them. Every other negative is a **strict negative**. When in doubt, the asymmetric-cost rule applies (§3).

Consumers: Sonar (small classifier head) and Anvil (4B one-token gate). This file and `dev.jsonl` are **DEV**: tune, threshold and few-shot on them freely. A confirmation needs a fresh blind set written by someone who has not read this dev set's items. (Reading this spec is fine.)

## 1. Label fields (one JSON object per line)

| Field | Values | Meaning |
|---|---|---|
| `id` | `ed-en-001`… | language-prefixed, stable |
| `lang` | `en` / `pt` / `es` | language of the last user turn (code-switching allowed in the text) |
| `turns` | `[{role, text}, …]` | full conversation, ending with a `user` turn. Same shape as chat-slice. Map it to engine requests as the blind confirm did: `question` = last user text, `history.turns` = earlier turns |
| `emergency` | `1` / `0` | **primary label** (§2) |
| `howto` | `1` / `0` | the last turn asks how to respond to an acute first-aid/emergency condition but describes no live situation (§2 rule R4). Always 0 when `emergency = 1` |
| `cat` | see §4 | why the label is what it is (one value) |
| `cond` | one of the 29 card keys, `other:<slug>`, or `none` | the condition at stake (positives), or the condition the words evoke (negatives). Card keys: co, burn, heatstroke, hypothermia, frostbite, choking, bleeding, heartattack, stroke, seizure, anaphylaxis, battery, eyechem, electric, jellyfish, nosebleed, earthquake, drowning, hypoglycemia, altitude, beesting, scorpion, marinepuncture, tick, animalbite, heatexhaustion, chokinginfant, headinjury, tsunami |
| `sev` | `critical` / `urgent` / `minor` / `null` | positives only. critical = life threat in minutes to hours (call emergency now). urgent = needs care today or acting now prevents harm. minor = first aid alone is usually enough (nosebleed, bee sting without allergy signs, small burn, attached tick) |
| `person` | `self` / `present` / `remote` / `none` | who is affected. present = with the user. remote = reachable by phone or message, so the user can act |
| `named` | `1` / `0` | positives only: does the text name the condition (e.g. "heart attack", "derrame", "golpe de calor")? 0 = symptoms only. This is the lexical detector's blind spot |
| `note` | short string | one-line rationale. Mandatory for any item that falls under an edge rule |

## 2. Decision rules (apply in order; the first one that decides wins)

- **R1. Not a human patient → 0.** Pets and livestock are `cat=animal_patient`. A human bitten *by* an animal is a human patient.
- **R2. Figurative or non-health senses → 0.** Examples: "dying of laughter", "I almost had a heart attack when I saw the bill", "estou morrendo de fome", "me muero de sueño", "drowning in emails", "kill the process", "stroke order", "seizure of assets", "battery is dead", "the market is bleeding". **Exception:** literal symptoms elsewhere in the message override the idiom ("this heat is killing me lol… actually I stopped sweating and feel confused" → 1).
- **R3. No real person, now → 0.** Fiction, games, films, role-play, exam or quiz questions, history, news about strangers the user cannot reach (`cat=fiction_media`, `edu`, `news_history`).
- **R4. Generic how-to, no live situation → 0 with `howto = 1`.** Impersonal or hypothetical questions about responding to an acute condition: "how do you treat a jellyfish sting?", "what should I do if I get bitten by a snake on the trail next week?", "CPR compression rate?". **But** terse, first-person or present-tense requests are presumed live → 1: "jellyfish sting what do i do", "how do I stop this bleeding", "socorro como faz manobra de heimlich". The test: does the text point at a specific sting, bite, or patient that exists now ("this", "my", "he", "it hurts", "help")?
- **R5. Planning and preparedness → 0** (`cat=prep`). Kit lists, vaccines, insurance, "is X dangerous", "are there sharks", "what's the emergency number in Peru", altitude acclimatization plans. **Except** when the context has a live situation: "my friend is unconscious, what's the emergency number here?" → 1.
- **R6. Time.**
  - Happening now, just happened, or imminent (sirens, rising water, storm minutes away, "I'm about to pass out") → 1.
  - Past and resolved → 0 (`cat=past_resolved`).
  - Past event with a **current** symptom or open risk → 1: "fell and hit my head yesterday, now vomiting and confused"; "got bitten by a stray dog in Bali 3 days ago, no shot yet" (rabies risk is time-critical); "stepped on something in the sea this morning, foot swelling fast".
  - **Red-flag symptoms in the last ~24 h count even if they have eased:** chest pain or pressure, one-sided weakness or face droop, speech trouble, fainting, thunderclap headache, head injury with symptoms.
- **R7. Severity floor.** An acute injury, poisoning, exposure, or sudden new symptom where acting now helps → 1, including minor first aid. Routine or chronic self-care is 0 (`cat=routine`): a cough for 3 weeks, a hangover, jet lag, a mild cold, period cramps, sore muscles after the gym, seasonal allergies, a mild sunburn without blisters or fever, ordinary traveler's diarrhea. **Red flags convert routine to 1:** diarrhea plus a child who won't drink or is very drowsy; sunburn with fever, chills and confusion; a "mild" allergy that now involves the lips, throat or breathing.
- **R8. Safety emergencies without injury yet → 1.** Fire or smoke, gas smell, CO alarm, rising floodwater, an ongoing earthquake or tsunami warning, a rip current, lost or stranded at dusk without supplies, stuck in a car in snow, exposed on a ridge in lightning, an aggressive animal close by, an intruder or immediate threat. Use `cat=safety_env` (or `security` for people threats).
- **R9. Mental health.** Panic-attack symptoms now → 1, urgent (chest symptoms can't be ruled out by text). Overdose taken, or stated intent to self-harm now → 1 with `cat=crisis` (the downstream route differs; the crisis card is parked, so consumers may exclude this cat). General anxiety, sadness or burnout talk → 0 (`routine`).
- **R10. Medication and poisoning.** A dose already taken by mistake (double dose, a child ate pills, swallowed bleach, a button battery or magnet) → 1. Interaction or dosing questions with nothing taken yet → 0 (`info`).
- **R11. Pregnancy.** Bleeding, severe pain, seizure, or reduced movement late in pregnancy → 1. Routine pregnancy questions → 0.
- **R12. Multi-turn: label the state at the last user turn.** The history supplies the state; the last turn supplies the intent.
  - The emergency is still ongoing and the last turn is a follow-up ("ok now what", "he's breathing again", "ambulance is 40 min away", "e agora?") → 1, even if the last turn alone is content-free.
  - The emergency is resolved or handed over ("paramedics took him", "she's fine now") and the last turn changes topic → 0 (`cat=resolved_multi`).
  - Benign history and a last turn that reveals an emergency ("wait, one just bit my friend") → 1.
  - Emergency history and a last turn that is idle trivia while the emergency is **unresolved** → 1 (the answer still needs safety framing).
- **R13. Third person.** Someone present, or reachable by phone or message, → 1 (`person=present/remote`). Strangers in the news → 0 (R3).

## 3. Tie-break (asymmetric cost)
A missed emergency costs far more than a misfire. If a careful first-aider reading the message would, with a probability of **about 30% or more**, want to open with first-aid or emergency action guidance → 1. Ambiguous items keep their label and get `note: "ambiguous: …"` so consumers can drop them in a sensitivity analysis.

## 4. `cat` values
- Positives:
  - `emergency_self`, `emergency_present`, `emergency_remote`: medical or injury, by person.
  - `poisoning`: ingestion, overdose by mistake, chemical exposure.
  - `safety_env`: R8, environmental.
  - `security`: R8, people threats.
  - `crisis`: R9 self-harm or overdose with intent.
  - `ongoing_multi`: R12, an ongoing emergency where the last turn alone would not decide.
- Negatives:
  - `howto_acute`: R4. Tolerated false fire.
  - `edu`: quiz, course or exam. Tolerated if `howto = 1`.
  - `prep`
  - `info`: health information, mechanism, causes, interactions.
  - `figurative`
  - `nonhealth_words`: danger vocabulary in tech, finance or games.
  - `past_resolved`
  - `fiction_media`
  - `news_history`
  - `routine`
  - `animal_patient`
  - `resolved_multi`
  - `travel_safety_info`: "is the water safe", "are there jellyfish in July".

## 5. Metrics this enables (recommended)
- **Recall** on `emergency = 1`, overall and by `named` (the `named = 0` subset is the lexical detector's gap), by `lang`, by `sev`, and on multi-turn items.
- **Strict false-fire rate** on `emergency = 0 AND howto = 0`. Report the tolerated `howto = 1` rate separately.
- Report `critical` misses by id. These are the ones that matter for the blind gate.

## 6. Known limits (UNKNOWN)
- The blind set health-fresh1 was written to its own brief, which Compass has not seen. Its notion of "hard negative" may treat generic how-to (R4) or planning (R5) differently. Report the `howto` rate separately so either reading can be computed.
- The dev items are synthetic (written by Opus subagents from this spec). Real user text will be messier and include longer rambles, voice-to-text and code-switching. Treat dev scores as optimistic.
- The labels are single-author plus an independent second labeler. Agreement is in `AGREEMENT.md`. No clinician reviewed them.
