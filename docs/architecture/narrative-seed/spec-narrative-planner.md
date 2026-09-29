# Spec: `narrative-planner`

**Program:** [narrative-seed](../narrative-seed-map.md) · **Module id:** `narrative-planner` · **Map row:** 16 · **Wave:** 4
**Depends on:** `narrative-contract`, `narrative-metrics`, `arc-shapes`, `lore-packet` · **Model calls:** none
**Ideal:** [../narrative-seed-ideal.md](../narrative-seed-ideal.md) §6.2 (patterns), §6.6 (plan step), §6.7 (budget and call cost), §11 item 7
**Status:** spec phase, 2026-09-19. Map approved by the owner 2026-09-19. No build authorized.

---

## Objective

Decide, with a pure function and before any model call, **what** narrative content is written, **in what
order** and **under which constraints** (seedsmith P4). The planner fixes every PLANNED field: ids, cells,
choice-slot patterns, arc shapes, species picks for characters and spine chapter slots. No model decides
what work to do, what kind of decision a storylet is, or which climate it lives in.

Its second job is cost honesty: `narrative plan --dry-run` renders every prompt and prints the call count
and time estimate **before anything is spent**, so the Wave 5 spend is approved against a printed number,
not an estimate in a document (map §6).

## Design

### 1. Cells

| Seed kind | Cell | Legality from |
|---|---|---|
| storylet | host kind × storylet kind × climate | `storylet-vocab`'s host-kind registry (which storylet kinds a host admits, and which climates it presents — Owner ruling 2026-09-20 (round 5): `climateSource`/`climates`, §3.1, ~~derived for world hosts from `sector-climates.v1.json`~~ Owner ruling 2026-09-20 (round 6), R20: world hosts present all seven, their site climate being the sector's own) |
| character | side × role, with element as a spread dimension inside the cell | `character-vocab` (role list, and the enemy-side restrictions of R13) |
| arc | arc shape × host kind | `arc-shapes` (each shape names each link's host kind) |
| spine chapter | spine chapter slot | `arc-shapes`' spine frame (one slot per time-machine piece, R3) |
| lead character | lead token | the names registry's lead rows (R11) |

**Climate is PLANNED.** The committed Delve corpus left climate to the model and got 39 of 54 events at
`none` and none at ice, earth or light (map §3.4). Here climate is a cell dimension over the six elements
plus `none`, fixed per work item and shown to the model as `const`.

**The Delve's hosts.** A delve room kind is a host. Which storylet kinds each room kind admits is
`storylet-vocab`'s registry data, seeded from the Delve's existing kind-fit rule (`curio → curio`,
`shrine → shrine`, `trap → trap`, `merchant → bargain`, `wild → story`, `rest → encounter-event`,
`unknown → any`; `docs/architecture/party-dungeon/spec-event-deck.md` §2 rule 1, line 92). The dry run
prints the resulting cell count; the ideal's hand count of 42 Delve cells (ideal §6.7) is a reading to be
reproduced or explained, never asserted.

**Other places.** World, expedition and homeworld hosts are not defined yet (map §9; ideal §11 item 7).
The planner computes their grids the same way once `storylet-vocab` lists their host kinds; until then no
coverage row is declared for them and their cells do not exist. (Alignment 2026-09-20 added their rows.) Owner
ruling 2026-09-20 (round 5): **R19 — world grids have climate cells.** A host's climate cells are its legal climates
in `storylet-vocab` §3.1: `room` hosts (the Delve) take all seven; `sector-type` hosts (the seven `world.*` rows)
take exactly their `climates` list, the image of `sector-climates.v1.json` (§3.9) over the sector types that can hold
that slot — for example `world.tear` × {`air`, `fire`}, `world.wildland` × {`none`, `earth`, `air`, `fire`, `dark`};
a `sector-type` host with an empty list (`world.anomaly` today) gets no cell; `none` hosts (`sanctum.hub`,
`expedition.return`, the neutral Delve rooms) take `none` only. A storylet naming several hosts is planned only at a
climate every named host admits. The dry run prints the grid; its cell count is a reading. Owner ruling 2026-09-20 (round 6): **R20** —
the `sector-type` column and its per-host image are retired; the `world.*` rows are `climateSource: sector` and take
**all seven** climate cells like the Delve's `room` hosts, because a world sector's climate is its own authored
`WorldSector.Climate`, which can be any element (the image examples above are superseded).

**This changes the approved dungeon contract.** Its event cell is kind (6) × planning theme (8) = 48
(`docs/architecture/party-dungeon/spec-dungeon-seed-contract.md` line 78). Draft `decisions.md` row, to
be appended in the change that lands this module (map §11 item 1):

> **Narrative seed adapter and the storylet contract** (narrative-seed, 2026-09-19). The Delve event anchor
> widens into the storylet contract (`choices[]`, roles, per-choice conditions and outcomes); the
> `dungeon-event` kind moves from the dungeon adapter to the `narrative` adapter; the event cell grid
> changes from kind × planning theme to host × kind × climate, with climate PLANNED. Amends
> `party-dungeon/spec-dungeon-seed-contract.md` §1.4.

### 2. Coverage targets — declared, never guessed

Targets live in the narrative generation budget, `gk-data/packs/fusion/data/seed/narrative/_plan/budget.v1.json` (new), as
`BudgetRow`s (`gk-forge/tools/seedsmith/seedsmith/budget/model.py:37`: `dimension`, `target`, asymmetric
`tolerance`, `derivation`, `rationale`). `narrative-metrics` reports actual against them per cell.

| Row | First ship per cell | Full target | Derivation and rationale |
|---|---|---|---|
| storylet × Delve cell | 2 | pending pulse rates | first ship: the ideal's first batch (ideal §6.7, "2 per Delve cell"), and the owner's phased rollout (*"small-batch-then-playtest before the full run"*, map §6). Full target: the repetition budget below |
| character × (side, role) | 3 | 3 | the roster research's comfortable density of about three per cell (ideal §6.7) |
| arc × shape | 1 | 1 | one arc per shape proves every shape end to end; more arcs follow playtest readings |
| spine × chapter slot | 1 | 1 | the spine is finite: one chapter per slot (R3) |
| lead character | 1 per lead | 1 per lead | three leads (R11) |

**The repetition budget** (ideal §6.7, CK3's lesson): a pool of `T` once-per-save storylets on a host
that fires `P` times per session lasts `T / P` sessions before the first repeat. The full target per cell
is

```text
T_cell = max(firstShipPerCell, ceil(P_host × S / cellsOnHost))
```

where `P_host` is the host's expected storylet draws per session (a runtime tunable owned by
`npc-story-events` in `gk-core/data/tuning/narrative.v1.json`, new), `cellsOnHost` is the host's legal cell
count, and `S = coverage.sessionsBeforeFirstRepeat` is this program's declared goal. Until
`npc-story-events` publishes `P_host`, the full-target row carries `derivation: pending-pulse-rates` and
`Narrative/CellCoverage` measures against the first-ship target only; nothing guesses `P_host`.

### 3. Choice-pattern allocation

Every storylet work item gets a choice pattern from `storylet-vocab`'s pattern registry (two unconditioned
options plus zero to two conditional ones; ideal §6.2), legal for its host and kind. Fixed slots are what
make each slot's fields votable by position — the fix for the dungeon adapter's pinned outcome count
(`gk-forge/tools/seedsmith/seedsmith/adapters/dungeon/briefs.py:236`, reason at lines 227–235).

Allocation is deterministic and meets the choice-kind floors (`distribution.choiceKind.<kind>.floorPermille`,
owned by `narrative-metrics`):

1. Order the storylet work items by `blake2b(storyletId)`.
2. For each item, among its legal patterns, pick the one that most reduces the largest remaining
   floor shortfall; ties break by pattern id order.
3. Before allocating, prove the floors are reachable: a pigeonhole check, then the existing matching check
   (`check_feasibility`, `gk-forge/tools/seedsmith/seedsmith/planner/feasibility.py:84`) over kind demands against
   legal slots. An infeasible plan is refused with the binding kind and the cells that could have held it
   named — never a partial plan.

**Teaching allocation (Owner ruling 2026-09-20: story is also the tutorial).** After patterns are fixed, each
storylet-carried `teaches` value (`storylet-vocab` §3.8) is assigned to storylet work items whose host, pattern and
planned consequences meet its `requires` — deterministically, in `blake2b(storyletId)` order, at least one item per
value per legal host family, ties by value order. The value lands in the item's PLANNED `teaches`
(`narrative-contract` §5). A value no legal item can carry is a named planning refusal, never dropped silently.
**Study-site raids (Alignment 2026-09-20):** a storylet allocated to the counter-doctrine raid cells (hosts
`world.anomaly`, `world.vault` once those rows exist, `storylet-vocab` §3.1) gets the PLANNED `eligibility`
`[{id: "doctrine-studying", arg: "none"}]` (`npc-story-events/spec-counter-doctrine.md` §5).

### 4. Species picks for characters

For each (side, role) cell and slot: the candidates are species of that side whose anchors are committed,
minus species already holding a character (one character per species, ideal §6.3), minus species the
role's R13 restriction excludes. Slots cycle through the elements in the element vocabulary's order so a
cell's characters spread across elements; within an element, the species is the first candidate in the
order `blake2b(cellKey | slotIndex | speciesId)`. A cell with too few candidates is refused with the cell
named. Lead characters are planned from the names registry's lead rows, not species-picked.

### 5. Arcs and the spine

- **Arcs.** One work order per arc: its shape, and for every link a storylet work item whose host kind,
  flags set and read, persistent roles and `arcRef`/`arcLink` are copied from the shape as PLANNED `const`.
  All links of one arc are **one unit of work** (§6), so a link can never point past its arc — the
  dangling-chain defect of the committed corpus (the forged `-{n+1}` id at
  `gk-forge/tools/seedsmith/seedsmith/adapters/dungeon/pipelines.py:310`) becomes structurally impossible.
- **Spine.** One work order per chapter slot in the spine frame, with the frame's scene count, beat count
  per scene, speaker slot per beat and cast per chapter as PLANNED `const` (R1: the planner owns the
  structure; the model writes inside it).

### 6. The work order

Output: `data/seed/narrative/_plan/plan.v{n}.json` (new), canonical JSON, committed. Each item:

| Field | Meaning |
|---|---|
| `itemId` | stable work-item id |
| `kind` | `storylet · character · arc · spine-chapter · lead-character` |
| `plannedId` | the seed id, minted `<namespace>.<cellKey>-<nnn>`, continuing from the high-water mark; tombstoned ids are never reissued (read from `narrative-emit`'s tombstone rows). Audit 2026-09-19: the namespace is `narrative-contract` §3's (`lead-character` items mint in `character`), and `cellKey` joins its dimensions with hyphens and begins with a letter, so the body matches `[a-z][a-z0-9-]*` (a dotted cell key would have broken the id grammar and `token-grammar`'s slug) |
| `planned` | every PLANNED field value, shown to the model as `const` — including, for an arc link, each `flagsSet` flag's pinned outcome position and the `eligibility` built from `flagsRead`, and for any item the quest anchor or spine scene a `quest.offer` or `scene.play` outcome may name (the inputs `narrative-contract` §5's `ref` rule reads; Audit 2026-09-19) |
| `unit` | the arc id for arc links (all items of one unit run in one pipeline invocation), else the item itself |
| `packetInputs` | the inputs `lore-packet` needs (species, host, climate, cast tokens) |
| `permutationKey` | the entity id `order_for` seeds from (`gk-forge/tools/seedsmith/seedsmith/adapters/creatures/anchor/permute.py:26`) |
| `callShape` | `{kind}` reference into the call-shape table (§7) |

Order: characters before storylets and arcs (a storylet may cast a planned character, and its packet
needs that character's token); leads before the spine; arcs as units. The order is derived from these
references, never written as a stage list.

Adding a cell to a later plan version must not rewrite any existing item's constraints, so a plan change
stales only the new items (the dungeon precedent, `docs/architecture/party-dungeon/spec-dungeon-seed-contract.md`
§6).

### 7. The call table and the dry run

**One call-shape table** — `tools/seedsmith/seedsmith/adapters/narrative/call_shape.py` (new) — declares
per kind how many calls a pipeline makes. It is structural (it describes pipeline shape, not a balance
value), each row commented with the pipeline spec that owns it, and the pipelines import it, so the dry
run and the pipelines cannot disagree. Formula (`docs/research/ai-native-generation/README.md` §9):
`entries × pipelines + entries × voted calls × (samples − 1)`, with repairs as a separate bound.

| Kind | Base calls per entry | Worst case per entry | Owning spec |
|---|---|---|---|
| storylet | 2 pipelines + 1 voted call × 2 = **4** | 3 structure draws × 3 samples + 3 text attempts = **12** | `storylet-pipeline` |
| character (texture) | identity 1 + anchors 1 + lines `B` + 1 voted call × 2 = **4 + B** (8 at the 4-band ladder) | identity 9 + anchors 3 + lines 3B = **12 + 3B** | `character-pipeline` |
| lead character | as texture with 2 anchor candidates = **5 + B** | **15 + 3B** | `character-pipeline` |
| arc | 1 premise + `L` × storylet = **1 + 4L** | **3 + 12L** | `arc-pipeline` |
| spine chapter | 2 candidates × (1 chapter call + `s` scene calls) = **2 + 2s** | **6 + 6s** | `spine-pipeline` |
| gloss chunk | 1 per chunk of `gloss.chunkSize` motifs | **3** per chunk | `gloss-fill` (runs in Wave 0 — Owner ruling 2026-09-19 (round 4) — so its row is used by `gloss fill --dry-run`, not by the narrative plan's total) |

`B` is the number of disposition bands with required lines (`character-vocab`), `L` the link count of the
shape, `s` the scene count of the chapter slot. The estimate prints base calls plus the heal allowance,
and the worst case separately.

**Illustration, not an assertion** (the ideal's first-batch shape, recomputed with the table above): 84
storylets × 4 = 336; 54 characters × 8 = 432; 6 arcs × (1 + 4 × 4) = 102; base 870 calls, about 1,000 with
a 15% heal allowance, about an hour at the dungeon spec's 3.7 s per call. The dry run replaces this with the
real figure from the real plan.

**The dry run** (`narrative plan --dry-run`, the default mode):

1. Builds the plan in memory; runs every feasibility check.
2. Builds every item's lore packet (refusals are reported per item, never skipped).
3. Renders every prompt: from Wave 5, each pipeline registers a prompt renderer for its kinds; before a
   kind's pipeline exists, its items render the packet and the constraint block and are reported as
   `prompt renderer not registered`, never silently omitted.
4. Prints, per kind and in total: items, base calls, heal allowance, worst case, estimated wall time,
   and the configured per-run call cap; exits non-zero if the base estimate exceeds the cap.
5. Makes no model call — proven by a test whose transport raises.

### 8. Tunables

Budget file `gk-data/packs/fusion/data/seed/narrative/_plan/budget.v1.json` (new): the coverage rows of §2, plus:

| Key | Unit | Starting value | Rationale |
|---|---|---|---|
| `coverage.sessionsBeforeFirstRepeat` | sessions | 3 | a player should not meet the same texture storylet twice on one host within their first three sessions; revised from `npc-story-events`' first-repeat reading |
| `calls.capPerRun` | calls | 1,500 | above the first batch's estimated ~1,000 with headroom for heals; a loop bug costs one cap, not a budget (`seedsmith/spec-pipeline.md` §7) |
| `calls.healAllowancePermille` | ‰ of base calls | 150 | the dungeon contract's measured allowance (`spec-dungeon-seed-contract.md` §7) |
| `calls.secondsPerCallEstimate` | seconds | 3.7 | the local-model rate the dungeon contract uses; replaced by the run ledger's measured mean once a run exists |

## Commands

```powershell
$env:PYTHONPATH = "gk-forge/tools/seedsmith"; python -m pytest tools/seedsmith/tests/test_narrative_planner.py -q
cd tools\seedsmith; python -m seedsmith narrative plan --dry-run           # DEFAULT: plan in memory, render prompts, print the call table, call nothing
cd tools\seedsmith; python -m seedsmith narrative plan --dry-run --kind storylet --sample-prompt 3
cd tools\seedsmith; python -m seedsmith narrative plan --write             # commit plan.v{n}.json; model-free
```

## Project structure

```text
tools/seedsmith/seedsmith/adapters/narrative/planner/__init__.py     (new)
tools/seedsmith/seedsmith/adapters/narrative/planner/cells.py        (new) §1 legality and cells
tools/seedsmith/seedsmith/adapters/narrative/planner/patterns.py     (new) §3 allocation and feasibility
tools/seedsmith/seedsmith/adapters/narrative/planner/species.py      (new) §4 species picks
tools/seedsmith/seedsmith/adapters/narrative/planner/work_order.py   (new) §5–§6 items, ids, ordering
tools/seedsmith/seedsmith/adapters/narrative/call_shape.py           (new) §7 structural call table
tools/seedsmith/seedsmith/adapters/narrative/planner/dry_run.py      (new) §7 renderer registry and report
gk-data/packs/fusion/data/seed/narrative/_plan/budget.v1.json                             (new) coverage rows and calls block
data/seed/narrative/_plan/plan.v1.json                               (new) the committed work order
tools/seedsmith/tests/test_narrative_planner.py                      (new)
```

## Code style

```python
def plan(regs: "NarrativeRegistries", budget: "NarrativeBudget", history: "IdHistory") -> WorkOrder:
    """Pure: no clock, no random state, no model. Same inputs, same bytes. Refuses an infeasible
    plan naming the binding constraint; never returns a partial plan."""
```

## Testing strategy

Fixture registries and budgets only; the model transport stubbed to raise.

| Test | Asserts |
|---|---|
| `plan_is_deterministic` | two plans from the same inputs are byte-identical |
| `climate_is_planned_const` | every storylet item carries `climate` as a PLANNED value; the rendered schema pins it as `const` |
| `cells_follow_host_legality` | a host admitting one kind yields cells only for that kind; a climate-neutral host yields only `none` cells; ~~a `sector-type` host yields exactly its `climates` cells and none when the list is empty (Owner ruling 2026-09-20 (round 5), R19)~~; a `sector` host (world) yields all seven climate cells (Owner ruling 2026-09-20 (round 6), R20) |
| `undefined_hosts_have_no_cells` | a host kind absent from the registry produces no cell and no budget row |
| `pattern_floors_met_or_refused` | a fixture where floors are reachable meets every floor; an unreachable fixture is refused naming the kind |
| `species_one_character_each` | no species receives two characters; R13-excluded species never receive an enemy-side role |
| `species_spread_across_elements` | a cell of three slots with candidates in three elements picks three elements |
| `arc_links_are_one_unit_and_close` | every link's `arcRef` names its own arc; no link references an id outside the unit |
| `ids_continue_and_skip_tombstones` | a new plan continues from the high-water mark and never reissues a tombstoned id |
| `minted_ids_match_the_contract_grammar` | every `plannedId` is `<namespace>.<body>` with the body matching `[a-z][a-z0-9-]*`; `lead-character` items mint under `character` (Audit 2026-09-19) |
| `arc_link_flag_positions_are_planned` | each `flagsSet` flag is pinned to one non-`leave` outcome position in slot, then outcome, order |
| `adding_a_cell_stales_nothing_else` | plan v2 with one extra cell leaves every existing item's constraints byte-identical |
| `dry_run_makes_no_call` | the dry run completes with a transport that raises on any call |
| `dry_run_reports_unregistered_renderers` | with no pipeline registered, every item is listed as `prompt renderer not registered` |
| `dry_run_call_table_matches_formula` | on a fixture plan, printed base and worst-case calls equal the call-shape formula per kind |
| `over_cap_exits_non_zero` | a fixture whose base estimate exceeds `calls.capPerRun` exits non-zero |
| `call_shape_is_single_source` | each pipeline's call accounting imports `call_shape`; no pipeline re-declares a count |

No test asserts the committed plan's item count, cell count or call total.

## Success criteria

1. `narrative plan --dry-run` builds the plan, renders every packet and every registered prompt, and prints
   the call table without a model call.
2. Climate, choice-slot patterns, species, arc links and spine structure are all PLANNED `const`.
3. An infeasible plan is refused with its binding constraint named.
4. The committed plan is byte-identical on rerun, and a new cell stales only new items.
5. The `decisions.md` row in §1 is appended in the change that lands this module.

## Boundaries

- **Always:** plan before any call; derive order from references; refuse rather than return a partial plan;
  print the cost before spending; keep targets in the budget file with a stated derivation.
- **Ask first:** declaring a full target before `npc-story-events` publishes pulse rates; raising
  `calls.capPerRun` beyond the first-batch size; planning cells for a host the runtime has not defined.
- **Never:** let a model choose a cell, a climate, a choice kind or a species; guess a runtime pulse rate;
  reuse a tombstoned id; write a stage list by hand.

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
| 1 | medium | Minted ids `<kind>.<cellKey>-<nnn>` could carry dots and a `lead-character` namespace the contract lacks | fixed |
| 2 | medium | The planned inputs `ref` derivation needs (flag positions, quests, scenes) were not in the work item | fixed (§6 `planned`) |
| 3 | low | Gloss chunks now run in Wave 0 | fixed (call table note) |
| 4 | low | Quest anchors are not yet planned work items (`spec-quest-vocab.md` §4 files it) | deferred — plan task |
| 5 | low | Dry run, call cap, deterministic plan, no population asserted (README §9) | verified |

## Cross-lane alignment (2026-09-20)

- Owner ruling 2026-09-20 (story is also the tutorial): §3 allocates each storylet-carried `teaches` value to items
  that meet its `requires`; the spine's teaching values come from the frame (`arc-shapes` §5).
- Alignment 2026-09-20: study-site raid storylets carry the eligibility condition `doctrine-studying`, the seed side
  of the runtime's `DoctrineStudying` leaf (`npc-story-events/spec-narrative-predicates.md` §5).
