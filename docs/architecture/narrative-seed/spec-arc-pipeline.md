# Spec: `arc-pipeline`

**Program:** [narrative-seed](../narrative-seed-map.md) · **Module id:** `arc-pipeline` · **Map row:** 20 · **Wave:** 5
**Depends on:** `storylet-pipeline` (and through it the planner, validators, emit, lore packet and model config) · **Model calls:** yes
**Ideal:** [../narrative-seed-ideal.md](../narrative-seed-ideal.md) §6.4 (the arc contract), §6.6; `npc-story-events-ideal.md` §6.12 (R13)
**Status:** spec phase, 2026-09-19. Map approved by the owner 2026-09-19. No build authorized.

---

## Objective

Generate an **arc** — three to five linked storylets with a cast that persists across links — as one unit:
first the arc's name and premise inside its planned shape, then every link through `storylet-pipeline` in
the **same work order**. A link can therefore never point past its arc: the committed corpus's defect, two
of four story `chainRef`s pointing at events that do not exist because the planner forged the last id
(`gk-forge/tools/seedsmith/seedsmith/adapters/dungeon/pipelines.py:310`; map §3.4), becomes structurally impossible
rather than merely detected.

The shape is authored and model-free (`arc-shapes`); the model writes identity inside it (ideal §6.4).

## Design

### 1. The unit

`narrative-planner` emits one work-order **unit** per arc: the arc item plus one storylet item per link,
each link's host kind, persistent roles, flags set and read, and `arcRef`/`arcLink` copied from the shape
as PLANNED `const` (`narrative-planner` §5). This module runs the unit end to end:

```text
arc premise call  ->  link 1 (structure, text)  ->  link 2  ->  ...  ->  link L  ->  emit the whole unit
```

**All or nothing at emit.** The unit is emitted only when the premise and every link are accepted. If any
link ends `unresolved`, nothing of the arc reaches the corpus; the accepted parts stay in the run ledger so
a TRANSIENT resume re-uses them, and the unresolved link is reported with its reason. A half-emitted arc is
how a dangling link reaches a player, so it cannot exist.

### 2. The premise call

**Shown:** the shape's description (its beats, e.g. `rescue`: rumor → search → confrontation → aftermath),
the persistent roles with their descriptions, each link's host kind, and a lore packet built for the arc
(the cast tokens the arc may use, glosses for the places its links visit).

**Written** (AUTHORED, keyed): `name`, `premise`. Single sample: prose has no vote (ideal §6.6: *"shape is
planned; premise unvoted"*). Validated by `narrative-validators`' text battery; at most two repairs, then the
whole unit is `unresolved`.

### 3. Links

Each link runs `storylet-pipeline` unchanged, with three additions that come from the unit, never from the
model:

| Addition | How |
|---|---|
| **Cast once, reused** | the persistent roles — `roleId`, `kind`, `allegiance` and `requires` — are copied verbatim from the shape (`spec-arc-shapes.md` §2; `spec-narrative-contract.md` §7 `cast[]`) into every link that uses them as PLANNED `const`; no structure call writes them. Audit 2026-09-19: this row had link 1's structure call write `requires[]`, which contradicted the shape registry that already declares them. The runtime casts them when the arc starts and later links read the same cast (ideal §6.4) |
| **Flags** | each flag in a link's `flagsSet` is pinned by the planner to one outcome position as a `const` consequence `{kind: story.flag, ref: flag:<id>, param: none}` — flags in `flagsSet` order take the non-`leave` slots' outcomes in slot, then outcome, order; a pinned position is `const` in all three samples and leaves the vote (`spec-storylet-pipeline.md` §1). The flags a link reads become the link's `eligibility` (`spec-narrative-contract.md` §5, Audit 2026-09-19: the contract had no field for it). The structure call cannot add, drop or rename a flag |
| **Continuity context** | each link's text call sees the arc's `name` and `premise` and the previous link's accepted `name` and `situation` — one link back, never the whole transcript, so state stays bounded (`seedsmith/spec-workflow-runtime.md` §2.2) |

After the last link, `Narrative/ArcIntegrity`'s rule set runs on the unit before emit (link count equals the
shape's, every `arcLink` resolves inside the unit, every flag read is set by an earlier link, every
persistent role is declared by every link that uses it). A failure here is a pipeline defect, not a content
defect, and stops the unit with the rule named.

### 4. Counter-doctrine arcs (R13)

A `rival` shape is a **fixed authored chain** (`arc-shapes`): the rival never levels, ranks up or remembers
encounters (`npc-story-events-ideal.md` §6.12 rules 1–3). This pipeline enforces the mechanical parts:

- A counter-doctrine shape declares **only `progress` flags** (`spec-arc-shapes.md` §4 rule 6), so no link's
  text or eligibility can vary on how the player fared against the rival; since flags are planned `const`,
  a structure reply cannot add one. Audit 2026-09-19: this bullet spoke of "faction- or world-scoped" flags,
  a scope attribute the shape registry does not have; the registry's own rule is restated instead.
- No outcome in a counter-doctrine arc recruits the antagonist role or shifts a relation about it —
  `narrative-validators`' `enemy-consequence` rule in the structural gate. Audit 2026-09-19: this bullet also
  named "any consequence `storylet-vocab` marks as growth"; no such marking exists, and no consequence kind
  can grow a character (`spec-narrative-contract.md` §6 has no such field).
- Enemy-side characters' lines obey `narrative-validators`' `enemy-memory` rule wherever the arc casts them.

Whether a link's prose *implies* the rival remembers the player is not mechanically decidable; the
premise and link briefs state the rule as a negative clause, and review samples every counter-doctrine arc
in full (`review-render` renders arcs as a census).

### 5. Transport and provenance

Model through the config layer only (`gk-forge/tools/seedsmith/seedsmith/pipeline/llm_caller.py:47`, `.env` keys at
lines 69–77); no literal (R6). One graph per arc unit in
`tools/seedsmith/seedsmith/workflow/graphs/narrative_arc.py` (new), calling the storylet graph's nodes for
each link; checkpointed, so TRANSIENT failures replay without new generation. Provenance: the arc's prompt
version, `packetHash`, the shape id and version, and each link's own storylet provenance.

### 6. Call budget

`docs/research/ai-native-generation/README.md` §9, via the call-shape table (`narrative-planner` §7). `L` is
the shape's link count (3 to 5):

```text
base per arc  = 1 premise + L x 4          = 13 to 21
worst per arc = 3 premise + L x 12         = 39 to 63
```

Illustration, not an assertion: the ideal's six arcs of four links are 6 × 17 = 102 base calls.

### 7. Tunables

Budget file `gk-data/packs/fusion/data/seed/narrative/_plan/budget.v1.json` (new), block `arc`: `arc.temperaturePermille.premise`
(‰, starting 500 — prose variety, as the storylet text call). Link calls use `storylet-pipeline`'s block.
**Structural (commented):** all-or-nothing emit; one-link-back continuity; two repairs.

## Commands

```powershell
$env:PYTHONPATH = "gk-forge/tools/seedsmith"; python -m pytest tools/seedsmith/tests/test_narrative_arc_pipeline.py -q
cd tools\seedsmith; python -m seedsmith narrative arcs run --dry-run                 # DEFAULT: premise + every link prompt, call count, no call
cd tools\seedsmith; python -m seedsmith narrative arcs run --write --shape rescue --limit 1
cd tools\seedsmith; python -m seedsmith narrative arcs run --resume <runId>
```

## Project structure

```text
tools/seedsmith/seedsmith/adapters/narrative/pipelines/arc.py             (new) premise node, unit assembly, integrity check, R13 structure rules
tools/seedsmith/seedsmith/adapters/narrative/pipelines/prompts/arc.py     (new) premise prompt, PROMPT_VERSION, schema
tools/seedsmith/seedsmith/workflow/graphs/narrative_arc.py                (new) graph wiring only
tools/seedsmith/tests/test_narrative_arc_pipeline.py                      (new)
```

## Code style

```python
def emit_unit(unit: "ArcUnit") -> "EmitResult | UnitUnresolved":
    """All or nothing: returns UnitUnresolved naming the first unresolved part when any part is
    unresolved, and writes nothing. Accepted parts stay in the run ledger for resume."""
```

## Testing strategy

Scripted transport fake that raises when exhausted or called unexpectedly.

| Test | Asserts |
|---|---|
| `dry_run_makes_no_call` | premise and every link prompt render with a transport that raises |
| `links_cannot_point_past_the_arc` | every emitted `arcLink` resolves inside the unit; the schema offers no free-text id |
| `unresolved_link_emits_nothing` | a link failing its gates leaves the corpus unchanged; accepted parts remain in the ledger |
| `resume_reuses_accepted_parts` | after a TRANSIENT failure at link 3, resume makes no new call for the premise or links 1–2 |
| `persistent_roles_are_const_in_every_link` | links 1..L receive the shape's persistent roles as `const` |
| `flags_are_planned` | a structure reply that adds or drops a flag cannot validate; the flags match the shape |
| `continuity_context_is_one_link_back` | link k's text prompt contains link k-1's name and situation and no earlier link's |
| `rival_links_carry_only_planned_progress_flags` | every flag position in a rival unit is a planned `const` progress flag; a reply changing one cannot validate |
| `counter_doctrine_rejects_enemy_consequence` | a rival-shape outcome recruiting the rival or shifting a relation about it fails `enemy-consequence` |
| `persistent_roles_copied_from_the_shape` | every link's persistent roles equal the shape's rows byte for byte, `requires` included; no call schema offers them |
| `flags_read_become_eligibility` | link k's `eligibility` lists exactly the shape's `flagsRead` for link k |
| `call_bounds` | a scripted L=4 unit makes 17 calls clean and 51 at worst |

No test asserts how many arcs exist or any generated text.

## Success criteria

1. Every emitted arc has exactly its shape's links, all resolving inside the arc, with flags and cast as
   planned.
2. No partial arc ever reaches the corpus.
3. Counter-doctrine arcs pass the R13 structure rules and are reviewed in full.
4. The suite passes with the model transport stubbed to raise.

## Boundaries

- **Always:** run an arc as one unit; emit all or nothing; reuse `storylet-pipeline` for every link; take
  shape, flags and persistent roles from the plan.
- **Ask first:** a new arc shape (that is `arc-shapes`' registry change); more than one link of continuity
  context.
- **Never:** let a link reference an id outside its arc; emit a partial arc; let a model add a flag or a
  role; let a rival grow, rank or remember the player; build a second storylet generator for links.

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
| 1 | medium | Link 1's structure call wrote persistent roles' `requires`, contradicting the shape registry | fixed (copied verbatim, const) |
| 2 | medium | Flag positions and flag reads had no defined home | fixed (pinned positions; `eligibility`) |
| 3 | medium | R13 bullets relied on a flag "scope" and a "growth" marking that no registry has | fixed (progress-only flags; `enemy-consequence`) |
