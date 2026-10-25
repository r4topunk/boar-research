# Data contract for the BOAR publication

TL;DR: six versioned data files (plus `status.json`, the living-preprint status) are the single source for every number, event, decision, experiment and term on the site and in the LLM layer. The UI and the `llm/` files are generated from them and never hard-code a number. Validate before every build:

```bash
node publication/scripts/validate-data.mjs     # exit 0 = contract holds
```

| file | rows (2026-10-24 20:34; 2026-10-18 in brackets) | what it holds | id pattern |
|---|---|---|---|
| `facts.json` | 2,191 (1,292) | every verified claim: numbers, events, decisions and null results as atomic facts | `F-001` … |
| `timeline.json` | 465 (285) | dated events, deduplicated across slices | `E-001` … |
| `decisions.json` (+ `decisions.md`) | 201 (118) | ADR-style decision log | `D-001` … |
| `experiments.json` | 401 (193) | experiment catalogue ("arms") with verdicts; feeds the graveyard visual | `X-001` … |
| `glossary.json` (+ `glossary.md`) | 97 (68) | internal term → plain + technical definition | `G-<slug>` |
| `status.json` | 8 open fronts (2026-10-25 03:30) | living-preprint status: `as_of`, research state, headline fact ids, open fronts, changelog; drives the status banner | `OF-<n>` |
| `SCHEMA.md` | — | this contract | — |

Every file shares one envelope:

```ts
const Envelope = <T extends z.ZodTypeAny>(key: string, row: T) => z.object({
  schema: z.literal(`boar-publication/${key}`),
  schema_version: z.string().regex(/^\d+\.\d+\.\d+$/),   // semver; bump MAJOR on any breaking field change
  generated: z.string().regex(/^\d{4}-\d{2}-\d{2}$/),
  license: z.string(),                                    // "CC BY 4.0 (text and data)"
  count: z.number().int(),                                // must equal rows.length
  notes: z.array(z.string()).optional(),
  [key]: z.array(row),
});
```

## Shared enums

```ts
const ChapterId = z.enum([                 // aligned with content/narrative.md (18 chapters; display order = facts.json `chapters[].n`)
  'question', 'ruler', 'floor-trap', 'builds', 'walls', 'deep-tier', 'phone',
  'agent-lab', 'packs', 'measurer', 'honest-number', 'handoff', 'reproduce',
  // added 2026-10-24 for 2026-10-18..10-24; order and titles fixed by the editorial step 2026-10-24 (ch 11-15)
  'small-engine', 'new-ruler', 'delivery', 'submission', 'closure']);
const Layer = z.enum(['curious', 'tech', 'ai']);
const IsoDate = z.string().regex(/^\d{4}-\d{2}-\d{2}$/);
const Time = z.string().regex(/^\d{2}:(\d{2}|\dx)$/);              // "03:4x" = 03:40–03:49 (source gives 10-minute precision)
const PublicSource = z.string().refine((s) =>               // "; "-separated list of <repo>:<path>[:<lines>|#R<n>]
  s.split('; ').every((p) => /^(boar-research|boar-bench):\S+$/.test(p)));
```


## facts.json

```ts
const Fact = z.object({
  id: z.string().regex(/^F-\d{3,}$/),
  kind: z.enum(['fact', 'event', 'decision', 'null-result']),
  claim: z.string().min(1),                       // one sentence, English, sanitized
  value: z.string().nullable(),                   // the number(s) as printed, with units
  ci: z.string().nullable(),                      // 95 % CI or CI method; null when the source has none
  n: z.string().nullable(),                       // items judged (string: sources mix "51", "57 (R450 contexts)")
  seeds: z.string().nullable(),
  set: z.string().nullable(),                     // v0.1 | v0.2 | V-para | 180 pack self-tests | …
  set_status: z.string().nullable(),              // public dev | dev | dev-style | held-out at run time | burnt → dev
  judge: z.string().nullable(),                   // judge family: Claude Opus | Claude Haiku L1 | cross-family (post-hoc) | none
  date: IsoDate.nullable(),
  date_text: z.string().optional(),               // original wording when it carries a range or a time
  source_public: PublicSource.nullable(),
  caveat: z.string().nullable(),                  // includes verifier notes ("Verification note: …")
  verification: z.enum(['CANONICAL (two-source check in verify pass)', 'CONFIRMED', 'CORRECTED', 'OVERCLAIM', 'CONFLICT']),
  visibility: Visibility,
  layer_tags: z.array(Layer).min(1),
  chapter: ChapterId,
  aliases: z.array(z.string()),                   // verify-layer ids (e.g. "F-results-18", "canon:k-vpara") → reconciles content/*.md citations
  superseded_by: z.array(z.string().regex(/^F-\d{3,}$/)).optional(),   // added 2026-10-24: later rows that changed this row's standing
  superseded_note: z.string().optional(),         // one sentence: what changed (the row itself is never edited)
});
```

- **Supersession (2026-10-24).** When a later result changes an older standing claim, the new result gets new rows and the old row gains `superseded_by` (+ `superseded_note`); its other fields stay as they were. The validator checks that every `superseded_by` id exists. Decisions keep using `status` / `superseded_by` as before.
- [sentence withheld in this file; see https://r4topunk.github.io/boar-research/data/ or the chapter record] The `caveat` names the family for (2) and (3). Never plot two families on one axis.

- `F-001` … `F-046` are the **canonical** facts: the load-bearing numbers, each checked against two sources by the verify pass, plus the resolutions of the verifiers' CONFLICT rows. Visuals bind to these first.
- `OVERCLAIM` rows keep their number but the `caveat` carries the honest framing; render the caveat.
- `CONFLICT` rows (4) are kept only for traceability; the canonical row that resolves each one is the one to render.

## timeline.json

```ts
const Event = z.object({
  id: z.string().regex(/^E-\d{3,}$/),
  date: IsoDate.nullable(), time: Time.nullable(),
  title: z.string(),
  type: z.enum(['start', 'pivot', 'decision', 'build', 'experiment', 'result', 'incident', 'release', 'milestone']),
  significance: z.number().int().min(1).max(3),   // 3 = chapter-level turning point
  fact_ids: z.array(z.string().regex(/^F-\d+$/)).min(1),
  decision_ids: z.array(z.string().regex(/^D-\d+$/)),
  chapter: ChapterId, visibility: Visibility,
  aliases: z.array(z.string()),                   // verify-layer event ids (E-chron-*, T-*)
});
```

Duplicates across the six slice notes were merged (same day + similar title or shared arm code); every merged row keeps all its `fact_ids`.

## decisions.json

```ts
const Decision = z.object({
  id: z.string().regex(/^D-\d{3,}$/),
  date: IsoDate.nullable(), time: Time.nullable(),
  title: z.string().max(160),
  context: z.string().nullable(),                 // the same-day event the decision answered
  decision: z.string(),
  alternatives: z.array(z.string()).nullable(),
  rationale: z.string().nullable(),
  consequence: z.string().nullable(),             // what happened next
  reversible: z.string().nullable(),              // as judged at the time
  status: z.enum(['kept', 'superseded', 'reversed']),
  status_label: z.string(),                       // "kept" | "superseded" | "superseded by D-036" | "reversed"
  status_note: z.string().nullable(),
  superseded_by: z.string().regex(/^D-\d+$/).nullable(),
  verification_note: z.string().nullable(),
  fact_ids: z.array(z.string().regex(/^F-\d+$/)).min(1),
  chapter: ChapterId, visibility: Visibility,
  aliases: z.array(z.string()),                   // verify-layer decision ids (D-method-09, D-chron-late-08, …)
});
```

## experiments.json

```ts
const Experiment = z.object({
  id: z.string().regex(/^X-\d{3,}$/),
  code: z.string(),                               // arm code as in the research record (DT512, HEADPASS-X2b, …)
  name: z.string(), family: z.string().nullable(),
  question: z.string().nullable(),
  hypothesis: z.string().nullable(),              // null: lives in the criterion file, not extracted yet
  preregistered: z.object({ status: z.string(), where_public: z.string().nullable() }),
  set: z.string().nullable(), judge: z.string().nullable(), n: z.string().nullable(), seeds: z.string().nullable(),
  result: z.string().nullable(),
  result_verified: z.boolean(),                   // false → render as "as recorded (ledger audit 2026-10-13)"
  effect: z.string().nullable(),                  // only from verified facts
  ci: z.string().nullable(),
  mde: z.string().nullable(),
  verdict: z.enum(['adopted', 'closed', 'not-detected', 'parity', 'measurement', 'tooling', 'open']),
  verdict_detail: z.string().nullable(),
  reopen_if: z.string().nullable(),
  closed_row: z.string().regex(/^R\d+$/).nullable(),        // row in the closed registry
  registry_public: z.string().nullable(),                   // boar-research:reports/CLOSED.md:<line> for R1–R76
  date: IsoDate.nullable(),
  fact_ids: z.array(z.string().regex(/^F-\d+$/)),
  chapter: ChapterId, source: z.string(),
});
```

`not-detected` is an addition to the brief's verdict list on purpose: an under-powered null (CI straddles 0 below the MDE) is not a closure. Rows R31, R83, R84, R85 and R97 were relabelled this way after the 2026-10-16 outside critique.

## glossary.json

```ts
const Term = z.object({
  id: z.string().regex(/^G-[a-z0-9-]+$/),
  term: z.string(), aliases: z.array(z.string()),
  layer: Layer,                                   // lowest layer that needs the term
  chapter: ChapterId,                             // chapter of first use
  plain: z.string(),                              // ≤ 2 sentences, no jargon
  technical: z.string(),                          // precise, with numbers where they define the term
  fact_ids: z.array(z.string().regex(/^F-\d+$/)),
});
```

## status.json (living preprint)

The research is open until its planned close; this file says what the current standing is and what could still move it. It has its own envelope (one object, no row array):

```ts
const OpenFront = z.object({
  id: z.string().regex(/^OF-\d+$/),
  title: z.string(),
  question: z.string(),                           // the open question, one sentence
  why_it_matters: z.string(),
  what_would_change: z.string(),                  // which claim/chapter moves if it lands, in BOTH directions
  related_fact_ids: z.array(z.string().regex(/^F-\d+$/)),   // must exist in facts.json and be public
  owner: z.string(),                              // "author"
  state: z.enum(['pending', 'running', 'landed', 'dropped']),
  note: z.string().nullable(),
});
const Status = z.object({
  schema: z.literal('boar-publication/status'),
  schema_version: z.string().regex(/^\d+\.\d+\.\d+$/),
  as_of: IsoDate,                                 // every headline on the site prints "as of <as_of>"
  as_of_time: z.string().regex(/^\d{2}:\d{2}$/).optional(),   // added 1.2.0 (2026-10-24 evening): clock time (GMT-3) of as_of; banner prints "as of <as_of> <as_of_time>"
  research_state: z.enum(['open', 'closed']),
  research_closed_on: IsoDate.optional(),         // added 1.1.0 (2026-10-24): the day the author closed the research lines
  planned_close: IsoDate.nullable(),
  version: z.string(),                            // "0.x-preprint" while open; "1.0" (+ DOI) at closure
  license: z.string(),
  banner: z.string(),                             // the status banner text; must contain as_of
  standing: z.array(z.string().regex(/^F-\d+$/)),   // fact ids of the headline numbers as of as_of (public)
  open_fronts: z.array(OpenFront),
  changelog: z.array(z.object({ date: IsoDate, version: z.string(), change: z.string() })),
  notes: z.array(z.string()).optional(),
  headline: z.object({                            // added 1.3.0 (2026-10-25, author decision 2): the headline number's slot
    label: z.string(), front: z.string().regex(/^OF-\d+$/),
    state: z.enum(['pending', 'landed']),
    fact_ids: z.array(z.string().regex(/^F-\d+$/)),   // empty while pending; public DEVICE-FINAL rows once landed
    metric: z.string(), order: z.array(z.string()),   // what is printed first (win-rate), then U-total per family, minimum, verdict
    template: z.string(),                         // {{as_of}}, {{M1.*}}, {{M5.*}} placeholders, filled by the build from fact rows only
    placeholder: z.string(),                      // rendered while state = pending
    note: z.string().nullable(),
  }).optional(),
  history: z.record(z.union([z.string(), z.array(z.string().regex(/^F-\d+$/))])).optional(),   // added 1.3.0: earlier readings (old_scale, desktop_ruler), never pooled with the headline; ids must be public
});
```

- Pass/fail criteria for the runs behind an open front are frozen (sha256) in the research repository before the run; `status.json` only reports state and never defines a criterion.
- When a front lands: add the new result as new fact rows (never edit the old ones), move its `state`, update `standing`, bump `as_of` and `version`, add a `changelog` row, rerun the validator (PLAN.md PT-13).

## Validation rules (enforced by `scripts/validate-data.mjs`)

1. Every file parses, matches its envelope, and `count === rows.length`.
2. Ids are unique per file and match their pattern.
3. Referential integrity: every `fact_ids[]` in timeline, decisions, experiments and glossary exists in `facts.json`; every `decision_ids[]` and `superseded_by` exists in `decisions.json`.
4. Every event and every decision has at least one fact (so every row on the site is sourced).
5. `status = superseded` with a known successor sets `superseded_by`; `reversed` carries a `status_note`.
6. Hygiene, over every file in `data/` and `llm/`: no absolute home paths, hostnames, handles, emails, wallet addresses, key-like strings, internal agent names, competitor names or held-out item ids. (The validator holds the pattern list.)
7. Numbers discipline (lint, warning level): a fact whose `value` contains a ratio (0.xxx) must carry `set` and `judge`, or a `caveat`; a canonical fact must carry both raw and floor-adjusted values when both exist.
8. `status.json` (when present): envelope fields, `as_of` inside `banner`, `research_state` and `state` enums, unique `OF-` ids, and every id in `standing`, `related_fact_ids`, `headline.fact_ids` and `history.*` exists in `facts.json` with `visibility = public`; `headline` (1.3.0) needs `template` and `placeholder`, and `state = landed` needs fact ids.

## Id stability


## Rendering rules the UI must honour

- A ratio renders only with its scale (raw / floor-adjusted), set + `set_status`, `judge`, `n`, `seeds` and `ci` (PLAN.md PD-03). Missing field → the component shows "UNKNOWN", never a blank.
- Dev and dev-style numbers carry the "development data" badge.
- Health content carries "AI-reviewed, not clinically reviewed. Nothing here is medical advice."
- Every rendered number carries `data-fact-id="F-…"` so a reader's AI can cite it.

## How the files are built

