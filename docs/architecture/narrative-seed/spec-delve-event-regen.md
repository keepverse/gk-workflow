# Spec: `delve-event-regen`

**Program:** [narrative-seed](../narrative-seed-map.md) · **Module id:** `delve-event-regen` · **Map row:** 22 · **Wave:** 6
**Depends on:** `storylet-pipeline`, `gloss-fill`, `dungeon-generator-repair` · **Cross-program cutover:** `npc-story-events` (loader, live Delve path), `party-dungeon` (room archetype contract, the dungeon adapter's other kinds) · **Model calls:** yes (runs `storylet-pipeline`)
**Ideal:** [../narrative-seed-ideal.md](../narrative-seed-ideal.md) §4.4, §6.1 ("the dungeon event kind moves into it"), §6.9 ("hand-fixing the 54 events")
**Status:** spec phase, 2026-09-19. Map approved by the owner 2026-09-19. No build authorized.

---

## Objective

Regenerate the Delve's events as **storylets hosted in delve rooms**, under the widened contract, through
the one storylet generator — and retire the dungeon adapter's `dungeon-event` kind **in the same change**
that the Delve's runtime loader switches from `gk-data/packs/fusion/data/seed/dungeon/events/` to the storylet tree. After this
module there is one storylet generator and one storylet corpus; no Delve event is ever patched by hand
(map §2 principles 8 and 15).

**What this replaces.** Owner ruling 2026-09-19 (round 4): by this wave the legacy tree is no longer the
contaminated 54-event batch measured in map §3.4. Wave-0 `dungeon-generator-repair` has already regenerated
its non-story events clean — glossed briefs, the widened script check, climate planned — and keyed their
`name` and `flavor` (`spec-dungeon-generator-repair.md` §8–§9), so the live Delve shows clean, keyed legacy
text from day one. This module replaces that **clean legacy tree** with storylets, because the legacy
contract still cannot express choices, roles, per-choice conditions, arcs or tokenised text, and it
retires the `dungeon-event` kind so one storylet generator remains (map §2 principle 15). What happens to the
four committed legacy `story` events before this wave was the owner question in `spec-dungeon-generator-repair.md`;
Owner ruling 2026-09-20 answered it: Wave 0 regenerates them clean and keyed with their ids and committed (dangling)
`chainRef`s, so this cutover replaces them with the rest of the tree and the runtime's known-defect list for their
dangling chains empties in the same change.

**Why this is not a patch.** The legacy tree is generated data, so the only sanctioned change is a generator
(map §2 principle 8); the widened contract is a different generator, so the tree is regenerated, never
converted row by row. (Audit 2026-09-19: the earlier "why once, and now" paragraph — no route answers an
event, so regenerate only once — was superseded by the round-4 ruling and is removed.)

## Design

### 1. The regeneration

`narrative-planner` plans the Delve's cells — delve room host kinds × storylet kind × climate, legal per
`storylet-vocab`'s host-kind registry — with the first-ship target of two per cell (`narrative-planner` §2).
This module runs `storylet-pipeline` over exactly those items: no Delve-specific prompt, validator or
schema. Every regenerated storylet:

- carries `hosts[]` = one or more delve room host kinds and `climate` PLANNED (Audit 2026-09-19: was a
  singular `host`, which neither the contract nor the runtime has);
- has 2–4 choices, exactly one `leave`, and passes the structural gate (no lose-lose, no dominated choice,
  choice type relaxed or dilemma-with-upside, conditional value);
- carries glosses, never motifs, in its brief (`lore-packet`; the cause of the leak removed);
- passes the script check by Unicode script property on every text field (`script-check`);
- names every entity by token (`names-registry`, `token-grammar`).

**No chains in this corpus.** Delve story chains return as **arcs** hosted in delve rooms, generated as
units by `arc-pipeline` when their shapes are planned; a chain generated as loose storylets is how two
references came to dangle. The regenerated Delve storylets therefore carry no chain reference, and no
dangling link can exist.

### 2. What the cutover retires

The `dungeon-event` kind lives in the dungeon adapter today:

| Retired | Where |
|---|---|
| the event `KindSpec` and its entry in the kind list | `gk-forge/tools/seedsmith/seedsmith/adapters/dungeon/kinds.py` |
| the event schema, descriptions and ownership rows | `gk-forge/tools/seedsmith/seedsmith/adapters/dungeon/schema.py` (event levels; `climateAffinity` is AUTHORED at line 123 today and PLANNED after `dungeon-generator-repair`) |
| the event brief and prompt, the motif demand and the pinned outcome count, plus what `dungeon-generator-repair` adds for events (the event prompt version, the event script policy, the climate assignment in the dungeon planner — [spec-dungeon-generator-repair.md](spec-dungeon-generator-repair.md) §2–§5) | `gk-forge/tools/seedsmith/seedsmith/adapters/dungeon/briefs.py:324`, `:236`; `gk-forge/tools/seedsmith/seedsmith/adapters/dungeon/planner.py` |
| `run_event_draws` and its forged chain id | `gk-forge/tools/seedsmith/seedsmith/adapters/dungeon/pipelines.py:251`, `:310` |
| the completeness registration for the kind | `gk-forge/tools/seedsmith/seedsmith/adapters/dungeon/completeness.py:48` |
| the `dungeon-event` budget row | `gk-data/packs/fusion/data/seed/dungeon/_plan/budget.v1.json` (published as the next version without the row) |
| the committed event files | `gk-data/packs/fusion/data/seed/dungeon/events/**` — removed, never edited |

The legacy event ids are **retired, never reused** (map §10). Audit 2026-09-19: this paragraph recorded them
as tombstone rows in "`narrative-emit`'s tombstone ledger", but `narrative-emit` has no such ledger and its
tombstones are narrative rows (`storylet.*`, `character.*` …), while legacy ids live in the `event.*`
namespace. Reuse is instead impossible by construction — the narrative minter never issues an `event.*` id —
and the cutover run's report lists every retired legacy id, committed under
`data/seed/narrative/_runs/delve-cutover.json`. Saves may reference legacy ids once the live Delve answers
legacy events (round 4), so the runtime's pin rule for a retired legacy id is `npc-story-events`'
(`storylet-contract` §4: legacy rows have `revision 0` and are never pinned).

### 3. Cutover preconditions — one change, several owners

The retirement is only correct if every reader of the old tree moves in the same change. This program
edits none of the runtime files (map §7); each row below is its owner's edit, landed together:

| Precondition | Owner | Evidence of the dependency |
|---|---|---|
| The runtime loader reads `choices[]`, hosts, keyed text and eligibility from the storylet tree | `npc-story-events` `storylet-contract` (the widening of `EventSeedFile`/`EventRow`), with `party-dungeon`'s event deck reading it | the loader refuses any eligibility tree today (`gk-core/src/FusionRpg.Core/Delve/Events/EventSeedFile.cs:40-44`); `EventOutcomeRow` has no choices (`gk-core/src/FusionRpg.Core/Delve/Events/EventRow.cs:17-18`) |
| A room's pool is the storylets hosted in its room kind, not a list of event ids | `party-dungeon` (room archetype contract and event deck) | rooms reference events through `eventPool` as a reference field (`gk-forge/tools/seedsmith/seedsmith/adapters/dungeon/kinds.py:27`; `docs/architecture/party-dungeon/spec-dungeon-seed-contract.md` line 72), and the deck is the union of those pools (`docs/architecture/party-dungeon/spec-event-deck.md` §2) |
| Every storylet presents `leave` (NS7), superseding "leave only on `story`" | `npc-story-events` (`storylet-contract`, NS7; Audit 2026-09-19: was `party-dungeon`, before the round-3 transfer) | `gk-core/src/FusionRpg.Core/Delve/Events/EventChoices.cs:23-31` |
| Preflight fails on a dangling link | `npc-story-events` `storylet-contract` | today an unresolved `chainRef` is skipped (`gk-core/src/FusionRpg.Core/Delve/Events/EventDeckPreflight.cs:50-55`) |
| C# tests that read the old directory move to the storylet tree | the owners of those tests | `gk-core/tests/FusionRpg.Core.Tests/Delve/Events/EventSeedContentTests.cs:41`; `gk-core/tests/FusionRpg.Core.Tests/Delve/Domains/DomainEventPreflightBridgeTests.cs:38`; `gk-core/tests/FusionRpg.Core.Tests/Delve/Domains/DomainQuestPreflightBridgeTests.cs:45` |
| The generated-seed guard knows the narrative tree's generator | `narrative-emit` (if not already landed) | `gk-core/scripts/guard-generated-seed.py:68` maps only `gk-data/packs/fusion/data/seed/dungeon/` to the dungeon adapter |
| The release scan's scope covers the narrative tree | `ip-censor` | the narrative surfaces are already named in `docs/architecture/ip-censor/spec-registry.md`; IC-3 makes the scan a release gate, never a generation blocker |

`narrative delve cutover --check` verifies the seed-side preconditions mechanically (§Commands) and lists
the runtime ones as a checklist the change's reviewers tick; it never reports the runtime rows as done on
its own say-so.

### 4. Call budget

`docs/research/ai-native-generation/README.md` §9, via the call-shape table (`narrative-planner` §7):

```text
base  = C x 2 x 4      (C = legal Delve cells, 2 per cell first ship, 4 calls per storylet)
worst = C x 2 x 12
```

Illustration, not an assertion: at the ideal's 42 Delve cells (a reading), 84 storylets cost 336 base calls
and at most 1,008. `narrative delve regen --dry-run` prints the real figure.

### 5. Readings after the run (printed by `report`, never asserted)

The share of Delve storylets whose text leaks a foreign script (expected zero, reported, not asserted;
map §10 — the legacy tree already reads zero after the round-4 regeneration); climate distribution per host; choice-kind and choice-type
distribution; calls spent, repairs per defect, `unresolved` per voted field.

### 6. Tunables

None of its own. Coverage rows are `narrative-planner`'s; call and temperature settings are
`storylet-pipeline`'s.

## Commands

```powershell
$env:PYTHONPATH = "gk-forge/tools/seedsmith"; python -m pytest tools/seedsmith/tests/test_narrative_delve_regen.py -q
cd tools\seedsmith; python -m seedsmith narrative delve regen --dry-run         # DEFAULT: plans the Delve cells, renders every prompt, prints calls
cd tools\seedsmith; python -m seedsmith narrative delve regen --write --limit 12 # a small batch first, reviewed, then the rest
cd tools\seedsmith; python -m seedsmith narrative delve cutover --check          # seed-side preconditions; runtime ones listed for review
cd tools\seedsmith; python -m seedsmith report --adapter narrative --corpus ..\..\data\seed\narrative
```

## Project structure

```text
tools/seedsmith/seedsmith/adapters/narrative/delve.py                 (new) Delve plan filter, regen driver, cutover check
gk-forge/tools/seedsmith/seedsmith/adapters/dungeon/kinds.py                   event KindSpec removed (cutover change)
gk-forge/tools/seedsmith/seedsmith/adapters/dungeon/schema.py                  event rows removed (cutover change)
gk-forge/tools/seedsmith/seedsmith/adapters/dungeon/briefs.py                  event brief removed (cutover change)
gk-forge/tools/seedsmith/seedsmith/adapters/dungeon/pipelines.py               run_event_draws removed (cutover change)
gk-forge/tools/seedsmith/seedsmith/adapters/dungeon/planner.py                 event climate assignment and event targets removed (cutover change)
gk-forge/tools/seedsmith/seedsmith/adapters/dungeon/completeness.py            dungeon-event registration removed (cutover change)
gk-data/packs/fusion/data/seed/dungeon/_plan/budget.v1.json                                superseded by the next version without the event row
gk-data/packs/fusion/data/seed/dungeon/events/**                                           removed in the cutover change
tools/seedsmith/tests/test_narrative_delve_regen.py                   (new)
```

The dungeon adapter edits are the retirement of one kind inside `party-dungeon`'s adapter, made in the same
change as that program's own runtime edits; the adapter's six other kinds are untouched (map §7).

## Code style

```python
def cutover_check(narrative_root: Path, dungeon_root: Path) -> CutoverReport:
    """Seed-side preconditions only, each a named pass/fail: every planned Delve cell holds its
    first-ship count; no Delve storylet carries a chain reference; the dungeon adapter registers no
    dungeon-event kind; no file remains under dungeon/events; every legacy id is listed as retired.
    Runtime preconditions are returned as an unticked checklist, never as passes."""
```

## Testing strategy

Fixture corpora and a scripted transport that raises when exhausted or called unexpectedly.

| Test | Asserts |
|---|---|
| `dry_run_makes_no_call` | the Delve plan and every prompt render with a transport that raises |
| `uses_only_the_storylet_pipeline` | the regen driver calls `storylet-pipeline`'s entry point and defines no prompt, schema or validator of its own |
| `climate_is_planned_for_every_delve_storylet` | every regenerated fixture storylet has a PLANNED climate |
| `no_chain_reference_in_delve_storylets` | no regenerated Delve storylet carries a chain or arc link |
| `legacy_ids_are_retired_and_never_reissued` | after a fixture cutover, every legacy event id is in the retired list, and the narrative minter cannot produce an `event.*` id |
| `dungeon_adapter_kinds_after_cutover` | the dungeon adapter's kind list no longer contains `dungeon-event` and still contains its six other kinds (a closed vocabulary; the membership is the declaration) |
| `cutover_check_fails_on_leftover_event_file` | one file left under a fixture `dungeon/events/` fails the check naming it |
| `cutover_check_never_passes_runtime_rows` | runtime preconditions are always returned unticked |
| `no_brief_contains_a_raw_motif` | every rendered Delve prompt passes the script check (the committed leak's cause) |

No test asserts the number of regenerated storylets, the number of legacy events, or any generated text.

## Success criteria

1. The Delve's storylets are generated by `storylet-pipeline` under the widened contract, with climate
   planned, every choice structurally gated, and every text field script-clean and tokenised.
2. In one change: the narrative Delve storylets land, the `dungeon-event` kind and its files — the clean,
   keyed tree `dungeon-generator-repair` regenerated — are gone, legacy ids are listed retired, and every
   runtime reader of the old tree has moved (its owners' edits).
3. No Delve storylet carries a chain reference; chains return later as arcs.
4. The suite passes with the model transport stubbed to raise.

## Boundaries

- **Always:** regenerate through `storylet-pipeline`; retire the old kind and switch its readers in one
  change; list legacy ids as retired; run a small reviewed batch before the rest.
- **Ask first:** landing the retirement before every runtime precondition is met (it would leave the Delve
  loader reading a deleted tree); regenerating Delve chains as loose storylets.
- **Never:** hand-edit a legacy event or a regenerated storylet; edit `gk-core/src/FusionRpg.Core/Delve/**`,
  `DelveWildEndpoints.cs` or any runtime file from this program (map §7); keep two event generators alive
  after the cutover; move the dungeon adapter's other six kinds.

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
| 1 | medium | Round-4 propagation: it now replaces a clean, keyed legacy tree; the "why once, and now" rationale was obsolete | fixed |
| 2 | medium | Legacy `event.*` ids cannot be `narrative-emit` tombstone rows (no such ledger; different namespace) | fixed (retired list; namespace makes reuse impossible) |
| 3 | low | Singular `host` where the contract has `hosts[]`; NS7 owner still `party-dungeon` | fixed |
| 4 | low | Call budget matches the call-shape table (4 base, 12 worst per storylet) | verified |
