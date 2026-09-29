# Spec: `quest-vocab`

**Program:** [narrative-seed](../narrative-seed-map.md) · **Module id:** `quest-vocab` · **Map row:** 23 · **Wave:** 2
**Depends on:** `storylet-vocab` (the `quest.offer` consequence kind), `narrative-contract` (adapter, envelope,
common fields, key rule) · **Model calls:** none
**Status:** spec phase, 2026-09-19. Owner ruling 2026-09-19 (round 3): the map amendment adding this module is
approved; no build authorized.
**Runtime consumer:** `npc-story-events`' `quest-sources` (`npc-story-events/spec-quest-sources.md` §2–§6) loads the
anchors and the objective registry; `quest-log-contract` shows them (`npc-story-events/spec-quest-log-contract.md`
§2–§3). This contract is shaped to those two specs.

---

## Objective

Define the **narrative quest** as a seed kind of the `narrative` adapter, and the closed registry of objective
templates it may use:

1. **A quest anchor** — the `QuestRow` shape the one quest engine already loads
   (`gk-core/src/FusionRpg.Core/Delve/Quests/QuestRow.cs:23-30`), with the two new scopes `save` and `world`, keyed text with
   tokens, and bands in place of every number.
2. **Objective templates as a closed vocabulary** — each with a target kind, the mode-agnostic fact sources that can
   fill it, and whether it is counted. **Standalone-first:** no template may be fillable only on the lawn.
3. **Expiry on host clocks, never the calendar**, declared as a closed choice; **rewards from the host's budget**,
   declared as a band (Owner ruling 2026-09-20: taken out of what the place already pays, never an extra roll).

The model writes a quest's name and flavor and never a number, a target id or an expiry length (map §2 principle 2).

**Done means:** the registry file and its reader exist; `contract --print --kind quest` and `contract --audit` cover
the quest document and call schemas; `validate_entry("quest", …)` accepts fixture anchors of every template and
refuses a crafted violation of every rule below; the registry's template ids are disjoint from the Delve's.

---

## Design

### 1. One quest engine — this contract widens `QuestCatalog`, it does not sit beside it

The decision the owner asked for, made by SOLID (principle 11 of `npc-story-events-map.md`: *one quest engine*):

| Option | Verdict |
|---|---|
| **Widen** — narrative anchors are `QuestRow`s loaded by the same `QuestCatalog.Load`, with the narrative objective templates and scopes passed in beside the Delve's | **Chosen.** `Load` already takes every vocabulary as a parameter — templates, scopes, reward bands, count bands (`gk-core/src/FusionRpg.Core/Delve/Quests/QuestCatalog.cs:84-92`) — and refuses a duplicate quest id across the whole row list (`:108-111`). The engine, its refusal namespace (`QuestRules`, `:8-33`), the offer draw and the reward window stay one |
| Sit beside — a `NarrativeQuestCatalog` with its own loader and rules | **Rejected.** A second catalog deciding "is this a legal quest" is the dual-engine defect SOLID forbids; it would fork the refusal rules and the reward window |

What "widen" costs the runtime, stated so `quest-sources` builds it (filed there; this module writes no C#):

1. **Scopes.** The caller passes `delve · domain · roster` (the Delve's `questScope`,
   `gk-data/packs/fusion/data/seed/dungeon/_registry/bands.v1.json:68-71`) **plus** `save · world` (§3 below). The refusal message at
   `QuestCatalog.cs:157` names the three Delve scopes literally and must name the list it was given.
2. **Target kinds.** `ObjectiveTargetKind` is closed at `room-kind · curio-kind · item-kind · boss · none`
   (`gk-core/src/FusionRpg.Core/Dungeon/Registry/ObjectiveTemplateCatalog.cs:5-12`, names at `:29-36`), and `Load`'s
   target-ref rule hard-codes which kinds need a ref (`QuestCatalog.cs:120`). The narrative target kinds (§2) widen
   that enum as a reviewed change, and the rule reads the registry's `targetRef` attribute instead of a kind list.
3. **Count-less templates.** `QuestCatalog.CountLessTemplates` is a hard-coded list of the six Delve count-less ids
   (`QuestCatalog.cs:57-61`). The narrative registry carries `counted` per template; the catalog reads it for
   narrative templates rather than growing the literal list.

The registry is a **separate file** from the Delve's `objective-templates.v1.json` because the two have different
owners (party-dungeon's dungeon adapter, this program) — not because they are different engines. Both parse into
the one `ObjectiveTemplateDef` type (`ObjectiveTemplateCatalog.cs:16-24`); a test proves the two id sets are
disjoint, so the union the caller passes can never hold one id twice.

### 2. `quest-objectives.v1.json` — the closed objective vocabulary

`data/seed/narrative/_registry/quest-objectives.v1.json` (new), the common registry shape of
`spec-storylet-vocab.md` §2 (`description` and `negative` as separate keys; unknown keys refused).

**Fact sources** — closed, each a durable record another program already commits (`npc-story-events/spec-quest-sources.md`
§3; a source never reads live state):

| Source | Standalone-playable | Negative clause |
|---|---|---|
| `battle` | yes | not a lawn match: a persisted battle report of any mode |
| `world-turn` | yes | not a live map read: a committed turn report |
| `expedition` | yes | not a dispatch: a collected expedition |
| `delve` | yes | not an open delve: a closed one |
| `story` | yes | not a counter: a story-ledger fact |
| `pvz` | **no** | enrichment only — a lawn activity fact may add to a count, never be its only source |

**Templates** — the eight `quest-sources` §3 names, each row with `targetKind`, `targetRef`, `counted`, `sources`:

| Template | `targetKind` | `targetRef` | `counted` | `sources` | Negative clause |
|---|---|---|---|---|---|
| `defeat-creatures` | `creature-tag` | kind ref | yes | `battle`, `pvz` | not "on the lawn": any battle source counts |
| `win-battles` | `battle-kind` | kind ref or `none` | yes | `battle`, `world-turn` | not a kill count |
| `hold-sector-kind` | `slot-kind` | kind ref | no | `world-turn` | not a specific sector |
| `hold-sector` | `sector` | **bound at offer** | yes (consecutive turns) | `world-turn` | the seed never names a sector id |
| `develop-sector` | `sector` | **bound at offer** | no | `world-turn` | not a build order the quest issues |
| `complete-expeditions` | `expedition-tier` | kind ref | yes | `expedition` | a recall does not count |
| `extract-delves` | `domain` | kind ref or `none` | yes | `delve` | not a wipe |
| `story-fact` | `story-fact` | kind ref (fact kind + subject family) | no | `story` | not a flag the quest itself sets |

- `targetRef` is one of three closed attributes: `kind ref` (the seed names a category from that target kind's own
  registry, never an id or a number — the Delve rule, `QuestRow.cs:7-8`), `none`, or `bound at offer` (the seed
  carries `none`; the runtime binds the id from the offering host when `quest.offer` fires,
  `spec-quest-sources.md` §3).
- **The standalone rule, structural:** every template's `sources` contains at least one source whose
  `standalonePlayable` is true. The reader refuses a row whose sources are `[pvz]` alone, with the same rule id the
  runtime uses, `quest.objective-lawn-only` (`spec-quest-sources.md` §3.1). No template reads a lawn-only fact.
- **Scopes** — the file's `questScopes` block declares `save` (*lives across worlds, like the roster; not a
  world's*) and `world` (*lives as long as its world exists; not a delve's*). The Delve's three scopes stay in the
  dungeon bands registry; this file never copies them.

The template member list, the source list and the target-kind list are closed and pinned with their reason (a
declaration, reviewed when changed). The template list starts at the eight `quest-sources` names; a ninth is a
reviewed registry row plus one evaluator arm in `quest-sources`.

### 3. The quest anchor — kind `quest`

One anchor per file under `data/seed/narrative/quests/` (new) when generated, `data/seed/narrative/authored/quests/`
(new) when hand-written, in `narrative-contract` §2's envelope with `kind: "quest"`. The common fields (`id`,
`revision`, `status`, `provenance`, `tokens`, `_provenance`) are `narrative-contract` §3's.

| Field | Level | Shape | Negative clause |
|---|---|---|---|
| `id` | PLANNED | `quest.narrative-<slug>` (generated) or `quest.authored-<slug>` (authored) | never reused; the `narrative-`/`authored-` body prefix keeps it apart from the Delve's `quest.<template>-…` ids, and `QuestCatalog.Load` refuses a collision anyway (`QuestCatalog.cs:108-111`) |
| `templateId` | PLANNED | a `quest-objectives.v1.json` template | not a Delve template: those are delve-scoped |
| `targetRef` | PLANNED | per the template's `targetRef` attribute: a kind ref, `none`, or `none` for a bound-at-offer template | never an id, never a number |
| `countBand` | PLANNED | `lone · few · several · many` (`gk-data/packs/fusion/data/seed/dungeon/_registry/bands.v1.json:33-35`) on a counted template; `none` on a count-less one | not a count; the runtime turns the band into `need` from tuning |
| `rewardBand` | PLANNED | `modest · fair · rich` (`gk-data/packs/fusion/data/seed/dungeon/_registry/bands.v1.json:73-74`) | not an amount, not a source and not an extra roll: Owner ruling 2026-09-20 — it is the rarity **window** applied to one roll the quest **takes out of** its host's existing budget line (a world turn's claim roll, an expedition collect's tier roll; `npc-story-events/spec-outcome-routing.md` §3, `spec-quest-sources.md` §6). Total income is unchanged; the band reshapes which roll pays what |
| `scope` | PLANNED | `save · world` | not a delve scope |
| `expiry` | PLANNED | `host · none` | `host` = expires on the offering host's own clock (turns, collects or returns) by the runtime's tuning (`spec-quest-sources.md` §4); `none` for spine and arc quests. Never a length, never real time |
| `eligibility` | PLANNED const | `null` | a narrative quest is offered by a storylet outcome (`quest.offer`); the storylet's eligibility is the gate, so the quest carries none (one gate, not two) |
| `name`, `flavor` | AUTHORED | keyed text with tokens (`narrative-contract` §4; `token-grammar`) | never a number, never a literal name; `flavor` never states the target amount |

**Not in the anchor, by design:** the `need` count, the reward source, the expiry length, the giver and any target
id — each is the runtime's (`quest-sources` §3–§6; the giver is the offering storylet's cast, `quest-log-contract`
§3). This is the Delve anchor's discipline (`QuestRow.cs:5-14`) with two new scopes.

**3.1 Field mapping to `QuestRow` (Alignment 2026-09-20).** One quest engine: `quest-sources` loads each anchor into
the existing `QuestRow` (`gk-core/src/FusionRpg.Core/Delve/Quests/QuestRow.cs:23-30`) and validates it with the widened
`QuestCatalog.Load` (§1). The Delve's own reader (`gk-core/src/FusionRpg.Core/Delve/Quests/QuestSeedFile.cs:35-42`) reads a
bare object with `questId`/`objectiveTemplate`; this kind is enveloped (`narrative-contract` §2) and keeps its own field
names. The mapping, exact:

| Seed field (this contract) | `QuestRow` member / runtime | Rule |
|---|---|---|
| envelope `{schemaVersion, kind: "quest", _meta, entries: [one]}` | — | the loader unwraps it; `_meta` and `_provenance` are not loaded |
| `id` | `QuestId` | verbatim (the Delve file's `questId`) |
| `templateId` | `TemplateId` | verbatim (the Delve file's `objectiveTemplate`) |
| `targetRef` | `TargetRef` | `"none"` → `null`, as `QuestSeedFile.NoneToNull` does (`QuestSeedFile.cs:21`) |
| `countBand` | `CountBand` | `"none"` → `null` |
| `rewardBand` | `RewardBand` | verbatim |
| `scope` | `Scope` | verbatim (`save` or `world`) |
| `eligibility` (const `null`) | `Predicate` | `null` (always eligible; the offering storylet is the gate) |
| `expiry` | appended member `Expiry` (`host · none`) | new `init` member on `QuestRow`, default `none` for Delve rows |
| `name`, `flavor` | appended members `Name`, `Flavor` (`TextRef`, `spec-storylet-contract.md` §2) | keyed text; the Delve rows have none |
| `revision`, `status`, `provenance`, `tokens` | appended members, as on `EventRow` (`spec-storylet-contract.md` §2) | a tombstone anchor loads as not offerable |

`QuestRow` widens by appended, defaulted `init` members, so every existing constructor call and the Delve reader keep
compiling — the `EventRow` precedent. The mapping is owned here; `npc-story-events/spec-quest-sources.md` §2 cites it
rather than restating it.

**Offering.** A storylet names a quest through its outcome consequence `{kind: quest.offer, ref: quest:<id>,
param: none}` (Owner ruling 2026-09-19 (round 3), `spec-narrative-contract.md` §5, `spec-storylet-vocab.md` §3.5).
`validate_entry` on a storylet refuses a `quest:` ref that names no live quest anchor, and on a quest refuses a
`world`-scoped anchor offered only by storylets whose hosts are all non-world (a `world` quest needs a world to
belong to).

### 4. Call schema

| Call | Writes | Shows as `const` |
|---|---|---|
| `quest-text` | `name`, `flavor` | the whole anchor above, the template's description and negative clause, the declared tokens |

Every other field is PLANNED. No quest field is voted: the only model-written fields are text, so the named
vote set is empty and nothing is permuted. The schema carries the root `blocked` escape every call schema
needs (`spec-narrative-contract.md` §9; Audit 2026-09-19), and `name`/`flavor` carry `maxLength` from the
budget's `text.lengthBounds.quest.*` rows. The call runs inside
whichever pipeline's work order offers the quest (a storylet or arc link with a `quest.offer` outcome); adding it to
`storylet-pipeline`'s and `arc-pipeline`'s work orders is filed on those modules. Until then quests are authored
under `authored/quests/`, which passes the same validators.

### 5. The schema audit and `validate_entry`

`narrative_audit("quest")` applies all eight rules of `narrative-contract` §10 to the quest document and the
`quest-text` call schema. `validate_entry("quest", entry)` refuses, naming the field path: an unknown or missing key;
a template outside the registry; a `targetRef` that disagrees with the template's attribute (a kind ref on a
bound-at-offer template, `none` where a kind ref is required); a `countBand` on a count-less template or `none` on a
counted one; a scope outside `save · world`; a digit in text; a token outside the grammar or not declared.

### 6. `decisions.md` row

None of its own: the narrative quest is part of the storylet contract's row drafted in `spec-narrative-planner.md`
§1 and of NS1/NS3's one-engine and one-store rows (`npc-story-events-map.md`, *decisions.md rows*).

---

## Commands

```powershell
$env:PYTHONPATH = "gk-forge/tools/seedsmith"; python -m pytest tools/seedsmith/tests/test_narrative_quest_vocab.py -q
cd tools\seedsmith; python -m seedsmith narrative contract --print --kind quest
cd tools\seedsmith; python -m seedsmith narrative contract --audit
```

## Project structure

```text
data/seed/narrative/_registry/quest-objectives.v1.json            (new)
data/seed/narrative/quests/                                        (new) empty until a pipeline offers quests
data/seed/narrative/authored/quests/                               (new) empty
tools/seedsmith/seedsmith/adapters/narrative/quest_vocab.py        (new) reader, lawn-only refusal
tools/seedsmith/seedsmith/adapters/narrative/kinds.py              the fifth KindSpec
tools/seedsmith/seedsmith/adapters/narrative/schema.py             the quest document and `quest-text` call schema
tools/seedsmith/seedsmith/adapters/narrative/descriptions.py       FieldDoc per quest field
tools/seedsmith/seedsmith/adapters/narrative/validate.py           the §5 rules
tools/seedsmith/tests/test_narrative_quest_vocab.py                (new)
```

## Code style

`spec-storylet-vocab.md`'s reader style: read fresh, frozen views, refusals that name the file and the key.

## Testing strategy

Fixture anchors with invented ids and text; no test counts quests in the corpus.

| Test | Asserts |
|---|---|
| `every_template_has_description_and_negative` | both keys non-empty |
| `no_template_is_lawn_only` | a fixture row with `sources: [pvz]` is refused with `quest.objective-lawn-only`; every committed row has a standalone source |
| `template_ids_disjoint_from_the_delve_registry` | parsed against `gk-data/packs/fusion/data/seed/dungeon/_registry/objective-templates.v1.json` — no shared id |
| `template_ids_match_quest_sources` | the member list equals `spec-quest-sources.md` §3's list (a declaration; pinned with its reason) |
| `bands_close` | `countBand` and `rewardBand` values resolve to `bands.v1.json`; `none` only where §3 allows |
| `bound_at_offer_templates_carry_none` | `hold-sector` with a kind ref refused |
| `counted_rule` | a count-less template with a `countBand` refused, and the reverse |
| `ids_are_namespaced` | a generated id without `narrative-` and an authored id without `authored-` refused |
| `quest_offer_ref_resolves` | a storylet whose `quest:` ref names no live anchor is refused |
| `no_number_in_quest` | the audit finds no numeric field; `"defeat 30 creatures"` in `flavor` refused |
| `audit_is_clean_for_quest_schemas` | `narrative_audit("quest")` returns nothing |

## Boundaries

- **Always:** every template has a standalone source; every number is a band; one catalog on the runtime side.
- **Ask first:** a new template, source or target kind (each needs an evaluator arm in `quest-sources`); a quest
  with its own eligibility tree (a second gate).
- **Never:** a lawn-only objective; a real-time expiry or a length in the seed; a second quest catalog; a target id
  or reward amount written by the model.

## Success criteria

- [ ] The objective registry exists, loads and refuses a lawn-only row.
- [ ] `quest` is a registered kind; document and call schemas pass the audit.
- [ ] `validate_entry` accepts one fixture per template and refuses a violation of every §5 rule.
- [ ] Template ids are disjoint from the Delve's, so the runtime's widened `QuestCatalog.Load` sees one id set.

## Contradictions found (report; not fixed here)

1. **`quest-sources` §2 says `QuestCatalog.Load` "accepts the two new scopes when the caller passes them", with "no
   code change in the catalog"** (its Contradictions 2). Read against the code, the scope list is a parameter
   (`QuestCatalog.cs:87`, `:155`), but two other rules are not: the target-ref rule hard-codes the kinds that need a
   ref (`:120`) and the count-less list is a literal (`:57-61`). Widening therefore needs the three runtime changes
   in §1, filed on `quest-sources`. It is still one engine.

## Open questions

None.

## Design-gate checklist

```
[x] Subsystems: quests (the Delve engine, widened), seedsmith narrative adapter, standalone rule.
[x] Read this session: narrative-seed map (§2, §4 gap entry, §6, §7), spec-narrative-contract, spec-storylet-vocab,
    npc-story-events/spec-quest-sources and spec-quest-log-contract in full; code: QuestCatalog.cs, QuestRow.cs,
    ObjectiveTemplateCatalog.cs, gk-data/packs/fusion/data/seed/dungeon/_registry/objective-templates.v1.json and bands.v1.json, a
    committed Delve quest anchor.
[x] Every claim cites file:line, checked against code.
[x] No population pinned: the template list is a declared closed vocabulary; the quest corpus is a reading.
[x] One engine: widens QuestCatalog; no second catalog.
[x] Standalone-first enforced structurally (the lawn-only refusal).
[ ] Registry row: the lawn-only refusal is guarded on the runtime side by quest-sources' row
    ns-quest-no-lawn-only-objective; the seed-side test above mirrors it, no new row.
```

---

## Standards audit (2026-09-19)

Independent adversarial review against `docs/research/ai-native-generation/README.md` §10, seedsmith P1–P5,
`seedsmith/spec-pipeline.md` §3, `spec-quality-gates.md`, `spec-workflow-runtime.md`, `validation-ssot.md`,
`tunables-ssot.md`, `item/seed-contract.md` §2–§7, `DESIGN-GATE.md` §3/§5, owner rulings R1–R13 and IC-3, and
the runtime contracts (`npc-story-events/spec-storylet-contract.md`, `spec-narrative-text.md`). Every change
in the body is marked "Audit 2026-09-19" (or "Owner ruling 2026-09-19 (round 4)" where the owner ruled).

| # | Severity | Finding | Status |
|---|---|---|---|
| 1 | low | `quest-text` lacked `blocked`, `maxLength` and an explicit (empty) vote set | fixed |
| 2 | low | Seed field names differ from `QuestRow` (`QuestId`, `Predicate`); the runtime maps them | **closed — Alignment 2026-09-20:** the exact mapping is §3.1 here (the seed owns its shape); `quest-sources` §2 cites it |
| 3 | low | Citations sampled: `QuestRow.cs:23-30`, `QuestCatalog.cs:84-92/:155-157`, `ObjectiveTemplateCatalog.cs:5-12`, `bands.v1.json:33-35/:68-75` — resolve | verified |

## Cross-lane alignment (2026-09-20)

- Alignment 2026-09-20: §3.1 states the exact seed-field → `QuestRow` mapping (verified against
  `gk-core/src/FusionRpg.Core/Delve/Quests/QuestRow.cs:23-30` and `QuestSeedFile.cs:21-42`); `quest-sources` cites it.
- Owner ruling 2026-09-20 (rewards come out of the host budget): `rewardBand` is the window on a roll the quest takes
  **out of** its host's budget line, never an added roll (§3 table; `npc-story-events/spec-outcome-routing.md` §3).
