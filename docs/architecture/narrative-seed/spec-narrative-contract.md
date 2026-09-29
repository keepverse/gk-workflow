# Spec: `narrative-contract`

**Program:** [narrative-seed](../narrative-seed-map.md) · **Module id:** `narrative-contract` · **Map row:** 10 · **Wave:** 2
**Depends on:** `storylet-vocab`, `character-vocab`, `arc-shapes`, `token-grammar` · **Model calls:** none
**Status:** spec phase, 2026-09-19. Map approved by the owner 2026-09-19; no build authorized.
**Runtime consumer:** `npc-story-events`' `storylet-contract` loads storylets with `choices[]`, `roles[]`,
`hosts[]`, `revision`, `provenance`, `arcRef`/`arcLink` and keyed text (`npc-story-events-map.md` row 3);
this contract is shaped to that list.

---

## Objective

Create the `narrative` seedsmith adapter shell and define its four seed schemas — **storylet**,
**character**, **arc**, **spine chapter** — as closed contracts: every field has exactly one ownership
level, a description with a negative clause, and a place in either the planner's work order or a named
model call. Every model-facing enum admits `none`; `additionalProperties` is false; every field is
required. Seeds carry `revision`, a live/tombstone status and `provenance: generated | authored`; every
text field is keyed. The schema audit is extended so no numeric field survives and no text field can hold
a digit.

The model writes identity and text and never a number (map §2 principle 2); the game resolves every seed
at runtime without calling a model (principle 3).

**Done means:** the adapter is registered; `contract --print` and `contract --audit` work for all four
kinds and every call schema; `validate_entry` accepts fixture seeds of each kind and refuses a crafted
violation of every rule below.

---

## Design

### 1. The adapter shell

| Piece | Where |
|---|---|
| `NarrativeAdapter`, implementing the adapter protocol (`kinds`, `dimensions`, `legal_combinations`, `registries`, `channels`) | `gk-forge/tools/seedsmith/seedsmith/adapters/narrative/__init__.py`; protocol at `gk-forge/tools/seedsmith/seedsmith/adapters/base.py:95-100` |
| Registration — one line | `"narrative": NarrativeAdapter` in `gk-forge/tools/seedsmith/seedsmith/adapters/registry.py:12-18` |
| `channels()` returns `[]` | no narrative seed carries a magnitude; the dungeon adapter's reasoning, `gk-forge/tools/seedsmith/seedsmith/adapters/dungeon/__init__.py:56-61` |
| `legal_combinations` | host × storylet kind is legal iff the host `admits` the kind; a climate-neutral host admits only climate `none`; ~~a `sector-type` world host admits only the climates in its `climates` list (Owner ruling 2026-09-20 (round 5), R19; `storylet-vocab` §3.1, §3.9)~~ a world host admits all seven climates (Owner ruling 2026-09-20 (round 6), R20: the site climate is the sector's own; `storylet-vocab` §3.1) |

All narrative knowledge lives in the adapter; the seedsmith core gains no narrative code (seedsmith P5).
The one core touch-point is the registry line above, which is how every adapter is added.

### 2. The corpus tree — `gk-data/packs/fusion/data/seed/narrative/` (new)

```text
gk-data/packs/fusion/data/seed/narrative/
  _registry/      authored registries (Wave 1 modules)
  _exemplars/     authored style references
  _plan/          budget and plans
  _runs/          run ledgers                       (narrative-emit)
  _revisions/     superseded revisions, immutable   (narrative-emit)
  storylets/  characters/  arcs/  spine/            generated seeds, one per file
  authored/storylets/  authored/characters/  authored/arcs/  authored/spine/   hand-written seeds
```

Owner ruling 2026-09-19 (round 3): `quest-vocab` is approved, so a fifth kind, **`quest`** (the narrative
quest anchor), joins this adapter under `quests/` and `authored/quests/`. Its schema and objective registry are
`spec-quest-vocab.md`'s; it uses this section's envelope, §3's common fields and §4's key rule unchanged.

**One seed per file**, inside the standard envelope so the core corpus loader reads it with no
narrative-specific loader (`gk-forge/tools/seedsmith/seedsmith/corpus/model.py:182-199` reads `kind` and
`entries[]` and needs each entry's `id`) — the dungeon adapter had to write its own loader because it
chose bare objects (`gk-forge/tools/seedsmith/seedsmith/adapters/dungeon/completeness.py:6-18`); this contract does
not repeat that.

```json
{
  "schemaVersion": 1,
  "kind": "storylet | character | arc | spine-chapter",
  "_meta": { "contractVersion": 1, "partition": "<cell key>", "batch": "<run id>", "model": "<resolved model id>", "promptVersion": "<version>" },
  "entries": [ { "...": "exactly one seed" } ]
}
```

`_meta.model`, `promptVersion` and `batch` are written by `narrative-emit` on generated files only; the
generated-seed guard keys on them (`gk-core/scripts/guard-generated-seed.py:117-124`). An authored file's `_meta`
carries `contractVersion` and `partition` only, so the guard leaves hand-written seeds alone.

### 3. Fields every seed carries

| Field | Level | Shape | Meaning | Negative clause |
|---|---|---|---|---|
| `id` | PLANNED | `<namespace>.<body>`: namespace one of `storylet`, `character`, `arc`, `spine-chapter`, `quest` (Audit 2026-09-19: the fifth kind, `spec-quest-vocab.md`); body `[a-z0-9-]+` beginning with a letter (so `token-grammar`'s slug always matches `^[a-z]`) | the seed's identity, minted by the planner from the high-water mark | never reused, never a display string |
| `revision` | DERIVED | integer ≥ 1 | bumped by `narrative-emit` when content changes | not a version of the contract; never in a model call |
| `status` | DERIVED | `live · tombstone` | a withdrawn seed is a tombstone row, never a deleted file | not a review verdict |
| `provenance` | DERIVED | `generated · authored` | from the path: `authored/` → `authored` | not the model id |
| `tokens` | PLANNED | array of token names | the entity tokens and slots this seed's text may use | not a mention list — declared is permitted, not required |
| `_provenance` | DERIVED | object | what produced this revision (`narrative-emit`) | absent on authored seeds |

`revision` is the one integer on disk. It is a counter compared for equality and order, never a magnitude;
the audit allow-lists it **by name, with that comment**, and it never appears in a model-facing schema.
Authored ids carry `authored-` as the first segment of their body (`storylet.authored-…`); the planner's
minter never produces that prefix, so the two sources cannot collide.

### 4. Keyed text — the key rule

Every text field is an object:

```json
{ "key": "ns.storylet.delve-curio-curio-fire-001.choices.2.label.3f2a9c1b", "text": "<ICU message>" }
```

| Part | Rule |
|---|---|
| `key` | DERIVED by `narrative-emit`: `ns.<kind-namespace>.<id body>.<field path>.<h8>`, where the field path joins keys and array indices with dots and `h8` is the first eight hex digits of the SHA-256 of `text`. Matches `^[a-z0-9.-]+$` (`docs/architecture/item/seed-contract.md` §6) and is globally unique |
| `text` | AUTHORED; the model writes the short token forms and `token-grammar`'s `expand` stores full ICU |

Because the key carries the text's hash, a changed string is a new key and an unchanged string keeps its
key across revisions — the seed contract's rule that *"a changed string is a new key"* holds, and a
translation of an unchanged line is never lost. The runtime's codegen bridge uses the key as the lingui id
(`narrative-seed-ideal.md` §6.8).

### 5. The storylet

| Field | Level | Shape |
|---|---|---|
| `pattern` | PLANNED | a `storylet-vocab` choice-pattern id |
| `hosts` | PLANNED | ≥ 1 unique host kinds; each admits `kind` |
| `kind` | PLANNED | a storylet kind (`gk-data/packs/fusion/data/seed/dungeon/_registry/bands.v1.json:45`) |
| `climate` | PLANNED | one of the six elements or `none`; `none` if any host is climate-neutral; ~~for a world host, a member of that host's `climates` (Owner ruling 2026-09-20 (round 5), R19)~~ (Owner ruling 2026-09-20 (round 6), R20: any of the seven for a world host) |
| `repeatScope` | PLANNED | `gk-data/packs/fusion/data/seed/dungeon/_registry/bands.v1.json:56` |
| `arcRef`, `arcLink` | PLANNED | an arc id and one of its shape's link ids, or both `none` |
| `chainRef` | DERIVED | the next link's storylet id in the same arc, or `none` — derived from the arc's work order, so it always resolves |
| `roles[]` | VALIDATED (arc roles PLANNED) | `{roleId, kind, requires}`; `roleId` in `token-grammar`'s role form; `kind` from `storylet-vocab` §3.6 `roleKinds`; `requires` an array of `<family>:<value>` strings over §3.6's `requireFamilies` (for example `characterRole:trader`, `source:named`) — Audit 2026-09-19: one shape for storylet roles, arc-shape roles and the runtime's string array; count within `storylet.maxRoles` in the budget |
| `choices[]` | PLANNED length and slot kinds | one entry per pattern slot, in slot order |
| `choices[].choiceKind`, `choices[].param` | PLANNED | the slot's choice kind and its argument (or `none`). Audit 2026-09-19: renamed from `kind`/`arg` to the names the runtime reads (`npc-story-events/spec-storylet-contract.md` §1), which also keeps `kind` unambiguous (the storylet's own kind) |
| `choices[].condition` | VALIDATED | `{id, arg}` from `storylet-vocab` §3.4; const `none` on an unconditioned slot |
| `eligibility` | PLANNED | Audit 2026-09-19 (was missing; the runtime reads it): `null` (always eligible) for texture storylets; for an arc link whose shape lists `flagsRead`, a non-empty list of `{id: "story-flag-set", arg: "<flag>"}` conditions, all required, copied from the shape. Same `{id, arg}` vocabulary as `condition`; never model-written. Alignment 2026-09-20: only conditions whose `usableIn` includes `eligibility` may appear (`storylet-vocab` §3.4: `story-flag-set`, and `doctrine-studying` for a storylet the planner allocates to a study-site raid, `npc-story-events/spec-counter-doctrine.md` §5); the runtime compiles the list into one `And` of leaves |
| `fragment` | PLANNED | Alignment 2026-09-20: `none`, or the `fragmentId` of an `arc-shapes` §5 `fragments[]` row this storylet reveals. A fragment storylet's hosts are among `world.vault`, `world.shrine`, `delve.shrine`, `delve.curio`; its `interact` slot carries a `story.flag` outcome whose `ref` is `flag:fragment.<fragmentId body>` (DERIVED by the §5 `ref` rule); it carries no `loot`. No sort number: the runtime orders fragments by the frame's `after` chain (`npc-story-events/spec-spine-progress.md` §6) |
| `teaches` | PLANNED | Owner ruling 2026-09-20 (story is also the tutorial): an array of `storylet-vocab` §3.8 values whose `carriers` include `storylet` and whose `requires` the storylet meets; empty for content that teaches nothing. Never model-written; the teaching sentence is the registry's, not this seed's |
| `choices[].label` | AUTHORED | text |
| `choices[].outcomes[]` | fixed length per slot | the slot's outcome count from the pattern |
| `outcomes[].ordinal` | VALIDATED, **voted** | `outcomeOrdinal` (`gk-data/packs/fusion/data/seed/dungeon/_registry/bands.v1.json:52`) + `none` |
| `outcomes[].consequence` | object | `{kind, ref, param}` — **one object, owned by this contract** (Owner ruling 2026-09-19 (round 3): one consequence shape; the runtime loads it as-is). Its three members follow |
| `outcomes[].consequence.kind` | VALIDATED, **voted** | a consequence kind from `storylet-vocab` §3.5 + `none` |
| `outcomes[].consequence.param` | VALIDATED, **voted with `kind`** (the voted value is the pair) | a closed modifier from the kind's `params` list (`storylet-vocab` §3.5): for `relation.shift` the relation fact kind — `met · helped · refused · betrayed · spared`, the five relation facts `npc-story-events/spec-relation-ledger.md` §2 derives bands from; `none` for every other kind. `none` on `relation.shift` is refused |
| `outcomes[].consequence.ref` | DERIVED (Audit 2026-09-19; was PLANNED — see below the table) | the consequence's target, a string or `null`, in the prefixed forms `storylet-vocab` §3.5 declares per kind: `role:<roleId>` (a role declared in `roles[]`) or `character:<characterId>` for `relation.shift`; `role:<roleId>` or `host:wild` (the host's unnamed wild creature) for `recruit`; `flag:<flagId>` for `story.flag`; `quest:<questId>` (a narrative quest anchor, `spec-quest-vocab.md`) for `quest.offer`; `scene:<sceneId>` for `scene.play`; `null` for `none`, `loot`, `encounter`, `scout`, `battle.start` and `doctrine.setback` (Alignment 2026-09-20). Filled by the pipeline's deterministic resolve step (rule below the table), never the model |

| `outcomes[].effects[]` | VALIDATED | 0–2 `{family, powerBand}` from the grantable atom families and power bands (`gk-forge/tools/seedsmith/seedsmith/adapters/dungeon/registries.py:158`, `:192`) |
| `outcomes[].dropBand` | VALIDATED | `dropBand` (`gk-data/packs/fusion/data/seed/items/_registry/bands.v1.json:451`) + `none` |
| `outcomes[].result` | AUTHORED | text |
| `name`, `situation` | AUTHORED | text |

Owner ruling 2026-09-19 (round 3): `consequenceRef`, the `arg` member of the old `{kind, arg}` shape and the proposed
`consequenceParam` are **retired**; no seed, schema or runtime row carries them. The runtime
(`npc-story-events/spec-storylet-contract.md` §1–§2) reads `consequence.kind`, `.ref` and `.param` with the same
names, nullability and closed lists.

Audit 2026-09-19: the paragraph above used to sit inside the table and split it, so the `effects`, `dropBand`,
`result` and `name` rows rendered without a header.

**How `consequence.ref` is filled (Audit 2026-09-19).** The table used to call `ref` PLANNED and filled "by the
planner from … the declared roles" — but `roles[]` is written by the structure call, after planning. `ref` is
therefore **DERIVED**: computed deterministically by the storylet pipeline's resolve step from planned facts and
the resolved structure, never by the model. The rule, per kind:

| Kind | `ref` source |
|---|---|
| `story.flag` | the arc shape's `flagsSet` entry the planner pinned to this outcome position (`spec-arc-pipeline.md` §3) |
| `quest.offer` | the quest anchor the planner attached to this storylet's work item (`spec-quest-vocab.md` §4) |
| `scene.play` | the spine scene the planner attached to this work item |
| `relation.shift`, `recruit` | the role of this slot's `role-cast` condition when present, else the first declared role (declaration order) whose `kind` is not `forbidden` and, for `recruit`, whose allegiance is not antagonist; `recruit` may also take `host:wild` when the host kind is `delve.wild` and no role qualifies |
| every other kind | `null` |

The structure call's per-item `consequence.kind` enum offers only the kinds whose `ref` the item can fill: no
`story.flag` outside an arc link with a pinned flag, no `quest.offer` without an attached quest, no `scene.play`
without an attached scene. A `relation.shift` or `recruit` whose rule finds no role is the named structural defect
`consequence-ref-unfillable` (a QUALITY retry, `spec-narrative-validators.md` §2).

Descriptions (excerpt; every field has one, with its negative clause, in `descriptions.py`):

- `situation` — *the scene the player reads before choosing. It is not a rules explanation, never names
  the better option, and never states an amount.*
- `choices[].label` — *what the player chooses, in a few words. It is not the outcome and does not promise
  one.*
- `outcomes[].ordinal` — *whether this outcome is good, mixed, bad or nothing for the party. It is not a
  size: a small good and a large good are both `good`.*
- `outcomes[].dropBand` — *how often this outcome is drawn among its choice's outcomes. It is not loot
  quality; `none` means the choice has one certain outcome.*

**Weights, magnitudes, costs, odds and cooldowns are not fields** — they are resolved at runtime from the
bands, `Instantiator` and `P(Θ)`, and tuning (`narrative-seed-ideal.md` §6.2 last row).

The `leave` slot's single outcome is PLANNED const: `ordinal: nothing`, `consequence: {kind: none, ref: null,
param: none}`, `effects: []`, `dropBand: none`. Only its `label` is written by the model. (Owner ruling 2026-09-19
(round 3): the constant uses the one `{kind, ref, param}` shape.)

### 6. The character

| Field | Level | Shape |
|---|---|---|
| `tier` | PLANNED | `lead · recurring · texture` |
| `lead` | PLANNED | a lead token, or `none`; set iff `tier` is `lead` |
| `speciesId` | PLANNED | a species id from the creature anchors (`gk-data/packs/fusion/data/seed/creatures/species/`, field `speciesId`), or `none` iff `tier` is `lead` |
| `side`, `element` | DERIVED | from the species anchor's `side` and `elementPrimary` (`docs/architecture/creature-seed/spec-anchor-contract.md` §2) |
| `role` | VALIDATED, **voted** — except on a lead, where it is PLANNED const `none` (Audit 2026-09-19: a lead is not one of the nine roles, `spec-character-vocab.md` §3) | `character-vocab` roles + `none` (a `none` result refuses a non-lead seed) |
| `voice` | VALIDATED, **voted** | `character-vocab` registers + `none` |
| `allegiance` | DERIVED | from `role`, or from the leads block for a lead |
| `name`, `epithet` | AUTHORED | text; `null` iff `tier` is `lead` (the names registry owns lead names); on a lead they never appear in the identity call schema |
| `bio` | AUTHORED | text |
| `grammar` | VALIDATED | `{gender, number, article, epithetArticle}` from `tokens.v1.json`'s features; `null` iff `tier` is `lead` |
| `anchors` | AUTHORED, reviewed | array of text; count within `character.anchorLines.{min,max}` in the budget |
| `lexicon` | AUTHORED, reviewed | `{signature: [word], forbidden: [word]}` |
| `anchorReview` | DERIVED | `pending · accepted · rejected`, from the review verdicts; no line call runs unless `accepted` |
| `lines[]` | AUTHORED text, PLANNED `context`/`band` | `{context, band, text}`; exactly one per required pair for the allegiance (`character-vocab` §6) |

**Not in the seed, by design:** personality (derived from the minted specimen,
`gk-core/src/FusionRpg.Core/Creatures/Contracts/ContractPolicy.cs:195`), disposition (the relation ledger), home
(casting) — `narrative-seed-ideal.md` §6.3. **No field changes a character** — no level, rank, title,
trait or subordinate list — which is R13 rules 1–2 made structural (`character-vocab` §6).

### 7. The arc

| Field | Level | Shape |
|---|---|---|
| `shape` | PLANNED | an `arc-shapes` shape id |
| `cast[]` | PLANNED | the shape's persistent roles, verbatim |
| `links[]` | PLANNED | `{linkId, storyletRef}` in shape order; every referenced storylet's `arcRef` is this arc and `arcLink` is that link |
| `name`, `premise` | AUTHORED | text |

### 8. The spine chapter

| Field | Level | Shape |
|---|---|---|
| `chapterId`, `pieceId`, `after` | PLANNED | copied from the spine frame (`arc-shapes` §5) |
| `title`, `synopsis` | AUTHORED | text. Audit 2026-09-19: `synopsis` added — `spine-pipeline` §2 writes it and feeds the next chapter's call; it was missing here |
| `scenes[]` | PLANNED shape | `{sceneId, teaches, beats[]}`; `sceneId` is `scene.<chapter slug>.<scene slot>`; the beat count equals the frame's |
| `scenes[].teaches` | PLANNED | Owner ruling 2026-09-20: a `storylet-vocab` §3.8 value whose `carriers` include `spine`, or `none`; copied from the frame (`arc-shapes` §5). The runtime shows that value's authored teaching sentence on the scene's last beat (`npc-story-events/spec-scene-script-loader.md` §2); the model never writes it |
| `beats[].speaker` | PLANNED | a cast token, or `none` for narration |
| `beats[].line` | AUTHORED | text |

A scene is data, not a TypeScript literal (today's scripts are,
`RIFT_PROLOGUE_SCRIPT` at `gk-web/web/fusion-rpg-web/src/features/story-scene/sceneScript.ts:105`; Reconciled 2026-09-19: `:32` is the `SceneBeat` type; the literal is at `:105`); loading it is the runtime's
`scene-script-loader`. Speaker ids are tokens rather than the closed `ActorId` union
(`gk-web/web/fusion-rpg-web/src/features/story-scene/sceneScript.ts:19`), which widens under story-scene review
(`npc-story-events-map.md` row 12).

### 9. Call schemas — which call writes which field

The contract owns the per-call JSON Schemas, so the audit covers exactly what a model sees. PLANNED fields
are `const`; VALIDATED fields are `enum`s (permuted per sample by the pipeline, `order_for`,
`gk-forge/tools/seedsmith/seedsmith/adapters/creatures/anchor/permute.py:26-33`); DERIVED fields never appear.

| Call | Writes | Shows as `const` |
|---|---|---|
| `storylet-structure` | `roles`, per-slot `condition`, per-outcome `ordinal`, `consequence.kind` and `consequence.param`, `effects`, `dropBand` | id, pattern, hosts, kind, climate, arc fields, `eligibility`, `teaches`, slot kinds and params, the leave outcome. `consequence.ref` never appears (filled deterministically after the vote) |
| `storylet-text` | `name`, `situation`, `label`s, `result`s | the whole resolved structure |
| `character-identity` | `role`, `voice`, `name`, `epithet`, `bio`, `grammar` (a lead: `voice` and `bio` only) | id, tier, lead, species facts |
| `character-anchors` | `anchors`, `lexicon` | identity |
| `character-lines` | the `text` of one band's lines | identity, anchors, the band's `(context, band)` list |
| `arc-premise` | `name`, `premise` | shape, cast, link ids |
| `spine-chapter` | `title`, `synopsis` | the frame, the cast tokens, the previous chapter's accepted synopsis (Audit 2026-09-19: the call `spine-pipeline` §2 makes was missing) |
| `spine-scene` | each beat's `line` for one scene | the frame, speakers, the scene's `teaches` value with its description (so the scene sets up the lesson; Owner ruling 2026-09-20), the same candidate's title and synopsis |

The vote sets named above (storylet `ordinal` and `consequence` — the `(kind, param)` pair, Owner ruling 2026-09-19
(round 3); character `role` and `voice`) are the map's (row 18–19); a 1-1-1 split is `unresolved`
(`gk-forge/tools/seedsmith/seedsmith/adapters/creatures/anchor/vote.py:26-43`).

**Every call schema carries the `blocked` escape (Audit 2026-09-19).** `seedsmith/spec-pipeline.md` §3.7 requires a
`blocked` variant with a reason string, and the core audit refuses a schema without one at its root
(`gk-forge/tools/seedsmith/seedsmith/pipeline/model.py:198-204`). Each call schema above therefore has a root `blocked`
property (a nullable reason string, with its own `FieldDoc`: *the reason you cannot write this without inventing
a fact; not a complaint about the brief's style*). A blocked reply writes nothing, is not retried, and ends
the work item with a terminal `blocked` ledger row (`spec-narrative-emit.md` §7) and its reason in the run
report. The contract previously omitted it, so `contract --audit` could never have exited 0.

### 10. The schema audit

`narrative_audit(kind)` runs over the document schema and every call schema for that kind:

1. **Core numeric audit**, `audit_schema` (`gk-forge/tools/seedsmith/seedsmith/pipeline/model.py:113`) over **every call
   schema** — the four smuggling shapes: bare numbers, digit-admitting patterns, numeric-string enums and
   magnitude-named fields are refused, plus the root `blocked` check. The document schema is walked with the
   same four checks **except over DERIVED fields**, and without the root `blocked` check (it is not
   model-facing). Audit 2026-09-19: this rule used to pass `name_allowlist={"revision"}`, but the core
   allowlist exempts only the name, pattern and enum checks — the bare-numeric check fires regardless
   (`gk-forge/tools/seedsmith/seedsmith/pipeline/model.py:144-151`) — so `revision` would have failed the audit.
   `revision` is DERIVED, so it is never walked; a test pins that it is the only integer on disk.
2. **Stem and spelled-number checks** — a property name containing `weight` or `chance`, or an enum member
   spelling a number, is refused (the dungeon adapter's extensions,
   `gk-forge/tools/seedsmith/seedsmith/adapters/dungeon/audit.py:30-35`, re-stated here because that module is
   dungeon-local).
3. **PLANNED is const** in every call schema.
4. **Every model-facing `enum` contains `none`** — including borrowed lists (atom family, power band,
   drop band, outcome ordinal, role kind, requirement families, condition arguments), whose `none` rows and
   notes come from `storylet-vocab`'s `value-notes.v1.json` (Audit 2026-09-19: previously only three borrowed
   lists had a `none` note).
5. **`additionalProperties: false` and every property required**, at every object level.
6. **Every property has a `FieldDoc(meaning, negative)`**, both non-empty — the negative clause is a
   separate string, so its presence is a mechanical test.
7. **Every text field** is declared as such, has a script policy of `latin` (`script-check`), and carries a
   `maxLength` equal to its `text.lengthBounds.<kind>.<field>.max` plus `text.schemaSlack` characters (budget
   rows; the slack covers short-form tokens longer than their display strings). Audit 2026-09-19: this rule
   relied on a digit-free `pattern` "as a decoding hint", but llama.cpp's schema-to-grammar converter does
   not enforce `pattern`, and a pattern-only field with no `maxLength` produced a 20K-token repeated-token
   loop in a real run (`gk-forge/tools/seedsmith/seedsmith/pipeline/llm_caller.py:52-59`). The no-digit rule is
   enforced by `validate_entry` and `narrative-validators`, never by decoding.
8. **Exactly one ownership level per field**, and every field in the document schema has one.

### 11. `validate_entry(kind, entry)` — the on-disk check

Refuses, naming the field path: an unknown or missing key; a value outside its registry; a PLANNED field
that disagrees with its registry (hosts vs kind, pattern vs slots, outcome counts, arc link vs shape); a
`leave` slot other than the const one; `nothing` with non-empty `effects` or a consequence other than
`none` or `story.flag`; a `consequence` that is not exactly `{kind, ref, param}`, a `ref` whose presence or prefix
disagrees with the kind's `refForms`, or a `param` outside the kind's `params` (Owner ruling 2026-09-19 (round 3));
`dropBand: none` on a slot with more than one outcome; a text key that does not
follow §4; **any digit in the literal text of a text field** (`token-grammar`'s `literal_text`); a token
in text outside the grammar (`parse`); a token not in `tokens`, not a declared role's token and not an
allowed slot; a character whose `lines` miss or repeat a required pair; a lead character with a name,
epithet or grammar; a non-lead with none; an `eligibility` that disagrees with the arc shape's `flagsRead`;
a `ref` that disagrees with the §5 derivation rule. A **tombstone row** (`spec-narrative-emit.md` §5) is
validated against its own closed shape — `id`, `revision`, `status: tombstone`, `provenance`,
`withdrawnReason` — instead of the kind's full field list (Audit 2026-09-19: the every-field-required rule
would otherwise refuse every tombstone).

This is structure and closure. Fairness (lose-lose, dominance, choice type, conditional value), echo,
collision and literal-name rules are `narrative-validators`' (map row 12), which calls `validate_entry`
first.

### 12. Wiring owed at build

- `gk-core/scripts/guard-generated-seed.py` gains a tree row: generated `^gk-data/packs/fusion/data/seed/narrative/`, sources
  `^gk-forge/tools/seedsmith/seedsmith/adapters/narrative/`, `^gk-data/packs/fusion/data/seed/narrative/_registry/`,
  `^gk-data/packs/fusion/data/seed/narrative/_exemplars/`, `^gk-data/packs/fusion/data/seed/narrative/_plan/` (the existing rows,
  `gk-core/scripts/guard-generated-seed.py:40-72`, are the pattern).
- `gk-core/scripts/enforcement-registry.v1.json` gains the invariant `narrative-no-digit-in-prose` (source: map §2
  principle 2; guard: `tools/seedsmith/tests/test_narrative_contract.py`) — the map §13 checklist names it.
- `decisions.md` row 1 (the storylet contract and the grid change) is drafted in
  `spec-narrative-planner.md` §1 and lands with that module; row 5 (identity over regeneration) is drafted
  in `spec-narrative-emit.md`.

### 13. Runtime field mapping — open cross-program differences (Audit 2026-09-19)

`npc-story-events/spec-storylet-contract.md` §1 lists the fields the runtime reads from this contract's
storylet. This audit renamed `choices[].kind`/`.arg` to the runtime's `choiceKind`/`param`, added the missing
`eligibility`, and aligned `requires` to a string array. Six differences remain; this contract is the seed
shape's owner, so each is filed on `storylet-contract` to read the seed as written, and none is changed here
because each change on this side would break a rule stated above:

| This contract | Runtime spec reads | Why this side keeps it |
|---|---|---|
| file envelope `{schemaVersion, kind, _meta, entries[]}` (§2) | a bare storylet object | the core corpus loader and the generated-seed guard read the envelope (§2) |
| `id` | `storyletId` | the core loader keys entries on `id` (`gk-forge/tools/seedsmith/seedsmith/corpus/model.py:193-194`) |
| `status: live · tombstone` | `tombstone: true · false` | same information; `status` is the emit and metrics vocabulary (`spec-narrative-emit.md` §5) |
| slot = array position | `slot` integer | a second integer on disk is "ask first" (Boundaries); the array index is the slot |
| `arcLink` = the shape's link id (`<shapeId>.<name>`) | an integer (`0` for none) | link ids are the shape registry's ids; an ordinal integer would be a second integer on disk |
| `condition` / `eligibility` as `{id, arg}` from `conditions.v1.json` | a compiled `PredicateNode` tree | two of the leaves are proposed, not built (`spec-storylet-vocab.md` §3.4); the runtime compiles `{id, arg}` through the shared registry's `compilesTo`, the one file both sides read |

Until `storylet-contract` records these, a loader built from its §1 sketch would refuse every generated
storylet — a HIGH finding, deferred to that spec's owner (this audit may not edit it).

**Resolution — Alignment 2026-09-20.** Checked against `npc-story-events/spec-storylet-contract.md` as it stood
after its own 2026-09-19 audit: the envelope, `id`, `status`, slot-as-position and `arcLink`-as-link-id rows were
already read as written here; the condition row was half-closed (the loader compiled `{id, arg}` through
`ConditionCompiler`), but the same audit had crossed two names the other way (its example wrote choices as
`kind`/`arg` while this contract had renamed them to `choiceKind`/`param`) and declared that a widened seed carries
no `eligibility`. The alignment made that spec read this contract exactly: its §1 example is this §5 field for
field (envelope, `id`, `status`, `choiceKind`, `param`, `{id, arg}` conditions, `eligibility`, `teaches`), its §2
C# sketch maps each seed name, its §3 loader compiles every condition object and the `eligibility` list into
`PredicateNode` trees at load (`npc-story-events/spec-narrative-predicates.md` §5), and its §5 refusal codes cover
the envelope, the status vocabulary, unknown condition ids and eligibility-only conditions. All six differences are
closed; this contract did not change shape for any of them.

---

## Commands

```powershell
$env:PYTHONPATH = "gk-forge/tools/seedsmith"; python -m pytest tools/seedsmith/tests/test_narrative_contract.py -q
cd tools\seedsmith; python -m seedsmith narrative contract --print --kind storylet     # document + call schemas
cd tools\seedsmith; python -m seedsmith narrative contract --audit                     # exit 1 on any finding
cd tools\seedsmith; python -m seedsmith check ..\..\data\seed\narrative --adapter narrative
```

## Project structure

```text
gk-forge/tools/seedsmith/seedsmith/adapters/narrative/__init__.py        NarrativeAdapter (the package marker from Wave 1 grows the class)
tools/seedsmith/seedsmith/adapters/narrative/kinds.py           (new) four KindSpecs
tools/seedsmith/seedsmith/adapters/narrative/schema.py          (new) ownership tables, document and call schemas
tools/seedsmith/seedsmith/adapters/narrative/descriptions.py    (new) FieldDoc(meaning, negative) per field
tools/seedsmith/seedsmith/adapters/narrative/audit.py           (new) narrative_audit
tools/seedsmith/seedsmith/adapters/narrative/validate.py        (new) validate_entry, key rule
gk-forge/tools/seedsmith/seedsmith/adapters/registry.py                  one line
gk-forge/tools/seedsmith/seedsmith/report/cli.py                         `narrative contract` subcommand
gk-data/packs/fusion/data/seed/narrative/{storylets,characters,arcs,spine}/          (new) empty
data/seed/narrative/authored/{storylets,characters,arcs,spine}/ (new) empty
gk-data/packs/fusion/data/seed/narrative/_plan/budget.v1.json                        blocks `storylet.maxRoles`, `character.anchorLines`, `text.schemaSlack` (Audit 2026-09-19)
tools/seedsmith/tests/test_narrative_contract.py                (new)
gk-core/scripts/guard-generated-seed.py                                one tree row (build change)
```

Descriptions live apart from the shape because they change far more often, and a diff mixing the two is
unreviewable (the creature anchor's precedent, `docs/architecture/creature-seed/spec-anchor-contract.md`
"Project structure").

## Code style

Follow the dungeon adapter: ownership tables as dicts per kind, schemas built in code from registries read
fresh, `_enum(..., const=True)` for PLANNED fields (`gk-forge/tools/seedsmith/seedsmith/adapters/dungeon/schema.py:67-79`).
Refusals name the kind, the field path and the value.

## Testing strategy

Fixture seeds use invented ids and invented text; no test counts seeds in the corpus.

| Test | Asserts |
|---|---|
| `adapter_is_registered_and_satisfies_the_protocol` | `resolve_adapter("narrative")` returns a `SeedAdapter` |
| `every_field_has_exactly_one_level` | all four kinds |
| `every_field_has_meaning_and_negative` | `FieldDoc` both non-empty |
| `audit_is_clean_for_every_document_and_call_schema` | `narrative_audit` returns nothing |
| `audit_catches_each_smuggling_shape` | one crafted schema per §10 rule fails |
| `revision_is_the_only_allowlisted_integer` | pinned, reason in the comment |
| `model_facing_enums_admit_none` | every call schema |
| `planned_fields_are_const_in_calls` | every call schema |
| `key_rule_is_deterministic_and_hash_bearing` | same text → same key; changed text → new key; pattern holds |
| `digit_in_literal_text_is_refused` | `"gain 50 souls"` refused; a character token whose slug has a digit is not |
| `undeclared_token_is_refused` | a `{c_x}` absent from `tokens` refused |
| `leave_slot_is_const` | a leave outcome with an effect refused |
| `consequence_is_kind_ref_param` | an outcome carrying `consequenceRef`, `arg` or `consequenceParam` is refused as an unknown key; `relation.shift` with `param: none`, a `loot` with a non-null `ref`, and a `story.flag` whose `ref` lacks the `flag:` prefix are each refused (Owner ruling 2026-09-19 (round 3)) |
| `pattern_slots_and_outcome_counts_enforced` | crafted mismatch refused |
| `arc_link_consistency` | `arcRef` without `arcLink`, or a link id from another shape, refused |
| `chain_ref_is_derived_and_resolves` | a fixture arc's storylets chain in link order, last link `none` |
| `character_lines_cover_required_pairs_exactly` | a missing and a duplicate pair each refused |
| `lead_character_has_no_name_or_grammar` | and a non-lead without them is refused |
| `no_character_field_changes_a_character` | the character schema has no level, rank, title, trait or subordinate property (R13) |
| `authored_and_generated_ids_cannot_collide` | the minter never emits the `authored-` prefix |
| `core_corpus_loader_reads_the_envelope` | `Corpus.load` over a fixture tree yields each seed with its kind |
| `every_call_schema_has_blocked_variant` | each call schema's root has `blocked`; a crafted schema without it fails the audit (Audit 2026-09-19) |
| `blocked_reply_writes_nothing` | a fixture reply with `blocked` set produces a terminal `blocked` row and no seed |
| `document_walk_skips_derived_fields` | `revision` (integer) passes the document audit; the same integer on a non-DERIVED field fails |
| `audit_catches_all_four_smuggling_shapes` | one crafted call schema per shape — bare number, digit-admitting pattern, numeric-string enum, magnitude name — each fails |
| `text_fields_carry_max_length` | every text field in every call schema has `maxLength` from the budget; none relies on `pattern` alone |
| `consequence_ref_derivation` | each row of the §5 rule on a fixture structure; a `relation.shift` with no qualifying role yields `consequence-ref-unfillable` |
| `per_item_consequence_enum_excludes_unfillable_kinds` | a texture storylet's schema offers no `story.flag`, `quest.offer` or `scene.play` |
| `eligibility_follows_flags_read` | an arc link's `eligibility` equals its shape's `flagsRead`; texture storylets carry `null`; a slot-only condition id in `eligibility` is refused (Alignment 2026-09-20) |
| `teaches_meets_requires` | a storylet whose `teaches` names `offer-cost` without an `offer` slot, or a spine value with `carriers: [spine]` on a storylet, is refused (Owner ruling 2026-09-20) |
| `tombstone_row_shape` | a tombstone with the five fields validates; one with an extra or missing field is refused |
| `lead_identity_writes_voice_and_bio_only` | the lead identity call schema has no `role`, `name`, `epithet` or `grammar` property |

## Boundaries

- **Always:** one level per field; meaning plus negative per field; PLANNED as const; keys derived; the
  audit over every schema a model sees.
- **Ask first:** a new field or kind; changing a vote set (it moves the call budget); a second integer on
  disk.
- **Never:** a magnitude, weight, cost or probability field; a model-written key; narrative code in the
  seedsmith core; a hand-edited generated seed.

## Success criteria

- [ ] `narrative` is a registered adapter and the core loader reads its tree.
- [ ] Four document schemas and eight call schemas exist (Audit 2026-09-19: `spine-chapter` added); with
      `quest-vocab`, five and nine. Every call schema carries the root `blocked` escape; `contract --audit`
      exits 0.
- [ ] `validate_entry` accepts one fixture per kind and refuses a crafted violation of every §11 rule.
- [ ] No text field can hold a digit; `revision` is the only integer, allow-listed by name.
- [ ] The guard row and the invariant row are added in the build change.

## Contradictions found in reconciliation (2026-09-19) — resolved

1. **`consequence` shape — RESOLVED.** Owner ruling 2026-09-19 (round 3): this contract owns one object,
   `outcomes[].consequence = {kind, ref, param}` (§5). It replaced three competing shapes: `{kind, arg}` here, a
   plain kind string beside `consequenceRef` in `npc-story-events/spec-storylet-contract.md` §1–§2, and the
   ordinal → relation-fact mapping `spec-outcome-routing.md` §2 used for want of a fact kind (with a proposed
   `consequenceParam`). `ref` carries the target the old `arg`/`consequenceRef` duplicated; `param` carries the
   relation fact kind, so the `warmer · colder` direction and the ordinal mapping are gone. The runtime loads the
   object as-is; the three sibling specs were updated in the same change.

## Open questions

None.

---

## Standards audit (2026-09-19)

Independent adversarial review against `docs/research/ai-native-generation/README.md` §10, seedsmith P1–P5,
`seedsmith/spec-pipeline.md` §3, `spec-quality-gates.md`, `spec-workflow-runtime.md`, `validation-ssot.md`,
`tunables-ssot.md`, `item/seed-contract.md` §2–§7, `DESIGN-GATE.md` §3/§5, owner rulings R1–R13 and IC-3, and
the runtime contracts (`npc-story-events/spec-storylet-contract.md`, `spec-narrative-text.md`). Every change
in the body is marked "Audit 2026-09-19" (or "Owner ruling 2026-09-19 (round 4)" where the owner ruled).

| # | Severity | Finding | Status |
|---|---|---|---|
| 1 | high | No call schema carried the `blocked` escape (`spec-pipeline.md` §3.7); the core audit refuses a schema without it (`pipeline/model.py:198-204`), so `contract --audit` could never exit 0 | fixed (§9, §10, tests) |
| 2 | high | `name_allowlist={"revision"}` does not exempt the bare-numeric check (`pipeline/model.py:144-151`); `revision` would have failed the document audit | fixed (§10 rule 1: DERIVED fields are not walked) |
| 3 | high | Six field-shape differences from the runtime reader (`storylet-contract` §1): envelope, `id`/`storyletId`, `status`/`tombstone`, `slot`, `arcLink` type, `{id, arg}` vs compiled tree — a loader built from that sketch would refuse every generated storylet | **closed — Alignment 2026-09-20** (§13 resolution note; the runtime reads this shape) |
| 4 | medium | `consequence.ref` was PLANNED "from the declared roles", but roles are written by the structure call after planning | fixed (DERIVED, deterministic rule, per-item kind enum, `consequence-ref-unfillable`) |
| 5 | medium | No `eligibility` field, though arc links read flags and the runtime reads `eligibility` | fixed (PLANNED from `flagsRead`) |
| 6 | medium | Text fields relied on an unenforced `pattern` as a decoding hint with no `maxLength` (the repeated-token-loop incident, `llm_caller.py:52-59`) | fixed (§10 rule 7) |
| 7 | medium | Spine chapter lacked `synopsis` and the `spine-chapter` call that `spine-pipeline` makes | fixed (§8, §9; eight call schemas) |
| 8 | medium | Leads had a voted `role`, though a lead is not one of the nine roles | fixed (§6, §9) |
| 9 | medium | Every-field-required would refuse every tombstone row | fixed (§11 tombstone shape) |
| 10 | medium | Borrowed model-facing enums (atom family, power band, role kind, requirement families, condition args) had no `none` | fixed (§10 rule 4, with `storylet-vocab` §3.7) |
| 11 | low | `choices[].kind`/`.arg` differed from the runtime's `choiceKind`/`param`; `quest` missing from the id namespaces; a paragraph split the storylet table; `requires` had three shapes across specs | fixed |
| 12 | low | Citations sampled against code: `adapters/base.py:95-100`, `adapters/registry.py:12-18`, `corpus/model.py:182-199`, `pipeline/model.py:113`, `dungeon/audit.py:30-35`, `dungeon/schema.py:67-79` — all resolve | verified |
