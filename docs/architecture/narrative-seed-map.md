# Capability map: `narrative-seed`

**Status: spec phase, written 2026-09-19. Map approved by the owner 2026-09-19 ("approve, go"). Module specs authorized; no build authorized.**
No module spec is written until the owner approves the module boundaries, the dependency direction
and the build order below.

**Program id:** `narrative-seed` (stable; every downstream spec, plan and task selects work by the
module ids in §4).
**Ideal:** [narrative-seed-ideal.md](narrative-seed-ideal.md) (idea phase, 2026-09-19; owner rulings
R6–R7 in its §10, enrichment in its §11). This map does not reopen the ideal's decisions; it cuts the
work into modules that can be specified and verified one at a time.
**Sibling rulings this map is bound by:** [npc-story-events-ideal.md](npc-story-events-ideal.md) §10
R1–R13 and [ip-censor-ideal.md](ip-censor-ideal.md) "Owner rulings" IC-1 to IC-6.
**Session record:** `tasks/sessions/narrative-programs-spec-20260919.json`.
**Future artifact paths (not written yet):** module specs at
`docs/architecture/narrative-seed/spec-<module-id>.md`, plan and task list at
`tasks/narrative-seed-plan.md` and `tasks/narrative-seed-todo.md`.

> **The program in one sentence.** A new seedsmith adapter, `narrative`, generates four seed kinds —
> storylets with player choices, characters with voices and lines, arcs, and main-story chapters —
> offline, under a closed contract in which the model writes identity and text and never a number, and
> the game resolves every seed deterministically at runtime without calling a model.

---

## 1. Which loop this extends

This program is **content supply**, not a runtime. It adds no loop, currency, stat or player surface.

- **Primary:** [the-loops.md](../guide/the-loops.md) loop **7. Quests and events**.
- **Through it:** **6. The Delve** (the first consumer — its 54 events become storylets), **4. World
  map**, **5. World stage**, **2. Idle expeditions** and **B. Summon** (characters who join).

The runtime side of each of those places — the storylet engine, casting, the relation ledger, the
story ledger and every route — belongs to `npc-story-events` and `party-dungeon` (§7). Nothing here
resolves a seed.

---

## 2. Principles, restated inline

These govern every module below. They are restated rather than linked because a link does not survive
a long session.

1. **Seed → concrete → per-player.** seedsmith emits **seeds** offline: identity text and picks from
   closed lists. The game runtime turns a seed into a concrete object per save, seeded and
   reproducible, through the one roll SDK, `Instantiator.TryInstantiate`
   (`gk-core/src/FusionRpg.Core/Effects/Atoms/Instantiator.cs:98`). The Delve event path already calls it
   (`gk-core/src/FusionRpg.Core/Delve/Events/EventDeck.cs:303`). This program designs no second roll.
2. **The model writes identity; deterministic code writes magnitude.** A model never picks a number, a
   weight, a probability, a cost or a duration, and **never writes one into prose** ("gain 50 souls" is
   a magnitude with no owner). Enforced by a schema audit and a no-digit text check, never by review.
3. **No model at runtime.** The game runtime never calls a model (`docs/architecture/party-dungeon-map.md`
   line 29). All interactivity is authored offline and resolved deterministically.
4. **A closed contract is a well-described structure, not a frozen vocabulary.** Every field has a
   description with a **negative clause** (what it is not). Every closed enum admits `none`.
   `additionalProperties: false`; every field required. A missing key is a defect; `none` is a value.
5. **Enum choice is the most bias-prone task a model does.** Every enum is permuted, seeded from
   `(entity_id, field, sample_index)`; load-bearing fields take a three-sample majority vote; a 1-1-1
   split is `unresolved`, never the first option. The committed Delve corpus shows the bias live: 39 of
   54 events chose `climateAffinity: none` and none chose ice, earth or light (§3.4).
6. **The plan is deterministic** (seedsmith P4). A pure function decides which content to write, in
   what order, with which constraints. No model decides what work to do or what kind of decision a
   storylet is.
7. **A metric without a declared target is an opinion** (P2), and **every metric says whether it can
   verify its own fix** (P3). An open-loop check ("is this line in character?") produces a review
   queue, never a pass. A model judge may rank prompt versions over a batch; it never passes or fails
   one item and never judges its own model's output.
8. **Generated data is never hand-edited.** Fix the generator, its registry or its tuning, then
   regenerate and commit the diff. The 54 existing Delve events are regenerated, never patched: first
   by the repaired legacy generator in Wave 0 (clean and keyed; Owner ruling 2026-09-20: all 54, the `story` events included with their committed `chainRef`s), then as
   storylets under the widened contract in Wave 6 (Owner ruling 2026-09-19 (round 4)).
9. **A guardrail validates the contract, never a population.** Corpus size, per-cell counts, accepted
   and rejected counts per run, and generated names and text are **readings**, printed and never
   asserted. Tests assert closed enums, joins, uniqueness, closure and structural rules. A closed
   vocabulary's member count (for example the choice-kind registry) is a declaration and may be pinned,
   with the reason stated.
10. **One power ladder.** A contest reads a `Θ` difference; a magnitude reads `P(Θ)`. Seeds carry
    ordinal bands (`powerBand`, `dropBand`); the runtime resolves them. No private `f(level)`.
11. **The balance surface is data.** Runtime numbers live in `gk-core/data/tuning/` (owned by the runtime
    programs); seedsmith's generation targets live in its `budget`. No threshold literal in a policy or
    catalog file.
12. **Every RPG feature lives in the RPG layer.** Narrative never touches what PvZ is.
13. **No hard-coded model** (owner ruling R6). Every call resolves its model through seedsmith's config
    layer: `.env` `SEEDSMITH_LLM_MODEL` over `seedsmith.toml` over the `LlmCallerConfig` default
    (`gk-forge/tools/seedsmith/seedsmith/pipeline/llm_caller.py:47`, the `.env` key table at lines 66–78). No
    adapter and no CLI flag carries its own model literal.
14. **Names are tokens, never words** (rulings R8–R11). Story text refers to the three leads, named
    characters, cast roles and places through closed ICU placeholders resolved from a names registry.
    The model never sees a real name, so it cannot leak one. Renaming a lead is one registry edit.
15. **SOLID and one generator per content kind.** One storylet generator for every place: the Delve's
    event kind moves into the `narrative` adapter rather than living beside it. The seedsmith core
    stays feature-agnostic (P5); all narrative knowledge lives in the adapter.

---

## 3. What the gate reading found in code (2026-09-19)

Every row was re-read in this session. Code beats the ideal where they disagree; §3.5 lists where the
ideal is stale.

### 3.1 Built

| Fact | Evidence |
|---|---|
| Per-field ownership levels (AUTHORED, PLANNED, VALIDATED, DERIVED, GENERATED) with a contract audit that fails a field with no level | `gk-forge/tools/seedsmith/seedsmith/adapters/dungeon/schema.py:1-5` |
| A schema audit that rejects numeric fields, digit patterns, all-numeric enums and magnitude-named fields | `gk-forge/tools/seedsmith/seedsmith/adapters/dungeon/audit.py:89` (`numeric_audit`) |
| Enum permutation seeded from id, field and sample index | `gk-forge/tools/seedsmith/seedsmith/adapters/creatures/anchor/permute.py:26-33` (`order_for`) |
| Three-sample majority vote with `unresolved` on a 1-1-1 split | `gk-forge/tools/seedsmith/seedsmith/adapters/creatures/anchor/vote.py:26-43` (`resolve_vote`) |
| Bounded, named-defect quality retry | `gk-forge/tools/seedsmith/seedsmith/adapters/dungeon/pipelines.py:328-346` (`MAX_QUALITY_RETRY = 2` at line 239) |
| Prose validators: `field_echo`, `subject_name_echo`, `name_collision`; corpus-wide `SemanticDedup` | `gk-forge/tools/seedsmith/seedsmith/workflow/validators/field_echo.py:48`, `:69`; `gk-forge/tools/seedsmith/seedsmith/metrics/dedup.py` |
| Run ledger and input staleness | `gk-forge/tools/seedsmith/seedsmith/pipeline/run_ledger.py`; `gk-forge/tools/seedsmith/seedsmith/pipeline/staleness.py` |
| Adapter registry — one line adds an adapter | `gk-forge/tools/seedsmith/seedsmith/adapters/registry.py:12-18` |
| Runtime event engine from seed to magnitude, including the roll SDK | `gk-core/src/FusionRpg.Core/Delve/Events/EventDeck.cs:303` (`TryInstantiate`), `:339` (`Answer`) |
| The roll SDK is a live production path: 12 `TryInstantiate` call sites in 10 production files (counted this session), e.g. siege structures, elite affixes, events, loot, supplies, item mint | `gk-core/src/FusionRpg.Core/Battle/Siege/StructureInstantiate.cs:70`; `gk-core/src/FusionRpg.Core/Delve/Loot/DelveLoot.cs:202`; `gk-core/src/FusionRpg.Core/Items/Drops/LootMintAt.cs:88` |
| A 16-leaf predicate vocabulary including the four event leaves | `gk-core/src/FusionRpg.Core/Effects/Atoms/PredicateNode.cs:28-46` |
| A shared per-kind budget file for the dungeon adapter | `gk-data/packs/fusion/data/seed/dungeon/_plan/budget.v1.json` |

### 3.2 Wiring gap (exists, inert — not a wall)

| What | The inert line |
|---|---|
| The dungeon event retry loop checks motifs only; the language check is never called during generation | `gk-forge/tools/seedsmith/seedsmith/adapters/dungeon/pipelines.py:334` |
| The language check's script test covers U+4E00–9FFF only (no CJK extension A, compatibility ideographs, CJK punctuation, fullwidth forms, kana or Hangul) | `gk-forge/tools/seedsmith/seedsmith/workflow/validators/language.py:33` |
| Eleven executable model literals in seven adapter files bypass the config layer (§3.5 item 1) | e.g. `gk-forge/tools/seedsmith/seedsmith/adapters/actions/generate_action_pipeline.py:78`, `:180`; `gk-forge/tools/seedsmith/seedsmith/adapters/creatures/generate_commander_effects.py:71`; `gk-forge/tools/seedsmith/seedsmith/adapters/effects/affix/generate_affixes.py:378` |
| Six emitters stamp `_meta.model` provenance with a literal default that names a model the call may not have used: two `claude-sonnet-5` emit helpers and four invented provenance names. Reconciled 2026-09-19: this row said two; `narrative-seed/spec-model-config-resolve.md` §2 class B found four more | `gk-forge/tools/seedsmith/seedsmith/adapters/items/affixfamgen/emit.py:124`; `gk-forge/tools/seedsmith/seedsmith/adapters/items/basetypegen/emit.py:152`; `gk-forge/tools/seedsmith/seedsmith/adapters/items/basetypegen/run.py:287`; `gk-forge/tools/seedsmith/seedsmith/adapters/items/droptablegen/run.py:216`; `gk-forge/tools/seedsmith/seedsmith/adapters/items/gemgen/run.py:254`; `gk-forge/tools/seedsmith/seedsmith/adapters/items/recipegen/emit.py:221` |
| Functions and CLI flags default to `DEFAULT_CONFIG`, so they skip `.env` and `seedsmith.toml` whenever the caller omits the argument (a bypass a string grep cannot see). Reconciled 2026-09-19: third bypass class found by `spec-model-config-resolve.md` §2 class C | e.g. `gk-forge/tools/seedsmith/seedsmith/adapters/creatures/generate_families.py:73-74`; `gk-forge/tools/seedsmith/seedsmith/adapters/dungeon/pipelines.py:109` |
| Outcome count fixed at 2 (the contract allows 2–4) because positional voting inside an array was never built | `gk-forge/tools/seedsmith/seedsmith/adapters/dungeon/briefs.py:236`, reason at lines 227–235 |
| The dungeon adapter has no committed orchestrator from pipeline to emit, so no `_provenance` and no `PROMPT_VERSION` ride on its output | `gk-forge/tools/seedsmith/seedsmith/adapters/dungeon/completeness.py:19-30` |
| Event eligibility trees cannot be loaded; only `null` is accepted | `gk-core/src/FusionRpg.Core/Delve/Events/EventSeedFile.cs:40-44` |
| No route answers an event (`DelveEventEndpoints.cs` does not exist); `EventDeck.Resolve`/`Answer` have no production caller (grep, this session) | `gk-core/src/FusionRpg.Core/Delve/Events/EventDeck.cs:218`, `:339` |
| Event text has no wire path: `EventView` carries no name or flavor | `gk-web/web/fusion-rpg-web/src/contract/types.ts:1276-1282` |
| `/talk` only commits an already-resolved join | `gk-core/src/FusionRpg.Server/DelveWildEndpoints.cs:14-22` |
| Chain preflight tolerates an unresolved `chainRef` | `gk-core/src/FusionRpg.Core/Delve/Events/EventDeckPreflight.cs:55` |
| `gk-forge/tools/seedsmith/**` has no verification boundary: `verify-change.ps1` throws for it; seedsmith's pytest runs only in CI | `scripts/verify-change.ps1:95`; `docs/architecture/test-verification-boundary/spec-python-test-lane.md` line 16; `.github/workflows/ci.yml:284` |

The last four rows of the C# group are runtime wiring owned by other programs (§7); they are listed so
no session reports them as walls.

### 3.3 Real gap (no mechanism anywhere)

| What | Owned by |
|---|---|
| Player-facing choices: option text, per-choice condition, per-choice consequences. `EventOutcomeRow` is `(Ordinal, DropBand, Consequence, Effects)` only (`gk-core/src/FusionRpg.Core/Delve/Events/EventRow.cs:17-18`); `spec-event-deck.md` §6 calls per-choice predicates *"a seed-contract widening — ask first"* (`docs/architecture/party-dungeon/spec-event-deck.md` line 210). This program is that widening on the seed side | seed side here (`storylet-vocab`, `narrative-contract`); runtime loading in `npc-story-events` (`storylet-contract`; Reconciled 2026-09-19: loader ownership per npc-story-events map), the Delve's answer route in `npc-story-events` (`delve-live-rooms`; Owner ruling 2026-09-19 (round 3): moved from `party-dungeon`) |
| A character contract (name, role, voice, anchors, lines) | here |
| Arcs: linked storylets with a persistent cast | here (seed side) |
| Main-story chapters as generated seeds (R1) and scene scripts as data — today's scripts are TypeScript literals (`RIFT_PROLOGUE_SCRIPT`, `gk-web/web/fusion-rpg-web/src/features/story-scene/sceneScript.ts:105`; Reconciled 2026-09-19: `:32` is the `SceneBeat` type; the literal is at `:105`) | seed side here; the data-driven scene loader belongs to `story-scene` / `npc-story-events` |
| Generated text into lingui: *"`msg({ message: someRuntimeString })` is a hard error"* (`gk-web/web/fusion-rpg-web/src/features/story-scene/messages.ts:13-19`) | keyed strings here; the codegen bridge is runtime-side (§7) |
| A names registry and a token grammar for story text | here |
| Name quality bounds (length bound, out-of-world word list) | here |
| A target-language gloss for motifs: all 1,586 motifs in `gk-data/packs/fusion/data/seed/creatures/_registry/motifs.v1.json` contain Han characters (counted this session) | here (`gloss-registry`, `gloss-fill`) |
| An English display name per species: all 904 `displayName` values in `gk-data/packs/fusion/data/seed/creatures/_registry/themes.v2.json` contain Han characters (counted this session) | coordinated with `creature-seed`, not owned here (§7) |
| A party-composition predicate leaf for `bring:{tag}` choices | runtime (`npc-story-events`); the seed side only names the condition |

### 3.4 Built, but defective (the committed corpus — readings, not assertions)

Measured this session over `gk-data/packs/fusion/data/seed/dungeon/events/` (54 event files plus `_index.json`):

| Reading | Cause | Fixed by |
|---|---|---|
| 53 of 54 events carry Han characters in `name` or `flavor` | The event system prompt demands *"Use at least one of the listed motifs"* (`gk-forge/tools/seedsmith/seedsmith/adapters/dungeon/briefs.py:324`) and the brief injects raw Chinese motifs (`:354`) | `gloss-registry`, `gloss-fill`, `dungeon-generator-repair` (regenerates the legacy non-story events clean and keyed — Owner ruling 2026-09-19 (round 4)), then `delve-event-regen` |
| `climateAffinity`: none 39, fire 12, air 2, dark 1; ice, earth and light 0 | Climate is AUTHORED by the model (`gk-forge/tools/seedsmith/seedsmith/adapters/dungeon/schema.py:123`, enum at `:240`) | Climate becomes PLANNED (`dungeon-generator-repair`, then `narrative-planner`) |
| Kinds: bargain, curio, encounter-event, shrine, trap 10 each; story 4 | The planner re-plan gap for `story` | `narrative-planner` |
| 2 of 4 story `chainRef`s point at events that do not exist | The planner invents `-{n+1}` for the last story event (`gk-forge/tools/seedsmith/seedsmith/adapters/dungeon/pipelines.py:310`) | `dungeon-generator-repair` stops forging; `arc-shapes` makes a dangling link structurally impossible |

No player sees any of this today, because no route answers an event (§3.2). That fact shapes the build
order in §6.

### 3.5 Stale claims found in the ideal (code wins)

**Reconciled 2026-09-23 (NS70), re-read against the code this session:** items 1–3 are FIXED in the ideal —
§4.2 carries the corrected count and now records the closure, the `TryInstantiate` citation reads
`gk-core/src/FusionRpg.Core/Effects/Atoms/Instantiator.cs:98` (`:98` is where the method begins), and §6.2 cites
`gk-forge/tools/seedsmith/seedsmith/adapters/dungeon/layouts.py:35-42` (the six `_TEMPLATES` rows). Items 4–5 are not
stale citations: item 4's claim stands and item 5 is a proposed change to the party-dungeon contract,
recorded in §11. The entries are kept below as the trail of what the pass found.

1. **The model-literal count.** `narrative-seed-ideal.md` §4.2 says *"hard-coded in 14 places … ten
   adapter files"* and cites `adapters/items/uniques/briefs.py` as an example. Counted this session:
   **11 executable literals in 7 files** — five files under `adapters/actions/` (9 literals, e.g.
   `gk-forge/tools/seedsmith/seedsmith/adapters/actions/generate_family_actions.py:66`, `:166`), plus
   `gk-forge/tools/seedsmith/seedsmith/adapters/creatures/generate_commander_effects.py:71` and
   `gk-forge/tools/seedsmith/seedsmith/adapters/effects/affix/generate_affixes.py:378`. The `uniques/briefs.py`
   hit (`gk-forge/tools/seedsmith/seedsmith/adapters/items/uniques/briefs.py:158`) is a comment, as are
   `adapters/creatures/family/consolidate.py:36` and `workflow/graphs/item_set.py:134`. The ideal's
   count also omits the provenance-stamp defaults in §3.2. `model-config-resolve` owns the real list
   (Reconciled 2026-09-19: three classes — 11 literals, 6 provenance defaults, and `DEFAULT_CONFIG`
   defaults — per its §2).
2. **`Instantiator.cs:92`** (ideal §1 principle 1, and the `seedsmith-design` skill) — `TryInstantiate`
   now begins at `gk-core/src/FusionRpg.Core/Effects/Atoms/Instantiator.cs:98`.
3. **`layouts.py:12-16`** (ideal §6.2) — lines 12–16 are the docstring; the six authored layout
   templates are at `gk-forge/tools/seedsmith/seedsmith/adapters/dungeon/layouts.py:35-42`.
4. **`gk-forge/tools/seedsmith/seedsmith/adapters/dungeon/schema.py:240`** (ideal §4.4, "model-authored") is the enum definition; the AUTHORED ownership
   level is declared at `gk-forge/tools/seedsmith/seedsmith/adapters/dungeon/schema.py:123`. The claim stands; the
   citation should name both.
5. **The Delve cell grid.** The ideal computes 6 kinds × 7 climates = 42 cells. The approved dungeon
   seed contract's event cell is kind (6) × planning theme (8) = 48
   (`docs/architecture/party-dungeon/spec-dungeon-seed-contract.md` line 78). The ideal's grid is a
   change to that contract, not a description of it; `narrative-planner` owns the new grid and a
   `decisions.md` row records the change (§11).

---

## 4. Modules

Twenty-three modules (Owner ruling 2026-09-19 (round 3): `quest-vocab` approved as row 23). **Model?** says whether the module itself spends model calls. Every module id is
stable and kebab-case.

| # | Module id | Capability (one line) | Model? | Depends on |
|---|---|---|---|---|
| 1 | `model-config-resolve` | Remove every executable model literal from seedsmith adapters and CLI defaults so each call resolves its model through the `.env` → `seedsmith.toml` → `LlmCallerConfig` layer, derive `_meta.model` provenance from the resolved config, and add a test that fails on any model literal outside `llm_caller.py` (R6) | no | — |
| 2 | `script-check` | Replace the U+4E00–9FFF range with a Unicode-script-property check (Han, kana, Hangul, fullwidth forms, CJK punctuation, Cyrillic) in the shared validator, with a declared target-script policy per field | no | — |
| 3 | `gloss-registry` | The motif gloss registry contract: one target-language gloss per motif, keyed by motif, versioned under `_registry/`, with a lookup that **refuses** a motif without a gloss rather than passing the raw token | no | — |
| 4 | `dungeon-generator-repair` | Fix the current dungeon event generator with no new design: briefs carry glosses, never raw motifs; the widened script check runs in every retry loop, starting at `gk-forge/tools/seedsmith/seedsmith/adapters/dungeon/pipelines.py:334`; a `PROMPT_VERSION`; `climate` moves to PLANNED; the planner stops forging chain ids. Owner ruling 2026-09-19 (round 4): it then **regenerates the contaminated legacy non-story events** through the repaired generator and gives every legacy event's `name` and `flavor` a text key (`item/seed-contract.md` §6: key and string together, keys from row one); ~~legacy `story` events are retired, never regenerated~~ Owner ruling 2026-09-20: the four legacy `story` events are regenerated clean and keyed too, ids and committed `chainRef`s kept (their tails still dangle as the legacy contract forces, tolerated as named known defects until `delve-event-regen`) | **yes** (one bounded regeneration run, after `gloss-fill`; the code repair itself is built against stubs) | `script-check`, `gloss-registry`, `gloss-fill` and `model-config-resolve` (for the regeneration run; Owner ruling 2026-09-19 (round 4)) |
| 5 | `storylet-vocab` | ~~Owner ruling 2026-09-20 (round 5): plus the sector-type → climate registry `sector-climates.v1.json` (new) (R19, `spec-storylet-vocab.md` §3.9).~~ Owner ruling 2026-09-20 (round 6): R20 retired that registry; world host rows read the sector's own climate (`spec-storylet-vocab.md` §3.1). Closed registries for storylets: choice kinds (`interact`, `leave`, `use:{supplyTag}`, `offer:{stock}`, `fight`, `bring:{element}` (Audit 2026-09-19: the spec's closed argument family is the six elements; a trait or tag argument is a later reviewed widening), `persuade`, `threaten`), choice patterns (two unconditioned options plus zero to two conditional ones), the condition vocabulary (compiling to `PredicateNode` leaves or a role requirement), consequence kinds (`none`, `loot`, `encounter`, `scout` plus `quest.offer`, `relation.shift`, `story.flag`, `recruit`, `scene.play`, `battle.start`; Reconciled 2026-09-19: `battle.start` added per `spec-storylet-vocab.md` §3.5), role requirement tags and host kinds — each value with a description and a negative clause. Owner ruling 2026-09-19 (round 3): consequence kinds declare which require a `ref` and which `param` values each allows (`spec-storylet-vocab.md` §3.5) | no | — |
| 6 | `character-vocab` | Closed registries for characters: the role list (shared with the runtime), voice registers each anchored by an authored exemplar under `_exemplars/`, line contexts, the 4-band disposition ladder (R4), the required (context, band) pairs, and the enemy-side restrictions of R13 | no | — |
| 7 | `arc-shapes` | Authored arc-shape registry (link count 3–5, host kind per link, persistent roles, flags set and read per link) and the spine frame (one chapter slot per time-machine piece, beat count and cast per chapter, R1/R3). A rival or antagonist shape is a fixed authored chain obeying R13 rules 1–3 | no | `storylet-vocab`, `character-vocab` |
| 8 | `token-grammar` | The closed text grammar: entity tokens (`{lead_summoner}`, `{lead_companion}`, `{lead_antagonist}`, `{c_<characterId>}`, `{c_<characterId>_epithet}`, `{role_<roleId>}`), runtime slots (`{place}`, `{supply}`, `{reward}`, `{cost}`), the closed semantic markup tags, and the ICU `select` features (gender, number, article) — each token with a description and a negative clause for the brief | no | — |
| 9 | `names-registry` | `gk-data/packs/fusion/data/seed/narrative/_registry/names.en.v1.json` (new): token → display string plus closed grammatical feature tags. First rows are R11's leads — the Garden Keeper, Hourbloom, the Rotwright. Published like any registry; renaming a lead is one row edit | no | `token-grammar` |
| 10 | `narrative-contract` | The `narrative` adapter shell (registered in `adapters/registry.py`, corpus under `gk-data/packs/fusion/data/seed/narrative/` (new)) and the four seed schemas — storylet, character, arc, spine chapter — with ownership levels, `revision`, tombstones, `provenance: generated | authored`, keyed text, and the schema audit extended to reject any digit in prose. Owner ruling 2026-09-19 (round 3): owns the one outcome consequence object `{kind, ref, param}` the runtime loads as-is (`spec-narrative-contract.md` §5); the fifth kind `quest` is added by `quest-vocab` | no | `storylet-vocab`, `character-vocab`, `arc-shapes`, `token-grammar` |
| 11 | `narrative-emit` | Canonical JSON, `_provenance` (resolved model, prompt version, input hashes), run ledger, staleness, `revision` bump on content-hash change, tombstone rows; a rerun is byte-identical by hash | no | `narrative-contract` |
| 12 | `narrative-validators` | Deterministic, closed-loop validators. Structural: 2–4 choices, exactly one `leave`, no lose-lose, no dominated choice, choice type classified from ordinals (relaxed or dilemma-with-upside pass; obvious, all-bad dilemma and unchoice fail), conditional choices at least as good as the best unconditional one. Text: script check, `field_echo`, `subject_name_echo`, name collision, token and placeholder closure, no digits, length bound per field, no literal name from the names registry or the species catalog, no entity absent from the lore packet, an out-of-world word list matched on word boundaries, and a round-trip render against two name sets | no | `narrative-contract`, `names-registry`, `script-check` |
| 13 | `narrative-metrics` | Coverage and distribution metrics against declared `budget` targets, each declaring closed- or open-loop: per-cell coverage, choice-kind distribution, required line-pair coverage, arc and chain integrity, per-cell diversity (compression ratio, long-n-gram self-repetition), acceptance per voice register (open-loop reading), voice distinctness (open-loop, feeds review only) | no | `narrative-contract` |
| 14 | `review-render` | seedsmith `report` sampling mode for narrative: renders each sampled seed with two to three sample casts and filled placeholders, plus its computed choice type and each option's outcome profile, so a reviewer reads what a player reads; records verdicts, never edits | no | `narrative-contract`, `names-registry` |
| 15 | `lore-packet` | Builds the per-call grounding packet: species facts, place, faction, motif glosses, the declared tokens, the allowed-entity list, and the free IP avoid-list rendered from the `ip-censor` registry (empty until that registry exists — IC-3 makes it advisory, never a blocker) | no | `gloss-registry`, `names-registry`, `token-grammar` |
| 16 | `narrative-planner` | Deterministic work order: host × kind × climate cells, choice-pattern allocation, arc shapes, species picks for characters (side × role × element), spine chapters from the spine frame, per-call constraints; a budget file with declared targets; `--dry-run` renders every prompt and prints the call count before anything is spent | no | `narrative-contract`, `narrative-metrics`, `arc-shapes`, `lore-packet` |
| 17 | `gloss-fill` | One-time translation pipeline over the motif list (identity text, so model-writable), verify-and-self-heal loop per `seedsmith/spec-pipeline.md` §5.1, script-checked, reviewed by sample, committed as the gloss registry. Owner ruling 2026-09-19 (round 4): runs in **Wave 0**, because the legacy regeneration in `dungeon-generator-repair` reads its output; its review sample uses seedsmith's core `sampling.stratified_sample`, not `review-render` (Audit 2026-09-19) | **yes** (one bounded pass) | `gloss-registry`, `model-config-resolve`, `script-check` |
| 18 | `storylet-pipeline` | Two calls per storylet: **structure** (roles, per-slot conditions and outcomes; three samples, vote per slot on `ordinal` and `consequence`) then **text** (name, situation, labels, results, with the structure shown as `const`; validators with at most two named repairs) | **yes** | `narrative-planner`, `narrative-validators`, `narrative-emit`, `lore-packet`, `model-config-resolve` |
| 19 | `character-pipeline` | **Identity** (role, voice, name, epithet, bio; vote on `role` and `voice`), **anchors** (3–5 anchor lines and a lexicon, accepted by a human before any line call runs), **lines** (one disposition band per call, anchors attached as prior turns) | **yes** | `narrative-planner`, `narrative-validators`, `narrative-emit`, `lore-packet`, `model-config-resolve` |
| 20 | `arc-pipeline` | Arc name and premise inside a planned shape, then every link through `storylet-pipeline` in the **same work order**, so a link can never point past its arc | **yes** | `storylet-pipeline` |
| 21 | `spine-pipeline` | Main-story chapters inside the planned spine frame, the Rotwright as a speaking lead (R2), two candidates for lead-tier text with the reviewer's pick recorded as a verdict (not an edit), scenes emitted as data with keyed, tokenised text | **yes** | `arc-pipeline`, `character-pipeline`, `names-registry` |
| 22 | `delve-event-regen` | Regenerate the Delve's events as storylets hosted in delve rooms under the widened contract, and retire the dungeon adapter's `dungeon-event` kind — and the clean, keyed legacy tree `dungeon-generator-repair` regenerated (Owner ruling 2026-09-19 (round 4)) — in the same change that the Delve's loader switches to the storylet tree | **yes** (runs `storylet-pipeline`) | `storylet-pipeline`, `gloss-fill`, `dungeon-generator-repair` |
| 23 | `quest-vocab` | The narrative quest seed contract: the `quest` kind in the `narrative` adapter (a `QuestRow`-shaped anchor, `scope: save \| world`, `provenance: generated \| authored`, keyed name and flavor with tokens, `countBand`/`rewardBand` bands only, expiry on the host clock or none), and the closed objective-template registry `data/seed/narrative/_registry/quest-objectives.v1.json` (new) with mode-agnostic fact sources and no lawn-only template. It widens the one quest engine, `QuestCatalog` (`gk-core/src/FusionRpg.Core/Delve/Quests/QuestCatalog.cs:84-92`, scope check `:155-157`), rather than sitting beside it; the runtime half is `npc-story-events`' `quest-sources` | no | `storylet-vocab` (the `quest.offer` consequence kind), `narrative-contract` |

#### Gap found in spec round (2026-09-19) — `quest-vocab` — APPROVED

Owner ruling 2026-09-19 (round 3): **approved.** The amendment is folded into the table above (row 23) and into
Wave 2 of §6; its spec is [narrative-seed/spec-quest-vocab.md](narrative-seed/spec-quest-vocab.md). The finding
that motivated it stands for the trail: the four seed schemas in `narrative-contract` (storylet, character, arc,
spine chapter) had no shape for a **narrative quest**, while `npc-story-events/spec-quest-sources.md` §2 and its
Data shapes section expect two seed-side artifacts from this program — a narrative quest anchor (the `QuestRow`
shape with `scope: save | world`, under `data/seed/narrative/quests/` (new) when generated) and the closed
objective-template registry `data/seed/narrative/_registry/quest-objectives.v1.json` (new). Today the only quest
scopes are Delve ones: `QuestCatalog` refuses anything outside `delve/domain/roster`
(`gk-core/src/FusionRpg.Core/Delve/Quests/QuestCatalog.cs:155-157`). `quest-sources` no longer needs its authored-only
fallback once `quest-vocab` lands.

### Why these boundaries

- **The four registry groups are separate modules** because each has its own consumer set and its own
  review: `storylet-vocab` is shared with the runtime's storylet engine, `character-vocab` with casting,
  `token-grammar` and `names-registry` with the rename program and the IP release gate. Merging them
  would make a role-list change re-review the choice kinds.
- **`names-registry` is separate from `token-grammar`** because it is the one file other programs
  consume directly (`identity-rename` points shipped surfaces at it; `ip-censor` scans it before
  publish), while the grammar is internal to generation.
- **`gloss-registry` and `gloss-fill` are split** so the only model-spending step in front of the
  dungeon repair is bounded and replaceable: the contract, lookup and refusal land model-free, and the
  code in `dungeon-generator-repair` is built and tested against a stub gloss table.
- **`review-render` is its own module** because its acceptance criterion ("a reviewer reads what a
  player reads") is independent of the validators' ("the draft is structurally legal").
- **Structure and text are separate pipeline calls, not separate modules**: they share one planner
  cell and one emit, and cannot ship independently.

---

## 5. Dependency direction

```text
model-config-resolve ──────────────────────────────────────────┐
script-check ──┬──────────────────────────────┐                 │
gloss-registry ┼─► dungeon-generator-repair ──┼─────────────────┼──────────────┐
               │                              │                 │              │
               └─► lore-packet ◄── names-registry ◄── token-grammar            │
                        │               │                 │                    │
storylet-vocab ─┬─► arc-shapes          │                 │                    │
character-vocab ┘       │               │                 │                    │
                        ▼               ▼                 │                    │
              narrative-contract ◄──────┴─────────────────┘                    │
                 │      │     │     └─► quest-vocab (◄ storylet-vocab)         │
                 │      │     │                                                │
                 ▼      ▼     ▼                                                │
     narrative-emit  narrative-metrics  review-render                          │
                 │      │                                                      │
                 │      ▼                                                      │
                 │  narrative-planner ◄── lore-packet                          │
                 │      │                                                      │
narrative-validators ◄──┴── (narrative-contract, names-registry, script-check) │
                 │                                                             │
                 ▼                                                             │
gloss-fill (gloss-registry, model-config-resolve, script-check)                │
                 │                                                             │
storylet-pipeline ◄── planner, validators, emit, lore-packet, model-config ────┤
character-pipeline ◄── same set                                                │
                 │                                                             │
arc-pipeline ◄── storylet-pipeline                                             │
spine-pipeline ◄── arc-pipeline, character-pipeline, names-registry            │
delve-event-regen ◄── storylet-pipeline, gloss-fill, dungeon-generator-repair ─┘
```

The table in §4 is authoritative; the diagram is a reading aid. **No cycles.** Every arrow points from
a model-free foundation towards the model pipelines, and nothing model-free depends on a model module.
Owner ruling 2026-09-19 (round 4): `gloss-fill` now runs in Wave 0, and `dungeon-generator-repair`'s
legacy regeneration run (not its code) depends on it and on `model-config-resolve`; the diagram's
placement of `gloss-fill` below the validators is superseded by §4 and §6. The code half of
`dungeon-generator-repair` stays model-free and is tested against a stub gloss table.
The only cross-program edges are soft: `lore-packet` reads the `ip-censor` registry when it exists
(IC-3: the avoid-list is free and advisory), and `delve-event-regen`'s cutover waits for
`npc-story-events`'s widened storylet loader (`storylet-contract`, §7; Reconciled 2026-09-19: the loader is npc-story-events', not party-dungeon's).

---

## 6. Build order — model-free first

```text
Wave 0 — repair and shared foundations                    (value today; two bounded model runs)
  model-config-resolve   script-check   gloss-registry
  gloss-fill             (after the three above; Owner ruling 2026-09-19 (round 4): moved from Wave 5)
  dungeon-generator-repair          (code after script-check + gloss-registry; the legacy
                                     regeneration run after gloss-fill + model-config-resolve)

Wave 1 — registries                                        (no model)
  storylet-vocab   character-vocab   token-grammar
  arc-shapes       (after the two vocab modules)
  names-registry   (after token-grammar)

Wave 2 — contract and emit                                 (no model)
  narrative-contract  ->  narrative-emit
  quest-vocab        (after narrative-contract; model-free; Owner ruling 2026-09-19 (round 3): approved)

Wave 3 — validators, metrics, review                       (no model)
  narrative-validators   narrative-metrics   review-render

Wave 4 — grounding and planning                            (no model)
  lore-packet  ->  narrative-planner   (dry run prints the call budget)

Wave 5 — model pipelines                                   (tokens spent from here)
  storylet-pipeline   character-pipeline
  arc-pipeline  ->  spine-pipeline

Wave 6 — the Delve corpus
  delve-event-regen                  (cutover with npc-story-events' widened loader)
```

**Waves 0–4 map to the ideal's §8 steps 1–5.** Waves 1–4 spend zero tokens; Wave 0 spends two bounded
runs, `gloss-fill` and the legacy regeneration, each with a dry run that prints its call count first
(Owner ruling 2026-09-19 (round 4)). They produce real value alone: the model literal guard, a script
check that sees the actual defect, a dungeon generator that can no longer leak motifs or forge chain ids,
a live Delve showing clean, keyed legacy text, every registry reviewable by a person, and a planner whose
dry run states the cost of Wave 5 before it is approved.

**The legacy Delve events are regenerated clean in Wave 0.** Owner ruling 2026-09-19 (round 4):
*players must never see a blank Delve event.* Wave-0 `dungeon-generator-repair` therefore **regenerates**
the contaminated legacy events through the repaired generator — glossed motifs in every brief, the widened
script check wired into the retry loop — and gives each legacy event's `name` and `flavor` a text key
(`docs/architecture/item/seed-contract.md` §6: the key and its string authored together, keys from row
one). The live Delve then shows clean, keyed legacy text from day one, rendered through `npc-story-events`'
`narrative-text` lingui codegen bridge. ~~The regeneration covers the **non-story** kinds only~~ Owner ruling
2026-09-20: the regeneration covers **all** 54 legacy events. The four `story` events are regenerated clean and keyed
under their own ids with their committed `chainRef`s carried over — the legacy contract still cannot express a
chain's last link without a dangling `chainRef` (§3.4), so those tails keep dangling (accepted) and are listed as
known defects until Wave 6; new story beats return as arcs. Wave-6 `delve-event-regen` later
replaces the whole legacy tree with storylets in the same change as the loader switch. (This supersedes
the earlier plan, which left the legacy text unregenerated and relied on `spec-delve-live-rooms.md` §4
showing it as `Pending`.)

**Batch size.** The first Wave 5 batch is deliberately small — the owner's standing phased-rollout
decision for generators, *"small-batch-then-playtest before the full run"* (`tasks/item-todo.md`
lines 9590–9591). The ideal's first-batch estimate (84 storylets, 54 characters, 6 arcs, about 980
calls) is a reading to be replaced by `narrative-planner`'s dry run. Batches are sized to what a
reviewer clears in one sitting; character anchors are accepted before any line call spends a token.

**Verification.** seedsmith's own pytest suite is the verification for every module here; it runs in
CI (`.github/workflows/ci.yml:284`). `verify-change.ps1` cannot select it yet because `gk-forge/tools/seedsmith/**`
has no boundary (§3.2); the mapping is `test-verification-boundary`'s `python-test-lane`, not this
program's. Every test stubs the model transport so that a real call raises.

---

## 7. Ownership splits (binding)

| Concern | Owner | This program must not |
|---|---|---|
| Storylet, character, arc and spine **seed** contracts, their registries, validators, metrics, planner, pipelines and committed corpus under `gk-data/packs/fusion/data/seed/narrative/` | `narrative-seed` | — |
| The storylet **runtime**: one engine for every place, eligibility, draw, per-choice answer, casting, relation ledger, story ledger, `revision` pinning of in-progress arcs, counter-doctrine mechanics (§6.12), the party-composition predicate leaf, narrative tunables in `gk-core/data/tuning/narrative.v1.json` (new) | `npc-story-events` | Resolve a seed, add a `LeafId`, choose a pulse rate, or write a runtime number |
| The storylet loader and catalog after the re-seam: `EventSeedFile` loading `choices[]` and eligibility trees, `EventRow` widening, the preflight rule that a dangling link fails, text on the wire (`EventView`). Reconciled 2026-09-19: moved from `party-dungeon` to `npc-story-events` (`storylet-contract`), matching `npc-story-events-map.md` (gap table, module 3, ownership table) and `npc-story-events/spec-storylet-contract.md` | `npc-story-events` (`storylet-contract`) | Edit the loader, `EventRow` or the preflight |
| The Delve's live path: domain import caller, `/start` reaching `CreateDelve`, `MarkRoom` caller, room-entry draw route, the event answer route, text on the wire, quest offer at `CreateDelve`. Owner ruling 2026-09-19 (round 3): absorbed by `npc-story-events` (`delve-live-start`, `delve-live-rooms`; transfer note at the top of `tasks/party-dungeon-todo.md`) | `npc-story-events` | Edit `gk-core/src/FusionRpg.Core/Delve/**` or `DelveWildEndpoints.cs` |
| Owner ruling 2026-09-19 (round 4): the legacy Delve events' Wave-0 regeneration and their text keys (`nameKey`, `flavorKey`) on the seed side; rendering those keys through lingui is `npc-story-events`' `narrative-text` codegen bridge | `narrative-seed` (`dungeon-generator-repair`) for the seed side; `npc-story-events` (`narrative-text`, `delve-live-rooms`) for rendering | Build a render path or show unkeyed text |
| The dungeon adapter's other six kinds (rooms, domains, quests, layouts, encounters, supplies) | `party-dungeon` via seedsmith's dungeon adapter | Move them; only `dungeon-event` moves here |
| The IP registry, its import and reconfirm stages, the `scan`, the **release gate**, and the shared avoid-list helper | `ip-censor` (IC-1 to IC-6) | Build an in-loop IP validator (withdrawn by IC-3) or keep a private banned-word list |
| The scene player, `StorySceneHost`, `scene-trigger`, the data-driven scene loader and the lingui codegen bridge that turns keyed seed strings into literal `msg` descriptors | `story-scene` with `npc-story-events` | Build a second scene player or a second translation path |
| Species display names in the target language (shared by every surface that shows a species) | coordinated with `creature-seed` | Own or fork a species name table; narrative prose never names a species anyway (R8) |
| Renaming shipped surfaces: the Rift prologue (`actorCast.ts`, `sceneScript.ts` and its messages), the player guide, the `decisions.md` Product vision row, the player-facing title (R9, R12, IC-1b) | `identity-rename` | Edit any of them; this program only publishes the names registry they point at |
| seedsmith core (corpus, budget, metrics, planner, pipeline, workflow runtime) | seedsmith core | Put narrative knowledge in the core (P5) |
| `verify-change.ps1` mapping for `gk-forge/tools/seedsmith/**` | `test-verification-boundary` (`python-test-lane`) | Edit `gk-core/scripts/verification-boundaries.v1.json`. **Reconciled 2026-09-23 (NS70):** this program DID add its rows there (NS1, NS2 and the wave-1 tasks), under the protected-path grant the runner gives each lane — the mapping and its guard still belong to `python-test-lane`, and the narrative rows are this program's content inside that mapping. A lane without the grant reports the missing mapping instead of editing the file. |

### Hand-off (Checkpoint 1, recorded 2026-09-23 by lane `ns-2`)

The Wave-1 registries are **published to be read, never edited** by a consumer. Named in each consumer's own
terms:

- `npc-story-events`' `narrative-vocabulary` may read every shared vocabulary file under
  `gk-data/packs/fusion/data/seed/narrative/_registry/`: `host-kinds`, `choice-kinds`, `choice-patterns`, `conditions`,
  `consequence-kinds`, `role-tags`, `value-notes` and `teaches` (`storylet-vocab`), plus `roles`, `voices`,
  `line-contexts` and `line-pairs` (`character-vocab`).
- `narrative-text` may read `tokens.v1.json` and `names.en.v1.json` (`token-grammar`, `names-registry`).
- `spine-progress` may read the spine frame's `fragments[]` (`arc-shapes` §5).

**One file in that directory is not this program's.** `doctrines.v1.json` carries per-mille effect weights
(`speciesElementBiasMilli`, `orderWeightMilli`) by design and its `_meta.owner` is
`docs/architecture/npc-story-events/spec-counter-doctrine.md#3` — `npc-story-events`' counter-doctrine module,
which places its registry here. It is the named exception in this program's registry-hygiene scan
(`gk-forge/tools/seedsmith/tests/test_narrative_registry_hygiene.py`), and the scan asserts every OTHER registry here
declares no `_meta.owner`, so the exclusion cannot silently widen.

---

## 8. Locked assumptions

Each is an owner ruling already made; none is reopened here.

1. **The spine is fully generated** (R1): a spine chapter is a seed like any other — regenerated, never
   hand-edited, reviewed by sample. The planner owns its structure; the model writes inside it.
2. **The antagonist speaks** (R2): the Rotwright is a lead character with lines.
3. **Finite chapters, then endless** (R3): one chapter per time-machine piece; after the last, arcs
   and texture continue. Not a progression ceiling.
4. **One relation ladder** (R4): lines are keyed to the 4-band disposition ladder.
5. **No hard-coded model; the environment sets it, default Gemma 26B** (R6).
6. **Avoid censorable words at the prompt** (R7): the free avoid-list from the shared registry goes into
   every brief; there is no in-loop IP block.
7. **Our own names everywhere in narrative, as parameters** (R8), including never naming a species by
   its PvZ or Fusion name in prose.
8. **Rename shipped surfaces** (R9) — done by `identity-rename`, not here.
9. **Lead names** (R10, superseded for the leads by R11): **the Garden Keeper**, **Hourbloom**, **the
   Rotwright** are the first three names-registry rows. A web search is not trademark clearance.
10. **Title** (R12): "Garden Keeper and his Multiverse" replaces the player-facing title; internal
    `FusionRpg.*` names are untouched. Not this program's change.
11. **Counter-doctrine, no Nemesis-style system** (R13): no generated enemy grows, ranks up or remembers
    the player personally; no enemy line is picked from its own past encounters with the player. Enemy
    memory is faction- and world-level only. `character-vocab` and `arc-shapes` encode this as registry
    rules and `narrative-validators` enforces it.
12. **IP categories** (IC-1): game and franchise marks, real-person names, company and brand names.
13. **Display "PvZ" becomes "Fusion"** (IC-1b) on player-facing surfaces — narrative text never names it.
14. **Registry from a dataset, then reconfirmed** (IC-2) — `ip-censor`'s work.
15. **The IP scan is a release gate, never a generation blocker** (IC-3). Briefs carry the free avoid-list.
16. **Both live IP findings are fixed before release** (IC-4) — `ip-censor`'s work.
17. **The IP registry is tracked in the repo** (IC-5).
18. **Short aliases need a minimum length or a narrow scope** (IC-6).
19. **Lines are personality-neutral in v1** (ideal §6.3); personality variants are a later widening that
    keeps the contract's shape.
20. **Choice shape follows the measured default**: two unconditioned options plus zero to two
    conditional ones (ideal §6.2, FTL data).

---

## 9. Explicitly out of this program

| Out | Why / owner |
|---|---|
| Any runtime resolution, route, endpoint, loader or UI | `npc-story-events`, `party-dungeon`, `story-scene` (§7) |
| A model generating replies during play; free-text player input | Principle 3 |
| Branching dialogue trees | Rejected in `npc-story-events-ideal.md` §6.11; storylet choices plus talk verbs cover the need |
| Per-personality line variants | Ideal §6.3, v1 decision |
| ~~Storylet grids for world, expedition and homeworld hosts~~ | ~~Their host kinds are not defined yet (ideal §11 item 7).~~ Alignment 2026-09-20: the hosts are defined (`narrative-seed/spec-storylet-vocab.md` §3.1). `narrative-planner` computes each grid the same way (host kinds × storylet kinds × climate). Owner ruling 2026-09-20 (round 5), R19: **the world grid now has climate cells** — ~~a world host's climates are the image of the closed `sector-climates.v1.json` registry (sector type → element or `none`, `spec-storylet-vocab.md` §3.9) over the sector types that can hold its slot, so `world.tear` plans `air` and `fire` cells, `world.wildland` and `world.petition` plan `none`, `earth`, `air`, `fire`, `dark`, `world.shrine`/`world.market` plan `none`, `world.vault` plans `none` and `dark`, and `world.anomaly` plans none (no sector type allows its slot).~~ Owner ruling 2026-09-20 (round 6): **R20** — every world host plans **all seven** climate cells (six elements and `none`), because a world storylet's site climate is the sector's own authored `WorldSector.Climate` (`gk-core/src/FusionRpg.Core/World/WorldState.cs:153-154`), which can be any element; R21 (`npc-story-events/spec-world-anomaly-sites.md`) makes `world.anomaly` reachable in new worlds. Expedition and homeworld grids stay `none`-only (no destination sector; untouched ground). Only the budget targets remain undeclared until the runtime's pulse rates are set |
| Voice audio and portraits | Ideal §9 |
| The IP registry, scan and release gate | `ip-censor` |
| Renaming shipped surfaces, the title, and the `decisions.md` Product vision row | `identity-rename` |
| A species English display-name table | Coordinated with `creature-seed` |
| Final member lists of choice patterns, arc shapes, roles, voices and line contexts | Written in the module specs, with descriptions and negative clauses; the ideal's lists are examples |
| Exact coverage targets per cell | Set in the `narrative-planner` spec from the runtime's pulse rates; declared in `budget`, never guessed |
| `SPEC.md`, `tasks/plan.md`, `tasks/todo.md` | Parallel programs; never written |

---

## 10. Success criteria (program level)

### Contract checks (asserted by tests; stable across generations)

- No executable model literal exists in `gk-forge/tools/seedsmith/seedsmith/**` outside `llm_caller.py`, and every
  `_meta.model` / `_provenance` model value is the resolved config value.
- The script check rejects Han, kana, Hangul, fullwidth and Cyrillic characters in a Latin-target field,
  and the dungeon event retry loop calls it.
- No brief contains a raw motif; a motif without a gloss is refused, never passed through.
- Every closed enum in every narrative schema admits `none`; `additionalProperties` is false; every
  field is required; every field has exactly one ownership level and a description with a negative
  clause.
- The schema audit finds no numeric field, and no text field contains a digit.
- Every storylet has 2–4 choices and exactly one `leave`, and passes the lose-lose, dominance,
  choice-type and conditional-value rules.
- Every token in every text field is in the closed grammar and declared for that seed; no text field
  contains a names-registry display string or a species catalog name; every seed renders against two
  different name sets and the outputs differ exactly at the tokens.
- Every arc link and chain reference resolves inside its own arc; ids are unique and never reused; a
  withdrawn seed is a tombstone row.
- Every character covers every required (context, band) pair its registry declares, and no enemy-side
  character has a line keyed to its own past encounters with the player (R13).
- Enum options are permuted from `(entity_id, field, sample_index)`; voted fields resolve 1-1-1 to
  `unresolved`.
- A rerun over unchanged inputs is byte-identical by hash; `stale_ids` names exactly the seeds whose
  inputs changed.
- The whole suite passes with the model transport stubbed to raise.
- `narrative-planner --dry-run` renders every prompt and prints the call count without a model call.
- Every closed registry's member list is pinned with its reason (a declaration, not a reading).

### Readings (printed by `report`, never asserted)

- Corpus size per kind; per-cell coverage against the declared target; climate and choice-kind
  distributions; line-pair coverage totals.
- Acceptance rate per voice register and per prompt version; review pass rate per batch.
- Diversity per cell (compression ratio, self-repetition) and voice distinctness.
- Calls spent, repairs per defect, `unresolved` votes per field, and wall time per run.
- The share of the legacy events whose text leaked a foreign script (53 of 54 when measured) — expected to
  reach zero after `dungeon-generator-repair`'s Wave-0 regeneration (Owner ruling 2026-09-19 (round 4)), but
  reported, not asserted.

---

## 11. `decisions.md` rows to draft at spec time

Listed so they are not discovered halfway through a task. **This map does not edit `decisions.md`.**

**Landed (2026-09-23, reconciled by NS70):** row 2 (NS6, no hard-coded model), row 3 (NS25, structured
story text), row 4 (NS28, the spine as a generated seed kind with a planned frame) and row 6 (NS23,
counter-doctrine) are in `decisions.md`. Rows 1 and 5 land with `narrative-contract` and `narrative-emit`
respectively; the lingui codegen bridge row belongs to the runtime programs (§7).

1. **Narrative seed adapter and the storylet contract.** The Delve event anchor widens into the
   storylet contract (`choices[]`, roles, per-choice conditions and outcomes); the `dungeon-event` kind
   moves from the dungeon adapter to the `narrative` adapter; the event cell grid changes from
   kind × planning theme (`spec-dungeon-seed-contract.md` §1.4) to host × kind × climate, with climate
   PLANNED. Amends the approved party-dungeon seed contract.
2. **No hard-coded model in seedsmith** (R6), with the guard test named.
3. **Structured story text.** Entity tokens, a names registry per locale with closed feature tags, and
   closed semantic markup tags — a reviewed widening of `item/seed-contract.md` §6's "markup forbidden"
   rule to semantic tags only, never HTML or styling.
4. **The spine as a generated seed kind with scene scripts as data** (R1). This interacts with
   `story-scene` decision S3 (typed TypeScript script module); the row records that generated scenes
   load as data through the runtime programs' loader, while the hand-authored Rift prologue keeps S3.
5. **Narrative seed identity over regeneration.** `revision` bumped on content-hash change, tombstones,
   ids never reused, `provenance: generated | authored` with authored entries under an authored path that
   regeneration never touches.
6. **Generated antagonist content obeys counter-doctrine** (R13): the enemy-side restrictions as
   contract rules, cross-referenced to `npc-story-events-ideal.md` §6.12.

A row about the lingui codegen bridge belongs to the runtime programs that build it (§7).

---

## 12. Tension recorded, not resolved here

The `decisions.md` Product vision row still reads *"it stays inside Fusion's own world (its plants and
zombies, Crazy Dave, Penny, Zomboss)"* (`docs/architecture/decisions.md` line 109). Rulings R8–R12
replace those names in narrative and in the title. The names registry built here follows R8–R11; the row
itself changes in `identity-rename`'s own change (R9 says so explicitly). Named here so no session
reads the row as a contradiction to fix from this program.

---

## 13. DESIGN-GATE §5 checklist

```
[x] I identified the subsystem(s) this touches: seedsmith (core boundary + a new adapter), the
    dungeon adapter, Delve events, story-scene, i18n/lingui, runtime storylets (as a consumer), ip-censor,
    product vision (loops), tunables (runtime-owned).
[x] Session boundary recorded: tasks/sessions/narrative-programs-spec-20260919.json; this file is in
    its paths. I did not run session-boundary-check.py in this pass (docs-only, one new file).
[~] I read the §1 row docs this session: the narrative-seed ideal in full; npc-story-events-ideal §6.12,
    §8, §10, §11; ip-censor-ideal "Narrative generation" and "Owner rulings"; the seedsmith-design and
    spec-driven-development skills; DESIGN-GATE §1 (product vision, tunables, creature-seed rows) and §5;
    the creature-seed, seedsmith (P1-P5, §3d, §4, §5), story-scene and ip-censor maps;
    ai-native-generation README by heading. Not read in full this session: the-game.md, the-loops.md,
    tunables-ssot.md, validation-ssot.md, item/seed-contract.md, spec-pipeline.md — their load-bearing
    rules are restated from the ideal and AGENTS.md, and the module specs must read them.
[x] I checked decisions.md for a lock: Product vision (line 109, tension recorded in §12), Standalone-first,
    Creature program. No row locks the narrative seed contract.
[x] Every factual claim cites file:line.
[x] audit-doc-citations.py --scope on this doc: 0 HIGH (94 citations; 9 D1 findings, all of them files marked "(new)" or not yet built, reported LOW; re-run 2026-09-23 by NS70, which added 4 resolvable citations and no D1).
[x] I verified claims against code, not comments: the model-literal count, TryInstantiate call sites, the
    motif and displayName scripts, the event corpus readings and every cited line were re-read or re-counted.
[x] I read the surrounding section of every rule quoted.
[x] No constraint reported as "moves goldens" or "needs sign-off"; none was assumed.
[x] Nothing contradicts a §2 invariant.
[x] Corrections are propagated: the ideal's stale claims are listed in §3.5 for the ideal's owner to fix;
    this pass edits only this file.
[x] No assertion pins a derived-population count, an item total or generated text; §10 separates
    contract checks from readings.
[x] No event-refreshed cache is introduced.
[x] No acceptance criterion fixes an ordering that can vary in real play.
[x] Actor numbers: N/A. Narrative seeds produce no actor combat or derived magnitude; outcome effects
    are {family, powerBand} resolved by the runtime through Instantiator and P(Θ).
[x] No SOLID-violating parallel path: one storylet generator (the dungeon event kind moves in), one
    roll SDK, one translation system, one scene player, one IP registry.
[ ] New rule registry rows: not yet. The no-model-literal test, the no-digit-in-prose audit and the
    no-literal-name validator each need a row in gk-core/scripts/enforcement-registry.v1.json; the module specs
    add them.
```

---

## Open questions

None. Every design question the ideals raised was answered by the owner on 2026-09-19 (R1–R13,
IC-1 to IC-6). The remaining gate is approval of this map.

---

## Standards audit (2026-09-19)

Independent adversarial review against `docs/research/ai-native-generation/README.md` §10, seedsmith P1–P5,
`seedsmith/spec-pipeline.md` §3, `spec-quality-gates.md`, `spec-workflow-runtime.md`, `validation-ssot.md`,
`tunables-ssot.md`, `item/seed-contract.md` §2–§7, `DESIGN-GATE.md` §3/§5, owner rulings R1–R13 and IC-3, and
the runtime contracts (`npc-story-events/spec-storylet-contract.md`, `spec-narrative-text.md`). Every change
in the body is marked "Audit 2026-09-19" (or "Owner ruling 2026-09-19 (round 4)" where the owner ruled).

| # | Severity | Finding | Status |
|---|---|---|---|
| 1 | high | Owner ruling 2026-09-19 (round 4): the "Pending" paragraph replaced; Wave 0 now runs `gloss-fill` and the legacy regeneration; rows 4, 17, 22, principle 8, §3.4, §5 note, §7 ownership row and the §10 reading updated | fixed |
| 2 | low | Row 5 `bring:{tag}` disagreed with the spec's element argument family | fixed |
| 3 | low | §13 left the registry rows owed | deferred — proposed rows below; `gk-core/scripts/enforcement-registry.v1.json` is outside this audit's fence |

**Proposed enforcement-registry rows (not added — shared file):** `seedsmith-no-model-literal` (guard
`gk-forge/tools/seedsmith/tests/test_no_model_literal.py`); `narrative-no-digit-in-prose` (guard
`tools/seedsmith/tests/test_narrative_contract.py`); `narrative-no-literal-name` (guard
`tools/seedsmith/tests/test_narrative_validators_text.py`); `narrative-call-schema-blocked-and-closed` (guard
`tools/seedsmith/tests/test_narrative_contract.py`); `narrative-no-raw-motif-in-brief` (guard
`gk-forge/tools/seedsmith/tests/test_briefkit_gloss.py`); `narrative-r13-counter-doctrine` (guards
`gk-forge/tools/seedsmith/tests/test_narrative_character_vocab.py`, `test_narrative_validators_structure.py`);
`legacy-delve-event-keyed-text` (guard `gk-forge/tools/seedsmith/tests/test_dungeon_commit.py`);
`narrative-no-hand-edit-generated` (guard `gk-core/scripts/guard-generated-seed.py` once its narrative tree row lands);
`narrative-open-loop-never-gates` (guard `tools/seedsmith/tests/test_narrative_metrics.py`);
`narrative-voice-quality` (unguardableReason: *whether a line is in character is open-loop; review verdicts
record it and no scan can pass it*).

## Owner ruling 2026-09-20 (round 5)

**R19 — world storylet climate is derived from the sector type.** `storylet-vocab` authors a closed registry
`data/seed/narrative/_registry/sector-climates.v1.json` (new): one row per sector type of
`gk-core/src/FusionRpg.Core/World/SectorTypeCatalog.cs:55-102` (read, never edited) → an element or `none`, each with its reason
(`spec-storylet-vocab.md` §3.9). World host rows lose `climateNeutral` and gain the climates they can present; the
planner's world grid gains climate cells (§9 row above; `spec-narrative-planner.md` §1); the contract's `climate` rule
follows (`spec-narrative-contract.md`). The Delve keeps its per-room climate; expedition hosts stay neutral because an
expedition carries no destination sector (`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Expeditions.cs:10-12`). The runtime reads
the registry through `npc-story-events`' `narrative-vocabulary` and passes the derived climate into selection
(`npc-story-events/spec-world-events-host.md` §3). **Open for the owner:** world sectors already carry a per-sector era
climate that world-map uses for spawns and raises (`gk-core/src/FusionRpg.Core/World/WorldState.cs:153-154`), which can differ
within a type; R19 follows the type (`spec-storylet-vocab.md` §3.9 "Known divergence").

## Owner ruling 2026-09-20 (round 6)

**R20** supersedes R19: `sector-climates.v1.json` is never authored (`spec-storylet-vocab.md` §3.9 kept as trail);
world host rows are `climateSource: sector` with all seven climates, and the runtime passes the sector's own climate
(`gk-core/src/FusionRpg.Core/World/WorldState.cs:153-154`) into selection. The round-5 open question above is closed. The world
grid note in §9 is updated.
