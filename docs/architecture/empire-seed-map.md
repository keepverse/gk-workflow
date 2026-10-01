# Capability map: `empire-seed`

**Status: APPROVED 2026-09-19.** The owner approved the module boundaries, the dependency direction and
the build order below, confirmed D-E1 (the `exchange` role) and D-E2 (`empire-seed` owns the structure
corpus), and decided §12 question 1 (the three rows outside the generator move into its source — see
§12). Module specs are written (spec phase, 2026-09-19); no build is authorized until each spec is
approved.

**Program id:** `empire-seed` (stable; every downstream spec, plan and task selects work by the module
ids in §4).
**Ideal:** [empire-seed-ideal.md](empire-seed-ideal.md) (idea phase, 2026-09-19; owner decisions D-E1
and D-E2 in its §9). This map does not reopen those decisions. It cuts the work into modules that can
be specified and verified one at a time, and it corrects the ideal where the code says otherwise (§11).
**Sibling documents this map is bound by:** [structure-seed-ideal.md](structure-seed-ideal.md) (the
structure anchor's design record), [legion-build-ideal.md](legion-build-ideal.md) §6.7 and §7 (the
legion families), [narrative-seed-ideal.md](narrative-seed-ideal.md) (storylets belong to the
`narrative` adapter), [trade-network-ideal.md](trade-network-ideal.md) §11 (the umbrella).
**Session record:** `tasks/sessions/trade-network-idea-20260919.json` (its `paths` include this file).
**Artifact paths:** module specs at `docs/architecture/empire-seed/spec-<module-id>.md` (all fifteen
written 2026-09-19); plan and task list at `tasks/empire-seed-plan.md` and `tasks/empire-seed-todo.md`
(not written yet).

> **The program in one sentence.** seedsmith fills the world and empire with catalogs of things —
> structures first, legion content once its mechanics exist — through a registered adapter, a
> deterministic planner that decides every enum, a model that only names and describes, and one shared
> C# reader that turns each seed's ordinals into numbers from `gk-core/data/tuning/` bands at load time.

---

## 1. Which loop this extends

Content supply only. It adds no loop, currency, stat or player surface of its own.

- **Place 5 — World stage** (buildings are what you build there) and **Place 3 — Farm, hunt, defend**
  (yield, storage, defence structures): the structure corpus.
- **Place 4 — World map** (legions, their standards and doctrines on lanes): the legion families.
- **Place 7 — Quests and events**: **not here.** Trade storylets are rows the `narrative` adapter emits
  (`narrative-seed-ideal.md` §6.1 refuses a second storylet generator); this program contributes no
  generator for them (§8).

---

## 2. Principles, restated inline

Restated rather than linked, because a downstream session reads this document and not its links.

1. **Seed → concrete → per-player.** seedsmith emits seeds offline: enums, ordinals, registry ids and
   identity text, committed and diffable. Deterministic stats are shared by every player (as species
   stats are); only effects roll, and only through the one roll SDK, `Instantiator.TryInstantiate`.
   **This program designs no roll.** Legion equipment does not roll at all (owner, 2026-09-19).
2. **The model writes identity; deterministic code writes magnitude.** *"A model has no calibrated
   sense of scale, so a number it picks is a plausible-looking guess that survives review because
   nothing looks wrong with it."* An author may write a count, a reference, an enum or a band —
   *"never a magnitude, never a weight, never a probability, never a quantity"*
   (`item/seed-contract.md` §3). Enforced by the schema audit, never by review.
3. **Four ownership levels; a field with none is a contract defect** (`item/seed-contract.md` §2):
   AUTHORED, DERIVED (*"the importer computes it from authored fields — a column, never the seed"*),
   GENERATED, VALIDATED. **Structure and legion magnitudes are DERIVED**, which is why this map resolves
   them at load (§5 `band-reader`) rather than emitting a `gk-data/packs/fusion/data/generated/` tree.
4. **Generated data is never hand-edited.** Change the generator, its tuning or its registry,
   regenerate, commit the diff. Hand-author only registries, `_exemplars/` and hand-authored kinds.
   `gk-core/data/tuning/**` is published as `v{n+1}` through `gk-core/tools/tuning/publish.py`, never edited in place.
5. **The plan is deterministic (P4); a planner runs before any model call** (base-defense decision 33).
   For invented content the planner fixes every enum; the model receives the drawn enums and writes
   only name, flavour and reason.
6. **Every metric declares closed or open loop (P3); a metric without a declared target is an opinion
   (P2).** An open-loop metric produces a review queue and never contributes to a pass.
7. **A guardrail validates the contract, never a population** (`validation-ssot.md`). Assert envelope,
   closed-enum membership, joins, uniqueness, reconciliation, determinism and structural bounds. Never
   pin how many structures, standards or doctrines exist, never assert generated text, never pin a
   per-cycle outcome. Pin a literal only for a closed vocabulary the code owns, and say why.
8. **AI-native contract rules** (`docs/research/ai-native-generation/README.md`): permute every enum
   seeded from `(entity_id, field, sample_index)`; vote only load-bearing fields the model actually
   chooses; a 1-1-1 split is `unresolved`, never the first option; every attribute description has a
   negative clause; `none` is a value and a missing key is a defect; prove constrained decoding with one
   real call before a run; transient and quality retries are separate paths, quality repairs bounded at
   two; tests never call a model (the transport stub raises); compute the call budget before the run.
9. **One power ladder, the balance surface is data, no hard ceilings, range-safe numbers.** Bands
   resolve through `gk-core/data/tuning/`, reading `P(Θ)` where a magnitude scales; integer magnitudes are
   `long`, widen before multiplying, integer overflow throws; floating point is allowed (owner ruling
   2026-09-15). A missing tunable is a load rejection naming it (tunables-ssot T5). **Core never reads a
   file; hosts load and inject** (tunables-ssot T8).
10. **Rarity buys breadth and ceiling, never power; tier is not a distinctness axis.** *"A stronger
    version is not a different unit."* A tier chain is a `variants` list, not four rows.
11. **Every actor number composes once in `ActorHub`.** Legion standards, traditions, doctrines and
    legion equipment reach a creature only through a registered subsystem or atom reader with a GG-49
    SourceId, owned by `legion-build`. This program emits seeds; it never folds an actor number.
12. **SOLID.** One structure corpus, one seed reader shape, one band resolver, one writer per generated
    tree. A new family extends the shared piece; it never forks it.

---

## 3. What the gate reading found in code (2026-09-19)

Sorted with the gate's words. Every row was re-read in this session; §11 lists where this contradicts
the ideal.

### 3.1 Built

| What | Evidence |
|---|---|
| The adapter protocol the core measures through | `gk-forge/tools/seedsmith/seedsmith/adapters/base.py:95-100` (`SeedAdapter`), `KindSpec` at `:23-61` |
| Registered adapters: `stub`, `items`, `creatures`, `actions`, `dungeon` | `gk-forge/tools/seedsmith/seedsmith/adapters/registry.py:12-18` |
| The structure anchor schema: every field an enum, ordinal, registry id or free text, `additionalProperties: false`, ownership per field | `gk-forge/tools/seedsmith/seedsmith/adapters/structures/anchor/schema.py:41-55` (vocabularies), `:94-110` (`OWNERSHIP`), `:152-207` (builder) |
| A deterministic planner with a committed plan, a tier ladder read from tuning, a stated call budget and a gate that raises before any model call | `gk-forge/tools/seedsmith/seedsmith/adapters/structures/planner.py:38`, `:78`, `:94-112`, `:134-166`; committed `gk-data/packs/fusion/data/seed/structures/_plan.json` |
| Corpus metrics with a declared loop and target per metric; open-loop metrics cannot fail a report | `gk-forge/tools/seedsmith/seedsmith/adapters/structures/metrics.py:215-224`, `Report.passed` reads closed-loop results only |
| A byte-identical rerun proven by hash | `gk-forge/tools/seedsmith/tests/test_structure_corpus.py`, `test_rerun_is_byte_identical_proven_by_hash` |
| A decision-43 identity guard against the real PvZ almanac dump | `gk-forge/tools/seedsmith/tests/test_structure_corpus.py`, `test_no_pvz_plant_appears_in_the_corpus` |
| The C# reader and catalog: corpus → `StructureDef`, loud validation | `gk-core/src/FusionRpg.Core/World/StructureSeed/StructureCorpus.cs:88-107`; `gk-core/src/FusionRpg.Core/World/StructureCatalog.cs:255-280`, `:350-430` |
| Enum permutation and majority vote, reusable by any adapter | `gk-forge/tools/seedsmith/seedsmith/adapters/structures/generate_anchor.py:25-26` imports `order_for` and `resolve_vote`/`resolve_set_vote` from the creatures adapter |
| The structure pipeline resolves its model through the config layer (no model literal) | `gk-forge/tools/seedsmith/seedsmith/adapters/structures/generate_anchor.py:28` (`LlmCallerConfig`) |
| An atom-family namespace validator another adapter already uses | `gk-forge/tools/seedsmith/seedsmith/adapters/actions/distribution_planner/derive.py:585` |

### 3.2 Wiring gap (exists, inert — not a wall)

| What is inert | The inert line |
|---|---|
| **`structures` bypasses the adapter protocol.** Its `__init__.py` is empty and it is not in `ADAPTERS`, so the generic `check`/`metrics` CLI cannot see the corpus; only `structures contract` is wired | `gk-forge/tools/seedsmith/seedsmith/adapters/registry.py:12-18`; `gk-forge/tools/seedsmith/seedsmith/report/cli.py:2242-2249` |
| **The planner and metrics measure the generator's in-memory rows, not the committed corpus.** Both `__main__` blocks import `ALL_ROWS`; three rows on disk (`relic-vault`, `standing-stones`, `sunspire-throne`) are outside the generator, so the committed plan counts fewer rows than the corpus holds | `gk-forge/tools/seedsmith/seedsmith/adapters/structures/planner.py:174-179`; `metrics.py:259-264`; `generate_corpus.py:468` |
| **Magnitudes live in the seed.** Playable rows carry a `magnitudes` block, written as literals by the generator (`cost=200`, `build_turns=2`, …) that transcribe `loam.v4.json` by hand | `gk-forge/tools/seedsmith/seedsmith/adapters/structures/generate_corpus.py:255-300`; `gk-core/src/FusionRpg.Core/World/StructureSeed/StructureCorpus.cs:126-168` |
| **Identity-only rows are never loaded.** A row without `magnitudes` is skipped; 17 of the 28 committed rows have none (counted this session — a reading), including `convoy-depot`, `causeway`, `coffer`, `stockyard`, `workshop`, `reliquary`, `refinery` | `gk-core/src/FusionRpg.Core/World/StructureSeed/StructureCorpus.cs:65`; `gk-core/src/FusionRpg.Core/World/StructureCatalog.cs:275` |
| **A band resolver exists and nothing in production calls it.** `Bands.MaterialTierOf` hardcodes the tier ladder a second time beside `bands.tierLadder` in tuning; only tests call it | `gk-core/src/FusionRpg.Core/World/Bands.cs:20-28`; `gk-core/data/tuning/structure-seed.v1.json:17`; callers `gk-core/tests/FusionRpg.Core.Tests/World/StructureCatalogImportTests.cs` only |
| **Structure cost has two sources.** `LoamPolicy` exposes every structure magnitude from `loam.v{n}.json`'s `structures` block; **no production code reads them** (grep this session: only a doc comment at `gk-core/src/FusionRpg.Core/Stats/Derived/StatClass.cs:88`), while tests use them as oracles for catalog values. `WaystationRangeHops` is the exception — a build rule, read at `gk-core/src/FusionRpg.Core/World/Movement/BuildResolver.cs:192` | `gk-core/src/FusionRpg.Core/World/Loam/LoamPolicy.cs:122-191`; `gk-core/tests/FusionRpg.Core.Tests/World/Loam/LoamStructuresTests.cs:42` |
| **The structure role is not validated in C#.** `StructureCorpusRow.Role` is a free string; the closed role list exists only in Python | `gk-core/src/FusionRpg.Core/World/StructureSeed/StructureCorpus.cs:119`; `gk-forge/tools/seedsmith/seedsmith/adapters/structures/anchor/schema.py:41` |
| **`ROLE_TO_STRUCTURE_KIND` is known wrong and still shipped.** It maps Extract/Multiply → `LoamSource` and Bank → `Storage`; the real rows are `Yield`, and the C# catalog ignores it | `gk-forge/tools/seedsmith/seedsmith/adapters/structures/anchor/schema.py:64-69`; `gk-core/src/FusionRpg.Core/World/StructureCatalog.cs:282-288` |
| **Core reads files.** `StructureCorpus.Load` calls `File.ReadAllText` inside Core, against tunables-ssot T8 | `gk-core/src/FusionRpg.Core/World/StructureSeed/StructureCorpus.cs:95`; the host call is `gk-core/src/FusionRpg.Server/Program.cs:223-224` |
| **The structure pipeline has no emit path and writes no name.** `generate_anchor.py` votes enums per field and records provenance; nothing writes an accepted row to disk, and the anchor has no flavour field | `gk-forge/tools/seedsmith/seedsmith/adapters/structures/generate_anchor.py:52-65`, `:186-221`; schema `gk-forge/tools/seedsmith/seedsmith/adapters/structures/anchor/schema.py:157-198` |
| **`gk-forge/tools/seedsmith/**`, `gk-data/packs/fusion/data/seed/structures/**` and `data/tuning/structure-seed.*` have no verification boundary** — `verify-change.py` throws for them; seedsmith's pytest runs only in CI | `gk-core/scripts/verify-change.py:771`; owned by `test-verification-boundary`'s `python-test-lane` |

### 3.3 Real gap (no mechanism anywhere)

| What | Why it matters |
|---|---|
| A shared C# seed-plus-bands reader and band resolver | Every new world family would otherwise hand-roll a reader like `StructureCorpus.cs` |
| An `exchange` structure role (D-E1) | No role clears exchanges; `enable` would mean two things |
| World-family exemplars and a tone brief | Exemplars exist only for items; invention needs a hand-authored distribution to extend |
| An invention-shaped naming stage (enums drawn, then named) with a cross-corpus dedup index | `generate_anchor.py` is classification-shaped (it votes enums) and writes no name |
| Legion seed contracts (standard, tradition, doctrine, legion equipment) | Content `legion-build` needs; its vocabularies (legion slots, tradition trigger facts) do not exist yet |
| Legion mechanics: layer 5c, `OwnerKind.Legion`, stack `Count`, a stack-scoped equipment layer | `gk-core/src/FusionRpg.Core/Effects/Atoms/OwnerScope.cs:20-30` has no `Legion`; `world-buff` is declared and never bound (`gk-core/src/FusionRpg.Core/Effects/Atoms/ContainerRow.cs:38`, `:203`). **Owned by `legion-build`, not this program** |

---

## 4. Modules

Fifteen modules. **Model?** says whether the module itself spends model calls. Ids are stable and
kebab-case; the ideal's I1–I5 keep their ids.

| # | Module id | Capability (one line) | Model? | Depends on |
|---|---|---|---|---|
| 1 | `structures-adapter` | Implement `SeedAdapter` for structures over the committed corpus on disk and register it in `ADAPTERS` (ideal I1) | no | — |
| 2 | `band-reader` | One C# seed-plus-bands reader and band resolver shared by every world family, fed by the host (ideal I2) | no | — |
| 3 | `world-budgets` | Per-role and per-cell budget targets as tuning values; tests read them instead of literals (ideal I5) | no | `structures-adapter` |
| 4 | `structure-bands` | Move every structure number out of the seed into `structure-seed` tuning bands; byte-identical catalog; one writer for the tree; delete `LoamPolicy`'s unread structure magnitudes (ideal I3) | no | `band-reader`, `structures-adapter` |
| 5 | `exchange-role` | Widen the closed role list with `exchange` (D-E1) in Python, the C# role registry and the docs together | no | `structure-bands`, `world-budgets` |
| 6 | `decision-45-revision` | Move ownership of the structure corpus to `empire-seed` (D-E2) in every document that still gives it to `base-defense` | no | — (lands after map approval) |
| 7 | `world-exemplars` | Hand-authored exemplars per structure role (including `exchange`) plus the tone brief every family's naming prompt carries (ideal I4) | no | `exchange-role` |
| 8 | `world-name-index` | A deterministic index of every existing name across every corpus plus the shared IP avoid-list, used as the dedup and block input to every naming call | no | `structures-adapter` |
| 9 | `corpus-metrics` | Close the metric set over the committed corpus: closed-loop contract metrics, open-loop review queues | no | `structures-adapter`, `structure-bands`, `world-budgets` |
| 10 | `call-budget-dry-run` | The planner's invention-shaped call budget and a `--dry-run` that renders every prompt and calls nothing | no | `world-exemplars`, `world-name-index` |
| 11 | `world-namer` | The one model stage: a planned entry with drawn enums → name, flavour, reason; validators; freeze on accept; provenance, `stale_ids`, byte-identical rerun | **yes** | `call-budget-dry-run`, `corpus-metrics` |
| 12 | `trade-structure-rows` | The **eight** feature buildings (seven from round 4, the Standard Hall from round 6 L6), one row each with its tiers as `variants`: Storehouse (`Store`), Counting House (`Bank`), Trading Post (`Exchange`), Caravan Yard (`Move`), Rift Anchor (`Move`), Embassy (`Enable`), Workshop (`Refine`), Banner Yard (`Refine`, the Standard Hall ladder); the `featureUnlock` anchor field and the neutral `structureKind: Feature` (§12b, §16) | no (owner-named; `world-namer` only for a deficit outside them) | `exchange-role`, `structure-bands`, `world-name-index` |
| 13 | `legion-seed-contract` | The `legion` adapter, four seed schemas — standard, tradition, doctrine, legion equipment — with ownership levels and no numbers, and their hand-authored exemplars | no | `band-reader`, `world-exemplars` |
| 14 | `legion-bands` | Legion seed bands in tuning: tier → fixed stats resolved once, identically for every player; standard tier and tradition rank ladders | no | `legion-seed-contract`, `band-reader` |
| 15 | `legion-seed-rows` | Planner-first legion seeds over the element × doctrine trade-off grid and the legion slot × tier grid | **yes** (runs `world-namer`) | `legion-bands`, `world-namer` |

### Why these boundaries

- **`band-reader` is separate from `structure-bands`** because it is the shared piece: legion families
  consume it without touching structures. Merging them would make the reader structure-shaped by
  accident (the P5 failure the seedsmith core already refuses).
- **`world-budgets` is separate from `corpus-metrics`** because its acceptance is a tuning-file and
  test change with no new metric, and `exchange-role` needs it before any metric work.
- **`exchange-role` is its own module** because widening a closed vocabulary is a reviewed change with
  its own consumers (Python, C#, four documents); folding it into `trade-structure-rows` would hide the
  vocabulary change inside a content batch.
- **`world-name-index` is separate from `world-namer`** so the dedup and block inputs are reviewable
  and testable with zero tokens, and so legion naming reuses them unchanged.
- **One naming stage (`world-namer`), not one per family.** Structures and legion seeds share the same
  shape — enums fixed by a planner, identity text written by a model — so a second namer would be the
  fork principle 12 forbids.
- **Legion families are three modules and come last** because their vocabularies belong to
  `legion-build` and do not exist yet (§3.3). The contract module can land as soon as those vocabularies
  are approved; the rows wait on the mechanics.
- **Legion exemplars belong to `legion-seed-contract`, not `world-exemplars`.** An exemplar must validate
  against its kind's schema, so authoring it before the schema exists would make the contract depend on
  its own exemplars. The cross-program order this fixes, against
  [legion-build-map.md](legion-build-map.md) (modules `legion-standards`, `legion-traditions`,
  `legion-doctrine`, `legion-equipment`, whose tests run on this program's exemplars): **legion-build
  approves its vocabularies at spec time → `legion-seed-contract` lands schemas and exemplars →
  legion-build builds its modules on those exemplars → `legion-seed-rows` generates.** The edge into
  this program is an approved spec, not built code, so the two programs do not wait on each other in a
  cycle.

---

## 5. Module detail

Each block: capability · built / wiring gap / real gap · depends on · touches · acceptance (contract
level) · verification boundary · open question (only where genuinely open).

### 5.1 `structures-adapter` (ideal I1)

**Capability.** A `StructuresAdapter` implementing `SeedAdapter` — one `KindSpec` for
`structure-anchor` (directory `structures`, id pattern kebab, required fields from the schema), the
`role` and `requiredSlotKind` dimensions, a real legality function (role × slot kind from the committed
plan's `legalRoleSlotPairs`, with a genuine `False` case), the closed vocabularies as a `RegistrySet`,
and an empty `channels()` with a comment saying why (structures own no stat channel). Registered in
`ADAPTERS`. The planner and metrics entry points read the **committed corpus on disk** through the
adapter, so every row the game loads is a row the planner counts.

- **Built:** the protocol (`adapters/base.py:95-100`), the schema (`structures/anchor/schema.py:152-207`),
  the planner and metrics functions (they take `rows` as a parameter already).
- **Wiring gap:** not registered (`adapters/registry.py:12-18`); planner and metrics `__main__` read
  `ALL_ROWS` (`structures/planner.py:174-179`, `structures/metrics.py:259-264`); the committed
  `_plan.json` therefore omits the three hand-authored rows.
- **Real gap:** none.
- **Depends on:** —.
- **Touches:** `gk-forge/tools/seedsmith/seedsmith/adapters/structures/__init__.py`, `adapters/registry.py`,
  `structures/planner.py` and `structures/metrics.py` entry points, `gk-data/packs/fusion/data/seed/structures/_plan.json`
  (regenerated by the planner, never by hand), new tests under `gk-forge/tools/seedsmith/tests/`.
- **Acceptance.** `resolve_adapter("structures")` returns an object that satisfies `SeedAdapter`;
  the generic `check` and `metrics` commands run on `gk-data/packs/fusion/data/seed/structures` with no structure-specific
  code in the core; the legality function returns `False` for at least one real pair; the plan's
  counted rows equal the entries on disk (a reconciliation, never a literal); the regenerated plan is
  byte-identical across reruns; the adapter conformance suite the `_stub` adapter already runs passes
  for `structures`.
- **Verification:** `python -m pytest gk-forge/tools/seedsmith/tests/test_structure_planner.py
  gk-forge/tools/seedsmith/tests/test_structure_metrics.py gk-forge/tools/seedsmith/tests/<new adapter test> -q`
  (pytest; no local boundary yet — §3.2).

### 5.2 `band-reader` (ideal I2)

**Capability.** One C# reader for every seed file in the shared `{"kind", "_meta", "entries"}` shape,
filtered by `kind`, and one band resolver that turns a declared ordinal into a number from a tuning
band table, throwing on an unauthored ordinal or a missing band (T5). The **host** loads the files and
the tuning and injects them (T8); Core never touches the file system. A family declares its ordinal
vocabularies and band tables once; `StructureCatalog` and the legion catalogs are its consumers. It
also validates each VALIDATED field against its registry (for structures: role, slot kind, rarity,
acquisition path).

- **Built:** the file shape and a kind-specific reader (`StructureCorpus.cs:88-107`); a single
  hardcoded resolver (`Bands.cs:20-28`); the `StructureDef` validation discipline
  (`StructureCatalog.cs:350-430`).
- **Wiring gap:** `Bands.MaterialTierOf` has no production caller and duplicates `bands.tierLadder`;
  `StructureCorpus.Load` reads files inside Core (`StructureCorpus.cs:95`).
- **Real gap:** the shared reader and resolver themselves.
- **Scope note — what this does not absorb.** `ConcreteSpeciesSeedReader`
  (`gk-core/src/FusionRpg.Core/Creatures/Generation/ConcreteSpeciesSeedReader.cs:25`) reads **GENERATED**
  concrete species already resolved offline; this reader serves **DERIVED** magnitudes resolved at
  load. Two ownership levels, two readers — not a SOLID fork (correction to the ideal, §11).
- **Depends on:** —.
- **Touches:** new files under `gk-core/src/FusionRpg.Core/World/StructureSeed/` (or a neutral
  `src/FusionRpg.Core/Seeds/` namespace — a spec-time naming choice), `gk-core/src/FusionRpg.Core/World/Bands.cs`
  (retired into the resolver), `gk-core/src/FusionRpg.Server/Program.cs:223-224` (host injection), the test
  bootstraps that call `StructureCorpus.Load` (`gk-core/tests/FusionRpg.Core.Tests/World/StructureCatalogTestBootstrap.cs`,
  `gk-core/tests/FusionRpg.Data.Tests/StructureCatalogTestBootstrap.cs`, `gk-core/tests/FusionRpg.Server.Tests/PowerAndAptitudeTuningTestBootstrap.cs`).
- **Acceptance.** An ordinal not in its declared vocabulary, or with no band row, is a load rejection
  naming the family, the field and the value; a VALIDATED value outside its registry is a load
  rejection; the same inputs produce the same resolved rows in the same order regardless of file
  enumeration order; the reader never opens a file (a guard or test proves Core has no `File.` call on
  this path); integer magnitudes resolve as `long` with `checked` arithmetic; the tier ladder has one
  source (the tuning file).
- **Verification:** `FusionRpg.Core.Tests` via
  `.\scripts\verify-change.ps1 -Paths <changed files> -Session <id>` (`core-fallback` /
  `core-tests-fallback` boundaries).

### 5.3 `world-budgets` (ideal I5)

**Capability.** Every corpus target is a declared tuning value, and every test reads it. The per-role
budget and the density band **already exist in tuning** (`gk-core/data/tuning/structure-seed.v1.json:3-14`,
`:23`); what is missing is that three places restate the band as literals, and two tests pin
population counts. This module removes the literals and pins, adds the `exchange` budget row (published
as `structure-seed.v2`), and declares the legion budget shape (element × doctrine trade-off cells,
legion slot × tier cells) for `legion-bands` to publish.

- **Built:** `budget`, `metrics.densityBand`, `metrics.roleCountTolerance` in
  `gk-core/data/tuning/structure-seed.v1.json`; `check_plan` reads the band (`structures/planner.py:146`).
- **Wiring gap:** density restated as literals at `gk-forge/tools/seedsmith/tests/test_structure_corpus.py:192-195`,
  `gk-forge/tools/seedsmith/tests/test_structure_planner.py:58-60` and the declared target string at
  `structures/metrics.py:217`.
- **Real gap:** none for structures; the legion budget block does not exist.
- **Also owed (validation-ssot):** population pins at `gk-forge/tools/seedsmith/tests/test_structure_corpus.py:149`
  (`len(DUMPED_ROWS) == 8`) and `:312-317` (`== 17`, `== 25`) become reconciliations.
- **Depends on:** `structures-adapter` (the budget is checked through the adapter's distribution
  metric).
- **Touches:** the two test files above, `structures/metrics.py`, `data/tuning/structure-seed.v2.json`
  (published through `gk-core/tools/tuning/publish.py`, extending it with a key-add path if `set` refuses the
  new role row).
- **Acceptance.** No seedsmith test contains a density or corpus-size literal; each reads the tuning
  value or asserts a relationship (`len(plan rows) == entries on disk`); changing the published band
  moves the verdict without a code edit; the budget file declares a target for every role in the closed
  role list and no role outside it.
- **Verification:** `python -m pytest gk-forge/tools/seedsmith/tests/test_structure_corpus.py
  gk-forge/tools/seedsmith/tests/test_structure_planner.py gk-forge/tools/seedsmith/tests/test_structure_metrics.py -q`;
  `python gk-core/tools/tuning/publish.py` dry path for the new version.

### 5.4 `structure-bands` (ideal I3)

**Capability.** Every structure number leaves the seed. The anchor keeps identity, ordinals and the
**mechanism enums** that are not magnitudes (`structureKind`, `obstacleKind`, `wonderScope`,
`wonderRarity`, `wonderEffects[].kind`, movement and fire blocking); every number (cost, build turns,
yield multiplier, flat yield, capacity, item capacity, construct costs, cover, entry stamina, vision,
material tier, relic cost, wonder effect values) resolves from `structure-seed` tuning bands through
`band-reader`. The corpus is regenerated **through its generator**, never by hand. The unread
`LoamPolicy` structure magnitudes are deleted.

- **Built:** the catalog (`StructureCatalog.cs:289-328`), the playable rows' numbers, the tier ladder
  in tuning.
- **Wiring gap:** literals in the generator (`structures/generate_corpus.py:255-300`); the `magnitudes`
  block (`StructureCorpus.cs:20-48`, `:126-168`); `LoamPolicy.cs:122-191` read only by tests;
  `ROLE_TO_STRUCTURE_KIND` (`gk-forge/tools/seedsmith/seedsmith/adapters/structures/anchor/schema.py:64-69`) contradicting the shipped rows; the seedsmith test
  still compares against `loam.v4.json` (`gk-forge/tools/seedsmith/tests/test_structure_corpus.py:75`) while the
  server loads `loam.v5.json` (`gk-core/src/FusionRpg.Server/Program.cs:36`) — identical `structures` blocks
  today, a stale reader tomorrow.
- **Real gap:** band tables for the numeric fields.
- **Obligations the acceptance must carry:**
  1. **One writer for the tree.** The three rows outside the generator (`store/relic-vault.json`,
     `wonder/standing-stones.json`, `wonder/sunspire-throne.json`) move into the generator's source (§12
     question 1), and the `wonder/` directory stops disagreeing with its rows' `partition` (`Extract`,
     `Bank`), which `test_file_tree_groups_by_role_directory` asserts for every generator row.
  2. **Band granularity follows the shipped numbers.** Today one `costProfile` value (`moderate`)
     covers costs 0, 150, 200 and 300, so a three-rung `costProfile` cannot reproduce the catalog.
     Decided by principle (one mechanism, `item/seed-contract.md` §3): **widen the ordinal vocabularies
     until every shipped number is some rung's value** and let the generator re-emit the anchors with
     the finer ordinals; a per-structure override table in tuning would be a per-row magnitude under
     another name. Tier zero (indestructible) becomes an explicit value rather than a `magnitudes`
     side-channel (`generate_corpus.py:61-66` explains why `materialTier` bypassed `strengthBand`).
  3. **`StructureKind` becomes a VALIDATED anchor field** chosen by the planner, and
     `ROLE_TO_STRUCTURE_KIND` is deleted — the C# catalog already treats the row's kind as
     authoritative (`StructureCatalog.cs:282-288`).
  4. **Refactor only (T7).** No resolved number changes in this module; a rebalance is a separate
     `v{n+1}` publish.
  5. **`LoamPolicy` deletion.** Delete the structure magnitudes at `LoamPolicy.cs:122-191` except
     `WaystationRangeHops` (a build rule, `BuildResolver.cs:192`, not a structure magnitude — it stays
     in loam tuning or moves to `structure-seed` by the spec's choice); retarget the test oracles
     (`gk-core/tests/FusionRpg.Core.Tests/World/Loam/LoamStructuresTests.cs`, `LoamTextureTests.cs`,
     `gk-core/tests/FusionRpg.Core.Tests/World/Turn/DistrictAssaultResolverTests.cs:256`) to
     `StructureCatalog.Get(...)`; publish a loam version without the block and update `LoamTuning`'s
     parser in the same change.
  6. **Two stale claims corrected in the same change:** `gk-core/data/tuning/loam-relics-wonders.v1.json`
     `_meta.note` (republished) and `gk-core/src/FusionRpg.Core/World/Loam/WonderTuning.cs:10` both say per-row
     magnitudes live in seed content.
- **Depends on:** `band-reader`, `structures-adapter`.
- **Touches:** `gk-forge/tools/seedsmith/seedsmith/adapters/structures/{generate_corpus.py,anchor/schema.py,anchor/descriptions.py,planner.py}`,
  `gk-data/packs/fusion/data/seed/structures/**` (regenerated), `data/tuning/structure-seed.v{n}.json`,
  `data/tuning/loam.v{n}.json`, `gk-core/src/FusionRpg.Core/World/StructureSeed/StructureCorpus.cs`,
  `gk-core/src/FusionRpg.Core/World/StructureCatalog.cs`, `gk-core/src/FusionRpg.Core/World/Loam/{LoamPolicy.cs,LoamTuning.cs,WonderTuning.cs}`,
  and every test that writes a temporary corpus with a `magnitudes` block (grep
  `StructureCorpus.Load(tmp)` across `gk-core/tests/FusionRpg.Core.Tests`, `gk-core/tests/FusionRpg.Data.Tests`,
  `gk-core/tests/FusionRpg.Server.Tests` — about forty temporary-corpus call sites this session).
- **Acceptance.** **The resolved `StructureCatalog.All` is byte-identical before and after** —
  serialize every `StructureDef` field for every row, in id order, and compare the hash taken on the
  pre-change tree with the post-change tree; no seed file contains a numeric field (the anchor audit
  covers the whole row, not only `anchor`); every playable row's ordinals resolve; the corpus has one
  writer and a rerun is byte-identical; `LoamPolicy` exposes no structure cost, yield, capacity or build
  turn; `python gk-core/scripts/audit-magic-numbers.py` shows no new literal on the balance surface.
- **Verification:** `.\scripts\verify-change.ps1 -Paths <changed C# and test files> -Session <id>`
  (Core, Data and Server tests through their boundaries), plus
  `python -m pytest gk-forge/tools/seedsmith/tests/test_structure_corpus.py -q`. This module crosses Core, Data
  and Server test projects, so it is one of the three points where the full suite is the right call
  (AGENTS.md "Verification boundary", point 2).

### 5.5 `exchange-role` (D-E1)

**Capability.** One reviewed widening of the closed role list: `Exchange`, with a description and a
negative clause (*"clears trades between parties; not storage, not a road, not a charter"*), a budget
row, legal slot kinds in the plan, and C# registry validation through `band-reader`. The behaviour a
trade hub has (clearing capacity, prices) is `trade-network` `exchange`'s; this module adds the
vocabulary only.

- **Built:** the closed list (`gk-forge/tools/seedsmith/seedsmith/adapters/structures/anchor/schema.py:41`) and its tests (`test_no_role_has_zero_rows`).
- **Wiring gap:** C# never validates a role (`StructureCorpus.cs:119`), so "widen C# together" means
  adding the role registry check `band-reader` introduces, not editing a C# enum (none exists).
- **Real gap:** the value itself.
- **Depends on:** `structure-bands` (so `ROLE_TO_STRUCTURE_KIND` is already gone and the C# registry
  exists), `world-budgets` (the budget row).
- **Touches:** `gk-forge/tools/seedsmith/seedsmith/adapters/structures/anchor/{schema.py,descriptions.py}`, the
  C# role registry, `data/tuning/structure-seed.v{n}.json`, and the documents that enumerate ten roles:
  `docs/architecture/structure-seed-ideal.md` §4, `docs/architecture/base-defense/spec-structure-schema.md`,
  `docs/architecture/base-defense-ideal.md` §5.21, `docs/architecture/trade-network-ideal.md:161`.
- **Acceptance.** The role list has exactly the ten existing roles plus `Exchange` — a closed-vocabulary
  pin, stated as such, because a twelfth role is a reviewed change; every role has a description with a
  negative clause, a budget target and at least one legal slot kind; a C# corpus row with an unknown
  role is a load rejection; `test_no_role_has_zero_rows` holds once `trade-structure-rows` lands (until
  then the plan reports the gap as a finding, which is the planner doing its job).
- **Verification:** seedsmith pytest (structure tests) and `FusionRpg.Core.Tests` through
  `verify-change.py`.

### 5.6 `decision-45-revision` (D-E2)

**Capability.** D-E2 gives `empire-seed` every world and empire content family, the structure corpus
included; `base-defense` and `trade-network` consume it. Decision 45's **content** (the structure
modules 23–29 and their specs) is unchanged; only the program boundary moves. This module lands the
revision in every document that still says otherwise, **after this map is approved**. This map lists
them and edits none.

| Where | What it says today | Revision |
|---|---|---|
| `docs/architecture/base-defense-ideal.md:163-164` | Decision 30: `structure-seed` is its own program | Annotate as superseded twice (45, then D-E2) |
| `docs/architecture/base-defense-ideal.md:184-191` | Decision 33: the planner "belongs to `structure-seed`" | Name `empire-seed` as the owner |
| `docs/architecture/base-defense-ideal.md:253-255` | Decision 45: structure content folds into `base-defense` | Record D-E2's boundary revision beside it |
| `docs/architecture/base-defense-map.md:36-38` | "`structure-seed` is now a module set inside this program" | Boundary moved to `empire-seed`; modules 23–29 shipped under base-defense, owned by empire-seed from here |
| `docs/architecture/base-defense-map.md:69`, `:124-130`, `:154-161`, `:284` | Module family table, module rows 23–29, build order c0–c5, the closed-question row | Mark the family as consumed from `empire-seed` |
| `tasks/base-defense-todo.md:1632-1903` | Task sections `structure-schema` (c0) through `structure-metrics` (c5) | A pointer to `tasks/empire-seed-todo.md` for any further structure-content work; history stays |
| `docs/architecture/structure-seed-ideal.md` §8 | Decision 45 as the program boundary | Add D-E2 |
| `docs/architecture/trade-network-ideal.md:573` | Boundary table: `base-defense` owns the structure schema and corpus | `empire-seed` owns it |
| `docs/architecture/decisions.md` | **No row** covers who owns the structure corpus (grep this session) | Add an `empire-seed` ownership row carrying D-E1 and D-E2 |
| `docs/DESIGN-GATE.md` §1 | No row for structure or empire content generation | Add a row pointing at the ideal and this map |

- **Depends on:** owner approval of this map. **Touches:** the documents above. **Acceptance:** every
  row above carries the revision; `python scripts/audit-doc-citations.py --scope <each edited doc>`
  reports no HIGH finding. **Verification:** the citation audit (docs only).

### 5.7 `world-exemplars` (ideal I4)

**Capability.** A small hand-authored distribution per family for the model to extend: exemplar rows
for every structure role (including `Exchange`) under `data/seed/structures/_exemplars/` (legion
exemplars are `legion-seed-contract`'s, §4 "Why these boundaries"). Plus the **tone brief**, shared by
every family's naming prompt: generic strategy-genre vocabulary (legion, unit, standard, doctrine,
depot, warehouse, enemy empires), **no named characters, no IP words** (owner, round 3; legion-build
vocabulary rule). The IP block list is **not** a private word list: it is the shared `avoid-list`
helper `ip-censor` owns (IC-3 — advisory in briefs, the release scan is the gate).

- **Built:** item exemplars only (`gk-data/packs/fusion/data/seed/items/_exemplars/`); the decision-43 almanac guard.
- **Real gap:** world exemplars, the tone brief.
- **Depends on:** `exchange-role`. Cross-map (soft): `ip-censor` `avoid-list` — an empty list until that
  registry exists never blocks this module.
- **Touches:** `data/seed/structures/_exemplars/**` (new), the tone brief under the adapter's
  `_registry/` (new), brief-rendering code in the structures adapter.
- **Acceptance.** Every role has at least one exemplar and every exemplar validates as real content of
  its kind (the seedsmith "exemplar conformance" metric); no exemplar name matches a real PvZ almanac
  type name; the tone brief carries no character or IP name and renders into every naming prompt;
  exemplars are never counted as corpus rows by the planner.
- **Verification:** seedsmith pytest (new exemplar tests).

### 5.8 `world-name-index`

**Capability.** A deterministic, committed index of every name in every seed corpus (structures,
creatures, items, actions, dungeon, and later legion and narrative), normalised the way the decision-43
guard normalises, plus the rendered `avoid-list`. Every naming call receives it as its dedup and block
input (ideal §7 step 4: *"a global dedup list and a blocklist built from every existing name in every
corpus"*).

- **Built:** `name_collision` and `SemanticDedup` validators (`narrative-seed-ideal.md` §4.1 lists them
  under `gk-forge/tools/seedsmith/seedsmith/workflow/validators/` and `metrics/dedup.py`).
- **Real gap:** the cross-corpus index.
- **Depends on:** `structures-adapter` (reads each corpus through its registered adapter).
- **Touches:** a seedsmith core or briefkit helper (feature-agnostic, P5) and its tests.
- **Acceptance.** The index equals the union of names on disk across the registered adapters (a
  reconciliation); building it twice is byte-identical; it calls no model; a new corpus joins by
  registering its adapter, not by editing the index code.
- **Verification:** seedsmith pytest.

### 5.9 `corpus-metrics`

**Capability.** The structure metric set, measured over the committed corpus, with the closed-loop /
open-loop split declared per metric.

| Metric | Loop | Target |
|---|---|---|
| Schema conformance, every field populated, every enum in its registry | closed | 100% |
| Every playable row's ordinals resolve to a band | closed | 100% |
| Per-role coverage against `budget` | closed | tuning `budget` ± `roleCountTolerance` |
| Grid density | closed | tuning `metrics.densityBand` |
| Name uniqueness per kind across corpora (via `world-name-index`) | closed | zero collisions |
| Idempotency (rerun hash) | closed | hash equality |
| Rarity is not a power axis | closed | existing target |
| Every good has two or more producers | closed | declared now, **measured only once `trade-network` `sector-yield` defines goods chains** |
| Flavour distinctness, n-gram mode collapse | **open** | review queue only |

- **Built:** most of the table (`structures/metrics.py:215-224`).
- **Wiring gap:** measured over `ALL_ROWS` (`structures/metrics.py:259-264`).
- **Real gap:** the band-resolves, cross-corpus uniqueness and two-producer metrics.
- **Depends on:** `structures-adapter`, `structure-bands`, `world-budgets`.
- **Touches:** `gk-forge/tools/seedsmith/seedsmith/adapters/structures/metrics.py`, its tests.
- **Acceptance.** Every registered metric declares a loop, and every closed metric a target (the
  existing registration error stays); no open-loop metric can make `Report.passed` false; the report
  prints corpus scale as a reading and asserts none.
- **Verification:** `python -m pytest gk-forge/tools/seedsmith/tests/test_structure_metrics.py -q`.

### 5.10 `call-budget-dry-run`

**Capability.** The planner's call budget follows the invention shape, and a dry run proves it before
anything is spent. Today the formula is classification-shaped — one call plus three votes on each of
five fields per row (`structures/planner.py:94-112`) — while the ideal's pipeline fixes enums in the
planner and spends one naming call per entry plus at most two quality repairs. The dry run renders
every prompt (brief, tone brief, exemplars, dedup and block inputs) with the transport stubbed to
raise, and prints the call count as a reading.

- **Built:** a stated `callBudget` in the committed plan.
- **Real gap:** the invention formula and a prompt-rendering dry run.
- **Depends on:** `world-exemplars`, `world-name-index`.
- **Touches:** `structures/planner.py`, the `structures` CLI subcommands in
  `gk-forge/tools/seedsmith/seedsmith/report/cli.py`.
- **Acceptance.** The plan states `targetNewRows`, calls per row, the retry bound and the vote set, and
  `estimatedCalls` is computed from them (a relationship, not a literal); `--dry-run` renders one prompt
  per planned entry and makes zero model calls (the stub raises); the output is byte-identical across
  reruns.
- **Verification:** seedsmith pytest (`test_structure_planner.py` and a dry-run test).

### 5.11 `world-namer`

**Capability.** The one model stage. Input: a planned entry whose enums are already drawn. Output:
`name`, `flavor` and `reason` — identity text only — validated against the tone brief, the dedup and
block inputs, a script check, `field_echo`, a no-digit rule for prose (principle 2) and length bounds.
Accepted entries are frozen: provenance records the plan hash, brief hash, prompt version and resolved
model; `stale_ids()` compares recorded against current inputs; a rerun over unchanged inputs is
byte-identical. Constrained decoding is proven with one real call before a run. The existing
`generate_anchor.py` voting path is kept for a field the model genuinely chooses, and is **not** used
for planner-fixed enums.

- **Built:** transport, permutation, vote and provenance helpers (`structures/generate_anchor.py:25-28`,
  `:186-221`).
- **Wiring gap:** no emit path; no name or flavour is written (§3.2).
- **Real gap:** the naming contract (a `flavor` field is a schema widening — keyed text per
  `item/seed-contract.md` §6), the emit path.
- **Depends on:** `call-budget-dry-run`, `corpus-metrics`. Cross-map (soft): `narrative-seed`
  `script-check` (the shared validator, reused rather than copied) and `model-config-resolve` (structures
  already resolves its model through `LlmCallerConfig`, so nothing blocks).
- **Touches:** `gk-forge/tools/seedsmith/seedsmith/adapters/structures/` (a naming module and emit),
  `anchor/schema.py` (`flavor`), `gk-data/packs/fusion/data/seed/structures/**` (emitted rows).
- **Acceptance.** A draft with any digit, an unknown enum, a name in the dedup index or the avoid-list,
  or an empty field is rejected with the defect named, repaired at most twice, then `unresolved`;
  transient errors resume without a new call; tests run with the transport stubbed to raise; an
  accepted row is never regenerated unless `stale_ids()` names it; no assertion names a generated
  string.
- **Verification:** seedsmith pytest with the offline guarantee (`gk-forge/tools/seedsmith/tests/test_offline_guarantee.py`).
- **Call budget (a reading, replaced by the dry run):** the ideal estimates ~15 structure rows and
  20–40 legion seeds at one call plus two repairs at most — roughly 100–400 calls on the local model.

### 5.12 `trade-structure-rows`

> **Superseded in part by round 4 (2026-09-19, §12b) and round 6 (§16).** The module now emits the
> **eight** owner-named feature buildings as authored rows with tier `variants`, model-free, in Wave 2 —
> eight since round 6 L6 added the **Standard Hall** — and every one of them carries the neutral
> `structureKind: Feature` (round 6 C2), so they load. The text below is the approved
> map text; where it disagrees, [spec-trade-structure-rows.md](empire-seed/spec-trade-structure-rows.md),
> §12b and §16 win.

**Capability.** The trade and logistics rows, generated planner-first as ordinary rows in the one
corpus: a trade hub (`Exchange`), warehouse variants (`Store`), a depot (`Move`), a bank point (`Bank`)
and a workshop that makes legion equipment (`Multiply` or `Refine`). The planner decides which rows are
missing against the budget; existing identity-only rows (`convoy-depot`, `coffer`, `stockyard`,
`reliquary`, `workshop`) count toward their roles and gain bands, so a gap is filled by a new row only
where the budget says so. A bigger warehouse is a `variants` entry, not a row (principle 10).

- **Built:** the identity rows above; the corpus and catalog.
- **Real gap:** the rows and their bands. **Behaviour is not here:** the warehouse capacity axis, bank
  points and production halt are `trade-network` `sector-yield`'s; clearing capacity and prices are
  `exchange`'s; depots and crews are `fleet`'s. A capacity or clearing ordinal is added to the anchor
  only when its consuming `StructureDef` field lands — a band with no reader is a converter with no
  consumer (`gk-core/src/FusionRpg.Core/World/Bands.cs:3-9` states the same rule).
- **Depends on:** `world-namer`, `exchange-role`. Cross-map: `trade-network` `sector-yield`, `exchange`,
  `fleet` for behaviour (their structure rows must land before `sector-yield` needs them —
  `trade-network-ideal.md` §11 order note).
- **Touches:** `gk-data/packs/fusion/data/seed/structures/**` (emitted), `data/tuning/structure-seed.v{n}.json` (budget and
  bands), the committed plan.
- **Acceptance.** Every new row passes the anchor audit and the full closed-loop metric set; every row
  names a legal role and slot kind; no new row duplicates an existing name; the per-role counts meet the
  published budget (read from tuning); the first batch is small and reviewed before any larger run (the
  owner's standing phased-rollout rule for generators).
- **Verification:** seedsmith pytest plus `FusionRpg.Core.Tests` (the catalog loads every new row).

### 5.13 `legion-seed-contract`

**Capability.** A `legion` adapter (registered in `ADAPTERS`, corpus under `data/seed/legion/`, new)
with four kinds, every field carrying an ownership level and a description with a negative clause:

| Kind | Fields (level) |
|---|---|
| `legion-standard` | `name`, `flavor` (AUTHORED); `elementAffinity` (VALIDATED); `atomFamilies[]` (VALIDATED, closed atom catalog); `carrierRequirement` ∈ any / fighter / commander (VALIDATED); `forgeGoods[]` (VALIDATED, goods registry) |
| `legion-tradition` | `triggerKind` (VALIDATED, closed list of world facts); `atomFamily` (VALIDATED); `rankNames[]` (AUTHORED) |
| `legion-doctrine` | `combatFamilies[]` (VALIDATED); `worldTradeoffKind` ∈ march / burn / sight / cargo (VALIDATED); `name`, `flavor` (AUTHORED) |
| `legion-equipment` | `name`, `flavor` (AUTHORED); `pieceId` (DERIVED — minted once per plan key and frozen, audit 2026-09-20 A-ES1); `slot` (VALIDATED, the legion-slot vocabulary, separate from `ItemRole`); `tier` (VALIDATED ordinal); `atomFamilies[]` (VALIDATED); `recipeGoods[]` (VALIDATED — which inputs, never how many); `producedBy` (VALIDATED structure role) |

Legion equipment is **fixed, not rolled**: the schema audit rejects any set, socket, affix pool, roll or
rarity-count field on that kind (owner amendment 2026-09-19: sets stay with unique-creature items).
Standards and traditions carry no inheritance field (owner ruling L2: both reset on disband or rout).

- **Built:** the atom-family namespace validator (`adapters/actions/distribution_planner/derive.py:585`);
  the goods vocabulary for v1, which is the closed material list
  (`gk-core/src/FusionRpg.Core/Items/Materials/MaterialCatalog.cs:68`).
- **Real gap:** everything else, and **three vocabularies this module must not invent**: the legion slot
  list, the tradition trigger-fact list and the `carrierRequirement` roles are `legion-build`'s.
- **Depends on:** `band-reader`, `world-exemplars` (the tone brief). Cross-map (hard): the vocabularies
  approved in the specs of `legion-build-map.md`'s `legion-equipment` (legion slot list),
  `legion-traditions` (trigger facts) and `legion-standards` (carrier roles); the contract lands when
  those specs are approved, not before.
- **Touches:** `tools/seedsmith/seedsmith/adapters/legion/` (new), `adapters/registry.py`,
  `data/seed/legion/` (new), `data/seed/legion/_exemplars/` (new, hand-authored — one or more per kind,
  each validating against its schema).
- **Acceptance.** The schema audit passes all four smuggling shapes for every kind; every closed enum
  admits `none` except where `none` is illegal and says why; every VALIDATED field joins to its registry;
  the legion-equipment schema has no set, socket or roll field; the adapter passes the conformance
  suite.
- **Verification:** seedsmith pytest.

### 5.14 `legion-bands`

**Capability.** Legion seed ordinals resolve to numbers through `band-reader`: a legion-equipment
piece's fixed stats resolve **once** from its `tier` at a tunable share (below 1) of the unique-item
budget at the same tier, identical for every player; the standard tier and tradition rank ladders
resolve through `P(Θ)`; doctrine trade-off magnitudes are signed modifiers read by the existing pricers
(`legion-build-ideal.md` §6.1 — never a second pricer). Tuning file: see §11 item 6.

- **Real gap:** all of it.
- **Depends on:** `legion-seed-contract`, `band-reader`. Cross-map (hard): `legion-build` layer 5c and
  the stack-scoped equipment layer, which is where these numbers enter `ActorHub`; this module produces
  numbers and folds none.
- **Touches:** the legion seed tuning file (new), catalog code consuming `band-reader`.
- **Acceptance.** Two loads with the same inputs produce the same resolved piece for every player (no
  roll seed enters); a legion-equipment piece's resolved budget is strictly below a unique item's at the
  same tier (the share is read from tuning); magnitudes are `long`; a missing band is a load rejection;
  no number appears in any legion seed file.
- **Verification:** `FusionRpg.Core.Tests` through `verify-change.py`.

### 5.15 `legion-seed-rows`

**Capability.** Planner-first generation of legion seeds, named by `world-namer`. Grids: element ×
doctrine trade-off for standards and doctrines (6 × 4 = 24 cells — both are closed vocabularies:
`gk-forge/tools/seedsmith/seedsmith/adapters/structures/anchor/schema.py:46` and the four trade-off kinds), legion slot × tier for equipment (element a second
axis only where a piece is attuned). The planner fills cells against the published legion budget.

- **Real gap:** all of it.
- **Depends on:** `legion-bands`, `world-namer`. Cross-map (hard): `legion-build` mechanics shipped
  (layer 5c binder and reader, `OwnerKind.Legion`, stack `Count`, stack-scoped equipment) — a catalog for
  a mechanic that does not exist is content nobody reads (ideal §2).
- **Touches:** `data/seed/legion/**` (emitted), the legion plan.
- **Acceptance.** As `trade-structure-rows`, per kind; per-cell coverage within the published budget
  band; no cell exceeds the documented failure density.
- **Verification:** seedsmith pytest.

---

## 6. Dependency direction

```text
structures-adapter ──┬──► world-budgets ──┐
                     │                    │
band-reader ─────────┼──► structure-bands ┼──► exchange-role ──► world-exemplars ──┐
                     │         │          │                                        │
                     │         └──────────┴──► corpus-metrics ─────────────┐       │
                     │                                                     │       │
                     └──► world-name-index ─────────────────────► call-budget-dry-run
                                                                           │
                                                                     world-namer ──► trade-structure-rows
                                                                           │                ▲
band-reader + world-exemplars ──► legion-seed-contract ──► legion-bands ───┴──► legion-seed-rows
                                                                              (exchange-role ─┘)
decision-45-revision   (documents only; after map approval; no code edge)
```

The table in §4 is authoritative; the diagram is a reading aid. **Round 4:** the `world-namer ──► trade-structure-rows` edge no longer holds — the eight feature buildings are authored and depend on `exchange-role`, `structure-bands` and `world-name-index` (§12b). **No cycles.** Every arrow points from a
model-free module toward the two model-spending ones, and nothing model-free depends on a model module.
Cross-map edges: `ip-censor` `avoid-list` and `narrative-seed` `script-check` / `model-config-resolve`
are soft (nothing blocks without them); `legion-build` vocabularies and mechanics are hard for modules
13–15; `trade-network` `sector-yield`, `exchange` and `fleet` are hard for the **behaviour** of module
12's rows, not for their identity.

---

## 7. Build order — model-free first

```text
Wave 0 — foundations                                   (no model; value today)
  structures-adapter      band-reader      decision-45-revision (docs, on approval)
  world-budgets           (after structures-adapter)

Wave 1 — one SSOT for structure numbers                (no model)
  structure-bands         (after band-reader + structures-adapter; refactor only, byte-identical)
  exchange-role           (after structure-bands + world-budgets)

Wave 2 — inputs a reviewer can read                    (no model)
  world-exemplars   world-name-index   corpus-metrics
  call-budget-dry-run     (prints the real call count for Wave 3)
  anchor schema widening  (featureUnlock, closed variants item, requiredSlotKinds, structureKind Feature
                           — split out of trade-structure-rows, lands BEFORE trade-foundation
                           sector-features; global audit M5, round 6 C1)
  trade-structure-rows    (round 4 + round 6 L6: the eight owner-named feature buildings, authored, no
                           model; after sector-features, before trade-network sector-yield needs them)

Wave 3 — structures content                            (tokens spent from here)
  world-namer             (flavour text and any planner deficit outside the eight; small first batch, reviewed)

Wave 4 — legion content                                (gated on legion-build)
  legion-seed-contract    (when legion-build's vocabularies are approved)
  legion-bands            (model-free)
  legion-seed-rows        (when legion-build's mechanics ship)
```

**Waves 0–2 spend zero tokens and stand alone:** the corpus becomes visible to every generic seedsmith
check, structure numbers get one source, the dead `LoamPolicy` block disappears, the role list is
widened with review, and the dry run states the cost of Wave 3 before anyone approves it.

---

## 8. Ownership splits (binding)

| Concern | Owner | This program must not |
|---|---|---|
| Structure and legion **seed** contracts, their registries, exemplars, tone brief, planner, metrics, naming stage and committed corpora; the band tables for seed ordinals | `empire-seed` | — |
| The structure schema's shipped modules 23–29 and their history | `base-defense` history, **owned by `empire-seed` from D-E2** | Rewrite base-defense's shipped history; only annotate it (§5.6) |
| Warehouse capacity axis, bank points, production halt, the reward layer | `trade-network` `sector-yield` | Add a capacity field without that module. (Round 6 C2: the only `StructureKind` a feature building carries is the neutral `Feature`, landed once by `trade-foundation` `sector-features`; this program emits the value and adds no kind) |
| Clearing capacity, prices, the trade hub's behaviour | `trade-network` `exchange` | Price anything |
| Depots, crews, caravans as legions on standing orders | `trade-network` `fleet`, `legion-build` | Build a hauler catalog (withdrawn by the owner, ideal §6.2) |
| Trade storylets, their hosts, predicate leaves and rate limits | `narrative-seed` (`narrative` adapter) and `npc-story-events` (runtime) | Build a second storylet generator |
| Legion slot list, tradition trigger facts, carrier roles, layer 5c, `OwnerKind.Legion`, stack `Count`, the stack-scoped equipment layer, the legion-equipment stock registry row (P4, P6, `empire-resource-ssot.md` §3) | `legion-build` | Invent any of these vocabularies or fold an actor number |
| The IP registry and the shared `avoid-list` helper | `ip-censor` | Keep a private banned-word list |
| ~~`verify-change.ps1` mapping for `gk-forge/tools/seedsmith/**` and `gk-data/packs/fusion/data/seed/**`~~ **Overruled 2026-09-20 for this file only** (reconciliation R-17): adding owner rows to `gk-core/scripts/verification-boundaries.v1.json` is the trade-network family's **own work**, in the task that first needs the path. `AGENTS.md` is explicit that an unmapped production path is a verification-boundary defect to add or repair, never something to compensate for by widening the suite, and `landing-order.md` §7 blocked row 0b on exactly these rows. `test-verification-boundary` still owns the **tool** (`verify-change.ps1`, the registry's schema and its guard); a second overlapping row at the same specificity throws `VERIFICATION BOUNDARY AMBIGUOUS`, so each path gets **one** owner row from **one** task | `test-verification-boundary` owns the tool; this family owns its own rows | Add a second overlapping row for a path another task already mapped |
| The orphaned `demons` adapter | seedsmith core | Build on it (named so no one does) |

---

## 9. Locked assumptions

1. **Magnitudes are DERIVED at load, not GENERATED offline** (`item/seed-contract.md` §2). No
   `data/generated/structures/` or `data/generated/legion/` tree.
2. **The corpus is invented, not classified** (`structure-seed-ideal.md` §3; base-defense decision 43).
3. **No model at runtime.** Every generated entry is resolved deterministically by the game.
4. **Paths are the pre-split monorepo's.** The Keepverse split (`decisions.md`, *Repository topology —
   Keepverse split*, 2026-09-19) moves generator code to `gk-forge`, `gk-data/packs/fusion/data/seed/**` to the private
   `gk-data`, and Core, Server and `gk-core/data/tuning` to `gk-core`. The `kvsplit` tool maps these paths; a
   module that lands after the split uses the mapped repositories, and nothing in this map depends on
   which side of the split it lands.
5. **`SPEC.md`, `tasks/plan.md` and `tasks/todo.md` are not used.** Specs, plan and todo go to the
   prefixed paths in the header.

---

## 10. Success criteria (program level)

### Contract checks (asserted by tests; stable across generations)

- Every seed file in `gk-data/packs/fusion/data/seed/structures/**` and `data/seed/legion/**` validates against its schema;
  no numeric field survives the audit in any seed file.
- Every VALIDATED field joins its registry in Python **and** in C#; an unknown value is a load rejection.
- Every resolved magnitude comes from a tuning band; the catalog's resolved rows are byte-identical
  across reruns and across a refactor.
- The plan counts exactly the entries on disk; each tree has one writer; a regeneration over unchanged
  inputs is byte-identical.
- Every closed-loop metric has a target read from tuning; no open-loop metric can fail a report.
- No test in this program pins a corpus size, a per-cycle outcome or a generated string.

### Readings (printed by `report`, never asserted)

Rows per role and per cell, grid density, unresolved rate, calls spent per batch, flavour distinctness.

---

## 11. Contradictions found (code wins; each is corrected by the named module, not by this map)

1. **"11 roles."** The ideal (§6.1) and `trade-network-ideal.md:161` count eleven roles including
   `wonder`. The closed list has **ten** (`gk-forge/tools/seedsmith/seedsmith/adapters/structures/anchor/schema.py:41`); `wonder/` is a directory whose two
   rows are `Extract` and `Bank`. With `exchange` there will be eleven. → `exchange-role`,
   `decision-45-revision`.
2. **The density band "moves from a test literal to a tuning value."** It is already a tuning value
   (`gk-core/data/tuning/structure-seed.v1.json:23`), read by the planner (`structures/planner.py:146`); the
   tests and a declared target string restate it. → `world-budgets`.
3. **The trade rows "land at ~4.0–4.4 per cell."** That reading assumed base-defense's ~36-row target;
   the generator deliberately stopped at 25 (`structures/generate_corpus.py:13-20`) and the corpus holds
   28. Density is a reading the planner prints, never a design input. → `call-budget-dry-run`.
4. **"One shared reader" named `ConcreteSpeciesSeedReader` as a second copy.** It reads GENERATED
   concrete output, not seed plus bands (§5.2 scope note). The duplicate that does exist is `Bands.cs`
   against the tuning tier ladder. → `band-reader`.
5. **Byte-identical acceptance versus coarse bands.** A three-rung `costProfile` cannot reproduce the
   shipped costs (`moderate` spans 0 to 300 across six rows). Resolved in §5.4 obligation 2.
6. **One tuning file for two owners.** `empire-seed-ideal.md` §8 and `legion-build-ideal.md` §9 both put
   legion seed bands and legion mechanics in `data/tuning/legion.v1.json` (proposed; does not exist yet). The structure precedent splits
   them — seed vocabulary and budget in `structure-seed.v1.json`, the multipliers they index in
   `siege.v1.json` (`StructurePolicy`) — and tunables-ssot §2 says a number belongs to the domain that
   owns the concept. **Decided by that precedent:** `data/tuning/legion-seed.v1.json` (proposed; does not exist yet) holds the
   legion seed ladders and budget; `legion.v1.json` (proposed; does not exist yet) stays `legion-build`'s. Both ideals need the one-line
   correction at spec time.
7. **"Standard" is already taken.** `ItemRole.Standard` is the commander's reserved item slot
   (`gk-core/src/FusionRpg.Core/Items/ItemRole.cs:29-31`). A legion standard is a different thing; the seed kind
   is named `legion-standard` to keep the vocabularies apart.
8. **Stale seedsmith-skill claim.** The ideal's §11 says the skill's Law 5 still says "never `float`".
   It no longer does (`.claude/skills/seedsmith-design/SKILL.md:74-79` says the old line is void).
9. **Two notes say per-row magnitudes belong in seed content**
   (`gk-core/data/tuning/loam-relics-wonders.v1.json` `_meta.note`; `gk-core/src/FusionRpg.Core/World/Loam/WonderTuning.cs:10`).
   They contradict `structure-seed-ideal.md` §7. → `structure-bands` obligation 6.
10. **A stale tuning reader.** `gk-forge/tools/seedsmith/tests/test_structure_corpus.py:75` compares against
    `loam.v4.json`; the server loads `loam.v5.json` (`gk-core/src/FusionRpg.Server/Program.cs:36`). The blocks
    are identical today. → `structure-bands`.
11. **No `decisions.md` row for structure-corpus ownership.** Decision 45 lives only in
    `base-defense-ideal.md`; D-E2 needs a row. → `decision-45-revision`.
12. **A session-boundary crossing is recorded, not resolved.** `session-boundary-check.py` exits 1 for
    this session because of broad worktree-lane globs; the session record's own notes explain why a new
    file cannot conflict.

---

## 12. Open questions

1. ~~**Fold the three hand-authored structure rows into the generator?**~~ **Decided by the owner,
   2026-09-19: yes.** `relic-vault`, `standing-stones` and `sunspire-throne` move into
   `generate_corpus.py`'s source and **stay hand-authored, with no model involved**; the generator is
   itself hand-written Python, so the tree gets one writer while the 2026-09-15 ruling's intent (no
   model, no generator logic owed — `gk-forge/tools/seedsmith/tests/test_structure_corpus.py:320-325`) holds.
   Carried out by `structure-bands` ([spec](empire-seed/spec-structure-bands.md) §5.1), which also moves
   the two wonder rows from `wonder/` to their role directories (`decisions.md` records that `wonder/` is
   a folder, not a role).

**Also confirmed by the owner, 2026-09-19:** D-E1 (a new `exchange` structure role) and D-E2
(`empire-seed` owns every world and empire content family, the structure corpus included). Both have
`decisions.md` rows (`docs/architecture/decisions.md` — 'Structure corpus owner — empire-seed (2026-09-19)' and '`exchange` structure role (2026-09-19)', present in the working tree 2026-09-19).

No other question changes the work. Band intervals, budget counts and the first batch size are tuning
and plan decisions made by principle at spec time.

## 12a. Corrections found while writing the specs (2026-09-19)

Code wins; each is carried by the named spec, and the module rows above are read through them.

| # | This map said | The code or a sibling doc says | Carried by |
|---|---|---|---|
| S1 | §5.1: the adapter passes "the conformance suite the `_stub` adapter already runs" | No shared suite exists; `test_stub_adapter.py` is per-adapter (`gk-forge/tools/seedsmith/tests/test_stub_adapter.py:22-56`) | [structures-adapter](empire-seed/spec-structures-adapter.md) §3 |
| S2 | §5.1/§5.3: the budget is checked "through the adapter's distribution metric" | Core `Distribution/CellDeviation` counts only `kind:` and item `role:` dimensions (`gk-forge/tools/seedsmith/seedsmith/metrics/distribution.py:18-25`); `Entry.get` reads top-level keys only (`gk-forge/tools/seedsmith/seedsmith/corpus/model.py:48-49`), so the adapter projects the nested `anchor` | structures-adapter §3, §5.2 |
| S3 | §5.3: `world-budgets` adds the `Exchange` budget row | Its own acceptance forbids a target for a role outside the list; the row lands with the role | [world-budgets](empire-seed/spec-world-budgets.md) §3, [exchange-role](empire-seed/spec-exchange-role.md) §5.3 |
| S4 | §5.5: `test_no_role_has_zero_rows` "holds once rows land" | Red-by-design is not allowed; the contract becomes "filled or planned" | exchange-role §5.4 |
| S5 | §5.6, §11 item 11: `decisions.md` has no ownership row | Rows exist at `docs/architecture/decisions.md` — 'Structure corpus owner — empire-seed (2026-09-19)' and '`exchange` structure role (2026-09-19)' (working tree, uncommitted) | [decision-45-revision](empire-seed/spec-decision-45-revision.md) §3 |
| S6 | §5.11: a name in the avoid-list is rejected | `ip-censor` IC-3: advisory in briefs, the release scan is the gate (`docs/architecture/ip-censor-ideal.md:440`); §5.7 of this map agrees | [world-namer](empire-seed/spec-world-namer.md) §3 |
| S7 | §5.11: `world-namer` widens the schema with `flavor` | Exemplars must validate against the schema first; the widening moves to `world-exemplars` | [world-exemplars](empire-seed/spec-world-exemplars.md) §3 |
| S8 | §3.1: the structure pipeline "resolves its model through the config layer" | Half true: no literal is passed, but `LlmCallerConfig()` binds at definition time (`gk-forge/tools/seedsmith/seedsmith/adapters/structures/generate_anchor.py:98`); `max_heal` defaults to 3 (`gk-forge/tools/seedsmith/seedsmith/pipeline/llm_caller.py:51`) against the two-repair bound | world-namer §3 |
| S9 | §5.9: `corpus-metrics` depends on three modules | The cross-corpus uniqueness metric also needs `world-name-index` (no cycle) | [corpus-metrics](empire-seed/spec-corpus-metrics.md) §5.2 |
| S10 | §5.13: the equipment field is `tier` | `tier` is on the numeric audit's deny list (`gk-forge/tools/seedsmith/seedsmith/adapters/structures/anchor/audit.py:18-21`); the field is `tierBand` | [legion-seed-contract](empire-seed/spec-legion-seed-contract.md) §3 |
| S11 | §5.14: `legion-bands` resolves the standard tier, tradition rank and doctrine terms | **Superseded by owner decision Q12 (2026-09-19, §12b):** tiers and the weaker budget share are seed magnitudes in `legion-seed.v1.json`; tradition rank *thresholds*, doctrine world-side terms and every other mechanic are `legion.v1.json`'s. The spec-time narrowing is withdrawn | [legion-bands](empire-seed/spec-legion-bands.md) §2, §3 |
| S12 | §5.4: "about forty" temporary-corpus test call sites | 63 `StructureCorpus.Load` call sites in `tests/` (a reading) | structure-bands §5.8 |
| S13 | (new) | The C# reader recurses into `_exemplars/` (`gk-core/src/FusionRpg.Core/World/StructureSeed/StructureCorpus.cs:93`); `LoamPolicy.WaystationRangeHops` has a second production reader (`gk-core/src/FusionRpg.Server/WorldEndpoints.cs:522`) | [band-reader](empire-seed/spec-band-reader.md) §3, structure-bands §3 |

## 12b. Reconciliation 2026-09-19 (round 4)

Applies [trade-network/decisions-round-4.md](trade-network/decisions-round-4.md) (binding; where this map
disagrees, the register wins). Everything below was checked against code or the committed corpus this session.

### Decisions applied

| Round-4 item | What changed here | Where |
|---|---|---|
| §B — buildings unlock features; tiers are `variants` | Seven rows, one per feature, each with its tiers as a closed `variants` list; roles decided from the closed role definitions (`base-defense-ideal.md:2071-2078`): Storehouse → `Store`, Counting House → `Bank`, Trading Post → `Exchange`, Caravan Yard → `Move` (replaces the identity-only `convoy-depot`), Rift Anchor → `Move`, Embassy → `Enable`, Workshop → `Refine` (re-roled from `Multiply`). Owner-named, so authored in the one generator and model-free; the module moves to Wave 2 | [spec-trade-structure-rows.md](empire-seed/spec-trade-structure-rows.md) §5 |
| §B — a feature is unlocked by a building **kind** | New VALIDATED anchor field `featureUnlock` (closed: `none · storage · banking · trade · caravans · cross-world · diplomacy · legion-equipment`); consumers read the feature and tier, never a row id | same, §5.4 |
| §B — Embassy's role | `Enable`'s description widens to *"gates what may be built or agreed here"* in the role registry v2; no twelfth role | same §5.3; [spec-exchange-role.md](empire-seed/spec-exchange-role.md) §5.1 |
| §B — budgets and density | Floors: Store 4, Bank 3, Exchange 1, Move 4, Enable 3, Refine 2, Multiply 1; zero deficits. Density readings: 2500‰ today (25/10) → 2800‰ after `structure-bands` → 2545‰ after `exchange-role` → 3000‰ after this module (33/11), inside the published `[2400, 4000]‰` band | spec-trade-structure-rows §5.5–§5.6 |
| §B — legion equipment: the tier is the best producible tier | The equipment `tierBand` ladder is bounded by the Workshop chain's tiers (rung *i* needs Workshop tier ≥ *i*); `producedBy` is removed from the equipment seed | [spec-legion-bands.md](empire-seed/spec-legion-bands.md) §3 item 3; [spec-legion-seed-contract.md](empire-seed/spec-legion-seed-contract.md) §5.1 |
| Q12 — legion tuning | `legion-seed.v1.json` = seed magnitudes: equipment `tierBand` ladder and weaker share, the standard tier and tradition rank tier multipliers, the doctrine combat band, the planner budget. `legion.v1.json` (`legion-build`) = every mechanic. No key in both files. S11 superseded | spec-legion-bands §2 |
| Q12 — one shared vocabulary registry | `data/seed/legion/_registry/vocab.v1.json` is the only list; `legion-build`'s C# enums are validated against it at load; the "mirror" open question is closed | spec-legion-seed-contract §5.2 |

### Contradictions fixed (inside and across this program's documents)

| # | Contradiction | Fix |
|---|---|---|
| R4-1 | §4 row 12 put the trade workshop on `Multiply`/`Refine` and the map ran the rows through the model in Wave 3 | One `Refine` row, authored, Wave 2 (§7 updated) |
| R4-2 | `spec-exchange-role.md` §5.1 cited `SlotTypeCatalog.cs:7` for `Market`; the member is at `:18` | Citation fixed; `Wildland` added to `Exchange`'s legal slots |
| R4-3 | `spec-legion-bands.md` §3 moved the standard and tradition tier ladders to `legion.v1.json`, while `legion-build`'s specs and map §10 S2 put them in `legion-seed.v1.json` | Q12 applied: `legion-seed.v1.json` |
| R4-4 | `spec-legion-seed-contract.md` fixed `rankNames[]` to "the rank count", while `legion-traditions` has no top rank (a curve extended by its last slope) | Names cover the authored points; later ranks reuse the last name — presentation, never a cap |
| R4-5 | `gk-forge/tools/seedsmith/seedsmith/adapters/structures/planner.py:52`'s comment says the variant bound of 4 "mirrors the tier ladder length"; the ladder has three rungs (`gk-core/data/tuning/structure-seed.v1.json:17`) | Named in spec-trade-structure-rows §5.4; corrected in that module's change |

### Cross-cluster conflicts (trade-network files — reported, not edited)

| # | Conflict | Recommended resolution |
|---|---|---|
| X-ES1 (**resolved, round 5 B1**) | `exchange/spec-exchange-hub.md` prices a bonus on the hub's **slot** being `Market`; `exchange-map.md` ask E-A2 wants the hub on both `Wildland` and `Market`; `counterparties/spec-clan-seeding.md` rule 2 seeds each clan's Trading Post on a `Market` slot. Round 4 makes the trade hub **one** row, and a row has one required slot kind (`BuildResolver.cs:82-89`) | Owner question ES-R4-1 below; recommended (c) serves all three specs unchanged |
| X-ES2 | `sector-yield/spec-bank-points.md` grants the bank point through an anchor ordinal `bankPoint: grant · deny · default` on existing rows; round 4 makes the bank point the Counting House building | `bank-points` reads `featureUnlock = banking` at tier ≥ 1; the per-good hold reads tier ≥ 2 (Treasury). The `bankPoint` ordinal is dropped |
| X-ES3 | `sector-yield/spec-warehouse-axis.md` resolves capacity from a `warehouseBand` ordinal on `coffer`/`stockyard` | Capacity reads the Storehouse chain's tier (`featureUnlock = storage`); `coffer` and `stockyard` stay per-world-stock capacity (rubble, ironwork), a different axis |
| X-ES4 (**resolved, round 5 X12:** `caravan-yard` is the row, `convoy-depot` its tier-2 variant) | `fleet/spec-depot.md` and `rift-trade/spec-crossing-anchor.md` use `convoy-depot` as the load point and the crossing anchor; fleet ask A5 and logistics-flow ask A5 ask for its magnitudes; the parallel `fleet` reconciliation (`fleet-map.md` A5, X-F4) keeps the id `convoy-depot` with **two** variants (Caravan Yard T1, Convoy Depot T2), which contradicts `trade-foundation/spec-sector-features.md` §2 (*"tier 1 is the row itself"*) | The row is `caravan-yard` (tier 1, *Caravan Yard*) with **one** variant `convoy-depot` (tier 2, *Convoy Depot*), per the sector-features tier rule; `fleet` reads `featureUnlock = caravans` through `TierOf`, never the id, so the rename touches only its docs. The crossing anchor is the separate `rift-anchor` row. A5 is answered: tier magnitudes resolve through `band-reader` in the consumer's change (`causeway`, `refinery`, `waystation` range keep their existing path under `structure-bands`) |
| X-ES5 | `sector-yield/spec-legion-equipment-stock.md` names "a `refine`/`multiply` row such as `workshop`" as the producer | The producer is the Workshop chain (`Refine`, `featureUnlock = legion-equipment`); production itself is `legion-build`'s (`legion-build-map.md` round-4 reconciliation) |
| X-ES6 | Nothing owned **moving a building up a tier** (`BuildResolver` builds only into an empty slot, `BuildResolver.cs:66-89`) | **Resolved by the parallel `trade-foundation` reconciliation:** `sector-features` owns the slot tier, the upgrade (a `build` naming the structure already on the slot) and the reads, and is the first reader of `featureUnlock` (`trade-network/trade-foundation/spec-sector-features.md` §2–§5). The former question ES-R4-2 is closed |
| X-ES7 | `trade-foundation/spec-sector-features.md` §2 says tier numbers are *"its consuming mechanism's own tuning, keyed by tier — never a band on the variant"*, while `spec-trade-structure-rows.md` §5.4 gives each variant `costProfile`/`strengthBand`/`footprint` ordinals | No conflict: the variant ordinals price **building** the tier (cost, HP, size — structure bands); what the tier **does** is the consumer's tuning. Both texts already say so; recorded so no one reads them as competing |

### Closed-vocabulary widenings (this program)

- Structure roles: `Exchange` (member, D-E1 — already listed); `Enable` description clause (wording only).
- Anchor schema: `featureUnlock` (new closed field, 8 values incl. `none`); `variants` item shape (closed).
- Legion seed: `producedBy` and `producedByRoles` removed (a narrowing).

### Owner questions (genuine)

**ES-R4-1 — DECIDED 2026-09-20 (round 5 B1): (c), Wildland or Market** — the Trading Post row carries
`requiredSlotKinds: [Wildland, Market]` and a Market slot gives `exchange-hub`'s bonus. *Original question:*
Which slot does the Trading Post need?
(a) `Wildland` only: buildable in every sector; `exchange-hub`'s Market-slot bonus becomes a sector bonus and
`clan-seeding` moves each clan's hub to a `Wildland` slot. (b) `Market` only: only `homeworld` and `nexus`
sectors have one (`SectorTypeCatalog.cs:57-62`, `:90-95`), and the home `Market` slot is also the only site for
`district-charter` (`generate_corpus.py:451-458`), so the player chooses between a district charter and trade.
(c) A row keeps `requiredSlotKind` and may name further legal slot kinds, bounded by its role's registry
`legalSlotKinds` (`spec-exchange-role.md` §5.1 already declares `Market` and `Wildland` for `Exchange`);
`StructureDef` carries the set and `BuildResolver`'s one comparison (`BuildResolver.cs:82-89`) becomes a
membership test. The Trading Post allows both.
**Recommendation: (c).** It is one comparison and one optional anchor field, and it keeps `exchange-hub`'s
Market-slot bonus and `clan-seeding`'s Market-slot hub exactly as written. Until answered, the row emits
`Wildland` only, which every option keeps.

## 13. DESIGN-GATE §5 checklist

```
[x] I identified the subsystem(s) this touches.
    seedsmith core and adapters; the structure corpus, catalog and tuning; LoamPolicy; the legion
    seed families (content only); documents carrying decision 45.
[~] I established and recorded this session's boundary.
    The record exists (tasks/sessions/trade-network-idea-20260919.json, paths include this file).
    session-boundary-check.py exits 1 on the crossing the record's notes already explain (§11 item 12).
[x] I read every doc in the §1 row(s) for those subsystems, this session.
    §1 rows "Creature species generation / seedsmith" (creature-seed-map.md as house style), "Any
    tunable number" (tunables-ssot.md §1-§3), validation (validation-ssot.md in full). Also read:
    seedsmith-design and spec-driven-development skills, DESIGN-GATE §2-§5, PRINCIPLES §5-§7 and §12,
    empire-seed-ideal (all), structure-seed-ideal, seedsmith-map (P1-P5, §3-§6, filed asks),
    item/seed-contract §1-§3, ai-native-generation README, narrative-seed-ideal §0 and §4 plus
    narrative-seed-map §3-§7, legion-build-ideal (all), trade-network-ideal §7.1, §8.2, §11.
    Not read: the creature-seed module specs under creature-seed/ (no creature change here) and
    the base-defense structure specs (spec-structure-*.md) — read through their code and todo
    evidence instead; decision-45-revision's spec must read them.
[x] I checked decisions.md for a lock covering this.
    No row for structure-corpus ownership (§11 item 11); the Keepverse split row shapes §9 item 4.
[x] Every factual claim cites file:line.
[x] `python scripts/audit-doc-citations.py --scope docs/architecture/empire-seed-map.md` reports no
    HIGH finding: 0 HIGH, 0 D1/D2, 0 D3 (run 2026-09-19 after the last edit).
[x] I verified claims against CODE, not comments.
    Row counts, magnitudes and ordinals were read from the committed JSON; LoamPolicy callers by grep;
    the vote path and missing emit path by reading generate_anchor.py.
[x] I read the surrounding section of every rule I quoted.
[~] I tested (not assumed) any constraint I am reporting.
    Ran: the corpus inventory, the loam v4/v5 structure-block comparison, the verification-boundary
    match for each touched path, the committed plan's call budget. The byte-identical catalog
    acceptance is a spec-time test, not run here.
[x] Nothing contradicts a §2 invariant, or I named the contradiction explicitly.
    Invariant 12 (balance surface is data) is what structure-bands closes; tunables T8 (Core never
    reads a file) is what band-reader closes.
[x] Corrections are propagated to prose, Structure, Testing, Boundaries, map, and tasks.
    This map is the only file in scope; §11 names where each correction must propagate.
[x] No assertion pins a derived-population count, an item total, generated text, or a per-cycle
    outcome. The one pinned literal is the closed role list in exchange-role, stated as a closed
    vocabulary with its reason; counts in this map are marked as readings.
[x] Event-refreshed cache (§2.16): none introduced. The catalog is load-time and host-configured.
[x] No acceptance criterion silently fixes an ordering that can vary in real play.
    band-reader's acceptance requires order-independence of file enumeration.
[x] Actor combat/derived magnitude: this program produces seeds and resolved seed numbers only;
    every actor contribution is legion-build's, through ActorHub (principle 11). No private fold.
[x] Does not invent or extend a SOLID-violating parallel path.
    One reader, one resolver, one namer, one writer per tree; the known debt (Bands.cs duplicate,
    LoamPolicy second source, Core file reads) is retired by named modules.
[ ] A new rule has a registry row.
    This map introduces no new enforcement rule. If a spec adds one (for example "Core never calls
    File. on the seed path"), that spec owes the gk-core/scripts/enforcement-registry.v1.json row.
```

## 14. Round 5 (2026-09-20)

Applies [trade-network/decisions-round-4.md](trade-network/decisions-round-4.md) *Round 5* (R5-A, R5-X;
binding). Re-verified this session: a structure row names one slot kind in the anchor
(`gk-core/src/FusionRpg.Core/World/StructureSeed/StructureCorpus.cs:120`) and in `StructureDef`
(`gk-core/src/FusionRpg.Core/World/StructureCatalog.cs:54`); `BuildResolver` compares it once
(`gk-core/src/FusionRpg.Core/World/Movement/BuildResolver.cs:84`); the planner derives legal pairs from that one
field (`gk-forge/tools/seedsmith/seedsmith/adapters/structures/planner.py:75`); the `workshop` row still sits under
`gk-data/packs/fusion/data/seed/structures/multiply/` and `convoy-depot` under `move/` (not yet regenerated).

| Ruling | Change | Where |
|---|---|---|
| **A1** — every seat starts with a tier-1 Counting House and Storehouse | The two rows exist (`counting-house`, `storehouse`, both `Wildland`); the kit is placed by feature in `world-continuity` `world-creation` §5a | [spec-trade-structure-rows.md](empire-seed/spec-trade-structure-rows.md) criterion 3b |
| **B1** — the Trading Post allows Wildland **or** Market | New optional VALIDATED anchor field `requiredSlotKinds` (first entry = `requiredSlotKind`); the Trading Post lists both; band-reader and the adapter validate every entry; the C# field and the `BuildResolver` membership test land in `exchange` `exchange-hub` §3 | spec-trade-structure-rows §5.1, §5.4 item 3, criterion 3a; [spec-band-reader.md](empire-seed/spec-band-reader.md) §5.2; [spec-structures-adapter.md](empire-seed/spec-structures-adapter.md) |
| **B2** — the Rift Anchor stands on Wildland, bonus with a rift-tear slot | Row unchanged (`Wildland`); the bonus is `rift-trade`'s sector read | spec-trade-structure-rows §5.1 |
| **C4** — slot display names renamed, building names and ids stay | Tone brief gains the rule "a building never takes a slot's display name" | [spec-world-exemplars.md](empire-seed/spec-world-exemplars.md) §5.3 |
| **X12** — `caravan-yard` is the row, `convoy-depot` its tier-2 variant | Already the row table; X-ES4 closed | spec-trade-structure-rows §5.1, §5.2 |
| **X16** — the Embassy uses `Enable`; the only role widening is `exchange` | Already §5.3 (a description clause, no new member) | spec-trade-structure-rows §5.3 |
| **X1** — every gate reads `sector-features` | Consumers read `featureUnlock`, never a row id (§5.4 item 1, unchanged) | — |

**Closed-vocabulary widening (this program):** anchor schema + `requiredSlotKinds` (optional, validated
list over the existing `SlotKind` names — no new slot kind).

**Not applicable here:** A2–A4, B3, B4, C1–C3, D1, X2–X11, X13–X15.

**Contradiction found (closed elsewhere).** `world-creation` §5a's kit needs two free `Wildland` slots in
each empire seat sector, and today's seat sectors have one or none (`world-continuity-map.md` *Round 5*).
The rows are not the problem; the fix is template content, which `counterparties` `empire-roster` §3a now
carries in its v2 template versions — no slot-kind change here.

Citation audit: `python scripts/audit-doc-citations.py --scope` run on this map and every edited
`empire-seed/` spec after these edits.

## 15. Audit 2026-09-20

An independent audit of this map and its fifteen specs against code, the committed corpus and the binding
documents (`DESIGN-GATE.md` §2, §3, §5 and its seedsmith, tunables and atom-layer rows; `PRINCIPLES.md`;
`tunables-ssot.md`; `validation-ssot.md`; `power/ssot-power-scale.md` §10–§11; `effect-atom/definitions.md`
§1–§6; the seedsmith-design skill; `research/ai-native-generation/README.md`;
`trade-network/decisions-round-4.md`), all read in this session. Every fix is in the named spec; where this
section and the text above disagree, this section wins.

### Findings

| # | Severity | Finding (evidence) | Status |
|---|---|---|---|
| A-ES1 | HIGH | `world-namer` derived a generated row's `id` from the kebab form of its accepted `name`. A later `stale_ids()` regeneration that changes the name would change the id — and a saved world stores the id of every structure it built (`rpg_world_slots.structure_id`, `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.World.cs:153`), so the save would hold an unknown id and refuse to load. The same held for legion `pieceId`s, which a fitted stack persists | **Fixed** — ids are minted once per `planKey` and frozen; only the texts regenerate (`spec-world-namer.md` §5.4, acceptance 10; `pieceId` is DERIVED in `spec-legion-seed-contract.md` §5.1 and in §5.13 above; `spec-legion-seed-rows.md` §4) |
| A-ES2 | HIGH | One power ladder: `legion-seed.v1.json` holds the standard tier multipliers and the tradition rank multipliers, per-tier quality multipliers on a `P(Θ)` magnitude with no `ssot-power-scale.md` §10 row; §10 is closed (row 38, the action rung quality ladder, is the precedent that got its own row) | **Gated** — `legion-bands` publishes neither block until the rows exist; the request is filed through `legion-build` (`spec-legion-bands.md` Hard edges, acceptance 9; `legion-build-map.md` *Audit 2026-09-20* A-LB4) |
| A-ES3 | MEDIUM | `legion-seed-contract` fixed `rankNames[]`'s length to the number of authored points in `legion.v1.json`, so a tuning publish that adds a threshold would invalidate every generated tradition seed — a balance change forcing a content regeneration (tunables-ssot T7) | **Fixed** — one or more names, independent of tuning; later ranks reuse the last name (`spec-legion-seed-contract.md` §5.1; `spec-legion-seed-rows.md` §4) |
| A-ES4 | MEDIUM | `legion-bands` took "the committed generated atom at the tier, with no roll", but generated atoms carry a range (`{"min": 23, "max": 47, "roll": "onApply"}`, `gk-data/packs/fusion/data/seed/atoms/generated/family-expand.g-attack.json`); the fixed value was unspecified | **Fixed** — the range midpoint, divide last, one rounding (`spec-legion-bands.md` §5.2 step 3, acceptance 8) |
| A-ES5 | MEDIUM | A generated family may be a `status.apply` proc (`family-expand.g-affliction.json`), while `legion-build`'s readers deliver `stat.derived` atoms only (as item equip does, `gk-core/src/FusionRpg.Core/Battle/EquipAtomSource.cs:86-98`). A piece naming such a family would load and do nothing | **Fixed** — a load rejection; the planner draws only from `legion-build`'s `legionAtomFamilies` subset (`spec-legion-bands.md` §5.2) |
| A-ES6 | LOW | `call-budget-dry-run` fills a deficit row from a per-role **template** for every enum and ordinal, so every invented row in a role is the template renamed, and with `structureKind: none` it is identity-only and never loads. Naming such rows spends tokens on content nothing reads (map §2: *"a catalog for a mechanic that does not exist is content nobody reads"*) | **Fixed by round 6, decided by principle** — `spec-call-budget-dry-run.md` §5.1a: a deficit is planned only where the drawn entry would carry `structureKind != none` (the neutral `Feature` counts), a drawn entry equal to an existing row of its role except for identity is dropped, and every unplanned deficit is **reported** as `unplannedDeficits` (a reading) instead of named. Criterion 8, and criterion 2 becomes the reconciliation. The eight feature buildings are authored and need no namer |

Checked and **clean**: the model writes identity only (three string fields; digits rejected); every field
carries an ownership level; the vote sets are empty with a stated reason, and the permutation and 1-1-1 →
`unresolved` rules are restated for any future model-chosen enum; constrained decoding is proven by one
real call before a run; transient and quality retries are separate, repairs bounded at two (and the
shipped `max_heal = 3` default is overridden); tests never call a model (the stub raises); every generated
tree has one writer and is never hand-edited; magnitudes are DERIVED from `gk-core/data/tuning/` bands at load,
`long` and `checked`; Core never reads a file (`band-reader`); no test pins a corpus size, a density, a
per-cycle outcome or a generated string (the closed role list, `featureUnlock` and the legion registry
lists are pinned as closed vocabularies with reasons); the `gk-forge/tools/seedsmith/**` and `gk-data/packs/fusion/data/seed/**`
verification gap is named in every spec with its owner (`test-verification-boundary` `python-test-lane`).

### Reported, not fixable in this program's files

| Item | Owner | Fix |
|---|---|---|
| §10.2 rows for the standard tier and tradition rank multiplier ladders (A-ES2) | the power program | Rows in the row-38 shape, PS-4 |
| `data/tuning/legion-seed.*` is unmapped for `verify-change.py` (`gk-core/scripts/verify-change.py:771`) | this program's `legion-bands` adds the tuning mapping in its publishing change; `data/seed/legion/**` stays `python-test-lane`'s (§8) | One mapping row per new tuning file |

### DESIGN-GATE §5 (this audit)

`[x]` §1 rows read this session · `[x]` verified against code and data (the slot structure-id column, the
generated atom value shape and kinds, the equip projection) · `[x]` citation audit run on this map and
every edited spec, no HIGH · `[ ]` no suite run (documents only) · `[~]` session boundary: the caller's
fence (this map and `empire-seed/**`); `session-boundary-check.py` not run · `[x]` corrections propagated ·
`[x]` no population pin added. No owner question from this audit: every finding had a principled fix.

## 16. Round 6 (2026-09-20)

Applies [trade-network/decisions-round-4.md](trade-network/decisions-round-4.md) *Round 6* (binding, owner
decisions after the global standards audit). Where this section and anything above disagree, this section
wins; each change is made in the named spec, not only here.

| Ruling | Change in this program | Where |
|---|---|---|
| **C2** — one neutral `StructureKind.Feature`; `StructureKind.Exchange` withdrawn; **round 5 X1's wording is amended** to allow this one neutral kind (the rule it protects is unchanged: a gate never reads a kind, it reads `featureUnlock` through `sector-features`) | Every feature building row carries `structureKind: "Feature"` and **loads**; the *"`none` until a consumer adds a kind"* rule is withdrawn as the cause of global audit C2 (six buildings that could never be placed, built or counted). `none` keeps one meaning: identity-registered content no mechanism consumes (exemplars, wonders). The C# member and `StructureDef.FeatureUnlock` land together in `trade-foundation` `sector-features`, ahead of the rows — this program emits the values and adds no kind of its own | [spec-structure-bands.md](empire-seed/spec-structure-bands.md) §5.2, §5.4a, criterion 10; [spec-trade-structure-rows.md](empire-seed/spec-trade-structure-rows.md) §2, §5.4 item 4, criterion 7; [spec-exchange-role.md](empire-seed/spec-exchange-role.md) §2, §10 |
| **L6** — forging a standard needs its own building kind: a **Standard Hall** with tier variants gating the standard tier | An **eighth** row, `standard-hall` (`Refine` — goods in, a forged standard out, the Workshop's shape), `featureUnlock: standard`, `Wildland`. `featureUnlock` widens to nine members. The `Refine` floor goes 1 → 3 and the density reading to 3090‰. The variant ladder's length is the standard tier ladder's, which publishes nothing until the `ssot-power-scale.md` §10.2 row lands (A-ES2 / A-LB4), so the row's **multipliers** wait on it. The owner named the ladder on 2026-09-20 — **Banner Yard → Standard Hall → Hall of Triumphs** — which fixes the standard tier ladder at three tiers, so all three variants ship with this module and only their magnitudes wait | spec-trade-structure-rows §1, §5.1, §5.1a, §5.4 item 1, §5.5, §5.6, §11 |
| **C1** — one capability flag and one ruleset bump per wave | This program publishes seed content and tuning and grants **no** capability flag. It still names its wave: the flag and the single `RulesetVersion` bump that make these rows buildable belong to the wave that lands `sector-features`, taken at landing (never pre-assigned) and recorded once in [landing-order.md](trade-network/landing-order.md) | spec-trade-structure-rows §9 |
| **C3** — banking waits on the save-identity re-key | Nothing in this program writes a banked stock, so nothing here waits. The `counting-house` row and its band tables may land before `material-ledger`; what waits is the *banking mechanism* (`sector-yield` `banking-fact`, `exchange` settlement at a bank point, `legion-build` upkeep drawing banked goods) | — (stated, no spec change) |
| **S1** — a feature building counts for nobody until one faction owns both its sector and its slot | A seed rule nowhere in this program: ownership is runtime state, and the rule lives once in `trade-foundation` `sector-features` (`TierOf` / `FactionTier`). This program adds no ownership field and no second answer | — (stated) |
| **M5** (global audit) — the schema widening lands before `sector-features` | The anchor schema step (`featureUnlock`, the closed `variants` item, `requiredSlotKinds`, the `Feature` value) is split out of `trade-structure-rows` as its own step in the build order, ahead of `sector-features`, with the rows after it | §7 Wave 2; spec-trade-structure-rows §5.4 |
| **A-ES6** (global audit, owed) — the dry run's template-copy rows | Answered by principle: plan only what can load, never a renamed template, report the rest as a reading | [spec-call-budget-dry-run.md](empire-seed/spec-call-budget-dry-run.md) §5.1a, criteria 2 and 8 |
| **m20** (global audit) — "Grand Exchange" is also a well-known name elsewhere | Every authored building and variant name passes the release scan against `ip-censor`'s `avoid-list`; the name stays the owner's call (advisory) | spec-trade-structure-rows criterion 8 |

### Consumer-added anchor fields (global audit M7, this program's table)

M7's defect was two rules pointing at each other: this map said *"a capacity or clearing ordinal is added to
the anchor only when its consuming `StructureDef` field lands"* (§5.12) while `structure-bands` §5 put the
field on the other side. **The rule, stated once:** the **anchor field, its band axis and its band table are
this program's**, published by `structure-bands`' successor version in the *consumer's* landing change, in
the order below. The consumer owns only its `StructureDef` field and its reader.

| Field | Shape | Band table | Consumer module | Lands |
|---|---|---|---|---|
| `featureUnlock` | VALIDATED string enum (nine members) | none (identity) | `trade-foundation` `sector-features` | schema step, before `sector-features` |
| `structureKind: Feature` | VALIDATED string enum value | none | `trade-foundation` `sector-features` | same step |
| `requiredSlotKinds` | VALIDATED list of `SlotKind` | none | `exchange` `exchange-hub` | round 5 B1, already specced |
| `warehouseBand` | AUTHORED ordinal | `bands.warehouse.<ordinal>` | `sector-yield` `warehouse-axis` | with `warehouse-axis` |
| `yieldBand` | AUTHORED ordinal | `bands.yield.<ordinal>` | `sector-yield` `yield-structures` | with `yield-structures` |
| `locatedYields` | **reshaped** — `structure-bands` §5.2's rule is *"every added field is a string enum or boolean"*, and an array of objects breaks it. It lands as a VALIDATED **list of string good ids** plus one `yieldBand` ordinal shared by the list (which good, never how many) | `bands.yield.<ordinal>` | `sector-yield` `yield-structures` | with `yield-structures` |
| clearing ordinal | AUTHORED ordinal | `bands.clearing.<ordinal>` | `exchange` `exchange-hub` (E-A2) | with `exchange-hub` |
| depot / anchor magnitudes | AUTHORED ordinals | per-axis | `fleet` `depot`, `rift-trade` `crossing-anchor` | with each consumer |

**Regeneration order.** Every one of these publishes `structure-seed.v{n+1}` and regenerates the corpus, so
they serialize: each change rebases on the published version it finds, takes the next one, and regenerates
the tree in the same commit (never a hand edit). The order is the landing order above, recorded once in
[landing-order.md](trade-network/landing-order.md).

### DESIGN-GATE §5 (this round)

`[x]` Read this session: the register's Round 6 (whole), the global audit (C1–C3, M1–M8, the minor table),
this map and the specs edited · `[x]` Verified against code: `StructureCatalog.cs:10-49` (the enum and the
`Obstacle` precedent), `:275` (`IsCatalogLoadable`), `StructureCorpus.cs:65` (magnitudes gate),
`gk-forge/tools/seedsmith/seedsmith/adapters/structures/planner.py:52` (variant bound 0–4) · `[x]` citation audit run on every edited file · `[~]` session
boundary: the caller's fence (this map, `empire-seed/**` and the other six named trees) · `[x]` corrections
propagated into §5.12, §7, §8 and A-ES6 · `[x]` no population pinned (the nine-member `featureUnlock`
vocabulary is a closed vocabulary with its reason; the density and row counts stay readings) · `[x]` no
number in a seed · `[x]` no hand-edited generated data (every change is a generator + regeneration).
